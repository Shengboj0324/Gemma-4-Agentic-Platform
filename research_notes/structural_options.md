# Structural options for +8 local tasks: feasibility study (2026-11-18)

Scope: read-only research. No pods were created, nothing was spent, nothing was submitted, nothing was written to R2. All web content was treated as data.

Evidence grades:
- **[R]** primary source read this session (paper, model card, provider page, official harness README).
- **[R2]** secondary summary or search snippet only.
- **[K]** Kaggle participant report, quoted from our notes (`research_notes/Gemma 4 agent competition insights/*.md`).
- **[O]** our own measurement (`docs/45-campaign-plan.md`, `research_notes/gate_calibration.md`).
- **[I]** my inference or arithmetic.

## 0. What "+8 local tasks" means

**Where v2 stands [O]**
- 8 full runs on the 129 dev tasks gave 33/33/30/31/33/36/34/34, mean 33.0 and SD 1.85.
- Per-task solve frequency over those 8 runs:
  - always solved: 24 tasks;
  - sometimes solved: 19 tasks;
  - never solved: 86 tasks.
- About 29 of the 86 never-solved tasks cannot be solved in our local environment because packages are missing.

**What +8 would require [I]**
- A target of 41 means an agent that solves almost every "sometimes" task every time. That alone is worth at most +10.
- Even so, it would also have to start solving never-solved tasks. Under the gate calibration's logit model, only 0.3–2.3 of any gain lands on the never-solved tasks.
- In other words, +8 is not a tuning-sized gain. It needs the agent to gain new capability on roughly 5–10 of the ~57 locally solvable never-solved tasks.

**Detectability [O]**
- Under the no-effect null, P(net ≥ 4) is about 0.10 and P(net ≥ 6) is about 0.02.
- A true +8 would therefore be obvious in one paired run.
- A true +2 to +3, the range everything we have tried so far points to, would not be.

**Hard constraints that bound every option**

| Constraint | Value | Source |
|---|---|---|
| 12 h fail-all limit on the scorer | v2 projects to 10.4 h for 120 tasks (311 s/task sequential on 4×L4), a 13% margin | [O] T1 timing run |
| Last safe submission | about Dec 1, because queues take 13–24 h and only one submission may be pending | [K] update_2026-11-18 §3 |
| Possible cutoff for new notebook versions | Nov 25 (unconfirmed by hosts) | [K] |
| Usable calendar time | about 7 days if the Nov 25 cutoff is real, 12–13 days if not | [I] |
| Bundle | declarative YAML only; no callbacks (ignored); compaction config is fixed by the harness App (`token_threshold` 14,336, `event_retention_size` 5); tool output caps fixed (5,000 chars; 150 lines / 10,000 chars per read) | [R] HARNESS_README §2.3, §7.1–7.2 |

## A. Teacher-distillation LoRA

### A1. Teacher candidates: licence, price, and strength in *our* harness

**Licences and prices**

| Teacher | Licence / ToS on training other models | Price per 1M tokens (in / out) | Grade |
|---|---|---|---|
| DeepSeek V4-Pro (API) | API ToS §4.2(3) lists "training other models (such as model distillation)" as a permitted use of inputs and outputs (released 2026-04-22, effective 2026-04-29) | cache-hit $0.022 / miss $0.66 / out $1.98 off-peak; double at peak (01–04 and 06–10 UTC, Mon–Fri) | [R] |
| DeepSeek V4.1-Flash (API) | same ToS | hit $0.003 / miss $0.15 / out $0.60 off-peak | [R] |
| Qwen3.6-27B (open weights; self-host) | Apache-2.0 on the HF card | self-host cost only | [R] |
| GLM-4.7 (355B MoE) | MIT | about $0.60 / $2.20 | [R2] aggregator pages |
| Kimi K2.x | "modified MIT": attribution is required only above 100M MAU or $20M monthly revenue; K3 has stricter terms | — | [R2] |
| gpt-oss-120b | Apache-2.0 plus a usage policy | — | [R2] |
| Claude / GPT / Gemini APIs | ToS forbid using outputs to build competing models | — | excluded |

