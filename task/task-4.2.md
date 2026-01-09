# Task 4.2: Expression Code Generation

**Phase:** 4 - Code Generator
**Status:** 🟢 Complete
**Estimated Effort:** 4-5 hours
**Actual Effort:** ~2 hours
**Priority:** High (Core functionality)
**Completed:** 2025-12-06

---

## 📋 Overview

Implement code generation for all expression types: literals, identifiers, binary operations, unary operations, function calls, and lambda expressions. These are the building blocks for all other code generation.

---

## 🎯 Goals

1. Generate code for literal expressions (int, float, string, bool, char)
2. Generate code for identifier expressions (variables, parameters)
3. Generate code for binary operations (arithmetic, comparison, logical)
4. Generate code for unary operations (-, not, !)
5. Generate code for function call expressions
6. Generate code for string interpolation
7. Handle operator precedence and parentheses

---

## 📝 Requirements

### 1. Literal Expressions

**File:** `src/codegen/c_generator.py`

```python
def visit_LiteralExpr(self, node: LiteralExpr) -> str:
    """Generate C code for literal expression.

    Args:
        node: Literal expression node

    Returns:
        C literal representation
    """
    type_hint = node.type_hint

    if type_hint == 'int':
        return str(node.value)

    elif type_hint == 'float':
        return f'{node.value}f'  # Add 'f' suffix

    elif type_hint == 'double':
        return str(node.value)

    elif type_hint == 'bool':
        return 'true' if node.value else 'false'

    elif type_hint == 'char':
        # Escape special characters
        escaped = node.value.replace('\\', '\\\\').replace("'", "\\'")
        return f"'{escaped}'"

    elif type_hint == 'string':
        # Escape special characters
        escaped = node.value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

    elif type_hint == 'null':
        return 'NULL'

    return '0'  # Fallback
```

### 2. Identifier Expressions

```python
def visit_IdentifierExpr(self, node: IdentifierExpr) -> str:
    """Generate C code for identifier expression.

    Args:
        node: Identifier expression node

    Returns:
        Variable/parameter name
    """
    return node.name
```

### 3. Binary Operations

```python
def visit_BinaryExpr(self, node: BinaryExpr) -> str:
    """Generate C code for binary expression.

    Args:
        node: Binary expression node

    Returns:
        C binary operation expression
    """
    left = self.visit(node.left)
    right = self.visit(node.right)
    op = node.operator

    # Map Fusion operators to C operators
    operator_map = {
        # Arithmetic
        '+': '+',
        '-': '-',
        '*': '*',
        '/': '/',
        '%': '%',
        '**': 'pow',  # Power requires math.h

        # Comparison
        '<': '<',
        '>': '>',
        '<=': '<=',
        '>=': '>=',
        '==': '==',
        '!=': '!=',

        # Logical
        'and': '&&',
        'or': '||',
        '&&': '&&',
        '||': '||',
    }

    c_op = operator_map.get(op, op)

    # Special case: power operator
    if op == '**':
        self.includes.add('<math.h>')
        return f'pow({left}, {right})'

    # Add parentheses for clarity
    return f'({left} {c_op} {right})'
```

### 4. Unary Operations

```python
def visit_UnaryExpr(self, node: UnaryExpr) -> str:
    """Generate C code for unary expression.

    Args:
        node: Unary expression node

    Returns:
        C unary operation expression
    """
    operand = self.visit(node.operand)
    op = node.operator

    operator_map = {
        '-': '-',
        '!': '!',
        'not': '!',
    }

    c_op = operator_map.get(op, op)
    return f'({c_op}{operand})'
```

### 5. Function Call Expressions

