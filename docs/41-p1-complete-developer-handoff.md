# P1 complete developer handoff: implementation, evidence and remaining work

**Snapshot: October 19, 2026. Project: ZenithSync, Gemma 4 developer agent. P1 is incomplete.**

This is the entry document for a developer with no conversation context. It supersedes older status summaries, not immutable experimental receipts. Read it together with the linked inventories: those enumerate individual source files, selected tasks, and retained artifacts that cannot usefully be repeated inside one narrative. Credentials are deliberately excluded. This is an implementation and evidence handoff, not a claim that the system is production-ready or that every historical experiment passed.

The original P1 meant model intake, serving and initial agent inference. The user's subsequent scope expanded it to dependable training infrastructure, realistic task data, validation and preparation for three 50-million-token candidate runs. Some of that work belonged to later phases in the original plan. **Do not declare P1 complete by reverting to its narrower definition.** The prior estimate of roughly 60% completion was an engineering judgment, not an earned-value calculation or a percentage of acceptance gates passed.

## 1. Read this first

1. Read sections 2–5 for the current state and architecture.
2. Read sections 6–10 before interpreting training, numerical or evaluation results.
3. Read sections 11–14 before restoring assets or spending GPU money.
4. Use the appendices to locate every retained file and the current task-specific review.
5. Consult [the implementation journal](40-p1-implementation-journal.md) for chronological attempts, including failures and superseded corpora. It is intentionally historical; a statement that work was pending there may have been superseded later.

| Handoff component | Contents |
|---|---|
| [Code catalog](p1-handoff/code-catalog.md) | All 371 enumerated implementation, script, test, configuration, dependency and candidate files; source links and available descriptions |
| [Code inventory](p1-handoff/code-inventory.json) | Paths, sizes, materialization flags and hashes where locally readable under the size limit |
| [Symbol inventory](p1-handoff/symbols.json) | 323 class/function definitions extracted from materialized Python files, with signatures, descriptions and line numbers; **not a complete symbol inventory of placeholder files** |
| [Current task ledger](p1-handoff/current-task-ledger.md) | Every one of the 51 selected tasks, repository, input/target counts and review decision |
| [Detailed task ledger](p1-handoff/current-task-ledger.json) | Per-task manifest bindings, history identity, synthetic metadata and full current review rationale |
| [Evidence directory catalog](p1-handoff/evidence-catalog.md) | 4,421 directory/file-prefix groups, including unsuccessful and superseded work |
| [Artifact file inventory](p1-handoff/artifact-files.tsv) | 33,410 retained file entries: 23,835 evidence, 9,297 artifacts, 278 reproduction; logical/allocated bytes and placeholder/symlink flags |
| [Existing document map](p1-handoff/document-map.md) | All earlier planning/research/implementation documents and their headings |
| [Inventory report](p1-handoff/inventory-report.json) | Recomputed counts, corpus manifest hash, parsing failures and inventory limits |
| [Inventory generator](p1-handoff/build_inventory.py) | Rebuilds these appendices without opening large artifact payloads or hydrating placeholders |

The inventories describe this checkout, including uncommitted/untracked work. A Git clone alone does **not** reproduce it. Artifact enumeration establishes existence, not integrity, semantics, completeness of cloud backup or permission to delete a file. Historical receipts and manifests remain the detailed evidence. Some files are File Provider placeholders: they have names and logical sizes but no resident contents. This snapshot deliberately did not hydrate the full repository.

## 2. Authoritative current checkpoint

| Item | State |
|---|---|
| Adopted goal | A trainable Gemma-powered repository engineering agent, using the official competition runtime/tool contract |
| Base model | `gemma-4-31b-it-qat-w4a16-ct`, locally referenced v2 download; quantized base, separate adapters |
| Current corpus | **Corpus072**, superseding Corpus071 as the selected corpus |
| Tasks / declared repository groups | **51 / 50**; both PennyLane tasks share a group |
| Input tokens / shifted supervised targets | **954,733 / 262,593** |
| Training status | **All 51 quarantined; zero training-approved examples** |
| Split status | Provisionally train; all selected tasks development-exposed; no unseen confirmation cohort frozen |
| Corpus admission | Four gates remain null: rights, split, runtime, task alignment. Task-review evidence exists, but it has not been turned into full corpus admission |
| Latest recorded full local regression | **671 passed, zero skips, Torch enabled, 28.042 seconds**; historical recorded run, not rerun for this documentation update |
| Real full-model training executed | One bounded H100 compatibility update on a **24-token fixture**, followed by adapter reload checks |
| Real-corpus / large-campaign training | Not started; no 50M-token candidate completed or initiated |
| Learned performance improvement | Not demonstrated; no sound claim of superiority over Codex, Claude or another strong agent |
| GPU decision | Keep the Pod stopped until the next admission/preflight and a fresh bounded session decision |
| Cloud freshness | No live Runpod, R2, DigitalOcean or Cloudflare state was queried during this handoff update |

