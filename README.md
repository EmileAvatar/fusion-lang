# Fusion Programming Language 🏗️

Fusion is not a traditional programming language. It is a configurable compiler platform where syntax is optional, behavior is declarative, and execution is pluggable.

Instead of choosing a language and accepting its trade-offs, Fusion lets you assemble the language your project needs.

The Fusion compiler (MVP) currently compiles Fusion source code to C, then uses GCC to produce native executables. Planned backends include LLVM IR, a bytecode VM, an interpreter, and a self-hosting compiler (written in Fusion).

## Code as Infrastructure

Traditional development forces you to choose a programming language first, then work around its strengths and weaknesses.

Fusion flips this model. Instead of selecting *a language*, the goal is to let you select **capabilities**: safety guarantees, performance constraints, memory management model, concurrency model, execution backend, and diagnostics level. The compiler is meant to configure itself to match what you declare - similar to how Infrastructure-as-Code tools like Terraform or AWS CDK work, but applied to programming languages.

## Why Fusion Exists

Most languages force trade-offs:

- C: fast, unsafe
- Python: safe, slow
- Java: portable, heavy
- Rust: safe, complex
- Go: simple, restrictive

Fusion's goal is to remove that forced choice - reconfigure Fusion instead of switching languages when requirements change. Fusion doesn't compete with C, Python, Rust, or Go. It competes with the idea that you must choose only one.

## Syntax Without Lock-In

Fusion separates **how code is written** from **how it is compiled and executed**. All three syntax styles below compile to the same AST:

- Indentation-based (Python-like)
- Brace-based (C / Java-like)
- Keyword-based (VB-style: `End if`, `End function`)

Syntax is a preference, not a limitation.

## Current Status (MVP)

The capability-driven vision above is the direction, not yet the implementation. What's real today is a working prototype that proves the pipeline:

```
Fusion Source -> C -> GCC -> Native Executable
```

Configurable safety modes, memory models, and pluggable execution backends are **planned, and partly decided**, but not yet implemented: an optional `fusion.toml` project config file exists today (indentation settings are actually wired to it; safety-mode/backend are recognized but not yet enforced), and the `Unique`/`Shared`/`Weak` memory-model semantics are fully decided and documented, but the compiler doesn't implement them yet. The section below lists what's actually built and tested right now.

## Features

### Core Language Features (MVP - Complete)
- **Multiple Block Styles**: Choose between indentation (Python), braces (C/Java), or `End` keywords (VB.NET) - all semantically equivalent
- **Return-Type-First Syntax**: `int function add(int a, int b)` - clear return type declaration
- **Inline Lambdas**: Single-expression functions with `:` syntax - `int double(int x) : x * 2`
- **String Interpolation**: Inline `{var}` and positional `{@1}` format - `print("Value: {x}")`
- **Complete Type System**: int, float, double, string, bool, char, void with automatic int→float promotion
- **const Declarations**: Immutable variables, enforced at compile time - `const int MAX = 100`
- **Fixed-Size Arrays**: `int[] x = [1,2,3]` or `int[5] x`, element read/write, `len(x)` resolved at compile time
- **Control Flow**: if/else, while, for loops with range support, break/continue
- **Block-Level (Lexical) Scoping**: a variable is only visible inside the `if`/`while`/`for`/`{ }` block it's declared in, and nested blocks can shadow outer variables of the same name - matches C/Java/Rust, not Python/JavaScript
- **Recursive Functions**: Full support for direct and indirect recursion
- **Project Configuration**: an optional `fusion.toml` next to your source file (or in the cwd) - `[indentation]` (`tab_width`/`allow_mixed`) is actually wired into the lexer; `[safety]`/`[backend]` are parsed and validated but not yet enforced. See [examples/project_config_demo/](examples/project_config_demo/) for a working demonstration

