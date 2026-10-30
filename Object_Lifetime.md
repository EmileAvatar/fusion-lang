# Object lifetime: when an object is freed

Every case where a class object gains or loses a reference, so that each object is freed
exactly once, at the right time, and never used after it is freed. A design document for
Task 32 (classes) - a mini-task of its own (32.10) - and the base for Task 38 (the memory
model). Status (2026-10-29): the **OWNERSHIP counting is built** for class objects, Lists and
Maps (Task 32.10a-c) - every case in sections 7 and 8 marked below has a test in
tests/test_object_lifetime.py that checks the moment each object is freed
(`-DFUSION_TRACE_OBJECTS` shows `[freed Car]`), with the leak check (exit 5: an object never
freed). Cycles get a warning (32.10d); a returned local is moved without counting (32.10e).
Still designed only: GC and MANUAL, `free` / `deallocate`, statics, copies of objects (clone),
Weak references and more moves (Task 38).

---

## 1. Three memory strategies (a project setting)

**OWNERSHIP is always the first choice (user, 2026-10-29):** memory stability - no crashes
where they can be avoided, and no leaks, which cause instability and security holes. GC and
MANUAL are there for the cases that need them.

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
- `unsafe` is only for memory, assembly and devices - where precise control is absolutely
  needed (raw performance, security)
- **Project-wide** (user, 2026-10-28): `[safety] mode = "safe"` (the default), `"strict"` -
  absolute strictness, for security or where no undetermined behaviour is allowed: what would
  be a warning is an error - or `"unsafe"`, only when the whole project needs it
- **Whole-number overflow is separate:** `OverflowWrap` (default false) - `byte 255 + 1` is an
  OverflowError; with `OverflowWrap = true` it gives 0. This replaces today's `[safety] mode =
  "unsafe"`, which only made arithmetic wrap (Task 27.2b). `unchecked { }` stays: overflow
  wraps inside that one block

#### The two ways to free by hand

| Call | Safe? | What it does | For |
|---|---|---|---|
| `deallocate(x)` | **safe** - the default way | checks the count: frees only when nothing else holds the object; on something already freed it does nothing (or an error, by `double_free`) | normal manual freeing; also what the compiler and the GC use internally |
| `free(x)` | **unsafe** - raw | frees the memory at once, whatever holds it; freeing twice can crash or corrupt memory | hardware, embedded - exact control over when memory goes |

- **After `free(x)` or `deallocate(x)`, using `x` is a compile error - always.** The memory is
  gone and can't be used again. `x` may be given a new object afterwards (as after `x = null`)
- **Other variables holding the same object** (`Car b = a; free(a)`): the object is marked
  freed. The compiler looks for every place `a` was given to, across the project; using `b` in
  the same block after the free is a **compile error**; anywhere else it is a **run-time error**
  when it happens (the mark is checked). `b?.name` is the guard here: a freed object counts as
  null, so it runs on without an error (user, 2026-10-28)
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
- **Rule of thumb (user, 2026-10-29):** in a struct, Arrays / Lists / Maps are `byVal` (copied
  with it) unless the field says `byRef`; everywhere else they are `byRef` (shared) unless
  written `byVal`. The truth table is in Arrays.md section 1

**Modifiers on a parameter:**

| Modifier | Meaning | Default for |
|---|---|---|
| `readonly` | the function may read but never change it - any change is a compile error | - |
| `byRef` | the function may change the caller's variable or object | reference types (classes, arrays, lists, maps) - implicit |
| `byVal` | the function gets a copy; the caller's value never changes | value types (int, string, decimal, structs) - implicit |

- `byVal` and `byRef` also work where a value is assigned: `List<int> b = byVal a` makes a copy;
  `List<int> b = a` shares the list (it is a reference)
- A struct assigned to another is copied (`byVal`, implicitly) - so a List inside it is copied
  too
- `readonly`, `byRef`, `byVal` on parameters only for now (user, 2026-10-28)

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

## 4b. Copying an object that holds objects (`byVal` and `byRef`)

A `Car` holds an `Engine`. What does a copy of the car hold?

```fusion
Car carA = Car("Honda")                  // carA holds Engine "V8"
Car carB = byRef carA                    // the same car (the default for objects)
carB.getEngine().kind = "V6"             // carA's engine is now V6 too - one car, one engine
Car carC = byVal carA                    // a copy: a new car AND a new engine
carC.getEngine().kind = "V12"            // carA's engine stays V6
```

**Decided (user, 2026-10-28):** `byVal` copies **everything** - the car and the engine inside it
(a *deep copy*). `byRef` shares - changing the engine through `carB` changes the one engine.

**How other languages do it** - most copy only the top object by default (a *shallow copy*:
the copy shares the engine) and make a deep copy something you ask for:

| Language | Assigning an object | A copy | The objects inside a copy |
|---|---|---|---|
| Java | shares (a reference) | `clone()` | shared (shallow) unless the class writes its own deep clone |
| C# | shares | `MemberwiseClone()`, a record's `with` | shared (shallow) |
| C++ | copies (value semantics) | the copy constructor | values copied; pointers shared - unless you write the copy constructor |
| Rust | moves (the old name can't be used) | `.clone()` | each field cloned - deep for owned fields, shared for `Rc` |
| Swift | classes share, structs copy | (structs) | a class held by a struct is shared |
| Go | structs copy | assignment | pointers, slices, maps inside are shared |
| Python | shares | `copy.copy` / `copy.deepcopy` | shallow / deep - you choose |
| JavaScript | shares | `{...obj}` / `structuredClone(obj)` | shallow / deep - you choose |

**What a deep copy has to get right** (why most languages don't make it the default):
- **Cycles:** a car whose engine points back to the car - a naive deep copy never ends. Fix: copy
  each object once, and keep the shape (as Python's `deepcopy` does)
- **Shared parts:** two wheels sharing one hub - the copy should share one copied hub too
- **Things that must not be copied:** an open file, a database connection, a lock, a thread -
  copying them is wrong or impossible. Such a class needs a way to say so (an error when copied
  by value, or it is shared instead)
- **Cost:** copying a big object tree takes time and memory - it should be visible in the code
  (`byVal` written out, never by accident)

**The setting** (Fusion's deep default, or the shallow copy other languages use):

```toml
[memory]
copy = "deep"        # byVal on an object: deep (default - everything copied, user 2026-10-28)
                     # | shallow (only the object itself; what it holds is shared - Java, C#)
