[< 050 Imports](050-Imports.md) | [Index](index.md) | [061 CommentHighlighting >](061-CommentHighlighting.md) <!-- nav -->

# 060 Comments

**Status:** design - `'` comments postponed (SYN.031); `'''` blocks designed (SYN.036); built today: [130 Comments](../spec/130-Comments.md)

**Contents**

- [Enhanced Comment Support](#enhanced-comment-support)
- [Current Comment Support (MVP)](#current-comment-support-mvp)
- [Feature 1: Re-enable `'` Comments (Line-Start Only)](#feature-1-re-enable--comments-line-start-only)
- [Feature 2: Triple-Quote Comment Blocks `'''`](#feature-2-triple-quote-comment-blocks-)
- [Feature 3: Comment Style Summary](#feature-3-comment-style-summary)
- [Implementation Notes](#implementation-notes)
- [Testing Strategy](#testing-strategy)
- [Timeline](#timeline)
- [Benefits](#benefits)
- [Open Questions](#open-questions)

## Enhanced Comment Support

**Status:** 📝 Proposed
**Priority:** Medium (syntax enhancement)
**Impact:** Lexer modifications, grammar changes
**Depends On:** Basic compiler completion

**Purpose:** Re-enable `'` single-line comments and add `'''` multi-line comment blocks (Python-style)

---

### Current Comment Support (MVP)

**Supported:**
- `//` - C-style single-line comments
- `/* */` - C-style multi-line comments

**Disabled:**
- `'` - VB-style single-line comments (conflicts with character literals `'c'`)

---

### Feature 1: Re-enable `'` Comments (Line-Start Only)

**Problem:** `'` currently disabled because it conflicts with character literals like `'x'`, `'\n'`, `'\t'`

**Solution:** Only treat `'` as comment start if:
1. It appears at the **start of a line** (optionally after whitespace/tabs)
2. It is NOT followed by another `'` (to avoid `'''` confusion)
3. It is NOT a character literal context

**Grammar Rule:**
```
' is a comment IF:
  - Line starts with: [whitespace/tabs]* '
  - NOT followed by another ' (e.g., not ''')
```

**Examples:**
```fusion
int x = 5
' This is a valid comment (line starts with ')

    ' This is also valid (line starts with whitespace then ')

int y = 'c'  ' ERROR: ' mid-line is NOT a comment (would be treated as char literal + syntax error)

char a = 'x'  // Correct: use // for inline comments
```

**Implementation:**
- Modify `is_comment_start()` in `src/lexer/comments.py`
- Add parameter `at_line_start: bool` to track position
- Only return True for `'` if at_line_start AND next char != `'`

**Rationale:**
- VB.NET developers expect `'` for line comments
- Clear rule: `'` at line start = comment, `'` elsewhere = char literal
- No ambiguity with proper grammar

---

### Feature 2: Triple-Quote Comment Blocks `'''`

**Purpose:** Python-style multi-line comments using `'''`

**Syntax:**
```fusion
'''
This is a multi-line comment block
It can span multiple lines
Similar to Python docstrings
'''

int function add(int a, int b)
    '''
    Adds two numbers
    Returns: sum of a and b
    '''
    return a + b
```

**Grammar:**
```
multi_line_comment_block = "'''" { any_character } "'''"
```

**Features:**
- Starts with `'''` (three single quotes)
- Ends with `'''`
- Can span multiple lines
- Can be indented
- Cannot be nested (first `'''` closes the block)

**Use Cases:**
1. **Documentation blocks** (like Python docstrings)
2. **Commenting out large code sections** (easier than `/* */` for some devs)
3. **Multi-line string literals** (future: may support this)

**Examples:**
```fusion
'''
File: calculator.fusion
Author: Alice
Purpose: Basic arithmetic operations
'''

import Fusion.Math

'''
Function: multiply
Parameters:
  - a: first number
  - b: second number
Returns: product of a and b
'''
int function multiply(int a, int b)
    return a * b
```

**Implementation:**
- Add `skip_triple_quote_comment()` to `src/lexer/comments.py`
- Check for `'''` before checking for `'` single-line comment
- Track line count for proper error location reporting

---


### Feature 3: Comment Style Summary

**After implementation, Fusion will support:**

| Syntax | Type | Scope | Use Case | Status |
|--------|------|-------|----------|--------|
| `//` | Single-line | Rest of line | Inline comments, quick notes | ✅ MVP |
| `/* */` | Multi-line | Between markers | Block comments | ✅ MVP |
| `'` | Single-line | **Line-start only** | VB.NET-style line comments | 🔮 Future |
| `'''` | Multi-line block | Between markers | Python-style docstrings | 🔮 Future |
| `'''language` | Multi-line block | Between markers | Code examples with syntax highlighting | 🔮 Future (Post-Compiler) |

**Style Guide Recommendations:**
- **`//`** - Use for inline comments and brief explanations
- **`/* */`** - Use for multi-line explanations within code
- **`'`** - Use for commenting out entire lines (line-start only)
- **`'''`** - Use for documentation blocks and large comment sections
- **`'''language`** - Use for code examples in documentation with IDE syntax highlighting

---

### Implementation Notes

**Lexer Changes:**
1. Add `at_line_start` tracking to lexer state
2. Modify `is_comment_start()` to check `'''` first, then `'`
3. Add `skip_triple_quote_comment()` method
4. Update tests to re-enable `'` comment tests with line-start restriction

**Parser Changes:**
- None required (comments are lexer-only)

**Grammar Changes:**
```ebnf
comment = single_line_comment | multi_line_comment | line_comment | triple_quote_comment

single_line_comment = "//" { character } newline

multi_line_comment = "/*" { character } "*/"

line_comment = [whitespace] "'" [^"'"] { character } newline
  (* Only valid at line start, not followed by another ' *)

triple_quote_comment = "'''" { character | newline } "'''"
```

**Edge Cases:**
```fusion
' Valid comment
  ' Valid comment (indented)
int x = 5 ' ERROR: not at line start
char c = ''' ERROR: this starts a comment block, not a char
'''

char c = '\'' // Correct: escaped quote in char literal

'''
This is a comment
'''
string s = "test ' not a comment inside string"
```

---

### Testing Strategy

**Test Cases:**
1. `'` at line start → comment
2. `'` after whitespace at line start → comment
3. `'` mid-line → error or char literal context
4. `'''` block → comment
5. Nested `'''` → first closing `'''` ends block
6. `'` inside string literal → not a comment
7. Character literals (`'x'`, `'\n'`) → work correctly

**Files to Update:**
- `src/lexer/comments.py` - Add logic
- `tests/test_comments.py` - Re-enable disabled tests, add new ones
- `tests/test_lexer_integration.py` - Update integration tests

---

### Timeline

**Phase 1:** Re-enable `'` comments (line-start only)
- Estimated: 1-2 days
- Depends on: Lexer tracking line start state

**Phase 2:** Add `'''` block comments
- Estimated: 1-2 days
- Depends on: Phase 1 complete

**Phase 3:** Add `'''language` syntax highlighting support (Post-Compiler)
- Estimated: 8-13 days
- Depends on: Working compiler + fusionlib.IDE module + LSP implementation
- Sub-phases:
  - 2a. Language hint parsing (1 day)
  - 2b. IDE integration via LSP (3-5 days)
  - 2c. DocWiki integration (2-3 days)
  - 2d. Testing and polish (2-4 days)

**Total Timeline:**
- **MVP Comments:** 2-4 days (Phases 1-2)
- **Enhanced Comments:** 8-13 days (Phase 3 - Post-Compiler)
- **Grand Total:** 10-17 days

---

### Benefits

**For VB.NET Developers:**
- ✅ Familiar `'` comment syntax
- ✅ Easier migration from VB.NET code
- ✅ Consistent with VB.NET experience

**For Python Developers:**
- ✅ Familiar `'''` docstring syntax
- ✅ Natural documentation style
- ✅ Easier to comment out large blocks

**For All Developers:**
- ✅ More comment style options
- ✅ Choose preferred style per project
- ✅ Better documentation capabilities

---

### Open Questions

1. **Should `'''` support nested blocks?**
   - **Recommendation:** No - first `'''` closes (same as Python)

2. **Should `'''` be allowed for string literals too?**
   - **Recommendation:** Future feature - multi-line string literals

3. **Should `'` require a space after it?**
   - **Recommendation:** No - `'comment` and `' comment` both valid

4. **What about `''` (two quotes)?**
   - **Recommendation:** Empty string literal, not a comment

5. **Should language hints be case-sensitive?**
   - **Recommendation:** No - normalize to lowercase (`Python`, `python`, `PYTHON` all work)

6. **What if IDE doesn't support the specified language?**
   - **Recommendation:** Gracefully degrade to plain comment (no syntax highlighting)

7. **Should language hints support aliases (e.g., `js` vs `javascript`)?**
   - **Recommendation:** Yes - IDE determines aliases, not compiler

8. **Should Fusion validate language names?**
   - **Recommendation:** No - pass through to IDE/LSP, unknown languages = plain comment

9. **Should `'''language` support language-specific linting?**
   - **Recommendation:** Future feature (post-LSP) - IDE provides inline diagnostics for embedded code

[< 050 Imports](050-Imports.md) | [Index](index.md) | [061 CommentHighlighting >](061-CommentHighlighting.md) <!-- nav -->
