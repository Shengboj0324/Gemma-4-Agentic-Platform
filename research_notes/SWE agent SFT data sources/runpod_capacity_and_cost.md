# Runpod capacity-and-cost briefing for the Gemma-4 31B QLoRA campaign

**All account/catalog figures below are live reads from the Runpod MCP server (hosted `https://mcp.getrunpod.io/`, REST v2 surface), made in a single session on 2026-10-28 (local session date). The server is authenticated against this account — account reads returned real pods, volumes, secrets and billing, so nothing here is public-doc fallback unless explicitly labelled.**

**Clock caveat (read it before quoting dates):** the session's stated date is 2026-10-28, but the Runpod API's own timestamps run ahead of that — `list-billing` resolved its default window as `"endTime": "2026-10-30T00:00:00Z"`, and the running pod reports `"createdAt": "2026-10-29T03:21:49.993Z"`. Every timestamp quoted below is verbatim from the API. Treat "today" in the billing table as the UTC bucket `2026-10-29T00:00:00Z → 2026-10-30T00:00:00Z`.

**READ-ONLY compliance:** every Runpod call made was `read-guide`, `lookup-concept`, `search-docs`, `list-*` or `get-*`. No `create-*`, `update-*`, `delete-*`, `pod-action`, `run-endpoint` or any other mutating call was issued. Where a mutation would be needed, the exact call is written down rather than run (see "Mutations deliberately NOT run").

