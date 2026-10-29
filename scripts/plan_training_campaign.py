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
           'zenithsync/corpus_audit.py', 'zenithsync/artifacts.py',
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
    args.output.mkdir(parents=True, exist_ok=False)
    sources = {name: file_record(ROOT / name) for name in SOURCES}

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
               if args.batch_width_tokens else None)
    mixture = mixture_plan(args.mixture, total_tokens=args.target_tokens) \
        if args.mixture else None

    forecast = forecast_reason = None
    if args.measured_tokens_per_second is not None:
        missing = [name for name, value in
                   [('--measurement-evidence', args.measurement_evidence),
                    ('--hourly-usd', args.hourly_usd)] if value is None]
        if missing:
            parser.error('A forecast also requires ' + ', '.join(missing))
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
    (args.output / 'report.json').write_bytes(canonical_json(report))
    (args.output / 'distribution.json').write_bytes(canonical_json(diversity['distribution']))
    print({'examples': len(selected),
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


if __name__ == '__main__':
    main()
