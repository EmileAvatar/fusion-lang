# Fusion - Feature and Task Status

The single place to see what is done, open, or postponed. One line per item.

- `[ ]` open · `[DONE]` finished · `[POSTPONED to X]` waits for X (a task, or a missing feature)
- `##` = major sections only. Tasks: `#### NN Title [status]`. Sub-tasks: one tab +
  `[status] NN.N`. Parts: two tabs
- Find things: `grep -n "\[ \]" FEATURES.md` (open), `grep -n "POSTPONED" FEATURES.md`,
  `grep -rn "18\.3\.2" FEATURES.md taskSummary2.md task/` (one item everywhere)
- Detail: active task -> `taskSummary2.md`; finished -> `task/taskSummaryArchive.md`;
  not started -> `task/taskBacklog.md`. What the language can do today, with examples ->
  `SYNTAX_REFERENCE.md`

---

## Tasks

#### 01-04 MVP compiler: lexer, parser, semantic analysis, C codegen [DONE]

#### 05 Cleanup & organization [DONE]
#### 06 Verification & bug fixes (incl. FizzBuzz) [DONE]
#### 07 Git & GitHub [DONE]
#### 08 const keyword [DONE]
#### 09 Fixed-size arrays v1 [DONE]

#### 10 Self-hosting - compiler rewritten in Fusion [ ]
	[DONE] 10.1 Prerequisites analysis & planning
	[POSTPONED to 18.5] 10.2 Missing language features (file I/O, collections, string helpers, CLI args)
	[ ] 10.3-10.12 Port lexer, parser, semantic, codegen, main; bootstrap twice; verify; optimize; docs

#### 11 LLVM backend [ ]
	[DONE] 11.1 Research & design
	[POSTPONED to 15.4] 11.2-11.13 Environment, IR generator, types, functions, codegen, strings, stdlib, optimization, tests, docs (order vs Task 10 undecided)

#### 12 Compiler architecture hardening (typed AST, codegen split, block scoping, memory-model ADR, config) [DONE]

#### 13 HIDL - hardware interface definition language [ ]
	[ ] 13.1 Grammar & format decision
	[ ] 13.2 Scope v1 vs. future layers
	[ ] 13.3 Memory model reconciliation
	[ ] 13.4 HIDL parser
	[ ] 13.5 Fusion code generation from HIDL
	[ ] 13.6 Compile-time hardware safety checks
	[ ] 13.7 Multi-language code generation (stretch)
	[ ] 13.8 Simulator & tooling (stretch)
	[ ] 13.9 Docs & examples

#### 14 Nullable arrays & safe navigation (`?.`, `?[`, `.length`) [ ]
	[ ] 14.1 Nullability model decision
	[ ] 14.2 Compile-time null-flow analysis
	[ ] 14.3 `.` / `?.` / `?[` parser support (the `.` part exists since 18.2.1)
	[ ] 14.4 Runtime null-check codegen
	[ ] 14.5 Beyond arrays (stretch)
	[ ] 14.6 Docs & examples

#### 15 Deferred decisions & known gaps (each item has its own trigger) [ ]
	[ ] 15.1 IR layer decision (trigger: Task 11 starts)
	[ ] 15.2 Stdlib runtime lowering decision (trigger: first real import module)
	[DONE] 15.3 LambdaExpr scope bug (18.1.3)
	[ ] 15.4 Task 10 vs 11 ordering (trigger: before either starts)
	[ ] 15.5 Memory model implementation (Unique/Shared/Weak, GC) not tracked yet - needs scoping
	[ ] 15.6 fusion.toml [safety]/[backend] not enforced (trigger: strict mode or 2nd backend)
	[DONE] 15.7 Lexer warnings surfaced (19.6.4)
	[ ] 15.8 Name collisions in C: `fusion_` prefix, and functions named like C library ones (`rename`, `free`, `exit`, `abs`) - fix before 18.4
	[DONE] 15.9 Printing an array crashed the compiler (18.2.1)
	[DONE] 15.10 Interpolated strings only worked inside print - real values since 18.3.3
	[DONE] 15.11 `{@N}` positional placeholders (18.2.2b)
	[ ] 15.12 Operator operands evaluated in C's order (`next(c) - next(c)`); call arguments are left-to-right already

#### 16 Example program coverage [ ]
	[ ] 16.1 Control flow / loops example (buildable now)
	[POSTPONED - needs classes, no task yet] 16.2 Classes, interfaces & enums example (structs: done in structs_demo)
	[POSTPONED - needs generics, no task yet] 16.3 Generics example
	[POSTPONED - needs threading, no task yet] 16.4 Multithreading / async example
	[POSTPONED to 21] 16.5 Error handling (try/catch) example
	[POSTPONED to 15.5] 16.6 Memory model (Unique/Shared/Weak) example
	[POSTPONED to 18.4] 16.7 Modules / import example

