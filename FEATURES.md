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
		needs a reference count, as Task 38's Shared does (`[structs] stringStorage =
		"pooled"` waits for this)
	[POSTPONED - needs fusionlib.Crypto] 29.5 Secure string storage, constant-time comparison

#### 49 Decisions.md - every feature and decision in one place (user, 2026-10-31) [ ]
	Before 32.5 (it keeps later work from contradicting earlier decisions)
	Rule: CLAUDE.md Rule 3b
	[DONE] 49.0 First version of Decisions.md: section 1 features, section 2 decisions, 4 clashes found
	[DONE] 49.1 The design documents' decisions logs: Object_Lifetime, Classes, Arrays, Nullable_Values, Ownership
		D.029-D.056 added; MEM.008, COL.011, COL.012 added; clashes C.005, C.006 for the user
	[DONE] 49.2 FEATURES.md, task/featuresArchive.md (built features), SYNTAX_REFERENCE.md
		39 feature lines added (the showcase ideas, built settings, postponed items); D.059-D.063
		Old Later lines marked: money as a decimal and string(255) replaced, namespaces built
		Clashes C.007 (the word "fixed"), C.008 (`switch` preferred, `match` used) - settled: D.064, D.065
	[DONE] 49.3 The spec and the grammar (files/fusion-language-spec.md, files/fusion.ebnf)
		17 feature lines added (comments, `<>`, `unchecked`, `...`, properties, casts, interop, ...)
		D.060 corrected: an int is used as a float when it fits exactly (27.2f)
		The spec summary fixed where it went against decisions: GC default, nullable strings,
			immutable strings, implicit widening, fields-only structs, locks, one class per file
	[DONE] 49.4 Concurrency.md, Concurrency_Traps.md, files/Service.md
		7 feature lines (version one, settings, the hierarchy, trap checks); D.066-D.075
		Clash C.009 settled 2026-10-31: a group service (D.077)
	[DONE] 49.5 Settings: files/fusionSettings.xml, files/showcase/fusion.toml (built / designed / idea / rejected)
		9 feature lines (the built settings missing, [project], [build], [threads], stack traces); D.076
	[DONE] 49.6 Notes/, FutureFeatures.md, FutureFeaturesCaution.md, task/taskSummaryArchive.md (decisions only)
		11 feature lines (comment blocks, bit type, decimal, arenas, tools, IDE module); D.078, D.079
		Fixed against decisions: Currency live rates (D.022), GC default (D.027), `Shared<T>?` (D.063)
		Marked as replaced in FutureFeatures: decimal money, string prefixes, `type()` arrays
		Clash C.010 settled 2026-10-31: no `.move()`, assigning moves (D.080)
	[ ] 49.7 The code: what the compiler does that no document records (src/)
	[ ] 49.8 The user settles each CLASH row; the losing side is fixed in its document
		C.001-C.004 settled 2026-10-31 -> D.025-D.028; documents fixed
	[ ] 49.9 A check in check.py: every feature line has a known area and status; IDs unique and in order

#### 47 Types: long, money, enums with fixed data (user, 2026-10-29) [ ]
	After Task 32 and 36.0. The type table: files/FusionTypes.html
	[ ] 47.1 `long` (64-bit, -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807; overflow
		checked like int) and `short` (16-bit) - reserved words today, not built
	[ ] 47.2 `money`: a `long` counting a currency's minor units - kind value, default 0, min /
		max as long, 8 bytes, never null; exact whole-number arithmetic with overflow checking -
		not a decimal, never a float. Plan the literal / printing form first
		[ ] 47.2.1 Minor units (user, 2026-10-29): `money` is a signed 64-bit whole number -
			always cents, or the currency's own minor unit where it has a smaller one; what a
			unit means is the Currency module's (43.3). USD / ZAR (2 decimal places): $1 is 100,
			12345 is R123.45. JPY (0 decimal places): stored the same way, ¥1 is 100 - always a
			whole multiple of 100 (100, 200 ... 900), so it never has a fraction: the smallest
			amount above zero is 100 (¥1), then 0, and the largest below zero is -100 (-¥1).
			KWD (3 decimal places): 1 KWD is 1000. `money` itself is just a long, whatever the
			currency - the Currency module's code enforces each currency's steps (user,
			2026-10-29). The core stays small; the currency system can change on its own
		[ ] 47.2.2 Exact on every device: rules for everything that makes a fraction - rounding,
			percentages (deals, discounts), tax, splitting an amount (R100 / 3) - so a
			calculation gives the same result on any CPU, OS or platform. Whole-number steps
			only (no floating point); the rounding mode written out (half-up, half-even /
			banker's, down, ...) with a project default; where a split's remainder goes
			(R33.34 + R33.33 + R33.33); the order of steps (discount before or after tax)
			stays the program's - Fusion only makes each step exact
		[ ] 47.2.3 Later option: a decimal or arbitrary-precision number type - for amounts past
			a long's range or more fractional precision than the minor unit gives
	[ ] 47.3 An enum whose values carry fixed data (Java's `enum Planet(double mass)`):
		`EARTH(5.976e24)`, read with a method for each field (`Planet.EARTH.mass()`); the data
		is const and byVal, set once; the constructor is always private. An enum is always
		const and static - `const static enum Planet` is accepted and changes nothing
	[ ] 47.5 The `fixed` prefix (user, 2026-10-31 - Ownership.md, files/Service.md)
		`fixed(n)` limits only the size; the values may change (`const`: nothing changes) - D.064
		`fixed(10) string name`: at most 10 characters, kept inline - no heap
		`fixed(10) int numbers[]`, or `fixed int numbers[10]` (the size written in the array)
		`fixed(14) List<Person> people`: at most 14 elements
		`fixed(10) Map<int, fixed(15) string> codes`: at most 10 keys, each value at most 15 characters
		Lower is fine, higher never - an error, never a silent cut
		Starts empty, grows as needed up to its maximum; memory reserved once
		The size may be a constant set by the hardware or a setting (H9)
	[ ] 47.4 A built-in enum `FusionType` describing every type (user, 2026-10-29 - the table in
		files/FusionTypes.html): fields Type, Kind, Default, Min, Max, Size, CanBeNull. Each
		field's method returns a value of that type itself, byVal: `FusionType.INT.MAX` is an
		int (2,147,483,647), `FusionType.BOOL.MAX` is `true`, `FusionType.DOUBLE.MIN` a double -
		for developers and IDEs. Value names in capitals (INT, BOOL, ...) so they never clash
		with the type keywords (user, 2026-10-29). To settle when planned: one spelling for
		the fields (`MAX` or `max`); a field whose type differs per value is more than 47.3
		gives, so it is built in

#### 45 Arrays that grow at the end (user, 2026-10-27 - Arrays.md) [ ]
	Today an array's size is fixed when it is made, and the compiler must know it. An array
	will grow and shrink at its end only (an item never moves position); a List changes
	anywhere.
	[ ] 45.1 Each array knows its own length at run time (like a List), so an array can be
		replaced by one of another size (`numbers = make()`, `numbers = [1, 2, 3]`)
	[ ] 45.2 Empty arrays: `int[] numbers` and `int numbers[]` (was 30.10)
	[ ] 45.10 Arrays live on the heap and follow the List rules (Decisions.md D.025, user 2026-10-31)
		Normal code: an array moves (`int[] b = a`); `byVal` copies
		Inside a struct: only borrowed - never moved out
		Then an array's `toList(false)` can hand it over
	[ ] 45.11 `toList` and `toCSV` on arrays of more dimensions - with multi-dimensional arrays
		(user, 2026-10-29)
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
	[ ] 45.7 The array being looped over can't be changed inside the loop (user, 2026-10-31, D.058)
		Any loop: `for` and `foreach` - a compile error where seen, else ModifiedWhileLoopingError
		Build a new array from it instead: loop over `a`, add to `b`
	[ ] 45.8 An array used by two or more threads gets a temporary service (D.057, 42.19) - with Task 42
	[ ] 45.6 Docs and examples: Arrays.md, SYNTAX_REFERENCE, spec "Arrays"

#### 31 Settings file formats - the postponed parts (31.1-31.4 done 2026-10-28: task/featuresArchive.md) [POSTPONED]
	[POSTPONED to 43.2] 31.6 `config.fusion` - a Fusion program whose only job is to create the
		settings file from the master template (user, 2026-10-28)
	[ ] 31.5 Enforce fusion.toml [safety] / [backend] (was 15.6; trigger: strict mode or a 2nd backend)

#### 32 Methods on structs, then classes and interfaces (user, 2026-10-11) [ ]
	[DONE] 32.0 Settings housekeeping (tests/test_settings_formats.py) - user, 2026-10-28: names in camelCase, read case-insensitively,
		`_` ignored (`tab_width` = `tabWidth`); `[numbers] overflowWrap` (default false) takes
		over arithmetic wrapping from `[safety] mode = "unsafe"`; `[safety] mode` = safe
		(default; `normal` accepted) / strict (every warning is an error) / unsafe
	[DONE] 32.1 Methods on the program's own structs (`[structs] functions = true`;
		tests/test_struct_methods.py) - (`p.move(1, 2)`) - built-in types have them (18.3.7);
		also 44.2
	[ ] 32.2 Classes, the rest (plan: taskSummary2.md; truth tables: Classes.md - user, 2026-10-30)
		[DONE] 32.2a Visibility (tests/test_visibility.py): class fields private, functions /
			constructors public by default; module level: structs, classes, enums public,
			functions / variables private; fixed: classes and struct methods in modules
		[DONE] 32.2b Several constructors, chosen by the values given; `this(...)` on the first
			line; a circle, two alike, no match or two matches: compile errors
			(tests/test_classes.py)
		[DONE] 32.2c `static` (tests/test_statics.py): fields, const static, static methods; set-up
			forms A (direct), B (self set-up), C (`static { }`) in that order before main;
			classes by dependency; a circle is an error showing the whole chain; freed last
		[DONE] 32.2d Form B on any variable (tests/test_setup_blocks.py) - `Car c = new Car() {
			c.setEngine("V6") }`: locals, let / const, Lists, class fields (any value, set by each
			constructor first); the block changes its own variable only
		[DONE] 32.2e `readonly` parameters (tests/test_readonly.py) - never changed, deeply;
			passing on is an error only when the other function changes it (calls followed); a
			variable sharing it is readonly; keeping it is an error; a set-up block may change
			the const / let it sets up
		[DONE] 32.2f Printing an object (tests/test_object_text.py): the class name (null:
			`null`) in print / format / "{x}" / toString, one warning per class until ToString (32.5)
		[DONE] 32.2g The `null == null` bug - gave false (the null had no type); now true, as
			`null is null` (tests/test_classes.py)
		[DONE] 32.2h Visibility levels (tests/test_visibility_levels.py): private (the class) /
			internal (the namespace; without one, the module) / public; `namespace A.B` the
			file's first line; module functions public by default; private on a top-level item
			is an error; [visibility] required (default false)
		[DONE] 32.10a Lists and Maps are references with a count (tests/test_shared_collections.py):
			shared in normal code, copied in a struct; `byVal` copies, a `byRef` field shares
			(user, 2026-10-29 - truth table in Arrays.md section 1)
		[DONE] 32.10a.1 `toList(copy = true)` on a List (false: shared) and a one-dimensional
			array (a copy); null on an array / List / Map names the planned nullable setting
		[DONE] 32.10b Minimal classes (tests/test_classes.py): fields, methods, one constructor
			(or none), `new` optional, objects by reference with a count, null, NullError on
			`.`, `==` is the same object; a failing constructor frees its object
		[DONE] 32.10c The catalogue (tests/test_object_lifetime.py): U1-U5, U8, U9, D1-D9,
			R1-R5, C1-C4, T1-T3, O1, O2 - each checks the moment its object is freed
			(-DFUSION_TRACE_OBJECTS); fixed: `for x in [A(), A()]` made new objects every pass
		[DONE] 32.10d Cycles (tests/test_object_lifetime.py): a warning where a class can hold
			itself (directly, through other classes, Lists, Maps, arrays) - once per circle;
			the leak check stops a program that keeps one (exit 5)
		[DONE] 32.10e No counting where one owner is proven (tests/test_object_lifetime.py): a
			local returned is moved - no copy, no counting, not freed (every constructor's
			`return this`, a returned string or List); not through a finally
	[DONE] 32.8 Structs building on structs (tests/test_struct_parents.py): `implements`
		(`extends` / `includes`); an Employee goes where a Person is expected (a copy of its
		Person part); Person's methods work on it; same-name fields warn, `e.Person.tel`;
		`"{e}"` prints every field
	[DONE] 32.13 A struct as text (tests/test_struct_parents.py): `"{e}"` gives
		`name : "Jeff",age : 30`; `x.toCSV(delimiter = ",")` on a struct, a one-dimensional
		array or a List of structs - one heading row (`Person.name`, ...), one row per struct
	[ ] 32.7 Inheritance - using a parent type (user, 2026-10-29): `typeOf(x)` gives the chain,
		top type first (`Person.Employee.Manager`), so the program can convert it back; for a
		struct, only a `byRef` parameter keeps the whole value (a normal one: `Person`)
	[ ] 32.5 Interfaces - also the built-in ones (Classes.md sections 5, 6): `ToString`
		(how an object prints; without it the class name and a warning), `Default` (a
		constructor with no arguments, may be private - a variable of the type is never null,
		the object made when declared; `s = null` lets the old object go and makes a new
		default one (user, 2026-10-30); arrays / Lists / Maps implement it), `Cloneable`
		(`clone()` - copies of objects, byVal / toList on a List of objects, nocopy / noshare)
	[ ] 32.14 List / Map options set in form B (user, 2026-10-30): no duplicates, no null,
		read only after set-up - `List<string> names = List<string>() { names.noDuplicates() }`
	[ ] 32.4 A `Collection` interface (user, 2026-10-27 - Arrays.md section 6): arrays, lists and
		maps implement it; `foreach` works on any class that does, and the class decides its
		own rules (adding / removing while looping, threads, special actions)
	[ ] 32.3 Example (was 16.2: classes, interfaces & enums)

#### 48 Ownership: move, borrow, share (user, 2026-10-31) [ ]
	After all of Task 32 (user)
	Design and truth tables: Ownership.md
	Decisions D1-D49: Notes/Ownership_Decisions_2026-10-31.md
	Settings: [memory] assignment = "move" (default) | "share"
	[ ] 48.0 The rules (from Rust's borrow checker)
		R1 One owner: every object, List and Map has one owner at a time
		R2 Assigning moves: `Car b = a` - using `a` afterwards is a compile error
		R3 Passing borrows: `f(a)` lends it for the call; `a` is back afterwards
		R4 Many readers or one writer, never both at the same time
		R5 A borrow never outlives its owner: never stored, returned or captured (no lifetimes)
		R6 `shared`: counted, read only except to the holder that made it shared
		R7 The thread boundary: two or more threads using a value - one writer, a service (42.19)
		R8 Copies are written: `byVal x` (objects: `clone()`, 32.5)
	[ ] 48.1 Moving
		Assignment, `this.f = a`, `list.add(a)`, `return a` move
		Use after a move: a compile error; a new value brings the name back
		A move in one branch of an `if`: dead after it unless every branch gives a new value
		A move inside a loop: an error unless each pass gives a new value
		Lists and Maps move too; strings stay values (copied)
		A struct holding a List / Map / object moves as a whole
		A struct's fields can't be moved out - only borrowed (D.026)
		Migrate tests and examples that rely on `b = a` sharing
	[ ] 48.2 Borrowing
		Passing to a function borrows (changeable unless readonly)
		Reading an element or a field (`Car c = fleet[0]`) is a local borrow - the owner is frozen while it is used
		A struct's collection only lends itself - never moved out (user)
		Taking an element out: `removeAt` / `removeLast` (a move)
		A function value can't capture a borrow
	[ ] 48.3 At the call: `byVal`, `byRef`, `readonly`
		`log(readonly acc)`: the caller's demand - an error if log changes it
		The same project: errors at the call and at the line that changes it
		A Fusion library: only its signature counts - the caller is responsible
		A library not written in Fusion: a warning when a borrowed value is passed (user)
	[ ] 48.4 `--interface` shows the readonly result of each public function
	[ ] 48.5 `shared` objects
		`shared Car c = a`: one more reader (counted)
		Only the holder that made it shared changes it
		`f(byRef pool)` from that holder lends the right to change it
	[ ] 48.6 Counting removed where moves make it unnecessary (covers 38.2)
	[ ] 48.7 Examples and SYNTAX_REFERENCE.md, tests with and without null checks (Rule 4b)

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
	[ ] 36.0 First small version - right after Task 32 (user, 2026-10-29): VS Code and Sublime
		Text / TextMate (macOS too) - keywords, types, numbers, strings with {name} / {@1},
		chars, comments, function names; installed by copying a folder (no marketplace)
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
	[ ] 38.2 (covered by Task 48 - moving by default) More moves where one owner is proven (after 32.10e): a variable's last use storing
		it (`xs.add(b)`, `field = b`, `Car d = b`) moves it instead of counting; no null check
		on a local just made (`Car c = Car()`) - a "last use" analysis over branches and loops
	[ ] 38.3 Weak references - break a circle of objects (32.10d warns where one can form)

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
		A reserved keyword (Task 46, 2026-10-29). Settings v1: Mailbox, WhenFull, Timeout, final. Roadmap phases
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
		(`[concurrency] resourceAsService = true`; direct access only in unsafe mode)
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
	[ ] 42.17 Collections and threads (Concurrency.md 3.12; settled 2026-10-31, D.057)
		An array, List or Map used by two or more threads gets a temporary service (42.19)
		`[collections] threads` picks its worker: "shared" pool (default) | "dedicated"
		`sharedThreads = 10` (default): the pool's size
	[ ] 42.18 Ownership in a service (user, 2026-10-31 - files/Service.md "Ownership in a service")
		S1 The worker is the only writer
		S2 The service owns its value; a request borrows it (read or change, by the signature)
		S3 Nothing escapes a request - `byVal` copies out
		S4 Readers in parallel: readonly requests together, a change alone (`Readers` setting)
		S5 Temporary services (42.19)
		S6 Into a request: borrowed for the request, moved in (send), or copied
		S7 A thread using two or more resources: a group service; waiting inside a request is an error
		S8 Plain counts inside a service, atomic only for handles
		S9 The thread-boundary check (42.22)
		S10 The Service interface (42.21)
	[ ] 42.19 Temporary services (Ownership.md section 6)
		Two or more threads use one variable: the compiler makes `service(acc)`
		The service owns it; the thread functions borrow it
		One request = one whole call (`deposit(acc)`); the others wait in the mailbox
		The parent's own use while threads run is a request too
		The last thread ends: the variable owns its value again
		`[concurrency] autoService = "on"` (a note per variable) | "warn" | "off" (an error)
	[ ] 42.20 Several resources: the group service (Ownership.md section 7, D.077)
		A service manages one resource; a group service several
		A thread using two or more resources: a group service - written (42.3) or made by the compiler
		It owns them while its requests run; its worker borrows them
		Done: it lets go, each variable owns its value again
		No thread holds two separate services at once (P2)
	[ ] 42.21 The Service interface (needs 32.5)
		`interface Service<T>`: send, `T fetch()` (the worker's next request), start, stop, state, waiting
		BasicService (one worker thread), SharedService (temporary), FileService, DatabaseService, HotPathService
		Settings checked against the implementation (`Core` only on a HotPathService)
	[ ] 42.22 The thread boundary - send and sync (Ownership.md truth table 5)
		send: a value goes to another thread, the sender no longer has it
		sync: many threads use a value through a service; only its thread changes it
		Worked out by the compiler, never written; errors say send / copy / service
	[ ] 42.23 `hotpath` functions: the H checks (files/Service.md "Hot-path services")
		H1 no allocating; H2 no blocking; H3 no count changes
		H4 no unknown calls; H5 no unbounded loops (a setting); H6 errors stay inside
		H7 fixed-size ring messages; H8 only the set-up allocates; H9 sizes from the hardware
	[ ] 42.24 `hotpath service`: a HotPathService - a dedicated thread that never sleeps (after 43.4 RingBuffer)
		T1 pinned to a core, real-time priority
		T2 an input ring (one / many producers, power-of-2, cache-line padded)
		T3 wait SPIN (default) or YIELD - never PARK
		T4 memory locked and touched at set-up
		T5 no replies - results go to other rings
		T6 a latency histogram and the `Budget` warning
		T7 a watchdog
		T8 set-up -> warm-up -> running -> drain -> stop
		Settings: Core, Ring, Producers, WhenFull (never WAIT), Wait, Budget, Priority, Prefault, WarmUp
		Project defaults: `[hotpath]` in fusion.toml
	[ ] 42.25 Examples per processor kept busy: CPU (trading), GPU, FPGA, NIC, DSP / audio, radio, NPU (files/Service.md table)
	(The thread view in the editor: 36.6. The service reference: files/Service.md)

#### 43 Core modules design (fusionlib) (user, 2026-10-24) [ ]
	The standard library's core modules, designed one at a time (spec "Fusion Standard
	Library (fusionlib)"). Plan first.
	[ ] 43.1 Time: hours, minutes, seconds, milliseconds, nanoseconds; days, months, years; time
		zones; epochs; durations and time calculations (a Math sub-module, user). Duration
		literals map to int milliseconds until then (42.16)
	[ ] 43.4 Collections module (user, 2026-10-30): more collection types beyond the core ones
		that are always there (array, List, Map) - first a RingBuffer: a fixed number of
		slots used round and round, the newest replacing the oldest; more later (with 32.9)
	[ ] 43.3 Currency module (user, 2026-10-29): how `money` (47.2) is used per currency -
		currency definitions with their decimal places (USD 2, JPY 0, KWD 3) and so their
		units (USD 100, JPY 100 in whole steps, KWD 1000), formatting, parsing, and exchange-
		rate conversion with rates the developer supplies.
		Hard rule: it never fetches prices or rates from an external API - the developer
		using it fetches the rates and gives them to it (see CLAUDE.md project notes)
	[ ] 43.2 Data formats module (user, 2026-10-28): read and write TOML, JSON, YAML, INI, XML,
		CSV (and others) in Fusion itself - recovering from broken settings and minor syntax
		mistakes where that is safe. Replaces the compiler's Python readers (Task 31) once
		the compiler is written in Fusion - a big task, after Fusion modules exist

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
	[POSTPONED - after Task 32] The builder pattern (user, 2026-10-30): a separate object that
		collects settings, then `build()` makes the result - a different idea from form B
		set-up (Classes.md section 4)
	From the Rust videos (user, 2026-10-29 - Notes/Program lang Compare.md):
	[ ] Errors for tools and AI agents: every error in one form (line, what failed, a `fix:`
		hint), and an optional machine-readable output (`--errors json`)
	[POSTPONED - needs `extern`] A Fusion library other programs load: a `.dll` / `.so` with a
		C interface, so Python and other languages can call Fusion code
	[POSTPONED - after the compiler no longer needs Python] `console` - one tool (not named
		cargo): `console build / run / test / add` (packages)
	[POSTPONED to 29.4] String pool (shared storage for identical text) - when pooling is on,
		strings are pooled and mutable strings use a StringBuilder internally (user note 2026-10-09)
	[POSTPONED to 38] StringBuilder for fast repeated appends (internal for mutable strings)
	[POSTPONED to 38] Garbage collection as a project-selectable memory strategy
	[POSTPONED to 38] Shared<T> / Weak<T> (decided in 12.7, not built); Unique<T> and `.move()` dropped - every object moves by default (D.080)
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
	[REPLACED by 47.2 - a long of minor units, never a decimal] money type (user, 2026-10-24 / 10-27): strict decimal for currency, default 0, written-out
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
	[REJECTED 2026-10-31, D.058] Changing a List / Map while looping, allowed by a setting -
		the collection being looped over is never changed; build a new one
	[ ] Map keys (user, 2026-10-27): values of any type; keys a non-empty constant string (never
		pooled) or a whole number 0 or above (byte, int - no floats). A map can bring its own
		hash function and key rules (e.g. only non-empty strings, or ints only). Today: keys
		are string, int or char. Combining: `m.add(otherMap)` (no `+`); a setting on the map
		decides a key already there - replace by default (user, 2026-10-27)
	[ ] Map literals: `Map<string, int> stock = {"apples": 3, "pears": 0}` (missed while writing
		examples/control_flow, 2026-10-11 - a map is filled one key at a time today)
	From the showcase review (user, 2026-10-23):
	[ ] `switch` as an alias of `match` (familiar from VB.NET); `elif` an alias for `else if`
		`match` stays the form in docs and examples (user, 2026-10-31 - D.065)
		`else if` for 2-3 checks; `match` / `switch` for a list of values
	[ ] Enum values with fixed constants, built by the enum's private constructor:
		`enum Planet { Mercury(3.7) ... }`, Planet.Mercury.gravity() / Planet.Mercury.Name
	[ ] Several return values only when `[functions] multipleReturns = true` (off by default);
		a function that can fail always has its Error last
	[ ] Operator overloading, off by default - `[language] operatorOverloading = true`
	[DONE - 32.2h] Namespaces: group related modules (several folders / libraries) under one name
	[ ] println with a line ending: the PC's own, or set in fusion.toml. Kept for later (user,
		2026-10-24); note for developers: `print` already ends the line
	[ ] `loop`: a `loop { }` with no break / return inside is a compile error (user, 2026-10-24),
		and the user is thinking of dropping the `loop` keyword - to review
	[ ] Struct settings (user, 2026-10-24): a struct is a value type and never null - it always
		has a value, so it may hold an empty List / Map / string but never null. In
		fusion.toml [structs]: holding List / Map (on by default - built), functions on
		structs (off by default, Task 32.1), classes inside structs (off by default)
	[DONE] Open: `int?` - decided with Task 30 (user, 2026-10-27): no `T?` types at all; `?` is
		used on a variable (`x?.method()`), and only class objects and enums can be null
		(Nullable_Values.md)
	Showcase [idea] list - to go through one by one (files/showcase/, user 2026-10-24):
	[ ] Import only some names from a module: `import geometry { square, circle }`
	[ ] A whole-program setting read from fusion.toml at compile time (`config.build.mode`)
	[ ] `++` and `--` as statements only (never inside an expression)
	[ ] Type tests with `is` (`if s is string`) - the spec uses `is` only for null
	[ ] `typeOf(x)` gives the type's name as text - for a parent type, the chain (32.7)
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
	[ ] fusion.toml: `[threads] poolSize = "auto"` (one per CPU core)
	[ ] fusion.toml: `[modules] paths` - extra folders searched for imported modules
	[DONE] fusion.toml: `[build] waitAtExit` - default false (user, 2026-10-28: for development,
		examples and testing; examples/fusion.toml turns it on); --headless never waits
	[DONE] `[structs] holdCollections` (default true) - the struct setting decided 2026-10-24
	(Already listed above: namespaces, operator overloading, println, map literals, loop)
	[POSTPONED - after MVP] Paged / memory-mapped strings: load only the part of a huge string in use
	[POSTPONED - with each feature] More error types (Task 26 list, 2026-10-16): NetworkError /
		TimeoutError (a network module), ParseError (JSON / data modules), CancelledError
		(threads), AssertionError (an `assert` statement), NotSupportedError (a backend that
		can't do something) - each an Error subtype
	[REPLACED by 47.5 - `fixed(255) string name`] Per-field string sizes (`string(255) name`) to match database columns
	[POSTPONED - needs references] Identity operator (same object in memory)
	[POSTPONED - after MVP] Multi-dimensional arrays (growable lists: done, 18.5.1)
	[POSTPONED to 32 / 33] Classes, interfaces, inheritance (32), generics (33); enums: Task 25;
		threading: no task yet

## Known limitations (by design for now)
	[ ] A string-holding variable can't reuse the name of one in an enclosing block (clear error)
	[ ] Single-quote comments disabled (clash with char literals) - 8 skipped tests
	[ ] Identifiers ASCII-only unless fusion.toml opts in (text and chars are Unicode since 18.3.2b)
