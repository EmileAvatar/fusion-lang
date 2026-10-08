# Fusion Programming Language - Claude Code Instructions

**Project:** Fusion Compiler Development
**Icon:** 🏗️ (official)
**Status:** MVP Complete - Post-MVP Development Phase

---

## 🚨 CRITICAL RULES - READ FIRST EVERY SESSION

### Rule 1: PLAN FIRST, THEN ACT

**NEVER implement without an approved plan!**

1. **Read taskSummary2.md** at session start
2. **Create detailed plan** in taskSummary2.md for ANY new work
3. **Show plan to user** and get approval
4. **ONLY THEN** implement the approved plan
5. **Update taskSummary2.md** after completing each sub-task

**Why:** Prevents AI drift, hallucinations, and wasted effort.

**Example Workflow:**
```
User: "Add const keyword support"
Claude: [Read taskSummary2.md]
Claude: [Add Task 7.X with detailed sub-tasks]
Claude: "Here's my plan... [show plan]. Should I proceed?"
User: "Yes, go ahead"
Claude: [Implement Task 7.X.1]
Claude: [Update taskSummary2.md - Task 7.X.1 complete]
Claude: [Implement Task 7.X.2]
... etc
```

---

## 📋 IMPORTANT NOTES

### Repository Status
- **Repository is PUBLIC** (made public 2026-08-04, after a git-history scrub removed the
  personal email address that had been in early commits - verified via GitHub API that the
  scrub held and a commit-search for the email returns zero results)
- **Naming Conflict Discovered**: There is an existing programming language called "Fusion"
  - https://github.com/fusionlanguage/fut
  - https://fusion-lang.org/
- **Renaming Plan**:
  - Will continue using "Fusion" name during development
  - Will rename ONLY after language is fully working and stable
  - Rename will happen after we can compile Fusion code to executables without issues
  - No rush - focus is on getting the language working correctly first

---

### Rule 2: NO EMOJIS IN CODE FILES

**CRITICAL: Emojis cause encoding errors!**

✅ **Emojis OK in:**
- Chat responses
- Markdown files (*.md)
- Comments in markdown

❌ **NEVER use emojis in:**
- Python files (*.py)
- C files (*.c, *.h)
- Any source code files
- Configuration files
- JSON/YAML files

**Why:** Unicode characters cause encoding errors on different systems (cp1252 on Windows, UTF-8 on Linux, etc.)

**Instead of emojis in code, use:**
- `[OK]` not ✓
- `[FAIL]` not ✗
- `[WARN]` not ⚠️
- `# TODO` not 🔴

---

### Rule 3: Task Tracking

**Active Files:**
- `taskSummary2.md` (ROOT folder) - Post-MVP tasks (Tasks 5+)
- `task/taskSummary.md` (ARCHIVED) - MVP tasks (Tasks 1-4)
- `task/taskSummaryArchive.md` (ARCHIVED) - Completed post-MVP task detail (Tasks 5+)
- `task/task-X.X.md` - Detailed task breakdowns

**Task Numbering:**
- Tasks 1-4: MVP (Phases 1-4) - COMPLETE
- Tasks 5+: Post-MVP (Verification, new features) - ACTIVE

**Update Frequency:**
- After EVERY sub-task completion
- At session start
- At session end

**Archiving Policy (minimize token usage):**
- `taskSummary2.md` grows every session and gets expensive to read into context - keep it
  small by moving fully-completed task sections out of it
- When a whole numbered task (all its sub-tasks) is marked Complete, move that task's full
  section (sub-tasks, success criteria, deliverables) from `taskSummary2.md` to
  `task/taskSummaryArchive.md`, verbatim
- Leave behind a short pointer in `taskSummary2.md` where the section was (task name + status +
  "see task/taskSummaryArchive.md") - do NOT delete the Overall Progress table row or Working
  Notes session history; those stay in the active file
- Do this as part of closing out a task (same session it's completed, or the next time
  `taskSummary2.md` is touched), not as a separate ceremony the user has to ask for each time

---

### Rule 4: File Organization

