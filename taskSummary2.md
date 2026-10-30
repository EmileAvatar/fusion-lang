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

## TASK 46: `let` / `var`, `match` as a value, `write` - COMPLETE (2026-10-29)

Plan and answers: task/taskSummaryArchive.md. Tests: tests/test_let_var_match.py.

## TASK 32: Classes and interfaces - PLAN (decisions 2026-10-28; awaiting final approval)

User (2026-10-28): "code to an interface, not a concrete type" - the principle has a name:
**"Program to an interface, not an implementation"** (the Gang of Four's *Design Patterns*,
1994); in SOLID it is the **Dependency Inversion Principle** (the D). Java's
`List<String> names = new ArrayList<>()` is the classic example. `foreach` works on anything
that implements a `Collection` interface (Java: `Iterable`). An array has one fixed
implementation; a `List` has a default implementation (never null) and can be given another.

Already decided (FEATURES 32): objects by reference, value types copied; `inherits` (alias
`extends`) for classes; interface names need no `I` prefix; several constructors;
`this(...)`; a circle of constructors is an error; class objects can be null (30.2).

**Decisions (user, 2026-10-28):**
1. `implements` is written out - clear and familiar (Java, C#)
2. Default methods in an interface (a method with a body): built now, as a setting, **off by
   default** - `[interfaces] default_methods = false`
3. A struct does **not** implement an interface - it only holds values. But a struct can
   build on another struct: it gets that struct's fields and adds its own (below)
4. Collection implementations (which `List` / `Map` kinds besides the defaults): a mini-task
   of its own - study Java's and other languages' collections, pick the best cases. They
   live in Fusion modules (fusionlib), not in the compiler; a few core ones are built in
   (arrays, List, Map)
5. Freeing objects: when it goes out of scope, like Rust (the default) - **and** reference
   counting: an object is freed when the last reference to it goes (at the end of the scope
   of the last variable holding it). The basics now; Task 38 continues (Weak for cycles, ...)
6. **Testing rule from now on: test with and without null checking** - a null without a check
   is a NullError that a `catch` handles; with `?.` the code runs on (CLAUDE.md)

**Classes and interfaces (proposed syntax):**
```
interface Shape                          // a contract: what, not how
    float function area()

class Circle implements Shape
    float radius
    constructor(float r)
        radius = r
    float function area() : 3.14159 * radius * radius

void function report(Shape s)            // coded to the interface: any Shape works
    print("{@1}", s.area())              // s null: a NullError (catchable)

void function report2(Shape s)           // the same, with null checking
    print("{@1}", s?.area())             // s null: area() is not run; prints null

List<string> names                       // List is an interface: the default implementation,
                                         // never null
foreach (string n in names)              // anything that implements Collection
```

**32.8 (structs building on structs) - DONE 2026-10-29:** its plan and decisions are in
task/taskSummaryArchive.md (Task 32.8); `typeOf` and converting back are in 32.7 below.

**Sub-tasks (order):**
- 32.1 Methods on structs (`p.move(1, 2)`); `[structs] functions` setting (default off -
  decided 2026-10-24)
- 32.8 Structs building on structs (`implements`), same-name fields, printing a whole struct
- 32.2 Classes: fields, methods, constructors (several, `this(...)`), objects by reference,
  null by default, `this`; freed by scope and reference counting (decision 5)
- 30.2 (from Task 30) the null guard: `?.`, `??`, `== null`, NullError - tested both ways
- 32.5 Interfaces: `interface`, `implements` (several), an interface as a type (variables,
  parameters, lists); the object's own method runs (in C: a table of function pointers per
  class); a missing method is a compile error; default methods behind the setting
- 32.4 The `Collection` interface and `foreach` (45.9): arrays, List, Map implement it; a class
  of your own can, and decides its own looping rules
- 32.6 `List` as an interface with a default implementation (never null)
- 32.9 Mini-task: collection implementations - study Java / C# / Rust / Go / Python, choose
  (for fusionlib); the core ones built in
- 32.7 Inheritance: `inherits` / `extends`, `override`, the parent's method; using a parent
  type (user, 2026-10-29): `typeOf(x)` gives the whole chain, top type first - an Employee
  held as a Person shows `Person.Employee` - so the program can decide whether to convert it
  back to an Employee (how the conversion is written: part of 32.7)
- 32.3 Example program (classes, interfaces, structs building on structs, enums)
- **Settings:** `[structs] functions` (32.1, default false), `[interfaces] default_methods`
  (32.5, default false) - into files/fusionSettings.xml when built; showcase updated
- Note: an interface of the program's own with a type parameter (`Repository<T>`) needs
  generics (Task 33); the built-in `Collection<T>` / `List<T>` can come first

**Follow-up answers (user, 2026-10-28):**
1. Names stay case-sensitive - and a setting: `[source] case_sensitive = true` (default).
   false: `name` and `Name` are the same name. Its description warns to choose it with care;
   when off, the compiler lists every group of names that differ only in case
2. No commas: a comma after a struct field (or after a value of a multi-line enum) is
   ignored - people may be used to typing one. A struct is always written over several lines;
   only an enum may be one line, without commas (`enum Light: Red Yellow Green`)
3. `implements` for structs too; `extends` and `includes` as quick-typing alternatives
4. Yes - and every way an object gains or loses a reference must be listed and handled: a
   mini-task of its own (32.10), very important to get right - the catalogue:
   **Object_Lifetime.md** (5 questions there)

