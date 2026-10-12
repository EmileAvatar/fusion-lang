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
| Python edit scripts written to the scratchpad (`patch(old, new)` helper) | many per task | **Automated** - `python tools/patch.py edits.py` (Task 22.11) |
| Shell heredocs containing `\n` or quotes | (caused repeated breakage) | **Stopped** - the shell mangles escapes; write a script file instead (CLAUDE.md Rule 8) |
| commit + `git push` | per completed task | **Automatic by rule** - CLAUDE.md Rule 7 (user decision 2026-10-09): commit and push after every completed task once `check.py` passes |
| Writing plans, reading the spec for design context | per task | **Can't automate** - judgement work; grep narrows what gets read |
| Turning non-ASCII characters into `\uXXXX` escapes (the editor tool sometimes stores `\u00e9` as the real character, which fails the ascii check) | most string / Unicode tasks | **Automated** - `python check.py --fix-ascii` (Task 22.8): only where the meaning is unchanged, the rest is listed |
| Gated commit: run `check.py`, commit + push only when every check passes | every completed task (Rule 7) | **Automated** - `python check.py --ship "message" --claude` (Task 22.9; one ungated push in 18.4.2 went out with a failing check) |
| Building and running one example by hand (`python main.py x.fusion`, run the exe with `--headless < nul`, compare with the expected output) | per example change | **Automated** - `python check.py --example NAME [args]` (Task 22.10) |

## Files without reliable markers

Searching works by finding a stable marker (`## 18 ...`, `[ ]`, `#### 18.3`) and reading only
that range. These files don't have reliable markers, so finding something in them costs more:

| File | Size | Problem | Suggestion |
|---|---|---|---|
| `files/fusion-language-spec.md` | ~5,800 lines | Status was prose in many places; headings carried no task numbers | **Fixed** (22.7b): a `**Status:** [DONE n] / [PARTLY] / [PLANNED n] / [DESIGN]` line under every major section - `grep -n "^\*\*Status" files/fusion-language-spec.md` lists them all |
| `FutureFeatures.md` | ~6,000 lines | 213 headings, almost no status or task links | Leave as a menu; link items to task numbers only when they become tasks |
| `task/taskSummaryArchive.md` | ~3,000 lines | Mixed heading styles across years (`####`, bold `**18.2.1 -`, `### Session`) | Fine - only searched, never read whole |
| `taskSummary2.md` (before Task 22) | was 2,738 lines | Status words varied (COMPLETE, RESOLVED, GUARDED, `[x]`); sub-task plans used bold lines, not headings | Fixed by Task 22 - now a small working file |
| `README.md` | 21 headings | Feature claims could drift from reality | **Fixed** (22.7a): goals + pointers to FEATURES.md / SYNTAX_REFERENCE.md, no status lists |
