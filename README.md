# ZenithSync-Gemma-4-Paper-Track

Joint research and execution plan for the Google Gemma 4 Developer Agent Competition and Paper Track. Initially researched October 6; scope and code-track requirements updated October 7, 2026.

**Adopted direction:** build a complete, trainable Gemma-powered repository engineering agent first, using the competition's supported runtime. Measure its failure profile, train targeted adapters, and add specialist capabilities only when their benefit is demonstrated. The discarded debugging/product hypotheses no longer gate core implementation. Research novelty remains unproved; documents 15–18 are historical evidence, not the current product mandate.

**Status, October 29:** P1 remains incomplete, but the admission blocker is closed. **Corpus072 is now training-admitted** (manifest `fa984ca3ff1006e2cf7817a8ee67f613fb4e37a5b603bdc6d5e61b586f623887`, content identity `c081880c71b9f78ffb4fdcf319d0959e8d7dfcb39878b8ac06f510f2d088f103`): all four gates are bound to recorded review evidence, the corpus lives in R2 rather than on the development machine, and the real worker's own preflight accepts it. Its 51 tasks / 954,733 input tokens / 262,593 supervised targets are still all development-exposed, so a 50M-target run would be 190 repetitions of the same data. A screened public task pool now supplies **2,966 tasks across 507 repositories and 439 owners**, split into repository- and owner-disjoint cohorts including a **445-task confirmation cohort**; those tasks still need environments, replay and their own admission. The full local regression passes **904 tests with zero skips, Torch enabled**. No GPU training has started, no throughput has been measured, and no Runpod resource was created, started, stopped or modified. See [the training unblock and data-scale cycle](docs/42-training-unblock-and-data-scale.md).

**Developer handoff:** [P1 complete developer handoff](docs/41-p1-complete-developer-handoff.md) explains the implementation, mathematics, data, instance/storage history, known failures and remaining work, with code, task and artifact inventories. Also see [current readiness](docs/39-p1-current-readiness.md) and the [implementation journal](docs/40-p1-implementation-journal.md).

## Reading order

| Document | Purpose |
| --- | --- |
| [Training unblock and data scale](docs/42-training-unblock-and-data-scale.md) | Corpus admission, R2-resident corpus transport, two-layer verification, the screened public task pool and campaign arithmetic |
| [Complete P1 developer handoff](docs/41-p1-complete-developer-handoff.md) | Start here for implementation boundaries, evidence inventories, mathematical contracts and remaining acceptance gates |
| [Current P1 readiness](docs/39-p1-current-readiness.md) | Current evidence, open admission requirements and the next GPU decision |
| [Pinned public data intake](docs/33-public-data-intake.md) | Acquired shard, measured metadata, conversion gaps and quarantine gates |
| [Full-checkpoint training qualification](docs/32-full-checkpoint-gpu-qualification.md) | Actual H100 update/reload evidence, memory measurements and remaining long-run gates |
| [P1 requirements audit](docs/28-p1-requirements-audit.md) | Published phase exit evidence, broader open obligations and measured resource limits |
| [H100 validation and content-fidelity finding](docs/30-p1-h100-validation.md) | Successful restored deployment; three repeated Unicode content failures in repository context |
| [P1 GPU session report](docs/27-p1-gpu-validation-report.md) | Actual inference, two repair attempts, corrected local grading, limits and cleanup |
| [P1 acceptance checklist](docs/26-p1-acceptance-checklist.md) | Gate-by-gate evidence and remaining failures |
| [P1 deployment handoff](docs/25-p1-deployment-handoff.md) | Corrected serving lock, durable recovery and future Pod procedure |
| [P1 implementation history](docs/24-p1-implementation-status.md) | Preserved development checkpoints and unsuccessful attempts |
| [Data requirements and acquisition](docs/23-data-requirements-and-acquisition-plan.md) | Specific source shortlist, schemas, 3×50M candidate mixtures, contamination controls and intake gates |
| [R0 implementation and correctness](docs/20-r0-foundation.md) | Contracts, CLI, schemas, mathematical ledger, offline checks and bounded integration acceptance |
| [Cloud preparation](docs/21-cloud-preparation.md) | Actions needed for Runpod, DigitalOcean, R2 and the model handoff |
| [Platform implementation and model handoff](docs/19-agent-platform-and-model-handoff.md) | Current architecture, staged implementation gates, mathematical specification, model intake, and live plugin verification |
| [Reproduction cycle results](docs/18-reproduction-cycle-results.md) | Latest evidence: real defect, three baseline repairs, detailed performance analysis, and no product promotion |
| [Failure-first research study](docs/15-failure-first-research-study.md) | Current conclusion: ranked failure families, competing systems, mathematical hypotheses, and rejection conditions |
| [Task cards and source audit](docs/16-failure-evidence-and-source-ledger.md) | Concrete published attempts, reproduction gaps, source reading depth, and media access limitations |
| [Replication and selection protocol](docs/17-replication-and-selection-protocol.md) | Next 8–14-hour cycles, fair baselines, statistical design, and the product adoption gate |
| [Novelty audit and alternatives](docs/14-novelty-audit-and-alternative-directions.md) | Historical audit rejecting Change Compiler; alternatives are not adopted |
| [Developer pain points and change synthesis](docs/13-user-painpoints-and-change-synthesis.md) | Historical candidate; novelty assessment superseded by document 14 |
| [Continuous implementation plan](docs/12-continuous-implementation-plan.md) | Living 8–14-hour cycles, phase gates, mathematical and statistical assurance, mandatory cycle closeout |
| [Joint strategy and code competition](docs/11-code-track-and-joint-strategy.md) | Start here: differences between tracks, aggregate runtime math, agent priorities, submission gates |
| [Competition facts](docs/01-competition-facts.md) | Verified requirements, deadlines, organizer clarifications, unresolved questions |
| [Judging strategy](docs/02-judging-strategy.md) | Criterion-by-criterion evidence and public judge information |
| [Research positioning](docs/03-research-positioning.md) | Prior art, public competition projects, choice of research question |
| [Technical proposal](docs/04-technical-proposal.md) | Mathematical formulation, assumptions, proofs, counterexamples |
| [Evaluation protocol](docs/05-evaluation-protocol.md) | Data isolation, baselines, ablations, statistics, claim gates |
| [Execution and resources](docs/06-execution-and-resources.md) | Dated milestones, compute scenarios, decision gates |
| [Paper and submission](docs/07-paper-and-submission.md) | Argument structure, word allocation, tables, final checks |
| [Risks and decisions](docs/08-risks-and-decisions.md) | Failure responses, open decisions, organizer questions |
| [Sources](docs/09-sources.md) | Linked source register with access and verification boundaries |
| [Planning validation](docs/10-planning-validation.md) | Arithmetic checks and logical review of this package |