### Compiler Features (MVP - Complete)
- **Robust Lexer**: 391 tests (383 passing, 8 skipped) - Tokenization, indentation tracking, operator recognition
- **Complete Parser**: 251 tests passing - AST generation, expression precedence, statement parsing
- **Semantic Analyzer**: 260 tests passing - Type checking, name resolution, control flow validation, const and array validation
- **C Code Generator**: 137 tests passing - Clean C code generation with GCC integration
- **Project Configuration**: 24 tests - `fusion.toml` discovery, parsing, validation, and lexer wiring (Task 12.12)
- **Additional Coverage**: 64 tests - error-handling utilities, full end-to-end compilation
- **End-to-End Compilation**: 8/8 example programs compile and run successfully
- **Test Coverage**: 1,119 tests passing (99.3%), 8 skipped

### Planned Features (Post-MVP)
- **Richer Collections**: List, Dictionary, Set with LINQ-style operations (basic fixed-size arrays already implemented, above)
- **Nullable Arrays & Safe Navigation**: `arr.length`/`arr?.length`, `arr?[i]` - needs Fusion's nullability/memory model decided first
- **Classes & Interfaces**: Object-oriented programming support
- **Generic Types**: Type parameters for functions and classes
- **Memory Models**: Unique, Shared, Weak pointer semantics (configurable)
- **Concurrency**: Threads, goroutines, channels, async/await primitives
- **Standard Library**: 21 modules (Core, Math, Collections, IO, Net, GUI, Graphics, Audio, AI, etc.)
- **Safety Modes**: standard | strict | unsafe (configurable per project)
- **LLVM Backend**: Direct LLVM IR generation for better optimization
- **Self-Hosting**: Compiler rewritten in Fusion (bootstrap process)

## Requirements

- **Python 3.11+** (raised from 3.10 by Task 12.12's project-config system, which uses the
  `tomllib` stdlib module added in 3.11 - see `src/config/project_config.py`)
- **GCC** (GNU Compiler Collection) - Required for compiling generated C code
  - Windows: Install MinGW-w64 or TDM-GCC
  - Linux: `sudo apt install gcc` (usually pre-installed)
  - macOS: `xcode-select --install`

### Installing GCC on Windows

1. **MinGW-w64** (recommended):
   - Download from: https://www.mingw-w64.org/
   - Or use MSYS2: https://www.msys2.org/
   - Add `bin` directory to PATH (e.g., `C:\msys64\mingw64\bin`)

2. **TDM-GCC**:
   - Download from: https://jmeubank.github.io/tdm-gcc/
   - Installer automatically adds to PATH

3. Verify installation:
   ```bash
   gcc --version
   ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/EmileAvatar/fusion-lang.git
   cd fusion-lang
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify GCC is installed:
   ```bash
   gcc --version
   ```

## Usage

### Compiling a Fusion Program

```bash
python main.py examples/hello_world.fusion
```

This will:
1. **Lexical Analysis**: Tokenize the source code
2. **Parsing**: Build Abstract Syntax Tree (AST)
3. **Semantic Analysis**: Validate types, names, and control flow
4. **Code Generation**: Generate C source code (`hello_world.c`)
5. **Compilation**: Compile to executable using GCC (`hello_world.exe` on Windows, `hello_world` on Linux/Mac)

### Running the Compiled Program

```bash
# Windows
hello_world.exe

# Linux/Mac
./hello_world
```

## Example Programs

The `examples/` directory contains sample Fusion programs:

### Hello World
```fusion
void function main()
    print("Hello, World!")
End function
```

### Factorial (Recursive)
```fusion
int function factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)
End function

int function main()
    int result = factorial(5)
    print("Factorial of 5 is {result}")
    return 0
End function
```

### FizzBuzz
```fusion
void function main()
    int i = 1
    while i <= 20
        if i % 15 == 0
            print("FizzBuzz")
        else
            if i % 3 == 0
                print("Fizz")
            else
                if i % 5 == 0
                    print("Buzz")
                else
                    print("{i}")
        i = i + 1
End function
```

### Calculator (Lambda Functions)
```fusion
int function add(int a, int b) : a + b
int function subtract(int a, int b) : a - b
int function multiply(int a, int b) : a * b

void function main()
    int x = 10
    int y = 5
    print("Sum: {add(x, y)}")
    print("Diff: {subtract(x, y)}")
    print("Prod: {multiply(x, y)}")
