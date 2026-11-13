[< 000 Overview](000-Overview.md) | [Index](index.md) | [011 IDEProjects >](011-IDEProjects.md) <!-- nav -->

# 010 IDE Module

**Status:** idea - no task; editor support is FEATURES Task 36; the IDE libraries as designed: [183](../spec/183-fusionlib-IDE.md)

Contents: [Proposed New Modules](#proposed-new-modules) | [1. fusionlib.IDE - IDE Integration Module (22nd Module)](#1-fusionlibide---ide-integration-module-22nd-module) | [Complete fusionlib.IDE Module API](#complete-fusionlibide-module-api)

## Proposed New Modules

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


## Complete fusionlib.IDE Module API

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

[< 000 Overview](000-Overview.md) | [Index](index.md) | [011 IDEProjects >](011-IDEProjects.md) <!-- nav -->
