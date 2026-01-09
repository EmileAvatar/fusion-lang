# Task 1.8: Error Handling & Diagnostics

**Phase:** Phase 1 - Lexer
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 1.1
**Estimated Effort:** 2 hours
**Last Updated:** 2025-11-10

---

## 🎯 Goal

Implement clear error reporting with source location information.

---

## 📋 Sub-Tasks

- [x] 1.8.1 Error reporting infrastructure
  - [x] 1.8.1.1 LexerError exception class
  - [x] 1.8.1.2 Error message formatting
  - [x] 1.8.1.3 Source location in errors
  - [x] 1.8.1.4 Error severity levels (error vs warning)

- [x] 1.8.2 Lexer-specific errors
  - [x] 1.8.2.1 Unterminated string literal
  - [x] 1.8.2.2 Invalid character
  - [x] 1.8.2.3 Mixed tabs/spaces warning
  - [x] 1.8.2.4 Indentation mismatch error
  - [x] 1.8.2.5 Unterminated comment

## ✅ Implementation Complete

**Files Created:**
- `src/utils/errors.py` - Error handling infrastructure (238 lines)
- `tests/test_errors.py` - Comprehensive test suite (29 tests, all passing)

**Files Modified:**
- `src/lexer/indentation.py` - Updated to use LexerError and LexerWarning
- `src/lexer/comments.py` - Added error imports
- `src/lexer/literals.py` - Added error imports
- `src/lexer/__init__.py` - Removed IndentationError export
- `tests/test_indentation.py` - Updated tests to use new error types

**Key Features:**
1. **LexerError** - Exception class with source location tracking
2. **LexerWarning** - Warning class with source location tracking
3. **DiagnosticReporter** - Collects and reports multiple errors/warnings
4. **LexerErrorMessages** - Standardized error message templates

**Test Coverage:**
- 29 tests in test_errors.py (100% pass)
- All existing 382 tests still passing
- Error handling integrated into indentation module

---

## 🏗️ Implementation

```python
class LexerError(Exception):
    """Lexer error with source location."""
    def __init__(self, message: str, location: SourceLocation):
        self.message = message
        self.location = location
        super().__init__(f"{location}: {message}")

class Lexer:
    def error(self, message: str):
        """Raise lexer error at current location."""
        raise LexerError(message, self.location())

    def warning(self, message: str):
        """Emit warning at current location."""
        print(f"Warning: {self.location()}: {message}", file=sys.stderr)
```

---

## 🧪 Tests

```python
def test_unterminated_string():
    with pytest.raises(LexerError) as exc:
        lex('"unterminated')
    assert "Unterminated string" in str(exc.value)

def test_invalid_character():
    with pytest.raises(LexerError) as exc:
        lex('int x = 5 \\u263A')  # Invalid char
    assert "Invalid character" in str(exc.value)

def test_error_location():
    try:
        lex('"unterminated')
    except LexerError as e:
        assert e.location.line == 1
        assert e.location.column > 0
```

---

**File:** task-1.8.md
