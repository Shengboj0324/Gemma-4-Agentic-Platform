"""Decide whether an observed licence file supports a declared licence label.

The task pool screens on a licence *label* carried by dataset metadata. A label
is a claim by the publisher about a repository; it is not the repository's
licence. This module compares the label against the text of a licence file
actually fetched from that repository at the task's pinned base commit, and
reports one of four outcomes per observation.

The detection is deliberately narrow. Each family is recognised by phrases that
only that family's canonical text contains, and a text that does not clearly
match exactly one family is `indeterminate` rather than guessed. Being unable to
tell is a result, and it withholds the task; it is never resolved in the
permissive direction, because the whole point of the exercise is that a wrong
answer here is the expensive kind.

What a `confirmed` outcome establishes: at that commit, the repository's root
carried a licence file whose text is the declared family's, and these exact
bytes were observed and hashed. What it does not establish: that the repository
owns everything it distributes, that vendored or third-party code inside it
carries the same terms, that contributors assigned rights, that the file was not
replaced at some other commit, or that any particular use is permitted. Those
are legal questions about which a file hash says nothing.
"""

import re
import unicodedata

#: Licence families the pool's screening is allowed to accept. A label outside
#: this set is refused before any text is compared, so an unexpected label can
#: never be confirmed by accident.
KNOWN_FAMILIES = ('Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC', 'MIT',
                  'MIT-0', 'Unlicense')

#: Paths worth trying, in the order they are tried. Mostly root, because a
#: licence inside a code subtree governs that subtree and not the repository,
#: and treating one as repository-wide is the mistake this ordering avoids
#: making quietly.
#:
#: The `licenses/` entries are the exception, and a reasoned one: a directory
#: whose only purpose is to hold licence files is not a code subtree, and the
#: astropy-affiliated ecosystem keeps the repository's own licence at
#: `licenses/LICENSE.rst` as a matter of convention. Refusing to look there
#: reports a repository with a perfectly good licence as having none.
LICENCE_FILENAMES = ('LICENSE', 'LICENSE.md', 'LICENSE.txt', 'LICENSE.rst',
                     'LICENCE', 'LICENCE.md', 'LICENCE.txt',
                     'COPYING', 'COPYING.txt', 'COPYING.md',
                     'LICENSE-MIT', 'LICENSE.APACHE2', 'LICENSE-APACHE',
                     'licenses/LICENSE.rst', 'licenses/LICENSE',
                     'licenses/LICENSE.txt', 'licenses/LICENSE.md',
                     'LICENSES/LICENSE', 'LICENSES/LICENSE.txt')

#: The only directories a licence may be read from. A path outside them is not
#: tried, so widening the list above cannot quietly start reading a licence out
#: of a vendored dependency.
LICENCE_DIRECTORIES = ('', 'licenses/', 'LICENSES/')

#: Apache-2.0 section 4(d) makes a NOTICE file, where one exists, part of what a
#: redistributor must carry. It is recorded when present and its absence is not
#: treated as a defect, because the licence only requires propagating a NOTICE
#: that exists.
NOTICE_FILENAMES = ('NOTICE', 'NOTICE.txt', 'NOTICE.md')

CONFIRMED = 'confirmed'
MISMATCH = 'mismatch'
INDETERMINATE = 'indeterminate'
ABSENT = 'absent'
#: The text is a recognised copyleft licence while the label claims a permissive
#: one. This is the outcome the review exists for: it is not a detection gap but
#: a wrong label on a repository whose terms are materially different, and a
#: reviewer needs to read "this is GPL-3.0" rather than "we could not tell".
COPYLEFT = 'copyleft'

