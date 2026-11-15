# 45 — Campaign plan to the final deadline (written 2026-11-15)

The working plan from the first held-out result to the final submission. Each
track lists what it does, the exact implementation, its gate, its cost and its
status. Status is updated in place, and results are appended to
`40-p1-implementation-journal.md`.

## 0. Facts the plan rests on

| Fact | Value | Source |
|---|---|---|
| Final deadline | 2026-12-02 23:59 UTC (17 days from writing) | `kaggle competitions list` |
| Entry / team-merger deadline | 2026-11-25 | competition overview (docs/01) |
| Submissions | **1 per day** (about 17 left) | rules (docs/01) |
| Hidden test | ~120 tasks from private repositories | data page (docs/01) |
| Scoring machine | 4×L4 (96 GB total), tensor parallel 4, offline | overview, HARNESS_README |
| Execution allowance | 12 h aggregate including setup | overview (docs/01) |
| Per-task budget | set by the submission's `eval_config.yaml`: `max_time_minutes`, `max_tool_calls`, `max_turns` (scorer defaults 60 min / 100 / 500) | HARNESS_README §7.1 |
| Leaderboard on 2026-11-15 | top **0.29**; ~14 teams at 0.24; 5,773 teams; steps of ~0.02 (one task in ~120) | `kaggle competitions leaderboard` |
| Our submissions | **none** | `kaggle competitions submissions` |
| Our local result (49 dev tasks, A100) | base agent **15/49 = 0.306**; epoch-1 adapter 13/49 | docs/44 |
| Local verifier ceiling | gold patches resolve 29/49 under the official image's packages | docs/44 |

Local scores are not leaderboard scores. The tasks differ (public dev repos
against private hidden repos), the hardware differs (A100 TP1 against 4×L4
TP4, which changes per-call latency and so how far a wall-clock budget goes),
and the sample is small. The first submission is the only calibration we can
get.

### Submission facts (2026-11-15, owner-confirmed)

| Fact | Value | Source |
|---|---|---|
| Account | `michealjiang`, display name **ZenithSync24**; confirmed by the owner | `kaggle config view`, profile page |
| Route | a private notebook writes `submission.zip`; that notebook version is submitted (`kaggle competitions submit -k michealjiang/<slug> -v <n> -f submission.zip`) | starter notebook, CLI |
| Text on submissions | the owner's name (ZenithSync24) only, technical language only | owner instruction |
| Limits | 1 per day to Dec 2; **2 final selections** | rules (docs/11) |
| Runtime rule | "12 hours to submit patches for all tasks, inclusive of sandbox setup time, excluding patch validation" | overview page |
| Official loop | the starter evaluates tasks **sequentially** and passes `build_submission_limits()` limits and generation constraints, `bfloat16`, `max_lora_rank` = largest detected rank | starter notebook |
| Public evidence | 8 min / 28 calls / 240 s / 80 turns scored 0.22 and completed; lowering those limits scored 0.13 | public notebooks (flexonafft, honghanhhh) |
| Small-model bonus | $10,000 for the best E2B/E4B entry, which must be one of the two final selections | overview page |

The first submission therefore uses **8 minutes per task**. That value has
public evidence of both completing and scoring, whereas the ~5 minutes
considered first was shown publicly to cost score.

## 1. What failed, and what each failure implies

Measured on `full-2` (docs/44), 98 agent runs:

| Failure | Base | Adapter | Lever |
|---|---|---|---|
| Patch produced but failed hidden tests | 30 | 28 | agent workflow: reproduce, then fix, then verify against the issue; test-patch awareness |
| Budget exhausted without a patch | 4 | 8 | budget sizing; earlier `submit_patch`; latency |
| Unsolvable here (gold fails) | 20 tasks | 20 tasks | none, because the official image lacks the packages |
| Adapter slower per call | — | +52% | LoRA serving cost (track C) and output length |

A top placement needs roughly 0.29 or more on the hidden set, about 35 of ~120
tasks. The levers in order of expected value per day:

1. **Budget to fit 12 h.** The whole hidden set must finish in time. Per-task
   wall clock × tasks ÷ concurrency must stay under about 11 h on 4×L4. Our
   current 10 min / 40 calls is self-imposed and probably leaves both time
   and resolutions unused.
2. **Agent workflow and prompts** (instruction text, tool policy, sub-agents
   allowed by the YAML compiler), aimed at the 30 failed patches.
3. **Generation settings** that the YAML allows (temperature, thinking
   budget, max output tokens), aimed at long reasoning turns.
