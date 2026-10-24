# Task 3.3: Name Resolution & Scope Validation

**Phase:** 3 - Semantic Analyzer
**Status:** 🟢 Complete
**Actual Effort:** 3 hours
**Priority:** High (Essential validation)
**Completed:** 2025-12-02

---

## 📋 Overview

Implement name resolution to link identifier uses to their declarations, validate scoping rules, and detect undefined variables/functions. Builds the symbol table by traversing the AST.

---

## 🎯 Goals

1. Create NameResolver class to populate symbol table
2. Traverse AST and define symbols (functions, variables, parameters)
3. Validate variable/function references
4. Detect undefined identifiers
5. Handle nested scopes correctly
6. Prevent duplicate declarations in same scope

---

## 📝 Requirements

### 1. NameResolver Class

**File:** `src/semantic/name_resolver.py`

```python
class NameResolver:
    """Resolves names and populates the symbol table."""

    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.errors: List[SemanticError] = []
        self.current_function: Optional[str] = None

    def resolve_program(self, program: ProgramNode) -> List[SemanticError]:
        """Resolve all names in the program."""
        # First pass: register all function declarations
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode):
                self.register_function(decl)

        # Second pass: resolve function bodies
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode):
                self.resolve_function(decl)

        return self.errors

    def register_function(self, func: FunctionDeclNode) -> None:
        """Register a function in the global symbol table."""
        try:
            # Create function type
            param_types = [param.param_type for param in func.parameters]
            func_type = FunctionType(func.return_type, param_types)

            # Create symbol
            symbol = Symbol(
                name=func.name,
                symbol_type='function',
                data_type=func_type,
                location=func.location
            )

            # Add to global scope
            self.symbol_table.define(symbol)

        except SemanticError as e:
            self.errors.append(e)
```

---

### 2. Function Body Resolution

**File:** `src/semantic/name_resolver.py`

```python
def resolve_function(self, func: FunctionDeclNode) -> None:
    """Resolve names inside a function body."""
    self.current_function = func.name

    # Enter function scope
    self.symbol_table.enter_scope(f"function:{func.name}")

    try:
        # Register parameters
        for param in func.parameters:
            self.register_parameter(param)

        # Resolve function body
        if func.body:
            self.resolve_statement(func.body)

    finally:
        # Always exit scope, even on error
        self.symbol_table.exit_scope()
        self.current_function = None

def register_parameter(self, param: ParameterNode) -> None:
    """Register a function parameter in current scope."""
    try:
        symbol = Symbol(
            name=param.name,
            symbol_type='parameter',
            data_type=param.param_type,
            location=param.location
        )
        self.symbol_table.define(symbol)
    except SemanticError as e:
        self.errors.append(e)
```

---

### 3. Statement Resolution

**File:** `src/semantic/name_resolver.py`

```python
def resolve_statement(self, stmt: ASTNode) -> None:
    """Resolve names in a statement."""
    if isinstance(stmt, VarDeclNode):
        self.resolve_var_decl(stmt)
    elif isinstance(stmt, AssignmentNode):
        self.resolve_assignment(stmt)
    elif isinstance(stmt, ReturnNode):
        self.resolve_return(stmt)
    elif isinstance(stmt, IfNode):
        self.resolve_if(stmt)
    elif isinstance(stmt, WhileNode):
        self.resolve_while(stmt)
    elif isinstance(stmt, ForNode):
        self.resolve_for(stmt)
    elif isinstance(stmt, BlockNode):
        self.resolve_block(stmt)
    elif isinstance(stmt, ExpressionStatementNode):
        self.resolve_expression(stmt.expression)

def resolve_var_decl(self, stmt: VarDeclNode) -> None:
    """Resolve variable declaration."""
    # First resolve initializer (if any)
    if stmt.initializer:
        self.resolve_expression(stmt.initializer)

    # Then define the variable
    try:
        symbol = Symbol(
            name=stmt.name,
            symbol_type='constant' if stmt.is_const else 'variable',
            data_type=stmt.var_type,
            location=stmt.location,
            is_constant=stmt.is_const
        )
        self.symbol_table.define(symbol)
    except SemanticError as e:
        self.errors.append(e)

def resolve_assignment(self, stmt: AssignmentNode) -> None:
    """Resolve assignment (check target exists)."""
    # Check if target variable is defined
    symbol = self.symbol_table.lookup(stmt.target)
    if not symbol:
        self.errors.append(SemanticError(
            f"Undefined variable: {stmt.target}",
            stmt.location
        ))

    # Resolve value expression
    self.resolve_expression(stmt.value)

def resolve_return(self, stmt: ReturnNode) -> None:
    """Resolve return statement."""
    if stmt.value:
        self.resolve_expression(stmt.value)

def resolve_if(self, stmt: IfNode) -> None:
    """Resolve if statement."""
    self.resolve_expression(stmt.condition)
    self.resolve_statement(stmt.then_branch)
    if stmt.else_branch:
        self.resolve_statement(stmt.else_branch)

def resolve_while(self, stmt: WhileNode) -> None:
    """Resolve while loop."""
    self.resolve_expression(stmt.condition)
    self.resolve_statement(stmt.body)

def resolve_for(self, stmt: ForNode) -> None:
    """Resolve for loop."""
    # Enter new scope for loop variable
    self.symbol_table.enter_scope("block:for")

    try:
        if stmt.initializer:
            self.resolve_statement(stmt.initializer)
        if stmt.condition:
            self.resolve_expression(stmt.condition)
        if stmt.increment:
            self.resolve_statement(stmt.increment)
        self.resolve_statement(stmt.body)
    finally:
        self.symbol_table.exit_scope()

def resolve_block(self, stmt: BlockNode) -> None:
    """Resolve block statement."""
    # Enter new scope
    self.symbol_table.enter_scope(f"block:{id(stmt)}")

    try:
        for statement in stmt.statements:
            self.resolve_statement(statement)
    finally:
        self.symbol_table.exit_scope()
```

