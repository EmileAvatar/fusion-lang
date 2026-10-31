# Fusion - Decisions

The single list of what Fusion is and what has been decided. Keep it small: one line per
feature, one row per decision. Only the **latest** decision on a subject is kept; an older
one is removed when replaced (its history is in git and the design document named). Language
features only - no bug fixes, no discussions.

- **Section 1** - every feature, one line each: `AREA.NNN [STATUS] description`
- **Section 2** - the decisions behind them, in a table; a clash between two is marked `CLASH`
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

#### TYP - types
TYP.001 [BUILT] int, float, double, bool, char, byte - overflow checked; `[numbers] overflowWrap` wraps
TYP.002 [PLANNED] `long`, `short` (47.1)
TYP.003 [PLANNED] `money`: a long of minor units, exact, never a float (47.2)
TYP.004 [BUILT] Enums; enums with data (tagged unions); an unset enum is null
TYP.005 [PLANNED] Enums whose values carry fixed data (47.3); the `FusionType` enum (47.4)
TYP.006 [PLANNED] The `fixed` prefix: a maximum size - `fixed string(16)`, `fixed List<T>(n)` (47.5)
TYP.007 [PLANNED] Generics: the program's own generic functions and types (Task 33)
TYP.008 [DESIGN] Operator overloading - only for exceptional cases (a setting, off)

#### STR - strings
STR.001 [BUILT] Strings are values, freed automatically; changed in place (`s[i] = c`)
STR.002 [BUILT] Interpolation `"{x}"`, `{@N}` placeholders, `template string`
STR.003 [BUILT] Unicode: characters vs bytes; `bytes` for raw data
STR.004 [BUILT] The string library: search, extract, change, pad, number bases, format
STR.005 [POSTPONED] String pooling (29.4); secure strings (29.5); StringBuilder (Task 38)
STR.006 [REJECTED] A "mutable" switch - a string can always be changed in place

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

#### FUN - functions and errors
FUN.001 [BUILT] `T, Error function`: an error returned as the last value
FUN.002 [BUILT] `try` / `catch` / `finally` / `throw`; custom error types
FUN.003 [BUILT] `readonly` parameters: never changed, deeply - worked out through the calls
FUN.004 [PLANNED] `readonly` / `byVal` / `byRef` written at the call (48.3)
FUN.005 [PLANNED] Several return values per function beyond the Error (`[functions] multipleReturns`, off)
FUN.006 [BUILT] Files, program arguments, console input, `exit`, `run` (another program)

#### NUL - null
NUL.001 [BUILT] Value types are never null; class objects and enums can be
NUL.002 [BUILT] A null without a check is a NullError a `catch` can handle; `null == null` is true
NUL.003 [PLANNED] `?.`, `?.null`, `??`, `case null` (Task 30.2)

#### STC - structs
STC.001 [BUILT] Structs: value types, copied, never null; may hold Lists, Maps, strings
STC.002 [BUILT] Methods on structs (`[structs] functions`, default off)
STC.003 [BUILT] A struct building on a struct (`implements` / `extends` / `includes`)
STC.004 [BUILT] A struct as text: `"{e}"` -> `name : "Jeff",age : 30`
STC.005 [REJECTED] A struct implementing an interface - a struct only holds values

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

#### MOD - modules
MOD.001 [BUILT] Modules and `import` (a folder = a module); module variables and constants
MOD.002 [BUILT] `--interface`: the public interface of the imported modules
MOD.003 [POSTPONED] A Fusion library other programs load (`.dll` / `.so`) - needs `extern`
MOD.004 [DESIGN] Library trust: capability signatures, sandboxing, supply-chain checks (Task 39)

#### MEM - memory and ownership
MEM.001 [BUILT] OWNERSHIP: scope plus counting; a returned local is moved
MEM.002 [PLANNED] Assigning moves: `Car b = a` leaves `a` unusable; `byVal` copies (48.1)
MEM.003 [PLANNED] Passing and reading an element borrow; a borrow is never stored (48.2)
MEM.004 [PLANNED] `shared`: read only except to the holder that made it shared (48.5)
MEM.005 [DESIGN] GC and MANUAL as project strategies; Unique / Shared / Weak (Task 38)
MEM.006 [DESIGN] `unsafe` blocks; `free` / `deallocate`
MEM.007 [BUILT] The leak check: every example and test

#### CON - concurrency
CON.001 [PLANNED] `service`: shared state with one owner (reserved keyword); version one (42.0-42.2)
CON.002 [PLANNED] One writer: the service's worker; readers in parallel (42.18)
CON.003 [PLANNED] Temporary services when two or more threads use one variable (42.19)
CON.004 [PLANNED] Several variables, each its own service; a fixed order (42.20)
CON.005 [PLANNED] A `Service` interface: BasicService, SharedService, FileService, DatabaseService, HotPathService (42.21)
CON.006 [PLANNED] send / sync worked out at the thread boundary (42.22)
CON.007 [PLANNED] `hotpath` functions and `hotpath service` (42.23-42.24)
CON.008 [DESIGN] Group services, service classes, the Thread class, schedulers (42.3-42.9)
CON.009 [POSTPONED] Cluster threads over several servers

#### SET - settings and tools
SET.001 [BUILT] `fusion.toml` (or .yaml / .json / .ini); camelCase, read case-insensitively; a bad key is an error
SET.002 [BUILT] `[safety] mode` = safe / strict / unsafe
SET.003 [PLANNED] Core modules: Time, Data formats, Currency (Task 43)
SET.004 [PLANNED] Syntax highlighting (36.0), later a language server (Task 36)
SET.005 [PLANNED] An LLVM backend and an IR layer (Task 40); HIDL for hardware (Task 41)
SET.006 [REJECTED] Fetching prices or exchange rates from an external API - in the core or any module

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
| D.020 | `fixed`: a maximum - lower fine, higher an error; starts empty, memory reserved once | TYP.006 | 2026-10-31 | Arrays.md | ACTIVE (planned) |
| D.021 | `money` is a long of minor units; the Currency module enforces each currency's steps | TYP.003 | 2026-10-29 | FEATURES 47.2 | ACTIVE (planned) |
| D.022 | The core and every module never fetch prices or rates; the developer passes them in | SET.006 | 2026-10-29 | CLAUDE.md | ACTIVE |
| D.023 | Settings named in camelCase, read case-insensitively, `_` ignored | SET.001 | 2026-10-28 | fusionSettings.xml | ACTIVE |
| D.024 | `service` is a reserved keyword | CON.001 | 2026-10-29 | Service.md | ACTIVE |
| C.001 | **CLASH:** 45.10 says arrays become references "shared in normal code, like Lists"; D.014 makes Lists move | COL.002 | - | FEATURES 45.10, Ownership.md | CLASH - check |
| C.002 | **CLASH:** a struct is copied with its Lists today (32.10a, built); Task 48 moves a struct holding a List as a whole | STC.001 | - | Arrays.md 1, Ownership.md 2 | CLASH - check (48 replaces it when built?) |
| C.003 | **CLASH:** `[memory] strategy = "smart"` (showcase) and "start with automatic GC" (spec) vs D.013 OWNERSHIP first | MEM.005 | - | spec Memory, showcase toml | CLASH - check |
| C.004 | **CLASH:** shared changeable data across threads "a warning by default" (Concurrency.md section 4) vs D.017 a temporary service | CON.003 | - | Concurrency.md | CLASH - check |
