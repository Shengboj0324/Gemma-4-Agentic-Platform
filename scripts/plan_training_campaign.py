"""Plan a token budget against a real corpus: accounting, diversity, cost.

Every figure is derived from the independent corpus audit, never from a summary
the loader produced. A duration or cost forecast is emitted only when a measured
throughput and its evidence are supplied; otherwise the forecast is omitted and
the report says so.

This plans. It allocates no cloud resource and starts no training.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync.campaign_plan import (account_tokens, diversity_limits,
                                      forecast_campaign, mixture_plan,
                                      padding_overhead)
from zenithsync.corpus_audit import audit_corpus

SOURCES = ['scripts/plan_training_campaign.py', 'zenithsync/campaign_plan.py',
           'zenithsync/corpus_audit.py', 'zenithsync/training_corpus.py',
           'zenithsync/training_schedule.py', 'zenithsync/training_batch.py',
           'zenithsync/splits.py', 'zenithsync/artifacts.py',
           'zenithsync/contracts.py']


def fraction(text):
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError) as error:
        raise argparse.ArgumentTypeError('Expected an exact fraction like 3/5') from error
    if not 0 < value <= 1:
        raise argparse.ArgumentTypeError('Share must be in (0, 1]')
    return value


def component(text):
    name, _, share = text.partition('=')
    if not name.strip() or not share:
        raise argparse.ArgumentTypeError('Expected name=share, for example real=3/5')
    return {'name': name.strip(), 'share': fraction(share)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--corpus-sha256', required=True)
    parser.add_argument('--target-tokens', type=int, required=True,
                        help='Token budget for one candidate run')
    parser.add_argument('--basis', choices=['supervised_tokens', 'input_tokens'],
                        default='supervised_tokens',
                        help='Whether the budget counts supervised targets or inputs')
    parser.add_argument('--max-epochs', type=int, required=True)
    parser.add_argument('--split', default='train',
                        choices=['train', 'development', 'confirmation', 'all'])
    parser.add_argument('--batch-width-tokens', type=int,
                        help='Optional fixed padding width for a padding-cost estimate')
    parser.add_argument('--max-group-share', type=fraction, default=Fraction(1, 20),
                        help='Maximum share of basis tokens per repository group')
    parser.add_argument('--mixture', type=component, action='append', default=[],
                        metavar='NAME=SHARE',
                        help='Mixture component as name=share, for example real=3/5')
    parser.add_argument('--measured-tokens-per-second', type=float,
                        help='Measured throughput; required for any cost forecast')
    parser.add_argument('--measurement-evidence',
                        help='Where the measured throughput came from')
    parser.add_argument('--hourly-usd', type=float,
                        help='Quoted hourly compute price for the chosen instance')
    parser.add_argument('--overhead-seconds', type=int, default=0)
    parser.add_argument('--storage-gib', type=int, default=0)
    parser.add_argument('--storage-usd-per-gib-month', type=float, default=0.0)
    parser.add_argument('--storage-hours', type=int, default=0)
    parser.add_argument('--candidates', type=int, default=1,
                        help='Number of candidate runs sharing this plan')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.candidates <= 0:
        parser.error('At least one candidate run is required')
    if args.target_tokens <= 0:
        parser.error('--target-tokens must be a positive integer')
    if args.max_epochs <= 0:
        parser.error('--max-epochs must be a positive integer')
    if args.batch_width_tokens is not None and args.batch_width_tokens <= 0:
        parser.error('--batch-width-tokens must be a positive integer')
    if not (args.corpus / 'corpus.json').is_file():
        parser.error('--corpus does not contain a readable corpus.json')
    # A forecast needs all three inputs. Accepting a price with no measured rate
    # would silently discard the price and emit a plan with no forecast at all.
    cost_inputs = {'--measured-tokens-per-second': args.measured_tokens_per_second,
                   '--measurement-evidence': args.measurement_evidence,
                   '--hourly-usd': args.hourly_usd}
    supplied = [name for name, value in cost_inputs.items() if value is not None]
    if supplied and len(supplied) != len(cost_inputs):
        missing = sorted(set(cost_inputs) - set(supplied))
        parser.error('A forecast needs all of ' + ', '.join(sorted(cost_inputs))
                     + '; missing ' + ', '.join(missing))
    if not supplied:
        for name, value in (('--overhead-seconds', args.overhead_seconds),
                            ('--storage-gib', args.storage_gib),
                            ('--storage-usd-per-gib-month',
                             args.storage_usd_per_gib_month),
                            ('--storage-hours', args.storage_hours)):
            if value:
                parser.error(name + ' only affects a forecast, which needs '
                             '--measured-tokens-per-second, '
                             '--measurement-evidence and --hourly-usd')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')
    sources = {name: file_record(ROOT / name) for name in SOURCES}
    args.output.mkdir(parents=True, exist_ok=False)

    audit = audit_corpus(args.corpus, expected_manifest_sha256=args.corpus_sha256)
    selected = [row for row in audit['examples_detail']
                if args.split == 'all' or row['split'] == args.split]
    if not selected:
        raise ValueError('No examples in the requested split: ' + args.split)

    accounting = account_tokens(selected, target_tokens=args.target_tokens,
                                basis=args.basis, max_epochs=args.max_epochs)
    diversity = diversity_limits(selected, basis=args.basis,
                                 maximum_share=args.max_group_share)
    padding = (padding_overhead(selected, batch_width_tokens=args.batch_width_tokens)
               if args.batch_width_tokens is not None else None)
    mixture = mixture_plan(args.mixture, total_tokens=args.target_tokens) \
        if args.mixture else None

    forecast = forecast_reason = None
    if args.measured_tokens_per_second is not None:
        forecast = forecast_campaign(
            processed_input_tokens=accounting['approximate_processed_input_tokens'],
            measured_tokens_per_second=args.measured_tokens_per_second,
            measurement_evidence=args.measurement_evidence,
            hourly_usd=args.hourly_usd, overhead_seconds=args.overhead_seconds,
            storage_gib=args.storage_gib,
            storage_usd_per_gib_month=args.storage_usd_per_gib_month,
            storage_hours=args.storage_hours)
        forecast['candidate_runs'] = args.candidates
        forecast['all_candidates_compute_usd'] = forecast['compute_usd'] * args.candidates
        forecast['all_candidates_total_hours'] = forecast['total_hours'] * args.candidates
    else:
        forecast_reason = ('No measured throughput supplied, so no duration or cost '
                           'figure is produced. Measure one bounded run first.')

    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during planning')
    report = {'schema_version': 1, 'status': 'campaign_plan_only',
              'policy_satisfied': (accounting['feasible_within_max_epochs']
                                   and diversity['policy_satisfied']),
              'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'sources': sources,
              'corpus': {key: value for key, value in audit.items()
                         if key != 'examples_detail'},
              'split': args.split, 'selected_examples': len(selected),
              'token_accounting': accounting, 'diversity': diversity,
              'padding': padding, 'mixture': mixture,
              'forecast': forecast, 'forecast_omitted_because': forecast_reason,
              'candidate_runs': args.candidates,
              'training_started': False, 'cloud_resources_allocated': False,
              'scope': 'Exposure, diversity and cost arithmetic over this exact corpus. '
                       'It does not establish data sufficiency, learned improvement or '
                       'provider capacity, and it does not stop cloud billing.'}
    # Sidecar first, then bind it, so an edited sidecar contradicts the report.
    distribution_path = args.output / 'distribution.json'
    distribution_path.write_bytes(canonical_json(diversity['distribution']))
    report['distribution_file'] = file_record(distribution_path)
    (args.output / 'report.json').write_bytes(canonical_json(report))
    # A plan whose target is infeasible, or whose concentration breaks the
    # declared cap, must be visible to a calling script, not only in the JSON.
    policy_satisfied = (accounting['feasible_within_max_epochs']
                        and diversity['policy_satisfied'])
    print({'examples': len(selected),
           'policy_satisfied': policy_satisfied,
           'unique_supervised_tokens': accounting['unique_supervised_tokens'],
           'unique_input_tokens': accounting['unique_input_tokens'],
           'target_tokens': args.target_tokens, 'basis': args.basis,
           'repetition_factor': accounting['repetition_factor_float'],
           'epochs_required': accounting['epochs_required'],
           'feasible_within_max_epochs': accounting['feasible_within_max_epochs'],
           'processed_input_tokens': accounting['approximate_processed_input_tokens'],
           'repository_groups': diversity['groups'],
           'largest_group_share': diversity['largest_share_float'],
           'groups_over_cap': diversity['groups_exceeding_maximum'],
           'forecast': forecast and {'hours': forecast['total_hours'],
                                     'usd': forecast['total_usd'],
                                     'all_candidates_usd':
                                         forecast['all_candidates_compute_usd']
                                         + forecast['storage_usd']}})
    raise SystemExit(0 if policy_satisfied else 1)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Campaign planning failed ({type(error).__name__}: {error}); '
              'no report written.', file=sys.stderr)
        raise SystemExit(1)
