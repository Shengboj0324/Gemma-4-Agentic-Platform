# v7 vs v6: trajectory mechanism of the gain and the losses (2026-11-19)

Read-only trace audit. No pods, no Kaggle, no R2 writes. The tars `runs/2026-11-19/pair-15.tar`, `pair-17.tar`, `pair-18.tar` and `screen-19.tar` were streamed one at a time (`tarfile` mode `r|`). Only `task_results.jsonl`, compacted traces (tool name, arguments, first ~2 kB of each observation, the model message) and patches were kept. The official `tasks.jsonl` was checked against sha256 `e4b3fd60…`. Reference patches were used only to label failures after the fact.

Scripts are in session scratch (not durable): `scratchpad/v7mech/` — `extract.py`, `analyze.py` (per-run features), `tables.py`, `cases.py`, `buckets.py`, `early.py`, `editfail.py`, `modes.py`, `sometimes.py`, `recover.py`, `reads.py`, `reread.py`; raw outputs in `out_*.txt`.

**Definitions used in this note**
- **Source edit:** a successful `edit_file`/`write_file` call on a path with a directory component.
- **Scratch write:** an edit or write to a root-level file (`repro.py`, `reproduce_issue.py`, …).
- **Parse-fail:** `edit_file` returned "mandatory input parameters are not present". This is the known backtick mis-termination; see `skills_and_edit_failures.md`.
- **Check:** a `python3 …` or `pytest` command run after the first source edit.
- **Re-read:** a `read_file` call where more than half of the returned lines were already returned earlier in the same run.
- Edits made through `sed -i` or a Python one-liner in `run_command` are not counted as source edits. This affects at most 2 runs (v7t03).

## Bottom line

1. **v7's gain does not come from fewer runs that never edit.** Both candidates fail to make any source edit in about 19 runs per 129: v6 59 and v7 56 over the three pairs.
   - These no-edit runs are a coin flip that cancels between the candidates. Among the 33 v7-only wins, v6 never edited in 12. Among the 19 v6-only wins, v7 never edited in 10.
   - The net comes from **runs that did edit**. v7-only wins where v6 edited: 21. v6-only wins where v7 edited: 9. That is +12 of the pooled +14.
2. **Why v7's edited runs convert better.** Per run, v7 has:
   - fewer edits to the wrong file: 6.7 vs 9.7;
   - fewer "right file, but turn cap or 8-min timeout before submit": 13.7 vs 18.7;
   - fewer 8-min timeouts overall: 5.7 vs 10.7;
   - fewer pytest runs: 0.27 vs 0.42 per run;
   - fewer scratch reproductions before the first edit: 1.14 vs 1.51;
   - smaller patches (v7-only tasks: +18.5 vs +39.7 added lines);
   - more submits (v7-only tasks: 76% vs 46%).

   The number of post-edit Python checks is unchanged: about 2.3 in both. **v7 did not check less. It stopped the edit → test → edit spiral and the reproduction-first opening** that v6's "Calls 13–24: verify with a reproduction…" invited.
3. **v7 has more "no patch at the cap" runs (13 vs 4 in pair-15), but that is cosmetic.** v6's no-edit runs leave `reproduce_issue*.py` in the tree, so the patch is non-empty but contains only scratch files: 16 such runs in pair-15 for v6, 8 for v7. Neither kind can resolve.
4. **v7's largest remaining recoverable pool is no-edit exploration on solvable tasks.**
   - Size: about 7 runs per run, an expected ~4 tasks per run if each became a normal edited run.
   - Cause: the model never counts calls. In never-edit runs there are 0 `get_status` calls and almost no mention of call numbers, so "By call 12" cannot fire.
   - An observable signal that does fire: the agent re-reads lines it has already seen. Never-edit runs average 4.7 re-reads; won runs average 1.6. In 46 of 56 v7 never-edit runs a re-read comes before any edit, at median call 19.5.
5. **Parse-fail loops** (byte-identical mangled `edit_file` calls at temperature 0) hit about 6 runs per run with 5 or more failures. They are mostly on hard tasks: about 0.5 tasks per run recoverable. 79% of mangled calls contain a backtick, against 5% of successful edits.

