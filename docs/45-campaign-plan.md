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
- F4 (from e4b-screen-1/2). Prompt, workflow, verification and thinking budget
  do not change E4B's resolved set; capability does. A LoRA on E4B is the
  remaining lever, and the 31B objection to LoRA (a ~16% wall-clock tax under
  the time cap) does not apply: E4B uses about a fifth of its 8-minute budget.
  Its first gate is the E4B v1 public score (submitted 11-16).

### Round protocol and timeline (owner request 11-17: timeline, stricter verification, steady progress)

Every fine-tuning round passes these gates in order; a failed gate stops the round, is logged, and is
fixed before anything downstream spends GPU time.

| Gate | What must hold | Tool |
|---|---|---|
| G0 data | packs gold/empty-qualified; R2 copies verified by HEAD (size + md5) | `rebench_pack_pipeline.py`, `presign_pack_uploads.py check` |
| G1 trajectories | resolved by swegemma under the egress guard; air gap held after the run; archive verified | `run_rebench_rollouts.py` receipt |
| G2 corpus | tokenization exact (pinned template), no truncation, alignment screen, freeze gate, two-layer verification, admission | `audit_replay_history_tokens.py`, `screen_task_alignment.py`, `admit_training_corpus.py` |
| G3 round | session complete (one checkpoint per update), checkpoint and export identities, loss falls (last third < first third), memory, adapter finite and non-zero | `verify_training_round.py` (`e0ba31b`, `ff75ea7`) |
| G4 serving | official VllmServer lists the adapter; greedy outputs differ from the base and both parse | `qualify_lora_serving.py` |
| G5 evaluation | paired, same server, 129 official development tasks, pre-registered rule, air gap, data/candidates unchanged | `run_official_eval.py`, `select_candidate.py` |
| G6 submission | package `validate_directory` with the official limits; notebook output zip digest = local package digest; only then submit | notebook builder, download check |

Timeline (UTC; each date is a target, the gates decide):

