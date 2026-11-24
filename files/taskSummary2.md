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
- **Next Action:** the research R10 (money and decimals: COBOL and other languages) before any money code (47.2,
  47.6) - Q.047 / Q.048 A for now; then R11 FSMA
- Done 2026-11-24: R11 FSMA set up (files/Research/Memory/FSMA/, FEATURES R11, R3.9-R3.11) - its plan in task/taskSummaryArchive.md

## Task 47 - Types: long, short, money, decimal ranges (47.1 done; 47.2 and 47.6 wait for R10)
**Order:** 47.1 `long` / `short` first, then 47.2 `money`, then 47.6 ranges over decimals and money - each shipped on its
own. 47.3 (enums with fixed data), 47.4 (`FusionType`) and 47.5 (`fixed(n)`) stay in Task 47, planned after the
number types (Q.049: A).
**Settings:** `[money] decimals` (default 2) and `[money] rounding` (Q.048) - with 47.2; `[ranges] decimals`,
`stepRequired`, `defaultStep`, `rangeMaxStep` (decided - D.170) - with 47.6; each into fusionSettings.xml once built.
**Waits on:** 36.0 first (Q.050: A). Money (47.2) and its ranges (47.6) wait for the research R10 - money is a
money handled accurately as COBOL does; the preference: money stays a long (D.021), its meaning from the Currency
module, a decimal type the backup (user, 2026-11-23).

**47.2 `money`** - a long counting minor units (D.021, 47.2.1): exact, never a float
- its literal and printed form - Q.047; `[money] decimals` gives the minor unit (2: R1 is 100)
- `+` / `-` between money; `*` by a whole number; `/` by a whole number rounds by `[money] rounding` (Q.048); money with
  a double an error ("money is exact - use percent / split"); overflow checked as long
- 47.2.2: `m.percent(15)` (rounded), `m.split(3)` - a List<money> whose parts add up exactly (the remainder to the first
  parts: R100 / 3 = 33.34 + 33.33 + 33.33), the rounding written out where it happens
- printing: `123.45` with the minor unit's places (a currency's symbol is the Currency module's - 43.3, not the core)
- tests: every operation, rounding modes, split sums, overflow, never a float; example syntax_money; TYP.003 BUILT

**47.6 Ranges over decimals and money** (47.6a-f in FEATURES, D.170)
- `[ranges] decimals = false` (default): `0.5...2.5` the error saying how to turn it on (today's message, kept)
- `for x in 0.5...2.5 step 0.5` - each value start + n * step (no drift); `stepRequired`, `defaultStep` 0.1,
  `rangeMaxStep` 3; a step that misses the end - the 33.2g rule
- money ranges exact (whole minor units); `case 0.0...0.5` in a match on a double
- tests per D.170's table; example syntax_ranges grows a decimal part
