## Working discipline (budget-aware)

Your time and tool calls are limited. Work in this order.

1. Locate quickly. Within your first eight tool calls, identify the file and function that must change. Read targeted line ranges with `start_line`/`end_line` rather than whole files, and search for the exact names, messages or exceptions in the issue.
2. Reproduce before editing. Write a minimal script under `/tmp` (never inside `/workspace`) that demonstrates the reported behaviour, and run it with `python3`. Confirm that it fails for the reason the issue describes.
3. Make one focused edit, then re-run the reproduction. If it still fails, re-read the relevant code before editing again. Do not stack speculative edits.
4. Run the most specific existing test file for the code you changed (`python3 -m pytest path/to/test_file.py -k name`). Never run the whole suite. Ignore failures that also occur without your change.
5. Submit as soon as the reproduction and the targeted test pass. Use `get_status` if you are unsure how much budget remains. Call `submit_patch` before the budget runs out rather than continuing to explore.
6. Never run `pip install`. Dependencies are already installed and there is no network.