## Q1: mechanism of v7's gain

### Group means (3 pairs pooled; a "row" is one task in one run)

The table medians are first edit and submit call; all other columns are means. "+lines" includes scratch files.

| group | cand | n | calls | dur s | first src edit (median) | src edits | checks after edit | pytest runs | submit call (median) | submitted % | +lines | touches ref file % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v7-only | v6 | 33 | 33.6 | 305 | 20 | 1.5 | 2.1 | 0.4 | 27 | 45 | 39.7 | 53 |
| v7-only | v7 | 33 | 27.0 | 245 | 15 | 2.2 | 2.6 | 0.2 | 22 | 76 | 18.5 | 100 |
| v6-only | v6 | 19 | 31.9 | 343 | 16 | 2.6 | 3.7 | 0.8 | 30 | 58 | 25.1 | 100 |
| v6-only | v7 | 19 | 34.8 | 373 | 17 | 1.3 | 4.1 | 0.2 | 31 | 26 | 29.1 | 64 |
| both | v6 | 115 | 24.5 | 179 | 10 | 1.9 | 2.6 | 0.6 | 19 | 90 | 14.4 | 97 |
| both | v7 | 115 | 21.5 | 173 | 9 | 1.9 | 2.3 | 0.3 | 17 | 90 | 11.1 | 97 |

### How the loser of each discordant pair failed

Columns 3–8 are counts of discordant runs.

| discordant group | loser | no src edit (explore) | parse-loop, no src edit | edited wrong file(s) | right file, cap/timeout before submit | right file, wrong content (submitted) | parse-loop with some edit |
|---|---|---|---|---|---|---|---|
| v7-only (33) | v6 | 9 | 3 | 4 | 4 | 11 | 2 |
| v6-only (19) | v7 | 10 | 0 | 0 | 4 | 5 | 0 |

### Failure modes per run (means over the three pairs)

| cand | WIN | no src edit | parse-loop | edited wrong file(s) | right file, cap/timeout before submit | right file, wrong content |
|---|---|---|---|---|---|---|
| v6 | 44.7 | 17.7 | 6.0 | 9.7 | 18.7 | 32.3 |
| v7 | 49.3 | 17.7 | 5.7 | 6.7 | 13.7 | 36.0 |

### Resolution by call of the first source edit (n / resolved)

| run | cand | 1–8 | 9–12 | 13–20 | 21–30 | 31+ | never |
|---|---|---|---|---|---|---|---|
| pair-15 | v6 | 30/15 | 23/8 | 33/14 | 18/3 | 6/3 | 19/0 |
| pair-15 | v7 | 27/18 | 28/12 | 31/12 | 11/4 | 11/4 | 21/0 |
| pair-17 | v6 | 29/20 | 16/7 | 36/15 | 14/3 | 14/2 | 20/0 |
| pair-17 | v7 | 36/26 | 18/7 | 31/12 | 14/1 | 15/2 | 15/0 |
| pair-18 | v6 | 28/14 | 18/8 | 38/17 | 17/5 | 8/0 | 20/0 |
| pair-18 | v7 | 32/21 | 25/10 | 26/13 | 14/5 | 12/1 | 20/0 |
| screen-19 | v7t03 | 31/17 | 16/5 | 32/9 | 14/8 | 14/3 | 22/2 |
| screen-19 | v7c48 | 34/21 | 20/9 | 29/11 | 15/5 | 13/5 | 18/0 |

For runs with the first edit at call 12 or earlier (pooled over the pairs): v7 resolves 57% (94/166) and v6 50% (72/144). v7 submits 90% vs 81%, and hits the 8-min timeout in 1.2% vs 6.2%. v7 makes more of these early edits (166 vs 144). Late edits still score: of runs whose first edit is at call 31 or later, v7 resolves 7/38, because the grader reads the working tree.

### Examples (sequence key: s search, r read, W scratch write, p python, T pytest, E source edit, e mangled edit, S submit, x cleanup, g status)

