# Runpod training runbook, and what the first billed session measured

**The session ran on 2026-11-12 and is finished.** Scope approved: build,
qualify, measure, stop, under a $10 cap. Actual spend **≈ $1.32** on two
A100-SXM4-80GB pods at $2.19/hour, both terminated, both temporary network
volumes deleted. Nothing is still billing from this project.

**Headline result: the pinned stack qualifies on the device, and the corpus does
not fit an 80 GB A100.** The first training update died with
`torch.OutOfMemoryError` requesting **35.39 GiB for a single attention score
tensor**, and the cause is identified precisely — see §9.

Results are in §9; §§1–8 are the plan as written beforehand and are kept
unchanged, because a plan rewritten after the fact to match the outcome records
nothing.

---

## 1. What still needs a GPU, and why

| Item | Why a GPU is unavoidable |
|---|---|
| Throughput measurement | Tokens per second is a property of the device and the sequence length. `forecast_campaign` refuses to produce a duration or cost without a measured rate, so nothing downstream can be planned until one exists. |
| Peak memory at full sequence length | The corpus's longest example is **24,366 input tokens**. The only recorded device figure, 67,231 MiB, came from a **24-token** fixture. The gap between those two is the whole question. |
| Image qualification | `scripts/verify_training_runtime.py` checks the device as well as the interpreter. It can pass the package half anywhere; the device half needs the device. |
| Environment pull and trajectory capture | 2,845 task images, each pulled, run and graded. This is bandwidth and CPU rather than GPU, but it is not local work: it needs a Linux host with Docker and a large disk. |
| Candidate comparison | Requires a trained adapter, which requires training. |

Everything that could be done without a GPU has been done, and the two findings
that came out of doing it are in §3.

## 2. Hardware the worker will accept

`zenithsync/runtime_preflight.py` refuses to start unless it sees:

- Linux, CPython exactly **3.12**
- torch **2.10.0**, transformers **5.13.1**, compressed-tensors **0.15.0.1**, peft **0.21.2**
- at least **70 GiB free device memory** (`REQUIRED_FREE_DEVICE_BYTES`)

That last line disqualifies the L4. **The competition's L4×4 runtime is an
inference constraint, not a training one** — conflating the two would send this
session to a card the worker rejects before the first update. Previous sessions
in this project ran on an A100-SXM4-80GB (81,920 MiB reported) and an H100 80GB
HBM3 (81,559 MiB); both clear 70 GiB. The A100 80GB was observed at **$1.79/hour
on 2026-10-09**; prices move, so read the live rate before launching rather than
trusting that figure.

Reconstructed dense weights total 60.88 GiB, measured load was 19.63 GiB, and
the adapter is 30,607,360 parameters. The unknown is activation memory at 24,366
tokens, which is exactly what phase 2 measures.

## 3. What the no-GPU preparation changed

**The image's lock could not have built.** `scripts/verify_lock_wheels.py`
audited every pin against the package index. Four pins in
`serving-linux-py312-httpfix.lock.txt` would have failed `--require-hashes`
after the build had already downloaded gigabytes: `vllm 0.19.1`, whose locked
digest matches none of the files the index serves for that version, and
`adk-eval-core`, `adk-submission` and `swegemma`, which are competition-private
and absent from the public index. A fifth, `pydantic-extra-types 2.11.2`, is
yanked upstream.

It also retired the largest unknown about the image: **the pinned training stack
is available for the target platform**, by exact digest — `torch 2.10.0` as
`torch-2.10.0-3-cp312-cp312-manylinux_2_28_x86_64.whl`, with transformers,
compressed-tensors and peft as pure-Python wheels.

None of the five problem pins is needed to train, so
`requirements/training-linux-py312.lock.txt` is now the dependency closure of
the worker's four required packages over the serving lock's own pins: **61 pins
instead of 251, all 61 confirmed present on the index by digest, 27 platform
wheels and 34 pure, no source distributions.** The Dockerfile installs that.

**The rights review is done.** See §6.

## 4. Phase 1 — build and qualify the image (billed, short)

The build needs a Linux amd64 host with Docker. It does not need a GPU; the
qualification step does.

