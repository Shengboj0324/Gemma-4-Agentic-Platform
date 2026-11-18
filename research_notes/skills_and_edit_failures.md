# Skills, callbacks and edit-call failures in the official harness (2026-11-18)

Read-only investigation. Sources:
- Wheels from `evidence/p1/official-wheelhouse-ingest-001/manifest.json`, read from R2 with ranged reads: swegemma 0.2.11, adk_submission 0.2.13, adk_eval_core 0.1.0, google_adk 1.36.1, and `vllm/tool_parsers/gemma4_tool_parser.py` from vllm 0.19.1 (sha256 `682b2152…`, the same file as T759580).
- v2 traces from `runs/2026-11-18/lora-eval-8.tar`: 129 traces plus `task_results.jsonl` (34 resolved). v4 traces from the same tar were used for one comparison.
- Line numbers below are in the wheel files.

## 1. How skills work in this harness

**Declaration.** `agent.yaml` takes `skills: [skills/<name>]`, a list of relative directory paths (`adk_submission/schema.py` 288–299; traversal check 306–323).
- swegemma calls `compile_submission` without a `skill_registry` (`swegemma/harness/agent_runner.py` 616–628). Each path is therefore loaded straight from the bundle with `google.adk.skills.load_skill_from_dir` (`adk_submission/resolvers/tools.py` 184–221).

**Layout.** Each skill is `skills/<name>/SKILL.md` plus optional `references/`, `assets/` and `scripts/`.
- `SKILL.md` must start with YAML frontmatter containing `name` and `description` (`google/adk/skills/_utils.py` 68–96).
- `name` must equal the directory name (`_utils.py` 157). It must be kebab-case or snake_case, at most 64 characters (`skills/models.py` ~81–98).
- Scripts must be `.py`. ADK can also run `.sh`/`.bash`, but the submission validator rejects any extension outside {.yaml, .yml, .md, .txt, .py, .json, .safetensors} (`swegemma/config.py` 20–30; `adk_submission/discovery.py` 122–127).
- Limits: 50 MiB per skill directory and 1,000 skills (`swegemma/config.py` 47, 54). ADK warns above 16 MB of bundled resources (`tools/skill_toolset.py` 53).

**What the model sees.** Declaring any skill appends one `SkillToolset` to the agent's tools (`adk_submission/builders/llm.py` 67–69).
- It adds four tools: `list_skills`, `load_skill`, `load_skill_resource`, `run_skill_script` (`skill_toolset.py` 938–943).
- It appends a fixed 1,333-character instruction to every request: "If a skill seems relevant … you MUST use the `load_skill` tool … follow them exactly" (`skill_toolset.py` 61–88; injected in `process_llm_request`, 1062–1082).
- Because `ListSkillsTool` is present, the skill list is not put into the instruction. The model has to call `list_skills` or `load_skill`, which costs at least one extra turn.
- So a skill is a prompt addition by construction, which is the kind of change that has hurt in v3 and v4.

**How a script runs.** The call is `run_skill_script(skill_name, file_path, args?, short_options?, positional_args?)`.
- `args` is declared `anyOf: [object, array of strings]` and `positional_args` is an array (`skill_toolset.py` 724–773).
- The tool builds a self-extracting Python wrapper (`skill_toolset.py` 571–711):
  - it writes every skill file into a `tempfile.TemporaryDirectory()` and does `os.chdir(td)` (634);
  - it sets `sys.argv` (a list arg is passed verbatim; a dict becomes `--key value`);
  - it calls `runpy.run_path(...)`.
- That wrapper goes to the harness `AdkSandboxCodeExecutor` (`adk_eval_core/sandbox/base.py` 164–223):
  - it first calls `budget_check_fn` (= `context.check_budget`), so each script run **counts one tool call** (`swegemma/context.py` 468–551);
  - it writes `/workspace/.adk_exec_<hex>.py`, runs `python3` on it **inside the task sandbox container**, then `rm -f`s it;
  - the timeout is `command_timeout_seconds` (120 s for v2), cut down to the remaining 8-minute budget (`agent_runner.py` 604–615).
- The script's working directory is the temp dir, not /workspace, so it must use absolute `/workspace/...` paths. Its stdout is returned untruncated, up to the sandbox's 10 MB cap.

**Errors that lose the patch.**
- The old loss of the whole task's patch on a list `file_path` (33/960 runs, T745028) is **handled in 0.2.11**:
  - `ToolErrorPlugin.before_tool_callback` and a wrapper on every skill tool reduce a one-element list to a string, and return `INVALID_ARGUMENTS` for any other non-string;
  - any exception becomes an error dict (`agent_runner.py` 61, 97–129, 132–190, 244–282, 629).
