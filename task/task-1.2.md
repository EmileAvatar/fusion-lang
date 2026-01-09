# Task 1.2: Indentation Tracking System

**Phase:** Phase 1 - Lexer
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 1.1 (Token Definitions)
**Estimated Effort:** 4-5 hours
**Last Updated:** 2025-11-04

---

## 🎯 Goal

Implement Python-style indentation tracking with INDENT/DEDENT token generation for indentation-based blocks.

**Critical:** This is the most complex part of the lexer. Bugs here will break the entire parser.

---

## 📋 Sub-Tasks

- [x] 1.2.1 Implement indentation stack ✅
  - [x] 1.2.1.1 Initialize stack with [0] ✅
  - [x] 1.2.1.2 Push operation for indent increase ✅
  - [x] 1.2.1.3 Pop operation for indent decrease ✅
  - [x] 1.2.1.4 Current level accessor ✅

- [x] 1.2.2 Implement INDENT token generation ✅
  - [x] 1.2.2.1 Detect indentation increase after newline ✅
  - [x] 1.2.2.2 Push new level to stack ✅
  - [x] 1.2.2.3 Emit INDENT token ✅
  - [x] 1.2.2.4 Update current position ✅

- [x] 1.2.3 Implement DEDENT token generation ✅
  - [x] 1.2.3.1 Detect indentation decrease after newline ✅
  - [x] 1.2.3.2 Pop stack until matching level ✅
  - [x] 1.2.3.3 Emit DEDENT token(s) - multiple if needed ✅
  - [x] 1.2.3.4 Validate dedent aligns with previous level ✅