End function
```

### const Declarations
```fusion
void function main()
    const int MAX_ITERATIONS = 1000
    const int WIDTH = 80
    const int HEIGHT = 24
    int total_pixels = WIDTH * HEIGHT
    print("Screen size: {WIDTH}x{HEIGHT} = {total_pixels} pixels")

    // Reassigning a const is a compile-time error:
    // MAX_ITERATIONS = 20
End function
```
See [examples/const_demo.fusion](examples/const_demo.fusion) for the full example.

### Arrays
```fusion
void function main()
    int[] scores = [10, 20, 30, 40, 50]
    scores[0] = 99
    print("Number of scores: {len(scores)}")

    float[3] buffer   // explicit size, zero-initialized
    buffer[0] = 1.5
End function
```
Fixed-size, local-variable arrays with element indexing and `len()`. See
[examples/arrays_demo.fusion](examples/arrays_demo.fusion) for the full example.

## Language Syntax Quick Reference

### Function Declaration
```fusion
// Return-type-first syntax
<return_type> function <name>(<type> <param> = <default>)
    <body>
End function

// Inline lambda
int double(int x) : x * 2
```

### Variable Declaration
```fusion
// Explicit type (required)
int count = 0
string name = "Alice"

// Constant (must initialize, cannot be reassigned)
const float PI = 3.14159

// Fixed-size array (see the Arrays example above for more)
int[] scores = [10, 20, 30]
```

### Block Styles
```fusion
// 1. Indentation (Python-style)
if condition
    statement1
    statement2

// 2. Braces (C-style)
if condition {
    statement1
    statement2
}

// 3. End keyword (VB.NET-style)
if condition
    statement1
    statement2
End if
```

### String Interpolation
```fusion
int x = 42
print("Value: {x}")               // Named interpolation
print("Values: {x}, {y}, {z}")    // Multiple variables
```

### Control Flow
```fusion
// If/Else
if x > 0
    print("Positive")
else
    print("Non-positive")

// While loop
while x > 0
    x = x - 1

// For loop with range
for i in range(0, 10)
    print("{i}")

// For loop with step
for i in range(0, 10, 2)
    print("{i}")

// Break and continue
for i in range(0, 10)
    if i == 5
        break
    if i % 2 == 0
        continue
    print("{i}")
```

## Project Structure

```
fusion-lang/
├── src/
│   ├── lexer/           # Lexical analyzer (tokenization)
│   ├── parser/          # Parser (AST construction)
│   ├── semantic/        # Semantic analyzer (validation)
│   ├── codegen/         # C code generator
│   ├── config/          # Project configuration - fusion.toml loading (Task 12.12)
│   └── utils/           # Utilities (errors, source location)
├── tests/               # Test suite (1,119 passing, 8 skipped)
├── examples/            # Example Fusion programs
├── task/                # Task tracking and planning documents
├── files/               # Language specifications and documentation
│   ├── fusion-language-spec.md    # Complete language spec
│   ├── fusion.ebnf                # EBNF grammar
│   └── reports/                   # Verification reports
├── debug/               # Debugging scripts (isolated from pytest)
├── main.py              # Compiler entry point
├── taskSummary2.md      # Current task tracking (Tasks 5+)
├── CLAUDE.md            # AI assistant instructions
└── README.md            # This file
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_lexer.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Note**: End-to-end tests require GCC to be installed and available in PATH.

## Development Status

