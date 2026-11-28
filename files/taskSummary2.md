# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## Next

- Task 33 (generics) complete 2026-11-22 - its plan in task/taskSummaryArchive.md
- Done 2026-11-22: 45.10 an array as a Collection<T> (D.090) - its plan in task/taskSummaryArchive.md
- Done 2026-11-23: 36.0 a simple highlighter for VS Code and Sublime Text (tools/editors/, installed in VS Code)
- Done 2026-11-24: 47.1 `long` / `short` (tests/test_long_short.py, syntax_long) - its plan in task/taskSummaryArchive.md
- Done 2026-11-24: 36.8 Fusion's colours (tools/editors/colors.json, four themes) - its plan in task/taskSummaryArchive.md
- Done 2026-11-24: research R10 written - files/Research/Money/Money.md
- Done 2026-11-25: files/fusion.ebnf synced with the compiler (no version until self-hosting - 35.7), the "ebnf" check;
  the memory tiers note to R11.8, Vale to R11.6, flash wear 41.11e
- Done 2026-11-25: 47.7 `int128` / `int256` (tests/test_wide_numbers.py, syntax_wide_numbers) - its plan in task/taskSummaryArchive.md
- Done 2026-11-25: 47.8 `decimal` (tests/test_decimal.py, syntax_decimal) - its plan in task/taskSummaryArchive.md
- Done 2026-11-25: 47.2a `money` - the type (tests/test_money.py, syntax_money)
- Done 2026-11-25: 47.2b the Currency module (tests/test_currency.py, syntax_currency) - 47.2 complete, its plan in task/taskSummaryArchive.md
- Done 2026-11-25: 47.6 ranges over decimals and money (tests/test_decimal_ranges.py, syntax_ranges) - its plan in
  task/taskSummaryArchive.md
- Done 2026-11-25: 47.3 an enum as a built-in value struct (tests/test_enum_fields.py, syntax_enum_planets) - its plan
  in task/taskSummaryArchive.md
- Done 2026-11-27: 47.10 an enum value alone anywhere (tests/test_bare_enum.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.11 enum values written with their enum (tests/test_bare_enum.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.12 `[source] shadowing` (tests/test_shadowing.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.9 number notations (tests/test_number_notations.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.4 FusionType (tests/test_fusion_type.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.5 `fixed(n)` (tests/test_fixed.py) - Task 47 complete, its plans in task/taskSummaryArchive.md
- Done 2026-11-24: R11 FSMA set up (files/Research/Memory/FSMA/, FEATURES R11, R3.9-R3.11) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: Tasks 33, 45, 47 closed - their postponed items moved (L6.9, 42.19, L8.11)
- Done 2026-11-28: Task 57 namespaces and modules (tests/test_namespaces.py, examples/13_projects/suppliers) - its plan
  in task/taskSummaryArchive.md
- Done 2026-11-28: Task 56 loop safety (tests/test_loop_checks.py, syntax_loop_checks) - its plan in
  task/taskSummaryArchive.md
- **Next Action:** Task 58 - 58.1 (the plan below, approved - D.221-D.229)

## Task 58 - Script mode: Fusion written and run like a Python script (plan 3 - 2026-11-28, approved - D.221-D.229)
**Today:** `python main.py program.fusion` writes program.c and program.exe next to it (and a fusion.toml when there is
none); it is then run by hand; a statement at the top of a file is a parse error; `main(string... args)`, `exit(n)`.
Decided D.221-D.229.

**Steps** (each shipped on its own):
- 58.1 Statements at the top (D.222, D.225): the parser takes statements at the top of a file; a file without
  `main` gets one made of them, in order; its variables become module variables set where their line runs, so
  functions see them; classes, structs, enums, interfaces and imports as in any file; a file with both `main` and
  statements at the top an error; `args` (none or many); the `#!` first line
- 58.2 `Fusion.Settings { ... }` (D.224, Q.096-Q.098): first in the file (after a `#!`); the name alone or
  `section.name`; the same checks as the settings file; used instead of the settings file; only the starting
  file's - another file's ignored with a warning; in a program with `main` too
- 58.2b The settings file (D.227, Q.099 A): none written any more - none means the defaults (`--no-new-config` and
  31.2's new file go); the file is `settings.toml` (/ .yaml / .yml / .json / .ini) - every fusion.toml in examples/
  and the tests renamed; `fusion.toml` stays the reference (files/showcase/); spec 001, CLAUDE.md, the docs
- 58.3 `python main.py run tidy.fusion [arguments]` (D.221, D.223, D.224): builds into the cache folder - a hash
  of the script, the files it imports, its settings and the compiler's version; unchanged - the kept program runs at
  once; where the cache folder can't be written, next to the script; the arguments passed, the exit code passed
  back; the build messages only when it fails (a script prints only its own output)
- 58.4 Start-up times measured and written down (spec 170): the first run and a cached one, for a small script
- 58.5 An example script (`examples/12_files_and_programs/tidy.fusion` - its expected output) and the documents:
  SYNTAX_REFERENCE, spec 170 (Script Mode as built, "Slower execution" / "interpreted" corrected - it is compiled),
  fusion.ebnf + page (the top-level statements), FeatureTree, the showcase, SET.013 PARTIAL
- Not in this task: FEATURES 58.5 (running other Fusion code inside a program - Task 60); an interpreter (later, after
  self-hosting); `fusion` as an installed command (Task 35)

**Tests:** tests/test_scripts.py - a truth table in spec 170 (Rule 4c): with / without main x statements at the top x
variables used by functions x args / exit code x the cache - first build, unchanged, the script changed, an import
changed, a setting changed x a fusion.toml there or not (none written) x a `Fusion.Settings` block - first, not first, in another file x `#!`
- each row a test.
**Settings:** none.
