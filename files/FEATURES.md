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
- Find things: `grep -n "\[ \]" files/FEATURES.md` (open), `grep -n "POSTPONED" files/FEATURES.md`,
  `grep -rn "18\.3\.2" files/FEATURES.md files/taskSummary2.md task/` (one item everywhere)
- Detail: active task -> `files/taskSummary2.md`; finished -> `task/taskSummaryArchive.md`;
  not started -> `task/taskBacklog.md`. What the language can do today, with examples ->
  `files/SYNTAX_REFERENCE.md`

**Features become settings (user, 2026-10-24).** Each feature is designed so a project can
turn it on or off in `fusion.toml` where that makes sense, with a safe default. When an item
here is reviewed (for example the showcase [idea] list), decide whether it becomes a
setting, a fixed rule, or is discarded. Example - structs:
- a struct is a value type, never null: it always has a value;
- it may hold empty or filled `List`, `Map`, `string` (a setting, on by default since it is
  built);
- functions on structs: a setting, off by default;
- holding an object: allowed - null until set, shared when the struct is copied (user, 2026-11-01).

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

#### 31 Settings file formats - the postponed parts (31.1-31.4 done 2026-10-28: task/featuresArchive.md) [POSTPONED]
	[POSTPONED to 43.2] 31.6 `config.fusion` - a Fusion program whose only job is to create the
		settings file from the master template (user, 2026-10-28)
	[ ] 31.5 Enforce fusion.toml [safety] / [backend] (was 15.6; trigger: strict mode or a 2nd backend)

#### 33 Generics: the program's own generic functions and types (user, 2026-10-11) [ ]
	[ ] 33.1 Plan (List<T> / Map<K, V> are built in since 18.5)
	[ ] 33.2 Example (was 16.3)
	[ ] 33.3 Another implementation behind `List<T>` (from 32.6) - needs generic classes of your own

#### 34 Example program coverage (was 16) [ ]
	[POSTPONED - needs threading, no task yet] 34.1 Multithreading / async example (was 16.4)
	[POSTPONED to 38] 34.2 Memory model (Unique/Shared/Weak) example (was 16.6)

#### 35 Self-hosting phase 2 - fully independent (was 10.9-10.12) [ ]
	[ ] 35.1 The self-hosted compiler covers the whole language
	[ ] 35.2 Bootstrap twice: the compiler compiles itself, and that one compiles itself again
	[ ] 35.3 The whole test suite runs against it
	[ ] 35.4 Performance
	[ ] 35.5 The Python compiler retired; docs
	[ ] 35.6 No `[PARTIAL]` line left in Decisions.md - each finished or split (user, 2026-11-07)

---

#### 45 Arrays that grow at the end (user, 2026-10-27 - files/Arrays.md) [ ]
	Today an array's size is fixed when it is made, and the compiler must know it. An array
	will grow and shrink at its end only (an item never moves position); a List changes
	anywhere.
	[ ] 45.1 Each array knows its own length at run time (like a List), so an array can be
		replaced by one of another size (`numbers = make()`, `numbers = [1, 2, 3]`)
	[ ] 45.2 Empty arrays: `int[] numbers` and `int numbers[]` (was 30.10)
	[ ] 45.10 Arrays live on the heap and follow the List rules (Decisions.md D.025, user 2026-10-31)
		[ ] An array as a Collection<T> value (from 32.6) - removing blocked
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
	[DONE - 32.4] 45.9 `foreach (string item in names)` over arrays, lists and maps
	[ ] 45.7 The array being looped over can't be changed inside the loop (user, 2026-10-31, D.058)
		Any loop: `for` and `foreach` - a compile error where seen, else ModifiedWhileLoopingError
		Build a new array from it instead: loop over `a`, add to `b`
	[ ] 45.8 An array used by two or more threads gets a temporary service (D.057, 42.19) - with Task 42
	[ ] 45.6 Docs and examples: files/Arrays.md, SYNTAX_REFERENCE, spec "Arrays"

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
	[ ] 47.5 The `fixed` prefix (user, 2026-10-31 - files/Ownership.md, files/Service.md)
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

