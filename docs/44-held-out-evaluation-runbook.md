# 44 — Held-out evaluation runbook (Runpod, official harness)

How the trained adapter is compared with the base model on the frozen official
development cohort, end to end, with the competition's own serving and
verification code. Results are recorded in `40-p1-implementation-journal.md`.

## What is compared

- **Base**: the P1 base agent (`evidence/p1/base-agent-001`).
- **Adapter**: the same submission plus `adapters/main_lora` (the epoch-1
  adapter, safetensors `962349d6…`) and one `adapter: main_lora` line.
  `scripts/build_eval_candidates.py` refuses any other difference.
- **Tasks**: the pilot (20) and development (29) roles of the frozen split
  `evidence/p1/official-split-001/split.json` (freeze `fe45b4f8…`), 49 of the
  129 official development tasks. The 80 holdout tasks are refused by
  `require_cohort`. The training corpus shares no repository with
  fastapi, rich, requests or httpx.

## Data path (nothing local, nothing credentialed on the pod)

1. Kaggle → R2 by digest with `scripts/ingest_kaggle_to_r2.py --bulk`. One API
   call yields the signed URL of the 21.93 GB all-files archive. The script
   stops at that redirect, because kagglesdk's own call would buffer the whole
   archive in memory. Members are read by HTTP range and checked against their
   zip CRC and the listing size. A journal makes reruns resume.
   - Core files (everything except snapshots): 395 files, 920 MB, manifest
     `5619f2ce…`.
   - Cohort snapshots: 49 files, 8.18 GB (`--files-from`).
   - Holdout snapshots (13.31 GB) are not needed for this comparison.
2. `scripts/freeze_official_split.py` freezes the split against the ingested
   `tasks.jsonl`. The split is published to R2 (manifest `f6488faf…`).
3. `scripts/presign_fetch_bundle.py` gives the pod presigned GET URLs only.
   Every fetched byte is verified against its manifest before use.

## Air gap on Runpod

Runpod containers have Docker's default capabilities and a seccomp filter
that refuses `unshare`, so the network-namespace mode of `zenithsync/netns.py`
is unavailable. The `egress-guard` mode is used instead:

- `scripts/egress_guard.py install` (as root) compiles
  `zenithsync/egress_guard.c` into `/usr/local/lib/zenithsync` and adds it to
  `/etc/ld.so.preload`. The dynamic loader reads that list for every process,
  whatever its environment, so the sandbox's environment sanitising cannot
  drop it.
- The library refuses any peer other than 127.0.0.1, ::1 and
  ::ffff:127.0.0.1 in `connect`, `sendto`, `sendmsg` and `sendmmsg`, and
  refuses raw and packet sockets. All of 127/8 is not allowed, because
  Docker's forwarding resolver listens on 127.0.0.11.
- `/etc/resolv.conf` is pointed at a dead loopback address, because glibc's
  resolver connects through an internal symbol the library cannot see.
- Everything that runs agents runs as the non-root user `evaluator`. The
  sandbox executes agent commands as that user, so they cannot rewrite the
  guard.

`netns.require_guard()` checks all of the following before the evaluation
starts, and again after every worker exits (otherwise the run is marked
`isolation_lost`):

- the process is not root;
- the guard library is mapped into the process;
- no guard file is writable;
- direct DNS queries to every original resolver, and to 127.0.0.11, get no
  answer;
- 1.1.1.1:443 is unreachable from this process and from fresh `env -i` Python
  and curl processes.

What the guard does not cover: statically linked binaries and raw syscalls.
Receipts record the mode and add it to `deviations_from_scoring_machine`.

## Pod procedure

Pod: one A100-SXM4-80GB ($2.19/hr, within the $5/hr cap), network volume at
`/mnt/data`.

1. Clone the repository. Fetch the model, wheelhouse, adapter, devset and
   split through the presigned bundle, then verify each against its manifest.
2. Create the venv on the **container disk** (`/root/venv`). Installing torch's
   many small files onto the network volume ran at about 0.4 MB/s.
3. `build_eval_candidates.py` builds `base` and `adapter`.
4. `prep.sh` creates `evaluator`, copies the compile caches, installs the
   guard (removed again by an EXIT trap) and runs the guard check as
   `evaluator`.
