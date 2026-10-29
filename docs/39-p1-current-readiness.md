# Current P1 readiness

Updated October 29, 2026. **P1 is incomplete. No GPU training has started.**

**October 29 change of state.** The corpus admission blocker is closed:
Corpus072 is now **training-admitted**, its bytes live in R2 rather than on the
development machine, and the real worker's own `preflight_corpus_run` accepts it.
A screened public task pool supplies 2,966 tasks across 507 repositories and 439
owners with a 445-task repository- and owner-disjoint confirmation cohort. The
local suite is 944 tests with zero skips on the full dependency stack, and 944
collected and passing with 70 skips on the standard library alone. The rows marked *(superseded October
29)* below are kept for history; see
[the training unblock and data-scale cycle](42-training-unblock-and-data-scale.md)
for what replaced them, what it does not establish, and the measurement work
that must precede any GPU run.

The [complete P1 developer handoff](41-p1-complete-developer-handoff.md) is the
entry point for a new developer, with code/task/artifact inventories and explicit
implementation and mathematical limits. October 19 filesystem verification found
the new confirmation metadata projection complete (32,079 rows); selection,
confirmation freeze and archive/restore qualification of that intake package
remain unfinished. Earlier running-process statements in the journal are historical.
No GPU or model training was performed during the documentation update.

This page describes the latest verified state. The previous 4,129-line status
ledger, including subsequent updates, is preserved without content changes in
[the historical readiness ledger](39-p1-readiness-history-through-2026-10-16.md).
The [implementation journal](40-p1-implementation-journal.md) records work over
time. Historical successes apply only to their recorded inputs and scope.

## Current evidence

| Area | Verified result | Limit |
|---|---|---|
| Local regression | **944 tests passed** in 27.605 seconds, Torch enabled, zero skips, October 29; the same 944 collect and pass with 70 skips on a stdlib-only Python 3.13.7, and 3.11 or newer is required. The previous [671-test run](../evidence/data/lenskit312-contract-policy-001/local-full-suite.log) is retained as history. | Finite CPU and reduced-model checks do not establish full-model GPU correctness. **The development interpreter has torch 2.14.1, not the worker's pinned 2.10.0, and no `compressed-tensors` at all**, so the Torch-dependent checks passed on a different Torch than the training stack. `scripts/verify_training_runtime.py` exits nonzero on this machine and names both mismatches. |
| R2 training readiness | [One command proves it from the bucket alone](../evidence/data/corpus072-admission-001/r2-training-readiness.json): corpus restored and double-verified, the loader offering exactly the audited training set, all three tokenizer assets fetched by content digest, **all 8 model files present (23,297,590,856 bytes, including the 21.7 GiB quantized checkpoint)**, the schedule regenerated to `4664ecf6…`, and the real worker's `preflight_corpus_run` passing. | The data path is complete and self-consistent from the bucket. Not rights clearance, not host capability, not model fit, and no claim about learned performance. The model check is presence-and-size from remote metadata; the 21.7 GiB checkpoint is not re-hashed. |
| Evidence completeness in R2 | A content-coverage audit found 15,426 local files (~1.03 GiB) whose bytes had no counterpart in the bucket; `scripts/ship_evidence_to_r2.py` publishes each evidence package under its own content-addressed manifest with an index. Credential paths, symlinks and oversized packages are refused whole; `.git`, caches and virtual environments are skipped. | Content presence, not a durability or access-control guarantee. A covered digest means the bytes are in the bucket, not that a manifest references them. |
| Frozen confirmation cohort | [445 tasks across 105 owners reserved](../evidence/data/confirmation-cohort-freeze-001/receipt.json) under freeze identity `e5b7cf7a…`, bound to the dataset revision, metadata identity, exposure-ledger identity and selection seed taken from the pool's own report. Owners are reserved with their tasks, and freezing refuses an owner spanning a reserved and a training cohort. [The gate](../evidence/data/confirmation-cohort-freeze-001/gate-refusal-receipt.json) caught one reserved task hidden among 200 training candidates and exits 1; a wrong pinned freeze digest exits 4 as `freeze_unusable`. | Establishes that these tasks were reserved **before** any optimisation, which is what makes a later comparison meaningful. Does **not** establish they are unseen: forks, backports, vendored copies and pretraining exposure are undetected, and the exposure ledger used records itself as incomplete. |
| Runtime preflight | `scripts/verify_training_runtime.py` checks the worker's own preconditions — Linux, Python exactly 3.12, the four pinned versions, one exclusive CUDA device, the 70 GiB free-memory floor, and the corpus's longest example against configured capacity — and exits nonzero naming every mismatch. Tests parse those pins out of `run_corpus_training_worker.py` and assert they match, so the two cannot drift. | Preconditions only. Not peak memory at full sequence length, not throughput, not checkpoint durability. No official Runpod template ships the pinned Torch 2.10 / Python 3.12 pair, so `configs/Dockerfile.p1-training-runtime` is prepared — **it has never been built or run** and is unqualified until the preflight exits zero inside it on the intended GPU. |
| Inference transport | [Real HTTP framing controls](../evidence/p1/inference-framing-001/assessment.md) reproduce five previous failure cases and verify rejection after the fix; three valid framing variants preserve response bodies. Evidence independently restored from R2. | Diagnostic nonstreaming transport only; no new model-generation or streaming qualification. |
| Evaluation accounting | [JUnit consistency audit](../evidence/p1/junit-accounting-001/report.json) preserves the retained 324-case Requests comparison and rejects eight contradictory aggregate reports. Supplied failure/error/skip counts must match case outcomes. | Existing report reanalysis, not a new repair run or official hidden-grader qualification. |
| Repaired mypy example | [Fresh replay and token evidence](../evidence/data/mypy47-replacement-001/report.json): readable source correction, 40 calls, 84 messages, 22,634 input tokens and 7,559 supervised targets. Exact final source matches the expanded local controls and all 11 publisher cases. | Reference-informed derivative, not an independent held-out solve. Earlier defects and failed/superseded attempts remain preserved. |
| Task alignment | [Corpus072 review](../evidence/data/corpus072-integration-001/task-reviews.json): all 51 accepted within documented scope. All 51 leave-one-review-out controls reject incomplete coverage. | LensKit uses explicit issue-contract acceptance, not reference equivalence; legacy failures/skips remain recorded. Rights, privacy, split and runtime gates remain separate. |
| Spline mathematical audit | [Exact projection audit](../evidence/data/csaps3-exact-projection-audit-001/assessment.md): 54 rational systems, 1,791 entries; selected/control patch outputs identical. Zero smoothing selects the weighted affine least-squares projection under stated assumptions. R2 independently restore-verified. | Finite algebraic checks plus conditional derivation, not universal floating-point correctness. Separate two-point metadata behavior documented; Csaps semantic alignment accepted; native publisher grading and mechanical/training admission remain separate. |
| Jsons synthetic replacement | [Source-bound admission](../evidence/data/jsons86-synthetic-admission-001/assessment.md): 10 charged calls, 29 messages, 8,118 input tokens, 2,152 supervised targets; exact issue reproduced, 126 finite checks and 19 original tests pass, ten publisher outcomes match. | Assistant-authored and reference-informed; not model performance. Old rejected histories remain preserved. |
| Emcee replacement candidate | [Fresh capture](../evidence/data/emcee295-synthetic-trajectory-002/assessment.md): nearby tests read before editing, two successful status calls, 21 reference outcomes matched; 8,295 input tokens and 2,279 supervised targets. | Mechanical checks pass; Corpus072 selects the fresh history. Assistant-authored and reference-informed, no training approval. |
| Context reserve | [Corpus072 recount](../evidence/data/corpus072-integration-001/context-report.json): all 51 fit input plus 8,192 output reserve; minimum margin 210. Jsons margin 16,458. | Context policy only, not measured generation memory or GPU fit. |
| Split exposure audit | [Corpus072 audit](../evidence/data/corpus072-split-audit-001/assessment.md): 51 train records, 50 case-normalized repository labels, 1,275 issue-text comparisons, no exact/normalized duplicates. PennyLane tasks linked in a separate draft; cross-split control rejects. | Zero unseen confirmation tasks **within Corpus072**; that is why its admission is all-train. A prospective 445-task confirmation cohort now exists in the separate task pool above and is not yet frozen. Low lexical overlap does not prove independence; repository lineage review remains required. |
| Development exposure inventory | [Receipt-derived exclusions](../evidence/data/confirmation-exposure-001/assessment.md): 2,894 receipts inspected, 108 repository labels and 111 task IDs identified; supporting receipt hashes rechecked. | Conservative lower bound only; acquisition is not proof of viewing, and absence is not proof of unseen status. Prospective confirmation remains unfrozen. |
| Current corpus | [Corpus072 admitted](../evidence/data/corpus072-admission-001/admission-receipt.json): 51 tasks; 954,733 input tokens and 262,593 shifted supervised targets; admitted manifest `fa984ca3…`, content identity `c081880c…` unchanged by promotion. All four gates bound to recorded review evidence. Published to and restored from R2; the real worker preflight accepts it. *(Supersedes the October 19 quarantine row.)* | Admission means the gates are resolved and bound, not that rights are cleared, a reviewer's conclusion is true or the GPU will fit the work. All 51 examples are `train` and all are development-exposed, so a 50M-target run is 190 repetitions of the same data. |
| Two-layer corpus verification | [Independent re-derivation](../evidence/data/corpus072-admission-001/two-layer-verification.json): `zenithsync.corpus_audit` recomputes every digest, count, duplicate check, split-isolation check and gate binding from stored bytes without calling the loader, and the two layers agree on all eight shared quantities. All 51 examples refetched and rechecked; schedule coverage exact; minimum context margin 210 reproduced from a separate code path. | Agreement is evidence of consistent accounting, not that the data is well chosen or that the model will learn anything. |
| Screened public task pool | [SWE-rebench V2 Python pool](../evidence/data/task-pool-v2-python-001/report.json), dataset revision `10483de0…`, metadata `701f75d5…`: 32,079 rows screened, **4,818 eligible** across 507 repositories and 439 owners; 2,966 selected under ≤12-per-repository and ≤24-per-owner caps; [cohorts](../evidence/data/task-pool-v2-python-001/cohorts.json) train 2,076 / development 445 / **confirmation 445**, repository- and owner-disjoint. | Metadata only; no issue text, source or reference patch read. A licence label is evidence for a rights review, not a clearance — 1,706 placeholder and 348 absent labels were refused. Exposure exclusion is a lower bound, so this is not an unseen-data guarantee. `rights_cleared`, `replay_verified`, `split_frozen` and `training_approved` are all false. |
| Campaign arithmetic | [50M-target plan](../evidence/data/campaign-plan-001/report.json): repetition factor **190.41×**, 191 whole epochs, ~181,789,499 processed input tokens, largest repository group share 4.87% under the declared 5% cap. | Exposure and cost arithmetic only. No duration or cost figure was produced, because no throughput has been measured for this configuration at a realistic sequence length. |
| Ingestion | [Corpus072 restored-worker checks](../evidence/data/corpus072-integration-001/corpus072-ingestion-001/report.json): all 42 deployment files match current repository counterparts; local/restored schedules agree; worker rejects quarantine before model access. | No optimizer steps, full-model execution or training admission. |
| Resume scheduling | [Corpus072: nine planned updates, ten resume boundaries](../evidence/data/corpus072-integration-001/corpus072-ingestion-001/resume-verification.json): every remaining schedule reproduced exactly; ten corrupt counters rejected; all 51 examples appear once with zero target overshoot. | Finite schedule recovery only, not full-model optimizer/checkpoint recovery. |
| Source provenance | [All 51 Corpus066 source metadata joins](../evidence/data/corpus066-attribution-index-001/report.json); [Dynaconf canonical commit tree](../evidence/data/dynaconf-canonical-lineage-003/report.json) matches its replay snapshot and current history. | The old Dynaconf URL now points to a different mirror. Canonical content verification does not make the URLs equivalent. |
| Synthetic source notices | [Exact range checks](../evidence/data/corpus071-synthetic-notice-bindings-001/assessment.md): Dynaconf three, LensKit five, Emcee three reads match pinned source; root notices match retained bytes. All 42 evidence files independently restored from R2. | The earlier Emcee history had ordering/status gaps; Corpus072 now selects the fresh corrected capture. Its three source reads match the same pinned snapshot. Task-behavior review is separate. Embedded/dependency rights remain unresolved. |
| Current histories | [Corpus072 inventory](../evidence/data/corpus072-history-material-001/assessment.md): all 51 Corpus072 histories located locally without downloads; 50 unchanged and only Emcee changed from Corpus071. | Inventory is not notice/privacy approval; shell observations require separate material review. |
| Encoded credential indicators | [Corpus072 decoded-token screen](../evidence/data/corpus072-history-material-001/token-screen/report.json): all 51 current examples screened, zero configured indicators. Exact current histories also pass nested scanning. | Finite indicator coverage only; no secret-free or whole-history privacy guarantee. |
| Contact indicators | [13 current occurrences reviewed](../evidence/data/corpus072-history-material-001/contact-review.json): nine software attribution, two decorator false positives, two article contacts. All 13 reviews carried forward after exact history, location and matched-text hash checks. | No whole-history privacy clearance; matched values are not printed or copied into the review. |
| Embedded Runpy component | [Pinned upstream comparison](../evidence/data/runpy17-embedded-source-001/assessment.md): all five logging methods match upstream syntax trees; the current corpus observation contains all 131 source lines with the BSD attribution preserved. | Whole-file differences recorded; full BSD license text, separate SQL filter, other notices and training admission remain unresolved. |
| Mypy source notices | [Current range bindings](../evidence/data/mypy47-current-notice-binding-002/assessment.md): four initial source reads match the pinned tree and root MIT notice; two reads are partial. | Four generated diagnostic files and three post-edit reads remain separately classified; shell/dependency and edited-material coverage is not established. |
| Missing dependency notice | [ptvsd 3.0.0 notice recovery](../evidence/data/ptvsd300-notice-001/report.json): seven runtime files match the verified release; headers and license preserved. | Other package/source notice coverage remains separate. |
| Transfer evidence integrity | [Receipt recovery](../evidence/p1/ingestion-receipt-recovery-002/report.json) restores two overwritten local metadata members in Corpus065/066 ingestion evidence; all 51 listed members across Corpus065–067 rechecked. [New disjoint verifier](../evidence/p1/ingestion-receipt-recovery-002-verification/verification.json) exercised on a real R2 round trip. | Legacy bundles retain extra metadata files; recovery validates manifest-listed members. New verifier requires exact inventories and separate metadata trees. |
| Storage | Corpus, integration, ingestion and recent review packages published and independently restore-verified in R2, including the [103-file Corpus072 payload](../evidence/data/corpus072-payload-001-verification/verification.json). [Duplicate package cleanup](../evidence/data/shared-debs-release-001/report.json) released 164.2 MiB; [redundant native archives](../evidence/data/native-archive-release-001/report.json) removed a further 114.0 MiB of allocated file blocks after fresh R2 restores and verification of all 129 inner members. | Retained primary data still occupies disk; R2 backups are not a claim that every local byte can be deleted. |
| Finder | [Current scoped diagnostic](../evidence/data/fileprovider-diagnostic-004/report.json): no unresolved conflicts in four inspected folders; source/docs recursively downloaded and uploaded; root syncing recent changes. | The user confirmed that Keep Downloaded on the small zenithsync source folder now reports no error. Large artifact placeholders make whole-repository Keep Downloaded unsuitable while storage is tight. |