```bash
docker build -f configs/Dockerfile.p1-training-runtime \
  -t <registry>/zenithsync-training:<tag> .
docker run --rm --gpus all <registry>/zenithsync-training:<tag> \
  python3 scripts/verify_training_runtime.py --output /tmp/preflight
```

The second command is the acceptance test, and its exit code is the gate: **0
satisfied, 1 a check failed, 2 bad arguments, 3 the run failed.** Anything other
than 0 stops the session here. The in-build `--skip-device` invocation already
fails the build on a wrong Python or an unpinned Torch, so a failure at this step
is specifically a device or driver problem.

Check the CUDA base tag against the host driver before building. The available
cards reported host CUDA 13.2 on 2026-10-29 and the Dockerfile pins
`nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04`; a base newer than the host driver
will not run.

**Stop condition:** if qualification does not exit 0 within one hour of billed
time, stop the pod and report. Do not begin modifying pins on a live pod — that
is the dependency fight the locks exist to avoid.

## 5. Phase 2 — the two measurements (billed, bounded)

Stage the data from R2. Nothing is copied from this machine:

```bash
python3 scripts/fetch_manifest_from_r2.py --env-file .env --output corpus-manifest \
  --manifest-sha256 326c9cd0fe69fb5c512513f5d037cbd075ace72670a4192e0eb2b7fee49d5cba
python3 scripts/stage_corpus_from_r2.py \
  --artifact-manifest corpus-manifest/artifact-manifest.json \
  --artifact-manifest-sha256 326c9cd0fe69fb5c512513f5d037cbd075ace72670a4192e0eb2b7fee49d5cba \
  --destination /workspace/corpus --expected-status admitted --purpose training \
  --corpus-sha256  2853b558f4bba36e5b2a1bf22ee23c5028a73da06e20d3d94919b23a994ca6fa \
  --content-sha256 c081880c71b9f78ffb4fdcf319d0959e8d7dfcb39878b8ac06f510f2d088f103 \
  --output stage --max-restore-bytes 1073741824 --env-file .env
```

Then one bounded session through the supervisor, not the worker directly. The
worker already records what both measurements need: `run_training_session`
returns `elapsed_seconds` and the update count, and the worker adds
`peak_allocated_bytes`, `peak_reserved_bytes` and a device-memory monitor
summary. **No new measurement code is required** — a config with a raised
`max_updates` and a `max_seconds` deadline is the whole change.

Two facts come out of one run:

- **Throughput** = processed supervised tokens ÷ `elapsed_seconds`. That becomes
  `measured_tokens_per_second` for `forecast_campaign`, with the worker receipt
  named as `measurement_evidence`.
- **Peak memory**, from `peak_allocated_bytes` and `peak_reserved_bytes`. The
  schedule covers the corpus, so the 24,366-token example is included; confirm
  from the schedule report that it was actually reached before quoting a peak as
  the peak.

**Stop conditions, all hard:** `max_seconds` bounds the session in-process; the
pod gets a wall-clock deadline of its own; any non-finite loss, any gradient on
a frozen parameter or any non-finite parameter after a step aborts the run by
design. A deadline does not stop the provider's meter — stop the pod explicitly.

## 6. Rights review — complete, and it found real problems

`scripts/review_pool_rights.py` fetched the licence file for **each of the 2,966
selected tasks at that task's own pinned base commit** — per commit, not per
repository, because a licence can change — hashed the bytes, and compared the
text against the label the dataset metadata carries.

**2,845 of 2,966 tasks confirmed.** 121 withheld, in four kinds, each named with
its tasks in the summary rather than reduced to a count. The categories that
matter:

- **Copyleft under a permissive label.** `AgnostiqHQ/covalent` is labelled
  `Apache-2.0` and carries **AGPL-3.0**. `GridTools/gt4py` and `SciTools/cartopy`
  are labelled `BSD-3-Clause` and carry **GPL-3.0**. `sciunto-org/python-bibtexparser`
  is labelled `MIT` and carries **LGPL-3.0**. Training on the pool's labels would
  have put copyleft code into a corpus screened as permissive.
- **Family mismatches**: BSD-3 labels over BSD-2 text, Apache labels over MIT
  text, and so on. Permissive either way, but the label is wrong and the
  attribution obligations differ.
