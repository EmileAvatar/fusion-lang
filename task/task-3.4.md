# Task 3.4: Control Flow Validation

**Phase:** 3 - Semantic Analyzer
**Status:** 🟢 Complete
**Actual Effort:** 2.5 hours
**Priority:** Medium (Quality validation)

---

## 📋 Overview

Validate control flow semantics: ensure all code paths return values (for non-void functions), detect unreachable code, validate break/continue usage, and check loop conditions.

---

## 🎯 Goals

1. Create ControlFlowValidator class
2. Ensure non-void functions return on all paths
3. Detect unreachable code after return/break/continue
4. Validate break/continue only appear inside loops
5. Validate conditions are boolean type
6. Detect missing return statements

---

## 📝 Requirements

### 1. ControlFlowValidator Class

**File:** `src/semantic/control_flow_validator.py`

```python
class ControlFlowValidator:
    """Validates control flow semantics."""

    def __init__(self):
        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []
        self.in_loop: int = 0  # Loop nesting depth
        self.current_function_return_type: Optional[TypeNode] = None

    def validate_program(self, program: ProgramNode) -> Tuple[List[SemanticError], List[SemanticError]]:
        """Validate control flow in entire program."""
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode):
                self.validate_function(decl)
        return self.errors, self.warnings
```

---

### 2. Return Path Validation

**File:** `src/semantic/control_flow_validator.py`

```python
def validate_function(self, func: FunctionDeclNode) -> None:
    """Validate function control flow."""
    self.current_function_return_type = func.return_type

    if func.body:
        returns = self.check_returns(func.body)

        # Non-void functions must return on all paths
        if func.return_type.name != 'void' and not returns:
            self.errors.append(SemanticError(
                f"Function '{func.name}' must return {func.return_type} on all code paths",
                func.location
            ))

    self.current_function_return_type = None

def check_returns(self, stmt: ASTNode) -> bool:
    """Check if a statement always returns. Returns True if all paths return."""
    if isinstance(stmt, ReturnNode):
        return True

    elif isinstance(stmt, BlockNode):
        # Block returns if any statement returns
        # (and there's no code after it, checked separately)
        for s in stmt.statements:
            if self.check_returns(s):
                return True
        return False

    elif isinstance(stmt, IfNode):
        # If returns only if both branches return
        if stmt.else_branch:
            then_returns = self.check_returns(stmt.then_branch)
            else_returns = self.check_returns(stmt.else_branch)
            return then_returns and else_returns
        return False

    elif isinstance(stmt, WhileNode):
        # While loops don't guarantee return (might not execute)
        return False

    elif isinstance(stmt, ForNode):
        # For loops don't guarantee return (might not execute)
        return False

    else:
        return False
```

---

### 3. Unreachable Code Detection

**File:** `src/semantic/control_flow_validator.py`

```python
def check_unreachable_code(self, stmt: ASTNode) -> None:
    """Detect unreachable code after return/break/continue."""
    if isinstance(stmt, BlockNode):
        found_terminal = False
        for i, s in enumerate(stmt.statements):
            if found_terminal:
                # Code after return/break/continue
                self.warnings.append(SemanticError(
                    "Unreachable code detected",
                    s.location
                ))
                break  # Only warn once per block

            if self.is_terminal_statement(s):
                found_terminal = True

            # Recursively check nested statements
            self.check_unreachable_code(s)

    elif isinstance(stmt, IfNode):
        self.check_unreachable_code(stmt.then_branch)
        if stmt.else_branch:
            self.check_unreachable_code(stmt.else_branch)

    elif isinstance(stmt, WhileNode):
        self.check_unreachable_code(stmt.body)

    elif isinstance(stmt, ForNode):
        self.check_unreachable_code(stmt.body)

def is_terminal_statement(self, stmt: ASTNode) -> bool:
    """Check if statement terminates execution (return/break/continue)."""
    return isinstance(stmt, (ReturnNode, BreakNode, ContinueNode))
```

---

### 4. Break/Continue Validation

**File:** `src/semantic/control_flow_validator.py`

```python
def validate_statement(self, stmt: ASTNode) -> None:
    """Validate a single statement."""
    if isinstance(stmt, BreakNode):
        if self.in_loop == 0:
            self.errors.append(SemanticError(
                "Break statement outside loop",
                stmt.location
            ))

    elif isinstance(stmt, ContinueNode):
        if self.in_loop == 0:
            self.errors.append(SemanticError(
                "Continue statement outside loop",
                stmt.location
            ))

    elif isinstance(stmt, WhileNode):
        self.in_loop += 1
        self.validate_statement(stmt.body)
        self.in_loop -= 1

    elif isinstance(stmt, ForNode):
        self.in_loop += 1
        self.validate_statement(stmt.body)
        self.in_loop -= 1

    elif isinstance(stmt, BlockNode):
        for s in stmt.statements:
            self.validate_statement(s)

    elif isinstance(stmt, IfNode):
        self.validate_statement(stmt.then_branch)
        if stmt.else_branch:
            self.validate_statement(stmt.else_branch)
```

---

### 5. Condition Type Validation

**File:** `src/semantic/control_flow_validator.py`

