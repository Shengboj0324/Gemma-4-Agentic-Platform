# Complete code, configuration and test catalog

Generated from the current checkout. Presence/docstrings are not proof of qualification.
See `code-inventory.json` for hashes and `symbols.json` for every parsed class/function in materialized files,
including test methods and line numbers. Tests describe intended checks, not results.

## [zenithsync/__init__.py](../../zenithsync/__init__.py)

Development-side contracts for the Gemma repository agent.

Size: 88 bytes. Materialized: True.

## [zenithsync/__main__.py](../../zenithsync/__main__.py)

Offline inspection CLI. Results go to stdout; inputs are never modified.

Size: 2767 bytes. Materialized: True.

## [zenithsync/action_training.py](../../zenithsync/action_training.py)

Experimental causal next-action supervision, separate from corpus admission.

Size: 3103 bytes. Materialized: True.

## [zenithsync/adapter_checkpoint.py](../../zenithsync/adapter_checkpoint.py)

Adapter-only resume contract over an independently verified frozen base.

Assumes a quiescent single-process model with immutable persistent frozen state.
Nonpersistent buffers must be deterministically reconstructed by the worker.

Size: 6401 bytes. Materialized: True.

## [zenithsync/architecture_layout.py](../../zenithsync/architecture_layout.py)

Exact descriptor coverage for the supported dense Gemma4 W4 checkpoint.

Size: 2580 bytes. Materialized: True.

## [zenithsync/archive.py](../../zenithsync/archive.py)

ZIP structural preflight only; official YAML/ADK validation is unresolved.

Size: 3310 bytes. Materialized: True.

## [zenithsync/artifacts.py](../../zenithsync/artifacts.py)

Portable local inventory and verification for quiescent artifact directories.

Not a sandbox for concurrently malicious filesystem writers. Supply an owned,
stable staging directory. Symlinks and nonregular entries are rejected.

Size: 5585 bytes. Materialized: True.

## [zenithsync/checkpoint_storage.py](../../zenithsync/checkpoint_storage.py)

Atomic, no-overwrite checkpoint files for owned POSIX directories.

Only deserialize trusted, independently hash-bound local training artifacts.
This storage layer does not validate model/optimizer/cursor semantic compatibility.

Size: 4151 bytes. Materialized: True.

## [zenithsync/container_cleanup.py](../../zenithsync/container_cleanup.py)

Observable cleanup for an explicitly owned container; uncertainty is retained.

Size: 660 bytes. Materialized: True.

## [zenithsync/contracts.py](../../zenithsync/contracts.py)

Pure contracts; no model, tool execution, or evaluator outcomes are invented.

Size: 7437 bytes. Materialized: True.

## [zenithsync/conversation.py](../../zenithsync/conversation.py)

Validated text-only tool history for the supplied Gemma chat template.

This normalizes transport syntax and call/result linkage. Tool-specific argument
schemas, execution authorization and generated Gemma-token parsing are separate.

Size: 6644 bytes. Materialized: True.

## [zenithsync/corpus_credentials.py](../../zenithsync/corpus_credentials.py)

Credential-indicator screening of complete decoded corpus inputs.

This finite rule screen is review evidence, not a privacy guarantee or an
admission decision. It includes prompts, observations and assistant text; it
never redacts immutable training examples or returns matched values.

Size: 2874 bytes. Materialized: True.

## [zenithsync/corpus_optimization.py](../../zenithsync/corpus_optimization.py)

Single-device token-mean update over separately attended microbatches.

The model must return mean causal loss over labels[..., 1:] != -100, with no
auxiliary loss. This contract is tested separately for each model backend.
No distributed reduction, AMP scaler, clipping or learning-rate schedule here.

Size: 5901 bytes. Materialized: True.

## [zenithsync/corpus_run.py](../../zenithsync/corpus_run.py)

CPU-only admission and configuration checks for the full-model corpus worker.

Size: 3240 bytes. Materialized: True.

## [zenithsync/corpus_training.py](../../zenithsync/corpus_training.py)

Bridge admitted indexed examples to one-example-at-a-time optimizer updates.

Size: 3358 bytes. Materialized: True.

## [zenithsync/deadline.py](../../zenithsync/deadline.py)

POSIX main-thread deadline for bounded diagnostic I/O.

This interrupts Python/socket waits, not arbitrary uninterruptible native code
or remote GPU billing. The serving process has its own session supervisor.

Size: 1308 bytes. Materialized: True.

## [zenithsync/evaluation.py](../../zenithsync/evaluation.py)

Strict paired JUnit accounting, not a benchmark solve or significance test.

Tests from one repository task are dependent observations. Counts here must not
be interpreted as independent task samples or evidence of generalization.

Size: 3471 bytes. Materialized: True.

## [zenithsync/gemma_training.py](../../zenithsync/gemma_training.py)

Exact-shape LoRA attachment for the full Gemma corpus worker.

Size: 1483 bytes. Materialized: True.

## [zenithsync/gemma_trajectory.py](../../zenithsync/gemma_trajectory.py)

Explicit source-text projection into Gemma's pre-action channel.

This is a transport convention, not a claim that source content was originally
a private reasoning field. Source records and transformation hashes must remain
available. It changes no tool name, argument value, call ID or result text.

Size: 1976 bytes. Materialized: True.

## [zenithsync/go_test_controls.py](../../zenithsync/go_test_controls.py)

Strict qualification of native Go 1.23 test JSON, without invented phases.

The caller supplies complete ``go test -json -count=1`` output and its process
exit code. These checks validate recorded event consistency, not log authenticity
or source immutability; the execution bundle must bind those independently.
Package-only skips require an explicit reviewed no-test-package allowlist.

Size: 8300 bytes. Materialized: True.

## [zenithsync/gpu_memory.py](../../zenithsync/gpu_memory.py)

Device-wide sampled memory telemetry, distinct from allocator peak counters.

Size: 4801 bytes. Materialized: True.

## [zenithsync/harness_context.py](../../zenithsync/harness_context.py)

Local evaluation settings matching the acquired competition README section 7.2.

These settings delegate to ADK; they do not implement a custom compactor or
guarantee that its summaries preserve tool observations. Hidden-grader parity
and long-context behavior require separate evidence.

Size: 948 bytes. Materialized: True.

## [zenithsync/inference_capture.py](../../zenithsync/inference_capture.py)

Bounded, loopback-only diagnostic capture for nonstreaming inference.

The sole request change asks vLLM to return raw generated token IDs. The original
and forwarded JSON bodies are both retained; response bytes pass through unchanged.
Use only with curated development inputs: bodies may contain repository contents.

Size: 5227 bytes. Materialized: True.

## [zenithsync/inference_probe.py](../../zenithsync/inference_probe.py)

Acceptance checks for a real generated tool call, not a simulated model.

Size: 2568 bytes. Materialized: True.

## [zenithsync/issue_contract.py](../../zenithsync/issue_contract.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5286 bytes. Materialized: False.

## [zenithsync/issue_similarity.py](../../zenithsync/issue_similarity.py)

Exact lexical overlap signals, never semantic or split admission decisions.

Positive thresholds let an inverted index omit zero-intersection pairs without
changing the answer. NFKC/case/whitespace normalization is an explicit heuristic:
it can change code semantics. Short issues use their complete token tuple.

Size: 5354 bytes. Materialized: True.

## [zenithsync/junit_controls.py](../../zenithsync/junit_controls.py)

Strict Maven Surefire XML outcomes; execution provenance is a separate gate.