### Completed (MVP) ✅
- ✅ **Phase 1: Lexer** - Tokenization, indentation tracking, block style detection
- ✅ **Phase 2: Parser** - Expression parsing, statement parsing, declaration parsing
- ✅ **Phase 3: Semantic Analyzer** - Type checking, name resolution, control flow validation
- ✅ **Phase 4: Code Generator** - C code generation with GCC integration
- ✅ **Task 5: Project Organization** - File structure cleanup
- ✅ **Task 6: Verification & Bug Fixes** - All examples verified, FizzBuzz bug fixed
- ✅ **Task 7: Git Integration** - GitHub repository setup, version control
- ✅ **Task 8: const Keyword** - Lexer, parser, semantic validation, codegen, docs, and verification complete (all 7 examples now checked, including const_demo)
- 🔄 **Task 12 (Architecture Hardening)** - In progress (10/12 sub-tasks). Complete: Typed AST (semantic analyzer hands the code generator resolved types instead of it guessing format specifiers - fixes the architectural gap that caused the FizzBuzz bug), C codegen module split (`c_types.py`/`c_names.py`/`c_runtime.py`), block-level (lexical) scoping (fixed a real bug where semantic analysis accepted programs the generated C could never compile), memory model semantics (`Unique`/`Shared`/`Weak` - decided and documented, not yet implemented), and a project configuration system (`fusion.toml` - indentation settings actually wired in; safety/backend recognized but not yet enforced). Remaining: IR layer and stdlib-lowering design - see taskSummary2.md Task 12
- ✅ **Task 9: Array Support (v1)** - Fixed-size local arrays, literal/explicit-size declarations, element read/write, `len()` resolved at compile time. Arrays as function parameters/return types, multi-dimensional arrays, and nullable arrays (`.length`/`?.`) are deferred - see taskSummary2.md Task 9

### Test Results
- **Total Tests**: 1,119 passing (99.3% pass rate)
- **Lexer Tests**: 391 (383 passing, 8 skipped) - tokenization, operators, literals, comments
- **Parser Tests**: 251 passing (AST nodes, expressions, statements, declarations)
- **Semantic Tests**: 260 passing (type checking, name resolution, control flow, const, arrays)
- **Code Generation Tests**: 137 passing (C code generation, GCC integration, const, arrays)
- **Project Configuration Tests**: 24 passing (`fusion.toml` discovery, parsing, validation, lexer wiring)
- **Additional Tests**: 64 passing (error-handling utilities, end-to-end compilation)
- **Skipped Tests**: 8 (single-quote comment syntax - deferred design decision, conflicts with char literals)
- **Example Programs**: 8/8 verified and working (hello_world, factorial, fizzbuzz, calculator, sum_array, max_three, const_demo, arrays_demo), plus a manual `fusion.toml` demonstration (`examples/project_config_demo/`)

