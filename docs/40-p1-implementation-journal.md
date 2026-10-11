# P1 implementation journal

Historical development records. Statements below describe their recorded cycle,
not current readiness. Use [Current P1 readiness](39-p1-current-readiness.md)
for the latest corpus, gates and next actions. Preserve failed attempts and
limitations; append future cycle records here, then update the current summary.

## Preserved readiness record through corpus 018

# Current P1 readiness

Updated October 9, 2026. P1 is incomplete. This document is the concise current
state; documents 12, 35, 37 and 38 retain detailed development history.

| Requirement | Current evidence | Remaining work |
| --- | --- | --- |
| Corpus supply | Fifteen quarantined examples across fourteen repository groups; 289,750 input / 90,869 supervised tokens | Abundant, diverse, approved corpus; the 3×50M plan is not supplied |
| Repair fidelity | Nodebook excluded; Datetransform has added semantic probes; Werkzeug portable replay matches reference on 12/12 publisher tests and 55/55 additional semantic cases | Broader tasks and stronger coverage; teacher replay is not learned performance |
| Task quality | Narwhals and mypy_extensions mismatches recorded; Dkey held; pipdeptree teacher held for a reproduced type-override regression | Task-by-task alignment evidence for every admitted task |
| Rights | Exact repository notices and selected dependency notices captured; pytest upstream 7.1.2 notice recovered | Complete observation/dependency attribution review; installed Conda build equivalence is not established |
| Evaluation isolation | Current ID/fork audit resolves all 14 corpus repository groups, two historical names and four reserved repositories; no cross-boundary ID/network-root overlaps. The old Dynaconf name resolves to a distinct mirror, not an identical repository ID. | Frozen complete splits, semantic and detached-copy review for the final corpus |
| Local training implementation | CPU loss/gradient, optimizer, checkpoint, RNG and scheduling tests; latest suite 367 passed / 33 skipped, plus seven focused Session replay tests passed in the requests-enabled environment | GPU/full-model corroboration and long-running stability |
| Remote ingestion | Corpus 018 published and restored from R2; fifteen examples validate; schedule and updates match original bytes | Repeat on the actual Runpod volume with the final admitted bundle |
| GPU qualification | Earlier single synthetic full-model update/reload only | Real-corpus long-sequence memory, checkpoint/resume, throughput and bounded failure handling |
| Product performance | No demonstrated learned held-out gain | Train, evaluate and compare against the frozen baseline |

## Current artifacts

- [Current fifteen-example quarantine assembly](../evidence/data/training-corpus-assembly-018/receipt.json)
- [Semantic probe results](../evidence/data/current-corpus-semantic-probes-001/report.json)
- [Candidate review and exclusion](../evidence/data/current-corpus-semantic-probes-001/review.json)
- [Current R2 restore receipt](../evidence/data/training-corpus-restore-018/receipt.json)
- [Restored corpus inspection](../evidence/data/training-corpus-inspection-018/report.json)
- [Byte-identical restored schedule](../evidence/data/corpus018-integration-check-001/report.json)
- [Werkzeug independent semantic probes](../evidence/data/werkzeug-v2-semantic-probes-001/report.json)
- [Werkzeug computational AST comparison and notice capture](../evidence/data/werkzeug-v2-source-review-001/report.json)
- [Werkzeug V2 mechanical assessment](../evidence/data/werkzeug-v2-admission-002/report.json)
- [Quarantined corpus training denial](../evidence/data/training-corpus-denial-017/report.json)
- [Datetransform mechanical assessment](../evidence/data/datetransform-native-admission-001/report.json)
- [Selected dependency notices and explicit gaps](../evidence/data/datetransform-rights-material-003/report.json)
- [Matching upstream pytest release notice](../evidence/data/datetransform-pytest-upstream-notice-001/receipt.json)
- [Earlier two-repository identity check](../evidence/data/current-corpus-lineage-001/report.json)
- [Candidate issue duplicate audit](../evidence/data/candidate-issue-duplicates-001/report.json)
- [Draft corpus split review](../evidence/data/current-corpus-split-review-001/report.json)
- [Datetransform observation audit](../evidence/data/datetransform-observation-audit-001/report.json)
- [Nodebook observation audit](../evidence/data/nodebook-observation-audit-001/report.json)
- [Datetransform direct file attribution](../evidence/data/datetransform-file-rights-001/report.json)

Corpus schema v2 requires rights/attribution, split-isolation, runtime and
task-alignment receipts bound to the exact content. All four remain unresolved
for the assembled real corpus. No passing real admission receipt was fabricated.
Receipt integrity checks do not establish the truth of semantic or rights review.

## Next implementation cycle

Complete observation-level attribution and task review for the current candidates,
continue diverse data qualification, and freeze the intended evaluation split.
Keep admission and GPU-fit claims separate: actual GPU fit cannot be guaranteed
by CPU tests. Prepare the exact restored corpus, source bundle, budget and resume
checks before requesting a user-initiated Pod restart. Do not start a campaign
based on the earlier short synthetic update.

An earlier local regression run completed 305 tests: 281 passed, 24 skipped.
The Python 3.7 notice-capture path was additionally exercised in the actual
Datetransform container. Missing notices still fail by default; the explicitly
requested inventory mode records gaps and never approves training.

## Task alignment coverage enforcement

The v2 loader now requires versioned task-review evidence with exact coverage of
every distinct `(task_id, repository_group)` pair. Each review must include an
`accepted` decision and nonempty rationale. Missing, duplicate, foreign and
unresolved reviews fail admission, including hash-valid receipts. Multiple
traces of the same task share one issue-level review. Every evidence document
under this gate must contain `schema_version: 1` and nonempty `task_reviews`;
review entries have exactly `task_id`, `repository_group`, `decision`, `rationale`.
This enforces coverage, not semantic truth or per-trace correctness.

The real two-example corpus was re-inspected unchanged and remains quarantined.
The refreshed worker is `artifacts/official/p1-task-coverage-worker-001`; isolated
CLI import verification passed. No GPU was used.

## Semantic counterexample review

Additional evaluator-only probes were run on the exact local snapshot images,
with networking disabled, in disposable containers. Nodebook improves four
argument cases but loses the `External` dependency in `def f(a:External)` and
incorrectly suppresses the module-level dependency in `def f(a): return a; z=a`
(with the final assignment outside the function). The original 19-case evaluator
does not expose these defects. The trace is excluded from selection 003 and
assembly 004. Older artifacts remain immutable historical evidence.

Datetransform passed 18/18 added cases (base: 0/18), covering 0/1/3 rows, time
fields enabled/disabled and default/false/true inplace. These are constructed
regression cases, not an independent statistical sample or general guarantee.
All real admission gates remain unresolved. The older two-example restore and
schedule evidence does not certify the new one-example assembly or its schedule.


### Easy-ptvsd evaluator qualification — 2026-10-09

Pinned image matches declared base commit. Original image retains seven Git
commits and is evaluator-only pending sanitization. Base/reference controls
match all four publisher outcomes: base 3 pass / 1 fail, reference 4 pass.
Nineteen additional mocked-debugger checks give base 4/19 and reference 19/19;
these cover return identity, forwarding, class/static methods, call order and
exception identity. They test the publisher reference, not a teacher or model.
Evidence: `evidence/data/easyptvsd-review-001/review.json`. Next: sanitize and
replay shortest eligible trajectory, then grade, tokenize and review rights.
Current assembled corpus remains one quarantined Datetransform example. No GPU.


### Easy-ptvsd sanitized replay and integration — 2026-10-09

Verified ten tracked files in an exact-tree snapshot with one parentless commit,
no remotes, known oracle paths absent, and old base/head/merge commits inaccessible.
Verification concerns the mounted filesystem, not inherited Docker layer bytes.
Snapshot base/reference outcomes match original controls for all four test IDs.

Shortest trace `a148d74a-1367-4d52-8c47-a73008f73e7e` replayed but failed the
source-path restriction because its submitted patch retains `reproduce_issue.py`.
Retained the failure and did not edit its patch. The alternate trace
`40eb374a-0850-4770-8b29-61e6905e5c55` performs its own cleanup, submits only
`easy_ptvsd.py`, and passes 4/4 independent evaluator outcomes and 19/19 added
semantic probes. Replayed observations are fresh; original teacher conditioning
on those observations is not established.

Alternate history: 15,297 input / 4,527 supervised tokens; plus 8,192 reserve is
23,489, below 32,768 by 9,279 tokens. Mechanical admission passes; training remains
unapproved. Selection 004 and corpus 005 combine this trace with Datetransform:
29,423 input / 9,101 supervised tokens. All four real admission gates remain
unresolved. Next: attribution/rights, observation review, broader supply, updated
split isolation and scheduling. No GPU used.


### Easy-ptvsd attribution and restore cycle — 2026-10-09

R2 replay archive restored (91 files); corpus 005 validates through indexed
scheduling. Local and restored schedule/updates bytes match exactly: two
whole-example updates, 9,101 supervised tokens, zero overshoot, one epoch.
This is an inspection schedule, not training approval or GPU-fit evidence.

Captured ten repository files including MIT LICENSE.md and pytest 8.3.3 notice.
ptvsd 3.0.0 has no installed/archive standalone notice; captured its source
headers and referenced Apache 2.0 text. All seven installed Python source files
match the hash-verified PyPI archive. This does not certify the whole environment
or exhaustive rights. Attribution review: evidence/data/easyptvsd-rights-review-001.

Replay observation audit found five errors (missing issue reads, direct test
import failure, grep no matches, reversed classmethod reproduction). None were
concealed. Twenty-three calls have unspecified truncation status. Continue
observation consistency/attribution and broader qualification; no GPU used.


### Fancy-header branch counterexamples — 2026-10-09

Pinned image matches declared base; publisher base/reference controls match
13 expected outcomes (base 12 pass / 1 fail, reference 13 pass). Additional
12-case source branch probes pass 8/12 on base, 12/12 on reference, and 11/12
on each of three teacher source-edit reconstructions. Two traces suppress
missing-header errors on nonempty inputs; the third suppresses invalid-header
validation for docstring-only input with an empty body. All three are held.

The separate docstring/body branch was tested with its explicit object contract,
not a native newer-Python AST. These probes do not establish cross-version
compatibility or reproduce teacher shell execution. Evidence and exact edits
are retained at evidence/data/fancyheader-semantic-review-001 and
evidence/data/fancyheader-branch-probes-001. Do not equate publisher Python 3.6
passes with branch-complete repair quality. No new example added; corpus stays
at two quarantined examples, 9,101 supervised tokens. Next: qualify another
repository and continue corpus review. No GPU used.


### Supply feasibility and broader qualification batch — 2026-10-09

Verified census: 34,269 raw traces. Current cost-screened, image-present cohort:
2,621 traces, 1,575 tasks, 902 repositories. These counts are not admission.
Corpus 005 remains 9,101 supervised tokens, quarantine only. Under the current
32,768 context cap and 8,192 output reserve, a complete example has at most
24,576 input tokens and at most 24,575 causal supervised targets. Thus even
before prompt/tool masks and quality losses, one trace per task in this cohort
has a single-pass ceiling of 1,575 × 24,575 = 38,705,625 targets. All 2,621 traces
have ceiling 64,411,075. Neither number is available training supply.

A 50M-token candidate therefore requires expanding this cohort, multiple
trajectories per task, repeated exposure, or some combination. Three candidates
may reuse the same corpus; 150M processed targets are not 150M unique targets.
Do not interpret repetitions as independent tasks or evidence. No acceptance
rate is extrapolated from the deliberately chosen small reviewed subset.

Added a deterministic 32-repository review batch: choose each unreviewed
repository's shortest source-proxy trace, divide repositories into four cost
rank strata, select eight per stratum by seeded hash ranking. This widens cost
and repository coverage; it is not an unbiased coding benchmark or proof of
native token fit. All 32 issue descriptions are extracted with pinned task
shard identities. Evidence: evidence/data/qualification-batch-001. Next: review
those tasks and qualify their runtime/trajectory evidence.

Full CPU regression: 305 tests, 281 passed, 24 skipped. No GPU used.


### Broad batch triage and NumPyro mathematical check — 2026-10-09

Read all 32 issue descriptions; extracted identity-checked evaluator-only
patches for all 32 and reviewed reference/test patches for ten. Reviews record
specific missing tests and distinguish issue-only from patch-reviewed tasks.
Priority batch: CRC, NumPyro, Verde, civisml-extensions, geomet, pandas-vet,
hyp3-sdk, litecli. This adds state, tensor-rank, numerical, CV-alignment and
parsing coverage; no examples are approved merely by selection.

For NumPyro composition ranks, derived the minimum feasible input rank as
max(0, max_i[d_i - sum_{j<i}(c_j-d_j)]). The reference's backward recurrence
starts at the final domain rank and visits preceding transforms only. Exact
source/reference functions were checked against forward feasibility and the
closed form for 69,904 bounded abstract sequences: reference 0 disagreements,
base 17,942. This is not JAX or full-task runtime validation.

Held broad reference approval for sktime due to formula documentation/edge
contract gaps and decode due to version/specification and coverage mismatch.
Uvicorn trusted-proxy semantics and magnivore rounding require clarification
from source/contracts before qualification. Corpus remains two quarantined
examples, 9,101 supervised tokens. Evidence: qualification-batch-review-001
and numpyro-compose-math-001. Next: runtime and teacher review for priority tasks.
No GPU used.


### CRC runtime and provenance qualification — 2026-10-09

Resolved Nicoretti__crc-153 against the benchmark's merged solution commit
7ac98da2c6df6bbb91e2793ac69fcf796f9dba14, rather than the unavailable PR head.
The new snapshot independently preserves all 56 tracked files, has one
parentless commit, and removes checked old commits and known oracle paths
from its mounted filesystem. Inherited image layers remain outside this audit.

Original controls could not import crc: its installed editable-path file points
to /crc/src instead of /testbed/src. A diagnostic runner verifies the exact old
path bytes, records their hashes, and applies the same path-only correction in
four disposable offline containers. Original/snapshot base outcomes match
exactly (11 passed, 6 failed); both reference runs pass all 17 cases. Source
imports resolve to the checkout and tests leave tracked diffs unchanged.
Evidence: evidence/data/crc-runtime-controls-002 and crc-snapshot-verify-002.
Earlier failed attempts are retained. No teacher replay or corpus admission is
claimed. Next: integrate the explicit runtime correction into the replay image,
then test digest state preservation and updates interleaved with digest reads.
Corpus remains two quarantined examples, 9,101 supervised tokens; Pod stopped.


### CRC deep checks and native replay — 2026-10-09

Added an independent bit-feedback CRC oracle over GF(2), cross-checked CRC32
against zlib, and checked every 8-bit register state plus all split points of
five bounded messages across 16 configurations and two implementations.
Reference: 4,965 passed; base: 3,433 passed, 1,532 failed. These are dependent
within-task checks, not independent performance samples. Continuation after
reads is explicitly a stronger engineering invariant than the abstract single
final-digest workflow. Scope and derivation: crc-semantic-probes-001/DERIVATION.md.

Packaged the editable-path repair into a local derived image; independently
verified unchanged source snapshot and reproduced all 17 publisher transitions.
Build 003 failed because Docker interpreted the bare image ID as a registry
name; retained that failure. Build 004 uses a local tag with parent identity
checks before and after build; final runtime is pinned by content ID.

Native replay of trace 888c60d0-0a64-4816-aa3b-6c0aaacbf89a completed with
36 charged calls and fresh observations. Its patch retains final_verification.py
and reproduce_issue.py outside the source allowance, so grading stopped before
tests. No artificial cleanup, trimmed patch, training admission or candidate
semantic pass is claimed. Evidence: crc-replay-001, crc-replay-grade-001,
crc-qualification-review-001. The other reviewed CRC traces exceed the current
40-call source-proxy budget. Move to the next priority task rather than change
these acceptance rules for a preferred example. Corpus remains two quarantined
examples / 9,101 supervised tokens. No GPU used; P1 remains incomplete.


### NumPyro teacher mathematical screening — 2026-10-09

Reviewed all three extracted NumPyro-1894 teacher source edits before downloading
the 2.53 GB compressed image. Each adds a singleton special case while retaining
the incorrect multi-transform recurrence. Exact edited functions disagree with
independent forward feasibility and the closed-form rank oracle on 17,936 of
69,904 bounded sequences per trace, despite zero singleton disagreements.
For CorrCholeskyTransform followed by its inverse, all return input rank 2 where
rank 1 is sufficient and minimal. The shortest trace changes its diagnostic
assertion from 1 to 2; preserve that contradiction instead of training on its
success claim. No native replay, JAX evaluation, tensor-value or Jacobian test
is claimed. All three held for positive training; image metadata resolved but
layers not downloaded. Evidence: numpyro-teacher-001, numpyro-teacher-math-001,
numpyro-image-001. Next priority: Verde or civisml task qualification. Current
corpus remains two quarantined examples / 9,101 targets, not training-approved.
Pod remains stopped; P1 is incomplete.


### Verde contract audit and civisml intake — 2026-10-09

Verde-255 has an issue/evaluator API mismatch: the issue asks for `copy`; all
three teachers implement it; reference/tests call `copy_jacobian`. Signature
binding confirms each teacher rejects the evaluator keyword. After parameter
normalization and docstring removal, all three executable function ASTs match
the reference. Hold benchmark alignment, not mathematical correctness; no
renaming, evaluator modification or invented successful replay. Numerical
change-of-variable derivation and limitations are in verde-contract-review-001.

Reviewed civisml-extensions-22 source edits, which cache CV splits to keep
prediction rows aligned with target labels. Selected trajectory
101cfa89-3239-48d5-a2bc-abbbaf09929d for the next native qualification: 40 source
proxy actions and explicit cleanup of five diagnostic files. This is selection,
not acceptance. Resolve deterministic changing-fold negative controls, unequal
fold sizes and sample-weight indexing before admission. Image digest is pinned;
1,432,048,066 compressed bytes, layers not downloaded. Evidence: civisml-review-001,
civisml-teacher-001, civisml-image-001. Corpus unchanged; Pod stopped; P1 incomplete.


### civisml runtime, deterministic controls and replay preflight — 2026-10-09

Pinned runtime downloaded; Python 3.6.13 / sklearn 0.19.2 imports the task from
/testbed. Sanitized snapshot independently preserves 22 tracked files, removes
checked old commits and known oracle paths, and has one parentless commit.
Original and snapshot controls match every publisher transition: base 53/54,
reference 54/54. This one stochastic publisher regression is supplemented by a
deterministic changing-fold mechanism check: base 0/12 aligned, reference and
all three editor variants 12/12. Checks cover unequal folds, estimator column
order, training weights, row coverage and meta parameters using real NumPy but
controlled fitting/job doubles. No model-performance or independence claim.

Cloud-offloaded local files blocked reads. Two owned processes were terminated
only after identifying blocked reads and dataless files; source_snapshot.py and
image metadata were restored byte-identically from manifest-verified archives.
Other hydration races were rejected by inventory checks; successful retries use
fresh paths. No integrity check was weakened. Evidence includes local restoration
receipt and retained partial snapshot context; failed extraction attempts created
no output directories. Successful inputs: civisml-input-004; snapshot build and
verification: civisml-snapshot-002 / civisml-snapshot-verify-002; controls:
civisml-controls-001 / civisml-snapshot-controls-002.

Selected teacher replay stopped before container creation: action 8 uses an
absolute-path grep invocation outside the adapter's reviewed shell form. Next:
implement/test a narrow command mapping, then native replay, actual-patch grading,
context audit and rights checks. No training example admitted. P1 remains
incomplete; Pod stayed stopped. See civisml-replay-preflight-001 and
civisml-alignment-probes-001 for explicit limitations.


### Source grep adapter and civisml native replay — 2026-10-09

Added a narrow standalone `grep -n` mapping for one literal identifier and one
repository file. It accepts reviewed quoting forms and uses source_path plus
shell-safe argument rendering; shell operators, extra files, traversal, metadata
paths and unreviewed patterns reject. Tests compare actual match/no-match
stdout, stderr and exits. Full CPU suite: 307 tests, 283 passed, 24 skipped.
Initial suite had two hydration-related inventory rejections; both logs retained.

Civisml replay 002 completed with 40 charged calls, fresh observations and only
civismlext/stacking.py in the submitted patch. Actual patch passes 54/54 evaluator
cases and 12/12 deterministic method-alignment cases (controlled estimator/job
doubles, not concurrent fitting validation). Observation audit records two
errors, one explicitly truncated output and 31 unspecified truncation statuses;
these are preserved rather than relabeled successful.

Untruncated native history has 84 messages / 41 exchanges, 40,688 input tokens
and 10,867 supervised targets. With the 8,192 output reserve this needs 48,880
context tokens, exceeding the current 32,768 limit by 16,112. Token export
rejected; no tokens were silently dropped. Admission 004 holds this otherwise
passing candidate for context fit; it is not added to the corpus. Next: assess
an explicit, generally applicable observation-budget policy or select fitting
trajectories; any changed replay needs fresh observations and requalification.
Evidence: civisml-replay-002, civisml-grade-002, civisml-candidate-alignment-002,
civisml-history-003, civisml-tokens-004, civisml-admission-004 and
source-grep-regression-001. Corpus unchanged; P1 incomplete; Pod stopped.


### Civisml context-policy analysis — 2026-10-09

Verified swegemma 0.2.10's command cap (5,000 characters per stream), separate
file limits, missing explicit command-truncation flags and duplicated error
stream payloads. Counterfactual tokenization leaves all actions intact and caps
tool payloads only in memory; no altered history/tokens were emitted for training.
Command cap 1,024 plus file cap 2,000 still needs 33,681 tokens including reserve.
Only the tested 512/2,000 policy fits (30,911 total), but information sufficiency
and adaptive repair quality are unverified. Do not lower limits solely to admit
this case. Current policy and corpus remain unchanged.

A future generally applicable observation policy must preserve recoverable full
outputs, explicitly report truncation, be checked against harness compatibility,
and pass multi-task information/repair evaluation using fresh executions. Long
assistant diagnostic scripts also contribute to cost. Evidence and decision:
civisml-context-analysis-001. Continue independent fitting-data qualification;
this is not a Runpod blocker. P1 remains incomplete; Pod remains stopped.


### Geomet native qualification and context gate — 2026-10-09

Reviewed three geomet-101 teacher repairs. All follow the issue's suggested
truthiness-based SRID override. Bounded extracted-function probes cover six
geometry types, five metadata conditions and omitted/None/positive overrides:
base 60/90, reference and each teacher 90/90. Coordinates and input nonmutation
are checked. Separate explicit-zero probes expose a difference: reference 30/30,
teachers 0/30. Do not equate this with a valid-CRS claim; zero-domain contract
remains unresolved. No projection/reprojection validity is asserted.

Pinned image and sanitized snapshot qualify: 36 tracked files, one parentless
commit, old commits/known oracle paths inaccessible in the mounted filesystem.
Original/snapshot publisher controls agree: base 19/23, reference 23/23.
Trace 8f942217-d0bf-4856-9387-3151dcc1df24 replays with 39 charged calls and
explicit diagnostic cleanup. Submitted patch contains only geomet/esri.py,
passes 23/23 tests, and yields exactly the source bytes used in semantic probes.
Observation audit: two errors, two explicit truncations, 29 unspecified statuses.

History: 82 messages / 40 exchanges; 34,811 input tokens, 8,494 targets.
With reserve, context need is 43,003, so mechanical admission rejects it. No
training token export or corpus addition. Evidence: geomet-precedence-probes-001,
geomet-snapshot-verify-001, geomet-snapshot-controls-001, geomet-replay-001,
geomet-grade-001, geomet-candidate-source-001, geomet-tokens-001, geomet-admission-001.

Repeated context failures motivate an explicit turn-level SFT investigation:
keep the full causal prefix through a selected assistant action, supervise only
that action, and exclude later observations/outcomes. Such examples must be
labeled partial trajectories, not complete successful episodes. Qualification
must verify valid exchange boundaries, token/label identity, no duplicated target
counting across overlapping prefixes, task-level split grouping and complete
coverage accounting for omitted long-prefix actions. No observation cropping or
teacher-action rewriting is authorized by this proposal. Compare usefulness
before replacing the full-trajectory corpus format. Current corpus remains two
quarantined examples / 9,101 targets; P1 incomplete; Pod stayed stopped.

### Experimental action supervision audit — 2026-10-09

Implemented `zenithsync/action_training.py` and `scripts/audit_action_training.py`.
Each selected action receives its complete causal prefix, with every earlier
assistant label masked. Future outcomes are excluded. Complete source histories
must validate first; partial examples explicitly end at a pending tool call.
The pinned native tokenizer verifies unchanged serialization, token identities,
assistant spans and context boundaries. The audit additionally requires action
labels to partition the full-history target positions exactly, without overlap.
No token arrays are exported and no training admission is granted.

| History | Fitting / all actions | Fitting / all unique targets | Repeated input tokens for fitting prefixes |
| --- | ---: | ---: | ---: |
| geomet | 24 / 40 | 4,921 / 8,494 | 344,145 |
| civisml | 27 / 41 | 7,448 / 10,867 | 296,504 |
| easyptvsd | 31 / 31 | 4,527 / 4,527 | 257,667 |
| datetransform | 28 / 28 | 4,574 / 4,574 | 220,178 |

All prefixes use input + 8,192 <= 32,768; no observation cropping. Evidence is
`evidence/data/{geomet,civisml,easyptvsd,datetransform}-action-audit-002/report.json`.
These are four source histories, not 140 independent tasks. Prefixes must retain
the source task/repository split. Aggregate token counts do not create new unique
data. All 140 actions partition 28,462 original targets; fitting prefixes cover
110 actions / 21,470 targets. Late supervision remains missing from long cases.

For the two already-fitting histories, 477,845 prefix input tokens replace
29,423 full-history input tokens (about 16.24 times), with the same 9,101 targets.
This is token-processing overhead, not a measured runtime multiplier. Do not
replace full trajectories with this format by default. Conditional mathematical
identity: if each shared position has identical causal model computation, the
sum of per-action target losses equals the full-history target-loss sum when all
actions are included. A token-weighted denominator is required; averaging action
means changes the objective. Dropout, position-dependent kernels, sequence-length
scaling and floating-point effects mean gradient equivalence has not been proved
for the deployed model. Excluding long prefixes also changes the training set.

CPU suite: 312 tests, 288 passed, 24 skipped. Five focused tests cover selection,
causality, mutation isolation, masking and rejection boundaries; real-tokenizer
checks cover the four histories above. The first datetransform audit rejected a
file changed during cloud hydration; the unchanged stable receipt-bound retry
passed. This check was not relaxed. Earlier audit-001 reports remain historical.
Current corpus remains two quarantined examples / 9,101 targets. No GPU training
or learned-gain claim. Pod remains stopped; P1 incomplete. Next work must address
corpus supply and integration without treating partial coverage as completion.

### Additional corpus pilot — 2026-10-09

