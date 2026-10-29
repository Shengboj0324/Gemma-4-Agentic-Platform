# Other public SWE-agent SFT data sources (non-Nebius / non-NVIDIA-SWE-Hero / non-SWE-smith-Gym-R2E), emphasis on 2026

**Method and observation date.** All Hugging Face facts below were pulled from the anonymous HF APIs on **2026-10-29 (UTC)** — `GET /api/datasets?search=…`, `?author=…`, `GET /api/datasets/<id>?blobs=true` (for `sha` and summed `siblings[].lfs.size`), and `GET https://datasets-server.huggingface.co/size?dataset=<id>` (for row counts). Row counts marked "viewer" come from the dataset-viewer size endpoint; where that endpoint returned 0 rows, an error, or `viewer: false`, the number is either absent or a **publisher claim from the card** and is marked as such. 13 search terms × up to 100 results plus 34 author listings were de-duplicated to 875 candidate datasets; the ones below are the relevant residue. No HTTP 429 was encountered; three per-dataset viewer calls failed (noted inline).

---

## Q1. Which organisations published SWE-agent trajectory or executable-task datasets in 2025–2026 (systematic org sweep)?

### Takeaway
Beyond the already-covered families, the landscape splits into four clusters: (a) **NVIDIA's non-SWE-Hero trajectory lines** (`Open-SWE-Traces`, `SWE-Zero`, `Nemotron-Terminal-Corpus`) which are by far the largest permissively-licensed multi-scaffold corpora; (b) **Chinese-lab SWE post-training releases** (AweAI Scale-SWE/DeNovoSWE, SWE-Lego / Lego-X, Zhipu `zai-org` SWE-Dev + CC-Bench, InternLM SWE-Fixer, ByteDance-Seed Multi-SWE-*); (c) **Harbor-format task/trajectory ecosystems** (open-thoughts AgentTrove, Lego-X LegoFlow-SWE, FineEnvs repo2rlenv-*, laion openswe-*, harborframework, UnipatAI, OpenMOSS); and (d) **execution-free mid-training scale-ups** (AlienKevin SWE-ZERO-12M, ricdomolm mini-coder-trajs-400k). Several orgs on the checklist have **nothing relevant**: `all-hands` / `all-hands-ai` (do not exist as HF dataset orgs), `THUDM` (0 datasets; SWE-Dev moved to `zai-org`), `deepseek-ai` (2 datasets, none SWE), `mistralai` (4, none SWE), `moonshotai` (3, none SWE), `Salesforce` (63, none SWE-agent), `Qwen` (13; only `AgentWorldBench`, `CodeElo` — neither is repo repair), `allenai` (no SWE-agent trajectory sets; the relevant work sits under the personal account `hamishivi`), `bigcode` (93 datasets, all pretraining/commit/benchmark, no agent trajectories), ByteDance **Trae** (no public trajectory dataset; only a 95-download third-party `Trae1ounG/SWE-Touch`), Augment / Cognition-Devin (only 2024-era `OpenHandsCommunity/SWE-bench-devin-*` output dumps), Lingma SWE-GPT (**search for "lingma" returns zero HF datasets**), Co-PatcheR and SWE-Mirror (**zero HF datasets**; "SWE-Mirror" only matches an unrelated `alucent/mirror-*` re-upload family).

### Cited Findings — the genuinely relevant hits

Master table. `sha` is the main-branch revision observed 2026-10-29. "Repo bytes" = sum of `siblings[].lfs.size` (+ plain sizes) from `?blobs=true`.