- **fastapi_11194 (pair-15 and pair-18), multipart Form + File parsing.**
  - v6 wrote `reproduce_issue.py` at call 1, then 4 repro variants: `WpsrrpWpssrsrWpWp…`. It never edited `fastapi/dependencies/utils.py` and ended on the 40-call cap with only scratch files in the tree.
  - v7 ran 5 Python probes, read, edited at call 13 (`EE`), ran 3 checks and submitted at call 18–21 with a 1-file patch (+2/−4).
- **fastapi_9425 (pair-18), one-line fix in `dependencies/utils.py`.**
  - v6 opened with 10 scratch-write/run cycles (`WpWpWpWp…`), never edited source, and took 486 s.
  - v7 edited at call 12 (+1/−1), ran 2 checks and submitted at call 23 (127 s).
- **rich_4079 (pair-17), Markdown code-block rendering.**
  - v6 edited the wrong file (`rich/table.py`, −28 lines) at call 13, ran one pytest and submitted at call 16.
  - v7 read longer, edited the reference file `rich/markdown.py` at call 16, ran 2 checks and submitted at call 26.
- **requests_7427 (pair-15), `utils.py` helper.**
  - v6 edited at call 4, then cycled reproduce/edit/reproduce (`EpWpsrr…EpWp`) and submitted at call 23 (+13/−5, wrong).
  - v7 ran 4 probes, edited at call 7, ran one check and submitted at call 9 (+12/−7, right).
- **rich_3454 (pair-15), URL highlighter regex with a backtick in the character class.**
  - v6 sent 28 mangled `edit_file` calls in a row (`Wpeeeeeeeeeeeeee…`) and hit the 8-min cap with no source edit.
  - v7 had 2 mangled calls, then a valid one at call 7, and submitted at call 16. This one is partly luck.
- **fastapi_13207 (pair-17), `_compat/v2.py` computed fields.**
  - v6 spent all 40 calls on `srsr…` and never edited.
  - v7 edited at call 11 (+5/−2) and submitted at call 21.

## Q2: mechanism of v7's losses (v6-only, 19)

| run | task | v7 sequence | v7 failure |
|---|---|---|---|
| p15 | fastapi_14459 | `srsrsrsrrsrsrsrssrrssrsrrsrr…` (37 calls) | no edit, 8-min timeout |
| p17 | fastapi_14485 | first edit at 32, `…EprEpS` | right file, wrong content |
| p18 | fastapi_14485 | `sssrssssrsrrrrsrrr…se` | no edit (one mangled edit at 40) |
| p15 | fastapi_14873 | `srrsrrrrrrrWprrsrsrs…` 39 calls | no edit |
| p17 | fastapi_15589 | `ssrssrrsrWpWWpWWp…sssss` | no edit (repro writes, then search) |
| p15 | fastapi_15589 | first edit 19, more repro, cap | right file, no submit |
| p17 | fastapi_14512 | first edit 33 | right file, cap |
| p17 | requests_7427 | edit at 12, then 14 Python probes | right file, cap |
| p18 | rich_3063 | `srrWppWprsWpsrWpWWprrWpT…` | no edit (repro loop) |
| p17 | rich_3130 | `ssrsssrrrsrsrWpsssrWpWp…` | no edit |
| p15 / p18 | rich_3521 | `srsrrrsrrppp…ppppp` | no edit, 8-min timeout / cap (Python probe loop) |
| p18 | rich_3506 | `rsrrrppppsrsps` 14 calls, 482 s | no edit, 8-min timeout |
| p18 | rich_3777 | 39 × `s/r`, then a mangled edit | no edit |
| p15 | rich_3676 | first edit 17, mangled edits, cap | right file, partial |
| p17 / p18 | rich_3480 | first edit 27 / 14 | wrong content |
| p17 | rich_3676 | submitted, `default_styles.py` missing | partial (missing file) |
| p18 | rich_3772 | +25/−21 vs ref +29/−0, 617 s | wrong content (rewrite) |

