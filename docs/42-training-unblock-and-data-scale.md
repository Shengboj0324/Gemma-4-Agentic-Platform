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
| Local regression: 671 tests | **904 tests, zero skips, Torch enabled** |
| No way to check a host before the worker billed for the failure | `zenithsync/runtime_preflight.py` + `scripts/verify_training_runtime.py`, with tests that assert the pins match the worker source |
| New code reviewed only by its author | 35 findings from two independent adversarial reviews, all substantive ones fixed, each with a regression test |
| No single command proved a run could start from the bucket | `scripts/verify_r2_training_readiness.py` — corpus, both layers, tokenizer assets by digest, all 8 model files, schedule digest, worker preflight |
| ~1.03 GiB of local evidence had no bytes in the bucket | `zenithsync/evidence_shipment.py` + `scripts/ship_evidence_to_r2.py` |

## 2. Corpus072 is admitted

Promotion is immutable: the quarantined corpus is never edited. A complete new tree is staged, example files and evidence documents are copied with post-copy identity verification, one receipt per gate is written, and the result is published atomically **only after the strict training loader accepts it with `purpose='training'`**.

| Quantity | Value |
|---|---|
| Source (quarantine) manifest SHA256 | `42da2d372f908d00b72a3f7d89af9b5fa082f8caeb8a4307bd77cfc363a2de75` |
| Admitted manifest SHA256 | `fa984ca3ff1006e2cf7817a8ee67f613fb4e37a5b603bdc6d5e61b586f623887` |
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
3. `publish_corpus_to_r2.py` published the admitted corpus to `artifacts/v1` — 115 files, 10,782,715 bytes, artifact manifest `50c8ee9398ff6c3a186ef558c08c72365060d41e3e796950cd5d7dd2b8eab323`.
4. `stage_corpus_from_r2.py` restored it again with `--purpose training` and the loader reported `training_admitted: true`.
5. `preflight_corpus_run` — the real worker's own preflight — accepted the staged tree, schedule and `configs/p1-corpus-qualification.json`.

No corpus bytes are retained on the development machine: every step above ran in a session scratch directory. The bucket now holds 17,058+ objects over roughly 34.5 GiB, and the new packages are listed in section 6.

`zenithsync/r2_client.py` centralises credential loading and exposes only `get_object`, `put_object`, `head_object` and `upload_file`, so an injected client cannot delete, list or reconfigure a bucket. Credentials are read from the process environment or an explicit dotenv file and never returned, logged or written into a receipt.

## 3a. Everything a run needs is in the bucket, and one command proves it

`scripts/verify_r2_training_readiness.py` is the end-to-end integration check.
It reads nothing local except the artifact manifest it is given and the
credentials, then:

1. restores the admitted corpus from R2 and requires the declared manifest
   digest, content identity and admission status to match;
2. runs the independent audit layer and requires agreement with the loader on
   every shared quantity;
3. requires the loader to offer exactly the audited training set, checks each
   row's split, and re-hashes every fetched token array;
4. fetches each tokenizer asset the corpus binds, **by content digest**, and
   verifies its bytes — without these the corpus is untrainable;
5. confirms every file of the model manifest is present in the bucket at its
   declared size, by metadata rather than by download;
6. regenerates the exposure schedule and requires the declared digest exactly;
7. runs the real worker's own `preflight_corpus_run` against the restored tree.

Verified result:

| Check | Result |
|---|---|
| Corpus restored from R2 | 115 files, 10,783,215 bytes |
| Two layers agree | yes, zero disagreements |
| Examples refetched, split-checked and re-hashed | 51 |
| Tokenizer assets fetched by digest and verified | `chat_template.jinja`, `tokenizer.json`, `tokenizer_config.json` |
| Model files present in the bucket | **8 files, 23,297,590,856 bytes** |
| Schedule regenerated to the declared digest | `4664ecf6…` |
| Worker preflight | passed |

