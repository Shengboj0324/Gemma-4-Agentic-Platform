"""Refuse any candidate task a frozen cohort reserved. Run before assembly.

This is the gate that makes a freeze mean something. Give it the freeze record
and the task identities an assembly wants to use; it exits nonzero and names
every candidate that is either a reserved task or belongs to a reserved owner.

Owner reservation is enforced as well as task reservation, because training on a
sibling package of a reserved repository is the leak that reserving by task
alone permits.

Exit codes: 0 no reserved task used; 1 a reserved task or reserved owner was
used; 2 bad arguments; 3 the run itself failed and no receipt exists; 4 the
freeze record is unusable — tampered, or not the one that was pinned — which is
a different failure from a reservation being spent.

A pass means none of these candidates is reserved. It is not a statement that
they are otherwise uncontaminated or fit to train on.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.cohort_freeze import CohortFreezeError, check_against_frozen

SOURCES = ['scripts/check_cohort_freeze.py', 'zenithsync/cohort_freeze.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']

EXIT_CLEAR = 0
EXIT_RESERVED_TASK_USED = 1
EXIT_BAD_ARGUMENTS = 2
EXIT_RUN_FAILED = 3
EXIT_FREEZE_UNUSABLE = 4


def candidate_tasks(path: Path, field):
    """Read candidate identities from a JSON list of strings or of objects."""
    rows = load_json(path)
    if not isinstance(rows, list) or not rows:
        raise ValueError('Candidate file must hold a nonempty JSON list')
    tasks = []
    for row in rows:
        if isinstance(row, str):
            tasks.append(row)
        elif isinstance(row, dict):
            if field not in row:
                raise ValueError(f'Candidate row has no {field!r} field')
            tasks.append(row[field])
        else:
            raise ValueError('Candidate rows must be strings or objects')
    return tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path, required=True,
                        help='freeze.json from scripts/freeze_confirmation_cohort.py')
    parser.add_argument('--freeze-sha256', required=True,
                        help='Expected freeze identity; a freeze you did not pin '
                             'cannot gate anything')
    parser.add_argument('--candidates', type=Path, required=True,
                        help='JSON list of candidate task identities, or of objects')
    parser.add_argument('--field', default='instance_id',
                        help='Field holding the identity when rows are objects')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.freeze.is_file():
        parser.error('--freeze is not a readable file')
    if not args.candidates.is_file():
        parser.error('--candidates is not a readable file')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')

    sources = {name: file_record(ROOT / name) for name in SOURCES}
    freeze_identity = file_record(args.freeze)
    candidates_identity = file_record(args.candidates)
    record = load_json(args.freeze)
    tasks = candidate_tasks(args.candidates, args.field)

    args.output.mkdir(parents=True, exist_ok=False)
    try:
        # A reserved task being used and the freeze itself being unusable are
        # different failures, and a receipt that calls both "reserved_task_used"
        # would misreport the second one.
        try:
            result = check_against_frozen(record, tasks,
                                          expected_freeze_sha256=args.freeze_sha256)
            problem, kind = None, None
        except CohortFreezeError as error:
            result, problem = None, str(error)
            kind = ('reserved_task_used' if 'reserved by the frozen cohort' in problem
                    else 'freeze_unusable')
        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during the check')
        receipt = {'schema_version': 1,
                   'status': 'no_reserved_task_used' if problem is None else kind,
                   'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                   'sources': sources, 'freeze_file': freeze_identity,
                   'candidates_file': candidates_identity,
                   'expected_freeze_sha256': args.freeze_sha256,
                   'candidate_tasks': len(tasks),
                   'result': result, 'problem': problem,
                   'training_approved': False,
                   'scope': 'Reservation check only. Not a statement that the '
                            'candidates are otherwise uncontaminated or fit to '
                            'train on.'}
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise
    print({'status': receipt['status'], 'candidate_tasks': len(tasks),
           'problem': problem})
    if problem is None:
        raise SystemExit(EXIT_CLEAR)
    raise SystemExit(EXIT_RESERVED_TASK_USED if kind == 'reserved_task_used'
                     else EXIT_FREEZE_UNUSABLE)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Cohort freeze check failed ({type(error).__name__}: {error}); '
              'no receipt written.', file=sys.stderr)
        raise SystemExit(EXIT_RUN_FAILED)
