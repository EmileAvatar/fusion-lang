# Task 3.6: Semantic Analyzer Integration & Testing

**Phase:** 3 - Semantic Analyzer
**Status:** 🔴 Not Started
**Estimated Effort:** 3-4 hours
**Priority:** High (Integration & validation)

---

## 📋 Overview

Integrate all semantic analysis components (symbol table, type checker, name resolver, control flow validator, entry point validator) into a unified SemanticAnalyzer class. Create comprehensive integration tests with real Fusion programs.

---

## 🎯 Goals

1. Create SemanticAnalyzer class that orchestrates all validators
2. Integrate all Phase 3 components in correct order
3. Collect and report all errors/warnings
4. Test with complete Fusion programs (Hello World, Factorial, FizzBuzz)
5. Validate error recovery (continue after first error)
6. Create integration test suite

---

## 📝 Requirements

### 1. SemanticAnalyzer Class

**File:** `src/semantic/semantic_analyzer.py`

```python
class SemanticAnalyzer:
    """Main semantic analyzer that orchestrates all validation passes."""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.name_resolver = NameResolver(self.symbol_table)
        self.type_checker = TypeChecker(self.symbol_table)
        self.control_flow_validator = ControlFlowValidator()
        self.entry_point_validator = EntryPointValidator()

        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []

    def analyze(self, ast: ProgramNode) -> bool:
        """
        Analyze the AST and return True if no errors.

        Performs semantic analysis in the following order:
        1. Entry point validation (check for main)
        2. Name resolution (build symbol table)
        3. Type checking (validate types)
        4. Control flow validation (validate returns, loops)

        Returns:
            True if analysis succeeded (no errors), False otherwise
        """
        # Clear previous results
        self.errors.clear()
        self.warnings.clear()

        # Pass 1: Validate entry point
        ep_errors, ep_warnings = self.entry_point_validator.validate_program(ast)
        self.errors.extend(ep_errors)
        self.warnings.extend(ep_warnings)

        # Pass 2: Name resolution (build symbol table)
        nr_errors = self.name_resolver.resolve_program(ast)
        self.errors.extend(nr_errors)

        # Pass 3: Type checking (requires symbol table from pass 2)
        tc_errors = self.type_checker.check_program(ast)
        self.errors.extend(tc_errors)

        # Pass 4: Control flow validation
        cf_errors, cf_warnings = self.control_flow_validator.validate_program(ast)
        self.errors.extend(cf_errors)
        self.warnings.extend(cf_warnings)

        # Return success if no errors
        return len(self.errors) == 0

    def get_errors(self) -> List[SemanticError]:
        """Get all collected errors."""
        return self.errors.copy()

    def get_warnings(self) -> List[SemanticError]:
        """Get all collected warnings."""
        return self.warnings.copy()

    def print_diagnostics(self) -> None:
        """Print all errors and warnings to stderr."""
        for error in self.errors:
            print(f"Error: {error}", file=sys.stderr)

        for warning in self.warnings:
            print(f"Warning: {warning}", file=sys.stderr)

        if self.errors:
            print(f"\n{len(self.errors)} error(s) found", file=sys.stderr)
        if self.warnings:
            print(f"{len(self.warnings)} warning(s) found", file=sys.stderr)
```

---

### 2. Compiler Integration

**File:** `src/semantic/__init__.py`

```python
"""Semantic analysis package.

Exports:
    - SemanticAnalyzer: Main analyzer class
    - SemanticError: Exception for semantic errors
    - SymbolTable: Symbol table for name resolution
"""

from .semantic_analyzer import SemanticAnalyzer
from .errors import SemanticError
from .symbol_table import SymbolTable

__all__ = ['SemanticAnalyzer', 'SemanticError', 'SymbolTable']
```

**Update:** `main.py` (compiler entry point)

```python
#!/usr/bin/env python3
"""Fusion compiler main entry point."""

import sys
from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer

def compile_file(source_path: str) -> int:
    """Compile a Fusion source file.

    Returns:
        0 on success, 1 on error
    """
    # Read source
    with open(source_path, 'r') as f:
        source = f.read()

    # Lexical analysis
    lexer = Lexer(source, source_path)
    tokens = lexer.tokenize()

    if lexer.errors:
        for error in lexer.errors:
            print(f"Lexer error: {error}", file=sys.stderr)
        return 1

    # Parsing
    parser = Parser(tokens)
    ast = parser.parse_program()

    if parser.errors:
        for error in parser.errors:
            print(f"Parser error: {error}", file=sys.stderr)
        return 1

    # Semantic analysis
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)

    if not success:
        analyzer.print_diagnostics()
        return 1

    # Print warnings even on success
    if analyzer.get_warnings():
        analyzer.print_diagnostics()

    print(f"✓ Semantic analysis passed: {source_path}")
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: fusion <source.fusion>", file=sys.stderr)
        return 1

    source_path = sys.argv[1]
    return compile_file(source_path)

if __name__ == '__main__':
    sys.exit(main())
```

---

## ✅ Acceptance Criteria

- [ ] SemanticAnalyzer class created
- [ ] All validators integrated in correct order
- [ ] Errors and warnings collected and reported
- [ ] Hello World example passes semantic analysis
- [ ] Factorial example passes semantic analysis
- [ ] FizzBuzz example passes semantic analysis
- [ ] Error programs correctly detected
- [ ] Multiple errors reported (not just first)
- [ ] Integration tests pass (30+ tests)
- [ ] Compiler main.py updated to use SemanticAnalyzer

