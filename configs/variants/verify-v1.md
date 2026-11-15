## Verify before you submit

Most failed attempts submit a plausible patch that does not fix the issue. You have far more budget than a first guess needs, so spend it on evidence.

1. Locate the code named by the issue: search for its exact names, messages and exception types, and read only the line ranges you need.
2. Before editing, write a reproduction script under `/tmp` (never inside `/workspace`) that encodes the issue's expected behaviour as assertions, and run it with `python3`. It must fail on the unmodified code for the reason the issue describes. If it passes, your reproduction is wrong: fix the reproduction, not the code.
3. Make one focused edit to the source. Re-run the reproduction. If it still fails, re-read the code path the reproduction exercises and find the real cause before editing again. Do not stack speculative edits.
4. Check the edge cases the issue implies (other inputs, sync and async variants, overloads, exported names) by extending the reproduction, and fix what fails.
5. Run the single most relevant existing test file (`python3 -m pytest path/to/test_file.py -k name`). Fix any failure your change caused; ignore failures that also occur without it.
6. Call `submit_patch` only after the reproduction passes and the targeted test shows no new failure. Before submitting, run `git status --short && git diff` and remove stray files. If budget is nearly exhausted (check with `get_status`), submit your best edit rather than nothing.
7. Never edit tests, `conftest.py` or `pytest.ini`. Never run the full suite. Never `pip install`.
