# Fusion Libraries (fusionlib)

A summary of the planned standard library, gathered from the spec files on 2026-11-19 for review.
Status: [DESIGN] - each module's API is designed in Task 43 (43.6: every module's name first).

## 1. Overview and where the lists are

fusionlib has **21 modules in three tiers**: 5 Core + 12 Additional + 4 IDE.

| File | What's in it |
|---|---|
| `files/spec/180-StandardLibrary.md` | Library areas overview: collections, math, file I/O, file formats, images, localization, networking, graphics/audio, threading, date/time, regex |
| `files/spec/181-fusionlib-Core.md` | The three-tier overview (top) + the 5 Core modules |
| `files/spec/182-fusionlib-Extended.md` | The 12 Additional modules |
| `files/spec/183-fusionlib-IDE.md` | The 4 IDE modules + the **Library Summary** (line ~202) listing all 21 imports |

Ideas, not yet in the 21 (`files/future/`):
- `030-LibraryLayout.md`, `010-IDEModule.md` - a 22nd module `fusionlib.IDE` holding all
  compile-time / editor settings (compiler, build config, IDE preferences, LSP, highlighting, formatter)
- `031-Regex.md`, `032-DomainPackages.md`, `033-Currency.md` - more library ideas

Naming: imports are moving from `import fusionlib.X` to `import Fusion.X` (D.136, Task 57).
Related `Decisions.md` entries: SET.014 (modules beyond the core), SET.024 (IDE module),
MOD.009 / D.098 (data formats live in fusionlib), D.121 (language modules `Lang.<language>.Fusion`).

## 2. Library table

| # | Library | Type | Description |
|---|---|---|---|
| 1 | Fusion.Core | Core | Essential types, console I/O, DateTime - string handling, console apps, basic I/O |
| 2 | Fusion.Math | Core | Vector, Matrix, Quaternion, trigonometry - games, graphics, physics, science |
| 3 | Fusion.Collections | Core | List, Dictionary, Set, Queue, Stack - data storage, algorithms, query operations |
| 4 | Fusion.Threading | Core | Threads, goroutines, channels, async - concurrency, parallel work, async I/O |
| 5 | Fusion.IO | Core | File operations, streams, compression - file handling, persistence, archives |
| 6 | Fusion.Net | Additional (Networking & Data) | Network communication protocols and utilities |
| 7 | Fusion.Data | Additional (Networking & Data) | Parsing and serialization of data formats (JSON, XML, TOML, YAML, INI, MD) |
| 8 | Fusion.System | Additional (System Integration) | Operating system integration and process management |
| 9 | Fusion.Lang | Additional (System Integration) | Multi-language compilation and code execution support |
| 10 | Fusion.Languages | Additional (System Integration) | Internationalization and localization |
| 11 | Fusion.GUI | Additional (Multimedia & UI) | Cross-platform user interface framework |
| 12 | Fusion.Graphics | Additional (Multimedia & UI) | 2D/3D rendering and game development utilities |
| 13 | Fusion.Audio | Additional (Multimedia & UI) | Sound playback, synthesis and audio processing |
| 14 | Fusion.Crypto | Additional (Advanced) | Cryptography and security operations |
| 15 | Fusion.Database | Additional (Advanced) | Database connectivity and ORM support |
| 16 | Fusion.Web | Additional (Advanced) | Web server and REST API framework |
| 17 | Fusion.AI | Additional (Advanced) | Machine learning and artificial intelligence |
| 18 | Fusion.Reflection | IDE & Development | Runtime type introspection and dynamic code execution |
| 19 | Fusion.Test | IDE & Development | Testing framework with IDE integration |
| 20 | Fusion.Diagnostics | IDE & Development | Profiling, logging and debugging utilities |
| 21 | Fusion.DocWiki | IDE & Development | Automatic documentation and wiki generation during background compilation |
| (22) | fusionlib.IDE | Idea (future) | All compile-time / development settings: compiler, build config, IDE preferences, LSP, highlighting, formatter |
| - | Regex | Idea (future) | Regular expressions (`files/future/031-Regex.md`) |
| - | Currency | Idea (future) | Currency conversion and locale-aware formatting; rates passed in by the developer, never fetched (`files/future/033-Currency.md`) |
| - | Domain packages | Idea (future) | Domain-specific packages (`files/future/032-DomainPackages.md`) |
