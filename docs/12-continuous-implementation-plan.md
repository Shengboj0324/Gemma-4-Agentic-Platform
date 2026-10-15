# Continuous implementation and acceptance plan

For current acceptance status, see [Current P1 readiness](39-p1-current-readiness.md).
Append new cycle records to the [implementation journal](40-p1-implementation-journal.md);
the historical cycle records in this plan remain preserved.

Updated October 8, 2026. **Living plan; user adopted a foundation-first, trainable Gemma agent. P0 is accepted within its recorded scope. P1 has real GPU inference and submitted-patch evidence, but is not fully accepted; training has not started.** Codex owns implementation, mathematical design, engineering, tests, analysis, and evidence preparation. The entrant supplies account access, eligibility decisions, and resource authorization. This document governs cycle cadence; [platform specification and handoff](19-agent-platform-and-model-handoff.md) governs the current build, [joint strategy](11-code-track-and-joint-strategy.md) governs competition constraints, and [evaluation protocol](05-evaluation-protocol.md) governs experiments.

The objective is a reproducible, competitive repair agent with defensible research results. Mathematical sophistication must improve a justified objective or explain observed behavior. No fabricated results, task-specific answer lookup, leaked reference patches, or cosmetic chat interface presented as a working system. Explicit configuration constants and clearly labeled synthetic test fixtures are legitimate; hardcoded benchmark outcomes are not.

## Cycle structure

**R1 closeout — October 7:** accepted as a bounded bug reproduction and baseline challenge; **revise the product hypothesis, no promotion**. The React artifact was inaccessible. The previously shortlisted real Raft shutdown defect was reproduced in a controlled component test. Three fresh `gpt-6.1-sol` high-reasoning attempts each passed 21 independent targeted race-enabled checks. Agent times were 314.606, 321.029 and 401.253 seconds. Broader suites retain two failures also present on the upstream reference repair. See [complete results and limits](18-reproduction-cycle-results.md). This does not establish Gemma performance or mechanism lift. Stop before R3: the required persistent baseline failure was not demonstrated. The next research input must be a different accessible failure set, not a product build around this solved example. This early gate did not consume or claim an 8–14-hour implementation phase; hands-on engineering time was not separately instrumented.

Use **8–14 hours per engineering cycle**, including protected acceptance work. A nominal 12-hour cycle allocates one hour to design and scope, six to implementation, three to verification, one to comparison, and one to assessment and documentation. Reallocate after measurement; never omit validation to meet the timebox. A phase may require several cycles. Do not fill time with unnecessary work or declare unfinished work accepted when time expires.

At cycle start, select one bounded deliverable, baseline commit, hypothesis, resource cap, failure conditions, and acceptance criteria. During implementation, checkpoint resumable work and test incrementally. At closeout, assign **accepted**, **revise**, or **blocked** with evidence. Record active engineering time, experiment runtime, and elapsed wall time separately. The cycle target is not a promise of unattended execution between chats.

## Phases and exit gates

P1 implementation evidence is tracked in [document 24](24-p1-implementation-status.md). The October 8 checkpoint storage gate passed; GPU inference and P1 acceptance remain pending.

**October 7 scope replacement:** build the general agent now; do not wait for a new specialist product hypothesis. Earlier graph, synthesis, migration, undo, simulator and GPU-optimization proposals are not mandatory components. Failure-first comparisons remain the gate for claiming a novel advantage. The historical R1 instruction to stop before R3 applied to the discarded mechanism, not the platform phases below. This documentation update is not an implementation cycle.

| Phase | Main work across one or more cycles | Required exit evidence |
| --- | --- | --- |
| P0. Contracts and skeleton | Obtain HARNESS_README.md and starter; pin schemas; design state/event records, packaging and dependency boundaries | Contract tests and archive validation; no fabricated model calls; fixtures explicitly synthetic. Can begin without weights |
| P1. Model intake and inference | Confirm user's downloaded path/version; inspect and hash complete model package; run exact quantized model and multi-turn tool calls | GPU memory/latency receipt; parsed tool calls and tool-result continuation; real starter task and captured patch. Runpod first required here |
| P2. Complete agent execution | Implement inspect/localize/edit/test/recover/submit; state transitions, bounded calls, checkpointing and offline behavior | Actual end-to-end tasks; interrupted/failed-tool tests; patch preservation and budget exhaustion checks. Linux worker needed here or earlier for harness smoke tests |
| P3. Independent evaluation | Audit task images and test oracles; freeze splits; record untuned Gemma baseline across task families | All-task denominator, failure categories, repeats and resource metrics; evaluator assets isolated from agent |
| P4. Core capability improvement | Compare repository context selection, reasoning settings, test selection, recovery and cost-aware stopping | Matched development comparisons and ablations; mathematical claim checks; simple baseline retained if stronger |
| P5. Training pipeline and pilot | Curate licensed trajectories; prove compatible adapter training/export/load; run supervised LoRA pilot with train-only feedback | Loss-mask and gradient checks, checkpoint resume/reload, independent post-training repair evaluation; no automatic promotion from lower loss |
| P6. Trained capability expansion | Tune data mixtures and difficult-task curriculum; evaluate preference/RL methods only with sound rewards and compute | Reproducible checkpoint and held-out gains under equal budgets; regression and contamination audit; unhelpful adapters rejected |
| P7. Platform and submission qualification | CLI/batch interface, run inspection, artifact registry, restart/cancel controls; offline clean build and full-budget replay | Target-runtime compatibility, manifests/hashes, restore test, packaged champion. Cloud services remain outside scored execution |
| P8. Research and releases | Identify a measured specialist gap, audit prior art, compare a novel intervention; freeze separate paper and code artifacts | Claims supported by frozen evidence; novelty optional for baseline completion but required for novelty claims; submission status checked separately |

P4–P6 are iterative. Building and testing a training pipeline is part of the adopted platform; deploying a trained adapter requires evidence. Full RL and specialist mechanisms remain conditional. Return to P2 when infrastructure invalidates measurements. Every phase may take multiple 8–14-hour cycles. Deadline pressure reduces scope, never evidence standards.

## Acceptance and correctness

Current data-supply constraint (corpus 028): 141,883 quarantined supervised tokens
would require approximately 352.40 corpus-equivalent passes per 50M-token
candidate. The three-candidate objective remains unchanged; this small corpus
does not supply it. Before a training streak, expand reviewed task diversity,
freeze splits, quantify token reuse, and resolve context-policy exceptions.
The [supply audit](../evidence/data/corpus028-supply-review-001/report.json) finds
24/24 sequences within the 32,768-token training length, but only 22/24 within
the separate 8,192-token output-reserve policy. Emcee 295 and CloudEvents 172
need an explicit, validated resolution before admission under that policy.
Do not silently truncate histories or weaken the gate to increase data counts.

Every cycle closes with these six assessments, marking a category inapplicable only with a reason:

1. **Mathematical validity:** maintain a claim ledger linking assumptions, derivation or proof, implementation, numerical tolerances, counterexamples, and limits. Check boundary cases and dimensions. A coverage-surrogate theorem does not prove repair success; a continuous concave allocation argument does not establish optimality for unknown discrete task responses.
2. **Software validity:** require focused unit, property, integration and regression checks appropriate to the change. Compare small optimization instances with an independent exhaustive reference. Exercise malformed tool output, empty evidence, interrupted execution and resource exhaustion where relevant. Verify real patch production and grading end to end.
3. **Statistical validity:** predeclare the primary comparison, estimand, cohort, meaningful effect, analysis and stopping rule. Pair tasks across methods; account for repeated seeds and repository dependence. Report effect sizes and uncertainty. Few repositories limit generalization; more seeds do not create independent tasks. Use a fixed confirmatory analysis or a justified sequential procedure, not repeated uncorrected significance checks.
4. **Fair comparison:** use the same task manifest, model constraints, grading and declared budget conditions. Count failures and timeouts; report setup and preprocessing. Audit exclusions before comparing methods. Keep development, confirmatory and leaderboard evidence distinct.
5. **Engineering quality:** assess maintainability, interface compatibility, reproducibility, observability, resource consumption and failure recovery. Remove unnecessary mechanisms. Evaluate numerical stability and deterministic replay where supported; record unavoidable nondeterminism.
6. **Evidence integrity:** every reported result traces to retained logs, configuration, data/environment versions and artifact hashes. Label planned, synthetic, measured and proved content distinctly. Missing evidence is unresolved, never inferred into a passing result.

**Integration acceptance and champion promotion are separate.** Correct infrastructure can be accepted without an accuracy gain. A performance intervention becomes champion only under predeclared repair and resource criteria. For paired outcomes, report the average task-level difference, with uncertainty appropriate to the sampling design. If superiority is required, an interval crossing the required improvement threshold is inconclusive. Efficiency promotion requires its declared accuracy noninferiority and resource criteria. Choose margins before viewing results; insufficient power cannot establish equivalence.

No finite test suite guarantees arbitrary patches or all future executions. Guarantees must name their domain: a proved property under stated assumptions, verified bounded states, or observed behavior on identified tests. Known correctness defects, invalid statistics, leakage, or missing critical evidence block promotion. A polished demo cannot override these gates.

## Adjustable variables

| Variable | Current setting and revision rule |
| --- | --- |
| Cycle duration and phase count | 8–14 hours; nominal 12. Estimate remaining cycles after the baseline pilot |
| Compute, storage and cash caps | First P1 GPU session: four hours at observed $1.79/hour, about $7.16 compute maximum; remote work ended early, Pod stop remains user-controlled. New sessions need their own cap |
| Hardware and runtime reserve | A100 80GB inference observed at up to 67,231 MiB in recorded samples; not a whole-run peak or training-memory estimate |
| Cohorts, seeds and evaluation budget | Provisional in document 5; freeze before relevant comparisons; log changes and lost holdout status |
| Effect threshold, noninferiority margin, confidence level | Declare per comparison before outcomes; use document 5 as the starting protocol, not a post-hoc choice |
| Candidate mechanism | Core Gemma agent adopted; specialist novelty undecided. Prioritize measured localization, editing, tool-use and budget failures |
| Deadline allocation | Preserve separate paper/code freezes; revise the resource schedule after each cycle |

## Required closeout and next cycle

After **every** implementation cycle, append a record below and update current variables, next-cycle scope, and affected technical/evaluation/resource/decision documents. Preserve old records and frozen results. No cycle is closed until documentation and evidence agree.

Each record includes: cycle ID; timestamps and three time measures; objective; baseline/candidate hashes; changes; proof and test evidence paths; task/config/run manifests; measured metrics and intervals; costs; failures and unresolved assumptions; six-category assessment; integration and promotion decisions; rollback reference; and next bounded objective. Use “not measured” where applicable. Do not manufacture an aggregate quality score from subjective ratings.

| Record | Status | Evidence and next action |
| --- | --- | --- |
| Planning, October 7 | Documentation only; no implementation cycle completed | Next cycle: phase 1, authorized harness inspection and smallest reproducible baseline. Resolve access and resource caps first; preserve protected evaluation tasks |
| Foundation-first revision, October 7 | Plan updated; live overview/model/plugin checks completed; no GPU allocated | Next cycle P0: official harness/starter intake, contract fixtures, state schema and packaging. Model required at P1; ask for downloaded folder/version then. Runpod read succeeded, DigitalOcean account active, Cloudflare not discoverable in current plugin search. See document 19 |

Once implementation begins, add detailed cycle records under this table or link them here from a dedicated cycle-log directory. Update this plan as evidence changes; retain the acceptance standards unless an explicitly justified revision improves their validity.


### R0 local foundation checkpoint — October 7, 2026

R0 means P0 in this plan. Status: **revise / official integration pending**. Baseline commit `20b44be`; uncommitted candidate identity is the per-file SHA-256 map in [local-002 receipt](../evidence/r0/local-002/receipt.json). Historical reproduction evidence is unchanged. Implementation and claim audit: [document 20](20-r0-foundation.md). Provider preparation: [document 21](21-cloud-preparation.md).

- Implemented: pure state/event contracts, exact budget and context admission, artifact manifests and verification, split validation, bounded ZIP structure inspection, CLI and offline verification script.
- Verification: 25 synthetic contract/integration tests passed; isolated zipapp success and rejection exits passed. Test log: [local-002/tests.log](../evidence/r0/local-002/tests.log). The earlier local-001 receipt predates a correction to zipapp exit-code propagation in the verification script; local-002 supersedes it for packaging evidence.
- Timing: recorded verification began 2026-10-08 00:40:27.143545 UTC and ended 00:40:27.435433 UTC; monotonic duration 0.291682625 seconds. Active engineering time and total session wall time were not instrumented. This checkpoint does not claim an 8–14-hour cycle was completed.
- Metrics: repair rate, model latency, training improvement and comparative confidence intervals not measured. No billable resources created; local energy/API costs not measured. Existing account charges not audited.
- Mathematical assessment: exact arithmetic and invariant arguments documented with bounded independent references. Software assessment: local checks pass; Linux and official runtime remain unverified. Statistical and fair-comparison assessment: no empirical treatment comparison yet; draft split only. Engineering assessment: standard-library package, explicit errors and retained failure paths. Evidence assessment: source hashes and real logs retained; fixtures labeled synthetic.
- Failure analysis: authenticated rule acceptance is now verified in Chrome, but the official files have not been retrieved. Browser navigation to Data did not yield readable file contents during this attempt. No official YAML contract was invented. Submission preflight cannot establish ADK compatibility.
- Integration decision: local foundation verified within documented assumptions; full R0 not accepted. Champion promotion: inapplicable, no model candidate. Rollback reference: baseline commit above; preserve historical reproduction files and any later user changes.
- Next bounded work: retrieve the authorized harness/starter, pin its exact contracts and offline dependencies, implement corresponding integration tests, then confirm the downloaded model path before P1. Runpod and DigitalOcean authenticated reads succeeded again. Cloudflare and SSH remain unverified.


### R0 official contract checkpoint — October 7, 2026

Status: **progress; Linux integration pending**. The asset-access blocker was resolved by authenticated Kaggle CLI using existing local credentials. The official guide, starter, notebook and four host wheels were downloaded and hashed. No task reference fixes were read. See [official audit](22-official-contract-audit.md).

- Baseline remains `20b44be`; candidate identity is in [core-003](../evidence/r0/local-003/receipt.json) and [compiler-004](../evidence/r0/compiler-004/receipt.json). Local tests: 26 passed plus isolated offline CLI checks. Official CPU compilation: unchanged starter plus eight rejection checks passed; three alias probes retained separately, two exposing a documented discrepancy.
- Compiler run: 2026-10-08T00:48:59.081900+00:00 to 2026-10-08T00:48:59.172494+00:00, 0.090594041 measured seconds. Core verification: 0.341357917 seconds. Engineering/session durations not instrumented; no claim of completing an 8–14-hour cycle.
- Correctness: retained algebraic/invariant checks, actual schema export, exact negative-error checks. Software: core/CPU compiler passed; Linux daemon unavailable. Statistics/comparison: no model evaluation, therefore no repair effect estimate. Engineering: isolated dependency tooling; core remains standard-library-only. Evidence: asset hashes, package inventory, source tool signatures and receipts retained. Test-fixture defects and upstream discrepancies are explicitly recorded in document 22.
- Cost: no billable resource created; acquisition traffic/local/API costs not measured. Promotion: no trained candidate or measured performance. Integration: full Linux sandbox/tool execution unresolved, despite successful CPU compilation. Historical compiler-002 negative-check attribution is superseded by compiler-004.
- Next scope: make the installed Docker daemon available or use an authorized bounded Linux worker; qualify the real sandbox/tool contracts. Model path and GPU spending cap are needed for P1, not for CPU compilation. The user no longer needs to download the harness/starter manually. Rollback uses the baseline commit while preserving historical evidence and unrelated changes.


### R0 Linux acceptance checkpoint — October 7, 2026

- Decision: **accept R0/P0 contracts and skeleton**, with all eight P0 deliverables audited in document 20. This closes infrastructure qualification only; no trained candidate or performance promotion.
- Candidate identity: [local-004 source hashes](../evidence/r0/local-004/receipt.json); [Linux receipt 002](../evidence/r0/linux-002/receipt.json) and [audit](../evidence/r0/linux-002/audit.json) pin the integration script, image and supporting evidence. Baseline/rollback reference remains `20b44be`; preserve prior evidence and unrelated changes.
- Software: 26 core tests pass on macOS and Linux; isolated zipapp checks pass; nine CPU compiler checks pass; 25 real-tool integration checks pass. Starter compilation now uses actual bound tools and the official limits builder. Exact synthetic patch transfers into a fresh container and passes there. No test containers remain.
- Mathematical assessment: exact arithmetic and state invariants remain supported by the claim ledger; tool integration adds observed boundary behavior, not a universal proof. Statistical assessment and fair comparison: inapplicable to performance promotion because no model or task cohort was evaluated. Engineering assessment: isolated no-network containers, pinned image, explicit failures and cleanup. Evidence assessment: retained failed Linux run and corrected representation check, immutable receipts and source hashes.
- Timing: Linux integration started 2026-10-08T00:57:32.035081+00:00 and finished 2026-10-08T00:57:42.257523+00:00; measured duration 10.222385958 seconds. Active engineering/session durations were not instrumented; this does not claim an 8–14-hour cycle.
- Costs: no paid resource created; local compute, transfer and API costs unmeasured. Repair rate, latency, confidence intervals and training gains remain unmeasured.
- Unresolved later-phase gates: actual checkpoint/loader, successful graph retrieval on real assets, full offline host installation, official Phase 2 grading, target GPU execution and comparative evaluation. Linux execution here uses AMD64 emulation on ARM64 macOS.
- Next bounded objective P1: receive complete model folder and Kaggle revision, inventory and verify it, establish experiment/storage/runtime caps, then propose the exact GPU allocation and run real inference plus an adapter compatibility smoke test. Prepare provider access as described in document 21; DigitalOcean and R2 allocation is not needed to finish R0.


### Data research update — October 8, 2026

See [document 23](23-data-requirements-and-acquisition-plan.md) for the proposed data plan supporting the user-preferred three 50M-token candidates. This is a research/planning update, not an implementation cycle or permission to spend on teacher generation. External sources are shortlisted, not yet admitted. Mixtures are provisional and total 50M processed tokens per candidate; they do not imply 150M unique source tokens. P1 requires only a small development subset; freeze contamination groups before corpus ingestion. Official task assets total approximately 22.42GB in the saved download listing; expanded environments are extra. Next gate: authenticated source-rule check, task/environment intake and native baseline traces. No training gains or data-quality acceptance are claimed.

### P1 first GPU session — October 8, 2026

Status: **revise / partial integration evidence**, no trained-candidate promotion. [Session report](27-p1-gpu-validation-report.md) records the environment correction, two actual attempts, independent local grading and remaining gates. Remote work lasted about 42 minutes after the approved start; active engineering time and the final billed Pod duration were not instrumented. The server stopped and temporary remote access was cleaned up. The user was notified to stop the Pod. Subsequent documentation and evaluator checks are local.

Next bounded work: finish durable recovery verification for the updated deployment/evidence; resolve official evaluator source selection and baseline compatibility, then investigate tool-call variability with captured failures. No bulk synthetic generation or training begins merely because the model loaded. P4 remains the main synthetic trajectory phase; P5 uses qualified training data for the pilot, and P6 owns the proposed three up-to-50M processed-token candidates.

Recovery closeout: the revised 75-file deployment bundle was published to R2, independently restored and passed all 77 tests from the restored copy ([qualification](../evidence/p1/deployment-restore-003/qualification.json)). The 28 evaluator dependency wheels also passed independent restoration. The separate audit archive was published and a fresh absolute-path restore independently verified all 493 members ([qualification](../evidence/p1/evidence-restore-002/qualification.json)). The first restore returned a passing receipt, but its destination was absent at follow-up; this unexplained discrepancy is retained in `evidence-restore-001/follow-up.json` and that first receipt is not treated as accepted recovery evidence. This archive contains evaluator outcomes and must not be used as agent context or training data. These recovery checks do not waive the remaining P1 acceptance gates.

### P1 local follow-up: final-destination recovery checks

Progress: strengthened restoration to verify the promoted public directory and bind its absolute path before transport callbacks. Two new fault tests passed; the complete local and freshly restored suites each passed 79 tests. A live R2 restore passed the revised path check. Deployment bundle 004 supersedes bundle 003 for this implementation and passed independent restoration ([qualification](../evidence/p1/deployment-restore-004/qualification.json)). The initial missing-directory anomaly remains unexplained; no cause was inferred from the new tests. The fifth unchanged evaluator failure was traced to HTTP fixture response construction, not changed Requests code. P1 remains unaccepted; continue evaluator compatibility and model/tool qualification locally before requesting any further GPU session. No GPU work or training ran in this follow-up.

### P1 local follow-up: actual pytest-process source qualification

Progress: implemented an evaluator-only source gate observing loaded modules inside pytest. The uncorrected environment is rejected before execution; the corrected environment passes the source gate, matches exact snapshot-plus-agent-patch source hashes, and retains all 324 previous per-case outcomes. All 81 local and restored-copy software tests passed. Deployment bundle 005 includes the plugin and corresponding tests and passed independent R2 recovery ([qualification](../evidence/p1/deployment-restore-005/qualification.json)). No GPU inference or training ran.

This strengthens the validity of local measurements without asserting that the organizer runtime has been repaired. Remaining work includes broader model/tool qualification and a defensible resolution of official evaluator incompatibilities. P1 remains unaccepted; the active implementation objective is unchanged.

### P1 requirements audit and resource evidence

The [requirements audit](28-p1-requirements-audit.md) separates the published intake/inference exit criteria from the broader reliability, independent evaluation and training obligations. It indexes actual memory/latency measurements and retains every unresolved limitation. The Pod is now confirmed `EXITED` by an authenticated read. No inference or training was started. The broad objective remains active; this audit is not a phase waiver or an assertion of training readiness. Next work must address a functional qualification gap rather than accumulating redundant packaging or test-count updates.

### P1 network-dependent evaluator qualification — October 8, 2026

The unchanged Requests baseline and captured agent patch were evaluated in the
same pinned Docker image with bridge networking, an explicit local diagnostic
source-path override, and source provenance checked inside pytest. Four timeout
failures disappeared from both runs. Of 324 paired cases, only the target
content-length regression changed (failure to pass); the candidate has 321
passed, one failed, and two skipped (including xfail). The remaining failure
is the HTTP fixture rejecting a negative-port redirect before delivering it
to Requests. Both official aggregate results remain false. This does not
establish Kaggle environment parity or an overall benchmark solve.

Added reusable JUnit comparison that rejects empty reports, duplicate identities,
ambiguous outcomes, declared-count mismatches, and different case sets. All 90
local tests passed. Individual tests are not independent task-level statistical
samples. Evidence: `evidence/p1/repair-network-comparison-001/receipt.json`.
No GPU work or training ran. Next: resolve the fixture/runtime compatibility
boundary without altering benchmark assertions, and continue training-readiness
qualification separately from this single repair.

### P1 clean local repair qualification — October 8, 2026

The unchanged agent patch now receives local resolved=true through the released
verifier: 322 passed and two skipped (one xfail); baseline has 321 passed, one
failed and two skipped. Exactly the target regression changes across 324 paired
cases. See [analysis](../evidence/p1/repair-compatible-comparison-001/analysis.md).
Historical HTTP fixture dependencies and a fresh per-run unpacked-wheel cache
were needed in addition to the previously recorded source-path/network controls.
The runner now records actual fixture versions and manifest identity. All 90
local tests passed. No GPU time or training was used. Official target parity,
broader reliability, and training qualification remain open; do not rerun this
same repair simply to accumulate repetitions.

### Training representation preflight — October 8, 2026

The pinned compressed-tensors path decompresses for forward execution. Static
checkpoint accounting gives 60.8757 GiB of dense BF16 weights, excluding working
memory. The [representation readiness note](31-training-representation-readiness.md)
sets the next CPU gradient/adapter and bounded GPU qualification steps. No long
training run, new weights, or H100 fit is approved by these static calculations.

### Synthetic CPU adapter qualification — October 8, 2026

The real compressed-tensors codec and PEFT passed a synthetic exact-grid
roundtrip, independent gradient comparison, frozen-base check, measurable
adapter effect, and exact adapter save/reload. See document 31 and
`evidence/p1/adapter-cpu-002/receipt.json`. This is CPU Torch 2.14.1, not the
CUDA training runtime. Next qualify a reduced Gemma architecture, masking
and optimizer resume before preparing the full-checkpoint GPU pilot. No
model-training or repair-performance gain is claimed from the toy fixture.

### Reduced Gemma training mechanics — October 8, 2026

Pinned Gemma4 code with random reduced dimensions passed exact adapter coverage,
independent masked-loss and logit-gradient checks, frozen-base integrity, and
bitwise optimizer-resume equivalence under non-reentrant checkpointing and
zero dropout. Receipt: `evidence/p1/gemma-training-cpu-002/receipt.json`. This
does not establish native chat-mask correctness, full-checkpoint training,
CUDA memory fit, stochastic resume, or a performance gain. Next prepare native
conversation masks and loader qualification locally; no GPU work occurred.

### Native assistant supervision — October 8, 2026

Added template-hash-bound assistant masks with exact native text/token identity
and character-boundary checks. Four actual-tokenizer fixtures and three invalid
input checks passed, including exclusion of a tool result containing model-turn
markers. Evidence: `evidence/p1/training-masks-001/receipt.json`. No corpus is
approved by these fixtures; padding/packing and full-checkpoint gradients are
not yet qualified. No GPU work occurred.

### Native batching integration — October 8, 2026

Native assistant masks now feed a strict independent-sequence collator. Actual
Gemma token IDs and full vocabulary passed reduced-model CPU loss/gradient
equivalence checks between a padded batch and token-weighted microbatches
with unequal target counts. Masked padding changes leave loss unchanged.
All 92 unit tests passed. Evidence: `evidence/p1/native-training-batch-001`.
Packing and full-checkpoint loader/CUDA qualification remain open. No GPU
compute or training corpus was used.

### Compressed BF16 loader qualification — October 8, 2026

A reduced random Gemma BF16 model was packed to W4/group32, saved, reloaded via
the pinned Transformers quantizer, and trained for one adapter update on CPU.
Loaded state matches its decompressed reference exactly; base remains frozen;
adapter reload reproduces logits exactly. Receipt:
`evidence/p1/compressed-gemma-loader-001/receipt.json`. Next prepare the bounded
full-checkpoint GPU bundle; no full-model training readiness, vLLM adapter
compatibility, or performance gain is claimed. No GPU compute was used.

