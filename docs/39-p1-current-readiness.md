# Current P1 readiness

Updated October 15, 2026. **P1 is incomplete. Keep Runpod stopped.**

Pubmed_parser89 native002 supersedes native001 for prospective content review.
Five explicitly attributed pre-publisher amendments strengthen four created
scripts and redirect the unavailable upstream-commit lookup to verified HEAD.
Expected subjects use standard-library XML ancestor traversal, not the production
XPath. Baseline reproduction now raises on both fixture mismatches; after the
unchanged source repair, exact subject strings match across all8local XML fixtures.
Original upstream tests6/6 and generated tests3/3 pass;9 selected post-fix/native
inspection commands succeed. Warning output remains visible. The source patch is
unchanged at645bytes/SHA b20a2b1bebd4ab77ba5f9f18d1f4d173fa9d4c5a320b8f0a2fa9c4d3afaf3205.
Native002 contains36charged calls/76messages,21,137inputs/2,879shifted targets;
plus8,192reserve leaves3,439headroom. Full history review, publisher grading,
rights/privacy/splits and training admission remain pending. No model inference.
Evidence: `evidence/data/pubmed89-native-evidence-002` (22 files/543,076 bytes),
R2-published and independently restore-verified.

Pubmed_parser89 native001 completed offline:36 charged calls/37 exchanges/
76 messages,23,958 inputs and5,064 shifted targets. Plus8,192 reserve leaves618
headroom.645-byte patch SHA256:
`b20a2b1bebd4ab77ba5f9f18d1f4d173fa9d4c5a320b8f0a2fa9c4d3afaf3205`.
Source snapshot3df1667fc6ac8165474b474cb0372f4a03b5cc8084f5641c01fc3da894193ba4
passes exact tracked-file/tree and parentless-history verification; reused Debian
artifacts match prior recorded hashes. Native upstream tests pass6/6 and created
subject tests pass3/3. One historical git-show command fails because original
commit history is intentionally absent; this failure is preserved. Three created
diagnostic scripts have no assert nodes and print broad conclusions; their full
failure semantics require review. The fourth has13assert nodes. Native001 is held
for explicit diagnostic amendments, replay and full history review; no publisher
assets accessed or corpus inclusion. Temporary source shard and container removed.
Evidence: `evidence/data/pubmed89-native-001`,3 archive files/58,433,088 bytes;
all64 inner files R2 restore-verified. Redundant restore removed after comparing
retained-copy hashes. No Runpod or model inference.

Pubmed_parser89 paired full-package controls now pass in diagnostic Python3.9
ARM64 runtime22a6c7b28646fb187bb6da4ecf5567ba9d21948453b87cd4fa2eaf11e9281d6a.
Both baseline and candidate pass6 unchanged upstream tests (7 warnings), including
30,000 MEDLINE records. The teacher's one-line subject XPath repair changes only
pubmed_parser/pubmed_oa_parser.py. Independent192-case XML fixture matrix varies
category count, wrapper depth, subject count, inline text and namespace handling;
baseline fails96 cases and candidate fails0. Expected strings come from fixture
construction, not the production XPath. Input XML bytes and PMID are preserved;
full non-subject output equivalence is not established. Finite dependent cases do
not imply population repair rate or universal XML correctness. Original source trees
unchanged within tests, containers removed, network disabled. Native replay,
history review, publisher grading and training admission remain pending.
Evidence: `evidence/data/pubmed89-runtime-001`,3 archive files/19,050,793 bytes,
all18 inner files R2 restore-verified. Redundant restored archive removed after
retained-copy hash checks. Latest disk24GiB free; avoid new bulk runtime builds.

Nbgrader1410 native002 complete content review now passes: all58messages read,
12 nonoverlapping sections bound to exact message hashes. Approved only as an
explicit nine-amendment tool-action derivative, without final conversational response.
Rights/privacy/splits/training remain unapproved. Before first publisher access,
all replay/history/token artifacts were frozen; hashes remained unchanged afterward.
Publisher controls now hold strict grading: base27/28passes, reference28/28passes.
The zero-credit test has the expected fail-to-pass transition. Exactly one metadata
transition disagrees: test_get_username is labelled FAIL_TO_FAIL but passes both
roles with USER=root. Original native baseline001 already demonstrated its missing
USER environment failure; the current environment fix was made before oracle access.
Do not claim strict publisher compatibility or change labels to manufacture a pass.
Candidate publisher grading and corpus integration remain blocked by this gate.
The publisher specifies Python3.6; current Python3.9 ARM64 is not historical equivalence.
Evidence: `evidence/data/nbgrader1410-history-review-002` and
`evidence/data/nbgrader1410-publisher-controls-001`; both R2-published and
independently restore-verified (4 files / 16,260 bytes and31 files / 78,603 bytes).
Any subsequent candidate
revision must be labelled post-evaluator-exposure; preserve frozen native002.

Nbgrader1410 native002 now supersedes native001 for prospective review. Nine
explicit pre-publisher amendments strengthen four diagnostic scripts and omit
pytest warning summaries in five commands without changing selected tests. The
baseline reproduction now raises AssertionError for its three zero-credit failures;
the same script passes after the unchanged480-byte source repair. Eight selected
post-fix commands succeed; original28-test suite summaries are visible. Unexpected
exceptions and missing expected ValueErrors now fail the comprehensive diagnostic.
The final script asserts one notebook-cell result and four direct zero forms,
and limits its conclusion to those cases. Original native001 remains preserved.

Native002:27 charged calls/28 exchanges/58 messages;15,991 input tokens and3,428
shifted targets. Plus8,192 reserve leaves8,585 headroom. Source patch SHA remains
795cf2122874f61f740cadac78d2742c9d886756d45259d386b0caaa1461fdff.
Complete history review now passes; strict publisher grading is held as above. No corpus inclusion,
training admission or model-performance claim. Evidence:
`evidence/data/nbgrader1410-native-evidence-002` (22 files / 441,154 bytes),
R2-published and independently restore-verified. The subsequent review/freeze/control results are recorded above.

Nbgrader1410 native001 completed:27 charged calls,28 exchanges,58 messages,
23,464 input tokens and4,768 shifted targets. With8,192 output reserve, total31,656
leaves1,112 headroom. All15 run_command calls exited0, but several diagnostics
print pass/fail without enforcing failure exits; this is explicitly not equivalent
to all assertions passing. Three generated scripts contain no assertions, and the
final script claims all other functionality unchanged beyond its finite evidence.
Warning-heavy native test output clips summaries. Hold this original trajectory
for diagnostic strengthening and full content review; no corpus inclusion yet.
Patch480 bytes, SHA256
`795cf2122874f61f740cadac78d2742c9d886756d45259d386b0caaa1461fdff`.
Snapshot image7ce46c4457602c8b7c6d7251e7064c1210204d1b7388e748742b55f815e3f938
matches all pinned source bytes/tree and contains one parentless commit with no
remotes or accessible original commit. Git was added offline from32 downloaded
Debian packages; Python3.9 ARM64 remains diagnostic-only. Native tool observations
are fresh; no Gemma inference or publisher assets accessed. Replay container and
temporary source shard removed. Archive `evidence/data/nbgrader1410-native-001`:
3 files/61,111,594 bytes, all65 inner files R2 restore-verified. Redundant restore
archive removed after retained-copy hash comparison. Next: explicit pre-publisher
diagnostic amendments, fresh replay and complete review.

Nbgrader1410 package follow-up: diagnostic runtime image
`sha256:dc3a9a70e81cff8d6a0b9ad5654a44270dd6faef8e049a96c1d0d44496495481`
uses Python3.9 ARM64 and respects source requirements nbconvert5.6.1 /
traitlets4.3.3. Offline installation and pip check pass; 64 downloaded wheels and
installed freeze are preserved. Initial baseline001 had27 passes/1 failure because
USER was absent. Setting USER=root to match the container user yields28/28 unchanged
utility tests for both baseline and candidate, with105 warnings per role. No tests
were edited. Full package-import controls reproduce200/20,200 baseline failures
and0/20,200 candidate failures. A real nbformat code cell containing output zero
is graded10/10 by baseline and0/10 by candidate. Only nbgrader/utils.py differs;
source trees remain unchanged during tests. This is not the full nbgrader suite,
original x86 publisher runtime, native replay or training admission. Runtime and
control evidence: `evidence/data/nbgrader1410-runtime-001`,3 archive files /
23,955,236 bytes, R2-published and independently restored with all82 inner hashes
verified. Redundant restore copy removed after comparing retained archive hashes.
Next: parentless source snapshot and fresh native trajectory replay. Latest disk
check shows25GiB available; avoid additional bulk downloads.

Next data candidates: nbgrader1410 and pubmed_parser89 are no longer blocked
on source acquisition. Their exact pinned source trees contain 519 files /
19,343,321 bytes and 43 files / 17,505,238 bytes respectively. Acquisition used
an explicit 25,000,000-byte cap per tree/archive, verified every Git blob and
complete tree membership, and accessed no publisher repair/test assets. The earlier
10 MB source-budget failures remain historical evidence. Source archive:
`evidence/data/held-source-acquisition-002`, 3 files / 30,332,298 bytes; all570
inner files independently R2 restore-verified. Capacity metadata archive:
`evidence/data/held-source-capacity-001`, 7 files / 181,092 bytes, also verified.

Nbgrader1410 isolated-function boundary controls: exact AST-extracted
get_partial_grade, 20,200 finite cases per role. Baseline has200 failures at zero;
the teacher's > to >= source change has zero failures. Three additional zero
representations also pass for the candidate. This is not full-package execution,
native replay, publisher grading, training admission or a statistical repair-rate
estimate. Evidence: `evidence/data/nbgrader1410-boundary-001`, 5 files / 59,714
bytes, R2-published and independently restore-verified. Package follow-up above supersedes the runtime hold; native replay and content
review remain pending.

Storage update: removed ten redundant historical corpus directories (Corpus052–059,
plus the old Corpus053/054 restore copies), releasing 87,298,048 allocated bytes
(83.3 MiB). Every historical corpus was reconstructed and validated before deletion
using freshly R2-restored Corpus060 token/audit files and archived exact manifests.
Corpus060 remains local and unchanged. Historical direct local paths no longer exist;
restore their original transfer manifests when rerunning old scripts, or reconstruct
from the saved path mappings. Do not interpret missing historical paths as lost data.
Archives: `evidence/data/corpus-dedup-001` (13 files / 552,244 bytes) and
`evidence/data/corpus-dedup-release-001` (4 files / 12,048 bytes), both R2-published
and independently restore-verified. Allocation totals are not exact APFS free-space
gains. This does not resolve the separate Finder/File Provider issue.

Latest pipeline change: corpus assembly now validates with `IndexedCorpus`,
retaining metadata rather than all token arrays. Explicit aggregate budgets remain
required; each token/audit file has a separately configurable 16 MiB default cap.
The prior 10,000,000-byte budget was caller policy, not a structural corpus limit.
On unchanged Corpus060, indexed versus materialized Python traced peak allocations
were 5,440,623 versus 64,348,796 bytes. This is a single local measurement, not OS
RSS or industrial throughput. Both readers produce identical summaries. The exact
9,888,249 referenced-byte budget succeeds; one byte below rejects. Manifest bytes
(29,355) are bounded separately, explaining the 9,917,604-byte transfer total.
The loader retains its 16 MiB manifest ceiling and 1 GiB default aggregate ceiling;
larger corpora require explicit capacity review, not unchecked limit removal.
All 615 local tests pass with Torch checks enabled, zero skips (22.680 seconds).
Evidence: `evidence/p1/corpus-capacity-001` and
`evidence/p1/full-suite-qualification-015`; both R2-published and independently
restore-verified (3 files / 5,070 bytes and 4 archive files / 622,959 bytes,
respectively; all 333 archived suite files verified). No new training data or training
admission is claimed; the 45-task corpus remains insufficient for the planned run.

Docker API is responsive (server 29.8.2); the earlier startup blocker is resolved.
Historical calendar native001 controls: that earlier candidate
fails 34/78 finite value cases and 20/78 column checks, preserves inputs in all
78 cases, and fails the separate single-schedule column-projection check. Baseline
fails 60/78 value cases and mutates inputs in all 78. Native001 remains excluded;
these finite checks do not establish universal correctness. Evidence:
`evidence/data/marketcal11-merge-controls-002` (11 files / 102,508 bytes,
R2-published and independently restore-verified).

Previously qualified: **pytypes37 native004** has passed mechanical and complete 72-message
content review as an explicitly amended tool-action replay. It contains no final
narrative response. It is now stored in quarantine Corpus059; R2 restoration and
local restored-worker ingestion checks pass. Eight explicit
pre-publisher amendments strengthen diagnostic assertions; a hash-bound completion
removes diagnostic scripts and runs the declared unittest command with checkout
PYTHONPATH. Native003's missing-import-path failure is retained, not counted as a
successful run. Native004 completes 34 charged calls / 72 messages: 17,018 input
tokens, 3,036 shifted targets; plus 8,192 reserve = 25,210, leaving 7,558 headroom.
Its 578-byte patch changes only pytypes/type_util.py; SHA256
`79b47b6e8ca62402b90e892a0e63a84bba8473ce497ab9d474ad6a8011c3e9f8`.
The declared unittest suite passes all 103 cases. Independent finite controls
previously found two baseline failures and zero candidate failures across 19 cases;
these do not establish correctness across arbitrary typing versions/cache states.

Publisher assets were accessed only after native004 artifacts were frozen.
Candidate matches reference on **all 156 published outcomes: 117 pass and 39
expected persistent failures**, with zero disagreements. Full-versus-selected
controls confirm identical test-phase outcomes for every published label in both
baseline and reference. Eight unlabelled module-helper setup errors remain recorded
and excluded from publisher comparison. The full pytest run is **not a pass**.
Mechanical admission and scoped history review pass. Rights, privacy, final split
isolation and training admission remain separate gates. No model-performance claim.
History review: `evidence/data/pytypes37-history-review-004` (4 files / 19,221
bytes, independently restored from R2 with matching hashes).

Evidence: `evidence/data/pytypes37-qualified-replay-004` (103 files / 1,321,378
bytes, R2-published and independently restored with every hash matching).
Earlier runtime archive: `evidence/data/pytypes37-runtime-001` (117 inner files,
3 outer files / 18,558,764 bytes); earlier replay and setup failures:
`evidence/data/pytypes37-replay-evidence-002` (59 files / 503,360 bytes), both
independently restore-verified. Historical failed attempts remain preserved.

New quarantine inclusion: **thu-ml__tianshou-67**. Exact source commit
`dd3e2130bb8fce5ac636a6d686a20b31584ea336` was acquired and tree-verified.
Full-package baseline002 uses a hash-verified NumPy1.23.5 wheel in temporary
container storage and writable /tmp cwd. All9unchanged upstream base tests pass;
all6pickleprotocols and same-process Pipe still reproduce RecursionError.
Earlier NumPy1.26 np.int failures and read-only log-directory failure are retained.
No task-source or upstream-test modifications were used to fix the environment.

Paired baseline/candidate controls001 use the cached teacher source-only repair:
__getstate__ copies the instance dictionary and __setstate__ updates it directly.
Both roles pass the identical9base tests. Baseline fails all60finite controls and
all7direct pickle/Pipe checks with RecursionError; candidate passes60/60 and7/7.
The finite cases cover empty/scalar/list/array/nested/tensor/None payloads, shared
array references and a self-cycle across6protocols. They are not independent random
trials or a universal/subclass/cross-version proof. Source unchanged within each
run; containers removed. Native004 completes37chargedcalls/38exchanges/78messages.
Ten explicitly attributed diagnostic amendments retain the core repair/action order;
two compacted assistant-created test scripts preserve all36assertions and exact
non-print executable AST. Original expected-value correction remains in sequence.
Fresh observations only; no history truncation. Native004 has22969inputs/4868shifted
targets; plus8192reserve=31161, leaving1607headroom. All13selected strengthened/
verification command statuses pass. Source patch remains552bytes, SHA256
`e7069df8c976929e449efa4d325069ebc49280cfbaffc78a911e9d56b6fbaa4f`.

Earlier held attempts remain:001overflows1324tokens;002overflows811and hits a
5second diagnostic-startup timeout;003uses20seconds and passes diagnostics but
overflows565. Their failures are preserved. Native004 now passes linked mechanical checks, including publisher grading:
all4publisher outcomes match reference with zero disagreements (base3pass/1fail,
reference4pass,candidate4pass). Evaluator assets were first accessed after freezing
replay/history/token files; all frozen hashes remain unchanged. Complete78message history review now passes as an explicitly amended tool-action
replay; no final narrative response exists. Rights/privacy/final splits and training
admission remain pending. Included only in quarantined Corpus060. Grading evidence: `evidence/data/tianshou67-grade-004`
(44files/52340bytes,R2-published and independently restore-verified).
The publisher specifies Python3.7; our verified Python3.10 diagnostic runtime is
not historical-environment equivalence or hidden-grader proof. Native evidence001/002/003
is R2 restore-verified; latest evidence `evidence/data/tianshou67-native-evidence-004`
(24files/596585bytes) is also independently R2 restore-verified.
Evidence: `evidence/data/tianshou67-qualified-controls-001` (33files/17232705bytes,
R2-published and independently restored with matching hashes).

Diagnostic runtime image:
`sha256:b957a1389672a1a49ae4834557a8e848fc166339017a2a02ab52e1b721848ca5`.
Python3.10 is not original CI Python3.6-3.8 equivalence. NumPy1.23.5 wheel
17,059,657bytes, SHA256:
`5e05b1c973a9f858c74367553e236f287e749465f773328c8ef31abe18f691e1`.
Replay snapshot image405f9b6b5bb056406a5c65426fdd00d5be856b662d3f162078d6335d612a1bd6
now has globally installed NumPy1.23.5, passing pip check, and independently
verified parentless source/tree/hash identity. Initial ignored-file snapshot failure
is retained; corrected snapshot includes all upstream tracked files. Inherited
Docker layers are not audited. Latest df shows26GiB available. Earlier cached
layer unpacking reduced33GiBto27GiB; do not confuse download size with disk footprint.
Earlier standalone evidence6files/21012bytes and package-runtime evidence30files/
1594912bytes are R2 restore-verified. No global prune or Runpod compute used.

Current inspection corpus: **Corpus060**, 45 examples / 45 tasks / 44 repository
groups, 894,687 input tokens and 253,048 supervised shifted targets. All 44
Corpus059 records are unchanged. Manifest SHA256:
`cb8fc8a8dadda2250e18bb350e7f0121c8e98fb27bce2f7015e9d81c7bca9f13`.
The corpus remains quarantine-only: **zero training-admitted tokens**. Its91files/
9917604bytes and integration evidence21files/274167bytes have been R2-published and
independently restored with matching hashes. Complete Tianshou history review:
`evidence/data/tianshou67-history-review-004` (4files/20620bytes,restore-verified).

Restored worker source matches all42manifest-listed repository files. Original and
restored corpus produce identical9-update schedules, all45examples once, zero
overshoot. All10resume boundaries match exact remaining sequences;10corrupted
cursors reject. Actual worker rejects quarantine before model access, no training
output. These are ingestion/scheduling checks, not optimizer/full-model/GPU
qualification. Evidence: `evidence/p1/corpus060-ingestion-001`
(17files/45070bytes,R2restore-verified). Release evidence3files/5734bytes is also
independently restore-verified.
No production source change; latest610-test regression remains historical
qualification014 with its recorded scope.

Tianshou repository/network identifiers do not overlap retained known/reserved
identifiers. All990lexical pairs over45issue texts match an independent set/Fraction
oracle, with no new Tianshou flags. Inherited flags and semantic/detached-fork
uncertainty remain. No reserved issue bodies read. New history credential-pattern
screen passes; this is not privacy or rights approval. Source LICENSE preserved.

A50Mtarget run would require197fullpasses plus149544targets; diversity remains
insufficient for the requested training programme. More qualified data is essential.
Corpus060 is near the current explicit10MBinspection bound; subsequent acquisition
must plan bounded growth or shards rather than silently treating this bound as a
training-data sufficiency target. Fresh hash comparisons allowed removal of redundant
new copies:10776576allocatedbytes, not a guarantee of exact APFS free-space gain.
Finder synchronization remains unresolved.

The calendar example passes complete 70-message history review as an explicitly
attributed pre-publisher-exposure derivative with an externally designed completion.
The Django example's earlier review remains a post-evaluator-exposure derivative.
Rights, privacy, frozen splits and broader qualification remain separate gates.
Earlier Corpus058 credential-pattern screen: all 43 examples, zero indicators; this is not
privacy approval. All 903 lexical issue pairs were checked against an independent
exact oracle, with no new calendar flags. Calendar candidate GitHub repository and
network IDs do not overlap retained known/reserved networks. Inherited flags and
semantic/detached-fork uncertainty remain unresolved. No reserved issue bodies read.

Calendar native003 now passes mechanical admission: 33 charged calls, 70
messages, 22,940 input tokens and 5,000 shifted targets; with 8,192 reserve,
31,132 tokens leaves 1,636 headroom. Its 2,493-byte one-file patch matches the
predeclared hash. Native002's context overflow is retained as failed evidence.
Publisher access followed the native003 artifact freeze: all five labelled utils
tests have qualified base/reference transitions (4/5 versus 5/5); candidate 5/5,
zero disagreements or skips. Separate unchanged upstream suite: 41/41. Prior
independent finite controls: 78 plus singleton projection and 3,072 expanded checks.
Complete history review and quarantine integration are now recorded in
`evidence/data/corpus058-integration`; rights/privacy/splits and training approval
remain open. Original review: `evidence/data/marketcal11-history-review-003`. Evidence:
`evidence/data/marketcal11-qualified-replay-003` (99 files / 1,262,632 bytes,
R2-published and independently restore-verified).

Latest production regression: **610 tests passed, zero skips**, 21.421 seconds,
local CPU with explicit reduced-model checks and offline model-hub settings.
Fixed the shared evaluator probe's Python3.6-incompatible subprocess options;
stdout/stderr capture, decoding, timeouts and check behavior are preserved.
The first evaluator infrastructure failure is retained, and fresh historical
runtime controls and grading succeeded after the fix. Evidence:
`evidence/p1/full-suite-qualification-014`, R2-published and restore-verified,
including all 332 archived source/evidence files. Old byte-bound probe receipts
remain historical; do not silently claim they match the changed implementation.
Historical Corpus058 would require 203 full passes plus 235,768 targets for 50M;
Corpus059 figures are given above. Neither is an approved training schedule.

Historical Corpus058 manifest SHA256:
`a15f8294e74fc51929ae2cf3c411c27174a6d1b0c828eb032ff7848cf2841372`.
Evidence: `evidence/data/corpus058-integration` (18 archived files / 263,915 bytes,
R2-published and independently restore-verified), plus the qualification evidence above.

Local storage: a fresh metadata census of 41,024 files still finds 598 nonresident
files, 24,850,330,811 logical bytes and zero allocated bytes. The largest is an
old 23.3 GB model restore placeholder; a live R2 HEAD confirms that model object
is present at the prior verified size (not a new content verification). Finder
reports the repository uploading, with no folder-level unresolved conflict. A
scoped read-only File Provider consistency check produced no output and was
terminated after 80 seconds; it is inconclusive. The Finder synchronization
error is **not resolved**. Avoid bulk hydration near disk capacity; do not infer
corruption or delete solely from residency flags. Evidence:
`evidence/data/repository-residency-audit-002`.

Current ingestion check: restored worker source matches the current 42-file
package. Corpus058 original/restored schedules are identical (9 updates,
zero overshoot); all 10 resume boundaries match and 10 corrupted cursors reject.
The actual worker rejects quarantine before model access. Evidence:
`evidence/p1/corpus058-ingestion-001` (18 files / 53,463 bytes, R2-published
and restore-verified). This is not GPU or optimizer recovery. Redundant new
corpus/evidence restores were released only after fresh retained-copy hash checks:
10,280,960 allocated bytes; no exact APFS free-space gain claimed.

Storage update: all eight R2E raw shards are now R2-verified and independently
restore-tested; their redundant local raw Parquet files are removed. This latest
release freed358MiB of file allocation. Restore instructions and exact manifests
are retained in `evidence/data/r2e-raw-release-000-004/RESTORE.md` and the005–007
release directory. Selected examples and their evidence remain local.

Current candidate: **pypinfo137 native003** completes 33 charged calls and 70
messages. Seven assistant-attributed amendments strengthen diagnostics and reduce
verbosity; an attributed completion fixes custom OR grouping. Fresh token audit:
19,601 input tokens + 8,192 reserve = 27,793, leaving 4,975 tokens of headroom.
The final 28-test upstream suite passes without skips. Independent finite
predicate controls find zero disagreements across 512 row evaluations (baseline:
81); this is not a BigQuery service test or all-domain proof.

