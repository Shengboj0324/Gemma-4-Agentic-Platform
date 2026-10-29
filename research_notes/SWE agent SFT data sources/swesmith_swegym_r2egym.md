# SWE-smith family, SWE-Gym and R2E-Gym as training data for a Python repo-repair agent

**Observation window: all HuggingFace API reads, DuckDB-over-parquet computations and Docker Registry reads in this file were performed on 2026-10-28 / 2026-10-29 (UTC).** Every revision SHA below is the `sha` field returned by `https://huggingface.co/api/datasets/<id>?blobs=true` on that date. Row counts marked **[computed]** were obtained by me running DuckDB 2.0.0 `read_parquet('hf://datasets/<id>@main/...')` against the live main-branch parquet files — they are not quotes. Numbers marked **[publisher claim]** come from card prose, README prose or paper abstracts and were *not* independently verifiable, or conflict with the data.

---

## Q1. Exact dataset ids, revision SHAs, row counts, file lists, declared licenses

### Takeaway
All ten target datasets are live and anonymously readable (no 429s encountered). The SWE-bench org has **moved SWE-smith from a mono-repo dataset to eight per-language datasets**; `SWE-bench/SWE-smith` carries an explicit deprecation notice dated 12/14/2025. Declared licenses are MIT for SWE-smith-py / SWE-smith / SWE-smith-trajectories / SWE-smith-go, MIT for SWE-Gym, Apache-2.0 for R2E-Gym-V1/Subset — and **no license at all** for five SWE-smith language variants, SWE-Gym-Lite, R2E-Gym-Lite and both R2E-Gym trajectory sets.

### Cited Findings

**SWE-bench org — SWE-smith task datasets** (metadata read 2026-10-28)

| dataset id | main sha | lastModified | splits (rows) | declared license | files |
|---|---|---|---|---|---|
| `SWE-bench/SWE-smith-py` | `77cab9055d42ab4a5c25c89a8f937096db13558e` | 2025-12-18 | train **50,908** | mit | 11 parquet, 220,645,767 B download_size |
| `SWE-bench/SWE-smith` (deprecated) | `ea6d7173829c7ec8fa16c22055699ff2e9188091` | 2025-12-14 | train **59,136** | mit | 11 parquet, 277,767,206 B |
| `SWE-bench/SWE-smith-go` | `d2f6ecc2cf8ae1af00fc790801bbacfa2913e015` | 2025-12-18 | train 8,212 | mit | 6,489,675 B |
| `SWE-bench/SWE-smith-java` | `1172df9919a8232e066562dfdb6e0193156de0c4` | 2026-02-12 | train 7,470 | **none** | 130,596,698 B |
| `SWE-bench/SWE-smith-js` | `d6aeb41ba9fb045c39e1c6d2322a8f08ee31cef4` | 2026-01-20 | train 6,073 | **none** | 29,302,638 B |
| `SWE-bench/SWE-smith-rs` | `1ae20d63edd611309d86133466247e3a9723a27d` | 2026-02-06 | train 5,311 | **none** | 22,178,093 B |
| `SWE-bench/SWE-smith-cpp` | `b1554a5f12603c825f9b48b361b9b97032347e48` | 2026-03-09 | train 5,123 | **none** | 64,873,798 B |
| `SWE-bench/SWE-smith-ts` | `c243d86f112d01b8507d311af912668aa1d74449` | 2026-02-28 | train 5,032 | **none** | 9,531,277 B |
| `SWE-bench/SWE-smith-php` | `6b5da17f1e3543fb2ed5d151a6f4972a457a8c36` | 2025-12-18 | train **1** | **none** | 30,103 B |

