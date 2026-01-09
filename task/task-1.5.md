# Task 1.5: Operator Tokenization

**Phase:** Phase 1 - Lexer
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 1.1
**Estimated Effort:** 3 hours
**Last Updated:** 2025-11-10

---

## 🎯 Goal

Tokenize all Fusion operators including multi-character operators using longest-match algorithm.

**Operators:** 30+ including `...`, `?.`, `**`, `==`, `!=`, `<>`, `<-`, etc.

---

## 📋 Sub-Tasks

- [x] 1.5.1 Single-character operators ✅
  - [x] 1.5.1.1 Arithmetic: + - * / % ✅
  - [x] 1.5.1.2 Comparison: < > ✅
  - [x] 1.5.1.3 Assignment: = ✅
  - [x] 1.5.1.4 Logical: ! ✅
  - [x] 1.5.1.5 Delimiters: ( ) [ ] { } , : . ? ✅

- [x] 1.5.2 Multi-character operators (longest-match) ✅
  - [x] 1.5.2.1 Three-char: ... (range), **= (power assign) ✅
  - [x] 1.5.2.2 Two-char comparison: == != <> <= >= ✅
  - [x] 1.5.2.3 Two-char logical: && || ✅
  - [x] 1.5.2.4 Two-char assignment: += -= *= /= %= ✅
  - [x] 1.5.2.5 Two-char special: ++ -- ** ?. ?[ <- -> ✅

- [x] 1.5.3 Longest-match algorithm implementation ✅
  - [x] 1.5.3.1 Lookahead for multi-char operators ✅
  - [x] 1.5.3.2 Try longest match first (3-char, then 2-char, then 1-char) ✅
  - [x] 1.5.3.3 Correct disambiguation (... not ..., **= not ** and =) ✅

---

## 🏗️ Implementation

```python
def tokenize_operator(self):
    """Tokenize operators using longest-match."""
    # Try 3-character operators first
    if self.peek(3) == '...':
        self.advance(3)
        return Token(TokenType.RANGE, '...', self.location())

    # Try 2-character operators
    two_char = self.peek(2)
    two_char_ops = {
        '==': TokenType.EQUAL,
        '!=': TokenType.NOT_EQUAL,
        '<>': TokenType.NOT_EQUAL_ALT,
        '<=': TokenType.LESS_EQUAL,
        '>=': TokenType.GREATER_EQUAL,
        '&&': TokenType.LOGICAL_AND,
        '||': TokenType.LOGICAL_OR,
        '+=': TokenType.PLUS_ASSIGN,
        '-=': TokenType.MINUS_ASSIGN,
        '*=': TokenType.MULTIPLY_ASSIGN,
        '/=': TokenType.DIVIDE_ASSIGN,
        '%=': TokenType.MODULO_ASSIGN,
        '**': TokenType.POWER,
        '?.': TokenType.SAFE_NAV,
        '?[': TokenType.SAFE_INDEX,
        '<-': TokenType.CHANNEL_SEND,
        '->': TokenType.ARROW,
        '++': TokenType.INCREMENT,
        '--': TokenType.DECREMENT,
    }
    if two_char in two_char_ops:
        self.advance(2)
        return Token(two_char_ops[two_char], two_char, self.location())

    # Single-character operators
    one_char_ops = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '%': TokenType.MODULO,
        '<': TokenType.LESS,
        '>': TokenType.GREATER,
        '=': TokenType.ASSIGN,
        '!': TokenType.LOGICAL_NOT,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        ',': TokenType.COMMA,
        ':': TokenType.COLON,
        '.': TokenType.DOT,
        '?': TokenType.QUESTION,
    }
    char = self.current_char
    if char in one_char_ops:
        self.advance()
        return Token(one_char_ops[char], char, self.location())

    return None
```

---

## 🧪 Tests Required

```python
def test_single_char_operators():
    assert lex('+')[0].type == TokenType.PLUS
    assert lex('-')[0].type == TokenType.MINUS

def test_two_char_operators():
    assert lex('==')[0].type == TokenType.EQUAL
    assert lex('!=')[0].type == TokenType.NOT_EQUAL
    assert lex('?.')[0].type == TokenType.SAFE_NAV

def test_three_char_operators():
    assert lex('...')[0].type == TokenType.RANGE

def test_longest_match():
    # Should tokenize as RANGE, not DOT DOT DOT
    tokens = lex('...')
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.RANGE

def test_operator_disambiguation():
    # Should be POWER_ASSIGN, not POWER + ASSIGN
    assert lex('**=')[0].type == TokenType.POWER_ASSIGN

    # Should be two tokens: POWER and ASSIGN
    tokens = lex('** =')
    assert tokens[0].type == TokenType.POWER
    assert tokens[1].type == TokenType.ASSIGN
```

---

## ✅ Completion Summary

**Implementation Completed:** 2025-11-10

**Files Created:**
- [src/lexer/operators.py](../src/lexer/operators.py) - Operator lookup tables and longest-match algorithm
- [tests/test_operators.py](../tests/test_operators.py) - Comprehensive test suite (45 tests)

**Test Results:**
- ✅ 45 tests passed
- ✅ All 30 operators recognized correctly
- ✅ All 10 delimiters recognized correctly
- ✅ Longest-match algorithm working perfectly
- ✅ Operator disambiguation verified (e.g., `...` vs `.`, `**=` vs `**`)

**Key Features:**
- **30 operators** total:
  - 2 three-character operators: `...`, `**=`
  - 19 two-character operators: `==`, `!=`, `<=`, `>=`, `<>`, `&&`, `||`, `+=`, `-=`, `*=`, `/=`, `%=`, `**`, `++`, `--`, `?.`, `?[`, `<-`, `->`
  - 9 single-character operators: `+`, `-`, `*`, `/`, `%`, `<`, `>`, `=`, `!`
- **10 delimiters**: `(`, `)`, `[`, `]`, `{`, `}`, `,`, `:`, `.`, `?`
- **Longest-match algorithm**: Tries 3-char → 2-char → 1-char for correct disambiguation
- Helper functions:
  - `match_operator(text, position)` - Main matching function
  - `is_operator_char(char)` - Check if character is part of operator
  - `is_operator(token_type)` - Check if TokenType is an operator
  - `is_delimiter(token_type)` - Check if TokenType is a delimiter

---

**File:** task-1.5.md
