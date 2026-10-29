# Training unblock, R2-resident data and campaign planning

**Snapshot: October 29, 2026. This cycle closed the admission blocker, moved the corpus to R2 as its durable home, and built the intake that scales the data. No GPU training has started and no Runpod resource was created, started, stopped or modified.**

Read this together with [the complete P1 developer handoff](41-p1-complete-developer-handoff.md), which remains the architecture and evidence entry point. This document records only what changed and what it now allows.

## 1. What changed

| Before this cycle | After this cycle |
|---|---|
| Corpus072 quarantined; all four admission gates `null`; the worker refused before model access | Corpus072 **admitted**; all four gates bound to recorded review evidence; `preflight_corpus_run` passes |
| No code existed to produce a gate receipt or promote a corpus | `zenithsync/corpus_admission.py` + `scripts/admit_training_corpus.py` |
| Corpus integrity trusted the training loader alone | `zenithsync/corpus_audit.py` re-derives everything independently and must agree |
| Corpus transport was a generic artifact publish | `zenithsync/corpus_transport.py` binds transport to corpus identity, status and an exact file set |
| 51 tasks / 50 repository groups, all `train`, no held-out cohort | **2,966** screened public tasks / **507** repositories / **439** owners, split into repository- and owner-disjoint train / development / confirmation cohorts |
| Token budgets discussed in prose | `zenithsync/campaign_plan.py` computes exposure, padding, mixture and cost exactly, and refuses a forecast without measured throughput |
| OpenHands trajectories unusable without undeclared tool renaming | `zenithsync/openhands_translation.py` translates actions under named rules and refuses the rest |
| Local regression: 671 tests | **805 tests, zero skips, Torch enabled** |
| No way to check a host before the worker billed for the failure | `zenithsync/runtime_preflight.py` + `scripts/verify_training_runtime.py`, with tests that assert the pins match the worker source |

## 2. Corpus072 is admitted

Promotion is immutable: the quarantined corpus is never edited. A complete new tree is staged, example files and evidence documents are copied with post-copy identity verification, one receipt per gate is written, and the result is published atomically **only after the strict training loader accepts it with `purpose='training'`**.

| Quantity | Value |
|---|---|
| Source (quarantine) manifest SHA256 | `42da2d372f908d00b72a3f7d89af9b5fa082f8caeb8a4307bd77cfc363a2de75` |
| Admitted manifest SHA256 | `c37dc07f2e33f2492b12025487ee87c8a9902ccceccdd8ca2a8a954faf40599d` |
| Corpus content identity (unchanged by promotion) | `c081880c71b9f78ffb4fdcf319d0959e8d7dfcb39878b8ac06f510f2d088f103` |
| Examples / unique tasks / repository groups | 51 / 51 / 50 |
| Input tokens / supervised targets | 954,733 / 262,593 |
| Files in the admitted bundle | 115 (103 corpus + 4 receipts + 8 evidence copies) |
| Schedule SHA256 (9 updates, one epoch, zero overshoot) | `4664ecf632b35fad11dfa6d9d3e1ff19cfddb352816e99bb8750c8167cd1f06b` |

The content identity is deliberately preserved, which is what lets a receipt bind it: `corpus_content_identity` hashes only `schema_version`, `tokenizer_assets`, `max_length` and `examples`, so adding receipts cannot change what the receipts refer to. The schedule hash reproduces the previously recorded value exactly, which is independent corroboration that promotion changed no training-relevant byte.

### Gate evidence actually bound

| Gate | Primary evidence (loader re-reads and, for alignment, schema-validates) | Supporting evidence (bound by hash only) |
|---|---|---|
| `rights_and_attribution` | `corpus072-history-material-001/report.json`, `.../contact-review.json` | — |
| `split_isolation` | `corpus072-split-audit-001/report.json` | — |
| `runtime_qualification` | `corpus072-integration-001/corpus072-ingestion-001/report.json`, `corpus072-integration-001/context-report.json` | `.../resume-verification.json` |
| `task_alignment` | `corpus072-integration-001/task-reviews.json` (51 accepted reviews, exact coverage) | `corpus072-integration-001/alignment-report.json` |