Only UTF-8, single-suite reports without retries are supported. Missing reports
(e.g. compilation failures) are not converted into fabricated failed test cases.
Skipped cases remain explicit and cannot establish a fail-to-pass transition.

Size: 7791 bytes. Materialized: True.

## [zenithsync/legacy_matrix_probe.py](../../zenithsync/legacy_matrix_probe.py)

Exact historical evaluator body for read-only receipt verification.

Uses Python 3.7+ subprocess aliases; current execution uses the current probe.
Do not normalize unknown program bodies into this accepted historical version.

Size: 3640 bytes. Materialized: True.

## [zenithsync/matrix_admission_evidence.py](../../zenithsync/matrix_admission_evidence.py)

Compose matrix outcomes, known probes and replay/task provenance checks.

Size: 8813 bytes. Materialized: True.

## [zenithsync/matrix_grade_evidence.py](../../zenithsync/matrix_grade_evidence.py)

Recompute publisher matrix outcomes from explicitly hash-bound files.

This verifies local evidence consistency, not provenance or training admission.
Probe reconstruction and patch/snapshot binding remain separate requirements.

Size: 5309 bytes. Materialized: True.

## [zenithsync/matrix_probe_contract.py](../../zenithsync/matrix_probe_contract.py)

Bind recorded matrix probes to the known evaluator and exact task inputs.

Parse literal settings without executing the stored program. Snapshot and
publisher provenance must still be checked by the admission caller.

Size: 3684 bytes. Materialized: True.

## [zenithsync/maven_compile_controls.py](../../zenithsync/maven_compile_controls.py)

Recognize bounded Maven test-compilation missing-symbol controls.

This is a deliberately explicit log profile, not log authentication or a Java
compiler proof. The caller must bind fresh execution, source and test bytes.
A compile failure has no runtime testcase outcomes.

Size: 9181 bytes. Materialized: True.

## [zenithsync/maven_grade_bundle.py](../../zenithsync/maven_grade_bundle.py)

Reconstruct Maven phase controls from bound artifacts; never admit training.

Size: 6897 bytes. Materialized: True.

## [zenithsync/mini_replay_admission.py](../../zenithsync/mini_replay_admission.py)

Cross-check V2 replay evidence; never authorize training from local receipts.

Size: 20401 bytes. Materialized: True.

## [zenithsync/mini_replay_amendment.py](../../zenithsync/mini_replay_amendment.py)

Derive explicit mini-trace command amendments without reusing observations.

Size: 2622 bytes. Materialized: True.

## [zenithsync/mini_source_history.py](../../zenithsync/mini_source_history.py)

Serialize inspected Open-SWE mini histories without claiming native semantics.

Size: 4036 bytes. Materialized: True.

## [zenithsync/mocha_controls.py](../../zenithsync/mocha_controls.py)

Validate complete Mocha JSON reports, not log authenticity or test quality.

This profile rejects pending tests, retries, duplicate full titles and hook-only
failures. Execution provenance and source integrity must be bound separately.
Publisher short titles must be resolved explicitly before comparison.

Size: 7360 bytes. Materialized: True.

## [zenithsync/model_intake.py](../../zenithsync/model_intake.py)

Bounded, CPU-only inspection of checkpoint storage, without loading weights.

This checks byte layout, not numerical weight validity or loader compatibility.
Inputs must be in an owned, quiescent directory (as with artifacts.inventory).
Unknown dtypes are rejected rather than assigned a guessed storage width.

Size: 5148 bytes. Materialized: True.

## [zenithsync/object_store.py](../../zenithsync/object_store.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6871 bytes. Materialized: False.

## [zenithsync/offline_resources.py](../../zenithsync/offline_resources.py)

Explicit evaluator-only replay of immutable HTTP response bodies.

This adapter is a qualification aid, not a general HTTP cache. It supports
only body reads through urllib.urlopen and requests.get. Unknown resources
and request options fail closed; production/agent networking is unaffected.

Size: 3431 bytes. Materialized: True.

## [zenithsync/optimizer_checkpoint.py](../../zenithsync/optimizer_checkpoint.py)

Identity-checked single-group AdamW checkpoint contract.

Scope: dense, non-AMSGrad AdamW with a state entry for every trainable tensor.
RNG, data-cursor and scheduler recovery are separate resume requirements.

Size: 5035 bytes. Materialized: True.

## [zenithsync/probe_receipt.py](../../zenithsync/probe_receipt.py)

Bind successful local container receipts to reconstructed probe bytes.

This checks consistency of retained local evidence, not cryptographic
attestation that an untrusted author actually ran a container.

Size: 1971 bytes. Materialized: True.

## [zenithsync/process_supervisor.py](../../zenithsync/process_supervisor.py)

Bound an owned POSIX process group; never manages cloud billing.

Children must remain in the inherited process group. This is lifecycle control
for trusted workers, not confinement against processes that detach themselves.

Size: 5459 bytes. Materialized: True.

## [zenithsync/pytest_applicability.py](../../zenithsync/pytest_applicability.py)

Interpret a deliberately small, auditable pytest version-condition language.

This is not Python execution. It supports direct django.VERSION comparisons
against integer tuples in top-level pytest.mark.skipif decorators. Callers must
bind the source bytes, module path and actual runtime version independently.

Size: 5612 bytes. Materialized: True.

## [zenithsync/pytest_controls.py](../../zenithsync/pytest_controls.py)

Strict paired-control checks retaining full pytest parameter identities.

Publisher whitespace-truncated names are matched as groups. Every member must
agree with the expected transition; last-write-wins collapse is never used.

Size: 5484 bytes. Materialized: True.

## [zenithsync/pytest_matrix.py](../../zenithsync/pytest_matrix.py)

Reconcile explicit version-dependent pytest obligations without counting skips.

Applicability is caller-supplied reviewed evidence, not inferred from outcomes.
This checks outcome structure and repair behavior only; callers must separately
bind runtime versions, test predicates, source/patch identities and provenance.
It does not grant corpus or training admission.

Size: 7919 bytes. Materialized: True.

## [zenithsync/qualification_sampling.py](../../zenithsync/qualification_sampling.py)

Deterministic repository coverage sampling, not an agent benchmark sample.

Size: 2699 bytes. Materialized: True.

## [zenithsync/quantized_layout.py](../../zenithsync/quantized_layout.py)

Dimension contracts for dense Gemma4 W4/group-32 text projections.

Scope deliberately excludes MoE, per-layer inputs, biases and shared KV layers.
These checks do not execute compressed-tensors unpacking or model inference.

Size: 4252 bytes. Materialized: True.

## [zenithsync/rebench_grade_evidence.py](../../zenithsync/rebench_grade_evidence.py)

Recompute a recorded SWE-rebench grade from hash-bound pytest outcomes.

Size: 2363 bytes. Materialized: True.

## [zenithsync/replay_admission.py](../../zenithsync/replay_admission.py)

Cross-check replay evidence before rights, split, and GPU admission reviews.

This verifies local evidence consistency, not the truth of arbitrary supplied
receipts. It never approves training or treats a replay as a new model result.

Size: 10790 bytes. Materialized: True.

## [zenithsync/replay_amendment.py](../../zenithsync/replay_amendment.py)

Construct explicitly attributed action derivatives; never reuse observations.

This is a provenance primitive, not a command sandbox or replay qualification.
Callers must preflight source actions and execute the derivative in a fresh runtime.

Size: 8714 bytes. Materialized: True.

## [zenithsync/replay_completion.py](../../zenithsync/replay_completion.py)

Explicit assistant-authored completion actions before native submission.

Size: 4507 bytes. Materialized: True.