Corpus manifest SHA256:
`42da2d372f908d00b72a3f7d89af9b5fa082f8caeb8a4307bd77cfc363a2de75`.

## Remaining work, in dependency order

1. **Finish current-content admission coverage.** Use the exact-history inventory
   to bind observed repository and dependency files to applicable notices. Carry
   separate embedded notices, including the PubMed article and Runpy BSD header.
   Complete contextual privacy review without silently rewriting observations.
2. **Complete split review for the intended training release.** Task alignment now covers all 51 Corpus072 records; carry that exact evidence forward. Record
   exact task/repository coverage, repository-family grouping and reviewed duplicate
   flags. Acquire a new confirmation cohort under the [prospective protocol](../evidence/data/corpus072-split-audit-001/confirmation-protocol.md) and freeze it before optimization; none of the 51 inspected tasks qualifies as unseen confirmation. Existing lexical checks
   and repository IDs alone do not prove semantic independence.
3. **Scale the qualified data pool.** Measure admitted tasks, repository diversity,
   supervised targets and rejection reasons across acquired datasets. The current
   262,593 targets are a qualification pool, not evidence of sufficient data for
   three 50M-token candidates. Repeated exposure is not additional unique data.
4. **Close local serving/evaluator limitations.** The official Requests evaluator
   previously imported an installed package instead of checkout edits. Preserve
   the source-origin guard and investigate official parity. Tool-call variability
   and streaming also remain unqualified. See the [acceptance checklist](26-p1-acceptance-checklist.md).
5. **Prepare a bounded GPU qualification session.** Bind the exact code, dependency,
   model, corpus and configuration manifests; restore-test required assets and
   run applicable local checks. Only then request the user's Pod restart and a
   fresh session spending/time limit.

Corpus071 retains the prior mypy derivative and Emcee/Dynaconf/Jsons synthetic replacements, and replaces LensKit with the corrected assistant-authored, reference-informed trajectory. Its audit records explicit issue-contract grading and reference disagreement. All four manifest admission fields remain null until release-gate binding:
`rights_and_attribution`, `split_isolation`, `runtime_qualification`, and
`task_alignment`. Reviews must produce evidence for the actual current content;
setting a receipt to passed is not a substitute for doing the review.



## GPU boundary and later training

Historical H100 evidence includes one synthetic full-checkpoint LoRA update and
reload, documented in the [acceptance checklist](26-p1-acceptance-checklist.md).
That does not qualify long training streaks, full-model optimizer resume,
serving with the trained adapter or coding improvement.

Do not restart Runpod for more metadata inventories, local replay qualification,
notice review or documentation. The next GPU request must name the remaining
GPU-only experiment, exact prerequisites, acceptance criteria, resource limits
and deadline. Before any long training streak, validate its exact inputs and
checkpoint/recovery behavior. Absolute error-free operation cannot be guaranteed
by finite tests; failures and untested conditions must remain visible.

## Storage and recovery instructions

The seven completed replay contexts named in the cleanup report no longer contain
duplicate Debian packages. Before rebuilding one, run
[restore-context.py](../evidence/data/shared-debs-release-001/restore-context.py)
with the exact absolute context path recorded in its sibling `before-unlink.json`.
The helper restores from the retained shared package set and checks hashes.
Its 32-file restore was tested. Source snapshots and Docker images were preserved.

The user confirmed that Keep Downloaded on the small `zenithsync` source
directory now reports no error. This confirmation does not cover the large
artifact folders or whole-repository hydration; no sync-database repair was performed.

Historical Corpus060–065 payload duplicates were removed after exact comparison
with retained Corpus066 and all-payload recovery testing, releasing 60.7 MiB.
Their manifests remain. Before loading one of these historical corpora, run
[restore.py](../evidence/data/historical-corpus-payload-release-001/restore.py)
with its version name, for example `corpus065`. The helper refuses differing
existing bytes. If Corpus066 is unavailable, restore it from R2 first using its
recorded transfer manifest. [Cleanup evidence](../evidence/data/historical-corpus-payload-release-001/report.json).

