# Task 3.2: Type Checking System

**Phase:** 3 - Semantic Analyzer
**Status:** 🟢 Complete
**Actual Effort:** 4 hours
**Priority:** High (Core validation)
**Completed:** 2025-12-02

---

## 📋 Overview

Implement type checking to validate type compatibility in expressions, assignments, function calls, and return statements. Ensures type safety before code generation.

---

## 🎯 Goals

1. Create TypeChecker class with AST visitor pattern
2. Validate binary/unary expression types
3. Check assignment type compatibility
4. Verify function call argument types
5. Validate return statement types
6. Detect type mismatches with clear error messages

---

## 📝 Requirements

### 1. TypeChecker Class

**File:** `src/semantic/type_checker.py`

```python
class TypeChecker:
    """Type checks the AST using visitor pattern."""

    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.current_function_return_type: Optional[TypeNode] = None
        self.errors: List[SemanticError] = []

    def check_program(self, program: ProgramNode) -> List[SemanticError]:
        """Type check entire program. Returns list of errors."""
        for decl in program.declarations:
            self.visit(decl)
        return self.errors

    def visit(self, node: ASTNode) -> Optional[TypeNode]:
        """Dispatch to appropriate visit method based on node type."""
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ASTNode):
        """Fallback for unhandled node types."""
        raise NotImplementedError(f"No visitor for {node.__class__.__name__}")
```

---

### 2. Type Compatibility Rules

**File:** `src/semantic/type_checker.py`

```python
def types_compatible(self, expected: TypeNode, actual: TypeNode) -> bool:
    """Check if two types are compatible."""
    # Exact match
    if self.types_equal(expected, actual):
        return True

    # Numeric promotions (int -> float -> double)
    if self.is_numeric_promotion(expected, actual):
        return True

    return False

def types_equal(self, type1: TypeNode, type2: TypeNode) -> bool:
    """Check if two types are exactly equal."""
    if isinstance(type1, PrimitiveType) and isinstance(type2, PrimitiveType):
        return type1.name == type2.name
    # Future: handle FunctionType, GenericType, etc.
    return False

def is_numeric_promotion(self, target: TypeNode, source: TypeNode) -> bool:
    """Check if source can be promoted to target (int->float->double)."""
    if not isinstance(target, PrimitiveType) or not isinstance(source, PrimitiveType):
        return False

    promotions = {
        'int': ['int', 'float', 'double'],
        'float': ['float', 'double'],
        'double': ['double']
    }

    if target.name in promotions:
        return source.name in promotions[target.name]
    return False
```

---

### 3. Expression Type Checking

**File:** `src/semantic/type_checker.py`

```python
def visit_LiteralNode(self, node: LiteralNode) -> TypeNode:
    """Return the type of a literal."""
    type_map = {
        'int': 'int',
        'float': 'float',
        'double': 'double',
        'string': 'string',
        'char': 'char',
        'bool': 'bool'
    }
    return PrimitiveType(type_map.get(node.value_type, 'int'))

def visit_IdentifierNode(self, node: IdentifierNode) -> TypeNode:
    """Look up identifier type in symbol table."""
    symbol = self.symbol_table.lookup(node.name)
    if not symbol:
        self.errors.append(SemanticError(
            f"Undefined variable: {node.name}",
            node.location
        ))
        return PrimitiveType('void')  # Error recovery
    return symbol.data_type

def visit_BinaryOpNode(self, node: BinaryOpNode) -> TypeNode:
    """Check binary operation type compatibility."""
    left_type = self.visit(node.left)
    right_type = self.visit(node.right)

    # Arithmetic operators: int/float/double + int/float/double
    if node.op in ['+', '-', '*', '/', '%']:
        if not self.is_numeric_type(left_type):
            self.errors.append(SemanticError(
                f"Left operand of '{node.op}' must be numeric, got {left_type}",
                node.left.location
            ))
        if not self.is_numeric_type(right_type):
            self.errors.append(SemanticError(
                f"Right operand of '{node.op}' must be numeric, got {right_type}",
                node.right.location
            ))
        # Result type is the wider of the two
        return self.get_wider_type(left_type, right_type)

    # Comparison operators: int/float/double -> bool
    if node.op in ['<', '>', '<=', '>=', '==', '!=']:
        if not self.types_compatible(left_type, right_type):
            self.errors.append(SemanticError(
                f"Cannot compare {left_type} with {right_type}",
                node.location
            ))
        return PrimitiveType('bool')

    # Logical operators: bool and bool -> bool
    if node.op in ['and', 'or', '&&', '||']:
        if not self.is_bool_type(left_type):
            self.errors.append(SemanticError(
                f"Left operand of '{node.op}' must be bool, got {left_type}",
                node.left.location
            ))
        if not self.is_bool_type(right_type):
            self.errors.append(SemanticError(
                f"Right operand of '{node.op}' must be bool, got {right_type}",
                node.right.location
            ))
        return PrimitiveType('bool')

    return PrimitiveType('void')  # Unknown operator

def visit_UnaryOpNode(self, node: UnaryOpNode) -> TypeNode:
    """Check unary operation type."""
    operand_type = self.visit(node.operand)

    if node.op == '-':
        if not self.is_numeric_type(operand_type):
            self.errors.append(SemanticError(
                f"Unary minus requires numeric type, got {operand_type}",
                node.operand.location
            ))
        return operand_type

    if node.op in ['not', '!']:
        if not self.is_bool_type(operand_type):
            self.errors.append(SemanticError(
                f"Logical not requires bool type, got {operand_type}",
                node.operand.location
            ))
        return PrimitiveType('bool')

    return PrimitiveType('void')
```

