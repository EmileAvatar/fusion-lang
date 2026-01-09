# Task 2.3: Statement Parsing

**Phase:** Phase 2 - Parser
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 2.2 (Expression Parsing)
**Estimated Effort:** 4-5 hours
**Actual Effort:** 4 hours
**Last Updated:** 2025-12-01

---

## 🎯 Goal

Implement statement parsing for control flow, assignments, variable declarations, and blocks.

---

## 📋 Sub-Tasks

- [x] 2.3.1 Simple Statements ✅
  - [x] 2.3.1.1 Expression statements: `print(x)` ✅
  - [x] 2.3.1.2 Variable declarations: `int x = 5` ✅
  - [x] 2.3.1.3 Assignments: `x = value` ✅
  - [x] 2.3.1.4 Return statements: `return value` ✅

- [x] 2.3.2 Control Flow Statements ✅
  - [x] 2.3.2.1 If statements: `if cond { body }` ✅
  - [x] 2.3.2.2 If-else statements: `if cond { body } else { else_body }` ✅
  - [x] 2.3.2.3 While loops: `while cond { body }` ✅
  - [x] 2.3.2.4 For loops: `for i in range { body }` ✅

- [x] 2.3.3 Block Statements ✅
  - [x] 2.3.3.1 Brace blocks: `{ stmt1; stmt2; }` ✅
  - [x] 2.3.3.2 Indentation blocks (INDENT/DEDENT tokens) ✅
  - [x] 2.3.3.3 End keyword blocks: `if cond ... End if` ✅
  - [x] 2.3.3.4 Empty blocks ✅

- [x] 2.3.4 Statement Disambiguation ✅
  - [x] 2.3.4.1 Distinguish var decl from assignment ✅
  - [x] 2.3.4.2 Distinguish expr stmt from other stmts ✅
  - [x] 2.3.4.3 Handle optional newlines (semicolons not supported by lexer) ✅

- [x] 2.3.5 Unit Tests ✅
  - [x] 2.3.5.1 Test simple statements (12 tests) ✅
  - [x] 2.3.5.2 Test control flow (23 tests) ✅
  - [x] 2.3.5.3 Test block statements (11 tests) ✅
  - [x] 2.3.5.4 Test error handling (7 tests) ✅
  - [x] 2.3.5.5 Test edge cases (5 tests) ✅
  - **Total: 46 tests, all passing** ✅

---

## ✅ Acceptance Criteria