Two redundant compressed archives (`nbgrader1410-native-archive-001/evidence.tar.gz`
and `pubmed89-native-archive-001/evidence.tar.gz`) were removed from the recovered
workspace. Their unpacked source evidence and archive manifests remain. To recover
an archive into a **fresh** destination, run
`python3 -B evidence/data/native-archive-release-001/restore.py nbgrader1410 /absolute/fresh/archive /absolute/fresh/receipts`
from the repository root; substitute `pubmed89` for the other archive. The helper
uses the existing private R2 environment, verifies the exact manifest and refuses
existing destinations. Both archive restore paths were exercised before cleanup.
Do not rerun historical archive-building scripts into their existing directories.

## Latest Jsons quality decision

The 84-message replay006/history003 passes mechanical checks but remains held for whole-history quality. Duplicate exploration, incomplete full-suite evidence, overbroad diagnostic wording, inaccurate reproduction labeling and missing final explanation prevent training-quality approval. Corpus067 remains unchanged. See [the review](../evidence/data/jsons86-history-quality-001/assessment.md); its four-file evidence package is R2-published and restore-verified. Docker API is responding at version 29.8.2.

## Historical GPU fixture moved to R2

The full 11-file single-update GPU fixture was published and independently restored with exact hash verification. Its two large local payloads (adapter weights and optimizer state) were then removed, releasing 368,103,424 allocated file bytes (351.1 MiB). Small local records remain. The separate 12-file cleanup/recovery package was also published and restore-verified. This fixture does not qualify production training.

To recover all original fixture files into a fresh directory, run `python3 -B evidence/data/full-checkpoint-fixture-release-001/restore.py /absolute/fresh/fixture /absolute/fresh/receipts` from the repository. Both paths must be new and disjoint. [Recovery details](../evidence/data/full-checkpoint-fixture-release-001/assessment.md). Existing historical paths to the two large payloads now require restoration; metadata paths remain available.

## Emcee replacement replay qualification in progress

[Fresh context-repair evidence](../evidence/data/emcee295-context-repair-001/report.json) preserves two amended offline replays. Attempt005 has 25,497 inputs (reserve margin -921); attempt006 has 24,551 inputs (margin 25). Both preserve the original patch, 40 charged calls and successful memory/HDF5 completion assertions. Six pytest commands use concise failure reporting; the original head pipeline is removed so failure exit status is visible. The 25-token margin is fragile. [Fresh grading and mechanical checks pass](../evidence/data/emcee295-native-qualification-001/report.json): all 21 outcomes match reference (19 passes, two expected persistent failures). Whole-history quality review is complete and holds this derivative: inaccurate earlier supervised labels/claims, print-only diagnostics and missing final explanation remain despite a genuine corrective completion. Corpus067 is unchanged. See [quality decision and replacement specification](../evidence/data/emcee295-history-quality-001/assessment.md); its four-file package is independently restore-verified in R2. The 39-file package was R2-published and independently restore-verified.

## Emcee concise synthetic replacement candidate

[Fresh assistant-authored trajectory](../evidence/data/emcee295-synthetic-trajectory-001/assessment.md) executes eight charged calls, with 21 messages and 8,038 input tokens (16,538 reserve margin). Identical unequal-axis assertions fail on base and pass after repair; both memory/HDF5 finite checks pass. Original sampler tests retain 10 failures/11 passes, correctly distinguished from external grading outcomes. The 415-byte patch is unchanged. Two runner failures are preserved alongside successful attempt003. All 25 evidence files (303,712 bytes) were R2-published and independently restore-verified. [Independent grading and full content review](../evidence/data/emcee295-synthetic-qualification-001/assessment.md) now pass within their stated scope: all 21 reference outcomes match (19 passes, two persistent failures), all 21 messages were reviewed, and captured exchanges/protocol schemas match current installed signatures. Content is accepted for subsequent synthetic-provenance mechanical integration, with minor limitations recorded. This is not historical runtime attestation or training admission. Corpus067 is unchanged; mechanical integration and corpus/ingestion qualification remain pending. The 22-file qualification package is R2-published and independently restore-verified.

## Corpus068 integration

[Integration evidence](../evidence/data/corpus068-integration-001/assessment.md) supersedes earlier statements that Corpus067 is current. Synthetic mechanical checks pass; 50 unaffected records are exact. [Corpus068 ingestion/resume and review rebinding](../evidence/p1/corpus068-ingestion-001/assessment.md) are now verified within their finite scope. Task review remains partial at 32 accepted/19 pending; historical Corpus067 results remain historical.

## Numkit issue alignment

[Selected Numkit repair review](../evidence/data/corpus068-task-alignment-001/assessment.md) binds exact patched source to retained 53-case controls and the selected native 1,620-case numerical check. Fresh endpoint checks cover 4,032 finite length/window pairs, with a conditional general length derivation. This is task alignment, not whole-history quality, full-suite success or training approval.

## Optuna issue alignment

[Selected Optuna repair](../evidence/data/corpus068-task-alignment-002/assessment.md) preserves supported types and warns for unsupported choices. Fresh isolated checks include warnings-as-errors behavior; retained nine-case grading and a six-point in-memory grid support bounded alignment. Sorting, persistent storage and distributed behavior remain outside that claim.

## LMFIT issue alignment

[Selected LMFIT review](../evidence/data/corpus068-task-alignment-005/assessment.md) binds the selected repair to 13 retained publisher outcomes. Fresh isolated method probes verify stale-state reset ordering, new-error propagation, recovery and candidate/reference list-alias differences using an explicit evaluator double. These are not fresh asteval integration tests. Full-history quality and all training admission gates remain separate and incomplete. The five-file review package is R2-published and independently restore-verified.

## CRC issue alignment

[Selected CRC repair review](../evidence/data/corpus068-task-alignment-006/assessment.md) freshly reproduces the original alternating digest and checks candidate/reference modules over all 131,072 eight-bit state/mask/reflection combinations each, plus 96 multiwidth continuation cases each. Retained publisher comparison matches 17 outcomes. A conditional state-preservation argument supports the finite checks; whole-history quality and training gates remain separate. Five evidence files are R2-published and independently restore-verified.

## Django API-key alignment and verifier compatibility

[Selected Django startup repair](../evidence/data/corpus068-task-alignment-007/assessment.md) passes fresh eight-version controlled-import checks and recomputation of the retained two-version matrix with 64 unique nodes. Fixed strict receipt verification to recognize the exact frozen historical evaluator body alongside the current body; altered bodies still reject. The latest full local suite passes **648 tests, zero skips, 28.351 seconds** with Torch enabled. Nine evidence files totaling 62,316 bytes are R2-published and independently restore-verified. Earlier deployment snapshots remain historical; this change does not establish a refreshed complete deployment or training approval.

## PubMed subject extraction alignment

[Selected PubMed repair review](../evidence/data/corpus068-task-alignment-008/assessment.md) verifies reference-equivalent parser source, fresh real-lxml execution over 36 synthetic structures and eight retained NXML fixtures, and preservation of unrelated output fields in those fixtures. Namespace handling and ambiguous semicolon serialization remain explicit limitations. Four retained publisher outcomes match. Ten evidence files are R2-published and independently restore-verified; no training approval or Runpod use.

## Tianshou serialization alignment

[Selected Batch serialization review](../evidence/data/corpus068-task-alignment-009/assessment.md) reproduces baseline recursion and verifies 36 candidate roundtrips plus exact Pipe/file use cases. Fresh reference checks reveal 12 protocol-0/1 failures and lost shared nested aliases; neither is hidden by the four-case retained publisher agreement. This is serialization correctness within stated cases, not RL convergence or general multiprocessing validation. Five evidence files are R2-published and independently restore-verified.

## Werkzeug historical PBKDF2 alignment

[Selected iteration-default review](../evidence/data/corpus068-task-alignment-010/assessment.md) freshly checks baseline/candidate/reference defaults, four explicit counts and password verification. Scrypt remains the public default. Retained publisher comparison matches 12 cases; retained 55-case semantic evidence is separately identified. The work-count ratio 5/3 is not an entropy or measured performance guarantee. Six evidence files are R2-published and independently restore-verified.

## Statsmodels bounded initialization alignment

[Selected automatic-lag review](../evidence/data/corpus068-task-alignment-011/assessment.md) verifies the first-argmax invariant with 2,184 fresh finite helper cases and 1,452 exact rational score cases. Acceptance covers the reported initialization fixes only. The unchanged caller includes lag-zero correlation and forces its 2p branch for ordinary finite nonconstant inputs; the publisher reference also has a documented off-by-one defect. Neither publisher agreement nor helper correctness proves the full statistical procedure. Five evidence files are R2-published and independently restore-verified.

## LensKit full-issue scope hold

[Fresh LensKit issue reproduction](../evidence/data/corpus068-task-alignment-012/assessment.md) shows candidate/reference fix explicit-k truncation but leave the first requested no-k normalization behavior unchanged. Task alignment is held, and the validator rejects that decision. Accepted coverage remains 32/51; 19 records are unaccepted, including this demonstrated hold. Passing the retained 20-case publisher suite or full-truth-convention numerical oracle does not resolve the omitted requirement. Six evidence files are R2-published and independently restore-verified.

## LensKit full-issue repair candidate

