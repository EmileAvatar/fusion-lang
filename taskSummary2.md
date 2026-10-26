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

## TASK 44: Lessons from the self-hosting test run - PLAN (awaiting approval, 2026-10-26)

The six suggestions of task/selfhost_report.md, so that writing Fusion (and the next
self-hosting stage, Task 35) is easier. Ordered from smallest and safest to largest. Each
lands with tests, a `SYNTAX_REFERENCE.md` example (Rule 4), spec and grammar notes. The
Fusion-written lexer (selfhost/) follows any lexer change, because tests compare its tokens
with the Python lexer's.

**44.3 A newline inside `(` or `[` continues the line** (smallest)
- Inside parentheses and brackets, the lexer emits no NEWLINE, INDENT or DEDENT, so long
  calls and list literals can be written over several lines:
  ```fusion
  print("{@1} {@2}",
        first,
        second)
  ```
- Braces `{` stay as they are, because they open blocks.
- The same change goes into selfhost/lexer, and the token comparison must stay identical.

**44.5 `_` for an unused field; `end` and `var` become ordinary names**
- `case Function(name, _, _, body, _)`: `_` binds nothing, and may be used any number of
  times.
- `End` (capital) stays the block closer. Lowercase `end` becomes an ordinary name, except
  directly before a block keyword (`end function` keeps working, though no file uses it).
  `var` becomes an ordinary name until type inference is built, when `var x = ...` can be
  recognised by its shape.
- Checked: no example or test uses lowercase `end` to close a block, or `var`.

**44.6 Fast `text[i]` for any string**
- Today, one non-ASCII character makes every `text[i]` count from the start of the string
  (28.1.2: 52 s instead of 0.03 s).
- The fix: a string value remembers where it was last indexed (two hidden fields: character
  index and byte offset). The next `text[i]` on the same variable continues from there,
  forwards or backwards, so a loop over the string is fast again.
- Measured with the 28.1.2 lexer prototype, before and after. Every leak check and test must
  still pass. `runtime/fusion_runtime.h` is regenerated (`check.py --runtime`).

**44.1 Module-level variables** (the biggest gain)
- A variable or constant declared outside any function:
  ```fusion
  const int MAX_TOKENS = 10000          // a module constant
  int errorCount = 0                    // a module variable
  public string version = "1.0"         // other modules can read it
  ```
- Private to its module unless `public`.
- Values are set in the order written, before `main` runs. Strings and lists are freed when
  the program ends (the leak check covers them).
- Note for the concurrency design: a module variable shared between threads is exactly what
  `service` exists for (Task 42). Until threads exist this is simple single-thread state.

**44.2 Calling any function as a method** (instead of functions inside structs)
- A function whose first parameter is a struct can be called on it:
  `p.moved(1, 2)` means `moved(p, 1, 2)`. Built-in types already work this way (18.3.7).
- Structs stay values only (no functions inside them - the default you set), so nothing
  about structs changes. Functions inside structs remain 32.1, behind its setting.
- A method gets a copy, as any function does: `p = p.moved(1, 2)`. Changing the caller's
  struct in place needs references, which is a later decision.

**44.4 An `Error` return type distinct from "can fail"** (smallest gain - recommend: defer)
- In practice the workaround (`return Error(message(...))`) was short and clear. A new
  spelling would add a second meaning to a word people already know.
- Recommendation: mark it postponed, and revisit if it comes up again.

**Order:** 44.3, 44.5, 44.6, 44.1, 44.2. Each is shipped on its own.

**Decisions for the user:**
1. Approve the order, and the five items above?
2. 44.1: should module-level variables be a `fusion.toml` setting (`[modules] globals`,
   allowed by default), or always allowed?
3. 44.2: calling any function as a method (recommended), instead of functions inside
   structs?
4. 44.4: postpone it?

---

## TASK 28: Self-hosting phase 1 - the test run - COMPLETE (2026-10-26)

A Fusion compiler written in Fusion (selfhost/, ~3,500 lines) builds all 18 tier 1 programs;
each prints what the Python-built one prints, leak-free (`python check.py --selfhost`).
Report: task/selfhost_report.md. Plans and notes: task/taskSummaryArchive.md.

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
- Slice 3 done: string ownership (fresh vs borrowed, freed in statement expressions - no
  temporaries), floats / chars / bools, format(), default and named arguments - 12 of 18
- Slice 4 done: fixed arrays, function values / types, lambdas (lifted to C functions,
  named by line + a hash of their text) - 15 of 18
- Slice 5 done: structs, equality across types - **all 18 tier 1 programs print the same,
  leak-free**: 28.3-28.6 done
- 28.7 done: check.py --selfhost - 18/18 the same; 28.8 done: task/selfhost_report.md
- **Task 28 complete - Phase 1 complete** (plan archived)
- The report's six suggestions scheduled as FEATURES.md Task 44 (Phase 2)
- User picked Task 44 ("so that it's easier going forward"); plan written
- **Next Action:** user approves the Task 44 plan and answers decisions 1-4