The last row of the model table is the one that was not previously established
anywhere: **the full 23,265,352,448-byte quantized `model.safetensors` is in the
bucket**, along with every other model file, and the three tokenizer assets the
corpus binds are byte-identical to the ones in the model manifest. The weights
are not on the development machine — the docs recorded them as archived, and the
machine has only ~14 GiB free, so they could not be re-downloaded here even if
wanted. Presence in the bucket is what makes a run possible at all.

The model check is deliberately presence-and-size from remote metadata. It does
not re-hash 21 GiB on every readiness check, so it is not a fresh integrity proof
of the checkpoint. A pass means the data path is complete and self-consistent
from the bucket; it says nothing about rights, host capability, model fit or
learned performance.

### Shipping the rest of the evidence

A content-coverage audit found **15,426 local files, about 1.03 GiB, whose bytes
had no counterpart in the bucket** — retained deployment bundles, replay
contexts, dependency wheels, Debian packages and recovered working artifacts, in
both the repository's `evidence/` and `reproduction/` trees and the recovered
material held outside the repository.

`scripts/ship_evidence_to_r2.py` closes that gap. It groups a tree into packages
at a declared depth, publishes each under its own content-addressed manifest, and
writes an index saying where every package landed so any one can be restored
later. Three things it refuses rather than works around:

* A package containing a **credential path** (`.env`, `.ssh`, `.aws`, `.kaggle`)
  is refused whole. Shipping it with the file removed would publish a bundle
  whose manifest disagrees with the directory it was built from. A test plants a
  `.env` and asserts nothing is uploaded.
* A package containing a **symlink or non-regular file** is refused whole, since
  the inventory contract covers regular files and a symlink's target is not part
  of the bundle.
* A package **over its byte ceiling** is refused, so one unexpectedly large
  directory cannot consume the whole transfer budget.

`.git` directories are **skipped, not refused** — a distinction that mattered in
practice. A repository checkout's working tree *is* the retained evidence, while
its VCS metadata is reproducible from the pinned commit and is a place a remote
URL could carry a credential. Treating `.git` as a credential path refused six
genuine evidence packages outright; skipping it ships their working trees and
their metadata reaches no bucket. Reconstructable caches and virtual
environments are skipped on the same reasoning.

Shipping is idempotent by construction: publication verifies what the bucket
already holds by reading it back and uploads only what is genuinely absent. A
re-run of an already-shipped tree reports every file as reused.

That property was exercised for real rather than assumed, and the exercise found
a hazard worth fixing.

A `pgrep` pattern of mine misread the first long run as dead, so a second run was
started while the first was still going. Both then uploaded the same
content-addressed keys, and the first run aborted with an `IntegrityError` from
the object store's own readback guard. That guard was doing its job: a readback
that races an in-flight overwrite of the same key can return a length or digest
matching neither writer. Because the keys are content-addressed, both writers
were putting *identical* bytes, so this was a false alarm rather than corruption
— but at the point it is raised it is indistinguishable from a real integrity
failure, which means it has to be prevented rather than tolerated.

`shipment_lock` now provides that mutual exclusion: an `O_EXCL` lock file keyed by
bucket and prefix, held for the whole publishing run. A second publisher against
the same prefix is refused by name, with the holder's label, PID and start time.
A lock whose recorded process is gone is reclaimed, since a killed publisher
leaves nothing to clean up, and an unreadable lock is reclaimed rather than
blocking forever. Verified against the live bucket: one run holds the lock and a
second exits with `ShipmentLockError` and no receipt.

It applies to **every** command that writes to a prefix, not only the bulk
shipment — `publish_corpus_to_r2.py` takes it too. The hazard is two writers of
the same content-addressed key, and which command they are does not matter; a
test asserts each publisher CLI takes the lock so a future one cannot forget.

The resume property itself held exactly as designed. Each package commits its
manifest only after every blob it names has been read back and verified, so the
aborted run left complete published packages plus, at worst, uploaded blobs no
manifest referenced yet; those are content-addressed and were reused by the next
run. There was no partially published package and nothing to clean up.