---

### 4. Statement Type Checking

**File:** `src/semantic/type_checker.py`

```python
def visit_VarDeclNode(self, node: VarDeclNode) -> None:
    """Check variable declaration type matches initializer."""
    if node.initializer:
        init_type = self.visit(node.initializer)
        if not self.types_compatible(node.var_type, init_type):
            self.errors.append(SemanticError(
                f"Cannot assign {init_type} to variable of type {node.var_type}",
                node.location
            ))

def visit_AssignmentNode(self, node: AssignmentNode) -> None:
    """Check assignment type compatibility."""
    # Look up target variable
    symbol = self.symbol_table.lookup(node.target)
    if not symbol:
        self.errors.append(SemanticError(
            f"Undefined variable: {node.target}",
            node.location
        ))
        return

    # Check if constant
    if symbol.is_constant:
        self.errors.append(SemanticError(
            f"Cannot assign to constant: {node.target}",
            node.location
        ))

    # Check type compatibility
    value_type = self.visit(node.value)
    if not self.types_compatible(symbol.data_type, value_type):
        self.errors.append(SemanticError(
            f"Cannot assign {value_type} to variable of type {symbol.data_type}",
            node.location
        ))

def visit_ReturnNode(self, node: ReturnNode) -> None:
    """Check return type matches function return type."""
    if not self.current_function_return_type:
        self.errors.append(SemanticError(
            "Return statement outside function",
            node.location
        ))
        return

    if node.value:
        return_type = self.visit(node.value)
        if not self.types_compatible(self.current_function_return_type, return_type):
            self.errors.append(SemanticError(
                f"Return type {return_type} does not match function return type {self.current_function_return_type}",
                node.location
            ))
    else:
        # No return value (return statement without expression)
        if self.current_function_return_type.name != 'void':
            self.errors.append(SemanticError(
                f"Function must return {self.current_function_return_type}",
                node.location
            ))
```

---

### 5. Function Call Type Checking

**File:** `src/semantic/type_checker.py`

```python
def visit_CallNode(self, node: CallNode) -> TypeNode:
    """Check function call argument types."""
    # Look up function
    symbol = self.symbol_table.lookup(node.function_name)
    if not symbol:
        self.errors.append(SemanticError(
            f"Undefined function: {node.function_name}",
            node.location
        ))
        return PrimitiveType('void')

    if symbol.symbol_type != 'function':
        self.errors.append(SemanticError(
            f"{node.function_name} is not a function",
            node.location
        ))
        return PrimitiveType('void')

    # Get function type
    func_type = symbol.data_type
    if not isinstance(func_type, FunctionType):
        return PrimitiveType('void')

    # Check argument count
    expected_count = len(func_type.param_types)
    actual_count = len(node.arguments)
    if actual_count != expected_count:
        self.errors.append(SemanticError(
            f"Function {node.function_name} expects {expected_count} arguments, got {actual_count}",
            node.location
        ))
        return func_type.return_type

    # Check each argument type
    for i, (arg, expected_type) in enumerate(zip(node.arguments, func_type.param_types)):
        actual_type = self.visit(arg)
        if not self.types_compatible(expected_type, actual_type):
            self.errors.append(SemanticError(
                f"Argument {i+1} to {node.function_name}: expected {expected_type}, got {actual_type}",
                arg.location
            ))

    return func_type.return_type
```

---

## ✅ Acceptance Criteria

