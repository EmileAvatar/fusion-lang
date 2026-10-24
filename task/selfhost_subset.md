# Task 28.1 - the self-hosting subset (2026-10-24)

What the programs in `examples/` use, measured: `python tools/example_subset.py` parses and
checks all 44 programs with the Python compiler's front end, then lists every construct,
type, operator, builtin and method they use. All 44 analysed cleanly.

The question for Task 28 has two sides:
1. **What the Fusion-written compiler must accept:** the constructs in the examples
   (sections 1-2 below).
2. **What the compiler itself needs, to be written in Fusion:** sections 3-4. It is built
   by the Python compiler, so it may use anything Python supports; it does **not** have to
   compile itself (that is Task 35).

---

## 1. The examples cover almost the whole built language

The `syntax_*` programs are one per `SYNTAX_REFERENCE.md` section, so together the 44
examples use nearly everything built:
- 53 kinds of syntax node;
- 15 types;
- 15 operators;
- about 110 builtin functions, about 80 of them from the string library;
- 14 list and map methods.

Compiling **all** of them means re-implementing nearly the whole Python compiler. That is
too big for a test run, so the examples fall into three tiers by what they need:

| Tier | Programs | What they need |
|---|---|---|
| **1 - core** (18) | hello_world, factorial, fizzbuzz, max_three, sum_array, const_demo, calculator, arrays_demo, functions_demo, structs_demo, syntax_strings, syntax_variables_and_control_flow, syntax_interpolation, syntax_defaults_and_named_args, syntax_functions_and_blocks, syntax_lambdas, syntax_structs, syntax_equality | Functions, variables, `if` / `while` / `for`, arrays, structs, strings, interpolation, function values; almost no library |
| **2 - collections and enums** (12) | control_flow, style_indent, style_braces, style_end, strings_demo, syntax_lists, syntax_maps, syntax_enums, syntax_enum_data, syntax_match, syntax_string_operations, syntax_unicode | Tier 1, plus List, Map, enums (with data), `match`, part of the string library |
| **3 - everything else** (14) | errors_demo, syntax_errors, syntax_error_types, syntax_try, syntax_arrays, syntax_overflow, expressions, shop, wordcount, syntax_bytes, syntax_files, syntax_methods, syntax_program_io, syntax_string_library | Errors and try / catch / throw, `unchecked`, modules and `import`, bytes, files, console input, the full string library |

`syntax_arrays` is in tier 3 only because it catches an `IndexError` with `try`.

## 2. The tier 1 subset in detail

| Area | What tier 1 uses |
|---|---|
| Types | `int`, `float`, `double`, `bool`, `char`, `string`, `void`; fixed arrays (`int[]`, `int[3]`); structs; function types `(int) : int` |
| Declarations | Functions (block bodies and one-line `: expr`), parameters with defaults, structs with fields, field defaults and nested structs, `const` |
| Statements | Variable declarations, assignment (also `a.b.c = x`, `a[i] = x`), `if` / `else if` / `else`, `while`, `for` over `range()` and over arrays, `break`, `continue`, `return`, expression statements |
| Expressions | Literals (int, float, char, string, bool); `+ - * / %`; `== != < > <= >= === !==`; `and or not`; unary `-`; calls, named arguments, struct construction (by position and by name); `a.field`; `a[i]`; array literals; interpolation `{name}`, `{a.b}`, `{@1}`; lambdas `func(int x) : x * 2` |
| Block styles | All three: indentation, braces, `End` |
| Builtins | `print`, `len`, `range`, `format`, and a handful of string functions (`toString`, `toInt`, `trim`, `toUpper`, `indexOf`, `formatNumber`) |
| Run-time checks | Array bounds, whole-number overflow, division by zero - each one stops the program with its message (no `try` in tier 1) |

## 3. What the Fusion-written compiler needs (tested 2026-10-24)

| Need | Status | Note |
|---|---|---|
| A tree of syntax nodes | **Works** | An enum that holds itself (`enum Node { Num(int value) Add(Node left, Node right) }`) plus `match` - tested |
| Lists of tokens and nodes, symbol tables | **Works** | `List<T>`, `Map<string, T>` |
| Reading source, writing C | **Works** | `readText`, `writeText`; `List<string>` + `join` builds the output fast |
| Program arguments, exit code | **Works** | `main(string... args)`, `exit(n)` |
| Characters of the source | **Works** | `s[i]`, `len`, `charCode` |
| Reporting errors | **Works** | `T, Error function`, `try` / `catch` |
| **Calling GCC** | **Missing** | No way to run another program. See gap A |
| **State shared across functions** | **Missing** | There are no module-level variables (`int counter = 0` at the top is a parse error). See gap B |
| **A function changing what it is given** | **By design, copies** | Lists and structs are passed as **copies**: `push(xs)` and `step(lexer)` leave the caller's values unchanged (tested). See gap B |
| Methods on own structs | Missing (Task 32.1) | Plain functions instead (`advance(lexer)`) - workable |
| Fast string building | Missing (Task 29) | `List<string>` + `join` instead - workable |

## 4. Gaps to decide before 28.2

**A. Calling GCC (needed by 28.6, the driver).** The options:
1. A small builtin: `int run(string command)` runs a program and returns its exit code
   (std layer only). This is my recommendation: it's small, and the driver needs it.
2. No builtin: `compiler.exe` writes the C file, and a `.bat` / shell script calls GCC
   afterwards.

**B. Shared state without globals or references.** A lexer and a parser carry state: the
position, the tokens, the errors. In Fusion today that state must be **passed in and
returned**:

```fusion
Parser p = advance(p)        // returns the updated parser; the old copy is dropped
```

This works, but each call copies the whole struct, including its token list, so long files
get slow. The options:
1. **Live with it** for the test run. The examples are small, so the speed is fine.
2. Keep large lists out of the struct: tokens as a separate `List<Token>` parameter that
   is only read, plus a small struct for the changing state (the position). This is my
   recommendation: it is fast enough and needs no new feature.
3. Add a small feature first: module-level variables, or `ref` parameters. That would be
   new design work, belonging to Phase 2.

**C. The C run-time library.** The Python compiler writes the run-time (strings, lists,
maps, errors, checks) into every C file it generates: `hello_world.c` is 1,635 lines. The Fusion
compiler shouldn't have to rebuild that text itself. My recommendation: put the run-time in
one shared file, such as `runtime/fusion_runtime.h`, which the Python compiler writes once.
The Fusion compiler then only outputs `#include "fusion_runtime.h"` and the program's own
code. 28.7 compares what the programs **print**, so the C text may differ.

---

## Recommendation for Task 28

- **The test run targets tier 1** (18 programs). Tiers 2 and 3 follow as extensions, in
  order, once tier 1 passes. Each tier is a clear checkpoint.
- Gap A: the `run(command)` builtin. Gap B: option 2. Gap C: a shared run-time header.
- The compiler is written in one block style (braces), as one module per stage: `lexer`,
  `parser`, `checker`, `codegen`, `main`.
