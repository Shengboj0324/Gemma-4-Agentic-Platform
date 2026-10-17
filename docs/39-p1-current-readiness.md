# Current P1 readiness

Updated October 16, 2026. **P1 is incomplete. Keep Runpod stopped.**

This page describes the latest verified state. The previous 4,129-line status
ledger, including subsequent updates, is preserved without content changes in
[the historical readiness ledger](39-p1-readiness-history-through-2026-10-16.md).
The [implementation journal](40-p1-implementation-journal.md) records work over
time. Historical successes apply only to their recorded inputs and scope.

## Current evidence

| Area | Verified result | Limit |
|---|---|---|
| Local regression | [647 tests passed](../evidence/data/corpus068-integration-001/synthetic-admission-full-suite-002.log) in 25.620 seconds with Torch enabled and no skips, including six new synthetic-projection checks. | CPU and reduced-model checks do not establish full-model GPU correctness. Historical 641-test snapshot predates the new module. |
| Inference transport | [Real HTTP framing controls](../evidence/p1/inference-framing-001/assessment.md) reproduce five previous failure cases and verify rejection after the fix; three valid framing variants preserve response bodies. Evidence independently restored from R2. | Diagnostic nonstreaming transport only; no new model-generation or streaming qualification. |
| Evaluation accounting | [JUnit consistency audit](../evidence/p1/junit-accounting-001/report.json) preserves the retained 324-case Requests comparison and rejects eight contradictory aggregate reports. Supplied failure/error/skip counts must match case outcomes. | Existing report reanalysis, not a new repair run or official hidden-grader qualification. |
| Repaired mypy example | [Fresh replay and token evidence](../evidence/data/mypy47-replacement-001/report.json): readable source correction, 40 calls, 84 messages, 22,634 input tokens and 7,559 supervised targets. Exact final source matches the expanded local controls and all 11 publisher cases. | Reference-informed derivative, not an independent held-out solve. Earlier defects and failed/superseded attempts remain preserved. |
| Task alignment | [Corpus068 review](../evidence/p1/corpus068-ingestion-001/task-reviews.json): twenty unchanged task reviews rebound by exact record identity, plus the reviewed synthetic emcee replacement; 21 accepted and 30 pending. Full-corpus validation rejects partial coverage. | HyP3 preserves an empty-batch warning that the reference removes; accepted issue alignment does not establish warning-policy parity or whole-history quality. Calendar/Pytypes/Munch/Gitignore/Importlab retained controls are bound by exact patch-output comparisons; no new runtime control run or corpus admission receipt issued. |
| Spline mathematical audit | [Exact projection audit](../evidence/data/csaps3-exact-projection-audit-001/assessment.md): 54 rational systems, 1,791 entries; selected/control patch outputs identical. Zero smoothing selects the weighted affine least-squares projection under stated assumptions. R2 independently restore-verified. | Finite algebraic checks plus conditional derivation, not universal floating-point correctness. Separate two-point metadata behavior documented; Csaps semantic alignment accepted; native publisher grading and mechanical/training admission remain separate. |
| Jsons replay budget | [Current-content audit](../evidence/data/jsons86-current-budget-audit-001/assessment.md) binds the selected history and recounts 42 charged calls, exceeding the local 40-call qualification policy. | Remains pending/quarantined. [Replay006 and native token audit](../evidence/data/jsons86-context-repair-001/report.json) now satisfy 40 calls and 24,504 input tokens plus 8,192 reserve, with only 72 tokens spare. Same patch and checks preserved. [Fresh ten-case grading and mechanical checks pass](../evidence/data/jsons86-native-qualification-001/report.json). Current corpus still contains the old trace. [Whole-history review](../evidence/data/jsons86-history-quality-001/assessment.md) is complete and rejects training-quality approval; any replacement needs a fresh attributed trajectory and renewed checks. |
| Context reserve | Corpus068 array recount: all 51 fit the existing input-plus-8,192 reserve envelope; minimum margin 210 tokens. Emcee replacement has margin 16,538. | Local whole-history policy only, not measured generation KV memory or GPU fit. |
| Current corpus | [Corpus068](../evidence/data/corpus068-integration-001/assessment.md): 51 tasks, 50 repository groups, 991,139 input tokens, 271,284 shifted supervised targets. Emcee replaced with explicitly synthetic content; other 50 records unchanged. Corpus R2-published and independently restore-verified. | Quarantine only; **zero training-approved tokens**. |
| Ingestion | [Corpus068 restored-worker checks](../evidence/p1/corpus068-ingestion-001/report.json): all 42 deployment files match current repository counterparts; local/restored schedules agree; worker rejects quarantine before model access. | No optimizer steps, full-model execution or training admission. |
| Resume scheduling | [Corpus068: ten planned updates, eleven resume boundaries](../evidence/p1/corpus068-ingestion-001/resume-verification.json): every remaining schedule reproduced exactly; eleven corrupt counters rejected; all 51 examples appear once with zero target overshoot. | Finite schedule recovery only, not full-model optimizer/checkpoint recovery. |
| Source provenance | [All 51 Corpus066 source metadata joins](../evidence/data/corpus066-attribution-index-001/report.json); [Dynaconf canonical commit tree](../evidence/data/dynaconf-canonical-lineage-003/report.json) matches its replay snapshot and current history. | The old Dynaconf URL now points to a different mirror. Canonical content verification does not make the URLs equivalent. |
| Corpus065 histories | [All 50 exact histories located](../evidence/data/corpus065-history-material-002/report.json); two recovered from R2 and hash-verified. | Material inventory is not full notice/privacy approval. Shell observations need separate coverage. |
| Encoded credential indicators | [Expanded screen](../evidence/data/corpus065-nested-credential-screen-001/report.json) passes all 50 hash-bound histories. Nested JSON and duplicate keys are inspected; decoding limits fail closed. [Current source verification](../evidence/data/corpus065-nested-credential-screen-001/current-source-verification.json) also confirms all 42 deployment files match. | Finite indicator coverage only; no secret-free or whole-history privacy guarantee. |
| Contact indicators | [12 occurrences reviewed](../evidence/data/corpus065-contact-review-001/report.json): eight software attribution, two decorator false positives, two article contacts. [Article-specific review and attribution](../evidence/data/pubmed89-article-review-001/report.json) completed. | No full-history privacy clearance or general secret-free guarantee. |
| Embedded Runpy component | [Pinned upstream comparison](../evidence/data/runpy17-embedded-source-001/assessment.md): all five logging methods match upstream syntax trees; the current corpus observation contains all 131 source lines with the BSD attribution preserved. | Whole-file differences recorded; full BSD license text, separate SQL filter, other notices and training admission remain unresolved. |
| Missing dependency notice | [ptvsd 3.0.0 notice recovery](../evidence/data/ptvsd300-notice-001/report.json): seven runtime files match the verified release; headers and license preserved. | Other package/source notice coverage remains separate. |
| Transfer evidence integrity | [Receipt recovery](../evidence/p1/ingestion-receipt-recovery-002/report.json) restores two overwritten local metadata members in Corpus065/066 ingestion evidence; all 51 listed members across Corpus065–067 rechecked. [New disjoint verifier](../evidence/p1/ingestion-receipt-recovery-002-verification/verification.json) exercised on a real R2 round trip. | Legacy bundles retain extra metadata files; recovery validates manifest-listed members. New verifier requires exact inventories and separate metadata trees. |
| Storage | Corpus, integration, ingestion and recent review packages published and independently restore-verified in R2, including the [latest 27-file alignment update](../evidence/data/corpus067-task-alignment-011-verification/verification.json). [Duplicate package cleanup](../evidence/data/shared-debs-release-001/report.json) released 164.2 MiB; [redundant native archives](../evidence/data/native-archive-release-001/report.json) removed a further 114.0 MiB of allocated file blocks after fresh R2 restores and verification of all 129 inner members. | Retained primary data still occupies disk; R2 backups are not a claim that every local byte can be deleted. |
| Finder | [Current diagnostic](../evidence/data/fileprovider-diagnostic-003/report.json): inspected folders uploaded with no reported conflicts; source/docs/evidence recursively downloaded. | User-visible error still needs confirmation. About 24.8 GB of cloud-only placeholders make whole-repository Keep Downloaded unsuitable while storage is tight. |

