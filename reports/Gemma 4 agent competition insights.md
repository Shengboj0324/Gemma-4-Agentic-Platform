# Close the scorer gaps before chasing draws

ZenithSync24 is not missing a public recipe. Every public Gemma 4 bundle whose repeat scores have been traced averages about **9–10 of 58** public tasks. Identical bytes swing by ±3 tasks from one draw to the next, and our 0.17 (10/58) and 0.15 (9/58) sit exactly on that mean. The configurations that produced the 0.22–0.24 claims are the same single-agent, prompt-only setup we already run, and they do not reproduce. One result breaks the pattern: the leader's **0.29 (17/58)** is too high to be a lucky draw from a 10-task configuration, so a real but undisclosed edge of about +3–4 tasks exists somewhere. The likeliest kickers we are missing are not prompt tricks. They are gaps between our local paired gate and the hidden scorer:

- **Hardware.** The gate runs on a single large GPU at concurrency 3. The scorer runs 4×L4 sequentially, against a 12-hour all-or-nothing limit.
- **Verification timeout.** In the harness source, our 120 s `timeout_seconds` also bounds the hidden-test pytest run.
- **Environment.** **29 of our 129 dev tasks** cannot be scored locally, because two test packages are missing here that the hidden environment evidently has.
- **Compaction.** Our prompt does not pin the issue text, and compaction is reported to halve solve odds.

External SWE-agent research agrees with our traces that wrong fixes and late, untested edits drive failure. Yet the competition-specific attempts to fix these with forced early edits, verification prompts or LoRA have all come back flat. The recommended order is:

1. Recalibrate the gate: scorer-like hardware and timing, and the env-blocked tasks restored.
2. Stack zero-cost hygiene changes into one v3 candidate large enough to clear the +4 threshold.
3. Then test a targeted behaviour check.

Expect round 7 (adapter-003 at thinking 1024) to fail the gate on resolutions or on time. With about 15 days left, one pending submission at a time and roughly one day to score each, use leaderboard submissions to confirm a bundle finishes inside 12 hours, not to rank configurations.

## One task in 58 separates most of the field, and luck sets the order