#: Copyleft families recognised so that a permissive label over one of them is
#: named. They are never confirmable here — the pool screens for permissive
#: terms — so recognising them is purely to make the refusal specific.
#:
#: These families are matched on the document's own **title line**, as one
#: contiguous phrase: the licence name immediately followed by its version line.
#:
#: Matching the name anywhere in the text does not work, and two earlier
#: versions of this table proved it on real files. The GNU licences cite each
#: other: GPL-3.0 section 13 grants permission to combine with the Affero
#: licence, and GPL-3.0's closing advice says to "use the GNU Lesser General
#: Public License instead" for a subroutine library. So a plain GPL-3.0 file
#: contains the Affero name three times and the Lesser name once, and
#: GridTools/gt4py and SciTools/cartopy — both carrying GPL-3.0's full text —
#: were read first as AGPL-3.0 and then as LGPL-3.0 before this.
#:
#: After `normalise` collapses whitespace, each document's heading becomes one
#: contiguous string, and those strings are unique per family. A citation inside
#: the body never reproduces the heading, so it cannot match.
_COPYLEFT_MARKERS = {
    'AGPL-3.0': ({'require': ('gnu affero general public license version 3, '
                              '19 november 2007',),
                  'forbid': ()},),
    'LGPL-3.0': ({'require': ('gnu lesser general public license version 3, '
                              '29 june 2007',),
                  'forbid': ()},),
    'LGPL-2.1': ({'require': ('gnu lesser general public license version 2.1, '
                              'february 1999',),
                  'forbid': ()},),
    'GPL-3.0': ({'require': ('gnu general public license version 3, '
                             '29 june 2007',),
                 'forbid': ()},),
    'GPL-2.0': ({'require': ('gnu general public license version 2, '
                             'june 1991',),
                 'forbid': ()},),
    'MPL-2.0': ({'require': ('mozilla public license version 2.0',),
                 'forbid': ()},),
}

#: Phrases that appear in one family's text and not in the others'. Each family
#: has one or more alternative rules; satisfying any one of them identifies the
#: family. Within a rule, every `require` phrase must be present and every
#: `forbid` phrase absent.
#:
#: The forbid lists are what separate the pairs that share an opening: BSD-3
#: from BSD-2 by the non-endorsement clause, and MIT from MIT-0 by the
#: notice-retention clause.
#:
#: Apache-2.0 needs two rules because projects ship it two ways. The full text's
#: header line is `http://www.apache.org/licenses/` — the `LICENSE-2.0` URL
#: appears only in the appendix boilerplate, which many projects strip, so
#: requiring it withholds genuine Apache-2.0 repositories. Others ship only the
#: short grant notice and point at the full text elsewhere; that file still
#: states its own licence, so reading it is an observation, not an inference.
_MARKERS = {
    'Apache-2.0': (
        # The title line as one contiguous phrase, for the same reason the
        # copyleft table below uses contiguous titles: a body citation of
        # another licence's name must not identify this file as that licence.
        {'require': ('apache license version 2.0, january 2004',
                     'terms and conditions for use, reproduction, and '
                     'distribution'),
         'forbid': ()},
        {'require': ('licensed under the apache license, version 2.0',),
         'forbid': ()},
    ),
    'MIT': (
        {'require': ('permission is hereby granted, free of charge',
                     'the above copyright notice and this permission notice'),
         # Apache's text contains no MIT phrase, so it needs no exclusion here.
         # Forbidding it would suppress MIT in a file carrying both licences,
         # turning "cannot tell which governs" into a confident wrong family.
         'forbid': ()},
    ),
    'MIT-0': (
        {'require': ('permission is hereby granted, free of charge',),
         'forbid': ('the above copyright notice and this permission notice',)},
    ),
    'BSD-3-Clause': (
        {'require': ('redistributions of source code must retain',
                     'redistributions in binary form must reproduce',
                     'neither the name'),
         'forbid': ()},
    ),
    'BSD-2-Clause': (
        {'require': ('redistributions of source code must retain',
                     'redistributions in binary form must reproduce'),
         'forbid': ('neither the name',)},
    ),
    'ISC': (
        {'require': ('permission to use, copy, modify, and/or distribute this '
                     'software for any purpose',),
         'forbid': ()},
    ),
    'Unlicense': (
        {'require': ('this is free and unencumbered software released into the '
                     'public domain',),
         'forbid': ()},
    ),
}


def normalise(text):
    """Collapse a licence text to a form the markers can be matched against.

    Licence files differ in wrapping, indentation, smart quotes and NBSPs
    without differing in terms, so matching raw bytes would report a mismatch
    for a file that is word-for-word the canonical text. Case is folded and
    runs of whitespace become single spaces; nothing else is removed, so a text
    that genuinely says something different still differs.
    """
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')
    if not isinstance(text, str):
        raise TypeError('Licence text must be str or bytes')
    text = unicodedata.normalize('NFKC', text)
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', text).strip().lower()


