# Compaction and win/loss behaviour on v2's "sometimes" tasks (2026-11-18)

Read-only trace analysis. No pods, no Kaggle, no R2 writes. Scripts: `scratchpad/compact/{extract.py,analyze.py,length_check.py}` (session scratch, not durable). Per-run summaries were streamed from R2 one tar at a time.

## Bottom line

- **No controllable factor that we can measure separates wins from losses inside the same task, apart from finishing the run.** The strongest within-task signals are submitting (wins 82 % vs losses 25 %) and running out of turns (20 % vs 45 %). These describe how a run ended rather than something we could switch on.
- **Compaction is a marker of long runs, not a demonstrated cause.** It happens in 76 % of all runs. Within a task, its odds ratio for winning is 0.43 (task-stratified). After also stratifying by run length the OR is 0.67, and on submitted runs stratified by length it is 1.2. Tasks that are always solved still compact in 34 % of runs and are solved 100 % of the time either way. The first compaction comes at the same point for wins and losses (median LLM call 17.5 vs 18). Compaction before the first edit shows no within-task effect (AUC 0.48, p = 0.45).
- **When the first edit happens does not matter within a task.** Medians are 7 vs 11 calls, but the within-task AUC is 0.54 and the sign test 11/9. The pooled gap of 5 calls comes from differences between tasks.
- **Edit failures matter only in their tail.** Median failed edit calls are 1 for both wins and losses. What separates them is failure loops: ≥ 10 failed edits in 4/110 wins vs 10/110 losses (sign test 6/16 tasks, p = 0.05). This is the one lever that looks controllable, by making the harness or tool schema more robust against `write_file`/`edit_file` argument errors. Even so, it accounts for at most about 6 of 110 losses.
- **Running pytest after the last edit:** 27 % of wins vs 3 % of losses (12/2 tasks, p = 0.01, MH OR 15.5). Restricted to submitted runs, the OR falls to 2.0, so most of the effect comes from the run having had time to finish. Also, 73 % of winners never ran pytest after their last edit.
- **Losing patches are rarely near-misses.** Of 110 losses, 54 left no source-file change at all: they ran out of budget after editing only repro scripts, or never edited. 45 touched the same source files as the winners but with different lines (median best line-Jaccard 0.02, against 1.00 between two winners). One clear near-miss: rich_3470 in lora-eval-8 has the winner's exact hunk plus one wrong extra hunk.

## Data and method

- **Runs (10):** the v2 arm of lora-eval-1, budget-eval-1, lora-eval-2b, lora-eval-4, lora-eval-6, lora-eval-7b, lora-eval-8, lora-eval-10a, lora-eval-10b and timing-l4-1. lora-eval-6's v2 is included because gate_calibration treats it as v2. Each run has 129 tasks, giving 1,290 run-tasks and 330 wins. Per-run totals match gate_calibration: 33, 33, 30, 31, 33, 36, 34, 32, 34, 34.
- **Task classes over 10 runs:** 22 always solved, 85 never solved, **22 sometimes solved**. This is 22 rather than the 19 found over 8 runs, because the 10a/10b runs reclassified some tasks.
- **Compaction signal.** ADK `EventsCompactionConfig(compaction_interval=15, overlap_size=2, token_threshold=14336, event_retention_size=5)` (`zenithsync/harness_context.py`). The trace has no summary step and the per-task log has no message. Compaction shows only as a drop in `prompt_tokens` between consecutive agent LLM calls.
  - **Rule:** drop to < 0.75× and by > 1,500 tokens, where the previous call had `prompt_tokens` ≥ 14,336.
  - **Validation:** of 1,580 raw drops, 1,570 follow a call at or above the threshold. Nothing else ever shrinks the prompt; the 10 sub-threshold drops are small and have no extra latency. The call after a drop is delayed by a median 8× the trace's median inter-call gap (10th percentile 3.9×), which is consistent with an extra summarisation LLM call. Only 11 calls at or above the threshold were not followed by a drop: 8 came after an earlier compaction, where the retained events were still large, and 3 did not.
  - **Example:** timing-l4-1/fastapi_15661 went 14,447 → 5,831 tokens with a 60 s gap against a typical 22 s.
  - **Scope:** compactions after `submit_patch` (36 runs) are excluded. "comp" means at least one compaction before submission.
