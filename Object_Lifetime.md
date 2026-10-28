# Object lifetime: when an object is freed

Every case where a class object gains or loses a reference, so that each object is freed
exactly once, at the right time, and never used after it is freed. A design document for
Task 32 (classes) - a mini-task of its own (32.10). Status: **being designed** (user,
2026-10-28). Task 38 (the memory model: Unique / Shared / Weak, GC as an option) continues
from here.

---

## 1. The rule

**Decided (user, 2026-10-28):** scope-based freeing, like Rust, **and** reference counting.

- Every object carries a **count**: how many places hold it
- A place that takes the object adds 1; a place that lets go subtracts 1
- **At 0 the object is freed** - at once, not later (no garbage collector pauses)
- An object only one variable holds is freed exactly when that variable's scope ends
  (Rust's rule); an object several places hold is freed when the last one lets go (Swift's
  rule)
- Freeing an object lets go of everything it holds - its fields, in turn (a cascade)

**What "a place that holds an object" is:**

| Holder | Example |
|---|---|
| A local variable | `Circle c = Circle(2.0)` |
| A parameter | `void function draw(Shape s)` |
| A field of an object | `this.helper = Helper()` |
| A module variable | `Logger log = Logger()` outside any function |
| An element of an array, List or Map (key or value) | `shapes.add(c)`, `byName["a"] = c` |
| A temporary - a value nobody stored | `makeCircle().area()` |
| The data of an error | a custom error type holding an object (Task 26.9) |
| Later: a closure, a thread or service's mailbox (Tasks 42, 18.3 closures) | |

---

## 2. When the count goes up (+1)

| # | Case | Example | Notes |
|---|---|---|---|
| U1 | Created and stored | `Circle c = Circle(2.0)` | the new object starts at 1 - the variable holds it |
| U2 | Assigned from another holder | `Circle d = c` | both hold the same object: 2 |
| U3 | Stored in a field | `this.helper = h` | |
| U4 | Stored in a collection | `shapes.add(c)`, `list[0] = c`, `map["k"] = c` | each element is a holder |
| U5 | Returned to a caller who stores it | `Circle c = make()` | the returned object moves to the caller - no extra count |
| U6 | A collection copied (`List<Shape> b = a`) | the new list holds the same objects - each +1 (question 2) | |
| U7 | A struct holding an object copied | only if `[structs] classes` is on (off by default) | |
| U8 | Passed as an argument | `draw(c)` | borrowed - no count change while the call runs; +1 only if the function stores it (question 1) |
| U9 | `this` returned or stored by a method | `return this`, `list.add(this)` | +1 where it is stored |

---

## 3. When the count goes down (-1)

#### Leaving a scope

| # | Case | Example | What happens |
|---|---|---|---|
| D1 | A block ends | the `}` / dedent / `End if` after `Circle c = ...` | every object variable of the block: -1 |
| D2 | A function ends normally | the last line runs | its locals and the parameters it took over: -1 |
| D3 | `return` | `return area` in the middle of a function | every scope being left: -1 - but not the object being returned (it moves to the caller) |
| D4 | `break` / `continue` | inside a loop body that holds objects | the scopes inside the loop: -1, each pass |
| D5 | `break` in a `match` | (Task 30.12) | the case's scopes: -1 |
| D6 | An error raised (`return Error(...)`, a failing call) | the error travels up | every scope it leaves: -1, at each level |
| D7 | `throw` until a `catch` | | every scope between the throw and the catch: -1; a `finally` runs first |
| D8 | A loop pass ends | `while` / `for` body | objects created in the body: -1 at the end of each pass, not only after the loop |
| D9 | The program ends | `main` returns, `exit(code)`, a run-time error | everything still held: -1 (module variables last); the leak check expects 0 |

#### Replacing what a holder holds

| # | Case | Example | What happens |
|---|---|---|---|
| R1 | A variable gets another object | `c = Circle(3.0)` | the new one +1 first, then the old one -1 - so `c = c` is safe |
| R2 | A variable is set to null | `c = null` | the old one -1 |
| R3 | A field gets another object | `this.helper = Helper()` (a method making a new object for its field) | new +1, old -1 |
| R4 | A collection element replaced | `list[0] = d`, `map["k"] = d` | new +1, old -1 |
| R5 | Swapping two holders | `t = a; a = b; b = t` | counts end where they started |

#### Collections letting go

| # | Case | Example | What happens |
|---|---|---|---|
| C1 | An element removed | `removeAt`, `remove`, `removeLast` / `pop`, `map.remove(k)` | that object -1 (if the removed object is returned and stored: it moves) |
| C2 | Cleared | `list.clear()`, `map.clear()` | every element -1 |
| C3 | The collection itself freed | its scope ends / it is replaced | every element -1 |
| C4 | A part copied | `copyPart`, `filter`, `map` | the new collection's elements +1 each |

#### Temporaries

| # | Case | Example | What happens |
|---|---|---|---|
| T1 | A result nobody stores | `makeCircle()` as a statement | -1 at the end of the statement - freed at once |
| T2 | A result used once | `makeCircle().area()`, `print("{makeCircle()}")` | -1 at the end of the statement |
| T3 | Inside `(c) ? a : b` | only the chosen value is made | as T2 |
| T4 | A `match` subject | `match makeShape()` | held while the cases run, -1 when the match ends (or a case leaves early) |

#### Objects holding objects

| # | Case | Example | What happens |
|---|---|---|---|
| O1 | An object freed | its count reaches 0 | each of its object fields -1 - which may free them in turn (a cascade) |
| O2 | A constructor fails half way | an error after some fields were set | the fields set so far -1, the half-made object freed - the caller gets the error, never the object |
| O3 | Two objects holding each other (a cycle) | `a.friend = b; b.friend = a` | the counts never reach 0 - a leak. **Needs Weak (Task 38)**; until then the leak check reports it (question 4) |
| O4 | An object holding itself | `node.next = node` | the same - a cycle of one |

---

## 4. What never changes the count

- Reading a field, calling a method, comparing (`==`, `===`, `is null`), printing
- A parameter while the call runs (borrowed - U8)
- `this` inside a method
- The loop variable of `for x in list` / `foreach` - it borrows each element in turn (the list
  holds it)

---

## 5. Questions to settle in the mini-task (32.10)

1. **Parameters:** borrowed - no count while the call runs, +1 only when the function stores
   the object (fast; how strings work today - recommended), or +1 on every call?
2. **Copying a collection or struct that holds objects** (`List<Shape> b = a`): the new list
   holds the **same** objects (+1 each - as Java, C#, Swift; recommended), or copies of the
   objects (a deep copy)?
3. **A clean-up method** run when an object is freed (`destructor()`, Swift's `deinit`) - to
   close a file or a connection: now, or later?
4. **Cycles** before Task 38's Weak: the leak check reports them (recommended), and the
   compiler warns where it can see one (a class holding its own type)?
5. **Threads** (Task 42): counts change from several threads at once - they must then be
   atomic; with Task 42

---

## 6. Decisions log

| Date | Decision |
|---|---|
| 2026-10-28 | Objects are freed by scope (like Rust) and by reference counting: at 0, at once |
