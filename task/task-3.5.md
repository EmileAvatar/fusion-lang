# Task 3.5: Entry Point Validation

**Phase:** 3 - Semantic Analyzer
**Status:** 🟢 Complete
**Actual Effort:** 1.5 hours
**Priority:** Medium (Program structure)

---

## 📋 Overview

Validate program structure: ensure a `main` function exists, has correct signature, and check for other program-level requirements.

---

## 🎯 Goals

1. Create EntryPointValidator class
2. Ensure `main` function exists
3. Validate `main` function signature
4. Detect multiple `main` functions
5. Support flexible `main` signatures (void or int return)
6. Optionally validate no orphaned top-level code (future)

---

## 📝 Requirements

### 1. EntryPointValidator Class

**File:** `src/semantic/entry_point_validator.py`

```python
class EntryPointValidator:
    """Validates program entry point (main function)."""

    def __init__(self):
        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []

    def validate_program(self, program: ProgramNode) -> Tuple[List[SemanticError], List[SemanticError]]:
        """Validate program structure."""
        main_functions = []

        # Find all main functions
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclNode) and decl.name == 'main':
                main_functions.append(decl)

        # Check for missing main
        if len(main_functions) == 0:
            self.errors.append(SemanticError(
                "Program must have a 'main' function",
                SourceLocation('<program>', 1, 1)
            ))
            return self.errors, self.warnings

        # Check for multiple main functions
        if len(main_functions) > 1:
            for func in main_functions[1:]:
                self.errors.append(SemanticError(
                    "Multiple 'main' functions defined",
                    func.location
                ))
            return self.errors, self.warnings

        # Validate main signature
        main_func = main_functions[0]
        self.validate_main_signature(main_func)

        return self.errors, self.warnings
```

---

### 2. Main Function Signature Validation

**File:** `src/semantic/entry_point_validator.py`

```python
def validate_main_signature(self, func: FunctionDeclNode) -> None:
    """Validate main function signature.

    Allowed signatures:
    - void function main()
    - int function main()
    - void function main(string[] args)  (future: command-line args)
    - int function main(string[] args)   (future: command-line args)
    """
    # Check return type (must be void or int)
    if isinstance(func.return_type, PrimitiveType):
        if func.return_type.name not in ['void', 'int']:
            self.errors.append(SemanticError(
                f"main function must return 'void' or 'int', got '{func.return_type.name}'",
                func.location
            ))
    else:
        self.errors.append(SemanticError(
            "main function return type must be 'void' or 'int'",
            func.location
        ))

    # Check parameters (MVP: must be empty)
    if len(func.parameters) > 0:
        self.warnings.append(SemanticError(
            "main function parameters are not supported in MVP (ignored)",
            func.location
        ))
        # Note: This is a warning for now; future versions will support args
```

---

### 3. Additional Validations (Optional/Future)

**File:** `src/semantic/entry_point_validator.py`

```python
def check_top_level_statements(self, program: ProgramNode) -> None:
    """Check for orphaned top-level statements (future feature).

    In MVP, only function declarations are allowed at top level.
    This is already enforced by the parser.
    """
    # This is a placeholder for future validation
    # Parser already only allows FunctionDeclNode at top level
    pass

def validate_import_order(self, program: ProgramNode) -> None:
    """Ensure imports come before declarations (future feature)."""
    # This is a placeholder for Phase 4+ when imports are supported
    pass
```

---

## ✅ Acceptance Criteria

- [x] EntryPointValidator class created
- [x] Missing `main` function detected (error)
- [x] Multiple `main` functions detected (error)
- [x] `main` return type validated (void or int only)
- [x] `main` parameters checked (empty for MVP)
- [x] Clear error messages with locations
- [x] All unit tests pass (19 tests)

---

## 🧪 Test Cases

### Main Function Existence (5 tests)
- Program with main (OK)
- Program without main (error)
- Program with multiple main functions (error)
- Empty program (error, no main)
- Program with only non-main functions (error)

### Main Signature - Return Type (5 tests)
- main returns void (OK)
- main returns int (OK)
- main returns string (error)
- main returns float (error)
- main returns custom type (error, future)

### Main Signature - Parameters (5 tests)
- main with no parameters (OK)
- main with one parameter (warning, MVP doesn't support)
- main with string[] args (warning, future feature)
- main with int parameter (warning)
- main with multiple parameters (warning)

**Total Estimated Tests:** 15 tests

---

## 📁 Files to Create

```
src/semantic/
└── entry_point_validator.py  # EntryPointValidator class

tests/
└── test_entry_point_validator.py  # Unit tests
```

---

## 🔗 Dependencies

**Depends On:**
- Task 2.1 (AST Nodes) - for ProgramNode, FunctionDeclNode
- src/utils/source_location.py - for SourceLocation

**Blocks:**
- Task 3.6 (Semantic Analyzer Integration)

---

## 📊 Progress Tracking

- [x] Create `src/semantic/entry_point_validator.py`
- [x] Implement EntryPointValidator class
- [x] Implement main function detection
- [x] Implement duplicate main detection
- [x] Implement return type validation
- [x] Implement parameter validation
- [x] Create `tests/test_entry_point_validator.py`
- [x] Write main existence tests (5 tests)
- [x] Write return type tests (5 tests)
- [x] Write parameter tests (5 tests)
- [x] Write edge case tests (4 tests)
- [x] All tests passing (19/19 tests)
- [x] Update taskSummary.md to 100%

---

## 💡 Implementation Notes

### Valid Main Signatures (MVP)
```fusion
// Option 1: No return value
void function main()
    print("Hello, World!")
End function

// Option 2: Return exit code
int function main()
    print("Hello, World!")
    return 0
End function
```

### Invalid Main Signatures (MVP)
```fusion
// ERROR: Wrong return type
string function main()
    return "error"
End function

// WARNING: Parameters not supported in MVP
void function main(string[] args)
    print("Hello")
End function
```

### Future Enhancements (Post-MVP)
```fusion
// Future: Command-line arguments
int function main(string[] args)
    for arg in args
        print(arg)
    return 0
End function

// Future: Return type inference
function main()
    print("Auto-inferred void")
```

### Error Message Examples
```
Error: Program must have a 'main' function
  at <program>:1:1

Error: Multiple 'main' functions defined
  at hello.fusion:10:1
  Note: First 'main' defined at hello.fusion:5:1

Error: main function must return 'void' or 'int', got 'string'
  at hello.fusion:5:1

Warning: main function parameters are not supported in MVP (ignored)
  at hello.fusion:5:20
  Note: Parameters will be supported in future versions
```

### Integration with Compiler
```python
# In main semantic analyzer
validator = EntryPointValidator()
errors, warnings = validator.validate_program(ast)

if errors:
    # Print errors and exit
    for error in errors:
        print(error)
    sys.exit(1)

if warnings:
    # Print warnings but continue
    for warning in warnings:
        print(f"Warning: {warning}")
```

---

## ✅ Definition of Done

- All code implemented and documented
- All 15+ unit tests passing
- No regressions in existing tests
- Clear distinction between errors and warnings
- Error messages are user-friendly
- Code follows project style guidelines
- Task file updated to 100% complete
- taskSummary.md updated with progress