— [HF API SWE-smith-py](https://huggingface.co/api/datasets/SWE-bench/SWE-smith-py?blobs=true); [HF API SWE-smith](https://huggingface.co/api/datasets/SWE-bench/SWE-smith?blobs=true); [HF org listing](https://huggingface.co/api/datasets?author=SWE-bench)
- `SWE-bench/SWE-smith-php` contains exactly **1 row** — it is a placeholder, not a usable dataset — [HF API SWE-smith-php](https://huggingface.co/api/datasets/SWE-bench/SWE-smith-php?blobs=true)
- All SWE-smith task datasets share the same 7 columns: `instance_id, patch, FAIL_TO_PASS, PASS_TO_PASS, image_name, repo, problem_statement`. **There is no `test_patch` column and no `base_commit`** — the bug is the diff in `patch` and the environment is the prebuilt image — [HF API SWE-smith-py](https://huggingface.co/api/datasets/SWE-bench/SWE-smith-py?blobs=true)
- `SWE-bench/SWE-smith-trajectories`, sha `08e109b4a59eaeebf80e4675cd125d42e7ac99a4`, lastModified 2025-07-19, license mit. Declared splits: **tool 24,100 / xml 26,076 / ticks 25,826** rows; `dataset_size` 10,727,976,693 B, `download_size` 3,171,137,897 B. Columns: `messages (string), instance_id, resolved (bool), model, traj_id, patch`. 32 parquet files — [HF API SWE-smith-trajectories](https://huggingface.co/api/datasets/SWE-bench/SWE-smith-trajectories?blobs=true)
- **Orphan files in SWE-smith-trajectories**: the repo also contains 8 files `data/train-0000{0..7}-of-00008.parquet` (totalling 1,052,703,887 B) that are **not referenced by any `configs` entry**. [computed] They are a duplicate of the `xml` split — identical row count (26,076), identical distinct `traj_id` (23,821), identical distinct `instance_id` (13,501), identical `resolved=true` count (11,503) and identical per-model row counts. A `git clone`/`snapshot_download` of this repo therefore pulls ~1 GB of redundant data — [HF API SWE-smith-trajectories](https://huggingface.co/api/datasets/SWE-bench/SWE-smith-trajectories?blobs=true) + my DuckDB scan

**SWE-Gym org** (metadata read 2026-10-28)

| dataset id | main sha | lastModified | splits (rows) | license |
|---|---|---|---|---|
| `SWE-Gym/SWE-Gym` | `bb94ed9e39bbeb96a7fcbfb533b80f25a7fd59cb` | 2025-05-10 | train **2,438** | mit |
| `SWE-Gym/SWE-Gym-Lite` | `f70b1a29ab120eb0a0ee7a1deb029825e735b2b0` | 2024-12-23 | train **230** | **none** |
| `SWE-Gym/SWE-Gym-Raw` | `47e98187b31fd5a83deb62d5c48b94619648f2db` | 2024-12-23 | train 64,689 (unvalidated) | **none** |
| `SWE-Gym/OpenHands-SFT-Trajectories` | `4aaa5a4a4b5861f4799d2336908760c190ac3b17` | 2025-05-10 | `train.success.oss` **491** | mit |
| `SWE-Gym/OpenHands-Sampled-Trajectories` | `baf3a4e4bff514d48ddc08a93a2ade5c126212c7` | 2024-12-23 | `train.raw` 6,055 | **none** |
| `SWE-Gym/OpenHands-Verifier-Trajectories` | `d47f6cab996d3a5f7ba517c0be57595f4f6201ce` | 2024-12-23 | mixture 2,636 / onpolicy 1,750 / offpolicy 886 | **none** |
| `SWE-Gym/MoatlessTools-Sampled-Trajectories` | `51ba9a7f38fed087bcb1a11b3d51972ed72a8317` | 2024-12-23 | *no `dataset_info`*; 15 files, 5,522,062,671 B | **none** |

— [HF org listing SWE-Gym](https://huggingface.co/api/datasets?author=SWE-Gym); [HF API SWE-Gym](https://huggingface.co/api/datasets/SWE-Gym/SWE-Gym?blobs=true)
- `SWE-Gym` / `SWE-Gym-Lite` columns: `instance_id, hints_text, patch, test_patch, created_at, problem_statement, repo, base_commit, version, PASS_TO_PASS, FAIL_TO_PASS` — i.e. full SWE-bench schema; **gold patch and test_patch both ship** — [HF API SWE-Gym](https://huggingface.co/api/datasets/SWE-Gym/SWE-Gym?blobs=true)
- `OpenHands-Sampled-Trajectories` columns `instance_id, run_id, resolved, messages, tools, test_result` — this is the rejection-sampling pool (6,055 rollouts) from which the 491-row SFT set was filtered — [HF API](https://huggingface.co/api/datasets/SWE-Gym/OpenHands-Sampled-Trajectories?blobs=true)
- **`SWE-Gym/*-trajectories` do exist** (the assignment asked "if any"): four of them, listed above. The org has no dataset named `SWE-Gym-trajectories`.

**R2E-Gym org** (metadata read 2026-10-28)

| dataset id | main sha | lastModified | splits (rows) | license |
|---|---|---|---|---|
| `R2E-Gym/R2E-Gym-V1` | `903d405799ac435061c41e72260c81ca5100f964` | 2026-07-23 | train **8,101** | apache-2.0 |
| `R2E-Gym/R2E-Gym-Subset` | `2e8108ff942f24fcb5686badfaf7f9a8808566d5` | 2026-07-23 | train **4,578** | apache-2.0 |
| `R2E-Gym/R2E-Gym-Lite` | `8d3163011f01f9393bb3dc7700497a79a8686ae5` | 2025-02-05 | train 4,578 + 9 `dev_*pr_v*` eval splits (100/1000/1876/1000/876/575/…) | **none** |
| `R2E-Gym/R2EGym-SFT-Trajectories` | `63ab4eb37668f8be0104133c21d896bedbcf8404` | 2025-02-09 | train **3,231** | **none** |
| `R2E-Gym/R2EGym-Verifier-Trajectories` | `d8340c4605bb1a00a206a1978813cee35daeff8c` | 2025-02-25 | train 5,750 (`messages, docker_images, rewards`) | **none** |
| `R2E-Gym/R2EGym-TestingAgent-SFT-Trajectories` | `0cfc507e195ff875fa622ab5cd4403d4a7409c46` | 2025-03-19 | train 2,281 (`messages, exit_reasons, num_steps`) | **none** |

— [HF org listing R2E-Gym](https://huggingface.co/api/datasets?author=R2E-Gym); [HF API R2E-Gym-V1](https://huggingface.co/api/datasets/R2E-Gym/R2E-Gym-V1?blobs=true)
- `R2E-Gym-V1` / `-Subset` / `-Lite` columns: `repo_name, docker_image, commit_hash, parsed_commit_content, execution_result_content, modified_files, modified_entity_summaries, relevant_files, num_non_test_files, num_non_test_func_methods, num_non_test_lines, prompt, problem_statement, expected_output_json`. **There is no `patch` / `test_patch` / `FAIL_TO_PASS` column** — the gold change and the tests are embedded inside the JSON blobs `parsed_commit_content` and `expected_output_json` — [HF API R2E-Gym-V1](https://huggingface.co/api/datasets/R2E-Gym/R2E-Gym-V1?blobs=true)
- [computed] **`R2E-Gym-Subset` is exactly a subset of `R2E-Gym-V1` and is identical to `R2E-Gym-Lite`'s `train` split**: all 4,578 distinct `docker_image` values in Subset appear in V1 and all 4,578 appear in Lite/train. Do not count Subset, Lite/train and V1 as three datasets.
- `R2E-Gym-Lite` ships 9 extra `dev_*` splits (dev_10pr_v1 100 rows, dev_100pr_v1 1,000, dev_200pr_v1 1,876, dev_100pr_v2 1,000, dev_100pr_v3 876, dev_100pr_v4 575, …). `dev_100pr_v1` and `dev_100pr_v2` have **byte-identical parquet sizes** (62,174,247 + 85,362,341) — almost certainly the same rows under two names — [HF API R2E-Gym-Lite](https://huggingface.co/api/datasets/R2E-Gym/R2E-Gym-Lite?blobs=true)

### Inferences
- Total declared SWE-smith task instances across all eight current language datasets = **88,130**, of which 50,908 (57.8%) are Python.
- The five license-less SWE-smith language variants (java/js/rs/cpp/ts) are a drafting oversight rather than a deliberate restriction (their sibling py/go datasets are MIT and the source repo is MIT), but as published they carry **no grant at all**, which is legally worse than a restrictive license.

### Gaps
- `SWE-Gym/MoatlessTools-Sampled-Trajectories` publishes no `dataset_info`, so its row count is unknown without a full download of 5.5 GB; I did not attempt it.

---

## Q2. SWE-smith bug generation: mechanisms, per-strategy fractions, issue-text leakage, and where the card disagrees with the data

### Takeaway
SWE-smith uses four documented families — LM-generated (modify/rewrite), procedural AST mutation, PR mirroring, and combination of validated bugs. [computed] For `SWE-smith-py` the mix is **67% procedural, 20% combined, 8.4% LM-rewrite, 4.9% PR-mirror, 0.008% LM-modify**. Issue text is LM-generated **with the bug-introducing diff, the test output and the failing test source all in the prompt**, under a prompt-level instruction not to reveal the fix — leakage is mitigated by instruction, not prevented structurally. And **22.5% of SWE-smith-py rows have a completely empty `problem_statement`**, which no card mentions.

### Cited Findings

**Mechanisms** (SWE-smith docs, `docs/guides/create_instances.md`, read 2026-10-29):
- *LM Generated*: "Per entity, we prompt a language model to either: *Modify* the entity such that a bug is introduced (a.k.a. *LM Modify*) or *Rewrite* the entity from scratch (a.k.a. *LM Rewrite*)." Reference commands use `openai/gpt-4o` for modify and `anthropic/claude-3-7-sonnet-20250219` for rewrite — [create_instances.md](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/docs/guides/create_instances.md)
- *Procedural Modification*: entities are converted to an `ast`, a criterion is checked, the AST subtree is mutated and unparsed. "There are 13 (and counting) in total." Artifacts are named `bug__func_pm_<name>__<hash>.diff` — same source
- *PR Mirroring*: uses SWE-bench's own collection script; a PR qualifies if it has ≥1 linked issue and edits ≥1 code file. "Per PR, we ask an LM to revert the PR's changes file by file." The docs explicitly note SWE-smith relaxes SWE-bench's criteria — SWE-bench additionally requires test-file changes, "Because SWE-smith does rely on test file changes to identify breaking existing tests, we can attempt to recreate a broader subset of PRs than what SWE-bench normally considers." Reference model `openai/o3-mini` — same source
- *Combining Bugs*: combines **already-validated** single-entity bugs that touch the same file (`combine_file`) or the same module subdirectory at a given `depth` (`combine_module`) — same source
- At-scale generation runs on Modal via `scripts/bug_gen.py --language <lang>`, with a two-phase generate-then-validate pipeline (pre-gold baseline tests, then post-gold tests) — same source

**[computed] Strategy mix in `SWE-smith-py` @ `77cab905…`** (classified from the `instance_id` suffix, which encodes the generator; the "other" bucket is empty, so this partition is exhaustive over all 50,908 rows):

| strategy | rows | share | rows with empty `problem_statement` | avg `problem_statement` chars |
|---|---|---|---|---|
| procedural `func_basic__` | 17,818 | 35.0% | 5,448 (30.6%) | 739 |
| procedural `func_pm_*__` | 16,256 | 31.9% | 3,170 (19.5%) | 879 |
| `combine_file__` | 5,861 | 11.5% | 1,307 (22.3%) | 946 |
| `lm_rewrite__` | 4,273 | 8.4% | 0 | 1,351 |
| `combine_module__` | 4,215 | 8.3% | 1,491 (35.4%) | 807 |
| `pr_*` (PR mirror) | 2,481 | 4.9% | 21 (0.8%) | 1,598 |
| `lm_modify__` | 4 | 0.008% | 0 | 912 |
| **total** | **50,908** | 100% | **11,437 (22.47%)** | 907 |

- [computed] `SWE-smith-py` also has: 50,908 distinct `instance_id` (no duplicates), **131 distinct `repo`**, 131 distinct `image_name` (one image per repo), 0 rows with an empty `FAIL_TO_PASS`, mean 80.7 F2P tests (max 10,936) and mean 1,063.5 P2P tests (max 22,010), mean `patch` length 1,782 chars.
- [computed] Top repos by row count in `SWE-smith-py`: `scanny__python-pptx` 2,389; `pandas-dev__pandas` 2,354; `pylint-dev__astroid` 1,770; `python-openxml__python-docx` 1,686; `cantools__cantools` 1,440; `pygments__pygments` 1,430; `pydicom__pydicom` 1,328; `sqlfluff__sqlfluff` 1,293; `conan-io__conan` 978; `seperman__deepdiff` 964; `pallets__jinja` 957; `oauthlib__oauthlib` 940. The distribution is heavily concentrated — the top 12 of 131 repos hold ~17,500 rows (34%).

**Issue-text generation and leakage** (`configs/issue_gen/ig_v2.yaml`, read 2026-10-29):
- Generator model on current main is `portkey/gpt-5-mini` (`litellm_model_name_override: openai/gpt-5-mini`). The docs' worked example uses `anthropic/claude-3-7-sonnet-20250219` — [issue_gen.md](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/docs/guides/issue_gen.md), [ig_v2.yaml](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/configs/issue_gen/ig_v2.yaml)
- The generator prompt is given four inputs: "1. Demonstration: A realistic GitHub issue to mimic… 2. Patch: A git diff output/pull request changes that introduces a bug… 3. Test output… 4. Test source code: Source code for one or more tests that failed" — [ig_v2.yaml](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/configs/issue_gen/ig_v2.yaml)
- Leakage is controlled only by instruction. Verbatim from the config: "DO NOT GIVE AWAY THE FIX! THE SOLUTION CODE SHOULD NEVER APPEAR IN YOUR RESPONSE." and "DO NOT SAY THAT EXISTING TEST(s) FAILED." and "DO NOT SUGGEST RUNNING ANY TESTING COMMANDS (e.g., pytest)." and, in the system prompt, "DO NOT explain the fix/what caused the bug itself, focus on how to reproduce the issue it introduces" — [ig_v2.yaml](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/configs/issue_gen/ig_v2.yaml)
- [computed] Empirical leakage check over all 50,908 `SWE-smith-py` problem statements: **5** contain `diff --git`, **5** contain a hunk header `@@ -`, and 38,140 (75%) contain a markdown code fence ```` ``` ````. So literal diff leakage is negligible (0.01%), but three quarters of statements embed code — which is the intended reproduction-script style, not necessarily the fix.
- Documented alternatives to LM issue text, which *do* leak by construction: "Random F2P Test Case — The problem statement shows a randomly selected Fail-to-Pass test case from the task instance", plus "Static Issue Text" (one of 7 templates) and "Original Issue Text" (only works for some PR mirrors) — [issue_gen.md](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/docs/guides/issue_gen.md)

**Where the cards/papers disagree with the data:**
- `SWE-bench/SWE-smith` card prose: "a training dataset of **50137** task instances from **128** GitHub repositories". Its own YAML metadata says `num_examples: 59136`. [computed] The parquet files contain **59,136 rows, 59,136 distinct instance_ids and 222 distinct repos**. The prose is wrong on both axes (−9,000 instances, −94 repos) — [SWE-smith card](https://huggingface.co/datasets/SWE-bench/SWE-smith/raw/main/README.md)
- arXiv 2504.21798 abstract: "we create a dataset of **50k** instances sourced from **128** GitHub repositories" — matches the stale card prose, not the current data — [arXiv:2504.21798](https://arxiv.org/abs/2504.21798)
- GitHub README: "**52k** task instances", "**26k** SWE-agent trajectories, including the **5k** used to train SWE-agent-LM-32B", "**250+** environments" — a third, different instance count — [SWE-smith README](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/README.md)
- `SWE-bench/SWE-smith-py` card prose: "As of 12/14/2025, **SWE-smith: Python** contains **50908** task instances from **131** GitHub repositories" — [computed] **this one is exactly right** (50,908 rows, 131 distinct repos) — [SWE-smith-py card](https://huggingface.co/datasets/SWE-bench/SWE-smith-py/raw/main/README.md)
- `SWE-bench/SWE-smith-go` card prose has a typo'd date: "As of 12/14/202, **SWE-smith: Golang** contains **8212** task instances from **87** GitHub repositories" — matches its metadata — [SWE-smith-go card](https://huggingface.co/datasets/SWE-bench/SWE-smith-go/raw/main/README.md)
- The deprecation notice on `SWE-bench/SWE-smith`, verbatim: "[12/14/2025] NOTE: We will no longer actively update this dataset. While this dataset is still functional and usable, we recommend you use the `SWE-bench/SWE-smith-[lang]` datasets." — [SWE-smith card](https://huggingface.co/datasets/SWE-bench/SWE-smith/raw/main/README.md)
- [computed] Relationship between the two: all **50,908** `SWE-smith-py` instance_ids are present in `SWE-smith` (59,136 rows / 222 repos); 91 of SWE-smith's 222 repos are absent from SWE-smith-py. So `SWE-smith` = `SWE-smith-py` + 8,228 non-Python rows. **Never sum them.**

### Inferences
- The ~22.5% empty-`problem_statement` rate is the single most consequential undocumented fact here. Those 11,437 rows cannot be used for issue-driven repair SFT without regenerating issue text (which requires re-running `issue_gen` with an LM, i.e. your own inference cost). A usable Python issue-driven pool is **39,471 rows**, not 50,908.
- Emptiness is strongly strategy-correlated (0% for lm_rewrite, 0.8% for pr_mirror, 19–35% for procedural/combine), consistent with the issue-generation pass having been run selectively rather than over the whole set.
- Because 67% of bugs are procedural AST mutations (shuffled control flow, removed assignments, inverted ifs), the *distribution of bug kinds* is far from real-world PR bugs. The `pr_*` family (2,481 rows, 4.9%) is the only part that mirrors real PRs, and it also has the longest, most realistic problem statements (1,598 chars avg).

### Gaps
- The docs do not publish the per-strategy counts used in the paper, so I cannot compare my computed mix to an author-stated mix. My breakdown is inferred from `instance_id` naming, which the docs confirm encodes the generator (`bug__<bug_type>__<hash>`) but which the authors do not promise as a stable API.
- I could not determine which issue-gen config version was actually used for the published 2025-12 `SWE-smith-py` rows (`ig_v2.yaml` is what is on main today; the prose and the paper reference Claude 3.7 Sonnet).

---

## Q3. SWE-smith-trajectories: teacher, scaffold, tools, serialization variants, failed trajectories

### Takeaway
Teacher is **Claude 3.7 Sonnet (73%), Claude 3.5 Sonnet (24%) and GPT-4o (2.5%)** — not a single model. Scaffold is SWE-agent, version unstated anywhere I could find. **Failed trajectories are included and are the majority**: only 39–44% of rows have `resolved=true`. The three splits are **not** the same trajectories re-serialized — `tool ∩ xml` = 14,984 traj_ids, `tool ∩ ticks` = 8,866, union = 49,897 distinct traj_ids — but they *do* overlap heavily and the 4,954 actual SFT trajectories live entirely in the `xml` split.

### Cited Findings
- Card prose: "This dataset contains the **5017** trajectories we fine-tuned Qwen 2.5 Coder Instruct on, leading to [SWE-agent-LM-32B], a coding LM agent that achieve 40.2% on SWE-bench Verified (no verifiers or multiple rollouts, just 1 attempt per instance). Trajectories were generated by running **SWE-agent + Claude 3.7 Sonnet** on task instances from the SWE-smith dataset." The card's YAML also says `size_categories: 1K<n<10K` — [SWE-smith-trajectories card](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories/raw/main/README.md)
- **The published splits are 5x larger than that prose and the size_categories tag is wrong.** [computed] per split:

| split | rows | distinct `traj_id` | distinct `instance_id` | `resolved=true` | resolve rate |
|---|---|---|---|---|---|
| `tool` | 24,100 | 24,100 | 10,637 | 9,427 | 39.1% |
| `xml` | 26,076 | 23,821 | 13,501 | 11,503 | 44.1% |
| `ticks` | 25,826 | 25,826 | 13,500 | 11,430 | 44.3% |
| (orphan `train`) | 26,076 | 23,821 | 13,501 | 11,503 | 44.1% |

- [computed] **Teacher model mix** (not one model, contrary to the card):

| model | tool | xml | ticks |
|---|---|---|---|
| `claude-3-7-sonnet-20250219` | 17,715 | 18,457 | 18,457 |
| `claude-3-5-sonnet-20241022` | 5,751 | 7,091 | 6,894 |
| `gpt-4o-2024-08-06` | 634 | 528 | 475 |

- [computed] **Cross-split relationship.** Distinct `instance_id`: tool 10,637, xml 13,501, ticks 13,500; union = **13,501** — i.e. tool's instance set is entirely contained in xml's, and ticks ∩ tool = 10,636. Distinct `traj_id`: tool ∩ xml = 14,984; tool ∩ ticks = 8,866; three-way union = **49,897**. So the splits are partly the same rollouts re-serialized and partly different rollouts.
- [computed] **The real SFT set is identifiable and is 4,954, not 5,017.** `docs/assets/traj_ids_swealm32b.txt` in the SWE-smith repo lists **4,954 unique traj_ids**. Joining them against the splits: **4,954/4,954 are in `xml`**, 3,567 are in `tool`, **0 are in `ticks`**. All 4,954 have `resolved=true`. — [traj_ids_swealm32b.txt](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/docs/assets/traj_ids_swealm32b.txt)
- `traj_id` has the form `<repo>.<commit8>.<bug_type>__<bughash>.<trajhash>`, i.e. `instance_id` + an 8-char rollout suffix. Example [computed] from `data/tool-00000-of-00008.parquet`: `django-money__django-money.835c1ab8.func_pm_ctrl_shuffle__viqnyl9u.8qa84d2e` with `instance_id` `django-money__django-money.835c1ab8.func_pm_ctrl_shuffle__viqnyl9u`. Multiple rollouts per instance therefore exist (xml: 23,821 traj over 13,501 instances ⇒ ~1.76 rollouts/instance).
- [computed] `messages` is a **JSON-encoded string**, not a struct. Roles observed in the `tool` split: `system, user, assistant, tool`. Sampled 400 rows of `data/tool-00004-of-00008.parquet`: mean 40.5 messages per trajectory.
- GitHub README confirms the 26k/5k split of the release: "26k SWE-agent trajectories, including the 5k used to train SWE-agent-LM-32B" — [SWE-smith README](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/README.md)
- [computed] Of `xml`'s 13,501 distinct instance_ids, **12,389 are present in today's `SWE-smith-py`**; and the instance_ids span **129 distinct source repos**. The ~1,100 unmatched instances come from repos/instances no longer in the current py dataset.

### Inferences
- **Do not count the three splits as 76,002 independent trajectories.** The defensible maxima are: 49,897 distinct rollouts if you union on `traj_id` and accept mixed serializations; 13,501 distinct *tasks*; 4,954 trajectories if you want exactly the recipe that produced SWE-agent-LM-32B.
- The naming suggests the three splits are three action-serialization formats for a SWE-agent-style scaffold: native tool-calling (`tool`), XML-tagged function blocks (`xml`, the original SWE-agent format) and a backtick/"ticks" format. **The authors do not document this anywhere I found** — the split names are the only evidence. Because the trajectory *content* differs between formats, a model trained on one format will not accept another without re-templating.
- Since `ticks` shares zero traj_ids with the published SFT list while having nearly the same instance coverage as `xml`, `ticks` looks like a later, independent re-collection rather than a re-serialization of the SFT set.
- The scaffold's tool set and argument semantics are **not described in the dataset card at all**; they are only recoverable by parsing the `tools`/`messages` payloads or by pinning the SWE-agent version. For a Python repair agent this is a real integration cost: you must reverse-engineer `str_replace_editor`-style argument conventions from the data.

### Gaps
- **No SWE-agent version is stated** on the card, in the README, or in the paper abstract. I could not establish which SWE-agent release produced these trajectories.
- No documentation of the `tool`/`xml`/`ticks` distinction exists on the card. This is an inference from split names plus the overlap statistics.
- The card's "5017" is not reproducible from any artifact I could find; the repo's own ID list has 4,954. I cannot explain the 63-trajectory difference.

---

## Q4. SWE-Gym and R2E-Gym: distinct instances, repos, gold patches, verification tests, Docker images

### Takeaway
SWE-Gym is small but clean: 2,438 real PR-derived instances from 11 Python repos, **gold patch and test_patch both ship for 100% of rows**, and its Docker images are published per-instance. R2E-Gym-V1 is 8,101 synthetically-back-translated instances from only **13 Python repos**, ships no separate patch/test columns, and publishes one Docker image per instance. All Docker images I probed are live.

### Cited Findings

**SWE-Gym** [computed] @ `bb94ed9e…`:
- 2,438 rows, **2,438 distinct instance_id**, **11 distinct repos**, **0 rows with an empty `patch`**, **0 rows with an empty `test_patch`**, mean `problem_statement` 2,314 chars (the longest/most realistic of any dataset in this note).
- Repo distribution: `pandas-dev/pandas` 737, `Project-MONAI/MONAI` 374, `getmoto/moto` 343, `python/mypy` 257, `iterative/dvc` 225, `dask/dask` 145, `modin-project/modin` 107, `pydantic/pydantic` 83, `conan-io/conan` 75, `facebookresearch/hydra` 66, `bokeh/bokeh` 26.
- `SWE-Gym-Lite`: 230 rows, 230 distinct instance_id, 11 repos, mean problem_statement 1,764 chars. **Card and repo README disagree**: the HF card says "SWE-Gym Lite contains **230** instances" while the GitHub README says "a Lite split of **234** instances" — [SWE-Gym-Lite card](https://huggingface.co/datasets/SWE-Gym/SWE-Gym-Lite/raw/main/README.md); [SWE-Gym README](https://raw.githubusercontent.com/SWE-Gym/SWE-Gym/main/README.md)
- `SWE-Gym-Raw`: 64,689 rows but only **62,041 distinct instance_id** [computed] over 358 repos — this is the pre-validation candidate pool, has duplicates, and has no executable guarantee.
- Publisher claims from the project README: "**2.4K real tasks from 11 Python repos**"; "Our baselines achieve new open SOTA - 32%/26% on SWE-Bench Verified/Lite"; "When fine-tuned on less than **500** agent-environment interaction trajectories sampled from it from **GPT-4o and Claude 3.5 Sonnet**, we achieve +14% absolute gains on SWE-Bench Verified with an 32B LM-powered OpenHands agent" — [SWE-Gym README](https://raw.githubusercontent.com/SWE-Gym/SWE-Gym/main/README.md). The "<500" figure matches the 491 rows in `OpenHands-SFT-Trajectories` [computed metadata].
- **Docker images (verified live 2026-10-29)**: registry Docker Hub, pattern `xingyaoww/sweb.eval.x86_64.<instance_id with / → _s_>:latest`. Probe of `xingyaoww/sweb.eval.x86_64.getmoto_s_moto-5347:latest` via the Docker Registry v2 manifest API returned **13 layers, 1,118,917,624 B compressed (~1.12 GB)** — [registry-1.docker.io manifest](https://registry-1.docker.io/v2/xingyaoww/sweb.eval.x86_64.getmoto_s_moto-5347/manifests/latest)

**R2E-Gym** [computed] @ `903d4057…` (V1) and `2e8108ff…` (Subset):
- `R2E-Gym-V1`: 8,101 rows, **13 distinct `repo_name`**, **8,101 distinct `docker_image`** (one image per instance), 8,101 distinct `commit_hash`, mean `problem_statement` 1,089 chars, and **1,192 rows (14.7%) with a completely empty `problem_statement`**.
- `R2E-Gym-Subset`: 4,578 rows, **10 distinct repo_name**, 4,578 distinct docker_image, mean problem_statement 1,162 chars, **0 empty**.
- Repo distribution in V1: `sympy` 2,331, `pandas` 1,444, `matplotlib` 808, `numpy` 781, `pillow` 620, `orange3` 482, `moto` 384, `aiohttp` 299, `tornado` 261, `scrapy` 215, `pyramid` 189, `datalad` 179, `coveragepy` 108. Note `repo_name` is a **bare name**, not `owner/repo`.
- **Docker images (verified live 2026-10-29)**: registry Docker Hub, pattern `namanjain12/<repo>_final:<40-char commit sha>` (e.g. `namanjain12/orange3_final:2d9617bd0cb1f0ba61771258410ab8fae8e7e24d`). Manifest probe returned **17 layers, 893,231,081 B compressed (~0.89 GB)**. A tag listing on `namanjain12/orange3_final` returns many per-commit tags, confirming the one-image-per-instance scheme — [registry-1.docker.io manifest](https://registry-1.docker.io/v2/namanjain12/orange3_final/manifests/2d9617bd0cb1f0ba61771258410ab8fae8e7e24d)
- R2E-Gym paper abstract: AgentGym has "more than **8.7K** tasks" and SYNGEN works by "test-generation and back-translation directly from commits", "which reduces reliance on human-written issues or unit tests". The 8.7K is a **[publisher claim]**; the published `R2E-Gym-V1` has 8,101 rows — [arXiv:2504.07164](https://arxiv.org/abs/2504.07164)

**SWE-smith Docker images (verified live 2026-10-29)**:
- Pattern: `swebench/swesmith.x86_64.<owner>_1776_<repo>.<commit8>:latest` (the literal `_1776_` replaces `/`). The `image_name` column carries this directly, e.g. `swebench/swesmith.x86_64.pdfminer_1776_pdfminer.six.1a8bd2f7` [computed from parquet].
- Manifest probes: `swebench/swesmith.x86_64.pdfminer_1776_pdfminer.six.1a8bd2f7:latest` → 12 layers, **1,466,822,017 B (~1.47 GB)** compressed; `swebench/swesmith.x86_64.pandas-dev_1776_pandas.95280573:latest` → 12 layers, **2,659,706,944 B (~2.66 GB)** compressed. Only tag is `latest` — [registry-1.docker.io](https://registry-1.docker.io/v2/swebench/swesmith.x86_64.pandas-dev_1776_pandas.95280573/manifests/latest)
- Build artifacts live in `SWE-bench/SWE-smith-envs`, "Artifacts for building environments (Docker images) for repositories represented in SWE-smith", last updated 2026-03-02, **`license: null`** on the GitHub API — [GitHub API](https://api.github.com/repos/SWE-bench/SWE-smith-envs)

### Inferences
- **SWE-smith is one image per repo (131 for Python), SWE-Gym and R2E-Gym are one image per instance.** At ~1.5–2.7 GB compressed per image this makes SWE-smith's environment footprint roughly 131 × ~1.5 GB ≈ **200 GB compressed** for full Python coverage, whereas R2E-Gym-V1 would be 8,101 × ~0.9 GB ≈ **7 TB** and SWE-Gym 2,438 × ~1.1 GB ≈ **2.7 TB**. For an execution-feedback or RL loop, SWE-smith is by far the cheapest to host; R2E-Gym and SWE-Gym are only practical if you pull images on demand for a sampled subset.
- R2E-Gym's 14.7% empty-`problem_statement` rate in V1 (0% in Subset) means the V1 → Subset relationship is partly a quality filter, and the Subset/Lite 4,578 rows are the vetted core.

### Gaps
- I did not verify image availability for every instance, only the four probed above. Registry-wide per-instance availability for R2E-Gym (8,101 tags) and SWE-Gym (2,438 images) is unverified.
- Uncompressed on-disk sizes are not exposed by the manifest API; all sizes above are **compressed layer sums**, typically 2–3x smaller than the extracted image.

---

## Q5. R2E-Gym SFT trajectories: current state, rows, columns, teacher, license

### Takeaway
**Confirmed: the card is genuinely empty.** `R2E-Gym/R2EGym-SFT-Trajectories` @ `63ab4eb3…` (lastModified 2025-02-09) has a 352-byte README consisting of **nothing but auto-generated YAML front matter** — no prose, no license, no teacher model, no scaffold, no provenance, no evaluation. The same is true of `R2E-Gym-V1` and `R2E-Gym-Lite`. This is not a fetch failure; I retrieved the raw README and it ends at the closing `---`.

### Cited Findings
- Full card body after the YAML: empty. The YAML declares only `dataset_info` (features: `messages` as a list of `{content, role}`; split `train`, `num_bytes` 154,802,030, `num_examples` **3,231**; `download_size` 55,949,361) and `configs` — [R2EGym-SFT-Trajectories README raw](https://huggingface.co/datasets/R2E-Gym/R2EGym-SFT-Trajectories/raw/main/README.md)
- **No license** is declared in the card YAML and no `license:*` tag appears in the HF API `tags` array — [HF API](https://huggingface.co/api/datasets/R2E-Gym/R2EGym-SFT-Trajectories?blobs=true)
- [computed] Full scan of the single parquet shard: **3,231 rows**, one column `messages` (list of `{role, content}` strings), roles present are **`system`, `user`, `assistant` only — no `tool` role**. Mean 33.2 messages per trajectory, mean 47,294 total chars per trajectory, mean **11,077 assistant chars** per trajectory (assistant share 23.4%).
- [computed] The scaffold is a **ReAct/text-function format with tool definitions inlined in the system prompt**, not native tool calling. Verbatim opening of the system prompt in row 0: "You are a programming agent who is provided a github issue and repository bash environment and is tasked to solve certain tasks (e.g., file localization, testcase generation, code repair and editing etc) to resolve the issue. We have access to the following functions: –– BEGIN FUNCTION #1: file_editor ––  Description: Custom editing tool for viewing, creating and editing files… The undo_edit command will revert the last edit made to the file at path". The `str_replace` semantics are documented inline: "The old_str parameter should match EXACTLY one or more consecutive lines from the original file. Be mindful of whitespaces!"
- **Teacher model: absent.** There is no `model` column, no `resolved`/reward column, and no card text naming a teacher. The sibling `R2EGym-Verifier-Trajectories` (5,750 rows) does carry `rewards` and `docker_images`, and `R2EGym-TestingAgent-SFT-Trajectories` (2,281 rows) carries `exit_reasons`/`num_steps` — but neither names a teacher either — [HF API Verifier](https://huggingface.co/api/datasets/R2E-Gym/R2EGym-Verifier-Trajectories?blobs=true)
- The R2E-Gym paper abstract does not name the trajectory teacher model; it says only that the authors will open-source "agent trajectories" — [arXiv:2504.07164](https://arxiv.org/abs/2504.07164)

### Inferences
- For a commercial Python repair agent, `R2EGym-SFT-Trajectories` is the **highest-risk artifact in this inventory**: no license, no teacher attribution, no success labels, and no way to tell from the data whether a frontier model's outputs are embedded. Its 3,231 rows also contain no instance identifier, so you cannot even decontaminate it against SWE-bench Verified by joining on an id.
- The absence of a `resolved`/reward column plus the "SFT" name implies these are already success-filtered, but that is an inference from naming only, not documented.

### Gaps
- Teacher model, scaffold version, rollout count before filtering, success criterion, and license are all **genuinely undocumented**. I found no primary source for any of them. Report this as absent provenance, not as a research shortfall.

---

## Q6. Contamination and overlap with SWE-bench / SWE-bench-Verified

### Takeaway
[computed] **SWE-Gym is cleanly disjoint from SWE-bench** — zero shared instance_ids and, more importantly, **zero shared repositories** with either SWE-bench (dev+test) or SWE-bench_Verified. SWE-smith-py shares **4 of 131 repos** with SWE-bench but **0 with Verified**. **R2E-Gym is the contaminated one**: 3,139 of 8,101 rows (38.7%) come from `sympy` and `matplotlib`, both of which are SWE-bench_Verified repos, and **54 of its commit hashes appear verbatim as `base_commit` values in SWE-bench**. **None of the four cards contains any overlap or decontamination warning at all.**

### Cited Findings
- Reference sets [computed]: `SWE-bench/SWE-bench` main-branch parquet = 2,519 rows / 2,519 distinct instance_id / **18 repos** (`mwaskom/seaborn, psf/requests, sympy/sympy, sqlfluff/sqlfluff, matplotlib/matplotlib, pyvista/pyvista, pylint-dev/pylint, pallets/flask, scikit-learn/scikit-learn, pvlib/pvlib-python, pytest-dev/pytest, pydata/xarray, marshmallow-code/marshmallow, pydicom/pydicom, astropy/astropy, django/django, pylint-dev/astroid, sphinx-doc/sphinx`). `SWE-bench_Verified` = 500 rows / **12 repos** (`django/django` 231, `sympy/sympy` 75, `sphinx-doc/sphinx` 44, `matplotlib/matplotlib` 34, `scikit-learn/scikit-learn` 32, `pydata/xarray` 22, `astropy/astropy` 22, `pytest-dev/pytest` 19, `pylint-dev/pylint` 10, `psf/requests` 8, `mwaskom/seaborn` 2, `pallets/flask` 1).
- **SWE-Gym vs SWE-bench** [computed]: instance_id overlap with SWE-bench = **0**; with Verified = **0**; **repo** overlap with SWE-bench = **0**; with Verified = **0**. SWE-Gym's 11 repos are deliberately disjoint from SWE-bench's 18.
- **SWE-smith-py vs SWE-bench** [computed]: mapping SWE-smith's `repo` field (`swesmith/<owner>__<repo>.<commit8>`) back to `owner/repo` gives 131 repos, of which **4 appear in SWE-bench (dev+test)**: `marshmallow-code/marshmallow`, `pydicom/pydicom`, `sqlfluff/sqlfluff`, `pylint-dev/astroid`. **0 appear in SWE-bench_Verified.** Three of those four are large in SWE-smith-py: astroid 1,770 rows, pydicom 1,328, sqlfluff 1,293.
- **R2E-Gym-V1 vs SWE-bench_Verified** [computed]: matching R2E's bare `repo_name` against the basename of Verified's `owner/repo`, **3,139 of 8,101 rows (38.7%)** are from matching repos — driven by `sympy` (2,331 rows) and `matplotlib` (808 rows), which are Verified repos #2 and #4 by instance count.
- **R2E-Gym-V1 commit-level overlap** [computed]: joining `R2E-Gym-V1.commit_hash` against `SWE-bench.base_commit` yields **54 exact matches**. These are the same repository snapshots that SWE-bench tasks are built on.
- **Explicit overlap warnings on the cards: none.** [checked 2026-10-28/29] `SWE-smith-py`, `SWE-smith`, `SWE-smith-trajectories`, `SWE-Gym`, `SWE-Gym-Lite`, `R2E-Gym-V1`, `R2E-Gym-Subset`, `R2E-Gym-Lite` and `R2EGym-SFT-Trajectories` cards contain **no contamination, overlap or decontamination statement**. The SWE-smith GitHub README likewise has none — [SWE-smith README](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/README.md). The only adjacent statement is SWE-Gym's claim to be disjoint-by-construction, which my computation confirms.
- SWE-Gym's PASS_TO_PASS/FAIL_TO_PASS and SWE-bench's are the same schema, so the zero instance_id overlap is a meaningful, not accidental, result.

### Inferences
- **For a model you intend to evaluate on SWE-bench Verified**: SWE-Gym is safe at the repo level. SWE-smith-py is safe at the Verified repo level but you should still consider dropping its 4 SWE-bench repos (~4,400–5,300 rows) if you report SWE-bench full/Lite numbers. **R2E-Gym-V1 requires active decontamination**: dropping `sympy` and `matplotlib` removes 3,139 rows (38.7%) and leaves 4,962 rows from 11 repos.
- The 54 exact commit-hash matches between R2E-Gym-V1 and SWE-bench are the strongest contamination signal available, because they mean the agent may have seen the exact tree state that a Verified task starts from, including (via `expected_output_json`) the behaviour the Verified test asserts.
- SWE-smith's instance_ids are structurally un-collidable with SWE-bench's (`<owner>__<repo>.<commit8>.<bugtype>__<hash>` vs `<owner>__<repo>-<PR#>`), so instance_id overlap is trivially zero and is **not** evidence of cleanliness. Repo-level and commit-level checks are the ones that matter, and I report those.

### Gaps
- I could not compute file- or function-level overlap (e.g. whether a SWE-smith procedural bug lands in the same function a Verified task edits). That would require pulling and diffing gold patches at scale; I did not attempt it.
- For R2E-Gym the bare `repo_name` field makes `owner/repo` matching ambiguous in principle (a `pandas` could be a fork). I matched on basename, which can over-count; for `sympy` and `matplotlib` the owner is almost certainly the canonical one, so the 38.7% figure is best read as an upper bound that is very likely correct.

---

## Q7. Realistic achievable totals for the Python-only subset

### Takeaway
Realistic Python totals: **~39.5K usable SWE-smith-py tasks over 131 repos** (after dropping 11,437 empty problem statements), **2,438 SWE-Gym tasks over 11 repos**, **~4,962 decontaminated R2E-Gym tasks over 11 repos**. On the supervision side, the defensible supervised-assistant-token totals are roughly **30M tokens** for the exact SWE-agent-LM-32B recipe, **~71M** for all resolved `xml` trajectories, **~160M** if you take every `xml` row including failures, and **~10M** for R2E-Gym SFT. These token figures are **my estimates**, derived from measured character counts at ~3.5 chars/token.

### Cited Findings

**Distinct tasks and repositories (Python only)** [all computed]:

| dataset | distinct tasks | usable tasks (non-empty problem_statement) | distinct repos | gold patch ships | tests ship |
|---|---|---|---|---|---|
| `SWE-smith-py` | 50,908 | **39,471** | **131** | yes (`patch`) | F2P/P2P names only, no `test_patch` |
| `SWE-smith` (deprecated, all langs) | 59,136 | n/c | 222 | yes | same |
| `SWE-Gym` | 2,438 | 2,438 | **11** | yes | yes (`test_patch` + F2P/P2P) |
| `SWE-Gym-Lite` | 230 | 230 | 11 | yes | yes |
| `SWE-Gym-Raw` | 62,041 | n/c | 358 | yes | yes, but **unvalidated** |
| `R2E-Gym-V1` | 8,101 | 6,909 | **13** | inside `parsed_commit_content` | inside `expected_output_json` |
| `R2E-Gym-V1` minus sympy+matplotlib | 4,962 | n/c | 11 | " | " |
| `R2E-Gym-Subset` = `R2E-Gym-Lite/train` | 4,578 | 4,578 | 10 | " | " |

- **Non-overlapping union of Python *tasks*** [computed from the repo-level checks in Q6]: SWE-smith-py's 131 repos, SWE-Gym's 11 and R2E-Gym's 13 are largely distinct sets, but 10 of SWE-Gym's 11 repos also appear in SWE-smith-py (`dask/dask, conan-io/conan, python/mypy, pydantic/pydantic, getmoto/moto, Project-MONAI/MONAI, iterative/dvc, modin-project/modin, facebookresearch/hydra, pandas-dev/pandas`; only `bokeh/bokeh` is unique to SWE-Gym). So the combined **distinct-repository** count is far below 131+11+13 — roughly **131 + 1 + ~11 ≈ 143** Python repos, and the *task* counts remain additive because the task definitions differ (synthetic bug vs real PR vs back-translated commit).

**Supervised assistant-token estimates** (measured chars, then ÷3.5 chars/token — the division is **my estimate**, not a published figure):
- [computed, sampled] `SWE-smith-trajectories` mean `messages` string length, measured over whole shard `*-00001-of-00008.parquet`: **tool 107,410 chars/row (3,013 rows), xml 92,210 (3,260 rows), ticks 97,918 (3,229 rows)**. Assistant share measured over a 400-row sample of `tool-00004`: **23.3%** (mean 14,778 assistant chars at that shard's 63,458 total). Note the card's `dataset_info` implies a higher mean (`3,731,934,842 B / 24,100 rows` = 154,852 B/row for `tool`), so shard-to-shard variance is large; treat the per-row figures as ±50%.
- Derived estimates (assistant chars = 0.233 × mean total chars):
  - **SWE-agent-LM-32B recipe (4,954 xml traj)**: ≈ 4,954 × 21,485 = **106M assistant chars ≈ 30M assistant tokens**
  - **xml resolved-only (11,503 traj)**: ≈ 247M chars ≈ **71M assistant tokens**
  - **xml all rows (26,076)**: ≈ 560M chars ≈ **160M assistant tokens**
  - **tool all rows (24,100)**: ≈ 603M chars ≈ **172M assistant tokens**
  - **union of distinct traj_ids (49,897)**: order **300M assistant tokens**, but mixing three incompatible action serializations
- [computed, full scan] `R2EGym-SFT-Trajectories`: 3,231 rows, mean 47,294 total chars, **mean 11,077 assistant chars** (23.4% share) ⇒ 35.8M assistant chars ≈ **~10M assistant tokens**.
- `SWE-Gym/OpenHands-SFT-Trajectories`: 491 rows, `num_bytes` 31,805,636 ⇒ ~64,777 chars/row [metadata]. At a comparable ~23% assistant share that is ~7.3M assistant chars ≈ **~2M assistant tokens** — small enough that SWE-Gym's value is as an *environment*, not as an SFT corpus — [HF API](https://huggingface.co/api/datasets/SWE-Gym/OpenHands-SFT-Trajectories?blobs=true)

### Inferences
- Ranked by usefulness for a Python repo-repair agent: **(1) SWE-smith-py** — largest task pool, cheapest environments (131 images, ~200 GB), clean w.r.t. Verified, MIT, but synthetic bug distribution and 22.5% of rows need issue regeneration. **(2) SWE-smith-trajectories `xml` resolved-only** — the only large, licensed (MIT), success-labelled agent-trajectory corpus here, ~71M assistant tokens, teacher = Claude 3.5/3.7 Sonnet + GPT-4o. **(3) SWE-Gym** — small (2,438) but the most realistic problem statements (2,314 chars avg) and the only set with both `patch` and `test_patch`, and provably disjoint from SWE-bench. **(4) R2E-Gym** — mid-sized, Apache-2.0 for V1/Subset, but 38.7% repo-contaminated against Verified and only 13 repos. **(5) R2EGym-SFT-Trajectories** — avoid absent provenance clarification.
- The ~160–300M assistant-token headline figures should not drive a training budget: after deduplicating `traj_id`, dropping failures, and committing to a single action serialization, the honest number is **30–71M assistant tokens** from SWE-smith-trajectories plus ~10M from R2E-Gym SFT.

### Gaps
- Token counts are character-derived estimates. I did not run a real tokenizer (that would require downloading ~3 GB of parquet per split). Any figure above labelled "tokens" carries ±30% from the chars/token assumption alone, on top of the ±50% shard variance.

---

## Q8. Licensing: what restricts commercial or competition use

### Takeaway
Nothing in this inventory carries an explicit non-commercial or competition restriction. The real risks are the opposite kind — **absence of any license** on nine of the artifacts, and the fact that every dataset-card license is a claim about the *card*, not about the thousands of upstream repositories whose source code is embedded in the patches, problem statements, images and trajectories.

### Cited Findings
- MIT declared: `SWE-bench/SWE-smith-py`, `SWE-bench/SWE-smith`, `SWE-bench/SWE-smith-go`, `SWE-bench/SWE-smith-trajectories`, `SWE-Gym/SWE-Gym`, `SWE-Gym/OpenHands-SFT-Trajectories` — [HF API reads, 2026-10-28]. The SWE-smith code repo is also MIT: "MIT License / Copyright (c) 2025 John Yang" — [LICENSE](https://raw.githubusercontent.com/SWE-bench/SWE-smith/main/LICENSE)
- Apache-2.0 declared: `R2E-Gym/R2E-Gym-V1`, `R2E-Gym/R2E-Gym-Subset` — [HF API R2E-Gym-V1](https://huggingface.co/api/datasets/R2E-Gym/R2E-Gym-V1?blobs=true)
- **No license declared** (no `license` in cardData, no `license:*` tag): `SWE-bench/SWE-smith-java`, `-js`, `-ts`, `-rs`, `-cpp`, `-php`; `SWE-Gym/SWE-Gym-Lite`; `SWE-Gym/SWE-Gym-Raw`; `SWE-Gym/OpenHands-Sampled-Trajectories`; `SWE-Gym/OpenHands-Verifier-Trajectories`; `SWE-Gym/MoatlessTools-Sampled-Trajectories`; `R2E-Gym/R2E-Gym-Lite`; `R2E-Gym/R2EGym-SFT-Trajectories`; `R2E-Gym/R2EGym-Verifier-Trajectories`; `R2E-Gym/R2EGym-TestingAgent-SFT-Trajectories` — [HF API reads, 2026-10-28]
- `SWE-bench/SWE-smith-envs` (the Docker environment build artifacts) returns **`license: null`** from the GitHub API — [GitHub API](https://api.github.com/repos/SWE-bench/SWE-smith-envs)
- The SWE-smith paper's arXiv listing carries a **CC BY-SA 4.0** license for the *article*; no license is named there for the code, dataset or trajectories — [arXiv:2504.21798](https://arxiv.org/abs/2504.21798)
- **No competition or benchmark-use restriction** appears on any of the cards I read, and no non-commercial clause. [checked 2026-10-28/29]

### Inferences
- **A dataset-card license does not settle the underlying repository code's rights.** SWE-smith-py embeds code from 131 upstream GitHub repositories in `patch`, `problem_statement` and the Docker images; SWE-Gym embeds 11 repos' code including GPL-ish and weak-copyleft projects; R2E-Gym embeds 13 (`sympy` is BSD-3, `pandas` BSD-3, `matplotlib` PSF-like, `orange3` is **GPL-3.0**, `datalad` MIT, `moto` Apache-2.0). An MIT or Apache-2.0 card cannot relicense GPL-3.0 source that appears verbatim in a patch or inside a published image. For a commercial product, the per-upstream-repo audit is the real work and none of these publishers has done it.
- The teacher-model terms of service are a second, separate constraint that no card addresses. `SWE-smith-trajectories` is 73% Claude 3.7 Sonnet and 24% Claude 3.5 Sonnet output [computed]; `SWE-Gym/OpenHands-SFT-Trajectories` is GPT-4o + Claude 3.5 Sonnet output [publisher claim, project README]. An MIT card on the dataset does not waive the originating provider's output-use terms, and `R2EGym-SFT-Trajectories` does not even disclose whose outputs they are.
- The five license-less SWE-smith language variants are a practical blocker only if you need non-Python data; `SWE-smith-py` itself is MIT, so a Python-only plan avoids that gap entirely.

### Gaps
- I did not enumerate the upstream licenses of all 131 SWE-smith-py / 11 SWE-Gym / 13 R2E-Gym repositories. That is a required follow-up for commercial use and is beyond what the cards or APIs expose.
- Whether the SWE-smith Docker images on Docker Hub carry any license metadata is unverified (the manifest API returns layer digests and sizes, not license labels).
