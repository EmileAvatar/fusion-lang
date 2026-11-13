# 🔮 Fusion Language - Future Features & Enhancements

**Status:** Planning / Not Yet Implemented
**Last Updated:** 2026-10-07
**Purpose:** Track proposed features and enhancements for post-MVP implementation

> **Read `files/FutureFeaturesCaution.md` first.** The first goal is a simple working language;
> everything in this document is a menu of possibilities, not a commitment - some features
> will be built, some will change, and some will never be added. Core-language work (Task 18
> in `files/taskSummary2.md`) comes before any of it.

---

## Moved to files/future/ (Task 51.5b)

| Old section | Now in |
|---|---|
| Proposed New Modules | [future/010-IDEModule.md](future/010-IDEModule.md) |
| Complete fusionlib.IDE Module API | [future/010-IDEModule.md](future/010-IDEModule.md) |
| IDE Module Enhancements | [future/011-IDEProjects.md](future/011-IDEProjects.md) |
| IDE Code Quality Overlays & Hints | [future/012-IDEOverlays.md](future/012-IDEOverlays.md) |
| Feature 5: Naming Quality Analysis (Dictionary Builder) | [future/013-IDEOverlays2.md](future/013-IDEOverlays2.md) |
| Configuration Management (Project-Level) | [future/014-IDEOverlaySettings.md](future/014-IDEOverlaySettings.md) |
| Core Concept | [future/015-WebServers.md](future/015-WebServers.md) |
| Overview | [future/000-Overview.md](future/000-Overview.md) |
| Implementation Priority | [future/000-Overview.md](future/000-Overview.md) |
| Related Files | [future/000-Overview.md](future/000-Overview.md) |
| Implementation Checklist | [future/000-Overview.md](future/000-Overview.md) |
| Timeline Estimate | [future/000-Overview.md](future/000-Overview.md) |
| Success Criteria | [future/000-Overview.md](future/000-Overview.md) |
| Discussion Points | [future/000-Overview.md](future/000-Overview.md) |
| Settings System - Module Placement | [future/020-Settings.md](future/020-Settings.md) |
| Configuration File Formats | [future/020-Settings.md](future/020-Settings.md) |
| Updated Module Count | [future/030-LibraryLayout.md](future/030-LibraryLayout.md) |
| Updated Standard Library Organization | [future/030-LibraryLayout.md](future/030-LibraryLayout.md) |
| fusionlib: Every Planned Module (names only) | [future/030-LibraryLayout.md](future/030-LibraryLayout.md) |
| Additional Ideas (Lower Priority) | [future/030-LibraryLayout.md](future/030-LibraryLayout.md) |
| Regex Fluent API | [future/031-Regex.md](future/031-Regex.md) |
| Regex Module (Planned) | [future/031-Regex.md](future/031-Regex.md) |
| Game Engine – Separate Domain Package | [future/032-DomainPackages.md](future/032-DomainPackages.md) |
| Physics Library | [future/032-DomainPackages.md](future/032-DomainPackages.md) |
| ECS Module (Entity Component System) | [future/032-DomainPackages.md](future/032-DomainPackages.md) |
| Shader Builder Tools | [future/032-DomainPackages.md](future/032-DomainPackages.md) |
| NumPy-Style Numerics Package | [future/032-DomainPackages.md](future/032-DomainPackages.md) |
| Pandas-Style DataFrames Package | [future/032-DomainPackages.md](future/032-DomainPackages.md) |
| Currency Module (Financial / FX Conversion) | [future/033-Currency.md](future/033-Currency.md) |
| Fixed-Point Decimal Type & `Currency` Sugar (Financial / Money Precision) | [future/033-Currency.md](future/033-Currency.md) |
| Data Formats Module: JSON, XML, TOML, YAML, INI, MD | [future/034-DataFormats.md](future/034-DataFormats.md) |
| HIDL Library: Hardware Testing Ideas from Maia | [future/035-HIDL.md](future/035-HIDL.md) |
| Cross-Language Compilation Support | [future/040-CrossLanguage.md](future/040-CrossLanguage.md) |
| Future Self-Hosting Considerations | [future/040-CrossLanguage.md](future/040-CrossLanguage.md) |
| Multi-Import & Parameter Syntax | [future/050-Imports.md](future/050-Imports.md) |
| Enhanced Comment Support | [future/060-Comments.md](future/060-Comments.md) |
| Feature 3: Comment Style Summary | [future/060-Comments.md](future/060-Comments.md) |
| Feature 2a: Language-Specific Syntax Highlighting in `'''` Blocks | [future/061-CommentHighlighting.md](future/061-CommentHighlighting.md) |

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
class Sortable<T> where T : Comparable, Cloneable
    private List<T> items

    public void function sort()
        items.sort()  // T implements Comparable
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