- [ ] TypeChecker class created with visitor pattern
- [ ] Type compatibility rules implemented (exact match + numeric promotion)
- [ ] Literal type inference works
- [ ] Identifier type lookup works
- [ ] Binary operator type checking (arithmetic, comparison, logical)
- [ ] Unary operator type checking
- [ ] Variable declaration type checking
- [ ] Assignment type checking
- [ ] Return statement type checking
- [ ] Function call type checking (args + return type)
- [ ] Constant assignment prevention
- [ ] Clear error messages with source locations
- [ ] All unit tests pass (50+ tests)

---

## 🧪 Test Cases

### Type Compatibility (10 tests)
- Exact type match (int == int)
- Type mismatch (int != string)
- Numeric promotion (int -> float)
- Numeric promotion (float -> double)
- Numeric promotion (int -> double)
- No promotion backwards (float -> int fails)
- Bool types equal
- String types equal
- Void types equal
- Incompatible types

### Expression Type Inference (12 tests)
- Literal int type
- Literal float type
- Literal string type
- Literal bool type
- Identifier type lookup
- Binary arithmetic (int + int = int)
- Binary arithmetic (int + float = float)
- Binary comparison (int < int = bool)
- Binary logical (bool and bool = bool)
- Unary minus (int)
- Unary not (bool)
- Nested expressions

### Type Errors (15 tests)
- Undefined variable
- Arithmetic on string (error)
- Comparison int with string (error)
- Logical and on int (error)
- Unary minus on bool (error)
- Unary not on int (error)
- Assignment type mismatch
- Variable decl type mismatch
- Return type mismatch
- Function call wrong arg count
- Function call wrong arg type
- Assign to constant (error)
- Return outside function (error)
- Call non-function (error)
- Void in expression (error)

### Control Flow Type Checking (8 tests)
- If condition must be bool
- While condition must be bool
- For condition must be bool
- Return with value in void function (error)
- Return without value in non-void function (error)
- Return correct type
- Multiple returns same type
- If/else branches same type

### Function Call Type Checking (8 tests)
- Call with correct args
- Call with wrong arg count (too few)
- Call with wrong arg count (too many)
- Call with wrong arg type
- Call with numeric promotion (int arg to float param)
- Call returns correct type
- Nested function calls
- Undefined function call

**Total Estimated Tests:** 53 tests

---

## 📁 Files to Create

```
src/semantic/
└── type_checker.py     # TypeChecker class

tests/
└── test_type_checker.py  # Unit tests
```

---

## 🔗 Dependencies

**Depends On:**
- Task 3.1 (Symbol Table) - for symbol lookup
- Task 2.1 (AST Nodes) - for visitor pattern

**Blocks:**
- Task 3.4 (Semantic Analyzer Integration)

---

## 📊 Progress Tracking

- [x] Create `src/semantic/type_checker.py`
- [x] Implement TypeChecker class skeleton
- [x] Implement type compatibility functions
- [x] Implement literal type inference
- [x] Implement identifier type lookup
- [x] Implement binary operator type checking
- [x] Implement unary operator type checking
- [x] Implement variable declaration checking
- [x] Implement assignment checking
- [x] Implement return statement checking
- [x] Implement function call checking
- [x] Create `tests/test_type_checker.py`
- [x] Write type compatibility tests (10 tests)
- [x] Write expression type tests (12 tests)
- [x] Write type error tests (15 tests)
- [x] Write control flow tests (8 tests)
- [x] Write function call tests (8 tests) + 7 additional
- [x] All tests passing (60 tests total)
- [x] Update taskSummary.md to 100%

**Total Tests:** 60 tests (all passing)
**Test Results:** 765 total tests passing, 8 skipped, 0 failures

---

## 💡 Implementation Notes

### Type Hierarchy (Numeric Promotion)
```
int → float → double
```
- int can be used where float is expected
- int/float can be used where double is expected
- No backwards promotion (float → int requires explicit cast)

### Binary Operator Result Types
- `+`, `-`, `*`, `/`, `%`: Returns wider of the two types
- `<`, `>`, `<=`, `>=`, `==`, `!=`: Returns `bool`
- `and`, `or`, `&&`, `||`: Returns `bool`

### Error Recovery
- On type error, return `void` type to prevent cascading errors
- Continue checking rest of program
- Collect all errors, report at end

### Example Type Checking
```fusion
int function add(int a, float b)
    return a + b  # OK: int + float = float, compatible with int return (no, this is ERROR!)
End function

int x = 5
float y = x  # OK: int -> float promotion
int z = y    # ERROR: float -> int not allowed

string s = "hello"
int n = s + 1  # ERROR: string + int not allowed
```

---

## ✅ Definition of Done

- All code implemented and documented
- All 53+ unit tests passing
- No regressions in existing tests (663 still passing)
- Type errors have clear messages with locations
- Code follows project style guidelines
- Task file updated to 100% complete
- taskSummary.md updated with progress
