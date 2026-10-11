# Current P1 readiness

Updated October 10, 2026. **P1 is incomplete. Keep the Runpod GPU stopped.**
No real training corpus is admitted and no learned coding-performance gain has
been demonstrated. The latest completed local integration is corpus 033, including the explicitly corrected
Lmfit, Munch, Importlab and Apispec replays and their diagnostic/compatibility checks.

This file is the current acceptance summary. Cycle details, failed attempts and
superseded results are preserved in the [implementation journal](40-p1-implementation-journal.md).
The [implementation plan](12-continuous-implementation-plan.md) retains the phase
scope and campaign assumptions. Update this summary and the journal after each
cycle; do not append historical logs to this summary.

## Training-content review — October 11, 2026

Corpus 033 remains quarantined. Contextual review now covers all 44 lexical matches
across 23 flagged histories; 145 exact selected-message bindings were verified.
Six histories had no lexical match, which is not semantic approval. Recursive
argument inspection found no nested string values in these 29 histories.

The [correction queue](../evidence/data/corpus033-claim-review-004/correction-queue.json)
requires explicit claim corrections for the Signac622, Lenskit312 and CloudEvents172
original histories. Lmfit487 completion wording and Importlab23 changed expectations
need scope/contract review. Six other histories have diagnostic-quality follow-ups.
Conditional success, explicitly negated guarantees and preserved failed attempts
are distinguished from unsupported claims; neither keyword counts nor exit code
alone determine correctness. Full content and admission review remains outstanding.

This queue is evidence, not an admission mechanism: the existing quarantine gate
continues to deny training. No corpus bytes, original histories or earlier review
reports were rewritten. Corrected derivatives require explicit provenance, fresh
replay and renewed grading, token and content qualification. Rally1469 remains a
separate held candidate outside corpus 033.
The complete 47-file review chain is uploaded and restore-verified in R2.

Lenskit's [fresh amended replay](../evidence/data/lenskit312-amended-review-001/report.json)
completed 26 charged calls with verified container removal. Its 56-message history
attributes all three amended actions explicitly, preserves one 30-second timeout,
and retains the same source patch. Finite completion checks again report 5,850
metric cases and 4,875 suffix checks. Token audit: 19,836 input, 5,644 supervised,
4,740-token margin after reserving 8,192 output tokens. Replay and projection now
verify original/derived action bindings and bind completion to the derived list.
The 435-test local suite passes with 17 skips. Independent derivative grading,
mechanical admission and full content review remain pending; corpus 033 is unchanged.
The 26-file implementation/replay archive is uploaded and restore-verified in R2.

## Storage status

Completed data/evidence bundles are published incrementally to R2; this is not a
backup of every local file. The PennyLane dependency archive is now restore-tested
(107 files, 1,005,376,281 bytes). Recoverable wheel caches were evicted after hash
and open-handle checks; historical wheel-cache paths must be restored before reuse.
The model, datasets, recipes, Docker images and containers were preserved.
See the [recovery receipt](../evidence/data/storage-capacity-audit-001/backend-restore-receipt.json)
and [eviction receipt](../evidence/data/dependency-cache-eviction-001/receipt.json).
Six unused project Python 3.7 build-cache records were also removed with exact-ID checks; Docker image and container IDs are unchanged. See the [cleanup receipt](../evidence/data/scoped-build-cache-cleanup-003/receipt.json). A 428,839,266-byte duplicate restore-test shard was also evicted after fresh R2 and local hash verification; the original source remains. See the [eviction receipt](../evidence/data/restore-cache-eviction-001/receipt.json). That historical restore directory now requires restoration before reuse. The held fancyheader image cache was subsequently evicted after a live pinned-registry check, preserving other image/container IDs. This recovered sufficient capacity to acquire Rally; free space after that pull was 3.89 GB. See the [image eviction receipt](../evidence/data/fancyheader-image-eviction-001/receipt.json). Remeasure before another image acquisition.

## Acceptance status