4. **LoRA trained on many verified trajectories** (track D). This is the
   slowest lever, and only worth it if it beats 1–3.

## 2. Tracks, run in parallel

### Track A — measurement fidelity (in progress, pod `clju4klkb0n6tn`)

- A1. Verifier qualification with the task wheels **prepended**, closer to
  the official image, where the task wheels are the only packages: gold and
  empty patches on all 49 tasks. Gate: gold ≥ 29/49 and empty ≤ 2/49, both
  explained. `scripts/qualify_verifier.py --test-site-order prepend`.
- A2. Re-grade `full-2`'s saved patches under both orders
  (`scripts/rescore_patches.py`). The `append` run must reproduce 15/13
  exactly, which validates the re-grader. The `prepend` run gives the
  corrected result.
- A3. Adopt the order with the higher gold resolution as the default for every
  later evaluation, and record it in each receipt (`test_site`).
- A4. **Scoring-hardware fidelity.** Run every decision evaluation on
  **4×L4 with tensor parallelism 4**, which matches the scorer's per-call
  latency. Runpod L4 is about $0.43/h per GPU, so about $1.7/h for four,
  under the cap. `run_official_eval.py` currently hardcodes
  `tensor_parallel_size=1`; add `--tensor-parallel-size` and record it in the
  receipt deviations. Gate: the base agent's per-call latency and resolved
  count on 4×L4 are measured before any budget decision is made.

### Track B — agent design and budget (highest expected value)

- B1. Failure taxonomy over the 98 traces in the run archive: per task, did
  the agent reproduce the bug, find the right file, edit it, run a test, how
  many calls went where (reads, greps, pip attempts, test runs), and where
  the time went. Output: `evidence/p1/failure-taxonomy-001/`, one row per
  run, plus totals. CPU only, run on the pod now.
- B2. Candidate variants, each a submission directory differing from the
  base in one declared way (`build_eval_candidates.py` generalised to a
  declared diff):
  1. Budget: 20 min / 80 calls; 30 min / 100 calls, sized against A4's
     latency and the 12 h limit with ~120 tasks.
  2. Instructions aimed at B1's top failure modes, for example: write a
     reproduction under `/tmp` first, never `pip install`, run the test
     closest to the change, submit before 80% of the budget.
  3. Generation settings (temperature, max output tokens).
- B3. Screening: evaluate **all variants concurrently against one server**.
  The orchestrator already takes N candidates, and the A100's KV cache holds
  10 concurrent 32k contexts. Run them on the **pilot** role (20 tasks), with
  every result paired against the base under the same load.
- B4. Confirmation: the best one or two variants on the **development** role
  (29 tasks) on 4×L4. Gate to submit: better than the base on development, by
  paired difference, with no regression in budget exhaustion. The holdout
  (80 tasks) stays untouched for the final choice between the last two
  candidates.

### Track C — adapter serving cost (in progress, same pod)

- C1. `scripts/bench_lora_latency.py`: base against full / attention-only /
  MLP-only subsets of the real adapter, identical unique ~6k-token prompts,
  256 fixed output tokens, concurrency 1/4/8.
- C2. Decide the target-module set for track D from the measured time to
  first token and decode ratios. Gate: a trained adapter is only evaluated if
  its serving ratio is ≤ 1.10 at concurrency 4. Add this check to the
  evaluation runbook as a pre-flight.

### Track D — data engine for rejection-sampled fine-tuning

The adapter only helps if it learns from many verified trajectories in the
exact official harness format. There is no Docker on Runpod, so the
trajectories are generated natively:

- D1. Converter: SWE-rebench-V2 train-cohort tasks (2,076, repository- and
  owner-disjoint from the frozen confirmation cohort and from the four dev
  repositories; licences confirmed for 2,845 of 2,966 in the pool) to
  swegemma tasks. That means a `tasks.jsonl` row (`instance_id`, `repo`,
  `base_commit`, `patch`, `test_patch`, `problem_statement`), a snapshot
  `.tgz` built by `git fast-export` up to `base_commit` (no future history,
  the official rule), and an offline wheel set per repository from its pinned
  requirements at that commit (`pip download` while online, before the guard).
  The cohort-freeze gate (`check_cohort_freeze.py`) runs before anything is
  built.
- D2. Per-repository test site (`build_test_site.py` with that repository's
  wheels) and gold/empty verification per task (`qualify_verifier.py`). Keep
  only tasks where the gold patch resolves and the empty patch does not.
  CPU pod.
