# Automation Scratchpad

Commands that get run over and over, and whether they are automated - so we can see what
else is worth scripting (user request, 2026-10-09, Task 22). Add a row whenever a long
command is typed more than twice.

## Repeated commands

| Command (what it did) | How often | Status |
|---|---|---|
| `python -m pytest tests/ -q` + read the tail | after every change | **Automated** - `python check.py` |
| `python tests/verify_examples.py` + grep "Output Matches" | after every change | **Automated** - `check.py` |
| `git checkout -- files/reports/verification_report.md` (undo date-only report change) | after every examples run | **Removed** - the report is only rewritten when its content changes |
| `python main.py x.fusion` + `gcc -DFUSION_LEAK_CHECK -Wall -Wextra ...` + run, per example | after string work | **Automated** - `check.py` leak check (all examples + SYNTAX_REFERENCE programs) |
| Python one-liner scanning files for non-ASCII characters | after every edit session | **Automated** - `check.py` ascii |
| Reading `taskSummary2.md` to find status / next action | every session start | **Automated** - `python check.py --status` |
| Compiling each SYNTAX_REFERENCE.md example by hand | after doc changes | **Automated** - `check.py` (it already caught a wrong example) |
| Copying reference examples into `examples/`, building every example, keeping a list and a runner | per feature | **Automated** - `python check.py --build-examples` (Task 23) |
| `gcc -Wall -Wextra -std=c99 -c x.c` to check generated C for warnings | after codegen changes | **Candidate** - add `check.py --warnings` (needs a list of accepted warnings, e.g. unused hidden `fusion_len_*` parameters) |
| Python edit scripts written to the scratchpad (`patch(old, new)` helper) | many per task | **Partly** - use the Edit tool for small changes; a reusable `tools/patch.py` is possible but low value |
| Shell heredocs containing `\n` or quotes | (caused repeated breakage) | **Stopped** - the shell mangles escapes; write a script file instead (CLAUDE.md Rule 8) |
| commit + `git push` | per completed task | **Automatic by rule** - CLAUDE.md Rule 7 (user decision 2026-10-09): commit and push after every completed task once `check.py` passes |
| Writing plans, reading the spec for design context | per task | **Can't automate** - judgement work; grep narrows what gets read |

## Files without reliable markers

Searching works by finding a stable marker (`## 18 ...`, `[ ]`, `#### 18.3`) and reading only
that range. These files don't have reliable markers, so finding something in them costs more:

| File | Size | Problem | Suggestion |
|---|---|---|---|
| `files/fusion-language-spec.md` | ~5,400 lines | Implementation status is prose ("implemented", "not yet", "planned") in 28 different places; headings carry no task numbers | Add `**Status:** [DONE 18.2]` / `[PLANNED 17.4]` lines under feature headings, matching FEATURES.md |
| `FutureFeatures.md` | ~6,000 lines | 213 headings, almost no status or task links | Leave as a menu; link items to task numbers only when they become tasks |
| `task/taskSummaryArchive.md` | ~3,000 lines | Mixed heading styles across years (`####`, bold `**18.2.1 -`, `### Session`) | Fine - only searched, never read whole |
| `taskSummary2.md` (before Task 22) | was 2,738 lines | Status words varied (COMPLETE, RESOLVED, GUARDED, `[x]`); sub-task plans used bold lines, not headings | Fixed by Task 22 - now a small working file |
| `README.md` | 52 headings | Feature claims can drift from reality | Point it at FEATURES.md / SYNTAX_REFERENCE.md at the next README pass |