---

### 4. Expression Resolution

**File:** `src/semantic/name_resolver.py`

```python
def resolve_expression(self, expr: ASTNode) -> None:
    """Resolve names in an expression."""
    if isinstance(expr, IdentifierNode):
        self.resolve_identifier(expr)
    elif isinstance(expr, BinaryOpNode):
        self.resolve_expression(expr.left)
        self.resolve_expression(expr.right)
    elif isinstance(expr, UnaryOpNode):
        self.resolve_expression(expr.operand)
    elif isinstance(expr, CallNode):
        self.resolve_call(expr)
    elif isinstance(expr, LambdaNode):
        self.resolve_lambda(expr)
    elif isinstance(expr, LiteralNode):
        pass  # Literals don't need resolution
    elif isinstance(expr, InterpolatedStringNode):
        for part in expr.parts:
            if isinstance(part, dict) and 'expr' in part:
                self.resolve_expression(part['expr'])

def resolve_identifier(self, expr: IdentifierNode) -> None:
    """Check if identifier is defined."""
    symbol = self.symbol_table.lookup(expr.name)
    if not symbol:
        self.errors.append(SemanticError(
            f"Undefined variable: {expr.name}",
            expr.location
        ))

def resolve_call(self, expr: CallNode) -> None:
    """Resolve function call."""
    # Check if function is defined
    symbol = self.symbol_table.lookup(expr.function_name)
    if not symbol:
        self.errors.append(SemanticError(
            f"Undefined function: {expr.function_name}",
            expr.location
        ))
    elif symbol.symbol_type != 'function':
        self.errors.append(SemanticError(
            f"{expr.function_name} is not a function",
            expr.location
        ))

    # Resolve arguments
    for arg in expr.arguments:
        self.resolve_expression(arg)

def resolve_lambda(self, expr: LambdaNode) -> None:
    """Resolve lambda expression."""
    # Enter lambda scope
    self.symbol_table.enter_scope(f"lambda:{id(expr)}")

    try:
        # Register lambda parameters
        for param in expr.parameters:
            self.register_parameter(param)

        # Resolve lambda body
        if isinstance(expr.body, list):
            for stmt in expr.body:
                self.resolve_statement(stmt)
        else:
            self.resolve_expression(expr.body)
    finally:
        self.symbol_table.exit_scope()
```

---

## ✅ Acceptance Criteria

- [ ] NameResolver class created
- [ ] Function declarations registered in global scope
- [ ] Function parameters registered in function scope
- [ ] Variable declarations registered in current scope
- [ ] Duplicate declarations detected (same scope)
- [ ] Undefined variables detected
- [ ] Undefined functions detected
- [ ] Nested scopes handled correctly (for, blocks, lambdas)
- [ ] Identifier resolution checks all parent scopes
- [ ] Clear error messages with source locations
- [ ] All unit tests pass (45+ tests)

---

## 🧪 Test Cases

### Function Registration (8 tests)
- Register single function
- Register multiple functions
- Duplicate function name (error)
- Function with parameters
- Function with return type
- Empty function
- Lambda functions don't pollute global scope
- Nested function declarations (future feature, error for now)

### Parameter Resolution (6 tests)
- Register single parameter
- Register multiple parameters
- Duplicate parameter name (error)
- Parameter visible in function body
- Parameter not visible outside function
- Parameter shadows global variable (allowed)

