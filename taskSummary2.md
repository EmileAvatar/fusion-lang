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

## TASK 30: Nulls, empty values, number conditions, conditional operator - ACTIVE (2026-10-27)

**Design settled** (user decisions 2026-10-27 - `Nullable_Values.md`, spec "Null Handling"):
only class objects can be null; strings, arrays, List and Map are never null (empty by
default, `nullable` settings default false); `?.` is a guard, `??` a default, number
conditions a setting ("positive" by default). The null guard needs class objects, so it
moves to Task 32 (30.2, 30.3); the rest is built now.

**Revised sub-tasks (order):**
- 30.0 DONE - bug: a statement must end its line (`int numbers[]`, `int x = 5 print(x)` were
  read silently as two statements)
- 30.10 Empty arrays: `int[] numbers` / `int numbers[]` - an empty array, length 0. Arrays
  are fixed-size, so an empty one gets values only by being replaced (`numbers = make()`,
  which already works); a growing collection is a List
- 30.8 `.len` and `.length` on strings, arrays, lists, maps (= `len(x)`)
- 30.7 The conditional operator `(condition) ? a : b` (`?` lexed so `?.` / `??` still fit
  later)
- 30.9 `[conditions] numbers` = "positive" (default) / "nonzero" / "off" - an int (or
  other number) as an `if` / `while` condition; `and` / `or` / `not` with numbers too
- 30.6 Docs, examples, spec status lines
- Postponed to 32: 30.2 the guard and checks on class objects, NullError, warnings; 30.3 the
  `nullable` settings and `?.length()` = -1

**Questions:**
1. `.len` / `.length`: with brackets (`s.length()`, as lists have `xs.len()` today),
   without (`a.length`), or both?
2. 30.9 changes today's rule (a condition must be a bool) to "positive" by default - so
   `if count` compiles where it was an error. Also allow numbers with `and` / `or` /
   `not` (`if count and ready`)?
3. Order as above?

**User notes and answers (2026-10-27, end of session - the plan above is revised next
session to match these):**
- `?` is NOT part of a type: `string? nickname` is not valid. `?` is used on a variable when
  calling a function / reading a member of it: `nickname?.length()` gives 0 when nickname is
  not set, e.g. `if nickname?.length() > 5` (0 when empty). It tells the compiler: if the
  value is not null use it, otherwise no error - it is for null checking. `?` calls the
  function or member of the variable's type (the T class type)
- Null applies only to strings (special: a value and a class with methods) and class types
  (Q1)
- Checking null: `==`, `===`, `is null`; `x?.null` stays as quick typing - true when x is
  null; `!x?.null` - not null (sugar) (Q2)
- No `x!`; `!x?.null` instead - option (a): an unchecked use is a compile error (Q3)
- Q4 "yes" (no silent 0). Follow-up (user, 2026-10-27): on a null string
  `nickname?.length()` gives **-1** (never a real length, so not a silent 0); numeric arrays:
  not decided yet. `??` gives a default when the value is null:
  `nickname?.length() ?? 0`. **Open, next session:** if `?.length()` gives -1, `??` never
  sees a null there - decide whether `?.` gives null (then `?? -1` / `?? 0` picks the value)
  or -1 (then `??` is for `?.` on other members / functions)
- Support both `.len` and `.length` - `len` is quick typing (Q5)
- Numbers as conditions - DECIDED (user, 2026-10-27): a `fusion.toml` setting with three
  options, e.g. `[conditions] numbers = "nonzero"` (default - 0 false, any other number
  true, as C / C++ / Python / JavaScript), `"positive"` (zero and negatives false),
  `"off"` (a condition must be a bool - today's behaviour). (Default changed to
  `"positive"` - see "Decided" below.) (Other languages: C / C++ / Python / JS /
  Perl - 0 false, others true; Ruby / Lua - every number true; Java / C# / Go / Rust /
  Swift / Kotlin - bool only.) Trap to document: `if indexOf(s, "x")` - -1 (not found) is true
- `?.` is a guard (user, 2026-10-27): on null it doesn't error or crash; inside an `if` the
  condition is false, so the else block runs - also for a comparison:
  `if person?.getAge() >= 18 ... else ...` runs else when person is null
- `??` gives the default when `?.` meets null: `someClass?.someMethod() ?? value`
- The conditional operator `(condition) ? a : b` - one line, gives a value:
  `int age = (person?.getAge()) ? person.getAge() : -1`
- **Open, next session (found when writing these down):**
  1. With the default `"nonzero"`, -1 is **true**: `if person?.getAge()` runs the "old
     enough" block when getAge() returns -1, and `if nickname?.length()` is true when
     length() gives -1 for null. The user's example comments expect -1 -> false (that is
     `"positive"`). Either `?.` on null gives null (always false, whatever the setting) and
     -1 is never used for "missing", or the default becomes `"positive"`
  2. "returns error": `?.` on a function that fails - does the guard also catch the error
     (false block), or does the error still travel (Task 26)?
  3. `(person?.getAge()) ? ... : -1` - an age of 0 is false under `"nonzero"`, so it gives -1