Publisher grading now finds an evaluator conflict: the candidate passes 29/30
collected tests; the failing exact-string check rejects parentheses around the
custom expression. The reference passes 30/30 but disagrees with 46/512 finite
predicate cases. Five extra database tests were explicitly accounted for in the
diagnostic control comparison. Candidate remains on hold; full-history review
and admission are incomplete. This candidate is not in Corpus058; no training admission.
See `evidence/data/pypinfo137-publisher-evidence-001`. The original native001 OR failure and native002
context overflow remain preserved as predecessor evidence. See
`evidence/data/pypinfo137-corrected-replay-003`.

Verified redundant pypinfo archive copies released 124,706,816 allocated bytes.
The earlier proposal's authorship-label correction is retained separately in
`evidence/data/pypinfo137-proposal-attribution-002`.

Additional candidate `rsheftel__pandas_market_calendars-11`: the historical
Python3.6/pandas0.20.3/numpy1.16.6 amd64 baseline passes all 41 tests with zero
skips. The same diagnostic confirms correct date lookup and object row dtype,
while preserving both target defects (three-schedule merge error and input-list
mutation). The newer-stack baseline and its four failures remain retained.
Multiple stack variables changed; no single-version causal claim is made.
Native001 replay completed before the interruption: 32 charged calls, 68
messages, 30,010 input tokens and 6,363 shifted targets. With the 8,192 reserve,
it exceeds the context limit by 5,434 tokens. The 9,104-byte submitted patch also
retains temporary diagnostic files. Candidate remains excluded; publisher grading
and admission are pending. Additional independent merge controls could not
start on October15 because Docker API was unavailable. The backend was launched
but readiness is unconfirmed. Evidence:
`evidence/data/marketcal11-legacy-evidence-001` and
`evidence/data/marketcal11-replay-evidence-001`.

Local runtime blocker: Docker startup logs report `installRootPasswordNeeded`
during helper/socket configuration. Its API remains unavailable; the user needs
to complete the Docker/macOS prompt directly. Calendar partial static review also
finds a single-schedule projection/aliasing regression and an unasserted success
claim. Six verbosity amendments are prepared but unexecuted; no new context or
correctness result is claimed. See `evidence/data/marketcal11-static-review-001`.

## Earlier qualification history

The entries below retain prior snapshots and are superseded by the current
summary above where they differ.

Updated October 11, 2026. **P1 is incomplete. Keep the Runpod GPU stopped.**
No real training corpus is admitted and no learned coding-performance gain has
been demonstrated. Corpus051 contains 35 examples across 35 tasks and 34 declared
repository groups: 671,515 input tokens and 191,210 supervised shifted targets.
KubeVirt99 is newly added; all 34 corpus050 records remain unchanged. Its 71 files
(7,438,027 bytes) are R2 upload/restore-verified. Independent recount agrees;
original and restored 31-update schedules are byte-identical with zero target
overshoot. Training loads reject quarantine. Emcee295 remains a context-reserve
exception. All assignments remain provisional train.

Corpus051 lexical checks cover all 595 pairs against an independent set oracle;
no new flags, inherited PennyLane overlap remains. Fresh KubeVirt repository metadata plus 37 inherited hash-bound observations
show no known reserved-network overlap; all 34 prior draft assignments remain
unchanged. The finite credential screen covers all 35 decoded histories with
zero indicators. Staged deployment reproduces the exact 31-update schedule;
inspector and worker reject quarantine before model access. These are scoped
checks, not privacy clearance, frozen splits or GPU training qualification.
Rights, frozen splits, sufficient diverse data and full training readiness remain
unqualified. A 50M-token run would repeat this corpus approximately 261.49 times;
repetition does not supply new diversity.
Manifest SHA256:
`72e7afca145a53ead7e118c3f93d37e505941616c2850e04516f71b284f1833e`.
Evidence: corpus051-integration-001, corpus051-publish-001,
corpus051-restore-001 and corpus051-similarity-002.
Latest full local regression: 530 tests, zero failures/errors/skips, Torch enabled.
Strict Mocha JSON validation is implemented and checked against real publisher
reports and integrated into mechanical admission. AWS X-Ray assessment rejects
its 11-token context-reserve excess. The 72-message review is complete with
silent output truncation and instruction-coverage limitations retained. No full 31B GPU
or learned-performance claim follows.

Local CPU dependency recovery completed: a fresh runtime outside cloud-managed
storage passes all 89 tests in the 19-module training/data regression cohort,
with zero failures, errors or skips. Its pinned core wheels match PyPI hashes;
installation and regression evidence are R2 restore-verified. This is CPU and
reduced-Gemma acceptance, not full 31B GPU readiness. Evidence:
cpu-recovery-001 and p1-data-regression-003 under evidence/data.

Recent screened candidates remain held: Touvlo34 has a callback-order contract
mismatch; Fuzzyfinder19 has unresolved API alignment; Flake8-1642 suppresses
start/ancestor directory errors beyond the publisher's HOME-only correction.
None is included in corpus048. Full corpus rights, split, runtime and training
admission remain unresolved. Repository-wide local regression completed: all 506 tests passed, with zero
failures, errors or skips (p1-full-regression-011, stable source snapshot). This includes optional
HTTP-resource and Parquet checks and the enabled CPU Torch tests.

Corpus045 review reconciliation linked 29/30 exact histories to named review
or admission evidence; Optuna was linked indirectly. Its printed-only diagnostic
has now been explicitly amended and replayed. All 64 amended messages have been
read and bound in 12 nonoverlapping review sections; structural coverage and
mechanical cross-artifact assessment pass. This derivative replaces the old
Optuna entry in corpus046. Fresh independent grading passes all nine GridSampler
cases, matching the reference (base: eight passes). The reconstructed history
encodes without truncation to 17,588 input tokens and 3,539 supervised shifted
targets. Error observations at messages 31, 35 and 43 remain visible. These are
finite repair/token checks, not training admission or learned-model performance.
Evidence: optuna3545-full-history-review-001, optuna3545-amended-admission-002,
optuna3545-amended-grade-003 and optuna3545-amended-tokens-001.
These evidence classes are not interchangeable semantic approvals. Lmfit's
inherited review chain and Signac's 78-message full-range review are reconciled.
A new structural coverage verifier passes 13 targeted tests after the 463-test
baseline; it cannot approve training or establish review truth.
Evidence: corpus045-review-coverage-004, lmfit487-review-chain-001 and
signac622-review-coverage-001.

Optuna attribution now binds both exact-revision dataset cards, the pinned MIT
notice, and five read_file observations to their exact tracked source lines.
Four source files plus LICENSE were captured as verified Git blobs from the
clean snapshot. This covers explicit source reads, not every indirect shell
output, dependency or teacher-service term. Corpus046 draft split identities
are rebound to the previously captured repository-network evidence; all 30 task
assignments are unchanged. This is not a new live network lookup or a frozen
held-out split. Evidence: corpus046-attribution-001. Rights and split gates remain
open; no corpus is admitted by these records.

A reusable exact lexical similarity checker now passes 25 targeted regression
tests (six new checker tests plus existing issue/corpus checks). On corpus046,
its inverted-index counts match the exhaustive oracle across all 435 pairs;
71 have positive intersection. With Jaccard >= 1/10 or containment >= 1/5,
only the two PennyLane tasks are flagged. Review of their full issues and all
46 shared shingles found different defects and shared issue-template material.
This is within-corpus lexical screening, not semantic independence or held-out
contamination clearance. Positive thresholds and exact rational comparisons
avoid rounding ambiguity; explicit resource exhaustion raises without returning
partial results. Evidence: corpus046-similarity-001. The new full 486-test
run includes this module and its CLI tests.

Candidate-scale lexical screening now covers the existing 1,575-task / 902-repository
cohort, using pinned local shards and excluding reserved repositories before
issue-body reads. The new bounded CLI and pair-visit limit pass 28 targeted tests.
An independent exhaustive oracle agrees on all 1,239,525 pairs: 229,535 positive
intersections and 967,495 posting-pair visits. At Jaccard1/2 or containment4/5,
five pairs are flagged and reviewed: two exact-text duplicate pairs (Mobly and
Hidrokit) receive candidate leakage families; three other pairs describe distinct
tasks with shared boilerplate. Patch equivalence and unflagged semantic
independence are unproven. No candidate is newly admitted or replay-qualified.
Evidence: candidate-similarity-001. This advances screening scale, not qualified
training-token volume; corpus046 remains unchanged.

Candidate duplicate families are now applied through merge_leakage_groups in
zenithsync/splits.py. Existing families and transitive links remain indivisible;
cross-split links fail without reassigning tasks. Frozen drafts, unknown tasks,
invalid links and label collisions reject. Thirty-one targeted tests pass,
including independent graph reachability and a forced hash collision.
The 1,575-task candidate draft now has 1,573 leakage families; only four task
family labels changed. This draft uses issue-text hashes and declared repository
names, not trajectory-token identities or verified fork roots. It cannot admit
training. Evidence: candidate-leakage-plan-001. Fresh full local regression
run004 passes all 486 tests with no failures, errors or skips. CPU Torch checks
are enabled; this is not full-model GPU qualification.

Rally1469 now has two explicitly attributed diagnostic amendments, with the
original source/documentation patch unchanged. Actual-source validation passes
seven constructor and twelve session/connector lifecycle cases; both programs
reject the base and five injected faults reject. Fresh native replay completes
39 charged calls without tool errors and removes its container. Reconstructed
history has 82 messages / 40 exchanges; pinned token audit yields 19,709 input
and 3,513 supervised shifted targets, leaving 4,867 tokens after the output
reserve. These results do not measure TLS, Elasticsearch requests or memory leaks.
Fresh independent grading matches all 197 reference case outcomes with zero
disagreements. All 82 messages are content-reviewed and bound in 15 complete,
nonoverlapping sections; mechanical cross-artifact assessment passes with no
blockers. The 22-file review/grading archive (386,660 bytes) is uploaded and
independently restore-verified in R2. The reviewed derivative is now added to corpus047;
all earlier corpus046 records remain unchanged. Evidence: rally1469-full-history-review-001,
rally1469-amended-grade-001, rally1469-amended-admission-001 and
rally1469-reviewed-grade-publish-001 / restore-001 under evidence/data.

The reusable source-capture module now exports selected committed regular blobs
with explicit size limits and Git-object identity checks. Seven new tests and
seven review-coverage regressions pass. Applied to Rally, seven captured files
cover all eight direct read observations, including the two sequential source
edits. LICENSE, NOTICE and a transformation supplement are preserved. The
23-file /189,253-byte archive is uploaded and independently restore-verified.
Evidence: rally1469-attribution-001 and attribution-publish-001 / restore-001.
This does not close indirect shell/dependency or dataset/teacher rights gates.
Full local regression005 now passes all 493 tests with zero failures, errors
or skips, including this new module and enabled CPU Torch checks.

Corpus047 now has a fresh metadata-only GitHub identity audit for all 30
candidate repositories and four reserved repositories. All 34 resolve, with no
canonical/declared fork-network overlap. All 31 current token-input identities
are bound into a validated draft split; the 33 earlier repository identities
are unchanged. All assignments remain provisional train. No development or
confirmation cohort or frozen split is claimed. Evidence: corpus047-split-001.
Detached copies, historical copies and semantic contamination remain unexcluded.

Linkding691 now has an explicit two-command diagnostic amendment plan.
On the actual pinned source, both replacement programs pass the patch and reject
the base; three injected option/exception faults reject. One check runs a real
local child process and verifies argv/gzip bytes; no browser/network success is
claimed. Fresh replay completes27 charged calls and native submission with the
unchanged1,025-byte patch. Paired grading reproduces base5/6 and reference/candidate
6/6. All58 messages are reviewed in11 bound sections, preserving errors11/37.
Token audit:17,612 input /7,571 supervised targets, no truncation,6,964 reserve
margin. Mechanical checks pass. The reviewed derivative is now added to corpus048;
all31 prior corpus047 records are unchanged. Evidence: linkding691-amended-native-002, amended-grade-001,
amended-tokens-001, amended-admission-002 and full-history-review-001. Original
source evidence remains unchanged.

Older sections below describe prior checkpoints.

This file is the current acceptance summary. Cycle details, failed attempts and
superseded results are preserved in the [implementation journal](40-p1-implementation-journal.md).
The [implementation plan](12-continuous-implementation-plan.md) retains the phase
scope and campaign assumptions. Update this summary and the journal after each
cycle; do not append historical logs to this summary.

## Numba6653 failure-reporting correction — October 11

Five explicitly attributed amendments now cover deprecated-prefix warning semantics,
pytest exit propagation, one asserted CPU JIT example and a strict CUDA-disabled
import check. Fresh standalone checks retain the real pytest collection error,
reject a wrong JIT result and reject an injected import failure. Four explicitly
labeled output fixtures preserve exit codes 0, 1, 2 and 5 with bounded displayed
output. These fixtures are not repair examples or model-generated successes.
Fresh replay completed with 35 charged calls and 74 messages; failed tool messages
23, 33 and 43 remain visible. The unchanged 362-byte patch matches the publisher
reference on its one test case. Mechanical assessment passes. Token audit: 17,157
input / 6,353 supervised, leaving 7,419 tokens after the output reserve.
All 74 messages have been reviewed and the bounded review is recorded in
numba6653-full-history-review-001. The derivative replaces the older Numba record
in quarantined corpus044; training stays unapproved. No CUDA hardware execution is claimed.
Two source-read failures and one grading preflight hydration rejection were retained;
subsequent attempts succeeded without weakening integrity checks. Evidence:
numba6653-claims-validation-001, claims-native-003, claims-grade-002 and
claims-admission-001. The 55-file / 534,569-byte qualification archive is uploaded and independently
restore-verified in R2 (claims-publish-001 / claims-restore-001 receipts).

## Statsmodels8339 diagnostic correction — October 11

Four explicit diagnostic amendments now distinguish output-contract checks from
numerical verification and population-statistical claims. Twelve finite direct-sum
checks pass; five altered outputs and fifteen forced assertion failures are rejected.
The original false-zero verification behavior is reproduced. The numerical reference
shares SciPy p-value calculation and does not establish statistical calibration.
Fresh replay completed: 130 diagnostic-file tests passed, 33 charged calls and
unchanged source patch. History has 70 messages; token audit is 14,841 input /
4,181 supervised, with 9,735 reserve margin. The intentional null-sample assertion
failure and its explanation remain visible. Native replay and diagnostic archives
are independently restored from R2. Fresh grading matches 131 publisher cases
(base 130 passed; reference/candidate 131). Full 70-message review and mechanical
admission pass. The reviewed derivative is integrated into quarantined corpus043;
training remains unapproved.
Evidence: statsmodels8339-diagnostic-001, diagnostic-validation-001 and
statsmodels8339-full-history-review-001. The 44-file / 566,819-byte qualification
archive is independently restore-verified in R2.

## Boltons205 diagnostic qualification — October 11

Seven explicit assistant amendments correct unchecked comparisons, unconditional
success reporting and reversed custom-priority commentary. Pinned real-package
checks reproduce the base false-success bug; all corrected scripts pass on the
existing candidate patch. All 19 separately falsified assertions fail as intended.
This proves bounded failure propagation, not general numeric correctness.
Diagnostic evidence (34 files / 99,114 bytes) is independently restored from R2.
Fresh replay completed with 31 charged calls and the unchanged 948-byte patch.
All 66 messages are reviewed. Fresh paired publisher grading is 0/2 base and
2/2 reference/candidate. Token audit: 20,215 input / 6,926 supervised, with 4,361
tokens remaining after the output reserve. Mechanical admission passes; the
reviewed derivative is integrated into quarantined corpus042. The 8,640 finite
ordering cases remain checks within one repair, not independent repair examples.
Evidence: boltons205-diagnostic-001, diagnostic-validation-002 and
boltons205-full-history-review-001. The 67-file / 488,959-byte qualification and
integration archive is independently restore-verified in R2.

## Pennylane5716 amended replay qualification — October 11

Mini-source replay now supports explicitly hash-bound command amendments. Original
candidate bytes remain unchanged; all three changed commands have assistant
attribution in fresh events and message mappings. Reconstruction/admission reject
missing or inconsistent amendment claims, modified terminals and unbound commands.
Fresh snapshot verification and replay completed: 74 messages, 35 charged calls,
18,874 input / 5,791 supervised tokens and 5,702 context reserve margin.
Independent grading matches 44 cases (32 base passes, 44 reference/candidate),
including three supplemental backend checks. Mechanical admission passes.
The multi-batch diagnostic remains a failure. Full review of all 74 messages is
complete, and the derivative is integrated into quarantined corpus041. The indexing
argument covers zero or one batch axis; it does not establish higher-rank support.
The issue supplies the proposed fix. The 117 separate-execution comparisons are
finite consistency checks, not independent repair examples. Both failed tool results
remain visible. Evidence: pennylane5716-full-history-review-001.
Targeted 27-test regression passed;
the first broad 459-test run failed on hydration integrity errors and CLI timeouts.
Stable-copy regression passed: 459 tests, 442 passed and 17 skipped. An intermediate
copy missed two fixture paths; both were restored before the passing run. No Runpod use or training approval.
Evidence: pennylane5716-amended-native-002, amended-grade-001, amended-admission-001
and mini-amendment-implementation-001. The 19-file / 95,647-byte review and integration archive is independently
restore-verified in R2. Earlier diagnostic validation remains valid
only for its stated finite fixture domain.

## Apispec full semantic correction — October 11

The complete 78-message review found and corrected stale observed-value reporting,
unconditional final success prose and four pytest pipelines that hid process status.
All seven amendments are explicitly attributed and replayed; the original and
held exit-only derivative remain preserved. The strengthened final check rejects
the base defect and four injected faults. Direct baseline testing reports 563
passes; this is not a claim about the final patch's full-suite result. Independent
final grading matches 117 publisher identities. Token audit: 23,621 input / 3,885
supervised, with 955 tokens remaining after the 8,192 output reserve.
Mechanical admission passes and full semantic review permits quarantine replacement.
The 46-file, 760,877-byte qualification archive is uploaded and restore-verified.
Evidence: apispec950-full-history-review-002, claims-admission-001 and claims transfer
receipts. The reviewed derivative is integrated into corpus040; training stays
unapproved. One diagnostic follow-up remains (Numba6653), alongside wider rights/split review,
data expansion and training runtime qualification. No Runpod use.

## Importlab failure-reporting correction — October 11

Further review found the graph unittest wrapper exited zero despite one real
error from missing python3.6. An explicitly attributed shell amendment now checks
wasSuccessful and rejects empty runs. Real graph errors exit one; separately
labeled one-test passing and empty fixtures verify both branches. Fresh replay
retains the error as a failed tool result: 80 messages, 38 charged calls, same
source patch and reference-informed completion. Untruncated token audit: 24,306
input / 6,664 supervised, 270 output-reserve margin. Fresh grading matches 30/30 exact publisher cases; paired controls reproduce
29 base passes and 30 reference passes. Mechanical admission passes. Full 80-message content review is now complete with
explicit scope: retained failed attempts, truncated full-suite output, finite
checks and reference-informed authorship. It permits quarantine replacement only;
the derivative is now integrated into corpus037, and training remains unapproved. The seven-file review
archive (124,357 bytes) is uploaded and independently restore-verified in R2.
Evidence: importlab23-full-history-review-001 and importlab23-full-review receipts.

## Importlab contract review — October 11

The two disputed diagnostic expectation changes are supported by fresh execution
of nine POSIX cases in four isolated roles (base, teacher, reference, corrected).
Root a.py resolves to a and root __init__.py to __init__ in every role. The teacher
patch independently fails literal-dot initializer filenames; the corrected patch
matches the publisher reference for all nine cases. A local separator/suffix
argument explains the correction; this is not complete import-system correctness.
Evidence: importlab23-contract-review-001. Full history and preservation-wording
review remain pending; reference-informed attribution stays mandatory. Corpus036
is unchanged and no training approval follows from this narrow contract result.

## Current CloudEvents correction status — October 11

The concise diagnostic derivative passed six real-source diagnostic checks and
six deliberately wrong-comparison rejection checks. Fresh replay retains 82
messages, 39 charged calls, original failure observations and the same source
patch. Independent grading matches 26/26 exact publisher cases. Untruncated
input is 23,420 tokens with 4,836 supervised tokens, leaving 1,156 tokens after
the 8,192 output reserve within 32,768. Mechanical admission passes; training
approval remains false. Full 82-message review is complete; the derivative is integrated only into
quarantined corpus036. Evidence: cloudevents172-compact-review-001. Earlier versions and their
context rejection remain preserved. Next: Lmfit/Importlab scope review, remaining diagnostic-quality follow-ups,
rights/split gates and diverse-data expansion.

## Amendment admission verification — October 11, 2026

Admission now reconstructs amended histories from hash-bound original and derived
actions, checks implementation and history-plan bindings, and rejects unbound
amendment artifacts. Both amended-only and amended-plus-completion paths are tested.
The latest [regression report](../evidence/p1/amendment-admission-regression-005/report.json)
records 450 tests: 433 passed, 17 skipped, in an isolated local source copy.
Earlier failed runs are retained; cloud hydration and missing isolated-copy fixtures
were resolved without weakening integrity checks. This is consistency validation,
not corpus approval. The 8-file implementation/test archive is uploaded and
restore-verified in R2. Lenskit independent grading now passes; full content review remains pending.

## Datetransform diagnostic correction — October 11

Prepared an attributed replacement for the diagnostic that swallowed empty-input
errors and failed to compare time-feature modes. It now checks twelve finite
row-count/copy-mode/time-mode configurations and six paired output comparisons.
The base fails and the existing source repair passes. Four synthetic faults
(empty exception, ignored time, ignored inplace, and copy-input mutation) are
rejected. The local container was removed. Calendar constants were independently
checked against the standard library. No source patch change or Runpod use.

Fresh replay now completes 27 charged calls with the same 608-byte source patch.
Its 58 messages use 14,550 input / 4,292 supervised tokens, with a 10,026-token
reserve margin. Fresh base/reference controls reproduce 1/3 and 3/3 passes; the
candidate matches all three exact publisher cases. Mechanical checks pass.
Full 58-message review is complete, with 51 unchanged messages and all seven
changed messages inspected. Compatibility observations cover returned columns,
not preservation of default mutation behavior. The derivative is integrated into
quarantined corpus039. Evidence: datetransform-full-history-review-001 and
corpus039-integration-check-001.

## Training-content review — October 11, 2026

Corpus037 remains quarantined. Historical corpus033 lexical review covered 44
matches across 23 histories; that is not complete semantic approval. Reviewed
Signac, Lenskit, CloudEvents and Importlab derivatives have since been integrated.

Lmfit487 full 84-message review identified additional hidden failure statuses in
the first amended derivative: pytest piped through head and a basic-check success
summary without failure assertions. The second derivative has six explicitly
attributed action amendments, including a failing exit for the unrecovered initial
reproduction and an explicit cleared-expression assertion. Fresh replay preserves
four failed tool observations and submits the same 553-byte source patch in 40
charged calls. Its 84-message history has 21,161 input / 5,269 supervised tokens
and a 3,415-token reserve margin. Candidate grading matches all 13 publisher cases
against the separately verified 12/13 base and 13/13 reference controls. Mechanical
checks pass. All new observations are reviewed: 71 messages exactly match the prior full
review and all 13 changed messages were inspected. This derivative is integrated
into quarantined corpus038; no training admission follows.
Evidence: lmfit487-full-content-review-002 and corpus038-integration-check-001.
No full-repository, training admission or learned-performance claim follows.
Five other histories retain diagnostic-quality follow-ups, and full content,
rights, frozen split and runtime admission checks remain open.

See the [corrected review](../evidence/data/munch52-correction-review-002/report.json).

The original Lmfit 487 teacher is held; its corrected derivative is in corpus 033: its independently verified
210-file source snapshot preserves the exact base tree. Base/reference/teacher
publisher results are 12/13, 13/13 and 13/13; 18 finite expression-recovery
sequences fail on the base and pass for both fixes. The teacher sometimes retains
an empty diagnostic string where the reference clears it to `None`. A subsequent
four-sequence diagnostic check reproduced two stronger counterexamples: an old
NameError message becomes the text of a new, unrelated SyntaxError, both within
one parameter and across two parameters sharing an evaluator. Reference clears
the stale state. See the [candidate hold](../evidence/data/lmfit487-diagnostic-review-001/report.json)
and [earlier runtime review](../evidence/data/lmfit487-runtime-review-001/report.json).
An explicitly authored correction now passes fresh replay and exact-patch grading;
the original teacher remains held. The derivative passes 13 publisher cases,
18 recovery sequences and four diagnostic sequences, and its added native checks
pass. Its untruncated history has 21,298 input / 5,514 supervised tokens and uses
40/40 tool calls. The mechanical assessment passes, but rights, split and training
admission remain open. The replay retains a NumPy API compatibility test failure
and a teacher diagnostic's invalid private-method call. See the
[corrected assessment](../evidence/data/lmfit487-mechanical-admission-001/report.json).
The derivative increases quarantined supply, not admitted training supply.

