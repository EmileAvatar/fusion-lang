# Fusion - Decisions

The single list of what Fusion is and what has been decided. Keep it small: one line per
feature, one row per decision. Only the **latest** decision on a subject is kept; an older
one is removed when replaced (its history is in git and the design document named). Language
features only - no bug fixes, no discussions.

- **Section 1** - every feature, one line each: `AREA.NNN [STATUS] description`
- **Section 2** - the decisions behind them, in a table; a clash between two is marked `CLASH`
  (none open - C.001-C.011 settled: D.025-D.028, D.057, D.058, D.064, D.065, D.077, D.080, D.094)
- A decision row: what was decided, a short **why** (`?` = not written down yet - ask the user),
  the feature, the date, where the detail is, and its status: `ACTIVE` (decided by the user) or
  `PROPOSED` (suggested by Claude, not official until the user makes it ACTIVE). Only decisions
  made are kept - a replaced one is removed, not marked superseded
- Status words: `[BUILT]` implemented · `[PARTIAL]` some parts built, some still planned or in
  design - every PARTIAL is resolved before self-hosting counts as complete (Task 35) ·
  `[PLANNED]` designed, not built · `[DESIGN]` still being planned / designed · `[POSTPONED]`
  waits for something · `[REJECTED]` decided against
- Kept up to date at the end of every task and session (user, 2026-11-07)
- Detail lives elsewhere: status `files/FEATURES.md`, what works `files/SYNTAX_REFERENCE.md`, settings
  `files/fusionSettings.xml`, design documents (named in each row)
- Built from every design document, note, setting and the compiler (Task 49, done 2026-10-31);
  `python check.py` checks its shape (`decisions`)

---

## 1. Fusion - the goal and the features

#### GOL - the goal
GOL.001 [PARTIAL] An agnostic language: each project chooses safety, memory model, concurrency and backend in `fusion.toml` - safety and memory settings built; concurrency and backends planned
GOL.002 [BUILT] Compiles Fusion -> C -> a native program (GCC); the compiler is written in Python for now
GOL.003 [PLANNED] Self-hosting: the compiler written in Fusion compiles itself (Task 35); Python retired after
GOL.004 [DESIGN] A million requests on one machine: no data races by construction, no deadlocks, small footprint (Task 42)
GOL.005 [PARTIAL] Memory-safe without a GC by default: one owner, moves, borrows built (Task 48); readonly results, deep const, storing `this` planned (Task 50, 48)
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
SYN.014 [PLANNED] Duration literals: `500ms`, `5s`, `2min` an int of milliseconds; `ns`, `us` a long of nanoseconds (hot path) - never mixed (42.16)
SYN.015 [REJECTED] An `I` prefix on interface names
SYN.016 [BUILT] Identifiers are ASCII; Trojan Source and look-alike letters are rejected
SYN.017 [BUILT] `_` for an unused `match` field
SYN.018 [DESIGN] `switch` as an alias of `match` (VB.NET); `elif` for `else if`
SYN.019 [DESIGN] `loop { }` - no break / return inside is a compile error; the keyword may be dropped
SYN.020 [DESIGN] `++` / `--` as statements only, never inside an expression
SYN.021 [DESIGN] `if` as a value; do-while
SYN.022 [DESIGN] Guards and ranges in match cases (`case x if x < 0`, `case 0...9`)
SYN.023 [DESIGN] `assert cond, "message"` - an AssertionError when false
SYN.024 [BUILT] Type tests `if s is string`; `typeOf(x)` as text (32.5a, 32.7)
SYN.025 [DESIGN] Extension methods (`extend string { }`); function overloading by parameter types
SYN.026 [DESIGN] Copy with changes (`a with { x = 5 }`); tuples
SYN.027 [DESIGN] Operands evaluated in one written order - today C's order (37.2)
SYN.028 [POSTPONED] Closures; named lambdas inside functions; multi-line lambda bodies
SYN.029 [BUILT] Comments `//` and `/* */`; `<>` as another way to write `!=`; hex, binary and octal numbers (`0xFF`)
SYN.030 [BUILT] `unchecked { }` - whole-number `+ - *` inside wrap around on purpose
SYN.031 [POSTPONED] `'` comments (VB style) - off so `'c'` works; maybe only at the start of a line
SYN.032 [DESIGN] `#Region` / `#End Region`; documentation comments; documentation written from them
SYN.033 [DESIGN] `loop { } end loop` with safety checks; loop labels; an iteration limit (`[safety] maxIterations`)
SYN.034 [PARTIAL] The `...` operator: variadic `string... args` of main built; ranges `1...100`, variadic `int... numbers`, spread `[...a, ...b]` designed
SYN.035 [DESIGN] `**` (power) - read by the lexer, not built; annotations `@name(...)`
SYN.036 [DESIGN] `'''` comment blocks; comment levels 0-5; coding hints
SYN.037 [DESIGN] Semicolons accepted; reading code written in other languages' syntax
SYN.038 [DESIGN] A minimum variable-name length in strict mode (default 3; loop counters and type parameters excepted)
SYN.039 [BUILT] `and`, `or`, `not`; a lambda as `func(int x) : x * 2`
SYN.040 [BUILT] `[source] caseSensitive` (default true); false: names that differ only in case are an error, each pair listed (32.11)

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
TYP.013 [DESIGN] Autoboxing (`(42).toString()`) - the type classes (`Int`, `String`) are built
TYP.014 [DESIGN] A `bit` type and bit-level operations
TYP.015 [DESIGN] `decimal(p, s)`: an exact fixed-point number - after `money` (47.2.3)
TYP.016 [PARTIAL] A cast written in front: `(Shape)aCircle` built - a compile error where it can be seen, else a CastError (32.5a); between numbers `(int)d` planned
TYP.017 [DESIGN] Value types have built-in methods through internal interfaces - `Length` with `length()` on strings, arrays, Lists and Maps, working on null and "" alike (52.4, D.055)

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
COL.005 [BUILT] `foreach (T x in c)` / `foreach x in c` - arrays, Lists, Maps, a Collection<T> class (32.4)
COL.006 [PARTIAL] `Collection<T>` and `Iterator<T>` - a class of your own, a List and a Map (of `Entry<K, V>`) built (32.4, 32.6); arrays planned (45.10)
COL.007 [BUILT] List / Map options in the set-up block: noDuplicates, noNull, readOnly - a DuplicateError / NullError / ReadOnlyError (32.14)
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
FUN.004 [PARTIAL] `readonly` / `byVal` / `byRef` written at the call built (48.3); library rows wait for 39.3
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
FUN.016 [PLANNED] A readonly result: `readonly Engine function getEngine()` - the caller gets a read-only borrow; part of the signature (50.1, D.110)
FUN.017 [PLANNED] `readonly` on a copy (a number result, `f(readonly n)`) is a warning, not an error (50.4, D.113)

