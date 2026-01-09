# Task 2.4: Declaration Parsing

**Phase:** Phase 2 - Parser
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Tasks 2.2, 2.3 (Expression & Statement Parsing)
**Estimated Effort:** 3-4 hours
**Actual Effort:** 3 hours
**Last Updated:** 2025-12-01

---

## 🎯 Goal

Implement parsing for top-level declarations: functions and program structure.

---

## 📋 Sub-Tasks

- [x] 2.4.1 Function Declarations ✅
  - [x] 2.4.1.1 Parse return type ✅
  - [x] 2.4.1.2 Parse function keyword ✅
  - [x] 2.4.1.3 Parse function name ✅
  - [x] 2.4.1.4 Parse parameter list ✅
  - [x] 2.4.1.5 Parse function body (block or inline lambda) ✅

- [x] 2.4.2 Parameter Parsing ✅
  - [x] 2.4.2.1 Parse parameter type ✅
  - [x] 2.4.2.2 Parse parameter name ✅
  - [x] 2.4.2.3 Parse optional default value ✅
  - [x] 2.4.2.4 Handle multiple parameters ✅

- [x] 2.4.3 Lambda-Style Functions ✅
  - [x] 2.4.3.1 Inline lambda with `:`: `int add(int a, int b) : a + b` ✅
  - [x] 2.4.3.2 Multi-line lambda with indentation ✅
  - [x] 2.4.3.3 Distinguish from regular functions ✅

- [x] 2.4.4 Program Structure ✅
  - [x] 2.4.4.1 Parse top-level declarations ✅
  - [x] 2.4.4.2 Build ProgramNode (AST root) ✅
  - [x] 2.4.4.3 Handle main function detection (semantic analyzer will validate) ✅

- [x] 2.4.5 Unit Tests ✅
  - [x] 2.4.5.1 Test function declarations (17 tests) ✅
  - [x] 2.4.5.2 Test parameter parsing (3 tests) ✅
  - [x] 2.4.5.3 Test lambda-style functions (6 tests) ✅
  - [x] 2.4.5.4 Test program structure (2 tests) ✅
  - [x] 2.4.5.5 Test error handling (7 tests) ✅
  - [x] 2.4.5.6 Test edge cases (3 tests) ✅
  - **Total: 37 tests, all passing** ✅

---

## ✅ Acceptance Criteria

- [x] Function declarations parse correctly ✅
- [x] Parameters with default values supported ✅
- [x] Inline lambda syntax (`:`) works ✅
- [x] Multi-line function bodies work ✅
- [x] Program structure (ProgramNode) created correctly ✅
- [x] Unit tests pass (37 tests, all passing) ✅
- [x] Error messages for malformed declarations ✅

---

## 🏗️ Implementation Plan

### Program Parsing (Entry Point)

```python
# File: src/parser/parser.py

def parse_program(self) -> ProgramNode:
    """Parse entire program (entry point for parser)."""
    start_loc = self.peek().location
    declarations = []

    while not self.is_at_end():
        decl = self.parse_declaration()
        if decl:
            declarations.append(decl)

    return ProgramNode(
        location=start_loc,
        declarations=declarations
    )

def parse_declaration(self) -> Optional[ASTNode]:
    """Parse top-level declaration (function, var, etc.)."""
    # Function declaration
    # Fusion syntax: <return_type> function <name>(<params>) { body }
    if self.is_type_start():
        return_type = self.parse_type()

        if self.match(TokenType.FUNCTION):
            return self.parse_function_declaration(return_type)

        # Could be a global variable declaration
        # For MVP, we might not support global vars
        raise ParserError(self.peek(), "Global variables not supported in MVP")

    # Skip unexpected tokens
    self.advance()
    return None
```

### Function Declaration

```python
def parse_function_declaration(self, return_type: TypeNode) -> FunctionDecl:
    """Parse function declaration: int function add(int a, int b) { body }"""
    func_token = self.previous()  # FUNCTION token

    # Function name
    if not self.match(TokenType.IDENTIFIER):
        raise ParserError(self.peek(), "Expected function name")

    name = self.previous().value
    location = self.previous().location

    # Parameter list
    self.consume(TokenType.LPAREN, "Expected '(' after function name")

    parameters = []
    if not self.check(TokenType.RPAREN):
        parameters.append(self.parse_parameter())
        while self.match(TokenType.COMMA):
            parameters.append(self.parse_parameter())

    self.consume(TokenType.RPAREN, "Expected ')' after parameters")

    # Function body: block or inline lambda
    is_lambda = False
    body = None

    if self.match(TokenType.COLON):
        # Inline lambda: int function add(int a, int b) : a + b
        is_lambda = True

        # Check if single expression or multi-line
        if self.check(TokenType.INDENT):
            # Multi-line lambda with indentation
            body = self.parse_block_statement()
        else:
            # Single expression
            expr = self.parse_expression()
            self.consume_statement_terminator()
            body = expr  # Store expression directly

    else:
        # Regular function with block body
        body = self.parse_block_statement()

    # Check for End function (if using End keyword style)
    if self.match(TokenType.END):
        self.consume(TokenType.FUNCTION, "Expected 'function' after 'End'")

    return FunctionDecl(
        location=location,
        return_type=return_type,
        name=name,
        parameters=parameters,
        body=body,
        is_lambda=is_lambda
    )
```