### Future Features (Post-MVP)
- Richer collections (List, Dictionary, Set, LINQ) - basic fixed-size arrays already implemented
- Nullable arrays and safe navigation (`.length`, `?.`, `?[`) - memory model decided (Task 12.7), not yet scoped for implementation
- Classes and interfaces
- Generic types
- Memory management (`Unique`/`Shared`/`Weak`) - semantics decided and documented (Task 12.7), compiler support not yet built
- Threading and async/await
- Standard library (fusionlib with 21 modules)
- Multiple safety modes (`fusion.toml`'s `[safety]` key is recognized today but not yet enforced)
- Optimizations

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Quick reference for AI assistant
- **[fusion-language-spec.md](files/fusion-language-spec.md)** - Complete language specification
- **[fusion.ebnf](files/fusion.ebnf)** - EBNF grammar specification
- **[taskSummary2.md](taskSummary2.md)** - Current development progress tracking (Task 5+)
- **[taskSummary.md](task/taskSummary.md)** - Archived MVP progress (Tasks 1-4)
- **[taskSummaryArchive.md](task/taskSummaryArchive.md)** - Archived completed post-MVP task detail (Tasks 5-9, 12)

## Troubleshooting

### GCC Not Found
**Error**: `FileNotFoundError: [WinError 2] The system cannot find the file specified`

**Solution**: Install GCC and ensure it's in your system PATH:
1. Install MinGW-w64 or TDM-GCC (Windows)
2. Add GCC bin directory to PATH
3. Restart terminal/IDE
4. Verify: `gcc --version`

### Compilation Errors
**Error**: GCC compilation fails with errors

**Solution**:
1. Check the generated `.c` file for issues
2. Verify your Fusion code passes semantic analysis
3. Report bugs with minimal reproducible example

### Python Version
**Error**: Syntax errors in Python code

**Solution**: Ensure you're using Python 3.11 or later:
```bash
python --version
```

## Contributing

Contributions are welcome! Fusion is an open-source project built collaboratively with transparency.

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/my-new-feature`
3. **Follow the PLAN FIRST methodology** (see [CLAUDE.md](CLAUDE.md)):
   - Read [taskSummary2.md](taskSummary2.md) to understand current progress
   - Plan your changes before implementation
   - Update task tracking after each sub-task
4. **Add tests**: All new features must have corresponding tests
5. **Ensure all tests pass**: `python -m pytest tests/ -v`
6. **NO EMOJIS IN CODE**: Only use emojis in markdown files, never in .py, .c, or .h files
7. **Commit your changes**: Use clear, descriptive commit messages
8. **Push to your fork**: `git push origin feature/my-new-feature`
9. **Submit a pull request** with a detailed description

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings for functions and classes
- Keep functions focused and single-purpose
- Write tests before implementing features (TDD)

### Testing
- Run full test suite: `python -m pytest tests/ -v`
- Run specific tests: `python -m pytest tests/test_lexer.py -v`
- Verify examples: `python tests/verify_examples.py`
- All tests must pass before submitting PR

### Areas for Contribution
- **Language Features**: classes, generics, richer collections, nullable arrays/safe navigation (basic fixed-size arrays already implemented - see [taskSummary2.md](taskSummary2.md) for the current roadmap)
- **Standard Library**: Implement fusionlib modules (IO, Collections, Net, etc.)
- **Optimizations**: Code generation improvements, performance tuning
- **Documentation**: Tutorials, examples, language guides
- **Tooling**: IDE plugins, syntax highlighters, LSP server
- **Testing**: Additional test cases, edge case coverage

### Reporting Issues
- Use GitHub Issues for bug reports and feature requests
- Provide minimal reproducible examples
- Include Fusion code, expected behavior, and actual behavior
- Mention your OS, Python version, and GCC version

### AI Transparency
This project was developed collaboratively with AI assistance (ChatGPT and Claude AI). We believe in transparency about AI contributions to open-source projects. All AI-generated code has been reviewed, tested, and verified by human maintainers.

## License

**MIT License** (Recommended for open-source projects)

Copyright (c) 2024-2025 Emile M Steenkamp

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Author

**Emile M Steenkamp**
- GitHub: [@EmileAvatar](https://github.com/EmileAvatar)

## Contributors

### AI Collaborators
This project was developed with significant contributions from AI assistants. We believe in transparency:

- **Claude AI (Anthropic)** - Claude Opus 4.5, Claude Sonnet 4.5, and Claude Sonnet 5
  - Compiler architecture and implementation
  - Test suite development
  - Documentation and planning
  - Code reviews and optimization suggestions

- **ChatGPT (OpenAI)** - GPT-4
  - Language design consultation
  - Feature planning and specification
  - Documentation reviews

**Note**: All AI-generated code has been thoroughly reviewed, tested (1,119+ passing tests), and validated by human maintainers. The project follows rigorous PLAN FIRST methodology to prevent AI drift and ensure quality.

### Human Contributors
- **Emile M Steenkamp** - Project creator, lead developer, and maintainer

Want to contribute? See the [Contributing](#contributing) section above!

## Acknowledgments

- **Language Design Inspiration**: Python (indentation), C (performance), VB.NET (End keywords), Go (simplicity), Rust (safety)
- **Tools & Technologies**: Python 3.11+, GCC, pytest, Git/GitHub
- **Development Methodology**: Test-Driven Development (TDD), PLAN FIRST approach
- **Community**: Open-source contributors and the broader programming language community

---

## Links

- **GitHub Repository**: https://github.com/EmileAvatar/fusion-lang
- **Language Specification**: [files/fusion-language-spec.md](files/fusion-language-spec.md)
- **EBNF Grammar**: [files/fusion.ebnf](files/fusion.ebnf)
- **Task Tracking**: [taskSummary2.md](taskSummary2.md)
- **Issues & Bug Reports**: https://github.com/EmileAvatar/fusion-lang/issues

---

**Star ⭐ this repository if you find it interesting!**

**Fusion Programming Language** - Write Once, Configure Anywhere 🏗️