- **Per run-task features:**
  - first edit_file/write_file call: any attempt, first success, and `first_mod` (first success or a modifying `run_command`), as a 1-based tool-call index
  - failed edit calls: the observation contains "mandatory input parameters", "old_string", "Path traversal" or `"status": "error"`, or starts with `{"error"`
  - `err_calls`: all errored calls
  - `repeats`: identical (name, args) calls seen before
  - `pytest_after`: a pytest command after the last modification. `exec_after` also counts any `python …` command.
  - total tool calls, peak `prompt_tokens`, and how the run ended (`submit_patch` / worker log "exceeded turns budget" / "timed out")
- **Statistics, within the 22 sometimes tasks:**
  - per task, Δ = mean(win) − mean(loss), then the mean Δ, a sign test over tasks, and a stratified permutation test (labels shuffled within task, 4,000 permutations, statistic = mean Δ)
  - mean within-task AUC P(win value > loss value)
  - Mantel–Haenszel OR stratified by task
  - Means are pulled around by heavy tails (e.g. 20+ failed edits). Prefer the sign test and AUC to permutation p values.

## Results: within task (22 sometimes tasks, 110 wins / 110 losses)

| feature | mean W | mean L | median W | median L | mean within-task Δ (W−L) | tasks W>L / W<L / tie | sign p | stratified perm p | within-task AUC P(W>L) |
|---|---|---|---|---|---|---|---|---|---|
| comp | 0.76 | 0.93 | 1 | 1 | -0.09 | 4/8/10 | 0.39 | 0.092 | 0.46 |
| n_comp | 0.96 | 1.26 | 1 | 1 | -0.25 | 7/14/1 | 0.19 | 0.022 | 0.39 |
| comp_before_edit | 0.06 | 0.21 | 0 | 0 | -0.04 | 4/7/11 | 0.55 | 0.453 | 0.48 |
| has_edit | 1.00 | 0.89 | 1 | 1 | +0.07 | 7/0/15 | 0.02 | 0.051 | 0.54 |
| first_edit | 8.04 | 11.60 | 6 | 10 | -0.28 | 9/12/1 | 0.66 | 0.772 | 0.50 |
| first_ok_edit | 9.16 | 11.54 | 7 | 11 | +0.32 | 11/10/1 | 1.00 | 0.721 | 0.53 |
| first_mod | 9.03 | 11.18 | 7 | 11 | +0.30 | 11/9/2 | 0.82 | 0.721 | 0.54 |
| failed_edits | 2.20 | 2.95 | 1 | 1 | -3.77 | 6/16/0 | 0.05 | 0.000 | 0.41 |
| any_failed_edit | 0.87 | 0.80 | 1 | 1 | +0.10 | 10/5/7 | 0.30 | 0.124 | 0.55 |
| err_calls | 4.47 | 5.58 | 3 | 4 | -4.21 | 4/17/1 | 0.01 | 0.000 | 0.36 |
| repeats | 3.57 | 4.62 | 3 | 3 | -3.83 | 8/13/1 | 0.38 | 0.000 | 0.40 |
| pytest_any | 0.34 | 0.10 | 0 | 0 | +0.21 | 14/3/5 | 0.01 | 0.005 | 0.60 |
| pytest_after | 0.27 | 0.03 | 0 | 0 | +0.20 | 12/2/8 | 0.01 | 0.001 | 0.60 |
| exec_after | 0.91 | 0.69 | 1 | 1 | +0.21 | 11/4/7 | 0.12 | 0.002 | 0.60 |
| calls | 28.62 | 32.31 | 28 | 38 | -3.44 | 8/14/0 | 0.29 | 0.008 | 0.36 |
| submitted | 0.82 | 0.25 | 1 | 0 | +0.56 | 19/2/1 | 0.00 | 0.000 | 0.78 |
| turns | 0.20 | 0.45 | 0 | 0 | -0.34 | 4/14/4 | 0.03 | 0.000 | 0.33 |
| timeout | 0.08 | 0.32 | 0 | 0 | -0.10 | 2/8/12 | 0.11 | 0.075 | 0.45 |
| peak_pt | 14202.95 | 15003.81 | 14662 | 14936 | -588.46 | 8/14/0 | 0.29 | 0.002 | 0.39 |