| Requirement | Verified evidence | Remaining acceptance work |
| --- | --- | --- |
| Data supply | 29 quarantined examples, 29 tasks, 28 declared repository groups; 588,865 input and 165,947 supervised tokens | Abundant, diverse, approved data; the 3×50M processed-target-token plan is not supplied |
| Task alignment | Publisher controls and bounded semantic checks for selected candidates; Boltons derivative repairs the reproduced compatibility failure | Final content-bound review for every admitted task; passing finite cases is not universal correctness |
| Attribution | Selected exact repository and dependency notices retained; teacher and assistant-derived actions distinguished | Complete source, observation, dependency and teacher-term review |
| Split isolation | Authenticated lineage audit 024 resolves 28 declared groups, two historical names and four reserved names; no cross-boundary ID/network-root overlap | Freeze splits and review semantic duplicates, detached copies and historical lineage; current IDs do not prove independence |
| Local training code | Latest CPU suite in native environment: 435 tests, 418 passed, 17 skipped | Skipped environments, full-model GPU corroboration and long-running stability |
| Artifact ingestion | Corpus 033 uploaded to R2, restored into an empty directory and validated; schedules match byte-for-byte | Repeat with the final admitted bundle on the actual Runpod volume |
| GPU validation | Earlier single synthetic full-model update/reload only | Real-corpus long-sequence memory, throughput, checkpoint/resume and bounded failure handling |
| Product performance | No demonstrated learned held-out gain | Train and compare against a frozen baseline on uncontaminated held-out tasks |

## Current corpus and evidence

Evaluator extraction and replay-history construction now also use one verified immutable byte snapshot for both Parquet reads. Four new real-parser integration tests and real SoftLayer output equivalence pass; see the [reader regression report](../evidence/p1/task-reader-snapshot-regression-001/report.json).

Teacher extraction now parses a bounded, SHA-256-verified immutable byte snapshot
rather than reopening a cloud-backed Parquet path. Provenance and final drift
checks remain active. Three regression tests and three real candidate extractions
pass; the latest full native suite passes 409 of 426 tests, with 17 skipped. See the
[ingestion regression report](../evidence/p1/source-byte-snapshot-regression-001/report.json).
SoftLayer2188 passes all four publisher cases and all 28 finite CLI cases; its 35-call native replay independently passes all four publisher cases. The untruncated history has 16,291 input and 2,850 supervised tokens, with an 8,285-token reserve margin. Mechanical checks pass and the candidate is integrated into quarantined corpus 033; final training-content approval remains pending. See the [native observation review](../evidence/data/softlayer2188-observation-review-001/scope.md) for seven preserved command failures. Its 114-file runtime evidence archive is uploaded and restore-verified in R2. The separate 62-file native archive is remotely hash-verified, but not restore-tested. See the [runtime review](../evidence/data/softlayer2188-runtime-review-001/scope.md). Rally1469 scope is resolved against upstream; its extra reference chart edit is outside the stated issue. Runtime now passes all 197 publisher cases and all 12 bounded connector/session checks; native replay and token qualification now pass, but the original is held for unsupported leak-prevention claims in teacher-written validation code. See the [content hold](../evidence/data/rally1469-observation-review-001/scope.md) and [runtime review](../evidence/data/rally1469-runtime-review-001/report.json). See the [scope and runtime plan](../evidence/data/rally1469-scope-review-001/scope.md).
Pylutron20 is held for delimiter and unresolved license issues. See the
[static decisions](../evidence/data/qualification-triage011-review-001/decisions.json).


Numba6653 is integrated into quarantined corpus033 after a 35-call native replay.
Its one-file patch passes independent grading on the single publisher regression.
The untruncated history has 16,388 input and 5,897 supervised tokens, leaving
8,188 after the output reserve. Mechanical checks pass; training approval is false.
Two observed shell errors remain recorded. See the [native review](../evidence/data/numba6653-observation-review-001/report.json)
and [bounded runtime review](../evidence/data/numba6653-runtime-review-001/report.json).
Mwclient365 and Pika851 remain held for state/default/logging discrepancies; the
[static decisions](../evidence/data/qualification-triage010-review-002/decisions.json)
and [historical cohort projection](../evidence/data/qualification-batch003-status-001/report.json)
record their scope. Numba is integrated in quarantine; no example is admitted for training.