### Implementation Strategy Tiers & the Configurable-Strategy Philosophy

**Status:** 📝 Proposed (vision/framing, not a scoped feature)
**Source:** User-provided notes (`Notes/03/Fusion_C_Rust_and_Implementation_Strategies.md`,
reviewed 2026-09-27) - written with limited knowledge of Fusion's current implementation,
so treat this as philosophy/direction, not an accurate description of what exists today.

**The central idea, stated more sharply than Fusion's philosophy is currently written down
anywhere else:**

> Don't make the *meaning* of Fusion configurable. Make the *implementation strategy*
> configurable.

A program's semantics stay stable; what changes per project is *how* that meaning gets
realized - memory strategy, safety level, compilation target, runtime footprint. This is
the same idea CLAUDE.md's "Core Concept" and this document's various per-project knobs
(`fusion.toml`'s `[safety]`/`[backend]`, the decimal/Currency precision config, the Feature
Registry concept explored in conversation) already point at individually - this framing is
worth adopting as the one sentence that explains *why* all of those exist, rather than each
looking like an unrelated configuration knob.

**Proposed escalation tiers** - not separate languages, one Fusion, with progressively lower
guardrails available when a project genuinely needs them:

```text
Application Fusion  - the default: safe memory, automatic resource management, high-level
                       collections, concurrency safety, productive defaults. Aimed at
                       covering roughly 70-90% of ordinary development, with 95% as a
                       long-term aspiration - the "everyday" tier most projects never leave.
        |
Systems Fusion       - explicit allocation, deterministic destruction, manual memory where
                       required, direct OS interaction. For OS components, high-performance
                       services, storage/networking systems, game engines.
        |
Embedded Fusion      - no GC, no runtime, fixed memory, predictable execution, direct
                       peripheral access. For devices with no OS, fixed memory budgets, and
                       hard determinism requirements.
        |
Kernel Fusion        - explicit hardware access, controlled unsafe operations, strict
                       compiler checks, direct memory manipulation, interrupt/device
                       interaction.
        |
Assembly / Hardware  - inline/integrated assembly as the final escape hatch when even
                       Kernel Fusion's control isn't enough (CPU-specific instructions, boot
                       code, SIMD, cryptographic primitives) - see "Bit Type & Assembly
                       Support" below, which already covers this tier concretely.
```

The stated principle: **"easy by default, but never a dead end"** - a developer starts in
Application Fusion and only descends a tier when the project actually demands it, without
switching languages or relearning semantics to do so.

**A distinctive idea worth keeping even if the tier model above changes:** tagging `unsafe`
blocks with a numbered design-rule reference connecting the code to *why* it's unsafe, not
just what it does:

```fusion
###<1042> Hardware buffer must remain valid
###<1043> DMA operation requires exclusive ownership

unsafe
{
    pointer = address(...)
    memory.write(pointer, value)
}
```

The idea is that `###<NNNN>` numbers key into a project's design/engineering-rule
documentation, so a reviewer (or a future maintainer) can trace an unsafe block back to the
actual constraint that justified it, not just trust a comment. Needs real design before it's
buildable (where does the rule registry live, is the numbering compiler-checked or purely
conventional) but it's a genuinely useful angle on "unsafe should be explicit and
*explained*, not just contained."

**Why this stays in "Unsafe Mode Enhancements" specifically:** everything below Application
Fusion in the tier list is, functionally, a larger version of what this section's "Bit Type
& Assembly Support" already proposes - this framing gives that existing content a home in a
bigger picture rather than treating hardware/assembly access as an isolated feature.

---

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

> **Replaced (2026-10-31, Decisions.md D.064):** read-only is `const`, a size limit is
> `fixed(n)` - `type()` / `type(N)` are not used.

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