- **No licence file at the pinned commit**, and **texts matching no known
  family** — including one repository whose "licence file" is a 19-byte path
  pointing somewhere else.

Getting this right took four passes, and the three wrong ones are instructive
because each failed in the same direction: the GNU licences cite each other.
GPL-3.0 §13 names the Affero licence and its closing advice names the Lesser
licence, so matching on a licence's *name* read plain GPL-3.0 files first as
AGPL-3.0 and then as LGPL-3.0. Matching the document's own contiguous title line
is what finally separated them. The detector refuses to guess: a text matching
no family, or more than one, withholds the task rather than resolving in the
permissive direction.

**What this establishes:** at each task's pinned commit, the repository root
carried a licence file whose text is the declared family, and those exact bytes
were observed and hashed. **What it does not:** that a repository owns
everything it distributes, that vendored third-party code inside it carries the
same terms, that contributors assigned rights, or that any particular use is
permitted. `rights_cleared` stays `false` in every receipt.

## 7. What is still not established after all of this

- **No throughput figure exists.** Phase 2 produces the first one.
- **No sustained training run, and no trained adapter.**
- **No learned improvement, and no comparison against any other agent.**
- **Peak memory at full sequence length is unmeasured.**
- **Corpus072 is 51 tasks, all `train`, all development-exposed.** A 50M-target
  run is 190.4 repetitions of the same data. The 2,845 rights-confirmed pool
  tasks are the answer to that, and they are not yet trajectories: eligibility is
  not a task.
- **The image has never been built.** Every pin is known to exist; that is not
  the same as the wheels resolving together, importing, or running on a GPU.

## 8. The permission being requested

Three things, in order, each with its own stop condition:

1. **Build and qualify the training image** on a Linux host, ending in
   `verify_training_runtime.py` exiting 0 on a ≥70 GiB card.
2. **One bounded measurement run** producing throughput and peak memory at
   realistic sequence length.
3. **A forecast** from that measured rate, brought back for a decision before
   any sustained run is started.

A sustained training run is **not** in this request. Neither is the environment
pull for the 2,845 tasks, which is a separate, larger piece of work on a host
with Docker and disk.

Until that permission is given: no pod is created, nothing is billed, and the
only thing standing between this repository and a first measurement is the
decision.

---

## 9. What the session actually measured

### 9.1 Phase 1 — the pinned environment qualifies on the device

`requirements/training-linux-py312.lock.txt` installed with `--require-hashes`
and no failures, on a stock `runpod/pytorch:…-ubuntu2404` pod whose system
Python is 3.12.3. Installed: torch **2.10.0+cu128**, transformers **5.13.1**,
compressed-tensors **0.15.0.1**, peft **0.21.2** — every pin matching, imported
versions included. The index audit's prediction held exactly.

