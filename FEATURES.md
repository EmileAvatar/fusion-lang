# Fusion - Feature and Task Status

The single place to see what is done, open, or postponed. One line per item.

- `[ ]` open · `[DONE]` finished · `[POSTPONED to X]` waits for X (a task, or a missing feature)
- `##` = major sections only. Tasks: `#### NN Title [status]`. Sub-tasks: one tab +
  `[status] NN.N`. Parts: two tabs
- Sections: Done (a pointer to task/featuresArchive.md), Phase 1 (up to the self-hosting
  test run), Phase 2, Phase 3, Later, Known limitations, Old task numbers (open tasks were
  renumbered from 25 on 2026-10-11)
- Only open and postponed items are kept here; a finished one moves to
  `task/featuresArchive.md` when its task is complete
- Find things: `grep -n "\[ \]" FEATURES.md` (open), `grep -n "POSTPONED" FEATURES.md`,
  `grep -rn "18\.3\.2" FEATURES.md taskSummary2.md task/` (one item everywhere)
- Detail: active task -> `taskSummary2.md`; finished -> `task/taskSummaryArchive.md`;
  not started -> `task/taskBacklog.md`. What the language can do today, with examples ->
  `SYNTAX_REFERENCE.md`

**Features become settings (user, 2026-10-24).** Each feature is designed so a project can
turn it on or off in `fusion.toml` where that makes sense, with a safe default. When an item
here is reviewed (for example the showcase [idea] list), decide whether it becomes a
setting, a fixed rule, or is discarded. Example - structs:
- a struct is a value type, never null: it always has a value;
- it may hold empty or filled `List`, `Map`, `string` (a setting, on by default since it is
  built);
- functions on structs: a setting, off by default;
- classes inside structs: a setting, off by default.

---

## Done

Every finished task and item is in `task/featuresArchive.md` (archived 2026-10-27 - this file
keeps only what is open or postponed). Finished tasks keep their numbers; their plans and
notes are in `task/taskSummaryArchive.md`.

---

## Phase 1 - up to the self-hosting test run

First major goal (user, 2026-10-11): a **simple working self-host** - a compiler written in
Fusion, covering only the simple part of the language, whose exe compiles the programs in
`examples/` by itself. A test run: the Python compiler stays the real compiler until the
self-hosted one is fully independent (Phase 2). Guide: `Notes/04/notes.md` section 5.

**Phase 1 is complete (2026-10-26):** Tasks 25 (enums), 26 (errors), 27 (the semantic contract
and safety), 28 (the self-hosting test run - report: `task/selfhost_report.md`). Their lines
are in `task/featuresArchive.md`.

---

## Phase 2 - growing the language, then a fully independent compiler

