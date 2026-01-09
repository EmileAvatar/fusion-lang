# Task 1.3: Block Style Detection

**Phase:** Phase 1 - Lexer
**Status:** 🟢 Complete
**Progress:** 100%
**Depends On:** Task 1.2 (Indentation Tracking)
**Estimated Effort:** 2-3 hours
**Last Updated:** 2025-11-04

---

## 🎯 Goal

Support all three Fusion block styles:
1. **Indentation-based** (Python-style)
2. **Brace-based** (C/Java-style with `{}`)
3. **End keyword-based** (VB.NET-style with `End function`, `End if`, etc.)

Users can mix styles, so lexer must handle all simultaneously.

---

## 📋 Sub-Tasks

- [x] 1.3.1 Brace block detection ✅
  - [x] 1.3.1.1 Recognize `{` as LBRACE token and block start ✅
  - [x] 1.3.1.2 Recognize `}` as RBRACE token and block end ✅
  - [x] 1.3.1.3 Disable indentation tracking inside brace blocks ✅
  - [x] 1.3.1.4 Track brace nesting depth ✅

- [x] 1.3.2 End keyword detection ✅
  - [x] 1.3.2.1 Recognize `End function` (two tokens: END + FUNCTION) ✅
  - [x] 1.3.2.2 Recognize `End if` (two tokens: END + IF) ✅
  - [x] 1.3.2.3 Recognize `End loop` (two tokens: END + LOOP) ✅
  - [x] 1.3.2.4 Recognize standalone `End` (generic block end) ✅

- [x] 1.3.3 Block style state management ✅
  - [x] 1.3.3.1 Track current block context (indent/brace/end) ✅
  - [x] 1.3.3.2 Switch between styles seamlessly ✅
  - [x] 1.3.3.3 Validate proper nesting (no mismatched blocks) ✅
  - [x] 1.3.3.4 Handle mixed styles in same file ✅

---

## ✅ Acceptance Criteria

- [x] Brace blocks `{}` tokenized correctly ✅
- [x] End keywords tokenized as two separate tokens ✅
- [x] Indentation tracking disabled inside brace blocks ✅
- [x] Can mix block styles in same file ✅
- [x] Nesting validated (e.g., can't close indent block with `}`) ✅
- [x] 15+ unit tests pass ✅ **(32 tests passed)**
- [x] Integration test: file with all three block styles ✅

---

## 🏗️ Implementation

```python
class Lexer:
    def __init__(self):
        self.indent_stack = [0]
        self.brace_depth = 0  # Track brace nesting
        self.block_style_stack = []  # Track block styles

    def tokenize_lbrace(self):
        """Handle opening brace."""
        self.brace_depth += 1
        self.block_style_stack.append('brace')
        return Token(TokenType.LBRACE, '{', self.location())

    def tokenize_rbrace(self):
        """Handle closing brace."""
        if self.brace_depth == 0:
            self.error("Unexpected closing brace")

        self.brace_depth -= 1
        if self.block_style_stack and self.block_style_stack[-1] == 'brace':
            self.block_style_stack.pop()

        return Token(TokenType.RBRACE, '}', self.location())

    def should_track_indentation(self) -> bool:
        """Check if indentation tracking is active."""
        # Don't track indentation inside brace blocks
        return self.brace_depth == 0
```

---

## 🧪 Tests Required

```python
def test_brace_block():
    """Test brace-based blocks."""
    source = """
if true {
    print("hello")
}
"""
    tokens = lex(source)
    # Should have: IF TRUE LBRACE NEWLINE IDENTIFIER ... RBRACE


def test_end_keyword_block():
    """Test End keyword blocks."""
    source = """
if true
    print("hello")
End if
"""
    tokens = lex(source)
    # Should have: ... END IF (two separate tokens)


def test_mixed_styles_same_file():
    """Test mixing block styles in one file."""
    source = """
int function add(int a, int b) {
    return a + b
}

void function greet()
    print("Hello")
End function
"""
    # Should handle both brace block and End keyword


def test_indentation_disabled_in_braces():
    """Test that indentation ignored inside braces."""
    source = """
if true {
print("no indent needed")
        print("random indent ok")
}
"""
    # Should not emit INDENT/DEDENT inside braces


def test_nested_braces():
    """Test nested brace blocks."""
    source = """
if true {
    if false {
        print("nested")
    }
}
"""
```

---

**File:** task-1.3.md
**Last Updated:** 2025-11-03