Current corpus manifest SHA256:

`42da2d372f908d00b72a3f7d89af9b5fa082f8caeb8a4307bd77cfc363a2de75`

Content identity:

`c081880c71b9f78ffb4fdcf319d0959e8d7dfcb39878b8ac06f510f2d088f103`

The current corpus payload contains 103 files, 10,578,444 bytes, with recorded R2 publication and independent restoration. The integration package contains 33 files, 198,454 bytes. All 51 current task reviews accepted their bounded behavioral evidence; all 51 leave-one-out coverage controls rejected an incomplete review set. The smallest remaining context margin is 210 tokens after reserving 8,192 tokens under a 32,768-token limit. These are qualification measurements, not evidence of sufficient training diversity or GPU capacity.

See [current readiness](39-p1-current-readiness.md), [Corpus072 integration](../evidence/data/corpus072-integration-001/), and [payload verification](../evidence/data/corpus072-payload-001-verification/verification.json).

## 3. Product and implementation boundaries

The intended product accepts a repository task, reads relevant code, calls supported tools, makes a patch, checks the result, and returns an evidence-backed submission. Gemma supplies model decisions. Training aims to improve those decisions using properly qualified trajectories. Host-side contracts validate data, budgets, artifacts and claims; they do not replace model competence or prove arbitrary patches correct.

What exists today is a substantial foundation: official-contract integration, model inspection, serving probes, native tool/history capture, task replay and grading, data provenance and admission machinery, tokenization/masking, bounded optimization/checkpoint infrastructure, and durable artifact workflows. It is not yet an industrial autonomous platform with a trained, benchmarked agent, service-level guarantees, frontend, multi-tenant deployment or demonstrated specialist advantage.

Earlier product directions and reproduction hypotheses in documents 13–18 were investigated and discarded or withheld. They are preserved as research history, not current feature commitments. Research novelty, leaderboard performance and competitiveness remain hypotheses requiring experiments.

## 4. Architecture and interfaces

The working data path is:

`pinned source → task/source snapshot → native history or explicitly synthetic capture → baseline/reference/candidate grading → behavioral review → tokenizer/mask audit → quarantined corpus → four-gate admission → indexed loader → exact schedule → supervised training worker → adapter/checkpoint → serving → independent evaluation`

The path through quarantined corpus and local training-infrastructure validation exists. The edge into **admitted real-corpus GPU training** is blocked. Adapter reload compatibility has been demonstrated in a small full-model fixture; general serving integration, sustained optimization and independent model comparison are not thereby established.

| Component | Code families and responsibilities | Important boundary |
|---|---|---|
| Core contracts / packaging | `contracts`, `archive`, `task_intake`, `offline_resources`, `__main__` | Structural preflight does not replace the official compiler or hidden grader |
| Model and serving | `model_intake`, `quantized_layout`, `architecture_layout`, `serving`, `gpu_memory`, `inference_probe`, `inference_capture`, `tool_diagnostic` | Measured loading/inference is not long-run capacity or content fidelity |
| Conversation / representation | `conversation`, `gemma_trajectory`, `trajectory_import`, `training_masks`, `training_batch`, `harness_context` | Native roles, tool results, terminal submission and context limits matter |
| Source reconstruction | `source_*`, `resource_replay_binding`, `session_resource_*` | Pin source and dependencies; never silently mix checkout and installed packages |
| Replay / amendments | `replay_*`, `mini_*`, `rebench_grade_evidence` | Preserve original observations, corrections, failed attempts and provenance |
| Test result interpretation | `pytest_*`, `junit_controls`, `go_test_controls`, `mocha_controls`, `maven_*`, `static_controls`, `matrix_*`, `legacy_matrix_probe` | Parser acceptance is not proof that the task behavior is correct |
| Synthetic / issue contract | `synthetic_admission`, `v2_synthetic_admission`, `issue_contract` | Synthetic, reference-informed work is not an independent model success |
| Corpus admission | `training_corpus`, `corpus_credentials`, `review_coverage`, `splits`, `issue_similarity`, `qualification_sampling` | Positive task review alone cannot open training |
| Optimization / scheduling | `gemma_training`, `corpus_optimization`, `corpus_training`, `corpus_run`, `training_schedule`, `training_pilot`, `training_fixture`, `action_training` | Reduced tests and experimental action supervision are not a trained release |
| State / operational bounds | `training_state`, `training_rng`, `training_session`, `adapter_checkpoint`, `optimizer_checkpoint`, `checkpoint_storage`, `process_supervisor`, `deadline` | Process deadlines do not stop cloud billing |
| Storage / evidence | `artifacts`, `object_store`, `transfer_evidence`, `container_cleanup`, `session_report`, `probe_receipt` | Verify restoration before cleanup; scoped receipt validity only |
| Evaluation | `evaluation`, `submission_reconciliation` and source/task grading modules | Development exposure invalidates an unseen-confirmation claim |