#### 48 Ownership: move, borrow, share (user, 2026-10-31) [ ]
	After all of Task 32 (user)
	Design and truth tables: files/Ownership.md
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
	[DONE] 48.1 Moving (tests/test_ownership_moves.py) - `[memory] assignment = "move"`, the default since 48.9 (D.102)
		Assignment, `x.f = a`, `list.add(a)` / insert, `m[k] = a`, `[a, b]`, `return a` move
		Use after a move: a compile error; a new value brings the name back
		A move in one branch of an `if` / `match`: maybe moved after it; in a `try`: maybe moved in the `catch`
		A move inside a loop: an error unless each pass gives a new value
		Lists, Maps, objects, interface values and structs holding them move; strings and plain structs copy
		A struct's fields can't be moved out - only borrowed (D.026): done in 48.2
	[DONE] 48.2 Borrowing (tests/test_ownership_borrows.py)
		Passing to a function borrows; a function that keeps a parameter (stores, adds, returns it) takes it -
			the call moves it, followed through the calls (D.100); a method's `this` is always borrowed
		An element, a field or a for loop's variable is a local borrow - the owner is frozen until its last use (D.101);
			while the borrow changes it, the owner can't be read either (R4)
		A borrow can't be stored or returned; a field or an element can't be moved out (D.026) - `byVal` copies
		A struct made with a List / object moves it; a for loop's collection can't change (beyond D.058's method calls)
		[POSTPONED to 33] Taking an element out as a move: `removeAt` returns nothing today - needs a method
			that returns the element (`removeAt` / `removeLast` giving it back)
		[POSTPONED to closures] A function value can't capture a borrow - ready, but lambdas can't capture yet
		Not followed yet: the classes answering an interface / virtual function, a function value that keeps a value
		A cast moves, back to the class too; `byVal` copies, `byRef` borrows (D.104, user)
		[POSTPONED to working programs] Review: a method's `this` is always borrowed (D.103, user) - recheck once
			working programs can verify it independently
	[DONE] 48.3 At the call: `byVal`, `byRef`, `readonly` (tests/test_ownership_at_the_call.py)
		`log(readonly acc)`: the caller's demand - an error if log changes or keeps it, through every call; every mode
		The same project: errors at the call and at the line that changes it
		`byRef` on an object too (was List / Map only); with "move" byRef / readonly only lend - an error given to
			a function that keeps it, or stored; `Car b = byRef a` is a local borrow
		Found with it: a NullError inside a called function skipped the caller's catch (the '.' check didn't
			count as failing) - fixed
		[POSTPONED to 39.3] A Fusion library: only its signature counts - the caller is responsible
		[POSTPONED to 39.3] A library not written in Fusion: a warning when a borrowed value is passed (user) -
			Fusion has no libraries / extern functions yet
	[ ] 48.4 `--interface` shows the readonly result of each public and internal function - never private (D.115)
	[POSTPONED to a real need] 48.5 `shared` objects (user, 2026-11-03 - D.106): not added yet; assignment
		moves, `byVal` copies, `byRef` already shares the object; the word kept for when a real need shows
		The design if it comes back: `shared Car c = a` one more reader; only the holder that made it
			shared changes it; `f(byRef pool)` from that holder lends the right to change it
	[ ] 48.6 Counting removed where moves make it unnecessary (covers 38.2)
	[ ] 48.7 Examples and files/SYNTAX_REFERENCE.md, tests with and without null checks (Rule 4b)
	[ ] 48.8 Release the `Unique` keyword - no `Unique<T>` or `.move()` (D.080)
	[DONE] 48.9 Migrate, then make "move" the default (D.102)
	[ ] 48.10 R4 changed (D.123): while a borrow changes a value its owner may still be read - only changing it
		another way is an error (today reading is an error too - 48.2)
	[ ] 48.11 A setting per borrow rule (D.124): one owner (`assignment`), one writer, a borrow never outlives
		its owner - names decided when built; files/fusionSettings.xml then
	[ ] 48.12 Storing `this` shares the object, counted (D.103): `cars.add(this)` - one car in several
		collections; freed when the last holder lets go - check today's behaviour, tests
		[DONE] The examples: byRef where sharing is meant, byVal where a copy (6 SYNTAX_REFERENCE, classes_demo)
		[DONE] The self-hosted compiler pinned to "share" (selfhost/fusion.toml, D.107) - its context handling
			is reworked for "move" with Task 35
		[DONE] `[memory] moveFieldOut` (default false, D.108): fields only borrowed; true = as Rust, a field may
			leave a struct the function owns and the struct is gone
		[DONE] `byVal` on a struct clones its objects too (D.097 - was shared); a case's names are new variables
		[DONE] A getter lends - its result borrows from the object; an iterator made with its collection too (D.109)
		[DONE] The tests: written for "move" (byRef / byVal), or `@pytest.mark.share` where "share" itself is tested
		[DONE] A for loop may set an element's value (27.2e) - unless the elements move
		[DONE] "move" the default

#### 50 readonly results and a deep const (user, 2026-11-03) [ ] - after Task 48
	Rules shown: files/showcase/Ownership.fusion; the skill .claude/skills/fusion-ownership
	[ ] 50.1 A readonly result, part of the signature (D.110): `public readonly Engine function getEngine()`
		The caller gets a read-only borrow: `e.kind = ...`, passing e to a function that changes it - errors
		No `readonly` in that function's body - `return readonly this.engine` is an error (the signature says it)
		`Engine e = byRef car.getEngine()`: an error - byRef asks to change what is readonly
		`byVal car.getEngine()`: a copy the caller may change
		Open (user): what such a function may return - a member of the class, a new object - decided while building
	[ ] 50.2 `const` on an object is deep (D.112): `const Car c` - no field set, no method that changes it;
		a `byVal` copy (or a function returning one) may change (today only Lists, Maps and structs are deep)
	[ ] 50.3 Tests - every allowed / not allowed case of D.110-D.113 (Rule 4c); Ownership.fusion tags [built]
	[ ] 50.4 `readonly` on a copy is a warning, not an error (D.113): a number result, and `f(readonly n)` on an
		int / string (an error since 48.3)

