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

## TASK 26: Error handling - ACTIVE (plan approved 2026-10-16)

**User decisions already made (2026-10-09, backlog):** Go-style error returns *only for
returning an error from a function* (`Spaceship, Error function loadShip(...)`, then
`Spaceship ship, Error err = loadShip(...)` and a simple `if err`); `try` / `catch` /
`finally` / `throw` / `Error`; both on by default, both can be turned off per project in
fusion.toml; the two are complementary.

#### What it looks like (proposal)
```text
Ship, Error function loadShip(string file)
    if not fileExists(file)
        return Error("No such file: {file}")      // fails: the Ship part gets its default
    return Ship(readText(file))                    // succeeds: no error

void function main()
    Ship ship, Error err = loadShip("ship.dat")    // capture: check it yourself
    if err                                         // true when there is an error
        print("Can't load: {@1} ({@2})", err.message, err.where)
        return

    string text, Error e = readText("x.txt")      // capture works on any call (Q2)

    try
        Ship s = loadShip("a.dat")                 // not captured: an error goes to catch
        int n = toInt("12x")                       // a built-in's error too (Q3)
    catch err
        print("failed: {@1}", err.message)
        throw err                                  // or pass it on
    finally
        print("always runs")

    throw Error("Bad state", 42)                   // message + an optional code
```

#### The model
- **`Error`** - a built-in value: `message` (string), `code` (int, default 0), `where`
  ("main.fusion:12", filled in where it was made). `Error("msg")`, `Error("msg", 404)`. A
  captured `err` with no error has an empty message; `if err` / `not err` test whether there
  is one (the one place a non-bool is a condition - user decision "a simple if err check")
- **A function that can fail** returns `T, Error` (or `Error` alone for a void one): `return
  Error(...)` fails, `return value` succeeds. `throw` works in any function
- **An error nobody captures bubbles up** (spec): out of the function, to the caller's
  `catch` if inside `try`, else further up; at `main` the program stops with the message,
  exactly as a run-time error does today (Q1)
- **No setjmp/longjmp** - C would skip the automatic cleanup and the leak check would fail.
  Instead explicit propagation, like Go / Zig / Rust's `?`: a failing call sets the current
  error; the generated C checks right after each call that can fail and jumps to the catch,
  or frees the function's values and returns. The checker works out which functions can
  fail, so calls that can't fail cost nothing
- **Config:** `[errors] returns = true`, `exceptions = true` - turning one off makes that
  syntax a compile error (with `exceptions = false`, an error nobody captures stops the
  program, as today)

#### Sub-tasks
- **26.1** this plan
- 26.2 DONE (Error and error returns) - detail archived
- 26.3 DONE (try / catch / finally / throw) - detail archived
- 26.4 DONE (every built-in failure catchable) - detail archived
- 26.5 DONE (config switches) - detail archived
- **26.6 Example + docs** - SYNTAX_REFERENCE section, an example program (catch an error,
  and show one nobody catches - was 16.5), spec "Error Handling" as built, fusion.ebnf
- Every part: tests, all programs under the leak check (every error path must free)

#### Not in this task
Typed catches (`catch NetworkError e`) - wait for classes (32) or a later enum-based
design; stack traces; `err.cause` chains

#### Decisions (user, 2026-10-16) - plan approved
1. Bubble up: capturing the error at a call is optional ("the err is optional to catch the
   error from the specific function"); with no err it bubbles up until there is a catch;
   at main the program stops with the message
2. The capture form works on any call - it also catches what a throwing function or
   built-in throws
3. **All** built-in failures become catchable (not only the expected ones) - so 26.4 covers
   every run-time error in the C runtime; an uncaught one stops the program as today
4. One catch-all `catch err` in this task; typed catches later

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
- **Next Action:** 26.6 example + docs
