"""Tests for the type checker."""

import pytest
from src.semantic.type_checker import TypeChecker
from src.semantic.symbol_table import SymbolTable
from src.semantic.symbol import Symbol
from src.semantic.errors import SemanticError
from src.parser.ast_nodes import (
    ProgramNode, FunctionDecl, ParameterDecl,
    VarDeclStmt, AssignmentStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    ExpressionStmt, BlockStmt,
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr, CallExpr, LambdaExpr,
    InterpolatedStringExpr,
    PrimitiveType, FunctionType
)
from src.lexer.token import SourceLocation


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def symbol_table():
    """Create an empty symbol table."""
    return SymbolTable()


@pytest.fixture
def type_checker(symbol_table):
    """Create a type checker with symbol table."""
    return TypeChecker(symbol_table)


@pytest.fixture
def location():
    """Create a dummy source location."""
    return SourceLocation("test.fusion", 1, 1)


# ============================================================================
# Type Compatibility Tests (10 tests)
# ============================================================================

def test_exact_type_match_int(type_checker, location):
    """Test exact type match for int."""
    int_type = PrimitiveType(location=location, name='int')
    assert type_checker.types_equal(int_type, int_type)
    assert type_checker.types_compatible(int_type, int_type)


def test_type_mismatch_int_string(type_checker, location):
    """Test type mismatch between int and string."""
    int_type = PrimitiveType(location=location, name='int')
    string_type = PrimitiveType(location=location, name='string')
    assert not type_checker.types_equal(int_type, string_type)
    assert not type_checker.types_compatible(int_type, string_type)


def test_numeric_promotion_int_to_float(type_checker, location):
    """Test int can be promoted to float."""
    int_type = PrimitiveType(location=location, name='int')
    float_type = PrimitiveType(location=location, name='float')
    assert type_checker.is_numeric_promotion(float_type, int_type)
    assert type_checker.types_compatible(float_type, int_type)


def test_numeric_promotion_float_to_double(type_checker, location):
    """Test float can be promoted to double."""
    float_type = PrimitiveType(location=location, name='float')
    double_type = PrimitiveType(location=location, name='double')
    assert type_checker.is_numeric_promotion(double_type, float_type)
    assert type_checker.types_compatible(double_type, float_type)


def test_numeric_promotion_int_to_double(type_checker, location):
    """Test int can be promoted to double."""
    int_type = PrimitiveType(location=location, name='int')
    double_type = PrimitiveType(location=location, name='double')
    assert type_checker.is_numeric_promotion(double_type, int_type)
    assert type_checker.types_compatible(double_type, int_type)


def test_no_promotion_backwards_float_to_int(type_checker, location):
    """Test float cannot be promoted to int."""
    int_type = PrimitiveType(location=location, name='int')
    float_type = PrimitiveType(location=location, name='float')
    assert not type_checker.is_numeric_promotion(int_type, float_type)
    assert not type_checker.types_compatible(int_type, float_type)


def test_bool_types_equal(type_checker, location):
    """Test bool types are equal."""
    bool_type1 = PrimitiveType(location=location, name='bool')
    bool_type2 = PrimitiveType(location=location, name='bool')
    assert type_checker.types_equal(bool_type1, bool_type2)


def test_string_types_equal(type_checker, location):
    """Test string types are equal."""
    string_type1 = PrimitiveType(location=location, name='string')
    string_type2 = PrimitiveType(location=location, name='string')
    assert type_checker.types_equal(string_type1, string_type2)


def test_void_types_equal(type_checker, location):
    """Test void types are equal."""
    void_type1 = PrimitiveType(location=location, name='void')
    void_type2 = PrimitiveType(location=location, name='void')
    assert type_checker.types_equal(void_type1, void_type2)


def test_incompatible_types(type_checker, location):
    """Test incompatible types."""
    bool_type = PrimitiveType(location=location, name='bool')
    string_type = PrimitiveType(location=location, name='string')
    assert not type_checker.types_compatible(bool_type, string_type)


# ============================================================================
# Expression Type Inference Tests (12 tests)
# ============================================================================

def test_literal_int_type(type_checker, location):
    """Test literal int type inference."""
    lit = LiteralExpr(value=42, type_hint='int', location=location)
    result_type = type_checker.visit_LiteralExpr(lit)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'int'