Key extra checks (sometimes tasks):

- runs with ≥5 failed edit calls: wins 16/110, losses 14/110 (sometimes tasks); all tasks wins 25/330, losses 76/960
- runs with ≥10 failed edit calls: wins 4/110, losses 10/110 (sometimes tasks); all tasks wins 9/330, losses 35/960
- sometimes-task losses by end: submitted 28, turns budget 48, timeout 34, other 0 of 110
- sometimes-task wins by end: submitted 90, turns budget 13, timeout 7, other 0 of 110
- sometimes tasks, submitted runs only: solve with comp 64/90 = 71.1%, without 26/28 = 92.9%
- MH OR(win | comp) within sometimes tasks, submitted runs only: 0.40
- MH OR(win | pytest_after) within sometimes tasks, submitted runs only: 2.04
- first compaction step (agent LLM call index): wins median 17.5, losses median 18.0
- compaction before call 15: sometimes wins 22/110, losses 31/110
- compaction before call 20: sometimes wins 59/110, losses 63/110
- Compaction OR within task: 0.43 stratified by task. Stratified by task × calls bucket (≤ 20, 21–30, > 30): **0.67**. Submitted runs only, task × bucket: **1.2**. Only 34 of 220 run-tasks never compacted, so these ORs have little information behind them.

## Results: pooled across all tasks (unpaired, confounded by task difficulty)

| feature | mean W (n) | mean L (n) | Δ |
|---|---|---|---|
| comp | 0.48 (330) | 0.86 (960) | -0.38 |
| n_comp | 0.57 (330) | 1.37 (960) | -0.80 |
| comp_before_edit | 0.02 (330) | 0.32 (960) | -0.29 |
| has_edit | 1.00 (330) | 0.92 (960) | +0.08 |
| first_edit | 6.23 (330) | 11.44 (887) | -5.21 |
| first_ok_edit | 7.16 (330) | 11.99 (869) | -4.83 |
| first_mod | 6.85 (330) | 11.72 (880) | -4.87 |
| failed_edits | 1.57 (330) | 1.91 (960) | -0.33 |
| any_failed_edit | 0.76 (330) | 0.77 (960) | -0.01 |
| err_calls | 3.73 (330) | 4.85 (960) | -1.12 |
| repeats | 2.90 (330) | 3.74 (960) | -0.84 |
| pytest_any | 0.41 (330) | 0.19 (960) | +0.22 |
| pytest_after | 0.37 (330) | 0.13 (960) | +0.24 |
| exec_after | 0.93 (330) | 0.70 (960) | +0.23 |
| calls | 23.16 (330) | 31.44 (960) | -8.28 |
| submitted | 0.93 (330) | 0.50 (960) | +0.43 |
| turns | 0.09 (330) | 0.38 (960) | -0.29 |
| timeout | 0.03 (330) | 0.19 (960) | -0.16 |
| peak_pt | 13292.31 (330) | 14844.37 (960) | -1552.06 |

## Compaction prevalence and solve rate