| When | Step |
|---|---|
| 11-17 01:00 | train-002 ends → G3 → G4 → G5 (v2 vs v2+adapter-002, ~4 h) |
| 11-17 ~05:30 | G5 decision by the pre-registered rule; archive; delete the pod after verification |
| 11-17 (E4B score, then each score) | submit the best G5-supported configuration (v2, or v2+adapter if it passed) |
| 11-17–18 | round 2 data: rollouts on the 445-task development cohort (converted like the train cohort; never the confirmation cohort) with the best agent; more tasks per GPU-hour via fewer agents per GPU if contention dominates |
| 11-18 | E4B adapter trained on the same corpus (distillation from 31B trajectories); G3–G5 on E4B |
| 11-19–20 | train-003 on the merged corpus; G3–G5 |
| 11-21–30 | repeat rounds while each one improves G5; submit after every score |
| 12-01 | final selection: best 31B and best E4B by G5 evidence and public scores |

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
| 11-15 20:06 | Both notebooks pushed and COMPLETE; downloaded outputs match: E4B v1 zip `65a7f72e…` (agent.yaml declares `gemma-4-e4b-it-qat-w4a16-ct`), v2 zip `49282ef9…`. Ready to submit at the daily resets | ready |
| 11-15 20:00 | **Submission order changed** (dates only; the configurations are unchanged): 11-16 00:00 UTC slot → **E4B v1** (`michealjiang/zenithsync24-agent-e4b-v1`, zip sha256 `65a7f72e…`); 11-17 slot → 31B v2 (callplan_nograph, `49282ef9…`). Reason: v2's expected gain over v1 is small and not significant (pooled 5 vs 3), and v1 already calibrates the 31B track, whereas no E4B score exists and the next E4B step (a LoRA, below) needs several days of lead time before Dec 2. An E4B score is the larger unknown. E4B projects 5–6 h sequential for 120 tasks, so it is runtime-safe | decided |
| 11-16 00:01 | E4B v1 submit **rejected (HTTP 400)**: "Your team already has 1 pending submissions; please wait for one to finish scoring." New constraint: **at most one pending submission per team**, on top of 1/day. Submission 1 is still PENDING after 13.6 h, so scoring takes over 12 h (queue plus run) and the real throughput is about one submission per scoring cycle. E4B v1 goes in as soon as submission 1 leaves PENDING (5-min poll); the zip was re-verified (`65a7f72e…` = package). Plan impact: 31B v2 and any E4B LoRA candidate each wait for the previous score, so the queue holds at most about 13 more submissions before Dec 2 | waiting |
| 11-16 ≤10:47 | **Submission 1 scored 0.17 public** (COMPLETE; the exact completion time is unknown, between 06:18 and 10:47). Leaderboard snapshot at 10:48: rank 2798 of 5,867 teams; 1,740 teams above 0.17 and 1,068 tied at it. Score distribution: 0.29 (1 team, Yurnero), 0.24 (14), 0.22 (102), 0.20 (515), 0.18 (1,108), 0.17 (1,068). **Calibration:** the local 49-task estimate (~0.22–0.29) overstated the public score, so the local harness is optimistic, and local gains must be discounted until a second score shows the local-to-public mapping. The poll bug: the 00:01 poll exited at 06:18 on an empty CLI reply (no status line), not on a status change; the new poll matches the submission's line and requires COMPLETE or ERROR | done |
| 11-16 10:47 | **Submission 2: E4B v1** (`michealjiang/zenithsync24-agent-e4b-v1` v1, zip sha256 `65a7f72e…` re-verified before submit). Accepted, PENDING | pending score |
| 11-16 10:55 | **Goal raised by the account owner: a top-10 rank.** Today that means beating the 14-team 0.24 cluster (a tie at 0.24 would rank about 16th; ties appear to be ordered by submission time, to be verified). Fastest evidence: public notebooks titled LB 0.22–0.24 that use the same model, so their configurations are being diffed against our 0.17 package (setting by setting, with prompts) before any further GPU spend. Every constraint still holds: ≤ $5/h, no H200, data only in R2, pods archived, verified and deleted | in progress |
| 11-16 11:10 | **Public-notebook diff** (11 notebooks pulled as untrusted data, read and never executed; prompts kept in scratchpad `pubnb_extracted/`). LB mechanics: **58 public tasks**; truncated k/58 reproduces every board value (0.17 = 10, 0.18 = 11, 0.20 = 12, 0.22 = 13, 0.24 = 14, 0.29 = 17), so we are 4 tasks behind 0.24 and 7 behind 0.29. **Identical bytes give different scores** (claimed by notebook authors, bundles matched by hash): Budget-Fit, 10 draws: 8–11, mean 10.0; flexonafft V10 (the "0.22" bundle), 8 draws: 7–13, mean 9.25; the "0.24" recipe re-scored 0.12. Median submissions per team: 28 at 0.24, 21 at 0.22, 7 at 0.17. A 10-task agent reaches ≥14 in ~1–4% of single draws, ~20–60% over 22 draws. **So the 0.24 cluster is mostly the maximum of many noisy draws; no public bundle shows a mean above ours (10).** Config diff: every ≥0.22 bundle drops the graph tools, sets an edit-by-call-12 deadline and a never-empty rule, and states budget numbers. **Our v2 (callplan_nograph) already does all four**; the remaining differences are max turns 80 vs 40 (7 of 3,476 public local runs hit the turn cap), temperature 0.2/top_p 0.95 (ablations show no effect), and 240 s per-call timeout (contradictory evidence) | done |
| 11-16 11:12 | **Strategy decision.** (1) The final ranking uses the private score of the two selected submissions, and public luck does not carry over to it, so a top-10 finish needs a **real gain of about 3 or more tasks per 58** in true mean; prompt-level levers are worth about 0–2. (2) Submit v2 at the next free slot (it is our best-supported configuration and matches the public consensus). (3) Every later daily slot goes to the best-supported configuration, which also lifts the public maximum. (4) The remaining large lever is **capability**: a LoRA trained on verified trajectories (31B track D, and E4B F4), with the 31B time tax (~16%) measured against its gain on the 80-task holdout. Large-effect work comes first; 49-task screens are only for large effects | decided |
| 11-16 11:15 | **Track D started (fine-tuning data).** Hidden test tasks come from private repositories (docs/01), so the data must generalise across repositories: SWE-rebench-V2 train cohort (2,076 tasks / 277 repositories, repository- and owner-disjoint from the frozen confirmation cohort and from fastapi/rich/requests/httpx). Route: D1 conversion → D2 gold/empty qualification → D3 rejection-sampled rollouts of our own agent (v2) in the official harness → only resolved trajectories, in the exact format the harness sends | in progress |
| 11-16 11:25 pod | CPU pod `gnhxl12bt62h3s` (cpu3g, 16 vCPU, $0.64/h). Probe: the official snapshot is a fresh repository built by `git fast-export` up to `base_commit`, branch `main`, archived from its root (fastapi_14099: 215 MB, one pack); tasks.jsonl keys `base_commit, created_at, hints_text, instance_id, patch, problem_statement, repo, test_patch`; the sandbox image is python:3.13-slim plus pytest, pytest-timeout 2.1.0 and build backends. All 2,076 train rows carry `install_config` (`install` commands, `test_cmd`, base image python_base_310 for 1,697 and python_base_37 for 379) | done |
| 11-16 11:40 | `scripts/build_rebench_tasks.py` (`be3960f`): per repository, bare clone, one official-format snapshot per task (tree identity checked against `base_commit`, no future commits), one test site built from the task's own install commands in a throwaway venv, with the repository's own distribution removed (found by its PEP 610 direct URL) and the image's packages added. System commands (apt-get, curl, rustup, conda) are skipped and recorded, so tasks that need them fail qualification. Refuses any overlap with the confirmation cohort. Tests: snapshot has the exact tree and no future history; selection; command filter. Pilot running: 10 repositories × 3 newest tasks, then gold/empty qualification per repository as the evaluator under the egress guard | running |
| 11-16 11:45 pod | **Pilot 1** (10 repositories, 26 tasks): gold 7/26, empty 0/26. Failures: (a) the evaluating venv's packages (numpy) shadow the task's under `append`; (b) the repository is not importable (subliminal: src layout; covalent: reads its own metadata); (c) Python 3.12 incompatibilities (`collections.Callable`, `numpy.longfloat`); (d) environment-dependent tests inside the test files (loguru). Fix 1: PEP 518 build requirements into the site (`11425f2`); fix 2: `--test-site-order prepend` for converted tasks. `scripts/run_rebench_rollouts.py` (`6b43d51`): one official VllmServer, one `run_official_eval.py --worker` per repository pack with its own test site prepended, qualified tasks only | done |
| 11-16 12:04 pod | **Pilot 2**: unchanged (gold 7/26). Root cause of (b): swegemma's `install_editable_package` returns early for the subprocess sandbox (the Docker scorer installs `-e /workspace`); only `PYTHONPATH=/workspace` is set, and the test site is reached as a plain path from `_host_env.pth`, so its `.pth` files never run. Fix (`478a2fe`): keep the repository's dist-info, delete its code copies and import hooks, map each top-level package directory (e.g. `src/`) onto the run-time workspace, and process the site's `.pth` files through a shim named `apport_python_hook` (Ubuntu's stdlib sitecustomize imports it from sys.path). Local data-generation plumbing only | done |
| 11-16 12:50 | **Local machine restarted.** Lost: the scratchpad (local venv, working copies of the v1/v2/E4B packages, background polls). Unaffected: repository, R2, Kaggle (E4B v1 still pending), the CPU pod (pilot 2 finished at 12:04; the pod idled until 12:55). Restored: local venv (`ctvenv`), E4B poll. The v2 package is re-derivable from its Kaggle notebook output and is checked against its recorded zip digest `49282ef9…` before submission | recovered |
| 11-16 12:55 pod | Pilot 3 (editable-install reproduction, prepend): gold 7/26. subliminal still unimportable (hatch editable records no top-level names; fixed in `a6156c0` by mapping a `src/` layout directly); yotta's qualification **crashed the host worker** under `prepend` (old task packages shadowed the host's imports: `collections.Hashable`). Fix (`82ab21b`): host order stays `append`; the site's shim moves the site ahead of every other site-packages inside the sandbox only | done |
| 11-16 13:36 pod | **Pilot 5** (all fixes): **gold 10/26, empty 0/26** (yotta 1/2, WALinuxAgent 2/3, chime 2/3, loguru 2/3, GPflow 1/1). Residual losses are genuine: Python 3.12 incompatibilities (serpent-tools, covalent), tests needing network or a running server (subliminal now imports: 40 passed, 5 network errors), failed dependency installs (CTFd). Projected yield about 35–40% of tasks | done |
| 11-16 13:37 pod | **Full D1/D2 run started** on all train-cohort repositories (`scripts/rebench_pack_pipeline.py`, `78df0b5`): batches of 24 repositories, 8 build processes (network open) → egress guard → 4 parallel qualifications × 3 → guard removed → qualified tasks only, archived per repository and PUT to `artifacts/v1/runs/2026-11-16/rebench-packs-train/<slug>.tar` (presigned, 36 h; `scripts/presign_pack_uploads.py`, `0f4f71e`), then deleted from the pod. Integrity: the pod records sha256, md5 and size; `presign_pack_uploads.py check` compares R2's size and ETag by HEAD, so nothing is downloaded locally. Pilot directories (7.6 GB per 10 repositories) removed to free disk. Note: 278 repositories map to 277 lower-case slugs (one case-variant pair shares a key); to resolve before rollouts | running |
| 11-16 14:30 | Batch timing measured at 35–40 min per 24 repositories (about 7 h serial). **Second CPU pod** `q62rbuxex8xoz0` (cpu3g 32 vCPU, $1.28/h) takes repositories 140–278 (12 build, 6 × 3 qualification processes); pod 1 resumes on 1–139 after its batch 2 (resume is idempotent through shipped.jsonl). Spend $1.92/h | running |
| 11-16 14:50 | Progress: 48 repositories, 360 tasks, **120 qualified (33%)**, 0 empty-resolved; 27 packs shipped and verified by HEAD (16.1 GB). **Contamination guard:** `textualize/rich` (an official development repository: 47 of our dev/holdout tasks) reached the train cohort because the pool's exposure ledger predates the official devset. Packs of fastapi, rich, requests and httpx are never handed to rollouts or training (`e5d8c4c`); rich's pack stays in R2 unused | done |
| 11-16 14:55 | GPU for rollouts: A100 SXM/PCIe (secure and community) and RTX PRO 6000 have no capacity; 48 GB cards cannot hold one 32,768-token context beside the 31B weights (the A100 itself had 55,008 KV tokens); H100 SXM/NVL would exceed the $5/h cap while both CPU pods run. Retry every 10 min; fall back to H100 NVL ($3.19/h) once the CPU pods are deleted | waiting |
| 11-16 15:02 pod | A100 SXM secured: pod `cfne7gn2sgm0d9` ($2.19/h; total $4.11/h). Wave 1: 26 packs (rich excluded), 15.6 GB, every pack's size and md5 checked on download; model fetched from R2 by digest | done |
| 11-16 15:33 pod | **Wave 1 (v2, 8 min) stopped early**: 2/16 resolved, 10 of 14 failures were the 8-minute wall cap after only 10–23 calls. 12 agents share one A100 (100% util, ~40 s per call); the official scorer runs one task at a time, so the wall cap binds far harder here than in scoring. **Wave 1c**: same v2 files except `max_time_minutes: 20` for rollouts only (40 calls / 40 turns / 120 s unchanged, so trajectories stay inside the official call budget). Partial wave 1 archived: `runs/2026-11-16/rollouts/wave1.tar` (md5 `f2c47c95…`). Incident: SIGTERM to the orchestrator left the old vLLM engine and workers alive and the new orchestrator attached to the old server; all killed by PID, GPU confirmed at 0 MiB before wave 1c started (`wave1b.tar` is a 40 KB discard, overwritten by wave 1c). `--skip-done-from` resume added (`a6d613a`) | running |
| 11-16 15:40 pod | cfn-lint stalled pod 1's batch for 50+ min (12 full-history fast-exports at ~4.5 min each). Fix (`955dd53`, pulled on both CPU pods between batches): newest task first; a repository whose first snapshot takes > 120 s keeps only its 4 newest tasks | done |
| 11-16 15:50 pod | keras (12 tasks, 11 qualified) failed to ship: a 5.9 GB pack exceeds a single R2 PUT (5 GiB). Fix (`abcaf41`): packs over 4.8 GB are gzipped (level 1; `tar xf` detects it). Both CPU pipelines restarted during a build phase (resume via shipped.jsonl), keras re-queued with its qualification redone; it shipped at 3.27 GB. pdm-project/pdm did not build (recorded `not_built`) | done |
| 11-16 17:32 pod | **Wave 1c complete**: 116 qualified tasks (26 packs), **29 resolved (25%)**, receipt `completed`, air gap held after the last worker. Archive `runs/2026-11-16/rollouts/wave1b.tar` (holds `rollouts-1c`), 17,111,040 B, md5 `d2e4f7c6…`, verified by HEAD. Throughput ≈ 48 tasks/h at 12 agents | done |
| 11-16 17:33 pod | Wave 2 queued and started on the same A100: 68 packs (37.1 GB, all verified by HEAD), the remaining shipped packs of both CPU pods at 17:20 | running |
| 11-16 17:33 | Conversion: 168 repositories, 431 qualified tasks (pod 1: 256, pod 2: 175) | running |
| 11-16 18:25 pod | scrapy's first fast-export ran 49 min: its builder was killed (scrapy recorded `not_built`). Fix (`fede6f6`): a 15-minute ceiling per snapshot; a timed-out first snapshot ends the repository | done |
| 11-16 18:45 pod | **CPU pod 1 finished and deleted** (`gnhxl12bt62h3s`, 404 confirmed; ≈ 7.6 h × $0.64 ≈ $4.9): 139 repositories, 76 packs shipped, **319 qualified**, 63 with none qualified. All 115 packs shipped so far by both pods verified by HEAD (64.1 GB). Logs and qualification results archived: `runs/2026-11-16/rebench-train-pod1-logs.tar`, 110,960,640 B, md5 `1d695363…`, verified | done |
| 11-16 19:14 pod | **CPU pod 2 finished and deleted** (`q62rbuxex8xoz0`, 404 confirmed; ≈ 4.7 h × $1.28 ≈ $6.0): 139 repositories, 72 shipped, **305 qualified**, 63 none qualified, 4 not built (pdm, scrapy and two others). **D1/D2 total: 278 repositories → 148 packs, 624 qualified tasks** (rich's pack excluded from use). All 148 packs verified by HEAD (79.5 GB). Logs archived: `runs/2026-11-16/rebench-train-pod2-logs.tar`, 70,625,280 B, md5 `d6d2cc37…`, verified | done |
| 11-16 19:15 pod | **Second A100** `vplav4wbke2bo9` ($2.19/h; total $4.38/h): wave 3 = the remaining 53 packs (26.3 GB), same v2r agent (20-min wall cap, 40 calls / 40 turns) | running |
| 11-16 19:55 | **D4 converter** `scripts/trace_to_history.py` (`eb8c288`): resolved ATIF traces → `history.json` (system, user, assistant {reasoning, tool_calls}, tool results bound by call id, final content) + `tools.json` (the exact schemas of a captured harness request, filtered to v2's six tools) + receipt; recorded text only; refuses ambiguous traces; one history per task; official development repositories excluded. Dry run on wave 1c (pod, network blocked, script passed in): **29/29 written, 0 refused, 0 `normalize_history` failures**. Next: tokenize with the pinned tokenizer (`audit_replay_history_tokens.py`), check the captured tool schemas against the live harness, assemble and admit the corpus | done |
| 11-16 20:30 pod | Progress: wave 2 197/311 (51 resolved), wave 3 65/193 (18 resolved); 100 resolved trajectories in total so far (wave 1c 29, wave 2 51, wave 3 18, partial wave 1 2). Combined throughput ≈ 144 tasks/h on two A100s | running |
| 11-16 20:31 pod | **Retry passes queued** (`b34dda3`, `--skip-resolved-from`): when each wave ends, the same A100 re-runs that wave's *unresolved* tasks with v2 at temperature 0.6 / top_p 0.95 (20-min wall cap; 40 calls / 40 turns), for more resolved tasks and sampling diversity. Archives `rollouts/wave2r.tar`, `wave3r.tar`. Wave 1c's failures follow on whichever A100 finishes first | queued |
| 11-16 22:20 pod | **Wave 2 complete**: 311 tasks, **78 resolved (25%)**, receipt `completed`, air gap held. Archive `runs/2026-11-16/rollouts/wave2.tar`, 44,349,440 B, md5 `cf301bea…`, verified by HEAD. The queued retry failed to start: the D4 dry run had left an untracked `scripts/trace_to_history.py` on this pod, so `git pull --ff-only` refused and the old orchestrator rejected `--skip-resolved-from` (the `&&` chain hid the failed pull). File removed, pulled to `3928395`, retry wave 2r restarted (233 unresolved tasks, v2 at temperature 0.6 / top_p 0.95) | running |
| 11-16 22:30 pod | **Wave 3 complete**: 193 tasks, **48 resolved (25%)**. Archive `runs/2026-11-16/rollouts/wave3.tar`, 29,655,040 B, md5 `5ed0b8e4…`, sha256 `d52367eb…`, verified by HEAD. Retry 3r started (145 unresolved). **First pass over all 620 qualified tasks: 155 resolved (25.0%)** — wave 1c 29/116, wave 2 78/311, wave 3 48/193 | done |
| 11-16 23:00 pod | **Retry 2r stopped** after 28 tasks with 0 resolved (retry 3r: 3/26, continues on A100 #2). Partial 2r archived: `rollouts/wave2r.tar`, 4,864,000 B, md5 `0f1d754c…`. GPU confirmed at 0 MiB; A100 #1 repurposed for the corpus and the first training run | done |
| 11-16 23:02 pod | **Training histories built** on A100 #1 (`trace_to_history.py` over rollouts 1c, 1, 2, 2r and wave 3 fetched from R2 by presigned GET, md5 checked): **152 written**, 2 duplicates, 3 refused (`system step after conversation start`: the harness inserted a system message mid-run; refused rather than re-labelled). Admission runbook for the new corpus being mapped (gates, schedule, worker config) before tokenization | in progress |
| 11-16 23:06 pod | Tokenization (`audit_replay_history_tokens.py`, pinned transformers 5.13.1 / tokenizers 0.22.2, qualified template `94899c0f…`): 140 of 152 tokenized, 12 refused as over the 32,768-token cap (no truncation). Alignment screen (`scripts/screen_task_alignment.py`, `f8d4374`; **automated, not a human review**: licence confirmed, train cohort, verifier-resolved, no test edits, edits a file the reference edits, size bound, within cap): **135 accepted**, 5 rejected (2 licence copyleft/indeterminate, 3 no file in common with the reference) | done |
| 11-16 23:11 pod | **Corpus `rebench-train-001` admitted**: 135 examples, 135 tasks, **71 repository groups**, 2,390,783 input / **854,534 supervised** tokens, all `train`; two-layer verification passed; freeze gate passed; credential screen 1 indicator (slack-sdk: an aiohttp deprecation message quoting `headers={'Authorization': aiohttp.encode_basic_auth(login, password)}`; no secret, reviewed false positive). Gates: rights (pool licence review + screen), split (freeze gate + cohorts), runtime (verification + qualification statement), task alignment (automated screen, labelled as such); reviewer recorded as the agent under the owner's delegated autonomy. Manifest `ae459ff4…`, content `4c344e57…`, schedule 29 updates (one epoch). Archive `runs/2026-11-16/corpus-rebench-train-001.tar`, 38,645,760 B, md5 `aefba3ff…`, verified | done |
| 11-16 23:12 pod | A100 #1 deleted (404 confirmed). The worker requires a non-overlay volume; US-MD-1 has no network volumes and no A100 (SXM or PCIe) was available in any volume-capable data center. **Training pod**: RTX PRO 6000 Blackwell 96 GB, `aftvcvodxh68j8`, US-CO-1, $2.69/h (total with A100 #2: $4.88/h), network volume `48v3bfyext` (80 GB) at /mnt/data (MooseFS). Run train-002: config lr 1e-4, seed 7401, 29 updates, 32,768-token sequences, 4.5 h cap, 12 GiB checkpoint budget; same qualified worker, then PEFT export and archive to `runs/2026-11-17/train-002.tar` | running |
| 11-16 23:40 | **Pre-registered rule for the adapter (written before any adapter result).** Evaluation: v2 and v2+adapter-002 (byte-identical except `agent.yaml` `adapter: main_lora` and `adapters/main_lora/`; `build_eval_candidates.py --base-dir`, `c4143fe`), concurrently against one server at concurrency 3 each, 8-minute cap, official harness, egress guard, on all 129 official development tasks (49 cohort + 80 holdout; the holdout is used with a recorded justification; none of these repositories is in the training corpus). Submit v2+adapter only if **(1)** adapter-only resolutions exceed base-only resolutions by **≥ 4** (net ≥ 3% of 129), **(2)** its out-of-budget-without-patch count is not higher than v2's by more than 3, and **(3)** no adapter run edits a test file that the base does not. Otherwise the adapter is not submitted and the next iteration (more data, or the E4B adapter) proceeds. The per-call LoRA tax (1.16× at concurrency 4, 1.30× at 1) is inside the measured outcome because both candidates run the same 8-minute cap | pre-registered |
| 11-16 23:35 pod | train-002 progress: 3 of 29 updates in ~11 min after a ~3-min load on the RTX PRO 6000 (≈ 3 min/update; ETA ≈ 00:55 UTC); 59–64 GiB in use of 96 GiB; runtime preflight passed (torch 2.10.0+cu128, capability 12.0) | running |
| 11-17 01:04 pod | **Retry 3r complete**: 145 unresolved wave-3 tasks at temperature 0.6, **10 resolved** (6.9%). Archive `rollouts/wave3r.tar`, 23,357,440 B, md5 `425d0405…`, verified by HEAD (with wave2r). **A100 #2 deleted** (`vplav4wbke2bo9`, 404 confirmed; ≈ 5.8 h × $2.19 ≈ $12.7). Retries of wave 1c skipped: second attempts resolve 2–7% at full GPU cost. Trajectories available for round 2: 152 (first pass) + 10 (3r) | done |
| 11-17 01:10 pod | **train-002 complete**: `schedule_complete`, 29/29 updates, 6,442 s, exit 0; peak 66.8 GiB of 95.0. Token-mean loss per update (each update on unseen examples): 0.134 → 0.068; **first-third mean 0.112, last-third 0.086**. The low starting loss is expected: the corpus is the base model's own resolved trajectories (rejection-sampled self-distillation), so the signal is a reweighting toward successful behaviour, not new knowledge. Adapter exported (`EXPORT_EXIT=0`). Archive `runs/2026-11-17/train-002.tar` (adapter, receipts, worker logs), 123,648,000 B, md5 `6bf816ea…`, verified by HEAD. Evaluation chain started (G3 → G4 → G5) | done |
| 11-17 01:11 pod | **Round-2 data started** in parallel: CPU pod `5qs9erdnha9ejy` (cpu3g 32 vCPU, $1.28/h; total $3.97/h) converts and qualifies the **development cohort** (445 tasks / 112 repositories; asserted disjoint from the confirmation cohort) with the same pipeline (`--cohort development`, `1006af2`), shipping to `runs/2026-11-17/rebench-packs-dev/` | running |
| 11-17 01:22 pod | **G3 passed** (`verify_training_round.py`): session complete 29/29, final checkpoint and export identities, loss 0.112 → 0.086, peak memory under the device total, adapter r=4 / alpha=8, 410 A + 410 B, all finite, **0 zero-B**. Evaluation attempt 1 had aborted earlier on a tar ownership error extracting v2 onto the MooseFS volume (fixed: `--no-same-owner`, local disk); no GPU time spent | done |
| 11-17 01:28 pod | **G4 (qualify_lora_serving) reported 'outputs identical'** for its two prompts (a two-sentence definition and a one-step `read_file` call): greedy text and tool call were byte-identical for base and adapter. Diagnosis by `scripts/probe_lora_effect.py` (`db0dfa1`), same server, token logprobs on agent prompts (system + user of 4 training histories) and one plain prompt: **adapter applied and effective** — divergence at token 7–9 on 3 of 4 agent prompts, max |Δ logprob| 0.32–0.93, mean 0.04–0.24; plain prompt diverges at token 5 (max Δ 0.0002, a near-tie). vLLM maps `model.language_model.*` adapter keys onto `language_model.model.*` (gemma4_mm `hf_to_vllm_mapper`); only vision-tower targets are ignored (expected; the adapter has none). **G4 redefined**: logprob probe verdict applied (weak or effective) + adapter tool calls parse (they do); `qualify_lora_serving.py` now records logprobs. G4 passed under the corrected definition; this also resolves the C1 caveat (identical latency figures did not mean adapters were unapplied) | done |
| 11-17 01:41 pod | **G5 started**: v2 vs v2+adapter-002, 129 official development tasks, concurrency 3 each, 8-min cap, pre-registered rule (11-16 23:40) | running |
| 11-15 19:58 | E4B v1 package: the e4b_base files (agent.yaml `fb0ab7b3…` declares `gemma-4-e4b-it-qat-w4a16-ct`, nine tools; sampling `5cbfd223…`; eval_config `404b197b…` 8 min / 40 / 40 / 120 s; system.md `1c4137aa…`, the base instruction). `validate_directory` passed on the pod with the official limits; no adapters. Notebook built, zip sha256 `65a7f72e…`, 1,974 B. Choice: every E4B variant tied within noise, so the simplest one (base) is used; it scored 7/49 in both screens with 0 out-of-budget runs | built |
| 11-15 19:55 | **Pod `rho6c1imvim7mj` deleted**, confirmed (404). Session ≈ 1.35 h × $2.19 ≈ $3.0 | done |
| 11-15 19:53 | e4b-screen-2 archived: `artifacts/v1/runs/2026-11-15/e4b-screen-2.tar`, sha256 `f378e2c9…`, 27,617,280 B, verified | done |
| 11-15 19:51 pod | **e4b-screen-2 complete**: e4b_base **7** (the same 7 as screen 1; replicate is exact at temperature 0), e4b_verify_think8k 7 (+0/−0), e4b_workflow 7 (+0/−0), e4b_think8k 6 (+2/−3), e4b_verify 5 (+0/−2). base, workflow and verify_think8k resolve the identical set. Median calls per run stay ~10 in every variant: **E4B largely ignores process instructions and a longer thinking budget**. Its result is bounded by capability, not by the agent design. Integrity: data verified, candidates unchanged, air gap held, guard removed. The two "error" rows are agent outcomes (turn budget; no submit_patch call), not infrastructure | done |
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

### 11-17 02:00 UTC — submissions and G5 progress
- E4B v1 public score: **0.06** (vs 31B v1 0.17). E4B track dropped as a submission candidate.
- 11-17 slot → **31B v2** (callplan_nograph) submitted 01:57 UTC, zip sha256 `49282ef9…` (matches recorded v2 digest; member digests agent.yaml 4f48dc18, sampling 5cbfd223, eval_config 404b197b, system.md 1fb83636). PENDING.
- G5 (v2 vs v2+adapter-002, 129 official dev tasks, concurrency 3): started ~01:42; at 01:59 7/129 each (v2 0, v2lora 1); ~1 task/min → ETA ~06:00. Decision rule unchanged (pre-registered 11-16 23:40).
- Round-2 dev pipeline: 38 repos processed, 15 packs shipped, 47 qualified tasks.

### 11-17 02:55 UTC — dev cohort packs verified; round-2 rollouts started
- D1/D2 (development cohort) complete: 112 repos → **58 packs, 135 qualified tasks**, 22,765,935,428 B. All 58 verified in R2 by HEAD (size + md5 ETag), 0 mismatches. Pod logs `runs/2026-11-17/rebench-packs-dev/pod-logs.tar` md5 d9daf505, verified by GET. CPU pod deleted.
- D3 round 2 (rollouts-dev1): A100 SXM pod `3ueoyvhxguqcpi` ($2.19/h; total $4.88/h with the G5 pod), v2 at 20-min cap (v2r) over the 135 tasks, egress guard, archive → `runs/2026-11-17/rollouts-dev1.tar`. Started with v2 rather than waiting for G5 (≈3 h saved); the G5 decision still governs whether the next round's sampler and submission use the adapter.
- Session interruption at ~02:45 (local Claude process restart only): pods unaffected; Kaggle poll re-armed.

### 11-17 05:20 UTC — round-2 rollouts complete; D4 round 2 running
- rollouts-dev1: **135 development-cohort tasks, 42 resolved (31.1%)**, 0 harness errors, guard held, rc=0. Archive `runs/2026-11-17/rollouts-dev1.tar` 19,752,960 B md5 `71090099…` (sha256 146a1165…), verified by HEAD.
- Pre-flight of the D4 script against R2 (stream-read, nothing stored locally): all six round-1 archives unpack to `rollouts-*/<pack>/results/`; all 135 corpus-001 tasks are present among 165 resolved round-1 trajectories.
- Launcher defect caught before it fired: the env file held presigned URLs unquoted (`&` split them); rewritten quoted, lengths checked (394/397), relaunched. No work lost.
- D4 round 2 (same pod): 204 histories written (3 refused: system step after start; 2 duplicates). Tokenization: 12 examples over the 32,768-token cap are refused (no truncation) and drop out of the screen.
- Screen now admits train + development cohorts (`fd05f48`, `--allowed-cohort`; confirmation is refused at argument parsing). Development-cohort licences: 441/445 confirmed.
