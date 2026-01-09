# Fusion Programming Language Compiler

A Python-based compiler for the Fusion programming language that compiles Fusion source code to C, then uses GCC to compile to native executables.

## Features

- **Multiple Block Styles**: Supports indentation, braces `{}`, and `End` keywords
- **Return-Type-First Syntax**: `int function add(int a, int b)`
- **Inline Lambdas**: `int double(int x) : x * 2`
- **String Interpolation**: `print("Value: {x}")`
- **Complete Type System**: int, float, double, string, bool, char, void
- **Control Flow**: if/else, while, for loops, break/continue
- **Full Semantic Analysis**: Type checking, name resolution, control flow validation

## Requirements

- **Python 3.10+**
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
   git clone <repository-url>
   cd fusion-compiler
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
fusion-compiler/
├── src/
│   ├── lexer/           # Lexical analyzer (tokenization)
│   ├── parser/          # Parser (AST construction)
│   ├── semantic/        # Semantic analyzer (validation)
│   ├── codegen/         # C code generator
│   └── utils/           # Utilities (errors, source location)
├── tests/               # Test suite
├── examples/            # Example Fusion programs
├── main.py              # Compiler entry point
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

### Completed (MVP)
- ✅ Lexer (tokenization, indentation tracking, block style detection)
- ✅ Parser (expression parsing, statement parsing, declaration parsing)
- ✅ Semantic Analyzer (type checking, name resolution, control flow validation)
- ✅ Code Generator (C code generation)
- ✅ GCC Integration (compilation to executable)

### Test Results
- **Total Tests**: 999+
- **Lexer Tests**: 412 passing
- **Parser Tests**: 251 passing
- **Semantic Tests**: 200 passing
- **Code Generation Tests**: 120 passing
- **Integration Tests**: 16 passing

### Future Features (Post-MVP)
- Classes and interfaces
- Generic types
- Memory management (Unique/Shared/Weak)
- Threading and async/await
- Standard library (fusionlib with 21 modules)
- Multiple safety modes
- Optimizations

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Quick reference for AI assistant
- **[fusion-language-spec.md](files/fusion-language-spec.md)** - Complete language specification
- **[fusion.ebnf](files/fusion.ebnf)** - EBNF grammar specification
- **[taskSummary2.md](taskSummary2.md)** - Current development progress tracking (Task 5+)
- **[taskSummary.md](task/taskSummary.md)** - Archived MVP progress (Tasks 1-4)

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

**Solution**: Ensure you're using Python 3.10 or later:
```bash
python --version
```

## Contributing

This is a prototype compiler for educational purposes. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

[Specify your license here]

## Author

[Your name/organization]

## Acknowledgments

- Inspired by Python, C, VB.NET, and modern language design
- Built with Python and GCC
- Developed using test-driven development (TDD)
