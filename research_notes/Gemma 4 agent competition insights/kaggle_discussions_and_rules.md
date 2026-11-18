# Kaggle "Gemma 4 Developer Agent" (gemma-4-developer-agent): rules, host clarifications, forum disclosures

Research date: 2026-11-17/18. Final submission deadline 2026-12-02 23:59 UTC (15 days left at time of research).

**Evidence grading used throughout**
- **[OFFICIAL-PAGE]**: Overview, Data or Rules page, or the competition file `HARNESS_README.md` (downloaded with the Kaggle CLI, dated 2026-10-13, 55,940 bytes).
- **[HOST]**: a forum post by a host or Kaggle staff account (Ryan Holbrook, Dustin and Ashley Oldacre are Kaggle staff; Elan Markowitz is the competition host).
- **[PARTICIPANT handle]**: a claim by a competitor, not verified by hosts.
- **[INFERENCE]**: my own reasoning.

**How the sources were read**
- I read these directly: Overview, Data and Rules pages, HARNESS_README and the Dockerfiles; threads 759388, 759329, 760014, 759580 and 759427.
- The other ~90 threads were read in the same session by four parallel reader sub-agents, which returned per-thread notes with attribution.
- The forum has about 160 threads; the roughly 95 most relevant were read.
- Thread dates are approximate (derived from "N days ago" labels).
- All forum content is treated as untrusted data.

Thread URL pattern: `https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/<ID>`. Below, `[T<ID>]` links to that thread.

