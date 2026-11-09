# Fusion Programming Language Specification v2

Description: A modern programming language combining the performance of C, structure of Java, simplicity of Python, readability of VB.NET, and concurrency of Go. Designed for game development, automation, and systems programming.

**Fusion is a combination of various programming languages unified into one cohesive language.**

---

**Status lines (Task 22.7b):** each major section below starts with a `**Status:**` line matching `files/FEATURES.md` - `[DONE n]` built (task n), `[PARTLY]` some of it built, `[PLANNED n]` scheduled as task n, `[DESIGN]` the intended design with no task yet. What works today, with examples: `files/SYNTAX_REFERENCE.md`.

---

## Language Philosophy, Syntax Overview

Moved to `files/spec/010-Philosophy.md` (Task 51.5 - the spec is split one file at a time;
the list: `files/spec/index.md`).

---

## The Semantic Contract

Moved to `files/spec/020-SemanticContract.md` (Task 51.5).

---

## Data Types and Variables

Moved to `files/spec/` (Task 51.5): `030-Types.md` (type categories, type specifications,
nullability, variables, constants), `031-Arrays.md`, `032-Strings.md`, `033-TypeCasting.md`.

---

## Functions and Methods

Moved to `files/spec/` (Task 51.5): `040-Functions.md` (declaring, main, block syntax,
calling), `041-Lambdas.md`, `042-MultipleReturns.md`.

---

## Classes and Objects, Interfaces and Contracts

Moved to `files/spec/` (Task 51.5): `050-Classes.md` (class definition, static vs instance,
properties), `051-Inheritance.md`, `052-Interfaces.md`.

---

## Structures and Value Types, Enumerations, Control Flow

Moved to `files/spec/` (Task 51.5): `060-Structs.md`, `061-Enums.md`, `070-ControlFlow.md`.

---

## Null Handling

**Status:** [PLANNED 30] - designed 2026-10-27 (user decisions). Full write-up with truth
tables and when (not) to use `?.`: `files/Nullable_Values.md`.

Description: No value is null unless it can be, and a missing object never crashes the
program by surprise. The problem it solves: in Java, C#, C, JavaScript and Python any
object may be null and using it crashes - far from where it was left unset. It matters most
for data from outside: a JSON object whose field is `null`, a database row, user input, a
class object that was never created.

---

### Core Principles

* **Only class objects and enums can be null** (class objects: Task 32; enums: built, Task
  30.11 - `Status s` with no value is null, not the first value). Numbers, bools, chars and structs are
  values; strings, arrays, `List` and `Map` are values too - never null, empty when not
  set (`""`, `[]`), length 0 when empty
* **A project may allow null** for strings, arrays, lists or maps when "not set yet" must
  differ from "empty": `[strings]` / `[arrays]` / `[lists]` / `[maps]` `nullable = true`
  (default false)
* **`?` is never part of a type** (no `int?`, `string?`): it is used on a variable, as a
  guard - `x?.method()`
* **Nothing changes silently**: a default is always one written in the code (`??`)

---

### Null Checking Methods

Description: Three ways to handle a value that might be null - check first, guard, or let it
fail.

* **Check if null** - `==`, `===`, `is null`, and `x?.null` as quick typing; `!x?.null`
  means "not null"

```
Spaceship ship = getShip()

if ship?.null                    // the same as: if ship == null / if ship is null
    print("No ship")
    return

ship.start()                     // safe: checked above
```

* **Guard with `?.`** - on a null object the method is not run and nothing errors. The
  result is null; inside an `if` the condition is false, so the else block runs - also
  for a comparison

```
Person pep                       // never set: null

if pep?.getAge() >= 18           // no error: false, the else block runs
    print("old enough")
else
    print("not old enough, or unknown")

if !(pep?.getAge() >= 18)        // true: runs
    print("ask for ID")

string captainName = ship?.getCaptain()?.getName() ?? "Unknown"   // a chain
```

* **Default with `??`** - only where a value is expected and none may come:
  `someObject?.someMethod() ?? value`
* **Plain `.`** - `pep.getAge()` on null is a **NullError** (an Error subtype, Task 26):
  only a `catch` handles it. Use it where missing would be a bug
* **Length through `?.`** - `string?.length()` and `array?.length` give -1 on a null string
  or array (only with the `nullable` settings on); an empty one gives 0. Every other member
  or method gives null
* **No `x!`** ("I know it isn't null") - write `if !x?.null` instead
* **Warnings**: a guarded value in a comparison (with null, `>= 18` and `< 18` are both
  false, so `!(x >= 18)` is not `x < 18`); `??` after `?.length()` (-1 is not null, so the
  default is never used)

---

### Numbers as conditions

`if count` with a number: a `fusion.toml` setting (Task 30.9, user 2026-10-27):

```toml
[conditions]
numbers = "positive"   # default: positive is true; zero and negatives are false
                       # "nonzero": 0 false, other numbers true (C, Python, JavaScript)
                       # "off": a condition must be a bool (Java, C#, Go, Rust, Swift)
```

With `"positive"`, -1 ("not found", "not set") and 0 ("empty") are both false. The editor
shows the project's choice as a hint (Task 36.7). **Built (Task 30.9)**: a number in a
condition becomes `n > 0` ("positive") or `n != 0` ("nonzero") while compiling.

Where numbers count as true / false (user, 2026-10-27) - only when the setting is not "off":
- in an `if` or `while` condition, including `and` / `or` / `not` inside it:
  `if count and ready`, `if not errors`
- `count == true` / `count == false` compares by the same rule (0 false; 1, 2, 1000 true)
- `count === true` is always false - a number is not a bool (the compiler already warns that
  `===` on two different types is always false)
- `bool b = count` is always an error, whatever the setting - write `bool b = count > 0`
- `and` / `or` always give a bool

---

### Strict Mode (replaced)

The earlier "strict mode" (the compiler adding null checks to every parameter) is replaced
by the rules above: only class objects and enums can be null, a plain `.` on null is a NullError with
file and line, and `?.` is the guard where missing is normal.

---

## Autoboxing

**Status:** [PARTLY] the built-in type classes (String, Int, ...) and method syntax on built-in values are built (18.3.7); autoboxing itself: no task yet

**Any function as a method** (Task 44.2, user decision 2026-10-26, implemented): `x.f(a)` is
`f(x, a)` when the program has a function `f` whose first parameter takes `x` - a struct, a
built-in value, a list, an enum. List / Map methods and an enum's `toString` / `toInt` come
first; the program's own function replaces a library one of the same name, as a plain call
does. The function gets a copy (structs are values): `p = p.moved(1, 2)`. Passing will follow
VB.NET once classes exist: value types by value, objects by reference. Functions inside a
struct are a later `fusion.toml` option, off by default (32.1).

Description: Automatic primitive-to-object conversion for method calls.

---

### How It Works

* Primitives automatically become objects when calling methods
* Compiler handles conversion transparently
* No manual boxing required
* Performance optimized

---

### Using Autoboxing

Description: Call methods on primitives seamlessly.

* **Number Methods**

```
int num = 42
string str = num.toString()           // "42"
string hex = num.toHexString()        // "2A"
string binary = num.toBinaryString()  // "101010"

float pi = 3.14159
float rounded = pi.round(2)           // 3.14
int truncated = pi.floor()            // 3
```

* **String Methods**

```
string text = "hello world"
string upper = text.toUpper()         // "HELLO WORLD"
string sub = text.substring(0, 5)     // "hello"
int length = text.length              // 11
bool contains = text.contains("world") // true
```

* **Array Methods**

```
int[] numbers = [1, 2, 3, 4, 5]
int len = numbers.length              // 5
int sum = numbers.sum()               // 15
int max = numbers.max()               // 5
int[] doubled = numbers.map(lambda x: x * 2)
```

* **Arrays and null:** arrays are never null by default (`[arrays] nullable = false`), so
  `numbers.length` is always safe - 0 for an empty array. With `nullable = true`,
  `numbers?.length` is -1 on a null array and `numbers?[0]` is null; see "Null Handling"
  and `files/Nullable_Values.md` (Task 30, planned)

---

### Autobox Classes

Description: Each primitive type has corresponding object class.

Primitive | Autobox Class | Example Methods
---|---|---
int | Int | toString(), toHexString(), abs()
uint | UInt | toString(), toHexString()
long | Long | toString(), abs()
float | Float | toString(), round(), floor(), ceil()
double | Double | toString(), round(), floor(), ceil()
bool | Boolean | toString(), not()
char | Char | toString(), toUpper(), toLower(), isDigit()
byte | Byte | toString(), toHexString()

---

## Memory Management

**Status:** [PARTLY] strings, bytes, lists, maps and structs holding them are values, copied deeply and freed automatically (18.3, 18.5) with a leak check; Unique / Shared / Weak and GC are decided (12.7) and [PLANNED 38]

Description: Three-tier memory management strategy for different use cases.

**Design status (Task 12.7, decided 2026-09-13):** the `Unique<T>`/`Shared<T>`/`Weak<T>`
semantics below are the authoritative, decided design - this section is the memory-model
ADR that Task 12.7 exists to produce. **Not yet implemented in the compiler**: `Unique`,
`Shared`, and `Weak` are currently reserved keywords only (tokenized, nothing else) - there
is no parser, semantic-analysis, or codegen support yet. Building that is separate future
work, unblocked by this decision but not scoped or scheduled here (see files/taskSummary2.md
Task 30, which depends on this section's Weak/nullability decisions).

---

### Tier 1: Automatic Garbage Collection (optional - never the default: OWNERSHIP first, Decisions.md D.027)

Description: Automatic memory management for most use cases.

* No manual memory management needed
* Like Java, Python, C#
* Suitable for 95% of applications
* Simplest for developers

```
// Automatic cleanup
Spaceship ship = Spaceship("Enterprise", 100.0)
// Automatically garbage collected when no longer referenced
```

---

### Tier 2: Smart Pointers (Performance Mode)

Description: Explicit lifetime control without garbage collection pauses.

* **Unique Pointer**: Single ownership
     * Only one owner at a time
     * Automatically deleted when owner goes out of scope
     * Cannot be copied, only moved
     * **Moving is automatic (decided 2026-10-31, Decisions.md D.080 - replaces the written
       `.move()` of 2026-09-13):** under OWNERSHIP every object has one owner, and
       assigning it moves it (`Car b = a`); `byVal` copies, `byRef` borrows. So no
       `Unique<T>` wrapper is needed - single ownership is what every object already has
       (files/Ownership.md)
     * **Use-after-move is a compile-time error where provable, a runtime crash with a
       clear message otherwise** - structurally the same hybrid analysis already decided
       for Task 30's nullable arrays (definite/maybe/unknown state tracked through
       straight-line code), so moved-from tracking and null-flow tracking should share one
       analysis pass when both are eventually implemented, not two parallel ones.
     * Zero overhead
     * Use for: temporary objects, factory returns, single-owner scenarios

```
// Creating unique pointer
Unique<Spaceship> ship = Unique.create<Spaceship>("Enterprise", 100.0)

// Use like normal object
ship.start()
ship.move(direction, speed)

// Transfer ownership (move) - by assigning (D.080)
Spaceship newOwner = ship               // moved: using ship again is a compile error
Spaceship copy = byVal newOwner         // a copy - both usable

// Automatic cleanup when newOwner goes out of scope
```

* **Shared Pointer**: Reference counting
     * Multiple owners allowed
     * Keeps count of references
     * Deleted when count reaches zero
     * Can be copied
     * **Refcounting is always atomic (decided 2026-09-13):** increment/decrement of the
       reference count is thread-safe unconditionally, regardless of any project-level
       threading configuration (see Task 12.12). Chosen over a configurable
       atomic-vs-non-atomic mode to keep one correct behavior rather than two runtime
       code paths to implement, test, and document - the small overhead of an atomic op
       even in single-threaded code was judged worth that simplicity.
     * **Cycles are not detected automatically (decided 2026-09-13):** there is no cycle
       detector or tracing collector. A cycle of `Shared<T>` references leaks memory -
       matches Swift ARC / Rust `Rc` / Objective-C ARC, not a garbage-collected language's
       behavior. `Weak<T>` (below) is the documented, required way to break a cycle; this
       is an accepted, permanent limitation of the design, not a gap awaiting a future fix.
     * Small overhead (reference count storage + atomic refcount ops)
     * Use for: shared resources (textures, sounds, configs)

```
// Creating shared pointer
Shared<Texture> texture = Shared.create<Texture>("ship.png")
print("Ref count: {texture.refCount()}")  // 1

// Make copies (reference count increases)
Shared<Texture> copy1 = texture  // Ref count: 2
Shared<Texture> copy2 = texture  // Ref count: 3

// All copies deleted when ref count reaches 0
```

* **Weak Pointer**: Non-owning reference
     * Doesn't increase reference count
     * **Upgrade is nullable, never a silent crash (decided 2026-09-13):** `.lock()`
       (shown below) always returns a `Shared<T>` that is `null` if the owner was
       already destroyed. The caller must null-check before use; there is no "just crash
       if the owner is gone" mode. Chosen for consistency with the same nullable-safe-
       navigation direction Task 30 defines for arrays, so Fusion has one null-handling
       story across features rather than a different rule per type. Once Task 30's
       `?.`/`?[` syntax exists, this should read as `child.parent.lock()?.doSomething()`
       instead of the explicit if/else shown below.
     * Breaks circular references
     * Use for: observer pattern, parent-child relationships
     * **WARNING**: Discouraged in most code
     * **STRICT MODE**: Causes compilation error
     * Only use when absolutely necessary to break circular references

```
// Breaking circular reference
class Parent
    Shared<Child> child

class Child
    Weak<Parent> parent  // Weak reference prevents memory leak

// Using weak pointer
Shared<Parent> parentRef = child.parent.lock()     // null when the parent is gone (no T? types - D.063)
if parentRef?.null
    print("Parent no longer exists")
else
    parentRef.doSomething()

// In strict mode, this would cause a compile error
// Prefer redesigning to avoid circular references
```

---

### Tier 3: Raw Pointers (Unsafe Mode)

Description: Manual memory management for embedded systems.

* Only for embedded systems or FFI (Foreign Function Interface)
* Requires `unsafe` blocks
* Manual allocation and deallocation
* Compiler warnings and restrictions

```
unsafe
    Spaceship* rawPtr = allocate<Spaceship>(1)
    rawPtr.initialize("Manual", 200.0)
    // ... use pointer
    deallocate(rawPtr)
```

---

### Memory Strategy Summary

Mode | Use Case | Complexity | Performance
---|---|---|---
Automatic GC | General applications | Low | Good
Smart Pointers | Performance-critical | Medium | Excellent
Raw Pointers | Embedded/FFI only | High | Maximum

**Decided (user, 2026-10-31 - Decisions.md D.027):** no GC by default - OWNERSHIP first (one owner, moves, borrows - Task 48). A GC exists only when made in code or when a project's `fusion.toml` chooses it

---

### Ownership: move, borrow, share

**Status:** [PLANNED 48] designed 2026-10-31 (user). The rules and truth tables:
`files/Ownership.md`; the decisions: `Notes/Ownership_Decisions_2026-10-31.md`.

* **Assigning moves:** `Car b = a` hands the object over - using `a` afterwards is a compile
  error until it gets a new value. Lists and Maps move too; strings and plain structs copy
* **`byVal` copies** (`clone()` for objects); **passing borrows** for the call; reading an
  element or field is a local borrow; a struct's collection only lends itself
