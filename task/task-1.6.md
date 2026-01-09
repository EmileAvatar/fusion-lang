# Task 1.6: Literal Tokenization

**Phase:** Phase 1 - Lexer
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 1.1
**Estimated Effort:** 3-4 hours
**Last Updated:** 2025-11-10

---

## 🎯 Goal

Tokenize all literal types: integers, floats, strings (with interpolation), characters, booleans, null.

**Critical:** String interpolation `{var}` and `{@1}` must be parsed correctly.

---

## 📋 Sub-Tasks

- [x] 1.6.1 Integer literals ✅
  - [x] 1.6.1.1 Decimal integers (123, 456) ✅
  - [x] 1.6.1.2 Long suffix (123L, 456l) ✅
  - [x] 1.6.1.3 Negative handled by unary operator ✅

- [x] 1.6.2 Float/Double literals ✅
  - [x] 1.6.2.1 Basic floats (3.14, 0.5) ✅
  - [x] 1.6.2.2 Float suffix (3.14f, 3.14F) ✅
  - [x] 1.6.2.3 Double suffix (3.14d, 3.14D) ✅

- [x] 1.6.3 String literals **WITH INTERPOLATION** ✅
  - [x] 1.6.3.1 Basic string parsing ("hello") ✅
  - [x] 1.6.3.2 Escape sequences (\n, \t, \", \\, \r, \0) ✅
  - [x] 1.6.3.3 **Inline interpolation {varName}** ✅
  - [x] 1.6.3.4 **Positional interpolation {@1}, {@2}** ✅

- [x] 1.6.4 Character literals ✅
  - [x] 1.6.4.1 Basic char ('a', 'Z') ✅
  - [x] 1.6.4.2 Escape sequences in chars ✅

- [x] 1.6.5 Boolean literals (handled as keywords) ✅
  - [x] 1.6.5.1 true keyword ✅
  - [x] 1.6.5.2 false keyword ✅

- [x] 1.6.6 Null literal (handled as keyword) ✅

---

## 🏗️ String Interpolation Implementation

```python
def tokenize_string(self):
    """Tokenize string with interpolation support."""
    start_loc = self.location()
    self.advance()  # Skip opening "

    parts = []  # Will contain string parts and interpolation tokens
    current_str = ""

    while self.current_char != '"':
        if self.current_char == '\\':
            # Escape sequence
            current_str += self.read_escape_sequence()
        elif self.current_char == '{':
            # Interpolation start
            if current_str:
                parts.append(('STRING_PART', current_str))
                current_str = ""

            self.advance()  # Skip {

            if self.current_char == '@':
                # Positional: {@1}
                self.advance()  # Skip @
                num = self.read_number()
                parts.append(('INTERP_POS', num))
            else:
                # Inline: {varName}
                var_name = self.read_identifier()
                parts.append(('INTERP_VAR', var_name))

            if self.current_char != '}':
                self.error("Expected } in string interpolation")
            self.advance()  # Skip }
        else:
            current_str += self.current_char
            self.advance()

    if current_str:
        parts.append(('STRING_PART', current_str))

    self.advance()  # Skip closing "

    # For MVP: store interpolation info in token value as JSON
    import json
    return Token(TokenType.STRING_LIT, json.dumps(parts), start_loc)
```

---

## 🧪 Tests Required

```python
def test_integer_literals():
    assert lex('42')[0].value == '42'
    assert lex('123L')[0].value == '123L'

def test_float_literals():
    assert lex('3.14')[0].value == '3.14'
    assert lex('3.14f')[0].value == '3.14f'

def test_string_basic():
    token = lex('"hello"')[0]
    assert token.type == TokenType.STRING_LIT

def test_string_escape_sequences():
    token = lex(r'"hello\nworld"')[0]
    # Should contain newline

def test_string_inline_interpolation():
    token = lex('"Hello {name}"')[0]
    # Should detect {name} as interpolation

def test_string_positional_interpolation():
    token = lex('"User {@1} is {@2} years old"')[0]
    # Should detect {@1} and {@2}

def test_char_literals():
    assert lex("'a'")[0].type == TokenType.CHAR_LIT
    assert lex("'\\n'")[0].value == "'\\n'"
```

---

## ✅ Completion Summary

**Implementation Completed:** 2025-11-10

**Files Created:**
- [src/lexer/literals.py](../src/lexer/literals.py) - Literal tokenization with string interpolation
- [tests/test_literals.py](../tests/test_literals.py) - Comprehensive test suite (70 tests)

**Test Results:**
- ✅ 70 tests passed
- ✅ Integer literals working (decimal, with L/l suffix)
- ✅ Float/Double literals working (with f/F/d/D suffix)
- ✅ String literals with full interpolation support
- ✅ Character literals with escape sequences
- ✅ All escape sequences working (\n, \t, \r, \0, \", \', \\)

**Key Features:**
- **Integer Literals**: Decimal integers with optional L/l suffix for long
- **Float/Double Literals**: Decimal floats with optional f/F/d/D suffix
- **String Interpolation** (CRITICAL FEATURE):
  - Inline interpolation: `{varName}`, `{user_name}`, `{var123}`
  - Positional interpolation: `{@1}`, `{@2}`, `{@123}`
  - Mixed interpolation in same string supported
  - JSON encoding for storage in token value
- **Escape Sequences**: \n, \t, \r, \0, \", \', \\ all supported
- **Character Literals**: Single chars with escape sequence support
- Helper functions:
  - `parse_integer(text, pos)` - Parse integer literal
  - `parse_float(text, pos)` - Parse float literal
  - `parse_string(text, pos)` - Parse string with interpolation
  - `parse_char(text, pos)` - Parse character literal
  - `has_interpolation(json_parts)` - Check if string has interpolation
  - `get_plain_string(json_parts)` - Extract plain string value

**String Interpolation Format:**
JSON-encoded list of tuples stored in token value:
- `('STRING_PART', 'text')` - Plain text
- `('INTERP_VAR', 'varName')` - Inline variable
- `('INTERP_POS', 'index')` - Positional parameter

---

**File:** task-1.6.md