Exact paths, module descriptions and script names are in the code catalog. Consult source rather than guessing CLI flags. Requirements locks are separate for serving, evaluator compatibility, tokenizer, R2 and the PEFT supplement; this is not a single interchangeable Python environment.

## 5. Official runtime and initial GPU qualification

The official-contract audit recorded 524 Kaggle metadata entries and pinned `swegemma 0.2.7`, `adk-submission 0.2.12`, `adk-eval-core 0.1.0`, and `google-adk 1.36.1`. The official starter compiled with nine tool placeholders plus AgentTool; compilation alone was not inference. Real Linux integration exercised 25 bound tool calls with network disabled, 4 GiB memory and two CPUs. AMD64 execution on the ARM64 development machine was emulated, so timing is not representative of production Linux.

Operational constraints discovered include `agent.yaml` discovery, required LlmAgent instruction, bounded include resolution, archive traversal rejection, and a conservative strictly-below-3-GiB submission limit. Task timing and aggregate runtime are different budgets. Baseline patch-diff fallback to HEAD must be understood when grading. Graph similarity searches known symbols/embeddings; the three deterministic float64 cosine checks did not demonstrate unrestricted natural-language retrieval.

Model intake recorded eight files totaling 23,297,590,856 bytes, 2,009 tensors, 410 quantized text projections and 779 unquantized tensors. Publisher listing names/sizes matched; absent publisher hashes, that is not independently authenticated publisher-byte identity. Numeric scans established their specified finite/positive-scale predicates, not global mathematical correctness of the model.

Historical GPU evidence includes:

- Six expected parser fixtures. One real repair attempt produced 11 malformed writes; a later attempt produced 29 schema-valid calls. Schema validity did not guarantee task success.
- A real tool read of an unpredictable marker and continuation demonstrated model/tool interaction.
- One repair exhausted 40 turns. A later repair produced a 439-byte patch. Under the original network diagnostic, baseline was 320 passed / 2 failed / 2 skipped and candidate 321 / 1 / 2. With the recorded HTTP-compatible fixture, candidate was 322 passed / 2 skipped and the target baseline failure remained. This is a scoped local resolution.
- Requests grading initially imported an installed package instead of edited checkout code. A source-origin guard and diagnostic override were added. Official hidden-environment parity remains unresolved.
- H100 validation exposed repeated Unicode content-fidelity failures; do not describe the model/tool path as fully reliable.
- Model loading measured 19.63 GiB; one serving configuration reported 43.23 GiB available KV memory and 47,216 cache tokens. The estimated 8.90 concurrency figure was not measured concurrency; actual configured maximum sequences was one.
- Startup 84.03 seconds and two completion measurements, 2.290692886 and 0.854144563 seconds, are isolated observations, not latency percentiles or a throughput forecast.

Sources: [official contract audit](22-official-contract-audit.md), [GPU report](27-p1-gpu-validation-report.md), [requirements audit](28-p1-requirements-audit.md), [H100 report](30-p1-h100-validation.md), [acceptance checklist](26-p1-acceptance-checklist.md).

## 6. Training design and mathematical contracts

### 6.1 Causal labels and weighted optimization

For example i, token IDs and labels have matching lengths. Non-supervised labels use `-100`; supervised positions come from approved assistant spans. Position zero supplies no shifted target. Define `n_i = sum(1[label[t] != -100], t=1..T_i-1)`. Input-token count and target-token count are different quantities.

If `L_i` is the mean cross-entropy over those n_i targets, the intended objective for one scheduled update is:

`L = (sum_i n_i L_i) / (sum_i n_i)`.

Streaming each example's backward pass with weight `n_i / N`, where N is the exact update target count, reproduces that objective's gradient under the stated deterministic, uncoupled-forward assumptions. Averaging example means equally would overweight short examples. The implementation does not concatenate examples across attention boundaries. Zero/invalid counts, nonfinite losses/gradients and unexpected trainable/frozen-state changes are rejection conditions.

