# FEATURES.md - finished tasks and items (archived)

Every task and item marked [DONE] in FEATURES.md, moved here verbatim on 2026-10-27
(user: "only the open and POSTPONED will be kept"). Task numbers never change, so
commits, code comments and task/taskSummaryArchive.md (the plans and notes) still match.
New finished items are added here when a task is complete.

---

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

#### 28 Self-hosting phase 1 - the test run (was 10) [DONE]
	[DONE] 28.0 Prerequisites: analysis (was 10.1) and language features (was 10.2, by Task 18)
	[DONE] 28.1 The subset: exactly what the programs in examples/ need - measured by
		tools/example_subset.py: three tiers (18 / 12 / 14 programs), and gaps A-C (calling GCC,
		shared state, the C run-time) - task/selfhost_subset.md. Target: tier 1 (user)
		[DONE] 28.1.1 `run(command)`: run another program through the shell, wait, return its
			exit code; ProcessError if the shell can't start; std layer; on Windows the command
			goes to cmd exactly as written. Tested: exit codes, output order, a failing
			command, compiling + running a Fusion program from Fusion (a folder with a space),
			an example's exe, Notepad
		[DONE] 28.1.2 Shared state (gap B), measured with three lexer prototypes
			(selfhost/prototype/): a read-only source over `bytes` + one token returned per call
			is fast (20,000 lines in 0.05 s) - no compiler change needed. A struct copied per
			step is slow (5,000 lines: 7.5 s); `text[i]` on a non-ASCII string is very slow
			(52 s) - task/selfhost_subset.md "28.1.2 results"
		[DONE] 28.1.3 The C run-time as a shared file `runtime/fusion_runtime.h` (gap C): the
			includes + run-time every program shares (1,666 lines), written by
			`check.py --runtime` and checked; CCodeGenerator(runtime_include=...) writes a C file
			that only #includes it. All 45 examples print the same both ways (tier 1 is a test)
		[DONE] 28.1.5 `\{` and `\}` escapes: a literal brace in a string or char (found
			2026-10-24 - `"{ "` is an error, and the only way was "\u007B"; the self-hosted
			compiler writes C full of braces)
		[DONE] 28.1.4 `files/Builtins.md`: every built-in function (94), type class and List / Map
			method, generated from the compiler (`check.py --builtins`, tools/builtins_doc.py);
			the "builtins" check fails when it is out of date
	[DONE] 28.2 Lexer in Fusion (selfhost/lexer/lexer.fusion, about 600 lines): every token
		kind, the three block styles, string parts, escapes, numbers in every base; `--tokens`
		matches the Python lexer token for token on all 53 example files (tests/test_selfhost.py).
		Found: a bare `return` in `void main` gave invalid C (fixed in the Python compiler)
	[DONE] 28.3 Parser in Fusion (selfhost/parser/, about 800 lines; `--ast` prints the tree)
	[DONE] 28.4 Checker in Fusion - types checked in the same walk as generating (user decision:
		one walk), in selfhost/codegen/
	[DONE] 28.5 C code generator in Fusion (selfhost/codegen/, about 1,900 lines): all 18 tier 1
		programs print exactly what the Python-built ones print, same exit codes, leak-free
		(tests/test_selfhost.py); built in 5 slices
	[DONE] 28.6 Driver (selfhost/main.fusion): reads the file, writes C, calls GCC with run();
		--tokens, --ast, --runtime DIR, --leak-check
	[DONE] 28.7 Verify: `check.py --selfhost` - 18/18 tier 1 programs the same (output, exit
		code, leak check); also in tests/test_selfhost.py. (Originally:) the Fusion-built
		compiler.exe compiles every example, and those programs
		print the same as the Python-built ones
	[DONE] 28.8 Report: task/selfhost_report.md - what worked, what was awkward (12 entries),
		six suggestions for Phase 2

