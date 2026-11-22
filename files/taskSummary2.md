# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## Task 33 - Generics: the program's own generic functions and types (replanned 2026-11-22 with the user's answers - to approve)

- **Today:** `List<T>`, `Map<K, V>`, `Iterator<T>`, `Collection<T>`, `Entry<K, V>` are built in - each made
  once per element type used (`Collection<Person>` its own interface, `fusion_list_int` its own C functions)
- **Decided (user, 2026-11-22):** D.166 the form, the names and the call; D.167 conditions; D.168 the setting;
  earlier: every type can be written by the programmer (RustZig R3); keep overload rules simple (Z10); a retry
  helper over any async call must compile (RustPitfalls P2 - a test once async exists)
- **Settings:** `[generics] enabled` (default true) - into fusionSettings.xml when built (part 1)

### How it works
- **One copy per type used** (as C++ templates and Rust): `first<int>` and `first<string>` become two C functions;
  no boxing, no run-time cost - the same as List<T> today
- A generic declaration is checked once, on its own, against its conditions - an error in it points at the generic
  code, not at a copy (as C# and Rust); a type that doesn't meet a condition is an error at the use
- The copies are made while type checking, when a use is found, and checked and generated like any function

### The form (D.166, D.167)
```fusion
T function first<T>(List<T> items) : items[0]                 // the form - type parameters after the name
T function first(List<T> items) : items[0]                    // also accepted: T, K, V (and T1, K2 ...) in a signature
V function valueOf<K, V>(Map<K, V> m, K key) : m[key]         // several: Key and Value
T1 function second<T, T1>(List<T> a, List<T1> b) : b[0]      // the result may be any of them
T function firstOf(T... items) : items[0]                     // T... - an array or a List of T is expected

int a = first(numbers)                                        // the types from the arguments - preferred
int b = first<int>(numbers)                                   // or written, if the developer wants
string c = second(numbers, names)                             // T is int, T1 is string

T function biggest<T implements Comparable>(List<T> xs)       // only a type that implements Comparable
T function total<T extends Number>(List<T> xs)                // any number type
int function count<T extends int>(List<T> xs)                 // only int
void function park<T extends Vehicle>(T v)                    // Vehicle or a child of it - anything else rejected
void function park<T : Vehicle>(T v)                          // the same - ':' is quick typing for extends
void function show<T implements Comparable, Printable>(T x)   // two interfaces
void function rank<T extends Vehicle implements Comparable>(T v)   // a parent and an interface

Aircraft[] aircrafts = [...]
biggest(aircrafts)          // a compile error when Aircraft doesn't implement Comparable - named in the message

struct Pair<A, B>                                             // structs and classes too (A, B written in <...>)
    A first
    B second
class Box<T implements Comparable>
    T item
Pair<int, string> p = Pair(1, "a")                            // the types from the values, or written
```
- Without a condition, T can be stored, passed, returned, compared with == / != and printed
- T, K, V (Type, Key, Value) and those with digits name type parameters; any other name is written in `<...>`;
  a struct, class or enum named T, K or V is an error
- `where` stays reserved (D.162) - not used for now

### `T...` (user, 2026-11-22)
```fusion
T function firstOf(T... items) : items[0]
firstOf(aircrafts)            // an array
firstOf(names)                // a List
firstOf(a, b, c)              // values written one by one
show(1, "two", car)           // void function show(T... items) - each value may be of any type
park(car, bus)                // void function park<T extends Vehicle>(T... vs) - every value a Vehicle (or a child)
```
**Understood as (to confirm):**
- With a condition (`extends`, `implements`), the values become one array of that type - the usual case
- Without one, values of different types are a "pack" (as C++'s variadic templates): each keeps its own type, and
  the function is made once for each combination used; inside, each value can do only what a T without a condition
  can - be printed, compared with ==, passed on - and `foreach (T x in items)` runs the body once per value
- That needs functions taking several values first (`int... numbers` - SYN.034, designed: only main's
  `string... args` is built), so `T...` is its own part, after the conditions

- Done 2026-11-22: 33.2a generic functions - src/semantic/generics.py, tests/test_generics.py, example syntax_generics
- Done 2026-11-22: 33.2b generic structs - a copy per set of types (`Pair__int__string`), registered when a type or a call needs it
- Done 2026-11-22: 33.2c generic classes and methods on a generic struct - copied with it; a parent / interfaces / statics later (33.3)
- Done 2026-11-22: 33.2d conditions - checked at each use (call or type written); the generic code itself checked against them later
- Done 2026-11-22: 33.2e1 `int... numbers` / `T...` of one type - a List inside; values, an array or a List
- Done 2026-11-22: 33.2e2 a pack - a copy per combination of types, the loop written out per value
- Done 2026-11-22: 33.2f ranges `1...10` in a for / foreach and `case 0...9` (L7.7); D.169 proposed
- Done 2026-11-22: 33.2g a step on a whole-number range (D.170); `range(10, 0, -1)` counts down now
- **Next Action:** first the review tasks below (before any code changes), then 33.3 another implementation behind
  `List<T>` (and a generic class with a parent / interfaces)

### Before 33.3 - from the ChatGPT review of README.md + FeatureTree.md (user, 2026-11-22; reviewed - Rule 3c)
- Done 2026-11-22: 1 (moved to Notes/), 2 (README), 3 (Ownership.md truth table 3b), 4 (FEATURES 33.4);
  5 stays a plan (designed later); README "Services: Shared State Without Locks" section added (user)
- Approved 2026-11-22 (user): the topic folder list in 6; a syntax_* example's folder from its marker
  (`<!-- example: name | folder: X -->`); next: 6 - the split
- Later README major features, once built (user): HIDL; `Lang.<Language>.Fusion` to run other languages
1. Move `chatgpt review 2026-11-22.md` from the root to `Notes/` (reviews go there); update Main.md if it lists Notes files
2. README.md (Rule 6 - goals, not status):
   - the first line reworded: "Fusion is a configurable programming language and compiler platform. It separates
     language semantics from implementation strategies, allowing projects to configure how their code is compiled,
     executed, managed and optimized without changing what the code means" (was "not a traditional programming
     language ... a configurable compiler platform") - user to approve the wording
   - one small program shown in all three block styles (indentation, braces, End) - syntax without lock-in
   - one line pointing to FeatureTree.md for what is built (status stays out of the README)
   - from its second review (same file, "second review"): the philosophy (code as infrastructure, configurable
     implementation strategies, syntax without lock-in, one owner / one writer, configurable backends); the
     pipeline as a small diagram (source -> lexer -> parser -> AST -> semantic analysis -> C generator -> C -> GCC
     -> native program); a pointer to `examples/` (each has the .fusion, the generated .c and the program); a
     documentation roadmap - links only, no copied content
   - its table puts taskSummary2 in `task/` - it is `files/taskSummary2.md` (a limited view, Rule 3c)
3. files/Ownership.md (Rule 4c): truth-table rows for generics - a pack's values lent (`show(car, bus)`), `T...` values
   retained in a temporary List, a generic class holding an object (`Box<Car>`), a generic struct's fields, a copy per
   set of types; tests for any row not covered yet
4. FEATURES: an interaction test - one program combining generics, ownership, collections, structs and classes, run
   under the leak check (the review's "test existing features together"); scheduled under Task 33 (33.4) or its own
5. A tutorial site in `files/tutorial/` (user, 2026-11-22 - designed later; only the folder and plan for now), in the
   style of w3schools - the review's "Getting Started" level:
   - left: an index bar - headings (collapsible) and sub-headings
   - right: the main page - the tutorial text and its code
   - top: a bar above both - tabs for the major features
   - plain HTML pages; one CSS for the site's styles, one CSS for Fusion code blocks, one JS for all interactivity
   - Main.md and files/CLAUDE.md (if any) list the folder when it is made
6. `examples/` split into numbered topic folders (user, 2026-11-22 - from the second review), easier to follow in order:
   `01_hello_world/`, `02_variables/`, `03_functions/`, `04_control_flow/`, `05_structs/`, `06_classes/`,
   `07_generics/` ... each with its .fusion, .c and program; plan the topic list first (the 105 programs, the
   syntax_* ones from SYNTAX_REFERENCE included)
   - **Proposed topic folders (to approve)** - the 102 programs and 4 project folders:
     - `01_basics/` - hello_world, style_indent / braces / end, syntax_functions_and_blocks,
       syntax_variables_and_control_flow, syntax_let_var, syntax_conditional, syntax_equality, syntax_overflow,
       syntax_number_conditions, syntax_long_lines, syntax_module_variables, syntax_ranges, const_demo, control_flow,
       fizzbuzz, factorial, max_three, calculator
     - `02_functions/` - functions_demo, syntax_defaults_and_named_args, syntax_functions_as_methods, syntax_lambdas,
       syntax_templates, syntax_variadic, syntax_at_the_call
     - `03_strings/` - strings_demo, syntax_strings, syntax_string_library / operations / put, syntax_interpolation,
       syntax_unicode, syntax_bytes, syntax_to_string
     - `04_arrays/` - arrays_demo, sum_array, syntax_arrays, syntax_array_* (6), syntax_growable_array, syntax_jagged,
       syntax_length, syntax_many_dims* (5)
     - `05_collections/` - syntax_lists, syntax_list_collection, syntax_list_options, syntax_maps, syntax_map_entries,
       syntax_foreach, syntax_shared_lists
     - `06_match_and_enums/` - syntax_match, syntax_match_value, syntax_fall_match, syntax_enums, syntax_enum_bare,
       syntax_enum_data
     - `07_structs/` - structs_demo, syntax_structs, syntax_struct_* (5)
     - `08_classes/` - classes_demo, syntax_classes, syntax_methods, syntax_statics, syntax_setup_blocks, syntax_getters,
       syntax_default, syntax_object_copies, syntax_object_text, syntax_inheritance, syntax_interfaces
     - `09_generics/` - syntax_generics, syntax_generic_conditions, syntax_variadic_pack
     - `10_errors_and_null/` - errors_demo, syntax_errors, syntax_error_types, syntax_try, syntax_null_enums,
       syntax_null_guard
     - `11_ownership/` - syntax_moving, syntax_borrowing, syntax_readonly, syntax_readonly_result, syntax_one_writer
     - `12_files_and_programs/` - syntax_files, syntax_program_io, syntax_run, syntax_write
     - `13_projects/` - expressions, project_config_demo, shop, wordcount (folders as they are)
   - the syntax_* programs are written from SYNTAX_REFERENCE's `<!-- example: name -->` markers - the folder could
     come from the marker (`<!-- example: syntax_ranges | folder: 01_basics -->`) or from the SYNTAX_REFERENCE
     section it sits in; a new example then lands in the right folder
   - update with it: `examples/#list.csv` and `examples/#run.bat`, `check.py --build-examples` (where it writes),
     `tests/verify_examples.py`, the reference / leaks checks, `examples/CLAUDE.md`, Main.md, any links to examples
- Not taken: "Current development status" / "What can I do today" in the README (Rule 6 - FeatureTree.md holds it;
  the second review agrees)

### Parts, in order (each shipped on its own)
1. **33.2a Generic functions:** the forms above without conditions; T, K, V (and digits) without `<...>`; types from the
   arguments or written; one type or several (`<T, T1>`, `<K, V>`); T as a parameter, result, local, List<T> /
   Map<K, V> / T[]; an error when a type can't be worked out ("write first<int>(...)"); one C function per
   set of types, its C name from them (`fu_first__int`); `[generics] enabled` - off: a generic declaration an error
2. **33.2b Generic structs:** `struct Pair<A, B>`; `Pair<int, string> p = Pair(1, "a")`; fields, copies, ==, text
3. **33.2c Generic classes:** `class Box<T>`, its methods and constructor; `Box<Person>`; ownership as today
4. **33.2d Conditions:** `extends` / `:` (a class or struct and its children), `extends Number` (any number),
   `extends int` (only int), `implements` - one or two at once; on functions, structs and classes; what each lets
   the generic code do (Comparable: compareTo; Number: + - * / < >; Vehicle: its fields and methods); a type that
   doesn't meet one - a compile error at the use, naming the type and the condition
5. **33.2e `T...` and `int... numbers`:** a function taking several values (SYN.034) - an array, a List or
   values one by one; with a condition one type; without one a pack of types, the function made per combination
6. **33.2f Ranges `1...100` in a `for`** (user, 2026-11-22): the same `...` as 33.2e; tested next to `range(...)`;
   both ends included, no step, `10...1` an error suggesting `range(10, 0, -1)` (settled when built, D.161);
   L7.7 `case 0...9` with it if it fits
7. **33.3 Another implementation behind `List<T>`** (from 32.6) - a generic class implementing `Collection<T>`;
   45.10 (an array as a Collection<T> value) if it fits
8. **Docs:** spec 110 rewritten, SYNTAX_REFERENCE examples (Rule 4) - one with several types (`<T, T1>`, `<K, V>`)
   kept as a test, files/fusion.ebnf, files/Symbols.md (`:` and `...` get one more job each), the showcase,
   Decisions.md

**Tests going forward:** each part's tests use one type and several (`<T>`, `<T, T1>`, `<K, V>`), with numbers,
strings, structs and objects (the leak check on every one), and a condition broken on purpose for each condition.

**Not in this task:** generic interfaces of your own (`interface Stack<T>`) - after 33.2c if easy, else later;
variance (`List<Dog>` as `List<Animal>`) - no; generics in the self-hosted compiler - Task 35
