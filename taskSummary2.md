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

## TASK 30 (reopened 2026-10-28) - COMPLETE

Null enums (30.11), `case null` and `break` ending a match (30.12), `fall match` (30.13).
Plan: task/taskSummaryArchive.md.

---

## TASK 30: Nulls, number conditions, conditional operator - COMPLETE for now (2026-10-27)

The statement-end bug fix (30.0), the null model (30.1, Nullable_Values.md), `.len` / `.length`
(30.8), `(c) ? a : b` (30.7), `[conditions] numbers` (30.9), docs (30.6). Postponed: 30.2 / 30.3
(the `?.` guard and nullable settings) to Task 32, 30.10 (empty arrays) to Task 45. Plan:
task/taskSummaryArchive.md.

---

## TASK 29: Strings - COMPLETE (2026-10-27)

s[i] = c (29.1), fixed strings = const (29.2), string templates `template string greet =
"..."` (29.3), examples and docs (29.6); 29.4 pooling postponed to Task 38, 29.5 secure
strings postponed (fusionlib.Crypto). Plan: task/taskSummaryArchive.md.

---

## TASK 44: Lessons from the self-hosting test run - COMPLETE (2026-10-26)

Long lines inside ( ) [ ] (44.3), `end` / `var` as names and `_` documented (44.5), fast
text[i] (44.6), module-level variables and constants (44.1), any function as a method
(44.2); 44.4 postponed. Plan: task/taskSummaryArchive.md.

---

## TASK 28: Self-hosting phase 1 - the test run - COMPLETE (2026-10-26)

A Fusion compiler written in Fusion (selfhost/, ~3,500 lines) builds all 18 tier 1 programs;
each prints what the Python-built one prints, leak-free (`python check.py --selfhost`).
Report: task/selfhost_report.md. Plans and notes: task/taskSummaryArchive.md.

---

## TASK 23.9: Fusion_showcase.fusion - COMPLETE (2026-10-23)

files/showcase/Fusion_showcase.fusion + fusion.toml: every feature tagged [built] /
[designed] / [idea] / [rejected] with a one-line description. Plan: task/taskSummaryArchive.md.

---

## TASK 27: Semantic contract and safety - COMPLETE (2026-10-17)