### Mutable vs. Fixed Strings, Templated Fixed Strings & String Pooling

> **Decided since (Task 29, Decisions.md D.059, D.064):** no `m"` / `f"` prefixes - a plain
> string can change, `const string` never does; templates are `template string`; `fixed(n)`
> now means a maximum size.

**Status:** 📝 Proposed
**Priority:** Medium (a real, common source of bugs in other languages - accidental
mutation of a string another part of the program still holds a reference to - but not
blocking anything currently built)
**Source:** User request (2026-09-27) - also logged as **Task 17** in `files/taskSummary2.md`

#### Mutable strings (default) vs. fixed/immutable strings

```fusion
string mutable = m"mutable string"   // explicit mutable prefix
string mutable2 = "mutable string"   // same thing - the m prefix is implicit/optional
                                      // on a plain string literal

string fixedString1 = f"fixed string, not mutable"
```

`m` and plain (no prefix) both mean "ordinary mutable string" - `m"..."` exists purely so
`m"..."` and `f"..."` read symmetrically side by side, not because a prefix is required.
`f"..."` marks the value as **fixed**: once created, nothing about that specific string
value can change. This is the same idea as Java's/C#'s immutable `String`, and the same
prefix-on-a-string-literal pattern Python (`f"..."`, `r"..."`, `b"..."`) and C# (`$"..."`)
already use, just applied to mutability instead of formatting/rawness.

**Calling a method on a fixed string doesn't mutate it - it returns a new value:**

```fusion
mutable = "changed string"
printf(fixedString1.ToUpper())

// Output:
// mutable is now "changed string"
// FIXED STRING, NOT MUTABLE      <- fixedString1 itself is completely unchanged after this
```

So "fixed" describes the variable's own stored value, not a restriction on what you can
compute from it - `.ToUpper()` still works, it just can't be the *same* string object
afterward.

#### Templated fixed strings - the more novel part

A fixed string containing positional placeholders (`{@1}`, `{@2}`, ...) can be stored once
and then **invoked later, like a function, with different arguments each time**:

```fusion
string fixedString2 = f"fixed string but with {@1} with changable value {@2}. not mutable"

printf(fixedString2("inserted text", "second inserted text").ToUpper())
// FIXED STRING WITH INSERTED TEXT WITH CHANGABLE VALUE SECOND INSERTED TEXT. NOT MUTABLE
```

**This is a real, new capability, not just applying existing syntax to a variable.**
Fusion's `{@1}`/`{@2}` positional interpolation already exists today, but it resolves
*immediately*, at the point the expression is evaluated (e.g. inside a `print(...)` call,
using the arguments given at that call site). What's proposed here is different: the
placeholders stay **unresolved** inside the stored value, and `fixedString2` itself becomes
a reusable, callable template - closer to a compiled format string / a closure over its own
placeholder slots than to today's immediate interpolation. This needs real design before
it's buildable, not just wiring up existing syntax:
- What is `fixedString2`'s actual type - still `string`, or does a placeholder-bearing
  fixed string need a distinct type (e.g. something template/closure-shaped) that happens
  to also support `.ToUpper()`-style chaining once called?
- What happens if the placeholders aren't contiguous (`{@1}` and `{@3}` but no `{@2}`), or
  the call is given the wrong number of arguments - compile-time error (the placeholder
  count is known at the point `f"..."` was written) or runtime error?
- Does this require a new AST node distinct from the existing `InterpolatedStringExpr`, or
  can that node grow a "deferred" mode?

#### String pooling - opt-in, not default

```text
Strings are not pooled by default. Each string is stored where it's declared - no implicit
interning/deduplication of equal string values.
```

String pooling (reusing one underlying storage location for multiple equal string values,
as Java and Python both do automatically for at least some strings) is proposed as an
**opt-in project setting**, not a default optimization:

```toml
# fusion.toml
[strings]
pooling = false   # default - matches "no implicit behavior the developer didn't ask for"
```

**Explicit guidance from the request:** only turn pooling on *after profiling* shows it's
actually worth it for a given application - i.e. after confirming a large volume of
repeated/duplicate strings are being created and that reusing storage would meaningfully
help. Pooling isn't free (it needs a lookup/hash step on string creation, and changes the
lifetime story for anything sharing pooled storage), so defaulting it off and treating it as
a measured, deliberate optimization - not a silent language behavior - fits Fusion's general
"don't guess, let the project decide" philosophy already established for `fusion.toml`.