#### 51 Documentation clean-up: folders and Markdown files (user, 2026-11-07) [ ] - soon
	Markdown stays the format (no HTML pages for now); Decisions.md keeps its format
	Proposal: files/DocumentationSystemProposal.md (from the Mac) - plan: files/taskSummary2.md Task 51
	[DONE] 51.1 Root files moved to files/ (debug scripts to debug/); the root keeps CLAUDE.md, README.md,
		Decisions.md, main.py, check.py, pytest.ini; paths in code and docs updated
	[DONE] 51.2 Decisions.md: a short "Why" column for all 112 decisions (none invented - blanks listed for
		the user); a PROPOSED status (only the user makes it ACTIVE); no superseded rows
	[DONE] 51.3 OpenQuestions.md next to Decisions.md - one line per open question
	[DONE] 51.4 Main.md in the root - what Fusion is for + the map of every file (from CLAUDE.md)
	[ ] 51.5 Split the spec into files/spec/NNN-Topic.md (then files/FutureFeatures.md) - file list shown first;
		no front matter for now - plain Markdown first (user, 2026-11-07)
		[ ] Navigation (user, 2026-11-08 - mockup Notes/showcase): each file starts and ends with
			`[< previous](..) | [Main](../../Main.md) | [next >](..)` - the first has no previous, the last no next;
			files/spec/index.md lists every spec file as a link; Main.md's paths become clickable links;
			a long file gets a contents list of links to its own sections; a script writes the nav lines
			from the index order, so they never drift (tools/doc_nav.py, the "nav" check)
		Root navigation (user): Main -> Decisions -> OpenQuestions -> README, each linking to the spec index;
			spec files link only to each other and their index - never back to the root
		[DONE] index.md, 010-Philosophy, 020-SemanticContract, 030-Types, 031-Arrays, 032-Strings, 033-TypeCasting,
			040-Functions, 041-Lambdas, 042-MultipleReturns,
			050-Classes, 051-Inheritance, 052-Interfaces,
			060-Structs, 061-Enums, 070-ControlFlow,
			080-Null, 081-Autoboxing, 090-Memory,
			100-Concurrency, 110-Generics, 120-Errors (2026-11-10), 130-Comments, 131-AutoDocs,
			140-Collections (2026-11-11), 150-Modules, 160-GameExample, 170-Build (2026-11-12),
			180-StandardLibrary, 181-fusionlib-Core, 182-fusionlib-Extended, 183-fusionlib-IDE,
			190-Callbacks, 191-Interop, 200-ReservedWords, 210-FeaturesSummary,
			220-Comparison (2026-11-12) - every section moved
		[DONE] 001-TomlSettings (user, 2026-11-08): every project setting; 000-009 kept for high-level files;
			"Built" generated from files/fusionSettings.xml (tools/settings_doc.py, the "settings" check)
		[DONE] 001 part 2: every setting decided so far - go through Decisions.md, the design docs, FEATURES,
			files/showcase/fusion.toml - into "Decided, not built"
	[DONE] 51.5a Bring files/spec/100-Concurrency.md up to date (user, 2026-11-10) - detail in task/taskSummaryArchive.md
		[DONE] 1 Gather (2026-11-10): the inventory in files/taskSummary2.md - 7 clashes / gaps found;
			no line limit on the file for now (user)
			was: go through every concurrency source; one list of what is built, decided, designed, an idea,
			rejected or replaced - with where each comes from
		[DONE] 1b Reorganised (user, 2026-11-10): Index; 1 summary and comparison; 2 traps (what solves each);
			3 the service model (primary); 4 other models - mutex, channels, async ... (for Lang.<language>.Fusion,
			Task 49); 5 built; 6 to settle (9 items); 7 the earlier text kept for review - tables throughout
		[DONE] 2 Clashes and gaps (2026-11-10): the user's provisional answers in spec 100 section 6;
			PROPOSED D.125-D.131; new 3.14-3.17 (channels, kinds of threads, sleep and wake,
			no thread state); 42.34-42.40; the 5 follow-up questions answered too (D.132, 3.18 baselines)
		[DONE] 3 Shown (2026-11-11): D.125-D.132 stay PROPOSED for now; `parallel for` kept as an idea
			(42.41); one file for now, split later; the showcase left for 42.40 (user)
		[DONE] 4 Rewritten (2026-11-11): the earlier spec text removed - the levels to 3.11, a counter
			with a Mutex and with a service in 1.2, an error return in 4.8, `unsafe` in the 4.2 example
		[DONE] 5 Decisions.md in step (CON.021-026, D.125-D.132 PROPOSED); showcase -> 42.40; checked, shipped
	[ ] 51.5b Split files/FutureFeatures.md into files/future/ (index.md + NNN-Topic.md, 31 files) - plan in
		files/taskSummary2.md, waiting for approval (2026-11-13)
	[ ] 51.6 A link check in check.py
	[POSTPONED - after 51] 51.7 HTML pages for people (a kit.js template, generated from the .md) - only if needed
#### 52 Classes, value types and null - follow-ups from the open questions (user, 2026-11-07) [ ]
	From the "why" of D.008, D.009, D.010, D.055 - some to build, some to recheck first
	[POSTPONED to closures - SYN.028] 52.1 Form D (CLS.016, D.119): a set-up block on an abstract class or an interface - where it is
		implemented in place (form B sets a value up; form D gives the missing functions) - design first
	[ ] 52.2 Recheck `implements Default` (CLS.014, D.010): a variable of the type is never null in every
		case (fields, statics, Lists, after a move); the developer writes the default values - tests per case
	[POSTPONED - a setting later] 52.3 `private` on a top-level item allowed by a setting (CLS.017, D.008);
		off for now - private hides a class's detail, internal is for the namespace / module
	[ ] 52.4 A `Length` interface (TYP.017): strings and arrays (value types) carry `length()` as if they
		were objects - made internal to the type by Fusion, so `s.length()` works on null and "" alike;
		later more built-in methods the same way - design first
	[ ] 52.5 Build D.055 (decided 2026-11-07): `length()` never null - 0 empty, -1 null (string, array, List,
		Map with `nullable` on); the -1 only in a comparison (`if` / `while`), elsewhere a NullError (a compile
		error where it can be seen); tests with and without a null check (Rule 4b)
	[ ] 52.6 An interface's functions are public or internal - `private` on one a compile error (D.114, CLS.019)
	[ ] 52.7 Null checks at compile time (D.116, D.117): a `?.` comparison warns; `!` around one an error (a
		`[conditions]` setting allows it, then a warning); an object surely null when passed - an error; a
		`?` parameter without a null check - a warning; a `Default` left null - an error