- DeepSeek's open-weight licence reportedly contains an anti-distillation clause [R2, unverified]. Use the API, which grants the right explicitly, rather than self-hosting DeepSeek weights.
- Qwen3.6-27B's own card reports 77.2 on SWE-bench Verified, against **Gemma4-31B at 52.0** in the same table. Both were run on Qwen's internal scaffold at 200K context.
- Kimi and gpt-oss were not checked in our harness. They are listed only for licence completeness.

**Strength inside our harness (the number that matters)**
- One participant ran the competition harness on the dev tasks [K, Ruijie Zhu, T747168]:

| Model | Solved |
|---|---|
| Gemma 31B QAT | 54/124 |
| DeepSeek V4-Pro | 58/124 |
| Qwen3.6-27B | 59/123 |

- The union of all runs was 73/123, and 48 tasks were solved by nobody.
- So **the best licence-clean teachers beat Gemma by only +4 to +5 tasks** in this harness and budget.
- The 25-point Verified gap collapses because the limit here is the harness (8 min, 40 calls, 32k context with compaction, offline environment), not knowledge.
- [I] A student fine-tuned on a teacher's trajectories almost never exceeds that teacher. The plausible ceiling for distillation is therefore about **+3 to +5** on our gate, not +8.

### A2. Can a teacher drive our exact harness, and be converted to Gemma format?

**Driving the harness: yes.**
- Other teams have done it [K]:
  - Ruijie Zhu ran DeepSeek V4-Pro and Qwen3.6-27B in the harness.
  - Munal Singh collected about 2,000 DeepSeek runs.
- The local harness is ours to patch. We would point the ADK/LiteLLM model at an OpenAI-compatible endpoint, keep the same six tools, budgets and initial prompt, and the trace then records requests and responses.
- One restriction applies: `validate_single_declared_model` only accepts registry aliases, so this works locally only, never in a bundle [R].

**Converting to Gemma format: mechanically yes, behaviourally risky.**
- Our D4 pipeline already renders histories into the exact Gemma 4 chat template [O].
- Teacher tool calls (OpenAI JSON) map onto `<|tool_call>` blocks.
- Teacher reasoning (`reasoning_content`, or Qwen `<think>`) has to be placed in the Gemma thought channel. This is exactly where distillation has failed in this competition:
  - mobassir [K]: a QLoRA on Open-SWE-Traces re-simulated into the harness cut teacher NLL threefold, but the agent collapsed from 37/60 to 4–11. It copied short thoughts (about 130 characters against 829) and looped.
  - Nir Aberman [K]: targets without thoughts produced zero reasoning in all 109 calls.
  - Our round 4 [O]: thinking content out of the loss led to thinking collapse.
- A teacher with long, differently styled reasoning (DeepSeek) would push thought length the other way, which means more time per task.

### A3. How many solved trajectories we could get

**Task sources we already have [O]**
- 620 qualified train-cohort tasks plus 135 development-cohort tasks from SWE-rebench-V2. They are repository-disjoint from the four dev repositories, licences were screened, and gold and empty patches were verified.
- Gemma's first-pass yield on them was **25%** (155/620); a retry at temperature 0.6 added 6.9%.

**Expected teacher yield [I]**
- In-harness teachers are about 1.07× Gemma, so expect about 27–32% first pass on the same tasks.
- Three attempts per task at about 40% unique coverage gives about 300 tasks and **≈ 500–800 resolved trajectories**.
- Only the teacher-only solves carry capability Gemma lacks. From T747168 that is roughly 10–15 of 124 tasks, so only **≈ 10% of the corpus**.

**Reaching 2,000–5,000 trajectories**
- That needs about 3–6× more qualified tasks:
  - SWE-rebench (21,336 Python tasks, CC-BY-4.0; per-repo licences apply);
  - SWE-rebench-V2 Python (7,243);
  - SWE-smith-py (MIT);
  - SWE-Gym (MIT);
  - R2E-Gym (Apache-2.0).