- all: compact (pre-submit) 983/1290 = 76.2%; any compaction incl. post-submit 1019; solve with comp 159/983 = 16.2%; without 171/307 = 55.7%
- sometimes: compact (pre-submit) 186/220 = 84.5%; any compaction incl. post-submit 192; solve with comp 84/186 = 45.2%; without 26/34 = 76.5%
- always: compact (pre-submit) 75/220 = 34.1%; any compaction incl. post-submit 88; solve with comp 75/75 = 100.0%; without 145/145 = 100.0%
- never: compact (pre-submit) 722/850 = 84.9%; any compaction incl. post-submit 739; solve with comp 0/722 = 0.0%; without 0/128 = 0.0%
- n_comp distribution (all): [(0, 307), (1, 561), (2, 337), (3, 75), (4, 8), (5, 2)]
- Mantel-Haenszel OR(win | comp) within sometimes tasks: 0.43
- Mantel-Haenszel OR(win | comp_before_edit) within sometimes tasks: 0.55
- Mantel-Haenszel OR(win | any_failed_edit) within sometimes tasks: 2.33
- Mantel-Haenszel OR(win | pytest_after) within sometimes tasks: 15.50
- Mantel-Haenszel OR(win | exec_after) within sometimes tasks: 4.19
- Mantel-Haenszel OR(win | submitted) within sometimes tasks: 9.89
- Mantel-Haenszel OR(win | turns) within sometimes tasks: 0.17
- Mantel-Haenszel OR(win | timeout) within sometimes tasks: 0.46
- Mantel-Haenszel OR(win | has_edit) within sometimes tasks: inf

The raw rates (16 % with compaction vs 56 % without) look dramatic, but the effect is almost entirely between tasks. On always-solved tasks compaction does not change the solve rate (100 % either way). On never-solved tasks it happens in 85 % of runs. Shorter runs avoid it because they submit early, and they submit early because the task is easy.