#### 44 Lessons from the self-hosting test run (task/selfhost_report.md, user 2026-10-26) [DONE]
	The six suggestions of the Task 28 report, most useful first - each makes the next
	self-hosting stage (Task 35) smoother. Plan first; each may become a fusion.toml setting
	where that makes sense (FEATURES.md, top).
	[DONE] 44.1 Module-level variables and constants (`int count = 0`, `const int LIMIT = 3`,
		`public ...` for other modules): set in order before main, freed when main ends, can't
		be hidden by a local name; `[modules] variables` (default true) turns variables off
	[DONE] 44.2 Any function can be called as a method on its first argument: p.moved(1, 2) is
		moved(p, 1, 2) - structs, built-in values, lists, maps, enums; list / map / enum methods
		come first; the method gets a copy. Functions inside structs: 32.1, a fusion.toml
		option, off by default
	[DONE] 44.3 A line break inside ( ) or [ ] continues the line - in both lexers (Python and
		selfhost/); braces still open blocks
	[POSTPONED - user, 2026-10-26: option A, keep the workaround] 44.4 An `Error` return type
		distinct from "can fail" (`Error function f()` means "returns nothing, can fail" - a
		function can't return an Error value; workaround: return the message, `Error(at(...))`)
	[DONE] 44.5 `_` for an unused `match` field (already built in Task 25 - now documented and
		tested); `end` and `var` are ordinary names (lowercase `end` closes a block only before a
		block word) - in both lexers
	[DONE] 44.6 Fast `text[i]` for any string: the run-time remembers the last position found in
		an owned non-ASCII string (forgotten when its memory is freed); the 28.1.2 prototype:
		52 s -> 0.03 s (5,000 lines), over 60 s -> 0.12 s (20,000)

From 34 Example program coverage (was 16) [ ]:
	[DONE] 34.0 Control flow (was 16.1, examples/control_flow) and modules (was 16.7, examples/shop)

From 39 Library trust, isolation & security (was 19) [ ]:
	[DONE] 39.0 Source-level attack defenses: Trojan Source, homoglyphs, ASCII identifiers (was 19.6)

From 40 IR layer and LLVM backend (was 11, 15.1) [ ]:
	[DONE] 40.0 Research & design (was 11.1)

From Later / advanced (after MVP):
	[DONE] Masking functions in the core string library: formatMask, digitsOnly, mask, maskEmail
		(design and all 9 decisions: spec "Masking", Task 18.3.6f; built 2026-10-10)

	[DONE] Fast `text[i]` for any string (found in 28.1.2, 2026-10-24) - done as 44.6

	[DONE] Bounds checks for fixed arrays - Task 27.1

#### 29 Mutable vs. fixed strings, templated strings, string pooling (was 17) [DONE]
	[DONE] 29.0 Prefixes decided (user, 2026-10-27): no `m"` (a plain string can change), no `f"`
		(`const string` is fixed), no `p"` (literals are already stored once); `a"` (ASCII) -
		with `extern` calls (Later); templates: `template string greet = "..."` (29.3)
	[DONE] 29.1 Changing a character in place: `s[i] = c` - that variable's text only, index
		checked, a wider character moves the rest (tests/test_string_put.py)
	[DONE] 29.2 Fixed strings = `const string` (no new type): `s[i] = c` on one - or on a string
		inside a const struct / array - is a compile error; a copy can change (spec "Constants")
	[DONE] 29.3 String templates: `template string greet = "Hello {@1} - {city}"`, then
		`greet("Ann")` - a fixed text that works as a function (no `t"` prefix, user
		2026-10-27); values counted at compile time; {name} read when called (a local template
		is expanded where it is called); passed where a function type is written (4b); private
		to its module (tests/test_templates.py)
	[DONE] 29.6 Examples (syntax_string_put, syntax_templates), spec "String Implementation" / "Constants", no new built-ins

#### 30 Nulls, empty values, number conditions, the conditional operator (was 14) [DONE]
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
	[DONE] 30.6 Docs & examples - shipped with each part: SYNTAX_REFERENCE (syntax_length, syntax_conditional, syntax_number_conditions), spec, Nullable_Values.md, Arrays.md

From #### 30 (reopened 2026-10-28 - null enums, case null, fall match):
	[DONE] 30.11 Enums can be null (tests/test_null_enums.py) - user, 2026-10-27/28: an enum is treated as a reference type
		like a class - `Status s` with no value is null, not the first value (today: the first
		value, Task 25). `s = null`, `== null` / `!= null` / `=== null` / `is null`,
		`s?.null` / `!s?.null`; using a null enum (toString, toInt, its data) is a NullError
		(a new built-in error type); the "first value can't hold the enum" rule (25.5) goes.
		`s?.toString() ?? x` waits for 30.2
	[DONE] 30.12 `case null` in a `match` (tests/test_case_null.py) - user, 2026-10-28: at most one, on any type (a library may
		send a null). A null never equals a case value: it goes to `case null`, else to
		`else`, else nothing runs - never a NullError. `break` inside any `match` ends the
		match; `continue` acts on the loop (it used to leave the loop)
	[DONE] 30.13 `fall match` (tests/test_fall_match.py) - user, 2026-10-28: falls through - after the matching case, the next
		cases' code runs too, until a `break` (as C / Java / C# `switch` do). A plain `match`
		never falls through

#### 31 Config file in any format: fusion.toml / .yaml / .json / .ini (was 20) [DONE]
	fusion.toml stays the default; the others are alternatives (a company that uses YAML,
	INI for legacy hardware / software). User decisions 2026-10-28: taskSummary2.md
	[DONE] 31.1 One reader per format, one set of checks (PyYAML for YAML while the compiler is
		Python; INI true / false only) - src/config/settings_files.py
	[DONE] 31.2 Finding the file: TOML first, then YAML, JSON, INI; none - a fusion.toml is
		written from the master template files/fusionSettings.xml (--no-new-config /
		FUSION_NO_NEW_CONFIG=1 turn it off). `[project] fusionSettingFormat` names the
		format; changing it rewrites the file and keeps the old one as .bak
	[DONE] 31.3 Tests (tests/test_settings_formats.py)
	[DONE] 31.4 Docs: spec "Project Configuration", SYNTAX_REFERENCE, CLAUDE.md, requirements

#### 46 `let` / `var`, `match` as a value, `write` (user, 2026-10-29) [DONE 2026-10-29]
	[DONE] 46.1 `let` (set once, may be later; never changes) and `var` (can change) - the type
		comes from the value; as parameters with a written type
	[DONE] 46.2 `match` gives a value: `match n { 6, 7 : "Weekend", _ : "Weekday" }`; no fall through
	[DONE] 46.3 `write(...)` - print without ending the line (console only, flushed)
	tests/test_let_var_match.py

#### 49 Decisions.md - every feature and decision in one place (user, 2026-10-31) [DONE 2026-10-31]
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
	[DONE] 49.7 The code: what the compiler does that no document records (src/)
		4 feature lines: and / or / not and `func` lambdas, the built-ins, the error tree, reserved inheritance words; D.081
		fusion-summary.md (GC default) and fusion-strict.md (Unique<T>) brought in line; `Unique` keyword: 48.8
	[DONE] 49.8 The user settles each CLASH row; the losing side is fixed in its document
		C.001-C.010 all settled 2026-10-31
		C.001-C.004 settled 2026-10-31 -> D.025-D.028; documents fixed
	[DONE] 49.9 A check in check.py: every feature line has a known area and status; IDs unique and in order
		`decisions` in check.py (tests/test_decisions_file.py): lines under their own area, numbered in
		order, decision rows in order naming a feature that exists, C rows marked CLASH

#### 32 Methods on structs, then classes and interfaces (user, 2026-10-11) [DONE 2026-11-01]
	[DONE] 32.0 Settings housekeeping (tests/test_settings_formats.py) - user, 2026-10-28: names in camelCase, read case-insensitively,
		`_` ignored (`tab_width` = `tabWidth`); `[numbers] overflowWrap` (default false) takes
		over arithmetic wrapping from `[safety] mode = "unsafe"`; `[safety] mode` = safe
		(default; `normal` accepted) / strict (every warning is an error) / unsafe
	[DONE] 32.1 Methods on the program's own structs (`[structs] functions = true`;
		tests/test_struct_methods.py) - (`p.move(1, 2)`) - built-in types have them (18.3.7);
		also 44.2
	[DONE] 32.2 Classes, the rest (plan: taskSummary2.md; truth tables: Classes.md - user, 2026-10-30)
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
	[DONE] 32.7 Inheritance (tests/test_inheritance.py, Classes.md section 8): one parent - `inherits` / `extends`
		fields, functions and interfaces inherited; override (required), sealed, abstract, protected
		a call through a parent runs the object's own function (the class table)
		super(...) runs the parent's constructor code; super.f() the parent's own code
		typeOf(x): Person.Employee.Manager; casts down checked while running; favour composition (D.083)
	[DONE] 32.5 Interfaces - also the built-in ones (Classes.md sections 5, 6): `ToString`
		[DONE] 32.5a Interfaces (tests/test_interfaces.py, Classes.md section 7): `interface`, `implements` (several)
			an interface building on several; as a type (variables, parameters, Lists); the object's own function runs
			`x is Circle`; casts written in front, a CastError when wrong; readonly followed through
			default methods behind `[interfaces] defaultMethods` (default false)
			Later: a cast between numbers `(int)d` (TYP.016)
		[DONE] 32.5b ToString, Default, Cloneable; copies of objects; nocopy / noshare
			[DONE] ToString (tests/test_object_text.py): print / format / "{x}" / toString(x) use it,
				also through an interface value; added to a program only when a class implements it
			[DONE] Copies of objects (tests/test_object_copies.py): `byVal` - a new object, each field byVal (D.088)
				Lists / Maps of objects and interface values too; Cloneable with its own clone()
				nocopy (set only in a constructor or clone()); noshare (handed out only as byVal)
			[DONE] Default (tests/test_default_interface.py): a local, field or static of the type is made
				when declared; `= null` makes a new one; a constructor without arguments (may be private)
		(how an object prints; without it the class name and a warning), `Default` (a
		constructor with no arguments, may be private - a variable of the type is never null,
		the object made when declared; `s = null` lets the old object go and makes a new
		default one (user, 2026-10-30); arrays / Lists / Maps implement it), `Cloneable`
		(`clone()` - copies of objects, byVal / toList on a List of objects, nocopy / noshare)
	[DONE] 32.14 List / Map options in the set-up block (tests/test_collection_options.py)
		noDuplicates(), noNull(), readOnly() (after the block) - a DuplicateError / NullError / ReadOnlyError
		a compile error where it can be seen, else while running (D.086); a refused value is freed
	[DONE] 32.4 `Collection<T>`, `Iterator<T>`, `foreach` (tests/test_foreach.py, Arrays.md section 6)
		`foreach (T x in c)` / `foreach x in c` over arrays, Lists, Maps and a Collection<T> class
		a collection gives a new Iterator<T> from iterator() per loop - nested loops work (D.089)
		the looped collection never changes inside a loop - a compile error (D.058); your own class
			only with `[collections] allowChangeWhileLooping` (default false)
	[DONE] 32.6 `List<T>` as an interface with a default implementation - never null
		[DONE] A List as a Collection<T> value (tests/test_list_collection.py): `Collection<int> c = xs`
			its class table answers every Collection function; c.iterator() an Iterator<T> object
		[POSTPONED to 45.10] An array as a Collection<T> value - arrays on the heap first; removing blocked
		[DONE] A Map as a Collection<Entry<K, V>> (tests/test_map_collection.py): Entry<K, V> (key, value)
			`keys()` / `values()` borrowed views (D.095); `.toList()` copies; typed foreach gives entries (D.096)
		[DONE] next() past the end (D.094): null for a string, List, Map, object or enum; a primitive:
			an IndexError "check hasNext() first"; a null string prints null, `s is null` works
		[POSTPONED to 33] Another implementation behind `List<T>` - needs generic classes of your own
	[DONE] 32.11 `[source] caseSensitive` (default true) (tests/test_case_sensitive.py)
		false: names that differ only in case are an error, each pair listed once
	[DONE] 32.12 Commas between struct fields (tests/test_structs.py): needed on one line, not on new lines (D.093)
	[DONE] 32.3 Example (was 16.2): examples/classes_demo.fusion - classes, interfaces, inheritance,
		casts, structs building on structs, a struct holding an object, enums with match, List options

