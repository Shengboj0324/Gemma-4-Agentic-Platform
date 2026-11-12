"""Parse a hash-locked requirements file and classify what each pin resolves to.

An unbuilt image's largest risk is that one of its pins cannot be installed at
all on the target platform: a wheel that was never published for cp312, a
version yanked since the lock was resolved, or a package that is not on the
public index and needs a wheelhouse the build does not have. Finding that out
from a `docker build` costs a build; finding it out from the index costs a few
hundred HTTP requests.

This module is the pure half: parsing, and judging an index response against a
pin. The fetching lives in `scripts/verify_lock_wheels.py`.

A pin is `satisfied` only when the index serves a file whose SHA-256 is exactly
the locked digest. Matching on name and version alone would accept a different
artifact under the same version, which is what `--require-hashes` exists to
prevent, so it is not accepted here either.
"""

import re

#: One pin per line: `name==version --hash=sha256:<64 hex>`. Anything else on a
#: non-comment line is refused rather than skipped, because a line this parser
#: silently ignored would be a pin nobody checked.
_PIN = re.compile(
    r'^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)=='
    r'(?P<version>[A-Za-z0-9][A-Za-z0-9.!+*_-]*)'
    r'(?P<hashes>(?:\s+--hash=sha256:[0-9a-f]{64})+)\s*$')

SATISFIED = 'satisfied'
DIGEST_ABSENT = 'digest_absent'
VERSION_ABSENT = 'version_absent'
NOT_ON_INDEX = 'not_on_index'

#: What the matched file actually is. An sdist pin means the image compiles that
#: package during the build; for a package the size of torch that is a different
#: proposition from installing a wheel, so it is reported rather than averaged in.
WHEEL_PLATFORM = 'platform_wheel'
WHEEL_PURE = 'pure_python_wheel'
SDIST = 'source_distribution'


