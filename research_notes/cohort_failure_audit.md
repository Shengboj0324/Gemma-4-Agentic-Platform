# Cohort failure audit: small/medium tasks v2 never solves (2026-11-18)

This is a read-only trace audit. It used no pods, made no Kaggle calls and wrote nothing to R2. The scripts are in `scratchpad/audit/` (session scratch, not durable): `fetch_tasks.py`, `extract.py`, `difflib2.py`, `churn.py`, `envcensus.py`, `features.py`, `aggregate.py`, `dump.py`, `testinfo.py`, `table.py`. The run tars were streamed from R2 one at a time (`tarfile` mode `r|`), keeping only `v2/task_results.jsonl` and the traces, patches, test outputs and logs of the candidate tasks. The official `tasks.jsonl` was checked against its sha256 (`e4b3fd60…`). Reference patches and tests were used **only** to classify failures after the fact.

## Bottom line

- **Cohort.** 52 tasks have v2 solves = 0 in all 10 v2 runs and reference Python source churn ≤ 40.
  - 19 are excluded because their tests cannot be collected here (missing `inline_snapshot` / `dirty_equals`).
  - 8 more are requests tasks where the grader imports the host venv's `requests`, so no workspace patch can matter (see below).
  - 4 have a reference patch that fails in our local gold receipt.
  - That leaves a **21-task diagnostic cohort**. The owner's 17 came from the LocBench census over FastAPI and Rich only; the definitions differ (see caveats).
  - Only 6 of the 21 have a local gold-pass receipt (strict version, below).
- **Primary class counts (21 tasks):**

  | class | count | tasks |
  |---|---:|---|
  | (a) wrong code path / file | 3 | fastapi_13920, rich_3935, rich_4076 |
  | (b) right place, wrong behaviour | 3 | fastapi_14986, rich_3052, rich_3471 |
  | (c) partial propagation | 1 | rich_3934 |
  | (d) missing new file / export | 0 | – |
  | (e) no edit / budget exhaustion | 1 | rich_3472 |
  | (f) grading artefact: environment | 5 | requests_6644, rich_3064, rich_3130, rich_3469, rich_4079 |
  | (f) grading artefact: hidden test pins content the issue does not state or contradicts | 8 | fastapi_14258, fastapi_14479, fastapi_14487, fastapi_15588, rich_3105, rich_3535, rich_3944, rich_3953 |
  | (g) unknown | 0 | – |

- **13 of 21 cannot be recovered by any agent policy in our local instrument.**
  - The 5 environment artefacts include **near-solves hidden by the environment**:
    - rich_3130: 8 of 10 v2 patches pass both new regression tests and fail only `test_markdown_render` / `test_inline_code`, whose expected syntax colours differ from what our Pygments emits.
    - rich_4079: 3 of 10 patches are equivalent to the reference and fail only on the colour of the `print` token.
  - The 8 "spec" artefacts include tasks where the issue text and the test disagree.
    - fastapi_14479: the issue prints `Query param 'data' must be of one of the supported types`. v2 copied that exactly in 10 of 10 runs, but the test requires `Query parameter 'q' must be one of the supported types`.
    - fastapi_15588: the validation behaviour is correct in 10 of 10 runs; only the exception text differs.
- **Only 8 tasks are attributable to agent behaviour.** The common pattern in 7 of them: the agent's post-edit check exercised **its own hypothesis** (a helper predicate, a hand-built object, a narrow `-k` test), and that check looked green while the patch was wrong. In none of these 8 tasks did the agent run the issue's scenario through the public entry point with an explicit expected value.

## New instrument findings (affect every local score, not only this cohort)

1. **requests tasks are graded against the host venv, not the workspace.** Every requests test traceback goes through `/root/venv/lib/python3.12/site-packages/requests/…`. With a `src/` layout and only `PYTHONPATH=/workspace`, `import requests` resolves to the installed wheel.
   - In requests_6644, two runs edited `RequestEncodingMixin.path_url`, which should have changed `HTTPAdapter.request_url`, yet the grader still returned `'//v:h'`.
   - Agents see the same thing live: `python3 repro.py` printed the unpatched result, and only `PYTHONPATH=src python3 repro.py` showed the patch.
   - This also explains the receipt: requests_7309 and requests_7315 "pass" with an empty patch, and requests_7205, requests_7433 and requests_7505 fail with the gold patch.
   - Most requests tests also fail on the `httpbin` fixture (recursive dependency).
   - All 13 requests tasks are uninformative locally.