Reduced float64 comparisons checked losses, gradients and AdamW updates to 1e-12; reduced deterministic checkpoint tests checked exact restoration. These do not prove bitwise equivalence on quantized full-model GPU kernels. Dropout, batch-dependent behavior, device arithmetic and nondeterministic kernels require separate consideration. There is no qualified distributed training path: initialized distributed execution is rejected. AMP scaling, clipping and a learning-rate schedule are not implemented as a qualified general training stack.

A failed forward may change buffers or RNG state even if no optimizer step occurs. Restore a known checkpoint after a failed transaction; “no step” does not mean all state remained pristine.

### 6.2 LoRA and the full-checkpoint fixture

The adapter parameterization is `W' = W + (alpha/r) BA`; for a projection from a inputs to b outputs, the adapter has `r(a+b)` trainable parameters. The qualified fixture uses r=4, alpha=8, zero dropout, exact selection of 410 text projections and **30,607,360 adapter parameters**. Base parameters remain frozen; adapters are stored separately.

The H100 compatibility probe used eager BF16, `run_compressed=false`, non-reentrant gradient checkpointing, disabled model cache and PEFT 0.21.2. It performed **one update on 24 actual tokens** under a configured maximum of 64, then verified frozen state and adapter reload logits. It did not run real-corpus optimization, a long sequence, a full optimizer-resume campaign or serving adapter qualification. Memory readings of 67,071 and 67,231 MiB were sampled observations, not measured peaks.

### 6.3 Corpus/index and schedule invariants

`IndexedCorpus` validates manifest/audit/token-array bindings before access and rehashes fetched examples. Its working representation is metadata plus the largest loaded example, rather than the whole corpus. File-size bounds are not a universal RSS bound. Current qualification limits include 16 MiB manifest/example bounds, 1 GiB corpus/session bounds and a 512 MiB checkpoint bound.

Corpus072 schedule validation used nine planned updates, ten valid resume boundaries and ten invalid cursor controls. Every task appeared exactly once with zero schedule overshoot. Those counts describe this qualification schedule, not the future 50M-token schedule. Resumption must preserve manifest/source identity, optimizer state, RNG state and the exact data cursor; changing any of them starts a different experiment.

### 6.4 Statistics and generalization

For independent Bernoulli outcomes, Hoeffding planning gives `n >= ceil(log(2/alpha)/(2 epsilon^2))`; alpha=.05 and epsilon=.05 require 738 observations. For independent paired differences in [-1,1], the corresponding bound is `ceil(2 log(2/alpha)/epsilon^2) = 2952`. These are conservative planning calculations, not sample-size claims about this corpus. Repository-related tasks and correlated cases do not automatically satisfy independence.

All 51 selected tasks have been inspected during development. Their outcomes cannot estimate unseen improvement without an appropriately independent, prospectively frozen cohort. Repeated tokens and repeated repository cases do not manufacture independent evidence. A result against a reference patch also does not prove the reference expresses the issue correctly.

Detailed implementations and limitations: [corpus integration](38-training-corpus-integration.md), [full-checkpoint qualification](32-full-checkpoint-gpu-qualification.md), and the individual training modules/tests in the inventory.

## 7. Data, provenance and corpus history

Corpus072 replaces only the selected Emcee record from Corpus071; the other 50 records are preserved. Corpus071 had 954,476 inputs and 262,577 targets. Earlier corpora and their receipts remain historical evidence, not interchangeable current manifests. Always bind a review or optimization run to the exact manifest hash.

Every current task is listed in the two task ledgers. For each, preserve repository/base identity, source snapshot, issue, native history, tool observations, patch, baseline/reference/candidate outcomes, parser profile, token audit, review rationale and synthetic designation. Missing synthetic metadata does not prove an untouched human/model trajectory. Teacher/replayed, corrected and assistant-authored trajectories must remain distinguishable.

Important changes and limitations that an aggregate pass count would conceal:

| Task/family | Established result | Boundary still relevant |
|---|---|---|
| LensKit312 | Explicit issue-contract solution for implicit and explicit NDCG; four contract cases pass; 6,969 high-precision comparison cases, maximum recorded absolute error about 1.11e-16 | This intentionally differs from the old reference normalization. Legacy suite candidate 78 passed / 3 failed versus baseline 81 passed. Full 367-node ledger: baseline 331 passed / 34 skipped / 2 failed; candidate 328 / 34 / 5. Two shared Hypothesis failures remain. No blanket full-suite pass |
| Emcee295 | Current native004 capture reads source/tests before edit, has two status calls and a 415-byte transpose patch; 112 probability values agree for memory/HDF5 backends | Reference checks 19 passed / 2 persistent failures; original sampler tests 11 passed / 10 failed, including eight old-axis expectations and two pytest API failures. Correlated seed cases do not establish MCMC convergence. Prior native003 ordering/status gap preserved |
| Jsons86 | Native002, four literal-form issue cases repaired; finite/legacy/publisher comparisons retained | Assistant/reference-informed synthetic work; no independent model performance claim |
| Mypy extensions47 | Replacement005: 84 messages, 40 calls, 22,634 input / 7,559 target tokens, 1,942-token margin; source matches the reviewed derivative | Earlier char-offset correction superseded; two initial source reads truncated, four generated diagnostic files and three post-edit reads classified separately |
| Dynaconf413 | Native002 source/notice bindings and root snapshot recovered | Canonical/mirror URL distinction and unresolved full-repository behavior remain recorded |
| Csaps3 | 54 rational oracle systems and 1,791 entries tested the zero-smoothing weighted-affine least-squares relation | Two-point metadata is separate; finite cases do not prove all floating-point inputs |
| Runpy17 | Five logging methods AST-match 131 observed source lines; BSD attribution preserved in the observation | Full BSD text, separate SQL filter and other embedded/dependency notice coverage remain open |
| ptvsd3.0.0 | Seven observed runtime files match recovered release material and notices | This covers that dependency, not every dependency in every history |

LensKit's concrete distinction: for the documented truth/recommendation example, the issue-contract normalization yields 8/9 rather than approximately .73443. The oracle assumes the stated nonnegative relevance, unique items, positive ideal denominator and contiguous ranks. `issue_contract.py` only permits declared, supported finite changes; undeclared changes still block. It does not authorize silently rewriting test failures or granting training approval.

Current full-history screening covers all 51 records. Configured credential-pattern scans found zero matches in the inspected nested histories and decoded token content. Thirteen contextual contact reviews were carried exactly: nine author, two decorator and two article cases. Eight histories contain contact material and fifteen contain notices. Pattern scans are not privacy clearance. Preserve content and provenance; any redaction requires a new derived artifact and renewed token/review bindings.

The synthetic-notice bundle binds Dynaconf's three, LensKit's five and Emcee's three source reads to snapshots/root notices. The Mypy initial notice assessment incorrectly described four post-edit reads; the **002 correction** records three. Keep both immutable packages and use the correction as the authoritative prose.

## 8. Sources acquired, proposed and not admitted

The source plan investigated SWE-Hero, OpenHands trajectories, SWE-smith, SWE-rebench/V2 and SWE-Gym. Publisher-scale figures in the plan (for example 34,269 SWE-Hero traces; 67,074 OpenHands traces; 50,908 SWE-smith Python instances; 32,079 V2 instances; 2,438 SWE-Gym instances) are source/card claims, not counts of usable data acquired by this project. They must not appear as our qualified training inventory.

Likewise, the official listing's graph, embedding and wheel volumes were metadata estimates, not a claim that terabytes of assets were downloaded. The qualified pool is the current manifest above. Proposed initial 500-trace / 100-task / 20-repository and later 5,000–15,000-trace targets are planning variables.

The three 50M-token candidates are a prospective experiment budget. Specify whether each budget means input tokens or supervised targets, how repeats count, and whether padding is excluded before scheduling. With only 262,593 current supervised targets, 50M targets would be about 190 repetitions of the present target count; that arithmetic is not a recommendation or evidence of sufficient diversity.

### New confirmation source intake: exact unfinished state

[Confirmation source intake](../evidence/data/confirmation-source-intake-001/) contains pinned cards/licenses, metadata projection, range receipts and analysis scripts. The V2 metadata extraction completed: **32,079 rows**, 20,607,932 network bytes, 47,605,612-byte metadata output. Its status is `provisional_metadata_only`, `training_approved=false`, `confirmation_frozen=false`.

Pinned V2 revision: `10483de0f50fe5da545942705a76c6150171af7f`; legacy revision: `89cdfbab4ab1bd8f5a658bb212d1b63624f4f881`. Decoded fields are instance_id, repo, base_commit, created_at, language, license, image_name and interface. Solution columns were not decoded. Range-fragment hashes were recorded, but **the full LFS digest was not verified**; footer-adjacent raw bytes may have been transferred. A dataset card license does not automatically settle upstream repository rights or contamination.

