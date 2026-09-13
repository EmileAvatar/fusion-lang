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
│   └── utils/
├── tests/                    [All test files]
│   ├── test_*.py             [Unit tests]
│   └── verify_examples.py    [Verification script]
├── examples/                 [Example programs]
│   ├── *.fusion              [Fusion source]
│   └── *.exe                 [Compiled executables]
└── FutureFeatures.md         [Post-MVP features]
```

**Rules:**
- taskSummary2.md stays in ROOT (active file)
- Use `files/` for documentation
- Use `tests/` for all test scripts
- NO `docs/` folder until compiler goes live

---

## 📍 CURRENT STATUS

**Date:** 2026-09-13
**Phase:** Post-MVP Development - Task 12 (Architecture Hardening) in progress
**MVP Status:** ✅ COMPLETE - see task/taskSummary.md; Tasks 5-9 also complete (see below)

**Test Results:**
- 1,090 tests passing (99.3%)
- 8 tests skipped (single-quote comment syntax - deferred design decision, conflicts with
  char literals; the earlier 2 skipped const tests were unskipped in Task 8.5)
- 0 tests failing

**Example Verification:**
- 8/8 examples compile, run, and produce correct output (hello_world, factorial, fizzbuzz,
  calculator, sum_array, max_three, const_demo, arrays_demo)
- FizzBuzz bug fixed long ago (Task 6.2) - was a lexer bug in interpolation part-splitting

**Completed since MVP:** Task 5 (cleanup), Task 6 (verification/FizzBuzz fix), Task 7 (git/
GitHub), Task 8 (const), Task 9 (fixed-size arrays v1), Task 12's Core Typed AST (12.1-12.4,
12.9 - codegen now reads resolved types instead of guessing format specifiers)

**In progress:** Task 12's remaining items (12.5-12.8, 12.10-12.12 - codegen module split,
scoping/memory-model/project-config decisions, IR layer and stdlib-lowering design)

**Blocked/future:** Task 10 (self-hosting), Task 11 (LLVM backend), Task 13 (HIDL module),
Task 14 (nullable arrays/safe navigation) - see taskSummary2.md for what each is blocked on

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
| **task-10-self-hosting-plan.md** | task/ | Self-hosting detailed plan |
| **task-11-llvm-backend-plan.md** | task/ | LLVM backend detailed plan |
| **FutureFeatures.md** | Root | Post-MVP features (IDE, Settings, etc.) |

---

## 🔧 Quick Syntax Reference

### Function Declaration
```fusion
// Return-type-first syntax
<return_type> function <name>(<type> <param> = <default>)

// Examples
int function add(int a, int b) : a + b
void function greet(string name = "World") : print("Hello, {name}!")
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

// Positional: {@1}, {@2}, ...
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
- String interpolation ({var} and {@1} syntax)
- Type checking with automatic int→float promotion
- Recursive functions and lambdas
- void main() → int main() automatic conversion
- C keyword name mangling (function "double" → "fusion_double")
- const declarations: must initialize, enforced immutable by semantic analyzer, emitted as
  C `const` (Task 8, complete)
- Fixed-size arrays: `int[] x = [1,2,3]` or `int[5] x`, element read/write (`x[i]`,
  `x[i] = v`), `len(x)` resolved to a compile-time constant (Task 9 v1, complete)

**Known Limitations (by design):**
- Single-quote comments disabled (conflicts with char literals)
- const follows the same block scoping as other variables (no global/class-level
  constants yet - classes not implemented)
- Arrays are local-variable-only (not function params/return types), single-dimension,
  fixed-size (no dynamic resize), no bounds checking, and not nullable (no `.length`,
  `?.`, or `?[` yet - see taskSummary2.md Task 9's deferred nullability task)

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

**Current Focus:** Task 12's remaining items (see taskSummary2.md) - codegen module split
(12.5), then a sequence of design decisions (scoping ADR, memory model, project config, IR
layer, stdlib lowering) that need the user's input, not just implementation.

**Completed:**
- Tasks 1-9: MVP + cleanup + verification + git + const + arrays (v1) - see
  task/taskSummary.md and task/taskSummaryArchive.md for full detail
- Task 12.1-12.4, 12.9: Core Typed AST - codegen reads `inferred_type` instead of guessing

**Planned (see taskSummary2.md for full detail and current blockers):**
- Task 12.5-12.8, 12.10-12.12: remaining architecture-hardening items
- Task 13: HIDL module (blocked on Task 12)
- Task 14: Nullable arrays & safe navigation (blocked on Task 12.7)
- Task 10: Self-hosting, Task 11: LLVM backend (both planning-complete, intentionally not
  started yet - the architecture review recommended stabilizing the language/IR first)

---

**Last Updated:** 2026-09-13
**Version:** 2.0 (Post-MVP)
**Next Action:** See taskSummary2.md
