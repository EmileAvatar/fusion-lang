# Task 2.5: Type Parsing

**Phase:** Phase 2 - Parser
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 2.1 (AST Node Definitions)
**Estimated Effort:** 2-3 hours
**Actual Effort:** 1 hour
**Last Updated:** 2025-12-01

---

## 🎯 Goal

Implement type parsing for primitive types and type expressions.

---

## 📋 Sub-Tasks

- [x] 2.5.1 Primitive Types ✅
  - [x] 2.5.1.1 Parse `int` type ✅
  - [x] 2.5.1.2 Parse `float` type ✅
  - [x] 2.5.1.3 Parse `double` type ✅
  - [x] 2.5.1.4 Parse `string` type ✅
  - [x] 2.5.1.5 Parse `bool` type ✅
  - [x] 2.5.1.6 Parse `char` type ✅
  - [x] 2.5.1.7 Parse `void` type ✅

- [x] 2.5.2 Type Detection ✅
  - [x] 2.5.2.1 `is_type_start()` helper ✅
  - [x] 2.5.2.2 Distinguish types from identifiers ✅
  - [x] 2.5.2.3 Handle type keywords ✅

- [x] 2.5.3 Unit Tests ✅
  - [x] 2.5.3.1 Test primitive type parsing (7 tests) ✅
  - [x] 2.5.3.2 Test types in contexts (13 tests) ✅
  - [x] 2.5.3.3 Test type detection helpers (4 tests) ✅
  - [x] 2.5.3.4 Test error handling (5 tests) ✅
  - **Total: 29 tests, all passing** ✅

---

## ✅ Acceptance Criteria

- [x] All MVP primitive types parse correctly ✅
- [x] Type detection helpers work correctly ✅
- [x] Error messages for invalid types ✅
- [x] Unit tests pass (29 tests) ✅
- [x] Type nodes have proper source location tracking ✅

---

## 🏗️ Implementation Plan

### Type Parsing

```python
# File: src/parser/parser.py

def parse_type(self) -> TypeNode:
    """Parse type expression."""
    # For MVP, only primitive types are supported
    return self.parse_primitive_type()

def parse_primitive_type(self) -> PrimitiveType:
    """Parse primitive type: int, float, double, string, bool, char, void"""
    if self.match(TokenType.INT):
        return PrimitiveType(
            location=self.previous().location,
            name="int"
        )

    if self.match(TokenType.FLOAT):
        return PrimitiveType(
            location=self.previous().location,
            name="float"
        )

    if self.match(TokenType.DOUBLE):
        return PrimitiveType(
            location=self.previous().location,
            name="double"
        )

    if self.match(TokenType.STRING):
        return PrimitiveType(
            location=self.previous().location,
            name="string"
        )

    if self.match(TokenType.BOOL):
        return PrimitiveType(
            location=self.previous().location,
            name="bool"
        )

    if self.match(TokenType.CHAR):
        return PrimitiveType(
            location=self.previous().location,
            name="char"
        )

    if self.match(TokenType.VOID):
        return PrimitiveType(
            location=self.previous().location,
            name="void"
        )

    raise ParserError(
        self.peek(),
        f"Expected type, got '{self.peek().value}'"
    )
```

### Type Detection Helpers

```python
def is_type_start(self) -> bool:
    """Check if current token starts a type."""
    return self.check_any(
        TokenType.INT,
        TokenType.FLOAT,
        TokenType.DOUBLE,
        TokenType.STRING,
        TokenType.BOOL,
        TokenType.CHAR,
        TokenType.VOID
    )

def check_any(self, *token_types: TokenType) -> bool:
    """Check if current token matches any of the given types."""
    for token_type in token_types:
        if self.check(token_type):
            return True
    return False
```

---

## 🧪 Test Strategy

### Test File: `tests/test_parser_types.py`