#### 29 Strings - the postponed parts (29.0-29.3, 29.6 done 2026-10-27: task/featuresArchive.md) [POSTPONED]
	[POSTPONED to 38] 29.4 String pooling: `[strings] pooling` (default off) and `pool(s)` -
		needs a reference count, as Task 38's Shared does (`[structs] string_storage =
		"pooled"` waits for this)
	[POSTPONED - needs fusionlib.Crypto] 29.5 Secure string storage, constant-time comparison

#### 30 Nulls, empty values, number conditions, the conditional operator (was 14) [ ]
	Design: Nullable_Values.md and spec "Null Handling" (user decisions 2026-10-27). Only class
	objects can be null, so the null guard itself waits for classes (Task 32); what doesn't
	need classes is built now.
	[DONE] 30.0 Bug (found 2026-10-27): `int numbers[]` was read silently as a plain int and an
		empty list, and `int x = 5 print(x)` as two statements - a statement must now end its
		line (or block); the C-style array form gives a clear error until 30.10
		(tests/test_statement_end.py)
	[DONE] 30.1 The model decided (user, 2026-10-27): only class objects can be null; strings,
		arrays, List, Map never null (empty by default); `?.` guard, `??`, checks, number
		conditions - Nullable_Values.md, spec "Null Handling"
	[POSTPONED to 45] 30.10 Empty arrays: `int[] numbers` and `int numbers[]` both declare an
		empty array, length 0 (user, 2026-10-27) - only useful once arrays can grow
	[DONE] 30.8 `.len` and `.length`, with or without brackets, on strings, bytes, arrays, lists
		and maps - the same as len(x); a struct field or the program's own function of that
		name comes first (tests/test_length_sugar.py)
	[DONE] 30.7 The conditional operator `(condition) ? a : b` - one line, gives a value; only
		the chosen value runs; strings always fresh (tests/test_conditional_operator.py)
	[DONE] 30.9 Numbers as conditions: `[conditions] numbers` = "positive" (default - zero and
		negatives false) / "nonzero" / "off" (user, 2026-10-27). Only in `if` / `while`
		conditions (and / or / not inside them); `count == true` follows the setting,
		`count === true` is false, `bool b = count` is always an error
		(tests/test_number_conditions.py)
	[ ] 30.6 Docs & examples (SYNTAX_REFERENCE, spec status lines)
	[POSTPONED to 32] 30.2 On class objects: the `?.` guard (not run on null, false in an `if`),
		`??`, `x?.null` / `!x?.null`, `== null` / `=== null` / `is null`, NullError for a plain
		`.` on null (was 30.1b), the two warnings (Nullable_Values.md section 5)
	[POSTPONED to 32] 30.3 `nullable` settings for strings / arrays / lists / maps (default
		false) and `?.length()` giving -1 on a null one - only useful with 30.2

#### 45 Arrays that grow at the end (user, 2026-10-27 - Arrays.md) [ ]
	Today an array's size is fixed when it is made, and the compiler must know it. An array
	will grow and shrink at its end only (an item never moves position); a List changes
	anywhere.
	[ ] 45.1 Each array knows its own length at run time (like a List), so an array can be
		replaced by one of another size (`numbers = make()`, `numbers = [1, 2, 3]`)
	[ ] 45.2 Empty arrays: `int[] numbers` and `int numbers[]` (was 30.10)
	[ ] 45.3 Grow and shrink at the end: `numbers.add(4)`, `numbers.removeLast()` (`pop()` as
		quick typing) - user, 2026-10-27
	[ ] 45.4 Combine arrays: `a + b + c + d` - a new array, each one's items in turn; all of
		the same type (user, 2026-10-27). Lists the same. Maps use `add(otherMap)` instead
		(see Later: "Map keys")
	[ ] 45.5 Copying a part: `copyPart(start, count)` / `copyPartAt(start, end)` (`slice` /
		`sliceAt` as quick typing) - the same rules as List (see Later: "List slice")
	[ ] 45.9 `foreach (string item in names)` over arrays, lists and maps - the item's type is
		the collection's; adding / removing that collection inside is a compile error;
		`continue` / `break` allowed (user, 2026-10-27)
	[ ] 45.7 Changing an array while looping over it is allowed: the loop sees the new length
		(user, 2026-10-27) - no temporary copy needed
	[ ] 45.8 Adding / removing at the end is thread-safe by itself (an atomic lock) - with
		Task 42 (user, 2026-10-27)
	[ ] 45.6 Docs and examples: Arrays.md, SYNTAX_REFERENCE, spec "Arrays"

#### 31 Config file in any format: fusion.toml / .yaml / .json / .ini (was 20) [ ]
	[ ] 31.1 One loader per format, one shared schema
	[ ] 31.2 Discovery and ambiguity (two config files = error)
	[ ] 31.3 Tests
	[ ] 31.4 Docs
	[ ] 31.5 Enforce fusion.toml [safety] / [backend] (was 15.6; trigger: strict mode or a 2nd backend)

#### 32 Methods on structs, then classes and interfaces (user, 2026-10-11) [ ]
	[ ] 32.1 Methods on the program's own structs (`p.move(1, 2)`) - built-in types have them (18.3.7);
		also 44.2
	[ ] 32.2 Classes, interfaces, inheritance - plan first
		Passing (user, 2026-10-26, as in VB.NET): value types (primitives, structs) by value - a
		copy; objects (class instances) by reference. Until classes exist, everything is a copy
		User decisions (2026-10-23, showcase review): `inherits`, with `extends` as an alias;
		interface names need no I prefix; several constructors per class; a constructor may
		call another (private ones too) with this(...); constructors calling each other in a
		circle are a compile error
	[ ] 32.4 A `Collection` interface (user, 2026-10-27 - Arrays.md section 6): arrays, lists and
		maps implement it; `foreach` works on any class that does, and the class decides its
		own rules (adding / removing while looping, threads, special actions)
	[ ] 32.3 Example (was 16.2: classes, interfaces & enums)

#### 33 Generics: the program's own generic functions and types (user, 2026-10-11) [ ]
	[ ] 33.1 Plan (List<T> / Map<K, V> are built in since 18.5)
	[ ] 33.2 Example (was 16.3)

#### 34 Example program coverage (was 16) [ ]
	[POSTPONED - needs threading, no task yet] 34.1 Multithreading / async example (was 16.4)
	[POSTPONED to 38] 34.2 Memory model (Unique/Shared/Weak) example (was 16.6)

#### 35 Self-hosting phase 2 - fully independent (was 10.9-10.12) [ ]
	[ ] 35.1 The self-hosted compiler covers the whole language
	[ ] 35.2 Bootstrap twice: the compiler compiles itself, and that one compiles itself again
	[ ] 35.3 The whole test suite runs against it
	[ ] 35.4 Performance
	[ ] 35.5 The Python compiler retired; docs

---

## Phase 3 - the advanced parts

#### 36 Editor support: syntax highlighting for code editors and IDEs (was 24) [ ]
	(user request 2026-10-11 - after self-hosting, when the syntax has settled)
	[ ] 36.1 One shared TextMate grammar (fusion.tmLanguage) - VS Code, Sublime Text, JetBrains
		IDEs (TextMate bundles), Atom-family editors and GitHub all read this format
	[ ] 36.2 VS Code extension: the grammar, `.fusion` file icon, comment / bracket / indent rules
	[ ] 36.3 Sublime Text package
	[ ] 36.4 Others as needed: Notepad++ (user-defined language), Vim / Neovim, tree-sitter grammar
	[ ] 36.6 Later: a thread view - a "stack of threads" (what each thread does, which variables
		and files / sockets / databases it touches), profiling, graphs and heat maps
		(user, 2026-10-23; Concurrency.md section 3.3 H - design later)
	[ ] 36.5 Later: a language server (LSP) - errors as you type, go to definition, completion -
		built on the self-hosted compiler, one server for every editor
	[ ] 36.7 A hint showing how number conditions are set for the project (`[conditions]
		numbers`, Task 30.9) - e.g. on `if count` (user, 2026-10-27)

#### 37 Deferred decisions (rest of 15 - user: after self-hosting, some become own sub-tasks) [ ]
	[ ] 37.1 Stdlib runtime lowering decision (was 15.2)
	[ ] 37.2 Operator operands evaluated in C's order (`next(c) - next(c)`); call arguments are
		left-to-right already (was 15.12)
	[ ] 37.3 Incremental builds, stable symbol identities (ChatGPT review; notes.md step 5)

#### 38 Memory model: Unique / Shared / Weak, GC as a project option (was 15.5) [ ]
	[ ] 38.1 Scope it (semantics decided in 12.7, not built)

#### 39 Library trust, isolation & security (was 19) [ ]
	[ ] 39.1 Compiler-verified capability signatures (was 19.1; layers from 18.5.6 are the groundwork)
	[ ] 39.2 Project restrictions (pragma Restrictions-style) (was 19.2)
	[ ] 39.3 Closed, compiled, licensed libraries (was 19.3)
	[ ] 39.4 Sandboxing and resource budgets (was 19.4)
	[ ] 39.5 Supply-chain security (was 19.5)
	[POSTPONED - needs fusionlib.AI] 39.6 AI module input guard (was 19.7)

#### 40 IR layer and LLVM backend (was 11, 15.1) [ ]
	[ ] 40.1 IR layer decision (was 15.1) - the IR expresses Fusion's meaning; the C and LLVM
		backends only translate it (ChatGPT review)
	[ ] 40.2-40.13 Environment, IR generator, types, functions, codegen, strings, stdlib,
		optimization, tests, docs (was 11.2-11.13)

#### 41 HIDL - hardware interface definition language (was 13) [ ]
	Note (user, 2026-10-24): the [stdlib] layers map to hardware - core: microcontrollers with
	no heap, bare metal (Arduino AVR, Cortex-M0; 2-64 KB RAM); alloc: microcontrollers /
	microprocessors with a heap, no OS or a small RTOS (ESP32, Cortex-M4/M7, STM32); std: a
	full OS (PCs, servers, Raspberry Pi on Linux). Open: an RTOS (FreeRTOS, Zephyr) has
	threads and timers but usually no files or console - its own layer, or optional std parts
	[ ] 41.1 Grammar & format decision
	[ ] 41.2 Scope v1 vs. future layers
	[ ] 41.3 Memory model reconciliation
	[ ] 41.4 HIDL parser
	[ ] 41.5 Fusion code generation from HIDL
	[ ] 41.6 Compile-time hardware safety checks
	[ ] 41.7 Multi-language code generation (stretch)
	[ ] 41.8 Simulator & tooling (stretch)
	[ ] 41.9 Docs & examples

#### 42 Concurrency: services and threads (user, 2026-10-23) [ ]
	Goal: a million requests on one machine with many cores - no data races by construction,
	deadlocks and freezes prevented by rules (any that slip through become clear errors), no
	slowdown, a small memory / CPU footprint, very scalable. A resource becomes a service;
	manual locking is a last resort. Design: Concurrency.md (sections 3-4); overview:
	Concurrency_Traps.md. Plan first when the task starts.
	[ ] 42.0 Version one (agreed 2026-10-24, Concurrency.md 3.11): five rules - one owner,
		each operation one step, copies out, handles shared; the compiler picks plain variable
		/ atomic / mailbox on a shared pool (never a thread per service); waits in order,
		`async` to not wait, not re-entrant by default; `service(x).run { }` for several steps;
		a timeout = the caller stopped waiting. Created only by a parent thread, outside loops
		(class field or function variable); a warning when no other thread uses it.
		Contextual keyword. Settings v1: Mailbox, WhenFull, Timeout, final. Roadmap phases
		1-5 and the 8 first tests in 3.11; a prototype measuring cost first
	[ ] 42.1 `service` keyword: `service <type> <name>` makes a variable, struct or class object
		a service with Fusion's default thread settings (`service int counter = 0`,
		`service Person person = ...`, `service Car honda = Honda(Color.Black)`)
	[ ] 42.2 Settings with `service(name).X = ...` - only from the thread that created it, never
		a sub-thread; the compiler picks the defaults not given (Mailbox, WhenFull, Scheduler,
		Timeout, ...)
	[ ] 42.3 (after version one) Group services: `service(a, b, ...) group` - two or more
		plain variables become one service; every call on a or b goes through the group's
		queue, atomically; released at the end of its scope. A variable has one owner only
		(a second group: compile error); nesting allowed; each service keeps its own
		settings; undone where possible; formed before use; also from class methods. A
		warning above `max_unit_warn` (5), an error above `max_unit` (32) - files/Service.md
	[ ] 42.3b (after version one) Service classes: `service class CarPerson { ... }` - every
		object is a service and each method is one atomic step; for advanced, more complex
		operations; not recommended in a loop (a warning); SINGLE / SHARED and the prime
		settings chosen by the developer (files/Service.md). `run { }` is a one-time atomic
		operation where it is written; the service carries out one operation at a time
	[ ] 42.4 `service(x).final = { ... }` - extra clean-up; leaving scope always releases every
		associated resource (like try-with-resources)
	[ ] 42.5 Resources as services by default: files, sockets, pipes, databases
		(`[concurrency] resource_as_service = true`; direct access only in unsafe mode)
	[ ] 42.6 Settings that fit the machine: built-in defaults < fusion.toml < the program's
		defaults < service(x) in code. Levels from MIN (embedded or unknown memory) up, e.g.
		2GB as low end. Runs on any machine: never blocks the program or errors - a machine
		matching no level gets MIN
	[ ] 42.7 The Thread class (to be designed): ID (never reused, main = 0), GUID, hierarchy
		key (0.2.1), priority, an internal counter and helper functions that track threads as
		they are created and end
	[ ] 42.8 Default timeouts and other defaults per resource kind - confirm the exact values
		(starting point: Concurrency.md 3.7)
	[ ] 42.9 (after version one) Custom contention rules and schedulers (Concurrency.md 3.8); Rule.HIERARCHY default
	[ ] 42.10 Trap checks: warnings by default, errors when fusion.toml says so (two resources
		per thread, shared variables, missing timeouts, services blocking on each other)
	[ ] 42.11 (after version one) Possible service settings to go through (user + Claude, 2026-10-23):
		Mailbox (size) / WhenFull (WAIT, ERROR, DROP_OLDEST, DROP_NEWEST) / Timeout per
		request / IdleTimeout (release the thread when unused) / Scheduler (IMMEDIATE,
		BATCHED, custom) / BatchSize and BatchDelay / Priority / Rule (who wins contention) /
		Threads (pool size, min and max) / MaxParallelReads / final (clean-up) / OnError
		(restart, stop, report to parent) / RestartLimit (n restarts per period) / Name (for
		tools and logs) / Trace (profiling on) / Affinity (pin to CPU cores) / MemoryLimit /
		Lifetime (scope, until close, whole program) / Snapshot (readers see copies) /
		WarnAt (mailbox fill level that warns, e.g. 80%) / Retry policy / Shutdown (finish
		the mailbox, or drop it) / Access (which threads may send to it) / Weight (share of
		turns)
	[POSTPONED - later, own framework] 42.12 Cluster threads over several servers
		(ClusterThreadPool) - a separate cluster framework, probably outside Fusion's first scope
	[ ] 42.14 Prime settings (user, 2026-10-24; files/Service.md): Mailbox (default 12), WhenFull
		(default WAIT), Timeout, final, Scheduler (IMMEDIATE), Priority ("5.4.1"), Rule
		(HIERARCHY), WorkerThreadType, ThreadPool, run - defaults in fusion.toml
		[concurrency.defaults]; the rest are secondary settings (Coalesce, BatchSize, ...)
	[ ] 42.15 WorkerThreadType per resource: AUTO (default - SHARED as more threads read it,
		SINGLE when its work is heavy) | SINGLE (workers dedicated to this resource: one thread
		or its own ThreadPool) | SHARED (shared workers from a specific ThreadPool); can be set
		by hand. Coalesce is a secondary setting; custom schedulers / rules / priorities: one
		method per class (files/Service.md)
	[ ] 42.16 Duration literals: `500ms`, `5s`, `2min`, `1h` - an int of milliseconds for now;
		also read from text (strings, fusion.toml). The full time module: Task 43.1
	[ ] 42.13 The compiler checks P9 (a service handling a request calls only down the
		hierarchy, or sends without waiting) across modules - to be designed
	[ ] 42.17 Collections and threads (user, 2026-10-27 - Concurrency.md 3.12): an array's
		add / remove at the end is thread-safe by itself (an atomic lock, 45.8); a List or
		Map is served by a shared or its own (dedicated) thread for adding, reading and
		removing - like a small service. `[collections] threads = "shared"` (default) /
		"dedicated", `shared_threads = 10` (default)
	(The thread view in the editor: 36.6. The service reference: files/Service.md)

#### 43 Core modules design (fusionlib) (user, 2026-10-24) [ ]
	The standard library's core modules, designed one at a time (spec "Fusion Standard
	Library (fusionlib)"). Plan first.
	[ ] 43.1 Time: hours, minutes, seconds, milliseconds, nanoseconds; days, months, years; time
		zones; epochs; durations and time calculations (a Math sub-module, user). Duration
		literals map to int milliseconds until then (42.16)

---

## Old task numbers (renumbered 2026-10-11)

Old notes, commits and code comments may use these. Old numbers are never reused.

| Old | New |
|---|---|
| 10 Self-hosting | 28 (phase 1), 35 (phase 2) |
| 11 LLVM backend | 40 |
| 13 HIDL | 41 |
| 14 Nullable & safe navigation | 30 |
| 15 Deferred decisions | 15.1 -> 40.1, 15.2 -> 37.1, 15.4 decided (self-hosting first), 15.5 -> 38, 15.6 -> 31.5, 15.12 -> 37.2; the rest done |
| 16 Example coverage | 34 (16.2 -> 32.3, 16.3 -> 33.2, 16.5 -> 26) |
| 17 Strings | 29 (17.N -> 29.N) |
| 19 Library security | 39 (19.N -> 39.N, 19.6 done, 19.7 -> 39.6) |
| 20 Config formats | 31 (20.N -> 31.N) |
| 21 Error handling | 26 |
| 24 Editor support | 36 (24.N -> 36.N) |

---

## Later / advanced (after MVP)

Kept in Fusion's design, deliberately postponed - the simple version comes first.
	[POSTPONED to 29.4] String pool (shared storage for identical text) - when pooling is on,
		strings are pooled and mutable strings use a StringBuilder internally (user note 2026-10-09)
	[POSTPONED to 38] StringBuilder for fast repeated appends (internal for mutable strings)
	[POSTPONED to 38] Garbage collection as a project-selectable memory strategy
	[POSTPONED to 38] Unique<T> / Shared<T> / Weak<T> (decided in 12.7, not built)
	[POSTPONED to 38] Copy-on-write string sharing (in-place editing, s[i] = c, done in 29.1)
	[POSTPONED to 32] Methods on structs (`p.move(1, 2)`) - user-defined classes; methods on
		built-in types are done (18.3.7)
	[POSTPONED to 18.3] Closures (lambdas using outer variables) - need string ownership first
	[POSTPONED - after MVP] Named lambdas inside functions; multi-line lambda bodies
	[POSTPONED - after MVP] Lambdas / function types returning arrays; const array set from a call
	[POSTPONED - after MVP] Full Unicode letters and case changes beyond Latin-1 (Greek, Cyrillic, ...
		- 18.3.6 covers ASCII + Latin-1), normalization (é typed two ways
		compares equal), counting what users see as one symbol (emoji families)
	[POSTPONED - needs IO (18.5) / Data module] Bytes <-> string, Base64, URL encoding,
		JSON/HTML escaping, validating UTF-8 from files and networks
	[POSTPONED - needs Regex module] Pattern matching: matches, find, replaceAll with patterns
	[POSTPONED - after MVP] Full expressions inside `{...}` (`{a + b}`)
	[ ] money type (user, 2026-10-24 / 10-27): strict decimal for currency, default 0, written-out
		conversions, rounding half away from zero + a rounding-mode enum (files/Literals.md
		"Money", spec "Complete Type Specifications")
	[ ] Lists (user, 2026-10-27 - Arrays.md): add many at once (another list, a group of
		values); capacity and a growth buffer that can be set; a kept sort order (every
		added item goes into its sorted place)
	[ ] List copyPart (user, 2026-10-27): rename `slice` to `copyPart(start, count)`, `slice` kept
		as quick typing; a count past the end gives the items up to the end (today an
		IndexError); a start outside the list is an IndexError. `copyPartAt(start, end)`
		(`sliceAt`): end included, stops at the end, start after end gives the items reversed.
		Positions count from 0. Also `+` for lists (`a + b + c`)
	[ ] Changing a List / Map while looping (user, 2026-10-27): a setting per list / map (or
		project) allows adding / removing inside the loop; when not allowed it stays a
		ModifiedWhileLoopingError (today's rule, 27.2e) - saves a temporary copy
	[ ] Map keys (user, 2026-10-27): values of any type; keys a non-empty fixed string (never
		pooled) or a whole number 0 or above (byte, int - no floats). A map can bring its own
		hash function and key rules (e.g. only non-empty strings, or ints only). Today: keys
		are string, int or char. Combining: `m.add(otherMap)` (no `+`); a setting on the map
		decides a key already there - replace by default (user, 2026-10-27)
	[ ] Map literals: `Map<string, int> stock = {"apples": 3, "pears": 0}` (missed while writing
		examples/control_flow, 2026-10-11 - a map is filled one key at a time today)
	From the showcase review (user, 2026-10-23):
	[ ] `switch` and `match` interchangeable; `elif` an alias for `else if`. The preferred forms
		(used in docs and examples) are `else if` and `switch` (user, 2026-10-24)
	[ ] Enum values with fixed constants, built by the enum's private constructor:
		`enum Planet { Mercury(3.7) ... }`, Planet.Mercury.gravity() / Planet.Mercury.Name
	[ ] Several return values only when `[functions] multiple_returns = true` (off by default);
		a function that can fail always has its Error last
	[ ] Operator overloading, off by default - `[language] operator_overloading = true`
	[ ] Namespaces: group related modules (several folders / libraries) under one name
	[ ] println with a line ending: the PC's own, or set in fusion.toml. Kept for later (user,
		2026-10-24); note for developers: `print` already ends the line
	[ ] `loop`: a `loop { }` with no break / return inside is a compile error (user, 2026-10-24),
		and the user is thinking of dropping the `loop` keyword - to review
	[ ] Struct settings (user, 2026-10-24): a struct is a value type and never null - it always
		has a value, so it may hold an empty List / Map / string but never null. In
		fusion.toml [structs]: holding List / Map (on by default - built), functions on
		structs (off by default, Task 32.1), classes inside structs (off by default)
	[DONE] Open: `int?` - decided with Task 30 (user, 2026-10-27): no `T?` types at all; `?` is
		used on a variable (`x?.method()`), and only class objects can be null (Nullable_Values.md)
	Showcase [idea] list - to go through one by one (files/showcase/, user 2026-10-24):
	[ ] Import only some names from a module: `import geometry { square, circle }`
	[ ] A whole-program setting read from fusion.toml at compile time (`config.build.mode`)
	[ ] `++` and `--` as statements only (never inside an expression)
	[ ] Type tests with `is` (`if s is string`) - the spec uses `is` only for null
	[ ] `typeOf(x)` gives the type's name as text
	[ ] A format inside `{}`: `{value:pattern}` (`{19.5:$0.00}`)
	[ ] Raw strings: `r"C:\path"` - no escapes
	[ ] Multi-line strings: `"""..."""`, indentation removed up to the closing quotes
	[ ] `Set<T>`: each value once
	[ ] Slices: a part of a list or string by range (`numbers[0...1]`)
	[ ] Tuples: a few values without declaring a struct (`(string, int) pair = ("Ada", 36)`)
	[ ] `if` as a value: `string size = if a > 5 then "big" else "small"`
	[ ] Function overloading by parameter types
	[ ] do-while: the body runs at least once
	[ ] Guards in match: `case x if x < 0`
	[ ] Ranges in match cases: `case 0...9`
	[ ] `assert cond, "message"` - an AssertionError when false
	[ ] Flag enums: values combine with `|` (`Permission.Read | Permission.Write`)
	[ ] Copy with changes: `Point moved = a with { x = 5 }`
	[ ] Extension methods: `extend string { ... }` adds methods to a type you didn't write
	[ ] `?` after a call: return its error from this function at once (`loadConfig("x")?`)
	[ ] Wait for several tasks together: `await all([...])`
	[ ] Calling a C function by declaring it: `extern "C" int function abs(int x)`
	[ ] Hardware descriptions: `import hardware "x.hidl" as microwave`; registers as typed
		properties, out-of-range values compile errors (Task 41)
	[ ] fusion.toml: `block_styles` - allow only some block styles in a project
	[ ] fusion.toml: `[threads] pool_size = "auto"` (one per CPU core)
	[ ] fusion.toml: `[modules] paths` - extra folders searched for imported modules
	[ ] fusion.toml: `wait_at_exit` as a setting (today: the default, --headless turns it off)
	(Already listed above: namespaces, operator overloading, println, map literals, loop)
	[POSTPONED - after MVP] Paged / memory-mapped strings: load only the part of a huge string in use
	[POSTPONED - with each feature] More error types (Task 26 list, 2026-10-16): NetworkError /
		TimeoutError (a network module), ParseError (JSON / data modules), CancelledError
		(threads), AssertionError (an `assert` statement), NotSupportedError (a backend that
		can't do something) - each an Error subtype
	[POSTPONED - after MVP] Per-field string sizes (`string(255) name`) to match database columns
	[POSTPONED - needs references] Identity operator (same object in memory)
	[POSTPONED - after MVP] Multi-dimensional arrays (growable lists: done, 18.5.1)
	[POSTPONED to 32 / 33] Classes, interfaces, inheritance (32), generics (33); enums: Task 25;
		threading: no task yet

## Known limitations (by design for now)
	[ ] A string-holding variable can't reuse the name of one in an enclosing block (clear error)
	[ ] Single-quote comments disabled (clash with char literals) - 8 skipped tests
	[ ] Identifiers ASCII-only unless fusion.toml opts in (text and chars are Unicode since 18.3.2b)