Start with documents 19 and 12 for the adopted build, then document 11 for competition constraints. Documents 13–18 preserve prior investigations; their no-go decisions do not block the core agent. Update document 12 after every implementation cycle. Source IDs link to the source register or directly to primary pages.

## Two deliverables and deadlines

| Deliverable | Success criterion | Current deadline in Los Angeles |
| --- | --- | --- |
| Research paper | Five equally weighted research criteria | November 12, 2026, 15:59 PST |
| Agent entry and team merger | Rules accepted and team finalized | November 25, 2026, 15:59 PST |
| Agent archive | Private-test repair performance within the official runtime | December 2, 2026, 15:59 PST |

The code track currently allows one submission per day and two final selections. Its twelve-hour budget covers all tasks, including setup. The research plan's illustrative twelve-minute task cost is not a deployment allocation. See document 11 for sources and the corrected runtime model.

## First actions for the next round

1. Measure throughput on one bounded GPU run at a realistic sequence length. Nothing in this project measures tokens per second for this configuration; the recorded 67,231 MiB reading came from a 24-token fixture and constrains memory, not speed. The campaign planner refuses to forecast duration or cost without a measured rate.
2. Measure peak memory at the corpus's longest example, 24,366 input tokens, before committing to an 80 GB card.
3. Pull environments for the selected public tasks, grade baseline and reference outcomes, and capture native trajectories through the official runtime. Eligibility is not a task.
4. Complete the rights review on the new pool. Licence labels are screened, not cleared.
5. Freeze the 445-task confirmation cohort before any optimization touches the train cohort, and record the freeze.
6. Assemble the replayed trajectories into a new quarantine corpus and admit it through the same four gates on its own evidence. Corpus072's admission says nothing about a successor corpus.
7. Compare trained candidates against a frozen baseline and that held-out cohort before claiming gains or novelty.

Both submissions remain planned. The earlier reproduction pilot used hosted Codex inference; P1 subsequently used the user's existing Runpod GPU. Full-corpus post-training and competition submission have not started; a synthetic single-update training qualification has run. Competition rule acceptance was confirmed in the authenticated Chrome session on October 7.

## Run the foundation checks

```sh
python3 -m unittest discover -s tests -v
python3 -m zenithsync --help
```

The original 26-test foundation used Python 3.13.7 and the standard library: [R0 validation](evidence/r0/local-004/receipt.json). The expanded suite passed 81 tests in the qualified tokenizer environment: [P1 validation](evidence/p1/local-006/receipt.json). The current suite is 904 tests; run it with the Torch checks explicitly enabled, since a smaller default run is not equivalent:

```sh
ZENITHSYNC_TEST_TORCH=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 <qualified-python> -m unittest discover -s tests
```

To check that a training run could start from the bucket alone — corpus, both
verification layers, tokenizer assets by digest, all eight model files, the
schedule digest and the real worker preflight — run:

```sh
python3 scripts/verify_r2_training_readiness.py --artifact-manifest evidence/data/corpus072-admission-001/r2-artifact-manifest.json --model-manifest evidence/p1/model-intake-001/model-manifest.json --corpus-sha256 fa984ca3ff1006e2cf7817a8ee67f613fb4e37a5b603bdc6d5e61b586f623887 --content-sha256 c081880c71b9f78ffb4fdcf319d0959e8d7dfcb39878b8ac06f510f2d088f103 --worker-config configs/p1-corpus-qualification.json --schedule-seed 7401 --schedule-sha256 4664ecf632b35fad11dfa6d9d3e1ff19cfddb352816e99bb8750c8167cd1f06b --output <new-dir> --prefix artifacts/v1 --env-file .env
```

It needs R2 credentials in a private `.env` at the repository root and reads
nothing else local except the two manifests.

Optional tokenizer checks require the pinned dependencies; do not interpret skipped checks as verified. These software tests are separate from inference and repair evidence.

The official starter and harness assets are now downloaded into ignored local storage. The unchanged starter compiled with ADK submission 0.2.12 and Google ADK 1.36.1. See the [official contract audit](docs/22-official-contract-audit.md) for source discrepancies, compiler tests and remaining runtime gates.

The [Linux integration receipt](evidence/r0/linux-002/receipt.json) records 25 checks using actual released tools; all 26 core tests also pass in the official sandbox image. This is local AMD64 emulation, not GPU qualification or official competition grading.