`scripts/verify_training_runtime.py` then exited **0** with
`device_checked: true`, `satisfied: true` and no failed checks, on an
A100-SXM4-80GB (capability 8.0, 85,094,825,984 bytes total, 84,649,377,792 free
at start, against the worker's 75,161,927,680-byte floor).

**What this does and does not establish.** The *environment* is qualified on the
device. The **container image is still unbuilt**: a Runpod pod offers no
Docker daemon, so the lock was installed into a virtualenv instead. That checks
the same package set the Dockerfile's `RUN` line would, on the same base OS and
interpreter, but it is not a built, pushed, reusable image, and this document
should not be read as saying otherwise.

### 9.2 Data reached the pod from R2 with nothing read from this machine

The corpus (115 files) and model (8 files, 23,297,590,856 bytes) were fetched by
**presigned URL** — signatures only, no credential on the pod — and then verified
on the pod against their manifests with the repository's own `verify()`. The
model manifest reproduced its published digest
`294f52e33ca2a1c055aa189f28966d96e4e65aa3f586a00cfd6f8ab0a0a87853` byte for byte,
confirming `canonical_json` is deterministic across machines.

`verify_admitted_corpus.py` ran on the pod and reproduced the local figures
exactly: 51 examples, 51 unique tasks, 50 repository groups, 954,733 input and
262,593 supervised tokens, 24,366-token longest example, 210-token minimum
margin, `loader_agreement: true`, all four gates resolved. The schedule
regenerated to `4664ecf6…`, the digest recorded months earlier.

The real checkpoint's architecture also checked out on device: **410 quantized
projections, 779 unquantized tensors, 2,009 checkpoint tensors, 1,189 logical
model tensors.**

### 9.3 Phase 2 — peak memory, answered

| Quantity | Value |
|---|---|
| Device | A100-SXM4-80GB, 79.25 GiB usable |
| Peak observed before failure | **80,191,946,752 bytes (74.68 GiB)**, 242 monitor samples |
| Allocated by PyTorch at failure | 64.45 GiB |
| Reserved but unallocated | 9.71 GiB |
| Free at failure | 4.57 GiB |
| **Failing single allocation** | **35.39 GiB** |
| Updates completed | **0** — it failed on the first |
| Session wall time | 285.87 s, `reason: exited`, `returncode: 1` |

The failing frame is the decisive detail:

```
transformers/models/gemma4/modeling_gemma4.py line 844, in eager_attention_forward
    attn_weights = torch.matmul(query, key_states.transpose(2, 3)) * scaling
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 35.39 GiB.
```

Two separate problems, and it matters which is which.

**The worker decompresses the 4-bit checkpoint to dense weights.** 64.45 GiB was
allocated before any activation, against 60.88 GiB of reconstructed dense
weights recorded at intake. The worker refuses packed parameters outright
(`'Offloaded or packed base parameters rejected'`), so the QAT checkpoint's 4-bit
packing — the entire reason the competition ships that checkpoint — is undone at
load time, consuming 80% of the card before training starts. Keeping the base
quantized and training only the adapter is the normal shape of this job, and the
worker currently forbids it.

**Attention runs eager, so memory is quadratic in sequence length.** Nothing in
the worker sets `attn_implementation`, and transformers selected
`eager_attention_forward`, which materialises the full `[batch, heads, seq, seq]`
score tensor — 35.39 GiB at this sequence length. An SDPA or flash kernel never
materialises it. This is the cheaper of the two fixes and should be tried first,
in a tested commit rather than on a billed pod.

Together these bound the configuration hard: ~15 GiB of headroom after dense
weights, against a corpus whose examples are **7,708 tokens at the shortest,
19,709 at the median and 24,366 at the longest**. There is no sequence length in
this corpus that comfortably fits.

### 9.4 Throughput — still not measured, and now for a stated reason

No update completed, so there is no rate. A second run restricted to the two
examples under 8,192 tokens was attempted and **correctly refused** by
`preflight_corpus_run`: *"Schedule does not cover the admitted training split
exactly."* Training on a cherry-picked subset of an admitted corpus is not
permitted, which is the right answer — measuring throughput on 2 of 51 examples,
below the corpus minimum, would have produced a number worth less than its
caveats. Obtaining one legitimately needs either a memory fix or a differently
admitted corpus.

So `forecast_campaign` still has no measured rate to work from, and still
refuses to forecast. That position is unchanged, but it is now a consequence of
a known blocker rather than of never having looked.

### 9.5 Evidence

Published to R2 under manifest
`c451db62c867509a5462723bdc76301178181064fb55a4b8b05f08b58b65f22b` (15 files,
161,908 bytes), and retained at
[evidence/p1/gpu-measurement-001](../evidence/p1/gpu-measurement-001): both
preflight receipts, the independent audit, the architecture report, the
242-sample device-memory trace, the full OOM traceback, the lifecycle record,
the schedules and configs, and the log of the refused subset run.

### 9.6 What to do next, in order

1. **Set `attn_implementation` to a non-materialising kernel** in the worker's
   model load, with a test, and re-measure. Cheapest change with the largest
   expected effect.
2. **Decide whether the worker should accept packed base parameters.** If LoRA
   training on the QAT checkpoint is the intent, decompressing to dense bf16
   defeats it; if decompression is deliberate, the card needs to be chosen for
   60.88 GiB of weights plus activations, which an 80 GB device cannot provide at
   these sequence lengths.
3. Only then re-run the bounded measurement, and only then forecast.

A card larger than 80 GB (H200 at 141 GB, B200 at 180 GB) would also clear it,
at 1.6–3.6× the hourly rate, and would be buying around a fixable defect.
