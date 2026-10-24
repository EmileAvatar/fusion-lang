# Fusion - Working File (active task plans)

**What this file is (Task 22, 2026-10-09):** only the task being worked on now - its detailed
plan, the next action, and the latest session note. Keep it small: it is read often.
- Status of every task and feature: `FEATURES.md` (`[ ]` open, `[DONE]`, `[POSTPONED to ...]`)
- Finished tasks and sub-tasks, old sessions: `task/taskSummaryArchive.md` (verbatim)
- Not-started task write-ups: `task/taskBacklog.md` (verbatim)
- Rules (plan first, no emojis in code, ...): `CLAUDE.md`

---

## Current status (2026-10-11)

**Task 18 (core language foundation) is COMPLETE** and archived (plans, notes and the
FEATURES.md detail are in `task/taskSummaryArchive.md`). Task 10.2 is met.

---

## Current plan: the roadmap (FEATURES.md, renumbered 2026-10-11)

Done tasks keep their numbers; open tasks were renumbered from 25 into three phases (the
approved plan is archived). Phase 1 = 25 enums, 26 error handling, 27 semantic contract and
safety (bounds checks, the three-block-style check), 28 self-hosting test run.

---

## TASK 28: Self-hosting phase 1 - the test run - ACTIVE (2026-10-24)

Done in steps (user). 28.1 done: `task/selfhost_subset.md` - the examples fall into three
tiers; gaps A (calling GCC), B (state without globals), C (the C run-time).

**The test run targets tier 1** - a milestone that confirms the approach works, not the
whole language (user, 2026-10-24). Tiers 2 and 3 come later.

### 28.1 - COMPLETE (2026-10-24)

28.1.1 run(command), 28.1.2 shared state measured, 28.1.3 shared C run-time
(runtime/fusion_runtime.h), 28.1.4 files/Builtins.md. Plan and results:
`task/taskSummaryArchive.md`, `task/selfhost_subset.md`.

### Plan for 28.2-28.8: the compiler in Fusion - APPROVED (2026-10-24)

User's answers: (1) one walk for checking and generating, for now; (2) the C it writes must
pass the leak check; (3) any run-time error ends the program (uncaught) - OK for now;
(4) the compiler's source uses braces, for now; (5) 28.1.5 first.

**Goal:** `selfhost.exe`, a Fusion compiler written in Fusion and built by the Python
compiler, compiles the **18 tier 1 programs**. Each program it builds prints exactly what
the Python-built one prints, with the same exit code. That is the test run. The Python
compiler stays the real compiler.

**Checked before planning (2026-10-24):**
- A syntax tree works in today's Fusion: an enum whose variants hold lists of themselves
  (`Block(List<Node> statements)`, `Call(string callee, List<Node> args)`), `match` over it,
  a `Map<string, Symbol>`, and a 20,000-node tree, with no leaks.
- The Python compiler writes 996 lines of program C in total for the 18 programs (with the
  shared header), so the C the Fusion compiler must write is small.
- **Gap found:** a string can't contain a literal `{` (it starts an interpolation, and
  `"{ "` is an error). The only way today is `"\u007B"`, and generated C is full of braces.

**28.1.5 (first, small): `\{` and `\}` escapes in strings.** `"int main() \{"` gives
`int main() {`. A lexer change, plus tests, a `SYNTAX_REFERENCE.md` example, and spec and
grammar notes.

**Layout** (one module per folder, as `import` already works):

```text
selfhost/
  main.fusion            28.6 the driver
  lexer/lexer.fusion     28.2 tokens
  parser/ast.fusion      28.3 the tree: enum Node, enum TypeRef
  parser/parser.fusion   28.3
  codegen/codegen.fusion 28.4 + 28.5 checking and C generation
```

**28.2 Lexer.**
- Reads the source as `bytes` (the 28.1.2 rule).
- Makes the tokens for tier 1: names, keywords, numbers (including hex, binary, octal and
  `_`), strings (with their `{name}` / `{@1}` parts), chars, operators, comments.
- Handles all three block styles: indentation (INDENT / DEDENT), braces, and
  `End function`.
- Verified first, on its own: `selfhost.exe --tokens file.fusion` prints the tokens one per
  line, and a test compares that with the Python lexer's tokens for all 18 programs.

**28.3 Parser.** It builds the tree for tier 1:
- functions (block bodies and `: expr`), parameters with defaults, structs (field defaults,
  nesting), `const`;
- `if` / `else if` / `else`, `while`, `for` over `range()` and arrays, `break`,
  `continue`, `return`, assignment to `a.b.c` and `a[i]`;
- every tier 1 operator, calls, named arguments, struct construction, array literals,
  interpolation and lambdas.

The pattern: the tokens are a read-only parameter, and each function returns a small
result `{Node node, int pos}`. A syntax error is an `Error`, with the file, line and
column.

