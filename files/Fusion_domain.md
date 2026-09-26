# Fusion Domain Hierarchy

**Purpose:** A visual map of Fusion's full feature domain - everything the language
supports today, is planned to support, and may eventually support - organized by what a
programmer writing Fusion code actually thinks in terms of (types, control flow, memory,
OOP, concurrency, standard library), not by compiler internals.

**How to read this document:** this is a feature *map*, not a build tracker. It does not
mark items as implemented/planned/aspirational - that level of engineering detail lives
elsewhere and changes far more often than the shape of the language itself:
- **`../taskSummary2.md`** - what's actually built, tested, and in progress right now
- **`FutureFeatures.md`** (repo root) - detailed proposals, tradeoffs, and open questions
  for individual features (e.g. the `decimal`/`Currency` numeric types, the Currency
  Module, IDE tooling, cross-language compilation)

Some branches below exist in the compiler today; some are written designs waiting to be
built; some are long-term ideas with no design work done yet. That's deliberate - Fusion's
whole premise is that a project only takes on the parts of this tree it actually needs (see
"Configuration Philosophy" and the example profiles at the end), so the full tree is worth
seeing as one shape rather than as a status report.

---

## 1. Project Configuration

The entry point that decides which parts of the rest of this tree apply to a given project.

```
Project Configuration (fusion.toml)
├── Syntax Style
│   ├── Block style (indentation / braces / End keywords)
│   ├── Indentation width, mixed tabs/spaces policy
│   └── Statement terminators (newline-only today; optional semicolons proposed)
├── Safety Mode
│   └── normal | strict (strict mode rules still being defined feature-by-feature)
├── Numeric Defaults
│   ├── Default decimal precision/scale
│   └── Default Currency precision/scale (per-project, e.g. JPY vs USD conventions)
├── Feature Selection
│   └── Which language capabilities this project turns on - see Section 8
│       (Abstraction) for why this matters most there
└── Backend Target
    └── c | llvm | vm | native | wasm (only "c" exists as a real target today)
```

---

## 2. Syntax & Style

```
Syntax & Style
├── Block Styles (all three are fully interchangeable, chosen per-file or per-project)
│   ├── Indentation (Python-style)
│   ├── Braces (C/Java-style)
│   └── End keywords (VB.NET-style)
├── Function Declaration
│   ├── Return-type-first syntax
│   └── Inline lambda body (`: expression`)
├── String Interpolation
│   ├── Inline (`{variable}`)
│   └── Positional (`{@1}`, `{@2}`, ...)
├── Comments
│   ├── Line (`//`) and block (`/* */`)
│   └── Single-quote line comments (conflicts with char literals - unresolved)
└── Grouped/Multi-line Constructs
    ├── Grouped import blocks (Go-style `import ( ... )`)
    └── Multi-line function parameters with inline documentation comments
