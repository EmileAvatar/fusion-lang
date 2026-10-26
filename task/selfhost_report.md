# Task 28.8 - self-hosting report: the test run

What happened when Fusion's compiler was written in Fusion (`selfhost/`, Task 28,
2026-10-24 to 10-26): the result, what worked, and what was missing or awkward. The
"awkward" list feeds Phase 2.

## Result

**The test run worked.** A Fusion compiler written in Fusion, built by the Python compiler,
compiles all 18 tier 1 programs (task/selfhost_subset.md). Each program it builds prints
exactly what the Python-built one prints, exits with the same code, and passes the leak
check.

- Check it with `python check.py --selfhost`. The same comparison runs in the normal test
  suite (`tests/test_selfhost.py`), together with a token-for-token comparison of the two
  lexers on all 53 example files.
- **Size:** about 3,500 lines of Fusion:

  | Part | Lines |
  |---|---|
  | lexer | 700 |
  | parser and tree | 850 |
  | checker and C generator | 1,900 |
  | driver | 80 |

- **Built in five vertical slices.** Each slice added programs and was shipped when they
  passed: 1, 8, 12, 15, then 18 of 18.
- **Two bugs found and fixed along the way:**
  - the Python compiler wrote invalid C for a bare `return` in `void main`;
  - Fusion had no way to write a literal `{` in a string.

**Timings** (`check.py --selfhost`, 2026-10-26):
- Building the Fusion compiler itself takes 3.9 s.
- Building all 18 programs: 9.9 s with the Python compiler, 6.5 s with the Fusion-written
  one.
- Both columns include GCC, and the difference is mostly Python's start-up. This is not a
  like-for-like measure of compiler speed.

## What the test run covers - and what it doesn't

The goal was a milestone, not the whole language (user, 2026-10-24). Deliberate limits:
- **Tier 1 only.** There are no lists, maps, enums, `match`, `try`, modules, bytes, files or
  string library calls in the programs it compiles. Its lexer is complete; its parser and
  generator cover tier 1. Tiers 2 and 3 come later.
- **A run-time error ends the program, as uncaught** (user decision). There are no
  `try` / `catch` paths, so a failing program frees nothing before it exits.
- **The C differs from the Python compiler's while behaving the same.**
  - Values that need freeing inside an expression use GCC statement expressions instead of
    temporaries.
  - Every function has a stack check, not just recursive ones.
- **Not supported yet** (each a clear "comes in a later slice" error):
  - arrays of values holding strings;
  - an array field set from anything but a literal;
  - a field of a value that isn't stored (`makePoint().x`).
- **The compiler does not compile itself.** It is written using tier 2 and 3 features (lists,
  maps, enums, `match`, errors, modules) that it can't compile yet. That is Task 35.

## What worked well

- **Enums with data and `match` made the syntax tree easy.** One `enum Node` with a variant
  per construct, holding lists of itself, plus exhaustive `match`. The compiler caught
  every missing case.
- **Value semantics never caused a bug.** Read-only parameters are not copied (28.1.2), so
  passing the token list and context everywhere was cheap and safe.
- **`T, Error` functions made error handling short:** errors bubble up with no code at each
  call. A parse error travels from deep in the expression parser to the driver untouched.
- **Clear compiler messages:**
  - for `var` / `end` used as names;
  - for a public function using a private struct;
  - for a `match` binding the wrong number of fields.
- **Comparing against the Python compiler at every step:** the tokens, then each program's
  output under the leak check. Mistakes showed up straight away, close to where they were
  made.

## Suggestions for Phase 2 (from the table below, most useful first)

1. **Module-level variables, or another way to share state** - the biggest source of
   friction (three entries below).
2. **Methods on structs** (Task 32.1) - every helper takes the context and the signature
   table as parameters.
3. **Newlines inside `( [ {` continue the line** - long calls and list literals had to stay
   on one line.
4. **An `Error` return type distinct from "can fail".**
5. **`_` for unused `match` fields**; reserved words that are rarely used (`end`, `var`)
   becoming contextual.
6. **Fast `text[i]` for any string** (FEATURES.md "Later").

---

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
| 28.5 | No module-level variables, and adding a struct-table parameter to every function would have meant ~40 signature changes | The struct table lives in the signature map already passed everywhere, under keys no function can have (`#Point`, `#heap:Point`) | Module-level variables (or a context object every function can reach) |
| 28.5 | The tree is made of values, so a pass can't mark nodes (e.g. number each lambda); a walk over the whole tree has to return what it found, merged up through every level | A generic `children(node)` makes each walk a few lines; lambdas are named by line + a hash of their text instead of a counter | A way to give nodes an identity (an id field set by the parser), or mutable references |

## Sizes and timings

| Slice | Programs | Fusion lines (lexer / parser / codegen / driver) |
|---|---|---|
| 1 | hello_world | ~600 / ~200 / ~140 / ~80 |
| 2 | + factorial, fizzbuzz, max_three, sum_array, const_demo, calculator, syntax_functions_and_blocks (8 of 18) | ~650 / ~720 / ~560 / ~90 |
| 3 | + syntax_strings, syntax_variables_and_control_flow, syntax_interpolation, syntax_defaults_and_named_args (12 of 18) | ~650 / ~790 / ~930 / ~90 |
| 4 | + arrays_demo, functions_demo, syntax_lambdas (15 of 18) | ~650 / ~790 / ~1,330 / ~90 |
| 5 | + structs_demo, syntax_structs, syntax_equality (18 of 18 - tier 1 complete) | ~700 / ~800 / ~1,900 / ~90 |