Every primary document that declares a corpus binding declares **this** corpus manifest; promotion refuses a document naming another. Supporting evidence exists because the loader requires every `task_alignment` document to carry `task_reviews`; a coverage-control report does not, and reshaping it to pass that schema would have been dishonest. It is therefore copied into the bundle, hashed and listed separately.

### What admission does and does not mean

Admission means the four gates are **resolved and bound**: named evidence exists, it refers to this exact corpus content, task-alignment coverage is complete and accepted, and the loader will now hand these examples to an optimizer. It does **not** mean rights are cleared, that a reviewer's conclusion is true, that the split is uncontaminated, or that the GPU will fit the work. Those remain the reviewers' claims, recorded with their own stated limits.

One limitation is explicit and unchanged: **all 51 examples are `train` and all have been development-exposed.** The split audit records `eligible_unseen_confirmation_tasks: 0`, so an all-train admission is the factually correct state for this corpus. Promotion deliberately cannot reassign a split, because that would describe different data than the supplied split evidence. The held-out cohort comes from the new task pool in section 4, not from Corpus072.

## 3. R2 is the corpus's durable home

`zenithsync/corpus_transport.py` adds the invariants that matter when the bucket is the only durable copy:

* **Publication uploads exactly the corpus.** The inventory is compared against the set of paths the corpus manifest reaches — `corpus.json`, every token and audit file, every gate receipt and every evidence document named inside those receipts. An extra file fails the publish rather than riding along, so a stray `.env`, cache or scratch file cannot reach the bucket. This is covered by a test that plants a `.env` and asserts nothing is uploaded.
* **Restoration proves identity before use.** The declared manifest digest, content identity and admission status must all match, and `--purpose training` additionally requires the loader to reach training admission. A quarantined corpus cannot be restored as admitted.

Verified live round trip, in order:

1. `stage_corpus_from_r2.py` restored the quarantined Corpus072 payload from `quarantine/v1` — 103 files, 10,578,444 bytes.
2. `admit_training_corpus.py` promoted it with the evidence above.
3. `publish_corpus_to_r2.py` published the admitted corpus to `artifacts/v1` — 115 files, 10,782,715 bytes, artifact manifest `2959faedf43b2f0d77bdc0f160085bd2cf863f843d7e0404cc1d20178289014a`.
4. `stage_corpus_from_r2.py` restored it again with `--purpose training` and the loader reported `training_admitted: true`.
5. `preflight_corpus_run` — the real worker's own preflight — accepted the staged tree, schedule and `configs/p1-corpus-qualification.json`.

No corpus bytes are retained on the development machine: every step above ran in a session scratch directory. The bucket now holds 17,058+ objects over roughly 34.5 GiB, and the new packages are listed in section 6.

`zenithsync/r2_client.py` centralises credential loading and exposes only `get_object`, `put_object`, `head_object` and `upload_file`, so an injected client cannot delete, list or reconfigure a bucket. Credentials are read from the process environment or an explicit dotenv file and never returned, logged or written into a receipt.

## 4. Data scale: a screened, cohort-split public task pool

The arithmetic that forced this work, computed by `scripts/plan_training_campaign.py` against the admitted corpus:

| Quantity | Value |
|---|---|
| Unique supervised targets | 262,593 |
| Target for one candidate run | 50,000,000 supervised targets |
| Repetition factor required | **190.41×** |
| Whole epochs required | 191 |
| Approximate processed input tokens | 181,789,499 |
| Largest repository group share | 4.87% (under the declared 5% cap) |

190 passes over 51 development-exposed tasks is an exposure count, not 50M tokens of data. The planner reports it as a repetition factor precisely so it cannot be presented as diversity.

`scripts/build_task_pool.py` therefore screens pinned public task metadata. Run against the already-pinned SWE-rebench V2 projection (`nebius/SWE-rebench-V2`, revision `10483de0f50fe5da545942705a76c6150171af7f`, metadata file `701f75d5eed78ffcce6355f6ea4093d63f5c9022188c1d7f018e4d9b5d2b15b4`, 32,079 rows):