- D3. Pilot: the base agent (the best variant from B, once known) on 100–200
  qualified tasks, on GPU, with the official harness, recording traces.
  Measure the yield: resolved trajectories per GPU-hour, and resolved
  trajectories per task. Gate to scale: an estimate of how many GPU-hours buy
  ≥ 1,000 resolved trajectories, reported before spending them.
- D4. Corpus: resolved traces to training examples in the exact chat format
  the harness sends (the trace already holds the requests), with the existing
  masking/admission gates. The four admission gates run on the new corpus's
  own evidence.
- D5. Train with the target-module set from C2, then evaluate exactly as in
  docs/44 (pilot, then development), paired against the best non-LoRA
  variant from B, not against the original base.

### Track F — small-model bonus ($10,000, best E2B/E4B entry)

- Public small-model leaderboard (host notebook, 2026-11-15): top **0.12**, a
  large cluster at 0.10, against 0.29 on the main board. It is far less
  contested.
- An E2B/E4B entry must be one of our **two final selections**. The plan:
  final selection 1 is the best 31B configuration, and selection 2 is the
  best E4B configuration if it leads or is near the top of the small-model
  board.
- F1. Weights: E4B `model.safetensors` is 11.5 GB (8 files). A pod fetches
  them through signed per-file URLs (`scripts/kaggle_model_urls.py`, no
  credential on the pod), computes digests, uploads to R2 by digest (presigned
  PUT), and they are verified locally by a streamed read.
- F2. Screen the 31B winners' agent designs on E4B (same harness, 49 tasks);
  E4B is faster per call, so budgets may differ.
- F3. Submit the best E4B configuration once it beats the small-model board's
  visible top on local evidence.

### Track E — submissions (each needs the account owner's go-ahead)

- E1. **Calibration: submit the current base agent** (`evidence/p1/base-agent-001/submission.zip`)
  to get a real leaderboard score. Every later decision depends on how local
  scores map to it.
- E2. One submission per day after that: only a variant that passed B4 (or
  D5).
- E3. Before Nov 25: confirm the team and entry state.
- E4. Final selection: the two best by local development score and public
  leaderboard score, decided on the untouched holdout.

## 3. Cost guardrails

- ≤ $5/h per pod at all times, never H200. Pods are terminated when idle, and
  every deletion is confirmed with a fresh read.
- Planned spend: A ≈ $3 (running); A4 ≈ $2 per 4×L4 evaluation; B ≈ $4–6 per
  screening round (pilot, all variants concurrently); D1–D2 CPU ≈ $1–3; D3
  pilot ≈ $3–5; D scale-up is reported first (estimated $40–60).

## 4. Status log

