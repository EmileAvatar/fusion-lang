# Fusion - Working File (active task plans)

**What this file is (Task 22, 2026-10-09):** only the task being worked on now - its detailed
plan, the next action, and the latest session note. Keep it small: it is read often.
- Status of every task and feature: `files/FEATURES.md` (`[ ]` open, `[DONE]`, `[POSTPONED to ...]`)
- Finished tasks and sub-tasks, old sessions: `task/taskSummaryArchive.md` (verbatim)
- Not-started task write-ups: `task/taskBacklog.md` (verbatim)
- Rules (plan first, no emojis in code, ...): `CLAUDE.md`

---

## Current status (2026-10-11)

**Task 18 (core language foundation) is COMPLETE** and archived (plans, notes and the
files/FEATURES.md detail are in `task/taskSummaryArchive.md`). Task 10.2 is met.

---

## Current plan: the roadmap (files/FEATURES.md, renumbered 2026-10-11)

Done tasks keep their numbers; open tasks were renumbered from 25 into three phases (the
approved plan is archived). Phase 1 = 25 enums, 26 error handling, 27 semantic contract and
safety (bounds checks, the three-block-style check), 28 self-hosting test run.

---

## TASK 46: `let` / `var`, `match` as a value, `write` - COMPLETE (2026-10-29)

Plan and answers: task/taskSummaryArchive.md. Tests: tests/test_let_var_match.py.

## TASK 51: Documentation clean-up - PLAN (2026-11-07, approved; 51.1-51.4 done; the 6 open whys answered - follow-ups in Task 52)

Settings: none. Source: user 2026-11-07, files/DocumentationSystemProposal.md (our formats kept)

- 51.1 Move the root files into files/ (git mv - history kept)
	- Stay in the root: CLAUDE.md, README.md, Decisions.md, main.py; new: Main.md, OpenQuestions.md; .gitignore (git needs it)
	- To files/: FEATURES, SYNTAX_REFERENCE, taskSummary2, Arrays, Classes, Concurrency, Concurrency_Traps,
		Nullable_Values, Object_Lifetime, Ownership, ASTs, FutureFeatures (+ Add Later, Caution), OtherFusionLanauge,
		Fusion Ecosystem Map, TestDriven..., dbcontext, fusion-devcontainer, notes, DocumentationSystemProposal, files/requirements.txt
	- check.py and pytest.ini stay in the root (user); fusion.icon -> icons and Images/
	- The old scripts test_const_*.py (4) and test_verification.fusion / .c / .exe -> debug/ (user)
	- Code: check.py (FEATURES, SYNTAX_REFERENCE, taskSummary2 paths), tests/verify_examples.py, tools/patch.py,
		tests/test_check_tool.py, tests/test_decisions_file.py; comments naming files/Classes.md / files/Ownership.md -> files/...
	- Docs: CLAUDE.md (paths, rules), README.md links, examples/CLAUDE.md, the skill; backtick names updated by a script
	- Done when: python check.py all [OK]; ship
- 51.2 Decisions.md (our format stays)
	- A short "Why" column in the decision table - one phrase from the design docs; none invented (blank = ask)
	- A PROPOSED status: Claude may add a row; only the user makes it ACTIVE; check.py accepts it
	- Only decisions made are kept - no superseded rows (a replaced one is removed, as now)
- 51.3 OpenQuestions.md next to Decisions.md: one line per open question (from FEATURES "Open (user)" lines and
	the design docs), each with where it belongs; answered -> removed, the answer goes to Decisions.md
- 51.4 Main.md in the root: what Fusion is for + a map of every file (the "Where things are" table moves there from
	CLAUDE.md; CLAUDE.md points to it)
- 51.5 Navigation in every split file (user, 2026-11-08 - mockup in Notes/showcase): a top and bottom line
	`[< previous](..) | [Main](../../Main.md) | [next >](..)`; files/spec/index.md links every file in order;
	Main.md's paths become links; a long file gets its own contents list; tools/spec_nav.py writes the nav lines
