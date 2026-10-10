# Fusion - Working File (active task plans)

**What this file is (Task 22, 2026-10-09):** only the task being worked on now - its detailed
plan, the next action, and the latest session note. Keep it small: it is read often.
- Status of every task and feature: `FEATURES.md` (`[ ]` open, `[DONE]`, `[POSTPONED to ...]`)
- Finished tasks and sub-tasks, old sessions: `task/taskSummaryArchive.md` (verbatim)
- Not-started task write-ups: `task/taskBacklog.md` (verbatim)
- Rules (plan first, no emojis in code, ...): `CLAUDE.md`

---

## TASK 18: Core Language Foundation ("a simple working language first")

**Goal:** Build the small set of core features every other planned feature depends on, so
Fusion can write real (non-toy) programs before any of the larger future features begin.
**Status:** In Progress - 18.1, 18.2, 18.3.1 complete (detail archived) (user agreed with the direction,
2026-10-07: "the first goal is to get a simple working language first"). Each sub-task still
needs its own detailed plan approved before implementation, per Rule 1.
**Priority:** HIGH - nearly every open task is blocked on something in this list (see "Why
this task exists")
**Blocked By:** Nothing
**Estimated Effort:** TBD - each sub-task gets its own plan; 18.4 (import) is the largest
**Source:** Claude review of the project (2026-10-07) - see `FutureFeaturesCaution.md` for
the full reasoning. Overlaps heavily with Task 10.2 (self-hosting prerequisites: file I/O,
collections, string helpers, CLI args) - this task effectively becomes that prerequisite
work, done for its own sake rather than only in service of self-hosting.

### Why this task exists

The documented vision (FutureFeatures.md) is far larger than the implemented core, and the
same few missing core features block almost everything else: the Currency Module, Crypto,
Regex, HIDL, the whole stdlib, the Symbol-ID system, most of Task 16's examples, and
self-hosting all need `import`; Currency's runtime representation, HIDL register maps, and
classes all need structs; self-hosting needs strings, file I/O, and collections. Building
this foundation unblocks roughly 80% of the open task list in one stretch.

### Sub-tasks (each needs its own approved plan before implementation)

Ordered by dependency - each builds on the ones before it.

#### 18.3: Proper Strings
**Why third:** today strings are only C string literals passed around as `char*` - there is
no concatenation, length, comparison, substring, or number conversion anywhere in codegen.
Nearly every real program needs these, and a self-hosted lexer is built entirely on them.
- [x] **Latent bug - string `==` compiles to C pointer comparison** (verified 2026-10-07) -
      FIXED in 18.3.1 (`fusion_str_eq`):
      `x == y` on two strings emits `(x == y)` in C, comparing addresses, not contents. It
      returns the right answer today only by accident - GCC deduplicates identical string
      literals - and will silently return false for equal strings as soon as any string is
      built at runtime. Same bug class as Task 12.6 (semantic analysis accepts something
      whose generated C is wrong). Fix early, before runtime-created strings exist
- [x] **Bug - `%` in a printed string is treated as a printf format code** - FIXED
      (2026-10-07, user-approved small fix): `print("Progress: 100% done")` printed
      `Progress: 100 1134633984one`, because string text was placed directly into `printf`'s
      format string, so `% d` read garbage from the stack (CWE-134 - `%n` could even write to
      memory). Now `escape_printf_text` in `c_runtime.py` doubles `%` in literal text on both
      the plain-print and interpolation paths, leaving codegen's own specifiers untouched.
      4 tests in `tests/test_source_security.py` (incl. end-to-end with `%d %s %n` in text)
- [ ] Concatenation, length, comparison (`==`/`!=`/ordering by content), indexing/substring,
      conversion to/from numbers
- [ ] **Equality operator family** (user request and decisions, 2026-10-07) - for strings
      first, then every other type (numbers, arrays, structs, later classes/references).
      **Decided:**
      - `=` is **assignment** as a statement (`xx = 2`), and **comparison inside an `if`
        condition** (`if xx = 2` or `if (xx = 2)`) - the compiler treats it as a compare
        there, never an assignment. Side benefit: C's classic `if (x = 5)` bug becomes
        impossible, because assignment can't happen inside a condition at all
      - `==` is **value comparison everywhere**: `xx == 2` is true if `xx` holds the number
        2, and `xx == "2"` is also true, because the value is the same
      - `===` is **strict comparison** - same type *and* same value: `xx === "2"` is false
        when `xx` is a number and `"2"` is text
      **Still open (decide when 18.3 is planned):**
      - Does `if xx = 2` compare like `==` (value) or `===` (strict)? Value seems most
        natural (VB-style readability) - confirm
      - Negation pairing: with `=` now a comparison, the original list reads as three
        pairs - `=`<->`!=`, `==`<->`!==`, `===`<->`!===` - confirm
      - Does the `=`-compares rule also apply in `else if` / `while` conditions? Consistency
        suggests yes
      - **Caution - define a small, explicit cross-type table for `==`:** JavaScript's loose
        `==` is a notorious bug source because its coercion rules are huge and surprising
        (`0 == ""` and `"0" == false` are both true). Recommend Fusion's `==` coerce only a
        few well-defined pairs (number <-> numeric text, char <-> one-character string) and
        never coerce "truthiness" (no bool <-> number/string)
      - Note: `'2'` (single quotes) is a **char** literal in Fusion, `"2"` is a string - the
        cross-type table must say whether char, string, and number all participate
      - An **identity** operator (the very same object in memory) has no symbol yet - needed
        once references and `Shared<T>` exist
      - Every operator must be defined per type and never fall through to C's raw `==` -
        that fall-through is exactly the pointer-comparison bug above
      - Security note: comparing secrets (passwords, tokens) needs constant-time comparison
        to avoid timing attacks - a Crypto concern (Task 17.5), but the operator design
        shouldn't rule it out
- [ ] Decide string memory ownership - concatenation creates new strings, so who frees
      them? This is the first place the memory model (Task 12.7) becomes practical, and
      it's the foundation Task 17 (mutable/fixed strings, pooling) builds on
- [ ] **Struct string fields become growable heap buffers** (from 18.2, user decision
      2026-10-08): owned by the struct, copied in full on struct copy, freed with the struct,
      `[structs] string_max_length` cut-off checked at runtime, `string_warn_length` stays a
      compile-time guideline
- [ ] Example program per Rule 4 / Task 16

### 18.3 Detailed Plan (APPROVED 2026-10-09 - all five parts)

**Today:** a `string` is a C `char*` pointing at text written in the source. Nothing can build,
change or free a string while the program runs; `==` compares addresses (the latent bug
above); interpolated strings only work inside `print` (Task 15.10); struct string fields are
fixed text (user accepted for 18.2, "eventually we will work on the strings").

**The core decision - who frees a string?** Building strings at run time means memory that
must be released. Recommended (decision 1 below): **strings are values, like structs** -
each string variable, field and array element owns its own text, copying makes an
independent copy, and the compiler frees it automatically when its owner goes away. No
garbage collector and no reference counts: the "stack / value types" row of
`FutureFeaturesCaution.md`'s strategy guide, and a core that works without GC (the D lesson).
Same model as C++ `std::string` and Rust `String`.

Split into five parts, each shippable and committed on its own (same pattern as 18.1/18.2).
Each adds tests, an example program (Rule 4), and spec/EBNF/CLAUDE.md updates.

**18.3.2 - String operations** - COMPLETE, detail archived (`task/taskSummaryArchive.md`)

**18.3.2b - Unicode by default** - COMPLETE, detail archived

**18.3.3 - Interpolated strings as values** - COMPLETE, detail archived

**18.3.4 - Struct string fields become growable** - COMPLETE, detail archived

**18.3.4b - One length limit for every string** - COMPLETE, detail archived

**18.3.5 - The equality operator family** - COMPLETE, detail archived

**18.3.6 - Versatile string functions** - COMPLETE, detail archived

**18.3.8 - Raw bytes** - COMPLETE, detail archived

**18.3.7 - Type classes and method syntax** - COMPLETE, detail archived

**Out of scope (logged for later):** in-place editing (`s[0] = 'X'`) and mutable vs fixed
strings (Task 17 - 18.3 strings are replaced, never edited in place, which keeps the
ownership rules simple); string pooling (Task 17); Unicode-aware functions; full expressions
inside `{...}` (`{a + b}`); an identity operator (needs references, `Shared<T>`); constant-time
comparison for secrets (Task 17.5); bounds checking for arrays (its own item).

**Decisions (user, 2026-10-09 - all four chose the recommended option):** 1. strings are
values with automatic cleanup; 2. invalid conversions stop with a clear run-time error (plus
`isInt`/`isFloat`); 3. `len`/`s[i]` count bytes for now; 4. the 18.3.5 equality
recommendations are accepted as written. The options that were offered:
1. **Who frees strings:** values with automatic cleanup (recommended) / reference-counted
   shared strings / never free during the run (simplest, but memory only grows - unusable
   for long-running programs)
2. **Invalid conversions** (`toInt("12x")`): stop with a clear run-time error, with
   `isInt`/`isFloat` to check first (recommended) / quietly return 0 / a fallback argument
   (`toInt(s, 0)`)
3. **What `len(s)` and `s[i]` count:** bytes for now (recommended - simple and fast; correct
   for ASCII, Unicode-aware functions later) / Unicode characters now (slower `s[i]`, more
   work in 18.3.2)
4. **Equality (18.3.5):** accept the recommendations above / decide them when 18.3.5 starts

**Success criteria:** strings can be built, joined, sliced, converted and compared by
content; `string s = "x is {x}"` works anywhere; a struct holds a 10,000-character string
built at run time; every string test runs leak-free under the counting allocator (nothing
freed twice, nothing left over); generated C compiles cleanly with `gcc -Wall -Wextra`; full
suite green; 11/11 examples.

#### 18.4: `import` and Multi-File Projects
**Why fourth:** the single biggest unblocker - everything in the stdlib, every proposed
module, and every program larger than a few hundred lines needs it. Placed after 18.1-18.3
because there needs to be something worth importing (functions, structs, string utilities).
- [ ] `import` parsing (lexer keyword only today) and module resolution (how a module name
      maps to a file path)
- [ ] Visibility (`public`/`private` - already reserved keywords) across module boundaries
- [ ] Multi-file compilation: generate one C file per module plus headers, or one combined
      C file - a real decision, with implications for build speed and the future Symbol-ID
      system
- [ ] Record each module's interface signature (exported symbols, plus what capabilities
      it uses) - the groundwork for the ecosystem-fragmentation answer in
      `FutureFeaturesCaution.md`. Cheap to capture now, very expensive to retrofit later