#### 53 Check the Core language (user, 2026-11-07) [ ]
	https://core-lang.dev - its design (https://core-lang.dev/design.html - simplicity, which we share) and
	code (https://codeberg.org/core-lang/core): ideas worth taking, and whether "CoreFusion" / "FusionCore"
	clash with it (the rename - GOL.009, after self-hosting)
	[ ] 53.1 Read its design principles - compare with Fusion's (Decisions.md GOL)
	[ ] 53.2 The name: CoreFusion / FusionCore next to Core - a clash or not

#### 55 Review the ChatGPT notes: features, domains, DSLs (user, 2026-11-09) [ ]
	From the user's Mac notes (ChatGPT - limited knowledge of Fusion); review with Claude Code: for each
	idea decide a setting, a fixed rule, already decided / built, or discarded (Decisions.md, Rule 3b)
	[ ] 55.1 Notes/Fusion_Language_Feature_Analysis.md - languages to study, features as settings,
		config organisation, what must not be configurable, an injectable language architecture
	[ ] 55.2 Notes/Fusion_Application_Domains_and_Targets.md - application domains, execution targets,
		domain modules, capturing customer requirements
	[ ] 55.3 DSLs: Martin Fowler, "Introduction to Domain Specific Languages" (external vs internal DSLs,
		trade-offs) - https://www.infoq.com/presentations/domain-specific-languages/ - does Fusion want
		internal DSLs (modules) or external ones (HIDL, Task 41)

#### 56 Loop safety: the `check` keyword (user, 2026-11-09 - SYN.033, files/spec/070-ControlFlow.md) [ ]
	A loop's `end loop with {N}` part holds `check` blocks - a health / limit check, run every Nth pass -
	and `check interrupt(signal, data)`, the loop's safe point for Shutdown / Pause / Stop (42.26, 42.27 build on it)
	[ ] 56.1 Questions first (OpenQuestions.md, with example code and options A / B / C):
		the name `check` - keep it, rename it, or drop the `with` part and keep only interrupts and the setting
		`{N}` - every Nth pass: the right form, or a setting
		the iteration limit: `[safety] maxIterations` (default 0 = no limit - decided) per project; per loop
			`{100000}` or nothing; is 10,000,000 too small for large database work (user note in 070)
		visible only when a setting asks for it (user note in 070) - what the compiler adds when the loop
			says nothing
		RAM / CPU monitoring and "adjusts limits to available RAM" (spec text, not decided) - keep or drop;
			it costs speed on every loop and clashes with the hot path (42.23)
		`#[max_iterations]` / `#[no_loop_protection]` in the spec - Fusion has no `#[...]` attributes: drop
		`exit loop` / `continue loop` inside a check - the same as `break` / `continue`, or words of their own
		User's first answers (2026-11-09) - to confirm in 56.1, then Decisions.md:
			Keep the name `check`; it can also serve as a debug tool
			A check runs after each loop pass, by the iteration; it holds a single condition to be met
			It is not for normal program control - only for what may affect the loop: a shutdown event,
				a loop limit reached
			Its job: exit the loop when the condition is true
			No `break`, `continue` or `continue loop` in it - carrying on is implicit; it cannot fall through
			It may contain `exit loop` - out of the inner loop or an outer one (loop labels)
			Forms:
				check <condition> { ... code block ... }   // cannot fall through
				check                                      // every pass (or every {N}th, when {N} is set)
				check 20                                   // every 20th pass
				check >= 10000                             // when the pass count is 10000 or more
				check !isHealthy()                         // run the method every pass
				check 50 !isHealthy()                      // run the method every 50th pass
				check InterruptSignal.Stop                 // when the interrupt is Stop, run the block
				check interrupt(signal, data)              // several interrupts, handled in the block
	[ ] 56.2 Bring files/spec/070-ControlFlow.md in line with the answers (old 1,000,000 default, the
		attributes, `fusion.config.max_iterations` -> `[safety] maxIterations`)
	[ ] 56.3 Make `check` a reserved word (src/lexer/keywords.py, the spec's Reserved Keywords) - a program
		using `check` as a name gets a clear error
	[ ] 56.4 Build `end loop with` + `check` blocks, then `{N}`; `[safety] maxIterations` built
		(files/fusionSettings.xml); tests, an example in files/SYNTAX_REFERENCE.md (Rule 4)
	[POSTPONED to 42] 56.5 `check interrupt(signal, data)` - needs the interrupt signals of Task 42 (42.26, 42.27)

#### 57 Namespaces and modules (user, 2026-11-12 - D.136, files/spec/150-Modules.md) [ ]
	A namespace is a supplier's group of modules, and a folder holding them; a module is one logical unit
		(one file or several); a name in full is `Namespace.Module.Name`
	[ ] 57.1 Design (when it is built - user): the namespace and module lines in a file and their syntax; the
		folder layout; what `internal` means (the module or the namespace); a file without a module line
		(the main program); finding a module's files (`[modules] paths`, MOD.005); a plan before building
	[ ] 57.2 Importing a namespace with an alias (`import SQL as Q`); `SQL.Database.createConnection(...)` next to
		`Fusion.Database.createConnection(...)`
	[ ] 57.3 Same namespace name from two suppliers: a reverse company domain in the namespace (`com.example.SQL`)
	[ ] 57.4 Build it: the loader, `--interface`, the examples with modules (shop, wordcount) and their tests
	[ ] 57.5 Fusion's own libraries under `namespace Fusion` (today's text says `namespace Core` - FusionTemplate.md,
		the showcase): bring them in line
	[POSTPONED - needs `extern`] 57.6 One module compiles to one library: `Fusion.IO.dll`, `SQL.Database.dll` (MOD.003)

#### 58 Script mode: Fusion written and run like a Python script (user, 2026-11-12 - SET.013, files/spec/170-Build.md) [ ]
	For a quick script (or a few): write it and run it, without setting up a whole compiled app
	[ ] 58.1 Design, plan first: `fusion run tidy.fusion` (today `python main.py`); no project and no
		fusion.toml needed (none written for a script); code at the top level runs in order, without a
		`main` - or `main` still required; a `#!` first line on Linux / macOS; arguments and exit codes
	[ ] 58.2 How it runs: compile in the background and run at once, the program cached so the next run
		starts fast (C + GCC, as today) - or an interpreter later; compare start-up times
	[ ] 58.3 What a script may use: the same language and checks as a compiled app (safe by default);
		the std library layer
	[ ] 58.4 Build it, with an example script and tests

#### 59 Faster checks: run only the tests the change needs (user, 2026-11-13) [ ]
	The full suite takes ~4 minutes (2,710 tests; the end-to-end ones compile with GCC under the leak check)
	[DONE] 59.1 Documents only changed: `--ship` runs only the document checks; `--full` forces every check;
		`check.py --docs` (CLAUDE.md Rule 7)
	[ ] 59.2 Find what takes long: time each test file (`pytest --durations=30`), the examples and the leak
		check; list the slowest
	[ ] 59.3 Run only the tests the changed code needs: map source folders to test files (lexer ->
		test_lexer*, codegen -> the end-to-end tests, ...); the full suite after a whole task is complete
	[ ] 59.4 Faster end-to-end tests where possible: build several programs per GCC call, run tests in
		parallel (pytest-xdist), cache unchanged builds

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
		(user, 2026-10-23; files/Concurrency.md section 3.3 H - design later)
	[ ] 36.5 Later: a language server (LSP) - errors as you type, go to definition, completion -
		built on the self-hosted compiler, one server for every editor
	[ ] 36.7 A hint showing how number conditions are set for the project (`[conditions]
		numbers`, Task 30.9) - e.g. on `if count` (user, 2026-10-27)

#### 37 Deferred decisions (rest of 15 - user: after self-hosting, some become own sub-tasks) [ ]
	[ ] 37.1 Stdlib runtime lowering decision (was 15.2)
	[ ] 37.2 Operator operands evaluated in C's order (`next(c) - next(c)`); call arguments are
		left-to-right already (was 15.12)
	[ ] 37.3 Incremental builds, stable symbol identities (ChatGPT review; files/notes.md step 5)

#### 38 Memory model: Unique / Shared / Weak, GC as a project option (was 15.5) [ ]
	[ ] 38.1 Scope it (semantics decided in 12.7, not built)
	[ ] 38.2 (covered by Task 48 - moving by default) More moves where one owner is proven (after 32.10e): a variable's last use storing
		it (`xs.add(b)`, `field = b`, `Car d = b`) moves it instead of counting; no null check
		on a local just made (`Car c = Car()`) - a "last use" analysis over branches and loops
	[ ] 38.3 Weak references - break a circle of objects (32.10d warns where one can form)
	[ ] 38.4 Manual memory in `unsafe` (`allocate`, a raw malloc) never freed: the compiler frees it at the end
		of the scope it is declared in (user, 2026-11-11 - D.134, files/Object_Lifetime.md 2); one returned or
		stored moves to its new owner (user, 2026-11-11)

#### 39 Library trust, isolation & security (was 19) [ ]
	[ ] 39.1 Compiler-verified capability signatures (was 19.1; layers from 18.5.6 are the groundwork)
	[ ] 39.2 Project restrictions (pragma Restrictions-style) (was 19.2)
	[ ] 39.3 Closed, compiled, licensed libraries (was 19.3)
	[ ] 39.4 Sandboxing and resource budgets (was 19.4) - nothing trusted by default (D.122): a library without
		source is sandboxed (no files / network) unless the developer trusts it; the customer running the app
		may still forbid files / network
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
	full OS (PCs, servers, Raspberry Pi on Linux). An RTOS (FreeRTOS, Zephyr): no layer of its
	own - the IO standard library covers what exists there, HIDL creates the tasks and timers (D.118)
	[ ] 41.1 Grammar & format decision
	[ ] 41.2 Scope v1 vs. future layers
	[ ] 41.3 Memory model reconciliation
	[ ] 41.4 HIDL parser
	[ ] 41.5 Fusion code generation from HIDL
	[ ] 41.6 Compile-time hardware safety checks
	[ ] 41.7 Multi-language code generation (stretch)
	[ ] 41.8 Simulator & tooling (stretch)
	[ ] 41.9 Docs & examples
	[ ] 41.10 Hardware testing ideas from Maia (maia-eda.net): a DUT block, drive / expect vectors,
		clocks, bit widths - in the HIDL library, not the core (files/FutureFeatures.md "HIDL Library")

#### 42 Concurrency: services and threads (user, 2026-10-23) [ ]
	Goal: a million requests on one machine with many cores - no data races by construction,
	deadlocks and freezes prevented by rules (any that slip through become clear errors), no
	slowdown, a small memory / CPU footprint, very scalable. A resource becomes a service;
	manual locking is a last resort. Design: files/Concurrency.md (sections 3-4); overview:
	files/Concurrency_Traps.md. Plan first when the task starts.
	[ ] 42.0 Version one (agreed 2026-10-24, files/Concurrency.md 3.11): five rules - one owner,
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
		(starting point: files/Concurrency.md 3.7)
	[ ] 42.9 (after version one) Custom contention rules and schedulers (files/Concurrency.md 3.8); Rule.HIERARCHY default
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
		[ ] Priority "5.4.1" (user, 2026-11-07): weighted turns - in every 10, high gets 5,
			medium 4, low 1, so low-priority work never starves; custom shares allowed
			A level with no work gives its turns to the others (no turn wasted)
			Turns are spread through the cycle (H M H M H L ...), not in blocks of 5
	[ ] 42.15 WorkerThreadType per resource: AUTO (default - SHARED as more threads read it,
		SINGLE when its work is heavy) | SINGLE (workers dedicated to this resource: one thread
		or its own ThreadPool) | SHARED (shared workers from a specific ThreadPool); can be set
		by hand. Coalesce is a secondary setting; custom schedulers / rules / priorities: one
		method per class (files/Service.md)
	[ ] 42.16 Duration literals: `500ms`, `5s`, `2min`, `1h` - an int of milliseconds for now;
		also read from text (strings, fusion.toml). The full time module: Task 43.1
		[ ] Two precisions (user, 2026-11-07): everyday code and ordinary services - `int`
			milliseconds (`ms`, `s`, `min`, `h`); hot path (42.23, 42.24) - `long` nanoseconds
			(`ns`, `us`; needs `long`, 47), where Fusion controls the CPU directly (a pinned core
			that spins), not the operating system. Nanoseconds are exact for measuring (a
			monotonic clock); an OS sleep / wake is only ~1 ms (Windows) / ~50 us (Linux)
		[ ] Kept separate (user, 2026-11-07): two different kinds of timing, never mixed or
			converted into each other - `1s` / `2min` stay int milliseconds for convenience;
			nanoseconds are always long, so the two can't be confused. Mixing them is an error
	[ ] 42.13 The compiler checks P9 (a service handling a request calls only down the
		hierarchy, or sends without waiting) across modules - to be designed
	[ ] 42.17 Collections and threads (files/Concurrency.md 3.12; settled 2026-10-31, D.057)
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
	[ ] 42.19 Temporary services (files/Ownership.md section 6)
		Two or more threads use one variable: the compiler makes `service(acc)`
		The service owns it; the thread functions borrow it
		One request = one whole call (`deposit(acc)`); the others wait in the mailbox
		The parent's own use while threads run is a request too
		The last thread ends: the variable owns its value again
		`[concurrency] autoService = "on"` (a note per variable) | "warn" | "off" (an error)
	[ ] 42.20 Several resources: the group service (files/Ownership.md section 7, D.077)
		A service manages one resource; a group service several
		A thread using two or more resources: a group service - written (42.3) or made by the compiler
		It owns them while its requests run; its worker borrows them
		Done: it lets go, each variable owns its value again
		No thread holds two separate services at once (P2)
	[ ] 42.21 The Service interface (needs 32.5)
		`interface Service<T>`: send, `T fetch()` (the worker's next request), start, stop, state, waiting
		BasicService (one worker thread), SharedService (temporary), FileService, DatabaseService, HotPathService
		Settings checked against the implementation (`Core` only on a HotPathService)
	[ ] 42.22 The thread boundary - send and sync (files/Ownership.md truth table 5)
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
	[ ] 42.26 A block that can't sleep or be interrupted (user, 2026-11-02 - files/FutureFeatures.md "Threads,
		Schedulers and Services" 2): within one loop iteration the thread doesn't sleep, yield or take an
		interrupt; interrupts and requests wait in its mailbox until the next safe point (builds on `check interrupt`)
		Starving others: a request timeout (seconds) and / or `sleepEvery(5)`; long-running work (a large file
			loaded or downloaded) always on its own thread
		Issues: the OS can always pause a thread (only the hot path avoids it); safe points outside loops;
			how far the mailbox grows meanwhile
	[ ] 42.27 A system shutdown is always handled (user, 2026-11-02): the interrupt reaches services and loops
		where the critical logic is - the log file and database connections closed, nothing left unstable
		(the `Shutdown` setting, `final` clean-up 42.4)
	[ ] 42.28 Recheck later: an identity for everything (user, 2026-11-02 - files/FutureFeatures.md "An Identity
		for Everything"): a GUID per name and a small database of the hierarchy with the code's hashes, so
		the compiler can tell by GUID which variables / objects are in a thread or a group service
	(The thread view in the editor: 36.6. The service reference: files/Service.md)

	[ ] 42.29 A `Transaction` interface (user, 2026-11-07 - D.120): commit gives OK / FAILED, rollback; marks a call
		as part of a transaction - only OK commits. Design properly first. Also: a step that can't be undone
		(a log line, a send) inside one - a warning "put it last, or in finally"?
	[ ] 42.30 Compare services with the actor model and other languages - Erlang / Elixir, Akka, Go, Rust
		(user, 2026-11-10 - Notes/chat gpt actove vs service.md, from ChatGPT: limited knowledge of Fusion)
		ChatGPT's name for it: an "Actor-inspired Resource Service Model" - the compiler finds the resources,
			makes the services, decides how requests run; check what is new and what an actor already does
	[ ] 42.31 Service forms, each configurable for its situation (user, 2026-11-10 - Notes/chatgpt serverices
		understanding.md, ChatGPT: limited knowledge of Fusion); the hot path service (42.23) is one form
		Auto lanes (like lanes at an airport): the primary thread full or heavy - a new lane for DBAccount;
			could split by kind (one worker for Account, one for Price) when one is overloaded
		A limit on the threads, or use of the thread pool
		Forms: 1 a single thread; 2 several threads with a simple buffer; 100x many threads with ring
			buffers, simple buffers, or channels (other threads send to a named channel); a shared buffer;
			a buffer on the calling thread that the service asks for its requests
	[ ] 42.32 Request order by a monotonically increasing sequence number, not time + thread id - the
		time can differ per CPU core (user, 2026-11-10)
	[ ] 42.33 Explain services to others (user, 2026-11-10): ChatGPT kept answering with the usual locks
		Two text boxes, ready to copy: one for people, one for another AI - in files/Service.md or
			files/Concurrency.md
		Diagrams showing how a service works (callers, mailbox, worker, resource)
	[ ] 42.34 Channels in a service (user, 2026-11-10 - provisional; D.126 proposed; spec 100 3.14)
		A default mailbox with no name - every service and group service; named channels (writes, reads,
			status) for many threads with special work; an interrupt channel; outbound channels
		The interrupt channel: only the OS sends (D.132 proposed)
		Design a `Channel` interface and a `ChannelType` enum (INBOUND, OUTBOUND) - first check how other
			languages do it and best practice: Go channels, Rust mpsc / crossbeam, Java BlockingQueue,
			C# System.Threading.Channels, Erlang mailboxes (pseudo code in spec 100 3.14)
	[ ] 42.35 Kinds of threads (user, 2026-11-10 - spec 100 3.15): worker, writer, reader, field reader
		(named), watcher, scheduler, outbound; one thread may do every job, some pooled or shared
		The names are suggestions, perhaps an enum (`ThreadType`); the compiler tells threads apart by ID
	[ ] 42.36 Sleep and wake (user, 2026-11-10 - D.131 proposed; spec 100 3.16): the parent holds the
		worker's channel, checks it, wakes the worker; a worker stays awake while it has tasks
		The parent's timings: baseline from other languages gathered (spec 100 3.18 - Go, Tokio, .NET,
			Erlang, Java); set and tuned once threads work
	[ ] 42.37 A service's interrupt handler `service(x).setCheckInterrupt(signal, data) { }` (user, 2026-11-10 -
		spec 100 3.14) - with 56.5; no `exit loop` / `continue loop` in it (D.132 proposed); not handled:
			Shutdown terminates, Pause suspends, others nothing; interrupts only from the OS, passed down
	[ ] 42.38 Locks off by default (D.125 proposed): `[concurrency] locks` in fusion.toml, a lock inside
		`unsafe`; the setting into 001-TomlSettings once decided
		The compiler unlocks a lock at the end of the scope it is declared in, even if the developer
			forgot it (user, 2026-11-11 - D.133)
	[ ] 42.39 A thread holds no state (D.130 proposed; spec 100 3.17): variables made in `run { }` are its
		own; thread-local storage only in `unsafe`
	[ ] 42.40 The showcase section 18 rewritten (user, 2026-11-10): files/showcase/Fusion_showcase.fusion
		"Concurrency (no task yet)" -> services, temporary and group services, channels in a service, the
		interrupt handler, `go`, async / await (both forms), a mutex inside `unsafe`, `check interrupt`
		Keywords: `service`, `go`, `async`, `await` reserved already; reserve `unsafe` and `check` (56.3);
			decide whether `channel` / `lock` are keywords or library types (`Channel<T>`, `Mutex`)
	[ ] 42.41 `parallel for` - each loop pass may run on a pool thread (idea, from the earlier spec text;
		user, 2026-11-11: kept for the future, `go` used for now)
#### 43 Core modules design (fusionlib) (user, 2026-10-24) [ ]
	The standard library's core modules, designed one at a time (spec "Fusion Standard
	Library (fusionlib)"). Plan first.
	[ ] 43.1 Time: hours, minutes, seconds, milliseconds, nanoseconds; days, months, years; time
		zones; epochs; durations and time calculations (a Math sub-module, user). Duration
		literals map to int milliseconds until then (42.16)
	[ ] 43.2 Data formats module (user, 2026-10-28; extended 2026-11-01 - files/FutureFeatures.md
		"Data Formats Module"): JSON, XML, TOML, YAML, INI, MD (and CSV, others) read into an
		in-memory document, easy to read and change, then saved - load / save, from or to a
		string; recovering from minor syntax mistakes where that is safe. In fusionlib, not the core.
		Replaces the compiler's Python readers (Task 31) once the compiler is written in Fusion -
		a big task, after Fusion modules exist
		[ ] JSON and XML written in the code: (FILE_LANG.XML)"""...""".save("a.xml") - needs
			multi-line strings (Later); the marker's form, compile-time checks, escaping open
	[ ] 43.3 Currency module (user, 2026-10-29): how `money` (47.2) is used per currency -
		currency definitions with their decimal places (USD 2, JPY 0, KWD 3) and so their
		units (USD 100, JPY 100 in whole steps, KWD 1000), formatting, parsing, and exchange-
		rate conversion with rates the developer supplies.
		Hard rule: it never fetches prices or rates from an external API - the developer
		using it fetches the rates and gives them to it (see CLAUDE.md project notes)
	[ ] 43.4 Collections module (user, 2026-10-30): more collection types beyond the core ones
		that are always there (array, List, Map) - first a RingBuffer: a fixed number of
		slots used round and round, the newest replacing the oldest; more later (with 43.5)
	[ ] 43.5 The study of collection kinds - Java, C#, Rust, Go, Python - which to offer in fusionlib (was 32.9)
	[ ] 43.6 Plan every fusionlib module - just its name first (user, 2026-11-01); each designed
		later, one at a time (files/FutureFeatures.md "fusionlib: Every Planned Module")
	[ ] 43.8 DocWiki (user, 2026-11-12 - files/spec/183-fusionlib-IDE.md): a separate app that runs alongside
		the developer's app (a doc wiki made by hand or from sources, not part of the app's code), and
		`Fusion.DocWiki` built into an app - its own wiki, e.g. showcasing the Fusion language or a library;
		documents Fusion code, other languages and DLL files (even from another language), or a custom wiki
	[POSTPONED to 42 + file I/O] 43.7 File handle manager (user, 2026-11-07): a FileManager
		(later the same for databases) keeps every open file, keyed by its path - each file its
		own service with its own reader / writer thread; parts of the program (or a file the user
		picks) opening the same file get the handle already open, not a second one that clashes.
		Opening a file directly, without the manager, still works as usual

