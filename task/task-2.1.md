# Task 2.1: AST Node Definitions

**Phase:** Phase 2 - Parser
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Phase 1 complete (Lexer)
**Estimated Effort:** 3-4 hours
**Last Updated:** 2025-11-25

---

## 🎯 Goal

Define Abstract Syntax Tree (AST) node classes for representing Fusion program structure.

---

## 📋 Sub-Tasks

- [x] 2.1.1 Base AST Node Infrastructure
  - [x] 2.1.1.1 Create `ASTNode` base class
  - [x] 2.1.1.2 Add source location tracking
  - [x] 2.1.1.3 Add visitor pattern support
  - [x] 2.1.1.4 Add `__repr__` for debugging (auto via @dataclass)

- [x] 2.1.2 Expression Nodes
  - [x] 2.1.2.1 `LiteralExpr` (int, float, string, char, bool)
  - [x] 2.1.2.2 `IdentifierExpr` (variable references)
  - [x] 2.1.2.3 `BinaryExpr` (+, -, *, /, ==, !=, <, >, etc.)
  - [x] 2.1.2.4 `UnaryExpr` (-, not, !)
  - [x] 2.1.2.5 `CallExpr` (function calls)
  - [x] 2.1.2.6 `LambdaExpr` (inline lambdas with `:`)
  - [x] 2.1.2.7 `InterpolatedStringExpr` (string with {var})

- [x] 2.1.3 Statement Nodes
  - [x] 2.1.3.1 `ExpressionStmt` (expression as statement)
  - [x] 2.1.3.2 `VarDeclStmt` (variable declarations)
  - [x] 2.1.3.3 `AssignmentStmt` (x = value)
  - [x] 2.1.3.4 `IfStmt` (if/else blocks)
  - [x] 2.1.3.5 `WhileStmt` (while loops)
  - [x] 2.1.3.6 `ForStmt` (for loops)
  - [x] 2.1.3.7 `ReturnStmt` (return statements)
  - [x] 2.1.3.8 `BlockStmt` (statement blocks)

- [x] 2.1.4 Declaration Nodes
  - [x] 2.1.4.1 `FunctionDecl` (function declarations)
  - [x] 2.1.4.2 `ParameterDecl` (function parameters)
  - [x] 2.1.4.3 `ProgramNode` (root node)

- [x] 2.1.5 Type Nodes
  - [x] 2.1.5.1 `TypeNode` base class
  - [x] 2.1.5.2 `PrimitiveType` (int, float, string, bool, char, void)
  - [x] 2.1.5.3 `FunctionType` (for lambda types)

- [x] 2.1.6 Unit Tests
  - [x] 2.1.6.1 Test AST node creation (53 tests total)
  - [x] 2.1.6.2 Test source location tracking
  - [x] 2.1.6.3 Test visitor pattern
  - [x] 2.1.6.4 Test node equality/repr

---

## ✅ Acceptance Criteria

- [x] All AST node classes defined with proper fields
- [x] Source location tracked for all nodes (for error messages)
- [x] Visitor pattern implemented for tree traversal
- [x] All nodes have `__repr__` for debugging (auto via @dataclass)
- [x] Unit tests pass (53 tests, all passing)
- [x] Type hints for all node fields
- [x] Documentation strings for each node class

---

## 🏗️ Implementation Plan

### Base AST Node Structure

```python
# File: src/parser/ast_nodes.py
from dataclasses import dataclass
from typing import List, Optional, Any
from src.lexer.token import SourceLocation

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    location: SourceLocation

    def accept(self, visitor):
        """Visitor pattern for tree traversal."""
        method_name = f'visit_{self.__class__.__name__}'
        method = getattr(visitor, method_name, None)
        if method:
            return method(self)
        raise NotImplementedError(f"Visitor does not implement {method_name}")
```

### Expression Nodes