## Per sometimes-task
| task | k/10 | comp W | comp L | first_mod W | first_mod L | failed edits W | failed edits L | pytest-after W | pytest-after L | calls W | calls L | end of losses (submit/turns/timeout) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fastapi_11194 | 9 | 1.0 | 1.0 | 1.0 | 1.0 | 1.7 | 0.0 | 0.2 | 0.0 | 37.3 | 40.0 | 0/1/0 |
| fastapi_14419 | 2 | 1.0 | 1.0 | 13.0 | 16.0 | 2.0 | 1.0 | 0.0 | 0.1 | 23.0 | 28.2 | 1/2/5 |
| fastapi_14616 | 2 | 1.0 | 1.0 | 10.5 | 11.5 | 0.5 | 3.2 | 0.0 | 0.0 | 37.0 | 39.8 | 0/7/1 |
| fastapi_14873 | 9 | 1.0 | 1.0 | 10.1 | 7.0 | 1.7 | 2.0 | 0.2 | 0.0 | 34.3 | 40.0 | 0/1/0 |
| fastapi_15589 | 4 | 1.0 | 1.0 | 16.5 | 11.5 | 1.2 | 1.7 | 0.0 | 0.0 | 38.5 | 36.3 | 0/3/3 |
| fastapi_5624 | 5 | 0.8 | 1.0 | 16.4 | 20.2 | 2.0 | 5.4 | 0.0 | 0.0 | 29.6 | 38.6 | 1/3/1 |
| fastapi_9425 | 4 | 1.0 | 1.0 | 16.8 | 13.2 | 1.0 | 0.8 | 0.0 | 0.0 | 37.8 | 39.2 | 3/3/0 |
| fastapi_9753 | 8 | 1.0 | 1.0 | 9.1 | 12.5 | 3.5 | 13.0 | 0.1 | 0.0 | 34.9 | 39.0 | 0/2/0 |
| rich_2943 | 8 | 0.0 | 0.5 | 11.1 | 12.5 | 1.2 | 22.5 | 0.5 | 0.0 | 20.1 | 40.0 | 0/2/0 |
| rich_3043 | 9 | 0.8 | 1.0 | 6.0 | 10.0 | 0.9 | 0.0 | 0.6 | 0.0 | 21.9 | 14.0 | 1/0/0 |
| rich_3063 | 2 | 1.0 | 0.9 | 3.5 | 5.9 | 0.5 | 1.8 | 0.5 | 0.0 | 25.0 | 30.4 | 1/2/5 |
| rich_3278 | 9 | 0.8 | 1.0 | 6.7 | 4.0 | 1.7 | 3.0 | 0.1 | 0.0 | 24.0 | 40.0 | 0/1/0 |
| rich_3454 | 9 | 0.9 | 1.0 | 5.8 | 4.0 | 8.7 | 23.0 | 0.3 | 0.0 | 26.9 | 27.0 | 0/0/1 |
| rich_3470 | 3 | 0.7 | 1.0 | 16.3 | 16.1 | 1.7 | 2.1 | 0.0 | 0.0 | 34.7 | 39.7 | 1/6/0 |
| rich_3480 | 6 | 0.7 | 0.8 | 8.0 | 11.2 | 1.2 | 3.2 | 0.2 | 0.0 | 27.3 | 27.2 | 2/1/1 |
| rich_3506 | 2 | 1.0 | 0.8 | 7.0 | 7.5 | 1.0 | 0.6 | 0.5 | 0.0 | 21.0 | 14.6 | 2/0/6 |
| rich_3521 | 3 | 1.0 | 0.7 | 13.0 | 12.8 | 1.0 | 0.6 | 0.7 | 0.1 | 26.0 | 19.4 | 2/0/5 |
| rich_3676 | 4 | 1.0 | 1.0 | 13.0 | 12.8 | 1.2 | 4.0 | 0.0 | 0.0 | 32.0 | 31.0 | 5/1/0 |
| rich_3772 | 1 | 1.0 | 1.0 | 7.0 | 5.7 | 1.0 | 1.4 | 0.0 | 0.1 | 24.0 | 29.8 | 7/0/2 |
| rich_3777 | 1 | 1.0 | 1.0 | 34.0 | 24.3 | 1.0 | 1.1 | 0.0 | 0.0 | 40.0 | 39.7 | 2/7/0 |
| rich_3882 | 9 | 0.0 | 1.0 | 5.6 | 4.0 | 2.6 | 28.0 | 0.8 | 0.0 | 18.4 | 40.0 | 0/1/0 |
| rich_4075 | 1 | 1.0 | 0.9 | 3.0 | 3.0 | 1.0 | 2.7 | 0.0 | 0.0 | 39.0 | 34.6 | 0/5/4 |

