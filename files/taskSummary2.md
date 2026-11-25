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
- **Next Action:** 47.3 an enum whose values carry fixed data - the plan below (replan 5 - D.188-D.194), waiting for approval
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

**47.3 An enum as a built-in value struct** (TYP.005, D.188-D.194, files/Value_Structs.md) - replan 5, 2026-11-25 -
waiting for approval
The developer writes the values, fields, an optional private constructor and methods; the compiler makes each value a
static const struct (never on the heap, never pooled) with `id`, `enumTypeName`, the fields, `toString()`, `value()`.
A variable holding one only borrows it.
```fusion
enum Planet
    MERCURY(3.303e23, 2.4397e6, "Mercury")       // id 0
    EARTH(5.976e24, 6.37814e6, "Earth"), 200     // id 200
    201, MARS(6.421e23, 3.3972e6, "Mars")        // id 201

    public const double mass
    public const double radius
    public const string name

    double function gravity(double kg)
        return 6.67e-11 * mass * kg / (radius * radius)

    string function toString()
        return name

enum Status
    200, OK
    403, ERROR

enum Primes                                      // no fields: each value a const fixed array
    SMALL(2, 3, 5)
print("{@1} {@2} {@3}", EARTH.mass, Status.fromValue(403), SMALL[1])    // 5.976e24 ERROR 3
```
- 47.3a Setting `[enums] upperCaseNames` (D.194): false / true (a warning) / strict (an error); fusionSettings.xml
- 47.3b Parsing: values first - `NAME`, `NAME(args)`, an id at the front or back; then fields, an optional
  `private Enum(...)` and methods; `const` / `static` before `enum` accepted and changing nothing
- 47.3c Ids (D.189): counted from 0, a written one used, then the next id not used; a clash a compile error; `id`,
  `value()`; `fromValue` / `fromString` (D.193)
- 47.3d Fields (D.190): the allowed types; always const; `public const` read from anywhere, else only inside the enum
- 47.3e Constructor and values (D.191): optional private Enum - its body worked out when compiling; else the fields filled
  in order; no fields - a const fixed array per value, `EARTH[i]` (out of range an IndexError, written a compile error)
- 47.3f Methods and toString() (D.192): read only, whatever `[structs] functions` says; toString() wherever the value
  becomes text; no inheritance or interfaces
- 47.3g Ownership: a borrow of a static value - never moved, copied or freed
- 47.3h C: one `static const` table of structs per enum (strings literals); a value is its index - the borrow; match / ==
  by index; a method a C function taking the index; a null value (-1, D.051) read - a NullError
- 47.3i Capitals: the examples, SYNTAX_REFERENCE and the showcase renamed (Red -> RED ...)
- Tests: tests/test_enum_fields.py (every field type, ids, constructor, arrays, methods, toString, fromValue, null, the
  borrow, upperCaseNames three ways, every error); one example, syntax_enum_planets (06_match_and_enums)
- Settings: `[enums] upperCaseNames` (new, default false)
