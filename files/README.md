# 🏗️ Fusion Language Documentation

Complete specification for the Fusion programming language.

Last Updated: November 2, 2025

**Historical snapshot (flagged 2026-09-13, Task 12.8):** written before compiler implementation
began - its "Project Status" table below still says `Compiler: Not Started`. That's long out of
date: the MVP compiler is complete and Tasks 5-9 plus Task 12's Core Typed AST have shipped
since. See `../CLAUDE.md` and `../taskSummary2.md` (root of the repo) for current status; this
file is left as-is otherwise, as a record of the specification-writing phase.

---

## Core Documentation Files

**1. fusion-language-spec.md** (150+ KB)
* Complete language specification
* All syntax and semantics
* Standard Library (fusionlib) - 15 modules
* External interoperability
* Auto-documentation system
* Complete examples

**2. fusion_specs.md** (30+ KB)
* All JSON configurations
* Language templates
* Safety modes and annotations
* Configuration reference
* CLI commands

**3. fusion-threading-concurrency.md** (16 KB)
* Threading model
* Channels and synchronization
* Compiler analysis
* Advanced patterns

**4. fusion-strict.md** (Strict Mode Reference)
* Complete strict mode documentation
* Performance and security focus
* Configuration examples
* Migration guide

**5. fusion-planning.md** (Simple checklist)
* Completed features
* In progress
* Planned features
* Milestones

**6. fusion-summary.md** (This overview)
* Project status
* Module overview
* Quick reference

**7. README.md** (This file)
* Documentation index

**8. fusion.ebnf** (Grammar Specification)
* Complete BNF/EBNF grammar
* Language syntax rules
* Parser reference

---

## Quick Start

**For New Users**:
1. Read fusion-summary.md
2. Review fusion-language-spec.md
3. Check fusion_specs.md for configs

**For Implementation**:
1. Use fusion.project.json template
2. Configure safety mode
3. Set up modules from fusionlib

---

## Standard Library (fusionlib)

**22 Modules**:

| Module | Domain | Purpose | Common Use Cases |
|--------|--------|---------|------------------|
| **Core** | Core | Essential types, Console I/O, DateTime, String interpolation | String manipulation, console apps, basic I/O |
| **Math** | Core | Vector, Matrix, Quaternion, trigonometry, geometry | Games, graphics, physics simulations |
| **Collections** | Core | List, Dictionary, Set, Queue, Stack, LINQ operations | Data storage, algorithms, data structures |
| **Threading** | Core | Threads, Goroutines, Channels, Mutex, Async/await | Concurrency, parallel processing, async I/O |
| **IO** | Core | File operations, Streams, Compression, async file I/O | File handling, data persistence, archives |
| **Net** | Additional | TCP/UDP, HTTP, WebSocket, DNS, Email, FTP | Network communication, web clients |
| **Data** | Additional | JSON, CSV, XML, YAML, Markdown, INI parsers | File format parsing, data serialization |
| **System** | Additional | Process management, DLL loading, environment, OS info | System integration, external processes |
| **Lang** | Additional | Multi-language compilation (C, C++, Java, Python, etc.) | Cross-language interop, code compilation |
| **Languages** | Additional | i18n/l10n, translations, locale support, Unicode | Internationalization, localization |
| **GUI** | Additional | HTML5-compliant cross-platform UI framework | Desktop apps, user interfaces, dialogs |
| **Graphics** | Additional | 2D/3D rendering, sprites, shaders, game engine utils | Game development, 3D visualization |
| **Audio** | Additional | Sound playback, synthesis, effects, MIDI, recording | Games, music apps, audio processing |
| **Crypto** | Additional | Encryption, hashing, SSL/TLS, certificates | Security, encryption, password hashing |
| **Database** | Additional | SQL/NoSQL support, ORM, query builder | Database apps, data persistence |
| **Web** | Additional | HTTP server, REST API framework, WebSocket, routing | Web servers, REST APIs, backend development |
| **AI** | Additional | Neural networks, ML algorithms, training, inference | Machine learning, AI applications |
| **Reflection** | IDE | Runtime type inspection, dynamic code execution | IDE features, dynamic plugins, serialization |
| **Test** | IDE | Unit testing framework, assertions, coverage, mocking | Testing, TDD, benchmarking |
| **Diagnostics** | IDE | Profiling, logging, debugging, performance monitoring | Debugging, performance tuning |
| **DocWiki** | IDE | Automatic documentation generation from code comments | API documentation, wiki generation |
| **IDE** | IDE | LSP, Syntax highlighting, Formatter, Compiler settings | Development tooling, editor integration |

---

## Language Support

**10 Languages** (fusionlib.Lang):
* C, C++, Java, VB.NET
* Python, Ruby, JavaScript, Go
* Fusion (self-hosting), Assembly

---

## External Interop

* Callback functions
* DLL/shared library loading
* External process execution
* Assembly language support
* External compiler integration

---

## Configuration Files

**fusion.project.json** - Project settings
**fusion.users.json** - User roles (7 predefined)
**fusion.user.json** - User preferences (IDE settings)
**fusion.file.json** - File-specific overrides

See fusion_specs.md for complete reference.

---

## Safety Modes

**Standard** (Default) - Balanced safety and flexibility
**Strict** - Maximum safety enforcement
**Unsafe** - Minimal restrictions for performance

---

## Key Features

* Return-type-first function syntax
* Value vs reference type distinction
* Three enum syntaxes (braces, indentation, single-line)
* Dual comment styles (// and ')
* Multi-purpose ... operator
* Comparison operators (both != and <>)
* Automatic loop protection
* Try-with-resources (automatic locking)
* HTML5-compliant GUI
* Built-in language compilers

---

## Project Status

Component | Status
---|---
Language Specification | ✓ Complete
Configuration System | ✓ Complete
Standard Library Design | ✓ Complete
External Interop | ✓ Complete
Documentation | ✓ Complete
Compiler | ◯ Not Started
Runtime | ◯ Not Started
IDE Integration | ◯ Not Started

---

## File Statistics

* **8 core documentation files**
* **150+ KB** of specification
* **20 modules** in standard library
* **10 languages** supported
* **4 configuration files**
* **Complete EBNF grammar**
* **100% specification complete**

---

## Next Steps

**For Development**:
1. Begin compiler implementation
2. Implement core runtime
3. Build standard library modules
4. Create IDE plugins

**For Users** (when available):
1. Install Fusion compiler
2. Copy configuration templates
3. Write Fusion code
4. Build and run!

---

## License

Fusion Language Specification
Status: Open Specification
Version: 1.0

---

_Fusion: Combining C, Java, Python, VB.NET, and Go into one unified language._
