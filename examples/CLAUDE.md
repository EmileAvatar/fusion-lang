# examples/ - rules for this folder

This folder is the **showcase** of what Fusion can do: for each example, the `.fusion` source,
the generated `.c`, and the working `.exe`. (Once Fusion is self-hosted: `.fusion` + `.exe`.)

## What's here

- **`syntax_*.fusion`** - generated from `SYNTAX_REFERENCE.md`, one per marked section
  (`<!-- example: name | task: N -->`). **Never edit these by hand** - edit the section in
  `SYNTAX_REFERENCE.md`, then run `python check.py --build-examples`. A block fenced as
  ` ```fusion multi-file ` (one file of a several-file project) is documentation only - it
  isn't built or checked as an example
- **Hand-written demos** (`hello_world`, `fizzbuzz`, `structs_demo`, `strings_demo`, ...) -
  fuller programs; each has its expected output in `tests/verify_examples.py`. Start the
  first line with `// ... (Task N)` so `#list.csv` gets its task number
- **Example projects** of several files (Task 18.4.4): a folder `examples/<name>/` with a
  `main.fusion` and its module folders - `shop/` (modules `money` and `cart`) and
  `wordcount/` (modules `text` and `counting`; counts a file given as an argument, or a
  sample it writes and deletes) and `expressions/` (modules `lexing` and `parsing`: text ->
  tokens -> an expression tree -> a value, with enums and match). Its `.c` /
  `.exe` are `examples/<name>/main.c` / `main.exe`; its expected output is keyed by the
  folder name; check.py, verify_examples and `#run.bat` include it
- **`#list.csv`** - generated: `fusion, c, exe, task, added` for every example (a row keeps
  the date it was first added)
- **`#run.bat`** - generated: runs every `.exe` with `--headless` and no input (`< nul`), each under a
  `---- name.exe ----` header, then pauses once so the console stays open. Double-click it
  to see everything run. (Run on its own, a program waits for a key before it closes)
- **`project_config_demo/`** - a manual demo of `fusion.toml` changing compiler behaviour

## Rules

1. After adding or changing an example (or a `SYNTAX_REFERENCE.md` section), run
   **`python check.py --build-examples`**. It writes the `syntax_*` programs, builds every
   example (`.c` + `.exe`), and regenerates `#list.csv` and `#run.bat`. Never hand-edit
   those two
2. `python check.py` fails if a `syntax_*.fusion` file is out of date with
   `SYNTAX_REFERENCE.md`
3. **In git:** `.fusion` files and this file. **Not in git (local preview only, reaches the
   other PC via Dropbox):** `.c`, `.exe`, `#list.csv`, `#run.bat` - user decision 2026-10-09
4. Every example must compile, run, and be leak-free - `python check.py` checks all of them