`selection-report.json` does not yet exist. `summarize.py` is prepared but its selection work is not recorded as complete. No new confirmation cohort has been selected/frozen, and this intake package has not yet received the separately recorded R2 archive/restore procedure. Earlier “extraction running” notes are historical.

The exposure inventory read 2,894 receipts and found 108 repository labels / 111 task IDs: a conservative lower bound, not complete exposure reconstruction. Browser preview also exposed legacy Spectree64 and Sepal_ui347/411; exclude those repositories from unseen confirmation selection. Current lexical checks found no exact/normalized issue duplicates across 1,275 pairs; maximum reported Jaccard overlap was 21/406 for the PennyLane pair. Repository-family lineage, forks and semantic contamination still require review.

## 9. Testing and what “passed” means

The latest recorded local suite is 671/671 with Torch tests enabled and zero skips. Earlier smaller suites and optional-skipped runs remain in the journal. The 671 result predates this documentation-only update; it was not independently rerun here. Test files and available test definitions are indexed, including placeholder status.

Verification layers are deliberately separate:

1. Pure structural/unit checks validate parsing, inventories, serialization, refusal paths and numerical helper contracts.
2. Reduced real-model/Torch checks validate masking, weighted loss/gradients, adapters, optimizer/state and restoration under bounded conditions.
3. Container task checks validate particular reconstructed source/runtime/test cases.
4. Full-model H100 checks demonstrate limited loading, inference and a one-step adapter fixture.
5. Sustained real-corpus optimization, frozen unseen evaluation and production deployment are **not completed**.

Synthetic admission tests cover altered observations, boolean call counts, invalid final prose/submission, teacher/synthetic distinctions, duplicate schemas and failed submissions. Legacy four-transition and V2 two-transition evidence formats are handled explicitly rather than conflated. Current corpus training is refused before attempting an absent model path; quarantined examples must remain unable to reach optimization.

Passing a test suite is evidence within those tests, not a guarantee of arbitrary mathematical correctness. Do not remove inconvenient legacy failures, relabel fixture successes as agent successes or report estimated concurrency as measured throughput.

## 10. Configuration ledger

| Configuration | Recorded values / intended scope |
|---|---|
| `configs/p1-serving.json` | Python3.12 Linux x86; loopback127.0.0.1:8000; max model length32768; BF16; Gemma4 tool/reasoning parsers; GPU utilization.8; tensor parallel1; max sequences1; startup1200s; no adapters. Some status/A100 labels are historical, not current acceptance |
| `configs/p1-training-pilot.json` | Rank4/alpha8/dropout0; max sequence64; batch1; one update; learning rate1e-4; weight decay0; seed7401; minimum free70GiB; CPU threads4/1; deadline900s; synthetic fixture only |
| `configs/p1-corpus-qualification.json` | Seed7401; learning rate1e-4; one update; deadline900s; max sequence32768; checkpoint512MiB; session/corpus1GiB; example16MiB |
| Harness context implementation | Recorded ADK compaction interval5, overlap2, threshold14336, raw retention5; cache minimum2048, TTL1800, interval10. Local driver/harness integration and GPU summarizer parity remain bounded/incomplete |

These are qualification settings, not a selected final training recipe. The exact source files take precedence over this explanatory table if deliberately changed later; update this table and record the new identity at that time.

## 11. Infrastructure, storage and instance history

| Location/service | Purpose and state |
|---|---|
| Repository | `/Users/jiangshengbo/Desktop/ZenithSync-Gemma-4-Paper-Track`; source, plans, receipts, many ignored/untracked artifacts and File Provider placeholders |
| Local recovered material | `/Users/jiangshengbo/.codex/zenithsync-p1-recovered`; current `corpus072/corpus.json`, restored runtimes and working recovered artifacts outside Git |
| Recovery tools/environment | `/Users/jiangshengbo/.codex/zenithsync-storage-recovery`; auxiliary venv and private recovery environment, not portable project assets |
| Model source folder | `/Users/jiangshengbo/Desktop/gemma-4-other-gemma-4-31b-it-qat-w4a16-ct-v2`; tokenizer retained; large weights were archived/released. Do not assume usable resident weights |
| Cloudflare R2 | Bucket `gemma4agenticdata`; content-addressed blobs and manifests under recorded `quarantine/v1` / `artifacts/v1` workflows. Endpoint and credentials supplied securely through environment |
| Original Runpod session | A100 session historically authorized for4h at$1.79/h; no network volume initially prompted durable-storage correction |
| Replacement Runpod session | H100 Pod historically `miniature_amethyst_pinniped`, ID`609g4lt940xrxe`;4h at$3.99/h; network volume attached. These prices/permissions are historical, not a new authorization or current quote |
| Network volume | Historical201GB volume and Python3.12.3 persistence checked after restart. Verify actual mount and identity on the next session |
| DigitalOcean / Render | No qualified deployed service established in this P1 record; unnecessary to start merely to continue local data work |
| Other Cloudflare services | No claim of a deployed frontend, Worker, production gateway or training service; R2 is the established storage role |