## Losing-run patch vs winning patches (sometimes tasks)
| task | k | losses | no patch | same file set as a winner | files ⊂/⊃ winner union | disjoint | max added-line Jaccard vs winners (median) | winning file sets |
|---|---|---|---|---|---|---|---|---|
| fastapi_11194 | 9 | 1 | 1 | 0 | 0 | 0 | - | fastapi/dependencies/utils.py ×9 |
| fastapi_14419 | 2 | 8 | 3 | 3 | 2 | 0 | 0.14 | fastapi/dependencies/models.py ×2 |
| fastapi_14616 | 2 | 8 | 2 | 2 | 1 | 3 | 0.00 | fastapi/dependencies/utils.py ×2 |
| fastapi_14873 | 9 | 1 | 1 | 0 | 0 | 0 | - | fastapi/routing.py ×9 |
| fastapi_15589 | 4 | 6 | 1 | 5 | 0 | 0 | 0.00 | fastapi/dependencies/utils.py ×4 |
| fastapi_5624 | 5 | 5 | 2 | 1 | 2 | 0 | 0.00 | fastapi/dependencies/utils.py ×5 |
| fastapi_9425 | 4 | 6 | 5 | 1 | 0 | 0 | 0.33 | fastapi/routing.py ×4 |
| fastapi_9753 | 8 | 2 | 0 | 1 | 1 | 0 | 0.16 | fastapi/dependencies/models.py,fastapi/dependencies/utils.py ×6; fastapi/dependencies/models.py ×2 |
| rich_2943 | 8 | 2 | 2 | 0 | 0 | 0 | - | rich/style.py ×8 |
| rich_3043 | 9 | 1 | 0 | 1 | 0 | 0 | 0.33 | rich/_export_format.py ×9 |
| rich_3063 | 2 | 8 | 5 | 3 | 0 | 0 | 0.14 | rich/markup.py ×2 |
| rich_3278 | 9 | 1 | 1 | 0 | 0 | 0 | - | rich/ansi.py ×9 |
| rich_3454 | 9 | 1 | 1 | 0 | 0 | 0 | - | rich/highlighter.py ×9 |
| rich_3470 | 3 | 7 | 5 | 2 | 0 | 0 | 1.00 | rich/console.py ×3 |
| rich_3480 | 6 | 4 | 2 | 2 | 0 | 0 | 0.00 | rich/text.py ×6 |
| rich_3506 | 2 | 8 | 5 | 3 | 0 | 0 | 0.00 | rich/segment.py ×2 |
| rich_3521 | 3 | 7 | 5 | 2 | 0 | 0 | 0.08 | rich/segment.py ×3 |
| rich_3676 | 4 | 6 | 1 | 5 | 0 | 0 | 0.31 | rich/traceback.py ×3; rich/default_styles.py,rich/traceback.py ×1 |
| rich_3772 | 1 | 9 | 0 | 9 | 0 | 0 | 0.00 | rich/traceback.py ×1 |
| rich_3777 | 1 | 9 | 3 | 4 | 2 | 0 | 0.22 | rich/console.py ×1 |
| rich_3882 | 9 | 1 | 0 | 1 | 0 | 0 | 0.33 | rich/prompt.py ×9 |
| rich_4075 | 1 | 9 | 9 | 0 | 0 | 0 | - | rich/console.py ×1 |

Totals: losses 110, no patch 54, same file set 45, overlapping 8, disjoint 3; added-line Jaccard (best winner) median 0.02, share ≥0.5: 3/56
Baseline: winner-vs-other-winner best added-line Jaccard median 1.00 (n=107)

Patch-closeness definitions:
- **Source files:** files under a package directory (the path contains "/"), excluding `tests/`. This drops the top-level `repro*.py` scratch files.
- **"No patch":** no source-file change. These are 41 scratch-only diffs and 13 runs with no patch file.
- **Line-Jaccard:** computed on the set of stripped +/- lines in source files. A loser is compared against its most similar winner. Sets ignore indentation and order. For example, rich_3470 lora-eval-8 scores Jaccard 1.0 because it contains the winning hunk plus an extra wrong hunk that re-adds the same lines in `export`/`capture`; test_capture_and_record fails.

## Caveats

- **Small sample:** 22 tasks and 220 run-tasks. With 19 features tested, about one permutation result at p < 0.05 is expected by chance. Effects are associations, not interventions.
- **Outcome-proximal features:** submitted, turns budget, calls and peak tokens are partly consequences of failing. A run that has not found the fix keeps exploring until the budget runs out.
- **Compaction mechanics:** compaction is tied mechanically to run length (14,336-token threshold), so it cannot be separated from "the run went long" without an intervention. The clean test is an A/B run with a higher threshold or no compaction on the 22 sometimes tasks.
- **Unmeasured:** the quality of compaction summaries. The summary text is not in the traces.
- **Index approximation:** "comp before edit" compares the agent-step index of the drop with the tool-call index of the first modification. These are nearly 1:1 because each step usually makes one call.