The [corpus034 integration audit](../evidence/data/corpus034-integration-check-001/report.json)
revalidates the restored manifest and independently recounts shifted-label targets.
All 29 sequences fit 32,768 tokens; 27 also satisfy the separate mechanical policy
`input_tokens + 8192 <= 32768`. Emcee 295 and CloudEvents 172 fail that reserve
screen. This does not invalidate their training-length accounting, and passing
the screen does not establish full admission. The input count already includes
supervised tokens; adding those tokens again would double-count them.

One 50M-target-token campaign is exactly `50000000/165734`, approximately 301.69,
current-corpus-equivalent passes. This is descriptive token reuse, not an exact
scheduler epoch count or independent evidence. No corpus is admitted. Expand
diverse, reviewed supply before scheduling a campaign; do not use repetition to
claim that the data requirement has been met.

- [Assembly receipt](../evidence/data/training-corpus-assembly-034/receipt.json)
- [R2 publish receipt](../evidence/data/training-corpus-publish-034/receipt.json)
- [R2 restore receipt](../evidence/data/training-corpus-restore-034/receipt.json)
- [Corpus integrity inspection](../evidence/data/training-corpus-inspection-033/report.json)
- [Integration evidence archived in R2](../evidence/data/corpus034-integration-publish-001/receipt.json)
- [Integration and schedule equality check](../evidence/data/corpus034-integration-check-001/report.json)
- [Explicit training rejection](../evidence/data/training-corpus-denial-032/report.json)
- [Current repository lineage screen](../evidence/data/current-corpus-lineage-024/report.json)
- [Lenskit corrected observation review](../evidence/data/lenskit312-observation-review-002/report.json)
- [Lenskit qualification archive](../evidence/data/lenskit312-qualification-publish-001/receipt.json)
- [Required correction archive](../evidence/data/lenskit312-correction-publish-001/receipt.json)
- [Latest CPU regression](../evidence/p1/subdirectory-replay-regression-001/full-suite-retry.log)
- [Boltons derivative review](../evidence/data/boltons205-compat-review-001/report.json)
- [Jsons completion evidence archived in R2](../evidence/data/jsons86-completion-publish-001/receipt.json)
- [Xhistogram dependency diagnostic](../evidence/data/xhistogram20-compat-review-001/report.json)
- [Dependency diagnostic and wheel archived in R2](../evidence/data/xhistogram20-compat-publish-001/receipt.json)
- [Xhistogram runtime evidence archived in R2](../evidence/data/xhistogram20-runtime-publish-002/receipt.json)
- [Xhistogram publisher-control environment hold](../evidence/data/xhistogram20-control-drift-001/report.json)
- [Conllu completion evidence archived in R2](../evidence/data/conllu35-completion-publish-001/receipt.json)
- [Conllu completed observation and token review](../evidence/data/conllu35-observation-review-001/report.json)
- [Conllu scoped label-language argument](../evidence/data/conllu35-language-review-001/proof.md)
- [Conllu parser runtime qualification](../evidence/data/conllu35-runtime-review-001/report.json)
- [Conllu runtime evidence archived in R2](../evidence/data/conllu35-runtime-publish-001/receipt.json)
- [Gitignore runtime evidence archived in R2](../evidence/data/gitignore38-runtime-publish-001/receipt.json)
- [Gitignore native evidence archived in R2](../evidence/data/gitignore38-completion-publish-001/receipt.json)
- [Gitignore native observation review](../evidence/data/gitignore38-observation-review-001/report.json)
- [Gitignore path-handling runtime review](../evidence/data/gitignore38-runtime-review-001/report.json)
- [Gitignore scoped reasoning and limitations](../evidence/data/gitignore38-runtime-review-001/scope.md)
- [Next candidate triage: Lmfit, Munch and ASDF](../evidence/data/qualification-triage007-review-001/report.json)
- [Triage 007 archived in R2](../evidence/data/qualification-triage007-publish-001/receipt.json)
- [ASDF runtime evidence archived in R2](../evidence/data/asdf1853-runtime-publish-001/receipt.json)
- [ASDF exact native patch grade](../evidence/data/asdf1853-standard-grade-001/report.json)
- [Completion-aware admission evidence archived in R2](../evidence/data/completion-admission-publish-001/receipt.json)
- [Gitignore and Conllu assessment archive](../evidence/data/completion-admission-batch-publish-001/receipt.json)
- [Gitignore and Conllu standard-grade assessment](../evidence/data/completion-admission-batch-review-001/report.json)
- [ASDF mechanical admission assessment](../evidence/data/asdf1853-mechanical-admission-001/report.json)
- [ASDF native observation review](../evidence/data/asdf1853-observation-review-001/report.json)
- [ASDF native evidence archived in R2](../evidence/data/asdf1853-completion-publish-001/receipt.json)
- [ASDF converter runtime qualification](../evidence/data/asdf1853-runtime-review-001/report.json)
- [ASDF finite-domain mathematical check](../evidence/data/asdf1853-runtime-review-001/scope.md)
- [Next boundary and parsing candidate triage](../evidence/data/qualification-triage006-review-001/report.json)
- [Triage 006 evidence archived in R2](../evidence/data/qualification-triage006-publish-001/receipt.json)
- [Next 32-repository qualification queue](../evidence/data/qualification-batch-current-003/report.json)
- [Queue, lineage and issue screening archive](../evidence/data/qualification-batch003-publish-001/receipt.json)
- [Numerical candidate triage](../evidence/data/qualification-triage005-review-002/report.json)
- [Csaps native observation and numerical review](../evidence/data/csaps3-observation-review-001/report.json)
- [Csaps qualification evidence archived in R2](../evidence/data/csaps3-qualification-publish-001/receipt.json)
- [Triage evidence archived in R2](../evidence/data/qualification-triage005-publish-001/receipt.json)

Manifest SHA-256:
`9b694ed3f9aeabff685e6f42298ffad5fc0875685d943016c48e7f88a7ced4d4`.
Content SHA-256:
`c19a5bbc1c1d3dc9fd2a90c60a3e4c2c6c8806e990ca021d5d10f62acc914e3f`.
The restored bundle has 59 files and 6,476,957 bytes. Its one-epoch schedule uses
seed 7401, 27 planned updates and a 9,216-supervised-token update cap. It consumes
165,734 target tokens with zero overshoot. No optimizer steps are implied.

All four admission fields remain null: rights/attribution, split isolation,
runtime qualification and task alignment. Training-purpose loading rejects with
`Quarantine corpus cannot train`. Receipt integrity verifies bytes and bindings;
it does not prove the truth or completeness of the underlying reviews.

## MkDocs Merge18 candidate triage — October 11

Pinned teacher and publisher extraction completed; 33 source actions inspected,
with no known credential indicators. The extracted teacher function uses enumerate
to update the current list slot. It passes 2,343 finite, unaliased navigation-tree
checks against a separately constructed functional oracle. The publisher loop uses
list.index and mismatches 381 cases in that same finite set. Minimal witness:
['a', 'r/a'] under root r should become ['r/a', 'r/r/a']; the publisher loop instead
produces ['r/r/a', 'r/a'] because a previously changed slot equals the next value.
These are extracted-function checks, not full publisher-suite results.
The initial generated fixture exposed shared-dictionary double prefixing; that
failure is retained and separately reproduced. No shared-object/YAML-alias or cycle
support claim is made. The original reproduction also exits normally on the broken
base without comparing actual and expected trees. Correct that diagnostic with
explicit attribution, narrow example-level claims, then perform exact source,
fresh native replay, publisher grading and token review before corpus integration.
Evidence: mkdocsmerge18-static-validation-001/002 and mkdocsmerge18-triage-001.
Corpus044 remains unchanged; no Runpod or new container image downloads.

### Selected-source compatibility follow-up

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

### Complete-tree follow-up and runtime boundary

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

### Python 3.9 compatibility follow-up

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

## Fuzzyfinder19 publisher contract mismatch — October 11

Pinned publisher extraction now shows a substantive API mismatch: the reference
and added test require ignore_case=False, whereas the source teacher implements
case_sensitive=True as mentioned in the issue. Fresh execution of the exact
extracted teacher function rejects ignore_case with TypeError, while its own
case_sensitive keyword gives the expected case-sensitive match. The prior 6,344
ASCII checks establish no compatibility with this publisher interface.
Keep this task excluded from the corpus. Do not silently rename its API to fit
reference tests; task alignment and explicit reference-informed provenance would
be needed to reconsider it. Prior diagnostic findings remain valid but correcting
them alone would not qualify this example. No full publisher-suite result is
claimed. Corpus044 is unchanged. Next: screen another batch004 repository.
Evidence: fuzzyfinder19-evaluator-001, contract-validation-002 and
contract-review-001. One mistyped image digest was rejected before execution;
the corrected bounded probe completed and cleaned up successfully. Runpod unused.

## Fuzzyfinder19 candidate triage — October 11

The first batch004 candidate is extracted from pinned source bytes after reserved
repository exclusion and a full-message credential-indicator screen. No known
indicators were detected; this is not a proof of absence of secrets. All 27 source
actions were inspected without running the original command sequence.
An extracted-function experiment in an offline container passed 6,344 comparisons
against independent subsequence enumeration on alphabet aAb, candidate lengths
0–4 and query lengths 0–2, including collection ordering and duplicates.
This establishes only the stated finite ASCII behavior, not Unicode semantics,
checked-out package behavior or publisher-test qualification.
The original final wrapper swallows an injected pytest failure; a printed expected
match list omits HelloThere. Reproduction/user-scenario diagnostics need assertions
and claims need narrowing. Hold the candidate pending explicit amendments, exact
publisher source/contract checks, fresh replay and grading. Corpus044 is unchanged.
Evidence: fuzzyfinder19-teacher-002, static-validation-001 and triage-001.

## Data expansion queue — October 11

Batch004 is selected against corpus044: 32 distinct repositories, eight from each
of four source-cost rank strata, from 793 remaining eligible repository names.
Independent reconstruction exactly matches the selected records, with zero overlap
with the effective exclusions (including previous batches and reserved repositories).
This is a purposive review queue, not an unbiased benchmark or admitted training data.
Source-proxy lengths do not measure native context or supervised targets.
The lowest-cost selected trace is amjith/fuzzyfinder issue 19; initial issue/action
review and indicator screening are complete as recorded above. Lineage, rights,
source-contract verification and runtime qualification remain pending.
Evidence: qualification-batch-current-004/report.json and verification.json.

The screened pool has 2,621 traces for 1,575 tasks across 902 repository names.
Under a 32,768 context, 8,192 output reserve and causal shift, the deliberately
optimistic bound is 24,575 targets per example. One trace per screened task can
therefore supply at most 38,705,625 targets before prompt masks or any rejection.
This is a bound for the current screened pool, not all available datasets. It does
not prove that multiple attempts on one task add independent information.
Expand unique-task supply and document repeat exposure before the 50M campaigns.
Three planner attempts stopped at cloud hydration metadata changes. Staged bytes
were checked against previously pinned hashes and the successful planner retained
all original integrity guards. No new images, GPU use or training approval.

## Next local cycle

Triage 008 is complete: corrected Importlab is in quarantine; corrected
Icontract remains above the call budget; corrected Marshmallow remains above
the context-reserve budget. The existing stochastic-assignment candidate remains held for demonstrated
probability-validation counterexamples. Triage 009 has runtime evidence for the API-schema candidate and static
evidence for spelling-caption nodes. The corrected API candidate is integrated with verified restore and schedule
accounting. Spelling, Numba and SoftLayer are integrated into quarantine. Rally1469 has a reviewed diagnostic derivative with fresh 197-case reference agreement and passing mechanical checks, now added to corpus047; Pylutron20 remains held on delimiter and rights questions. None is approved training data.
Measure local capacity before any additional container image downloads.

1. Continue diverse task qualification. ASDF1853 passes 28 publisher tests and
   1,024 finite tag-set checks; completed native replay is integrated into quarantine. The corrected Lmfit487 derivative is also integrated; Munch52
   has a corrected derivative integrated into quarantine; its original teacher remains held. Gitignore38 passes publisher controls and
   120 targeted path checks. Native replay and token export are complete;
   quarantine integration is complete; final attribution and admission review remain pending. Xhistogram density compatibility is
   diagnosed, but its historical publisher transition table remains unreproduced;
   25 passing candidate tests and 192 finite numerical cases do not override
   that distinction. Expand diverse task supply from the pinned source cohort, preserving failed
   candidates and explicit source-versus-derived authorship. Keep source credential
   screening ahead of replay; flagged material requires review.
2. Complete observation-level attribution and task acceptance. The completion-aware
   assessor now verifies ASDF, Gitignore, Conllu and corrected Lmfit/Munch exact patches, histories and budgets; this mechanical
   result is not training admission. Conllu has only 520 input tokens of margin
   after the 8,192-token output reserve; re-audit after any prompt or tool-schema
   change. Extend standard grading to the other candidates, then bind reviews
   to the final corpus. Preserve the Dynaconf mirror distinction and investigate
   semantic overlap before freezing evaluation splits.
3. Reassemble, publish, restore and compare token accounting and deterministic
   schedules after each admitted-to-quarantine data change. Quarantine eligibility
   must not be promoted to training approval by a successful transfer.
4. Prepare the exact worker, admitted data bundle, resume checks, GPU validation
   commands and cost cap before asking the user to restart Runpod.

## GPU restart boundary

Request a restart only when a concrete next validation requires the GPU and its
inputs and local checks are ready. CPU checks cannot guarantee full-model GPU fit
or absence of errors. The next GPU session must first measure real-corpus memory,
throughput and checkpoint/resume behavior; it must not launch a long campaign
based on the earlier synthetic update. Obtain the session budget and preserve
checkpoints and evidence on persistent storage. Do not restart a user-stopped Pod
automatically.

The three 50M-token candidates are a changeable experimental plan, not evidence
of sufficient unique data. Repeated exposure is not new data or independent
statistical evidence. Learned gains and industrial readiness remain unproven.


### Signac review archive verified — October 11

The second preservation attempt also rejected cloud hydration metadata drift.
The successful attempt reads the scope note into a stable temporary file, checks
its bytes against the repository source, and checks the staged archive identity
against the report binding. Existing integrity guards remain enabled.

The corrected full-review bundle contains 29 files / 624,776 bytes. R2 publish
and independent restore both passed: evidence/data/signac622-full-review-publish-001
and evidence/data/signac622-full-review-restore-001. The transfer manifest is
saved with signac622-full-history-review-002. The preservation script executed
its history, patch, grade, attribution and review-coverage assertions successfully.
No production code changed; no new full-suite result is claimed.

Corpus034 remains the current quarantined corpus. Next: integrate exactly this
reviewed Signac replacement, recheck token accounting and deterministic schedules,
and publish/restore the new corpus. Rights, split and training-runtime gates remain
open. Runpod was not used. No local datasets or Docker resources were deleted.


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

Cogent2050 qualification hold (2026-10-11): fresh replay and 206 candidate
publisher-patched tests pass, but base collection failure and two malformed
publisher node IDs prevent strict paired qualification. It is not added to
Corpus050. V2 evaluator now preserves the reviewed src/flat import path when
launching pytest; full CPU regression014 passes all522 tests without skips.
See journal40 and evidence/data/cogent2050-qualification-001/report.json.

KubeVirt99 now passes full 64-message structural review coverage and mechanical
assessment. Its review/assessment archive is R2 upload/restore-verified. Corpus
integration was subsequently completed in corpus051; static agent checks and external runtime tests are
explicitly distinguished. The silent 5,000-character source observation cutoff
is retained as a limitation. Evidence: kubevirt99-full-history-review-001 and
kubevirt99-admission-001. Training approval remains false.


### AWS X-Ray70 reporter qualification follow-up

Fresh replay006 uses Mocha's minimal reporter for three full-core test commands.
Each complete native observation reports 320 passing and exit 0; no output
filtering or history truncation was introduced. The 744-byte submitted patch is
byte-identical to replay004 and replay005. Reporter changes occurred after prior
publisher evaluator exposure and are explicitly attributed diagnostic amendments;
this is not a new independent blind repair attempt.

The dot-reporter replay005 completed but increased tokenized input to 26,156.
The minimal reporter reduces input to 20,390 with 8,298 supervised targets.
20,390 + 8,192 = 28,582, leaving 4,186 tokens under the 32,768 context limit.
The output reserve is unchanged. The failed dot alternative is retained as evidence.

Fresh publisher grading003 executes 321 unique full-title tests per role:
base 320 pass / 1 fail; reference and candidate 321 pass / 0 fail. Tracked diffs
remain unchanged during testing and containers clean up successfully. Normalized
Mocha admission002 has no mechanical blockers; training approval remains false.
The exact 72-message history has a newly bound semantic review and coverage audit.
The initial source-cat observation remains capped; relevant source slices were
checked separately. Random sampling observations do not prove distributions.

Corpus051 remains authoritative: this candidate is not yet integrated. Rights,
frozen split qualification, data scale and full-model GPU qualification remain
open. No Runpod use, new image build, or production-code modification occurred.
Reporter comparison evidence: 139 files / 3,340,420 bytes, R2 published,
hash-verified and independently restore-verified. Receipts are stored under
`evidence/data/awsxray70-reporter-{publish,restore}-001/`.


### Corpus052: reviewed AWS X-Ray integration and restored-data qualification

Corpus052 supersedes corpus051 for quarantine inspection. It contains36examples,
36tasks and35declared repository groups:691,905input tokens and199,508shifted
supervised targets. All35prior records are unchanged. Manifest SHA256:
`86f2ed84bdd41950830c466e0646d9fc4c757d142b07336a0e8c5a7d81409877`.
Content SHA256:`c34b2d49713c16203657ca61f9c97f8a1f0e77897bd95276713dda8e9a4d4da8`.
The73files /7,662,870bytes were R2 published and independently restore-verified.

Independent token recount and original/restored schedule comparison agree exactly:
seed7401, one epoch,9216supervised-target budget per update produces32updates,
zero target overshoot. Staged deployment reproduces the same schedule. Inspection
for training and the worker reject quarantine before model access/output creation.
This does not qualify a positive training run or the full31B model. Emcee295 is
still the inherited8192reserve exception; the new AWS example has4186tokens spare.

All630lexical pairs were cross-checked against independent exact shingle sets.
The inherited PennyLane5716/5831containment flag remains; no new pair flags.
Fresh AWS repository/network metadata and inherited hash-bound metadata show no
known reserved-network overlap; detached copies and semantic leakage remain open.
All36split assignments remain provisional train,35unchanged. No frozen split is
approved. Decoded-input credential screening returned0indicators under the finite
rule set; privacy approval remains false. Repository rights remain unresolved.

The full candidate history review and attribution include prior evaluator exposure
before reporter-only amendments. This is a reviewed derived example, not an
independent blind repair. Training gates remain null.50M/199,508 is approximately
250.62corpus passes; repetition is not additional diversity or sufficient data.
No GPU usage or production-code changes in this integration. Qualification evidence
archive91files /598,746bytes is R2 published and independently restore-verified.
Both receipts are saved under `evidence/data/corpus052-archive-{publish,restore}-001/`.


### Next-source semantic preflight: Traitlets517, TSDB649, Restic4446

Three source rows extracted from the existing hash-pinned OpenSWE shard without
reading evaluator patches. Bounded findings bind exact converted message identities.
Traitlets has an observed custom-parent logger mismatch before the change and match
afterward, but its comprehensive diagnostic prints unconditional success without
assertions. Prioritize a freshly executed, explicitly attributed assertion upgrade.
TSDB's metric probe fails compilation, then reports the metric absent; no counter
increment validation established. Restic uses a hard-coded snapshot ID, an echoed
before-fix section, a timeout, and a Go command reporting no tests to run. Hold
those two traces for diagnostic repair/runtime qualification. These findings do
not prove the repairs incorrect and are not exhaustive semantic reviews.

Three-trace source/review archive12files /303,662bytes is R2 published and independently
restore-verified. Exact Traitlets base8b20889da69f5d22485d61609043f8e633dea144 source
preflight verifies5files by Git blob hash (configurable.py, log.py, setup.py,
setup.cfg, COPYING.md). Runtime dependencies include ipython_genutils; the pinned
notice identifies Modified BSD and prior Enthought origin. Capturing the notice
does not approve all observations or dependencies for training.

No new examples admitted; corpus052 remains authoritative and quarantined.
No Runpod usage or Docker downloads/builds. Next: qualify an existing local runtime
against complete pinned Traitlets source and add assertions before fresh replay.

Traitlets pinned-source preflight archive8files /44,563bytes also R2 published and independently restore-verified; receipts saved.


### Traitlets517 complete-source and finite runtime controls

All56tracked source files /464,971bytes match pinned Git tree blobs and modes.
The109,180byte codeload archive SHA256 is
`c1693c2f76c0543dfa12cd7e5c610dddd783e8e0f9b80fe568e351f3b020a8ee`.
Existing local image03c834da87825b7b06ccba27c8c5a0dce07ed29a9d63e7adc50a8066d4e1ee50
used offline with cap-drop and2GiB/2CPU limits. Its testbed interpreter is actually
Python3.9.20 with pytest8.3.3, not the source trace's3.7.17/7.4.4. The image label
is not interpreter evidence. A26KB ipython_genutils0.2.0wheel was installed offline;
its digest matches PyPI version metadata. No new image build or GPU use.

Source import path was asserted. Base upstream suite:406pass,2skip,0failure/error;
all56source file bytes unchanged by tests. Candidate upstream suite has identical
408test identities/outcomes. Candidate source is byte-exact to the trajectory's
command30replacement; the later docstring edit is outside this behavior variant.

Eight deterministic identity tests cover parent chains of depth1/2/8/32, orphan,
nonlogging parent, explicit child override and independent families. Base3pass/5fail;
candidate8pass; unguarded-parent mutant6pass/2fail; discarded-parent mutant3pass/5fail.
All variants execute the same8identities without skips or collection errors.
These are external finite controls, not fresh agent observations, a publisher grade,
or exhaustive correctness proof. Native replay, amended diagnostic assertions,
source-snapshot sanitization and publisher controls remain next. Corpus052 unchanged.
Source/runtime/control archive99files /795,651bytes R2 published and independently restore-verified; receipts saved.


### Traitlets517 replay preparation and sanitized source

Prepared34source commands with exactly one attributed diagnostic amendment at
source message40. All other commands, including both source repair edits, remain
byte-identical to the source conversion. The diagnostic now asserts logger object
identity across the three-level hierarchy and global fallbacks for orphan and
nonlogging-parent cases before reporting finite-case success. The exact amended
script was executed against base/candidate/two faulty variants: base and both
mutants fail, candidate passes. Candidate upstream suite still passes with2skips.
This is not a native replay receipt; original printed observations remain unchanged.

The shallow pinned base checkout matches all56Git blobs and modes and the upstream
tree d9320348d3a96244bcbf52aeaf1e3793c33ab0a8. Sanitization produces parentless
commit b44865c576a8169eb5657db2b78acab64271fa37, exactly one reachable commit,
no remotes, and inaccessible known base/head/merge commits. Archive construction
uses Python tarfile to avoid macOS extended-attribute sidecars. PR metadata IDs
were read; publisher test and solution patches were not inspected.

Snapshot verification is local only; broader image/container qualification remains
open. Replay-input profile exists but lacks a container-qualified snapshot and is
not yet runnable/admitted. Source-preparation archive33files /476,006bytes R2 published and independently
restore-verified; receipts saved. No production-code modifications, Docker build or Runpod usage.
Corpus052 remains unchanged and quarantined.


### Traitlets517 native replay completed; publisher grading pending

Local derived image2c9cc4ab5c8263548daa632fcbd2ae30bafa8c12a576535dbb7968b9d9c5cfb3
was built offline from the already installed digest-pinned parent, with a sub1MB
context and a2GiBminimum free-space guard. Initial tag lookup incorrectly assumed
latest and failed before build; actual isolated-001tag resolved to the expected ID.
Container checks verify all56tracked files, one parentless commit, inaccessible
known historical commits and declared oracle paths, and406passed/2skipped upstream
tests. This checks the mounted filesystem, not inherited layer contents.

