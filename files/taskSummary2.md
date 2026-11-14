# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## TASK 48: Ownership - what is left - PLAN (2026-11-14), waiting for approval

Settings: 48.11 adds them - names and meaning asked first (question 1 below); the rest none

Done already (48.1-48.3, 48.9): moving, borrowing, byVal / byRef / readonly at the call, "move" the default.
In the order to build:

- 48.0 The rules R1-R8: written (files/Ownership.md) and built by 48.1-48.3 -> mark DONE (R6 `shared`
  postponed - 48.5; R7 threads - Task 42)
- 48.10 R4 relaxed (D.123): while a borrow changes a value, its owner may still be read - remove the
  "'fleet' can't be read while 'first' ... changes it" error; changing the owner another way stays an
  error. Tests changed / added; Ownership.md R4 and the fusion-ownership skill updated
- 48.12 Storing `this` shares the object (D.103) - checked today: works (one car in two Lists, a change
  through one seen through the other, freed with no leak). Add the tests that keep it so: shared,
  freed when the last holder lets go (leak check), with and without null checks (Rule 4b)
- 48.8 Release the `Unique` keyword (D.080): no `Unique<T>`, no `.move()` - `Unique` becomes an ordinary
  name; `Shared` / `Weak` stay reserved (Task 38). Spec 200, Decisions, a test
- 48.7 Examples: files/SYNTAX_REFERENCE.md already shows moves, byVal / byRef (lines 630-680) - add the
  borrow rules (the owner frozen while a borrow is used, R4 relaxed) and storing `this`; null-check
  tests for moves and borrows both ways (Rule 4b)
- 48.11 A setting per borrow rule (D.124) - after question 1
- 48.4 `--interface` shows readonly results - needs readonly results (Task 50, D.110) -> POSTPONED to 50
- 48.6 Counting removed where a move proves one owner (the speed gain; covers 38.2) - question 2

Question 1 (48.11 - to OpenQuestions as Q.014 if not answered here):
- One owner: `[memory] assignment` = "move" / "share" (built)
- One writer (R4): `[memory] oneWriter = true` - false lets two names change one object at once (as C)
- A borrow never outlives its owner (R5): `[memory] borrowsStay = true` - false lets a borrow be stored
  or returned: the object is then counted (shared) instead of an error
- A: these two booleans; B: one `[memory] borrowRules = "strict" | "relaxed"`; C: postpone until a need

Question 2 (48.6): the C code changes (no counting where one owner is proven) - the riskiest part.
- A: do it now, last in Task 48, with its own plan; B: postpone to Task 38 (memory model) / after
  self-hosting - Task 48 then finishes without it

Then Task 48 complete: its lines to the archive, the Later list checked, a full check.

- **Next Action:** 48 - the plan above and its 2 questions, waiting for approval