Spelling177 is integrated into quarantined corpus033.
Its 32-call native replay submits one production file; independent grading matches
all 11 reference outcomes, including the expected docstring failure. The untruncated
history has 20,807 input and 4,433 supervised tokens, leaving 3,769 after the output
reserve. Mechanical checks pass; training approval remains false. Broader teacher
suite failures and the shared emphasized-caption omission remain documented.
See the [native observation review](../evidence/data/spelling177-observation-review-001/report.json)
and [bounded runtime review](../evidence/data/spelling177-runtime-review-001/report.json).


The corrected Apispec950 replay is integrated into quarantined corpus033.
The explicit assistant correction submits a one-file patch in 37 charged calls,
passes 117 independently graded publisher cases and the previously recorded 36
finite metadata/schema checks. Its 78-message, 38-exchange history contains
23,112 input and 4,244 supervised tokens; after the 8,192 output reserve, 1,464
context tokens remain. Mechanical checks pass, but training approval is false.
The original teacher and reference overwrite explicit metadata; six finite cases
lose closed or typed restrictions, while three differ only in representation.
See the [native review](../evidence/data/apispec950-correction-review-002/report.json),
[mechanical checks](../evidence/data/apispec950-mechanical-admission-001/report.json),
and [bounded invariant](../evidence/data/apispec950-correction-review-001/scope.md).
The source pip/search/legacy-test failures remain in the observed history.

Marshmallow-dataframe 19 remains outside the corpus. The original teacher fails
one of 18 publisher cases and six of 36 finite schema checks. Its explicit
assistant correction passes all of those checks and all 18 independently graded
native cases. Native attempt 006 submits only the intended production file in
40 charged calls. The remaining hold is context: 25,649 input tokens plus the
8,192 output reserve exceeds 32,768 by 1,073. No truncation or policy relaxation
was applied. See the [latest correction review](../evidence/data/marshdf19-correction-review-002/report.json).

Replay and grading support a validated checkout-relative import root; exact
module-origin checks remain active. The [regression log](../evidence/p1/source-import-regression-001/full-suite-003.log)
records 419 tests: 402 passed and 17 skipped. The [94-file evidence archive](../evidence/data/marshdf19-correction-publish-002/receipt.json)
has remote hash verification; it has not been restore-tested.

Importlab 23's teacher is held: it passes all 30 publisher tests but fails four
of 30 POSIX path checks by truncating two literal dotted filenames. Base
preserves those filenames; reference passes all 30 checks. See the
[runtime review](../evidence/data/importlab23-runtime-review-001/report.json).
An attributed correction now passes 30 path checks and all 30 graded publisher
cases after a 38-call native replay. Mechanical checks pass; history is 23,697
input / 6,640 supervised tokens, with 879 tokens of output-reserve margin.
See the [correction review](../evidence/data/importlab23-correction-review-001/report.json).
The corrected replay is integrated into corpus 033; training admission remains pending.

Icontract 115's uncorrected teacher is held outside the corpus. It passes all
25 publisher tests but bypasses preconditions, postconditions and snapshots in
nine of 15 valid variadic-call checks; reference passes all 15. Base fails those
nine with IndexError, whereas the teacher runs the body without contracts.
See the [runtime review](../evidence/data/icontract115-runtime-review-001/report.json).
An assistant-authored, reference-informed correction now passes 25 publisher,
15 variadic and 152 bounded-mapping/call-shape checks. Its original trace already
uses 40 tool calls, leaving no room for appended correction under current policy.
See the [correction review](../evidence/data/icontract115-correction-review-001/report.json).
No corrected native replay or training admission is claimed.