#### Security: strings are the wrong type for secrets

Explicitly flagged as unsuitable for passwords/cryptographic material: a plain string
(pooled or not) can end up copied or retained in memory for longer than intended, and can't
be reliably zeroed out once no longer needed - a well-known real problem in other managed
languages (Java's own security guidance recommends `char[]` over `String` for passwords for
exactly this reason - a `String` can't be scrubbed, and if it's ever pooled/interned, a
copy of the secret can persist in memory well past the point the program considers it
"done" with it).

**Proposed answer: a dedicated secure-storage type in a future `fusionlib.Crypto` module**
(Crypto is already one of the 21 envisioned stdlib modules) - explicitly never pooled,
intended to store encrypted-at-rest secrets rather than plain fixed/mutable strings. Marked
explicitly as **far-future** - this depends on the Crypto module existing at all, which
depends on `import` having parser support in the first place (currently none).

**Success Criteria:**
- Mutable strings behave exactly as they do today (no regression - `m"..."` and a plain
  literal are equivalent)
- `f"..."` strings are provably never mutated in place - every "mutating" method returns a
  new value
- A templated fixed string can be invoked multiple times with different arguments without
  ever changing the stored template
- String pooling is off by default and has zero effect on program behavior when disabled;
  enabling it changes memory reuse only, never observable string equality/behavior
- Passwords/secrets have a documented, explicitly-recommended alternative to plain strings

**Deliverables (once scoped and approved):**
- `m"..."`/`f"..."` lexer and parser support
- Semantic rules for fixed-string immutability and templated-fixed-string calling
- `[strings]` `fusion.toml` section (`pooling`)
- Cross-reference from `fusionlib.Crypto`'s eventual design to the secure-storage need
  identified here

---

## ⚙️ Compiler Infrastructure Enhancements

### Symbol-ID System

**Status:** 📝 Proposed - far future. This depends on infrastructure Fusion doesn't have
any of yet: multiple source files, a module/class system, and a package manager at minimum
(`import` itself has no parser support today - confirmed by source search). Realistically
post-self-hosting territory, not a near-term item. Written down so the idea isn't lost, not
because it's close to being scoped.
**Purpose:** Enable stable refactoring and cross-language interoperability

**What:** Internal symbol referencing using hashed IDs instead of text names, with configurable per-project or per-class activation.