- [x] All statement types parse correctly ✅
- [x] Three block styles supported (braces, indentation, End keywords) ✅
- [x] Nested blocks work correctly ✅
- [x] Error messages for malformed statements ✅
- [x] Unit tests pass (46 tests, all passing) ✅
- [x] Newlines handled correctly (lexer doesn't tokenize semicolons) ✅

---

## 🏗️ Implementation Plan

### Statement Parsing (Entry Point)

```python
# File: src/parser/parser.py

def parse_statement(self) -> ASTNode:
    """Parse any statement (entry point)."""
    # Return statement
    if self.match(TokenType.RETURN):
        return self.parse_return_statement()

    # If statement
    if self.match(TokenType.IF):
        return self.parse_if_statement()

    # While loop
    if self.match(TokenType.WHILE):
        return self.parse_while_statement()

    # For loop
    if self.match(TokenType.FOR):
        return self.parse_for_statement()

    # Block statement
    if self.check(TokenType.LBRACE) or self.check(TokenType.INDENT):
        return self.parse_block_statement()

    # Variable declaration or assignment or expression statement
    return self.parse_simple_statement()

def parse_simple_statement(self) -> ASTNode:
    """Parse simple statements: var decl, assignment, or expression."""
    # Check if it's a variable declaration (starts with type)
    if self.is_type_start():
        return self.parse_var_declaration()

    # Otherwise, parse as expression (could be assignment)
    expr = self.parse_expression()

    # Check for assignment: expr = value
    if self.match(TokenType.ASSIGN):
        value = self.parse_expression()
        self.consume_statement_terminator()
        return AssignmentStmt(
            location=expr.location,
            target=expr,
            value=value
        )

    # Expression statement
    self.consume_statement_terminator()
    return ExpressionStmt(
        location=expr.location,
        expression=expr
    )

def consume_statement_terminator(self):
    """Consume optional semicolon or newline."""
    # Semicolons are optional in many contexts
    self.match(TokenType.SEMICOLON)
    # Newlines are handled by lexer (not tokens in most cases)
```

### Variable Declaration

```python
def parse_var_declaration(self) -> ASTNode:
    """Parse variable declaration: int x = 5"""
    var_type = self.parse_type()

    if not self.match(TokenType.IDENTIFIER):
        raise ParserError(self.peek(), "Expected variable name")

    name = self.previous().value
    location = self.previous().location

    # Optional initializer
    initializer = None
    if self.match(TokenType.ASSIGN):
        initializer = self.parse_expression()

    self.consume_statement_terminator()

    return VarDeclStmt(
        location=location,
        var_type=var_type,
        name=name,
        initializer=initializer
    )
```

### Return Statement

```python
def parse_return_statement(self) -> ASTNode:
    """Parse return statement: return value"""
    return_token = self.previous()  # RETURN token

    # Optional return value
    value = None
    if not self.check(TokenType.SEMICOLON) and not self.is_block_end():
        value = self.parse_expression()

    self.consume_statement_terminator()

    return ReturnStmt(
        location=return_token.location,
        value=value
    )
```

### If Statement

```python
def parse_if_statement(self) -> ASTNode:
    """Parse if statement: if condition { body } else { else_body }"""
    if_token = self.previous()  # IF token

    # Condition
    condition = self.parse_expression()

    # Then branch (block)
    then_branch = self.parse_block_statement()

    # Optional else branch
    else_branch = None
    if self.match(TokenType.ELSE):
        # Else can be followed by if (elif) or block
        if self.match(TokenType.IF):
            else_branch = self.parse_if_statement()
        else:
            else_branch = self.parse_block_statement()

    # Check for End if (if using End keyword style)
    if self.match(TokenType.END):
        self.consume(TokenType.IF, "Expected 'if' after 'End'")

    return IfStmt(
        location=if_token.location,
        condition=condition,
        then_branch=then_branch,
        else_branch=else_branch
    )
```

### While Loop

```python
def parse_while_statement(self) -> ASTNode:
    """Parse while loop: while condition { body }"""
    while_token = self.previous()  # WHILE token

    # Condition
    condition = self.parse_expression()

    # Body
    body = self.parse_block_statement()

    # Check for End while (if using End keyword style)
    if self.match(TokenType.END):
        self.consume(TokenType.WHILE, "Expected 'while' after 'End'")

    return WhileStmt(
        location=while_token.location,
        condition=condition,
        body=body
    )
```

### For Loop

```python
def parse_for_statement(self) -> ASTNode:
    """Parse for loop: for i in range { body }"""
    for_token = self.previous()  # FOR token

    # Loop variable
    if not self.match(TokenType.IDENTIFIER):
        raise ParserError(self.peek(), "Expected loop variable name")

    variable = self.previous().value

    # 'in' keyword
    self.consume(TokenType.IN, "Expected 'in' after loop variable")

    # Iterable expression
    iterable = self.parse_expression()

    # Body
    body = self.parse_block_statement()

    # Check for End for (if using End keyword style)
    if self.match(TokenType.END):
        self.consume(TokenType.FOR, "Expected 'for' after 'End'")

    return ForStmt(
        location=for_token.location,
        variable=variable,
        iterable=iterable,
        body=body
    )
```

### Block Statement

```python
def parse_block_statement(self) -> ASTNode:
    """Parse block statement (braces, indentation, or End keyword)."""
    start_loc = self.peek().location

    # Brace block: { stmt1; stmt2; }
    if self.match(TokenType.LBRACE):
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.parse_statement())

        self.consume(TokenType.RBRACE, "Expected '}' after block")
        return BlockStmt(location=start_loc, statements=statements)

    # Indentation block: INDENT stmt1 stmt2 DEDENT
    if self.match(TokenType.INDENT):
        statements = []
        while not self.check(TokenType.DEDENT) and not self.is_at_end():
            statements.append(self.parse_statement())

        self.consume(TokenType.DEDENT, "Expected DEDENT after indented block")
        return BlockStmt(location=start_loc, statements=statements)

    # End keyword block: handled by caller (if/while/for)
    # Single statement without block
    return self.parse_statement()

def is_block_end(self) -> bool:
    """Check if at end of block."""
    return (self.check(TokenType.RBRACE) or
            self.check(TokenType.DEDENT) or
            self.check(TokenType.END) or
            self.is_at_end())
```

### Type Checking Helpers

```python
def is_type_start(self) -> bool:
    """Check if current token starts a type."""
    return self.check_any(
        TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
        TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
        TokenType.VOID
    )

def check_any(self, *token_types: TokenType) -> bool:
    """Check if current token matches any type."""
    for token_type in token_types:
        if self.check(token_type):
            return True
    return False
```

---

## 🧪 Test Strategy

### Test File: `tests/test_parser_statements.py`

```python
import pytest
from src.parser.parser import Parser
from src.parser.ast_nodes import *
from src.lexer.lexer import Lexer

def parse_stmt(source: str) -> ASTNode:
    """Helper: tokenize and parse statement."""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_statement()

def test_var_declaration():
    """Test variable declaration: int x = 5"""
    stmt = parse_stmt("int x = 5")
    assert isinstance(stmt, VarDeclStmt)
    assert stmt.name == "x"
    assert stmt.var_type.name == "int"
    assert stmt.initializer.value == 5

def test_assignment():
    """Test assignment: x = 10"""
    stmt = parse_stmt("x = 10")
    assert isinstance(stmt, AssignmentStmt)
    assert stmt.target.name == "x"
    assert stmt.value.value == 10

def test_return_statement():
    """Test return: return 42"""
    stmt = parse_stmt("return 42")
    assert isinstance(stmt, ReturnStmt)
    assert stmt.value.value == 42

def test_if_statement():
    """Test if statement: if x > 0 { return x }"""
    source = """
if x > 0 {
    return x
}
"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert isinstance(stmt.then_branch, BlockStmt)

def test_if_else_statement():
    """Test if-else: if x > 0 { return x } else { return 0 }"""
    source = """
if x > 0 {
    return x
} else {
    return 0
}
"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert stmt.else_branch is not None

def test_while_loop():
    """Test while loop: while x > 0 { x = x - 1 }"""
    source = """
while x > 0 {
    x = x - 1
}
"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, WhileStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert isinstance(stmt.body, BlockStmt)

def test_for_loop():
    """Test for loop: for i in range { print(i) }"""
    source = """
for i in range {
    print(i)
}
"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, ForStmt)
    assert stmt.variable == "i"

def test_indentation_block():
    """Test indentation block style."""
    source = """
if x > 0
    return x
"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.then_branch, BlockStmt)

def test_end_keyword_block():
    """Test End keyword block style."""
    source = """
if x > 0
    return x
End if
"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)

def test_nested_blocks():
    """Test nested if statements."""
    source = """
if x > 0 {
    if y > 0 {
        return x + y
    }
}
"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    inner_stmt = stmt.then_branch.statements[0]
    assert isinstance(inner_stmt, IfStmt)
```

---

## 📝 Implementation Notes

### Block Style Detection

The lexer already handles block style detection and generates appropriate tokens:
- **Braces**: `{` and `}` tokens
- **Indentation**: `INDENT` and `DEDENT` tokens
- **End keywords**: `End if`, `End while`, etc.

The parser must support all three styles and handle mixed styles correctly.

### Semicolon Handling

Semicolons are **optional** in most contexts:
- After simple statements (var decl, assignment, return, expr)
- NOT required after blocks (if, while, for)
- NOT required before closing brace `}`
- NOT required before DEDENT

### Error Recovery

For MVP, panic mode recovery on statement boundaries:
- Synchronize on semicolons, closing braces, DEDENT tokens
- Skip tokens until next statement start keyword

### MVP Scope

**Include:**
- Variable declarations with initializers
- Assignments
- Return statements
- If/else statements
- While loops
- For loops (basic iteration)
- Block statements (all three styles)
- Expression statements

**Exclude:**
- Break/continue statements (add if needed)
- Switch/match statements
- Try/catch blocks
- Multiple variable declarations: `int x = 1, y = 2`

---

**File:** task-2.3.md
**Last Updated:** 2025-11-10
