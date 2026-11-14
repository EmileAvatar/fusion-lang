# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## TASK 50: readonly results and a deep const - PLAN (2026-11-14), waiting for approval

Settings: none. Decisions: D.110, D.112, D.113, D.115 (all ACTIVE). Checked today (2026-11-14):
- `public readonly Engine function getEngine()` - a parse error ("Expected type name")
- `const Car c = Car("Mini")` then `c.name = "x"` and `c.rename("y")` - both compile: const is
  shallow on an object today (deep only on Lists, Maps, structs)
- `show(readonly x)` on an int - an error ("a int is copied anyway")

In the order to build:

- 50.1 A readonly result, part of the signature (D.110, D.113):
  - Parsed: `[public|internal|private] readonly T function name(...)` - the function's result is readonly
  - The caller gets a read-only borrow: `Engine e = car.getEngine()` - `e` follows the readonly
    parameter rules already built (32.2e): no field set, no changing method, not kept, not passed to
    a function that changes it; `car` frozen while `e` is used (D.109, built)
  - `Engine e = byVal car.getEngine()` - a copy the caller may change; `byRef car.getEngine()` - an error
  - Inside that function: `return readonly x` - an error (the signature says it)
  - What it may return (D.113): a member (a read-only borrow), a new object (stays read-only for the
    caller), a number or string (a copy - `readonly` does nothing: a warning, 50.4)
- 50.2 `const` on an object is deep (D.112): `const Car c` - no field set (`c.name = ...`), no method
  that changes the object (worked out as for a readonly `this`), not passed to a function that changes
  it; `Car d = byVal c` may change; the same error texts as readonly
- 50.4 `readonly` on a copy is a warning, not an error (D.113): `f(readonly n)` on an int / string, and a
  readonly result that is a number or string
- 50.5 `--interface` (D.115): shows public and internal functions (never private), with `readonly` on a
  readonly result
- 50.3 Tests: a truth table in files/Ownership.md section 4 (Rule 4c) - every allowed / not allowed case
  of D.110-D.113, one test per row; null both ways (Rule 4b): a getter returning a null member - no check
  a NullError caught, with `is null` the code runs on
- Docs: files/SYNTAX_REFERENCE.md example (syntax_readonly_result), files/showcase/Ownership.fusion tags
  [built], the fusion-ownership skill, spec 040 / 090 where they mention it, Decisions FUN.016 / FUN.017 /
  MEM.010 / MOD.002 lines

Then Task 50 complete: its lines to the archive, the Later list checked, a full check.

- **Next Action:** 50 - the plan above, waiting for approval