def _matches(flat, rules):
    return any(all(phrase in flat for phrase in rule['require'])
               and not any(phrase in flat for phrase in rule['forbid'])
               for rule in rules)


def detect_families(text):
    """Return every permissive family whose markers the text satisfies."""
    flat = normalise(text)
    return sorted(family for family, rules in _MARKERS.items()
                  if _matches(flat, rules))


def detect_copyleft(text):
    """Return every recognised copyleft family the text satisfies."""
    flat = normalise(text)
    return sorted(family for family, rules in _COPYLEFT_MARKERS.items()
                  if _matches(flat, rules))


def review_observation(declared, text, *, path=None):
    """Compare a declared label against an observed licence text.

    `text` is None when no licence file was found at the commit, which is
    `absent` — a different result from a text that matched nothing, and the
    distinction matters because the remedies differ.
    """
    if declared not in KNOWN_FAMILIES:
        raise ValueError(f'Declared licence {declared!r} is not a known family; '
                         'screening should not have accepted it')
    if text is None:
        return {'outcome': ABSENT, 'declared': declared, 'detected': [],
                'path': None,
                'reason': 'No licence file was found at the pinned commit'}
    # Checked before the permissive families, and decisive: a file carrying
    # copyleft terms under a permissive label is the dangerous case, and
    # reporting it as merely unrecognised would bury it among detection gaps.
    copyleft = detect_copyleft(text)
    if copyleft:
        return {'outcome': COPYLEFT, 'declared': declared,
                'detected': copyleft, 'path': path,
                'reason': f'Observed {", ".join(copyleft)} while the label '
                          f'claims {declared}; the pool screens for permissive '
                          'terms and this is not one'}
    detected = detect_families(text)
    if not detected:
        return {'outcome': INDETERMINATE, 'declared': declared, 'detected': [],
                'path': path,
                'reason': 'Licence text matches no known family'}
    if len(detected) > 1:
        return {'outcome': INDETERMINATE, 'declared': declared,
                'detected': detected, 'path': path,
                'reason': 'Licence text matches more than one family: '
                          + ', '.join(detected)}
    if detected[0] != declared:
        return {'outcome': MISMATCH, 'declared': declared, 'detected': detected,
                'path': path,
                'reason': f'Observed {detected[0]}, label says {declared}'}
    return {'outcome': CONFIRMED, 'declared': declared, 'detected': detected,
            'path': path,
            'reason': f'Observed text is {declared} at the pinned commit'}


def summarise(rows):
    """Count outcomes and report which tasks training may use.

    Only `confirmed` rows are eligible. The other three outcomes are withheld
    and listed, because a review whose failures are summarised as a number
    cannot be acted on.
    """
    if not isinstance(rows, list) or not rows:
        raise ValueError('Rights review needs a nonempty list of rows')
    counts = {name: 0 for name in (CONFIRMED, MISMATCH, INDETERMINATE, ABSENT,
                                   COPYLEFT)}
    eligible, withheld = [], []
    for row in rows:
        outcome = row['outcome']
        if outcome not in counts:
            raise ValueError(f'Unknown review outcome {outcome!r}')
        counts[outcome] += 1
        (eligible if outcome == CONFIRMED else withheld).append(row)
    return {'schema_version': 1,
            'observations': len(rows),
            'outcome_counts': counts,
            'eligible_tasks': len(eligible),
            'withheld_tasks': len(withheld),
            'withheld': [{key: row[key] for key in
                          ('instance_id', 'repo', 'base_commit', 'declared',
                           'detected', 'outcome', 'reason') if key in row}
                         for row in withheld],
            'rights_cleared': False,
            'scope': 'Licence-file observation at each task\'s pinned base '
                     'commit, compared against the declared label. Not legal '
                     'clearance: it says nothing about vendored third-party '
                     'code, contributor rights, patent grants, or whether any '
                     'particular use is permitted.'}