- Generic exceptions inside the agent loop now fall through to the fallback `git diff` capture (`agent_runner.py` 1039–1086).
- The remaining loss modes are:
  1. **A vLLM parser hang on array arguments** (`gemma4_tool_parser.py` `_parse_gemma4_array`, bare-value branch 271–278). If an element is a bare, non-delimited string that contains `[...]`, then `]` is never consumed and the loop never advances (T759580's `args:["Fix list[str] handling"]`). It stalls the server, which means a 12-hour fail-all. `run_skill_script` invites exactly this through `args`-as-list and `positional_args`.
  2. A script that runs git operations (stash/checkout/reset) or rewrites the baseline.
  3. After a `submit_patch`, the harness keeps only the submitted patch; later edits are lost unless resubmitted (1048, 1054).

**Examples.**
- The google_adk wheel ships one skill, `tools/bigquery/skills/bigquery-ai-ml/SKILL.md`, with references only and no scripts.
- The repo has `candidates/p1-observation-memory/skills/source-observations/` (SKILL.md + `scripts/observe.py`). It is a valid layout, but its SKILL.md tells the model to pass **list** arguments, which is the parser-hang pattern. No run of it is recorded.

## 2. Callbacks

**Callbacks cannot be used.**
- The schema accepts `before/after_agent_callbacks` on every agent and `before/after_model/tool_callbacks` on LlmAgents (`schema.py` 252–254, 296–299).
- `compile_submission(callback_registry=None)` is the default (`compiler.py` 63, passed at 193).
- swegemma's call does not pass a registry (`agent_runner.py` 616–628). `validate_directory` passes `callback_registry=None` too (`discovery.py` 719).
- `resolve_callback_fields` returns `{}` when the registry is None (`resolvers/callbacks.py` 84–85).
- No `CallbackRegistry().register` call exists in swegemma, adk_eval_core or adk_submission. The only one is a docstring example in `adk_submission/__init__.py` 24.
- So callback names in YAML are **silently ignored**: they cause no error and have no effect. The harness's own `ToolErrorPlugin`, `ModelRetryPlugin` and display plugin are App plugins (`agent_runner.py` 690) and cannot be extended from the bundle.

## 3. v2 edit_file / write_file failures (lora-eval-8, 129 tasks)

| category | calls | tasks |
|---|---|---|
| all edit/write calls | 762 (399 edit, 363 write) | |
| failed | **196 (25.7%)**; 189 excluding BudgetExceeded | **97/129 (75%)** with ≥ 1 |
| write_file "Path traversal" (all `/tmp/...`) | 85 (43% of failures) | 80 |
| "mandatory input parameters are not present" | 64 (47 edit: old_string missing; 17 write: filepath missing) | 14 |
| edit "old_string not found" | 31 (11 contain escaped `\n` or `\"`) | 22 |
| edit "occurs N times" | 7 | |
| BudgetExceeded (the cap itself) | 7 | |
| edit "old == new" | 2 | |

**Mechanism of the "mandatory" failures (correcting "the parser drops arguments after a backtick").**
- The parser does what the format says. The **model ends a string argument with a backtick (56/64) or a plain `"` (8/64) instead of the `<|"|>` delimiter token**. Example from fastapi_5624: ``…scopes)`,old_string:<|"|>…``.
- The value then runs on to the next `<|"|>`. It swallows `,old_string:`, the remaining code becomes junk keys (e.g. `'r\"(?P<url>(file|https|http|ws|wss)'`), and ADK's FunctionTool returns the missing-parameter error (`google/adk/tools/function_tool.py` 179–189). That error does not count a tool call but does use a turn.
- The model emits keys **alphabetically**: edit as `filepath, new_string, old_string` in 352/353 calls, write as `content, filepath` in 345/346. So the long code string is never the last key, and a mis-termination always loses the key after it.
- The trigger is a backtick inside the string. Among successful edits, 20 had a backtick in `new_string` and 332 did not. All 64 mangled calls had one by termination.
- Junk keys could in principle reach the array hang above (code containing `:[` …). That risk already exists in v2, and no hang appeared in 8 × 129 v2 runs.

**Resends.**
- 47 failed calls were byte-identical to an earlier failed call in the same task (46 of them back-to-back). **45 of the 47 are mangled calls**, so only 19 distinct mangled calls exist. The resends sit in 11 tasks: rich_3882 13, fastapi_9753 7, fastapi_14430 6, fastapi_14873 6, …
- Five failing calls were sent 6 or more times. v2 runs at **temperature 0.0**, so a resend after an identical error is close to deterministic.
- In v4's run, fastapi_5624 sent 22 identical mangled calls and ended on the 40-turn cap with 18 tool calls and no patch.

