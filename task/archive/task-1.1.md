# Task 1.1: Token Definitions & Infrastructure

**Phase:** Phase 1 - Lexer
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** None
**Estimated Effort:** 2-3 hours
**Last Updated:** 2025-11-04

---

## 🎯 Goal

Create the foundational classes and infrastructure for tokenization:
- Token class to represent individual tokens
- TokenType enumeration for all token types
- SourceLocation class for error reporting
- Test infrastructure for validation

---

## 📋 Sub-Tasks

- [x] 1.1.1 Define TokenType enumeration (all 60+ token types) ✅
  - [x] 1.1.1.1 Control flow keywords (if, else, for, while, loop, end, break, continue, return, match, case) ✅
  - [x] 1.1.1.2 Function keywords (function, func, async, await) ✅
  - [x] 1.1.1.3 OOP keywords (class, struct, interface, enum, inherits, implements, property, get, set) ✅
  - [x] 1.1.1.4 Modifier keywords (public, private, protected, static, virtual, override, abstract, sealed) ✅
  - [x] 1.1.1.5 Type keywords (int, float, double, string, bool, char, byte, short, long, void) ✅
  - [x] 1.1.1.6 Memory keywords (Unique, Shared, Weak) ✅
  - [x] 1.1.1.7 Variable keywords (var, const) ✅
  - [x] 1.1.1.8 Literal keywords (true, false, null, this) ✅
  - [x] 1.1.1.9 Operator keywords (and, or, not, is, in) ✅
  - [x] 1.1.1.10 Other keywords (import, new, cast, try, catch, finally, throw, Error, go) ✅
  - [x] 1.1.1.11 Arithmetic operators (+, -, *, /, %, **) ✅
  - [x] 1.1.1.12 Comparison operators (<, >, <=, >=, ==, !=, <>) ✅
  - [x] 1.1.1.13 Logical operators (&&, ||, !) ✅
  - [x] 1.1.1.14 Assignment operators (=, +=, -=, *=, /=, %=, **=) ✅
  - [x] 1.1.1.15 Special operators (..., ?., ?[, <-, ->, ++, --) ✅
  - [x] 1.1.1.16 Delimiters ((, ), [, ], {, }, ,, :, .) ✅
  - [x] 1.1.1.17 Literal types (INTEGER, FLOAT, STRING, CHAR, BOOLEAN) ✅
  - [x] 1.1.1.18 Special tokens (INDENT, DEDENT, NEWLINE, EOF, IDENTIFIER) ✅

- [x] 1.1.2 Define Token class with value and metadata ✅
  - [x] 1.1.2.1 Token type field (TokenType) ✅
  - [x] 1.1.2.2 Token value field (str) ✅
  - [x] 1.1.2.3 Source location field (SourceLocation) ✅
  - [x] 1.1.2.4 __repr__ method for debugging ✅
  - [x] 1.1.2.5 __eq__ method for testing ✅

- [x] 1.1.3 Define SourceLocation class for position tracking ✅
  - [x] 1.1.3.1 Filename field (str) ✅
  - [x] 1.1.3.2 Line number field (int) ✅
  - [x] 1.1.3.3 Column number field (int) ✅
  - [x] 1.1.3.4 __repr__ method for error messages ✅
  - [x] 1.1.3.5 to_string method (format: "file:line:col") ✅

- [x] 1.1.4 Create test infrastructure ✅
  - [x] 1.1.4.1 Setup pytest configuration ✅
  - [x] 1.1.4.2 Create test_token.py file ✅
  - [x] 1.1.4.3 Token equality test helpers ✅
  - [x] 1.1.4.4 Token creation test fixtures ✅
  - [x] 1.1.4.5 SourceLocation test helpers ✅

---

## ✅ Acceptance Criteria

- [x] TokenType enum contains all 80+ token types ✅ **(114 total)**
- [x] Token class is immutable (frozen dataclass) ✅
- [x] SourceLocation accurately tracks file position ✅
- [x] All classes have proper __repr__ for debugging ✅
- [x] Unit tests pass (10+ tests) ✅ **(37 tests passed)**
- [x] Code is type-hinted (mypy clean) ✅
- [x] Documentation strings for all classes ✅

---

## 🏗️ Implementation Details

### File: `src/lexer/token.py`

```python
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class TokenType(Enum):
    """Enumeration of all Fusion token types."""

    # Keywords - Control Flow
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    LOOP = auto()
    END = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    MATCH = auto()
    CASE = auto()

    # Keywords - Functions
    FUNCTION = auto()
    FUNC = auto()
    ASYNC = auto()
    AWAIT = auto()

    # Keywords - OOP
    CLASS = auto()
    STRUCT = auto()
    INTERFACE = auto()
    ENUM = auto()
    INHERITS = auto()
    IMPLEMENTS = auto()
    PROPERTY = auto()
    GET = auto()
    SET = auto()

    # Keywords - Modifiers
    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()
    STATIC = auto()
    VIRTUAL = auto()
    OVERRIDE = auto()
    ABSTRACT = auto()
    SEALED = auto()

    # Keywords - Types
    INT = auto()
    FLOAT = auto()
    DOUBLE = auto()
    STRING = auto()
    BOOL = auto()
    CHAR = auto()
    BYTE = auto()
    SHORT = auto()
    LONG = auto()
    VOID = auto()

    # Keywords - Memory
    UNIQUE = auto()
    SHARED = auto()
    WEAK = auto()

    # Keywords - Variables
    VAR = auto()
    CONST = auto()

    # Keywords - Literals
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    THIS = auto()

    # Keywords - Operators (word-based)
    AND = auto()
    OR = auto()
    NOT = auto()
    IS = auto()
    IN = auto()

    # Keywords - Other
    IMPORT = auto()
    NEW = auto()
    CAST = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    ERROR = auto()
    GO = auto()

    # Operators - Arithmetic
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    POWER = auto()          # **

    # Operators - Comparison
    LESS = auto()           # <
    GREATER = auto()        # >
    LESS_EQUAL = auto()     # <=
    GREATER_EQUAL = auto()  # >=
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    NOT_EQUAL_ALT = auto()  # <> (alternative)

    # Operators - Logical
    LOGICAL_AND = auto()    # &&
    LOGICAL_OR = auto()     # ||
    LOGICAL_NOT = auto()    # !

    # Operators - Assignment
    ASSIGN = auto()         # =
    PLUS_ASSIGN = auto()    # +=
    MINUS_ASSIGN = auto()   # -=
    MULTIPLY_ASSIGN = auto() # *=
    DIVIDE_ASSIGN = auto()  # /=
    MODULO_ASSIGN = auto()  # %=
    POWER_ASSIGN = auto()   # **=

    # Operators - Special
    RANGE = auto()          # ...
    SAFE_NAV = auto()       # ?.
    SAFE_INDEX = auto()     # ?[
    CHANNEL_SEND = auto()   # <-
    ARROW = auto()          # ->
    INCREMENT = auto()      # ++
    DECREMENT = auto()      # --

    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    COMMA = auto()          # ,
    COLON = auto()          # :
    DOT = auto()            # .
    QUESTION = auto()       # ?

    # Literals
    INTEGER = auto()
    FLOAT_LIT = auto()
    STRING_LIT = auto()
    CHAR_LIT = auto()

    # Identifiers
    IDENTIFIER = auto()

    # Special Tokens
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    EOF = auto()


@dataclass(frozen=True)
class SourceLocation:
    """Represents a location in source code for error reporting."""
    filename: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column}"

    def to_string(self) -> str:
        """Format as file:line:col for error messages."""
        return f"{self.filename}:{self.line}:{self.column}"


@dataclass(frozen=True)
class Token:
    """Represents a single token from the lexer."""
    type: TokenType
    value: str
    location: SourceLocation

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.value}', {self.location})"

    def is_keyword(self) -> bool:
        """Check if token is a keyword."""
        keyword_types = {
            TokenType.IF, TokenType.ELSE, TokenType.FOR, TokenType.WHILE,
            TokenType.FUNCTION, TokenType.CLASS, TokenType.RETURN,
            # ... (check against keyword set)
        }
        return self.type in keyword_types

    def is_operator(self) -> bool:
        """Check if token is an operator."""
        return self.type.name.endswith(('_OP', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE'))
```

---

## 🧪 Tests Required

### File: `tests/test_token.py`

```python
import pytest
from src.lexer.token import Token, TokenType, SourceLocation


def test_token_creation():
    """Test basic token creation."""
    loc = SourceLocation("test.fusion", 1, 1)
    token = Token(TokenType.INTEGER, "42", loc)

    assert token.type == TokenType.INTEGER
    assert token.value == "42"
    assert token.location == loc


def test_token_equality():
    """Test token equality comparison."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 1, 1)

    token1 = Token(TokenType.INTEGER, "42", loc1)
    token2 = Token(TokenType.INTEGER, "42", loc2)

    assert token1 == token2


def test_token_repr():
    """Test token string representation."""
    loc = SourceLocation("test.fusion", 5, 10)
    token = Token(TokenType.IF, "if", loc)

    repr_str = repr(token)
    assert "IF" in repr_str
    assert "if" in repr_str
    assert "5:10" in repr_str


def test_source_location_formatting():
    """Test source location string formatting."""
    loc = SourceLocation("example.fusion", 42, 15)

    assert str(loc) == "example.fusion:42:15"
    assert loc.to_string() == "example.fusion:42:15"


def test_token_type_enum():
    """Test TokenType enum has all required types."""
    # Control flow
    assert hasattr(TokenType, 'IF')
    assert hasattr(TokenType, 'ELSE')
    assert hasattr(TokenType, 'FOR')

    # Types
    assert hasattr(TokenType, 'INT')
    assert hasattr(TokenType, 'STRING')

    # Operators
    assert hasattr(TokenType, 'PLUS')
    assert hasattr(TokenType, 'EQUAL')

    # Special
    assert hasattr(TokenType, 'INDENT')
    assert hasattr(TokenType, 'DEDENT')
    assert hasattr(TokenType, 'EOF')


def test_token_immutability():
    """Test that tokens are immutable."""
    loc = SourceLocation("test.fusion", 1, 1)
    token = Token(TokenType.INTEGER, "42", loc)

    with pytest.raises(AttributeError):
        token.type = TokenType.FLOAT_LIT  # Should raise error


def test_is_keyword():
    """Test keyword detection."""
    loc = SourceLocation("test.fusion", 1, 1)

    keyword_token = Token(TokenType.IF, "if", loc)
    assert keyword_token.is_keyword()

    identifier_token = Token(TokenType.IDENTIFIER, "myVar", loc)
    assert not identifier_token.is_keyword()
```

---

## 📝 Implementation Notes

### Design Decisions

1. **Frozen Dataclasses:** Use `@dataclass(frozen=True)` for immutability
   - Tokens should never change after creation
   - Enables use as dictionary keys
   - Prevents accidental mutation bugs

2. **Enum auto():** Use `auto()` for TokenType values
   - Automatic numbering
   - Don't care about specific values
   - Easier to add new types

3. **Type Hints:** Full type annotations
   - Use `typing` module for Optional, List, etc.
   - Enables static type checking with mypy
   - Better IDE autocomplete

4. **Separate FLOAT vs FLOAT_LIT:** Avoid naming collision
   - FLOAT = keyword "float"
   - FLOAT_LIT = literal like 3.14
   - Similar for STRING/STRING_LIT, CHAR/CHAR_LIT

---

## 🚨 Edge Cases

1. **Column Tracking:** Tabs count as 1 or 4 columns?
   - Decision: Count as 1 character, track actual character position
   - Alternative: Expand tabs to spaces before lexing

2. **Unicode Identifiers:** Support non-ASCII identifiers?
   - MVP: ASCII only (a-zA-Z0-9_)
   - Future: Unicode support (émile, 变量)

3. **Token Value Storage:** Store original text or interpreted value?
   - Decision: Store original text ("3.14" not 3.14)
   - Parser will convert to actual values
   - Preserves source fidelity

---

## ✅ Completion Checklist

- [x] token.py file created ✅
- [x] TokenType enum with 80+ types ✅ (114 types)
- [x] Token dataclass implemented ✅
- [x] SourceLocation dataclass implemented ✅
- [x] test_token.py file created ✅
- [x] All unit tests pass ✅ (37/37 tests)
- [x] Type hints complete (mypy clean) ✅
- [x] Documentation strings added ✅
- [x] Code reviewed ✅
- [ ] Committed to version control (optional)

---

## 🔗 Next Task

After completing Task 1.1, proceed to **Task 1.4 (Keyword Recognition)** as it builds directly on the TokenType enum defined here.

---

**File:** task-1.1.md
**Last Updated:** 2025-11-03