#### 49 Multi-language support: `Lang.<language>.Fusion` modules (user, 2026-11-03) [POSTPONED to 35]
	Design: files/Fusion_Multi_Language_Compiler_Architecture.md - after self-hosting (D.105)
	A language module brings its own lexer, parser, AST and rules; the compiler loads it through one
		injection point and never holds C / Java / Python logic itself (MOD.011; SYN.037)
	Two capabilities: migrate (source -> Migration IR -> Fusion AST -> new .fusion files, the
		original never changed) and compile the language by its own rules (separate, later)
	[ ] 49.0 A gap table per language, before 49.1 (user, 2026-11-12): every feature of C, C++, Go, Java, C#,
		Rust, Python, JavaScript - its syntax, meaning, run time and standard library - and where it belongs:
		Fusion has it / partly / needs it; a gap is placed, not just listed:
		In Fusion's core - only when Fusion itself wants it (closures 52.1, generics 33, GC 38, `extern`)
		Only in that language's module - not part of Fusion: e.g. `Lang.C.Fusion` brings the C preprocessor,
			macros and pointer arithmetic; Python's dynamic objects and `eval` only in `Lang.Python.Fusion`
		Shared by a family of languages - one piece several modules use: the C family (C, C++, Objective-C),
			the JVM (Java, Kotlin), .NET (C#, VB.NET), dynamic scripting (Python, JavaScript, Ruby)
		A flavour or version of one language: C89 / C99 / C11 / GNU C, Python 2 / 3, Java 8 / 21, ...
			its own module named `Lang.<language>.<optional flavour>.Fusion` - `Lang.Python.2.Fusion`,
			`Lang.Python.3.Fusion` (user, 2026-11-12 - D.137)
		Passed through: interop with the real library (FFI) instead of a rewrite - NumPy, the JDK
		The table feeds the language modules (49.5, 49.9) and the precepts (Task 54)
	[ ] 49.1 The language-module contract and the injection point: registry, capabilities, versions
	[ ] 49.2 `Lang.Fusion.Fusion` first - Fusion as its own module proves the design
	[ ] 49.3 A Fusion source writer: Fusion AST -> readable .fusion (today's code generator writes C) -
		also serves formatting and upgrading old syntax
	[ ] 49.4 The Migration IR - small, grown from real translations (not the Task 40 backend IR)
	[ ] 49.5 `Lang.C.Fusion`: a subset of C, then C -> Fusion for types, functions, expressions,
		control flow; checked by Fusion's own semantic pass
	[ ] 49.6 Pointers, allocation and lifetimes -> Fusion ownership (needs Task 48)
	[ ] 49.7 A migration report and sidecar notes per node: converted, needs review, unsupported
	[ ] 49.8 Compiling C itself through its module (separate from migrating; GCC does it today)
	[ ] 49.9 C++, Java, Python modules - each on its own
	Open: language modules are code the compiler runs - trust and sandboxing (Task 39);
		their name next to `fusionlib.Lang` (files/FutureFeatures.md "Cross-Language Compilation Support")

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


#### 54 Precepts: a project that behaves like C, Java, Python, Rust (user, 2026-11-08) [POSTPONED to 35]
	A precept is a ready-made set of settings and behaviour, so a new project acts like a familiar
	language without editing fusion.toml by hand: `c.precept.fusion`, `cpp.precept.fusion`,
	`java.precept.fusion`, `python.precept.fusion`, `rust.precept.fusion` ... Built and checked only
	after self-hosting (Task 35); goes with Task 49 (language modules)
	[ ] 54.1 Design: what a precept holds (settings, defaults, warnings), how a project picks one, and
		how its own fusion.toml overrides a precept's setting
	[ ] 54.2 The first precepts, each tested against programs written the way that language works
## Later / advanced (after MVP)

Kept in Fusion's design, deliberately postponed - the simple version comes first.
	[POSTPONED - after Task 32] The builder pattern (user, 2026-10-30): a separate object that
		collects settings, then `build()` makes the result - a different idea from form B
		set-up (files/Classes.md section 4)
	From the Rust videos (user, 2026-10-29 - Notes/Program lang Compare.md):
	[ ] Errors for tools and AI agents: every error in one form (line, what failed, a `fix:`
		hint), and an optional machine-readable output (`--errors json`)
	[POSTPONED - needs `extern`] A Fusion library other programs load: a `.dll` / `.so` with a
		C interface, so Python and other languages can call Fusion code
		A module compiled to a DLL: its folders and files become one library, ready for a larger
			application (user, 2026-11-12 - MOD.003)
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
	[ ] Lists (user, 2026-10-27 - files/Arrays.md): add many at once (another list, a group of
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
		structs (off by default, Task 32.1); an object in a struct: allowed since 2026-11-01 (D.097)
	[DONE] Open: `int?` - decided with Task 30 (user, 2026-10-27): no `T?` types at all; `?` is
		used on a variable (`x?.method()`), and only class objects and enums can be null
		(files/Nullable_Values.md)
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
