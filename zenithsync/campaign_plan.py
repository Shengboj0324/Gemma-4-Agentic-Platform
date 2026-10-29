"""Exact token accounting, diversity limits and cost arithmetic for a campaign.

Five quantities are deliberately kept apart, because conflating them is how a
token budget turns into a false diversity claim:

* unique supervised targets — distinct assistant tokens that contribute to loss
* unique input tokens       — distinct tokens the forward pass must process once
* processed input tokens    — input tokens summed over every scheduled exposure
* processed supervised      — supervised targets summed over every exposure
* padding tokens            — positions the kernel still processes but never learns

Repetition is reported as a repetition factor, never silently absorbed into a
"tokens of data" figure. A duration or cost forecast requires a *measured*
throughput; this module refuses to invent one.
"""

from fractions import Fraction

BASES = ('supervised_tokens', 'input_tokens')


def _positive(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError(name + ' must be a positive integer')
    return value


def _nonnegative(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(name + ' must be a nonnegative integer')
    return value


def _rate(value, name):
    """Accept an int, float or exact Fraction as a positive rate.

    A float is converted through `limit_denominator`, so a price or throughput
    given as a float is used to within 1e-9 rather than exactly. Pass a Fraction
    when the figure must be carried exactly.
    """
    if isinstance(value, Fraction):
        rate = value
    elif type(value) is int:
        rate = Fraction(value)
    elif type(value) is float:
        import math
        if not math.isfinite(value):
            raise ValueError(name + ' must be finite')
        rate = Fraction(value).limit_denominator(10**9)
    else:
        raise ValueError(name + ' must be an int, float or Fraction')
    if rate <= 0:
        raise ValueError(name + ' must be positive')
    return rate


def account_tokens(examples, *, target_tokens, basis='supervised_tokens', max_epochs):
    """Describe what a token target actually costs and repeats for this corpus.

    `examples` are per-example metadata rows with `example_id`, `input_tokens`
    and `supervised_tokens`. The returned `epochs_required` is the number of
    whole passes needed to reach the target on the chosen basis; it is an
    exposure count, not a claim that repetition adds information.
    """
    if basis not in BASES:
        raise ValueError('Basis must be one of ' + ', '.join(BASES))
    _positive(target_tokens, 'target_tokens')
    _positive(max_epochs, 'max_epochs')
    if not isinstance(examples, list) or not examples:
        raise ValueError('Nonempty example metadata required')
    seen = set()
    unique_input = unique_supervised = 0
    longest = 0
    for row in examples:
        if not isinstance(row, dict) or not {'example_id', 'input_tokens',
                                             'supervised_tokens'} <= set(row):
            raise ValueError('Example metadata requires identity and both token counts')
        name = row['example_id']
        if not isinstance(name, str) or not name or name in seen:
            raise ValueError('Unique nonempty example identity required')
        seen.add(name)
        inputs = _positive(row['input_tokens'], 'input_tokens')
        supervised = _positive(row['supervised_tokens'], 'supervised_tokens')
        if supervised >= inputs:
            raise ValueError('Supervised targets must be fewer than input tokens: ' + name)
        unique_input += inputs
        unique_supervised += supervised
        longest = max(longest, inputs)
    per_epoch = {'input_tokens': unique_input, 'supervised_tokens': unique_supervised}
    basis_per_epoch = per_epoch[basis]
    allowance = basis_per_epoch * max_epochs
    # Whole passes needed; the final pass is truncated by the schedule's target.
    epochs_required = -(-target_tokens // basis_per_epoch)
    feasible = allowance >= target_tokens
    repetition = Fraction(target_tokens, basis_per_epoch)
    processed_input = int(unique_input * repetition)
    processed_supervised = int(unique_supervised * repetition)
    if basis == 'supervised_tokens':
        processed_supervised = target_tokens
    else:
        processed_input = target_tokens
    return {
        'schema_version': 1, 'basis': basis,
        'examples': len(examples),
        'unique_input_tokens': unique_input,
        'unique_supervised_tokens': unique_supervised,
        'longest_example_input_tokens': longest,
        'target_tokens': target_tokens,
        'tokens_per_epoch_on_basis': basis_per_epoch,
        'max_epochs': max_epochs,
        'declared_epoch_allowance': allowance,
        'feasible_within_max_epochs': feasible,
        'epochs_required': epochs_required,
        'repetition_factor': [repetition.numerator, repetition.denominator],
        'repetition_factor_float': float(repetition),
        'approximate_processed_input_tokens': processed_input,
        'approximate_processed_supervised_tokens': processed_supervised,
        'scope': 'Exposure arithmetic only. A repetition factor above one means the '
                 'same data is seen again; it does not add distinct examples, tasks '
                 'or repositories.',
    }


def padding_overhead(examples, *, batch_width_tokens):
    """Report padding the kernel still processes under right padding to a width.

    Masking a position out of the loss does not remove its forward-pass cost.
    This models one example per sequence padded to a fixed width, which is the
    worst case for the current single-sequence collator.
    """
    _positive(batch_width_tokens, 'batch_width_tokens')
    rows = []
    padded = real = 0
    for row in examples:
        inputs = _positive(row['input_tokens'], 'input_tokens')
        if inputs > batch_width_tokens:
            raise ValueError('Example exceeds the batch width; truncation is forbidden: '
                             + str(row['example_id']))
        rows.append(batch_width_tokens - inputs)
        padded += batch_width_tokens
        real += inputs
    return {'schema_version': 1, 'batch_width_tokens': batch_width_tokens,
            'examples': len(rows), 'real_input_tokens': real,
            'padded_positions': padded - real, 'processed_positions': padded,
            'padding_fraction': [padded - real, padded],
            'padding_fraction_float': (padded - real) / padded,
            'max_padding_for_one_example': max(rows),
            'scope': 'Fixed-width right padding cost. Masked positions are still '
                     'processed by the kernel.'}


def mixture_plan(components, *, total_tokens):
    """Allocate a token budget by exact rational shares with no silent rounding.

    Shares are exact Fractions summing to one. Allocation uses the largest
    remainder method so the parts sum to the total exactly, and each component
    records the rounding applied to it.
    """
    _positive(total_tokens, 'total_tokens')
    if not isinstance(components, list) or not components:
        raise ValueError('Nonempty component list required')
    names, shares = [], []
    for component in components:
        if not isinstance(component, dict) or set(component) != {'name', 'share'}:
            raise ValueError('Each component requires exactly a name and a share')
        name = component['name']
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError('Unique nonempty component name required')
        share = component['share']
        if not isinstance(share, Fraction) or not 0 < share <= 1:
            raise ValueError('Each share must be an exact Fraction in (0, 1]')
        names.append(name)
        shares.append(share)
    if sum(shares) != 1:
        raise ValueError('Component shares must sum to exactly one')
    exact = [share * total_tokens for share in shares]
    floors = [int(value) for value in exact]
    remainder = total_tokens - sum(floors)
    order = sorted(range(len(exact)), key=lambda i: (-(exact[i] - floors[i]), names[i]))
    allocation = list(floors)
    for index in order[:remainder]:
        allocation[index] += 1
    rows = [{'name': names[i], 'share': [shares[i].numerator, shares[i].denominator],
             'exact_tokens': [exact[i].numerator, exact[i].denominator],
             'allocated_tokens': allocation[i],
             'rounding_tokens': allocation[i] - floors[i]}
            for i in range(len(names))]
    if sum(row['allocated_tokens'] for row in rows) != total_tokens:
        raise ValueError('Mixture allocation does not sum to the total')
    return {'schema_version': 1, 'total_tokens': total_tokens, 'components': rows,
            'largest_remainder_adjustments': remainder,
            'scope': 'Budget allocation only. It does not establish that qualified '
                     'data exists for any component.'}


def diversity_limits(examples, *, basis='supervised_tokens', group_field='repository_group',
                     maximum_share=Fraction(1, 20)):
    """Measure per-group concentration against an explicit maximum share.

    Exceeding the cap is reported, not silently corrected: dropping data to hit
    a percentage can remove exactly the rare cases worth keeping. The decision
    belongs to a reviewer.
    """
    if basis not in BASES:
        raise ValueError('Basis must be one of ' + ', '.join(BASES))
    if not isinstance(maximum_share, Fraction) or not 0 < maximum_share <= 1:
        raise ValueError('Maximum share must be an exact Fraction in (0, 1]')
    totals, counts = {}, {}
    overall = 0
    for row in examples:
        if group_field not in row:
            raise ValueError('Example metadata lacks the grouping field: ' + group_field)
        group = row[group_field]
        if not isinstance(group, str) or not group.strip():
            raise ValueError('Grouping field must be a nonempty string')
        key = group.casefold()
        value = _positive(row[basis], basis)
        totals[key] = totals.get(key, 0) + value
        counts[key] = counts.get(key, 0) + 1
        overall += value
    rows = []
    for key in sorted(totals, key=lambda k: (-totals[k], k)):
        share = Fraction(totals[key], overall)
        rows.append({'group': key, 'examples': counts[key], 'tokens': totals[key],
                     'share': [share.numerator, share.denominator],
                     'share_float': float(share),
                     'exceeds_maximum': share > maximum_share})
    exceeded = [row for row in rows if row['exceeds_maximum']]
    return {'schema_version': 1, 'basis': basis, 'group_field': group_field,
            'groups': len(rows), 'total_tokens': overall,
            'maximum_share': [maximum_share.numerator, maximum_share.denominator],
            'largest_share_float': rows[0]['share_float'],
            'groups_exceeding_maximum': len(exceeded),
            'distribution': rows,
            'policy_satisfied': not exceeded,
            'scope': 'Measured concentration against a declared cap. Not a decision '
                     'to remove data, and not a claim that the remainder is diverse.'}


def forecast_campaign(*, processed_input_tokens, measured_tokens_per_second,
                      measurement_evidence, hourly_usd, overhead_seconds=0,
                      storage_gib=0, storage_usd_per_gib_month=0,
                      storage_hours=0):
    """Forecast duration and cost from a *measured* throughput, never a guess.

    `measurement_evidence` must name where the throughput came from. A forecast
    built on an unmeasured rate is worse than no forecast, so it is refused.
    Cloud billing is not stopped by a process deadline: these figures bound a
    plan, not the provider's meter.
    """
    _positive(processed_input_tokens, 'processed_input_tokens')
    rate = _rate(measured_tokens_per_second, 'measured_tokens_per_second')
    if not isinstance(measurement_evidence, str) or not measurement_evidence.strip():
        raise ValueError('Throughput measurement evidence is required for a forecast')
    price = _rate(hourly_usd, 'hourly_usd')
    _nonnegative(overhead_seconds, 'overhead_seconds')
    _nonnegative(storage_gib, 'storage_gib')
    _nonnegative(storage_hours, 'storage_hours')
    storage_rate = (Fraction(0) if storage_gib == 0 else
                    _rate(storage_usd_per_gib_month, 'storage_usd_per_gib_month'))
    compute_seconds = Fraction(processed_input_tokens) / rate
    total_seconds = compute_seconds + overhead_seconds
    compute_hours = total_seconds / 3600
    compute_cost = compute_hours * price
    # A month is billed as 730 hours by convention; state it rather than hide it.
    storage_cost = Fraction(storage_gib) * storage_rate * Fraction(storage_hours, 730)
    total = compute_cost + storage_cost
    return {
        'schema_version': 1,
        'processed_input_tokens': processed_input_tokens,
        'measured_tokens_per_second': float(rate),
        'measurement_evidence': measurement_evidence,
        'compute_seconds': float(compute_seconds),
        'overhead_seconds': overhead_seconds,
        'total_seconds': float(total_seconds),
        'total_hours': float(compute_hours),
        'hourly_usd': float(price),
        'compute_usd': float(compute_cost),
        'storage_gib': storage_gib,
        'storage_hours': storage_hours,
        'storage_hours_per_month_convention': 730,
        'storage_usd': float(storage_cost),
        'total_usd': float(total),
        'scope': 'Linear extrapolation from one measured throughput. It ignores '
                 'warm-up, checkpoint writes, sequence-length variance, preemption '
                 'and restarts, and it does not stop provider billing.',
    }