- Also supported: the conditional operator `(condition) ? valueIfTrue : valueIfFalse`
- **To do:** update the spec (`files/fusion-language-spec.md`) with every change made so far
  (check Tasks 29 / 44 and earlier decisions are all reflected) - noted 2026-10-27

- **Decided (user, 2026-10-27, answers to the 3 open points):**
  1. Default is `"positive"` (zero and negatives false) - the user's own model; options stay
     `"positive"` (default) / `"nonzero"` / `"off"`. IDE note (Task 36): show developers how
     number conditions are set for the project, as a hint
  2. `?.` guards a null **object**: the method is not run and nothing errors; in an `if` the
     condition is false. Plain `.` on a null object is a NullError (only a catch handles it).
     A comparison with a guarded null is false, so `!(pep?.getAge() >= 18)` is true
  3. Only `string.length()` and `array.length` give -1 through `?.` on null; every other
     member / method gives null (or, with plain `.`, a NullError)

**Truth tables (draft, 2026-10-27 - default `[conditions] numbers = "positive"`):**

Table 1 - string and array length. `s` is a string, `a` an int array:

| Expression | s / a is null | s = "" / a = [] | s = "abc" / a = [1, 2, 3] |
|---|---|---|---|
| `s.length()` / `a.length` | NullError | 0 | 3 |
| `s?.length()` / `a?.length` | -1 | 0 | 3 |
| `if s?.length()` - "positive" (default) | false | false | true |
| `if s?.length()` - "nonzero" | **true** (-1) | false | true |
| `if s?.length()` - "off" | compile error | compile error | compile error |
| `if s?.length() > 0` | false | false | true |
| `if !(s?.length() > 0)` | true | true | false |
| `if s?.length() >= 0` | false | true | true |
| `s?.length() ?? 0` | -1 (never null, so ?? is never used) | 0 | 3 |
| `s?.null` / `s == null` / `s is null` | true | false | false |
| `!s?.null` | false | true | true |

Table 2 - a class. `Person p = new Person("Jake")`; `Person pep` (never set = null);
`getAge()` returns an int, `getSpouse()` returns a Person or null:

| Expression | age 30 | age 10 | age 0 | pep (null) |
|---|---|---|---|---|
| `x.getAge()` | 30 | 10 | 0 | NullError - only a catch handles it |
| `x?.getAge()` | 30 | 10 | 0 | null (getAge not run) |
| `if x?.getAge() >= 18` | true | false | false | false |
| `if !(x?.getAge() >= 18)` | false | true | true | true |
| `if x?.getAge() < 18` | false | true | true | **false** (see open 1) |
| `if x?.getAge()` - "positive" (default) | true | true | false | false |
| `if x?.getAge()` - "nonzero" | true | true | false | false |
| `x?.getAge() ?? -1` | 30 | 10 | 0 | -1 |
| `(x?.getAge()) ? x.getAge() : -1` | 30 | 10 | **-1** (0 is false) | -1 |
| `x?.null` / `x == null` / `x is null` | false | false | false | true |
| `!x?.null` | true | true | true | false |
| `x?.getSpouse()?.getName()` | name, or null if no spouse | same | same | null |
| `x.getSpouse().getName()`, no spouse | NullError | NullError | NullError | NullError |

**Answered (user, 2026-10-27):** 1. warn; 2. warn (`??` is only for where a value is
expected and none may come); 3. strings always default to "" and are never null - unless
`[strings] nullable = true` (default false). Full write-up: `Nullable_Values.md` (root).
Arrays, List and Map are the same (user, 2026-10-27): never null, empty by default,
`nullable` settings default false; `"".length()` and `[].length()` are 0.

**Was open:**
1. With null, `>= 18` is false and `< 18` is false too - so `!(x >= 18)` is not the same as
   `x < 18`. Keep that (SQL works this way), or warn when a guarded `?.` value is compared?
2. `s?.length() ?? 0` never uses the 0 (-1 is not null) - warn there?
3. Strings and arrays become nullable: does `string s` with no value start as null or ""
   (today "")? Same for arrays

### Backlog write-up (moved from task/taskBacklog.md, 2026-10-27, verbatim)

#### Original: TASK 30 (was 14): Nullable Arrays & Safe Navigation

