"""
Unit tests for Entry Point Validator

Tests main function validation: existence, signature, and duplicate detection.
"""

import pytest
from src.lexer.token import SourceLocation
from src.parser.ast_nodes import *
from src.semantic.entry_point_validator import EntryPointValidator, SemanticError


# ============================================================================
# Helper Functions
# ============================================================================

def make_location():
    """Create a dummy source location for testing."""
    return SourceLocation(filename="test.fusion", line=1, column=1)


def make_primitive_type(name: str) -> PrimitiveType:
    """Create a primitive type node."""
    return PrimitiveType(location=make_location(), name=name)


def make_function_decl(name: str, return_type_name: str, params: List[ParameterDecl] = None) -> FunctionDecl:
    """Create a function declaration node."""
    return FunctionDecl(
        location=make_location(),
        return_type=make_primitive_type(return_type_name),
        name=name,
        parameters=params if params is not None else [],
        body=BlockStmt(location=make_location(), statements=[])
    )


def make_parameter(param_type_name: str, name: str) -> ParameterDecl:
    """Create a parameter declaration node."""
    return ParameterDecl(
        location=make_location(),
        param_type=make_primitive_type(param_type_name),
        name=name,
        default_value=None
    )


def make_program(functions: List[FunctionDecl]) -> ProgramNode:
    """Create a program node."""
    return ProgramNode(
        location=make_location(),
        declarations=functions
    )


# ============================================================================
# Main Function Existence Tests (5 tests)
# ============================================================================

def test_program_with_main():
    """Program with main function is OK."""
    main_func = make_function_decl("main", "void")
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0
    assert len(warnings) == 0


def test_program_without_main():
    """Program without main function is ERROR."""
    other_func = make_function_decl("foo", "void")
    program = make_program([other_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 1
    assert "must have a 'main' function" in errors[0].message


def test_program_with_multiple_main_functions():
    """Program with multiple main functions is ERROR."""
    main_func1 = make_function_decl("main", "void")
    main_func2 = make_function_decl("main", "int")
    program = make_program([main_func1, main_func2])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 1
    assert "Multiple 'main' functions" in errors[0].message


def test_empty_program():
    """Empty program (no functions) is ERROR."""
    program = make_program([])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 1
    assert "must have a 'main' function" in errors[0].message


def test_program_with_only_non_main_functions():
    """Program with only non-main functions is ERROR."""
    func1 = make_function_decl("foo", "void")
    func2 = make_function_decl("bar", "int")
    func3 = make_function_decl("baz", "string")
    program = make_program([func1, func2, func3])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 1
    assert "must have a 'main' function" in errors[0].message


# ============================================================================
# Main Signature - Return Type Tests (5 tests)
# ============================================================================

def test_main_returns_void():
    """main returning void is OK."""
    main_func = make_function_decl("main", "void")
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0


def test_main_returns_int():
    """main returning int is OK."""
    main_func = make_function_decl("main", "int")
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0


def test_main_returns_string():
    """main returning string is ERROR."""
    main_func = make_function_decl("main", "string")
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 1
    assert "must return 'void' or 'int'" in errors[0].message
    assert "got 'string'" in errors[0].message


def test_main_returns_float():
    """main returning float is ERROR."""
    main_func = make_function_decl("main", "float")
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 1
    assert "must return 'void' or 'int'" in errors[0].message
    assert "got 'float'" in errors[0].message


def test_main_returns_bool():
    """main returning bool is ERROR."""
    main_func = make_function_decl("main", "bool")
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 1
    assert "must return 'void' or 'int'" in errors[0].message
    assert "got 'bool'" in errors[0].message


# ============================================================================
# Main Signature - Parameters Tests (5 tests)
# ============================================================================

def test_main_with_no_parameters():
    """main with no parameters is OK."""
    main_func = make_function_decl("main", "void", [])
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0
    assert len(warnings) == 0


def test_main_with_one_parameter():
    """main with one parameter is WARNING (MVP doesn't support)."""
    param = make_parameter("int", "argc")
    main_func = make_function_decl("main", "void", [param])
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0
    assert len(warnings) == 1
    assert "parameters are not supported in MVP" in warnings[0].message


def test_main_with_string_array_parameter():
    """main with string[] args is WARNING (future feature)."""
    # Note: In MVP, we don't have array types, so we just use string as placeholder
    param = make_parameter("string", "args")
    main_func = make_function_decl("main", "void", [param])
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0
    assert len(warnings) == 1
    assert "parameters are not supported in MVP" in warnings[0].message


def test_main_with_int_parameter():
    """main with int parameter is WARNING."""
    param = make_parameter("int", "value")
    main_func = make_function_decl("main", "int", [param])
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0
    assert len(warnings) == 1
    assert "parameters are not supported in MVP" in warnings[0].message


def test_main_with_multiple_parameters():
    """main with multiple parameters is WARNING."""
    param1 = make_parameter("int", "argc")
    param2 = make_parameter("string", "argv")
    main_func = make_function_decl("main", "void", [param1, param2])
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0
    assert len(warnings) == 1
    assert "parameters are not supported in MVP" in warnings[0].message


# ============================================================================
# Combined Tests (Edge Cases)
# ============================================================================

def test_main_with_wrong_return_type_and_parameters():
    """main with wrong return type AND parameters has both error and warning."""
    param = make_parameter("int", "x")
    main_func = make_function_decl("main", "string", [param])
    program = make_program([main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    # Should have 1 error (wrong return type) and 1 warning (has parameters)
    assert len(errors) == 1
    assert "must return 'void' or 'int'" in errors[0].message
    assert len(warnings) == 1
    assert "parameters are not supported in MVP" in warnings[0].message


def test_multiple_main_stops_signature_validation():
    """Multiple main functions detected stops further validation."""
    main_func1 = make_function_decl("main", "string")  # Wrong return type
    main_func2 = make_function_decl("main", "float")   # Also wrong
    program = make_program([main_func1, main_func2])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    # Should only report duplicate main, not signature errors
    assert len(errors) == 1
    assert "Multiple 'main' functions" in errors[0].message


def test_program_with_main_and_other_functions():
    """Program with main and other functions is OK."""
    main_func = make_function_decl("main", "void")
    helper_func = make_function_decl("helper", "int")
    program = make_program([helper_func, main_func])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    assert len(errors) == 0
    assert len(warnings) == 0


def test_case_sensitive_main():
    """main is case-sensitive (Main is not main)."""
    func_Main = make_function_decl("Main", "void")
    func_MAIN = make_function_decl("MAIN", "void")
    program = make_program([func_Main, func_MAIN])

    validator = EntryPointValidator()
    errors, warnings = validator.validate_program(program)

    # Neither "Main" nor "MAIN" is "main"
    assert len(errors) == 1
    assert "must have a 'main' function" in errors[0].message


# ============================================================================
# Summary
# ============================================================================

# Total tests: 18
# - Main existence: 5 tests
# - Return type: 5 tests
# - Parameters: 5 tests
# - Edge cases: 3 tests