The 2026-11-17 board has **5,990 teams**: 1 at 0.29 (17/58), 14 at 0.24 (14/58), 110 at 0.22, 538 at 0.20, 1,146 at 0.18, 1,080 at 0.17 and 851 at 0.15. Scores are truncated multiples of 1/58 ([dariushafshar board](https://www.kaggle.com/code/dariushafshar/gemma-4-lb-58-tasks-bronze-is-a-124-team-tie); [T743506](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743506)). The same notebook author puts bronze at about 0.20, which is a 124-team tie. Our 10/58 is two tasks below bronze and seven below the leader.

How much of that ordering is skill is the central question, and the noise evidence is overwhelming:

- One sha256-identical ZIP scored 0.18 and then **0.01** ([T750521](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750521)).
- A byte-identical bundle went 0.17 → 0.12 ([T758969](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758969)).
- Identical files ranged from 7/58 to 13/58 ([T751596](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751596)).
- Temperature 0 is not deterministic under continuous batching, so our setting buys no reproducibility ([T760014](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/760014)).

A census of repeated public draws puts the pooled per-draw SD at **1.56 tasks**, and estimates that about 40 draws per arm are needed to detect a one-task difference ([census](https://www.kaggle.com/code/dariushafshar/gemma-4-most-run-public-config-averages-10-58)). The public "0.22" recipes have these means:

- Budget-Fit V5: **10.0/58** over 10 draws (95% CI 8.98–11.02).
- Budget-Aware V10: **8.71/58**. It first drew 13, then 7–10.

Both are statistically indistinguishable from our 10 and 9.

The 0.24 block is mostly what a max over many draws looks like. Its 14 teams have a median of **28.5 submissions** ([board](https://www.kaggle.com/code/dariushafshar/gemma-4-lb-58-tasks-bronze-is-a-124-team-tie)). The expected maximum of about 28 normal draws sits roughly 2.1 SD above the mean, so a 14/58 best is consistent with an underlying mean near 10.5–11. That is the public recipe.

The leader is different. Yurnero reached 17/58 within 18 submissions. For a 10-task configuration that is about 4.5 SD above the mean, essentially impossible over 18 draws. A configuration that averages 13 would reach it about 9% of the time over 18 draws, and one that averages 14 about 40% of the time. My reading is that the leader's true mean is **at least about 13/58 (0.22)**, a genuine 3–4 task edge. A few 0.24 teams with only 2, 5 or 8 submissions may hold smaller real edges too. None of them has published anything. Yurnero says only that variance is "the real problem", that he expects a "huge" shakeup, and that LoRA can score above zero ([T757626](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/757626); [T755677](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755677)). Radek's 0.24 team disclosed a replay-and-fork harness for prompt search, not a configuration ([T758817](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758817)).

The private board inherits the noise. Every submission runs public and private tasks (about 58 + 60) in one evaluation ([HOST T746008](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746008)), so each past submission already holds one private draw. Hosts have not answered whether final scoring averages several runs, and Yurnero notes Kaggle "has never done" that ([T754295](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/754295)).

Under the usual Kaggle convention, a team's private score is the better of its two selected submissions ([Rules §2.2](https://www.kaggle.com/competitions/gemma-4-developer-agent/rules)). Selecting on a noisy public score buys almost nothing on private. The lever that does matter is putting two submissions of the highest-mean configuration into the final pair, because that is a maximum of two independent private draws: about **+0.56 SD**, or roughly +0.9 task, over one. This is my inference from the convention, not a host statement.

## Public notebooks and hosts confirm we already run the consensus recipe

A read of 40 public notebooks found two scored 31B families: Budget-Fit V5 and Budget-Aware V10 (the SuperAgent lineage). Both use one agent with:

- temperature 0.2, top_p 0.95, max_output 8192, thinking 4096;
- 8 min / 28 calls / 80 turns / 240 s;
- nine declared tools, with the three graph tools forbidden in the prompt.

Later variants change one knob at a time ([Budget-Fit](https://www.kaggle.com/code/verracodeguacas/gemma-4-agent-budget-fit-single-agent); [V10](https://www.kaggle.com/code/flexonafft/gemma-4-budget-aware-coding-agent-v2)). No public bundle uses best-of-n, multiple attempts, patch voting or callbacks. The submission format is declarative YAML with no Python entrypoints ([Data page / HARNESS_README](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)). Hosts confirmed that ParallelAgent still executes tool calls sequentially, and that there will be no ADK v2 ([HOST T748287](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748287)). Test-time scaling is therefore off the table for everyone.

Our v2 already matches the elements the 0.22-era bundles share: no graph tools, an edit-by-call-12 deadline, a never-submit-empty rule and stated budgets ([campaign plan, 11-16 diff](/Users/jiangshengbo/Gemma-4-Agentic-Platform/docs/45-campaign-plan.md)). The remaining differences are small and testable:

| Setting | ZenithSync24 v2 | Public consensus | What the evidence says |
|---|---|---|---|
| temperature / top_p | **0.0 / 1.0** | 0.2 / 0.95 | Local single runs: 0.0 → 47, 0.2 → 48, 0.4 → 51 of 129 ([T746250](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746250)) |
| thinking_budget | **2048** (round 7: 1024) | 4096 | 2048 → 50 vs 4096 → 48; thinking off → 23 ([T746250](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746250)); 1024 flat at 48/150 with ±9 flips ([moranzavdi](https://www.kaggle.com/code/moranzavdi/gemma4-agent-lessons-for-competitors)) |
| max_turns | **40** | 80 | Our v2b60 turned turn endings into 8-minute timeouts with no gain |
| timeout_seconds | **120** | 240 (Patchsmith / Repair Lab: 60) | Also bounds verification pytest in harness 0.2.10 (next section) |
| Issue pinned in system prompt | **no** | bliverrigpdoge, v13: `{problem_description}` / `{hints?}` | Targets compaction ([bliverrigpdoge](https://www.kaggle.com/code/bliverrigpdoge/lb-0-22-3-tweaks-40-tool-calls-no-training)) |
| Post-submit | call plan | "reply with the single word Done" | Saves a turn |

The host statements that matter most are about the shape of the hidden set and the hard limits:

- About 120 tasks from **private repositories**. None of fastapi, rich, requests or httpx appears, no task touches an `async def`, and every hidden task "validates at 100%" with its gold patch ([Data](https://www.kaggle.com/competitions/gemma-4-developer-agent/data); [HOST T747248](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747248); [HOST T745998](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745998)).
- Tasks run sequentially under a **12-hour patch-generation limit**. Exceeding it errors the entire submission with no partial score, and a plan to score unfinished tasks as zero was withdrawn ([HOST T743063](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743063)).
- Edits to tests, `conftest.py`, `pyproject.toml` and `setup.cfg` are stripped from the patch. Untracked files in `/workspace` go into it ([HARNESS_README](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)).
- Distillation from external models is allowed ([HOST T742807](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/742807)).

Participants report no reliable LoRA gain anywhere in the competition:

- An r16 adapter trained on 2,000 DeepSeek runs solved 37 vs 38 held-out tasks and scored 0.12 on the leaderboard ([T751596](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751596)).
- Adapters that looked better locally scored **0.00** on the leaderboard ([T755677](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755677)).
- An Open-SWE-Traces QLoRA collapsed the agent from 37/60 to 4/51 through short thoughts and looping ([mobassir](https://www.kaggle.com/code/mobassir/why-your-leaderboard-can-t-see-a-3-point-gain)).

Our best adapter result, +3 net of 129, is therefore at the competition's ceiling for LoRA, not below it.

## Five gaps separate our local gate from the hidden scorer

### The gate's hardware does not match the scorer's clock

Our paired gate runs v2 and the candidate concurrently, at concurrency 3 each, on one RTX PRO 6000 or A100 ([campaign plan](/Users/jiangshengbo/Gemma-4-Agentic-Platform/docs/45-campaign-plan.md)). The scorer serves 31B with TP=4 on 4×L4 at `gpu_memory_utilization` 0.90 and `max_model_len` 32,768, one task at a time ([HARNESS_README](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)). Participant measurements on that hardware give:

- **33–35 tok/s decode** and a **10.3 s median call**; at 7 min / 28 calls, a quarter of runs hit the time cap ([T750974](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750974));
- about 8.7 s per call with thinking ([T746250](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746250)).

One participant estimates the scorer at **1.6–1.7× slower than an RTX PRO 6000 running three tasks at a time**, which is precisely our gate configuration ([alexust](https://www.kaggle.com/code/alexust/one-bundle-three-outcomes-0-24-0-17-no-score)). Our own data contradict the strong form of that claim. v2's local median was 323 s and its total 11.86 h for 129 tasks on the A100 ([campaign plan](/Users/jiangshengbo/Gemma-4-Agentic-Platform/docs/45-campaign-plan.md)). At 1.65× slower, most tasks would hit the 480 s cap and 120 tasks would overrun 12 hours, yet v2 finished on the scorer twice.

The defensible conclusion is the uncomfortable one: the scorer runs at roughly our local speed or faster, and **v2's 12-hour margin is thin**. Other participants' bundles have already crossed the line:

- A LoRA bundle at 8 min / thinking 4096 returned "no score" twice; at 6 min / 2048 it scored, because the adapter made tasks about 29% slower ([T755677](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755677)).
- A 40-call, 8-minute bundle like ours exceeded the runtime once ([alexust](https://www.kaggle.com/code/alexust/one-bundle-three-outcomes-0-24-0-17-no-score)).

Two consequences follow. Adapter-003's measured +20% time at thinking 2048 would very plausibly forfeit an entire submission. And LoRA serving shrinks the L4 KV cache by about 24%, from 36.4k to 27.7k tokens ([T744331](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744331)). That effect cannot appear on a 96 GB local card.

### The 120 s timeout also limits the grader's pytest run

In the harness source we hold (swegemma 0.2.10), `EvalConfig.timeout_seconds` overrides `harness.command_timeout_seconds` (`config.py` around lines 178–190). The hidden-test verification in `harness/verification.py` (around line 638) runs pytest with `timeout=config.harness.command_timeout_seconds` and sets `resolved = test_res.exit_code == 0` ([local harness source](/Users/jiangshengbo/.codex/zenithsync-p1-recovered/native-runtime-recovery/venv/lib/python3.13/site-packages/swegemma/harness/verification.py)). Two notebook authors reach the same reading, and one reports that `requests` test files take about 100 s ([leoprovorov](https://www.kaggle.com/code/leoprovorov/score-to-gemma-4); [hitarthjain0](https://www.kaggle.com/code/hitarthjain0/gemma-4-agent-what-took-lb-0-12-0-24)). Against this, the README is reported to fix verification at 300 s ([HARNESS_README](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)), and 60 s bundles have claimed 0.22 ([Repair Lab](https://www.kaggle.com/code/denpugovkin/gemma-4-repair-lab-compare-before-you-submit)).

The conflict is unresolved, and the scorer runs 0.2.11, not 0.2.10. Our local failure taxonomy has no timeout category: 56% assertion, 34% missing modules, 6% collection, 2% naming. But the local tasks come from four public repositories, and the hidden ones come from private repositories with unknown test runtimes. This is a cheap insurance item, not a likely large gain.

### A quarter of our dev set is unscorable locally but scorable on the scorer

Our failure analysis found that **29 tasks fail only on missing `inline_snapshot` / `dirty_equals`**. It concluded that they are "unsolvable for every entrant" and that only about 74 tasks discriminate between configurations ([campaign plan](/Users/jiangshengbo/Gemma-4-Agentic-Platform/docs/45-campaign-plan.md)). That holds for the public kit. The hidden set is a different matter: hosts say every hidden task validates at 100% with its gold patch ([HOST T744370](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744370)), and a scorer-like replica with the extra wheels passes **127 of 129** public gold patches against 52 in a plain notebook ([T751487](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751487)).

Adding those packages (plus asttokens and executing) to our local sandbox turns about 29 dead tasks into discriminating ones. That makes the gate roughly 40% more sensitive and moves its task mix closer to the scorer's. The broader lesson is that local cross-validation in this competition tracks the leaderboard poorly. Pairs of 0.18 → 0.05 and 0.24 → 0.10 are reported, and two configurations tied at 28/74 locally scored 0.17 vs 0.10 ([T744319](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744319); [T751973](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751973)). Tuning against fastapi or rich quirks will not transfer to private repositories that contain no async code.

### Compaction erases the issue and the tool results

Compaction fires at **14,336 tokens**. Its summarizer keeps only `part.text`, dropping function calls and responses, and hosts will not fix this under ADK v1 ([T754783](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/754783); [HOST T744794](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744794)). One participant reports that about 80% of runs cross the threshold and that one compaction **halves the odds of solving** (OR 0.50, CI 0.35–0.64, controlling for difficulty) ([mobassir](https://www.kaggle.com/code/mobassir/why-your-leaderboard-can-t-see-a-3-point-gain)).

The harness places `problem_description` and `hints` in ADK session state (`agent_runner.py` around lines 639–643). Otherwise the issue survives only in the first user message ([local harness source](/Users/jiangshengbo/.codex/zenithsync-p1-recovered/native-runtime-recovery/venv/lib/python3.13/site-packages/swegemma/harness/agent_runner.py)); two public bundles already pin it ([bliverrigpdoge](https://www.kaggle.com/code/bliverrigpdoge/lb-0-22-3-tweaks-40-tool-calls-no-training)). Our prompts never reference `{problem_description}`. Pinning it, using `{hints?}` with the `?` so that a missing key does not break templating, costs nothing.

A related risk comes from how prior reasoning is fed back. The harness now copies prior `reasoning_content` back into context ([HOST T744354](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744354)). A community audit found that re-injecting prior tool-turn reasoning drives verbatim repetition loops, from 33% of seeds to 0% once stripped ([HF #119](https://huggingface.co/google/gemma-4-31B-it/discussions/119)). Serving flags are fixed by the scorer, so we can only monitor this, through the repeat-call gate.

### Edit calls may be failing silently at a high rate

One audit found **43% of 31B `edit_file` calls failed** (107/246). The gemma4 parser mangles `"""` and drops arguments after a backtick, and rejected calls were resent up to 14 times. They cost wall time but not tool calls ([T747168](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747168); [T748323](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748323)). SWE-agent's data show why this matters: after a single failed edit, eventual edit success drops from **90.5% to 57.2%**, and cascading edit failures account for about 23% of unresolved instances ([SWE-agent](https://arxiv.org/html/2405.15793)). We have not reported our own failed-edit rate. If it is anywhere near 43%, it is a larger lever than anything in the config table.

### The gate itself is underpowered for small effects

v2 scored **33, 33, 30 and 31** on identical bytes. Of the 129 tasks, 26 were always solved, 14 sometimes and 89 never ([campaign plan](/Users/jiangshengbo/Gemma-4-Agentic-Platform/docs/45-campaign-plan.md)). Two identical arms should therefore produce about 7 discordant tasks from noise alone, giving an SD of the net difference of about 2.6. The pre-registered "+4 net" threshold is about 1.5 SD: a null candidate passes about 9% of the time, and a true +3 candidate only about 40–45%. Adapter-003 at +6/−3 and adapter-005 at +6/−5 both sit inside that noise band. The arithmetic forces a strategy: **single-knob changes worth one or two tasks can never pass this gate, so zero-risk changes must be stacked into one candidate**, or promising candidates must be replicated.

## Research favours faster localisation and real verification, not more turns or LoRA

### What the literature supports

The external SWE-agent literature lines up with our traces, which is reassuring as diagnosis but not as prescription:

- About 52% of SWE-agent's unresolved instances are incorrect or overly specific fixes, against our **56% wrong fixes**.
- Agents "succeed quickly and fail slowly": a median of 12 steps for resolved runs vs 21 for failed ones, with 93% of resolved instances submitted before the budget ran out.
- Interface details are worth 3–8 points each at GPT-4 scale. Removing linting from edits costs 3 points; a full-file viewer instead of a 100-line window costs 5.3; iterative search instead of summarized search costs 6 ([SWE-agent](https://arxiv.org/html/2405.15793)).
- Overthinking correlates with lower resolution, and picking low-overthinking runs cut compute 43% while improving results ([arXiv 2502.08235](https://arxiv.org/abs/2502.08235)).
- Adding 45 turns moved a 32B model by only 2.6 points ([SWE-Dev](https://www.arxiv.org/pdf/2506.07636)).

Our own budget experiments reproduce that last result. A 12 min / 60 / 60 budget gave +2/−2 against 8 min / 40 / 40. v2b60 cut turn-budget endings from 35 to 8 but raised session timeouts from 25 to 41 with no net gain ([campaign plan](/Users/jiangshengbo/Gemma-4-Agentic-Platform/docs/45-campaign-plan.md)).

### What our setting rules out

The literature's bigger wins do not fit our budget:

- Best-of-n with verifiers adds 4.5–6.2 points, but needs 16–32 rollouts ([SWE-Lego](https://arxiv.org/abs/2601.01426); [arXiv 2604.01496](https://arxiv.org/pdf/2604.01496)).
- Agentless reaches 48% for Qwen3-32B, but at about 83 calls and roughly 15 minutes per issue ([SWE-Effi](https://arxiv.org/html/2509.09853v2)).
- Fine-tuning gains appear only at scale. SWE-smith reaches 28.2% at 500 teacher trajectories and 40.2% at 5,016, from weaker bases. Its SFT students repeat 10+ identical commands in over 25% of trajectories, and such a run implies an 89% failure probability ([SWE-smith](https://arxiv.org/html/2504.21798)).

Self-generated trajectories in the low hundreds sit an order of magnitude below where gains appear, which matches our +3/129.

### Reproduce-then-verify, and the competition evidence against it

The one transferable idea with strong frontier-model evidence is reproduce-then-verify. SWE-Doctor reports +8 to +8.9 points from reproduction tests plus runtime diagnosis ([SWE-Doctor](https://www.alphaxiv.org/abs/2607.00990)). It maps onto our observation that failed runs ran a test only **18%** of the time against **42%** for resolved runs. That gap is observational, and it is confounded with task difficulty.

Competition evidence tempers it in three ways:

- In about 66% of tasks the existing suite already passes on buggy code, and in 34% it asserts the old behaviour. Logic that prefers "passes existing tests" destroyed correct patches ([T760014](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/760014)).
- Forcing earlier edits moved the first edit from 149 s to 91 s without changing solves ([T759329](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759329)). It also turned no-edit runs into wrong-edit runs, for only 26 → 30 solves ([T749198](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/749198)).
- The SWE-Doctor gain comes from frontier models; the paper reports no open 7B–70B results and no cost breakdown.

A useful verification step for us is narrow: a tiny repro of the issue's stated behaviour in `/tmp`, run with a `timeout` prefix, and not a call to the old suite as an oracle.

### Gemma-specific notes

For Gemma itself, Google recommends temperature 1.0 / top_p 0.95 / top_k 64 ([model card](https://huggingface.co/google/gemma-4-31B-it)). In this harness, temperature 0.7 made looping worse ([T745774](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745774)), so a moderate 0.3–0.4 is the only sampling change worth a slot.

On thinking, the hazard for round 7 is concrete. An adapter trained on targets without thought text learned to skip thinking ([T759329](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759329)), and thinking off roughly halves solves ([T746250](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746250)). Adapter-003 supervised its thinking, and our gate already checks the no-thinking rate, so this risk is covered. The expected-value problem remains: a 1024 budget has shown flat accuracy with large symmetric flips ([moranzavdi](https://www.kaggle.com/code/moranzavdi/gemma4-agent-lessons-for-competitors)). That inflates discordance, the very noise the +4 gate cannot see through.

## Ranked changes to test before the December 2 deadline

Evidence grades: **A** = verified in harness source, an official page or our own paired runs. **B** = a host statement, or at least two independent participant reports. **C** = a single participant claim, or research extrapolated across settings. **D** = our inference. Effect sizes are my estimates on our 129-task set, not measured results.

| Rank | Change | Evidence | Expected effect | Gate path |
|---|---|---|---|---|
| 1 | **Calibrate on scorer hardware**: one sequential official-harness run of v2 on a rented 4×L4 TP=4 pod (within the $5/h cap) over about 20–30 tasks. Measure median call latency against about 10 s, per-task time, a 12-h projection for 120 tasks, and LoRA KV cache size | B/C timing reports; A our v2 timings; D thin margin | None directly. Decides whether round 7 and any slower candidate can finish at all | Prerequisite; run once |
| 2 | **Restore the 29 env-blocked tasks** by adding `inline_snapshot`, `dirty_equals`, `asttokens` and `executing` to the local sandbox and verifier, then re-baseline v2 | A our analysis; B host gold-100%; C 127/129 replica | About +40% discriminating tasks; truer gate | Prerequisite; one v2 run |
| 3 | **Hygiene stack v3** = v2 + `{problem_description}` / `{hints?}` pinned in system.md + "Done." after `submit_patch` + scratch files in `/tmp` only + a rule never to put `"""` or backticks in `edit_file` arguments (use small unique anchors, re-read 15 lines after a failed edit) | A templating mechanism; C compaction OR 0.50; C 43% edit failures; C SWE-agent cascade (GPT-4 scale) | +1 to +4 combined | Standard +4 gate; stacking is what makes it detectable |
| 4 | **timeout_seconds 120 → 240**, with a prompt rule to prefix agent test commands with `timeout 90` | A source (0.2.10) vs official README "300 s" conflict; C 100 s test files | 0 locally; protects slow hidden test files | Non-inferiority: no resolution loss, time ≤ 1.05×. First audit local verification durations |
| 5 | **Targeted behaviour check**: after editing, run a minimal repro of the issue's claim in `/tmp` with `timeout`; do not treat pre-existing tests as the oracle | A 18% vs 42% (observational); C SWE-Doctor (frontier models); C 66/34% test-misleading | 0 to +4; costs 2–4 calls, which is risky against the 12-h margin | Standard gate on top of v3 |
| 6 | **Sampling 0.3–0.4 / top_p 0.95** | C single-run 47 → 51; C temperature 0.7 loops | ±2 | Fold into v3 only if the repeat-call rate stays below 5% |
| 7 | **Round 7, adapter-003 at thinking 1024** (in progress) | A +6/−3 at 2048 with +20% time; C 1024 flat | Probably fails the +4 rule; if it passes, its time and KV cost still need rank 1 | Existing rule, plus a scorer-hardware time check before any submission |
| 8 | **Small-model track (E4B)** as a strategic option, not a resolve-rate change: thinking 0 or about 768–1024 | C E4B 16 vs 10/114 with thinking off; B a $10k prize that requires an E2B/E4B final | Staff board top was 0.06 (dated 10-20) | Costs one of two final picks, about −0.9 expected private tasks on the main board |

Several changes should not be retested:

- **More turns or more time.** Measured twice, with no gain and runtime cost.
- **Thinking 4096.** No local gain, at a time cost.
- **Graph tools.** No gain: 34/68 vs 32/68 ([T756400](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/756400)), and embeddings place the gold file in the top 10 for only 35 of 129 tasks, against 67 for grep ([T744040](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744040)).
- **Earlier forced-edit deadlines.**
- **New self-generated LoRA rounds.**
- **Any best-of-n design.** Impossible in a declarative bundle.

Operationally, the calendar is tighter than the 15 days suggest:

- **November 25** is both the team-merger deadline and the reported notebook-publishing cutoff. Whether new notebook versions can be submitted after it is unanswered ([T759388](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759388)). Every candidate we might select should therefore exist as a submitted notebook version before then.
- Only one submission may be pending, scoring takes about a day, and a batch from November 9 has been stuck for over five days ([HOST T747519](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747519)). Do not leave the final candidate to the last 48 hours.
- Packaging traps are cheap to avoid: build the ZIP with `zip -D -X -r` ([T752282](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/752282)), and keep a single model across every agent YAML ([T758969](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758969)).
- Read every leaderboard result through the latency heuristic: an 8-minute bundle normally scores in 12–20 hours, and a very low score with unusual latency signals an infrastructure fault, not a regression ([T759329](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759329)).

## Conclusion

This competition is decided by two things that do not show up as resolve rate on our local runs: whether a bundle finishes inside 12 hours on 4×L4, and how many independent draws of a good configuration end up among the final picks. The prompt war is over. Every public recipe converges on about 10/58, and so do we. The leader's 17/58 proves that a better mean exists, but nothing public says how it was reached. So our remaining edge lies in measurement more than in invention. A gate that runs on scorer-speed hardware and on the full set of scorable tasks will reject candidates that look good locally but would overrun 12 hours, such as round 7 if its time cost survives the 1024 cap. It can also detect the +2 to +4 tasks a stacked hygiene candidate might deliver.

The most consequential unknowns are cheap to settle. One 4×L4 calibration run tells us whether v2's 12-hour margin is thin. One audit of local verification durations settles the 120 s timeout question in practice, whatever the source conflict. One count of failed `edit_file` calls in our traces tells us whether the largest silent loss in the competition is also ours. Settle those three before spending another training cycle.
