# Fusion - Feature and Task Status

The single place to see what is done, open, or postponed. One line per item.

- `[ ]` open · `[DONE]` finished · `[POSTPONED to X]` waits for X (a task, or a missing feature)
- `##` = major sections only. Tasks: `#### NN Title [status]`. Sub-tasks: one tab +
  `[status] NN.N`. Parts: two tabs
- Sections: Done, Phase 1 (up to the self-hosting test run), Phase 2, Phase 3, Later,
  Known limitations, Old task numbers (open tasks were renumbered from 25 on 2026-10-11)
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

Finished tasks keep their numbers (commits, the archive and code comments refer to them).
Their detail is in `task/taskSummaryArchive.md`.

#### 01-04 MVP compiler: lexer, parser, semantic analysis, C codegen [DONE]
#### 05 Cleanup & organization [DONE]
#### 06 Verification & bug fixes (incl. FizzBuzz) [DONE]
#### 07 Git & GitHub [DONE]
#### 08 const keyword [DONE]
#### 09 Fixed-size arrays v1 [DONE]
#### 12 Compiler architecture hardening (typed AST, codegen split, block scoping, memory-model ADR, config) [DONE]
#### 18 Core language foundation ("a simple working language first") [DONE]
	(every part's detail: task/taskSummaryArchive.md, "Task 18 - FEATURES.md detail")
	[DONE] 18.1 Functions: default values, array parameters, lambdas v1 and function types
	[DONE] 18.2 Structs: fields, named arguments, nesting, arrays of structs, arrays as return values
	[DONE] 18.3 Proper strings: values with cleanup, Unicode, interpolation, equality, the string
		library, raw bytes, type classes and method syntax
	[DONE] 18.4 `import` and multi-file projects: modules, `public`, aliases, `--interface`
	[DONE] 18.5 Minimal standard library: List, Map, text helpers, program arguments, console input,
		files, layers core / alloc / std, the word-counter example
#### 23 Examples folder as a showcase [DONE]
	[DONE] 23.1-23.6 One example per SYNTAX_REFERENCE.md section, #list.csv, #run.bat, examples/CLAUDE.md
	[DONE] 23.7 A compiled program waits for a key before its window closes; `--headless` closes it at
		once; no wait when output is redirected (user request 2026-10-11) - #run.bat passes --headless
	[DONE] 23.8 Windows Explorer preview of .fusion files: tools/windows/fusion-file-preview.reg (user request)
	[DONE] 23.9 files/showcase/: Fusion_showcase.fusion + fusion.toml - the whole language, built and
		future, each feature tagged [built] / [designed] / [idea] / [rejected] (user request 2026-10-23)

#### 22 Project tracking restructure (FEATURES.md, SYNTAX_REFERENCE.md, slim CLAUDE.md, check.py) [DONE]
	[DONE] 22.1-22.6 FEATURES.md, SYNTAX_REFERENCE.md, slim CLAUDE.md, working file / archive /
		backlog split, nothing lost, check.py
	[DONE] 22.7 Reliable markers for files that lack them (see task/automation.md)
		[DONE] 22.7a README reduced to goals + pointers to FEATURES.md / SYNTAX_REFERENCE.md
		[DONE] 22.7b A `**Status:**` line under each major section of the language spec (31),
			matching FEATURES.md; the spec's old task numbers changed to the new ones; a duplicate
			"Reserved Words and Operators" heading removed
		(FutureFeatures.md: a task link is added only when an item becomes a task - a standing rule)
	[DONE] 22.8 `check.py --fix-ascii`: non-ASCII characters -> \uXXXX escapes, only where meaning is unchanged
	[DONE] 22.9 `check.py --ship "message"`: every check, then commit + push only if all pass
	[DONE] 22.10 `check.py --example NAME`: build, run and compare one example
	[DONE] 22.11 `tools/patch.py`: apply a list of exact edits, all or nothing
	[DONE] 22.12 FEATURES.md reorganized into phases, open tasks renumbered from 25 (2026-10-11)

---

## Phase 1 - up to the self-hosting test run

First major goal (user, 2026-10-11): a **simple working self-host** - a compiler written in
Fusion, covering only the simple part of the language, whose exe compiles the programs in
`examples/` by itself. A test run: the Python compiler stays the real compiler until the
self-hosted one is fully independent (Phase 2). Guide: `Notes/04/notes.md` section 5.

#### 25 Enums and tagged unions [DONE]
	[DONE] 25.1 Detailed plan - approved 2026-10-12 (data inside enum; Color.Red, bare names in match cases; else; data only through match)
	[DONE] 25.2 Plain enums: one line / block / braces / End enum, commas optional, explicit values;
		Color.Red, ==, printing, toString / toInt, values(), fromString; as fields, elements, Map
		keys; across modules and in --interface
	[DONE] 25.3 `match` on enums (bare names, every value covered or an else) and on int / byte /
		char / string (constants, else required); several values per case; three block styles;
		break / continue act on the loop
	[DONE] 25.4 Enums with data (tagged unions): Token.Number(42) / named arguments, read through
		`case Number(n)` (copies; `_` skips), ==, copies and cleanup like structs; prints the name
	[DONE] 25.5 Enums holding themselves: Add(Expr left, Expr right) on the heap, or List<Expr>;
		deep copies, ==, cleanup; first value can't hold itself; loops through other types are errors
	[DONE] 25.6 Example examples/expressions (tokenize -> parse into an Expr tree -> evaluate) + docs

#### 26 Error handling: Go-style error returns + try/catch, both on by default, switchable in config [DONE]
	[DONE] 26.1 Detailed plan - approved 2026-10-16 (errors bubble up, capture optional on any call,
		every built-in failure catchable, one catch-all)
	[DONE] 26.2 `Error` and error returns: `T, Error function`, `return Error(...)`, capture on any
		call, `if err`, bubbling (explicit, leak-free), stop at main
	[DONE] 26.3 try / catch err / finally / throw: one catch-all, finally on every exit (return,
		break, continue, errors passing through), rethrow, nesting, three block styles
	[DONE] 26.4 Every built-in failure catchable: index out of range, missing key, conversions,
		files, patterns, fromString, max_length, ... - uncaught still stops ("Runtime error at")
	[DONE] 26.5 Config: `[errors] returns / exceptions` in fusion.toml (both on by default) - turning
		one off makes that syntax a compile error
	[DONE] 26.6 Example examples/errors_demo (capture, bubbling, try / catch / finally, built-in
		failures; the argument "uncaught" shows one nobody catches) + docs
	(part 2 - user request 2026-10-16)
	[DONE] 26.7 Implicit errors: `return Error(...)` in any function; `T, Error function` an optional
		marker (shown by --interface; marked but can't fail: a warning)
	[DONE] 26.8 Capture without a type: `Ship s, err = f()` (`Error err` still works)
	[DONE] 26.9 Custom error types: `error FileError` + fields, `error FileNotFound : FileError`, a
		default message / code, made like a struct, across modules
	[DONE] 26.10 Typed capture `Ship s, FileError err = f()` (captures any error); `err.kind`; `match err`
		with error type names as cases (subtype-aware, the type's own fields inside)
	[DONE] 26.11 Typed catch: `catch FileError e` ... `catch e` - first match, subtypes, unmatched goes on
	[DONE] 26.12 Built-in error types - every one is an Error, a parent catches its children
		(full list with examples: taskSummary2.md "Built-in error types"):
		[DONE] ArithmeticError: DivideByZeroError - NEW check: 7 / 0 and 7 % 0 no longer crash
		[DONE] FormatError: NumberFormatError (toInt("12x")), PatternError (formatNumber),
			HexFormatError (hexToBytes), TextEncodingError (bytes that aren't text)
		[DONE] ValueError: RangeError (toByte(300), negative counts, base), UnknownValueError
			(Color.fromString("Pink"))
		[DONE] LookupError: IndexError (s[9], xs[9], b[9], slice ...), KeyError (m["missing"])
		[DONE] FileError (path): FileNotFoundError, PermissionError, FileReadError, FileWriteError,
			FileTooLargeError, DeleteError
		[DONE] LimitError: StringTooLongError (max_length), ResultTooLargeError (over 2 GB)
		(not catchable by design: out of memory, a List past 536,870,911 elements)
	[DONE] 26.13 Docs + examples: examples/errors_demo with a custom error type, match on error
		types, typed catch, built-in types (FileNotFoundError, DivideByZeroError)
	[DONE] Error handling example (was 16.5) - examples/errors_demo (26.6)

#### 27 Semantic contract and safety (from the ChatGPT review, 2026-10-11; notes.md step 2) [DONE]
	[DONE] 27.1 Bounds checks for fixed arrays: `a[5]` on an `int[3]` crashes today (segmentation
		fault, found 2026-10-11) or, worse, silently overwrites other memory. Every out-of-range
		index must be a clear run-time error, never missed (user: "so we don't miss out-of-range
		errors any more") - reading and writing, array parameters, arrays in structs, arrays of
		structs. Lists, strings and bytes are checked already
	[DONE] 27.1b Indexing an array literal directly - `[1, 2][5]` - generates invalid C (found
		2026-10-16 while testing 26.10)
	[DONE] 27.2 The contract, written in the spec in one place: copying (deep - every copy is
		independent, nested lists too), the equality table (which types `==` / `===` compare),
		`=` in conditions with its ambiguous cases tested, Unicode indexing (code points, not
		what a reader sees as one symbol), integer conversions and overflow, changing a
		collection while looping over it, cleanup on every path (early return, break, exit)
	[DONE] 27.2e Changing a List / Map while a for loop goes over it is a ModifiedWhileLoopingError
		(user decision 2026-10-17: an error, never a skipped element); `=` outside a condition
		says to write `==`
	[DONE] 27.2f int to float: `[numbers] auto_widening` (user decision 2026-10-17) - false (default):
		an int used as a float must fit exactly (a written number that doesn't: compile error;
		a value: PrecisionError); true: widens automatically, with a warning at every place
	[DONE] 27.2b OverflowError: whole-number arithmetic that doesn't fit (2147483647 + 1 wraps
		silently today - against "never change values silently"). User decision 2026-10-17:
		**checked by default** (+ - * unary -, / of -2147483648 by -1, number conversions that
		don't fit) - an OverflowError, subtype of ArithmeticError; **turned off in unsafe mode**
		([safety] mode = "unsafe" - wraps, still never C undefined behaviour). Checks the
		compiler can prove unneeded are left out (constants, range loop counters)
	[DONE] 27.2c Endless recursion: a stack overflow crashes today - a catchable StackOverflowError.
		User decision 2026-10-17: stack use by default (a limit from the real stack size);
		`[safety] max_call_depth` = "max" (default) or a number - a call counter for
		memory-constrained devices
	[DONE] 27.2d Wrapping on purpose: wrapAdd(a, b), wrapSub, wrapMul (hashes, checksums); an
		`unchecked` block turns overflow checks off inside it (user, 2026-10-17) - bounds checks
		are never turned off
	[DONE] 27.3 Interaction tests: features together - a struct holding lists, copied, passed
		through functions and across modules; nested collections; early returns - tests/test_safety.py
	[DONE] 27.4 Block-style equivalence: the same app written 3 times - indentation, braces,
		`End` keywords - 3 .fusion files that must compile to identical C (user request);
		kept as examples and checked by check.py - examples/style_indent, style_braces,
		style_end; tests/test_safety.py compares their C
	[DONE] 27.5 Doc fix: the equality heading in SYNTAX_REFERENCE.md names `!==` too

#### 28 Self-hosting phase 1 - the test run (was 10) [ ]
	[DONE] 28.0 Prerequisites: analysis (was 10.1) and language features (was 10.2, by Task 18)
	[DONE] 28.1 The subset: exactly what the programs in examples/ need - measured by
		tools/example_subset.py: three tiers (18 / 12 / 14 programs), and gaps A-C (calling GCC,
		shared state, the C run-time) - task/selfhost_subset.md. Target: tier 1 (user)
		[ ] 28.1.1 `run(command)`: run another program, wait, return its exit code (gap A) -
			tested with Notepad, the examples, and compiling + running an app from Fusion
		[ ] 28.1.2 Shared state (gap B): measure; a parameter a function never changes is
			not copied (List parameters are copied today - found 2026-10-24)
		[ ] 28.1.3 The C run-time as a shared file `runtime/fusion_runtime.h` (gap C)
		[ ] 28.1.4 `files/Builtins.md`: every built-in function (94) and method, generated
			from the compiler and checked by check.py
	[ ] 28.2 Lexer in Fusion
	[ ] 28.3 Parser in Fusion
	[ ] 28.4 Checker in Fusion
	[ ] 28.5 C code generator in Fusion
	[ ] 28.6 Driver (main): read files, write C, call GCC
	[ ] 28.7 Verify: the Fusion-built compiler.exe compiles every example, and those programs
		print the same as the Python-built ones
	[ ] 28.8 Report: what was missing or awkward -> feeds Phase 2

---

## Phase 2 - growing the language, then a fully independent compiler

#### 29 Mutable vs. fixed strings, templated strings, string pooling (was 17) [ ]
	[ ] 29.1 Mutable string literal syntax (in-place editing, `s[0] = 'X'`)
	[ ] 29.2 Fixed (immutable) string type
	[ ] 29.3 Templated fixed strings
	[ ] 29.4 String pooling as a project setting (`[structs] string_storage = "pooled"` waits for this)
	[POSTPONED - needs fusionlib.Crypto] 29.5 Secure string storage, constant-time comparison

#### 30 Nullable values & safe navigation (`?.`, `?[`, `.length`) (was 14) [ ]
	[ ] 30.1 Nullability model decision
	[ ] 30.1b NullError: using a value that holds nothing (the "divide by null" case) - an Error
		subtype (Task 26 error list, 2026-10-16)
	[ ] 30.2 Compile-time null-flow analysis
	[ ] 30.3 `.` / `?.` / `?[` parser support (the `.` part exists since 18.2.1)
	[ ] 30.4 Runtime null-check codegen
	[ ] 30.5 Beyond arrays (stretch)
	[ ] 30.6 Docs & examples

#### 31 Config file in any format: fusion.toml / .yaml / .json / .ini (was 20) [ ]
	[ ] 31.1 One loader per format, one shared schema
	[ ] 31.2 Discovery and ambiguity (two config files = error)
	[ ] 31.3 Tests
	[ ] 31.4 Docs
	[ ] 31.5 Enforce fusion.toml [safety] / [backend] (was 15.6; trigger: strict mode or a 2nd backend)

#### 32 Methods on structs, then classes and interfaces (user, 2026-10-11) [ ]
	[ ] 32.1 Methods on the program's own structs (`p.move(1, 2)`) - built-in types have them (18.3.7)
	[ ] 32.2 Classes, interfaces, inheritance - plan first
		User decisions (2026-10-23, showcase review): `inherits`, with `extends` as an alias;
		interface names need no I prefix; several constructors per class; a constructor may
		call another (private ones too) with this(...); constructors calling each other in a
		circle are a compile error
	[ ] 32.3 Example (was 16.2: classes, interfaces & enums)

#### 33 Generics: the program's own generic functions and types (user, 2026-10-11) [ ]
	[ ] 33.1 Plan (List<T> / Map<K, V> are built in since 18.5)
	[ ] 33.2 Example (was 16.3)

#### 34 Example program coverage (was 16) [ ]
	[DONE] 34.0 Control flow (was 16.1, examples/control_flow) and modules (was 16.7, examples/shop)
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

#### 37 Deferred decisions (rest of 15 - user: after self-hosting, some become own sub-tasks) [ ]
	[ ] 37.1 Stdlib runtime lowering decision (was 15.2)
	[ ] 37.2 Operator operands evaluated in C's order (`next(c) - next(c)`); call arguments are
		left-to-right already (was 15.12)
	[ ] 37.3 Incremental builds, stable symbol identities (ChatGPT review; notes.md step 5)

#### 38 Memory model: Unique / Shared / Weak, GC as a project option (was 15.5) [ ]
	[ ] 38.1 Scope it (semantics decided in 12.7, not built)

#### 39 Library trust, isolation & security (was 19) [ ]
	[DONE] 39.0 Source-level attack defenses: Trojan Source, homoglyphs, ASCII identifiers (was 19.6)
	[ ] 39.1 Compiler-verified capability signatures (was 19.1; layers from 18.5.6 are the groundwork)
	[ ] 39.2 Project restrictions (pragma Restrictions-style) (was 19.2)
	[ ] 39.3 Closed, compiled, licensed libraries (was 19.3)
	[ ] 39.4 Sandboxing and resource budgets (was 19.4)
	[ ] 39.5 Supply-chain security (was 19.5)
	[POSTPONED - needs fusionlib.AI] 39.6 AI module input guard (was 19.7)

#### 40 IR layer and LLVM backend (was 11, 15.1) [ ]
	[DONE] 40.0 Research & design (was 11.1)
	[ ] 40.1 IR layer decision (was 15.1) - the IR expresses Fusion's meaning; the C and LLVM
		backends only translate it (ChatGPT review)
	[ ] 40.2-40.13 Environment, IR generator, types, functions, codegen, strings, stdlib,
		optimization, tests, docs (was 11.2-11.13)

#### 41 HIDL - hardware interface definition language (was 13) [ ]
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
	[POSTPONED to 29] StringBuilder for fast repeated appends (internal for mutable strings)
	[POSTPONED to 38] Garbage collection as a project-selectable memory strategy
	[POSTPONED to 38] Unique<T> / Shared<T> / Weak<T> (decided in 12.7, not built)
	[POSTPONED to 29] Copy-on-write string sharing, in-place string editing
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
	[DONE] Masking functions in the core string library: formatMask, digitsOnly, mask, maskEmail
		(design and all 9 decisions: spec "Masking", Task 18.3.6f; built 2026-10-10)
	[POSTPONED - needs Regex module] Pattern matching: matches, find, replaceAll with patterns
	[POSTPONED - after MVP] Full expressions inside `{...}` (`{a + b}`)
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
	[ ] Open: `int?` - the spec says value types can't be null but its `?[` example uses `int?`
		(user will check, with Task 30)
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
	[DONE] Bounds checks for fixed arrays - Task 27.1
	[POSTPONED to 32 / 33] Classes, interfaces, inheritance (32), generics (33); enums: Task 25;
		threading: no task yet

## Known limitations (by design for now)
	[ ] A string-holding variable can't reuse the name of one in an enclosing block (clear error)
	[ ] Single-quote comments disabled (clash with char literals) - 8 skipped tests
	[ ] Identifiers ASCII-only unless fusion.toml opts in (text and chars are Unicode since 18.3.2b)
