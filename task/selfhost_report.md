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
| 28.2, 28.5 | `end` and `var` are keywords, so they can't name a field, variable or `match` binding (`var` is reserved for type inference, which isn't built) | `stop`, `loopName` | Make little-used reserved words contextual, like `error` |
| 28.2 | `Error function f()` means "returns nothing, can fail" - there is no way to write a function that *returns* an Error value to its caller | A helper returns the message: `return Error(at(...))` | An `Error` return type, distinct from "can fail" |
| 28.3 | A list literal can't continue on the next line, even inside its brackets | Write it on one line, or use `add` | Newlines inside `( [ {` should continue the line |
| 28.3 | `{@N}` placeholders work only in `print` / `format`, not in `Error(...)` | `Error(format(...))` | Allow `{@N}` wherever a string is made with arguments? |
| 28.4 | No methods on own structs: every helper is a plain function taking the struct (`genExpr(e, ctx, funcs)`), and the same context is passed to every function | Pass a `Ctx` struct and a `Map` of signatures | Methods on structs (Task 32.1) |
| 28.4 | A `match` case binds all of a variant's fields or none (`case Function(name, result, params, body, line)` to use one; `case Rect` alone is allowed - verified, with a clear error) | List them all | Allow `_` for an unused field, or binding the first few |
| 28.4 | An empty `else { }` is needed to make a `match` complete when nothing should happen | Write the empty block | Fine as it is - explicit |
| 28.4 | A function that should be private can't be marked public if it uses a private struct - a good, clear error | - | - |
| 28.5 | The tree is made of values, so a pass can't mark nodes (e.g. number each lambda); a walk over the whole tree has to return what it found, merged up through every level | A generic `children(node)` makes each walk a few lines; lambdas are named by line + a hash of their text instead of a counter | A way to give nodes an identity (an id field set by the parser), or mutable references |

## Sizes and timings

| Slice | Programs | Fusion lines (lexer / parser / codegen / driver) |
|---|---|---|
| 1 | hello_world | ~600 / ~200 / ~140 / ~80 |
| 2 | + factorial, fizzbuzz, max_three, sum_array, const_demo, calculator, syntax_functions_and_blocks (8 of 18) | ~650 / ~720 / ~560 / ~90 |
| 3 | + syntax_strings, syntax_variables_and_control_flow, syntax_interpolation, syntax_defaults_and_named_args (12 of 18) | ~650 / ~790 / ~930 / ~90 |
| 4 | + arrays_demo, functions_demo, syntax_lambdas (15 of 18) | ~650 / ~790 / ~1,330 / ~90 |