```python
def validate_conditions(self, stmt: ASTNode, type_checker: TypeChecker) -> None:
    """Ensure all conditions are boolean type."""
    if isinstance(stmt, IfNode):
        cond_type = type_checker.visit(stmt.condition)
        if not self.is_bool_type(cond_type):
            self.errors.append(SemanticError(
                f"If condition must be bool, got {cond_type}",
                stmt.condition.location
            ))
        self.validate_conditions(stmt.then_branch, type_checker)
        if stmt.else_branch:
            self.validate_conditions(stmt.else_branch, type_checker)

    elif isinstance(stmt, WhileNode):
        cond_type = type_checker.visit(stmt.condition)
        if not self.is_bool_type(cond_type):
            self.errors.append(SemanticError(
                f"While condition must be bool, got {cond_type}",
                stmt.condition.location
            ))
        self.validate_conditions(stmt.body, type_checker)

    elif isinstance(stmt, ForNode):
        if stmt.condition:
            cond_type = type_checker.visit(stmt.condition)
            if not self.is_bool_type(cond_type):
                self.errors.append(SemanticError(
                    f"For condition must be bool, got {cond_type}",
                    stmt.condition.location
                ))
        self.validate_conditions(stmt.body, type_checker)

    elif isinstance(stmt, BlockNode):
        for s in stmt.statements:
            self.validate_conditions(s, type_checker)

def is_bool_type(self, type_node: TypeNode) -> bool:
    """Check if type is bool."""
    return isinstance(type_node, PrimitiveType) and type_node.name == 'bool'
```

---

## ✅ Acceptance Criteria

- [x] ControlFlowValidator class created
- [x] Non-void functions must return on all paths
- [x] Void functions can omit return statement
- [x] Unreachable code detected (warnings, not errors)
- [x] Break only allowed inside loops
- [x] Continue only allowed inside loops
- [x] If conditions must be bool
- [x] While conditions must be bool
- [x] For conditions must be bool (if present)
- [x] Nested loops handled correctly
- [x] All unit tests pass (35 tests)

---

## 🧪 Test Cases

### Return Path Validation (12 tests)
- Void function without return (OK)
- Void function with return (OK)
- Non-void function with return (OK)
- Non-void function without return (error)
- Function with if-else both return (OK)
- Function with if-else only then returns (error)
- Function with if (no else) returns (error, might not execute)
- Multiple return statements (OK)
- Return in nested block (OK)
- Function with while loop return (error, loop might not execute)
- Lambda with return (OK)
- Early return followed by unreachable return (warning)

### Unreachable Code Detection (8 tests)
- Code after return (warning)
- Code after break (warning)
- Code after continue (warning)
- Return in if branch, code after if (OK, else branch might execute)
- Multiple statements after return (warn on first)
- Nested unreachable code
- Return at end of function (OK)
- Break at end of loop (OK)

### Break/Continue Validation (8 tests)
- Break inside while (OK)
- Break inside for (OK)
- Break outside loop (error)
- Continue inside while (OK)
- Continue inside for (OK)
- Continue outside loop (error)
- Nested loops with break (breaks inner only)
- Break in if inside loop (OK)

### Condition Type Validation (7 tests)
- If with bool condition (OK)
- If with int condition (error)
- While with bool condition (OK)
- While with int condition (error)
- For with bool condition (OK)
- For with no condition (OK)
- Nested if conditions (all must be bool)

**Total Estimated Tests:** 35 tests

---

## 📁 Files to Create

```
src/semantic/
└── control_flow_validator.py  # ControlFlowValidator class

tests/
└── test_control_flow_validator.py  # Unit tests
```

---

## 🔗 Dependencies

**Depends On:**
- Task 3.2 (Type Checker) - for condition type checking
- Task 2.1 (AST Nodes) - for traversal

**Blocks:**
- Task 3.5 (Semantic Analyzer Integration)

---

## 📊 Progress Tracking

- [x] Create `src/semantic/control_flow_validator.py`
- [x] Implement ControlFlowValidator class skeleton
- [x] Implement return path checking
- [x] Implement unreachable code detection
- [x] Implement break/continue validation
- [x] Implement condition type validation
- [x] Create `tests/test_control_flow_validator.py`
- [x] Write return path tests (12 tests)
- [x] Write unreachable code tests (8 tests)
- [x] Write break/continue tests (8 tests)
- [x] Write condition type tests (7 tests)
- [x] All tests passing (35/35 tests)
- [x] Update taskSummary.md to 100%

---

## 💡 Implementation Notes

### Return Path Analysis
Complex logic for if/else:
```fusion
int function test1()
    if condition
        return 1
    else
        return 2
    # OK: both branches return
End function

int function test2()
    if condition
        return 1
    # ERROR: else branch doesn't return
End function

int function test3()
    if condition
        return 1
    return 2  # OK: guaranteed return after if
End function
```

### Unreachable Code (Warnings)
```fusion
int function test()
    return 1
    int x = 5  # WARNING: unreachable
End function

void function loop()
    while true
        break
        print("hi")  # WARNING: unreachable
End function
```

### Break/Continue Depth Tracking
```fusion
while condition1
    if condition2
        break  # OK: inside loop (depth = 1)
    while condition3
        break  # OK: inside nested loop (depth = 2)
End while

break  # ERROR: outside loop (depth = 0)
```

### Condition Type Enforcement
```fusion
int x = 5
if x > 0  # OK: comparison returns bool
    print("positive")

if x  # ERROR: int is not bool (no implicit conversion)
    print("non-zero")

while true  # OK: bool literal
    break
```

---

## ✅ Definition of Done

- All code implemented and documented
- All 35+ unit tests passing
- No regressions in existing tests
- Warnings vs errors used appropriately
- Clear error messages with locations
- Code follows project style guidelines
- Task file updated to 100% complete
- taskSummary.md updated with progress