Native replay001 completes34charged tool calls including adapter cleanup, then
submission:35exchanges,72history messages. Submitted888byte patch changes only
traitlets/config/configurable.py, including the original docstring edit. The
asserted comprehensive diagnostic passes twice; focused configurable suite reports
32passed twice. Filtered log tests select no tests (293deselected) and return5;
retained as an error. Full-suite native stdout is capped at5000characters, so
those observations cannot independently establish complete counts. External JUnit
controls remain separate evidence; no false count inferred from capped output.

Pinned token audit:22,782input tokens and5,935shifted supervised targets.
22,782+8,192=30,974, leaving1,794tokens under32,768. No truncation or reserve change.
Task-only issue extraction occurs after freezing the replay. Publisher patches
remain unread. Full semantic history review, publisher grading and mechanical
admission are still pending; corpus052 unchanged. R2 native archive52files /
973,301bytes published and independently restore-verified; receipts saved. No Runpod usage.


Storage recovery completed2026-10-12: full23,265,352,448byte R2 model GET
matched SHA2561b9b1d622a93f02c0d33f98e502f233b5d707443af6ddc464ed0bf5498506c20
and the original local model hash. The separate local model weight was deleted
only after verification; tokenizer/config files retained. Repository artifacts
were evicted locally through macOS while retaining iCloud copies. Free disk
space approximately22GiB; .env and docs readable. Recovery receipts reside in
/Users/jiangshengbo/.codex/zenithsync-storage-recovery. The broken .venv was removed
with a173distribution inventory; recreate qualified runtime before implementation.
Restore model weights from R2 to Runpod when needed, not to this low-space Mac.
P1 remains incomplete. Do not pin the full repository/artifacts in iCloud.


### 2026-10-12 — recovered corpus053 and verified R2 round trip

Supersedes the earlier pending Traitlets grading/archive status. The grading and
review archive was restored from R2 (44 files, 198,600 bytes); restored review,
admission, history, patch and token-audit identities agree. Historical evaluator
executions were not rerun during this recovery.

Rebuilt corpus053 from restored corpus052 plus the reviewed Traitlets517 token
candidate. All 36 predecessor records remain identical. The result contains
37 examples, 714,687 input tokens and 205,443 shifted supervised targets. Its
manifest SHA256 is 291d20d9125419ee36b02ce6c54229f73ca12e6da0ac60bd71ca32d656fec19d.
All 75 files (7,913,673 bytes) were published to R2 quarantine and independently
restored with the production transfer code. The restored corpus passes full
corpus validation and independent token counting. Training access is rejected.

Seed 7401, one epoch and a 9,216-target update budget produce 33 updates with
zero target overshoot; original/restored schedule files are byte-identical.
The inherited dfm__emcee-295 input-plus-8,192 reserve exception remains open.
35 targeted corpus, batching, scheduling and object-store tests pass in the
small recovered runtime. This is not the historical full regression suite or
GPU qualification. Some iCloud file reads completed after a delay; that does
not prove the general iCloud issue resolved.

Evidence: evidence/data/corpus053-recovery-001. Working copies are outside
iCloud under /Users/jiangshengbo/.codex/zenithsync-p1-recovered. No model weights
were restored to the Mac and no Runpod was used. Rights, privacy, frozen split
qualification, refreshed similarity checks, data scale and full runtime
qualification remain open. P1 remains incomplete; corpus053 is quarantine only.

Recovery validation evidence also published and independently restore-verified: 32 files, 166,092 bytes. Explicit archive excludes credentials. Removed redundant selection staging after matching each file to the restored corpus identities. Mac free space remains approximately21GiB.


### 2026-10-12 — corpus053 qualification follow-up

Recomputed all 666 within-corpus lexical issue pairs against independent exact
shingle sets. Production inverted-index counts and rational overlaps agree. Only
the inherited PennyLane5716/5831 containment pair is flagged at Jaccard1/10 or
containment1/5; no new lexical flag. This does not establish semantic isolation.
Fresh GitHub Traitlets repository metadata plus hash-bound inherited observations
yield no known reserved repository-network overlap. All36 previous assignments
are unchanged;37 assignments remain provisional train, not a frozen split.

Complete decoded-input credential screening with the pinned tokenizer and
tokenizers0.22.2 reports37 examples,0 indicators under four rule families.
Privacy and training approval remain false. The recovered runtime initially
lacked replay_source_teacher during test collection; restored its production
dependency closure and reran:53 tests pass, no skips. Both logs are retained.
This remains targeted CPU validation, not the full historical suite or GPU fit.
Evidence: evidence/data/corpus053-checks-001. No Runpod used.

The qualification bundle is now R2 published and independently restore-verified:46 files,366,005bytes. Receipts and content-addressed manifest are retained beside the checks. Mac free space remains approximately21GiB.


### 2026-10-12 — Build290 source diagnostic review

Selected pypa__build-290 from the existing15-candidate queue and extracted only
repo/instance/trajectory/messages/tools from the hash-verified R2 shard. Reference
patch metadata was not read. All assistant actions and the user issue were
inspected, along with selected tool observations; this is not a complete semantic
history review or native replay.

The source imports /build/src while editing /testbed, then copies the candidate
to /build. Its later git-stash baseline attempt reverts /testbed alone, without
binding the imported module to pristine source. Pytest-to-tail also returns zero
while printing failure. The filtered suite reports41 passing/1deselected, and a
separate requested test node does not exist. Final submit has no recorded result.

Eight synthetic executions of four extracted diagnostic bodies show the early
execution diagnostic returns zero when the runner is not called; the later
assertion correctly rejects that fixture. Both constructor diagnostics and the
later assertion nevertheless accept deliberately wrong forwarded arguments.
These are finite diagnostic counterexamples, not real-package failure evidence.
The source patch may still be correct. Retain the original and hold for an
explicitly attributed native replay with one import root, pristine baseline,
forwarding/output/error controls, grading and full-history/token qualification.
Corpus053 is unchanged. Evidence: evidence/data/build290-source-review-001.
No Runpod used.

Build290 review bundle (8 files,109,666bytes) published and independently restore-verified in R2. Released the98,620,316byte temporary source bundle after matching every local file to the verified R2 manifest. Selected evidence retained; no model weights downloaded.


### 2026-10-12 — Build290 real-source controls

Downloaded the exact base8d93fc48c68236b37621353a5800eeb7cd078f54 archive from
GitHub. Initial strict export rejected docs/changelog.rst symlink; retained the
original archive and explicitly omitted that documentation symlink from the
49-regular-file control export. Root MIT notice and source SPDX header preserved.
The source-observed patch applies cleanly and changes only src/build/__init__.py.
Every base file still matches its recorded checksum after testing.

Five focused controls run against base/candidate and one dropped-context mutant
in separate read-only, offline containers with the import path asserted exactly.
The already-installed image uses Python3.9.20, versus3.10.19 in the source trace;
pep5170.10.0 and toml0.10.2 wheels were hash-verified against PyPI metadata and
installed offline into temporary storage. No image pull or Runpod used.

Base:5 API-related errors; candidate:5 passes; mutant:3 passes,1 assertion failure
and1 backend error. Controls cover default runner identity, exact forwarding,
instance isolation, runner exception propagation, and an actual PEP517 backend
call capturing stdout and stderr separately. The mutant drops cwd/environment
and is caught. This supports the candidate under these finite controls; it is
not native replay, full upstream qualification, publisher grading or a correctness
guarantee. Corpus053 remains unchanged and training admission remains closed.
Evidence: evidence/data/build290-controls-001.

Build290 control archive:164 files,405,739bytes, R2 published and independently restore-verified. Source, dependency wheels, notices, three variants and executable controls are included. Receipts saved with the focused evidence.


### 2026-10-12 — Build290 upstream ProjectBuilder parity

The complete42-case tests/test_projectbuilder.py runs on both immutable base and
candidate exports in separate offline containers as UID65534. Initial attempts
both reported41pass/1fail: a console-script lookup failed because Docker tmpfs
defaulted to noexec. A separate live probe recorded os.access(X_OK)=false under
noexec and true with explicit exec. Repeating with /tmp execution allowed inside
the disposable container yields42pass/0fail/0skip on each variant. No tests or
source inputs were modified. Base checksums still match.

Initial reporting compared ordered case lists and stopped despite equal case
sets; corrected comparison uses unique full identities. All42 case IDs and
statuses agree. The original trace's permission test also passes as nonroot.
This is the complete ProjectBuilder module, not the entire repository suite.
The Python3.9.20 alternate-runtime limitation remains. Two additional dependency
wheels (filelock3.13.1 and flit_core3.2.0) were verified against PyPI metadata.
Evidence: evidence/data/build290-upstream-001. Native replay and publisher grading
remain pending; corpus053 unchanged, no training approval and no Runpod usage.

Build290 upstream evidence archive15files/130,918bytes is R2 published and independently restore-verified. Official SDK wheel metadata is readable again; native replay still requires restoring its qualified environment, without bulk hydration of the wheelhouse.


### 2026-10-12 — official native SDK environment recovered

Created a fresh Python3.13 environment outside iCloud under
/Users/jiangshengbo/.codex/zenithsync-p1-recovered/native-runtime-recovery/venv.
Four official SDK wheels match existing lock hashes. Resolved159 macOS-compatible
wheels, pinned every artifact URL and SHA256, verified342,321,717download bytes
and1,354,754,496expanded bytes, then installed offline with required hashes.
This is a new resolved local environment, not byte-identical reconstruction of
the deleted environment or qualification of Linux/GPU training. pip check passes.

Imports verify swegemma0.2.10,adk-submission0.2.13,google-adk1.36.1,
adk-eval-core0.1.0,Torch2.14.1,Torchvision0.29.1,Transformers5.13.1.
Docker connectivity succeeds. A real official SDK smoke test uses an offline,
unmounted disposable container: successful command returns exact marker; failing
command preserves exit7; status charges exactly2calls; container absence verified
after cleanup. No model loaded. All53 staged targeted tests pass.

Evidence: evidence/p1/native-runtime-recovery-001. Replay source dependency closure
and reserved-task metadata are staged outside iCloud. Build290 native replay is
still pending. Mac free space approximately18GiB after installation; no Runpod used.

All159 runtime wheels (342,321,717bytes) are R2 published with full remote hash verification. Removed the duplicate local wheel cache; installed environment retained. The14-file/2,202,390byte recovery evidence bundle is independently restore-verified. Wheel archive has not been independently restored as a whole in this step.


### 2026-10-12 — Build290 exact-tree native replay

Restored all archive file modes and the documentation symlink into a fresh
parentless Git snapshot. Its tree7acd87ff28ad38ad32904ffe749f603f5151162b matches
the GitHub base-commit metadata exactly. The original upstream commit is not
present locally; one snapshot commit, no remotes, clean tracked tree verified.
Built a small offline layer on the installed parent; image
da88d35608545331c6805002f6e64170c7809198e6309fed667df869ffe6b0a8
imports the base checkout and has no runner parameter before repair. /build
is an explicit alias of the same checkout. Named inherited oracle paths absent;
inherited layer bytes remain unaudited.

Native replay completed40charged calls,41exchanges including submit, and verified
container removal. Three explicit assistant amendments: source46 verifies import
origin instead of copying to a second checkout; source50 runs the five finite
runner controls; source58 preserves pytest exit status instead of tail masking.
Original repair and remaining command order preserved. Submitted2041byte patch
SHA256c7af65b21d0a13f0ccb589aaeb04a6cfc039e6d05fc2b70a6fe490c1db8bd68e
is byte-identical to the source-observed patch. Allfive strengthened controls pass.

Fresh replay retains errors at source52/58 (root permission check) and62
(nonexistent test node); source64 reports41pass/1deselected. The separate nonroot
42-case upstream comparison remains external evidence, not an agent observation.
Initial preparation failures (raw history not converted; missing staged hashed
module) occurred before command execution and were repaired through existing
conversion and exact source copies. No source observations reused.

Publisher grading, independent task-body binding, token/context audit and full
semantic history review remain pending. Corpus053 unchanged. Evidence:
evidence/data/build290-native-001. No Runpod or model execution.

Build290 native archive43files/682,411bytes is R2 published and independently restore-verified. Includes exact source snapshot, offline image recipe, input bindings, attributed profile, replay events and source implementation.


### 2026-10-12 — Build290 publisher grading and context audit

Independent pinned SWE-rebench-V2 task/issue fields were extracted after replay
was frozen; publisher patches were isolated to evaluator input. Reconstructed
native history has84messages/41exchanges. Temporary428,839,266byte source shard
was removed after extraction and checksum verification; original remains in R2.

Initial grading stopped on missing snapshot audit fields. A live probe supplied
old-commit absence and final container state; no earlier receipt was edited.
Next grading attempt exposed retained Mac UID501 ownership: cap-dropped root
could read but not apply the publisher patch. A separate git-apply probe reproduced
Permission denied. Offline image rebuild normalizes ownership to root, preserving
the exact Git tree. New image615e8aeb9a74826e1d658f5fa4efd272909708199afa6980ddcfa35c70c8784b
passes exact-tree/import/baseline checks. Replay003 is the current graded attempt.

Allthree attempts have identical amendment-profile and submitted-patch hashes.
Repeats occurred after evaluator extraction for infrastructure corrections only;
no repair or action plan changed. They are not independent model trials.

Publisher controls:38log-derived keys expand to42unique full case identities.
Three truncated-parameter collision groups are explicitly reconciled. Base41pass
and1fail; reference42pass; candidate42pass; all expected transitions match and
no candidate/reference disagreement. Publisher's newly passing case is
test_runner_user_specified. Publisher scope excludes test_init; separate nonroot
full-module42-case upstream validation remains distinct evidence.

Replay003 token audit:24,401input/7,582shifted supervised targets.
24,401+8,192=32,593, leaving175tokens under32,768. No truncation. Earlier
attempts had24,400and24,402input tokens from fresh runtime observations.
Full semantic history review and mechanical admission remain pending; corpus053
unchanged and training approval false. Evidence:evidence/data/build290-grade-001.
No Runpod or model execution.

Build290 graded-history archive146files/1,936,093bytes is R2 published and independently restore-verified. Historical failed probes and alternate replay receipts are retained; latest admitted-to-review attempt is003, not a training admission.


## 2026-10-12: verified local serving dependency release

Released 9,097,474,048 allocated bytes (8.47 GiB) across 478 resident Linux serving wheel copies after matching the pinned R2 manifest, hashing each local file, and streaming each corresponding remote object through SHA-256. Independent receipt audit confirms every removed path is absent and has a matching pre-deletion verification record. Left 22 nonresident entries untouched. Disk available increased from approximately 18 GiB to 26 GiB; physical free-space change differs from per-file allocation totals. Active Mac runtime retained; no Runpod actions. Restore manifest and instructions: evidence/data/serving-local-release-001/RESTORE.md. This is storage recovery only; P1 and Build290 admission remain incomplete. No claim that all iCloud errors are resolved.

Cleanup evidence archive: six files, 577,487 bytes, R2 published and independently restore-verified. Transfer and both receipts retained in evidence/data/serving-local-release-001.


## 2026-10-12: Build290 mechanical pass, semantic quality hold

Latest replay003 passes production mechanical admission: 24,401 input tokens, 7,582 shifted supervised tokens, 40 charged calls, no mechanical blockers. All 84 native history messages were inspected. Semantic review holds corpus integration: the supervised repair docstring incorrectly promises returned output, and diagnostic command print statements overclaim backward compatibility/output capture/full requirements relative to their assertions. These are quality defects even though external finite tests pass. Preserve original evidence; prepare explicitly attributed corrections, fresh replay, regrading and token audit before reconsidering admission. Repeats after evaluator exposure cannot be treated as independent agent trials. Corpus053 remains unchanged; training approval false. Evidence: evidence/data/build290-admission-review-001. No Runpod usage.

Mechanical admission and full-history review archive: four files, 39,712 bytes; R2 publish and independent restore verified. Coverage contains every index 0–83 exactly once.


## 2026-10-12: Build290 attributed quality correction004

Prepared six explicit source-action amendments, retaining original evidence. New repair differs only in the corrected runner docstring; diagnostics now describe their finite assertions. Fresh native replay completed 40 charged calls plus submission, removed container, and produced patch SHA-256 57883f951188cec342af0177b4dc7bee1874aa144cb7ad6ce88bc2ce4c90e9c4 (2,026 bytes). Publisher base41/reference42/candidate42, all42 full case identities match reference. Mechanical admission passes. Fresh untruncated token audit:24,366 inputs,7,577 shifted targets; plus8,192 reserve leaves210 context tokens. Complete differential review covers18 changed messages and66 exact-byte matches to the previous84-message review; two semantic quality holds resolved. This is an assistant-corrected derivative after evaluator exposure, not an independent model attempt. Corpus053 unchanged pending quarantine integration and cross-corpus checks; training approval false. Evidence:evidence/data/build290-corrected-004. No Runpod usage.

Corrected004 archive:48files/815,648bytes R2 published and independently restore-verified; both receipts retained.


## 2026-10-12: corpus054 quarantine integration

Added the explicitly assistant-corrected Build290 derivative; all37 predecessor records unchanged. Corpus now38examples/38tasks/37repositories,739,053input tokens and213,020shifted supervised targets. Manifest SHA-256 e6ea2242d9af271cac42c628c8a70b7aa24c763efd6b53ba0771675a31be10c0. All77files/8,182,579bytes R2 published and independently restore-verified. Training-purpose loader rejection verified. Original/restored schedules byte-identical:34updates,one epoch,seed7401,max9,216targets/update,zero overshoot. All703lexical pairs match independent exact-set oracle; inherited PennyLane5716/5831 containment flag remains, no new threshold flag. Inherited emcee295 context-reserve exception remains unresolved. Repository lineage/split and credential screening need extension to054; no frozen split or privacy clearance. Data remains far below a50M-token candidate and is not training-approved. Duplicate local assembly staging removed only after comparing every file to assembled corpus. No Runpod usage. Evidence:evidence/data/corpus054-integration-001.

Integration evidence archive20files/245,304bytes also R2 published and independently restore-verified.


## 2026-10-12: corpus054 provisional lineage and credential screens

Fresh GitHub metadata identifies pypa/build repository/network root262827329. All38 provisional assignments validate with37 inherited assignments unchanged and no known reserved-name or fork-network overlap; older metadata observations remain historical. No evaluation issue bodies accessed. Complete decoded-input screening covers38unique examples/739,053input tokens with zero indicators under four credential-rule families. This excludes neither PII nor obfuscated secrets, detached repository copies, semantic contamination or pretraining overlap. Split remains draft, privacy approval false, training approval false. Evidence:evidence/data/corpus054-checks-001. No Runpod use.

Corpus054 check evidence10files/43,196bytes R2 published and independently restore-verified.


## 2026-10-12: context exception precisely diagnosed

All38 teacher-forced sequences fit32,768tokens. This is distinct from reserving8,192tokens for generation. The emcee295 history alone violates the conservative full-history-plus-reserve condition. Exact local native generation-prompt rendering at assistant message indices78/80/82 produces24,754/25,387/27,364tokens, leaving8,014/7,381/5,404tokens respectively. Full history re-render exactly matches the stored27,404token array with hash-verified tokenizer assets. Initial probe errors from default tokenizer mapping return type were corrected by explicitly requesting return_dict=False; not a corpus drift. No truncation, reserve waiver, endpoint execution or GPU memory claim. Next: inspect actual inference budget enforcement and define a measured compatible policy before serving qualification. Training admission stays false. Evidence:evidence/data/corpus054-context-001.

Context audit evidence6files/176,711bytes R2 published and independently restore-verified.


## 2026-10-12: official adapter budget transport verified locally

Current candidate sampling requests8,192output tokens and serving profile caps context32,768. Official ADK conversion and real ADK/LiteLLM HTTP transport to a loopback fixture preserve synthetic user text of1/100,000/200,000characters and send max_completion_tokens=8192 in all three requests, with no truncate_prompt_tokens parameter. These are character-length transport probes, not tokenizer or model tests. Responses are synthetic fixture content and no vLLM server/model executes. The checked client path provides no automatic reserve adjustment for these inputs; do not assume it resolves the emcee295 late-prompt mismatch. Exact deployed vLLM overflow behavior and permitted context-management policy remain to verify before serving qualification. No candidate policy changed, no training admission and no Runpod use. Evidence:evidence/p1/adapter-context-budget-001.

Adapter budget evidence4files/7,734bytes R2 published and independently restore-verified.


## 2026-10-12: pinned-version context validation source audit

vLLM tag0.19.1 resolves to b1388b1fbf5aaef47937fabe98931211684666a6; three downloaded source files match Git blob identities. Exact upstream _validate_input method executed via AST extraction with explicit type/exception doubles passes27 boundary probes. Chat branch requires prompt<32,768 and prompt+requested_output<=32,768; it rejects the three emcee295 late prefixes with8,192 requested output rather than clamping or truncating.4,096 fits those lengths in this method but is diagnostic only, not an adopted or quality-tested policy. Source provenance is not yet pinned-wheel byte equivalence or running-server validation. No production configuration change and no Runpod use. Evidence:evidence/p1/vllm-context-source-001. Next: bind downloaded method to the pinned wheel and qualify permitted request-budget handling before declaring serving compatibility.

Source audit evidence7files/1,436,403bytes R2 published and independently restore-verified.


## 2026-10-12: vLLM validator bound to deployment wheel

Streamed433,132,506bytes from R2 to a temporary file and verified SHA-2566b29fdc200966eda4d0cc4d10b8c338ec32620bb069ad3629d8a78e3b35fd3fa against serving-linux-py312-httpfix.lock.txt. Chat serving/protocol and engine serving source bytes exactly equal the audited tag source. Bound the27-case source-level validator report to these wheel bytes. Temporary wheel automatically closed and released; only bounded source/evidence retained. Thus the deployed artifact contains the audited overflow-rejection method; no live vLLM/CUDA/model execution is claimed. The fixed8192 client budget still conflicts with three emcee295 long prompts. Preserve this serving-policy incompatibility as an open gate; do not classify it as training-sequence overflow or alter data silently. Next CPU work can continue on data qualification while policy compatibility remains open. No Runpod use. Evidence:evidence/p1/vllm-wheel-source-001.

Wheel/source binding evidence7files/159,732bytes R2 published and independently restore-verified.


## 2026-10-12: OpenVPN519 source preflight hold

Extracted the exact selected trajectory from SHA-verified98,551,191byte R2 shard using only repo/instance/trajectory/messages/tools columns; publisher patch column unread and temporary shard released. Selected source inspection finds masked build exit codes, a diagnostic that fails Go internal-import rules, and pending terminal with no observation. Later direct build success is preserved but does not prove behavior. Storage-interface appendix versus configuration-reload issue requires independent semantic reconciliation. Abstract Load(expired v1),Store(fresh v2),Delete(key),Get interleaving loses v2; this is a model-level counterexample under a stated replacement-preservation contract, not a real Go concurrency test. Expired never-read entries also remain after collector removal. Hold before replay; no corpus addition or training approval. Source and model evidence:evidence/data/openvpn519-source-preflight-001. No Runpod use.

OpenVPN519 source preflight evidence8files/83,137bytes R2 published and independently restore-verified.


## 2026-10-12: OpenVPN519 real Go lost-update control

Pinned upstream go.mod/go.sum/errors/license verified against Git blob IDs at53dbe929c360a54a8f3b37b0bdd94d182b7bbf26. Source-observed candidate executes real sync.Map and zitadel AES with an explicitly injected scheduling hook after expiry check. One controlled expired-Get/concurrent-Set schedule fails100/100 candidate repetitions by deleting the fresh token. Separate pointer-entry plus CompareAndDelete derivative passes100repetitions. Both use Go1.24.3 darwin/arm64 and -race; no memory-data-race warning observed. These are deterministic repetitions, not independent statistical trials or a general proof. No whole-repository/publisher validation, issue-reload implementation or memory-retention fix claimed. Hold remains; corpus054 unchanged. Evidence:evidence/data/openvpn519-go-control-001. No Runpod use.

Go control evidence28files/125,862bytes R2 published and independently restore-verified.


## 2026-10-12: OpenVPN519 independent task mismatch confirmed

Extracted only independent task metadata/problem_statement from the hash-verified428,839,266byte task shard; publisher repair/test fields unread and temporary shard released. Actual task asks bypass-name configuration reload without disconnecting clients. The token-storage constructor/Delete/lazy-expiration appendix exists only in teacher conditioning. Source patch modifies storage signatures/lifetime and two callers, with no reload behavior or client-continuity evidence. Exclude current trajectory from corpus expansion: a repaired storage race would still not demonstrate this task. Preserve all evidence and require a separate independently task-aligned attempt for reconsideration. Corpus054 remains38examples/213,020targets, quarantine only. Evidence:evidence/data/openvpn519-task-alignment-001. No Runpod use.

