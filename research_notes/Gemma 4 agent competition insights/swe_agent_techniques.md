# Techniques that raise SWE-bench-style resolve rates for open ~30B models under tight per-task budgets (as of 2026-11-17)

Evidence grades used throughout: **[R]** = number reported by the primary paper/model card (fetched this session); **[R2]** = reported, but read only through a secondary summary or search snippet (verify before relying on it); **[C]** = community/anecdotal (HF discussions, GitHub issues, blogs); **[I]** = my inference. No number below was independently replicated by me. Unless noted, the setting is SWE-bench Verified (500 tasks), pass@1.

Constraint recap used for inferences: Gemma 4 31B-it, QAT W4A16, vLLM TP=4 on 4xL4, one run per task, 8 min / 40 tool calls / 40 turns / 120 s per call, about 6 min average per task (12 h / 120 tasks), offline python:3.13-slim + pytest sandbox. Our failure profile: 56% of failed patches are wrong fixes; failing runs rarely run tests (18% vs 42%); first edit comes late (call 9 vs 4); 30% of runs hit the 40-turn cap; LoRA on 177 self-generated trajectories gave at most +3/129.

## Q1. Which scaffold-level methods help most at this scale?

### Takeaway
In a single-attempt, tight-budget setting, the methods with the best evidence are the agent-computer-interface details: a linted, structured edit tool; bounded file views; summarized search; and short context history. These are worth 3-8 pp each in SWE-agent ablations. Next come fail-fast policies, because agents "succeed quickly and fail slowly", and a lightweight reproduce-then-verify loop. Best-of-n with verifiers adds real but modest gains (+4 to +6 pp at 8-32 rollouts for 32B models) and is incompatible with our one-run, about 6 min/task budget. Agentless-style pipelines do well for 32B models (48% vs 28-38% for agentic scaffolds in one small study), but they cost about 83 LLM calls and about 15 min per issue, so we cannot use them as published.