| Stage | Result |
|---|---|
| Rows screened | 32,079 |
| **Eligible** | **4,818** (15.02%) across **507** repositories and **439** owners |
| Refused: language not `python` | 24,524 |
| Refused: licence label is a placeholder | 1,706 |
| Refused: repository already development-exposed | 466 |
| Refused: no licence field at all | 348 |
| Refused: duplicate repository base commit | 199 |
| **Selected** under caps (≤12 per repository, ≤24 per owner) | **2,966** across 507 repositories / 439 owners |

Split into repository- **and owner-disjoint** cohorts:

| Cohort | Tasks | Repositories | Owners |
|---|---:|---:|---:|
| train | 2,076 | 277 | 240 |
| development | 445 | 112 | 100 |
| confirmation | 445 | 118 | 99 |

Owners are the indivisible unit, because a fork, a backport or a sibling package inside one owner is exactly the contamination path that splitting by task misses. A requested share is therefore approached, never hit exactly, and the achieved size and its deviation are both reported. A cohort is never balanced by splitting an owner.

That gives a **445-task confirmation cohort, repository-disjoint from training**, which is above the 200–500 breadth target in [document 23](23-data-requirements-and-acquisition-plan.md) and is the first prospectively selectable held-out cohort this project has had.

### Honesty boundaries on the pool

* Screening reads **metadata only** — identifiers, commits, language, licence label, image name, timestamp. No issue body, repository source or reference patch is read, so nothing here can leak a reference solution.
* A publisher's licence label is **evidence for a rights review, not a clearance.** The 1,706 placeholder values (`custom-check-github` and similar) are refused as unknown rather than optimistically treated as permissive. The allowlist excludes copyleft families, which need a case-by-case decision rather than a default.
* Exposure exclusion used this project's own recorded ledger, which states `complete_exposure_ledger: false`. It reduces **known** contamination. Forks, backports, vendored copies and base-model pretraining exposure are not visible here, so this is **not** an unseen-data guarantee.
* `split_frozen` is `false`, `rights_cleared` is `false`, `replay_verified` is `false` and `training_approved` is `false` on every artifact in the pool. Nothing in it may train until each becomes true on its own evidence.
* Eligibility is not a task. Each selected task still needs its environment pulled, its baseline and reference outcomes graded, and a native trajectory captured before it becomes a training example.

## 5. OpenHands translation: actions only, by design

The large public trajectory corpora use OpenHands tool semantics. `zenithsync/openhands_translation.py` translates their **actions** into the official nine-tool contract under named rules, and translates **no results at all**.

That restriction is the finding, not a shortcut. The official tools return structured JSON — `run_command` returns `exit_code`/`status`/`stdout`/`stderr`, `read_file` returns `content` with a line range, `edit_file` returns a unified diff and an occurrence count, `write_file` returns a size — and an OpenHands observation does not separate those fields. Re-rendering one into the other would fabricate a runtime result. Results must come from executing the translated action in the official runtime, which is what `zenithsync/replay_history.py` already does.

| OpenHands | Official | Rule |
|---|---|---|
| `execute_bash{command}` | `run_command{command}` | `execute_bash_to_run_command` |
| `str_replace_editor{view, path}` | `read_file{filepath}` | `view_whole_file_to_read_file` |
| `str_replace_editor{view, path, view_range:[a,b]}` | `read_file{filepath, start_line, end_line}` | `bounded_view_range_to_read_file_line_range` |
| `str_replace_editor{view, path, view_range:[a,-1]}` | `read_file{filepath, start_line}` | `open_ended_view_range_to_whole_file_read` |
| `str_replace_editor{create, path, file_text}` | `write_file{filepath, content}` | `create_to_write_file` |
| `str_replace_editor{str_replace, path, old_str, new_str}` | `edit_file{filepath, old_string, new_string}` | `str_replace_to_edit_file` |
| `think{thought}` | assistant `reasoning` channel on the next action | `think_to_reasoning_channel` |
| `finish` | **not** `submit_patch`; submission is adapter-authored | `finish_is_not_submit_patch` |