The original Munch 52 teacher remains held. It passes all six
publisher tests but fails 27 of 54 finite subclass/default/YAML-graph checks;
reference fails none. The teacher repairs DefaultMunch behavior while leaving
ordinary subclass identity loss and DefaultFactoryMunch TypeError unresolved.
These are remaining base deficiencies, not new regressions. See the
[runtime hold](../evidence/data/munch52-runtime-review-001/report.json).
An explicitly authored derivative now passes all six publisher cases, all 54
subclass/graph checks and 12 optional/keyword default compatibility checks.
It retains the teacher's DefaultMunch override: reference alone fails eight of
those compatibility checks, which are not asserted publisher requirements.
Native replay and exact-patch grading pass; mechanical assessment passes with
39/40 calls and 24,332 input / 5,953 supervised tokens. Only 244 tokens remain
after the output reserve. The corrected derivative is integrated into corpus 033; training admission is pending.
See the [corrected review](../evidence/data/munch52-correction-review-002/report.json).

The original Lmfit 487 teacher is held; its corrected derivative is in corpus 033: its independently verified
210-file source snapshot preserves the exact base tree. Base/reference/teacher
publisher results are 12/13, 13/13 and 13/13; 18 finite expression-recovery
sequences fail on the base and pass for both fixes. The teacher sometimes retains
an empty diagnostic string where the reference clears it to `None`. A subsequent
four-sequence diagnostic check reproduced two stronger counterexamples: an old
NameError message becomes the text of a new, unrelated SyntaxError, both within
one parameter and across two parameters sharing an evaluator. Reference clears
the stale state. See the [candidate hold](../evidence/data/lmfit487-diagnostic-review-001/report.json)
and [earlier runtime review](../evidence/data/lmfit487-runtime-review-001/report.json).
An explicitly authored correction now passes fresh replay and exact-patch grading;
the original teacher remains held. The derivative passes 13 publisher cases,
18 recovery sequences and four diagnostic sequences, and its added native checks
pass. Its untruncated history has 21,298 input / 5,514 supervised tokens and uses
40/40 tool calls. The mechanical assessment passes, but rights, split and training
admission remain open. The replay retains a NumPy API compatibility test failure
and a teacher diagnostic's invalid private-method call. See the
[corrected assessment](../evidence/data/lmfit487-mechanical-admission-001/report.json).
The derivative increases quarantined supply, not admitted training supply.

The [corpus 033 supply audit](../evidence/data/corpus033-supply-review-001/report.json)
revalidates the restored manifest and independently recounts shifted-label targets.
All 29 sequences fit 32,768 tokens; 27 also satisfy the separate mechanical policy
`input_tokens + 8192 <= 32768`. Emcee 295 and CloudEvents 172 fail that reserve
screen. This does not invalidate their training-length accounting, and passing
the screen does not establish full admission. The input count already includes
supervised tokens; adding those tokens again would double-count them.

One 50M-target-token campaign is exactly `50000000/165947`, approximately 301.30,
current-corpus-equivalent passes. This is descriptive token reuse, not an exact
scheduler epoch count or independent evidence. No corpus is admitted. Expand
diverse, reviewed supply before scheduling a campaign; do not use repetition to
claim that the data requirement has been met.

