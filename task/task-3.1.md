# Task 3.1: Symbol Table Infrastructure

**Phase:** 3 - Semantic Analyzer
**Status:** 🟢 Complete
**Actual Effort:** ~3 hours
**Priority:** High (Foundation for all semantic analysis)

---

## 📋 Overview

Build the symbol table infrastructure to track variables, functions, and scopes throughout the program. The symbol table is the foundation for type checking and name resolution.

---

## 🎯 Goals

1. Create Symbol class to represent identifiers (variables, functions)
2. Create SymbolTable class with scope management
3. Implement scope stack for nested scopes
4. Support function parameter tracking
5. Detect duplicate declarations
6. Enable symbol lookup with scope resolution

---

## 📝 Requirements

### 1. Symbol Class

**File:** `src/semantic/symbol.py`

```python
@dataclass
class Symbol:
    """Represents a variable or function in the symbol table."""
    name: str
    symbol_type: str  # 'variable', 'function', 'parameter'
    data_type: TypeNode  # The Fusion type (int, string, etc.)
    location: SourceLocation  # Where it was declared
    is_constant: bool = False
    value: Optional[Any] = None  # For constants
```

**Attributes:**
- `name`: identifier name (e.g., "count", "add")
- `symbol_type`: kind of symbol ('variable', 'function', 'parameter')
- `data_type`: Fusion type from AST (PrimitiveType, FunctionType)
- `location`: source location for error reporting
- `is_constant`: True for `const` declarations
- `value`: compile-time constant value (if known)

---

### 2. Scope Class

**File:** `src/semantic/symbol.py`

```python
class Scope:
    """Represents a single scope (global, function, block)."""
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name  # e.g., "global", "function:add", "block:1"
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> None:
        """Add a symbol to this scope. Raises error if duplicate."""
        if symbol.name in self.symbols:
            raise SemanticError(f"Duplicate declaration: {symbol.name}")
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope only."""
        return self.symbols.get(name)

    def lookup_recursive(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope and parent scopes."""
        symbol = self.lookup(name)
        if symbol:
            return symbol
        if self.parent:
            return self.parent.lookup_recursive(name)
        return None
```

---

### 3. SymbolTable Class

**File:** `src/semantic/symbol_table.py`

```python
class SymbolTable:
    """Manages scopes and symbol resolution."""

    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.scope_stack: List[Scope] = [self.global_scope]

    def enter_scope(self, name: str) -> None:
        """Enter a new nested scope."""
        new_scope = Scope(name, parent=self.current_scope)
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope

    def exit_scope(self) -> None:
        """Exit the current scope, return to parent."""
        if len(self.scope_stack) <= 1:
            raise SemanticError("Cannot exit global scope")
        self.scope_stack.pop()
        self.current_scope = self.scope_stack[-1]

    def define(self, symbol: Symbol) -> None:
        """Define a symbol in the current scope."""
        self.current_scope.define(symbol)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol starting from current scope."""
        return self.current_scope.lookup_recursive(name)

    def is_defined_in_current_scope(self, name: str) -> bool:
        """Check if symbol exists in current scope (not parent)."""
        return self.current_scope.lookup(name) is not None
```

---

### 4. SemanticError Class

**File:** `src/semantic/errors.py`

```python
class SemanticError(Exception):
    """Raised when semantic analysis fails."""
    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        self.message = message
        self.location = location
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.location:
            return f"{self.location}: {self.message}"
        return self.message
```

---

## ✅ Acceptance Criteria

- [ ] Symbol class created with all required fields
- [ ] Scope class supports define/lookup operations
- [ ] SymbolTable manages scope stack correctly
- [ ] SemanticError exception class created
- [ ] Can enter/exit nested scopes
- [ ] Duplicate declarations are detected
- [ ] Symbol lookup works across parent scopes
- [ ] All unit tests pass (40+ tests)

---

## 🧪 Test Cases