def test_literal_float_type(type_checker, location):
    """Test literal float type inference."""
    lit = LiteralExpr(value=3.14, type_hint='float', location=location)
    result_type = type_checker.visit_LiteralExpr(lit)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'float'


def test_literal_string_type(type_checker, location):
    """Test literal string type inference."""
    lit = LiteralExpr(value="hello", type_hint='string', location=location)
    result_type = type_checker.visit_LiteralExpr(lit)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'string'


def test_literal_bool_type(type_checker, location):
    """Test literal bool type inference."""
    lit = LiteralExpr(value=True, type_hint='bool', location=location)
    result_type = type_checker.visit_LiteralExpr(lit)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'bool'


def test_identifier_type_lookup(type_checker, symbol_table, location):
    """Test identifier type lookup from symbol table."""
    # Define variable in symbol table
    int_type = PrimitiveType(location=location, name='int')
    symbol = Symbol('x', 'variable', int_type, location)
    symbol_table.define(symbol)

    # Look up identifier
    ident = IdentifierExpr(name='x', location=location)
    result_type = type_checker.visit_IdentifierExpr(ident)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'int'


def test_binary_arithmetic_int_int(type_checker, location):
    """Test binary arithmetic with int + int = int."""
    left = LiteralExpr(value=5, type_hint='int', location=location)
    right = LiteralExpr(value=3, type_hint='int', location=location)
    binary = BinaryExpr(left=left, operator='+', right=right, location=location)
    result_type = type_checker.visit_BinaryExpr(binary)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'int'


def test_binary_arithmetic_int_float(type_checker, location):
    """Test binary arithmetic with int + float = float."""
    left = LiteralExpr(value=5, type_hint='int', location=location)
    right = LiteralExpr(value=3.14, type_hint='float', location=location)
    binary = BinaryExpr(left=left, operator='+', right=right, location=location)
    result_type = type_checker.visit_BinaryExpr(binary)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'float'


def test_binary_comparison_int_int_bool(type_checker, location):
    """Test binary comparison with int < int = bool."""
    left = LiteralExpr(value=5, type_hint='int', location=location)
    right = LiteralExpr(value=10, type_hint='int', location=location)
    binary = BinaryExpr(left=left, operator='<', right=right, location=location)
    result_type = type_checker.visit_BinaryExpr(binary)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'bool'


def test_binary_logical_bool_bool_bool(type_checker, location):
    """Test binary logical with bool and bool = bool."""
    left = LiteralExpr(value=True, type_hint='bool', location=location)
    right = LiteralExpr(value=False, type_hint='bool', location=location)
    binary = BinaryExpr(left=left, operator='and', right=right, location=location)
    result_type = type_checker.visit_BinaryExpr(binary)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'bool'


def test_unary_minus_int(type_checker, location):
    """Test unary minus on int."""
    operand = LiteralExpr(value=5, type_hint='int', location=location)
    unary = UnaryExpr(operator='-', operand=operand, location=location)
    result_type = type_checker.visit_UnaryExpr(unary)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'int'


def test_unary_not_bool(type_checker, location):
    """Test unary not on bool."""
    operand = LiteralExpr(value=True, type_hint='bool', location=location)
    unary = UnaryExpr(operator='not', operand=operand, location=location)
    result_type = type_checker.visit_UnaryExpr(unary)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'bool'


def test_nested_expressions(type_checker, location):
    """Test nested expressions."""
    # (5 + 3) * 2
    inner_left = LiteralExpr(value=5, type_hint='int', location=location)
    inner_right = LiteralExpr(value=3, type_hint='int', location=location)
    inner = BinaryExpr(left=inner_left, operator='+', right=inner_right, location=location)
    outer_right = LiteralExpr(value=2, type_hint='int', location=location)
    outer = BinaryExpr(left=inner, operator='*', right=outer_right, location=location)
    result_type = type_checker.visit_BinaryExpr(outer)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'int'


# ============================================================================
# Type Error Tests (15 tests)
# ============================================================================

def test_undefined_variable_error(type_checker, location):
    """Test error for undefined variable."""
    ident = IdentifierExpr(name='undefined', location=location)
    type_checker.visit_IdentifierExpr(ident)
    assert len(type_checker.errors) == 1
    assert "Undefined variable" in type_checker.errors[0].message