### Cited Findings
**Interface / ACI design (single attempt)**
- SWE-agent ACI ablations [R] (SWE-bench Lite, GPT-4 Turbo, baseline 18.0%):
  - Edit command: linted edit 18.0; edit without linting 15.0 (-3.0); no edit command 10.3 (-7.7).
  - Search: summarized search 18.0; iterative search 12.0 (-6.0); no search tools 15.7 (-2.3).
  - File viewer: 100-line window 18.0; 30 lines 14.3; full file 12.7 (-5.3).
  - Context: keeping the last 5 observations 18.0; full history 15.0 (-3.0).
  - [SWE-agent, arXiv 2405.15793](https://arxiv.org/html/2405.15793)
- SWE-agent failure dynamics [R]:
  - 51.7% of trajectories had at least 1 failed edit. Edits eventually succeed 90.5% of the time overall, but only 57.2% of the time after one failed edit.
  - Cascading edit failures account for about 23.4% of unresolved instances. About 52% of unresolved instances are incorrect or overly specific implementations.
  - Successful runs: median 12 steps / $1.21. Unsuccessful runs: average 21 steps / $2.52.
  - 93% of resolved instances were submitted before the budget ran out. The authors conclude that a larger budget is unlikely to help much ("succeed quickly, fail slowly").
  - [SWE-agent](https://arxiv.org/html/2405.15793)
- Aider edit formats [R, qualitative only]:
  - "whole" (rewrite the full file) is slow and costly. "diff" (search/replace blocks) is efficient. "diff-fenced" exists because Gemini-family models often break diff fencing. udiff reduced "lazy coding" placeholders in GPT-4 Turbo.
  - The page gives no quantitative error rates.
  - [Aider edit formats](https://aider.chat/docs/more/edit-formats.html)

**Scaffold choice for a 32B open model under resource constraints**
- SWE-Effi [R] (50 stratified Verified issues, single runs, Qwen3-32B via API). For each scaffold: resolve % / LLM calls / input k-tokens / output k-tokens / inference seconds per issue:

  | Scaffold | Resolve % | LLM calls | Input k-tok | Output k-tok | Inference s |
  |---|---|---|---|---|---|
  | AutoCodeRover | 38 | 14.7 | 55.5 | 20.4 | 106 |
  | OpenHands | 34 | 19.5 | 335 | 16.7 | 99 |
  | SWE-agent | 28 | 35.5 | 440 | 41.0 | 225 |
  | Agentless | 48 | 83.1 | 26.0 | 41.4 | 209 (+728 s CPU) |
  | Agentless-Mini | 28 | 2.0 | 34.1 | 9.3 | 49 |

  - Llama-3.3-70B: AutoCodeRover 28, OpenHands 20, SWE-agent 12, Agentless 28, Agentless-Mini 4.
  - [SWE-Effi, arXiv 2509.09853](https://arxiv.org/html/2509.09853v2)
- SWE-Effi [R], failed (U) vs resolved (R) runs for Qwen3-32B: OpenHands 237 s vs 132 s and 424k vs 211k tokens; SWE-agent 275 s vs 178 s; Agentless 1037 s vs 829 s. The paper's principle is that the number of interactions, not per-call intensity, drives cost. [SWE-Effi](https://arxiv.org/html/2509.09853v2)
- Kimi-Dev (72B, Qwen2.5-72B-Base with about 150B tokens of mid-training) [R2]:
  - 60.4% in the Agentless workflow setting with 40 patches and 40 tests. This is a heavy multi-sample result.
  - 48.6% pass@1 as an agent after SFT on 5k trajectories.
  - SWE-SWISS-32B is reported at 58.2% in a comparable workflow setting.
  - [Kimi-Dev, arXiv 2509.23045](https://arxiv.org/html/2509.23045v3)
- SWE-RL [R]: Llama3-SWE-RL-70B reaches 41.0% on Verified (abstract; the scaffold and sampling details were not visible on the abstract page). [SWE-RL, arXiv 2502.18449](https://arxiv.org/abs/2502.18449)

**Reproduction-test-first / runtime verification**
- SWE-Doctor (July 2026) [R2]:
  - Generates multi-faceted bug-reproduction tests, then does PDB-based runtime diagnosis, then patches.
  - Reports +8.0-8.9 pp average on SWE-bench Pro over baseline agents (mini-SWE-agent and live-SWE-agent), and an average of 75.7% on Verified across five frontier backends (GPT, Claude, DeepSeek). Removing either stage "significantly reduces" resolution.
  - It reports no open 7B-70B results and no cost numbers beyond "requires more computational resources and time".
  - [SWE-Doctor, arXiv 2607.00990](https://www.alphaxiv.org/abs/2607.00990)
- SWE-smith issue-text ablation [R]: when issues were phrased as failing tests, the student attempted reproduction in only 127 of 500 runs, versus 379 of 500 for LM-written issues. Resolve rates were 6.4-7.8% across variants at about 300 trajectories. Reproduction behaviour is learned from data, and its presence tracks better outcomes. [SWE-smith, arXiv 2504.21798](https://arxiv.org/html/2504.21798)
- Darwin harness notes [C, unreviewed]: a closed loop (run failing tests, feed the traceback back, retry) lifted a cheap model from 7.7% to 15.3%. The notes say the repair lift is "model-bound" below about 14B. [metaharness LEARNINGS.md](https://cdn.jsdelivr.net/npm/@metaharness/darwin@0.8.0/LEARNINGS.md)

**Best-of-n / verifiers (multi-attempt; flagged as needing many rollouts)**
- R2E-Gym [R2]:
  - 32B agent at 34.4% pass@1.
  - Execution-based and execution-free verifiers each saturate at about 42-43%. A hybrid verifier reaches 51.0% best@26.
  - [R2E-Gym, NeurIPS 2025](https://neurips.cc/virtual/2025/131676); [arXiv 2504.07164](https://arxiv.org/abs/2504.07164v1)
- SWE-Lego [R2]: Qwen3-32B goes from 52.6% (SFT only) to 58.8% at TTS@16 (+6.2 pp), using a generative verifier. Generative verifiers beat regression-style ones as the rollout count grows. [SWE-Lego, arXiv 2601.01426](https://arxiv.org/abs/2601.01426)
- SWE-ZERO/SWE-HERO [R2]:
  - 32 rollouts plus generative verifiers give up to +4.5 pp for the 32B model.
  - Best@K stays well below pass@K, and the authors name verifier selection as the bottleneck.
  - [arXiv 2604.01496](https://arxiv.org/pdf/2604.01496)
- R4P (reasoning patch verifier, no tests or sandbox) [R2]: Qwen3-32B reaches 32.8% with R4P test-time scaling. [arXiv 2602.03419](https://arxiv.org/pdf/2602.03419)

### Inferences
- [I] Our metrics match the literature's failure signature closely:
  - 30% of our runs hit the turn cap; SWE-smith-32B has about 53% of failures tied to limits.
  - Our failing runs are long and late to edit; SWE-agent's failing runs average 21 vs 12 steps.
  - Our 56% wrong-fix share is close to SWE-agent's about 52% incorrect or overly specific implementations.
  - The levers with evidence behind them are therefore (a) getting to a first edit sooner, (b) running a targeted test after editing, and (c) stopping or submitting before thrashing. More turns is not one of them.
- [I] Best-of-n is out of scope. One run per task and about 6 min average leave no room for 8-32 rollouts. Verifier gains also shrink at small n: +4 to +6 pp needs 16-32 rollouts.
- [I] A within-run "mini best-of-2" (generate two candidate edits and test both) is unlikely to pay off. SWE-agent shows that each failed edit cuts eventual edit success from 90.5% to 57.2%, so a single, verified edit beats branching.
- [I] Agentless's strength for Qwen3-32B (48%) comes from many cheap, short-context calls plus test-based selection. The part we can borrow inside one agent run is the ordering: localize, then edit, then validate with a reproduction test, then submit.

### Gaps
- I found no published single-attempt, wall-clock-capped (under 10 min) ablation of reproduce-first vs no-reproduction for a 30B-class model. SWE-Doctor gives no open-model or cost breakdown.
- CodeMonkeys and repository-map (Aider repo-map / RepoGraph-style) localization numbers for 7B-70B models were not retrieved this session.
- Satori-SWE (EvoScale) and DeepSWE numbers were not retrieved.
- I found no quantitative search/replace vs whole-file comparison for open 30B models.

## Q2. Reasoning budget: thinking tokens, temperature, and turns vs resolve rate under fixed wall-clock

### Takeaway
More reasoning or more turns helps only weakly once a model is in a fail-slow regime. Agents that overthink (long internal reasoning instead of acting) resolve less, and selecting lower-overthinking runs improved results while cutting compute 43%. Our wall-clock is dominated by decode time. Each 1k thinking tokens per turn probably costs tens of seconds on 4xL4 W4A16, which is an inference we need to measure. So a small per-turn thinking budget, with reasoning concentrated on localization and fix design, is the likely optimum. Raising turns or thinking uniformly is not.

### Cited Findings
- "Danger of Overthinking" [R]:
  - Over 4,018 SWE-bench Verified trajectories, higher overthinking scores correlate with lower resolution.
  - Reasoning models overthink more.
  - Picking the lower-overthinking candidate "improve[s] model performance by almost 30% while reducing computational costs by 43%". The abstract does not say whether the 30% is absolute or relative.
  - The named patterns are Analysis Paralysis, Rogue Actions, and Premature Disengagement.
  - [arXiv 2502.08235](https://arxiv.org/abs/2502.08235)
- A secondary summary of the same paper [R2]: sampling k=3 low-effort attempts and picking the lowest overthinking score gave 27.3% resolution, nearly matching high-reasoning configurations. [search snippet via arXiv 2502.08235](https://web3.arxiv.org/pdf/2502.08235)
- SWE-Dev [R2]: adding 45 more interaction turns moved a 32B model from 34.0% to 36.6% (+2.6 pp). [SWE-Dev, arXiv 2506.07636](https://www.arxiv.org/pdf/2506.07636)
- SWE-agent [R]: 93% of resolved instances finished before the budget ran out. A larger budget "is unlikely to help much". [SWE-agent](https://arxiv.org/html/2405.15793)
- SWE-Effi [R]: unresolved Qwen3-32B runs consume about 1.4-2x the tokens and time of resolved runs for agentic scaffolds. [SWE-Effi](https://arxiv.org/html/2509.09853v2)
- Open-SWE-Traces [R2, snippet]: OpenHands token totals were about 1.11B with thinking vs 2.08B without, so thinking reduced total tokens by cutting turns. Its best fine-tuned model reached 61.7% on Verified. [arXiv 2510.16786](https://arxiv.org/pdf/2510.16786.pdf) (the search tool matched this URL to the paper; I did not open it to confirm, so verify the attribution).
- "Thinking Longer, Not Larger" [R2, via literature review]: a 32B model combining internal and external test-time compute reached 46%. [Moonlight review](https://www.themoonlight.io/en/review/thinking-longer-not-larger-enhancing-software-engineering-agents-via-scaling-test-time-compute)
- Temperature:
  - Google recommends temperature 1.0, top_p 0.95, top_k 64 "across all use cases" for Gemma 4 [R]. [Gemma 4 31B-it model card](https://huggingface.co/google/gemma-4-31B-it)
  - SWE-smith evaluated its fine-tuned 32B student at temperature 0.0 with a 75-step cap [R]. [SWE-smith](https://arxiv.org/html/2504.21798)
- An execution-free result attributed to "Lin et al. (2026)" [C/R2, secondary only, unverified]: banning execution costs only about 1.25 pp on commercial models, and this "does not transfer to weaker setups". [search snippet](https://www.agentpatterns.ai/verification/execution-budgeting-program-repair/)

### Inferences
- [I] Back-of-envelope with unmeasured numbers: 480 s for 40 turns is about 12 s per turn including tool time. At a plausible 20-40 tok/s single-stream decode for W4A16 31B on 4xL4 (to be measured), a 1,024-token thinking budget alone is about 25-50 s per turn. A 1,024 budget on every turn is therefore incompatible with reaching 40 turns, which may explain part of our 30% turn-exhaustion and late first edits.
  - Recommendation: measure tokens/s and tokens per turn from our logs.
  - Consider a front-loaded budget: allow larger thinking on turns 1-3 (localization and plan) and on the turn after a test failure, and keep it small elsewhere. This needs harness support if the budget is per request; otherwise prompt "think briefly unless deciding the fix".
- [I] Raising turns from 40 to 60 (our round 6) is predicted by SWE-Dev/SWE-agent to give at most about +2-3 pp. Our round-6 gate rejection (repeat rate 7.6%) fits the "fail slowly" pattern: extra turns are spent repeating.
- [I] Temperature: Google's 1.0 is tuned for general use. For one-shot agent runs where repetition and rogue actions hurt, a lower temperature (0.6-0.8) is plausible, but it may increase verbatim loops. Low temperature is a known loop amplifier, though I found no Gemma-specific source. Run an A/B on our dev set rather than adopting either default blindly.

### Gaps
- I found no published sweep of thinking-token budget vs resolve rate under fixed wall-clock for any 30B-class model.
- I found no Gemma 4-specific temperature ablation on agentic coding.
- Decode throughput for Gemma 4 31B W4A16 on 4xL4 TP4 was not found in public sources; it must be measured locally.

## Q3. Fine-tuning open models on agentic SWE trajectories

### Takeaway
Published SFT gains for 32B models come from thousands of teacher-distilled trajectories over hundreds of repos: about 500 trajectories gives +8 to +20 pp from a weak base; 5k gives 40%; 50k+ gives 52-59%. Those gains start from bases far weaker than Gemma 4 31B. 177 self-generated (rejection-sampled) trajectories from the same model is roughly 10-30x below the scale where gains appear, and adds little new behaviour. Our +3/129 and lengthened thinking match this. Repetition and looping are documented side effects of SFT students.

### Cited Findings
- SWE-smith [R]:
  - Setup: Qwen2.5-Coder-32B/7B-Instruct students; Claude 3.7 Sonnet teacher; 5,016 trajectories; at most 3 per instance; resolved-only (rejection sampling); 75-step cap; temperature 0.
  - Results: 40.2% Verified / 30.7% Lite at 32B; 15.2% / 11.7% at 7B.
  - At 500 trajectories the 32B model reaches 28.2%. Gains grow roughly log-linearly with the number of repos.
  - Repo specialization (SymPy, 700 trajectories) gives 42.4% vs 33.3% at 32B.
  - [SWE-smith](https://arxiv.org/html/2504.21798)
- SWE-smith side effects [R]:
  - More than 25% of SWE-agent-LM-32B trajectories contain a repeated run of 10 or more identical commands, vs under 4% for Claude 3.7. A length-10 repetition implies an 89% failure probability. About 73% of these repetitions are `view` calls.
  - About 53% of student failures hit cost, step, or time limits, often while stuck in localization or reproduction.
  - Simple scaffold anti-repetition interventions reduced repetition but did not improve resolve rate.
  - [SWE-smith](https://arxiv.org/html/2504.21798)
- SWE-Gym [R2]:
  - Qwen2.5-Coder-32B SFT on 491 trajectories reaches 20.6% on Verified.
  - Rejection-sampling self-improvement in the Moatless scaffold reaches 19.7% on Lite.
  - [SWE-Gym, arXiv 2412.21139](https://arxiv.org/html/2412.21139v1)
- R2E-Gym [R2]: 32B at 34.4% pass@1 (trajectory count not retrieved this session). [R2E-Gym](https://arxiv.org/abs/2504.07164v1)
- SWE-Lego [R2]:
  - Qwen3-32B SFT-only reaches 52.6%. Contributions: dataset +25.6 pp from a 23.2% base, refined SFT +3.8, TTS@16 +6.2.
  - Error masking: invalid tool calls are excluded from the loss, but failing-test steps are kept.
  - A difficulty curriculum is used. Failure modes shift from "failed to reproduce" to "ran out of max turns" as training proceeds.
  - [SWE-Lego](https://arxiv.org/abs/2601.01426)
- CoderForge-Preview (Together) [R2]: Qwen3-32B SFT on Qwen3-Coder-480B trajectories (only those whose patches pass the tests) reaches 59.4%. Tasks come from R2E-Gym, SWE-smith, and SWE-rebench. [Together blog](https://together.ai/blog/coderforge-preview)
- SWE-Dev [R2]: 7B at 23.4% and 32B at 36.6%, using LLM-synthesized tests. [SWE-Dev](https://www.arxiv.org/pdf/2506.07636)
- Kimi-Dev [R2]: agentless-skill training as a prior; 5k agentic SFT trajectories give 48.6% at 72B. [Kimi-Dev](https://arxiv.org/html/2509.23045v3)
- SWE-RL [R]: an SFT baseline degraded out-of-domain performance on average, while RL improved it. Llama3-SWE-RL-70B reaches 41.0%. [SWE-RL](https://arxiv.org/abs/2502.18449)
- LoRA trajectory curation (Qwen2.5-Coder-7B, QLoRA r=64, alpha=128, lr 2e-5, 32k context; proxy metric = held-out cross-entropy, not resolve rate) [R2]:
  - At 500-1,000 trajectories, quantity dominates curation. Resolved-only vs random: delta +0.0049, p=0.78.
  - Quality ranking only matters by 2,000 trajectories (3.6%, p=0.016).
  - None of the 16 LoRA configurations reached perfect tool-call format compliance.
  - [arXiv 2607.17205](https://www.alphaxiv.org/abs/2607.17205)
- SWE-Effi [R]: unresolved runs cost about 2x resolved runs, so resolved-only (rejection-sampled) data from the same model skews toward short, easy tasks. [SWE-Effi](https://arxiv.org/html/2509.09853v2)

### Inferences
- [I] 177 self-generated trajectories sits below every published threshold. The smallest positive results start at about 491-500 trajectories, and those come from teachers much stronger than the student. With self-distillation, the trajectories encode behaviours the model already has on tasks it already solves. Expect regression toward its own easy-task style, and possible lengthened thinking if the resolved runs had long thoughts.
- [I] If more training is pursued, the evidence favours these choices:
  - Thousands of teacher-distilled trajectories from SWE-smith, SWE-rebench, R2E-Gym, or CoderForge data.
  - Mask invalid tool-call turns, as in SWE-Lego.
  - Cap trajectories per instance at about 3.
  - Filter out trajectories containing long repeated command runs. This is not tested in the papers but follows from the 89% failure association.
  - Truncate or strip thinking in targets to avoid lengthening reasoning.
  - Given the competition deadline and +3/129, the expected value is lower than prompt and sampling work.
- [I] I found no direct 30B-class LoRA vs full fine-tuning comparison on SWE resolve rate. The 7B LoRA paper's format-compliance failure is a concrete risk for Gemma's custom tool-call tokens.

### Gaps
- No direct LoRA-vs-full fine-tuning comparison on SWE-bench resolve rate at 30B scale was found.
- No public SWE trajectory fine-tuning results specific to Gemma 4 were found (only community checkpoints such as [gemma4-31b-full-mini-swe-secbench](https://featherless.ai/models/MananSuri27/gemma4-31b-full-mini-swe-secbench), with no verified numbers).
- Nemotron/SWE-Hero exact data scales were not retrieved. SWE-HERO was seen only as a TTS snippet.

## Q4. Gemma 4-specific tips (tool-calling, thinking mode, vLLM parsers, sampling)

### Takeaway
Use Google's sampling (temperature 1.0, top_p 0.95, top_k 64) as the baseline. Use vLLM's `gemma4` reasoning and tool parsers with vLLM's own example tool chat template. Pay close attention to how prior thinking is fed back in multi-step tool use. Google says to keep thinking for tool-call turns, but a community audit found that re-injecting prior tool-step reasoning causes verbatim repetition loops (33% to 0% on one derivative). That is directly relevant to our repetition gate and our lengthened thinking.

### Cited Findings
- Model card [R]:
  - Sampling: temperature 1.0, top_p 0.95, top_k 64 for all use cases.
  - Thinking: enabled by putting `<|think|>` at the start of the system prompt. When disabled, the 31B model still emits an empty thought block.
  - Multi-turn history: should contain only final responses, except tool-call turns, where thinking "should be preserved".
  - No thinking-budget mechanism is documented.
  - 256K context.
  - Benchmarks: LiveCodeBench v6 80.0%, tau2 76.9%. No SWE-bench number is published.
  - [Gemma 4 31B-it](https://huggingface.co/google/gemma-4-31B-it)
- HF discussion #119 (June 10) [C]:
  - The shipped template re-injects each prior tool-call step's reasoning after the last user message. This causes verbatim repetition loops in harnesses that send back `reasoning_content`.
  - The fix (disable historical re-injection) moved the agentic loop rate from 33% (4 of 12 seeds) to 0%.
  - This was measured only on a pruned-MoE derivative; it was found statically in the 31B template.
  - No Google response.
  - [HF #119](https://huggingface.co/google/gemma-4-31B-it/discussions/119)
- HF discussion #118 [C]: a template PR adds handling for prior-turn reasoning across tool-call chains and stricter argument validation. [HF #118](https://huggingface.co/google/gemma-4-31B-it/discussions/118)
- HF discussion #141 [C]: after a tool response, "thinking off" does not actually disable thinking; there is a proposed generation-prompt fix. [HF #141](https://huggingface.co/google/gemma-4-31B-it/discussions/141)
- HF discussion #115 [C]: the 31B model often skips reasoning after the first tool call. [HF #115](https://huggingface.co/google/gemma-4-31B-it/discussions/115)
- HF discussion #136 [C]: without usable tool schemas, the model emits tool-shaped text and claims actions succeeded. [HF #136](https://huggingface.co/google/gemma-4-31B-it/discussions/136)
- HF discussion #134 [C]: occasional missing arguments in a custom harness, but no loops. [HF #134](https://huggingface.co/google/gemma-4-31B-it/discussions/134)
- vLLM #39043 [C]: with `--reasoning-parser gemma4 --tool-call-parser gemma4`, reasoning tags leak into content when thinking is enabled. [vLLM #39043](https://github.com/vllm-project/vllm/issues/39043)
- vLLM #39468 (v0.19.0) [C]: tool calls are returned as raw text in content. [vLLM #39468](https://github.com/vllm-project/vllm/issues/39468)
- vLLM #39130 [C]: with `enable_thinking: false` plus the gemma4 reasoning parser, structured-output grammar is not enforced. [vLLM #39130](https://github.com/vllm-project/vllm/issues/39130)
- HF discussion #28 [C]: empty reasoning field; reasoning is expected in `reasoning_content`. [HF #28](https://huggingface.co/google/gemma-4-31B-it/discussions/28)
- Dynamo #8851 [C]: the stock HF Gemma 4 template does not emit the tool-definition encoding the parser expects. Workaround: vLLM's `tool_chat_template_gemma4.jinja`. [Dynamo #8851](https://github.com/ai-dynamo/dynamo/issues/8851)
- vLLM gemma4 parser API docs [R]: [docs.vllm.ai gemma4 parser](https://docs.vllm.ai/en/stable/api/vllm/parser/gemma4/)
- Aider [R]: Gemini-family models often break the standard diff fencing convention (hence "diff-fenced"). This is related lineage, not Gemma-verified. [Aider](https://aider.chat/docs/more/edit-formats.html)

### Inferences
- [I] Measure in our logs whether the official harness sends `reasoning_content` back for prior tool turns. If it does, the re-injection loop mechanism is a candidate cause of our 7.6% repeat rate and our long thinking.
  - Thinking-budget truncation may make it worse, because truncated thoughts get re-injected.
  - If eval_config or the served chat template is under our control, A/B the template with historical reasoning stripped.
- [I] Parse failures (raw-text tool calls, leaked tags) waste turns silently. Count turns with no valid tool call per run; any nonzero rate is a cheap fix target (template, parser version, or a prompt reminder of the exact tool format).
- [I] Edit format: Gemma (a Gemini sibling) may follow exact search/replace less reliably. Prefer `edit_file` with small unique anchors, and tell the model to re-read about 10 lines after a failed edit rather than retrying blind. SWE-agent shows that a failed edit drops eventual success from 90.5% to 57.2%.

### Gaps
- No official Google guidance on agentic coding, thinking budgets, or SWE-bench for Gemma 4 was found.
- No measured Gemma 4 31B tool-call error rate under vLLM was found.
- Which vLLM version fixed #39043 or #39468 was not checked.

## Q5. Prompt / sampling / eval_config vs harness changes, and the ranked catalogue

### Takeaway
Most of the high-value levers for our failure profile can be implemented by prompt and sampling alone: forcing an early localize-then-edit plan, a reproduce-and-test step, a fail-fast/submit policy, and anti-repetition rules. Thinking-budget shaping and the chat-template fix need eval_config or serving control. Verifiers and best-of-n need harness changes and many rollouts, and are out of scope under one run per task.

### Cited Findings
- The evidence backing each lever is cited in Q1-Q4. Key anchors:
  - Fail-slow dynamics and the edit-failure cascade: [SWE-agent](https://arxiv.org/html/2405.15793)
  - Repetition and limit-bound failures of 32B students: [SWE-smith](https://arxiv.org/html/2504.21798)
  - Overthinking hurts: [arXiv 2502.08235](https://arxiv.org/abs/2502.08235)
  - Interaction count drives cost: [SWE-Effi](https://arxiv.org/html/2509.09853v2)
  - Reproduction tests help (frontier models): [SWE-Doctor](https://www.alphaxiv.org/abs/2607.00990)
  - Template loop: [HF #119](https://huggingface.co/google/gemma-4-31B-it/discussions/119)
  - TTS gains need 16-32 rollouts: [SWE-Lego](https://arxiv.org/abs/2601.01426), [arXiv 2604.01496](https://arxiv.org/pdf/2604.01496)

### Inferences
[I] Ranked catalogue by expected gain per unit of wall-clock under our constraints. Gains are my estimates for our setting, extrapolated from the cited deltas, and are not reported numbers.

| # | Technique | Mechanism / evidence | Est. gain (ours) | Wall-clock cost | Where implemented |
|---|---|---|---|---|---|
| 1 | Fix the tool-turn reasoning re-injection (strip historical thoughts) and verify parser health (no raw-text tool calls, no leaked tags) | HF #119: loops 33% to 0% [C]; vLLM issues [C] | 0 to +4 tasks/129; reduces repeat-rate gate risk | Negative (saves turns) | Chat template / vLLM flags (eval_config or serving); not prompt |
| 2 | Front-loaded, small thinking budget (e.g. larger budget for plan and after test failure, about 256-512 otherwise), or "think briefly" prompt | Overthinking correlates with failure [R]; decode-dominated budget [I] | +2 to +5 | Negative (more turns fit in 8 min) | Budget: eval_config / per-request (harness if per-turn); prompt part is prompt-only |
| 3 | Early-edit protocol: at most about 4 exploration calls (grep and targeted read, never full-file view), then state hypothesis plus file:function, then edit | First edit at call 9 vs 4; 100-line views beat full-file by 5.3 pp; summarized search beats iterative by 6 pp [R] | +2 to +5 | Negative | Prompt-only |
| 4 | Reproduce-then-verify: write a tiny repro script or pytest from the issue before or right after editing; run it plus the nearest existing test file after the edit; if the env is missing deps, fall back to `python -c` import-level checks | Resolved runs test 42% vs 18%; SWE-Doctor +8-9 pp (frontier) [R2]; Darwin 7.7% to 15.3% [C] | +3 to +6 (targets the 56% wrong-fix share) | +2-4 calls, about 30-60 s | Prompt-only (uses run_command/write_file) |
| 5 | Fail-fast / submit policy: submit once the repro passes and the nearest tests pass; hard rule to submit the best current patch by about turn 32 or about 6.5 min (get_status); never end without submit_patch | 93% of resolved runs finish early; unsubmitted runs score 0 [R]/[I] | +1 to +4 (converts turn-exhausted runs with a plausible patch) | Negative | Prompt-only (if get_status exposes time/turns); otherwise harness |
| 6 | Anti-repetition and edit-failure rules: never repeat an identical command; after a failed edit_file, re-read 15 lines around the anchor before retrying; use smaller unique anchors | 10x repetition implies 89% failure; failed edit drops success to 57% [R] | +1 to +3 | Negative | Prompt-only (a harness-side repeat detector would be stronger; SWE-smith found scaffold interventions alone did not raise resolve) |
| 7 | Minimal-diff and generalization instruction: fix the root cause in library code, don't special-case the example, don't modify tests, check other call sites | About 52% of SWE-agent failures are incorrect or overly specific [R] | +1 to +3 | About 0 | Prompt-only |
| 8 | Sampling: A/B temperature 1.0 (Google) vs about 0.7, top_p 0.95, top_k 64; optional small repetition/presence penalty | Model card [R]; no Gemma agentic ablation [gap] | ±2 | 0 | Sampling config |
| 9 | Raise turns or the per-call cap (e.g. 60 turns) | +2.6 pp for +45 turns in SWE-Dev [R2]; fail-slow [R] | +0 to +2, but raises repeat-rate risk (our round 6) | Positive (uses budget) | eval_config |
| 10 | Within-run self-critique before submit (re-read the diff against the issue, one turn) | Execution-free critics saturate around 42-43% and need multiple candidates [R2] | +0 to +2 | 1 turn | Prompt-only |
| 11 | Best-of-n with test-, hybrid-, or generative-verifier selection | +4.5 to +6.2 pp at 16-32 rollouts; R2E 51% at best@26 [R2] | Not feasible (one run per task, about 6 min) | 16-32x | Harness |
| 12 | Agentless pipeline (localize, sample patches, generate repro tests, select) | Qwen3-32B 48% vs 28-38% agentic, but about 83 calls and about 15 min [R] | Not feasible as published; borrow the ordering only (items 3-5) | About 3x our budget | Harness |
| 13 | Further SFT/LoRA on self-generated trajectories | Needs thousands of teacher trajectories; ours +3/129 [R]/[ours] | About 0 to +3 at high cost | Training time | Training |

- [I] The prompt-only levers (items 3-7) overlap. Their combined effect is likely less than additive; a realistic combined target is +5 to +10 tasks of 129. That bound is speculative and should be tested on our dev split.
- [I] Pre-register at least the repeat rate and the turn-exhaustion rate as guardrails. Items 2, 3, 5 and 6 each lower turn usage, which should also reduce the repeat-rate risk that rejected round 6.

### Gaps
- Whether the official harness lets us change the chat template, per-turn thinking budget, or vLLM parser flags through eval_config was not determinable from public sources; check the harness docs locally.
- No public source quantifies prompt-only interventions for 30B models in a capped-time single-run setting. All gain estimates above are inferences.