* **At the call:** `show(readonly acc)` - the call must not change acc; `f(byRef x)`; `f(byVal x)`
* **The contract is the signature:** `readonly Account a` only reads; `Account a` may change
  it. Inside a project it is worked out from the body; a library counts by its signature
  only; a library not written in Fusion gets a warning when a borrowed value is passed
* **`shared Car c = a`:** counted, read only except to the holder that made it shared
* **`fixed(n)`** (Task 47.5, D.064): `fixed(10) string name`, `fixed(14) List<Person> people`,
  `fixed int numbers[10]` - only the size is limited (the values may change; `const`: nothing changes),
  lower fine, never higher; memory reserved once
* Setting:
  ```toml
  [memory]
  assignment = "move"            # "move" (default) | "share" - b = a: two names, one object
  ```

---

## Threading and Concurrency Model

**Status:** [DESIGN] files/FEATURES.md Task 42. The current design, newer than this section:
`files/Concurrency.md` (terms, traps, the model, other languages), `files/Concurrency_Traps.md` (overview
tables) and `files/Service.md` (the `service` keyword: a shared resource becomes a service
instead of every caller locking it). Where they differ from this section, they win

Description: Hybrid concurrency model supporting both message passing and shared memory.

Note: This is a high-level overview. Full threading specification will be in a separate detailed document.

---

### Threading Hierarchy

Description: Layers of concurrent execution units.

* **System**: Operating system managing all processes
* **Process**: Isolated execution with own memory space
* **Thread**: Lightweight unit within process, shares memory
* **Task/Goroutine**: User-space thread, very lightweight
* **Channel**: Communication queue between threads

Extended Hierarchy: System → Process → Thread Pool → Thread → Task/Job → Channel/Queue

---

### Two Concurrency Approaches

Description: Fusion supports both paradigms for maximum flexibility.

---

#### Approach 1: Message Passing (Recommended)

Description: Share memory by communicating (Go-style).

* **Philosophy**: Don't share memory, send messages instead
* **Benefits**: No locks needed, no race conditions, clearer ownership
* **Use**: Default approach for most concurrent code

**How It Works**

* Threads don't share variables directly
* Data sent through channels
* Only one thread owns data at a time
* Ownership transfers through channel

**Analogy**: Sending emails vs writing on shared whiteboard

```
// Create channel
Channel<Task> taskQueue = Channel.create<Task>()

// Producer thread
void function producer()
    for i in range(100)
        Task task = createTask(i)
        taskQueue.send(task)  // Send to channel
    end loop

// Consumer thread
void function consumer()
    while true
        Task task = taskQueue.receive()  // Receive from channel
        processTask(task)
    end loop
```

---

#### Approach 2: Shared Memory (Traditional)

Description: Communicate by sharing memory (requires locks).

* **Philosophy**: Multiple threads access same variables
* **Requirement**: Must use locks/mutexes for synchronization
* **Benefits**: Sometimes more natural for certain problems
* **Use**: When message passing doesn't fit

**How It Works**

* Threads access shared variables
* Mutex locks prevent race conditions
* Must remember to lock/unlock

```
// Shared counter with mutex
class Counter
    private int count
    private Mutex mutex
    
    void function increment()
        mutex.lock()
        count += 1
        mutex.unlock()
    
    int function getCount()
        mutex.lock()
        int value = count
        mutex.unlock()
        return value
```

---

### "Share Memory by Communicating" Explained

Description: Understanding Go's concurrency philosophy.

**Traditional Approach** (Shared Memory)

* Multiple threads write to same variable
* Use mutex to prevent conflicts
* Easy to forget locks → bugs
* Easy to deadlock

```
// Shared variable approach
int sharedCounter = 0
Mutex lock

// Thread 1
lock.acquire()
sharedCounter += 1
lock.release()

// Thread 2
lock.acquire()
sharedCounter += 1
lock.release()
```

**Go's Approach** (Message Passing)

* Don't share variables
* Send data through channels
* Only one thread "owns" data
* No locks needed

```
// Channel approach
Channel<int> updates = Channel.create<int>()

// Thread 1 sends update
updates.send(1)

// Thread 2 sends update
updates.send(1)

// Counter thread receives all updates
int counter = 0
while true
    int update = updates.receive()
    counter += update
end loop
```

---

### Try-With-Resources Pattern

Description: Automatic resource locking to prevent race conditions and deadlocks.

* **Automatic Locking**: Compiler adds locks automatically
* **No Manual Lock/Unlock**: User doesn't need to manage locks
* **Race Condition Prevention**: Automatic synchronization
* **Deadlock Prevention**: Smart lock ordering by compiler

**How It Works**

* When thread/channel tries to access resource, it's locked automatically
* Resource unlocked when done (scope ends or exception thrown)
* Compiler analyzes code to prevent deadlocks
* User can add custom locks if needed

**File Handling Example**

```
// Automatic locking for file access
using file = openFile("data.txt")
    file.write("Some data")
    file.flush()
// File automatically closed and unlocked

// Multiple threads accessing same file
// Thread 1
using file = openFile("shared.txt")
    file.write("Thread 1 data")
// Unlocked

// Thread 2 (waits for Thread 1 to finish)
using file = openFile("shared.txt")
    file.write("Thread 2 data")
// Unlocked
```

**Object/Variable Locking Example**

```
class Counter
    private int count
    
    // Compiler automatically adds locking
    void function increment()
        using this  // Lock entire object
            count += 1
        // Unlocked
    
    int function getCount()
        using this
            return count

// Multiple threads calling increment() - automatically synchronized
Counter counter = Counter()

// Thread 1
counter.increment()  // Locked during execution

// Thread 2
counter.increment()  // Waits for Thread 1, then executes
```

**Manual Locking (When Needed)**

```
// User can specify custom locking
Mutex customLock = Mutex()

void function criticalSection()
    using customLock
        // Protected code
        sharedVariable += 1
    // Unlocked
```

**Compiler Optimizations**

* Analyzes resource access patterns
* Determines minimal locking needed
* Orders locks to prevent deadlocks
* Adds locks only where necessary for performance

---

### Thread Interrupt Handling

Description: Cooperative multitasking via loop checks.

* Threads can signal other threads to stop/pause
* Checked at `end loop` automatically
* Graceful shutdown possible

```
for item in largeDataset
    processItem(item)
    
end loop with
    check interrupt(signal, data)
        if signal == InterruptSignal.Shutdown
            saveProgress()
            cleanup()
            exit loop
        
        if signal == InterruptSignal.Pause
            waitForResume()
            continue loop
```

---

### Async/Await Pattern

Description: Modern asynchronous programming for I/O operations.

```
// Async function
async Spaceship, Error function downloadShipData(string url)
    Response response = await http.get(url)
    
    if response.statusCode != 200
        return null, Error("HTTP error: {response.statusCode}")
    
    string data = await response.readBody()
    Spaceship ship = parseShipData(data)
    return ship, null

// Calling async function
Spaceship ship, Error err = await downloadShipData("https://api.ships.com/ship/1")
if err
    print("Error: {err.message}")
else
    print("Loaded ship: {ship.Name}")
```

---

### One writer, temporary services, hot paths

**Status:** [PLANNED 42.18-42.25] designed 2026-10-31 (user) - `files/Service.md`,
`files/Concurrency.md` 3.13, `files/Ownership.md` sections 5-7.

* **One writer:** a service's worker thread is the only writer of what it holds
* **Temporary services:** two or more threads using one variable - the compiler makes
  `service(acc)`; it owns the value, the threads borrow it, one call at a time; ownership
  comes back when the last thread ends. `[concurrency] autoService = "on"` (a note) | "warn" | "off"
* **Readers in parallel:** a readonly signature or call makes a request a read
* **send / sync:** send - a value goes to another thread and the sender no longer has it;
  sync - many threads use it through a service. Worked out by the compiler
* **The `Service` interface:** `send`, `T fetch()`, ...; BasicService, SharedService,
  FileService, DatabaseService, HotPathService implement it
* **`hotpath service T x = ... { }`:** a dedicated thread that never sleeps - no allocating,
  blocking or counting (checked), an input ring, pinned to a core. `hotpath void function f()`:
  the checks without the thread. Defaults in `[hotpath]`

---

### Thread Safety Summary

Strategy | Pros | Cons | Use When
---|---|---|---
Message Passing | Safe, no locks, clear ownership | Learning curve | Default choice
Shared Memory | Familiar, sometimes natural | Needs locks, error-prone | Specific performance needs
Async/Await | Clean syntax, efficient I/O | Not for CPU-bound | I/O operations

**Note**: Full threading specification with thread pools, synchronization primitives, and detailed examples will be in separate document.

---

## Generics and Templates

**Status:** [PARTLY] the built-in `List<T>` and `Map<K, V>` (18.5); generic functions and types of your own [PLANNED 33]

Description: Type-safe generic programming.

---

### Generic Classes

Description: Parameterized types for reusable code.

```
class Container<T>
    private List<T> items
    
    constructor()
        items = List<T>()
    
    void function add(T item)
        items.append(item)
    
    T function get(int index)
        return items[index]
    
    property Count: int
        get
            return items.length

// Usage
Container<int> intContainer = Container<int>()
intContainer.add(42)

Container<Spaceship> shipContainer = Container<Spaceship>()
shipContainer.add(Spaceship("Alpha", 100.0))
```

---

### Generic Functions

Description: Type-parameterized functions with constraints.

```
// Generic function with constraints
T function findMax<T>(List<T> items) where T implements Comparable<T>
    if items.isEmpty()
        throw Exception("Cannot find max of empty list")
    
    T max = items[0]
    for item in items
        if item.compareTo(max) > 0
            max = item
    end loop
    
    return max

// Usage
List<int> numbers = [1, 5, 3, 9, 2]
int maxNum = findMax<int>(numbers)  // 9
```

---

### Multiple Type Parameters

Description: Functions and classes with multiple generic types.

```
class Dictionary<K, V>
    void function put(K key, V value)
        // Implementation
    
    V function get(K key)
        // Implementation

// Usage
Dictionary<string, int> ages = Dictionary<string, int>()
ages.put("Alice", 30)
int age = ages.get("Alice")
```

---

## Error Handling

**Status:** [PARTLY] error returns, capturing (26.2), try / catch / finally / throw (26.3)
catchable built-in failures (26.4) and the `[errors] returns / exceptions` switches (26.5)
are built (Task 26 complete). Example program: `examples/errors_demo.fusion`

**Custom error types (Task 26.9, user decisions 2026-10-16):** `error FileError` with fields
like a struct's; `error FileNotFound : FileError` extends one. Every error type is an Error:
message, code, where - plus its parents' fields and its own. A body line `message = "File
not found"` (or `code = 404`) gives that type a default. Made like a struct: message, code,
then the fields (the parent's first), by position or by name; a field without a default must
be given. An error type is accepted where its parent (or Error) is expected. Its fields are
read only. Thrown or returned like any error, copied and freed automatically, across modules
with `public error`.

**Typed capture, `err.kind`, match on error types (Task 26.10):** `Ship s, FileError err =
f()` captures **any** error (user decision): err's own fields are their defaults unless it
really is a FileError. `err.kind` is the type's name ("FileError", "Error"). `match err`
takes error type names as cases: `case FileError` also matches its subtypes, `case Error`
any error, and inside a case with one type err *is* that type, so its own fields can be
read. A name that isn't an error type is a compile error (string compares would let a typo
through); an else (or `case Error`) is required; a case already covered by an earlier one
is a warning.

**Fusion's own error types (Task 26.12):** every run-time failure raises one of these -
all Errors, a parent catches its children (`catch LookupError e` takes IndexError and
KeyError). A program can extend them (`error ConfigError : FileError`), not reuse their names.

```text
ArithmeticError: DivideByZeroError (7 / 0, 7 % 0 on whole numbers - a crash before 26.12)
FormatError: NumberFormatError (toInt("12x")), PatternError (formatNumber), HexFormatError,
             TextEncodingError (bytes that aren't text)
ValueError: RangeError (toByte(300), negative counts, base), UnknownValueError (fromString)
LookupError: IndexError (s[9], xs[9], b[9], slice ...), KeyError (m["missing"])
FileError (path): FileNotFoundError, PermissionError, FileReadError, FileWriteError,
                  FileTooLargeError, DeleteError - chosen by why the system said no
LimitError: StringTooLongError ([strings] maxLength), ResultTooLargeError (over 2 GB)
```
Added by Task 27: OverflowError and PrecisionError (ArithmeticError), StackOverflowError
(LimitError), ModifiedWhileLoopingError (ValueError). Added by Task 30.11: NullError (Error) -
using a null value: `toInt()` on a null enum, a match on a null enum with no case for it.
Not catchable: out of memory, a List past 536,870,911 elements.

**Endless recursion (Task 27.2c, user decisions 2026-10-17):** a function that can call
itself (directly, through others, or through a function value) checks the stack on entry:
when it is nearly full - the limit comes from the real stack size - it raises a
**StackOverflowError** (a LimitError) instead of crashing; every frame then unwinds and frees
what it holds, so it can be caught or captured like any error. Functions that can't recurse
get no check. For memory-constrained devices `[safety] maxCallDepth = 10000` also counts
calls (tune the number by profiling); the default "max" uses stack use alone.

**Whole-number overflow (Tasks 27.2b, 27.2d, user decisions 2026-10-17):** int `+ - *`,
unary `-` and `-2147483648 / -1` that don't fit raise an **OverflowError** (an
ArithmeticError) - never a silently changed value (C, Go and Java wrap; Fusion checks, like
Swift). In C each is GCC's overflow builtin: the operation and one jump; arithmetic made only
of written numbers (`60 * 60 * 24`) isn't checked. Wrapping on purpose (hashes, checksums):
`wrapAdd(a, b)`, `wrapSub`, `wrapMul` (methods too: `a.wrapMul(b)`), or an `unchecked` block
whose `+ - *` wrap. `[numbers] overflowWrap = true` makes every `+ - *` wrap (Task 32.0 - it was
`[safety] mode = "unsafe"`). Wrapping is always
defined (unsigned arithmetic) - never C's undefined behaviour. Array bounds checks are never
turned off.

**Typed catch (Task 26.11, user: now, for a working sample):** `catch FileNotFound e`,
`catch FileError e`, ... `catch e` - the first catch whose type matches takes the error (a
parent type catches its subtypes); an untyped catch takes any error and must be last; an
error no catch takes goes on, through the finally. A catch an earlier one already covers is
a warning. No central ERROR enum: each error type is its own kind, so a module
can add its own

**Every run-time error is an Error (Task 26.4, user decision 2026-10-16: all of them):** an
index out of range (strings, lists, bytes), a missing Map key, text that isn't a number,
a file that won't open, an invalid pattern, `Enum.fromString` with an unknown name, a
string over `[strings] maxLength`, ... can be captured or caught like any other error;
`err.where` says where it happened. One nobody handles stops the program at the end of main
with `Runtime error at main.fusion:12: ...`, as before. Only running out of memory (and a
List past 536,870,911 elements) still stops at once. In C, a runtime function reports with
its `where` argument and returns a safe value; the call is checked right after it runs

**try / catch / finally / throw as built (Task 26.3):** `try` then `catch err` (or a bare
`catch`) and/or `finally`, indented, in braces, or closed by `End try`. One catch catches
any error - tell them apart with `err.code` (typed catches come later). An error in the try
block goes to the catch; one in the catch goes on (through the finally). `finally` always
runs: after the try block, after the catch, when an error passes through, and before a
`return`, `break` or `continue` leaves the try. `throw Error(...)` / `throw err` work in any
function - a function that throws can fail, so its callers check it. A capture
(`int n, Error err = f()`) also catches what `f` throws

