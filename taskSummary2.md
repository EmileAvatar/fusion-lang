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

### Plan for 28.1.1-28.1.4 - PLAN (awaiting approval, 2026-10-24)

**28.1.1 `run(command)` - run another program**
- `int run(string command)`: runs the command through the system shell (`cmd /c` on
  Windows, `/bin/sh -c` elsewhere - C's `system()`), **waits** until it ends, and returns
  its exit code.
- If the shell itself can't be started, that is a new built-in error type,
  **`ProcessError`** (an Error subtype, added at the end of the list so the existing kind
  numbers don't change). A program that runs and fails is not an error: its exit code is
  returned. (A command that isn't found gives the shell's own code: 9009 on Windows, 127
  elsewhere.)
- Layer: **std** only (not alloc / core). Security note: running programs is a capability;
  Task 39 will be able to restrict it per project.
- Not waiting: `run("start notepad")` on Windows. A separate `start(command)` and
  capturing the output (`runOutput`) are left for later.
- **Tests:**
  - unit tests: the type, the layer, and the error type;
  - end-to-end tests: `run("exit 3")` returns 3;
  - run a compiled example (`hello_world.exe --headless`);
  - **compile and run from Fusion:** `run("python main.py examples/hello_world.fusion")`,
    then run the exe it made;
  - by hand: `run("notepad")` opens Notepad and waits until it is closed (a window can't
    be tested automatically).
- Example in `SYNTAX_REFERENCE.md` (Rule 4), using `run("echo hello")`, which works on
  every system; spec and grammar notes.

**28.1.2 Shared state - measure, then decide**
- **Corrected while building 28.1.4:** a parameter the function only **reads** is already
  passed without a copy (`fu_count(fusion_list_string xs) { return xs.len; }`). Only a
  parameter the function **changes** is copied when it starts. So handing the token list
  to every parser function is cheap already, and no compiler change is needed unless the
  measurement says otherwise.
- A small prototype first: a lexer in Fusion tokenizing a large file (about 5,000 lines),
  timed before and after, so the numbers decide.
- The pattern for the compiler's code: a small struct for the changing state (the
  position, the errors), returned from functions; the token list as a read-only parameter.

**28.1.3 The C run-time as a shared file**
- Today every generated C file contains the whole run-time (`hello_world.c`: 1,635 lines).
- Part of it is always the same (strings, errors, checks, files). Part of it is generated
  for the program's own types: `List<T>` helpers, and copy / free functions for structs.
- Step 1: find the boundary in the C generator, and measure how much is fixed.
- Step 2: the Python compiler writes the fixed part to `runtime/fusion_runtime.h`, and
  `#include`s it, or keeps writing it inline, whichever keeps the tests simplest.
- The Fusion compiler then writes only the include, the type helpers its program needs,
  and the program. For tier 1 the only type helpers are structs and arrays.

**28.1.4 A list of the built-in functions, kept in step automatically** (user question)
- There is no single list today. `SYNTAX_REFERENCE.md` shows examples, and the spec
  describes the library, but neither is complete.
- Correction to 28.1: the compiler has **94** built-in functions (the "about 110" counted
  struct constructions as calls). On top of these come the list and map methods.
- Proposed: `files/Builtins.md`, **generated from the compiler itself**. Each entry has:
  - the name;
  - the parameters and return type;
  - the layer (core / alloc / std);
  - whether it can fail;
  - the list and map methods.

  `check.py` gets a check that the file matches the compiler (like the reference check),
  so it updates whenever a builtin is added.

**Order:** 28.1.4 (small) and 28.1.1, then 28.1.2, then 28.1.3. After those comes the plan
for 28.2-28.8.

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
- **Next Action:** 28.1.2 shared state (measure with a lexer prototype)
