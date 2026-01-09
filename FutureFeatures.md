# 🔮 Fusion Language - Future Features & Enhancements

**Status:** Planning / Not Yet Implemented
**Last Updated:** 2025-11-03
**Purpose:** Track proposed features and enhancements for post-MVP implementation

---

## 📋 Overview

This document tracks features that are **not part of the MVP (Minimum Viable Product)** but are planned for future versions of Fusion. These features have been discussed and documented here to ensure they're not forgotten during development.

**Current MVP Status:** Building basic compiler (Lexer → Parser → Semantic → CodeGen)

---

## 🆕 Proposed New Modules

### 1. fusionlib.IDE - IDE Integration Module (22nd Module)

**Status:** 📝 Proposed
**Priority:** High (needed for developer experience)
**Depends On:** Basic compiler completion

**Purpose:** Enable IDEs and text editors to understand and work with Fusion code

---

#### 1.1 IDE Integration Components

##### Language Server Protocol (LSP)
**What:** Standard protocol for IDE language features
**Provides:**
- Auto-completion
- Go-to-definition
- Find references
- Hover documentation
- Error diagnostics in real-time

**Example:**
```fusion
// User types: ship.
// IDE shows: .move(), .stop(), .getSpeed()
```

---

##### Syntax Highlighting Definitions
**What:** Color schemes for Fusion code in various editors
**Supports:**
- VS Code (TextMate grammar)
- IntelliJ IDEA / PyCharm (XML definitions)
- Sublime Text (tmLanguage)
- Vim / Neovim (syntax files)
- Emacs (major mode)
- Atom (CSON grammar)

**Example:** Keywords blue, strings green, comments gray, etc.

---

##### Code Formatter
**What:** Convert between the three block styles
**Features:**
- Convert indentation → braces
- Convert braces → End keywords
- Convert End keywords → indentation
- Preserve code semantics
- User-configurable indent size (2/4/8 spaces)

**Example API:**
```fusion
import fusionlib.IDE

string code = """
if condition
    doSomething()
"""

// Convert to braces
string bracesCode = Formatter.convertToBraces(code)
// Result:
// if condition {
//     doSomething()
// }

// Convert to End keywords
string endCode = Formatter.convertToEndKeywords(code)
// Result:
// if condition
//     doSomething()
// End if
```

---

##### Editor Integration
**What:** Official plugins for major IDEs
**Planned Integrations:**
- **VS Code Extension** (highest priority)
  - Syntax highlighting
  - LSP integration
  - Debugger support
  - Build tasks
- **IntelliJ IDEA Plugin**
  - Full language support
  - Refactoring tools
  - Code inspections
- **Sublime Text Package**
  - Syntax highlighting
  - Build system integration
- **Vim Plugin**
  - Syntax highlighting
  - LSP integration via coc.nvim
- **Emacs Mode**
  - Major mode for Fusion
  - LSP integration via lsp-mode

---

##### User Preference Manager
**What:** Store and retrieve user's preferred code style
**Settings:**
```fusion
import fusionlib.IDE

// Get user's preferred block style
BlockStyle style = UserPreferences.getPreferredBlockStyle()
// Returns: BlockStyle.Indentation | BlockStyle.Braces | BlockStyle.EndKeywords

// Set preferred style
UserPreferences.setPreferredBlockStyle(BlockStyle.Braces)

// Get indent size
int spaces = UserPreferences.getIndentSize()
// Returns: 2, 4, or 8

// Save preferences
UserPreferences.save()
```

**Storage Location:**
- `~/.fusion/preferences.json` (user-wide)
- `.fusion/settings.json` (project-specific)

---

#### 1.2 IDE Module API Reference

```fusion
// Module: fusionlib.IDE

// ===== Syntax Highlighting =====
class SyntaxHighlighter
    static string generateVSCodeGrammar()
    static string generateIntelliJGrammar()
    static string generateSublimeGrammar()
    static string generateVimSyntax()

// ===== Language Server =====
class LanguageServer
    void start(int port = 9257)
    void stop()
    void handleRequest(LSPRequest request)

    // Features
    List<CompletionItem> getCompletions(Position pos)
    Location getDefinition(Position pos)
    List<Location> getReferences(Position pos)
    Hover getHover(Position pos)

// ===== Code Formatter =====
class Formatter
    static string convertToIndentation(string code)
    static string convertToBraces(string code)
    static string convertToEndKeywords(string code)
    static string format(string code, FormatOptions options)

// ===== Editor Integration =====
class EditorIntegration
    static bool installVSCodeExtension()
    static bool installIntelliJPlugin()
    static bool installSublimePackage()
    static string getExtensionPath(Editor editor)

// ===== User Preferences =====
Enum BlockStyle { Indentation, Braces, EndKeywords }

class UserPreferences
    static BlockStyle getPreferredBlockStyle()
    static void setPreferredBlockStyle(BlockStyle style)
    static int getIndentSize()
    static void setIndentSize(int spaces)
    static void load()
    static void save()
    static void reset()
```

---

## ⚙️ Settings System - Module Placement

**Issue:** Where should compiler/build/runtime settings live?

**Solution:** Consolidate ALL settings into fusionlib.IDE module

**Rationale:**
- Settings only needed at **compile-time/development**, NOT at runtime
- Cleaner separation: Runtime code doesn't need compiler settings
- IDE module handles all developer tooling (LSP, formatter, settings)
- Simpler architecture: One module for all dev tools

---

### 2.1 Compiler & Build Settings → `fusionlib.IDE` (New Module)

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

### 2.2 Project Configuration → `fusionlib.IDE` (New Module)

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

### 2.3 User App Configuration (Runtime) → `fusionlib.Data` (Existing Module)

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

### 2.4 IDE Preferences → `fusionlib.IDE` (New Module)

**Rationale:**
- IDE preferences (preferred block style, indent size) are development-time
- Stored in ~/.fusion/preferences.json
- Not needed in compiled executables

**API:** (Already documented in section 1.2 above)

---

## 📊 Updated Module Count

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

## 🗂️ Updated Standard Library Organization

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

## 🎯 Implementation Priority

### Phase 1: Basic Compiler (Current - MVP)
- ✅ Lexer
- ✅ Parser
- ✅ Semantic Analyzer
- ✅ Code Generator (C output)

### Phase 2: Core Enhancements (Post-MVP)
- Design fusionlib.IDE module architecture
- Define project.json schema
- Plan Language Server Protocol implementation

### Phase 3: IDE Integration (High Priority)
- Build fusionlib.IDE module
- Implement Language Server Protocol
- Create VS Code extension (highest priority)
- Generate syntax highlighting files

### Phase 4: Additional IDE Support
- IntelliJ IDEA plugin
- Sublime Text package
- Vim plugin
- Code formatter tool

---

## 📦 Complete fusionlib.IDE Module API

**Summary:** All APIs consolidated into one module

```fusion
// Module: fusionlib.IDE
// Purpose: All development/compile-time tooling and settings

// ===== Compiler Settings =====
class CompilerSettings
    static Platform getTargetPlatform()
    static void setTargetPlatform(Platform platform)
    static int getOptimizationLevel()
    static void setOptimizationLevel(int level)
    static SafetyMode getSafetyMode()
    static void setSafetyMode(SafetyMode mode)

// ===== Build Configuration =====
class BuildConfig
    static BuildMode getBuildMode()
    static void setBuildMode(BuildMode mode)
    static string getOutputPath()
    static void setOutputPath(string path)

// ===== Project Configuration =====
class ProjectConfig
    static ProjectConfig load(string path)
    string getName()
    string getVersion()
    Platform getTarget()
    SafetyMode getSafetyMode()
    int getOptimization()
    BuildMode getBuildMode()
    string getOutputPath()
    List<string> getDependencies()

// ===== User Preferences =====
class UserPreferences
    static BlockStyle getPreferredBlockStyle()
    static void setPreferredBlockStyle(BlockStyle style)
    static int getIndentSize()
    static void setIndentSize(int spaces)
    static void load()
    static void save()

// ===== Language Server Protocol =====
class LanguageServer
    void start(int port = 9257)
    void stop()
    List<CompletionItem> getCompletions(Position pos)
    Location getDefinition(Position pos)
    List<Location> getReferences(Position pos)
    Hover getHover(Position pos)

// ===== Syntax Highlighting =====
class SyntaxHighlighter
    static string generateVSCodeGrammar()
    static string generateIntelliJGrammar()
    static string generateSublimeGrammar()
    static string generateVimSyntax()

// ===== Code Formatter =====
class Formatter
    static string convertToIndentation(string code)
    static string convertToBraces(string code)
    static string convertToEndKeywords(string code)
    static string format(string code, FormatOptions options)

// ===== Editor Integration =====
class EditorIntegration
    static bool installVSCodeExtension()
    static bool installIntelliJPlugin()
    static bool installSublimePackage()
    static string getExtensionPath(Editor editor)

// ===== Enumerations =====
Enum Platform { Native, Script, Bytecode, WebAssembly }
Enum SafetyMode { Standard, Strict, Unsafe }
Enum BuildMode { Debug, Release }
Enum BlockStyle { Indentation, Braces, EndKeywords }
```

**Key Point:** This is ONE module with ALL development tooling. Runtime code never imports this.

---

## 📝 Configuration File Formats

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

---

## 🔗 Related Files

When implementing these features, update:
1. **fusion-language-spec.md** - Add fusionlib.IDE module documentation
2. **fusion-summary.md** - Update module count to 22
3. **CLAUDE.md** - Update standard library table
4. **fusion_specs.md** - Add API specifications for new features
5. **README.md** - Mention IDE integration support

---

## ✅ Implementation Checklist

### fusionlib.IDE Module
- [ ] Design module architecture (all components)
- [ ] Implement CompilerSettings API
- [ ] Implement BuildConfig API
- [ ] Implement ProjectConfig API (read project.json)
- [ ] Implement UserPreferences API
- [ ] Design Language Server Protocol implementation
- [ ] Create VS Code extension skeleton
- [ ] Implement syntax highlighter generators
- [ ] Build code formatter (indentation ↔ braces ↔ End)
- [ ] Define project.json schema
- [ ] Define preferences.json schema
- [ ] Update compiler to use IDE module for settings
- [ ] Write comprehensive tests
- [ ] Document all APIs

### Documentation
- [ ] Update fusion-language-spec.md (add IDE module)
- [ ] Update fusion-summary.md (22 modules)
- [ ] Update CLAUDE.md (library table)
- [ ] Update fusion_specs.md (new APIs)
- [ ] Create IDE integration guide
- [ ] Write user preference documentation

---

## 💡 Additional Ideas (Lower Priority)

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

---

## 🌍 Cross-Language Compilation Support

**Status:** 📝 Proposed (Post-MVP)
**Priority:** Medium (after working compiler is complete)
**Purpose:** Enable Fusion to compile and interoperate with code from other languages

### Overview

Fusion aims to support compilation of multiple programming languages through its `fusionlib.Lang` module. To achieve this, the Fusion parser needs to support various syntax conventions used by different languages.

### Semicolon Support

**Current State:** Fusion lexer does **not** tokenize semicolons (`;`). Statements are terminated by newlines or block boundaries.

**Proposed Enhancement:**
- Add semicolon tokenization to the lexer
- Make semicolons optional statement terminators (like Swift, JavaScript, Kotlin)
- Support both styles: newline-terminated AND semicolon-terminated statements
- Enable parsing of C/C++/Java-style code with semicolons

**Rationale:**
To compile C, C++, Java, C#, and other semicolon-based languages through `fusionlib.Lang`, the Fusion parser must understand semicolon syntax.

**Example:**
```fusion
// Current Fusion (newline-terminated)
int x = 5
int y = 10
return x + y

// Future Fusion (semicolon-terminated - optional)
int x = 5;
int y = 10;
return x + y;

// Mixed (both valid)
int x = 5;
int y = 10
return x + y;
```

### Cross-Language Parsing Support

**Languages to Support via fusionlib.Lang:**
1. **C** - Semicolons, preprocessor directives, pointer syntax
2. **C++** - Templates, namespaces, operator overloading
3. **Java** - Packages, interfaces, annotations
4. **C#** - Properties, LINQ, async/await
5. **Python** - Indentation-based (already supported), decorators
6. **JavaScript** - Prototypes, arrow functions, optional semicolons
7. **TypeScript** - Type annotations, interfaces
8. **Go** - Implicit semicolons, goroutines
9. **Rust** - Macros, lifetimes, ownership syntax
10. **VB.NET** - End keyword syntax (already supported)

### Implementation Strategy