### Full-checkpoint test preparation — October 8, 2026

PEFT 0.21.2 metadata satisfies all ten active dependencies against the existing
Linux/Python 3.12 GPU lock; no core-package change is planned. Added a pinned
supplement and a [bounded qualification specification](32-full-checkpoint-gpu-qualification.md)
with an explicit unexecuted profile. Next implement and locally test the worker
and external deadline supervisor. This is preparation, not full-model training
qualification or GPU execution.

### Training supervisor implementation — October 8, 2026

Implemented external POSIX process-group deadlines, stop requests, termination
escalation and interruption cleanup. Seven lifecycle tests passed on macOS and
local Linux; the full suite passed 99 tests. The training worker itself and
GPU integration remain pending. No GPU time was used. Evidence:
`evidence/p1/process-supervisor-001`.

### Frozen-state audit implementation update

Added bounded-chunk state fingerprinting for the training qualification worker,
including parameters and persistent buffers, with explicit adapter exclusions.
Six dedicated CPU tests passed. Integrated the check into the reduced BF16
compressed Gemma loader/adapter probe; evidence is recorded under
`evidence/p1/training-state-001` and `evidence/p1/compressed-gemma-loader-002`.
Full CUDA worker integration and checkpoint qualification remain pending;
this update does not approve a training streak or close P1 acceptance.

### Shared adapter qualification engine

Implemented `zenithsync/training_pilot.py`: exact target/shape and adapter-count
checks, non-reentrant checkpointing, one AdamW update, finite gradient and
parameter checks, frozen state fingerprints, adapter/optimizer export, complete
first-model scope release, independent reload, and predeclared output comparison.
The reduced compressed BF16 Gemma probe passed with 7,808 trainable parameters
and zero reload logit error. Weak references confirmed the first base object
was released before the second load. Ten focused tests passed, including
wrong-target, missing-supervision, altered-reload-base and output-preservation
failures. Evidence: `evidence/p1/training-pilot-cpu-002` and
`evidence/p1/training-pilot-tests-001`.

Remaining: full CUDA entry point, native-tokenized fixture integration, runtime
and storage preflight, memory measurements, supervisor integration and actual
GPU qualification. Optimizer state is saved but resume is not qualified by
this engine. CPU results do not qualify full-model training or repair quality.

### Full-checkpoint command and native fixture integration

Added a deadline-supervised full-checkpoint command and CUDA worker, with
persistent-filesystem checks, exact manifest verification, pinned core runtime
versions, single-device/no-competing-process admission, exact projection count,
native supervision and shared update/reload qualification. Native fixture
preflight passed: 24 input tokens, five supervised targets. Three storage
admission tests passed, including symlink escape rejection. CLI imports/help
are checked without loading the model. Evidence:
`evidence/p1/training-worker-preflight-001`.

No GPU command has been executed. Device-wide memory sampling, curated
deployment preparation and actual full-checkpoint qualification remain open.
The command does not start/stop the Pod or extend session authorization.

### Device-wide telemetry and deployable source closure

Added persistent initial/periodic/final device-memory samples, strict parsing,
identity/capacity consistency and failure propagation. Six monitoring tests
passed; the core suite passed 108 tests with ten separately scoped Torch tests
skipped. Prepared an explicit 19-file source bundle and verified both CLI
imports outside the checkout and in a network-disabled Linux container.
Evidence: `evidence/p1/gpu-memory-monitor-001` and
`evidence/p1/training-deployment-001`. Device readings are sampled maxima,
not continuous peak bounds. Full CUDA execution remains unperformed; no
training-corpus or coding-quality claim follows from this preparation.

### H100 full-checkpoint attempt and setup diagnosis

Verified persistent storage, idle H100, 251 runtime pins and PEFT dependencies.
The full checkpoint loaded/decompressed, but the first qualification attempt
was stopped after 278.84 seconds of prolonged CPU-heavy setup. Supervisor
cleanup and zero remaining GPU memory were confirmed. No update/reload success
is claimed. Default Torch thread counts were 104/104; added explicit 4/1 thread
limits and stage timestamps for the next bounded attempt. Ten focused tests
and the reduced compressed-model probe passed after this instrumentation.
Evidence: `evidence/p1/full-training-gpu-001`,
`evidence/p1/training-thread-limit-001`, `evidence/p1/training-pilot-cpu-003`.

### Full-checkpoint H100 one-update qualification passed

The revised bounded worker completed in 216.195 seconds. All 30,607,360
rank-four adapter parameters matched expected targets/counts; loss and gradients
were finite; an optimizer update changed the adapter; frozen state remained
identical; export and fresh reload reproduced logits exactly. The diagnostic
used only one 24-token synthetic example with five supervised targets.
Peak Torch allocated/reserved memory was 60.919/71.961 GiB; maximum sampled
device-wide memory was 72.632 GiB. Process cleanup and zero remaining GPU memory
were confirmed. The temporary session SSH key was removed, preserving other keys.

Complete outputs remain on the network volume and in a local copy verified
against the remote manifest. Evidence: `evidence/p1/full-training-gpu-002`;
large artifacts: `artifacts/official/p1-full-training-gpu-002`;
R2 publication: `evidence/p1/full-training-gpu-publish-002`.
P1 remains open. Next functional gates are full-model resume/stability and
realistic sequence-length admission, adapter serving compatibility, qualified
data ingestion and held-out agent evaluation. No long training streak has begun.

### Optimizer export audit and identity-bound resume contract

Audited the actual H100 export locally: all 820 states/30,607,360 parameter
elements have finite moments, nonnegative second moments, step one and
first-step Adam consistency within a declared numerical tolerance. The old
export has no names, so full-model resume remains unqualified. Added explicit
ordered name/shape/dtype and hyperparameter validation for new optimizer
checkpoints. Five contract tests and four engine failure tests pass; a reduced
Gemma export/reload probe passes with the new format. No GPU run occurred for
this change. Evidence: `evidence/p1/exported-optimizer-audit-002`,
`evidence/p1/optimizer-contract-001`, `evidence/p1/training-pilot-cpu-004`.

### Pinned public-data quarantine intake

Acquired and hash-verified one 151.8 MB SWE-Hero shard plus pinned source cards
and Nebius metadata/LICENSE. The shard contains 2,500 distinct issue records
over eight repositories; the first-shard selection is not representative.
Metadata-only inspection found no exact competition-repository overlap but
identified missing explicit tool-response IDs and no row-level resolved field.
No trace body or patch was read by this audit and no source was training-approved.
Implemented bounded publisher-hash verification, four download tests, and a
metadata-only audit. See [current findings and admission work](33-public-data-intake.md).

### Source-history conversion without fabricated tool outcomes

Implemented a strict SWE-Hero converter that preserves source call IDs, links
responses only to one outstanding call, retains unanswered terminal finish
calls, and records inferred-link provenance. All 2,500 acquired histories passed
its structural contract: 296,414 messages and 144,457 inferred links. Five
rejection/preservation tests passed. No commands were executed, no task-success
label was invented, and no source tool was renamed to imply runtime equivalence.
Native pending-call supervision, tool semantics, replay, rights and broader
contamination remain open. Evidence: `evidence/data/swe-hero-conversion-audit-001`.

### Native supervision qualified; long-context admission gap measured

Added explicit terminal-tool supervision without weakening default complete
history checks. Four contract tests and six positive/six negative native
tokenizer fixtures pass. A predetermined per-repository sample of eight real
trajectories passes full render/token identity and mask checks without truncation.
Lengths range from 32,376 to 114,224 tokens; seven exceed the current 32,768
serving cap and all exceed the actual 24-token GPU qualification fixture.
Next data admission work must address context handling jointly with the runtime,
not silently truncate traces. Tool semantics, replay, rights and contamination
remain open. Evidence: `evidence/data/native-trajectory-masks-001`.

### Imported-history causal ordering correction

Found that naive native rendering moves source assistant text accompanying a
tool call behind its result. This affects 104,196 result-followed messages in
the acquired shard. Added an explicit, provenance-preserving field projection
into Gemma's pre-action channel, with guards against later-user text loss and
reasoning-field collisions. The native synthetic fixture verifies chronology
and invariance of earlier tokens under changed future results. Four unit tests
pass; all 2,500 histories meet structural projection preconditions and the same
eight sampled traces pass native mask checks. Their lengths remain too large
for current admission. Earlier mask results were format consistency, not proof
of semantic chronology. No training data was promoted and no GPU was used.

### Full-shard context measurement and admission decision

Measured all 2,500 projected native histories without truncation: 120,914,948
input-token occurrences, median 44,981, maximum 183,776. Only 250 histories fit
32,768 input tokens, with NumPy/pandas increasing to 82% of that retained subset.
None fit 16,384. Eight prior native-mask cases match exact token hashes. Two new
statistics tests pass; the core suite has 127 passes and 15 explicit skips.
Evidence: `evidence/data/context-census-001`; details and mathematical target
accounting are in `docs/33-public-data-intake.md`. Next implement and replay-test
a shared runtime/training context policy before admission; do not silently
truncate or count these raw input tokens toward approved candidate budgets.
GPU use remains unnecessary for this local data-policy work.

### Competition context configuration and summarizer audit

The local repair driver left compaction and cache disabled, unlike the acquired
competition README. It now supplies documented settings using pinned ADK 1.36.1
and records them in attempt receipts. Deployment bundle 006 includes the helper
and passes archive verification and isolated CLI import. The actual-ADK offline
probe reproduces omission of structured tool calls/results from summary input.
This is a diagnostic finding, not a successful memory mechanism. Core suite:
127 passed, 15 skipped. No GPU or real summarizer call was made.

Revised next step: reproduce the pinned runner's selection/trigger behavior and
official request stream before designing context transformations. A custom
compactor needs a supported competition deployment path. Future admitted data
must retain actual summary/continuation pairs and evaluate observation recovery.
Historical repair evidence does not establish compaction compatibility.
Evidence: `evidence/p1/harness-compaction-002`.

### Runner-level compaction reproduction

Ran three actual-ADK offline cases with six local tool calls inside one user
invocation. Synthetic prompt usage 14,335 produced no compaction; 14,336 produced
five summaries and excluded the oldest tool observation from later agent input.
The disabled control retained it. Original tool events remain in session storage.
The runner compacts before model calls as well as post-invocation; the earlier
docstring-based post-invocation description was incomplete and is corrected.
Source bytes match pinned ADK. These are synthetic-model integration tests, not
GPU or learned-agent performance tests. Evidence: `evidence/p1/compaction-runner-002`.
Next qualify recovery and capture actual summaries during a bounded future
GPU session; local context/data work remains available before that session.

### Supported source-observation recovery candidate

Added a separate untrained declarative candidate with an ADK source-observation
skill. It saves actual source excerpts outside the repository and checks whole-file
freshness before recall. Five focused tests pass. The pinned compiler and actual
ADK script wrapper pass snapshot/recall/staleness checks across separate processes.
This does not yet qualify the production sandbox or demonstrate model adoption
and repair gains. Compare against the preserved baseline after executor and
compaction-recovery integration checks; account for added tool/token costs.

The compiler version guard detected older packages in the general environment.
Pinned versions now run in an isolated overlay; the earlier compaction config
check was repeated under the correct harness and still passes (probe 003).
Evidence: `evidence/p1/observation-skill-001` and `harness-compaction-003`.

### Actual Docker skill execution and patch isolation

The recovery candidate compiles against real bound tools and executes through
the released sandbox executor in a pinned local Linux container with networking
disabled and no host mounts. Exact recall survives separate calls; actual source
edits invalidate records. The workspace stays clean until the intended source
edit, and official patch extraction includes only that edit. The owned container
was removed and cleanup verified. Evidence: `evidence/p1/observation-sandbox-001`.
No GPU or model was used. Next integrate deterministic compaction/recovery and
cost accounting before testing whether Gemma uses this capability effectively.

### Compiled candidate through runner compaction and real skill dispatch

Integrated actual ADK runner/compaction, compiled candidate, bound tools and
Docker executor in two controlled cases. A scripted summary retaining the handle
permits exact source recovery after the original observation leaves context;
dropping the handle prevents recovery. The source marker is fresh, and recall
uses only information present in the current model request. Snapshot/recall each
consume one harness tool call; summary requests are reported separately.
Evidence: `evidence/p1/observation-recovery-001`. No model quality, real token
cost, learned retention rate or training-data claim follows. Both containers
were removed. Next learned-agent comparison needs an explicitly bounded GPU
session; local source-data qualification and ingestion remain open in parallel.

### Actual Gemma paired development run

Used the still-running H100 within the existing approved four-hour session.
The driver now selects either immutable candidate and records its identity;
both use the same checkpoint, 40-turn/40-tool/10-minute budgets and documented
compaction. Deadline enforcement reserves 30 seconds for cleanup. Deployment
bundle 007 includes both candidates and manifests. Core suite: 132 passed,
15 skipped. Neither candidate was modified between attempts.

On repeated development task `requests_6589`, both produced source patches and
passed the paired compatible local grading. The base hit the turn limit despite
submitting; the observation candidate finished without an agent error but used
no skill tools. Captured total tokens, including summary requests, were 384,697
versus 312,008. This single ordered pair does not establish an efficiency gain,
and cannot attribute any difference to unused observation recovery. Do not adopt
or train toward the candidate on this evidence alone. Next select an independent
development scenario where loss/recovery is actually exercised, with a fixed
comparison protocol and no oracle leakage.

Initial grading used the wrong original container image and failed the source
origin measurement before tests. Both failures remain in grade-001; grade-002
uses the previously qualified compatibility image and passes source checks.
Results are local diagnostics with a source-path override and network-enabled
test environment, not hidden-grader parity. Evidence:
`evidence/p1/observation-comparison-live-001` and `observation-comparison-grade-002`.
Server ran 441.32 seconds including startup, shut down cleanly, and GPU memory
returned to zero. Temporary SSH access was revoked and the tunnel closed.

### Corpus tool contracts and success-label qualification

Audited argument shapes for all 2,500 acquired histories. Found 1,874 root-directory
views, 231 shell-input calls across 122 histories, 468 explicit shell timeouts,
six editor undos and 298 open-ended view ranges. These require explicit semantic
handling; ordinary tool renaming is not a valid native-runtime conversion.
The linked paper also retains unresolved Hero trajectories, and its reported
composition differs from the pinned card. No row-level success is inferred.
Evidence: `evidence/data/source-tool-contracts-001`. Next join source tasks and
base-state metadata, then replay or regenerate with native tools before admission.

### Source task metadata recovered

Acquired and checksum-verified all 4,578 R2E-Gym subset tasks (~944 MB compressed).
All 2,500 acquired Hero trajectories join to a source task. Added a strict metadata
projection that excludes oracle content and distinguishes unresolved first-parent
references from actual base commit hashes. The initial full-hash assumption was
rejected by real data and corrected; no environment or training admission follows
from the join alone. Core suite: 137 passed, 15 skipped.

Next: resolve base references and image digests, audit oracle isolation in actual
source environments, then qualify native tool replay/regeneration. No GPU run is
needed for the metadata stage. Evidence: `evidence/data/source-task-join-001`.

### Source environment resolution and isolation finding

Completed R2 readback verification for all eight source task shards (~944 MB).
Resolved immutable Linux/amd64 image digests and first-parent commits for a fixed
eight-repository sample. Local inspection of the first sample (Pyramid) confirmed
the intended base commit but also accessible solution Git objects and generated
grading tests. The inspection container was removed; no GPU work was used.
Core suite: 140 passed, 15 skipped.

Next implement a sanitized agent snapshot with an independent evaluator, verify
that intended source/dependencies still execute, and then qualify native replay.
Do not promote these trajectories based on metadata joins or publisher labels.
Evidence: `source-environment-resolution-001`, `source-image-probe-001`.

### Sanitized source snapshot and reference-control qualification

For the fixed Pyramid task, built a fresh one-commit workspace that preserves
the exact original Git tree (891 paths) while removing known grading artifacts
and original solution history from the agent-visible filesystem. Original versus
sanitized repository tests match on all 2,470 cases: 2,433 passed/37 failed each.
Shared failures remain unresolved; this is preservation evidence, not a green
repository or general isolation guarantee.

Separate evaluator controls reveal a lossy upstream test-name convention. Added
an all-members comparison that preserves full case identities and the publisher's
expected failures. The reference matches all 994 actual cases; the buggy base has
19 mismatches. No learned agent ran and no trajectory was admitted to training.
Next connect native tools and patch export to this sanitized/evaluator split,
then expand qualification across the preselected repositories. Continue locally.

### Native source workspace and patch transfer

Added a reusable snapshot-to-native-workspace adapter with source identity checks
and strict handling of the known installer leftover. Qualified actual native
command/read/edit/submit operations, empty baseline submission, byte-identical
patch application in a separate evaluator, and unchanged results across all 994
evaluator cases. This used an explicit random-comment transport fixture with no
model invocation, so it earns no repair credit and is excluded from training.

Evidence: `evidence/data/native-source-transport-006`, with earlier integration
failures retained. Next expose the sanitized/evaluator split through a repeatable
task runner, including task-prompt provenance and runtime budgets, before any
model-driven rollout or corpus admission. Broader repository qualification and
the training campaign remain open; local work does not require a running Pod.

### External task packaging and rollout-driver dry-run

Prepared a manifest-backed task package with disjoint model-visible and evaluator
projections, including an opaque task ID and source issue hash verification.
Added a bounded ADK source-task driver and verified its dry-run using pinned SDKs.
Its model execution path remains unqualified; no GPU restart is needed yet.
The core suite has 148 passed and 15 skipped. Next exercise its actual lifecycle
with an explicit offline fixture and connect independent patch grading.
See `34-source-task-runtime.md` for artifacts, scope and remaining gates.

### Actual offline source-runner lifecycle

Ran five scripted fixtures through the actual new ADK/Docker execution path:
success, exception after submission, asynchronous model timeout, 40-turn limit,
and 42 requested tools against a 40-call budget. Verified exact patch retention,
40 successful/2 rejected batched calls, model-input metadata separation, and
cleanup of all five containers. No model quality or training credit is assigned.
Evidence: `source-runner-lifecycle-001`, `source-runner-lifecycle-audit-001`.
Next: slow-tool cancellation, cleanup-failure receipts, independent grading of
saved outputs, and real HTTP behavior. GPU execution is still unnecessary.

### Independent saved-patch grading and bounded native commands

Added manifest/identity-checked grading of saved runner patches in a separate
evaluator. The scripted file-addition fixture remains unsolved (19 mismatches),
and tampered/unsubmitted/wrong-task inputs reject before evaluator execution.
Verified native slow-command timeout with no delayed file write after its
scheduled time. Cleanup failures now retain explicit uncertainty in receipts;
controlled API-failure tests and a live successful cleanup pass.
Core suite: 151 passed, 15 skipped. No model inference or GPU work occurred.
Next qualify the real HTTP client path locally, then broaden task qualification
and corpus preparation before requesting a GPU session.

### Production-client loopback HTTP qualification

Exercised the real registered HTTP client against explicit local scripted
responses. Native tool calls/results round-trip and produce a saved patch;
503 fails after one request without retries. Both paths clean up their servers
and containers. Independent grading preserves the fixture label and reports
the expected unsolved baseline, not model success. No GPU was used.
Evidence: `source-http-client-audit-001`. Next expand source data/environment
coverage and admission; Gemma execution and training remain separate gates.

### Source contract census update

The complete pinned R2E source census now covers 4,578 tasks / ten repository
basenames. One Orange3 contract has a blank test identity; 2,203 otherwise valid
contracts include expected failures/errors. All remain unapproved for training
until runtime controls establish a reproducible repair signal. Expand repository
qualification before scaling native rollouts. See `34-source-task-runtime.md`
and `evidence/data/source-expectation-corpus-001`. Pod remains stopped; this work
and the 170-test local suite require no GPU.

### Tornado runtime qualification update

Two independent base/reference runs now qualify one Tornado evaluator task:
29/30 passes at the buggy base, 30/30 at the reference, with exact publisher
expectation agreement only for the reference. Both repeats match, and source
integrity and cleanup checks passed. This expands evaluator coverage beyond
Pyramid; source snapshot isolation and native trajectory execution remain next.
No training examples were admitted and no Pod restart was needed.

### Tornado workspace update

The exact-tree sanitized Tornado snapshot now passes native import/read/empty-
submission checks. All 28 original gen_test cases give identical passing outcomes
before/after sanitization. The shared workspace probe also passes on Pyramid.
Next: native patch transfer and teacher trajectory replay, with independent
Tornado grading. Preserve the distinction between 28 original repository tests
and 30 generated evaluator tests. GPU remains unnecessary for these checks.

### First independently graded teacher replay

One pinned Tornado Hero trace now executes through adapted native tools and its
saved patch passes all 30 independent grading cases. The replay has 58 charged
calls and exceeds the 40-call competition profile. It is explicitly not admitted
to training. Next qualify fresh-observation trajectory construction and context/
mask limits, then expand replay coverage without treating this single success as
population-level evidence. All work was local; no GPU or new model generation.

### Native training representation update

The twice-graded Tornado replay now has a fresh-observation, action-only native
history: 59 exchanges, 28,933 input tokens, 6,764 supervised targets, exact native
Gemma token/mask checks passing with nine tool schemas and no truncation.
This is diagnostic data, not admitted training data: the reconstructed prompt
and 58-call trajectory require explicit policy and fidelity checks. Next expand
budget-compatible source replay coverage and qualify training memory using
measured sequence lengths before requesting another GPU session.

### Corpus-scale replay selection

The 2,500-trace census yields 417 histories within the estimated 40-call budget,
including 136 joint source-context/call-budget candidates without known adapter
flags. A deterministic eight-repository shortlist has pinned image/revision
metadata ready for qualification. Prioritize these new candidates before more
long-trace demonstrations. Use fresh native lengths and independently graded
patches for admission; source metadata is only a replay-cost screen. Local suite:
180 tests run, 165 passed, 15 skipped.

### Budget-compatible replay milestone

The selected shorter Tornado trace now replays in 33 calls under the enforced
40-call ceiling, passes all 39 independent grading cases, and renders into
14,884 native input tokens with 3,890 supervised targets. Source build/replay
configuration is reusable and validated. This is evidence for one teacher repair,
not trained Gemma performance or corpus admission. Next extend the same pathway
to the selected Pyramid candidate, then other repositories, while maintaining
rights/contamination and fresh-observation admission gates. No Pod needed yet.

### Cross-repository budget-compatible replay

The selected Pyramid trace now replays in 29 calls, produces a patch matching
all 835 independent case expectations (80 remain expected failures), and renders
into 18,924 input / 3,868 supervised tokens without truncation. Together with
Tornado, two repositories now have budget-compatible graded teacher histories.
Shared replay/grading entry points replace task-specific implementation names;
compatibility wrappers preserve earlier commands. Next expand to additional
selected repositories and resolve admission gates; these two traces do not form
an abundant training corpus or prove Gemma performance. No GPU was used.

### Admission evidence and source-license correction

Live rules review confirms conditional external-data/model allowance. Current
GitHub repository-ID/fork-network metadata shows no overlap between the eight
source repositories and four reserved official repositories. This is a limited
identity screen, not semantic contamination clearance. Exact source notices
revealed that Pyramid's MIT row label does not describe its mixed-license tree;
keep it quarantined pending file-level review. Preserve Tornado's Apache notice
and all transformation attribution. See `35-data-rights-and-evaluation-isolation.md`.
Do not scale acquisition based on unverified publisher license labels alone.

### P1 local follow-up — 2026-10-09: replay source provenance

- Verified the admission-review R2 upload: 23 files, 116,081 bytes, remote hash
  readback complete (`admission-review-publish-001`).
- Exported the short Pyramid replay's three directly observed source files from
  its immutable snapshot; matched the recorded reads and final edited read with
  explicit terminal-newline normalization. Accounted for all 19 shell outputs.
- Narrowed the rights finding: this trace does not show rendered docs bodies,
  but its source is not MIT-only; dependency warning snippets and derived
  redistribution notices still require coverage. Kept training approval false.
- Recorded a concrete quality hazard: a teacher-written test prints failure while
  exiting zero. Independent grading, not exit status or success prose, controls
  outcome labels. No GPU work was started; P1 remains incomplete.

### P1 local follow-up — linked replay preflight

Added `assess_replay_admission.py` and its consistency-checking module. Saved
patches, grades, native history, event mappings, schemas and token audit now have
an executable cross-artifact check. Reconstructed histories and charged-call
counts are independently compared; no training approval is issued by this tool.
The two short traces pass these mechanical checks. The long Tornado trace fails
both the 40-call limit and the 32,768 context limit with an 8,192 output reserve.
Local suite: 190 run, 175 passed, 15 skipped. Rights/split/runtime gates remain;
no Pod restart or training campaign was performed.

### P1 local follow-up — full pinned trajectory acquisition

Expanded acquisition from one to all 14 SWE-Hero shards at the same immutable
revision. Publisher size and SHA-256 checks passed. The full metadata census has
34,269 trajectories, 1,695 repository names and 11,766 repository–issue pairs,
with no duplicate trajectory IDs. It found 73 encode/httpx rows overlapping a
reserved repository; these are explicitly flagged for exclusion. No trajectory
or patch bodies were read by the census. See `36-full-trajectory-corpus-intake.md`.

This materially broadens the raw supply, but 22,503 trajectories repeat existing
issues, and 24,048 rows come from source datasets outside the currently qualified
R2E task adapter. Do not extrapolate the two successful native replay examples to
this corpus. Raw R2 transfers are underway; use each verified publish receipt
before claiming a shard is stored remotely. Training admission remains false.

### P1 local follow-up — verified R2 corpus and expanded task join

All 14 pinned raw shard bundles are now verified in R2 (2,402,170,043 bytes,
including cards/metadata), with manifest-linked receipts. A separate 151,559,597
byte shard restore passed destination checksum validation. The full census bundle
is also remotely verified. No GPU was used.

Expanded the task join to consume the verified full metadata index. Exclusion
runs before source selection: 73 reserved-repository rows excluded, 10,221 R2E
traces joined to 3,442 unique tasks, zero unmatched R2E traces, 23,975 other-source
rows left outside this adapter. This joins identities only; broad environment,
rights, native token/mask and replay admission remain incomplete. Local suite:
194 run, 178 passed, 16 skipped; separate PyArrow census integration passed.