**Update (2026-09-27):** a second, more detailed pass at this same idea arrived via user
notes (`Notes/03/Fusion_Compiler_Symbol_Index_System.md`, written with limited knowledge of
Fusion's current implementation). It fixes a real logical problem in the design below and
adds mechanisms worth folding in - see "Rename-Stability Fix" and "Distributed Refactoring"
after the original design.

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
```toml
# fusion.toml (corrected 2026-09-27 - Fusion's real project config format is TOML,
# decided in Task 12.12; the original JSON example predates that decision)
[symbols]
enabled = true
symbol_table_file = "./symbols.fusion"
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

**Rename-Stability Fix (2026-09-27) - this hashing scheme has a self-defeating flaw:**
hashing the *fully qualified name* means renaming a symbol changes its name, which changes
the hash input, which changes the ID - exactly the thing this system exists to prevent. A
rename would silently break every reference it was supposed to protect. The fix, taken from
the newer note referenced above: generate the ID **once, at creation, independent of the
name entirely** (a random or creation-time-ordered identifier, e.g. ULID-style
`01J8ZK4M2Q...`), and store the current name as a separate, mutable field that changes
freely on rename. The ID itself never derives from anything that can change - not from the
name, not from the file path, not from anything a refactor would touch. This is a
correction to the mechanism, not to the goal - the SHA256 approach above should not be
implemented as designed; the ID-assigned-at-creation approach below should be, if this ever
gets built.

#### Distributed Refactoring (2026-09-27 addition)

The newer note above adds mechanisms this design didn't originally have, worth keeping
together with it rather than as a separate proposal:

- **Persistent, regenerable database** - `.fusion/symbols.db` (plus dependency/reference/
  type indexes) instead of a single flat `symbols.fusion` file, so large projects don't
  reload and re-derive everything on every compiler invocation. Source remains the single
  source of truth; the database can always be deleted and rebuilt from it.
- **Symbol lifecycle rules**, missing from the original design:
  - **Renamed/moved:** ID unchanged, only name/path/file change.
  - **Copied:** the copy gets a **new** ID - a copy is a new logical entity, not the same
    one appearing twice.
  - **Deleted:** the ID is tombstoned, never reused - so stale references (old branches,
    cached IDE state) get a clear "this symbol was deleted" diagnostic instead of silently
    binding to an unrelated later symbol that happened to reuse the same ID.
- **A committed refactor log** (`fusion/refactors/`, outside the deletable `.fusion/` cache)
  for team/distributed use: every rename/move/delete/split/merge produces an append-only,
  git-committed entry (author, timestamp, before/after, a signature hash to verify the
  entry applies to the symbol the receiver actually has). When a developer pulls new
  changes, their local tooling replays new refactor entries against their own database, so
  everyone's IDE stays in sync with the project's current symbol identities without a
  rename ever silently breaking someone else's branch. Conflict detection (e.g. the same
  ID renamed two different ways on two branches) is surfaced precisely by the compiler, but
  resolution stays the job of source control and the reviewer - not the compiler.
- **A real, acknowledged cost worth deciding explicitly rather than assuming away:**
  embedding the ID directly in the raw source text (with the name kept only as a "backup"
  the compiler verifies against the database) makes plain-text `grep`, diffs, and code
  review noticeably worse without Fusion-aware tooling. A less invasive alternative that
  gets most of the same benefit: keep the same creation-time IDs and the same refactor log,
  but store the ID **only in the out-of-band database** (keyed by file + position + a
  content hash), never touching the source text at all - closer to how Roslyn (C#) and
  rust-analyzer already do stable incremental analysis and safe renames today. Whichever
  approach is chosen, it should be a deliberate decision made with real tooling and
  real-project experience in hand, not assumed by whichever note happened to describe it
  first.

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

Here is the **clean, concise, ready-to-paste section** for **files/FutureFeatures.md**, following your structure and style.
It fits naturally into your existing document and uses wording consistent with the rest of the Fusion spec.


# 🌐 Additional Specialized Packages (Not Core – Optional Ecosystem Modules)

These packages extend Fusion for domain-specific or high-performance workloads.
They are **not part of the core 22 modules**, but should be available as **separate optional packages** within the Fusion ecosystem.


## 🧵 Threads, Schedulers and Services: Notes for Future Consideration

**Status:** Notes and designs (user, 2026-11-02), not decisions. Some will become tasks
(42.26 and 42.27 already are), others are for future discussion. Moved here from CLAUDE.md's
project notes, with the user's clarifications and the useful ideas from the ChatGPT review
(`files/Fusion_Memory_Ownership_and_Services.md` - it saw only `files/Service.md`, so it is
taken as ideas, not plans).

#### Language documentaries

- https://nate.spot/software-documentaries/ - documentaries on how some languages came to be;
  many are on YouTube: https://www.youtube.com/channel/UCsUalyRg43M8D60mtHe6YcA
- The user's pick: the Clojure one, where Rich Hickey keeps it simple. Next to watch: *Simple
  Made Easy* (Rich Hickey, Strange Loop 2011) - **simple** (not tangled together) is not
  **easy** (familiar, close at hand). It supports "a simple working language first"; see also
  `files/Programming Languages Pain points.md`

#### 1. Starting a thread, and choosing its scheduler

The user's original note: `go.run(variables we need to use)(option how to schedule it) { ... }`

- The first brackets name the variables the thread uses (a capture list): the compiler knows
  exactly what crosses into the thread - each moved, borrowed or put in a temporary service
  (files/Ownership.md R7, Service.md S5)
- The second brackets choose a scheduler. **Optional:** by default there is none, and the
  extra brackets are left out
- **For now, the form is** `{ ... }.scheduler(x)` on the block - for example
  `service(x).run { ... }.scheduler(x)` - telling the compiler which scheduler to use when the
  service wasn't set up with one. (`go.run(...)(...)` is left aside for now)
- **The scheduler is declared before the threads that use it start:** it tells the service
  how to schedule when several variables or requests are being worked on - for example:
  - group read requests and carry them out together, instead of one at a time
  - one writer only - unless the writes touch different things (a different file lock,
    different database tables), which may run side by side
- Fits: `go f(x)` (Decisions.md CON.012); the `Scheduler` setting and a custom scheduler class
  (`files/Service.md`, Task 42.14); readers in parallel (42.18)

#### 2. A block that can't sleep or be interrupted (Task 42.26)

- While one iteration of a loop (or a marked block) runs, the thread doesn't sleep, yield or
  take an interrupt; only **between iterations** may it
- Interrupts and requests that arrive meanwhile go into the thread's **mailbox queue**, and
  are handled at the next safe point - data is never left half-changed
- This is cooperative scheduling with safe points (Erlang; Go before 1.14) - it builds on the
  `check interrupt` block after a loop (`files/Concurrency.md` "Cancellation / interrupt")
- **Issues to design for:**
  - **A long iteration could starve the other work** (why Go added preemption in 1.14). The
    user's answers:
    - a **request timeout** of so many seconds
    - and / or `sleepEvery(5)` - sleep every 5 seconds so others can work
    - **long-running work always gets its own thread**, never starving the others - loading
      a large text file, downloading a large file
  - **The operating system can always pause a thread** - no language can stop that. Fusion
    can promise the thread never sleeps, yields or takes an interrupt *by its own choice*
    mid-iteration, and ownership means no one else sees the half-done state. Truly never
    being paused needs a pinned core - the hot-path design (42.23, 42.24)
  - What counts as a safe point outside loops (a function call? the end of a `run` block?)
  - How long the mailbox may grow while a block runs (`Mailbox`, `WhenFull` settings)

#### 3. Telling requests apart: reads, writes, and resources with their own threads

The database was only an example. The point: a scheduler must know **what kind of request
each one is** - what is a write, what is a read, and how to tell them apart - so each request
goes to the right thread and none conflict.

- **A log file is easy:** one file, one writer
- **A database is more complex:**
  - it has **its own threads** - its own pool handling requests, including requests from
    other programs, not just ours. **We can't simply lock a database because we're connected
    to it.** Fusion schedules only its own requests to it
  - a scheduler with priorities tells its requests apart
- **The user's example** - each request first goes into the queue of its service or group
  service; inside, the database object has its own threads and scheduler:

  | Request | Goes to | Why |
  |---|---|---|
  | writes `users` | the writer thread (the only one allowed to write) | one writer |
  | reads `users` while a write to it is waiting | the writer thread | it waits behind the write and sees its result |
  | reads `accounts` only | a separate shared (reader) thread | nothing writes accounts - no conflict |
  | reads `users` and `accounts` together (a join) | the writer thread | it borrows `users` for the request (a temporary borrow); the others keep readonly use of `accounts` |

- The database itself has its own **group service** implementation to handle its many
  requests (Service.md S7, D.077)
- **The goal:** every request lands on the right thread, never conflicting with another
- **To design:** how a request says what it reads and writes (worked out by the compiler,
  like the readonly analysis 32.2e, or declared by the database module); how the database's
  own concurrency (transactions, its locks) and Fusion's scheduler fit together

#### 4. A system shutdown is always handled (Task 42.27)

When the system shuts down (or the program is asked to stop), the interrupt must be handled
inside services and loops wherever the critical logic is - for example closing the log file
and the database connections - so nothing is left in an unstable state. Fits the `Shutdown`
setting (finish the mailbox, or drop it) and `final` clean-up (42.4).

#### 5. Ideas from the ChatGPT review

- **Memory budgets** - a limit per scope, request or service, giving a controlled error
  instead of growth without limit (a service's `MemoryLimit` exists in Service.md). The user
  adds: it feeds the **visualisation of threads and variables - everything - when profiling
  the program** (the thread view in the editor: 36.6)
- **Resource lifetimes** - files, sockets, database connections: a timeout and a maximum
  lifetime, **backoff settings** (how long to wait before trying again, growing each time),
  and a **timeout error to the calling thread** when a resource goes over its lifetime. A
  timeout never destroys a resource another thread is still using - clean-up waits for the
  requests still running, cancellation and shutdown
- **Run-time diagnostics** - capture everything: mailbox pressure, memory per service,
  resources still alive (logical leaks ownership can't find), and a **heatmap of variables and
  functions** - how often each is used, in threads and in normal code
- **Left for the future:** its `scope Request { memory_limit = ... }` and
  `resource X { timeout = ... }` forms (its own invented syntax, not Fusion's yet)
- **Its review questions already answered by the design:** leaving a scope (the `Shutdown`
  setting); parallel reads (the readonly analysis, 32.2e); waiting inside a request (an
  error). **Still open:** how the compiler proves a temporary service starts and ends
  (42.19); undoing side effects of a failed request; charging memory to `MemoryLimit`; when
  clean-up itself fails; the boundary with C code (`extern`)

---

## 🆔 An Identity for Everything: a GUID per Name, a Small Database of the Hierarchy

**Status:** Idea for future consideration (user, 2026-11-02) - recheck later (files/FEATURES.md
42.28). Related: SET.024 (an IDE module with a symbol database), 36.5 (language server),
36.6 (the thread view), and "Threads, Schedulers and Services" above.

**The idea:** every namespace, module, class, function, variable and nested field gets its
own GUID, plus a readable path - the user's example:
`namespace:Core.Class:Main.Thread:CarService.Car:car.Engine.engine.int:Horsepower`

**Why (the user):**
- **The compiler checks by GUID alone** whether a variable or object is used in a thread -
  so it knows when an explicit or automatic service, or a group service, is needed
- **A hierarchy stored in a small database**, together with the code's hashes: which
  namespace holds which module, class, function and variable, and which threads and group
  services use each. The compiler reads it to tell which variables / objects are in a thread
  or group service
- **Refactoring:** in future, each name refers to its GUID instead of being written by hand
  everywhere - a rename changes the index, not every file

**Done before:** Unison stores code by content hash, names being only labels (renames never
break anything - but its source of truth isn't text files); C# / Roslyn give every symbol an
ID string (`M:Core.Car.Drive(System.Int32)`) used for rename refactoring; Fusion's compiler
already mangles names for C (`fu_Car__drive`).

#### Two different things inside it

| | A readable path | A stable ID (GUID) |
|---|---|---|
| Example | `Core.Main.CarService.car.engine.horsepower` | `7f3c...` |
| Comes from | the code's structure | stored (the database) |
| On a rename | changes | stays the same |
| Cost | small - the symbol table knows it already | an index kept in step with the files |
| Serves | diagnostics, the thread map, the profiler heatmap, deciding services | renames across files and libraries |

#### Points to settle (from the discussion)

1. **A thread isn't a container:** a variable belongs to its function or class in the code;
   *which threads use it* is worked out by the compiler (and can differ between runs). Keep
   the thread out of the ID and record it as a link - "used by thread CarService" - in the
   database. That link is what decides a service
2. **The type isn't identity:** `int` -> `long` would change the ID; keep the type as
   information about the ID
3. **Overloads and repeated names:** several constructors share a name; two blocks can each
   declare `i` - a signature or position tells them apart
4. **A declaration vs an object:** one declared `car` can have many `Car` objects while
   running - the heatmap and thread view need both the declaration's ID (fixed when
   compiling) and each object's own number (made while running)
5. **Short numbers while running:** GUIDs are 128 bits - small integers mapped to them keep
   the program fast; the GUIDs stay in the database. Random GUIDs (version 4), never ones
   holding the machine's address
6. **Problems with stored IDs:** git merges (two people adding names change the database at
   once), copy-paste duplicating an ID, edits made outside Fusion's tools leaving the database
   out of step, other projects still seeing a library's names (a public rename needs an alias)

#### A path that fits "simple first"

1. **With the Task 42 thread work:** the compiler gives every declaration its path and a
   number per build, and records which thread uses which variable - for diagnostics, the
   profiler, the heatmap and deciding services. No files change
2. **With the language server (36.5):** rename refactoring through the compiler's symbol
   table, as C# and Java do - most of the "change once" benefit, with no stored IDs
3. **Far future:** stable GUIDs in the small database with the code's hashes (or content
   hashes as in Unison); libraries publish old name -> ID -> new name

---

## 🌌 Far Future (after self-hosting): traits from variables, types made while running, DLCs and mods

**Status:** 💭 Far-future discussion (user, 2026-10-31) - not in files/FEATURES.md or Decisions.md
yet; recheck after self-hosting (Task 35). Beyond the current scope.

### 1. Interfaces held in a variable, used as traits

- A basic interface has no methods with code - default methods are a setting, off (Decisions.md D.006)
- Instead, a **variable** implements the interface, and its functions get their code in the
  form B set-up block `{ ... }`
- That variable can then be **added to classes** as needed - as a trait (reusable behaviour),
  or as a variable inside the class

```fusion
// a sketch only - the syntax is to be designed
Drivable wheels = Drivable() {
    wheels.drive = function(int speed) : print("driving at {speed}")
}

class Car
    uses wheels                // added as a trait - Car can drive
class Truck
    Drivable motion = wheels   // or held as a variable in the class
```

### 2. Interfaces and structs made while the program runs (enterprise flexibility)

- For enterprise systems that need the most flexibility: new interfaces and structs created
  while the program runs
- A **struct is the template**: it only holds the names and types of the members to make -
  the functions for a new interface, the fields for a new struct
- A **special class** (a type builder) reads the template and generates the new interface or
  struct
- Structs still never implement an interface (Decisions.md STC.005) - here a struct only
  describes what to make
- To work out then: Fusion compiles to static C, so this needs type information at run time
  and calls looked up at run time - kept to the code that asks for it, so the rest of the
  program stays static and fast

### 3. DLCs, mods and frameworks for the compiler

**Terms (user):**

| Term | What it is | Who makes it |
|---|---|---|
| **DLC** | A major add-on pack that enhances the base Fusion - officially supported | The Fusion team |
| **Mod** | A modification of the base Fusion that adds functionality: a team mod that didn't make a DLC and isn't planned for Fusion, or one made by fans / customers for their own needs; shared as needed (Steam Workshop as the model) | The Fusion team, fans, customers |
| **Framework** | The rules for **how, where and when** a DLC or mod may change things | The Fusion team |

**How it works (user):**
- The **Fusion compiler stays the same** - a mod never patches it
- The framework builds the DLC / mod into a **second binary** holding the new code; the
  compiler uses it through the framework
- A mod developer implements a **minimal set of features** the framework asks for - for
  example how an editor understands and shows the new syntax, and how the compiler compiles it
- What a mod may change (each allowed by the framework's rules): how code compiles, new
  types, parsing, the editor / IDE, the GUI, settings
- Instead of asking for a language feature, a developer can add it as a mod; a mod that
  becomes very popular can be added to Fusion itself

**The goal (user):** Fusion covers about 85% of the features of C, C++, C#, VB.NET, Java,
Rust and Python in one language; the other ~15% - features that don't suit Fusion's core -
come as DLCs and mods.

**Prior art:** Haskell (GHC) language extensions switched on per file, the popular ones later
folded into the standard set (GHC2021); Babel plugins trying JavaScript syntax before it
enters the standard; Racket (`#lang`: a language as a library); Kotlin / Scala compiler
plugins; Rust procedural macros; RimWorld's Harmony (a base mod other mods build on).

**Points to design then (Claude's notes, 2026-10-31):**
- **Fragmentation:** every mod lowers to base Fusion or the IR (Task 40); a tool shows the
  plain result; a module's public interface stays expressible in base Fusion, so code with
  and without a mod works together (files/FutureFeaturesCaution.md, Caution 3)
- **Security:** a mod runs code while building - sandboxed, with capability signatures
  (Task 39); official DLCs signed; tiers: DLC, verified mod, community mod
- **Compiler updates:** the framework is a stable, versioned API; each mod states the API
  version it supports
- **Two mods changing the same thing:** detected when they load, with a declared order - an
  error, never a silent winner
- **Settings:** a project lists its DLCs and mods in `fusion.toml` - features already become
  settings, so they are the first built-in "mods"
- **The 85% goal:** some features exclude each other (GC and ownership, exceptions and error
  returns); measure by what developers can do, not by a count of features
  (files/FutureFeaturesCaution.md, Caution 2)




---

**End of Future Features Document**

**Status:** Documented, pending implementation
**Next Review:** After MVP compiler completion
**Last Updated:** 2026-09-27