**Phase 1: Lexer Enhancement**
- Add `TokenType.SEMICOLON` to token definitions
- Update lexer to recognize `;` as a delimiter
- Make semicolons optional (don't require them)

**Phase 2: Parser Enhancement**
- Update `consume_statement_terminator()` to accept semicolons OR newlines
- Ensure backward compatibility (existing Fusion code still works)
- Add tests for semicolon-terminated statements

**Phase 3: Language-Specific Parsers**
- Create specialized parsers for each target language
- Implement in `fusionlib.Lang` module
- Convert foreign language AST → Fusion AST → C code

**Phase 4: Syntax Extension System**
- Plugin architecture for custom syntax
- Allow community-contributed language parsers
- Standard API for AST conversion

### Benefits

1. **Multi-language compilation** - Compile any language through Fusion
2. **Developer flexibility** - Use semicolons or not, developer's choice
3. **IDE support** - Better interoperability with existing tools
4. **Migration path** - Easier to migrate C/Java code to Fusion
5. **Ecosystem growth** - Support for more languages = larger community

### Timeline

- **Phase 1 (Semicolon Support):** 1-2 weeks (after MVP compiler complete)
- **Phase 2 (Parser Updates):** 1 week
- **Phase 3 (Language Parsers):** 6-12 months (incremental per language)
- **Phase 4 (Plugin System):** 2-3 months

### Dependencies

- ✅ Basic compiler must be complete (Milestone 4)
- ✅ Parser must be fully functional
- ⚪ fusionlib.Lang module must be implemented
- ⚪ AST must be stable and well-documented

### Success Criteria

- [ ] Fusion code works with or without semicolons
- [ ] Can parse valid C code and compile to executable
- [ ] Can parse valid Java code and compile to executable
- [ ] Can parse valid Python code and compile to executable
- [ ] Backward compatibility: All existing Fusion code still works
- [ ] Comprehensive test suite for each supported language
- [ ] Documentation for cross-language compilation

### Notes

- This feature is **not part of MVP** - implement after basic compiler works
- Semicolons remain **optional** in Fusion - they're for compatibility
- Fusion's native style (newline-terminated) is still recommended
- Cross-language support enables Fusion to become a universal compiler frontend

---

## 🚀 Future Self-Hosting Considerations

When the compiler is rewritten in Fusion (self-hosting), these modules become critical:

**Why fusionlib.IDE matters for self-hosting:**
1. Compiler developers need IDE support to write compiler in Fusion
2. Language Server needed for auto-completion while coding compiler
3. Syntax highlighting makes compiler code easier to read
4. Formatter helps maintain consistent code style

**Why Settings matter for self-hosting:**
1. Compiler needs to read its own build configuration
2. CompilerSettings used internally by compiler
3. Self-compilation requires understanding target platform

---

## 📅 Timeline Estimate

| Feature | Estimated Effort | Depends On |
|---------|------------------|------------|
| Config API (Core) | 1 week | Basic compiler complete |
| CompilerSettings (System) | 1 week | Config API |
| Language Server Protocol | 3-4 weeks | Basic compiler complete |
| VS Code Extension | 2-3 weeks | LSP complete |
| Syntax Highlighters | 1 week | LSP complete |
| Code Formatter | 2 weeks | Parser complete |
| User Preferences | 1 week | Config API |
| IntelliJ Plugin | 3-4 weeks | LSP complete |
| **Total** | **14-17 weeks** | Parallel work possible |

---

## 🎯 Success Criteria

### fusionlib.IDE Module Complete When:
- [ ] VS Code extension works (syntax highlighting, LSP)
- [ ] Can convert code between all 3 block styles
- [ ] Language Server provides auto-completion
- [ ] User preferences saved and loaded correctly
- [ ] Syntax highlighting available for 5+ editors
- [ ] Documentation complete
- [ ] All tests pass

### Settings System Complete When:
- [ ] project.json fully supported
- [ ] CompilerSettings API available at runtime
- [ ] User apps can read config files (JSON, INI, YAML)
- [ ] IDE can save/load user preferences
- [ ] All build targets work (native, script, bytecode)
- [ ] Documentation complete
- [ ] All tests pass

---

## 📞 Discussion Points

**To discuss later:**
1. Should fusionlib.IDE be included in compiled executables? (Probably not - dev-only)
2. Should Config API support custom formats? (Extensibility?)
3. Priority order: VS Code first or IntelliJ first? (VS Code more popular)
4. Should formatter be a CLI tool or library or both? (Both!)
5. LSP port number: 9257 or configurable? (Configurable with default)
6. Block style conversion: preserve comments? (Yes!)

---

## 🔤 Regex Fluent API

**Status:** 📝 Proposed
**Priority:** Medium (developer experience enhancement)
**Module:** `fusionlib.Core` (String utilities) OR new `fusionlib.Regex` module
**Depends On:** Basic compiler completion

**Purpose:** Provide human-readable, chainable methods for regex operations instead of cryptic regex symbols

---

### Overview

Traditional regex is difficult to read and maintain due to symbolic syntax (`\d+`, `[a-z]*`, etc.). The Regex Fluent API provides descriptive method names that clearly communicate intent.

**Traditional Regex:**
```fusion
string pattern = "^\d{3}-\d{4}$"  // What does this mean?
```

**Fluent API:**
```fusion
import fusionlib.Regex

Regex phonePattern = Regex.create()
    .regexStartWith()
    .regexFilterNumbers().regexRepeat(3, 3)
    .regexLiteral("-")
    .regexFilterNumbers().regexRepeat(4, 4)
    .regexEndWith()
// Clear: "Start with 3 digits, dash, 4 digits, end"
```

---

### Regex Pattern to Method Mapping

| Traditional Pattern | Meaning | What it Does | Fluent API Method |
|---------------------|---------|--------------|-------------------|
| `.` | Any single character | Matches **any one character** except newline | `.regexAnyChar()` |
| `\d` | Digit (0–9) | Matches **any single digit** | `.regexFilterNumbers()` or `.regexFilterNumbers(0,9)` |
| `\w` | Word character | Matches **letters, numbers, or underscore** | `.regexWord()` |
| `\s` | Whitespace | Matches **spaces, tabs, newlines** | `.regexWhiteSpace()` |
| `\S` | Non-whitespace | Matches **any non-whitespace character** | `.regexNonWhiteSpace()` |
| `^` | Start of string | Ensures match **starts at beginning** | `.regexStartWith()` or `.regexStartWith('pattern')` |
| `$` | End of string | Ensures match **ends at end** | `.regexEndWith()` or `.regexEndWith('pattern')` |
| `+` | One or more | Repeats **previous element one or more times** | `.regexRepeat(1, null)` or `.regexOneOrMore()` |
| `*` | Zero or more | Repeats **previous element zero or more times** | `.regexRepeat(0, null)` or `.regexZeroOrMore()` |
| `?` | Zero or one | Makes **previous element optional** | `.regexOptional()` |
| `{n}` | Exactly n times | Repeats **exactly n times** | `.regexRepeat(n, n)` |
| `{n,m}` | Between n and m | Repeats **between n and m times** | `.regexRepeat(n, m)` |
| `[abc]` | Character set | Matches **any character in brackets** | `.regexFilterCharacters('abc')` |
| `[^abc]` | Negated set | Matches **any character NOT in brackets** | `.regexNotCharacters('abc')` |
| `[a-z]` | Character range | Matches **any character in range** | `.regexRange('a', 'z')` |
| `(pattern)` | Capture group | Groups pattern to **extract or reuse** | `.regexExtractGroup('pattern')` |
| `(?:pattern)` | Non-capture group | Groups without capturing | `.regexGroup('pattern')` |
| `pattern1\|pattern2` | Alternation (OR) | Matches **either pattern** | `.regexOr('pattern1', 'pattern2')` |
| `\b` | Word boundary | Matches **boundary between word and non-word** | `.regexWordBoundary()` |
| `\B` | Non-word boundary | Matches **not at word boundary** | `.regexNonWordBoundary()` |
| `(?=pattern)` | Positive lookahead | Matches if **followed by pattern** | `.regexLookAhead('pattern')` |
| `(?!pattern)` | Negative lookahead | Matches if **NOT followed by pattern** | `.regexNegativeLookAhead('pattern')` |

---

### API Design (Option 1: Chainable Builder)

```fusion
import fusionlib.Regex

// Builder pattern - construct regex step by step
class Regex
    // Start new pattern
    static Regex create()

    // Character matching
    Regex regexAnyChar()
    Regex regexFilterNumbers(int min = 0, int max = 9)
    Regex regexWord()
    Regex regexWhiteSpace()
    Regex regexNonWhiteSpace()
    Regex regexLiteral(string text)

    // Character sets
    Regex regexFilterCharacters(string chars)
    Regex regexNotCharacters(string chars)
    Regex regexRange(char start, char end)

    // Quantifiers
    Regex regexRepeat(int min, int? max)  // null = unlimited
    Regex regexOneOrMore()
    Regex regexZeroOrMore()
    Regex regexOptional()

    // Anchors
    Regex regexStartWith(string? pattern = null)
    Regex regexEndWith(string? pattern = null)
    Regex regexWordBoundary()
    Regex regexNonWordBoundary()

    // Groups
    Regex regexExtractGroup(Regex pattern)
    Regex regexGroup(Regex pattern)
    Regex regexOr(Regex pattern1, Regex pattern2)

    // Lookahead
    Regex regexLookAhead(Regex pattern)
    Regex regexNegativeLookAhead(Regex pattern)

    // Execute
    bool matches(string input)
    List<string> findAll(string input)
    string replace(string input, string replacement)
    string toPattern()  // Get traditional regex string
```

---

### API Design (Option 2: Static Helpers)

```fusion
import fusionlib.Regex

class RegexHelper
    // Pre-built common patterns
    static string emailPattern()
    static string phonePattern()
    static string urlPattern()
    static string ipAddressPattern()

    // Quick matchers
    static bool isEmail(string input)
    static bool isPhone(string input)
    static bool isURL(string input)
    static bool isIPAddress(string input)

    // Validation helpers
    static bool hasNumbers(string input)
    static bool hasLetters(string input)
    static bool hasSpecialChars(string input)
    static bool isAlphanumeric(string input)

    // Extraction
    static List<string> extractEmails(string text)
    static List<string> extractURLs(string text)
    static List<string> extractPhones(string text)
    static List<string> extractNumbers(string text)
```

---

### Examples

**Example 1: Email Validation**
```fusion
import fusionlib.Regex

// Traditional regex (hard to read)
string emailRegex = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

// Fluent API (readable)
Regex emailPattern = Regex.create()
    .regexStartWith()
    .regexFilterCharacters("a-zA-Z0-9._%+-").regexOneOrMore()
    .regexLiteral("@")
    .regexFilterCharacters("a-zA-Z0-9.-").regexOneOrMore()
    .regexLiteral(".")
    .regexRange('a', 'z').regexRepeat(2, null)
    .regexEndWith()

bool isValid = emailPattern.matches("user@example.com")

// Or use helper
bool isValid2 = RegexHelper.isEmail("user@example.com")
```

**Example 2: Phone Number Extraction**
```fusion
import fusionlib.Regex

string text = "Call me at 555-1234 or 555-5678"

// Fluent API
Regex phonePattern = Regex.create()
    .regexFilterNumbers().regexRepeat(3, 3)
    .regexLiteral("-")
    .regexFilterNumbers().regexRepeat(4, 4)

List<string> phones = phonePattern.findAll(text)
// Result: ["555-1234", "555-5678"]

// Or use helper
List<string> phones2 = RegexHelper.extractPhones(text)
```

**Example 3: Replace with Validation**
```fusion
import fusionlib.Regex

string html = "<p>Hello</p><div>World</div>"

// Remove HTML tags
Regex tagPattern = Regex.create()
    .regexLiteral("<")
    .regexFilterCharacters("a-zA-Z/").regexOneOrMore()
    .regexLiteral(">")

string plainText = tagPattern.replace(html, "")
// Result: "HelloWorld"
```

**Example 4: Password Strength**
```fusion
import fusionlib.Regex

bool function isStrongPassword(string password)
    // Must have: 8+ chars, uppercase, lowercase, digit, special char
    bool hasLength = password.length >= 8
    bool hasUpper = RegexHelper.hasPattern(password, "[A-Z]")
    bool hasLower = RegexHelper.hasPattern(password, "[a-z]")
    bool hasDigit = RegexHelper.hasNumbers(password)
    bool hasSpecial = RegexHelper.hasSpecialChars(password)

    return hasLength and hasUpper and hasLower and hasDigit and hasSpecial
```

---

### Implementation Notes

**Key Design Decisions:**
1. **Chainable builder** (Option 1) for complex patterns
2. **Static helpers** (Option 2) for common use cases
3. **Hybrid approach** - provide both for flexibility
4. **Interoperability** - can convert to/from traditional regex strings
5. **Performance** - compiles to traditional regex internally (no performance loss)

**Compatibility:**
- Fluent API wraps traditional regex engine
- Can use `toPattern()` to get traditional regex string
- Can construct from traditional regex: `Regex.fromPattern("^\d+$")`

**Documentation:**
- All methods have clear descriptions
- Examples for common use cases
- Migration guide from traditional regex
- Performance considerations

---

### Open Questions

1. **Module placement:** Core module or separate Regex module?
   - **Recommendation:** Start in Core, move to separate module if it grows large

2. **Replace traditional regex literals?**
   - **Recommendation:** No - supplement, don't replace. Traditional regex still supported.

3. **Case-insensitive matching?**
   - **Recommendation:** Add `.regexCaseInsensitive()` flag method

4. **Unicode support?**
   - **Recommendation:** Add `.regexUnicode()` flag method

5. **Named capture groups?**
   - **Recommendation:** Add `.regexNamedGroup(string name, Regex pattern)`

---

## 📦 Multi-Import & Parameter Syntax

**Status:** 📝 Proposed
**Priority:** Medium (syntax enhancement)
**Impact:** Grammar changes to EBNF
**Depends On:** Basic compiler completion

**Purpose:** Support Go-style grouped imports and multi-line function parameters for better code organization

---

### Feature 1: Grouped Import Blocks

**Current Syntax:**
```fusion
import Fusion.Core
import Fusion.Collections
import Fusion.IO
import Fusion.Net
```

**Proposed Grouped Syntax (Go-style):**
```fusion
import (
    Fusion.Core
    Fusion.Collections
    Fusion.IO
    Fusion.Net
)
```

**Benefits:**
- Cleaner organization for multiple imports
- Clear visual grouping
- Less repetition of `import` keyword
- Standard in many modern languages (Go, Kotlin)

**Grammar Changes Required:**
```ebnf
import_statement = "import" ( single_import | grouped_import )
single_import = module_path
grouped_import = "(" newline { module_path newline } ")"
module_path = identifier { "." identifier }
```

---

### Feature 2: Multi-line Function Parameters

**Current Syntax (single-line):**
```fusion
int function createUser(string name, string surname, int age, Date birthDate)
```

**Proposed Multi-line Syntax:**
```fusion
// Stepped/formatted parameters
int function createUser(string name,      // first name
                        string surname,   // last name
                        int age,          // user age
                        Date birthDate)   // date of birth
```

**Benefits:**
- Better readability for functions with many parameters
- Inline documentation via comments
- IDE parameter hints enhanced
- Common in enterprise codebases

**Implementation Notes:**
- Comments are standard `//` comments (already supported)
- Compiler ignores comments, preserves formatting
- No grammar change needed - already valid syntax
- IDE formatter can auto-align parameters

---

### Feature 3: Mixed Import Styles

**Allow mixing single and grouped imports:**
```fusion
import Fusion.Core  // Single import

import (
    Fusion.Collections
    Fusion.IO
    Fusion.Net
)

import Fusion.Math  // Another single import
```

**Style Recommendation:**
- Use grouped imports for related modules
- Use single imports for one-off imports
- Keep grouped imports together

---

### Examples

**Example 1: Web Application Imports**
```fusion
// Before
import Fusion.Core
import Fusion.Collections
import Fusion.IO
import Fusion.Net
import Fusion.Web
import Fusion.Database
import Fusion.Crypto

// After (grouped)
import (
    Fusion.Core
    Fusion.Collections
    Fusion.IO
    Fusion.Net
    Fusion.Web
    Fusion.Database
    Fusion.Crypto
)
```

**Example 2: Categorized Imports**
```fusion
// Core modules
import (
    Fusion.Core
    Fusion.Collections
    Fusion.Math
)

// Network modules
import (
    Fusion.Net
    Fusion.Web
)

// Database modules
import (
    Fusion.Database
    Fusion.Crypto
)
```

**Example 3: Multi-line Function with Comments**
```fusion
import Fusion.Database

User function registerUser(
    string email,        // User's email address (must be valid)
    string password,     // Hashed password (min 8 chars)
    string firstName,    // First name
    string lastName,     // Last name
    int age,             // Age (must be 18+)
    Date registeredDate, // Registration timestamp
    bool isActive)       // Account active status

    // Function implementation
    User user = User(email, password, firstName, lastName)
    Database.save(user)
    return user
```

**Example 4: Complex Function Signature**
```fusion
import (
    Fusion.Collections
    Fusion.Database
)

List<Order> function searchOrders(
    int customerId,           // Customer ID to filter by
    Date startDate,           // Start of date range
    Date endDate,             // End of date range
    OrderStatus status,       // Order status filter
    int pageNumber = 1,       // Pagination: page number (default 1)
    int pageSize = 20,        // Pagination: items per page (default 20)
    bool includeArchived = false)  // Include archived orders (default false)

    // Implementation
    return Database.query()
        .where("customerId", customerId)
        .where("orderDate", ">=", startDate)
        .where("orderDate", "<=", endDate)
        .where("status", status)
        .paginate(pageNumber, pageSize)
        .toList()
```

---

### Implementation Details

**Grouped Imports:**
1. Update EBNF grammar for import statements
2. Lexer already handles parentheses and newlines
3. Parser modification to recognize grouped syntax
4. Validation: ensure no duplicate imports
5. Code generator: flatten to single imports in C code

**Multi-line Parameters:**
1. No grammar change needed (already valid)
2. Formatter tool can auto-align parameters (future IDE feature)
3. IDE can extract parameter comments for hints
4. Comments preserved in AST for documentation generation

**Compatibility:**
- Single-line imports still fully supported
- Mixed styles allowed
- No breaking changes to existing code

---

### Style Guide Recommendations

**When to use grouped imports:**
- 3+ imports from same namespace
- Related functional modules (all network, all database, etc.)
- Standard library modules vs third-party

**When to use multi-line parameters:**
- 4+ parameters
- Complex parameter types
- When parameter documentation is important
- Enterprise/team codebases

**Formatting:**
```fusion
// Good: aligned parameters
int function createOrder(
    int customerId,    // Customer ID
    int productId,     // Product ID
    int quantity)      // Order quantity

// Bad: misaligned
int function createOrder(
int customerId, // Customer ID
int productId,     // Product ID
    int quantity)  // Order quantity
```

---

### Clarification: Type Casing

**Question:** Is `String` vs `string` significant?

**Answer:**
- **`string`** = primitive type (value type)
- **`String`** = class object (reference type, for autoboxing)

**Similar to other languages:**
- Java: `int` (primitive) vs `Integer` (wrapper class)
- C#: `int` (primitive) vs `Int32` (struct)
- Fusion: `string` (primitive) vs `String` (class for advanced operations)

**Example:**
```fusion
string name = "Alice"  // Stack-allocated primitive
String name2 = String("Alice")  // Heap-allocated object with methods

// Autoboxing (implicit conversion)
string primitive = "test"
String object = primitive  // Auto-converts to String object
```

**Grammar Impact:**
- Both `string` and `String` are valid types
- Types ARE case-sensitive
- `string` ≠ `String` (different types, autoboxing allowed)

---

## 🛠️ CLI Tooling (Go-style Command Suite)

**Status:** 📝 Proposed
**Priority:** High (developer experience)
**Impact:** Compiler CLI interface
**Depends On:** Basic compiler completion

**Purpose:** Provide built-in command-line tools for common development tasks (inspired by Go's toolchain)

---

### Overview

Go's success partly comes from its **unified, consistent tooling**. Every Go developer uses the same commands (`go fmt`, `go test`, `go build`). Fusion should adopt this approach.

**Problems with fragmented tooling:**
- ❌ Different teams use different formatters
- ❌ Test frameworks vary by project
- ❌ Build systems are custom per project
- ❌ Documentation generation is inconsistent

**Solution: Built-in command suite**
- ✅ Standard tools included with compiler
- ✅ Consistent commands across all projects
- ✅ No configuration needed (works out of the box)
- ✅ Encourages best practices

---

### Proposed Commands

| Command | Purpose | Equivalent To |
|---------|---------|---------------|
| `fusion fmt` | Auto-format code | Go's `go fmt`, Rust's `rustfmt` |
| `fusion test` | Run unit tests | Go's `go test`, Cargo's `cargo test` |
| `fusion doc` | Generate/view docs | Go's `go doc`, Javadoc |
| `fusion build` | Compile program | Go's `go build`, `cargo build` |
| `fusion run` | Compile and run | Go's `go run`, `cargo run` |
| `fusion clean` | Remove build artifacts | `make clean`, `cargo clean` |
| `fusion vet` | Analyze code for bugs | Go's `go vet`, Clippy |
| `fusion check` | Syntax check (no compile) | Rust's `cargo check` |

---

### Command Specifications

#### 1. `fusion fmt` - Code Formatter

**Purpose:** Automatically format Fusion code according to style guide

**Features:**
- Convert between block styles (indentation ↔ braces ↔ End keywords)
- Fix indentation inconsistencies
- Align parameters and expressions
- Remove trailing whitespace
- Consistent spacing around operators

**Usage:**
```bash
# Format single file
fusion fmt main.fusion

# Format entire project
fusion fmt .

# Format specific directory
fusion fmt src/

# Check formatting (don't modify, exit code 1 if unformatted)
fusion fmt --check .

# Convert block style
fusion fmt --style=braces main.fusion  # Convert to braces
fusion fmt --style=indent main.fusion  # Convert to indentation
fusion fmt --style=end main.fusion     # Convert to End keywords

# Custom options
fusion fmt --indent=4 --tabs=false main.fusion
```

**Example:**
```bash
# Before: inconsistent formatting
int function add( int a,int b )
    return a+b

# After: fusion fmt main.fusion
int function add(int a, int b)
    return a + b
```

**Implementation:**
- Uses `fusionlib.IDE.Formatter` internally
- Reads user preferences from `~/.fusion/preferences.json`
- Can override with command-line flags

---

#### 2. `fusion test` - Test Runner

**Purpose:** Run unit tests using `fusionlib.Test` framework

**Features:**
- Auto-discover test files (`*_test.fusion`)
- Run all tests or specific tests
- Show pass/fail results
- Code coverage reports
- Benchmarking support

**Usage:**
```bash
# Run all tests in project
fusion test

# Run tests in specific package
fusion test ./src/utils

# Run specific test file
fusion test calculator_test.fusion

# Run with coverage report
fusion test --coverage

# Run benchmarks
fusion test --bench

# Verbose output
fusion test -v

# Run tests matching pattern
fusion test --run TestAdd
```

**Example:**
```bash
$ fusion test
Running tests...
✓ TestAdd (1ms)
✓ TestSubtract (1ms)
✗ TestDivide (2ms)
  Error: Division by zero not handled

PASS: 2/3 tests passed
FAIL: 1/3 tests failed
Coverage: 78%
```

**Implementation:**
- Uses `fusionlib.Test` module
- Test files must end with `_test.fusion`
- Test functions must start with `Test`

---

#### 3. `fusion doc` - Documentation Generator

**Purpose:** Generate and view documentation from code comments

**Features:**
- Extract doc comments from source code
- Generate HTML/Markdown documentation
- Search documentation
- View in terminal or browser

**Usage:**
```bash
# View documentation for symbol
fusion doc print
fusion doc List.add
fusion doc Fusion.Collections.List

# Generate HTML docs for project
fusion doc --generate --output=docs/

# Generate Markdown docs
fusion doc --generate --format=markdown --output=README_API.md

# Serve docs locally (opens browser)
fusion doc --serve
```

**Example:**
```bash
$ fusion doc List.add
List<T>.add(item: T) -> void
    Adds an item to the end of the list.

    Parameters:
        item - The item to add

    Example:
        List<int> numbers = List<int>()
        numbers.add(42)
```

**Implementation:**
- Uses `fusionlib.DocWiki` module
- Extracts doc comments (triple-slash `///` or `/**  */`)
- Generates searchable documentation

---

#### 4. `fusion build` - Compiler

**Purpose:** Compile Fusion code to executable

**Features:**
- Compile to native executable
- Cross-compilation support
- Optimization levels
- Debug/release builds

**Usage:**
```bash
# Build current project (uses project.json)
fusion build

# Build specific file
fusion build main.fusion

# Build with optimizations
fusion build --release

# Build for specific platform
fusion build --target=windows
fusion build --target=linux
fusion build --target=wasm

# Custom output path
fusion build --output=bin/myapp.exe

# Build with specific safety mode
fusion build --mode=strict
fusion build --mode=unsafe
```

**Example:**
```bash
$ fusion build --release
Compiling main.fusion...
Generating C code...
Invoking GCC...
✓ Build complete: ./bin/myapp.exe
```

**Implementation:**
- Uses compiler pipeline (Lexer → Parser → Semantic → CodeGen)
- Reads `project.json` for configuration
- Invokes GCC/Clang for final compilation

---

#### 5. `fusion run` - Compile and Execute

**Purpose:** Compile and run in one command (for quick testing)

**Features:**
- Compile to temporary executable
- Run immediately
- Pass arguments to program
- Clean up temp files

**Usage:**
```bash
# Run program
fusion run main.fusion

# Run with arguments
fusion run main.fusion --arg1 value1 --arg2 value2

# Run with optimizations
fusion run --release main.fusion
```

**Example:**
```bash
$ fusion run hello.fusion
Compiling...
Running...
Hello, Fusion!
```

**Implementation:**
- Compiles to temporary directory
- Executes binary
- Deletes temp files on exit

---

#### 6. `fusion clean` - Cleanup Build Artifacts

**Purpose:** Remove compiled binaries and temporary files

**Usage:**
```bash
# Clean current project
fusion clean

# Clean specific directory
fusion clean ./build
```

**Example:**
```bash
$ fusion clean
Removing build artifacts...
✓ Deleted ./bin/
✓ Deleted ./temp/
✓ Deleted ./obj/
```

---

#### 7. `fusion vet` - Code Analyzer

**Purpose:** Detect potential bugs and code smells

**Features:**
- Unused variables
- Unreachable code
- Type mismatches
- Null pointer risks
- Memory leaks

**Usage:**
```bash
# Analyze entire project
fusion vet

# Analyze specific file
fusion vet main.fusion

# Show warnings only
fusion vet --warn
```

**Example:**
```bash
$ fusion vet
main.fusion:10: Unused variable 'count'
main.fusion:25: Unreachable code after return
utils.fusion:42: Potential null pointer dereference

3 issues found.
```

**Implementation:**
- Uses semantic analyzer
- Static analysis rules
- Configurable via `.fusion/vet.json`

---

#### 8. `fusion check` - Syntax Check (No Compilation)

**Purpose:** Fast syntax validation without full compilation

**Usage:**
```bash
# Check syntax
fusion check main.fusion

# Check entire project
fusion check .
```

**Example:**
```bash
$ fusion check main.fusion
✓ Syntax OK

$ fusion check broken.fusion
✗ Syntax error at line 15:
  Expected 'End function', found EOF
```

**Implementation:**
- Lexer + Parser only (no semantic analysis or codegen)
- Fast feedback for IDEs and CI/CD

---

### Additional Commands (Lower Priority)

| Command | Purpose |
|---------|---------|
| `fusion init` | Create new Fusion project (generates project.json) |
| `fusion version` | Show compiler version |
| `fusion env` | Print Fusion environment info |
| `fusion install` | Install dependencies (if package manager added) |
| `fusion update` | Update dependencies |
| `fusion bench` | Run benchmarks |
| `fusion profile` | Profile application performance |
| `fusion fix` | Auto-fix common issues |

---

### Implementation Plan

**Phase 1: Core Commands (MVP)**
- [x] `fusion build` (already being built)
- [ ] `fusion run`
- [ ] `fusion check`
- [ ] `fusion clean`

**Phase 2: Developer Experience**
- [ ] `fusion fmt` (requires Formatter in fusionlib.IDE)
- [ ] `fusion test` (requires fusionlib.Test)
- [ ] `fusion doc` (requires fusionlib.DocWiki)

**Phase 3: Advanced Tooling**
- [ ] `fusion vet`
- [ ] `fusion init`
- [ ] `fusion version`
- [ ] `fusion env`

**Phase 4: Package Management (Future)**
- [ ] `fusion install`
- [ ] `fusion update`
- [ ] `fusion publish`

---

### CLI Architecture

**Main entry point:**
```bash
fusion <command> [arguments] [flags]
```

**Help system:**
```bash
fusion --help              # Show all commands
fusion build --help        # Show build command help
fusion fmt --help          # Show format command help
```

**Version:**
```bash
fusion --version
# Output: Fusion compiler version 1.0.0
```

**Environment:**
```bash
fusion env
# Output:
# FUSION_ROOT: /usr/local/fusion
# FUSION_PATH: /usr/local/fusion/lib
# FUSION_CACHE: ~/.fusion/cache
# Compiler: GCC 11.2
```

---

### Benefits of Unified CLI

**For Developers:**
- ✅ No need to learn different tools per project
- ✅ Consistent commands across all Fusion projects
- ✅ Works out of the box (no setup required)
- ✅ Faster onboarding for new team members

**For Projects:**
- ✅ Consistent code style (via `fusion fmt`)
- ✅ Reliable testing (via `fusion test`)
- ✅ Easy CI/CD integration
- ✅ Standard documentation

**For Language Adoption:**
- ✅ Better developer experience = more users
- ✅ Professional tooling = enterprise adoption
- ✅ Reduces ecosystem fragmentation

---

### Comparison with Other Languages

| Language | Formatter | Test Runner | Doc Generator | Build Tool |
|----------|-----------|-------------|---------------|------------|
| **Go** | `go fmt` | `go test` | `go doc` | `go build` |
| **Rust** | `rustfmt` | `cargo test` | `cargo doc` | `cargo build` |
| **Java** | External (Spotless) | External (JUnit) | `javadoc` | External (Maven/Gradle) |
| **Python** | External (black) | External (pytest) | External (Sphinx) | N/A (interpreted) |
| **C++** | External (clang-format) | External (Google Test) | External (Doxygen) | External (Make/CMake) |
| **Fusion** | `fusion fmt` ✅ | `fusion test` ✅ | `fusion doc` ✅ | `fusion build` ✅ |

**Fusion's advantage:** All tools built-in and consistent (like Go and Rust)

---

### Open Questions

1. **Should `fusion fmt` modify files in-place or output to stdout?**
   - **Recommendation:** In-place by default, `--stdout` flag for piping

2. **Should `fusion test` run tests in parallel?**
   - **Recommendation:** Yes, with `--parallel=N` flag (default: CPU cores)

3. **Should `fusion doc` generate static HTML or dynamic site?**
   - **Recommendation:** Static HTML (easy to host), optional `--serve` for local preview

4. **Should there be a package manager (`fusion install`)?**
   - **Recommendation:** Yes, but post-MVP. Use Git submodules initially.

5. **Should `fusion build` use project.json or command-line flags?**
   - **Recommendation:** Both. project.json for defaults, CLI flags override.

---

## 💬 Enhanced Comment Support

**Status:** 📝 Proposed
**Priority:** Medium (syntax enhancement)
**Impact:** Lexer modifications, grammar changes
**Depends On:** Basic compiler completion

**Purpose:** Re-enable `'` single-line comments and add `'''` multi-line comment blocks (Python-style)

---

### Current Comment Support (MVP)

**Supported:**
- `//` - C-style single-line comments
- `/* */` - C-style multi-line comments

**Disabled:**
- `'` - VB-style single-line comments (conflicts with character literals `'c'`)

---

### Feature 1: Re-enable `'` Comments (Line-Start Only)

**Problem:** `'` currently disabled because it conflicts with character literals like `'x'`, `'\n'`, `'\t'`

**Solution:** Only treat `'` as comment start if:
1. It appears at the **start of a line** (optionally after whitespace/tabs)
2. It is NOT followed by another `'` (to avoid `'''` confusion)
3. It is NOT a character literal context

**Grammar Rule:**
```
' is a comment IF:
  - Line starts with: [whitespace/tabs]* '
  - NOT followed by another ' (e.g., not ''')
```

**Examples:**
```fusion
int x = 5
' This is a valid comment (line starts with ')

    ' This is also valid (line starts with whitespace then ')

int y = 'c'  ' ERROR: ' mid-line is NOT a comment (would be treated as char literal + syntax error)

char a = 'x'  // Correct: use // for inline comments
```

**Implementation:**
- Modify `is_comment_start()` in `src/lexer/comments.py`
- Add parameter `at_line_start: bool` to track position
- Only return True for `'` if at_line_start AND next char != `'`

**Rationale:**
- VB.NET developers expect `'` for line comments
- Clear rule: `'` at line start = comment, `'` elsewhere = char literal
- No ambiguity with proper grammar

---

### Feature 2: Triple-Quote Comment Blocks `'''`

**Purpose:** Python-style multi-line comments using `'''`

**Syntax:**
```fusion
'''
This is a multi-line comment block
It can span multiple lines
Similar to Python docstrings
'''

int function add(int a, int b)
    '''
    Adds two numbers
    Returns: sum of a and b
    '''
    return a + b
```

**Grammar:**
```
multi_line_comment_block = "'''" { any_character } "'''"
```

**Features:**
- Starts with `'''` (three single quotes)
- Ends with `'''`
- Can span multiple lines
- Can be indented
- Cannot be nested (first `'''` closes the block)

**Use Cases:**
1. **Documentation blocks** (like Python docstrings)
2. **Commenting out large code sections** (easier than `/* */` for some devs)
3. **Multi-line string literals** (future: may support this)

**Examples:**
```fusion
'''
File: calculator.fusion
Author: Alice
Purpose: Basic arithmetic operations
'''

import Fusion.Math

'''
Function: multiply
Parameters:
  - a: first number
  - b: second number
Returns: product of a and b
'''
int function multiply(int a, int b)
    return a * b
```

**Implementation:**
- Add `skip_triple_quote_comment()` to `src/lexer/comments.py`
- Check for `'''` before checking for `'` single-line comment
- Track line count for proper error location reporting

---

### Feature 2a: Language-Specific Syntax Highlighting in `'''` Blocks

**Status:** 📝 Proposed (Post-Compiler)
**Priority:** Low (IDE enhancement)
**Depends On:** Working compiler + IDE module + Language Server Protocol (LSP)

**Purpose:** Allow `'''` comment blocks to specify a language for syntax highlighting in IDEs and documentation viewers.

**Syntax:**
```fusion
'''language_name
code or text here with syntax highlighting
'''
```

**Supported Languages:**
- `fusion` - Fusion language syntax
- `python` - Python syntax
- `javascript` / `js` - JavaScript syntax
- `typescript` / `ts` - TypeScript syntax
- `csharp` / `cs` - C# syntax
- `java` - Java syntax
- `cpp` / `c++` - C++ syntax
- `c` - C syntax
- `rust` - Rust syntax
- `go` - Go syntax
- `sql` - SQL syntax
- `json` - JSON syntax
- `xml` - XML syntax
- `html` - HTML syntax
- `css` - CSS syntax
- `bash` / `shell` - Shell script syntax
- `markdown` / `md` - Markdown syntax
- And any other language supported by the IDE's syntax highlighter

**Examples:**

**Example 1: Fusion Code in Comments**
```fusion
'''fusion
// Example of Fusion code in documentation
int function add(int a, int b)
    return a + b
'''

int function multiply(int a, int b)
    '''fusion
    This could also be written as:
    int multiply(int a, int b) : a * b
    '''
    return a * b
```

**Example 2: Python Comparison**
```fusion
'''
This Fusion function is equivalent to the following Python code:
'''

'''python
def add(a, b):
    return a + b
'''

int function add(int a, int b)
    return a + b
```

**Example 3: SQL in Documentation**
```fusion
class UserRepository
    '''
    Executes the following SQL query:
    '''

    '''sql
    SELECT id, name, email
    FROM users
    WHERE active = 1
    ORDER BY name
    '''

    List<User> function getActiveUsers()
        // Implementation here
```

**Example 4: JSON Configuration Example**
```fusion
'''
Configuration file format (config.json):
'''

'''json
{
    "app": {
        "name": "MyApp",
        "version": "1.0.0",
        "debug": true
    }
}
'''
```

**Grammar:**
```ebnf
triple_quote_comment = "'''" [language_identifier] { character | newline } "'''"

language_identifier = letter { letter | digit | "_" | "-" }
  (* Optional language name on same line as opening ''' *)
```

**Parsing Rules:**
1. If `'''` is followed by text on the same line → treat as language identifier
2. Language identifier must be alphanumeric + `_` + `-` (no spaces)
3. Language identifier ends at newline
4. If no language specified → plain comment (no syntax highlighting)
5. Unknown language names → treat as plain comment (no error)

**IDE Integration:**

**For IDEs (VS Code, IntelliJ, Sublime, Vim):**
- Parse `'''language` directive
- Apply syntax highlighting for specified language within comment block
- Show in documentation preview with proper formatting
- Language Server Protocol (LSP) provides language hints

**For Documentation Generators (fusionlib.DocWiki):**
- Convert `'''language` blocks to properly formatted code blocks
- Generate syntax-highlighted HTML/Markdown
- Support light/dark themes

**Implementation Notes:**

**Lexer Changes:**
```python
# In src/lexer/comments.py

def skip_triple_quote_comment(text: str, position: int) -> Tuple[int, int, Optional[str]]:
    """Skip a triple-quote comment block with optional language hint.

    Returns:
        Tuple of (new_position, lines_consumed, language_hint)
        language_hint is None if no language specified
    """
    pos = position

    # Must start with '''
    if pos + 2 >= len(text) or text[pos:pos + 3] != "'''":
        return position, 0, None

    pos += 3  # Skip '''

    # Check for language identifier on same line
    language_hint = None
    line_start = pos
    while pos < len(text) and text[pos] not in ['\n', '\r']:
        pos += 1

    lang_text = text[line_start:pos].strip()
    if lang_text and lang_text.replace('_', '').replace('-', '').isalnum():
        language_hint = lang_text.lower()

    # Continue to closing '''
    # ... (rest of implementation)

    return new_pos, lines_consumed, language_hint
```

**Token Changes:**
```python
# In src/lexer/token.py

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    location: SourceLocation
    language_hint: Optional[str] = None  # For '''language blocks
```

**LSP (Language Server Protocol) Integration:**
- Provide `textDocument/semanticTokens` with language hints
- IDEs query LSP for syntax highlighting within `'''language` blocks
- LSP returns token ranges with language identifiers

**Use Cases:**

1. **Code Examples in Documentation**
   - Show equivalent code in other languages
   - Compare Fusion syntax to Python/C#/Java/etc.

2. **Configuration Examples**
   - Document JSON/YAML/XML config file formats
   - Show SQL queries in database modules

3. **Cross-Language Interop Documentation**
   - Show C/C++ FFI examples
   - Document external API calls (REST, GraphQL)

4. **Teaching and Tutorials**
   - Side-by-side comparisons of languages
   - Educational comments with highlighted examples

5. **Code Migration Notes**
   - Document original code from other languages
   - Show translation notes during porting

**Edge Cases:**

```fusion
''' This is NOT a language hint (has space after ''')
No syntax highlighting
'''

'''python This is NOT valid (space in identifier)
No syntax highlighting
'''

'''python-3.11 This IS valid (hyphen allowed)
Syntax highlighting as Python
'''

'''c++ This IS valid
Syntax highlighting as C++
'''

'''UnknownLang This is valid but unknown language
No syntax highlighting (treated as plain comment)
'''

''''fusion This is 4 quotes - ERROR (see note below)
''''
```

**Note on `''''` (Four Quotes):**
This syntax (`''''`) is **NOT** supported. The lexer would interpret this as:
1. `'''` → Start of comment block
2. `'` → Part of comment content
3. Must close with `'''`

To avoid confusion:
- Lexer only recognizes exactly `'''` (three quotes)
- `''''` is invalid and would cause unterminated comment error
- Users should only use `'''` (three quotes)

**Timeline:**
- **Phase 1:** Basic `'''` comments (2-4 days) - Part of Enhanced Comment Support
- **Phase 2:** Language hint parsing (1 day) - Lexer modification
- **Phase 3:** IDE integration via LSP (3-5 days) - Requires fusionlib.IDE module
- **Phase 4:** DocWiki integration (2-3 days) - Documentation generation

**Total:** 8-13 days (AFTER compiler MVP complete)

**Benefits:**

**For Documentation:**
- ✅ Rich code examples with syntax highlighting
- ✅ Multi-language comparison in single file
- ✅ Better generated documentation (HTML/PDF)

**For Developers:**
- ✅ Easier to read embedded code examples
- ✅ IDE provides syntax checking for examples
- ✅ Copy-paste code examples stay formatted

**For Teaching:**
- ✅ Language comparison tutorials
- ✅ Migration guides with side-by-side code
- ✅ Interactive learning materials

---

### Feature 3: Comment Style Summary

**After implementation, Fusion will support:**

| Syntax | Type | Scope | Use Case | Status |
|--------|------|-------|----------|--------|
| `//` | Single-line | Rest of line | Inline comments, quick notes | ✅ MVP |
| `/* */` | Multi-line | Between markers | Block comments | ✅ MVP |
| `'` | Single-line | **Line-start only** | VB.NET-style line comments | 🔮 Future |
| `'''` | Multi-line block | Between markers | Python-style docstrings | 🔮 Future |
| `'''language` | Multi-line block | Between markers | Code examples with syntax highlighting | 🔮 Future (Post-Compiler) |

**Style Guide Recommendations:**
- **`//`** - Use for inline comments and brief explanations
- **`/* */`** - Use for multi-line explanations within code
- **`'`** - Use for commenting out entire lines (line-start only)
- **`'''`** - Use for documentation blocks and large comment sections
- **`'''language`** - Use for code examples in documentation with IDE syntax highlighting

---

### Implementation Notes

**Lexer Changes:**
1. Add `at_line_start` tracking to lexer state
2. Modify `is_comment_start()` to check `'''` first, then `'`
3. Add `skip_triple_quote_comment()` method
4. Update tests to re-enable `'` comment tests with line-start restriction

**Parser Changes:**
- None required (comments are lexer-only)

**Grammar Changes:**
```ebnf
comment = single_line_comment | multi_line_comment | line_comment | triple_quote_comment

single_line_comment = "//" { character } newline

multi_line_comment = "/*" { character } "*/"

line_comment = [whitespace] "'" [^"'"] { character } newline
  (* Only valid at line start, not followed by another ' *)

triple_quote_comment = "'''" { character | newline } "'''"
```

**Edge Cases:**
```fusion
' Valid comment
  ' Valid comment (indented)
int x = 5 ' ERROR: not at line start
char c = ''' ERROR: this starts a comment block, not a char
'''

char c = '\'' // Correct: escaped quote in char literal

'''
This is a comment
'''
string s = "test ' not a comment inside string"
```

---

### Testing Strategy

**Test Cases:**
1. `'` at line start → comment
2. `'` after whitespace at line start → comment
3. `'` mid-line → error or char literal context
4. `'''` block → comment
5. Nested `'''` → first closing `'''` ends block
6. `'` inside string literal → not a comment
7. Character literals (`'x'`, `'\n'`) → work correctly

**Files to Update:**
- `src/lexer/comments.py` - Add logic
- `tests/test_comments.py` - Re-enable disabled tests, add new ones
- `tests/test_lexer_integration.py` - Update integration tests

---

### Timeline

**Phase 1:** Re-enable `'` comments (line-start only)
- Estimated: 1-2 days
- Depends on: Lexer tracking line start state

**Phase 2:** Add `'''` block comments
- Estimated: 1-2 days
- Depends on: Phase 1 complete

**Phase 3:** Add `'''language` syntax highlighting support (Post-Compiler)
- Estimated: 8-13 days
- Depends on: Working compiler + fusionlib.IDE module + LSP implementation
- Sub-phases:
  - 2a. Language hint parsing (1 day)
  - 2b. IDE integration via LSP (3-5 days)
  - 2c. DocWiki integration (2-3 days)
  - 2d. Testing and polish (2-4 days)

**Total Timeline:**
- **MVP Comments:** 2-4 days (Phases 1-2)
- **Enhanced Comments:** 8-13 days (Phase 3 - Post-Compiler)
- **Grand Total:** 10-17 days

---

### Benefits

**For VB.NET Developers:**
- ✅ Familiar `'` comment syntax
- ✅ Easier migration from VB.NET code
- ✅ Consistent with VB.NET experience

**For Python Developers:**
- ✅ Familiar `'''` docstring syntax
- ✅ Natural documentation style
- ✅ Easier to comment out large blocks

**For All Developers:**
- ✅ More comment style options
- ✅ Choose preferred style per project
- ✅ Better documentation capabilities

---

### Open Questions

1. **Should `'''` support nested blocks?**
   - **Recommendation:** No - first `'''` closes (same as Python)

2. **Should `'''` be allowed for string literals too?**
   - **Recommendation:** Future feature - multi-line string literals

3. **Should `'` require a space after it?**
   - **Recommendation:** No - `'comment` and `' comment` both valid

4. **What about `''` (two quotes)?**
   - **Recommendation:** Empty string literal, not a comment

5. **Should language hints be case-sensitive?**
   - **Recommendation:** No - normalize to lowercase (`Python`, `python`, `PYTHON` all work)

6. **What if IDE doesn't support the specified language?**
   - **Recommendation:** Gracefully degrade to plain comment (no syntax highlighting)

7. **Should language hints support aliases (e.g., `js` vs `javascript`)?**
   - **Recommendation:** Yes - IDE determines aliases, not compiler

8. **Should Fusion validate language names?**
   - **Recommendation:** No - pass through to IDE/LSP, unknown languages = plain comment

9. **Should `'''language` support language-specific linting?**
   - **Recommendation:** Future feature (post-LSP) - IDE provides inline diagnostics for embedded code

---

## ⚙️ Enhanced Option Strict - Variable Naming Rules

**Status:** 📝 Proposed
**Priority:** Medium (code quality enhancement)
**Impact:** Compiler semantic analyzer, strict mode
**Depends On:** Basic compiler completion

**Purpose:** Extend `option strict` with configurable variable naming rules to enforce meaningful identifier names and improve code readability.

---

### Overview

Poor variable naming is a common source of code maintenance issues. Single-character variable names (except in specific contexts) make code harder to understand and maintain. This feature extends `option strict` to enforce minimum variable name lengths with intelligent exceptions for common cases.

---

### Important Context: When Single-Character Names Are Acceptable

**🎓 Tutorial/Demo/Toy Code:**
- Single-character variables (e.g., `x`, `y`, `n`) are **acceptable** for ease of use in:
  - Tutorial code and learning materials
  - Demo applications and example code
  - Toy projects and prototypes
- **Reason:** Simplicity helps learners focus on concepts, not naming
- **Recommendation:** Disable strict mode for educational projects

**🏢 Production Code:**
- Single-character variables should be **actively prevented** in production
- **Reason:** Code maintainability, team collaboration, long-term support
- **Recommendation:** Enable strict mode with minimum 3-4 character requirement

**🔬 Math/Science/Engineering Exception:**
- Mathematical, scientific, and engineering modules **may use single-character variables** due to domain conventions
- **Common conventions:**
  - `m` = mass
  - `v` = velocity
  - `a` = acceleration
  - `t` = time
  - `F` = force
  - `E` = energy
  - `P` = power
  - `c` = speed of light constant
  - `g` = gravitational constant
  - `h` = Planck's constant
  - `π` (pi) = mathematical constant (~3.14159)
  - `e` = Euler's number (~2.71828)
  - `θ` (theta) = angle
  - `φ` (phi) = phase angle
  - `Δ` (delta) = change/difference
  - `Σ` (sigma) = summation
  - `λ` (lambda) = wavelength
- **Reason:** These are **universal domain conventions** recognized across scientific literature
- **Recommendation:** Allow short names in specific modules (Math, Physics, Chemistry, Engineering)

**Configuration Strategy by Project Type:**

```json
// Tutorial/Demo Project
{
  "strictMode": {
    "enabled": false  // Allow short names for simplicity
  }
}

// Production Web/Business Application
{
  "strictMode": {
    "enabled": true,
    "minVariableNameLength": 3,
    "enforcementLevel": "error"  // Block compilation
  }
}

// Scientific/Math Module
{
  "strictMode": {
    "enabled": true,
    "minVariableNameLength": 3,
    "allowShortNamesInModules": [
      "Math",
      "Physics",
      "Chemistry",
      "Engineering",
      "Geometry",
      "Calculus"
    ]
  }
}

// Hybrid Project (tutorial + production)
{
  "strictMode": {
    "enabled": true,
    "minVariableNameLength": 3,
    "enforcementLevel": "warning",  // Warn, don't block (for migration)
    "excludePaths": [
      "./examples/**",
      "./tutorials/**",
      "./demos/**"
    ]
  }
}
```

**Annotation-Based Exception (Future Feature):**
```fusion
// Allow short names in this function using annotation
@allow-short-names
float function calculateKineticEnergy(float m, float v)
    // m = mass, v = velocity (domain conventions)
    return 0.5 * m * v * v  // KE = ½mv²

// Or allow for entire module
@allow-short-names
module Physics.Kinematics
    // All functions in this module can use short names
```

---

**Problem:**
```fusion
// Hard to understand
int x = 10
string n = "Alice"
float p = 3.14
bool f = true

// What do these variables represent?
```

**Solution with Enhanced Strict Mode:**
```fusion
option strict

// Compiler error: Variable names must be at least 3 characters
int count = 10        // ✅ Valid
string name = "Alice" // ✅ Valid
float price = 3.14    // ✅ Valid
bool isActive = true  // ✅ Valid

int x = 10  // ❌ Error: Variable name 'x' is too short (min 3 characters)
```

---

### Feature: Minimum Variable Name Length

**Configuration:**
- **Default minimum length:** 3 characters
- **Configurable:** Project lead can adjust (e.g., 2, 3, 4, 5 characters)
- **Applies to:** Local variables, function parameters, class fields, properties
- **Does NOT apply:** Type parameters (generics), loop counters (see exceptions)

**Configuration Options (project.json):**
```json
{
  "strictMode": {
    "enabled": true,
    "minVariableNameLength": 3,
    "allowSingleCharLoopCounters": true,
    "allowGenericTypeParams": true
  }
}
```

**Alternative Configuration (.fusion/strict.json):**
```json
{
  "variableNaming": {
    "minLength": 3,
    "exceptions": {
      "loopCounters": ["i", "j", "k", "x", "y", "z"],
      "typeParameters": ["T", "K", "V"]
    }
  }
}
```

---

### Exception 1: Reserved Loop Counter Names

**Allowed single-character names in loop contexts ONLY:**
- `i` - Primary loop counter (most common)
- `j` - Nested loop counter
- `k` - Third-level nested loop counter
- `x` - Horizontal coordinate loops
- `y` - Vertical coordinate loops
- `z` - Depth coordinate loops (3D)

**Valid Usage (within loops only):**
```fusion
// ✅ Valid: i, j, k in loop context
for i = 0 to 10
    print(i)

for i = 0 to 10
    for j = 0 to 5
        print("{i}, {j}")

// ✅ Valid: x, y for coordinates
for x = 0 to width
    for y = 0 to height
        drawPixel(x, y)

// ✅ Valid: nested loops with i, j, k
for i = 0 to rows
    for j = 0 to cols
        for k = 0 to depth
            matrix[i][j][k] = 0
```

**Invalid Usage (outside loop context):**
```fusion
// ❌ Error: 'i' not allowed outside loop context
int i = 5
print(i)

// ❌ Error: 'x' not allowed as function parameter
int function calculate(int x, int y)
    return x + y

// ❌ Error: 'j' not allowed as class field
class Counter
    private int j  // Error: Use meaningful name like 'count' or 'value'
```

**Context Detection:**
The compiler tracks whether a variable is declared inside:
- `for` loop initializer
- `while` loop body (local scope)
- `loop` statement body (local scope)

**Example: Valid and Invalid**
```fusion
// ✅ Valid loop counter
for i = 0 to 10
    print(i)  // 'i' valid here

// ❌ Error: 'i' used outside loop
print(i)  // Error: Variable 'i' out of scope or invalid name

// ✅ Valid: meaningful names required outside loops
int index = 0
for i = 0 to 10
    index = i * 2  // Both valid in their contexts
```

---

### Exception 2: Generic Type Parameters (Reserved Names)

**Allowed single-character type parameter names:**
- `T` - Generic Type (most common)
- `K` - Key type (for maps/dictionaries)
- `V` - Value type (for maps/dictionaries)

**Common Usage Patterns:**

**Generic Type `T`:**
```fusion
// ✅ Valid: T for generic type parameter
class Box<T>
    private T value

    public constructor(T item)
        value = item

    public T function get()
        return value

// ✅ Valid: Multiple type parameters
class Pair<T, U>
    public T first
    public U second

// ✅ Valid: Generic function
T function identity<T>(T item)
    return item

// ✅ Valid: Generic collection
class ArrayList<T>
    private List<T> items

    public void function add(T item)
        items.append(item)

    public T function get(int index)
        return items[index]
```

**Key-Value Types `K` and `V`:**
```fusion
// ✅ Valid: K for Key, V for Value
class Map<K, V>
    private Dictionary<K, V> data

    public void function put(K key, V value)
        data[key] = value

    public V function get(K key)
        return data[key]

// ✅ Valid: Dictionary usage
class Cache<K, V>
    private Map<K, V> storage

    public void function set(K key, V value)
        storage.put(key, value)

// ✅ Valid: Generic function with K, V
V function getOrDefault<K, V>(Map<K, V> map, K key, V defaultValue)
    if map.containsKey(key)
        return map.get(key)
    return defaultValue
```

**Descriptive Type Parameter Names (Alternative):**
While `T`, `K`, `V` are allowed as single-character names, developers may also use longer descriptive names:
```fusion
// Also valid: Descriptive type parameter names
class Box<TItem>
    private TItem value

class Map<TKey, TValue>
    private Dictionary<TKey, TValue> data

// Both styles allowed - project lead decides coding standards
```

**IDE Tooltip Support:**
When hovering over generic type parameters in IDEs:
```fusion
// Hover over 'T' in code
ArrayList<String> names = ArrayList<String>()
// IDE Tooltip: "T = String (generic type parameter)"

// Hover over 'K' or 'V'
Map<int, String> userMap = Map<int, String>()
// IDE Tooltip:
//   "K = int (key type parameter)"
//   "V = String (value type parameter)"
```

**Type Parameter Constraints:**
```fusion
// ✅ Valid: T with constraint
class NumberBox<T> where T : Number
    private T value

// ✅ Valid: Multiple constraints
class Sortable<T> where T : IComparable, ICloneable
    private List<T> items

    public void function sort()
        items.sort()  // T implements IComparable
```

---

### Scope and Applicability

**Applies to:**
- Local variables in functions
- Function parameters
- Class fields (private, protected, public)
- Struct fields
- Property backing fields
- Lambda parameters (if not inferred)

**Does NOT apply to:**
- Generic type parameters (`T`, `K`, `V`) - always allowed as single-char
- Loop counters (`i`, `j`, `k`, `x`, `y`, `z`) - allowed in loop context only
- Constant names (follow separate naming conventions)
- Enum values (follow separate naming conventions)
- Interface method parameters (often abbreviated)

---

### Error Messages

**Example 1: Variable name too short**
```fusion
int x = 10
```
**Error:**
```
Error: Variable name 'x' is too short (min 3 characters required in strict mode)
  at line 1, column 5
  Hint: Use a descriptive name like 'count', 'index', or 'value'
  Hint: Single-character names are only allowed for loop counters (i, j, k, x, y, z) within loops
```

**Example 2: Loop counter outside loop**
```fusion
int i = 0
while i < 10
    print(i)
    i = i + 1
```
**Error:**
```
Error: Variable name 'i' is too short (min 3 characters required in strict mode)
  at line 1, column 5
  Hint: Single-character name 'i' is only allowed as a loop counter inside a 'for' loop initializer
  Hint: Use 'for i = 0 to 10' instead, or rename to a descriptive name like 'index' or 'counter'
```

**Example 3: Correct usage**
```fusion
// ✅ All valid
for i = 0 to 10
    int count = i * 2  // 'i' valid in loop, 'count' is 5 chars
    print(count)

class Box<T>  // 'T' allowed as type parameter
    private T value  // 'value' is 5 chars (valid)
```

---

### Configuration Levels

**Project managers can configure strictness levels:**

**Level 1: Lenient (minLength = 2)**
```json
{ "minVariableNameLength": 2 }
```
- Allows: `id`, `x`, `y`, `no`, `ok`
- Good for: Prototyping, small projects

**Level 2: Balanced (minLength = 3, default)**
```json
{ "minVariableNameLength": 3 }
```
- Allows: `age`, `idx`, `key`, `val`
- Good for: Most projects, teams

**Level 3: Strict (minLength = 4)**
```json
{ "minVariableNameLength": 4 }
```
- Requires: `name`, `user`, `count`, `index`
- Good for: Enterprise, large teams

**Level 4: Very Strict (minLength = 5)**
```json
{ "minVariableNameLength": 5 }
```
- Requires: `userId`, `count`, `index`, `value`
- Good for: Critical systems, strict coding standards

**Per-Project Configuration:**
Project leads decide based on:
- Team size and experience
- Project complexity
- Maintenance requirements
- Industry standards (e.g., finance, healthcare)

---

### Implementation Notes

**Semantic Analyzer Changes:**
1. Check variable/parameter names during declaration
2. Track variable declaration context (loop vs. non-loop)
3. Enforce minimum length (configurable)
4. Allow exceptions for:
   - Loop counters (`i`, `j`, `k`, `x`, `y`, `z`) in loop context
   - Generic type parameters (`T`, `K`, `V`)
5. Provide helpful error messages with suggestions

**Configuration System:**
- Read from `project.json` under `strictMode` section
- Fall back to `~/.fusion/strict.json` for user defaults
- Command-line override: `fusion build --strict-var-length=3`

**Compiler Flags:**
```bash
# Enable strict mode with custom min length
fusion build --strict --min-var-length=4

# Disable variable name checking (override strict mode)
fusion build --no-strict-names

# Show all variable name violations (warnings, don't fail)
fusion build --warn-short-names
```

---

### IDE Integration

**Real-time Validation:**
- IDE underlines short variable names as you type
- Tooltip explains minimum length requirement
- Quick-fix suggestions: "Rename to descriptive name"

**Code Completion:**
- IDE suggests meaningful names based on type
  - `int` → suggests "count", "index", "value"
  - `string` → suggests "name", "text", "message"
  - `bool` → suggests "isActive", "hasValue", "enabled"

**Refactoring:**
- "Rename variable" command checks minimum length
- Warns if new name is too short
- Auto-suggests longer alternatives

---

### Benefits

**For Code Quality:**
- ✅ Enforces meaningful variable names
- ✅ Reduces "code smell" from poor naming
- ✅ Makes code self-documenting
- ✅ Easier code reviews

**For Maintenance:**
- ✅ New developers understand code faster
- ✅ Less need for comments (names explain purpose)
- ✅ Reduces bugs from variable confusion
- ✅ Easier refactoring

**For Teams:**
- ✅ Consistent naming standards across projects
- ✅ Configurable per project/team needs
- ✅ Enforced automatically (no manual code reviews needed)
- ✅ Exceptions for common patterns (loops, generics)

---

## 🔍 IDE Code Quality Overlays & Hints

**Status:** 📝 Proposed
**Priority:** High (developer experience, code quality)
**Impact:** IDE integration, Language Server Protocol (LSP)
**Depends On:** fusionlib.IDE module, LSP implementation
**Module:** fusionlib.IDE

**Purpose:** Provide real-time code quality analysis, performance insights, and refactoring suggestions directly in the IDE through visual overlays and interactive hints.

---

### Overview

Modern IDEs provide rich feedback beyond syntax errors. This feature adds intelligent overlays and hints that help developers write better, faster, more maintainable code. All features are configurable by project managers to match team standards and project requirements.

**Key Principles:**
- Non-intrusive: Hints don't block development
- Configurable: Project leads control thresholds and enabled features
- Actionable: Each hint provides clear next steps
- Context-aware: Suggestions match project patterns

---

### Feature 1: Inverted If Detection (Reduce Nesting)

**Purpose:** Detect deeply nested IF statements and suggest guard clauses/early returns to reduce complexity.

**Problem - Deeply Nested Code:**
```fusion
int function processUser(User user)
    if user != null
        if user.isActive
            if user.hasPermission("admin")
                if user.age >= 18
                    // 4 levels of nesting - hard to read
                    return performAdminAction(user)
                else
                    return ErrorCode.TooYoung
            else
                return ErrorCode.NoPermission
        else
            return ErrorCode.Inactive
    else
        return ErrorCode.NullUser
```

**Solution - Inverted Conditions (Guard Clauses):**
```fusion
int function processUser(User user)
    // Early returns - flat structure
    if user == null
        return ErrorCode.NullUser

    if not user.isActive
        return ErrorCode.Inactive

    if not user.hasPermission("admin")
        return ErrorCode.NoPermission

    if user.age < 18
        return ErrorCode.TooYoung

    // Main logic at top level - easy to read
    return performAdminAction(user)
```

**IDE Visualization:**
- **Overlay:** Colored vertical lines showing nesting depth
- **Warning:** "Consider inverting conditions to reduce nesting"
- **Quick-fix:** "Refactor to guard clauses" (auto-applies transformation)
- **Before/After Preview:** Shows refactored code

**Configuration:**
```json
{
  "codeQuality": {
    "maxNestingDepth": 3,
    "suggestGuardClauses": true,
    "warnAtDepth": 3,
    "errorAtDepth": 5
  }
}
```

**Thresholds:**
- **Depth 1-2:** ✅ Green (good)
- **Depth 3:** ⚠️ Yellow warning (consider refactoring)
- **Depth 4:** 🟠 Orange warning (should refactor)
- **Depth 5+:** 🔴 Red error (must refactor)

---

### Feature 2: Thread Visualization (Communication Tracking)

**Purpose:** Show where threads/goroutines are created and visualize channel communication between concurrent tasks.

**Example Code:**
```fusion
import Fusion.Threading

void function main()
    Channel<int> results = Channel<int>()

    // Create 3 worker threads
    go worker(results, 1)  // Thread 1
    go worker(results, 2)  // Thread 2
    go worker(results, 3)  // Thread 3

    // Collect results
    for i = 0 to 3
        int result = results.receive()
        print("Got result: {result}")

void function worker(Channel<int> ch, int id)
    // Do work
    int result = compute(id)
    ch.send(result)  // Send to channel
```

**IDE Visualization:**

**1. Thread Creation Points:**
- `go worker(...)` highlighted with thread icon 🧵
- Hover tooltip: "Creates new goroutine/thread"
- Click to jump to function definition

**2. Channel Communication:**
- Visual arrows showing data flow:
  ```
  worker(1) -----> [Channel] -----> main()
  worker(2) -----> [Channel] -----> main()
  worker(3) -----> [Channel] -----> main()
  ```

**3. Synchronization Points:**
- Mutex locks highlighted in blue
- Channels highlighted in green
- WaitGroups highlighted in purple

**4. Data Race Detection:**
- Warn if shared variables accessed without locks
- Highlight potential race conditions in red

**IDE Features:**
- **Thread Tree View:** Shows all threads and their parent-child relationships
- **Message Trace:** Shows channel send/receive pairs
- **Deadlock Detection:** Warns about potential deadlocks (circular waits)

**Configuration:**
```json
{
  "threading": {
    "showThreadCreation": true,
    "showChannelFlow": true,
    "showSynchronization": true,
    "warnDataRaces": true,
    "warnDeadlocks": true
  }
}
```

---

### Feature 3: Performance Profiling Overlay

**Purpose:** After running/profiling the app, show inline performance metrics (execution time, memory usage, call frequency) directly in the code editor.

**Example:**
```fusion
void function main()
    processData()  // 85% of total time ⚠️
    saveResults()  // 10% of total time
    cleanup()      // 5% of total time

void function processData()
    // Called: 1 time
    // Time: 850ms (85% of total)
    // Memory: 120MB allocated

    for i = 0 to 1000000  // 60% of function time
        heavyCalculation(i)

    sortResults()  // 25% of function time

void function heavyCalculation(int n)  // Called: 1,000,000 times ⚠️
    // Avg time per call: 0.85μs
    // Total time: 850ms
    // Memory per call: 120 bytes

    // Hot path detected ⚡
    int result = complexMath(n)
    return result
```

**IDE Visualization:**

**1. Inline Metrics (Next to Function):**
```fusion
void function processData()  // 🔥 85% | 850ms | 120MB
```

**2. Heatmap Overlay:**
- Red: Hot code (most time spent)
- Orange: Warm code (moderate time)
- Yellow: Cool code (little time)
- Green: Cold code (negligible time)

**3. Memory Allocation Indicators:**
```fusion
List<int> data = List<int>()  // 💾 5MB allocated
```

**4. Call Frequency:**
```fusion
void function calculate(int x)  // 📞 Called 1,000,000× per run
```

**IDE Features:**
- **Profiler Panel:** Shows flame graph, call tree, memory timeline
- **Comparison Mode:** Compare performance before/after refactoring
- **Export:** Save profile data to file for analysis

**Configuration:**
```json
{
  "profiling": {
    "showInlineMetrics": true,
    "showHeatmap": true,
    "showMemoryAllocation": true,
    "showCallFrequency": true,
    "hotPathThreshold": 10,  // % of total time to mark as "hot"
    "frequentCallThreshold": 1000  // Calls per run to warn
  }
}
```

**Integration:**
```bash
# Run app with profiling enabled
fusion run --profile main.fusion

# IDE automatically loads profile data and shows overlays
```

---

### Feature 4: Duplicate Code Detection

**Purpose:** Highlight duplicated code blocks and suggest extraction to functions/methods to follow DRY principle.

**Example - Duplicated Code:**
```fusion
void function processOrderA(Order order)
    // Duplicate block 1
    if order.total > 100
        order.discount = order.total * 0.1
        order.total = order.total - order.discount

    saveOrder(order)

void function processOrderB(Order order)
    // Duplicate block 2 (87% similar)
    if order.total > 100
        order.discount = order.total * 0.1
        order.total = order.total - order.discount

    emailCustomer(order)
```

**IDE Visualization:**

**1. Highlight Duplicates:**
- Both duplicate blocks highlighted in yellow
- Link icon showing relationship
- Hover tooltip: "87% similar to code at line 15"

**2. Similarity Percentage:**
```
🔗 Duplicate detected (87% similar)
Found in: processOrderB() at line 15
```

**3. Quick-fix Suggestion:**
```
💡 Extract to function: "applyDiscount(Order)"
```

**Refactored Code:**
```fusion
void function applyDiscount(Order order)
    if order.total > 100
        order.discount = order.total * 0.1
        order.total = order.total - order.discount

void function processOrderA(Order order)
    applyDiscount(order)
    saveOrder(order)

void function processOrderB(Order order)
    applyDiscount(order)
    emailCustomer(order)
```

**IDE Features:**
- **Duplicate Panel:** Lists all duplicates in project
- **Auto-refactor:** One-click extraction to function
- **Ignore List:** Mark intentional duplicates (e.g., templates)

**Configuration:**
```json
{
  "duplicateDetection": {
    "enabled": true,
    "minSimilarity": 70,  // % similarity to flag as duplicate
    "minLines": 5,        // Minimum lines to consider
    "ignoreComments": true,
    "ignoreWhitespace": true,
    "suggestExtraction": true
  }
}
```

---

### Feature 5: Naming Quality Analysis (Dictionary Builder)

**Purpose:** Build a dictionary of all identifiers (variables, functions, classes, etc.) and suggest better names based on usage context and clarity.

**Example - Poor Names:**
```fusion
class U
    private string n
    private int a

    public void function p()
        print("{n} is {a} years old")

void function main()
    U u = U()
    u.n = "Alice"
    u.a = 25
    u.p()
```

**IDE Suggestions:**

**1. Class Name `U`:**
```
⚠️ Class name 'U' is unclear (1 character)
💡 Suggested names based on usage:
   - User (contains name and age)
   - Person
   - Customer
```

**2. Field Name `n`:**
```
⚠️ Field 'n' is unclear (1 character)
💡 Suggested names based on type and usage:
   - name (most common for string)
   - fullName
   - userName
```

**3. Method Name `p()`:**
```
⚠️ Method 'p' is unclear (1 character)
💡 Suggested names based on behavior:
   - print()
   - printInfo()
   - displayDetails()
```

**Refactored Code:**
```fusion
class User
    private string name
    private int age

    public void function printInfo()
        print("{name} is {age} years old")

void function main()
    User user = User()
    user.name = "Alice"
    user.age = 25
    user.printInfo()
```

**IDE Features:**

**1. Naming Dictionary:**
- Tracks all identifiers in project
- Analyzes usage patterns
- Builds context-aware suggestions

**2. Clarity Score:**
```fusion
class User      // Clarity: 95% ✅
class U         // Clarity: 20% ⚠️
class UsrMgr    // Clarity: 60% (abbreviation)
```

**3. Auto-complete with Context:**
```fusion
// Typing: int c
// Suggestions:
//   - count (common int name)
//   - counter
//   - currentIndex
```

**Configuration:**
```json
{
  "namingQuality": {
    "enabled": true,
    "minNameLength": 3,
    "flagAbbreviations": true,
    "suggestAlternatives": true,
    "clarityThreshold": 50,  // % clarity score to warn
    "buildDictionary": true,
    "learnFromProject": true  // Learn naming patterns from codebase
  }
}
```

---

### Feature 6: Nested Loop Warning (Performance)

**Purpose:** Detect nested loops with potential O(n²) or O(n³) complexity and suggest optimization opportunities.

**Example - O(n²) Nested Loop:**
```fusion
void function findPairs(List<int> numbers)
    for i = 0 to numbers.length  // O(n)
        for j = 0 to numbers.length  // O(n) → O(n²) total
            if numbers[i] + numbers[j] == 10
                print("{numbers[i]} + {numbers[j]} = 10")
```

**IDE Warning:**
```
⚠️ Nested loop detected: O(n²) complexity
  Outer loop: line 2 (n iterations)
  Inner loop: line 3 (n iterations)
  Total: n × n = n² iterations

💡 Optimization suggestions:
  1. Use HashMap for O(n) lookup
  2. Sort and use two-pointer technique
  3. Break early when possible
```

**Optimized Code (Example):**
```fusion
void function findPairs(List<int> numbers)
    Set<int> seen = Set<int>()

    for num in numbers  // O(n)
        int complement = 10 - num
        if seen.contains(complement)  // O(1) lookup
            print("{num} + {complement} = 10")
        seen.add(num)

    // Total: O(n) instead of O(n²)
```

**IDE Visualization:**

**1. Complexity Indicator:**
```fusion
for i = 0 to n      // 🟢 O(n)
    for j = 0 to n  // 🟡 O(n²) - Nested loop warning
        for k = 0 to n  // 🔴 O(n³) - High complexity!
```

**2. Iteration Count Estimate:**
```
Loop at line 2:
  Estimated iterations: 1,000,000 (n=1000, n²=1,000,000)
  ⚠️ High iteration count - consider optimization
```

**Configuration:**
```json
{
  "nestedLoops": {
    "enabled": true,
    "warnAtComplexity": "O(n²)",  // or "O(n³)"
    "errorAtComplexity": "O(n³)",
    "suggestOptimizations": true,
    "showIterationEstimate": true,
    "estimatedInputSize": 1000  // For iteration calculations
  }
}
```

---

### Feature 7: Nested Control Flow Refactoring

**Purpose:** Detect deeply nested IF/switch statements and suggest extraction to separate functions for improved readability.

**Example - Deeply Nested Control Flow:**
```fusion
int function processRequest(Request req)
    if req.type == "GET"
        if req.hasAuth
            if req.user.role == "admin"
                if req.path.startsWith("/admin")
                    return handleAdminGet(req)
                else
                    return ErrorCode.Forbidden
            else
                return handleUserGet(req)
        else
            return ErrorCode.Unauthorized
    else if req.type == "POST"
        if req.hasAuth
            if req.body != null
                return handlePost(req)
            else
                return ErrorCode.BadRequest
        else
            return ErrorCode.Unauthorized
    else
        return ErrorCode.MethodNotAllowed
```

**IDE Warning:**
```
⚠️ Complex control flow detected (cyclomatic complexity: 8)
💡 Consider extracting to separate functions:
  - extractAuthCheck()
  - extractGetHandler()
  - extractPostHandler()
```

**Refactored Code:**
```fusion
int function processRequest(Request req)
    if not req.hasAuth
        return ErrorCode.Unauthorized

    match req.type
        case "GET":
            return handleGet(req)
        case "POST":
            return handlePost(req)
        default:
            return ErrorCode.MethodNotAllowed

int function handleGet(Request req)
    if req.user.role == "admin" and req.path.startsWith("/admin")
        return handleAdminGet(req)
    else if req.user.role == "admin"
        return ErrorCode.Forbidden
    else
        return handleUserGet(req)

int function handlePost(Request req)
    if req.body == null
        return ErrorCode.BadRequest
    return handlePostWithBody(req)
```

**IDE Visualization:**

**1. Complexity Meter:**
```
Cyclomatic Complexity: 8 🟠
  1-5:   🟢 Simple
  6-10:  🟡 Moderate - consider refactoring
  11-15: 🟠 Complex - should refactor
  16+:   🔴 Very complex - must refactor
```

**2. Visual Nesting Indicator:**
```
Nesting depth visualization (left margin):
|     if                 // Depth 1
| |     if               // Depth 2
| | |     if             // Depth 3 ⚠️
| | | |     if           // Depth 4 🔴
```

**Configuration:**
```json
{
  "controlFlowComplexity": {
    "enabled": true,
    "maxComplexity": 10,
    "warnAtComplexity": 6,
    "maxNestingDepth": 3,
    "suggestExtraction": true,
    "suggestMatchStatement": true  // Suggest 'match' instead of if-else chains
  }
}
```

---

### Configuration Management (Project-Level)

**Master Configuration File (project.json):**
```json
{
  "name": "MyFusionProject",
  "version": "1.0.0",

  "codeQuality": {
    "invertedIfDetection": {
      "enabled": true,
      "maxNestingDepth": 3,
      "warnAtDepth": 3
    },

    "threadVisualization": {
      "enabled": true,
      "showThreadCreation": true,
      "showChannelFlow": true,
      "warnDataRaces": true
    },

    "performanceProfiling": {
      "enabled": true,
      "showInlineMetrics": true,
      "hotPathThreshold": 10
    },

    "duplicateDetection": {
      "enabled": true,
      "minSimilarity": 70,
      "minLines": 5
    },

    "namingQuality": {
      "enabled": true,
      "minNameLength": 3,
      "clarityThreshold": 50
    },

    "nestedLoops": {
      "enabled": true,
      "warnAtComplexity": "O(n²)",
      "errorAtComplexity": "O(n³)"
    },

    "controlFlowComplexity": {
      "enabled": true,
      "maxComplexity": 10,
      "maxNestingDepth": 3
    }
  }
}
```

**Per-Developer Overrides (~/.fusion/preferences.json):**
```json
{
  "codeQuality": {
    "showHints": true,
    "autoFixSuggestions": false,  // User prefers manual fixes
    "overlayOpacity": 0.7
  }
}
```

**Command-Line Overrides:**
```bash
# Disable all hints temporarily
fusion build --no-hints

# Enable only specific hints
fusion build --hints=nesting,performance

# Adjust thresholds
fusion build --max-nesting=4 --max-complexity=15
```

---

### IDE Integration Architecture

**Language Server Protocol (LSP) Extensions:**
- **Custom notifications:** Send code quality data to IDE
- **Custom commands:** "Refactor to guard clauses", "Extract function"
- **Diagnostics:** Warnings and errors for code quality issues
- **Code actions:** Quick-fixes for detected issues

**Real-time Analysis:**
- Background thread analyzes code as you type
- Non-blocking: Doesn't slow down editing
- Debounced: Waits for pause in typing before analyzing

**Visual Overlays:**
- InlayHints: Show metrics inline
- Decorations: Color overlays for heatmaps
- Gutter icons: Thread creation, hot paths
- Hover tooltips: Detailed information

---

### Benefits Summary

**For Developers:**
- ✅ Real-time code quality feedback
- ✅ Learn best practices while coding
- ✅ Catch performance issues early
- ✅ Reduce time spent in code review

**For Project Managers:**
- ✅ Enforce team coding standards automatically
- ✅ Configure quality thresholds per project
- ✅ Track code quality metrics over time
- ✅ Reduce technical debt

**For Teams:**
- ✅ Consistent code quality across team
- ✅ Faster onboarding (IDE guides new developers)
- ✅ Fewer bugs from poor practices
- ✅ Better collaboration (readable code)

---

user added comments to be formated and updated with claude
Webserver
create webserver module to handle webservices, hosting, routeing of websites
Simple host like direct index.html
Complex where its a highbrid like php where you have the weebsite.php code and inside is code to generate and add addtional sections
in code gennerateion like nodejs


above to be rechecked and checked with below
the below will not be enough to have a single additonal class
it will be under
Webserver
	- 

from chat gpt
Here’s a breakdown of **common programming languages used for web servers and hosting**, including how they compare, what they do, and where they’re used.

### 🧩 Core Concept

A **web server language** (or **backend language**) runs on the **server** — it handles requests, processes logic, connects to databases, and sends responses (HTML/JSON/etc.) to the client’s browser.


### ⚙️ Common Web Server Languages

| Language / Runtime             | What It Is                                                          | How It Works                                                   | Typical Use Cases                                    | Key Differences                                                                |
| ------------------------------ | ------------------------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------ |
| **PHP**                        | Scripting language designed for web development.                    | Runs inside Apache/Nginx using PHP engine.                     | WordPress, Drupal, custom websites.                  | Easy to embed in HTML; synchronous; older ecosystem but very mature.           |
| **Node.js (JavaScript)**       | JavaScript runtime built on Chrome’s V8 engine.                     | Runs JS server-side (non-blocking I/O).                        | APIs, chat apps, real-time apps.                     | Event-driven; single-threaded but asynchronous; shares language with frontend. |
| **Python**                     | General-purpose language with frameworks like Flask/Django/FastAPI. | Interpreted; usually served via WSGI/ASGI (Gunicorn, Uvicorn). | Web apps, APIs, data dashboards.                     | Readable, flexible; great async support (FastAPI).                             |
| **Ruby**                       | Language with Ruby on Rails framework.                              | Interpreted; runs in Puma/Unicorn web servers.                 | Full web apps, startups, SaaS.                       | Convention over configuration; productive but slower runtime.                  |
| **Java**                       | Compiled language running on JVM.                                   | Runs via servlet containers (Tomcat, Jetty, Spring Boot).      | Enterprise web apps, APIs, banking.                  | Statically typed, highly scalable, mature ecosystem.                           |
| **C# (.NET / ASP.NET)**        | Microsoft’s language/framework for web apps.                        | Compiled; runs on .NET runtime.                                | Enterprise, corporate intranet, Windows integration. | Strong typing, fast, tightly integrated with Microsoft tools.                  |
| **Go (Golang)**                | Compiled, high-performance systems language.                        | Built-in HTTP server; compiled to native binary.               | APIs, microservices, cloud apps.                     | Extremely fast, low memory usage, easy concurrency.                            |
| **Rust (with Actix / Rocket)** | Compiled systems language with web frameworks.                      | Runs as compiled binary.                                       | High-performance web APIs, secure apps.              | Memory-safe, fastest among modern languages, steep learning curve.             |
| **Perl**                       | Early web scripting language (CGI era).                             | Runs via CGI/mod_perl.                                         | Legacy systems, text processing.                     | Old but still used in some server automation.                                  |
| **ColdFusion (CFML)**          | Adobe’s tag-based scripting language.                               | Runs on CFML engine (Lucee, Adobe CF).                         | Business intranet, CMS apps.                         | Easy for rapid development, but niche today.                                   |
| **Elixir (Phoenix Framework)** | Functional language on the Erlang VM.                               | Compiled; runs BEAM virtual machine.                           | Real-time systems, messaging, scalable APIs.         | Excellent concurrency and fault-tolerance.                                     |
| **Kotlin (Ktor / Spring)**     | Modern JVM language.                                                | Compiled; interoperates with Java.                             | APIs, microservices.                                 | Safer syntax than Java, modern features.                                       |


### 🕸️ Also Seen in Hosting Environments

* **Lua** → Used with Nginx/OpenResty for high-performance scripting.
* **Scala** → Used in enterprise APIs and data pipelines (on JVM).
* **C/C++** → Low-level web servers or embedded systems (e.g., Nginx, Apache modules).
* **R** → Used occasionally for data-driven APIs or dashboards.


### 🔍 Key Differences Summary

| Feature              | PHP            | Node.js             | Python           | Java         | C#           | Go                  |
| -------------------- | -------------- | ------------------- | ---------------- | ------------ | ------------ | ------------------- |
| **Speed**            | Medium         | Fast                | Medium           | Fast         | Fast         | Very Fast           |
| **Concurrency**      | Thread-based   | Event-driven        | Async/await      | Multi-thread | Multi-thread | Goroutines          |
| **Ease of Learning** | Easy           | Medium              | Easy             | Harder       | Medium       | Medium              |
| **Best For**         | Websites, CMS  | APIs, real-time     | APIs, automation | Enterprise   | Enterprise   | Microservices       |
| **Hosting Style**    | Shared hosting | Dedicated/Container | Container/Server | JVM          | .NET runtime | Binary (direct run) |


### ✅ Choosing One

* **Small website:** PHP
* **Modern web app or API:** Node.js / Python (FastAPI)
* **Enterprise system:** Java / C#
* **High performance microservice:** Go / Rust
* **Real-time messaging:** Elixir / Node.js


Would you like me to include **which hosting platforms support each best** (e.g., AWS, Azure, shared hosting, Docker, etc.)? That would make the overview more practical for deployment decisions.


here is another from Chat GPT
Perfect — here’s a **language-agnostic abstraction** of what all server-side languages (PHP, Node.js, Python, etc.) actually *do* under the hood, regardless of syntax or framework.


# 🧠 Core Server Function

### **1. Accepts and Handles Requests**

* Listens for incoming HTTP/HTTPS requests from browsers, apps, or APIs.
* Parses the request (method, headers, parameters, body, authentication).
* Routes it to the correct function, endpoint, or controller based on URL or path.


### **2. Processes Business Logic**

* Executes the logic that defines how the app behaves.
* Examples: validating user input, applying discounts, checking permissions, calculating totals, or running stored procedures.
* Enforces rules (e.g., “a user must be logged in to view orders”).


### **3. Interacts with Databases**

* Connects to databases (SQL or NoSQL) using a driver or ORM (Object-Relational Mapper).
* Executes queries to read or modify data (SELECT, INSERT, UPDATE, DELETE).
* Transforms raw database results into structured objects or JSON.


### **4. Communicates with External Systems**

* Makes API calls to other services (payment gateways, cloud APIs, messaging queues).
* Integrates with authentication providers (OAuth, SSO, JWT).
* Can send or receive messages from queues (Kafka, SQS, RabbitMQ).


### **5. Generates and Formats Responses**

* Converts results or templates into an appropriate response format:

  * **HTML** for web pages.
  * **JSON** or **XML** for APIs.
  * **Binary data** for file downloads.
* Sets headers (status codes, content type, cookies).
* Sends the response back to the client via HTTP.


### **6. Manages Sessions and Authentication**

* Tracks user sessions (login state) via cookies, tokens, or session IDs.
* Validates credentials and permissions for each request.
* May encrypt/decrypt sensitive session data.


### **7. Handles Errors and Logging**

* Catches runtime or network errors gracefully.
* Logs system activity and errors for debugging and audits.
* Optionally sends alerts or metrics to monitoring systems.


### **8. Performs Background or Async Tasks**

* Offloads long-running work (emails, image processing, batch jobs).
* Uses queues, schedulers, or background workers.
* Improves user response time by not blocking the main request thread.


### **9. Manages Configuration and Environment**

* Loads environment variables (API keys, DB credentials, feature toggles).
* Adjusts behavior based on deployment (development, test, production).
* Controls scaling, concurrency, and resource limits.


### **10. Serves Static or Dynamic Content**

* **Static:** delivers files directly (images, CSS, JS).
* **Dynamic:** generates output in real time (HTML pages, API responses).
* Often proxies static files through a CDN or web server (like Nginx).


### **11. Scales and Manages Resources**

* Spawns multiple worker processes/threads to handle many clients.
* Balances load, caches responses, and maintains uptime.
* Uses memory efficiently to serve concurrent connections.


### **12. Ensures Security**

* Sanitizes user input to prevent injection attacks.
* Uses HTTPS, encryption, and CSRF protection.
* Validates tokens and access scopes on every request.


Would you like me to show **how these 12 core responsibilities map** to each language (PHP, Node.js, Python, etc.) — i.e., what component or library typically handles each part in each ecosystem? That gives a clear “same function, different tool” comparison.


# 🌐 Web Service (Core Structure)

### **1. Requests (Entry Point)**

* Receives HTTP/HTTPS requests from browser, mobile app, or another API.
* Parses method (GET, POST, PUT, DELETE) and parameters.
* Passes request to the correct route or controller.

🧩 **Example**:

* `/api/users` → calls `UserController.getUsers()`
* `/api/orders/123` → calls `OrderController.getOrderById(123)`


### **2. Routing (Path Handling)**

* Defines URL endpoints and maps them to specific functions or modules.
* Handles versioning (e.g., `/v1/orders`) and middleware (auth, logging).

🧩 **Example**:

* `GET /api/products` → list products
* `POST /api/login` → authenticate user


### **3. Business Logic Layer**

* Contains the actual **rules and behavior** of your application.
* Should be **separate** from routes for cleaner design.
* Often communicates with other APIs or microservices.

🧩 **Example**:

* `OrderService.calculateDiscount()`
* `UserService.validateLogin(credentials)`
* `PaymentService.connectToGateway()`


### **4. Database Layer**

* Handles data persistence and retrieval.
* Uses an ORM (e.g., SQLAlchemy, Sequelize, Hibernate) or raw SQL queries.
* Returns structured data (objects, JSON) to the business layer.

🧩 **Example**:

* `UserRepository.getById(id)`
* `OrderRepository.save(orderData)`


### **5. Response (Output Layer)**

* Takes the processed data and formats it into a response for the client.
* Adds HTTP headers, status codes, and JSON or HTML output.
* Handles errors gracefully and returns messages or error codes.

🧩 **Example**:

* `return { "status": "success", "data": userList }`
* `return { "error": "Invalid credentials" }`


### **6. Middleware (Cross-Cutting Layers)**

* Code that runs **before or after** requests.
* Handles logging, authentication, rate limiting, caching, etc.

🧩 **Example**:

* `AuthMiddleware` → verify JWT token
* `LoggerMiddleware` → record request time and path
* `ErrorHandler` → catch and format exceptions


### **7. External Integrations**

* Connects to other APIs, microservices, or third-party platforms.
* Handles communication with payment systems, CRMs, or messaging services.

🧩 **Example**:

* `PaymentAPI.chargeCustomer()`
* `EmailService.sendWelcomeEmail()`


### **8. Background / Asynchronous Tasks**

* Executes heavy or delayed tasks outside the main request flow.
* Uses task queues or schedulers (Celery, BullMQ, Hangfire, etc.).

🧩 **Example**:

* Send report emails nightly.
* Resize uploaded images in the background.


### **9. Configuration / Environment**

* Holds environment variables, API keys, and runtime settings.
* Separates dev, test, and production configurations.

🧩 **Example**:

* `.env` → stores DB credentials, API secrets.
* Config loader module reads settings on startup.


### **10. Security Layer**

* Applies validation, sanitization, and access control.
* Uses HTTPS, CORS, CSRF, and input filtering.

🧩 **Example**:

* Check `Authorization` header.
* Escape user input in SQL queries.


### **Simplified Flow Diagram**

```
[Client Request]
       ↓
[Router / Endpoint]
       ↓
[Middleware]
       ↓
[Business Logic]
       ↓
[Database or External API]
       ↓
[Response Builder]
       ↓
[Client Receives JSON/HTML]
```


Would you like me to show this same structure as **code skeletons** in a few different languages (e.g., PHP, Node.js, Python, Java) — using the same logic flow so you can see how each implements it differently but achieves the same result?

---

## 🧑‍💻 Developer Experience Enhancements

### Comment Level System (0-5)

**Status:** 📝 Proposed
**Purpose:** Standardized documentation and comment hierarchy for code quality and maintainability

**What:** A six-level comment system that provides structure for code documentation, from self-documenting code to deprecated features.

#### Comment Level Definitions

**Level 0: Naming Comments (Self-Documenting Code)**

Code should be written with descriptive names that make the logic and flow understandable without comments.

🧩 **Example:**
```fusion
// Bad - requires comments
int x = 10  // user age
string n = "John"  // user name

// Good - self-documenting
int userAge = 10
string userName = "John"
```

**Level 1: Inline Comments**

Single-line comments for classes, functions, variables, and inside code blocks (decisions, loops, structures).

🧩 **Example:**
```fusion
// User authentication service
class AuthService
    // Validate user credentials
    bool function validateUser(string username, string password)
        // Check if username exists
        if userExists(username)
            // Verify password hash matches
            return checkPasswordHash(password)
        return false
```

**Level 2: Documentation Comments (DocFeature)**

Block comments explaining code in detail, including usage examples. Used for library APIs and public interfaces.

🧩 **Example:**
```fusion
/**
 * Authenticates a user against the database.
 *
 * @param username - The user's login name
 * @param password - The user's password (will be hashed)
 * @return bool - True if authentication successful, false otherwise
 *
 * Example:
 *   bool success = authenticate("john_doe", "myPassword123")
 *   if success
 *       print("Login successful")
 */
bool function authenticate(string username, string password)
    // Implementation...
```

**Level 3: Implementation Comments**

Block comments explaining decision points and why code was implemented a certain way. Stored separately in implementation documentation and optionally shown in normal DocFeature.

🧩 **Example:**
```fusion
/**
 * IMPLEMENTATION DECISION:
 * Using bcrypt instead of SHA-256 for password hashing.
 *
 * Why: bcrypt includes automatic salting and is designed to be slow,
 * making brute-force attacks computationally expensive.
 *
 * Alternatives considered:
 * - SHA-256: Too fast, vulnerable to rainbow tables
 * - Argon2: Better but less widely supported in 2025
 *
 * Decision date: 2025-11-10
 * Decided by: Security team review
 */
string function hashPassword(string password)
    return bcrypt.hash(password, rounds: 12)
```

**Level 4: TODO Comments**

Single-line or block comments describing what needs to happen or be changed. Documented separately for tracking pending work.

🧩 **Example:**
```fusion
// TODO: Add rate limiting to prevent brute-force attacks
// TODO: Implement two-factor authentication support
// TODO: Add logging for failed login attempts

/**
 * TODO: Refactor authentication system
 * - Split into separate AuthValidator and AuthStorage classes
 * - Add support for OAuth2 providers (Google, GitHub)
 * - Implement session management with Redis
 * Priority: Medium
 * Estimated effort: 3 days
 */
```

**Level 5: Deprecated Comments**

Like Level 4, but for code that needs to be actively removed in the future. Documented separately for deprecation tracking.

🧩 **Example:**
```fusion
/**
 * DEPRECATED: Use authenticateWithHash() instead
 * This function will be removed in version 2.0
 * Reason: Uses insecure MD5 hashing
 * Migration: Replace calls with authenticateWithHash()
 * Removal date: 2026-01-01
 */
bool function authenticateOld(string username, string password)
    // Old implementation using MD5...
```

#### Comment Level Summary Table

| Level | Type | Purpose | Storage | Examples |
|-------|------|---------|---------|----------|
| 0 | Naming | Self-documenting code | In code (names) | `userAge`, `calculateTotalPrice()` |
| 1 | Inline | Quick explanations | In code | `// Check if user exists` |
| 2 | DocFeature | API documentation | In code + docs | Function/class documentation with examples |
| 3 | Implementation | Design decisions | Separate doc | Why certain algorithms/patterns were chosen |
| 4 | TODO | Pending work | Separate tracker | Features to add, bugs to fix |
| 5 | Deprecated | Code to remove | Separate tracker | Old APIs, legacy code |


#### IDE Integration

**fusionlib.IDE** can extract and manage comment levels:

```fusion
import fusionlib.IDE

// Extract all TODO comments from project
List<TodoComment> todos = CommentAnalyzer.extractTodos("./src")

// Extract deprecated code
List<DeprecatedCode> deprecated = CommentAnalyzer.extractDeprecated("./src")

// Generate implementation decisions document
string decisions = CommentAnalyzer.generateImplementationDoc("./src")
```

---

### Coding Hints System

**Status:** 📝 Proposed
**Purpose:** Provide intelligent code structure suggestions beyond basic syntax hints

**What:** Advanced IDE hints that suggest structural improvements, design patterns, and best practices (not just autocomplete).

#### Hint Categories

##### 1. Control Flow Simplification

Detect nested conditionals and suggest inversions or early returns.

🧩 **Before:**
```fusion
void function processUser(User user)
    if user != null
        if user.isActive()
            if user.hasPermission("admin")
                // Do something
```

💡 **Hint:** "Invert conditions and use early returns to reduce nesting"

🧩 **After:**
```fusion
void function processUser(User user)
    if user == null
        return
    if not user.isActive()
        return
    if not user.hasPermission("admin")
        return

    // Do something (now at top level)
```

##### 2. Extract Method

Suggest extracting nested logic into separate functions.

🧩 **Before:**
```fusion
void function handleOrder(Order order)
    if order.items.count > 0
        float total = 0.0
        for item in order.items
            total += item.price * item.quantity
            if item.discount > 0
                total -= item.price * item.discount
        order.total = total
```

💡 **Hint:** "Extract calculation logic into 'calculateOrderTotal()' method"

🧩 **After:**
```fusion
void function handleOrder(Order order)
    if order.items.count > 0
        order.total = calculateOrderTotal(order.items)

float function calculateOrderTotal(List<Item> items)
    float total = 0.0
    for item in items
        total += item.price * item.quantity
        if item.discount > 0
            total -= item.price * item.discount
    return total
```

##### 3. Design Pattern Suggestions

Suggest applicable design patterns based on code structure.

💡 **Hint Examples:**
- "Consider using Strategy pattern for multiple payment methods"
- "This looks like a Factory pattern candidate"
- "Consider Singleton for DatabaseConnection class"
- "Observer pattern could simplify event handling here"

##### 4. Best Practice Enforcement

Suggest improvements based on programming principles.

**DRY (Don't Repeat Yourself)**
```fusion
// Detects duplicate code blocks
💡 Hint: "Duplicate code detected in 3 locations - extract to shared method"
```

**SOLID Principles**
```fusion
// Class with too many responsibilities
💡 Hint: "Class has 12 methods with different concerns - consider splitting (Single Responsibility Principle)"
```

**YAGNI (You Aren't Gonna Need It)**
```fusion
// Unused code detection
💡 Hint: "Method 'calculateFutureFeature()' is never called - remove if not needed"
```

#### Hint API (fusionlib.IDE)

```fusion
import fusionlib.IDE

// Analyze code and get suggestions
class CodeHints
    static List<Hint> analyzeFile(string filePath)
    static List<Hint> analyzeClass(string className)
    static List<Hint> analyzeFunction(string functionName)

// Hint types
Enum HintType
    ControlFlowSimplification
    ExtractMethod
    DesignPattern
    DRYViolation
    SOLIDViolation
    Performance
    Security

class Hint
    HintType type
    string message
    int lineNumber
    string suggestion
    string codeExample
```

---

## 🔓 Unsafe Mode Enhancements

### Bit Type & Assembly Support

**Status:** 📝 Proposed
**Purpose:** Enable absolute hardware control for low-level programming

**What:** Support for bit-level operations and inline assembly code for scenarios requiring maximum control and performance.

#### Use Cases

- **Direct hardware control** (PC, embedded systems, IoT, robotics)
- **Banking security systems** (hardware encryption modules)
- **Operating system development** (kernel, drivers)
- **Real-time systems** (fighter jets, spacecraft, medical devices)
- **Performance-critical code** (game engines, cryptography)

#### Bit Type

**Definition:** A primitive type representing a single bit (0 or 1)

🧩 **Example:**
```fusion
// Bit type declaration (unsafe mode only)
bit flag = 1
bit isEnabled = 0

// Bit manipulation
bit result = flag & isEnabled  // AND
bit result2 = flag | isEnabled // OR
bit result3 = flag ^ isEnabled // XOR
bit result4 = ~flag            // NOT

// Hardware register access
bit[8] statusRegister = readHardwareRegister(0x3F8)
statusRegister[3] = 1  // Set bit 3
writeHardwareRegister(0x3F8, statusRegister)
```

#### Bit Arrays

```fusion
// 8-bit register
bit[8] register = [0, 1, 0, 1, 1, 0, 1, 0]

// 32-bit integer as bit array
bit[32] flags = int32.toBits(0xDEADBEEF)

// Access individual bits
bit highBit = flags[31]
flags[0] = 1  // Set LSB
```

#### Assembly Code Support

**Inline Assembly:** Embed assembly directly in Fusion code

🧩 **Example:**
```fusion
// x86_64 assembly example
void function enableInterrupts()
    asm
        sti  // Set interrupt flag
    end asm

// ARM assembly example
int function addWithCarry(int a, int b)
    int result
    asm
        adds r0, r0, r1  // Add with status update
        mov result, r0
    end asm
    return result
```

#### Hardware Interface Classes

**Concept:** Encapsulate hardware-specific code in classes/interfaces

🧩 **Example:**
```fusion
// Abstract hardware interface
interface IHardwareController
    void function initialize()
    void function writeRegister(int address, byte value)
    byte function readRegister(int address)
    void function shutdown()

// PC serial port implementation
class SerialPortController implements IHardwareController
    private int baseAddress = 0x3F8

    public void function initialize()
        // Configure baud rate, parity, etc.
        writeRegister(baseAddress + 1, 0x00)  // Disable interrupts
        writeRegister(baseAddress + 3, 0x80)  // Enable DLAB
        writeRegister(baseAddress + 0, 0x03)  // Set divisor (low byte)
        writeRegister(baseAddress + 1, 0x00)  // Set divisor (high byte)
        writeRegister(baseAddress + 3, 0x03)  // 8N1 mode

    public void function writeRegister(int address, byte value)
        asm
            mov dx, address
            mov al, value
            out dx, al
        end asm

// Spacecraft thruster controller
class ThrusterController implements IHardwareController
    private int thrusterPort = 0x400

    public void function fireThruster(int thrusterId, int duration)
        // Safety checks
        if thrusterId < 0 or thrusterId > 15
            throw Error("Invalid thruster ID")

        // Set thruster bit
        bit[16] thrusterMask = 0
        thrusterMask[thrusterId] = 1
        writeRegister(thrusterPort, thrusterMask.toInt16())

        // Wait for duration (microseconds)
        sleep(duration)

        // Disable thruster
        writeRegister(thrusterPort, 0x0000)
```

#### Safety Considerations

**Unsafe mode required:**
```fusion
// Must be in unsafe block or unsafe file
unsafe
    bit[8] register = readPort(0x3F8)
    asm
        cli  // Disable interrupts (dangerous!)
    end asm
end unsafe
```

**Warning system:**
```
⚠️  Warning: Bit type used outside unsafe context
⚠️  Warning: Inline assembly may cause undefined behavior
⚠️  Warning: Direct hardware access requires elevated privileges
```

---

## 📊 Type System Enhancements

### Advanced Array Declaration Syntax

**Status:** 📝 Proposed
**Purpose:** Provide fine-grained control over array mutability and resizing

**What:** Extended array syntax using `[]` vs `()` to control element mutability and array resizing behavior.

#### Array Syntax Overview

| Syntax | Size | Elements | Use Case |
|--------|------|----------|----------|
| `type[]` | Flexible (can grow/shrink) | Mutable (can edit) | General-purpose dynamic arrays |
| `type[N]` | Fixed (cannot resize) | Mutable (can edit) | Fixed-size buffers, C-style arrays |
| `type()` | Flexible (can grow) | Immutable (read-only) | Append-only collections |
| `type(N)` | Fixed (cannot resize) | Immutable (read-only) | Constant lookup tables |

#### Detailed Examples

##### 1. Flexible Mutable Arrays `type[]`

Can grow/shrink, elements can be changed.

```fusion
string cars[] = ['Volvo', 'BMW', 'Toyota']

// Modify elements
cars[0] = 'Mercedes'  // OK

// Resize array
cars.add('Audi')      // OK - now 4 elements
cars.remove('BMW')    // OK - now 3 elements
cars.clear()          // OK - now 0 elements
```

##### 2. Fixed Mutable Arrays `type[N]`

Cannot resize, but elements can be changed.

```fusion
string cars[3] = ['Volvo', 'BMW', 'Toyota']

// Modify elements
cars[0] = 'Mercedes'  // OK

// Resize attempts fail
cars.add('Audi')      // ❌ Compile error: Cannot resize fixed array
cars.remove('BMW')    // ❌ Compile error: Cannot resize fixed array
```

🧩 **Use case:** C-style arrays, hardware buffers
```fusion
byte buffer[256] = [0, 0, 0, ...]  // Fixed 256-byte buffer
buffer[10] = 0xFF  // OK - modify element
```

##### 3. Flexible Immutable Arrays `type()`

Can grow (append-only), elements cannot be changed.

```fusion
string cars() = ('Volvo', 'BMW', 'Toyota')

// Modify elements fails
cars[0] = 'Mercedes'  // ❌ Compile error: Cannot modify immutable element

// Can append (grows)
cars.add('Audi')      // OK - now 4 elements

// Cannot remove
cars.remove('BMW')    // ❌ Compile error: Cannot remove from immutable array
```

🧩 **Use case:** Append-only logs, event streams
```fusion
string logMessages() = ()
logMessages.add("Application started")
logMessages.add("User logged in")
// Old logs cannot be modified or deleted
```

##### 4. Fixed Immutable Arrays `type(N)`

Cannot resize, elements cannot be changed.

```fusion
string cars(3) = ('Volvo', 'BMW', 'Toyota')

// Modify elements fails
cars[0] = 'Mercedes'  // ❌ Compile error: Cannot modify immutable element

// Resize fails
cars.add('Audi')      // ❌ Compile error: Cannot resize fixed array
```

🧩 **Use case:** Constants, lookup tables
```fusion
string dayNames(7) = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
int primes(10) = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)

// Read-only access
print(dayNames[0])  // OK: "Mon"
```

#### Syntax Disambiguation

**`()` on types vs function calls:**

```fusion
// Array declaration (type followed by ())
string names() = ('Alice', 'Bob')
int values(5) = (1, 2, 3, 4, 5)

// Function call (variable/function name followed by ())
void function greet()
    print("Hello")

greet()  // Function call - OK

// No ambiguity
string arr() = ()     // Empty immutable array
myFunction()          // Function call
```

**Rule:** If `()` follows a **type name** → array declaration. If `()` follows a **variable/function name** → function call.

#### Array Syntax API

```fusion
// Common operations on all array types

// Read access (all types)
string item = cars[0]

// Write access (only mutable: [], [N])
cars[0] = 'Mercedes'  // OK for [], [N]; Error for (), (N)

// Add (only flexible: [], ())
cars.add('Audi')      // OK for [], (); Error for [N], (N)

// Remove (only flexible mutable: [])
cars.remove('BMW')    // OK for []; Error for [N], (), (N)

// Size
int count = cars.length  // All types

// Iterate (all types)
for car in cars
    print(car)
```

#### Type Safety Examples

```fusion
// Compile-time enforcement
string mutable[] = ['A', 'B', 'C']
string immutable() = ('X', 'Y', 'Z')

mutable[0] = 'D'     // OK
immutable[0] = 'E'   // ❌ Compile error

void function processArray(string items[])
    items.add('new')  // OK - expects flexible mutable

processArray(mutable)    // OK
processArray(immutable)  // ❌ Type error: Cannot pass immutable() as mutable[]
```

---

## 🔧 IDE Module Enhancements

### Project Integration System

**Status:** 📝 Proposed
**Purpose:** Manage external API endpoints and data structure templates within the IDE

**What:** IDE features for importing, validating, and managing external API contracts and data schemas.

#### 1. Endpoint Management

**Purpose:** Track REST APIs, GraphQL endpoints, and service calls used by the application.

##### Features

**Import API specifications:**
- OpenAPI / Swagger JSON/YAML
- GraphQL schemas
- WSDL (SOAP services)
- Custom endpoint definitions

**Validation:**
- Ensure code calls match API contracts
- Detect type mismatches in request/response
- Warn about deprecated endpoints

🧩 **Example:**
```fusion
// Import API specification
import fusionlib.IDE

// Load OpenAPI spec
APISpec spec = ProjectIntegration.loadOpenAPI("./api/petstore.yaml")

// IDE validates this call against spec
void function fetchUser(int userId)
    // IDE knows this endpoint exists and requires int parameter
    HttpResponse response = Http.get("https://api.example.com/users/{userId}")

    // IDE validates response structure matches spec
    User user = response.parseJson<User>()
```

##### IDE Features

**Auto-complete endpoints:**
```fusion
Http.get("https://api.example.com/")
// IDE suggests: /users, /products, /orders (from imported spec)
```

**Endpoint browser panel:**
```
📁 Project Endpoints
  └─ 🌐 PetStore API (https://api.petstore.com)
      ├─ GET /pets
      ├─ POST /pets
      ├─ GET /pets/{id}
      └─ DELETE /pets/{id}
```

**Generate client code:**
```fusion
// IDE generates client class from OpenAPI spec
class PetStoreClient
    List<Pet> function getPets()
    Pet function getPet(int id)
    void function createPet(Pet pet)
    void function deletePet(int id)
```

#### 2. Data Structure Templates

**Purpose:** Manage JSON schemas, XML templates, database schemas, and data format contracts.

##### Supported Formats

- JSON Schema
- XML Schema (XSD)
- Database schemas (SQL DDL, ER diagrams)
- CSV column definitions
- Protocol buffers (.proto files)
- Avro schemas

🧩 **Example: JSON Schema Validation**

**Import schema:**
```json
// schemas/user.json
{
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "name": { "type": "string", "minLength": 1 },
    "email": { "type": "string", "format": "email" },
    "age": { "type": "integer", "minimum": 0, "maximum": 150 }
  },
  "required": ["id", "name", "email"]
}
```

**IDE integration:**
```fusion
import fusionlib.IDE

// Register schema
ProjectIntegration.registerSchema("User", "./schemas/user.json")

// IDE validates this class matches schema
class User
    int id
    string name
    string email
    int age  // IDE warns if type doesn't match schema

// IDE validates JSON parsing
string json = """{"id": 1, "name": "Alice", "email": "alice@example.com"}"""
User user = Json.parse<User>(json)  // IDE checks structure
```

#### 3. Template Library

**Purpose:** Store and reuse data format templates directly in code.

##### Store Templates as Comments

```fusion
/**
 * @template UserJSON
 * {
 *   "id": 0,
 *   "name": "",
 *   "email": "",
 *   "roles": []
 * }
 */

/**
 * @template ConfigXML
 * <config>
 *   <database>
 *     <host>localhost</host>
 *     <port>5432</port>
 *     <name>mydb</name>
 *   </database>
 * </config>
 */
```

##### IDE Features

**Insert template at cursor:**
```
Right-click → Insert Template → UserJSON
// Pastes template into code
```

**View template in sidebar:**
```
📁 Templates
  ├─ 📄 UserJSON
  ├─ 📄 ConfigXML
  └─ 📄 OrderRequest
```

**Validate against template:**
```fusion
// IDE compares this JSON to @template UserJSON
string userJson = """
{
  "id": 123,
  "name": "Bob"
  // ⚠️  Warning: Missing required field "email"
}
"""
```

#### 4. Database Schema Integration

**Purpose:** Import database schemas and generate model classes.

🧩 **Example:**
```fusion
import fusionlib.IDE

// Import database schema
DatabaseSchema schema = ProjectIntegration.importDatabaseSchema(
    "postgresql://localhost:5432/mydb"
)

// IDE generates classes from tables
// Auto-generated from 'users' table:
class UserModel
    int id          // PRIMARY KEY
    string name     // VARCHAR(100) NOT NULL
    string email    // VARCHAR(255) UNIQUE
    DateTime created // TIMESTAMP DEFAULT NOW()
```

**IDE validation:**
```fusion
// IDE warns if query doesn't match schema
string sql = "SELECT id, name, invalid_column FROM users"
// ⚠️  Warning: Column 'invalid_column' does not exist in table 'users'
```

#### 5. ProjectIntegration API

```fusion
// Module: fusionlib.IDE

class ProjectIntegration
    // === API Endpoints ===
    static APISpec loadOpenAPI(string path)
    static APISpec loadGraphQL(string path)
    static void registerEndpoint(string name, string url, HttpMethod method)
    static List<Endpoint> getAllEndpoints()

    // === Data Schemas ===
    static void registerSchema(string name, string schemaPath)
    static Schema getSchema(string name)
    static bool validateAgainstSchema(object data, string schemaName)
    static void generateClassFromSchema(string schemaName, string outputPath)

    // === Templates ===
    static void registerTemplate(string name, string content)
    static string getTemplate(string name)
    static List<Template> getAllTemplates()

    // === Database Integration ===
    static DatabaseSchema importDatabaseSchema(string connectionString)
    static void generateModelsFromDatabase(string connectionString, string outputPath)
    static void validateQuery(string sql, string databaseName)

Enum HttpMethod { GET, POST, PUT, DELETE, PATCH }

class Endpoint
    string name
    string url
    HttpMethod method
    Schema requestSchema
    Schema responseSchema

class Schema
    string name
    string format  // "json", "xml", "csv", etc.
    string content
    bool function validate(object data)

class Template
    string name
    string content
    string description
```

---

## ⚙️ Compiler Infrastructure Enhancements

### Symbol-ID System

**Status:** 📝 Proposed
**Purpose:** Enable stable refactoring and cross-language interoperability

**What:** Internal symbol referencing using hashed IDs instead of text names, with configurable per-project or per-class activation.

#### How It Works

**Traditional approach (name-based):**
```fusion
class UserService
    void function createUser(string name)

// Renaming requires changing everywhere it's used
// 50+ files might reference "createUser"
```

**Symbol-ID approach (ID-based):**
```
Internal representation:
- Symbol: createUser → ID: @A1B2C3D4
- Symbol table maps: @A1B2C3D4 → "createUser"
- Renaming updates only the symbol table
```

#### Symbol Table File

**Example: `symbols.fusion`**
```
// Auto-generated symbol table
@A1B2C3D4 = class UserService
@E5F6G7H8 = function createUser
@I9J0K1L2 = function deleteUser
@M3N4O5P6 = interface IAuthService
@Q7R8S9T0 = enum UserRole
```

**Internal compilation:**
```fusion
// Developer writes:
class UserService
    void function createUser(string name)

// Compiler stores:
class @A1B2C3D4
    void function @E5F6G7H8(string name)
```

#### Benefits

##### 1. Instant Refactoring

**Rename function:**
```
// Change symbol table only
@E5F6G7H8 = function createUser → @E5F6G7H8 = function registerUser

// All code automatically uses new name
// No source file changes needed
```

##### 2. ABI-Safe Linking

**Backend compilation:**
```c
// C backend links to stable ID, not name
void userservice_A1B2C3D4_E5F6G7H8(char* name) {
    // Implementation
}
```

**Renaming doesn't break compiled libraries:**
```
Old version: createUser → @E5F6G7H8
New version: registerUser → @E5F6G7H8
Binary compatibility maintained!
```

##### 3. Cross-Language Interoperability

**Python calling Fusion:**
```python
# Python imports using stable IDs
from fusion_lib import symbol_E5F6G7H8 as create_user

create_user("Alice")
# Works even if Fusion renames the function
```

##### 4. Database-Like Symbol Management

```fusion
// Query symbols
List<Symbol> symbols = SymbolTable.findAll("*User*")
// Returns: UserService, createUser, deleteUser, UserRole

// Symbol metadata
Symbol sym = SymbolTable.get("@E5F6G7H8")
print(sym.name)           // "createUser"
print(sym.type)           // "function"
print(sym.references)     // 47 locations
print(sym.definedIn)      // "UserService.fusion:23"
```

#### Configuration

**Enable/disable per project:**
```fusion
// fusion-config.json
{
  "symbolIdSystem": true,
  "symbolTableFile": "./symbols.fusion"
}
```

**Enable/disable per class:**
```fusion
// Enable for this class
@symbolId(enabled: true)
class UserService
    // All symbols in this class use IDs

// Disable for this class
@symbolId(enabled: false)
class LegacyCode
    // Uses traditional name-based approach
```

#### Symbol ID Generation

**Hashing algorithm:**
```
ID = SHA256(fullyQualifiedName + salt)[0:8]

Examples:
- "fusion.auth.UserService.createUser" → @A1B2C3D4
- "fusion.auth.UserService.deleteUser" → @I9J0K1L2
```

**Collision handling:**
```
If hash collision detected:
- Append sequence number: @A1B2C3D4_1, @A1B2C3D4_2
```

#### IDE Support

**Symbol browser:**
```
📁 Symbol Table
  ├─ @A1B2C3D4 → UserService (class)
  ├─ @E5F6G7H8 → createUser (function) [47 refs]
  ├─ @I9J0K1L2 → deleteUser (function) [12 refs]
  └─ @M3N4O5P6 → IAuthService (interface) [8 refs]
```

**Refactoring:**
```
Right-click createUser → Rename → registerUser
// IDE updates symbol table only
// Shows: "47 references will use new name automatically"
```

#### Limitations & Tradeoffs

**Pros:**
- Instant, safe refactoring
- ABI stability across versions
- Easier cross-language linking
- Centralized symbol management

**Cons:**
- Symbol table file must be maintained
- Debugging shows IDs instead of names (IDE must translate)
- Requires tooling support
- Adds complexity to build system

**When to use:**
- Large projects with frequent refactoring
- Libraries with public APIs (ABI stability)
- Cross-language interop projects
- Enterprise codebases with strict versioning

**When NOT to use:**
- Small scripts/prototypes
- Single-developer projects
- Legacy codebases without tooling support


user added note: IDE should not show the ID in any case. IDE shows a rendered layers including the perfered coding preference (indention, {}, keywords) as part of Fusion core functonality.
when edditng the raw file format then it will show the ID's like @A1B2C3D4_1 and an internal format that uses {}.
Symbole table is regenated when rebuild build and is used while editing a file gets automatically updated.

---

User added content - Copied from chat gpt to be reviewd.
# Core & Additional Packages — Fusion vs Other Languages

Most major languages ship with similar core packages (strings, math, collections,
IO, networking, data formats, concurrency). Fusion’s standard library exceeds
these by integrating 22 modules:
Core (5), Additional (12), IDE/Tooling (5).

Fusion matches or exceeds Java, Python, Go, Rust in:
• Networking (TCP/UDP/HTTP/WebSocket)
• Data formats (JSON, XML, YAML, CSV, Markdown, INI)
• Concurrency (threads, goroutines, channels)
• Graphics, GUI, Audio
• Crypto, Database, Web servers
• Reflection, Testing, Diagnostics, Documentation generation

Fusion also provides unique capabilities:
• Multi-syntax support (indent, braces, keywords)
• Multi-backend execution (native, bytecode, interpreter)
• 3-tier memory system (GC, Smart, Raw)
• Auto-thread locking and deadlock detection
• Built-in multi-language compilers (fusionlib.Lang)
• IDE integration module (LSP, formatter, syntax generator)

Missing or planned features:
• Regex module - i think we did dis one already.
• Physics engine module
• DataFrame/Numerics modules (Pandas/NumPy equivalents)
• AI/ML expansion
• Enhanced DateTime utilities

here is an updated summary from chat gpt to be reviewed as well

Here is the **clean, concise, ready-to-paste section** for **FutureFeatures.md**, following your structure and style.
It fits naturally into your existing document and uses wording consistent with the rest of the Fusion spec.


# 🌐 Additional Specialized Packages (Not Core – Optional Ecosystem Modules)

These packages extend Fusion for domain-specific or high-performance workloads.
They are **not part of the core 22 modules**, but should be available as **separate optional packages** within the Fusion ecosystem.


## ✔ Regex Module (Planned)

**Status:** Proposed
**Module:** `Fusion.Regex`
**Purpose:** Provide full regular-expression capabilities without bloating the Core module.

**Features:**

* Traditional regex engine
* Optional Fluent/Builder API
* Pattern validation
* Find/replace helpers
* Extraction utilities

**Reason:** Regex systems grow large and should stay modular.


## 🎮 Game Engine – Separate Domain Package

**Status:** Proposed (NOT part of standard library)
**Module:** `Fusion.GameEngine` (external / community package)

Fusion should NOT ship a full game engine inside the core language because it is large, domain-specific, and opinionated.

Fusion itself only provides:

* Graphics
* Audio
* Windowing
* Input
* Shader system
* Math

A complete engine (scenes, assets, physics, ECS, animation, prefab system, etc.) belongs in a **separate ecosystem package**, not inside Core.


## ⚙ Physics Library

**Status:** Proposed
**Module:** `Fusion.Physics`
**Purpose:** Physics simulation tools useful for science, engineering, robotics, and optional game development.

**Features:**

* Rigid-body physics
* Collision detection
* Forces, impulses, friction, gravity
* 2D/3D vector integration
* Raycasting utilities

**Reason:** Powerful but niche — belongs outside the core standard library.


## 🧩 ECS Module (Entity Component System)

**Status:** Proposed
**Module:** `Fusion.ECS`
**Purpose:** Data-oriented architecture for high-performance simulations and optional game tooling.

**Concepts:**

* **Entity** → ID only
* **Component** → Data attached to entities
* **System** → Logic operating on all entities with matching components

**Use Cases:**

* Game engines
* Large-scale simulations
* Parallelizable workloads
* Robotics and behavior systems


## 🎨 Shader Builder Tools

**Status:** Proposed
**Module:** `Fusion.Graphics.Shaders`
**Purpose:** Simplify GPU programming by providing structured tools for shader creation and validation.

**Features:**

* Vertex / Fragment / Compute shader builders
* Uniform & resource binding API
* Code generation from templates
* Syntax validation
* Cross-platform shader pipeline helpers

**Use Cases:**
Graphics, visualization, tooling, rendering pipelines.


## 🔢 NumPy-Style Numerics Package

**Status:** Proposed
**Module:** `Fusion.Numerics`
**Purpose:** High-performance numeric and scientific computing.

**Features:**

* Multi-dimensional arrays
* Vectorized math
* Linear algebra (matrices, decomposition, solvers)
* FFT & numeric transforms
* Broadcasting rules

**Use Cases:**
Scientific computing, analytics, simulation, ML preprocessing.


## 📊 Pandas-Style DataFrames Package

**Status:** Proposed
**Module:** `Fusion.DataFrames`
**Purpose:** Table-based data manipulation similar to Pandas.

**Features:**

* DataFrame structure
* CSV/JSON/SQL loading
* Filtering, grouping, merging
* Sorting, aggregation
* Time-series support

**Use Cases:**
Finance, analytics, reporting, ML pipelines, ETL jobs.


# ✔ Summary

These packages extend Fusion without affecting the minimal core.
All of them are **modular**, **opt-in**, and **domain-specific**, designed to grow the Fusion ecosystem cleanly.




---

**End of Future Features Document**

**Status:** Documented, pending implementation
**Next Review:** After MVP compiler completion
**Last Updated:** 2025-11-16