- [Assembly receipt](../evidence/data/training-corpus-assembly-033/receipt.json)
- [R2 publish receipt](../evidence/data/training-corpus-publish-033/receipt.json)
- [R2 restore receipt](../evidence/data/training-corpus-restore-033/receipt.json)
- [Corpus integrity inspection](../evidence/data/training-corpus-inspection-032/report.json)
- [Integration evidence archived in R2](../evidence/data/corpus033-integration-publish-001/receipt.json)
- [Integration and schedule equality check](../evidence/data/corpus033-integration-check-001/report.json)
- [Explicit training rejection](../evidence/data/training-corpus-denial-031/report.json)
- [Current repository lineage screen](../evidence/data/current-corpus-lineage-024/report.json)
- [Lenskit corrected observation review](../evidence/data/lenskit312-observation-review-002/report.json)
- [Lenskit qualification archive](../evidence/data/lenskit312-qualification-publish-001/receipt.json)
- [Required correction archive](../evidence/data/lenskit312-correction-publish-001/receipt.json)
- [Latest CPU regression](../evidence/p1/subdirectory-replay-regression-001/full-suite-retry.log)
- [Boltons derivative review](../evidence/data/boltons205-compat-review-001/report.json)
- [Jsons completion evidence archived in R2](../evidence/data/jsons86-completion-publish-001/receipt.json)
- [Xhistogram dependency diagnostic](../evidence/data/xhistogram20-compat-review-001/report.json)
- [Dependency diagnostic and wheel archived in R2](../evidence/data/xhistogram20-compat-publish-001/receipt.json)
- [Xhistogram runtime evidence archived in R2](../evidence/data/xhistogram20-runtime-publish-002/receipt.json)
- [Xhistogram publisher-control environment hold](../evidence/data/xhistogram20-control-drift-001/report.json)
- [Conllu completion evidence archived in R2](../evidence/data/conllu35-completion-publish-001/receipt.json)
- [Conllu completed observation and token review](../evidence/data/conllu35-observation-review-001/report.json)
- [Conllu scoped label-language argument](../evidence/data/conllu35-language-review-001/proof.md)
- [Conllu parser runtime qualification](../evidence/data/conllu35-runtime-review-001/report.json)
- [Conllu runtime evidence archived in R2](../evidence/data/conllu35-runtime-publish-001/receipt.json)
- [Gitignore runtime evidence archived in R2](../evidence/data/gitignore38-runtime-publish-001/receipt.json)
- [Gitignore native evidence archived in R2](../evidence/data/gitignore38-completion-publish-001/receipt.json)
- [Gitignore native observation review](../evidence/data/gitignore38-observation-review-001/report.json)
- [Gitignore path-handling runtime review](../evidence/data/gitignore38-runtime-review-001/report.json)
- [Gitignore scoped reasoning and limitations](../evidence/data/gitignore38-runtime-review-001/scope.md)
- [Next candidate triage: Lmfit, Munch and ASDF](../evidence/data/qualification-triage007-review-001/report.json)
- [Triage 007 archived in R2](../evidence/data/qualification-triage007-publish-001/receipt.json)
- [ASDF runtime evidence archived in R2](../evidence/data/asdf1853-runtime-publish-001/receipt.json)
- [ASDF exact native patch grade](../evidence/data/asdf1853-standard-grade-001/report.json)
- [Completion-aware admission evidence archived in R2](../evidence/data/completion-admission-publish-001/receipt.json)
- [Gitignore and Conllu assessment archive](../evidence/data/completion-admission-batch-publish-001/receipt.json)
- [Gitignore and Conllu standard-grade assessment](../evidence/data/completion-admission-batch-review-001/report.json)
- [ASDF mechanical admission assessment](../evidence/data/asdf1853-mechanical-admission-001/report.json)
- [ASDF native observation review](../evidence/data/asdf1853-observation-review-001/report.json)
- [ASDF native evidence archived in R2](../evidence/data/asdf1853-completion-publish-001/receipt.json)
- [ASDF converter runtime qualification](../evidence/data/asdf1853-runtime-review-001/report.json)
- [ASDF finite-domain mathematical check](../evidence/data/asdf1853-runtime-review-001/scope.md)
- [Next boundary and parsing candidate triage](../evidence/data/qualification-triage006-review-001/report.json)
- [Triage 006 evidence archived in R2](../evidence/data/qualification-triage006-publish-001/receipt.json)
- [Next 32-repository qualification queue](../evidence/data/qualification-batch-current-003/report.json)
- [Queue, lineage and issue screening archive](../evidence/data/qualification-batch003-publish-001/receipt.json)
- [Numerical candidate triage](../evidence/data/qualification-triage005-review-002/report.json)
- [Csaps native observation and numerical review](../evidence/data/csaps3-observation-review-001/report.json)
- [Csaps qualification evidence archived in R2](../evidence/data/csaps3-qualification-publish-001/receipt.json)
- [Triage evidence archived in R2](../evidence/data/qualification-triage005-publish-001/receipt.json)

