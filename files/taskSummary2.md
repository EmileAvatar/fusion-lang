# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## Next

- Task 33 (generics) complete 2026-11-22 - its plan in task/taskSummaryArchive.md
- Done 2026-11-22: 45.10 an array as a Collection<T> (D.090) - its plan in task/taskSummaryArchive.md
- Done 2026-11-23: 36.0 a simple highlighter for VS Code and Sublime Text (tools/editors/, installed in VS Code)
- Done 2026-11-24: 47.1 `long` / `short` (tests/test_long_short.py, syntax_long) - its plan in task/taskSummaryArchive.md
- Done 2026-11-24: 36.8 Fusion's colours (tools/editors/colors.json, four themes) - its plan in task/taskSummaryArchive.md
- Done 2026-11-24: research R10 written - files/Research/Money/Money.md
- Done 2026-11-25: files/fusion.ebnf synced with the compiler (no version until self-hosting - 35.7), the "ebnf" check;
  the memory tiers note to R11.8, Vale to R11.6, flash wear 41.11e
- Done 2026-11-25: 47.7 `int128` / `int256` (tests/test_wide_numbers.py, syntax_wide_numbers) - its plan in task/taskSummaryArchive.md
- Done 2026-11-25: 47.8 `decimal` (tests/test_decimal.py, syntax_decimal) - its plan in task/taskSummaryArchive.md
- Done 2026-11-25: 47.2a `money` - the type (tests/test_money.py, syntax_money)
- Done 2026-11-25: 47.2b the Currency module (tests/test_currency.py, syntax_currency) - 47.2 complete, its plan in task/taskSummaryArchive.md
- Done 2026-11-25: 47.6 ranges over decimals and money (tests/test_decimal_ranges.py, syntax_ranges) - its plan in
  task/taskSummaryArchive.md
- Done 2026-11-25: 47.3 an enum as a built-in value struct (tests/test_enum_fields.py, syntax_enum_planets) - its plan
  in task/taskSummaryArchive.md
- Done 2026-11-27: 47.10 an enum value alone anywhere (tests/test_bare_enum.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.11 enum values written with their enum (tests/test_bare_enum.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.12 `[source] shadowing` (tests/test_shadowing.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.9 number notations (tests/test_number_notations.py) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: 47.4 FusionType (tests/test_fusion_type.py) - its plan in task/taskSummaryArchive.md
- **Next Action:** 47.5 `fixed(n)` - the plan below (approved, D.202, D.203)
- Done 2026-11-24: R11 FSMA set up (files/Research/Memory/FSMA/, FEATURES R11, R3.9-R3.11) - its plan in task/taskSummaryArchive.md

## Task 47 - Types: wide numbers, decimal, money, ranges (replan 2 - 2026-11-24, every question answered)
**Decided (user, 2026-11-24 - D.176-D.187):**
- `int128` / `int256`: signed, used like any number - no byte[16] / ArrayLarge type.
- `decimal` is built first, for money, science and engineering.
- `money` is a sealed value struct built into the compiler: `value` (long), `scale`, `currency` (a fixed 3-char text,
  empty by default) and `symbol`. Never on the heap, never pooled.
- The scale is how many places the value holds (1323242 at scale 6 is 1.323242); adding keeps the larger scale.
- Two currencies must be the same, or one empty; `convert(from, to, rate)` first otherwise.
- halfEven rounding, an operation may name its own mode, and `[money] rounding = "exact"`.
- The steps in between are done in int128, rounded once.
- Money is 16 bytes: `value` 8, `scale` 1, `currency` 3, `symbol` 4 (D.184). One money type, convertible to and
  from decimal (D.185).
- Money is only a container: the compiler does `+ - *` and comparing itself; everything with rules is a static
  method of the Currency module that the compiler calls (D.186).
- The symbol is for display only: `R100.05`, or `100.05` without a symbol (D.187).
**Order:** 47.7, then 47.8, then 47.2, then 47.6 - each shipped on its own; 47.3-47.5 after (Q.049).
**Settings:**
- `[money] rounding` (halfEven | halfUp | down | up | exact - D.177);
- `[decimal] maxScale` (18);
- `[ranges] ...` (D.170) with 47.6.
- Each goes into fusionSettings.xml once built. No `[money] currency` - empty is the default (D.183).

**47.5 `fixed(n)`** (D.020, D.064, TYP.006 - files/Arrays.md) - plan, waiting for approval
```fusion
fixed(10) string code = "AB-123"           // at most 10 characters; the values may change
code = "TOO-LONG-CODE"                     // written: a compile error; from a value: an error while running
fixed(14) List<Person> people              // at most 14; the 14 slots reserved at once - adding never grows it
fixed(3) Map<string, fixed(15) string> codes
fixed int numbers[10]                      // an array that never takes another size (D.141's `fixed` form)
```
- 47.5a `fixed(n)` on a List / Map: at most n elements / keys, the n reserved when made (one allocation, never
  grown); adding the n+1th a CapacityError (D.202); lower is fine, a value is never cut (D.020)
- 47.5b `fixed(n)` on a string: at most n characters - a written value checked when compiling, others while running;
  an ordinary string with its length checked, inline later with FSMA (D.203)
- 47.5c `fixed(n)` on a struct field, a parameter (`fixed(10) string code` - a longer argument an error), a List's
  element type (`List<fixed(15) string>`), a Map's value type
- 47.5d n is a whole number constant - written, or a `const` (`fixed(MAX_NAME) string name` - the hardware's or a
  setting's size later, H9); n of 0 or below an error
- Tests tests/test_fixed.py; example syntax_fixed; Settings: none