#### NUL - null
NUL.001 [BUILT] Value types are never null; class objects and enums can be
NUL.002 [BUILT] A null without a check is a NullError a `catch` can handle; `null == null` is true
NUL.003 [PARTIAL] `case null` built (30.12); `?.`, `?.null`, `??` planned (Task 30.2)
NUL.004 [REJECTED] `T?` types - `?` goes on a variable (`x?.f()`), never on a type
NUL.005 [PLANNED] A `?.` comparison is false on null and warns; `!` around one is a compile error - `[conditions]` setting allows it with a warning (52.7, D.116)
NUL.006 [PLANNED] The compiler checks an object is made before it is used: a surely-null one passed is an error; a `?` parameter without a null check warns (52.7, D.117)

#### STC - structs
STC.001 [BUILT] Structs: value types, copied, never null; may hold Lists, Maps, strings
STC.002 [BUILT] Methods on structs (`[structs] functions`, default off)
STC.003 [BUILT] A struct building on a struct (`implements` / `extends` / `includes`)
STC.004 [BUILT] A struct as text: `"{e}"` -> `name : "Jeff",age : 30`
STC.005 [REJECTED] A struct implementing an interface - a struct only holds values
STC.006 [BUILT] A struct's fields are only borrowed, never moved out; the whole struct moves or is borrowed (48.9, D.026, D.108)
STC.007 [BUILT] A struct may hold an object - null until set; with "share" a copied struct shares it, `byVal` clones it (D.097)
STC.008 [BUILT] Commas between struct fields: needed on one line (`struct Point { int x, int y }`), not needed on new lines (32.12)

#### CLS - classes
CLS.001 [BUILT] Classes: objects by reference, counted, freed when the last holder goes
CLS.002 [BUILT] Several constructors; `this(...)`; `new` optional
CLS.003 [BUILT] Statics set up in three forms (A, B, C) before main
CLS.004 [BUILT] Visibility `private` (the class) / `internal` (the namespace) / `public`; `namespace A.B`
CLS.005 [BUILT] Printing an object gives its class name, with a warning (until ToString)
CLS.006 [BUILT] Interfaces: `interface`, `implements` (several), building on several, as a type, `is`, casts; default methods behind `[interfaces] defaultMethods` (32.5a)
CLS.007 [BUILT] Inheritance: one parent, `inherits` (alias `extends`), `override`, `sealed`, `abstract`, `protected`, `super`; `typeOf(x)` gives the chain (32.7)
CLS.008 [BUILT] `nocopy` / `noshare` fields; `byVal` copies objects; `Cloneable` with its own clone() (32.5b)
CLS.009 [POSTPONED] The builder pattern (after Task 32)
CLS.010 [BUILT] A warning for each circle of classes that could leak
CLS.011 [DESIGN] Properties: `property Name: type { get; set; }`, computed and indexed ones
CLS.012 [DESIGN] A constant in a class is always static
CLS.013 [BUILT] `abstract`, `sealed`, `override`, `protected` (32.7)
CLS.014 [BUILT] `implements Default` - a variable, field or static of the type is never null; `= null` makes a new one (32.5b)
CLS.015 [BUILT] `implements ToString` - print, format, "{x}", toString(x) use its toString(), also through an interface (32.5b)
CLS.016 [POSTPONED] Form D: `{ }` on an abstract class or an interface makes a class right there - fields set, functions given, using the variables around it; after closures (52.1, D.119)
CLS.017 [POSTPONED] A setting allowing `private` on a top-level item (meaning its module); off for now (52.3)
CLS.018 [DESIGN] `virtual` - a reserved word, not used yet
CLS.019 [PLANNED] An interface's functions are public or internal - `private` is a compile error (52.6, D.114)

#### MOD - modules
MOD.001 [BUILT] Modules and `import` (a folder = a module); module variables and constants
MOD.002 [BUILT] `--interface`: the public interface of the imported modules
MOD.003 [POSTPONED] A Fusion library other programs load (`.dll` / `.so`) - needs `extern`
MOD.004 [DESIGN] Library trust: nothing trusted by default - a library without source is sandboxed (no files / network) unless the developer trusts it; capability signatures, supply-chain checks (Task 39, D.122)
MOD.005 [DESIGN] Import only some names (`import geometry { square, circle }`); `[modules] paths`
MOD.006 [DESIGN] Working with other code: loading a DLL, assembly blocks, calling outside compilers
MOD.007 [DESIGN] Callbacks and events
MOD.008 [DESIGN] Grouped import blocks
MOD.009 [DESIGN] Data formats module (fusionlib): JSON, XML, TOML, YAML, INI, MD to an in-memory document, load / save; JSON and XML written in the code: `(FILE_LANG.XML)"""..."""` (43.2)
MOD.010 [DESIGN] HIDL library: hardware testing in the style of Maia - a DUT block, drive / expect vectors, clocks, bit widths (41.10)
MOD.011 [DESIGN] Language modules `import Lang.Python.Fusion`: each brings its lexer, parser, AST and rules through one injection point - migrate a language to new .fusion files, or compile it by its own rules (Task 49)

