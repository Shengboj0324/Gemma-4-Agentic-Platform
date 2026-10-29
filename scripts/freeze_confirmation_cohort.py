"""Freeze a reserved task cohort before any optimisation can spend it.

A held-out cohort is only held out if something later refuses to train on it.
This writes an immutable freeze record naming the reserved tasks and their
owners, bound to the exact selection inputs that produced them, with an identity
of its own. `scripts/check_cohort_freeze.py` is the gate that enforces it.

The freeze is a commitment, not a measurement: it establishes that these tasks
were reserved *before* optimisation, which is what makes a later comparison
meaningful. It does not establish they are unseen — forks, backports, vendored
copies and base-model pretraining exposure are invisible here, and the exposure
ledger the selection used is incomplete by its own account.

Nothing is trained, and no cloud resource is allocated.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.cohort_freeze import freeze_cohorts, validate_freeze

SOURCES = ['scripts/freeze_confirmation_cohort.py', 'zenithsync/cohort_freeze.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohorts', type=Path, required=True,
                        help='cohorts.json from scripts/build_task_pool.py')
    parser.add_argument('--cohorts-sha256', required=True)
    parser.add_argument('--pool-report', type=Path, required=True,
                        help="The pool's report.json, which pins the selection inputs")
    parser.add_argument('--pool-report-sha256', required=True)
    parser.add_argument('--reserve', action='append', required=True,
                        metavar='COHORT',
                        help='Cohort to hold out; repeatable. Not every cohort.')
    parser.add_argument('--reviewer', required=True,
                        help='Accountable identity recorded in the freeze')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for path, expected, label in ((args.cohorts, args.cohorts_sha256, '--cohorts'),
                                  (args.pool_report, args.pool_report_sha256,
                                   '--pool-report')):
        if not path.is_file():
            parser.error(label + ' is not a readable file')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')

    cohorts_identity = file_record(args.cohorts)
    if cohorts_identity['sha256'] != args.cohorts_sha256:
        raise ValueError('Cohort file identity differs from the expected digest')
    report_identity = file_record(args.pool_report)
    if report_identity['sha256'] != args.pool_report_sha256:
        raise ValueError('Pool report identity differs from the expected digest')
    cohorts = load_json(args.cohorts)
    report = load_json(args.pool_report)

    # Everything the selection depended on, taken from the pool's own report so
    # the freeze cannot name inputs the selection did not actually use.
    screening = report['screening']
    exposure = report.get('exposure')
    if exposure is None:
        raise ValueError('The pool report records no exposure ledger; a freeze '
                         'without one would reserve tasks screened against nothing')
    inputs = {'dataset': screening['dataset'], 'revision': screening['revision'],
              'metadata': report['metadata_file'],
              'exposure_ledger': exposure['ledger'],
              'seed': report['selection']['seed']}

    sources = {name: file_record(ROOT / name) for name in SOURCES}
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        record = freeze_cohorts(
            cohorts, reserved=args.reserve,
            frozen_at=datetime.now(timezone.utc).isoformat(),
            reviewer=args.reviewer, inputs=inputs)
        validate_freeze(record)
        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during the freeze')
        if (file_record(args.cohorts) != cohorts_identity
                or file_record(args.pool_report) != report_identity):
            raise RuntimeError('Inputs changed during the freeze')
        freeze_path = args.output / 'freeze.json'
        freeze_path.write_bytes(canonical_json(record))
        receipt = {'schema_version': 1, 'status': 'cohort_frozen',
                   'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                   'sources': sources,
                   'cohorts_file': cohorts_identity,
                   'pool_report_file': report_identity,
                   'freeze_file': file_record(freeze_path),
                   'freeze_sha256': record['freeze_sha256'],
                   'reserved_cohorts': record['reserved_cohorts'],
                   'training_cohorts': record['training_cohorts'],
                   'reserved_tasks': record['reserved_task_count'],
                   'reserved_owners': record['reserved_owner_count'],
                   'cohort_sizes': record['cohort_sizes'],
                   'inputs': inputs,
                   'exposure_ledger_complete': exposure['complete_exposure_ledger'],
                   'training_approved': False, 'training_started': False,
                   'scope': record['scope']}
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise
    print({'status': receipt['status'], 'freeze_sha256': record['freeze_sha256'],
           'reserved_cohorts': record['reserved_cohorts'],
           'reserved_tasks': record['reserved_task_count'],
           'reserved_owners': record['reserved_owner_count'],
           'training_cohorts': record['training_cohorts'],
           'cohort_sizes': record['cohort_sizes'],
           'exposure_ledger_complete': exposure['complete_exposure_ledger']})


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Cohort freeze failed ({type(error).__name__}: {error}); '
              'no freeze written.', file=sys.stderr)
        raise SystemExit(1)