**Pattern**
- **10 of 19 losses never make a source edit** (8 explore to the turn cap, 2 hit the 8-min timeout).
- When v7 does edit in a loss, the first edit is late: median call 17. No loss comes from an edit at or before call 12.
- **Repo:** the losses lean Rich (11 of 19, against 12 of 33 wins). The gains lean FastAPI (19 of 33 wins, against 7 of 19 losses). Net by repo: FastAPI +12, Rich +1, requests +1.
- **What never-edit runs do:**
  - repeated 40–60-line reads of the same function and its callers: 15.2 reads per run, 4.7 of them re-reads (won runs: 6.7 reads, 1.6 re-reads);
  - searches that fail with exit code 1 and are retried with another grep (fastapi_5624 p18 retried `grep` → `git grep` → `git grep fastapi/` twice);
  - in Rich, long Python probe chains (`ppppp`) that use up the 8 minutes.
  - They are not edit loops: only 3 of 56 had any mangled edit.
- Typical shape (fastapi_5624 p18): by call 17 the model has written the fix plan ("merge scopes instead of `extend`"), then reads 23 more ranges and re-greps the same symbols. Its first edit is at call 40.
- **Call counting:** `get_status` calls in never-edit runs: 0 in all 3 runs. The phrase "call N" appears in 1 of 56 never-edit runs. Count-based deadlines are not observed by the model.

## Q3: tasks v7 solves in 1 or 2 of 3 runs (24 tasks, 35 losses)

| task | v7 wins | v6 wins | pair-15 | pair-17 | pair-18 | v7t03, v7c48 |
|---|---|---|---|---|---|---|
| fastapi_13207 | 2/3 | 0/3 | WIN (fe36) | WIN (fe11) | no-edit explore | WIN, WIN |
| fastapi_14266 | 1/3 | 0/3 | no-edit explore | WIN (fe37) | no-edit explore | no-edit, WIN |
| fastapi_14419 | 2/3 | 1/3 | WIN (fe27) | wrong patch (fe11, +79) | WIN (fe11, +19) | no-edit timeout, wrong |
| fastapi_14430 | 1/3 | 0/3 | WIN (fe12, +1) | no-edit timeout | no-edit timeout | wrong, no-edit timeout |
| fastapi_14459 | 1/3 | 1/3 | no-edit timeout | edited, no submit | WIN (fe21, +2) | WIN, no-edit timeout |
| fastapi_14482 | 1/3 | 0/3 | WIN (fe12) | wrong (fe17) | wrong (fe22) | no submit, wrong |
| fastapi_14485 | 1/3 | 3/3 | WIN (fe24) | wrong (fe32) | no-edit explore | wrong, WIN |
| fastapi_14605 | 2/3 | 0/3 | WIN (fe3) | WIN (fe3) | edited, no submit (mangled loop) | no submit, WIN |
| fastapi_14616 | 2/3 | 0/3 | WIN (fe35) | no-edit explore | WIN (fe22) | no submit, parse loop |
| fastapi_14791 | 2/3 | 0/3 | wrong (fe6, 8 calls, over-spec) | WIN (fe7) | WIN (fe12) | wrong, wrong |
| fastapi_14873 | 2/3 | 3/3 | no-edit explore | WIN (fe39) | WIN (fe21) | WIN, WIN |
| fastapi_15589 | 1/3 | 2/3 | edited, no submit (+106) | no-edit explore | WIN (fe17, +2) | WIN, WIN |
| fastapi_5624 | 2/3 | 1/3 | WIN (fe17) | WIN (fe15) | no-edit explore | WIN, WIN |
| fastapi_9425 | 2/3 | 1/3 | WIN (fe21) | no-edit explore | WIN (fe19) | WIN, WIN |
| requests_7427 | 2/3 | 1/3 | WIN (fe7, 9 calls) | edited, 14 probes, no submit | WIN (fe5, 10 calls) | WIN, WIN |
| rich_3130 | 1/3 | 1/3 | WIN (fe17) | no-edit explore | edited, no submit | WIN, WIN |
| rich_3278 | 2/3 | 1/3 | wrong (fe9, regex variant) | WIN (fe7) | WIN (fe7) | wrong, wrong |
| rich_3296 | 1/3 | 0/3 | wrong (+42) | wrong (+79) | WIN (+1) | wrong, wrong |
| rich_3471 | 2/3 | 0/3 | wrong (fe13) | WIN (fe26) | WIN (fe25) | no submit, no-edit timeout |
| rich_3506 | 1/3 | 1/3 | WIN (fe9) | wrong (fe6, 9 calls) | no-edit timeout | no-edit timeout, wrong |
| rich_3521 | 1/3 | 3/3 | no-edit timeout | WIN (fe17) | no-edit explore | no-edit timeout, no submit |
| rich_3777 | 2/3 | 3/3 | WIN (fe34) | WIN (fe19) | no-edit explore | WIN, WIN |
| rich_4075 | 1/3 | 0/3 | parse loop | no-edit explore | WIN (fe18) | no submit, WIN |
| rich_4079 | 2/3 | 0/3 | no-edit explore | WIN (fe16) | WIN (fe34) | no-edit, no-edit timeout |