- 51.5 The spec's files (proposed 2026-11-08 - waiting for approval); numbers in tens leave room; lines = spec lines today
	- One file per step (user): cut the section out of files/fusion-language-spec.md, add the nav lines, check, ship;
		the old spec keeps a line "moved to files/spec/NNN-...md" until it is empty, then it is removed and every
		reference (19 files) points to files/spec/index.md
	- Nav line, top and bottom: `[< prev](..) | [Main](../../Main.md) | [Decisions](../../Decisions.md) | [next >](..)`
	- index.md  the list of every spec file, each a link
	- 010-Philosophy.md         philosophy, syntax overview (1-119)                        120
	- 020-SemanticContract.md   the semantic contract (120-192)                             73
	- 030-Types.md              type categories, specs, nullability, variables, constants   200
	- 031-Arrays.md             arrays                                                      87
	- 032-Strings.md            strings                                                     299
	- 033-TypeCasting.md        type casting                                                53
	- 040-Functions.md          declaring, main, block syntax, calling                      272
	- 041-Lambdas.md            lambdas and function values                                 196
	- 042-MultipleReturns.md    several return values, an Error returned                    73
	- 050-Classes.md            class definition, static vs instance, properties            318
	- 051-Inheritance.md        inheritance, static methods and constants                   96
	- 052-Interfaces.md         interfaces                                                  57
	- 060-Structs.md            structs and value types                                     237
	- 061-Enums.md              enums                                                       234
	- 070-ControlFlow.md        control flow                                                334
	- 080-Null.md               null handling                                               112
	- 081-Autoboxing.md         autoboxing                                                  86
	- 090-Memory.md             memory management                                           193
	- 100-Concurrency.md        threading model + async (one home for concurrency)          376
	- 110-Generics.md           generics and templates                                      84
	- 120-Errors.md             error handling                                              242
	- 130-Comments.md           comments and code organisation                              140
	- 131-AutoDocs.md           documentation written from the code                         153
	- 140-Collections.md        collections (as built)                                      132
	- 150-Modules.md            modules                                                     191
	- 160-GameExample.md        a complete game example                                     229
	- 170-Build.md              build, compilation, fusion.toml                             291
	- 180-StandardLibrary.md    the standard library                                        151
	- 181-fusionlib-Core.md     fusionlib: overview + core libraries                        332
	- 182-fusionlib-Extended.md fusionlib: additional libraries                              236
	- 183-fusionlib-IDE.md      fusionlib: IDE and development libraries + summary          217
	- 190-Callbacks.md          callbacks and events                                        35
	- 191-Interop.md            working with other code                                     61
	- 200-ReservedWords.md      reserved words and operators                                222
	- 210-FeaturesSummary.md    the language features summary                               235
	- 220-Comparison.md         Fusion compared with other languages                        208
	- Later (not this task): a topic with a design doc too (Classes.md, Ownership.md, ...) gets one home
- 51.5 Split the spec into files/spec/NNN-Topic.md (100-200 lines each; fusion-language-spec.md is 6,574 lines,
	files/FutureFeatures.md 6,360) - the file list shown to the user first
- 51.6 A link check in check.py (every link and file name in the .md files exists)

## TASK 48: Ownership - move, borrow, share - PLAN (2026-11-01; answers below)

Design: files/Ownership.md (R1-R8, truth tables 1-4); decisions D.014, D.025, D.026, D.033, D.080;
the record D1-D49 in Notes/Ownership_Decisions_2026-10-31.md.

- **Approach:** compile-time rules first, run time unchanged
  - 48.1-48.5 are checks in the compiler only; the C code keeps today's counting, so a
    program that compiles behaves as now (no new crash or leak risk)
  - 48.6 then removes the counting where a move proves one owner (the speed gain)
- **New pass:** `src/semantic/ownership.py`, after type checking, one function at a time
  - each variable's state along every path: alive, moved (where, to what), moved on some path
  - `if` / `match`: dead after it if any branch moved it and didn't give a new value
  - loops: a move inside is an error unless each pass gives a new value (run the body twice)
  - `try` / `catch`: moved in the `try` = maybe moved in the `catch` and after
  - `return` / `break` / `continue` end a path