Concurrency is per-package. Sequentially the shipment ran at about 2.6 files per
second, which is hours for a tree this size; `--workers` publishes different
packages at once while each package keeps its full sequential contract — verify
the tree, read back or upload every blob, verify again, commit the manifest.
Admission against the byte ceiling is decided up front in sorted order, so the
set of shipped packages does not depend on worker scheduling, and a test asserts
a 1-worker and a 4-worker run produce byte-identical results including the index
digest. Two packages sharing a blob may both upload it; publication is
content-addressed and verified by readback, so that is idempotent rather than a
race. The connection pool is sized to the worker count, or packages block on the
pool instead of the network.

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

| `tests/test_evidence_shipment.py` | 30 | Every file lands in exactly one package at any depth; caches and `.git` skipped but the working tree still shipped; credential paths, symlinks, oversized and empty packages each refused whole with their reason; re-shipping reuses every object; a planning run publishes nothing; a 1-worker and a 4-worker run produce identical results including the index digest; the index locates every package; coverage reports exactly what is absent; and a second shipment against the same bucket prefix is refused by name while a stale or unreadable lock is reclaimed rather than blocking forever. |
| `tests/test_r2_client.py` | 9 | A missing-field error names fields and never values; blank treated as missing; which source supplied each field; the exposed surface is exactly the four declared operations and no destructive one; upload counting exact under eight concurrent threads. |
| `tests/test_repository_hygiene.py` | 10 | That all three layers keeping the live credential file out of Git and out of the bucket still hold: the ignore rules, the object store's manifest refusal, and shipment's package refusal. It also scans every tracked text file for live-secret patterns, requires no tracked file to carry private-key *material* (which keeps the scanner-fixture exemption honest), and refuses a stale or unnecessary exemption. |
| `tests/test_r2_readiness_helpers.py` | 8 | A blob whose bytes differ, or that is longer or shorter than declared, is refused; the ceiling is checked before any request; presence is confirmed from metadata with no `get_object` at all, so a 21 GiB checkpoint is never streamed by a readiness check. |
| `tests/test_runtime_preflight.py` | 35 | That the preflight pins are byte-identical to the worker's own (parsed out of `run_corpus_training_worker.py`, so the two cannot drift apart); local build tags stripped before comparison; absent packages, wrong platform, wrong Python, insufficient device memory and an over-capacity example each reported with every problem kept. |

Full local suite: **904 passed, zero skips, Torch tests enabled, 27.076 seconds**, run as
`ZENITHSYNC_TEST_TORCH=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 <qualified-python> -m unittest discover -s tests`.

**One caveat on that suite, found by the new preflight.** The development
interpreter used for these runs has torch **2.14.1**, not the worker's pinned
**2.10.0**, and `compressed-tensors` is absent from it entirely. The Torch-dependent
tests therefore pass on a *different* Torch than the training stack. That is a
real limitation on what the suite establishes, and it is exactly what
`scripts/verify_training_runtime.py` is for: run on this machine it exits nonzero
and names both mismatches. The reduced-model numerical checks remain valid for the
interpreter that ran them; they are not evidence about torch 2.10.0 kernels.

### Adversarial review and what it found

An independent reader was given the seven new modules, the authoritative loader
and the house conventions, and asked to break them. It reported **16 findings**,
every one of which was real; all are fixed, and each fix carries a regression
test. Recording them matters more than recording the clean result, because they
show which invariants were only *stated* until something tried to violate them.

**Two confirmed path escapes in the second verification layer.** `corpus_audit`
resolved a declared path as `root / reference['path']` with no canonical-path
check, no containment check, and a symlink test covering only the final
component — three checks the loader has and the audit did not re-derive. Both
escapes returned `training_admitted: True` from the audit on a corpus the loader
*refuses*:

* An evidence path of `../planted/ev.json`, with the receipt-to-manifest chain
  re-signed, pointed outside the tree entirely.
* An entire gate directory moved out of the tree and replaced with a symlink,
  leaving every declared path byte-identical and fully canonical.

This was the most serious class of defect available here: the audit's whole
purpose is to establish that the corpus tree contains the corpus, and it did
not. Both are now refused, both are regression-tested, and both tests also
assert that the loader refuses the same tree, so the layers are shown to agree
rather than assumed to. The audit's byte ceilings were also looser than the
loader's; it now re-derives the loader's 1 MiB receipt, 16 MiB evidence, 16 MiB
manifest and 1 GiB aggregate limits, and the test asserts those constants
against the loader's source.