def test_arithmetic_on_string_error(type_checker, location):
    """Test error for arithmetic on string."""
    left = LiteralExpr(value="hello", type_hint='string', location=location)
    right = LiteralExpr(value=5, type_hint='int', location=location)
    binary = BinaryExpr(left=left, operator='+', right=right, location=location)
    type_checker.visit_BinaryExpr(binary)
    assert len(type_checker.errors) == 1
    assert "must be numeric" in type_checker.errors[0].message


def test_comparison_ordering_string_error(type_checker, location):
    """Test error for ordering comparison with string."""
    left = LiteralExpr(value="hello", type_hint='string', location=location)
    right = LiteralExpr(value="world", type_hint='string', location=location)
    binary = BinaryExpr(left=left, operator='<', right=right, location=location)
    type_checker.visit_BinaryExpr(binary)
    assert len(type_checker.errors) == 2  # Both operands must be numeric


def test_logical_and_on_int_error(type_checker, location):
    """Test error for logical and on int."""
    left = LiteralExpr(value=5, type_hint='int', location=location)
    right = LiteralExpr(value=10, type_hint='int', location=location)
    binary = BinaryExpr(left=left, operator='and', right=right, location=location)
    type_checker.visit_BinaryExpr(binary)
    assert len(type_checker.errors) == 2  # Both operands must be bool


def test_unary_minus_on_bool_error(type_checker, location):
    """Test error for unary minus on bool."""
    operand = LiteralExpr(value=True, type_hint='bool', location=location)
    unary = UnaryExpr(operator='-', operand=operand, location=location)
    type_checker.visit_UnaryExpr(unary)
    assert len(type_checker.errors) == 1
    assert "numeric type" in type_checker.errors[0].message


def test_unary_not_on_int_error(type_checker, location):
    """Test error for unary not on int."""
    operand = LiteralExpr(value=5, type_hint='int', location=location)
    unary = UnaryExpr(operator='not', operand=operand, location=location)
    type_checker.visit_UnaryExpr(unary)
    assert len(type_checker.errors) == 1
    assert "bool type" in type_checker.errors[0].message


def test_assignment_type_mismatch_error(type_checker, symbol_table, location):
    """Test error for assignment type mismatch."""
    # Define int variable
    int_type = PrimitiveType(location=location, name='int')
    symbol = Symbol('x', 'variable', int_type, location)
    symbol_table.define(symbol)

    # Try to assign string to int
    target = IdentifierExpr(name='x', location=location)
    value = LiteralExpr(value="hello", type_hint='string', location=location)
    assignment = AssignmentStmt(target=target, value=value, location=location)
    type_checker.visit_AssignmentStmt(assignment)
    assert len(type_checker.errors) == 1
    assert "Cannot assign" in type_checker.errors[0].message


def test_var_decl_type_mismatch_error(type_checker, location):
    """Test error for variable declaration type mismatch."""
    int_type = PrimitiveType(location=location, name='int')
    initializer = LiteralExpr(value="hello", type_hint='string', location=location)
    var_decl = VarDeclStmt(var_type=int_type, name='x', initializer=initializer, location=location)
    type_checker.visit_VarDeclStmt(var_decl)
    assert len(type_checker.errors) == 1
    assert "Cannot assign" in type_checker.errors[0].message


def test_return_type_mismatch_error(type_checker, location):
    """Test error for return type mismatch."""
    # Set current function return type to int
    type_checker.current_function_return_type = PrimitiveType(location=location, name='int')

    # Try to return string
    value = LiteralExpr(value="hello", type_hint='string', location=location)
    return_stmt = ReturnStmt(value=value, location=location)
    type_checker.visit_ReturnStmt(return_stmt)
    assert len(type_checker.errors) == 1
    assert "does not match function return type" in type_checker.errors[0].message


