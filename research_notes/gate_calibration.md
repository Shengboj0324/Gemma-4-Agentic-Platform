# Gate calibration: v2 run-to-run noise, paired-gate null/power, LB noise (2026-11-18)

Data: `task_results.jsonl` from R2 `artifacts/v1/runs/2026-11-1{7,8}/*.tar`, streamed (read-only).
Eight complete v2 runs on the 129 dev tasks (fastapi 67, rich 48, requests 13, httpx 1):
lora-eval-1 33, budget-eval-1 33, lora-eval-2b 30, lora-eval-4 31, lora-eval-6 33, lora-eval-7b 36, lora-eval-8 34, timing-l4-1 34 (mean 33.0).
Candidate names found: lora-eval-1 = [v2, **v2lora**] (no "v2lora2"), budget-eval-1 = [v2, v2b60], lora-eval-2b = [v2, v2lora3],
lora-eval-4 = [v2, v2lora5], **lora-eval-5 = [v2, v2lora5t60], partial (13 rows each; 12 shared tasks)**, lora-eval-6 = [v2, v2lora3tb1024],
lora-eval-7b = [v2, v3], lora-eval-8 = [v2, v4], timing-l4-1 = [v2]. lora-eval-5's v2 is left out of the v2 pool.
Scripts: scratchpad `calib/fetch.py`, `calib/analyze.py`, `calib/loo.py`; full numbers in `calib/results.json`.

## 1. v2 per-task solve frequency (k of 8)

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| tasks | 86 | 4 | 3 | 4 | 1 | 1 | 1 | 5 | 24 |
| beta-binomial fit | 86.0 | 4.4 | 2.6 | 2.1 | 1.9 | 2.0 | 2.3 | 3.6 | 24.1 |

Always 24, never 86, sometimes 19. Nearly all run-to-run variance comes from the 19 "sometimes" tasks plus a small leak from the extremes.

**Shrinkage.** Raw p = k/8 treats 110 tasks as deterministic. I fitted a Beta(a, b) prior to the k_i by marginal maximum likelihood (beta-binomial):
**a = 0.045, b = 0.131**. Method of moments gives 0.041 / 0.120. The prior is strongly U-shaped. The posterior mean is p_i = (k+a)/(8+a+b):
0/8 → 0.0056, 1/8 → 0.128, 4/8 → 0.495, 7/8 → 0.862, 8/8 → 0.984.
Leave-one-out check among the v2 runs: a run solved 4 of 692 tasks that the other 7 runs never solved (0.58 %, matching 0.56 %). It failed 5 of 197 tasks that the other 7 always solved (2.5 % against 1.6 %), so the always-solved side is slightly optimistic.

| SD of one v2 run's resolved count | value |
|---|---|
| observed (8 runs) | **1.85** |
| binomial mixture, unbiased sum k(n-k)/(n(n-1)) | 1.90 |
| binomial mixture, raw p = k/8 (biased low) | 1.78 |
| shrunk p, plug-in | 2.02 |
| shrunk p, posterior-integrated E[p(1-p)] | 1.91 |

