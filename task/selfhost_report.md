# Task 28.8 - self-hosting report (in progress)

What was missing or awkward in Fusion while writing the compiler in Fusion (`selfhost/`).
Each entry: what happened, the workaround, and what it suggests for Phase 2. Started
2026-10-24 and filled in as each slice is written; summarised when Task 28 ends.

## Fixed during Task 28

| Found | What | Fix |
|---|---|---|
| 28.1 planning | A string couldn't hold a literal `{` (the compiler writes C full of braces) | 28.1.5: `\{` and `\}` escapes |
| 28.2 | A bare `return` in `void main` gave invalid C (`return;` in C's `int main`) - a Python compiler bug | `return 0` in main (`_bare_return`) |

## Awkward - worked around

| Found | What | Workaround | For Phase 2 |
|---|---|---|---|
| 28.1.2 | `text[i]` on a string with any non-ASCII character counts from the start each time | Read the source as `bytes` | FEATURES.md "Later": remember the last position |
| 28.1 | No module-level variables; a function changing a struct or list it was given gets a copy | Pass state in and return it; big lists as read-only parameters | Module-level variables, or `ref` parameters |
| 28.2 | `end` is a keyword (the `End` block style), so it can't name a field or variable | `stop` | Consider making `end` contextual like `error` |
| 28.2 | `Error function f()` means "returns nothing, can fail" - there is no way to write a function that *returns* an Error value to its caller | A helper returns the message: `return Error(at(...))` | An `Error` return type, distinct from "can fail" |
| 28.3 | A list literal can't continue on the next line, even inside its brackets | Write it on one line, or use `add` | Newlines inside `( [ {` should continue the line |
| 28.3 | `{@N}` placeholders work only in `print` / `format`, not in `Error(...)` | `Error(format(...))` | Allow `{@N}` wherever a string is made with arguments? |

## Sizes and timings

| Slice | Programs | Fusion lines (lexer / parser / codegen / driver) |
|---|---|---|
| 1 | hello_world | ~600 / ~200 / ~140 / ~80 |