**Goal:** Let arrays (and eventually other reference-like types) be nullable, with
`arr.length`/`arr?.length` and `arr?[i]` behaving safely instead of crashing unpredictably -
the richer null-safety design the user asked for while scoping Task 9, split out because it's
a language-wide feature, not an array-specific one.
**Status:** Not Started (proposed breakdown only, not yet approved for implementation - same
status convention as Tasks 12/13). **Unblocked as of 2026-09-13** - Task 12.7 is now complete;
this task still needs its own scoping approval before implementation begins, per Rule 1.
**Priority:** MEDIUM (no urgency stated)
**Blocked By:** ~~Task 12.7~~ - COMPLETE (2026-09-13). Task 12.7 decided `Weak<T>.lock()`
returns a nullable value that must be checked, which is the same null-handling shape this task
needs for `arr?.length`/`arr?[i]` - the two features should share one null-flow-analysis
design (noted in Task 12.7's own writeup), not two independent ones.
**Estimated Effort:** TBD - needs its own sub-plan once approved for scoping
**Source:** Arose from scoping Task 9 (2026-09-13) - the user asked for `arr.length` with
null-checking, `arr?.length` returning 0 silently on null, and a hybrid null-safety model:
compile-time error where the compiler can prove an array is null before use, a runtime crash
with a clear message where it can't prove it, and `?.`/`?[` as the way to opt out of both (get
0 back instead). The user also noted this might eventually be configurable per-project
(ties to Task 12.12's project configuration system). Notably, `files/fusion-language-spec.md`
already describes this exact design for strings and arrays under "Array Safe Navigation" and
"Null Safety" (e.g. "`string?.length` returns 0 if null") - this task is about actually
building it, starting with arrays.

#### Sub-tasks (NOT YET APPROVED - proposed breakdown only)

##### 14.1: Nullability Model Decision
- [ ] Decide whether arrays become a nullable reference type (pointer + length) or whether
      nullability is a separate wrapper/modifier applicable to multiple types
- [ ] Decide how `null` (currently type-checks as `void`, not wired to any real type) becomes
      assignable to nullable array types
- [ ] Resolve alongside Task 12.7's `Unique`/`Shared`/`Weak` design - a nullable array's
      ownership story needs to fit that same model, not a separate one
- [ ] Get user decision; record as an ADR alongside Task 12.7's memory model spec

##### 14.2: Compile-Time Null-Flow Analysis
- [ ] Track definite-null / maybe-null / definite-non-null state through straight-line code
      (at minimum; branch-merging is a further decision)
- [ ] Compile-time error when `.length`/indexing is used on a provably-null array without a
      preceding `?.`/`?[`
- [ ] Write semantic tests for provably-null and provably-safe cases

##### 14.3: `.` / `?.` / `?[` Parser Support
- [ ] Add member-access (`.` identifier) and safe-navigation (`?.` identifier, `?[`
      expression `]`) postfix parsing - doesn't exist in the parser at all today
- [ ] `arr.length` lowers to the same thing `len(arr)` does (both should stay available and
      behave identically per the user's "give devs both, don't lock into one way" request)

##### 14.4: Runtime Null-Check Codegen
- [ ] For accesses that can't be proven safe at compile time: emit a null check that crashes
      with a clear message on null (matches the user's "crash the app with clear error
      message" requirement)
- [ ] For `?.`/`?[` accesses: emit a null check that evaluates to 0 instead of crashing (no
      warning - matches the user's "we don't execute the function and return a 0" description)
- [ ] Regression tests: provably-null (compile error), runtime-null via non-provable path
      (crash with message), `?.`/`?[` on null (0, no crash)

##### 14.5: Extend Beyond Arrays (stretch)
- [ ] `string?.length` is already described in the language spec alongside arrays - evaluate
      applying the same mechanism to strings once arrays prove it out
- [ ] Note for future classes/objects: this mechanism should generalize, not be
      array-specific plumbing

##### 14.6: Documentation & Examples
- [ ] Update `files/fusion-language-spec.md`'s "Array Safe Navigation"/"Null Safety" sections
      from aspirational to actually-implemented, with the real semantics decided above
- [ ] Example program demonstrating `.length` vs `len()` vs `?.length` vs `?[i]`
- [ ] Update `files/fusion.ebnf`'s postfix production (already has the grammar drafted -
      confirm it still matches what got built)

**Success Criteria:**
- Arrays can be null; `null` is assignable to a nullable array type
- `.length` and `len(arr)` both exist and behave identically
- A provably-null `.length`/index access is a compile-time error
- A non-provably-null access that turns out null at runtime crashes with a clear message
- `?.length`/`?[i]` on null returns 0 without crashing, silently (no warning)
- No behavior regressions to Task 9's existing non-nullable array support

**Deliverables:**
- Nullability decision recorded (ADR, alongside Task 12.7)
- Compile-time null-flow analysis pass
- `.`/`?.`/`?[` parser support
- Runtime null-check codegen
- Updated language spec matching actual behavior

**Explicitly NOT scheduled now:** this task is future work. Task 12.7 is now complete, so
its blocker is cleared, but no implementation, grammar design, or parser work should begin
until the user re-opens this task for scoping approval - same convention as Tasks 12/13.

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
  default; CLAUDE.md naming rule. Open: sliceAt examples count from 1 (Fusion counts from 0);
  map + map with the same key
- **Next Action:** 30.8 (.len / .length)
