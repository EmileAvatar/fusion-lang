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
- **Next Action:** 33.2c generic classes (and methods on a generic struct)

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
6. **33.3 Another implementation behind `List<T>`** (from 32.6) - a generic class implementing `Collection<T>`;
   45.10 (an array as a Collection<T> value) if it fits
7. **Docs:** spec 110 rewritten, SYNTAX_REFERENCE examples (Rule 4) - one with several types (`<T, T1>`, `<K, V>`)
   kept as a test, files/fusion.ebnf, files/Symbols.md (`:` and `...` get one more job each), the showcase,
   Decisions.md

**Tests going forward:** each part's tests use one type and several (`<T>`, `<T, T1>`, `<K, V>`), with numbers,
strings, structs and objects (the leak check on every one), and a condition broken on purpose for each condition.

**Not in this task:** generic interfaces of your own (`interface Stack<T>`) - after 33.2c if easy, else later;
variance (`List<Dog>` as `List<Animal>`) - no; generics in the self-hosted compiler - Task 35