The model/runtime was restored and qualified previously, but no remote state was rechecked for this handoff. A worker deadline or SSH exit cannot stop Runpod billing. Use a separately observed Pod state and budget closeout when a future session ends.

The corrected serving environment used Torch2.10.0, not an assumption that the original Runpod PyTorch2.8 template was qualified. Serving is Python3.12; task evaluation used Python3.13. The serving bundle had250 packages and5,331,545,654 wheel bytes, plus16,666,629 bootstrap bytes. FastAPI0.136.3 corrected the observed incompatibility between FastAPI0.141.1 and instrumentator7.1.0. The PEFT0.21.2 supplement was added with no dependency expansion;251-package consistency was checked. Never merge these environments casually.

R2 publication/restoration is recorded per manifest. The current corpus, integration, history-material, split-audit, exposure, synthetic-notice and notice-correction packages have their own receipts. The artifact index includes manifests and verification directories; not every local file has an R2 counterpart. Historical overwritten ingestion metadata was repaired and manifest members rechecked; newer transfer verification enforces disjoint metadata trees and exact inventories. Preserve the recovery reports.

Storage cleanup removed only verified redundant material in recorded cycles, including164.2MiB shared Debian packages and114.0MiB redundant native archives after restored inner-member verification. Retained originals and placeholders are not blanket deletion candidates. The latest known local disk was very tight; recheck before restoring large payloads. The user confirmed Keep Downloaded on the small `zenithsync` source folder no longer gives the Finder error. Do not apply Keep Downloaded to the entire artifact tree.

## 12. Safe developer restart procedure

1. Obtain the **current working tree**, not only HEAD, together with the handoff appendices. Preserve existing staged, unstaged and untracked files. Read applicable AGENTS.md instructions. Do not reset the repository to make it clean.
2. Provision credentials through the private `.env` mechanism. Do not copy secrets into docs, issue comments, logs or source. Credentials previously shared in chat are not documentation assets; confirm their validity/security separately with the owner.
3. Check available disk and File Provider status. Materialize the small source/test/config/requirements files needed for the chosen operation. The code inventory flags absent resident contents; hashes are omitted where unavailable. Do not hydrate the model or all evidence simply to browse.
4. Restore the selected R2 manifest to a new owned destination; verify exact file inventory, sizes and SHA256 before using it. Preserve the publication and independent read-back receipts. Do not restore over the current corpus or edit archived evidence in place.
5. Recount current corpus tokens and targets and compare its manifest hash against section2. Inspect all four admission gates. Any changed history, token file, review, split or source requires a new version and renewed bindings.
6. Reconstruct the appropriate environment from its pinned lock and verified wheel bundle. Use offline `--no-index --require-hashes` installation where the recorded workflow requires it; run `pip check`. Use the deployment handoff for concrete scripts/arguments, not invented flags.
7. Run the complete local suite from the intended source root with optional Torch checks explicitly enabled. The recorded command shape is `ZENITHSYNC_TEST_TORCH=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 <qualified-python> -m unittest discover -s tests`. Replace the interpreter with the verified environment, retain stdout/stderr and identify the source tested. Zero skips matters; a smaller default suite is not equivalent.
8. Address the admission/confirmation work below before spending GPU time. On a future Pod, verify mount persistence, capacity, Python/CUDA/runtime versions, source/model hashes, GPU availability and deadline controls before launch. Keep the model server off during training unless concurrent memory use has been explicitly qualified.
9. Start a new bounded session only after fresh budget approval; retain launch manifest, PID/process-group ownership, metrics, checkpoints and shutdown evidence. A STOP file/process supervisor only controls its owned workload.

Known local interpreters are recovery conveniences, not stable deployment APIs: `.../.codex/zenithsync-storage-recovery/venv/bin/python` has storage/Arrow helpers but not all HTTP dependencies; `.../.codex/zenithsync-p1-recovered/native-runtime-recovery/venv/bin/python` contains the recovered SDK/Torch/tokenizer stack. Verify imports before selecting either. Architecture-specific containers must explicitly distinguish native ARM64 from emulated AMD64; two wrong-platform Mypy attempts failed before execution.

