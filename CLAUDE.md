# Fusion Programming Language - Claude Code Instructions

**Project:** Fusion compiler (Python, compiles Fusion -> C -> native executable via GCC)
**Icon:** 🏗️ (official)

This file holds only **rules and how to run things**. It is loaded every session, so keep it
short. Status, features and plans live elsewhere (see "Where things are").

---

## 🚨 Rules

### Rule 1: Plan first, then act
1. At session start run `python check.py --status` (open items + next action)
2. For any new work, write a detailed plan in `taskSummary2.md` - including a **Settings**
   line: which project settings the task adds or changes (or "none"). Every new or changed
   setting goes into `files/fusionSettings.xml` (user, 2026-10-28)
3. Show the plan to the user and get approval
4. Only then implement it
5. After each sub-task: update its line in `FEATURES.md`, write at most a few lines in
   `taskSummary2.md`, add or update any setting it needs in `files/fusionSettings.xml`, and
   run `python check.py`

### Rule 2: No emojis in code files
Emojis and other non-ASCII characters cause encoding errors (cp1252 vs UTF-8). OK in `*.md`
files and chat; never in `.py`, `.c`, `.h`, `.fusion`, config, JSON or YAML. Use `[OK]`,
`[FAIL]`, `[WARN]`, `# TODO` instead. `check.py` enforces this.

### Rule 3: Tracking - where status and detail go
- **`FEATURES.md`** - the status of every open and postponed task and feature, one line each:
  `[ ]` open, `[POSTPONED to X]` (waits for task X or a missing feature). When a task is
  complete, its `[DONE]` lines move to `task/featuresArchive.md` (verbatim, same session).
  Tasks are `#### NN Title [status]`; sub-tasks are one tab + `[status] NN.N`; parts two
  tabs. Postponed advanced features are listed there too
- **`taskSummary2.md`** - a working file only: the active task's detailed plan, the next
  action, the latest session note
- **`task/taskSummaryArchive.md`** - when a task **or a sub-task** is complete, move its
  detail there verbatim (same session); its `FEATURES.md` lines, marked `[DONE]`, move to
  `task/featuresArchive.md` when the whole task is complete
- **`task/taskBacklog.md`** - write-ups of tasks not started yet; a task's section moves
  back to `taskSummary2.md` when it becomes active
- Detail of *what* changed is in git commit messages and tests - don't repeat it in notes
- **"Add it to the tasks"** (user phrase) means: schedule it in `FEATURES.md` - under the task
  being worked on if it belongs there, otherwise under the future task it fits, or "Later /
  advanced" with a `[POSTPONED to X]`

### Rule 3b: Decisions.md - one list of every feature and decision
From 2026-10-31 (user): `Decisions.md` lists every Fusion language feature in one line
(`AREA.NNN [STATUS] ...`) and the latest decision on each subject in one table row.
- Before designing anything: grep it for the subject; if a proposal goes against an
  ACTIVE decision, tell the user before going further
- After the user decides: update the feature line and the decision row in the same session;
  a replaced decision is removed (git keeps the history); a conflict is a `CLASH` row until
  the user settles it
- Language features only - no bug fixes, no discussions; keep it small
- Keep it ordered: a new line goes at the end of its area with the next number (STC.006 after
  STC.005), decisions by number (user, 2026-10-31)

### Rule 4: Ship an example for every new feature
When a language feature lands: add a short example to `SYNTAX_REFERENCE.md` (it becomes an
example program in `examples/` - see `examples/CLAUDE.md`), or a fuller demo program in
`examples/` with its expected output in `tests/verify_examples.py`.

### Rule 4b: Test with and without null checks
From 2026-10-28 (user): a feature where a value can be null is tested both ways - without a
check, the null is a NullError that a `catch` handles correctly; with `?.` / `?.null` /
`case null`, the code runs on as intended.