**28.4 + 28.5 Checker and C generator: one walk over the tree** (my recommendation). Each
expression comes back as `{string code, TypeRef type}`, so the types are worked out where
they are needed. The C must know whether `+` joins strings or adds ints, and how `print`
formats each value. The checks tier 1 needs:
- names exist;
- types match (assignments, arguments, returns, conditions);
- the number of arguments, and named and default arguments.

The programs are all valid, so these checks catch the compiler's own mistakes too. A
separate checker pass, like the Python compiler's, can come in Phase 2.

The C it writes follows the Python compiler's output for the same program, with the
shared header:
- struct typedefs, with free helpers for structs holding strings;
- checked `+ - * / %` and array indexes (`fusion_add_int`, `fusion_index`);
- `printf` formats like the Python compiler's, so floats print identically;
- lambdas lifted to functions, and function-type typedefs;
- defaults and named arguments resolved at the call.

**Run-time errors (a simplification):** tier 1 has no `try`, so any run-time error ends
the program with the same message and exit code as the Python-built one (the error is
uncaught at main). There are no `goto` chains for catching.

**Memory:** strings are freed as the Python compiler frees them (temporaries after the
statement, variables at the end of their block). `python check.py --selfhost` runs the
programs under the leak check too (decision 2 below).

**28.6 Driver.** `selfhost.exe program.fusion [--runtime DIR] [--tokens]`:
- reads the file;
- lexes, parses and generates;
- writes `program.c`;
- runs `gcc -I DIR program.c -o program.exe -lm` with `run()`;
- exits 0 on success, or prints the error (file:line:col) and exits 1.

`DIR` defaults to `runtime` (run from the repo root).

**28.7 Verify: `python check.py --selfhost`.**
1. Build `selfhost/main.fusion` with the Python compiler.
2. For each of the 18 programs, build it with both compilers, run both, and compare the
   output and the exit code. Also run under the leak check.
3. Report `n/18 the same`.

It is a separate option at first, because it is slow. Once it passes it can join
`python check.py`.

**28.8 Report:** `task/selfhost_report.md` - what was missing or awkward in Fusion while
writing it, the sizes and the timings. This feeds Phase 2.

**How it is built - vertical slices.**
1. `hello_world` goes through all four stages first.
2. Then one program at a time, in order of difficulty: factorial, max_three, fizzbuzz,
   sum_array, const_demo, syntax_strings, syntax_interpolation,
   syntax_variables_and_control_flow, syntax_functions_and_blocks, arrays_demo, calculator,
   syntax_defaults_and_named_args, syntax_lambdas, functions_demo, syntax_equality,
   syntax_structs, structs_demo.
3. Each one adds what it needs, and is shipped once `--selfhost` passes for it.

`FEATURES.md` lines 28.2-28.6 are marked done when tier 1 is complete.

**Size estimate:** about 3,500-5,000 lines of Fusion, over several sessions.

**Language gaps found along the way:** a workaround first. Each gap goes into the 28.8
report. A gap that blocks progress is raised with the user before anything is added to
the language.

**Decisions for the user:**
1. Checking and generating in **one walk** (recommended) or as two passes?
2. Must the C it writes pass the **leak check**? Recommended: yes, done as the last step
   for each program.
3. The run-time error simplification (any error ends the program, as uncaught): OK for
   the test run?
4. The block style the compiler's own source is written in: **braces** (recommended -
   easiest to read when there are many nested blocks), indentation, or `End`?
5. Start with **28.1.5** (`\{` / `\}` escapes)?


---

## TASK 23.9: Fusion_showcase.fusion - COMPLETE (2026-10-23)

files/showcase/Fusion_showcase.fusion + fusion.toml: every feature tagged [built] /
[designed] / [idea] / [rejected] with a one-line description. Plan: task/taskSummaryArchive.md.

---

## TASK 27: Semantic contract and safety - COMPLETE (2026-10-17)

