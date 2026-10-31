# Fusion - Decisions

The single list of what Fusion is and what has been decided. Keep it small: one line per
feature, one row per decision. Only the **latest** decision on a subject is kept; an older
one is removed when replaced (its history is in git and the design document named). Language
features only - no bug fixes, no discussions.

- **Section 1** - every feature, one line each: `AREA.NNN [STATUS] description`
- **Section 2** - the decisions behind them, in a table; a clash between two is marked `CLASH`
  (none open - C.001-C.010 settled 2026-10-31: D.025-D.028, D.057, D.058, D.064, D.065, D.077, D.080)
- Status words: `[BUILT]` works today · `[PLANNED]` designed, not built · `[DESIGN]` to be
  designed · `[POSTPONED]` waits for something · `[REJECTED]` decided against
- Detail lives elsewhere: status `FEATURES.md`, what works `SYNTAX_REFERENCE.md`, settings
  `files/fusionSettings.xml`, design documents (named in each row)
- First version 2026-10-31; the full pass over every file, note and the code: FEATURES.md Task 49

---

## 1. Fusion - the goal and the features

#### GOL - the goal
GOL.001 [DESIGN] An agnostic language: each project chooses safety, memory model, concurrency and backend in `fusion.toml`
GOL.002 [BUILT] Compiles Fusion -> C -> a native program (GCC); the compiler is written in Python for now
GOL.003 [PLANNED] Self-hosting: the compiler written in Fusion compiles itself (Task 35); Python retired after
GOL.004 [DESIGN] A million requests on one machine: no data races by construction, no deadlocks, small footprint (Task 42)
GOL.005 [PLANNED] Memory-safe without a GC by default: one owner, moves, borrows (Task 48)
GOL.006 [BUILT] Features become settings - a safe default, switchable per project
GOL.007 [BUILT] A simple working language first, advanced features after
GOL.008 [BUILT] Never trust code - a library is checked by what its signature promises
GOL.009 [PLANNED] Rename before 1.0 (another language is called Fusion)
GOL.010 [BUILT] The self-hosting test run: lexer, parser, checker and C generator written in Fusion (Task 28)

#### SYN - syntax
SYN.001 [BUILT] Three block styles, one meaning: indentation, braces, keywords (`End if`)
SYN.002 [BUILT] `void function main()`; `int function f(int x)`; a one-line body after `:`
SYN.003 [BUILT] Default parameters and named arguments
SYN.004 [BUILT] Lambdas and function values
SYN.005 [BUILT] `if` / `while` / `for`; numbers as conditions (`if count`, a setting)
SYN.006 [BUILT] `(cond) ? a : b`
SYN.007 [BUILT] `match`, `fall match`, `match` as a value
SYN.008 [BUILT] `let` / `var`: the type comes from the value
SYN.009 [BUILT] A line break inside `( )` or `[ ]` continues the line
SYN.010 [BUILT] Equality `=`, `==`, `!=`, `===`, `!==`
SYN.011 [BUILT] Method form: `name.toUpper()` is `String.toUpper(name)`; your own functions too (`p.moved(1, 2)`)
SYN.012 [BUILT] `len` / `length`, with or without brackets
SYN.013 [BUILT] Form B: a set-up block right after a value, on any variable, field or static
SYN.014 [PLANNED] Duration literals `500ms`, `5s`, `2min` (42.16)
SYN.015 [REJECTED] An `I` prefix on interface names
SYN.016 [BUILT] Identifiers are ASCII; Trojan Source and look-alike letters are rejected
SYN.017 [BUILT] `_` for an unused `match` field
SYN.018 [DESIGN] `switch` as an alias of `match` (VB.NET); `elif` for `else if`
SYN.019 [DESIGN] `loop { }` - no break / return inside is a compile error; the keyword may be dropped
SYN.020 [DESIGN] `++` / `--` as statements only, never inside an expression
SYN.021 [DESIGN] `if` as a value; do-while
SYN.022 [DESIGN] Guards and ranges in match cases (`case x if x < 0`, `case 0...9`)
SYN.023 [DESIGN] `assert cond, "message"` - an AssertionError when false
SYN.024 [DESIGN] Type tests `if s is string`; `typeOf(x)` as text
SYN.025 [DESIGN] Extension methods (`extend string { }`); function overloading by parameter types
SYN.026 [DESIGN] Copy with changes (`a with { x = 5 }`); tuples
SYN.027 [DESIGN] Operands evaluated in one written order - today C's order (37.2)
SYN.028 [POSTPONED] Closures; named lambdas inside functions; multi-line lambda bodies
SYN.029 [BUILT] Comments `//` and `/* */`; `<>` as another way to write `!=`; hex, binary and octal numbers (`0xFF`)
SYN.030 [BUILT] `unchecked { }` - whole-number `+ - *` inside wrap around on purpose
SYN.031 [POSTPONED] `'` comments (VB style) - off so `'c'` works; maybe only at the start of a line
SYN.032 [DESIGN] `#Region` / `#End Region`; documentation comments; documentation written from them
SYN.033 [DESIGN] `loop { } end loop` with safety checks; loop labels; an iteration limit (`[safety] maxIterations`)
SYN.034 [DESIGN] The `...` operator: ranges `1...100`, variadic `int... numbers`, spread `[...a, ...b]` (`string... args` of main is built)
SYN.035 [DESIGN] `**` (power) - read by the lexer, not built; annotations `@name(...)`
SYN.036 [DESIGN] `'''` comment blocks; comment levels 0-5; coding hints
SYN.037 [DESIGN] Semicolons accepted; reading code written in other languages' syntax
SYN.038 [DESIGN] A minimum variable-name length in strict mode (default 3; loop counters and type parameters excepted)
SYN.039 [BUILT] `and`, `or`, `not`; a lambda as `func(int x) : x * 2`