#### Moved out of files/FEATURES.md 2026-11-13 (user): Task 34, and the finished / replaced / rejected
#### items of "Later / advanced"
#### 34 Example program coverage (was 16) [ ] - its two examples are now FEATURES "Later" L14.1 / L14.2
	[DONE - 32.1, `[structs] functions`] Methods on structs (`p.move(1, 2)`) - user-defined classes; methods on
		built-in types are done (18.3.7)
	[REPLACED by 47.2 - a long of minor units, never a decimal] money type (user, 2026-10-24 / 10-27): strict decimal for currency, default 0, written-out
		conversions, rounding half away from zero + a rounding-mode enum (files/Literals.md
		"Money", spec "Complete Type Specifications")
	[REJECTED 2026-10-31, D.058] Changing a List / Map while looping, allowed by a setting -
		the collection being looped over is never changed; build a new one
	[DONE - 32.2h] Namespaces: group related modules (several folders / libraries) under one name
	[DONE] Open: `int?` - decided with Task 30 (user, 2026-10-27): no `T?` types at all; `?` is
		used on a variable (`x?.method()`), and only class objects and enums can be null
		(files/Nullable_Values.md)
	[DONE] fusion.toml: `[build] waitAtExit` - default false (user, 2026-10-28: for development,
		examples and testing; examples/fusion.toml turns it on); --headless never waits
	[DONE] `[structs] holdCollections` (default true) - the struct setting decided 2026-10-24
	[REPLACED by 47.5 - `fixed(255) string name`] Per-field string sizes (`string(255) name`) to match database columns
	[DONE - 32; generics: Task 33, threading: Task 42] Classes, interfaces, inheritance (32), generics (33); enums: Task 25;
		threading: no task yet