Corpus manifest SHA256:
`d53098963010a7aa7dddb4e78c34ed2f5726b5d49478e49273c379fb4ffb0a0e`.

## Remaining work, in dependency order

1. **Finish current-content admission coverage.** Use the exact-history inventory
   to bind observed repository and dependency files to applicable notices. Carry
   separate embedded notices, including the PubMed article and Runpy BSD header.
   Complete contextual privacy review without silently rewriting observations.
2. **Complete task and split review for the intended training release.** Record
   exact task/repository coverage, repository-family grouping and reviewed duplicate
   flags. Freeze held-out evaluation before optimization. Existing lexical checks
   and repository IDs alone do not prove semantic independence.
3. **Scale the qualified data pool.** Measure admitted tasks, repository diversity,
   supervised targets and rejection reasons across acquired datasets. The current
   271,284 targets are a qualification pool, not evidence of sufficient data for
   three 50M-token candidates. Repeated exposure is not additional unique data.
4. **Close local serving/evaluator limitations.** The official Requests evaluator
   previously imported an installed package instead of checkout edits. Preserve
   the source-origin guard and investigate official parity. Tool-call variability
   and streaming also remain unqualified. See the [acceptance checklist](26-p1-acceptance-checklist.md).
5. **Prepare a bounded GPU qualification session.** Bind the exact code, dependency,
   model, corpus and configuration manifests; restore-test required assets and
   run applicable local checks. Only then request the user's Pod restart and a
   fresh session spending/time limit.

Corpus068 retains the prior mypy derivative and replaces emcee with a fresh assistant-authored, reference-informed synthetic trajectory. Its content-bound token audit preserves that provenance. All four Corpus068 admission fields remain null:
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

For Finder confirmation, retry Keep Downloaded only on the small `zenithsync`
source directory. No sync-database repair or successful GUI retry is claimed.

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

[Integration evidence](../evidence/data/corpus068-integration-001/assessment.md) supersedes earlier statements that Corpus067 is current. Synthetic mechanical checks pass; 50 unaffected records are exact. [Corpus068 ingestion/resume and review rebinding](../evidence/p1/corpus068-ingestion-001/assessment.md) are now verified within their finite scope. Task review remains partial at 21 accepted/30 pending; historical Corpus067 results remain historical.