#### TYP - types
TYP.001 [BUILT] int, float, double, bool, char, byte - overflow checked; `[numbers] overflowWrap` wraps
TYP.002 [PLANNED] `long`, `short` (47.1)
TYP.003 [PLANNED] `money`: a long of minor units, exact, never a float (47.2)
TYP.004 [BUILT] Enums; enums with data (tagged unions); an unset enum is null
TYP.005 [PLANNED] Enums whose values carry fixed data (47.3); the `FusionType` enum (47.4)
TYP.006 [PLANNED] `fixed(n)`: a maximum size, values may change - `fixed(10) string name`, `fixed(14) List<Person> people`, `fixed int numbers[10]` (47.5)
TYP.007 [PLANNED] Generics: the program's own generic functions and types (Task 33)
TYP.008 [DESIGN] Operator overloading - only for exceptional cases (a setting, off)
TYP.009 [BUILT] An int is used as a float only when it fits exactly (a written number that doesn't: compile error; a value: PrecisionError); `[numbers] autoWidening = true` widens with a warning
TYP.010 [DESIGN] Flag enums combined with `|` (`Permission.Read | Permission.Write`)
TYP.011 [BUILT] Conversions are functions: `toInt`, `toFloat`, `toString`, `toByte`, `parseInt`
TYP.012 [BUILT] Enum functions `values()`, `fromString()`; an enum prints its name
TYP.013 [DESIGN] Cast syntax `cast<T>(x)`; autoboxing (`(42).toString()`) - the type classes (`Int`, `String`) are built
TYP.014 [DESIGN] A `bit` type and bit-level operations
TYP.015 [DESIGN] `decimal(p, s)`: an exact fixed-point number - after `money` (47.2.3)

#### STR - strings
STR.001 [BUILT] Strings are values, freed automatically; changed in place (`s[i] = c`)
STR.002 [BUILT] Interpolation `"{x}"`, `{@N}` placeholders, `template string`
STR.003 [BUILT] Unicode: characters vs bytes; `bytes` for raw data
STR.004 [BUILT] The string library: search, extract, change, pad, number bases, format
STR.005 [POSTPONED] String pooling (29.4); secure strings (29.5); StringBuilder (Task 38)
STR.006 [REJECTED] A "mutable" switch - a string can always be changed in place
STR.007 [BUILT] An unchangeable string is `const string` - no new type
STR.008 [DESIGN] Raw strings `r"..."`; multi-line strings; a format inside `{value:pattern}`
STR.009 [POSTPONED] Full expressions inside `{...}`; full Unicode case and normalization; Base64 / URL / JSON escaping; regex
STR.010 [POSTPONED] Paged / memory-mapped strings

#### COL - arrays, Lists, Maps
COL.001 [BUILT] Fixed-size arrays, bounds always checked
COL.002 [PLANNED] Arrays know their length, grow and shrink at the end, `+`, `copyPart` (Task 45)
COL.003 [BUILT] `List<T>`, `Map<K, V>` (also `Dictionary`) - never null, just empty
COL.004 [BUILT] Lists and Maps are counted references; `byVal` copies, `byRef` shares
COL.005 [PLANNED] `foreach`; changing a collection inside it is an error (45.9)
COL.006 [PLANNED] A `Collection` interface - `foreach` on any class that implements it (32.4)
COL.007 [PLANNED] List / Map options in form B: no duplicates, no null, read only (32.14)
COL.008 [PLANNED] A Collections module: RingBuffer first (43.4)
COL.009 [BUILT] `toList`, `toCSV`
COL.010 [REJECTED] Turning off array bounds checks, even in unsafe mode
COL.011 [PLANNED] Lists: a capacity, a growth buffer, a kept sort order
COL.012 [PLANNED] Maps: `add(otherMap)`; a map may bring its own hashing and key rules
COL.013 [REJECTED] Changing a collection while looping over it (a setting to allow it) - build a new one
COL.014 [DESIGN] `Set<T>`; slices by range (`numbers[0...1]`); Map literals (`{"apples": 3}`)
COL.015 [POSTPONED] Multi-dimensional arrays
COL.016 [REJECTED] `type()` / `type(N)` arrays meaning read-only or fixed size - `const` and `fixed(n)` instead (D.064)

#### FUN - functions and errors
FUN.001 [BUILT] `T, Error function`: an error returned as the last value
FUN.002 [BUILT] `try` / `catch` / `finally` / `throw`; custom error types
FUN.003 [BUILT] `readonly` parameters: never changed, deeply - worked out through the calls
FUN.004 [PLANNED] `readonly` / `byVal` / `byRef` written at the call (48.3)
FUN.005 [PLANNED] Several return values per function beyond the Error (`[functions] multipleReturns`, off)
FUN.006 [BUILT] Files, program arguments, console input, `exit`, `run` (another program)
FUN.007 [BUILT] Endless recursion is a catchable StackOverflowError (`[safety] maxCallDepth`)
FUN.008 [BUILT] Wrapping on purpose: `wrapAdd`, `wrapSub`, `wrapMul`
FUN.009 [BUILT] `[errors] returns` / `exceptions` - both on by default
FUN.010 [DESIGN] `?` after a call returns its error at once; `await all([...])`
FUN.011 [DESIGN] `extern "C"` - call a C function by declaring it
FUN.012 [POSTPONED] More error types (Network, Timeout, Parse, Cancelled, Assertion, NotSupported) - with each feature
FUN.013 [DESIGN] Every error carries a stack trace
FUN.014 [BUILT] 96 built-in functions, 16 List and 7 Map methods, each with its `[stdlib]` layer - the list: files/Builtins.md (generated)
FUN.015 [BUILT] Built-in error types in a tree (IndexError, KeyError, FileError, OverflowError, NullError, ...) - a parent catches its children

#### NUL - null
NUL.001 [BUILT] Value types are never null; class objects and enums can be
NUL.002 [BUILT] A null without a check is a NullError a `catch` can handle; `null == null` is true
NUL.003 [PLANNED] `?.`, `?.null`, `??`, `case null` (Task 30.2)
NUL.004 [REJECTED] `T?` types - `?` goes on a variable (`x?.f()`), never on a type

#### STC - structs
STC.001 [BUILT] Structs: value types, copied, never null; may hold Lists, Maps, strings
STC.002 [BUILT] Methods on structs (`[structs] functions`, default off)
STC.003 [BUILT] A struct building on a struct (`implements` / `extends` / `includes`)
STC.004 [BUILT] A struct as text: `"{e}"` -> `name : "Jeff",age : 30`
STC.005 [REJECTED] A struct implementing an interface - a struct only holds values
STC.006 [PLANNED] A struct's fields are only borrowed, never moved out; the whole struct moves or is borrowed (Task 48)
STC.007 [DESIGN] Classes inside structs (a setting, off)

#### CLS - classes
CLS.001 [BUILT] Classes: objects by reference, counted, freed when the last holder goes
CLS.002 [BUILT] Several constructors; `this(...)`; `new` optional
CLS.003 [BUILT] Statics set up in three forms (A, B, C) before main
CLS.004 [BUILT] Visibility `private` (the class) / `internal` (the namespace) / `public`; `namespace A.B`
CLS.005 [BUILT] Printing an object gives its class name, with a warning (until ToString)
CLS.006 [PLANNED] Interfaces with `implements`; ToString, Default, Cloneable (32.5)
CLS.007 [PLANNED] Inheritance with `inherits` (alias `extends`); `typeOf(x)` gives the chain (32.7)
CLS.008 [PLANNED] `nocopy` / `noshare` fields
CLS.009 [POSTPONED] The builder pattern (after Task 32)
CLS.010 [BUILT] A warning for each circle of classes that could leak
CLS.011 [DESIGN] Properties: `property Name: type { get; set; }`, computed and indexed ones
CLS.012 [DESIGN] A constant in a class is always static
CLS.013 [DESIGN] `abstract`, `sealed`, `virtual`, `override`, `protected` - reserved words, for inheritance (32.7)

#### MOD - modules
MOD.001 [BUILT] Modules and `import` (a folder = a module); module variables and constants
MOD.002 [BUILT] `--interface`: the public interface of the imported modules
MOD.003 [POSTPONED] A Fusion library other programs load (`.dll` / `.so`) - needs `extern`
MOD.004 [DESIGN] Library trust: capability signatures, sandboxing, supply-chain checks (Task 39)
MOD.005 [DESIGN] Import only some names (`import geometry { square, circle }`); `[modules] paths`
MOD.006 [DESIGN] Working with other code: loading a DLL, assembly blocks, calling outside compilers
MOD.007 [DESIGN] Callbacks and events
MOD.008 [DESIGN] Grouped import blocks

#### MEM - memory and ownership
MEM.001 [BUILT] OWNERSHIP: scope plus counting; a returned local is moved
MEM.002 [PLANNED] Assigning moves: `Car b = a` leaves `a` unusable; `byVal` copies (48.1)
MEM.003 [PLANNED] Passing and reading an element borrow; a borrow is never stored (48.2)
MEM.004 [PLANNED] `shared`: read only except to the holder that made it shared (48.5)
MEM.005 [DESIGN] GC and MANUAL as project strategies, never the default; `Shared<T>` / `Weak<T>` (Task 38) - single ownership is the default, no `Unique<T>` (D.080)
MEM.006 [DESIGN] `unsafe` blocks; `free` / `deallocate`
MEM.007 [BUILT] The leak check: every example and test
MEM.008 [PLANNED] `copy(x)` follows `[memory] copy` (deep by default); `copyDeep(x)` always deep
MEM.009 [DESIGN] Arena / region memory (many objects freed together); memory-mapped resources

#### CON - concurrency
CON.001 [PLANNED] `service`: shared state with one owner (reserved keyword); version one (42.0-42.2)
CON.002 [PLANNED] One writer: the service's worker; readers in parallel (42.18)
CON.003 [PLANNED] Temporary services when two or more threads use one variable (42.19)
CON.004 [PLANNED] A thread using two or more resources: a group service - written or made by the compiler (42.20)
CON.005 [PLANNED] A `Service` interface: BasicService, SharedService, FileService, DatabaseService, HotPathService (42.21)
CON.006 [PLANNED] send / sync worked out at the thread boundary (42.22)
CON.007 [PLANNED] `hotpath` functions and `hotpath service` (42.23-42.24)
CON.008 [DESIGN] Group services, service classes, the Thread class, schedulers (42.3-42.9)
CON.009 [POSTPONED] Cluster threads over several servers
CON.010 [PLANNED] Resources as services: files, sockets, databases (42.5); `final` clean-up (42.4)
CON.011 [DESIGN] Default settings that fit the machine (42.6); default timeouts per resource (42.8)
CON.012 [DESIGN] `async` / `await`; `go f(x)`; thread interrupts checked in loops; channels (`<-` read by the lexer only)
CON.013 [PLANNED] The compiler picks how a service runs: a plain variable (one thread), atomics (a simple value), a mailbox with workers (42.0)
CON.014 [PLANNED] Calls wait in order; `async` to not wait; one request at a time (not re-entrant) (42.0)
CON.015 [PLANNED] `service(x).run { }` - several steps as one (42.0)
CON.016 [PLANNED] A timeout means the caller stopped waiting; a request ends completed / failed / timed out / cancelled (42.0)
CON.017 [PLANNED] Settings with `service(x).X = ...`: Mailbox, WhenFull, Timeout, Scheduler, Priority, Rule, WorkerThreadType, ThreadPool (42.2, 42.14)
CON.018 [PLANNED] Every thread has an ID, a parent and a place in the hierarchy; the hierarchy decides who gets a resource (42.7, 42.9)
CON.019 [PLANNED] Concurrency trap checks: warnings by default, errors when `fusion.toml` says so (42.10)

#### SET - settings and tools
SET.001 [BUILT] `fusion.toml` (or .yaml / .json / .ini); camelCase, read case-insensitively; a bad key is an error
SET.002 [BUILT] `[safety] mode` = safe / strict / unsafe
SET.003 [PLANNED] Core modules: Time, Data formats, Currency (Task 43)
SET.004 [PLANNED] Syntax highlighting (36.0), later a language server (Task 36)
SET.005 [PLANNED] An LLVM backend and an IR layer (Task 40); HIDL for hardware (Task 41)
SET.006 [REJECTED] Fetching prices or exchange rates from an external API - in the core or any module
SET.007 [BUILT] `[build] waitAtExit` (default false); `--headless`
SET.008 [PLANNED] Enforce `[safety]` / `[backend]` (31.5)
SET.009 [PLANNED] Errors for tools and AI agents: one form with a `fix:` hint; `--errors json`
SET.010 [DESIGN] `blockStyles` (only some block styles); `config.build.mode`; `[console] lineEnding`
SET.011 [POSTPONED] `config.fusion` writes the settings file from the master template (31.6)
SET.012 [POSTPONED] `console build / run / test / add` - one tool, after Python
SET.013 [DESIGN] How a program is built: script mode, JIT, a library, other platforms (WebAssembly)
SET.014 [DESIGN] Library modules beyond the core (fusionlib): file formats, images, math, networking, graphics, audio, localization
SET.015 [BUILT] `[indentation]` tabWidth, allowMixed; `[source]` allowUnicodeIdentifiers (default false)
SET.016 [BUILT] `[stdlib] layer` = std (everything) / alloc (no OS: no print, no files) / core (no heap)
SET.017 [BUILT] `[strings]` maxLength, encoding (utf-8 / ascii); `[structs]` nesting depth, string storage and warnings
SET.018 [BUILT] `[backend] target = "c"`; other targets with Task 40
SET.019 [DESIGN] `[project]` name, version, the file that holds main
SET.020 [DESIGN] `[build]` mode (debug / release), optimize (speed / size / none), output (exe / lib); `[backend]` platform (windows-x64, linux-x64, wasm)
SET.021 [DESIGN] `[threads] enabled` - threads off for small devices
SET.022 [DESIGN] Strict mode extras: null checks forced, `Weak<T>` an error, callbacks limited
SET.023 [DESIGN] Tools: a formatter that converts between block styles, a debugger protocol, hot reloading, a bytecode VM
SET.024 [DESIGN] An IDE module (fusionlib.IDE): code-quality overlays, refactoring, a symbol database

---

## 2. Decisions

| ID | Decision | Feature | Since | Detail | Status |
|---|---|---|---|---|---|
| D.001 | Code to an interface, not an implementation (`List`, `Collection`, `Service`) | GOL.006 | 2026-10-28 | Classes.md | ACTIVE |
| D.002 | A behaviour that differs from most languages becomes a setting; the default is the familiar one | GOL.006 | 2026-10-24 | FEATURES.md top | ACTIVE |
| D.003 | No silent changes: an impossible value is an error, never cut or adjusted | GOL.008 | 2026-10 | - | ACTIVE |
| D.004 | Method names say what they do (`copyPart`, `removeLast`); short names are aliases (`slice`, `pop`) | SYN.011 | 2026-10-27 | CLAUDE.md | ACTIVE |
| D.005 | The shortest readable syntax; well-known long names kept as aliases | SYN | 2026-10 | - | ACTIVE |
| D.006 | `implements` written out; default methods in interfaces a setting, off | CLS.006 | 2026-10-28 | taskSummary2.md | ACTIVE |
| D.007 | Nothing written: fields and module variables private, everything else public | CLS.004 | 2026-10-30 | Classes.md 1 | ACTIVE |
| D.008 | `private` on a top-level item is an error - write `internal` | CLS.004 | 2026-10-30 | Classes.md 1 | ACTIVE |
| D.009 | Form B may change only its own variable (and the const / let it sets up) | SYN.013 | 2026-10-30 | Classes.md 4 | ACTIVE |
| D.010 | `Default` type: `s = null` lets the old object go and makes a new default one | CLS.006 | 2026-10-30 | Classes.md 5 | ACTIVE |
| D.011 | readonly is deep; passing it on is an error only when that function changes it | FUN.003 | 2026-10-30 | Object_Lifetime.md 3 | ACTIVE |
| D.012 | Test every nullable feature with and without a null check | NUL.002 | 2026-10-28 | CLAUDE.md 4b | ACTIVE |
| D.013 | OWNERSHIP is always the first memory choice; GC / MANUAL only where a project needs them | MEM.001 | 2026-10-29 | Object_Lifetime.md 1 | ACTIVE |
| D.014 | Assigning moves (`[memory] assignment = "move"`, `"share"` optional) - Lists, Maps, objects | MEM.002 | 2026-10-31 | Ownership.md 2 | ACTIVE (planned) |
| D.015 | A struct's collection only lends itself - never moved out | MEM.003 | 2026-10-31 | Ownership.md 2 | ACTIVE (planned) |
| D.016 | The called function's signature is the contract; a library counts by its signature only; a non-Fusion library gets a warning | FUN.004 | 2026-10-31 | Ownership.md 4 | ACTIVE (planned) |
| D.017 | A value two or more threads use gets a temporary service; ownership returns when they end | CON.003 | 2026-10-31 | Ownership.md 6 | ACTIVE (planned) |
| D.018 | Counts inside a service are plain; `shared` objects a thread can reach and handles stay atomic | CON.002 | 2026-10-31 | Service.md S8 | ACTIVE (narrows "always atomic", 2026-09-13) |
| D.019 | `hotpath service` (a modifier, not `serviceHotPath`); a dedicated thread that never sleeps | CON.007 | 2026-10-31 | Service.md | ACTIVE (planned) |
| D.020 | `fixed(n)`: lower fine, higher an error (never cut); starts empty, memory reserved once (the meaning: D.064) | TYP.006 | 2026-10-31 | Arrays.md | ACTIVE (planned) |
| D.021 | `money` is a long of minor units; the Currency module enforces each currency's steps | TYP.003 | 2026-10-29 | FEATURES 47.2 | ACTIVE (planned) |
| D.022 | The core and every module never fetch prices or rates; the developer passes them in | SET.006 | 2026-10-29 | CLAUDE.md | ACTIVE |
| D.023 | Settings named in camelCase, read case-insensitively, `_` ignored | SET.001 | 2026-10-28 | fusionSettings.xml | ACTIVE |
| D.024 | `service` is a reserved keyword | CON.001 | 2026-10-29 | Service.md | ACTIVE |
| D.025 | Arrays, Lists, Maps move in normal code; inside a struct they can only be borrowed | COL.002 | 2026-10-31 | Ownership.md 2 | ACTIVE (planned) |
| D.026 | A struct's fields can't be moved out, only borrowed; the whole struct moves or is borrowed | STC.001 | 2026-10-31 | Ownership.md 2 | ACTIVE (planned; replaces "copied with its Lists" when Task 48 is built) |
| D.027 | No GC by default - OWNERSHIP first; a GC only when made in code or when a project's `fusion.toml` chooses it | MEM.005 | 2026-10-31 | Object_Lifetime.md 1 | ACTIVE |
| D.028 | Data shared across threads: a temporary service first; `send` moves data (and its ownership) to another thread; or share a readonly value | CON.006 | 2026-10-31 | Ownership.md 5, 6 | ACTIVE (planned) |
| D.029 | The three strategies may be mixed: MANUAL frees by hand; a GC can be made in code as a backup | MEM.005 | 2026-10-28 | Object_Lifetime.md 1 | ACTIVE (planned) |
| D.030 | `unsafe` functions and `unsafe { }` blocks: only memory, assembly and devices | MEM.006 | 2026-10-28 | Object_Lifetime.md 2 | ACTIVE (planned) |
| D.031 | `free(x)`: unsafe, at once; `deallocate(x)`: safe, checks the count; using the variable after either is a compile error | MEM.006 | 2026-10-28 | Object_Lifetime.md 2 | ACTIVE (planned) |
| D.032 | Passing never copies an object or collection: it is borrowed, with no count change | MEM.003 | 2026-10-28 | Object_Lifetime.md 3 | ACTIVE |
| D.033 | `byVal` copies deeply (the engine inside the car too); `[memory] copy = "deep"` (default) / "shallow" | MEM.008 | 2026-10-28 | Object_Lifetime.md 4b | ACTIVE (planned) |
| D.034 | `nocopy` field: the class can't be copied unless Cloneable (`clone()` recreates it); `noshare` field: always copied; not both on one field | CLS.008 | 2026-10-28 | Object_Lifetime.md 4b | ACTIVE (planned) |
| D.035 | Leaks are warned in development; a published app logs them, never shows debug messages | MEM.007 | 2026-10-28 | Object_Lifetime.md 9 | ACTIVE |
| D.036 | Constructors: `constructor(...)` or `Car(...)`; `new` optional; private constructors and static factories allowed | CLS.002 | 2026-10-28 | Object_Lifetime.md 4 | ACTIVE |
| D.037 | `[safety] mode`: safe (default) / strict (every warning an error) / unsafe (the whole project) | SET.002 | 2026-10-28 | fusionSettings.xml | ACTIVE |
| D.038 | Whole-number overflow is an error; `[numbers] overflowWrap = true` wraps | TYP.001 | 2026-10-28 | SYNTAX_REFERENCE.md | ACTIVE |
| D.039 | A circle of classes gets a warning; Weak references break it (Task 38) | CLS.010 | 2026-10-29 | Object_Lifetime.md | ACTIVE |
| D.040 | A class with no constructor written gets `Car()`: value fields at their defaults, objects null | CLS.002 | 2026-10-29 | Classes.md 2 | ACTIVE |
| D.041 | A private constructor is used only by forms A, B, C and the class's own functions | CLS.002 | 2026-10-30 | Classes.md 2 | ACTIVE |
| D.042 | Static set-up forms A, B, C in that order; classes set up by dependency; a circle is a compile error showing the chain | CLS.003 | 2026-10-30 | Classes.md 3 | ACTIVE |
| D.043 | Printing an object: its `ToString`; without one, the class name and a warning | CLS.005 | 2026-10-30 | Classes.md 6 | ACTIVE |
| D.044 | Arrays, Lists, Maps are never null - empty when declared; a nullable setting per kind (default false) | COL.003 | 2026-10-27 | Arrays.md 1 | ACTIVE |
| D.045 | Arrays grow and shrink only at the end - an item never moves position; Lists change anywhere | COL.002 | 2026-10-27 | Arrays.md 3 | ACTIVE (planned) |
| D.046 | `copyPart(start, count)` / `copyPartAt(start, end)` copy; from 0, end included, past the end stops there, a start outside is an IndexError; `slice` / `sliceAt` as aliases | COL.002 | 2026-10-27 | Arrays.md 8 | ACTIVE (planned) |
| D.047 | `a + b + c` combines arrays or Lists of one type; Maps use `add(otherMap)` - a key already there is replaced (a setting) | COL.012 | 2026-10-27 | Arrays.md 5 | ACTIVE (planned) |
| D.048 | Arrays and Lists allow duplicates; Map keys never repeat - a non-empty constant string or a whole number 0 or above; values any type | COL.012 | 2026-10-27 | Arrays.md 5 | ACTIVE |
| D.049 | `foreach`: the item's type is the collection's; `continue` / `break` allowed (changing it inside: D.058) | COL.005 | 2026-10-27 | Arrays.md 6 | ACTIVE (planned) |
| D.050 | A string is never null by default (`[strings] nullable`, default false) | NUL.001 | 2026-10-27 | Nullable_Values.md 2 | ACTIVE |
| D.051 | An unset enum is null, like a class object - not its first value | NUL.001 | 2026-10-27 | Nullable_Values.md 2 | ACTIVE |
| D.052 | A null in a `match` goes to `case null`, else to `else`; neither: a NullError | SYN.007 | 2026-10-28 | Nullable_Values.md 8 | ACTIVE |
| D.053 | `?.` is a guard: a null object's function isn't run, no error, false in an `if`; `??` gives a default | NUL.003 | 2026-10-27 | Nullable_Values.md 3 | ACTIVE (planned) |
| D.054 | Null checks: `==`, `===`, `is null`; `x?.null` as quick typing; no `x!` | NUL.003 | 2026-10-27 | Nullable_Values.md 3 | ACTIVE (planned) |
| D.055 | `string?.length()` / `array?.length` on null give -1; everything else gives null | NUL.003 | 2026-10-27 | Nullable_Values.md 5 | ACTIVE (planned) |
| D.056 | Numbers as conditions only in `if` / `while`: `[conditions] numbers` = positive (default) / nonzero / off; `bool b = count` is an error | SYN.005 | 2026-10-27 | Nullable_Values.md 4 | ACTIVE |
| D.057 | A List, Map or array used by two or more threads gets a temporary service (D.017); `[collections] threads` only picks its worker: a shared pool (default) or a dedicated thread | CON.003 | 2026-10-31 | Concurrency.md 3.12 | ACTIVE (planned) |
| D.058 | The collection being looped over can't be changed inside the loop - any loop (`for`, `foreach`), any collection; build a new one (`b`) from it instead. A compile error where seen, else a ModifiedWhileLoopingError | COL.005 | 2026-10-31 | Arrays.md 6 | ACTIVE |
| D.059 | No string prefixes (`m"`, `f"`): a plain string can change; interpolation is always on | STR.001 | 2026-10-27 | spec Strings | ACTIVE |
| D.060 | An int is used as a float only when it fits exactly - else a compile error (a written number) or a PrecisionError (a value); `[numbers] autoWidening = true` widens anything, with a warning | TYP.001 | 2026-10-17 | spec Type Casting | ACTIVE |
| D.061 | Error returns and exceptions are both on by default; a project may turn either off | FUN.001 | 2026-10-16 | spec Errors | ACTIVE |
| D.062 | Errors bubble up; capturing is optional on any call; `catch` goes by first match, a parent catches its children | FUN.002 | 2026-10-16 | spec Errors | ACTIVE |
| D.063 | No `T?` types: only class objects and enums can be null; `?` goes on a variable | NUL.001 | 2026-10-27 | Nullable_Values.md | ACTIVE |
| D.064 | `const`: nothing changes - neither the length nor the values. `fixed(n)`: only the size is limited - at most n characters or slots, the values may change; the compiler guarantees it never exceeds n (limited memory, hot paths) | TYP.006 | 2026-10-31 | Arrays.md 1 | ACTIVE (planned) |
| D.065 | `match` is the form; `switch` an alias (familiar from VB.NET). `else if` for 2-3 checks; `match` / `switch` for a list of values | SYN.007 | 2026-10-31 | SYNTAX_REFERENCE.md | ACTIVE |
| D.066 | A service is made by a parent thread, outside loops (a class field or a function variable); its child threads use it; a warning when no other thread does | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.067 | Each call on a service is one step; anything read out is a copy; copying a service variable gives another handle to it | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.068 | A service finishes one request before the next (not re-entrant); the caller waits unless it writes `async` | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.069 | `WorkerThreadType` AUTO by default: SHARED as more threads read the resource, SINGLE when its work is heavy | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.070 | A full mailbox: the sender waits (`WhenFull = WAIT`, the default) or gets a QueueFullError; a hot path never waits | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.071 | Every wait has a timeout; defaults per kind of resource | CON.001 | 2026-10-23 | Concurrency.md 3.7 | ACTIVE (planned) |
| D.072 | Resources are services by default (`resourceAsService = true`); direct access only in unsafe mode | CON.010 | 2026-10-23 | Concurrency.md 3.6 | ACTIVE (planned) |
| D.073 | The OS scheduler by default; a Fusion scheduler for advanced use | CON.008 | 2026-10-23 | Concurrency.md 3.6 | ACTIVE (planned) |
| D.074 | Concurrency trap checks are warnings by default; `fusion.toml` can make each an error | CON.001 | 2026-10-23 | Concurrency.md 3.6 | ACTIVE (planned) |
| D.075 | The principles P1-P11 govern every concurrency feature | GOL.004 | 2026-10-23 | Concurrency_Traps.md | ACTIVE |
| D.076 | A misspelled setting or a bad value is an error, never ignored; every built setting, its values and default are in `files/fusionSettings.xml`; every setting a finished Fusion will have, tagged, in `files/showcase/fusion.toml` | SET.001 | 2026-10-23 | fusionSettings.xml | ACTIVE |
| D.077 | A thread using two or more resources: they become a **group service** - written by the developer or made by the compiler. It is their temporary owner; its worker borrows them and carries out the requests; when they are done it lets go, and each variable owns its value again. A **service** manages one resource, a **group service** several | CON.004 | 2026-10-31 | Ownership.md 7 | ACTIVE (planned) |
| D.078 | No automatic cycle detection: `Weak<T>` breaks a circle of objects | MEM.005 | 2026-09-13 | spec Memory | ACTIVE (planned) |
| D.079 | `Weak<T>.lock()` gives a `Shared<T>` that is null when the target is gone - the caller checks; never a crash (written without `?` - D.063) | MEM.005 | 2026-09-13 | spec Memory | ACTIVE (planned) |
| D.080 | No `.move()`: under OWNERSHIP assigning moves by itself; `byVal` copies, `byRef` borrows. Every object is single-owner by default, so no `Unique<T>` wrapper is needed (replaces Task 12.7's written move) | MEM.002 | 2026-10-31 | Ownership.md 2 | ACTIVE (planned) |
| D.081 | Not catchable: running out of memory, a List past 536,870,911 elements - every other failure is an error a program can catch | FUN.002 | 2026-10-16 | spec Errors | ACTIVE |
