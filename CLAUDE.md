# Fusion Programming Language - Claude Code Instructions

**Project:** Fusion compiler (Python, compiles Fusion -> C -> native executable via GCC)
**Icon:** 🏗️ (official)

This file holds only **rules and how to run things**. It is loaded every session, so keep it
short. Status, features and plans live elsewhere (see "Where things are").

---

## 🚨 Rules

### Rule 1: Plan first, then act
1. At session start run `python check.py --status` (open items + next action)
2. For any new work, write a detailed plan in `taskSummary2.md`
3. Show the plan to the user and get approval
4. Only then implement it
5. After each sub-task: update its line in `FEATURES.md`, write at most a few lines in
   `taskSummary2.md`, and run `python check.py`

### Rule 2: No emojis in code files
Emojis and other non-ASCII characters cause encoding errors (cp1252 vs UTF-8). OK in `*.md`
files and chat; never in `.py`, `.c`, `.h`, `.fusion`, config, JSON or YAML. Use `[OK]`,
`[FAIL]`, `[WARN]`, `# TODO` instead. `check.py` enforces this.

### Rule 3: Tracking - where status and detail go
- **`FEATURES.md`** - the status of every task and feature, one line each:
  `[ ]` open, `[DONE]`, `[POSTPONED to X]` (waits for task X or a missing feature).
  Tasks are `#### NN Title [status]`; sub-tasks are one tab + `[status] NN.N`; parts two
  tabs. Postponed advanced features are listed there too
- **`taskSummary2.md`** - a working file only: the active task's detailed plan, the next
  action, the latest session note
- **`task/taskSummaryArchive.md`** - when a task **or a sub-task** is complete, move its
  detail there verbatim (same session), leaving its line in `FEATURES.md` as `[DONE]`
- **`task/taskBacklog.md`** - write-ups of tasks not started yet; a task's section moves
  back to `taskSummary2.md` when it becomes active
- Detail of *what* changed is in git commit messages and tests - don't repeat it in notes
- **"Add it to the tasks"** (user phrase) means: schedule it in `FEATURES.md` - under the task
  being worked on if it belongs there, otherwise under the future task it fits, or "Later /
  advanced" with a `[POSTPONED to X]`

### Rule 4: Ship an example for every new feature
When a language feature lands: add a short example to `SYNTAX_REFERENCE.md` (it becomes an
example program in `examples/` - see `examples/CLAUDE.md`), or a fuller demo program in
`examples/` with its expected output in `tests/verify_examples.py`.

### Rule 5: Headings in tracking and reference files
In `FEATURES.md`, `SYNTAX_REFERENCE.md` and similar files, `##` is only for **major
sections**. Tasks and headings inside a major section use `####` - easier to read.

### Rule 6: README.md states goals, not status
`README.md` says what Fusion is trying to achieve and points to `FEATURES.md` (status) and
`SYNTAX_REFERENCE.md` (what works now). It never lists what currently works or not. Update it
only for a major change - e.g. a new feature direction that wasn't accounted for before.

### Rule 7: Commit and push after every completed task
When a task or sub-task is complete and `python check.py` passes: commit, then push to
GitHub (`git push`) - automatically, without asking (user decision, 2026-10-09).

### Rule 8: Work efficiently (token budget is limited)
- Find before reading: `grep -n` for a heading or task number, then read only that range
- Don't re-read large files (spec ~5,400 lines, `FutureFeatures.md` ~6,000) - grep them
- Edit code with the Edit tool or a Python script file - not shell heredocs with escapes
  (they mangle `\n` and quotes)
- Verify with `python check.py` rather than running the individual commands

---

## How to run

```text
python main.py program.fusion        # compile -> program.c and program.exe (fusion.toml optional)
python check.py                      # all checks, short summary (about 25 s)
python check.py --quick              # unit tests only
python check.py --status             # open items + next action, no build
python -m pytest tests/ -q           # tests directly
python tests/verify_examples.py      # examples directly
```

`check.py` runs: the test suite (end-to-end tests compile with `-DFUSION_LEAK_CHECK`), the
examples, a leak check of every example and every `SYNTAX_REFERENCE.md` program (exit 3 =
string never freed, 4 = freed twice), and the ASCII rule.

### Setting up a new machine
1. Python 3.11+ (`tomllib`), and GCC on PATH (Windows: MinGW-w64, e.g.
   `winget install BrechtSanders.WinLibs.POSIX.UCRT`, then restart the editor)
2. `pip install -r requirements.txt`
3. `python check.py` - every line should say `[OK]`

On a Dropbox copy of the repo, git may need `git config windows.appendAtomically false`
(already set locally). Use one PC at a time and let Dropbox finish syncing before switching.

---

## Where things are

| What | Where |
|---|---|
| Status of every task/feature, postponed items | `FEATURES.md` |
| What the language can do now, with examples | `SYNTAX_REFERENCE.md` |
| Active task plan + next action | `taskSummary2.md` |
| Finished task detail, old sessions | `task/taskSummaryArchive.md` |
| Not-started task write-ups | `task/taskBacklog.md` |
| MVP history (Tasks 1-4) | `task/taskSummary.md` |
| Commands we repeat / could automate | `task/automation.md` |
| Full language design | `files/fusion-language-spec.md` (grep it) |
| Grammar | `files/fusion.ebnf` |
| Read before picking future features | `FutureFeaturesCaution.md`, then `FutureFeatures.md` |
| Compiler source | `src/` (lexer, parser, semantic, codegen, config) - `c_memory.py` = string runtime |
| Tests / examples | `tests/`, `examples/` |

Folders: `taskSummary2.md`, `FEATURES.md`, `SYNTAX_REFERENCE.md` stay in the root; docs in
`files/`; tests in `tests/`; no `docs/` folder until the compiler goes live.

---

## Auto-update policy

When a language feature or spec changes, update every affected file without asking:

| Change | Update |
|---|---|
| Any implemented feature | `FEATURES.md`, `SYNTAX_REFERENCE.md`, an example program |
| Syntax (lambdas, blocks, types, keywords, operators) | `files/fusion.ebnf`, `files/fusion-language-spec.md`, `SYNTAX_REFERENCE.md` |
| String interpolation | language spec, `SYNTAX_REFERENCE.md`, examples |
| Standard library module | language spec |

---

## Project notes
- **Core concept:** an agnostic language - each project configures features, safety level,
  memory strategy and backend (`fusion.toml`)
- **Guiding rule:** a simple working language first, advanced features after
  (`FutureFeaturesCaution.md`). Security principle: never trust code
- **Repository is public** on GitHub (`EmileAvatar/fusion-lang`); history was scrubbed of a
  personal email on 2026-08-04
- **Name conflict:** another language is called Fusion (fusion-lang.org). Keep the name
  during development; rename once the language works reliably, before 1.0
