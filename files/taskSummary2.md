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
- **Next Action:** 47.8 `decimal` (the plan below)
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

**47.8 `decimal`** (D.182) - exact base-10: a whole number and its scale (how many places)
- the whole number an int128 - 38 digits (SQL's DECIMAL(38, s), more than C#'s 28) - so science and engineering
  get room, and every step stays exact
- **Exact for money and finance - no drift:**
  - + - * are always exact (no rounding at all);
  - only a division that doesn't end (1 / 3) needs rounding, and it is rounded once, by the mode named or
    `[decimal] rounding` (exact makes it an error);
  - 0.1 + 0.2 is 0.3 exactly;
  - its limit is digits (38), never accuracy - past 38 is an OverflowError, never a lost place
- a literal `1.323242` where a decimal is expected keeps its places; adding lines up the scales (keeps the larger);
  multiplying adds them (capped by `maxScale`, rounding once if past it)
- `value`, `scale`, `toString()` ("1.323242"), `round(places, mode)`, `toDouble()` (said to be inexact), `toDecimal(text)`
- a rate is a decimal (Q.052): `price * 1.155`, `price.percent(15.5)`

**47.2 `money`** (D.021, D.180-D.187) - a sealed 16-byte value struct built into the compiler
- C: `typedef struct { int64_t value; uint8_t scale; char currency[3]; char symbol[4]; } fusion_money;`
  (16 bytes, 8-aligned, two registers)
- On older CPUs or restricted targets the compiler may override these sizes for the final output - rechecked with
  HIDL (FEATURES 41.11, user 2026-11-24)
- fields read as a struct's (`m.value`, `m.scale`, `m.currency`, `m.symbol`); made by `money(123.45, "ZAR", "R")` or
  `money price = 123.45` (scale from the places written - D.176); a symbol over 4 bytes a compile error until the
  Currency module gives short codes (D.184)
- by the compiler, with no call:
  - `a + b`, `a - b`: the scales lined up, the larger kept (100.05 + 200.125 = 300.175);
  - `a * 3`: the value multiplied;
  - `==`, `<`: by amount;
  - the currencies the same or one empty (the result takes the one set), else a compile error where it can be
    seen, or a CurrencyError;
  - overflow checked; the steps in between in int128 (D.178)
- by the Currency module's static methods (Currency.fusion, written in Fusion - 43.3 starts here):
  - `Currency.convert(m, "JPY", "ZAR", 0.11)`;
  - `round(m, places, mode)`, dividing, `percent`, `split` (the parts add up exactly);
  - formatting.
  - `m.convert(...)` written as a method is the same call. The default rounding is `[money] rounding = "halfEven"`.
- money * money an error; `toDecimal(m)` / `toMoney(d)`
- printing by the compiler, not as a struct: `R100.05` with a symbol, `100.05` without (D.187)
- tests: every operation, currencies (same, empty, different), scales, the struct's size (16), printing, the
  Currency statics (convert, round, split sums); example syntax_money

**47.6 Ranges over decimals and money** (47.6a-f in FEATURES, D.170)
- `[ranges] decimals = false` (default): `0.5...2.5` the error saying how to turn it on (today's message, kept)
- `for x in 0.5...2.5 step 0.5` - each value start + n * step (no drift); `stepRequired`, `defaultStep` 0.1,
  `rangeMaxStep` 3; a step that misses the end - the 33.2g rule
- money ranges exact (whole minor units); `case 0.0...0.5` in a match on a double
- tests per D.170's table; example syntax_ranges grows a decimal part