---

## 🧪 Test Cases

### Integration - Valid Programs (10 tests)
- Hello World (void main, print call)
- Factorial recursive (int return, recursion, if-else)
- Factorial iterative (for loop, accumulator)
- FizzBuzz (for loop, if-else, modulo)
- Simple calculator (multiple functions, parameters)
- Variable shadowing (nested scopes)
- Type promotion (int to float)
- Lambda expression (inline lambda)
- Const variable (constant declaration)
- Multiple returns (different branches)

### Integration - Invalid Programs (15 tests)
- No main function (error)
- Multiple main functions (error)
- Undefined variable (error)
- Type mismatch in assignment (error)
- Type mismatch in return (error)
- Function call wrong arg count (error)
- Function call wrong arg type (error)
- Break outside loop (error)
- Continue outside loop (error)
- Non-void function missing return (error)
- Duplicate variable in same scope (error)
- Duplicate function (error)
- Call undefined function (error)
- Assign to constant (error)
- If condition not bool (error)

### Error Recovery (5 tests)
- Multiple undefined variables (report all)
- Multiple type errors (report all)
- Undefined function + type error (report both)
- Missing return + type error (report both)
- Mix of errors and warnings

**Total Estimated Tests:** 30 tests

---

## 📁 Files to Create/Update

```
src/semantic/
├── __init__.py             # Package exports
└── semantic_analyzer.py    # SemanticAnalyzer class

main.py                     # Updated compiler entry point

tests/
└── test_semantic_integration.py  # Integration tests
```

---

## 🔗 Dependencies

**Depends On:**
- Task 3.1 (Symbol Table)
- Task 3.2 (Type Checker)
- Task 3.3 (Name Resolver)
- Task 3.4 (Control Flow Validator)
- Task 3.5 (Entry Point Validator)

**Blocks:**
- Phase 4 (Code Generation)

---

## 📊 Progress Tracking

- [ ] Create `src/semantic/semantic_analyzer.py`
- [ ] Implement SemanticAnalyzer class
- [ ] Implement analyze() method with 4 passes
- [ ] Implement error/warning collection
- [ ] Implement print_diagnostics()
- [ ] Update `src/semantic/__init__.py` with exports
- [ ] Update `main.py` with semantic analysis integration
- [ ] Create `tests/test_semantic_integration.py`
- [ ] Write valid program tests (10 tests)
- [ ] Write invalid program tests (15 tests)
- [ ] Write error recovery tests (5 tests)
- [ ] Test Hello World example
- [ ] Test Factorial example
- [ ] Test FizzBuzz example
- [ ] All tests passing
- [ ] Update taskSummary.md to 100%

---

## 💡 Implementation Notes

### Analysis Pass Order

**Why this order?**

1. **Entry Point Validation** (fast fail)
   - Check for main function first
   - If no main, abort (program can't run)

2. **Name Resolution** (build symbol table)
   - Register all functions and variables
   - Required for type checking (need to look up types)

3. **Type Checking** (requires symbol table)
   - Validate type compatibility
   - Needs symbols from pass 2

4. **Control Flow Validation**
   - Check return paths, break/continue
   - Can run independently but benefits from type info

### Test Program Examples

**Hello World (hello.fusion)**
```fusion
void function main()
    print("Hello, World!")
End function
```

**Factorial (factorial.fusion)**
```fusion
int function factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)
End function

int function main()
    int result = factorial(5)
    print("Factorial: {result}")
    return 0
End function
```

**FizzBuzz (fizzbuzz.fusion)**
```fusion
void function main()
    int i = 1
    while i <= 100
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

**Error Example (errors.fusion)**
```fusion
void function test()
    int x = "hello"  # Type error
    y = 5            # Undefined variable
    return 10        # Return in void function
End function

# No main function - error
```

### Expected Output

**Success:**
```
✓ Semantic analysis passed: hello.fusion
```

**With Warnings:**
```
Warning: Unreachable code detected
  at test.fusion:10:5

✓ Semantic analysis passed: test.fusion
1 warning(s) found
```

**With Errors:**
```
Error: Cannot assign string to variable of type int
  at errors.fusion:2:13

Error: Undefined variable: y
  at errors.fusion:3:5

Error: Function 'test' must return void, got int
  at errors.fusion:4:12

Error: Program must have a 'main' function
  at <program>:1:1

4 error(s) found
```

---

## ✅ Definition of Done

- All code implemented and documented
- All 30+ integration tests passing
- All Phase 3 unit tests still passing (188+ tests total)
- No regressions in Phase 1 & 2 tests (663 tests)
- Example programs (Hello World, Factorial, FizzBuzz) pass
- Compiler main.py successfully runs semantic analysis
- Error reporting is clear and helpful
- Code follows project style guidelines
- Task file updated to 100% complete
- taskSummary.md updated: Phase 3 complete!
- CLAUDE.md updated with Phase 3 completion status

---

## 🎉 Phase 3 Completion Criteria

When this task is complete:
- **All 6 Phase 3 tasks finished**
- **~188 semantic analysis tests passing**
- **Total tests: 851+ (663 lexer/parser + 188 semantic)**
- **Overall project: 85% complete**
- **Ready for Phase 4: Code Generation**