def test_function_call_wrong_arg_count_too_few(type_checker, symbol_table, location):
    """Test error for function call with too few arguments."""
    # Define function with 2 parameters
    int_type = PrimitiveType(location=location, name='int')
    func_type = FunctionType(
        parameter_types=[int_type, int_type],
        return_type=int_type,
        location=location
    )
    symbol = Symbol('add', 'function', func_type, location)
    symbol_table.define(symbol)

    # Call with 1 argument
    callee = IdentifierExpr(name='add', location=location)
    arg = LiteralExpr(value=5, type_hint='int', location=location)
    call = CallExpr(callee=callee, arguments=[arg], location=location)
    type_checker.visit_CallExpr(call)
    assert len(type_checker.errors) == 1
    assert "expects 2 argument" in type_checker.errors[0].message


def test_function_call_wrong_arg_count_too_many(type_checker, symbol_table, location):
    """Test error for function call with too many arguments."""
    # Define function with 1 parameter
    int_type = PrimitiveType(location=location, name='int')
    func_type = FunctionType(
        parameter_types=[int_type],
        return_type=int_type,
        location=location
    )
    symbol = Symbol('square', 'function', func_type, location)
    symbol_table.define(symbol)

    # Call with 2 arguments
    callee = IdentifierExpr(name='square', location=location)
    arg1 = LiteralExpr(value=5, type_hint='int', location=location)
    arg2 = LiteralExpr(value=3, type_hint='int', location=location)
    call = CallExpr(callee=callee, arguments=[arg1, arg2], location=location)
    type_checker.visit_CallExpr(call)
    assert len(type_checker.errors) == 1
    assert "expects 1 argument" in type_checker.errors[0].message


def test_function_call_wrong_arg_type(type_checker, symbol_table, location):
    """Test error for function call with wrong argument type."""
    # Define function with int parameter
    int_type = PrimitiveType(location=location, name='int')
    func_type = FunctionType(
        parameter_types=[int_type],
        return_type=int_type,
        location=location
    )
    symbol = Symbol('square', 'function', func_type, location)
    symbol_table.define(symbol)

    # Call with string argument
    callee = IdentifierExpr(name='square', location=location)
    arg = LiteralExpr(value="hello", type_hint='string', location=location)
    call = CallExpr(callee=callee, arguments=[arg], location=location)
    type_checker.visit_CallExpr(call)
    assert len(type_checker.errors) == 1
    assert "expected int, got string" in type_checker.errors[0].message


def test_assign_to_constant_error(type_checker, symbol_table, location):
    """Test error for assigning to constant."""
    # Define constant
    int_type = PrimitiveType(location=location, name='int')
    symbol = Symbol('PI', 'constant', int_type, location, is_constant=True)
    symbol_table.define(symbol)

    # Try to assign
    target = IdentifierExpr(name='PI', location=location)
    value = LiteralExpr(value=5, type_hint='int', location=location)
    assignment = AssignmentStmt(target=target, value=value, location=location)
    type_checker.visit_AssignmentStmt(assignment)
    assert len(type_checker.errors) == 1
    assert "Cannot assign to constant" in type_checker.errors[0].message


def test_return_outside_function_error(type_checker, location):
    """Test error for return outside function."""
    value = LiteralExpr(value=5, type_hint='int', location=location)
    return_stmt = ReturnStmt(value=value, location=location)
    type_checker.visit_ReturnStmt(return_stmt)
    assert len(type_checker.errors) == 1
    assert "outside function" in type_checker.errors[0].message


def test_call_non_function_error(type_checker, symbol_table, location):
    """Test error for calling non-function."""
    # Define variable (not function)
    int_type = PrimitiveType(location=location, name='int')
    symbol = Symbol('x', 'variable', int_type, location)
    symbol_table.define(symbol)

    # Try to call it
    callee = IdentifierExpr(name='x', location=location)
    call = CallExpr(callee=callee, arguments=[], location=location)
    type_checker.visit_CallExpr(call)
    assert len(type_checker.errors) == 1
    assert "is not a function" in type_checker.errors[0].message


# ============================================================================
# Control Flow Type Checking Tests (8 tests)
# ============================================================================

def test_if_condition_must_be_bool(type_checker, location):
    """Test if condition must be bool."""
    # Test with int condition (should error)
    condition = LiteralExpr(value=5, type_hint='int', location=location)
    then_branch = BlockStmt(statements=[], location=location)
    if_stmt = IfStmt(condition=condition, then_branch=then_branch, else_branch=None, location=location)
    type_checker.visit_IfStmt(if_stmt)
    assert len(type_checker.errors) == 1
    assert "must be bool" in type_checker.errors[0].message