| When (UTC) | Item | State |
|---|---|---|
| 11-15 07:14 | Pod `clju4klkb0n6tn` (A100, $2.19/h) for A1–A2, B1, C1 | running |
| 11-15 07:40 | Plan written; leaderboard read (top 0.29); no submission yet | done |
| 11-15 07:55 | Single R2 connection throttled to ~1.5 MB/s; fetch now 8 files at a time (`5b088e9`) | fixed |
| 11-15 08:00 | 4×L4 out of stock on Runpod secure cloud (L40/L40S too); A4 blocked, re-check daily | blocked |
| 11-15 08:05 | B1 failure taxonomy (base, 49 runs): resolved runs ran a test 67% / submitted 87% / first edit at call 6; failed-patch runs 13% / 33% / 10.5; out-of-budget runs first edit at call 37; graph tools ~0.1–0.3 calls per run, so D skips graph construction | done |
| 11-15 08:10 | Scorer concurrency is not configurable and not documented; `eval_config.yaml` sets only the four budget keys. Budgets stay at the current scale until the calibration submission shows where the time goes | open |
| 11-15 08:15 | Official sample prompt (fix within 8–10 turns, targeted test, immediate submit; temp 0.2, think 4096) added as a screening candidate | done |
| 11-15 07:40 pod | A1: task wheels first (`prepend`) resolve gold 22/49 against 29/49 for `append`; the 7 lost tasks are all fastapi (newest starlette wheel). `append` stays the default, chosen by the screening job's own rule | done |
| 11-15 07:40 pod | A2 crashed: `--results` parsed as a path (`edf9735` fixes it); the job's `| tail -1` hid the exit code. A2 is dropped: re-grading under the rejected order has no decision value | fixed, dropped |
| 11-15 08:30 | Owner approved the first submission: the screening winner with the runtime-safe budget, name ZenithSync24 only, technical text | approved |
| 11-15 08:35 | Local evaluation now passes the official limits and generation constraints, `bfloat16`, and `max_lora_rank` from detected ranks (`3406dc2`); the screening pulls this before starting | done |
| 11-15 08:40 | Packager: candidate to private notebook, deterministic `submission.zip` with its sha256 checked inside the notebook (`cfa3001`) | done |
| 11-15 08:04 pod | C1 LoRA latency (4,527-token prompts, 256 fixed output tokens): any adapter costs time per call of 1.30× (c=1), 1.16× (c=4), 1.13× (c=8) against base; decode 0.73/0.86/0.89×. Full, attention-only and MLP-only are identical to 3 decimals, so the cost is fixed, not per module. vLLM already served max-lora-rank 8, so the rank fix changed nothing. Gate C2 (≤ 1.10 at c=4) fails for every target set. To check: that the subset adapters actually change outputs (the identical figures could mean they are not applied) | done, caveat open |
| 11-15 08:05 | Decision: LoRA has a fixed ~16% wall-clock tax under the time budget. Track B (no serving cost) takes priority; track D proceeds only if a measured agent gain can exceed that tax | decided |
| 11-15 10:21 pod | **screen-1 complete** (49 tasks, 3 agents per candidate, concurrent): sample_oursampling **15**, base 14, workflow 14, sample 12. Paired against base: +2/−1, +2/−2, +1/−3 (all p ≥ 0.63). Median task time 510 s against 604 s for base; out of budget without a patch 5 / 6 / 18 / 5. No patch touches a test file; the air gap held afterwards; the data and candidates were unchanged. The 15 vs 14 margin is noise (the same base scored 15 in full-2); the speed gain is systematic | done |
| 11-15 10:21 | Selected **sample_oursampling** (official sample instruction, our sampling). Rule winner: equal or better accuracy and 15% faster per task, which matters under a fixed wall clock on slower L4. Projected sequential runtime at an 8-minute cap: 14.6 h for 120 tasks, over 12 h if the scorer is sequential; public 8-minute configs scored, so the scorer is concurrent or truncates. Kept 8 min | decided |
| 11-15 10:22 | screen-1 archived: `artifacts/v1/runs/2026-11-15/screen-1.tar`, sha256 `ed98cc2f…`, 31,621,120 B, verified by streamed read-back | done |
| 11-15 10:24 | **Submission 1**: kernel `michealjiang/zenithsync24-agent-v1` v1, zip sha256 `cd9dbad7…` (local package = notebook assert = downloaded output). Files: agent.yaml `504d63de…`, sampling `5cbfd223…`, eval_config `404b197b…` (8 min / 40 calls / 40 turns / 120 s), system.md `f1cbf794…`. `validate_directory` passed with the official limits | pending score |
| 11-15 12:27 pod | **screen-2 complete** (all at 8 min): ref8_callplan_nograph **14**, ref8 12, ref8_callplan 12, ref8_nograph 12. Winner +2/−0 against ref8 (p = 0.5); out of budget without a patch **5 vs 11**; paired time equal (p = 0.10). Integrity: data and candidates unchanged, air gap held, workers exited 0, no test edits. The same agent as ref8 scored 15 at a 10-minute cap in screen-1 against 12 at 8 minutes here, so the cap may cost ~3 tasks or this is noise; screen-3's replicate measures the noise | done |
| 11-15 12:29 | screen-2 archived: `artifacts/v1/runs/2026-11-15/screen-2.tar`, sha256 `0efdf6f2…`, 25,466,880 B, verified by read-back | done |
| 11-15 12:30 pod | screen-3 started: reference = ref8_callplan_nograph; ref_repeat (byte-identical, measures run-to-run noise); think1024; think4096 | running |
| 11-15 18:28 pod | **screen-4 complete** (budget sweep on callplan_nograph, 4 agents each): b8 13, b10 14 (+1/−0, the noise floor), b12 13 (+2/−2). Out of budget without a patch 9 / 2 / 1. Paired task time against b8: **+119 s (p = 0.01)** and **+91 s (p = 0.03)**. More time turns budget exhaustion into failed patches, not resolutions, and costs significant runtime. **8 minutes stays.** The earlier 3-task gap between screen-1 (10 min) and screen-2 (8 min) was load and noise, not budget | done |
| 11-15 18:29 | Final archive `artifacts/v1/runs/2026-11-15/screen-4-and-final.tar` (screen-4, all logs, workspace scripts, test-site record, submission-1 package), sha256 `e0897099…`, 21,616,640 B, verified. All run directories are covered by today's five archives; the two `rescore-*` directories are empty (dropped A2) | done |
| 11-15 19:17 pod | **e4b-screen-2 started** (5 candidates, 8 min, reference e4b_base): e4b_base (replicate), e4b_think8k (thinking budget 8,192), e4b_workflow (workflow-v1 addendum), e4b_verify (new verify-v1 addendum: reproduction must fail before the edit and pass before submitting), e4b_verify_think8k | running |
| 11-15 19:16 | E4B weights uploaded from the pod by presigned multipart PUT (`r2_handoff.py presign-blob`, `put_parts.py`; 22 parts of 512 MiB for `model.safetensors`). The first attempt failed: the egress guard's DNS blackhole is system-wide and also cut the root upload already running, which confirms the air gap covers root. Re-run after the guard was removed. Completion and digest read-back done locally for all 8 blobs; manifest `16e2b001…` committed (`artifacts/v1/manifests/sha256/16e2b001….json`, 8 files, 11,546,103,780 B, every blob re-verified by streamed read). Digests are our own (computed on the pod from the Kaggle download; sizes match the Kaggle listing) | done |
| 11-15 19:15 | e4b-screen-1 archived: `artifacts/v1/runs/2026-11-15/e4b-screen-1.tar`, sha256 `8de27a51…`, 17,479,680 B, verified by streamed read-back | done |
| 11-15 19:12 pod | **e4b-screen-1 complete** (49 tasks, 4 agents each): e4b_base **7**, e4b_sample 7 (reference; +1/−1), e4b_cpng 5 (+1/−3). Median task 95 / 101 / 78 s; out of budget 0 / 1 / 0; projected sequential 120 tasks 5.2 / 5.9 / 4.9 h. Integrity: data verified, candidates unchanged, air gap held, guard removed. **Taxonomy: the dominant E4B failure is a wrong patch submitted early**: e4b_base 35/49 patch_failed_verification after a median of 10 calls and 93 s; resolved runs also short (9 calls, 60 s). E4B uses about a fifth of its 8-minute budget, so the lever is verification, not time. The callplan design that helped 31B hurts E4B (it pushes an early edit) | done |
| 11-15 18:33 pod | Track F: pod `rho6c1imvim7mj` (A100, $2.19/h). Chain: setup (devset by presigned URL; E4B weights from signed Kaggle URLs, 16 parallel ranges, digests in `/mnt/data/e4b-digests.json`), then **e4b-screen-1**: e4b_base, e4b_sample (official instruction, reference), e4b_cpng (callplan_nograph design), all `--model gemma-4-e4b-it-qat-w4a16-ct` at 8 min, 49 tasks, 4 agents each, paired. Afterwards the weights go to R2 by digest | running |
| 11-15 18:30 | **Pod `clju4klkb0n6tn` deleted**, confirmed with a fresh read (404); no project volume exists. Session cost ≈ 11.25 h × $2.19 ≈ $24.60 | done |
| 11-15 16:33 pod | **holdout-1 complete** (80 holdout tasks, verifier gold 45/80 and empty 3/80): callplan_nograph **18/80**, submitted 18/80; discordant 3/3; out of budget without a patch **10 vs 15**; paired time equal. Integrity: the receipt records roles=['holdout'] and the justification; 524 data files verified; candidates unchanged; air gap held; workers exited 0. callplan_nograph's flagged "test edit" is a stray `repro_test_sse.py` at the workspace root (agents still leave scratch files despite the instruction, a known weakness) | done |
| 11-15 16:34 | **Rule applied**: pooled discordant pairs over screen-2 and holdout-1 (129 paired tasks), callplan_nograph-only 5 against submitted-only 3, so (1) holds; out of budget 10 ≤ 15, so (2) holds. **Submission 2 = callplan_nograph.** The resolved gain is not significant (5 vs 3); the consistent effect is fewer out-of-budget runs (5 vs 11, 10 vs 15) | decided |
| 11-15 16:36 | holdout-1 archived: `artifacts/v1/runs/2026-11-15/holdout-1.tar`, sha256 `e35aad3a…`, 28,559,360 B, verified | done |
| 11-15 16:40 | Submission-2 package built and checked locally: files agent.yaml `4f48dc18…` (six tools, no graph tools), sampling `5cbfd223…`, eval_config `404b197b…` (8 min / 40 / 40 / 120 s), system.md `1fb83636…`; `validate_directory` passed on the pod; zip sha256 `49282ef9…`; kernel `michealjiang/zenithsync24-agent-v2`. Submit after the 00:00 UTC daily reset | queued |
| 11-15 16:45 pod | screen-4 started: budget sweep on callplan_nograph, b8 (8 min/40/40), b10 (10/50/50), b12 (12/60/60), 4 agents each, paired | running |
| 11-15 15:35 | **Pre-registered rule for submission 2**, written before the holdout finishes: submit callplan_nograph only if (1) pooled over screen-2 and holdout-1 (129 paired tasks) its candidate-only resolutions exceed the submitted config's reference-only resolutions, and (2) its out-of-budget-without-patch count is not higher than the submitted config's on the holdout. Otherwise no new configuration is submitted on agent-quality grounds | pre-registered |
| 11-15 14:20 pod | **screen-3 complete** (reference ref8_callplan_nograph, 8 min): ref 13, **ref_repeat 14 (byte-identical copy: +1/−0, so the within-run noise floor is about 1 task flip)**, think1024 13 (same resolved set as ref), think4096 14 (+1/−0, equal to the noise). Thinking budget shows no effect. Across runs the same config moved by up to 3 tasks (different cap and co-load), so decisions use paired within-run comparisons. think1024's flagged "test edit" is a stray `repro_test_escaping.py` at the workspace root, not a test change | done |
| 11-15 14:22 | screen-3 archived: `artifacts/v1/runs/2026-11-15/screen-3.tar`, sha256 `1a869c99…`, 25,098,240 B, verified | done |
| 11-15 14:25 pod | Holdout chain: fetch the 80 holdout snapshots (445 present files skipped) and verify; qualify the verifier (gold/empty) on 80 holdout tasks; paired callplan_nograph vs submitted (ref8) on all 80, with a recorded holdout justification. Decides submission 2 | running |
| 11-15 10:40 | **Correction** to the 10:21 selection note: paired by task, sample_oursampling and base differ by a median of −1 s (faster on 23 tasks, slower on 14; sign test p = 0.19). The median gap 510 vs 604 s came from capped runs, not consistent speed. Neither accuracy nor speed differs significantly. The submission remains rule-valid (≥ reference) but has no demonstrated edge. Consequence: 49-task screens detect only large effects, so decisions now pool repeated runs and the 80-task holdout, and large-effect interventions come first | corrected |
| 11-15 10:30 pod | screen-2 started (all at the 8-minute submission budget): ref8 = winner; ref8_callplan; ref8_nograph; ref8_callplan_nograph. The first start was stopped after ~1 min: the sample instruction told the agent to use `search_similar_code`, a tool the nograph variants remove. Fixed by replacing that one line with an equivalent `git grep -n -F` instruction; checked that no graph tool is named in their prompt or tool list | running |
| 11-15 09:25 | Holdout snapshots in R2: 80 files, 13.31 GB, manifest `6b84791b…` (69 uploaded; 11 already present by digest). Holdout evaluation needs `--roles … --holdout-justification`, recorded in the receipt (`015eeec`) | done |
| 11-15 09:25 | Owner rule: archive every pod's outputs to R2, verify by digest, then delete the pod promptly (`scripts/r2_handoff.py`, memory `pod-teardown-rule`) | in force |
| 11-15 08:58 | Checked: the official GenerationConstraints only bound max_output_tokens and thinking_budget (≤ 32,768) and supply defaults (16,384 / 4,096) when unset. Every candidate sets both, so omitting the constraints earlier changed no result. The submission limits (3 GiB, extensions .json/.yaml/.yml/.py/.safetensors/.txt/.md) apply to packaging | done |
| 11-15 09:00 | Owner granted standing autonomy for Kaggle submissions (best-only, ZenithSync24, technical text), with a status update every 10 min during long jobs (memory `kaggle-submission-autonomy`) | in force |
| 11-15 08:50 | Owner: submit the screening winner when screening completes (~12:00 UTC / 04:00 PST), not the base now. A base 8-minute package was built (zip sha256 `aae035bd…`, README removed) and not submitted | held |
| 11-15 08:20 | Chain on pod: A1 verify (prepend), A2 re-grade ×2, C1 latency bench, then screen-1 (base, workflow, sample, sample_oursampling; 49 tasks; 3 agents each, concurrently) | running |