**Loss modes over the 35 losses**

| loss mode | count |
|---|---|
| no-edit exploration | 14 |
| wrong patch | 10 |
| no-edit timeout | 5 |
| edited, no submit | 5 |
| parse loop | 1 |

**Win runs vs loss runs**

| | runs | median first edit | calls | reads | searches | src+ lines |
|---|---|---|---|---|---|---|
| win | 37 | 17 | 28 | 10.7 | 7.2 | 15 |
| loss | 35 | none | 33 | 14.1 | 9.8 | 28 |

- **What separates them is whether an edit happens at all.** 19 of 35 losses never edit.
- The second separator is **over-specification after a fast submit**:
  - fastapi_14791 p15 added `"required": [..., "input"]` and `nullable` beyond the issue;
  - rich_3296 and rich_3506 p17 made larger rewrites;
  - rich_3278 p15 used a different regex.
- These fast wrong-patch losses are short (8–15 calls). There is no prompt lever for them that would not add instructions.

## Recoverable pools for v7 (per run, means over 3 pairs)

"P > 0 tasks" means the task was solved by at least one of the 8 runs after a source edit. "Expected" sums each task's P(resolved | source edit) over the failing runs, which is an upper bound for converting that run into an ordinary edited run.

| v7 failure mode | runs/run | of which on P > 0 tasks | expected recoverable/run |
|---|---|---|---|
| no src edit (explore to cap) | 15.0 | 5.3 | 3.6 |
| no src edit (8-min timeout) | 2.7 | 1.7 | 0.8 |
| parse loop (no edit / some edit) | 1.0 / 4.7 | 0.3 / 0.7 | 0.2 / 0.2 |
| edited, wrong or incomplete patch | 56.3 | 10.7 | 3.5 (mostly semantic; no cheap lever) |

## Q4: proposed candidates on top of v7

All three replace or remove text. None adds a new pre-edit rule. No curly braces.

### A. `v7rr`: replace the call-count deadline with a re-read trigger (primary)

- **Targets:** no-edit exploration, which is 10 of 19 v6-only losses and 19 of 35 v7 inconsistent-task losses.
- **Why:** the model does not track call numbers, but it can see in its own context that it is about to read lines it has already read. Never-edit runs re-read 4.7 times, and in 82% of them a re-read precedes any edit, at median call 19.5. That leaves about 20 calls for the edit and one check.
- **Risk:** 47 of 148 won v7 runs also re-read before their first edit (median call 12.5). For them the trigger only moves the edit earlier, inside the window where v7 already does best.
- **Estimate:** upper bound +4.4 per run. **Realistic +1 to +3 per run**, because forced edits are weaker than natural ones. The prompt gets shorter.

```diff
--- candidates/v7/prompts/system.md
+++ candidates/v7rr/prompts/system.md
@@ -45 +45 @@
-- By call 12 you must have edited a source file. If you are unsure, make the best-supported edit now and refine it. Reading alone cannot score.
+- Edit a source file by call 12. If you are about to read lines you have already read, edit instead: make the best-supported edit now and refine it. Reading alone cannot score.
```

### B. `v7trim`: delete sections 3 and 4 (pure removal)

- **What they contain:**
  - Section 3 ("Run Targeted Tests Only…") restates the call plan's "Never run the full suite" and the anti-pattern "NEVER attempt to fix … existing tests".
  - Section 4 ("Once your targeted test passes: call `submit_patch`…") conflicts with v7's own "run one check … otherwise stop testing", and pulls toward a pytest step.
