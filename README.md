# ZenithSync — a trainable Gemma 4 repository-repair agent

An autonomous software-engineering agent for the **Google Gemma 4 Developer Agent
Competition**, plus the training and verification infrastructure behind it. The
agent takes a repository issue, reads the code, runs the nine permitted tools,
writes a patch, checks it, and submits a diff. Everything around that — data
provenance, tokenization, admission gating, LoRA training, checkpoint resume,
artifact transport — is built so that **no claim in this repository rests on an
unverified step**.

```
pinned public source → task/source snapshot → native trajectory capture
  → baseline/reference/candidate grading → behavioural review
  → tokenizer + assistant-mask audit → quarantined corpus
  → four-gate admission → indexed loader → deterministic schedule
  → token-weighted LoRA worker → adapter checkpoint → serving → held-out evaluation
```

Every arrow in that path is implemented and tested. The edge into
**sustained real-corpus GPU training** is open: see [Status](#status) for exactly
what is and is not measured.

---

## Why this repo looks the way it does

Most agent projects fail at the seams — a corpus that quietly contains its own
test set, a "verified" checkpoint whose verifier shares the bug, a receipt that
attests something it never checked. This codebase is built around three rules:

1. **Reject, never coerce.** Exact field-set checks, exact integer accounting, no
   silent truncation, no inferred defaults for anything load-bearing.
2. **Two layers that do not share code.** The training loader
   (`zenithsync/training_corpus.py`) and an independent re-derivation
   (`zenithsync/corpus_audit.py`) must agree on every shared quantity. A defect
   in one cannot hide behind the other's agreement.
3. **Every receipt states what it does *not* establish.** A `scope` field on
   every artifact names the limit. Passing a gate is never promoted to passing
   the thing the gate is a proxy for.

That discipline has caught real defects, including in its own verifiers — three
independent adversarial reviews found **49 findings**, all fixed with regression
tests. Two of the worst were in the verification code itself: a second layer
that would bless bytes from outside the corpus tree, and an end-to-end check
carrying the exact blindness it was written to prove absent. Both are recorded in
[docs/42](docs/42-training-unblock-and-data-scale.md) rather than quietly fixed.

---

## Quickstart

```bash
git clone https://github.com/Shengboj0324/Gemma-4-Agentic-Platform
cd Gemma-4-Agentic-Platform
```

**The core needs no third-party packages** — only Python 3.11 or newer (3.11,
3.12 and 3.13.7 all verified; `/usr/bin/python3` on macOS is 3.9 and fails on
PEP 604 annotations):

```bash
python3 -m unittest discover -s tests
python3 -m zenithsync --help
```

That collects all **941 tests** and passes, skipping the 70 that need an
optional dependency. Every such test *skips* — a suite that errors instead
cannot tell you whether your environment or the code is wrong.

The **zero-skip** run needs torch, transformers, tokenizers, boto3 and
python-dotenv, plus explicit Torch opt-in, because a smaller default run is not
equivalent:

```bash
ZENITHSYNC_TEST_TORCH=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  python3 -m unittest discover -s tests
```

Locks for each environment are in `requirements/`; they are **not** one
interchangeable environment, so install the one matching the layer you are
touching.

To prove **from the R2 bucket alone** that a training run has everything it needs
— corpus restored and double-verified, the loader offering exactly the audited
training set, tokenizer assets fetched by content digest, all eight model files
present, the schedule digest reproduced, and the real worker's preflight passing:

```bash
python3 scripts/verify_r2_training_readiness.py \
  --artifact-manifest evidence/data/corpus072-admission-001/r2-artifact-manifest.json \
  --model-manifest    evidence/p1/model-intake-001/model-manifest.json \
  --corpus-sha256  <admitted manifest digest> \
  --content-sha256 c081880c71b9f78ffb4fdcf319d0959e8d7dfcb39878b8ac06f510f2d088f103 \
  --worker-config  configs/p1-corpus-qualification.json \
  --schedule-seed  7401 \
  --schedule-sha256 4664ecf632b35fad11dfa6d9d3e1ff19cfddb352816e99bb8750c8167cd1f06b \
  --output <new-dir> --prefix artifacts/v1 --env-file .env
```

Needs R2 credentials in a private `.env` at the repo root. Reads nothing else
local except those two manifests. The current admitted manifest digest is in
[docs/39](docs/39-p1-current-readiness.md).

---

## The competition contract we build against

| Constraint | Value |
|---|---|
| Base model, every agent and subagent | `gemma-4-31b-it-qat-w4a16-ct` (4-bit QAT, compressed-tensors) |
| Adapters | PEFT LoRA directories, referenced by name |
| Submission | `submission.zip`, root `agent.yaml`, restricted ADK schema, strictly under 3 GiB |
| Tools | exactly nine, plus declared `agent_tool` subagents |
| Runtime | L4×4, 96 GB **aggregate** (not one 96 GB device), network disabled |
| Budget | 12 h across all tasks **including** sandbox setup, excluding patch validation |
| Scoring | fraction of issues whose patch passes hidden validation; private leaderboard |
| Final deadline | 2026-12-02 |

The nine tools, extracted from the released wheel and exercised against real
bound functions in a Linux sandbox:

| Tool | Arguments |
|---|---|
| `run_command` | `command` |
| `read_file` | `filepath`, `start_line?`, `end_line?` |
| `edit_file` | `filepath`, `old_string`, `new_string`, `allow_multiple?` |
| `write_file` | `filepath`, `content` |
| `get_status` | — |
| `submit_patch` | — |
| `get_code_neighbors` | `node`, `edge_type?`, `max_neighbors?` |
| `search_similar_code` | `query`, `k?` |
| `get_code_subgraph` | `nodes` |

Results come back as compact JSON objects, e.g. `run_command` returns
`{"exit_code":…,"status":"ok","stdout":…,"stderr":…}`. That exact shape matters —
see [Trajectory translation](#trajectory-translation-what-we-refuse-to-fake).

**Budget model.** For `n` tasks with charged startup `T₀`, per-task setup `sᵢ`,
active allowance `tᵢ` and reserve `R`:

```
maximise Σ pᵢ(tᵢ)   subject to   T₀ + Σ(sᵢ + tᵢ) + R ≤ 43,200 s
```

At ~120 tasks that is six minutes per task *before* setup and reserve. This
motivates measured allocation; it does not prove a greedy scheduler optimal,
since a two-step fix produces discontinuous returns. Reliability has direct score
value: a 5 % whole-run failure rate against a 45 % conditional repair rate yields
`0.95 × 0.45 = 0.4275`, so a stable 44 % configuration is preferable.

---

## Architecture

### Contracts layer — `contracts.py`, `artifacts.py`, `archive.py`, `splits.py`

Pure, dependency-free, exhaustively tested.

- **Budget** — integer-nanosecond accounting. `admits(A)` iff `C + R + A ≤ L`,
  so at least the reserve `R` survives any admitted action. Overruns are retained
  as visible debt, never clipped.
- **Event/state reducer** — an append-only log with a legal-transition table.
  `candidate` events clear any prior check result; a `check` requires the
  *current* candidate hash, so a stale receipt cannot be re-associated.
  `submit` is permitted without a passing local check, because only the
  independent evaluator may declare acceptance.
- **Artifact manifests** — streaming SHA-256 inventories, exact field sets,
  symlinks and non-regular files rejected, path traversal rejected.
- **Split isolation** — task, `repository_group`, `leakage_group` and
  `input_sha256` each map to exactly one split; a conflict is refused. String
  labels do not prove real independence, and the code says so.

### Model and serving — `model_intake.py`, `quantized_layout.py`, `architecture_layout.py`, `serving.py`, `gpu_memory.py`

Model intake recorded **8 files / 23,297,590,856 bytes / 2,009 tensors**, of
which **410 are quantized text projections** and 779 unquantized. Reconstructed
dense weights total **65,364,750,040 bytes (60.88 GiB)** — which is why packed
on-disk size is not the training footprint. Measured load was 19.63 GiB; one
serving configuration reported 43.23 GiB available for KV cache and a
47,216-token cache capacity. Separate device samples read 67,071 and 67,231
MiB **including serving reservations** — neither is a whole-run peak.

An H100 validation run exposed **repeated Unicode content-fidelity failures** in
repository context. That is recorded, not papered over: do not describe the
model/tool path as fully reliable.

### Conversation and supervision — `conversation.py`, `training_masks.py`, `gemma_trajectory.py`

Tool histories are validated transport: every tool response binds to exactly one
call, interrupted exchanges are refused, and a pending call is accepted only at
the end and only when explicitly requested.

Assistant-token masks are derived by **instrumenting the pinned chat template
without changing what it renders**. `annotate_template` inserts
`{% generation %}` markers, then the implementation requires:

- annotated rendering is byte-identical to native rendering;
- annotated tokenization is identical to native tokenization;
- an independent span renderer agrees with the tokenizer;
- offset-mapped tokenization agrees again;
- every token either lies wholly inside a supervised span or wholly outside it.

A token crossing a supervision boundary is a hard failure. Supervision covers
assistant reasoning, tool calls, content and terminal markers — **never** tool
results or user text.

### Training — `training_corpus.py`, `training_batch.py`, `corpus_optimization.py`, `corpus_training.py`, `training_schedule.py`, `training_session.py`

**Objective.** For example `i` with labels using `-100` for unsupervised
positions, `nᵢ = Σ_{t=1..Tᵢ-1} 1[labelᵢ[t] ≠ -100]`. Position zero supplies no
shifted target. With `Lᵢ` the mean cross-entropy over those `nᵢ` targets:

```
L = (Σᵢ nᵢ Lᵢ) / (Σᵢ nᵢ)
```

Streaming each example's backward pass with weight `nᵢ / N` reproduces that
objective's gradient, where `N` is the exact update target count. **Averaging
per-example means would overweight short examples.** Examples are never
concatenated across attention boundaries; there is no packing.

Rejection conditions: zero or mismatched target counts, non-finite loss or
gradients, a gradient on a frozen parameter, non-finite parameters after the
step, or any initialised distributed context — global distributed normalisation
is not implemented, so it is refused rather than approximated.

**LoRA.** `W' = W + (α/r)·BA`, with `A: r×d_in`, `B: d_out×r`, so `r(d_in+d_out)`
trainable parameters per projection. The qualified fixture uses **r=4, α=8,
dropout 0, exactly the 410 text projections, 30,607,360 adapter parameters**,
base frozen, adapters stored separately. Attachment refuses if the trainable set
or the parameter count differs from the projection accounting.

**Schedule.** Deterministic whole-example updates with exact supervised-token
accounting. Order is a reproducible hash shuffle — explicitly *not* a claim of
statistical independence. Resume is permitted only at an exactly reproduced
boundary: manifest identity, optimizer state, RNG state and data cursor must all
match, and the consumed prefix is re-validated. Changing any of them starts a
different experiment.

**State.** `fingerprint_state` hashes parameters and persistent buffers in bounded
chunks, rejecting meta/sparse/quantized/non-contiguous tensors rather than
silently making model-sized copies. RNG checkpoints cover Python, NumPy's legacy
global and Torch CPU/CUDA generators, and validate against private generators
*before* mutating any global state. A failed forward can still have moved buffers
or RNG — so "no optimizer step" never means "state is pristine", and the worker
must restore a checkpoint rather than retry.

### Admission — `corpus_admission.py` + `scripts/admit_training_corpus.py`

A corpus is born `quarantine` with four null gates and **cannot** reach the
optimizer. Promotion is immutable: stage a complete new tree, copy example files
and reviewer evidence with post-copy identity verification, write one receipt per
gate bound to the **corpus content identity**, and publish only after the strict
training loader accepts the result.

| Gate | What must be supplied |
|---|---|
| `rights_and_attribution` | licence/notice provenance over the exact observed material |
| `split_isolation` | exposure audit and cross-split controls |
| `runtime_qualification` | context margins, schedule replay, resume boundaries |
| `task_alignment` | one accepted review per `(task_id, repository_group)`, exact coverage |

Two digests, and **only one is stable**. The *content identity* hashes
`schema_version`, `tokenizer_assets`, `max_length`, `examples` — unchanged by
promotion, which is what lets a receipt bind it. The *manifest digest* covers the
whole `corpus.json` including receipts, so it moves whenever a receipt does.
Compare content identities between corpora.

### Independent verification — `corpus_audit.py` + `scripts/verify_admitted_corpus.py`

Re-derives from stored bytes without calling the loader, collator or schedule
iterator: every digest, per-example supervised count (by walking labels
directly), token validity against the vocabulary, duplicate token-sequence
detection, split isolation across task/repository/leakage families, context
margin, and every gate binding and coverage check — with the loader's own
per-kind byte ceilings re-derived rather than loosened.

`verify_loader_offers` is the check that matters: comparing each fetched example
against *its own* audit row passes a held-out example substituted one-for-one
into training. So the **set** of offered identities is compared against the
audited set, each split is asserted, and each token array is re-hashed.

### Artifact transport — `object_store.py`, `corpus_transport.py`, `evidence_shipment.py`, `r2_client.py`

Content-addressed publish/restore over an injected S3-compatible client.
ETags are never treated as digests; remote bytes are streamed and hashed;
restore is atomic and verifies the promoted destination afterwards.

Corpus transport adds the invariants that matter when the bucket is the only
durable home: **publication uploads exactly the file set the corpus manifest
reaches** (a stray `.env` fails the publish — there is a test that plants one),
and restoration proves manifest digest, content identity and admission status
before the corpus is usable.

Bulk evidence shipment groups a tree into packages and **stages each into a fresh
directory holding exactly the files classification admitted**. That is not
cosmetic: handing the live directory to a recursive inventory meant packages
published each other's subtrees, files published twice, byte ceilings saw a
fraction of what shipped, and caches shipped anyway. Credential paths and
symlinks refuse a package whole; `.git` and caches are *skipped*, because a
checkout's working tree is the evidence while its VCS metadata is reproducible
and could carry a remote credential.

`shipment_lock` excludes concurrent publishers per bucket prefix — two writers of
one content-addressed key can make a readback race an in-flight overwrite, which
the integrity guard reports as a failure indistinguishable from a real one.

### Campaign planning — `campaign_plan.py` + `scripts/plan_training_campaign.py`

Five token quantities are kept rigorously apart, because conflating them is how a
token budget becomes a false diversity claim: unique supervised targets, unique
inputs, processed inputs, processed supervised, and padding. Repetition is
reported as a **repetition factor**, never absorbed into "tokens of data".
Mixtures allocate by exact `Fraction` via largest remainder. `forecast_campaign`
**refuses** to produce a duration or cost without a measured throughput and its
stated evidence.

### Data intake — `task_pool.py`, `cohort_freeze.py`, `openhands_translation.py`

Task screening reads **metadata only** — identifiers, commits, language, licence
label, image name, timestamp. No issue body, source or reference patch, so
nothing here can leak a solution. A placeholder licence value such as
`custom-check-github` is refused as *unknown* and cannot be allowlisted.

Selection is deterministic and breadth-first across repositories under explicit
per-repository and per-owner caps; a shortfall is reported rather than met by
breaking a cap. Cohorts are repository- **and owner**-disjoint, with whole owners
as the indivisible unit — a sibling package inside one owner is the contamination
path that splitting by task misses.

`cohort_freeze` makes a held-out cohort mean something: an immutable record
binding dataset, revision, metadata identity, exposure-ledger identity and seed,
with a gate (`scripts/check_cohort_freeze.py`) that exits nonzero on any
candidate that is a reserved task *or* belongs to a reserved owner.

#### Trajectory translation: what we refuse to fake

`openhands_translation.py` converts OpenHands tool calls into the official
nine-tool contract under eight named equivalence rules — and translates **no tool
results at all**. That restriction *is* the finding. The official tools return
structured JSON that an OpenHands observation does not separate, so re-rendering
one into the other would fabricate a runtime result. Results must come from
executing the translated action in the official runtime.

| OpenHands | Official | Rule |
|---|---|---|
| `execute_bash{command}` | `run_command{command}` | `execute_bash_to_run_command` |
| `str_replace_editor{view,path}` | `read_file{filepath}` | `view_whole_file_to_read_file` |
| `…{view,path,view_range:[a,b]}` | `read_file{filepath,start_line,end_line}` | `bounded_view_range_…` |
| `…{create,path,file_text}` | `write_file{filepath,content}` | `create_to_write_file` |
| `…{str_replace,path,old_str,new_str}` | `edit_file{filepath,old_string,new_string}` | `str_replace_to_edit_file` |
| `think{thought}` | assistant `reasoning` channel | `think_to_reasoning_channel` |
| `finish` | **not** `submit_patch` | `finish_is_not_submit_patch` |

Refused with stable reason codes: `insert`, `undo_edit`, `task_tracker`,
interactive stdin writes, `C-c`-style control sentinels (they interrupt a running
process, they are not commands), an implicit empty replacement, a no-op
replacement, a directory listing turned into a file read, and out-of-workspace
paths. One untranslatable call fails the whole trajectory — a partial translation
silently changes what the agent did.

### Test-outcome interpretation — `pytest_*`, `junit_controls.py`, `go_test_controls.py`, `mocha_controls.py`, `maven_*`, `static_controls.py`

Parsers for real test output across ecosystems, with the boundary stated
everywhere: parser acceptance is not proof the task behaviour is correct, and
supplied aggregate counts must agree with per-case outcomes or the report is
refused.

---

## Status

**What is verified**

| Area | Evidence |
|---|---|
| Local suite | **941 tests, zero skips** with the full dependency stack and Torch enabled, ~31 s; 941 collected and passing with 70 skips on a stdlib-only 3.13 |
| Official contract | unchanged starter compiles with the nine real bound functions; 25 Linux integration checks with networking disabled, 4 GiB, 2 CPUs |
| Model intake | 8 files / 23,297,590,856 B / 2,009 tensors; 410 quantized projections verified |
| Masks | six positive and six rejection fixtures against the real tokenizer |
| LoRA on the real checkpoint | one H100 update on a **24-token** fixture, frozen-state and adapter-reload checks |
| Admitted corpus | Corpus072: 51 tasks / 50 repository groups / 954,733 input / 262,593 supervised targets; four gates bound; content identity `c081880c…` |
| Two-layer agreement | an independent audit reproduces every quantity, including the 210-token minimum context margin, from separate code |
| R2 round trip | quarantine → promote → publish → restore with `--purpose training`; worker preflight accepts the staged tree |
| Model in R2 | all 8 files present, including the 23,265,352,448-byte `model.safetensors` — **the weights are not on the dev machine** |
| Task pool | 32,079 rows screened → 4,818 eligible / 507 repos / 439 owners → 2,966 selected → train 2,076 / dev 445 / **confirmation 445 frozen** |

**What is not**

- **No throughput has ever been measured** for this configuration. The recorded
  67,231 MiB device reading came from a **24-token** fixture: it bounds memory,
  not speed. The planner refuses to forecast without a measured rate.
- **No sustained real-corpus training run.** No 50M-token candidate started.
- **No learned improvement.** No sound claim of superiority over any other agent.
- **Peak memory at full sequence length is unmeasured.** The corpus's longest
  example is 24,366 input tokens.
- **Corpus072 is all `train` and all development-exposed.** A 50M-target run
  would be **190.4 repetitions** of the same 51 tasks — which is exactly why the
  public task pool exists.
- **Rights are screened, not cleared.** Licence labels are evidence for a review.
- The dev interpreter has **torch 2.14.1**, not the worker's pinned **2.10.0**,
  and no `compressed-tensors`. The Torch tests therefore pass on a *different*
  Torch than the training stack; `scripts/verify_training_runtime.py` exits
  nonzero here and names both mismatches. Closing that gap needs the container,
  because the lock pins Linux wheels.
- `configs/Dockerfile.p1-training-runtime` **has never been built.** No official
  Runpod template ships Torch 2.10 with Python 3.12.

### Next, in order

1. Measure throughput on one bounded GPU run at realistic sequence length.
2. Measure peak memory at 24,366 input tokens before committing to an 80 GB card.
3. Build and qualify the training image; require `verify_training_runtime.py` to
   exit zero inside it on the intended GPU.
4. Pull environments for the selected tasks, grade baseline/reference outcomes,
   capture native trajectories. **Eligibility is not a task.**
5. Complete the rights review on the pool.
6. Assemble replayed trajectories into a new quarantine corpus and admit it on
   its own evidence. Corpus072's admission says nothing about a successor.
7. Compare candidates against a frozen baseline and the frozen confirmation
   cohort before claiming anything.

---

## Repository layout

```
zenithsync/     104 modules, ~11.8k lines — contracts, model, masks, training,
                admission, audit, transport, intake. Core needs no third-party packages.
scripts/        134 CLIs, ~14.5k lines — every one writes a hash-bound receipt,
                refuses an existing --output, and writes nothing on failure.
tests/          134 modules, ~14.1k lines, 941 tests — zero skips with the
                full stack, 70 skips with the standard library alone.
configs/        pinned serving/training profiles, deployment file map, Dockerfiles.
requirements/   separate locks: serving, evaluator, tokenizer, R2, PEFT supplement.
                These are NOT one interchangeable environment.
docs/           43 documents — design, audits, failures, journal.
evidence/       immutable receipts and manifests. Not every file has an R2 counterpart.
candidates/     agent.yaml bundles for the restricted ADK schema.
```

**Operational conventions** every CLI follows: validate arguments *before*
creating `--output`; record the implementation's source identities and re-check
them after the operation; remove the output directory on failure; and never write
a passing receipt for a failed run. Exit codes carry meaning where a caller needs
them — `verify_training_runtime.py` uses 0 satisfied / 1 check failed / 2 bad
arguments / 3 run failed, and `check_cohort_freeze.py` adds 4 for an unusable
freeze record.

### Pinned runtime

| Component | Version |
|---|---|
| Training/serving host | Linux, Python **3.12** (enforced by the worker) |
| torch | 2.10.0 |
| transformers | 5.13.1 |
| compressed-tensors | 0.15.0.1 |
| peft | 0.21.2 |
| Core contracts | Python 3.13.7, standard library only |

---

## Documentation

Start with **[docs/42](docs/42-training-unblock-and-data-scale.md)** for the
current cycle, then **[docs/41](docs/41-p1-complete-developer-handoff.md)** for
the full handoff and **[docs/39](docs/39-p1-current-readiness.md)** for live
status.

| Area | Documents |
|---|---|
| Current cycle and status | [42 training unblock & data scale](docs/42-training-unblock-and-data-scale.md), [41 developer handoff](docs/41-p1-complete-developer-handoff.md), [39 readiness](docs/39-p1-current-readiness.md), [40 implementation journal](docs/40-p1-implementation-journal.md) |
| Architecture and contracts | [19 platform & model handoff](docs/19-agent-platform-and-model-handoff.md), [20 R0 foundation](docs/20-r0-foundation.md), [22 official contract audit](docs/22-official-contract-audit.md) |
| Training design | [31 training representation](docs/31-training-representation-readiness.md), [32 full-checkpoint GPU qualification](docs/32-full-checkpoint-gpu-qualification.md), [38 corpus integration](docs/38-training-corpus-integration.md) |
| Data | [23 data requirements](docs/23-data-requirements-and-acquisition-plan.md), [33 public data intake](docs/33-public-data-intake.md), [35 rights & evaluation isolation](docs/35-data-rights-and-evaluation-isolation.md), [37 SWE-rebench adapter](docs/37-swe-rebench-source-adapter.md) |
| Runtime and serving | [25 deployment handoff](docs/25-p1-deployment-handoff.md), [27 GPU session report](docs/27-p1-gpu-validation-report.md), [30 H100 validation](docs/30-p1-h100-validation.md), [34 source task runtime](docs/34-source-task-runtime.md) |
| Competition and evaluation | [11 code track & strategy](docs/11-code-track-and-joint-strategy.md), [01 competition facts](docs/01-competition-facts.md), [05 evaluation protocol](docs/05-evaluation-protocol.md), [04 technical proposal](docs/04-technical-proposal.md) |
| Cloud and cost | [21 cloud preparation](docs/21-cloud-preparation.md); [reports/](reports/) holds the data-source and Runpod research |
| Process and history | [12 continuous implementation plan](docs/12-continuous-implementation-plan.md), [24 implementation history](docs/24-p1-implementation-status.md), [26 acceptance checklist](docs/26-p1-acceptance-checklist.md), [28 requirements audit](docs/28-p1-requirements-audit.md) |
| Preserved research (not the current mandate) | [13](docs/13-user-painpoints-and-change-synthesis.md)–[18](docs/18-reproduction-cycle-results.md) |

**Precedence when documents disagree:** exact current manifest and referenced
receipts → explicit correction package → current readiness/handoff → older
narrative → original proposal. A later prose claim never silently overrides
contradictory raw output; where a discrepancy remains, both are retained and the
uncertainty is stated.

---

## Contributing

- Read [docs/41](docs/41-p1-complete-developer-handoff.md) §12 before touching
  anything: it is the safe-restart procedure.
- Credentials go in a private `.env` at the repo root. Three independent
  mechanisms keep it out of Git and out of the bucket, and
  `tests/test_repository_hygiene.py` asserts all three still hold.
- Never reset the working tree to make it clean — uncommitted and untracked
  evidence is part of the handoff.
- After each cycle, append to [docs/40](docs/40-p1-implementation-journal.md) and
  update [docs/39](docs/39-p1-current-readiness.md). Record failures, not just
  successes: the journal's value is the attempts that did not work.

## Licence

Competition winner obligations require Apache-2.0 terms and reproducible
source/environment delivery. Model weights are **never** in this repository.
Third-party data retains its upstream licences; see
[docs/35](docs/35-data-rights-and-evaluation-isolation.md).