## [zenithsync/replay_correction.py](../../zenithsync/replay_correction.py)

Explicit, hash-bound correction plans; no invented observations or admission.

Size: 4032 bytes. Materialized: True.

## [zenithsync/replay_history.py](../../zenithsync/replay_history.py)

Project captured native exchanges without inventing reasoning or observations.

Size: 6343 bytes. Materialized: True.

## [zenithsync/replay_noop.py](../../zenithsync/replay_noop.py)

Verify a rejected identical edit without replacing its native observation.

Size: 3009 bytes. Materialized: True.

## [zenithsync/replay_observations.py](../../zenithsync/replay_observations.py)

Inventory replay observations without converting tool success into correctness.

Size: 3895 bytes. Materialized: True.

## [zenithsync/replay_resources.py](../../zenithsync/replay_resources.py)

Stage explicitly pinned public resource responses in a disposable sandbox.

Size: 2732 bytes. Materialized: True.

## [zenithsync/resource_replay_binding.py](../../zenithsync/resource_replay_binding.py)

Verify a recorded Session environment without approving its training use.

Size: 2564 bytes. Materialized: True.

## [zenithsync/review_coverage.py](../../zenithsync/review_coverage.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3987 bytes. Materialized: False.

## [zenithsync/serving.py](../../zenithsync/serving.py)

CPU-only validation of the versioned P1 serving profile.

Size: 3147 bytes. Materialized: True.

## [zenithsync/session_report.py](../../zenithsync/session_report.py)

Independent schedule/accounting verification of a completed worker report.

This establishes checkpoint and schedule consistency, not numerical training
quality. The caller supplies an independently hash-bound checkpoint reader.

Size: 5302 bytes. Materialized: True.

## [zenithsync/session_resource_bundle.py](../../zenithsync/session_resource_bundle.py)

Load explicitly reviewed response bundles for offline Session replay.

Hashes establish byte identity, not authenticity, rights, or training admission.
All validation finishes before a caller receives a transport payload.

Size: 6878 bytes. Materialized: True.

## [zenithsync/session_resource_replay.py](../../zenithsync/session_resource_replay.py)

Exact public UTF-8 response replay for disposable, offline test processes.

This supports successful body reads through requests Sessions, not arbitrary
HTTP behavior. It does not reproduce TLS, cookies, redirects, hooks or timing.
Install only in an isolated process; restoration is not concurrency-safe.

Size: 4488 bytes. Materialized: True.

## [zenithsync/source_base.py](../../zenithsync/source_base.py)

Normalize an owned disposable checkout; retain history for later sanitization.

Size: 2293 bytes. Materialized: True.

## [zenithsync/source_bytes.py](../../zenithsync/source_bytes.py)

Bounded immutable input snapshots for parsers that otherwise reopen files.

Size: 1095 bytes. Materialized: True.

## [zenithsync/source_capture.py](../../zenithsync/source_capture.py)

Bounded export of selected committed blobs; never a rights approval.

Size: 4616 bytes. Materialized: True.

## [zenithsync/source_credentials.py](../../zenithsync/source_credentials.py)

Conservative source-text credential indicators, never credential validation.

Reports contain only rule names and character locations. Absence of indicators
is not proof of absence of secrets; flagged examples require review, not silent
redaction that would break trajectory provenance.

Size: 4124 bytes. Materialized: True.

## [zenithsync/source_evaluator.py](../../zenithsync/source_evaluator.py)

Compare source expectations without dropping colliding test identities.

Size: 2374 bytes. Materialized: True.

## [zenithsync/source_http_fixture.py](../../zenithsync/source_http_fixture.py)

Loopback-only scripted HTTP fixture; never evidence of model capabilities.

Size: 3858 bytes. Materialized: True.

## [zenithsync/source_imports.py](../../zenithsync/source_imports.py)

Validate explicit checkout-relative import roots for offline Python runtimes.

Size: 721 bytes. Materialized: True.

## [zenithsync/source_runner_fixture.py](../../zenithsync/source_runner_fixture.py)

Scripted ADK lifecycle fixtures. Never use as training or model evidence.

Size: 3447 bytes. Materialized: True.

## [zenithsync/source_snapshot.py](../../zenithsync/source_snapshot.py)

Create a fresh Git history while preserving an exact base tree.

Run only in a disposable build container or an explicitly owned test fixture.
This removes known oracle paths; it does not certify arbitrary image contents.

Size: 9096 bytes. Materialized: True.

## [zenithsync/source_task.py](../../zenithsync/source_task.py)

Agent-visible source task projection, separate from evaluator metadata.

Size: 1927 bytes. Materialized: True.

## [zenithsync/source_task_metadata.py](../../zenithsync/source_task_metadata.py)

Project source task identities without exporting reference fixes or tests.

These records describe publisher metadata, not verified runnable environments.
Image tags remain untrusted mutable references until resolved and inspected.

Size: 6778 bytes. Materialized: True.

## [zenithsync/source_test_risk.py](../../zenithsync/source_test_risk.py)

Conservative review hints for Python test snippets, never admission decisions.

Only supplied Python text is parsed. No code executes and no correctness claim
is inferred from missing findings. Locations refer to the original snippet.

Size: 2215 bytes. Materialized: True.

## [zenithsync/source_workspace.py](../../zenithsync/source_workspace.py)

Prepare a qualified source snapshot for native /workspace tool semantics.

Size: 3672 bytes. Materialized: True.

## [zenithsync/splits.py](../../zenithsync/splits.py)

Validate declared split isolation; semantic contamination needs a later audit.

Size: 5437 bytes. Materialized: True.

## [zenithsync/static_controls.py](../../zenithsync/static_controls.py)

Compare bounded mypy text diagnostics without conflating existing and new errors.

This supports the explicit noncolored, error-code-bearing mypy output profile
used by our offline evaluator. Unknown output or inconsistent exit status rejects.
It does not infer runtime correctness or approve a training example.

Size: 3057 bytes. Materialized: True.

## [zenithsync/submission_reconciliation.py](../../zenithsync/submission_reconciliation.py)

Plan explicit scratch cleanup only when tracked repair bytes already agree.

This module never deletes files, stages changes, executes a source command, or
approves a training example. The caller must expose any subsequent cleanup as
an adapter-authored native action and reverify the submitted patch afterward.

Size: 6539 bytes. Materialized: True.

## [zenithsync/synthetic_admission.py](../../zenithsync/synthetic_admission.py)

Consistency checks for assistant-authored native trajectories.

Synthetic captures retain their own provenance; they are never relabeled as
teacher replays. Passing these checks does not authorize training.

Size: 10446 bytes. Materialized: True.

## [zenithsync/task_intake.py](../../zenithsync/task_intake.py)

Strict official-task projection: evaluator patches never enter agent inputs.

Size: 3491 bytes. Materialized: True.

## [zenithsync/tool_diagnostic.py](../../zenithsync/tool_diagnostic.py)

Independent, strict grammar check for two-string native Gemma write calls.

Diagnostic only: not a replacement production parser. Inputs containing native
delimiter tokens as literal file content are outside this experiment's grammar.

Size: 2659 bytes. Materialized: True.

## [zenithsync/training_batch.py](../../zenithsync/training_batch.py)

Validated right-padding for independently masked causal training examples.

No truncation or concatenation: examples remain separate attention sequences.
Loss normalization counts supervised next-token targets, not padded positions.

Size: 2486 bytes. Materialized: True.

## [zenithsync/training_corpus.py](../../zenithsync/training_corpus.py)

Hash-bound corpus loading; integrity checks are separate from training admission.