### Parameter Parsing

```python
def parse_parameter(self) -> ParameterDecl:
    """Parse function parameter: int x = default_value"""
    # Parameter type
    param_type = self.parse_type()

    # Parameter name
    if not self.match(TokenType.IDENTIFIER):
        raise ParserError(self.peek(), "Expected parameter name")

    name = self.previous().value
    location = self.previous().location

    # Optional default value
    default_value = None
    if self.match(TokenType.ASSIGN):
        default_value = self.parse_expression()

    return ParameterDecl(
        location=location,
        param_type=param_type,
        name=name,
        default_value=default_value
    )
```

---

## 🧪 Test Strategy

### Test File: `tests/test_parser_declarations.py`

```python
import pytest
from src.parser.parser import Parser
from src.parser.ast_nodes import *
from src.lexer.lexer import Lexer

def parse_program(source: str) -> ProgramNode:
    """Helper: tokenize and parse program."""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_program()

def test_simple_function():
    """Test simple function: int function add(int a, int b) { return a + b }"""
    source = """
int function add(int a, int b) {
    return a + b
}
"""
    program = parse_program(source)
    assert len(program.declarations) == 1

    func = program.declarations[0]
    assert isinstance(func, FunctionDecl)
    assert func.name == "add"
    assert func.return_type.name == "int"
    assert len(func.parameters) == 2
    assert func.parameters[0].name == "a"
    assert func.parameters[1].name == "b"
    assert not func.is_lambda

def test_inline_lambda_function():
    """Test inline lambda: int function multiply(int x, int y) : x * y"""
    source = "int function multiply(int x, int y) : x * y"

    program = parse_program(source)
    assert len(program.declarations) == 1

    func = program.declarations[0]
    assert isinstance(func, FunctionDecl)
    assert func.name == "multiply"
    assert func.is_lambda
    assert isinstance(func.body, BinaryExpr)

def test_function_with_default_params():
    """Test function with default parameter values."""
    source = """
void function greet(string name = "World") {
    print("Hello, " + name)
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert len(func.parameters) == 1
    assert func.parameters[0].name == "name"
    assert func.parameters[0].default_value is not None
    assert func.parameters[0].default_value.value == "World"

def test_function_no_params():
    """Test function with no parameters."""
    source = """
int function getNumber() {
    return 42
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert len(func.parameters) == 0

def test_void_function():
    """Test void function (no return value)."""
    source = """
void function printHello() {
    print("Hello")
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.return_type.name == "void"

def test_main_function():
    """Test main function entry point."""
    source = """
int function main() {
    print("Hello, World!")
    return 0
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "main"
    assert func.return_type.name == "int"

def test_multiple_functions():
    """Test multiple function declarations."""
    source = """
int function add(int a, int b) {
    return a + b
}

int function multiply(int x, int y) {
    return x * y
}
"""
    program = parse_program(source)
    assert len(program.declarations) == 2
    assert program.declarations[0].name == "add"
    assert program.declarations[1].name == "multiply"

def test_indentation_style_function():
    """Test function with indentation block style."""
    source = """
int function factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "factorial"
    assert isinstance(func.body, BlockStmt)

def test_end_keyword_style_function():
    """Test function with End keyword block style."""
    source = """
int function factorial(int n)
    if n <= 1
        return 1
    End if
    return n * factorial(n - 1)
End function
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "factorial"

def test_multiline_lambda():
    """Test multi-line lambda with indentation."""
    source = """
int function factorial(int n) :
    if n <= 1
        return 1
    return n * factorial(n - 1)
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.is_lambda
    assert isinstance(func.body, BlockStmt)
```

---

## 📝 Implementation Notes

### Function Syntax Variations

Fusion supports multiple function body styles:

**1. Block with braces:**
```fusion
int function add(int a, int b) {
    return a + b
}
```

**2. Block with indentation:**
```fusion
int function add(int a, int b)
    return a + b
```

**3. Block with End keyword:**
```fusion
int function add(int a, int b)
    return a + b
End function
```

**4. Inline lambda (single expression):**
```fusion
int function add(int a, int b) : a + b
```

**5. Multi-line lambda:**
```fusion
int function factorial(int n) :
    if n <= 1
        return 1
    return n * factorial(n - 1)
```

### Parameter Default Values

Parameters can have default values:
```fusion
void function greet(string name = "World") {
    print("Hello, " + name)
}
```

Rules:
- Parameters with defaults must come after required parameters
- Default value must be a compile-time constant expression (for MVP: literals only)

### Main Function

Every Fusion program must have a `main` function:
```fusion
int function main() {
    // Program entry point
    return 0
}
```

Parser doesn't enforce this (semantic analyzer will).

### MVP Scope

**Include:**
- Function declarations with return types
- Parameter lists with default values
- Inline lambda syntax (`:`)
- All three block styles
- void functions

**Exclude:**
- Global variable declarations (add if needed)
- Class/struct declarations
- Interface declarations
- Generic functions
- Function overloading (semantic analyzer handles)

---

**File:** task-2.4.md
**Last Updated:** 2025-11-10