### P1 local follow-up — SWE-rebench filtered source join

Implemented a metadata-only adapter for the largest remaining trajectory source.
The pinned 6,542-task filtered table joins 17,798 traces to 6,125 tasks across
1,686 repositories. All 73 reserved-repository rows are excluded first. There
are 318 unmatched traces across 111 tasks; investigate the larger source release
rather than guessing mappings. Nine matched rows lack publisher license terms,
and 103 declare ZPL 2.1; rights remain unresolved despite simplified trajectory
labels. Image strings exist for all matched rows but are not digest-resolved or
runtime-qualified. See `37-swe-rebench-source-adapter.md`.

Validation for this adapter: 198 tests run, 182 passed, 16 skipped. The raw
filtered table is remotely checksum-verified in R2. Missing terms, unmatched
identities, unresolved images and evaluator qualification remain explicit gates;
no training or GPU work was performed.

### P1 local follow-up — full SWE-rebench task identity coverage

Acquired both full-release task shards at the pinned revision and extended the
join command with an explicit source split. All 18,116 nonreserved SWE-rebench
traces now match 6,236 tasks across 1,687 repositories. The previously unresolved
318 traces map to 111 tasks without image references: do not substitute guessed
images. Filtered results reproduce exactly, and all common task metadata agrees.
Source shard hashes and row positions are retained for controlled retrieval.
Suite: 198 run, 182 passed, 16 skipped. No GPU work or training approval.

### P1 local follow-up — SWE-rebench images

Pinned all eight images in a reproducible cross-repository metadata sample. Pulled
only the smallest (1.27 GB compressed) locally and inspected it in a read-only,
networkless container. Its Git HEAD matches the task base and tracked files are
clean, but 624 commits and extra root files remain accessible. This is not yet
an isolated agent image. Next: source sanitization and independent evaluator
controls. The probe container was removed; no task tests, agent or GPU ran.
Suite: 200 run, 184 passed, 16 skipped. See the source-adapter document for scope.

### P1 local follow-up — SWE-rebench source snapshot

Built and independently verified a parentless exact-tree snapshot for the first
SWE-rebench image: 30 files/290,019 bytes preserved; old base/head/merge commits
inaccessible via Git; root issue/env artifacts removed. An initial first-parent
assumption failed and was retained as evidence. Explicit ancestor validation now
supports multi-commit SWE-rebench PRs; R2E retains its strict first-parent default.
Task evaluator and runtime compatibility remain unverified. Docker lower layers
retain original bytes and must not be agent-accessible. Latest suite: 204 run,
188 passed, 16 skipped. Improved file-mutation diagnostics without weakening the
guard; intermittent source-metadata changes remain an open local reliability issue.


### P1 evaluator qualification update — 2026-10-09

Biolink task 172 base/reference controls both stop in fixture setup (93/93
errors each); no test assertions execute. Captured and hash-pinned the two
Biolink 4.2.1 resources required by the fixture. Offline replay and paired
assertion-level verification remain outstanding; see document 37. New
resource/diagnosis bundles still require R2 publication. Pod remains stopped.


### P1 offline evaluator controls — 2026-10-09

Biolink task 172 now reaches all assertions offline: base 92/93 passing and
reference 93/93 passing, with the intended failure-to-pass transition. Exact
resource bodies are hash-pinned; no assertions changed. Full suite: 210 tests,
22 skipped; six adapter tests passed separately. Continue with source-harness
identity mapping and sanitized-image parity before admitting trajectories.
Pod remains stopped; this is evaluator evidence, not model improvement.


### P1 sanitized source controls — 2026-10-09

Confirmed task-172 evaluator equivalence between original and sanitized images:
all 93 full identities have identical outcomes; all 82 publisher expectation
groups match without suppressing collisions. Added strict paired-control
validation and five adversarial tests. Suite: 215 tests, 193 passed, 22 skipped.
Continue source trajectory integration and rights/admission work; no model
performance claim or training readiness follows. Pod remains stopped.


### P1 candidate grading path — 2026-10-09

Task-172 patch grader now rejects an empty repair, accepts the known reference
repair, and rejects added test files before execution. This establishes grader
behavior only. Full suite: 217 tests, 195 passed, 22 skipped. Located three
source trajectories for provenance/action review and subsequent native replay.
Runpod remains unnecessary and stopped; training admission remains pending.


### P1 teacher data screening — 2026-10-09

Verified all three task-172 trajectories. Their 55/56/49 executable actions
exceed the 40-call limit. Editor-only diagnostic projections distinguish one
failing repair and one passing repair; the second trace needs state-divergence
analysis. These are not full replays or training-admitted examples. Prioritize
third-trace native replay, followed by independently validated shorter data.
All work remains local; no Pod restart is needed.


### P1 native Biolink replay integration — pending runtime result

Implemented task-environment selection, pinned response staging, and explicit
source-shard loading for native replay. Suite: 219 tests, 197 passed, 22 skipped.
One local replay process is live but waiting on dependency reads before
container startup (session 46435). Preserve and poll it; no duplicate run.
No new training admission, replay completion, or GPU requirement is claimed.


### P1 source-state discrepancy audit — 2026-10-09

Isolated the second teacher trace's first replacement mismatch to one line's
four-space indentation difference. Preserve source-state uncertainty and do
not force the trace to apply. The original native replay process remains live
in dependency loading; continue polling session 46435 before any retry.


### P1 corpus-wide budget screening — 2026-10-09

Completed static screening of all 34,196 non-reserved traces (73 excluded).
4,507 fit estimated 40-call cost without currently detected adapter flags,
covering 2,753 distinct issues across 913 repositories. This expands the
replay-candidate pool; it does not admit training data or prove token sufficiency.
The original Biolink replay session 46435 remains pending dependency imports.
Continue that exact process, then prioritize additional candidates from the
corpus-wide pool with issue-level isolation and independently graded outcomes.


### P1 budget-first environment cohort — 2026-10-09

Bound 2,621 image-backed, statically budget-fit SWE-rebench trajectories to
1,575 issues / 902 repositories. Resolved eight deterministic image identities
from this cohort without downloading layers. Prefer this pool for additional
replays; it remains unqualified for training. Existing Biolink replay session
46435 continues, with no duplicate workload or Runpod restart.


### P1 replay retry after verified terminal failure

Biolink replay-001 ended during resource hash validation; its container cleanup
is verified. Both resources subsequently matched stable pinned hashes. Fresh
replay-002 (session 88472) is now running; poll it before any further retry.
Budget-cohort evidence R2 publication verified. Runpod remains stopped.


### P1 native SWE-rebench success; admission still pending

Rebuilt a self-contained native harness runtime to avoid workspace dependency
read stalls; core pins and shared dependency versions retained, import-origin
and dependency checks passed. Native Biolink replay-003 completed with fresh
observations and a submitted patch that independently matches all 93 expected
test outcomes. Both containers cleaned up. Its 48 charged calls exceed the
40-call limit, so this remains compatibility evidence, not admitted training
data or model performance. Next: audit native masks/context and accelerate
qualification of budget-fit corpus candidates. Runpod remains stopped.


### P1 native context and mask audit — 2026-10-09

Linked Biolink replay, exact patch grading, reconstructed native history, and
pinned-tokenizer masks. History: 26,118 input / 5,530 supervised tokens; input
plus reserve 34,310 exceeds 32,768, and 48 calls exceeds 40. Admission checker
correctly rejects both constraints. Extended grading-backend identity checks;
full rerun 221 tests, 199 passed, 22 skipped. Keep this as compatibility evidence
and pursue budget-fit corpus candidates; no GPU training is authorized by these
results and Runpod remains stopped.


### P1 budget-fit task triage — 2026-10-09

Completed provenance-bound issue/environment extraction for eight budget-fit
SWE-rebench tasks without reading solution/test patches. Reviewed test breadth,
issue type and estimated call counts; prioritize nodebook AST repair (35 calls,
1 new regression / 18 preserved tests) for the next environment qualification,
then an encoding case. Counts are publisher declarations, not execution results.
Do not equate static call fit with native token fit or corpus admission. Keep the
full data goal unchanged; next work is local snapshot/evaluator qualification.
Runpod remains stopped. Detailed comparison: document 37.


### P1 second SWE-rebench evaluator qualification — 2026-10-09

Nodebook original-image paired controls reproduce 19/19 expected transitions
(18 base passes to 19 reference passes). Generalized evaluator input extraction
and explicit execution profiles; Biolink regression still matches 93/93
transitions. Full local suite: 201 passed, 22 skipped after metadata-guard
failures were retained and stable reruns completed. No GPU used. Next qualify
sanitized Nodebook source and replay/context, then expand corpus admission;
original-image tests alone do not approve a training example.


### P1 budget-fit native replay — 2026-10-09

Nodebook second snapshot preserves its exact tracked tree and reproduces all
19 original-image test transitions. First replay safely rejected a retained
untracked issue file; declared cleanup was corrected and a new snapshot verified.
The subsequent native teacher replay completed within 35/40 charged tool calls,
submitted a hash-bound patch and cleaned up. Patch grading and native context
admission remain pending. Added reusable snapshot verification and exact teacher
selection; full suite 202 passed / 22 skipped. Runpod remains stopped.


### P1 Nodebook mechanical candidate qualification — 2026-10-09

Independent replay-patch grade matches 19/19 expected outcomes; empty-patch and
unauthorized-file negative controls behave correctly. Pinned token audit yields
17,353 input / 4,183 supervised tokens; with 8,192 reserve, context is 25,545 of
32,768. Tool budget is 35/40. Linked mechanical admission passes. This remains
unapproved training data pending rights, frozen split/duplicate checks, remaining
source qualification and GPU runtime validation. Full suite 204 passed / 22
skipped, followed by focused allowance checks and regrading. Keep Runpod stopped.
Next advance corpus rights/isolation and assembly using this linked evidence.


### P1 provenance and trainable candidate export — 2026-10-09

Captured Nodebook tracked source and identified dependency notices; compared all
four direct-read spans, retaining one truncated tool observation. Added an
attribution record. Expanded identity isolation to the eight selected source
repositories and four reserved repositories; no current declared fork-network
or canonical-ID overlap. Semantic duplication and frozen splits remain open.
Exported actual token/label arrays, matching prior audit hashes and collator
counts, into quarantine for later corpus assembly. The GPU worker remains a
synthetic fixture qualifier, not yet a production corpus trainer. Next implement
corpus isolation/assembly and the real-data training path under explicit gates.
Runpod remains stopped.


### P1 real-data corpus loader and deployment preflight — 2026-10-09

Implemented portable quarantine corpus assembly and a hash-bound loader. It
validates token/audit identities, exact label/count accounting, aggregate bytes,
no truncation, duplicate sequences and declared cross-split families. Separate
content-bound rights/split/runtime receipts are required for training loads;
these are consistency gates, not proofs of arbitrary receipt authenticity.
Assembled one real Nodebook candidate (17,353 input / 4,183 supervised targets).
Staged CLI inspection passes outside the repository, and training-purpose access
is denied for the real quarantine corpus. Full suite: 212 passed, 22 skipped.
The first source-bundle staging attempt rejected filesystem metadata drift on
p1-training-pilot.json; stable rereads and a fresh bundle succeeded without
weakening inventory guards. The GPU qualification worker is still fixture-based.
Next: deterministic bounded real-data batching, token-weighted optimizer loop
and resumable corpus state. Details and current limits are in document 38.
# Corpus optimization progress — 2026-10-09

Implemented whole-example deterministic schedules, exact supervised-target
accounting, verified data-cursor resume, and single-device token-weighted
gradient accumulation. Eight focused CPU tests passed, including bitwise
deterministic optimizer/cursor resume. A reduced actual Gemma backend test passed
loss, gradient and AdamW batch-equivalence checks. Repository suite: 243 tests,
216 passed, 27 skipped. Four staged CLI imports passed. See document 38 and
`evidence/p1/corpus-optimization-001` for scope and tolerances.

No Pod restart or training campaign occurred. The real candidate remains
quarantined. Next work is bounded corpus iteration and complete worker/checkpoint
integration, followed by admitted data expansion and real-sequence GPU memory
qualification. No full-scale readiness, accuracy gain or error-free guarantee is
established by these CPU checks.
# Indexed corpus progress — 2026-10-09

Added an indexed corpus reader that validates all examples and split/admission
invariants before exposing metadata, then rehashes token files on demand.
The schedule CLI now avoids retaining all token arrays. Real Nodebook fetches
and schedule/update files match the materialized implementation exactly.
Twelve corpus tests pass; the full suite has 247 tests, 220 passed and 27 skipped.
Four staged CLI imports pass. No GPU or optimizer execution was performed.

This bounds retained token data to individual examples, not total process RSS:
manifest metadata and per-example JSON decoding still consume memory. Next:
connect indexed fetching to bounded training microbatches and complete resume
checkpoints, then qualify full-model GPU behavior. Data remains quarantined.
# Streamed optimizer integration — 2026-10-09

Connected indexed training data to supervised-token-weighted accumulation with
one complete example resident at a time. Exact metadata/target checks and
end-of-stream validation precede the optimizer step. Synthetic admission fixtures
verify numerical equivalence and error paths; weak-reference checks verify tensor
release before fetching the next microbatch. Twenty-four focused tests passed,
including reduced Gemma; four stream tests passed after the tensor-lifetime test
was added. The repository run had 250 tests, 220 passed and 30 skipped.

The corpus-update bridge is implemented, but the full worker/checkpoint/RNG
integration remains open. Actual data remains quarantined, and no GPU was used.
Full-model long-sequence memory and BF16/LoRA behavior require a later authorized
GPU session after local integration is ready. See document 38 for limitations.
# Stochastic resume progress — 2026-10-09

Implemented global Python/NumPy/Torch RNG capture and validated restoration with
runtime/determinism settings bound to the payload. CPU dropout training resumes
with exact loss, weight and AdamW moment agreement after model/optimizer/cursor
reconstruction. Eleven focused tests and four staged CLI imports pass. No GPU
used. CUDA RNG recovery remains untested; custom generators and worker processes
are out of scope for this helper.

Next: atomically publish and restore a complete checkpoint from disk, connect
recovery to the training worker, finish data admission/expansion and then qualify
the real full-model training path on an explicitly restarted Pod. P1 is ongoing.
# Durable storage progress — 2026-10-09

Implemented no-overwrite atomic checkpoint publication, serialized-byte ceilings,
fsync and same-descriptor hash-checked weights-only loading. A fresh subprocess
restored synthetic model/AdamW/RNG state and reproduced the next dropout update
exactly. Failure tests cover partial/tampered files, write exceptions, over-budget
serialization, symlinks and FIFOs. Fifteen focused tests pass; staged CLI checks
pass. The prior full suite ran 257 tests with 220 passed and 37 skipped.

Next: bind adapter/frozen-base identity, corpus, schedule/cursor and configuration
into the complete checkpoint contract, then wire worker save/resume. Actual
network-volume durability, GPU behavior and real data training remain unqualified.
The Pod was not restarted; the full P1 objective remains active.
# Bound adapter recovery — 2026-10-09

Implemented adapter-only checkpoint binding to base/corpus/config/schedule
identities, frozen-state fingerprints, module modes, exact data cursor, AdamW
and RNG state. CPU disk save/resume reproduces the remaining dropout schedule
exactly. Incompatible identities, tensor/state/count/mode changes are rejected
before parameter application. Eighteen focused tests pass; the repository suite
ran 261 tests, 220 passed and 41 skipped. Four staged CLI imports pass.

Next: connect these contracts into the actual training worker with finite run
budgets, checkpoint publication and resume. Qualify PEFT/full-model restore,
frozen-state scan cost, long-sequence memory and real data on GPU only after
local integration and admission work are ready. No Pod restart or real training.
# Budgeted training session — 2026-10-09

Integrated indexed corpus fetching, deterministic schedules, streamed optimizer
updates and bound checkpoint/resume into a reusable session loop. Update/time/
sequence/checkpoint budgets are explicit. The committed cursor advances only
after durable checkpoint publication. Five session tests cover exact resumed
execution, preserved prior checkpoints after disk failure, input rejection and
budget stops. Twenty-three focused tests pass; the repository suite ran 266 tests
with 220 passed and 46 skipped. Four staged CLI import checks pass.

Next: connect this loop to the full Gemma/PEFT worker, pinned runtime checks,
volume verification, durable reports and hard deadline supervision. Real data
remains quarantined; data expansion/admission and GPU qualification remain open.
No Pod restart and no real-data optimization occurred.
# Full corpus worker wiring — 2026-10-09

Connected CPU admission/config preflight, exact Gemma LoRA attachment, the
budgeted training loop, bound checkpoint resume, pinned runtime/volume/model
checks and deadline supervision in new corpus-worker entrypoints. Added a
proposed one-update qualification config. The real quarantined candidate is
correctly rejected before loading a model. No Pod restart or real training.

Reduced Gemma + PEFT update/restore passes, along with fourteen focused tests.
Repository suite: 271 tests, 224 passed, 47 skipped. Six staged CLI imports pass.
Full 31B GPU execution, supervisor end-to-end behavior with that worker,
long-sequence memory, throughput and resume remain unverified. Next: review and
test worker orchestration/error paths, complete corpus admission/expansion, and
prepare a concrete GPU qualification only after those prerequisites are ready.
# Supervisor evidence reconciliation — 2026-10-09

Added independent schedule/checkpoint/metric/budget reconciliation before the
supervisor accepts a session. Resume bindings are checked before worker launch;
worker execution identity must match the supervisor's own calculation. Actual
locally produced Torch checkpoints pass reconciliation, while altered reports,
payloads, paths, bytes and unsupported stop reasons fail. Thirteen focused tests
pass; full suite has 276 tests, 229 passed and 47 skipped. Six CLI imports pass.

GPU execution remains pending. Next priorities are full worker failure-path
coverage and data admission/expansion; CPU evidence is not a full-model readiness
or repair-performance claim. The Pod remains unused.
# Data expansion: Mailmerge controls — 2026-10-09

Downloaded and probed the pinned Mailmerge-135 environment. The base/reference
controls reproduce all 27 publisher transitions (26 versus 27 passing tests).
The selected teacher has 37 shell/editor calls before native adaptation. The
image exposes 906 reachable commits, so source isolation is mandatory before
replay. No training approval or real optimizer update is claimed.

**Mailmerge follow-up:** isolated exact-tree snapshot verified, 37-call native
replay completed, and its patch matched all 27 reference tests. Untruncated
history has 30,191 inputs / 7,415 targets; input plus the 8,192 output reserve
exceeds the 32,768 context budget by 5,615, so admission remains denied. Source
and selected dependency notices are retained. The runtime path aliases were
verified and capture containment corrected. Regression: 277 tests, 230 passed,
47 skipped. Next data work should evaluate the alternate trace or other tasks
without weakening the declared context criterion.

Next: bind the public solution commit, build/verify an exact-tree isolated source
snapshot, replay and grade the selected trace, then evaluate native context length
and rights/split admission. The Pod remains stopped; this work uses local CPU.


### Mailmerge alternate trace: independent replay and context rejection

Trace `8ac352d1-ec64-4e81-8999-778c27f6739c` was extracted from the pinned
SWE-Hero shard 011, reviewed, and replayed against the same verified offline
snapshot. All 37 charged shell/editor calls completed; the container was removed.
The submitted patch changes only the CSV reader encoding to `utf-8-sig`.
Independent grading matched all 27 reference outcomes, with zero disagreements.
This is teacher replay evidence, not learned Gemma performance.

The untruncated native history has 28,451 input tokens and 7,870 supervised
targets. With the unchanged 8,192-token output reserve, total demand is 36,643:
3,875 above the 32,768 limit. Assessment `swe-rebench-mailmerge-native-admission-002`
rejects training admission. Both reviewed Mailmerge traces fail this policy;
no reserve reduction or truncation was used. Rights and split admission remain
separate, unfinished requirements. No training corpus admission is implied.

This supersedes the earlier next-step note proposing the already completed
Mailmerge snapshot/replay. Next acquisition work should select a different
shorter candidate, preserving independent grading and the same context gate.
The Runpod Pod remains stopped; all this work ran locally.


### Complete source-token cost screening (local, no GPU)

Implemented `scripts/screen_source_token_cost.py` and
`scripts/merge_source_token_screens.py`. The screening binds census, cohort,
reserved repository index, intake receipts, source shards and exact model
tokenizer bytes before deserializing selected histories. All 14 shards now
cover exactly 2,621 image-present candidates (1,575 tasks, 902 repositories).
The merged result is `evidence/data/source-token-cost-full-001`.

Ranking uses the token count of canonical converted source-message JSON with
no truncation, padding or special tokens. This includes source observations
and reasoning. It is NOT native replay context, a bound on native length, a
quality score, or training admission. No token-fit threshold is inferred from
this proxy. Native replay, independent grading, actual token masking and
context admission remain mandatory. The sample remains cost-selected and
cannot estimate unbiased agent performance.

The eight shortest distinct repositories were bound to task records, their
Linux amd64 image metadata resolved (no layer download), and their issue and
environment records reviewed. Evidence: `source-token-shortlist-001`,
`source-token-images-002`, `source-token-task-review-001`. Shortness alone is
insufficient: dkey and mypy_extensions request version information/changes;
Narwhals requests documentation despite four published fail-to-pass tests,
which warrants inspecting evaluator relevance before use. Other candidates
include optional dataframe mutation, decorator return propagation, logger
optional arguments, debug-expression formatting and empty-file lint behavior.
These are potential bootstrap examples, not evidence of industrial capability.

Five selection tests cover reserved names and flags, linkage substitution,
duplicates and shard boundaries. A real incomplete cohort was rejected before
merge output. The first empty-shard run exposed an Arrow null-type issue;
explicit string typing fixed it, and all empty shards subsequently completed.
A source metadata change on first read stopped another attempt; the failure
was retained and a fresh run passed unchanged byte-identity guards. Final CPU
suite: 282 tests, 258 passed, 24 skipped in the isolated Torch environment.
No CUDA/full-model capability follows from those results.

Next: inspect task/evaluator relevance for a code-behavior candidate, then
qualify its clean-source controls and replay. Expand task diversity and
complexity alongside context feasibility; do not optimize training quality
solely for shortness. The Pod remains stopped; P1 and corpus admission remain
incomplete.


### Task/evaluator alignment requirement and corpus schema v2

The pinned task `narwhals-dev__narwhals-941` fails task-alignment review.
Its request asks for README media links, but the evaluator adds dataframe
column-selection assertions; all four published fail-to-pass cases exercise
that behavior. The reference patch contains both documentation and indexing
changes. Record `evidence/data/task-alignment-narwhals-001/review.json` binds
these inputs and rejects all three corresponding candidates in the screened
cohort. The oracle patches remain evaluator-only. This finding does not
establish a dataset-wide error rate.

Corpus schema v2 supersedes the earlier three-gate admission contract: it
requires `task_alignment`, `rights_and_attribution`, `split_isolation`, and
`runtime_qualification`. Alignment evidence must review the stated behavior,
reference change and evaluator relevance for every included task, including
incidental merge changes and missing test coverage. A green evaluator result
is insufficient. Generic receipt validation enforces content identity and
evidence presence; it does not automatically establish the semantic truth of
a review. No genuine passing alignment receipt has been created yet.

Schema v1 remains readable for inspection but cannot train, even if it carries
legacy passed receipts. New assembly emits v2. The real Nodebook candidate was
rebuilt as `artifacts/data/quarantine/training-corpus-002` and remains quarantine:
17,353 input tokens / 4,183 supervised targets, one example. Its manifest hash
is `f9b731e8af73f3e7597abc6c14dc4aeafaeee8e6cee0ffa94fe2de5b5d87fc5d`.
The schema change alters corpus content identity; schedules and admission
receipts must be regenerated and reviewed, never relabeled from v1.

Actual v1 and v2 candidate training denials are retained in
`evidence/p1/task-alignment-denial-001`. The current worker bundle passed all
six isolated CLI imports in `evidence/p1/task-alignment-source-001`. Final
CPU suite: 285 tests, 261 passed, 24 skipped. Tests include forged alignment
bindings, omitted alignment gates and an otherwise admitted legacy corpus.
These checks establish local enforcement, not semantic review accuracy or
full-model/CUDA qualification. P1 remains active; no GPU was used.

Next: select a substantive code-behavior candidate whose problem statement,
reference patch and tests agree; perform paired controls and native replay.
Continue rights, split and task review before any real admission or training.


### Shortlist alignment review and Datetransform base inspection

Reviewed the seven remaining shortlisted task/reference/test bundles; the
inputs and decisions are in `source-token-alignment-inputs-001` and
`task-alignment-shortlist-001`. Mypy_extensions task 57 is rejected for the
same class of issue/evaluator mismatch: its request is a version update, but
its added evaluator checks NoReturn deprecation. Three cohort traces are
affected. Dkey task 18 is held: its reference queries `VersionInfo('mgen')`
while exposing dkey version information, and its tests only assert attribute
existence. This is insufficient evidence of correct version provenance.

Pydbg, Ignite, flake8-fancy-header, easy-ptvsd and Datetransform have provisional
static alignment, with narrow coverage limits explicitly recorded. None has
received training approval. The findings are from a cost-selected eight-task
shortlist; they cannot estimate a dataset-wide error rate.

Datetransform task 2 was selected for further qualification: optional mutation
is a concrete behavioral contract, with tests for the default copy behavior
and explicit inplace=True. Its pinned image was pulled locally and probed
without running task tests. The image checkout is
`51571c772ad0939dd35f1e9788fbbabfd8117b88`, not the expected
`33b75b1948cad92aa4edf91850887f27562b0632`. Read-only Git inspection confirms
the expected commit exists and has tree
`696e971b020003634b90ffa249380b5bead8fc50`. The only tracked differences
between base and image HEAD are files `=1.0.0` and `=1.16.0`; the image HEAD
commit is titled Environment setup changes. The original full Git history
also contains the solution commits, so it is unsuitable as an agent workspace.

Evidence: `datetransform-probe-001`, `datetransform-base-audit-001`. Both owned
probe containers were removed. No repair score or environment compatibility
claim was produced. Next: derive an explicitly bound baseline at the requested
commit, verify the exact tree, then run base/reference controls and sanitize
solution history before replay. Preserve the original image and all identity
checks; do not reinterpret the setup commit as the official base.

This cycle changed data-quality evidence and candidate selection, not training
code. The Pod remains stopped; P1 is incomplete and no data was admitted.


