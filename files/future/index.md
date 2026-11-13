# Future Features - Index

Ideas for Fusion that are not decided or scheduled yet - one topic per file, in this order. Each file
links to the one before and after it and back here. Split out of `files/FutureFeatures.md` (Task 51.5b,
2026-11-13).

> **Read [files/FutureFeaturesCaution.md](../FutureFeaturesCaution.md) first.** Everything here is a menu
> of possibilities, not a commitment - some will be built, some will change, some never added.

Each file starts with a **Status:** line: the FEATURES task or Decisions.md line that covers it now, or
"idea - no task". The language as decided: [files/spec/index.md](../spec/index.md).

| File | What it holds | Status |
|---|---|---|
| [000 Overview](000-Overview.md) | The old overview, priorities, checklist, related files, timeline, success criteria, discussion points | historic - the planning notes of 2026-09 / 10 |
| [010 IDE Module](010-IDEModule.md) | fusionlib.IDE: the proposed module and its complete API | idea - no task |
| [011 IDE Projects](011-IDEProjects.md) | The IDE module enhancements: the project integration system | idea - no task (editor support: FEATURES Task 36) |
| [012 IDE Overlays](012-IDEOverlays.md) | Code quality overlays 1-4: inverted if, thread view, profiling, duplicate code | idea - the thread view is FEATURES 36.6 |
| [013 IDE Overlays 2](013-IDEOverlays2.md) | Overlays 5-7: naming quality, nested loops, nested control flow | idea - no task |
| [014 IDE Overlay Settings](014-IDEOverlaySettings.md) | Overlay configuration per project, the IDE architecture, benefits | idea - no task |
| [015 Web Servers](015-WebServers.md) | Notes: what a web server does, its layers (found inside the overlays section) | notes - not a feature |
| [020 Settings](020-Settings.md) | Where the settings system lives (module placement), configuration file formats | partly built - the four settings formats are built (Task 31, [170 Build](../spec/170-Build.md)) |
| [030 Library Layout](030-LibraryLayout.md) | Module count, standard library organisation, every planned module's name, more ideas | idea - every fusionlib module is named first in FEATURES 43.6, then designed one at a time (Task 43) |
| [031 Regex](031-Regex.md) | The regex fluent API and the planned regex module | idea - no task (a fusionlib module - FEATURES 43.6) |
| [032 Domain Packages](032-DomainPackages.md) | Game engine, physics, ECS, shaders, NumPy-style numerics, Pandas-style data frames | idea - no task (separate packages, not the core library) |
| [033 Currency](033-Currency.md) | The Currency module; fixed-point decimals and `Currency` sugar | planned - the Currency module is FEATURES 43.3, the `money` type 47.2 |
| [034 Data Formats](034-DataFormats.md) | The data formats module: JSON, XML, TOML, YAML, INI, MD | planned - FEATURES 43.2 (MOD.009) |
| [035 HIDL](035-HIDL.md) | HIDL hardware testing ideas from Maia | planned - HIDL is FEATURES Task 41 |
| [040 Cross Language](040-CrossLanguage.md) | Cross-language compilation; self-hosting considerations | planned - the language modules `Lang.<language>.<optional flavour>.Fusion` are FEATURES Task 49 (after self-hosting, Task 35 |
| [050 Imports](050-Imports.md) | Importing several names at once; parameter syntax | design - importing only some names (MOD.005), grouped import blocks (MOD.008) |
| [060 Comments](060-Comments.md) | `'` comments at a line's start, `'''` comment blocks, the comment styles, notes | design - `'` comments postponed (SYN.031) |
| [061 Comment Highlighting](061-CommentHighlighting.md) | Language-specific highlighting inside `'''` blocks | idea - no task (with SYN.036) |
| [062 Comment Levels](062-CommentLevels.md) | Comment levels 0-5 and coding hints (developer experience) | design - comment levels and coding hints (SYN.036) |
| [070 Naming Rules](070-NamingRules.md) | Option strict naming: when short names are fine, a minimum name length | design - a minimum variable-name length in strict mode, default 3 (SYN.038) |
| [071 Naming Exceptions](071-NamingExceptions.md) | Loop counters and type parameters excepted; scope, errors, levels, IDE, benefits | design - with SYN.038 |
| [080 Arrays](080-Arrays.md) | Advanced array declaration syntax | idea - multi-dimensional arrays postponed (COL.015) |
| [081 Strings](081-Strings.md) | Mutable and fixed strings, templated fixed strings, string pooling | partly built - strings change in place, `const` strings never (Task 29, [032 Strings](../spec/032-Strings.md)) |
| [090 Unsafe](090-Unsafe.md) | Unsafe mode enhancements | design - `unsafe` blocks and functions (MEM.006, D.030, D.031) |
| [100 CLI](100-CLI.md) | The CLI tool suite: overview, commands, plan, architecture, comparison, questions | later - one `console` tool after the compiler no longer needs Python (FEATURES "Later") |
| [101 CLI Commands](101-CLICommands.md) | Each command's specification | later - with 100 CLI |
| [110 Symbol IDs](110-SymbolIDs.md) | The symbol-ID system (compiler infrastructure) | idea - no task |
| [111 Identity](111-Identity.md) | An identity for everything: a GUID per name, a small database of the hierarchy | idea - FEATURES 42.28 |
| [120 Threads](120-Threads.md) | Threads, schedulers and services: notes for later | design - the notes behind [100 Concurrency](../spec/100-Concurrency.md) (Task 42) |
| [130 Far Future](130-FarFuture.md) | Traits from variables, types made while running, DLC | idea - after self-hosting (Task 35) |
