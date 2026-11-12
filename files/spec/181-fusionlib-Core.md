[< 180 StandardLibrary](180-StandardLibrary.md) | [Index](index.md) | [182 fusionlib-Extended >](182-fusionlib-Extended.md) <!-- nav -->

# 181 fusionlib Core

Contents: [Core Libraries (Essential)](#core-libraries-essential) | [Core Module (fusionlib.Core)](#core-module-fusionlibcore) | [Math Module (fusionlib.Math)](#math-module-fusionlibmath) | [Collections Module (fusionlib.Collections)](#collections-module-fusionlibcollections) | [Threading Module (fusionlib.Threading)](#threading-module-fusionlibthreading) | [IO Module (fusionlib.IO)](#io-module-fusionlibio)

## Fusion Standard Library (fusionlib)

**Status:** [DESIGN] the planned library modules - designed one at a time in Task 43 (43.6: every
module's name first). Fusion's own libraries are the `Fusion` namespace (D.136, Task 57): `import Fusion.IO`

Description: Complete standard library with 21 modules organized in three tiers for clarity and ease of learning.

**Total**: 21 modules covering all application domains
* **Core Libraries** (5 modules): Essential functionality used in most programs
* **Additional Libraries** (12 modules): Domain-specific features for specialized applications
* **IDE & Development Libraries** (4 modules): Tools for development, testing, debugging, and documentation

**Import Syntax**: `import Fusion.<ModuleName>` (`fusionlib.<ModuleName>` was the earlier name - Task 57 settles it)

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

**Implemented today** (the full string reference: [032 Strings](032-Strings.md)):
- A variable name, or a struct field path such as `{player.name}` or `{p.x}` (Task 18.2.1)
- Full expressions inside `{...}` (like `{age + 1}` above) are not implemented yet
- A whole array or struct can't be printed - print its elements or fields
- An interpolated string is an ordinary string value anywhere - `string s = "x is {x}"`,
  `return "Hi {name}"`, `f("{a}-{b}")` (Task 18.3.3)
- `format(text, args...)` returns the text `print` would write, with the same `{@N}` rules; `{@N}`
  placeholders only work in the text given to `print` or `format`

**A literal brace** (Task 28.1.5):
- `\{` and `\}` - `print("\{name\} is {name}")` prints `{name} is Alice`
- A `{` on its own always starts an interpolation; one not followed by a name or `@N` is an error,
  never silently printed as text

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
* Map<K,V> (hash map, key-value pairs; `Dictionary<K,V>` is the same type)
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

Services are Fusion's primary way ([100 Concurrency](100-Concurrency.md)); the primitives below are for
other languages and the `Lang` modules: locks off by default, inside `unsafe` (D.125 proposed), unlocked at
the end of their scope (D.133); thread-local storage only in `unsafe` (D.130 proposed).

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

[< 180 StandardLibrary](180-StandardLibrary.md) | [Index](index.md) | [182 fusionlib-Extended >](182-fusionlib-Extended.md) <!-- nav -->
