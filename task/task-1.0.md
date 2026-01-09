# Task 1.0: Phase 1 - Lexer/Tokenizer

**Phase:** Phase 1
**Status:** 🔴 Not Started
**Overall Progress:** 0%
**Depends On:** None (first phase)
**Estimated Effort:** 2-3 weeks (or 15-20 hours in 1-hour sessions)
**Last Updated:** 2025-11-03

---

## 🎯 Goal

Build a complete **lexical analyzer (lexer/tokenizer)** in Python that converts Fusion source code into a stream of tokens.

**Input:** Fusion source code (`.fusion` files)
**Output:** Token stream with type, value, and source location

---

## 📋 Overview

The lexer is the **first phase** of the compiler pipeline:

```
Fusion Source Code → [LEXER] → Token Stream → [Parser] → AST → [Semantic] → [CodeGen] → C Code
```

The lexer must handle Fusion's unique features:
- ✅ **Three block styles:** Indentation (Python), braces (C/Java), End keywords (VB.NET)
- ✅ **INDENT/DEDENT tokens** for indentation-based blocks
- ✅ **60+ keywords** (control flow, types, OOP, memory, threading)
- ✅ **30+ operators** including multi-character (`...`, `?.`, `**`, `<-`, etc.)
- ✅ **String interpolation:** `{var}` and `{@1}` inside strings
- ✅ **Three comment styles:** `//`, `'`, `/* */`
- ✅ **Multiple literal types:** int, float, string, char, bool, null

---

## 📊 Sub-Tasks

| Task ID | Task Name | Status | Progress | File |
|---------|-----------|--------|----------|------|
| 1.1 | Token Definitions & Infrastructure | 🔴 Not Started | 0% | [task-1.1.md](task-1.1.md) |
| 1.2 | Indentation Tracking System | 🔴 Not Started | 0% | [task-1.2.md](task-1.2.md) |
| 1.3 | Block Style Detection | 🔴 Not Started | 0% | [task-1.3.md](task-1.3.md) |
| 1.4 | Keyword Recognition | 🔴 Not Started | 0% | [task-1.4.md](task-1.4.md) |
| 1.5 | Operator Tokenization | 🔴 Not Started | 0% | [task-1.5.md](task-1.5.md) |
| 1.6 | Literal Tokenization | 🔴 Not Started | 0% | [task-1.6.md](task-1.6.md) |
| 1.7 | Comment Handling | 🔴 Not Started | 0% | [task-1.7.md](task-1.7.md) |
| 1.8 | Error Handling & Diagnostics | 🔴 Not Started | 0% | [task-1.8.md](task-1.8.md) |
| 1.9 | Lexer Integration & Testing | 🔴 Not Started | 0% | [task-1.9.md](task-1.9.md) |

---

## ✅ Acceptance Criteria

Phase 1 is complete when:
- [ ] All 9 sub-tasks are complete (1.1 - 1.9)
- [ ] Lexer can tokenize all MVP Fusion features
- [ ] INDENT/DEDENT tokens correctly generated
- [ ] All three block styles supported (indent, braces, End)
- [ ] All 60+ keywords recognized
- [ ] All 30+ operators tokenized (including multi-char)
- [ ] String interpolation parsed correctly
- [ ] Comments properly skipped (three styles)
- [ ] Error messages include source location
- [ ] All unit tests pass (100+ tests)
- [ ] Integration tests pass (6 EBNF test cases)
- [ ] Can tokenize Hello World example
- [ ] Can tokenize factorial example
- [ ] Documentation complete

---

## 🧪 Key Test Cases

### From EBNF Grammar
1. **Test Case 1:** Simple inline lambda
   ```fusion
   int multiply(int x, int y) : x * y
   ```

2. **Test Case 2:** Multi-line with indentation
   ```fusion
   int compare(int a, int b)
       if a < b
           return -1
       return 0
   ```

3. **Test Case 3:** Variable declaration
   ```fusion
   int count = 0
   ```

4. **Test Case 7:** Import statement
   ```fusion
   import Fusion.Core
   ```

5. **Test Case 8:** Lambda expression
   ```fusion
   func comparator = (int a, int b) : a - b
   ```

6. **Test Case 9:** End function syntax
   ```fusion
   int function factorial(int n)
       if n <= 1
           return 1
       End if
       return n * factorial(n - 1)
   End function
   ```

### MVP Examples
7. **Hello World**
   ```fusion
   void function main(string... args)
       print("Hello, Fusion!")
   ```

8. **Factorial**
   ```fusion
   int function factorial(int n)
       if n <= 1
           return 1
       return n * factorial(n - 1)
   ```

---

## 🏗️ Implementation Strategy

