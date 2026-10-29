"""Screen pinned public task metadata into an eligible pool and select from it.

Input is a JSON-lines metadata projection pinned to a dataset revision. The
exclusion lists come from this project's own recorded development exposure, so
repositories and tasks already inspected cannot be selected as unseen.

Metadata only: no issue body, repository source or reference patch is read, so
nothing here can leak a reference solution. The output is an eligibility and
selection record, not rights clearance and not training approval.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.task_pool import (PERMISSIVE_LICENSES, disjoint_cohorts,
                                  screen_task_pool, select_task_pool)

SOURCES = ['scripts/build_task_pool.py', 'zenithsync/task_pool.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']


def read_jsonl(path: Path, *, expected_sha256, max_bytes, max_rows):
    """Read a pinned JSON-lines file, enforcing the digest on the parsed bytes.

    Hashing once and parsing from a second read would leave the pin unenforced
    on what was actually parsed, so the identity is taken before and rechecked
    after.
    """
    identity = file_record(path)
    if identity['sha256'] != expected_sha256:
        raise ValueError('Metadata file identity differs from the expected digest')
    if identity['size_bytes'] > max_bytes:
        raise ValueError('Metadata file exceeds the explicit byte ceiling')
    rows = []
    import json
    with path.open('r', encoding='utf-8') as stream:
        for number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            if len(rows) >= max_rows:
                raise ValueError('Metadata row count exceeds the explicit ceiling')
            try:
                rows.append(json.loads(line))
            except ValueError as error:
                raise ValueError(f'Invalid JSON on line {number}') from error
    if file_record(path) != identity:
        raise ValueError('Metadata file changed while reading')
    return rows, identity


def exposure_exclusions(path: Path, *, expected_sha256, max_bytes=64 * 1024**2):
    """Read this project's recorded development-exposure ledger, pinned.

    The exclusion list is the single thing that makes a selected pool arguably
    unseen, so it is the last input that should go unpinned. A stale or
    truncated ledger excludes fewer repositories and the run still succeeds,
    which is exactly the failure a digest prevents.
    """
    identity = file_record(path)
    if identity['sha256'] != expected_sha256:
        raise ValueError('Exposure ledger identity differs from the expected digest')
    if identity['size_bytes'] > max_bytes:
        raise ValueError('Exposure ledger exceeds the explicit byte ceiling')
    document = load_json(path)
    if file_record(path) != identity:
        raise ValueError('Exposure ledger changed while reading')
    repositories = sorted(document.get('repository_evidence', {}))
    instances = sorted(document.get('task_evidence', {}) or [])
    return {'repositories': repositories, 'instances': instances,
            'identity': identity,
            # These are what make the ledger a lower bound rather than a census.
            'complete_exposure_ledger': bool(document.get('complete_exposure_ledger')),
            'receipt_files_read': document.get('receipt_files_read'),
            'skipped_receipts': document.get('skipped_receipts')}


def cohort(text):
    from fractions import Fraction
    name, _, value = text.partition('=')
    if not name.strip() or not value:
        raise argparse.ArgumentTypeError('Expected name=count or name=share, for '
                                         'example train=400 or train=3/5')
    if '/' in value:
        try:
            share = Fraction(value)
        except (ValueError, ZeroDivisionError) as error:
            raise argparse.ArgumentTypeError('Invalid share fraction') from error
        if not 0 < share <= 1:
            raise argparse.ArgumentTypeError('Share must be in (0, 1]')
        return {'name': name.strip(), 'share': share}
    if not value.isdigit() or int(value) <= 0:
        raise argparse.ArgumentTypeError('Task count must be a positive integer')
    return {'name': name.strip(), 'tasks': int(value)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', type=Path, required=True,
                        help='JSON-lines task metadata projection')
    parser.add_argument('--metadata-sha256', required=True)
    parser.add_argument('--dataset', required=True, help='owner/dataset identifier')
    parser.add_argument('--revision', required=True,
                        help='Pinned 40-character dataset commit SHA')
    parser.add_argument('--language', default='python',
                        help='Language label to select exactly as the source spells it '
                             '(SWE-rebench V2 uses "python"), or "all" for every label')
    parser.add_argument('--allow-license', action='append', default=[],
                        help='Additional licence label to allow; repeatable')
    parser.add_argument('--exposure-ledger', type=Path,
                        help='Recorded development-exposure ledger to exclude')
    parser.add_argument('--exposure-ledger-sha256',
                        help='Expected digest of the exposure ledger; required '
                             'with --exposure-ledger')
    parser.add_argument('--exclude-repository', action='append', default=[])
    parser.add_argument('--exclude-owner', action='append', default=[])
    parser.add_argument('--exclude-instance', action='append', default=[])
    parser.add_argument('--minimum-created-at',
                        help='Lexicographic minimum creation timestamp')
    parser.add_argument('--allow-missing-image', action='store_true',
                        help='Keep tasks with no published environment image')
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--target-tasks', type=int, required=True)
    parser.add_argument('--max-per-repository', type=int, default=1)
    parser.add_argument('--max-per-owner', type=int)
    parser.add_argument('--cohort', type=cohort, action='append', default=[],
                        metavar='NAME=COUNT',
                        help='Repository- and owner-disjoint cohort as name=count '
                             'or name=share (for example train=3/5); repeatable')
    parser.add_argument('--max-bytes', type=int, default=256 * 1024**2)
    parser.add_argument('--max-rows', type=int, default=1000000)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Validate every argument, including cohort mode consistency, before the
    # output directory is created or 32k rows are screened.
    if args.seed < 0:
        parser.error('--seed must be a nonnegative integer')
    if args.target_tasks <= 0:
        parser.error('--target-tasks must be a positive integer')
    if args.max_per_repository <= 0:
        parser.error('--max-per-repository must be a positive integer')
    if args.max_bytes <= 0 or args.max_rows <= 0:
        parser.error('--max-bytes and --max-rows must be positive integers')
    if (args.exposure_ledger is None) != (args.exposure_ledger_sha256 is None):
        parser.error('--exposure-ledger and --exposure-ledger-sha256 must be '
                     'given together')
    if args.cohort:
        if len(args.cohort) < 2:
            parser.error('--cohort needs at least two cohorts')
        modes = {'share' if 'share' in row else 'tasks' for row in args.cohort}
        if len(modes) != 1:
            parser.error('Declare every --cohort by share or every one by count')
        names = [row['name'] for row in args.cohort]
        if len(set(names)) != len(names):
            parser.error('--cohort names must be unique')
        if modes == {'share'} and sum(row['share'] for row in args.cohort) != 1:
            parser.error('--cohort shares must sum to exactly one')
    if not args.metadata.is_file():
        parser.error('--metadata is not a readable file')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')
    sources = {name: file_record(ROOT / name) for name in SOURCES}

    rows, identity = read_jsonl(args.metadata,
                                expected_sha256=args.metadata_sha256,
                                max_bytes=args.max_bytes, max_rows=args.max_rows)

    repositories = list(args.exclude_repository)
    instances = list(args.exclude_instance)
    exposure = None
    if args.exposure_ledger is not None:
        ledger = exposure_exclusions(
            args.exposure_ledger, expected_sha256=args.exposure_ledger_sha256)
        repositories.extend(ledger['repositories'])
        instances.extend(ledger['instances'])
        exposure = {'ledger': ledger['identity'],
                    'repositories_excluded': len(ledger['repositories']),
                    'instances_excluded': len(ledger['instances']),
                    'complete_exposure_ledger': ledger['complete_exposure_ledger'],
                    'receipt_files_read': ledger['receipt_files_read'],
                    'skipped_receipts': ledger['skipped_receipts'],
                    'limitation': 'A lower bound on exposure. Forks, backports, '
                                  'vendored copies and pretraining exposure are not '
                                  'covered.'}
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        _build(args, sources, rows, identity, repositories, instances, exposure)
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise


def _build(args, sources, rows, identity, repositories, instances, exposure):
    allowed = set(PERMISSIVE_LICENSES) | {name.casefold() for name in args.allow_license}
    screened = screen_task_pool(
        rows, dataset=args.dataset, revision=args.revision,
        language=None if args.language == 'all' else args.language.casefold(),
        allowed_licenses=allowed, excluded_repositories=repositories,
        excluded_owners=args.exclude_owner, excluded_instances=instances,
        require_image=not args.allow_missing_image,
        minimum_created_at=args.minimum_created_at, max_rows=args.max_rows)

    selection = select_task_pool(
        screened['eligible_tasks'], seed=args.seed, target_tasks=args.target_tasks,
        max_per_repository=args.max_per_repository, max_per_owner=args.max_per_owner)

    cohorts = disjoint_cohorts(selection, cohorts=args.cohort) if args.cohort else None

    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during pool construction')
    report = {'schema_version': 1, 'status': 'task_pool_screened_and_selected',
              'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'sources': sources, 'metadata_file': identity,
              # Recorded so the screening is reproducible: merged counts alone
              # make a CLI-supplied exclusion unrecoverable.
              'command_line_exclusions': {
                  'repositories': sorted(args.exclude_repository),
                  'owners': sorted(args.exclude_owner),
                  'instances': sorted(args.exclude_instance)},
              'byte_policy': {'max_bytes': args.max_bytes,
                              'max_rows': args.max_rows},
              'screening': {key: value for key, value in screened.items()
                            if key not in ('eligible_tasks', 'refused_tasks')},
              'selection': {key: value for key, value in selection.items()
                            if key != 'selection'},
              'cohorts': cohorts, 'exposure': exposure,
              'rights_cleared': False, 'replay_verified': False,
              'training_approved': False, 'split_frozen': False,
              'scope': 'Metadata eligibility, reproducible selection and declared '
                       'disjoint cohorts. No rights clearance, no replay verification, '
                       'no training approval, and not an unseen-data guarantee.'}
    # Sidecars first, then bound into the report; a report that cannot
    # contradict an edited sidecar is not evidence about that sidecar.
    sidecars = {'eligible.json': screened['eligible_tasks'],
                'refused.json': screened['refused_tasks'],
                'selection.json': selection['selection']}
    if cohorts is not None:
        sidecars['cohorts.json'] = cohorts
    written = {}
    for name, payload in sidecars.items():
        path = args.output / name
        path.write_bytes(canonical_json(payload))
        written[name] = file_record(path)
    report['sidecar_files'] = written
    (args.output / 'report.json').write_bytes(canonical_json(report))
    # A shortfall against the target must be visible to a calling script.
    print({'target_met': selection['target_met'],
           'rows': screened['rows'], 'eligible': screened['accepted'],
           'refused': screened['refused'],
           'acceptance_rate': round(screened['acceptance_rate'], 4),
           'eligible_repositories': screened['distinct_repositories'],
           'eligible_owners': screened['distinct_owners'],
           'top_refusal_reasons': dict(sorted(screened['refusal_reasons'].items(),
                                              key=lambda kv: -kv[1])[:5]),
           'selected_tasks': selection['selected_tasks'],
           'selected_repositories': selection['selected_repositories'],
           'selected_owners': selection['selected_owners'],
           'shortfall': selection['shortfall'],
           'cohorts': cohorts and [(c['name'], c['tasks'], c['repositories'])
                                   for c in cohorts['cohorts']]})
    raise SystemExit(0 if selection['target_met'] else 1)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Task pool construction failed ({type(error).__name__}: {error}); '
              'no report written.', file=sys.stderr)
        raise SystemExit(1)