Refused with stable reason codes: `insert` and `undo_edit` (no official counterpart), `task_tracker` (no official tool), `execute_bash` with `is_input` (writes to a running process's stdin, which `run_command` has no session for), an empty or missing `new_str` (deleting a block and replacing it with the empty string are different declarations), a no-op replacement, a directory-shaped or out-of-workspace path, and an inverted or malformed line range. One untranslatable call fails the whole trajectory: a partially translated trajectory would silently change what the agent did.

`finish` is not mapped to `submit_patch` because they are different acts — one signals that the agent considers itself done, the other captures the working tree as a diff. The terminal submission is therefore authored by the replay adapter and recorded as adapter-authored, which is the precedent `mini_replay_history` already set.

## 6. Two-layer verification

`zenithsync/corpus_audit.py` is a deliberately separate second layer. It does not call the training loader, the collator or the schedule iterator, and it does not trust any summary those produce. It recomputes from stored bytes: every file digest and size, the corpus content identity, per-example supervised-target counts by walking labels directly, token/label validity against the vocabulary, the audit file's declared counts and digests, duplicate token-sequence detection, split isolation across task, repository and leakage families, context margin under a declared output reserve, and every gate receipt's binding and coverage.

`scripts/verify_admitted_corpus.py` runs both layers and requires them to agree on eight shared quantities, then refetches **every** example through the loader and rechecks it against the audit. Disagreement is a failure, not a warning.

Result on the staged admitted corpus:

| Quantity | Value |
|---|---|
| Examples / unique tasks / repository groups | 51 / 51 / 50 |
| Split counts | train 51, development 0, confirmation 0 |
| Input tokens / supervised targets | 954,733 / 262,593 |
| Longest example | 24,366 input tokens |
| Smallest context margin (32,768 limit, 8,192 reserve) | **210 tokens** |
| Examples refetched and rechecked | 51 |
| Loader agreement | true, zero disagreements |
| Schedule coverage | exact one-to-one |

The 210-token margin reproduces the figure recorded in document 41 from a wholly separate code path, which is the strongest corroboration available short of a third implementation.

Agreement between the layers is evidence of **consistent accounting**. It is not evidence that the data is well chosen, that the rights are cleared or that the model will learn anything.

### Test coverage added

| Test module | Tests | What it pins |
|---|---:|---|
| `tests/test_corpus_admission.py` | 18 | One success path; refusals for missing/empty/duplicate/oversized/non-object evidence, evidence naming another corpus, evidence inside the corpus tree, incomplete or rejected task reviews, an already- or partly-admitted source, a wrong manifest digest, an existing destination, a tampered example file, and evidence mutated mid-promotion. Also that the promoted tree still loads after its source is deleted. |
| `tests/test_corpus_transport.py` | 14 | Quarantine and admitted round trips; a planted `.env` blocking publication; status and digest mismatches; a quarantined corpus refused as admitted; a bundle missing its corpus manifest; a bundle carrying an undeclared extra file; the restore byte budget; a tampered receipt; an unknown gate; and an admitted corpus restored after both its origins are deleted. |
| `tests/test_corpus_audit.py` | 16 | Agreement with the loader on every shared quantity; independent content-identity recomputation; tampered token arrays, counts disagreeing with the stored audit, a label that is not its own input token, cross-split leakage, a duplicate token sequence, a candidate claiming training approval, a context limit leaving no output room, a receipt bound to another corpus; and schedule-coverage refusals. |
| `tests/test_campaign_plan.py` | 18 | Separation of unique/processed/padding counts; partial-epoch rounding; infeasible targets reported rather than accepted; largest-remainder allocation summing exactly on indivisible totals; case-insensitive group concentration; and a forecast refused without measurement evidence. |
| `tests/test_task_pool.py` | 22 | Stable reason codes for malformed rows; placeholder licences refused separately and un-allowlistable; each exclusion having its own reason; duplicate instance and repeated base commit; deterministic selection that changes with the seed; owner caps honoured and shortfall reported rather than a cap broken; cohorts repository- and owner-disjoint with whole owners kept together even when that skews a share. |
| `tests/test_openhands_translation.py` | 24 | Every translation rule and its argument mapping; every refusal reason; thoughts folding onto the next action and a trailing thought dropped rather than attached to an invented one; one untranslatable call failing the whole trajectory; actions after or duplicated terminals refused; determinism. |

| `tests/test_runtime_preflight.py` | 22 | That the preflight pins are byte-identical to the worker's own (parsed out of `run_corpus_training_worker.py`, so the two cannot drift apart); local build tags stripped before comparison; absent packages, wrong platform, wrong Python, insufficient device memory and an over-capacity example each reported with every problem kept. |

Full local suite: **805 passed, zero skips, Torch tests enabled, 27.135 seconds**, run as
`ZENITHSYNC_TEST_TORCH=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 <qualified-python> -m unittest discover -s tests`.

**One caveat on that suite, found by the new preflight.** The development
interpreter used for these runs has torch **2.14.1**, not the worker's pinned
**2.10.0**, and `compressed-tensors` is absent from it entirely. The Torch-dependent
tests therefore pass on a *different* Torch than the training stack. That is a
real limitation on what the suite establishes, and it is exactly what
`scripts/verify_training_runtime.py` is for: run on this machine it exits nonzero
and names both mismatches. The reduced-model numerical checks remain valid for the
interpreter that ran them; they are not evidence about torch 2.10.0 kernels.

### Runtime preflight and the image gap

`scripts/verify_training_runtime.py` runs the worker's own preconditions — Linux,
Python exactly 3.12, the four pinned versions, one exclusive CUDA device, the
70 GiB free-memory floor, and the corpus's longest example against the configured
sequence capacity — and exits nonzero naming every mismatch. It allocates nothing
on the device and loads no model. Discovering a wrong Python here costs nothing;
discovering it inside the worker costs a billed pod.

Its constants are not maintained by hand against a memory of the worker: a test
parses the pin block, the platform guard and the memory floor out of
`scripts/run_corpus_training_worker.py` and asserts they match, so the two cannot
silently diverge.

A live read of Runpod's official pod templates on October 29 found **none shipping
PyTorch 2.10, and none stating a Python version in its image tag** — the newest is
2.9.0. Upgrading Torch in place inside a 2.8 or 2.9 template is the dependency
fight that hash-locked installs exist to avoid, so
`configs/Dockerfile.p1-training-runtime` is provided: an Ubuntu 24.04 CUDA base
that asserts Python 3.12, installs the existing hash-locked runtime and PEFT
supplement, and fails its own build if the preflight does not pass. It bakes in no
weights, no corpus and no credentials.

**That Dockerfile has never been built or run.** It is a reviewed starting point,
not a qualified image, and its CUDA base tag must be checked against the pod's
host driver first — the available cards reported host CUDA 13.2 on October 29. The
acceptance test is `verify_training_runtime.py` exiting zero inside the built
image on the intended GPU; until that happens the image is unqualified.

## 7. Retained artifacts

| Package | Local receipts | R2 artifact manifest SHA256 |
|---|---|---|
| Admitted Corpus072 bundle | — (bytes live only in R2) | `2959faedf43b2f0d77bdc0f160085bd2cf863f843d7e0404cc1d20178289014a` |
| Admission receipts and two-layer verification | `evidence/data/corpus072-admission-001/` | `12079b1854b8979221a8dfc42790b17cc465dc1e59b512a5e4daa2426dd1aa9e` |
| Screened task pool, cohorts and pinned source metadata | `evidence/data/task-pool-v2-python-001/` | `c841921f7fea1812cbb9609b2dec2e71d72af4bebaf4718cecb7c089398b4ea5` (pool, 53,181,615 bytes) and `23f20dea57d3eee23d03a1b8f6e351effece65b7e0d7787c1ab58788d196d96b` (receipts) |
| Campaign plan | `evidence/data/campaign-plan-001/` | `f58b0f893da37fa7daced614b9ef0a7638bc63262b8f3f567f4c5ded7b25eee0` |

Receipts are audit records, not cryptographic proof of a remote service's behaviour. Keep the artifact manifest with the receipt, never inside the bundle it describes.

## 8. Remaining work before a GPU run

This cycle removed the admission blocker and the data-scale blocker's CPU half. These remain, in order:

1. **Throughput measurement.** No figure in this project measures tokens per second for this configuration at a realistic sequence length. The previously recorded 67,231 MiB device-memory reading came from a **24-token** fixture: it constrains memory, not throughput. `forecast_campaign` refuses to produce a duration or cost without a measured rate, so one bounded run must come first.
2. **Long-sequence memory.** The corpus's longest example is 24,366 input tokens. Peak memory at that length is unmeasured. An 80 GB card leaves little slack over a peak measured at 24 tokens.
3. **Build and qualify the training image.** No official Runpod template ships the pinned Torch 2.10 / Python 3.12 combination. Build `configs/Dockerfile.p1-training-runtime`, check its CUDA base against the pod's host driver, and require `verify_training_runtime.py` to exit zero inside it on the intended GPU.
4. **Pull environments and replay.** The 2,966 selected tasks need their published images pulled, baseline and reference outcomes graded, and native trajectories captured through the official runtime before any of them becomes a training example.
5. **Rights review on the new pool.** Licence labels are screened, not cleared. The 348 rows with no licence field and the 1,706 placeholders are correctly withheld; the 4,818 eligible rows still need the review the gate name describes.
6. **Freeze the confirmation cohort** before any optimization touches the train cohort, and record the freeze.
7. **Tokenize, mask and assemble** the replayed trajectories into a new quarantine corpus, then admit it through the same four gates on its own evidence. Corpus072's admission says nothing about a successor corpus.
8. **Runpod preflight on a fresh budget.** See the compute section of the data-source research report for live account state, including a constraint discovered this cycle: the data centre holding the existing 201 GB network volume no longer offers network volumes, so the volume and GPU data centres must now be chosen together.

## 9. Operating the new commands

```sh
# Stage a corpus from R2 and prove its identity before use.
python3 scripts/stage_corpus_from_r2.py \
  --artifact-manifest <manifest.json> --artifact-manifest-sha256 <sha> \
  --destination <new-dir> --corpus-sha256 <sha> --content-sha256 <sha> \
  --expected-status admitted --purpose training \
  --output <new-receipt-dir> --prefix artifacts/v1 --env-file .env \
  --max-restore-bytes <bytes>

# Promote a quarantined corpus; every gate must be supplied explicitly.
python3 scripts/admit_training_corpus.py \
  --corpus <quarantine-dir> --corpus-sha256 <sha> \
  --destination <new-dir> --output <new-receipt-dir> --reviewer "<accountable identity>" \
  --rights-and-attribution <doc.json> --split-isolation <doc.json> \
  --runtime-qualification <doc.json> --task-alignment <reviews.json> \
  [--<gate>-support <doc.json>]

# Check a host against the worker's preconditions before spending GPU time.
python3 scripts/verify_training_runtime.py \
  --output <new-receipt-dir> \
  --worker-config configs/p1-corpus-qualification.json \
  --longest-input-tokens <from the corpus audit>

# Require both verification layers to agree.
python3 scripts/verify_admitted_corpus.py \
  --corpus <dir> --corpus-sha256 <sha> --content-sha256 <sha> \
  --expected-status admitted --purpose training --schedule <schedule.json> \
  --output <new-receipt-dir>

# Plan a token budget; a forecast needs a measured throughput.
python3 scripts/plan_training_campaign.py \
  --corpus <dir> --corpus-sha256 <sha> \
  --target-tokens 50000000 --basis supervised_tokens --max-epochs 200 \
  --candidates 3 --output <new-dir>

# Screen and select a public task pool with disjoint cohorts.
python3 scripts/build_task_pool.py \
  --metadata <metadata.jsonl> --metadata-sha256 <sha> \
  --dataset <owner/dataset> --revision <40-char-sha> --language python \
  --exposure-ledger <development-exposure.json> \
  --seed 7401 --target-tasks 4818 --max-per-repository 12 --max-per-owner 24 \
  --cohort train=7/10 --cohort development=3/20 --cohort confirmation=3/20 \
  --output <new-dir>
```

Every one of these commands refuses to overwrite an existing output directory, records the identities of the implementation files it ran, and writes no passing receipt on failure.