def test_while_condition_must_be_bool(type_checker, location):
    """Test while condition must be bool."""
    # Test with string condition (should error)
    condition = LiteralExpr(value="hello", type_hint='string', location=location)
    body = BlockStmt(statements=[], location=location)
    while_stmt = WhileStmt(condition=condition, body=body, location=location)
    type_checker.visit_WhileStmt(while_stmt)
    assert len(type_checker.errors) == 1
    assert "must be bool" in type_checker.errors[0].message


def test_for_statement_basic(type_checker, location):
    """Test for statement basic type checking."""
    # For now, just check it doesn't crash
    iterable = LiteralExpr(value=10, type_hint='int', location=location)
    body = BlockStmt(statements=[], location=location)
    for_stmt = ForStmt(variable='i', iterable=iterable, body=body, location=location)
    type_checker.visit_ForStmt(for_stmt)
    # Should not error for now


def test_return_with_value_in_void_function_error(type_checker, location):
    """Test error for return with value in void function."""
    type_checker.current_function_return_type = PrimitiveType(location=location, name='void')
    value = LiteralExpr(value=5, type_hint='int', location=location)
    return_stmt = ReturnStmt(value=value, location=location)
    type_checker.visit_ReturnStmt(return_stmt)
    assert len(type_checker.errors) == 1
    assert "does not match function return type" in type_checker.errors[0].message


def test_return_without_value_in_non_void_function_error(type_checker, location):
    """Test error for return without value in non-void function."""
    type_checker.current_function_return_type = PrimitiveType(location=location, name='int')
    return_stmt = ReturnStmt(value=None, location=location)
    type_checker.visit_ReturnStmt(return_stmt)
    assert len(type_checker.errors) == 1
    assert "must return" in type_checker.errors[0].message


def test_return_correct_type(type_checker, location):
    """Test return with correct type."""
    type_checker.current_function_return_type = PrimitiveType(location=location, name='int')
    value = LiteralExpr(value=5, type_hint='int', location=location)
    return_stmt = ReturnStmt(value=value, location=location)
    type_checker.visit_ReturnStmt(return_stmt)
    assert len(type_checker.errors) == 0


def test_multiple_returns_same_type(type_checker, location):
    """Test multiple returns with same type."""
    type_checker.current_function_return_type = PrimitiveType(location=location, name='int')

    # First return
    value1 = LiteralExpr(value=5, type_hint='int', location=location)
    return_stmt1 = ReturnStmt(value=value1, location=location)
    type_checker.visit_ReturnStmt(return_stmt1)

    # Second return
    value2 = LiteralExpr(value=10, type_hint='int', location=location)
    return_stmt2 = ReturnStmt(value=value2, location=location)
    type_checker.visit_ReturnStmt(return_stmt2)

    assert len(type_checker.errors) == 0


def test_if_condition_with_bool(type_checker, location):
    """Test if condition with bool (should pass)."""
    condition = LiteralExpr(value=True, type_hint='bool', location=location)
    then_branch = BlockStmt(statements=[], location=location)
    if_stmt = IfStmt(condition=condition, then_branch=then_branch, else_branch=None, location=location)
    type_checker.visit_IfStmt(if_stmt)
    assert len(type_checker.errors) == 0


# ============================================================================
# Function Call Type Checking Tests (8 tests)
# ============================================================================

def test_call_with_correct_args(type_checker, symbol_table, location):
    """Test function call with correct arguments."""
    # Define function
    int_type = PrimitiveType(location=location, name='int')
    func_type = FunctionType(
        parameter_types=[int_type, int_type],
        return_type=int_type,
        location=location
    )
    symbol = Symbol('add', 'function', func_type, location)
    symbol_table.define(symbol)

    # Call with correct arguments
    callee = IdentifierExpr(name='add', location=location)
    arg1 = LiteralExpr(value=5, type_hint='int', location=location)
    arg2 = LiteralExpr(value=3, type_hint='int', location=location)
    call = CallExpr(callee=callee, arguments=[arg1, arg2], location=location)
    result_type = type_checker.visit_CallExpr(call)

    assert len(type_checker.errors) == 0
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'int'