**As built (Task 26.2, user decisions 2026-10-09 and 2026-10-16):**
* `Error` is a built-in value: `message` (string), `code` (int, 0 unless given), `where`
  ("main.fusion:12", where it was made). Made with `Error("msg")` or `Error("msg", 404)`;
  printing it prints the message. There is no `null`: a captured Error with no error has an
  empty message, and `if err` / `not err` test whether there is one - the one non-bool
  allowed as a condition
* Any function can fail: `return Error(...)` fails (the value part is its default),
  `return ship` succeeds. Writing `Ship, Error function loadShip(...)` only marks it as able
  to fail (Task 26.7, user decision 2026-10-16) - `--interface` shows the marker, and a
  marked function with nothing in it that could fail gets a warning. `Error function save(...)` is a function with no
  value that can fail. `return err` passes a captured error on
* `Ship s, err = loadShip(f)` (or `Ship s, Error err = ...` - the type is optional, Task
  26.8) captures the error of any call - including any error
  raised while evaluating the right side; `Error e = save(s)` when there's no value to keep
* An error nobody captures **bubbles up**: out of the function to its caller, until
  something captures (or, with 26.3, catches) it. At the end of `main` the program stops
  with `Error at main.fusion:12: message` and exit code 1
* In C: no setjmp / longjmp. A failing function sets the current error and returns a
  default; the call is checked right after it runs (a GCC statement expression), and the
  statement's failure block frees what is held before passing the error on - so every
  error path is leak-free. Only calls that can fail are checked

Description: Explicit error handling with multiple return values.

---

### Multiple Return Values

Description: Go-style error handling with type safety.

* Functions return both result and error
* Error is null if operation succeeded
* Must check error before using result
* Explicit and visible in function signature

---

### Function with Error Return

```
Spaceship, Error function loadShip(string filename)
    if not fileExists(filename)
        return null, Error("File not found: {filename}")
    
    string data = readFile(filename)
    if data.isEmpty()
        return null, Error("Empty file")
    
    Spaceship ship = parseShipData(data)
    if ship is null
        return null, Error("Invalid ship data")
    
    return ship  // Success - error is implicitly null
```

---

### Calling with Error Capture

```
Spaceship ship, Error err = loadShip("ship.dat")

// Check error first
if err
    print("Error loading ship: {err.message}")
    return

// Safe to use ship here (no error occurred)
ship.start()
ship.move(forward, speed)
```

---

### Calling Without Error Capture

Description: Error bubbles up to caller if it occurs.

```
// Don't capture error - will propagate to caller
Spaceship ship = loadShip("ship.dat")
ship.start()

// If loadShip returns error, it bubbles up
```

---

### Error Chaining

```
Spaceship, Error function loadAndValidateShip(string filename)
    // Load ship
    Spaceship ship, Error err = loadShip(filename)
    if err
        return null, err  // Propagate error
    
    // Validate ship
    bool valid, Error err2 = validateShip(ship)
    if err2
        return null, err2  // Propagate error
    
    // Success
    return ship
```

---

### Error Object

```
class Error
    string message
    int code
    string stackTrace
    
    constructor(string msg)
        this.message = msg
        this.code = 0
        this.stackTrace = captureStackTrace()
    
    constructor(string msg, int code)
        this.message = msg
        this.code = code
        this.stackTrace = captureStackTrace()
```

---

### Traditional Exceptions

Description: Available for unexpected errors when needed.

```
void function riskyOperation()
    try
        Data data = readNetworkData()
        processData(data)
    catch NetworkException as e
        print("Network error: {e.message}")
    catch ParseException as e
        print("Parse error: {e.message}")
    finally
        cleanup()
```

---

### When to Use Each

* **Multiple Returns**: Expected errors (file not found, invalid input, network timeout)
* **Exceptions**: Unexpected errors (out of memory, assertion failures, system errors)

---

## Comments and Code Organization

**Status:** [PARTLY] `//` and `/* */` comments are built (01-04); region blocks and documentation comments: no task yet

Description: Code documentation and organizational features.

---

### Single-Line Comments

Description: Two comment styles based on user preference.

* **Double Slash** (Stored as `//` in Fusion)

```
// This is a single-line comment
int count = 10  // End-of-line comment

// Multiple single-line comments
// can be used for longer
// explanations
```

* **Single Quote** (User preference, converted to `//`)

```
' This is a single-line comment
int count = 10  ' End-of-line comment

' Multiple single-line comments
' using single quotes
```

**Note**: Both styles work identically. Fusion internally stores all comments as `//`. User can configure IDE preference.

---

### Multi-Line Comments

Description: Block comments spanning multiple lines.

```
/* 
 * This is a multi-line comment
 * Spanning multiple lines
 * Useful for longer explanations
 */

void function processData(Data data)
    /* Quick inline multi-line comment */
    data.process()

/*
 * Function: calculateDistance
 * Parameters:
 *   - x1, y1: First point
 *   - x2, y2: Second point
 * Returns: Distance between points
 */
float function calculateDistance(float x1, float y1, float x2, float y2)
    float dx = x2 - x1
    float dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
```

---

### Region Blocks

Description: Collapsible code sections for IDE organization.

* **Purpose**: Organize large files into logical sections
* **IDE Support**: Regions can be collapsed/expanded in IDE
* **No Runtime Effect**: Pure organizational feature

```
#Region Initialization Code
void function initialize()
    setupSystem()
    loadConfiguration()
    connectDatabase()

void function setupSystem()
    // System setup code
#End Region

#Region Helper Functions
void function helper1()
    // Helper implementation

void function helper2()
    // Helper implementation

private void function internalHelper()
    // Internal helper
#End Region

#Region Data Structures
class DataCache
    // Cache implementation

struct CacheEntry
    string key
    string value
#End Region
```

**Features**:
* String literal displays in IDE when collapsed
* Can nest regions
* Helps navigate large files
* No effect on compilation
* IDE shows as: `[+] Initialization Code`

---

### Documentation Comments

Description: Special comments for API documentation generation.

```
/**
 * Calculates the distance between two points in 2D space.
 * 
 * @param x1 X coordinate of first point
 * @param y1 Y coordinate of first point
 * @param x2 X coordinate of second point
 * @param y2 Y coordinate of second point
 * @return Distance between the points
 * @example
 *   float dist = calculateDistance(0, 0, 3, 4)  // Returns 5.0
 */
float function calculateDistance(float x1, float y1, float x2, float y2)
    float dx = x2 - x1
    float dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
```

---

## Async and Concurrency

**Status:** [DESIGN] files/FEATURES.md Task 42 - see `files/Concurrency.md` and `files/Service.md`

Description: Built-in support for asynchronous programming.

* Async/Await: Modern asynchronous pattern
     * Native language support
     * Task-based model
     * Automatic state machine generation

* Parallel Processing: Multi-threading support
     * Thread-safe collections
     * Atomic operations
     * Lock-free structures

```fusion
// Async function - return-type-first syntax
async Result<Spaceship, string> function downloadShipData(string url)
    var response = await http.get(url)

    if response.statusCode != 200
        return Result.Error("HTTP error: {response.statusCode}")

    var data = await response.readBody()
    var ship = parseShipData(data)
    return Result.Ok(ship)

// Parallel processing
async void function updateFleet(List<Spaceship> fleet, float deltaTime)
    var tasks = List<Task>()

    for ship in fleet
        var task = async:
            ship.update(deltaTime)
        tasks.append(task)

    await Task.waitAll(tasks)

// Concurrent data structures
var safeQueue = ConcurrentQueue<Task>()
parallel for i in range(1000):
    safeQueue.enqueue(createTask(i))
```

---

## Collections (as built)

**Status:** [DONE 18.5] List, Map (alias Dictionary), text helpers, program arguments, console input, files, standard-library layers

**`List<T>`** (Task 18.5.1, user decisions 2026-10-11) - a growable list of any value type:
numbers, chars, bools, text, bytes, structs, and lists (`List<List<int>>`). It is a
**reference with a count** (Task 32.10a, user decisions 2026-10-29): in normal code - a
variable, a parameter, an element - `b = a`, passing and returning share the same list, and
it is freed when its last holder lets go; `byVal a` (or `byValue a`) makes a deep copy, and a
`byVal List<int> xs` parameter gets one. **Inside a struct** it is copied with the struct,
unless the field is written `byRef`. It is never null - empty when declared. A Map works the
same way. Arrays follow once they can grow (Task 45); until then they are copied.

`xs.toList(copy = true)` (Task 32.10a.1): a List's copy, or with `false` the same list,
shared; on a one-dimensional array, a new List with copies of its elements (sharing needs
arrays on the heap - Task 45). Both are revisited with multi-dimensional arrays. `null` is an
error on an array, List or Map until `[arrays]` / `[lists]` / `[maps] nullable = true` (Task 30.3). Built-in generic
types - user-written generics come later, with classes. In C each element type has its own
small set of functions, made only when used, so there is no boxing and no speed cost.

```
List<int> xs = [3, 1, 2]        // a literal takes the declared type; List<int>() is empty
xs.add(10)                      // add(v), insert(i, v), removeAt(i), remove(v) -> bool, clear()
xs[0] = 7                       // reading or writing outside the list is a run-time error
int n = xs.len()                // also len(xs)
bool has = xs.contains(2)       // contains(v), indexOf(v) -> -1 when missing
xs.sort()                       // numbers, chars, bools, text; sortBy((a, b) : ...) for any type
List<int> part = xs.slice(1, 2) // start, count
List<int> big = xs.filter((int x) : x > 2)
List<string> labels = xs.map(label)          // a function (int) : string
int total = xs.reduce(0, (int sum, int x) : sum + x)
for x in xs                     // each element; a list or an array
    print("{x}")
bool same = xs == [7, 1, 2, 10] // element by element
```

* `sortBy` is stable - equal elements keep their order
* `for x in xs` gives `x` the element type; strings and other managed elements are copied
  into `x` for each pass, so the body may change the list safely. `for` loops over
  `range(...)`, a List or an array - anything else is a compile error (before Task 18.5.1
  such a loop silently ran 0..9)
* Mutating methods (`add`, `insert`, `removeAt`, `remove`, `clear`, `sort`, `sortBy`) need a
  variable (or a field / element of one) that isn't const