```

**Decided (user, 2026-10-28):** deep is the default; `[memory] copy = "shallow"` is the option.
Either way the developer can ask for a copy by name:

```fusion
Car car = copyDeep(honda)     // always a deep copy
Car car = copy(honda)         // a deep copy - or shallow when [memory] copy = "shallow"
```

#### `nocopy` and `noshare` - fields that must not be copied, or must not be shared

```fusion
class Car
    // a nocopy field: a Car can't be copied - unless Car implements Cloneable (below)
    private nocopy Database database     // a database can't be copied
    private noshare Logbook log          // when a Car is copied, the log is copied too
    private nocopy noshare Settings set  // a compile error - one field can't be both

    // allowed - a method decides what it hands out:
    public Database function shareDB()
        return database                  // shares the database's reference
    public Logbook function copyLogbook()
        return copy(log)                 // a copy of the logbook
```

| Modifier | Means | When the object holding it is copied (`byVal`, `copy`, `copyDeep`) | An error |
|---|---|---|---|
| `nocopy` | the value can never be copied (a database, a file lock) | **an error** - unless the class implements `Cloneable`: then its `clone()` makes the copy and recreates the field | copying the object without `Cloneable` |
| `noshare` | when the enclosing object is copied, this field is copied too | the copy gets `copy(field)` automatically - even when `[memory] copy = "shallow"` | - (it doesn't stop sharing) |

- A class may have `nocopy` fields and `noshare` fields; **one field can't be both** -
  `private nocopy noshare Database db` is a compile error
- Both are for special cases - to be used sparingly

#### The rules (user, 2026-10-28)

- **`nocopy`** - copying the object that holds it (`copy(x)`, `byVal x`) is a compile error,
  **unless its class implements the `Cloneable` interface**: then the copy calls the class's
  own `clone()`, which recreates the `nocopy` field (e.g. opens a new database connection)
- **`noshare`** - only matters when the enclosing object is copied: the compiler then copies
  that field automatically - `copy(field)` - without the developer doing it by hand. It does
  not stop the enclosing object being shared
- **A class that can't be copied can still be passed to functions** (borrowed, like Rust) - the
  function can call its methods; only `copy(...)` / `byVal` on it is an error
- **Structs are always copied** - a value, never a reference
- **A List or array of a class with a `nocopy` field:** copying the list copies each element, so
  that class must implement `Cloneable` too - its `clone()` recreates the `nocopy` fields
- **Rule of thumb:** `nocopy` -> the class implements `Cloneable`, and `clone()` recreates that
  field; `noshare` -> the field becomes `copy(field)` automatically, and the copy is used
- **`copy(a)` / `byVal a` / `byValue a`** (both spellings work): when `a`'s class implements
  `Cloneable` **and** has a `nocopy` field, its `clone()` is used; otherwise it is a normal copy
  (deep, or shallow by `[memory] copy`)
- **A `nocopy` field gets a new value only in a constructor or in `clone()`** - e.g. a new
  `Database`; `copy(car.database)` anywhere is a compile error
- **A `noshare` field can't be handed out:** `return engine` is a compile error - write
  `return copy(engine)`; handing out a value from it is fine (`return engine.make`)
- **Structs:** copied by default (`byVal`); a function may take one `byRef` and change the
  caller's struct. Assigning by reference (`structB = byRef structA`) is a compile error - a
  struct is only copied - unless a setting allows it (`[structs] allowReference = false` by
  default)
- **Objects inside a struct** (a List / array of a class in a struct): a struct is for values
  you can copy, so `[structs] shareableListBehaviour = "cloneable"` (default) - the class must
  implement `Cloneable`; `"none"` - objects aren't allowed in a struct

```fusion
interface Cloneable
    Cloneable function clone()

