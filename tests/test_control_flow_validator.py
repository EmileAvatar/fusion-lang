"""
Unit tests for Control Flow Validator

Tests control flow validation: return paths, unreachable code, break/continue,
and condition type checking.
"""

import pytest
from src.lexer.token import SourceLocation
from src.parser.ast_nodes import *
from src.semantic.control_flow_validator import ControlFlowValidator, SemanticError
from src.semantic.type_checker import TypeChecker
from src.semantic.symbol_table import SymbolTable


# ============================================================================
# Helper Functions
# ============================================================================

def make_location():
    """Create a dummy source location for testing."""
    return SourceLocation(filename="test.fusion", line=1, column=1)


def make_primitive_type(name: str) -> PrimitiveType:
    """Create a primitive type node."""
    return PrimitiveType(location=make_location(), name=name)


def make_function_decl(name: str, return_type_name: str, body: ASTNode) -> FunctionDecl:
    """Create a function declaration node."""
    return FunctionDecl(
        location=make_location(),
        return_type=make_primitive_type(return_type_name),
        name=name,
        parameters=[],
        body=body
    )


def make_program(functions: List[FunctionDecl]) -> ProgramNode:
    """Create a program node."""
    return ProgramNode(
        location=make_location(),
        declarations=functions
    )


# ============================================================================
# Return Path Validation Tests (12 tests)
# ============================================================================

