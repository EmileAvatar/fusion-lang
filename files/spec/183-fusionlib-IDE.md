[< 182 fusionlib-Extended](182-fusionlib-Extended.md) | [Index](index.md) | [190 Callbacks >](190-Callbacks.md) <!-- nav -->

# 183 fusionlib IDE

Contents: [Reflection Module (fusionlib.Reflection)](#reflection-module-fusionlibreflection) | [Test Module (fusionlib.Test)](#test-module-fusionlibtest) | [Diagnostics Module (fusionlib.Diagnostics)](#diagnostics-module-fusionlibdiagnostics) | [DocWiki Module (fusionlib.DocWiki)](#docwiki-module-fusionlibdocwiki) | [Library Summary](#library-summary)

**Status:** [DESIGN] designed one at a time in Task 43; the core libraries: [181](181-fusionlib-Core.md),
the additional ones: [182](182-fusionlib-Extended.md)

## IDE & Development Libraries

Description: Tools specifically designed for development workflow, testing, debugging, documentation, and IDE integration.

---

### Reflection Module (fusionlib.Reflection)

Description: Runtime type introspection and dynamic code execution.

**Features**:
* Runtime type inspection
* Method invocation (call methods dynamically)
* Property access (get/set dynamically)
* Attribute/annotation reading
* Type creation at runtime
* Assembly loading
* Code generation (emit IL/bytecode)
* Serialization and deserialization
* Duck typing support
* Dynamic proxy generation

**IDE Integration**:
* Powers autocomplete and IntelliSense
* Enables runtime code analysis
* Supports dynamic plugin systems

---

### Test Module (fusionlib.Test)

Description: Comprehensive testing framework with IDE integration.

**Features**:
* Unit testing framework
* Assertions (assertEquals, assertTrue, etc.)
* Test fixtures and setup/teardown
* Test suites and runners
* Mocking and stubbing
* Code coverage analysis
* Benchmarking tools
* Performance testing
* Parameterized tests
* Test reporting (HTML, XML, JSON)

**IDE Integration**:
* Test runner UI
* Real-time test execution
* Coverage visualization
* Failure navigation

---

### Diagnostics Module (fusionlib.Diagnostics)

Description: Profiling, logging, and debugging utilities.

**Features**:
* Logging framework (levels: debug, info, warn, error)
* Performance profiling
* CPU profiling
* Memory profiling
* Execution tracing
* Stopwatch and timing
* Performance counters
* Event logging
* Crash reporting
* Debug output and breakpoints

**IDE Integration**:
* Profiler visualization
* Memory leak detection
* Performance hotspot highlighting
* Real-time log viewing

---

### DocWiki Module (fusionlib.DocWiki)

Description: Automatic documentation generation and wiki creation during background compilation.

**Two forms** (user, 2026-11-12 - FEATURES 43.8):

| Form | What it is | Used for |
|---|---|---|
| A separate app | Runs alongside the developer's app; not part of the app's code | Making a doc wiki by hand or from sources |
| Built into the app (`Fusion.DocWiki`) | The app's own implementation | A wiki for the developer's application - e.g. showcasing the Fusion language, or another app's library |

What it can document:
- Fusion code - from its comments and signatures ([131 AutoDocs](131-AutoDocs.md))
- Other languages, and DLL files - even ones written in another language
- A custom wiki - written by hand, no code behind it


**Features**:
* Automatic documentation extraction from code comments
* Real-time wiki generation during IDE background compilation
* API reference generation from function signatures and types
* Markdown and HTML output formats
* Cross-referencing of types, methods, and modules
* Custom documentation templates
* Code example extraction and formatting
* Version history and changelog generation
* Search index creation
* Export to static site generators (Jekyll, Hugo, Docusaurus)

**Documentation Comment Formats**:
```fusion
/// Single-line documentation comment

/**
 * Multi-line documentation comment
 * Supports markdown formatting
 */

/**
 * Calculates the factorial of a number
 * @param n The input number (must be non-negative)
 * @return The factorial of n
 * @example
 *   int result = factorial(5)  // Returns 120
 */
int function factorial(int n)
    if n <= 1
        return 1
    End if
    return n * factorial(n - 1)
End function
```

**Supported Annotations**:
* `@param` - Parameter description
* `@return` - Return value description
* `@throws` - Exception descriptions
* `@example` - Code examples
* `@deprecated` - Mark as deprecated
* `@since` - Version information
* `@see` - Cross-references

**IDE Integration**:
* Real-time preview in IDE sidebar
* Hover tooltips with documentation
* Automatic wiki updates on file save
* Documentation coverage metrics
* Broken link detection
* IntelliSense powered by doc comments

**Example Usage**:
```fusion
import Fusion.DocWiki

/// Main application entry point
/// @param args Command-line arguments
void function main(string... args)
    // Generate documentation for the project
    DocWiki wiki = DocWiki.create("MyProject")
    wiki.setVersion("1.0.0")
    wiki.addSource("src/")
    wiki.setOutputFormat(DocFormat.HTML)
    wiki.generate("docs/")

    print("Documentation generated successfully!")
    print("Open docs/index.html to view")
End function

/**
 * Vector3 represents a 3D vector
 * @example
 *   Vector3 pos = Vector3(10.0, 5.0, 0.0)
 *   float length = pos.magnitude()
 */
class Vector3
    public float x
    public float y
    public float z

    /// Calculates the magnitude (length) of the vector
    /// @return The Euclidean length of the vector
    float function magnitude()
        return Math.sqrt(x * x + y * y + z * z)
    End function
End class
```

---

## Library Summary

**Quick Import Reference**:
```fusion
// Core Libraries (use in 90% of programs)
import Fusion.Core
import Fusion.Math
import Fusion.Collections
import Fusion.Threading
import Fusion.IO

// Networking & Data
import Fusion.Net
import Fusion.Data

// System Integration
import Fusion.System
import Fusion.Lang
import Fusion.Languages

// Multimedia
import Fusion.GUI
import Fusion.Graphics
import Fusion.Audio

// Advanced
import Fusion.Crypto
import Fusion.Database
import Fusion.Web
import Fusion.AI

// IDE & Development
import Fusion.Reflection
import Fusion.Test
import Fusion.Diagnostics
import Fusion.DocWiki
```

Each module's API is designed in Task 43 (43.6: every module's name first). The names follow the
`Fusion` namespace (D.136, Task 57); `Fusion.Lang` / `Fusion.Languages` next to the language modules
`Lang.<language>.Fusion` (D.121, D.137) - to settle in Task 49 ("Open").

**Module Count**: 21 total (5 Core + 12 Additional + 4 IDE)

[< 182 fusionlib-Extended](182-fusionlib-Extended.md) | [Index](index.md) | [190 Callbacks >](190-Callbacks.md) <!-- nav -->