```python
def visit_CallExpr(self, node: CallExpr) -> str:
    """Generate C code for function call expression.

    Args:
        node: Call expression node

    Returns:
        C function call
    """
    # Get function name
    if isinstance(node.callee, IdentifierExpr):
        func_name = node.callee.name

        # Special handling for built-in functions
        if func_name == 'print':
            return self._generate_print_call(node)

    func = self.visit(node.callee)

    # Generate arguments
    args = ', '.join(self.visit(arg) for arg in node.arguments)

    return f'{func}({args})'

def _generate_print_call(self, node: CallExpr) -> str:
    """Generate code for print() built-in function.

    Args:
        node: Call expression node for print

    Returns:
        printf() call
    """
    if len(node.arguments) == 0:
        return 'printf("\\n")'

    arg = node.arguments[0]

    # Handle string interpolation
    if isinstance(arg, InterpolatedStringExpr):
        return self._generate_interpolated_print(arg)

    # Simple print
    arg_code = self.visit(arg)
    return f'printf("%s\\n", {arg_code})'
```

### 6. String Interpolation

```python
def visit_InterpolatedStringExpr(self, node: InterpolatedStringExpr) -> str:
    """Generate C code for interpolated string expression.

    Args:
        node: Interpolated string expression node

    Returns:
        C sprintf expression or direct printf
    """
    # This is complex - for MVP, we'll use sprintf
    # Full implementation in the actual task
    pass

def _generate_interpolated_print(self, node: InterpolatedStringExpr) -> str:
    """Generate printf for interpolated string.

    Args:
        node: Interpolated string node

    Returns:
        printf() with format string and arguments
    """
    # Parse interpolation parts from node.parts (JSON encoded)
    import json
    parts = json.loads(node.parts)

    format_str = ''
    args = []

    for part in parts:
        if part[0] == 'STRING_PART':
            format_str += part[1]
        elif part[0] == 'VAR_INTERP':
            var_name = part[1]
            format_str += '%d'  # Assume int for MVP (needs type info)
            args.append(var_name)
        elif part[0] == 'POS_INTERP':
            # Positional interpolation - not yet supported
            pass

    format_str += '\\n'

    if args:
        args_str = ', ' + ', '.join(args)
    else:
        args_str = ''

    return f'printf("{format_str}"{args_str})'
```

---

## ✅ Acceptance Criteria

- [ ] Literal expressions generate correct C literals
- [ ] Identifier expressions generate variable names
- [ ] Binary operations generate correct C operators
- [ ] Operator precedence handled with parentheses
- [ ] Unary operations generate correct C code
- [ ] Function calls generate correct C function calls
- [ ] print() function generates printf() calls
- [ ] String interpolation works (basic MVP version)
- [ ] All tests pass (35+ tests)

---

## 🧪 Test Cases

### Literal Expressions (10 tests)
- Integer literal: `42` → `42`
- Float literal: `3.14` → `3.14f`
- Double literal: `3.14159` → `3.14159`
- Boolean true: `true` → `true`
- Boolean false: `false` → `false`
- Character: `'a'` → `'a'`
- String: `"hello"` → `"hello"`
- String with escape: `"hello\n"` → `"hello\\n"`
- Null literal: `null` → `NULL`
- Character with escape: `'\n'` → `'\\n'`

### Identifier Expressions (3 tests)
- Simple variable: `x` → `x`
- Parameter: `param` → `param`
- Function name: `add` → `add`

### Binary Operations (12 tests)
- Addition: `a + b` → `(a + b)`
- Subtraction: `a - b` → `(a - b)`
- Multiplication: `a * b` → `(a * b)`
- Division: `a / b` → `(a / b)`
- Modulo: `a % b` → `(a % b)`
- Less than: `a < b` → `(a < b)`
- Greater than: `a > b` → `(a > b)`
- Equals: `a == b` → `(a == b)`
- Not equals: `a != b` → `(a != b)`
- Logical and: `a and b` → `(a && b)`
- Logical or: `a or b` → `(a || b)`
- Power: `a ** b` → `pow(a, b)` (adds math.h)

### Unary Operations (3 tests)
- Negation: `-x` → `(-x)`
- Logical not: `not x` → `(!x)`
- Logical not (!): `!x` → `(!x)`