**More sub-tasks:**
- **32.0 Settings housekeeping (user, 2026-10-28) - built code, so planned first:**
  - Setting names in **camelCase** (professional look): `tabWidth`, `allowMixed`,
    `allowUnicodeIdentifiers`, `maxNestingDepth`, `stringWarnLength`, `holdCollections`,
    `maxLength`, `autoWidening`, `maxCallDepth`, `waitAtExit`, ... - read **case-insensitively**
    (`tabwidth`, `TabWidth` work too). The template, loader, docs, tests, showcase, examples
  - `[numbers] overflowWrap` (default false) takes over arithmetic wrapping from `[safety] mode
    = "unsafe"`
  - `[safety] mode`: `safe` (default; `normal` still accepted), `strict` (warnings become
    errors), `unsafe` (the whole project - memory / assembly; nothing more yet). The old
    `mode = "unsafe"` that wrapped arithmetic: a clear error - "now `[numbers] overflowWrap =
    true`"
  - Answers (user, 2026-10-28): `_` may be used and is ignored (a reading aid some people
    prefer) - `tab_width`, `tabWidth`, `TABWIDTH` are the same; new files are written in
    camelCase. `strict`: every warning becomes an error. Approved - build it now
- **32.2 plan (2026-10-30, third version - answers in; truth tables in Classes.md)** - the
  rest of a class (interfaces 32.5, inheritance 32.7 and `?.` 30.2 stay their own sub-tasks):
  - **32.2a Visibility:** class fields private, functions and constructors public by
    default; a class always has a default constructor. Module level: structs, classes and
    enums public by default, functions and module variables private (Classes.md section 1)
  - **32.2b Constructors:** several, chosen by the arguments; `this(...)`; a circle is an
    error; a private constructor is used only inside the class - forms A, B, C and its
    methods (section 2)
  - **32.2c `static`:** forms A (direct), B (self set-up - its own field, reads statics
    already set up), C (`static { }` - any static); A, then B, then C; classes set up by
    dependency, found by following what the set-up names until nothing new; a circle is a
    compile error showing the whole chain (`Car -> Engine -> Parts -> Factory -> Car`: "Factory
    can't use Car - Car is still being set up"); before `main`; freed last; static methods,
    plain statics (section 3)
  - **32.2d Form B on any variable:** a local, a field, a static (section 4) - its block
    changes that variable only
  - **32.2e `readonly` parameters** (Object_Lifetime.md section 3)
  - **32.2f Printing an object:** the class name with a warning until ToString (32.5) -
    section 6
  - **32.2g** the `null == null` bug (gives false)
  - **With 32.5 (interfaces):** `ToString`, `Default` (never null - the object made when
    declared, its constructor may be private; section 5), `Cloneable` / `clone()`, copies of
    objects, nocopy / noshare
  - **Tests:** each table row in Classes.md; with and without null checks (4b); the lifetime
    trace for statics (freed last) and the set-up order
  - **Settings:** none
- 32.10 (object lifetime) - DONE 2026-10-30: its plan and answers are in
  task/taskSummaryArchive.md (Task 32.10)
- 32.11 `[source] case_sensitive` (default true); off: the compiler lists names that differ
  only in case
- 32.12 Commas after struct fields / multi-line enum values are ignored
- **Settings (added):** `[source] case_sensitive`

---

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
  includes for structs; object lifetime - a mini-task, Object_Lifetime.md written)
- Object_Lifetime.md rewritten (user, 2026-10-28): three memory strategies (MANUAL / OWNERSHIP /
  GC, a setting; GC implementations, its thread), free (unsafe) vs deallocate (safe), a full
  function / class / module example, answers 1-5 recorded; 6 new questions there. Nothing
  built until it is 150% sure
- Object_Lifetime.md updated (user, 2026-10-28): OWNERSHIP default, GC optional (also made in
  code), all three at once; `unsafe` functions / blocks; free (unsafe) vs deallocate (safe), use
  after either a compile error; lists / arrays / maps become references (never null);
  readonly / byRef / byVal; constructor forms, private / static constructors, factories
- More answers: freed objects marked (compile error in the same block, run-time elsewhere, `?.`
  treats freed as null); lists references, `byVal` copies; deep copy for byVal on objects
  (other languages compared - Object_Lifetime.md 4b)
- More answers: OverflowWrap (default false) replaces [safety] mode = "unsafe" (arithmetic);
  [safety] mode = "safe" / "unsafe"; [memory] copy deep; copy() / copyDeep(); nocopy / noshare
  field modifiers
- Answers: nocopy - a class with one can't be copied; not both on one field; settings camelCase,
  read case-insensitively; strict = warnings become errors; safe default - 32.0 planned
- 32.0 approved (camelCase, `_` ignored, strict = warnings are errors); Car nocopy + noshare
  example recorded (Object_Lifetime.md - 1 question)
- 32.0 done: camelCase settings read ignoring case and _; overflowWrap; safety safe / strict /
  unsafe (normal accepted, old unsafe warns); strict = warnings are errors
- Cloneable rules + two truth tables (structs / classes / nocopy / Cloneable / noshare; fields
  inside an enclosing object) - Object_Lifetime.md 4b; 6 questions
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
- **Next Action:** 32.2 - the plan above (third version) is ready to build, in order 32.2a-g;
  then 32.5 (interfaces: ToString, Default, Cloneable), then the rest of Task 32 - finish Task
  32, then 36.0 (a small syntax highlighter: VS Code, Sublime Text / TextMate), then Task 47
  (long, money, enums with fixed data) - user, 2026-10-29
