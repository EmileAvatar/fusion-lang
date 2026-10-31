# Fusion Programming Language 🏗️

Fusion is not a traditional programming language. It is a configurable compiler platform where syntax is optional, behavior is declarative, and execution is pluggable.

Instead of choosing a language and accepting its trade-offs, Fusion lets you assemble the language your project needs.

The Fusion compiler compiles Fusion source code to C, then uses GCC to produce native executables. Planned: a self-hosting compiler (written in Fusion), then more backends - LLVM IR, a bytecode VM, an interpreter.

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

## One Owner, One Writer

Fusion aims to be memory-safe and free of data races by construction, without a garbage
collector by default: every value has one owner, assigning moves it, passing lends it, and a
value several threads use gets exactly one writer - a service. The rules: `Ownership.md`.

## Status

Fusion is in early development. The capability-driven vision above is the direction; what
exists today is a compiler, written in Python, that proves the pipeline:

```
Fusion source -> C -> GCC -> native executable
```

- **What the language can do today, with examples:** [SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md)
  and the programs in [examples/](examples/)
- **Status of every task and feature - done, open, postponed:** [FEATURES.md](FEATURES.md)
- **Next major goal:** a simple self-hosting compiler - Fusion compiling Fusion - as a first
  test run; the Python compiler stays in use until the self-hosted one is fully independent

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

[examples/](examples/) holds one program for every section of
[SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md), fuller demos (`fizzbuzz`, `structs_demo`,
`control_flow`, ...) and projects of several files (`shop`, `wordcount`). Build them all with
`python check.py --build-examples`; [examples/CLAUDE.md](examples/CLAUDE.md) explains the
folder.

## Project Structure

```
fusion-lang/
├── src/                 # The compiler - src/CLAUDE.md explains the pipeline
│   ├── lexer/           # Tokens, indentation, block styles, source security
│   ├── parser/          # The AST
│   ├── semantic/        # Types, names, built-in functions, checks
│   ├── codegen/         # C code and the C runtime (strings, bytes, lists, maps, files)
│   ├── modules/         # import: module folders, public / private
│   ├── config/          # fusion.toml
│   └── utils/           # Errors, source locations
├── tests/               # The test suite
├── examples/            # Example programs and projects
├── tools/               # Helper scripts
├── files/               # Language specification, grammar, reports
├── task/                # Task archive, backlog, automation notes
├── main.py              # Compiler entry point
├── check.py             # Runs every check
├── FEATURES.md          # Status of every task and feature
├── SYNTAX_REFERENCE.md  # What works today, with examples
├── taskSummary2.md      # The active task's plan
└── CLAUDE.md            # Rules for the AI assistant
```

## Running Tests

```bash
# Every check: tests, examples, leak check, reference examples, ASCII rule
python check.py

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_lexer.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Note**: End-to-end tests require GCC to be installed and available in PATH.

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Quick reference for AI assistant
- **[fusion-language-spec.md](files/fusion-language-spec.md)** - Complete language specification
- **[fusion.ebnf](files/fusion.ebnf)** - EBNF grammar specification
- **[FutureFeaturesCaution.md](FutureFeaturesCaution.md)** - Project review and cautions: why a simple working core language comes before the larger planned features, a proposed answer to ecosystem fragmentation, a guide to choosing memory strategies, and the library trust/sandboxing/security design
- **[Fusion_domain.md](files/Fusion_domain.md)** - Visual, domain-first hierarchy of everything Fusion supports or plans to support (types, control flow, OOP, memory model, concurrency, stdlib) - a feature map, not a build-status tracker
- **[FEATURES.md](FEATURES.md)** - Status of every task and feature
- **[SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md)** - What the language can do today, with examples
- **[taskSummary2.md](taskSummary2.md)** - The active task's plan
- **[taskSummary.md](task/taskSummary.md)** - Archived MVP progress (Tasks 1-4)
- **[taskSummaryArchive.md](task/taskSummaryArchive.md)** - Detail of finished tasks

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
   - Read [FEATURES.md](FEATURES.md) and [taskSummary2.md](taskSummary2.md) to see where things stand
   - Plan your changes before implementation
   - Update task tracking after each sub-task
4. **Add tests**: All new features must have corresponding tests
5. **Ensure every check passes**: `python check.py`
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
- Everything at once: `python check.py` - all must pass before submitting a PR

### Areas for Contribution
- **Language Features**: see the open tasks in [FEATURES.md](FEATURES.md)
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

**Note**: All AI-generated code has been thoroughly reviewed, tested (the full test suite and every example), and validated by human maintainers. The project follows rigorous PLAN FIRST methodology to prevent AI drift and ensure quality.

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
- **Status of every feature**: [FEATURES.md](FEATURES.md)
- **Issues & Bug Reports**: https://github.com/EmileAvatar/fusion-lang/issues

---

**Star ⭐ this repository if you find it interesting!**

**Fusion Programming Language** - Write Once, Configure Anywhere 🏗️