def test_call_returns_correct_type(type_checker, symbol_table, location):
    """Test function call returns correct type."""
    # Define function returning string
    int_type = PrimitiveType(location=location, name='int')
    string_type = PrimitiveType(location=location, name='string')
    func_type = FunctionType(
        parameter_types=[int_type],
        return_type=string_type,
        location=location
    )
    symbol = Symbol('to_string', 'function', func_type, location)
    symbol_table.define(symbol)

    # Call function
    callee = IdentifierExpr(name='to_string', location=location)
    arg = LiteralExpr(value=5, type_hint='int', location=location)
    call = CallExpr(callee=callee, arguments=[arg], location=location)
    result_type = type_checker.visit_CallExpr(call)

    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'string'


def test_call_with_numeric_promotion(type_checker, symbol_table, location):
    """Test function call with numeric promotion (int arg to float param)."""
    # Define function with float parameter
    int_type = PrimitiveType(location=location, name='int')
    float_type = PrimitiveType(location=location, name='float')
    func_type = FunctionType(
        parameter_types=[float_type],
        return_type=float_type,
        location=location
    )
    symbol = Symbol('sqrt', 'function', func_type, location)
    symbol_table.define(symbol)

    # Call with int argument (should be promoted to float)
    callee = IdentifierExpr(name='sqrt', location=location)
    arg = LiteralExpr(value=4, type_hint='int', location=location)
    call = CallExpr(callee=callee, arguments=[arg], location=location)
    type_checker.visit_CallExpr(call)

    assert len(type_checker.errors) == 0


def test_nested_function_calls(type_checker, symbol_table, location):
    """Test nested function calls."""
    # Define functions
    int_type = PrimitiveType(location=location, name='int')
    func1_type = FunctionType(parameter_types=[int_type], return_type=int_type, location=location)
    func2_type = FunctionType(parameter_types=[int_type], return_type=int_type, location=location)

    symbol1 = Symbol('double', 'function', func1_type, location)
    symbol2 = Symbol('square', 'function', func2_type, location)
    symbol_table.define(symbol1)
    symbol_table.define(symbol2)

    # Create nested call: square(double(5))
    arg = LiteralExpr(value=5, type_hint='int', location=location)
    inner_callee = IdentifierExpr(name='double', location=location)
    inner_call = CallExpr(callee=inner_callee, arguments=[arg], location=location)
    outer_callee = IdentifierExpr(name='square', location=location)
    outer_call = CallExpr(callee=outer_callee, arguments=[inner_call], location=location)

    result_type = type_checker.visit_CallExpr(outer_call)
    assert len(type_checker.errors) == 0
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'int'


def test_undefined_function_call(type_checker, location):
    """Test error for undefined function call."""
    callee = IdentifierExpr(name='undefined_func', location=location)
    call = CallExpr(callee=callee, arguments=[], location=location)
    type_checker.visit_CallExpr(call)
    assert len(type_checker.errors) == 1
    assert "Undefined function" in type_checker.errors[0].message


def test_call_with_no_args(type_checker, symbol_table, location):
    """Test function call with no arguments."""
    # Define function with no parameters
    int_type = PrimitiveType(location=location, name='int')
    func_type = FunctionType(parameter_types=[], return_type=int_type, location=location)
    symbol = Symbol('get_value', 'function', func_type, location)
    symbol_table.define(symbol)

    # Call with no arguments
    callee = IdentifierExpr(name='get_value', location=location)
    call = CallExpr(callee=callee, arguments=[], location=location)
    result_type = type_checker.visit_CallExpr(call)

    assert len(type_checker.errors) == 0
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'int'


def test_function_type_equality(type_checker, location):
    """Test function type equality checking."""
    int_type = PrimitiveType(location=location, name='int')
    func1 = FunctionType(parameter_types=[int_type, int_type], return_type=int_type, location=location)
    func2 = FunctionType(parameter_types=[int_type, int_type], return_type=int_type, location=location)
    assert type_checker.types_equal(func1, func2)