Task-alignment evidence5files/9,804bytes R2 published and independently restore-verified.


## 2026-10-12: selected queue independent-task prompt audit

All 15 selected trajectories joined exactly once to independent task metadata using hash-verified source and task shards. Five teacher PR descriptions match after NFKC/whitespace normalization; ten append additional interface instructions. This classification is not semantic clearance or proof of leakage. Publisher repair/test columns remained unread. OpenVPN519 exclusion remains; GumTree163 is prioritized for full source review because its children-access topic aligns, while the unmodifiable-view contract is teacher-only. Peri93 requires menu/device-language behavior review beyond its storage appendix. Corpus054 remains unchanged and training approval false.

Audit and triage archive: 18 files, 152,644 bytes; R2 quarantine publication and independent restoration both verified, followed by per-file original/restored SHA-256 comparison. Temporary source shards were released. Evidence: evidence/data/queue-task-alignment-001. No Runpod use.


## 2026-10-12: GumTree163 source preflight

Extracted the selected 73-message trajectory from a hash-verified temporary shard; publisher repair/test columns unread. Source patch adds CtVirtualElement.getChildren. Preflight identifies a masked javac failure, later explicit compile/classpath failures, weak printed membership checks, and an unanswered terminal submission. Source-observed Maven summary reports 140 tests with zero failures/errors and one skipped; this is not a fresh validation. Hold for hash-bound base preparation, native replay, direct Maven status/report accounting, and actual-dependency behavioral controls covering both constructors, membership, empty collections, live-view behavior and mutation rejection. Preserve teacher-only contract provenance. No corpus change or training approval.

Six files / 88,750 bytes published to R2 quarantine and independently restored, with original/restored per-file hashes compared. Evidence: evidence/data/gumtree163-source-preflight-001. Temporary source shard released; no Runpod use.


## 2026-10-12: GumTree163 local real-dependency controls

Verified all 243 pinned upstream Git blobs (8,685,528 bytes), then ran baseline and source-patched Maven suites under local macOS arm64 Java21.0.5/Maven3.9.9. XML reconciliation confirms the same 140 unique case identities:139 pass,1 skipped,0 failures/errors in each run. All baseline blobs remain unchanged; only CtVirtualElement.java differs in candidate. Four constructor/input combinations exercise expected membership, backing updates and mutation rejection. Candidate passes; unchanged base and three explicit empty/mutable/snapshot mutants fail with their expected reasons. This is finite real-dependency validation, not native agent replay, publisher grading, universal correctness, or corpus admission. Teacher-only live/read-only contract remains separately attributed.

Archive42files/61,652,387bytes R2 published and independently restored. Every original/restored file hash matched; restored dependency/source archive was opened and all243 upstream blobs rechecked. Two redundant local compressed archive copies removed; bounded working dependencies retained for next replay. Compact evidence:evidence/data/gumtree163-local-controls-001; transfer.json restores full bundle from quarantine/v1. Corpus054 unchanged; training approval false; no Runpod use.


## 2026-10-12: GumTree163 native replay, token qualification, semantic hold

Exact Linux snapshot tree71bafc4594da435bcfe1d4e620abee050c877718 verified offline with243tracked files and one parentless commit. Preparation caught and corrected Git CRLF normalization, unsupported local-image FROM syntax, raw history schema, and missing workspace cache; failed attempt evidence retained. Latest image sha256:8942734895a435029068820b145f9c85d7707bb63217d8eb5e51e4a42bfd8a68. Native replay002 completed36run_command calls plus submit_patch, removed its container, and submitted the exact976-byte source-observed patch. Reconstructed76-message history renders18,751input/6,832shifted supervised tokens without truncation; plus8,192reserve totals26,943.

Semantic hold: source action62 full-suite call times out at30seconds, but source message64 claims all tests pass. This cannot enter training unchanged. Original masked compile failure and weak diagnostic assertions also remain. Separate local full-suite success does not make the native timed-out call a pass. No publisher grading, corpus integration, model execution or training approval. Next requires an explicitly attributed, observation-consistent derivative or separate trajectory, retaining failures.

Native evidence51files/62,812,143bytes R2 quarantine published and independently restored; all original/restored file hashes matched. Removed redundant archive copies after verification; active build inputs retained. Compact evidence:evidence/data/gumtree163-native-evidence-001. Docker image remains local, not yet exported to R2; byte-identical Linux runtime recovery is not claimed. No Runpod use.


## 2026-10-12: correction to GumTree163 narrative hold

Direct audit of all37projected exchanges confirms empty assistant prose, no teacher reasoning, and exact native tool observations including the full-suite timeout. The previous section incorrectly treated source message64 success narrative as entering the projected training candidate; it does not. That rationale is superseded. Commands themselves remain supervised, so weak diagnostic-program contents still require review. No automatic corpus admission follows. Added a regression test injecting false teacher success claims around a native timeout; all32targeted amendment/history/admission tests pass. Audit6files/19,357bytes R2 published and independently restored with per-file hashes verified. Evidence:evidence/data/gumtree163-projection-audit-001. No Runpod use.


## 2026-10-12: GumTree163 independent offline publisher-test controls

Frozen replay/history identities checked before and after evaluator extraction from SHA-verified task shard; temporary428,839,266byte shard released. Publisher solution/test fields remain evaluator-only. Three disposable offline Linux containers evaluated base, reference and native-submitted candidate with direct Maven status. Base fails compilation at the publisher-added getChildren test, producing no runtime case results. Reference and candidate each have141unique XML case identities,140passed and1skipped, with identical outcomes. New testGettingChildrenOfCtVirtualElement passes. All three containers removed. These are finite patch controls, not a learned-model benchmark or replacement for the native timeout.

Publisher FAIL_TO_PASS metadata contains class-level strings and an unnamed-test sentinel, with no PASS_TO_PASS entries. Exact case-level publisher-label reconciliation remains unresolved; no fabricated base per-test failures. Supervised diagnostic-program quality review and corpus admission remain pending. Any further edits now occur after evaluator exposure and must be attributed accordingly. Corpus054 unchanged; training approval false.

Grading archive41files/194,050bytes R2 published and independently restored; all per-file hashes match. Evidence:evidence/data/gumtree163-grade-evidence-001. No Runpod use.


## 2026-10-12: strict Surefire parser qualification002

Added zenithsync/junit_controls.py and tests/test_junit_controls.py. Bounded UTF-8 single-suite XML parser verifies explicit test/failure/error/skip counts, unique classname/name pairs across reports, and normal Maven completion status. It rejects DTD/entities, unsupported encodings/roots, retries, ambiguous outcomes, hidden nested cases, unsupported testcase status attributes, abnormal exits, absent reports and duplicate identities. Explicit three-run comparison requires an exhaustive disjoint case partition and retains skips; compilation-only failures cannot be invented as per-case outcomes.

All43targeted parser/history/amendment/admission tests pass. Actual GumTree reference and candidate XML each parse to141unique cases across4suites and match the independent earlier case audit exactly. Parser does not establish report authenticity or semantic test quality. Production mini admission intentionally still rejects unsupported Java evaluator kind: JVM grader provenance, compilation-phase evidence and that integration remain outstanding. Diagnostic amendments deferred until this grading foundation is integrated. No corpus change, training approval or Runpod use.

Current qualification002 archive16files/131,177bytes and earlier001 archive16files/130,979bytes both R2 published and independently restored; every file hash checked. Current source/test files match002 archived bytes. Evidence:evidence/data/surefire-parser-qualification-002.


## 2026-10-12: Maven compilation-phase controls

Added zenithsync/maven_compile_controls.py and focused tests. An explicit bounded log profile verifies normal Maven testCompile exit1, absent XML reports, exact missing-symbol diagnostic records/counts, consistent repeated diagnostics, and absence of conflicting errors or test execution. Returned base runtime_case_outcomes is null, never fabricated case failures. Separate comparison requires exhaustive disjoint pass/skip case pairs and matching complete reference/candidate Surefire results. It reports compile-to-test phase change, explicitly not runtime fail-to-pass transitions.

All49targeted compiler/Surefire/replay/amendment tests pass. Applied to GumTree frozen real controls: exact missing getChildren diagnostic at publisher test line206,column57; reference/candidate141cases,140pass/1skip. Profile is explicitly assistant-reviewed after evaluator exposure, not claimed original publisher case labels. Log consistency is not execution authenticity. Production admission integration still requires a fresh JVM grading receipt with exact replay/patch/profile bindings, report inventory, tracked-source before/after checks, and cleanup evidence. Existing one-off grader controls do not yet contain that complete receipt; unsupported Java admission remains rejected. No corpus change or training approval.

Qualification23files/173,239bytes published to R2 quarantine and independently restored with every file hash compared. Evidence:evidence/data/maven-compile-controls-qualification-001. No Runpod use.


## 2026-10-12: fresh Maven grading receipts with source provenance

Added scripts/run_maven_grade_probe.py and scripts/qualify_maven_compile_replay.py. Fresh grade002 ran base/reference/candidate in separate offline image004 containers. Probe verifies pristine exact snapshot and absent build/report state, binds applied repair/test bytes, inventories243source entries and full diffs before/after Maven, and captures every XML/text report with hashes. Host verifies normal probe completion, no OOM, copied artifacts, exact report inventories, identical source states, and successful cleanup for all three containers. Input bindings include frozen replay receipt/patch, snapshot verification, evaluator task, explicit profile, and implementation sources.

Recomputed comparison: base normal testCompile failure with no XML reports; reference/candidate4XML suites each,141cases with140pass/1skip and exact outcome agreement. Compilation-phase success is not a runtime per-case fail-to-pass claim. Independent audit rechecked every input/artifact hash, all243source records per role and the comparison. New grading receipt is ready for admission-validator integration; production mini admission still does not recognize Java until that adapter and mutation checks are implemented. Supervised diagnostic quality review, publisher-label interpretation, rights/split gates and training approval remain outstanding.

Evidence65files/507,065bytes R2 quarantine published and independently restored, all files hash-compared. Evidence:evidence/data/gumtree163-bound-grade-evidence-001. No corpus change, model execution or Runpod use.


## 2026-10-12: Maven admission reconstruction and mutation checks

Production mini-replay admission now recognizes the source-bound Maven compilation-control receipt and requires an explicit grading profile. The adapter reconstructs patch identities, exact role inventories, source records and before/after diffs, report inventories, container completion/cleanup and the raw compilation/test comparison. Tracked-source records require canonical paths, regular Git modes, SHA-256 digests and nonnegative integer sizes; booleans are rejected as sizes. Synthetic mutation tests cover altered repair bytes, source changes, missing reports, OOM, changed profile/comparison, undeclared artifacts and cross-role paths. Fixed the fixture root to resolve macOS /var aliases so rejection tests exercise their intended condition.

All72focused compiler/Surefire/bundle/admission/history/amendment tests pass. The real GumTree002 receipt passes evidence reconstruction but remains mechanically blocked solely by maven_publisher_case_label_review_required. Its18,751input/6,832supervised tokens remain outside the corpus. Compilation failure produces no fabricated runtime case failures. This is finite consistency validation, not general correctness or execution attestation; diagnostic quality, task/rights/split review and training gates remain.

Evidence11files/82,272bytes published to R2 quarantine and independently restored, with every original/restored SHA-256 checked. Compact evidence:evidence/data/maven-admission-qualification-001. Corpus054 unchanged; training approval false; no Runpod use.


## 2026-10-12: full local CPU regression qualification

Ran the complete unittest discovery suite with ZENITHSYNC_TEST_TORCH=1. Initial556-test run exposed5errors caused by absent PEFT in the recovered Mac runtime; retained the failed log. Installed repository-pinned peft0.21.2 with --require-hashes --no-deps; pip check then reports no broken requirements. Repeated complete suite with Hugging Face/Transformers offline mode:556tests, all passed, no skips,22.130seconds. This includes reduced real Gemma token-weighted loss/gradient/update equivalence, adapter attachment and checkpoint restoration, optimizer/data cursor contracts, and the new Maven evidence checks. No downloaded full model, GPU execution or training approval.

Bound311source/lock files before execution and verified unchanged afterward. Archived source bytes in a compressed bundle and checked every member against source identities. Six-file596,014byte evidence archive published to R2 quarantine and independently restored; all file hashes and restored source archive members verified. Evidence:evidence/p1/full-suite-qualification-001. These are finite CPU regressions, not full-size quantized model/GPU kernel/performance qualification. Corpus054 and outstanding admission/rights/split/context-budget gates unchanged. No Runpod use.


## 2026-10-12: additional raw dataset storage release

Removed13resident raw SWE-Hero parquet copies only after checking their local SHA-256, exact remote manifest bytes, and a fresh full streaming SHA-256/length of each R2 blob. Durable per-file verification precedes unlink; independent audit confirms all13paths absent with matching verification events. Released2,250,248,192allocated bytes (approximately2.10GiB); filesystem available space rose from approximately24GiB to26GiB. Physical storage changes can differ due to shared blocks/snapshots.

The first cleanup runner terminated on shard000's differently named publish-receipt path after3other shard deletions had completed safely. A separate bounded runner handled004–013; shard000 remains untouched. No unmatched data, selected trajectories, active runtime, metadata or source manifests removed. No claim that iCloud errors are globally resolved. Restore instructions and per-shard manifests:evidence/data/swe-hero-release-audit-001. Audit20files/30,847bytes R2 published and independently restored, with all file hashes compared. No Runpod use; P1 remains incomplete.


## 2026-10-12: corpus exposure capacity audit and scaling priority

Revalidated corpus054 through the hash-bound inspection loader:38examples,213,020supervised tokens, still quarantined with zero training-admitted tokens. Enumerated a hypothetical50M-token schedule with seed7401 and9216maximum supervised tokens/update:7,884updates,50,004,719consumed tokens,4,719whole-example overshoot,234–235exposures per example. Independently reconciled per-example exposure counts to consumed tokens. This diagnostic schedule is not a training authorization and must not be deployed as a substitute for corpus growth.

Exact corpus-size lower bounds for a50M-token candidate under1/2/3/5maximum passes are50M/25M/16,666,667/10M supervised positions respectively. The3-pass scenario therefore requires16,453,647additional positions beyond the current quarantine corpus, plus admission of all counted data. These are sensitivity scenarios, not approved epoch policies. Three candidates can reuse an admitted corpus:150M cumulative exposure does not mean150M distinct data. Inverse token concentration is reported per example/task/repository as descriptive balance only, never statistical effective sample size or independence.

Next scaling work must prioritize batch qualification and rights/split coverage of acquired source pools, measuring yield in admitted tasks and supervised tokens; additional isolated replay examples alone cannot establish50M-scale readiness. Retain task fidelity, evaluator isolation, duplication controls and exact masks while expanding. No weakening of gates or speculative token counts. The first audit script hit a metadata-field mismatch before emitting a report;002 explicitly joins repository groups from the verified corpus manifest. Four-file41,807byte audit published to R2 and independently restored with all hashes matched. Evidence:evidence/data/corpus054-capacity-audit-002. No Runpod use or training approval.


## 2026-10-12: SWE-Hero batch qualification queue

Verified the full34,269-row census index against its stored manifest identity and current reserved-repository index. Deterministic seed7401 hash ranking chooses one task and one trajectory per repository across128repositories from1,668eligible repository names, excluding corpus054 repositories and exact reserved matches. Reversing input order reproduces identical selection. All source shard identities match their intake receipts; each queue entry carries the R2 blob key, exact size/hash and row locator.127entries originate from SWE-rebench and1from R2E-Gym. Publisher license labels comprise70MIT,27Apache-2.0,21BSD-3-Clause and10BSD-2-Clause; none is treated as rights clearance.

This is a development coverage queue, not an unbiased benchmark or an admitted corpus. Body inspection, independent task alignment, source rights, fork/semantic isolation, native reconstruction, exact token masks/context, runtime patch controls and privacy review remain pending. No token yield is inferred from metadata. Next step: bounded one-shard-at-a-time extraction of selected source trajectories from R2, hash verification before parsing, evaluator repair/test fields excluded, temporary shards released after extraction. Two-file73,696byte queue/runner bundle published to R2 and independently restored with both hashes checked. Evidence:evidence/data/swe-hero-batch-qualification-001. Corpus054 unchanged; no Runpod use.


## 2026-10-12: batch source extraction and structural preflight

Extracted all128selected SWE-Hero histories from9R2 shards using bounded one-shard-at-a-time temporary storage. Verified each complete shard SHA-256/length before parsing and rechecked after parsing; all selected row identities match the census queue and every temporary directory was removed. Only repo/instance/trajectory identity, license, dataset and trajectory columns read; model_patch excluded. This column exclusion does not prove that source history text is free of answer conditioning.

All128pass existing source serialization conversion and single-pending-call linkage checks; all terminal finish calls remain unanswered source calls, not execution evidence. Four-family recursive credential screen flags0records; this is not a privacy guarantee. Native tool semantics, independent task alignment, source rights, fork/split isolation, token masks/context and runtime controls remain unqualified. No corpus admission or supervised-token expansion claimed.

132extracted files total29,465,082bytes. Compressed four-file archive4,633,092bytes published to R2 and independently restored. All outer file hashes and132inner archive member identities verified. Redundant compressed archive copies released afterward; selected working records retained outside iCloud. Compact receipts:evidence/data/swe-hero-batch-extraction-archive-001. Corpus054 unchanged; no Runpod use.


## 2026-10-12: batch source context census

All128source histories measured without truncation using hash-pinned Gemma tokenizer/template assets, Transformers5.13.1/tokenizers0.22.2 and the existing source pre-action text projection. Total6,642,586input tokens, median49,724, range27,150–114,032. Only6histories fit32,768;106fit65,536; all128fit131,072. None fits32,768with an8,192full-history reserve. These are source-format input counts, not supervised targets, native per-action serving requests or GPU capacity tests. Tool schemas are not included.

Second measurement reproduces all full-history counts and hashes while measuring initial prefixes separately: median2,911,max6,056tokens. Even full-minus-prefix rendered differences exceed32,768for116histories and24,576for127. Differences are descriptive and cannot be substituted for native context counts. Thus prompt boilerplate alone does not explain the length bottleneck. No truncation, compression, model context extension or training approval adopted. Next requires native-context feasibility work and broader short-trajectory selection, retaining task fidelity; longer-context training would require separately measured GPU cost/quality and serving compatibility.

Three-file80,886byte report/runner/prefix audit published to R2 and independently restored, all hashes verified. Evidence:evidence/data/swe-hero-batch-context-002. Corpus054 unchanged; no Runpod use.


## 2026-10-12: source editor preflight and batch adapter feasibility

Tightened source replay preflight to reject missing editor fields, nontext mutation payloads, empty replacement search strings, invalid/bool/reversed line ranges before container creation. Empty file creation and deletion via empty replacement remain supported byte-for-byte. All24focused editor/profile/search/subdirectory tests pass. This changes the adapter source identity; historical receipts must retain their original implementation binding.

Static action audit of128histories finds a single repository-matching source-root candidate for every history; these inferred roots are not approved runtime profiles.88histories have all individual actions accepted by the current grammar. Across the remainder:121unreviewed shell calls,41additional root substitutions,17timeout mismatches,17outside-root paths,4unsafe paths,1directory edit and1missing mutation argument. Counts are calls, not histories, and may overlap per history. No commands executed. This identifies concrete adapter work without relaxing path or timeout rules; supported grammar does not prove runtime semantics, context fit, task correctness or admission.

Five-file93,607byte implementation/test/audit bundle published to R2 and independently restored with all hashes checked. Evidence:evidence/data/swe-hero-batch-adapter-001. Corpus054 unchanged; no Runpod use.


## 2026-10-12: bounded nested pytest path compatibility

Extended only the standalone root-relative pytest grammar to nested Python files and canonical test directories, preserving optional-v. No traversal, wildcard, expansion, shell chaining or implicit persistent-directory support added. Real-shell fixture checks exact argv/cwd/stdout/stderr and nonzero status preservation; macOS temporary-root aliases resolved explicitly. All27focused adapter tests pass.

Re-auditing128histories reduces unreviewed shell calls121to116; all-action-compatible history count remains88because affected histories retain other blockers. No inflated trajectory yield claimed.23rejected C-c controls reveal persistent shell semantics that cannot simply be mapped to independent run_command calls; they remain rejected. Native replay, task qualification and context constraints remain unresolved. Six-file96,117byte implementation/test/audit archive R2 published and independently restored with all hashes verified. Evidence:evidence/data/swe-hero-batch-adapter-002. No Runpod use or corpus admission.


## 2026-10-12: independent issue-text reconciliation for batch

Hash-verified both pinned SWE-rebench task shards before and after reading only repo,instance_id,base_commit,problem_statement. All127selected SWE-rebench entries join uniquely:99source issue-description blocks equal independent text exactly;28equal after NFKC/whitespace normalization. One R2E trajectory(tornadoweb/tornado,e704489dd1a897ca66c8a7becb963556929cfef6) requires a separate independent task-text join. Publisher repair/test columns unread. Selected independent problem statements retained with base identities and source hashes for semantic review.

Text identity is not proof of semantic solution alignment, absence of extra teacher instructions outside the issue block, rights clearance or evaluator isolation beyond the recorded column boundary. All trajectories remain unapproved; corpus054 unchanged. Two-file278,634byte task-text report/runner bundle R2 published and independently restored with both hashes checked. Evidence:evidence/data/swe-hero-batch-task-alignment-001. No Runpod use.


## 2026-10-12: complete independent text join and batch review ledger

Verified all8pinned R2E shards and read only repo_name,commit_hash,problem_statement. The remaining selected Tornado trajectory joins uniquely by repository basename and commit; owner identity and unresolved base-parent ref remain separate gates. Independent issue text781characters versus teacher1,592characters: both concern TCPClient.connect source_ip/source_port, but teacher paraphrases and adds invalid-bind/socket-error expectations. Marked semantic review pending, not silently normalized or declared unrelated. Final batch text statuses:99exact,28normalized,1different. No evaluator solution/test fields read in this check.

Unified all128queue/task/context/adapter identities and explicit remaining gates in a review ledger. Five histories intersect32,768source-token fit and all-action static grammar support; none passes the full-history8,192reserve proxy, and none is training-admitted. These are development feasibility metrics, not model performance or native context qualification. Four-file74,571byte ledger/task/scope/runner evidence published to R2 and independently restored with all hashes verified. Evidence:evidence/data/swe-hero-batch-review-ledger-001. No Runpod use; corpus054 unchanged.


## 2026-10-12: CRC153 pinned source and digest invariants

Selected Nicoretti/crc153 from the five source-context/static-action feasible histories. Verified56upstream blobs(209,852bytes) against exact base8d928145df5caf588d9ff5af83bd72feb241fd1e and its Git tree. Reconstructed the sole production-file replacement from the selected teacher trajectory; no publisher repair read. Source teacher diagnostics still require review: final_verification.py prints a fixed138and performs an additional update, so it is not an exact reproduction despite its label. Such output must not become accepted runtime evidence.

Executed finite digest controls on real source modules:16exported configurations, both Register/TableBasedRegister, all256states for8-bit configurations and boundary/single-bit states for larger widths. Independent binary-string reversal oracle plus repeated digest/state-preservation checks:3,656cases per variant; base1,120failures,source candidate0failures,constant-output mutant3,624failures. This is not exhaustive larger-width coverage, continuation-after-digest testing, native replay, publisher grading or training admission. No learned-model claim.

Three-file99,100byte archive published to R2 and independently restored; all outer hashes and68inner member hashes checked. Evidence:evidence/data/crc153-controls-archive-001. Native environment/replay remains next; corpus054 unchanged; no Runpod use.


## 2026-10-12: CRC153 offline upstream regression controls

Ran base and source-derived candidate in fresh Linux/amd64 containers using pinned local base image14d857d591be7d1a7efc83ff1dcc87f83c96c764895b0986a45db0d8af5a8a46, Python3.13/pytest9.1.1, network disabled,1GiB memory,2CPU,cap-dropALL. Read-only source mounts and PYTHONPATH=/testbed/src avoid packaging mutation. Both upstream suites pass47unique cases,0skips, with identical case identities. Complete source inventories are unchanged; normal exits and both container removals verified. This confirms finite regression compatibility under this runtime, not source-native replay or publisher fail-to-pass grading. Base passing proves the upstream tests do not detect the digest-state defect; separate state-invariant controls remain necessary.