```python
import pytest
from src.parser.parser import Parser
from src.parser.ast_nodes import *
from src.lexer.lexer import Lexer

def parse_type_from_source(source: str) -> TypeNode:
    """Helper: tokenize and parse type."""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_type()

def test_int_type():
    """Test int type parsing."""
    type_node = parse_type_from_source("int")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "int"

def test_float_type():
    """Test float type parsing."""
    type_node = parse_type_from_source("float")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "float"

def test_double_type():
    """Test double type parsing."""
    type_node = parse_type_from_source("double")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "double"

def test_string_type():
    """Test string type parsing."""
    type_node = parse_type_from_source("string")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "string"

def test_bool_type():
    """Test bool type parsing."""
    type_node = parse_type_from_source("bool")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "bool"

def test_char_type():
    """Test char type parsing."""
    type_node = parse_type_from_source("char")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "char"

def test_void_type():
    """Test void type parsing."""
    type_node = parse_type_from_source("void")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "void"

def test_invalid_type():
    """Test error on invalid type."""
    with pytest.raises(ParserError):
        parse_type_from_source("invalid_type")

def test_type_in_var_declaration():
    """Test type parsing in variable declaration context."""
    source = "int x = 5"
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    stmt = parser.parse_statement()

    assert isinstance(stmt, VarDeclStmt)
    assert isinstance(stmt.var_type, PrimitiveType)
    assert stmt.var_type.name == "int"

def test_type_in_function_declaration():
    """Test type parsing in function declaration context."""
    source = """
int function add(int a, int b) {
    return a + b
}
"""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse_program()

    func = program.declarations[0]
    assert isinstance(func.return_type, PrimitiveType)
    assert func.return_type.name == "int"
    assert func.parameters[0].param_type.name == "int"
    assert func.parameters[1].param_type.name == "int"

def test_is_type_start():
    """Test type detection helper."""
    lexer = Lexer("int x", "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)

    assert parser.is_type_start()  # 'int' is a type

    parser.advance()  # Move to 'x'
    assert not parser.is_type_start()  # 'x' is not a type
```

---

## 📝 Implementation Notes

### MVP Type System

For MVP, only primitive types are supported:
- `int` - 32-bit signed integer
- `float` - 32-bit floating point
- `double` - 64-bit floating point
- `string` - UTF-8 string
- `bool` - Boolean (true/false)
- `char` - Single character
- `void` - No return value (functions only)

### Future Type Extensions (Not MVP)

These will be added in later phases:
- **Array types**: `int[]`, `string[]`
- **Generic types**: `List<int>`, `Dictionary<string, int>`
- **User-defined types**: classes, structs, interfaces
- **Function types**: `(int, int) -> int` (for lambda type hints)
- **Optional types**: `int?`, `string?`
- **Tuple types**: `(int, string)`
- **Memory qualifiers**: `Unique<int>`, `Shared<string>`, `Weak<Object>`

### Type vs Identifier Disambiguation

In Fusion, types and identifiers can be distinguished by:
1. **Keywords**: Type keywords (`int`, `float`, etc.) are reserved
2. **Position**: Types appear in specific contexts (after function, before variable name)
3. **Case sensitivity**: Types are lowercase, user identifiers can be mixed case

The parser uses `is_type_start()` to check if the current token is a type keyword.

### Error Messages

Provide clear error messages:
- "Expected type, got 'identifier'" - when type required but identifier found
- "Unknown type 'foo'" - when invalid type keyword used
- "Type 'void' not allowed here" - when void used in invalid context (e.g., variable type)

### Type Node Structure

```python
@dataclass
class TypeNode(ASTNode):
    """Base class for all type nodes."""
    pass

@dataclass
class PrimitiveType(TypeNode):
    """Primitive type: int, float, string, bool, char, void"""
    name: str  # "int", "float", "string", "bool", "char", "void"
```

For MVP, `PrimitiveType` is sufficient. Future phases will add:
- `ArrayType(element_type: TypeNode, size: Optional[int])`
- `GenericType(name: str, type_args: List[TypeNode])`
- `FunctionType(param_types: List[TypeNode], return_type: TypeNode)`
- `UserDefinedType(name: str)`

---

## 🔗 Related Files

- [fusion-language-spec.md](../files/fusion-language-spec.md) - Type system specification
- [src/parser/ast_nodes.py](../src/parser/ast_nodes.py) - AST node definitions
- [task-2.1.md](task-2.1.md) - AST Node Definitions task

---

**File:** task-2.5.md
**Last Updated:** 2025-11-10
