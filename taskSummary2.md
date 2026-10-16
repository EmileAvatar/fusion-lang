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

## TASK 26 (part 2): implicit errors, untyped capture, custom error types - PLAN (decisions made, awaiting "proceed")

**User request (2026-10-16):** the `, Error` in a signature is optional - any function can
give an error, writing it just tells the compiler (and readers) that this one can. The
capture variable's type is optional too: it is always Error or a subtype. Custom errors are
subtypes of Error with extra fields, so modules (files, databases, a graphics engine) can
have their own specific errors.

#### What it looks like
```text
Ship, Error function loadShip(string name)   // marked: this function can give an error
Ship function loadShip(string name)          // the same function - `, Error` is optional
    if name == ""
        return Error("No name given")         // allowed in any function now
    ...

Ship s = loadShip("")                        // an error bubbles up until something catches it
Ship s, err = loadShip("")                   // capture: err is an Error (any name works)
Ship s, err24 = loadShip("")
Ship s, Error err = loadShip("")             // the type may still be written
Ship s, FileError err = loadShip("")         // only a FileError is captured (see Q2)

error FileError                              // a custom error (syntax: Q1)
    string path
    int attempts = 1

throw FileError("Can't open", path = "ship.dat")   // message first, then its own fields
print("{@1} {@2}", err.message, err.path)     // message / code / where + its own fields

try
    ...
catch FileError e                            // typed catches, first match wins (Q3)
    print("file: {e.path}")
catch e                                      // any other error
    print(e.message)
```

#### Sub-tasks
- **26.7 Implicit errors** - `return Error(...)` in any function (it then can fail, as
  with throw); `T, Error function` stays valid as a marker, shown by `--interface`; a
  function marked `, Error` that can never fail gets a warning. `[errors] returns` still
  switches Go-style returns / capturing off
- **26.8 Capture without a type** - `Ship s, err = f()`; `Ship s, Error err` still works.
  A call with no value keeps `Error err = save(s)` (a bare `err = save(s)` would read as an
  assignment)
- **26.9 Custom error types** - declare one (Q1) with extra fields; built like a struct
  (message first, code optional, then its fields - named arguments too); `where` filled in
  as for Error; every Error field plus its own; `throw` / `return` it; printing shows the
  message; a custom error can extend another custom error (FileNotFound -> FileError ->
  Error). In C: the error carries a kind number and its extra fields on the heap, with
  copy / free per kind (leak-checked)
- **26.10 Typed capture** - `Ship s, FileError err = f()` captures any error (decision 2);
  `err.kind` - the error's type name. (Typed catches: later)
- **26.11 Built-in failures get their own types (Q4)** - e.g. IndexError (index out of
  range), KeyError (missing Map key), FormatError (text that isn't a number, a bad
  pattern), FileError (with `path`) - all subtypes of Error, so `catch e` still catches
  everything
- **26.12 Docs + examples** - SYNTAX_REFERENCE sections, examples/errors_demo extended,
  spec "Error Handling", fusion.ebnf
- Every part: tests under the leak check

#### Decisions (user, 2026-10-16)
1. Declared with `error FileError` + fields; `error FileNotFound : FileError` extends one
2. `Ship s, FileError err = f()` captures **any** error: err is a FileError only when it
   is one - otherwise its own fields are empty. Proposed: `err.kind` gives the error's
   type name ("FileError", "Error", "IndexError") to tell them apart
3. Typed catches (`catch FileError e`) come later - one `catch e` for now
4. Built-in failures get their own types now: IndexError, KeyError, FormatError,
   FileError (with `path`)

---

## TASK 26: Error handling - COMPLETE (2026-10-16)

Error values, functions that can fail, capturing, bubbling, try / catch / finally / throw,
every built-in failure catchable, `[errors]` switches, examples/errors_demo. Plan and notes:
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
- **Next Action:** user to say proceed, then 26.7