## 13. Remaining work and acceptance evidence

| Priority | Unfinished work | Required evidence to close it |
|---|---|---|
| 1 | Complete rights, embedded/dependency notices and contextual privacy review on exact current histories | Exact observed-material coverage, retained license/notice provenance, reviewed exceptions, immutable decision binding; credential-pattern scan alone insufficient |
| 2 | Finalize current task-alignment and runtime admission | All51 source/history/patch/grading bindings, review coverage controls, precise runtime limitations; explicitly populate the gate only when its criteria hold |
| 3 | Finalize train/dev/confirmation policy and repository-family lineage | Frozen manifests, exposure exclusions, duplicate/fork decisions and negative cross-split tests; no current inspected task called unseen |
| 4 | Finish new confirmation-source selection | Review projection limitations, run and inspect selection reporting, exclude exposed repositories, acquire permitted independent tasks, freeze before optimization, R2 archive and restore-verify intake |
| 5 | Expand qualified data | Measured admitted—not merely downloaded—tasks, targets, repository diversity, rejection reasons, licenses and contamination controls. Current51 are insufficient evidence for the planned scale |
| 6 | Close serving and evaluator gaps | Checkout-origin parity, repeatable native tool/content fidelity, official context/compaction behavior, adapter serving path and realistic bounded limits |
| 7 | Full-corpus bounded GPU preflight | Fresh budget and launch identity, admitted data, realistic sequence/memory behavior, finite loss/gradient checks, frozen-base checks, checkpoint/reload and exact optimizer/cursor resumption |
| 8 | Sustained training design | Explicit token accounting, training mixture, optimizer/precision/schedule choices, stability monitoring, storage/checkpoint policy and measured throughput-based duration forecast |
| 9 | Three50M-token candidates | Only after preceding gates: reproducible independently identified runs, complete metrics and failure accounting; not currently launched |
| 10 | Independent comparison and novelty | Frozen strong baselines, paired task outcomes, exposure-aware uncertainty, cost/runtime comparisons and ablations. No superiority claim until measured |
| 11 | Product/submission hardening | Official packaging, resource/runtime validation, reproducible deployment, operating instructions and competition deliverables; no current industrial release |

The next useful work is admission and prospective confirmation/data expansion, not turning on the Pod to repeat the24-token fixture. Do not accept “advanced mathematics” as a substitute for falsifiable objectives, measured stability and independent task outcomes.

## 14. Failure history and precedence rules

Preserve failed compiler attempts, malformed writes, turn exhaustion, Unicode failures, source-import mistakes, dependency/platform failures, incorrect token/history captures, rejected task/control outcomes, incomplete notices and obsolete corpus manifests. They explain why the present contracts exist and prevent recurrence. The evidence catalog/file index exposes retained attempts; the implementation journal explains decisions and corrections.

Use this precedence order: exact current manifest and referenced receipts → explicit correction package → current readiness/handoff → older narrative/config labels → original proposal. A later prose claim must not silently override contradictory raw output. When a discrepancy remains, retain both and state the uncertainty.

Specific stale claims to avoid: README previously said Corpus050/522 tests; earlier docs used three admission gates; some configuration status strings still describe pending initial GPU work; old extraction notes say running; older corpora remain on disk. Current values are Corpus072/671 recorded tests/four admission gates/completed metadata projection but unfinished confirmation selection. The archived records themselves should not be rewritten to pretend they were always current.

## 15. Maintaining and transferring this handoff

After each implementation cycle, record changed code/config identities, data additions/removals and provenance, tests actually run with failures/skips, numerical assumptions and counterexamples, infrastructure state and cost bounds, published/restored artifacts, gate transitions and the exact next work. Update current readiness and this document; append the journal. Regenerate inventories only from the intended checkout and verify counts/links. The generator currently uses the explicit local Corpus072 recovery path; changing the authoritative corpus requires updating that selection deliberately.

The handoff is the **main document plus inventories, current working tree, immutable evidence/manifests, recoverable payloads and securely provided credentials**. It is not a standalone copy of all model weights or runtime dependencies. Existing source files contain the exact code; the catalog links to them rather than maintaining a second divergent copy. External recovery directories are named but not recursively copied. Hidden environments, keys, large payload contents and remote live state were not audited during this documentation pass.

This package accounts for the known P1 implementation and outstanding obligations at this snapshot. It does not claim to recover undocumented historical actions or inspect every byte of33,410 artifacts. A new developer can identify every indexed artifact, follow its receipts, reproduce the relevant bounded check and see clearly where evidence or implementation is still missing.