**Current Structure:**
```
d:\Dropbox\Fusion\
├── taskSummary2.md           [ACTIVE - Keep in root]
├── CLAUDE.md                 [This file]
├── README.md                 [Project readme]
├── main.py                   [Compiler entry point]
├── task/                     [Task tracking]
│   ├── taskSummary.md        [ARCHIVED - MVP complete]
│   ├── taskSummaryArchive.md [ARCHIVED - completed post-MVP task detail]
│   ├── task-*.md             [Task details]
│   └── Revisit.md            [Technical debt]
├── files/                    [Documentation]
│   ├── *.md specs            [Language specs]
│   └── archive/              [Old versions]
├── src/                      [Source code]
│   ├── lexer/
│   ├── parser/
│   ├── semantic/
│   ├── codegen/
│   ├── config/               [Project config - fusion.toml loading, Task 12.12]
│   └── utils/
├── tests/                    [All test files]
│   ├── test_*.py             [Unit tests]
│   └── verify_examples.py    [Verification script]
├── examples/                 [Example programs]
│   ├── *.fusion              [Fusion source]
│   └── *.exe                 [Compiled executables]
├── FutureFeatures.md         [Post-MVP features - a menu, not commitments]
└── FutureFeaturesCaution.md  [Read before FutureFeatures.md - review, cautions, priorities]
```

**Rules:**
- taskSummary2.md stays in ROOT (active file)
- Use `files/` for documentation
- Use `tests/` for all test scripts
- NO `docs/` folder until compiler goes live

---

## 📍 CURRENT STATUS

**Date:** 2026-10-08
**Phase:** Post-MVP Development - Tasks 5-9 and 12 complete; Task 18 (Core Language) in progress
**MVP Status:** ✅ COMPLETE - see task/taskSummary.md; Tasks 5-9 and 12 also complete (see below)

**Test Results:**
- 1,337 tests passing (99.4%)
- 8 tests skipped (single-quote comment syntax - deferred design decision, conflicts with
  char literals; the earlier 2 skipped const tests were unskipped in Task 8.5)
- 0 tests failing

**Example Verification:**
- 10/10 examples compile, run, and produce correct output (hello_world, factorial, fizzbuzz,
  calculator, sum_array, max_three, const_demo, arrays_demo, functions_demo, structs_demo)
- Plus `examples/project_config_demo/` - a manual (not automated-harness) demo of
  `fusion.toml` actually changing compiler behavior (Task 12.12)
- FizzBuzz bug fixed long ago (Task 6.2) - was a lexer bug in interpolation part-splitting

**Completed since MVP:** Task 5 (cleanup), Task 6 (verification/FizzBuzz fix), Task 7 (git/
GitHub), Task 8 (const), Task 9 (fixed-size arrays v1), Task 12 (all 12 sub-tasks: Typed AST,
codegen split, block scoping, memory model semantics, docs sync, project config system, and
two deliberately-deferred design decisions - IR layer and stdlib lowering)

**In progress:** Task 18 (Core Language Foundation). **18.1** (default params, array
params, lambdas) is complete. **18.2 (structs)** has an approved four-part plan; **18.2.1**
(core structs) and **18.2.2** (named arguments) are complete, next is **18.2.3 (nesting)**. Task 19.1-19.5 depend on 18.4 (`import`). Guiding rule:
a simple working language first, complex features after (see `FutureFeaturesCaution.md`).
Security principle: **never trust code**.

**Open / not yet scoped:** Task 13 (HIDL module), Task 14 (nullable arrays/safe navigation),
Task 15 (deferred-decisions revisit list), Task 16 (example coverage), Task 17 (mutable/fixed
strings & pooling), Task 10 (self-hosting), Task 11 (LLVM backend) - see taskSummary2.md

**Next:** See taskSummary2.md's "Next Action" line (bottom of file) for the current session's
starting point

---

## 🎯 Core Concept

Fusion is an **agnostic programming language** where developers configure which features, safety levels, and performance systems apply per build or project.

The compiler adapts to project configuration (memory model, locking strategy, strictness level, async behavior).

---

## 📊 MVP Summary (Tasks 1-4 - COMPLETE)

### Phase 1: Lexer (100% Complete)
- 9/9 tasks complete
- 412 tests passing
- Tokenization, indentation tracking, block styles, keywords, operators, literals, comments