def parse_lock(text):
    """Return [{name, version, hashes}] for every pin, refusing junk lines."""
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    pins, seen = [], {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.endswith('\\'):
            raise ValueError(f'Line {number} is a continuation; this parser '
                             'expects one complete pin per line')
        match = _PIN.match(line)
        if match is None:
            raise ValueError(f'Line {number} is not a hashed pin: {line!r}')
        name = match.group('name').lower().replace('_', '-')
        version = match.group('version')
        if name in seen:
            raise ValueError(f'Line {number} pins {name!r} again; it was '
                             f'already pinned at line {seen[name]}')
        seen[name] = number
        pins.append({'name': name, 'version': version,
                     'hashes': sorted(set(
                         re.findall(r'--hash=sha256:([0-9a-f]{64})',
                                    match.group('hashes'))))})
    if not pins:
        raise ValueError('Lock file contains no pins')
    return pins


def classify_file(filename, packagetype):
    """Say what kind of artifact the index served for a pin."""
    if packagetype == 'sdist':
        return SDIST
    if filename.endswith('-any.whl'):
        return WHEEL_PURE
    return WHEEL_PLATFORM


def judge_pin(pin, release):
    """Compare a pin against the index's files for that exact version.

    `release` is None when the index has no such package, and an empty list
    when it has the package but not that version. Those are different problems
    — a missing wheelhouse versus a yanked or mistyped version — so they get
    different outcomes.
    """
    base = {'name': pin['name'], 'version': pin['version']}
    if release is None:
        return {**base, 'outcome': NOT_ON_INDEX, 'filename': None,
                'artifact': None,
                'reason': 'Package is not on the index; the build needs a '
                          'wheelhouse that carries it'}
    if not release:
        return {**base, 'outcome': VERSION_ABSENT, 'filename': None,
                'artifact': None,
                'reason': 'Index has the package but not this version'}
    wanted = set(pin['hashes'])
    for entry in release:
        if entry.get('digests', {}).get('sha256') in wanted:
            return {**base, 'outcome': SATISFIED,
                    'filename': entry['filename'],
                    'artifact': classify_file(entry['filename'],
                                              entry.get('packagetype', '')),
                    'yanked': bool(entry.get('yanked')),
                    'reason': 'Index serves a file with the locked digest'}
    return {**base, 'outcome': DIGEST_ABSENT, 'filename': None,
            'artifact': None,
            'reason': f'Version is present with {len(release)} files, none '
                      'matching the locked digest'}


def summarise_lock(rows):
    """Count outcomes and name every pin that would fail an install."""
    if not isinstance(rows, list) or not rows:
        raise ValueError('Lock audit needs a nonempty list of rows')
    counts, artifacts = {}, {}
    failing, yanked = [], []
    for row in rows:
        outcome = row['outcome']
        if outcome not in (SATISFIED, DIGEST_ABSENT, VERSION_ABSENT,
                           NOT_ON_INDEX):
            raise ValueError(f'Unknown pin outcome {outcome!r}')
        counts[outcome] = counts.get(outcome, 0) + 1
        if outcome == SATISFIED:
            artifacts[row['artifact']] = artifacts.get(row['artifact'], 0) + 1
            if row.get('yanked'):
                yanked.append(row['name'] + '==' + row['version'])
        else:
            failing.append({key: row[key] for key in
                            ('name', 'version', 'outcome', 'reason')})
    return {'schema_version': 1, 'pins': len(rows),
            'outcome_counts': counts, 'artifact_counts': artifacts,
            'satisfied': counts.get(SATISFIED, 0),
            'failing_pins': failing, 'yanked_pins': sorted(yanked),
            'installable': not failing,
            'scope': 'Index availability and digest match for each pin. Not a '
                     'build: it does not establish that the wheels resolve '
                     'together, that they import, or that they work on a GPU.'}

def resolve_closure(roots, dependencies, available):
    """Return the transitive closure of `roots` over `dependencies`.

    `dependencies` maps a package name to the names it requires under the target
    environment; `available` is the set of names the source lock pins. A
    requirement outside `available` is returned as a gap rather than dropped,
    because a lock missing a transitive dependency installs a different
    environment than the one it claims to pin — and silently omitting it is how
    a derived lock ends up unbuildable for a reason nobody recorded.

    The walk is iterative and tolerates cycles, which real Python dependency
    graphs contain.
    """
    missing_roots = sorted(set(roots) - set(available))
    if missing_roots:
        raise ValueError('Roots absent from the source lock: '
                         + ', '.join(missing_roots))
    keep, gaps, queue = set(), {}, list(dict.fromkeys(roots))
    while queue:
        name = queue.pop()
        if name in keep:
            continue
        keep.add(name)
        for required in dependencies.get(name, ()):
            if required in available:
                if required not in keep:
                    queue.append(required)
            else:
                gaps.setdefault(required, []).append(name)
    return {'keep': sorted(keep),
            'gaps': {name: sorted(set(users)) for name, users in sorted(gaps.items())}}


def render_lock(pins, keep, *, header):
    """Render the kept pins as a hash-locked requirements file.

    Versions and digests are copied from the source lock, never re-resolved, so
    a derived lock cannot quietly introduce a version nobody audited.
    """
    if not header.strip():
        raise ValueError('A derived lock must carry a header saying what it is')
    kept = [pin for pin in pins if pin['name'] in set(keep)]
    if len(kept) != len(set(keep)):
        found = {pin['name'] for pin in kept}
        raise ValueError('Kept names absent from the source pins: '
                         + ', '.join(sorted(set(keep) - found)))
    lines = ['# ' + line if line else '#'
             for line in header.strip().splitlines()]
    for pin in kept:
        hashes = ' '.join('--hash=sha256:' + value for value in pin['hashes'])
        lines.append(f"{pin['name']}=={pin['version']} {hashes}")
    return '\n'.join(lines) + '\n'