### Datetransform exact-base normalization and paired controls

Implemented `zenithsync/source_base.py` and
`scripts/prepare_rebench_baseline.py` for disposable evaluator containers whose
image HEAD is an environment setup commit. The build requires a successful
probe bound to the immutable parent image, the observed initial HEAD and clean
tracked source. It performs a non-forced detached checkout, disables checkout
hooks, verifies the target tree, and hashes every tracked file against Git
blobs. Untracked files and solution history deliberately remain; the result
is explicitly not an agent-approved workspace. The parent image is unchanged.

Datetransform's derived baseline is
`sha256:e5c7fa51e8347815c94030d656efecb882773209da57a6c7fd3c708c7fb651cd`.
Readback preserves nine tracked files at commit
`33b75b1948cad92aa4edf91850887f27562b0632`, tree
`696e971b020003634b90ffa249380b5bead8fc50`. Evidence is in
`datetransform-baseline-001`, `datetransform-baseline-readback-001`,
`datetransform-baseline-input-001`, and `datetransform-controls-001`.

Paired evaluator controls import `datetransform.transform` from the checkout
and match all three published transitions by full test identity: base passes
one and fails two, reference passes all three. Test execution did not modify
the tracked diff, and owned control/readback containers were removed. This
qualifies the narrow three-test evaluator behavior, not broad correctness or
agent performance. No teacher replay or trained model ran in this cycle.

New tests cover wrong initial HEAD, tracked edits, checkout-hook suppression,
exact base restoration and preservation of unrelated untracked files. Final
CPU suite: 288 tests, 264 passed, 24 skipped. Runtime code for the normalizer
also executed successfully inside the real Linux baseline build.

Next: bind the solution commit, sanitize reachable history and known oracle
files while preserving the exact tree, independently verify the resulting
workspace, repeat paired controls to check parity, then replay and grade a
selected trajectory. Rights, split and semantic admission remain separate.
No GPU was used; keep the Pod stopped. P1 remains incomplete.


### Datetransform sanitized replay and two-example corpus integration

Bound PR 2 solution head `82085ef8e7f17cce30732a179cf5cf280eaa1754` and merge
`7331185d854f14734a33ee00a84367d33c2aada0` to the captured GitHub response.
Snapshot builds now accept an explicit successful probe of the same pinned
image to normalize a setup HEAD before sanitization. The original strict
base requirement remains the default. Independent verification also checks
that the former setup HEAD is inaccessible.

Datetransform snapshot
`sha256:5f0dad187211379bfa4e913571460b9ab47eb0264263b0d0472a35dced139d0c`
preserves the nine tracked base files and has one parentless commit. Base,
solution, merge and setup commits are inaccessible; declared oracle paths
are absent. This audits the mounted filesystem, not inherited Docker layers.
Paired controls on the snapshot match the qualified baseline exactly: one
base pass and two base failures, three reference passes.

Trace `2bd25bdd-8342-4fb7-99a8-6ef15a2ea5ff` was source-reviewed and replayed
with fresh native observations, 27 charged calls, no executed teacher thoughts
and successful disposable-container cleanup. Its submitted source-only patch
adds `inplace=False` and copies the dataframe when false. Independent grading
matched all three evaluator outcomes. These tests cover a narrow one-row date
example, not general dataframe aliasing correctness or learned model behavior.

The untruncated history contains 14,126 input tokens / 4,574 supervised targets.
Adding the unchanged 8,192 output reserve gives 22,318, leaving 10,450 tokens
under 32,768. `datetransform-native-admission-001` passes mechanical checks
without approving training. Evidence uses the `datetransform-*` directories
for source, snapshot, controls, replay, grade, history, tokens and admission.

Assembled schema-v2 `artifacts/data/quarantine/training-corpus-003`: two real
examples across two tasks/repositories, 31,479 input tokens and 8,757 supervised
targets. Manifest SHA-256:
`5c0fb2f37acf0d2b425f983c5db38316b15f97482231b4641371b4d8baf921ef`.
A seed-7401, one-epoch dry schedule with an 8,192-target per-update ceiling
produces two whole-example updates, zero target overshoot and no repetition.
The real corpus is still rejected for training. Rights, split isolation, task
alignment receipts and runtime admission remain unresolved. This tiny corpus
is pipeline qualification material, not sufficient campaign data.

Final CPU regression suite: 288 tests, 264 passed, 24 skipped; snapshot building,
verification, controls and replay also ran locally in Linux containers. No
GPU was used. Next: rights and complete admission review for these candidates,
continued diverse corpus expansion, then full-model runtime qualification when
local prerequisites justify restarting the Pod. P1 remains incomplete.


### Rights capture compatibility and restored corpus validation

Datetransform source capture preserves all nine tracked files and MIT license
(Copyright 2020 Brandon Schabell). The Python 3.7 metadata path now uses the
installed backport and compatible canonical path-containment checks. Selected
notices were captured for pandas 1.3.5, NumPy 1.21.6, python-dateutil
2.9.0.post0, pytz 2025.2 and six 1.17.0. Installed pytest 7.1.2 has no
discoverable notice. Default capture still rejects this absence; an explicit
inventory option preserves the missing-notice flag without approving rights.
Both initial failures and a fresh default-denial check are retained.

The matching pytest 7.1.2 upstream source archive was downloaded from PyPI,
verified against its published SHA-256, and its LICENSE preserved separately.
This supplements attribution evidence but does not prove installed Conda build
identity or complete all dependency/observation rights review.

The 83-file Datetransform replay archive was independently restored from R2.
The restored two-example corpus validates at the exact original manifest hash;
both the regenerated schedule and update stream match the original bytes.
Counts remain 31,479 input / 8,757 supervised tokens and two dry updates.
Training admission remains false. Evidence: `datetransform-replay-restore-001`,
`training-corpus-restored-inspect-001`, `training-corpus-restored-schedule-001`.

Current readiness is consolidated in document 39 and linked first from README.
The latest CPU suite remains 288 tests, 264 passed, 24 skipped. No GPU was used.
Next: complete attribution and split/admission evidence while expanding corpus
coverage; do not treat two quarantined examples as sufficient campaign data.


### Current repository identity and issue-duplicate audit

Live GitHub metadata resolves Nodebook and Datetransform plus the four reserved
repositories. No canonical-ID or declared fork-network-root overlap was found
(`current-corpus-lineage-001`). Reserved task bodies were not read.

New `audit_issue_duplicates.py` verifies the pinned candidate cohort and task
shards, validates source metadata before reading candidate issue text, and
records exact UTF-8 hashes separately from whitespace-normalized heuristics.
It covered all 1,575 candidate tasks and found two exact duplicate pairs:
Mobly 164/165 and Hidrokit 121/122. Whitespace screening found the same pairs.
Neither pair includes the current two assembled tasks. Source text equality
is a grouping/review signal, not proof of task equivalence; case and Unicode
forms are deliberately not conflated.

`current-corpus-split-review-001` binds the actual corpus, identity audit and
fingerprint evidence to a validated draft grouping using fork-network IDs and
exact issue hashes. No training admission or frozen split was created. This
review does not exclude detached copies, semantic/patch duplication, vendored
source, unknown hidden evaluation data or model-pretraining exposure. It cannot
be interpreted as a dataset-wide independence guarantee.

Four new tests cover exact-versus-whitespace equality, case/Unicode separation,
order independence and duplicate/empty input rejection. The final CPU suite
ran 292 tests: 268 passed, 24 skipped. Next: complete attribution and task
review while expanding the qualified corpus, and resolve the final split before
training. No GPU was used; P1 remains incomplete.


### Native observation audit and direct-source attribution

Added reusable replay observation inventory with exact text/result identities,
root and wrapped command exit codes, explicit truncation flags, and unknown
status when a flag is absent. It validates event ordering and charged-call
counts against the completed replay receipt. It does not equate successful
tool execution or printed test claims with correctness, and does not remove
failed observations from the training history.

Datetransform: 27 charged calls plus submission; 27 ok results and one error
(the empty no-match grep result, exit 1). No explicit truncation is reported;
20 responses have no truncation flag, including response types without file
content. Nodebook: 35 charged calls plus submission; all report ok, but one
source read is explicitly truncated and 31 responses have no truncation flag.
Do not conflate full token serialization with full underlying observations.
Evidence: `datetransform-observation-audit-001`, `nodebook-observation-audit-001`.

All five Datetransform direct read_file observations match preserved base
source or sequential unique edits under the native line rendering. Three
unique edits were checked, including two in a temporary diagnostic script.
The source attribution record and span hashes are in
`datetransform-file-rights-001`. This closes direct-read byte correspondence
for that trace, not arbitrary shell-output rights or semantic equivalence
to the original teacher's observations. Shell diagnostics and conditioning
fidelity remain explicit review obligations. No rights or training admission
was granted.

Six new tests cover missing versus explicit truncation flags, wrapped errors,
ambiguous/boolean exit codes, event ordering and changed observation hashes.
Final CPU suite: 298 tests, 274 passed, 24 skipped. The two-example corpus,
labels and schedules are unchanged; no GPU was used. Next: complete remaining
attribution and admission review, expand corpus coverage, and qualify GPU
execution only after the exact candidate bundle is ready.


### Task alignment coverage cycle — 2026-10-09

Implemented exact task/repository review coverage in corpus admission, with
negative tests for omitted, duplicate, foreign and unresolved reviews. Full CPU
regression: 302 tests, 278 passed, 24 skipped. Worker source bundle and isolated
CLI checks refreshed. Real corpus remains two quarantined examples with 8,757
supervised tokens; no real approval or GPU training occurred. Next: complete
semantic and rights reviews and expand the qualified corpus before GPU use.


### Semantic probe and corpus exclusion cycle — 2026-10-09

Executed base/candidate probes in exact local snapshot containers, no GPU.
Nodebook passes its 19 publisher cases but misses annotation dependencies and
leaks parameter scope in added counterexamples: exclude its trajectory.
Datetransform passes 18 added copy/inplace/time/row-count cases versus 0 on base.
Selection 003 and corpus 004 now contain only Datetransform: 14,126 input and
4,574 supervised tokens, quarantine only. No teacher trajectory was rewritten
to conceal a failure. Next: expand qualification, finish rights/admission and
regenerate the schedule for the final approved corpus. Old schedules are stale.


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


#### Icontract 115 qualification update

The teacher is excluded pending an explicitly attributed correction: 25/25
publisher passes conceal nine contract-bypass counterexamples among 15 valid
variadic-call checks. A correction must preserve contract execution and pass
publisher controls, argument-binding checks, native replay and content-bound
admission assessment before corpus consideration. Runtime evidence is published
and hash-verified in R2 (icontract115-runtime-publish-001). Corpus028 and the
three planned 50M processed-target-token campaigns are unchanged; adequate data
supply remains unresolved. Keep Runpod stopped during this local qualification.


Icontract correction follow-up: bounded mapping now passes the 25 publisher,
15 variadic and 152 mapping/call-shape tests. Native integration remains held:
40 source calls plus an appended correction exceed current 40-call policy.
Do not trim history or relax admission implicitly. Continue qualifying other
sources while considering an explicitly authored fresh episode separately.


Importlab 23 follow-up: runtime qualification found a filename-boundary
regression despite 30/30 publisher passes. Prioritize an attributed correction
that distinguishes path separators from literal dots, then native replay,
context-budget audit and grading. Its 37 source calls leave up to three calls
under existing policy, subject to actual replay validation. Corpus028 remains
unchanged; no GPU restart is needed for this work.


Importlab corrected replay now passes 30 graded cases and mechanical checks
at 38 calls, with 23,697 input / 6,640 supervised tokens and 879 reserve margin.
Next integrate its explicitly attributed candidate, then repeat corpus hash,
restore, lineage, schedule and denial checks. Training remains unapproved.
Use byte-verified temporary runtime staging for Desktop hydration failures;
do not relax identity guards. Prefer existing images and verified duplicate
cache removal while local storage is constrained.


Corpus029 is the current integrated quarantine: 25 tasks / 24 declared groups,
148,523 supervised tokens. R2 publish/restore, identical schedules, lineage020
and explicit training denial verified. Expand reviewed source diversity and
resolve attribution/admission gates before a GPU campaign. Three 50M processed
target campaigns remain a plan, not supplied data. Keep Runpod stopped.


Marshmallow-dataframe19: complete runtime qualification only after local storage
headroom is established. Static review confirms a typed-index required-policy
difference and prepares 36 unexecuted acceptance cases. Do not count static
checks as publisher passes. Prefer auditing reusable/retired project caches
before another image pull; retain model files, unfinished work and recovery
sources. This is a local-capacity issue, not a reason to restart paid Runpod.


Marshmallow-dataframe19 runtime hold supersedes the capacity defer: scoped
project-only build-cache cleanup allowed the pinned image to run locally.
Teacher fails one of18 publisher tests and six of36 finite typed-index cases.
An attributed correction must preserve dtype-dependent requiredness, then pass
runtime, native replay, context and admission checks. Corpus029 unchanged;
Runpod remains stopped. Continue scoped cache management with before/after IDs.


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


### Current content-quality gate update — October 11, 2026

Before corpus033 promotion, resolve the Signac622/Lenskit312 original-history
claim holds and Lmfit487 wording review recorded in
`evidence/data/corpus033-claim-review-001/report.json`. Complete remaining contextual
review, including nested tool arguments and claims outside lexical patterns.
Keep true recorded results distinct from unsupported generalization and incorrect
hard-coded narration. Any corrected trajectory needs explicit derivative provenance,
fresh replay and renewed token/runtime qualification. Preserve original evidence.

Second review batch: selected claims in 10 distinct histories now have contextual review. All 29 histories have zero nested argument string leaves under the recursive check. Remaining claim contexts, full semantic review and explicit corrections remain required; no training approval follows from these counts. See `evidence/data/corpus033-claim-review-002/report.json`.

Third review batch: 16 distinct histories have selected-claim contextual review; seven flagged histories remain. Preserve Importlab expectation changes for independent contract checking. Numkit integer-index algebra is distinct from finite floating-point equality evidence; see `evidence/data/corpus033-claim-review-003/division-scope.json`. No training admission follows from this review.


### Current correction queue — October 11, 2026

The selected lexical-context pass is complete: 44 matches, 23 histories, 145 exact
message bindings. This supersedes earlier remaining-match counts, not broader
semantic/admission requirements. Use
`evidence/data/corpus033-claim-review-004/correction-queue.json` for next actions.
Prioritize explicit, freshly replayed claim corrections for Signac622, Lenskit312
and CloudEvents172; independently resolve Lmfit487 wording and Importlab23 changed
expectations. Keep six diagnostic-quality follow-ups distinct from observed false
results. No-match histories still require semantic review. Preserve all original
records and requalify each derivative; do not promote the unchanged corpus.

Action-amendment implementation: strict pure builder and Lenskit prepared derivative now exist; 431 local tests pass with 17 skips. Next wire explicit amendments into native replay and reconstructed-history provenance, reconcile completion action identities, then freshly replay/grade/token-audit the derivative. Do not relabel old observations or count preparation as resolving the hold.

Amendment integration update: native replay/history plumbing is implemented and locally tested (435 tests, 17 skips). Lenskit fresh amended replay, history projection and token audit completed; next independently grade the derivative, check mechanical admission compatibility and finish content review before replacing any quarantined corpus example. Preserve its timeout and the original evidence; no training admission yet.

Amended Lenskit qualification update: exact patch independently matches all 20
publisher cases; fresh base/reference transitions and mechanical admission pass.
Selected corrected claims reviewed; full-history review, rights, frozen splits
and runtime admission remain open. Snapshot controls now accept task-only
resolution when a verified snapshot supplies the image. Suite: 453 tests,
436 passed, 17 skipped. Next finish full content review before replacing the
quarantined original; no training approval and no Runpod restart.

Lenskit full-history update: first amended history held for truncated pre-edit
source observation. New source-observed derivative passes fresh replay,20-case
grading, token and mechanical checks; all56 messages reviewed with exact bindings.
Next replace the old Lenskit member in quarantine using observed-history-001 and
observed-tokens-001, then reassemble, restore-test and schedule-check the corpus.
Retain original holds and no-k contract limitation. No training admission.

Corpus 034 update: the reviewed Lenskit replacement is integrated; the other 28
records are unchanged. Assembly, R2 publish/restore, independent token counts,
byte-identical restored schedules and training-denial checks pass. The 29
quarantined examples and 165,734 supervised tokens remain insufficient for the
three 50M-token campaigns. Next resolve held Signac/CloudEvents content and
scope/contract reviews, then expand diverse supply. Keep Runpod stopped for these
local data tasks.

Signac update: three diagnostic amendments prepared and freshly replayed; token
audit passes. Real snapshot positive/negative/mutation checks validate finite
diagnostic failure propagation. Next independently grade the exact patch on the
pymongo-qualified image and finish full history review before corpus replacement.
Keep repeated verifier executions distinct from unique coverage. No Runpod use.

Signac grading update: dependency-image isolation verified; explicit child Python
PATH repaired the generic evaluator environment. Fresh controls and exact patch
match all 36 publisher expectations; mechanical admission passes. Full suite:
438 passed, 17 skipped. Next finish history review before quarantined replacement.
Do not count the failed environment-control attempt as model performance.

Signac full-review update: attribution-corrected version002 freshly passes replay,
36-case grading, tokens and mechanical checks. All 78 messages reviewed with
finite scope and preserved failures. Next replace the older Signac example inside
quarantine, restore-test and recount the new corpus; then continue CloudEvents
and remaining scope reviews. No training admission or Runpod use.


October 11 update: Signac corrected full-history review is archived and independently
restore-verified in R2 (29 files, 624,776 bytes). Next remains its exact replacement
in corpus034 with fresh accounting, schedule and restore checks; training gates
remain closed. No Runpod session is required for this step.


October 11 corpus035 integration: reviewed Signac replacement completed; 29 examples,
165,360 supervised tokens, 59 files restored from R2 with exact schedule equality
and training denial. Next is CloudEvents content correction and remaining admission
work, alongside diverse-data expansion. No Runpod session is needed yet.


CloudEvents correction update: six amendments freshly replayed and token-audited;
next independent grading and full content review. Retain its 2,412-token reserve
shortfall as an unresolved policy constraint. Corpus035 remains unchanged.


CloudEvents independent qualification update: 26/26 candidate cases match the
reference, but mechanical admission rejects its context reserve. Next is an
explicit concise diagnostic derivative preserving checks, followed by fresh
replay and review. Corpus035 remains unchanged; no GPU session required.


CloudEvents concise derivative now fits context with 1,156 reserve margin, passes
26/26 independent cases and mechanical checks. Next: full content review before
quarantined replacement; corpus035 unchanged and training unapproved.


Corpus036 update: full CloudEvents content review and exact quarantined replacement
complete. R2 restore, token accounting, deterministic schedule and training denial
verified. 29 examples / 162,807 supervised tokens remains insufficient diversity.
Next: remaining scope/diagnostic reviews, rights/splits and data expansion; no GPU yet.


Importlab contract checkpoint: two changed root expectations independently supported
by four-role execution. Next remains full history/wording review and Lmfit scope
review; this narrow result does not admit data or change corpus036.


Importlab follow-up: corrected graph unittest exit propagation and freshly replayed;
24,306 input / 6,664 supervised tokens fits reserve by270. Next fresh grading and
full content review; preserve missing-python3.6 failure and reference-informed
completion attribution. Corpus036 remains unchanged.


Importlab exit-corrected replay now passes 30/30 grading cases and mechanical
admission checks. Next: full 80-message content review before quarantined corpus
replacement. Reference-informed attribution and all training gates remain.


Importlab full-content checkpoint: all 80 messages are reviewed and hash-bound,
with explicit finite-check, failure and reference-informed provenance limits.
Review archive is R2 publish/restore verified. Next replace only this record in a
new quarantined corpus, independently recount targets and verify restored schedule
equality and training denial. Corpus036 and all training gates remain unchanged.


Corpus037 integration checkpoint: reviewed Importlab derivative replaced exactly
one record; 28 unchanged. R2 restore and independent token recount pass, original
and restored 27-update schedules match, and quarantine training denial holds.
Continue remaining content/rights/split qualification and data expansion before
GPU training. Current data: 29 examples and 162,831 supervised tokens; not sufficient
for the projected three 50M-token campaigns.


Lmfit checkpoint: three attributed diagnostic amendments pass finite local checks
and four synthetic failure-propagation checks. Preserve the failed first validator.
Next require fresh replay, token audit, independent grading and full content review
before a one-record corpus replacement. Corpus037 remains quarantined and unchanged.


Lmfit replay checkpoint: fresh amended replay and independent 13-case grading pass;
40 charged calls and 20,804 input tokens fit policy, with 5,221 supervised targets.
Mechanical checks pass. Next review all 84 messages before any quarantined corpus
replacement; rights, frozen splits and training runtime remain separate gates.


Lmfit second-derivative checkpoint: full review held the first derivative for two
additional failure-reporting defects. Six attributed amendments now replay within
40 calls; independent candidate grading passes 13/13 and token audit fits policy.
Next review the new observations before corpus replacement. Corpus037 is unchanged.


Corpus038 checkpoint: Lmfit full review closed through exact unchanged-message
bindings and all changed-message inspection. One replacement, 28 unchanged; R2
restore, target recount, schedule equality and training denial pass. Current corpus
has 29 examples / 162,586 supervised tokens. Continue six diagnostic follow-ups
and remaining semantic/rights/split/data-expansion work before training admission.


Datetransform checkpoint: attributed finite diagnostic replacement passes on the
existing repair, fails on base and detects four injected faults. Twelve finite
configurations are not additional real training tasks. Next complete history-scope
review and fresh replay/token/grading before replacement; corpus038 is unchanged.


Datetransform replay checkpoint: 27 calls, exact unchanged patch, 3/3 independent
candidate cases and mechanical checks pass. History is 14,550 input / 4,292 targets.
Next close amended-history content review before quarantine replacement; default
mutation changes are intentional, so column compatibility is not global compatibility.


Corpus039 checkpoint: Datetransform full scoped review and exact one-record
replacement complete. R2 restore, independent target recount, schedule equality
and training denial pass. Continue five diagnostic follow-ups and remaining
semantic/rights/split/data-expansion work; 29 examples are not campaign-scale data.

## October 11 checkpoint — Apispec exit-status qualification

Corrected the diagnostic aggregate exit status, then rebound its cleanup hash to
the amended bytes. Preserved failed replay 001 and documented pre-replay hydration
rejection 002; fresh replay 003 completes. No integrity guard was weakened.
Paired controls reproduce 115/117 base and 117/117 reference passes. Independent
candidate grading matches all 117 identities. Untruncated audit: 78 messages,
37 calls, 23,126 input / 4,250 supervised tokens, 1,450 reserve margin.
Mechanical admission passes; no learned model was evaluated. Corpus039 unchanged.
Next: inspect the complete Apispec history before quarantine replacement, continue
the remaining diagnostic reviews, then rights/split and diverse-data expansion.
Keep Runpod stopped. Full P1 and training readiness are unproven.

R2 preservation verified: 70 files / 1,062,451 bytes uploaded and independently
restored. Receipts: apispec950-exit-publish-001 and restore-001.

## October 11 checkpoint — Apispec reviewed replacement, corpus040

Full 78-message review identified stale Actual text, unconditional final success
and four pytest pipelines. Seven explicit action amendments now compute observed
values, propagate aggregate status and run pytest directly. Fresh replay preserves
four failed tool results and the same final source patch. Three finite final
comparisons pass; base and four injected faults fail as expected. Publisher grading
matches 117/117 cases. The 563-pass baseline precedes source edits and must not be
reported as a final full-suite pass. Review also corrects the issue's OpenAPI
rationale: https://spec.openapis.org/oas/v3.0.2.html#schema-object specifies omitted
additionalProperties defaults to true. This is an explicit-output repair.

Fresh audit: 23,621 input / 3,885 supervised tokens, 955 reserve margin, 78 messages
and 37 calls. Qualification/review archive: 46 files / 760,877 bytes uploaded and
independently restored. Corpus040 replaces exactly one record; 28 unchanged.
Corpus: 582,029 input / 161,945 supervised targets, 59 files / 6,441,443 bytes,
uploaded and independently restored. Independent recount agrees; original/restored
27-update schedules match byte-for-byte with zero overshoot. Training rejects
quarantine; Emcee295 remains the sole context reserve exception.

Preserved failures: source hydration timed out before replay; complete source read
verified the pinned hash before fresh replay. Assembly001 selected an existing
output path and was rejected; assembly002 uses a fresh output and verifies the old
corpus unchanged. No guard was weakened. No production-code change or Runpod use.
Next: Pennylane5716, Statsmodels8339, Boltons205 and Numba6653 diagnostic reviews;
broader rights, split/duplicate review; diverse data expansion and runtime testing.
P1 remains incomplete and no learned-model improvement has been demonstrated.

Integration/accounting archive: 15 files / 76,454 bytes published and independently
restore-verified. Receipts: corpus040-integration-publish-001 and restore-001.

## October 11 checkpoint — Pennylane5716 finite diagnostics

Reviewed the three weak diagnostic scripts. Replacements use fixed random input,
propagate aggregate failure and check names, wires, list lengths and all 36
parameters for an eight-operation, three-slice decomposition fixture. Three
broadcast shapes match 117 separate executions at rtol=atol=1e-10; unbatched checks
are smoke checks only. Six injected faults are rejected. Fourteen subprocess
observations include base failures, the original false-zero result and corrected
candidate results. The multi-batch limitation remains a failed 6/7 observation.
First container launch used an absent default Python path; second uses the declared
/usr/local/bin/python and completes with cleanup. A preservation assertion initially
miscounted observations as 13; an explicit set of 14 named executions replaced it
before archival. No source guard or diagnostic result was weakened.

Corpus040 unchanged. Next: bind these amendments through the mini-source replay
path, run a fresh replay/grading/token audit and full semantic review, then consider
quarantine replacement. Remaining diagnostic, rights/split, data-expansion and
runtime gates stay open. No production-code changes, training or Runpod use.

Diagnostic evidence archive: 20 files / 37,854 bytes uploaded to R2 and independently
restore-verified. Receipts: pennylane5716-diagnostic-publish-001 and restore-001.

## October 11 checkpoint — mini-source amendment integration

