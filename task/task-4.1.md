# Task 4.1: C Code Generator Infrastructure

**Phase:** 4 - Code Generator
**Status:** 🟢 Complete
**Actual Effort:** 1 hour
**Priority:** High (Foundation)

---

## 📋 Overview

Create the foundational infrastructure for the C code generator, including the main CCodeGenerator class, helper utilities for C code formatting, and type mapping from Fusion types to C types.

---

## 🎯 Goals

1. Create CCodeGenerator class with visitor pattern
2. Implement type mapping (Fusion → C)
3. Create C code formatting utilities
4. Setup indentation and code structure helpers
5. Create basic test framework for code generation

---

## 📝 Requirements

### 1. CCodeGenerator Class

**File:** `src/codegen/c_generator.py`

```python
class CCodeGenerator:
    """Generates C code from Fusion AST.

    Uses visitor pattern to traverse the AST and generate equivalent C code.
    Supports MVP features: functions, basic types, expressions, statements.

    Attributes:
        output: List of generated C code lines
        indent_level: Current indentation level
        includes: Set of required C header includes
        generated_functions: List of generated function signatures
    """

    def __init__(self):
        """Initialize code generator."""
        self.output: List[str] = []
        self.indent_level: int = 0
        self.includes: Set[str] = set()
        self.generated_functions: List[str] = []

        # Add standard includes
        self.includes.add('<stdio.h>')   # For printf
        self.includes.add('<stdbool.h>') # For bool type
        self.includes.add('<string.h>')  # For string operations

    def generate(self, program: ProgramNode) -> str:
        """Generate C code from program AST.

        Args:
            program: Root AST node

        Returns:
            Complete C source code as string
        """
        # Clear previous state
        self.output.clear()
        self.generated_functions.clear()

        # Generate includes
        self._generate_includes()

        # Generate forward declarations
        self._generate_forward_declarations(program)

        # Generate all functions
        for decl in program.declarations:
            self.visit(decl)

        # Return complete C code
        return '\n'.join(self.output)

    def visit(self, node: ASTNode) -> str:
        """Visit an AST node and generate C code.

        Args:
            node: AST node to visit

        Returns:
            Generated C code for this node
        """
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> str:
        """Handle unknown node types."""
        raise NotImplementedError(f"No visitor for {type(node).__name__}")
```

### 2. Type Mapping

**File:** `src/codegen/c_generator.py`

```python
def map_type(self, fusion_type: TypeNode) -> str:
    """Map Fusion type to C type.

    Args:
        fusion_type: Fusion type node

    Returns:
        Equivalent C type string
    """
    if isinstance(fusion_type, PrimitiveType):
        type_map = {
            'int': 'int',
            'float': 'float',
            'double': 'double',
            'bool': 'bool',
            'char': 'char',
            'string': 'char*',  # Strings as char pointers
            'void': 'void'
        }
        return type_map.get(fusion_type.name, 'void')

    elif isinstance(fusion_type, FunctionType):
        # Function pointer type
        param_types = ', '.join(self.map_type(p) for p in fusion_type.parameter_types)
        return_type = self.map_type(fusion_type.return_type)
        return f'{return_type} (*)({param_types})'

    return 'void'
```

### 3. Code Formatting Helpers

**File:** `src/codegen/c_generator.py`

```python
def emit(self, code: str = '') -> None:
    """Emit a line of C code with proper indentation.

    Args:
        code: Code to emit (without indentation)
    """
    if code:
        indent = '    ' * self.indent_level
        self.output.append(f'{indent}{code}')
    else:
        self.output.append('')  # Blank line

def emit_line(self, code: str) -> None:
    """Emit a line of C code with semicolon.

    Args:
        code: Code to emit (semicolon added automatically)
    """
    self.emit(f'{code};')

def indent(self) -> None:
    """Increase indentation level."""
    self.indent_level += 1

def dedent(self) -> None:
    """Decrease indentation level."""
    if self.indent_level > 0:
        self.indent_level -= 1

def emit_block_start(self) -> None:
    """Emit opening brace and increase indentation."""
    self.emit('{')
    self.indent()

def emit_block_end(self) -> None:
    """Emit closing brace and decrease indentation."""
    self.dedent()
    self.emit('}')
```

### 4. Header Generation

**File:** `src/codegen/c_generator.py`