### Phase 2: Parser (100% Complete)
- 6/6 tasks complete
- 251 tests passing
- AST nodes, expression/statement/declaration parsing, all 3 block styles

### Phase 3: Semantic Analyzer (100% Complete)
- 6/6 tasks complete
- 230 tests passing
- Symbol table, type checking, name resolution, control flow, entry point validation

### Phase 4: Code Generator (100% Complete)
- 5/5 tasks complete
- 150 tests passing
- C code generation, GCC integration, end-to-end compilation

**Total:** 1,041 tests passing across all phases

---

## 🗂️ Documentation Reference

| File | Location | Purpose |
|------|----------|---------|
| **taskSummary2.md** | Root | Active task tracking (Tasks 5+) |
| **taskSummary.md** | task/ | Archived MVP tasks (Tasks 1-4) |
| **taskSummaryArchive.md** | task/ | Archived completed post-MVP task detail (Tasks 5+) |
| **task-X.X.md** | task/ | Detailed task breakdowns |
| **Revisit.md** | task/ | Technical debt tracking |
| **fusion.ebnf** | files/ | Grammar specification |
| **fusion-language-spec.md** | files/ | Complete language spec (5000+ lines) |
| **fusion-summary.md** | files/ | High-level overview (historical planning snapshot - predates compiler work, see its own header note) |
| **fusion_specs.md** | files/ | API specifications |
| **fusion-strict.md** | files/ | Strict mode rules |
| **fusion-threading-concurrency.md** | files/ | Threading model |
| **fusion-planning.md** | files/ | Development roadmap |
| **Fusion_Hardware_Interface_Definition_Language_HIDL.md** | files/ | HIDL vision doc (Task 13, blocked/future) |
| **Fusion_domain.md** | files/ | User-facing domain-first feature hierarchy - what Fusion supports/will support, organized by language domain (types, control flow, OOP, memory, concurrency, stdlib), not by build status |
| **task-10-self-hosting-plan.md** | task/ | Self-hosting detailed plan |
| **task-11-llvm-backend-plan.md** | task/ | LLVM backend detailed plan |
| **FutureFeatures.md** | Root | Post-MVP features (IDE, Settings, etc.) - a menu of possibilities, not commitments |
| **FutureFeaturesCaution.md** | Root | Read before FutureFeatures.md: project review, cautions (scope, feature interactions, ecosystem fragmentation), memory-strategy selection guide, library trust/sandboxing/supply-chain security (zero trust in library authors), and why core-language work (Task 18) comes first |

---

## 🔧 Quick Syntax Reference

### Function Declaration
```fusion
// Return-type-first syntax
<return_type> function <name>(<type> <param> = <default>)

// Examples
int function add(int a, int b) : a + b
void function greet(string name = "World") : print("Hello, {name}!")

// Defaults must come last and be constants (literals, or a negated number); omitted
// trailing arguments are filled in at the call site: greet() -> greet("World") (Task 18.1.1)

// Named arguments (Task 18.2.2): any order, unnamed ones first, any default skippable;
// evaluated left to right as written. Not for builtins or function variables
createShip("Discovery", crew = 80)
int r = sub(b = 5, a = 3)
```

### Lambdas (Task 18.1.3 - no closures yet)
```fusion
(int) : int op = func(int x) : x * 2     // function type, inline lambda
int function apply((int) : int f, int v) : f(v)
int r = apply(tripler, 5)                // named functions are values too
```

### Block Styles
```fusion
// 1. Indentation (Python-style)
if condition
    statement1

// 2. Braces (C/Java-style)
if condition {
    statement1
}

// 3. End keyword (VB.NET-style)
if condition
    statement1
End if
```

### String Interpolation
```fusion
// Inline: {variable}
print("Name: {name}, Age: {age}")

// Positional: {@1}, {@2}, ... - documented but NOT working yet (Task 15.11)
print("User {@1} is {@2} years old", name, age)
```

### Variable Declaration
```fusion
// Explicit type (required in safe mode)
int count = 0
string name = "Alice"

// Constant (must initialize)
const float PI = 3.14159
```