[A new attributed candidate](../evidence/data/lenskit312-full-scope-candidate-001/assessment.md) implements both original behaviors and matching bulk per-list normalization. It passes 3,510 scalar, 3,456 bulk and three mixed-truth checks in both local and retained NumPy 1.22.4/Pandas 1.5.3 environments; maximum Decimal-oracle error is 1.11e-16. Nine files are R2-published and independently restore-verified. Full-package compatibility, fresh trajectory capture and replacement admission remain required. Original Corpus068 LensKit record stays held; accepted coverage remains 32/51.

## LensKit paired compatibility and requested-behavior tests

[Paired top-N regression](../evidence/data/lenskit312-full-scope-regression-002/assessment.md): baseline 81 passed; candidate 78 passed and three failures asserting the old no-k denominator. All original tests remain unchanged. [Four new contract tests](../evidence/data/lenskit312-full-scope-contract-001/assessment.md) fail baseline and pass candidate, including real RecListAnalysis and custom-discount alignment. These are subsystem checks, not a full-repository pass or native agent capture. Both evidence packages (50 files total) are R2-published and independently restore-verified. Original corpus record stays held.

## LensKit fresh synthetic capture

[Fresh attributed capture](../evidence/data/lenskit312-synthetic-trajectory-001/assessment.md) observes both complete edit preimages, reproduces both issue failures and captures the qualified repair with numerical checks and the three disclosed legacy-test failures. Projection validation passes: 29 messages, 12 charged calls, 12,964 input tokens and 5,012 shifted targets. An 8,192-token output reserve leaves 11,612 context tokens. All 28 evidence files (558,052 bytes), including the two earlier incomplete attempts, are R2-published and independently restore-verified. Task-specific grading and full admission remain outstanding; Corpus068 and its LensKit hold are unchanged. Docker API is responding at version 29.8.2; no manual startup intervention is needed.

## LensKit contract binding and wider test inventory

[Contract assessment](../evidence/data/lenskit312-synthetic-contract-grade-001/assessment.md) binds the exact synthetic patch to retained paired tests: four issue-contract fixes, with three legacy compatibility failures preserved. Three changed-patch controls reject. The local project suite passes 648 tests in 28.443 seconds with Torch enabled. [Default repository assessment](../evidence/data/lenskit312-full-repository-001/assessment.md) remains incomplete: baseline timed out after 240 seconds; candidate was not run. Separate collection succeeds with 367 unique nodes across 38 files, now recorded for bounded paired execution. Both packages (25 files, 78,811 bytes total) are R2-published and independently restore-verified. No production admission policy was relaxed, no corpus record was replaced, and no Runpod resources were used.

## Verified Linux serving-wheel release

[Wheel release and recovery helper](../evidence/data/vllm-wheel-release-001/assessment.md) preserve the qualified vLLM 0.19.1 wheel in R2. A fresh independent 433,132,506-byte restore passed exact verification before local removal, releasing 433,135,616 allocated bytes (about 413 MiB). Other SDK wheels and installed environments remain. The ten-file release evidence package is also R2-published and independently restore-verified. Restore this wheel before any deployment step that requires it; no model or training qualification follows from this storage result.

## Scoped Finder refresh

[Current File Provider diagnostics](../evidence/data/fileprovider-diagnostic-004/assessment.md) show no unresolved conflicts in the four inspected project folders. Source and documentation are recursively downloaded and uploaded; the root is syncing recent changes. The user-visible Finder error remains unconfirmed, and a retry on only the small zenithsync folder has been requested. No sync-database repair or bulk artifact hydration was attempted. Seven evidence files are R2-published and independently restore-verified.

## LensKit bounded full-inventory assessment

[Paired execution](../evidence/data/lenskit312-full-repository-002/assessment.md) scheduled all 367 default-collected nodes in 38 file groups per role. Baseline records 323 passed, 30 skipped, 12 incomplete and two failed; candidate records 326 passed, 34 skipped, three incomplete and four failed. Both item-item groups timed out. Candidate failures are the three reviewed legacy NDCG expectations and an accumulator Hypothesis health check also seen in baseline. Baseline has an additional flaky accumulator failure. Randomized order and unpinned seeds prevent interpreting pass-count differences as improvement. Missing data and optional dependencies account for recorded skip reasons where final JUnit reports are available.

The checker reconciles exact collection, stage observations, JUnit aggregates, source identities and container cleanup. Four altered-evidence controls reject. The [archive](../evidence/data/lenskit312-full-repository-002-archive/assessment.md) is R2-published and independently restored: all five archive-package files and all 472 extracted evidence members verify exactly. The follow-up plan records 20 paired retries with fixed seeds and 34 skipped-node reviews, not completed work. Both containers are removed. This is not full-repository acceptance or a model result; Corpus068, accepted alignment coverage and training admission remain unchanged.

## LensKit controlled retries and skipped-case review

[Fixed-seed per-node retries](../evidence/data/lenskit312-full-repository-003/assessment.md) execute all 20 selected cases without timeouts: baseline 14 passed, four skipped and two failed; candidate 11 passed, four skipped and five failed. The only paired differences are the three reviewed legacy NDCG expectations. Both roles reproduce the accumulator filtering health check and a timing-deadline failure. No assertions, deadlines or health checks were suppressed. Four altered-evidence controls reject.

The explicit [coverage ledger](../evidence/data/lenskit312-full-repository-003/coverage-ledger.json) selects 347 original outcomes and 20 controlled retries, accounting for all 367 nodes with no incomplete entries. Baseline totals 331 passed, 34 skipped and two failed; candidate totals 328 passed, 34 skipped and five failed. This is evidence selection across two protocols, not a single-run full-suite pass or model score. The five-file archive package and all 260 extracted members are independently R2 restore-verified.

[Skip prerequisite review](../evidence/data/lenskit312-skipped-fixtures-001/assessment.md) covers all 34 nodes: nonexclusive prerequisites are MovieLens 100K (20), MovieLens 20M (three), scikit-learn (seven) and explicit upstream disabling (five). One SVD case needs both 100K and scikit-learn. Dataset terms distinguish research use from redistribution/commercial permission; no new raw MovieLens data was downloaded or uploaded. All 17 review files are independently R2 restore-verified. Corpus068 remains unchanged and quarantined. No Runpod resources were used; both local test containers are removed.


## Workalendar alignment and Finder confirmation

[Workalendar review](../evidence/data/corpus068-task-alignment-013/assessment.md) accepts the requested registry API behavior: fresh pinned-image execution records baseline 0/20, reference 19/20 and candidate 20/20. The reference difference is warning caller location. Warning-as-error prevents delegation, so lookup-value equivalence is conditional on ordinary warning handling. The retained 11-case publisher comparison still matches; it was recomputed from recorded outcomes, not rerun. Documentation parity and whole-history quality remain separate. All 19 evidence files (63,061 bytes) were published to R2 and independently restored and verified. Accepted alignment coverage is now 33/51, with 18 unaccepted; full-corpus validation still rejects incomplete coverage. Corpus068 remains unchanged and quarantined, with no training approval or Runpod use.

The user subsequently confirmed “No error now” after retrying Finder Keep Downloaded on the small `zenithsync` source folder. This resolves that scoped user-visible check. It does not establish whole-repository download status or authorize hydration of large artifact placeholders. The earlier archived diagnostic remains unchanged.


## Dynaconf registration counterexample

[Fresh Dynaconf qualification](../evidence/data/corpus068-task-alignment-014/assessment.md) finds a material gap despite the retained 26-case publisher match. Across 9,216 finite ordered comparisons of 96 instances representing 48 structural rule descriptions, baseline matches 1,680, reference 9,216 and candidate 9,184. Candidate registration raises AttributeError after 24 distinct rules when absent/present `when` conditions are compared; reference registers all 48 once. The literal issue example is repaired, but that narrower success does not establish registration correctness. The selected task is held, and the admission validator rejects that decision.

Both the initial probe exception and completed exception-recording probe are retained. All 28 files (82,784 bytes) were R2-published and independently restored with exact verification; temporary restored copies were removed afterward. No test containers remain. Accepted alignment remains 33/51 with 18 unaccepted, now including explicit LensKit and Dynaconf holds. Corpus068 is unchanged and quarantined. This is finite local qualification, not a model score or a universal correctness proof. Next work is a corrected attributed Dynaconf repair with regression verification and fresh trajectory capture. No Runpod resources were used; P1 remains incomplete.


## Corrected Dynaconf candidate qualification

[New attributed candidate](../evidence/data/dynaconf413-repair-001/assessment.md) guards ordinary Validator comparisons by concrete type and compares combined validators through parent attributes and ordered children. Fresh actual-package checks pass all 9,216 finite comparisons and preserve exactly the first occurrence of each of 48 structural descriptions during registration. Candidate and reference pass all 26 publisher validator cases; baseline passes 24 and fails two. The argument is restricted to immutable acyclic structures with ordinary attribute equality, and preserves the historical equality-field selection. It is not semantic equivalence of arbitrary predicates or compatibility proof for custom subclasses.

Full original test invocation stops on missing Flask, Redis and hvac collection dependencies in both roles. An explicit continuation run preserves those collection errors while executing available tests: baseline and candidate have identical identities and outcomes, 255 passed, 19 failed and three collection errors. No timeout or tracked-source mutation occurred, and execution containers were removed. Full-repository acceptance remains false.

All 59 files (1,480,657 bytes) are R2-published and independently restore-verified. The temporary restored copy was removed after verification. This candidate is assistant-authored and reference-informed; a fresh attributed trajectory and replacement admission remain outstanding. Original Corpus068 Dynaconf remains held, accepted alignment stays 33/51, and no training or Runpod use is authorized by this result. P1 remains incomplete.


## Fresh Dynaconf synthetic trajectory