**Two translation rules that were not semantically justified.** The source
`str_replace_editor` accepts a *directory* for `view` and lists it, while the
official `read_file` reads a file — so a directory listing was being turned into
a file read. And `execute_bash` documents `C-c` as a control character sent to a
running process, so `{'command': 'C-c'}` was being translated into a literal
shell command that would run a nonexistent program instead of interrupting one.
The module had correctly refused `is_input` for exactly the reasoning that
applies to `C-c`. Both are now refused. The directory case is resolved exactly
when the caller supplies `file_paths` — the set of files in the pinned snapshot
— and otherwise by a declared suffix heuristic that errs toward refusal, so
extensionless files such as `Makefile` are refused rather than mistranslated.

**Promotion could write into the corpus it promised not to edit.** A destination
nested inside `source_root` was accepted, putting the admitted tree and its
staging directory inside the quarantined corpus, which then failed its own
publish with extra files. The symmetric guard already existed for evidence
documents but not for the destination. Now refused, and the test asserts the
source directory listing is unchanged afterwards.

**A verification receipt could attest coverage for an unrunnable schedule.**
`verify_schedule_coverage` never re-derived the schedule's own identity, so a
schedule with a stale `schedule_sha256` — one `iter_updates` refuses to execute
— was reported as `coverage_exact: True`. It now rebuilds the schedule through
`make_schedule` and requires an exact match, and the test confirms the iterator
refuses the same object.

**A rejected restore blocked every retry.** The object store promotes the tree
before `restore_corpus` runs its four corpus checks, so a content-identity
mismatch left a rejected corpus at the destination and made the next attempt
fail with `FileExistsError`. The tree is now removed before the error
propagates, and a failure to remove it is reported rather than masked.

**The evidence-to-corpus binding was not re-derivable.** Promotion checked each
evidence document's declared corpus against the quarantine manifest, but that
manifest was not recorded anywhere in the admitted tree, so neither layer could
re-derive the check afterwards. Each gate receipt now records
`reviewed_against_manifest`, and the audit requires every evidence document that
declares a corpus to declare that same one. Writing the test for this surfaced a
further defect of my own: a shadowed local variable had been putting the
task-alignment coverage set into the gate report where the manifest identity
belonged.

**The rest.** A missing `path` raised a bare `KeyError`, which both broke the
stable-reason-code contract and aborted a whole shard screen instead of counting
one refusal; `audit_translation` now maps any unexpected exception type to a
named reason. `finish` was the only tool with no field-set check and accepted
arbitrary arguments. One rule name claimed a whole-file read for a call that
reads from a line. `execute_bash` used one reason code for three different
situations, so an exporter that writes schema defaults explicitly would have
yielded zero translatable trajectories with no way to tell why.
`padding_overhead` raised `ZeroDivisionError` and `diversity_limits` raised
`IndexError` on empty input rather than `ValueError`, and neither enforced unique
example identities, so a duplicated row could inflate a measured concentration
share that `account_tokens` would have refused outright. A float rate too small
to represent was rounded to zero and then misreported as nonpositive. A symlink
guard was vacuous because the path had already been resolved — the honest fix
was to delete it and document that resolution is the containment mechanism,
rather than add a check that rejects ordinary system symlinks.

**Four tests that passed for the wrong reason** were rewritten to assert the
behaviour rather than a hardcoded flag: `repository_disjoint`, `owner_disjoint`
and `owner_indivisible` are literal `True` in the return value and would have
passed with the entire disjointness verification loop deleted, so the test now
intersects the cohort assignments itself. The receipt-binding test tripped an
identity check before reaching the binding check it named, so the chain is now
re-signed to make the intended check fire.