No run-level (pod/hardware) effect was found. A permutation test (each task's results shuffled across runs) gives P(var ≥ observed) = 0.51, and timing-l4-1 (sequential 4xL4) is not an outlier. Runs behave like independent draws.

## 2. Null distribution of net = (arm-only) − (v2-only), no effect

Note: net is identical to (arm total − v2 total) because concordant tasks cancel. The paired view does not reduce variance; it only explains where the difference comes from.

| P(net ≥ t) | t=0 (arm ≥ v2) | 1 | 2 | 3 | 4 | 5 | 6 | SD |
|---|---|---|---|---|---|---|---|---|
| (a) empirical, 56 ordered v2 pairs | 0.571 | 0.429 | 0.304 | 0.214 | 0.071 | 0.036 | 0.018 | 2.62 |
| (b) exact, shrunk plug-in p | 0.570 | 0.430 | 0.298 | 0.189 | 0.109 | 0.056 | 0.026 | 2.85 |
| (b') posterior predictive (p_i redrawn) | 0.574 | 0.426 | 0.287 | 0.175 | **0.096** | 0.047 | 0.020 | 2.69 |

P(tie) = 0.14. (a) has only 8 runs, so its tails are coarse. Use (b') as the reference and (b) as the conservative bound.

## 3. Power

Effect models (on the 105 tasks with k < 8, from the shrunk p):
- **logit**: logit p' = logit p + δ, with δ solved so that E[total] rises by d. Gains go mostly to the sometimes tasks; only 0.3–2.3 of d lands on never-solved tasks.
- **frac**: p' = p + f(1−p), so every non-always task closes the same fraction f of its failure probability. About 90 % of the gain lands on never-solved tasks.

| true effect | 1 run P(net≥4) logit / frac | 2 runs P(Σnet≥6) | 2 runs P(Σnet≥8) |
|---|---|---|---|
| 0 (null) | 0.096 (0.109 plug-in) | 0.074 (0.086) | 0.024 (0.031) |
| +2 | 0.30 / 0.31 | 0.36 / 0.37 | 0.20 / 0.21 |
| +3 | 0.43 / 0.43 | 0.55 / 0.54 | 0.36 / 0.37 |
| +5 | 0.69 / 0.66 | **0.85 / 0.82** | 0.72 / 0.69 |
| +8 | 0.93 / 0.88 | 0.99 / 0.97 | 0.97 / 0.94 |

Smallest threshold with false-pass ≤ 10 % per number of paired runs m, and power at +5 (logit / frac):
m=1: t=4, FP 9.6 % (plug-in 10.9 %), power 0.69 / 0.66 (fails 70 %). m=2: t=6, FP 7.4 % (8.6 %), 0.85 / 0.82. m=2, t=7: FP 4.4 %, 0.79 / 0.76. m=3: t=7, FP 8.2 %, 0.95 / 0.92.

**Cheaper alternative: pooled v2 baseline.** v2 bytes are identical and no run effect is detectable, so compare the arm against the mean of all v2 runs (now 33.0 over 8 runs) instead of only the same-run v2. Keep adding each new same-run v2 to the pool. MC results, logit model, plug-in p (conservative):

| design | FP | power +5 |
|---|---|---|
| 1 arm run, arm − pooled mean ≥ 3 (arm ≥ 36/129) | 8.6 % | 0.81 |
| 1 arm run, ≥ 4 (arm ≥ 37) | 3.4 % | 0.67 |
| 2 arm runs, Σarm − 2·mean ≥ 6 | 3.3 % | 0.88 |
| 2 arm runs, ≥ 7 | 1.6 % | 0.82 |

**Recommendation.**
- **Paired gate:** use 2 independent paired runs and pass if Σnet ≥ 6 (FP 7–9 %, power 82–85 % at +5). Use Σnet ≥ 7 if you want FP below 5 % (power 76–79 %). The current single-run "net ≥ 4" rule gives about 10 % FP but only 66–69 % power at +5.
- **Pooled-baseline gate (preferred, half the GPU cost):** run 1 arm and pass if arm − pooled-v2-mean ≥ 3. Confirm with a second arm run (Σ ≥ 6) before any submission.
- **Caveat:** the pooled design depends on keeping the harness, hardware and task set fixed. Re-run the permutation check as the v2 pool grows.

## 4. Public / private LB calibration

Scale c = (9.5/58)/(33/129) = 0.640; hidden-task p_i = 0.640 × dev p_i.

| quantity | public (58) | private (~62) |
|---|---|---|
| SD of one score, fixed hidden set (resubmission noise) | **2.04** tasks (0.035) | **2.11** (0.034) |
| extra SD from which tasks are hidden | 1.94 | 2.01 |
| SD for an unseen task set | 2.82 | 2.91 |

v1 at 10 and v2 at 9 differ by 1, against an SD of about 2.9 for the difference, so they are indistinguishable. The private set is different tasks, so the expected private score for v2 is about 10.2 ± 2.9 and its correlation with public rank is weak.

P(a v2-quality agent ever scores ≥ X in N public submissions). This is a bootstrap of hidden-task sets rescaled to E = 9.5, so the draws are correlated within a task set.

| X | N=1 | 5 | 10 | 14 |
|---|---|---|---|---|
| ≥ 12/58 | 0.15 | 0.55 | 0.78 | 0.87 |
| **≥ 14/58** | **0.023** | **0.11** | **0.20** | **0.27** |
| ≥ 17/58 (top) | 0.0004 | 0.002 | 0.004 | 0.006 |

Best-of-N on public is selection noise and does not carry to private.

Dev improvement needed for a given expected public score:

| target | proportional transfer (p scaled by 0.64) | absolute transfer (Δrate same on hidden) |
|---|---|---|
| E = 14/58 | +15.6 → about 49/129 | +10.0 → 43/129 |
| E = 12/58 | +8.7 → about 42/129 | +5.6 → 39/129 |

## 5. Completed arms vs same-run v2

| run | arm | arm | v2 | arm-only | v2-only | net | p(≥net) | p two-sided | arm − pooled 33.0 (z) |
|---|---|---|---|---|---|---|---|---|---|
| lora-eval-1 | v2lora | 31 | 33 | 4 | 6 | −2 | 0.82 | 0.57 | −2 (−0.99) |
| budget-eval-1 | v2b60 | 32 | 33 | 2 | 3 | −1 | 0.71 | 0.85 | −1 (−0.49) |
| lora-eval-2b | v2lora3 | 33 | 30 | 6 | 3 | +3 | 0.18 | 0.35 | 0 (0.00) |
| lora-eval-4 | v2lora5 | 32 | 31 | 6 | 5 | +1 | 0.43 | 0.85 | −1 (−0.49) |
| lora-eval-5 (12 tasks) | v2lora5t60 | 1 | 1 | 0 | 0 | 0 | — | 1.0 | uninformative |
| lora-eval-6 | v2lora3tb1024 | 30 | 33 | 3 | 6 | −3 | 0.90 | 0.35 | −3 (−1.48) |
| lora-eval-7b | v3 | 35 | 36 | 3 | 4 | −1 | 0.71 | 0.85 | +2 (+0.99) |
| lora-eval-8 | v4 | 34 | 34 | 4 | 4 | 0 | 0.57 | 1.0 | +1 (+0.49) |

**Pooled evidence.** Across the 8 arms: combined z (paired) = −0.39; χ² = 3.44 on 8 df, p = 0.90. Against the pooled baseline: χ² = 6.2, p = 0.62, and these z values are correlated. The 7 full-arm nets have an SD of about 2.0, smaller than the null SD of 2.7. **No arm shows evidence of differing from v2 overall**, and v2lora3's +3 is exactly cancelled by its own run's low v2 (30, versus a pooled 33).

Task-level hints (not significant, but worth inspecting):
- rich_3278 is solved 8/8 by v2 but failed by 5 of 7 arms (v2lora, v2b60, v2lora3, v2lora3tb1024, v3).
- rich_3180 is solved 0/8 by v2 but solved by v2lora3 and v2lora5.
- Taken together, the arms failed v2's always-solved tasks 8 times against 4.3 expected from v2's own leave-one-out rate (Poisson p ≈ 0.07). The arm changes seem to swap specific tasks rather than shift the total.

## Per-task v2 solve counts (k of 8)

```json
{"runs":["lora-eval-1","budget-eval-1","lora-eval-2b","lora-eval-4","lora-eval-6","lora-eval-7b","lora-eval-8","timing-l4-1"],"n_runs":8,"k":{"fastapi_11194":7,"fastapi_11355":0,"fastapi_12942":0,"fastapi_13207":0,"fastapi_13537":8,"fastapi_13713":0,"fastapi_13786":0,"fastapi_13920":0,"fastapi_14077":8,"fastapi_14099":0,"fastapi_14186":0,"fastapi_14246":0,"fastapi_14258":0,"fastapi_14262":0,"fastapi_14266":0,"fastapi_14297":0,"fastapi_14301":8,"fastapi_14303":0,"fastapi_14306":0,"fastapi_14349":0,"fastapi_14356":0,"fastapi_14360":0,"fastapi_14361":0,"fastapi_14371":0,"fastapi_14372":8,"fastapi_14419":2,"fastapi_14430":0,"fastapi_14448":0,"fastapi_14455":0,"fastapi_14458":8,"fastapi_14459":0,"fastapi_14463":8,"fastapi_14479":0,"fastapi_14482":0,"fastapi_14485":0,"fastapi_14487":0,"fastapi_14492":8,"fastapi_14512":0,"fastapi_14583":0,"fastapi_14605":0,"fastapi_14609":0,"fastapi_14616":1,"fastapi_14786":8,"fastapi_14791":0,"fastapi_14794":8,"fastapi_14851":0,"fastapi_14873":7,"fastapi_14953":0,"fastapi_14962":0,"fastapi_14964":0,"fastapi_14978":0,"fastapi_14986":0,"fastapi_15023":0,"fastapi_15030":0,"fastapi_15280":0,"fastapi_15588":0,"fastapi_15589":3,"fastapi_15661":0,"fastapi_15745":0,"fastapi_15763":0,"fastapi_15785":0,"fastapi_15800":0,"fastapi_5077":8,"fastapi_5624":3,"fastapi_9425":4,"fastapi_9555":8,"fastapi_9753":7,"httpx_3672":0,"requests_6589":0,"requests_6592":0,"requests_6629":0,"requests_6644":0,"requests_6757":0,"requests_7205":0,"requests_7309":8,"requests_7315":8,"requests_7328":0,"requests_7427":8,"requests_7433":0,"requests_7502":0,"requests_7505":0,"rich_2725":8,"rich_2943":6,"rich_3006":8,"rich_3043":7,"rich_3052":0,"rich_3061":0,"rich_3063":1,"rich_3064":0,"rich_3067":8,"rich_3105":0,"rich_3130":0,"rich_3180":0,"rich_3278":8,"rich_3296":0,"rich_3454":7,"rich_3468":0,"rich_3469":0,"rich_3470":2,"rich_3471":0,"rich_3472":0,"rich_3480":5,"rich_3486":0,"rich_3506":2,"rich_3518":8,"rich_3521":3,"rich_3535":0,"rich_3675":0,"rich_3676":3,"rich_3718":8,"rich_3772":0,"rich_3777":1,"rich_3782":0,"rich_3882":8,"rich_3894":8,"rich_3905":8,"rich_3930":0,"rich_3934":0,"rich_3935":0,"rich_3938":0,"rich_3942":0,"rich_3944":0,"rich_3953":0,"rich_4006":0,"rich_4070":0,"rich_4075":1,"rich_4076":0,"rich_4077":8,"rich_4079":0}}
```