- [ ] Example: a small multi-file project

#### 18.5: Minimal Standard Library (IO and Collections)
**Why last:** needs everything above - it's the first real importable module (18.4), built
from functions (18.1), structs (18.2), and strings (18.3).
- [ ] Console input, and file read/write
- [ ] A growable list (and probably a map/dictionary)
- [ ] Command-line arguments
- [ ] **Layer the stdlib from day one** (core / alloc / std, Rust-style): the core layer
      works with no heap, no GC, no exceptions; higher layers add allocation and OS
      services. This is the specific thing D got wrong - its standard library was built
      assuming a garbage collector, so making GC optional later split the ecosystem. See
      `FutureFeaturesCaution.md`
- [ ] Satisfies Task 10.2's self-hosting prerequisites (file I/O, collections, string
      helpers, CLI args)
- [ ] Example programs per Rule 4 / Task 16

**Success Criteria:**
- A non-trivial multi-file Fusion program (e.g. a word counter that reads a file, builds a
  list/map of words, and prints sorted counts) compiles and runs correctly
- Default parameters and string equality both behave correctly (the two verified gaps)
- Full test suite stays green; every sub-task ships with tests and an example program

**Deliverables:**
- Functions with full parameter support, structs, a real string type, `import`/multi-file
  compilation, and a minimal layered stdlib (IO + collections)