Added hash-bound shell-command amendment support to mini-source replay, history
reconstruction and admission. Reuses the existing amendment validator, preserves
original trace bytes and indices, rejects terminal modification, and records
assistant authorship per changed event. Profile/replay/history provenance must
agree. New rejection tests cover hashes, altered calls, authorship, source index,
terminal changes and missing/orphaned claims; 27 targeted tests passed.

Pennylane source ordinals 11,19,28 are amended. Fresh snapshot verification required
stable copied build inputs because the historical receipt bound old verifier code
and cloud hydration changed metadata. No guard was weakened. Fresh replay completes
with 74 messages, 35 charged calls and the same patch. Full publisher plus supplemental
grading matches 44 cases; paired base/reference counts are 32/44. Untruncated audit:
18,874 input / 5,791 supervised, 5,702 reserve margin. Mechanical admission passes;
full semantic review and quarantine integration remain pending. Corpus040 unchanged.

The first broad regression ran 459 tests but failed (1 failure, 10 errors, 17 skips):
source hydration triggered integrity guards and three CLI subprocesses timed out.
That failed log is retained; stable local source-copy regression is required before
claiming a full pass. No training, Runpod use or learned-model improvement claim.

Implementation/replay qualification archive: 63 files / 779,663 bytes uploaded and
independently restore-verified in R2 (pennylane5716-amended transfer receipts).

Stable-copy regression completed: 459 tests, 442 passed, 17 skipped in 17.537s.
An intermediate local-copy run lacked two fixture paths; both were restored. All
three logs and tested-source hashes are preserved in mini-amendment-regression-003.
The seven changed implementation/test files match the tested copy byte-for-byte.

Regression archive independently restored from R2: four files / 70,868 bytes;
receipts mini-amendment-regression-publish-003 and restore-003.


## Corpus041: completed Pennylane semantic review and R2 integration — October 11, 2026

Reviewed every reconstructed message, including full cleanup code. The issue proposes
the layer-axis fix. The exact rank argument covers (L,W,3) and (B,L,W,3), while the
unsupported multi-batch diagnostic remains a failed tool result. Decomposition
parameter checks and 117 separate-execution comparisons are finite consistency
checks; repeated tests are not additional independent tasks. Original reproduction
exit zero is observational only. Review permits quarantine replacement, not training.

Exactly one corpus040 example was replaced; the other 28 records are unchanged.
Corpus041 has 579,746 input / 160,597 shifted supervised tokens, independently
recounted after R2 restoration. All 59 files / 6,415,283 bytes match. The local and
restored schedules match byte-for-byte: 27 updates, seed 7401, one epoch, zero target
overshoot. Quarantine training rejection is verified. Only Emcee295 exceeds the
input-plus-8192-output-reserve policy. All admission gates remain unset.

Evidence: training-corpus-selection-040, training-corpus-assembly-041,
corpus041-integration-check-001, training-corpus-schedule-047,
training-corpus-restored-schedule-039 and corpus041 transfer receipts.
No production code changes in this integration; prior 459-test regression remains
scoped to its recorded source hashes. No Runpod use or learned-performance claim.
Next: three remaining diagnostic follow-ups, broader semantic and rights/split review,
diverse-data expansion and full training-runtime qualification. P1 remains incomplete.

Full semantic review and integration archive independently restored from R2:
19 files / 95,647 bytes; corpus041-integration-publish-001 and restore-001.


## Boltons205 diagnostic correction — October 11, 2026

The pinned real package reproduces false success on the base: the original final
script prints false comparisons, prints an unconditional all-pass banner, and exits
zero. Seven explicit assistant amendments add missing comparisons and correct
custom-key ordering commentary. All seven corrected scripts pass on the existing
candidate patch. Each of 19 assertions, forced false separately, produces a nonzero
exit with AssertionError and no final success banner. This tests reachability and
failure propagation; it is not independent numerical-oracle or general-correctness
proof. Earlier base reproduction remains observational. Existing compatibility
completion is preserved and rebound to the derived action identity.

Evidence: boltons205-diagnostic-001 and diagnostic-validation-002. First validation
used an alias created only by native replay and failed before checks; the second
uses the snapshot's /testbed root. Both removed their containers. The 34-file,
99,114-byte diagnostic archive is uploaded and independently restored from R2.
Fresh native replay attempt 001 rejected shard metadata changing during cloud
hydration; the guard remains intact. Fresh replay/grading/review remain pending.
Corpus041 remains unchanged. No Runpod use; P1 and training admission are incomplete.

Fresh native replay 002 completed with 31 charged calls and verified container
cleanup; the 948-byte final patch is unchanged. Evidence:
boltons205-amended-native-002. History projection, token audit, independent grading
and full semantic review remain pending before quarantine replacement.

Native replay archive independently restored from R2: seven files / 148,495 bytes;
boltons205-amended-native-publish-001 and restore-001.


## Corpus042: Boltons semantic qualification and integration — October 11, 2026

Full 66-message review completed, including both assistant completion commands.
The bounded interpretation distinguishes printed observations, repeated original
repository tests, publisher tests and exact-Fraction permutation checks. The default
queue aliases the sorted backend. Numeric-string compatibility is restored by the
explicit assistant completion, not by the intermediate teacher patch. No universal
numeric or compatibility claim. Fresh publisher controls: base 0/2, reference 2/2,
candidate 2/2. Token audit: 20,215 input / 6,926 supervised; reserve margin 4,361.
Mechanical admission passes. The first assessment used an obsolete local runtime
without amendment-aware reconstruction and rejected the history; the current
repository-equivalent admission module passes with all guards preserved.

Exactly one example replaced; 28 records unchanged from corpus041. Corpus042 has
580,237 input / 161,157 shifted supervised tokens, independently recounted after R2
restore. All 59 files / 6,421,400 bytes verified. Local and restored schedules are
byte-identical: 27 updates, seed 7401, one epoch and zero overshoot. Restored training
is denied, all admission gates remain unset, and only Emcee295 exceeds the output
reserve policy. No production implementation change or Runpod use in this cycle.

Evidence: boltons205-full-history-review-001, amended-grade-001,
amended-admission-002, corpus042-integration-check-001 and corpus042 transfer
receipts. Remaining work includes Statsmodels8339 and Numba6653 diagnostics,
broader semantic/rights/split review, diverse data expansion and full runtime
qualification. P1 remains incomplete; no learned performance improvement measured.

Qualification and integration archive independently restored from R2: 67 files /
488,959 bytes; corpus042-integration-publish-001 and restore-001.


## Statsmodels8339 finite diagnostic correction — October 11, 2026

Four explicitly attributed action amendments replace unsupported white-noise lag
and p-value expectations, unchecked output shapes and swallowed verification errors.
The strengthened numerical diagnostic computes centered lagged dot products and
first-maximum penalized lag selection independently of statsmodels acf/selection.
It preserves this snapshot's inclusion of lag zero in the threshold calculation;
that is implementation matching, not endorsement of statistical optimality. P-value
references share SciPy chi-square survival functions; no independent tail-probability
or post-selection calibration claim. Fixtures use finite nonconstant data, model_df=0.

Pinned offline validation passes twelve direct-sum/fixed-lag cases across six fixed
samples and two statistic modes. All five injected numerical/structure faults and
fifteen forced contract assertions fail as required. The original comprehensive
script's zero exit despite reported failure is reproduced on base. All four amended
scripts pass on the existing candidate patch. Explicit completion preserves the
failed p>0.05 null-sample counterexample and explains its meaning. Scratch hashes
are rebound to amended bytes; fresh native replay remains required.

Evidence: statsmodels8339-diagnostic-001 and diagnostic-validation-001. Native
attempt 001 was rejected during cloud hydration because shard metadata changed;
no identity guard was weakened. Corpus042 is unchanged. P1 remains incomplete;
no Runpod or trained-model evaluation in this cycle.

Diagnostic archive independently restored from R2: 25 files / 81,428 bytes;
statsmodels8339-diagnostic-publish-001 and restore-001.

Fresh native replay 002 completed: 33 charged calls, 34 exchanges, 70 messages,
130 repository diagnostic tests passed, unchanged 603-byte source patch and
verified cleanup. The expected null-sample p>0.05 assertion fails with observed
p=0.03719492177943689; its failure and subsequent explanation remain in history.
Token audit: 14,841 input / 4,181 supervised, 9,735 reserve margin. No truncation.
The eight-file / 106,018-byte native replay archive is independently restored from
R2; reconstructed history/tokens are saved locally pending the next qualification
archive. Independent grading, admission and full semantic review remain pending.


## Statsmodels8339 full semantic and publisher qualification — October 11, 2026

All 70 reconstructed messages reviewed, including the deliberate failed null-sample
assertion and all completion/cleanup commands. The issue itself supplies both
initialization diagnoses. The finite running-maximum invariant explains the repair;
no general statistical calibration or external-paper equivalence is asserted.
Original 1/4/130 diagnostic test runs overlap. Fresh independent publisher grading
uses 131 full identities: base 130 passed, reference/candidate 131 passed and all
transitions match. The historical original-image control failure remains preserved;
this new evidence is specific to the verified snapshot and exact replay patch.

Mechanical admission passes: 14,841 input / 4,181 supervised tokens, 33 charged
calls, 9,735 reserve margin. Full review permits quarantine replacement, with rights,
frozen splits/duplicates, data scale and GPU runtime still unresolved. Corpus042
remains unchanged pending integration. No production-code changes or Runpod use.
Evidence: statsmodels8339-amended-grade-001, amended-admission-002 and
statsmodels8339-full-history-review-001.

Qualification archive independently restored from R2: 44 files / 566,819 bytes;
statsmodels8339-qualified-publish-001 and restore-001. This includes reconstructed
history, token export, paired grading, admission and full semantic review.


## Corpus043: Statsmodels reviewed replacement — October 11, 2026

Integrated the reviewed 70-message Statsmodels derivative, preserving its explicit
assistant authorship and intentional failed null-sample assertion. Exactly one
record replaced; all other 28 are unchanged. Corpus043 has 575,084 input / 158,892
shifted supervised tokens, independently recounted after R2 restoration. All 59
files / 6,361,386 bytes match. Original/restored schedules are byte-identical:
27 updates, seed 7401, one epoch, zero target overshoot. Quarantine training refusal
is verified; all admission gates remain unset. Emcee295 is the only reserve-policy
exception. This checkpoint does not demonstrate model learning or GPU readiness.

Evidence: corpus043-integration-check-001, training-corpus-selection-042,
training-corpus-assembly-043 and corpus043 transfer receipts. Next: Numba6653
diagnostic review, broader semantic/rights/split reviews, diverse-data expansion
and full training-runtime qualification. No production-code changes or Runpod use.

Integration evidence independently restored from R2: 16 files / 77,952 bytes;
corpus043-integration-publish-001 and restore-001. Numba source inspection confirms
NUMBAPRO values are ignored with a warning; the diagnostic fallback wording and
unasserted warning behavior require correction, while original evidence stays intact.


## Numba6653 deprecated-prefix diagnostic correction — October 11, 2026

Two explicit assistant amendments correct the misleading “working fallback” claim:
NUMBAPRO_ is ignored with a warning and returns the supplied default. Diagnostics
now check the default, exactly one NumbaWarning and identifying message text. The
reproduction's third comparison now contributes to process exit status. Pinned
real-package checks reject the base defect and pass on the candidate. Ten separate
injected faults (missing/duplicate warning, wrong category/message, wrong return,
across two scripts) are rejected. The original reproduction's false success after
a wrong deprecated return is reproduced. This is function-level validation, not
CUDA hardware execution or a general warning-filter/concurrency guarantee.

Evidence: numba6653-diagnostic-001 and diagnostic-validation-002. Validator source
001 had a quoting syntax error and ran no checks; source 002 fixes that and all
checks pass, with container cleanup verified. Fresh native replay attempt 001
rejected shard metadata changes during cloud hydration, without weakening guards.
Replay qualification remains pending; corpus043 is unchanged. No Runpod use.

Fresh native replay 002 completed: 35 charged calls, 36 exchanges and 74 messages;
unchanged 362-byte source patch, verified container cleanup. Token audit is
untruncated: 16,381 input / 6,152 supervised, with 8,195 output-reserve margin.
Diagnostic archive is independently restored from R2: 21 files / 111,390 bytes.
Independent grading and full semantic review remain pending before replacement.

Native replay, history and token archive independently restored from R2:
14 files / 409,020 bytes; numba6653-amended-replay-publish-001 and restore-001.


### October 11 — Numba failure reporting and bounded claims

The completed replay review exposed a pytest-to-head pipeline that hid a CUDA
collection error, a CPU JIT example without result assertions, and a catch-all
import check that could accept unexpected failures. Added three explicit command
amendments alongside the two prior deprecated-warning amendments. Verified the
real pytest exit 2, rejection of deliberately wrong JIT output and import failure,
and four separately labeled output/status fixtures. Fresh replay and independent
publisher grading pass their bounded checks; patch unchanged. Mechanical admission
passes, with 17,157 input and 6,353 supervised tokens. Final content-review record
and corpus integration are next; no training authorization or general CUDA claim.
The 55-file / 534,569-byte qualification bundle is uploaded and independently
restore-verified in R2. Corpus043 remains current. Runpod unused.


### October 11 — Reviewed Numba integrated into corpus044

Completed the 74-message semantic review, retaining the no-match grep, base
reproduction failure and CUDA collection error. Explicitly limited driver checks,
CPU JIT and CUDASIM-variable retrieval claims; the issue itself supplies the defect.
Replaced exactly one corpus record, preserving the other 28 byte-for-byte at the
manifest-record level. Corpus044 has 575,853 input and 159,348 supervised tokens.
All 59 files / 6,370,249 bytes are uploaded and independently restored from R2.
Independent shifted-label accounting matches, schedules are byte-identical with
27 updates and no target overshoot, and restored training loads reject quarantine.
All four admission gates remain null; Emcee295 is still a reserve exception.
Next work: broader corpus semantic/rights/split qualification, substantial data
expansion, and eventual full-model runtime qualification. No Runpod use and no
learned model-performance claim. Integration review evidence is preserved separately.


### October 11 — New repository batch004

Selected and independently verified 32 new repository candidates against corpus044,
excluding prior batches and reserved/current repository names. All four rank strata
have eight selections; no exclusion overlap. The queue is not new training data.
Rechecked the 38,705,625-target optimistic single-pass ceiling for one trace per
screened task; this is below a 50M campaign and precedes prompt masks/rejections.
Next: issue/action and credential screening beginning with fuzzyfinder19, then
source lineage, rights and bounded runtime checks. No image downloads or Runpod.
Source-proxy counts must not be interpreted as native target counts. Three
cloud-hydration failures were resolved through hash-verified stable metadata copies.
Evidence: qualification-batch-current-004; preservation receipts identify R2 status.


### October 11 — Fuzzyfinder19 extraction and finite oracle

Extracted 27 source actions from hash-verified immutable Parquet bytes, with
reserved-repository checks before parsing and a full-message credential-indicator
screen before displaying content. The standard extractor first rejected hydration
metadata drift; the bounded snapshot extraction retains source digest verification.
Inspected the action sequence and independently checked the extracted matching
function with 6,344 finite ASCII subsequence/order comparisons. Reproduced hidden
pytest failure in the original final wrapper and an omitted valid match in printed
expectations. This candidate remains held pending explicit diagnostic amendments,
publisher contract/source checks, native replay, grading and content/token reviews.
No added corpus row, learned gain, new image download or Runpod use. Preserve
triage evidence in R2 with independent restoration before local cleanup.


### October 11 — Fuzzyfinder19 held for API contract mismatch

Extracted pinned publisher issue/reference/tests after source-identity and reserved
repository checks. The required publisher keyword is ignore_case=False; the teacher
instead implements case_sensitive=True, matching the issue snippet but incompatible
with the reference API. Exact extracted-function execution confirms TypeError for
the publisher keyword and correct matching through the teacher keyword. No full
publisher test-suite claim follows. Preserve both findings; do not silently change
the API to obtain a passing grade. Candidate excluded pending task-alignment
resolution, with any future amendment explicitly reference-informed. Continue
batch004 elsewhere; corpus044 unchanged. One mistyped image ID was rejected before
container creation; corrected validation succeeded. No Runpod or image download.


### October 11 — MkDocs Merge18 finite structural validation

Extracted pinned teacher and publisher records and inspected 33 actions. The teacher
index-based update passes 2,343 finite unaliased-tree oracle comparisons; the
publisher value-based update disagrees in 381, with a concrete path-collision
witness preserved. This does not substitute for actual repository/publisher grading.
An initial fixture unintentionally shared dictionaries and failed; preserved that
failure and separately demonstrated repeated-reference double prefixing. The stated
successful domain excludes aliases and cycles. The reproduction script also hides
the base defect by omitting equality and exit checks. Next: explicit diagnostic
amendments, exact base/source and runtime validation. No corpus addition, learned
performance claim, GPU use or container download. Preserve triage through R2
publish and independent restore; receipts establish transfer completion.


### October 11 — MkDocs Merge selected-source compatibility

Five files were fetched from the exact task base commit, including the source,
original test file and MIT notice. The teacher replacement text matches that
source exactly. The first package probe failed on missing ruamel.yaml before
any test result. A second probe used the existing Python 3.12.4 interpreter with
that dependency, verified imports from each staged role directory, applied the
publisher test patch unchanged and executed its four unittest methods: base 3/4,
reference 4/4, teacher 4/4. This is selected-source compatibility evidence, not
the publisher Python 3.9 environment, complete checkout or native replay.
The corrected reproduction now compares complete trees and exits 1 on base,
0 on reference and 0 on teacher. Two hash-bound assistant amendments retain the
source repair: reproduction failure propagation and narrower final-example wording.
Fresh native replay, qualified grading and token/content review remain pending.
Evidence: mkdocsmerge18-package-validation-001/002 and amendments-002.
The initial amendment receipt overcounted charged calls: 33 normalized actions
include three think records and finish, leaving 29 charged calls. The corrected
receipt supersedes that count; action and amendment bytes are unchanged.

No Runpod or container download; corpus044 remains unchanged.


### October 11 — Complete MkDocs Merge source and compatibility boundary

The complete 19-blob source snapshot now matches every Git blob and reconstructed
tree hash, rooted at fb7fec40eca289ec02883709c8715c9babea78ba, linked to the
publisher base commit. Publisher image metadata is pinned; about 688 MB of
compressed layers appear missing locally, with unknown unpacked growth and only
about 3.7 GiB free. No image pull was attempted.
Executing all five repository unittest methods on Python 3.12.4 exposed a shared
compatibility error: this source assigns a dict to distutils _path_created, while
the installed implementation expects a set. Base passes 3/5; reference and teacher
pass 4/5. All three fail the filesystem merge test with the same AttributeError.
The initial probe that expected a complete pass is preserved. The corrected
reproduction still exits 1/0/0 on base/reference/teacher. This does not establish
publisher Python 3.9 or native replay readiness. Next: prepare a bounded compatible
Python 3.9 runtime using the verified tree, or use the pinned publisher image once
local capacity permits. Do not alter production source/tests to hide this error.
Evidence: mkdocsmerge18-image-001, snapshot-001 and full-tree-validation-001/002.

Corpus044 unchanged; Runpod unused. Snapshot and failures preserved through R2.


### October 11 — MkDocs Merge Python 3.9 validation

A cached Python 3.9.23 ARM64 image and a hash-verified 109,478-byte pure-Python
ruamel.yaml 0.17.21 wheel were used offline. All five repository test methods ran
without skips on the complete pinned source tree: base 4/5, reference 5/5,
teacher 5/5. The filesystem merge test that failed on Python 3.12 now passes in
all roles. Corrected reproduction exits are 1/0/0. Imported paths point into the
staged role trees, and all source bytes remain unchanged after testing.
This resolves the observed compatibility obstacle for this specific environment;
it does not qualify the original AMD64 publisher image or a native agent replay.
No new Docker image or GPU was required. Only the small pinned wheel was downloaded.
Next: prepare a bounded native replay runtime with explicit architecture/provenance,
verify actual call/context budgets and preserve the diagnostic amendments.
Evidence: mkdocsmerge18-py39-validation-001 and py39 transfer receipts.

Corpus044 unchanged; Runpod unused. Native replay and training admission remain pending.


### October 11 — MkDocs Merge actual submitted-patch grading

The reconstructed Python 3.9.23 ARM64 runtime completed a fresh native teacher
replay: 29 charged calls, 62 history messages, and a 729-byte source-only patch.
Token audit reports 15,614 input tokens and 4,876 supervised tokens, without
truncation, with 8,962 tokens remaining after the configured output reserve.
The exact runtime and replay bundle (55 files / 91,835,477 bytes) was uploaded
and independently restored from R2 with byte verification.

Independent grading applied the actual submitted patch (SHA256
2c49a54bcfb200059b977dd449492ffd2d1597009a53c5fd512128a1a1b0e8a1)
to the pinned source tree, alongside unchanged publisher tests. All five test
methods executed with zero skips: base 4/5, publisher reference 5/5, submitted
patch 5/5. The corrected diagnostic exits 1/0/0 respectively. Import origins
and unchanged source bytes were checked; the grading container was removed.
This qualifies only the reconstructed ARM64 environment, not the original
AMD64 publisher image. Its testbed interpreter is a stdlib venv, not a Conda
installation. Earlier finite structural checks do not imply general correctness.

Full 62-message content review and mechanical admission remain pending before
corpus integration. Corpus044 is unchanged; training remains unapproved.
Runpod was not used. Evidence: mkdocsmerge18-native-002, tokens-001,
native-restore-001 and native-grade-001 under evidence/data.

The independent grading bundle (79 files / 120,412 bytes) is also uploaded
and independently restore-verified in R2; see native-grade-publish-001 and
native-grade-restore-001 receipts.


### October 11 — MkDocs Merge complete history review

All 62 messages were read and reviewed, with indexed findings covering each
message exactly once. Thirty tool exchanges include 29 charged calls and terminal
submission. The actual history retains one failed tool result: the corrected
base reproduction at message 29. No grep error appears in this replay. Both
attributed diagnostic amendments are present; existing tests remain unchanged,
and the submitted patch edits only source. Finite scratch tests assert expected
results and propagate failures. No general alias/cycle guarantee is supported.

Content review is complete for this history, but admission remains pending.
The independent unittest grading on reconstructed ARM64 needs a correctly bound
report accepted by the admission pipeline; do not relabel it as original publisher
image grading. Rights, frozen splits, evaluator qualification and training runtime
gates remain open. Corpus044 unchanged; no Runpod use.
Evidence: evidence/data/mkdocsmerge18-full-history-review-001/report.json.


### October 11 — MkDocs Merge pytest qualification and mechanical admission

Fresh isolated pytest runs on the exact reconstructed ARM64 image now retain
full node identities and setup/call/teardown phases. All four publisher-declared
transitions match; the filesystem merge test is explicitly recorded as one
supplemental pass-to-pass test, not misrepresented as a publisher declaration.
Base passes 4/5; reference and actual native candidate pass 5/5, with no skipped
or missing phases, collection errors, outcome disagreements or source mutation.
All containers cleaned up. Image, source tree, native receipt and patch identities
are bound in the report; runtime provenance remains explicitly reconstructed.

The existing mechanical replay assessor passes without changing its guards.
Training remains unapproved; rights, split isolation, evaluator qualification
and training runtime gates remain open. Corpus044 is unchanged.

The shared test-container helper now accepts only explicit linux/amd64 or
linux/arm64 platforms, preserving AMD64 as default and recording the selection.
Sixteen focused unit tests passed across platform rejection, replay grading,
control profile, admission and snapshot controls. Three live ARM64 grading runs
exercise the new execution path. Scoped diff checks passed.
Evidence: mkdocsmerge18-pytest-grade-001 and mkdocsmerge18-admission-001.
Runpod unused. Next: integrate the reviewed example into a new quarantined
corpus version, verify token accounting and restore reproducibility.


### October 11 — Corpus045 quarantine integration

Added the reviewed MkDocs Merge18 native derivative; all 29 prior example records
remain byte-identical. Thirty tasks now total 591,467 input tokens and 164,224
shifted supervised targets, independently recounted after R2 restoration. All
61 files / 6,540,367 bytes were restored and verified. Original/restored exposure
schedules are byte-identical: 27 updates, one maximum epoch, seed 7401,
9,216-target update cap and zero overshoot. Only Emcee295 retains a reserve
exception. Training-purpose loading rejects the restored quarantine.

Initial assembly failed on the existing workspace directory guard; the second
attempt encountered the first attempt's existing output directory. Both scripts
are preserved. The successful third attempt uses verified copies within the
runtime workspace and a fresh output path. No guard was weakened.
All four corpus admission gates remain null. Corpus growth does not establish
rights, frozen split isolation, GPU training readiness, or improved model skill.
Next: continue diverse source qualification and address the open admission gates.
Runpod unused. See corpus045-integration-001 and corpus transfer receipts.


### October 11 — Current corpus repository-network isolation review

Fetched only public GitHub repository metadata for all 29 corpus repositories
and four reserved evaluation repositories. All 33 requests resolved. Verified
response hashes and repository/fork-network IDs show no declared-name overlap
or fork-network overlap with the reserved repositories. Infinidat/munch belongs
to the dsc/bunch network, which is explicitly represented in the new draft.
Thirty training tasks map to 29 network groups. The draft passes structural
split validation and is bound to corpus045 and the captured metadata.

This replaces reliance on the old two-example split draft for current coverage;
it does not freeze the split or approve training. Metadata does not detect
detached copies, semantic task duplication, hidden evaluation tasks or prior
model exposure. No reserved issue text or solution/test patches were accessed.
Remaining split requirements are enumerated in corpus045-split-review-001.
Evidence: corpus045-lineage-001 and corpus045-split-review-001.
Corpus unchanged; Runpod unused.


### October 11 — Corpus045 within-training issue duplication audit

Read all 30 issue texts only after verifying each complete replay history against
the corpus token audit's pinned SHA256 and byte size. All 435 unordered pairs
were compared: no exact or NFKC/casefold/whitespace-normalized duplicates.
Five-token shingle intersection/union counts were independently recounted for
every pair, with exact rational ranking. Highest Jaccard similarity is 46/662
(approximately 0.06949) between the two PennyLane issues. Manual inspection of
the four highest-ranked pairs finds distinct requested repairs; shared issue
templates and GitHub link syntax contribute lexical overlap.

