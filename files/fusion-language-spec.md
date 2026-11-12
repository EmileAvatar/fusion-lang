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

## Null Handling, Autoboxing, Memory Management

Moved to `files/spec/` (Task 51.5): `080-Null.md`, `081-Autoboxing.md`, `090-Memory.md`.

---

## Threading and Concurrency Model, Generics and Templates, Error Handling

Moved to `files/spec/` (Task 51.5): `100-Concurrency.md`, `110-Generics.md`, `120-Errors.md`.

---

## Comments and Code Organization

Moved to `files/spec/130-Comments.md` (Task 51.5).

---

## Async and Concurrency

Moved to `files/spec/100-Concurrency.md` (Task 51.5), with the threading model.

---

## Collections (as built)

Moved to `files/spec/140-Collections.md` (Task 51.5).

---

## Module System, Complete Game Example, Build and Compilation

Moved to `files/spec/` (Task 51.5): `150-Modules.md`, `160-GameExample.md`, `170-Build.md`.

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

Moved to `files/spec/131-AutoDocs.md` (Task 51.5). What follows here - document formats, a custom
format creator, localization and library notes - belongs to the standard library (180).

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