class Car implements Cloneable
    private nocopy Database database     // copying a Car calls clone()
    private noshare Logbook log          // a copied Car gets copy(log) automatically
    string name
    public Car function clone()          // the class decides how a copy is made
        Car chevy = new Car(name)        // a new Car
        // ... copy the other values over
        chevy.database = new Database("connection string")   // the nocopy field: a new one -
                                         // only here (or in a constructor)
        return chevy                     // (log is copied by the compiler - noshare)

Car a = Car("Honda")
Car b = a                    // shares - one Car
Car c = copy(a)              // a.clone(): a new Car with its own database, and copy(a.log)
void function drive(Car car) // borrowed - drive can call car's methods
```

#### Truth table 1: copying and sharing a whole value

Columns: a **struct**; a **class** with no special fields; a class with a **`nocopy`** field
that is **not** `Cloneable`; the same class **with** `Cloneable`; a class with a **`noshare`**
field.

| Operation | struct | class | class: `nocopy` | class: `nocopy` + `Cloneable` | class: `noshare` |
|---|---|---|---|---|---|
| `b = a` | a copy | shared - one object | shared | shared | shared |
| pass to a function `f(a)` | a copy | borrowed (shared) - `f` may change it | borrowed | borrowed | borrowed |
| `f(byRef a)` | the caller's struct - `f` may change it | shared (the default) | shared | shared | shared |
| `b = byRef a` | **compile error** (unless `[structs] allowReference = true`) | shared | shared | shared | shared |
| `f(byVal a)` / `b = byVal a` (or `byValue`) | a copy | a copy (deep by default) | **compile error** | `a.clone()` | a copy; the `noshare` field copied |
| `copy(a)` | a copy | a copy (deep, or shallow by `[memory] copy`) | **compile error** | `a.clone()` | a copy; the `noshare` field copied - even when shallow |
| `copyDeep(a)` | a copy | a deep copy | **compile error** | `a.clone()` | a deep copy |
| `f(readonly a)` | a copy, read only | borrowed, read only | borrowed, read only | borrowed, read only | borrowed, read only |
| `return a` | a copy | moves to the caller | moves | moves | moves |
| `list.add(a)` | the list holds a copy | the list shares it | shares | shares | shares |
| copy a list of them (`byVal list`, `copy(list)`) | each element copied | each element copied (deep by default) | **compile error** | each element's `clone()` | each element copied |
| put in a struct's List / array | a copy | only if the class is `Cloneable` (`shareableListBehaviour = "cloneable"`), or never (`"none"`) | the same | allowed (`Cloneable`) | the same as a class |
| `a = null`, scope ends | (a value - freed with its holder) | count -1 | count -1 | count -1 | count -1 |

#### Truth table 2: a field inside an enclosing object `E`

Columns: the kind of field.

| When ... | a struct field | an object field (plain) | a `nocopy` field | a `noshare` field |
|---|---|---|---|---|
| `E` is shared (`b = e`, `f(e)`) | part of `E` - shared with it | shared with `E` | shared with `E` | shared with `E` |
| `E` is copied, `[memory] copy = "deep"` | copied | copied (deep) | **error** - unless `E` is `Cloneable` (then `E.clone()` decides) | copied - `copy(field)` |
| `E` is copied, `[memory] copy = "shallow"` | copied | shared with the original | **error** - unless `E` is `Cloneable` | copied anyway - `copy(field)` |
| A method hands the field out: `return field` | a copy | shared | shared (`shareDB()`) | **compile error** - write `return copy(field)`; `return field.make` (a value from it) is fine |
| `copy(e.field)` | a copy | a copy | **compile error** - a new one only in a constructor or `clone()` | a copy |
| `E` is freed | freed with `E` | count -1 | count -1 | count -1 |


- **Later:** classes that are naturally `nocopy` - a file lock, a database connection, a lock,
  a thread - get it by default (Tasks 42, 43)


## 5. The rule for OWNERSHIP (the counting)

- Every object carries a **count**: how many places hold it
- A place that takes the object adds 1; a place that lets go subtracts 1
- **At 0 the object is freed** - at once (no collector pauses)
- An object only one variable holds is freed exactly when that variable's scope ends
  (Rust's rule); an object several places hold is freed when the last one lets go (Swift's)
- Freeing an object lets go of everything it holds - its fields, in turn (a cascade)
- **No counting where it isn't needed (2026-10-29):** where the compiler can prove an object
  has one owner (made, used and dropped, or handed on once), it skips the count - the cost of
  counting is paid only for objects really shared (as Swift and Lobster do)

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

**Built and tested (32.10c):** U1-U5, U8, U9 - and R1-R5, D1-D9, C1-C4, T1-T3, O1, O2 below.
O3 / O4 (32.10d): a warning on a class that can hold itself, directly or through other
classes, Lists, Maps or arrays (`Class 'Node' can hold itself (Node -> Node)`), and the leak
check stops a program that keeps a circle (exit 5); setting a field to null breaks it.
Not yet: U6 / U7 (need clone() and `[structs] classes`), U10 (statics), F1-F4, T4 (a match
works on enums, numbers and text, not objects), Weak references (Task 38).

| # | Case | Example | Notes |
|---|---|---|---|
| U1 | Created and stored | `Car honda = Car("Honda")` | starts at 1 - the variable holds it |
| U2 | Assigned from another holder | `Car d = honda` | both hold the same object: 2 |
| U3 | Stored in a field | `engine = Engine("V8")`, `this.owner = p` | |
| U4 | Stored in a collection | `cars.add(c)`, `list[0] = c`, `map["k"] = c` | each element is a holder |
| U5 | Returned to a caller who stores it | `Car c = garage.leave(0)` | moves to the caller - no extra count |
| U6 | A collection copied (`byVal`) | each element copied (deep by default) - the copies start at 1 | replaces "the copy refers to the same objects" (user, 2026-10-28) |
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
gcThread = "shared"        # shared (default) | dedicated
doubleFree = "ignore"      # deallocate on something already freed: ignore | error
copy = "deep"               # byVal / copy(): deep (default) | shallow

[safety]
mode = "safe"               # safe (default) | strict (warnings are errors) | unsafe (the whole
                            # project) - today "normal" (= safe) / "strict" / "unsafe" (= wrap)

[numbers]
overflowWrap = false        # false (default): 255 + 1 in a byte is an OverflowError; true: 0

[diagnostics]
leakCheck = "dev"          # dev (report while developing) | log (log in the app) | off
```