Bounds checks, three block styles, overflow / wrapping / unsafe mode, endless recursion,
interaction tests, changing a collection while looping, the contract (spec "The Semantic
Contract"), int to float ([numbers] auto_widening, 27.2f). Plan: task/taskSummaryArchive.md.

---

## TASK 26: Error handling - COMPLETE (2026-10-16)

Error values, functions that can fail, capturing, bubbling, try / catch / finally / throw,
every built-in failure catchable, `[errors]` switches, examples/errors_demo. Part 2 (26.7-26.13):
implicit errors, untyped capture, custom error types, err.kind, match on error types, typed
catch, Fusion's own error types. Plan and notes:
`task/taskSummaryArchive.md`.

---

## TASK 25: Enums and tagged unions - COMPLETE (2026-10-12)

Plain enums, `match`, enums with data, enums holding themselves, and the expressions
example. Plan and notes: `task/taskSummaryArchive.md`.

---

## TASK 22 (housekeeping) - ACTIVE (user: "do the housekeeping first and the ascii issue first")

Kept under Task 22 until the renumbering is approved.

- 22.8-22.11 DONE (tools; detail archived)
- 16.1 DONE - examples/control_flow
- 22.7a DONE - README reduced to goals + pointers
- 22.7b DONE - spec status lines (Task 22 complete)
- Each one: FEATURES.md line, `task/automation.md` row marked Automated, check, commit

---

## Working Notes

### Session 31 (2026-10-09 .. 10-11 - 18.3.5 to 18.5.7)
- Done: 18.3.5 equality, 18.3.5b bool printing, 18.3.6 string library (a-f, masking design
  and build), 18.3.7 type classes / methods, 18.3.8 bytes, 18.4 modules (1-4), 23.7 / 23.8
  (wait at exit, --headless, .fusion preview), Task 24 added (editor support), 18.5 (1-7)
- User preferences saved to memory: as little typing as possible; never change values
  silently
- Task 18 archived (FEATURES.md detail too); 3 automation candidates added
- 22.8-22.11 done: check.py --fix-ascii / --ship / --example, tools/patch.py
- 16.1 done: examples/control_flow; map literals noticed missing (FEATURES.md Later)
- 22.7a done: README is goals + pointers (554 -> 321 lines); 22.7b waits for the renumbering
- User answered: numbers from 25, classes / generics in Phase 2. ChatGPT review read:
  fixed arrays are not bounds-checked (segfault) -> new Task 27 "semantic contract and safety"
- FEATURES.md reorganized into phases and renumbered (22.12); the user asked for 27.1
  (bounds checks for fixed arrays) and 27.4 (one app in 3 block styles -> identical C)
- 2026-10-12: 22.7b done - a status line under each of the spec's 31 major sections; Task 22
  complete
- Task 25 plan approved (all 4 recommended answers)
- 25.2 plain enums and 25.3 `match` done
- 25.4 enums with data done
- 25.5 enums holding themselves done
- Task 25 complete (25.6: examples/expressions)
- Task 26 plan approved (bubble up, capture any call, all built-ins catchable, one catch)
- 26.2 done
- 26.3 done
- 26.4 done
- 26.5 done
- Task 26 complete (26.6: examples/errors_demo)
- Task 26 part 2 planned, 4 questions answered
- Plan updated (default message, match on error types, typed catch now, built-in
  error type list)
- 26.7 done
- 26.8 done
- 26.9 done
- 26.10 done
- 26.11 done
- 26.12 done
- Task 26 part 2 complete (26.7-26.13)
- Task 27 plan approved (bounds always; wrapAdd functions; stack use + max_call_depth; unchecked blocks)
- 27.1 done
- 27.5 and 27.4 done
- 27.2b and 27.2d done
- 27.2c done
- 27.3 done (found: changing a list while looping over it skips elements)
- Task 27 complete; 27.2f done ([numbers] auto_widening, default false)
- 23.9 done: files/showcase (Fusion_showcase.fusion + fusion.toml); user answered: files/showcase/,
  tags built / designed / idea / rejected + one-line description each
- 28.1 done: the subset measured (task/selfhost_subset.md, tools/example_subset.py)
- User: tier 1 is the test-run target; 28.1.1-28.1.3 sub-tasks; 28.1.4 builtins list proposed
- Plan approved (user: 28.1.4, then 28.1.1). 28.1.4 done: files/Builtins.md, generated and
  checked
- 28.1.1 done: run(command), ProcessError, tests, SYNTAX_REFERENCE example
- 28.1.2 done: measured (selfhost/prototype/) - pattern B over bytes is fast; no compiler
  change needed; slow string indexing found (FEATURES.md Later)
- 28.1.3 done: runtime/fusion_runtime.h; all 45 examples print the same with it
- 28.1 complete (plan archived)
- 28.2-28.8 planned (taskSummary2.md); gap found: no literal { in strings -> 28.1.5
- Plan approved (one walk, leak-free, errors end the program, braces, 28.1.5 first)
- 28.1.5 done: \{ and \} escapes
- User moved the old task-1.x-4.x files to task/archive/ (links updated)
- 28.2 done: the lexer in Fusion matches the Python lexer on all 53 example files; a
  Python compiler bug found and fixed (bare return in void main)
- Slice 1 done: hello_world compiled by the Fusion-written compiler - its C is the Python
  compiler's line for line, the program passes the leak check. Gaps logged in
  task/selfhost_report.md
- Slice 2 done: the parser is complete for tier 1 (all 18 programs parse; --ast); the
  code generator checks types in the same walk; 8 of 18 programs print the same as the
  Python-built ones, leak-free
- **Next Action:** slice 3 - string values and printing every type (syntax_strings,
  syntax_interpolation, syntax_variables_and_control_flow, syntax_defaults_and_named_args)
