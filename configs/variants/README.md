Prompt addenda for agent variants (`scripts/build_agent_variant.py --prompt-addendum`).

- `workflow-v1.md`: derived from the failure taxonomy of the first held-out run
  (docs/44, docs/45 §1). Resolved runs ran a test in 67% of cases and failed
  ones in 13%; resolved runs submitted explicitly in 87% of cases and failed
  ones in 33%; runs that ran out of budget made their first edit at call 37.
  These are correlations; the variant is screened against the base, paired.