- **Why remove them:** v7 gained by replacing prescriptive testing text. v7 still runs pytest 0.27 times per run. "Right file, cap or timeout before submit" is still 13.7 per run, 2.7 of them on solvable tasks.
- **Removal also takes out about 12 of the prompt's 80 backticks.** That could reduce backtick priming of mis-terminated strings, but this is a hypothesis only.
- **Estimate:** +0.5 to +1.5 per run. Weak evidence; this is mainly a cheap test of the principle that less instruction text means more editing.
- **Nothing unique is lost.** Bare-pytest bans remain in the anti-patterns and the call plan. Patch-size verification remains in the anti-patterns.

```diff
--- candidates/v7/prompts/system.md
+++ candidates/v7trim/prompts/system.md
@@ -18,13 +17,0 @@
-### 3. Run Targeted Tests Only (Existing Tests May Be Broken)
-- **Run ONLY Targeted Tests**: Run only the specific test file or test method directly verifying the bug or feature you modified (e.g. `pytest tests/test_target.py -k test_feature` or `python3 -m unittest tests.test_target`).
-- **Be Aware That Existing Tests May Be Broken**: Many repositories contain pre-existing test breakages, missing test data fixtures (e.g. `/test_data`), or environment import errors unrelated to your task.
-- **Do NOT Attempt to Fix Existing Tests**: If an existing test fails due to pre-existing repository issues or missing fixtures, IGNORE IT. Never spend turns attempting to repair pre-existing test failures, create test stubs, or alter test code.
-- **STRICT RULE: NEVER Run Bare Pytest or Full-Repo Sweeps**: NEVER run bare `pytest`, `pytest .`, `python3 -m unittest discover`, or full-repo test suites without specifying a target file. Full test suites take several minutes, cause catastrophic timeouts, and exhaust your turn and time budgets.
-- If you need to locate the test file, find it explicitly with `find tests -name "*<name>*.py"` instead of running the test runner across the repo.
-
-### 4. Immediate Patch Submission
-- Once your targeted test passes:
-  1. Call `submit_patch` immediately.
-  2. Verify `patch_size > 0` and `files_changed > 0`.
-  3. Output a short summary of the fix to end the session.
-
```

A and B touch different lines and can be stacked as `v7rr+trim` if only one screen slot is available. Screening them separately is cleaner.

### C. `v7pf`: one reactive line for mangled edits, swapped for a duplicate bullet

- **Targets:** parse-fail loops.
  - Per run, about 13 runs have at least one mangled call and about 6 have five or more.
  - Recovery after a loop is 4/18 for v7.
  - The calls are byte-identical resends at temperature 0.
  - 79% of mangled calls contain a backtick, against 5% of successful edits.
- **History:** v3's preventive rules (avoid backticks, route through Python) cut edit calls by 55%; see the campaign plan at line 487. This line only fires after the error, and it replaces a bullet whose content appears twice elsewhere (section 3 STRICT RULE, call-plan last bullet).
- **Estimate:** +0.3 to +1 per run. Most loops are on tasks nobody solves (fastapi_14583, fastapi_14964, rich_3064). It also frees roughly 5–20 turns in each looping run.
- **Ranked last.**

```diff
--- candidates/v7/prompts/system.md
+++ candidates/v7pf/prompts/system.md
@@ -33 +33 @@
-- **NEVER run full repository test suites** (e.g., bare `pytest` or `pytest .`) — always specify the exact test file path.
+- If `edit_file` answers that `old_string` is missing, do not resend the same call: retry with a shorter `old_string`, a unique fragment of the line that contains no backtick.
```

### Not recommended (already measured)

- More calls: v7c48 scored 51, +1.7 vs the v7 mean. It halves the no-edit-explore runs (7 vs 15) but adds 8-min timeouts (17 vs 5–7) and time.
- Temperature 0.3: v7t03 scored 44.
- A count-based backstop such as "from call 25…": v6 had one, and its never-edit rate is the same as v7's.