### Recommended Order
1. **Task 1.1:** Build foundation (Token class, infrastructure)
2. **Task 1.4:** Implement keyword recognition (simple lookup)
3. **Task 1.5:** Implement operator tokenization (single-char first)
4. **Task 1.6:** Implement literal tokenization (ints, strings)
5. **Task 1.7:** Implement comment handling (skip tokens)
6. **Task 1.2:** Implement indentation tracking (complex but critical)
7. **Task 1.3:** Implement block style detection (uses indentation)
8. **Task 1.8:** Implement error handling (used throughout)
9. **Task 1.9:** Integration testing and validation

**Rationale:** Build simple features first, then tackle complex indentation system, finish with integration.

---

## 📚 Key Algorithms

### 1. Indentation Tracking (INDENT/DEDENT)
```python
# Stack-based algorithm from EBNF spec
indent_stack = [0]

on_newline_with_content:
    current_indent = count_leading_whitespace()

    if current_indent > indent_stack[-1]:
        indent_stack.append(current_indent)
        emit(INDENT)

    elif current_indent < indent_stack[-1]:
        while indent_stack[-1] > current_indent:
            indent_stack.pop()
            emit(DEDENT)

        if indent_stack[-1] != current_indent:
            error("Indentation mismatch")

    # Equal indent: no INDENT/DEDENT
```

### 2. Longest-Match Operator Recognition
```python
# Try longest match first
if peek(3) == "...":
    return RANGE_OP
elif peek(2) == "**":
    return POWER_OP
elif peek(2) == "?.":
    return SAFE_NAV_OP
elif peek(1) == "*":
    return MULTIPLY_OP
```

### 3. String Interpolation Parsing
```python
# Inside string literal
if char == '{':
    if next_char == '@':
        # Positional: {@1}
        parse_positional_interpolation()
    else:
        # Inline: {varName}
        parse_inline_interpolation()
```

---

## 📝 Implementation Notes

### Python Libraries Needed
- **dataclasses:** For Token class definition
- **enum:** For TokenType enumeration
- **typing:** For type hints
- **pytest:** For testing framework
- **re:** For regex (optional, for literals)

### File Structure
```
src/lexer/
├── __init__.py
├── token.py              # Token class, TokenType enum
├── lexer.py              # Main Lexer class
├── keywords.py           # Keyword lookup table
└── source_location.py    # SourceLocation class
```

### Token Class Structure
```python
@dataclass
class Token:
    type: TokenType
    value: str
    location: SourceLocation

class TokenType(Enum):
    # Keywords
    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    # ... 60+ more

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    # ... 30+ more

    # Literals
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    # ...

    # Special
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"
```

---

## 🚨 Critical Challenges

### 1. Indentation Tracking
**Complexity:** High
**Risk:** Bugs in INDENT/DEDENT will break parser
**Mitigation:** Extensive unit tests, follow EBNF algorithm exactly

### 2. Block Style Switching
**Complexity:** Medium
**Risk:** Mixing styles incorrectly (e.g., `{` with End)
**Mitigation:** Track block context, validate proper nesting

### 3. String Interpolation
**Complexity:** Medium
**Risk:** Complex parsing inside strings
**Mitigation:** Separate string lexer sub-function

### 4. Multi-Character Operators
**Complexity:** Low-Medium
**Risk:** `=` vs `==`, `<` vs `<=` vs `<-`, `.` vs `...`
**Mitigation:** Longest-match algorithm with lookahead

---

## 🔗 Dependencies

### Required Before Starting
- ✅ Fusion language spec (files/fusion-language-spec.md)
- ✅ EBNF grammar (files/fusion.ebnf)
- ✅ Python 3.10+ installed
- ✅ pytest installed
- ✅ Project structure created

### Blocks Following Phases
- Phase 2 (Parser) cannot start until Phase 1 complete
- Phase 3 (Semantic) blocked by Phase 2
- Phase 4 (CodeGen) blocked by Phase 3

---

## 📈 Progress Tracking

**Current Status:** 🔴 Not Started (0%)

**Update after each sub-task:**
- Task 1.1 complete → 11% progress
- Task 1.2 complete → 22% progress
- Task 1.3 complete → 33% progress
- Task 1.4 complete → 44% progress
- Task 1.5 complete → 56% progress
- Task 1.6 complete → 67% progress
- Task 1.7 complete → 78% progress
- Task 1.8 complete → 89% progress
- Task 1.9 complete → 100% progress ✅

---

## 🎯 Next Action

**Start with:** Task 1.1 - Token Definitions & Infrastructure

This establishes the foundation for all other lexer tasks.

---

**File:** task-1.0.md
**Last Updated:** 2025-11-03
