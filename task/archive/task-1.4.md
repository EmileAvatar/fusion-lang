# Task 1.4: Keyword Recognition

**Phase:** Phase 1 - Lexer
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 1.1
**Estimated Effort:** 2 hours
**Last Updated:** 2025-11-10

---

## 🎯 Goal

Implement keyword recognition to distinguish keywords from identifiers.

**Keywords:** 60+ reserved words (if, else, for, class, int, string, etc.)
**Identifiers:** User-defined names (variables, functions, types)

---

## 📋 Sub-Tasks

- [x] 1.4.1 Create keyword lookup table (dictionary) ✅
  - [x] 1.4.1.1 Add control flow keywords ✅
  - [x] 1.4.1.2 Add function keywords ✅
  - [x] 1.4.1.3 Add OOP keywords ✅
  - [x] 1.4.1.4 Add type keywords ✅
  - [x] 1.4.1.5 Add all 66 keywords (including special cases) ✅

- [x] 1.4.2 Implement keyword vs identifier check ✅
  - [x] 1.4.2.1 Read alphanumeric sequence (handled by lexer) ✅
  - [x] 1.4.2.2 Check against keyword table ✅
  - [x] 1.4.2.3 Return keyword token if match ✅
  - [x] 1.4.2.4 Return identifier token if no match ✅

- [x] 1.4.3 Verify case sensitivity ✅
  - [x] 1.4.3.1 Keywords are case-sensitive ("if" not "IF") ✅
  - [x] 1.4.3.2 "int" is keyword, "Int" is identifier ✅

---

## 🏗️ Implementation

```python
# File: src/lexer/keywords.py
from src.lexer.token import TokenType

KEYWORDS = {
    # Control flow
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'while': TokenType.WHILE,
    'loop': TokenType.LOOP,
    'end': TokenType.END,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'return': TokenType.RETURN,
    'match': TokenType.MATCH,
    'case': TokenType.CASE,

    # Functions
    'function': TokenType.FUNCTION,
    'func': TokenType.FUNC,
    'async': TokenType.ASYNC,
    'await': TokenType.AWAIT,

    # OOP
    'class': TokenType.CLASS,
    'struct': TokenType.STRUCT,
    'interface': TokenType.INTERFACE,
    'enum': TokenType.ENUM,
    'Enum': TokenType.ENUM,  # Special case: Enum with capital E
    'inherits': TokenType.INHERITS,
    'implements': TokenType.IMPLEMENTS,
    'property': TokenType.PROPERTY,
    'get': TokenType.GET,
    'set': TokenType.SET,

    # Modifiers
    'public': TokenType.PUBLIC,
    'private': TokenType.PRIVATE,
    'protected': TokenType.PROTECTED,
    'static': TokenType.STATIC,
    'virtual': TokenType.VIRTUAL,
    'override': TokenType.OVERRIDE,
    'abstract': TokenType.ABSTRACT,
    'sealed': TokenType.SEALED,

    # Types
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'double': TokenType.DOUBLE,
    'string': TokenType.STRING,
    'bool': TokenType.BOOL,
    'char': TokenType.CHAR,
    'byte': TokenType.BYTE,
    'short': TokenType.SHORT,
    'long': TokenType.LONG,
    'void': TokenType.VOID,

    # Memory
    'Unique': TokenType.UNIQUE,
    'Shared': TokenType.SHARED,
    'Weak': TokenType.WEAK,

    # Variables
    'var': TokenType.VAR,
    'const': TokenType.CONST,

    # Literals
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'null': TokenType.NULL,
    'this': TokenType.THIS,

    # Operators (word-based)
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'is': TokenType.IS,
    'in': TokenType.IN,

    # Other
    'import': TokenType.IMPORT,
    'new': TokenType.NEW,
    'cast': TokenType.CAST,
    'try': TokenType.TRY,
    'catch': TokenType.CATCH,
    'finally': TokenType.FINALLY,
    'throw': TokenType.THROW,
    'Error': TokenType.ERROR,
    'go': TokenType.GO,
}

def is_keyword(word: str) -> bool:
    """Check if word is a keyword."""
    return word in KEYWORDS

def get_keyword_type(word: str) -> TokenType:
    """Get token type for keyword."""
    return KEYWORDS.get(word, TokenType.IDENTIFIER)
```

---

## 🧪 Tests Required

```python
def test_keyword_recognition():
    assert is_keyword('if')
    assert is_keyword('class')
    assert is_keyword('int')
    assert not is_keyword('myVariable')

def test_case_sensitivity():
    assert is_keyword('int')
    assert not is_keyword('INT')  # All caps is identifier
    assert is_keyword('Enum')  # Special case: capital E allowed
```

---

## ✅ Completion Summary

**Implementation Completed:** 2025-11-10

**Files Created:**
- [src/lexer/keywords.py](../src/lexer/keywords.py) - Keyword lookup table with 66 keywords
- [tests/test_keywords.py](../tests/test_keywords.py) - Comprehensive test suite (82 tests)

**Test Results:**
- ✅ 82 tests passed
- ✅ All 66 keywords recognized correctly
- ✅ Case sensitivity verified
- ✅ Identifier vs keyword distinction working
- ✅ Special cases handled (Enum/enum, Unique/Shared/Weak, Error)

**Key Features:**
- Complete keyword lookup table (66 keywords)
- `is_keyword(word)` - Check if word is a keyword
- `get_keyword_type(word)` - Get TokenType or IDENTIFIER
- Case-sensitive matching with special cases:
  - Both 'enum' and 'Enum' map to TokenType.ENUM
  - Memory keywords require capitals: 'Unique', 'Shared', 'Weak'
  - Error type requires capital: 'Error'

---

**File:** task-1.4.md
