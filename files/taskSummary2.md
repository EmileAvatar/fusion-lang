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
- Done 2026-11-22: 33.4 features tested together - tests/test_generics.py; every Ownership.md 3b row tested;
  Q.042 / Q.043 for the user
- Done 2026-11-22: 33.5 a generic's types from where it is stored (D.171) - `Garage<Car> g = Garage()`
- Done 2026-11-22: 33.6 a local taken from a parameter (D.172, B1) - strict: the function keeps it; `--interface` showing it is 33.7
- Done 2026-11-22: 33.3a a generic class with a plain parent and plain interfaces; fixed: a child held as its parent
  leaked its own object fields (freed / copied through the parent's helpers)
- Done 2026-11-22: 33.3b a generic parent or interface (`inherits Box<T>`, `implements Collection<T>`) - copied before
  inheritance from the types written; fixed: `e is Person` taken for never
- Done 2026-11-22: 33.3c statics on a generic class - one set per copy, `[generics] sharedStatics` (D.173)
- Done 2026-11-22: 33.3d1 a List of your own - `implements List<T>`, the core five written, the rest added (D.174)
- **Next Action:** 33.3d2 a `List<int>` value holding any implementation (D.175); 33.7 after

### 33.3d - plan (to approve): another implementation behind `List<T>` (D.174, D.175)
**Settings:** none. **What it takes:** Fusion's List is a C block (`data`, `len`, ...) with 42 helpers, and some 190
places in the code generator read `->data[i]` / `->len` directly (indexing, foreach, print, `==`, copies, struct text) -
some write into an element in place (`xs[i].x = 5`), which a class's `get(i)` can't give. So D.175 (a `List<int>`
holding a class of your own) is a change through the whole code generator; done in two steps:

**33.3d1 A class implementing `List<T>` - the core five, the rest built from it (D.174)**
- `class Ring<T> implements List<T>` writes `len()`, `get(i)`, `set(i, v)`, `insert(i, v)`, `removeAt(i)`; Fusion
  adds every other List method the class doesn't write (add, contains, indexOf, remove, removeLast, clear, copyPart,
  sort, map, filter, reduce, join, toList ...), written in Fusion from the core five and added to the class as its
  own methods - so they are checked and compiled like any method (a class may write any of them itself to do better)
- on a `Ring<int>` value: every List method, `r[i]` / `r[i] = v` (get / set), `foreach` and `len(r)`, `print`
- a missing core method an error that lists the five; a method with the wrong signature names List's
- tests: each method on a program's own List (an array-backed one and a linked one), strict and relaxed, the leak
  check; example syntax_list_implementation

**33.3d2 A `List<int>` value holding any implementation (D.175)**
- `List<int> xs = Ring()` - a List variable, parameter, field or element holding one; each List operation first
  checks which it is (a flag in the block): the default goes the direct way as today, another through its class
- the ~190 direct uses go through small inline accessors (`len`, element at i); an element changed in place
  (`xs[i].x = 5`) on another implementation: get, change, set
- measured before and after (the examples, a List-heavy loop) - the default must stay as fast; if not, Q.046's C
  (a setting) is the fallback
- tests: every List test run again with a `Ring` behind the `List<int>`; the leak check

**Order:** 33.3d1 first (useful on its own - a List of your own with all 22 methods); 33.3d2 after it.

### 33.3 - plan (to approve): a generic class with a parent, interfaces or statics; another List<T> implementation
**Settings:** `[generics] sharedStatics` (33.3c, D.173 - default false: one set per copy); none else.
Today a generic class with a parent, interfaces or statics is an error ("comes later (Task 33.3)"). The passes for
inheritance (32.7), interfaces (32.5a) and statics (32.2c) run on the generic class itself, before it is taken out
and copied per set of types - so a part that doesn't mention T already works on the template; one that does needs
filling in per copy.

**33.3a A plain parent and plain interfaces** - `class Box<T> inherits Vehicle implements Printable`
- the error lifted for a parent / interfaces that don't mention T; each copy (`Box<int>`, `Box<Car>`) has the parent's
  fields and functions, its own table of virtual functions, answers the interface; `is`, casts, `super(...)`
- a `Box<Car>` given where a `Vehicle` or a `Printable` is expected; a List of them
- tests: each, strict and relaxed, the leak check; mistakes (a missing interface function) name the copy as written

**33.3b A generic parent or interface** - `class Special<T> inherits Box<T>`, `class Bag<T> implements Collection<T>`
- the parent copied for the same types first (`Special<int>` builds on `Box<int>`), then the child; an interface with
  T (`Collection<T>`, `Comparable<T>`) filled in per copy - a generic collection of your own in `foreach`
- a parent with other types (`class IntBox inherits Box<int>`, a plain class on a generic parent) too
- tests as 33.3a; `Bag<int>` as a `Collection<int>` value, its iterator

**33.3c Statics** - D.173: per copy; `[generics] sharedStatics = true` one for all
- `class Box<T>` with `static int made` - one per copy (`Box<int>.made`, `Box<string>.made`) or one for all; a static
  of type T only per copy; the set-up (forms A, B, C) run for each copy used
- tests: each form, the set-up order (32.2c)

**33.3d Another implementation behind `List<T>`** - D.174 (a core of five, the rest built from it), D.175 (a List value holds any; one check per call)
- `class Ring<T> implements List<T>` - what it must write (Q.045); `List<int> xs = Ring()` - a List variable,
  parameter or field holding it, every List method and `xs[i]`, `foreach`, `len` working on it; what it costs (Q.046)
- the default implementation stays as it is (never null, D.001 - code to an interface)
- tests: each List method on a program's own implementation; the default unchanged and as fast; the leak check;
  examples: syntax_generics / a new syntax_list_implementation; 45.10 (an array as a Collection) after it

**Order:** 33.3a, 33.3b, 33.3c, then 33.3d - each shipped on its own. FeatureTree, Decisions TYP.007 / COL.006,
showcase (Interfaces.fusion `List<T>` [designed 32.6] -> built), SYNTAX_REFERENCE examples (Rule 4).

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