#### 17 Mutable vs. fixed strings, templated strings, string pooling [ ]
	[ ] 17.1 Mutable string literal syntax (in-place editing, `s[0] = 'X'`)
	[ ] 17.2 Fixed (immutable) string type
	[ ] 17.3 Templated fixed strings
	[ ] 17.4 String pooling as a project setting (`[structs] string_storage = "pooled"` waits for this)
	[POSTPONED - needs fusionlib.Crypto] 17.5 Secure string storage, constant-time comparison

#### 18 Core language foundation ("a simple working language first") [ ]
	[DONE] 18.1 Functions with full parameter types
		[DONE] 18.1.1 Default parameter values
		[DONE] 18.1.2 Arrays as function parameters (by reference)
		[DONE] 18.1.3 Lambdas v1 and function types (no closures)
	[DONE] 18.2 Structs (fields only, value types)
		[DONE] 18.2.1 Core structs + [structs] settings
		[DONE] 18.2.2 Named arguments (calls and constructors)
		[DONE] 18.2.2b `{@N}` placeholders, left-to-right argument order
		[DONE] 18.2.3 Nested structs, array fields, arrays of structs, depth limits
		[DONE] 18.2.4 Arrays as function return values
	[ ] 18.3 Proper strings
		[DONE] 18.3.1 String values and automatic cleanup, compare by content, leak check
		[DONE] 18.3.2 String operations: `+`, `len`, `s[i]`, substring/contains/indexOf/..., conversions
		[DONE] 18.3.2b Unicode by default: `[strings] encoding = "utf-8"` (ascii | utf-8 | utf-16 | utf-32);
			len counts characters, lenb counts bytes; s[i]/substring by character; char holds any
			Unicode character; fast path for ASCII text; isAscii, asciiOnly, charCode, fromCharCode, byteAt
		[DONE] 18.3.3 Interpolated strings as values anywhere, `format(...)`
		[DONE] 18.3.4 Struct string fields growable, string_max_length at run time
		[DONE] 18.3.4b No string length limit by default; `[strings] max_length` (a number) for
			memory-constrained devices - exceeding it is always an error, never a cut; replaces
			[structs] string_max_length
		[DONE] 18.3.5 Equality operator family (`=` in conditions, `==`, `===`, `!==`, struct/array equality)
		[DONE] 18.3.5b A bool prints as `true` / `false` (print, `{...}`, `format`); still 1 / 0 as a value
		[ ] 18.3.6 Versatile string functions
			[DONE] 18.3.6a Optional arguments for built-ins; a program's own function/struct may reuse a
				library built-in's name
			[DONE] Inspect: isEmpty, isBlank, isDigits, isLetters (ASCII + Latin-1), countOf
			[DONE] Search: lastIndexOf, indexOf(s, part, from), containsAny
			[DONE] Extract: left, right (clamp; negative count = run-time error)
			[DONE] 18.3.6b Change: replace, replaceFirst, insert, remove, repeat, reverse, trimStart,
				trimEnd, capitalize, toTitle; toUpper / toLower now cover Latin-1 too
			[DONE] 18.3.6c Padding & alignment: padLeft, padRight, center (optional fill char),
				truncate (the first n characters only - adds nothing, user decision 2026-10-10)
			[ ] Masking: email, phone, number and custom string-number formats - planning overview only;
				design in detail when this item starts
			[DONE] 18.3.6d-1 Number bases: toHex / toBinary / toOctal / toBase (from an int or numeric
				text, optional width; negatives in two's complement, C# style), fromHex / fromBinary /
				fromOctal / parseInt(s, base), isInt(s, base), bytesToHex / hexToBytes; literals 0xFF,
				0b1010, 0o17 and 1_000_000
			[ ] 18.3.6d-2 Number formatting: formatNumber(1234.5, "#,##0.00") or printf style "%.2f"
			[ ] Compare: equalsIgnoreCase, compareIgnoreCase, natural order ("file2" before "file10")
		[DONE] 18.3.8 Raw bytes: `byte` (unsigned 0-255) and `bytes` (growable, edited in place);
			strings, chars and ints to bytes and back (toBytes, toString, getInt / setInt, 16-bit
			versions; little-endian, bigEndian option), hexToRaw / rawToHex, slice, indexOf; prints
			as plain hex - for raw hex work and self-hosting; file read / write stays in 18.5
		[ ] 18.3.7 The String class and method syntax - every string function reachable three ways:
			`String.replace(s, old, new)` (static class, always available), `name.toUpper()` (a string
			variable), `"Claude".toUpper()` (a string literal)
	[ ] 18.4 `import` and multi-file projects
	[ ] 18.5 Minimal standard library (IO, collections, CLI args), layered core/alloc/std
		[ ] 18.5.x String split & join: split(s, ","), join(list, ", "), lines(s), words(s) (need lists)

#### 19 Library trust, isolation & security [ ]
	[POSTPONED to 18.4] 19.1 Compiler-verified capability signatures
	[POSTPONED to 18.4] 19.2 Project restrictions (pragma Restrictions-style)
	[POSTPONED to 18.4] 19.3 Closed, compiled, licensed libraries
	[POSTPONED to 18.4] 19.4 Sandboxing and resource budgets
	[POSTPONED to 18.4] 19.5 Supply-chain security
	[DONE] 19.6 Source-level attack defenses (Trojan Source, homoglyphs, ASCII identifiers)
	[POSTPONED - needs fusionlib.AI] 19.7 AI module input guard

#### 20 Config file in any format: fusion.toml / .yaml / .json / .ini [ ]
	[ ] 20.1 One loader per format, one shared schema
	[ ] 20.2 Discovery and ambiguity (two config files = error)
	[ ] 20.3 Tests
	[ ] 20.4 Docs

#### 21 Error handling: Go-style error returns + try/catch, both on by default, switchable in config [ ]
	[POSTPONED to 18.3] 21.1 Detailed plan (needs working strings for error messages)

#### 23 Examples folder as a showcase [DONE]
	[DONE] 23.1 One example per SYNTAX_REFERENCE.md section, written and built by `check.py --build-examples`
	[DONE] 23.2 `examples/#list.csv` (fusion, c, exe, task, date added) - local only, not in git
	[DONE] 23.3 `examples/#run.bat` runs every .exe with `---- name.exe ----` separators, then pauses - local only
	[DONE] 23.4 `examples/CLAUDE.md` - the folder's rules
	[DONE] 23.5 Main CLAUDE.md Rule 4 points to it
	[DONE] 23.6 Removed the stray `examples/New folder` (user); `fusion.yaml` -> `files/fusion-overview.yaml`

#### 22 Project tracking restructure (FEATURES.md, SYNTAX_REFERENCE.md, slim CLAUDE.md, check.py) [ ]
	[DONE] 22.1 FEATURES.md
	[DONE] 22.2 SYNTAX_REFERENCE.md
	[DONE] 22.3 Slim CLAUDE.md
	[DONE] 22.4 Working file / archive / backlog split
	[DONE] 22.5 Verify nothing lost
	[DONE] 22.6 check.py - one command for tests, examples, leak check, ASCII, status
	[ ] 22.7 Reliable markers for files that lack them (see task/automation.md): status lines
		under each feature heading in the language spec, matching FEATURES.md; README reduced to
		goals + pointers to FEATURES.md / SYNTAX_REFERENCE.md; task links in FutureFeatures.md
		only when an item becomes a task

---

## Later / advanced (after MVP)

Kept in Fusion's design, deliberately postponed - the simple version comes first.
	[POSTPONED to 17.4] String pool (shared storage for identical text) - when pooling is on,
		strings are pooled and mutable strings use a StringBuilder internally (user note 2026-10-09)
	[POSTPONED to 17] StringBuilder for fast repeated appends (internal for mutable strings)
	[POSTPONED to 15.5] Garbage collection as a project-selectable memory strategy
	[POSTPONED to 15.5] Unique<T> / Shared<T> / Weak<T> (decided in 12.7, not built)
	[POSTPONED to 17] Copy-on-write string sharing, in-place string editing
	[POSTPONED to 18.3.7] Method-call syntax on strings (`name.toUpper()`); on structs - after MVP
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
	[POSTPONED - after MVP] Paged / memory-mapped strings: load only the part of a huge string in use
	[POSTPONED - after MVP] Per-field string sizes (`string(255) name`) to match database columns
	[POSTPONED - needs references] Identity operator (same object in memory)
	[POSTPONED to 18.5] Growable arrays / lists; multi-dimensional arrays
	[POSTPONED - after MVP] Array bounds checking (strings are checked from 18.3.2)
	[POSTPONED - needs classes] Classes, interfaces, inheritance, enums, generics, threading

## Known limitations (by design for now)
	[ ] A string-holding variable can't reuse the name of one in an enclosing block (clear error)
	[ ] Single-quote comments disabled (clash with char literals) - 8 skipped tests
	[ ] Identifiers ASCII-only unless fusion.toml opts in (text and chars are Unicode since 18.3.2b)