Playbook routing (as the server's instructions require): `read-guide runpod-mcp` was loaded first; it routed to `cost-audit` (cost questions), which was also read in full. Both are plugin v1.8.0, commit `f66d200`.

---

## 1. GPU types this account can reach, and their exact listed hourly prices

### Takeaway
`list-gpu-types` returned 48 GPU type records. Secure-cloud on-demand is the authoritative tier for this workload; community cloud is cheaper on every card that offers it. **No spot / interruptible price field is exposed by the v2 catalog at all** — the only price keys returned are `secure`, `community` and (where applicable) `serverless`. Spot pricing is a gap, not a zero.

### Cited findings — verbatim prices from `list-gpu-types` (2026-10-28)

Every row below is quoted from that one read. `memory` is GB of VRAM per GPU as the API reports it. `maxCount` is the largest GPU count the API will place in that tier.

| API `id` (use verbatim on create) | `name` | VRAM | Secure $/hr | Community $/hr | Serverless $/hr | maxCount secure / community |
|---|---|---|---|---|---|---|
| `NVIDIA H100 PCIe` | H100 PCIe | 80 | **2.89** | 1.99 | 5.39 | 8 / 1 |
| `NVIDIA H100 80GB HBM3` | H100 SXM | 80 | **3.99** | 2.69 | 5.39 | 8 / 1 |
| `NVIDIA H100 NVL` | H100 NVL | 94 | **3.19** | 2.59 | 5.39 | 8 / 10 |
| `NVIDIA H200` | H200 SXM | 141 | **5.29** | 3.59 | 6.99 | 8 / 8 |
| `NVIDIA H200 NVL` | H200 NVL | 143 | **3.79** | 0.5 † | — | 8 / 0 |
| `NVIDIA B200` | B200 | 180 | **7.99** | 5.98 | 10.79 | 8 / 0 |
| `NVIDIA B300 SXM6 AC` | B300 | 288 | **8.99** | 6.94 | 11.99 | 8 / 0 |
| `NVIDIA A100 80GB PCIe` | A100 PCIe | 80 | **1.79** | 1.19 | 2.72 | 8 / 6 |
| `NVIDIA A100-SXM4-80GB` | A100 SXM | 80 | **1.79** | 1.39 | 2.72 | 8 / 8 |
| `NVIDIA A100-SXM4-40GB` | A100 SXM 40GB | 40 | 0 (not secure) | 1 | — | 0 / 2 |
| `NVIDIA L40S` | L40S | 48 | **1.09** | 0.79 | 1.75 | 8 / 8 |
| `NVIDIA L40` | L40 | 48 | **0.82** | 0.69 | 1.75 | 8 / 10 |
| `NVIDIA RTX 6000 Ada Generation` | RTX 6000 Ada | 48 | **0.99** | 0.74 | 1.75 | 8 / 8 |
| `NVIDIA RTX PRO 6000 Blackwell Server Edition` | RTX PRO 6000 | 96 | **2.49** | 1.69 | 3.49 | 9 / 9 |
| `NVIDIA RTX PRO 6000 Blackwell Workstation Edition` | RTX PRO 6000 WK | 96 | **2.59** | 1.69 | 3.49 | 8 / 4 |
| `NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition` | RTX PRO 6000 MaxQ | 96 | 0.5 † | 1.64 | 3.49 | 0 / 2 |
| `NVIDIA RTX PRO 6000 Blackwell Server Edition MIG 2g.48gb` | PRO 6000 MIG 48GB | 48 | **1.29** | 1 | 1.75 | 16 / 0 |
| `NVIDIA RTX PRO 6000 Blackwell Server Edition MIG 1g.24gb` | PRO 6000 MIG 24GB | 24 | **0.69** | 0.5 † | 0.75 | 32 / 0 |
| `AMD Instinct MI300X OAM` | MI300X | 192 | **2.39** | 0.5 † | — | 8 / 0 |
| `NVIDIA RTX A6000` | RTX A6000 | 48 | 0.59 | 0.33 | 1.22 | 10 / 3 |
| `NVIDIA A40` | A40 | 48 | 0.59 | 0.35 | 1.22 | 10 / 1 |
| `NVIDIA GeForce RTX 5090` | RTX 5090 | 32 | 1.19 | 0.69 | 1.79 | 8 / 8 |
| `NVIDIA GeForce RTX 4090` | RTX 4090 | 24 | 0.89 | 0.34 | 1.34 | 8 / 8 |

† **Do not quote `0.5` as a real community price.** It appears as `price.community: 0.5` on exactly the cards whose `community: false` and `maxCount.community: 0` (MI300X, H200 NVL, RTX 2000 Ada, PRO 6000 MIG 24GB, RTX PRO 4500 SE) and as `price.secure: 0.5` on RTX PRO 6000 MaxQ, whose `secure: false` / `maxCount.secure: 0`. It is a placeholder in the tier the card is not sold in. Same for the `0` secure prices on community-only cards (RTX 3070/3080/3080 Ti, Tesla V100, V100 SXM2, A100 SXM 40GB).

- The catalog also returns a junk row: `{"id": "unknown", "manufacturer": "UNKNOWN", "memory": 0, "price": {"community": 0, "secure": 0}}` — ignore it.
- Cards that clear the worker's **70 GiB free device memory** gate on VRAM alone: H100 PCIe/SXM (80), H100 NVL (94), H200 SXM (141), H200 NVL (143), B200 (180), B300 (288), A100 80GB PCIe/SXM (80), RTX PRO 6000 SE/WK/MaxQ (96), MI300X (192).
- Cards that **fail** the gate and must be struck from the candidate list regardless of price: L40S (48), L40 (48), RTX 6000 Ada (48), PRO 6000 MIG 48GB (48), RTX A6000 (48), A40 (48), RTX 5090 (32), RTX 4090 (24), A100 SXM 40GB (40).

### Inferences
- The campaign's shortlist on price-per-GB-of-usable-VRAM, secure cloud, is: **A100 80GB at $1.79/hr** (cheapest ≥80 GB card on the account), then **RTX PRO 6000 SE 96 GB at $2.49/hr**, then **H100 PCIe at $2.89/hr**, then **H100 SXM at $3.99/hr**. H200/B200/B300 buy headroom the measured 67,231 MiB peak does not need.
- MI300X at $2.39/hr secure is listed but is ROCm, not CUDA — the workload pins `torch.cuda`, `single CUDA device`, and `compressed-tensors`; treat it as out of scope rather than a price candidate.

### Gaps
- **Spot / interruptible pricing is not exposed by these tools.** The v2 catalog returns only `secure`, `community`, `serverless`. The `spot-pod` concept exists in the concept graph (it is listed as `is_a: pod`), but no MCP read returns a spot bid price. To get spot rates you need the console or the pricing page; mark any spot figure as unread.
- Savings-plan rates are also unreadable here, and per `https://docs.runpod.io/pods/pricing` "Savings plans are deprecated and can no longer be purchased."

---

## 2. Current availability / capacity per data centre, live

### Takeaway
Right now, **H100 SXM, A100 SXM and RTX PRO 6000 Server Edition are the only ≥80 GB candidates with High stock**. H100 PCIe, H100 NVL, B200, H200 NVL and MI300X are **out of stock entirely** — `stockStatus: "unavailable"`, `pricePerHr: null`. H200 SXM and A100 PCIe are Low. Every available ≥80 GB card currently reports host CUDA **13.2** and nothing lower.

### Cited findings — `get-capacity`, secure cloud only (`secureCloudOnly: true`), 2026-10-28

| GPU | VRAM | `stockStatus` | `pricePerHr` | CUDA versions reported |
|---|---|---|---|---|
| RTX PRO 6000 (Server Edition) | 96 | **High** | 2.49 | 13.2 AVAILABLE |
| A100 SXM | 80 | **High** | 1.79 | 13.2 AVAILABLE |
| H100 SXM | 80 | **High** | 3.99 | 13.2 AVAILABLE |
| PRO 6000 MIG 24GB | 24 | Medium | 0.69 | 13.2 AVAILABLE |
| H200 SXM | 141 | Low | 5.29 | 13.2 AVAILABLE |
| RTX PRO 6000 WK | 96 | Low | 2.59 | 13.2 AVAILABLE |
| A100 PCIe | 80 | Low | 1.79 | 13.2 AVAILABLE |
| L40S | 48 | Low | 1.09 | 13.2 AVAILABLE |
| RTX 6000 Ada | 48 | Low | 0.99 | 13.2 AVAILABLE |
| PRO 6000 MIG 48GB | 48 | Low | 1.29 | 13.2 AVAILABLE |
| MI300X | 192 | **unavailable** | null | {} |
| B200 | 180 | **unavailable** | null | 13.2 UNAVAILABLE |
| H200 NVL | 143 | **unavailable** | null | 13.2 UNAVAILABLE |
| H100 NVL | 94 | **unavailable** | null | 13.2 UNAVAILABLE |
| H100 PCIe | 80 | **unavailable** | null | 13.2 UNAVAILABLE |

The same call **without** `secureCloudOnly` (i.e. community included) returned the same stock verdicts but community prices, plus wider CUDA matrices: A100 SXM `{13.1: AVAILABLE, 13.2: AVAILABLE}`, H200 SXM `{12.9: AVAILABLE, 13.2: AVAILABLE}`, A100 PCIe `{12.4: AVAILABLE, 13.2: AVAILABLE}`, H100 NVL `{12.8: AVAILABLE, 13.2: UNAVAILABLE}`, RTX PRO 6000 SE `{12.8: UNAVAILABLE, 13.0: UNAVAILABLE, 13.2: AVAILABLE}`, RTX 6000 Ada `{12.4: UNAVAILABLE, 13.0: UNAVAILABLE, 13.2: AVAILABLE}`.

### Cited findings — per-data-centre availability, `list-data-centers include=GPU_AVAILABILITY` (2026-10-28)

35 data centres returned. Only the candidates that matter for a ≥80 GB single-GPU training pod:

**H100 SXM (`NVIDIA H100 80GB HBM3`) — listed in 10 DCs, all at `LOW`:** AP-IN-1, AP-JP-1, CA-MTL-1, EU-FR-1, EUR-IS-3, EUR-NO-2, US-CA-2, US-GA-2, US-MO-1, US-NE-1.

**H200 SXM (`NVIDIA H200`) — 6 DCs, all `LOW`:** CA-MTL-3, CA-MTL-4, EUR-IS-4, EUR-IS-5, US-CA-2, US-GA-2.

**A100 SXM (`NVIDIA A100-SXM4-80GB`) — 5 DCs:** US-MD-1 at **`MEDIUM`** (the only MEDIUM/HIGH A100 SXM anywhere in the read), plus EUR-IS-1, US-KS-2, US-MO-1, US-WA-1 all `LOW`.

**A100 PCIe (`NVIDIA A100 80GB PCIe`) — 3 DCs, all `LOW`:** CA-MTL-3, US-KS-2, US-MO-1.

**RTX PRO 6000 Server Edition — 10 DCs:** EU-RO-1 at **`MEDIUM`**, plus EU-CZ-1, EU-NL-1, EUR-IS-1, EUR-IS-2, US-MO-2, US-NC-2, US-NE-1, US-PA-1 all `LOW`.

**B200 — 1 DC only, `LOW`:** US-NC-2. (Note the contradiction with §2's capacity read, which says B200 stock is `unavailable` with `pricePerHr: null`; the DC list shows B200 *offered* in US-NC-2, the capacity probe shows none placeable right now. The capacity probe is the live stock check — treat B200 as not placeable today.)

**B300 — 3 DCs, all `LOW`:** EU-NL-1, EUR-IS-1, US-WA-2.

**MI300X and H200 NVL appear in no data centre's `gpuAvailability` array** in this read.

Four data centres returned **no `gpuAvailability` array at all** (per the `data-center` concept, that means "not requested or this DC offers none", never "out of stock"): OC-AU-1, US-CO-1, US-NC-1, US-TX-3.

### Inferences
- The realistic "place it today" set, in cost order: **A100 SXM in US-MD-1** ($1.79/hr, MEDIUM — the single best stock signal for an 80 GB card), **RTX PRO 6000 SE in EU-RO-1** ($2.49/hr, MEDIUM), **H100 SXM anywhere in its 10 DCs** (High fleet-wide stock but LOW per-DC, so expect to retry DCs).
- `pod.no-capacity-fallback` means a create places exactly the GPU type asked for and 400s rather than substituting, so a candidate list in priority order is mandatory, not optional.

### Gaps
- The per-DC `availability` enum (`LOW`/`MEDIUM`/`HIGH`) and the fleet-wide `stockStatus` (`Low`/`Medium`/`High`/`unavailable`) are different scales from different endpoints and disagree for B200. No read reconciles them.

---

## 3. Network volume pricing, per-DC availability, and stop-vs-terminate semantics

### Takeaway
Standard network volume is **$0.07/GB/month under 1 TB, $0.05/GB/month above**, billed hourly on *allocated* size from creation to deletion whether or not anything is attached. **Container disk is wiped on stop and not charged while stopped; a network volume keeps its data and keeps billing at the same rate forever.** The authoritative source is `https://docs.runpod.io/pods/pricing`.

### Cited findings — pricing, quoted verbatim from the docs read

From `https://docs.runpod.io/pods/pricing` § Storage pricing:

| Storage type | Running Pod | Stopped Pod | Notes |
|---|---|---|---|
| Container disk | $0.10/GB/month | **Not charged** | Temporary; erased when Pod stops |
| Volume disk | $0.10/GB/month | **$0.20/GB/month** | Persistent; retained until Pod deleted |
| Network volume | $0.07/GB/month (< 1TB) | $0.07/GB/month | Permanent; portable between Pods |
| | $0.05/GB/month (> 1TB) | $0.05/GB/month | |

"Storage is billed per-second for container and volume disks, and hourly for network volumes. You are not charged if the host is unavailable." Same table is repeated at `https://docs.runpod.io/accounts-billing/billing` § Storage pricing summary.

High-performance tier: `https://docs.runpod.io/storage/high-performance-storage` § Pricing says only "High-performance storage is priced per-GB at a premium to standard storage… Exact pricing varies by data center. Check the volume creation flow in the console for current rates." **There is no authoritative public per-GB number for HIGH_PERFORMANCE.** A Runpod blog (`https://runpod.io/articles/guides/ai-server-cost`) lists "Network storage, high performance | $0.14/GB/mo" — blog, not docs, and contradicted by the docs' own "varies by data center". Mark as unverified.

Account limits, same pricing page: "**Spend limit**: Default limit of $80/hour across all resources." and "Pods are automatically stopped when your account balance reaches $0. Pods with a network volume are stopped and their data is preserved, while Pods without a network volume are terminated and their data cannot be recovered."

### Cited findings — per-data-centre network volume availability, `list-data-centers` (2026-10-28)

`networkVolumeTypes` per DC, verbatim. **An empty array means no network volume can be created there** (`data-center.volume-types` rule).

- `["STANDARD"]`: AP-JP-1, CA-MTL-3, EU-CZ-1, EU-NL-1, EU-RO-1, EUR-IS-1, EUR-IS-3, EUR-IS-4, EUR-NO-1, US-CO-1, US-IL-1, US-KS-2, US-NC-1, US-NE-1, US-TX-3, US-WA-1
- `["HIGH_PERFORMANCE"]`: AP-IN-1, CA-MTL-1, EU-FR-1, EUR-NO-2, US-CA-2
- `["HIGH_PERFORMANCE","STANDARD"]` (both): **CA-MTL-4 only**
- `[]` — **no network volumes at all**: EU-SE-1, EUR-IS-2, EUR-IS-5, OC-AU-1, US-GA-2, **US-MO-1**, US-MO-2, US-NC-2, US-PA-1, US-TX-4, US-WA-2

**This is the single most important storage finding for the campaign: `US-MO-1`, where this account's existing 201 GB volume already lives, now reports `networkVolumeTypes: []` — no *new* network volume can be created there.** The existing volume still works; a second one cannot be added.

### Cited findings — stop vs terminate, from `lookup-concept pod` / `network-volume`

- `container-disk.what-survives`: "The container disk is cleared when the pod stops, restarts, is reset by an edit, or is terminated. Keep anything you need in `/workspace` on the volume disk or on a network volume."
- Pod state `EXITED` = "The pod is stopped. Compute is released and the volume disk is kept."
- `pod.cost-is-compute-only`: "`cost` reads 0.0 when a pod is `EXITED`, but a stopped pod is still billed for its volume disk. Terminate the pod when you no longer need its data." (evidence: `https://docs.runpod.io/pods/manage-pods` § Stop a Pod)
- `pod.terminate-irreversible`: "Terminating a pod cannot be undone. It destroys the container and any persistent mount; **a network volume is only detached and keeps its data.**" (evidence: `https://docs.runpod.io/pods/manage-pods`)
- `pod.stopped-pod-keeps-host`: "A stopped pod stays tied to its machine and resumes on the same host. If another user has taken the GPU, you can wait, start the pod with zero GPUs to copy data off, or migrate it to a new machine." (evidence: `https://docs.runpod.io/pods/troubleshooting/zero-gpus`)
- `pod.edits-apply-on-restart`: editing a running pod's `image`, `args`, `env`, `ports`, `disk` or `registry` **resets** the pod and "erases everything outside `/workspace` or a network volume".
- `pod.mount-kind-fixed`: the mount kind is fixed at create. "A network volume cannot be swapped or detached later; only the mount path can change." So the volume decision must be made before the pod exists.
- `network-volume.size-grow-only`: size can only grow, 10–4096 GB at create. `network-volume.placement-immutable`: `dataCenter` and `type` are fixed at creation.
- `network-volume.secure-cloud-only`: "Network volumes can be attached only to Secure Cloud pods." → **the community-cloud discount is unavailable to any run that mounts a network volume.**
- `network-volume.concurrent-writes`: several pods can mount the same volume but concurrent writes can corrupt data — relevant because the plan is three candidate runs.
- `network-volume.low-balance-deletion`: at $0 balance, pods with a volume stop and data stays, but storage charges keep accruing and "If the balance stays at $0, the volume can be terminated and its data cannot be recovered."

### Inferences
- Stopping the training pod between the three runs costs the GPU rate × 0 (compute released) but keeps paying $0.07/GB/mo on the network volume and $0.20/GB/mo on any *volume disk*. Since the three runs want the same 23.3 GB checkpoint + adapters, the volume is the right place and the stopped-pod bill is storage-only.
- Because US-MO-1 can no longer create volumes and A100 SXM's best stock is US-MD-1 (which also has `networkVolumeTypes: []`), **the volume DC and the GPU DC have to be chosen together.** US-KS-2 (STANDARD volumes + A100 SXM LOW + A100 PCIe LOW) and EU-RO-1 (STANDARD volumes + RTX PRO 6000 SE MEDIUM) are the two DCs that satisfy both constraints today. CA-MTL-4 is the only DC offering both volume tiers, and it has H200 SXM at LOW.

---

## 4. What this account already has

### Takeaway
Two pods (one RUNNING at $1.09/hr, one EXITED H100), one 201 GB network volume, two secrets, four SSH keys. **Zero** templates, zero serverless endpoints, zero container registry credentials, zero global volumes.

### Cited findings — `list-pods` (2026-10-28)

| id | name | status | GPU | count | DC | cloud | `cost` $/hr | container disk | image | mounts | createdAt |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `sfa1c0z6bsypri` | `st-round14b-prior-w14b` | **RUNNING** | `NVIDIA L40S` (48 GB, 188 GB RAM, 16 vCPU) | 1 | **US-TX-4** | SECURE | **1.09** | 120 GB | `runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04` | none | `2026-10-29T03:21:49.993Z` |
| `609g4lt940xrxe` | `miniature_amethyst_pinniped` | **EXITED** | `NVIDIA H100 80GB HBM3` (80 GB, 251 GB RAM, 26 vCPU) | 1 | **US-MO-1** | SECURE | **3.99** | 80 GB | `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` | network `ipbk8awbhv` → `/workspace` | `2026-10-09T02:33:15.058Z` |

- `sfa1c0z6bsypri`: `actions: ["stop","restart","terminate"]`, `cudaVersion: "13.2"`, ports `["22/tcp"]`, SSH proxy `ssh sfa1c0z6bsypri-644118e6@ssh.runpod.io`, `ssh.direct: null`. Env references `{{ RUNPOD_SECRET_Access_Key_ID }}`, `{{ RUNPOD_SECRET_Secret_Access_Key }}`, `R2_BUCKET: signingdatatranslator`, `R2_ENDPOINT_URL: https://e3d9647571bd8bb6027db63db3197fd0.r2.cloudflarestorage.com`. **This is a live Cloudflare R2 pipeline already wired into a pod — the S3-compatible source for the 23.3 GB checkpoint most likely already exists.**
- `609g4lt940xrxe`: `actions: ["start","terminate"]`, `template: "runpod-torch-v280"`, ports `["8888/http","22/tcp"]`. Its `cost: 3.99` is the H100 SXM secure rate it *would* resume at; per `pod.cost-is-compute-only`, an EXITED pod's `cost` normally reads 0, so read 3.99 here as the resume rate, not current burn.
- `pagination.hasNextPage: false` — that is all the pods (cluster pods excluded by default; no cluster pods were requested).

### Cited findings — `list-network-volumes` (2026-10-28)

| id | name | size | type | dataCenter |
|---|---|---|---|---|
| `ipbk8awbhv` | `romantic_pink_flea` | **201 GB** | `STANDARD` | **US-MO-1** |

`hasNextPage: false`. Volume id doubles as the S3 bucket name (`network-volume` field note: "also the S3 bucket name").

### Cited findings — everything else

- `list-templates` → `{"templates": [], "pagination": {"returned": 0, "hasNextPage": false}}` — **no account-owned templates.**
- `list-endpoints` → `{"items": [], "pagination": {"returned": 0}}` — **no serverless endpoints.**
- `list-global-volumes` → `{"globalVolumes": [], "pagination": {"hasNextPage": false}}` — **no global volumes.**
- `list-registries` → `{"registries": []}` — **no container registry credentials.** (Matters: a custom PyTorch-2.10 image on a private registry would need one.)
- `list-secrets` → two secrets, values never returned:
  - `{"id": "5hl2vy6hpl", "name": "Access_Key_ID", "createdAt": "2026-10-20T06:31:45.764Z"}`
  - `{"id": "08hoggibhz", "name": "Secret_Access_Key", "createdAt": "2026-10-20T06:32:15.814Z"}`
- `get-ssh-keys` → **4 registered keys**, all ed25519: three commented `shengbojmicheal8866@gmail.com` (fingerprint prefixes `AAAAC3NzaC1lZDI1NTE5AAAAIKxHLVA/…`, `AAAAC3NzaC1lZDI1NTE5AAAAIPA0soYaPvhP…`, `AAAAC3NzaC1lZDI1NTE5AAAAICBi2vf/zxrw…`) and one commented `jiangshengbo@Mac.coppola.hamdenhall.org` (`AAAAC3NzaC1lZDI1NTE5AAAAIFISqFxTsOd/…`). Per `https://docs.runpod.io/get-started/credentials`: "all SSH keys in your account are injected into all your Pods. If you add a new key while a Pod is already running, it is injected dynamically without a restart." **SSH is already set up; nothing to provision.**

### Inferences
- The one live cost leak to flag: `sfa1c0z6bsypri` is RUNNING at $1.09/hr. Projected at that rate (`cost × 730`, the cost-audit formula): **$795.70/month**. It is a 48 GB L40S, which cannot host this workload, so it is unrelated to the campaign.
- The EXITED H100 pod `609g4lt940xrxe` is burning nothing for compute but is pinned to US-MO-1 and holds the only mount of the 201 GB volume. Restarting it is the *cheapest* route to an 80 GB card with the model volume already attached — `pod.stopped-pod-keeps-host` says it resumes on the same machine, with the risk that the H100 may have been taken by another user.

### Mutations deliberately NOT run (write these down, do not execute)
- To resume the H100: `pod-action` with `podId: "609g4lt940xrxe"`, `action: "start"`. Not run — it would start billing $3.99/hr.
- To stop the running L40S: `pod-action` with `podId: "sfa1c0z6bsypri"`, `action: "stop"`. Not run — the user did not name it and it is not this session's creation; per the `cost-audit` hard rules, the audit *is* the answer.
- To add a 500 GB standard volume in a DC that still allows them: `create-network-volume` with `name`, `size: 500`, `dataCenter: "US-KS-2"` (or `"EU-RO-1"`), `volumeType: "STANDARD"`. Not run.
- To create the training pod: `create-pod` with `gpu: {id: "NVIDIA A100-SXM4-80GB", count: 1, minCudaVersion: "12.8"}`, `dataCenterIds: ["US-KS-2"]`, `mounts.network[0] = {volumeId: <new>, path: "/workspace"}`, `startSsh: true`, `disk: 120`. Not run.

---

## 5. Current and recent billing / spend

### Takeaway
`list-billing` (bucketSize `day`, `lastN: 30`) returned 22 non-empty daily records totalling **$1,214.5798261696327** over the resolved window `2026-09-30T00:00:00Z → 2026-10-30T00:00:00Z`. **All of it is pods and storage — serverless, public endpoints and clusters are all exactly $0.**

### Cited findings — `list-billing` totals, verbatim (2026-10-28)

```
totalAmount                     1214.5798261696327
podGpuAmount                    1011.2369187213917
podCpuAmount                     167.4148841308779
podDiskAmount                     17.47106531029567
storageStandardAmount              9.438624635338783
storageHighPerformanceAmount       9.018333371728659
endpointAmount                     0
serverlessGpuAmount                0
serverlessCpuAmount                0
serverlessDiskAmount               0
serverlessFeeAmount                0
clusterGpuAmount                   0
clusterDiskAmount                  0
clusterNetworkingAmount            0
recordCount                       22
```

Per-type table in the `cost-audit` report format, every category shown even at zero:

| Category | Spend in window | Share |
|---|---|---|
| Pods — GPU | $1,011.2369187213917 | 83.3% |
| Pods — CPU | $167.4148841308779 | 13.8% |
| Pods — disk | $17.47106531029567 | 1.4% |
| Storage — standard network volume | $9.438624635338783 | 0.8% |
| Storage — high-performance network volume | $9.018333371728659 | 0.7% |
| Serverless (GPU + CPU + disk + fee) | $0.00 | 0% |
| Public Endpoints | $0.00 | 0% |
| Instant Clusters (GPU + disk + networking) | $0.00 | 0% |
| **Total** | **$1,214.5798261696327** | 100% |

Rows sum to the stated total. **The costliest category is pod GPU time at $1,011.24.**

Daily shape (verbatim `totalAmount` per bucket, bucket labelled by its `startTime`):

| Day (UTC start) | total | podGpu | podCpu | podDisk | storageStd | storageHP |
|---|---|---|---|---|---|---|
| 2026-10-08 | 0.06101492419838905 | 0.061 | 0 | 0 | 0 | 0 |
| 2026-10-09 | 16.88535039499402 | 15.653 | 0 | 0.052 | 0.410 | 0.770 |
| 2026-10-10 … 2026-10-18 (9 days) | 1.3089999854564667 each | 0 | 0 | 0 | 0.469 | 0.840 |
| 2026-10-19 | 1.0756666511297226 | 0 | 0 | 0 | 0.469 | 0.607 |
| 2026-10-20 | 90.36375955987023 | 88.457 | 0 | 1.356 | 0.469 | 0.082 |
| **2026-10-21** | **487.8275699525402** | **480.027** | 0 | 7.331 | 0.469 | 0 |
| 2026-10-22 | 116.71072224818636 | 114.417 | 0 | 1.825 | 0.469 | 0 |
| 2026-10-23 | 98.87041996675543 | 50.461 | 46.486 | 1.454 | 0.469 | 0 |
| 2026-10-24 | 86.1464152628032 | 26.292 | 58.248 | 1.137 | 0.469 | 0 |
| 2026-10-25 | 76.86839892109856 | 51.923 | 23.401 | 1.075 | 0.469 | 0 |
| 2026-10-26 | 55.146365389751736 | 41.936 | 11.960 | 0.781 | 0.469 | 0 |
| 2026-10-27 | 78.65218780311989 | 72.164 | 4.869 | 1.150 | 0.469 | 0 |
| 2026-10-28 | 73.92730958262109 | 56.102 | 16.336 | 1.020 | 0.469 | 0 |
| 2026-10-29 (in progress) | 20.263645643455675 | 13.743 | 6.114 | 0.290 | 0.117 | 0 |

### Inferences
- **The single costliest day is 2026-10-21 at $487.83**, almost all pod GPU ($480.03) — a spike roughly 6× the surrounding daily rate.
- The quiet stretch 2026-10-10 → 2026-10-19 bills a flat **$1.309/day** with zero GPU: $0.469 standard + $0.840 high-performance storage. That is the floor cost of keeping volumes alive with nothing running. The high-performance component drops to $0 from 2026-10-21 onward, so a high-performance volume existed and was deleted around then — it does not appear in `list-network-volumes` now.
- Cross-check on the volume rate, from reads only: $0.468999981880188/day × 30.4167 days = **$14.26/month**, against the catalog arithmetic 201 GB × $0.07 = **$14.07/month**. Within rounding of the hourly-billing model. The published $0.07/GB-month rate is confirmed against this account's own meter.
- Recent run-rate: the last 7 complete days (10-22 … 10-28) sum to $586.32, ≈ **$83.76/day ≈ $2,546/month** at this pace. A three-run campaign has to be budgeted on top of that, against a **$80/hour default account spend limit**.

### Gaps
- `list-billing` reports spend, not **credit balance**. No MCP read in this session returns the account's remaining balance or auto-pay state. Given `credit-balance.low-balance-actions` (at $0 all pods stop; volumes can eventually be deleted), **check the balance in the console at `https://www.console.runpod.io/user/billing` before starting a 72-hour run.** This is a real gap, not a zero.
- Per-pod attribution was not drilled (`list-pod-billing` was not called) — the aggregate answers the question asked, and the cost-audit guide warns the per-resource dump can overflow. If the 10-21 spike needs attributing to a specific pod, the call is `list-pod-billing` with `startTime: "2026-10-21T00:00:00Z"`, `endTime: "2026-10-22T00:00:00Z"`, `bucketSize: "day"`.

---

## 6. Official Runpod PyTorch pod templates — and the Python 3.12 / PyTorch 2.10 gap

### Takeaway
**No official Runpod template ships PyTorch 2.10, and none ships Python 3.12 explicitly.** The newest PyTorch in the official catalog is **2.9.0** (`a9dk3g7cny`, a *cluster* template). The newest non-cluster PyTorch template is **2.8.0**. The worker's pin (PyTorch 2.10 / transformers 5.13.1 / peft 0.21.2 / compressed-tensors 0.15.0.1 / Python 3.12) is **not satisfiable by any stock template as-is**.

### Cited findings — `list-public-templates source=official` (2026-10-28), all 14 templates

| id | name | image | `allowedCudaVersions` | container `disk` | persistent mount | ports |
|---|---|---|---|---|---|---|
| `runpod-torch-v21` | Runpod Pytorch 2.1.0 | `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04` | 11.8 | 20 | /workspace 20 GB | 8888/http, 22/tcp |
| `runpod-torch-v220` | Runpod Pytorch 2.2.0 | `runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04` | 12.1–12.9 | 20 | /workspace 20 GB | 8888/http, 22/tcp |
| `runpod-torch-v240` | Runpod Pytorch 2.4.0 | `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04` | 12.4–12.9 | 20 | /workspace 20 GB | 8888/http, 22/tcp |
| `runpod-torch-v280` | **Runpod Pytorch 2.8.0** | `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` | 12.8, 12.9, 13.0, 13.1, 13.2, 13.3, 13.4 | 30 | /workspace 50 GB | 8888/http, 22/tcp |
| `9yo900pjtt` | Runpod Pytorch 2.8.0 for clusters | `runpod/pytorch:1.0.7-cu1281-torch280-ubuntu2404-cluster` | 12.8–13.4 | 50 | /workspace 30 GB | 8888/http, 8889/http, 22/tcp |
| `a9dk3g7cny` | **Runpod Pytorch 2.9.0 for clusters** | `runpod/pytorch:1.0.7-cu1300-torch291-ubuntu2404-cluster` | 13.0, 13.1, 13.2, 13.3, 13.4 | 50 | /workspace 30 GB | 8888/http, 8889/http, 22/tcp |
| `cw3nka7d08` | ComfyUI - CUDA 12.8 | `runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda12.8` | 12.8, 12.9 | 150 | /workspace 50 GB | 8188, 8080, 8888, 22 |
| `wgd3p4n4o6` | ComfyUI - CUDA 13.0 | `runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda13.0` | 13.0–13.4 | 150 | /workspace 50 GB | 8080, 8188, 8888, 22 |
| `runpod-torch-v240-rocm61` | Runpod Pytorch 2.4.0 ROCm 6.1 | `runpod/pytorch:2.4.0-py3.10-rocm6.1.0-ubuntu22.04` | [] | 40 | /workspace 40 GB | 8888/http, 22/tcp |
| `runpod-ubuntu` | Runpod Ubuntu 20.04 | `runpod/base:0.7.0-ubuntu2004` | [] | 5 | — | 8888/http, 22/tcp |
| `runpod-ubuntu-2204` | Runpod Ubuntu 22.04 | `runpod/base:1.0.2-ubuntu2204` | [] | 10 | — | 8888/http, 22/tcp |
| `runpod-ubuntu-2404` | Runpod Ubuntu 24.04 | `runpod/base:1.0.2-ubuntu2404` | [] | 10 | — | 8888/http, 22/tcp |
| `hf23frbcgj` | Network storage file browser | `filebrowser/filebrowser:v2.63.5` | [] | 5 | — | 80/http |
| `wq8gm4lvp4` | Network storage file browser - CPU | `filebrowser/filebrowser:v2.63.5` | [] | 5 | — | 80/http |

All PyTorch/Ubuntu templates have `startSsh: true` and `startJupyter: true`, `public: true`, `registry: null`, `serverless: false`.

Python versions, **only where the image tag states one**: `py3.10` on 2.1.0, 2.2.0 and ROCm 6.1; `py3.11` on 2.4.0. **The 2.8.0 and 2.9.0 tags (`1.0.2-cu1281-torch280-ubuntu2404`, `1.0.7-cu1300-torch291-ubuntu2404-cluster`) carry no `py3.x` component at all** — the catalog read does not tell you their Python version.

### Inferences (clearly marked — not read from a tool)
- The 2.8.0/2.9.0 images are `ubuntu2404`-based, and Ubuntu 24.04's system Python is 3.12. **That is general knowledge, not a tool read.** To state the Python version as fact you must `docker run --rm runpod/pytorch:1.0.7-cu1300-torch291-ubuntu2404-cluster python3 -V`, or `python3 -V` on a live pod. Neither was done here (no shell against a pod; and these MCP tools explicitly do not do commands inside a pod).
- The RUNNING L40S pod already reports `runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04` — **py3.11**, so the pod currently in flight is *not* on 3.12.

### The gap, and the normal remedy
The gap is exactly two notches: **PyTorch 2.9.0 → 2.10** and an unverified Python. The documented remedies, in the order the guides recommend:

1. **Install into the template** — start from `runpod-torch-v280` (or `a9dk3g7cny` for 2.9.0) and `pip install` the pinned stack on top. This is what golden path 04 (LoRA fine-tune on a pod) actually does: "reuses the template's torch (no dependency fights), installs only `peft` + `datasets`", with `pip install --break-system-packages -q peft datasets` to get past PEP 668. **The catch for this campaign: upgrading torch itself from 2.8/2.9 to 2.10 inside a template is not "installing only peft" — it replaces the image's load-bearing layer, pulls a different CUDA wheel set, and is the dependency fight the guide is steering you away from.** Viable for transformers/peft/compressed-tensors; risky for torch.
2. **Build an image** — `runpod-usage/building-images` and golden path 22 cover it. Base on `runpod/pytorch:1.0.7-cu1300-torch291-ubuntu2404-cluster`, install the exact pins, keep `CMD ["/start.sh"]` so SSH still comes up. Golden path 22's warning, verbatim: "a pod image must set up SSH, or you get locked out… Official `runpod/pytorch` images do this for you via `/start.sh`". This account has **no container registry credentials** (`list-registries` → `[]`), so a private image would need `create-registry` first; a public Docker Hub image needs none.
3. CUDA floor: per `runpod-mcp`, "Pin the CUDA floor on every GPU create… `gpu.minCudaVersion` (`"12.8"` by default, `"13.0"` only for a CUDA-13 image)". `pod.cuda-constraints`: `allowedCudaVersions` and a non-empty `minCudaVersion` cannot both be sent (400). Every available ≥80 GB card today reports only CUDA **13.2**, so a 12.8-built image still places (12.8 ≤ 13.2) but a `allowedCudaVersions: ["12.8"]` pin would 400 on capacity.

### Gaps
- The Python version shipped by the 2.8.0 and 2.9.0 official images is **not readable from any tool in this session.** Verify on-pod before committing the campaign to a template-install path.
- PyTorch 2.10, transformers 5.13.1, peft 0.21.2 and compressed-tensors 0.15.0.1 appear in **no** Runpod template, guide, or doc returned by these reads. Treat the whole pinned stack as "bring your own".

---

## 7. Guidance answers from Runpod's own documentation

### 7a. Getting a 23.3 GB model onto a pod efficiently from S3-compatible object storage

**Takeaway:** write it to a **network volume** once, over the **S3-compatible API with no pod running** — that is the documented default and the cheapest method.

- Golden path 10 ranks the three methods by compute cost, verbatim: "**S3-compatible API** (recommended) | **none — no pod at all** | the DC supports the S3 API and the data is files you already have (models, datasets, adapters)"; then CPU pod ("cheap"); then cheapest GPU pod ("most expensive"). — `https://github.com/runpod/runpod-plugins-official/blob/97221eb/plugins/runpod/skills/runpod/golden-paths/10-multi-region-ha-serverless.md`
- Invocation shape, verbatim: `--region <DC> --endpoint-url https://s3api-<DC>.runpod.io/`, bucket name = the network volume id. Path mapping: `/workspace/my-folder/file.txt` on a pod == `s3://NETWORK_VOLUME_ID/my-folder/file.txt`. — `runpod-usage/reference/storage.md`
- Credentials: `AWS_ACCESS_KEY_ID` = your Runpod **user ID** (`user_...`); `AWS_SECRET_ACCESS_KEY` = an **S3 API key** (`rps_...`). **Console-only to create** — "They cannot be created via `runpodctl` or any REST/GraphQL call — only in the Console (Settings → S3 API Keys → Create)… the secret is shown **once**." Create at `https://console.runpod.io/user/credentials` → S3 API Keys tab. — `https://docs.runpod.io/get-started/credentials`
- Per-DC limitation, verbatim: "The S3-compatible API for network volumes is available only in some data centers, each with its own endpoint. REST v2 `DataCenter` has no field for it, so check the S3 API docs before creating a volume you plan to reach over S3." Golden path 10 names "EU-RO-1, EU-CZ-1, EUR-IS-1, US-KS-2, and more" and points at `https://docs.runpod.io/storage/s3-api#datacenter-availability`.
- **Size warnings that bite a 23.3 GB / 2,009-tensor checkpoint**, verbatim from golden path 21: "over the S3 access path, listing/syncing >10k files or >10 GB degrades, and **single-object `PUT` caps at 500 MB (use multipart above)**." And from golden path 10: "`aws s3 sync` is fine for modest trees but **struggles past ~10,000 files** and has weak resume… Bump retries on 502s: `export AWS_RETRY_MODE=standard AWS_MAX_ATTEMPTS=10`."
- **Pulling from an external bucket (this account's R2) is a different operation** and is the better fit here: the pod already carries `R2_BUCKET`/`R2_ENDPOINT_URL` env and `{{ RUNPOD_SECRET_* }}` references, so `aws s3 cp --endpoint-url $R2_ENDPOINT_URL` **from inside the pod** writes straight to `/workspace` on the mounted volume. Docs confirm the pattern generally: "Connect to external object storage (AWS S3, MinIO, Backblaze B2, DigitalOcean Spaces, etc.) using your own credentials. Useful for large files exceeding API payload limits." — `https://docs.runpod.io/serverless/storage/overview`
- Point caches at the volume so a restart does not re-download, verbatim: `export HF_HOME=/workspace/hf-cache`, `export UV_CACHE_DIR=/workspace/uv-cache`, `export PIP_CACHE_DIR=/workspace/pip-cache`. — `runpod-usage/reference/on-pod-setup.md`
- **Gotcha that will bite the R2 path:** `pod.env-pid1-only` (status **verified** by live probe, seen 2026-09-28): "Environment variables set at create time reach the container's main process but **not SSH login shells**. Pass them explicitly in commands you run over SSH, or export them in the shell profile." So `$R2_ENDPOINT_URL` will be empty in an SSH session even though it is set on the pod.
- Network volume throughput, for sizing the copy: "NVMe-backed (roughly 200–400 MB/s, higher peak)"; HIGH_PERFORMANCE gives "up to 3x the throughput and 4x the IOPS of STANDARD". — `runpod-usage/reference/storage.md`, `network-volume.type-per-dc`

### 7b. Does pod stop keep the container disk?

**No.** Verbatim, `container-disk.what-survives`: "The container disk is cleared when the pod stops, restarts, is reset by an edit, or is terminated. Keep anything you need in `/workspace` on the volume disk or on a network volume." The pricing table agrees from the billing side: container disk is "Temporary; erased when Pod stops" and **Not charged** while stopped. Pod state `EXITED` keeps the *volume disk*, not the container disk.

### 7c. How billing works for a stopped pod with a network volume

- Compute: released. `pod.cost-is-compute-only`: "`cost` reads 0.0 when a pod is `EXITED`". No GPU charge while EXITED.
- Container disk: **$0 while stopped** (pricing table, "Not charged").
- Volume disk (host-local `/workspace`, if the pod has one instead of a network volume): **$0.20/GB/month while stopped** — double the running rate.
- Network volume: **$0.07/GB/month, unchanged** whether the pod is running, stopped or terminated. `network-volume-billing.price`: "billed hourly per GB of **allocated** size from creation until deletion, whether or not anything is attached."
- So for pod `609g4lt940xrxe` (EXITED, 80 GB container disk, network volume `ipbk8awbhv` 201 GB mounted at `/workspace`): current bill = $0 compute + $0 container disk + 201 GB × $0.07 = **$14.07/month**, which matches the $0.469/day standard-storage line in the billing read ($14.26/mo). Terminating the pod would not change that figure — the volume bills independently, and terminate only detaches it.
- `network-volume.allocated-size-only`: "`size` is the allocated size. The API returns no usage figure" — you pay for 201 GB whether 23 GB or 200 GB is in use.

### 7d. SSH access setup

Already done on this account (4 keys registered), but the documented procedure, verbatim from `https://docs.runpod.io/get-started/credentials` and `https://docs.runpod.io/pods/configuration/use-ssh`:

1. `ssh-keygen -t ed25519 -C "YOUR_EMAIL@DOMAIN.COM"` → `~/.ssh/id_ed25519{,.pub}`.
2. Add the **public** key at `https://console.runpod.io/user/credentials` → SSH Public Keys, or `runpodctl ssh add-key --key-file ~/.ssh/id_ed25519.pub`; verify with `runpodctl ssh list-keys`. "If you add multiple SSH keys, each key must be on its own line."
3. Two connection methods, and the difference matters:
   - **Basic SSH** via the proxy: `ssh <pod-id>-<hash>@ssh.runpod.io -i ~/.ssh/id_ed25519`. "This method does **not** support commands like SCP… or SFTP." Needs no public IP or exposed port.
   - **Full SSH over exposed TCP**: `ssh root@[POD_IP] -p [SSH_PORT] -i [KEY]`. Supports SCP/SFTP/rsync/port-forwarding. Requires `22/tcp` in the pod's `ports` **and** a public IP. The concept rule: "SCP, SFTP, rsync and port forwarding need `ssh.direct`, which requires `22/tcp` in `ports` and is **null while the pod is provisioning or stopped**. Prefer `ssh.direct` when it is available."
4. `startSsh` on create injects the account's keys as `PUBLIC_KEY`: "A pod created without it has no SSH access, whatever its `ssh` block reports, and with no keys registered the flag does nothing. Only images that read `PUBLIC_KEY` start an SSH daemon; all official Runpod images do."
5. **Observed on this account:** both pods report `"ssh": {"direct": null, "proxy": {...}}` — `direct` is null on the RUNNING pod too, even though it exposes `22/tcp`. **For SCP/SFTP to the training pod you will need a pod that actually gets a public IP; neither current pod has `ssh.direct` populated.** Per the troubleshooting list, a password prompt means the key is wrong, not that a password exists: "Runpod does not require a password for SSH connections."
6. If a pod is unreachable: `runpodctl ssh info <pod-id>` "to see the specific reason".

### 7e. Running a long training job so an SSH disconnect does not kill it

**Two documented options. For a 10–72 hour run, use `tmux`; for agent-driven launches, use `setsid` + a log on the volume.**

- Runpod has a dedicated page, `https://docs.runpod.io/tips-and-tricks/tmux`. tmux is **not** preinstalled: `apt-get update && apt-get install -y tmux`. Its own "Practical example: running model training", verbatim:
  ```bash
  tmux new -s model_training
  cd /workspace/my_project
  python train.py --epochs 100 --batch-size 32
  # Detach from the session with Ctrl+B, then D
  # You can now safely disconnect from the Pod
  tmux attach -t model_training
  ```
  Plus `tmux ls`, `tmux kill-session -t training`.
- **`&` alone is not enough**, verbatim from `runpod-usage/reference/on-pod-setup.md`: "A long-lived server needs full detachment, not just `&`. When the SSH channel closes it sends SIGHUP to its process group, which kills a plainly backgrounded `&`/subshell process." The documented detached form:
  ```bash
  ssh <host> 'setsid bash -c "<cmd>" > /workspace/svc.log 2>&1 < /dev/null &'
  ```
  "`setsid` (new session, off the SSH TTY/pgroup) **and** `< /dev/null` are both needed. Do not `sleep` in the same invocation — it can drop the channel (exit 255)." Poll with a **separate** call: `ssh <host> 'tail -n 20 /workspace/setup.log'`.
- Golden path 04 says the same for a real training run, verbatim: "For a **real** run (longer than a few minutes), don't paste the script interactively — **write it to the volume as `/workspace/train.py`**, launch it **detached** so it survives SSH disconnect, and monitor by tailing the log in separate calls."
- **Do not use the browser web terminal:** "The browser web terminal is tied to its session and is not suited to long-running work. Use SSH for long-running processes, and run them under `tmux` or a similar tool so they survive a dropped connection."
- Cost guard for an unattended run: `pod.scheduled-stop`, verbatim — "REST v2 has no field that stops a pod after a set time. `runpodctl pod create` takes `--stop-after` and `--terminate-after` for that. For a pod created another way, run `runpodctl pod stop $RUNPOD_POD_ID` from inside it, for example `sleep 2h; runpodctl pod stop $RUNPOD_POD_ID &`." **This is a real gap in the MCP surface: a pod created with `create-pod` has no auto-stop. Build the stop into the training script's exit path or create the pod with runpodctl.**
- Checkpoint to the volume, not the container disk — `pod.edits-apply-on-restart` warns an edit "erases everything outside `/workspace` or a network volume".

---

## 8. Arithmetic a planner needs

### Takeaway
At secure-cloud on-demand rates, 72 hours on the cheapest ≥80 GB card (A100 80GB, $1.79/hr) is **$128.88**; on H100 SXM ($3.99/hr) it is **$287.28**. 200 GB of standard network volume is **$14.00/month**; 500 GB is **$35.00/month**.

### GPU cost table — every rate quoted from the `list-gpu-types` read above; cost = rate × hours

**Secure cloud, on-demand (the only tier that can mount a network volume):**

| GPU | VRAM | $/hr | × 10 h | × 24 h | × 72 h | Live stock today |
|---|---|---|---|---|---|---|
| A100 PCIe | 80 | 1.79 | **17.90** | **42.96** | **128.88** | Low |
| A100 SXM | 80 | 1.79 | **17.90** | **42.96** | **128.88** | **High** (MEDIUM in US-MD-1) |
| RTX PRO 6000 SE | 96 | 2.49 | **24.90** | **59.76** | **179.28** | **High** (MEDIUM in EU-RO-1) |
| RTX PRO 6000 WK | 96 | 2.59 | 25.90 | 62.16 | 186.48 | Low |
| H100 PCIe | 80 | 2.89 | 28.90 | 69.36 | 208.08 | **unavailable** |
| H100 NVL | 94 | 3.19 | 31.90 | 76.56 | 229.68 | **unavailable** |
| H200 NVL | 143 | 3.79 | 37.90 | 90.96 | 272.88 | **unavailable** |
| H100 SXM | 80 | 3.99 | **39.90** | **95.76** | **287.28** | **High** |
| H200 SXM | 141 | 5.29 | 52.90 | 126.96 | 380.88 | Low |
| B200 | 180 | 7.99 | 79.90 | 191.76 | 575.28 | **unavailable** |
| B300 | 288 | 8.99 | 89.90 | 215.76 | 647.28 | Low (3 DCs) |
| MI300X | 192 | 2.39 | 23.90 | 57.36 | 172.08 | **unavailable** (and ROCm, not CUDA) |
| *L40S (48 GB — fails the 70 GiB gate)* | 48 | 1.09 | 10.90 | 26.16 | 78.48 | Low |
| *RTX 6000 Ada (48 GB — fails)* | 48 | 0.99 | 9.90 | 23.76 | 71.28 | Low |

Worked example so the arithmetic is auditable: A100 SXM 72 h = $1.79 × 72 = $128.88. H100 SXM 72 h = $3.99 × 72 = $287.28. RTX PRO 6000 SE 24 h = $2.49 × 24 = $59.76.

**Community cloud, on-demand** — cheaper, but `network-volume.secure-cloud-only` means **no network volume**, so the 23.3 GB checkpoint must live on the container/volume disk and is lost on terminate. Included for completeness:

| GPU | $/hr | × 10 h | × 24 h | × 72 h |
|---|---|---|---|---|
| A100 PCIe | 1.19 | 11.90 | 28.56 | 85.68 |
| A100 SXM | 1.39 | 13.90 | 33.36 | 100.08 |
| RTX PRO 6000 SE | 1.69 | 16.90 | 40.56 | 121.68 |
| H100 PCIe | 1.99 | 19.90 | 47.76 | 143.28 |
| H100 NVL | 2.59 | 25.90 | 62.16 | 186.48 |
| H100 SXM | 2.69 | 26.90 | 64.56 | 193.68 |
| H200 SXM | 3.59 | 35.90 | 86.16 | 258.48 |
| B200 | 5.98 | 59.80 | 143.52 | 430.56 |

### Network volume cost table

Standard tier, rate $0.07/GB/month under 1 TB (from `https://docs.runpod.io/pods/pricing`):

| Size | Arithmetic | Per month | Per day (÷30.4167) | 3 months |
|---|---|---|---|---|
| 200 GB | 200 × $0.07 | **$14.00** | $0.46 | $42.00 |
| 500 GB | 500 × $0.07 | **$35.00** | $1.15 | $105.00 |
| 201 GB (the existing `ipbk8awbhv`) | 201 × $0.07 | **$14.07** | $0.46 | $42.21 |
| 1024 GB (tier boundary) | 1000 × $0.07 + 24 × $0.05 | $71.20 | $2.34 | $213.60 |

Cross-check against this account's own meter: the quiet days bill `storageStandardAmount: 0.468999981880188`/day for the 201 GB volume → × 30.4167 = **$14.26/month**. Published rate confirmed.

HIGH_PERFORMANCE at 200 GB / 500 GB: **cannot be computed from an authoritative source.** Docs say the rate "varies by data center… Check the volume creation flow in the console". *If* the blog's $0.14/GB/mo holds, 200 GB = $28.00 and 500 GB = $70.00 — **blog figure, unverified, do not budget on it.**

Container disk, for completeness at $0.10/GB/month while running: the campaign needs ≥120 GB container disk to stage a 23.3 GB checkpoint plus a dequantized working set, so 120 GB × $0.10 = **$12.00/month while running, $0 while stopped**.

### Campaign-shaped totals (arithmetic only — see the gap below)

Three runs on the cheapest available 80 GB card, A100 SXM at $1.79/hr secure, with a 500 GB standard volume held for one month:

| Hours per run | GPU cost per run | GPU cost × 3 | + 500 GB volume (1 mo) | Campaign total |
|---|---|---|---|---|
| 10 | $17.90 | $53.70 | $35.00 | **$88.70** |
| 24 | $42.96 | $128.88 | $35.00 | **$163.88** |
| 72 | $128.88 | $386.64 | $35.00 | **$421.64** |

Same on H100 SXM at $3.99/hr: 10 h → $39.90 × 3 + $35.00 = **$154.70**; 24 h → $95.76 × 3 + $35.00 = **$322.28**; 72 h → $287.28 × 3 + $35.00 = **$896.84**.

### Gaps
- **Hours per run cannot be derived from anything read.** The target is 3 × ~50 M processed tokens, but no read gives tokens/second for rank-4 QLoRA at 32,768-token sequences, batch size 1, eager attention, non-reentrant gradient checkpointing, on any of these cards. The prior session's data point — ~19.63 GiB model load and 67,071–67,231 MiB peak during a **24-token single-step** fixture on an H100 — fixes the *memory* envelope but gives no throughput. **The 10/24/72-hour columns above are the planner's brackets, not estimates of the run length.** Measure tokens/sec on a short pilot, then multiply.
- The Runpod blog `https://runpod.io/articles/guides/ai-server-cost` offers reference points ("Full fine-tune, 70B, quantized | H100 SXM | 24 hrs | $71.76") but that figure implies $2.99/hr, which matches no price in this account's catalog — the blog is stale or uses a different tier. **Do not use blog workload timings.**
- Memory headroom check that still needs doing on-pod: the worker refuses to start below 70 GiB free device memory. 70 GiB = 71,680 MiB. An 80 GB card reports ~81,920 MiB total, so a *clean* 80 GB card passes the gate and the measured 67,231 MiB peak (≈65.7 GiB) fits — **but with only ~14 GiB of slack against a 24-token fixture.** Scaling the fixture to 32,768-token sequences was not measured. A 96 GB RTX PRO 6000 SE at $2.49/hr buys 16 GB more headroom for $0.70/hr over the A100, which is $50.40 over 72 hours — cheap insurance if the long-sequence peak is unknown. Flagging this as the live risk, not a read.

---

## 9. Observation log — what was read, when

Every row observed **2026-10-28** (session date; see the clock caveat at the top), via the authenticated hosted Runpod MCP server.

| Read | Result summary |
|---|---|
| `read-guide runpod-mcp` | plugin v1.8.0 / commit `f66d200`; routed to `cost-audit` |
| `read-guide cost-audit` | read-only audit procedure + report contract |
| `list-gpu-types` | 48 GPU types with secure/community/serverless prices |
| `get-capacity` (8 candidate filters, with and without `secureCloudOnly`) | 17 matching types; stock + per-CUDA matrix |
| `list-data-centers include=GPU_AVAILABILITY` | 35 data centres, per-DC GPU availability, `networkVolumeTypes`, compliance, `globalNetwork` |
| `list-pods` | 2 pods (1 RUNNING L40S, 1 EXITED H100) |
| `list-network-volumes` | 1 volume, 201 GB STANDARD, US-MO-1 |
| `list-templates` | **empty** |
| `list-public-templates source=official` | 14 official templates |
| `list-endpoints` | **empty** |
| `list-global-volumes` | **empty** |
| `list-registries` | **empty** |
| `list-secrets` | 2 secrets |
| `get-ssh-keys` | 4 ed25519 keys |
| `list-billing lastN=30 bucketSize=day` | 22 records, $1,214.5798261696327 total |
| `lookup-concept` × 3 (`pod`, `network-volume`, `network-volume-billing`) | state machine, rules, public evidence URLs |
| `search-docs` × 4 (volume pricing, S3 model transfer, tmux/detach, SSH setup, S3 API per-DC) | docs/knowledge/blog passages with source URLs |

**Not read / could not be read live (gaps):** spot and savings-plan prices (no tool exposes them); account credit balance and auto-pay state; HIGH_PERFORMANCE per-GB rate (console-only); Python version inside the 2.8.0/2.9.0 official images; per-DC S3-API availability as a structured field (REST v2 `DataCenter` has no such field); throughput/tokens-per-second for this workload on any card.