def test_void_function_without_return():
    """Void function without return is OK."""
    body = BlockStmt(location=make_location(), statements=[
        ExpressionStmt(
            location=make_location(),
            expression=LiteralExpr(location=make_location(), value=42, type_hint="int")
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_void_function_with_return():
    """Void function with return is OK."""
    body = BlockStmt(location=make_location(), statements=[
        ReturnStmt(location=make_location(), value=None)
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_non_void_function_with_return():
    """Non-void function with return is OK."""
    body = BlockStmt(location=make_location(), statements=[
        ReturnStmt(
            location=make_location(),
            value=LiteralExpr(location=make_location(), value=42, type_hint="int")
        )
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_non_void_function_without_return():
    """Non-void function without return is ERROR."""
    body = BlockStmt(location=make_location(), statements=[
        ExpressionStmt(
            location=make_location(),
            expression=LiteralExpr(location=make_location(), value=42, type_hint="int")
        )
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 1
    assert "must return" in errors[0].message
    assert "all code paths" in errors[0].message


def test_function_if_else_both_return():
    """Function with if-else where both branches return is OK."""
    body = BlockStmt(location=make_location(), statements=[
        IfStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            then_branch=BlockStmt(location=make_location(), statements=[
                ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int"))
            ]),
            else_branch=BlockStmt(location=make_location(), statements=[
                ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=2, type_hint="int"))
            ])
        )
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_function_if_else_only_then_returns():
    """Function with if-else where only then branch returns is ERROR."""
    body = BlockStmt(location=make_location(), statements=[
        IfStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            then_branch=BlockStmt(location=make_location(), statements=[
                ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int"))
            ]),
            else_branch=BlockStmt(location=make_location(), statements=[
                ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=2, type_hint="int"))
            ])
        )
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 1
    assert "must return" in errors[0].message


def test_function_if_no_else_returns():
    """Function with if (no else) that returns is ERROR (else path doesn't return)."""
    body = BlockStmt(location=make_location(), statements=[
        IfStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            then_branch=BlockStmt(location=make_location(), statements=[
                ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int"))
            ]),
            else_branch=None
        )
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 1
    assert "must return" in errors[0].message


def test_function_multiple_returns():
    """Function with multiple return statements is OK."""
    body = BlockStmt(location=make_location(), statements=[
        ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int")),
        ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=2, type_hint="int"))
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_function_return_in_nested_block():
    """Function with return in nested block is OK."""
    body = BlockStmt(location=make_location(), statements=[
        BlockStmt(location=make_location(), statements=[
            ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int"))
        ])
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_function_while_loop_return():
    """Function with return only in while loop is ERROR (loop might not execute)."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[
                ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int"))
            ])
        )
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 1
    assert "must return" in errors[0].message


def test_lambda_with_return():
    """Lambda function with return is OK."""
    # Lambda as single expression (treated as implicit return)
    body = BlockStmt(location=make_location(), statements=[
        ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int"))
    ])
    func = make_function_decl("lambda", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_early_return_followed_by_unreachable_return():
    """Early return followed by unreachable return generates WARNING."""
    body = BlockStmt(location=make_location(), statements=[
        ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int")),
        ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=2, type_hint="int"))
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0
    assert len(warnings) == 1
    assert "Unreachable code" in warnings[0].message


# ============================================================================
# Unreachable Code Detection Tests (8 tests)
# ============================================================================

def test_code_after_return_warning():
    """Code after return generates WARNING."""
    body = BlockStmt(location=make_location(), statements=[
        ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int")),
        ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=2, type_hint="int"))
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(warnings) == 1
    assert "Unreachable code" in warnings[0].message


def test_code_after_break_warning():
    """Code after break generates WARNING."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[
                BreakStmt(location=make_location()),
                ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=1, type_hint="int"))
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(warnings) == 1
    assert "Unreachable code" in warnings[0].message


def test_code_after_continue_warning():
    """Code after continue generates WARNING."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[
                ContinueStmt(location=make_location()),
                ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=1, type_hint="int"))
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(warnings) == 1
    assert "Unreachable code" in warnings[0].message


def test_return_in_if_branch_code_after_if():
    """Return in if branch, code after if is OK (else branch might execute)."""
    body = BlockStmt(location=make_location(), statements=[
        IfStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            then_branch=BlockStmt(location=make_location(), statements=[
                ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int"))
            ]),
            else_branch=None
        ),
        ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=2, type_hint="int"))
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    # No warning because else branch might execute
    assert len(warnings) == 0


def test_multiple_statements_after_return_warn_first():
    """Multiple statements after return: warn on first only."""
    body = BlockStmt(location=make_location(), statements=[
        ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int")),
        ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=2, type_hint="int")),
        ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=3, type_hint="int"))
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    # Only warn once per block
    assert len(warnings) == 1
    assert "Unreachable code" in warnings[0].message


def test_nested_unreachable_code():
    """Nested unreachable code is detected."""
    body = BlockStmt(location=make_location(), statements=[
        BlockStmt(location=make_location(), statements=[
            ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=1, type_hint="int")),
            ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=2, type_hint="int"))
        ])
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(warnings) == 1
    assert "Unreachable code" in warnings[0].message


def test_return_at_end_of_function():
    """Return at end of function is OK (no warning)."""
    body = BlockStmt(location=make_location(), statements=[
        ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=1, type_hint="int")),
        ReturnStmt(location=make_location(), value=LiteralExpr(location=make_location(), value=2, type_hint="int"))
    ])
    func = make_function_decl("test", "int", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(warnings) == 0


def test_break_at_end_of_loop():
    """Break at end of loop is OK (no warning)."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[
                ExpressionStmt(location=make_location(), expression=LiteralExpr(location=make_location(), value=1, type_hint="int")),
                BreakStmt(location=make_location())
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(warnings) == 0


# ============================================================================
# Break/Continue Validation Tests (8 tests)
# ============================================================================

def test_break_inside_while():
    """Break inside while loop is OK."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[
                BreakStmt(location=make_location())
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_break_inside_for():
    """Break inside for loop is OK."""
    body = BlockStmt(location=make_location(), statements=[
        ForStmt(
            location=make_location(),
            variable="i",
            iterable=LiteralExpr(location=make_location(), value=[1, 2, 3], type_hint="list"),
            body=BlockStmt(location=make_location(), statements=[
                BreakStmt(location=make_location())
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_break_outside_loop():
    """Break outside loop is ERROR."""
    body = BlockStmt(location=make_location(), statements=[
        BreakStmt(location=make_location())
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 1
    assert "Break statement outside loop" in errors[0].message


def test_continue_inside_while():
    """Continue inside while loop is OK."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[
                ContinueStmt(location=make_location())
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_continue_inside_for():
    """Continue inside for loop is OK."""
    body = BlockStmt(location=make_location(), statements=[
        ForStmt(
            location=make_location(),
            variable="i",
            iterable=LiteralExpr(location=make_location(), value=[1, 2, 3], type_hint="list"),
            body=BlockStmt(location=make_location(), statements=[
                ContinueStmt(location=make_location())
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_continue_outside_loop():
    """Continue outside loop is ERROR."""
    body = BlockStmt(location=make_location(), statements=[
        ContinueStmt(location=make_location())
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 1
    assert "Continue statement outside loop" in errors[0].message


def test_nested_loops_with_break():
    """Nested loops with break (breaks inner only)."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[
                WhileStmt(
                    location=make_location(),
                    condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
                    body=BlockStmt(location=make_location(), statements=[
                        BreakStmt(location=make_location())
                    ])
                )
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_break_in_if_inside_loop():
    """Break in if inside loop is OK."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[
                IfStmt(
                    location=make_location(),
                    condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
                    then_branch=BlockStmt(location=make_location(), statements=[
                        BreakStmt(location=make_location())
                    ]),
                    else_branch=None
                )
            ])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    validator = ControlFlowValidator()
    type_checker = TypeChecker(SymbolTable())
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


# ============================================================================
# Condition Type Validation Tests (7 tests)
# ============================================================================

def test_if_with_bool_condition():
    """If with bool condition is OK."""
    body = BlockStmt(location=make_location(), statements=[
        IfStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            then_branch=BlockStmt(location=make_location(), statements=[]),
            else_branch=None
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    # Setup symbol table and type checker
    symbol_table = SymbolTable()
    type_checker = TypeChecker(symbol_table)

    validator = ControlFlowValidator()
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_if_with_int_condition():
    """If with int condition is ERROR."""
    body = BlockStmt(location=make_location(), statements=[
        IfStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=5, type_hint="int"),
            then_branch=BlockStmt(location=make_location(), statements=[]),
            else_branch=None
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    # Setup symbol table and type checker
    symbol_table = SymbolTable()
    type_checker = TypeChecker(symbol_table)

    validator = ControlFlowValidator()
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 1
    assert "If condition must be bool" in errors[0].message
    assert "got int" in errors[0].message


def test_while_with_bool_condition():
    """While with bool condition is OK."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            body=BlockStmt(location=make_location(), statements=[])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    # Setup symbol table and type checker
    symbol_table = SymbolTable()
    type_checker = TypeChecker(symbol_table)

    validator = ControlFlowValidator()
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_while_with_int_condition():
    """While with int condition is ERROR."""
    body = BlockStmt(location=make_location(), statements=[
        WhileStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=5, type_hint="int"),
            body=BlockStmt(location=make_location(), statements=[])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    # Setup symbol table and type checker
    symbol_table = SymbolTable()
    type_checker = TypeChecker(symbol_table)

    validator = ControlFlowValidator()
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 1
    assert "While condition must be bool" in errors[0].message
    assert "got int" in errors[0].message


def test_for_with_bool_condition():
    """For loops in MVP don't have explicit conditions, so this test is skipped."""
    # For-in loops don't have condition expressions in MVP
    pass


def test_for_with_no_condition():
    """For loop with no condition is OK (for-in loops)."""
    body = BlockStmt(location=make_location(), statements=[
        ForStmt(
            location=make_location(),
            variable="i",
            iterable=LiteralExpr(location=make_location(), value=[1, 2, 3], type_hint="list"),
            body=BlockStmt(location=make_location(), statements=[])
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    # Setup symbol table and type checker
    symbol_table = SymbolTable()
    type_checker = TypeChecker(symbol_table)

    validator = ControlFlowValidator()
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


def test_nested_if_conditions():
    """Nested if conditions (all must be bool)."""
    body = BlockStmt(location=make_location(), statements=[
        IfStmt(
            location=make_location(),
            condition=LiteralExpr(location=make_location(), value=True, type_hint="bool"),
            then_branch=BlockStmt(location=make_location(), statements=[
                IfStmt(
                    location=make_location(),
                    condition=LiteralExpr(location=make_location(), value=False, type_hint="bool"),
                    then_branch=BlockStmt(location=make_location(), statements=[]),
                    else_branch=None
                )
            ]),
            else_branch=None
        )
    ])
    func = make_function_decl("test", "void", body)
    program = make_program([func])

    # Setup symbol table and type checker
    symbol_table = SymbolTable()
    type_checker = TypeChecker(symbol_table)

    validator = ControlFlowValidator()
    errors, warnings = validator.validate_program(program, type_checker)

    assert len(errors) == 0


# ============================================================================
# Summary
# ============================================================================

# Total tests: 35
# - Return path validation: 12 tests
# - Unreachable code detection: 8 tests
# - Break/continue validation: 8 tests
# - Condition type validation: 7 tests