This is not an exhaustive semantic review, statistical independence proof, or
train/evaluation contamination clearance. No similarity threshold automatically
admits a task. No reserved evaluation issue content was read. The two PennyLane
examples stay in the same repository group. Training remains unapproved; current
corpus and Runpod state unchanged.
Evidence: corpus045-issue-audit-001/report.json, pairs.json and review.json.


### October 11 — Restore disk preflight and interruption validation

ArtifactStore.restore now checks filesystem free space against the declared
payload bytes before creating staging or making network requests. It preserves
the existing total-byte cap, hash validation and atomic directory promotion.
This is a lower-bound preflight, not a reservation: metadata overhead, quotas
and concurrent allocations can still exhaust storage.

Twenty-nine object-store/corpus tests passed. New fault tests verify that
insufficient space prevents download, a midstream disconnect closes the body
and removes staging, and fsync ENOSPC never exposes a partial destination.
Both interrupted cases allow a subsequent verified retry. Live R2 restore
through the updated implementation recovered six files / 156,356 bytes.
Two earlier wrapper attempts failed with pre-transfer ValueError and have no
passing receipt; their root cause was not established. A diagnostic invocation
of the same main function succeeded without implementation or credential changes.

Evidence: storage-preflight-live-003 and storage-preflight transfer archive.
This does not establish resumable partial-file downloads or GPU training
readiness. The trainer still requires an admitted training-purpose corpus.
Corpus045 unchanged; Runpod unused.


### October 11 — Training deployment includes the ingestion path

The separate training-worker source bundle now includes transfer_artifact.py
and object_store.py; the main inference deployment already included them.
Seven staged CLI entrypoints pass isolated import checks. The 39-file source
bundle totals 209,315 bytes and contains no credentials or model weights.
Pinned serving requirements already declare the R2 transport dependencies.

Using only the staged transfer CLI from outside the repository, live R2 restore
recovered all 61 Corpus045 files / 6,540,367 bytes. The staged corpus inspector
verified the restored manifest and accepted inspection; training-purpose loading
failed with the required quarantine rejection and produced no success report.
The first staging attempt rejected an observed source ctime/flag change; reading
the explicit source list and using fresh paths allowed the existing guard to pass.

Evidence: training-deployment-storage-check-002, training-deployment-restore-001
and training-deployment-validation-001. These prove local source closure and
ingestion behavior, not pinned Linux CUDA, adapter training, or GPU readiness.
Runpod unused; training admission remains closed.


### October 11 — Current-corpus attribution evidence index

Created a 30-row inventory bound to the Corpus045 manifest. Six explicitly
located historical rights/attribution reports are indexed, with their retained
notice files copied only after SHA256 and size verification. The other rows
are marked not indexed in this pass, not asserted to lack all existing evidence.
No current-history rights binding is claimed from historical report presence.
The easy-ptvsd material report explicitly records a missing ptvsd notice.

Next actions: map current observed files and dependency output to notice coverage,
resolve that recorded missing notice, and index remaining exact source captures.
This is an evidence inventory, not legal clearance or a training authorization.
Evidence: corpus045-attribution-index-001. No corpus admission gate changed.
The broader CPU regression is still running through local dependency imports;
no overall result is claimed. Runpod unused.


### October 11 — ptvsd 3.0.0 notice supplement

Investigated the easy-ptvsd dependency capture gap against the exact installed
version. The PyPI 3.0.0 source archive is 51 KB and matches the release SHA256
44fe6af915711b5f144d5344fa24b524d6b19cb0dbd784e177e3e65935d458dc.
It contains no standalone LICENSE/NOTICE file. Its seven Python package files
carry Microsoft copyright and Apache-2.0 headers; all seven match the installed
files byte-for-byte in the pinned easy-ptvsd runtime. The offline export container
exited successfully and was removed.

Preserved those headers and the separately fetched official Apache license text
in ptvsd300-supplement-001. The historical missing-file report remains unchanged;
this is a supplementary evidence capture, not blanket rights clearance. Current
trajectory observation coverage, other dependencies and corpus admission remain
open. Sources: https://pypi.org/project/ptvsd/3.0.0/ and
https://www.apache.org/licenses/LICENSE-2.0.txt .
Runpod unused. The existing broad CPU regression process remains pending.


### October 11 — Touvlo34 source and exact recurrence triage

Extracted the preselected Benardi/touvlo task from its pinned local SWE-Hero shard
after repository exclusion and full-byte SHA256 verification. Forty-two source
actions are retained; no source shell command was executed. The first file read
timed out; the successful retry verified the complete pinned bytes before parsing.

The extracted proposed function passes 432 finite scalar Fraction cases against
the affine-gradient closed form theta_n=(1-alpha*scale)^n*theta_0 minus
alpha*offset times the finite geometric sum. Base rejects the new keyword inputs.
The candidate rejects an unwrapped positional-only extra parameter, so this
cannot establish the source's broad any-signature claim. No convergence or NumPy
array guarantee follows from the scalar identity checks.

Source diagnostic 48 catches failures without propagating them; action 78 prints
passed based on shapes without checking numerical values and overstates coverage.
Correct diagnostic behavior with explicit attribution before fresh replay.
Publisher alignment, full content review, native budgets and grading remain
pending. Corpus045 unchanged; Runpod unused.
Evidence: touvlo34-teacher-001 and touvlo34-static-001.


### October 11 — Broad CPU regression failed during dependency loading

Run001 completed 89 tests: 49 passed, zero assertion failures, 40 errors and
zero skips. The first error was errno 60 while Python loaded torch.distributions.
Subsequent errors report partially initialized Torch or missing torch.cuda.
This is a failed qualification run, not numerical acceptance; no production
mathematical defect is established by these import errors. Full traces retained
in p1-data-regression-001. Versions: Torch 2.14.1, Transformers 5.13.1, PEFT 0.21.2.
A fresh run002 imports dependencies before tests and uses a /tmp bytecode cache;
its result is pending. No test expectation or production algorithm was changed.
Runpod unused.


### October 11 — Touvlo34 held after publisher contract comparison

Pinned publisher extraction reveals a calling-convention mismatch. Teacher code
retains grad(theta, X, y, **kwargs), whereas the reference and both new tests
require grad(X, y, theta, **kwargs). An exact Fraction witness with gradient
returning its third argument, X=5, y=7, theta0=2, alpha=1/2 and two iterations
returns -5 under the teacher but should return 1/2 under the publisher contract.
The argument-call log confirms the ordering discrepancy.

The 432 prior scalar checks remain valid only under the teacher callback order;
they do not qualify task alignment. Mark this candidate held; do not spend time
on a native replay or silently alter its repair to the reference. No publisher
suite was run, so this is a direct contract counterexample rather than a full
repository score. Corpus045 unchanged. Evidence: touvlo34-contract-001 and
touvlo34-evaluator-001. Runpod unused. CPU regression run002 remains pending
in dependency import preflight.


### October 11 — R2 recovery bypasses local source hydration failure

CPU regression002 terminated during Torch import preflight with errno 60; no
tests ran. It is no longer pending. The referenced Torch sparse source file is
marked dataless by macOS, and the CPU environment imports repository .venv
packages through project-host.pth. Moving bytecode to /tmp did not resolve this.
Full CPU numerical qualification remains failed/unproven; do not start Runpod.

Flake8 source extraction001 and publisher extraction001 also terminated on local
shard reads. Restored the 200,489,804-byte teacher shard directly from R2, bound
to the previously published manifest and pinned SHA-256
529244ce0c3465c022565e8c6eeb3ef3d6b2981cabfb76dbed4f02c4f782722d.
Extraction002 succeeded: 36 actions, 33 potentially charged after excluding two
think actions and finish. Actual native budget remains unmeasured.

Task PyCQA__flake8-1642 proposes catching OSError in _stat_key for nonexistent
HOME. Action-argument review found diagnostics that catch errors without nonzero
exit, a subprocess check accepting exit 1 without validating its output, and an
unsupported universal backward-compatibility claim. Publisher comparison,
full message/result review, corrected diagnostics and native grading remain
required. No source commands were executed; corpus045 is unchanged.
Evidence: evidence/data/flake81642-triage-001/report.json.

Flake8 triage evidence: 8 files / 173,099 bytes published to R2 and independently
restored with hash verification (flake81642-triage-publish-001 and
flake81642-triage-restore-001). Removed only the temporary 200,489,804-byte
R2 download after verifying its identity again; original local source and R2
blob remain intact. No Docker, model, dependency or user data was deleted.


### October 11 — Flake8 candidate held on error-propagation regression

Recovered the 101,556,119-byte pinned publisher shard from R2 with complete
SHA-256 verification, then extracted evaluator002. Publisher catches OSError
only for HOME; teacher catches it inside every _stat_key invocation.

Fetched config.py at base commit 446b18d35a5fa0be6b3531d30a0706fc82247313;
its Git blob hash matches publisher patch index f5c93ce. Executed only the two
reviewed config-discovery functions from base, reference and candidate using
real temporary directories and controlled stat failures. In the missing-HOME
case, base raises and both repairs return None. Four additional witnesses
(start/ancestor crossed with FileNotFoundError/PermissionError) show base and
reference propagating errors while candidate silently returns None.

These witnesses contradict universal backward compatibility; they do not claim
the candidate fails the publisher's single new missing-HOME test. Hold the
unchanged teacher candidate for broader error suppression. Do not silently
substitute the reference repair or admit this as verified training behavior.
This was a focused differential function evaluation, not a full repository
pytest run, native replay or general correctness proof. Source tool logs show
23 config tests and 27 selected config-related tests passing historically; those
are teacher logs, not newly reproduced results. Full-history review is unfinished.

Evidence: evidence/data/flake81642-contract-001/report.json and
flake81642-evaluator-002. Corpus045 unchanged; Runpod unused. CPU import
qualification remains unresolved as recorded above.

Contract archive: 14 files / 34,106 bytes published and independently restored
with hash verification (flake81642-contract-publish-001 and restore-001).
Removed only the identity-rechecked temporary 101,556,119-byte R2 download;
original local shard and remote blob retained.


### October 11 — CPU dependency import recovered outside cloud storage

Created /tmp/zenithsync-cpu-local-p1-001 without a project-host.pth dependency on
the cloud-managed repository .venv. Cached Torch 2.14.1, Transformers 5.13.1 and
NumPy 2.5.3 wheels matched the exact SHA-256 and size in PyPI release metadata.
PEFT 0.21.2 and dependencies were installed by pip; full install report, package
freeze and pip-check result are retained in evidence/data/cpu-recovery-001.
Transitive packages were freshly resolved, so this is not an assertion of exact
identity to the earlier runtime. pip check reports no broken requirements.
Runtime occupies approximately 725 MB; disk free was approximately 2.1 GiB.

Regression003 imports Torch, Transformers and PEFT successfully and verifies
that those module paths are under the fresh runtime prefix. This resolves the
observed dependency-import failure for this invocation. The complete 19-module
regression cohort has been launched; it is not yet a passing test result.
Repository source loading may still encounter local hydration delays. Runpod
remains unused; no full model training readiness is established.

CPU recovery evidence: 7 files / 578,164 bytes uploaded to R2 and independently
restored with hash verification (cpu-recovery-publish-001 and restore-001).

Regression003 completed: 89 tests passed, zero failures, errors or skips,
72.05 seconds reported elapsed. All 19 requested modules ran under the fresh
CPU environment; report binds test source hashes before/after execution and
runner identity. No production-code change was made in this recovery cycle.
This establishes local CPU regression acceptance, including reduced Gemma,
not full 31B or Linux GPU readiness or corpus admission. Earlier failed runs
remain retained. Evidence: evidence/data/p1-data-regression-003.


### October 11 — Repository-wide regression refresh launched

The 89-test CPU training/data cohort is already passing. The broader repository
suite is now being collected using the recovered local CPU runtime, with Torch
checks enabled. Attempt001 failed before collection because the runner supplied
a repository top-level directory although tests is not a regular package.
Attempt002 uses the README-compatible discover start directory without that
override; it is live, not a passing result yet. Optional dependency omissions
will be reported as coverage gaps, not verified behavior. No production code or
test expectation was changed. README now refers to corpus045's 30 quarantined
examples; current readiness summary includes the recovered CPU result and held
Touvlo, Fuzzyfinder and Flake8 candidates. Runpod remains stopped.


### October 11 — Full-suite cache isolation and data test dependencies

Attempt002 was observed reading a cloud-managed tests/__pycache__ bytecode file.
-B disables writes but does not bypass existing cache reads. After an interrupt
request did not promptly terminate it, a targeted SIGTERM was sent. Collection
completed (462 tests) during this transition and four test completions reached
the partial log. Exit143 is an interrupted run, not a suite result. The retained
interruption record states this race explicitly; no successful run is claimed.

Installed requests 2.34.2 and pyarrow 25.0.1 in the isolated CPU environment to
exercise optional HTTP-resource and Parquet-ingestion tests. pip check passes;
updated frozen requirements and installation report are retained. Approximate
remaining free disk: 2.0 GiB. Attempt003 uses a separate /tmp bytecode prefix
and prints module collection progress. It remains in progress. No production
algorithm or test expectation changed, and no Runpod resources were used.
Evidence: evidence/data/full-suite-recovery-001.


### October 11 — Full local regression passes

Attempt003 completed all 463 tests with zero failures, errors or skips in
220.88 seconds including collection. This covers the current discovered local
unittest suite under the recovered CPU runtime, including Torch, HTTP-resource
and Parquet checks. No production algorithm or test expectation was changed.
The runner and complete test log are retained; the receipt does not claim a
complete before/after repository source snapshot. Prior failed/interrupted
attempts remain preserved. Full-model GPU behavior, training-data rights and
admission, dataset sufficiency and learned repair gains remain unproven.
Evidence: evidence/data/p1-full-regression-003. Runpod remains unused.


### October 11 — Corpus045 review linkage index

Verified the corpus045 manifest and all 30 audit identities, then indexed
explicitly named /tmp/zenithsync-*-full-history-review-*/report.json files.
Nine of 30 exact history identities matched, with zero read errors. The other
21 are not indexed by this naming/location-limited pass; this is not proof their
reviews are absent. Older report formats and locations require reconciliation.
Matched reports are preserved by content hash, but identity linkage alone does
not establish complete or correct semantic review. No admission gate changed.
Evidence: evidence/data/corpus045-review-coverage-001/report.json. Next work:
resolve the 21 unmatched current histories against their original qualification
and review evidence before considering task-alignment admission.


### October 11 — Lmfit current-history review chain reconciled

Expanded /tmp review/admission/semantic indexing finds exact-history evidence for
13 of 30 examples, but mechanical admission reports are not full-content review.
A repository evidence scan (coverage004) is still running to resolve older formats.
Coverage003 was stopped after detecting an incorrect reused output-directory
literal; no previous output was overwritten. Its script, log and interruption
record remain available. Coverage002 remains an intermediate limited index.

Lmfit's current history has an existing full-content-review-002 report rather
than a full-history-review-named report. Independently verified corpus/audit/history
identities, all 168 old/current per-message hashes, complete nonoverlapping prior
review ranges and the exact partition of 84 current messages: 71 unchanged and
13 reviewed changes. Both scope notes match their bound hashes. This resolves
one of the initial 21 catalog gaps through its existing review chain. It is not
a new semantic or rights approval; the corpus and all admission gates are unchanged.
Evidence: evidence/data/lmfit487-review-chain-001. Runpod remains unused.


### October 11 — Corpus evidence index and reusable review coverage checks

Coverage004 completed: 219 unique named repository reports inspected, with exact
history links for 29 of 30 current examples; Optuna3545 remains unmatched in this
bounded scan. Mechanical admission, selected-claim reviews and full-history
reviews remain distinct. This is not 29 semantic approvals. Nine original /tmp
full-history report matches remain recorded separately. The expanded report and
49-file / 518,485-byte referenced evidence archive preserve the links.

Added zenithsync/review_coverage.py for native message lists with explicit full
review sections. It checks caller-supplied file digests, byte ceilings, strict
message-count and index coverage, canonical per-message hashes, nonempty findings,
bounded inclusive ranges, absence of gaps/overlaps and unchanged input identities.
Its result explicitly disclaims semantic truth, rights and training approval.
Inherited/delta reviews require separate chain validation; they are not accepted
as explicit full-range reviews by this API. Seven new fault/coverage tests plus
six adjacent task-alignment and file-integrity tests pass (13 total). The prior
463-test full-suite result predates this isolated addition; no new full-suite
count is claimed.

Applied the verifier to current Signac622: all 78 message bindings and 10 complete
nonoverlapping review sections agree with corpus045's exact history. The bound
scope note also matches. This reconciles its existing version002 full review,
which the earlier /tmp-only search missed. Corpus and admission gates unchanged.
Evidence: corpus045-review-coverage-004 and signac622-review-coverage-001.
Runpod unused; data rights, broader semantic acceptance, abundance and GPU
qualification remain open.


### October 11 — Optuna evidence linkage resolved; diagnostic hold identified

Optuna's observation review binds native replay events and receipt, not the
rendered history directly. Verified the corpus audit/current history identity,
history-receipt inputs, shared replay event/receipt identities, exact completion
plan and submitted patch. This resolves the catalog gap by an indirect chain.
The corpus therefore has 29 direct indexed history links and one explicitly
verified indirect link; these are not 30 full semantic approvals.

Message50 writes final_verification.py. A bounded synthetic fault probe executes
that exact diagnostic with an injected GridSampler stub that emits no unsupported
value warnings while the categorical stub warns. The diagnostic prints
Inconsistent behavior yet exits zero. This is a failure-propagation witness for
the diagnostic, not a new actual-Optuna performance or repair result. Existing
completion assertions remain useful finite checks but do not correct earlier
supervision. Hold this history for explicitly attributed diagnostic correction,
fresh replay and content review. Corpus045 remains unchanged and quarantined.

Evidence: evidence/data/optuna3545-review-link-001; the archive includes original
history, linked receipts/events, original diagnostic and labeled synthetic probe.
Full history review is not established by this linkage. Runpod unused.


### October 11 — Optuna diagnostic corrections qualified locally

Prepared four explicitly attributed source-action replacements for reproduction,
post-fix checks, edge cases and final verification. Warning counts/categories,
valid-value silence, mixed choices and the two-point actual in-memory study now
use assertions. Broad compatibility claims and caught-but-unpropagated diagnostic
errors are removed. Original implementation edit and other source actions remain
unchanged; old records remain retained.

The pinned local Optuna image was already available; no pull or Runpod use.
Four revised programs pass against the actual patched source. The pre-repair
reproduction exits nonzero with ValueError. Eight separately labeled injections
(missing warnings and wrong warning categories for each program) reject with
AssertionError. Original source hash, package origin, exact patch application,
unchanged final diff and container cleanup were checked. This is finite diagnostic
validation, not fresh native replay acceptance or universal repair correctness.

The old finite completion is rebound to the derived action identity. Recovered
the exact 245,825,405-byte original trajectory shard from its R2 manifest and
verified SHA-256. Fresh amended native replay001 is launched with the existing
40-call profile; it remains pending. Corpus045 remains unchanged and quarantined.
Evidence: optuna3545-amendments-001 and optuna3545-diagnostic-validation-001.

Fresh replay001 completed: 30 charged calls, unchanged patch SHA-256
64a2a53b29e79186d744d165e0754ee7313f387271534f2199a30c28a3fd7740,
finite completion passed and container removed. Source errors 32,36,46 remain
visible (no-match grep, desired-behavior reproduction before repair and obsolete
ValueError expectation). Reconstruction, full-content review, grading and token
audit remain pending; no corpus replacement or training admission yet.


### October 11 — Amended Optuna reconstruction, tokens and independent grading

Reconstructed 64 messages / 31 exchanges from the amended native replay. The
pinned tokenizer audit passes without truncation: 17,588 input tokens and 3,539
supervised shifted targets; exported arrays and collator counts agree. The first
audit attempt failed before encoding because its selected runtime lacked the
model manifest. The successful attempt uses the existing pinned validation
runtime and verifies model tokenizer assets and history identities.

Independent grading attempt003 uses the actual replay patch. Base passes 8/9;
reference and candidate pass 9/9. All publisher transitions and candidate versus
reference cases match. Package origin, unchanged tracked diff during tests,
input identities and container cleanup are checked. Attempts001/002 stopped
before tests because macOS placeholder hydration changed metadata during strict
inventory; inputs were hydrated before retry, without weakening checks.

The history/token archive (11 files, 296,140 bytes) is R2 uploaded and
restore-verified. Grading evidence (32 files, 108,890 bytes) is uploaded and independently
restore-verified (optuna3545-amended-grade-restore-003). Full transcript
content review and corpus replacement remain pending. Corpus045 stays unchanged
and quarantined. No Runpod use or training approval.


### October 11 — Full Optuna review and corpus046 replacement

Read all 64 amended messages in four bounded groups, then recorded 12 exhaustive
nonoverlapping review sections and per-message canonical hashes. The review
retains errors at messages31/35/43: no-match search, pre-repair reproduction and
obsolete ValueError test. Eight selected source-test passes are distinguished
from the independent publisher-patched nine-case grading. The six-point integer
objective oracle proves only the finite enumeration result, with unique minimum
1 at (1,0). NumPy seeding does not establish deterministic Python random order;
coverage assertions are order-independent. No persistence or universal claim.
Review coverage passes and its 10-file / 134,269-byte archive is R2 restore-verified.

The admission-format grading summary derives from existing three-arm outcomes,
not a new test run. Mechanical assessment002 passes with no blockers. The first
summary attempt rejected cloud hydration before creation; a dependent invocation
then failed on the absent summary. Hydration completed before strict retry.
No integrity checks were weakened.

Corpus046 replaces only Optuna: 30 tasks, 29 declared repositories, 588,288 input
tokens and 162,093 supervised shifted targets. All four admission gates remain
null. Its 61 files / 6,507,113 bytes are R2 uploaded and independently restored.
Independent recount agrees; restored training loading rejects quarantine. Local
and restored schedules match byte-for-byte: 26 updates, zero overshoot, seed7401,
max_epochs1, supervised update cap9216. Emcee295 alone exceeds the context cap
with the 8,192-token output reserve. A 50M-token campaign needs about 308.46 passes
of this corpus; it is not sufficient diversity.

Evidence: corpus046-integration-001, corpus046-optuna-schedule-001,
training-corpus-publish-046 / restore-046. A pre-existing schedule-046 directory
caused initial archive preparation to stop; it was preserved, and current
schedule evidence uses the explicit optuna path. Integration archive publication
uses corpus046-integration-publish-002; all 15 files / 66,383 bytes are independently
restore-verified in corpus046-integration-restore-001.
No production code changed this cycle. No Runpod execution or training approval.


### October 11 — Current-history attribution and split evidence binding

Recovered the SWE-Hero and SWE-rebench cards at their exact intake revisions;
SHA-256 and sizes match the original receipts. Captured Optuna's MIT notice from
the pinned local image. A separate source capture verifies clean HEAD, tree,
base commit, and each Git blob for README, GridSampler, distributions, grid tests
and LICENSE. All five read_file outputs in the current Optuna history match
exact source line slices, including the explicitly truncated first GridSampler
read. Recorded dataset declarations, repository notice and transformation
attribution separately. This does not clear dependencies, indirect shell output
or original teacher-service terms, nor other 29 corpus examples.

Rebound the split draft to corpus046 input identities and verified unchanged
task/repository/leakage/split assignments for all 30 tasks. Prior repository API
responses are hash-verified; their original observation timestamp is retained.
No fresh network lookup is claimed. The draft remains unfrozen and does not
establish semantic near-duplicate isolation or hidden-evaluation cleanliness.

Evidence: corpus046-attribution-001; all 21 files / 170,039 bytes are R2 uploaded
and independently restore-verified (publish-001 / restore-001). No production
code changed, no training approval and no Runpod use.


### October 11 — Reusable exact lexical similarity and corpus046 screening

Added zenithsync/issue_similarity.py and six tests. The implementation indexes
sets of contiguous token shingles after explicitly heuristic NFKC/casefold/space
normalization. Short issues use their complete token tuple. For sets A and B,
Jaccard is |A∩B|/(|A|+|B|-|A∩B|), containment is |A∩B|/min(|A|,|B|). Fractions
are compared exactly. Each unique shingle contributes once to each posting-list
pair, so accumulated counts equal intersections. Because both thresholds are
strictly positive, omitted zero-intersection pairs cannot meet either threshold.
This is exact only for the defined lexical representation, not semantic meaning.

Document, total-token and candidate-pair limits reject exhaustion without a
partial report. Callers must separately bound input bytes before parsing.
Common boilerplate can still create quadratic candidate work; no unmeasured
large-corpus throughput or semantic recall claim is made. Tests cover exhaustive
independent randomized-set comparisons, input ordering, exact rational boundary,
containment-only flags, repeated-shingle multiplicity, short Unicode text,
invalid inputs and limit failures. All 25 targeted issue/corpus tests pass.

Rebound prior issue bodies to corpus046: 29 entries identical, amended Optuna
issue body directly checked equal. Indexed results match all 435 earlier
exhaustive pair calculations (71 positive intersections). At exploratory
thresholds Jaccard1/10 or containment1/5, PennyLane5716/5831 alone is flagged:
Jaccard23/331, containment46/227. Full issues and all 46 shared shingles were
read; overlap consists of headings, markdown, no-response placeholders and
the existing-issue checklist. The defects differ: batched layer indexing versus
Exp.num_steps preservation. These thresholds are not calibrated semantic tests.
Reserved evaluation bodies remain unread; split and training remain unapproved.

Evidence: corpus046-similarity-001, including source, tests, 25-test log, inherited
issue bodies, exhaustive oracle and scoped pair review. R2 archive is 8 files /
165,371 bytes; all files are uploaded and independently restore-verified in R2
(corpus046-similarity-publish-001 / restore-001). No Runpod use.


### October 11 — Bounded CLI and 1,575-task candidate screen

Added scripts/audit_issue_similarity.py: exact input SHA256/size and bounded
immutable bytes, strict duplicate-key/nonfinite JSON rejection, rational CLI
thresholds, explicit workload limits and fresh output directory. Source selection
and authorization must precede the CLI; it does not itself grant access to held-out
material. Added a pair-visit budget to the core: sum_s choose(posting_size_s,2)
is checked before pair counting, limiting repeated boilerplate work independently
of distinct pair count. Twenty-eight targeted tests pass, including CLI rejection
of changed bytes, oversized input, duplicate keys, nonfinite JSON and zero threshold.