```python
@dataclass
class LiteralExpr(ASTNode):
    """Literal expression: 42, 3.14, "hello", 'c', true, false, null"""
    value: Any  # int, float, str, char, bool, None
    type_hint: str  # "int", "float", "string", "char", "bool", "null"

@dataclass
class IdentifierExpr(ASTNode):
    """Identifier expression: variable_name"""
    name: str

@dataclass
class BinaryExpr(ASTNode):
    """Binary expression: left op right"""
    left: ASTNode
    operator: str  # "+", "-", "*", "/", "==", "!=", "<", ">", etc.
    right: ASTNode

@dataclass
class UnaryExpr(ASTNode):
    """Unary expression: op operand"""
    operator: str  # "-", "not", "!"
    operand: ASTNode

@dataclass
class CallExpr(ASTNode):
    """Function call: func(arg1, arg2, ...)"""
    callee: ASTNode  # Usually IdentifierExpr
    arguments: List[ASTNode]

@dataclass
class LambdaExpr(ASTNode):
    """Lambda expression: (int x, int y) : x + y"""
    parameters: List['ParameterDecl']
    return_type: 'TypeNode'
    body: ASTNode  # Single expression or BlockStmt

@dataclass
class InterpolatedStringExpr(ASTNode):
    """Interpolated string: "Hello {name}, you are {age} years old" """
    parts: List[str]  # Static string parts
    expressions: List[ASTNode]  # Expression parts (inline or positional)
```

### Statement Nodes

```python
@dataclass
class ExpressionStmt(ASTNode):
    """Expression as statement: print(x)"""
    expression: ASTNode

@dataclass
class VarDeclStmt(ASTNode):
    """Variable declaration: int x = 5"""
    var_type: 'TypeNode'
    name: str
    initializer: Optional[ASTNode]

@dataclass
class AssignmentStmt(ASTNode):
    """Assignment: x = value"""
    target: ASTNode  # Usually IdentifierExpr
    value: ASTNode

@dataclass
class IfStmt(ASTNode):
    """If statement: if condition { body } else { else_body }"""
    condition: ASTNode
    then_branch: ASTNode  # Usually BlockStmt
    else_branch: Optional[ASTNode]

@dataclass
class WhileStmt(ASTNode):
    """While loop: while condition { body }"""
    condition: ASTNode
    body: ASTNode

@dataclass
class ForStmt(ASTNode):
    """For loop: for i in range { body }"""
    variable: str
    iterable: ASTNode
    body: ASTNode

@dataclass
class ReturnStmt(ASTNode):
    """Return statement: return value"""
    value: Optional[ASTNode]

@dataclass
class BlockStmt(ASTNode):
    """Block statement: { stmt1; stmt2; ... }"""
    statements: List[ASTNode]
```

### Declaration Nodes

```python
@dataclass
class ParameterDecl(ASTNode):
    """Function parameter: int x = default_value"""
    param_type: 'TypeNode'
    name: str
    default_value: Optional[ASTNode]

@dataclass
class FunctionDecl(ASTNode):
    """Function declaration: int function add(int a, int b) { return a + b }"""
    return_type: 'TypeNode'
    name: str
    parameters: List[ParameterDecl]
    body: ASTNode  # BlockStmt or single expression (for lambdas)
    is_lambda: bool = False  # True for inline lambdas with ":"

@dataclass
class ProgramNode(ASTNode):
    """Root node of the AST: entire program"""
    declarations: List[ASTNode]  # FunctionDecl, VarDeclStmt, etc.
```

### Type Nodes

```python
@dataclass
class TypeNode(ASTNode):
    """Base class for type nodes."""
    pass

@dataclass
class PrimitiveType(TypeNode):
    """Primitive type: int, float, string, bool, char, void"""
    name: str  # "int", "float", "string", "bool", "char", "void"

@dataclass
class FunctionType(TypeNode):
    """Function type (for lambdas): (int, int) -> int"""
    parameter_types: List[TypeNode]
    return_type: TypeNode
```

