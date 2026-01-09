# Task 1.7: Comment Handling

**Phase:** Phase 1 - Lexer
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 1.1
**Estimated Effort:** 1-2 hours
**Last Updated:** 2025-11-10

---

## 🎯 Goal

Skip all three comment styles without emitting tokens.

**Comment Styles:**
1. `//` - Single-line (C-style)
2. `'` - Single-line (VB-style)
3. `/* */` - Multi-line (C-style)

---

## 📋 Sub-Tasks

- [x] 1.7.1 Single-line comments (`//`) ✅
  - [x] 1.7.1.1 Detect `//` sequence ✅
  - [x] 1.7.1.2 Consume until newline ✅
  - [x] 1.7.1.3 Do not emit token ✅

- [x] 1.7.2 Single-line comments (`'`) ✅
  - [x] 1.7.2.1 Detect `'` at token start ✅
  - [x] 1.7.2.2 Consume until newline ✅
  - [x] 1.7.2.3 Do not emit token ✅

- [x] 1.7.3 Multi-line comments (`/* */`) ✅
  - [x] 1.7.3.1 Detect `/*` sequence ✅
  - [x] 1.7.3.2 Consume until `*/` ✅
  - [x] 1.7.3.3 Track line numbers inside comment ✅
  - [x] 1.7.3.4 Error if unterminated ✅

---

## 🏗️ Implementation

```python
def skip_comment(self):
    """Skip comment and return nothing."""
    if self.peek(2) == '//':
        # Single-line comment
        while self.current_char != '\n' and not self.is_eof():
            self.advance()
        return

    if self.current_char == "'":
        # VB-style single-line comment
        while self.current_char != '\n' and not self.is_eof():
            self.advance()
        return

    if self.peek(2) == '/*':
        # Multi-line comment
        self.advance(2)  # Skip /*
        while True:
            if self.is_eof():
                self.error("Unterminated comment")
            if self.peek(2) == '*/':
                self.advance(2)  # Skip */
                break
            self.advance()
        return
```

---

## 🧪 Tests Required

```python
def test_single_line_comment_slash():
    source = "int x = 5 // this is a comment\nint y = 10"
    tokens = lex(source)
    # Should have: INT IDENTIFIER ASSIGN INTEGER NEWLINE INT IDENTIFIER ASSIGN INTEGER
    # Comment should not appear

def test_single_line_comment_quote():
    source = "int x = 5 ' VB-style comment\nint y = 10"
    tokens = lex(source)
    # Comment should be skipped

def test_multi_line_comment():
    source = """
    int x = 5
    /* This is a
       multi-line
       comment */
    int y = 10
    """
    tokens = lex(source)
    # Comment should be skipped

def test_unterminated_comment_error():
    source = "/* unterminated"
    with pytest.raises(LexerError):
        lex(source)
```

---

## ✅ Completion Summary

**Implementation Completed:** 2025-11-10

**Files Created:**
- [src/lexer/comments.py](../src/lexer/comments.py) - Comment handling for all three styles
- [tests/test_comments.py](../tests/test_comments.py) - Comprehensive test suite (52 tests)

**Test Results:**
- ✅ 52 tests passed
- ✅ Single-line comment handling (`//` and `'`)
- ✅ Multi-line comment handling (`/* */`)
- ✅ Line number tracking in multi-line comments
- ✅ Unterminated comment error handling

**Key Features:**
- **Three Comment Styles**:
  - `//` - C-style single-line (consume until newline)
  - `'` - VB-style single-line (consume until newline)
  - `/* */` - C-style multi-line (consume until `*/`)
- **Line Tracking**: Multi-line comments track newlines for accurate error reporting
- **Error Handling**: Unterminated multi-line comments raise ValueError
- **Position Management**: All functions return (new_position, lines_consumed) tuple
- Helper functions:
  - `is_comment_start(text, pos)` - Detect if position starts a comment
  - `skip_single_line_comment(text, pos)` - Skip `//` or `'` comments
  - `skip_multi_line_comment(text, pos)` - Skip `/* */` comments
  - `skip_comment(text, pos)` - Main entry point (auto-detects comment type)
  - `get_comment_type(text, pos)` - Returns 'single', 'multi', or None

**Implementation Notes:**
- Comments are skipped during lexing (no tokens emitted)
- Single-line comments point to newline or EOF when done
- Multi-line comments point to position after `*/`
- Unterminated multi-line comments raise clear error messages

---

**File:** task-1.7.md