2. **Rich markdown tests fail on Pygments colour drift.** `tests/test_markdown.py::test_markdown_render` and `::test_inline_code` fail in 10/10 runs of rich_3064 and rich_3130 and in 4/4 graded runs of rich_3469, whatever the patch, with colour-only diffs (e.g. `38;2;0;0;0` vs `38;2;187;187;187`). rich_4079's later checkout fails the same way on the `print` token (`166;226;46` vs `248;248;242`). Any rich task graded on that file is unsolvable here.
3. Both artefacts mean local scores **undercount** v2. The host states that hidden tasks validate at 100 %, so these are measurement losses, not hidden-set losses. Fix them before using this cohort as a gate. Pin Pygments to the version the expected strings were generated with, and make `src/` packages importable from the workspace in the subprocess sandbox. The round-14 plan to add `inline_snapshot`/`dirty_equals`/`typing_inspection` addresses only the first exclusion group.

## Cohort construction

- **Solve counts:** all 10 v2 runs (lora-eval-1, budget-eval-1, lora-eval-2b, lora-eval-4, lora-eval-6, lora-eval-7b, lora-eval-8, lora-eval-10a, lora-eval-10b, timing-l4-1). All 52 candidates are 0/10, consistent with the 8-run JSON in `gate_calibration.md`.
- **Reference churn:** added + deleted lines in the reference `patch`, over `.py` files not under `tests/`/`testing/`, not `test_*.py`/`*_test.py`/`conftest.py`, and not under `docs_src/` or `docs/`. New files are included, and `scripts/` counts as source. `docs_src` churn is recorded separately. fastapi_14487 changes only `docs_src/` (7 lines) and is kept with churn 0.
- **Owner's bucket comparison:** on all 129 tasks this gives ≤ 10: 62 tasks / 29 never solved; 11–40: 32 / 23; > 40: 35 / 34. The owner's 41/14/16 are restricted to the 71 LocBench-valid tasks.
- **Gold census:** no 129-task local gold census exists. The only local receipt is `evidence/p1/held-out-eval-001/verifier-qualification/receipt.json` (49 tasks; gold 29/49, empty 2/49). For the rest, the per-run `test_outputs/` were scanned for `No module named …` and `fixture 'httpbin'`.

Two versions are reported.

- **Primary, 21 tasks:** not environment-blocked and not a known local gold failure. These are the tasks in the main table.
- **Strict, 6 tasks:** local gold pass confirmed by the receipt. fastapi_14258 (f-spec), fastapi_14986 (b), rich_3052 (b), rich_3535 (f-spec), rich_3935 (a), rich_3944 (f-spec). Agent-attributable: 3 of 6.
- **Excluded, 31 tasks:**
  - **Missing modules (19).** inline_snapshot: fastapi_11355, 13207, 14246, 14266, 14297, 14349, 14361, 14430, 14455, 14482, 14485, 14583, 15023. dirty_equals: fastapi_12942, 13713, 14303, 14356, 14360. Both: fastapi_14791.
  - **requests, host-venv import and `httpbin` fixture (8):** requests_6589, 6592, 6629, 6757, 7328, 7433, 7502, 7505.
  - **Local gold fails (4):** fastapi_15763, requests_7205, rich_3296, rich_3782.
  - **requests_6644** is kept in the primary cohort only because it is not in the receipt. It is classified (f) for the same host-venv reason.

## Per-task trace metrics (10 v2 runs each)

Column definitions:
- **files vs ref:** compares the package `.py` files in the final patch with the reference source files.
- **first src edit:** the 1-based tool-call index of the first successful `edit_file`/`write_file`, or modifying shell command, on a package path.
- **check after edit:** any `python`/`pytest` command after that call.
- **last check looked green:** a heuristic. The final post-edit command exited 0 with no `Traceback`/`FAILED`/`AssertionError`/`failed` in its tail. Where the fix *is* an error message, a red check can be the intended output.
- **test_exit_code −1:** no patch was produced.

