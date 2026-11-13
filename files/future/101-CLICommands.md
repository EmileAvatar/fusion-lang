[< 100 CLI](100-CLI.md) | [Index](index.md) | [110 SymbolIDs >](110-SymbolIDs.md) <!-- nav -->

# 101 CLI Commands

**Status:** later - with 100 CLI

Contents: [Command Specifications](#command-specifications) | [1. `fusion fmt` - Code Formatter](#1-fusion-fmt---code-formatter) | [2. `fusion test` - Test Runner](#2-fusion-test---test-runner) | [3. `fusion doc` - Documentation Generator](#3-fusion-doc---documentation-generator) | [4. `fusion build` - Compiler](#4-fusion-build---compiler) | [5. `fusion run` - Compile and Execute](#5-fusion-run---compile-and-execute) | [6. `fusion clean` - Cleanup Build Artifacts](#6-fusion-clean---cleanup-build-artifacts) | [7. `fusion vet` - Code Analyzer](#7-fusion-vet---code-analyzer) | [8. `fusion check` - Syntax Check (No Compilation)](#8-fusion-check---syntax-check-no-compilation)

## Command Specifications

### 1. `fusion fmt` - Code Formatter

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

### 2. `fusion test` - Test Runner

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

### 3. `fusion doc` - Documentation Generator

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

### 4. `fusion build` - Compiler

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

### 5. `fusion run` - Compile and Execute

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

### 6. `fusion clean` - Cleanup Build Artifacts

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

### 7. `fusion vet` - Code Analyzer

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

### 8. `fusion check` - Syntax Check (No Compilation)

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

[< 100 CLI](100-CLI.md) | [Index](index.md) | [110 SymbolIDs >](110-SymbolIDs.md) <!-- nav -->
