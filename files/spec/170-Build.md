[< 160 GameExample](160-GameExample.md) | [Index](index.md) | [180 StandardLibrary >](180-StandardLibrary.md) <!-- nav -->

# 170 Build

Contents: [Compilation Modes](#compilation-modes) | [Project Configuration](#project-configuration) | [Build Commands](#build-commands) | [Build Configurations](#build-configurations) | [Output Targets](#output-targets) | [Using Libraries](#using-libraries)

## Build and Compilation

**Status:** [PARTLY] the settings file is built - `fusion.toml` / `.yaml` / `.json` / `.ini` (Tasks 12.12, 31); every
built setting: [001 Project Settings](001-TomlSettings.md); enforcing [safety] / [backend] [PLANNED 31.5]. Build
modes and the `fusion run` / `fusion build` commands: design, no task yet - today the compiler is
`python main.py program.fusion` (an executable, through C and GCC)

Description: Flexible compilation options for different targets and use cases.

---

### Compilation Modes

Description: Multiple ways to run and build Fusion code - the design; today only the executable mode
exists, as `python main.py program.fusion`.

* **Script Mode**: Interpreted execution
     * Run directly without compilation
     * Fast development iteration
     * Slower execution
     * Like Python

```
fusion run game.fusion
```

* **Executable Mode**: Native compilation
     * Compile to standalone executable
     * Fast execution
     * Platform-specific binary
     * Like C/Java compiled

```
fusion build game.fusion --output game.exe
```

* **Library Mode**: Shared library
     * Compile to DLL/shared library
     * Reusable across projects
     * Link at runtime or compile time
     * Platform-specific format

```
fusion build engine.fusion --lib --output engine.dll
```

* **JIT Mode**: Just-in-time compilation
     * Compiles during first run
     * Caches compiled code
     * Balance of flexibility and speed
     * Like Java/C#

---

### Project Configuration

**Built (Task 12.12, decided 2026-09-13; Task 31, 2026-10-28).** Every setting, its values and default:
[001 Project Settings](001-TomlSettings.md) - generated from `files/fusionSettings.xml`, so it is never
out of date; the authoritative schema and error messages: `src/config/project_config.py`.

**Why a settings file:**
- Fusion's core concept is per-project configurability (see [010 Philosophy](010-Philosophy.md))
- The compiler once hardcoded its indentation settings in the lexer, with no way to change them -
  a gap between the concept and the code; the settings file closes it

**Four formats (Task 31, built - user decisions 2026-10-28):**
- `fusion.toml` is the default; `fusion.yaml` (or `.yml`), `fusion.json` and `fusion.ini` are alternatives -
  for a company that standardises on YAML, or INI for legacy hardware and software
- All four give the same settings and are checked by the same rules
- Why TOML is the default (2026-09-13): YAML needed a new dependency, and a Fusion-only format would
  mean a whole new parser for no real benefit; Python 3.11's `tomllib` reads TOML with no dependency

**Rules:**
* **Names (Task 32.0):** camelCase (`tabWidth`, `maxCallDepth`), read ignoring case and `_` -
  `tab_width`, `tabWidth` and `TABWIDTH` are the same setting; one written twice is an error
* **The master template:** `files/fusionSettings.xml` lists every setting, the values it can
  have, its default and what it does. It is read only; a project's settings file carries its
  choices, based on it
* **Finding the file:** next to the source file, then in the current folder; in a folder the
  first of TOML, YAML, JSON, INI is used
  - Not a parent-folder walk like git's `.git` or npm's `package.json` - revisit once Fusion has
    multi-folder projects
* **No settings file at all:** not an error - every setting has its default; the compiler writes a
  new `fusion.toml` from the template, every setting at its default, each with a comment
  (`--no-new-config`, or `FUSION_NO_NEW_CONFIG=1`, turns that off for build scripts)
* **A broken file is an error:** bad syntax, or a known setting with a wrong value - never a silent
  fall-back to defaults, so a typo doesn't compile with other settings than intended; an unknown
  setting is an error too
* **Changing format:** `[project] fusionSettingFormat = "TOML"` (TOML / YAML / JSON / INI).
  Set it to another format and the next compile writes the settings in that format (with
  the template's comments) and keeps the old file as a backup (`fusion.toml.bak`) - only one
  settings file is active. Your own comments live on in the backup
* **INI** holds only text: `true` / `false` (nothing else) become true / false, whole numbers
  become numbers, `"quoted"` or bare text stays text. **YAML** reads a bare `no` / `off` as
  false (the "Norway problem") - quote text values; a wrong type is reported
* **Reading:** Python's own readers for TOML, JSON and INI, PyYAML for YAML (`safe_load` -
  never runs code from the file; needed only by a YAML project). Fusion's own readers - also
  for XML and CSV, and recovering from small mistakes - come with its data-formats module
  (files/FEATURES.md 43.2); a dedicated `config.fusion` program will create settings files
* **Parsed, not enforced yet:** `[safety]` and `[backend]` are read and checked (a project can state
  its intent and catch typos) but not acted on (31.5)

```toml
# fusion.toml - a few settings; everything else keeps its default (the full list: 001)
[indentation]
tabWidth = 4               # spaces per tab

[memory]
assignment = "move"        # "share": two names on one object

[safety]
mode = "safe"              # "strict": every warning an error
```

---

### Build Commands

Description: Command-line build options.

```
// Run as script
fusion run game.fusion

// Compile to executable (debug)
fusion build game.fusion --debug --output game-debug.exe

// Compile to executable (release - optimized)
fusion build game.fusion --release --optimize --output game.exe

// Compile to library
fusion build engine.fusion --lib --release --output engine.dll

// Cross-compile for different platforms
fusion build game.fusion --target linux-x64 --output game-linux
fusion build game.fusion --target windows-x64 --output game.exe
fusion build game.fusion --target wasm --output game.wasm

// Compile with specific optimizations
fusion build game.fusion --optimize speed --output game-fast.exe
fusion build game.fusion --optimize size --output game-small.exe
```

---

### Build Configurations

Description: Common build scenarios.

**Development Build**

* Quick compilation
* Debug symbols included
* No optimizations
* Runtime checks enabled

```
fusion build game.fusion --debug --output game-dev.exe
```

**Release Build**

* Full optimizations
* No debug symbols
* Smaller binary
* Runtime checks disabled

```
fusion build game.fusion --release --optimize --output game.exe
```

**Library Build**

* Creates shared library
* Can be imported by other projects
* Platform-specific format

```
fusion build SpaceshipEngine.fusion --lib --release --output SpaceshipEngine.dll
```

---

### Output Targets

Description: Platform-specific compilation.

Platform | Target | Output Format
---|---|---
Windows | windows-x64 | .exe / .dll
Linux | linux-x64 | (binary) / .so
macOS | macos-arm64 | (binary) / .dylib
Web | wasm | .wasm

---

### Using Libraries

Description: Import compiled libraries in projects.

```
// Link against compiled library
fusion build game.fusion --link engine.dll --output game.exe

// In code
import SpaceshipEngine
Spaceship ship = SpaceshipEngine.createShip("Enterprise")
```

[< 160 GameExample](160-GameExample.md) | [Index](index.md) | [180 StandardLibrary >](180-StandardLibrary.md) <!-- nav -->