### Arrays
```fusion
// Fixed size, inferred from the literal
int[] scores = [10, 20, 30]

// Explicit size, zero-initialized
float[3] buffer

scores[0] = 99          // element assignment
int n = len(scores)     // size (compile-time constant)

// Array parameters (by reference): int[] = any size (len() works), int[3] = exactly 3
int function sum(int[] values)
int total = sum(scores)
```

### Structs (Task 18.2.1 - fields only, value types)
```fusion
struct Point            // also: struct Point { ... }  or  ... End struct
    int x
    int y

struct Player
    string name
    float health = 100.0     // field defaults: constants only

Point a = Point(3, 4)        // generated constructor, fields in declaration order
Point n = Point(y = 4, x = 3)   // named construction (18.2.2)
Point b = a                  // copies; b.x = 9 leaves a alone
Point z                      // every field its default, or zero
a.x = 10
print("({a.x}, {a.y})")      // fields in interpolation
Point function add(Point p, Point q) : Point(p.x + q.x, p.y + q.y)   // by value
```
No methods/operators in structs - use functions. Not yet: `==` on structs (18.3), printing a
whole struct, nested structs / array fields / arrays of structs (18.2.3).

### Project Configuration (`fusion.toml`)
```toml
# Optional - place next to your .fusion source file (or in the cwd). Every key defaults
# to the value shown; a missing file is not an error.
# Decided (Task 20, not yet implemented): fusion.yaml / fusion.json / fusion.ini will be
# accepted interchangeably. Until then only fusion.toml works.
[indentation]
tab_width = 4        # spaces per tab
allow_mixed = true   # mixed tabs/spaces: warning (true) vs compile error (false)

[source]
allow_unicode_identifiers = false   # ASCII-only identifiers by default (Task 19.6)

[structs]                      # Task 18.2
max_nesting_depth  = 3         # 1 = no nested structs (enforced from 18.2.3)
warn_nesting_depth = 3         # 0 = never warn (enforced from 18.2.3)
string_storage     = "owned"   # "pooled" reserved (Task 17) - compile error until then
string_mutable     = true      # false = string fields fixed after construction
string_warn_length = 64        # guideline only: longer strings kept, with a warning
string_max_length  = 4096      # the one hard cut-off; "max memory" = no limit (unsafe)

[safety]
mode = "normal"      # "normal" | "strict" - reserved, not yet enforced (Task 12.12)

[backend]
target = "c"         # "c" only for now - "llvm" reserved for Task 11
```

---

## 🔑 Reserved Keywords (67 total)

**Control Flow:** if, else, for, while, loop, end, break, continue, return, match, case

**Functions:** function, func, async, await

**Classes:** class, struct, interface, enum, inherits, implements, property, get, set

**Modifiers:** public, private, protected, static, virtual, override, abstract, sealed

**Variables:** var, const

**Literals:** true, false, null, this

**Operators:** and, or, not, is, in

**Types:** int, float, double, string, bool, char, byte, short, long, void

**Memory:** Unique, Shared, Weak

**Threading:** go

**Error:** try, catch, finally, throw, Error

---

## 📚 Fusion Standard Library (fusionlib)

**21 Modules Total**

### Core Libraries (5 modules)
- **Core** - Essential types, Console I/O, DateTime
- **Math** - Vector, Matrix, Quaternion, trigonometry
- **Collections** - List, Dictionary, Set, Queue, Stack, LINQ
- **Threading** - Threads, Goroutines, Channels, Mutex, Async/await
- **IO** - File operations, Streams, Compression

### Additional Libraries (12 modules)
- **Net** - TCP/UDP, HTTP, WebSocket, DNS, Email, FTP
- **Data** - JSON, CSV, XML, YAML, Markdown, INI
- **System** - Process management, DLL loading, environment
- **Lang** - Multi-language compilation (C, C++, Java, Python)
- **Languages** - i18n/l10n, translations, locale
- **GUI** - HTML5-compliant cross-platform UI
- **Graphics** - 2D/3D rendering, sprites, shaders
- **Audio** - Sound playback, synthesis, effects, MIDI
- **Crypto** - Encryption, hashing, SSL/TLS
- **Database** - SQL/NoSQL support, ORM
- **Web** - HTTP server, REST API framework
- **AI** - Neural networks, ML algorithms