Receipts are local reviewed evidence, not cryptographic proof of their truth.
Operate on a quiescent, owned directory, not an adversarial concurrent filesystem.

Size: 16571 bytes. Materialized: True.

## [zenithsync/training_fixture.py](../../zenithsync/training_fixture.py)

Native-tokenized qualification input, explicitly separate from training data.

Size: 1736 bytes. Materialized: True.

## [zenithsync/training_masks.py](../../zenithsync/training_masks.py)

Instrument the supplied Gemma template without changing rendered content.

Only this audited template layout is supported. Generation annotations label
assistant reasoning/calls/content and terminal markers, never tool results.

Size: 5635 bytes. Materialized: True.

## [zenithsync/training_pilot.py](../../zenithsync/training_pilot.py)

One-update qualification engine; not a corpus trainer or performance claim.

Size: 8161 bytes. Materialized: True.

## [zenithsync/training_rng.py](../../zenithsync/training_rng.py)

Process RNG checkpoints for quiescent CPU or CUDA training.

Includes Python, NumPy's legacy global generator, and Torch global generators.
Custom Generator objects and data-loader workers require their own checkpoints.
Restoration must occur after model/optimizer construction and before training.

Size: 4402 bytes. Materialized: True.

## [zenithsync/training_schedule.py](../../zenithsync/training_schedule.py)

Deterministic whole-example updates with exact supervised-token accounting.

Hash ordering is a reproducible shuffle rule, not a claim of statistical
independence. Repeated epochs are repeated exposures, not new training data.

Size: 5724 bytes. Materialized: True.

## [zenithsync/training_session.py](../../zenithsync/training_session.py)

Single-process corpus training with explicit budgets and durable update boundaries.

The caller constructs and verifies the model/runtime and uses an external hard
deadline supervisor. This loop's wall limit is checked only between updates.

Size: 5817 bytes. Materialized: True.

## [zenithsync/training_state.py](../../zenithsync/training_state.py)

Bounded-copy state fingerprints for quiescent, single-process training.

These fingerprints detect byte changes; they do not establish numerical quality.
Call only between completed model operations, with no concurrent state writers.

Size: 3043 bytes. Materialized: True.

## [zenithsync/trajectory_import.py](../../zenithsync/trajectory_import.py)

Strict SWE-Hero serialization conversion; not a tool-semantic adapter.

Response linkage is inferred only from a single outstanding source call.
Inferred linkage never establishes that a command ran or an issue was solved.

Size: 3456 bytes. Materialized: True.

## [zenithsync/transfer_evidence.py](../../zenithsync/transfer_evidence.py)

Retain transfer receipts outside the immutable artifacts they describe.

Use quiescent, owned directories. Receipt contents are audit evidence, not
cryptographic proof of a remote service; both local trees are verified here.

Size: 3080 bytes. Materialized: True.

## [zenithsync/v2_synthetic_admission.py](../../zenithsync/v2_synthetic_admission.py)

Bind synthetic captures, publisher controls, content review and token audits.

Mechanical qualification never changes a corpus or grants training approval.

Size: 10952 bytes. Materialized: True.

## [scripts/acquire_official_wheels.py](../../scripts/acquire_official_wheels.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5006 bytes. Materialized: False.

## [scripts/assemble_training_corpus.py](../../scripts/assemble_training_corpus.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4494 bytes. Materialized: False.

## [scripts/assess_mini_replay.py](../../scripts/assess_mini_replay.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2809 bytes. Materialized: False.

## [scripts/assess_replay_admission.py](../../scripts/assess_replay_admission.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1470 bytes. Materialized: False.

## [scripts/audit_action_training.py](../../scripts/audit_action_training.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6081 bytes. Materialized: False.

## [scripts/audit_corpus_action_budget.py](../../scripts/audit_corpus_action_budget.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5319 bytes. Materialized: False.

## [scripts/audit_exported_optimizer.py](../../scripts/audit_exported_optimizer.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4055 bytes. Materialized: False.

## [scripts/audit_issue_duplicates.py](../../scripts/audit_issue_duplicates.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6468 bytes. Materialized: False.

## [scripts/audit_issue_similarity.py](../../scripts/audit_issue_similarity.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2881 bytes. Materialized: False.

## [scripts/audit_native_trajectory_masks.py](../../scripts/audit_native_trajectory_masks.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6267 bytes. Materialized: False.

## [scripts/audit_r2_multipart.py](../../scripts/audit_r2_multipart.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4602 bytes. Materialized: False.

## [scripts/audit_replay_history_tokens.py](../../scripts/audit_replay_history_tokens.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4518 bytes. Materialized: False.

## [scripts/audit_replay_observations.py](../../scripts/audit_replay_observations.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1984 bytes. Materialized: False.

## [scripts/audit_repository_lineage.py](../../scripts/audit_repository_lineage.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4399 bytes. Materialized: False.

## [scripts/audit_source_expectation_corpus.py](../../scripts/audit_source_expectation_corpus.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5330 bytes. Materialized: False.

## [scripts/audit_source_expectations.py](../../scripts/audit_source_expectations.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3520 bytes. Materialized: False.

## [scripts/audit_source_task_join.py](../../scripts/audit_source_task_join.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5899 bytes. Materialized: False.

## [scripts/audit_source_tool_contracts.py](../../scripts/audit_source_tool_contracts.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5673 bytes. Materialized: False.

## [scripts/audit_swe_rebench_task_join.py](../../scripts/audit_swe_rebench_task_join.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5604 bytes. Materialized: False.

## [scripts/audit_training_representation.py](../../scripts/audit_training_representation.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5649 bytes. Materialized: False.

## [scripts/audit_trajectory_conversion.py](../../scripts/audit_trajectory_conversion.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5920 bytes. Materialized: False.

## [scripts/audit_trajectory_metadata.py](../../scripts/audit_trajectory_metadata.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5447 bytes. Materialized: False.

## [scripts/build_deployment_bundle.py](../../scripts/build_deployment_bundle.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4431 bytes. Materialized: False.

## [scripts/build_mini_replay_history.py](../../scripts/build_mini_replay_history.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6858 bytes. Materialized: False.

## [scripts/build_rebench_replay_history.py](../../scripts/build_rebench_replay_history.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 9181 bytes. Materialized: False.

## [scripts/build_replay_history.py](../../scripts/build_replay_history.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4505 bytes. Materialized: False.

## [scripts/build_source_snapshot.py](../../scripts/build_source_snapshot.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6756 bytes. Materialized: False.

## [scripts/capture_replay_rights_material.py](../../scripts/capture_replay_rights_material.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5194 bytes. Materialized: False.

## [scripts/capture_snapshot_notices.py](../../scripts/capture_snapshot_notices.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1924 bytes. Materialized: False.

## [scripts/census_trajectory_context.py](../../scripts/census_trajectory_context.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6137 bytes. Materialized: False.

## [scripts/census_trajectory_corpus.py](../../scripts/census_trajectory_corpus.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5498 bytes. Materialized: False.

## [scripts/compare_evaluations.py](../../scripts/compare_evaluations.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1518 bytes. Materialized: False.

## [scripts/compare_source_snapshot.py](../../scripts/compare_source_snapshot.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5854 bytes. Materialized: False.

## [scripts/compare_tornado_snapshot.py](../../scripts/compare_tornado_snapshot.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3504 bytes. Materialized: False.

## [scripts/evaluator_source_plugin.py](../../scripts/evaluator_source_plugin.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2196 bytes. Materialized: False.