5. Run `qualify_lora_serving.py --isolation egress-guard` as `evaluator`.
   It checks that the official `VllmServer` lists the adapter, that base and
   adapter outputs differ on the same greedy prompts, and that both parse a
   tool call.
6. Run `run_official_eval.py --isolation egress-guard` as `evaluator`, first on
   two tasks as a smoke test and then on all 49. Then run
   `compare_paired_eval.py`.
7. Remove the guard, archive the run directory to R2 through presigned PUT
   URLs, terminate the pod and delete the volume. Confirm both with fresh reads.

## Evaluation data is read-only to the agents

The network volume ignores ownership and shows every file as mode 777. The
devset, split and candidates therefore get copied to `/opt/eval-data` on the
container disk, owned by root and read-only, and the run reads them only
from there. `scripts/verify_manifests.py` checks the copy against the fetched
manifests before the run and again afterwards; candidates are compared by
hash tree. A run whose data changed is not reported.

## Model routing

The scoring runtime builds its model registry with the running server's
`VllmServer.create_model_registry`. It binds the single declared model alias
and every adapter name to `openai/<served model>` (HARNESS_README §3.3). The
worker does the same from an unstarted handle on the running endpoint, and
records the routes it got:
`gemma-4-31b-it-qat-w4a16-ct → openai//mnt/data/model` and
`main_lora → openai/main_lora`. A submission declaring anything other than
exactly one allowed base model is refused.

## Measured on the A100 (one vLLM server, both candidates)

- Cold start: 101 s to load weights from the network volume (7 s from page
  cache) and 600–660 s of engine initialisation (torch.compile, flashinfer JIT,
  4 min of CUDA-graph capture), so 10–13 min from launch to ready. The
  compile cache is per user and is reused on the next start.