- [x] 1.2.4 Handle edge cases ✅
  - [x] 1.2.4.1 EOF dedent emission (emit DEDENTs for all remaining levels) ✅
  - [x] 1.2.4.2 Blank line handling (skip, don't change indent) ✅
  - [x] 1.2.4.3 Mixed tabs/spaces detection (error or warning) ✅
  - [x] 1.2.4.4 Comment-only lines (skip, don't change indent) ✅

---

## ✅ Acceptance Criteria

- [x] Indentation stack correctly tracks nesting levels ✅
- [x] INDENT emitted when indentation increases ✅
- [x] DEDENT emitted when indentation decreases ✅
- [x] Multiple DEDENTs emitted for multi-level unindent ✅
- [x] EOF emits DEDENTs to close all blocks ✅
- [x] Blank lines don't affect indentation ✅
- [x] Comment-only lines don't affect indentation ✅
- [x] Mixed tabs/spaces detected and reported ✅
- [x] Misaligned dedents cause error ✅
- [x] 20+ unit tests pass ✅ **(35 tests passed)**
- [x] Integration test: multi-level indentation example ✅

---

## 🏗️ Implementation Algorithm

### From EBNF Specification

```python
class Lexer:
    def __init__(self):
        self.indent_stack = [0]  # Start with zero indentation
        self.pending_tokens = []  # Queue for INDENT/DEDENT tokens

    def handle_newline(self):
        """Called when newline is encountered."""
        # Skip blank lines
        while self.current_char in [' ', '\t', '\n']:
            if self.current_char == '\n':
                self.advance()
                continue
            break

        # Check if line is comment-only
        if self.is_comment_line():
            return

        # Count leading whitespace
        indent_level = self.count_indentation()

        # Compare with current level
        current = self.indent_stack[-1]

        if indent_level > current:
            # Increase indentation
            self.indent_stack.append(indent_level)
            self.pending_tokens.append(Token(TokenType.INDENT, "", self.location()))

        elif indent_level < current:
            # Decrease indentation
            while len(self.indent_stack) > 0 and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.pending_tokens.append(Token(TokenType.DEDENT, "", self.location()))

            # Validate alignment
            if self.indent_stack[-1] != indent_level:
                self.error("Indentation mismatch")

        # Equal indentation: no INDENT/DEDENT

    def count_indentation(self) -> int:
        """Count leading whitespace on current line."""
        count = 0
        has_spaces = False
        has_tabs = False

        while self.current_char in [' ', '\t']:
            if self.current_char == ' ':
                count += 1
                has_spaces = True
            elif self.current_char == '\t':
                count += 4  # Tab = 4 spaces (or use 8, or 1 - decide!)
                has_tabs = True
            self.advance()

        # Warn if mixed tabs/spaces
        if has_spaces and has_tabs:
            self.warning("Mixed tabs and spaces")

        return count

    def handle_eof(self):
        """Emit remaining DEDENTs at end of file."""
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.pending_tokens.append(Token(TokenType.DEDENT, "", self.location()))

        # Final EOF token
        self.pending_tokens.append(Token(TokenType.EOF, "", self.location()))
```

---

## 🧪 Tests Required

```python
def test_simple_indent():
    """Test single level indentation."""
    source = """
if true
    print("hello")
"""
    tokens = lex(source)
    assert tokens[0].type == TokenType.IF
    assert tokens[2].type == TokenType.INDENT
    assert tokens[3].type == TokenType.IDENTIFIER  # print
    assert tokens[5].type == TokenType.DEDENT


def test_multiple_indent_levels():
    """Test nested indentation."""
    source = """
if true
    if true
        print("nested")
"""
    tokens = lex(source)
    # Expect: IF TRUE NEWLINE INDENT IF TRUE NEWLINE INDENT IDENTIFIER...


def test_multiple_dedent():
    """Test multiple dedents at once."""
    source = """
if true
    if true
        print("a")
print("b")
"""
    # Should emit 2 DEDENTs before final print


def test_blank_lines_ignored():
    """Test that blank lines don't affect indentation."""
    source = """
if true

    print("hello")
"""
    # Blank line should be skipped


def test_comment_only_lines_ignored():
    """Test comment-only lines don't affect indentation."""
    source = """
if true
    // This is a comment
    print("hello")
"""


def test_mixed_tabs_spaces_warning():
    """Test warning on mixed tabs/spaces."""
    source = "if true\n\t  print('mixed')"  # Tab then spaces
    # Should emit warning


def test_indent_mismatch_error():
    """Test error on misaligned dedent."""
    source = """
if true
    print("a")
  print("b")
"""
    # 2 spaces dedent doesn't align with 4 spaces indent
    # Should raise error


def test_eof_dedents():
    """Test DEDENT emission at EOF."""
    source = """
if true
    if true
        print("end")
"""
    tokens = lex(source)
    # Last tokens should be: DEDENT DEDENT EOF
```

---

## 📝 Implementation Notes

### Design Decisions

1. **Tab Width:** How many spaces is a tab?
   - Option 1: 4 spaces (Python standard)
   - Option 2: 8 spaces (traditional)
   - Option 3: 1 character (simplest)
   - **Recommendation:** 4 spaces for MVP, make configurable later

2. **Mixed Tabs/Spaces:** Error or warning?
   - Python 3: Error
   - Our choice: Warning for MVP, error in strict mode
   - **Reason:** Flexibility during development

3. **Blank Lines:** Always skip or count in certain contexts?
   - **Decision:** Always skip blank lines
   - Simplifies logic, matches Python behavior

4. **Comment-Only Lines:** Skip indentation tracking?
   - **Decision:** Yes, skip (like blank lines)
   - Comments shouldn't affect block structure

---

## 🚨 Edge Cases

1. **EOF with open blocks:** Emit DEDENTs for all levels
2. **First line indented:** Error (unexpected indent)
3. **Dedent doesn't align:** Error (inconsistent indentation)
4. **Windows CRLF vs Unix LF:** Handle both
5. **UTF-8 BOM:** Skip if present at start of file

---

## 🔗 Next Task

After completing Task 1.2, proceed to **Task 1.3 (Block Style Detection)** which builds on indentation tracking to support braces and End keywords.

---

**File:** task-1.2.md
**Last Updated:** 2025-11-03