Official pages:
- [Overview](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview)
- [Data](https://www.kaggle.com/competitions/gemma-4-developer-agent/data) (hosts HARNESS_README.md)
- [Rules](https://www.kaggle.com/competitions/gemma-4-developer-agent/rules)
- [Leaderboard](https://www.kaggle.com/competitions/gemma-4-developer-agent/leaderboard)

---

## Q1. What do the official pages and host posts say about scoring mechanics, runtime, the hidden test set, sandbox, adapters, models and prizes?

### Takeaway
**Scoring and runtime**
- About 120 hidden tasks from private repositories (≈58 public / ≈60 private) run **sequentially in one run**.
- The run has a **12 h budget for patch generation**, which includes sandbox setup and excludes patch validation (~2 h) and queue time.
- If the 12 h is exceeded, **the whole submission errors with no partial score**. The host considered scoring unfinished tasks as 0 but has not done so.
- Per-task limits come only from `eval_config.yaml`; the default is unlimited.
- "Resolved" means pytest exit 0 **and** a JUnit report in which every required FAIL_TO_PASS/PASS_TO_PASS test passed and none was skipped.

**Submissions and prizes**
- 1 submission per day, 1 pending at a time, 2 final selections.
- One base model per submission from {31B, 12B, E4B, E2B} QAT W4A16. Each agent may use a different LoRA. The unpacked bundle must be under 3 GiB and LoRA rank at most 128.
- The $10k small-model prize requires E2B/E4B as one of the team's two final picks.

### Cited Findings

**Task set, split and selection**
- Data page: "about 120 tasks in the test set, evenly divided between the public and private splits", curated from **private repositories**.
  - Hidden tasks pass a "near completion with frontier models" filter: a larger frontier model passes, or gets within one test case of passing.
  - The training set is replaced by the hidden test set at scoring time. — [OFFICIAL-PAGE Data](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)
- The public set is exactly 58 tasks (1 task ≈ 0.0172). This is inferred from Kaggle's truncated score values; there is no host confirmation. — [PARTICIPANT Geremie Yeo, T743506](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743506)
- Every submission runs **all tasks, public and private, in one evaluation**. This is deliberate: a public score shows the private part also ran. — [HOST Ryan Holbrook, T746008](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746008)
- None of the published training repositories (fastapi, rich, requests, httpx) occur in the test set, and every hidden task "validates at 100%" with its gold patch. — [HOST Ryan Holbrook, T747248](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747248); [T744370](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744370)
- No private task touches an `async def` function. Code graphs omit async functions, and the private graphs will not be updated. — [HOST Elan Markowitz, T745998](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745998)
- Submission and selection limits:
  - At most 1 submission per day; up to **2 Final Submissions**; maximum team size 5. — [OFFICIAL-PAGE Rules §2.1–2.2](https://www.kaggle.com/competitions/gemma-4-developer-agent/rules)
  - The winner is decided solely by the private leaderboard. Ties go to the earlier submission. — [OFFICIAL-PAGE Rules §3.7](https://www.kaggle.com/competitions/gemma-4-developer-agent/rules)
  - Team merger and entry deadline Nov 25; final deadline Dec 2. — [OFFICIAL-PAGE Overview](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview)
- A **one-pending-submission limit per team** was added on top of 1/day. A long pending run can cost a daily slot. — [HOST Dustin and Ryan Holbrook, T747519](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747519)
- Whether private scoring uses multiple runs or seeds: **no host answer**. Yurnero (LB #1) expects a single run. — [T754295](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/754295)

**Runtime and the 12 h limit**
- Overview text: the agent has "a limit of 12 hours to submit patches for all tasks, inclusive of sandbox setup time, but excluding time for patch validation". Per-task limits in `eval_config.yaml` are optional. — [OFFICIAL-PAGE Overview](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview)
- Tasks run **sequentially**.
  - The scorer reads only `timeout_seconds`, `max_tool_calls`, `max_time_minutes` and `max_turns`; the default is no limit.
  - Hitting 12 h errors the submission. — [HOST Ryan Holbrook, T743063](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743063)
  - Ryan's earlier plan to score unfinished tasks as 0 was **withdrawn ("reconsidering")** in mid-October, because public and private tasks share the run. — [HOST, T743063](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743063); [HOST, T749597](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/749597)
- Patch validation takes about 2 h if every task submits a patch and sits outside the 12 h. A task with no patch skips validation and scores 0. — [HOST Ryan Holbrook, T743663](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743663)
- A run on 10-22 ended "Notebook Timeout" after about 12 h, **with no partial score and the daily slot used**. — [PARTICIPANT Nir Aberman, T752017](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/752017)
- Queue time is reportedly excluded from the 12 h. This rests on a 10-Oct host reply cited in T752017; the reader could not see it directly. — [T752017](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/752017); [T748443](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748443)
- There is a separate **1,200 s inference-server startup limit** ("ServerStartupError…within 1200s"). vLLM startup on L4 was observed at 340–1,677 s. — [PARTICIPANT Syurolh, T747519](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747519) (cites T751264); [PARTICIPANT Pavel Nasovich, T744807](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744807)
- The current open question to hosts, unanswered, asks three things — [T759388](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759388):
  - whether the "12 h ⇒ whole submission errors" rule also applies to final private scoring;
  - whether the scorer environment is frozen until Dec 2 (wheelhouse "v31"; vLLM `gpu_memory_utilization` 0.90 in the README vs 0.80 quoted by participants);
  - whether new notebook versions can be submitted after `kernelsPublishingDisabledDeadline` = 2026-11-25.

**Harness mechanics** (all [OFFICIAL-PAGE HARNESS_README](https://www.kaggle.com/competitions/gemma-4-developer-agent/data) unless noted)
- vLLM settings: TP=4, `gpu_memory_utilization=0.90`, `max_model_len=32768`, `tool_call_parser=gemma4`, `reasoning_parser=gemma4`.
- LoRA sizing: `max_loras=len(adapters)` and `max_lora_rank=max(detected ranks)`, with a default of 128 if none.
- Each sandbox container gets 4 GiB RAM and 2 vCPUs, with `network_mode=none`.
- Per-task lifecycle:
  - Container A is the agent sandbox: snapshot at `base_commit` (no future git history), editable install, cached test site-packages, harness-written `pytest.ini`/`conftest.py`, then a "baseline" commit.
  - Container B is a fresh verification sandbox: apply the patch (4 fallback passes), reset protected/test files, apply `test_patch`, run pytest with JUnit output.
- Agent time starts **after** container setup ("Container Setup Is Excluded from Agent Time Budget"), but setup still counts toward the global 12 h.
- Defaults if `eval_config.yaml` omits them:
  - `inference.py`: 60 min/task, 100 tool calls, 500 turns, 300 s per command.
  - Verification pytest timeout: fixed at 300 s.
  - Command output cap: 5,000 chars. `read_file` cap: 150 lines / 10,000 chars.
- `submit_patch()` and `get_status()` do **not** count toward the tool-call budget.
  - After `submit_patch`, the loop ends once the current turn finishes.
  - Without `submit_patch`, the harness still captures `git add -N . && git diff` as a fallback when the agent finishes, hits max nudges, exhausts calls or turns, or times out.
- Up to 3 consecutive no-tool-call "nudges" are allowed before termination.
- A `budget_warning` field is appended only when `tool_calls >= 20` and 10 or fewer calls remain.
- **Protected-file stripping**: diff hunks touching the following are removed from the patch, and those files are reset before `test_patch`:
  - test files: `test_*.py`, `*_test.py`, or `.py` under `tests/`, `test/` or `testing/`;
  - runner config: `conftest.py`, `pytest.ini`, `pyproject.toml`, `tox.ini`, `setup.cfg`, `sitecustomize.py`, `*.pth`.
  - Note that **`pyproject.toml`/`setup.cfg` edits are discarded**.
- **Untracked scratch files inside /workspace go into the patch.** The README advises putting repro scripts in `/tmp` or deleting them.
- The resolved criterion is pytest exit 0 **and** JUnit with `passed>0`, `failures==0`, `errors==0`, and every required FAIL_TO_PASS/PASS_TO_PASS (or `test_patch`-extracted) test explicitly passed and not skipped. The score is resolved / total.
- Context management:
  - Compaction: `compaction_interval=15`, `overlap=2`, `token_threshold=14,336`, `event_retention_size=5`.
  - Context cache: `min_tokens 2048`.
  - Model retries: up to 5 on 429/5xx errors.
  - Participants report a discrepancy: interval 5 in the Getting Started notebook, and README threshold 32,768 at one point. — [T744692](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744692); [T748584](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748584)
- Generation limits:
  - `max_output_tokens` ranges 1–32,768, default 16,384.
  - `thinking_budget` ranges 0–32,768, default 4,096. A positive value turns thinking on and passes `thinking_token_budget` to vLLM; 0 turns it off.
  - `thinking_level` should be omitted with vLLM/LoRA.
- The task prompt can advertise the three graph tools and `read_file` limits.
  - Participants report this happened even when those tools were undeclared in older builds. — [T745028](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745028)

**Sandbox image and packages**
- `Dockerfile.sandbox` is `python:3.13-slim` plus git, patch, protobuf-compiler and pigz.
- It pip-installs `pytest`, `pytest-timeout==2.1.0`, `typer`, `pdm-backend`, `setuptools`, `wheel`, `poetry-core`, `hatchling`, `flit-core` and `editables`.
- It adds `imp.py` and `telnetlib.py` shims, git user agent@eval, and `TEST_TMPDIR=/tmp`.
- `Dockerfile.public` additionally copies the public `wheels/` (124 wheels). — [OFFICIAL-PAGE docker/ files](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)
- Test dependencies are not baked into the image. They are streamed per task from cached site-packages via `install_test_dependencies` (`/sandbox/setup.py --fast-path`). — [OFFICIAL-PAGE HARNESS_README §4.2](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)
- The **public** wheelhouse lacks the following, so only 52/129 public gold patches pass in a plain notebook — [T745775](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745775); [T756400](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/756400); [T751487](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751487):
  - `inline_snapshot` (+asttokens, executing), `dirty_equals`, `typing_inspection`;
  - pytest-httpbin/httpbin, python-multipart, orjson/ujson, sqlmodel, flask, PyJWT and more.
- The host's position is that hidden tasks validate at 100% with the gold patch, which implies the hidden environment carries whatever their tests need. — [HOST, T744370](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744370)

**Models, adapters and the small-model prize**
- Allowed models: `gemma-4-31b-it-qat-w4a16-ct`, `gemma-4-12b-it-qat-w4a16-ct`, `gemma-4-e4b-it-qat-w4a16-ct`, `gemma-4-e2b-it-qat-w4a16-ct`.
  - Every agent and subagent must use the same model.
  - Different LoRA adapters per agent are allowed (PEFT, `.safetensors`, under `adapters/<name>/`). — [OFFICIAL-PAGE Overview](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview); [HOST Ryan Holbrook, T748287](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748287)
- Smaller variants are scored under identical conditions: same 4×L4, same 12 h, same budgets.
  - Train LoRAs on the unquantized variants.
  - ParallelAgent allows concurrent LLM calls, but "tool calls are still executed sequentially". A ParallelAgent+tools bug in ADK 1.36 remains, and there will be no ADK v2 migration. — [HOST Ryan Holbrook, T748287](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748287)
- Bundle limits:
  - Unpacked bundle under 3 GiB including adapters; at most 10,000 files.
  - Allowed extensions: `.yaml/.yml/.md/.txt/.py/.json/.safetensors`.
  - No symlinks, no `..`, no Python entrypoints (declarative YAML only); `max_lora_rank` at most 128. — [OFFICIAL-PAGE HARNESS_README §2.4, §3.1](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)
- Small-model bonus ($10k):
  - Highest private-LB submission using E2B or E4B, which must be one of the team's two selected finals. LoRA is allowed, and the entry stays eligible for main prizes.
  - A daily standings notebook is promised. — [OFFICIAL-PAGE Overview](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview); [HOST Elan Markowitz, T751104](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751104)
  - The Overview prize text also says "Submissions must be made by November 12, 2026", which participants read as the paper-track date, not the small-model deadline. There has been **no host clarification**. — [T757244](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/757244)
- Prize totals:
  - Main prizes $37k / $18k / $10k.
  - Paper award $35k (paper deadline Nov 12, already passed).
  - Winners must license under OSI-approved open source and deliver training and inference code. — [OFFICIAL-PAGE Overview, Rules §2.5, §2.8](https://www.kaggle.com/competitions/gemma-4-developer-agent/rules)

**External data and distillation**
- Distillation from external LLMs is **allowed** if the teacher's license terms are respected and the output does not conflict with competition license requirements. No list of approved teachers was given. — [HOST Ashley Oldacre (pinned), T742807](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/742807)
- External data must be publicly available or reasonably accessible at minimal cost. Competition data may be used for any purpose but must not be redistributed to non-participants. — [OFFICIAL-PAGE Rules §2.4, §2.6](https://www.kaggle.com/competitions/gemma-4-developer-agent/rules)
- Open questions with no host answer:
  - SVD-derived or hand-constructed LoRAs (T756792, T759848).
  - Hosted-Gemma-API trajectory generation ([T759427](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759427)).

**Queue and failures**
- Scoring takes about 13–46 h end to end. Hosts say most runs finish "within ~24hish" of submitting, after queue fixes. — [HOST Dustin, T747519](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747519); [T748443](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748443)
- A batch of submissions from 2026-11-09 (14:30–17:35 UTC, 15 teams) has been stuck PENDING for 5+ days and blocks new submissions. There is no user-side cancel. Staff said "looking into this" around 11-16, with no resolution yet. — [T747519](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747519); [T759630](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759630)
- Kaggle-side failures ("Notebook Threw Exception", system errors) still consume the daily slot.
  - Reruns were promised several times, but there was no confirmation of completion, and the 743683 rescore was paused. — [HOST Ryan Holbrook, T743683](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743683); [T751339](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751339)

### Inferences
- [INFERENCE] With ~120 sequential tasks, the per-task average must be at most about (12 h − setup) / 120 ≈ 5.5–5.8 min of wall time, including per-task container setup. A cap above that only works because many tasks finish early (see Q3 numbers). The failure mode is total, not partial, so the cap must be set for the worst case, not the median.
- [INFERENCE] There are 2 final selections. Given the variance in Q2, choose them to diversify (two different configs) rather than picking the two highest public scores of near-identical configs. For a small-model prize attempt, one of the two slots must be spent on E2B/E4B.
- [INFERENCE] Hidden repos are private and unseen, with no async-function tasks. Tuning against fastapi/rich quirks (async code, Pygments versions, starlette `on_startup`) does not transfer.
- [INFERENCE] Two silent patch-loss traps:
  - Edits to `pyproject.toml`/`setup.cfg`/`conftest.py` are stripped, so a fix that needs a config change will fail.
  - Any new file under `tests/` is dropped.

### Gaps
- No host statement on whether vLLM server startup (up to 1,200 s) counts inside the 12 h.
- The exact order of tasks, and whether public and private tasks are interleaved, is not disclosed.
- No host answer on multiple-run private scoring, on an environment freeze until Dec 2, or on post-Nov-25 notebook versions (T759388).
- The exact private task count is not stated (≈60 inferred).
- The small-model prize deadline wording is unresolved (T757244).
- Whether a partial diff is graded when a per-task `max_time_minutes` fires: the README says the fallback diff is captured on timeout, but participants report that context-overflow and tool-exception paths lose the patch (Q4).

---

## Q2. Which threads report score variance, scorer failures, timeouts, harness bugs or workarounds, and what did they find?

### Takeaway
- Run-to-run noise on identical bytes is large. The participant consensus SD is about 1.5–3 tasks of 58 (0.03–0.05), with recorded swings of 0.17→0.12 and a claimed 0.24 reproducing at 0.17.
- An occasional infrastructure collapse can produce near-zero scores (0.18→0.01), plausibly from a vLLM gemma4 tool-parser infinite loop.
- Our observed 7–13/58 spread is within the reported range. Hosts have said nothing about averaging or reruns for the private LB.

### Cited Findings

**Variance on identical submissions**
- A byte-identical bundle scored 0.17 then **0.12**. Budget-Aware v2 scored 0.17 and 0.17, although its public notebook shows 0.22. Changes under about 0.05 (±3 tasks) are treated as noise. — [PARTICIPANT Muhammad Akhtar Quddus, T758969](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758969)
- A public "Budget-Fit v6 prompt-only" bundle claimed at 0.24 re-ran unchanged at **0.17**.
  - Harshit's leaderboard shape on 11-10 (5,250 teams): 1 at 0.29, 11 at 0.24, 74 at 0.22, 416 at 0.20, 964 at 0.17, 764 at 0.15; median 0.15.
  - Hypothesis: published scores are best-of-several draws. — [PARTICIPANT Harshit Kumar, T757588](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/757588)
- The same sha256 ZIP scored 0.18 (10-27) and **0.01** (10-31), both completing without error. Local runs on 121 tasks gave 50/50/47. Suspected cause: a frozen inference server. — [PARTICIPANT fan yunsheng, T750521](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750521)
- Same bytes scored 0.20, 0.18 and 0.15.
  - The pooled sigma is about 1.5 tasks per draw (citing another participant).
  - **A normal draw scores in roughly 12–20 h for an 8-minute bundle; a very low score with unusual latency signals an infrastructure fault.** — [PARTICIPANT Nir Aberman, T759329](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759329)
- Same LoRA bundle (thinking_budget 512) scored 0.15 then 0.13 on identical bytes. — [PARTICIPANT moruku36, T759329](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759329)
- Same package scored 0.17, 0.15, 0.13 and 0.15 on resubmits. — [PARTICIPANT Sahil Das, T748051](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748051)
- Identical files scored between 7/58 and 13/58 on the public LB. — [PARTICIPANT Munal Singh, T751596](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751596)
- Five submissions of a public notebook with an all-zero LoRA (temperature 0.2) scored 0.15 each time. Others report the same notebook ranging 0.13–0.20. — [PARTICIPANT xz, T759514](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759514)

**Measured noise in local runs**
- 19 of 123 tasks (15%) flipped between two identical Gemma passes. — [PARTICIPANT Ruijie Zhu, T747168](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747168)
- σ ≈ 1 task per 7-task rep (≈2 per 58).
  - Of tasks with 6+ draws, about 67% are flippy, 23% never solved and 10% always solved.
  - Scores are truncated to multiples of 1/58, so only 14 distinct values appear. — [PARTICIPANT Adam Johnson, T753524](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/753524)
- Identical runs differ by 1–2 of 55. With a single run, a real +2-task gain ranks the wrong way 11–20% of the time (106 runs). — [PARTICIPANT Akanksha Pathak, T758954](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758954)
- E4B fixed config × 10 runs on 114 tasks gave 14, 14, 15, 11, 13, 14, 11, 12, 11, 14 (SD 1.52).
  - Temperature 0.0 is **not deterministic**, because continuous batching changes floating-point order.
  - Pass@5 was 26/114 against a mean of 12.9. — [PARTICIPANT Japan OpenData Lab, T760014](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/760014)

**Local CV vs LB**
- Local CV does not track the LB:
  - pairs 0.18→0.05, 0.19→0.06, 0.23→0.12, 0.24→0.10;
  - an inverse case: 0.211→0.10 vs 0.316→0.03;
  - two configs tied at 28/74 locally scored 0.17 vs 0.10 on the hidden set. — [T744319](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744319); [PARTICIPANT Carson Rodrigues, T751973](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751973)
- An agent that solved 50% of the valid public tasks at 15 min/task timed out on the hidden set. At 5 min with thinking off it scored 0.05 on the LB. — [PARTICIPANT Manohar Papasani, T756400](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/756400)

**Timeouts and whole-run failures**
- Budgets that timed out (no score): thinking + skills with no eval config; 32 calls / 8 min.
- Budgets that scored: 24 calls / 5 min = 0.13; 28 calls / 5 min / 80 turns, timeout_seconds 240 = 0.15. — [PARTICIPANT Murugesan Narayanaswamy, T748168](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748168)
- A 12B submission at 8 min did not finish within 12 h. — [PARTICIPANT Dmitrii Gluzdov, T750974](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750974)
- LoRA with 8 min and thinking 4096 gave "complete, no score" twice. The same adapter at 6 min with thinking 2048 scored 0.17, because the adapter makes tasks about 29% slower. — [PARTICIPANT Kapil Chopra, T755677](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755677)
- A 4.5-min cap took about 10 h in total, i.e. about 0.5 min of per-task overhead. — [PARTICIPANT Oleksii Zhukov, T746250](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746250)

**Harness bugs and their status** (details in Q4)
- Tool-parser infinite loop on array arguments containing `]` (vLLM 0.19.1 `_parse_gemma4_array`).
  - It freezes the API server and ignores SIGTERM, so **every later task hangs until its time cap**.
  - Two freezes were seen in about 830 tasks, and one process grew to 26.7 GB and was OOM-killed.
  - Fixed upstream in vLLM PR #41991. No host reply; status on the scorer UNKNOWN. — [T753973](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/753973)
  - Reproduced against the competition wheel (`gemma4_tool_parser.py` sha256 682b2152…): a malformed `args:["Fix list[str] handling"]` loops forever, while correctly delimited input returns. — [PARTICIPANT bugkeeper, T759580](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759580)
- Other bugs: zip directory entries fail the submission; context overflow discards the patch; an undeclared tool ends the task; compaction drops tool results. — [T752282](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/752282); [T744692](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744692); [T745028](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745028); [T754783](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/754783)

**Public task validity**
- Only 68 of 129 public tasks discriminate in the public kit environment:
  - fastapi 29/67 valid, rich 39/48, requests 0/13, httpx 0/1;
  - 34 gold failures come from missing inline_snapshot (27) and dirty_equals (7);
  - 5 tasks pass with an empty patch.
  - 14.7% of planted bugs still "resolved".
  - Graph tools gave no gain (34/68 vs 32/68, p=0.69). — [PARTICIPANT Manohar Papasani, T756400](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/756400)
- A scorer-like local sandbox (extra wheels and pinned Pythons) gets 127/129 gold passes, against 52 in a plain notebook. — [PARTICIPANT Zbigniew Kirchner, T751487](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751487)

### Inferences
- [INFERENCE] With SD ≈ 2 tasks per draw and only about 70 submissions left in the competition, the public LB cannot rank configs within about ±3 tasks. The 0.29 (17/58) is about 1.5–2 SD above the 0.24 cluster (14/58). It may be a lucky draw or a genuinely better config; the private shakeup will tell.
- [INFERENCE] The private split is about 60 tasks, so its noise is comparable. Expected private differences between configs in the 0.17–0.24 band are mostly noise.
- [INFERENCE] The "hours-to-score" heuristic (normal 12–20 h for 8-min bundles; anomalous latency plus a very low score means an infrastructure fault) is a cheap diagnostic for our submissions. It fits our observed 20–24 h scoring times.
- [INFERENCE] A run with several consecutive tasks at the full time cap and zero LLM calls is the signature of the parser freeze. Avoiding array-typed tool arguments, such as `run_skill_script` args or `get_code_subgraph(nodes: list[str])`, lowers that risk.

### Gaps
- No host data on scorer-side variance, logs or per-task outcomes. Hosts never answered the requests for run logs (T750521, T759580).
- Unknown whether the scorer's vLLM carries the PR #41991 parser fix.
- No confirmation that the Nov 9 stuck batch will be rerun or cleared before Dec 2.

---

## Q3. What have top-scoring teams (0.24–0.29) disclosed about their approach?

### Takeaway
- The 0.29 leader (team "Yurnero") has disclosed **no method**. They have only commented that variance must be fixed, that a big shakeup is coming, that LoRA can score above 0, and that private gold patches are host-verified.
- Teams at 0.24 have disclosed tooling (a replay/fork prompt-search harness) but no config.
- Most public 0.22–0.24 claims come from a prompt-only, single-agent lineage (SuperAgent → Budget-Aware v2, Budget-Fit), and these do not reproduce at their claimed scores.
- Common settings around 0.15–0.24:
  - Gemma 4 31B, temperature 0.2, top_p 0.95, max_output 8192, thinking_budget 2048–4096;
  - about 5–8 min / 28–30 calls / 80 turns per task;
  - no subagents, skills or graph tools;
  - no proven LoRA gain.

### Cited Findings

**Leaderboard and the top teams' own statements**
- Leaderboard pulled with the Kaggle CLI on 2026-11-17:
  - Yurnero 0.29 (submitted 2026-10-29).
  - 14 teams at 0.24: Yike Xu, MUHAMMED IDRIS BIN YACOOB, SAVE, chizhu, pluris, Alberth Moreira, tammam alasha, Pınar Aksoy, Takumu Hata, Serhii Mosiiash, LuisSpecian, Radek, Sophia0817, bgunshui.
  - Then 0.22. Total 6,010 teams. — [Leaderboard](https://www.kaggle.com/competitions/gemma-4-developer-agent/leaderboard); [Overview](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview)
- Yurnero (LB #1) says:
  - 1 team solved 17 public tasks (0.29), 11 solved 14 and 74 solved 13 (as of about Nov 9);
  - probing the public/private split is impractical;
  - he expects the shakeup "will be huge";
  - the real problem is variance. — [T757626](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/757626)
- Yurnero also says: "Kaggle has never done" multi-run averaging ([T754295](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/754295)); a fixed seed won't make inference deterministic ([T750521](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750521)); scoring above 0 with LoRA is possible ([T755677](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755677)); 0.31 is reachable, and private gold patches are all host-verified ([T752848](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/752848)).
- Radek Maciaszek (around rank 13; team "Radek" is at 0.24) released "kaggle-glassbox".
  - It captures and replays model calls and forks runs from any step. He uses it to test hundreds of prompt variants on a few tasks before doing full runs.
  - It builds on the Budget-Fit notebook, and the write-up explicitly does not claim a better prompt. — [PARTICIPANT, T758817](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758817)
- "None of the top submissions" got gains from fine-tuning. — [PARTICIPANT OrDant (rank ~19), T748051](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748051)

**The public notebook lineage**
- Budget-Fit (verracodeguacas): 31B, about 4 min/task, scored 0.17 then 0.12 for one rerunner.
- Budget-Aware v2 (Igor Zharov, from matterhorn3838's "Gemma 4 SuperAgent"): 0.22 in its notebook, 0.17 and 0.17 on rerun.
- "Mega Ensemble" (kevlarzanderchi): 0.22.
- — [T758969](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758969); [T757588](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/757588)
- Most scores up to 0.22 come from single-agent setups such as the public SuperAgent notebook. — [PARTICIPANT Sahil Das, T748051](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748051)
- Three public configs scored 0.20, 0.18 and 0.05 with identical 8192 output / 4096 thinking / 8 min / 240 s settings. Budgets alone do not explain scores. — [PARTICIPANT XingLing, T755291](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755291)

**Configs disclosed in the 0.15–0.22 band**
- Murugesan Narayanaswamy, 0.15: 28 calls / 5 min / 80 turns, timeout_seconds 240, temperature 0.2, top_p 0.95, max_output 8192, thinking 4096. — [T748168](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748168)
- Luca Massaron, 0.18 without an adapter: 8 min / 28 calls / 80 turns, temperature 0.2, thinking 4096. — [T755677](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755677)
- About 0.20 from iterative prompt edits only, no subagents or skills: 8 min / 28 calls, thinking 4096, max_output 8192. Another participant uses 8 min / 30 calls and found subagents and skills unhelpful. — [PARTICIPANT Souvik_D_Biswas, RISHAV KUMAR, T750496](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750496)
- Adam Johnson's 0.18 used no subagents or skills; his LoRAs scored below baseline. — [T748051](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748051)
- yiyu0716, 0.17 at 7.5 min with thinking off (v19, 15 min / 100 calls locally). — [T747696](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747696)

**What local experiments found** (129 local tasks, single runs, so noisy)
- Ayush Thakur, sampling and thinking — [T746250](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746250):
  - temperature 0.0 = 47, 0.2 = 48, 0.4/1.0 = 51;
  - thinking 2048 = 50, 4096 = 48, 6144 = 48, **thinking off = 23**, thought summaries off ≈ 35;
  - cutting tool calls 50→25 lost 14 tasks;
  - graph tools gave no gain; an analyzer subagent gave +1 (noise).
- Ayush Thakur, timing:
  - Kaggle 4×L4 calibration: about 1,110 total tok/s, 8.68 s per model call with thinking, about 12.6 min fixed setup. He recommends 5.5 min/task. — [T746250](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746250)
  - Command timeout (100–300 s) had no effect.
  - An empty system prompt gave similar solves but more test-patch conflicts (8–11 vs 2–4) than a finalize/patch-hygiene prompt. — [T747857](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747857)
- 31B on Kaggle 4×L4 (Oleksii Zhukov) — [T750974](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750974):
  - 33–35 tok/s decode; per call ≈ 1.4 s + 28.7 ms per output token; median call 10.3 s;
  - at 7 min / 28 calls, mean 296 s per task;
  - 35% of runs used every call and 25% hit the time cap.
- Ilya Gordey, first-edit timing (1,254 runs): solve rate is 53% when the first edit lands within 3 calls of reading the gold file and 24% when it takes 12+ calls. 86% of never-solved tasks were in the right file. — [T751596](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751596)
- Nir Aberman, on prompt rules:
  - "Edit by call N" moved the median first edit from 149 s to 91 s but left solves unchanged.
  - The 4096 thinking cap is rarely reached, and 2048 cut timeouts with solves level.
  - Paper-track write-ups: "Find Early, Commit Late", "Commit Anatomy". — [T759329](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759329)
- kimdonggyu1255, on forced edits: with the default prompt, 38% of tasks never edit source. Budget-Fit's "edit by call 12" cut no-edit tasks to 13/112 but raised solves only 26→30, because forced edits become wrong edits. — [T749198](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/749198)
- A teacher comparison in this harness found Gemma 31B QAT at 54/124 vs DeepSeek V4 Pro 58/124 and Qwen3.6-27B 59/123. The union of all runs was 73/123, and 48 tasks were solved by nobody. — [PARTICIPANT Ruijie Zhu, T747168](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747168)

**LoRA evidence: no reliable gain reported anywhere**
- Munal Singh: an r16/α32 adapter trained on 2,000 DeepSeek runs solved 37 vs 38 for prompt-only on 98 held-out tasks, and scored 0.12 on the LB vs 0.15–0.17. Any LoRA adds 15–20% time per call. — [T751596](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/751596)
- icfoer: α scale 2.0 caused loops and LB 0.0. Training data without thinking, used with inference thinking on, produced long thought blocks. — [T750713](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750713)
- Luca Massaron: r16 and r4 adapters both scored 0.00 on the LB against 0.18 without an adapter, despite looking better locally (17 vs 12/129). — [T755677](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755677)
- E4B: LoRA, SFT and DPO results were null or negative. — [T753793](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/753793); [T750961](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750961); [T760014](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/760014)
- **Nir Aberman: an adapter trained on targets with no thought text learned to skip thinking.**
  - reasoning_content was empty in 0 of 109 calls, and tool calls leaked as plain text in 5 of 9 runs.
  - His suggested check: log reasoning length per call with and without the adapter. — [T759329](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/759329)
- The only targeted positive result is a training-free rank-128 LoRA that repairs an E4B copying bug (a `per_layer_model_proj` scale): copy failures went from 15/18 to 1/18. — [PARTICIPANT Michi Yamamoto, T753277](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/753277)

**Small models**
- On 4×L4, 12B decodes about 1.9× faster (62–64 tok/s) but solves under half as many tasks as 31B (8 vs 15–21 of 48). E4B solved 0/31 in one comparison. The best small-model LB score was 0.06 around Oct 20. — [T750974](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750974)
- E4B with zero thinking (16/114) beat think=4096 (10/114). A budget of 768–1024 was best for custom E4B systems. Setting `include_thoughts:false` made tool-argument JSON errors jump from 3 to 132. — [PARTICIPANT Japan OpenData Lab, T760014](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/760014)
- E4B with 80 calls / 150 turns / 5 min scored 0.08 then 0.05; temperature 0.6 scored 0.03. — [PARTICIPANT Muhammad Akhtar Quddus, T758969](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758969)

### Inferences
- [INFERENCE] There is no disclosed recipe above 0.24. The evidence says the 0.22–0.24 cluster is reachable with prompt-only single-agent configs plus a good draw, and that public LB differences in the 0.15–0.24 band are dominated by noise.
- [INFERENCE] Our config is close to the community optimum on budgets and sampling: 31B, temperature 0, thinking 2048, 8 min / 40 calls / 40 turns.
  - Thinking 2048 ≥ 4096 locally; temperature 0 vs 0.2 is a wash.
  - Our 40-turn cap is lower than the common 80. It can bind before 40 calls if turns are counted per LLM step. Worth checking against traces.
- [INFERENCE] For our planned adapter-003 with thinking budget 1024, the Nir Aberman finding is directly relevant: if SFT targets lacked thought text, the adapter may suppress thinking entirely.
  - Thinking off cost about half the solves in Ayush's ablation (23 vs 48).
  - Verify per-call reasoning length with the adapter before submitting.
  - LoRA's reported +15–29% per-task time also erodes 12 h headroom at 8 min/task.

### Gaps
- No method disclosure from Yurnero (0.29) or from 13 of the 14 teams at 0.24. Radek disclosed tooling only.
- No reproducible public bundle has been shown to score 0.24 twice.
- No external blog or write-up with a top-team approach was found. A web search surfaced only paper-track blogs and aggregator pages (e.g. [aiwiki](https://aiwiki.ai/wiki/gemma_4_developer_agent_competition), which wrongly states 31B-only).
- Paper-track write-ups ("Find Early, Commit Late", "Commit Anatomy") are referenced but were not read.

---

## Q4. Known gotchas that affect resolve rate (submit_patch, diff extraction, ignored files, test-file edits, scratch files, compaction, packaging)

### Takeaway
The patch is the git diff of /workspace against the baseline commit, after protected test and config files are stripped. Several paths silently zero a task:
- context overflow before the fallback diff;
- an undeclared or hallucinated tool, or a tool-argument exception;
- a scratch file or an edited test or config file;
- a patch that fails to apply;
- zip directory entries or mixed model variants failing the whole submission;
- a parser freeze stalling all later tasks.

Several early bugs (double-JSON encoding, dropped reasoning, `read_file` TypeError, empty embeddings, LoRA zeroing and KV hang) were fixed by hosts in late September and October.

### Cited Findings

**Patch capture and stripping**
- `submit_patch` and the fallback both run `git add -N . && git diff --binary _swegemma_baseline || git diff --binary HEAD`.
  - **Untracked files in /workspace (e.g. repro.py) are included.** Use `/tmp` or delete them.
  - Editing the harness-written `pytest.ini`/`conftest.py` pollutes the diff. — [OFFICIAL-PAGE HARNESS_README §8.1, §10](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)
- Protected test files and runner configs are stripped from the patch and reset before `test_patch`. The agent "must fix the underlying library code". — [OFFICIAL-PAGE HARNESS_README §8.2](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)
- The test-file reset was a silent no-op in swegemma 0.2.7, because `git checkout` aborted on missing pathspecs.
  - An edited existing test then made `test_patch` fail ("Reversed (or previously applied) patch"), so a correct fix scored 0.
  - Host: "addressing now". Participants verify that the Oct 8 build drops test-file edits from the submitted patch, i.e. likely FIXED. — [T744825](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744825); [T748323](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748323)
- An empty system prompt gave 8–11 test-patch conflicts vs 2–4 with a patch-hygiene/finalize prompt. — [PARTICIPANT Ayush Thakur, T747857](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747857)
- Lost to edited tests: 0 tasks with the robust-edit skill vs 3 without; resolved stayed at 6/16. — [PARTICIPANT MagicSword, T747923](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747923)

**Paths that lose the patch even after edits**
- `ContextWindowExceededError` is caught by the generic handler, which skips the fallback git-diff.
  - 44/44 overflowed sessions had an empty patch, 14 of them after successful edits.
  - Overflow rate: about 12% of sessions at threshold 14,336 and 17–33% at 32,768. Host: "I will look into it". UNFIXED/UNKNOWN. — [PARTICIPANT Avery Wright, T744692](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744692)
- 32,768 − 14,336 threshold − 16,384 default `max_output_tokens` leaves only 2,048 tokens of headroom. A 13.5k prompt jumping to 17.5k was rejected by vLLM. No compact-and-retry exists. — [PARTICIPANT Ruihuan, T747791](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747791); [T749198](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/749198)
- An undeclared or hallucinated tool raised ValueError in ADK `_get_tool`, ending the session with score 0. Host: "I'll implement something". Fix on the scorer is UNCONFIRMED.
  - The README now describes a `ToolErrorPlugin` that returns structured errors for undeclared tools. [INFERENCE] This suggests it was addressed in later builds. — [T745028](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745028); [HARNESS_README §5.3](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)
- `run_skill_script` with `file_path` as a list raised AttributeError and ended the task with an empty `agent_patch`, even after a successful `submit_patch`: 33 of 960 runs. UNFIXED per the thread. — [PARTICIPANT Joseph Arthur Koo, T745028](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745028)
- Compaction's `LlmEventSummarizer` keeps only `part.text`, so function_call and function_response parts are dropped from summaries. The agent loses tool results after compaction unless it restated them in text. UNFIXED, and there will be no ADK v2. — [T754783](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/754783); [HOST, T744794](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744794)

**Tool-call reliability**
- In vLLM's gemma4 parser, `edit_file` calls containing `"""` get mangled, and arguments are lost after a backtick.
  - 43% of 31B `edit_file` calls failed (107/246); 105 of 524 edit/write calls were rejected ("mandatory input parameters are not present"), often resent identically up to 14 times.
  - Rejected calls don't count toward the call cap but do cost time. — [T747168](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747168); [T747923](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747923); [T748323](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748323)
- Double-JSON-encoded tool results caused 39 of 62 "old_string not found" failures. Host: fixed in the latest wheelhouse (one encoding level plus an unescape fallback). FIXED (partly).
  - Remaining: if `new_string` is escaped while `old_string` matches, the escapes are written into the file. — [T744272](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744272)
- The baseline agent repeats the same command up to 69 times. Lower call caps limit looping better than prompt wording; temperature 0.7 made looping worse. — [T745774](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745774)
- Prompt-level instructions are unreliable:
  - "First, call X" ran 5/16 times, while a SequentialAgent setup step ran 47/48. — [T747923](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/747923)
  - Budget instructions were ignored in 61% of tasks for E4B. — [T760014](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/760014)

**Thinking and reasoning plumbing**
- vLLM 0.19.1 ignored `reasoning_content`, so prior thoughts were dropped between tool calls. Host: fixed in the wheelhouse; adk_submission 0.2.12+ copies it into `reasoning`. With the fix, context grows faster and compaction triggers earlier. — [HOST Ryan Holbrook, T744354](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744354)
- `include_thoughts:false` used to disable reasoning. Since the Oct 8 build it only hides thoughts when a budget is set (participant-verified).
  - `thinking_budget` and `seed` were not forwarded earlier; host says fixed. — [T745059](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745059); [HOST, T744794](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744794)

**LoRA serving**
- An early bug shrank the KV cache to about 7.6k tokens with LoRA enabled, and longer requests hung. Host sized LoRA to the submission; FIXED (28k prompts complete on wheelhouse v28).
  - Adapters still cost about 24% of KV cache (36.4k → 27.7k tokens). — [T744331](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744331); [HOST, T744794](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744794)
- Adapters were silently zeroed by double registration in patched vLLM 0.19.1; FIXED per host from wheelhouse v23.
  - One participant later still saw logprobs identical to base with noise adapters. Effect UNKNOWN. — [T743508](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743508)
- PEFT cannot attach to the `-ct` checkpoint. Train on a dequantized bf16 or unquantized QAT copy, and patch PEFT for `Gemma4ClippableLinear`. — [T750713](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750713); [T750597](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/750597); [T755677](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/755677)

**Packaging**
- A zip containing directory entries fails after about 1 h with no explanation. Use `zip -D -X -r`. — [PARTICIPANT Victor Paslay, T752282](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/752282)
- A leftover agent YAML using a different model (E4B) inside the zip caused "Notebook Threw Exception". The single-model check scans **all standalone agent YAMLs** in the bundle. — [T758969](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/758969); [HARNESS_README §3.2](https://www.kaggle.com/competitions/gemma-4-developer-agent/data)
- Wheelhouse builds changed without version bumps (the Sep 30 build changed 10 files while keeping 0.2.7). Fingerprint builds by checksum.
  - Graph-tool replay returned results for 82 → 11 → 270 → 270 of 314 calls across builds. — [T748323](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/748323)

**Graph and embedding tools**
- Embeddings are near-collapsed: mean random-pair cosine 0.78–0.90. The gold file is in the top 10 for 35/129 tasks vs 67 for grep, and `search_similar_code` only accepts existing node names. — [T744040](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744040)
- Graphs have only "calls" edges and no async functions. — [T742911](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/742911)
- Graph tools give no measured gain. — [T756400](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/756400); [T746250](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746250)

**Task-text limits**
- `hints_text` is empty in 129/129 public tasks. 18 statements are just a title plus a URL, and the sandbox is offline.
- 6–16 public tasks need names or wording that are not in the prompt.
- Hosts have not said whether hidden tasks include issue bodies. — [T746944](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/746944); [T745855](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745855); [T757149](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/757149)

**Pre-existing tests mislead in both directions**
- In about 66% of dev tasks the existing suite already passes on the buggy code, so it cannot confirm a fix.
- In about 34% the task is a spec change, so the old tests assert the buggy behavior and a correct patch breaks them.
- Logic that prefers "patch passes existing tests" destroyed correct patches. — [PARTICIPANT Japan OpenData Lab, T760014](https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/760014)

### Inferences
- [INFERENCE] Highest-value hygiene for our bundle:
  - Keep `max_output_tokens` around 8192 so prompt + output stays under 32,768 below the 14,336 compaction trigger. This prevents the overflow that discards patches.
  - Instruct scratch files into `/tmp`.
  - Never edit tests or `pyproject.toml`/`setup.cfg`.
  - Declare only flat, non-array tools and avoid skills with list arguments; this sidesteps the parser freeze and the list-argument crash.
  - Package with `zip -D -X -r` and keep exactly one model across all YAMLs.
- [INFERENCE] Tool results are lost after compaction. Prompting the agent to restate key findings (file path, failing line, planned fix) in plain text before it edits may preserve them across compaction.
- [INFERENCE] Calling `submit_patch` is free and ends the loop. If time is near the cap, an early `submit_patch` after the first plausible edit guarantees capture, whereas relying on the fallback is exposed to the overflow and exception paths above.

### Gaps
- No host confirmation of which fixes (undeclared-tool handling, overflow patch capture, parser loop) are on the current scorer build (wheelhouse "v31" per T759388).
- Unknown whether hidden task statements are richer than the public ones (issue bodies, hints).
- No official list of the hidden environment's test packages; only the host's "validates at 100%" assurance.