#### 51 Documentation clean-up: folders and Markdown files (user, 2026-11-07) [DONE 2026-11-14]
	Markdown stays the format (no HTML pages for now); Decisions.md keeps its format
	Proposal: files/DocumentationSystemProposal.md (from the Mac) - plan: task/taskSummaryArchive.md Task 51
	[DONE] 51.1 Root files moved to files/ (debug scripts to debug/); the root keeps CLAUDE.md, README.md,
		Decisions.md, main.py, check.py, pytest.ini; paths in code and docs updated
	[DONE] 51.2 Decisions.md: a short "Why" column for all 112 decisions (none invented - blanks listed for
		the user); a PROPOSED status (only the user makes it ACTIVE); no superseded rows
	[DONE] 51.3 OpenQuestions.md next to Decisions.md - one line per open question
	[DONE] 51.4 Main.md in the root - what Fusion is for + the map of every file (from CLAUDE.md)
	[DONE] 51.5 Split the spec into files/spec/NNN-Topic.md (then files/FutureFeatures.md) - file list shown first;
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
		[DONE] 1 Gather (2026-11-10): the inventory in task/taskSummaryArchive.md (51.5a) - 7 clashes / gaps found;
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
	[DONE] 51.5b Split files/FutureFeatures.md into files/future/ (index.md + NNN-Topic.md, 31 files) - plan in
		task/taskSummaryArchive.md, approved 2026-11-13 (6 files per step - user)
		[DONE] 010-IDEModule, 011-IDEProjects, 012-IDEOverlays, 013-IDEOverlays2, 014-IDEOverlaySettings,
			015-WebServers (2026-11-13)
		[DONE] 000-Overview, 020-Settings, 030-LibraryLayout, 031-Regex, 032-DomainPackages, 033-Currency (2026-11-13)
		[DONE] 034-DataFormats, 035-HIDL, 040-CrossLanguage, 050-Imports, 060-Comments, 061-CommentHighlighting (2026-11-13)
		[DONE] 062-CommentLevels, 070-NamingRules, 071-NamingExceptions, 080-Arrays, 081-Strings, 090-Unsafe (2026-11-13)
		[DONE] 100-CLI, 101-CLICommands, 110-SymbolIDs, 111-Identity, 120-Threads, 130-FarFuture (2026-11-13) -
			FutureFeatures.md is now a table of where each section went
	[DONE] 51.6 A link check in check.py (2026-11-14): tools/doc_links.py, the `links` check (also in --docs),
		tests/test_doc_links.py - every relative link in the .md documents leads to a file and a heading
	[DONE] 51.8 FEATURES.md reorganised (user, 2026-11-13): a Preface (the rules, the counts, what is done,
		the old task numbers), an Index of every task in working order, then the phases

