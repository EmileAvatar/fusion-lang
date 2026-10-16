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

#### 26 Error handling: Go-style error returns + try/catch, both on by default, switchable in config [ ]
	[DONE] 26.1 Detailed plan - approved 2026-10-16 (errors bubble up, capture optional on any call,
		every built-in failure catchable, one catch-all)
	[DONE] 26.2 `Error` and error returns: `T, Error function`, `return Error(...)`, capture on any
		call, `if err`, bubbling (explicit, leak-free), stop at main
	[ ] 26.3 try / catch / finally / throw
	[ ] 26.4 Every built-in failure catchable (files, conversions, index out of range, ...)
	[ ] 26.5 Config: [errors] returns / exceptions
	[ ] 26.6 Example + docs
	[POSTPONED to 26] Error handling (try/catch) example (was 16.5)

#### 27 Semantic contract and safety (from the ChatGPT review, 2026-10-11; notes.md step 2) [ ]
	[ ] 27.1 Bounds checks for fixed arrays: `a[5]` on an `int[3]` crashes today (segmentation
		fault, found 2026-10-11) or, worse, silently overwrites other memory. Every out-of-range
		index must be a clear run-time error, never missed (user: "so we don't miss out-of-range
		errors any more") - reading and writing, array parameters, arrays in structs, arrays of
		structs. Lists, strings and bytes are checked already
	[ ] 27.2 The contract, written in the spec in one place: copying (deep - every copy is
		independent, nested lists too), the equality table (which types `==` / `===` compare),
		`=` in conditions with its ambiguous cases tested, Unicode indexing (code points, not
		what a reader sees as one symbol), integer conversions and overflow, changing a
		collection while looping over it, cleanup on every path (early return, break, exit)
	[ ] 27.3 Interaction tests: features together - a struct holding lists, copied, passed
		through functions and across modules; nested collections; early returns
	[ ] 27.4 Block-style equivalence: the same app written 3 times - indentation, braces,
		`End` keywords - 3 .fusion files that must compile to identical C (user request);
		kept as examples and checked by check.py
	[ ] 27.5 Doc fix: the equality heading in SYNTAX_REFERENCE.md names `!==` too

#### 28 Self-hosting phase 1 - the test run (was 10) [ ]
	[DONE] 28.0 Prerequisites: analysis (was 10.1) and language features (was 10.2, by Task 18)
	[ ] 28.1 The subset: exactly what the programs in examples/ need
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
	[POSTPONED - after MVP] Paged / memory-mapped strings: load only the part of a huge string in use
	[POSTPONED - after MVP] Per-field string sizes (`string(255) name`) to match database columns
	[POSTPONED - needs references] Identity operator (same object in memory)
	[POSTPONED - after MVP] Multi-dimensional arrays (growable lists: done, 18.5.1)
	[POSTPONED to 27.1] Bounds checks for fixed arrays (strings, lists and bytes are checked)
	[POSTPONED to 32 / 33] Classes, interfaces, inheritance (32), generics (33); enums: Task 25;
		threading: no task yet

## Known limitations (by design for now)
	[ ] A string-holding variable can't reuse the name of one in an enclosing block (clear error)
	[ ] Single-quote comments disabled (clash with char literals) - 8 skipped tests
	[ ] Identifiers ASCII-only unless fusion.toml opts in (text and chars are Unicode since 18.3.2b)