- Our conversion pipeline qualified 33% of tasks at about 12 CPU-pod-hours (≈ $11) per 278 repositories. 1,500–2,000 more qualified tasks would therefore take about 2–3 days and about 250 GB of packs in `gemma4agenticdata` [O, I].
- Ready-made public trajectories are not in our tool schema. Re-simulating them is mobassir's failed route:
  - nebius/SWE-rebench-openhands-trajectories: 67,074 rows, CC-BY-4.0;
  - nvidia/SWE-Hero: 34,269 rows; Qwen3-Coder-480B teacher; 4-tool OpenHands schema;
  - nvidia/Open-SWE-Traces: 1.14M rows.
  - Source: `research_notes/SWE agent SFT data sources/` [O].

**Cost [I]**
- Per-run token usage, from v2 traces: about 30 steps, a mean prompt of about 9k tokens, mostly prefix-cached, and about 265 completion tokens per step. That is about 270k input and 8k output. Teachers emit more reasoning, so assume 15k output.
- DeepSeek V4-Pro at peak: about **$0.11 per run**; off-peak about $0.055. With a 2× allowance for verbosity, call it about $0.05–0.20.
  - 3,000 runs cost about **$150–600**, or about $75–300 if run off-peak.
- Self-hosted Qwen3.6-27B (BF16 on one RTX PRO 6000 or A100 at $2.2–2.7/h, under the $5/h cap):
  - about 30–48 tasks/h, scaled from Gemma's 48 tasks/h at 12 agents on an A100;
  - 3,000 runs ≈ 60–100 GPU-h ≈ **$150–270**.
- Training plus evaluation: about $30–50.

### A4. Published evidence that 500–5,000 teacher trajectories help a ~30B student

