# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## TASK 52: Classes, value types and null - follow-ups - PLAN (2026-11-14), waiting for approval

Settings: none (the `[conditions]` setting of D.116 only if question 2 says so)

Found while checking (2026-11-14): the null guard - `x?.name`, `x?.f()`, `x ?? y` - was postponed from
Task 30 (30.2) to Task 32 and never built; it fell out of FEATURES (Decisions NUL.003 still PARTIAL).
Today `c ?? Car()` is a parse error and `c?.name` "planned (Task 30.2)". The nullable settings (30.3 -
a string / array / List / Map that may be null) were postponed the same way.

In the order to build:
- 52.6 `private` on an interface's function: a clear compile error (D.114) - today a vague parse error
  ("Expected type name, got 'private'")
- 52.2 Recheck `implements Default` (D.010): never null in every case - a field, a static, a List element,
  after a move, `= null` makes a new one; one test per case
- 52.8 NEW - the null guard (was 30.2, Nullable_Values.md): `c?.name` / `c?.rename("x")` - not run on null,
  no error, false in an `if`; `c ?? Car()` - the value, or the default when null; with and without a check
  (Rule 4b); NUL.003 then BUILT
- 52.7 Null checks at compile time (D.116, D.117), after 52.8:
  - a `?.` comparison (`if c?.speed > 5`) is false on null - a warning; `!` around one an error
  - an object surely null when passed (`Car c = null` then `drive(c)`, nothing in between) - an error
  - a `Default` variable left null and not made again - an error
  - a parameter marked `?` without a null check - a warning: its syntax is question 1
- 52.4 A `Length` interface (TYP.017): design only - files/Classes.md (how built-in methods reach value
  types); building it later
- 52.5 `length()` -1 on null (D.055): needs the nullable settings (30.3) - question 2

Question 1 (OpenQuestions Q.014): how is a parameter marked "may be null"? (D.117; `T?` types are
rejected - NUL.004)
Question 2: the nullable settings (30.3) and 52.5 - build them in Task 52, or postpone to Task 45
(arrays move to the heap there) / their own task?

Then Task 52 complete: its lines to the archive, the Later list checked, a full check.

- **Next Action:** 52 - the plan above and its 2 questions, waiting for approval
