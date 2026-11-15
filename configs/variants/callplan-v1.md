## Call plan (hard limits)

The task is graded on the working tree when the budget ends, whether or not you call `submit_patch`. An unedited tree scores zero.

- Calls 1–8: locate and read. Take the exact names, messages, exception types and return values in the issue as the specification. Search for those literals with `git grep -n -F`, and combine independent searches into one `run_command`. Read only the line ranges you need.
- By call 12 you must have edited a source file. If you are unsure, make the best-supported edit now and refine it. Reading alone cannot score.
- Calls 13–24: verify with a reproduction under `/tmp` and the single most relevant existing test file (`python3 -m pytest path/to/test_file.py -k name`). Fix what they reveal.
- From call 25 on: no new exploration. Run `git status --short && git diff`, remove stray files, then call `submit_patch`.
- Apply the change everywhere the issue implies, including parallel implementations such as sync and async variants, overloads and exported names.
- Never edit tests, `conftest.py` or `pytest.ini`. Never run the full suite. Never `pip install`. Never read outside `/workspace`.