| Study | Student, base score | Trajectories | Result | Grade |
|---|---|---|---|---|
| SWE-smith | Qwen2.5-Coder-32B, about 7% | 500 / 5,016 (Claude 3.7) | 28.2% / 40.2% Verified | [R] |
| SWE-Gym | Qwen2.5-Coder-32B | 491 | 20.6% | [R2] |
| Skywork-SWE | Qwen2.5-Coder-32B, 6.4% | 8,209 | 38.0%, log-linear, no saturation | [R2] [arXiv 2506.19290](https://arxiv.org/pdf/2506.19290) |
| SWE-Lego | Qwen3-32B, 23.2% | dataset contribution +25.6 | 52.6% (full-parameter SFT, not LoRA) | [R2] [arXiv 2601.01426](https://arxiv.org/pdf/2601.01426) |
| CoderForge | Qwen3-32B | Qwen3-Coder-480B teacher | 59.4% | [R2] |

**Why this does not transfer to our case [I]**
- Every large gain starts from a base at 6–23% Verified.
- **Gemma 4 31B already sits at about 52%** (Qwen's table). That is the level SWE-Lego reached only *after* SFT on a large curated corpus.
- I found no published result of a ~50%-Verified 30B student gaining from 500–5,000 teacher trajectories, and no LoRA-vs-full comparison at 30B for SWE.
- A 7B LoRA study never reached perfect tool-call format [R2, arXiv 2607.17205].

**In-competition evidence**
- Munal Singh: an r16 adapter trained on about 2,000 DeepSeek runs scored 37 vs 38 held-out and 0.12 vs 0.15–0.17 on the LB [K].
- Luca Massaron: r16 and r4 adapters scored 0.00 on the LB despite 17 vs 12 locally [K].
- No participant has shown a LoRA gain on the scorer [K].
- Our own three self-distilled adapters each came out at net −3 to +3 [O].

### A5. Time overhead against the 13% margin

**Measured costs**
- Adapters cost +15–29% time per task [K] and about 24% of the KV cache (36.4k → 27.7k tokens) [K].
- Our measurements [O]:
  - adapter-003: 1.20× time;
  - adapter-003 at thinking budget 1024: 1.18× time and **−3 tasks** (round 7);
  - adapter-005: 0.82× time, but only because thoughts got shorter, and resolves stayed flat.

**Why the overhead can't be removed**
- The bundle ships PEFT adapters on a fixed registry model. Merging the adapter into the weights is not possible inside the declarative bundle and the 3 GiB limit [R, HARNESS_README §3].

**Mitigations and what they cost**
- Thinking budget 1024 lost resolves in round 7.
- Lower rank or attention-only targets reduce the kernel tax only modestly (untested on L4).
- A 7-minute cap.
- Each mitigation spends part of the gain it is protecting.

**Margin arithmetic [I]**
- Any adapter that is not at least as fast as v2 in behaviour needs an equivalent time cut.
- 1.10× is the pre-registered limit. 1.15× projects to 12.0 h, a coin flip on fail-all.

### A6. Verdict on A

| Item | Assessment |
|---|---|
| Expected gain | **0 to +4** (range −10 to +5, including collapse modes); evidence quality moderate and mostly negative |
| Time-to-test | **8–10 days**: task expansion 2–3 d, teacher rollouts 2–3 d, conversion and training 1 d, paired eval 1 d, 4×L4 timing run 0.5 d. This misses a Nov 25 notebook cutoff, and even without one it leaves no room for a second iteration |
| Cost | $250–700 for 1,000–3,000 runs plus training. The low end fits $300 only at about 1,000 runs |
| 12 h risk | **High** |

**Minimal first experiment: a 1-day go/no-go for about $15–40**
- Run the teacher once on the 129 dev tasks in our harness at v2's budgets: 8 min wall clock for Qwen3.6-27B self-hosted, or 40 calls / 40 turns for the API.
- Kill A unless teacher − v2 ≥ +12 on our gate. A student will not exceed its teacher, and T747168 predicts about +4.

## B. Agent-design changes inside the allowed schema

### B1. What the schema allows [R, HARNESS_README §2.3, §3.4, §5.3]

**Agent types and fields**
- `LlmAgent` supports `sub_agents` (transfer), `agent_tool: {config_path, skip_summarization}`, `output_key`, `include_contents: none`, a per-agent `adapter`, and a per-agent `generate_content_config`.
- `SequentialAgent`, `LoopAgent` and `ParallelAgent` are also available.

**Budgets are per task and shared**
- 40 calls, 40 turns and 8 min apply across all agents.
- Callbacks are ignored.

**Two control-flow hazards to verify before any eval**
1. The harness "immediately breaks out of the agent loop" when *any* event `is_final_response()`, or when a turn ends after `submit_patch`. In a `SequentialAgent`, a localizer that ends with a text summary may therefore end the whole task before the editor runs.
   - Partial counter-evidence: a SequentialAgent setup step executed 47/48 times [K, T747923]. Its terminal event type is unknown.
2. When a turn ends without a submit, the harness sends a nudge and calls `run_async` again. A `SequentialAgent` would then restart from its first sub-agent.
- `AgentTool` avoids both hazards:
  - the root coder keeps control;
  - the sub-agent runs in a fresh context and returns its final text as a tool result;
  - no braces are needed in prompts, because the query is passed as the tool argument.

**ParallelAgent**
- Tool calls still execute sequentially, and there is a known ParallelAgent+tools bug in ADK 1.36 that will not be fixed [K, HOST T748287].

### B2. Evidence that phase-separated agents beat a single agent at ~30B under tight budgets

**Literature (none of it matches our setting)**
- SWE-Effi [R]: Qwen3-32B, 50 issues, single runs.

  | Scaffold | Resolve % |
  |---|---|
  | AutoCodeRover (2-stage: retrieve, then patch) | 38 |
  | OpenHands | 34 |
  | SWE-agent | 28 |
  | Agentless (83 calls, about 15 min) | 48 |

  - Different tools and budgets, and a ±7 pp 95% CI at n = 50.
- Multi-agent SWE papers report gains with frontier models at higher cost [R2]:
  - AgentForge: +26 pp on Lite, against a weak single-agent baseline;
  - PhoenixRepair: 76% Verified with MiniMax-M2.5 at **1.85× cost per task**;
  - SWE-Debate: the debate component is worth +4.2 pp.
- None of these isolates "phase split vs single agent" at 30B under a wall-clock cap.

**Context isolation**
- JetBrains' comparison of observation masking vs LLM summarization [R2, via secondary summary] found masking matched or beat summarization (+2.6 pp, 52% cheaper).
- Amp replaced compaction with a fresh-context "handoff" [R2].
- In our harness, compaction keeps text only and drops tool results [K, T754783]. About 80% of runs are reportedly compacted, and solve odds "halve" after a compaction [K, correlational and confounded by task difficulty]. A fresh-context sub-agent is the only bundle-level way to sidestep this.

**In this competition [K]**
- An analyzer sub-agent gave +1 (noise) on 129 tasks (Ayush Thakur).
- Two teams found "subagents and skills unhelpful" (T750496, Adam Johnson).
- spiritofvishwakarma's `agent_tool` "code_analyzer" with a rank-32 LoRA claims a best of 0.18 (single draws).
- No 0.24+ team has disclosed a multi-agent setup.

**Behaviour evidence against forced phases [K]**
- "Edit by call N" moved the first edit 149 s → 91 s with unchanged solves (Nir Aberman).
- Forced edits raised solves only 26 → 30/112 (kimdonggyu) because forced edits become wrong edits.
- Our v3 (round 8) cut edit calls but tripled budget exhaustion (25 vs 8) [O].
- Agents already find the gold file by call 2 in 63% of runs [K, Ilya Gordey]. Separating localization from editing attacks a phase that is not the bottleneck.
- The bottleneck is the *wrong fix within 20 lines of gold* (18 of 41 failures [K, Munal Singh]; 56% wrong-fix share in ours [O]).

### B3. Variants and verdicts

| Variant | Mechanism | Expected gain | Time risk |
|---|---|---|---|
| B-i. Root coder plus `agent_tool` "investigator" (read-only tools, fresh context, ≤ 200-word report: file:function, root cause, repro command) called once at start | Fresh-context localization; keeps the root context shorter, so fewer compactions | **0 to +3** (weak) | +5–15% (re-reads, extra turns; prefill spikes already 24% of runtime [K]) |
| B-ii. Root coder plus `agent_tool` "reviewer" after the first edit (reads the diff and issue, runs the nearest test, returns PASS/concerns) | Targets the wrong-fix share | **0 to +3** (execution-free critics saturate [R2]; SWE-Debate +4 pp with frontier models) | +10–20%; needs a cap or call trade-off |
| B-iii. SequentialAgent planner → coder (`output_key`) | Reliable forced plan step | **−2 to +2**; forced-phase evidence is null | control-flow hazard above |
| B-iv. Per-phase LoRAs | — | no data; inherits all of A's problems | high |

**Verdict on B**
- Nothing in the literature or the competition supports +8.
- B-i and B-ii are the only structural changes with a plausible mechanism, a small cost and a short test.

| Item | Assessment |
|---|---|
| Time-to-test | 2–3 days each |
| Cost | ≈ $30–60 per paired 129-task run |

**Minimal first experiment for B-i**
1. Read the `agent_runner.py` loop on a pod and run a 3-task smoke test to confirm that the AgentTool's events neither end the task nor double-count turns.
2. Run a 12-task behaviour gate.
3. Run the 129-task paired run under the pre-registered rule: net ≥ 4, time ≤ 1.10×, budget exhaustion ≤ v2 + 3.

## C. Everything else

**C1. Test-time selection / best-of-n: infeasible (confirmed).**
- Gains need 16–32 rollouts for +4 to +6 pp at 32B [R2: SWE-Lego TTS@16 +6.2; SWE-HERO +4.5 at 32].
- Our margin is 13% of one rollout.
- ParallelAgent branches share one `/workspace` container. `edit_file` refuses paths outside `/workspace`, so isolated candidate edits are impossible except through shell gymnastics.
- Tool calls run sequentially [K, HOST], and there is no patch-selection hook (no callbacks, no Python).

**C2. Context management: bundle levers only.**
- Compaction settings and tool-output caps are fixed by the harness [R].
- What the bundle controls:
  - `max_output_tokens` (8192 in v2; already the safe value [K]);
  - thinking budget (round 12 is testing 1024);
  - prompt rules for windowed reads and `grep -n`/`head` piping.
- `include_thoughts: false` hurt in two reports [K]:
  - 31B: about 35 vs 51 solves;
  - E4B: tool-argument JSON errors rose from 3 to 132.
- Expected gain: **0 to +2**.
- Zero-GPU first step: from the eight archived v2 runs on R2 (read-only), measure, per task:
  - compaction count;
  - context-overflow rate;
  - solve rate with vs without compaction, *within the 19 "sometimes" tasks* (to control for difficulty).
- If compaction does not separate wins from losses within those tasks, drop B-i and C2.

**C3. Tool-output truncation**
- Fixed at 5,000 characters and 150 lines [R]. The only lever is prompt guidance.
- The edit_file argument-order slip was fixed by others with no solve gain [K].
- Expected gain: about 0.

**C4. Variance itself**
- Two final picks of the best-mean configuration are worth about +0.9 expected tasks [K/I].
- This is the cheapest "gain" available and costs nothing to build.

## D. Ranking

| Rank | Option | P(≥ +8 local) | Expected net | Evidence quality | Days | Cost | 12 h risk |
|---|---|---|---|---|---|---|---|
| 1 | C2 trace analysis (compaction/overflow vs solve) | n/a (diagnostic) | decides B-i | own data | 0.5 | $0 (CPU, read-only R2) | none |
| 2 | B-i AgentTool investigator (fresh context) | < 3% | 0 to +3 | weak / analogical | 2–3 | $30–60 | medium |
| 3 | B-ii AgentTool reviewer after edit | < 3% | 0 to +3 | weak | 2–3 | $30–60 | medium-high |
| 4 | A teacher-distilled LoRA | < 5% | 0 to +4 (tail −10) | moderate, mostly negative in-competition | 8–10 | $250–700 | high |
| 5 | B-iii SequentialAgent / B-iv per-phase LoRA | ≈ 0 | −2 to +2 | negative | 3+ | $60+ | medium-high |
| — | C1 best-of-n / test-time selection | 0 | — | — | infeasible | — | fatal |

**Plain conclusion.** No structural option has credible evidence of reaching +8 local tasks within about 10 days and about $300.
- The strongest single fact: licence-clean teachers beat Gemma 31B by only +4 to +5 tasks in this exact harness. That caps distillation.
- Every in-competition distillation attempt was null or negative.
- Phase-split agents have no 30B, wall-clock-capped evidence, and the bottleneck they target (localization) is already solved by call 2.

## Sources

- DeepSeek pricing: https://api-docs.deepseek.com/quick_start/pricing
- DeepSeek Open Platform ToS §4.2(3): https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html
- Qwen3.6-27B card (Apache-2.0; Verified 77.2 vs Gemma4-31B 52.0): https://huggingface.co/Qwen/Qwen3.6-27B
- GLM-4.7 licence and pricing (aggregators): https://llm-stats.com/blog/research/glm-4.7-launch
- Kimi K2 licence: https://huggingface.co/moonshotai/Kimi-K2-Instruct-0905/blob/main/LICENSE ; https://simonwillison.net/2026/Jul/27/kimi-k3/
- Skywork-SWE: https://arxiv.org/pdf/2506.19290
- SWE-Lego: https://arxiv.org/pdf/2601.01426
- SWE-Zero/SWE-Hero: https://arxiv.org/html/2604.01496v1
- LoRA trajectory curation (7B): https://arxiv.org/abs/2607.17205
- AgentForge: https://arxiv.org/pdf/2604.13120
- PhoenixRepair: https://www.alphaxiv.org/abs/2607.18859
- SWE-Debate: https://arxiv.org/pdf/2507.23348
- Context-management summaries (JetBrains masking result, Amp handoff): https://zylos.ai/research/2026-05-05-ai-agent-context-window-management-compaction-continuity-cost ; https://dev.to/rawveg/when-coding-agents-forget-44g0
- SWE-smith, SWE-Gym, SWE-Effi, SWE-agent: cited in `research_notes/Gemma 4 agent competition insights/swe_agent_techniques.md`
- Kaggle threads T747168, T751596, T755677, T759329, T747923, T748287, T754783, T749198: cited in `kaggle_discussions_and_rules.md` and `update_2026-11-18.md`
- Harness: local copy of the official HARNESS_README.md (§2.3, §3, §5.3, §7)
- Ours: `docs/45-campaign-plan.md`, `research_notes/gate_calibration.md`