**`Map<K, V>`** (Task 18.5.2; also written `Dictionary<K, V>` - the same type, user decision
2026-10-11: "Map is easier to type"). Keys are `string`, `int` or `char`; values any value
type (lists and maps too). A map remembers the order its keys were added - `keys()`,
`values()` and `for k in m` follow it (as in Python and C#). A value like a list: copies are
independent, freed automatically. In C an open-addressing hash table over the entries.

```
Map<string, int> ages = Map<string, int>()   // `Map<string, int> ages` starts empty too
ages["Alice"] = 30              // adds the key, or replaces its value
int a = ages["Alice"]           // reading a missing key is a run-time error naming the key
bool known = ages.has("Bob")
int b = ages.get("Bob", 0)      // the value, or the default when the key is missing
bool gone = ages.remove("Bob")  // false when it wasn't there
List<string> names = ages.keys()        // also values(), len(), clear()
for name in ages                // the keys
    print(name)
bool same = ages == other       // the same keys with equal values, in any order
```

* `m["a"][0] = 5` needs `"a"` to be there already; only the final `m[k] = v` adds a key
* A name after `.` may be a word Fusion reserves for later (`m.get`, `x.set`) - after a dot
  it can only be a field or method name
**Text and lists** (Task 18.5.3) - each also a method (`s.split(",")`, `parts.join(", ")`):
* `split(s, sep)` - every piece between separators, empty ones too (`"a,,b"` -> `a`, `""`,
  `b`; `""` -> one empty piece, as Python); an empty separator splits into characters
* `join(parts, sep)` - a `List<string>` into one string
* `lines(s)` - the lines without their `\n` (a `\r` before it is dropped too); a final
  newline doesn't make an empty last line
* `words(s)` - the pieces between runs of spaces, tabs and newlines; never an empty word

**Program arguments, console input, exit** (Task 18.5.4):
* `void function main(string... args)` (user decision 2026-10-11 - "List<string> args seems a
  bit too wordy") - `args` is a `string[]` of any length (`len(args)`, `args[0]`,
  `for a in args`); main may also take nothing. The program's name and `--headless` are not
  in it. On Windows the arguments are read as UTF-16 and turned into UTF-8, so accented
  ones arrive intact. `...` is only for main for now - functions taking any number of
  values come later. Before Task 18.5.4 other main parameters were accepted with a warning
  and silently ignored; now they are an error
* `readLine()` - the next line of input without `\n` / `\r\n`, of any length; `""` at the
  end of input. `isEndOfInput()` - true when nothing is left to read. On Windows the console
  reads UTF-8
* `exit(code)` - ends the program at once with that exit code (the "Press any key" wait
  still happens when someone is at the console)
* `run(command)` (Task 28.1.1) - runs another program through the system shell (`cmd /c`
  on Windows, `/bin/sh -c` elsewhere), **waits** until it ends and returns its exit code.
  A program that runs and fails is not an error - its code comes back (a command that
  doesn't exist gives the shell's own non-zero code). Only a shell that can't be started is
  a `ProcessError`. Output printed before the call is flushed first, so lines stay in
  order. On Windows the command is passed to `cmd` exactly as written, quotes included
  (`run("\"C:/My Apps/x.exe\" \"a b\"")`). Not waiting: `run("start notepad")` on
  Windows. Running programs will be a declared capability (Task 39). Later: capturing a
  program's output, and a separate `start`

**Files** (Task 18.5.5):
* `readText(path)` (the whole file - it must be valid UTF-8 text; a UTF-8 byte-order mark at
  the start is dropped, as C# does), `readLines(path)` -> `List<string>` (as `lines`),
  `writeText(path, s)` (creates or replaces), `appendText(path, s)`, `readBytes(path)` ->
  `bytes` and `writeBytes(path, b)` for binary files, `fileExists(path)` (a file, not a
  folder), `deleteFile(path)`
* Files are read and written byte for byte - no newline translation
* Paths are relative to the folder the program runs in, `/` or `\\` between folders; names
  with accents work on Windows (the wide-character file functions)
* A failure - a missing file, no permission, a missing folder - stops the program with a
  run-time error naming the file and the reason; check first with `fileExists`. Error
  handling (Task 26) will make these catchable. File access will be a declared capability
  (Task 39)

**Standard-library layers** (Task 18.5.6 - "layer the stdlib from day one", the lesson from D,
whose library assumed a garbage collector and split the ecosystem when GC became optional).
`fusion.toml` `[stdlib] layer` says how much a project may use; each layer adds to the one
before it:
* **core** - no heap: numbers, chars, bools, fixed arrays, structs of those, `range`, `len`
  of an array, `toByte`, `charCode` / `fromCharCode`. For the smallest embedded devices
* **alloc** - adds memory: text, `bytes`, `List`, `Map` and every function on them
* **std** (the default) - adds the operating system: `print`, `readLine` / `isEndOfInput`,
  files, `exit`, `run`, and main's arguments (`string... args`)
* Using something above the project's layer is a compile error, once per place:
  "'print' needs the std layer, but this project uses alloc ([stdlib] layer in fusion.toml)";
  in a core project any text, bytes, List or Map - a value or a declared type - is refused
* `print` is std, as console output is an operating-system service (Rust's `core` / `alloc`
  can't print either); an embedded program reports through its own device
* Every built-in is tagged with its layer (src/semantic/name_resolver.py) - the groundwork
  for capability checks (Task 39): a library will declare the layer it needs

Example program using all of it: `examples/wordcount/` - modules, a file, `List`, `Map`,
`sortBy` and the text helpers (Task 18.5.7).

---

## Module System

**Status:** [DONE 18.4] module folders, `import`, aliases, `public` / `private`, `--interface`; class files [PLANNED 32]

Description: Organized code structure with clear dependencies.

**As built (Task 18.4.2, user decisions 2026-10-10)** - Fusion has structs and functions
(no classes yet), so modules hold those; the class-based design below stays the long-term
direction:

* **A module is a folder** next to the program's main file: every `.fusion` file in
  `money/` belongs to module `money`, and they share each other's names freely.
  `geometry/shapes/` is module `geometry.shapes` (folders nest; modules don't contain each
  other). The program itself is just its main file, so a folder of separate programs (like
  `examples/`) still works
* **Imports come first in a file, and each file imports what it uses** (as in Go, Java and
  Python):
  ```
  import money                    // money.round(x), money.Price, money.make(5)
  import money.Price              // Price - one name, no prefix
  import money.*                  // every name, no prefix
  import geometry.shapes          // used by the last part of its path: shapes.area(2)
  import lib.utils as libutils    // an alias: libutils.trim(s)
  money.Price p = money.make(100) // a struct from another module in a type
  ```
* **Each module is loaded once**, from one list of loaded modules: imports may criss-cross
  (`money` imports `tax`, `tax` imports `money`) without looping
* **Name rules:** a file's own names win over a `.*` import; the same name from two `.*`
  imports is an error where it's used ("'f' is ambiguous: a.f or b.f - use the module
  prefix"); `import money.Price` next to a declared `Price` is an error; **two different
  modules with the same name** in one file (`shop/utils`, `lib/utils`) are an error - give
  one an alias with `as`. A local variable may share a name with an imported one; inside
  its block the variable wins
* Only the main file may have `main`. A module can't be named after a built-in type class
  (`String`, `Int`, ...) or contain `__`
* All modules compile into one C file; `money.round` is `fu_money__round` there, and two
  Fusion names that would share a C name are reported
* **Module interfaces** (Task 18.4.4): `fusion main.fusion --interface [module]` prints the
  public structs and functions of the modules a program imports, with their types and
  defaults - what other modules may rely on. The groundwork for library signatures and
  capability checks (Task 39):
  ```
  module money
      public struct Price
          int cents
      public Price function make(int cents)
      public string function show(Price p)
  ```
* Example: `examples/shop/` - a program of three files in two modules
* **`public` / `internal` / `private`** (Task 18.4.3; 32.2a; 32.2h, user decisions
  2026-10-30): structs, classes, enums, error types and functions are public unless written
  `internal`; module variables private to their module unless written `public` / `internal`.
  `internal` means the namespace - a file without one: its module. Other modules use public
  names through `money.round`, `import money.round` or `import money.*` (public names only);
  a module's own files see all of each other's names. `private` on a top-level struct,
  class, enum, error type or function is an error ("write 'internal'"). A public function or
  struct can't use an internal struct of its module in its parameters, result or fields
  ("make 'Secret' public too") - other modules would get values of a type they can't name
  ```
  public struct Price          // other modules may use it
      int cents
  public Price function make(int cents) : Price(cents + fee())
  internal int function fee() : 50   // only module money (or its namespace) sees it
  ```
* **`namespace Shop.Tools`** (Task 32.2h): the file's first line, before the imports - a line,
  not a folder. Modules whose files share a namespace see each other's internal names and
  class members; Fusion's own libraries use `namespace Core`

---

### File Organization

Description: Clear structure for maintainability.

* **Rules**
     * One class per file (class name matches filename)
     * Module groups related files in directory
     * Special module.fusion file defines module
     * Subclasses can be nested within class file
     * Modules cannot be nested in other modules

* **Directory Structure**

```
project/
├── Spaceships/
│   ├── module.fusion          // Module definition
│   ├── Spaceship.fusion        // One class
│   ├── Warship.fusion          // One class
│   └── CargoShip.fusion        // One class
├── Weapons/
│   ├── module.fusion
│   ├── Laser.fusion
│   └── Missile.fusion
└── main.fusion
```

---

### Module Definition

Description: Define module in module.fusion file.

```
// Spaceships/module.fusion
module Spaceships

export Spaceship
export Warship
export CargoShip

// Private helper (not exported)
void function validateShipName(string name)
    return name.length > 0
```

---

### Class Files

Description: One class per file with optional nested subclasses.

```
// Spaceships/Spaceship.fusion
class Spaceship
    string name
    float speed
    
    constructor(string name, float speed)
        this.name = name
        this.speed = speed
    
    void function start()
        print("{name} started")
    
    // Nested subclass allowed
    class Engine
        float power
        
        constructor(float power)
            this.power = power
```

---

### Import Syntax

Description: Multiple ways to import modules and classes.

```
// Import entire module
import Spaceships

// Use with module prefix
Spaceship ship = Spaceships.Spaceship("Enterprise", 100.0)

// Import specific class
import Spaceships.Spaceship

// Use without prefix
Spaceship ship = Spaceship("Enterprise", 100.0)

// Import all from module
import Spaceships.*

// Use all exported classes
Spaceship ship = Spaceship("Enterprise", 100.0)
Warship warship = Warship("Destroyer", 150.0, 50)
```

---

### Visibility Control

Description: Control what is accessible from outside module.

```
// module.fusion
module Spaceships

export Spaceship        // Public: can be imported
export Warship          // Public: can be imported

// CargoShip not exported - internal to module only

void function internalHelper()  // Not exported - module-private
    // ...
```

---

## Complete Game Example

**Status:** [DESIGN] shows the full intended language - most of it is not built yet

Description: Putting it all together in a simple space game using Fusion v2 syntax.

```
// game.fusion - Complete space game example
module SpaceGame

// Vector math structure - a plain value type (structs hold fields only)
struct Vector2
    float x
    float y

// Vector math lives in ordinary functions
Vector2 function vadd(Vector2 a, Vector2 b)
    return Vector2(a.x + b.x, a.y + b.y)

Vector2 function vscale(Vector2 v, float scalar)
    return Vector2(v.x * scalar, v.y * scalar)

// Base game object interface
interface IGameObject
    property Position: Vector2 { get; set; }
    void function update(float deltaTime)
    void function render()

// Spaceship class
class Spaceship implements IGameObject
    property Position: Vector2 { get; set; }
    property Velocity: Vector2 { get; set; }
    property Health: float { get; set; }
    property Name: string { get; private set; }
    
    private float fuel
    private bool isActive
    
    constructor(string name, Vector2 startPos)
        this.Name = name
        this.Position = startPos
        this.Velocity = Vector2(0, 0)
        this.Health = 100.0
        this.fuel = 100.0
        this.isActive = true
    
    void function accelerate(Vector2 direction, float power)
        if fuel > 0 and isActive
            Velocity = vadd(Velocity, vscale(direction, power))
            fuel -= power * 0.1
    
    void function update(float deltaTime)
        if isActive
            Position = vadd(Position, vscale(Velocity, deltaTime))

            // Apply drag
            Velocity = vscale(Velocity, 0.99)
            
            // Regenerate fuel slowly
            if fuel < 100
                fuel += deltaTime * 2.0
        end loop
    
    void function render()
        if isActive
            drawSprite("ship", Position.x, Position.y)
            drawHealthBar(Position.x, Position.y - 20, Health)
    
    void function takeDamage(float amount)
        Health -= amount
        if Health <= 0
            Health = 0
            isActive = false
            print("{Name} destroyed!")

// Projectile class
class Projectile implements IGameObject
    property Position: Vector2 { get; set; }
    property Velocity: Vector2 { get; set; }
    property Damage: float { get; private set; }
    
    private float lifetime
    private float maxLifetime = 3.0
    
    constructor(Vector2 startPos, Vector2 velocity, float damage)
        this.Position = startPos
        this.Velocity = velocity
        this.Damage = damage
        this.lifetime = 0
    
    void function update(float deltaTime)
        Position = vadd(Position, vscale(Velocity, deltaTime))
        lifetime += deltaTime
    
    void function render()
        if lifetime < maxLifetime
            drawCircle(Position.x, Position.y, 3, Color.Yellow)
    
    property IsExpired: bool
        get
            return lifetime >= maxLifetime

// Game manager class
class GameManager
    private List<Spaceship> ships
    private List<Projectile> projectiles
    private float gameTime
    private bool isRunning
    
    constructor()
        ships = List<Spaceship>()
        projectiles = List<Projectile>()
        gameTime = 0
        isRunning = false
    
    void function initialize()
        // Create player ship
        Spaceship player = Spaceship("Player", Vector2(400, 300))
        ships.append(player)
        
        // Create enemy ships
        for i in range(5)
            Vector2 enemyPos = Vector2(100 + i * 150, 100)
            Spaceship enemy = Spaceship("Enemy-{i}", enemyPos)
            ships.append(enemy)
        end loop
        
        isRunning = true
        print("Game initialized with {ships.Count} ships")
    
    void function update(float deltaTime)
        if not isRunning
            return
        
        gameTime += deltaTime
        
        // Update all ships
        for ship in ships
            ship.update(deltaTime)
        end loop
        
        // Update projectiles
        for projectile in projectiles
            projectile.update(deltaTime)
        end loop
        
        // Remove expired projectiles
        projectiles = projectiles.filter(lambda p: not p.IsExpired)
        
        // Check collisions
        checkCollisions()
        
        // Remove destroyed ships
        ships = ships.filter(lambda s: s.Health > 0)
        
        // Check win/lose conditions
        if ships.Count == 1
            print("Victory! Time: {gameTime} seconds")
            isRunning = false
    
    void function render()
        clearScreen()
        
        for ship in ships
            ship.render()
        end loop
        
        for projectile in projectiles
            projectile.render()
        end loop
        
        drawText("Ships: {ships.Count}", 10, 10)
        drawText("Time: {gameTime}", 10, 30)
    
    void function fireProjectile(Spaceship fromShip, Vector2 direction)
        Projectile projectile = Projectile(
            fromShip.Position,
            vscale(direction, 500.0),
            25.0
        )
        projectiles.append(projectile)
    
    private void function checkCollisions()
        for projectile in projectiles
            for ship in ships
                float dx = ship.Position.x - projectile.Position.x
                float dy = ship.Position.y - projectile.Position.y
                float distance = dx * dx + dy * dy
                
                if distance < 400  // 20 pixel radius squared
                    ship.takeDamage(projectile.Damage)
                    projectile.lifetime = projectile.maxLifetime
            end loop
        end loop

// Main game loop
void function main()
    GameManager game = GameManager()
    game.initialize()
    
    float lastTime = getTime()
    
    while game.isRunning
        float currentTime = getTime()
        float deltaTime = currentTime - lastTime
        lastTime = currentTime
        
        // Handle input
        if isKeyPressed(Key.Space)
            Spaceship player = game.ships[0]
            game.fireProjectile(player, Vector2(0, -1))
        
        if isKeyDown(Key.Left)
            game.ships[0].accelerate(Vector2(-1, 0), 10.0)
        
        if isKeyDown(Key.Right)
            game.ships[0].accelerate(Vector2(1, 0), 10.0)
        
        // Update and render
        game.update(deltaTime)
        game.render()
        
        // Cap framerate
        sleep(16)  // ~60 FPS
    end loop
```

---

## Build and Compilation

**Status:** [PARTLY] `fusion.toml` with [indentation], [source], [structs], [strings], [stdlib] and [errors] is built (12.12, 19.6, 18.2, 18.3, 18.5.6, 26.5); other config formats [PLANNED 31]; enforcing [safety] / [backend] [PLANNED 31.5]; build modes and commands: no task yet

Description: Flexible compilation options for different targets and use cases.

---

### Compilation Modes

Description: Multiple ways to run and build Fusion code.

* **Script Mode**: Interpreted execution
     * Run directly without compilation
     * Fast development iteration
     * Slower execution
     * Like Python

```
fusion run game.fusion
```

* **Executable Mode**: Native compilation
     * Compile to standalone executable
     * Fast execution
     * Platform-specific binary
     * Like C/Java compiled

```
fusion build game.fusion --output game.exe
```

* **Library Mode**: Shared library
     * Compile to DLL/shared library
     * Reusable across projects
     * Link at runtime or compile time
     * Platform-specific format

```
fusion build engine.fusion --lib --output engine.dll
```

* **JIT Mode**: Just-in-time compilation
     * Compiles during first run
     * Caches compiled code
     * Balance of flexibility and speed
     * Like Java/C#

---

### Project Configuration

**Design status (Task 12.12, decided 2026-09-13):** unlike most of this "Build and
Compilation" section (which describes an aspirational `fusion run`/`fusion build` CLI that
doesn't exist yet - the actual compiler today is invoked as `python main.py <source.fusion>`),
this subsection is **partially implemented now**. Fusion's core concept is per-project
configurability (see "Language Philosophy"), but the compiler previously hardcoded its
indentation settings directly in the lexer with no way to override them - a real gap between
the concept and the implementation. This section is the config-format ADR that closes it.

**Four formats (Task 31, built - user decisions 2026-10-28):** `fusion.toml` is the default;
`fusion.yaml` (or `.yml`), `fusion.json` and `fusion.ini` are alternatives - for a company
that standardises on YAML, or INI for legacy hardware and software. All four give the same
settings and are checked by the same rules.
* **Names (Task 32.0):** camelCase (`tabWidth`, `maxCallDepth`), read ignoring case and `_` -
  `tab_width`, `tabWidth` and `TABWIDTH` are the same setting; one written twice is an error
* **The master template:** `files/fusionSettings.xml` lists every setting, the values it can
  have, its default and what it does. It is read only; a project's settings file carries its
  choices, based on it
* **Finding the file:** next to the source file, then in the current folder; in a folder the
  first of TOML, YAML, JSON, INI is used. **No settings file at all:** the compiler writes a
  new `fusion.toml` from the template - every setting at its default, each with a comment
  (`--no-new-config`, or `FUSION_NO_NEW_CONFIG=1`, turns that off for build scripts)
* **Changing format:** `[project] fusionSettingFormat = "TOML"` (TOML / YAML / JSON / INI).
  Set it to another format and the next compile writes the settings in that format (with
  the template's comments) and keeps the old file as a backup (`fusion.toml.bak`) - only one
  settings file is active. Your own comments live on in the backup
* **INI** holds only text: `true` / `false` (nothing else) become true / false, whole numbers
  become numbers, `"quoted"` or bare text stays text. **YAML** reads a bare `no` / `off` as
  false (the "Norway problem") - quote text values; a wrong type is reported
* **Reading:** Python's own readers for TOML, JSON and INI, PyYAML for YAML (`safe_load` -
  never runs code from the file; needed only by a YAML project). Fusion's own readers - also
  for XML and CSV, and recovering from small mistakes - come with its data-formats module
  (files/FEATURES.md 43.2); a dedicated `config.fusion` program will create settings files

**Format decision (2026-09-13, extended by Task 31 above):** an optional `fusion.toml` file, using TOML - chosen over YAML (would
need a new dependency; the project has none today) and a custom Fusion-native format (would
mean writing and maintaining a whole new parser for no real benefit). Python 3.11's stdlib
`tomllib` parses it with zero added dependency.

**Decision update (2026-10-07) - not yet implemented:** the user decided Fusion will accept
the configuration file in four interchangeable formats - `fusion.toml`, `fusion.yaml`,
`fusion.json`, and `fusion.ini` - so older applications and tools that can only produce JSON
or INI can still configure a project. TOML stays the documented default. All four will load
through one shared validation path, so they always mean the same thing; finding more than
one config file in the same place is planned to be an error rather than a silent choice.
YAML is the only format that adds a dependency (PyYAML), loaded only when a project uses it.
Tracked as Task 31 in `files/FEATURES.md`. **Until Task 31 ships, only `fusion.toml` works.**

**Lookup decision:** the compiler looks for `fusion.toml` next to the source file being
compiled first, then in the current working directory. A missing file is not an error - every
setting just uses its default, identical to the compiler's previous hardcoded behavior. A
*present but malformed* file (bad TOML syntax, or a recognized key with an invalid value) IS
a hard error with a clear message - never a silent fallback to defaults, so a typo doesn't
silently compile with different settings than intended. (Deliberately not a parent-directory
walk like git's `.git` or npm's `package.json` - Fusion has no multi-file project/workspace
concept yet, so that would solve a problem that doesn't exist yet. Revisit once it does.)

**v1 scope decision:** only `[indentation]` was wired to real behavior at first - it reaches
`src/lexer/lexer.py`'s `IndentationTracker` exactly as this section's own hardcoded values
used to. Since then `[source]` (Task 19.6) reaches the lexer and `[structs]` (Task 18.2)
reaches the semantic analyzer. `[safety]` and `[backend]` are parsed and validated (so a project can already state
its intent and catch typos) but **not yet enforced anywhere** - the same "recognized, not yet
implemented" status as the `Unique`/`Shared`/`Weak` keywords (see "Memory Management").

```toml
# fusion.toml - optional, place next to your .fusion source file (or in the cwd)

[indentation]
tabWidth = 4        # spaces per tab (default: 4)
allowMixed = true   # allow mixed tabs/spaces with a warning instead of an error (default: true)

[source]
allowUnicodeIdentifiers = false   # identifiers ASCII-only by default (homoglyph defense) -
                                    # see "Source Text Rules" under Syntax Overview

[strings]                      # Tasks 18.3.2b / 18.3.4b - see "String Implementation"
encoding = "utf-8"             # utf-8 (default) | ascii; utf-16 / utf-32 reserved (future)
maxLength = "max"             # "max" (default) = no limit; a number = error when exceeded

[stdlib]                       # Task 18.5.6 - see "Collections (as built)" / layers
layer = "std"                  # std (default) | alloc | core

[modules]                      # Task 44.1 - see "Constants"
variables = true               # module-level variables; constants are always allowed

[collections]                  # Task 32.4 - foreach, Collection<T>
allowChangeWhileLooping = false   # true: a collection class of your own may change in a loop

[memory]                       # Task 48 - files/Ownership.md
assignment = "move"            # move (default, Task 48.9): `Car b = a` hands it over, `a` is dead
                               # until a new value; share: two names, one object
moveFieldOut = false           # true: a field may be moved out of a struct the function owns -
                               # the struct is then unusable (as Rust); false: fields only borrowed

[interfaces]                   # Task 32.5a - see "Interfaces and Contracts"
defaultMethods = false         # true: an interface's function may have code (a default)

[visibility]                   # Task 32.2h - see "Modules" / public, internal, private
required = false               # true: public / internal / private must be written on every
                               # top-level item and class member

[conditions]                   # Task 30.9 - see "Null Handling" / numbers as conditions
numbers = "positive"           # positive (default): if / while count is count > 0;
                               # nonzero: count != 0 (C, Python); off: bool only

[numbers]                      # Task 27.2f - see "The Semantic Contract"
overflowWrap = false          # true: whole-number + - * wraps (a byte: 255 + 1 is 0) -
                               # false (default): an OverflowError (Task 32.0)
autoWidening = false          # false: an int used as a float must fit exactly - a written
                               # number that doesn't is a compile error, a value a
                               # PrecisionError; true: widens automatically, with a warning

[errors]                       # Task 26.5 - see "Error Handling"
returns = true                 # false: T, Error function / return Error / capturing are errors
exceptions = true              # false: try / catch / finally / throw are errors

[structs]                      # Task 18.2 - see "Structures and Value Types"
maxNestingDepth  = 3         # deepest struct nesting (1 = no struct inside a struct)
warnNestingDepth = 3         # warn when a struct reaches this depth (0 = never)
stringStorage     = "owned"   # each struct holds its own string value; "pooled" reserved (Task 29)
stringMutable     = true      # false = string fields can't be changed after construction
stringWarnLength = 64        # guideline: warn when a string field is longer (0 = never warn)
holdCollections   = true      # a struct field may be a List / Map; false: an error

[build]
waitAtExit = false           # true: wait for a key before the window closes (dev / examples)

[safety]
mode = "safe"        # safe (default) | strict (every warning is an error - security, no
                     # undetermined behaviour) | unsafe (the whole project - memory, assembly)
                     # (Task 27.2b); bounds checks stay. "strict" is reserved
maxCallDepth = "max"   # Task 27.2c: "max" - endless recursion is caught by stack use; a
                         # number also counts calls, for memory-constrained devices

[backend]
target = "c"         # "c" only for now - "llvm" is reserved for the Task 40 backend, not implemented yet
```

Every key is optional and defaults to the value shown above. An unknown key in `[structs]`
is an error (so a misspelled setting can't silently do nothing). See
`src/config/project_config.py` for the authoritative schema, validation rules, and error
messages.

---

### Build Commands

Description: Command-line build options.

```
// Run as script
fusion run game.fusion

// Compile to executable (debug)
fusion build game.fusion --debug --output game-debug.exe

// Compile to executable (release - optimized)
fusion build game.fusion --release --optimize --output game.exe

// Compile to library
fusion build engine.fusion --lib --release --output engine.dll

// Cross-compile for different platforms
fusion build game.fusion --target linux-x64 --output game-linux
fusion build game.fusion --target windows-x64 --output game.exe
fusion build game.fusion --target wasm --output game.wasm

// Compile with specific optimizations
fusion build game.fusion --optimize speed --output game-fast.exe
fusion build game.fusion --optimize size --output game-small.exe
```

---

### Build Configurations

Description: Common build scenarios.

**Development Build**

* Quick compilation
* Debug symbols included
* No optimizations
* Runtime checks enabled

```
fusion build game.fusion --debug --output game-dev.exe
```

**Release Build**

* Full optimizations
* No debug symbols
* Smaller binary
* Runtime checks disabled

```
fusion build game.fusion --release --optimize --output game.exe
```

**Library Build**

* Creates shared library
* Can be imported by other projects
* Platform-specific format

```
fusion build SpaceshipEngine.fusion --lib --release --output SpaceshipEngine.dll
```

---

### Output Targets

Description: Platform-specific compilation.

Platform | Target | Output Format
---|---|---
Windows | windows-x64 | .exe / .dll
Linux | linux-x64 | (binary) / .so
macOS | macos-arm64 | (binary) / .dylib
Web | wasm | .wasm

---

### Using Libraries

Description: Import compiled libraries in projects.

```
// Link against compiled library
fusion build game.fusion --link engine.dll --output game.exe

// In code
import SpaceshipEngine
Spaceship ship = SpaceshipEngine.createShip("Enterprise")
```

---

## Standard Library

**Status:** [PARTLY] strings, bytes, collections, files and console are built (18.3, 18.5), and `run(command)` runs another program (28.1.1); math, text formats and the rest: no task yet. Every built-in function and method, generated from the compiler: `files/Builtins.md`

Description: Comprehensive built-in library for common tasks and formats.

---

### Core Collections

* **List<T>**: Dynamic array with resizing
* **Dictionary<K,V>**: Hash map for key-value pairs
* **Set<T>**: Unique elements collection
* **Queue<T>**: FIFO queue
* **Stack<T>**: LIFO stack

---

### Math Library

* **Vector**: 2D, 3D, 4D vector operations
* **Matrix**: Matrix operations and transformations
* **Quaternion**: Rotation calculations
* **Math functions**: sin, cos, tan, sqrt, abs, pow, etc.

---

### File I/O

* **Synchronous**: Read/write operations that block
* **Asynchronous**: Non-blocking I/O with async/await
* **Streams**: Buffered reading and writing

---

### Text File Formats

Description: Built-in support for common text formats.

**Supported Formats**:
* **txt** - Plain text files
* **md** - Markdown documentation
* **JSON** - JavaScript Object Notation
* **XML** - Extensible Markup Language
* **CSV** - Comma-Separated Values
* **YAML** - YAML Ain't Markup Language
* **ini** - Configuration files

**API Example**:
```
import Fusion.IO.JSON

// Read and parse JSON
JSON data, Error err = JSON.readFile("config.json")
if not err
    string name = data.getString("name")
    int value = data.getInt("value")

// Write JSON
JSON output = JSON.create()
output.put("name", "Spaceship")
output.put("speed", 100.0)
err = JSON.writeFile("output.json", output)
```

**Features**:
* Format-specific reader/writer
* Format validation
* Custom format creator framework

---

### Programming Language Support

Description: Built-in compilers, parsers, and lexers for multiple languages.

**Supported Languages**:
* Go, Fusion, Java, C, C++
* VB.NET, JavaScript, HTML, CSS

**Components**:
* **Lexer**: Tokenize source code
* **Parser**: Build Abstract Syntax Tree (AST)
* **Compiler**: Generate executable/bytecode
* **Interpreter**: Execute code directly
* **Custom Language Creator**: Define new language syntax

**API Example**:
```
import Fusion.Compiler

// Compile Fusion code
Compiler fusionCompiler = Compiler.create(Language.FUSION)
Program program, Error err = fusionCompiler.compile("source.fusion")
if not err
    program.execute()

// Parse Java code to AST
Parser javaParser = Parser.create(Language.JAVA)
AST ast, Error err = javaParser.parse(javaCode)
```

---

### Image Formats

Description: Read, write, and manipulate common image formats.

**Supported Formats**:
* BMP - Bitmap
* JPEG/JPG - Joint Photographic Experts Group
* GIF - Graphics Interchange Format
* PNG - Portable Network Graphics

**API Example**:
```
import Fusion.Graphics.Image

// Load image
Image img, Error err = Image.load("photo.jpg")
if not err
    // Edit image
    img.resize(800, 600)
    img.rotate(90)
    img.setPixel(10, 10, Color.RED)
    
    // Save in different format
    err = img.save("output.png", ImageFormat.PNG)
```

**Features**:
* Pixel-level access
* Image transformations
* Format conversion
* Custom format support

---

### Advanced Binary Formats

user added note: eg fusionlib.Data.Zip or fusionlib.Data.PDF or fusionlib.Data.Docx
Description: Support for complex document and archive formats (see fusionlib.Data module).

**Supported Formats**:
* **DOC/DOCX** - Microsoft Word
* **XLS/XLSX** - Microsoft Excel
* **PDF** - Portable Document Format
* **ZIP** - Compressed archives

---

## Fusion Standard Library (fusionlib)

**Status:** [DESIGN] the planned library modules - no task yet

Description: Complete standard library with 21 modules organized in three tiers for clarity and ease of learning.

**Total**: 21 modules covering all application domains
* **Core Libraries** (5 modules): Essential functionality used in most programs
* **Additional Libraries** (12 modules): Domain-specific features for specialized applications
* **IDE & Development Libraries** (4 modules): Tools for development, testing, debugging, and documentation

**Import Syntax**: `import Fusion.<ModuleName>` or `import fusionlib.<ModuleName>`

---

### Core Libraries (Essential)

Description: Fundamental modules used in almost every Fusion application. Master these first.

**Quick Reference**:

Module | Purpose | Common Use Cases
---|---|---
**Core** | Essential types, Console I/O, DateTime | String manipulation, console apps, basic I/O
**Math** | Vector, Matrix, Quaternion, trigonometry | Games, graphics, physics, scientific computing
**Collections** | List, Dictionary, Set, Queue, Stack | Data storage, algorithms, LINQ operations
**Threading** | Threads, Goroutines, Channels, Async | Concurrency, parallel processing, async I/O
**IO** | File operations, Streams, Compression | File handling, data persistence, archives

---

#### Core Module (fusionlib.Core)

Description: Foundation types and basic operations required by all Fusion programs.

**Features**:
* Essential types (String, Byte, Int, Float, Boolean, Char)
* Array and collection basics
* Console I/O (print, input, formatting)
* DateTime and TimeSpan (date/time manipulation)
* Math basics (abs, min, max, round)
* String manipulation (substring, split, join, format)
* String interpolation (inline `{var}` and positional `{@1}` syntax)
* Type conversion and parsing
* Exception handling
* Object base class
* Memory management utilities

**String Interpolation**:

Fusion supports two powerful string formatting syntaxes for embedding values in strings:

**Syntax 1: Inline Interpolation** (`{variable}`)
```fusion
string name = "Alice"
int age = 30
print("Name: {name}, Age: {age}")  // Name: Alice, Age: 30

// Works with expressions
print("Next year: {age + 1}")  // Next year: 31
```

**Implemented today:** a variable name, or a struct field path such as `{player.name}` or
`{p.x}` (Task 18.2.1). Full expressions inside `{...}` (like `{age + 1}` above) are not
implemented yet. A whole array or struct can't be printed - print its elements or fields.
An interpolated string is an ordinary string value anywhere - `string s = "x is {x}"`,
`return "Hi {name}"`, `f("{a}-{b}")` (Task 18.3.3). `format(text, args...)` returns the text
`print` would write, with the same `{@N}` rules; `{@N}` placeholders only work in the text
given to `print` or `format`.

**A literal brace** (Task 28.1.5): `\{` and `\}` - `print("\{name\} is {name}")` prints
`{name} is Alice`. A `{` on its own always starts an interpolation, and one that isn't
followed by a name or `@N` is an error, never silently printed as text.

**Syntax 2: Positional Formatting** (`{@1}`, `{@2}`, ...)
```fusion
string name = "Alice"
int age = 30

// Arguments referenced by position (1-indexed)
print("Name: {@1}, Age: {@2}", name, age)  // Name: Alice, Age: 30

// Reuse arguments (great for translations)
print("{@1} is {@2} years old. {@1} likes coding.", name, age)
// Output: Alice is 30 years old. Alice likes coding.

// Mix with expressions
print("User: {@1} ({@2})", name, age + 1)

// Any order (translations often reorder words)
print("{@2}, {@1}", "first", "second")   // second, first
```

**Rules (implemented, Task 18.2.2b - in `print` for now):**
* `{@N}` is the Nth argument after the text, counting from 1 - in any order, as often as
  needed, and mixable with `{name}` values in the same text
* Each argument is evaluated **once, left to right as written** - a repeated `{@1}` never
  re-runs a function call, and the order the placeholders appear in doesn't change when the
  arguments run
* Errors: `{@N}` with no argument N, `{@0}`, extra arguments when the text has no `{@N}`, and
  an argument that can't be printed (a whole array or struct)
* An argument that no placeholder uses is a warning, not an error - a translated message may
  leave one out on purpose (its function calls still run)
* A general `format(...)` returning a string waits for runtime strings (Task 18.3)

**String templates (Task 29.3, implemented - user design 2026-10-27):** a fixed text that
works as a function - write it once, fill it in many times:

```fusion
const string SHOP = "Ann's"
template string welcome = "Welcome to {SHOP}, {@1}!"     // module-level

void function main()
    string city = "Paris"
    template string greet = "Hello {@1}, you are {@2} - {city}"   // inside a function
    print(greet("Ann", 30))          // Hello Ann, you are 30 - Paris
    (string) -> string f = welcome   // a template is a function value
```
* `template string name = "..."` marks the text constant and makes it an internal function:
  `greet` is like `string function greet(@1, @2)` whose body is the interpolated text. Every
  call reuses it; no `t"..."` prefix (decided 2026-10-27)
* Each `{@N}` takes any printable value; the number of values is the highest `{@N}`, checked
  at compile time (a gap such as `{@1} {@3}` is an error); values are given in order, not by
  name
* `{name}` is ordinary interpolation, read **when the template is called**; an unknown name
  is a compile error. A template inside a function is expanded where it is called, so it
  can use that function's variables. A module-level template may use module variables and
  constants only
* Passing a template on (4b): where a function type is written - a parameter
  `(string) -> string line`, a variable - it becomes a function value. A local template
  that uses the function's own variables can't be passed on (that needs closures)
* Templates are private to their module; an unused one is a warning
* `template` is special only before `string` and a name - it is still usable as an ordinary
  name, and the word is kept free for other kinds of templates later

**Example Usage**:
```fusion
import Fusion.Core

void function main(string... args)
    // Console I/O with inline interpolation
    print("Enter your name:")
    string name = Console.readLine()
    print("Hello, {name}!")

    // DateTime manipulation
    DateTime now = DateTime.now()
    print("Current time: {now.toString()}")

    // Positional formatting (translation-friendly)
    int count = 5
    print("Found {@1} files at {@2}", count, now.toString())

    // String operations
    string text = "Hello, World!"
    string[] words = text.split(", ")
    print("Words: {words.length}")
End function
```

---

#### Math Module (fusionlib.Math)

Description: Mathematical operations, vectors, matrices, and geometry for games and scientific computing.

**Features**:
* Vector types (Vector2, Vector3, Vector4)
* Matrix types (Matrix3x3, Matrix4x4)
* Quaternion (rotation calculations)
* Trigonometric functions (sin, cos, tan, asin, acos, atan)
* Exponential and logarithmic (exp, log, pow, sqrt)
* Geometric functions (distance, dot product, cross product)
* Interpolation (lerp, slerp, smoothstep)
* Random number generation
* Constants (PI, E, TAU)
* Numerical analysis utilities

**Example Usage**:
```fusion
import Fusion.Math

void function main(string... args)
    // Vector operations
    Vector3 position = Vector3(10.0, 20.0, 5.0)
    Vector3 velocity = Vector3(1.0, 0.0, 0.0)
    Vector3 newPos = position + velocity

    // Matrix transformations
    Matrix4x4 transform = Matrix4x4.identity()
    transform = transform.rotate(45.0, Vector3.up())

    // Distance calculation
    float distance = Vector3.distance(position, Vector3.zero())
    print("Distance from origin: {distance}")
End function
```

---

#### Collections Module (fusionlib.Collections)

Description: High-performance data structures for storing and manipulating collections of data.

**Features**:
* List<T> (dynamic array with resizing)
* Dictionary<K,V> (hash map, key-value pairs)
* Set<T> (unique elements, no duplicates)
* Queue<T> (FIFO queue)
* Stack<T> (LIFO stack)
* LinkedList<T> (doubly-linked list)
* PriorityQueue<T> (heap-based priority queue)
* HashSet<T> (fast lookup set)
* SortedSet<T> (ordered set)
* Concurrent collections (thread-safe variants)
* LINQ-style operations (map, filter, reduce, sort)

**Example Usage**:
```fusion
import Fusion.Collections

void function main(string... args)
    // List operations
    List<int> numbers = List<int>()
    numbers.add(1)
    numbers.add(2)
    numbers.add(3)

    // Dictionary usage
    Dictionary<string, int> ages = Dictionary<string, int>()
    ages["Alice"] = 30
    ages["Bob"] = 25

    // LINQ operations
    List<int> evens = numbers.filter((int x) : x % 2 == 0)
    int sum = numbers.reduce(0, (int acc, int x) : acc + x)
    print("Sum: {sum}")
End function
```

---

#### Threading Module (fusionlib.Threading)

Description: Concurrency primitives for multi-threaded and parallel programming.

**Features**:
* Thread creation and management
* Goroutines (lightweight threads)
* Channels (message passing, Go-style)
* Mutex and RWLock (synchronization primitives)
* Semaphore and Barrier
* Thread pools and task scheduling
* Atomic operations
* Thread-local storage
* Race condition detection
* Deadlock detection
* Async/await support

**Example Usage**:
```fusion
import Fusion.Threading

void function main(string... args)
    // Create channel
    Channel<int> ch = Channel.create<int>()

    // Launch goroutine
    go processData(ch)

    // Send data
    ch.send(42)
    ch.send(100)
    ch.close()

    // Async operation
    async Task<string> result = fetchDataAsync()
    string data = await result
    print("Received: {data}")
End function

void function processData(Channel<int> ch)
    while not ch.isClosed()
        int value = ch.receive()
        print("Processing: {value}")
    End while
End function
```

---

#### IO Module (fusionlib.IO)

Description: File system operations, stream processing, and data persistence.

**Features**:
* File operations (read, write, append, delete)
* Directory operations (create, delete, list, traverse)
* Path manipulation (join, normalize, absolute)
* Stream I/O (FileStream, MemoryStream, BufferedStream)
* Text readers and writers
* Binary readers and writers
* Async file I/O
* File watching (monitor changes)
* Compression (zip, gzip)
* Temporary files and directories

**Example Usage**:
```fusion
import Fusion.IO

void function main(string... args)
    // Write to file
    File.writeText("output.txt", "Hello, Fusion!")

    // Read from file
    string content = File.readText("output.txt")
    print("File contents: {content}")

    // Directory operations
    Directory.create("temp")
    string[] files = Directory.getFiles(".", "*.txt")
    print("Found {files.length} text files")

    // Async file I/O
    async Task<string> content = File.readTextAsync("large.txt")
    string data = await content
End function
```

---

### Additional Libraries (Extended Functionality)

Description: Domain-specific modules for networking, multimedia, system integration, and advanced features.

---

#### Networking & Data Processing

##### Net Module (fusionlib.Net)

Description: Network communication protocols and utilities.

**Features**:
* TCP client and server
* UDP sockets
* HTTP client (GET, POST, PUT, DELETE)
* HTTP server (basic web server)
* WebSocket client and server
* DNS resolution
* Email (SMTP, POP3, IMAP)
* FTP client
* SSL/TLS support
* Socket options and configuration
* Network utilities (ping, traceroute)

---

##### Data Module (fusionlib.Data)

Description: Parsing and serialization for common data formats.

**Features**:
* JSON parser and serializer
* CSV reader and writer
* XML parser and generator
* YAML parser and serializer
* Markdown parser and renderer
* INI file parser
* TOML parser
* Protocol Buffers support
* MessagePack support
* Custom format creators

---

#### System Integration

##### System Module (fusionlib.System)

Description: Operating system integration and process management.

**Features**:
* Process creation and management
* Environment variables
* Command-line execution
* DLL/shared library loading
* Platform detection (OS, architecture)
* System information (CPU, memory, disk)
* Registry access (Windows)
* User and group management
* Permissions and security
* System events and signals

---

##### Lang Module (fusionlib.Lang)

Description: Multi-language compilation and code execution support.

**Features**:
* C compiler integration
* C++ compiler integration
* Java compiler and JVM execution
* VB.NET compiler integration
* Python interpreter
* Ruby interpreter
* JavaScript engine (V8/SpiderMonkey)
* Go compiler integration
* Fusion self-hosting compiler
* Assembly language support
* Lexer and parser generators
* AST manipulation
* Code generation utilities

---

##### Languages Module (fusionlib.Languages)

Description: Internationalization and localization support.

**Features**:
* Internationalization (i18n)
* Localization (l10n)
* Translation management
* Locale support (date, time, currency formats)
* Resource bundles
* Text direction (LTR, RTL)
* Unicode handling
* Character encoding conversion
* Pluralization rules
* Language detection

---

#### Multimedia & User Interface

##### GUI Module (fusionlib.GUI)

Description: Cross-platform user interface framework.

**Features**:
* HTML5-compliant UI framework
* Cross-platform widgets (buttons, textboxes, labels, etc.)
* Layout managers (grid, stack, dock, flex)
* Event handling (click, hover, keyboard, etc.)
* Data binding
* Styling and theming (CSS-like)
* Drag and drop
* Menus and toolbars
* Dialogs (file picker, message box, etc.)
* Custom controls
* Accessibility support

---

##### Graphics Module (fusionlib.Graphics)

Description: 2D/3D rendering and game development utilities.

**Features**:
* 2D rendering (shapes, lines, curves)
* 2D sprites and textures
* 2D animations and sprite sheets
* 3D rendering pipeline
* 3D meshes and models
* Lighting and shadows
* Shaders (vertex, fragment, compute)
* Cameras and viewports
* Particle systems
* Physics integration
* Image loading and manipulation
* Game engine utilities

---

##### Audio Module (fusionlib.Audio)

Description: Sound playback, synthesis, and audio processing.

**Features**:
* Sound playback (WAV, MP3, OGG, FLAC)
* Music streaming and looping
* 3D spatial audio positioning
* Real-time synthesis (oscillators, filters)
* Audio effects (reverb, delay, distortion, EQ)
* Multi-track mixing
* Microphone input and recording
* MIDI support
* Audio analysis (FFT, spectrum, beat detection)

---

#### Advanced Features

##### Crypto Module (fusionlib.Crypto)

Description: Cryptography and security operations.

**Features**:
* Symmetric encryption (AES, ChaCha20)
* Asymmetric encryption (RSA, ECC)
* Hashing (SHA-256, SHA-512, BLAKE3)
* Password hashing (bcrypt, Argon2)
* Digital signatures
* Key derivation (PBKDF2, HKDF)
* Random number generation (CSPRNG)
* SSL/TLS support
* Certificate management

---

##### Database Module (fusionlib.Database)

Description: Database connectivity and ORM support.

**Features**:
* SQL database support (SQLite, PostgreSQL, MySQL, SQL Server)
* NoSQL support (MongoDB, Redis, Cassandra)
* Connection pooling
* Transaction management
* ORM (Object-Relational Mapping)
* Query builder
* Schema migration
* Database backup/restore
* Performance optimization

---

##### Web Module (fusionlib.Web)

Description: Web server and REST API framework.

**Features**:
* HTTP/HTTPS server
* WebSocket server
* Routing and middleware
* Template engine
* Session management
* Cookie handling
* REST API framework
* JSON/XML serialization
* File upload/download
* Static file serving
* Request/response handling
* CORS support

---

##### AI Module (fusionlib.AI)

Description: Machine learning and artificial intelligence.

**Features**:
* Neural networks (feedforward, CNN, RNN, LSTM)
* Training algorithms (backpropagation, gradient descent)
* Model serialization and loading
* Data preprocessing and normalization
* Feature extraction
* Classification and regression
* Clustering algorithms
* Natural language processing basics
* Computer vision utilities
* Pre-trained model integration

---

### IDE & Development Libraries

Description: Tools specifically designed for development workflow, testing, debugging, documentation, and IDE integration.

---

#### Reflection Module (fusionlib.Reflection)

Description: Runtime type introspection and dynamic code execution.

**Features**:
* Runtime type inspection
* Method invocation (call methods dynamically)
* Property access (get/set dynamically)
* Attribute/annotation reading
* Type creation at runtime
* Assembly loading
* Code generation (emit IL/bytecode)
* Serialization and deserialization
* Duck typing support
* Dynamic proxy generation

**IDE Integration**:
* Powers autocomplete and IntelliSense
* Enables runtime code analysis
* Supports dynamic plugin systems

---

#### Test Module (fusionlib.Test)

Description: Comprehensive testing framework with IDE integration.

**Features**:
* Unit testing framework
* Assertions (assertEquals, assertTrue, etc.)
* Test fixtures and setup/teardown
* Test suites and runners
* Mocking and stubbing
* Code coverage analysis
* Benchmarking tools
* Performance testing
* Parameterized tests
* Test reporting (HTML, XML, JSON)

**IDE Integration**:
* Test runner UI
* Real-time test execution
* Coverage visualization
* Failure navigation

---

#### Diagnostics Module (fusionlib.Diagnostics)

Description: Profiling, logging, and debugging utilities.

**Features**:
* Logging framework (levels: debug, info, warn, error)
* Performance profiling
* CPU profiling
* Memory profiling
* Execution tracing
* Stopwatch and timing
* Performance counters
* Event logging
* Crash reporting
* Debug output and breakpoints

**IDE Integration**:
* Profiler visualization
* Memory leak detection
* Performance hotspot highlighting
* Real-time log viewing

---

#### DocWiki Module (fusionlib.DocWiki)

Description: Automatic documentation generation and wiki creation during background compilation.

**Features**:
* Automatic documentation extraction from code comments
* Real-time wiki generation during IDE background compilation
* API reference generation from function signatures and types
* Markdown and HTML output formats
* Cross-referencing of types, methods, and modules
* Custom documentation templates
* Code example extraction and formatting
* Version history and changelog generation
* Search index creation
* Export to static site generators (Jekyll, Hugo, Docusaurus)

**Documentation Comment Formats**:
```fusion
/// Single-line documentation comment

/**
 * Multi-line documentation comment
 * Supports markdown formatting
 */

/**
 * Calculates the factorial of a number
 * @param n The input number (must be non-negative)
 * @return The factorial of n
 * @example
 *   int result = factorial(5)  // Returns 120
 */
int function factorial(int n)
    if n <= 1
        return 1
    End if
    return n * factorial(n - 1)
End function
```

**Supported Annotations**:
* `@param` - Parameter description
* `@return` - Return value description
* `@throws` - Exception descriptions
* `@example` - Code examples
* `@deprecated` - Mark as deprecated
* `@since` - Version information
* `@see` - Cross-references

**IDE Integration**:
* Real-time preview in IDE sidebar
* Hover tooltips with documentation
* Automatic wiki updates on file save
* Documentation coverage metrics
* Broken link detection
* IntelliSense powered by doc comments

**Example Usage**:
```fusion
import Fusion.DocWiki

/// Main application entry point
/// @param args Command-line arguments
void function main(string... args)
    // Generate documentation for the project
    DocWiki wiki = DocWiki.create("MyProject")
    wiki.setVersion("1.0.0")
    wiki.addSource("src/")
    wiki.setOutputFormat(DocFormat.HTML)
    wiki.generate("docs/")

    print("Documentation generated successfully!")
    print("Open docs/index.html to view")
End function

/**
 * Vector3 represents a 3D vector
 * @example
 *   Vector3 pos = Vector3(10.0, 5.0, 0.0)
 *   float length = pos.magnitude()
 */
class Vector3
    public float x
    public float y
    public float z

    /// Calculates the magnitude (length) of the vector
    /// @return The Euclidean length of the vector
    float function magnitude()
        return Math.sqrt(x * x + y * y + z * z)
    End function
End class
```

---

### Library Summary

**Quick Import Reference**:
```fusion
// Core Libraries (use in 90% of programs)
import Fusion.Core
import Fusion.Math
import Fusion.Collections
import Fusion.Threading
import Fusion.IO

// Networking & Data
import Fusion.Net
import Fusion.Data

// System Integration
import Fusion.System
import Fusion.Lang
import Fusion.Languages

// Multimedia
import Fusion.GUI
import Fusion.Graphics
import Fusion.Audio

// Advanced
import Fusion.Crypto
import Fusion.Database
import Fusion.Web
import Fusion.AI

// IDE & Development
import Fusion.Reflection
import Fusion.Test
import Fusion.Diagnostics
import Fusion.DocWiki
```

See **fusion_specs.md** for complete API documentation of each module.

**Module Count**: 21 total (5 Core + 12 Additional + 4 IDE)

---

## Callbacks and Events

**Status:** [DESIGN] no task yet (function values exist since 18.1.3)

Description: Function pointers and event-driven programming.

**Note**: Callbacks are not allowed in strict mode when performance is more important, as they can introduce overhead and unpredictability in execution.

**Function Types**:
```
// Define callback type
type Callback = void function(int result)
type EventHandler = void function(Object sender, EventArgs args)

// Use callback
void function processAsync(int data, Callback onComplete)
    int result = data * 2
    onComplete(result)

// Lambda callback
processAsync(42, lambda r: print("Result: {r}"))

// Events
class Button
    Event<void function(Button)> onClick
    
    void function click()
        onClick.invoke(this)

Button btn = Button()
btn.onClick += lambda b: print("Clicked!")
```

---

## External Interoperability

**Status:** [DESIGN] no task yet

Description: Integration with external code and systems.

---

### DLL Loading

```
import Fusion.System.DllLoader

DLL lib = DLL.load("mylib.dll")
type AddFunc = int function(int, int)
AddFunc add = lib.getFunction<AddFunc>("add")
int result = add(10, 20)
lib.unload()
```

---

### External Processes

```
import Fusion.System.Process

Process proc = Process.start("python", ["script.py"])
string output = proc.readOutput()
int exitCode = proc.exitCode
```

---

### Assembly Language

```
@Unsafe
int function fastAdd(int a, int b)
    int result
    asm
        mov eax, [a]
        add eax, [b]
        mov [result], eax
    return result
```

---

### External Compilers

```
import Fusion.Lang.Compiler

Compiler msvc = Compiler.loadExternal("fusion-msvc-x64.dll")
msvc.setOptimizationLevel(3)
CompileResult result = msvc.compile("code.fusion")
```

---

## Auto-Documentation

**Status:** [DESIGN] no task yet

Description: Generate documentation from source comments.

**Documentation Format**:
```
/**
 * @title Spaceship Class
 * @description Main spaceship entity
 * @category Game/Entities
 * @example
 *   Spaceship ship = Spaceship("Enterprise", 100.0)
 */
class Spaceship
```

**Generate**:
```bash
fusion doc generate --output ./wiki
```

---

**Word Documents**:
```
import Fusion.Documents

Document doc, Error err = Document.load("report.docx")
if not err
    string text = doc.getText()
    doc.appendText("New content")
    doc.save("modified.docx")
```

**Excel Spreadsheets**:
```
import Fusion.Spreadsheet

Workbook wb, Error err = Workbook.load("data.xlsx")
Sheet sheet = wb.getSheet("Sheet1")
string value = sheet.getCell("A1").getValue()
sheet.setCell("B1", "New Value")
wb.save()
```

**PDF Documents**:
```
import Fusion.PDF

PDF pdf = PDF.create()
pdf.addPage()
pdf.drawText(100, 700, "Hello PDF!")
pdf.save("output.pdf")
```

**ZIP Archives**:
```
import Fusion.Archive

ZIP zip = ZIP.create("archive.zip")
zip.addFile("file1.txt")
zip.addFile("file2.txt")
zip.close()
```

---

### Custom Format Creator

Description: Framework for defining new file formats.

```
import Fusion.Format

// Define custom format
FormatDefinition myFormat = FormatDefinition.create("myformat")
myFormat.setMagicBytes([0x4D, 0x59, 0x46, 0x4D])
myFormat.defineField("header", FieldType.STRING, 32)
myFormat.defineField("version", FieldType.INT32)

// Create reader/writer
FormatReader reader = FormatReader.create(myFormat)
FormatWriter writer = FormatWriter.create(myFormat)
```

---

### Localization Support

Description: Multi-language application support.

**Supported Languages**: English, Japanese, Spanish, French, German, Chinese, and more

**API Example**:
```
import Fusion.Localization

// Set current language
Locale.setCurrent("ja-JP")

// Get translated strings
string greeting = Locale.getString("greeting")  // "こんにちは"

// Formatted strings
string message = Locale.format("welcome_user", userName)
```

---

### Networking

* **HTTP**: Client and server implementations
* **WebSocket**: Real-time bidirectional communication
* **TCP/UDP**: Low-level socket programming

---

### Graphics and Audio

* **2D Graphics**: Drawing primitives, sprites, textures
* **3D Graphics**: Rendering, lighting, shaders
* **Audio**: Sound playback, synthesis, effects

---

### Threading and Concurrency

* **Task Parallel Library**: High-level task management
* **Thread Pools**: Efficient worker thread management
* **Channels**: Message passing between threads
* **Async/Await**: Simplified asynchronous programming

---

### Date and Time

* **DateTime**: Date and time manipulation
* **TimeSpan**: Duration calculations
* **Calendar**: Calendar-specific operations
* **Time zones**: Timezone conversions

---

### Regular Expressions

* **Pattern matching**: Powerful text search and replace
* **Validation**: Input validation with regex
* **Parsing**: Extract data from text

---

## Reserved Words and Operators

**Status:** [PARTLY] every operator listed is built except where its section says otherwise; several reserved keywords belong to planned features (match: 25, class / interface: 32)

Description: Complete list of language keywords and operators.

---

### Reserved Keywords

Description: Words that cannot be used as identifiers.

**`end` and `var` are not reserved** (Task 44.5, implemented): `End` closes a block; a
lowercase `end` does only right before a block word (`end function`, `end if`, ...) and is an
ordinary name everywhere else. `let`, `var` and `service` are reserved (Task 46, 2026-10-29).
In `match`, `_` skips a value: `case Rect(w, _)`.

**Control Flow**:
* `if`, `elif`, `else`
* `match`, `case`
* `for`, `while`, `do`
* `break`, `continue`
* `return`
* `end` (end loop, end function, etc.)

**Type Declarations**:
* `class`, `struct`, `interface`, `enum`
* `property`
* `var`, `const`
* `static`

**Access Modifiers**:
* `public`, `private`, `protected`, `internal`

**Memory & Pointers**:
* `unsafe`
* `allocate`, `deallocate`
* `Unique`, `Shared`, `Weak`

**Functions & Methods**:
* `function`
* `constructor`
* `lambda`
* `async`, `await`

**Modules**:
* `module`
* `import`, `export`

**Operators & Logic**:
* `and`, `or`, `not`
* `is`, `in`
* `where`

**Threading & Concurrency**:
* `thread`, `channel`
* `goroutine`
* `lock`, `unlock`
* `try` (try-with-resources)

**Error Handling**:
* `try`, `catch`, `finally`
* `throw`, `Error`

**Literals**:
* `true`, `false`
* `null`, `none`

**Special**:
* `this`, `super`
* `goto` (reserved but not used, except in unsafe embedded mode)

**Annotations & Directives**:
* `#Region`, `#End Region`
* `#[attribute]` (for annotations like `#[no_loop_protection]`)

---

### Operators

Description: Symbols used for operations.

---

#### Arithmetic Operators

Operator | Description | Example
---|---|---
`+` | Addition | `a + b`
`-` | Subtraction | `a - b`
`*` | Multiplication | `a * b`
`/` | Division | `a / b`
`%` | Modulo | `a % b`
`**` | Exponentiation | `a ** 2` (a squared)

---

#### Comparison Operators

Operator | Description | Example
---|---|---
`==` | Equal value | `a == b`
`!=` | Not `==` | `a != b`
`===` | Same type and equal value | `a === b`
`!==` | Not `===` | `a !== b`
`=` | Inside an `if` / `while` / `else if` condition: the same as `==` | `if a = b`
`<>` | Not equal to (alternative) | `a <> b`

**Equality rules (Task 18.3.5, user decisions 2026-10-07):**

* `=` assigns as a statement, but compares inside an `if`, `while` or `else if` condition
  (VB-style readability): `if x = 2` is `if x == 2`. Named arguments still win:
  `if f(x = 2)` passes `x`
* `==` compares values. Across types it uses a small fixed table, and nothing else:
  * a number equals text holding that number - `2 == "2"`, `2.5 == "2.5"`, `2 == "2.0"`;
    text that isn't a number is simply unequal (`2 == "two"` is false, no error)
  * a char equals a one-character string - `'a' == "a"`
  * int, float and double compare by value - `2 == 2.0`
  * never "truthiness": a bool only equals a bool. Any other mixed pair (bool and int,
    char and int, a struct and a number, ...) is a compile error
* `===` also requires the same type: `2 === 2.0` and `2 === "2"` are false. On two
  different types the answer is known when compiling, so the compiler warns that it is
  always false (both sides still run)
* `!=` is "not `==`" and `!==` is "not `===`", as in JavaScript
* A `bool` prints as `true` / `false` - in `print`, `{...}` interpolation and `format()` -
  while as a value it stays 1 / 0 in the generated C (Task 18.3.5b)
* Structs compare field by field with the same rules; two different struct types compare
  with `==` when they have the same field names in the same order (`===` needs the same
  struct). Arrays compare element by element and must have the same length
* Every comparison is generated per type - C's raw `==` is used only on plain numbers,
  chars and bools, never on strings, structs or arrays
`<` | Less than | `a < b`
`>` | Greater than | `a > b`
`<=` | Less than or equal to | `a <= b`
`>=` | Greater than or equal to | `a >= b`

---

#### Logical Operators

Operator | Description | Example
---|---|---
`and` | Logical AND | `a and b`
`or` | Logical OR | `a or b`
`not` | Logical NOT | `not a`
`&&` | Alternative AND | `a && b`
`||` | Alternative OR | `a || b`
`!` | Alternative NOT | `!a`

---

#### Bitwise Operators

Operator | Description | Example
---|---|---
`&` | Bitwise AND | `a & b`
`|` | Bitwise OR | `a | b`
`^` | Bitwise XOR | `a ^ b`
`~` | Bitwise NOT | `~a`
`<<` | Left shift | `a << 2`
`>>` | Right shift | `a >> 2`

---

#### Assignment Operators

Operator | Description | Example
---|---|---
`=` | Assignment | `a = 10`
`+=` | Add and assign | `a += 5`
`-=` | Subtract and assign | `a -= 5`
`*=` | Multiply and assign | `a *= 2`
`/=` | Divide and assign | `a /= 2`
`%=` | Modulo and assign | `a %= 3`

---

#### Special Operators

Operator | Description | Example
---|---|---
`.` | Member access | `object.property`
`?.` | Null guard (Task 30): not run on null, no error | `object?.method()`
`??` | Default when null (Task 30) | `object?.method() ?? default`
`? :` | Conditional operator (Task 30.7, built) | `(count > 5) ? "big" : "small"`
`[]` | Array/index access | `array[0]`
`?[]` | Null-guarded index (only with `[arrays] nullable = true`) | `array?[0]`
`()` | Function call / grouping | `function(args)`
`...` | Spread/variadic/range | `1...10`, `int... args`
`::` | Scope resolution | `Module::Class`
`:` | Lambda/type separator (default) | `int add(int x) : x + 1`
`->` | Lambda/type separator (alternative) | Reserved, alternative to `:`

---

### Operator Precedence

Description: Order of operations from highest to lowest priority.

Priority | Operators | Associativity
---|---|---
1 | `()`, `[]`, `.`, `?.` | Left-to-right
2 | `**` | Right-to-left
3 | `~`, `!`, `not`, unary `-`, unary `+` | Right-to-left
4 | `*`, `/`, `%` | Left-to-right
5 | `+`, `-` | Left-to-right
6 | `<<`, `>>` | Left-to-right
7 | `<`, `<=`, `>`, `>=` | Left-to-right
8 | `==`, `!=`, `<>` | Left-to-right
9 | `&` | Left-to-right
10 | `^` | Left-to-right
11 | `|` | Left-to-right
12 | `and`, `&&` | Left-to-right
13 | `or`, `||` | Left-to-right
14 | `??` | Left-to-right
15 | `? :` (conditional) | Right-to-left
16 | `=`, `+=`, `-=`, `*=`, `/=`, `%=` | Right-to-left

**Use parentheses for clarity**: When in doubt, use `()` to make order explicit.

---

## Language Features Summary

**Status:** [DESIGN] a summary of the whole design, built and not built

One file showing all of it, each feature tagged built / designed / idea / rejected:
`files/showcase/Fusion_showcase.fusion` (with its `fusion.toml`).

Description: Comprehensive overview of Fusion's capabilities and design decisions.

---

### Syntax Features

* **Function Declaration**: `<returnType> function name(<type> param = defaultValue)`
* **Variable Declaration**: `type name = value` or `var name = value`
* **Constructor**: `constructor(type param)` - explicit keyword
* **Loop Endings**: `end loop` with optional safety checks
* **No Semicolons**: Line breaks end statements
* **Flexible Blocks**: Indentation-based or braces (user preference)
* **Named Parameters**: `function(param2 = value, param1 = value)`
* **Default Parameters**: Optional parameter values
* **Enums**: Three syntax styles (braces, indentation, single-line)
* **Comments**: `//` and `/* */`; `'` (VB style) is off so `'c'` works - maybe only at a line's start later
* **Regions**: `#Region` / `#End Region` for code organization
* **Comparison Operators**: Both `!=` and `<>` for not-equal
* **Spread Operator**: `...` for variadic, range, and array spread

---

### Enumerations

* **Multiple Syntaxes**: Braces, indentation, or single-line
* **Custom Values**: Integer values for enum constants
* **Type Safety**: Cannot assign int directly to enum
* **Built-in Methods**: `toString()`, `values()`, `fromString()`
* **Usage**: In switch/match statements, comparisons

---

### The `...` Operator

* **Range in Loops**: `for i in 1...100`
* **Variadic Functions**: `int function sum(int... numbers)`
* **Array Spread**: `[...arr1, ...arr2]`
* **Rest Parameters**: `function log(string level, string... messages)`
* **Can Be Disabled**: In strict mode if needed

---

### Type System

* **Value Types**: Never null (int, float, bool, char, struct)
* **Reference Types**: class objects and enums can be null; strings, arrays, Lists and Maps never are (D.050)
* **No Nullable Value Types**: Syntax like `int?` does not exist
* **Explicit Null Checks**: `object?.null` or `object is null`
* **String Implementation**: values, changed in place (`s[i] = c`); `const string` never changes; pooling and copy-on-write postponed (Task 38)
* **Type Casting**: an int is used as a float only when it fits exactly (D.060); other conversions by function (`toInt`, `toFloat`, ...)
* **Default Values**: All types have defaults (0, false, "", null)
* **Enums**: Type-safe enumeration values

---

### Static Members and Constants

* **Static Methods**: Belong to class, not instance
* **Static Fields**: Shared across all instances
* **Constants**: Automatically static (no instance constants)
* **Access**: Via `ClassName.memberName`
* **Visibility**: Can be public or private

---

### Array Safe Navigation

* **Never null by default**: arrays, lists, maps and strings are empty, not null
* **With `nullable = true`**: `array?.length` is -1 on null, `array?[0]` is null
* Task 30, planned - `files/Nullable_Values.md`

---

### Error Handling

* **Multiple Return Values**: `result, err = function()`
* **Optional Error Capture**: `result = function()` (error bubbles up)
* **Error Object**: Built-in with message, code, stack trace
* **Traditional Exceptions**: Available for unexpected errors
* **When to Use**: Multiple returns for expected, exceptions for unexpected

---

### Memory Management

* **Default**: OWNERSHIP - one owner, assigning moves, passing borrows (Task 48; D.013, D.027)
* **GC**: only when a project's `fusion.toml` chooses it, or one is made in code
* **MANUAL / unsafe**: raw pointers and `free` - memory, assembly and devices only

---

### Null Safety

* **Only class objects and enums can be null**; strings, arrays, lists, maps, structs and numbers
  never are (unless a `nullable` setting allows it)
* **Check**: `== null`, `=== null`, `is null`, `x?.null`; `!x?.null` = not null
* **Guard**: `object?.method()` - not run on null, no error, false in an `if`
* **Default**: `object?.method() ?? value`
* **Plain `.` on null**: NullError, caught with `catch`
* **Numbers as conditions**: `[conditions] numbers` = "positive" (default) / "nonzero" / "off"

---

### Autoboxing

* **Automatic Conversion**: Primitives become objects when needed
* **Method Calls**: `(42).toString()`, `(3.14).round(2)`
* **Autobox Classes**: Int, Long, Float, Double, Boolean, Char, Byte
* **Performance**: Compiler optimizes unnecessary boxing

---

### Properties

* **Auto-Properties**: `property Name: type { get; set; }`
* **Computed Properties**: Custom get/set with validation
* **Indexed Properties**: `property Items[int index]: type`
* **Indexed-Only**: Prevent array replacement, allow element access
* **Multi-Dimensional**: `property Cell[int x, int y]: type`

---

### Structures

* **Fields**: one generated constructor, `Point(3, 4)`, fields in declaration order; methods
  when `[structs] functions = true` (default off)
* **Value Semantics**: never null; copied today - with Task 48 a struct holding a List moves as
  a whole, and its fields are only borrowed (D.026)
* **Allowed Types**: primitives, strings, other structs, arrays, Lists and Maps
  (`[structs] holdCollections`, default on)
* **Objects**: a struct may hold one - null until set, shared when the struct is copied (D.097)
* **Not Allowed**: implementing an interface
* **Use Case**: Pure data containers for performance

---

### Threading and Concurrency

* **Services**: a value several threads use gets one writer - a service, written or temporary
  (Task 42, `files/Service.md`); `send` moves data to another thread; locks only as a last resort
* **Async/Await**: Built-in for I/O operations
* **Thread Interrupts**: Cooperative multitasking via loop checks
* **Philosophy**: "Share memory by communicating"

---

### Loops

* **Explicit Endings**: `end loop` marker
* **Safety Checks**: Manual, periodic, iteration limit, interrupt handling
* **Check Types**: `end loop with {count} check ...`
* **Automatic Protection**: Compiler adds infinite loop prevention
* **Resource Monitoring**: Adapts to system RAM/CPU
* **Thread Safety**: Interrupt handling built-in
* **Range Operator**: `for i in 1...100` with optional step
* **Configurable**: Per-project or per-loop settings

---

### Standard Library

* **File Formats**: txt, md, JSON, XML, CSV, YAML, ini
* **Programming Languages**: Compilers for Go, Fusion, Java, C, C++, VB.NET, JS, HTML, CSS
* **Image Formats**: BMP, JPEG, GIF, PNG readers/writers
* **Binary Formats**: DOC, Excel, PDF, ZIP support
* **Custom Formats**: Framework for defining new formats
* **Localization**: Multi-language support (English, Japanese, etc.)
* **Collections**: List, Dictionary, Set, Queue, Stack
* **Math**: Vector, Matrix, Quaternion libraries
* **Networking**: HTTP, WebSocket, TCP/UDP
* **Graphics**: 2D and 3D rendering primitives
* **Audio**: Sound playback and synthesis

---

### Modules

* **Organization**: a folder is a module; `namespace A.B` groups modules
* **Import Syntax**: `import money`, `import money.round`, `import money.*`
* **Visibility**: `public` / `internal` / `private` (D.007, D.008)
* **Nested Classes**: Allowed within class file

---

### Compilation

* **Script Mode**: Run directly without compilation
* **Executable**: Native binary compilation
* **Library**: DLL/shared library for reuse
* **JIT Mode**: Just-in-time compilation
* **Cross-Platform**: Linux, Windows, macOS, WebAssembly

---

### From Parent Languages

* **From C**: Performance, structs, memory control, operators
* **From Java**: Strong typing, interfaces, generics, OOP structure
* **From Python**: Simple syntax, indentation, easy to read
* **From VB.NET**: Readable keywords, properties, explicit intent
* **From Go**: Message passing, channels, multiple returns, goroutines

---

### Unique to Fusion

* **Return-Type-First**: Clear function signatures
* **Value/Reference Distinction**: Explicit null safety
* **Flexible Block Syntax**: Indentation or braces (user preference)
* **Three Enum Syntaxes**: Braces, indentation, or single-line
* **Dual Comment Styles**: Both `//` and `'` supported
* **Loop Safety Checks**: Multiple check types with automatic protection
* **Indexed Properties**: Enhanced array access
* **Error Bubbling**: Optional error capture with multiple returns
* **Three-Tier Memory**: GC, smart pointers, or raw
* **Script or Compile**: Choose execution mode
* **`...` Operator**: Multi-purpose (range, spread, variadic)
* **`<>` Comparison**: Alternative to `!=` for not-equal
* **Automatic Locking**: Try-with-resources prevents deadlocks
* **Weak Pointers Discouraged**: Error in strict mode
* **Constants Auto-Static**: No instance constants
* **Comprehensive Standard Library**: Built-in support for 20+ file formats
* **Programming Language Support**: Built-in compilers for 9 languages
* **IDE Integration**: Threading visualization, code regions
* **Main Function**: `void function main(string... args)` as application entry point

---

## Language Comparison

**Status:** [DESIGN] how the design compares with other languages

Description: How Fusion compares to its parent languages across key features.

---

### Syntax and Structure Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Function Syntax** | `int add(int a)` | `int add(int a)` | `def add(a):` | `Function Add(a) As Integer` | `func add(a int) int` | `int function add(int a)`
**Return Type** | Before name | Before name | None/hints | After name | After params | **Before name**
**Block Style** | Braces `{}` | Braces `{}` | Indentation | Keywords | Braces `{}` | **Both** (user choice)
**Semicolons** | Required | Required | Not used | Not used | Optional | **Not used**
**Type Inference** | No (C89), Yes (C11) | Limited (`var`) | Yes | Limited (`var`) | Yes | **Yes** (`var`)
**Null Safety** | No | Limited | No | Limited | No | **Yes** (built-in)
**Comments** | `//` `/* */` | `//` `/* */` | `#` | `'` `REM` | `//` `/* */` | **`//` `'` `/* */`**
**Main Entry** | `int main()` | `void main()` | N/A (script) | `Sub Main()` | `func main()` | **`void function main(string... args)`**

---

### Type System Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Static Typing** | Yes | Yes | No (dynamic) | Yes | Yes | **Yes**
**Type Inference** | Limited | Limited | N/A | Limited | Yes | **Yes**
**Nullable Types** | All (pointers) | Objects only | All | Limited | Pointers only | **Objects only**
**Value Types** | Structs | Primitives | N/A | Structures | Structs | **Primitives + Structs**
**String Type** | `char*` | `String` (object) | `str` | `String` | `string` | **`string` (value type, freed automatically)**
**Generics** | No | Yes | No | Yes | Yes | **Yes**
**Auto-boxing** | No | Yes | N/A | Yes | No | **Yes**

---

### Memory Management Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Manual Memory** | malloc/free | No | No | No | No | **Yes (unsafe mode)**
**Garbage Collection** | No | Yes | Yes | Yes | Yes | **Yes (tier 1)**
**Smart Pointers** | No (C++11) | No | No | No | No | **Yes (tier 2)**
**Raw Pointers** | Yes | No | No | No | Yes | **Yes (unsafe only)**
**Memory Safety** | No | Yes | Yes | Yes | Mostly | **Yes (3 tiers)**
**RAII** | No (C++ only) | No | No | No | Defer | **Yes (using)**

---

### Concurrency Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Threading** | pthreads | Threads | Threads | Threads | Goroutines | **Threads + Goroutines**
**Channels** | No | No | queue.Queue | No | Yes | **Yes (Go-style)**
**Message Passing** | No | Limited | queue | No | Yes | **Yes**
**Shared Memory** | Yes | Yes | Limited (GIL) | Yes | Yes | **Yes (with locks)**
**Async/Await** | No | No | Yes | Yes | No | **Yes**
**Race Detection** | No | No | No | No | Yes | **Yes (built-in)**
**Auto-locking** | No | No | No | No | No | **Yes (try-with)**

---

### Error Handling Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Exceptions** | No | Yes | Yes | Yes | No | **Yes**
**Multiple Returns** | No | No | Yes (tuples) | No | Yes | **Yes (Go-style)**
**Error Type** | int codes | Exception | Exception | Exception | error | **Error object**
**Try-Catch** | No | Yes | Yes | Yes | No | **Yes**
**Error Bubbling** | No | Yes | Yes | Yes | No | **Yes (optional)**
**Checked Exceptions** | No | Yes | No | No | No | **No**

---

### Object-Oriented Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Classes** | No (structs) | Yes | Yes | Yes | No | **Yes**
**Inheritance** | No | Single | Multiple | Single | No | **Single**
**Interfaces** | No | Yes | Protocols | Yes | Yes | **Yes**
**Properties** | No | No (getters) | Yes | Yes | No | **Yes (VB-style)**
**Constructors** | No | Yes | `__init__` | `New` | No | **Yes (`constructor`)**
**Static Members** | No | Yes | Class vars | Yes | No | **Yes**
**Access Modifiers** | No | Yes | Convention | Yes | Capitalization | **Yes (public/private)**

---

### Advanced Features Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Enums** | Yes (int) | Yes | Enum class | Yes | iota | **Yes (3 styles)**
**Pattern Matching** | No | Limited | Yes (3.10+) | No | No | **Yes (match)**
**Lambdas** | No | Yes | Yes | Yes | Yes | **Yes**
**Closures** | No | Limited | Yes | Yes | Yes | **Yes**
**Operator Overload** | No (C++ only) | No | Yes | Yes | No | **Yes**
**Reflection** | No | Yes | Yes | Yes | Limited | **Yes**
**Annotations** | No | Yes | Decorators | Attributes | No | **Yes (custom)**

---

### Standard Library Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Collections** | Limited | Extensive | Extensive | Extensive | Limited | **Extensive (20 modules)**
**File I/O** | Basic | Good | Excellent | Good | Good | **Excellent**
**Networking** | Sockets | Good | Excellent | Good | Excellent | **Excellent**
**JSON** | No (libs) | Yes | Yes | Yes | Yes | **Yes (built-in)**
**XML** | No (libs) | Yes | Yes | Yes | No | **Yes (built-in)**
**HTTP** | No (libs) | Limited | Yes | Limited | Yes | **Yes (built-in)**
**Graphics** | No (libs) | Limited | Yes (libs) | Yes | No | **Yes (built-in)**
**Audio** | No (libs) | Limited | Yes (libs) | Yes | No | **Yes (built-in)**
**Crypto** | No (libs) | Yes | Yes (libs) | Yes | No | **Yes (built-in)**
**Database** | No (libs) | JDBC | Yes (libs) | ADO.NET | database/sql | **Yes (built-in ORM)**
**Web Server** | No (libs) | Limited | Yes (Flask/Django) | ASP.NET | net/http | **Yes (built-in)**
**AI/ML** | No (libs) | Limited | Excellent (libs) | ML.NET | No | **Yes (built-in)**
**Multi-language** | No | No | No | No | No | **Yes (10 languages)**

---

### Build and Execution Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Compilation** | Native | Bytecode | Bytecode | IL/Native | Native | **Native/Bytecode/JIT**
**Script Mode** | No | No | Yes | No | No | **Yes**
**Execution Speed** | Fastest | Fast | Slow | Fast | Fast | **Fast**
**Compile Time** | Slow | Medium | N/A | Medium | Fast | **Medium**
**Cross-Platform** | Yes (recompile) | Yes (JVM) | Yes | Limited | Yes (recompile) | **Yes (recompile)**
**Binary Size** | Small | Large (JVM) | Large | Medium | Medium | **Medium**
**Startup Time** | Instant | Slow (JVM) | Medium | Medium | Instant | **Fast**

---

### Safety and Security Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Memory Safety** | No | Yes | Yes | Yes | Mostly | **Yes (3 modes)**
**Type Safety** | Weak | Strong | Dynamic | Strong | Strong | **Strong**
**Null Safety** | No | Limited | No | Limited | No | **Yes (built-in)**
**Buffer Overflow** | Vulnerable | Protected | Protected | Protected | Protected | **Protected**
**Safety Modes** | No | No | No | No | No | **Yes (3 levels)**
**Strict Mode** | No | No | No | No | No | **Yes**
**Unsafe Mode** | Default | No | No | No | unsafe | **Yes (explicit)**

---

### Unique Language Features Summary

Feature | Availability
---|---
**Return-type-first syntax** | Fusion only
**Dual comment styles (// and ')** | Fusion only (VB has ')
**Three enum syntaxes** | Fusion only
**Flexible blocks (indent or braces)** | Fusion only
**Three-tier memory (GC/Smart/Raw)** | Fusion only
**Automatic loop protection** | Fusion only
**Try-with-resources auto-locking** | Fusion only (Java has try-with, Fusion adds locking)
**Built-in language compilers** | Fusion only
**20+ file format support** | Fusion only
**Script or compile mode** | Fusion + Python
**Indexed properties** | Fusion + VB.NET
**Multiple return values** | Fusion + Go + Python
**Channels** | Fusion + Go
**Message passing concurrency** | Fusion + Go
**`...` operator (multi-purpose)** | Fusion only (others have parts)
**Main function syntax** | Unique: `void function main(string... args)`

---

### Language Philosophy Comparison

Language | Primary Focus | Strengths | Weaknesses
---|---|---|---
**C** | Performance, low-level control | Fast, small binaries, hardware access | Unsafe, manual memory, no OOP
**Java** | Enterprise, portability | Strong ecosystem, JVM, garbage collection | Verbose, slow startup, memory heavy
**Python** | Simplicity, productivity | Easy to learn, extensive libraries, rapid dev | Slow execution, GIL limits threading
**VB.NET** | Readability, RAD | Natural language syntax, quick UI dev | Windows-focused, less popular
**Go** | Simplicity, concurrency | Fast compilation, goroutines, simple | No generics (old), limited OOP
**Fusion** | **All of the above** | Combines best features, flexible, comprehensive | New (unproven), learning curve

---

### Fusion's Advantage

**Fusion combines**:
* ✓ C's performance and memory control
* ✓ Java's strong typing and OOP structure
* ✓ Python's simplicity and ease of learning
* ✓ VB.NET's readability and natural syntax
* ✓ Go's concurrency model and efficiency

**Plus unique features**:
* ✓ Three safety modes (standard, strict, unsafe)
* ✓ Flexible syntax (choose your style)
* ✓ Built-in language compilers
* ✓ Comprehensive standard library
* ✓ Script or compile execution
* ✓ Superior error handling (exceptions + multiple returns)

**Result**: A modern, flexible, safe, and powerful language suitable for any application domain.