def test_function_type_inequality(type_checker, location):
    """Test function type inequality checking."""
    int_type = PrimitiveType(location=location, name='int')
    string_type = PrimitiveType(location=location, name='string')
    func1 = FunctionType(parameter_types=[int_type], return_type=int_type, location=location)
    func2 = FunctionType(parameter_types=[string_type], return_type=int_type, location=location)
    assert not type_checker.types_equal(func1, func2)


# ============================================================================
# Additional Tests (7 tests for comprehensive coverage)
# ============================================================================

def test_interpolated_string_type(type_checker, location):
    """Test interpolated string returns string type."""
    parts = ["Hello ", ", you are ", " years old"]
    name_expr = LiteralExpr(value="Alice", type_hint='string', location=location)
    age_expr = LiteralExpr(value=25, type_hint='int', location=location)
    interp = InterpolatedStringExpr(parts=parts, expressions=[name_expr, age_expr], location=location)
    result_type = type_checker.visit_InterpolatedStringExpr(interp)
    assert isinstance(result_type, PrimitiveType)
    assert result_type.name == 'string'


def test_expression_statement(type_checker, symbol_table, location):
    """Test expression statement type checking."""
    # Define function
    int_type = PrimitiveType(location=location, name='int')
    func_type = FunctionType(parameter_types=[], return_type=int_type, location=location)
    symbol = Symbol('get_value', 'function', func_type, location)
    symbol_table.define(symbol)

    # Create expression statement
    callee = IdentifierExpr(name='get_value', location=location)
    call = CallExpr(callee=callee, arguments=[], location=location)
    expr_stmt = ExpressionStmt(expression=call, location=location)
    type_checker.visit_ExpressionStmt(expr_stmt)
    assert len(type_checker.errors) == 0


def test_block_statement(type_checker, location):
    """Test block statement type checking."""
    # Create block with statements
    lit = LiteralExpr(value=5, type_hint='int', location=location)
    expr_stmt = ExpressionStmt(expression=lit, location=location)
    block = BlockStmt(statements=[expr_stmt], location=location)
    type_checker.visit_BlockStmt(block)
    assert len(type_checker.errors) == 0


def test_function_declaration(type_checker, location):
    """Test function declaration type checking."""
    int_type = PrimitiveType(location=location, name='int')
    param = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    return_value = IdentifierExpr(name='x', location=location)
    return_stmt = ReturnStmt(value=return_value, location=location)
    body = BlockStmt(statements=[return_stmt], location=location)

    func_decl = FunctionDecl(
        return_type=int_type,
        name='identity',
        parameters=[param],
        body=body,
        is_lambda=False,
        location=location
    )

    # Need to define 'x' in symbol table for the function body
    type_checker.symbol_table.define(Symbol('x', 'parameter', int_type, location))
    type_checker.visit_FunctionDecl(func_decl)
    # Should have no errors (return type matches)


def test_parameter_default_value_type_mismatch(type_checker, location):
    """Test parameter default value type mismatch."""
    int_type = PrimitiveType(location=location, name='int')
    default_value = LiteralExpr(value="hello", type_hint='string', location=location)
    param = ParameterDecl(param_type=int_type, name='x', default_value=default_value, location=location)
    type_checker.visit_ParameterDecl(param)
    assert len(type_checker.errors) == 1
    assert "does not match parameter type" in type_checker.errors[0].message


def test_lambda_expression(type_checker, location):
    """Test lambda expression type checking."""
    int_type = PrimitiveType(location=location, name='int')
    param = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    body = IdentifierExpr(name='x', location=location)  # Simple body: just return x

    lambda_expr = LambdaExpr(
        parameters=[param],
        return_type=int_type,
        body=body,
        location=location
    )

    result_type = type_checker.visit_LambdaExpr(lambda_expr)
    assert isinstance(result_type, FunctionType)
    assert len(result_type.parameter_types) == 1


def test_check_program(type_checker, location):
    """Test check_program method."""
    # Create simple program with function
    int_type = PrimitiveType(location=location, name='int')
    return_value = LiteralExpr(value=42, type_hint='int', location=location)
    return_stmt = ReturnStmt(value=return_value, location=location)
    body = BlockStmt(statements=[return_stmt], location=location)

    func_decl = FunctionDecl(
        return_type=int_type,
        name='main',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func_decl], location=location)
    errors = type_checker.check_program(program)
    assert len(errors) == 0
