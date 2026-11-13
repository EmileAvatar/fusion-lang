[< 020 Settings](020-Settings.md) | [Index](index.md) | [031 Regex >](031-Regex.md) <!-- nav -->

# 030 Library Layout

**Status:** idea - every fusionlib module is named first in FEATURES 43.6, then designed one at a time (Task 43)

## Updated Module Count

With these additions:

```
Original Modules: 21
+ fusionlib.IDE (new): 1
= Total: 22 modules
```

**Settings consolidated into IDE module:**
- `fusionlib.IDE` - **ALL development/compile-time settings:**
  - Compiler settings (target platform, optimization, safety mode)
  - Build configuration (project.json reading)
  - IDE preferences (block style, indent size)
  - Language Server Protocol
  - Syntax highlighting
  - Code formatter

**Runtime config parsing:**
- `fusionlib.Data` - **Already exists!** Handles JSON/XML/YAML/INI parsing at runtime
  - No new module needed for user app config
  - Games/apps use Data module to read settings.json at runtime

---


## Updated Standard Library Organization

### Core Libraries (5 modules - unchanged)
1. Core - **Enhanced with Config API**
2. Math
3. Collections
4. Threading
5. IO

### Additional Libraries (12 modules - unchanged)
6. Net
7. Data
8. System - **Enhanced with CompilerSettings and BuildConfig**
9. Lang
10. Languages
11. GUI
12. Graphics
13. Audio
14. Crypto
15. Database
16. Web
17. AI

### IDE & Development (5 modules - **+1 new**)
18. Reflection
19. Test
20. Diagnostics
21. DocWiki
22. **IDE** - **NEW MODULE** (LSP, Syntax Highlighting, Formatter, CompilerSettings, BuildConfig, ProjectConfig, UserPreferences)

**Total: 22 modules**

**Key Design Decision:** All compile-time/development settings consolidated into fusionlib.IDE
- Cleaner separation: Runtime code never imports fusionlib.IDE
- Smaller executables: IDE module excluded from release builds
- Simpler architecture: One module for all developer tooling

### Why This Design is Better

**Problem with splitting settings across modules:**
- ❌ Pollutes System module with development-only features
- ❌ Adds Config API to Core when Data module already exists
- ❌ Confusing: "Is this compile-time or runtime?"
- ❌ Runtime executables include compile-time settings (wasted space)

**Solution: Consolidate into IDE module:**
- ✅ Clear separation: IDE = development, Data = runtime
- ✅ No duplication: Data already parses JSON/XML/YAML
- ✅ Smaller binaries: Release builds exclude IDE module entirely
- ✅ Logical grouping: All developer tools in one place
- ✅ Easier to understand: "Need settings? Use IDE module when compiling, Data module at runtime"

**Example:**
```fusion
// WRONG: Don't do this in runtime code
import fusionlib.IDE  // This is for compiler/IDE only!

void function main()
    // DON'T access compiler settings at runtime
    Platform p = CompilerSettings.getTargetPlatform()  // ❌ Bad design
```

```fusion
// RIGHT: Runtime config parsing
import fusionlib.Data

void function main()
    // Parse user config at runtime
    string json = File.readAllText("settings.json")
    JSON.Object config = JSON.parse(json)  // ✅ Good design
    int width = config.getInt("graphics.width")
```

---


## fusionlib: Every Planned Module (names only)

**Status:** To plan (user, 2026-11-01 - files/FEATURES.md 43.6): a list of every Fusion library
module, just its name first; each is designed later, one at a time.

---

## Summary

These packages extend Fusion without affecting the minimal core.
All of them are **modular**, **opt-in**, and **domain-specific**, designed to grow the Fusion ecosystem cleanly.


---


## Additional Ideas (Lower Priority)

### Code Navigation
- Breadcrumb navigation in IDEs
- Symbol outline view
- Code minimap

### Refactoring Tools
- Rename symbol (with references)
- Extract function
- Extract variable
- Inline variable
- Change block style (refactor entire file)

### Debugging Integration
- Debugger protocol
- Breakpoint support
- Variable inspection
- Call stack visualization
- Watch expressions

### Code Quality
- Linter integration
- Code smell detection
- Complexity metrics
- Dead code detection

### Project Management
- Project templates (web app, game, CLI tool)
- Dependency manager integration
- Build script generation
- Deployment tools

[< 020 Settings](020-Settings.md) | [Index](index.md) | [031 Regex >](031-Regex.md) <!-- nav -->
