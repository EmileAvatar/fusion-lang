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
- **Next Action:** Task 57 - approve the plan below, then 57.1

## Task 57 - Namespaces and modules (replan 2 - 2026-11-27, D.204-D.213)
**Today (built 18.4, 32.2h):** a folder is a module (`geometry/shapes/` is `geometry.shapes`, used as `shapes.x`);
`namespace X` is a free first line that only shares `internal` names; `money.round` is `fu_money__round` in C.
**Decided (user, 2026-11-27):**
- the folder gives the namespace and module; the lines optional, a mismatch an error (D.204);
- a namespace groups related modules in a folder; a module holds classes, static variables, structs, interfaces and
  static functions (sparingly) - for structured code, naked files and scripts excluded (D.205);
- the project's settings file lists its external libraries, else the import gives a path (D.206);
- `internal` is the namespace (D.207); `import SQL as Q`, full names, `Fusion.Core` always imported (D.208);
- two imported modules with the same name an error until aliased; a reverse domain a longer namespace (D.209);
- `Fusion` reserved, `Fusion.Currency` (D.210)
- structured = a module in a namespace (D.211); static added with a warning, who may be private (D.212);
  `[libraries]` and an import with a path (D.213)

**Steps** (each shipped on its own):
- 57.1 The lines and the folder (D.204, D.207):
  - the parser reads `module Name` after `namespace A.B` (both optional, the first lines, before the imports);
  - the loader works out each file's namespace and module from its folder - `SQL/Database/` is namespace SQL, module
    Database; a line that doesn't match is an error naming both;
  - `internal` follows the folder's namespace, no longer a free line - the shop example and the tests checked
- 57.2 What a structured module holds (D.211, D.212):
  - structured = a module inside a namespace; a module folder without one and the main file stay free;
  - a top-level function or variable without `static`: the compiler adds it, with a warning "write public static"
    (functions) / "write static" (variables);
  - a function public (added when nothing is written) or internal - private an error; a variable private by
    default, public or internal when written;
  - interfaces and enums public and static by default, may be private; structs and classes public by default,
    internal or private; error types and constants allowed;
  - `private` on a top-level type = its module (internal = the namespace) - D.008 replaced for types, and the
    "write internal" error kept for functions;
  - a static function called by its module's name (`Money.make(5)`); FusionTemplate.md updated (the namespace a
    folder now, the module line, the static items, the visibility table)
- 57.3 Finding libraries (D.206, Q.083):
  - `[libraries]` in fusion.toml: a namespace and its folder (`SQL = "C:/vendor/SQL"`); relative to the program's
    folder;
  - `import "C:/vendor".SQL.Database` - a quoted folder, then the names, for a library not listed;
  - the order: the program's folder, `[libraries]`, Fusion's own; the same module found twice an error naming both
- 57.4 Importing (D.208, D.209):
  - `import SQL as Q` - a namespace; `Q.Database.x` loads Database when used;
  - the full name `SQL.Database.x` once imported; two imported modules with the same name an error until one or
    both get an alias (today's rule kept);
  - `com.example.SQL` - a longer namespace in nested folders (tests);
  - the scope-aware rewrite in loader.py learns the longer names; C names `fu_SQL__Database__x`
- 57.5 Fusion's own (D.208, D.210):
  - `Fusion` reserved - a program's `namespace Fusion` (or a folder Fusion/) an error;
  - `Fusion.Core` - the built-ins' namespace, imported implicitly everywhere; `Fusion.Core.print(...)` its full name;
  - src/stdlib/Currency.fusion moves to src/stdlib/Fusion/Currency/ - module `Fusion.Currency`, still added when
    money is used (C names and the tests that name them updated);
  - `namespace Core` becomes `Fusion` / `Fusion.Core` in FusionTemplate.md and the showcase
- 57.6 `--interface` shows `namespace SQL` / `module Database` and works on a namespace (`--interface SQL`)
- 57.7 Examples and docs:
  - a new example `examples/13_projects/suppliers/` - two suppliers' `Database` modules, `[libraries]`, an alias, a
    full name, a static factory function, `internal` across a namespace;
  - shop, wordcount and the self-hosted compiler unchanged and still passing (Q.081 A);
  - SYNTAX_REFERENCE modules section, files/spec/150-Modules.md (the earlier `module.fusion` design removed),
    fusion.ebnf + page, FeatureTree, the showcase, MOD.012 BUILT, MOD.005's library part

**Tests:** tests/test_namespaces.py - every row of a truth table (Rule 4c) in files/spec/150-Modules.md: the line
written / not written / not matching x a module with / without a namespace x what it holds (static or not) x found in
the folder / `[libraries]` / a path / twice x imported as the module / the namespace / an alias / the full name - each
row a test; the existing module tests unchanged.
**Settings:** `[libraries]` (a namespace and its folder, default none) - new; into fusionSettings.xml,
project_config.py, the settings doc and the showcase toml once built.
**Not in this task:** FEATURES 57.8 (one module, one library - needs `extern`); importing only some names
`import geometry { square }` (MOD.005's other half - stays [DESIGN]).
