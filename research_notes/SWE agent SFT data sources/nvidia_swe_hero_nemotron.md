# NVIDIA public SWE / agentic-coding SFT datasets as training data for a Python repository-repair agent

**All HF API / dataset-viewer facts below observed 2026-10-28 → 2026-10-29 (UTC) unless a different date is stated.** Numbers labelled "computed" were derived by me with DuckDB 2.0 reading the pinned parquet revisions directly over `hf://`; numbers labelled "card claim" are NVIDIA's prose and were not independently reproducible.

---

## Q1. `nvidia/SWE-Hero-openhands-trajectories` and sibling `SWE-Hero*` / `SWE-Zero*` datasets and models

### Takeaway
SWE-Hero is a 34,269-row OpenHands trajectory set over 11,766 issues / 1,695 repos, CC-BY-4.0, teacher Qwen3-Coder-480B-A35B-Instruct, with a **4-tool** OpenHands schema (not the 5-tool nebius one). It ships **no success/failure label, no gold patch and no verification tests** — unlike its much larger siblings `nvidia/SWE-Zero-openhands-trajectories` (318,115 rows) and `nvidia/Open-SWE-Traces` (1,138,945 rows, which *does* carry `resolved` and `reference_patch`). No NVIDIA SWE-Hero/SWE-Zero **model** weights are published on Hugging Face.

### Cited Findings