### IDE & Development (4 modules)
- **Reflection** - Runtime type inspection, dynamic execution
- **Test** - Unit testing framework, assertions, coverage
- **Diagnostics** - Profiling, logging, debugging
- **DocWiki** - Automatic documentation generation

**Import Pattern:** `import Fusion.<ModuleName>` or `import fusionlib.<ModuleName>`

---

## ⚙️ Compiler Implementation Details

**Language:** Python (for MVP)
**Target:** C code → GCC → Native executable
**Future:** Self-hosting (rewrite compiler in Fusion)

**Current Features:**
- Block-level (lexical) scoping: a variable declared inside `if`/`while`/`for` is only
  visible inside that block, and a nested block can shadow an outer variable of the same
  name (Task 12.6, complete - replaced the earlier function-scoped model, which had a
  real bug: semantic analysis accepted programs whose generated C could never actually
  compile, since C's own `{ }` braces are natively block-scoped)
- Three block styles (indentation, braces, End keywords)
- String interpolation ({var} and {p.x}; the {@1} positional form does not work yet - Task 15.11)
- Type checking with automatic int→float promotion
- Recursive functions and lambdas
- void main() → int main() automatic conversion
- C keyword name mangling (function "double" → "fusion_double")
- const declarations: must initialize, enforced immutable by semantic analyzer, emitted as
  C `const` (Task 8, complete)
- Fixed-size arrays: `int[] x = [1,2,3]` or `int[5] x`, element read/write (`x[i]`,
  `x[i] = v`), `len(x)` resolved to a compile-time constant (Task 9 v1, complete)
- Project configuration via an optional `fusion.toml` (source file's directory, then cwd) -
  `[indentation]` (`tab_width`/`allow_mixed`) actually reaches the lexer; `[safety]`/
  `[backend]` are parsed/validated but not yet enforced (Task 12.12, complete - see
  `src/config/project_config.py` and `examples/project_config_demo/`)
- Source-level attack defenses (Task 19.6, complete - `src/lexer/source_security.py`):
  invisible/bidirectional control characters rejected anywhere in a file incl. comments and
  strings (Trojan Source); identifiers ASCII-only by default, opt-in via `[source]
  allow_unicode_identifiers` (mixed look-alike scripts still rejected); `\uXXXX` escapes in
  string and char literals; lexer warnings printed by `main.py`
- Char literals work correctly end-to-end (`char c = 'a'` - was broken before Task 19.6)
- Functions (Task 18.1, complete): parameter default values; arrays as parameters (`int[]` any
  size, `int[5]` exact, by reference); lambdas and function types (`(int) : int`), named
  functions as values, calls through function variables - no closures yet (Task 18.3 first)
- Structs (Task 18.2.1): fields only (no methods), three block styles, generated positional
  constructor, field defaults, `.` access/assignment incl. in `{p.x}` interpolation, value
  semantics (copy on assign/pass/return), const structs, `[structs]` string-field length
  rules (see `tests/test_structs.py`, `examples/structs_demo.fusion`)
- Named arguments (Task 18.2.2): `f(b = 1, a = 2)`, `Point(y = 4, x = 3)` - any order after
  unnamed ones, any defaulted parameter skippable, evaluated left to right as written

**Known Limitations (by design):**
- Single-quote comments disabled (conflicts with char literals)
- Identifiers are ASCII-only unless `fusion.toml` opts in; char literals hold one ASCII
  character (a C `char` is one byte) - both by design (Task 19.6)

**Known bugs (logged, not yet fixed):**
- String `==` compares C pointers, not contents (correct today only by accident). Task 18.3
- Interpolated strings only work as `print()`'s own argument - elsewhere they're now a clear
  error (Task 15.10, they used to generate invalid C); `{...}` holds a name or field path
  (`{p.x}`), not a full expression yet. Building strings at run time is Task 18.3
- Positional interpolation (`print("{@1}", name)`, shown in the Quick Syntax Reference) has
  never compiled - `print` accepts only one argument (Task 15.11)
- const follows the same block scoping as other variables (no global/class-level
  constants yet - classes not implemented)
- `fusion.toml`'s `[safety]`/`[backend]` sections are recognized and validated but not
  enforced by any compiler pass yet (same status as the `Unique`/`Shared`/`Weak` keywords
  below - reserved, not implemented); `[indentation]`, `[source]` and `[structs]` change
  real behavior today
- Arrays can be function parameters (by reference) but not return types (Task 18.2.4); they're
  single-dimension,
  fixed-size (no dynamic resize), no bounds checking, and not nullable (no `.length`,
  `?.`, or `?[` yet - see taskSummary2.md Task 14)

---

## 🔄 Archive Policy

**Ignore unless explicitly requested:**
- `files/archive/*` - Old specification versions
- Single-quote comment tests (8 skipped) - Future design decision

**Technical Debt:**
- See `task/Revisit.md` for deferred issues
- Review before each major release

---

## 🎯 Auto-Update Policy

**When updating any Fusion specification, automatically propagate changes to ALL relevant files:**

| If User Changes... | Must Auto-Update... |
|-------------------|---------------------|
| Lambda syntax | EBNF grammar, language-spec, summary, CLAUDE.md, examples |
| Block syntax | EBNF grammar, language-spec, summary, CLAUDE.md |
| Standard library module | fusionlib table (CLAUDE.md), language-spec, summary |
| Type system | EBNF grammar, language-spec, summary, CLAUDE.md |
| String interpolation | language-spec, CLAUDE.md, code examples |
| Keywords/operators | EBNF grammar, language-spec, summary |

**DO NOT ASK** - just update all files automatically to maintain consistency.

---

## 📝 Session Workflow

**At Session Start:**
1. Read `taskSummary2.md`
2. Check current task status
3. Review any notes from previous session

**During Work:**
1. Create plan in taskSummary2.md for new tasks
2. Get user approval
3. Implement approved plan
4. Update taskSummary2.md after each sub-task

**At Session End:**
1. Update taskSummary2.md with current state
2. Document any blockers or issues
3. Set "Next Action" for next session

---

## 🚀 Next Steps

**Current Focus:** Tasks 18.2.1 (core structs) and 18.2.2 (named arguments) are done. Next:
18.2.3 (nesting), per the approved 18.2 plan in taskSummary2.md. Read
`FutureFeaturesCaution.md` before picking up anything from `FutureFeatures.md`.

**Completed:**
- Tasks 1-9 and 12 - see task/taskSummary.md and task/taskSummaryArchive.md for full detail

**Planned (see taskSummary2.md for full detail and current blockers):**
- Task 13: HIDL module, Task 14: Nullable arrays & safe navigation - both unblocked, need
  scoping approval
- Task 15: Deferred decisions revisit list (IR layer, stdlib lowering, a LambdaExpr scope
  bug, Task 10/11 ordering, etc.) - each item has its own trigger
- Task 16: Example program coverage (16.1 buildable now)
- Task 17: Mutable/fixed strings, templated strings, string pooling - logged, not scoped
- Task 10: Self-hosting, Task 11: LLVM backend (both planning-complete, intentionally not
  started - ordering between them is itself an open question, Task 15.4)

---

## 💻 Setting Up a New Machine

The repo is fully self-describing - no out-of-band context is needed beyond this file and
`taskSummary2.md`. To verify a fresh environment:

1. **Python 3.11+** (required - `src/config/project_config.py` uses stdlib `tomllib`)
2. **GCC on PATH** (MinGW-w64 on Windows) - `main.py` invokes `gcc` directly
3. `pip install -r requirements.txt`
4. `python -m pytest tests/ -q` - expect **1337 passed, 8 skipped**
5. `python tests/verify_examples.py` - expect **10/10**

If both match, the environment is correct. Note `Notes/` (user's AI review notes) and
`.claude/settings.local.json` (Claude Code permissions) are gitignored - they exist only via
Dropbox sync, not via `git clone`.

---

**Last Updated:** 2026-10-08
**Version:** 2.0 (Post-MVP)
**Next Action:** See taskSummary2.md