**What the reviewer could not break.** 3,000 randomised selection trials found
no cap breach, no duplicate and no shortfall error; 2,000 randomised cohort
splits lost no task and split no owner; 4,000 randomised mixture allocations
summed exactly to their total with every rounding adjustment in {0, 1}; and no
input was found on which both verification layers accept and disagree. Promotion
could not be made to publish a tree the loader rejects, and transport could not
be made to carry an extra or missing object.

### Second review: the command-line tools

The first review covered the library modules. The CLIs and two helpers were not
reviewed, so they were handed to a second independent reader, which found **19
findings plus several minor ones**. All of the substantive ones are fixed. Four
could have cost real money or produced a false assurance:

**A missing `nvidia-smi` turned a worker-fatal condition into a passing
preflight.** `device_report` swallowed `OSError` into `device_exclusive: None`,
and the CLI only reacted to `False`, so a host without `nvidia-smi` on PATH got
`runtime_preflight_passed` and exit 0 — and then the worker, which makes the
same query with `check=True`, died after the pod was already billing. That is
the exact inversion the module exists to prevent. A query that cannot run is now
a failure, with the reason recorded.

**The same check failed a *healthy* host from the other direction.** The worker
excludes its own PID; the preflight treated any PID as foreign. Reading free
memory initialises CUDA and creates a context, so the preflight appeared in its
own query and reported itself as a competing process. It now excludes its own
PID exactly as the worker does, and a test asserts the worker still does.

**`device_report` could raise instead of returning a finding.** Only
`import torch` was guarded; `device_count`, `mem_get_info`, `get_device_name`
and `get_device_capability` can all raise on a real host — driver mismatch, ECC
disabled, `CUDA error: unknown error`. The CLI promises a receipt either way, and
a raise produced none. All of them are guarded now, and the exit codes are
distinguishable: 0 satisfied, 1 a check failed and a receipt exists, 2 bad
arguments, 3 the run itself failed and no receipt exists.

**The two-layer check was blind to the one invariant it exists for.** The refetch
loop compared each example against *its own* audit row, so a held-out example
substituted into the training set matched itself on split, task and both token
counts, and a one-for-one substitution kept the count right. The reviewer
demonstrated it end to end: a 2-train/1-development corpus with the loader
patched to return a development example in place of a train one printed
`two_layer_corpus_verification_passed` under a receipt whose scope claims the
layers agree on split isolation.

That check now compares the *set* of identities the loader offers against the set
the audit says belongs to the purpose, asserts each row's split explicitly, and
re-hashes every fetched token array against the digest the audit computed. It
lives in `zenithsync.corpus_audit.verify_loader_offers` so it is directly
testable, and the reviewer's scenario is a regression test.

**The rest, by theme.** The exposure ledger was the only unpinned input in the
whole toolchain — the one thing that makes a selected pool arguably unseen — so
`--exposure-ledger-sha256` is now required alongside it, and the ledger's
`receipt_files_read` and `skipped_receipts` are recorded because they are what
make it a lower bound. `build_task_pool` checked its metadata digest and then
rebound the variable to a fresh `file_record` taken inside the reader, leaving
the pin unenforced on the bytes actually parsed; the expected digest now goes
into the reader. Four reports wrote sidecar files without binding them, so an
edited `selection.json` could not be contradicted by its own report; sidecars are
now written first and bound by hash. Four `SOURCES` lists omitted modules that
had executed — worst of all `training_batch.py`, which produces the very
`supervised_tokens` figure the two-layer receipt attests agreement on.
`admit_training_corpus` snapshotted its sources *after* the work and had no
failure handler, so a checkout during a long promotion would have been recorded
as the code that ran. Five CLIs created their output directory before validating
arguments and left it behind on failure, blocking the corrected retry. Cost
inputs were silently discarded when the throughput flag was missing, so a typo
produced a plausible plan with no forecast; that is now an error naming every
missing flag. `--batch-width-tokens 0` was silently treated as absent.
`--cohort` mode mixing was refused only after 32,000 rows had been screened.
`publish_corpus_to_r2` defaulted to the quarantine prefix even for an admitted
corpus, which would re-upload every object under the correct one. The artifact
manifest was the one input read with no byte ceiling. And the two planning tools
always exited 0, so an infeasible target or a breached concentration cap was
invisible to a calling script.