```python
def _generate_includes(self) -> None:
    """Generate #include directives."""
    for include in sorted(self.includes):
        self.emit(f'#include {include}')
    self.emit()  # Blank line

def _generate_forward_declarations(self, program: ProgramNode) -> None:
    """Generate forward declarations for all functions.

    Args:
        program: Program AST node
    """
    self.emit('// Forward declarations')
    for decl in program.declarations:
        if isinstance(decl, FunctionDecl):
            return_type = self.map_type(decl.return_type)
            params = ', '.join(
                f'{self.map_type(p.param_type)} {p.name}'
                for p in decl.parameters
            )
            self.emit(f'{return_type} {decl.name}({params});')
    self.emit()  # Blank line
```

---

## ✅ Acceptance Criteria

- [x] CCodeGenerator class created
- [x] Visitor pattern implemented
- [x] Type mapping function works for all MVP types
- [x] Code formatting helpers (emit, indent, dedent) work correctly
- [x] Include generation works
- [x] Forward declarations generated correctly
- [x] Basic test framework created
- [x] Tests pass (25 tests - exceeded goal!)

---

## 🧪 Test Cases

### Type Mapping (8 tests)
- Map int → int
- Map float → float
- Map double → double
- Map bool → bool
- Map char → char
- Map string → char*
- Map void → void
- Map unknown type → void (fallback)

### Code Formatting (7 tests)
- emit() adds proper indentation
- emit_line() adds semicolon
- indent() increases level
- dedent() decreases level
- emit_block_start() adds { and indents
- emit_block_end() dedents and adds }
- Multiple indent levels work correctly

### Header Generation (5 tests)
- Includes generated in sorted order
- Standard includes present (stdio.h, stdbool.h, string.h)
- Forward declarations for single function
- Forward declarations for multiple functions
- Forward declarations with parameters

**Total Estimated Tests:** 20 tests

---

## 📁 Files to Create/Update

```
src/codegen/
├── __init__.py             # Package exports
└── c_generator.py          # CCodeGenerator class

tests/
└── test_codegen_infrastructure.py  # Infrastructure tests
```

---

## 🔗 Dependencies

**Depends On:**
- Phase 3 (Semantic Analyzer) - Complete ✅

**Blocks:**
- Task 4.2 (Expression Code Generation)
- Task 4.3 (Statement Code Generation)
- Task 4.4 (Function Code Generation)

---

## 📊 Progress Tracking

- [x] Create `src/codegen/__init__.py`
- [x] Create `src/codegen/c_generator.py`
- [x] Implement CCodeGenerator class
- [x] Implement type mapping function
- [x] Implement code formatting helpers
- [x] Implement include generation
- [x] Implement forward declaration generation
- [x] Create `tests/test_codegen_infrastructure.py`
- [x] Write type mapping tests (8 tests)
- [x] Write code formatting tests (7 tests)
- [x] Write header generation tests (5 tests)
- [x] Write additional tests (5 tests)
- [x] All tests passing (25/25)
- [x] Update taskSummary.md to reflect progress

---

## 💡 Implementation Notes

### C Type Mapping Strategy

**Fusion Type → C Type:**
- `int` → `int` (32-bit signed integer)
- `float` → `float` (32-bit floating point)
- `double` → `double` (64-bit floating point)
- `bool` → `bool` (requires stdbool.h)
- `char` → `char` (8-bit character)
- `string` → `char*` (null-terminated string)
- `void` → `void`

**String Handling:**
- Fusion strings map to C `char*`
- String literals generate C string literals
- String interpolation requires sprintf/snprintf
- Memory management deferred (no malloc/free in MVP)

### Code Structure

```c
// Generated C code structure:
#include <stdio.h>
#include <stdbool.h>
#include <string.h>

// Forward declarations
int add(int a, int b);
void main();

// Function definitions
int add(int a, int b) {
    return a + b;
}

void main() {
    int result = add(5, 3);
    printf("%d\n", result);
}
```

### Indentation

- Use 4 spaces per indent level
- Never mix tabs and spaces
- Blank lines between functions
- Blank line after includes
- Blank line after forward declarations

---

## ✅ Definition of Done

- All code implemented and documented
- All 20 infrastructure tests passing
- Type mapping works for all MVP types
- Code formatting produces valid C syntax
- Includes and forward declarations generated correctly
- Code follows project style guidelines
- Task file updated to 100% complete
- taskSummary.md updated with progress