Exported only the existing metadata-qualified 1,575-task cohort from two already
local pinned shards. Reserved repository checks and exact metadata checks precede
issue-body access; no oracle patches read. First export stopped on hydration;
second stopped because /tmp resolved to /private/tmp and the source root had not
been canonicalized. Third explicitly resolves the allowed root and passes the
same containment and content checks. Failed logs/scripts are retained.

The cohort has 454,737 lexical tokens. Indexed screening processes 229,535
positive pairs and 967,495 posting-pair visits. Independent exhaustive integer/set
calculations agree across all 1,239,525 unordered pairs. At Jaccard>=1/2 or
containment>=4/5, all five flags were read: Mobly164/165 and Hidrokit121/122 have
exactly identical issue text and candidate leakage families; ebook-reader-dict,
EinsteinPy and Streamlink pairs describe different requirements with shared
funding or issue-template material. Linked image contents and patches are not
reviewed. No guarantee for unflagged semantic duplication or hidden evaluation.

Evidence: candidate-similarity-001, candidate-similarity-publish-001 / restore-001.
The archive preserves input issues, fingerprints, source bindings, failure logs,
production implementation, tests, oracle and scoped review. Corpus046 and all
admission gates remain unchanged. Screening 1,575 candidates is not acquiring
1,575 verified training trajectories. No Runpod use.

R2 completion: all 18 archive files (2,392,793 bytes) are uploaded and
independently restore-verified. No local source shard was downloaded or deleted.


### October 11 — Enforce reviewed duplicate families in split planning

Added merge_leakage_groups to the split module. It computes connected components
of existing family membership and reviewed task links, preserves split choices,
and rejects conflicting components. The merge is deterministic and idempotent
at manifest level, retains prior family constraints, never mutates caller input,
and refuses frozen manifests. Generated label collisions are explicitly rejected
including a forced collision between two independent components. Links remain
caller-supplied evidence; the function does not infer semantic equivalence.

31 targeted tests pass: seven merge tests plus issue-similarity/CLI and corpus
checks. Independent graph reachability across 50 seeded small graphs confirms
component membership. An intermediate new-test syntax error was corrected;
initial, failure and final logs are retained.

The candidate draft integrates the two exact-issue families after verifying
fingerprint and review identities: 1,575 task rows, 1,573 leakage groups. Task,
repository, split and issue-hash fields are unchanged. All assignments remain
provisional train; input_sha256 denotes issue bytes only in this planning artifact,
not tokenized examples. Corpus046 is unchanged and quarantined. Reserved test
bodies were not accessed. No training or GPU execution.

Evidence: candidate-leakage-plan-001; nine files / 777,521 bytes. R2 publication
and restoration use candidate-leakage-plan-publish-001 / restore-001. Fresh full
local regression004 was started after the shared split-module change; its result
remains pending until the runner terminates and the report is checked.

Full regression004 completed successfully: 486 tests, zero failures/errors/skips,
CPU Torch checks enabled. Runner elapsed time including collection: 128.87s;
unittest execution: 64.921s. No production source changed during this run.
The report binds its runner and captures test logs, not a complete before/after
repository snapshot. Evidence: p1-full-regression-004. Duplicate-family evidence
is uploaded and independently restore-verified (nine files / 777,521 bytes).

Full-regression004 archive completion: four files / 79,744 bytes are uploaded
and independently restore-verified in R2. P1 remains incomplete; GPU stays off.


### October 11 — Rally1469 explicit diagnostic derivative

Selected a held candidate with an already-local qualified runtime; no image pull
or Runpod session. The original final script inferred TLS1.3/Elasticsearch memory
leak prevention from constructor attributes. Replaced two created diagnostics via
the explicit amendment mechanism (action ordinals29/38); no source patch edit,
source action reorder or silent observation rewrite. The original validation
script and all historical evidence remain available.

The first replacement asserts seven finite constructor cases. The second creates
actual sessions/connectors across 3 option settings × 2 static modes × 2 SSL
settings, checking stored policy, connector type/policy, timer creation, session
and connector closure, timer cancellation and no pending async tasks. No request
or TLS handshake is made. It does not claim sustained memory behavior or server
compatibility. Both diagnostics fail on the base and pass the patched source;
five explicitly injected default/override/connector-policy faults reject. Exact
patch application, unchanged final diff and container cleanup are checked.

Fresh replay completes39 charged calls under40, no tool errors and unchanged
2,185-byte patch4d9f24a4a36f82ba0b0f9eff929aa56d7f763ccb9a3b08b6acfbf8ee681861f6.
History reconstruction:82 messages/40 exchanges. Pinned token audit:19,709 input,
3,513 supervised shifted targets, no truncation and4,867 reserve margin. Fresh
grading, full-content review and mechanical assessment remain pending before
corpus integration. Corpus046 is unchanged, all training gates remain open.

Diagnostic archive15files58,981bytes is R2 uploaded/restore-verified. Native
archive7files150,661bytes and history/token archive7files309,926bytes are both
uploaded and independently restore-verified in R2. No production code changed this cycle;
prior full486-test CPU result remains the latest local suite.


### October 11 — Rally1469 review and grading completion

Fresh independent grading of the amended replay matches all 197 reference case
outcomes with zero disagreements. Read the remaining messages 66–81, completing
review of all 82 messages across the continued review. Fifteen explicit sections
cover the exact history without overlaps or omissions; per-message hashes bind
the findings. Mechanical cross-artifact assessment passes with no blockers.
The final twelve-case check exercises connector policies and lifecycle only;
it does not measure network requests, TLS handshakes or sustained memory leaks.
Original teacher evidence remains separate from the two attributed amendments.

Evidence: rally1469-full-history-review-001, amended-grade-001 and
amended-admission-001 under evidence/data. The combined archive has 22 files /
386,660 bytes and is uploaded and independently restore-verified in R2
(rally1469-reviewed-grade-publish-001 / restore-001). Corpus046 remains unchanged;
next action is quarantined replacement with token recount, schedule verification
and R2 restoration. No training admission or learned-model gain is established.

No production code changed; the latest full local regression remains 486 tests
passing. Runpod remains stopped. Local disk has only about 1.5 GiB available, so
this cycle uses existing images and small evidence bundles without large pulls.


### October 11 — Corpus047 adds reviewed Rally; restore and schedule verified

Inspected corpus046 before integration: Rally was absent. Corrected earlier
replacement wording; this is a new quarantined addition. All 30 earlier records
remain byte-identical. Corpus047 has 31 examples/tasks across 30 declared
repository groups, 607,997 input tokens and 165,606 supervised shifted targets.
Manifest SHA256 a0ffe9d3702086b123403071710da5ef84cb152a2e8b5f516e5d73c2b09cfeef.
Its 63 files / 6,724,848 bytes are R2 published and independently restore-verified.
Recounting restored token arrays agrees; quarantine training loads reject.

With seed7401, one epoch and a9,216-supervised-token update cap, original and
restored schedules are byte-identical:27 updates, zero target overshoot.
Emcee295 remains the only input-plus-8,192-reserve exception. No GPU is used.
Evidence: corpus047-integration-001, corpus047-rally-schedule-001 and
training-corpus-publish-047 / restore-047.

All465 lexical pair counts agree with an independent exhaustive set oracle.
At Jaccard>=1/10 or containment>=1/5, Rally adds no flags. The identical prior
PennyLane issue pair remains the only flag; its earlier template-overlap finding
is rebound to unchanged issue bodies. Unflagged does not prove semantically
independent, and this does not establish held-out isolation or a frozen split.
Evidence: corpus047-similarity-001.

The19-file /170,603-byte integration evidence archive is R2 published and
independently restore-verified (corpus047-integration-publish-001 / restore-001).
No production code changed, so the prior486-test full local regression remains
the latest relevant suite. README and current readiness now reflect corpus047.
Next: expand qualified diverse data and close rights/attribution and split gates;
this165,606-target corpus is not sufficient for three50M-token candidates without
roughly302 repeats per candidate. Keep Runpod stopped; no training is admitted.


### October 11 — Reusable bounded source attribution capture

Implemented zenithsync/source_capture.py for explicit tracked regular Git blobs.
It checks qualified commit/tree identities, reported tracked cleanliness before
and after capture, literal paths and blob types, per-file/aggregate sizes before
reading content, and each Git object hash. Success reports are written last.
The API does not infer a license, read evaluation task bodies or approve training.
Seven new temporary-Git tests plus seven review-coverage tests pass. The initial
fixture expected31 bytes instead of32; its failed log is retained, followed by
the corrected passing run.

An actual offline capture on Rally exports seven files /88,905 bytes, including
LICENSE and NOTICE. All eight direct read observations match the captured base
blobs after applying the two recorded source edits in chronological order.
No source excerpt is silently rewritten. NOTICE preserves Elasticsearch B.V.'s
copyright; a supplement records the project's replay and diagnostic changes.
Indirect shell content, dependency notices and dataset/teacher requirements
remain separate. This is source provenance, not exhaustive rights approval.

Attribution archive:23 files /189,253 bytes, R2 published and independently
restore-verified. Evidence: rally1469-attribution-001 and its publish/restore-001
receipts. Corpus047 is unchanged and quarantined. Full local regression005 was
started with CPU Torch checks enabled; its result will be recorded separately.
Runpod remains stopped.


Full regression005 completed:493 tests passed, zero failures/errors/skips, CPU
Torch enabled. Collection plus execution took250.02s; test execution44.536s.
No production code changed during the run. The four-file /80,736-byte test
evidence archive is uploaded and independently restore-verified in R2; see
p1-full-regression-005, p1-full-regression-publish-005 and restore-005. This
supersedes the486-test local baseline. Full-model GPU qualification remains open.


### October 11 — Corpus047 repository identity and draft split refresh

Queried fresh public GitHub repository metadata for all30 candidate repositories
and four reserved evaluation repositories. All34 resolved, with no declared-name
or fork-network-root overlap. The33 previously observed repository identities
are unchanged; Rally adds network root47140131. Reserved issue bodies and patches
were not opened. This excludes observed canonical/declared-fork overlap only;
detached copies, vendored source and semantic overlap remain outside this check.

Bound all31 current examples to canonical network groups and their exact audited
input-token hashes. The draft validates without changing task, leakage-family or
provisional split assignments. All entries are still provisional train; there is
no new development/confirmation cohort, frozen split or training admission.
Evidence: corpus047-split-001.

The first binding attempt passed a string to the Path-only JSON loader and failed
before emitting the split result. The subsequent transfer found no bundle and
wrote no passing receipt. Corrected the path type and reran successfully; the
successful publication is corpus047-split-publish-002. Production code is
unchanged, so the493-test full local result remains current. Runpod stays stopped.

The39-file /253,263-byte lineage/split bundle is independently restore-verified
in R2 (corpus047-split-publish-002 / restore-001). The restored draft was also
revalidated against the current corpus identity; all31 entries remain draft.


### October 11 — Linkding691 diagnostic derivative, fresh replay pending

Revisited the held Linkding candidate using its already-local qualified snapshot.
Its original passing publisher/argv checks do not justify the two unsupported
assistant test claims. Built an explicit amendment plan for source indices28/44
(two of27 shell actions); terminal, source edits and all other commands remain
unchanged. Original teacher history is preserved separately. The first attempt
stopped during cloud hydration metadata drift; retry retained the pinned source
hash and unchanged strict identity checks.

The requirements diagnostic asserts exact mocked argv, gzip bytes, missing-file
SingeFileError, propagation of the same OSError and translation of an explicitly
injected CalledProcessError. The use-case diagnostic runs a real local child
and checks its exact argv through compressed output. Neither claims that a
browser or external website works. Both programs reject the actual base and
pass the actual patched checkout. Three explicit process-local faults reject:
dropped options in each program, and swallowed exceptions in the first. Source
origin, snapshot/tree identity, unchanged diff and container cleanup are checked.
The original source patch's trailing-whitespace warning is retained.

Evidence: linkding691-amendments-001 and linkding691-diagnostics-001. Fresh
amended native replay, independent grading, token rendering, full-content review
and mechanical assessment remain necessary before quarantine integration.
Corpus047 is unchanged. No production code changed;493-test local baseline
remains current. No image pull or GPU usage.

Linkding diagnostic archive31 files /82,864 bytes is uploaded and independently
restore-verified in R2: linkding691-diagnostic-publish-001 / restore-001.


### October 11 — Linkding691 fresh derivative fully reviewed

Fresh replay completed27 charged calls and native submission, with the original
1,025-byte source patch unchanged (434cb0f506d81378184e83fc57e0fd3861183ea434a183c1d26b6aef777beb21).
Container cleanup succeeds without errors. Independent paired grading reproduces
all six publisher transitions:base5/6, reference6/6, candidate6/6.
Reconstructed native history has58 messages /28 exchanges,17,612 input tokens
and7,571 supervised shifted targets. No truncation;6,964 tokens remain after
the8,192 output reserve. Mechanical assessment passes with no blockers.

Read all58 messages in three bounded groups and bind findings in11 complete
nonoverlapping sections. No-match errors at messages11/37 remain visible. The
original three-case and four-case mock diagnostics remain finite checks; later
attributed diagnostics assert exception outcomes and actual child argv/gzip
behavior without website claims. Existing service tests pass4; snapshot-related
task tests pass27 with15 deselected. These scopes are not conflated with the
independent six-case publisher grade or an entire-repository test pass.

Cloud hydration changed metadata during the first replay preflight, before
execution. Copied hash-checked inputs to local temporary storage and reverified
the existing snapshot. An old staged replay script lacked amendment support,
so staged current source. A missing protocol fixture in the old staging root
was copied from the repository. CLI assessment correctly rejected sibling
evidence directories; the public assessor was then given their explicit common
/private/tmp workspace without changing receipts or weakening identity checks.

Evidence: linkding691-amended-native-002, amended-grade-001, amended-history-001,
amended-tokens-001, amended-admission-002 and full-history-review-001. Original
teacher evidence is preserved. Quarantine integration remains pending; corpus047
is unchanged. No production code changed;493-test local baseline remains current.
No image download, GPU execution or training approval.

The complete amended Linkding bundle (259 files /1,598,228 bytes) is R2 uploaded
and independently restore-verified: linkding691-amended-publish-001 / restore-001.
Next action is quarantined-corpus addition with recount and restored scheduling,
followed by attribution and updated isolation checks.


### October 11 — Corpus048 Linkding integration and isolation update

Added the fully reviewed Linkding derivative to quarantine. All31 prior records
are unchanged. Corpus048 has32 examples/tasks across31 declared repository
groups:625,609 input tokens and173,177 supervised shifted targets. Its65 files /
6,921,324 bytes are published and independently restore-verified in R2.
Manifest SHA256:36f25103da05d8791d23b5c4fc48853766dc6831d0df17c27639e2a152b796e5.

Restored token-array recount agrees. With seed7401, one epoch and9,216-target
update cap, original/restored schedules are byte-identical:28 updates, zero
target overshoot. Quarantine training loads still reject. Emcee295 is the only
input-plus8,192-reserve exception. Evidence: corpus048-integration-001 and
corpus048-linkding-schedule-001, training-corpus-publish-048 / restore-048.

All496 lexical pair counts match an independent exhaustive set oracle; Linkding
adds no Jaccard>=1/10 or containment>=1/5 flags. The sole prior PennyLane template
flag remains unchanged. The first audit stopped on source-file hydration
metadata drift; retry uses the same hash-bound staged implementation and keeps
all integrity checks. Successful evidence: corpus048-similarity-002.

Fresh public Linkding metadata resolves repository/network ID194212327. Reused
34 earlier hash-bound observations with their original retrieval timestamp.
There is no known declared fork-network overlap with the four reserved repos;
no evaluation bodies were read. All32 current token identities validate in the
draft;31 previous assignments are unchanged. All remain provisional train,
without a development/confirmation cohort or frozen split. Detached copies and
semantic leakage remain outside these checks. Evidence: corpus048-split-001.

The58-file /432,269-byte integration/isolation archive is independently
restore-verified: corpus048-integration-publish-001 / restore-001. README and
readiness reflect corpus048. No production code changed;493-test local baseline
remains current. Runpod stays stopped and no training is approved.

A50M-token candidate would require approximately288.72 corpus-equivalent passes
on this small corpus. Further diverse qualified supply and rights/attribution
work remain required; repetition is not a substitute for data coverage.


### Linkding selected shell attribution — 2026-10-11

`evidence/data/linkding691-attribution-001/report.json` binds the exact corpus048
Linkding history and token audit to nine preserved committed source blobs
(91,188 bytes). Three complete `cat` observations and two context `grep`
observations match exactly; the post-edit source observation is reconstructed
from the recorded message-14 heredoc without executing that command. The
original MIT `LICENSE.txt` is preserved unchanged. The attribution bundle has
22 files / 173,979 bytes and is independently R2 restore-verified by
`linkding691-attribution-publish-001` and `linkding691-attribution-restore-001`.

This closes only selected source-observation checks. Recursive grep output,
scratch programs, diffs, dependencies, dataset/teacher attribution and complete
redistribution review remain open. The local source receipt identifies
`nvidia/Open-SWE-Traces` revision
`e192b26a43b8d09f156eeee781aef8e6bd5108ba`; its preserved card declares
CC BY 4.0. This is a pinned local declaration, not a fresh publisher check or
blanket source/teacher rights clearance. Do not substitute SWE-Hero provenance
for this example. Corpus048 remains quarantined; no admission gate changed.

No production code changed in this step. Five exact observation comparisons,
all nine source identities, corpus/history/token-audit bindings and the R2
restore were checked. The existing 493-test CPU result remains the latest full
regression, not a newly executed suite. Runpod was not used. Local disk has
approximately 1.4 GiB free; avoid large downloads until scoped cleanup is
verified against archives and current consumers.


### Scoped local cache cleanup — 2026-10-11

Completed `evidence/data/scoped-cache-cleanup-001`: removed 441,586,142 logical
bytes from three explicitly inspected generated `.pyc` cache trees and one
redundant SWE-Hero shard. The removed
`/tmp/zenithsync-lmfit487-source-cache-001/train-00010-of-00014.parquet`
is byte-identical to retained
`/tmp/zenithsync-optuna3545-r2-source-001/source.parquet`
(SHA256 `bf5e920077bf721832ab9fc34d1ea9275ed4cb8b5a2355bff2b6b2f598c199de`,
245,825,405 bytes); retained content was checked again after deletion.
Historical runners needing the old location must restore a copy from that
retained file and verify the hash. No symlinks or shared writable aliases were
introduced. The retained shard has its prior verified R2 recovery receipt.

Filesystem free bytes increased from 1,475,829,760 to 1,932,759,040 at the
cleanup measurement; these are transient whole-filesystem readings, not an
exact attribution of all concurrent disk changes. Source code, model, virtual
environments, unique evidence and shared Docker resources were preserved.
The five-file cleanup evidence archive (3,204,182 bytes) was R2 published and
restore-verified: `scoped-cache-cleanup-publish-001` /
`scoped-cache-cleanup-restore-001`. This is storage maintenance, not additional
model validation or a changed training-admission decision. Runpod was unused.
Disk headroom remains limited; continue bounded work and verify ownership and
recoverability before removing larger resources.


### Linkding exact dataset lineage — 2026-10-11

`evidence/data/linkding691-dataset-lineage-001/report.json` reselects exactly
one trajectory from the hash-verified Open-SWE shard and reproduces the
pre-replay candidate messages, response links, terminal status, tool schema and
source metadata. Only five source columns were selected; reference-patch
metadata was not loaded. The pinned dataset README was freshly downloaded at
revision `e192b26a43b8d09f156eeee781aef8e6bd5108ba` and matches the intake
SHA256 exactly. The archive includes NVIDIA attribution, its citation, CC BY
4.0 declaration/link and a description of downstream modifications.