### Rule 4c: A truth table when there are many permutations
From 2026-10-30 (user): when a design has many combinations (visibility x where it is used,
form x order x what it may change, ...), write them out as a truth table in its design
document (`Classes.md`, `Object_Lifetime.md`, `Ownership.md`, `Nullable_Values.md`, `Arrays.md`) - every row
a case, so it can be checked at a glance and each row becomes a test.

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
`python check.py --ship "message" --claude` does both, only if every check passes.

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
python main.py main.fusion --interface [module]   # public interface of the modules it imports
python main.py program.fusion --no-new-config     # don't write a fusion.toml when there is none
python check.py                      # all checks, short summary (about 25 s)
python check.py --quick              # unit tests only
python check.py --status             # open items + next action, no build
python check.py --ship "msg" --claude # all checks; commit + push only if all pass (Rule 7)
python check.py --example wordcount  # build, run, compare one example
python check.py --builtins           # rewrite files/Builtins.md after adding a built-in
python check.py --runtime            # rewrite runtime/fusion_runtime.h after changing the C run-time
python check.py --selfhost           # the Fusion-written compiler vs the Python one, tier 1 (28.7)
python check.py --fix-ascii          # non-ASCII -> \uXXXX where the meaning is unchanged
python tools/patch.py edits.py       # exact (file, old, new) edits, all or nothing
python -m pytest tests/ -q           # tests directly
python tests/verify_examples.py      # examples directly
```

`check.py` runs: the test suite (end-to-end tests compile with `-DFUSION_LEAK_CHECK`), the
examples, a leak check of every example and every `SYNTAX_REFERENCE.md` program (exit 3 =
string never freed, 4 = freed twice), that `files/Builtins.md` and `runtime/fusion_runtime.h`
match the compiler, that `Decisions.md` is in shape (Rule 3b), and the ASCII rule.

### Setting up a new machine
1. Python 3.11+ (`tomllib`), and GCC on PATH (Windows: MinGW-w64, e.g.
   `winget install BrechtSanders.WinLibs.POSIX.UCRT`, then restart the editor)
2. `pip install -r requirements.txt`
3. `python check.py` - every line should say `[OK]`
4. Optional (Windows): double-click `tools/windows/fusion-file-preview.reg` so Explorer's
   preview pane shows `.fusion` files (undo: `fusion-file-preview-undo.reg`)

On a Dropbox copy of the repo, git may need `git config windows.appendAtomically false`
(already set locally). Use one PC at a time and let Dropbox finish syncing before switching.

---

## Where things are

| What | Where |
|---|---|
| Every feature (one line) and the latest decision on each subject, clashes marked | `Decisions.md` |
| Status of every open task/feature, postponed items | `FEATURES.md` |
| Finished tasks and items (their FEATURES.md lines) | `task/featuresArchive.md` |
| What the language can do now, with examples | `SYNTAX_REFERENCE.md` |
| Every built-in function and method (generated) | `files/Builtins.md` |
| Every type: default, range, size, status (open in a browser; update by hand) | `files/FusionTypes.html` |
| Active task plan + next action | `taskSummary2.md` |
| Finished task detail, old sessions | `task/taskSummaryArchive.md` |
| Not-started task write-ups | `task/taskBacklog.md` |
| MVP history (Tasks 1-4) | `task/taskSummary.md` |
| Commands we repeat / could automate | `task/automation.md` |
| Full language design | `files/fusion-language-spec.md` (grep it) |
| Grammar | `files/fusion.ebnf` |
| Every project setting, its values and default (master template, read only) | `files/fusionSettings.xml` |
| Null design: `?.`, `??`, number conditions, truth tables | `Nullable_Values.md` |
| Single values, arrays, lists, maps: what each does, when (not) to use it | `Arrays.md` |
| When a class object is freed: every way it gains or loses a reference | `Object_Lifetime.md` |
| Ownership: moves, borrows, `shared`, readonly caller / called, one writer across threads (Task 48) | `Ownership.md` |
| Classes: visibility, constructors, static set-up (forms A, B, C), Default, ToString - truth tables | `Classes.md` |
| How a .fusion file is laid out: namespace, imports, the preferred order | `files/FusionTemplate.md` |
| Read before picking future features | `FutureFeaturesCaution.md`, then `FutureFeatures.md` |
| Compiler source | `src/` - `src/CLAUDE.md` explains the pipeline; each subfolder's `CLAUDE.md` has one line per file |
| Tests / examples | `tests/`, `examples/` |

Folders: `taskSummary2.md`, `FEATURES.md`, `SYNTAX_REFERENCE.md` stay in the root; docs in
`files/`; tests in `tests/`; no `docs/` folder until the compiler goes live. `Notes/` is for
our internal discussion (reviews, sources); `files/` is for developers who need to understand
the language and its code (user, 2026-10-29).

---

## Auto-update policy

When a language feature or spec changes, update every affected file without asking:

| Change | Update |
|---|---|
| Any implemented feature | `FEATURES.md`, `SYNTAX_REFERENCE.md`, an example program, its `Decisions.md` line ([BUILT]) |
| Any language decision (new, changed, postponed, rejected) | `Decisions.md` (Rule 3b) |
| Syntax (lambdas, blocks, types, keywords, operators) | `files/fusion.ebnf`, `files/fusion-language-spec.md`, `SYNTAX_REFERENCE.md` |
| String interpolation | language spec, `SYNTAX_REFERENCE.md`, examples |
| Standard library module | language spec |
| A concurrency idea, design decision, trap, principle or real-world case | `Concurrency.md` (full write-up), `Concurrency_Traps.md` (the overview tables) and `files/Service.md` (the `service` reference) - keep them in step; schedule any new feature in `FEATURES.md` Task 42 |
| An ownership decision (moving, borrowing, `shared`, readonly at the call, threads) | `Ownership.md` (truth tables + decisions log); the thread side also `files/Service.md` and `Concurrency.md` 3.13; schedule in `FEATURES.md` Task 48 / 42 |
| A null-handling decision (`?.`, `??`, nullable types, number conditions) | `Nullable_Values.md` (decisions log + tables); schedule in `FEATURES.md` Task 30 |
| A project setting added or changed (`fusion.toml` / `.yaml` / `.json` / `.ini`) | **Once the feature is built** (not before): `files/fusionSettings.xml` (the master template - its type, values, default, description, task), `src/config/project_config.py`, spec "Project Configuration", `SYNTAX_REFERENCE.md` settings section - `tests/test_settings_formats.py` checks template and compiler agree |
| A task done (any new, changed or newly decided setting) | `files/showcase/fusion.toml` - every setting a finished Fusion will have, tagged [built] / [designed] / [idea] / [rejected] (user, 2026-10-28) |
| A source file added, renamed or given a new job | that folder's `CLAUDE.md` (one line per file) |

---

## Project notes
- **Core concept:** an agnostic language - each project configures features, safety level,
  memory strategy and backend (`fusion.toml`)
- **Long-term concurrency goal:** a million requests on one machine with many cores - no
  data races by construction, deadlocks and freezes prevented by rules (any that slip through
  become clear errors), no slowdown - with as small a memory and CPU footprint as
  possible, and very scalable. The core: a resource becomes a service (`service` keyword),
  instead of every caller updating it by hand; manual locking is a last resort
  (`Concurrency.md`, `Concurrency_Traps.md`, FEATURES.md Task 42)
- **Features become settings:** design each feature so a project can switch it in
  `fusion.toml` where that makes sense, with a safe default (e.g. `[structs]`: holding
  List / Map on, functions on structs off, classes inside structs off). Reviewing an idea
  means deciding: a setting, a fixed rule, or discarded (FEATURES.md, top)
- **Method names say what they do (user, 2026-10-27):** a verb where possible -
  `copyPart`, `removeLast`, `removeRange`, `insertAll`; a method that changes the
  collection says so, one that copies leaves the original alone. A short familiar name may
  be added as quick typing (sugar) for the clear one: `slice` / `copyPart`, `pop` /
  `removeLast`, `len()` / `length()`
- **Program to an interface, not an implementation (user, 2026-10-28):** code - Fusion's own
  and its libraries - uses an interface where it makes sense (`List`, `Collection`), so the
  implementation behind it can change later; an array is one fixed implementation, a `List`
  has a default one (never null) that can be swapped (the Dependency Inversion Principle)
- **Memory: OWNERSHIP first, always (user, 2026-10-29):** memory stability - no crashes where
  avoidable, no leaks (they cause instability and security holes); GC / MANUAL only where a
  project needs them (`Object_Lifetime.md`)
- **No outside price or rate lookups (user, 2026-10-29) - a hard rule:** the core and every
  module (Currency included) never call an external API to fetch prices or exchange rates;
  the developer using them fetches the data and passes it in
- **Guiding rule:** a simple working language first, advanced features after
  (`FutureFeaturesCaution.md`). Security principle: never trust code
- **Repository is public** on GitHub (`EmileAvatar/fusion-lang`); history was scrubbed of a
  personal email on 2026-08-04
- **Name conflict:** another language is called Fusion (fusion-lang.org). Keep the name
  during development; rename once the language works reliably, before 1.0