### Function Calls (7 tests)
- Simple call: `add(1, 2)` → `add(1, 2)`
- No args: `foo()` → `foo()`
- Nested call: `add(mul(2, 3), 4)` → `add(mul(2, 3), 4)`
- Print string: `print("hello")` → `printf("%s\\n", "hello")`
- Print empty: `print()` → `printf("\\n")`
- Print with variable: `print("{x}")` → `printf("%d\\n", x)`
- Print with multiple vars: `print("{x} and {y}")` → `printf("%d and %d\\n", x, y)`

**Total Estimated Tests:** 35 tests

---

## 📁 Files to Create/Update

```
src/codegen/
└── c_generator.py          # Add expression visitors

tests/
└── test_codegen_expressions.py  # Expression generation tests
```

---

## 🔗 Dependencies

**Depends On:**
- Task 4.1 (Code Generator Infrastructure)

**Blocks:**
- Task 4.3 (Statement Code Generation)
- Task 4.4 (Function Code Generation)

---

## 📊 Progress Tracking

- [x] Implement visit_LiteralExpr() ✅
- [x] Implement visit_IdentifierExpr() ✅
- [x] Implement visit_BinaryExpr() ✅
- [x] Implement visit_UnaryExpr() ✅
- [x] Implement visit_CallExpr() ✅
- [x] Implement _generate_print_call() ✅
- [x] Implement visit_InterpolatedStringExpr() ✅
- [x] Implement _generate_interpolated_print() ✅
- [x] Create `tests/test_codegen_expressions.py` ✅
- [x] Write literal expression tests (10 tests) ✅
- [x] Write identifier expression tests (3 tests) ✅
- [x] Write binary operation tests (12 tests) ✅
- [x] Write unary operation tests (3 tests) ✅
- [x] Write function call tests (7 tests) ✅
- [x] Write string interpolation tests (3 tests) ✅
- [x] Write complex expression tests (3 tests) ✅
- [x] All tests passing (41/41 tests) ✅
- [x] Update taskSummary.md ✅

## ✅ Completion Summary

**Total Tests Created:** 41 tests
**Tests Passing:** 41/41 (100%)
**Files Created:** 1 (test_codegen_expressions.py)
**Files Modified:** 1 (c_generator.py)

**Test Breakdown:**
- Literal expressions: 10 tests
- Identifier expressions: 3 tests
- Binary operations: 12 tests
- Unary operations: 3 tests
- Function calls: 7 tests
- String interpolation: 3 tests
- Complex expressions: 3 tests

**Overall Project Progress:**
- Total tests: 945 passing + 8 skipped + 14 failing (semantic integration)
- Code generation tests: 66 total (25 infrastructure + 41 expressions)

---

## 💡 Implementation Notes

### String Interpolation Format Specifiers

For MVP, use simple type-based format specifiers:
- `int` → `%d`
- `float` → `%f`
- `double` → `%lf`
- `char` → `%c`
- `string` → `%s`
- `bool` → `%d` (0 or 1)

**Example:**
```fusion
int x = 42
print("Value: {x}")
```

**Generates:**
```c
int x = 42;
printf("Value: %d\n", x);
```

### Operator Precedence

C operator precedence (highest to lowest):
1. Unary: `!`, `-`, `+`
2. Multiplicative: `*`, `/`, `%`
3. Additive: `+`, `-`
4. Relational: `<`, `>`, `<=`, `>=`
5. Equality: `==`, `!=`
6. Logical AND: `&&`
7. Logical OR: `||`

Use parentheses liberally to ensure correct precedence.

### Special Cases

**Power Operator:**
- Fusion `**` → C `pow(a, b)`
- Requires `#include <math.h>`
- Link with `-lm` when compiling

**Boolean Literals:**
- Requires `#include <stdbool.h>`
- `true` and `false` are C99+ keywords

---

## ✅ Definition of Done

- All expression visitors implemented
- All 35 expression tests passing
- Code generates valid C syntax
- Operator precedence handled correctly
- String interpolation works (MVP version)
- Task file updated to 100% complete
- taskSummary.md updated