Native replay packaging remains unresolved: teacher invokes pip install-e., requiring an offline build backend and pristine source snapshot preparation. No need for Runpod at this stage. Three-file179,065byte control archive published to R2 and independently restored; all outer and inner member hashes verified. Evidence:evidence/data/crc153-upstream-archive-001. Corpus054 unchanged; training approval false.


## 2026-10-12: CRC153 pristine offline replay image

Prepared parentless snapshotf5264923d61414244fbe2563f5444bc3a6708931 with exact upstream treef24f4966cb9dd7d491032140a8a994512e8583c9, one reachable commit and no remotes. Downloaded poetry-core2.2.1 wheel, checked hash/size against PyPI release metadata, installed via hash-pinned offline lock. Docker build used networknone and the previously inspected local base tag. Image:c0a084e62b93109dc253bc8dd421f33175880daa232ff0204d0a2daedd3879a8.

Fresh offline probe verifies snapshot identities, editable pip install, base digest sequence81/138/81,47upstream passing cases and unchanged tracked source. Only the explicit bootstrap install.sh remains untracked for the existing workspace-preparation cleanup contract. Initial probe001 incorrectly imported the newly editable-installed package within an already-running interpreter;002 uses a fresh interpreter, consistent with source shell calls. Both probe containers removed. Native trajectory replay still pending; no model execution or training approval.

Sixteen-file518,031byte build-input/probe evidence R2 published and independently restored with all file hashes verified. Evidence:evidence/data/crc153-image-verification-002. Built Docker image itself remains local and is not exported to R2; byte-identical image recovery is not claimed. No Runpod use; corpus054 unchanged.


## 2026-10-12: CRC153 native replay and token qualification

Restored and full-hash-verified one temporary SWE-Hero shard, ran unchanged source actions through pinned native tools in the offline CRC image, then verified container removal and temporary shard release. Replay completed with36charged tool calls and37captured exchanges(including submission). Submitted patch4,415bytes SHA2562ff4673af41064f38344e2c704997e6551a4329378b5731571b5b0dceac3d186. Fresh failures at source16(import collection before install),42(base digest reproducer)and58(diagnostic enum attribute error)retained; no source observations reused.

Reconstructed76-message action-only history using independent issue and native schema. Exact pinned-tokenizer audit:21,266input/3,839shifted supervised tokens,untruncated; plus8,192reserve=29,458within32,768. This demonstrates source-format length is not native-context length. History remains quarantined: submitted final_verification.py hardcodes printed138 and updates payload twice despite exact-reproduction label, requiring attributed correction and fresh replay; publisher grading, semantic review and rights/split gates remain. No model performance or training approval claimed.

Seventeen-file445,013byte replay/history/token evidence R2 published and independently restored with every file hash matched. Evidence:evidence/data/crc153-native-evidence-001. No Runpod use; corpus054 unchanged.


## 2026-10-12: CRC153 attributed diagnostic correction and fresh replay

Amended only source70created final_verification.py and source76final shell diagnostic through hash-bound assistant amendment plan. Removed fabricated printed138 and duplicate update; new diagnostic computes independent binary-reversal oracle, checks repeated reads preserve state, and verifies continuation against untouched control. Final shell now asserts values/state instead of only printing consistency. Diagnostic passes candidate and fails base/constant-output mutant with nonzero exits. Original production repair, paths and action order preserved. No publisher repair inspected.

Fresh native002replay completed; amendment binding verified during history reconstruction. Source errors remain captured, container removed, temporary shard deleted. Submitted patch applied independently to a fresh source copy: production bytes equal the previously tested candidate and final diagnostic bytes equal the amendment.76messages/37exchanges encode21,058input and3,727shifted supervised tokens without truncation; plus8,192reserve=29,250. Publisher grading, remaining diagnostic semantic review and rights/split admission pending. Corpus054 unchanged; no model or Runpod use.

Twenty-seven-file474,199byte amendment/control/replay/history/token evidence R2 published and independently restored with every file hash compared. Evidence:evidence/data/crc153-native-evidence-002.


## 2026-10-12: CRC153 publisher regression qualification

Frozen native002 replay, patch, history and token identities before extracting publisher-only evaluator inputs; all frozen identities rechecked unchanged after grading. Fresh isolated offline base/reference/candidate containers use the same content-pinned CRC replay image. Strict full-node-ID comparison covers all17publisher cases: base11pass/6fail, reference17pass, candidate17pass. All six fail-to-pass and eleven pass-to-pass expectations match exactly; no case disagreements. Tracked changes remain unchanged by tests; no OOM and all three containers removed. Candidate receives its submitted patch and publisher tests, not the reference patch.

This standalone qualification uses Python3.13 rather than publisher install metadata Python3.9. Existing production profile requires /opt interpreter paths, while this image uses /usr/local/bin/python; no validator bypass or false production-admission receipt adopted. Production grading/admission integration, remaining diagnostic review and rights/split gates remain unresolved. No training admission, model performance claim or Runpod use. Publisher input exposure is now recorded; subsequent changes must preserve that attribution.

Forty-file93,555byte evidence bundle published to R2 and independently restored with every file hash matched. Compact receipts/report/manifest:evidence/data/crc153-publisher-evidence-001. Corpus054 remains unchanged.


## 2026-10-12: refreshed complete local regression suite

After editor/nested-pytest adapter changes, full unittest discovery passes562tests,0skips,in22.283seconds with explicit Torch tests enabled and model hubs offline. Source identities checked before/after execution. Includes existing reduced-model numerical/gradient/optimizer/checkpoint tests; this does not qualify full-size quantized Gemma, GPU kernels, serving capacity, training data admission or model performance. No Runpod use.

Four-file586,790byte compressed evidence bundle published to R2, independently restored, and all316inner member hashes checked. Receipts/report/log/manifest:evidence/p1/full-suite-qualification-002. P1 remains incomplete; corpus054 remains quarantined and training unapproved.


## 2026-10-12: production grading interpreter integration and CRC153

Production profile now permits canonical /usr/local/bin/python,python3,python3.N alongside reviewed /opt paths, rejecting traversal, doubled separators, control characters and alternate executable names under /usr/local/bin. Both control and candidate probes use the explicitly bound interpreter as container entrypoint rather than assuming /usr/bin/python3. Image and source-origin bindings remain required. Added path/activation rejection coverage and control-entrypoint assertion.

Fresh independent snapshot verification matches every tracked file to separately fetched upstream base bytes, confirms exact tree/parentless single commit/no remotes/no tracked modifications and inaccessible original base commit. Inherited Docker layer contents are not audited. Production controls and grade commands now succeed on unchanged native002 patch:17cases,6expected base failures,reference/candidate17pass,zero disagreements,cleanup verified. Initial integration attempt used an absolute import_root and was rejected before controls; corrected002 uses canonical relative src. Python3.13 versus publisher3.9 remains a documented runtime difference. All subsequent candidate edits would be post-evaluator exposure.

Production evidence53files127,946bytes published to R2 and independently restored/hash-compared. Evidence:evidence/data/crc153-production-evidence-001. Full updated local regression:564tests,0skips,22.197seconds; source identities unchanged during run; explicit reduced Torch checks enabled, model hubs offline. Four-file587,546byte suite archive R2 published/restored,all316inner member hashes verified. Evidence:evidence/p1/full-suite-qualification-003.

Remaining: semantic/diagnostic review, source rights/split and corpus admission; no training admission or full-size GPU/model qualification. Corpus054 unchanged. P1 incomplete; Runpod unused.


## 2026-10-12: CRC153 diagnostic semantics and amended replay004

Existing replay002 passes the production mechanical admission assessment, but manual diagnostic inspection identifies inaccurate explanatory text: MODBUS reverse_output is true, IBM_3740 false despite an all-reversing list description; the reproducer calls a first-observation consistency comparator an expected-value test. Four total source amendments now bind earlier70/76corrections plus40/56wording corrections. Production repair and action order unchanged. New amendments explicitly post-publisher-evaluator exposure; no attempt to present this as an untouched teacher trajectory.

Initial amendment preparation rejected unsorted indices. A prematurely launched003wrapper then failed on missing plan before native execution; its logs retained and temporary shard removed. Sorted unique plan validated, fresh004wrapper/replay completed and cleaned up. Original fresh errors at16(before editable installation),42(base reproducer)and58(enum attribute)remain visible. History76messages/37exchanges,21,053input/3,731shifted supervised tokens,29,245with8,192reserve. Production candidate grade matches all17publisher cases; mechanical assessment passes with no blockers and training_approved false. No corpus admission yet; full source/semantic review, rights/attribution, frozen split/duplicate review and training runtime gates remain.

Forty-file572,564byte replay/history/token/grade/admission/amendment evidence published to R2 and independently restored, every file hash checked. Evidence:evidence/data/crc153-native-evidence-004. Corpus054 unchanged. No Runpod use, no learned-model performance claim. P1 incomplete.


## 2026-10-12: corpus055 quarantine integration and restoration

CRC native004 reviewed for action/diagnostic scope and fresh-observation linkage with76per-message identity records; original teacher prose absent. Repository LICENSE.txt retained with attribution. Review002 supersedes erroneous review001 explanation about why comprehensive_test.py is absent from the submitted patch: upstream .gitignore does not support that explanation, so no such cause is claimed. Dataset/issue rights remain open. Explicitly post-evaluator-exposure derivative.

Assembled corpus055 with39examples/39tasks/38repositories,760,106input and216,751shifted supervised tokens. All38predecessor records unchanged; counts independently recomputed from arrays and matched loader totals. Manifest SHA256d1de99344a91238b777a8ab1c79452046d8fd34a9ee7e69206ff107171aae74f; content SHA25651a3a2a7a8a8981e719e8bbcf07dcf5cfb0f9b2d999d6df416290b4b146e5341. All admission fields null; actual training-purpose load rejected. This adds3,731quarantined targets,not training-admitted data.

All79corpus files8,415,451bytes published to R2,independently restored,hash-compared and loaded successfully. Redundant restoration copy then removed after another per-file comparison; authoritative local corpus retained. Integration evidence11files73,059bytes independently published/restored. Evidence:evidence/data/corpus055-integration.

All741within-corpus issue pairs cross-checked against independent set intersections/rational similarity. Only inherited PennyLane5716/5831containment flag remains; no new flagged pair at existing thresholds. Lexical screen is not proof of semantic independence. All39decoded examples screened,zero credential indicators; privacy approval false. Five-file157,482byte check bundle independently R2published/restored. Evidence:evidence/data/corpus055-checks. Frozen split extension, context/runtime holds including inherited emcee serving overflow, rights and full-scale data sufficiency remain open. No Runpod use; P1 incomplete and zero training-admitted tokens.


## 2026-10-12: corpus055 provisional split/context and next batch environments

Fresh GitHub Nicoretti/crc metadata extends the hash-checked prior lineage:39provisional assignments,38unchanged,no known reserved repository-name or GitHub-network overlap. Draft remains unfrozen; detached copies/semantic contamination/pretraining overlap unexcluded. Exact token/label interval audit finds no teacher-forced sequence overflow; inherited dfm__emcee-295 remains the sole full-history and supervised-span8,192reserve exception. This does not resolve its previously measured native serving failure.

Selected eight remaining statically supported, independent-text-matched tasks from the128batch, ranking source transport token length then trace hash. All eight Docker Hub Linux/amd64 image manifests/configs resolve to immutable digests:python-frontmatter31,pandera64,csv2md22,djangorestframework-api-key187,files-to-prompt36,pytypes37,marshmallow-dataframe19,structlog350. Source lengths are screening priorities,not native context bounds. Compressed layers per image1.23–1.54GB; no image layers downloaded. No runtime/source-snapshot/oracle isolation or evaluator qualification claimed.

Forty-one-file332,899byte split/context/registry evidence published to R2 and independently restored with all hashes matched. Evidence:evidence/data/corpus055-batch-readiness. Next batch work must inspect or reconstruct bounded source environments, then replay and grade each with explicit admission gates. No Runpod use; P1 incomplete;216,751quarantined targets and zero training-admitted tokens.


## 2026-10-12: eight pinned source snapshots and offline baseline screen

Fetched all eight selected exact base commits through bounded GitHub commit/tree metadata and codeload archives. Every materialized regular file matches Git blob SHA1/size and mode; complete path inventories match untruncated tree responses. Trees with links/submodules would be rejected. Verified source bytes per candidate:frontmatter48,027;pandera102,820;csv2md17,487;django-api-key88,474;files-to-prompt34,338;pytypes1,029,921;marshmallow-dataframe39,737;structlog772,656. No benchmark solution/test columns read during this acquisition.

Fresh sequential offline containers use pinned existing base14d857d591be7d1a7efc83ff1dcc87f83c96c764895b0986a45db0d8af5a8a46 with1GiB/2CPU/read-only source/PYTHONPATH/source byte checks/60second cap. All eight removed and source inventories unchanged. csv2md10upstream tests pass. frontmatter default pytest discovery finds no tests; requires explicit target. Pandera lacks numpy; Django key lacks dj_database_url; files-to-prompt lacks click; pytypes hits imp.PY_SOURCE runtime incompatibility; marshmallow-dataframe lacks pandas; structlog lacks test packages and asyncio marker. These are environment screens,not publisher-equivalent grading or evidence that the tasks fail in their intended runtime. No skips or exit5 counted as passes.

Four-file1,195,177byte compressed source/runtime evidence published to R2 and independently restored; all356inner member hashes verified. Evidence:evidence/data/next-batch-source-runtime-evidence-001. Sources remain outside iCloud; no large image layers downloaded. Next: offline dependency locks/runtime selection, starting with csv2md's runnable baseline while preparing lightweight click/PyYAML environments. No Runpod use, corpus055 unchanged, P1 incomplete.


## 2026-10-12: files-to-prompt36 offline dependency and baseline qualification

Pinned Click8.1.8 universal wheel using official PyPI release metadata, verified98,188bytes and SHA25663c132bbbed01578a06712a2d1f497bb62d9c1c0d329b7903a866228027263b2. Retained origin JSON and hash-required offline requirements lock. Linux Python3.13 requires neither conditional Windows colorama nor Python<3.8 importlib-metadata; no transitive downloads used. Reference:https://pypi.org/pypi/click/8.1.8/json.

Fresh bounded offline container installed wheel with--no-index/--no-deps/--require-hashes into temporary dependency directory. Explicit import-origin probe confirms Click under/tmp/dependencies and files_to_prompt under read-only/testbed. Strict full-node-ID setup/call/teardown parser records12upstream cases,allpassed. Source inventory unchanged,noOOM,containerremoved. This qualifies one local baseline with Python3.13/pytest9.1.1,not publisher environment equivalence, candidate repair, native trajectory or training admission.

Fourteen-file120,428byte wheel/lock/probe/results/source identities bundle R2published and independently restored,allhashesverified. Evidence:evidence/data/filesprompt36-baseline-evidence-001. No large image layers or Runpod used. Corpus055 unchanged; P1 incomplete. Next requires parentless exact source snapshot and native replay; source/evaluator separation remains mandatory.


## 2026-10-12: files-to-prompt36 exact snapshot and native replay

Built offline image0be4dbfb3020be65b18bf13f1bbaff5235359f4ea7821208735424ec536d1b9e from inspected existing base with hash-pinned Click wheel. Parentless snapshot preserves exact upstream Git tree atf9a4d8fa20aa978c3502c94de335b44e57ac0a61. Independent container verifies all tracked bytes against fetched source,one parentless commit,no remotes,no tracked modifications,and original base inaccessible. Image itself not exported to R2; build inputs retained.

Unamended native source replay completes35chargedcalls/36exchanges,containerremoved,temporaryR2shardremoved. Submitted439byte patch SHA256448d04627cd7c4d0bf256b4007a4b197f2d3601ea56eb3281fc7312600296cf2 changes output open to explicit UTF-8. Independent issue/native schema projection produces74messages,21,141input/5,962shifted supervised tokens untruncated; plus8,192reserve=29,333. Source-format33,317token count was not a native-context blocker.

Quarantine hold: source diagnostic labels Windows reproduction but does not force a legacy default encoding; direct open-copy test is not a regression oracle for patched CLI and Boolean failures do not consistently set nonzero process exit. Linux success must not be promoted to Windows regression evidence. Next requires an explicit legacy-codepage negative control through actual CLI,Unicode output oracle,base/reference/candidate publisher grading and attributed diagnostic correction if admitted. No publisher fields inspected during this replay stage,no model improvement claim.

Thirty-three-file600,554byte build-input/snapshot/replay/history/token evidence R2published and independently restored,allfilehashesmatched. Evidence:evidence/data/filesprompt36-native-evidence-001. Corpus055 unchanged; Runpod unused; P1 incomplete.


## 2026-10-12: files-to-prompt36 encoding controls and publisher-scope mismatch

Controlled actual CLI output-file defaults across UTF-8,cp1252,ASCII;fivepayloadclasses(ASCII,accent,emoji,CJK,combining)andplain/XMLformat=30casesperrole. Stdout CLI output provides expected UTF-8bytes,output file is compared byte-for-byte. Base14pass/16fail;submittedUTF-8candidate30pass;explicitASCII mutant6pass/24fail. This is a Linux codepage simulation,not nativeWindows execution. Initial probe001 lacked explicit/testbed import path;002 fixes harness path,originalfailure retained. All containersremoved;noOOM.

Frozen candidate/replay/history/tokens before publisher extraction. Publisher reference includes both UTF-8 fix and additional line-number feature;sole fail-to-pass is test_line_numbers,not the provided encoding issue. Freshproductionbase12/13,reference13/13,candidate12/13withline-number disagreement. Mechanicaladmission correctly blocks publisher_expectations_not_matched. Do not add unrelatedfeature or silently substitute tests to force acceptance. Excluded from publisher-qualified corpus; independentencoding evidence retained separately. Disposition002 explicitly clarifies referenceincludesUTF-8aswellasline-number additions;001retained.

Evaluationbundle58files108,987bytes R2published/restored/hashverified;clarifieddisposition1007bytes separatelyR2published/restored. Evidence:evidence/data/filesprompt36-evaluation-evidence-001 and evidence/data/filesprompt36-disposition-evidence-002. Corpus055unchanged;noRunpod;P1incomplete. This case demonstrates that exact issue-text joins and green upstreamtests do not establish evaluator semantic alignment.


## 2026-10-12: csv2md22 native replay and detected parsing regression

Built offline image150757138b7572f27caa76c9db32a7035843c472e821f18efeb52614f8aef788 using existing pinned local base,without extra package downloads. Exact source-tree verification at2dd166be84bcbd86da199cb4186ab908ad9ab9c1 confirms parentless snapshot,tracked bytes,no remotes,original commit inaccessible. Native unamended replay completes38chargedcalls/39exchanges;container and temporarysource shardremoved. Failures including legacy nose calls remain in observations. Submitted945byte patch SHA25654abca1ad705db50029fd5d2f7b7eab46ca90ac6628e8377044ed3c7c2fe47ce.

Independent task/schema history80messages,21,251input/5,160shiftedtargets,untruncated;29,443withoutputreserve. Frozen candidate artifacts before publisher extraction and rechecked unchanged afterward. Publisher controls align with pipe-escaping issue:base6/9pass,reference9/9pass,candidate5/9pass. Candidate fixes three rendering cases but regresses four parse_csv cases by escaping raw cells during construction. Mechanicaladmission blocks publisher_expectations_not_matched; no corpus addition. This is a real candidate regression,unlike files-to-prompt's extra-feature test mismatch.

Correction invariant for future explicitly post-evaluator derivative: parsing preserves raw cell values; rendering computes escaped strings and display widths without mutating stored cells. Need fresh negative controls,repeat-render/state checks,complete publisher regression and attributed replay before reconsidering admission. Historical passing upstream tests without pipes did not detect the defect.

Seventy-file554,286byte build-input/snapshot/replay/history/token/publisher/control/admission evidence R2published and independently restored,allhashesverified. Evidence:evidence/data/csv22-native-evidence-001. Built image itself remains local,not exported. Corpus055unchanged;Runpodunused;P1incomplete.


## 2026-10-12: csv2md22 pure-render correction and attributed replay002

Assistant derivative after publisher exposure restores original constructor/raw cells/stored widths,computing escaped cells and rendered widths locally in markdown(). For finite rectangular string cells,escaping inserts one backslash per pipe,so escaped codepoint length is len(s)+count_pipe(s);column rendering width is its rowwise maximum. This is codepoint padding,not a claim about terminal grapheme widths or all Markdown implementations. Stored parsing state is not assigned by rendering.

Finite differential controls:85strings length0..3 over{a,pipe,backslash,é},threealignments,twoheadermodes=510cases perrole. CSVroundtrip/raw state/repeat-render/output oracle:base240pass270fail;originalteacherrepair240pass270fail;corrected510pass0fail. Initial harness001 incorrectly expected uppercase defaultheaders;repositoryutils useslowercase. Corrected002 preservesfailedrun and passes allcases. Publisher standalone corrected9/9; no skippedcases counted.

Explicit completionplan appends two assistant commands to unchanged sourceactionprefix:hash-checked productioncorrection,then upstreamtests+rawparse/escape/repeat/stateassertions. No publishertests injected into agenthistory. Freshnative002completes40chargedcalls/41exchanges;84messages,23,373input/7,186shiftedtargets,31,565with8,192reserve. Submitted1,596bytepatch SHA256323997766f6a3e1c96842cdf119cae0d4fc800b0f5f7262e1749d35131398378 matches plan. Freshproductionpublishergrade9/9,mechanicaladmissionpasses,trainingfalse. Container/tempR2shardremoved. Semantic/source/rights/splitreview remains before integration.

Sixty-nine-file1,048,925byte correction/control/completion/replay/history/token/grade/admission evidence R2published and independently restored,allhashesverified. Evidence:evidence/data/csv22-corrected-evidence-002. Corpus055unchanged;Runpodunused;P1incomplete. No newmodelperformance claim.


## 2026-10-12: raw-outcome admission verification and storage release

The SWE-rebench admission path now recomputes publisher base/reference transitions and candidate/reference agreement from four uniquely selected, hash-bound raw evidence files. It rejects missing or ambiguous bindings, altered outcomes, and a grading summary inconsistent with recomputation. It rechecks file identities before returning. This establishes evidence consistency, not authenticity of arbitrary receipts; the legacy R2E backend is unchanged.

Fresh reassessments preserve expected decisions: CRC153 native004 and corrected csv2md22 native002 pass mechanical checks; original csv2md22 and files-to-prompt36 remain blocked by publisher expectations. All remain training-unapproved. The ten-file reassessment bundle (39,527 bytes) is R2-published and independently restored.

Full local suite: 571 tests passed, zero skips, 21.081 seconds. Current hashes of all 315 bound source files match the tested snapshot. Independently rechecked all 318 archived inner files. Four-file archive (591,110 bytes) has verified R2 upload and restore receipts. Evidence: evidence/p1/full-suite-qualification-004 and evidence/data/raw-grade-admission-evidence-001. These checks do not qualify full-size model execution, GPU kernels or deployment performance.

Released only the redundant shard001 restore-check parquet after local hash verification, fresh full R2 object read/hash verification, exact remote manifest comparison and an unchanged local file-identity check. Confirmed removal; released allocated bytes: 151,552,000 (about 144.5 MiB). Source metadata, manifests, selected trajectories and runtime retained. Evidence: evidence/data/swe-hero-restore-release-003. This does not establish that iCloud's general Download Now issue is fixed.

P1 remains incomplete: corpus055 has 39 quarantined examples and 216,751 supervised tokens, with zero training-admitted tokens. Rights, source qualification, frozen split and duplicate review, substantial data scale-up, and training runtime/memory qualification remain open. Runpod unused. Next data step is semantic/rights/split review of corrected csv2md22 and qualification of remaining batch candidates; passing finite controls alone is insufficient for training admission.


## 2026-10-12: frontmatter31 explicit baseline and native replay

Default pytest discovery missed this repository's test.py. Explicit discovery exposed missing six; a bounded modern compatibility environment installs PyYAML6.0.3, six1.17.0 and toml0.10.2 from exact PyPI wheels verified against publisher SHA256 and size, with a hash-required offline lock. Explicit upstream run: 13 cases passed. Historical requirements pin PyYAML3.11/six1.10.0/toml0.9.1, so this is not historical dependency equivalence. Optional pyaml is absent and its conditional behavior remains unexercised.

Offline image sha256:9902a8ce40835efd0e1a298efd13d49f88aa2dbc2792b09dd12ef1789de2762c uses a parentless snapshot of e017a210fc4c9725c36fb970df03a32cd655aa77. Independent container verifies all tracked bytes/tree, exactly one parentless commit, no remotes and inaccessible original commit. Inherited image layers are not audited for historical content.