## [scripts/extract_rebench_evaluator_input.py](../../scripts/extract_rebench_evaluator_input.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4670 bytes. Materialized: False.

## [scripts/grade_rebench_replay.py](../../scripts/grade_rebench_replay.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7872 bytes. Materialized: False.

## [scripts/grade_replayed_patch.py](../../scripts/grade_replayed_patch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6661 bytes. Materialized: False.

## [scripts/grade_source_attempt.py](../../scripts/grade_source_attempt.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5874 bytes. Materialized: False.

## [scripts/grade_swe_rebench_patch.py](../../scripts/grade_swe_rebench_patch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5199 bytes. Materialized: False.

## [scripts/grade_tornado_teacher.py](../../scripts/grade_tornado_teacher.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 254 bytes. Materialized: False.

## [scripts/inspect_training_corpus.py](../../scripts/inspect_training_corpus.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1496 bytes. Materialized: False.

## [scripts/intake_public_trajectory_source.py](../../scripts/intake_public_trajectory_source.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6385 bytes. Materialized: False.

## [scripts/merge_source_token_screens.py](../../scripts/merge_source_token_screens.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4148 bytes. Materialized: False.

## [scripts/plan_corpus_updates.py](../../scripts/plan_corpus_updates.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2660 bytes. Materialized: False.

## [scripts/plan_qualification_batch.py](../../scripts/plan_qualification_batch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6120 bytes. Materialized: False.

## [scripts/plan_serving.py](../../scripts/plan_serving.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2567 bytes. Materialized: False.

## [scripts/plan_trajectory_replays.py](../../scripts/plan_trajectory_replays.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6506 bytes. Materialized: False.

## [scripts/prepare_rebench_baseline.py](../../scripts/prepare_rebench_baseline.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4913 bytes. Materialized: False.

## [scripts/prepare_source_task.py](../../scripts/prepare_source_task.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5761 bytes. Materialized: False.

## [scripts/prepare_training_deployment.py](../../scripts/prepare_training_deployment.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4678 bytes. Materialized: False.

## [scripts/prepare_unicode_comparison.py](../../scripts/prepare_unicode_comparison.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4524 bytes. Materialized: False.

## [scripts/prepare_write_diagnostic.py](../../scripts/prepare_write_diagnostic.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6577 bytes. Materialized: False.

## [scripts/probe_adapter_cpu.py](../../scripts/probe_adapter_cpu.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5680 bytes. Materialized: False.

## [scripts/probe_compaction_runner.py](../../scripts/probe_compaction_runner.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7540 bytes. Materialized: False.

## [scripts/probe_compressed_gemma_loader.py](../../scripts/probe_compressed_gemma_loader.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7311 bytes. Materialized: False.

## [scripts/probe_evaluator_source.py](../../scripts/probe_evaluator_source.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6408 bytes. Materialized: False.

## [scripts/probe_gemma_parser.py](../../scripts/probe_gemma_parser.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4141 bytes. Materialized: False.

## [scripts/probe_gemma_training_cpu.py](../../scripts/probe_gemma_training_cpu.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 8716 bytes. Materialized: False.

## [scripts/probe_generated_write.py](../../scripts/probe_generated_write.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3641 bytes. Materialized: False.

## [scripts/probe_harness_compaction.py](../../scripts/probe_harness_compaction.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5812 bytes. Materialized: False.

## [scripts/probe_http_stack.py](../../scripts/probe_http_stack.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1915 bytes. Materialized: False.

## [scripts/probe_inference.py](../../scripts/probe_inference.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4633 bytes. Materialized: False.

## [scripts/probe_native_source_transport.py](../../scripts/probe_native_source_transport.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 10580 bytes. Materialized: False.

## [scripts/probe_native_training_batch.py](../../scripts/probe_native_training_batch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6285 bytes. Materialized: False.

## [scripts/probe_observation_recovery.py](../../scripts/probe_observation_recovery.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 10838 bytes. Materialized: False.

## [scripts/probe_observation_sandbox.py](../../scripts/probe_observation_sandbox.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7941 bytes. Materialized: False.

## [scripts/probe_observation_skill.py](../../scripts/probe_observation_skill.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4948 bytes. Materialized: False.

## [scripts/probe_serving_runtime.py](../../scripts/probe_serving_runtime.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3766 bytes. Materialized: False.

## [scripts/probe_source_image.py](../../scripts/probe_source_image.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4104 bytes. Materialized: False.

## [scripts/probe_source_workspace.py](../../scripts/probe_source_workspace.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5261 bytes. Materialized: False.

## [scripts/probe_swe_rebench_image.py](../../scripts/probe_swe_rebench_image.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4015 bytes. Materialized: False.

## [scripts/probe_training_pilot_cpu.py](../../scripts/probe_training_pilot_cpu.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3380 bytes. Materialized: False.

## [scripts/qualify_maven_compile_replay.py](../../scripts/qualify_maven_compile_replay.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 8030 bytes. Materialized: False.

## [scripts/qualify_rebench_v2.py](../../scripts/qualify_rebench_v2.py)

Qualify selected V2 Python base/reference controls in offline containers.

Size: 18578 bytes. Materialized: True.

## [scripts/qualify_source_evaluator.py](../../scripts/qualify_source_evaluator.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3667 bytes. Materialized: False.

## [scripts/qualify_swe_rebench_evaluator.py](../../scripts/qualify_swe_rebench_evaluator.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 11151 bytes. Materialized: False.

## [scripts/qualify_tornado_evaluator.py](../../scripts/qualify_tornado_evaluator.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5127 bytes. Materialized: False.

## [scripts/replay_mini_source.py](../../scripts/replay_mini_source.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 12482 bytes. Materialized: False.

## [scripts/replay_source_teacher.py](../../scripts/replay_source_teacher.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 27878 bytes. Materialized: False.

## [scripts/replay_tornado_teacher.py](../../scripts/replay_tornado_teacher.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 331 bytes. Materialized: False.

## [scripts/resolve_source_environments.py](../../scripts/resolve_source_environments.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 8671 bytes. Materialized: False.

## [scripts/resolve_swe_rebench_images.py](../../scripts/resolve_swe_rebench_images.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4235 bytes. Materialized: False.

## [scripts/review_budget_rebench_tasks.py](../../scripts/review_budget_rebench_tasks.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5732 bytes. Materialized: False.

## [scripts/review_python_test_source.py](../../scripts/review_python_test_source.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1588 bytes. Materialized: False.

## [scripts/review_swe_rebench_teacher.py](../../scripts/review_swe_rebench_teacher.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5249 bytes. Materialized: False.

## [scripts/run_corpus_training.py](../../scripts/run_corpus_training.py)

Deadline-supervised corpus training; never starts or stops a Runpod Pod.

Size: 5279 bytes. Materialized: True.

## [scripts/run_corpus_training_worker.py](../../scripts/run_corpus_training_worker.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 10680 bytes. Materialized: False.

## [scripts/run_maven_grade_probe.py](../../scripts/run_maven_grade_probe.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4590 bytes. Materialized: False.

## [scripts/run_p1_repair.py](../../scripts/run_p1_repair.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7870 bytes. Materialized: False.

## [scripts/run_p1_server.py](../../scripts/run_p1_server.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5326 bytes. Materialized: False.

## [scripts/run_p1_training.py](../../scripts/run_p1_training.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3581 bytes. Materialized: False.

## [scripts/run_p1_training_worker.py](../../scripts/run_p1_training_worker.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7117 bytes. Materialized: False.

## [scripts/run_rebench_controls.py](../../scripts/run_rebench_controls.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7861 bytes. Materialized: False.

