# examples/ - rules for this folder

This folder is the **showcase** of what Fusion can do: for each example, the `.fusion` source,
the generated `.c`, and the working `.exe`. (Once Fusion is self-hosted: `.fusion` + `.exe`.)

## Topic folders (user, 2026-11-22)

The programs sit in numbered topic folders, to follow in order:

- `01_basics/` - hello world, the three block styles, variables, control flow, ranges
- `02_functions/` - functions, default and named arguments, lambdas, templates, `int...`, at the call
- `03_strings/` - strings, interpolation, Unicode, bytes, ToString
- `04_arrays/` - arrays, growable and jagged arrays, arrays of many dimensions, length
- `05_collections/` - Lists, Maps, foreach, shared or copied Lists
- `06_match_and_enums/` - match, enums
- `07_structs/` - structs
- `08_classes/` - classes, methods, statics, getters, copies, interfaces, inheritance, `Default`
- `09_generics/` - generics, conditions, packs
- `10_errors_and_null/` - errors, try, null handling (null enums too)
- `11_ownership/` - moving, borrowing, readonly, one writer
- `12_files_and_programs/` - files, program input and output, running programs, `write`
- `13_projects/` - programs of several files, and `project_config_demo/`

A program's name is unique across the folders - `python check.py --example NAME` finds it by
name alone. `tools/example_files.py` knows the layout; check.py, verify_examples and the tests use it.

## What's here

- **`syntax_*.fusion`** - generated from `files/SYNTAX_REFERENCE.md`, one per marked section
  (`<!-- example: name | task: N | folder: X -->` - written to `examples/X/`). **Never edit
  these by hand** - edit the section in `files/SYNTAX_REFERENCE.md`, then run
  `python check.py --build-examples` (a changed `folder:` moves the program). A block fenced as
  ` ```fusion multi-file ` (one file of a several-file project) is documentation only - it
  isn't built or checked as an example
- **Hand-written demos** (`hello_world`, `fizzbuzz`, `structs_demo`, `strings_demo`,
  `control_flow`, `errors_demo` - run it with the argument `uncaught` to see an error nobody
  catches, `style_indent` / `style_braces` / `style_end` - one program in the three block
  styles; a test checks they compile to the same C (Task 27.4), ...) -
  fuller programs; each has its expected output in `tests/verify_examples.py` and its topic
  folder in `DEMO_FOLDERS` (`tools/example_files.py` - check.py fails for a program in neither).
  Start the first line with `// ... (Task N)` so `#list.csv` gets its task number
- **Example projects** of several files (Task 18.4.4): a folder `examples/13_projects/<name>/`
  with a `main.fusion` and its module folders - `shop/` (modules `money` and `cart`) and
  `wordcount/` (modules `text` and `counting`; counts a file given as an argument, or a
  sample it writes and deletes) and `expressions/` (modules `lexing` and `parsing`: text ->
  tokens -> an expression tree -> a value, with enums and match). Its `.c` /
  `.exe` are `main.c` / `main.exe` in its folder; its expected output is keyed by the
  folder name; check.py, verify_examples and `#run.bat` include it
- **`fusion.toml`** - the same file in each topic folder 01-12 (a program finds the settings
  file next to it): `[build] waitAtExit = true`, `[structs] functions = true` for
  `syntax_struct_methods`, and `[ranges] decimals = true` for `syntax_ranges` (47.6). Change all of them together
- **`#list.csv`** - generated: `fusion, c, exe, task, added` for every example, with its topic
  folder (a row keeps the date it was first added)
- **`#run.bat`** - generated: runs every `.exe` with `--headless` and no input (`< nul`), each under a
  `---- folder\name.exe ----` header, then pauses once so the console stays open. Double-click it
  to see everything run. (Run on its own, a program waits for a key before it closes - the
  folder's `fusion.toml` sets `[build] waitAtExit = true`; programs elsewhere close at once by default)
- **`13_projects/project_config_demo/`** - a manual demo of `fusion.toml` changing compiler behaviour

## Rules

1. After adding or changing an example (or a `files/SYNTAX_REFERENCE.md` section), run
   **`python check.py --build-examples`**. It writes the `syntax_*` programs, builds every
   example (`.c` + `.exe`), and regenerates `#list.csv` and `#run.bat`. Never hand-edit
   those two
2. `python check.py` fails if a `syntax_*.fusion` file is out of date with
   `files/SYNTAX_REFERENCE.md`, or a program has no topic folder
3. **In git:** `.fusion` files, the `fusion.toml` files and this file. **Not in git (local
   preview only, reaches the other PC via Dropbox):** `.c`, `.exe`, `#list.csv`, `#run.bat` -
   user decision 2026-10-09
4. Every example must compile, run, and be leak-free - `python check.py` checks all of them
