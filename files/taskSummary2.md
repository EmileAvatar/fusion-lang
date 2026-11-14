# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## TASK 52: Classes, value types and null - follow-ups - PLAN replanned 2026-11-14 (user's null rules)

Settings: `[strings] nullBecomesEmpty` (52.12 - its default asked: D.003 "no silent changes")

The rule (user, 2026-11-14 - D.138, D.139, D.140): a string, array, List or Map is never null, whatever
the settings; only a class object, an enum, an interface - and an array slot of an object type - can be
null, with no mark needed. A List / Map never holds null; a List literal adds each item.

Checked today: `fleet.add(null)`, `[null]` as a List, `m["a"] = null` are accepted (wrong);
`Car[] a = [Car(), null]` is refused (wrong); `[Car(), Truck()]` refused (right); `List<int> xs = null`
refused but the message promises a `[lists] nullable` setting (to change).

In the order to build:
- 52.6 `private` on an interface's function: a clear compile error (D.114)
- 52.2 Recheck `implements Default` (D.010): one test per case
- 52.10 A List / Map never holds null (D.139) - compile errors; a null variable added at run time: NullError
- 52.11 Arrays of objects (D.140): a null slot, in a literal too; `arr[i] = null` frees the object
- 52.12 `[strings] nullBecomesEmpty`: `s = null` an error or "" - default asked
- 52.8 The null guard (was 30.2): `c?.name`, `c?.rename()`, `c ?? Car()` - objects only
- 52.13 `?.` / `??` on a string, array, List, Map: a warning - it can't be null
- 52.7 Compile-time checks (D.116, D.117): a `?.` comparison warns, `!` around one an error, a surely-null
  object passed an error, a `Default` left null an error
- 52.4 The `Length` interface: design only (files/Classes.md)
- Closed: 52.5 (nothing can be null - D.055), 52.9 nullable settings rejected (D.138), Q.014 (no mark)
- Docs: Nullable_Values.md, spec 080 / 140 / 210, the showcase, the messages that promise nullable settings

- **Next Action:** 52 - the default of `[strings] nullBecomesEmpty`, then build from 52.6
