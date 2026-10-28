# Object lifetime: when an object is freed

Every case where a class object gains or loses a reference, so that each object is freed
exactly once, at the right time, and never used after it is freed. A design document for
Task 32 (classes) - a mini-task of its own (32.10) - and the base for Task 38 (the memory
model). Status: **being designed** (user decisions 2026-10-28). Nothing here is built yet:
"we need to be 150% sure before creating any code on this".

---

## 1. Three memory strategies (a project setting)

Fusion lets a project choose how memory is managed (user, 2026-10-28):

| Strategy | Like | How an object is freed | For |
|---|---|---|---|
| **OWNERSHIP** (scope) | Rust (+ reference counting, as Swift) | when the last place holding it lets go - at once, usually when a scope ends | most programs: no pauses, no manual work |
| **GC** (garbage collection) | Java, C# | a collector finds objects nothing can reach and frees them later | programs with many shared objects and cycles |
| **MANUAL** | C | the program frees each object itself: `free(x)` / `deallocate(x)` | hardware, embedded, full control |

```toml
[memory]
strategy = "ownership"    # ownership | gc | manual   (default: question 1)
```

- **GC has several implementations** - for a single-core processor, a multi-core processor,
  and none at all: on an embedded device without spare memory, GC is turned off
- **GC runs on a thread** - a shared one (the default) or its own (dedicated), depending on
  the implementation (Task 42's thread model)
- **The app can still use manual freeing and GC** whatever the strategy (user) - how they
  combine is question 2
- The spec's "Memory Management" section names GC as the default (an older design) - this
  document and the setting replace it once decided

---

## 2. The two ways to free by hand

| Call | Safe? | What it does | For |
|---|---|---|---|
| `deallocate(x)` | **safe** - the default way | checks the count: frees only when nothing else holds the object; freeing something already freed does nothing (an error only if a setting asks for it) | normal use; also what the compiler and the GC use internally |
| `free(x)` | **unsafe** - raw | frees the memory at once, whatever holds it; freeing twice can crash or corrupt memory | hardware, embedded - when the developer must control exactly when memory goes |

- Normally a developer uses `free` / `deallocate` only with `strategy = "manual"`
- After `free(honda)`, `honda` is marked as freed: using it again is reported (question 5)

```toml
[memory]
double_free = "ignore"    # deallocate on something already freed: ignore (default) | error
```

---

## 3. The rule for OWNERSHIP (the counting)

- Every object carries a **count**: how many places hold it
- A place that takes the object adds 1; a place that lets go subtracts 1
- **At 0 the object is freed** - at once (no collector pauses)
- An object only one variable holds is freed exactly when that variable's scope ends
  (Rust's rule); an object several places hold is freed when the last one lets go (Swift's)
- Freeing an object lets go of everything it holds - its fields, in turn (a cascade)

**What passing does (user, 2026-10-28):**
- **Value types** (numbers, bools, chars, structs) are copied - the function can't change
  the caller's value
- **Strings** are copied
- **Class objects** are passed by reference, borrowed (no count change while the call runs)
  - the function **can change** the object, and the caller sees it
- **Arrays, lists and maps:** the function can change their values (user) - see question 3

**Places that hold an object:**

| Holder | Example |
|---|---|
| A local variable | `Car honda = Car()` |
| A parameter | `void function service(Car c)` |
| A field of an object | `engine = Engine("V8")` inside `Car` |
| A module variable | `Garage garage = Garage()` outside any function |
| An element of an array, List or Map (key or value) | `cars.add(honda)`, `byName["a"] = honda` |
| A temporary - a value nobody stored | `Car().describe()` |
| The data of an error | a custom error type holding an object (Task 26.9) |
| Later: a closure, a thread or service's mailbox (Task 42) | |

---

## 4. A full example - function, class and module level

The count of each object is shown after each line (OWNERSHIP strategy).

```fusion
// ---------------------------------------------------------------- module level
class Engine
    string kind
    Engine(string kind)
        this.kind = kind

class Car
    private Engine engine
    string name
    Car(string name)
        this.name = name
        engine = Engine("V8")               // the new Engine: 1 (this car's field holds it)
    void function swapEngine(string kind)
        engine = Engine(kind)               // new Engine: 1; old Engine: 0 -> freed
    Engine function getEngine() : engine    // the caller that stores it adds 1

class Garage
    List<Car> cars
    void function park(Car c)               // c is borrowed - no count change
        cars.add(c)                         // the list holds it: +1
    Car function leave(int i)
        Car c = cars[i]                     // +1
        cars.removeAt(i)                    // -1 (the list let go)
        return c                            // moves to the caller - no change

Garage garage = Garage()                    // a module variable: Garage 1, held until the
                                            // program ends (freed last)

// ---------------------------------------------------------------- function level
void function testDrive()
    Car honda = Car("Honda")                // Car 1, its Engine 1
    Engine e = honda.getEngine()            // Engine 2 (the car's field + e)
    honda.swapEngine("V6")                  // V6: 1; V8: 1 (only e holds it now)
    honda = null                            // Car 0 -> freed -> its V6 engine 0 -> freed
    print(e.kind)                           // "V8" - e still holds the old engine
                                            // end of testDrive: e goes -> V8 0 -> freed

void function main()
    testDrive()
    Car toyota = Car("Toyota")              // Car 1
    garage.park(toyota)                     // Car 2 (toyota + the garage's list)
    toyota = null                           // Car 1 - the garage still holds it: not freed
    Car back = garage.leave(0)              // the list let go, back holds it: Car 1
    Car().name                              // a temporary Car: made, used, 0 -> freed at once
                                            // end of main: back goes -> Car 0 -> freed
                                            // (and its Engine); program end: garage 0 ->
                                            // freed, and its (empty) list
```

**The same with MANUAL:**

```fusion
void function main()
    Car honda = Car("Honda")
    print(honda.name)
    deallocate(honda)                       // safe: nothing else holds it -> freed (and its
                                            // Engine)
    Car bmw = Car("BMW")
    free(bmw)                               // unsafe: freed at once, no checks
    // print(bmw.name) here: bmw is marked freed - reported (question 5)
```

---

## 5. When the count goes up (+1)

| # | Case | Example | Notes |
|---|---|---|---|
| U1 | Created and stored | `Car honda = Car("Honda")` | starts at 1 - the variable holds it |
| U2 | Assigned from another holder | `Car d = honda` | both hold the same object: 2 |
| U3 | Stored in a field | `engine = Engine("V8")`, `this.owner = p` | |
| U4 | Stored in a collection | `cars.add(c)`, `list[0] = c`, `map["k"] = c` | each element is a holder |
| U5 | Returned to a caller who stores it | `Car c = garage.leave(0)` | moves to the caller - no extra count |
| U6 | A collection copied | the new collection refers to the **same** objects - each +1 (user, 2026-10-28) | |
| U7 | A struct holding an object copied | only if `[structs] classes` is on (off by default) | +1 per object |
| U8 | Passed as an argument | `garage.park(toyota)` | borrowed - no change while the call runs; +1 only where the function stores it |
| U9 | `this` stored or returned by a method | `list.add(this)`, `return this` | +1 where it is stored |

---

## 6. When the count goes down (-1)

#### Leaving a scope

| # | Case | Example | What happens |
|---|---|---|---|
| D1 | A block ends | the end of an `if`, a loop body, a `{ }` | every object variable of the block: -1 |
| D2 | A function ends normally | the last line runs | its locals: -1 |
| D3 | `return` | `return c` in the middle | every scope being left: -1 - except the returned object (it moves) |
| D4 | `break` / `continue` | inside a loop body holding objects | the scopes inside the loop: -1, each pass |
| D5 | `break` in a `match` | (Task 30.12) | the case's scopes: -1 |
| D6 | An error raised | `return Error(...)`, a call that fails | every scope it leaves: -1, at each level |
| D7 | `throw` until a `catch` | | every scope between them: -1; `finally` runs first |
| D8 | A loop pass ends | `while` / `for` body | objects made in the body: -1 at the end of each pass |
| D9 | The program ends | `main` returns, `exit(code)`, a run-time error | everything still held: -1; module variables last |

#### Replacing what a holder holds

| # | Case | Example | What happens |
|---|---|---|---|
| R1 | A variable gets another object | `honda = Car("New")` | new +1 first, then old -1 - so `c = c` is safe |
| R2 | A variable set to null | `honda = null` | old -1 |
| R3 | A field gets another object | `engine = Engine(kind)` in `swapEngine` | new +1, old -1 |
| R4 | A collection element replaced | `list[0] = d`, `map["k"] = d` | new +1, old -1 |
| R5 | Swapping two holders | `t = a; a = b; b = t` | counts end where they started |

#### Collections letting go

| # | Case | Example | What happens |
|---|---|---|---|
| C1 | An element removed | `removeAt`, `remove`, `removeLast` / `pop`, `map.remove(k)` | -1 (a removed object that is returned and stored moves) |
| C2 | Cleared | `list.clear()`, `map.clear()` | every element -1 |
| C3 | The collection itself freed | its holder lets go of it | every element -1 |
| C4 | A part copied | `copyPart`, `filter`, `map` | the new collection's elements +1 each |

#### Temporaries

| # | Case | Example | What happens |
|---|---|---|---|
| T1 | A result nobody stores | `Car("x")` as a statement | -1 at the end of the statement - freed at once |
| T2 | A result used once | `Car("x").name`, `print("{makeCar()}")` | -1 at the end of the statement |
| T3 | Inside `(c) ? a : b` | only the chosen one is made | as T2 |
| T4 | A `match` subject | `match makeShape()` | held while the cases run, -1 when the match ends (or a case leaves early) |

#### Objects holding objects

| # | Case | Example | What happens |
|---|---|---|---|
| O1 | An object freed | its count reaches 0 | each of its object fields -1 - which may free them in turn |
| O2 | A constructor fails half way | an error after `engine` was set | the fields set so far -1, the half-made object freed - the caller gets the error, never the object |
| O3 | Two objects holding each other (a cycle) | `a.friend = b; b.friend = a` | the counts never reach 0 - a leak. Needs Weak (Task 38) or GC |
| O4 | An object holding itself | `node.next = node` | the same - a cycle of one |

#### What never changes the count

- Reading a field, calling a method, comparing (`==`, `===`, `is null`), printing
- A parameter while the call runs (borrowed)
- `this` inside a method
- The loop variable of `for x in list` / `foreach` - it borrows each element in turn

---

## 7. Leaks, debug messages and threads (user, 2026-10-28)

- **Leak reports:** while developing, the compiler warns where it can see a cycle (a class
  holding its own type), and the leak check reports what was never freed
- **The leak check may be turned off, or built into the app**
- **A published app never shows debug messages to the customer** - it only logs them, as the
  company's policy says, or as the app's own logging does
- **Threads:** counts that change from several threads at once must be atomic; the GC and the
  counting run on a shared thread (default) or a dedicated one (Task 42)

---

## 8. Questions still open

1. **The default strategy:** OWNERSHIP (scope + counting - the earlier decision, recommended)?
   The old spec section says GC
2. **"The app can still use manual and GC"** - which combinations? E.g. with OWNERSHIP:
   `deallocate` / `free` allowed in `unsafe` code, and a GC that runs only to find cycles
   (as Python does)?
3. **Arrays, lists and maps passed to a function** - "the function can change the values":
   today a function gets its own copy, and the caller's list never changes. Should a list
   become a reference, as in Java and C# (the caller sees `xs.add(5)` made in a function)?
   That changes how lists work now, and `b = a` too (one list, or a copy?) - a sub-task of
   its own if yes
4. **Constructors:** named like the class, `Car(string name)` (Java, C#, your example) or
   `constructor(...)` (the spec)? And `new` optional: `Car()` and `new Car()` both work?
5. **Using a freed object** after `free(x)` (MANUAL): marked, so using it is a NullError-like
   error (safe, a small cost), or nothing checked in raw `unsafe` code?
6. **Settings names** (proposed): `[memory] strategy`, `[memory] gc = "single-core" |
   "multi-core" | "off"`, `[memory] gc_thread = "shared" | "dedicated"`, `[memory]
   double_free`, `[diagnostics] leak_check = "dev" | "off" | "log"`

---

## 9. Decisions log

| Date | Decision |
|---|---|
| 2026-10-28 | Three strategies as a setting: MANUAL (C), OWNERSHIP (scope, like Rust, + reference counting), GC (Java; several implementations - single-core, multi-core, off for embedded; on a shared or dedicated thread) |
| 2026-10-28 | `free(x)`: unsafe, raw, at once (hardware / embedded). `deallocate(x)`: safe - checks the count, a second free does nothing (an error only by a setting); what the compiler and the GC use |
| 2026-10-28 | Parameters: class objects borrowed, by reference (the function can change them); value types and strings copied |
| 2026-10-28 | Copying a collection that holds objects: the new one refers to the same objects |
| 2026-10-28 | Leaks: warned in development; the leak check can be off or built into the app; a published app logs, never shows debug messages to the customer |
| 2026-10-28 | Atomic counts with threads; a shared (default) or dedicated thread |