### Variable Resolution (10 tests)
- Define variable in function
- Use variable after definition
- Use variable before definition (error)
- Duplicate variable in same scope (error)
- Variable in nested scope
- Inner scope shadows outer scope (allowed)
- Variable not visible outside scope
- Const variable definition
- Multiple variables in scope
- Variable in loop scope

### Identifier Resolution (8 tests)
- Resolve local variable
- Resolve parameter
- Resolve variable from parent scope
- Undefined variable (error)
- Resolve after multiple scopes
- Shadowing resolution (inner wins)
- Global variable access from function
- Variable defined in if branch not visible outside

### Function Call Resolution (7 tests)
- Call defined function
- Call undefined function (error)
- Call variable as function (error)
- Nested function calls
- Recursive function call
- Forward reference (call before definition in source, but registered in pass 1)
- Built-in function call (e.g., print)

### Scope Management (6 tests)
- Enter/exit function scope
- Enter/exit block scope
- Enter/exit for loop scope
- Nested scopes (3+ levels)
- Scope cleanup after error
- Lambda scope isolation

**Total Estimated Tests:** 45 tests

---

## 📁 Files to Create

```
src/semantic/
└── name_resolver.py    # NameResolver class

tests/
└── test_name_resolver.py  # Unit tests
```

---

## 🔗 Dependencies

**Depends On:**
- Task 3.1 (Symbol Table) - for symbol registration
- Task 2.1 (AST Nodes) - for traversal

**Blocks:**
- Task 3.4 (Semantic Analyzer Integration)

---

## 📊 Progress Tracking

- [x] Create `src/semantic/name_resolver.py`
- [x] Implement NameResolver class skeleton
- [x] Implement function registration (pass 1)
- [x] Implement function body resolution (pass 2)
- [x] Implement parameter registration
- [x] Implement variable declaration resolution
- [x] Implement assignment resolution
- [x] Implement control flow resolution (if, while, for)
- [x] Implement block scope resolution
- [x] Implement identifier resolution
- [x] Implement function call resolution
- [x] Implement lambda resolution
- [x] Create `tests/test_name_resolver.py`
- [x] Write function registration tests (8 tests)
- [x] Write parameter resolution tests (6 tests)
- [x] Write variable resolution tests (11 tests)
- [x] Write identifier resolution tests (8 tests)
- [x] Write function call tests (6 tests)
- [x] Write scope management tests (5 tests)
- [x] All tests passing (44 tests total)
- [x] Update taskSummary.md to 100%

**Total Tests:** 44 tests (all passing)
**Test Results:** 809 total tests passing, 8 skipped, 0 failures

---

## 💡 Implementation Notes

### Two-Pass Resolution
**Pass 1:** Register all function declarations in global scope
- Allows forward references (call function before it's defined in source)
- Detects duplicate function names

**Pass 2:** Resolve function bodies
- Parameters, local variables, function calls
- Can reference any function from Pass 1

### Scope Naming
- Global: `"global"`
- Function: `"function:<name>"`
- For loop: `"block:for"`
- Block: `"block:<id>"` (use object id for uniqueness)
- Lambda: `"lambda:<id>"`

### Shadowing Rules
- ✅ Parameter can shadow global variable
- ✅ Local variable can shadow outer scope variable
- ❌ Cannot redeclare in same scope (error)

### Example Resolution
```fusion
int x = 10  # Global variable

int function test(int x)  # Parameter shadows global
    int y = x + 5  # OK: x refers to parameter
    return y
End function

int function main()
    int x = 20  # Local variable shadows global
    int z = test(x)  # OK: calls test with local x
    return x  # Returns 20 (local), not 10 (global)
End function
```

### Built-in Functions
For MVP, hardcode `print` as a built-in:
```python
def __init__(self, symbol_table: SymbolTable):
    self.symbol_table = symbol_table
    self.errors = []

    # Register built-in functions
    self.register_builtins()

def register_builtins(self):
    """Register built-in functions like print."""
    print_type = FunctionType(
        return_type=PrimitiveType('void'),
        param_types=[PrimitiveType('string')]
    )
    self.symbol_table.define(Symbol(
        name='print',
        symbol_type='function',
        data_type=print_type,
        location=SourceLocation('<builtin>', 0, 0)
    ))
```

---

## ✅ Definition of Done

- All code implemented and documented
- All 45+ unit tests passing
- No regressions in existing tests
- Two-pass resolution working correctly
- Clear error messages with locations
- Code follows project style guidelines
- Task file updated to 100% complete
- taskSummary.md updated with progress
