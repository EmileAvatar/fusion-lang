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
- **Repository is now PRIVATE** - Email address removed from public view
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
- `task/task-X.X.md` - Detailed task breakdowns

**Task Numbering:**
- Tasks 1-4: MVP (Phases 1-4) - COMPLETE
- Tasks 5+: Post-MVP (Verification, new features) - ACTIVE

**Update Frequency:**
- After EVERY sub-task completion
- At session start
- At session end

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

**Date:** 2025-12-14
**Phase:** Post-MVP Verification & Planning
**MVP Status:** ✅ COMPLETE - All 1,041 tests passing

**Test Results:**
- 1,041 tests passing (99.0%)
- 10 tests skipped (8 lexer comments + 2 const keyword)
- 0 tests failing

**Example Verification:**
- 6/6 examples compile successfully
- 6/6 examples run without crashes
- FizzBuzz output issue identified (missing numbers)

**Next:** File cleanup, verification fixes, Git integration

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
| **task-X.X.md** | task/ | Detailed task breakdowns |
| **Revisit.md** | task/ | Technical debt tracking |
| **fusion.ebnf** | files/ | Grammar specification |
| **fusion-language-spec.md** | files/ | Complete language spec (4000+ lines) |
| **fusion-summary.md** | files/ | High-level overview |
| **fusion_specs.md** | files/ | API specifications |
| **fusion-strict.md** | files/ | Strict mode rules |
| **fusion-threading-concurrency.md** | files/ | Threading model |
| **fusion-planning.md** | files/ | Development roadmap |
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
- Function-level scoping (like Python/JavaScript)
- Three block styles (indentation, braces, End keywords)
- String interpolation ({var} and {@1} syntax)
- Type checking with automatic int→float promotion
- Recursive functions and lambdas
- void main() → int main() automatic conversion
- C keyword name mangling (function "double" → "fusion_double")

**Known Limitations (by design):**
- No block-level scoping (variables are function-scoped)
- Single-quote comments disabled (conflicts with char literals)
- const keyword not yet implemented (planned for Task 7)

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

**Current Focus:** File cleanup and verification (see taskSummary2.md)

**Planned:**
- Task 5: Project organization & cleanup
- Task 6: Verification phase (investigate FizzBuzz, define expected outputs)
- Task 7: Git integration & GitHub setup
- Task 8+: New language features (const, arrays, match statement, etc.)

---

**Last Updated:** 2025-12-14
**Version:** 2.0 (Post-MVP)
**Next Action:** See taskSummary2.md