[Native capture and review](../evidence/data/dynaconf413-synthetic-trajectory-001/assessment.md) records both failures before editing, passes both afterward, passes all 9,216 finite structural comparisons and the 48-rule registration check, and passes 19 original validator tests. The prior 26-case publisher-patched qualification is separate retained evidence. Both edit preimages were observed, and applying the submitted patch reproduces the exact qualified candidate source bytes. The network-disabled container was removed.

The assistant-authored, reference-informed capture has 11 exchanges, ten charged calls and 25 messages; projection and all nine tool schemas match the retained protocol and installed signatures. Untruncated pinned tokenization yields 6,800 inputs and 2,467 shifted supervised targets, leaving 17,776 tokens after an 8,192-token output reserve. This is token fit, not GPU readiness or model performance.

All 17 files (187,204 bytes) are published to R2 and independently restore-verified; the temporary restore was removed afterward. Original Corpus068 and its Dynaconf hold remain unchanged. Task-specific admission integration, content/rights/split/runtime review and versioned replacement remain outstanding; full-repository acceptance remains false. P1 remains incomplete and Runpod was not used.


## Explicit synthetic V2 grading integration

[Fresh synthetic grading](../evidence/data/dynaconf413-synthetic-qualification-002/assessment.md) adds a mutually exclusive --synthetic-capture path to the V2 evaluator. It binds explicit authorship, snapshot/image, patch/history/schemas, captured exchanges, cleanup, call counts and original issue text without relabeling a synthetic capture as historical replay. Existing source-path restrictions, controls and post-execution identity checks remain. Fresh Dynaconf publisher grading passes all 26 candidate/reference cases against 24 baseline passes and the expected two failures.

The old snapshot verification rejected on stale verifier-code bindings. Fresh verification of the same image confirms the 511-file source manifest and sanitized commit history; no old receipt was changed. The complete project suite passes 652 tests in 27.010 seconds with Torch enabled and no skips. All 41 qualification files (119,747 bytes), including code snapshots and test logs, are R2-published and independently restore-verified; the temporary restore was removed afterward.

This enables direct grading of the synthetic patch but does not approve training or resolve full-repository failures/dependencies. Content review, generic synthetic-bundle admission integration and rights/split/runtime gates remain. Corpus068 stays unchanged with its Dynaconf hold; accepted alignment remains 33/51. P1 remains incomplete and Runpod was not used.


## Dynaconf content review and native budget accounting

[Revision 2](../evidence/data/dynaconf413-synthetic-trajectory-002/assessment.md) addresses two procedural omissions found in revision 1: nearby test-source inspection before edits and native budget-status inspection. The original capture is preserved. The fresh 31-message capture passes a complete content-review ledger, 9,216 finite structural checks, 19 original validator tests and a new 26-case publisher-reference grade. The submitted patch is byte-identical to revision 1.

This capture exposed and corrected a production accounting defect: get_status is uncharged in the installed native runtime, like submit_patch. The projection validator now follows that contract, with a regression test that rejects an inflated charged count. The full local suite passes 653 tests in 26.092 seconds with Torch enabled and zero skips. Capture totals are 14 exchanges, 11 charged calls, 7,708 input tokens and 2,519 shifted targets; context margin is 16,868 after an 8,192-token reserve.

All 50 files (308,816 bytes), including native runtime source evidence, code snapshots, grade, content ledger and test log, are independently R2 restore-verified. Temporary restore removed afterward; no Dynaconf execution containers remain. Content acceptance is assistant review, not independent human or training approval. Corpus068 is unchanged; generic bundle integration, versioned replacement and rights/split/runtime gates remain. P1 remains incomplete and Runpod was not used.


## Reusable V2 synthetic-bundle qualification

[Mechanical integration](../evidence/data/dynaconf413-synthetic-admission-001/assessment.md) now binds synthetic provenance, captured exchanges, source fixtures, task/snapshot identities, runtime receipts, recomputed publisher transitions, token arrays/audits and accepted content review in one reusable checker. Dynaconf revision 2 passes with no mechanical blockers: 7,708 inputs, 2,519 shifted targets and 11 charged calls. The result explicitly remains training_approved=false.

The seven new tests cover nonmutation, context policy, changed source/capture, false outcome summary, inconsistent tokens and wrong-grade content review. The full local suite passes 660 tests in 26.751 seconds with Torch enabled and zero skips. All seven evidence files (27,687 bytes) are independently R2 restore-verified, with the temporary restore removed afterward. The prior full-nodeid synthetic backend is unchanged.

Next is a versioned corpus replacement and ingestion requalification, not training. Corpus068 still contains the held original Dynaconf trajectory, so its accepted alignment remains 33/51. Rights, split isolation, full runtime gates and broader P1 work remain incomplete. No Runpod resources were used.


## Corpus069 replacement and restored ingestion

[Corpus069 integration](../evidence/data/corpus069-integration-001/assessment.md) replaces only the held original Dynaconf record with the reviewed synthetic revision 2. The other 50 records are unchanged. Totals are 978,548 inputs and 266,933 shifted supervised targets across 51 tasks and 50 repositories. All context reserves pass, minimum margin 210. Accepted task alignment increases to 34/51; 17 records remain unaccepted, including LensKit. All four training admission fields stay null and training loads reject.

All 103 payload files (10,838,848 bytes) and 32 integration/ingestion evidence files (185,075 bytes) are independently R2 restore-verified. The existing 42-file worker bundle still matches current repository counterparts. Original/restored scheduling matches exactly, with ten planned updates, 51 examples each once, eleven exact resume suffixes and eleven rejected corrupted counters. The real worker rejects quarantine before model access. Temporary restores were removed after verification and ingestion checks. No optimizer steps or Runpod use occurred; P1 remains incomplete.


## MkDocs section-index alignment

[Bound navigation review](../evidence/data/corpus069-task-alignment-003/assessment.md) accepts the selected positional list repair. Exact extracted function execution in the pinned image passes all 576 finite navigation trees; reference passes 567 and baseline 144. A prefix-collision example demonstrates the reference list.index mutation defect; selected code preserves the intended leaf correspondence. Four malformed-input diagnostics remain unchanged. All five retained publisher/integration outcomes still match after recomputation.

Fresh evidence is function-only: two preserved probes first failed on a historical path mismatch and then an unavailable ruamel.yaml import. No package-import success or new publisher run is claimed. The proof scope is finite acyclic nonaliased structures and literal prefixing, with path/URL normalization and idempotence excluded. All 33 evidence files (135,859 bytes) are independently R2 restore-verified, and execution containers are removed. Accepted alignment is now 35/51; 16 records remain unaccepted. Corpus069 remains unchanged and quarantined; P1 remains incomplete and Runpod was not used.


## ASDF converter tag-cardinality review

[Fresh actual-package checks](../evidence/data/corpus069-task-alignment-004/assessment.md) verify the selected warning-to-error repair across 1,024 combinations of exact-tag subsets, selector presence and direct/virtual inheritance. Candidate and reference have zero mismatches and warnings; baseline has exactly 67 of each. The set-count derivation, sum over k=2..4 of C(4,k)×3^(4-k)=67, matches observation. The check concerns distinct relevant tags and attribute presence; wildcard behavior, arbitrary callability and serialization are not claimed.

All 28 retained publisher outcomes match after recomputation. All 20 evidence files (67,259 bytes) are independently R2 restore-verified; temporary restore and execution containers are removed. Accepted alignment rises to 36/51, with 15 unaccepted. Corpus069 remains unchanged and quarantined; no training approval or Runpod use. P1 remains incomplete.


## Numba environment-value alignment

[Fresh actual-module checks](../evidence/data/corpus069-task-alignment-005/assessment.md) verify the selected return-value fix over 36 current/legacy/default combinations and three invalid prefix arguments. Candidate/reference have no value, warning or rejection mismatches; baseline fails the 27 current-variable-present cases. Empty strings remain present values, default identity is preserved, and deprecated NUMBAPRO values are ignored with the existing warning behavior. No GPU or arbitrary-warning-policy correctness is claimed.

The one retained publisher test matches after recomputation. All 20 evidence files (105,745 bytes) are independently R2 restore-verified; temporary restore and test containers are removed. Accepted alignment is now 37/51 with 14 unaccepted. Corpus069 remains unchanged and quarantined. P1 remains incomplete; no Runpod use.


## October 17 — PennyLane Exp step-preservation review

[Corpus069 alignment006](../evidence/data/corpus069-task-alignment-006/assessment.md)
binds the current history and native patch to fresh execution in the sanitized
snapshot. Candidate and reference pass 100 cases; baseline passes 20 because it
loses non-None step metadata. All 300 matrix comparisons per role agree with
explicit Pauli generators and SciPy expm at absolute tolerance 1e-12. SciPy may
also underlie the implementation, so this is a generator/construction regression
check, not an independent numerical algorithm validation. The retained 169-case
publisher comparison was recomputed, not rerun. Initial interpreter failure is
preserved alongside the successful attempt.

The 25-file, 217,582-byte evidence bundle was independently restored from R2 and
verified against its exact manifest. Temporary restore copies were removed only
after verification. Task alignment is now 38 accepted / 13 unaccepted; full
coverage still rejects and training approval remains zero. No production code
changed; this cycle exercised qualification scripts and real package execution,
not the full local regression suite. Runpod remains unnecessary.

Corrected the current readiness page's stale Corpus068 manifest digest to the
hash computed directly from Corpus069: 6bad23677fa222bf518b6f167af82cc6bf1f8c835e94b7e351c39ee513dd43cd.


## October 17 — PennyLane single-axis broadcast alignment

