# Fusion - Feature Tree

What Fusion has, and what it still needs, at a glance. Kept simple - one line per feature.
Detail: `Decisions.md` (every feature line and decision), `files/FEATURES.md` (tasks and status),
`files/SYNTAX_REFERENCE.md` (examples of what works).

Updated: 2026-11-25

Tags: **[partial]** some of it built - **[planned]** decided, scheduled as a task - **[design]** described,
not settled - **[postponed]** waits for something else

## Implemented

```
Core
   - Compiler                 Fusion -> C -> native .exe via GCC (compiler in Python)
   - Settings per project     fusion.toml / .yaml / .json / .ini; features become settings with safe defaults
   - Safety modes             [safety] mode = safe / strict / unsafe
   - Self-host test run       lexer, parser, checker, C generator written in Fusion (tier 1)
   - Never trust code         a library is checked by what its signature promises

Syntax
   - Block styles             indentation, braces, or End if - one meaning
   - Functions                void function main(); one-line body after ':'; default params; named args
   - Any number of values     int... numbers - values one by one, an array or a List; a List inside
   - Lambdas                  function values; func(int x) : x * 2
   - Control flow             if / while / for / for i in range(a, b, step); numbers as conditions
   - Ranges                   for i in 1...10 (both ends); 0...13 step 5, 10...0 step -2; case 0...9 in a match
   - Decimal / money ranges   0.0...1.0 step 0.1 - start + n * step, no drift; decimal and money exact; case 0.0...0.49
                              on a double; behind [ranges] decimals
   - Conditional              (cond) ? a : b
   - match                    match, fall match, match as a value, _ for unused fields
   - let / var                type from the value; let set once
   - Operators                = == != === !== <>; and / or / not; hex / binary / octal numbers
   - Method form              name.toUpper() is String.toUpper(name); works for your own functions
   - len / length             with or without brackets
   - Form B set-up blocks     a block right after a value, on any variable, field or static
   - Type tests               if s is string; typeOf(x)
   - unchecked { }            whole-number math wraps on purpose
   - Comments                 // and /* */
   - Line continuation        a line break inside ( ) or [ ]
   - ASCII identifiers        Trojan Source / look-alike letters rejected
   - Case sensitivity         [source] caseSensitive; names differing only by case an error when off
   - Shadowing                [source] shadowing - off: a name used further out an error; on: the nearest, ::name, this.name
   - Reserved words           keywords + words kept for future features, with a clear error

Types
   - Numbers                  int, long, short, int128, int256, decimal, float, double, bool, char, byte - overflow checked, overflowWrap setting
   - Money                    money (16 bytes: value, scale, currency, symbol) and the Currency module - every ISO 4217 currency
   - int as float             only when it fits exactly, else an error
   - Conversions              toInt, toFloat, toString, toByte, parseInt
   - Enums                    plain and with data (tagged unions); values(), fromString(); written Status.OK, case OK in a match
   - Enums as value structs   fields (EARTH.mass), ids (200, OK), constructor, methods, toString, fromValue - static, never on the heap
   - Generics                 functions, structs, classes; conditions (extends / : / Number / int / implements);
                              T... items - of one type, or a pack show(1, "two", car);
                              types from the left - Garage<Car> g = Garage(); a parent / interfaces (Box<T>, Collection<T>); statics per copy

Strings
   - Strings as values        freed automatically; changed in place s[i] = c
   - Interpolation            "{x}", {@N}, template string
   - Unicode                  characters vs bytes; bytes type for raw data
   - String library           search, extract, change, pad, number bases, format
   - const string             an unchangeable string

Collections
   - Arrays                   fixed size, bounds always checked; acts as an Array object (a.length)
   - Multi-dimension arrays   up to 3D; views cube[1]; foreach; walk orders; jagged rows
   - List<T>, Map<K, V>       never null, counted references; byVal copies, byRef shares
   - foreach                  over arrays, Lists, Maps, your own Collection<T> class
   - Collection<T>            classes, Lists, Maps and arrays (removing blocked on an array)
   - Collection options       noDuplicates, noNull, readOnly
   - toList, toCSV            on arrays, Lists, structs

Functions & errors
   - Error returns            T, Error function - error as last value
   - Exceptions               try / catch / finally / throw; custom error types; built-in error tree
   - readonly parameters      never changed, deeply, checked through calls
   - readonly results         readonly Engine function getEngine()
   - Built-ins                96 functions, 16 List and 7 Map methods (files/Builtins.md)
   - Files, args, console     read/write files, program arguments, input, exit, run
   - Recursion guard          endless recursion is a catchable StackOverflowError
   - Wrapping on purpose      wrapAdd / wrapSub / wrapMul

Null safety
   - Values never null        strings, arrays, Lists, Maps, structs never null
   - NullError                an unchecked null is catchable
   - Null guard               ?. , ?.null, ??, case null
   - Made-before-used check   a surely-null object passed is a compile error

Structs
   - Structs                  value types, copied, may hold Lists / Maps / strings / objects
   - Methods on structs       behind [structs] functions
   - Struct inheritance       implements / extends / includes
   - Struct as text           "{e}" -> name : "Jeff",age : 30

Classes
   - Classes                  objects by reference, counted, freed at last holder
   - Constructors             several; this(...); new optional
   - Statics                  three set-up forms, run before main
   - Visibility               private / internal / public / protected; namespace A.B
   - Interfaces               several, building on others, as a type, is, casts, default methods
   - Inheritance              one parent, override, sealed, abstract, super
   - Default / ToString       implements Default (never null), implements ToString
   - Copying rules            nocopy / noshare fields, Cloneable
   - Leak warning             a warning for each circle of classes that could leak

Modules
   - import                   a folder = a module; module variables and constants
   - --interface              shows the public interface of imported modules

Memory
   - OWNERSHIP                scope + counting; returned local moved
   - Moves and borrows        Car b = a moves; borrows never stored; [memory] ownership strict / relaxed
   - const objects            deep - no field or changing method
   - Shared this              one object in several collections, freed when the last lets go
   - Leak check               every example and test

Settings
   - Built                    [build] waitAtExit, --headless; [indentation]; [stdlib] layer std / alloc / core;
                              [strings] maxLength, encoding; [structs] limits; [backend] target = "c";
                              [generics] enabled, sharedStatics; [ranges] strictStep, decimals, stepRequired,
                              defaultStep, rangeMaxStep

Tooling
   - Syntax highlighting      VS Code and Sublime Text - one grammar from the lexer's keywords (Task 36.0)
   - Colour themes            Fusion Dark / Light and colour-blind safe ones, one colours file (36.8)
```