| task | src edit (runs) | files vs ref: all/some/none/no-edit | first src edit (median call) | check after edit (runs) / pytest after | last check looked green | end: submit/turns/timeout | test_exit_code |
|---|---|---|---|---|---|---|---|
| fastapi_13920 | 10/10 | 0/0/10/0 | 9 | 9 / 0 | 8/9 | 8/0/2 | 1:10 |
| fastapi_14258 | 9/10 | 9/0/0/1 | 10 | 9 / 0 | 4/9 | 3/5/2 | 1:10 |
| fastapi_14479 | 10/10 | 10/0/0/0 | 6 | 10 / 1 | 0/10 | 10/0/0 | 1:10 |
| fastapi_14487 | 10/10 | 4/0/6/0 | 14 | 0 / 0 | 0/0 | 9/1/0 | 1:10 |
| fastapi_14986 | 10/10 | 10/0/0/0 | 13.5 | 6 / 1 | 5/6 | 6/3/1 | 1:9, 2:1 |
| fastapi_15588 | 10/10 | 10/0/0/0 | 4 | 10 / 7 | 10/10 | 10/0/0 | 1:10 |
| requests_6644 | 9/10 | 0/0/9/1 | 10 | 9 / 0 | 9/9 | 8/2/0 | 1:10 |
| rich_3052 | 10/10 | 10/0/0/0 | 3 | 10 / 9 | 10/10 | 10/0/0 | 1:10 |
| rich_3064 | 9/10 | 9/0/0/1 | 20 | 9 / 6 | 7/9 | 5/5/0 | 1:10 |
| rich_3105 | 1/10 | 0/0/1/9 | 38 | 1 / 1 | 0/1 | 2/6/2 | −1:5, 1:5 |
| rich_3130 | 10/10 | 10/0/0/0 | 15 | 10 / 7 | 6/10 | 4/5/1 | 1:10 |
| rich_3469 | 3/10 | 0/0/3/7 | 35 | 2 / 0 | 2/2 | 0/7/3 | −1:6, 1:4 |
| rich_3471 | 5/10 | 5/0/0/5 | 24 | 5 / 0 | 5/5 | 5/0/5 | −1:1, 1:9 |
| rich_3472 | 3/10 | 0/0/3/7 | 29 | 2 / 1 | 2/2 | 1/9/0 | −1:6, 1:4 |
| rich_3535 | 10/10 | 0/10/0/0 | 13.5 | 10 / 5 | 10/10 | 10/0/0 | 1:10 |
| rich_3934 | 6/10 | 0/6/0/4 | 20.5 | 6 / 1 | 6/6 | 3/2/5 | 1:10 |
| rich_3935 | 9/10 | 0/0/9/1 | 22 | 8 / 1 | 6/8 | 2/7/1 | 1:10 |
| rich_3944 | 9/10 | 0/0/9/1 | 13 | 6 / 5 | 3/6 | 7/1/2 | −1:1, 1:9 |
| rich_3953 | 10/10 | 10/0/0/0 | 15.5 | 10 / 7 | 7/10 | 8/1/1 | 1:10 |
| rich_4076 | 6/10 | 0/0/6/4 | 33.5 | 5 / 1 | 4/5 | 1/8/1 | −1:2, 1:8 |
| rich_4079 | 4/10 | 3/0/1/6 | 34 | 2 / 0 | 2/2 | 1/8/1 | −1:3, 1:7 |

## Per-task classification

**Issue text** says what the agent was given:
- **full:** a description with an example.
- **title:** a one-line title plus "Fixes <link>". The linked issue body is not in `problem_statement`.
- **none:** no behavioural content.

**Cheapest observation** is something the live agent could have run from the issue and the repository alone.