#### 59 Faster checks: run only the tests the change needs (user, 2026-11-13) [DONE 2026-11-14]
	The full suite took ~4 minutes (2,710 tests; the end-to-end ones compile with GCC under the leak check)
	[DONE] 59.1 Documents only changed: `--ship` runs only the document checks; `--full` forces every check;
		`check.py --docs` (CLAUDE.md Rule 7)
	[DONE] 59.2 What takes long (2026-11-14): 522 end-to-end tests at 0.3-0.5 s each = 208 of 238 s (GCC once
		per test); no single slow test; 12 cores, the suite used one
	[DONE] 59.4 (its parallel part) The tests on every core (2026-11-14): pytest-xdist, `-n auto --dist loadfile`
		in check.py (one after another when xdist is missing) - 238 s -> 50 s, the same 2,714 passed / 8 skipped
	59.3 and the rest of 59.4: not needed now - FEATURES Later L2.4 / L2.5

#### 48 Ownership: move, borrow, share (user, 2026-10-31) [DONE 2026-11-14]
	After all of Task 32 (user)
	Design and truth tables: files/Ownership.md
	Decisions D1-D49: Notes/Ownership_Decisions_2026-10-31.md
	Settings: [memory] assignment = "move" (default) | "share"
	[DONE] 48.0 The rules (from Rust's borrow checker) - written (files/Ownership.md) and built by 48.1-48.3
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
	[DONE] 48.7 Examples and files/SYNTAX_REFERENCE.md, tests with and without null checks (Rule 4b) -
		syntax_one_writer (R4 relaxed, storing this, null with and without a check); tests/test_ownership_this.py
	[DONE] 48.8 Release the `Unique` keyword - no `Unique<T>` or `.move()` (D.080) - an ordinary name now;
		the self-hosted lexer too; `Shared` / `Weak` stay reserved (Task 38)
	[DONE] 48.9 Migrate, then make "move" the default (D.102)
	[DONE] 48.10 R4 changed (D.123): while a borrow changes a value its owner may still be read - only changing it
		another way is an error (today reading is an error too - 48.2)
	[DONE] 48.11 `[memory] ownership = "strict" | "relaxed"` (D.124, user 2026-11-14): every ownership rule at once,
		replaces `assignment` (old values read with a warning); files/fusionSettings.xml; the before / after table
		in files/Ownership.md 1 and spec 090
	[DONE] 48.12 Storing `this` shares the object, counted (D.103): `cars.add(this)` - one car in several
		collections; freed when the last holder lets go - it already worked; tests/test_ownership_this.py keeps it
		so (leak check, with and without a null check)
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
	48.4 -> 50.5, 48.6 -> 38.5, 48.5 -> FEATURES Later L4.4 (2026-11-14)

#### 50 readonly results and a deep const (user, 2026-11-03) [DONE 2026-11-14]
	Rules shown: files/showcase/Ownership.fusion; the skill .claude/skills/fusion-ownership
	[DONE] 50.1 A readonly result, part of the signature (D.110): `public readonly Engine function getEngine()`
		The caller gets a read-only borrow: `e.kind = ...`, passing e to a function that changes it - errors
		No `readonly` in that function's body - `return readonly this.engine` is an error (the signature says it)
		`Engine e = byRef car.getEngine()`: an error - byRef asks to change what is readonly
		`byVal car.getEngine()`: a copy the caller may change
		Open (user): what such a function may return - a member of the class, a new object - decided while building
	[DONE] 50.2 `const` on an object is deep (D.112): `const Car c` - no field set, no method that changes it;
		a `byVal` copy (or a function returning one) may change (today only Lists, Maps and structs are deep)
	[DONE] 50.3 Tests - every allowed / not allowed case of D.110-D.113 (Rule 4c); Ownership.fusion tags [built]
	[DONE] 50.4 `readonly` on a copy is a warning, not an error (D.113): a number result, and `f(readonly n)` on an
		int / string (an error since 48.3)
	[DONE] 50.5 `--interface` shows the readonly result of each public and internal function - never private
		(D.115) - was 48.4

#### 52 Classes, value types and null - follow-ups from the open questions (user, 2026-11-07) [DONE 2026-11-14]
	From the "why" of D.008, D.009, D.010, D.055 - some to build, some to recheck first
	[DONE - it held in every case; 4 more tests] 52.2 Recheck `implements Default` (CLS.014, D.010): a variable of the type is never null in every
		case (fields, statics, Lists, after a move); the developer writes the default values - tests per case
	[DONE - designed in files/Classes.md 5b; built later, with Task 33] 52.4 A `Length` interface (TYP.017): strings and arrays (value types) carry `length()` as if they
		were objects - made internal to the type by Fusion, so `s.length()` works on null and "" alike;
		later more built-in methods the same way - design first
	[DONE - nothing to build, D.138 (2026-11-14)] 52.5 Build D.055 (decided 2026-11-07): `length()` never null - 0 empty, -1 null (string, array, List,
		Map with `nullable` on); the -1 only in a comparison (`if` / `while`), elsewhere a NullError (a compile
		error where it can be seen); tests with and without a null check (Rule 4b)
	[DONE] 52.6 An interface's functions are public or internal - `private` on one a compile error (D.114, CLS.019)
	[DONE] 52.8 The null guard (was 30.2 - postponed to 32 and never built, found 2026-11-14): `c?.name`,
		`c?.rename("x")` not run on null, false in an `if`; `c ?? Car()` - files/Nullable_Values.md; NUL.003
	[REJECTED 2026-11-14 - D.138] 52.9 The nullable settings (was 30.3): a string, array, List or Map is never null,
		whatever the settings
	[DONE] 52.10 A List or Map never holds null (D.139): `add(null)`, `m[k] = null`, `[car1, null]` as a List - errors;
		a null variable added at run time - a NullError; `[car1, car2]` adds each item
	[DONE] 52.11 Arrays of objects (D.140): a null slot allowed (in a literal too - today refused); `arr[i] = null`
		frees the object; an element of the wrong type stays an error
	[DONE - default false] 52.12 `[strings] nullBecomesEmpty` (user, 2026-11-14): `s = null` - an error, or ""; default asked (D.003)
	[DONE] 52.13 `?.` / `??` on a string, array, List or Map - never null, so the guard does nothing: a warning
	[DONE - a Default is never null by construction (52.2)] 52.7 Null checks at compile time (D.116, D.117): a `?.` comparison warns; `!` around one an error (a
		`[conditions]` setting allows it, then a warning); an object surely null when passed - an error; a
		`?` parameter without a null check - a warning; a `Default` left null - an error
	52.1 -> FEATURES Later L5.8, 52.3 -> Later L10.4 (2026-11-14)