Bounds checks, three block styles, overflow / wrapping / unsafe mode, endless recursion,
interaction tests, changing a collection while looping, the contract (spec "The Semantic
Contract"), int to float ([numbers] auto_widening, 27.2f). Plan: task/taskSummaryArchive.md.

---

## TASK 26: Error handling - COMPLETE (2026-10-16)

Error values, functions that can fail, capturing, bubbling, try / catch / finally / throw,
every built-in failure catchable, `[errors]` switches, examples/errors_demo. Part 2 (26.7-26.13):
implicit errors, untyped capture, custom error types, err.kind, match on error types, typed
catch, Fusion's own error types. Plan and notes:
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
- 26.10 done
- 26.11 done
- 26.12 done
- Task 26 part 2 complete (26.7-26.13)
- Task 27 plan approved (bounds always; wrapAdd functions; stack use + max_call_depth; unchecked blocks)
- 27.1 done
- 27.5 and 27.4 done
- 27.2b and 27.2d done
- 27.2c done
- 27.3 done (found: changing a list while looping over it skips elements)
- Task 27 complete; 27.2f done ([numbers] auto_widening, default false)
- 23.9 done: files/showcase (Fusion_showcase.fusion + fusion.toml); user answered: files/showcase/,
  tags built / designed / idea / rejected + one-line description each
- 28.1 done: the subset measured (task/selfhost_subset.md, tools/example_subset.py)
- User: tier 1 is the test-run target; 28.1.1-28.1.3 sub-tasks; 28.1.4 builtins list proposed
- Plan approved (user: 28.1.4, then 28.1.1). 28.1.4 done: files/Builtins.md, generated and
  checked
- 28.1.1 done: run(command), ProcessError, tests, SYNTAX_REFERENCE example
- 28.1.2 done: measured (selfhost/prototype/) - pattern B over bytes is fast; no compiler
  change needed; slow string indexing found (FEATURES.md Later)
- 28.1.3 done: runtime/fusion_runtime.h; all 45 examples print the same with it
- 28.1 complete (plan archived)
- 28.2-28.8 planned (taskSummary2.md); gap found: no literal { in strings -> 28.1.5
- Plan approved (one walk, leak-free, errors end the program, braces, 28.1.5 first)
- 28.1.5 done: \{ and \} escapes
- User moved the old task-1.x-4.x files to task/archive/ (links updated)
- 28.2 done: the lexer in Fusion matches the Python lexer on all 53 example files; a
  Python compiler bug found and fixed (bare return in void main)
- Slice 1 done: hello_world compiled by the Fusion-written compiler - its C is the Python
  compiler's line for line, the program passes the leak check. Gaps logged in
  task/selfhost_report.md
- Slice 2 done: the parser is complete for tier 1 (all 18 programs parse; --ast); the
  code generator checks types in the same walk; 8 of 18 programs print the same as the
  Python-built ones, leak-free
- Slice 3 done: string ownership (fresh vs borrowed, freed in statement expressions - no
  temporaries), floats / chars / bools, format(), default and named arguments - 12 of 18
- Slice 4 done: fixed arrays, function values / types, lambdas (lifted to C functions,
  named by line + a hash of their text) - 15 of 18
- Slice 5 done: structs, equality across types - **all 18 tier 1 programs print the same,
  leak-free**: 28.3-28.6 done
- 28.7 done: check.py --selfhost - 18/18 the same; 28.8 done: task/selfhost_report.md
- **Task 28 complete - Phase 1 complete** (plan archived)
- The report's six suggestions scheduled as FEATURES.md Task 44 (Phase 2)
- User picked Task 44 ("so that it's easier going forward"); plan written
- Task 44 approved (order as planned; globals a setting, on by default; methods: any function)
- 44.3 done: a line break inside ( ) or [ ] continues the line (both lexers)
- 44.4 postponed (user: option A); 44.5 done (`_` was already built - documented; end / var
  ordinary names in both lexers)
- 44.6 done: fast text[i] (a one-entry cache in the run-time, cleared when memory is freed -
  safer than changing the string struct); 52 s -> 0.03 s
- 44.1 done: module-level variables and constants ([modules] variables, default true)
- 44.2 done: any function as a method (p.moved(1, 2)); Task 44 complete (44.4 postponed)
- FEATURES.md: every [DONE] task and item moved to task/featuresArchive.md (user, 2026-10-27);
  it keeps only open and postponed ones; check.py --status counts done from the archive
- User picked Task 29; plan written (prefix review + 29.1-29.6, 3 questions)
- Task 29 approved (no m/f/p prefixes, t"..." templates, pooling postponed to 38)
- 29.1 done: s[i] = c (fusion_str_put; copies, literals and callers' strings unchanged)
- Comparison with other languages added to Notes/Program lang Compare.txt (user request)
- 29.2 done: const string = fixed (inside const structs / arrays too); spec "Constants"
- 29.3 design: user dropped t"..." - `template string greet = "..."` becomes an internal
  function; option A (local templates expanded where called) + 4b (passed as a function value)
- 29.3 done: src/semantic/templates.py expands every use before analysis; names inside {...}
  now report the string's line (was 1:1); the module loader keeps templates per module
- 29.6 done (examples syntax_string_put / syntax_templates, spec); **Task 29 complete** (29.4,
  29.5 postponed; FEATURES lines and plan archived)
- Task 30 planned (model: `T?` opt-in, narrowing, `??`, `?.` / `?[`, `x!`; 5 questions)
- User answered the Task 30 questions and added notes (in the plan); session closed
- Task 30 design settled (Nullable_Values.md): only class objects null; strings / arrays /
  lists / maps never null (nullable settings, default false); ?. guard, ??, number conditions
  "positive" by default; spec updated with every change so far (user request)
- Task 30 started: 30.0 done (a statement must end its line - the int numbers[] bug); plan
  revised to the settled design (30.2 / 30.3 postponed to 32)
- Task 30 answers: 1. both `.len` / `.length` - with and without brackets, `length` is sugar
  for `len`; 3. order OK; 2. explained (numbers in and / or / not) - waiting
- Question 2 answered (user, 2026-10-27): numbers as bool only when the setting allows it
  (on by default - "positive"); only in `if` / `while` conditions (with and / or / not);
  `count == true` follows the setting, `count === true` is false, `bool b = count` always an
  error
- 30.10 postponed to new Task 45 (arrays that grow at the end - user: an empty array is for
  adding to later); Arrays.md written (single values, arrays, lists, maps)
- Collections decisions recorded (Arrays.md, FEATURES 45 / Later / 42.17, Concurrency.md
  3.12): a + b, removeLast / pop, slice / sliceAt, looping while changing, thread safety,
  map keys; slice / splice names - suggestions in Arrays.md section 7, user to pick
- More collections decisions (user): copyPart (slice as sugar), sliceAt end included, A + B +
  C + D, foreach (no add / remove - compile error), lists / maps shared threads (10) by
  default; CLAUDE.md naming rule. Then: positions from 0; maps combine with add() (same key:
  replace by default, a map setting); foreach (Type item in c); Collection interface (32.4);
  lists allow duplicates, maps don't
- 30.8 done: .len / .length with or without brackets (type checker rewrite to len)
- 30.7 done: (c) ? a : b (ConditionalExpr; a string result is always owned)
- 30.9 done: [conditions] numbers (a number in an if / while condition becomes n > 0 or
  n != 0 in the type checker)
- 30.6 done (shipped with each part); **Task 30 complete for now** - FEATURES lines and plan
  archived; 30.2 / 30.3 wait for Task 32, 30.10 for Task 45
- Enums recheck (user, 2026-10-27): enums are reference types like classes - `Status s` with no
  value is null, not the first value (today: the first value). Recorded as 30.11, docs updated;
  open: build now or with Task 32, match on null
- 2026-10-28: user - build null enums now (30.11), `case null` (30.12), `fall match` (30.13);
  plan written, 3 questions
- User answered (no NullError in match - null goes to case null / else; prints "null"; break
  ends a match, continue acts on the loop); approved
- 30.11 done: null enums (IsNullExpr for == null / is null / ?.null; FUSION_ENUM_NULL;
  NullError; a covering match with no else raises it on null; toString / print give "null")
- 30.12 done: case null (any type, one per match); break ends a match (end label, frees,
  finally); continue acts on the loop
- 30.13 done: fall match (sequential ifs on the chosen case number; break to the end label)
- **Next Action:** the user picks the next step - Task 31 (config in any format) is next in
  order; Task 45 (growing arrays) and Task 32 (classes) carry the postponed parts
