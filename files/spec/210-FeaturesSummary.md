[< 200 ReservedWords](200-ReservedWords.md) | [Index](index.md) | [220 Comparison >](220-Comparison.md) <!-- nav -->

# 210 Features Summary

**Contents**

- [Syntax Features](#syntax-features)
- [Enumerations](#enumerations)
- [The `...` Operator](#the--operator)
- [Type System](#type-system)
- [Static Members and Constants](#static-members-and-constants)
- [Array Safe Navigation](#array-safe-navigation)
- [Error Handling](#error-handling)
- [Memory Management](#memory-management)
- [Null Safety](#null-safety)
- [Autoboxing](#autoboxing)
- [Properties](#properties)
- [Structures](#structures)
- [Threading and Concurrency](#threading-and-concurrency)
- [Loops](#loops)
- [Standard Library](#standard-library)
- [Modules](#modules)
- [Compilation](#compilation)
- [From Parent Languages](#from-parent-languages)
- [Unique to Fusion](#unique-to-fusion)

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
* Task 30 - `files/Nullable_Values.md`

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
* **Value Semantics**: never null; a struct of plain values is copied; one holding a List, Map or
  object moves as a whole (Task 48, built), and its fields are only borrowed (D.026)
* **Allowed Types**: primitives, strings, other structs, arrays, Lists and Maps
  (`[structs] holdCollections`, default on)
* **Objects**: a struct may hold one - null until set, shared when the struct is copied (D.097)
* **Not Allowed**: implementing an interface
* **Use Case**: Pure data containers for performance

---

### Threading and Concurrency

* **Services**: a value several threads use gets one writer - a service, written or temporary
  (Task 42, `files/Service.md`); `send` moves data to another thread; locks only as a last resort
* **Services first** ([100 Concurrency](100-Concurrency.md)); mutex and the other locks for other
  languages - off by default, inside `unsafe`, unlocked at the end of their scope (D.125, D.133)
* **Async/Await**: both forms - `async` at a call, and `async function` + `await` (D.127 proposed)
* **Interrupts**: only from the OS, passed down to every thread; checked after a loop pass or by the
  service's handler (D.132 proposed)

---

### Loops

* **Explicit Endings**: `end loop` marker
* **Safety Checks**: Manual, periodic, iteration limit, interrupt handling
* **Check Types**: `end loop with {count} check ...`
* **Automatic Protection**: Compiler adds infinite loop prevention - to settle in Task 56
* **Resource Monitoring**: Adapts to system RAM/CPU - not decided (56.1)
* **Thread Safety**: Interrupt handling built-in
* **Range Operator**: `for i in 1...100` with optional step
* **Configurable**: Per-project or per-loop settings

---

### Standard Library

* **File Formats**: txt, md, JSON, XML, CSV, YAML, ini
* **Programming Languages**: language modules `Lang.<language>.<optional flavour>.Fusion` (Task 49, D.137)
* **Image Formats**: BMP, JPEG, GIF, PNG readers/writers
* **Binary Formats**: DOC, Excel, PDF, ZIP support
* **Custom Formats**: Framework for defining new formats
* **Localization**: Multi-language support (English, Japanese, etc.)
* **Collections**: List, Map (alias Dictionary) built; Set, Queue, Stack (43.4)
* **Math**: Vector, Matrix, Quaternion libraries
* **Networking**: HTTP, WebSocket, TCP/UDP
* **Graphics**: 2D and 3D rendering primitives
* **Audio**: Sound playback and synthesis

---

### Modules

* **Organization** (built): a folder is a module; `namespace A.B` groups modules
* **Direction** (D.136, Task 57): a namespace is a supplier's group of modules; `Namespace.Module.Name`
* **Import Syntax**: `import money`, `import money.round`, `import money.*`
* **Visibility**: `public` / `internal` / `private` (D.007, D.008)
* **Nested Classes**: not decided; a file may hold many classes (D.135)

---

### Compilation

* **Script Mode**: Run directly without compilation (design)
* **Executable**: Native binary compilation
* **Library**: DLL/shared library for reuse
* **JIT Mode**: Just-in-time compilation (design)
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
* **Dual Comment Styles**: `//` built; `'` postponed (SYN.031)
* **Loop Safety Checks**: Multiple check types with automatic protection
* **Indexed Properties**: Enhanced array access
* **Error Bubbling**: Optional error capture with multiple returns
* **Memory**: OWNERSHIP first (D.027); GC or manual only where a project chooses; unsafe memory
  freed at the end of its scope (D.134)
* **Script or Compile**: Choose execution mode
* **`...` Operator**: Multi-purpose (range, spread, variadic)
* **`<>` Comparison**: Alternative to `!=` for not-equal
* **Services instead of locks**: a shared resource becomes a service - no data races, deadlocks
  prevented by rules (Task 42)
* **Weak Pointers Discouraged**: Error in strict mode
* **Constants Auto-Static**: No instance constants
* **Comprehensive Standard Library**: Built-in support for 20+ file formats
* **Programming Language Support**: language modules (Task 49)
* **IDE Integration**: Threading visualization, code regions
* **Main Function**: `void function main(string... args)` as application entry point

[< 200 ReservedWords](200-ReservedWords.md) | [Index](index.md) | [220 Comparison >](220-Comparison.md) <!-- nav -->
