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
