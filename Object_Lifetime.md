# Object lifetime: when an object is freed

Every case where a class object gains or loses a reference, so that each object is freed
exactly once, at the right time, and never used after it is freed. A design document for
Task 32 (classes) - a mini-task of its own (32.10) - and the base for Task 38 (the memory
model). Status: **being designed** (user decisions 2026-10-28). Nothing here is built yet:
"we need to be 150% sure before creating any code on this".

---

## 1. Three memory strategies (a project setting)

| Strategy | Like | How an object is freed | For |
|---|---|---|---|
| **OWNERSHIP** (scope) - **the default** | Rust (+ reference counting, as Swift) | when the last place holding it lets go - at once, usually when a scope ends | most programs: no pauses, no manual work |
| **GC** (garbage collection) - optional | Java, C# | a collector finds objects nothing can reach and frees them later | many shared objects, cycles, external libraries |
| **MANUAL** | C | the program frees each object itself: `deallocate(x)` / `free(x)` | hardware, embedded, full control |

```toml
[memory]
strategy = "ownership"    # ownership (default) | gc | manual
```

**All three can be used at once (user, 2026-10-28):**
- With **MANUAL** the program must free what it makes
- With **GC** as the strategy, a GC is added automatically - nothing to create
- With **OWNERSHIP**, a GC can still be made in code where it helps - as a backup and
  clean-up when a part of the program makes very many objects, or uses external libraries
  that may not manage memory correctly (Fusion libraries, DLLs, other languages' libraries):

```fusion
void function importData()
    GC gc = new GC(...)          // a collector for this part of the program
    ...
```

- **GC implementations:** several - for a single-core processor, a multi-core processor, and
  none at all (an embedded device without spare memory turns GC off)
- **GC's thread:** a shared one (the default) or its own (dedicated), depending on the
  implementation (Task 42's thread model)
- The spec's "Memory Management" section names GC as the default (an older design) - this
  document replaces it

---

## 2. `unsafe`, `free` and `deallocate`

#### `unsafe` - where the program takes direct control

```fusion
unsafe void function fillBuffer(Buffer b)    // a whole function marked unsafe
    ...
    free(b)

void function render()
    ...
    unsafe {                                 // or a block inside a method
        deallocate(frame)
        // later: assembly code, direct device access (with HIDL, Task 41)
    }
```

- For performance-critical code that needs more direct control, assembly code, and direct
  control of a device (combined with HIDL where needed)
- `free` / `deallocate` belong in `unsafe` code or a MANUAL project: used anywhere else, the
  compiler **warns**
- (Fusion already has `unchecked { }` - arithmetic that wraps, Task 27.2d - and `[safety] mode
  = "unsafe"` for the whole project; question 1 below)

#### The two ways to free by hand

| Call | Safe? | What it does | For |
|---|---|---|---|
| `deallocate(x)` | **safe** - the default way | checks the count: frees only when nothing else holds the object; on something already freed it does nothing (or an error, by `double_free`) | normal manual freeing; also what the compiler and the GC use internally |
| `free(x)` | **unsafe** - raw | frees the memory at once, whatever holds it; freeing twice can crash or corrupt memory | hardware, embedded - exact control over when memory goes |

- **After `free(x)` or `deallocate(x)`, using `x` is a compile error - always.** The memory is
  gone and can't be used again
- **`x = null` is different:** the variable can be used again - for a new object
- **`double_free`** - what `deallocate` does when it is given something already freed (for
  example, freed in another function): `"ignore"` (default - nothing happens) or `"error"`
  (a run-time error that names the place, to find such mistakes while developing)

---

## 3. Passing values and objects

**Decided (user, 2026-10-28):**
- **Value types** - int, float, bool, char, decimal, structs, **strings**: passed **by value**
  (a copy) - the function can't change the caller's value
- **Reference types** - class objects, **arrays, lists and maps**: passed **by reference** - the
  function can change them, and the caller sees it. Arrays, lists and maps become references
  (today they are copied) but are still treated like values in one way: **never null**
  (unless a `nullable` setting allows it)
- A class object passed is borrowed - no count change while the call runs

**Modifiers on a parameter:**

| Modifier | Meaning | Default for |
|---|---|---|
| `readonly` | the function may read but never change it - any change is a compile error | - |
| `byRef` | the function may change the caller's variable or object | reference types (classes, arrays, lists, maps) - implicit |
| `byVal` | the function gets a copy; the caller's value never changes | value types (int, string, decimal, structs) - implicit |

```fusion
public void function addMoney(readonly BankAccount account, money amount)
    account.balance = account.balance + amount     // compile error - account is readonly

public money function readBalance(readonly BankAccount account)
    return account.balance                         // fine - only reading

void function addOne(byRef int count)              // an int the function may change
    count = count + 1                              // the caller's variable changes

void function sorted(byVal List<int> numbers)      // a copy of the whole list
    numbers.sort()                                 // the caller's list is untouched
```

---

## 4. Constructors

- **`constructor(...)` is the default form** - easy to see. `Car(...)` (named like the class)
  is quick typing for it
- **`new` is optional:** `Car("x")` and `new Car("x")` are the same - `new` is for those who want
  to show a new object is being made
- **Private constructors** (as in Java): only the class itself can make its objects - for a
  factory, or a class that makes a fixed set of objects:

```fusion
class Car
    string make
    private constructor(string make)           // nobody outside can make a Car
        this.make = make
    const static Car HONDA = new Car("Honda")  // made by the class itself - only possible
    const static Car TOYOTA = new Car("Toyota") // inside the class
    const static Car BMW = new Car("BMW")

Car mine = Car.HONDA
```

- Also a **private static constructor** - code the class runs once, to set up its statics

---

## 5. The rule for OWNERSHIP (the counting)

- Every object carries a **count**: how many places hold it
- A place that takes the object adds 1; a place that lets go subtracts 1
- **At 0 the object is freed** - at once (no collector pauses)
- An object only one variable holds is freed exactly when that variable's scope ends
  (Rust's rule); an object several places hold is freed when the last one lets go (Swift's)
- Freeing an object lets go of everything it holds - its fields, in turn (a cascade)

**Places that hold an object:**

| Holder | Example |
|---|---|
| A local variable | `Car honda = Car()` |
| A parameter (only when the function stores it) | `void function service(Car c)` |
| A field of an object | `engine = Engine("V8")` inside `Car` |
| A static field of a class | `const static Car HONDA` - held until the program ends |
| A module variable | `Garage garage = Garage()` outside any function |
| An element of an array, List or Map (key or value) | `cars.add(honda)`, `byName["a"] = honda` |
| A temporary - a value nobody stored | `Car().describe()` |
| The data of an error | a custom error type holding an object (Task 26.9) |
| A GC made in code (`GC gc = new GC(...)`) | the objects it watches |
| Later: a closure, a thread or service's mailbox (Task 42) | |

---

## 6. A full example - module, class and function level

The count of each object is shown after each line (OWNERSHIP strategy).

```fusion
// ---------------------------------------------------------------- module level
class Engine
    string kind
    constructor(string kind)
        this.kind = kind

class Car
    private Engine engine
    string name
    constructor(string name)
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
    Car("Temp").name                        // a temporary Car: made, used, 0 -> freed at once
                                            // end of main: back goes -> Car 0 -> freed
                                            // (and its Engine); program end: garage 0 ->
                                            // freed, and its (empty) list
```

**The same with MANUAL (or in `unsafe` code):**

```fusion
void function main()
    Car honda = Car("Honda")
    print(honda.name)
    deallocate(honda)                       // safe: nothing else holds it -> freed (and its
                                            // Engine)
    // print(honda.name) here: a compile error - honda was freed
    honda = Car("New Honda")                // fine? (question 3)
    Car bmw = Car("BMW")
    free(bmw)                               // unsafe: freed at once, no checks
```

---

## 7. When the count goes up (+1)

| # | Case | Example | Notes |
|---|---|---|---|
| U1 | Created and stored | `Car honda = Car("Honda")` | starts at 1 - the variable holds it |
| U2 | Assigned from another holder | `Car d = honda` | both hold the same object: 2 |
| U3 | Stored in a field | `engine = Engine("V8")`, `this.owner = p` | |
| U4 | Stored in a collection | `cars.add(c)`, `list[0] = c`, `map["k"] = c` | each element is a holder |
| U5 | Returned to a caller who stores it | `Car c = garage.leave(0)` | moves to the caller - no extra count |
| U6 | A collection copied (`byVal`) | the copy refers to the **same** objects - each +1 | |
| U7 | A struct holding an object copied | only if `[structs] classes` is on (off by default) | +1 per object |
| U8 | Passed as an argument | `garage.park(toyota)` | borrowed - no change while the call runs; +1 only where the function stores it |
| U9 | `this` stored or returned by a method | `list.add(this)`, `return this` | +1 where it is stored |
| U10 | A static field set | `const static Car HONDA = new Car("Honda")` | held until the program ends |

---

## 8. When the count goes down (-1)

#### Leaving a scope

| # | Case | Example | What happens |
|---|---|---|---|
| D1 | A block ends | the end of an `if`, a loop body, `unsafe { }` | every object variable of the block: -1 |
| D2 | A function ends normally | the last line runs | its locals: -1 |
| D3 | `return` | `return c` in the middle | every scope being left: -1 - except the returned object (it moves) |
| D4 | `break` / `continue` | inside a loop body holding objects | the scopes inside the loop: -1, each pass |
| D5 | `break` in a `match` | (Task 30.12) | the case's scopes: -1 |
| D6 | An error raised | `return Error(...)`, a call that fails | every scope it leaves: -1, at each level |
| D7 | `throw` until a `catch` | | every scope between them: -1; `finally` runs first |
| D8 | A loop pass ends | `while` / `for` body | objects made in the body: -1 at the end of each pass |
| D9 | The program ends | `main` returns, `exit(code)`, a run-time error | everything still held: -1; module variables and statics last |

#### Replacing what a holder holds

| # | Case | Example | What happens |
|---|---|---|---|
| R1 | A variable gets another object | `honda = Car("New")` | new +1 first, then old -1 - so `c = c` is safe |
| R2 | A variable set to null | `honda = null` | old -1; the variable can be used again |
| R3 | A field gets another object | `engine = Engine(kind)` in `swapEngine` | new +1, old -1 |
| R4 | A collection element replaced | `list[0] = d`, `map["k"] = d` | new +1, old -1 |
| R5 | Swapping two holders | `t = a; a = b; b = t` | counts end where they started |

#### Freed by hand

| # | Case | Example | What happens |
|---|---|---|---|
| F1 | `deallocate(x)` | nothing else holds it | freed (and what it holds, -1 each); using `x` afterwards: a compile error |
| F2 | `deallocate(x)` | something else still holds it | not freed - `x` lets go (-1); using `x` afterwards: a compile error |
| F3 | `free(x)` | unsafe | freed at once, whatever holds it - other holders now point at freed memory (question 2) |
| F4 | `deallocate` on something already freed | | `double_free`: ignore (default) or a run-time error |

#### Collections letting go

| # | Case | Example | What happens |
|---|---|---|---|
| C1 | An element removed | `removeAt`, `remove`, `removeLast` / `pop`, `map.remove(k)` | -1 (a removed object that is returned and stored moves) |
| C2 | Cleared | `list.clear()`, `map.clear()` | every element -1 |
| C3 | The collection itself freed | its last holder lets go of it (lists are references now) | every element -1 |
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
| O3 | Two objects holding each other (a cycle) | `a.friend = b; b.friend = a` | the counts never reach 0 - a leak. Needs Weak (Task 38) or a GC |
| O4 | An object holding itself | `node.next = node` | the same - a cycle of one |

#### What never changes the count

- Reading a field, calling a method, comparing (`==`, `===`, `is null`), printing
- A parameter while the call runs (borrowed); a `readonly` parameter never
- `this` inside a method
- The loop variable of `for x in list` / `foreach` - it borrows each element in turn

---

## 9. Leaks, debug messages and threads (user, 2026-10-28)

- **Leak reports:** while developing, the compiler warns where it can see a cycle (a class
  holding its own type), and the leak check reports what was never freed
- **The leak check may be turned off, or built into the app**
- **A published app never shows debug messages to the customer** - it only logs them, as the
  company's policy says, or as the app's own logging does
- **Threads:** counts that change from several threads at once must be atomic; the GC and the
  counting run on a shared thread (default) or a dedicated one (Task 42)

---

## 10. Settings (proposed names)

```toml
[memory]
strategy = "ownership"      # ownership (default) | gc | manual
gc = "multi-core"           # single-core | multi-core | off - the GC implementation
gc_thread = "shared"        # shared (default) | dedicated
double_free = "ignore"      # deallocate on something already freed: ignore | error

[diagnostics]
leak_check = "dev"          # dev (report while developing) | log (log in the app) | off
```

---

## 11. Questions still open

1. **`unsafe` and the existing words:** `unchecked { }` (arithmetic wraps, Task 27.2d) and
   `[safety] mode = "unsafe"` (whole project: arithmetic wraps) already exist. Keep all three
   (`unsafe` for memory / assembly / devices, `unchecked` for arithmetic), or let an `unsafe`
   block also wrap arithmetic?
2. **After a raw `free(x)`, other variables holding the same object** (`Car b = a; free(a);
   b.name`) - the compiler can't always see them. A run-time check in development builds
   (each freed object marked; a use is an error naming the place), and nothing in a release
   build (raw speed)?
3. **A freed variable given a new object** - `deallocate(honda)` then `honda = Car("New")`: is
   that allowed (like after `honda = null`), with only reading it before a new value an
   error?
4. **Lists as references** changes how they work today: `List<int> b = a` then `b.add(1)` -
   `a` changes too (Java, C#, Python). A struct holding a List: when the struct is copied,
   does the copy share the list or get its own (`byVal`)?
5. **`readonly` beyond parameters:** also `readonly` fields and variables (`readonly List<int>
   days = [...]`), or parameters only?

---

## 12. Decisions log

| Date | Decision |
|---|---|
| 2026-10-28 | Three strategies as a setting: OWNERSHIP (default - scope, like Rust, + reference counting), GC (optional; Java; implementations for single-core, multi-core, off for embedded; a shared or dedicated thread), MANUAL (C) |
| 2026-10-28 | All three can be used at once: MANUAL - the program frees; GC strategy - a GC is added automatically; OWNERSHIP - a GC can be made in code (`GC gc = new GC(...)`) as a backup / clean-up |
| 2026-10-28 | `unsafe` functions and `unsafe { }` blocks: where memory is freed by hand, assembly code, device control (HIDL); `free` / `deallocate` elsewhere (not MANUAL) - a warning |
| 2026-10-28 | `free(x)`: unsafe, raw, at once. `deallocate(x)`: safe - checks the count; the default way, used by the compiler and the GC. Using a variable after either: a compile error, always. `x = null` leaves the variable usable |
| 2026-10-28 | Passing: value types (int, decimal, string, structs) by value; class objects, arrays, lists, maps by reference (lists become references, still never null). Modifiers `readonly` (no change - compile error), `byRef`, `byVal` |
| 2026-10-28 | Constructors: `constructor(...)` the default, `Car(...)` quick typing; `new` optional; private constructors, a private static constructor, static const objects made only inside the class (a factory) |
| 2026-10-28 | Copying a collection that holds objects: the copy refers to the same objects |
| 2026-10-28 | Leaks: warned in development; the leak check can be off or built into the app; a published app logs, never shows debug messages to the customer |
| 2026-10-28 | Atomic counts with threads; a shared (default) or dedicated thread |