Native replay completes 38 charged calls, 39 exchanges and 80 messages. Actual tokenizer audit: 19,021 input tokens, 7,302 shifted supervised targets; input plus 8,192 output reserve is 27,213. Patch is 1,114 bytes, SHA256 99892f201185cf325b5657edc331a0ca28e130ccaf1d6b940dbf94aedf7d396a. It adds explicit encoding parameters to load/dump filename handling. No publisher grading or task-semantic approval is established; file-like and byte-input semantics require independent checks. Source observations are not reused. Container and temporary 200,489,804-byte source shard were removed after verification.

Evidence bundle: evidence/data/frontmatter31-native-evidence-001. Corpus055 unchanged, training approval false, Runpod unused. Next: freeze these artifacts before inspecting publisher controls; evaluate base/reference/candidate and independently exercise encoding behavior. A source teacher replay is not evidence of improved Gemma performance.

Archival confirmed: all 53 files (2,245,087 bytes) published to R2, independently restored and compared by per-file hash. Build inputs are archived; the Docker image itself is not exported.


## 2026-10-12: frontmatter31 publisher grading and independent encoding failures

Frozen native replay/history/token artifacts before extracting publisher-only patches from the identity-verified SWE-rebench shard; rechecked all frozen hashes after extraction. Fresh isolated publisher controls reproduce 11/13 base passes and 13/13 reference passes. Teacher candidate passes 12/13: test_with_crlf_string still fails because loads lacks the positional encoding argument. Raw-outcome recomputation blocks mechanical admission with publisher_expectations_not_matched. Corpus055 remains unchanged.

Independent finite API/codec matrix evaluates six operations (load filename, load BytesIO, loads bytes, parse bytes, dump filename, dump BytesIO) across UTF-8, cp1252, UTF-16 and ASCII with representable payloads: 24 cases per variant. Loading checks exact content and metadata, detecting encoding accidentally captured as metadata defaults. Dumping compares actual bytes with dumps(post).encode(encoding), plus inverse decoding. Base passes2/fails22, teacher passes10/fails14, publisher reference passes20/fails4. Each container is removed; frozen repair patches remain unchanged.

All four reference failures are filename dumping: reference encodes content to bytes, then passes bytes to codecs.open's text encoder, raising TypeError. Publisher tests do not exercise this path. Therefore publisher agreement alone cannot establish task-level correctness. The teacher's filename handling works but its byte-input and binary-output coverage is incomplete. These are finite contemporary-Python compatibility controls, not universal codec proofs or historical runtime claims; existing optional pyaml coverage remains absent.

Evidence: evidence/data/frontmatter31-evaluation-evidence-001. Training approval remains false; Runpod unused. Any correction must be explicitly marked as a post-evaluator-exposure derivative, preserve the failed prefix and diagnostics, and independently validate filename/text-stream/binary-stream semantics before fresh replay and grading. Do not copy the reference's filename-dump defect merely to agree with its narrow tests.

Archival verified: 56 files / 83,370 bytes uploaded to R2 and independently restored, with original/restored per-file hashes compared.


## 2026-10-12: frontmatter31 explicit encoding correction and replay002

Post-evaluator-exposure assistant derivative propagates encoding through parse/loads/load and keeps filename output as text through a codec writer, preventing double encoding. Standard binary IO and streams declaring binary mode receive encoded bytes. Other writers preserve the original text protocol. No write-and-retry dispatch is used, avoiding a second write after an ambiguous failure. Opaque custom binary sinks without type/mode declarations are not autodetected; this remains an explicit API limitation.

For representable Unicode text and the tested codecs, the check uses decode(encode(text,e),e)=text, exact parsed metadata/content and exact output bytes from dumps(post).encode(e). Expanded finite matrix: four codecs and eight operations, including StringIO and a custom text writer, gives32cases pervariant. Base10pass/22fail; originalteacher18/14; publisherreference20/12; corrected32/0. This covers the observed defects, not all codecs, custom writers, platform encoders or historical dependency behavior.

Fresh attributed completion appends repair plus upstream and encoding assertions to the unchanged source prefix. No publisher tests injected into history. Native002:40chargedcalls,41exchanges,84messages;23,562inputtokens/11,758shiftedsupervisedtargets;31,754with8,192reserve. Patch2,327bytes SHA25676a4e8b9bb524d827ef02885b7ba236e66ae7b9389f319370175965144bac05d. Publisher candidate13/13matchesreference; raw-outcome mechanical admission passes. Training approval remainsfalse and corpus055unchanged pendingsemantic/rights/splitreview. All disposable containers and temporary source shardremoved. Runpodunused.

Evidence: evidence/data/frontmatter31-corrected-evidence-002. This is repaired supervision and finite functional validation, not new Gemma performance evidence. P1 remains incomplete and substantial dataset scale-up remains necessary.

R2 archival confirmed:52files,583,219bytes,published and independently restored with all per-file hashes compared.


## 2026-10-12: semantic integration holds and codec-stream regression

Targeted history review blocks integration of csv22 native002 and frontmatter31 native002. This is not an exhaustive rights/privacy/history review. Hash-bound findings identify exact assistant messages. csv22's reproduction checks pipe membership in line.split('|')[1], which is identically false: splitting on a single-character delimiter leaves no delimiter in any component. A finite 1,093-string enumeration confirms the implementation property but the argument applies to all strings. Another diagnostic miscounts columns from raw delimiters, and a comprehensive helper prints Boolean failures without propagating a nonzero exit. Frontmatter helpers likewise catch/print failures, and one accepts arbitrary exceptions for an invalid-codec test. These observations are not fabrication, but they are unsuitable as unqualified successful-test supervision.

Review also prompted a missing production edge-case check: codecs.open text wrappers can expose binary mode from their underlying stream. Native002's correction dispatches bytes based on that mode and fails all four added codec-stream cases, despite13/13publisher and32/32previous finite controls passing. Expanded36-case matrix:base14pass22fail,originalteacher22/14,publisherreference20/16,correction00132/4. Prior evidence remains historically accurate at its narrower scope but does not establish codec-stream correctness.

Correction002 prioritizes codecs.StreamReaderWriter/StreamWriter text protocols before mode-based binary dispatch. Fresh five-variant36-case matrix reproduces predecessor failures and gives36pass0fail for correction002. This corrected patch is not yet replayed or publisher-graded; native002 remains blocked. Opaque custom binary sinks without a type/mode declaration remain outside automatic detection. Evidence: evidence/data/two-candidate-review-evidence-001. Corpus055 unchanged,zero admittedtokens,Runpodunused,P1incomplete. Next: attributable diagnostic amendments plus fresh completion/replay and grading, then source/rights/split review; do not infer corpus eligibility from mechanical passing alone.

R2 publication and independent restoration confirmed:46files,93,111bytes,all original/restored file hashes matched.


## 2026-10-12: frontmatter31 attributed diagnostic amendment and replay003

Three created diagnostic files are amended under exact canonical source/derived action hashes. Selected broad handlers now re-raise failures; invalid-codec checks require LookupError and fail when no exception occurs. Compatibility claims are narrowed to exercised examples. No actions are removed/reordered and original histories remain preserved. The separately bound completion applies correction002, including codec text-wrapper handling, and exercises that path in fresh native observations.

Independent mutation controls verify four role/fault combinations: an injected load RuntimeError and a silently accepted invalid codec are swallowed by the original helpers but propagate as RuntimeError/AssertionError in the amended helpers. Injected responses are restricted to evaluator controls and never enter the training history. This is targeted validation of the identified diagnostic defects, not an exhaustive semantic review.

Native003 completes40chargedcalls/41exchanges/84messages. Exact token audit:23,679inputs,11,887shiftedsupervisedtargets;31,871with8,192reserve. Fresh production publisher grade13/13matchesreference and raw-outcome mechanical admission passes. Latest correction has36/36independent encoding cases from controls004. Temporarysource shard and containersremoved. Evidence: evidence/data/frontmatter31-amended-evidence-003.

Training approval remainsfalse; corpus055unchanged. Full source/history/rights/splitreview still required, including the documented opaque custom-binary-stream limitation and optional pyaml coverage. csv22's diagnostic holds remain unresolved. P1 remainsincomplete;Runpodunused. Mechanical passing is not corpus eligibility or evidence of improved model performance.

R2 publication and independent restoration confirmed:40files,712,115bytes,all per-file hashes matched.


## 2026-10-12: csv22 attributed diagnostic amendment and replay003

Three created helper files amended under canonical source/derived hashes. The impossible split-component predicate becomes a literal unescaped-source-sequence diagnostic; raw pipe count is explicitly not presented as parsed Markdown column count. CLI subprocess failures now propagate. The comprehensive helper returns process failure whenever either Boolean result fails. Existing historical width-error/fix sequence is preserved rather than retrospectively hiding failures. Original histories remain intact.

Independent truth-table control extracts the actual original/amended main blocks, injects all four Boolean helper-result combinations and verifies eight subprocess outcomes. Original always exits0; amended exits0 exactly when both results aretrue. This is exit-status validation, not Markdown rendering proof. Injected results are evaluator-only.

Fresh native003 uses amended source actions and the separately bound parsing-preserving completion. It completes40chargedcalls/41exchanges/84messages;24,112inputtokens/7,201shiftedsupervisedtargets;32,304with8,192reserve,within32,768. Fresh publisher grading9/9matchesreference; raw-outcome mechanical admission passes. Production patch remains the independently510-case-checked pure-render correction; no new patch performance claim. All temporary shard data and replay/grading containersremoved.

Evidence:evidence/data/csv22-amended-evidence-003. Training approval remainsfalse,corpus055unchanged. Full history/source/rights/split review is still pending; repairing the identified diagnostics does not imply every statement or command is qualified. P1 remainsincomplete and Runpodunused.

R2 archival confirmed:36files,620,356bytes,published and independently restored with all hashes compared.


## 2026-10-12: two-candidate repository and lexical isolation checks

Fresh GitHub metadata for lzakharov/csv2md and eyeseast/python-frontmatter checked for exact canonical repository identity and network-root IDs. Neither overlaps reserved names or known network roots from the hash-verified historical registry, nor existing corpus repository networks. Existing registry metadata is historical; detached copies and unrecorded relationships remain unexcluded. Reserved evaluation issue bodies were not read.

Retained byte-identical MIT notices from both pinned source checkouts with copyright attribution. This records source notices only; rights to complete trajectories and downstream training remain unapproved. Added the independently reconstructed issue texts to a review inventory with the39existing corpus issues; neither new task triggers Jaccard>=1/10 or containment>=1/5 lexical screening. The inherited PennyLane overlap remains. All820pair intersection/union/containment counts independently crosschecked by set operations and exact Fraction arithmetic. This does not establish semantic independence.

Both native003 history trees pass the narrow source credential-indicator gate, with before/after identity checks; privacy approval remainsfalse. Evidence:evidence/data/two-candidate-isolation-evidence-001. Corpus055unchanged; no frozen split or training approval inferred. Remaining work includes complete history/source review, trajectory-rights qualification and substantial data expansion. Runpodunused;P1incomplete.

R2 publication and independent restoration confirmed:10files,171,480bytes,all per-file hashes matched.


## 2026-10-12: corpus056 quarantine integration and capacity assessment

Versioned csv22 native003 and frontmatter31 native003 as explicitly post-evaluator, assistant-amended inspection candidates. This is quarantine storage, not a completed review or training admission. Verification records retain full-history, rights, privacy and frozen-split holds. All39predecessorrecords preserved exactly;41examples/41tasks/40repositorygroups. Independent totals807,897inputs and235,839shiftedsupervisedtargets agree with production loader. ManifestSHA25689913c88a792b88a1c9305e04a82d046a9d8e42fa0eace6c73ee5ff380d56908. Every admissiongate remainsnull and an actual training-purpose load rejects the corpus.

R2 corpus83files/8,950,093bytes uploaded/restored/allhashescompared; production loader revalidated restored bytes. Integration evidence18files/227,819bytes likewise R2verified. Redundant staging and independently restored corpus copy removed after fresh comparisons; authoritative corpus retained. Evidence:evidence/data/corpus056-integration.

Exact capacity arithmetic:50Mtokens per candidate would consume212complete passes plus2,132tokens from pass213, even if all current targets were admitted. They are not: admittedtokens remainzero. A hypothetical maximumthreepasses would require16,666,667unique supervisedtokens,shortfall16,430,828; this is an illustration,not an approved repetition policy. Repetition does not add tasks or repositories. Evidence:evidence/data/corpus056-scale-evidence-001. Substantial source expansion and qualification remain essential; no industrial quality or model-performance claim follows from this corpus. P1incomplete,Runpodunused.


## 2026-10-12: structlog350 bounded dependency/runtime qualification

Pinned ten dependencies from PyPI release metadata with exact wheel sizes/SHA256:freezegun1.5.1,pretend1.0.9,python-dateutil2.9.0.post0,six1.17.0,pytest8.3.5,pytest-asyncio0.25.3,iniconfig2.1.0,packaging24.2,pluggy1.5.0,simplejson3.20.1. Offline install uses hash-required lock and no dependency resolution. Import origin verifies the independently fetched source under/testbed/src/structlog. Original pinned source remains unchanged; containers removed.

First explicit upstream run:440passed,12failed,16skipped. Eleven failures stem from async fixtures being treated as plain fixtures under strict asyncio mode. A second fresh run with explicitly configured --asyncio-mode=auto yields451passed,1failed,16skipped. No test expectations or repository code changed. Remaining failure:test_threadlocal.TestThreadLocalDict.test_delattr_missing expects a bare missing-attribute name while Python3.13 returns a descriptive AttributeError message. This modern environment is not fully qualified or equivalent to historical supported Python versions. Skips include Windows,better-exceptions,greenlet and parameterized optional coverage; they are not counted as success.

Source issue concerns bytearray acceptance by the final logging processor. No publisher solution/test fields inspected and no training example created. Evidence:evidence/data/structlog350-runtime-evidence-001. Next requires an explicit supported runtime decision or bounded task-specific controls with the full-suite limitation retained, followed by native replay and publisher comparison. Corpus056unchanged,Runpodunused,P1incomplete.

R2 archival confirmed:54files,2,407,066bytes,published and independently restored with all per-file hashes compared.


## 2026-10-12: structlog350 source snapshot and no-op edit replay blocker

Built pinned offline image32b6af744f665141b4b86476c44c1e0f08d2231fcb3412dd288512ff451c2117 with the reviewed dependency lock and explicit asyncio auto mode. Parentless snapshot preserves upstream tree at6bd5b32ea58a9f9a8edfd846284f918b78fe3468. Independent container verifies all tracked bytes/tree,one parentless commit,no remotes and inaccessible original base commit. Native import root is explicitly/workspace/src. Known broader runtime limit remains451pass/1fail/16skips; not historical environment equivalence.

Fresh replay captures33source events before stopping at sourceindex66. Native edit_file rejects a str_replace whose old_string and new_string are byte-identical. The replay's general mutation-error rule aborts. This is a concrete no-op compatibility restriction,not proof that the bytearray repair itself is incorrect. No submitted patch or complete history is claimed. Receipt status=incomplete;trainingfalse. Container and temporary200,489,804bytesource shard removed. Original observed error retained; no publisher patches/tests inspected.

Evidence:evidence/data/structlog350-replay-evidence-001. Next:qualify explicit no-op behavior with unchanged-state verification and negative controls,without suppressing genuine failed edits or fabricating success. Corpus056unchanged,Runpodunused,P1incomplete.

R2 archival confirmed:34files,1,935,098bytes,published and independently restored with all file hashes matched.


## 2026-10-12: verified rejected-no-op replay support

Added zenithsync/replay_noop.py and narrow native replay integration. Only nonempty identical replacement strings with exactly one occurrence in a bounded regular UTF-8 file qualify. Before/after snapshots checkSHA256,size,device,inode,mode,mtime,ctime; symlink paths and unstable reads reject. Native result must exactly match the known FileEditError for identical old/new strings. The error remains in observations; a separate event annotation records unchanged target evidence. Genuine mutation/submission errors retain the stop rule. Snapshot reads are adapter verification,not charged agent tool calls; module identity is recorded in replay receipts. Scope is the target file,not a claim that every container byte is unchanged.

Seven targeted tests cover valid no-op preservation,changedstate,missing/repeatedmatches,invalidUTF8,symlinks,noncanonicalpaths,unexpectederrors and malformed snapshots. Full local suite578tests passed,zero skips,23.623seconds,source identities bound. Reduced-model CPU tests included; no full-size/GPU runtime qualification. Full-suite archive4files/594,645bytes R2verified with320innerfilehashes checked. Evidence:evidence/p1/full-suite-qualification-005.

Structlog350 native002 now completes53chargedcalls,54exchanges,110messages with one verified rejected identical edit. Submittedpatch1,258bytesSHA2569d4ce0bfbed00ca147f4da738d10eeebb107af46c38f618903282cb031d28125. Actual tokens23,859inputs/7,489shiftedtargets;32,051with8,192reserve. Contextfits but53calls exceeds40-callpolicy. Remains outside corpus; do not increase policy or truncate history merely to force acceptance. Publisher grading remains undone. Container and temporarysource shard removed. Evidence:evidence/data/structlog350-noop-replay-evidence-002. Corpus056unchanged,Runpodunused,P1incomplete.

Replay archive21files/562,587bytes R2published and independently restored,all per-file hashes compared.


## 2026-10-12: native-call-aware batch expansion

Reparsed128hash-verified cached histories with current source converter and native adapter.88passstaticpreflight;19fit40chargedcalls and12fit38,leaving room for two completioncalls. One native charge per shell/view/create/replace action is independently crosschecked against source tool calls and four completed native receipts(csv22,frontmatter31,filesprompt36,structlog350);predictedcounts match. Source-format token lengths remain no guarantee of native context fit. This is deterministic development triage,not a statistical performance estimate.

Eightnewprioritytasks remain after excluding corpus056 and completedattempts:nbgrader1410,pypinfo137,pandas_market_calendars11,djangorestframework-api-key187,pytypes37,kombu1754,pubmed_parser89,tianshou67. The38-call preference does not declare39/40-call histories invalid; those remain in the full screening record. Two source trees were already acquired. Of six new fetches,fourpassfulltree/blob verification:pypinfo51,602bytes,pandas_market_calendars188,106,kombu1,697,303,tianshou1,267,965. nbgrader and pubmed_parser exceed10MBmaterializationlimit;no archive payload downloaded for them. Do not relax the storage bound silently.

Combined archive3files/1,591,096bytes R2published/restored;all511innerfilehashesverified. Removed redundant staging and independent restore copy after comparison; original working sources retained. Evidence:evidence/data/budget-batch-source-evidence-001. These sources have no runtime or training qualification yet. Corpus056unchanged,Runpodunused,P1incomplete. Next:bounded runtime qualification for the new candidates; source-scale expansion remains far short of the50M-per-candidate plan.


## 2026-10-12: new batch baseline and kombu1754 JSON environment

Four independently verified new repositories ran in fresh offline containers with read-only sources and unchanged-source checks. Baseline collection blockers:pypinfo requires freezegun/platformdirs;pandas_market_calendars requires pandas;kombu requires amqp;tianshou requires torch/numpy. Allcontainersremoved. These failures are dependency evidence,not task-solving outcomes.

Kombu's source issue concerns UUID JSON round trips beyond historical versions1-5. A bounded offline environment pins13PyPIwheels by SHA256/size,including amqp5.3.1,vine5.1.0,hypothesis6.131.9,attrs25.3.0,sortedcontainers2.4.0,pytest7.3.1,pytest-freezer0.4.9,freezegun1.5.1,python-dateutil2.9.0.post0,six1.17.0,iniconfig2.1.0,packaging24.2,pluggy1.5.0. JSONmodule tests11/11pass underPython3.13. This includes the existing Hypothesis tests but is not an exhaustive UUID proof or full-suite/historical-runtime qualification. Source import path is verified; no live services or credentials used.

Built image99a2b84bb377612fd0f18da23df0ea38e164172c7698a30ddc950bc4997bc22c from the pinned base with offline hash-required installation. Parentlesssnapshot independently verified against all fetched upstreamtrackedbytes/tree;onecommit,noremotes,originalbaseinaccessible. Hypothesis scratchstorage routes to/tmp. Dockerimage remains local; buildinputs are archived. No publisher test/solution fields inspected, no native replay or training approval yet.

Evidence:evidence/data/kombu1754-runtime-evidence-001. Corpus056unchanged,Runpodunused,P1incomplete. Next:native replay followed by independent UUID identity/round-trip controls and publisher grading with frozen artifacts.

R2 archival confirmed:80files,4,156,376bytes,published and independently restored with all per-file hashes compared.


## 2026-10-12: kombu1754 native replay and context exclusion

Native replay completed 36 charged calls, 37 exchanges and 76 messages in the pinned offline image. Submitted one-line UUID decoder change uses UUID(hex=o["hex"]) instead of reapplying version metadata. Patch SHA256 e3998a6f1e0dda3f7bcf46e09e2267d8fb622ed52b38c5c1313425387809e55f. Container removed and the temporary 245,825,405-byte source shard deleted after full hash verification.

Independent finite controls cover 16 version nibbles x 8 variant prefixes x 8 deterministic payloads x 4 input representations, with integer and byte preservation checked against the original 128-bit value. Base: 3,392 passed / 704 failed. Candidate: 4,096 passed / 0 failed. Forced-version-4 mutant: 64 passed / 4,032 failed. This is finite repair evidence, not exhaustive 128-bit coverage, historical runtime qualification or full-history approval.

Native token export correctly rejected the history as out of bounds. A separate non-exporting diagnostic records 32,917 input tokens and 7,748 shifted supervised targets without truncation. With the fixed 8,192 output reserve, total demand is 41,109 versus the 32,768 budget. Candidate is excluded from corpus056; no policy relaxation, shortened history or training token export. Publisher grading is deferred and publisher oracle fields remain unread. Static source call-budget screening alone does not predict native context fit.

Evidence: evidence/data/kombu1754-replay-evidence-001. Corpus056 unchanged, admitted tokens remain zero, Runpod unused and P1 incomplete. Next: continue source qualification with context-aware triage while preserving complete observations; sufficient diverse qualified data remains a major unmet requirement.

R2 archival confirmed: 32 files, 1,623,262 bytes, independently restored and all file hashes compared. Redundant publication staging and restore copies removed after comparison with retained repository evidence.


## 2026-10-12: verified SWE-rebench-V2 raw-shard release

Published/verified the complete four-file SWE-rebench-V2 source artifact, then independently restored all 428,868,318 bytes and compared every file against the original manifest. Removed only the original raw Parquet payload after a final local identity/residency check and durable pre-unlink record. Removed the temporary restored directory. Released 428,843,008 allocated bytes (about 409 MiB); original source metadata, manifest, intake receipts and selected task extracts retained. This is not a claim that macOS has immediately reduced its physical-volume usage by exactly that amount.

Evidence and restoration instructions: evidence/data/rebench-v2-local-release-001. Older extractors expecting artifacts/data/quarantine/swe-rebench-v2-shard-001/data/train-00000-of-00001.parquet now require a verified R2 restore first. No training admission or dataset-rights change. Runpod unused; corpus056 unchanged and P1 incomplete.

Next runtime candidate pypinfo137 was inspected before provisioning: source-format history is 43,468 tokens and core imports Google BigQuery. This source-format measurement is neither a native-context acceptance nor a rejection. No additional dependency environment built in this cycle; storage release took priority. Native-context and complete dependency qualification remain necessary.

Release evidence also R2-published and independently restored: 7 files, 8,235 bytes; all hashes matched.


## 2026-10-12: current training-worker R2 recovery qualification

Staged the current explicit 42-file / 226,786-byte training worker bundle; all eight CLI help/import checks passed in isolation. Published and independently restored the bundle with manifest SHA256 5328ce1d319ead0386ecb5924d3d55443707e6b5e0214fa036caf09755c25c9b. Independently restored corpus056 (83 files / 8,950,093 bytes). The restored worker inspected the complete corpus successfully and rejected purpose=training with Quarantine corpus cannot train.

Focused tests exercised object transport, corpus validation, token scheduling/weighted optimization, optimizer state, checkpoint storage, adapter recovery and training sessions against restored production modules. First harness attempt: 54 tests, one failure and one error caused by an incorrect optimizer test-module name and a missing package path in a fresh subprocess. Those logs remain unchanged. Corrected only the harness: selected test_optimizer_checkpoint_torch and linked the restored package into the owned test overlay. Second attempt: 58 tests passed, zero skips; production import origins checked, all restored source and corpus bytes reverified. The temporary package link was removed after testing.