[Alignment007](../evidence/data/corpus069-task-alignment-007/assessment.md) verifies
the selected amended history and exact submitted patch against Corpus069.
Fresh sanitized-snapshot execution compares 60 circuit configurations against
explicit rotation matrices, Kronecker operators and CNOT basis permutations.
Candidate/reference pass 60/60; baseline passes 24/60. The baseline succeeds for
unbatched input and when batch size equals layer count, which can conceal the
axis-selection bug. Maximum candidate state error: 4.965068306494546e-16, under
the declared 1e-11 absolute tolerance. This is finite NumPy evidence; multi-axis
batches and general differentiation correctness are not claimed.

Recomputed retained grading covers 41 publisher identities and three declared
supplemental interface tests. No new interface/backend run is implied. Task
alignment is now 39 accepted / 12 unaccepted; full-corpus coverage still rejects.
Zero tokens are training-approved. All 20 files (128,337 bytes) in this evidence
bundle were R2-published, independently restored and exactly verified. Only the
temporary restored duplicate was removed afterward. No production source changes,
full local-suite rerun or GPU execution occurred this cycle. Keep Runpod stopped.


## October 17 — Sphinx caption-node alignment

[Alignment008](../evidence/data/corpus069-task-alignment-008/assessment.md) binds
the selected corpus history and native patch to fresh Sphinx integration runs.
Each document runs in a separate process. Candidate/reference satisfy ten required
cases; baseline fails four. The extra emphasized-caption observation still finds
zero misspellings in every role and is not counted as passing. Missing-image and
spelling warnings remain in the evidence. Retained grading matches eleven outcomes,
including one pre-existing docstring failure; it is not an all-green suite.

Task alignment is now 40 accepted / 11 unaccepted, with zero training-approved
tokens. The 20-file, 96,479-byte evidence bundle was published to R2, independently
restored and exactly verified; its temporary restored duplicate was then removed.
No production source changed, no full-suite rerun was warranted, and no GPU was
used. The previous 660-test local-suite result retains its documented scope.


## October 17 — Linkding option delivery alignment

[Alignment009](../evidence/data/corpus069-task-alignment-009/assessment.md) binds
the amended current history and patch to real child-process argv checks in the
sanitized snapshot. Candidate/reference pass all 77 cases; baseline passes two.
The cases include ten fixed strings, 64 seeded token vectors and three malformed
strings. Valid cases verify the complete argv, gzip payload and temporary-file
cleanup. The child is a controlled executable, not SingleFile or a browser; no
remote-page or user-agent acceptance claim follows. The assessment's network
exclusion refers to test execution; R2 archival does use the network.

Retained grading matches six reference outcomes. Task alignment is now 41 accepted
/ 10 unaccepted; all training gates remain closed. The 20-file, 143,979-byte
bundle was published to R2, independently restored and exactly verified. The
temporary restored duplicate was removed after verification. No production code
changed and no GPU was used; the full local suite was not rerun for this evidence-only
review. Runpod remains unnecessary.


## October 17 — Snowflake cancellation-command alignment

[Alignment010](../evidence/data/corpus069-task-alignment-010/assessment.md) binds
the current corpus patch to fresh real adapter imports with mocked query/cursor
boundaries. Candidate/reference pass 17 cases; baseline passes two. The command
matches Snowflake's documented session-level cancellation function. This is not
live cancellation, privilege, latency, race-condition or Ctrl+C-routing evidence.
The retained 38-case grade was recomputed, not freshly rerun.

Coverage is now 42 accepted / 9 unaccepted; training admission remains closed.
All 20 evidence files (67,445 bytes) were published to R2 and independently
restore-verified. The temporary restored duplicate was removed afterward.
No production code changed or GPU was used; no full local-suite rerun was needed
for this evidence-only review. Keep Runpod stopped.


## October 17 — Rally cleanup-default alignment

[Alignment011](../evidence/data/corpus069-task-alignment-011/assessment.md) binds
the current amended history and patch to fresh actual connector/session checks.
Candidate/reference pass all twelve absent/true/false × static/normal × SSL/plain
cases; baseline fails four default cases. All sessions and connectors close,
cleanup timers cancel, and no pending async tasks remain. The pinned runtime uses
aiohttp 3.11.18. This does not measure TLS leaks or performance. Code and
command-line documentation defaults agree. Retained grading matches 197 reference
outcomes; that publisher suite was reanalyzed, not freshly rerun.

Task alignment is now 43 accepted / 8 unaccepted; training remains closed. All
23 evidence files (96,928 bytes) were R2-published, independently restored and
exactly verified. Temporary restore data was removed afterward. No production
source changed, full local suite rerun or GPU session occurred. Runpod can remain
stopped while remaining task and admission work proceeds.


## October 17 — SoftLayer search routing alignment

[Alignment012](../evidence/data/corpus069-task-alignment-012/assessment.md) binds
the current history and native patch to 28 fresh actual CLI/local XML-RPC cases.
Candidate/reference pass all 28; baseline fails six. Exit codes, routing priority
and exact RPC arguments are checked. Empty-string-containing tuples remain truthy
and forwarded; meaningful query validation and remote search relevance are not
claimed. Retained grading matches four reference outcomes and was not rerun.

Task alignment is now 44 accepted / 7 unaccepted; training admission remains
closed. All 20 files (139,694 bytes) were R2-published, independently restored and
exactly verified. The temporary restore duplicate was then removed. No production
source changed, full local-suite rerun or GPU session occurred. Keep Runpod stopped.


## October 17 — PySyft equality/mutation alignment

[Alignment013](../evidence/data/corpus069-task-alignment-013/assessment.md) binds
the corrected selected history and native patch to twenty fresh actual-package
checks. Candidate/reference pass 20; baseline lacks the methods. Cases cover
scalar and broadcast equality, integers/floats/nonfinite/complex/empty inputs,
mutation identity and encrypted/conversion guards. In-place means tensor-object
mutation, not underlying-array alias preservation. NotImplemented is a returned
sentinel rather than a raised exception, following the explicit reference.
Retained grading matches 132 reference outcomes and was not freshly rerun.

Task alignment is now 45 accepted / 6 unaccepted; training remains closed. All
20 files (71,305 bytes) were R2-published, independently restored and exactly
verified. The temporary restored duplicate was removed afterward. No production
code changed, full local-suite rerun or GPU execution occurred. Keep Runpod stopped.


## October 17 — Berlin holiday label discrepancy preserved

[Fresh calendar reconciliation](../evidence/data/holidays2052-current-semantics-001/assessment.md)
compares 1,496 complete calendar configurations per base/reference/candidate role.
Both patches change exactly eight Berlin-2025 mappings by adding May 8, but their
labels differ: candidate uses the issue's short name, reference the anniversary
name. All other entries agree with baseline in the tested domain. The original
runner's exact-label assertion failed and remains preserved; separate reconciliation
verifies the actual difference. The official Berlin source confirms date and
jurisdiction, without establishing byte-identical naming. No acceptance ledger
change was made: 45 accepted / 6 unaccepted, zero approved training tokens.

All 18 files (4,146,076 bytes) were published to R2 and independently restore-verified;
the temporary restore duplicate was removed afterward. No production changes,
full-suite rerun or GPU execution occurred. Next integrate the label distinction
with exact corpus provenance and retained publisher grading before deciding
alignment. Runpod remains unnecessary.


## October 17 — Berlin issue alignment accepted with label distinction

[Alignment014](../evidence/data/corpus069-task-alignment-014/assessment.md) binds
the calendar evidence to current Corpus069. Reconstructing each exact executed
probe reproduces the receipt's source hash, including patch, snapshot and collector.
The issue requests the short holiday name used by the candidate. The publisher's
new German test checks date/subdivision membership, not label identity. Alignment
is accepted with the candidate/reference label difference explicitly retained;
there is no claim of full-reference or translation parity. Retained 43-case
comparison is recomputed, with no new runtime run this cycle.

Coverage is now 46 accepted / 5 unaccepted. Training remains closed. The five-file
review package (51,055 bytes) was R2-published and independently restore-verified;
the larger prior calendar bundle remains separately archived. Temporary restore
data was removed after verification. No production changes or GPU use occurred.


## October 17 — Hetzner exact whitespace-test source recovered

[Recovery and verification](../evidence/data/hcloud547-test-recovery-001/assessment.md)
restores the missing 4,407-byte test source by exact R2 content hash. Reconstructed
probe identities match all five retained variant execution receipts. Recounted Go
logs confirm candidate 13 metadata and 623 upstream test/subtest pass events; base
and mutants fail their intended boundary checks. The source explicitly covers
1,080 combinations plus method/failure checks. These are retained results, not
fresh Go execution or independent statistical samples. Current-corpus and publisher
join remains next; acceptance stays 46 / 51 and training remains closed.

The seven-file recovery package (18,345 bytes) was independently R2 restore-verified.
Temporary restored duplicates were removed afterward. No production changes,
new compiler run or GPU use occurred. Keep Runpod stopped.


## October 17 — Hetzner metadata alignment accepted

[Alignment015](../evidence/data/corpus069-task-alignment-015/assessment.md) binds
the current corpus record to retained publisher probes, raw Go logs and the
recovered independent test source. All 627 publisher test/subtest identities
resolve uniquely with exact outcome coverage: candidate/reference pass 627;
baseline fails five. Probe hashes include both repair and test patches. Historical
controls cover boundary trimming and reject three incorrect variants. No new Go
execution or external metadata-service validation is claimed.

Task alignment is now 47 accepted / 4 unaccepted; training remains closed. All
five review files (50,553 bytes) were R2-published and independently restore-verified.
Temporary restored duplicates were removed afterward. No production changes or
GPU use occurred. Keep Runpod stopped.


## October 17 — AWS X-Ray selected parser freshly checked