**Resolved vs failed tasks: failed tasks do not have more edit failures.**
- Resolved: 25/34 tasks with ≥ 1 failure (74%), 2.09 failures per task, 38% of their calls failed.
- Unresolved: 72/95 (76%), 1.32 per task, 22%.
- The mangled failures fall mostly in *resolved* tasks: 43 of 64 calls, 7 of 14 tasks.
- Only "old_string not found" goes with failure: 22 tasks, 1 resolved. That is probably a marker of struggling, not a cause.

**Budget.**
- 50/95 unresolved runs end on a budget: 36 on the 40-turn cap, 14 on the 8-minute cap.
- The turn-capped runs had already used 35–39 tool calls (median 39), and only 5 of their turns were mangled calls. **Edit failures are not what exhausts the budget**; exploration is.
- All failed edit/write turns: 196, about 3,400 s at concurrency 3.

**Path traversal is self-inflicted.**
- The cause is v2's line "verify with a reproduction under `/tmp`".
- 77 of the 85 refusals are followed by a `write_file` of the same script to the workspace root. 256 of the 260 successful writes are root-level scratch scripts, and 3 are source files.
- Cost: 85 turns, about 1,800 s (about 5% of the run's 35,854 s) and 63k completion tokens, because the script is generated twice.
- 25 tasks submitted twice. In 23 of them the file count dropped, i.e. scratch files were removed and the patch resubmitted.

**v4 check.**
- v4's edit_file count is **409 vs v2's 399**. Its "fewer edit/write calls" (427 vs 762) is almost entirely write_file moving into `run_command` heredocs (461 heredocs vs 18).
- So the instruction did **not** reduce editing.
- 13 of its 15 budget-exhausted runs without a patch made no successful edit at all, which points to exploration-bound runs.

## 4. Proposed changes (no added prompt text)

**P1 (recommended): delete the words "with a reproduction under `/tmp`"**
- What: v2's `prompts/system.md`, the "Calls 13–24" line. Result: "verify with a reproduction and the single most relevant existing test file (…)".
- Files: new `candidates/v5/` = v2 bytes, with that one deletion in `prompts/system.md`. `agent.yaml`, `configs/sampling.yaml` and `eval_config.yaml` stay identical. v2's files are re-derivable from the Kaggle output / v2 tgz `1bed0fb7…`.
- Why: it removes about 85 failed turns, about 5% of task time and 63k tokens without adding a rule. The model already ends in that state (repro in the workspace root) 77 of 85 times. Unlike v4, there are no heredocs.
- Risks:
  - This model is sensitive to prompt changes.
  - Scratch files in the patch: this is unchanged from today, they are kept, and they are harmless to the tests.
  - Fewer reproductions written.
  - There is no patch-loss path.
  - Time goes down, which helps the 12-hour margin.
- Test: a paired lora-eval run, v2 vs v5, 129 tasks, concurrency 3, with the round-9 non-inferiority rule. Mechanism check: path traversal ≤ 10. Readouts: time ratio, multi-submit count, budget-no-patch.

**P2: sampling, already running in round 10 (t03/t10)**
- Add readouts there: mangled calls (v2 baseline 64), identical resends (45), and the maximum repeat in one task (13).
- A nonzero temperature should break the deterministic resend loops, which are 70% of the mangled turns. No new files.

**P3 (only if P1 passes): also drop `write_file`**
- Change: remove it from `agent.yaml` `tools`, and delete "or `write_file`" from the system.md line that names it.
- This removes the 17 write mangles, since `content` sorts before `filepath`. Scratch writes would move to `run_command`, where code is the only and last string, so a mis-termination degrades instead of dropping a key.
- Risks:
  - It is v4's route, and v4 had budget-no-patch 15 vs 8.
  - New source files then need a heredoc.
  - Calls to the undeclared tool return a ToolErrorPlugin error, which costs a turn.

**Rejected, with reasons.**
- **A skill with a robust edit script.** Its code still passes through the same Gemma 4 call format: `args:{…}` sorts first (args < file_path < skill_name), so a mis-termination loses `file_path`/`skill_name`. It adds array parameters (hang risk), the 1,333-character instruction and at least one load turn. The harness edit already tries the exact/flexible/regex/unescaped strategies (`swegemma/edit.py` 19). Public results agree: an edit-gate skill was worse (dominyellow), and a robust-edit skill left resolves unchanged at 6/16 (T747923).
- **A SequentialAgent pre-step.** It needs its own instruction, it shares the 40-turn and 8-minute budget, and nothing it does reaches the delimiter slip.
- **Post-steps.** They never run: the harness loop breaks on the main agent's final text after submit, and budget ends abort the whole run.
- **Replacing `edit_file`.** The only alternatives are write_file, which has the same failure plus whole-file rewrites, and `run_command` scripts.
- **Callbacks.** Unusable (§2).
