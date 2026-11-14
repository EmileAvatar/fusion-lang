[< 015 WebServers](015-WebServers.md) | [Index](index.md) | [030 LibraryLayout >](030-LibraryLayout.md) <!-- nav -->

# 020 Settings

**Status:** partly built - the four settings formats are built (Task 31, [170 Build](../spec/170-Build.md)); every setting: [001](../spec/001-TomlSettings.md); the rest idea

**Contents**

- [Settings System - Module Placement](#settings-system---module-placement)
- [2.1 Compiler & Build Settings `fusionlib.IDE` (New Module)](#21-compiler--build-settings-fusionlibide-new-module)
- [2.2 Project Configuration `fusionlib.IDE` (New Module)](#22-project-configuration-fusionlibide-new-module)
- [2.3 User App Configuration (Runtime) `fusionlib.Data` (Existing Module)](#23-user-app-configuration-runtime-fusionlibdata-existing-module)
- [2.4 IDE Preferences `fusionlib.IDE` (New Module)](#24-ide-preferences-fusionlibide-new-module)
- [Configuration File Formats](#configuration-file-formats)
- [Project Configuration (project.json)](#project-configuration-projectjson)
- [User Preferences (~/.fusion/preferences.json)](#user-preferences-fusionpreferencesjson)

## Settings System - Module Placement

**Issue:** Where should compiler/build/runtime settings live?

**Solution:** Consolidate ALL settings into fusionlib.IDE module

**Rationale:**
- Settings only needed at **compile-time/development**, NOT at runtime
- Cleaner separation: Runtime code doesn't need compiler settings
- IDE module handles all developer tooling (LSP, formatter, settings)
- Simpler architecture: One module for all dev tools

---

### 2.1 Compiler & Build Settings `fusionlib.IDE` (New Module)

**Rationale:**
- Compiler settings only used during compilation (development-time)
- IDE needs settings to know how to build/run code
- No need to pollute System module with dev-only features
- Runtime executables don't include IDE module (smaller binaries)

**API:**
```fusion
import fusionlib.IDE

// ===== Compiler Settings =====
class CompilerSettings
    // Target platform
    static Platform getTargetPlatform()
    // Returns: Platform.Native | Platform.Script | Platform.Bytecode | Platform.WebAssembly

    static void setTargetPlatform(Platform platform)

    // Optimization level
    static int getOptimizationLevel()
    // Returns: 0 (none), 1 (basic), 2 (aggressive), 3 (maximum)

    static void setOptimizationLevel(int level)

    // Safety mode
    static SafetyMode getSafetyMode()
    // Returns: SafetyMode.Standard | SafetyMode.Strict | SafetyMode.Unsafe

    static void setSafetyMode(SafetyMode mode)

// ===== Build Configuration =====
class BuildConfig
    // Load project configuration
    static ProjectConfig loadProjectConfig(string path)

    // Build mode
    static BuildMode getBuildMode()
    // Returns: BuildMode.Debug | BuildMode.Release

    static void setBuildMode(BuildMode mode)

    // Output settings
    static string getOutputPath()
    static void setOutputPath(string path)

    // Dependencies
    static List<Dependency> getDependencies()

// ===== Enumerations =====
Enum Platform
    Native       // Compile to native executable (.exe, .elf)
    Script       // Run as interpreted script
    Bytecode     // Compile to bytecode (like JVM)
    WebAssembly  // Compile to .wasm

Enum SafetyMode
    Standard     // Balanced safety and flexibility
    Strict       // Maximum safety, restricted features
    Unsafe       // Allow raw pointers, manual memory

Enum BuildMode
    Debug        // Debugging symbols, no optimization
    Release      // Optimized, stripped binaries
```

**Example Usage:**
```fusion
import fusionlib.IDE

void function main()
    // Check how the app was compiled (only available in dev builds)
    Platform platform = CompilerSettings.getTargetPlatform()

    if platform == Platform.Native
        print("Running as native executable")
    else if platform == Platform.Script
        print("Running as interpreted script")

    // Check build mode
    BuildMode mode = BuildConfig.getBuildMode()
    if mode == BuildMode.Debug
        print("DEBUG: Extra logging enabled")
```

---

### 2.2 Project Configuration `fusionlib.IDE` (New Module)

**Rationale:**
- Project settings (project.json) only used during compilation
- IDE needs to read project config to build correctly
- Not needed in runtime executables

**API:**
```fusion
import fusionlib.IDE

// ===== Project Configuration =====
class ProjectConfig
    // Read project.json
    static ProjectConfig load(string path)

    // Project metadata
    string getName()
    string getVersion()

    // Build settings
    Platform getTarget()
    SafetyMode getSafetyMode()
    int getOptimization()
    BuildMode getBuildMode()
    string getOutputPath()

    // Dependencies
    List<string> getDependencies()

    // Custom settings
    string getValue(string key)
    bool hasKey(string key)
```

**Example project.json:**
```json
{
  "name": "MyFusionApp",
  "version": "1.0.0",
  "target": "native",
  "safetyMode": "standard",
  "optimization": 2,
  "buildMode": "release",
  "output": "./build/myapp.exe",
  "dependencies": [
    "fusionlib.Core",
    "fusionlib.Collections"
  ]
}
```

---

### 2.3 User App Configuration (Runtime) `fusionlib.Data` (Existing Module)

**Rationale:**
- User apps need to read config files at RUNTIME (not compile-time)
- fusionlib.Data already handles JSON, CSV, XML, YAML, INI parsing
- This is runtime data parsing, not compiler settings
- Example: Game reads graphics settings at startup

**Note:** fusionlib.Data already exists and handles this! No new API needed.

**Existing API:**
```fusion
import fusionlib.Data

void function main()
    // Parse JSON at runtime (fusionlib.Data already does this)
    string json = File.readAllText("settings.json")
    JSON.Object settings = JSON.parse(json)

    int width = settings.getInt("graphics.width")
    int height = settings.getInt("graphics.height")
```

**Decision:** Use existing fusionlib.Data module for runtime config parsing. No need for new Config API.

---

### 2.4 IDE Preferences `fusionlib.IDE` (New Module)

**Rationale:**
- IDE preferences (preferred block style, indent size) are development-time
- Stored in ~/.fusion/preferences.json
- Not needed in compiled executables

**API:** (Already documented in section 1.2 above)

---


## Configuration File Formats

### Project Configuration (project.json)
```json
{
  "name": "MyFusionApp",
  "version": "1.0.0",
  "target": "native",
  "safetyMode": "standard",
  "optimization": 2,
  "buildMode": "release",
  "output": "./build/myapp.exe",
  "dependencies": [
    "fusionlib.Core",
    "fusionlib.Collections",
    "fusionlib.IO"
  ]
}
```

### User Preferences (~/.fusion/preferences.json)
```json
{
  "editor": {
    "blockStyle": "indentation",
    "indentSize": 4,
    "tabsOrSpaces": "spaces"
  },
  "compiler": {
    "defaultTarget": "native",
    "defaultOptimization": 1
  },
  "ide": {
    "enableLSP": true,
    "lspPort": 9257,
    "showInlayHints": true
  }
}
```

[< 015 WebServers](015-WebServers.md) | [Index](index.md) | [030 LibraryLayout >](030-LibraryLayout.md) <!-- nav -->