[Fresh parser evidence](../evidence/data/awsxray70-current-parser-001/assessment.md)
applies the exact native patch to retained base source and verifies resulting
bytes. Node v20.14.0 runs 4,320 cases per variant (two versions, three configurations,
720 field permutations). Candidate passes all; baseline and three mutants show
the intended version/field failures. Checks preserve configuration and reservoir
values. Wildcard sampling/file loading are explicitly stubbed out, so this is
parser evidence rather than request matching or stochastic-performance evidence.
Current-corpus and publisher joins remain pending; acceptance stays 47 / 51.

All fourteen files (42,927 bytes) were R2-published and independently restore-verified.
Temporary restored data was removed afterward. No production changes or GPU use
occurred; training admission remains closed. Keep Runpod stopped.


## October 17 — AWS selected-history provenance and publisher checks

[Alignment016](../evidence/data/corpus069-task-alignment-016/assessment.md) recovers
Corpus069's selected history003/native006 and missing publisher task from R2 by
exact hashes. Selected patch bytes equal graded replay004; histories are explicitly
different. Reconstructed probe hashes bind repair and publisher tests. All 321
Mocha full-title outcomes are recounted, including every match for ambiguous short
titles; candidate/reference pass 321 and baseline fails one. This is retained-suite
verification, with fresh parser evidence separately scoped. Task alignment is now
48 accepted / 3 unaccepted; training admission remains closed.

All 18 files (267,339 bytes) were published to R2 and independently restore-verified.
Temporary restored duplicates were removed afterward. No production changes,
new full runtime suite or GPU execution occurred. Keep Runpod stopped.


## October 17 — KubeVirt missing-secret alignment accepted

[Alignment017](../evidence/data/corpus069-task-alignment-017/assessment.md) recovers
exact selected history/attempt artifacts and raw grading files from R2. Reconstructed
probes and recounted Go logs verify the five declared unit-suite entrypoints;
the controller suite fails on baseline and passes for candidate/reference. The
publisher regression exercises reconcileDelete with nil DataSecretName and checks
successful finalizer removal. Thirteen packages include eight without tests;
live-cluster e2e is explicitly excluded. No new Go execution or cluster-level
acceptance is claimed.

Task alignment is now 49 accepted / 2 unaccepted. Jsons and LensKit remain held;
rights, privacy, split and training gates are still separate and closed. All 55
files (304,857 bytes) were R2-published and independently restore-verified. Temporary
restored duplicates were removed afterward. No production changes or GPU use.
Keep Runpod stopped.


## October 17 — Jsons literal issue reproduction verified

[Fresh reproduction](../evidence/data/jsons86-literal-reproduction-001/assessment.md)
checks the literal `A('abc')` issue separately from three annotation-conforming
tuple inputs in pinned Python 3.7.16. All four reproduce exact SerializationError
messages on the base snapshot and produce the expected decoded JSON with the
candidate patch. Source remained unchanged by tests; both containers were removed.
The string becomes a character list, which is historical serializer behavior,
not annotation-conformity validation. The fail-closed verifier checks exact
outcomes and input/probe identities.

All 15 files (15,365 bytes) were R2-published and independently restore-verified;
only the temporary restored duplicate was deleted. This resolves the reproduction
ambiguity but does not approve the old history. A fresh attributed native capture,
regrading, tokenization and content review remain required. Corpus069 stays
unchanged at 49 accepted / 2 unaccepted task alignments, with zero training-approved
tokens. No production code change or GPU use; keep Runpod stopped.


## October 17 — Fresh Jsons synthetic capture and grading

[Selected capture002](../evidence/data/jsons86-synthetic-trajectory-002/assessment.md)
replaces the proposed use of the poor-quality old teaching history with a freshly
executed assistant-authored, reference-informed candidate. Its 29 messages include
13 exchanges (10 charged calls), source/helper/test inspection, four exact baseline
failures, two focused edits, four successful reproductions, 126 finite API checks,
19 original tuple/list test passes, submission and bounded final prose. Separate
fresh base/reference/candidate grading matches all ten publisher cases. No model
was evaluated. Attempt001 failed during setup and is retained with cleanup evidence.

Native encoding verifies 8,118 input tokens and 2,152 shifted supervised targets;
16,458 tokens remain after the 8,192 output reserve. Nine schemas and exact history
projection are checked. Content review is assistant review, not independent human
review. All 53 files (298,285 bytes) are R2-published and independently restore-verified;
the temporary restored duplicate was removed only afterward.

Next: bind this legacy evaluator's synthetic capture through a reusable admission
validator before corpus replacement. Existing V2 and replay-only admission paths
must not be bypassed or confused. Corpus069 remains unchanged, 49/51 task alignments
accepted, zero training-approved tokens. No production code changed this cycle;
the prior full local suite was not rerun. Runpod remains unnecessary.


## October 17 — Shared legacy synthetic admission validator

[Implementation and verification](../evidence/data/legacy-synthetic-admission-001/assessment.md)
adds a separate legacy entry point to the shared publisher admission checker.
Legacy reports require an explicit format and all four transition categories;
V2 remains compatible. Tests reject format interchange, missing categories and
false summaries, and accept a correctly declared stable failure without training
approval. A regression test confirms the existing projector rejects calls after
submission; no redundant production change was retained for that invariant.

All 664 discovered local tests passed across two runs: 647 in full discovery,
then the 17 skipped opt-in Torch tests explicitly enabled and passed. No GPU run.
Ten evidence files (54,589 bytes) were R2-published and independently restore-verified;
the temporary restored duplicate was removed. Current source/test snapshots and
both test logs are archived.

The real Jsons capture still needs a complete source-bound task document and
canonical grade/review bindings before this checker can qualify it. Preserve
prior immutable evidence. Corpus069 remains unchanged at 49 accepted / 2
unaccepted task alignments and zero training-approved tokens. Keep Runpod stopped.


## October 17 — Corpus070 integrated and independently restored

Jsons now passes the reusable legacy synthetic admission checks against its exact
source issue and fresh retained controls. The source shard was SHA256-verified in
memory; no 109 MB local shard copy was created. The canonical grade explicitly
records schema adaptation, with no new execution claim or replay relabeling.
The 38-file admission bundle (81,145 bytes) is R2-published and restore-verified.

Corpus070 replaces only Jsons, preserving the other 50 records. It contains 51
tasks, 962,448 input tokens and 263,216 shifted supervised targets. Task alignment
is 50 accepted / one unresolved (LensKit). All 103 payload files (10,662,970 bytes)
were independently restored; current worker sources and restored schedules match.
Nine planned updates cover all examples once with no overshoot. Ten resume
boundaries reproduce exact suffixes and reject corrupted counters. The worker
rejects quarantine before model access or output creation. All admission fields
remain null; zero tokens are training-approved.

The 32-file integration bundle (197,869 bytes) is also independently restore-verified.
Temporary restored duplicates were removed after checks. Current readiness table
and manifest pointer now identify Corpus070, SHA256
`dacc63ba2161addb027eecdb270bc7db1792b4614b412569e4c5993778179754`.
No production source changes this cycle; prior 664-test verification remains the
latest local suite. Next: resolve the LensKit contract/reference discrepancy and
continue rights, privacy, split and runtime admission work. Keep Runpod stopped.


## October 17 — LensKit publisher reference gap measured

[Fresh three-way contract comparison](../evidence/data/lenskit312-reference-contract-002/assessment.md)
applies base, publisher reference and full-issue candidate to the same pinned
runtime and four unchanged assertion-based tests. Results are 0/4, 1/4 and 4/4
passes respectively. Reference fixes explicit scalar cutoff but fails the original
implicit-cutoff request and both bulk consistency checks. Exact source SHA256,
module origin, raw outcomes, unchanged tracked source and cleanup are verified.

Under historical rank weights, the issue's implicit example is (3+5)/(5+4)=8/9.
The former denominator includes the third ideal item and yields about 0.73443,
which the issue explicitly rejects. This supports a documented contract distinction,
not relabeling old tests or claiming a full-suite pass. The three legacy expectation
failures and broader compatibility limits remain recorded. A first import-path
failure was retained; the successful retry checks actual checkout import origin.

Next: implement explicit issue-contract admission binding the source task, selected
synthetic capture, contract comparisons, finite numerical oracle and compatibility
ledger. Keep reference-equivalence checks strict. Corpus070 remains unchanged,
LensKit held, and training unapproved. No production code changes or GPU use.

All 29 comparison-evidence files (57,493 bytes) were R2-published and independently
restore-verified. The temporary restored duplicate was removed afterward.


## October 17 — Explicit contract outcome policy implemented

[Contract checker](../evidence/data/lenskit312-contract-policy-001/assessment.md)
requires exact three-role contract coverage and paired compatibility coverage.
Declared intentional pass-to-fail changes need a rationale and links to supporting
contract cases; all unexpected changes remain blockers. It preserves raw failures,
skips and reference disagreement and grants no training approval.

LensKit's four contract checks pass, and its three observed legacy changes match
the declared normalization change. Actual compatibility remains 78 passed / three
failed. Source hashes and captured patch bind the same candidate. The broader
367-node ledger and its 34 skips/two shared failures remain separate limitations.
No full-suite LensKit acceptance is claimed.

Seven new tests passed, and the complete local suite passed 671 tests in 28.042
seconds with Torch enabled and zero skips. Next: full issue-contract bundle
admission binding source task, history, tokens, numerical oracle and compatibility
ledger. Corpus070 is unchanged, LensKit remains held, and Runpod remains off.

All eight evidence files (27,812 bytes) were R2-published and independently
restore-verified; the temporary restored duplicate was removed afterward.


## October 17 — LensKit capture corrected against its prompt