| task | issue text | primary class | what v2 did vs the reference (2–3 diffs read) | cheapest observation that would have exposed the wrong patch |
|---|---|---|---|---|
| fastapi_13920 | full (PEP 695 `TypeAliasType`) | **(a)** | 10/10 added `is_typealiastype`/unwrap helpers to `fastapi/_compat/shared.py` predicates. The reference unwraps in `analyze_param` (`dependencies/utils.py`) so that `Annotated[…, Depends()]` inside an alias is seen. The helpers also test `typing.TypeAliasType`, while the test uses `typing_extensions.TypeAliasType`. Agent checks exercised the helper predicates ("All tests passed!"). | An endpoint with `value: TypeAliasType("A", Annotated[int, Depends(f)], type_params=())` called through `TestClient(app).get("/")` gives **422** instead of 200. |
| fastapi_14258 | full, but no message or exception type stated | **(f-spec)** | 9/10 added `if router is self: raise FastAPIError(...)` in `include_router` (right place). The test requires `AssertionError` matching an exact sentence. | None for the message. Neighbouring code in `include_router` uses `assert …, "msg"`, which hints at the type only. |
| fastapi_14479 | full, and gives a message | **(f-spec)**, issue contradicts test | 10/10 changed the right assert to the message *printed in the issue* (`Query param 'data' must be of one of…`). The test expects `Query parameter 'q' must be one of…`. | None: the agent did exactly what the issue showed. |
| fastapi_14487 | title (docs) | **(f-spec)** | 6/10 edited `custom_request_and_route/tutorial002*` (drop body), and 4/10 also `handling_errors/tutorial004.py`, with a different text. The test pins `"Validation errors:"` and `"Field: ('path', 'item_id')"`. | None for the format. |
| fastapi_14986 | full but vague | **(b)** | 10/10 touched both reference files. Most removed root_path insertion entirely, and escaping was partial (`'{url}'`→`json.dumps`, or `html.escape`). The tests need root_path to still appear per request without persisting, and `<`→`<` in Swagger parameters. | `TestClient(app, root_path="/api/v1").get("/openapi.json").json().get("servers")` before and after: the patch drops `{"url": "/api/v1"}` (existing behaviour the issue keeps). `"<" in get_swagger_ui_html(..., init_oauth={"appName": "</script>"}).body.decode()` shows unescaped parameters. |
| fastapi_15588 | full | **(f-spec)** | Behaviour correct 10/10: `AfterValidator` rejects `\n`/`\r` on `event`/`id`, and 7/10 ran `tests/test_sse.py` green. The only failure is the message: "SSE field must not contain newlines" vs "SSE 'event' must be a single line". | None (message unstated). The existing `"SSE 'id' must not contain null characters"` pattern hints at the prefix only. |
| requests_6644 | full | **(f-env)**; agent-side (a) | 9/10 trimmed `//` in `PreparedRequest.prepare_url`/`path_url` (`models.py`); the reference trims in `HTTPAdapter.request_url`. The grader imports `/root/venv/.../requests`, so even the `path_url` variants returned `//v:h`. | Agent side: `HTTPAdapter().request_url(Request("GET","http://h//v:h").prepare(), {})` with `PYTHONPATH=src`. Grading here cannot see any patch. |
| rich_3052 | full | **(b)** | 10/10 threaded `case_sensitive` through `PromptBase`/`ask` (right file) and accepted `FoO`, but returned the raw input. The test expects the canonical choice `"foo"`. Checks: repro "passed", `tests/test_prompt.py` 6 passed. | `Prompt.ask("x", choices=["foo"], case_sensitive=False, stream=io.StringIO("FoO\n"))` returns `'FoO'`. Seeing that this is wrong needs the inference "return the matching choice". |
| rich_3064 | title | **(f-env)**; agent-side (b) | 9/10 edited `TableElement.__rich_console__` (right function) but added column `justify` instead of tolerating a missing header/body. `test_partial_table` fails 10/10. `test_markdown_render`/`test_inline_code` fail 10/10 on Pygments colours. | `Markdown("| Simple | Table |\n| ------ | ----- ")` rendered raises `AssertionError` (the issue title "markdown table" plus a header-only table). The environment blocks the pass anyway. |
| rich_3105 | none ("Fix #3104") | **(f-spec)**; agent-side (e) | 9/10 made no source edit (turns/timeout). One run edited `markdown.py`. The reference adds `style="font-family:inherit"` to the HTML export `<code>`. | None. |
| rich_3130 | full | **(f-env)**, near-solve | 10/10 rewrote `TableDataElement.on_text` to append rather than replace, essentially the reference. **8/10 pass both new tests**; every run fails `test_markdown_render` + `test_inline_code` on Pygments colours. | – (already correct). |
| rich_3469 | title | **(f-env)**; agent-side (e)/(a) | 7/10 no edit (40 turns). 3/10 edited `rich/rule.py`. The reference skips the newline before inline elements in `markdown.py`. `test_inline_code` fails on Pygments in every graded run. | `len(render(Markdown(table_with_empty_cells)).splitlines())` vs the full table: 9 vs 7. Agents never formed this hypothesis. |
| rich_3471 | title ("exception in append_tokens") | **(b)** | 5/10 edited `Text.append_tokens` (right function) with `try/finally` or a `None` guard. The reference applies `strip_control_codes` as `Text()`/`append()` do. 5/10 timed out with no edit. Checks printed lengths and looked green. | `git grep -n strip_control_codes rich/text.py` shows `__init__`/`append` sanitise and `append_tokens` does not. Or `Console().print(Text().append_tokens([("…code \r\n","red")]), width=40)` raises `IndexError`. |
| rich_3472 | title ("missing field in dataclass") | **(e)** | 7/10 used all 40 turns reading rich's *own* `@dataclass`es (console.py, table.py, traceback.py) and never ran a repro. 3 edits to `table.py`/`console.py` were unrelated. The reference adds `hasattr(obj, field.name)` in `pretty.py`. | A 3-line repro: `@dataclass class B: x: int = field(init=False)`, then `rich.print(B())` gives an `AttributeError` traceback ending in `rich/pretty.py`. |
| rich_3535 | full ("regex for single-width fast path") | **(f-spec)**; agent-side (b) | 10/10 fixed the visible `o`→`~` typo. All missed the second typo (` ˿` lacks `-`). The test also requires box-drawing `─-◿`, which the issue never mentions, and fails first on `'┌'`. | For the second typo: `_is_single_cell_widths("é")` is `None`. The box range cannot be found. |
| rich_3934 | title ("empty live") | **(c)** | 6/10 edited `LiveRender.position_cursor`/`restore_cursor` for height 0 (one of the two reference files). All missed `Live.stop()` in `live.py`, which still calls `console.line()`. The agent's own repro output still ended `…\n\x1b[?25h`, and the agent did not assert on it. | Capture `with Live(Group(), console=Console(file=io.StringIO(), force_terminal=True), transient=True): pass` and check `"\n" not in output`. |
| rich_3935 | title ("padding width") | **(a)** | 9/10 rewrote `rich/padding.py` (`Padding` renderable, None-width guards). The reference fixes `Table._get_padding_width` (`collapse_padding`/`pad_edge`). | `git grep -n padding_width` points only to `table.py:_get_padding_width`. `Table.grid(padding=(0,1))` with three `width=3` columns prints `'aaa  aaa aaa '`. |
| rich_3944 | none ("fix fonts") | **(f-spec)**; agent-side (a) | 9/10 edited SVG export font-family, `box.py` substitutions or unicode tables. The reference makes code points beyond the width table width 1 (nerd-font glyphs). | Unknown. The title does not name a behaviour. |
| rich_3953 | title ("Fix ZWJ and edge cases") | **(f-spec)**; agent-side (b) | 10/10 edited ZWJ handling in `_cell_len` (right place). 2/10 (7b, 8) fix all ZWJ cases. Every run fails `test_non_printable` (control characters width 0, unstated). 5/10 also broke `test_split_graphemes`/`test_split_text`; those runs checked only `-k test_cell_len`. | `pytest tests/test_cells.py` (whole file) after the edit would have exposed the regressions in 5/10 runs. Non-printable width is unstated. |
| rich_4076 | title ("preserve newlines") | **(a)** | 6/10 edited `Text.rstrip`/`_re_whitespace` or `markdown.CodeBlock`. The reference replaces `splitlines()` in `AnsiDecoder.decode`. 8/10 ended on the 40-turn budget. | Weak: `git grep -n "splitlines()" rich/` lists `ansi.py` among candidates. `Text.from_ansi("Hello\n").plain == "Hello"` once the agent hypothesises the decoder. |
| rich_4079 | title ("Inline table code") | **(f-env)**, near-solve | 3/10 (lora-eval-4, lora-eval-10a, timing-l4-1) have `TableDataElement.on_text` equivalent to the reference and fail only on the `print` token colour (Pygments). 6/10 made no edit (turn budget). | – (correct patches already present). |