## [scripts/run_source_task.py](../../scripts/run_source_task.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 11433 bytes. Materialized: False.

## [scripts/run_write_diagnostic.py](../../scripts/run_write_diagnostic.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 8492 bytes. Materialized: False.

## [scripts/screen_corpus_credentials.py](../../scripts/screen_corpus_credentials.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2249 bytes. Materialized: False.

## [scripts/screen_issue_credentials.py](../../scripts/screen_issue_credentials.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2374 bytes. Materialized: False.

## [scripts/screen_source_token_cost.py](../../scripts/screen_source_token_cost.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7410 bytes. Materialized: False.

## [scripts/select_budget_rebench_tasks.py](../../scripts/select_budget_rebench_tasks.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3429 bytes. Materialized: False.

## [scripts/transfer_artifact.py](../../scripts/transfer_artifact.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5116 bytes. Materialized: False.

## [scripts/verify_architecture_layout.py](../../scripts/verify_architecture_layout.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4621 bytes. Materialized: False.

## [scripts/verify_conversation.py](../../scripts/verify_conversation.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3152 bytes. Materialized: False.

## [scripts/verify_gemma_causal_projection.py](../../scripts/verify_gemma_causal_projection.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5219 bytes. Materialized: False.

## [scripts/verify_graph_retrieval.py](../../scripts/verify_graph_retrieval.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4773 bytes. Materialized: False.

## [scripts/verify_linux_r0.py](../../scripts/verify_linux_r0.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 10196 bytes. Materialized: False.

## [scripts/verify_model_storage.py](../../scripts/verify_model_storage.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2748 bytes. Materialized: False.

## [scripts/verify_model_text_boundary.py](../../scripts/verify_model_text_boundary.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3605 bytes. Materialized: False.

## [scripts/verify_official_r0.py](../../scripts/verify_official_r0.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7928 bytes. Materialized: False.

## [scripts/verify_p1_repair.py](../../scripts/verify_p1_repair.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 9056 bytes. Materialized: False.

## [scripts/verify_pilot_environment.py](../../scripts/verify_pilot_environment.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 8048 bytes. Materialized: False.

## [scripts/verify_pilot_snapshot.py](../../scripts/verify_pilot_snapshot.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4134 bytes. Materialized: False.

## [scripts/verify_quantized_layout.py](../../scripts/verify_quantized_layout.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3517 bytes. Materialized: False.

## [scripts/verify_r0.py](../../scripts/verify_r0.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4191 bytes. Materialized: False.

## [scripts/verify_r2_transport.py](../../scripts/verify_r2_transport.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4664 bytes. Materialized: False.

## [scripts/verify_serving_wheels.py](../../scripts/verify_serving_wheels.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4314 bytes. Materialized: False.

## [scripts/verify_source_http_client.py](../../scripts/verify_source_http_client.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4472 bytes. Materialized: False.

## [scripts/verify_source_runner_lifecycle.py](../../scripts/verify_source_runner_lifecycle.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4522 bytes. Materialized: False.

## [scripts/verify_source_snapshot.py](../../scripts/verify_source_snapshot.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5024 bytes. Materialized: False.

## [scripts/verify_tokenizer.py](../../scripts/verify_tokenizer.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7001 bytes. Materialized: False.

## [scripts/verify_training_masks.py](../../scripts/verify_training_masks.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6393 bytes. Materialized: False.

## [scripts/verify_weight_numerics.py](../../scripts/verify_weight_numerics.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6380 bytes. Materialized: False.

## [tests/test_action_training.py](../../tests/test_action_training.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4116 bytes. Materialized: False.

## [tests/test_adapter_checkpoint.py](../../tests/test_adapter_checkpoint.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6375 bytes. Materialized: False.

## [tests/test_amendment_admission.py](../../tests/test_amendment_admission.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5614 bytes. Materialized: False.

## [tests/test_architecture_layout.py](../../tests/test_architecture_layout.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2265 bytes. Materialized: False.

## [tests/test_artifact_file_record.py](../../tests/test_artifact_file_record.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1258 bytes. Materialized: False.

## [tests/test_checkpoint_storage.py](../../tests/test_checkpoint_storage.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6504 bytes. Materialized: False.

## [tests/test_completion_admission.py](../../tests/test_completion_admission.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5193 bytes. Materialized: False.

## [tests/test_container_cleanup.py](../../tests/test_container_cleanup.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1465 bytes. Materialized: False.

## [tests/test_context_census.py](../../tests/test_context_census.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1082 bytes. Materialized: False.

## [tests/test_conversation.py](../../tests/test_conversation.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3297 bytes. Materialized: False.

## [tests/test_corpus_assembly.py](../../tests/test_corpus_assembly.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6658 bytes. Materialized: False.

## [tests/test_corpus_credentials.py](../../tests/test_corpus_credentials.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3298 bytes. Materialized: False.

## [tests/test_corpus_gemma_torch.py](../../tests/test_corpus_gemma_torch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3280 bytes. Materialized: False.

## [tests/test_corpus_optimization.py](../../tests/test_corpus_optimization.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5720 bytes. Materialized: False.

## [tests/test_corpus_run.py](../../tests/test_corpus_run.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3025 bytes. Materialized: False.

## [tests/test_corpus_training.py](../../tests/test_corpus_training.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6012 bytes. Materialized: False.

## [tests/test_deadline.py](../../tests/test_deadline.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2177 bytes. Materialized: False.

## [tests/test_editor_preflight.py](../../tests/test_editor_preflight.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1711 bytes. Materialized: False.

## [tests/test_evaluation.py](../../tests/test_evaluation.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4539 bytes. Materialized: False.

## [tests/test_evaluator_source_plugin.py](../../tests/test_evaluator_source_plugin.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2550 bytes. Materialized: False.

## [tests/test_foundation.py](../../tests/test_foundation.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 14488 bytes. Materialized: False.

## [tests/test_gemma_training_torch.py](../../tests/test_gemma_training_torch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3202 bytes. Materialized: False.

## [tests/test_gemma_trajectory.py](../../tests/test_gemma_trajectory.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1983 bytes. Materialized: False.

## [tests/test_go_test_controls.py](../../tests/test_go_test_controls.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6354 bytes. Materialized: False.

## [tests/test_gpu_memory.py](../../tests/test_gpu_memory.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3738 bytes. Materialized: False.

## [tests/test_inference_capture.py](../../tests/test_inference_capture.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6236 bytes. Materialized: False.

## [tests/test_inference_probe.py](../../tests/test_inference_probe.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2575 bytes. Materialized: False.

## [tests/test_issue_contract.py](../../tests/test_issue_contract.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4476 bytes. Materialized: False.

## [tests/test_issue_duplicates.py](../../tests/test_issue_duplicates.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1502 bytes. Materialized: False.

## [tests/test_issue_similarity.py](../../tests/test_issue_similarity.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5144 bytes. Materialized: False.

## [tests/test_issue_similarity_cli.py](../../tests/test_issue_similarity_cli.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2207 bytes. Materialized: False.

## [tests/test_junit_controls.py](../../tests/test_junit_controls.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 8346 bytes. Materialized: False.

## [tests/test_leakage_merge.py](../../tests/test_leakage_merge.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4404 bytes. Materialized: False.

## [tests/test_matrix_admission_evidence.py](../../tests/test_matrix_admission_evidence.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 8065 bytes. Materialized: False.

## [tests/test_matrix_grade_evidence.py](../../tests/test_matrix_grade_evidence.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5102 bytes. Materialized: False.

