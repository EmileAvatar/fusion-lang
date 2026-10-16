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

#### Sub-tasks (updated 2026-10-16 after the user's review)
- 26.7 DONE (implicit errors) - detail archived
- 26.8 DONE (capture without a type) - detail archived
- 26.9 DONE (custom error types) - detail archived
- **26.10 Typed capture, `err.kind`, match on error types** - `Ship s, FileError err = f()`
  captures any error (its own fields empty unless it is a FileError); `err.kind` is the
  type name ("FileError") for logs and printing; `match err` with **error type names as
  cases** - `case FileError` also matches its subtypes (FileNotFound), and inside the case
  err is that type, so its own fields can be read; misspelled names are compile errors
- **26.11 Typed catch** (user: now, for a working sample) - `catch FileError e` ...
  `catch e`: first match wins, a parent type catches its subtypes, an untyped `catch e`
  last; an error no catch matches goes on (through finally)
- **26.12 Built-in error types** - the list below; built-in failures raise them; new
  checks for failures that aren't errors yet (integer division by zero)
- **26.13 Docs + examples** - SYNTAX_REFERENCE sections, examples/errors_demo extended
  (custom errors, match on error types, typed catch), spec "Error Handling", fusion.ebnf
- **No central ERROR enum** (user agreed): one closed list can't grow when a module adds
  its own errors; each error type is its own kind, with an optional default message
- Every part: tests under the leak check

#### Built-in error types (26.12) - a proposal for the user to review
Every one is an `Error`; a parent catches its children (`catch LookupError e` catches both
IndexError and KeyError). "today" = raised as a plain Error now; "NEW" = not an error yet.

```text
Error
 +- ArithmeticError                     doing the math is impossible
 |   +- DivideByZeroError     NEW       7 / 0 and 7 % 0 on whole numbers - today the
 |   |                                  program crashes (C stops it); 7.0 / 0 is infinity
 |   +- OverflowError         later     a whole number too big for int (2147483647 + 1
 |                                      wraps silently today) - Task 27.2 decides
 +- FormatError                         text in the wrong shape
 |   +- NumberFormatError     today     toInt("12x"), toFloat, parseInt, fromHex
 |   +- PatternError          today     formatNumber with a bad pattern
 |   +- HexFormatError        today     hexToBytes / hexToRaw: not hex, odd digit count
 |   +- TextEncodingError     today     bytes that aren't valid text (toString, readText
 |                                      of a binary file, hexToBytes)
 +- ValueError                          a value outside what's allowed
 |   +- RangeError            today     toByte(300), fromCharCode(-5), base not 2-36,
 |   |                                  setInt16 too big, a negative count / width
 |   |                                  (left, right, repeat, padLeft, truncate, mask ...)
 |   +- UnknownValueError     today     Color.fromString("Pink")
 +- LookupError                         asking for something that isn't there
 |   +- IndexError            today     s[9], xs[9], b[9], substring / slice / insert /
 |   |                                  removeAt / remove outside the range, getInt room;
 |   |                                  fixed arrays a[9]: NEW with Task 27.1
 |   +- KeyError              today     m["missing"]
 +- FileError (path)                    the file system said no
 |   +- FileNotFoundError     today     readText / readBytes / readLines of a missing file
 |   +- PermissionError       today     not allowed to open / write / delete
 |   +- FileReadError         today     reading failed part way
 |   +- FileWriteError        today     writing failed (disk full)
 |   +- FileTooLargeError     today     a file over 2 GB
 |   +- DeleteError           today     deleteFile failed (missing, in use)
 +- LimitError                          bigger than Fusion allows
     +- StringTooLongError    today     a string over [strings] max_length
     +- ResultTooLargeError   today     a result over 2 GB (repeat, join, replace ...)

Not catchable - the program stops at once, nothing can recover:
     out of memory, a List past 536,870,911 elements,
     endless recursion (stack overflow - today a crash; a depth check is a later task)

Later, when the feature exists: NullError (Task 30), NetworkError / TimeoutError (a net
module), ParseError (JSON / data modules), CancelledError (threads), AssertionError
(an `assert` statement), NotSupportedError (a backend that can't do something)
```

#### Decisions (user, 2026-10-16)
1. Declared with `error FileError` + fields; `error FileNotFound : FileError` extends one
2. `Ship s, FileError err = f()` captures **any** error: err is a FileError only when it
   is one - otherwise its own fields are empty. `err.kind` gives the error's type name
   ("FileError", "Error", "IndexError") - user: yes; plus `match err` with error type names
   as cases (compiler-checked, subtype-aware)
3. Typed catches (`catch FileError e`) - user changed this: **now**, so there is a
   working sample (26.11)
5. An error type may give a default message; no central ERROR enum (user agreed)
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
- Plan updated (default message, match on error types, typed catch now, built-in
  error type list)
- 26.7 done
- 26.8 done
- 26.9 done
- **Next Action:** 26.10 err.kind and match on error types