The shard path and pinned card identify Qwen3.6-27B. A fresh model metadata
lookup resolved revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`; its
LICENSE was preserved at that immutable revision and identifies Apache 2.0.
This is the currently observed model revision, not proof of the original
generation revision or original generation-service terms. The archive does not
replace the separate Linkding source-notice supplement or establish full rights
clearance. Corpus048 and its null admission gates remain unchanged.

The 12-file / 206,911-byte bundle is R2 published and independently
restore-verified (`linkding691-dataset-lineage-publish-001` / `restore-001`).
No production code changed; exact data/conversion and remote-content identity
checks ran, not a new full regression. Runpod remained unused. Next provenance
work must close uncovered source/dependency observations and assess coverage
across the remaining corpus, alongside held-out split and privacy gates.


### Final-input credential indicator screening — 2026-10-11

Added `zenithsync/corpus_credentials.py` and
`scripts/screen_corpus_credentials.py`. The CLI binds the tokenizer bytes to
the corpus assets and uses IndexedCorpus inspection to screen every split.
Complete decoded inputs include masked prompts/tool observations as well as
assistant targets. Special tokens are retained; unknown token IDs fail instead
of being silently dropped. Reports contain only rule names and character/line
locations, never matched values. Inputs exceeding the character ceiling fail
without truncation. Corpus files and training admission remain unchanged.

Corpus048 screen003 covers 32 examples, 625,609 input tokens and 2,080,927
decoded characters: zero indicators in the four existing rule families
(private-key headers, AWS access IDs, GitHub tokens and authorization literals).
This is not a general PII, entropy, obfuscation or privacy clearance. All 26
targeted corpus/credential tests pass, including five new scanner tests.
The previous 493-test full regression predates this new module; it is not a
full-suite result for this change.

Attempt002 stopped on macOS cloud-hydration metadata drift during source
hashing; its failure log is preserved. Screen003 used a stable temporary source
runtime with strict identity checks unchanged. Eleven evidence files / 52,807
bytes are R2 published and independently restore-verified under
`corpus048-credentials-publish-003` / `corpus048-credentials-restore-003`.
Source and tests are in `evidence/data/corpus048-credentials-003`.

Repeat this screen for each new corpus identity; do not reuse this result for
changed token arrays. Broader privacy review, rights, held-out splits and GPU
qualification remain open. Runpod was unused.


### Full CPU regression after corpus credential screening — 2026-10-11

`evidence/data/p1-full-regression-008/report.json` reports 498 tests passed,
zero failures, zero errors and zero skips; CPU Torch checks were enabled.
Execution took 21.420 seconds (21.553 seconds including collection and source
checks) in the stable temporary snapshot. All 294 Python source files from
the initial repository run match exactly. The final 297 bound inputs include
the observation helper, serving configuration and official repository metadata
fixture, checked unchanged before and after execution.

Attempt006 ran 498 tests in the cloud-managed workspace and failed with five
errors and one failure, all traced to strict file_record rejection of metadata
changes during hydration. Attempt007 used the same source bytes but omitted
two fixture files, so its 494 collected entries were not acceptance. Adding
the unchanged fixtures restored complete 498-test discovery for attempt008.
No integrity check was relaxed, no test was removed and no production fix was
needed for these environment failures. All failed logs/reports are retained.

The exact source snapshot, successful and failed reports, runners and comparison
record form a 315-file / 1,800,701-byte archive, published and independently
restore-verified in R2: `p1-full-regression-publish-008` and
`p1-full-regression-restore-008`. This supersedes the 493-test005 result for
current local regression. It does not establish full 31B GPU memory, throughput,
training stability, corpus rights/admission or learned task performance.
P1 remains incomplete and Runpod stayed unused.


### Complete checkpoint descriptor correspondence — 2026-10-11

Added `zenithsync/architecture_layout.py` and
`scripts/verify_architecture_layout.py`. The verifier binds config bytes to the
existing model manifest, constructs Gemma4 with pinned Transformers 5.13.1 on
meta tensors, requires every state tensor to remain meta, and accounts for the
exact checkpoint descriptor set. Independent existing W4/group-32 projection
formulas agree with the meta constructor for all 410 projections; stored
original dimensions, packed shapes and scale shapes match. All 779 remaining
embedding/norm/vision tensors have exact expected names/shapes and BF16 dtype.
There are 2,009 stored descriptors corresponding to 1,189 logical tensors.

Evidence: `evidence/p1/architecture-layout-001/report.json`. The current header
SHA256 matches the earlier storage receipt; its bytes and expected shapes are
archived. This run inspects structural metadata and stored dimension integers,
not a fresh full-weight hash or numerical weight scan. Constructor agreement
is an implementation comparison, not independent proof of architecture
semantics, inference accuracy, dequantization or training compatibility.

Eight targeted tests pass. The malformed-extra-descriptor test initially
exposed an unhelpful KeyError; explicit descriptor validation now rejects it
with ValueError. The failed log is preserved. Full stable-snapshot regression009
passes 502 tests with zero failures/errors/skips and CPU Torch enabled; elapsed
time including collection/source checks was 21.193 seconds. This supersedes
regression008 for the current implementation.

The complete 322-file / 1,928,960-byte source and evidence archive was published
and independently restore-verified in R2 (`architecture-layout-publish-001` /
`architecture-layout-restore-001`). The P1 architecture checklist row is updated
within this structural scope. Full corpus admission, data expansion, evaluation
splits, long-context GPU training/resume and measured coding gains remain open.
Runpod was not used.


### Open-SWE mini-agent expansion shard000 — 2026-10-11

Acquired pinned `nvidia/Open-SWE-Traces` revision
`e192b26a43b8d09f156eeee781aef8e6bd5108ba`, shard
`data/minisweagent/qwen36_27b/swe-rebench-v2/train-00000-of-00022.parquet`,
with a 105,000,000-byte cap and preflight free-space check. Publisher LFS
SHA256/size verified. Its source/card/publisher metadata bundle contains three
files / 98,620,316 bytes and is R2 published and independently restore-verified.
The temporary restored duplicate was removed after both local copies were
reverified; the original remains under `/tmp/zenithsync-open-swe-mini-shard000-001`
and is recoverable from R2. This prevents retaining two large local copies.

Metadata census found 2,500 unique tasks across 1,186 repositories. Four rows
from reserved official repository names were excluded before reading messages.
All remaining 2,496 tasks are absent from the earlier 1,575-task source-cost
screen; 1,135 repository names are new relative to its 902 repositories. This
is exact spelling/casefold comparison, not semantic or fork-family clearance.
Eligible publisher labels: 803 success, 1,454 failure, 239 unknown. Those labels
are not independent repair verification or an estimate of agent performance.

Batch-size-eight content screening covered exactly all 2,496 eligible rows:
2,488 serialized successfully, eight were held for credential-indicator review
without printing matched values. There are 516 traces within 40 source calls;
226 of those have publisher success labels and span 180 repositories. Source
call counts include the unanswered terminal call; they do not establish native
charged-call budget, context fit or supervised-token supply. No commands were
executed and no reference-metadata column was loaded. Independent record
recount matches all totals. The reference solution may still occur in untrusted
source-message content; this screen is not semantic leakage clearance.

Evidence: `mini-shard000-census-001`, `mini-shard000-screen-001`, and the
20-file / 1,709,224-byte `mini-shard000-expansion-001` archive. Source and
expansion publish/restore receipts are verified. No new corpus records were
admitted or added to corpus048, and no production code changed; the 502-test
regression remains the latest full suite. Runpod was unused.

Next: select a repository-diverse bounded review queue from the 226 candidates,
retain the other outcomes and indicator holds, then establish task alignment,
source attribution, isolated runtime, native replay, grading and token fit.
The increased raw supply does not replace these gates or justify a 50M-token
training campaign yet.


### Diverse mini-agent qualification queue — 2026-10-11

`qualification_sampling.stratified_repository_batch` now accepts an explicit
`source_call_proxy` cost field while retaining its historical source-token
default. Call counts are never relabelled as tokens. Source-cost checks reject
unsupported fields and nonpositive/noninteger values. Four targeted sampling
tests pass; full stable-source regression010 passes 503 tests with zero
failures/errors/skips (22.613 seconds including collection and source checks).

From shard000's 226 publisher-success/short-call candidates, excluding current
corpus names, official reserved names, explicit holds and four previous review
batches leaves 175 repository names. A seeded (7401) four-stratum queue selects
16 repositories, four per rank stratum, after taking one minimum-call trace per
repository. Independent grouping/ranking reconstruction matches exactly.
Evidence: `mini-shard000-batch-001`. This is purposive review selection, not a
random agent-performance sample; source call counts are not native tool budgets.

Fresh GitHub observations for all 16 selected names, compared with 35 inherited
corpus/reserved observations, identify `peopledoc/workalendar` as already
represented. Its trace is held from this diversity queue, not rejected as an
inherently invalid task. The final working queue has 15 distinct observed
repository/fork-root IDs, with no match to the inherited corpus/reserved roots.
Post-hold strata contain 3/4/4/4 records. Previous review queues were excluded
by names only; detached copies, historical aliases outside the captured set
and semantic duplication remain unresolved. No source repair was executed.
Evidence: `mini-batch-lineage-001` and `mini-shard000-review-queue-001`.

The 370-file / 1,928,186-byte queue, inherited/fresh lineage, exact tested source
and full-regression evidence archive is R2 published and restore-verified
(`mini-queue-publish-001` / `mini-queue-restore-001`). README and current
readiness now identify regression010 as latest. Corpus048 remains unchanged
and quarantined. Next work is task-content and source-contract review of this
queue before any runtime downloads, with local disk capacity checked first.
Runpod stayed unused.


### Ember8613 source review and diagnostic counterexamples — 2026-10-11

Reviewed all 31 source messages for the selected `ember-cli__ember-cli-8613`
trace, bound to the exact shard000 row and 15-candidate queue. The source patch
changes `@ember/jquery` from `^0.5.2` to `^0.6.0` in both blueprint package
files, consistent with the issue. Source observations support the declarations,
not an actual Ember transpilation/deprecation regression test. The unanswered
last source submission remains explicitly unexecuted evidence.

The message24 verification script has two reproduced weaknesses on five
isolated synthetic fixtures: mismatches/missing files print failure but return
zero, and unescaped regex dots falsely accept `^0x6y0`. These were executions
of the inspected diagnostic body on synthetic files only, not task replay.
A separately labeled project-authored JSON diagnostic checks the exact
devDependencies values, rejects duplicate members and exits nonzero on failure.
Seven synthetic cases give the expected outcomes; the original app blueprint
observation also parses as JSON. The original trace is preserved, not silently
rewritten. Decision: hold for explicit amended native qualification.

An explicit nested Arrow projection of `metadata.teacher_model` identifies
Qwen3.6-27B with `enable_thinking=false` and `reasoning_effort=null` for this row.
Sibling reference-patch metadata was not read. This is stronger row-level
teacher-name evidence than the dataset path alone, but does not establish
the exact model generation revision or service terms.

Evidence: `ember8613-source-review-001`. Its twelve files / 45,238 bytes were
R2 published and independently restore-verified (`ember8613-review-publish-001`
/ `ember8613-review-restore-001`). No production library changed; the latest
full regression remains 503 tests. No candidate was added to corpus048.
Required next steps: independent base/environment binding, applicable notices,
explicit amended replay, grader comparison and native token/context audit.
No new runtime image was downloaded and Runpod stayed unused.


### Independent task joins and Ember pinned-source controls — 2026-10-11

All 15 working-queue candidates match independent SWE-rebench-V2 task IDs and
casefold repository names at pinned dataset revision
`10483de0f50fe5da545942705a76c6150171af7f`. The projection reads only repository,
instance ID, base commit, image tag, language and license; no reference or test
patch column. Evidence: `mini-queue-task-join-002`. Attempt001 stopped on
cloud-hydration receipt metadata drift; attempt002 used byte-verified staged
receipt data with integrity checks unchanged. The 428,839,266-byte temporary
shard duplicate was deleted only after both it and the retained original matched
the pinned SHA256. No sole data copy was removed.

Ember8613 is bound to base `e40d3dd4f51635b37fba4ef11023ea60b1ebdfef`.
Exact-revision GitHub API exports preserve the two blueprint files and MIT
license (3 files / 4,142 bytes); decoded content matches Git blob hashes.
The app-file observation equals the pinned blob. Applying the recorded source
patch passes git apply --check, then the exact-version diagnostic; baseline
fails that diagnostic. Both files differ by exactly one requested dependency
string replacement each, with all other bytes unchanged. This is declaration
validation, not blueprint rendering, deprecation behavior or publisher grading.
Evidence: `ember8613-source-export-001`, `ember8613-source-controls-001`.

The publisher image manifest reports 1,190,545,013 compressed layer bytes,
before extraction and workspace overhead. Only metadata was fetched; no image
was downloaded given current disk constraints. Its tag is not yet a qualified
immutable runtime. Explicit amended native replay and independent grading remain
open; no example was added to corpus048.

The 29-file / 60,428-byte joined-metadata/source/control archive is R2 published
and restore-verified (`mini-task-ember-controls-publish-001` / `restore-001`).
No production code changed; latest full regression remains 503 passing tests.
Continue other bounded source reviews and improve local storage headroom before
image acquisition. Runpod stayed unused.


### Scoped Docker build-cache audit — 2026-10-11

Inspected BuildKit records and selected 44 unused, immutable, unshared regular
cache IDs matching this project's snapshot/ZenithSync build commands. Used an
anchored ID filter and regular-cache restriction; no global Docker prune.
Docker removed two selected records and reported 7.979 MB reclaimed. The
remaining 42 selected records remained; do not report their approximately
269 MB aggregate advertised size as freed. No unselected cache ID disappeared.
Before/after hashed image/tag, container identity/image and volume inventories
match exactly. Host free bytes did not materially improve (1,743,237,120 before,
1,742,450,688 immediately after); VM reclamation and concurrent disk activity
prevent treating reported cache bytes as observed host free space.

Three larger unused unshared cache entries (approximately 12.289 GB advertised)
appear outside this project. Their exact IDs and descriptions are preserved in
`project-build-cache-cleanup-001/outside-project-proposal.json`. User approval
was requested because this exceeds the project cleanup scope; no response or
authorization is assumed. Do not clear those entries until authorization arrives.
Images, containers and volumes are excluded from the proposal. Docker's
ID-filter semantics were checked against its official buildx prune reference.

The five-file / 26,883-byte audit archive is R2 published and restore-verified
(`project-cache-cleanup-publish-001` / `project-cache-cleanup-restore-001`).
No production change or new model test; latest full regression remains 503.
Large runtime downloads remain deferred, but bounded source/content work can
continue. Runpod stayed unused and P1 remains incomplete.


### More Itertools892 review checkpoint — 2026-10-11

P1 remains incomplete. Four source-authored diagnostics were shown to return
success with an implementation that ignores strict length checking. An
independent 79-check finite diagnostic passes a positive fixture and rejects
three faulty variants; 20 subprocess controls were recorded. This is diagnostic
qualification, not a native repair replay or evidence of learned capability.
The exact pinned source row and counterexamples are preserved in
`evidence/data/moreitertools892-diagnostic-review-001`; 13 files / 111,230 bytes
were R2 published and independently restore-verified by
`moreitertools892-diagnostic-publish-001` / `moreitertools892-diagnostic-restore-001`.

Next for this candidate: bind pinned source and license, explicitly amend weak
diagnostics and unsupported claims, then perform native replay, independent
grading and token/context review. Do not silently rewrite the original teacher
trace or admit it based on publisher success. Corpus048 remains unchanged;
latest full production regression remains the prior 503-test run. Runpod is off.


### More Itertools892 pinned-source controls — 2026-10-11

Fetched five selected source/test/license files at independent task base
`1ae91eb4ff6ee9c326bc1ceb52e2d6edbdb0c3a8`, verified API content sizes and Git
blob hashes, and retained MIT copyright 2012 Erik Rose. Applied the original
observed patch unchanged using `git apply --check` and `git apply` on a copy.
Executed only inspected AST-selected definitions with explicit standard-library
bindings; no arbitrary module initialization or source shell actions executed.

The five existing SortTogetherTest methods pass on both base and patch. The
base rejects the strict keyword with TypeError; the patch raises the requested
UnequalIterablesError on unequal nonempty-column collections. Independent
row-index sorting agrees on 12,800 finite cases: both columns range over all
sequences of length 0–3 on {-1,0,1}, with both strictness settings, sort orders,
and single-column key priorities. The separately authored 79 contract checks
also pass on the actual selected patched function, including iterator inputs.
These cases are finite and correlated; they are not independent statistical
samples, a confidence bound, full-module execution or native publisher grading.

Observed unresolved boundary: zero outer columns return [] with strict=False
but raise IndexError with strict=True, inherited from _zip_equal indexing its
first iterable. Do not silently fix the teacher patch or claim universal
correctness. Resolve intended zero-column semantics and explicitly amend weak
diagnostics and overbroad claims before native qualification. All rights,
full-history, context, grading and admission gates remain open; corpus048 is
unchanged. Runpod remains off. Evidence: moreitertools892-source-controls-001.

The 26-file / 1,331,901-byte selected-source/control archive is R2 published
and independently restore-verified (`moreitertools892-source-publish-001` /
`moreitertools892-source-restore-001`). No production code changed; the prior
503-test production regression remains the latest such run.


### More Itertools892 whole-module container controls — 2026-10-11

Used an already-local immutable Python image
`sha256:ae52c5bef62a6bdd42cd1e8dffef86b9cd284bde9427da79839de7a4b983e7ca`
(ARM64 Python 3.11.15), without downloading an image or using Runpod. Base and
unchanged candidate patch each pass all 640 cases collected from the complete
pinned `tests/test_more.py` and its doctest loader: zero failures, errors or
skips. These are unittest cases, including doctest cases, not 640 distinct
repair tasks. The patched whole module also passes the 79 independent finite
contract checks. This improves on the earlier AST-selected function controls.

Each execution used network=none, read-only root and input mount, non-root user,
no capabilities, no-new-privileges, bounded memory/CPU/PIDs and a bounded tmpfs.
Input manifests remained identical after execution; both named containers were
removed successfully. Only the selected source/test files were mounted. No
credentials or host Docker socket were exposed to the containers.

Evidence: `evidence/data/moreitertools892-container-controls-001`. This is a
local alternate-runtime control, not the publisher task image, full repository
suite, complete source-action replay or independent publisher grader. The
zero-outer-column strict IndexError remains unresolved; original weak teacher
diagnostics and overbroad claims still require explicit amendments. No training
admission or corpus addition occurred. The production framework was unchanged,
so its latest full regression remains the prior 503-test run. P1 is incomplete.

The 23-file / 787,550-byte container-control archive is R2 published and
independently restore-verified (`moreitertools892-container-publish-001` /
`moreitertools892-container-restore-001`).


### More Itertools892 explicit diagnostic amendments — 2026-10-11

Prepared a hash-bound assistant-authored amendment plan for source message
indices 18, 38, 52, 54 and 64. The existing converter normalizes publisher rows
before the existing mini amendment validator derives commands. There are still
33 source actions: five amended diagnostics and 28 byte-identical actions,
including the patch-producing actions and terminal. Original source history is
preserved. No source observations or teacher reasoning are fabricated/reused.
The existing native-history projection excludes teacher reasoning and final
narratives; amended diagnostic output avoids unsupported universal claims.

The baseline diagnostic now distinguishes absence of the strict keyword from a
missing required exception after implementation. Three later diagnostic bodies
use the independent finite contract checker, and the doctest action now exits
nonzero when examples fail. Every amended body checks the imported package is
from the working source tree. Fourteen bounded, network-isolated executions on
the existing ARM64 Python image matched expected outcomes: all five bodies pass
on patched source; baseline and doctest controls pass on base while the three
new-feature checks fail; all four behavioral checks reject an ignore-strict
mutant with the intended assertion. Container cleanup succeeded for every run.

Evidence: `evidence/data/moreitertools892-amendment-001`. Only extracted Python
bodies were executed in these controls; this is not complete shell-action replay
or publisher grading. Fresh replay remains required. The zero-outer-column
strict IndexError remains an unresolved boundary; no patch correction was made.
The source patch, corpus048 and production code remain unchanged. P1 remains
incomplete, training admission is false, and Runpod remains unused.

The 16-file / 145,393-byte amendment/control archive is R2 published and
independently restore-verified (`moreitertools892-amendment-publish-001` /
`moreitertools892-amendment-restore-001`).


### Corpus048 staged-worker integration — 2026-10-11

Refreshed the explicit 39-file training source bundle (212,876 bytes). All seven
CLI entrypoints pass isolated help/import checks. Initial staging failed closed
on cloud hydration metadata drift in p1-training-pilot.json; reading the explicit
source list and rerunning the unchanged preparer into fresh paths succeeded.
No identity guards were relaxed.

Using only the staged transfer CLI from outside the repository, restored and
verified all 65 corpus048 files / 6,921,324 bytes from R2. Staged inspection passes,
and the seed7401, 173,177-target, one-epoch, 9,216-target/update schedule and
update stream are byte-identical to the previous corpus048 schedule. Both the
staged training-purpose inspector and actual corpus worker reject quarantine;
neither creates its success/output directory. The worker rejects in CPU
preflight before touching an explicitly nonexistent model path or loading CUDA.
This is a negative admission control, not a positive admitted-training test.

Evidence: training-deployment-corpus048-002, training-deployment-corpus048-restore-001,
and training-deployment-corpus048-validation-001. Deployment bindings distinguish
the R2 transfer manifest from corpus manifest and bind worker sources, model
manifest, qualification config and inspection schedule. The config remains a
bounded qualification config; it does not replace the planned three 50M-target
candidates. The current small quarantined corpus is still insufficient for that
campaign. Admission, rights, held-out split, pinned Linux/GPU and full-model
long-context/resume qualification remain open. No production change or training;
Runpod remains off and P1 incomplete.

The 67-file / 273,164-byte worker/integration/binding archive is R2 published
and independently restore-verified (`training-deployment-corpus048-publish-001`
/ `training-deployment-corpus048-archive-restore-001`). The corpus objects were
verified separately through the staged client; credentials and model weights
are not included in this source/evidence archive.


### Worker-enforced complete architecture gate — 2026-10-11

The full corpus worker now requires the CPU-only architecture CLI before GPU
weight allocation. A nonzero exit or 120-second timeout aborts the worker;
returned report status, model manifest identity, GPU-free flag and all four
complete-layout counts are verified and the report identity is recorded in
worker output. The child has CUDA hidden without changing the parent's CUDA
visibility. The CLI and its architecture/storage modules are included in worker
source identity binding and the explicit deployment bundle.

The refreshed 42-file bundle passes eight isolated CLI imports. The actual
staged worker helper passes against the local checkpoint: 410 quantized
projections, 779 unquantized tensors, 2,009 stored descriptors and 1,189 logical
state tensors. This reads metadata and stored shape integers only; it does not
verify numerical values, fresh whole-weight hashes or model quality. The worker
still performs its separate full model-manifest verification before this gate.
This local execution uses the available CPU runtime, not pinned Linux CUDA.

Eleven targeted tests pass. The complete local regression (Torch enabled) passes
506 tests with zero errors, failures or skips and stable identities for 301
source/fixture files. Tests cover subprocess failure/timeout despite stale
success reports, wrong model identities, bad counts and status rejection.
Evidence: p1-full-regression-011, worker-architecture-actual-001 and
training-deployment-architecture-check-002. First deployment staging from the
reduced regression tree lacked a config fixture; staging the complete explicit
source list in a separate directory resolved it without changing guards.

P1 remains incomplete. No corpus admission or learned-model improvement; full
GPU long-context, dequantization, training and resume qualification remain open.
Runpod was not used. Corpus048 remains quarantined.

The 361-file / 1,856,799-byte source, deployment and validation archive is R2
published and independently restore-verified (`worker-architecture-publish-001`
/ `worker-architecture-restore-001`).


### Holidays2052 pinned-source review — 2026-10-11

Reviewed the next 20-call source candidate, vacanza__holidays-2052, from the
publisher-hash-verified Open-SWE shard. Berlin's official portal corroborates
the one-time May8,2025 Berlin holiday (published September26,2024; updated
April9,2025): https://www.berlin.de/aktuelles/9188766-958090-einmaliger-feiertag-am-8-mai-2025.html.
This fact check does not qualify runtime holiday calculations or translations.

Captured three pinned source/test/license files (27,206 bytes), verified their
Git blob hashes, and applied the unchanged observed patch. Static controls prove
exactly seven inserted lines adding the 2025 tuple to Berlin's special holiday
table; removing it restores both complete file bytes and complete module AST.
Three complete source observations match exact pinned source slices. The full
file-read observation at message7 is publisher-elided: its retained head/tail
and omitted-character count match, but no missing teacher output was invented.
Initial control attempt001 failed on that envelope assumption; attempt002
explicitly validates only the available partial observation.

Native execution and grading remain pending. The source trace contains a failed
translation test; substituting alias-instantiation checks does not establish
translation support. The final diagnostic checks seven excluded years, not all
years. Original failures remain visible. MIT LICENSE is retained; its referenced
AUTHORS file and broader dataset/teacher rights still need binding. Evidence:
holidays2052-source-review-001. No training admission or corpus addition;
production code unchanged, latest regression remains 506 tests. Runpod unused.

The 21-file / 172,199-byte source-review archive is R2 published and
independently restore-verified (`holidays2052-review-publish-001` /
`holidays2052-review-restore-001`).


### Holidays2052 runtime checkpoint — 2026-10-11

Pinned source now has 661 verified Git blobs and retained LICENSE/AUTHORS.
In a cached alternate Python3.10 runtime, compiled catalogs plus explicit German
locale produce31upstreampasses for base and patch; three source diagnostics
reject base and accept patch. Prior missing-catalog and ambient-locale failures
are retained. New-label foreign translations remain absent. See journal40 and
`evidence/data/holidays2052-runtime-controls-001`. Next: explicit environment
provenance, native replay, grading and token review; no training admission.

The 79-file / 4,481,441-byte source/catalog/runtime archive is R2 published
and independently restore-verified (`holidays2052-runtime-publish-001` /
`holidays2052-runtime-restore-001`).


### Holidays2052 replay source prerequisite — 2026-10-11

Complete pinned base acquired and verified:1,334files /38,191,295bytes match
independent Git tree metadata, and the compressed archive matches all file
contents/modes. Raw base commit identity is independently recomputed. Evidence:
`holidays2052-full-base-binding-002`. Sanitized snapshot/runtime construction and
fresh native replay remain pending; no training admission or Runpod usage.

The seven-file /4,166,688-byte complete-source archive and binding evidence are
R2 published and independently restore-verified (`holidays2052-full-base-publish-001`
/ `holidays2052-full-base-restore-001`).


### Holidays2052 snapshot checkpoint — 2026-10-11

The complete base is now a verified parentless snapshot with exact tracked-tree
preservation and inaccessible old base/head/merge commits. Evidence:
`holidays2052-snapshot-001`; details in journal40. Runtime-image/catalog/locale
binding and fresh native replay remain pending. No training admission or GPU use.

The eight-file /9,361,333-byte sanitized snapshot archive and evidence are R2
published and independently restore-verified (`holidays2052-snapshot-publish-001`
/ `holidays2052-snapshot-restore-001`).


### Holidays2052 native replay checkpoint — 2026-10-11

Fresh amended replay completes20chargedcalls /21exchanges in the independently
verified offline runtime. Both observed command errors are retained; cleanup
confirmed. Native and original patch text differ in hash abbreviations, but
independent application produces identical source files. See journal40 and
`holidays2052-native-replay-002`. Next: independent grading, full-history review
and token audit. No corpus addition/admission; Runpod off.


### Holidays2052 history checkpoint — 2026-10-11

Replay R2 restore verified (57 files / 8,831,099 bytes). Fresh native history
serialized without truncation: 14,102 input / 7,123 supervised target tokens.
Independent grading and semantic/admission review remain next; no corpus change
or GPU qualification claim. Detailed evidence is in journal40. Runpod off.


### Holidays2052 independent controls checkpoint — 2026-10-11

Exact native patch passes 1,496 finite calendar comparisons plus 31 upstream
tests. Base and three distinct incorrect mutation operators fail the generated
oracle. This is not publisher grading or corpus admission. Complete semantic
review and rights/split qualification remain; see journal40 for scope/evidence.
Runpod off; corpus048 unchanged.


### Holidays2052 qualification checkpoint — 2026-10-11

Candidate matches reference on43 publisher-declared nodes; base passes42/fails1.
Existing mechanical assessment passes replay/history/token/budget consistency.
R2 grade archive publish/restore verified (42files312,224bytes). Scope is declared
nodes in alternate runtime; unlisted localization case is not covered. Corpus048
unchanged. Next: quarantine integration/split review; rights and full-model
admission remain open. Runpod off.


### Corpus049 checkpoint — 2026-10-11

33 quarantined examples,180,300 supervised targets; R2 restore/recount and
29-update deterministic scheduling verified.528 pairwise lexical checks agree
with independent arithmetic. Next: updated split/privacy review and deployment
binding; broader data expansion and rights/full-model admission remain open.
Runpod remains off.


### Corpus049 qualification checkpoint — 2026-10-11

Draft repository-network isolation, full decoded four-pattern credential screen,
and latest staged-worker CPU integration completed. Training remains denied.
Next work remains diverse data expansion, rights/admission, frozen split design
and eventual bounded GPU qualification. No Runpod restart is needed yet.


### Hcloud547 runtime checkpoint — 2026-10-11

Complete pinned source and full dependencies prepared; offline Linux base suite
passes623test/subtest records across10packages. Fresh agent replay and restored
dependency bootstrap remain required. Corpus049 unchanged; Runpod off.


### Hcloud547 recovery checkpoint — 2026-10-11

Offline bootstrap from R2-restored source/dependency archives reproduces all
prior full-suite outcomes. Exact parentless source snapshot verified. Runtime
container assembly and fresh native replay remain pending. Runpod off.


### Runtime assembly storage gate — 2026-10-11

Hcloud547 offline image context prepared; build requires2GiB free disk. Current
343MiB is insufficient. Exact three-cache cleanup proposal awaits user approval
because caches belong to other projects; manual disk cleanup is an alternative.
No Runpod restart requested. Do not weaken unmounted/offline native protocol.


### Storage recovery and P1 exit requirement — 2026-10-11

User approved all11 identified Docker cache IDs; exact-ID deletion in leaf-first
dependency order removed all11. Post-cleanup free space was7,739,768,832bytes;
the prior storage gate is cleared. Evidence:approved-build-cache-cleanup-002.
At P1 exit, inventory project-owned bulk data and artifacts, publish missing
curated bundles to R2, verify content hashes and restoration, then remove
redundant local copies and report measured recovered space. Retain source code,
small manifests/receipts and active working inputs. Never infer full backup
coverage from a subset of transfer receipts; exclude secrets from archives.


## 2026-10-12: corpus exposure capacity audit and scaling priority

Revalidated corpus054 through the hash-bound inspection loader:38examples,213,020supervised tokens, still quarantined with zero training-admitted tokens. Enumerated a hypothetical50M-token schedule with seed7401 and9216maximum supervised tokens/update:7,884updates,50,004,719consumed tokens,4,719whole-example overshoot,234–235exposures per example. Independently reconciled per-example exposure counts to consumed tokens. This diagnostic schedule is not a training authorization and must not be deployed as a substitute for corpus growth.

Exact corpus-size lower bounds for a50M-token candidate under1/2/3/5maximum passes are50M/25M/16,666,667/10M supervised positions respectively. The3-pass scenario therefore requires16,453,647additional positions beyond the current quarantine corpus, plus admission of all counted data. These are sensitivity scenarios, not approved epoch policies. Three candidates can reuse an admitted corpus:150M cumulative exposure does not mean150M distinct data. Inverse token concentration is reported per example/task/repository as descriptive balance only, never statistical effective sample size or independence.

Next scaling work must prioritize batch qualification and rights/split coverage of acquired source pools, measuring yield in admitted tasks and supervised tokens; additional isolated replay examples alone cannot establish50M-scale readiness. Retain task fidelity, evaluator isolation, duplication controls and exact masks while expanding. No weakening of gates or speculative token counts. The first audit script hit a metadata-field mismatch before emitting a report;002 explicitly joins repository groups from the verified corpus manifest. Four-file41,807byte audit published to R2 and independently restored with all hashes matched. Evidence:evidence/data/corpus054-capacity-audit-002. No Runpod use or training approval.


### 2026-10-12 P1 batch continuation

Current corpus055:39quarantined tasks/216,751supervised tokens; no admission. Next eight candidate environment digests are recorded in evidence/data/corpus055-batch-readiness/swe-hero-next-batch-images-001. Process environments with a bounded disk budget, preserve source/evaluator separation, retain failed attempts, and compare fresh base/reference/candidate runs. Registry availability is not runtime qualification. Do not pull all eight images together. Before training, resolve rights/frozen splits, inherited emcee context incompatibility and full-size GPU validation; measured training-token sufficiency remains far below the planned50M-token candidate runs. Runpod stays stopped until local preparation reaches the explicit GPU gate.