- KV cache: 55,008 tokens, 10.37× concurrency at 32,768 tokens per request
  (Gemma's sliding-window layers hold less).
- Budget from the candidates' `eval_config.yaml`: 10 min, 40 turns and 40 tool
  calls per task. Wall clock is the binding limit. In the smoke run one agent
  made only 12 model calls in 10 min, because Gemma's reasoning makes each
  call long.
- The harness verifies a patch even when the agent ran out of budget, and
  records the budget error on the same row.

## Faults met and fixed on the way

| Fault | Fix | Commit |
|---|---|---|
| kagglesdk bulk call buffers the 22 GB archive in memory | stop at the redirect | `5272125` |
| `unshare` refused by Runpod's seccomp profile | egress-guard mode | `6d72596`, `0018350` |
| guard allowed Docker's loopback DNS; root agent could remove it | exact 127.0.0.1; non-root; checks | `32c94a6` |
| `VllmServer.stop()` deletes its log; reading it after lost a receipt | hard-link before stop | `7a19565` |
| vLLM rendezvous on the pod's external IP | `VLLM_HOST_IP=127.0.0.1` | `6d72596` |
| torch onto the network volume at ~0.4 MB/s | venv on container disk | — |
| network volume writable by the agents' user | read-only root-owned copy; re-verify after | `269c21c` |
| `swegemma.models.registry` absent in 0.2.11 (first smoke run's workers died) | official `create_model_registry` | `64e541c`, `3a0d600` |
| a verified failing patch classed as an error because the budget ran out | patch decides the class | `aade59c` |

## Verifier qualification (fixed before any agent result)

The first full run (`full-1`, 06:28 UTC) scored 0/40 on both sides. It was
stopped and is kept only as evidence: every hidden-test run had failed with
`No module named pytest`. swegemma's subprocess sandbox installs nothing into
the task venv. It exposes the host interpreter's site-packages and expects
the host to carry the repositories' runtime and test packages.

The fix mirrors the official sandbox image, `<devset>/docker/Dockerfile.sandbox`:
- the task wheels, highest compatible version per distribution, which is the
  rule of `sandbox/setup.py` and swegemma;
- `pytest-timeout==2.1.0`, digest-pinned;
- the image's `imp.py` and `telnetlib.py`.

All of it goes into a read-only `site-packages` exposed to sandboxes
(`scripts/build_test_site.py`, `--test-site`). Nothing that is absent from
both the task wheels and the image was added.

`scripts/qualify_verifier.py` then ran swegemma's own per-task path on all 49
cohort tasks, once with the gold patch and once with an empty patch, before
the agents ran again (receipt sha256 `90adbf67…`):

| | resolved |
|---|---|
| gold patch | **29 / 49** |
| empty patch | 2 / 49 (`requests_7309`, `requests_7315`: their hidden tests pass unchanged) |

The 20 gold failures:
- 14 fastapi tasks import `inline_snapshot`, which neither the official
  wheels nor the image provide;
- 2 requests tasks need the pytest-httpbin plugin, likewise absent;
- 4 tasks (`rich_3296`, `rich_3782`, `fastapi_15763`, `requests_7205`) fail
  their own tests with the gold patch here.

So under this environment the agent ceiling is about 29/49. The primary
metric stays resolved/49. The 29 gold-resolving tasks are a secondary subset,
fixed by the receipt above before `full-2` produced any result:

fastapi_14258 fastapi_14301 fastapi_14306 fastapi_14419 fastapi_14448
fastapi_14463 fastapi_14786 fastapi_14794 fastapi_14986 fastapi_15800
requests_7309 requests_7315 rich_2943 rich_3006 rich_3052 rich_3278 rich_3506
rich_3518 rich_3535 rich_3777 rich_3882 rich_3894 rich_3930 rich_3935
rich_3938 rich_3942 rich_3944 rich_4075 rich_4077

## Result: `full-2`, 2026-11-14 06:36–08:34 UTC

Both candidates were served concurrently from one vLLM server, with 4 agents
each, on all 49 cohort tasks. Every task produced a row on both sides and both
workers exited 0. The air gap held after the run (`network_isolation_after`
shows the external address unreachable and no DNS). The data and candidates
were byte-identical afterwards.

| | resolved / 49 | Wilson 95% | resolved / 29 gold-qualified |
|---|---|---|---|
| base | **15** (30.6%) | 19.5–44.5% | 15 (51.7%) |
| adapter (`main_lora`, epoch 1) | **13** (26.5%) | 16.2–40.3% | 13 (44.8%) |

- **Paired:** both solved 11, only the base solved 4 (`fastapi_14419`,
  `rich_3052`, `rich_3278`, `rich_4075`), only the adapter solved 2
  (`rich_3777`, `rich_3882`), neither solved 32.
- **Effect:** Δ = −4.1 points, seeded bootstrap 95% −14.3 to +6.1, exact
  McNemar p = 0.69. On the gold subset Δ = −6.9 points (−24.1 to +10.3).
- **By repository** (base / adapter): rich 8/7 of 19, fastapi 5/4 of 25,
  requests 2/2 of 5.
- **Consistency:** every resolution on either side is inside the gold-qualified
  subset that was fixed before the run.
- **Interpretation:** the adapter is not shown to help. The point estimate is
  slightly worse, the interval comfortably includes zero, and 49 tasks from
  three repositories cannot support a broader claim either way. A
  non-significant difference is not equivalence.
- **Time budget:** the adapter's agents were slower. Median task time was
  594 s against 426 s, about 18.6 s per model call against 12.2 s. Completion
  tokens per call were higher (mean 313 vs 248, +26%), which explains only
  part of that, so the rest is LoRA serving overhead. The adapter therefore
  ran out of the 10-minute wall clock without a patch twice as often (8 vs 4).
  The scorer serves adapters the same way, so this is a real cost of the
  approach, not an artefact.
- **Leakage audit:** no agent command or trace references `tasks.jsonl`,
  `/opt/eval-data`, the run directories or the R2 data. Paths outside the
  sandbox appear only in tracebacks: the test site's pytest, and
  `/root/venv` packages that agents' code imported.
- **Caveat on the test environment:** with `append` order, packages already in
  the evaluator's own environment (vLLM's starlette, pydantic and others) take
  precedence over the task wheels inside sandboxes. The official image has
  only pytest, its pinned plugins and the task wheels.

Evidence is in R2. The package `evidence/p1/held-out-eval-001` (manifest
`1184e02d…`, 21 files) holds the receipts, comparisons, task results,
verifier and LoRA qualification, and the pod scripts. The full archive
`artifacts/v1/tmp/eval-2026-11-14/runs.tar` (sha256 `f3c8ba3d…`, 26.1 MB) holds
every run's traces, task logs, test outputs and patches. The pod (A100-SXM4-80GB,
$2.19/h, 03:22–08:47 UTC, ≈ $11.90) and its volume were deleted, and both
deletions were confirmed with fresh reads.