| HF dataset id | main `sha` (2026-10-29) | Rows | Repo bytes | Card license | Multi-turn tool-use? | Failed trajs? | Gold patch / tests? | Docker? |
|---|---|---|---|---|---|---|---|---|
| `nvidia/Open-SWE-Traces` | `4fa4c2ae9afc6b397bc50391d43450c79993c138` | 1,138,945 (viewer; v1.0 151,219 / v1.1 263,226 / v1.2 235,391 / v2.0 489,109) | 97,939,491,044 (~97.9 GB, 487 files) | `cc-by-4.0` | Yes — `messages` + `tools` JSON schemas | Yes (`resolved` 0/1/-1) | Gold patch in `metadata.reference_patch.patch`; no test lists | No (tasks point at Scale-SWE / SWE-rebench-V2 images) |
| `AlienKevin/SWE-ZERO-12M-trajectories` | `44e028077c55e7255c328516c8bd76080fbb3840` | 12,290,800 (viewer) | 35,972,855,768 (~36.0 GB, 1,233 files) | `apache-2.0` | Yes — mini-swe-agent v1 bash loop | Yes, overwhelmingly | No | No (execution-free by design) |
| `open-thoughts/AgentTrove` | `b395a4307a2bc9950a90dc899438f149e115fc60` | 1,696,847 (viewer) | not captured (gap) | `apache-2.0` | Yes — terminus-2 / ShareGPT via Harbor | Yes (`reward` 0.0/1.0) | No (reward only) | Generated in Harbor sandboxes; images not shipped |
| `ricdomolm/mini-coder-trajs-400k` | `90b240e09807bbfdead1a18c0a861e2c2d20fa14` | 396,515 (viewer) | card: 29.8 GB uncompressed / 9.40 GB download | `mit` | Yes — mini-swe-agent | Yes (`verified` bool) | `patch` column | No (SWE-smith images upstream) |
| `nvidia/SWE-Zero-openhands-trajectories` | `7b3cd106d00f60918e722d33a1d74bc67072a7ea` | 318,115 (viewer) | 12,207,173,274 (~12.2 GB) | `cc-by-4.0` | Yes — OpenHands, `tool_calls` | Yes (execution-free, unverified) | `model_patch` only | No |
| `nvidia/Nemotron-Terminal-Corpus` | `a1667c4ffdadea02a89bffe4f1bb7ca2ff19f8d9` | 366,154 (viewer: dataset_adapters 226,313 / easy 44,809 / medium 89,343 / mixed 5,689) | not captured | `cc-by-4.0` | Yes | Card implies filtered | No | Terminal sandboxes, not shipped |
| `SALT-NLP/SWE-chat` | `202b071f18e03c79df5a7287565ce2ebc5ee7756` | **unknown — viewer returns HTTP 401** | 46,989,343,640 (~47.0 GB, 21,675 files) | `odc-by` | presumed (tags `agent`, `traces`) | unknown | unknown | unknown |
| `AweAI-Team/Scale-SWE` | `d8db20390a936bbda9c96d88b97cc4778dff1481` | 20,181 (viewer) | 983,661,478 | card text: CC BY 4.0 (no `license` field in metadata) | Tasks, not trajectories | n/a | Yes — `patch`, `f2p_patch`, `f2p_script`, `FAIL_TO_PASS`, `PASS_TO_PASS` | **Yes — `image_url` per instance** |
| `AweAI-Team/Scale-SWE-Distilled` | `c14ce2130f494812fef907f4afc81d8e33990805` | 71,498 (viewer) | 4,715,079,587 | card text: CC BY 4.0 | Yes | unknown | task fields retained | via upstream `image_url` |
| `AweAI-Team/Scale-SWE-Distilled-DeepSeek-v4-Pro-High-41k` | `cf6eb6188051a85fa34ebd91cae1956352f0e78d` | **viewer 0 — publisher claim ~41k from the repo name** | 6,442,623,956 | card text: CC BY 4.0 | Yes | unknown | — | — |
| `AweAI-Team/DeNovoSWE-Trajectory-Filtered` | `cf1442b9b22ba8a88d472aec399e60ee40a7795d` | **viewer 0 — publisher claim "11k filtered from 34k DeepSeek-v4-High trajectories"** | 4,617,122,531 | `cc-by-4.0` | Yes (max 500 turns, 256k ctx) | Raw variant keeps them | `test_patch`, `unit_test` | `image_url` |
| `AweAI-Team/DeNovoSWE-Trajectory-Raw` | `779e725994adf678bb5c7849a7d833c3f04bb2c5` | viewer 0 | 24,686,826,491 (~24.7 GB) | `cc-by-4.0` | Yes | **Yes (unfiltered)** | — | — |
| `Lego-X/LegoFlow-SWE` | `4a795d06051d3445b0e0372f10b616bc4a8d2d77` | 9,767 trajectories (viewer: opencode 5,014 / openhands-sdk 4,753) + 5,000 Harbor tasks ×2 prompt variants | 3,679,863,397 (100,000 files) | **none declared** | Yes — `tools` + `messages` + `reasoning_content` | Yes (only 1,430 / 1,350 have `reward = 1`) | Yes — `solution/fix.patch`, `tests/test.sh` | **Yes — `environment/Dockerfile` per task** |
| `Lego-X/SWE-Lego-Real-Data` | `879c96b91dfa321b4d1c621d149a9200f8a1d118` | 18,036 (viewer; 5k resolved + 13k unresolved parquet) | 1,422,779,773 | `apache-2.0` | Yes — OpenHands v0.53.0 | **Yes, explicitly (13k unresolved)** | derived from SWE-rebench | No |
| `Lego-X/SWE-Lego-Synthetic-Data` | `3e745545b07516f8772d2b7ecc5d3bbee84c012c` | 11,471 (viewer) | 622,399,606 | `apache-2.0` | Yes | unknown | synthetic | No |
| `Lego-X/SWE-Review-Traj` | `587eaa89ca868365dcd84c480a87e7bde5bdb508` | 8,914 (viewer) | 596,892,458 | `apache-2.0` | Yes — OpenHands-SDK review sessions | No (decision-correct only) | verified against test suites | No |
| `Lego-X/Terminal-Lego-Traj-Deepseek-V3-2-15k` | `922c2fcb019854911fc05eb1a208d2685ac6e006` | 14,834 (viewer) | 540,500,559 | **none declared** | Yes (terminal) | unknown | No | No |
| `internlm/SWE-Fixer-Train-110K` | `9e3f1366be2c9a1a230d243b4008354436685501` | 115,406 (viewer) | 1,471,208,381 | `mit` | **No — retrieve-then-edit, single-turn** | n/a | editing targets | No |
| `internlm/SWE-Fixer-Train-Editing-CoT-70K` | `0859c3e13375e488519a79d8d004d1698cddb6e8` | 69,752 (viewer) | 3,670,255,342 | `mit` | No (CoT editing) | n/a | — | No |
| `zai-org/SWE-Dev-train` | `5888e5864886590ead78a69b6e60490a0d89a594` | 20,147 (card: sft 17,871 + rft 2,276) | 350,923,615 | **none declared** | Yes — OpenHands-based, `input` messages | Yes (`reward`, `f2p_pass`, `f2p_count`) | f2p counts | No |
| `zai-org/CC-Bench-trajectories` | `792c6d3221db4d9ed475702ed61a176dd8948152` | 260 (viewer) | 44,146,189 | `mit` | Yes (Claude-Code-style) | unknown | No | No |
| `ByteDance-Seed/Multi-SWE-bench_trajs` | `9180bb0c633e4580fc8f74629ac6a47b8582543f` | **unknown — viewer returns HTTP 500**; 321 files | 4,725,948,398 | `cc0-1.0` | Yes — leaderboard agent trajectories + logs | Yes (all leaderboard runs) | upstream benchmark | upstream images |
| `ByteDance-Seed/Multi-SWE-RL` | `9777648932daa214ba18c70c81e85821b5836f32` | viewer 0 rows (jsonl per repo, 131 files) | 23,868,863,679 (~23.9 GB) | `other` (card: CC0 + per-repo compliance) | Tasks/RL data, not trajectories | n/a | `fix_patch`, `test_patch`, f2p/p2p | per-repo build data |
| `II-Vietnam/Agentic-Multi-SWE-RL` | `ab06012b476e77798603e183791c89e2077b8d39` | 7,526 (viewer; card 23.85 GB uncompressed) | 5,398,004,435 | **none declared** | Task instances | n/a | `fix_patch`, `test_patch`, `f2p_tests`, `p2p_tests`, `s2p_tests`, `n2p_tests` | **Yes — `docker` column** |
| `JetBrains-Research/SWE-TaskFlow-SWE-Bench-Pro-Trajectories` | `a5ec6ad8428715a689ee62cf7cef82334773c958` | 25,200 (viewer: 3 configs × 8,400) | 6,266,779,960 | `other` (unspecified) | Yes — every model call + shell command + output | **Yes** (`failed`, `terminal_agent_failure` statuses) | verifier reward + final patch | Harbor-run, images not shipped |
| `JetBrains-Research/agent-trajectories-swe-bench-test-minus-verified` | `dd79e2540cab4c0cc2c5bab6ea71ddd7ac6c1775` | 1,785 (viewer) | 40,006,015 | `mit` | Yes — OpenAI messages format | `resolved` column is all-null; `exit_status` present | gold patch used by the router, not shipped | No |
| `OpenHands/CodeScout_Training_Rollouts` | `65a3599683b901be691621f9eab7cd932a9a2c5f` | 54,845 (viewer: CodeScout_14B 39,040 / 4B 15,805) | 608,515,145 | **none declared** | Yes — `chat_messages` with `tool_calls` | reward-graded (localization F1) | **No — localization rewards only** | No |
| `OpenHands/SWE-rebench-code-search` | `b4e0432105eef4bf7b2f4cfad41b9167af3f418c` | 17,591 (viewer) | 85,033,098 | none declared | localization task data | n/a | No | No |
| `hamishivi/swerl-tmax-15k` | `2e297abb28a9b22fe67063742f8134a745e35505` | 14,601 (viewer) | 49,016,931 | **none declared** | RL prompts + `env_config.image` (Harbor) | n/a | `ground_truth` | **image name per row** |
| `TMaxxx/TMax-15K-Harbor` | `48a77eb0b017606c643ed905f96db41672914798` | 14,601 (viewer) | — | none declared | Harbor tasks | n/a | yes | yes |
| `TIGER-Lab/SWE-Next-SFT-Trajectories` | `e378a60ddd7050fe9519a31a4d41d4872eeec6ac` | 3,693 (viewer; from 2,308 execution-grounded tasks) | — | `mit` | Yes — ShareGPT `system/user/assistant/tool` | No (expert rollouts) | tasks are execution-grounded | upstream SWE-Next |
| `FineEnvs/repo2rlenv-swe-next` | `a6b1edf56ccadb722f34c40dde05944517fc7efe` | **100 Harbor tasks** (viewer disabled, HTTP 501) | 217,102,712 (18,412 files) | `other` / `mixed-source-licenses` | Tasks | n/a | `solution/solve.sh`, `tests/test.sh` | **Yes — `environment/Dockerfile`** |
| `FineEnvs/repo2rlenv-swe-gen` | `f0035f039f4cef878c53789886502447e21e37b3` | task bundles (viewer 501) | 258,983,481 (15,385 files) | `other` / `mixed-source-licenses` | Tasks | n/a | yes | Yes |
| `FineEnvs/repo2rlenv-pr-runtime` | `abade24929575ad10549108f51c681c96b32a667` | viewer HTTP 500 | 7,901,550 | `apache-2.0` | Tasks | n/a | yes | Yes |
| `laion/openswe-harbor-tasks` | `87fe59354cfa0ccb560398ea0ef5f183fc78cfcd` | 45,320 (viewer) | 680,224,637 | **none declared; README is "Entry not found"** | Harbor tasks | n/a | unknown | Harbor |
| `laion/openswe-tasks-patched-v5` | `f8d308cee050b32721401af2cceb47c4d34de0f6` | 45,320 (viewer) | 696,365,452 | none declared | Harbor tasks | n/a | unknown | Harbor |
| `whitecircle/swe-rebench-v2-glm-5.1-pi-agent-successful-traces` | `5c7255ede80994b117fbdd8bd28d43da227beb53` | 7,777 (viewer) | — | **none declared** (region:eu) | Yes | **No — successful only** | — | — |
| `netpreme/coding_agent_traces` | `d56ae0d0bc80f3663a7a61a38c4ee60c26ce7b67` | 1,962 (gpt-oss-120b-pro 731 / gpt-oss-120b-verified 500 / opus-pro 731) | — | `mit` | Yes | partly | — | — |
| `mondk/agentic-coding-traces` | `9bc4c723af77b2326b00e9efc7fc656131fd02f3` | 417 (viewer) | 295,118,031 | `apache-2.0` (aggregator-asserted) | Yes (`<think>` + tool turns) | unknown | No | No |
| `swesynth/SWE-Synth_Moatless-SFT-Trajectories` | `a2e8a9961a8209dbb01a801ee8d50852b8a61522` | 3,018 (viewer) | — | **none declared** | Yes — Moatless Tools scaffold | unknown | upstream SWE-Synth | SWE-Synth images |
| `SWE-bench-Live/SWE-bench-Live` | `b51a86422e10cfd403beb4773e5a2947953e36ec` | 3,688 (test 1,000 / lite 300 / verified 500 / full 1,888) | 241,145,312 | `mit` | Eval tasks | n/a | Yes — `patch`, `test_patch`, FAIL_TO_PASS, PASS_TO_PASS, `test_cmds`, `log_parser` | **Yes — instance-level `image_key`** |
| `SWE-bench-Live/MultiLang` | `3638632e8153a10ca422c1022bed79023084b5c9` | 1,077 (c 111, cpp 142, go 138, js 108, rust 171, java 160, ts 111, cs 136) | 410,955,101 | `mit` | Eval | n/a | yes | yes |
| `PrimeIntellect/Scale-SWE-Verified` | `2c29b67e0ea4d7819f60d8a10d7475a7ad89ccd6` | 17,202 (viewer) | 218,074,727 | `cc-by-4.0` | Tasks (verifiers env) | n/a | gold-patch-validated | upstream `image_url` |
| `nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1` | `d2b67746ca0087e73c4675b56bcc139b99354963` | 50,308 (viewer) | 5,101,900,981 | `cc-by-4.0` | RL env (`nemo-gym` tag), not SFT traces | n/a | — | nemo-gym |
| `nvidia/Nemotron-SFT-Agentic-v4` | `a4593a26ea83a700035bbe0ec1edc9ef3810669d` | viewer 0 | 18,881,629,804 (~18.9 GB) | **`openmdw-1.1`** | Agentic SFT (mixed domains) | unknown | — | — |
| `nvidia/Nemotron-SFT-SWE-v3.5` | `ad64129216649f86179a759a6df65d0975c5df07` | 5,115 (viewer) | — | `cc-by-4.0` | Yes | unknown | — | — |