---

## 🧪 Test Strategy

### Test File: `tests/test_ast_nodes.py`

```python
import pytest
from src.parser.ast_nodes import *
from src.lexer.token import SourceLocation

def test_literal_expr():
    """Test literal expression node creation."""
    loc = SourceLocation("test.fusion", 1, 1)

    # Integer literal
    node = LiteralExpr(loc, value=42, type_hint="int")
    assert node.value == 42
    assert node.type_hint == "int"

    # String literal
    node = LiteralExpr(loc, value="hello", type_hint="string")
    assert node.value == "hello"

def test_binary_expr():
    """Test binary expression node creation."""
    loc = SourceLocation("test.fusion", 1, 1)

    left = LiteralExpr(loc, value=5, type_hint="int")
    right = LiteralExpr(loc, value=3, type_hint="int")
    node = BinaryExpr(loc, left=left, operator="+", right=right)

    assert node.operator == "+"
    assert node.left.value == 5
    assert node.right.value == 3

def test_function_decl():
    """Test function declaration node creation."""
    loc = SourceLocation("test.fusion", 1, 1)

    return_type = PrimitiveType(loc, name="int")
    param1 = ParameterDecl(
        loc,
        param_type=PrimitiveType(loc, name="int"),
        name="a",
        default_value=None
    )
    param2 = ParameterDecl(
        loc,
        param_type=PrimitiveType(loc, name="int"),
        name="b",
        default_value=None
    )
    body = ReturnStmt(loc, value=BinaryExpr(
        loc,
        left=IdentifierExpr(loc, name="a"),
        operator="+",
        right=IdentifierExpr(loc, name="b")
    ))

    func = FunctionDecl(
        loc,
        return_type=return_type,
        name="add",
        parameters=[param1, param2],
        body=body
    )

    assert func.name == "add"
    assert len(func.parameters) == 2

def test_visitor_pattern():
    """Test visitor pattern implementation."""
    loc = SourceLocation("test.fusion", 1, 1)
    node = LiteralExpr(loc, value=42, type_hint="int")

    class TestVisitor:
        def visit_LiteralExpr(self, node):
            return f"Visited literal: {node.value}"

    visitor = TestVisitor()
    result = node.accept(visitor)
    assert result == "Visited literal: 42"
```

---

## 📝 Implementation Notes

### Design Decisions

1. **Use `@dataclass`**: Simplifies node creation, provides auto `__init__`, `__repr__`, etc.
2. **Source location on all nodes**: Essential for error messages in later phases
3. **Visitor pattern**: Allows clean separation of tree traversal logic (semantic analysis, code generation)
4. **Type hints**: Improves code clarity and IDE support
5. **Immutable where possible**: Use frozen dataclasses for safety (optional)

### MVP Scope

**Include in MVP:**
- Basic types: int, float, string, bool, char, void
- Expressions: literals, identifiers, binary/unary ops, calls, lambdas
- Statements: var decl, assignment, if/else, while, for, return, blocks
- Declarations: functions, parameters

**Exclude from MVP:**
- Classes, structs, interfaces
- Enums
- Generic types
- Property nodes
- Import/module nodes (add if needed)
- Error handling nodes (try/catch)

### File Organization

```
src/parser/
├── __init__.py
├── ast_nodes.py       # All AST node definitions (this task)
└── parser.py          # Parser implementation (tasks 2.2-2.5)

tests/
├── test_ast_nodes.py  # AST node tests (this task)
└── test_parser.py     # Parser tests (task 2.6)
```

---

## 🔗 Related Documentation

- [fusion.ebnf](../files/fusion.ebnf) - Grammar specification for AST structure
- [fusion-language-spec.md](../files/fusion-language-spec.md) - Language specification
- [taskSummary.md](../taskSummary.md) - Overall project progress

---

**File:** task-2.1.md
**Last Updated:** 2025-11-10