Evidence: evidence/p1/training-deployment-recovery-evidence-001. This is current local CPU source/data recovery evidence, not Linux/CUDA equivalence, full-checkpoint optimization, long-run training or model improvement. P1 remains incomplete; corpus056 remains quarantine-only with zero admitted tokens. Runpod unused. No production code changes in this cycle.

Recovery evidence archived to R2 and independently restored: 4 outer files / 281,179 bytes; all 249 inner member hashes verified. Removed the redundant restored corpus copy after fresh comparison; original corpus retained.


## 2026-10-12: Django API-key187 supported-version offline baseline

Pinned 22 PyPI wheels for Python3.9/Django3.2.25/DRF3.12.4/pytest6.2.5, including pytest-django, coverage and all tested password hashers. Each wheel matches official metadata size/SHA256; aggregate wheel cap16,000,000bytes. x86-64 selection11,495,747bytes; ARM64 selection11,482,653bytes. Common wheel bytes reused locally for the second selection.

Initial container creation rejected linux/amd64 because the available pinned Python3.9 image cf0704507972b63c9b20382dd6f05248572d6b25961410305f96479bf2e8a23c is ARM64. No tests ran in that first attempt. A second fresh offline ARM64 container used matching wheels, source read-only, explicit src import origin and temporary coverage/dependency paths. All62upstream tests passed with pytest exit0; repository coverage threshold80% met (reported96.55%). All recorded phases pass, no skips; four warnings retained in log. Source inventory unchanged and container removed.

This qualifies the tested Python3.9/Django3.2 SQLite configuration locally, not PostgreSQL, x86-64 replay, publisher controls or training readiness. No publisher oracle fields inspected. Native replay remains pending; source-format history30,964tokens is not a native-context fit decision. Evidence:evidence/data/djangoapikey187-runtime-evidence-001. Corpus056 unchanged, zero admitted tokens, Runpod unused, P1 incomplete.

Runtime archive R2-published and independently restored:4outerfiles/21,944,171bytes;all111innerfilehashesverified. Redundant archive staging, local archive bundle and restore copy removed after verification; original dependency/runtime evidence retained.


## 2026-10-12: Django API-key187 offline snapshot and native replay

Fetched Git/system packages in a disposable credential-free ARM64 container using APT signature/hash checks and an explicit50MB package-download cap; archived downloads and plan bind exact packages. First offline image build failed with APT's relative-path internal error for perl-base. Preserved its log. Second build used the same downloaded packages through dpkg -i and required an empty dpkg --audit result. No network used during image construction. Image57762e8cd04b8b803ae9cd35f11f7b0928a0f7280ed540b70ad96976e7afc08d.

Independent container checks all tracked source bytes/tree against pinned upstream dd806cf8b9879ae37e3b0c0a57f9209dab61c25b,one parentless commit,no remotes and inaccessible original commit. Native ARM64 replay completed33chargedcalls,34exchanges,70messages. Full pinned-tokenizer rendering:22,412inputs/3,749shiftedtargets;30,604including8,192reserve fits32,768. Patch2,299bytesSHA256eca2cd63c94056610148f8eb6d799b4736c70cd2842dfcd727bf0971bbd1c912. Replay container and temporary source shard removed.

No training admission: submitted patch includes reproduce_warning.py beyond the intended package source; warning reproduction redirects stderr without explicitly enabling deprecation warnings, so absence-of-warning claims need a negative control. Publisher grading and complete semantic,rights,privacy,split review remain pending. Publisher oracle fields unread. Native history is preserved without shortening. Evidence:evidence/data/djangoapikey187-replay-evidence-001. Corpus056unchanged,Runpodunused,P1incomplete. Next: independent warning controls and explicit source-only completion if justified, then freeze and publisher grading.

Replay/build evidence R2-published and independently restored:4outerfiles/35,561,368bytes;all96innerfilehashesverified. Redundant staging/archive/restore copies removed after fresh validation; original working evidence retained.


## 2026-10-12: Django API-key187 warning negative controls and corrected replay

Fresh-process ARM64 Django3.2.25 controls prove both source warning diagnostics falsely report absence on unchanged code. Initial script captures warnings after django.setup; warning is emitted outside the capture. Replacement redirects stderr but leaves deprecation warnings filtered. Independent explicit always-filter capture surrounding setup detects exactly1targetwarning on base and0on candidate, and verifies application config loads. This is version-specific evidence, not historical-version equivalence.

Before any publisher oracle exposure, appended two explicitly assistant-authored completion commands: remove only the SHA256-bound reproduction script, then run the correct fresh-process warning capture plus upstream tests with failures propagated. Original prefix and erroneous observations are preserved; completion explicitly explains those false negatives. New replay002 completes35chargedcalls,36exchanges,74messages; actual tokens23,494inputs/4,317shiftedtargets and31,686including8,192reserve. All62upstream tests pass in the appended command; four unrelated warnings retained. Appended pytest overrides addopts to avoid repeated coverage output; earlier baseline independently met the repository coverage threshold.

Final patch is source-only:708bytes,SHA2568333802709173030023b01a7a68d60920b5f3830301d9b2157b195b75691103c. No new-model evaluation. Complete history still requires semantic review (including earlier faulty diagnostics and the source grep pipeline); publisher grading,rights,privacy,split qualification pending. No corpus integration or training admission. Replay container and temporary source shard removed. Evidence:evidence/data/djangoapikey187-corrected-replay-evidence-002. Corpus056unchanged,Runpodunused,P1incomplete. Next: freeze this corrected attempt before publisher extraction and qualify grading on the explicit ARM64 environment.

Corrected replay/control evidence R2-published and independently restored:33files/532,032bytes,allhashesmatched. Redundant publication staging and restore copies removed after comparison with retained evidence.


## 2026-10-12: explicit evaluator architecture and Django publisher comparison

Added optional validated platform to the execution profile: linux/amd64 or linux/arm64 only; omitted platform preserves existing amd64 behavior. Both base/reference and candidate runners forward it explicitly to Docker. Rejected unsupported/ambiguous profile values in tests. Full local CPU suite579tests passed,zero skips,20.923seconds; source-bound evidence R2archived/restored4files595,070bytes with320innerhashesverified. Evidence:evidence/p1/full-suite-qualification-006. This is not full-model/GPU qualification.

Froze corrected Django replay002,history and tokens before extracting publisher oracle fields; frozen files rechecked unchanged after evaluation. All publisher runs use the same pinned ARM64 image, Python3.9/Django3.2.25, src import root and full tests directory. Base:62passed/1failed/1skipped. Reference:63passed/1skipped. Candidate raw diagnostic:63passed/1skipped. Exact64collectednodeidentities match across roles. Candidate source-only patch remains unchanged by tests.

Strict compare_controls rejects the skipped outcome. The publisher adds mutually exclusive version-conditioned tests: test_app_config_not_defined runs on Django>=3.2; test_app_config_defined skips there and applies below3.2. We retain the skip and do not mark it passed or issue mechanical admission. The raw candidate diagnostic is explicitly non-admitted; older-version branch remains unexecuted. No publisher tests inserted into replay history and no source/history revision after oracle exposure.

Evidence:evidence/data/djangoapikey187-publisher-evidence-001. Corpus056unchanged,zero admittedtokens,Runpodunused,P1incomplete. Next: qualify a supported older-Django environment and define explicit version-matrix evidence without weakening skipped-test checks or hiding unexecuted branches. Full-history,rights,privacy,split review remains necessary even if version coverage is resolved.

Publisher diagnostic evidence R2-published/restored:41files/199,804bytes,allhashesmatched. Redundant staging/restore copies removed after comparison.


## 2026-10-12: Django API-key187 two-version execution coverage

Downloaded the official Django 3.1.14 wheel within a 9 MB bound and verified its PyPI size/SHA256. Built an offline ARM64 environment atop the verified Python 3.9 replay image, replacing only Django; pip check passed. Image e77233cf27c4e60857abe458a8242f74bce57c79e3fbc4bb54499aec9040805c. Independent snapshot verification preserved all upstream tracked bytes, the exact tree and parentless history.

Full publisher suite on Django 3.1.14: base, reference and candidate each 63 passed / 1 skipped. The skipped test is test_app_config_not_defined, which applies to Django >=3.2. The older-version test_app_config_defined executes and passes for all three roles. Django 3.2.25 results remain base 62 passed / 1 failed / 1 skipped, reference and candidate 63 passed / 1 skipped.

Exact two-version reconciliation checks all 64 node identities, unique phase identities, setup/teardown outcomes, applicable call outcomes, the two explicit skipped branches and exit codes. Every node executes in at least one applicable version for each role. No skipped execution is counted as passed. This closes the previously unexecuted older-Django branch for these two tested versions, not every supported version or PostgreSQL/x86-64 compatibility.

Evidence: evidence/data/djangoapikey187-matrix-evidence-001. No source or replay history changes after publisher exposure. The existing strict single-environment grader still rejects skips; a tested, explicit matrix admission contract remains unimplemented. History, rights, privacy and split review remain open. Corpus056 unchanged, zero admitted tokens, Runpod unused and P1 incomplete.

Matrix evidence archived to R2 and independently restored: 4 outer files / 7,456,223 bytes; all 48 inner file hashes verified. Redundant archive staging and restore copies removed after validation.


## 2026-10-12: reusable explicit pytest matrix outcome contract

Implemented zenithsync/pytest_matrix.py. Caller must supply exact applicable node lists for each named environment; applicability is not inferred from observed skips. All base/reference/candidate documents must collect the same full unique node set. Inactive nodes require skipped setup, passed teardown and no call. Active nodes retain original collection errors and exit status and pass through the existing strict phase verifier. Every node must execute somewhere; every active reference/candidate obligation must pass, with at least one base failure demonstrating a repair transition. Unexpected skips, missing/duplicate phases, inconsistent collection, inactive calls and uncovered nodes reject. No skip is relabeled passed. Inputs remain unchanged.

Six tests cover the complete matrix and negative cases. Full local CPU suite: 585 tests passed, zero skips, 20.282 seconds. Applied the contract to all six recorded Django role/version executions: 64 exact nodes covered; one repair transition, test_app_config_not_defined on Django 3.2.25. Application binds raw outcomes and runtime receipts, publisher test-patch identity and explicit reviewed applicability declarations. The verifier checks declared obligations, not the truth of arbitrary caller declarations; runtime/version/provenance authentication remains a caller responsibility.

Evidence: evidence/data/djangoapikey187-matrix-contract-evidence-001 and evidence/p1/full-suite-qualification-007. This is an outcome contract, not an integrated mechanical-admission or corpus-approval path. Existing strict single-environment grading is unchanged. Need to bind matrix evidence into admission without accepting unreviewed applicability, then complete full-history/rights/privacy/split review. Corpus056 unchanged, zero admitted tokens, Runpod unused and P1 incomplete.

R2 publication and independent restoration confirmed: matrix contract 24 files / 282,161 bytes; full-suite archive 4 files / 599,000 bytes with all 322 inner hashes verified. Redundant matrix staging/restore copies removed after comparisons.


## 2026-10-12: source-derived version applicability

Added zenithsync/pytest_applicability.py, a non-executing AST interpreter for a deliberately restricted test-module language: direct imports, plain top-level tests and direct pytest.mark.skipif comparisons between django.VERSION and literal integer tuples. Unsupported expressions, aliases, rebinding, executable defaults/annotations, multiple decorators, duplicate tests and mismatched module collection reject. Callers bind source bytes and actual runtime identity; other modules' conditions remain outside this parser's scope.

Full five-component Django VERSION is required. This preserves Python tuple comparison semantics at equality boundaries; reducing VERSION to a three-component tuple would change comparisons against an equal three-component constant. Tests independently check six comparison operators across boundary versions, false/malformed version inputs and unsupported syntax. No arbitrary Python source execution is used for predicate interpretation.

Fresh offline probes in both exact grading images applied the hash-bound publisher test patch, exported byte-identical tests/test_compatibility.py and read the actual five-component Django versions. All six earlier role runtime receipts match the corresponding probe image identity. Derived applicable node lists feed the matrix contract, reproducing complete 64-node execution coverage and the one expected modern-version repair transition. Evidence:evidence/data/djangoapikey187-predicate-evidence-001. Evidence is not generic applicability approval for other test modules or full training admission.

Full local CPU suite:591tests passed,zero skips,21.764seconds; evidence/p1/full-suite-qualification-008. Matrix-grade binding into replay admission remains unfinished, as do complete history,rights,privacy and split review. Corpus056unchanged,zero admittedtokens,Runpodunused,P1incomplete.

R2 verification complete: predicate evidence15files/78,416bytes; full-suite archive4files/603,350bytes with all324innerhashesverified. Independently restored both; removed redundant predicate staging/restore copies after comparisons.


## 2026-10-12: publisher-complete matrix obligations

Admission integration review found the generic matrix contract proved an observed repair but did not bind it to publisher transition expectations. Added compare_publisher_matrix in zenithsync/pytest_matrix.py. Requires exact expectation categories, unique publisher keys and explicit supplemental pass-to-pass identities. Full whitespace-containing pytest node IDs remain grouped without collapsing members; each member must match the publisher transition in every applicable environment. Exact union coverage is mandatory. Extra baseline failures cannot be relabeled as useful repair transitions. Candidate/reference failures remain rejected by the underlying strict matrix contract.

Declared all63non-publisher collected identities as regression obligations without filtering on observed success. Applied source-derived applicability from the exact grading images: one publisher FAIL_TO_PASS key plus63supplementalnodes cover all64nodes and pass the two-version outcome contract. No skip is counted passed, and no full-history or training approval follows. Producer binds original raw outcomes, image receipts, actual Django VERSION and test-source identities. Mechanical-admission integration remains explicitly false; patch/runtime/probe binding still needs to be verified in that path.

Four new negative/positive test methods cover publisher category disagreement, omitted/duplicate obligations, extra baseline failure and whitespace-group member disagreement. Full local CPU suite595tests passed,zero skips,21.475seconds. Evidence:evidence/data/djangoapikey187-publisher-matrix-evidence-001 and evidence/p1/full-suite-qualification-009. Corpus056unchanged,zero admittedtokens,Runpodunused,P1incomplete.

R2 publication/independent restoration verified: publisher-matrix5files/83,733bytes; regression archive4files/604,894bytes with all324innerhashesmatched. Redundant matrix staging and restore copies removed after validation.


## 2026-10-12: exact matrix probe and runtime bindings

Added zenithsync/probe_receipt.py to reject probe-byte mismatch, wrong image/platform/interpreter, mismatched execution scope, failed export/cleanup, ambiguous Boolean exit codes, OOM and nonterminal container state. This is consistency verification of retained local evidence, not attestation of arbitrary untrusted receipts. Three tests include positive identity preservation and negative program/runtime/status cases.

Reconstructed all six Django base/reference/candidate probe programs using the exact candidate/reference/publisher-test bytes, parentless snapshot commit and source tree, source import path, full tests target, role and known PLUGIN/PROBE implementation. The regenerated source hash equals the executed probe_source identity in every container receipt. Older-version probes include the recorded Django3.1.14 assertion. Runtime role/import/pytest status also matches raw outcomes; primary grading image equals the native replay image. Publisher input identities and native patch/task/base identities match. All source evidence remained unchanged during verification.

Evidence:evidence/data/djangoapikey187-probe-binding-evidence-001. Full CPU suite598tests passed,zero skips,20.618seconds; evidence/p1/full-suite-qualification-010. These stronger probe bindings remain a prerequisite report: the generic replay-admission function has not yet been extended to consume the matrix backend. No mechanical/training approval is claimed. Full-history,rights,privacy,split review remains pending. Corpus056unchanged,Runpodunused,P1incomplete.

R2 publish/independent restore verified: probe evidence9files/64,009bytes; full-suite archive4files/607,256bytes with326innerhasheschecked. Redundant probe staging/restore copies removed after validation.


## 2026-10-12: bounded raw-data release and file-residency audit

Completed archival verification of the three R2E raw-shard release records (005–007): 18 evidence files / 17,097 bytes published to R2 and independently restored with matching file hashes. The released raw Parquet files occupied 568,532,992 allocated bytes; selected examples, metadata and reconstruction manifests remain. Combined with the separately verified SWE-rebench-v2 raw release, recorded released allocation is 997,376,000 bytes (about 951 MiB). This is file allocation, not a guarantee of an equal immediate increase in APFS free space. Restoration instructions and per-shard publication/restore receipts are retained in evidence/data/r2e-raw-release-005-007.

The repository metadata census examined 40,252 files: 598 UF_DATALESS entries, zero metadata-access errors and zero .icloud filename placeholders. UF_DATALESS means nonresident content; it is not evidence of corruption. The Finder Download Now/Keep Downloaded error remains unresolved. Do not remove nonresident files merely because they are flagged. A trusted artifact manifest plus independent R2 recovery is required before replacement/removal. Audit paths and assessment were published/restored with matching hashes (2 files / 61,700 bytes), under evidence/data/repository-residency-audit-001. No bulk hydration or global Docker pruning was performed.

P1 remains incomplete. Matrix admission integration, full-history/rights/privacy/split reviews and sufficient approved training data remain pending. No training approval changed; Runpod was unused.


## 2026-10-12: recomputed matrix evidence contract

Implemented zenithsync/matrix_grade_evidence.py. Explicit hash-bound references supply publisher metadata, declared regression obligations, predicate source, exported five-component Django versions, predicate/role image receipts and all base/reference/candidate outcomes. The verifier re-derives applicability from source, requires identical predicate sources and distinct runtime versions, checks role/predicate image agreement, recomputes publisher transitions and exact node coverage, compares the entire claimed outcome summary, and rechecks all input hashes before return. No directory-search fallback, saved active-node list or passing summary flag substitutes for recomputation.

Four synthetic-fixture tests cover unchanged inputs, lack of training approval, tampered bytes/results, version/source/image substitutions, omitted roles and missing obligations. Full local CPU suite: 602 tests passed, zero skips, 21.492 seconds. Real Django matrix reproduced all 64 test identities from 20 bound input files. Result and descriptor published to R2 and independently restored: four files / 135,148 bytes with matching hashes. Evidence: evidence/data/djangoapikey187-matrix-recomputed-001.

This verifier is deliberately evidence-consistency-only: its image equality checks do not independently authenticate receipts or reconstruct executed probes. The separate exact-probe/snapshot/patch bindings must still be consumed alongside it by replay admission. Full-history, rights, privacy and frozen-split reviews remain open. Corpus056 unchanged, zero admitted training tokens, Runpod unused, P1 incomplete.

Full-suite evidence R2-published and independently restored: four outer files / 611,136 bytes; all 328 inner member hashes verified. Redundant archive staging and restore copies removed after fresh hash comparisons.


## 2026-10-12: semantic binding of matrix probe programs

Added zenithsync/matrix_probe_contract.py. It parses the saved probe's settings with AST literal evaluation, without executing the program. It requires the exact known evaluator body and pytest plugin, rejects executable/duplicate settings, binds role, snapshot/tree, import location, interpreter, test targets and allowed patch paths to explicit caller inputs, and checks base64 payloads against exact candidate/reference/test patch bytes. A bounded optional Django version assertion must match the recorded literal assertion. Receipt verification then binds those exact program bytes to the declared image/platform/interpreter and successful execution/export/cleanup state.

Negative tests recompute receipt hashes for deliberately altered programs, so detection cannot rely merely on a stale hash. They reject narrowed tests, wrong roles/snapshots, changed plugin/body, injected statements, missing/substituted patches and missing version assertions. All six recorded Django role/version probes pass this reusable contract. Evidence: evidence/data/djangoapikey187-probe-contract-001; three files / 10,625 bytes published to R2 and independently restored with matching hashes.

Full CPU suite: 606 tests passed, zero skips, 20.299 seconds. The generic replay-admission backend has not yet been extended: it must combine outcome recomputation, these probe checks, independently bound publisher/task/snapshot provenance and predicate-export provenance before emitting matrix mechanical admission. No claim that caller-supplied image/snapshot assertions authenticate themselves. Corpus056 unchanged; zero admitted training tokens; full-history/rights/privacy/split review pending; Runpod unused and P1 incomplete.

Full-suite R2 publication and independent restoration verified: four outer files / 614,935 bytes and all 330 inner hashes. Redundant archive staging and temporary restore copies removed after fresh comparison; original working evidence retained.


## 2026-10-12: integrated version-matrix mechanical admission

Added the swe_rebench_version_matrix backend to assess_replay_bundle. It recomputes publisher outcomes and source-derived applicability, reconstructs the exact predicate/version exporter, verifies every role probe against known evaluator code and exact patches, and binds task/repository/base, publisher metadata, source snapshot evidence, primary native-replay image, per-version images, import observations and pytest exits. Source trees must agree across environments; snapshot verification inputs remain hash-bound. Existing native-history reconstruction, completion provenance, exact patch/attempt identities, tool counting and context/reserve gates still apply. Stored passing flags alone do not establish admission.

The full Django native002 assessment passed mechanical checks with no blockers: 35 tool calls (limit40), 23,494 input tokens plus8,192 reserve =31,686 (limit32,768), 4,317 supervised targets. All64publisher/regression test identities are covered across two versions without counting skipped execution as passed. Evidence:evidence/data/djangoapikey187-matrix-admission-002. Its three-file result/descriptor/runner bundle (85,799bytes) was published to R2 and independently restored with matching hashes.

Four synthetic end-to-end tests include context-overflow preservation and denial of altered task/primary image/summary, rehashed publisher patch substitution, false snapshot verification, missing verification inputs, changed version-export probe and failed runtime observations. Full local CPU suite:610tests passed,zero skips,21.247seconds. Protocol receipt checks now explicitly distinguish grading execution from the non-grading predicate-export probe.

Mechanical admission is not training approval or independent attestation of arbitrary receipts. Complete history review, rights, privacy, frozen splits and GPU qualification remain required. Django is not yet added to Corpus056, and zero tokens are admitted to training. Runpod unused; P1 incomplete. This entry supersedes prior statements that matrix admission integration was unimplemented.

Full-suite R2 publication and independent restoration verified: four outer files / 620,648 bytes and all332inner hashes. Redundant archive staging and temporary restore copies removed after fresh comparisons. The integrated assessment binds49evidence files.


## 2026-10-12: complete Django history review and fresh attributed amendment

Reviewed all74native002 messages in12nonoverlapping sections, with per-message hashes and structural coverage verification. The review rejected history quality despite mechanical success: a pytest|grep||echo command could hide pytest failure, and an import/setup check printed an overbroad integration-test claim. Earlier warning-capture false negatives were already explicitly corrected by completion and remain honestly recorded; targeted coverage failures remain CommandError observations rather than being relabeled passes. Public source author contact and synthetic test secrets were noted without granting privacy approval.

Created an explicitly post-evaluator-exposure assistant amendment replacing only shell actions31and32: scope the import/setup message correctly and execute targeted pytest directly, disabling global coverage addopts only for that targeted invocation. The later unmodified full suite still enforces80percent coverage. Actions, paths and order are preserved; observations were generated in a fresh offline local container, not edited. The temporary source shard was hash-verified and removed after replay.

Native003:35chargedcalls,36exchanges,74messages,23,863inputtokens and4,305supervisedtargets. With8,192reserved output tokens, total32,055fits32,768. Full test command reports62passed,4warnings and96.20percent coverage; corrected targeted command reports1passed,2warnings with actual exit0. Explicit warning-capture completion reports0targetwarnings and loaded application on Django3.2.25. The original earlier false-negative diagnostic results remain followed by an explicit correction.

Complete native003 content review used exact comparisons for already inspected unchanged messages plus inspection of every changed field; per-message hashes and full section coverage bind the new history. History quality approved only as an attributed corrected trajectory; training remains false. Patch remains exactly708bytes with the same identity, image and replay profile as native002. The matrix assessment explicitly reuses already executed grading observations for that identical patch, rather than claiming a new publisher execution; all49bound provenance files are rechecked by the integrated backend. Native003mechanicalassessment passes without blockers.

Evidence:evidence/data/djangoapikey187-history-review-002 (rejected predecessor), djangoapikey187-history-review-003, djangoapikey187-matrix-admission-003 and djangoapikey187-amended-replay-evidence-003. Corpus056 unchanged; no token admission. Rights, privacy, split review and corpus integration remain pending. Runpod unused; no production code changed, so the610test full-suite result remains the latest code regression. P1 incomplete.

R2 publication and independent restoration verified:33files/677,686bytes, all hashes matched. Redundant staging and restore copies removed after fresh comparison against retained repository evidence. Earlier rejection/review evidence also published/restored:5files/23,505bytes.