#### MEM - memory and ownership
MEM.001 [BUILT] OWNERSHIP: scope plus counting; a returned local is moved
MEM.002 [BUILT] Assigning moves: `Car b = a` leaves `a` unusable; `byVal` copies - `[memory] assignment = "move"`, the default since 48.9; "share" keeps two names on one object (D.102)
MEM.003 [BUILT] Passing and reading an element borrow; a borrow is never stored (48.2) - with `[memory] assignment = "move"`
MEM.004 [POSTPONED] `shared`: read only except to the holder that made it shared (48.5) - not until a real need (D.106)
MEM.005 [DESIGN] GC and MANUAL as project strategies, never the default; `Shared<T>` / `Weak<T>` (Task 38) - single ownership is the default, no `Unique<T>` (D.080)
MEM.006 [DESIGN] `unsafe` blocks; `free` / `deallocate`
MEM.007 [BUILT] The leak check: every example and test
MEM.008 [PLANNED] `copy(x)` follows `[memory] copy` (deep by default); `copyDeep(x)` always deep
MEM.009 [DESIGN] Arena / region memory (many objects freed together); memory-mapped resources
MEM.010 [PLANNED] `const` on an object is deep - no field set, no changing method; a `byVal` copy may change (50.2, D.112)
MEM.011 [PLANNED] Storing `this` shares the object (counted): one car in several collections is one car, freed when the last holder lets go (48.12, D.103)
MEM.012 [PLANNED] While a borrow changes a value, its owner may still be read - only changing it another way is an error (48.10, D.123)
MEM.013 [PLANNED] A setting per borrow rule: one owner (`assignment`), one writer, a borrow never outlives its owner (48.11, D.124)

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
CON.020 [DESIGN] A `Transaction` interface: commit gives OK / FAILED, rollback - marks a call as part of a transaction (42.29, D.120)

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