- One example program per sub-task

---

## Working Notes

### Session 29 (2026-10-08 - New PC Setup, Task 18.2 Plan, 18.2.1 Core Structs)

- **New machine (via Dropbox):** Python 3.13.1 present; installed requirements.txt and GCC
  16.2.0 (WinLibs MinGW-w64 UCRT, via winget). Baseline confirmed: 1234 passed, 8 skipped;
  9/9 examples. Note: on this Dropbox copy git can't append to `.git/logs/HEAD` ("Invalid
  argument" - git suggests `git config windows.appendAtomically false`)
- **18.2 plan written and approved** after three rounds of user decisions: nested structs
  supported with `[structs]` depth limits (warn 3, max 3); positional **and** named
  construction, with named arguments built now for function calls too (18.2.2); string
  fields mutable, not pooled, never cut below `string_max_length` (default 4096, or "max
  memory" = unsafe/no limit), `string_warn_length` (64) a guideline only. User accepted that
  growable heap string fields wait for 18.3 ("for now the string fixed length is ok")
- **18.2.1 COMPLETE** - see the 18.2 Detailed Plan for the full checklist and notes. Committed
  (`88d0ef5`) and pushed; `main` now tracks `origin/main`. Set `windows.appendAtomically
  false` (repo-local) so git can write its logs in the Dropbox folder - safe because only one
  PC uses the folder at a time
- **18.2.2 COMPLETE** - named arguments for function calls and struct construction; logged
  Task 15.11 (`{@1}` positional interpolation never worked)
- **18.2.2b COMPLETE** (added at the user's request, plan approved): `{@N}` placeholders in
  print (closes 15.11, fixes `print("{@1}")` printing "1") and left-to-right argument order
  for every call. Logged Task 15.12 (operator operand order)
- Pushed 18.2.2 and 18.2.2b to GitHub
- **18.2.3 COMPLETE** - nesting with the `[structs]` depth limits; fixed NULL string arrays
- **18.2.4 COMPLETE (2026-10-09)** - arrays as function return values; **Task 18.2 done**
- **18.3 plan approved (2026-10-09)** - all four decisions took the recommended option
  (values + automatic cleanup; bad conversions stop with an error; bytes; equality
  recommendations accepted). User decided error handling: Go-style error returns *and*
  try/catch, both on by default, both switchable in the config - logged as **Task 21**,
  scheduled right after 18.3
- **18.3.1 COMPLETE** - strings are values with automatic cleanup; leak check on every test
- **Next Action:** implement **18.3.2 (string operations)** per the approved plan.

---

### Session 30 (2026-10-09 - 18.2.4, 18.3 plan, 18.3.1 strings, Task 22 tracking restructure)
- Done: 18.2.4 (array returns, completes 18.2), 18.3 plan approved, 18.3.1 (string values +
  automatic cleanup + leak check), Task 21 recorded (error handling decisions), Task 22
  (FEATURES.md, SYNTAX_REFERENCE.md, CLAUDE.md slimmed 629 -> ~120 lines, this file
  2,738 -> ~200 lines, `task/taskBacklog.md`, `task/automation.md`, `check.py`)
- User notes: string pool, GC and string methods stay planned as advanced features (after
  MVP); keep `task/automation.md` updated with repeated commands
- Not pushed yet: 18.2.3, 18.2.4, 18.3.1, 22 (ask before pushing)
- 18.3.2 COMPLETE (string operations).
- 18.3.2b COMPLETE (Unicode by default).
- 18.3.3 COMPLETE (interpolated strings as values, format).
- 18.3.4 COMPLETE (string_max_length at run time).
- 18.3.4b COMPLETE (no length limit by default; exceeding a project limit is an error).
- 18.3.5 COMPLETE (equality operator family; Task 18.3 core done).
- 18.3.5b COMPLETE (a bool prints as true / false).
- 18.3.6 plan approved (all four decisions; formatNumber takes both pattern styles).
- 18.3.6a COMPLETE (optional built-in arguments, inspect / search / extract).
- 18.3.6b COMPLETE (change functions; toUpper / toLower cover Latin-1).
- 18.3.6c COMPLETE (padding & alignment).
- 18.3.6c revised: truncate adds nothing (user decision).
- 18.3.6d plan approved (two's complement C# style; bytes as hex now; literals with _).
- 18.3.6d-1 COMPLETE (number bases, bytes as hex, 0x / 0b / 0o literals).
- 18.3.8 COMPLETE (raw bytes: byte / bytes, added at the user's request).
- 18.3.6d-2 COMPLETE (formatNumber, both pattern styles).
- 18.3.6e COMPLETE (compare functions).
- 18.3.6f COMPLETE (masking design overview in the spec, 9 open questions); 18.3.6 done.
- Masking: all 9 design questions decided (ready to build, listed in FEATURES).
- 18.3.7 COMPLETE (built-in type classes and method syntax) - Task 18.3 complete.
- **Next Action:** user to choose: build masking, or plan **18.4 (import and multi-file projects)**.