Manifest SHA-256:
`de181d6fb9014532d3394a0bef42ee2b47a54c183a7a7770b783f7d98bb0f0db`.
Content SHA-256:
`01d42a005439e35c7fae2a47aef3c6ed0c726a33ca970dc169e438d1653c84d5`.
The restored bundle has 59 files and 6,514,884 bytes. Its one-epoch schedule uses
seed 7401, 27 planned updates and a 9,216-supervised-token update cap. It consumes
165,947 target tokens with zero overshoot. No optimizer steps are implied.

All four admission fields remain null: rights/attribution, split isolation,
runtime qualification and task alignment. Training-purpose loading rejects with
`Quarantine corpus cannot train`. Receipt integrity verifies bytes and bindings;
it does not prove the truth or completeness of the underlying reviews.

## Next local cycle

Triage 008 is complete: corrected Importlab is in quarantine; corrected
Icontract remains above the call budget; corrected Marshmallow remains above
the context-reserve budget. The existing stochastic-assignment candidate remains held for demonstrated
probability-validation counterexamples. Triage 009 has runtime evidence for the API-schema candidate and static
evidence for spelling-caption nodes. The corrected API candidate is integrated with verified restore and schedule
accounting. Spelling, Numba and SoftLayer are integrated into quarantine. Rally1469 has passed native/mechanical checks but remains excluded for unsupported validation claims; Pylutron20 remains held on delimiter and rights questions. None is approved training data.
Measure local capacity before any additional container image downloads.

1. Continue diverse task qualification. ASDF1853 passes 28 publisher tests and
   1,024 finite tag-set checks; completed native replay is integrated into quarantine. The corrected Lmfit487 derivative is also integrated; Munch52
   has a corrected derivative integrated into quarantine; its original teacher remains held. Gitignore38 passes publisher controls and
   120 targeted path checks. Native replay and token export are complete;
   quarantine integration is complete; final attribution and admission review remain pending. Xhistogram density compatibility is
   diagnosed, but its historical publisher transition table remains unreproduced;
   25 passing candidate tests and 192 finite numerical cases do not override
   that distinction. Expand diverse task supply from the pinned source cohort, preserving failed
   candidates and explicit source-versus-derived authorship. Keep source credential
   screening ahead of replay; flagged material requires review.
2. Complete observation-level attribution and task acceptance. The completion-aware
   assessor now verifies ASDF, Gitignore, Conllu and corrected Lmfit/Munch exact patches, histories and budgets; this mechanical
   result is not training admission. Conllu has only 520 input tokens of margin
   after the 8,192-token output reserve; re-audit after any prompt or tool-schema
   change. Extend standard grading to the other candidates, then bind reviews
   to the final corpus. Preserve the Dynaconf mirror distinction and investigate
   semantic overlap before freezing evaluation splits.
3. Reassemble, publish, restore and compare token accounting and deterministic
   schedules after each admitted-to-quarantine data change. Quarantine eligibility
   must not be promoted to training approval by a successful transfer.
4. Prepare the exact worker, admitted data bundle, resume checks, GPU validation
   commands and cost cap before asking the user to restart Runpod.

## GPU restart boundary

Request a restart only when a concrete next validation requires the GPU and its
inputs and local checks are ready. CPU checks cannot guarantee full-model GPU fit
or absence of errors. The next GPU session must first measure real-corpus memory,
throughput and checkpoint/resume behavior; it must not launch a long campaign
based on the earlier synthetic update. Obtain the session budget and preserve
checkpoints and evidence on persistent storage. Do not restart a user-stopped Pod
automatically.

The three 50M-token candidates are a changeable experimental plan, not evidence
of sufficient unique data. Repeated exposure is not new data or independent
statistical evidence. Learned gains and industrial readiness remain unproven.
