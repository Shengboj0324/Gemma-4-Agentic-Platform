# Nebius SWE-rebench dataset family as training data for a Python repository-repair agent

**Observation window: all API/parquet reads below were executed 2026-10-28 local / 2026-10-29 UTC** (HF HTTP response header `Date: Thu, 29 Oct 2026 06:50:20 GMT`). Facts labelled **[verified]** were computed by me directly from the HuggingFace datasets HTTP API, the HF dataset-viewer API, Docker Hub's v2 API, or by running DuckDB SQL over the pinned parquet revisions. Facts labelled **[publisher claim]** come from dataset cards, blog posts, or papers and were not independently reproduced.

---

## Q1. Exact dataset ids, revisions, row counts, file lists, declared licenses

### Takeaway
There are **seven** relevant `nebius/*` SWE datasets (not three). All seven declare `cc-by-4.0` on the card. The two trainable task corpora are `nebius/SWE-rebench` (21,336 rows, Python-only, pinned SHA `89cdfbab…`) and `nebius/SWE-rebench-V2` (32,079 rows, 20 languages, pinned SHA `10483de0…`); the trajectory corpus is `nebius/SWE-rebench-openhands-trajectories` (67,074 rows, 1.94 GiB single parquet, SHA `35455389…`). All row counts I report were reproduced from both the HF size API and the parquet files themselves.

### Cited Findings