```

---

## 3. Type System

```
Type System
├── Primitive Types
│   ├── Integer
│   │   ├── Signed: int8, int16, int32 (int), int64 (long), int128
│   │   └── Unsigned: byte, uint16, uint32, uint64, uint128
│   ├── Floating Point
│   │   └── float16, float32 (float), float64 (double)
│   ├── Exact / Decimal
│   │   ├── decimal(precision, scale) - fixed-point, exact arithmetic
│   │   └── Arbitrary-precision decimal (a distinct future extension of the same family,
│   │         not a second type built from scratch)
│   ├── Text
│   │   └── char, string
│   └── Other
│       └── bool, void
│
├── Composite Types
│   ├── Arrays - `type[]` (inferred size) / `type[N]` (fixed size)
│   ├── Advanced array mutability - `type[]`, `type[N]`, `type()`, `type(N)`
│   │     (independent mutable/resizable axes)
│   ├── List, Map, Set, Tuple, Queue, Stack (fusionlib.Collections)
│   ├── Struct, Enum, Union
│   └── Nullable / Optional
│
├── Financial / Money-Precision Types
│   ├── Currency - convenience sugar over `decimal`, defaults to a COBOL-equivalent
│   │     shape (`PIC 9(9)V99`), fully overridable per declaration: `Currency(p, s)`
│   ├── Rounding modes (banker's / round-half-away-from-zero) - project-configurable
│   └── Currency Module (fusionlib) - conversion, exchange rates, locale-aware formatting,
│         built on top of `decimal`/`Currency`, not inside the type itself
│
└── Type Relationships
    ├── Type inference
    ├── Implicit numeric promotion (int -> float)
    ├── Explicit casts (required between decimal/Currency and float/double)
    ├── Type aliases
    └── Generic types & type constraints
```

---

## 4. Variables & Constants

```
Variables & Constants
├── Variable declaration (explicit type)
├── const declaration (must initialize, enforced immutable)
└── Scoping
    └── Block-level (lexical) scoping - a variable is only visible inside the block
          ({ }, if/while/for) it's declared in; nested blocks may shadow outer names
```

---

## 5. Functions

```
Functions
├── Named functions (return-type-first)
├── Inline lambda bodies (`: expr`)
├── Anonymous functions / closures
├── Parameters
│   ├── Default values
│   ├── Named parameters
│   └── Variadic parameters
├── Overloading
├── Higher-order functions
└── Function references / delegates / callbacks
```

---

## 6. Control Flow

```
Control Flow
├── Branching
│   ├── if / else if / else
│   └── switch / match (pattern matching)
├── Loops
│   ├── while
│   ├── for (with range())
│   ├── foreach
│   └── break / continue
├── Guard conditions
└── Early exit
    └── return
```

---

## 7. Error Handling

```
Error Handling
├── try / catch / finally / throw / Error
├── Result-style return values (explicit success/failure, no exceptions)
├── Nullable/optional as an error-avoidance mechanism
└── Panics for unrecoverable conditions
```

---

## 8. Abstraction & Object Model

**Configuration philosophy for this domain specifically:** Fusion supports classical
inheritance, interfaces, traits, and composition **all at once**, as independent,
combinable capabilities - not a forced choice between OOP philosophies. A project
configures which of these it wants: one, several, or all of them together, and they are
designed to interoperate rather than compete (a `class` can implement an `interface`,
mix in a `trait`, and still favor composition for the rest of its design, all in the same
project). This is a deliberate design decision, not an accident of which keywords got
reserved early - see Section 1's Feature Selection.

```
Abstraction & Object Model
├── class
│   ├── Fields, properties (get/set)
│   ├── Constructors
│   └── static vs instance members
├── struct (value-type alternative to class)
├── interface (contract - what a type promises)
├── trait (reusable behavior - what a type gets for free)
├── inheritance (class hierarchies)
├── composition (has-a relationships, favored as an inheritance alternative)
├── enum, union
├── Generics
│   ├── Generic types and functions
│   └── Type constraints
└── Access modifiers
    └── public, private, protected, static, virtual, override, abstract, sealed
```

---

## 9. Memory Model

```
Memory Model
├── Unique<T>  - single ownership, move-only
│     (plain assignment is a compile error; ownership transfer requires explicit .move())
├── Shared<T>  - reference-counted, multiple owners
│     (refcounting is always atomic; no automatic cycle detection - Weak<T> breaks cycles)
├── Weak<T>    - non-owning reference to a Shared<T>
│     (.lock() returns a nullable value - never a silent crash on a dead reference)
└── Automatic memory management (default tier - no explicit annotation needed)

Possible future direction (not currently planned): borrow-checking / lifetime analysis
(Rust-style). This would be a substantial extension beyond the three-tier model above,
not an incremental addition to it.
```

---

## 10. Concurrency

```
Concurrency
├── Threads
├── Goroutine-style lightweight tasks (go)
├── async / await
├── Channels
├── Mutex / synchronization primitives
└── Atomic operations
```

---

## 11. Code Organisation

```
Code Organisation
├── Modules
├── import (single and grouped-block forms)
├── Namespaces / packages
└── Visibility
    └── public, private, protected, internal
```

---

## 12. Metaprogramming & Reflection

```
Metaprogramming & Reflection
├── Runtime type inspection (fusionlib.Reflection)
├── Attributes / annotations
├── Compile-time evaluation
└── Code generation from templates
```

---

## 13. Interoperability & Hardware

```
Interoperability & Hardware
├── Cross-Language Compilation (fusionlib.Lang)
│   ├── Parsing C, C++, Java, C#, Python, JavaScript, TypeScript, Go, Rust, VB.NET syntax
│   └── Optional semicolon statement terminators (for compatibility with those languages)
├── Foreign Function Interface / C ABI
└── HIDL - Hardware Interface Definition Language module
    ├── Consumes a separately-specified hardware description (registers, bitfields,
    │     access modes, timing, constraints) - HIDL itself is language-agnostic, not
    │     Fusion-specific
    └── Generates a safe, typed Fusion API from it (the "HIDL module" is Fusion's
          consumer of that description, not HIDL itself)
```

---

## 14. Standard Library (fusionlib)

```
fusionlib
├── Core            - Essential types, Console I/O, DateTime
├── Math            - Vector, Matrix, Quaternion, trigonometry
├── Collections     - List, Dictionary, Set, Queue, Stack, LINQ-style operations
├── Threading       - Threads, goroutines, channels, mutex, async/await
├── IO              - File operations, streams, compression
├── Net             - TCP/UDP, HTTP, WebSocket, DNS, email, FTP
├── Data            - JSON, CSV, XML, YAML, Markdown, INI
├── System          - Process management, DLL loading, environment
├── Lang            - Multi-language compilation (see Section 13)
├── Languages       - i18n/l10n, translations, locale
├── GUI             - Cross-platform UI
├── Graphics        - 2D/3D rendering, sprites, shaders
├── Audio           - Playback, synthesis, effects, MIDI
├── Crypto          - Encryption, hashing, SSL/TLS
├── Database        - SQL/NoSQL, ORM
├── Web             - HTTP server, REST API framework
├── AI              - Neural networks, ML algorithms
├── Reflection      - Runtime type inspection, dynamic execution
├── Test            - Unit testing framework, assertions, coverage
├── Diagnostics     - Profiling, logging, debugging
├── DocWiki         - Automatic documentation generation
├── IDE             - LSP, syntax highlighting, formatter, project/build settings
├── Currency        - FX conversion, exchange rates, locale-aware money formatting
├── Regex           - Full regex engine plus an optional fluent/builder API
└── (proposed, separate ecosystem packages, not core)
    ├── GameEngine, Physics, ECS, Shader tooling
    └── Numerics (NumPy-style), DataFrames (Pandas-style)
```

---

## 15. Developer Tooling

```
Developer Tooling
├── CLI Suite
│   └── fusion build / run / fmt / test / doc / vet / check / clean
├── IDE Integration
│   ├── Language Server Protocol (completion, go-to-definition, diagnostics)
│   ├── Syntax highlighting (VS Code, IntelliJ, Sublime, Vim, Emacs)
│   ├── Code formatter (converts between all three block styles)
│   └── Editor extensions (VS Code, IntelliJ, Sublime, Vim, Emacs)
└── Project Configuration
    └── fusion.toml (see Section 1)
```

---

## 16. Compilation Targets

```
Compilation Targets
├── C - Fusion -> C -> GCC/Clang -> native executable
├── LLVM - Fusion -> LLVM IR -> native executable (no C intermediate)
├── VM / Bytecode - Fusion -> bytecode -> interpreter or JIT
├── Native - direct machine code (x86-64, ARM64, RISC-V, ...)
└── Future targets - WebAssembly, GPU, embedded/bare-metal
```

---

## Example Configuration Profiles

These illustrate the point of Section 1's Feature Selection: the same language, shaped
differently per project, by turning parts of the tree above on or off.

```
"Financial" Profile
├── Types: int, long, decimal(p, s), Currency(p, s)
├── Numeric rules: exact decimal arithmetic, explicit precision/scale, deterministic
│     rounding, no implicit float conversion
├── Memory: automatic (Unique/Shared/Weak available, not required)
├── Error handling: Result-style values preferred over exceptions
└── Disabled: raw/unsafe memory, inline assembly

"Systems" Profile
├── Types: byte, char, int8-int64, uint8-uint64, float32
├── Memory: manual allocation, raw pointers, volatile memory
├── Interoperability: C ABI, inline assembly
└── Disabled: garbage collection, reflection

"Full OOP" Profile
├── Abstraction: class + interface + trait + inheritance + composition + generics,
│     all enabled together (Section 8's default philosophy)
├── Memory: automatic (Unique/Shared/Weak)
└── Error handling: try/catch/finally

"Embedded" Profile
├── Types: byte, fixed-width integers
├── Memory: manual allocation, raw pointers, packed structures, no heap
├── Error handling: none (no exceptions, no dynamic allocation to fail)
└── Disabled: garbage collection, reflection, dynamic dispatch
```

A project isn't limited to picking one named profile wholesale - profiles are a
convenient starting point; any individual feature can still be turned on or off on top of
one.

---

**Related documents:**
- `../taskSummary2.md` - active task tracking and current build status
- `FutureFeatures.md` (repo root) - detailed feature proposals and open design questions
- `fusion-language-spec.md` - the complete language specification
- `fusion.ebnf` - formal grammar
- `Fusion_Hardware_Interface_Definition_Language_HIDL.md` - full HIDL vision document
