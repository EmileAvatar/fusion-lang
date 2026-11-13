# Future Features - Index

Ideas for Fusion that are not decided or scheduled yet - one topic per file, in this order. Each file
links to the one before and after it and back here. Split out of `files/FutureFeatures.md` (Task 51.5b,
2026-11-13); a topic not listed yet is still there.

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