Pinned NVIDIA [Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces/tree/e192b26a43b8d09f156eeee781aef8e6bd5108ba)
at `e192b26a43b8d09f156eeee781aef8e6bd5108ba`. The current card declares
CC BY 4.0 and reports removal of Git-exploit trajectories from its earlier
release. This is publisher evidence, not our independent exploit/rights audit.
The [paper](https://arxiv.org/html/2606.16038v1) describes multilingual,
multi-teacher distillation; its older corpus totals cannot stand in for the
current pinned revision. Its reported 65,244 successes divided by 207,489 total
trajectories is about 31.45%, not the nearby claimed 40.6%; the denominator for
that rate is unclear. We will use row-level measured counts and preserve unknown
outcomes rather than inherit that aggregate percentage.

Acquired two bounded shards, each matched to publisher size and SHA-256:
OpenHands/Qwen3.5-122B tail shard 16/17 (43,048,099 bytes) and
mini-swe-agent/Qwen3.6-27B tail shard 21/22 (40,259,778 bytes), both SWE-rebench-V2.
Cards and publisher inventories are preserved. Selection was the smallest file
within each chosen framework/teacher/source, not random sampling. No population
success or usability estimate follows from these samples.

| Pilot | Rows | Repositories | Publisher resolved / unresolved / unknown | Python rows |
| --- | ---: | ---: | --- | ---: |
| OpenHands | 463 | 343 | 90 / 251 / 122 | 76 |
| mini-swe-agent | 1,035 | 669 | 360 / 593 / 82 | 224 |

Metadata projection reads no trajectory or patch bodies. Both shards contain one
exact `Textualize/rich` row, reserved by the official task index. Exact reserved
repository exclusion happens before subsequent body projection. No fork or
semantic-duplicate clearance is claimed. The new schema still omits explicit
tool-response IDs; do not silently treat it as native Gemma history.

Inspected only publisher-positive Python histories outside exact reserved repos:
26 OpenHands, 109 mini-swe-agent. All 26 OpenHands histories pass the existing
single-pending response-link diagnostic after explicit projection excluding the
reasoning field (zero reasoning characters in these inspected rows). None fit
40 source shell/editor calls; the shortest has 54. For mini-swe-agent, 28 of 109
have <=40 source bash calls; the shortest has 18. These proxies do not establish
native charged calls, context fit, independent repair correctness or replay.
No source commands were executed, no reference/model patches were read, and no
training examples were admitted. These counts are not new independent tasks
across all existing datasets; cross-source overlap remains to be measured.

Extended the metadata auditor with an explicit Open-SWE-Traces schema branch.
Two isolated-data-runtime tests cover both schemas, projection behavior, unknown
labels and rejection of boolean/out-of-range/null outcomes. Evidence:
`open-swe-{openhands,mini}-metadata-001`, `open-swe-pilot-screen-001`.

Decision: investigate mini-swe-agent terminal/bash semantics and the pinned V2
task/runtime join before bulk download. Do not expand the demonstrated expensive
OpenHands tail-shard route without a broader metadata/token screen. Preserve the
same replay, quality, attribution and split requirements. Current approved
training supply has not increased; corpus 005 remains two quarantined examples.
Pod remains stopped and P1 remains incomplete.

Regression: 314 tests, 288 passed, 26 skipped in the CPU environment; the two
new PyArrow-dependent tests separately passed in the isolated data runtime.

### Mini-swe-agent serialization and V2 task join — 2026-10-09

Added `zenithsync/mini_source_history.py`, a separate source serializer. It accepts
only the inspected four-field message schema and single bash calls, validates
command argument shape, preserves assistant text/reasoning and observation text,
and infers response IDs only with one outstanding call. Parallel, orphan,
interrupted and duplicate exchanges reject. Unknown fields and malformed
arguments reject. A final unanswered bash call remains explicitly unanswered;
its text is not proof of execution, submission or successful repair. No commands
are run or rewritten by the converter.

Pinned [SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2/tree/10483de0f50fe5da545942705a76c6150171af7f)
at `10483de0f50fe5da545942705a76c6150171af7f`. Acquired its 428,839,266-byte
Parquet shard with publisher hash/size verification, plus card and LICENSE.
Only task ID, repository, base commit, image tag, language and license metadata
were projected for this join. No task problem bodies or reference patches were
read during this operation. All 28 selected source histories joined uniquely by
task ID with matching casefold repository names, excluding exact reserved repos.
Image tags are source metadata, not verified runtime digests or executable tests.

All 28 converted source histories pass the exact pinned Gemma rendering,
token-identity and assistant-span checks. Sixteen fit input + 8,192 <= 32,768,
with 99,359 source assistant targets in total. The other twelve are retained as
context exclusions. All source assistant text is counted, including source
reasoning embedded in content. The single bash schema, source prompts and
observations differ from our native nine-tool interface, so these are not native
training-token counts or new corpus admissions. No token arrays exported.
Evidence: `evidence/data/mini-source-qualification-001/{receipt,token-report}.json`.

The shortest fitting histories are werkzeug-2971 (11,198 input / 3,853 targets)
and dbt-snowflake-716 (12,216 / 3,068). Select runtime/replay work by clear issue
contracts and practical environment requirements, not length alone. Next:
inspect source shell/session/terminal behavior against the native executor,
pin candidate container digests, verify pristine source and independent grading,
then replay with fresh observations and measure native token costs. Larger data
acquisition remains conditional on this compatibility result.

Four focused converter tests passed. Full CPU suite: 318 tests, 292 passed,
26 skipped. The first source-token run failed because the evidence script name
`tokenize.py` shadowed Python's standard library; it was renamed to
`measure_source_tokens.py`, and all 28 real-history checks then completed.
Failure and passing logs are retained. Current admitted supply has not increased;
corpus 005 still contains two quarantined examples. Pod stayed stopped; P1 remains
incomplete and no learned gain or GPU-fit claim is made.

### Submission contract reconciliation — 2026-10-09

Inspected source command sequences for fitting mini candidates, including
werkzeug-2971, dbt-snowflake-716 and brutils-python-116. Their source finish reads
an exported path-selected patch file. The pinned native submit_patch instead
stages intent-to-add untracked files, captures a baseline diff, then strips
protected files. Thus a source patch export and native submission are not
interchangeable: scratch artifacts can enter the native diff.

Added `zenithsync/submission_reconciliation.py`. The planner supports an explicit
tracked-repair/untracked-scratch profile: the current tracked binary diff must
already equal the intended patch byte-for-byte; the complete nonignored
untracked inventory must exactly match individually reviewed scratch paths.
It rejects staged changes, path traversal, duplicate paths, symlinks and changed
repair bytes. Returned scratch records contain content hashes and sizes. It
performs no cleanup, executes no source commands and grants no training approval.
Scratch designation remains a semantic review responsibility, not a filename
heuristic. The planner is a point-in-time check, not concurrent-writer protection.

Four disposable-Git tests establish the artifact mismatch, exact patch equality
after explicit fixture cleanup, mutation-free planning, and rejection boundaries.
This is not a real task replay. Before integration, any cleanup must appear as
an adapter-authored native action, with file identities rechecked immediately
before deletion and actual post-cleanup native submitted patch equality checked.
Do not call this source-teacher-authored behavior or silently change its repair.
New-source-file and staged-change reconciliation remain unsupported.

Pinned werkzeug-2971 registry metadata to
`swerebenchv2/pallets-werkzeug@sha256:6ccc246ac36fe305dd00e85767d1a0d2ec1216d82792a6eac208c573dd7d5439`:
Linux amd64, 781,021,260 compressed layer bytes. No layers downloaded or runtime
verified. Evidence: `werkzeug-v2-image-001`, `submission-reconciliation-001`.
Next: pristine V2 runtime/control qualification and actual native replay with
explicit submission adaptation; do not accept source labels as repair proof.

Full CPU retry: 322 tests, 296 passed, 26 skipped. Initial run had one failure
and one error when macOS hydration changed inventory metadata for run_p1_server.py
and model_intake.py. Stable rereads and the unchanged test suite then passed.
Both logs retained; integrity checks were not relaxed. P1 remains incomplete,
corpus 005 unchanged and quarantined, Pod stopped.

### Werkzeug V2 original-image controls — 2026-10-09

Pulled the pinned werkzeug-2971 image. Read-only offline inspection verifies
HEAD `2139fa0b2cad96053f807384a6d04d8d09717802`, clean tracked/untracked status,
Python 3.10.19 at `/usr/local/bin/python`, and package origin
`/werkzeug/src/werkzeug/__init__.py`. The image contains 5,684 reachable commits;
it is evaluator-only until sanitization. Registry digest remains
`sha256:6ccc246ac36fe305dd00e85767d1a0d2ec1216d82792a6eac208c573dd7d5439`.

Selected V2 task extraction is evaluator-only. Its problem requests increasing
the PBKDF2 default to 1,000,000 iterations. Reference changes the constant and
changelog; the test patch changes the expected default hash prefix. This is a
historical task contract, not current password-storage guidance or a claim of
cryptographic security. Source-teacher correctness still requires actual replay
and additional relevant compatibility checks.

Added `scripts/qualify_rebench_v2.py` with an explicit src-layout Python profile,
exact task/registry bindings, reserved-repository exclusion and full test-node
comparison. The shared disposable-container runner now accepts a validated
absolute interpreter path; its default remains /usr/bin/python3. Existing
source-bound historical receipts retain their old helper identity; any future
requalification must use a correspondingly pinned implementation bundle.

Original-image controls (final script, controls-002): base 11/12; reference 12/12;
all 12 publisher outcome transitions match, no node-ID collisions. Both runs
import from the declared source and leave their patched tracked diff unchanged.
Containers were offline and cleanup succeeded. No sanitized image, teacher
candidate grade or trained model result is claimed.

Three profile/entrypoint tests pass. An initial negative test caught acceptance
of an absolute test path; validation now rejects absolute, repeated-separator,
traversal and ambiguous target lists before execution. Full CPU suite: 325 tests,
299 passed, 26 skipped. Initial and final control directories are retained.

The cloud-backed local V2 Parquet read timed out. Restored the previously
published 53-file / 431,730,739-byte bundle from R2 into a local /tmp directory;
restore completed with byte verification. Extraction then used that verified
copy. This is an additional recovery check, not permission to delete originals.
Evidence: mini-source-restore-001, werkzeug-v2-{probe,evaluator,profile}-001,
werkzeug-v2-controls-002 and werkzeug-v2-source-001.

Next: sanitize the V2 root layout, verify exact tree preservation and old-history
removal, repeat paired controls, then replay the source actions and explicitly
reconcile submission artifacts. P1 incomplete; current corpus unchanged and
quarantined; Pod remains stopped.

### Werkzeug V2 exact-tree snapshot — 2026-10-09

Snapshot build/verification supports explicit source roots and interpreter paths;
legacy /testbed and /usr/bin/python3 defaults remain. The first Werkzeug build
rejected the ancestry precondition: both PR head and merge objects are absent in
the publisher image, despite older history being retained. No check was disabled
silently. Added explicit `already_absent` solution mode, requiring Git's quiet
commit lookup to return exactly missing-object status with no output. Existing
commits reject that mode; default ancestry behavior remains. Receipts explicitly
set `solution_ancestry_verified: false`. Exact declared base and tracked tree
verification still apply. Absence is not ancestry evidence.

Build 002 produced local image
`sha256:00b4cc4b5bdbc142374db2ea14e6387094e4fca157e3c50392f7dcb0c1ed1854`.
Independent offline verification checks all 311 tracked files, their content,
modes and aggregate manifest against the preserved base tree; one parentless
commit remains, no remotes, no tracked changes. Original base, PR head and merge
commits are inaccessible. Declared oracle paths at both /testbed and /werkzeug
are absent. This covers the mounted filesystem, not arbitrary inherited layers
or a universal absence-of-oracles claim.

Re-ran original and sanitized-image controls with the same current evaluator:
base 11/12 and reference 12/12 on each. Exact full-node-ID outcome maps agree
between images in both roles. Sanitization has not changed these evaluator
outcomes. This does not grade the teacher patch or establish learned performance.
Evidence: werkzeug-v2-snapshot-002, werkzeug-v2-snapshot-verify-002,
werkzeug-v2-controls-003, werkzeug-v2-snapshot-controls-001/original-parity.json.
Failed build 001 remains preserved.

Six source-snapshot tests pass, including rejection of present solutions in the
new absence mode and preservation of exact source bytes. Full CPU suite:
326 tests, 300 passed, 26 skipped. Next: qualify moving /werkzeug into native
/workspace with dependency and /testbed aliases, replay the selected source
commands, and test explicit scratch cleanup plus native patch equality. Source
and native observations must remain distinguished. P1 incomplete; corpus still
quarantined; Pod remained stopped.


### P1 continuation: native V2 replay and independently graded candidate

The selected Werkzeug mini-source trace completed offline native replay in
werkzeug-v2-replay-001. Its 23 nonterminal source commands remained unchanged;
the adapter then issued explicit scratch cleanup and native submit_patch.
There were 24 charged commands and one submission. Four reviewed untracked
scratch files were removed only after tracked diff and complete untracked-set
checks. The submitted 1,103-byte patch exactly equals the source-exported patch
(SHA-256 534f7a271cf231bb692cf9eda4dcff925c8eed7ee55629776a6d51dc7e74da4b).
The owned container was removed. No model executed, and source observations
were not reused. /werkzeug and /testbed resolve to native /workspace; the
preexisting runtime cache was explicitly moved outside the source tree.

Fresh isolated evaluation in werkzeug-v2-candidate-grade-002 verifies base
11/12, reference 12/12, and candidate 12/12, with identical complete test-node
coverage and no candidate/reference disagreements. Candidate execution receives
only its patch and the evaluator test patch, not the reference solution. The
allowance restricts candidate changes to src/werkzeug/security.py. Patch, replay,
task and sanitized-image identities are bound and checked. This is one repair
qualification result, not learned model performance or an independent statistical
estimate. The initial grader preflight compared the replay snapshot receipt hash
to the wrong snapshot file; it rejected before starting a container. That binding
was corrected to receipt.json and both subsequent grading runs completed.

Source command 11 attempts an editable reinstall in a shell pipeline. pip fails
to fetch build dependencies offline, while the final tail command returns zero.
The full failure text is retained in fresh observations. Neither the pipeline's
zero status nor the passing final patch proves installation succeeded. Existing
source imports remain qualified by independent evaluator origin checks.

Latest CPU suite: 327 tests, 301 passed, 26 skipped. Candidate allowance tests
reject traversal, metadata, test-file and duplicate allowances. These checks do
not establish GPU readiness, semantic correctness beyond tested cases, or
training admission. Native prompt reconstruction, token-budget audit, semantic
compatibility probes and admission gates remain pending. The corpus remains
quarantine-only. Keep Runpod stopped; no GPU training was started this cycle.


### P1 continuation: portable adapted history and measured token candidate

A portability audit found replay 001's cleanup depended on a support module
installed only in its disposable container. It remains useful grading evidence,
but is not the selected training-history replay. The new standalone cleanup
command embeds the inspected planner and file-identity routine, requires only
Python standard library and Git, reads the native baseline tag and patch export
at execution time, and exposes deletion as an adapter-authored native action.
No helper package is installed or imported on the replay target. Disposable Git
tests confirm exact patch preservation without an installed project and rejection
of unknown scratch files before deletion. Point-in-time checks still do not
protect against concurrent malicious filesystem writers.

Replay 002 completes 24 charged commands plus submission, with fresh tool
observations and exact intended/native patch equality. Its independent grade 003
again gives base 11/12, reference and candidate 12/12. The source offline install
failure remains visible; no source observations or teacher reasoning are copied.

build_mini_replay_history.py produces 52 messages / 25 exchanges. It verifies
source command order and exact arguments, explicitly maps the two adapter-authored
suffix actions, requires the reviewed standalone cleanup command, checks task,
profile and patch identities, and excludes reserved repositories. History 002
has identical history, mapping and tool bytes to history 001; its receipt adds
explicit cleanup-profile validation. This is reconstructed conditioning, not an
original teacher rollout or a newly generated independent example.

Pinned Gemma token audit 002 exports quarantined token/label arrays after native
nine-tool rendering and collator validation: 12,199 input tokens, 4,607 supervised
tokens. With the planned 8,192 output reserve, 12,377 tokens remain below 32,768.
The audit now checks history input identities again after encoding. A retained
history-validation report binds the identical projection bytes and token report.
No truncation, GPU fit claim, corpus admission, or learned gain is implied.

Full CPU suite: 331 tests, 305 passed, 26 skipped. Two new history tests cover
source-response exclusion, provenance and rejection of dropped, changed,
reordered, misattributed or failed terminal actions. Two additional standalone
cleanup tests use actual disposable Git repositories. The first history build
rejected a cloud-backed protocol file whose metadata changed during hydration;
a stable reread succeeded without relaxing file identity checks.

Next: integrate V2 evidence with mechanical admission, independently probe task
semantics and compatibility, resolve rights/split/runtime gates, and expand
qualified task diversity. Three token candidates would still be radically
insufficient for the planned training scale; this new candidate is not yet in
the existing two-example quarantined corpus. Keep Runpod stopped. P1 incomplete.


### P1 continuation: V2 consistency assessment and corpus 006 round trip

Added a separate V2 mechanical assessment for portable mini-source replays. It
reconstructs every native exchange and provenance mapping; binds task, profile,
replay and grading inputs; verifies intended/submitted patch equality; recomputes
full test-node comparisons from base, reference and candidate outcomes; checks
execution cleanup and test exit statuses; and checks token/label hashes, causal
label constraints, exact shifted-target counts and context/call budgets. It does
not authenticate arbitrary receipts, rerun tokenization, or approve training.
Five disposable-fixture tests exercise valid-but-unapproved evidence, exceeded
budgets, patch mutation, concealed candidate failure and changed token labels.
Werkzeug assessment 002 passes its mechanical checks with remaining gates intact.

Assembled corpus 006 from the two prior exact candidates plus the portable
Werkzeug candidate: three examples/tasks, 41,622 input and 13,708 supervised
tokens. All four schema-v2 admission gates remain null. A direct training-purpose
load fails with "Quarantine corpus cannot train" before any GPU work.
Manifest SHA-256: 016a17c1d590600f85f9f132dfeb1ae1496a8e8578c1b369e5b83344ae189cf3.
Content SHA-256: 9fcf14059899acd24d5dd00a3bfc894d793f21649d8dd4ac891acade8df9c318.

The explicit dry-run schedule uses seed 7401, one epoch, 13,708 target tokens,
and an 8,192-target update cap: three whole-example updates, zero overshoot.
Published all seven corpus files (460,221 bytes) to R2 and restored them into a
fresh /tmp directory. The restored loader reports the identical content hash,
and schedule.json plus updates.jsonl are byte-identical to the local originals.
This verifies the local R2 ingestion round trip, not execution on Runpod's volume.

Initial candidate inspection and schedule 004 rejected cloud-hydration metadata
changes. The failed schedule artifacts remain retained; stable rereads and fresh
schedule 005 succeeded without weakened integrity checks. Latest CPU suite:
336 tests, 310 passed, 26 skipped. Pod remains stopped. This is still a tiny
quarantine corpus, far short of abundant approved data or the 3×50M-token plan.
Next: independent Werkzeug semantic/compatibility checks, V2 rights and split
review, and systematic expansion to additional source tasks. P1 incomplete.


### P1 continuation: independent Werkzeug semantics and source review

The issue's historical contract is a PBKDF2 default of 1,000,000 iterations.
An evaluator-only probe independently checks that requirement and preserves
explicit-parameter behavior, legacy 600,000-iteration hash verification, rejection
of wrong passwords, and the unchanged scrypt default. Inputs include empty,
ordinary, Unicode and embedded-NUL passwords. Low explicit counts are test cases,
not recommended password settings.

The small-count oracle implements the HMAC recurrence from
[RFC 8018 section 5.2](https://www.rfc-editor.org/rfc/rfc8018.html#section-5.2):
U1 = HMAC(P, S || BE32(i)); Uj = HMAC(P, U(j-1)); each output block is the XOR
of all c values, and concatenated blocks are truncated to the requested byte
length. It does not call the standard-library PBKDF2 function internally.
Two known-answer vectors from [RFC 6070](https://www.rfc-editor.org/rfc/rfc6070.txt)
and 324 matrix comparisons with hashlib calibrate the oracle, including multi-
block output and truncation boundaries. Expensive historical/default checks use
hashlib directly. Shared primitive implementations limit independence; this is
not a cryptographic security proof.

All three fresh offline runtimes pass 326 oracle-calibration checks. On 55 task
semantic cases, base passes 48 and fails exactly the seven requested-default
checks; reference and candidate pass all 55 with identical case outcomes.
Calibration counts are separate from task-case counts. The deterministic cases
are not independent statistical samples, and the result is not a learned agent
success-rate gain. Probe execution leaves tracked source unchanged and owned
containers are removed. Evidence: werkzeug-v2-semantic-probes-001.

A separate exact-snapshot source capture compares candidate and reference ASTs
for security.py, excluding only docstrings and source locations. They match;
base and reference do not. The sole changed function docstring is
 generate_password_hash, reflecting the new default. This equivalence excludes
introspection and traceback/source-location behavior and does not establish the
reference is universally correct. The reference also updates CHANGES.rst;
the candidate patch does not claim to reproduce that changelog edit.
Evidence: werkzeug-v2-source-review-001.

Captured the snapshot's tracked LICENSE.txt and copied pinned Open-SWE-Traces
and SWE-rebench-V2 cards plus the task dataset license into attribution evidence.
Both dataset cards declare CC BY 4.0; repository notices remain separate. The
attribution record lists all trajectory transformations and unresolved review
items. No rights, split, runtime or task-alignment corpus gate is automatically
approved. No product/training code changed in this cycle, so the previous full
CPU result remains 310 passed / 26 skipped; the new evaluator probes are reported
separately. Corpus 006 remains three quarantined examples. Pod stays stopped.


### P1 continuation: pipdeptree candidate held after pinned type checks

Reviewed mini-source candidate 168469d9-e93e-438b-9f73-120b2f6f6088 for
 tox-dev__pipdeptree-310. The issue asks for consistent unconstrained dependency
version serialization. Resolved the source image to immutable digest
07746f257fa029380050e8b395ac372c3fd938a598fc05267f1f4dcf0d4c7e2d, acquired it
locally, and verified its clean declared base
06c2f9d518f8bd7d8fa7f3520e231cdf15f0cd7f (410 commits, expected src import).
PR head and merge objects are absent. This image has not been sanitized for
agent execution; no native teacher replay or publisher test grading occurred.

The trace changes ReqPackage.as_dict to return dict[str, str] but leaves its
abstract Package method returning dict[str, str | None]. Repository tox.ini
pins mypy 1.7.1 and pyproject.toml enables strict checking. Prepared exact
Linux/Python-3.10 mypy wheels (with explicitly pinned supporting packages),
hash-checked them, and installed them only in an offline disposable evaluator.
The original image and training/runtime environments were not modified.

Full-source checks under the same checker and installed dependency environment:
base and reference each have three existing errors; the source-observed teacher
patch has those plus two new diagnostics: an incompatible override and an unused
ignore in dag.py. To separate the override from preexisting dependency/type
issues, extracted only the three relevant class method signatures from each
patched source and checked them independently: base and reference pass; the
teacher signature fails with the same override. This is a source-patch screen,
not a fresh model-generated failure or proof the full reference CI passes.

The type distinction is substantive: mutable dict value parameters are invariant,
so dict[str, str] is not a subtype of dict[str, str | None] for this override.
See the [mypy variance explanation](https://mypy.readthedocs.io/en/stable/common_issues.html#invariance-vs-covariance);
the actual experiment used the repository's 1.7.1 pin, not current documentation's
release. Runtime success on the reported JSON case would not remove this static
contract regression. Evidence and decision: pipdeptree-v2-review-001/report.json.
The candidate remains excluded from positive training data. Corpus 006 is
unchanged at three quarantined examples / 13,708 supervised tokens.

Added static_controls.py: bounded noncolored mypy output parsing, exact diagnostic
multiplicity, path/code/message comparison across base/reference/candidate, and
strict summary/exit-code consistency. Source line movements and diagnostic order
do not count as new errors. Unknown output and checker infrastructure failures
reject. Four tests cover new errors amid old ones, line/order invariance,
duplicate multiplicity, and malformed/fatal/contradictory output. This comparison
requires independently qualified equal environments and does not grant admission.

Next: move to the next candidate and reuse the source/runtime checks; do not
silently repair this teacher using the evaluator reference or relabel its
publisher status as verified correctness. Preserve this counterexample for
future negative-example or repair-recovery research with explicit provenance.
Pod remains stopped; no GPU training started. P1 remains incomplete.


Static-control cycle validation: full CPU suite 340 tests, 314 passed, 26 skipped.
The initial run retained one error and one failure caused by cloud hydration
changing run_p1_server.py and model_intake.py metadata during integrity reads.
No checker was relaxed; after that run terminated, a fresh complete run passed.
Both logs are retained in the archived evidence package.


### Dynaconf recursive-equality screen (local, pre-admission)

Pinned original image `sha256:d25a589823a03ab10900ae43aeda1c3845b78d97921702ad91138189ef0d0ad6`
was tested offline at task base `b389b2bbb07b2abb92577e81384f7f939b05c5f5`.
Compared base, publisher reference, and the exact source-observed teacher patch
from message 51. This is evaluator screening, not native agent replay.

Enumerated 202 distinct ordered expression trees of depth at most two using
AND/OR and required-name leaves A/B. Across 40,804 ordered pairs per role,
structural equality mismatches were base 39,800, reference 448, teacher 0.
Registering two independently constructed copies of each tree retained 3, 74,
and 202 entries respectively. Ordered structure is a deliberately conservative
screening oracle; Boolean-equivalent trees need not be structurally equal.
These are exhaustive finite cases, not independent statistical trials.

A concrete reference collision is A AND (A AND B) versus A AND (A OR B).
With A present and B absent, real Dynaconf validation rejects the first and
accepts the second, yet the reference treats them as equal. All four truth-table
rows were checked against those Boolean predicates. The teacher distinguishes
them. This exposes a reference limitation; it does not establish universal
correctness of the teacher or permission to train from evaluator information.

Evidence: `evidence/data/dynaconf-v2-semantic-screen-001`, reproducible drivers in
`evidence/data/dynaconf-v2-semantic-source-001`. All roles imported the repository
package, left tracked source unchanged, and the owned offline container was
removed. Native replay, publisher tests, lineage/snapshot qualification, token
admission, and corpus gates remain pending. No training infrastructure changed.
Corpus 006 remains three quarantined examples / 13,708 supervised tokens.
Runpod stays stopped. P1 remains incomplete.


### Dynaconf native qualification and historical evidence support

Resolved the task's upstream pull request at https://github.com/dynaconf/dynaconf/pull/413.
The old owner path now redirects to a different mirror repository, whose PR 413
returns 404. Canonical upstream validator.py at the task base matches the pinned
image byte-for-byte; this is file-level corroboration, not whole-repository proof.
The original image is clean at the expected base, with 457 reachable commits;
PR head and merge objects are absent. Two failed diagnostic runs are retained:
the diagnostic used the same dictionary key for repository HEAD and PR head.
Run 003 separates these fields and verifies the expected base correctly.

Built and independently verified sanitized snapshot
`sha256:4ddee414e4597204acde8b3ebca8cfb550ff1d0bfcafbba95c2b5d17f90acd5a`:
511 tracked files preserved, one parentless commit, old base/head/merge objects
inaccessible, known oracle files absent. This verifies the mounted filesystem,
not inherited Docker layer contents. Original and snapshot publisher outcome
maps match exactly: base 24/26, reference 26/26.

Native replay 001 completed 26 charged tool calls plus submit_patch, yielding
the exact source-observed patch. Candidate grading passed 26/26 publisher cases.
History 001 contains 56 messages / 27 exchanges. Token audit 001 exported
20,299 input and 6,870 supervised tokens; input plus 8,192 reserve is 28,491,
below 32,768. Mechanical admission 001 passes without granting training approval.
One broad source test command fails collection because optional dependencies
are absent; this error is retained, not transformed into successful verification.
Native replay is teacher trajectory reproduction, not a newly trained agent result.

The qualifier now explicitly supports src and flat package layouts. Exact
repository import origin and package-scoped candidate source allowances remain
required. Historical evidence can explicitly map implementation files to an
archived source copy with the original hash; mapping data, patches, or receipts
is prohibited, and unused mappings reject. Existing Werkzeug evidence was
successfully reassessed with its original archived qualifier in admission 005.
Two prior attempts stopped on macOS cloud hydration metadata changes; after
reading the files locally, the unchanged integrity checks passed. The archived
code is checked as historical evidence; current reconstruction checks still run.

Validation: 13 focused tests pass; complete CPU suite 344 tests, 318 passed,
26 skipped. No GPU checks ran. Source lineage, snapshot, controls, replay,
history, token, and admission evidence are under evidence/data/dynaconf-v2-*.
Dynaconf remains pending final attribution/split/semantic review and assembly;
corpus 006 is unchanged at three quarantined examples / 13,708 supervised tokens.
P1 is incomplete; Runpod remains stopped.


### Corpus 007: four-task quarantine integration

Added the native Dynaconf replay to the quarantine assembly; preserved MIT
repository notice, pinned CC-BY-4.0 dataset cards/license and transformation
notes in dynaconf-v2-attribution-002. Dependency/observation rights and teacher
service-term coverage remain unapproved. Attribution attempt 001 stopped on a
cloud-file metadata change; checks were preserved and attempt 002 succeeded.

Current assembly: four examples and four tasks, 61,921 input tokens and 20,578
supervised tokens. Manifest SHA-256:
`24b6b11a8a111174eac74631043d2804a32bb83b7584a152fc489a6dbcdd0610`.
Content SHA-256: `0a0ac1667b6b6e4096f3aabc0a0c932f7da960d4fcc01e61b7e00f4ad4eb3f7c`.
All four admission gates remain null. Direct purpose=training loading rejects
with `Quarantine corpus cannot train`; no training ran.

Fresh GitHub metadata resolves four source projects, the old Dynaconf mirror,
and all four named reserved repositories. No repository-ID or declared
fork-network overlap is found. The old URL resolves to dynaconf-mirror with fork=false; this metadata alone
cannot establish historical independence.
Dynaconf is explicitly grouped under canonical dynaconf/dynaconf in the corpus.
Final semantic duplicate review, historical/detached-copy grouping, and frozen
splits remain pending; reserved task bodies were not opened.

Published all nine corpus files (684,444 bytes) to R2 and restored to an empty
/tmp directory with verified hashes. Restored loader counts and content hash
match. A one-epoch schedule, seed 7401, target 20,578 supervised tokens and
8,192-token update cap produces four whole-example updates, zero overshoot.
Schedule and updates files from restored data match original bytes exactly.
Schedule attempt 006 stopped on cloud hydration of training_corpus.py; attempt
007 completed with unchanged integrity checks. No optimizer or GPU ran.

Evidence: training-corpus-assembly-007, publish-007, restore-007,
restored-inspection-007, schedule-007, restored-schedule-006, denial-005, and
current-corpus-lineage-002. Code was unchanged this cycle; integration was
verified by actual assembly, rejection, transfer, restore and schedule replay.
The latest code suite remains 318 passed / 26 skipped. Four quarantined examples
are not sufficient for the planned 3x50M candidates; repeated exposure would
not create additional independent tasks. Continue corpus qualification and
admission review locally. Keep Runpod stopped. P1 remains incomplete.


### Workalendar qualification and corpus 008

Qualified peopledoc__workalendar-493, canonical workalendar/workalendar. Original
image digest sha256:3837c3917cae0f429c4540fe570a3d9b68d70615e86995b9a2fc9ea62abebb41
has clean task base 3fd9b831b308f1b0f7e1ca8fffc456ab6bdce56a, 1,008 reachable
commits and no local PR head/merge objects. Sanitized snapshot
sha256:5125f7b3193618806b0a734412dd43486b88fed20d94d49c6cc7467e4735076f
preserves 177 tracked files exactly, one parentless commit, no old base/head/merge
objects or declared oracle paths. Verification concerns the mounted filesystem,
not inherited image layers. Original/snapshot publisher outcomes match exactly:
base 8/11; reference 11/11.

Native replay 002 completed 29 charged calls plus submit_patch; submitted bytes
match the separately screened teacher patch. Candidate passed 11/11 publisher
tests. Independent finite checks: base 0/18, reference 18/18, candidate 18/18.
These cover exact registered/unknown lookups, warning category/count, registry
nonmutation, subclass delegation and exception propagation, not calendar-date
correctness or statistical generalization. An unmatched grep and nonexistent
source-requested pytest node remain errors in the fresh native history. Pipelines
that truncate test output are not treated as independent full-suite evidence.

History 002 has 62 messages / 30 exchanges. Token audit 001: 20,149 input and
7,312 supervised tokens; with 8,192 output reserve, 28,341 fits 32,768.
Mechanical admission 002 passes, without training authorization. Captured the
MIT repository notice and pinned dataset notices; dependency/observation rights
and teacher service terms remain pending.

Local Desktop cloud offloading delayed the existing runtime/profile processes.
Explicit macOS materialization requests allowed them to resume; runtime 001
then correctly rejected a metadata-changing integrity read. Fresh runtime 002
passed. Similar integrity rejections preceded successful semantic-screen 002,
replay 002, history 002, admission 002 and corpus-denial 007. No integrity check
was relaxed; prior outputs/scripts are retained where written.

Corpus 008: five tasks, 82,070 input / 27,890 supervised tokens. All admission
gates remain null and purpose=training is rejected. Manifest SHA-256:
4ced40b5cb89e799a845cd833ae7d34a0c291b170a6a8988f4a028f7e411bf45.
Content SHA-256: b9b1451ea77f89f9a19d50dbc218976af0a8a456bc65f47cf6fcd6d731f626b9.
Published 11 files / 905,531 bytes through publish-009; restored and validated
through restore-008 / restored-inspection-008. One epoch, seed 7401, 8,192-target
update cap: five whole-example updates, zero overshoot. Original schedule-008
and restored-schedule-007 schedule/update bytes match exactly.

Metadata-only lineage audit 003 resolves all five source projects, aliases and
four reserved repositories without known ID/fork-network overlap. This excludes
neither detached copies nor semantic duplicates. No held-out issue bodies read.
No shared implementation changes this cycle; the prior 318-passed/26-skipped
suite is unchanged, not newly rerun. Five quarantined examples remain far below
the planned training supply. Continue local corpus expansion and gate review;
Runpod remains stopped and P1 remains incomplete.


### PennyLane 5716: independent numerical screen, interface gate still closed

Selected the batched StronglyEntanglingLayers issue from 16 source-context-fitting
candidates; mini-candidate-priorities-002 records current status and qualitative
selection rationale. This task adds tensor-shape and quantum-circuit numerical
coverage. It is not yet a sixth corpus example.

Pinned original image sha256:b41317e4fdf7780cc28d1e5eed4a65e69159331091f6749fde7a92f29c5f4a94
runs PennyLane 0.37.0-dev on Python 3.10.19 at clean base
85ff62b9c9218f523ef7ff0535cde7cbf55ebb7b; 4,180 reachable commits,
PR head/merge absent. Verified sanitized snapshot
sha256:e60eb0ef6d062901bedc874d4c731c438b7182d707f06704c0382f8c62800f23
preserves all 1,353 tracked files, one parentless commit, no accessible old
base/head/merge objects or declared oracle paths. Mounted filesystem only;
this does not audit inherited image layers.

Independent dense-state oracle constructs RZ(omega) RY(theta) RZ(phi), Kronecker
operators and explicit computational-basis CNOT permutations, without reusing
the template/decomposition. Rotation convention follows
https://docs.pennylane.ai/en/stable/code/api/pennylane.Rot.html; that current
reference is not a claim about the installed version. Primitive gate calibration
against the pinned runtime establishes matching conventions before comparison.
Seed 5716; batch sizes absent/1/2/4, layer counts 1/2/3, wire counts 1/2/3:
36 cases per version. Reference and source-observed teacher pass 36/36; base
passes 15/36. Candidate maximum absolute state error is 3.554447978966673e-16,
with required atol 1e-11 and rtol 0. Norms also checked. These are finite NumPy
calculations, not independent statistical trials or universal correctness proof.

Screen 002 initially supplied explicit zero ranges for one-wire circuits, which
this constructor rejects. It therefore recorded 12 probe-input failures for
both fixes. Screen 003 uses the supported default in these cases; both runs
are preserved. Other failed attempts stopped on cloud-hydration metadata drift;
none of the integrity checks was relaxed. Runtime 002 is the completed bound run.

Full publisher-module controls collect 44 tests. Base: 29 pass, 12 fail,
3 skip; reference: 41 pass, 3 skip. The strict grader rejects skipped controls.
The skipped tests exercise JAX, TensorFlow, and Torch interfaces, including
gradients; dependencies are absent. Dependency metadata, repository requirements,
test source, and skip mechanism captured under pennylane5716-v2-dependencies-001.
Do not drop these tests or equate 41 passing calls with fully qualified controls.
Next: derive compatible pinned backend dependencies, install in a separately
qualified offline runtime, and rerun complete controls and snapshot parity.
Native source replay, token assessment, attribution and split review remain.

Evidence: pennylane5716-v2-review-001, semantic-screen-003, controls-original-002,
runtime-002, snapshot-verify-001. Shared implementation unchanged this cycle;
prior code suite remains 318 passed / 26 skipped, not newly rerun. Corpus 008
remains five quarantined tasks / 27,890 supervised tokens, all gates pending.
Runpod stays stopped. P1 remains incomplete.


### PennyLane backend qualification follow-up

A separately built offline dependency image now passes pip check and imports
PennyLane, Torch 2.3.0+cpu, JAX 0.4.23, TensorFlow 2.16.1, tf-keras 2.16.0,
and cvxpy 1.4.2. SciPy is 1.12.0, following source CI; cvxpy was adjusted
for compatibility. Original wrapt 1.12.1 remains installed. This is an
explicitly changed runtime, not a claim about the publisher image unchanged.
Image: sha256:5269b39ab665401139db6d6953893c831f1f5ae1cae7eecce6366472e8b71051.

Supplementary paired publisher tests: base 32 passed / 12 failed; reference
44 passed; zero skips. Tracked source remained unchanged during each test run.
Task recovered from the previously hash-verified source shard; recovery checks
its complete SHA-256 again. Four independent dense-state finite-difference
checks cover 72 Torch gradient components, batch sizes 1/3 and depths 1/2
on two wires. Maximum gradient discrepancy: 6.66134231108728e-11; repeated
fresh-tensor gradients agree exactly. These finite cases are not a proof for
arbitrary circuits, framework versions, or training behavior.

Evidence: evidence/data/pennylane5716-v2-backend-summary-001. The 1.005 GB
wheel/build/evidence bundle is being published through the existing verified
R2 transfer path; only its terminal verified receipt establishes archival.
Strict admission integration, sanitized snapshot parity, native replay,
token-fit assessment and attribution remain pending. Corpus 008 is unchanged,
Runpod remains stopped, and P1 is not complete.


Backend snapshot follow-up: independent verification passed for all 1,353
tracked files. The original and expanded snapshots have the same source tree,
tracked-file manifest digest and byte counts. The expanded snapshot has one
parentless commit, no accessible original base/merge commits, and no known
oracle files in its mounted filesystem. Inherited image layers are outside
this isolation claim. Both 44-test publisher runs have exactly the same
per-test outcomes before and after sanitization (32/12 base; 44/0 reference;
no skips/errors). See backend-snapshot-verify-001/source-parity.json and
backend-snapshot-paired-001/parity.json under evidence/data/pennylane5716-v2-.
Native replay and admission integration remain pending; corpus unchanged.

R2 backend bundle publish-002 completed with verified receipt: 107 files,
1,005,376,281 bytes. This archive covers the backend build and initial
controls/gradient evidence; the later snapshot verification and parity
evidence require a subsequent archive. Publish-001 failed before completion
and is not treated as a backup.


PennyLane native replay now completed (35 charged calls plus native submission;
36 exchanges / 74 messages). Candidate-grade-003 passes all 44 cases;
admission-001 recomputes the full evidence with no mechanical blockers.
Native-tokens-003 records 21,157 input / 7,139 supervised tokens, untruncated.
Corpus 008 remains unchanged pending attribution and repository split review.
Source patch body is identical; Git index abbreviations differ (8 versus 7
characters). Stable Git patch IDs agree. The unsupported double-batch example
and no-match grep error remain visible in the native history.

Evaluator profiles now optionally declare supplemental pass-to-pass tests and
an explicit repository pytest root. For this task, 41 publisher expectations
remain unchanged; three backend tests are separately declared and must pass
both controls. Exact complete coverage, setup/teardown success and no-skips
requirements remain enforced. Admission rechecks a hash-bound supplemental
profile. Focused suite: 25 tests passed. Full suite is running; no full-suite
success claimed yet. Snapshot/CI archive verified: 69 files / 227,052 bytes.

Full CPU suite rerun completed: 349 tests, 323 passed and 26 skipped.
The initial run had two source-hydration integrity failures; both logs are
retained. No integrity check was relaxed. This does not prove GPU readiness.


### Corpus 009: PennyLane integration, still quarantined

Six tasks now total 103,227 input / 35,029 supervised tokens. Manifest SHA-256:
`066260151fe14e4778837b124235a25e013d650a3b542915daae79a5f52dd5b0`.
Content SHA-256: `23531344ea84e04f3feb260d5ef9b0155f413974088a761837206f807a6a2b58`.
All four admission gates remain null. Training-denial-008 confirms refusal.

Publish-010 and restore-009 verified 13 files / 1,143,461 bytes. Restored
inspection-009 validates all six examples. Schedule-010 and restored-schedule-008
are byte-identical: seed 7401, one epoch, 35,029 supervised tokens, six
whole-example updates, 8,192-target update cap, zero overshoot. No optimizer or
GPU execution is implied. Failed schedule-009 stopped on cloud-hydration drift.

PennyLane attribution-001 captures Apache-2.0 repository license, observed-file
header and pinned dataset notices. Complete rights review remains pending.
Lineage-004 resolves current canonical repository IDs and declared fork roots
for six source projects, aliases and reserved evaluation repositories, with no
overlap. Detached copies, semantic duplicates and historical forks remain outside
that metadata screen. Native qualification archive verified: 341 files /
1,988,275 bytes. Earlier backend wheel bundle and snapshot archive are also verified.

Current suite: 323 passed / 26 skipped (349 total); focused control/admission
suite: 25 passed. Real-corpus GPU training, held-out learned improvement, final
rights/split approval, and abundant data supply remain unfulfilled. Pod remains
stopped. Next: archive corpus integration evidence, then expand the qualified
candidate pool without treating repeated exposure as new data.


### Linkding 691 candidate qualification

Pinned clean base edd958fff61a640cf02c7640b717e78f10322b8b; sanitized
296-file snapshot verified with exact publisher-control parity. Native replay
completed 27 charged calls plus submit; patch matches its fresh intended export.
Candidate and reference pass 6/6 publisher tests; base passes 5/6. Independent
real child-process argv and gzip checks: base 2/77, reference/source candidate
77/77. No browser, website-access or network success is claimed.

Native history: 18,910 input / 8,540 supervised tokens, untruncated; mechanical
admission passes. The 8,192-update target cap rejects this whole example as
intended; a metadata-only 9,000-cap probe preserves it in one update. Neither
probe establishes GPU fit. Corpus 009 stays unchanged. Source mock-test claims
and a permissive exception check require explicit quality review; attribution,
split review and integration remain pending. See linkding691-v2-review-001.


### Two additional positive-supervision exclusions

Linkding 691 remains outside corpus 009 despite passing mechanical grading.
Supervision-review-001 binds two exact unsupported claims to assistant tool-call
commands, which the current loss mask labels: a mock-only test asserts external
website access, and a permissive exception test claims success without proving
its requirement. Preserve original evidence; do not silently sanitize the trace.
A replacement trajectory or separately specified selective-supervision policy
must be qualified before reconsideration. Its initial qualification archive is
verified in R2: 147 files / 712,237 bytes.

Scrapy 6897 is held for a reproduced source-candidate type regression. The pinned
source tox.ini requires mypy 1.14.0 and Python 3.9. Exact extracted constructor
bodies (with explicit external types) pass for base/reference; candidate fails
with `Attribute "path" already defined [no-redef]`. Checker executed on local
Python 3.13 with target 3.9; this is not a full repository or native CI run.
The source command calls this edit a type-annotation fix, so it is unsuitable
positive supervision without replacement. No native replay or publisher tests
were performed for this candidate. See scrapy6897-v2-review-001 and the saved
checker inputs/results. Priority review 003 records both exclusions. Corpus 009
remains six quarantined examples / 35,029 supervised tokens; no GPU work started.


### Kubernetes client 247: source test acceptance counterexample

The source trace's index-28 integration-test function claims successful URL
conversion whenever an exception lacks the substring "hostname is invalid".
An isolated run of its exact class/function definitions accepts both a substitute
that raises an unrelated RuntimeError and a no-op substitute. A negative control
with the expected error substring is rejected. No network or repository code
was executed; this establishes unsound test acceptance, not a broken URL fix.

The candidate is held out of positive supervision because its success-printing
code would become assistant-call training targets under unchanged replay policy.
No native history or token arrays have been produced. Preserve the original
trace and the executable counterexample; do not rewrite it to look successful.
The evidence can support future error-analysis work, but is not automatically
approved as negative training data or a preference pair. Priority review 004
records the hold. Corpus 009 remains unchanged and Runpod remains stopped.

### Brutils 116: verification accepts a broken formatter

The exact source index-48 verification script exits zero and prints that all
requirements are verified when run against an explicit substitute returning
`WRONG_FORMAT` without calling validation. Its own output reports that the
validation-call requirement is false. This is an isolated acceptance-logic
counterexample, not an execution of the repository or proof that its patch is
wrong. The trace is held out of positive supervision; source evidence is retained.
See `brutils116-v2-review-001` and priority review 005. No native replay or
publisher tests were run for this candidate.

`scripts/review_python_test_source.py` now records hash-bound, non-executing
review hints for explicitly selected Python snippets. On the saved Brutils and
Kubernetes snippets it locates the known success message and broad exception
handler. Findings never decide admission; absent findings never prove quality.
Literal matching misses aliases and computed messages, and legitimate checks can
precede a flagged message. Executable counterexamples and contextual review remain
necessary. Seven focused tests cover the hints, non-execution, source identities
and preservation of existing reports. Corpus 009 and its unresolved admission
gates remain unchanged.

The source-test review integration regression run completed 356 tests: 330 passed
and 26 skipped. This local suite does not validate GPU training readiness.

### Online-judge-tools 445: repair supported, environment qualification pending

The base, reference and source-candidate versions pass 12/18, 18/18 and 18/18
local HTML cases respectively. The probe executes the exact extracted
`_parse_start_time`, `_load_details` and `get_name` methods with a real HTML parser
and a substituted HTTP boundary. It checks penalty values, duration and cached
name reads. The six base failures concern singular English `minute`. These are
generated fixtures, not historical website responses, and this screen is not a
full repository test or native replay.

The pinned original image imports the correct base repository under Python
3.7.17. Its original `test_load_details` fails offline with a DNS-derived
connection error. No conftest or HTML/YAML/HAR fixtures were found in the recorded
search. The publisher tests need further reproducible environment work; they
must not be reported as passing based on the separate semantic screen. Source
supervision review also remains open because its scenario script tests a copied
regex rather than calling repository `get_name`.

See `onlinejudge445-v2-review-001` and priority review 006. The task remains
pending, not rejected as a faulty repair and not admitted to training. Authentic
attributable response fixtures, or an explicitly separate supplemental offline
evaluator, are the next investigation. Corpus 009 is unchanged.

### Online-judge-tools 445: current recorded-response controls

Five current public AtCoder pages were captured with exact URLs, retrieval times,
HTTP status and body hashes. The reported contest still displays singular
`minute`. Replaying those exact bodies at the requests Session transport boundary
in the pinned offline image yields base 7/8, reference 8/8 and candidate 8/8 for
the publisher assertions. Complete collected identities and setup/call/teardown
phases pass the strict transition comparator. No publisher assertion was changed.
The earlier unchanged offline environment failure remains valid and preserved.

Seven separate transport checks pass: exact body bytes, response metadata,
unknown URL rejection, unrecorded-language rejection, POST rejection, GET-body
rejection and restoration of the original transport. This experimental adapter
is task-specific qualification code, not yet shared native replay support.

See `onlinejudge445-v2-response-replay-002/comparison.json`,
`onlinejudge445-v2-transport-check-001/checks.json` and review 002. Current pages
are not proven identical to the 2019 responses. Access to public HTML does not
establish redistribution or training rights; that review remains unresolved.
Source isolation, native replay, resource integration and supervision review also
remain pending. No examples were added to Corpus 009 and no GPU work started.

### Reusable Session response adapter

`zenithsync/session_resource_replay.py` validates the complete response mapping
before installing an exact prepared-URL GET adapter in a disposable process.
It rejects authentication/cookies, conditional reads, POST or GET bodies,
unrecorded URLs, response hooks and unsupported transport settings. Response
bytes and content type are retained; text decoding uses the documented UTF-8
convention. It does not reproduce the general HTTP protocol or TLS behavior.
Restoration is explicit and the adapter is not safe for concurrent installation.

Seven focused tests pass in the requests-enabled environment, including
no-network byte replay, invalid-record atomicity and rejection paths. The full
local discovery run completes 363 tests: 330 passed, 33 skipped. Seven of those
skips are these new tests because that suite's environment lacks requests; their
separate successful run is retained rather than counted as full-suite passes.
In the pinned Python 3.7 task image, the shared adapter independently reproduces
the eight expected publisher transitions (base 7/8, both repairs 8/8); see
`onlinejudge445-v2-response-replay-003/comparison.json`.

This is reusable transport code with an exercised task integration. The shared
native replay CLI and qualification/admission bindings still need resource
support before the task can enter the native corpus pipeline. Training remains
unapproved and the six-example corpus remains unchanged.

### Bound response bundles and native staging

`session_resource_bundle.py` now requires complete capture coverage, an exact
capture-receipt hash, matching body identities/content types, unique response
URLs and local filenames, and an explicit cumulative byte budget. Redirects,
failed responses, changed files and symlink bodies are rejected. The five-page
AtCoder bundle contains 103,669 response bytes and remains unapproved for training.
Capture metadata links evidence; it does not prove authenticity or grant rights.

`replay_mini_source.py --session-resources` requires a reviewed profile containing
the exact bundle receipt identity and byte budget. It stages only body data,
the transport module and startup code, records their identities, and explicitly
marks injected support modules. Existing admission rejects that flag; no new
training-admission path has been enabled. The previous replay implementation is
preserved under `artifacts/official/mini-replay-before-session-resources-001` for
historical hash-bound evidence.

The real native ContainerManager staging probe in the pinned Python 3.7 image
served the captured singular-minute page and rejected an unknown URL. Deliberate
hash corruption caused the next Python process to exit 78 before its user code
ran. Owned-container removal was confirmed. This tests staging/startup, not a
full teacher trajectory or protection against a malicious process bypassing
Python startup. See `session-bundle-native-staging-001/receipt.json`.

Fourteen focused bundle/transport tests pass in the requests-enabled environment.
Full discovery completes 370 tests: 337 passed, 33 skipped. Shared qualifier
resource bindings, native trajectory qualification and resource-aware admission
review remain outstanding. Corpus 009 and all training gates are unchanged.

### Shared qualifier resource integration

The V2 qualifier now accepts an explicitly profile-bound Session response bundle,
records its receipt, capture and body identities in qualification inputs, and
checks that a candidate replay used the same bundle and adapter as its grader.
Missing resources or a mismatched receipt are rejected before container startup;
the preflight denial probes recorded zero container calls and no output directory.

An explicit `publisher_nodes_only: true` profile option selects every declared
FAIL_TO_PASS and PASS_TO_PASS node within the reviewed test files. This avoids
implicitly running unrelated website-dependent tests. Duplicate/foreign nodes
are rejected and the existing strict comparator still requires exact outcome
coverage. Reports retain the scope of current recorded-response transport.

The shared qualifier, exercised in two separate base/reference containers, passes
all eight expected publisher transitions for online-judge-tools 445: base 7/8,
reference 8/8. The final source-bound result is
`onlinejudge445-v2-bound-controls-002/report.json`. No native candidate was supplied
to this run. Twenty-four focused tests pass; full discovery completes 372 tests,
339 passed and 33 skipped. Previous shared implementations and the first control
run's implementation are retained in `artifacts/official` for evidence integrity.

Remaining work for this task includes sanitized source isolation, full teacher
replay, grading its submitted patch, and resource-aware admission and supervision
review. The current admission rejection for injected support modules remains in
force; corpus size and training approval are unchanged.

### Online-judge-tools snapshot and native workspace preflight

The first snapshot build exposed a Python 3.7 incompatibility in the containment
check (`Path.is_relative_to`). The replacement uses component-aware `relative_to`
with a ValueError boundary, retaining the containment policy. Seven snapshot
tests pass, including prefix-confusion rejection; full discovery completes 373
tests, 340 passed and 33 skipped. The earlier implementation and failed build
remain preserved.

Snapshot build 002 and verification 001 preserve all 89 tracked files and the
exact source tree. One parentless commit is reachable; the old base, PR head and
merge commits are inaccessible, and the declared oracle paths are absent. This
is mounted-filesystem evidence, not an audit of inherited Docker layer bytes.
The same eight recorded-response publisher transitions pass on the sanitized
image, with base 7/8 and reference 8/8.

Native replay attempt 001 terminated at workspace preparation, before any source
trajectory command. Traced diagnosis identifies six untracked
`online_judge_tools.egg-info` metadata files and one `__about__.cpython-37.pyc`
cache file. The owned container was removed. No broad cleanup or allowlist
exception was added. These exact leftovers require reviewed handling and another
native replay attempt; do not describe this attempt as a successful trajectory.
See `onlinejudge445-v2-workspace-diagnostic-001/report.json` and the retained
native replay receipt. Training remains unapproved.

### Online-judge-tools native replay and graded patch

The exact six installer metadata files were relocated byte-for-byte outside the
source workspace in an owned derived image. A path-only site-packages entry
preserves distribution discovery. Version 6.3.0, metadata location, source import
and the console entry point were checked. Only the reviewed bytecode cache was
removed. The tracked tree and snapshot isolation were independently reverified.
The strict workspace preparation policy was not relaxed.

Replay 002 reached cleanup and exposed Python 3.7 incompatibilities in the
standalone cleanup code (assignment expression and `Path.is_relative_to`). The
replacement preserves file-identity and path checks. The failed attempt and
previous shared implementations are retained. Six cleanup tests pass and full
discovery remains 373 tests: 340 passed, 33 skipped.

Replay 003 completes with 29 charged calls plus native submission (30 recorded
exchanges), all tool outcomes successful, intended/submitted patch bytes equal,
and confirmed container removal. The resource-bound native grade matches all
eight reference outcomes; base is 7/8, reference and native candidate are 8/8.
See `onlinejudge445-v2-native-replay-003/receipt.json` and
`onlinejudge445-v2-native-grade-001/report.json`. This is teacher replay evidence,
not model inference or learned improvement.

History construction was attempted and rejected by the existing portable-replay
gate for injected support modules. No history or token arrays were produced.
Resource-aware history/admission contracts and supervision/rights review remain
required; the gate has not been bypassed and no training example was admitted.

### Resource-aware history reconstruction and context audit

The history builder now accepts an explicit Session bundle only after verifying
its capture/body identities, reviewed receipt and budget, replay producer hashes,
adapter bytes, startup hash and exact PYTHONPATH. All resource inputs and the
binding verifier are included in the history receipt. Missing bundles, altered
producer/configuration bindings and changed response bytes reject. This proves
configuration and byte consistency, not training permission or semantic quality.

The final history 003 contains 62 messages / 30 exchanges. Token audit 002 exports
19,438 untruncated input tokens and 7,151 supervised tokens. It fits the 32,768
input cap and leaves room for the configured 8,192-token reserve; it also fits
the 8,192-supervised-token update limit. No model weights or GPU were used.

Six focused binding/history tests pass. Full discovery completes 377 tests:
344 passed, 33 skipped. A real admission attempt still rejects the resource-backed
replay under the unchanged portable-replay gate; its failure log is retained.
Resource-aware admission, supervision quality, rights and final corpus gates
remain unresolved. These exported arrays are unapproved candidates, not part of
the assembled training corpus. The prior history-builder implementations remain
archived for hash-bound evidence.

### Resource-aware mechanical assessment; online-judge-tools supervision hold

Assessment now verifies the replay/history/grader resource chain, bound grader
profile, actual cached response bytes and adapter in each control container,
and the recorded transport events. It recomputes tests, histories and token
budgets as before. Four copied-evidence attacks (body, adapter, denied transport
event and claimed bundle metadata) reject. Orphaned resource claims on a portable
replay also reject. Full discovery completes 378 tests: 345 passed, 33 skipped.

Online-judge-tools 445 passes this mechanical assessment with 19,438 input and
7,151 supervised tokens. The result explicitly does not approve training.
Substantive supervision review instead holds the trajectory: its unmodified
source-index-50 scenario script exits successfully and claims to test `get_name`
on the actual broken base, while calling the real repository `get_name` with the
captured contest page raises AssertionError. The copied regex test does not
exercise the claimed repository behavior. This does not invalidate the repaired
patch, which passes eight graded cases; it invalidates the unchanged test claim
as positive command supervision.

See `onlinejudge445-v2-admission-001`, `resource-admission-negative-001`,
`onlinejudge445-v2-supervision-screen-001`, supervision review 001 and priority
review 009. Preserve the trace and counterexample. Reconsider only with qualified
replacement supervision or a separately specified selective-supervision policy.
Corpus 009 remains six quarantined examples / 35,029 supervised tokens.

### dbt–Snowflake 716: method contract screened, native replay pending

The task was extracted from the hash-verified SWE-rebench V2 shard. Source and
Apache-2.0 notice were retrieved at its exact base commit. The initial capture
used the wrong license filename and remains recorded as failed; capture 002
uses the actual `LICENSE.md` path.

The candidate patch produces the same connections file and cancellation-method
AST as the publisher reference. Eleven constructed method-level cases execute
that exact AST with observable adapter/cursor boundaries: base 2/11, candidate
11/11, reference 11/11. They cover session-ID SQL construction, one result fetch,
return behavior, and propagation of query/fetch errors. These probes do not
import the full repository or test Ctrl+C dispatch or live Snowflake queries.

Source supervision review does not reject a static check merely for being
static: the source script labels database behavior as expected, while its
actual checks inspect source text. Its orphan-query explanation is an issue
report, not a verified universal database rule. Native publisher controls,
trajectory replay, rights review and token audit remain pending. See
`dbtsnowflake716-v2-review-001` and `dbtsnowflake716-v2-semantic-001`.
The candidate is not added to Corpus 009 and remains unapproved for training.

### dbt–Snowflake 716: native replay and mechanical assessment completed

The digest-pinned original image and independently verified source snapshot both
produce the expected 38-node publisher result: base 37/38, reference 38/38.
The submitted native candidate passes 38/38 with no reference disagreements.
The snapshot preserves 152 tracked files, has one parentless commit, and makes
the prior base, PR head and merge commits inaccessible in its mounted filesystem.
Inherited image layers have not been audited for recoverable history.

Native replay 001 retains fresh observations for 18 charged calls plus submission.
Its `diff` command returns the expected exit 1 for a changed file; the native
CommandError and difference output remain intact in the history. The initial
`find /testbed` returns no results because that path is a workspace alias; later
direct file reads succeed. Neither observation was replaced with source output.
Reviewed cleanup removes the source-created backup and patch export before
native submission. Submitted and intended patch bytes match, and container
cleanup is confirmed.

History 001 has 40 messages / 19 exchanges. Token audit 001 exports 12,307 input
tokens and 4,125 supervised tokens without truncation. Mechanical assessment
001 passes; it does not approve training. Complete observation/dependency rights,
final split isolation and corpus admission remain pending. No live Snowflake
service or GPU/model execution occurred. Corpus 009 remains unchanged.

### Corpus 010 integration supersedes the six-example current assembly

The new quarantine assembly adds dbt–Snowflake and contains seven examples,
115,534 input tokens and 39,154 supervised tokens. All four admission gates
remain null. Publication 011 and restore 010 verify 15 files / 1,280,267 bytes;
restored inspection validates all records. Original schedule 011 and restored
schedule 009 are byte-identical: seven whole-example updates, one epoch,
seed 7401, 8,192 supervised-token update ceiling and zero target overshoot.
Training denial 009 rejects this exact real corpus. Nineteen focused corpus
and scheduling tests pass. Lineage review 005 finds no known repository-ID or
fork-network overlap with the four reserved projects; broader isolation remains
unproven. Earlier Corpus 009 statements above are historical results.

### PennyLane 5831 controls and publisher parameter selection

The next candidate preserves `Exp.num_steps` during simplification. The pinned
original environment collects 345 whole-file cases, of which 176 skip; that run
is retained and fails strict qualification. Directly selecting all publisher
keys also fails because six parameter labels were truncated at whitespace in
the publisher metadata.

The qualifier now widens an incomplete parameter identity to the whole test
function and deduplicates overlapping selectors. This only controls execution;
the existing comparison still demands exact publisher-group coverage, all
phases, no skips and correct transitions. A regression test confirms that an
extra, unlisted parameter rejects. The previous qualifier bytes are archived in
`artifacts/official/qualifier-before-truncated-publisher-001` for historical
receipt verification. No old receipt was rebound to changed producer code.

Controls 003 execute all 169 required publisher cases: base 168/169, reference
169/169. Additional actual-repository numerical probes compare explicit 4x4
Pauli-generator exponentials against SciPy, checking step counts and repeated
simplification with absolute tolerance 1e-12. Base passes 8/24; reference and
source candidate pass 24/24. NumPy-only probes do not certify optional backends,
differentiation or arbitrary operators. Native trajectory replay remains pending.

Source review also identifies errors in the dataset's added interface paragraph
(an extra imaginary factor and incorrect `num_steps=None` semantics). The
existing history builder conditions on the original task problem statement,
excluding that paragraph; inspect the actual generated history before assembly.
No candidate has been added to Corpus 010 in this cycle. Twenty-one focused
tests pass; full discovery completes 380 tests: 347 passed, 33 skipped.

### PennyLane 5831 native qualification

The source snapshot preserves all 1,366 tracked files and has one parentless
commit. Independent verification finds the old base, PR head and merge commits
inaccessible and known oracle paths absent in the mounted filesystem. Inherited
image layers are outside that verification scope.

Native replay 001 completes 30 charged calls plus submission. Two original
trajectory mistakes remain as actual failed observations: source index 18 calls
a NumPy matrix as a function, and index 32 specifies an incorrect pytest class.
Subsequent corrections and final checks succeed. Cleanup removes only the six
reviewed scratch files; submitted and intended patch bytes match.

Native grade 001 covers all 169 publisher cases: base 168/169, reference and
candidate 169/169. Mechanical assessment 001 passes without approving training.
History 001 has 64 messages / 31 exchanges; token audit 001 exports 17,691 input
tokens and 6,993 supervised tokens without truncation. Conditioning review 001
verifies that the original issue is preserved and the inaccurate added-interface
paragraph is absent from the actual generated user prompt.

Whole-file optional-backend skips remain unresolved; these results do not
certify all PennyLane backends. Rights, final split review and corpus integration
remain pending. Corpus 010 is unchanged and no GPU was used.

### Corpus 011: eight tasks across seven repositories

Selection 010 and assembly 011 add the qualified PennyLane 5831 token history to
quarantine: 133,225 input tokens / 46,147 supervised tokens. Both PennyLane tasks
remain in the same `train` repository group; this is not an eighth independent
repository. Four admission gates remain null, and denial 010 confirms training
is rejected for the actual new bundle.

Publication 012 and restore 011 verify 17 files / 1,479,218 bytes. Restored
inspection 011 validates all eight records. Schedule 012 and restored schedule
010 are byte-identical: seed 7401, one epoch, eight updates, an 8,192-token
supervised-update ceiling, and zero overshoot of the 46,147-token target.

Composition report 001 computes exact rational repository token shares. The
two PennyLane tasks account for 30.62% of supervised tokens. Inverse squared-share
concentration is approximately 5.604 repository equivalents out of seven; this
describes token concentration, not statistical independence or effective sample
size. Prioritize additional projects rather than treating same-project examples
as independent evidence. Corpus 011 remains far short of the 3×50M plan.

### PySyft 250: operational checks pass; documentation defects hold the trace

The hash-verified V2 task and digest-pinned Python 3.7 image reproduce publisher
controls: base 128/132, reference 132/132. Twenty additional actual-repository
cases cover integer, float, nonfinite, scalar, complex, empty and broadcast
equality, copy/in-place behavior, failed broadcasts and encrypted-left-operand
short-circuiting. Scalar comparisons provide the expected values. Base passes
0/20; reference and source candidate pass 20/20. This does not prove arbitrary
tensor behavior or encrypted computation correctness.

However, Python doctest executes seven examples in the candidate's added method
docstrings and finds two failures. `eq` shows `TensorBase([...])` instead of the
actual `BaseTensor: array([...])`. The `eq_` example expects no display although
the method returns the tensor. The source verification checks documentation
presence and keywords, so it does not catch these incorrect examples.

Review 001 holds this unchanged trajectory out of positive corpus selection.
The executable equality code is not invalidated by these documentation defects.
A corrected, explicitly new trajectory can be qualified later; do not silently
rewrite historical supervision. Snapshot build 001 completed, but independent
snapshot verification and native replay were not performed after discovering
the defect. Corpus 011 remains unchanged; no GPU was used.

### PySyft 250: verified documentation correction, not a new trajectory

Correction 001 is a separately labeled assistant-authored derivative. It changes
the `eq` example's displayed result to the actual representation and assigns
the `eq_` return to `_` so that the example correctly expects no display.
The original candidate and all original observations remain untouched.

The executable AST, excluding documentation strings, is identical before and
after correction. Actual pinned-runtime checks pass 132/132 publisher cases,
20/20 operational cases and 7/7 doctest examples. The correction report binds
the source inputs, derived patch and exact documentation-only difference.
This verifies a patch artifact; it is not a model-generated trajectory or
training-admission receipt.

To recover this task as training material, record an explicit new correction
trajectory with fresh native observations of the failing examples, the edit
and the successful rerun. Preserve the source trace's identity and label new
commands as assistant-authored extensions. Verify the final submitted patch,
reconstruct the extended history, audit tokens and retain all admission gates.
Do not relabel historical source messages or invent intermediate observations.
Corpus 011 remains unchanged pending that work.

### Explicit correction replay support and PySyft fresh history

The replay path now accepts an optional reviewed correction plan with separate
source/corrected patch identities, assistant authorship, rationale, exact commands
and expected process exits. Native command failures must match their explicit
exit codes; timeout/infrastructure errors cannot substitute. History projection
maps correction indices and authorship separately, preserves fresh failure
observations and rejects undeclared or misattributed actions. Assessment verifies
the correction provenance and adds a distinct supervision-review gate.

Previous implementations are retained under
`artifacts/official/before-correction-replay-001`. Original traces and receipts
are not rewritten. Four new tests cover plan/schema rejection, actual-exit
requirements, patch-provenance mismatches and history attribution. Fifteen focused
tests pass; final full discovery completes 384 tests: 351 passed, 33 skipped.

PySyft corrected replay 001 reached cleanup but was rejected because a manually
formatted diff differed from canonical Git output. The failed attempt remains
intact. Profile 002 binds a canonical diff generated from the verified correction.
Replay 002 completes 34 charged calls plus submission, with four explicit
correction commands: failing doctests, the edit, successful doctests and patch
export. Cleanup is confirmed and submitted bytes equal the corrected export,
explicitly not the original teacher export. Native grade passes 132/132 cases.

Corrected history 001 has 72 messages / 35 exchanges and passes mechanical
assessment with 22,706 input / 8,218 supervised tokens. The context plus reserve
fits, but the example exceeds the current 8,192 supervised-token update cap by
26 tokens. Budget review 001 records this without truncation or silently raising
the cap. Correction-supervision review, budget/runtime qualification and all
ordinary admission gates remain pending. Corpus 011 is unchanged; no GPU was used.

## Corpus 012: preserved correction history and restored schedule

The current assembly contains nine examples across eight repository groups,
155,931 input tokens and 54,365 supervised targets. The added PySyft trajectory
preserves the observed doctest failure and explicitly assistant-authored correction;
the unchanged original trace remains excluded. Mechanical replay is not evidence
of a trained model producing this fix. All admission gates remain unresolved.

The inspection update cap is now 9,216 supervised targets, explicitly replacing
8,192 for this plan because the complete correction example has 8,218 targets.
This changes example grouping and optimizer-update frequency; it is not claimed
equivalent to the earlier schedule or validated GPU capacity. With seed 7,401,
one epoch consumes all 54,365 targets in eight planned updates with zero overshoot.
No tokens were truncated to meet the earlier cap.

R2 publish and independent restore verified 19 files totaling 1,731,152 bytes.
Restored corpus inspection passed, and both schedule and update files are byte
identical to the original 9,216-cap plan. Training-purpose loading still rejects
the quarantine corpus. Repository identity/fork screening found no overlap with
the four reserved projects; detached copies and semantic overlap remain unexcluded.

Evidence: [assembly](../evidence/data/training-corpus-assembly-012/receipt.json),
[selection rationale](../evidence/data/training-corpus-selection-011/rationale.json),
[restore](../evidence/data/training-corpus-restore-012/receipt.json),
[schedule comparison](../evidence/data/training-corpus-restored-schedule-011/comparison.json),
[training denial](../evidence/data/training-corpus-denial-011/report.json), and
[lineage screen](../evidence/data/current-corpus-lineage-006/report.json).

This small qualification corpus does not supply the planned 3×50M campaigns.
Continue diverse task acquisition, attribution and split review locally; keep
the Pod stopped until a bounded GPU qualification bundle is ready.

## Explicit-input qualification batch planning

The batch planner now requires the corpus path and expected manifest SHA-256,
source screen, census and evaluation metadata as explicit inputs. Seed and
per-stratum sample size are configurable. It automatically adds current corpus
repository groups and reserved evaluation repository names to exclusions.
Source/census integrity, deterministic selection and input-drift checks remain.
The prior implementation is preserved under
`artifacts/official/qualification-planner-before-explicit-inputs-001`.

`evidence/data/qualification-batch-current-001` records a 32-repository batch
against Corpus 012 from 2,621 screened traces, 1,575 tasks and 902 repositories.
Three sampling tests pass; a live negative check rejects an incorrect corpus
manifest hash without creating output. Selected repository names are distinct
and do not overlap explicit exclusions. These are exact-name checks only.
Before new replay, reconcile this batch with historical task reviews and canonical
repository aliases; selection alone does not establish that every task is new.

The optimistic one-trace-per-task ceiling is 38,705,625 supervised targets
before masks, quality rejection and admission review. It is not acquired usable
training supply. No new example is admitted and no GPU work is started.

## Batch reconciliation and new repository coverage

Exact trajectory reconciliation found all 32 entries in current-batch-001 were
already in qualification-batch-001. They are not new data. The planner now
accepts repeatable `--previous-batch` files, binds their hashes, and excludes
their repository names before stratification. Current-batch-002 contains
32 distinct repositories with zero case-normalized name overlap with batch001.
All 32 issue descriptions were extracted from identity-checked pinned shards.
Three deterministic sampling tests still pass. No task has been accepted.

The new live lineage check resolved five of 36 requested source/reserved names;
31 returned HTTP 403. Its identity screen is incomplete and cannot support
admission. Do not interpret this as evidence of repository independence or
retry the entire batch blindly. Local issue/patch review can continue meanwhile.

Next review priority: statsmodels-8339 (penalized autocorrelation lag selection),
numkit-8 (smoothing boundary indices) and emcee-295 (compatibility axis order).
These are issue-only priorities, not verified fixes or mathematical claims.
Inspect pinned source, reference tests and teacher actions before defining
independent boundary/property tests or spending runtime resources.

Evidence: `qualification-batch-reconciliation-001`,
`qualification-batch-current-002/issue-extraction.json`, and
`qualification-batch-current-lineage-002/report.json`. Pod remains stopped.

## Statsmodels 8339: reference defect and teacher distinction

Pinned source and evaluator patches were extracted and retained. The reference
patch uses `max(1, np.argmax(scores))` for scores indexed by lags 1 through
n-1; this omits the index-to-lag +1 conversion. An isolated execution of its
actual patched auto-lag block disagrees with rational score maximization in
322 of 1,452 cases (all nonconstant ternary length-six series, both statistics).
For [-1,-1,-1,0,0,-1], Ljung-Box penalized scores have their maximum at lag 2
(-33/20), while the reference selects lag 1 (-26/15). The test patch only
requires a positive lag count and leaves exact lag validation as a TODO.

The extracted teacher edit instead initializes the original helper with lag 1
and negative infinity. Its actual helper agrees with all 1,452 rational-score
cases, versus 1,138 disagreements for the base helper. These are constructed
algorithm probes of the 2p penalty branch, not full-package tests, mathematical
proof over all inputs, or validation of the teacher's recorded test claims.
The pinned full source also includes lag zero in its threshold metric; broader
theoretical conformity needs a separate source/paper audit before any such claim.

Hold the reference as a correctness oracle; retain the teacher for independent
runtime and supervision review. No corpus admission or GPU use. Evidence:
`statsmodels8339-{task,evaluator,source,math,teacher-math}-001` and
`statsmodels8339-teacher-002`. Probe sources are retained alongside results.

## Statsmodels full-package runtime corroboration and control mismatch

The pinned local evaluator image downloaded successfully; its /testbed checkout
matched the exact base commit and source bytes. Actual package calls reproduce
the mathematical probe results on all 1,452 cases: base raises 1,138 errors;
reference returns 322 wrong lags; teacher has neither errors nor wrong lags.
NumPy is 1.24.4. This is direct runtime evidence, not agent replay or training.

With publisher test additions applied, all 131 diagnostic-file tests pass in
all three roles, including all setup/call/teardown phases and unchanged tracked
source during tests. The publisher-declared failing white-noise case already
passes on the base. Therefore benchmark-control qualification is held; do not
write a passing baseline receipt or call these tests discriminating evidence.
The independent cases remain useful but do not silently override this mismatch.

Teacher verification also includes a universal p>0.05 expectation for a random
white-noise sample and catches failures without failing process exits. Audit
actual observations before any native history can be admitted. Disposable
containers were removed. Evidence: `statsmodels8339-runtime-math-001`,
`statsmodels8339-controls-001`, and retained runtime-source-001 scripts.
The earlier import hydration wait completed; no duplicate run or Pod start.

## Statsmodels random-state diagnosis and explicit control configuration

The pinned fixture resets NumPy's global state to seed 1. A paired direct-call
sweep (seeds 0..31, normal and uniform length-1000 inputs) produced 49 base
errors and zero candidate errors, with identical input hashes across roles.
Two candidate samples have first-lag p-values below 0.05; the teacher's universal
white-noise p-value expectation is invalid. These fixed-cohort counts are not
population failure-rate estimates.

Repeating the full diagnostic file with the explicit pytest option
`-p no:randomly` restored the publisher distinction: base 130/131, reference
131/131, candidate 131/131. The base fails exactly the declared white-noise
FAIL_TO_PASS node; all other setup/call/teardown outcomes meet expectations.
This intervention identifies pytest-randomly interaction as the cause of the
observed default-plugin mismatch. Preserve both configurations and require the
explicit override for this task's qualification. No default-runtime parity claim.
The separate reference lag-index defect remains and blocks its use as an
unqualified correctness oracle. Native history and supervision review remain.

Evidence: `statsmodels8339-randomstate-001/comparison.json` and
`statsmodels8339-controls-002/comparison.json`; scripts and prior runs retained.
No training admission, learned-performance claim or Pod start.

## Statsmodels native replay preparation

Source-action preflight passed: 18 shell calls, eight views, three creates and
one source replacement; two reasoning entries are excluded from execution and
one finish becomes submission. The three scratch verification scripts require
explicit reconciliation before submission. Actual failure observations and
unsupported blanket claims require review, not silent removal.

GitHub API PR metadata still returns 403. Public Git ref resolution succeeded:
refs/pull/8339/head advertises 0dd88024badd563190f8000f06ec003506215df2. This is
a PR head, not an asserted merge commit. The snapshot build uses this identity
and checks its local relationship to the pinned base. Build and independent
verification must finish before native replay. Evidence:
`statsmodels8339-snapshot-resolution-002` and `statsmodels8339-replay-preflight-001`.
No native replay, data admission or Pod restart has occurred in this step.

## Snapshot verification and exact blob-hash optimization

Statsmodels snapshot build001 and independent verify001 completed: 2,131
tracked files match the original manifest, one parentless commit remains,
base/PR-head commits are inaccessible and declared oracle paths are absent.
This covers the mounted filesystem, not inherited Docker layer bytes.

Future snapshot verification now computes Git SHA-1 blob identities directly
from `blob <byte length>\0` followed by the original bytes, rejecting non-40-hex
index identities under the existing SHA-1 snapshot contract. Symlinks use link
text. This removes one Git process per file without dropping byte/mode checks.
Eight focused tests pass, including independent `git hash-object` comparisons
for binary, empty, Unicode/CRLF, executable and symlink content and rejection
of modified content. The previous implementation is retained in
`artifacts/official/source-snapshot-before-local-blob-hash-001`.

On the actual 2,131-file statsmodels snapshot, the new verifier produced the
identical full tracked manifest hash as the old Git-backed implementation.
Observed verification time was about 0.254 seconds in one run, not a general
performance guarantee. Evidence: `snapshot-blob-hash-runtime-001`. The full
regression run remains pending local test-file hydration; no all-suite pass
is claimed. Native replay and training admission remain pending; Pod stopped.

## Snapshot optimization regression complete

The pending full local suite completed: 385 tests, 352 passed, 33 skipped,
zero failures. Evidence: `evidence/p1/snapshot-blob-hash-regression-001`.
Skipped coverage and GPU behavior remain unqualified. Statsmodels native replay
attempt001 stopped before execution on shard-hydration metadata drift; after
confirmed termination, attempt002 started against the verified source snapshot.

## Statsmodels native replay result and hold

Attempt002 completed with 30 charged tool calls plus native submission, fresh
observations and confirmed container removal. The original error appears in
pre-edit stdout despite exit zero; after the repair the same reproduction
succeeds. The actual diagnostic run reports 130 passed (original tests, without
publisher additions). Reconstructed history has 64 messages and 31 exchanges.

Pinned tokenizer measurement: 17,227 input and 4,057 supervised tokens; adding
8,192 output reserve gives 25,419, within 32,768. No tokens were exported for
training. Submitted patch includes final_verification.py and reproduce_issue.py
as well as the intended diagnostic.py edit. Hold this attempt pending explicit
scratch reconciliation and supervision correction; do not silently strip files
or relabel the attempt as accepted. See `statsmodels8339-native-review-001`.

## Explicit pre-submission completion support

The SWE-Hero replay path accepts an optional assistant-authored completion plan
bound to the exact adapted source actions and expected final patch. One to
eight declared commands run before the original terminal submission. Every
native outcome is retained, including an explicitly expected nonzero process
exit; infrastructure errors do not count as that expected failure. Source and
completion actions remain separately attributed in reconstructed history.
Plan, source-action and final patch mismatches reject; tool budgets still apply.
Original traces and earlier replay artifacts are unchanged.

Four focused tests exercise authorship, ordering, altered commands, failure
provenance and terminal validation. Full local suite: 389 tests, 356 passed,
33 skipped. Evidence: `evidence/p1/replay-completion-regression-001`.
Previous scripts are preserved under
`artifacts/official/source-replay-before-completion-001`.

Statsmodels completion-plan-001 declares an expected failing p-value assertion,
a correction plus independent lag check, and hash-verified scratch cleanup.
Native attempt003 is the integration test; do not infer success from unit tests
or plan preparation. Training approval remains false and the Pod stays stopped.

## Statsmodels corrected native replay and completion integration

Attempt003 completed with 33 charged calls plus native submission and confirmed
container removal. Three separately attributed completion actions preserve the
observed p-value counterexample (native CommandError exit1), correct the
verification assumption, check the independent lag case, and remove three
hash-verified scratch scripts. Final native patch matches the declared hash
and modifies only diagnostic.py. Applying it and the control candidate to the
same pinned source produces identical bytes; prior 131-test controls apply to
that exact source change, not to an invented new test run.

Reconstructed history: 70 messages, 34 exchanges; all three added actions have
null original source indices and explicit adapter authorship. Complete native
tokenization yields 19,994 input / 6,446 supervised tokens, 28,186 including the
8,192 output reserve. Token arrays were exported as an unapproved candidate.
Source failures and corrective observations are retained. No Gemma model ran.

Evidence: native-replay-003, native-history-003, native-tokens-002 and
native-alignment-001 under the statsmodels8339 prefix. Next: task-level review,
canonical repository isolation, rights/observation attribution and corpus
integration. The reference's lag-index defect remains documented; no general
mathematical correctness or training readiness is claimed. Pod remains stopped.

## Corpus 013: corrected statsmodels quarantine integration

Ten examples across nine repository groups now total 175,925 input tokens and
60,811 supervised targets. The corrected statsmodels history has a distinct
completion-plan-derived example ID; the earlier scratch-containing submission
remains excluded. All four training admission gates remain null. New repository
identity and observation/rights checks remain open; no lineage pass is invented.

R2 publish and independent restore verified 21 files, 1,957,026 bytes. Restored
inspection passed and schedule/update files are byte-identical. Seed7401, one
epoch and cap9216 yield nine planned updates with zero target overshoot. This
is an inspection plan only. Training-purpose load rejects the new manifest.

Evidence: selection012, assembly013, publish014, restore013, restored-inspection013,
schedule014, restored-schedule012 and denial012 under their training-corpus
prefixes. P1 remains incomplete: this small qualification corpus does not
supply three 50M-token campaigns. Next local work should expand repository/task
coverage and close attribution and isolation gaps, without repeating the current
small corpus and describing that as additional unique data. Pod remains stopped.

## Numkit 8 mathematical/source screening

Selected exact teacher trace 9157adb5-0648-4a1d-8ab6-c58fdc6394d2 from the
new repository batch. Pinned source, evaluator patches, teacher actions and
LICENSE were captured; old COPYING and alternative notice URLs returned 404.
The teacher smooth function AST equals the reference's smooth function AST.
Reference changes elsewhere are not asserted equivalent.

An independent scalar convolution calculation matched the extracted teacher
function in 1,620 constructed cases: lengths3..20, supported odd window sizes,
six window types including asymmetric custom weights, and ramp/constant/
oscillatory inputs. Base raises TypeError on all those cases under Python3.
Even-window rejection and unit-window identity were checked. This is isolated
function execution, not full-package qualification or native replay.

For odd w>=3, n>=w: padded length n+2(w-1), valid convolution length n+w-1,
then trimming w-1 entries yields n. Nonfinite/zero-sum weights and Python2
behavior are outside this check. Next: pinned runtime controls and source
observation review. Evidence: numkit8-{source002,evaluator002,teacher002,math001,
review001} directories (hyphens retained in actual filenames). Corpus remains
013, training unapproved, Pod stopped.

### Numkit pinned runtime controls

The first control attempts did not execute tests: the publisher image had the
wrong checkout, and neither Conda interpreter imported the source package.
Those failures are retained. The normalized, isolated snapshot preserves all
39 tracked files. A derived image explicitly binds `/testbed/src` into the
existing Python 3.6 environment using a `.pth` file; it downloads no packages.
The installed versions are NumPy 1.19.2, SciPy 1.5.2 and pytest 7.0.1.

The repaired image reproduces exactly the publisher's five smoothing failures
on the original code and 48 passes. Reference and teacher fixes each pass all
53 cases. Every setup, call and teardown result, collection membership,
unchanged tracked source and container cleanup is checked by
`numkit8-runtime-source-001/assess_controls.py`; the bound report is
`evidence/data/numkit8-runtime-assessment-001/report.json`.
Isolation was reverified after the import repair: one parentless commit,
matching tracked manifest, old commits inaccessible, declared oracle paths
absent. This checks the mounted filesystem, not inherited image layers.

These results qualify this test file only. Native action replay, observation
quality, rights and final corpus admission remain separate requirements.
Corpus 013 remains unchanged and unapproved for training. No Runpod compute
was used for these controls.

Numkit native replay subsequently completed 28 charged actions plus submission
(29 exchanges), removing its own three scratch scripts. The submitted patch
changes only the slice division and produces exactly the source bytes tested
above. History projection preserves fresh observations and four command
failures, including full-suite collection failure from the missing
`scipy.integrate.quadrature` module. A NumPy binary-compatibility warning also
remains visible. Neither is treated as a passing full-suite result.
The reconstructed history tokenizes to 17,967 input and 3,973 supervised tokens;
with an 8,192-token output reserve, the total is 26,159, below 32,768.
Evidence: `numkit8-native-{replay,history,tokens,assessment}-001`.
This candidate is not added to Corpus 013 pending observation and attribution
review. Native teacher replay demonstrates tool execution, not Gemma ability.


## Corpus 014: Numkit numerical-verification integration

Eleven examples across ten repository groups total 195,042 input tokens and
65,769 supervised targets. The Numkit example uses a completion-plan-derived ID
and explicitly attributes one added numerical verification command to the
assistant. The earlier original-only replay remains archived, not duplicated
in this assembly. Native numerical verification matched an independent scalar
convolution oracle in 1,620 cases, with maximum absolute error
7.105427357601002e-15; zero-output and reversed-custom-weight mutations were
rejected in 1,620 and 180 cases respectively. This is bounded numerical evidence,
not a universal proof. Full-suite collection failure, compatibility warnings
and original command failures remain in the observations.

R2 publish and independent restore verified 23 files / 2,169,563 bytes. Restored
corpus validation passed. With seed 7401, one epoch and a 9,216 supervised-token
update cap, the inspection schedule has ten updates and zero token overshoot.
Original and restored schedule/update files match byte for byte. No optimizer
steps occurred; training-purpose loading correctly rejects the quarantine
manifest. All four admission gates remain null. Repository identity and rights
review remain open, including the newly added Numkit group.

Evidence: selection013, assembly014, publish015, restore014,
restored-inspection014, schedule015, restored-schedule013 and denial013, under
the training-corpus evidence prefixes. Numerical evidence and content review:
numkit8-native-replay-002, numkit8-native-history-002, numkit8-native-tokens-002,
and numkit8-observation-review-001. Corpus manifest SHA256:
`ccca52a2abb0b9bf856390dc33349357e2d2b95b1eb3396c14a513b6d78dd78d`.

Next: scale diverse task qualification and complete attribution and repository
isolation review. This small corpus still does not supply the planned 3×50M
campaigns. P1 remains incomplete and the Pod stays stopped.


## Explicit source timeout support and emcee runtime controls

The replay adapter now accepts an explicitly specified integer 30-second source
command timeout because it equals the native runner limit. The original timeout
is retained in the adapted action. Other limits, boolean/float/string values and
unknown argument fields reject. The same constant controls the recorded limit
and native context configuration. Fourteen focused tests pass; the full local
suite reports 391 tests, 358 passed and 33 skipped. The initial broad run had two
source-hydration inventory failures; those logs are retained, and no integrity
check was relaxed to obtain the subsequent passing run.

Emcee task 295 has a pinned 124-file source snapshot. Its original image lacked
h5py, silently omitting ten HDF backend tests. An explicitly recorded offline
addition of the hash-verified h5py 3.12.1 CPython 3.9 Linux wheel restores that
coverage while retaining NumPy 2.0.2. This is an environment repair, not a claim
of historical environment equivalence. Source isolation was reverified after
installation. All 21 publisher test transitions match: base 11 passes / 10
failures, reference and candidate 19 passes / 2 failures. Both persistent
failures are publisher-declared FAIL_TO_FAIL cases; they are not counted as
successful tests or silently omitted. Candidate and reference agree on every
case, including setup and teardown validation.

Evidence: `evidence/p1/explicit-source-timeout-regression-001`,
`evidence/data/emcee295-h5py-verify-001`,
`evidence/data/emcee295-controls-002`, and `qualification-triage-publish-002`.
Emcee native replay and observation review are still separate requirements.
Corpus 014 remains unchanged and quarantine-only. The Pod remains stopped.


The first completed emcee native replay executes 39 charged actions with the
explicit 30-second source timeout preserved. Its disposable container was
removed. The submitted patch still contains `reproduce_issue.py` alongside the
intended source fix; it is held and is not part of Corpus 014. Next work must
review the observations, verify numerical axis mapping inside the native
package, and remove only identity-verified scratch files through an explicitly
attributed completion. The initial pre-container attempt failed source-shard
hydration checks and its log is retained. Evidence: emcee295-native-replay-002
and emcee295-native-preflight-failure-001.

### Completed emcee replay and bounded observation review

The later `emcee295-native-replay-004` completes 40 charged actions and submission,
with container cleanup verified. Its 415-byte source-only patch produces exactly
the same source bytes as the candidate tested in controls-002. The separately
attributed completion checks 224 stored log-probability values across memory and
HDF5 storage, legacy/modern axis correspondence and flatten order, with observed
maximum absolute error zero. It removes four hash-verified scratch files.

`emcee295-native-history-003` reconstructs 84 messages and 41 exchanges.
`emcee295-tokens-001` measures **27,404 input / 5,675 supervised tokens**, without
truncation, using the pinned model tokenizer. This establishes context-cap fit,
not GPU-memory fit. `emcee295-observation-review-001` verifies patch alignment,
completion observations, history attribution and preserved error indices
16, 18, 62 and 72. Native test output is tool-truncated; no full-suite totals are
inferred from it. The independent publisher controls retain both FAIL_TO_FAIL
cases and verify all 21 cases (base 11 passes; reference and candidate 19).

This candidate is eligible for quarantine selection review only. It has **not**
been assembled into Corpus 014, which remains unchanged. Training approval,
repository identity, observation attribution and dependency notices remain open.
Finite checks do not establish MCMC convergence or universal correctness.
The new history, token audit and observation review still require R2 archival.


## Corpus 015: emcee completion integration

The current quarantine assembly contains 12 examples from 12 tasks and 11 declared
repository groups: **222,446 input / 71,444 supervised tokens**. The added emcee
history includes a separately attributed completion with actual memory/HDF5
sampler assertions and verified scratch cleanup. Its source patch yields the
same bytes as the independently tested candidate. Original failures remain in
the history; no full-suite pass or universal numerical guarantee is asserted.

Corpus manifest SHA-256:
`57e8f47b47f79dee03ed97980aa66c9c93a274f9894c0f36e1bc8e122ef22427`.
Content SHA-256:
`ba775fc6f5eed1ea729e104ab678c6d877faed16c6e8f8a538e5538371a98048`.

Publish-016 and restore-015 verify 25 files / 2,476,074 bytes. Inspection-015
validates the restored examples. Schedule-016 and restored-schedule-014 match
byte for byte: seed 7401, one epoch, 11 planned updates, 71,444 supervised tokens,
zero target overshoot, and a 9,216-supervised-token update cap. These are planned
exposures, not executed optimizer updates or new unique data. Denial-014 confirms
`Quarantine corpus cannot train`; all four admission gates remain null.

Evidence: `training-corpus-selection-014`, `training-corpus-assembly-015`,
`training-corpus-publish-016`, `training-corpus-restore-015`,
`training-corpus-inspection-015`, and `corpus015-integration-check-001` under
`evidence/data`. Earlier Corpus 014 entries above describe the previous assembly.

Next: finish archival of the runtime evidence, expand diverse qualified supply,
and resolve attribution, repository identity and admission. The corpus remains
far below the planned training scale. GPU memory fit and learned coding gains
remain unproven. Keep the Pod stopped during this local work.


## Optuna 3545: isolated runtime qualification

The digest-pinned source image matches base
`f00abac7d53bb29e53e7c8bd13e9b4be9e0f9d44`. Its original Git history exposes
19,230 commits. Snapshot verification preserves all 402 tracked files, leaves
one parentless commit, and confirms that the base and PR-head objects plus
listed oracle paths are inaccessible in the mounted filesystem. Inherited image
layers are not audited.

Paired controls execute the full GridSampler test file with the publisher test
patch: baseline 8/9 pass; reference and teacher candidate 9/9 pass, with zero
candidate/reference outcome disagreements. Import origin is the task checkout;
tests leave the tracked patch unchanged; all three containers are removed.
The teacher changes unsupported-value rejection into UserWarning and differs
from the reference in warning type-name formatting. The nine tests do not
establish universal semantic equivalence.

The static action audit accepts 27 source actions and holds source indices
14, 18, 26, 30 and 32: standalone find/grep forms outside the reviewed adapter.
No command is silently skipped or repaired. Native replay, token measurement,
observation review, admission and corpus integration remain pending. Corpus 015
is unchanged. Evidence prefixes: `optuna3545-base-probe-001`,
`optuna3545-snapshot-build-001`, `optuna3545-snapshot-verify-001`,
`optuna3545-controls-001`, and `optuna3545-action-audit-001`.

Next: implement and test faithful, bounded adaptation of these search forms,
then replay against the isolated runtime. The Pod remains stopped.


## Reviewed standalone searches and first Optuna native replay

The source adapter now supports bounded quoted grep phrases, BRE alternation
with context, recursive grep on a source file, find/name with a grep/head
pipeline, and find/name with grep execution. Only the captured repository path
changes; pattern bytes, quoting, options, pipes and escaped terminators remain
unchanged. Unknown forms continue to reject. This compatibility grammar is not
a general shell security boundary; replay remains offline and disposable.

Actual shell parity tests cover matching and nonmatching fixtures, exit codes,
stdout/stderr, timeout metadata and unsafe extensions/paths. The full regression
suite reports **394 tests: 361 passed, 33 skipped, zero failures**. Evidence:
`evidence/p1/source-search-regression-001`. The previous adapter is retained at
`artifacts/official/source-replay-before-search-001/scripts/replay_source_teacher.py`.

`optuna3545-native-replay-001` completes 29 charged calls plus submission and
verifies container cleanup. Its 809-byte source-only patch changes rejection to
UserWarning. The trace retains source errors at 32 (grep no match) and 46 (the
original test still expects ValueError). The independent publisher controls
already verify corrected expectations; do not call the native old test a pass.

`optuna3545-native-history-001` and `optuna3545-tokens-001` measure **18,723 input /
4,509 supervised tokens** without truncation. These are candidate tokens, not
Corpus 015 additions. Next: review source observations and add explicitly
attributed assertions where printed checks are insufficient, then verify patch
alignment and decide quarantine assembly. No training admission or GPU fit is
established; the Pod remains stopped.


## Corpus 016: Optuna completion integration

The current quarantine assembly contains **13 tasks across 12 declared repository
groups, 243,213 input tokens and 77,114 supervised tokens**. The Optuna history
uses a completion-derived identity and explicitly attributes the added assertions.
Its final patch remains byte-identical to the original native submission and
produces the independently tested candidate source. Errors 32 and 46 remain
visible; the obsolete ValueError test is not relabeled as passing.

Actual package checks verify 12 supported values without warnings and 8
unsupported values with UserWarning. An in-memory study visits all six members
of `{1,2} × {-1,0,1}` once and attains the independently enumerated minimum of
`x²+y² = 1`. This is finite exhaustive coverage of that grid, not a proof of
persistent storage, distributed optimization or arbitrary Python types.
Four source-created scratch files are verified absent. The completed history
contains 20,767 input and 5,670 supervised tokens, without truncation.

Corpus manifest SHA-256:
`480acac8206c6b68355799ba1bfef71e87f89f9c2fa642c2659a3298050f3709`.
Content SHA-256:
`17d76bdaaa3dbfb2f7da81e454bf10b445aea3a416a0770a4b77368351e41de0`.
Publish-017 and restore-016 verify **27 files / 2,705,581 bytes**. Inspection-016
validates the restored corpus. Schedule-017 and restored-schedule-015 are
byte-identical: seed 7401, one epoch, 12 planned updates, 77,114 supervised tokens,
zero overshoot and a 9,216-target update cap. No optimizer update was executed.
Denial-015 retains `Quarantine corpus cannot train`; all admission gates are null.

Evidence: `optuna3545-observation-review-001`, `optuna3545-native-replay-002`,
`optuna3545-native-history-002`, `optuna3545-tokens-002`,
`training-corpus-selection-015`, `training-corpus-assembly-016` and
`corpus016-integration-check-001`, under `evidence/data`.
Earlier Corpus 015 entries describe the previous assembly.

Next: expand diverse qualified supply and resolve identity, attribution,
dependency notices and admission. These 77,114 targets do not supply the planned
50M-token candidates. Full-model GPU readiness and learned coding gains remain
unproven. The Pod stays stopped.


## Next-cohort semantic screening: units, ordering and equality

Three explicit candidates from qualification-batch-current-002 were extracted
with pinned task/teacher lineage and evaluator-only patches. Base source files
and licenses were fetched at exact base commits. The executable screen is
`evidence/data/qualification-triage-source-002/review.py`; its result is
`qualification-triage-002/report.json`.

- **Climlab 188: hold original teacher.** Its edited longitude-selection branch
  treats the documented degree input as radians. Five of six concrete degree
  inputs disagree with conversion to radians; base and reference match all six.
  The composition test alone can pass under either unit convention and is not
  sufficient to protect the existing input contract. This is extracted-branch
  evidence, not full package/xarray execution.
- **Boltons 205: hold for numeric-type contract review.** Actual extracted keys
  show teacher and reference both correctly order 0.2/0.9/0.7; the baseline
  truncates them. The teacher preserves order between 2^53 and 2^53+1 while the
  reference float conversion collapses them, but the teacher raises TypeError
  for numeric string '2', accepted previously. Queue backend execution and an
  explicit accepted-type decision remain necessary.
- **CloudEvents 172: advance to isolated runtime review.** Eight actual-method
  cases agree between teacher/reference and reproduce baseline attribute errors.
  The minimal carrier deliberately does not exercise the real constructor or
  serialization. Static preflight accepts all 38 charged source actions; no
  shell form is held. The pinned image has 17 layers / 1,348,086,486 compressed
  bytes; layers have not been pulled or runtime-qualified in this screen.

These candidates are not additions to Corpus 016. No model performance is
measured and no admission gate is opened. Next: CloudEvents source isolation,
paired full-package controls and native observations; preserve both other
holds rather than infer correctness from passing narrow tests. Pod remains stopped.


## CloudEvents 172: verified squash-merge provenance and paired controls

The pinned image matches declared base
`f39b964209babfbcd6a17502b9873cd87df7e6f0` and initially exposes 143 commits.
The live PR-head object is absent. Initial snapshot-build-001 correctly rejected
its ancestry. Inspection found local squash merge
`ad111ae89ae0ec77f7ba98adaabe3ffcdc3a5325`; merge-verification-002 confirms its
single parent is the declared base and all three changed files exactly match
the publisher's reference plus test patches. The initial verification omitted
the changed test file and failed; both attempts remain retained.

Snapshot-build-002 / snapshot-verify-002 preserve all 71 tracked files, leave one
parentless commit, and confirm old base/solution objects and declared oracle
paths inaccessible. Scope is mounted filesystem only, not inherited image
layers. Image ID:
`sha256:49e414e9143d2ea496a4f23c8281eb9051c28975cbb78a9eaf7732168408b58a`.

Controls-001 execute all 26 publisher HTTP CloudEvent cases with exact full
parameter identities: baseline **18 pass / 8 fail**, reference and candidate
**26 pass**, no candidate/reference disagreements. Source import origin,
unchanged tracked patch after tests and cleanup of all three containers are
verified. This is the complete selected test file, not the full repository.

Native replay and observation review are the next gate; the source includes an
installer attempt that may fail in the offline runtime. Preserve its real
outcome. Corpus 016 is unchanged and all training admission remains closed.
Evidence resides under the `cloudevents172-` prefix in `evidence/data`.


### CloudEvents native replay and token audit

`cloudevents172-native-replay-001` completes 38 charged source calls and submits
one 470-byte source patch, SHA-256
`2b492863db15ee67aae93bb4a8db490d028ed91e32baf7523d4bbf2f9d240723`.
Container cleanup succeeds. Errors at source indices 16, 18 and 36 are retained,
including the failed offline Sanic installation and pre-fix reproduction.
No whole-repository test success is claimed.

`cloudevents172-native-history-003` and `cloudevents172-tokens-003` verify
**25,495 input / 6,339 supervised tokens** without truncation. Earlier history
and token attempts stopped on cloud-file hydration metadata changes; their logs
and partial outputs are retained. Integrity checks were not relaxed.

Next: content review of source assertions, patch-to-controls alignment and any
explicitly attributed completion needed before quarantine selection. This is not
a Corpus 016 addition or training approval. GPU/full-model readiness remains
unproven; the Pod remains stopped.


## Corpus 017: CloudEvents finite-relation completion integration

The current quarantine assembly contains **14 tasks across 13 declared repository
groups, 270,026 input tokens and 84,503 supervised tokens**. The CloudEvents
history explicitly attributes the added completion; the source-only patch is
unchanged and produces the independently tested candidate bytes. Source errors
16, 18 and 36 remain visible, including the failed offline installer.

The actual constructor creates 32 events with explicit IDs/timestamps across
both spec versions and a subclass without a comparison override. All 1,024
ordered pairs match independently assigned equivalence classes. Exhaustive
checking of 32,768 triples covers 512 true transitivity antecedents; 512 ordinary
non-event directional comparisons also pass. A foreign class override produces
asymmetric cross-type equality, explicitly refuting a universal symmetry claim.
The source's untested transitivity heading and nonexistent `__req__` terminology
are corrected in the separately attributed completion. These finite results do
not prove equality axioms for arbitrary payloads or overrides.

Completed history: **26,813 input / 7,389 supervised tokens**, no truncation,
39 charged calls plus submission, six scratch files verified absent.
Corpus manifest SHA-256:
`c56ec783fae55397de271abb64312ecc40513e2e586b4b51a1eb64f6baec9a36`.
Content SHA-256:
`495829aa7bdb97d64afdd994bac06d76978e7402e5e7fbd3201fce13d26de754`.
Publish-018 and restore-017 verify **29 files / 2,998,210 bytes**. Inspection-017
validates the restored corpus. Schedule-019 and restored-schedule-016 are
byte-identical: seed 7401, one epoch, 13 planned updates, 84,503 supervised tokens,
zero overshoot and a 9,216-target update cap. Failed schedule-018 is retained;
it stopped on source-file hydration metadata drift. No optimizer update ran.
Denial-016 preserves `Quarantine corpus cannot train`; all four gates remain null.

Evidence: `cloudevents172-observation-review-001`,
`cloudevents172-native-replay-002`, `cloudevents172-native-history-004`,
`cloudevents172-tokens-004`, `training-corpus-selection-016`,
`training-corpus-assembly-017`, and `corpus017-integration-check-001`.
Earlier Corpus 016 entries describe the previous assembly.

Next: expand diverse qualified supply and resolve identity, attribution,
dependency notices and admission. The corpus is still far below the planned
training scale; repeated exposure does not add unique evidence. Full-model GPU
readiness and learned coding gains remain unproven. Keep the Pod stopped.

### Corpus 017: current identity and tracked-notice evidence

The metadata-only lineage audit 007 resolves 15 source names and all four
reserved repository names. No cross-boundary repository-ID or declared
fork-network-root overlap was found. This screen does not establish historical
independence or exclude detached copies, vendoring or semantic duplication.
No reserved evaluation task bodies were read.

Workalendar's historical and current names share repository ID 14559169.
The historical `rochacbruno/dynaconf` URL resolves to
`rochacbruno/dynaconf-mirror`, ID 841020260, whereas `dynaconf/dynaconf` has ID
40736676. The `historical_aliases` field in identity-binding-001 means URL
resolution only. Provenance-review-001 makes this distinction explicit. Keep
both Dynaconf names in one conservative split family pending content and
historical-lineage review; distinct current IDs are not evidence of independent
training and evaluation material.

Captured and hash-verified eight tracked license files from five qualified
images: four Statsmodels notices and one each for Numkit, emcee, Optuna and
CloudEvents. The original texts and snapshot/runtime bindings are retained in
`corpus017-notice-capture-001` and the corresponding `*-tracked-notices-001`
directories. This basename-based capture does not cover every embedded notice,
dependency, observation, or teacher service term and does not approve training.
The review driver is `corpus017-provenance-source-001/verify.py`; it validates
receipt and notice hashes and records both repository identity comparisons.

Corpus 017 remains 14 quarantined examples, 13 declared repository groups and
84,503 supervised tokens; all admission gates remain unchanged. No model
training or new GPU validation ran. Expand qualified supply and complete rights,
split and observation review before GPU admission. The Pod remains stopped.

### Boltons 205: stateful exact-order review, still not admitted

Expanded the earlier lambda-only screen to execute the complete, inspected
`queueutils.py` source for the base, teacher and publisher-reference variants.
Both heap and sorted-list backends were checked against a separate dictionary
oracle: choose the greatest exact `Fraction` priority, breaking ties by the
oldest surviving insertion counter. Re-adding a task resets that counter.
The seed-7401 sequences cover add/update, remove (including missing tasks),
peek/pop, length, final draining and empty-queue defaults. These are deterministic
finite tests, not independent statistical samples or a universal proof.

For each variant/backend/type family, 250 traces start with two insertions,
then 40 mixed operations and a final drain. Teacher: 0 failing traces out of
1,500. Base: 245/250 float traces and 247/250 fraction traces fail per backend;
large integers pass. Reference: ordinary floats pass, but 207/250 large-integer
and 200/250 fraction traces fail per backend. Float conversion merges distinct
exact priorities (including adjacent integers beyond 2^53); the teacher avoids
that precision loss. Each failing trace stops at its first mismatch.

Numeric string `'2'` remains accepted by base/reference and rejected by teacher
with TypeError. That is a compatibility difference requiring an explicit task
contract decision, not evidence that either implementation is universally
correct. The source teacher's reproduction/edge-case scripts also contain
printed comparisons that are not assertions; native replay and completion
review remain necessary.

Evidence: `boltons205-stateful-source-001/verify.py` and
`boltons205-stateful-review-001/report.json`. Execution uses the standalone
module's optional-import fallbacks (built-in list), not the publisher image or
full package. No NaN, infinity or concurrency claim is made. This candidate
remains outside corpus 017; no admission gates or training totals changed.

### Source issue credential indicators

Added `zenithsync/source_credentials.py` and the bounded, hash-bound
`scripts/screen_issue_credentials.py` CLI. It scans issue text for selected
credential-shaped authorization literals, GitHub token prefixes, AWS access-key
IDs and private-key headers. Diagnostics contain rule names and Unicode
character positions, never matched values or issue snippets. It does not contact
credential providers, validate credentials, automatically redact trajectories,
or certify absence of secrets. Other credential formats and other text fields
remain outside this screen's coverage.

Screening the 32-row current qualification issue batch found one flagged row
(index 3, GIScience/openrouteservice-py issue 67), with two authorization-literal
occurrences. Hold that candidate pending content review and an explicitly
attributed sanitization decision; do not replay the pasted credential or use it
for network requests. Raw provenance remains quarantined. Evidence is
`qualification-credential-screen-001/report.json`; the corpus is unchanged.
Four focused tests cover formats, safe diagnostics, Unicode locations, short
placeholders and deterministic ordering. The first broader suite failed two
file-identity checks during macOS cloud hydration; its log is retained under
`evidence/p1/source-credential-regression-001/failed-hydration.log`.

Fresh rerun: 398 tests, 365 passed, 33 skipped, no failures. No integrity check
was weakened. GPU and skipped-environment claims remain unverified.


### Credential indicators enforced before native replay

Native teacher replay now scans the decoded source message tree before command
adaptation or container creation. It checks prompt/observation strings and nested
action arguments, including separate authorization header key/value fields.
Detected indicators reject with a value-free error. The gate does not rewrite
source trajectories and has no implicit bypass; a reviewed sanitized derivative
would require its own provenance. Only the documented pattern families are
covered. A pass is not absence-of-secrets certification or training admission.

Real 32-issue batch validation through the replay preflight rejects the one
previously flagged issue before any execution; 31 have no known indicators.
Nine focused credential/search tests pass. Full CPU suite: 400 tests, 367 passed,
33 skipped, no failures. Evidence is `evidence/p1/replay-credential-screen-001`.
The former replay helper is preserved under
`artifacts/official/source-replay-before-credential-screen-001`; historical native
receipts still refer to their original implementation. Future replay receipts
record the screening module hash. No new native task qualification or training
was performed; corpus 017 and all admission gates remain unchanged.

### Boltons 205: isolated runtime and native replay

Pinned the publisher image by registry digest and checked its declared source
base. Snapshot 001 preserves all 112 tracked files exactly, has one parentless
commit and no accessible original base/solution objects or declared oracle paths.
Verification concerns the mounted filesystem; inherited image layers are not
an oracle-removal guarantee. Both publisher queue tests fail on base and pass
on reference and candidate; all transitions match, and module origin is the
checked-out package. This remains a two-test publisher control, supplemented by
the separately scoped exact-order probes above.

Native replay 001 rejected an incorrect profile base (snapshot ID supplied where
original base provenance was required); its receipt and cleanup are preserved.
Profile 002 corrects that field without changing the snapshot or replay checks.
An earlier missing intake-path invocation is also retained. Native replay 002
completed 29 charged tool calls plus submission, zero tool-error events and
verified cleanup. Its 459-byte patch hashes to
`e841d054ff94365dc4958b0587a78b2cbfd6ce3d276ba6f9405bee83733a3266`.
Applying it and the evaluated candidate patch to the exact source produces
identical bytes. Three temporary source scripts are absent from the submitted
patch. No observation-level acceptance is inferred from successful commands.

Evidence: `boltons205-runtime-resolution-001`, `boltons205-snapshot-verify-001`,
`boltons205-controls-001`, `boltons205-native-002` and
`boltons205-native-alignment-001`. The candidate remains outside corpus 017
pending explicit numeric-string compatibility, observation and attribution
review. No GPU usage, model training or new full-suite claim is made.

### Boltons 205: explicit finite completion and token-ready held trace

Native replay 003 adds one assistant-authored, hash-bound verification command
before submission; its final patch remains unchanged. Actual package execution
checks every insertion permutation of three six-item priority families, on both
queue backends, with and without one update/removal: 8,640 cases pass against
exact rational ordering, including FIFO ties and empty defaults. Two custom-key
cases pass. Both backends explicitly reject numeric string `'2'`; the added
observation records this incompatibility and limits all correctness claims to
the enumerated finite cases. No universal or statistical generalization follows.

Review distinguishes the original two repository tests (which pass even before
the fix) from the two patched publisher tests (which fail on base). The printed
base reproduction exits zero while displaying the wrong ordering. Several source
scripts print comparisons without assertions. These statuses must not be used as
proof of semantic correctness. The added completion contains actual assertions,
records the compatibility counterexample, and confirms scratch files are absent.

History 002 preserves fresh tool observations and labels the added command as
assistant-authored. Token audit 001 exports 19,017 input / 5,708 supervised tokens,
without truncation. The first history invocation supplied a metadata-join receipt
instead of the task-shard receipt and was correctly rejected; its failure is
retained. The corrected invocation uses the evaluator's pinned task receipt.

Evidence: `boltons205-completion-source-001`, `boltons205-completion-plan-001`,
`boltons205-native-003`, `boltons205-observation-review-001`,
`boltons205-native-history-002`, and `boltons205-tokens-001`.
The trace remains held outside corpus 017 until task compatibility and rights
review are resolved. These 5,708 targets are not counted in the current corpus
or an approved training campaign. No GPU or training ran.

### Boltons 205: compatibility-restoring assistant derivative

Created an explicitly assistant-authored derivative of the teacher fix. Its
priority key first negates numeric values without float conversion, then falls
back to the prior integer conversion when negation raises TypeError. This
preserves exact finite numeric ordering and restores the observed numeric-string
and byte-string behavior. It does not promise equivalence for every custom Python
numeric protocol. The priority-key docstring now permits ordered numeric values.

Two assistant completion actions apply the exact hash-bound edit and verify the
actual package. Native replay 004 completes with 31 charged calls plus submission,
no tool-error events and verified cleanup. All 8,640 enumerated ordering cases,
32 finite compatibility/invalid-input cases and two custom-key cases pass.
Paired publisher controls remain base 0/2, reference 2/2, derivative 2/2, with
all expected transitions and no reference/candidate disagreements. The submitted
948-byte patch exactly matches the evaluated derivative and hashes to
`7669282674b6b49f02da01eb3fe5fec6ea8c80e6108daa3c7bd22a9b88867f48`.

History 003 separately attributes the two added actions. Token audit 002 exports
19,724 input / 6,366 supervised tokens without truncation. The earlier original
teacher trace and its known incompatibility remain immutable. Review 001 marks
the derivative eligible for quarantine assembly only; rights, split integration,
GPU fit and learned performance remain unresolved. Corpus 017 is unchanged until
explicit assembly, transfer and restore verification of this derivative.

Evidence: `boltons205-compat-source-001`, `boltons205-compat-plan-001`,
`boltons205-compat-controls-001`, `boltons205-native-004`,
`boltons205-compat-review-001`, `boltons205-native-history-003` and
`boltons205-tokens-002`. No shared training implementation changed in this step.


### Corpus 018: fifteen-task quarantine integration

Added only the explicitly attributed Boltons compatibility derivative. Current
assembly: **15 examples, 15 tasks, 14 repository groups, 289,750 input tokens and
90,869 supervised tokens**. Manifest SHA-256:
`3c26a771de1a2d2f5a5f98b75d5a3cb6d5adcadb426754f89a6ca3a98f7f4109`.
Content SHA-256:
`cda219ef9998fe0b138c6cbe4f86b843b1daaea24f420a1e5597d8c69c17f01d`.
All four admission gates remain null; training-purpose loading explicitly rejects
with `Quarantine corpus cannot train`.

Published and restored 31 files / 3,216,759 bytes through R2. Restored token and
content identities match. Original and restored schedule/update files are
byte-identical: seed 7401, one epoch, 14 planned updates, 9,216 target-token update
cap, 90,869 targets and zero overshoot. This is a schedule, not optimizer execution.
Lineage audit 008 resolves all 14 declared repository groups, two historical
names and four reserved names, with no cross-boundary ID/network-root overlap.
Detached copies, semantic duplication and hidden evaluation independence remain
unproven; the Dynaconf mirror distinction remains explicit. No evaluation bodies
were read. Evidence binding: `corpus018-integration-check-001/report.json`.

The 3x50M processed-target-token campaigns are still not supplied by an abundant,
approved corpus. No training or GPU use occurred. Continue diverse qualification,
attribution and split review; keep the Pod stopped.

## Diverse candidate triage 003

Extracted three additional candidates from the existing pinned, metadata-joined
cohort: OpenFreeEnergy/openfe issue 28, glotzerlab/signac issue 622 and
KyleJamesWalker/yamlsettings issue 36. Teacher actions and evaluator patches stay
separate. Fetches use each declared base commit. Source file fetches succeeded;
Signac's attempted `LICENSE` path returned 404, recorded without substituting a
license or claiming notice coverage. No task images or GPU were used this cycle.

Signac: executed the inspected standalone filter module for base, teacher and
reference. A typed JSON serialization comparison checks 292 finite array/nested
object round trips, with and without whitespace. Base matches 146, teacher 292,
reference 146. The reference indexes empty strings unsafely (IndexError) and
loses whitespace handling retained by the teacher. Both teacher and reference
reject a closed malformed array; unmatched opening brackets remain plain text.
The teacher retains the base's acceptance of JSON-shaped keys when another
branch wins, whereas the reference rejects them. This is a separate preexisting
key-validation issue, not evidence that the source teacher solves all parser
validation. Select Signac for actual runtime qualification; no training acceptance
or full CLI/database semantics claim follows from this standalone module check.

OpenFE: reconstructed the complete teacher class. It protects input and returned
dictionaries from mutation, but accepts inconsistent forward/reverse maps and
rejects the publisher test's molecule-based constructor signature. The issue's
AtoB/BtoA API and publisher's molecule API differ. Hold for contract review rather
than silently declaring the teacher and publisher patches equivalent or treating
the reference as a faithful reading of the issue. RDKit execution was not tested.

YAMLSettings: inspected the actual AST key-normalization expressions. The teacher
fixes hyphens and more punctuation, but maps `café` to `CAF_`, changing an existing
Unicode environment lookup retained by base/reference. Hold for normalization
contract review. Only the extracted key expression/helper ran; no package YAML
traversal or environment mutation was simulated as integration evidence.

Evidence: `qualification-triage-source-003/{extract,fetch,review}.py`,
`qualification-triage-003/report.json`, and each candidate's task, teacher,
evaluator and source directories. Corpus 018 remains unchanged at 15 examples
and 90,869 quarantined supervised tokens. No shared training code changed.

## Signac 622: pinned runtime and incomplete shell controls

Pinned and downloaded the publisher image. Resolution 001 records PR head and
merge metadata; resolution 002 selects the merge SHA because the pinned task
metadata explicitly declares `merge_commit`. The image probe confirms the
original declared base. Snapshot build/verification 001 preserves all 149 tracked
files, one parentless commit, no accessible original base/solution objects and
no declared oracle paths on the mounted filesystem. Inherited layer bytes are
not covered by this isolation statement.

macOS offloaded required files during the cycle. Two live processes were polled,
not restarted; explicit file-download requests restored availability and both
completed. A later control preflight failed on hydration-induced file metadata
drift and its log was preserved. Hash checks were not relaxed.

Full shell controls 001 used the intended pytest interpreter but shell children
selected another interpreter, producing missing-deprecation failures. Controls
002 explicitly prepends the task environment to PATH before executing the
unchanged probe. The actual find regression now fails on base and passes on
reference/teacher. Qualification still rejects: two publisher-expected
host-configuration tests skip with `pymongo is required for host configuration`;
the broader test file also contains an expected-failure test_index. No passing
comparison receipt was generated and no skipped result was relabeled passed.

Next: inspect the pinned package's dependency contract, repair missing PyMongo
support with recorded provenance if feasible, and rerun all publisher-expected
cases. Preserve wider-file skips/xfails as separate evidence. Source semantic
checks remain bounded and do not override missing runtime coverage.

Evidence: `signac622-runtime-resolution-00{1,2}`, `signac622-base-probe-001`,
`signac622-snapshot-verify-001`, `signac622-controls-00{1,2}`,
`signac622-controls-preflight-failure-001`, and
`signac622-control-diagnosis-001/report.json`. Corpus 018 is unchanged; no Runpod
compute or model training was used.


## Signac622 offline dependency repair and publisher controls

The dependency probe proved that PyMongo and its bundled BSON module were absent
from the test interpreter. The task metadata explicitly requests PyMongo; the
repository declares the optional database extra as `pymongo>=3.0`. Pinned PyMongo
3.12.3 was fetched from PyPI and checked against the published byte count and
SHA-256; wheel metadata and license text are retained. Installation used an offline
Docker build with no dependency resolution. This is a historical test environment
repair, not a production dependency recommendation.

The repaired image revalidated all 149 tracked source files, one reachable
parentless commit, inaccessible original base/merge objects, and absence of the
previously enumerated oracle files. Scope remains the mounted filesystem; inherited
image layers are not audited. The earlier diagnostic's `signac.contrib.host` import
failure was outside the repository import path and is not evidence of a missing
installed Signac package; paired controls verify the actual `/testbed` import.

Controls 003 explicitly select every one of the 36 publisher identities: base
35 pass / 1 fail; reference and teacher candidate each 36 pass / 0 fail. All
publisher transitions match, no required test is skipped, and tests leave tracked
source unchanged. The additional non-contract `test_index` expected failure remains
preserved in the full-file controls 002 and is not relabeled a pass. Shared control
validation was not relaxed. All three containers were removed successfully.

Evidence: `evidence/data/signac622-controls-003/comparison.json`,
`signac622-pymongo-wheel-001/receipt.json`, and
`signac622-pymongo-verify-001/verification.json`. Native trajectory replay,
observation review, semantic completion and token audit remain outstanding. This
candidate is not added to corpus 018 and has no training approval. Runpod remains
stopped; this cycle used only local compute.


## Signac622 native trajectory replay and search adapter extension

Two source search forms required a narrow compatibility extension: find piped to
quoted grep -E alternatives and find -exec grep with literal/escaped BRE branches.
Only the source-root path is replaced; original quoting and pattern bytes remain.
Real shell parity tests cover matching/nonmatching text; shell extensions,
substitution and unsafe paths remain rejected. The previous replay script is
preserved under artifacts/official/source-replay-before-signac-search-001.

The first preflight rejection and subsequent macOS hydration integrity failure
are preserved. Native replay 002 completed 36 charged calls plus submission;
container cleanup succeeded. Its 658-byte production patch matches the candidate
used in all 36 passing publisher controls. Two searches returned no matches and
the original full shell-test command exceeded its 30-second limit. None is
converted into a passing observation. Native replay is not new-model evaluation.

Full CPU regression: 400 tests, 367 passed, 33 skipped, no failures/errors on the
completed rerun. The first run's four file-hydration failures are retained; no
integrity check was relaxed. Evidence is in signac622-native-alignment-001 and
evidence/p1/signac-search-regression-001. Semantic completion, observation review,
history construction and token audit remain outstanding; corpus 018 is unchanged.
The GPU Pod remains stopped.


## Signac622 bounded semantic completion and native token audit

Completion 002 / native replay 005 passed 292 typed JSON round trips (73 arrays,
array versus nested-object values, with/without surrounding whitespace), seven
scalar cases, three operator cases, three malformed closed-JSON rejections, and
eight actual CLI subprocess selections over real temporary project jobs. Typed
comparison distinguishes bool from int. Assertions use independently constructed
values and job identities; printed success text is not the oracle. These are
finite coverage checks, not independent statistical observations or a general
correctness proof.

The original source reproduction contains a stale hard-coded string claim after
the actual result becomes a list; the contradiction is retained and identified.
The source final demo uses package APIs rather than a CLI subprocess. Unsupported
universal compatibility claims are explicitly rejected by the observation review.
Unclosed bracket text remains a string, JSON-shaped keys can bypass validation,
and lone arrays parse to lists rather than query mappings. Original search errors
and the 30-second shell-test timeout remain in the reconstructed observations.

The first completion failed because a subprocess launched in the temporary
project directory could not import the isolated checkout. Completion 002 sets
PYTHONPATH=/workspace explicitly; the original failed attempt and successful
container cleanup are retained. Separate preflight failures involved macOS
hydration of replay_completion.py, then the task parquet and protocol exchange
file during history binding. Each process exited before retry; no integrity
check was relaxed.

Native replay 005 completed 37 charged calls plus submission with the production
patch unchanged. History 001 has 78 messages / 38 exchanges. Token audit 001:
24,278 input tokens, 6,385 supervised tokens, no truncation, within the 32,768 cap.
Evidence: signac622-observation-review-001/report.json,
signac622-native-history-001/receipt.json, signac622-tokens-001/report.json.
Corpus 018 is unchanged; task acceptance, attribution and training admission are
still outstanding. No GPU was started and no model was trained.


## Corpus 019 integration and explicit incomplete lineage refresh

Selection 018 adds the Signac completion derivative to quarantine only. Assembly
019 verifies 16 examples/tasks across 15 declared repository groups, 314,028 input
and 97,254 supervised tokens. All four admission gates remain null; denial 018
confirms training-purpose loading rejects exactly `Quarantine corpus cannot train`.
The 33-file, 3,484,675-byte bundle was published (020), restored into an empty local
directory (019), and inspected (019). Original schedule 023 and restored schedule
018 match byte-for-byte: seed 7401, one epoch, 9,216 target-token cap, 16 updates,
97,254 target tokens and zero overshoot. Schedules 021/022 failed source inventory
on macOS hydration and are preserved; no optimizer ran.

Lineage refresh 009 includes 15 declared groups, two historical names and four
reserved names, but six metadata requests returned HTTP 403. It is incomplete and
not a passing split audit. Earlier audit 008 remains historical evidence only.
This does not block quarantine assembly but must be resolved before admission.
Integration check: evidence/data/corpus019-integration-check-001/report.json.
No full-model test, training gain, abundant-data claim or GPU restart is implied.


## Corpus 019 authenticated lineage recovery

Audit 010 used the existing authenticated GitHub CLI for public repository
metadata only. All 21 requested names resolved: 15 declared corpus groups, two
historical names and four reserved repositories. No cross-boundary repository ID
or declared fork-network-root overlap was found. The six HTTP 403 responses in
audit 009 remain preserved; corpus019 integration check 001 describes that earlier
state and is not rewritten. Detached copies, semantic duplication, historical
lineage and model-pretraining overlap remain unproven. No admission gate changes.


## Additional parser/serialization cohort triage 004

Pinned source/evaluator/teacher material was extracted for price-parser 43,
dict2xml 27 and jsons 86. Original source at each declared base and selected LICENSE
files returned HTTP 200. Conservative credential-indicator screening passed for
the extracted action lists; this is not a secret-free certification.

Price-parser: 12 source-function cases combine four whitespace forms (NBSP,
narrow NBSP, tab and doubled space) with three currency prefixes. Exact Decimal
amount checks: base 3/12, teacher 9/12, reference 12/12. Normalized amount_text:
base 0/12, teacher 0/12, reference 12/12. The initial review's assumption that the
teacher fixed every numeric case was contradicted by tab inputs; initial script
is retained. The revised review reports actual outcomes and holds the candidate;
no passing criterion was lowered for admission. This is AST-selected execution
of actual functions, not full-package publisher qualification.

Dict2xml: static source analysis finds that the wrapper forwards all options into
Converter, while the teacher only adds data_sorter to its constructor. Publisher
requirements also pass iterables_repeat_wrap and closed_tags_for, still absent
from the constructor. Hold pending corrected implementation and runtime controls.
Jsons variable-length tuple dispatch remains pending historical runtime review.
No corpus increment or training approval results from this triage. Corpus 019 and
the stopped GPU boundary remain unchanged.


## Jsons86 historical runtime and paired-control failure

Pinned registry digest bfe70ea2c78e2563ca2e41e3dc423adc5fd629ea4a56b70769993febe899b84d
and PR head e986c3350134a0943d75326b50a20ec42a4478ca (metadata selects head_commit).
Base probe confirms aa565f530b3e72c5854cf11b10b1d90daa85f047 with 571 reachable
commits before isolation. Snapshot verification confirms 112 tracked files,
one parentless commit, inaccessible base/head objects and enumerated oracle-file
absence. Mounted filesystem only; inherited layers are not audited.

All ten publisher tuple tests ran: base 8 pass / 2 fail, reference and teacher
9 pass / 1 fail. The new variable-length tuple test fails only in the base.
However test_load_namedtuple_with_types fails in all three with a datetime
DeserializationError, contradicting its required pass-to-pass transition.
Controls correctly reject qualification. Pytest logs identify Python3.9 while
publisher installation metadata requests Python3.7; this discrepancy is observed,
not yet proved to cause the failure. All control containers were removed.

Two preflight file-hydration failures were retained before the successful test
execution. No acceptance condition was removed. Next: isolate named-tuple failure
and historical dependency/interpreter requirements before replay admission.
Corpus019 remains unchanged and Runpod remains stopped.


## Jsons86 named-tuple runtime failure isolated

The required named-tuple test fails alone with pytest-randomly disabled, excluding
order dependence for this reproduction. Installed runtime: Python3.9.20,
typish1.9.3, pytest8.3.3. Source default_namedtuple_deserializer reads _field_types
to choose each field type; Python3.9 removed that NamedTuple attribute in favor
of __annotations__ (official documentation:
https://docs.python.org/3.13/library/typing.html#typing.NamedTuple).

Causal probe002 in fresh subprocesses: with untouched Python3.9 metadata, two
explicit datetime-string inputs deserialize correctly, while list/dict inputs
using the datetime default raise DeserializationError. Restoring only the test
class's historical _field_types metadata yields four correct results. The
initial diagnostic incorrectly expected all four untouched cases to fail; that
assertion failure and cleanup are preserved. The corrected diagnostic narrows
the causal claim to default-value handling, rather than changing acceptance.

This intervention is diagnostic only: no publisher test or production source is
changed, and it does not qualify the candidate. The next required step is an
actual Python3.7 environment with pinned dependencies, followed by unchanged
paired controls. Corpus019 remains unchanged; no training or GPU use occurred.


## Jsons86 actual Python3.7 runtime and passing publisher controls

Built a separate /opt/zenithsync-py37 environment with Python3.7.16 and pip22.3.1
on the isolated source image. Ten pinned Python wheels (including typish1.9.3 and
pytest7.4.4) were checked against PyPI size and SHA-256 and installed with
--no-index --no-deps. pip check passed. Exact conda package records, explicit
package URLs/checksums, pip freeze, wheel metadata and notices were retained.
This is an archived historical qualification environment, not a recommendation
for the product runtime. The environment solve used network access; test containers
remained offline.

Snapshot revalidation still matches 112 tracked files, one parentless commit,
inaccessible base/solution objects and enumerated oracle absence. All ten original
publisher cases ran without test edits or the diagnostic metadata intervention:
base 9 pass / 1 fail, reference 10/10, teacher 10/10. Every publisher transition
matches; source remains unchanged by tests and all containers were removed.
The legacy NamedTuple attribute is naturally present in Python3.7.16. This
corroborates the prior isolated metadata diagnosis; pytest also changed to a
Python3.7-compatible version, so the full-environment comparison alone is not a
single-variable experiment.

Evidence: jsons86-controls-002/comparison.json,
jsons86-py37-packages-001/runtime.json, jsons86-py37-verify-001/verification.json.
Native trajectory replay and independent semantic completion remain outstanding.
Corpus019 and all training-admission gates are unchanged; Runpod remains stopped.


## Jsons86 native replay and bounded public API screen

The replay runner now has a mutually exclusive --python37-testbed option. It
checks the actual interpreter path and exact Python3.7.16 version before replay.
All 15 focused replay-profile tests passed. Native replay002 completed 40 charged
tool calls plus submission; the container was removed. A source file view failed
because start line200 exceeded end line77, and that observation is retained.
Alignment002 verifies the production edit matches publisher-qualified controls,
but the submitted patch also contains reproduce_issue.py; completion must remove
that scratch addition with explicit provenance.

Semantic screen001 applies the actual native patch in an offline Python3.7
container and passes 126 public API cases: 72 variable-length cases across four
primitive types, nine lengths and two strict settings; 50 nested tuple cases;
two fixed tuple cases; two named-tuple default cases. Typed comparison separates
bool, int and float. These finite checks do not prove universal semantics,
parallel behavior, malformed-input handling or learned-model performance.

The first full regression run completed 401 tests with one failure, six errors
and 33 skips: four integrity failures during macOS hydration and three subprocess
timeouts. The failed log is preserved. After confirming old process handles and
OS processes were gone, a fresh source-hydration/read pass and full rerun were
started; at this checkpoint that process remains live and no passing full-suite
result is claimed. Do not restart it merely for observation latency.
Corpus019 remains unchanged. No GPU or training was started.


## Jsons86 completed replay and finalized Python3.7 runner regression

Completion001 binds exact source actions, verifies reproduce_issue.py bytes by
SHA-256 before removal, then executes all 126 semantic assertions. Native003
completed 42 charged calls plus submission; final1265-byte patch contains only
the production serializer edit. The original invalid view action remains in the
history. Container cleanup succeeded. History001: 88 messages /43 exchanges;
tokens001: 24,218 input /5,869 supervised, untruncated within32768 context.
Observation review explicitly distinguishes source print/catch demonstrations and
pytest-to-head pipelines from verified passing tests. No training approval.

The earlier source-hydration process eventually finished; its full regression
rerun had one subprocess timeout. After terminal confirmation, a final rerun with
PYTHONPYCACHEPREFIX=/tmp/zenithsync-python-cache inherited by subprocesses passed
401 tests:368 pass,33 skip,0fail/error in15.543s. Timeouts and assertions were not
changed. Both failed logs are preserved. Updated current readiness links this
result; no full-model GPU or training claim follows.

Corpus019 remains current. Jsons completion awaits quarantine integration,
attribution, split and task acceptance. GPU remains stopped.

## Corpus 021 assembly and Jsons integration — October 10, 2026

The Jsons completion archive is confirmed in R2: 26 files, 940,033 verified
bytes, manifest `8fa213c96cb61f3470257e3a6aa6e2dc04cc496a8c44d3d3896b84b378909e47`.
Selection 019 added its completed replay. Corpus 020 assembly failed closed when
macOS hydration changed a token file's ctime during inventory; the partial output
is preserved and is not a valid corpus. The lineage preflight likewise retained
a source-hydration failure before its successful retry.

Selection 020 binds fresh candidate copies to the already verified corpus 019
restore and the Jsons token candidate. Every copied byte identity was checked;
no integrity check was relaxed. Corpus 021 assembled successfully with 17 examples,
17 tasks, 16 declared repository groups, 338,246 input tokens and 103,123
supervised tokens. Manifest:
`58bd9b83383b86bb0cb25e322478944b58b1cd56d1ae554d75e5dbcded88cd32`.
Content:
`b3ecbbe9da8de54808a14d90909fac65177bffdb544dd8a13286c4c92543fad8`.
All four gates remain null; training denial 019 confirms that training-purpose
loading raises `Quarantine corpus cannot train`.

Authenticated lineage audit 011 resolves all 22 names (16 declared groups, two
historical aliases and four reserved repositories). No cross-boundary GitHub ID
or declared network-root overlap was found. This does not exclude semantic
copies, historical relationships or pretraining contamination.

At this checkpoint corpus 021 publication and schedule generation are still
running; a new completed integration must not be inferred from assembly alone.
The GPU remains stopped. No runtime implementation changed in this cycle, and
the previously reported 368-passed/33-skipped regression is historical evidence,
not a new full-suite run.

## Corpus 021 round-trip accepted — October 10, 2026

Publication 021 and restore 020 verified all 35 files, 3,752,523 bytes. Restored
inspection 020 agrees with assembly 021. Original schedule 025 and restored
schedule 019 are byte-identical for schedule, update stream and report: seed
7401, one epoch, 17 planned updates, 9,216-target update cap, 103,123 consumed
supervised tokens, zero overshoot. Integration check 001 verifies these bindings
and the still-null admission gates. No optimization or training was started.

Schedule 024 failed its source inventory after macOS hydration changed
training_corpus.py metadata; the partial attempt and failure record are retained.
The successful fresh attempt kept all integrity assertions unchanged.

The corpus has only 103,123 supervised tokens across 17 tasks. This is not enough
to substantiate the planned 50M-token campaigns or a performance claim. Next
work expands the repository qualification queue, followed by content-bound
rights, split and task review; Runpod remains stopped.

## Next repository qualification queue — October 10, 2026

Corpus 021 integration evidence is archived in R2: 28 files, 277,009 verified
bytes. Qualification batch current-003 selects 32 additional repositories from
the pinned 2,621-trace screen, excluding the current corpus, prior batches and
reserved evaluation names. Validation-002 rederives the selection with normal
and reversed input order and verifies eight repositories in each of four cost
strata. This is a purposive queue, not an unbiased success-rate sample.

Authenticated batch003 lineage-001 resolves all 32 selected repositories and
four reserved repositories, with no cross-boundary ID/network-root overlaps.
Issue-text extraction and limited credential screening are underway; selected
repository metadata is checked before reading issue bodies. No oracle patches
or source commands are used by this extraction.

### Batch 003 issue screening and archive completion

Issue extraction completed for all 32 selected tasks, after repository identity
checks and reserved-name exclusion. The limited source credential scanner found
zero indicator-bearing rows; this is not certification of secret absence or
rights clearance. No oracle columns were read and no source command was run.
Task shards were copied into a SHA-named local cache and checked against the
pinned join registry before reading issue content.

The batch, validation, authenticated lineage, extraction/screening evidence and
current documentation snapshot are archived in R2: 13 files, 283,507 verified
bytes (`qualification-batch003-publish-001`). Three first-review tasks are
csaps-3 (zero smoothing), stochatreat-26 (probability summation) and lkpy-312
(nDCG truncation). Their teacher/evaluator extraction is in progress. None has
runtime qualification, mathematical acceptance or training approval yet.

### Numerical candidate triage completed

All three selected teacher action lists and evaluator inputs were extracted.
Two evaluator attempts failed closed on hydrated intake-receipt metadata; only
the failed stages were retried after terminal failures. The original scripts,
failure records and successful outputs are retained. Exact-base production
sources and notices were fetched; the first guessed stochatreat LICENSE.txt
path returned 404, then the exact-base tree identified LICENSE, fetched
successfully. All three action lists passed the limited indicator screen.

Triage review 002 verifies the stochatreat teacher replacements apply exactly to
the pinned source, then evaluates the changed acceptance expressions using NumPy
summation. The teacher's Fraction(...).limit_denominator() path rejects
[0.123456789, 0.234567891, 0.64197532] despite a NumPy sum of 1, and accepts
[1e-7, 0.9999998] despite a sum near 0.9999999. The publisher's tolerance rule
accepts the former and rejects the latter. The reported [1/2, 1/3, 1/6] case
passes both fixes and fails the original rule. This isolates a real acceptance
regression; it is not a full-package execution claim. The teacher fix is held.

Csaps and Lenskit remain pending isolated runtime controls and independent
weighted-regression/discounted-gain checks. In particular, csaps linear-data
examples cannot by themselves distinguish automatic smoothing from the intended
zero-smoothing fit. None of the three is admitted to the corpus. Review 001 is
superseded by 002, which additionally binds exact production source bytes; its
original script is preserved as review_initial.py under the original hash.

Triage archive completed: 48 files, 389,540 verified bytes in R2, recorded by
`qualification-triage005-publish-001/receipt.json`. No extraction or transfer
process from this cycle remains pending. Next: isolated csaps and Lenskit
runtime controls, independent mathematical checks, then observation review.

## Csaps zero-smoothing qualification — October 10, 2026

Pinned the declared publisher image to
`sha256:a00331f4efcff7a4e8d41d5c63c9bb0712b89c66f61353bd6d156cece8090623`.
The base probe confirms commit 6b73408ecd9d39f5f3c292a8b0446601353e6bac.
A sanitized snapshot retains all 10 tracked files, a single parentless commit,
no accessible old base/solution commits and no enumerated mounted oracle files.
Inherited image layers remain outside that isolation claim. The task interpreter
is Python 3.9.21, NumPy 2.0.2, SciPy 1.13.1, pytest 8.3.4; both conda paths
resolve to the same interpreter file.

Full-file controls retained one deliberately skipped large-vectorization test.
The strict comparator rejected that run. A separate run executes all 46
publisher-declared nodes explicitly: base 45 passed/1 failed; reference and
teacher candidate 46 passed; every expected transition matches. The skipped
case is not represented as passed or silently removed from the full-file record.

An independently derived weighted-affine oracle uses exact Fraction moments and
verifies both normal equations exactly. The zero-smoothing source update is the
weighted orthogonal projection onto the affine nullspace of its second-divided-
difference matrix. Curvature minimization alone does not uniquely select an
affine fit; the projection characterization supplies that distinction. Both
fixes pass 324 vectorized zero-smoothing cases, 6,480 scalar comparisons and 162
interpolation cases, with maximum absolute error 2.4868995751603507e-14. The base
fails the zero-smoothing assertion. Cases cover n=3..8, three moderate grids,
three positive-weight patterns, three non-affine patterns and two output
channels. This does not establish arbitrary-conditioning or universal accuracy.
The source's separate two-point branch reports smooth=1 and is outside these
zero-smoothing cases.

Native replay 003 preserves two no-match grep errors and adds the independent
checks as an explicitly assistant-authored completion. It uses 32 charged calls
plus submission; container cleanup is confirmed. The production patch is 420
bytes, SHA 6e150cc65b9a8688542d9a1a6f7b8702a6acf00dab8fbd620096be8db57fca45,
and its hunk content matches the controlled teacher edit. No scratch files are
in the submission. History 001 has 68 messages/33 exchanges. Token audit 002
verifies 20,802 input tokens and 6,244 supervised tokens without truncation,
with matching collator accounting. Original unseeded demonstrations and print-
only checks are retained but are not used as statistical evidence.

One completion, two history inventories and one token inventory failed closed
on macOS hydration metadata changes; failed attempts are retained and only
terminal stages were retried. No assertions, tolerances or admission gates were
relaxed. The candidate selection and review bindings are ready for quarantine
assembly; corpus021 remains the last integrated corpus. No production runtime
implementation changed in this cycle and no new full regression suite is claimed.
Runpod remains stopped.

Csaps qualification archive verified in R2: 138 files, 1,015,891 bytes
(`csaps3-qualification-publish-001/receipt.json`). All replay, history, token
and transfer processes from this cycle are terminal. Next: integrate the
quarantined candidate with a fresh corpus round-trip, then qualify Lenskit.

## Corpus 022 integration — October 10, 2026

The Csaps candidate is integrated in quarantine: 18 examples/tasks, 17 declared
repository groups, 359,048 input and 109,367 supervised tokens. Manifest SHA
3e9424ea3f8bfc4a0018cd45c9ccb86357c54c4d8156e58ffbc47096a410664d; content SHA
fbab5bdc37acd1487897d76a0a80b8ccc8873bfb6d13db88e9e49def910d27c3. Publication
022 and restore 021 verify 37 files/3,985,491 bytes. Inspection 021 agrees with
assembly. Original schedule 026 and restored schedule 020 match byte-for-byte:
seed 7401, one epoch, 18 planned updates, 9,216-target cap, zero target overshoot.

Authenticated lineage 012 resolves 17 declared groups, two historical aliases
and four reserved names without a cross-boundary current ID/network-root
overlap. Semantic duplication and historical provenance remain separate work.
Denial 020 confirms training-purpose loading rejects the quarantine corpus; all
four gates remain null. Integration check 001 binds these assertions. No model
training or new full regression run is implied. Runpod remains stopped.

The next numerical candidate is Lenskit task 312. Its runtime image is resolved
to an immutable digest; pulling and runtime qualification are separate from
corpus022 acceptance. Its metric oracle must follow the declared discount
convention rather than silently substituting a different nDCG definition.

Corpus022 integration archive is verified in R2: 22 files, 282,006 bytes
(publish attempt002). Attempt001 returned a generic ValueError without a
passing receipt; its exact cause was not exposed by the CLI. Before retrying,
the staged archive and all transfer-source identities were reverified. The
failed attempt and diagnosis limits are retained.

## Lenskit nDCG runtime qualification — October 10, 2026

Pinned publisher image
sha256:d346e23eccfcc530fc12796ec926a912c0d617acd321ba5c7834040887eb6237
and verified the base 0716300a91e55b54e3da150c5fa8355af79fa745. Sanitized image
sha256:3db7134d030d36da8af8d26aa7dd26d6789c289d4efed9769dab865c0b59182c
retains 154 exact tracked files, one parentless commit, inaccessible old commits
and no enumerated mounted evaluator files. Runtime: Python 3.9.20, NumPy 1.22.4,
SciPy 1.13.1, pytest 8.3.3. Both conda interpreter paths resolve to one file.

All 20 publisher-declared nodes are controlled: base 19 pass/1 fail, reference
and teacher 20 pass, with every outcome transition matching. The independent
70-digit Decimal oracle checks 5,850 finite metric cases plus 4,875 exact
suffix-invariance comparisons. Both fixes pass with maximum absolute error
1.1102230246251565e-16; the base fails the oracle. Cases enumerate 65 unique-item
recommendation lists, five graded/binary truth patterns, three explicit discount
conventions, and five positive cutoffs plus None. Ground-truth nonmutation is
also checked. Default discount is max(1, log2(rank)), not log2(rank+1).

This is finite enumeration, not an unbiased success estimate. Zero ideal gain,
negative cutoffs, duplicate recommendations and malformed inputs remain outside
these bounded-score claims. Runtime review 001 binds the results. Native teacher
replay has been initiated; observation review, token validity and training
admission are not yet established. Runpod remains stopped.


## Lenskit 312 completed native qualification

The completed replay `lenskit312-native-003` used 26 charged tool calls plus
submission and confirmed container removal. The first replay broad top-N pytest command timed out after 30 seconds.
The completed replay instead recorded a bus error (exit 135) in shared-memory
code; that actual error remains in the reconstructed history. The assistant-authored completion passed 5,850 independent discounted
gain cases and 4,875 suffix-invariance checks, matching the separate controls
exactly (maximum absolute error 1.1102230246251565e-16). These are finite checks
on unique-item lists, nonnegative relevance and positive ideal gain, not a
universal numerical guarantee or a full top-N suite pass.

The submitted and controlled diffs have different hunk representations. Applying
each to the retained exact base produces identical source bytes. The review also
checks the single changed file, completion bindings and retained bus error.
History construction initially failed a strict inventory check when macOS hydrated
the task shard; that failure is preserved. Retrying after hydration completed
produced 56 messages and 27 tool exchanges. The pinned tokenizer and collator
agree on 24,556 input tokens and 5,880 supervised tokens without truncation.

Evidence: `evidence/data/lenskit312-observation-review-002/report.json`,
`lenskit312-native-history-001/receipt.json`, and `lenskit312-tokens-001/report.json`.
Corpus 022 remains the current integrated corpus; this candidate has not yet been
added. Rights, split and final task admission remain unresolved. No GPU or training
was used.

Review correction: the first observation review carried an inaccurate timeout
limitation copied from replay 001, despite binding replay 003's actual bus-error
event. Review 002 explicitly asserts exit 135 and the fatal bus-error text. The
original review and first R2 qualification archive are preserved as superseded
evidence; the correction archive must accompany them. No token/history bytes
were changed and no full-suite pass is claimed.


## Corpus 023 integration and R2 round trip

Added the Lenskit completion candidate using corrected observation review 002
and quarantine selection 002. Corpus 023 contains 19 tasks, 18 declared repository
groups, 383,604 input tokens and 115,247 supervised tokens. All admission gates
remain null, and training-purpose loading rejects with `Quarantine corpus cannot
train`. No optimizer was run.

R2 publication and restoration verified all 39 files (4,259,039 bytes). Inspection
of the restored corpus matches assembly. Original schedule 027 and restored
schedule 021 match byte-for-byte for schedule, updates and report: seed 7401,
one epoch, 19 updates, 9,216-target update cap and zero overshoot. Lineage audit
013 resolved 20 source names (including historical aliases) and four reserved
names without cross-boundary ID or declared fork-network overlap. The initial
lineage inventory failed on source-file hydration; its log is retained and the
terminal attempt was retried after hydration. Semantic independence is unproven.

Integration verification: `evidence/data/corpus023-integration-check-001/report.json`.
Manifest: c56c4442c2946b6b56b29a84c3775d20536dc9d06717a1cdd8ea2aafff0ea106.
Content: 5ba766c6c4d4fa8aca5975605241a1a38ddb38c4d2537ea2dc7f740a1b36cdf5.
The corpus is still far below the requested data supply; repetition would not
create additional unique tasks or independent evidence. Runpod remains stopped.


## Qualification triage 006: boundary and parsing tasks

Extracted the exact batch-003 teacher/task pairs for xhistogram 20, conllu 35
and gitignore_parser 38. No source commands were executed. Each action list
passed the existing limited credential-indicator screen. Exact-base production
files and license notices were fetched successfully, and each teacher production
replacement matched uniquely. These are provenance checks, not rights approval.

The xhistogram publisher patch increments the final edge by a fixed 1e-8. An
independent interval-membership oracle exposed four discrepancies across 44
scalar boundary cases at scales 1e-12, 1, 1e12 and 1e16: the increment can admit
values above the edge, or round away and still exclude the edge. The base also
fails four cases. The teacher uses equality to move only the final-edge values
from overflow to the last bin and matches all 44 cases. This verifies isolated
NumPy indexing expressions only; weighted/density/multidimensional and Dask
behavior still require runtime checks. The teacher also removes an empty-array
demonstration and uses print-only checks, so those observations cannot establish
assertion-backed correctness.

Conllu's teacher/reference regex edits agree syntactically; malformed labels,
ID grammar and multi-pair parsing still need tests. Gitignore's teacher stringifies
paths whereas the publisher checks exact str type, so subclass handling and
str/Path parity need independent checks. All three remain outside corpus 023.
Evidence: `evidence/data/qualification-triage006-review-001/report.json`.


## Xhistogram runtime boundary checks and environment hold

The pinned raw image ran 192 full-array numerical cases per role: 1D/2D,
four boundary scales, weighted/unweighted, density/counts, three block settings,
and NumPy/Dask. The teacher correction passed all cases, preserving 96 lazy Dask
results. Base and the publisher's isolated numerical insertion failed all 192
constructed boundary cases. This is targeted diagnosis, not a general benchmark.

Snapshot 002 independently preserves all 34 tracked files with one parentless
commit and removes checked history/oracle paths from the mounted filesystem.
Build 001 failed because the PR head object is absent; build 002 explicitly
requires absence and does not assert ancestry. The initial interpreter probe
incorrectly imported unrelated SciPy, which is not installed; probe 002 records
the actual NumPy/Dask/xarray dependencies. Both failures are retained.

All 25 publisher nodes ran in each snapshot role: base 21 passed/4 failed,
reference and candidate 24 passed/1 failed. Candidate fixes exactly the three
right-edge cases and matches reference outcomes. However, the three declared
Dask failures now pass, and the declared-passing 3D-density case fails in every
role with a NumPy 2.0.2 inhomogeneous-shape reduction error. The strict comparator
rejects this mismatch. Runtime qualification is held pending dependency
compatibility diagnosis; expectations were not weakened. No task was added to
corpus 023 and no agent/GPU training ran. See
`evidence/data/xhistogram20-control-drift-001/report.json`.


## Xhistogram single-dependency diagnostic

NumPy's official 1.24 release notes document the removal of implicit ragged-array
creation (https://numpy.org/doc/1.24/release/1.24.0-notes.html). A PyPI-hash-verified
NumPy 1.23.5 CPython 3.9 Linux wheel was installed offline, without dependency
resolution, over the isolated snapshot. Python, Dask, xarray and pytest version
fields remain unchanged; this is not an exhaustive environment-equivalence proof
or a reconstruction of the unpinned Python 3.6 publisher environment.

The 3D-density test now passes in every role. Base: 22 pass/3 fail; complete
reference and candidate: 25 pass/0 fail. The only base failures are the three
reported right-edge cases. All 192 independent finite boundary/weight/density
cases also pass for the candidate in the diagnostic snapshot; the complete
reference patch fails the targeted boundary oracle. The three declared Dask
FAIL_TO_FAIL cases still pass for all roles, so the unchanged strict comparator
continues to reject exact publisher-transition reproduction. Training admission
and native replay qualification are not granted by this diagnostic.

Build 001 failed because BuildKit interpreted the bare local image ID as a
registry name. Build 002 uses a unique local tag whose image ID was checked before
and after the build. The failed attempt and immutable input records are retained.
Evidence: `evidence/data/xhistogram20-compat-review-001/report.json`.


## Conllu 35 runtime preparation

The pinned task image was downloaded after a free-space check. Base HEAD matches
the joined task and 454 commits were reachable before sanitization. The first
snapshot build failed because the selected PR-head object is absent. Its receipt
and Docker log record failure; the wrapper then stalled on an iCloud source read
while formatting the error. After checking its exact PID/command and absence of
child processes, the wrapper was terminated (exit 143), preserving the failure
artifacts. A fresh context explicitly requiring solution absence built snapshot
002. This verifies absence during construction, not ancestry.

The interpreter probe identifies Python 3.9.20 and pytest 8.3.3, importing
`/testbed/conllu/parser.py`. A finite grammar oracle contains 2,974 cases and
round-trip assertions; it is prepared but not yet executed. Independent snapshot
verification is pending a separate source-file hydration read. No qualification,
corpus change or training admission is implied by this preparation.


## Conllu 35 snapshot and runtime qualification

Independent snapshot verification now passes: 21 exact tracked files, one
parentless commit, checked old commits inaccessible and enumerated oracle paths
absent from the mounted filesystem. A preflight hydration metadata change in
`source_snapshot.py` was rejected and retained; the retry kept all checks.

All 49 publisher nodes reproduce declared transitions: base 48 pass/1 fail;
reference and candidate 49 pass. The independent character-grammar oracle ran
2,974 finite cases: base 288 mismatches, reference and candidate zero. Candidate
and reference each passed 366 serialization round trips. Scope includes short
label strings, five canonical ID forms, selected malformed input fallbacks and
inverted range errors; this is not complete CoNLL-U conformance.

Runtime review: `evidence/data/conllu35-runtime-review-001/report.json`. Native
replay preparation has started using a hash-verified source cache and the isolated
image. Corpus 023 is unchanged, and training admission remains ungranted.


## Conllu 35 completed replay and token audit

Completion replay 003 finished with 37 charged calls plus submission, and the
container was removed. Its final 578-byte patch exactly matches the retained
reference production patch; the two print-only demonstration files were removed
by explicit assistant-authored completion commands. The independent 2,974-case
checker then completed with zero mismatches and 366 round trips. The original
commit lookup error at source index 68 is retained, rather than suppressed.
Replay 002 failed its source inventory during hydration before execution; its
partial actions and diagnostic log are retained.

History 001 contains 78 messages and 38 tool exchanges. The pinned tokenizer
and collator agree on 24,056 input tokens and 5,893 supervised tokens without
truncation. Observation review 001 binds the final patch, command results,
semantic counts and masks. A separate source-bound language argument explains
backward acceptance inclusion and its limits, including newly reached invalid
ID exceptions; it is not proof-assistant verification or full format compliance.

`conllu35-quarantine-candidate-001` is ready for quarantine assembly. Corpus 023
is still the current integrated corpus. No training admission or learned model
performance is claimed.


## Corpus 024 integration and restore verification

Added the completed Conllu candidate to quarantine. Corpus 024 contains 20 tasks
across 19 declared repository groups, 407,660 input tokens and 121,140 supervised
tokens. All admission gates remain null; training-purpose loading still rejects
with `Quarantine corpus cannot train`. No optimizer was run.

R2 publication and restoration verified 41 files totaling 4,525,271 bytes.
Inspection of the restored bundle matches assembly. Original schedule 030 and
restored schedule 022 have identical schedule, update and report bytes: seed 7401,
one epoch, 20 planned updates, 9,216-target update cap and zero overshoot.
Lineage audit 014 resolved 21 source names including historical aliases and four
reserved names, without cross-boundary IDs or declared fork-network roots. This
does not establish semantic independence.

The initial lineage audit and schedules 028/029 rejected hydration metadata
changes; their failure records and partial outputs are preserved. After reading
all inventory-bound source files before retry, schedule 030 passed without
weakening any check. Integration verification is in
`evidence/data/corpus024-integration-check-001/report.json`.
Manifest SHA-256: cf8a26f3e94d7ea0f971cbb94068c2dec91746aa4d15047062acef84d0af485a.
Content SHA-256: 960d74ba3f66d24f36289861509cbc28a188f248562dcdea98837a32286519d5.
Data remains far below the planned campaign supply and is not training-admitted.


## Corpus 024 integration evidence archive

Completed October 10, 2026 (transfer receipts dated October 11 UTC).
Revalidated every input bound by the existing corpus024 integration report before
staging an explicit allowlist of receipts, schedules, lineage data, source scripts,
failed preflight evidence and documentation snapshots. No credentials or whole
workspace directory were staged. The archive contains 29 files / 324,042 bytes.

R2 publish and fresh-directory restore both returned verified receipts. The restored
archive also passed the local manifest verifier. The publish reused seven objects
and uploaded 22. Manifest SHA-256:
`38a6328cfc8bba505736af077b54876aab64b5577fdeafc8ae9b9417812ee028`.
Evidence: `evidence/data/corpus024-integration-publish-001/receipt.json` and
`evidence/data/corpus024-integration-restore-001/receipt.json`.
The archived documentation is the pre-archive snapshot; these receipt links and this
journal entry were added afterward. Production code was unchanged, so no additional
CPU-suite result is claimed. The previous goal turn supplied a live stopped-pod
check; this cycle advances evidence durability and restore validation locally.

P1 remains incomplete. Corpus024 is quarantine-only, with 20 tasks and 121,140
supervised tokens. No training admission or GPU readiness was established. Keep
Runpod stopped. Next local qualification: Gitignore38 path semantics; Xhistogram20
remains held pending resolution of historical publisher-transition discrepancies.


## Gitignore38 runtime and independent path qualification

The previous goal cycle completed corpus024 evidence archival and restore verification.
This cycle advances the next candidate without using Runpod. Pulled the pinned
Gitignore38 image after checking available disk capacity; reproduced the exact base
with 66 reachable commits. Built a snapshot requiring the solution commit already
absent, then verified eight tracked files, one parentless commit, inaccessible old
commits and absence of enumerated oracle files in the mounted filesystem. This
does not audit inherited image layers.

Python 3.9.20 and pytest 8.3.3 reproduce all 12 publisher transitions: base 11 pass,
reference and teacher 12 pass. Independent literal-rule, precedence and directory
negation checks cover 120 targeted cases. Base has 40 mismatches; reference has
two plain-str-subclass slash-preservation mismatches; teacher has zero. Empty str
still raises IndexError, and arbitrary custom path classes and complete Git
semantics are not established. The scoped preservation argument and limitations
are in `evidence/data/gitignore38-runtime-review-001/scope.md`.

All runtime test containers reported successful cleanup. Native replay, observation
attribution, and corpus admission remain pending. Corpus024 remains unchanged and
quarantined. No production code changed, no GPU session ran, and no statistical
model-performance gain is claimed.

Runtime evidence archive verified in R2: 86 files, 131,847 bytes. Receipt:
`evidence/data/gitignore38-runtime-publish-001/receipt.json`. No archive restore
was run for this candidate in this cycle; publish verifies remote object hashes.


## Gitignore38 native replay and adapter compatibility

Expanded the replay adapter with a narrow grammar for root-relative Python test
commands, selected git status/diff commands, removal of explicitly named local
Python scratch files, and escaped bracket grep searches. Source command text and
search escapes are retained; root-relative commands are bound to /workspace.
This does not emulate arbitrary persistent shell directory changes. Rejection
tests cover shell operators, expansions, unsafe paths and unreviewed flags.

Focused regression: 21 tests passed. Full native-environment regression: 404 tests,
387 passed, 17 skipped, 17.714 seconds. Earlier runs failed because cloud-backed
files changed metadata while hydrating; their full logs are preserved. Integrity
checks were not relaxed. This environment differs from the earlier 33-skip suite;
no GPU or skipped-environment coverage is claimed.

Native002 completed 33 tool calls and cleanup. Native003 adds one explicitly
assistant-authored completion call asserting all 120 independent path cases;
34 tool calls completed and cleanup succeeded. The 607-byte submitted production
patch produces the same file bytes as the runtime-qualified teacher patch.
Source errors at indices 28 (original TypeError reproduction), 38 (unsupported
directory expectation), and 54 (grep no match) remain in the recorded history.

History001 contains 72 messages and 35 exchanges. Tokens003 exports 15,369 input
and 4,251 supervised tokens without exceeding the 32,768 input cap. Earlier token
exports rejected hydration changes in training_masks.py and training_batch.py;
earlier history attempts rejected hydration changes in the task shard and protocol
fixture. No failed attempt is counted as passing. Corpus024 is unchanged; this
candidate still needs integration and final admission review. Runpod stays stopped.

Native evidence archive: 35 files / 652,172 bytes, remote hashes verified.
Receipt: `evidence/data/gitignore38-completion-publish-001/receipt.json`.
No restore of this native archive was performed in this cycle.


## Corpus 025 integration and restore verification

Added the reviewed Gitignore38 completion to quarantine using token and observation
identity bindings. Reused corpus024 examples only after checking restored bytes
against their manifest identities. Corpus025 contains 21 tasks, 20 declared
repository groups, 423,029 input tokens and 125,391 supervised tokens.

Manifest SHA-256: `5dc4fb2ee99ce2f5a1b1587dc32ec533a44e892fe75081c87e8721a262d229cc`.
Content SHA-256: `4fb93bd1b0f9f6f41846897b4df3a957e131aa5180a92d842bf035181530aceb`.
R2 publish025 and restore024 verified 43 files / 4,694,369 bytes. Restored
inspection024 agrees with assembly025. Original schedule031 and restored schedule023
are byte-identical, including their reports: one epoch, seed 7401, 20 planned updates,
9,216-supervised-token update cap, exactly 125,391 targets and zero overshoot.
No optimizer steps were performed.

Authenticated lineage015 resolves 26 names (20 declared groups, two historical
aliases and four reserved repositories), with no cross-boundary IDs or declared
fork-network roots. Semantic duplicates and historical independence remain
unproven. All four admission fields are null and training-purpose loading fails
with `Quarantine corpus cannot train`. Runpod remains stopped. The next work is
expanding qualified task supply and completing content-bound admission reviews;
this small corpus does not supply the three planned 50M-token campaigns.

Integration evidence archive verified in R2: 23 files / 311,021 bytes.
Receipt: `evidence/data/corpus025-integration-publish-001/receipt.json`.
Archived documentation predates this receipt link. The corpus itself was restored
and inspected; the separate evidence archive was remotely hash-verified on publish.


## Triage 007 and ASDF1853 runtime qualification

Reviewed three additional pinned-cohort tasks: Lmfit487 error-state recovery,
Munch52 default-valued YAML loading, and ASDF1853 converter validation. Exact-base
production sources and licenses fetched successfully. Limited credential-indicator
screen passed for all three action sets. No source actions were executed during
static review. One evaluator extraction rejected hydration metadata drift; the
failure log was retained and extraction completed after hydration.

Lmfit's teacher clears the error list but omits the reference error_msg reset;
Munch's teacher specializes DefaultMunch while the reference generalizes subclass
construction. Their runtime consequences remain unmeasured. ASDF's ConverterProxy
AST matches the reference; import cleanup differs. Triage archive verified in R2:
45 files / 214,865 bytes, receipt qualification-triage007-publish-001.

ASDF's pinned image matches base f3f60705343b1f0ad521cf780b330f2eabf103fa.
The first absent-solution build failed; the ancestry-checking build succeeded.
Snapshot verification matches 887 tracked files, one parentless commit, old
commits inaccessible and enumerated oracle files absent in the mounted filesystem.
Python 3.9.21 / pytest 8.3.4 imports the intended module. Publisher controls reproduce
all 28 transitions (base 26 pass; reference and candidate 28 pass). Independent
set-intersection checks cover 1,024 combinations; base 67 mismatches, reference and
candidate 0. The exact finite combinatorial count is derived in the scoped review.
No wildcard/general converter theorem, statistical model gain or training
admission follows. Native replay is next; corpus 025 remains unchanged. All
probe/test containers reported successful cleanup. Runpod remains stopped.

ASDF runtime archive verified in R2: 88 files / 169,961 bytes. Receipt:
`evidence/data/asdf1853-runtime-publish-001/receipt.json`. Remote object hashes
were verified on publish; no restore of this evidence archive ran in this cycle.


## ASDF native replay and corpus 026 integration

ASDF native001 completed 28 tool calls and container cleanup. The submission
contained the converter change and a reproduction script. An explicitly
assistant-authored completion removed three source-created scratch scripts and
asserted all 1,024 independent tag-set cases. Native002 completed 30 calls,
verified cleanup and submitted only the 1,565-byte converter patch. Applying it
to the pinned base produces the same file bytes as the runtime-qualified teacher
patch. The no-match grep at source index 28 and old warning-test failure at 44
remain in the history. Neither is represented as a passing test.

History001: 64 messages, 31 exchanges. Tokens001: 19,911 input and 5,025
supervised tokens, untruncated. Native evidence archive: 27 files / 591,209 bytes,
R2 verified receipt asdf1853-completion-publish-001. No new shared production
code change or CPU regression result is claimed in this cycle.

Corpus 026 contains 22 tasks / 21 declared repository groups, 442,940 input and
130,416 supervised tokens. Manifest:
`711580a0d1798811c0040b15e6e27c54939203d333efff8c2bcd07d3992ec087`.
Content: `234e924198305fdf0b3624b649d5edc0738161cbccdc80e26d8265685db91450`.
R2 publish026 and restore025 verified 45 files / 4,912,935 bytes; inspection025
agrees with assembly026. Original schedule032 and restored schedule024 are
byte-identical: one epoch, seed 7401, 21 planned updates, 9,216 target-token
update cap, exactly 130,416 target tokens and zero overshoot. No optimizer ran.

Lineage016 resolves 27 names: 21 declared groups, two historical aliases and
four reserved repositories. No cross-boundary repository-ID or declared network
root overlap was found; semantic and historical independence remain unproven.
All admission fields remain null, and training-purpose loading rejects the
quarantine corpus. Runpod remains stopped. Lmfit and Munch behavioral differences,
corpus-scale attribution, frozen splits and sufficient data volume remain open.

Integration evidence archive verified in R2: 23 files / 319,038 bytes. Receipt:
`evidence/data/corpus026-integration-publish-001/receipt.json`. Documentation
snapshots in the archive precede this receipt link. Corpus restore is verified;
the separate evidence archive has publish-time remote hash verification only.


## Completion-aware mechanical admission

The previous goal cycle completed ASDF replay and corpus 026 integration. This
cycle closes a shared-tooling gap: replay_admission previously reconstructed only
ordinary histories, although the history builder already supported explicitly
authored completion steps. It now selects completion-aware reconstruction and
checks source-action identity, final-patch identity, completion implementation
identity, matching history/replay plans, command results and authorship mappings.
Undeclared completion events are rejected. Added calls remain charged to the same
tool budget, and training_approved remains false.

Nineteen focused tests pass, including tampered commands, results, authorship,
source actions and plan bindings. Full native-environment suite: 413 tests,
396 passed, 17 skipped, 17.486 seconds. No GPU coverage is claimed.

Validated the implementation against actual ASDF evidence: regenerated paired
controls under an explicit standard execution profile, checked all 28 publisher
transitions, and graded the exact native002 submitted patch in a fresh container.
All 28 cases match the reference, with no disagreements and successful cleanup.
The mechanical assessor passes with no blockers: 30 calls including 2 completion
calls, 19,911 input tokens plus 8,192 output reserve = 28,103 <= 32,768. Source errors
and completion authorship remain in the reconstructed history. This does not
resolve rights, semantic split isolation, all runtime qualifications or training
readiness. Corpus 026 bytes and admission fields are unchanged; Runpod stays stopped.

Completion-admission evidence archive verified in R2: 44 files / 107,454 bytes.
Receipt: `evidence/data/completion-admission-publish-001/receipt.json`. Publish
verified remote hashes; no archive restore ran in this cycle.


## Standard mechanical assessment: Gitignore38 and Conllu35

Extended standard paired controls and exact native-patch grading to two more
completed replays. Gitignore matches all 12 reference nodes; Conllu matches all
49. All grading containers report cleanup and unchanged tracked source during
tests. Mechanical assessments pass with training_approved=false.

Gitignore: 34 charged calls (one explicit completion), 15,369 input plus 8,192
output reserve = 23,561 / 32,768; 4,251 supervised tokens. Conllu: 37 charged
calls (two explicit completions), 24,056 input plus 8,192 reserve = 32,248 /
32,768; 5,893 supervised tokens. Conllu has only 520 tokens of margin, requiring
re-audit after prompt or schema changes. Both use the 40-call assessment limit.

The first batch used the wrong Conllu history directory. No passing admission
receipt was produced for that attempt. Its log is retained; the follow-up used
conllu35-native-history-001 after checking every token-audit history binding.
No replay or grader needed repeating. Source observations and completion
authorship are preserved.

Three corpus examples now have current standard exact-patch and completion-aware
mechanical assessments: ASDF, Gitignore and Conllu. This is not corpus-wide
qualification. Rights, frozen semantic split review, sufficient data volume and
GPU checks remain open. Corpus026 and its null admission fields are unchanged.
No shared code changed in this cycle; the previous 413-test result is retained.
Runpod remains stopped.

Assessment archive verified in R2: 77 files / 185,695 bytes. Receipt:
`evidence/data/completion-admission-batch-publish-001/receipt.json`. Remote hashes
were verified during publish; this archive was not restore-tested in this cycle.


## Corpus 026 supply and context-policy audit

Revalidated the restored corpus against manifest
`711580a0d1798811c0040b15e6e27c54939203d333efff8c2bcd07d3992ec087`.
Independent shifted-label and input accounting matches 130,416 supervised and
442,940 input tokens across 22 tasks and 21 declared repository groups. All
sequences fit 32,768 tokens. The separate 8,192-token output-reserve screen
passes 20/22: Emcee 295 exceeds it by 2,828 tokens; CloudEvents 172 by 2,237.
This is not an admission or model-runtime test. No histories were truncated.

A 50M-token campaign represents exactly 3125000/8151 (about 383.39) current
corpus-equivalent passes. Repetition does not create new tasks or independent
observations. The campaign objective is unchanged and supply remains insufficient.
The current readiness summary and implementation plan now record these constraints.

Source and report: `evidence/data/corpus026-supply-source-001/audit.py` and
`evidence/data/corpus026-supply-review-001/report.json`. The audit executed
successfully using the production inspection loader; no production code changed,
so the prior full regression result remains the latest suite evidence.
Seven files / 45,674 bytes were published and remotely hash-verified in R2,
receipt `evidence/data/corpus026-supply-publish-001/receipt.json`. This small
evidence archive was not independently restore-tested; corpus 026 itself was
restored and validated earlier. Runpod remains stopped.


## Lmfit 487 exact-base runtime qualification

Resumed the original pending probe and file-read processes; both completed.
The source image matches base `6c87262fcfd3c361b197c6769852f76366113246`
and initially exposes 2,987 reachable commits. Built snapshot
`sha256:c69caebdbf28f749b25f5a271625ef9361720b00563e1b0a8b162bcbc16c0fae`
and independently verified all 210 tracked files, one parentless commit,
inaccessible old base/head objects and absence of enumerated evaluator assets.
This checks the mounted filesystem, not inherited image-layer confidentiality.
Runtime: Python 3.9.21, pytest 8.3.4, asteval 1.0.5, exact local Lmfit module.

All 13 publisher nodes reproduced expected transitions: base 12 pass, reference
and candidate 13 pass. Independent finite recovery checks use 3 invalid syntax
forms × 3 integer-valued expressions × 2 assignment methods = 18 sequences,
each with two invalid-valid cycles. All 18 fail on base and pass for both fixes.
Integer expectations 12, 34 and 8 avoid numerical-tolerance ambiguity; this is
finite functional evidence, not a universal mathematical guarantee.

The candidate can retain an empty `error_msg` after recovery, while reference
clears it to None. Shared-evaluator and nonempty diagnostic state are unresolved;
no native replay or training admission is claimed. Corpus 026 is unchanged.
Sources and evidence are under `evidence/data/lmfit487-runtime-source-001`,
`lmfit487-controls-001`, `lmfit487-semantic-controls-001` and
`lmfit487-runtime-review-001`. All completed probe/test containers reported
successful cleanup. No shared production code changed; full regression was not
repeated. Runpod remains stopped.

Runtime evidence archive: 85 files / 262,026 bytes, published and remotely
hash-verified in R2. Receipt: `evidence/data/lmfit487-runtime-publish-001/receipt.json`.
This archive has not been independently restore-tested.


## Lmfit 487 diagnostic counterexamples and teacher hold

Four additional deterministic sequences exercise actual NameError and division
errors, followed by a valid assignment, a new syntax error and final recovery.
The target is either the original parameter or another parameter that shares
the exact evaluator object. No internal error state is manually injected.

Both NameError sequences expose a teacher defect: `missing_symbol+1` fails,
`x+4` is then assigned without evaluation, and the unrelated invalid expression
`x+` raises SyntaxError with the old missing-symbol message. The reference clears
the message. Both fixes ultimately recover value 15 on `x+5`; numeric recovery
alone therefore misses this diagnostic regression. The four sequences are
finite counterexamples, not an estimate of failure prevalence.

The content-bound review holds the uncorrected teacher. A derivative must identify
the assistant-authored correction and repeat native replay and exact-patch grading;
the original trajectory must not be silently relabeled as correct. Corpus 026
remains unchanged. Source: `evidence/data/lmfit487-runtime-source-001/diagnostic_check.py`.
Results and review: `lmfit487-diagnostic-controls-001` and
`lmfit487-diagnostic-review-001` under `evidence/data`.
All diagnostic containers returned successful export and cleanup statuses.
No shared production code changed and no GPU was used.

Diagnostic archive published and remotely hash-verified in R2: 17 files /
37,475 bytes. Receipt: `evidence/data/lmfit487-diagnostic-publish-001/receipt.json`.
The archive has not been independently restore-tested.


## Lmfit 487 explicitly authored derivative

Added `error_msg = None` after the teacher's in-place error-list clear. This is
an assistant-authored derivative; the original teacher remains held. The patch
passes 13/13 publisher cases, 18 finite recovery sequences and four diagnostic
sequences with observed results identical to reference. This does not prove
behavior for arbitrary external aliases of the error list.

Native002 replays the uncorrected teacher and preserves two errors: source68
uses removed NumPy `asfarray` in an algebraic-constraint test; source72 calls
`__set_expression` without Python name mangling. Native005 retains both errors,
adds one explicit correction/cleanup/assertion command, and submits the exact
553-byte patch SHA256 `96cb40cb35de84f2336a4d69ce55b0249b0e8cc2adca14410566b22aeed8c336`.
The added command succeeds and verifies same/shared evaluator recovery. All
40 permitted tool calls are used; container cleanup is confirmed.

Exact-patch grading matches all 13 reference cases. History002 has 84 messages
and 41 exchanges. Tokens002 exports an untruncated 21,298-input / 5,514-target
sequence; input plus 8,192 reserve is 29,490 (3,278 context margin). Mechanical
admission001 passes with no blockers, while training_approved remains false.
Rights, split gates and corpus integration remain pending. Corpus026 is unchanged.

Failed preflights were retained: attempts001/003 hit source-shard hydration
metadata drift; attempt004 hit source_credentials.py hydration drift before
container start. A hash-verified /tmp shard cache and hydrated bound sources
allowed retry005. Evaluator re-extraction first stopped on registry hydration,
history001 on protocol exchanges.json hydration, and tokens001 on training_masks.py
hydration; subsequent executions retained all integrity guards and succeeded.
No shared production code changed; no full regression repeat was warranted.
No GPU was used.

Corrected-candidate evidence archive published and remotely hash-verified in R2:
124 files / 858,107 bytes; `evidence/data/lmfit487-correction-publish-001/receipt.json`.
This archive has not been independently restore-tested.


## Corpus 027 quarantine integration

Added the explicitly corrected Lmfit candidate to verified corpus026 bytes.
Corpus027: 23 examples/tasks, 22 declared repository groups, 464,238 input and
135,930 supervised tokens. Manifest SHA256
`391f7884476c1fa2545615a086fe03a80328505860d8d7631e085f3414c95e4a`;
content SHA256 `bc57e23b1c2bc207a21401066f81d6de3ab9fe969ddb433dbf2e247b58424ff4`.
Measured bundle: 47 files / 5,146,579 bytes. Explicit byte cap raised to 6,000,000.

R2 publish027 and restore027 verified; fresh restore directory is
`/tmp/zenithsync-training-corpus-restored-027`. Inspection026 agrees with assembly027.
Seed7401, one epoch, 9,216-target update cap yields 22 updates and zero overshoot.
Schedule033 and restored-schedule025 are byte-identical, including reports.
Schedule SHA256 `db94a18e7a7252f0a73c6ffaf5b55c2cffa7cf74840d9990cafd462d3c5b67d5`;
prefix SHA256 `0c56972fada889949064ca072e7bd963e65d3097c72b79a26e3266380909f9e5`.
Explicit denial025 returns `Quarantine corpus cannot train`; all four admission
fields remain null. Integration-check001 confirms these facts.

Authenticated lineage018 resolved 28 names: 22 declared groups, two historical
aliases, four reserved repositories. No cross-boundary ID/network-root overlap
was found; this is not proof of semantic or pretraining independence.
Supply audit: 23/23 fit the training length, 21/23 fit the separate output-reserve
policy. Emcee and CloudEvents exceptions remain. Each 50M campaign represents
exactly 5000000/13593 (~367.84) current-corpus-equivalent passes. Data sufficiency
and admission are still open; the campaign objective is unchanged.

Failed outputs retained: restore026 ended with generic ValueError and no passing
receipt (cause not conclusively diagnosed). A later inspection of that directory
passed corpus loading but failed at hashing a cloud-hydrating loader source, so
no passing inspection receipt was produced. Lineage017 failed its final source
inventory during hydration. Fresh restore027 ran byte-identical transfer sources
from /tmp to avoid source eviction; lineage018 hydrates bound sources before
hashing. Integrity guards remain unchanged.

No shared production code changed; corpus inspection, scheduling, rejection and
round-trip verification were the relevant checks. Runpod remains stopped.

Integration and supply evidence archive: 24 files / 99,060 bytes, published
and remotely hash-verified in R2; receipt
`evidence/data/corpus027-integration-publish-001/receipt.json`. The corpus was
restore-tested; this separate small evidence archive was not.


## Munch 52 runtime qualification and incomplete-teacher hold

Pinned image digest `12b95ab79504cc9ef295ac978dd40d1a6ccbb9cd9aa307af851585fac284c269`,
1,351,559,372 compressed bytes. Base probe matches
`dede29c5e8bde7ca575365d50dd44f8fc12a5991` with 184 reachable commits.
Snapshot `35327b86c6110824739502262b2404dcf8bc2b308092ccbc7edab9dfad335069`
independently verifies 20 tracked files, one parentless commit, inaccessible old
base/head objects and absent enumerated evaluator files. Scope is mounted
filesystem, not inherited image-layer confidentiality. Python3.9.20/pytest8.3.3
imports exact `/testbed/munch/__init__.py`.

Publisher controls: base5/6, reference6/6, teacher6/6; transitions reproduced.
Independent checks: six classes × four graph shapes × two loaders + six custom
constructor cases = 54. Graph shapes cover nesting, list-contained mappings,
shared aliases and cycles. Checks require exact subclass identity for each
mapping, sentinel identity for defaults, distinct/memoized factory values and
preserved alias/cycle identities. Base fails45, reference0, teacher27.
Teacher repairs DefaultMunch and its subclass but leaves ChildMunch type loss
and DefaultFactoryMunch/ChildFactory TypeError. These are remaining base
deficiencies rather than introduced regressions. The uncorrected teacher is
held for incomplete general subclass support, with no native replay/admission.

Semantic run001 completed all containers but failed final source inventory on
macOS hydration; its outputs are retained, not treated as a passing comparison.
A retry to the same populated output was rejected; a fresh run002 completed
with all input bindings and cleanup confirmed. Runtime source and review are
`evidence/data/munch52-runtime-source-001` and `munch52-runtime-review-001`;
authoritative finite comparison is `munch52-semantic-controls-002/comparison.json`.
No shared production code changed. Corpus027 remains unchanged; Runpod remains stopped.

Munch runtime evidence archived in R2: 96 files / 237,729 bytes, remote hashes
verified; receipt `evidence/data/munch52-runtime-publish-001/receipt.json`.
This evidence archive has not been independently restore-tested.


## Munch 52 reference-informed corrected derivative

Retained the teacher's DefaultMunch-specific loader and added a generic Munch
classmethod informed by the inspected reference. This explicitly attributed
derivative supports ordinary/custom subclasses and DefaultFactoryMunch without
silently replacing the original teacher. Publisher cases pass 6/6 and all 54
subclass/default/graph cases pass. Added 12 compatibility cases check omitted,
positional and keyword defaults for DefaultMunch and a subclass across nesting
and aliases. Teacher and derivative pass 12/12; reference fails 8/12. These checks
preserve teacher behavior, not a claim that the publisher specifies every call form.

Native001 records original teacher execution (38 calls). Native002 adds one
correction/cleanup/assertion action and submits the expected 1,059-byte patch,
SHA256 `16691be769c060cd4163b60521431bfb6a448a0117cc5ebf42a303f15db38df2`.
Both retain source index 80's exit 128 old-Git-object lookup failure caused by the
sanitized history. Added checks pass, cleanup succeeds, final calls 39/40.
Standard exact-patch grading matches 6/6 reference cases. History001 contains
82 messages/40 exchanges; tokens001 exports 24,332 input/5,953 supervised tokens
without truncation. Input+reserve=32,524, leaving 244 tokens. Mechanical
admission002 passes with no blockers; training_approved remains false.

Mechanical assessment001 failed before writing a passing receipt because
replay_completion.py hydration changed metadata. A prematurely invoked review
then failed on the missing assessment receipt, leaving empty review001.
The completed assessment002 and review002 are authoritative. All integrity
guards were retained. No shared production code changed; relevant validation
was finite runtime, replay, exact-patch grade, token audit and mechanical checks.
Corpus027 is unchanged pending integration; Runpod remains stopped.

Corrected Munch evidence archive: 125 files / 832,963 bytes published and
remotely hash-verified in R2; receipt
`evidence/data/munch52-correction-publish-001/receipt.json`. This separate
evidence archive has not been independently restore-tested.


## Corpus 028 corrected Munch integration

Added the explicitly corrected Munch example to verified corpus027 bytes.
Corpus028 contains 24 examples/tasks, 23 declared repository groups, 488,570
input and 141,883 supervised tokens. Manifest SHA256
`4e0c5cea950900735c89df72550a07ac8305f87d2305792d7cad410265e69ea9`;
content SHA256 `3433a9a4b3d1e657c01e8383c1dbc7c381490b61424a50a21aea8d42d711a1f3`.
The 49-file bundle is 5,414,857 bytes, within the retained 6,000,000-byte cap.

R2 publish028 and restore028 verified. Fresh restore directory:
`/tmp/zenithsync-training-corpus-restored-028`; inspection027 matches assembly028.
Seed7401, one epoch, 9,216-target update cap produces 23 updates and zero overshoot.
Schedule034 and restored-schedule026 match byte-for-byte, including reports.
Schedule SHA256 `3baaaa0128d4daaf4df2266468ec39293fe29b254dc92cab9c162cefbe9fff30`;
prefix SHA256 `a4869579a14018d6d70cdb716ba7b5505f3e19b5fd875dd639c0898a8b66c1d5`.
Denial026 explicitly rejects training with `Quarantine corpus cannot train`;
all four admission fields remain null. Integration verification passed.

Authenticated lineage019 resolves 29 names (23 groups, two historical aliases,
four reserved repositories), with no cross-boundary ID/fork-root overlap.
This does not establish semantic or pretraining independence. Supply audit:
24/24 sequences fit training length; 22/24 satisfy the output reserve policy.
Emcee/CloudEvents remain exceptions. A 50M campaign represents exactly
50000000/141883 (~352.40) current-corpus-equivalent passes. That repetition
does not establish sufficient diverse data. Munch's individual context margin
remains 244 tokens and must be rechecked after prompt/tool changes.

No shared production code changed; relevant checks were corpus validation,
schedule equality, explicit rejection, lineage screening and R2 restore.
The implementation plan and current readiness summary now describe corpus028.
No GPU was used; Runpod remains stopped.

Integration and supply evidence archive: 24 files / 102,223 bytes published
and remotely hash-verified in R2; receipt
`evidence/data/corpus028-integration-publish-001/receipt.json`. The corpus was
restore-tested; the separate evidence archive was not independently restored.


## Qualification triage 008: three distinct repositories

Selected Importlab23, icontract115 and marshdf19 from the existing bounded
32-repository cohort, preserving task/trajectory/source identity and reserved
repository exclusion. Teacher actions, evaluator patches and exact-base
production files are extracted. Production/reference/teacher Python parses;
known credential indicators were not detected in the selected actions. This
indicator screen is not a proof that arbitrary content is secret-free.

Static differences establish the next checks, not runtime success/failure:
Importlab strips .__init__ after converting separators to dots; reference
strips a separator-delimited __init__ first. Literal dotted filenames and path
precedence require review. Icontract's teacher returns the underlying function
before checking contracts when argument count exceeds signature-name count;
valid variadic calls may bypass pre/postconditions and snapshots. Marshmallow
dataframe teacher makes indexes unconditionally optional and synthesizes range
values, whereas reference keeps explicit-dtype indexes required. Typed/missing/
null/mismatched/empty-index cases need runtime evaluation.

Exact-base license retrieval: Importlab LICENSE and marshmallow-dataframe
LICENSE returned 200. Icontract LICENSE returned 404 (retained); the exact-base
GitHub tree identified LICENSE.txt, fetched successfully with its own receipt.
First extraction stopped on batch.json hydration; failed log and script are
retained. Retry binds batch identity before processing and rechecks it after
hydration at completion; integrity guards are unchanged.

Source: `evidence/data/qualification-triage-source-008`; authoritative review:
`evidence/data/qualification-triage008-review-001/report.json`. No new container
images were downloaded. Local free space measured about 7 GiB, so runtime image
work needs capacity review. No shared production code changed; corpus028 is
unchanged. No GPU was used; Runpod remains stopped.

Triage evidence archive published and remotely hash-verified in R2: 40 files /
175,483 bytes; `evidence/data/qualification-triage008-publish-001/receipt.json`.
This separate archive has not been independently restore-tested.


### Icontract 115 runtime qualification — teacher held

Local offline validation completed with Python 3.6.13 and pytest 7.0.1,
importing the exact task module. Snapshot build001 failed because the pinned
image lacks the solution commit. A separate disposable-container Git probe
verified solution absence and base availability. Build002 explicitly used the
already-absent path; no ancestry claim is made. Independent verification checks
58 tracked files, one parentless commit, inaccessible old commits and absent
known oracle paths. This covers mounted files, not inherited Docker layers.

Publisher controls002: base 24/25; reference and candidate 25/25, with every
publisher transition matched. Controls001 completed test processes but failed
its final source identity inventory on macOS hydration of
compare_source_snapshot.py. Its outputs and source are retained; controls002
warms files before the final unchanged-identity comparison without weakening it.

Semantic-controls001: 3 contract kinds × 5 argument counts = 15 finite cases.
For body(*args), signature-name count is one but 2, 3 and 5 positional arguments
are valid. Candidate returns body directly on all nine such cases, skipping
preconditions, postconditions and snapshots; reference has zero mismatches.
Base also fails nine cases, but raises IndexError before body execution.
Equal failure counts do not indicate equivalent behavior. These checks establish
concrete counterexamples, not statistical prevalence or general correctness.

Decision: hold uncorrected teacher; no native replay or corpus addition.
Corpus028 remains unchanged, and Runpod remains stopped. No shared production
code changed. Runtime review: evidence/data/icontract115-runtime-review-001/report.json.
Archive manifest: evidence/data/icontract115-runtime-manifest-001.json
(122 files, 255,875 bytes). Publication status is recorded separately in
evidence/data/icontract115-runtime-publish-001/receipt.json; this evidence
archive has not been independently restore-tested.

R2 publication completed with status verified; all archived content was remotely
hash-verified. This is not an independent restore test.


### Icontract 115 assistant correction — runtime passes, replay policy hold

Removed the teacher early return and replaced unbounded mapping indexing with
zip(param_names, args). For finite sequences P and A, zip enumerates exactly
indices below min(len(P), len(A)), matching reference guarded assignment.
Default initialization and keyword override order remain unchanged. This is a
bounded-mapping equivalence argument, not general Python signature correctness.

Corrected-controls001: all 25 publisher cases match reference; base passes 24.
Corrected-semantics001: all 15 cases pass for candidate/reference; base fails 9.
Corrected-binding001: all 152 cases pass for candidate/reference; base fails 85.
The latter covers 140 mapping combinations (5 name counts × 7 argument counts ×
4 keyword overlays) and 12 fixed/variadic/keyword-only/mixed call-shape cases.
These are deterministic checks, not independent statistical samples. Invalid
calls with rejecting preconditions are excluded because exception priority is
not specified by these acceptance checks.

Source trace has 40 charged calls. At least one appended correction makes 41,
exceeding current 40-call policy. No source history was trimmed, no native replay
or token audit performed, and no corpus addition made. A future independently
authored episode must preserve its own provenance; policy changes need explicit
rationale and broader evaluation. The runtime derivative alone is not trainable.

First correction-script preflight failed with KeyError before runtime because
it used the final action instead of the matched edit. Failed source retained as
controls-preflight.py; fixed source stores teacher_edit explicitly. No shared
production code changed. Corpus028 unchanged; Runpod remains stopped.

Evidence: icontract115-correction-review-001/report.json. Archive inventory:
65 files / 246,789 bytes. R2 publication receipt is
icontract115-correction-publish-001/receipt.json; no independent restore test.

Correction evidence R2 publication completed: status verified, remote hashes
checked; independent restore remains untested.


### Importlab 23 runtime qualification — filename-boundary regression

Source trajectory has 37 charged calls, leaving possible room under the 40-call
policy for an explicit correction. Pinned image pulled after capacity review:
661,973,636 compressed bytes in layers absent from local RootFS identities;
this does not bound uncompressed growth. No unrelated images were removed.

Build001 failed its ancestry requirement. Build002 explicitly checks solution
absence before sanitization; no ancestry claim is made. Independent snapshot
verification confirms 33 exact-base tracked files, one parentless commit,
inaccessible historical commits and absent known oracle files. This covers
mounted filesystem, not inherited image layers.

Runtime Python 3.9.20 / pytest 8.3.3 differs from metadata Python 3.6.
Publisher controls001: base 29/30, teacher/reference 30/30, every expected
transition matched. Semantic-controls001: 30 finite POSIX cases; base fails 8,
teacher fails 4, reference none. Teacher turns foo.__init__.py into foo and
pkg/foo.__init__.py into pkg.foo; each is tested with and without a preceding
search-root miss. These are two filename counterexamples, not four independent
statistical observations. Literal filename dots are not path separators.
Base preserves those inputs, so this is a new regression. No claim is made
that dotted filenames are ordinary import-statement identifiers.

Root __init__, nested packages, dotted directories, ordinary modules and
non-.py extensions are covered. Windows and precedence between two successful
roots are not covered. Teacher held; no correction, native replay, token audit
or corpus integration. Shared production code unchanged; Runpod stays stopped.

Runtime review: evidence/data/importlab23-runtime-review-001/report.json.
Archive inventory: 87 files / 222,705 bytes; publication receipt:
evidence/data/importlab23-runtime-publish-001/receipt.json. Independent archive
restore not tested.

Importlab runtime archive publication completed with status verified; remote
content hashes checked. Independent restore remains untested.


### Importlab 23 corrected replay and subdirectory command mapping

Assistant correction strips an actual separator-delimited __init__ before dot
conversion. Corrected publisher controls and 30 finite POSIX path checks pass.
The original trace required a previously unsupported literal command:
cd <source>/tests && ./run_all.sh. Added narrow subdirectory/script mapping;
execution-parity test preserves working directory, stdout and nonzero exit,
while rejection tests cover traversal, nonlocal roots, options and shell syntax.
This grammar is replay compatibility, not a general shell security boundary.

Original native001: 37 calls; corrected native002: 38 calls including one
explicit assistant completion. Source actions preserved; native commands have
no nonzero exit. Final patch 610 bytes, SHA-256
0f1fc92f4f19c5f99a3b6c003c6f80f860f03de27ee90f4c302e50d09627d9b9.
Both disposable containers removed. Plan001 failed during source hydration;
plan002 is authoritative. Standard controls003 and grade001 establish all 30
publisher matches. History001 has 80 messages / 39 exchanges; tokens003 has
23,697 input / 6,640 supervised tokens, no truncation, 879-token output-reserve
margin. Mechanical-admission001 passes, training_approved remains false.

Desktop hydration interrupted evaluator extraction, controls001, tokens001/002
and history preflight. Byte-equal code/input staging at
/tmp/zenithsync-importlab23-validation-runtime-001 allowed final controls/token
checks without weakening file_record; stable-runtime001 binds staged identities.
Retain failed artifacts; do not label incomplete attempts passing.

Full suite initial run: 416 tests, one failure/four errors caused by hydration
inside identity guards, 17 skipped. Retry after hydration: 416 tests, 399 passed,
17 skipped, zero failures/errors in 18.314 seconds. Logs retained under
evidence/p1/subdirectory-replay-regression-001. This does not verify skipped
GPU/dependency environments or full model training.

Storage: verified three byte-identical 245,825,405-byte shard010 temporary
caches and no open file handles. Removed only Lenskit/Optuna duplicate caches;
retained /tmp/zenithsync-lmfit487-source-cache-001. Logical bytes removed:
491,650,810. Audit evidence/data/local-cache-dedup-001. Historical receipts keep
original paths; reusable bytes remain in the retained cache. No model or Docker
pruning. Corpus028 unchanged; Runpod stays stopped.

Corrected Importlab archive published to R2 with verified remote hashes:
136 files / 981,309 bytes, importlab23-correction-publish-001/receipt.json.
This archive has not been independently restore-tested.


### Corpus029 integration — corrected Importlab retained in quarantine

25 examples/tasks, 24 declared repository groups; 512,267 input tokens and
148,523 shifted-label supervised tokens. 51 files / 5,673,434 bytes, below the
explicit 6,000,000-byte transfer cap. Manifest SHA-256:
8aeebdaff3af35b3cab4b7c012ee4175f2abe989b9f3960025aa404767882e86.
Content SHA-256:
862e7e67f7cb909dcd2d218527773df55f6e085e42bdd200e9a0da7f65cdbbbb.

Published029 and restored029 verified. Restore to a fresh temporary directory
passed inspection028 with exact assembly totals. Schedule035 and restored027
match byte-for-byte: seed7401, one epoch, 24 updates, max9216 target tokens per
update, zero overshoot. Training-denial027 proves quarantine cannot train;
all four admission gates remain null. Integration-check001 verifies bindings.

Lineage020 resolves 24 declared groups plus two historical names and four
reserved repositories; no current ID/network-root overlap. This does not prove
semantic, historical or pretraining independence. Supply audit029 independently
recounts labels: 25/25 fit training length, 23/25 fit the separate 8192-token
output reserve. Emcee295 and CloudEvents172 remain reserve exceptions.
50M targets / 148,523 = approximately336.65 corpus-equivalent passes; repetition
is not new data or an independent statistical sample. Campaign supply remains
inadequate, and there is no demonstrated learned gain.

Preparation failures from hydration retained in preflight notes. Stable-runtime
assembler originally lacked root-contained candidate paths; empty outputs were
verified empty and removed, and byte-identical candidates were staged inside
its ROOT. Workspace-boundary checks were unchanged. Corpus028 is preserved.
No shared production code changed this cycle; Runpod remains stopped.
Integration evidence inventory: 26 files / 108,783 bytes; publication receipt
corpus029-integration-publish-001. Separate evidence archive not restore-tested;
the corpus itself is restore-tested.

Corpus029 integration evidence publication completed with verified remote hashes.


### Marshmallow-dataframe 19 static policy and capacity qualification

Pinned registry image metadata and public PR head were resolved; no image was
downloaded and no third-party schema code was executed. Capacity screen found
541,065,112 compressed bytes in absent layers, against 4,547,203,072 host free
bytes at measurement. Compressed size is not a decompressed-growth bound.
Download deferred while retaining useful source-policy work; Runpod remains off.

Exact base/teacher/reference ASTs establish the required-field truth table:
index_dtype=None: base True, teacher False, reference False;
index_dtype non-None: base True, teacher False, reference True.
This is a source-policy difference, not measured validation behavior. Teacher
contains three production edits. Publisher added require_index=True case retains
its index, so that case alone does not test typed missing-index rejection.
Other publisher cases may cover it; runtime pass/fail counts remain unknown.

Prepared 36 finite acceptance cases: three index configurations × three row
counts × four presence states. Assertions cover required typed indexes, untyped
range defaults, null/length errors, DataFrame values and unchanged input.
Script compiled only. First draft used dtype strings; retained as
a semantic_check-draft001.py. Current draft uses actual pandas dtype objects;
static-policy-review002 supersedes001 and binds the current script. No claimed
runtime result, native replay, token audit, corpus integration or training gain.
No shared production code changed. Corpus029 remains current quarantine.

Static policy evidence published and hash-verified in R2: 13 files / 37,852
bytes, marshdf19-policy-publish-001/receipt.json. Not restore-tested.


### Scoped build-cache recovery and Marshmallow-dataframe19 runtime hold

Remaining temporary source caches were different shards and retained. Docker
reported a 4.229GB unshared reclaimable PennyLane backend build-cache record.
Its exact command matches saved project Dockerfiles. Single-record prune
reported0B and left the record present; this failed deletion assertion is retained
in scoped-build-cache-cleanup001. The cache graph exposed three descendant
records from the same snapshot build. All four were unshared, immutable and
reclaimable; no outside descendants were present. Pruned individually leaf-first
and verified each ID absent. Image IDs and container IDs remained identical.
No model files, volumes or images deleted. Cleanup002 is authoritative.
Host space recovery was asynchronous; reported cache size is not immediate host
space. Pinned marshdf image pull then completed with 6,393,913,344 bytes free at
its end (measurement fluctuates as Docker/macOS reclaim space).

Raw image starts at exact base. Snapshot001 preserves 17 tracked files and one
parentless commit, hides old history and removes known answer files. Original
Python probe failed because src-layout package was not on sys.path. Probe002
uses explicit /testbed/src and confirms Python3.7.16, pytest7.4.4 and exact local
module origin. Publisher/semantic runs explicitly use that src path; no dependency
versions changed. This adaptation is recorded, not an unmodified-image claim.

Controls001: base17/18, reference18/18, teacher17/18. Teacher fails existing
missing-top-level-index test. Semantic001: 36 finite cases, base3failures,
reference0, teacher6. All six teacher failures accept absent integer/string
indexes with row counts0,1,3 despite configured required dtype. Input dictionaries
remain unchanged in all roles. No universal schema or statistical prevalence
claim follows. Hold teacher; no correction, native replay or corpus addition.
Current runtime semantic source supersedes compile-only draft; prior draft is
preserved as semantic_check-static002.py and in earlier R2 policy archive.
No shared production code changed. Corpus029 unchanged; Runpod remains stopped.

Runtime archive106 files /247,772 bytes published and remotely hash-verified:
marshdf19-runtime-publish002. First publication ended in generic ValueError
and wrote no passing receipt; failure.log retained. Retry used byte-identical
temporary manifest. No independent restore test of this separate archive.


### Marshmallow-dataframe19 correction checkpoint

The explicit reference-informed assistant correction makes an index required if
and only if `index_dtype is not None`. It passes all 18 publisher cases and all
36 finite schema cases (three dtype configurations, three row counts, four index
presence conditions), with unchanged input payloads. These finite checks do not
establish universal dtype correctness.

Native attempt 002 completed the original trajectory; attempt 003 ran the
correction and its nine local assertions at 40 charged calls. Admission remains
held: the submitted patch also contains the teacher-created `reproduce_issue.py`,
so the strict production-patch identity check rejected it. Both containers were
removed. Original native test commands also encountered source-package import
failures; the isolated publisher/semantic controls explicitly set the src path.
These observations must be resolved and retained honestly before qualification.

Evidence: `evidence/data/marshdf19-correction-review-001/report.json`,
`evidence/data/marshdf19-native-003/receipt.json`, and
`evidence/data/marshdf19-native-003/submitted.patch`.
Next: constrain the completion to the production diff, explicitly qualify the
src-layout runtime, independently grade the replay, and audit context/targets.
Corpus029 remains unchanged and quarantined. No GPU was used; Runpod remains
reserved for the explicit user restart and later GPU readiness gates.

Correction evidence archived in R2: 72 files, 449,234 bytes; remote hash
verification passed (`evidence/data/marshdf19-correction-publish-001/receipt.json`).
This evidence archive has not been restore-tested.


### Marshmallow-dataframe19: native correction verified, context hold

This checkpoint supersedes the earlier native patch/import hold. Native attempt
006 uses the explicit `import_root=src` profile, removes only byte-verified
teacher-created diagnostic scripts, and submits exactly one production file.
The final patch is 1,563 bytes, SHA-256
`4cb320c90944de66586bc71b4245b1d1eaacab8a8c2ea06be78d0329dedc9d1a`.
Independent grading matches all 18 publisher cases. The original five command
errors remain in the reconstructed observations; these include offline pip,
unsuccessful searches, and the pre-correction typed-index failure.

Admission remains **held**: 25,649 input tokens + 8,192 output reserve = 33,841,
which exceeds the 32,768 context cap by 1,073. The history has 84 messages,
41 exchanges and 4,229 supervised tokens; native execution uses 40 charged calls.
No truncation, context-policy relaxation, or corpus addition was performed.
Corpus029 remains authoritative and quarantined.

Shared replay and grading now accept a validated, explicit checkout-relative
import root. Grading retains exact module-origin validation. The full regression
run passed 402 tests, with 17 skipped (419 total); earlier hydration-induced
failures are preserved. This is local pipeline qualification, not GPU readiness.
Evidence: `evidence/data/marshdf19-correction-review-002/report.json`,
`evidence/data/marshdf19-standard-grade-001/report.json`,
`evidence/data/marshdf19-mechanical-admission-001/report.json`, and
`evidence/p1/source-import-regression-001/full-suite-003.log`.
Next: retain this candidate outside the corpus and qualify diverse candidates
that satisfy the unchanged context, provenance and correctness requirements.

The updated qualification bundle is archived in R2: 94 files, 915,118 bytes,
with remote hash verification (`evidence/data/marshdf19-correction-publish-002/receipt.json`).
This evidence archive has not been restore-tested.


### Triage 009: API schemas and spelling captions

Prepared pinned teacher actions, exact-base production files and licenses,
evaluator patches, image identities and capacity checks for apispec950 and
spelling177. Source actions pass the known credential-indicator screen; replay
preflight accepts 36 and 32 charged calls respectively. Production syntax trees
match the reference edits (for spelling, only literal TEXT_NODES set order is
normalized). This is static evidence, not package execution or native token fit.

The official OpenAPI 3.0.2 Schema Object specification says additionalProperties
defaults to true. The issue's claim that omission only permits an empty object
is incorrect; qualification must measure explicit schema output and downstream
constraints without adopting that premise. Spelling checks must cover caption
text, existing node categories, inline markup and suppression behavior.

The earlier stochatreat26 counterexamples remain a hold; its existing evidence
was reused rather than overwritten. An attempted duplicate extraction stopped
before overwriting the existing directory, and its failure log was retained.

Image metadata is pinned, but no new image was pulled. Missing compressed layers
are 434,285,633 bytes (apispec) and 484,700,275 bytes (spelling); these do not bound
extraction size. Host free space was about 5.3 GB at inspection. Next: review
reclaimable project caches, then qualify one task runtime at a time. No Runpod
use and no corpus change. The readiness summary was reconciled to corpus029,
including current hashes, 51 files, 148,523 target tokens and 24 planned updates.

Triage009 archive: 49 files, 215,823 bytes, R2 remote hash verification passed
(`evidence/data/qualification-triage009-publish-001/receipt.json`); archive restore
not yet tested.


### Apispec950 runtime correction

The pinned image was acquired after a capacity check. One unused temporary task
shard copy (101,556,119 bytes) was deleted only after verifying the retained shared
cache hash and absence of open handles. Original repository data and the model
were preserved. The source snapshot preserves 56 tracked files and one parentless
commit; the original solution object was absent, so ancestry was not asserted.
Python 3.9.21 / pytest 8.3.5 imports the exact checkout module.

Publisher controls: base 115/117, teacher and reference 117/117. Independent
finite checks: base fails six requested-output cases; teacher and reference fail
nine exact metadata-preservation cases. Six remove closed or typed restrictions;
three true-to-empty-schema changes are representation differences. Three version
configurations are not independent statistical samples.

The explicit assistant correction preserves accumulated additionalProperties
metadata and supplies an empty schema only if that key is absent. It passes all
117 publisher cases and all 36 finite checks. The invariant and its assumptions
are recorded in evidence/data/apispec950-correction-review-001/scope.md.
Next: native replay with attributed correction and byte-checked temporary-file
cleanup, independent exact-patch grading, observation review and token admission.
No corpus change or GPU usage. Runtime correctness of selected cases is not
training readiness or proof of learned performance.

Apispec runtime/correction archive: 150 files, 950,299 bytes; remote hashes
verified (`evidence/data/apispec950-runtime-publish-001/receipt.json`). This
evidence archive has not been restore-tested.


### Apispec950 native qualification complete

Native attempt 001 completed with 37 charged calls and submitted exactly the
intended one-file production patch (743 bytes, SHA-256
231b4599022cd1b6038ef6ef3a97eb009a28e8a91f4cb017140e0a801c16893f).
The attributed completion checks default and explicit metadata and removes three
teacher-created diagnostic files only after matching their SHA-256 identities.
The container was removed. Independent publisher grading passes all 117 cases.

History: 78 messages, 38 exchanges, 23,112 input tokens and 4,244 supervised
tokens. With 8,192 output reserve and a 32,768 context limit, margin is 1,464.
Mechanical admission checks pass; training approval remains false. Observed
errors are preserved: offline flit_core installation failure, one empty grep
result, and two invocations of legacy tests whose expectations are changed by
the publisher test patch. These are not silently relabeled as passing commands.
The first history export was rejected on Desktop file hydration and retained;
a subsequent checked export succeeded without weakening provenance guards.

Next: integrate the hash-bound selection at
`evidence/data/apispec950-quarantine-candidate-001/selection.json` into corpus030;
publish, empty-directory restore, recount tokens, compare schedules, and refresh
lineage/admission-denial evidence. Corpus029 remains authoritative until that
integration is verified. No GPU use or learned model-performance claim.

Native qualification archive: 76 files, 908,807 bytes, remote R2 hashes verified
(`evidence/data/apispec950-native-publish-001/receipt.json`). This evidence archive
has not been restore-tested.


### Corpus030 integration verified

Added the corrected, attributed Apispec950 native replay to quarantine. Corpus030
contains 26 examples/tasks in 25 declared repository groups, 535,379 input tokens
and 152,767 supervised tokens. Its 53-file bundle is 5,928,050 bytes. R2 publication
and restore into an empty directory both passed hash verification. Original and
restored schedules are byte-identical: seed 7401, one epoch, 25 updates, 9,216
supervised tokens per update cap and zero target overshoot. This is scheduling
validation, not executed optimizer updates.

Manifest SHA-256: 806c1ffe57ccee1fa1f6b2d8c73f5b17533786850314126e653599d24428c74b.
Content SHA-256: 310d3c9bc725ab7afe86f9461d9e65de57a934ab1a9577ef8fc15bc2f8626847.
The refreshed public-metadata lineage audit resolves 25 declared groups, two
historical names and four reserved names without current-ID/fork-network overlap.
This does not establish semantic, historical or pretraining independence.

All four admission gates remain null and training-purpose loading rejects the
bundle. The independent supply audit finds 26 sequence-fit examples but only 24
fit input plus the 8,192 output reserve; Emcee295 and CloudEvents172 remain
reserve exceptions in quarantine. Repetition cannot make this sufficient unique
data for the three planned 50M-token candidates. Next: expand qualified diverse
data, complete content-bound attribution and split reviews, and resolve remaining
admission holds before GPU validation. Runpod was not used.

Corpus030 integration evidence: 26 files, 136,267 bytes, R2 hash-verified
(`evidence/data/corpus030-integration-publish-001/receipt.json`). The corpus itself
is restore-tested; the separate evidence archive has not been restore-tested.


## Storage and recovery checkpoint — October 10, 2026

The PennyLane dependency archive was restored from R2 into an empty directory:
107 files, 1,005,376,281 bytes, all content-verified. See
`evidence/data/storage-capacity-audit-001/backend-restore-receipt.json`.
The 231 wheel-cache paths shared only 58 inodes; they were not four independent
copies. After verifying local hashes and no open handles, 289 wheel paths
(the original cache links plus 58 newly restored copies) were evicted.
Recipes, manifests, model files, datasets, Docker images and containers were
preserved. See `evidence/data/dependency-cache-eviction-001/receipt.json`.
Historical wheel-cache paths are now absent: restore the preserved manifest
from R2 into a fresh directory before rebuilding that dependency environment.
Free space after cleanup was 5,299,523,584 bytes, a point-in-time system reading;
concurrent system changes prevent attributing its entire change to this cleanup.
No new training data or training approval resulted. Runpod was not used.
Next: remeasure capacity before the spelling177 runtime acquisition, then resume
candidate qualification and corpus expansion. Keep R2 publication incremental;
verify recovery before evicting unique local artifacts.

Storage recovery/eviction evidence: eight files, 178,838 bytes, published and remotely hash-verified in R2 (`evidence/data/storage-recovery-publish-001/receipt.json`). This separate audit archive has not been restore-tested.


## Spelling177 runtime qualification — October 10, 2026

Pinned image acquisition and a 41-file exact-tree source snapshot completed.
Normal solution ancestry verification passed; the initial absence-check assertion
failed because the solution object was present. That observation is retained.
The sanitized runtime has one commit and inaccessible old base/solution objects.

All 11 publisher transitions reproduce: base passes nine; teacher and reference
pass ten, with the declared docstring FAIL_TO_FAIL preserved. Ten additional
Sphinx integration cases have four base failures and zero teacher/reference
failures. The cases cover direct/repeated captions, existing title/body/list text,
literal suppression, mixed caption text, document exclusion and a custom word list.
A separate observation shows emphasized caption text is skipped in all variants;
this is recorded as a shared limitation, not comprehensive markup correctness.

Review: `evidence/data/spelling177-runtime-review-001/report.json` and `scope.md`.
No native replay, token audit, corpus addition or training admission is claimed.
Next: replay the teacher under the unchanged call/context limits, independently
grade the submitted patch, and complete attribution/split/admission review.
Runpod was not used. Corpus030 remains the current quarantined corpus.

Spelling177 runtime evidence: 103 files, 666,402 bytes, uploaded and remotely hash-verified in R2 (`evidence/data/spelling177-runtime-publish-001/receipt.json`); this archive has not been restore-tested. After image/snapshot validation, local free space measured about 3.1 GiB; do not acquire another image without a fresh capacity review.


## Spelling177 native replay and quarantine candidate — October 10, 2026

Native replay001 completed 32 charged calls and removed its container. The final
386-byte patch changes only sphinxcontrib/spelling/builder.py. Independent grading
matches all 11 reference outcomes: ten passes and the declared docstring failure.
Eight teacher shell errors remain in the recorded history, including grep no-match,
the pre-fix reproduction, and broader suite failures. No full-suite pass is claimed.
The earlier ten finite semantic cases remain passing for teacher and reference;
emphasized caption text remains a documented shared omission.

The 68-message, 33-exchange untruncated history has 20,807 input tokens and 4,433
supervised tokens. After the 8,192 output reserve, 3,769 context tokens remain.
Mechanical admission checks pass, with training approval false. The candidate is
prepared in `evidence/data/spelling177-quarantine-candidate-001/selection.json`.
The bound review is `evidence/data/spelling177-observation-review-001/report.json`.
History and token export each encountered a cloud-file hydration identity change;
failed attempts were preserved and retried without weakening file identity checks.

Next: integrate this candidate into a new quarantined corpus version, restore it
from R2, compare deterministic schedules and refresh lineage/duplicate review.
Corpus030 remains current until that integration completes. Data sufficiency,
rights/split admission and full-model validation remain open. Runpod was not used.

Spelling177 native evidence and token candidate: 54 files, 496,208 bytes, uploaded and remotely hash-verified (`evidence/data/spelling177-native-publish-001/receipt.json`). This archive has not been restore-tested.


## Corpus031 integration — October 10, 2026

Spelling177 is integrated into the next quarantined corpus: 27 examples/tasks,
26 declared repository groups, 556,186 input tokens and 157,200 supervised tokens.
The 55-file, 6,155,247-byte bundle exceeds the prior 6 MB cap; this reviewed
integration uses a 6.5 MB transfer/inspection cap. The byte cap does not relax
sequence length, tool-call, output-reserve or admission policy.

Manifest SHA-256: de6cf69928394b7860693a99acd198520f58b63841b544e260c79c1cb7afce1c.
Content SHA-256: 6b613de0bf8d82656c84d9aea69d43a757d6390e625ffa5ac7d29a2e06227376.
R2 publication and empty-directory restore both verify. Original/restored schedule,
updates and report bytes match: seed 7401, one epoch, 26 updates, 9,216-target cap,
157,200 target tokens, zero overshoot. This plans updates; it does not execute them.

Authenticated lineage audit022 resolves 26 declared groups, two historical names
and four reserved names, with no current ID/network-root overlap. This is not proof
of semantic, historical or pretraining independence. All four admission fields
remain null, and training-purpose loading rejects the restored quarantine corpus.
All 27 sequences fit the length cap; 25 satisfy input plus output reserve. Emcee295
and CloudEvents172 remain reserve exceptions. A 50M-target campaign would reuse
about 318.07 corpus-equivalent passes, which does not provide new independent data.

Next: expand diverse qualified data and complete content-bound rights, split and
training admission review. Runpod remains unused; P1 remains incomplete.

Corpus031 integration evidence: 26 files, 140,204 bytes, published and remotely hash-verified (`evidence/data/corpus031-integration-publish-001/receipt.json`). The corpus is restore-tested; the separate integration evidence archive has not been restore-tested.


## Cohort010 static triage and queue reconciliation — October 10, 2026

Reviewed three pinned existing-cohort traces: Numba6653 (35 planned calls),
Mwclient365 (30), Pika851 (38). All pass action preflight; no native token length
or runtime success is inferred. Numba's production AST matches the reference and
is next for offline runtime qualification. Test absent/present/empty values,
deprecated-prefix precedence and warnings, plus publisher nocuda controls.

Hold the original Mwclient teacher pending state-transition review: it only sets
exists inside a newtimestamp branch and omits publisher metadata/delete/move
updates. The issue's suggested timestamp guard was explicitly uncertain.
Hold Pika pending default/logging review: its default Normal Shutdown differs
from the publisher's Normal shutdown, and it lowers an extra logger's severity.
These are static discrepancies, not measured runtime failures.

`qualification-batch003-status-001/report.json` projects the 32-task cohort onto
corpus031: ten tasks represented (possibly through corrected derivatives), six
explicit holds, one next runtime candidate and fifteen not qualified by this
reconciliation. The original frozen batch remains unchanged.

Numba runtime image is pinned at
sha256:f829d7620787dd998e0614dcba60f20c661fe1dbb90181199dea91e49fb74a53.
The layer-reuse screen estimates 810,263,089 absent compressed bytes; this does
not bound extracted space. Host free space changed to about 7.59 GB during this
cycle without project cleanup, so remeasure before acquisition. No image was
pulled, no corpus was added and Runpod was not used in this cycle.

Cohort010 evidence: 50 files, 361,577 bytes, remotely hash-verified in R2 (`qualification-triage010-publish-001/receipt.json`). The task-status projection is separately published and hash-verified (`qualification-batch003-status-publish-001/receipt.json`). Neither new archive has been restore-tested.


## Numba6653 pinned runtime qualification — October 10, 2026

Acquired the pinned image after a fresh capacity check (~7.59 GB available;
~5.20 GB immediately after acquisition). Its HEAD was not the task base. Accepted
snapshot build002 normalizes the verified image HEAD to the declared base;
915 tracked files match, with one reachable commit and inaccessible old base,
solution and original image-head objects. This is mounted-filesystem validation.
Build001 encountered cloud hydration drift in a final identity check; that failure
is retained. Build002 used byte-identical stable inputs with unchanged guards.

Python3.7.16/pytest7.4.4 imports numba.cuda.envvars from the exact task source.
The single publisher regression fails on base and passes on teacher/reference.
Thirty-six environment/default combinations yield 27 base value failures and
zero teacher/reference failures. Warning checks and three invalid-prefix cases
pass across all variants. Empty-string presence, deprecated-prefix precedence
and default-object identity are explicitly checked. No GPU was used, and no
full Numba suite, native teacher replay or learned-model result is claimed.

Review: `evidence/data/numba6653-runtime-review-001/report.json` and `scope.md`.
Next: replay the 35-call teacher, independently grade the exact submitted patch,
and audit untruncated native context and supervision masks before integration.
Corpus031 remains current. Runpod was not used; P1 remains incomplete.

Numba6653 runtime archive: 99 files, 131,663 bytes, published and remotely hash-verified in R2 (`evidence/data/numba6653-runtime-publish-001/receipt.json`). This separate archive has not been restore-tested.


## Numba6653 native replay — October 10, 2026

Native replay001 completed 35 charged calls, with container cleanup verified.
The 362-byte submitted patch changes only numba/cuda/envvars.py. Independent
exact-patch grading passes the single publisher regression; no full-suite claim.
Two teacher errors are preserved: a no-match grep and the pre-fix reproduction.
The prior 36 environment/default combinations and three invalid-prefix checks
remain bounded semantic evidence, not a trained-model or GPU result.

The 74-message, 36-exchange history is untruncated: 16,388 input tokens and
5,897 supervised tokens, with 8,188 tokens remaining after the 8,192 reserve.
Mechanical checks pass, training approval false. The candidate is ready for
quarantine integration (`numba6653-quarantine-candidate-001/selection.json`).
The bound review is `numba6653-observation-review-001/report.json`.
Cloud hydration interrupted evaluator/admission inventories; failed attempts
are documented. The passing admission uses stable byte-identical history/token
copies and unchanged integrity checks. No output was treated as passing early.

Next: corpus integration, verified R2 restore, deterministic schedule comparison
and refreshed lineage/supply review. Corpus031 remains current until that work
completes. Runpod was not used and P1 remains incomplete.

Numba6653 native evidence and token candidate: 55 files, 377,865 bytes, uploaded and remotely hash-verified in R2 (`evidence/data/numba6653-native-publish-001/receipt.json`). This archive has not been restore-tested.


## Corpus032 integration — October 10, 2026

Numba6653 is integrated: 28 quarantined examples/tasks, 27 declared repository
groups, 572,574 input tokens and 163,097 supervised tokens. The 57-file bundle
is 6,335,601 bytes and remains within the explicit 6.5 MB cap.
Manifest SHA-256: f2a7d2c76913c6ab63d49809cb8113f2f31e5248b0a564b181fa13f308c38b8a.
Content SHA-256: 95c2ff7beaf23a3bfef27a0c7c25c299e42c2bbccf6cbdd618fea11ee11ff474.

R2 publish and empty-directory restore verify. Original and restored schedule,
updates and report bytes match: seed 7401, one epoch, 27 planned updates,
9,216-target update cap, exactly 163,097 supervised tokens, zero overshoot.
No optimizer step or training performance is implied by schedule construction.
All four admission fields remain null; training-purpose loading rejects the data.

Lineage023 resolves 27 declared groups, two historical names and four reserved
names without current ID/network-root overlap. Historical/semantic independence
remains unproven. All 28 examples fit 32,768 tokens; 26 meet the separate output
reserve policy. Emcee295 and CloudEvents172 remain reserve exceptions. A 50M-token
campaign would consume about 306.57 corpus-equivalent passes; repetition does
not add independent tasks. Data abundance and final rights/split approval remain
unmet. The supply audit was retried after a loader-file hydration guard failure;
no integrity check was weakened.

Next: expand diverse qualified supply and complete remaining admission reviews.
Runpod was not used; P1 remains incomplete.

Corpus032 integration evidence: 27 files, 144,165 bytes, uploaded and remotely hash-verified (`evidence/data/corpus032-integration-publish-001/receipt.json`). Corpus032 is restore-tested; the separate integration evidence archive has not been restore-tested.


## Verified source-byte ingestion and cohort011 triage — October 10, 2026

A real Rally teacher extraction passed file hashing but failed PyArrow's subsequent
file-backed footer read. The exact OS cause is unproven; cloud hydration/eviction
is a plausible contributor. `verified_source_bytes` now captures at most the pinned
size plus one byte (512 MiB cap), verifies exact length/SHA-256, and supplies a
PyArrow BufferReader. Existing census, rights/provenance, metadata linkage and
post-extraction file drift checks remain unchanged. The helper identity is recorded.
This cap bounds captured bytes, not arbitrary parser decompression memory.

Three focused tests pass: modified/truncated/extended bytes reject; oversized
inputs reject before open; an actual filtered Parquet parse survives replacement
of the source path after capture, while a new capture of that changed path rejects.
All three real candidate extractions succeed. Full suite attempt001 recorded one
unrelated server-source hydration error. Attempt002: 422 tests, 405 passed, 17 skipped.
No GPU or optional-environment coverage is claimed.

Static review: SoftLayer2188 matches the reference AST and has 35 planned calls;
prioritize complete CLI behavior checks, not only truthiness snippets. Rally1469
has 39 calls and matches the connection default edit; the reference also changes
a chart metric, so review issue/test scope explicitly. Pylutron20 has 34 calls but
joins device-name components with spaces instead of underscores. Hold it pending
exact-name contract and rights review: root LICENSE returned 404; root metadata
showed no license/copying-named file. No runtime candidate was executed here.

Evidence: `qualification-triage011-review-001` and
`evidence/p1/source-byte-snapshot-regression-001`. Corpus032 remains current;
no training admission changed. Runpod was not used; P1 remains incomplete.

Cohort011 and verified-byte ingestion evidence: 47 files, 260,658 bytes, uploaded and remotely hash-verified (`evidence/data/qualification-triage011-publish-001/receipt.json`). This archive has not been restore-tested.


## SoftLayer2188 runtime qualification — October 10, 2026

The pinned source snapshot matches 753 tracked files and exposes only one reachable
commit; base/solution commits and known evaluator paths are inaccessible in the
mounted repository. Inherited Docker-layer bytes remain outside this audit.
Publisher controls reproduce exactly: base 3/4, reference and teacher 4/4.
The 28-case CLI grid (seven query tuples × two types states × two advanced states)
has six base failures and no reference/teacher failures. Exact exit codes, API
method routing and argument lists are checked through the real CLI and the
repository's local XML-RPC fixture server. No external service correctness claim.

The earlier static type description is corrected: query is a tuple of strings;
a tuple containing an empty string is truthy even though its joined query is empty.
Types takes precedence over advanced; advanced with no query is accepted. The
initial direct search import failed because CLI.command was not initialized;
probe002 imports CLI.core first, matching normal initialization. Both attempts
are preserved. Python 3.9.21 / pytest 8.3.5 and exact source origins were verified.

Evidence: `softlayer2188-runtime-review-001`, `softlayer2188-controls-001`, and
`softlayer2188-semantic-controls-001`. Native replay, untruncated token auditing,
content-bound review and integration remain pending. Corpus032 is unchanged;
no training approval, learned gain or full-model guarantee follows from this work.
No production code changed; the existing CPU suite result remains 405 passed and
17 skipped, not a new suite execution. Runpod was not used.

Local storage remains constrained (about 3 GiB available at the current check).
Only 7,530 regenerable task bytecode files were removed after an open-handle check
in the preceding acquisition step; receipt: `bytecode-cache-cleanup-001`.
No additional large downloads were needed for this runtime qualification.

SoftLayer runtime archive: 114 files, 2,904,966 bytes; R2 publication and fresh-directory restoration both verified. Receipts: `softlayer2188-runtime-publish-001` and `softlayer2188-runtime-restore-001`.


## SoftLayer2188 native replay and token qualification — October 10, 2026

Native replay completed with 35 charged calls, 74 messages and 36 exchanges. The
431-byte submitted patch changes only `SoftLayer/CLI/search.py`; SHA-256:
`0be7e50c36cb4e94c2e3a49e9836f3539d41c9cee812b911b704548d97209bf4`.
Independent grading matches all four publisher cases. The last native test command
passes seven existing CLI/manager tests. Earlier failures remain visible: original
bug reproduction at index14; offline external API errors at44/58/70; obsolete
embedded diagnostic working directories at52/56/62. No full-suite or external API
success is asserted. The history ends with observed native patch submission, not
unverified teacher finish prose.

Untruncated pinned-tokenizer audit: 16,291 input / 2,850 supervised tokens. Reserve
margin = 32,768 - 16,291 - 8,192 = 8,285. Mechanical linkage, grading and mask/budget
checks pass with training_approved=false. Candidate remains pending content-bound
review and corpus integration; corpus032 remains authoritative. Evidence:
`softlayer2188-observation-review-001`, `softlayer2188-standard-grade-001`,
`softlayer2188-tokens-001`, `softlayer2188-mechanical-admission-001`.

Cloud hydration changed file metadata during local evaluator/history checks;
stable cached sources and copied receipts were used without weakening integrity
checks. Existing task-cache files were hard-linked into the stable runtime, not
redownloaded. No production code changed, no full CPU suite was rerun and Runpod
was not used. P1 remains incomplete.

Native replay evidence archive: 62 files, 414,112 bytes; uploaded and remotely hash-verified in R2 (`softlayer2188-native-publish-001/receipt.json`). This separate native archive has not been restore-tested; the earlier runtime archive has.


## Corpus033 integration and R2 round trip — October 10, 2026

SoftLayer2188 joins quarantine after its linked runtime and native observation
review; its seven failed commands remain preserved. Corpus033 contains 29 tasks
and 28 declared repository groups, with 588,865 input and 165,947 supervised tokens.
No training admission is granted. Assembly and independent shifted-label recount
agree. The 59-file, 6,514,884-byte bundle is published and restored from R2. Its
manifest SHA-256 is `de181d6fb9014532d3394a0bef42ee2b47a54c183a7a7770b783f7d98bb0f0db`.

Original and restored schedule.json, updates.jsonl and report.json are byte-identical:
seed7401, one epoch, 27 planned updates, cap9216 targets/update, 165947 consumed
supervised tokens, zero overshoot. These are planning outputs, not optimizer steps.
All four admission gates remain null; training-purpose load rejects exactly with
`Quarantine corpus cannot train`. All29 sequences fit32768;27 satisfy the separate
8192-token reserve screen. Emcee295 and CloudEvents172 remain reserve exceptions.
50M/165947 is about301.30 corpus-equivalent passes, not sufficient unique supply.

Lineage024 resolves34 names (28 declared groups, two historical names and four
reserved names) with no current repository-ID or declared-fork-root cross-boundary
overlap. Detached copies, historical overlap, semantic duplication and pretraining
contamination remain unexcluded. No claim of statistical independence follows.

Preparation attempt001 caught an incorrect expected-token literal introduced while
adapting the prior script. The assertion stopped staging before assembly; corrected
attempt002 preserved the actual2850-target audit and assembled successfully. The
partial first staging remains separate. Production code and policies were unchanged;
no new full CPU suite or GPU test is claimed. Runpod was not used. P1 is incomplete.

Evidence: corpus033-integration-check-001, corpus033-supply-review-001,
training-corpus-publish-033, training-corpus-restore-033, training-corpus-denial-031,
and current-corpus-lineage-024. Corpus033 supersedes032 as the current quarantine
bundle. Next: broaden reviewed task supply and complete content-bound admission.

Corpus033 integration evidence archive: 26 files, 147,284 bytes, uploaded and remotely hash-verified (`corpus033-integration-publish-001/receipt.json`). The corpus itself is restore-tested; this separate evidence archive is not.


## Rally1469 scope resolution and capacity hold — October 10, 2026

The pinned issue and live upstream PR1469 identify the cleanup-default change.
The PR base SHA matches the task. Its four-file list excludes chart_generator.py,
which the dataset reference additionally changes from maximum to median. The
origin of that extra change is unproven; its omission is not classified as failure
of the issue's cleanup requirement. The full publisher reference and197-case
transition table remain intact for eventual runtime comparison. Static AST review
confirms the teacher's exact default change and forwarding into both connector
paths. This is not real connector execution or proof of leak mitigation.

Public source responses, pinned issue text, static checks and a concrete runtime
plan are retained under rally1469-upstream-scope-001 and rally1469-scope-review-001.
The runtime plan requires all197 publisher cases and real/static connector option
checks, session cleanup,39-call native replay, exact patch grading and token audit.
No performance gain is inferred from the publisher's relaxed timing tolerances.

Registry metadata is pinned without downloading layers: new compressed bytes
579,427,803; free host bytes3,215,695,872. Compressed sizes do not bound extraction.
The existing5GB acquisition guard is unmet, so image pull/runtime work did not
start. Next local infrastructure work is verified task-specific storage recovery;
Runpod remains unused. Corpus033 and all training-admission gates are unchanged.

Rally1469 scope evidence: 19 files, 95,609 bytes, published and remotely hash-verified in R2 (`rally1469-scope-publish-001/receipt.json`); this archive has not been restore-tested.


## Scoped Docker build-cache recovery — October 10, 2026

Removed six explicitly identified immutable/private/reclaimable records in the
ZenithSync Python3.7 build-cache chain, leaf first. Rechecked each record immediately
before deletion and required its read-only ID filter to select exactly one ID.
All six are absent afterward; all image and container IDs are unchanged. No model,
source dataset, evidence, image, container or volume was deleted. Other large
cache records lacked established project ownership and were preserved.

The first filter syntax was rejected before mutation; corrected documented syntax
was preview-checked. The largest selected record was reported as657.5MB. Host free
space changed asynchronously and was about3.5GiB in the follow-up df; this is not
an exact attribution of released bytes. The5GB acquisition guard remains unmet,
so Rally1469 was not pulled. Evidence: scoped-build-cache-cleanup-003. Runpod was
not used, corpus033 is unchanged, and P1 remains incomplete. Continue verified
local storage recovery before further large image acquisition.

Cleanup evidence: 10 files, 16,092 bytes, uploaded and remotely hash-verified in R2 (`scoped-build-cache-publish-003/receipt.json`); no restore test for this audit archive.


## Restore-test duplicate eviction — October 10, 2026

Allocation inspection found the repository's teacher Parquet shards cloud-backed
with zero currently allocated blocks; removing those paths would not meaningfully
recover host storage. The completed mini-source restore-test directory instead
held a resident428,839,266-byte duplicate shard. A fresh R2 publish/readback pass
verified the existing53-file431,730,739-byte manifest; the exact local shard hash
was rechecked, lsof showed no handles, and inode/size/mtime were checked before
unlinking this one duplicate. Original dataset paths and all other restore-test
files remain. The historical restore receipt remains valid evidence of the past
restore, but its directory is no longer complete and must be restored before reuse.

Evidence: restore-cache-eviction-001, including the pinned manifest and fresh
remote verification receipt. Host free bytes after eviction:4,168,867,840; still
below the5GB image acquisition guard. No Rally image was pulled, no GPU was used,
and corpus033/training gates are unchanged. An external-storage path question is
pending; do not infer authorization or an answer from elapsed time. Continue work
that fits local capacity and preserve unique data. P1 remains incomplete.

Restore-cache eviction audit:5 files,14,736 bytes uploaded and remotely hash-verified in R2 (`restore-cache-eviction-publish-001/receipt.json`); separate audit archive not restore-tested.


## Immutable evaluator and history parser inputs — October 10, 2026

Extended the existing verified_source_bytes helper to evaluator extraction and
replay-history construction. Both Parquet reads now consume the same SHA-256/size
verified immutable byte payload, capped at512MiB. Source provenance, reserved-repo
screening, identity-before-oracle/body access and final source/input drift checks
remain active. Receipts bind the snapshot helper and parsing mode. This avoids
reopening a changing source path inside the parser; it does not suppress metadata
hydration failures, bound arbitrary decompressed memory or promise error-free I/O.

Four new integration tests exercise both real Parquet readers: transient path
replacement between reads leaves the verified snapshot unchanged; corruption after
metadata inspection rejects before parsing; persistent post-read drift rejects
without emitting output; reserved repositories reject before snapshot/parsing.
The existing three snapshot tests also pass. Full local suite:426 tests,409 passed,
17 skipped. The original suite process was retained while cloud-backed Python
source hydration was requested; no retry was substituted for this passing result.

A fresh isolated runtime processed real SoftLayer inputs. All three evaluator
files and all three history/tools/mapping files match prior outputs byte-for-byte;
new receipts bind parser provenance. Prior runtime and evidence remain unchanged.
Evidence: evidence/p1/task-reader-snapshot-regression-001. Corpus033 remains current,
no training approval changed, no GPU used. P1 remains incomplete. Storage recovery
and broader data/admission work remain necessary before Rally image acquisition.

Task-reader code and validation archive:15 files,159,702 bytes uploaded and remotely hash-verified in R2 (`evidence/p1/task-reader-snapshot-publish-001/receipt.json`); separate archive not restore-tested.


## Recoverable image eviction and Rally1469 runtime qualification — October 10, 2026

The held flake8-fancy-header image had no container references or derived images.
Its pinned registry descriptor was verified live before nonforced exact-reference
removal. The initial RepoTags check rejected Docker's digest-as-tag representation;
inspection confirmed the sole entry was the same pinned reference. All other image
IDs and all container IDs stayed unchanged. Model/data/evidence files were preserved;
the exact pull recipe is recorded. Recovery depends on registry availability, not
an image-byte backup in R2. Free bytes rose4,124,770,304 to5,714,190,336. Eviction
receipt: fancyheader-image-eviction-001; audit archive6files28,923bytes remotely
hash-verified in R2, not restore-tested.

The recovered capacity passed the unchanged5GB acquisition guard. Rally's pinned
image pulled successfully; free bytes afterward3,889,389,568. Its base checkout
matched and PR-head commit was explicitly absent. Snapshot verification preserved
241tracked files, one reachable commit, and absence of known evaluator paths.
Inherited image layers are outside the mounted-filesystem audit. Python3.9.21,
pytest6.2.5 and exact esrally.async_connection source origin were verified.

All197 publisher cases reproduce: base196/197, reference and teacher197/197.
Twelve real object cases cross absent/True/False cleanup options, static/TCP
connectors and use_ssl False/True. Both fixes pass12/12; base fails four default
cases. Tests check policy, connector class, timer setup, session/connector close,
timer cancellation and no remaining asyncio tasks. No network requests or TLS
handshake occur. Do not claim leak prevention or performance gains from these tests.

Evidence: rally1469-runtime-review-001, rally1469-controls-001 and
rally1469-semantic-controls-001. Native39-call replay, exact patch grading, token
qualification and integration remain pending. Corpus033 is unchanged; Runpod was
not used. P1 remains incomplete. No production change or new full CPU suite here.

Rally runtime evidence:108files989,017bytes uploaded and remotely hash-verified in R2 (`rally1469-runtime-publish-001/receipt.json`); this archive is not restore-tested. All six publisher/semantic test containers have successful cleanup receipts.


## Rally1469 native replay: mechanical pass, content hold — October 10, 2026

Replay completed39 charged calls,82 messages and40 exchanges with no tool-error
events. The2185-byte two-file patch updates code and its documentation; independent
exact-patch grading matches197/197 publisher cases. The last native test command
reports13 passed. Untruncated audit:21320 input/4638 supervised tokens, reserve
margin3256; mechanical linkage, grading and budget checks pass, training=false.

Content review independently holds the original trajectory: event78 creates a
script that only checks connection attributes but prints TLS1.3/Elasticsearch
memory-leak prevention; event80 runs it successfully. Observed stdout is not proof
of that inference. The unsupported script text is an assistant tool argument and
therefore relevant to supervised labels even though tool responses are masked.
No TLS exchange, affected server, repeated-cycle memory measurement or sustained
leak test supports the claim. Do not admit this original to corpus033. A corrected,
explicitly authored and freshly replayed derivative must preserve provenance and
meet budgets; silently editing old actions/observations is not acceptable.

Evidence: rally1469-observation-review-001, including exact claim-producing events,
rally1469-standard-grade-001 and rally1469-mechanical-admission-001. The first
new-runtime tokenizer call lacked model-intake metadata; the established pinned
runtime completed successfully. No model weights/GPU used, no production changes,
no new full CPU suite. Corpus033 and P1 admission remain unchanged/incomplete.

Rally native/content-hold archive:53files1,277,020bytes uploaded and remotely hash-verified in R2 (`rally1469-native-publish-001/receipt.json`); not restore-tested. Corpus033 still contains29 tasks and excludes Rally1469.


## Corpus033 claim review, first detailed batch — October 11, 2026

Screen resolved29/29 exact histories,44 lexical spans in23 histories. All44
excerpts were triaged; only four histories received detailed contextual review in
this batch. Negated guarantees and conditional success messages are not automatic
failures. Signac622 and Lenskit312 original histories require claim correction
before promotion. Lenskit recorded equal1.0 scores followed by a hard-coded
inequality sentence; Signac's summary claims all functionality preserved despite
only finite checks. Lmfit487 complete-fix wording remains under scope review.
Boltons205's three recorded comparisons are true despite weak unconditional
success control flow. Full histories and selected messages are hash-bound in
corpus033-claim-review-001. Later bounded checks were considered, not ignored;
they do not remove earlier supervised claims. No source history, corpus, label,
or admission receipt changed. No fresh runtime execution or production-code
change; no GPU or large download. Review is incomplete and P1 remains active.

Claim review archive: 9 files, 382,108 bytes uploaded, remotely hash-verified, and independently restored from R2 (`corpus033-claim-review-publish-003`, `corpus033-claim-review-restore-001`). Two earlier inventory attempts rejected cloud hydration metadata changes; explicit hydration allowed the unchanged integrity checks to pass. Four full-history hashes and every selected-message binding were independently verified.


## Corpus033 claim review, second contextual batch — October 11, 2026

Reviewed selected flagged claims and execution context in six additional histories:
Statsmodels8339, Emcee295, Numba6653, Werkzeug2971, Dynaconf413 and Gitignore38.
This brings distinct contextual reviews to 10, not full semantic approvals.
Emcee's initial walker-count failure precedes an explicit setup correction and a
computed True result. Gitignore's failed comprehensive diagnostic never reaches
its success print; later finite edge checks pass. Numba and Werkzeug successes
are guarded by real comparisons/assertions. Statsmodels' five-test summary is
conditional, but the later shape-printing smoke check is not numerical validation.
Preserve these distinctions rather than classify every success phrase as false.
Numba's deprecated-fallback title is misleading despite a correctly documented
ignored-variable expectation in the body; note it for derivative cleanup.

A recursive argument-value screen found zero nested string leaves in all 29 exact
histories; no additional matches under the existing patterns. This closes only
that structural coverage question, not semantic review. Six history identities
and 39 selected-message bindings independently verified. No production code,
corpus contents or training approval changed; no GPU or fresh runtime replay.
Evidence: corpus033-claim-review-002. Earlier original-history holds remain open.

Second review archive: 14 files, 489,332 bytes uploaded and remotely hash-verified, then independently restored from R2 (`corpus033-claim-review-publish-004`, `corpus033-claim-review-restore-002`). Production tests were not rerun for this evidence-only review; no new runtime qualification is claimed.


## Corpus033 claim review, third contextual batch — October 11, 2026

Reviewed selected claim contexts in Datetransform2, Jsons86, Munch52, Importlab23,
Apispec950 and Numkit8: 16 distinct histories across three batches. Datetransform
has a swallowed exception branch, but its recorded empty-frame call succeeded.
Jsons explicitly denies a universal guarantee. Munch's optional-dependency skip
branch was not taken. Importlab initially fails two expectations, then explicitly
changes them before a passing rerun; the revised expectations still need independent
contract justification. Apispec checks seven schema mappings but does not propagate
its Boolean return into process exit status. Actual recorded comparisons pass.

Numkit's nine finite odd-window division comparisons pass. Exact algebra proves
(w-1)//2=k and -(w-1)//2=-k for w=2k+1. A separate local arithmetic check at
k=2**54+1 demonstrates that floating true division rounds down by one, so the
small-case float equality cannot be generalized to arbitrary integers. This is an
arithmetic scope boundary, not a feasible huge-array test or a smoothing defect.
Full original histories and selected messages are preserved and hash-verified in
corpus033-claim-review-003. No original history, corpus, production code or training
approval changed. No GPU or fresh candidate replay. Prior content holds remain.

Third review archive: 14 files, 537,989 bytes uploaded and remotely hash-verified, then independently restored from R2 (`corpus033-claim-review-publish-006`, `corpus033-claim-review-restore-003`). Initial packaging rejected a cloud-hydrated screen.py metadata change; explicit hydration and a fresh stage passed the unchanged integrity checks. Six source histories and 26 selected-message bindings verified. Evidence-only work did not rerun the production suite.


## Corpus033 lexical-context pass and correction queue — October 11, 2026

Fourth batch reviews Workalendar493, PennyLane5716/5831, PySyft250,
CloudEvents172, Csaps3 and ASDF1853. Coverage verification initially rejected six
omitted message contexts from the first batch; those were read with execution
observations and preserved in an additive supplement, leaving old reports intact.
Consolidation now verifies all 44 matched spans across 23 flagged histories and
145 exact selected-message bindings. Six unflagged histories are not approved by
absence of matches. Full semantic review remains outstanding for every history.

PennyLane5716's first run reports 6/7 despite zero exit status; later 8/8 omits the
multi-batch case and only samples decomposition parameters. PennyLane5831's failed
matrix-call diagnostic is preserved before its explicit correction. CloudEvents
names transitivity without a triple/implication check, and broad preservation
wording exceeds the finite tests: original joins Signac/Lenskit in the claim-
correction queue. ASDF's guarantee phrase is an explicit limitation and its exact-
tag enumeration records 1024 cases, zero mismatches. Selected finite successes
remain evidence; they do not erase earlier supervised overclaims.

Correction queue records three original-history claim holds, two scope/contract
reviews, six diagnostic-quality follow-ups, and other selected-context or no-match
states. It is not loader enforcement or admission approval. Existing quarantine
continues to block training. No production code, corpus, model or original history
changed; no GPU or fresh candidate runtime execution. No production-suite rerun for
this evidence-only review. Next work: resolve claims with explicit replayed
derivatives and independent contract evidence, plus broader semantic review.

Complete review-chain archive: 47 files, 1,993,596 bytes uploaded and remotely hash-verified, then independently restored from R2 (`corpus033-claim-review-publish-008`, `corpus033-claim-review-restore-004`). All correction-queue source identities also verified against restored report files. Initial stage007 rejected cloud hydration metadata change; stage008 passed the same integrity guard.


## Explicit action amendment primitive and Lenskit derivative — October 11, 2026

Added zenithsync/replay_amendment.py: validates explicit assistant authorship,
canonical source and derived action-list identities, ordered unique amendment
ordinals, exact text preimages, and only whole shell-command/create-text changes.
Deep-copy construction preserves caller inputs, action order, metadata and paths.
This is provenance machinery, not a command sandbox; callers still require source
preflight, fresh native execution and full qualification. No observations are
accepted or emitted. Five focused tests cover tampering, forged/invalid fields,
no-op changes, duplicate indices, source immutability and shell amendments.
Full local suite: 431 tests, 414 pass, 17 skipped.

Lenskit prepared derivative changes three diagnostic create actions (10,20,27):
compute reproduction comparisons and remove overbroad/static success narration.
All three diagnostic scripts compile; source repair action13 is unchanged.
Original histories/actions are retained. Local snapshot image is available.
Native driver and history projection do not yet consume amendment plans; reconcile
original completion binding and add replay provenance checks before any execution
or training use. Evidence: lenskit312-claim-amendment-001 and
p1/action-amendment-regression-001. No Runpod, model update or fresh replay occurred.

Action-amendment archive: 10 files, 110,055 bytes uploaded and remotely hash-verified, then restored successfully from R2 (`action-amendment-publish-002`, `action-amendment-restore-001`). First packaging attempt rejected cloud hydration metadata drift; a fresh stage passed the unchanged inventory guard.


## Native amendment integration and fresh Lenskit replay — October 11, 2026

Native replay now accepts explicit amendment plans, preserves original-actions.json,
checks credentials on derived text, and binds plan/module/original/derived bytes.
History projection verifies changed native tool arguments, source event order and
counts; completion must bind derived actions, with separate authorship mappings.
Tests reject original calls relabeled as amended, changed paths, missing events,
wrong ordering and original-action completion bindings. A task-reader integration
test exercises actual history projection and rejects substituted command evidence.

Full suite: 435 tests, 418 pass, 17 skip. Earlier focused/full runs hit inventory
metadata guards while macOS hydrated source files; failed full run001 is preserved,
and hydrated run002 passed without disabling guards. Fresh isolated runtime used
the existing Lenskit image, no new image download or Runpod. Native replay completed
26 charged calls; exact548-byte patch matches the prior repair, cleanup verified.
One original test command again times out at30seconds and is preserved. Completion
records5850 finite metric cases,4875 suffix checks, max error1.1102230246251565e-16.
History:56messages27exchanges, three separately attributed amended actions. Token
audit:19836input5644supervised,4740reserve margin after8192 output tokens.

Evidence: lenskit312-amended-native/history/tokens/review-001 and
p1/action-amendment-integration-regression-002. Prepared claim amendment001 remains
historical. Independent derivative grading, mechanical admission and full content
review are pending. Corpus033 is unchanged and training remains denied.

Amendment integration/fresh replay archive: 26 files, 669,139 bytes uploaded and remotely hash-verified, then restored successfully from R2 (`lenskit312-amended-publish-002`, `lenskit312-amended-restore-001`). Initial archive attempt rejected preserve.py cloud hydration metadata drift; fresh stage passed unchanged integrity checks.