Classification rule:
- **(f)** when a patch that is correct by the issue text could not pass the hidden test **in our environment**. This covers environment failures, and tests pinning an unstated or contradicted literal, format or extra behaviour.
- Otherwise, the agent-side class is taken from the diff comparison and the trace.
- Where both apply, the agent-side class is shown after a semicolon.

## What a policy change would need to recover ≥ 5 of these 21

- Only 8 tasks are policy-recoverable in this instrument: (a) 3, (b) 3, (c) 1, (e) 1. Recovering ≥ 5 means fixing 5 of those 8 (≥ 62 %). No single prompt rule is likely to reach that. Even a perfect agent-side fix cannot move the other 13 without fixing the environment.
- **Most promising lever: an issue-observable check at the public entry point, run before and after the edit.** Before the first source edit, write a ≤ 10-line repro through the public API (`TestClient`, `Console(file=StringIO)` capture, `Prompt.ask(stream=…)`, `rich.print`). Make it print the specific observable the issue names, with an explicit expected value. After the edit, rerun the same script plus the touched module's whole test file. Continue only if the observable changed and nothing that passed before now fails.
  - In 7 of the 8 recoverable tasks the actual check tested the agent's own helper or hand-built object and looked green (13920, 3052, 3471, 3934, 3935, 4076, 14986). In rich_3472 the agent never wrote a check at all.
  - Plausible recoveries:
    - Likely: fastapi_13920 (422 vs 200), rich_3934 (`\n` in captured output), rich_3472 (the repro localises `pretty.py`), fastapi_14986 (root_path disappears).
    - Possible: rich_3471 and rich_3052 (need the right trigger or the right expectation).
    - Needs localisation, not checking: rich_3935 and rich_4076. Grep the title's noun phrase as an identifier, e.g. `padding_width`.
  - A realistic yield is 3–6 of 8, so ≥ 5 is possible but not expected.