[Corrected native capture](../evidence/data/lenskit312-synthetic-trajectory-002/assessment.md)
binds the original issue recovered from the SHA256-verified archived source shard.
The 101,556,119-byte shard was read in memory only. The former native003 capture
was found to read nearby tests after editing and omit get_status; preserve it as
superseded evidence, not an admitted teaching trace.

Fresh native004 reads source preimages and nearby tests before editing and records
both budget checks. It has 33 messages, 15 exchanges and 12 charged calls. Both
issue reproductions pass after the edit, all 6,969 finite numerical cases pass,
and three legacy failures remain visible. Its patch is byte-identical to the
qualified candidate. Schema/projection/observation checks pass. Native tokenization
has 13,225 inputs and 5,028 shifted targets, with 11,351 context margin after the
output reserve. This is assistant-authored, reference-informed content.

Next: bind this corrected history through full issue-contract bundle admission
without concealing reference disagreement or compatibility failures/skips. No
production code changed; the prior 671-test suite remains the latest regression
result. Corpus070 remains unchanged and LensKit held. Keep Runpod stopped.

All 20 corrected-capture/source-task files (328,605 bytes) were R2-published
and independently restore-verified. The temporary restored duplicate was removed.


## October 17 — LensKit contract bundle qualification passed

[Task-specific admission assessment](../evidence/data/lenskit312-contract-admission-001/assessment.md)
binds the exact source task, corrected native004 history, patch/source, token arrays,
finite numerical observations, contract outcomes and retained compatibility ledger.
Both original compatibility assessors were rerun read-only against raw collection,
pytest stage and JUnit evidence; exact immutable reports matched. The full 367-node
merged ledger was reconstructed, retaining candidate 328 passes, five failures and
34 skips. Only three declared normalization changes differ from the baseline.

The bundle passes mechanical checks under the explicit issue contract, with
reference_equivalent=false and training_approved=false. Five parsed-evidence
mutation controls reject. Assistant content/task review accepts the corrected
history within those limits; this is not independent human adjudication or a
single-process repository pass. Corpus070 remains unchanged until verified
replacement assembly; next step is Corpus071 and its R2 restore/ingestion checks.
No production code changes or GPU use this cycle; keep Runpod stopped.

All 11 admission-evidence files (34,862 bytes) were R2-published and independently
restore-verified; only the temporary restored duplicate was removed.


## October 17 — Corpus071 assembled with 51/51 task alignment

[Corpus071 integration](../evidence/data/corpus072-integration-001/assessment.md)
replaces only LensKit with corrected native004 and explicit issue-contract provenance.
The other 50 records remain unchanged. All 51 task reviews pass exact coverage;
each of 51 leave-one-out controls rejects. Reference disagreement and all LensKit
compatibility limitations remain visible. This is not training admission.

The manifest SHA256 is
`42da2d372f908d00b72a3f7d89af9b5fa082f8caeb8a4307bd77cfc363a2de75`.
There are 954,733 input tokens and 262,593 shifted supervised targets. All examples
fit context plus output reserve. The 103-file payload (10,575,597 bytes) was
R2-published and independently restored. Restored worker sources match; schedules
are byte-identical, nine updates cover all examples once, all ten resume boundaries
match, and corrupt counters reject. Quarantine blocks the real worker before model
access. The temporary restored corpus was removed after verification.

All four manifest gates remain null and zero tokens are training-approved. Current
readiness now points to Corpus071. Next: current-content rights/privacy notices,
split validation, qualified-data scaling and remaining runtime limitations. No
production code changed this cycle; the 671-test suite remains the latest local
regression evidence. No GPU use; keep Runpod stopped.

The 32-file integration package (211,404 bytes) is also R2-published and independently
restore-verified. Its temporary restored duplicate was removed afterward.


## October 17 — Current Corpus071 material and indicator coverage

All 51 exact current histories were located locally with no R2 recovery or large
artifact download. A content delta identifies 46 unchanged and five changed/new
histories since Corpus065. Nested history scanning and independent token-array
decoding both yield zero configured credential indicators. This is a bounded
indicator result, not universal privacy clearance.

All 13 contact-pattern occurrences are reviewed: 12 carried only by exact history,
location and matched-text hash; one new mypy_extensions package-author metadata
occurrence classified as attribution. No history bytes were changed. Reports
retain only locations and hashes, not contact values. Whole-history privacy and
notice coverage remain unapproved. Next: observed-material notice bindings for
changed histories and contextual privacy review. Corpus071 remains quarantined;
no production changes or GPU use.

All 13 inventory/screen/review files (152,470 bytes) were R2-published and
independently restore-verified. The temporary restored duplicate was removed.


## October 17 — Current Jsons source/notice binding verified

[Snapshot extraction and observation comparison](../evidence/data/jsons86-current-notice-binding-001/assessment.md)
maps the current capture's two structured file reads and shell helper excerpt to
exact tracked source line ranges. Snapshot commit/tree and clean source are checked.
The root LICENSE matches retained upstream bytes, as do both implementation files
covered by that source receipt. All three pre-edit source-printing observations
are accounted for; the container was removed.

This is a current repository-source-to-notice binding, not approval for all dataset,
issue-text, dependency or embedded material. Histories and production code remain
unchanged. Next: the other four changed/new histories' observed materials and
contextual notice/privacy coverage. Corpus071 remains quarantined; no GPU use.

All 13 source/notice evidence files (39,163 bytes) were R2-published and independently
restore-verified. The temporary restored duplicate was removed afterward.


## October 29 — Corpus admission closed, corpus moved to R2, public task pool screened

[Corpus072 is training-admitted](../evidence/data/corpus072-admission-001/admission-receipt.json).
Promotion is immutable: the quarantined corpus was never edited. A complete new
tree was staged from the R2-restored payload, its 103 example files were copied
with post-copy identity verification, eight reviewer evidence documents were
copied in, one receipt per gate was written binding the corpus content identity,
and the result was published only after `IndexedCorpus(purpose='training')`
accepted it. Admitted manifest `fa984ca3ff1006e2cf7817a8ee67f613fb4e37a5b603bdc6d5e61b586f623887`;
content identity `c081880c71b9f78ffb4fdcf319d0959e8d7dfcb39878b8ac06f510f2d088f103`
unchanged, which is what lets the receipts bind it. The regenerated schedule hash
`4664ecf632b35fad11dfa6d9d3e1ff19cfddb352816e99bb8750c8167cd1f06b` reproduces the
previously recorded value exactly, independent corroboration that promotion
changed no training-relevant byte. `preflight_corpus_run` — the real worker's own
preflight — accepts the staged tree, the schedule and
`configs/p1-corpus-qualification.json`.

The live R2 round trip ran in order: restore the quarantined payload (103 files,
10,578,444 bytes) → promote → publish the admitted corpus (115 files, 10,782,715
bytes, artifact manifest `50c8ee9398ff6c3a186ef558c08c72365060d41e3e796950cd5d7dd2b8eab323`)
→ restore it again with `--purpose training`, loader reporting
`training_admitted: true`. No corpus bytes were retained on the development
machine; every step ran in a session scratch directory. Publication uploads
exactly the file set the corpus manifest reaches, so a stray credential, cache or
scratch file fails the publish instead of reaching the bucket.

[Two independent verification layers agree](../evidence/data/corpus072-admission-001/two-layer-verification.json).
`zenithsync.corpus_audit` re-derives every digest, per-example supervised-target
count, duplicate check, split-isolation check, context margin and gate binding
from stored bytes without calling the loader, collator or schedule iterator. The
layers agree on all eight shared quantities, all 51 examples were refetched and
rechecked, schedule coverage is exactly one-to-one, and the minimum context
margin of 210 tokens is reproduced from a wholly separate code path.

[A screened public task pool](../evidence/data/task-pool-v2-python-001/report.json)
addresses the data-scale blocker's CPU half. From the pinned SWE-rebench V2
projection (revision `10483de0f50fe5da545942705a76c6150171af7f`, metadata
`701f75d5eed78ffcce6355f6ea4093d63f5c9022188c1d7f018e4d9b5d2b15b4`, 32,079 rows):
4,818 eligible Python tasks across 507 repositories and 439 owners; refusals were
24,524 non-Python, 1,706 placeholder licence labels, 466 already development-exposed
repositories, 348 absent licence fields and 199 repeated repository base commits.
2,966 were selected under ≤12-per-repository and ≤24-per-owner caps and split into
[repository- and owner-disjoint cohorts](../evidence/data/task-pool-v2-python-001/cohorts.json):
train 2,076 (277 repositories), development 445 (112), confirmation 445 (118).
Owners are the indivisible unit, because a fork, backport or sibling package inside
one owner is the contamination path that splitting by task misses.

[Campaign arithmetic](../evidence/data/campaign-plan-001/report.json) quantifies why
that pool matters: 50,000,000 supervised targets against Corpus072's 262,593 is a
repetition factor of 190.41 over 191 whole epochs and roughly 181,789,499 processed
input tokens. No duration or cost figure was produced, because no throughput has
been measured for this configuration at a realistic sequence length; the planner
refuses to forecast without one.

What this does **not** establish: rights clearance on either corpus, the truth of
any reviewer's conclusion, that the remaining pool is unseen, that peak memory at
the corpus's longest example (24,366 input tokens) fits an 80 GB card, or any
learned improvement. The local suite is 944 tests, zero skips, Torch enabled,
27.605 seconds on the full stack; on a stdlib-only Python 3.13.7 it collects the
same 944 and passes with 70 skips. Python 3.11 or newer is required: macOS's
/usr/bin/python3 is 3.9 and cannot import `zenithsync.contracts` at all. No GPU training ran and no Runpod resource was created, started,
stopped or modified. Full detail, including the refused OpenHands translation
rules and the remaining work in order, is in
[the training unblock and data-scale cycle](42-training-unblock-and-data-scale.md).