- **48.0 The rules:** files/Ownership.md is the spec; the exact error texts written there with 48.1
  (open question 1 in section 8)
- **48.1 Moving** (Lists, Maps, objects, structs holding them; strings and plain structs copy)
  - moves: `T b = a`, `b = a`, `this.f = a`, `x.f = a`, `list.add(a)` / insert / `m[k] = a`,
    a List literal `[a, b]`, `return a`
  - use after a move: "'a' was moved to 'b' on line 2 - use byVal a for a copy"; `a = T(...)`
    brings it back
  - a struct's field can't be moved out (D.026): `Car c = order.car` is a borrow (48.2)
  - **setting** `[memory] assignment = "move" | "share"`; "share" = today's behaviour, no
    move errors
  - migrate the tests, examples, files/SYNTAX_REFERENCE.md and the self-hosted compiler
    (`check.py --selfhost`) that rely on `b = a` sharing - `byVal` or restructured
- **48.2 Borrowing**
  - passing borrows: `f(a)` - `a` is back after the call
  - a parameter is a borrow: storing it (`this.f = p`, `list.add(p)`) or returning it is an
    error (R5) - but see question A (constructors that keep what they're given)
  - a local borrow: `Car c = fleet[0]`, `for c in fleet`, `List<int> xs = order.items`; the
    owner can't change while the borrow is still used (until its last use - question C)
  - taking out is a move: `removeAt` / `removeLast` / `pop`
  - a lambda can't capture a borrow
- **48.3 At the call:** `show(readonly acc)`, `f(byVal a)`, `f(byRef a)` - truth table 4; the
  readonly analysis (32.2e, readonly.py) already follows each call; a non-Fusion library:
  a warning
- **48.4** `--interface` shows each public function's result: reads / changes / keeps each
  parameter
- **48.5 `shared`:** POSTPONED (user, 2026-11-03 - D.106): assignment moves, `byVal` copies,
  `byRef` already shares - `shared` waits for a real need
- **48.6** counting removed where a move proves one owner (covers 38.2); leak check and the
  object-lifetime tests (32.10c) must still pass
- **48.7** files/SYNTAX_REFERENCE.md examples (moving, borrowing, shared), a demo program; tests with
  and without null checks (Rule 4b); each truth-table row a test (Rule 4c)
- **48.8** release the `Unique` keyword (D.080)
- **Order:** 48.1 (behind the setting, default "share" while building - question D), 48.2,
  48.3, 48.5, then migrate and switch the default to "move", 48.4, 48.6, 48.8, 48.7 - each
  shipped on its own
- **Settings:** `[memory] assignment` ("move" default | "share") - into
  files/fusionSettings.xml, project_config, showcase [built] when 48.1 lands
- **Answers (user, 2026-11-01):**
  - A. Worked out: a function whose body keeps a parameter takes it - the call moves the
    argument (like `list.add`), `--interface` shows it; no new word (D.100)
  - B. A struct made locally moves as a whole, so ownership works the same everywhere;
    `byVal r` copies it and clones its object; `byRef r` borrows it (D.097 updated)
  - C. A local borrow freezes its owner until the borrow's last use (D.101)
  - D. Build with "share" as the default; switch to "move" once everything is migrated (D.102)

- 48.1 done: src/semantic/ownership.py - each variable's state on every path (moved, maybe
  moved, the loop's earlier pass); runs only with assignment = "move"; the C code unchanged.
  Under "move" today: 14 errors in 8 programs (FEATURES 48.9); `Circle c = (Circle)first`
  moves `first` too - worth a look at 48.2 (a cast back to the class could be a borrow)
- 48.2 done: ownership.py - kept parameters found across the calls (D.100), local borrows and
  for loops freeze their owner until the last use (D.101), R4, R5, no field / element moved out;
  the readonly analysis' core is shared (`changed_parameters`). Under "move": 18 errors in 8
  programs (FEATURES 48.9). Taking an element out waits for a `removeAt` that returns it
- User (2026-11-02): `this` always borrowed - correct for now, review with working programs
  (D.103); a cast moves, back to the class too, unless byVal / byRef is written (D.104)
- 48.3 done: `f(readonly a)` parsed (PassingExpr.is_readonly), checked in every mode by
  readonly.py `check_readonly_calls` (two errors, truth table 4); byRef on objects; move-mode
  lending rules in ownership.py. Library rows postponed to 39.3. Fixed on the way: '.' on a
  null object inside a called function didn't make it "can fail" - the caller's catch was skipped

## TASK 32: Classes and interfaces - COMPLETE (2026-11-01)

Plan and answers: task/taskSummaryArchive.md. Example: examples/classes_demo.fusion.

## TASK 31: The settings file in four formats - COMPLETE (2026-10-28)

fusion.toml (default), fusion.yaml / .json / .ini; the master template files/fusionSettings.xml;
a new fusion.toml when there is none; `[project] fusionSettingFormat` changes the format (.bak kept).
31.5 (enforce [safety] / [backend]) and 31.6 (config.fusion) postponed. Plan: task/taskSummaryArchive.md.

---

## TASK 30 (reopened 2026-10-28) - COMPLETE

Null enums (30.11), `case null` and `break` ending a match (30.12), `fall match` (30.13).
Plan: task/taskSummaryArchive.md.

---

## TASK 30: Nulls, number conditions, conditional operator - COMPLETE for now (2026-10-27)

The statement-end bug fix (30.0), the null model (30.1, files/Nullable_Values.md), `.len` / `.length`
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
- Each one: files/FEATURES.md line, `task/automation.md` row marked Automated, check, commit

---

## Working Notes

### Session 31 (2026-10-09 .. 10-11 - 18.3.5 to 18.5.7)
- Done: 18.3.5 equality, 18.3.5b bool printing, 18.3.6 string library (a-f, masking design
  and build), 18.3.7 type classes / methods, 18.3.8 bytes, 18.4 modules (1-4), 23.7 / 23.8
  (wait at exit, --headless, .fusion preview), Task 24 added (editor support), 18.5 (1-7)
- User preferences saved to memory: as little typing as possible; never change values
  silently
- Task 18 archived (files/FEATURES.md detail too); 3 automation candidates added
- 22.8-22.11 done: check.py --fix-ascii / --ship / --example, tools/patch.py
- 16.1 done: examples/control_flow; map literals noticed missing (files/FEATURES.md Later)
- 22.7a done: README is goals + pointers (554 -> 321 lines); 22.7b waits for the renumbering
- User answered: numbers from 25, classes / generics in Phase 2. ChatGPT review read:
  fixed arrays are not bounds-checked (segfault) -> new Task 27 "semantic contract and safety"
- files/FEATURES.md reorganized into phases and renumbered (22.12); the user asked for 27.1
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
  change needed; slow string indexing found (files/FEATURES.md Later)
- 28.1.3 done: runtime/fusion_runtime.h; all 45 examples print the same with it
- 28.1 complete (plan archived)
- 28.2-28.8 planned (files/taskSummary2.md); gap found: no literal { in strings -> 28.1.5
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
- The report's six suggestions scheduled as files/FEATURES.md Task 44 (Phase 2)
- User picked Task 44 ("so that it's easier going forward"); plan written
- Task 44 approved (order as planned; globals a setting, on by default; methods: any function)
- 44.3 done: a line break inside ( ) or [ ] continues the line (both lexers)
- 44.4 postponed (user: option A); 44.5 done (`_` was already built - documented; end / var
  ordinary names in both lexers)
- 44.6 done: fast text[i] (a one-entry cache in the run-time, cleared when memory is freed -
  safer than changing the string struct); 52 s -> 0.03 s
- 44.1 done: module-level variables and constants ([modules] variables, default true)
- 44.2 done: any function as a method (p.moved(1, 2)); Task 44 complete (44.4 postponed)
- files/FEATURES.md: every [DONE] task and item moved to task/featuresArchive.md (user, 2026-10-27);
  it keeps only open and postponed ones; check.py --status counts done from the archive
- User picked Task 29; plan written (prefix review + 29.1-29.6, 3 questions)
- Task 29 approved (no m/f/p prefixes, t"..." templates, pooling postponed to 38)
- 29.1 done: s[i] = c (fusion_str_put; copies, literals and callers' strings unchanged)
- Comparison with other languages added to Notes/Program lang Compare.md (user request)
- 29.2 done: const string = fixed (inside const structs / arrays too); spec "Constants"
- 29.3 design: user dropped t"..." - `template string greet = "..."` becomes an internal
  function; option A (local templates expanded where called) + 4b (passed as a function value)
- 29.3 done: src/semantic/templates.py expands every use before analysis; names inside {...}
  now report the string's line (was 1:1); the module loader keeps templates per module
- 29.6 done (examples syntax_string_put / syntax_templates, spec); **Task 29 complete** (29.4,
  29.5 postponed; FEATURES lines and plan archived)
- Task 30 planned (model: `T?` opt-in, narrowing, `??`, `?.` / `?[`, `x!`; 5 questions)
- User answered the Task 30 questions and added notes (in the plan); session closed
- Task 30 design settled (files/Nullable_Values.md): only class objects null; strings / arrays /
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
  adding to later); files/Arrays.md written (single values, arrays, lists, maps)
- Collections decisions recorded (files/Arrays.md, FEATURES 45 / Later / 42.17, files/Concurrency.md
  3.12): a + b, removeLast / pop, slice / sliceAt, looping while changing, thread safety,
  map keys; slice / splice names - suggestions in files/Arrays.md section 7, user to pick
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
- Task 31 planned (user: fusion.toml stays the default; YAML / JSON / INI are alternatives) -
  3 questions
- Task 31 answered (PyYAML for now; INI true / false only; a format setting, convert and
  delete, TOML > YAML > JSON > INI, create fusion.toml if none) - 3 follow-up questions
- Follow-ups answered (keep a .bak; create from an XML master template, config.fusion later;
  `[project] fusionSettingFormat`); 31.1-31.4 done
- Settings audit: [structs] hold_collections, [build] wait_at_exit (default false) added;
  showcase updated; CLAUDE.md rules (XML once built; showcase after every task)
- Task 32 planned (user: program to an interface; Collection + foreach; List as an
  interface with a default implementation) - 5 questions
- Task 32 answers (implements; default methods as a setting, off; structs build on structs,
  not interfaces; collection implementations a mini-task, in fusionlib; scope + reference
  counting); testing rule: with and without null checks - 4 follow-up questions
- Follow-ups answered (case_sensitive setting; commas ignored; implements + extends /
  includes for structs; object lifetime - a mini-task, files/Object_Lifetime.md written)
- files/Object_Lifetime.md rewritten (user, 2026-10-28): three memory strategies (MANUAL / OWNERSHIP /
  GC, a setting; GC implementations, its thread), free (unsafe) vs deallocate (safe), a full
  function / class / module example, answers 1-5 recorded; 6 new questions there. Nothing
  built until it is 150% sure
- files/Object_Lifetime.md updated (user, 2026-10-28): OWNERSHIP default, GC optional (also made in
  code), all three at once; `unsafe` functions / blocks; free (unsafe) vs deallocate (safe), use
  after either a compile error; lists / arrays / maps become references (never null);
  readonly / byRef / byVal; constructor forms, private / static constructors, factories
- More answers: freed objects marked (compile error in the same block, run-time elsewhere, `?.`
  treats freed as null); lists references, `byVal` copies; deep copy for byVal on objects
  (other languages compared - files/Object_Lifetime.md 4b)
- More answers: OverflowWrap (default false) replaces [safety] mode = "unsafe" (arithmetic);
  [safety] mode = "safe" / "unsafe"; [memory] copy deep; copy() / copyDeep(); nocopy / noshare
  field modifiers
- Answers: nocopy - a class with one can't be copied; not both on one field; settings camelCase,
  read case-insensitively; strict = warnings become errors; safe default - 32.0 planned
- 32.0 approved (camelCase, `_` ignored, strict = warnings are errors); Car nocopy + noshare
  example recorded (files/Object_Lifetime.md - 1 question)
- 32.0 done: camelCase settings read ignoring case and _; overflowWrap; safety safe / strict /
  unsafe (normal accepted, old unsafe warns); strict = warnings are errors
- Cloneable rules + two truth tables (structs / classes / nocopy / Cloneable / noshare; fields
  inside an enclosing object) - files/Object_Lifetime.md 4b; 6 questions
- Truth tables settled (byValue / byVal; structs byRef as a parameter, [structs] allowReference,
  shareableListBehaviour; noshare can't be handed out; nocopy set only in constructor / clone;
  clone() only with nocopy) - no open questions
- Task 32 approved (user, 2026-10-29: "continue with task 32")
- **32.1 plan (methods on structs):** a function written inside a struct, allowed by
  `[structs] functions = true` (default false - decided 2026-10-24; off: a compile error that
  names the setting). It gets the struct as `this`, by reference: `p.move(1, 2)` changes p.
  Fields by bare name or `this.x`; another method by bare name or `this.f()`; a local or
  parameter can't have a field's name. On a const struct, a method that changes `this` is an
  error. The struct's own method comes before a free function of the same name (44.2). In C:
  `fu_Point__move(fu_Point* this, ...)`, called with `&p`. Settings: `[structs] functions`
  (default false) into files/fusionSettings.xml
- 32.1 done: methods on structs (lifted to Struct.method with `this` by reference;
  [structs] functions, default false)
- 32.8 done: structs building on structs (a hidden first field holds the parent part; an
  Employee becomes its Person part where a Person is expected; "{e}" prints every field)
- 32.13 done: "{e}" as `name : value`, toCSV on structs, arrays and Lists of structs
- 32.10a done: Lists and Maps are references with a count (shared in normal code, copied in
  a struct; byVal / byRef)
- 32.10b done: minimal classes with the counting (a class is a StructDecl with is_class;
  the constructor is the function Car.new; C helpers __make / __retain / __release / __set)
- 32.10c done: the catalogue, a test per case group, each checking when its object is freed
- 32.10d done: cycles - a warning per circle of classes (src/semantic/class_rules.py); the
  leak check reports a kept circle
- 32.10e done: a returned local is moved (no copy, no counting); 32.10 complete
- 32.2h plan - done (moved to task/taskSummaryArchive.md)
- 32.2a done: visibility (fields private, functions public; types public at module level);
  also fixed classes / struct methods inside modules (the loader walked methods twice)
- 32.2b done: several constructors (Car.new, Car.new_2, ...), chosen by the arguments;
  this(...) - the other constructor makes the object (class_rules.check_constructors)
- 32.2c done: statics - module variables `Car.count` + a set-up function `Car.__setup` per
  class (src/semantic/statics.py); main calls them first, ordered after type checking
- 32.2d done: form B on any variable - a local's block follows its declaration
  (src/semantic/setup_blocks.py); a class field's value and block go to the start of each
  constructor (parser `_field_setups`)
- 32.2e done: readonly parameters - src/semantic/readonly.py follows what each function does
  with each parameter (change, keep, pass on); a set-up block may change the const / let it
  sets up (user, 2026-10-30)
- 32.2f done: an object prints its class name (null: `null`), one warning per class
- 32.2g done: `null == null` is true (it gave false)
- 32.2h done: private / internal / public, `namespace A.B` as the first line (the loader
  shares internal names inside a namespace), [visibility] required; module functions public
  by default; class helpers renamed fusion_make_fu_Car ... (a static `make` clashed)
- Design session 2026-10-31: ownership, one writer, services, hot paths (nothing built)
  - The record, decisions D1-D49: Notes/Ownership_Decisions_2026-10-31.md
  - Rules and truth tables: files/Ownership.md (new)
  - Services S1-S10, the Service interface, hotpath service: files/Service.md
  - Threads: files/Concurrency.md 3.13; files/Concurrency_Traps.md P11
  - Scheduled: Task 48 (after all of Task 32), 42.18-42.25, 47.5 `fixed`
- Task 49 done (2026-10-31): Decisions.md built from every source, 10 clashes settled, a check in
  check.py - detail in task/taskSummaryArchive.md
- 32.5a done: interfaces - each class has a table (name, release, one function table per
  interface, small wrappers); an interface value is a void* in C; CastError added
- 32.5b ToString done: a run-time fusion_object_text (its toString() through the class table,
  else the class name); the ToString interface is added only when a class implements it
- 32.5b copies done: fusion_clone_fu_Car per class (a Cloneable class's own clone()); the class
  table got a clone entry; nocopy / noshare checked after type checking (class_rules)
- 32.5b Default done: the interface pass gives each Default variable / field / static Settings()
  (made_by_default - may call a private constructor); a field's is called in the make function
- 32.5 complete
- 32.7 done: inheritance.py - a child's struct starts with the parent's fields (a pragma lets
  C use it as the parent); virtual functions through a hidden X.virtual table; Employee.init
  for super(...); typeOf via the class chain
- 32.4 done (user, 2026-11-01: a collection gives a new Iterator<T> per loop; arrays / Lists /
  Maps implement Collection<T> and Iterator<T>, an array's own implementation blocks remove):
  Iterator<X> / Collection<X> made per element type; foreach over a class collects its
  iterator's items into a List, then the List loop runs
- 32.6 List part done: a List's struct now starts like an object (count, class table); a
  List<X> table answers Collection<X> when the program uses it; a list iterator object;
  fixed on the way: assigning to an interface / parent variable set by the value's type
- User 2026-11-01: next() past the end gives null (D.091 - an error only for a genuine
  failure); Map = Collection<Entry<K, V>> + keys() / values() borrowed (D.092); struct commas
  needed only on one line (D.093) - 32.12 done
- C.011 settled (D.094): next() past the end - null for string / List / Map / object / enum,
  an IndexError for a primitive; a null string = data NULL (prints null, `is null` works)
- 32.6 done: a Map is a Collection<Entry<K, V>> (Entry made per Map type, a struct that may hold
  an object); keys() / values() borrowed views (user 2026-11-01); c.toList() copies any Collection
- A struct may hold an object (user, 2026-11-01 - D.097): null until set, shared when the struct
  is copied; the old error and the planned [structs] classes setting are gone
- 32.14 done: options marked in the set-up block (readOnly moved to its end), flags in the
  List / Map struct, checks at the start of each changing function; DuplicateError, ReadOnlyError
- 32.11 done: src/semantic/case_names.py - program names, a type's members, a function's own
  (with the program's and its class's); checked before any rewrite
- 32.3 done: examples/classes_demo.fusion; Task 32 complete and archived (2026-11-01)
- Task 48 plan answered (user, 2026-11-01 - D.100-D.102); 48.1 (moving) done
- 48.9 so far (2026-11-03): examples migrated; selfhost pinned to share (D.107); moveFieldOut
  setting (D.108); byVal on a struct clones its objects; a case's names are new variables. With
  "move" the default: 38 tests fail - getters (`return this.engine`, `return this.people[i]`)
  are the main open question (asked the user)
- 48.9 done (2026-11-03): "move" is the default. A getter lends (D.109, user); tests of "share"
  itself carry @pytest.mark.share (tests/conftest.py); selfhost pinned (D.107)
- User (2026-11-03): readonly results in the signature (D.110), what a function returns (D.111),
  const deep on objects (D.112) - Task 50, after 48; the rules in files/showcase/Ownership.fusion
  and the skill .claude/skills/fusion-ownership/SKILL.md
- 51.5 (2026-11-09): spec split done up to 070-ControlFlow; long paragraphs split into bullets
  as each file moves (user)
- **Next Action:** 51.5 - 080-Null, 081-Autoboxing, 090-Memory, then the rest of the file list above
  - then 48.4 (`--interface` shows what each public function does with its parameters)
  - then 36.0 (a small syntax highlighter: VS Code, Sublime Text / TextMate)
  - then Task 47 (long, money, enums with fixed data) - user, 2026-10-29