**Full `nebius/*` dataset inventory — `GET https://huggingface.co/api/datasets?author=nebius&full=true` returned 13 datasets; 7 are SWE/agentic-coding, 6 are unrelated Infinity-Instruct distillation sets.** [verified, 2026-10-29] — [HF datasets API](https://huggingface.co/api/datasets?author=nebius&limit=200&full=true)

| Dataset id | main SHA (observed 2026-10-29) | lastModified | license (cardData) | downloads (30d) | likes |
|---|---|---|---|---|---|
| `nebius/SWE-rebench` | `89cdfbab4ab1bd8f5a658bb212d1b63624f4f881` | 2025-12-23T19:41:57Z | cc-by-4.0 | 54,810 | 77 |
| `nebius/SWE-rebench-V2` | `10483de0f50fe5da545942705a76c6150171af7f` | 2026-10-01T17:53:16Z | cc-by-4.0 | 95,880 | 72 |
| `nebius/SWE-rebench-openhands-trajectories` | `35455389ab51bf5e2306bfd436ef72d0f98bf882` | 2025-12-27T14:08:07Z | cc-by-4.0 | 10,566 | 151 |
| `nebius/SWE-rebench-V2-PRs` | `fbf0ecf50f268d5344149e2f0097db6bede83737` | 2026-08-18T12:22:32Z | cc-by-4.0 | 51,701 | — |
| `nebius/SWE-bench-extra` | `11dcbfb30e19552df2a2f8030bd764adc95c92a5` | 2025-05-28T16:27:57Z | cc-by-4.0 | 26,581 | — |
| `nebius/SWE-agent-trajectories` | `68195a1450865274106246d0d0296a1d6807b88e` | 2024-12-23T12:42:05Z | cc-by-4.0 | 14,679 | — |
| `nebius/SWE-rebench-leaderboard` | `34d5a58864acf91613740a09ec5d205228dcfa39` | 2026-07-28T09:59:05Z | cc-by-4.0 | 4,820 | — |

**Row counts per split/config (HF dataset-viewer `/size` endpoint, cross-checked against `count(*)` in parquet):** [verified, 2026-10-29] — [datasets-server size API](https://datasets-server.huggingface.co/size?dataset=nebius/SWE-rebench)

- `nebius/SWE-rebench`, config `default`: split `test` = **21,336** rows (211,279,395 parquet bytes); split `filtered` = **6,542** rows (33,886,640 bytes). Card `dataset_info` declares `test` num_bytes 738,277,003 / `filtered` 226,368,961 (uncompressed), download_size 245,166,035.
- `nebius/SWE-rebench-V2`, config `default`: split `train` = **32,079** rows (428,839,266 bytes). Card declares dataset_size 2,556,647,025 uncompressed.
- `nebius/SWE-rebench-openhands-trajectories`, config `default`: split `train` = **67,074** rows (2,079,503,354 bytes ≈ 1.94 GiB).
- `nebius/SWE-rebench-V2-PRs`, `train` = **126,300** rows (2,682,022,715 bytes; card declares 14,182,919,873 uncompressed).
- `nebius/SWE-bench-extra`, `train` = **6,376** rows (24,675,794 bytes). (Card prose says "6,415 Issue-Pull Request pairs" — **card prose and actual row count disagree by 39**.)
- `nebius/SWE-agent-trajectories`, `train` = **80,036** rows (1,114,367,701 bytes; 5,627,973,531 uncompressed).
- `nebius/SWE-rebench-leaderboard`: 16 configs/splits — `test` 860 rows plus monthly snapshots `2025_01` (109) … `2026_03` (110). Monthly rows 2025_01→2026_03: 109, 76, 62, 40, 40, 40, 30, 52, 50, 51, 47, 48, 48, 57, 110.

**File lists with exact LFS byte sizes (`?blobs=true` siblings):** [verified, 2026-10-29] — [HF API](https://huggingface.co/api/datasets/nebius/SWE-rebench?blobs=true)

- `nebius/SWE-rebench`: `.gitattributes` 2,461 B; `README.md` 9,190 B; `data/filtered-00000-of-00001.parquet` 33,886,640 B; `data/test-00000-of-00002.parquet` 101,556,119 B; `data/test-00001-of-00002.parquet` 109,723,276 B. **No LICENSE file.**
- `nebius/SWE-rebench-V2`: `.gitattributes` 2,520 B; `LICENSE` 17,509 B; `README.md` 6,629 B; `data/train-00000-of-00001.parquet` 428,839,266 B.
- `nebius/SWE-rebench-openhands-trajectories`: `.gitattributes` 2,461 B; `LICENSE` 18,656 B; `README.md` 6,924 B; `config.toml` 7,261 B; `tools.json` 18,512 B; `trajectories.parquet` 2,079,503,354 B.

**Declared license text, identical across all four main cards:** "The dataset is licensed under the Creative Commons Attribution 4.0 license. However, please respect the license of each specific repository on which a particular instance is based. To facilitate this, the license of each repository at the time of the commit is provided for every instance." — [SWE-rebench README](https://huggingface.co/datasets/nebius/SWE-rebench/raw/main/README.md); [SWE-rebench-V2 README](https://huggingface.co/datasets/nebius/SWE-rebench-V2/raw/main/README.md)

**`nebius/SWE-agent-trajectories` carries an extra licensing notice:** "if you intend to use the outputs of these models, you must comply with the [Llama 3.1 License]" (traces were generated partly with Llama3-70B-Instruct). [publisher claim, card text] — [SWE-agent-trajectories README](https://huggingface.co/datasets/nebius/SWE-agent-trajectories/raw/main/README.md)

### Inferences
- For a *Python repository-repair* agent the directly usable task corpora are `nebius/SWE-rebench` (21,336 Python tasks) and the `language='python'` slice of V2 (7,243 tasks); `SWE-bench-extra` is explicitly superseded ("This dataset has an improved and significantly larger successor: SWE-rebench").
- `SWE-rebench-V2-PRs` (126,300 rows) is *not* execution-validated task data in the same sense — the card describes it as raw PR material with LLM-generated problem statements; treat it as weak-supervision material, not verified tasks.

### Gaps
- `nebius/SWE-rebench-V2-PRs` and `nebius/SWE-bench-extra` `cardData.dataset_info` feature names were stripped by my grep filter; I have the documented field table from the card but did not dump the raw parquet schema for those two.

---

## Q2. Underlying repository code licenses — per-row license field, value distribution, redistribution rights

### Takeaway
Both task datasets **do** carry a per-row license field, and I computed the full distribution. V1 uses free-text `license_name` (56 distinct strings, messy, 2.49% null); V2 uses a cleaner SPDX-ish `license` (16 values, 1.09% null) but **15.7% of V2 rows are the non-license placeholder `custom-check-github`**. The CC-BY-4.0 card license covers Nebius's *compilation/annotations only* — the cards explicitly disclaim the underlying code rights.

### Cited Findings

**`nebius/SWE-rebench` `test` split (21,336 rows), `license_name` distribution — computed via DuckDB over the pinned parquet at rev `89cdfbab…`:** [verified, 2026-10-29]

| license_name | rows | % of 21,336 |
|---|---|---|
| MIT License | 8,864 | 41.54 |
| Apache License 2.0 | 4,970 | 23.29 |
| BSD 3-Clause "New" or "Revised" License | 3,718 | 17.43 |
| BSD | 806 | 3.78 |
| BSD 2-Clause "Simplified" License | 541 | 2.54 |
| **NULL (no license detected)** | **532** | **2.49** |
| BSD License | 482 | 2.26 |
| Zope Public License 2.1 | 176 | 0.82 |
| MIT-CMU License | 164 | 0.77 |
| BSD-2-Clause | 162 | 0.76 |
| New BSD License | 158 | 0.74 |
| BSD 3-Clause | 115 | 0.54 |
| BSD-3-Clause | 97 | 0.45 |
| BSD 3-Clause License | 87 | 0.41 |
| The Unlicense | 84 | 0.39 |
| ISC License | 68 | 0.32 |
| MIT/Apache-2.0 Dual License | 27 | 0.13 |
| Apache License 2.0 or MIT License | 25 | 0.12 |
| Creative Commons Zero v1.0 Universal | 24 | 0.11 |
| Modified BSD License | 21 | 0.10 |

Long tail (each ≤20 rows) includes: CC0 1.0 variants (20+4), BSD 4-Clause "Original"/"Old" (19), BSD-2-Clause-Patent (18), PSF License Agreement (9), **Academic Free License v3.0 (6) + Academic Free License 3.0 (2)**, Mozilla Public License 2.0 (2), PostgreSQL License (2), **"Do What The F*ck You Want To Public License" (2)**, Public Domain (1), plus many duplicate spellings of BSD/MIT. `count(distinct license_name) = 56`. **I observed zero GPL/AGPL/LGPL strings in the V1 `test` split** — notable and favourable for commercial use, though the 532 NULLs and the free-text "BSD"/"BSD License" buckets (1,288 rows combined) are unresolvable without re-checking upstream. [verified]

**`nebius/SWE-rebench-V2` (32,079 rows), `license` distribution — HF dataset-viewer `/statistics` endpoint, `string_label` with 16 unique values, nan_count 348 (1.085%):** [verified, 2026-10-29] — [datasets-server statistics](https://datasets-server.huggingface.co/statistics?dataset=nebius/SWE-rebench-V2&config=default&split=train)

Apache-2.0 10,407 · MIT 13,117 · **custom-check-github 5,038** · BSD-3-Clause 2,175 · BSD-2-Clause 357 · MIT-0 206 · ISC 206 · CC0-1.0 100 · **AGPL-3.0 54** · Unlicense 42 · NCSA 8 · BSL-1.0 7 · **GPL-3.0 5** · AFL-3.0 5 · PostgreSQL 3 · ECL-2.0 1 · NULL 348.

**V2 Python-only slice (7,243 rows), license distribution — DuckDB over pinned parquet:** [verified, 2026-10-29]
MIT 1,940 · Apache-2.0 1,854 · **custom-check-github 1,706 (23.6% of the Python slice)** · BSD-3-Clause 1,366 · MIT-0 166 · BSD-2-Clause 122 · NULL 36 · ISC 25 · Unlicense 22 · AFL-3.0 5 · NCSA 1. **No GPL/AGPL rows in the Python slice** — the 54 AGPL-3.0 and 5 GPL-3.0 V2 rows are all non-Python. [verified]

**Card statement on upstream rights (verbatim, both V1 and V2):** "However, please respect the license of each specific repository on which a particular instance is based. To facilitate this, the license of each repository at the time of the commit is provided for every instance." [publisher claim / card text] — [SWE-rebench README](https://huggingface.co/datasets/nebius/SWE-rebench/raw/main/README.md)

**V1 field documentation:** `license_name` is documented as "The type of license of the repository." V2 documents `license` as "SPDX license identifier of the repository." [publisher claim] — same READMEs.

### Inferences
- **The CC-BY-4.0 card license does NOT settle the underlying code's rights.** Nebius says so itself. CC-BY-4.0 plausibly covers the compilation, LLM-generated annotations (`meta.llm_metadata`, `interface`, `pr_description`), and the `install_config`; the `patch`, `test_patch`, and `problem_statement` fields are verbatim derivatives of upstream repository content and upstream issue text, which CC-BY-4.0 cannot relicense. A fine-tuning team needs its own position on whether training on permissively-licensed code is in scope.
- **Commercial / competition use:** CC-BY-4.0 itself permits commercial use with attribution and permits derivatives. For the *underlying code*: the V1 Python corpus appears to be ~100% permissive (MIT/Apache/BSD/ISC/CC0/Unlicense/PSF/AFL/Zope) with 2.49% unknown; V2's Python slice is permissive except 23.6% unresolved (`custom-check-github`) + 0.5% NULL. The 59 GPL/AGPL rows in V2 are non-Python and trivially excludable by `license IN ('GPL-3.0','AGPL-3.0')`.
- `custom-check-github` is a **placeholder meaning "we did not resolve this; go look at the repo"**, not a license. ~5,038 V2 rows (1,706 Python) are therefore *licence-unknown* for compliance purposes, in addition to the 348 NULLs.

### Gaps
- Neither card defines `custom-check-github`; I found no documentation of its semantics. My reading is inference from the name.
- V1's 532 NULL-license rows and 1,288 free-text "BSD"/"BSD License" rows cannot be mapped to SPDX from the dataset alone.
- Neither card addresses whether redistribution of the `patch`/`test_patch` diffs is itself licensed; no `LICENSE` file exists in the V1 repo at all (verified from the siblings list).

---

## Q3. Trajectory dataset: teacher model, scaffold, tool set, trajectories per issue, failed traces

### Takeaway
One teacher model (**Qwen3-Coder-480B-A35B-Instruct**) with **OpenHands v0.54.0**, native function calling, a **five-tool** set (`execute_bash`, `str_replace_editor`, `think`, `task_tracker`, `finish`), **67,074 trajectories over 6,306 distinct instances (mode ≈ 7–13 rollouts/issue, max 34)**, and **failed trajectories are included and explicitly labelled** via `resolved` (0/1) and `exit_status`. 34,913 of 67,074 rows (52.1%) are failures.

### Cited Findings

**Teacher model and scaffold (card):** "collected using [Qwen/Qwen3-Coder-480B-A35B-Instruct] with OpenHands (v0.54.0) agent scaffolding." Comparison table lists Scaffolding = "OpenHands (v0.54.0)", Bootstrapping Model = "Qwen3-Coder-480B-A35B-Instruct", "Uses function calling ✅". [publisher claim] — [trajectories README](https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories/raw/main/README.md)

**Sampling configuration, from the shipped `config.toml` (7,261 B) in the repo:** [verified, file read 2026-10-29] — [config.toml](https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories/raw/main/config.toml)
- `[llm]`: `model = "qwen3-coder-480b-a35b-instruct"`, `temperature = 0.7`, `top_p = 0.8`, `top_k = 20`, `timeout = 300`, `native_tool_calling = true`, `custom_llm_provider = "openai"`, `reasoning_effort = "low"`.
- `[llm.vllm_qwen3_coder_480B]`: comment states "repetition_penalty=1.05 was used by default by our deployed vllm inference engine, it can't be overriden on OpenHands side".
- `[agent]`: `enable_browsing = true`, `enable_editor = true`, `enable_cmd = true`, `enable_think = true`, `enable_finish = true`, `enable_jupyter = false`, `enable_llm_editor = false`, `enable_history_truncation = false`, `enable_condensation_request = false`.
- `[condenser] type = "noop"` (no history compression). `[core] runtime = "docker"`.
- Additional named LLM configs present for `Qwen/Qwen3-235B-A22B-Instruct-2507`, `zai-org/GLM-4.5`, `zai-org/GLM-4.5-Air`, and fine-tuned 30B/235B variants — **these were used for the blog's evaluation/RFT experiments, not stated to be trajectory producers.**

**Tool set and argument semantics, from the shipped `tools.json` (18,512 B) — exactly 5 tools:** [verified, parsed 2026-10-29] — [tools.json](https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories/raw/main/tools.json)

| tool | properties | required |
|---|---|---|
| `execute_bash` | `command`, `is_input`, `timeout` | `command` |
| `think` | `thought` | `thought` |
| `finish` | `message` | `message` |
| `task_tracker` | `command`, `task_list` | `command` |
| `str_replace_editor` | `command`, `file_text`, `insert_line`, `new_str`, `old_str`, `path`, `view_range` | `command`, `path` |

`execute_bash` description: "Execute a bash command in the terminal within a persistent shell session. … One command at a time". `str_replace_editor` description: "Custom editing tool for viewing, creating and editing files in plain-text format * State is persistent across command calls". `task_list` items require an object schema with `id`, `title`, `status` (enum), `notes`. [verified]

**Tool-call argument serialization:** `tool_calls[].function.arguments` is stored as a **JSON-encoded string**, not a struct — the card's own loader calls `json.loads(tool_call["function"]["arguments"])`. Confirmed by the parquet schema: `tool_calls STRUCT("function" STRUCT(arguments VARCHAR, "name" VARCHAR), id VARCHAR, "type" VARCHAR)[]`. There is also a per-row `tools` column embedding the full tool schema. [verified, DuckDB `DESCRIBE`]

**Actual parquet schema (9 columns), DuckDB `DESCRIBE` at rev `35455389…`:** `trajectory_id` VARCHAR, `instance_id` VARCHAR, `repo` VARCHAR, `trajectory` LIST<STRUCT(content, name, role, tool_call_id, tool_calls[])>, `tools` LIST<STRUCT(function STRUCT(description, name, parameters), type)>, `model_patch` VARCHAR, `exit_status` VARCHAR, `resolved` BIGINT, `gen_tests_correct` DOUBLE, `pred_passes_gen_tests` DOUBLE. [verified]
**Schema/card discrepancy:** the card documents the field as **`pred_passes_gen_test`** (singular) but the parquet column is **`pred_passes_gen_tests`** (plural), and the card omits the `tools` column entirely. [verified]

**Counts computed over all 67,074 rows:** [verified, 2026-10-29]
- 67,074 rows = 67,074 distinct `trajectory_id`; **6,306 distinct `instance_id`**; **1,823 distinct `repo`**; **1,445 distinct repository owners**.
- `resolved = 1`: **32,161 rows across 3,792 distinct instances**; `resolved = 0`: **34,913 rows across 4,255 distinct instances**. Exactly **3,792** instances have ≥1 resolved trajectory (so 2,514 instances have only failures).
- `exit_status` distribution: `submit` 60,739 · `RuntimeError: Agent reached maximum iteration. Current iteration: 100, max iteration: 100` 6,003 · `AgentStuckInLoopError: Agent got stuck in a loop` 252 · `Timeout: litellm.Timeout…` 36 · `RuntimeError: … ServiceUnavailableError` 29 · `unknown` 10 · `AttributeError: 'str' object has no attribute 'get'` 5.
- **Trajectories per issue** (issues at each count): 1→24, 2→18, 3→39, 4→77, 5→124, 6→321, 7→966, 8→602, 9→595, 10→580, 11→654, 12→650, 13→501, 14→403, 15→123, 16→90, 17→110, 18→66, 19→88, 20→97, 21→49, 22→34, 23→23, 24→21, 25→16, 26→6, 27→8, 28→8, 29→4, 30→4, 32→2, 33→2, 34→1. Mean ≈ 10.6, **max 34**.
- `gen_tests_correct` NULL in 35,621 rows (53.1%); `pred_passes_gen_tests` NULL in 35,685 rows (53.2%). Non-null means: `gen_tests_correct` ≈ 0.300, `pred_passes_gen_tests` ≈ 0.721.
- 56 rows have an empty/NULL `model_patch`.

**Max-iteration cap confirmed empirically:** the 6,003 `max iteration: 100` exit statuses independently confirm the card's "Turns Max Count 100". [verified]

**Failed-trajectory policy (blog):** "Only trajectories whose patches failed to apply were removed. Fine-tuning used only resolved trajectories." [publisher claim] — [Nebius blog: OpenHands trajectories with Qwen3-Coder-480B](https://nebius.com/blog/posts/openhands-trajectories-with-qwen3-coder-480b)

**Card's comparison table vs. peers (publisher claim):** Ours = 1,823 repositories, 3,792 resolved issues, 67,074 total trajectories, 32,161 successful, max 100 turns, **average 64.3 turns** (highest average in the table; SWE-smith-trajectories 30.2, SWE-Gym OpenHands 18.9, R2E-Gym 16.1, nebius/SWE-agent-trajectories 26.4). [publisher claim] — [trajectories README](https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories/raw/main/README.md)

**Reported downstream results (blog, RFT checkpoints, SWE-bench Verified 484-instance subset, max 500 turns):** 30B checkpoint 50.3% Pass@1 vs 50.0% for base Qwen3-Coder-30B-A3B-Instruct; 235B checkpoint 61.7% vs 66.5% for Qwen3-Coder-480B-A35B-Instruct (i.e. **the 235B student did not match the teacher, and the 30B gain was +0.3pp**). [publisher claim] — [Nebius blog](https://nebius.com/blog/posts/openhands-trajectories-with-qwen3-coder-480b)

### Inferences
- The trajectory set is **single-teacher**, unlike `nebius/SWE-agent-trajectories` (Qwen2.5-72B-Instruct + Llama3-70B-Instruct) — so no Llama-license contamination applies to the OpenHands set, and the card carries no such notice.
- `instance_id` joins to `nebius/SWE-rebench`; 6,306 of the trajectory instances vs 6,542 rows in the V1 `filtered` split (which is exactly the Docker-image-bearing subset) strongly suggests the rollouts were run over the `filtered` split, with ~236 instances dropped.
- For SFT on successful traces only, the realistic ceiling is **32,161 trajectories over 3,792 issues in 1,823 repos**. Dedup-to-one-per-issue would give 3,792 SFT examples.
- The `tools` column being per-row means you do **not** need `tools.json` to reconstruct prompts, but the two should be cross-checked if you re-render system prompts.

### Gaps
- I could not compute the real per-trajectory turn-count distribution (min/avg/max message counts): the query hit HF's anonymous rate limit (HTTP 429, "We had to rate limit your IP … pass a HF_TOKEN"). The card's "average 64.3 / max 100" therefore remains a **publisher claim**, though the max-100 figure is corroborated by the exit-status counts.
- The blog does not state the intended rollouts-per-issue target or how the number varied; the empirical distribution (mode 7, mean 10.6) implies adaptive sampling, but no source documents the policy.
- Neither the card nor the blog states the system prompt verbatim; it is only recoverable from the `trajectory` field's first `system` message (not extracted here).

---

## Q4. Contamination and overlap statements

### Takeaway
**V1's card says nothing at all about benchmark overlap** — this is a real gap for a training team. **V2's card carries an explicit warning** (quoted below) added in response to a third-party audit. The trajectory dataset's overlap statement lives only in the blog post, not on the card.

### Cited Findings

**`nebius/SWE-rebench-V2` card, exact warning text (verbatim):**
> "❗ **Benchmark overlap:** We excluded repositories from the original SWE-bench, but did not explicitly filter other benchmarks. Before training, check the [overlap analysis and task IDs](https://github.com/raimondasl/agentleak#case-3-swe-rebench-v2-vs-multilingual-swe-benchmarks) and exclude tasks that overlap with your evaluation benchmarks."

[publisher claim / exact card text, read 2026-10-29] — [SWE-rebench-V2 README](https://huggingface.co/datasets/nebius/SWE-rebench-V2/raw/main/README.md)

**`nebius/SWE-rebench` (V1) card: contains NO overlap or contamination warning.** I read the full raw README; it mentions SWE-bench only as methodological lineage ("builds upon and extends the methodology of SWE-bench") and never mentions SWE-bench-Verified, SWE-Gym, R2E-Gym, or SWE-smith overlap. [verified by reading the complete README at rev `89cdfbab…`] — [SWE-rebench README](https://huggingface.co/datasets/nebius/SWE-rebench/raw/main/README.md)

**`nebius/SWE-rebench-V2-PRs` card: NO overlap warning** (identical License/Citation sections to V2 but without the ❗ block). [verified] — [V2-PRs README](https://huggingface.co/datasets/nebius/SWE-rebench-V2-PRs/raw/main/README.md)

**`nebius/SWE-rebench-openhands-trajectories` card: NO overlap/contamination warning.** It names SWE-smith-trajectories, SWE-Gym/OpenHands-Sampled-Trajectories, and R2E-Gym/R2EGym-SFT-Trajectories **only in a comparison table**, with no statement about overlap with them. [verified] — [trajectories README](https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories/raw/main/README.md)

**Trajectory-set decontamination claim (blog only, not on the card):** the authors state they "explicitly excluded all SWE-bench Verified issues and repositories from our training data", also excluded the SWE-rebench September instances, and note they cannot determine whether base models saw SWE-bench Verified during pretraining. [publisher claim] — [Nebius blog](https://nebius.com/blog/posts/openhands-trajectories-with-qwen3-coder-480b)

**Third-party overlap audit referenced by Nebius's own card (`raimondasl/agentleak`, case 3), raw README read 2026-10-29:** [third-party claim, not independently reproduced]
- "348 of V2's 32,079 tasks (1.1%) match a benchmark task", matched by PR and base commit.
- Per benchmark (same PR + base commit): Multi-SWE-bench (1,632 tasks) → 83 shared / 5.1%; Multi-SWE-bench Kotlin extension (105) → 14 / 13.3%; SWE-PolyBench (2,110) → 239 / 11.3%; SWE-PolyBench Verified (382) → 41 / 10.7%; SWE-bench Multilingual (300) → 12 / 4.0%.
- Concentration: 202 of the 239 PolyBench overlaps are in `serverless/serverless`; all 12 Multilingual overlaps are in three PHP repos.
- Of the 348, 307 have identical git blobs on every file both patches touch; 9 partly identical, 10 differ, 22 incomparable.
- A 13-gram text filter would catch 347 of the 348 overlapping tasks, but also flags 1,249 of the other 31,731.
- `SWE-rebench-V2-PRs` adds 20 overlapping PRs (3 Multi-SWE-bench, 6 PolyBench, 11 Multilingual); because its problem statements are LLM-written, they share **no 8-gram** with the benchmarks, so a text filter would not catch them.
- The audit found no evidence V2 filtered Multi-SWE-bench PRs (83 observed vs 77.4 expected) and says the test has little power.

— [agentleak README](https://raw.githubusercontent.com/raimondasl/agentleak/main/README.md)

**V1 paper position on contamination (abstract):** "We compare results of various LLMs on this benchmark to results on SWE-bench Verified" and "performance of some language models might be inflated due to contamination issues." The paper frames freshness as the decontamination mechanism. [publisher claim] — [arXiv:2505.20411](https://arxiv.org/abs/2505.20411) (v1 2025-05-26, v2 revised 2025-11-04)

### Inferences
- **No Nebius card quantifies overlap with SWE-bench-Verified, SWE-Gym, R2E-Gym, or SWE-smith.** Only the *original* SWE-bench repository list is claimed to be excluded (V2), and SWE-bench-Verified exclusion is claimed only for the trajectory set and only in a blog post.
- For a Python repair agent the audit's findings are largely *not* the binding risk: the quantified overlaps are with multilingual benchmarks, and the concentrated cases are JS (`serverless/serverless`) and PHP. **A Python-only team still has an unquantified SWE-bench-Verified / SWE-Gym / R2E-Gym overlap exposure in `nebius/SWE-rebench` V1** and must run its own repo+commit-level exclusion.
- Practical decontamination recipe implied: exclude by `(repo, base_commit)` and by PR number against every evaluation benchmark, not by text n-grams — the audit's own data shows text filters both miss LLM-rewritten statements and over-flag by ~4%.

### Gaps
- No source quantifies V1 (`nebius/SWE-rebench`) overlap with SWE-bench-Verified, SWE-Gym, R2E-Gym, or SWE-smith. I did not find any such analysis.
- The V2 arXiv abstract page does not discuss overlap/decontamination; I did not read the full PDF, so the paper may contain more.

---

## Q5. Executable environments — Docker images, registry/tag patterns, sizes, install/test commands

### Takeaway
Yes, both generations publish Docker images on Docker Hub, with **different and fully observable naming schemes**. I counted **8,127 repositories under `swerebench/`** and **3,743 under `swerebenchv2/`** (Docker Hub v2 API, 2026-10-29). Image sizes are large: a sampled V1 image is **1.42 GB** compressed, V2 images **~469–514 MB**. Every row of both datasets carries a documented `install_config` with an explicit `test_cmd`.

### Cited Findings

**V1 Docker Hub namespace `swerebench`: `count = 8127` repositories.** Sample repos and pull counts: `sweb.eval.x86_64.aunsiels_1776_pyformlang-32` (3,351 pulls, updated 2026-04-20), `sweb.eval.x86_64.pennylaneai_1776_pennylane-7671` (3,922), `sweb.eval.x86_64.swe-agent_1776_swe-agent-1207` (1,929), `sweb.eval.x86_64.conan-io_1776_conan-18444` (3,061), `sweb.eval.x86_64.deepset-ai_1776_haystack-9527` (3,732). [verified, 2026-10-29] — [Docker Hub v2 API](https://hub.docker.com/v2/repositories/swerebench/?page_size=5)

- **V1 tag pattern:** `swerebench/sweb.eval.x86_64.<owner>_1776_<repo>-<PR#>:latest` — the PR number is part of the *repository* name and there is exactly **one tag, `latest`**, per repo. Verified: `swerebench/sweb.eval.x86_64.conan-io_1776_conan-18444` has `count = 1`, tag `latest`, **`full_size = 1,421,352,753` bytes (1.42 GB compressed)**, pushed 2026-04-20. The `1776` is the SWE-bench convention replacing `__` in instance ids. [verified]
- **V1 row-level image fields:** `docker_image` and `image_name` are **both populated for exactly 6,542 of 21,336 rows (30.7%) and NULL for the other 14,794** — and 6,542 is precisely the size of the `filtered` split (all 6,542 `filtered` rows have `image_name`, and all 6,542 are also present in `test`). Sample value: `swerebench/sweb.eval.x86_64.0b01001001_1776_spectree-64`. [verified, DuckDB over rev `89cdfbab…`]
- **V1 card claim:** "We've released 7,500 pre-built Docker images used in our RL pipeline. They're publicly available on Docker Hub. You do not need to build them yourself." News entry: "[2025/08/05] Uploaded the corresponding Docker images for 7,500 tasks to Docker Hub." [publisher claim] — [SWE-rebench README](https://huggingface.co/datasets/nebius/SWE-rebench/raw/main/README.md). **This conflicts with what the dataset actually exposes: only 6,542 rows carry an image name, while the namespace holds 8,127 repos.** [verified discrepancy]

**V2 Docker Hub namespace `swerebenchv2`: `count = 3743` repositories.** Samples: `scrapy-scrapy` (32,906 pulls), `mgechev-revive` (102,736), `myremylar-pygame-gui` (25,321), `pre-commit-pre-commit` (24,265), plus a `testrepo` with 0 pulls; most updated 2026-10-27. [verified, 2026-10-29] — [Docker Hub v2 API](https://hub.docker.com/v2/repositories/swerebenchv2/?page_size=5)

- **V2 tag pattern:** `docker.io/swerebenchv2/<owner>-<repo>:<PR#>-<short-sha>` — one repo per GitHub repo, one **tag per task**. `split_part(image_name,'/',1)` = `docker.io` for **all 32,079 rows** (i.e. fully-qualified refs). `image_name` is non-empty for **32,079/32,079 rows (100%)**. [verified]
- **V2 image sizes (observed `full_size`, compressed):** `swerebenchv2/scrapy-scrapy` has 20 tags, e.g. `6863-5902aab` 514,138,173 B; `6867-d602f13` 514,132,756 B; `6801-82acef3` 513,958,184 B; `6606-98ba612` 513,129,316 B. `swerebenchv2/wtforms-wtforms` has 22 tags, e.g. `823-e737a6c` 468,864,154 B; `809-1148de5` 468,821,812 B; `765-9f9146c` 469,610,815 B. So **~0.47–0.51 GB per V2 image vs ~1.42 GB for the sampled V1 image.** [verified, 2026-10-29]
- Real V2 `image_name` samples: `docker.io/swerebenchv2/elastic-synthetics:316-f52f0bf`, `docker.io/swerebenchv2/wtforms-wtforms:614-848d28d`, `docker.io/swerebenchv2/webpack-contrib-copy-webpack-plugin:590-a9b06a6`, `docker.io/swerebenchv2/crawler-commons-crawler-commons:227-ab9e33a`. [verified]

**Per-instance install/test commands — yes, documented and populated.** [verified]
- **V1** `install_config` struct fields: `env_vars`, `env_yml_path`, `install`, `log_parser`, `no_use_env`, `packages`, `pip_packages`, `pre_install`, `python`, `reqs_path`, `test_cmd`. Top `test_cmd` values across 21,336 rows: `pytest --no-header -rA --tb=line --color=no -p no:cacheprovider -W ignore::DeprecationWarning` **21,068 rows (98.7%)**; `pytest -xvs` 72; `python -m pytest --no-header -rA …` 19; `py.test --no-header …` 14; then a long tail of repo-specific commands (`pytest -p no:pastebin -p no:nose -p no:doctest -sv -vv --cov=pytorch_optimizer …` 7, bare `pytest` 6, etc.). `install_config.python` sample value `3.9`. V1 also ships `requirements` ("Freezed requirements") and `environment` fields. [verified]
- **V2** `install_config` struct fields: `base_image_name`, `docker_specs` (27 toolchain version keys: `python_version`, `python_image`, `node_version`, `go_version`, `rust_version`, `java_version`, `jdk_version`, `gcc_version`, `bazel_version`, `bun_version`, `deno_version`, `erlang_version`, `helm_version`, `llvm_version`, `lua_version`, `luajit_version`, `neovim_version`/`nvim_version`, `npm_version`, `pnpm_version`, `redis_version`, `ruby_version`, `rustc_version`, `cargo_version`, `solana_version`, `sqlite_version`, `docker_version`, `_variant`), `install` (list of strings), `log_parser`, `test_cmd`. Observed `base_image_name` values include `node_20`, `python_base_310`, `node_16`, `java_21`; observed `log_parser` values include `parse_log_pytest`, `parse_log_js_4`, `parse_java_mvn`; observed `test_cmd` includes `pytest --no-header -rA --tb=line --color=no -p no:cacheprovider -W ignore::DeprecationWarning tests/test_fields.py tests/test_validators.py tests/test_widgets.py` and `mvn test -B --no-transfer-progress -Dsurefire.printSummary=true`. [verified]

**Execution harness (V1):** Nebius provides a fork of SWE-bench based on "Release 4.0.3" at `github.com/SWE-rebench/SWE-bench-fork`, whose "primary modification introduces functionality to source environment installation constants directly from the `install_config` field"; the card points to commit `980d0cca8aa4e73f1d9f894e906370bef8c4de8a`. [publisher claim] — [SWE-rebench README](https://huggingface.co/datasets/nebius/SWE-rebench/raw/main/README.md)
**V2 harness/assets:** "For log parser functions, base Dockerfiles, and the prompts used, please see https://github.com/SWE-rebench/SWE-rebench-V2". [publisher claim] — [V2 README](https://huggingface.co/datasets/nebius/SWE-rebench-V2/raw/main/README.md)

### Inferences
- **V2 is the better-engineered execution surface**: 100% image coverage, fully-qualified refs, per-task tags, ~3× smaller images, explicit toolchain pinning. V1 has images for only 30.7% of its rows.
- Storage planning: pulling the whole V1 Python image set (~6,542 images × ~1.4 GB) implies ~9 TB compressed / substantially more on disk; the V2 Python slice (7,243 tasks across 691 repos, ~0.5 GB/image) is far cheaper, and because V2 tags share a repo base layer, actual disk use is well below tag_count × full_size.
- V1's near-universal `test_cmd` (98.7% one pytest invocation) means log parsing is effectively uniform — easy to build a single verifier.

### Gaps
- Docker Hub's API did not return a tag listing for the V1 repo name I formed from `docker_image` minus the PR suffix (`…_spectree` returned `count: None`), confirming the PR number belongs to the repo name rather than the tag; I verified the pattern on only one V1 repo (`conan-18444`), so the 1.42 GB figure is a **single-sample** size, not a distribution.
- Neither card states image sizes; all sizes here are my Docker Hub observations.
- I did not verify that the GitHub repos `SWE-rebench/SWE-bench-fork` and `SWE-rebench/SWE-rebench-V2` are reachable or that the named commit exists.

---

## Q6. Gold/reference patches and verification test patches (evaluator-only material)

### Takeaway
**Yes — and in both task datasets 100% of rows ship both the gold patch and the verification test patch, plus explicit FAIL_TO_PASS/PASS_TO_PASS test ID lists.** This material must be stripped from agent prompts; V1 additionally ships a `hints_text` field (issue comments) that is a prompt-leakage hazard of a different kind.

### Cited Findings

**V1 (`nebius/SWE-rebench`, 21,336 rows):** `length(patch) > 0` for **21,336/21,336**; `length(test_patch) > 0` for **21,336/21,336**; `meta.has_test_patch = true` for **21,336/21,336**. Fields `FAIL_TO_PASS`, `PASS_TO_PASS`, **plus `FAIL_TO_FAIL` and `PASS_TO_FAIL`** are all present in the schema. [verified, DuckDB over rev `89cdfbab…`]
- Card definitions: `patch` = "The gold patch, the patch generated by the PR (minus test-related code), that resolved the issue"; `test_patch` = "A test-file patch that was contributed by the solution PR"; `hints_text` = "Comments made on the issue prior to the creation of the solution PR's first commit creation date." [publisher claim] — [SWE-rebench README](https://huggingface.co/datasets/nebius/SWE-rebench/raw/main/README.md)
- `meta.is_lite = true` for **2,197/21,336** rows in `test`, and **1,091/6,542** in `filtered`. `meta.failed_lite_validators` lists why an instance is not lite; `meta.llm_score` carries `difficulty_score`, `issue_text_score`, `test_score`; `meta.num_modified_files` is present. [verified]
- `created_at` range in V1 `test`: **2014-04-30 14:58:36 → 2025-04-30 20:14:11**. [verified]

**V2 (`nebius/SWE-rebench-V2`, 32,079 rows):** `length(patch) > 0` for **32,079/32,079**; `length(test_patch) > 0` for **32,079/32,079**; `problem_statement` non-empty for **32,033** (46 empty); `interface` non-empty for **32,078** (1 empty). `FAIL_TO_PASS` and `PASS_TO_PASS` present (no FAIL_TO_FAIL/PASS_TO_FAIL). [verified]
- `created_at` range in V2: **2014-11-10 05:17:52 → 2025-10-31 18:00:44**. [verified]
- `meta.llm_metadata.difficulty` distribution: medium 21,798 · easy 8,677 · hard 1,485 · NULL 119. [verified]
- V2 `meta.llm_metadata` also carries `code`, `confidence` (float), `detected_issues` (booleans B1–B6), `external_urls`, `intent_completeness`, `pr_categories`, `reasoning`, `test_alignment_issues`; `meta` also has `num_modified_files`, `num_modified_lines`, `pr_author`, `pr_labels`, `pr_url`. [verified, from cardData dataset_info]

**Trajectory dataset:** no gold patch field. It ships `model_patch` (the agent's own diff) and the derived labels `resolved`, `gen_tests_correct`, `pred_passes_gen_tests`. Gold patches must be joined in from `nebius/SWE-rebench` by `instance_id`. [verified from DESCRIBE]

### Inferences
- Prompt-construction hygiene for a repair agent: from V1 keep `problem_statement`, `repo`, `base_commit`, `install_config`, `image_name`; **exclude `patch`, `test_patch`, `FAIL_TO_PASS`, `PASS_TO_PASS`, `FAIL_TO_FAIL`, `PASS_TO_FAIL`, `meta.llm_score`**; treat `hints_text` as optional-but-leaky (it is maintainer discussion that often contains the fix). From V2 additionally exclude `interface` and `meta.llm_metadata.code`/`reasoning`, which are LLM descriptions of the changed code and can leak the solution.
- V2 has no `FAIL_TO_FAIL`/`PASS_TO_FAIL`, so a V2-based evaluator cannot replicate V1's full SWE-bench-style four-way test accounting.

### Gaps
- Neither card warns that any field is evaluator-only or must be withheld from prompts; this is my inference from field semantics, not a publisher statement.

---

## Q7. Realistic achievable totals — instances, repositories, owners, Python-only subsets

### Takeaway
For a Python repository-repair agent the verified totals are: **21,336 Python task instances across 3,468 repos / 2,653 owners** (V1 `test`), of which only **6,542 instances / 1,790 repos** have prebuilt images; **7,243 Python instances across 691 repos / 573 owners** in V2; and **32,161 successful OpenHands trajectories over 3,792 Python issues in 1,823 repos / 1,445 owners** for SFT.

### Cited Findings

**All figures computed with DuckDB over the pinned parquet revisions, 2026-10-29.** [verified]

| Corpus / slice | rows | distinct instance_id | distinct repos | distinct owners |
|---|---|---|---|---|
| `nebius/SWE-rebench` split `test` (all Python) | 21,336 | 21,336 | **3,468** | **2,653** |
| `nebius/SWE-rebench` split `filtered` (= Docker-image subset) | 6,542 | 6,542 | **1,790** | **1,429** |
| `nebius/SWE-rebench` `test` with `meta.is_lite` | 2,197 | 2,197 | — | — |
| `nebius/SWE-rebench` `filtered` with `meta.is_lite` | 1,091 | 1,091 | — | — |
| `nebius/SWE-rebench-V2` all languages | 32,079 | 32,079 | **3,617** | **2,726** |
| `nebius/SWE-rebench-V2` `language='python'` | **7,243** | 7,243 | **691** | **573** |
| `nebius/SWE-rebench-openhands-trajectories` all | 67,074 | 6,306 | **1,823** | **1,445** |
| …`resolved=1` | 32,161 | **3,792** | — | — |
| …`resolved=0` | 34,913 | 4,255 | — | — |

**V2 full language × repo breakdown (rows / distinct repos):** python 7,243/691 · go 6,144/967 · ts 4,204/457 · js 4,138/452 · rust 3,123/307 · java 1,716/178 · php 1,445/138 · kotlin 889/68 · julia 793/79 · elixir 416/61 · scala 411/14 · swift 362/41 · dart 251/24 · c 230/24 · cpp 182/17 · csharp 173/21 · r 157/21 · clojure 105/32 · ocaml 58/18 · lua 39/7. Total 20 languages. [verified, cross-checked against the HF `/statistics` `language` `string_label` frequencies which match exactly]

**Publisher claims vs. my measurements:**
- V1 card: "over 21,000 issue–pull request pairs from 3,400+ Python repositories" → **verified: 21,336 rows, 3,468 repos.** [publisher claim corroborated]
- V1 paper abstract: "over 21,000 interactive Python-based SWE tasks" → consistent. — [arXiv:2505.20411](https://arxiv.org/abs/2505.20411)
- V2 card / paper: "32,079 samples covering Python, Go, TypeScript, …" and "32,079 executable tasks spanning 20 languages and 3,617 repositories" → **verified exactly.** — [arXiv:2602.23866](https://arxiv.org/abs/2602.23866) (v1 2026-02-27, v2 2026-06-01; marked ICML 2026)
- Trajectory card: "Repositories 1,823 / Issues Resolved 3,792 / Trajectories 67,074 / Successful 32,161" → **all four verified exactly from the parquet.** [publisher claim corroborated]
- V2 paper also claims "120,000+ tasks with installation instructions, fail-to-pass tests, and metadata" whose "problem statements are generated from the original pull request descriptions" — this is `nebius/SWE-rebench-V2-PRs` (126,300 rows verified). [publisher claim] — [arXiv:2602.23866](https://arxiv.org/abs/2602.23866)
- `nebius/SWE-bench-extra` card: "6,415 Issue-Pull Request pairs sourced from 1,988 Python repositories" — **the actual row count is 6,376** (HF size API). [verified discrepancy] — [SWE-bench-extra README](https://huggingface.co/datasets/nebius/SWE-bench-extra/raw/main/README.md)

**Union sizing for a Python agent:** V1 Python instances (21,336) + V2 Python instances (7,243) = 28,579 before dedup. V1 covers 3,468 repos, V2's Python slice 691 — V2's Python repo set is much narrower but its instances are all image-backed.

### Inferences
- **Realistic executable Python task pool today ≈ 6,542 (V1 image-backed) + 7,243 (V2 Python, 100% image-backed) ≈ 13,785 instances before deduplication**, spanning at most 1,790 + 691 = 2,481 repos. The remaining 14,794 V1 rows require building environments yourself from `install_config` via the SWE-bench fork.
- Deduplication between V1 and V2 is not pre-computed by Nebius. Both have `repo` + `base_commit`, and V1's `instance_id` is `owner__repo-PR` while V2's is a different scheme — join on `(repo, base_commit)` or `(repo, PR#)`, not on `instance_id`.
- **Highest-confidence SFT corpus for a Python repair agent: 32,161 resolved OpenHands trajectories over 3,792 issues** — real-world (not synthetic), single teacher, function-calling format, 5-tool OpenHands schema shipped alongside. Its main weakness is length (card claims 64.3 average turns, the highest of any comparable set), which drives long-context training cost.
- Owner counts (2,653 for V1, 573 for V2-Python, 1,445 for the trajectory set) matter for license due diligence: there is no small set of upstreams to negotiate with; a per-row license filter is the only tractable approach.

### Gaps
- I did not compute the V1↔V2 Python overlap (shared `(repo, base_commit)` pairs); this would require both parquets in one query and I was rate-limited before attempting it. The union figure of 28,579 is therefore an **upper bound**, not a deduplicated count.
- `nebius/SWE-rebench-V2-PRs` distinct-repo/owner counts were not computed (2.7 GB parquet; not attempted after the 429).
- No source states how many of the 21,336 V1 instances Nebius considers "training-grade" versus leaderboard/eval-reserved, beyond the `filtered` split and `is_lite` flag.
- My anonymous HF access was rate-limited (HTTP 429) during the final queries; a team re-running this should pass an `HF_TOKEN`.
