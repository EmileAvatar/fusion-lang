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
- Done 2026-11-27: 47.5 `fixed(n)` (tests/test_fixed.py) - Task 47 complete, its plans in task/taskSummaryArchive.md
- Done 2026-11-24: R11 FSMA set up (files/Research/Memory/FSMA/, FEATURES R11, R3.9-R3.11) - its plan in task/taskSummaryArchive.md
- Done 2026-11-27: Tasks 33, 45, 47 closed - their postponed items moved (L6.9, 42.19, L8.11)
- Done 2026-11-28: Task 57 namespaces and modules (tests/test_namespaces.py, examples/13_projects/suppliers) - its plan
  in task/taskSummaryArchive.md
- **Next Action:** Task 56 - 56.2 spec 070, then 56.3 loop labels (the plan below, approved - D.214-D.220)

## Task 56 - Loop safety: the `check` keyword (plan - 2026-11-28, approved - D.214-D.220)
**Today:** `check` is a reserved word (Task 61) - nothing more; `loop` a keyword without a statement; no loop
labels, no `exit loop`, no iteration limit.
**Decided (user, 2026-11-09 - to confirm):** the name `check` (also a debug tool); after each pass, by the pass count;
not for normal program control - a shutdown, a loop limit; it exits the loop when true; no break / continue in it;
`exit loop` to an outer loop; the forms `check`, `check 20`, `check >= 10000`, `check not isHealthy()`,
`check 50 not isHealthy()`, `check InterruptSignal.Stop`, `check interrupt(signal, data)` (the last two with Task 42).
Q.084-Q.090 answered A (D.214-D.220).

**Steps** (each shipped on its own):
- 56.1 The answers into Decisions.md; spec 070 rewritten to them (56.2): the old 1,000,000 default, the
  attributes, `fusion.config.max_iterations`, the RAM / CPU text removed
- 56.3 Loop labels (Q.089): `outer: for ...`, `break outer` / `continue outer` - C labels and gotos; an unknown or
  unused label an error
- 56.4 The `with` part and `check` (Q.084-Q.087): parsed in the three block styles; a check with a condition runs
  its block and ends the loop; without one, every pass / every Nth, and the loop carries on; `check >= N`;
  `loop.count`; `exit loop` / `exit loop outer`; break / continue in a check an error; the C - a pass counter only
  in a loop that has checks
- 56.5 `[safety] maxIterations` (Q.088): a counter in `while` / `loop` when above 0; a LoopLimitError (a new
  built-in error) naming the line and the limit; a loop's own `check >= N` instead
- 56.6 Examples and docs: SYNTAX_REFERENCE (Rule 4), fusion.ebnf + page, fusionSettings.xml, the settings doc, the
  showcase, FeatureTree, SYN.033 BUILT
- Not in this task: `check interrupt(...)` / `check InterruptSignal.Stop` - Task 42 (FEATURES 56.7 -> 42.26, 42.27);
  the `loop { }` statement itself (L7.2)

**Tests:** tests/test_loop_checks.py - a truth table in spec 070 (Rule 4c): each form x each block style x with /
without a condition x labels x the limit on / off - each row a test; with and without a null in a check's condition
(Rule 4b).
**Settings:** `[safety] maxIterations` (a whole number, default 0 = no limit) - new; fusionSettings.xml,
project_config.py, the settings doc, the showcase toml once built.