---

## 11. Questions still open

None - the truth tables are settled (user, 2026-10-28). Reviewing them once more before Task
32 starts is still welcome.

The settings changes this brought (camelCase names, `overflowWrap`, `[safety] mode`) are task
32.0 - see taskSummary2.md.

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
| 2026-10-28 | Copying a collection that holds objects: the copy refers to the same objects - **replaced** the same day: each element is copied (deep by default) |
| 2026-10-28 | After free / deallocate: the object is marked freed; the compiler finds where it was given to - a use in the same block is a compile error, elsewhere a run-time error; `?.` treats a freed object as null (no error). A freed variable may get a new object |
| 2026-10-28 | Lists, arrays, maps are references: `b = a` shares, `b = byVal a` copies; a struct assigned is copied (byVal), its lists too. `readonly` / `byRef` / `byVal`: parameters only for now |
| 2026-10-28 | `byVal` on an object copies everything (deep - the engine inside the car too); `byRef` shares |
| 2026-10-28 | `unsafe`: only memory, assembly and devices - precise control (raw performance, security) |
| 2026-10-28 | Overflow: `OverflowWrap` (default false - 255 + 1 in a byte is an error; true - 0). `[safety] mode = "safe"` (default) / `"unsafe"` (the whole project) |
| 2026-10-28 | `[memory] copy = "deep"` (default) / `"shallow"`; `copyDeep(x)` always deep, `copy(x)` follows the setting |
| 2026-10-28 | Field modifiers `nocopy` (the value can never be copied - a class with one can't be copied at all, only shared; e.g. a database) and `noshare` (never shared - always copied); not both on one field; used sparingly; file locks, connections, locks, threads `nocopy` by default later |
| 2026-10-28 | `[safety] mode`: safe (default) / strict (warnings become errors - security, no undetermined behaviour) / unsafe; `overflowWrap` in `[numbers]` |
| 2026-10-28 | `byValue` / `byVal` both. Structs: copied; `byRef` as a parameter (the function may change the caller's struct); `structB = byRef structA` an error unless `[structs] allowReference`. Objects in a struct's list: `[structs] shareableListBehaviour` = cloneable (default) / none. A `noshare` field can't be handed out (`return copy(field)`; a value from it is fine). A `nocopy` field is set only in a constructor or `clone()`. `copy(a)` uses `clone()` when the class is `Cloneable` and has a `nocopy` field; otherwise a normal copy |
| 2026-10-28 | A class with a `nocopy` field can't be copied - unless it implements `Cloneable`: then `copy(x)` / `byVal x` call its `clone()`, which recreates the field. A `noshare` field is copied automatically when the enclosing object is copied (it doesn't stop sharing). A class that can't be copied can still be passed to functions (borrowed). Structs are always copied. A list of a `nocopy` class needs that class to be `Cloneable` to be copied. A method may hand out a `nocopy` field's reference (`return database`) or a copy of a `noshare` field (`return copy(log)`) |
| 2026-10-28 | Leaks: warned in development; the leak check can be off or built into the app; a published app logs, never shows debug messages to the customer |
| 2026-10-28 | Atomic counts with threads; a shared (default) or dedicated thread |
| 2026-10-29 | Lists and Maps become references with a count (shared in normal code, copied in a struct, `byVal` copies) - the same counting the class objects use. A class with no constructor: `Car()` - value fields at their defaults, objects null; its methods set them. 32.10 builds a minimal class together with the counting |
| 2026-10-29 | OWNERSHIP is always the first choice - no crashes, no leaks (they cause instability and security holes). Counting is skipped where the compiler proves a single owner |