## [tests/test_matrix_probe_contract.py](../../tests/test_matrix_probe_contract.py)

Synthetic programs and receipts exercise probe substitution rejection.

Size: 5250 bytes. Materialized: True.

## [tests/test_maven_compile_controls.py](../../tests/test_maven_compile_controls.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6403 bytes. Materialized: False.

## [tests/test_maven_grade_bundle.py](../../tests/test_maven_grade_bundle.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 8740 bytes. Materialized: False.

## [tests/test_mini_replay_admission.py](../../tests/test_mini_replay_admission.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 19321 bytes. Materialized: False.

## [tests/test_mini_replay_amendment.py](../../tests/test_mini_replay_amendment.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7095 bytes. Materialized: False.

## [tests/test_mini_replay_history.py](../../tests/test_mini_replay_history.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3043 bytes. Materialized: False.

## [tests/test_mini_source_history.py](../../tests/test_mini_source_history.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3631 bytes. Materialized: False.

## [tests/test_mocha_controls.py](../../tests/test_mocha_controls.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5917 bytes. Materialized: False.

## [tests/test_model_intake.py](../../tests/test_model_intake.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4028 bytes. Materialized: False.

## [tests/test_object_store.py](../../tests/test_object_store.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 10503 bytes. Materialized: False.

## [tests/test_offline_resources.py](../../tests/test_offline_resources.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3264 bytes. Materialized: False.

## [tests/test_optimizer_checkpoint_torch.py](../../tests/test_optimizer_checkpoint_torch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3817 bytes. Materialized: False.

## [tests/test_p1_server.py](../../tests/test_p1_server.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3975 bytes. Materialized: False.

## [tests/test_probe_receipt.py](../../tests/test_probe_receipt.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2348 bytes. Materialized: False.

## [tests/test_process_supervisor.py](../../tests/test_process_supervisor.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4787 bytes. Materialized: False.

## [tests/test_public_source_download.py](../../tests/test_public_source_download.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2267 bytes. Materialized: False.

## [tests/test_pytest_applicability.py](../../tests/test_pytest_applicability.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3753 bytes. Materialized: False.

## [tests/test_pytest_controls.py](../../tests/test_pytest_controls.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5342 bytes. Materialized: False.

## [tests/test_pytest_matrix.py](../../tests/test_pytest_matrix.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6889 bytes. Materialized: False.

## [tests/test_qualification_sampling.py](../../tests/test_qualification_sampling.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3193 bytes. Materialized: False.

## [tests/test_quantized_layout.py](../../tests/test_quantized_layout.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3433 bytes. Materialized: False.

## [tests/test_rebench_control_profile.py](../../tests/test_rebench_control_profile.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4587 bytes. Materialized: False.

## [tests/test_rebench_grade_evidence.py](../../tests/test_rebench_grade_evidence.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4296 bytes. Materialized: False.

## [tests/test_rebench_replay_grader.py](../../tests/test_rebench_replay_grader.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 765 bytes. Materialized: False.

## [tests/test_rebench_snapshot_controls.py](../../tests/test_rebench_snapshot_controls.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4190 bytes. Materialized: False.

## [tests/test_rebench_source_snapshots.py](../../tests/test_rebench_source_snapshots.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 10434 bytes. Materialized: False.

## [tests/test_rebench_v2_profile.py](../../tests/test_rebench_v2_profile.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7869 bytes. Materialized: False.

## [tests/test_replay_admission.py](../../tests/test_replay_admission.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7118 bytes. Materialized: False.

## [tests/test_replay_amendment.py](../../tests/test_replay_amendment.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 13248 bytes. Materialized: False.

## [tests/test_replay_completion.py](../../tests/test_replay_completion.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4058 bytes. Materialized: False.

## [tests/test_replay_correction.py](../../tests/test_replay_correction.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5245 bytes. Materialized: False.

## [tests/test_replay_history.py](../../tests/test_replay_history.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1714 bytes. Materialized: False.

## [tests/test_replay_noop.py](../../tests/test_replay_noop.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4490 bytes. Materialized: False.

## [tests/test_replay_observations.py](../../tests/test_replay_observations.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2194 bytes. Materialized: False.

## [tests/test_replay_resources.py](../../tests/test_replay_resources.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1773 bytes. Materialized: False.

## [tests/test_replay_selection.py](../../tests/test_replay_selection.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1150 bytes. Materialized: False.

## [tests/test_repository_lineage.py](../../tests/test_repository_lineage.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1105 bytes. Materialized: False.

## [tests/test_resource_replay_binding.py](../../tests/test_resource_replay_binding.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3683 bytes. Materialized: False.

## [tests/test_review_coverage.py](../../tests/test_review_coverage.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4744 bytes. Materialized: False.

## [tests/test_serving.py](../../tests/test_serving.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2183 bytes. Materialized: False.

## [tests/test_serving_wheels.py](../../tests/test_serving_wheels.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2542 bytes. Materialized: False.

## [tests/test_session_report.py](../../tests/test_session_report.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4635 bytes. Materialized: False.

## [tests/test_session_resource_bundle.py](../../tests/test_session_resource_bundle.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5563 bytes. Materialized: False.

## [tests/test_session_resource_replay.py](../../tests/test_session_resource_replay.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4799 bytes. Materialized: False.

## [tests/test_source_base.py](../../tests/test_source_base.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2282 bytes. Materialized: False.

## [tests/test_source_bytes.py](../../tests/test_source_bytes.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2182 bytes. Materialized: False.

## [tests/test_source_capture.py](../../tests/test_source_capture.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5311 bytes. Materialized: False.

## [tests/test_source_credentials.py](../../tests/test_source_credentials.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5435 bytes. Materialized: False.

## [tests/test_source_environment_resolution.py](../../tests/test_source_environment_resolution.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3956 bytes. Materialized: False.

## [tests/test_source_evaluator.py](../../tests/test_source_evaluator.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1749 bytes. Materialized: False.

## [tests/test_source_expectation_corpus.py](../../tests/test_source_expectation_corpus.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1201 bytes. Materialized: False.

## [tests/test_source_imports.py](../../tests/test_source_imports.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2419 bytes. Materialized: False.

## [tests/test_source_local_commands.py](../../tests/test_source_local_commands.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3745 bytes. Materialized: False.

## [tests/test_source_observations.py](../../tests/test_source_observations.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2920 bytes. Materialized: False.

## [tests/test_source_pytest_paths.py](../../tests/test_source_pytest_paths.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2249 bytes. Materialized: False.

## [tests/test_source_search_replay.py](../../tests/test_source_search_replay.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4828 bytes. Materialized: False.

## [tests/test_source_snapshot.py](../../tests/test_source_snapshot.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7378 bytes. Materialized: False.

## [tests/test_source_subdirectory_commands.py](../../tests/test_source_subdirectory_commands.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3056 bytes. Materialized: False.

## [tests/test_source_task.py](../../tests/test_source_task.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1151 bytes. Materialized: False.

## [tests/test_source_task_metadata.py](../../tests/test_source_task_metadata.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6544 bytes. Materialized: False.

## [tests/test_source_test_platform.py](../../tests/test_source_test_platform.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 906 bytes. Materialized: False.

## [tests/test_source_test_risk.py](../../tests/test_source_test_risk.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3560 bytes. Materialized: False.

## [tests/test_source_token_screen.py](../../tests/test_source_token_screen.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2121 bytes. Materialized: False.

## [tests/test_source_tool_contracts.py](../../tests/test_source_tool_contracts.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 790 bytes. Materialized: False.