- **Cheaper, larger and certain local gain: fix the instrument.** Pin Pygments to the test-generation version and make `src/` packages importable in the subprocess sandbox. That turns rich_3130 (8/10 runs already correct) and rich_4079 (3/10) into solves and makes the 13 requests tasks and the rich markdown tasks measurable. It does not change the hidden score; it stops the local gate from discarding real solves.
- (d) did not occur in this cohort, and (c) once. The "second, cross-file" experiment in the owner's §5 has almost no support in the small/medium cohort; its evidence would have to come from the > 40-line tasks.

## Caveats

- One reader classified the tasks, from 2–3 diffs per task plus test outputs, without re-running grading. Borderline calls:
  - rich_3535 and rich_3953 are (f-spec) because the hidden test needs behaviour beyond the issue text. Both have agent-side (b) defects too.
  - fastapi_14986 is (b) although its escape format is pinned (`<`). That is the common Flask/Jinja `tojson` form, so it is treated as guessable.
- The Pygments attribution is inferred from colour-only diffs on unchanged tests. The version was not checked against the expected strings.
- The requests host-venv attribution is inferred from traceback paths in the test outputs and the agents' `PYTHONPATH=src` observations.
- The 49-task receipt is the only local gold evidence. fastapi_13920's reference imports `typing_inspection`. Its local gold status is unverified; it is likely available, because pydantic 2.14 depends on it.
- The rich problem statements usually omit the linked GitHub issue body. "title"/"none" issue-text grades reflect what the agent saw, not the real issue.
- This cohort was selected after seeing outcomes. Use it for diagnosis only. Any policy change still needs the paired full-task gate on fresh repositories.
- The 21 differs from the owner's 17 for four reasons:
  - a different census (LocBench October harness vs our test outputs and receipt);
  - their restriction to FastAPI and Rich;
  - `docs_src` handling;
  - a different source-file definition for churn.