### Test Symbol Class (8 tests)
- Create variable symbol
- Create function symbol
- Create parameter symbol
- Create constant symbol
- Symbol with source location
- Symbol equality comparison
- Symbol string representation
- Symbol with value

### Test Scope Class (12 tests)
- Create scope with name
- Define symbol in scope
- Lookup symbol in scope
- Lookup nonexistent symbol returns None
- Duplicate declaration raises error
- Recursive lookup finds parent symbol
- Recursive lookup returns None if not found
- Child scope shadows parent symbol
- Scope hierarchy (grandparent lookup)
- Scope name tracking
- Empty scope
- Multiple symbols in scope

### Test SymbolTable (20+ tests)
- Initialize with global scope
- Enter nested scope
- Exit nested scope
- Cannot exit global scope
- Define symbol in global scope
- Define symbol in nested scope
- Lookup in current scope
- Lookup in parent scope
- Lookup in global scope from nested
- Symbol shadowing (child hides parent)
- Multiple nested scopes
- Scope stack tracking
- is_defined_in_current_scope (true case)
- is_defined_in_current_scope (false case, parent has it)
- Define multiple symbols
- Lookup nonexistent symbol
- Complex nesting (3+ levels)
- Scope names ("function:add", "block:1")
- Enter/exit multiple times
- Current scope tracking

**Total Estimated Tests:** 40 tests

---

## 📁 Files to Create

```
src/semantic/
├── __init__.py
├── symbol.py           # Symbol and Scope classes
├── symbol_table.py     # SymbolTable class
└── errors.py           # SemanticError exception

tests/
└── test_symbol_table.py  # Unit tests
```

---

## 🔗 Dependencies

**Depends On:**
- Task 2.1 (AST Node Definitions) - for TypeNode
- src/utils/source_location.py - for SourceLocation

**Blocks:**
- Task 3.2 (Type Checking)
- Task 3.3 (Name Resolution)

---

## 📊 Progress Tracking

- [x] Create `src/semantic/__init__.py`
- [x] Create `src/semantic/errors.py` with SemanticError
- [x] Create Symbol class in `src/semantic/symbol.py`
- [x] Create Scope class in `src/semantic/symbol.py`
- [x] Create SymbolTable class in `src/semantic/symbol_table.py`
- [x] Create test file `tests/test_symbol_table.py`
- [x] Write Symbol tests (8 tests)
- [x] Write Scope tests (12 tests)
- [x] Write SymbolTable tests (22 tests)
- [x] All tests passing (42/42)
- [x] Update taskSummary.md to 100%

**Final Test Count:** 42 tests (8 Symbol + 12 Scope + 22 SymbolTable)
**All Tests Passing:** ✅ 705 total (663 previous + 42 new)

---

## 💡 Implementation Notes

### Scope Naming Convention
- Global scope: `"global"`
- Function scope: `"function:<name>"` (e.g., "function:add")
- Block scope: `"block:<depth>"` (e.g., "block:1", "block:2")

### Symbol Types
- `'variable'` - Regular variables (`int x = 5`)
- `'parameter'` - Function parameters
- `'function'` - Function declarations
- `'constant'` - `const` declarations

### Shadowing Rules
- Child scopes CAN shadow parent scope symbols
- Same scope CANNOT have duplicate symbols (error)

### Example Usage
```python
# Create symbol table
st = SymbolTable()

# Global function
st.define(Symbol("main", "function", FunctionType(...), loc))

# Enter function scope
st.enter_scope("function:main")

# Define parameters
st.define(Symbol("argc", "parameter", PrimitiveType("int"), loc))

# Define local variable
st.define(Symbol("count", "variable", PrimitiveType("int"), loc))

# Lookup
symbol = st.lookup("count")  # Found in current scope
symbol = st.lookup("main")   # Found in parent (global) scope

# Exit function
st.exit_scope()
```

---

## ✅ Definition of Done

- All code implemented and documented
- All 40+ unit tests passing
- No regressions in existing tests
- Code follows project style guidelines
- Task file updated to 100% complete
- taskSummary.md updated with progress