| ID | Decision | Why | Feature | Since | Detail | Status |
|---|---|---|---|---|---|---|
| D.001 | Code to an interface, not an implementation (`List`, `Collection`, `Service`) | the implementation behind it can change later | GOL.006 | 2026-10-28 | files/Classes.md | ACTIVE |
| D.002 | A behaviour that differs from most languages becomes a setting; the default is the familiar one | people from other languages are not surprised; a project may switch | GOL.006 | 2026-10-24 | files/FEATURES.md top | ACTIVE |
| D.003 | No silent changes: an impossible value is an error, never cut or adjusted | a silently changed value is a hidden bug; an error shows it | GOL.008 | 2026-10 | - | ACTIVE |
| D.004 | Method names say what they do (`copyPart`, `removeLast`); short names are aliases (`slice`, `pop`) | code reads clearly; changing vs copying is visible in the name | SYN.011 | 2026-10-27 | CLAUDE.md | ACTIVE |
| D.005 | The shortest readable syntax; well-known long names kept as aliases | less to type and read; familiar names still work | SYN | 2026-10 | - | ACTIVE |
| D.006 | `implements` written out; default methods in interfaces a setting, off | implements is easy to read; a default method may not be used as meant - opt in | CLS.006 | 2026-10-28 | files/taskSummary2.md | ACTIVE |
| D.007 | Nothing written: fields and module variables private, everything else public | a safe default: data hidden, behaviour usable | CLS.004 | 2026-10-30 | files/Classes.md 1 | ACTIVE |
| D.008 | `private` on a top-level item is an error - write `internal` | private hides a class's detail; internal lets the namespace / module use it (a setting later - CLS.017) | CLS.004 | 2026-10-30 | files/Classes.md 1 | ACTIVE |
| D.009 | Form B may change only its own variable (and the const / let it sets up) | sets an object up without a builder or another constructor - complex set-up in place | SYN.013 | 2026-10-30 | files/Classes.md 4 | ACTIVE |
| D.010 | `Default` type: `s = null` lets the old object go and makes a new default one | a new object is always there, never null; the developer decides its default values | CLS.006 | 2026-10-30 | files/Classes.md 5 | ACTIVE |
| D.011 | readonly is deep; passing it on is an error only when that function changes it | readonly holds through calls; readers may still be passed it freely | FUN.003 | 2026-10-30 | files/Object_Lifetime.md 3 | ACTIVE |
| D.012 | Test every nullable feature with and without a null check | a null is shown to be caught, and the checks to work | NUL.002 | 2026-10-28 | CLAUDE.md 4b | ACTIVE |
| D.013 | OWNERSHIP is always the first memory choice; GC / MANUAL only where a project needs them | memory stability: no crashes, no leaks (instability, security holes) | MEM.001 | 2026-10-29 | files/Object_Lifetime.md 1 | ACTIVE |
| D.014 | Assigning moves (`[memory] assignment = "move"`, `"share"` optional) - Lists, Maps, objects | one owner per value: freed exactly once, no GC, no hidden sharing | MEM.002 | 2026-10-31 | files/Ownership.md 2 | ACTIVE (planned) |
| D.015 | A struct's collection only lends itself - never moved out | the struct stays whole and usable | MEM.003 | 2026-10-31 | files/Ownership.md 2 | ACTIVE (planned) |
| D.016 | The called function's signature is the contract; a library counts by its signature only; a non-Fusion library gets a warning | never trust code: only the signature is checked; a body may change | FUN.004 | 2026-10-31 | files/Ownership.md 4 | ACTIVE (planned) |
| D.017 | A value two or more threads use gets a temporary service; ownership returns when they end | no data races by construction; ownership comes back after | CON.003 | 2026-10-31 | files/Ownership.md 6 | ACTIVE (planned) |
| D.018 | Counts inside a service are plain; `shared` objects a thread can reach and handles stay atomic | atomics cost time; inside a service only one thread runs | CON.002 | 2026-10-31 | Service.md S8 | ACTIVE (narrows "always atomic", 2026-09-13) |
| D.019 | `hotpath service` (a modifier, not `serviceHotPath`); a dedicated thread that never sleeps | one keyword (`service`); a hot path cannot wait for sleep / wake | CON.007 | 2026-10-31 | Service.md | ACTIVE (planned) |
| D.020 | `fixed(n)`: lower fine, higher an error (never cut); starts empty, memory reserved once (the meaning: D.064) | never cut silently (D.003); memory reserved once for hot paths | TYP.006 | 2026-10-31 | files/Arrays.md | ACTIVE (planned) |
| D.021 | `money` is a long of minor units; the Currency module enforces each currency's steps | exact money: no float rounding | TYP.003 | 2026-10-29 | FEATURES 47.2 | ACTIVE (planned) |
| D.022 | The core and every module never fetch prices or rates; the developer passes them in | the developer controls where data comes from; the core never calls out | SET.006 | 2026-10-29 | CLAUDE.md | ACTIVE |
| D.023 | Settings named in camelCase, read case-insensitively, `_` ignored | forgiving to read, one style to write | SET.001 | 2026-10-28 | fusionSettings.xml | ACTIVE |
| D.024 | `service` is a reserved keyword | services are a core feature of Fusion - a major selling point | CON.001 | 2026-10-29 | Service.md | ACTIVE |
| D.025 | Arrays, Lists, Maps move in normal code; inside a struct they can only be borrowed | one owner; a struct stays whole (D.015) | COL.002 | 2026-10-31 | files/Ownership.md 2 | ACTIVE (planned) |
| D.026 | A struct's fields can't be moved out, only borrowed; the whole struct moves or is borrowed | a struct missing a field cannot be used safely | STC.001 | 2026-10-31 | files/Ownership.md 2 | ACTIVE (planned; replaces "copied with its Lists" when Task 48 is built) |
| D.027 | No GC by default - OWNERSHIP first; a GC only when made in code or when a project's `fusion.toml` chooses it | OWNERSHIP first (D.013); a GC only by choice | MEM.005 | 2026-10-31 | files/Object_Lifetime.md 1 | ACTIVE |
| D.028 | Data shared across threads: a temporary service first; `send` moves data (and its ownership) to another thread; or share a readonly value | no data races: one owner at a time | CON.006 | 2026-10-31 | files/Ownership.md 5, 6 | ACTIVE (planned) |
| D.029 | The three strategies may be mixed: MANUAL frees by hand; a GC can be made in code as a backup | a project picks what each part needs | MEM.005 | 2026-10-28 | files/Object_Lifetime.md 1 | ACTIVE (planned) |
| D.030 | `unsafe` functions and `unsafe { }` blocks: only memory, assembly and devices | unsafe code kept small and visible - easy to review | MEM.006 | 2026-10-28 | files/Object_Lifetime.md 2 | ACTIVE (planned) |
| D.031 | `free(x)`: unsafe, at once; `deallocate(x)`: safe, checks the count; using the variable after either is a compile error | use after free caught at compile time | MEM.006 | 2026-10-28 | files/Object_Lifetime.md 2 | ACTIVE (planned) |
| D.032 | Passing never copies an object or collection: it is borrowed, with no count change | passing is cheap and the caller keeps its value | MEM.003 | 2026-10-28 | files/Object_Lifetime.md 3 | ACTIVE |
| D.033 | `byVal` copies deeply (the engine inside the car too); `[memory] copy = "deep"` (default) / "shallow" | a copy shares nothing with the original | MEM.008 | 2026-10-28 | files/Object_Lifetime.md 4b | ACTIVE (planned) |
| D.034 | `nocopy` field: the class can't be copied unless Cloneable (`clone()` recreates it); `noshare` field: always copied; not both on one field | some objects (handles, devices) must never be copied | CLS.008 | 2026-10-28 | files/Object_Lifetime.md 4b | ACTIVE (planned) |
| D.035 | Leaks are warned in development; a published app logs them, never shows debug messages | developers learn of leaks early; users never see debug output | MEM.007 | 2026-10-28 | files/Object_Lifetime.md 9 | ACTIVE |
| D.036 | Constructors: `constructor(...)` or `Car(...)`; `new` optional; private constructors and static factories allowed | familiar from Java / C#; `new` optional for short code (D.005) | CLS.002 | 2026-10-28 | files/Object_Lifetime.md 4 | ACTIVE |
| D.037 | `[safety] mode`: safe (default) / strict (every warning an error) / unsafe (the whole project) | one switch for a project's safety level (GOL.001) | SET.002 | 2026-10-28 | fusionSettings.xml | ACTIVE |
| D.038 | Whole-number overflow is an error; `[numbers] overflowWrap = true` wraps | a wrong number is never silent (D.003) | TYP.001 | 2026-10-28 | files/SYNTAX_REFERENCE.md | ACTIVE |
| D.039 | A circle of classes gets a warning; Weak references break it (Task 38) | counting cannot free a circle | CLS.010 | 2026-10-29 | files/Object_Lifetime.md | ACTIVE |
| D.040 | A class with no constructor written gets `Car()`: value fields at their defaults, objects null | every class can be made without writing a constructor | CLS.002 | 2026-10-29 | files/Classes.md 2 | ACTIVE |
| D.041 | A private constructor is used only by forms A, B, C and the class's own functions | the class controls how its objects are made | CLS.002 | 2026-10-30 | files/Classes.md 2 | ACTIVE |
| D.042 | Static set-up forms A, B, C in that order; classes set up by dependency; a circle is a compile error showing the chain | a known order: no static used before it is set | CLS.003 | 2026-10-30 | files/Classes.md 3 | ACTIVE |
| D.043 | Printing an object: its `ToString`; without one, the class name and a warning | printing always shows something; the warning asks for ToString | CLS.005 | 2026-10-30 | files/Classes.md 6 | ACTIVE |
| D.044 | Arrays, Lists, Maps are never null - empty when declared; a nullable setting per kind (default false) | no null checks on collections - fewer NullErrors | COL.003 | 2026-10-27 | files/Arrays.md 1 | ACTIVE |
| D.045 | Arrays grow and shrink only at the end - an item never moves position; Lists change anywhere | an index stays valid - an item stays where it was | COL.002 | 2026-10-27 | files/Arrays.md 3 | ACTIVE (planned) |
| D.046 | `copyPart(start, count)` / `copyPartAt(start, end)` copy; from 0, end included, past the end stops there, a start outside is an IndexError; `slice` / `sliceAt` as aliases | the name says it copies (D.004); a slice past the end is no error | COL.002 | 2026-10-27 | files/Arrays.md 8 | ACTIVE (planned) |
| D.047 | `a + b + c` combines arrays or Lists of one type; Maps use `add(otherMap)` - a key already there is replaced (a setting) | combining reads naturally; a Map key clash needs a rule | COL.012 | 2026-10-27 | files/Arrays.md 5 | ACTIVE (planned) |
| D.048 | Arrays and Lists allow duplicates; Map keys never repeat - a non-empty constant string or a whole number 0 or above; values any type | a key must find exactly one value | COL.012 | 2026-10-27 | files/Arrays.md 5 | ACTIVE |
| D.049 | `foreach`: the item's type is the collection's; `continue` / `break` allowed (changing it inside: D.058) | familiar loop control | COL.005 | 2026-10-27 | files/Arrays.md 6 | ACTIVE (planned) |
| D.050 | A string is never null by default (`[strings] nullable`, default false) | fewer NullErrors; an empty string is enough | NUL.001 | 2026-10-27 | files/Nullable_Values.md 2 | ACTIVE |
| D.051 | An unset enum is null, like a class object - not its first value | a first value as default would hide a missing set | NUL.001 | 2026-10-27 | files/Nullable_Values.md 2 | ACTIVE |
| D.052 | A null in a `match` goes to `case null`, else to `else`; neither: a NullError | every value handled; a null never slips through | SYN.007 | 2026-10-28 | files/Nullable_Values.md 8 | ACTIVE |
| D.053 | `?.` is a guard: a null object's function isn't run, no error, false in an `if`; `??` gives a default | short code for "if not null"; no crash | NUL.003 | 2026-10-27 | files/Nullable_Values.md 3 | ACTIVE (planned) |
| D.054 | Null checks: `==`, `===`, `is null`; `x?.null` as quick typing; no `x!` | familiar checks; `x!` would crash on null | NUL.003 | 2026-10-27 | files/Nullable_Values.md 3 | ACTIVE (planned) |
| D.055 | `length()` never gives null: 0 when empty, -1 when the string, array, List or Map is null (possible only with its `nullable` setting on). The -1 is allowed only in a comparison (`if` / `while`); anywhere else a null gives a NullError (a compile error where it can be seen) | an int is never null (D.063); -1 can't slip into a sum unnoticed (D.003) | NUL.003 | 2026-11-07 | files/Nullable_Values.md 3 | ACTIVE (planned) |
| D.056 | Numbers as conditions only in `if` / `while`: `[conditions] numbers` = positive (default) / nonzero / off; `bool b = count` is an error | `if count` is familiar; outside conditions an int stays an int | SYN.005 | 2026-10-27 | files/Nullable_Values.md 4 | ACTIVE |
| D.057 | A List, Map or array used by two or more threads gets a temporary service (D.017); `[collections] threads` only picks its worker: a shared pool (default) or a dedicated thread | no data races (D.017); the worker is only a tuning choice | CON.003 | 2026-10-31 | files/Concurrency.md 3.12 | ACTIVE (planned) |
| D.058 | The collection being looped over can't be changed inside the loop - Fusion's own collections never; a class of your own only with `[collections] allowChangeWhileLooping = true` (default false); build a new one (`b`) instead | changing while looping skips items or crashes | COL.005 | 2026-10-31 | files/Arrays.md 6 | ACTIVE |
| D.059 | No string prefixes (`m"`, `f"`): a plain string can change; interpolation is always on | one kind of string - nothing to choose | STR.001 | 2026-10-27 | spec Strings | ACTIVE |
| D.060 | An int is used as a float only when it fits exactly - else a compile error (a written number) or a PrecisionError (a value); `[numbers] autoWidening = true` widens anything, with a warning | no silent loss of precision (D.003) | TYP.001 | 2026-10-17 | spec Type Casting | ACTIVE |
| D.061 | Error returns and exceptions are both on by default; a project may turn either off | each project chooses its error style (GOL.006) | FUN.001 | 2026-10-16 | spec Errors | ACTIVE |
| D.062 | Errors bubble up; capturing is optional on any call; `catch` goes by first match, a parent catches its children | an error cannot be lost; familiar catch order | FUN.002 | 2026-10-16 | spec Errors | ACTIVE |
| D.063 | No `T?` types: only class objects and enums can be null; `?` goes on a variable | null only where it means something; simpler types | NUL.001 | 2026-10-27 | files/Nullable_Values.md | ACTIVE |
| D.064 | `const`: nothing changes - neither the length nor the values. `fixed(n)`: only the size is limited - at most n characters or slots, the values may change; the compiler guarantees it never exceeds n (limited memory, hot paths) | limited memory needs a size limit without freezing the values | TYP.006 | 2026-10-31 | files/Arrays.md 1 | ACTIVE (planned) |
| D.065 | `match` is the form; `switch` an alias (familiar from VB.NET). `else if` for 2-3 checks; `match` / `switch` for a list of values | `match` is clearer; `switch` is familiar | SYN.007 | 2026-10-31 | files/SYNTAX_REFERENCE.md | ACTIVE |
| D.066 | A service is made by a parent thread, outside loops (a class field or a function variable); its child threads use it; a warning when no other thread does | a service outlives the threads that use it | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.067 | Each call on a service is one step; anything read out is a copy; copying a service variable gives another handle to it | a step is atomic; a copy cannot change under the service | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.068 | A service finishes one request before the next (not re-entrant); the caller waits unless it writes `async` | no half-done state; waiting is the familiar call | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.069 | `WorkerThreadType` AUTO by default: SHARED as more threads read the resource, SINGLE when its work is heavy | a good default without tuning; may be set by hand | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.070 | A full mailbox: the sender waits (`WhenFull = WAIT`, the default) or gets a QueueFullError; a hot path never waits | no endless queue; a hot path never blocks | CON.001 | 2026-10-24 | Service.md | ACTIVE (planned) |
| D.071 | Every wait has a timeout; defaults per kind of resource | no freeze lasts forever - it becomes a clear error | CON.001 | 2026-10-23 | files/Concurrency.md 3.7 | ACTIVE (planned) |
| D.072 | Resources are services by default (`resourceAsService = true`); direct access only in unsafe mode | no data races by construction (GOL.004) | CON.010 | 2026-10-23 | files/Concurrency.md 3.6 | ACTIVE (planned) |
| D.073 | The OS scheduler by default; a Fusion scheduler for advanced use | simple first; a custom scheduler for advanced use | CON.008 | 2026-10-23 | files/Concurrency.md 3.6 | ACTIVE (planned) |
| D.074 | Concurrency trap checks are warnings by default; `fusion.toml` can make each an error | a familiar default; a strict project tightens it | CON.001 | 2026-10-23 | files/Concurrency.md 3.6 | ACTIVE (planned) |
| D.075 | The principles P1-P11 govern every concurrency feature | one set of rules keeps every concurrency feature consistent | GOL.004 | 2026-10-23 | files/Concurrency_Traps.md | ACTIVE |
| D.076 | A misspelled setting or a bad value is an error, never ignored; every built setting, its values and default are in `files/fusionSettings.xml`; every setting a finished Fusion will have, tagged, in `files/showcase/fusion.toml` | a typo never silently changes behaviour (D.003) | SET.001 | 2026-10-23 | fusionSettings.xml | ACTIVE |
| D.077 | A thread using two or more resources: they become a **group service** - written by the developer or made by the compiler. It is their temporary owner; its worker borrows them and carries out the requests; when they are done it lets go, and each variable owns its value again. A **service** manages one resource, a **group service** several | locking several resources by hand causes deadlocks | CON.004 | 2026-10-31 | files/Ownership.md 7 | ACTIVE (planned) |
| D.078 | No automatic cycle detection: `Weak<T>` breaks a circle of objects | detection costs time; Weak is written where needed | MEM.005 | 2026-09-13 | spec Memory | ACTIVE (planned) |
| D.079 | `Weak<T>.lock()` gives a `Shared<T>` that is null when the target is gone - the caller checks; never a crash (written without `?` - D.063) | never a crash; the caller decides | MEM.005 | 2026-09-13 | spec Memory | ACTIVE (planned) |
| D.080 | No `.move()`: under OWNERSHIP assigning moves by itself; `byVal` copies, `byRef` borrows. Every object is single-owner by default, so no `Unique<T>` wrapper is needed (replaces Task 12.7's written move) | assigning already moves - nothing extra to write | MEM.002 | 2026-10-31 | files/Ownership.md 2 | ACTIVE (planned) |
| D.081 | Not catchable: running out of memory, a List past 536,870,911 elements - every other failure is an error a program can catch | these cannot be recovered from safely | FUN.002 | 2026-10-16 | spec Errors | ACTIVE |
| D.082 | A cast is written in front: `Shape shp = (Shape)aCircle`; a type it isn't is a compile error where it can be seen, else a CastError; `x is Circle` tests first | familiar from C / Java / C#; an impossible cast found early | TYP.016 | 2026-10-31 | files/taskSummary2.md (32.5) | ACTIVE (planned) |
| D.083 | Favour composition over inheritance: holding an object comes first in docs and examples; inheritance has one parent | composition is easier to change than a deep class tree | CLS.007 | 2026-10-31 | files/Classes.md | ACTIVE |
| D.084 | Inheritance: `override` is required to replace a parent's function, `sealed` stops it, `abstract` allowed, `protected` for the class and its children, `super(...)` / `super.f()` | a parent's function is never replaced by accident | CLS.007 | 2026-10-31 | files/taskSummary2.md (32.7) | ACTIVE |
| D.085 | `Collection<T>`, from Java's: add, remove, length, isEmpty, contains, addAll, removeAll, keepOnly (alias retainAll), clear | familiar from Java; one interface for every collection (D.001) | COL.006 | 2026-10-31 | files/taskSummary2.md (32.4) | ACTIVE (planned) |
| D.086 | A rule that is broken: a compile error wherever it can be seen, else a run-time error | the earlier a broken rule shows, the cheaper it is | GOL.008 | 2026-10-31 | - | ACTIVE |
| D.087 | An interface can build on several: `interface D implements A, B, C` | small interfaces combined into larger ones | CLS.006 | 2026-10-31 | files/taskSummary2.md (32.5) | ACTIVE (planned) |
| D.088 | A copy of an object is usually a new default object with each field set byVal from the original; `Cloneable` and a written `clone()` only for a `nocopy` field | a copy works without writing `clone()` | CLS.008 | 2026-10-31 | files/Object_Lifetime.md 4b | ACTIVE (planned) |
| D.089 | `Iterator<T>`: `bool hasNext()`, `T next()`; a collection gives a new one from `iterator()` for each loop (a loop inside a loop works); `foreach` needs it - for your own classes too | a new iterator per loop: a loop inside a loop works | COL.006 | 2026-11-01 | files/Arrays.md 6 | ACTIVE |
| D.090 | Arrays, Lists and Maps implement Collection<T> and Iterator<T> - each its own implementation: an array's blocks removing an item, a List's / Map's allows it (code to an interface) | code to an interface (D.001); each kind keeps its own rules | COL.006 | 2026-11-01 | files/Arrays.md 6 | ACTIVE (planned - 32.6) |
| D.091 | `Iterator<T>.next()` past the end is not an error for what can be null - an error is for a genuine failure, never to steer a loop; `hasNext()` is the way to check, and Fusion's own code uses it | errors are for failures only; `hasNext()` is the check | COL.006 | 2026-11-01 | files/Arrays.md 6 | ACTIVE |
| D.092 | A Map is a `Collection<Entry<K, V>>` (each entry its key and value); `keys()` and `values()` give its keys and its values as borrowed collections | a Map works with every Collection function | COL.006 | 2026-11-01 | files/Arrays.md 5 | ACTIVE |
| D.093 | Struct fields: a comma is needed between fields on one line; on new lines it isn't needed (ignored if written) | one line reads like a list; new lines need nothing | STC.008 | 2026-11-01 | files/SYNTAX_REFERENCE.md | ACTIVE |
| D.094 | `next()` past the end: null for a string, List, Map, object or enum - whatever the nullable settings say (null = no more items); a primitive (int, double ...): an IndexError saying "check hasNext() first"; written in next()'s documentation and next to the nullable settings | null means "no more" where null is allowed; a primitive has none | COL.006 | 2026-11-01 | files/Arrays.md 6 | ACTIVE |
| D.095 | A Map's `keys()` / `values()` are borrowed views - `Collection<K>` / `Collection<V>` looking into the Map, no copy; removing from one removes the entry, adding gives false; `.toList()` on any Collection gives a copy (replaces keys() / values() as List copies) | no copy - cheap; `.toList()` when a copy is wanted | COL.006 | 2026-11-01 | files/Arrays.md 5 | ACTIVE |
| D.096 | `foreach k in m` gives a Map's keys; `foreach (Entry<K, V> e in m)` each key and value | familiar (keys first); entries when both are needed | COL.005 | 2026-11-01 | files/Arrays.md 5 | ACTIVE |
| D.097 | A struct may hold an object: null until set. Under `[memory] assignment = "move"` the struct moves as a whole (its object with it), `byVal` copies it and clones the object, `byRef` borrows it; under "share" a copied struct shares its object - an object isn't a value. Arrays, Lists and Maps in a struct stay never null | a struct moves as one value; move / byVal / byRef mean the same everywhere | STC.007 | 2026-11-01 | files/Ownership.md 2 | ACTIVE |
| D.098 | Data formats live in fusionlib, not the core: JSON, XML, TOML, YAML, INI, MD read into memory, load / save; JSON and XML may be written in the code as `(FILE_LANG.XML)"""..."""` (form to be designed) | the core stays small; formats change and grow | MOD.009 | 2026-11-01 | files/FutureFeatures.md | ACTIVE |
| D.099 | Hardware testing ideas (from Maia) go in the HIDL library, not the core | the core stays small; hardware testing is a domain library | MOD.010 | 2026-11-01 | files/FutureFeatures.md | ACTIVE |
| D.100 | A function whose body keeps a parameter (stores or returns it) takes it: the call moves the argument, like `list.add`; worked out from the body, shown by `--interface` - no written word | nothing extra to write: the compiler sees it; `--interface` shows it | MEM.003 | 2026-11-01 | files/Ownership.md 2 | ACTIVE |
| D.101 | A local borrow (`Car c = fleet[0]`, `for c in fleet`) freezes its owner until the borrow's last use, not the end of its block | the shortest freeze: code after the last use is free | MEM.003 | 2026-11-01 | files/Ownership.md 2 | ACTIVE |
| D.102 | Task 48 is built with `[memory] assignment = "share"` as the default; the default becomes "move" once tests, examples and the self-hosted compiler are migrated | built without breaking existing code; switched after migrating | MEM.002 | 2026-11-01 | files/taskSummary2.md (48) | ACTIVE (done 2026-11-03) |
| D.103 | A method's `this` is always borrowed: calling `car.register()` never moves `car`. Storing `this` (`cars.add(this)`) shares the object, counted: several collections may hold one car; it is freed when the last holder lets go; an object made in a function and never stored is freed when the function ends | a method call never loses its object; a collection may refer to an object it didn't make | MEM.011 | 2026-11-07 | files/Ownership.md 9 | ACTIVE (planned) |
| D.104 | A cast moves like any assignment - `Circle c = (Circle)first` moves `first` (back to the class too); `byVal` copies, `byRef` borrows | a cast is an assignment - one rule everywhere | MEM.002 | 2026-11-02 | files/Ownership.md 9 | ACTIVE |
| D.105 | Multi-language support (`Lang.<language>.Fusion` modules: migrate or compile other languages) comes after self-hosting (Task 35); the core compiler holds no other language's logic | self-hosting first; the core holds no other language | MOD.011 | 2026-11-03 | files/Fusion_Multi_Language_Compiler_Architecture.md | ACTIVE (planned) |
| D.106 | No `shared` yet: assignment moves, `byVal` copies, `byRef` already shares an object - `shared` waits for a real need | `byRef` already shares; no keyword until a real need | MEM.004 | 2026-11-03 | files/Ownership.md 3 | ACTIVE |
| D.107 | The self-hosted compiler keeps `[memory] assignment = "share"` (selfhost/fusion.toml) until its context handling is reworked for "move" with Task 35 | its context handling relies on sharing until Task 35 | MEM.002 | 2026-11-03 | selfhost/fusion.toml | ACTIVE |
| D.108 | A struct's fields are only borrowed, changed through the borrow, never taken out (D.026 stays); `[memory] moveFieldOut = true` allows it as Rust does - a field leaves a struct the function owns, and the struct can't be used until it gets a new value. Default false | a struct stays whole by default; the Rust way available | STC.001 | 2026-11-03 | files/Ownership.md 2 | ACTIVE |
| D.109 | A function returning a part of its object (`return this.engine`, `this.people[i]`) or of a parameter it borrows lends from it - the result is a borrow of the argument, frozen while used, never stored; so does one returning a new object made with such a part (an iterator holding its collection) | a getter gives its member without copying or losing it | MEM.003 | 2026-11-03 | files/Ownership.md 2 | ACTIVE |
| D.110 | `readonly` on a function's result is part of its signature: the caller gets a read-only borrow; no `readonly` inside that function's body (`return readonly x` an error); `byRef` on its result an error; `byVal` a changeable copy | the signature tells the caller; the class protects its member | FUN.016 | 2026-11-03 | files/showcase/Ownership.fusion | ACTIVE (planned) |
| D.111 | What a function returns: a single object it made moves to the caller; a member fetched from the class is a borrow, changeable unless the signature says `readonly` (D.109, D.110) | made here, nobody else owns it; a member stays the object's | MEM.003 | 2026-11-03 | files/showcase/Ownership.fusion | ACTIVE |
| D.112 | `const` protects the whole object (fields, changing methods), as it does Lists, Maps and structs; a `byVal` copy - also one a method returns - may change | `const` means nothing changes - the same for every kind | MEM.010 | 2026-11-03 | files/showcase/Ownership.fusion | ACTIVE (planned) |
| D.113 | A readonly result may be a member (a read-only borrow), a new object (stays read-only for the caller) or a number (a copy); `readonly` on a copy - a result or `f(readonly n)` - is a warning, not an error | nothing can change a copy; the warning shows the word does nothing | FUN.017 | 2026-11-07 | files/Ownership.md | ACTIVE (planned) |
| D.114 | An interface's functions are public or internal; `private` on one is a compile error | private defeats the purpose of an interface | CLS.019 | 2026-11-07 | files/Classes.md | ACTIVE (planned) |
| D.115 | `--interface` shows a module's public and internal functions, never private ones | it shows what other modules may use | MOD.002 | 2026-11-07 | files/Ownership.md 8 | ACTIVE (planned) |
| D.116 | A `?.` comparison is false on null and gives a warning; `!` around one is a compile error (a `[conditions]` setting allows it, then a warning); null is handled on its own: `if x is null ... else if ...` | null is neither true nor false - `!` would turn "unknown" into "yes" | NUL.005 | 2026-11-07 | files/Nullable_Values.md 5 | ACTIVE (planned) |
| D.117 | The compiler checks an object is made before it is used: passing one that is surely null is a compile error; a parameter marked `?` without a null check warns; a `Default` type is never null - one left null and not made again is a compile error | NullErrors found at compile time (D.086) | NUL.006 | 2026-11-07 | files/Nullable_Values.md | ACTIVE (planned) |
| D.118 | An RTOS (FreeRTOS, Zephyr) gets no layer of its own: the IO standard library covers what exists there, HIDL creates the tasks and timers | keeps the standard library one; hardware detail in HIDL | MOD.010 | 2026-11-07 | files/FEATURES.md 41 | ACTIVE |
| D.119 | Form D: `{ }` on an abstract class or an interface makes a class right there; written like form B (fields and functions together) or with `implements { }`; may set up consts; its functions use the variables around them - so it comes after closures | set up and implement in one place, without a separate class | CLS.016 | 2026-11-07 | files/FEATURES.md 52.1 | ACTIVE (planned) |
| D.120 | A failing operation: Fusion undoes what can be undone (default); the developer handles the error (try / catch / finally, or an Error returned); not handled, it bubbles up to the caller after the undo. A `Transaction` interface marks a call that commits (OK / FAILED) or rolls back - to be designed | the caller knows a transaction completed, or that nothing changed | CON.020 | 2026-11-07 | files/Service.md group rule 7 | ACTIVE (planned) |
| D.121 | Language modules are imported as `import Lang.Python.Fusion` | its own top-level name, apart from fusionlib | MOD.011 | 2026-11-07 | files/Fusion_Multi_Language_Compiler_Architecture.md | ACTIVE (planned) |
| D.122 | Nothing is trusted by default: a library is checked by its signature; one without source is sandboxed (no files / network) unless the developer trusts it (to run fast); the customer running the app may still forbid files / network | never trust code (GOL.008); the customer may not trust the developer's app | MOD.004 | 2026-11-07 | files/FEATURES.md 39 | ACTIVE (planned) |
| D.123 | While a borrow changes a value (`Car c = fleet[0]`), its owner may still be read (`fleet.length()`); only changing it another way (`fleet[0] = ..`) is an error - unlike Rust | reading can't break the borrow; one writer is enough | MEM.012 | 2026-11-07 | files/Ownership.md R4 | ACTIVE (planned - changes 48.2) |
| D.124 | Each borrow rule has its own setting: one owner (`[memory] assignment`), one writer, a borrow never outlives its owner - names decided when built | a project may loosen each rule on its own | MEM.013 | 2026-11-07 | files/Ownership.md | ACTIVE (planned) |