## [tests/test_static_controls.py](../../tests/test_static_controls.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2221 bytes. Materialized: False.

## [tests/test_submission_reconciliation.py](../../tests/test_submission_reconciliation.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4914 bytes. Materialized: False.

## [tests/test_synthetic_admission.py](../../tests/test_synthetic_admission.py)

(No module docstring; inspect source.)

Size: 7946 bytes. Materialized: True.

## [tests/test_task_alignment.py](../../tests/test_task_alignment.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3252 bytes. Materialized: False.

## [tests/test_task_intake.py](../../tests/test_task_intake.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2801 bytes. Materialized: False.

## [tests/test_teacher_replay_profile.py](../../tests/test_teacher_replay_profile.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 9653 bytes. Materialized: False.

## [tests/test_terminal_training_history.py](../../tests/test_terminal_training_history.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1606 bytes. Materialized: False.

## [tests/test_tool_diagnostic.py](../../tests/test_tool_diagnostic.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2205 bytes. Materialized: False.

## [tests/test_training_batch.py](../../tests/test_training_batch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1678 bytes. Materialized: False.

## [tests/test_training_corpus.py](../../tests/test_training_corpus.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 9976 bytes. Materialized: False.

## [tests/test_training_pilot_torch.py](../../tests/test_training_pilot_torch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3292 bytes. Materialized: False.

## [tests/test_training_rng.py](../../tests/test_training_rng.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 5319 bytes. Materialized: False.

## [tests/test_training_schedule.py](../../tests/test_training_schedule.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2558 bytes. Materialized: False.

## [tests/test_training_session.py](../../tests/test_training_session.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 6934 bytes. Materialized: False.

## [tests/test_training_state_torch.py](../../tests/test_training_state_torch.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3405 bytes. Materialized: False.

## [tests/test_training_volume.py](../../tests/test_training_volume.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1980 bytes. Materialized: False.

## [tests/test_trajectory_corpus_census.py](../../tests/test_trajectory_corpus_census.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2961 bytes. Materialized: False.

## [tests/test_trajectory_import.py](../../tests/test_trajectory_import.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2577 bytes. Materialized: False.

## [tests/test_trajectory_metadata_audit.py](../../tests/test_trajectory_metadata_audit.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3584 bytes. Materialized: False.

## [tests/test_transfer_evidence.py](../../tests/test_transfer_evidence.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 4393 bytes. Materialized: False.

## [tests/test_v2_synthetic_admission.py](../../tests/test_v2_synthetic_admission.py)

(No module docstring; inspect source.)

Size: 11833 bytes. Materialized: True.

## [tests/test_weight_numerics.py](../../tests/test_weight_numerics.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2720 bytes. Materialized: False.

## [tests/test_worker_architecture.py](../../tests/test_worker_architecture.py)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 3030 bytes. Materialized: False.

## [configs/Dockerfile.p1-evaluator-http](../../configs/Dockerfile.p1-evaluator-http)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 558 bytes. Materialized: True.

## [configs/Dockerfile.p1-evaluator-http.dockerignore](../../configs/Dockerfile.p1-evaluator-http.dockerignore)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 206 bytes. Materialized: True.

## [configs/Dockerfile.p1-http-compatibility](../../configs/Dockerfile.p1-http-compatibility)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 703 bytes. Materialized: True.

## [configs/p1-corpus-qualification.json](../../configs/p1-corpus-qualification.json)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 293 bytes. Materialized: True.

## [configs/p1-deployment-files.json](../../configs/p1-deployment-files.json)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 7066 bytes. Materialized: True.

## [configs/p1-serving.json](../../configs/p1-serving.json)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 620 bytes. Materialized: True.

## [configs/p1-training-pilot.json](../../configs/p1-training-pilot.json)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 899 bytes. Materialized: True.

## [configs/p1-unicode-comparison-file-map.json](../../configs/p1-unicode-comparison-file-map.json)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 959 bytes. Materialized: True.

## [configs/p1-write-diagnostic-file-map.json](../../configs/p1-write-diagnostic-file-map.json)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 871 bytes. Materialized: True.

## [requirements/evaluator-http-compatibility.lock.txt](../../requirements/evaluator-http-compatibility.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 187 bytes. Materialized: False.

## [requirements/evaluator-http-linux-py313.lock.txt](../../requirements/evaluator-http-linux-py313.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2683 bytes. Materialized: False.

## [requirements/r2-transport.lock.txt](../../requirements/r2-transport.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 147 bytes. Materialized: False.

## [requirements/serving-download-linux-py312.lock.txt](../../requirements/serving-download-linux-py312.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 63115 bytes. Materialized: False.

## [requirements/serving-linux-py312-httpfix.lock.txt](../../requirements/serving-linux-py312-httpfix.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 25432 bytes. Materialized: False.

## [requirements/serving-linux-py312.lock.txt](../../requirements/serving-linux-py312.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 25432 bytes. Materialized: False.

## [requirements/serving-local.constraints.txt](../../requirements/serving-local.constraints.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1540 bytes. Materialized: False.

## [requirements/serving-official.constraints.txt](../../requirements/serving-official.constraints.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1063 bytes. Materialized: False.

## [requirements/serving-p1.in](../../requirements/serving-p1.in)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 421 bytes. Materialized: False.

## [requirements/tokenizer-official-versions.lock.txt](../../requirements/tokenizer-official-versions.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 480 bytes. Materialized: False.

## [requirements/tokenizer-preflight.lock.txt](../../requirements/tokenizer-preflight.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 480 bytes. Materialized: False.

## [requirements/training-peft-supplement.lock.txt](../../requirements/training-peft-supplement.lock.txt)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 92 bytes. Materialized: False.

## [examples/splits.draft.json](../../examples/splits.draft.json)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 49 bytes. Materialized: False.

## [candidates/p1-base/README.md](../../candidates/p1-base/README.md)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 930 bytes. Materialized: True.

## [candidates/p1-base/agent.yaml](../../candidates/p1-base/agent.yaml)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 323 bytes. Materialized: True.

## [candidates/p1-base/configs/sampling.yaml](../../candidates/p1-base/configs/sampling.yaml)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 118 bytes. Materialized: True.

## [candidates/p1-base/eval_config.yaml](../../candidates/p1-base/eval_config.yaml)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 166 bytes. Materialized: True.

## [candidates/p1-base/prompts/system.md](../../candidates/p1-base/prompts/system.md)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2308 bytes. Materialized: True.

## [candidates/p1-observation-memory/agent.yaml](../../candidates/p1-observation-memory/agent.yaml)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 376 bytes. Materialized: True.

## [candidates/p1-observation-memory/configs/sampling.yaml](../../candidates/p1-observation-memory/configs/sampling.yaml)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 118 bytes. Materialized: True.

## [candidates/p1-observation-memory/eval_config.yaml](../../candidates/p1-observation-memory/eval_config.yaml)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 166 bytes. Materialized: True.

## [candidates/p1-observation-memory/prompts/system.md](../../candidates/p1-observation-memory/prompts/system.md)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 2667 bytes. Materialized: True.

## [candidates/p1-observation-memory/skills/source-observations/SKILL.md](../../candidates/p1-observation-memory/skills/source-observations/SKILL.md)

Configuration, dependency specification or non-Python asset; inspect linked content.

Size: 1685 bytes. Materialized: True.

## [candidates/p1-observation-memory/skills/source-observations/scripts/observe.py](../../candidates/p1-observation-memory/skills/source-observations/scripts/observe.py)

Source snapshots for context recovery; checksums are integrity, not authenticity.

Size: 5117 bytes. Materialized: True.