**`nvidia/SWE-Hero-openhands-trajectories`** — [HF API](https://huggingface.co/api/datasets/nvidia/SWE-Hero-openhands-trajectories?blobs=true) (observed 2026-10-28)
- Current `main` revision SHA: **`150bc119e52c647216fce285fd801f16b6fd745b`**. `createdAt` 2026-04-17T00:27:41Z, `lastModified` 2026-05-08T17:10:16Z. `gated: false`. 3,000 downloads, 30 likes.
- Card license: **`cc-by-4.0`** (frontmatter `license: cc-by-4.0`; no `license_name`/`license_link`). Tagged `arxiv:2604.01496`.
- File list: 17 files, **2,402,031,292 bytes total (2.402 GB)**. `data/train-{00000..00013}-of-00014.parquet` (140.9 MB – 245.8 MB each: 151791408, 151548338, 151438507, 157662607, 157992475, 157021081, 175925246, 168067123, 171348241, 208247441, 245825405, 163740812, 200489804, 140913929), plus `README.md` (5,622 B), `tools.json` (10,749 B), `.gitattributes` (2,504 B).
- Dataset-viewer `/size`: **34,269 rows**, 7 columns, single `train` split, `num_bytes_parquet_files` 2,402,012,417, `num_bytes_memory` **8,491,261,226** — [datasets-server /size](https://datasets-server.huggingface.co/size?dataset=nvidia/SWE-Hero-openhands-trajectories)
- Columns (7): `instance_id`, `repo`, `license`, `trajectory_id`, `trajectory` (list of `{content, role, tool_calls[{function{arguments,name}, id, type}]}`), `model_patch`, `dataset` — [dataset card](https://huggingface.co/datasets/nvidia/SWE-Hero-openhands-trajectories)
- Card claim: "34k agent trajectories collected using the OpenHands framework … synthesized using Qwen3-Coder-480B-A35B-Instruct"; "Total Issues: **11,766**", "Total Trajectories: **34,269**"; "We use MIT, Apache-2.0, BSD-2-Claude [sic], and BSD-3-Clause licenses only"; "This dataset is ready for commercial/non-commercial use." Data Version 1.0. Data Developer: NVIDIA. — [dataset card](https://huggingface.co/datasets/nvidia/SWE-Hero-openhands-trajectories)
- **Teacher model:** Qwen3-Coder-480B-A35B-Instruct, for both the trajectories *and* (for the R2E-Gym subset) for synthesising the issue statements from R2E-Gym prompts — [dataset card](https://huggingface.co/datasets/nvidia/SWE-Hero-openhands-trajectories)
- **Scaffold:** OpenHands (`github.com/OpenHands/OpenHands`). **The card does not state an OpenHands version number** (contrast: `nvidia/Open-SWE-Traces` v1.0 explicitly says OpenHands **v0.53.0**) — [Open-SWE-Traces card](https://huggingface.co/datasets/nvidia/Open-SWE-Traces)
- **Tool set = 4 tools**, from the shipped `tools.json` (observed 2026-10-28) — [tools.json](https://huggingface.co/datasets/nvidia/SWE-Hero-openhands-trajectories/raw/main/tools.json):
  - `execute_bash` — required `["command"]`; props `command` (string; "Can be empty string to view additional logs when previous exit code is `-1`. Can be `C-c` (Ctrl+C) to interrupt the currently runni…"), `is_input` (string, "If True, the command is an input to the running process… Default is False"), `timeout` (number, hard timeout in seconds).
  - `think` — required `["thought"]`; prop `thought` (string, "The thought to log.").
  - `finish` — required `["message"]`; prop `message` (string, "Final message to send to the user").
  - `str_replace_editor` — required `["command","path"]`; props `command` (enum-in-prose: `view`, `create`, `str_replace`, `insert`, `undo_edit`), `path` (absolute path, e.g. `/workspace/file.py`), `file_text` (for `create`), `old_str`, `new_str`, `insert_line` (insert AFTER that line), `view_range` (array, for `view`).
  - `nvidia/SWE-Zero-openhands-trajectories` ships the **identical 4-tool `tools.json`** (same tool names, same required/props lists) — [SWE-Zero tools.json](https://huggingface.co/datasets/nvidia/SWE-Zero-openhands-trajectories/raw/main/tools.json)
- **Computed tool-call frequency** (shard `train-00000-of-00014.parquet`, 2,500 rows, pinned sha 150bc119): `execute_bash` 77,771; `str_replace_editor` 59,763; `think` 6,923; `finish` 2,500 (= exactly one `finish` per trajectory). Role counts in the same shard: `assistant` 146,957; `tool` 144,457; `system` 2,500; `user` 2,500 — i.e. exactly one system + one user message per row, so **the issue statement is a single user turn and there is no multi-turn user interaction**. ~58.8 assistant tool calls per trajectory. (computed, DuckDB, 2026-10-29)
- **Computed trajectory length:** 34,269 rows; mean **118.57 messages** per trajectory in shard 0. The dataset-viewer `/statistics` over a 22,500-row sample reports the `trajectory` list length as min 49, max 201, mean 123.77, median 119, std 31.31 — [datasets-server /statistics](https://datasets-server.huggingface.co/statistics?dataset=nvidia%2FSWE-Hero-openhands-trajectories&config=default&split=train)
- **Trajectories per issue (computed, full dataset):** 11,066 issues have exactly **3** trajectories, 371 have 2, 329 have 1. Mean 2.91 trajectories/issue. Per-source mean: SWE-rebench 2.91, R2E-Gym-Subset 2.97, SWE-Gym-Raw 2.86, SWE-Gym 2.81. So the design is **3 rollouts per issue**, with a small tail where fewer survived.
- **Failed trajectories: not labelled and apparently not included.** The 7-column schema has **no `resolved` / `success` / `reward` field** and no reference patch — there is no way to separate successful from unsuccessful rollouts within the file. The paper frames SWE-HERO as the "execution-backed" stage ("Stage 2 … applies targeted, execution-backed refinement"), implying the released SWE-Hero rows are the execution-filtered ones, but **the card never states this explicitly** — [arXiv 2604.01496](https://arxiv.org/abs/2604.01496); [dataset card](https://huggingface.co/datasets/nvidia/SWE-Hero-openhands-trajectories)

**Sibling `nvidia/SWE-Zero-openhands-trajectories`** — [HF API](https://huggingface.co/api/datasets/nvidia/SWE-Zero-openhands-trajectories?blobs=true) (observed 2026-10-28)
- SHA **`7b3cd106d00f60918e722d33a1d74bc67072a7ea`**; created 2026-04-17T00:27:16Z, lastModified 2026-05-05T19:34:05Z; `gated: false`; 4,129 downloads, 27 likes; license `cc-by-4.0`; tagged `arxiv:2604.01496`.
- 67 files, **12,207,173,274 bytes (12.207 GB)**: `data/train-{00000..00063}-of-00064.parquet` (137.8 MB – 234.6 MB each) + `README.md`, `tools.json` (11,115 B), `.gitattributes`.
- `/size`: **318,115 rows**, 7 columns, one `train` split; parquet bytes 12,207,153,721; memory **33,945,440,130**.
- Identical 7-column schema to SWE-Hero (so likewise **no success label, no gold patch, no tests**).
- Card claim: "318k agent trajectories"; "Total Issues: **118,092**", "Total Trajectories: **318,115**"; teacher Qwen3-Coder-480B-A35B-Instruct; sources SWE-Gym, SWE-Gym-Raw, R2E-Gym-Subset, **SWE-Fixer-Train-110K**, SWE-rebench; "ready for commercial/non-commercial use" — [dataset card](https://huggingface.co/datasets/nvidia/SWE-Zero-openhands-trajectories)

**Paper** — [arXiv 2604.01496](https://arxiv.org/abs/2604.01496) (observed 2026-10-28): "From SWE-ZERO to SWE-HERO: Execution-free to Execution-based Fine-tuning for Software Engineering Agents", Nikolai Ludwig, Wasi Uddin Ahmad, Somshubra Majumdar, Boris Ginsburg, 2026, cs.CL. Abstract claims a release of "**300k SWE-ZERO and 13k SWE-HERO trajectories** distilled from Qwen3-Coder-480B", agents based on the **Qwen2.5-Coder** series, and "**SWE-HERO-32B achieves a 62.2% resolution rate on SWE-bench Verified**" plus 44.1% zero-shot on SWE-bench Multilingual for Python-only-trained agents.
- **Conflict:** the paper abstract says 300k / 13k; the HF cards and the dataset-viewer say **318,115 / 34,269**. The HF artefacts are newer (last modified 2026-05-05 and 2026-05-08) than the paper's figures, so treat the HF numbers as the shipped sizes and the paper numbers as superseded.

**No NVIDIA SWE-Hero / SWE-Zero model weights on HF.** A `?author=nvidia&limit=500&sort=lastModified` model listing contains no `SWE-*`, `*-Hero`, or `Nemotron-*Coder` entries (only `nvidia/Qwen3-Coder-480B-A35B-Instruct-NVFP4`, `nvidia/Kimi-K2.7-Code-NVFP4`, `nvidia/Kimi-K2.7-Code-DFlash`). A full-HF `?search=SWE-Hero` / `?search=SWE-ZERO` model search returns only third-party accounts. — [HF models API](https://huggingface.co/api/models?author=nvidia) (observed 2026-10-28)

**Third-party mirrors exist** (not NVIDIA-controlled, do not rely on them): `alucent/mirror-SWE-Hero-openhands-trajectories`, `Arsh9210/SWE-Hero-openhands-trajectories`, `Arsh9210/SWE-Zero-openhands-trajectories`, `fan-shu/swe-mt-combined-*-hero-*`, `jackyk02/swe-hero-openhands-qwen3.6-35b-a3b-fp8-embeddings-256k` — [HF datasets search](https://huggingface.co/api/datasets?search=SWE-Hero)

### Inferences
- SWE-Hero's 4-tool schema is a **strict subset** of the nebius OpenHands trajectory tool set the sibling researcher documented (execute_bash / str_replace_editor / think / task_tracker / finish, OpenHands v0.54.0): **SWE-Hero has no `task_tracker`**. Mixing the two corpora in one SFT blend therefore requires either dropping `task_tracker` turns from the nebius data or accepting that the model sees a tool in some system prompts and not others.
- Because every row ends in exactly one `finish` call and has exactly one user turn, SWE-Hero rows are directly usable as single-task multi-turn SFT sequences with no reformatting beyond the chat template.
- The absence of a `resolved` column makes SWE-Hero unusable for reward-weighted or rejection-sampled SFT; you get take-it-or-leave-it supervision.

### Gaps
- Exact OpenHands version for SWE-Hero / SWE-Zero: not stated on either card; the arXiv abstract page does not give it and I could not retrieve the full paper body (WebFetch returned only the abstract for both `/abs/2604.01496` and `/abs/2604.01496v1`). **Unverified.**
- Whether SWE-Hero rows were filtered by test execution (and with which tests) is only implied by the paper title/abstract, never asserted on the card. **Unverified.**
- SWE-HERO-32B / SWE-ZERO-32B checkpoints: the paper names them, but I found no NVIDIA-published weights on HF. They may exist elsewhere (NGC) — not checked.

---

## Q2. Which upstream task collections SWE-Hero derives from, and overlap with nebius/SWE-rebench{,-V2}

### Takeaway
**Computed from the pinned parquet: 53.1% of SWE-Hero trajectories (6,261 of 11,766 issues) come straight from `nebius/SWE-rebench`, and every one of those `instance_id`s matches a SWE-rebench row exactly — so for a team that already has nebius/SWE-rebench, more than half of SWE-Hero is re-trajectoried, not new, issues.** The genuinely additive half is R2E-Gym-Subset + SWE-Gym, which however covers only **19 repositories** between them. Overlap with `nebius/SWE-rebench-V2` is near-zero (215 issues, 1.8%).

### Cited Findings

**Declared sources** — card: "The issue statements are gathered from [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym), [R2E-Gym-Subset](https://huggingface.co/datasets/R2E-Gym/R2E-Gym-Subset), [SWE-rebench](https://huggingface.co/datasets/nebius/SWE-rebench)." **SWE-smith is not a source.** — [dataset card](https://huggingface.co/datasets/nvidia/SWE-Hero-openhands-trajectories)

**Computed per-source breakdown** (DuckDB over `hf://datasets/nvidia/SWE-Hero-openhands-trajectories@150bc119e52c647216fce285fd801f16b6fd745b/data/*.parquet`, 2026-10-29; `GROUP BY dataset`):

| `dataset` value | trajectories | % of 34,269 | distinct `instance_id` | distinct `repo` | traj/issue |
|---|---:|---:|---:|---:|---:|
| `nebius/SWE-rebench` | 18,189 | 53.08% | 6,261 | **1,688** | 2.91 |
| `R2E-Gym/R2E-Gym-Subset` | 10,221 | 29.83% | 3,442 | **8** | 2.97 |
| `SWE-Gym/SWE-Gym-Raw` | 3,990 | 11.64% | 1,397 | **10** | 2.86 |
| `SWE-Gym/SWE-Gym` | 1,869 | 5.45% | 666 | **1** | 2.81 |
| **total** | **34,269** | 100% | **11,766** | **1,695** | 2.91 |

(The dataset-viewer `/statistics` endpoint, on a 22,500-row partial sample, gives proportionally similar frequencies: R2E-Gym 10,221, nebius/SWE-rebench 6,420, SWE-Gym-Raw 3,990, SWE-Gym 1,869 — note that endpoint's sample is not the full set, so prefer the computed table.) — [datasets-server /statistics](https://datasets-server.huggingface.co/statistics?dataset=nvidia%2FSWE-Hero-openhands-trajectories&config=default&split=train)

**Computed overlap with the nebius family** (same session, 2026-10-29):
- Reference sizes I measured myself over `hf://datasets/nebius/SWE-rebench/data/*.parquet`: **27,878 rows, 21,336 distinct `instance_id`, 3,468 distinct repos.** The sibling researcher's figure of 21,336 rows matches my *distinct instance_id* count, not my row count — the published parquet glob contains 27,878 physical rows, i.e. ~6.5k duplicate `instance_id`s (likely multiple config/split copies). **Flag this discrepancy to the writer.**
- `hf://datasets/nebius/SWE-rebench-V2/data/*.parquet`: **32,079 rows, 32,079 distinct `instance_id` (no duplicates), 3,617 distinct repos** — consistent with the sibling's 32,079.
- **SWE-Hero ∩ nebius/SWE-rebench on `instance_id`: 6,261 distinct issues = 53.2% of SWE-Hero's 11,766 issues**, and **100% of the 6,261 rows SWE-Hero itself labels `nebius/SWE-rebench`** (so the provenance label is exact, not approximate). Repo-level: **1,689 of SWE-Hero's 1,695 repos** are also in SWE-rebench.
- **SWE-Hero ∩ nebius/SWE-rebench-V2 on `instance_id`: only 215 distinct issues (1.83%)** — and none of those come from SWE-Hero's SWE-rebench slice; they are 156 from `SWE-Gym/SWE-Gym-Raw` and 59 from `SWE-Gym/SWE-Gym`. Repo-level overlap with V2: 243 of 1,695 repos.

**Related NVIDIA sets and their sources:**
- `nvidia/Open-SWE-Traces` sources are **exclusively `AweAI-Team/Scale-SWE` and `nebius/SWE-rebench-V2`** — "All underlying issue statements and repository environments are sourced exclusively from permissively licensed datasets: Scale-SWE, SWE-rebench-V2" — [Open-SWE-Traces card](https://huggingface.co/datasets/nvidia/Open-SWE-Traces). Its `instance_id` is documented as "(from nebius/SWE-rebench-V2)".
- `nvidia/Nemotron-SFT-SWE-v2`'s agentless subset draws on "SWE-Bench-Train / SWE-reBench / **SWE-Smith** … SWE-Fixer-Train" — the only NVIDIA set I found that uses SWE-smith — [Nemotron-SFT-SWE-v2 card](https://huggingface.co/datasets/nvidia/Nemotron-SFT-SWE-v2)

### Inferences
- **For a team that already holds nebius/SWE-rebench, SWE-Hero adds ~5,505 genuinely new issues (11,766 − 6,261) but only ~19 new repositories** (R2E-Gym 8 + SWE-Gym-Raw 10 + SWE-Gym 1), because the entire repo diversity of SWE-Hero comes from its SWE-rebench slice. SWE-Hero's value proposition is therefore **trajectories on known issues**, not task diversity.
- Conversely, SWE-Hero is complementary to `nebius/SWE-rebench-openhands-trajectories`: same 6,261 issues, different teacher-model rollouts would be a near-pure teacher-diversity gain — but note both corpora use the *same* teacher (Qwen3-Coder-480B-A35B-Instruct) and the *same* OpenHands family, so the diversity gain is small. The main difference is the 4- vs 5-tool schema.
- The ~1.8% V2 overlap means `nvidia/Open-SWE-Traces` (sourced from V2 + Scale-SWE) is **largely issue-disjoint from SWE-Hero** and is the better axis of expansion.
- R2E-Gym-Subset contributes 3,442 issues across **8 repos** — extremely repo-concentrated, and its issue statements are LLM-synthesised rather than real GitHub issues. Expect distribution shift relative to real repository-repair work.

### Gaps
- I did not compute overlap against `AweAI-Team/Scale-SWE` or `SWE-bench_Verified` (decontamination check). A team should run that before training — NVIDIA's cards make no decontamination claim for SWE-Hero.
- The 27,878 vs 21,336 row-count discrepancy for `nebius/SWE-rebench` is unresolved; I did not enumerate that repo's configs to find the cause.

---

## Q3. NVIDIA Nemotron code / code-reasoning SFT datasets (2025–2026): which are, and are NOT, repository-repair trajectories

### Takeaway
NVIDIA ships a **large** amount of genuine multi-turn repository-repair tool trajectory data — `Open-SWE-Traces` (1.14M rows / 98 GB) is by far the biggest public one, plus `SWE-Zero` (318k), `Nemotron-SFT-SWE-v3` (238k), `SWE-Hero` (34k), `Nemotron-SWE-v1` (51k JSONL), `Nemotron-SFT-SWE-v2` (46k agentic + 210k agentless). The `OpenCode*` and `Nemotron-*Competitive-Programming*` families and `Llama-Nemotron-Post-Training-Dataset` are **NOT** repository-repair data.

### Cited Findings — genuine repository-repair trajectory data

**`nvidia/Open-SWE-Traces`** — the flagship. [HF API](https://huggingface.co/api/datasets/nvidia/Open-SWE-Traces?blobs=true), [/size](https://datasets-server.huggingface.co/size?dataset=nvidia/Open-SWE-Traces), [card](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) (observed 2026-10-28)
- SHA **`4fa4c2ae9afc6b397bc50391d43450c79993c138`**; created 2026-04-16T21:36:03Z, **lastModified 2026-10-28T18:30:09Z** (actively updated the day I looked); `gated: false`; 25,378 downloads, 158 likes; license **`cc-by-4.0`**.
- 487 files, **97,939,464,900 bytes (97.94 GB)**. `/size`: **1,138,945 rows**, 10 columns, memory 267,333,525,642 bytes.
- Four configs: `v2.0` (default) 489,109 rows / 37.11 GB; `v1.2` 235,391 / 30.44 GB; `v1.1` 263,226 / 17.39 GB; `v1.0` 151,219 / 13.00 GB. Each config has five splits by harness: `claudecode`, `opencode`, `openhands`, `sweagent`, `minisweagent` (v1.0/v1.1 have fewer).
- **Scaffolds (5):** OpenHands (v1.0 = **v0.53.0**), SWE-agent, mini-SWE-agent, OpenCode, Claude Code.
- **Teachers by version:** v1.0 Minimax-M2.5 (thinking) + Qwen3.5-122B (non-thinking); v1.1 DeepSeek-V4-Flash-0731 (thinking) + Qwen3.6-27B; v1.2 Qwen3.8-27B (xhigh thinking); v2.0 **Qwen3.8-Flash-Next** at xhigh / medium / low reasoning effort. Card also names GLM among families used.
- **10 columns incl. `resolved` (int): "1 if the agent solved the issue, 0 otherwise. (-1 if the information is unavailable)"**, plus `language`, `tools` (list of JSON tool definitions **per row** — so the tool schema is self-describing per harness), and `metadata` containing `category` (bug-fix / enhancement / feature-request / other), **`reference_patch` {patch, num_modified_files, num_modified_lines}** and `model_patch` {patch, num_modified_files, num_modified_lines}.
- **Failed trajectories are included and labelled.** The distribution table gives explicit Resolved / Unresolved / Unknown counts per agent × model, e.g. v2.0 OpenHands/Qwen3.8-Flash-Next: Resolved 12,810 vs Unresolved 13,217 across categories; v1.0 OpenHands/Minimax-M2.5: Resolved 14,363, Unresolved 19,510, Unknown 9,730 — [data_distribution.md](https://huggingface.co/datasets/nvidia/Open-SWE-Traces/raw/main/data_distribution.md)
- **Python share** (trajectories / PRs, from data_distribution.md): v1.0 34,343 Python traj of 151,219 (22.7%); v1.1 **162,411 of 263,226 (61.7%)**; v1.2 140,709 of 235,396 (59.8%); v2.0 97,383 of 168,824 (57.7%). Non-Python: Go, TypeScript, JavaScript, Rust, Java, PHP, C, C++.
- Note: data_distribution.md gives v1.2 = 235,396 and v2.0 = 168,824 trajectories, but `/size` reports v1.2 = 235,391 rows and v2.0 = 489,109 rows. The v2.0 mismatch is because the v2.0 *config* globs in reasoning-effort subdirectories (`thinking-low`, `thinking-medium`) in addition to the xhigh set documented in the table. **Flag: card table ≠ viewer row count for v2.0.**
- Published at EMNLP 2026 Findings: "OPEN-SWE-TRACES: Advancing Dual-Mode Multilingual Distillation for Software Engineering Agents", Ahmad, Ludwig, Majumdar, Ginsburg, pp. 2668–2679 — [ACL Anthology](https://aclanthology.org/2026.findings-emnlp.131/)

**`nvidia/Nemotron-SFT-SWE-v3`** — [card](https://huggingface.co/datasets/nvidia/Nemotron-SFT-SWE-v3), [/size](https://datasets-server.huggingface.co/size?dataset=nvidia/Nemotron-SFT-SWE-v3)
- SHA **`3f73de64c1fe928a8f538fe45ccc10c228cc4c6a`**; lastModified 2026-06-06T00:24:01Z; 98 files, **11.678 GB**; `/size` **237,970 rows**, 3 columns, 11.68 GB parquet. Tagged `Nemotron_3_Ultra`.
- License frontmatter: **`[cc-by-4.0, apache-2.0, mit, bsd-3-clause, bsd-2-clause]`**; prose: "licensed under Creative Commons Attribution 4.0 International (CC-BY 4.0). Additional Information: Apache 2.0 License; MIT License; BSD-3 License; BSD-2 License."
- "agentic trajectories collected using a variety of agent harnesses, including the OpenHands, SWE-agent, and mini-SWE-agent frameworks"; "ready for commercial use". Columns: `messages` (with `role`, `content`, **`reasoning_content`**, `tool_calls`), `uuid`, `license`. Sampled first row's system prompt begins "You are OpenHands agent, a helpful AI assistant that can interact with a computer to solve tasks." — **confirmed OpenHands-format multi-turn repo-repair data, pre-blended, with reasoning traces.** Carries **no `resolved` label and no reference patch.**

**`nvidia/Nemotron-SWE-v1`** — [card](https://huggingface.co/datasets/nvidia/Nemotron-SWE-v1)
- SHA **`0fe17a965b297a9c943a59050a14c42d5f0083ce`**; lastModified 2026-01-12T20:28:21Z; license `cc-by-4.0`. 3 files, **11.141 GB**, single `data/r2e_gym.jsonl` (11,141,242,062 B). `/size` reports 24,875 rows for the parquet conversion of split `r2e_gym` — but the **card claims 51,029 samples** ("r2e_gym 51,029 / Total 51,029", "~11 GB"); the card prose separately says "59k agent trajectories". **Three conflicting counts (24,875 viewer / 51,029 card table / 59k card prose).** Treat 51,029 as the publisher claim and the viewer's 24,875 as a likely-truncated parquet conversion.
- OpenHands framework, teacher Qwen3-Coder-480B-A35B-Instruct, sources SWE-Gym + R2E-Gym-Subset. License prose: "governed by CC BY 4.0, **except for certain subsets, which are governed by the BSD-3-Clause License as indicated in the Hugging Face Dataset Viewer**."

**`nvidia/Nemotron-SFT-SWE-v2`** — [card](https://huggingface.co/datasets/nvidia/Nemotron-SFT-SWE-v2)
- SHA **`bd151f3f2d89c4804dda0083d912bd9f6a0a9fb7`**; lastModified 2026-03-11T01:12:11Z. 5 files, **18.084 GB** (`data/swe.jsonl` 11,350,621,642 B; `data/agentless.jsonl` 6,733,030,079 B). Dataset-viewer `/size` returns **0 rows** (no parquet conversion for these JSONL files) — row counts are publisher claims only.
- Card claim: `openhands_swe` **46,278** samples (OpenHands agentic, Qwen3-Coder-480B-A35B-Instruct, SWE-Gym + R2E-Gym-Subset) and `agentless_swe` **209,976** samples; total 256,254, ~17 GB.
- **The agentless subset is NOT agentic trajectory data:** "supervised fine-tuning data for agentless software engineering sub-tasks … code localization, code repair, and test generation. Each example is formatted with task-specific outputs such as a ranked file list for localization, patch edits for repair, and reproduction plus unit tests for test generation." Teacher: **DeepSeek-R1-0528**, 8 responses per prompt for SWE-Bench-Train / SWE-reBench / SWE-Smith and 4 for SWE-Fixer-Train.
- License frontmatter: `[cc-by-4.0, apache-2.0, mit, bsd-3-clause, bsd-2-clause]`.

**`nvidia/Nemotron-SFT-SWE-v3.5`** — [card](https://huggingface.co/datasets/nvidia/Nemotron-SFT-SWE-v3.5)
- SHA **`ad64129216649f86179a759a6df65d0975c5df07`**; lastModified 2026-08-28T16:41:09Z; license `cc-by-4.0`; tagged `Nemotron_Lightning_v3.5`. 12 files, **0.269 GB** on disk (`data/train-{00000..00009}-of-00010.jsonl.gz`); `/size` **5,115 rows**, 1.18 GB parquet; card says "5,115 records, 3 features, 1.9 GiB".
- **OpenCode harness** (not OpenHands). "The seed tasks model real-world coding applications requiring changes across multiple files and artifacts, including source code, tests, documentation, and configuration." Labeling Method: "Manually Labeled". **"This dataset is for commercial uses only."** — an unusual phrasing worth legal review (it appears to *restrict to* commercial use, the inverse of the usual NVIDIA wording).

**`nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1`** — [card](https://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1)
- SHA **`d2b67746ca0087e73c4675b56bcc139b99354963`**; lastModified 2026-09-29T05:43:48Z; license `cc-by-4.0`; tagged `nemo-gym`. 3 files, **5.102 GB** (`train.jsonl` 5,101,895,830 B). `/size`: **50,308 rows**, 11 columns, 5.02 GB. Card claims "Train Samples - 6436, 2 top-level features: `responses_create_params`, `agent_ref`, Train ~4.25GB" — **card claim (6,436) conflicts with the viewer (50,308 rows, 11 cols)**.
- **This is RL task/environment data, not SFT trajectories:** "provides GitHub issues for training and validating real-world software engineering agents using the OpenHands environment in NeMo Gym … a refactored version of the SWE-Gym and R2E-Gym datasets to support the NeMo Gym input format." Labeling Method: "Not Applicable".

### Cited Findings — NVIDIA code sets that are **NOT** repository-repair data

- **`nvidia/OpenCodeReasoning`** — SHA `20a1ca19c0d050fe9057fc08339d6b370ec1c67a`, lastModified 2025-05-04; license `cc-by-4.0`; splits `split_0` **567,850** + `split_1` **167,405**. **Single-turn competitive-programming reasoning** (features `id, input, output, source, license, dataset, split, difficulty, solution`). **NOT repo repair.** — [HF API](https://huggingface.co/api/datasets/nvidia/OpenCodeReasoning)
- **`nvidia/OpenCodeReasoning-2`** — SHA `eadf535931451525f3e5621d0f960c240bc62fd9`, lastModified 2025-05-17; `cc-by-4.0`; `train` splits `python` **1,398,166** + `cpp` **1,174,475**. Single-turn competitive programming. **NOT repo repair.**
- **`nvidia/OpenCodeInstruct`** — SHA `8f3ba5bafe4d6e8db46082cf7ae6741bc370604d`, lastModified 2025-04-28; `cc-by-4.0`; **5,000,000** train rows. Single-turn code instruct. **NOT repo repair.**
- **`nvidia/Nemotron-Competitive-Programming-v1`** (SHA `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8`, 2025-12-15, `cc-by-4.0`) and **`nvidia/Nemotron-SFT-Competitive-Programming-v2`** (SHA `778afc98a9e027e10b3cd78020c120e93e142ef2`, 2026-03-11, license `[cc-by-4.0, odc-by, mit]`). **NOT repo repair.**
- **`nvidia/Llama-Nemotron-Post-Training-Dataset`** — SHA `ab2a40d258a6a4d9d4c277d702aeea445081766c`, lastModified 2025-05-08, Data Version 1.1 (2025-04-08); `cc-by-4.0`; config `SFT` **1,073,011 rows / 6.83 GB**; splits `code` **104,597**, `math` 276,536, `science` 620,660, `chat` 39,792, `safety` 31,426. The `code` split is single-turn reasoning-style code SFT, **not** repository-repair tool trajectories. **NOT repo repair.** — [/size](https://datasets-server.huggingface.co/size?dataset=nvidia/Llama-Nemotron-Post-Training-Dataset)
- **`nvidia/Nemotron-Post-Training-Dataset-v2`** — SHA `5c89e01dd720ae0f4058445ed49c5fb68a03c76e`, 2025-08-21, `cc-by-4.0`, **`gated: auto`** (requires accepting access on HF); splits `code` **175,000**, `math` 239,467, `stem` 355,000, `chat` 627,720, plus ~4.9M multilingual rows. **NOT repo repair.**
- **`nvidia/Nemotron-SFT-OpenCode-v1`** — SHA `556d5237acff203f3e1a0be49428634c3606cda2`, 2026-03-23, `cc-by-4.0` (prose: "GOVERNING TERMS: … CC BY 4.0"). Six subsets by tool configuration (`general` 90K, `bash_only_tool` 97K, `bash_only_tool_skills` 96K, `question_tool` 76K, `agent_skills` 67K, `agent_skills_question_tool` 33K; ≈459K total). Questions and agent skills synthesised by **GPT OSS 120B**; traces by Qwen3-Coder-480B-A35B-Instruct. This is **OpenCode-CLI tool-use / agent-skills data, not issue-driven repository repair** — "general questions that are commonly asked to Agentic CLI". Borderline-useful for tool-call formatting, **not** repo repair.
- **`nvidia/Nemotron-SFT-Agentic-v2`** — SHA `7c804833427f633ccd53b582dbf02525fd680f78`, 2026-08-10; license `[cc-by-4.0, apache-2.0, mit]`; 6 files, **21.861 GB**; `/size` 0 rows (JSONL, no parquet conversion). Card claims `tool_calling` 707,052, `customer_service_838_domains` 278,880, `search_graph_walk` 5,968; total 991,900, ~20 GB. Seeded from UltraTool, ToolEyes, AutoTools, API-Bank, glaive-function-calling-v2, Toucan-1.5M; simulated/judged with DeepSeek-V3.2 and GLM-4.6. **Generic function-calling and customer-service tool use. NOT repo repair.**
- **`nvidia/Nemotron-SFT-Agentic-v4`** — SHA `a4593a26ea83a700035bbe0ec1edc9ef3810669d`, lastModified 2026-10-15; 4 files, **18.882 GB**; `/size` 0 rows. Card claims `tool_calling` **549,707** + `knowledge_agent` **84,957** = 634,664 records / 18.88 GB; teachers **Qwen3.5-397B-A17B and GLM-5.2**. **License is `openmdw-1.1`, not CC-BY — see Q4.** **NOT repo repair.**
- **`nvidia/Nemotron-Agentic-v1`** — SHA `650d590978ca35c8f1ecea2faf136e5fac421b62`, 2025-12-15, `cc-by-4.0`. Predecessor of the above. **NOT repo repair.**
- **`nvidia/Nemotron-Terminal-Corpus`** (SHA `a1667c4ffdadea02a89bffe4f1bb7ca2ff19f8d9`, 2026-02-27, `cc-by-4.0`) and `nvidia/Nemotron-Terminal-Synthetic-Tasks` — terminal/CLI data, adjacent but **not** issue-driven repository repair.

### Inferences
- The practical ranking for a Python repository-repair agent is: **(1) `Open-SWE-Traces`** (largest, labelled `resolved`, five harnesses, ships gold patches, ~58–62% Python in v1.1–v2.0), **(2) `Nemotron-SFT-SWE-v3`** (238k pre-blended OpenHands/SWE-agent/mini-SWE-agent rows with `reasoning_content`, smallest integration cost), **(3) `SWE-Zero`** (318k, but execution-free so quality is unverified), **(4) `SWE-Hero`** (34k, small but the paper's "execution-backed" stage).
- `Nemotron-SFT-SWE-v3` and `SWE-Zero`/`SWE-Hero` almost certainly overlap heavily with each other and with `Open-SWE-Traces` (the SWE-Pivot / Nemotron blends are internal re-mixes of the same R2E-Gym / SWE-Gym / SWE-rebench pools). Treat the sum of row counts as an **upper bound**, not an achievable total.
- `Nemotron-SFT-SWE-v2`'s **agentless** 209,976 samples are the one genuinely different supervision signal on offer: single-shot localisation, repair and test-generation targets, usable for a localiser or a test-writer sub-model rather than the agent policy.

### Gaps
- Row counts for `Nemotron-SFT-SWE-v2`, `Nemotron-SFT-Agentic-v2`, `Nemotron-SFT-Agentic-v4` and `Nemotron-SFT-OpenCode-v1` could not be independently verified — the dataset-viewer returns 0 rows for all four because they ship raw `.jsonl` with no parquet conversion. **All their counts here are publisher claims.**
- I did not compute cross-dataset `instance_id` overlap among the NVIDIA sets themselves (SWE-Hero vs Nemotron-SFT-SWE-v3 vs Open-SWE-Traces). `Nemotron-SFT-SWE-v3` exposes only `messages`/`uuid`/`license` — **it has no `instance_id`, so instance-level dedup against it is impossible without patch/prompt hashing.** This is a real integration risk.

---

## Q4. Licensing — exact card licenses, restrictive clauses, and the underlying repo-code question

### Takeaway
Nearly everything relevant is **CC-BY-4.0** with no field-of-use restriction, which is unusually permissive for this corpus class. The two things to flag are **`nvidia/Nemotron-SFT-Agentic-v4` (OpenMDW-1.1, not CC-BY)** and **`nvidia/Llama-Nemotron-Post-Training-Dataset`, which propagates Llama Community License obligations onto any model you train on it**. Separately, **no NVIDIA card license settles the rights in the repository source code embedded in the trajectories.**

### Cited Findings

| Dataset | Card license (frontmatter) | Notable prose |
|---|---|---|
| `nvidia/SWE-Hero-openhands-trajectories` | `cc-by-4.0` | "governed by the Creative Commons Attribution 4.0 International License (CC BY 4.0). Additional Information: MIT License, Apache 2.0 License, BSD 2 Clause License, and BSD 3 Clause License." / "ready for commercial/non-commercial use" |
| `nvidia/SWE-Zero-openhands-trajectories` | `cc-by-4.0` | same wording |
| `nvidia/Open-SWE-Traces` | `cc-by-4.0` | "Governing Terms: this dataset is governed by the Creative Commons Attribution 4.0 International License (CC BY 4.0). **Each user is responsible for checking the content of datasets and the applicable licenses and determining if suitable for the intended use.**" |
| `nvidia/Nemotron-SWE-v1` | `cc-by-4.0` | "governed by CC BY 4.0, **except for certain subsets, which are governed by the BSD-3-Clause License as indicated in the Hugging Face Dataset Viewer**" |
| `nvidia/Nemotron-SFT-SWE-v2` | `[cc-by-4.0, apache-2.0, mit, bsd-3-clause, bsd-2-clause]` | "licensed under CC-BY 4.0. Additional Information: Apache 2.0; MIT; BSD-3; BSD-2." |
| `nvidia/Nemotron-SFT-SWE-v3` | `[cc-by-4.0, apache-2.0, mit, bsd-3-clause, bsd-2-clause]` | same |
| `nvidia/Nemotron-SFT-SWE-v3.5` | `cc-by-4.0` | "**This dataset is for commercial uses only.**" |
| `nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1` | `cc-by-4.0` | "ready for commercial use" |
| `nvidia/Nemotron-SFT-OpenCode-v1` | `cc-by-4.0` | "GOVERNING TERMS: This dataset is governed by the CC BY 4.0" |
| `nvidia/Nemotron-SFT-Agentic-v2` | `[cc-by-4.0, apache-2.0, mit]` | "ready for commercial use" |
| **`nvidia/Nemotron-SFT-Agentic-v4`** | **`openmdw-1.1`** | **"Use of this dataset is governed by `OpenMDW-1.1`. Each user is responsible for checking the content of the dataset and the applicable licenses and determining if suitable for the intended use."** Also: "Persona grounding derived from Nemotron-Personas-USA … licensed under CC-BY-4.0." |
| `nvidia/OpenCodeReasoning`, `-2`, `OpenCodeInstruct`, `Nemotron-Competitive-Programming-v1` | `cc-by-4.0` | — |
| `nvidia/Nemotron-SFT-Competitive-Programming-v2` | `[cc-by-4.0, odc-by, mit]` | ODC-BY adds attribution/share-notice obligations on the database |
| `nvidia/Nemotron-Post-Training-Dataset-v2` | `cc-by-4.0`, **`gated: auto`** | access gate on HF |
| **`nvidia/Llama-Nemotron-Post-Training-Dataset`** | `cc-by-4.0` | see restrictive quote below |

**The restrictive clause to flag, quoted verbatim** — [Llama-Nemotron-Post-Training-Dataset README](https://huggingface.co/datasets/nvidia/Llama-Nemotron-Post-Training-Dataset/raw/main/README.md) (observed 2026-10-29):

> "The dataset contains information about license type on a per sample basis. The dataset is predominantly CC-BY-4.0, with a small subset of prompts from Wildchat having an ODC-BY license and a small subset of prompts from StackOverflow with CC-BY-SA license.
>
> This dataset contains synthetic data created using Llama-3.3-70B-Instruct, Llama-3.1-Nemotron-70B-Instruct and Llama-3.3-Nemotron-70B-Feedback/Edit/Select (ITS models). **If this dataset is used to create, train, fine tune, or otherwise improve an AI model, which is distributed or made available, such AI model may be subject to redistribution and use requirements in the Llama 3.1 Community License Agreement and Llama 3.3 Community License Agreement.**"

This is the only clause I found across NVIDIA's code/SWE datasets that **imposes conditions on models trained on the data**. It also contains CC-BY-SA samples (copyleft-style share-alike on those prompts) — a per-sample filter on the `license` column is advisable.

**`nvidia/Nemotron-SFT-SWE-v3.5`'s "This dataset is for commercial uses only."** — [card](https://huggingface.co/datasets/nvidia/Nemotron-SFT-SWE-v3.5). Every other NVIDIA SWE card says "ready for commercial/non-commercial use" or "ready for commercial use". Taken literally this *excludes* non-commercial/academic use, the opposite of a typical restriction. It is most likely a drafting error, but it is the published text.

**Observed `license` column distribution inside SWE-Hero** (dataset-viewer `/statistics`, **22,500-row partial sample**, not the full 34,269): BSD-3-Clause 10,666; Apache-2.0 6,179; MIT 5,320; BSD-2-Clause 333; MIT-0 2 — [datasets-server /statistics](https://datasets-server.huggingface.co/statistics?dataset=nvidia%2FSWE-Hero-openhands-trajectories&config=default&split=train)

### Inferences
- **The CC-BY-4.0 card license does not settle the rights in the repository source code that the trajectories quote and diff.** Each row's `trajectory` embeds verbatim file contents from the upstream GitHub repository, and each row's `license` column names that repo's own SPDX license (BSD-3-Clause, Apache-2.0, MIT, BSD-2-Clause, MIT-0). NVIDIA itself disclaims this on `Open-SWE-Traces` and `Nemotron-SFT-Agentic-v4` ("Each user is responsible for checking the content of datasets and the applicable licenses"). Practically: NVIDIA's CC-BY grant covers NVIDIA's own contribution (the synthesised agent behaviour), while Apache-2.0 attribution/NOTICE obligations and BSD attribution obligations continue to attach to the embedded code. **A team should retain the per-row `license` column through its training pipeline so it can produce attribution and, if needed, exclude license classes.** Note NVIDIA restricted collection to MIT / Apache-2.0 / BSD-2 / BSD-3 precisely to keep this tractable — no GPL/AGPL/LGPL/SSPL repos.
- `openmdw-1.1` on `Nemotron-SFT-Agentic-v4` is a different legal regime from CC-BY (the Linux Foundation's Open Model, Data and Weights licence family). Since that dataset is not repo-repair data, the simplest mitigation is to exclude it from a repository-repair blend entirely.
- No competition-use restriction appears on any of these cards. No SWE-bench-specific "evaluation only" clause appears either.

### Gaps
- I did not retrieve and read the OpenMDW-1.1 licence text itself, so I cannot quote its restrictive clauses — only that it governs `Nemotron-SFT-Agentic-v4`. **Unverified.**
- `nvidia/Nemotron-Post-Training-Dataset-v2`'s README has no `## License/Terms of Use` prose section reachable by grep; I only have the `cc-by-4.0` frontmatter plus the `gated: auto` flag. Its gate terms were not read.

---

## Q5. Do these ship gold/reference patches and verification tests (evaluator-only material)?

### Takeaway
**`nvidia/Open-SWE-Traces` is the only NVIDIA SWE set that ships the gold patch** (in `metadata.reference_patch.patch`). **None of them ship verification tests** — no `FAIL_TO_PASS` / `PASS_TO_PASS` / `test_patch` fields anywhere. For tests you must go back to the upstream task collection.

### Cited Findings
- `nvidia/Open-SWE-Traces` columns include `metadata.reference_patch` = "Reference ground-truth patch details: *`patch`* (`string`): The gold patch in unified diff format", `num_modified_files`, `num_modified_lines` — alongside `metadata.model_patch` and `resolved` — [Open-SWE-Traces card](https://huggingface.co/datasets/nvidia/Open-SWE-Traces)
- `nvidia/SWE-Hero-openhands-trajectories` and `nvidia/SWE-Zero-openhands-trajectories` have **7 columns only** (`instance_id, repo, license, trajectory_id, trajectory, model_patch, dataset`): **`model_patch` is the agent's patch, not the gold patch.** No reference patch, no tests, no `resolved`. (verified against the parquet schema, computed 2026-10-29) — [SWE-Hero card](https://huggingface.co/datasets/nvidia/SWE-Hero-openhands-trajectories)
- `nvidia/Nemotron-SFT-SWE-v3` has **3 columns** (`messages`, `uuid`, `license`) — no patches of any kind, no tests, no instance id (dataset-viewer `/first-rows`, observed 2026-10-29).
- `nvidia/Nemotron-SFT-SWE-v3.5`: 3 features (card), no patch/test fields described.
- By contrast, the upstream `nebius/SWE-rebench-V2` **does** carry evaluator material: its columns are `base_commit, created_at, image_name, instance_id, interface, language, license, patch, pr_description, problem_statement, repo, test_patch, FAIL_TO_PASS, PASS_TO_PASS, install_config, meta` — [datasets-server /first-rows](https://datasets-server.huggingface.co/first-rows?dataset=nebius%2FSWE-rebench-V2&config=default&split=train) (observed 2026-10-28)
- `nvidia/Nemotron-SFT-SWE-v2`'s **agentless** subset is the exception in the other direction: its test-generation examples contain "reproduction plus unit tests" as *training targets* (model-generated, DeepSeek-R1-0528), **not** verified gold tests — [card](https://huggingface.co/datasets/nvidia/Nemotron-SFT-SWE-v2)

### Inferences
- To build a verifier or run RL on SWE-Hero tasks you must **re-join on `instance_id` against the upstream collection** (`nebius/SWE-rebench` for 53% of issues; `R2E-Gym/R2E-Gym-Subset`, `SWE-Gym/SWE-Gym`, `SWE-Gym/SWE-Gym-Raw` for the rest) to recover `test_patch` / `FAIL_TO_PASS` / `PASS_TO_PASS`. My computed overlap confirms this join is clean for the SWE-rebench slice (6,261/6,261 exact `instance_id` matches).
- `nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1` is the NVIDIA-native route to executable task specs, but it's a NeMo Gym input format (`responses_create_params`, `agent_ref`) rather than SWE-bench-style fields.

### Gaps
- I did not verify whether `Nemotron-RL-Agentic-SWE-Pivot-v1`'s 11 viewer-reported columns include test specifications; the card describes only 2 top-level features. **Unverified.**

---

## Q6. Are executable Docker environments published for SWE-Hero tasks?

### Takeaway
**No. NVIDIA publishes no Docker images for SWE-Hero (or SWE-Zero, or Open-SWE-Traces) tasks.** The environments come from the upstream task collections' own registries, and NVIDIA's own docs say so.

### Cited Findings
- The `nvidia/SWE-Hero-openhands-trajectories` repo contains **only** `.gitattributes`, `README.md`, `tools.json` and 14 parquet shards — no Dockerfile, no image manifest, no `image_name` column. Same for `SWE-Zero` (`.gitattributes`, `README.md`, `tools.json`, 64 parquets). `nvidia/Open-SWE-Traces` non-data files are only `.gitattributes`, `README.md`, `data_distribution.md`. (HF API `?blobs=true`, observed 2026-10-28)
- Neither card mentions Docker, a registry, image tags or image sizes.
- NVIDIA's own Nemotron SWE-RL documentation states the SWE environment images are "available as standard Docker images from **R2E-Gym, SWE-Gym, and SWE-Bench Verified on HuggingFace**", with no NVIDIA-published image names or tags for them. Its own NVIDIA-published images are the training runtime, not task environments: base `nvcr.io/nvidia/nemo-rl:v0.5.0.nemotron_3_super`, with a user-built SWE variant shown as the placeholder `your-registry/nemo-rl:v0.5.0.nemotron_3_super_swe` (the `_swe` suffix marks a pre-fetched-venv build). It recommends Apptainer `.sif` images with a writable tmpfs overlay on SLURM, or Docker/Podman. It notes the OpenHands loop runs "up to 200 turns" and that OpenCode and Codex agent classes inside OpenHands mimic Claude Code / Codex CLI tool formats. **No image sizes are stated.** — [NVIDIA Nemotron docs, SWE-RL (Stages 2.1–2.2)](https://docs.nvidia.com/nemotron/latest/nemotron/super3/rl/swe.html) (observed 2026-10-28)
- The upstream `nebius/SWE-rebench-V2` *does* carry an `image_name` column per instance, so the 53%-of-SWE-Hero SWE-rebench slice has a documented upstream image per task — [datasets-server /first-rows](https://datasets-server.huggingface.co/first-rows?dataset=nebius%2FSWE-rebench-V2&config=default&split=train)
- A web search for an NVIDIA blog post on SWE-Hero returned nothing; I found **no NVIDIA technical blog post about SWE-Hero or SWE-Zero**. The only NVIDIA-domain hit was the Nemotron SWE-RL docs above.

### Inferences
- Reproducing or verifying SWE-Hero rollouts requires standing up environments yourself from three different upstream registries (SWE-rebench's `image_name`, R2E-Gym's, SWE-Gym's) — and NVIDIA's docs independently flag the operational weight of that path (Apptainer conversion, tmpfs overlays, memory watchdogs, a regex blocklist for `killall`/`pkill`).
- **The "200 turns" ceiling in NVIDIA's RL docs is consistent with the observed SWE-Hero trajectory length cap (max 201 messages).** Likely the same harness configuration.

### Gaps
- Image tag patterns and sizes for SWE-Hero's R2E-Gym and SWE-Gym slices were not looked up (they live on the upstream dataset repos, outside my scope). **Unverified.**
- I did not search NGC's catalog directly for an NVIDIA-published SWE task-environment image. **Unverified** — but the Nemotron docs pointing at HF upstream images is strong negative evidence.

---

## Q7. Realistic achievable totals: distinct issues, distinct repositories, supervised assistant tokens

### Takeaway
SWE-Hero alone is small: **11,766 issues / 1,695 repos / ~0.39–0.45B assistant tokens.** The realistic NVIDIA ceiling for a repository-repair blend is dominated by `Open-SWE-Traces`: ~**1.14M trajectories** and, after Python filtering and dedup, something on the order of **50–60k distinct Python issues** and **tens of billions of assistant tokens** — far more than any team would actually train on.

### Cited Findings

**SWE-Hero, measured (computed 2026-10-29, DuckDB over sha 150bc119):**
- 34,269 trajectories; **11,766 distinct `instance_id`**; **1,695 distinct `repo`**.
- Shard `train-00000-of-00014.parquet` (2,500 rows = 7.3% of the dataset): mean 118.57 messages/trajectory; **mean assistant-side characters per trajectory = 45,445** (assistant `content` + `tool_calls[].function.name` + `tool_calls[].function.arguments`); mean all-role `content` characters = 139,615.
- Extrapolated to 34,269 rows: **≈1.56 × 10⁹ assistant characters → ≈0.39–0.47 billion supervised assistant tokens** (at 3.3–4.0 chars/token; code and unified diffs tokenise denser than prose, so the higher end is more likely). Full-sequence (all roles) ≈4.8 × 10⁹ characters ≈ **1.2–1.4 billion total context tokens**, consistent with the viewer's 8.49 GB `num_bytes_memory`.
  - **This is an extrapolation from one of 14 shards. Mark as an estimate.**

**Other NVIDIA sets, for the ceiling:**
| Dataset | rows | parquet bytes | in-memory bytes | source |
|---|---:|---:|---:|---|
| `Open-SWE-Traces` | **1,138,945** | 97.94 GB | **267.33 GB** | [/size](https://datasets-server.huggingface.co/size?dataset=nvidia/Open-SWE-Traces) |
| `SWE-Zero-openhands-trajectories` | **318,115** | 12.21 GB | 33.95 GB | [/size](https://datasets-server.huggingface.co/size?dataset=nvidia/SWE-Zero-openhands-trajectories) |
| `Nemotron-SFT-SWE-v3` | **237,970** | 11.68 GB | — | [/size](https://datasets-server.huggingface.co/size?dataset=nvidia/Nemotron-SFT-SWE-v3) |
| `SWE-Hero-openhands-trajectories` | **34,269** | 2.40 GB | 8.49 GB | [/size](https://datasets-server.huggingface.co/size?dataset=nvidia/SWE-Hero-openhands-trajectories) |
| `Nemotron-SWE-v1` | 51,029 (card) / 24,875 (viewer) | 11.14 GB JSONL | — | [card](https://huggingface.co/datasets/nvidia/Nemotron-SWE-v1) |
| `Nemotron-SFT-SWE-v2` | 256,254 (card claim) | 18.08 GB JSONL | — | [card](https://huggingface.co/datasets/nvidia/Nemotron-SFT-SWE-v2) |
| `Nemotron-SFT-SWE-v3.5` | 5,115 | 1.18 GB | — | [/size](https://datasets-server.huggingface.co/size?dataset=nvidia/Nemotron-SFT-SWE-v3.5) |

- SWE-Zero issue/repo counts: card claims **118,092 total issues**; a third-party mirror's viewer page reports 628 repo classes for `repo` ("repo stringclasses 628") — [Arsh9210 mirror](https://huggingface.co/datasets/Arsh9210/SWE-Zero-openhands-trajectories). **Treat 628 as unverified third-party.**
- Open-SWE-Traces Python PR counts from the card's distribution tables (PRs, not trajectories, and **not unique across agent/model columns** — the card explicitly warns "PR counts are non-unique across agent/model columns and cannot be summed horizontally"): the largest single Python PR column is v1.1 mini-SWE-agent/Qwen3.6-27B at **23,374 Python PRs**; v1.2 mini-SWE-agent 24,287; v2.0 OpenCode 20,872 — [data_distribution.md](https://huggingface.co/datasets/nvidia/Open-SWE-Traces/raw/main/data_distribution.md)

### Inferences
- **Realistic distinct-issue ceiling across all NVIDIA SWE releases, deduped: roughly 130k–170k issues**, driven by SWE-Zero's claimed 118,092 (which is a superset of SWE-Hero's 11,766) plus Open-SWE-Traces' SWE-rebench-V2 + Scale-SWE pool (near-disjoint from SWE-Hero at the instance level — 1.8% overlap measured). **Python-only, the figure is far smaller: on the order of 25k–35k distinct Python issues**, since Open-SWE-Traces' per-version Python PR columns top out around 20–24k and are heavily shared across versions.
- **Distinct repositories:** SWE-Hero 1,695 (measured). SWE-rebench-V2 contributes 3,617 (measured). A full NVIDIA blend would plausibly reach **4,000–6,000 distinct repos**, but this is unmeasured.
- **Supervised assistant tokens:** scaling SWE-Hero's measured 45,445 assistant chars/row by in-memory bytes per row (SWE-Hero 248 KB/row; SWE-Zero 107 KB/row, i.e. ~43%; Open-SWE-Traces 235 KB/row, ~95%) gives rough assistant-token estimates of **SWE-Zero ≈ 1.6–1.9 B**, **Open-SWE-Traces ≈ 12–15 B**, **Nemotron-SFT-SWE-v3 ≈ 1–1.5 B**. **All of these are my extrapolations from one SWE-Hero shard — mark as estimates, not publisher figures.** The practical point for the writer: the binding constraint is compute and issue diversity, not token volume.
- A pragmatic recipe: `Open-SWE-Traces` filtered to `language='Python'` AND `resolved=1` as the backbone (it is the only set where that filter is possible), plus all 34,269 SWE-Hero rows as a small execution-backed top-up, plus `Nemotron-SFT-SWE-v2`'s agentless subset for a separate localiser/test-writer. Skip SWE-Zero unless you need volume at unverified quality.

### Gaps
- I did not compute Open-SWE-Traces' distinct `instance_id` / `repo` counts or its `resolved=1` ∧ `language='Python'` row count directly — at 98 GB with `instance_id`/`language`/`resolved` scattered across 487 files in four configs, the column-projected scan exceeded my time budget. **The single most valuable follow-up query** is: `SELECT language, resolved, count(*), count(DISTINCT instance_id) FROM read_parquet('hf://datasets/nvidia/Open-SWE-Traces/data/**/*.parquet') GROUP BY 1,2`.
- SWE-Zero's distinct `instance_id` and `repo` counts were not computed (12.2 GB, 64 shards); only the card's 118,092-issue claim is available.
- Exact tokenizer-based token counts were not produced; all token figures are character-count extrapolations.