Teacher models and scaffolds (from the cards, observed 2026-10-29):

- `nvidia/Open-SWE-Traces` — five scaffolds: **OpenHands, SWE-agent, mini-swe-agent, OpenCode, Claude-Code**. Teachers by version: v1.0 MiniMax-M2.5 + Qwen3.5-122B; v1.1 DeepSeek-V4-Flash-0731 + Qwen3.6-27B; v1.2 Qwen3.8-27B (xhigh); v2.0 Qwen3.8-Flash-Next (xhigh/medium/low). Task sources are **only** `AweAI-Team/Scale-SWE` and `nebius/SWE-rebench-V2`. v1.0 was pruned from 207k to 151k after removing "trajectories exhibiting git hacking behaviors". — [card](https://huggingface.co/datasets/nvidia/Open-SWE-Traces/raw/main/README.md), [EMNLP 2026 Findings](https://aclanthology.org/2026.findings-emnlp.131/)
- `nvidia/SWE-Zero-openhands-trajectories` — OpenHands; teacher **Qwen3-Coder-480B-A35B-Instruct**; 118,092 issues → 318,115 trajectories; issue statements from SWE-Gym, SWE-Gym-Raw, R2E-Gym-Subset, **`internlm/SWE-Fixer-Train-110K`**, SWE-rebench. — [card](https://huggingface.co/datasets/nvidia/SWE-Zero-openhands-trajectories/raw/main/README.md), [arXiv 2604.01496](https://arxiv.org/abs/2604.01496)
- `AlienKevin/SWE-ZERO-12M-trajectories` — teacher **`ricdomolm/mini-coder-1.7b`**, mini-swe-agent v1 format, 100 rollouts per PR, temp 1.0, **15-turn cap**, 32,768-token budget; 122,908 unique PRs, 3,222 repos, 16 languages, 111.06 B tokens; seeded from `nebius/SWE-rebench-V2-PRs`. — [card](https://huggingface.co/datasets/AlienKevin/SWE-ZERO-12M-trajectories/raw/main/README.md)
- `open-thoughts/AgentTrove` — **219 source datasets**, terminus-2 format, all generated with **Harbor**; teachers include GLM-4.6, GLM-4.7, GPT-5.1-Nano, GPT-5-mini, GPT-5, GPT-OSS-120B, Kimi K2.0 Thinking, Kimi-2.5, MiniMax M2.0, Qwen3-Coder-480B, Gemini-2.5-Flash, GPT-4o. Repo-repair-relevant sources: `swesmith`, `r2egym`, `SWEGym`, `defects4j`, `Inferred Bugs`, `exp_rpt`. Most rows are **not** repo repair (nl2bash, freelancer, taskmaster, codeforces, puzzles, stack_exchange). — [card](https://huggingface.co/datasets/open-thoughts/AgentTrove/raw/main/README.md)
- `AweAI-Team/Scale-SWE` family — publisher claims mining **6M+ PRs / 23,000+ repositories**, releasing 20,000 executable Python instances ("currently the largest Real Executable open-source SWE dataset") and **71k DeepSeek-v3.2 distillation trajectories (3.5B tokens)**; claimed 64% SWE-bench-Verified from Qwen3-30B-A3B-Instruct. Later `…-DeepSeek-v4-Pro-High-41k` uses DeepSeek v4-Pro. — [card](https://huggingface.co/datasets/AweAI-Team/Scale-SWE/raw/main/README.md), [arXiv 2602.09892](https://arxiv.org/abs/2602.09892)
- `Lego-X/LegoFlow-SWE` — teacher **GLM-5.2**, scaffolds **OpenHands SDK** and **OpenCode**; 5,000 Harbor tasks (c 889, cpp 370, go 761, java 725, js 372, **python 716**, rust 639, ts 504). Publisher claims a 1k-sample SFT reaches **70.2 SWE-bench Verified / 48.8 Pro / 57.0 Multilingual** from Qwen3.5-35B-A3B-Base, vs 64.4/46.9/56.0 for the same recipe run on `nebius/SWE-rebench-V2` instances — i.e. the publisher's own ablation puts LegoFlow instances +5.8 Verified over SWE-rebench-V2. — [card](https://huggingface.co/datasets/Lego-X/LegoFlow-SWE/raw/main/README.md)
- `Lego-X/SWE-Lego-Real-Data` — 18k real **Python** GitHub issues; teacher **Qwen3-Coder-480B-A35B-Instruct** with **OpenHands v0.53.0**; split into `resolved` (5k) and `unresolved` (13k) parquet files; built on `nebius/SWE-rebench`. Publisher claims SWE-Lego-Qwen3-32B = 52.6% Pass@1 Verified. — [card](https://huggingface.co/datasets/Lego-X/SWE-Lego-Real-Data/raw/main/README.md), [paper 2601.01426](https://huggingface.co/papers/2601.01426)
- `Lego-X/SWE-Review-Traj` — teacher **GLM-5 (thinking)** via OpenHands-SDK; patch generators GLM-5-FP8 (3,056), Qwen3-Coder-30B-A3B (2,991), Qwen3-30B-A3B-Instruct-2507 (2,867); 14,156 candidate PRs → 8,914 decision-correct review trajectories. — [card](https://huggingface.co/datasets/Lego-X/SWE-Review-Traj/raw/main/README.md), [arXiv 2607.06065](https://arxiv.org/abs/2607.06065)
- `JetBrains-Research/agent-trajectories-swe-bench-test-minus-verified` — **GT-aware lookahead agent**: each turn samples from both `gpt-5.2` and `gpt-5-mini`, a `gemini-3-pro-preview` router (with access to the ground-truth patch) picks the better step. "This 'best-of-two' selection is oracle-informed (access to the ground-truth patch during routing)". — [card](https://huggingface.co/datasets/JetBrains-Research/agent-trajectories-swe-bench-test-minus-verified/raw/main/README.md)
- `JetBrains-Research/SWE-TaskFlow-SWE-Bench-Pro-Trajectories` — 4 models (GPT-5.6 Luna, GPT-5.6 Terra, GPT-5.4 mini, Gemini 3.7 Flash) × 3 prompt conditions × 3 runs × 700 SWE-Bench Pro tasks = 25,200 rows, Harbor-scored, with `cost_usd` and full shell command logs. — [card](https://huggingface.co/datasets/JetBrains-Research/SWE-TaskFlow-SWE-Bench-Pro-Trajectories/raw/main/README.md), [arXiv 2610.09633](https://arxiv.org/abs/2610.09633)
- `ricdomolm/mini-coder-trajs-400k` — teacher **Qwen3-Coder-30B-A3B-Instruct**, **mini-swe-agent**, tasks from **SWE-smith**. — [card](https://huggingface.co/datasets/ricdomolm/mini-coder-trajs-400k/raw/main/README.md)
- `zai-org/SWE-Dev-train` — OpenHands-based pipeline (issue tracking, code localization, test-case generation); publisher claims SWE-Dev-7B/32B = 23.4%/36.6% Verified. Mirrors `THUDM/SWE-Dev-train` (the `THUDM` org now returns 0 datasets). — [card](https://huggingface.co/datasets/zai-org/SWE-Dev-train/raw/main/README.md), [arXiv 2506.07636](https://arxiv.org/abs/2506.07636)
- `TIGER-Lab/SWE-Next-SFT-Trajectories` — 3,693 ShareGPT multi-turn examples from expert rollouts on 2,308 execution-grounded tasks synthesized from real merged PRs. — [card](https://huggingface.co/datasets/TIGER-Lab/SWE-Next-SFT-Trajectories/raw/main/README.md), [arXiv 2603.20691](https://arxiv.org/abs/2603.20691)
- `OpenHands/*` LocAgent/CodeScout line (all `sha`-pinned 2026-03-17): `SWE-rebench-code-search` 17,591 rows, `SWE-Gym-code-search`, `SWE-smith-py-code-search`, `CodeScout_Training_Rollouts` 54,845 rows, `CodeScout_Eval_Rollouts`, plus `SWE-bench_{Pro,Verified,Lite}-locagent`. The reward schema is `multilevel_localization_f1_reward` / `file_reward` / `module_reward` / `entity_reward` — **localization, not patching**. — HF API + `OpenHands/CodeScout_Training_Rollouts` card

### Orgs checked with nothing relevant (negative results, all observed 2026-10-29)
- `author=all-hands`, `author=all-hands-ai` → **0 datasets** (the live org is `OpenHands`, 11 datasets, all listed above).
- `author=THUDM` → 0 datasets. `author=deepseek-ai` → 2, none SWE. `author=mistralai` → 4, none SWE. `author=moonshotai` → 3, none SWE.
- `author=Qwen` → 13; only `Qwen/AgentWorldBench` (1,054 dl) and `Qwen/CodeElo` (367 dl) are code/agent, neither is repo repair.
- `author=Salesforce` → 63 datasets, no SWE-agent set.
- `author=allenai` → 500 listed, no SWE-agent trajectories; the Ai2-adjacent work is `hamishivi/swerl-tmax-{10k,15k}` and `wAI-org/swerl-tmax-15k-*` variants (`swerl-tmax-15k-rubric-gpt-5-6-sol`, `-solvable-gpt-5-6-terra`, `-hardened-prefilter`, `-repairs-gpt-5-6-sol`).
- `author=facebook` → 127; only `facebook/collaborative_agent_bench` (61 likes) and `neural_code_search`, neither repo-repair trajectories. **No public HF dataset for Code World Model's 3M agentic trajectories** was found.
- `author=bigcode` → 93; `commitpack`/`commitpackft`/`the-stack*`/`bigcodebench` — pretraining and benchmark data, **no agentic sets**.
- search `lingma` → **0 results**; search `Co-PatcheR` → **0 results**; search `SWE-Flow` → only `FineEnvs/repo2rlenv-swe-flow` (a HF re-implementation, 3,368 dl); search `SWE-Mirror` → only `alucent/mirror-*` re-uploads of other people's datasets.
- `open-thoughts/AgentTrove-v2` → **HTTP 401** (does not exist publicly / gated).
- Amazon: `AmazonScience/SWE-PolyBench` (6,714 dl), `_Verified` (382 rows, `sha b3fca77b637379f0c01ad86d18753a7ac1998b53`, MIT), `_500`, `massive-agents` — all **evaluation**, no trajectories.

### Inferences
- The 2026 trajectory supply is dominated by a handful of "teacher × scaffold" sweeps over a **small set of shared task pools** (SWE-rebench/-V2, Scale-SWE, SWE-smith, SWE-Gym, R2E-Gym). The genuinely *new instance supply* in 2026 comes from AweAI Scale-SWE (20k executable Python, publisher-claimed 5,200 repos), Lego-X LegoFlow (5,000 Harbor tasks, 716 Python), laion openswe (45,320 tasks), and SWE-bench-Live's monthly additions.
- Harbor has become the de facto task container format for 2026 releases (AgentTrove, LegoFlow-SWE, FineEnvs, laion openswe, UnipatAI, OpenMOSS, TMax, hamishivi swerl-tmax). A pipeline that can ingest Harbor task dirs unlocks many sources at once.

### Gaps
- `SALT-NLP/SWE-chat` (14,698 downloads, 141 likes, 47.0 GB, 21,675 files, `odc-by`, arXiv 2604.20779) is **gated**: the viewer returns HTTP 401 and `GET /raw/main/README.md` returns "Access to dataset SALT-NLP/SWE-chat is restricted." Row count, teacher, scaffold and whether failed trajectories ship could not be verified anonymously. Given its size it is the single largest unresolved unknown in this inventory.
- `open-thoughts/AgentTrove` total repo bytes not captured (only row count).
- `ByteDance-Seed/Multi-SWE-bench_trajs` row count unobtainable — viewer HTTP 500.
- `AweAI-Team/*` trajectory datasets return viewer 0 rows (non-parquet layout); their 41k / 11k / 34k figures are **publisher claims from card text and repo names only**.
- `laion/openswe-harbor-tasks` has **no README** ("Entry not found") and no declared license; its provenance and teacher are unknown.
- I did not verify the SWE-bench leaderboard's open-source entries page or arXiv listings directly; org/paper attributions above come from the dataset cards themselves.

---

## Q2. Which of these are NOT repository-repair data (do not mistake for usable trajectories)?

### Takeaway
A large share of high-download "SWE"- or "trajectory"-named datasets are competitive programming, localization-only, computer-use, eval-only, or outright homonyms. The list below is explicit so a reader does not misclassify them.

### Cited Findings
**Named like SWE data, but not repo-repair trajectories** (all observed 2026-10-29 via HF API/cards):
- `internlm/SWE-Fixer-Train-110K` + `-Editing-CoT-70K` — **single-turn retrieve-then-edit**, not agentic tool-use. Card: "a streamlined retrieve-then-edit pipeline with two core components: a code file retriever and a code editor". Useful as *task/issue source* (NVIDIA SWE-Zero used it that way), not as trajectories.
- `OpenHands/CodeScout_*`, `OpenHands/*-code-search`, `OpenHands/*-locagent`, `adityasoni17/SWE-bench_Pro-locagent*`, `czlll/LocAgent_index_data` — **fault localization only**; rewards are file/module/entity F1, no patch.
- `Hcompany/trajectories` (11,185 dl, 41 likes, `apache-2.0`, `sha ede2a362c99ddba0d03f439c47a0b8fea6abae22`) — **computer-use**, 7,366 Holo4 trajectories on OSWorld / OSWorld-2 / AndroidWorld / AutomationBench / PinchBench. Zero repo repair.
- `elemental-tasks/model-trajectories` (13,851 dl) — **not trajectories at all**; schema is `model, checkpoint, tokens_B, task, task_type, metric, value` — 6,985 rows of eval metrics from "The Implicit Curriculum Hypothesis" (arXiv 2604.08510).
- `AweAI-Team/BeyondSWE` (500 rows, test split) and `AweAI-Team/DeNovoSWE` (3,675) — **repository generation from scratch / doc2repo**, not bug repair; DeNovoSWE rows are `document` → whole-repo reconstruction.
- `Lego-X/SWE-Review-Traj` / `SWE-Review-Bench` — **code review** decisions, adjacent but a different task head.
- `ScaleAI/SWE-Atlas-QnA` (124 rows), `TIGER-Lab/SWE-QA-Pro-Bench` (1,683 dl) — **repository question answering**.
- `Fsoft-AIC/SWE-EVO` (48 rows, 17.2 GB, `apache-2.0`, `sha 77310c70d3648d6815f6a7555ecc492bc28c44ec`) — 48-instance **feature-evolution eval**, not training data.
- `DeepCommit-ai/SWE-Milestone-data` (`sha 3500478e740d42583277c2658aa7729eb36e10f4`, MIT) — **eval only**: 7 repositories, 98 graded milestones, 5 languages (only scikit-learn is Python); metadata + SRS docs + dependency DAGs.
- Eval benchmarks, not SFT data: `ScaleAI/SWE-bench_Pro` (1,424 rows: default 642 / hard 51 / v1 731), `swe-bench-promax/SWE-Bench-ProMax` (170), `opencompass/SWEBench-Pro-Verified` (1,225 dl), `SWE-bench-Live/*`, `AmazonScience/SWE-PolyBench*`, `OpenMOSS-Team/SWE-bench-Science` (119 rows, MIT, Harbor), `UnipatAI/Monthly-SWEBench-2026-0{3,4,5}` (100 rows each, MIT, Harbor), `internlm/WildClawBench-Trajectories` (720 rows — *eval* traces), `guildlm/go-swe-bench-v0` (Go), `SWE-bench/SWE-bench_Multilingual` (300 rows), `SWE-bench/SWE-bench_Multimodal`, `ByteDance-Seed/Multi-SWE-bench{,_mini,-flash}`, `cerebras-nidhip/SWE-bench-JS`.
- Single-turn code instruct / competitive programming / completion / pretraining (never repo repair): `nvidia/OpenCodeInstruct` (43,055 dl), `nvidia/OpenCodeReasoning{,-2}`, `nvidia/Nemotron-Pretraining-Code-v{1,2,3}`, `nvidia/Nemotron-RL-coding-competitive_coding`, `ByteDance-Seed/Code-Contests-Plus`, `Qwen/CodeElo`, `bigcode/commitpack{,ft}` (single-turn commit diffs), `bigcode/the-stack*`, `bigcode/bigcodebench`, `JetBrains-Research/lca-*` (code completion/bug localization), `Fsoft-AIC/RepoExec`, `PrimeIntellect/verifiable-coding-problems`, `allenai/tulu-3-sft-personas-code`.
- `rmems/long-horizon-coding-trajectories` — synthetic `goal / plan / outcome` records from Grok-4.6, **not executed trajectories**; card: "The raw, uncurated payload is now published under `data/raw/`… it is **not training-ready**."
- Pure homonyms that pollute "swe"/"patch" searches: `NeuroTec/SWEC_iEEG_Dataset`, `wildflow/sweet-corals`, `danish-foundation-models/swedish-dynaword`, `1aurent/PatchCamelyon`, `rttss/ota-patches`, robot "sweep" datasets, `webarena-x/*`, `mlfoundations-cua-dev/osworld-trajectories`, `YuvrajSingh9886/androidlife-trajectories`, `*/browsecomp-trajectories`.
- `aisa-group/PostTrainBench-Trajectories` (85,981 downloads — the 4th-most-downloaded hit in my sweep) and `tonychenxyz/sweeperbench-traces` / `zlab-princeton/SWEeper-Bench-traces` were **not inspected**; treat as unclassified rather than relevant.

### Inferences
- Download count is a poor relevance signal here: four of the ten most-downloaded "trajectory" matches are computer-use, eval-metric tables, or homonyms.

### Gaps
- `aisa-group/PostTrainBench-Trajectories`, `tonychenxyz/sweeperbench-traces`, `zlab-princeton/SWEeper-Bench-traces`, `rdesai2/swe-marathon`, `Charly-chan/SWE-Game`, `Dorothydu/swe-dev-eval`, `MaxDevv/real-pi-coding-agent-traces-sessions` (license `other`, viewer 0 rows) were found but not characterised — ran out of budget.

---

## Q3. Licensing — restrictions on commercial use, competition use, or trained models

### Takeaway
The large permissive core is `cc-by-4.0` (NVIDIA, AweAI, PrimeIntellect), `apache-2.0` (AgentTrove, SWE-ZERO-12M, SWE-Lego) and `mit` (SWE-Fixer, SWE-bench-Live, TIGER-Lab, JetBrains MIT sets). I found **no card imposing a non-commercial, competition, or trained-model-output restriction** among the datasets I read. The real risks are different: several of the most useful sets declare **no license at all**, two use bespoke/unspecified terms, and one asserts a self-imposed "no model-weight update" policy.

### Cited Findings
- **`rmems/long-horizon-coding-trajectories`** declares `license: apache-2.0` in metadata but the card contradicts it: "> **Rights & intended use:** legacy public **research corpus / portfolio artifact**. Hosted frontier-model outputs are research-only inputs under project policy…: `intended_use: research_only`, `project_training_policy: blocked`. **Not training data for any model-weight update.**" It also carries a `research-only` tag. — [card](https://huggingface.co/datasets/rmems/long-horizon-coding-trajectories/raw/main/README.md)
- **`ByteDance-Seed/Multi-SWE-RL`** metadata says `license: other`; the card says: "The dataset is licensed under CC0, subject to any intellectual property rights in the dataset owned by Bytedance. The data is adapted from the listed open source projects; **your use of that data must comply with their respective licenses.** licenses of all the repositories collected by us are listed below, with an overall low license risk." The card then enumerates the per-repository licenses. — [card](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-RL/raw/main/README.md)
- **`FineEnvs/repo2rlenv-swe-next` / `-swe-gen`** declare `license: other`, `license_name: mixed-source-licenses`, pointing at a per-dataset `LICENSES.md`; the card adds "Repository and seed license notices remain attached to their original materials" and disclaims quality: "An `exported` task is a generation artifact… an export is not an accepted-quality claim." Quality labels: `{"unverified": 100}`. — [card](https://huggingface.co/datasets/FineEnvs/repo2rlenv-swe-next/raw/main/README.md)
- **`JetBrains-Research/SWE-TaskFlow-SWE-Bench-Pro-Trajectories`** declares `license: other` with no `license_name` or `license_link` in `cardData` — terms unresolved. Its tasks derive from SWE-Bench Pro, whose own terms I did not verify.
- **`nvidia/Nemotron-SFT-Agentic-v4`** uses **`openmdw-1.1`** (Open Model Data Weights 1.1), not CC-BY — different obligations from the rest of the NVIDIA line.
- **No license field at all** (`cardData.license` absent) on, notably: `Lego-X/LegoFlow-SWE`, `Lego-X/Terminal-Lego-Traj-Deepseek-V3-2-15k`, `zai-org/SWE-Dev-train`, `AweAI-Team/Scale-SWE`, `AweAI-Team/Scale-SWE-Distilled`, `AweAI-Team/Scale-SWE-Distilled-DeepSeek-v4-Pro-High-41k`, `OpenHands/CodeScout_Training_Rollouts`, `OpenHands/SWE-rebench-code-search`, `hamishivi/swerl-tmax-15k`, `TMaxxx/TMax-15K-Harbor`, `laion/openswe-harbor-tasks`, `laion/openswe-tasks-patched-v5`, `II-Vietnam/Agentic-Multi-SWE-RL`, `whitecircle/swe-rebench-v2-glm-5.1-pi-agent-successful-traces`, `swesynth/SWE-Synth_Moatless-SFT-Trajectories`, `ScaleAI/SWE-bench_Pro`, `ScaleAI/SWE-Atlas-QnA`. For AweAI the card body says "This project is licensed under the CC BY 4.0 License" even though the HF metadata field is empty.
- **`NVIDIA`** sets state affirmatively: "This dataset is ready for commercial/non-commercial use" (`Open-SWE-Traces`, `SWE-Zero`, `SWE-Hero`), with `Open-SWE-Traces` adding "Each user is responsible for checking the content of datasets and the applicable licenses and determining if suitable for the intended use." `SWE-Zero` narrows source repos: "We use MIT, Apache-2.0, BSD-2-Claude, and BSD-3-Clause licenses only."
- **Teacher-model terms are a separate, unaddressed layer.** Several high-value sets are distilled from hosted proprietary models whose provider terms typically restrict using outputs to train competing models — e.g. `JetBrains-Research/agent-trajectories-swe-bench-test-minus-verified` (gpt-5.2 / gpt-5-mini / gemini-3-pro-preview) and `SWE-TaskFlow-*` (GPT-5.6 / Gemini 3.7), and `mondk/agentic-coding-traces`, which is an `apache-2.0`-tagged aggregation of third-party Claude-Code and Codex trace dumps (`armand0e/claude-fable-5-claude-code`, `AletheiaResearch/Kimi-K3-Codex`, …). No card in this group discusses that layer.
- **A card license never settles the underlying repository code's rights.** The data in every repo-repair set embeds verbatim source from the target repositories under their own licenses (GPL, LGPL, MPL, AGPL appear in the Multi-SWE-RL repo list, which includes `php/php-src`, `redis/redis`, `bitcoin/bitcoin`). Only NVIDIA SWE-Zero states an explicit permissive-only source filter; `Open-SWE-Traces` instead ships a per-row `license` field with the repo's SPDX identifier, which is the right mechanism to filter on.

### Inferences
- For a commercially-safe Python repair SFT mix, the defensible core is: `nvidia/Open-SWE-Traces` (filter `license` column to MIT/Apache/BSD), `nvidia/SWE-Zero-openhands-trajectories`, `open-thoughts/AgentTrove` (filter `original_source` to swesmith/r2egym/SWEGym and `original_teacher` to open-weights GLM/Qwen/Kimi/MiniMax), `AlienKevin/SWE-ZERO-12M-trajectories`, `ricdomolm/mini-coder-trajs-400k`, `Lego-X/SWE-Lego-Real-Data`, `TIGER-Lab/SWE-Next-SFT-Trajectories`, `PrimeIntellect/Scale-SWE-Verified`.
- The AweAI and Lego-X trajectory sets are the best quality-per-token on published ablations but carry the weakest license metadata — worth a direct request to the publishers.

### Gaps
- Did not read `FineEnvs/.../LICENSES.md`, the `ScaleAI/SWE-bench_Pro` terms, or the `JetBrains .../SWE-TaskFlow-*` "other" license text.

---

## Q4. Contamination — cards that warn about SWE-bench / SWE-bench-Verified overlap

### Takeaway
No card I read carries an explicit "this may be contaminated with SWE-bench Verified" warning. Instead, the 2026 cards document contamination *controls*. The one dataset built directly on SWE-bench instances is deliberately scoped to exclude Verified.

### Cited Findings
- `JetBrains-Research/agent-trajectories-swe-bench-test-minus-verified` is scoped by construction: "Full multi-turn agent trajectories collected from the **SWE-bench Test minus Verified** split (i.e., SWE-bench Test instances that are **not** part of SWE-bench Verified). Intended for SFT of agent models on coding tasks." — [card](https://huggingface.co/datasets/JetBrains-Research/agent-trajectories-swe-bench-test-minus-verified/raw/main/README.md). Note the trajectories are still *oracle-informed* (the router saw the gold patch), which is a different leakage axis.
- `SWE-bench-Live/SWE-bench-Live`: "Thanks to our automated dataset curation pipeline, we plan to update SWE-bench-Live on a monthly basis to provide the community with up-to-date task instances and support rigorous and **contamination-free** evaluation." Its initial release was 1,319 instances "created after 2024"; the `lite` and `verified` splits are frozen and new issues land in `full` (50/month). — [card](https://huggingface.co/datasets/SWE-bench-Live/SWE-bench-Live/raw/main/README.md)
- `Lego-X/SWE-Review-Traj`: "Three models generate patches for ~6,000 SWE-rebench instances (**no overlap** with SWE-Review-Bench to prevent data leakage)."
- `Lego-X/LegoFlow-SWE` documents anti-hack controls rather than contamination: an anti-hack prompt that "prohibit[s] looking up related issues, pull requests, patches, commits, discussions, or ready-made solutions"; "**Git information removal:** remove the original repository history and remote information before the agent starts"; and network restriction to the inference endpoint only. It warns that the shipped `tasks-anti-hack/` variant "adds prompt instructions only; downloading it does not enable Git cleanup or network isolation."
- `nvidia/Open-SWE-Traces` v1.0 was reduced from 207k to 151k trajectories after "we cleaned up trajectories exhibiting **git hacking** behaviors" — reward hacking, not benchmark overlap.
- `SWE-bench-Live` states the evaluation protocol an agent must follow, which is relevant for anyone training on its instances: "During a rollout, the agent may access only the `problem_statement` field… It must not access any other fields, such as `hint`, `FAIL_TO_PASS`, or `test_patch`."
- **Transitive-overlap risk worth flagging to the writer:** `nvidia/Open-SWE-Traces` instances come *only* from `AweAI-Team/Scale-SWE` and `nebius/SWE-rebench-V2`; `AlienKevin/SWE-ZERO-12M-trajectories` from `nebius/SWE-rebench-V2-PRs`; `Lego-X/SWE-Lego-Real-Data` and `SWE-Review-Traj` from `nebius/SWE-rebench`; `nvidia/SWE-Zero` from SWE-Gym / R2E-Gym / SWE-Fixer-110K / SWE-rebench; `ricdomolm/mini-coder-trajs-400k` from SWE-smith. All of those task pools are in the sibling researchers' scope — so these datasets add *trajectories and scaffold diversity*, not new instances, and inherit whatever Verified overlap their pools have.

### Inferences
- Contamination screening for this corpus should be done on `repo` + `base_commit` against SWE-bench Verified, not trusted to cards — none of the 2026 trajectory cards publishes an overlap count.

### Gaps
- No card quantified SWE-bench-Verified overlap. The `SALT-NLP/SWE-chat` card is inaccessible, so its contamination posture is unknown.

---

## Q5. Ranked shortlist — which sources actually add distinct tasks or repositories

### Takeaway
Only four sources add large volumes of *new instances or repositories* beyond the already-covered pools; the rest add teacher/scaffold diversity over shared pools, which is still valuable but is a different kind of addition.

### Cited Findings

**Tier 1 — adds distinct task instances / repositories, permissive, large**
1. **`AweAI-Team/Scale-SWE` + `PrimeIntellect/Scale-SWE-Verified`** — 20,181 executable Python instances with per-instance `image_url`, gold patch, developer `f2p_patch` *and* synthetic `f2p_script`, FAIL_TO_PASS/PASS_TO_PASS; publisher claims 5,200 repositories mined from 6M+ PRs. PrimeIntellect's fork is gold-patch-validated down to **17,202** (removed 892 excluded images, 2,061 `gold_patch_failure`, 15 `noop_pass`, 11 `stable_infra_failure`), `cc-by-4.0`. Plus 71,498 + ~41k distilled DeepSeek trajectories. This is the single biggest *new* executable Python pool outside the covered families.
2. **`Lego-X/LegoFlow-SWE`** — 5,000 Harbor tasks with Dockerfile + `fix.patch` + tests (716 tagged Python, rest 7 other languages) and 9,767 GLM-5.2 trajectories across two scaffolds. Publisher's own controlled ablation shows its instances beat SWE-rebench-V2 by +5.8 SWE-bench-Verified points under an identical 1k-sample recipe. No declared license — the main blocker.
3. **`laion/openswe-harbor-tasks` / `openswe-tasks-patched-v5`** — 45,320 Harbor tasks each. Largest unexamined task pool found; **no README, no license**, provenance unknown. Worth one hour of diligence given the size.
4. **`SWE-bench-Live` family** — `SWE-bench-Live` 3,688 rows across splits (164+ repos, all post-2024, instance-level Docker images, MIT) + `MultiLang` 1,077 + `Windows` + `OS-bench` + `repo-build-test-benchmark`. Small but the only *continuously refreshed* permissively-licensed Python pool, and the cleanest contamination story.

**Tier 2 — adds trajectory/scaffold/teacher diversity over already-covered pools, at scale**
5. **`nvidia/Open-SWE-Traces`** — 1,138,945 trajectories, 97.9 GB, `cc-by-4.0`, five scaffolds (OpenHands / SWE-agent / mini-swe-agent / OpenCode / Claude-Code), four teacher generations, gold patch + model patch + `resolved` flag + per-row repo SPDX license. The highest-value single download in this inventory; instances overlap SWE-rebench-V2 + Scale-SWE.
6. **`open-thoughts/AgentTrove`** — 1,696,847 rows, `apache-2.0`, 219 sources, ~12 teachers, Harbor/terminus-2, `reward` per row. Needs filtering: a minority of rows are repo repair (swesmith, r2egym, SWEGym, defects4j, InferredBugs).
7. **`AlienKevin/SWE-ZERO-12M-trajectories`** — 12,290,800 rollouts / 111.06 B tokens, `apache-2.0`, 122,908 PRs over 3,222 repos and 16 languages. Explicitly a **mid-training** corpus: execution-free, unverified, 15-turn cap, low submission rate. Card reports Marin-8B 0% → 5.3% SWE-bench-Verified at 1.1 B tokens, and argues (citing NemotronTerminal Table 7: no filtering 12.4% vs complete-only 6.74% vs success-only 5.06%) that keeping failures is better.
8. **`nvidia/SWE-Zero-openhands-trajectories`** — 318,115 trajectories over 118,092 issues, `cc-by-4.0`, permissive-source-only filter.
9. **`ricdomolm/mini-coder-trajs-400k`** — 396,515 mini-swe-agent trajectories, MIT, with `patch` and `verified` columns.
10. **`Lego-X/SWE-Lego-Real-Data`** — 18,036 Python issues with OpenHands trajectories, `apache-2.0`, **ships resolved and unresolved as separate files** (5k / 13k) — the cleanest failed-trajectory split available.
11. **`AweAI-Team/DeNovoSWE-Trajectory-Raw` / `-Filtered`** — 24.7 GB raw / 4.6 GB filtered DeepSeek-v4-High long-horizon trajectories (500-turn, 256k context), `cc-by-4.0`. Task is doc→repo generation, so complementary rather than repair.

**Tier 3 — small but distinct and clean**
12. `JetBrains-Research/SWE-TaskFlow-SWE-Bench-Pro-Trajectories` 25,200 rows (license `other`; four proprietary teachers; full command logs and costs).
13. `zai-org/SWE-Dev-train` 20,147 (17,871 SFT + 2,276 RFT) with reward and f2p counts.
14. `OpenHands/CodeScout_Training_Rollouts` 54,845 — localization-only, useful as an auxiliary head.
15. `II-Vietnam/Agentic-Multi-SWE-RL` 7,526 instances with a `docker` column and five test categories (f2p/p2p/s2p/n2p/fixed).
16. `whitecircle/swe-rebench-v2-glm-5.1-pi-agent-successful-traces` 7,777 (GLM-5.1, successful-only).
17. `Lego-X/SWE-Lego-Synthetic-Data` 11,471; `Lego-X/Terminal-Lego-Traj-Deepseek-V3-2-15k` 14,834.
18. `TIGER-Lab/SWE-Next-SFT-Trajectories` 3,693 over 2,308 tasks, MIT.
19. `hamishivi/swerl-tmax-15k` / `TMaxxx/TMax-15K-Harbor` 14,601 Harbor RL tasks with per-row image.
20. `FineEnvs/repo2rlenv-*` — ~100-task Harbor bundles each across 10+ recipes (`swe-next`, `swe-gen`, `swe-flow`, `pr-runtime`, `pr-diff`, `commit-runtime`, `r2e`, `cve-patches`, `tmax`, `scaler`); small, fully executable, well-documented provenance, mixed licenses.
21. `swesynth/SWE-Synth_Moatless-SFT-Trajectories` 3,018 — the only **Moatless Tools** scaffold trajectories found; 2025-era, no license.
22. `internlm/SWE-Fixer-Train-110K` 115,406 — **use as an issue/task source, not as trajectories**; already consumed that way by NVIDIA SWE-Zero.

### Inferences
- Rough distinct-instance accounting beyond the covered pools: Scale-SWE ~20.2k Python (17.2k gold-validated) + LegoFlow ~5k multi-language (~0.7k Python) + laion openswe ~45.3k (unverified) + SWE-bench-Live ~3.7k + MultiLang ~1.1k + II-Vietnam ~7.5k + SWE-Next ~2.3k ≈ **85k new task instances**, of which maybe 40–45k are Python once laion's provenance is settled.
- Rough distinct-trajectory accounting: Open-SWE-Traces 1.14M + AgentTrove ~1.70M (partially repo-repair) + SWE-ZERO-12M 12.3M (mid-training grade) + SWE-Zero 318k + mini-coder 397k + SWE-Lego 18k + Scale-SWE-Distilled ~112k + LegoFlow 9.8k + SWE-TaskFlow 25.2k ≈ **16M rollouts**, heavily dominated by one execution-free mid-training corpus.

### Gaps
- `SALT-NLP/SWE-chat` (47.0 GB, gated) could change this ranking materially and could not be assessed.
- `laion/openswe-*` (45,320 tasks each) ranking is provisional — zero documentation.
- AweAI trajectory row counts are publisher claims; the viewer returns 0 rows for all three.