## Partly implemented

```
   - Agnostic language        safety + memory settings built; concurrency + backend choice not yet
   - Memory safety            ownership built; some readonly / library parts left
   - ... operator             string... args, int... numbers, T..., ranges 1...10 built; spread [...a] to do
   - Casts                    (Shape)aCircle built; some number casts left
   - Arrays in three forms    plain, fixed, growable - RECT storage later
   - Large arrays             stack limits built; buffers (RING etc.) after self-hosting
   - readonly at the call     built; library rows wait for Task 39
```

## Still to be implemented

```
Core goals
   - Self-hosting [planned]          the Fusion-written compiler compiles itself; Python retired (Task 35)
   - Million requests [design]       no data races, no deadlocks, small footprint (Task 42)
   - Rename [planned]                before 1.0 (CoreFusion / FusionCore / MaiaFusion)

Concurrency (Task 42) - nothing built yet
   - service keyword [planned]       one owner, one writer, readers in parallel
   - Temporary + group services [planned]   made by the compiler when threads share resources
   - Service interface [planned]     BasicService, SharedService, FileService, DatabaseService, HotPathService
   - send / sync checks [planned]    at the thread boundary
   - hotpath [planned]               hotpath functions and services
   - How a service runs [planned]    plain variable / atomics / mailbox with workers
   - Calls + timeouts [planned]      wait in order, async, completed / failed / timed out / cancelled
   - service(x).run { } [planned]    several steps as one
   - Service settings [planned]      Mailbox, Timeout, Scheduler, Priority, ThreadPool ...
   - Thread hierarchy [planned]      IDs, parents, who gets a resource
   - Trap checks [planned]           warnings by default, errors when set
   - Resources as services [planned] files, sockets, databases; final clean-up
   - Transactions [design]           commit / rollback interface
   - Channels [design]               mailbox, named, interrupt, outbound
   - Thread kinds [design]           worker, writer, reader, watcher, scheduler ...
   - Sleep / wake [design]           parent wakes worker via its channel
   - Interrupts [design]             from the OS, passed down; handlers per service
   - Locks [design]                  off by default, only in unsafe
   - Split resources [design]        a database split by table, one writer each
   - async / await, go f(x) [design]
   - Machine-fit defaults [design]   default settings and timeouts per resource
   - Cluster threads [postponed]     over several servers

Syntax
   - Duration literals [planned]     500ms, 5s, 2min
   - switch / elif aliases [design]
   - loop { } [design]               must have break / return; check blocks; labels; iteration limit
   - ++ / -- [design]                statements only
   - if as a value, do-while [design]
   - Match guards [design]           case x if x < 0
   - assert [design]
   - Extension methods, overloading [design]
   - Copy with changes, tuples [design]   a with { x = 5 }
   - Evaluation order [design]       operands in written order
   - ** power, @annotations [design]
   - #Region, doc comments [design]
   - ''' comment blocks, comment levels [design]
   - Semicolons, other languages' syntax [design]
   - Minimum name length [design]    in strict mode
   - Closures, nested named lambdas [postponed]
   - ' comments (VB) [postponed]

Types
   - FusionType enum [planned]
   - fixed(n) [planned]              max size: fixed(10) string name
   - Operator overloading [design]   a setting, off
   - Flag enums [design]             Read | Write
   - Autoboxing [design]             (42).toString()
   - bit type [design]
   - Built-in methods through internal interfaces [design]

Strings
   - Raw / multi-line strings, {value:pattern} [design]
   - String pooling, secure strings, StringBuilder [postponed]
   - Full expressions in {...}, Unicode case / normalization, Base64 / JSON escaping, regex [postponed]
   - Paged / memory-mapped strings [postponed]

Collections
   - Set<T>, slices numbers[0...1], Map literals [design]
   - Collections module [planned]    RingBuffer first
   - List capacity, growth buffer, kept sort order [planned]
   - Map add(otherMap), custom hashing [planned]

Functions & errors
   - Multiple return values [planned]   [functions] multipleReturns
   - ? after a call, await all [design]
   - extern "C" [design]             call a C function by declaring it
   - Stack traces [design]           every error carries one
   - More error types [postponed]    Network, Timeout, Parse, ... with each feature

Classes
   - Properties [design]             property Name: type { get; set; }
   - Constants always static [design]
   - virtual [design]                reserved, not used
   - Builder pattern [postponed]
   - Form D (anonymous class) [postponed]
   - private on top-level items [postponed]

Modules & libraries
   - Shared libraries .dll / .so [postponed]
   - Library trust / sandbox [design]
   - Partial imports, [modules] paths, grouped imports [design]
   - Other code: DLLs, assembly, outside compilers [design]
   - Callbacks and events [design]
   - Data formats module [design]    JSON, XML, TOML, YAML, INI, MD
   - HIDL library [design]           hardware testing, Maia-style
   - Language modules [design]       import Lang.Python.Fusion
   - Namespaces as supplier groups [design]
   - Script libraries [design]       Lua / JS / Fusion scripts through interfaces

Memory
   - shared [postponed]              read-only except to its holder
   - GC / MANUAL strategies, Shared<T> / Weak<T> [design]
   - unsafe blocks, free [design]
   - copy(x) / copyDeep(x) [planned]
   - Arenas / regions, memory-mapped resources [design]
   - FSMA [research]                 the heap as Data Stacks with a purpose; FULL / STATIC / REGISTER-ONLY (R11)

Settings & tooling
   - Core modules [planned]          Time, Data formats, Currency (Task 43)
   - Language server [planned]       errors as you type, go to definition (Task 36.5); a .fusion file icon
   - LLVM backend, IR layer [planned]   (Task 40); HIDL for hardware (Task 41)
   - Enforce [safety] / [backend] [planned]
   - Errors for tools / AI [planned]    fix: hints; --errors json
   - blockStyles, build mode, lineEnding [design]
   - [project], [build], [backend] platform [design]
   - [threads] enabled [design]
   - Strict-mode extras [design]
   - Build kinds [design]            script mode, JIT, library, WebAssembly
   - fusionlib modules [design]      file formats, images, math, networking, graphics, audio
   - Tools [design]                  formatter, debugger protocol, hot reload, bytecode VM
   - IDE module [design]
   - config.fusion writes settings [postponed]
   - One console tool build / run / test [postponed]
   - Precepts [postponed]            ready-made settings so a project behaves like C, Java, Python
```

## Rejected (decided against)

```
   - I prefix on interfaces; a "mutable" string switch; T? nullable types
   - Turning off array bounds checks; changing a collection while looping over it
   - type() arrays (use const / fixed); a struct implementing an interface
   - Fetching prices / exchange rates from an external API
```