**`r2_client` had an honesty problem rather than a bug.** Its docstring said
credentials are "never logged, returned or written to a receipt" while
`load_credentials` returns them in a plain dict — accurate for logs and receipts,
false for the return value. The docstring now says exactly what is true, and the
value is documented as a secret to keep in a local. The "bounded" client is also
convention, not a sandbox: `_client` is reachable, and the reviewer demonstrated
`store.client._client.delete_object(...)` working. That is now stated rather than
implied, with the declared operation set asserted by a test. Separately,
`load_credentials` now reports which source supplied each field, because the
process environment silently overrides `--env-file` and a stale exported
`R2_BUCKET_NAME` would otherwise publish to the wrong bucket undetectably.

**And three weak tests.** One restated the constants it was meant to check and
passed with `check_platform` deleted; it now derives the worker's values and
compares. One grepped the literal string `'free < 70*1024**3'`, so reformatting
the worker would fail a test about behaviour; it now parses the arithmetic. One
exercised a path the only production caller cannot reach. `device_report` had no
test at all, which is why three of the four severe findings lived in it; it now
has six, driven by a stubbed torch and a stubbed `subprocess.run`.

Eight files had no test coverage whatsoever. `r2_client` and the readiness
helpers now do; the remaining CLIs are covered through the library functions they
drive plus the live end-to-end chain below.

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
| Admitted Corpus072 bundle | — (bytes live only in R2) | `50c8ee9398ff6c3a186ef558c08c72365060d41e3e796950cd5d7dd2b8eab323` |
| Admission receipts and two-layer verification | `evidence/data/corpus072-admission-001/` | `e1e2114c0da57d658179254f55c03aa1aea2d71a3712a088c447cb84948233ad` |
| Screened task pool, cohorts and pinned source metadata | `evidence/data/task-pool-v2-python-001/` | `c841921f7fea1812cbb9609b2dec2e71d72af4bebaf4718cecb7c089398b4ea5` (pool, 53,181,615 bytes) and `93e73c6c5bafe0af8f31859fffde36edc4b407ae045aa18b5214e28fa13657d0` (receipts) |
| Campaign plan | `evidence/data/campaign-plan-001/` | `3d0bdc9d4fbd1499eb113f9309728798a3a5a655018e361cfcb4c780451434f7` |

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

## 10. Operating the shipment and readiness commands

```sh
# See what a shipment would do, without spending bandwidth.
python3 scripts/ship_evidence_to_r2.py --plan \
  --tree evidence --tree reproduction --package-depth 2 \
  --source-prefix zenithsync-evidence --revision 001 --output <new-dir>

# Ship it. Re-running is safe: present objects are verified, not re-uploaded.
python3 scripts/ship_evidence_to_r2.py \
  --tree evidence --tree reproduction --package-depth 2 --workers 16 \
  --source-prefix zenithsync-evidence --revision 001 \
  --output <new-dir> --prefix artifacts/v1 --env-file .env

# Prove from the bucket alone that a run has everything it needs.
python3 scripts/verify_r2_training_readiness.py \
  --artifact-manifest evidence/data/corpus072-admission-001/r2-artifact-manifest.json \
  --model-manifest evidence/p1/model-intake-001/model-manifest.json \
  --corpus-sha256 <sha> --content-sha256 <sha> \
  --worker-config configs/p1-corpus-qualification.json \
  --schedule-seed 7401 --schedule-sha256 <sha> \
  --output <new-dir> --prefix artifacts/v1 --env-file .env
```

Exit codes now carry meaning where a calling script needs them.
`verify_training_runtime.py`: 0 satisfied, 1 a check failed and a receipt was
written, 2 bad arguments, 3 the run failed and no receipt exists.
`plan_training_campaign.py` exits 1 when the token target is infeasible within
the declared epochs or a repository group breaches the concentration cap.
`build_task_pool.py` exits 1 when the selection falls short of its target. Every
one of these commands refuses an existing output directory, validates its
arguments before creating anything, removes the directory if the run fails, and
writes no passing receipt on failure.
