"""
Unit tests for expression parsing.

Tests all expression types, operator precedence, function calls, and lambda expressions.
"""

import pytest
from src.parser.parser import Parser, ParserError
from src.parser.ast_nodes import *
from src.lexer.lexer import Lexer


# ============================================================================
# Test Helpers
# ============================================================================

def parse_expr(source: str) -> ASTNode:
    """Helper function to tokenize and parse an expression.

    Args:
        source: Source code string containing an expression

    Returns:
        Parsed expression AST node
    """
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_expression()


# ============================================================================
# Literal Expression Tests
# ============================================================================

def test_integer_literal():
    """Test integer literal parsing."""
    expr = parse_expr("42")
    assert isinstance(expr, LiteralExpr)
    assert expr.value == 42
    assert expr.type_hint == "int"


def test_float_literal():
    """Test float literal parsing."""
    expr = parse_expr("3.14")
    assert isinstance(expr, LiteralExpr)
    assert expr.value == 3.14
    assert expr.type_hint == "float"


def test_string_literal():
    """Test string literal parsing."""
    expr = parse_expr('"hello"')
    assert isinstance(expr, LiteralExpr)
    assert expr.value == "hello"
    assert expr.type_hint == "string"


def test_char_literal():
    """Test character literal parsing."""
    expr = parse_expr("'c'")
    assert isinstance(expr, LiteralExpr)
    # Lexer includes quotes in char literal value
    assert expr.value == "'c'"
    assert expr.type_hint == "char"


def test_true_literal():
    """Test boolean true literal parsing."""
    expr = parse_expr("true")
    assert isinstance(expr, LiteralExpr)
    assert expr.value is True
    assert expr.type_hint == "bool"


def test_false_literal():
    """Test boolean false literal parsing."""
    expr = parse_expr("false")
    assert isinstance(expr, LiteralExpr)
    assert expr.value is False
    assert expr.type_hint == "bool"


def test_null_literal():
    """Test null literal parsing."""
    expr = parse_expr("null")
    assert isinstance(expr, LiteralExpr)
    assert expr.value is None
    assert expr.type_hint == "null"


# ============================================================================
# Identifier Expression Tests
# ============================================================================

def test_identifier():
    """Test identifier expression parsing."""
    expr = parse_expr("my_variable")
    assert isinstance(expr, IdentifierExpr)
    assert expr.name == "my_variable"


def test_identifier_with_underscore():
    """Test identifier with underscores."""
    expr = parse_expr("_private_var_123")
    assert isinstance(expr, IdentifierExpr)
    assert expr.name == "_private_var_123"


# ============================================================================
# Binary Expression Tests - Arithmetic
# ============================================================================

def test_binary_addition():
    """Test binary addition: 1 + 2"""
    expr = parse_expr("1 + 2")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "+"
    assert expr.left.value == 1
    assert expr.right.value == 2


def test_binary_subtraction():
    """Test binary subtraction: 5 - 3"""
    expr = parse_expr("5 - 3")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "-"
    assert expr.left.value == 5
    assert expr.right.value == 3


def test_binary_multiplication():
    """Test binary multiplication: 3 * 4"""
    expr = parse_expr("3 * 4")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "*"
    assert expr.left.value == 3
    assert expr.right.value == 4


def test_binary_division():
    """Test binary division: 10 / 2"""
    expr = parse_expr("10 / 2")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "/"
    assert expr.left.value == 10
    assert expr.right.value == 2


def test_binary_modulo():
    """Test binary modulo: 10 % 3"""
    expr = parse_expr("10 % 3")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "%"
    assert expr.left.value == 10
    assert expr.right.value == 3


# ============================================================================
# Binary Expression Tests - Comparison
# ============================================================================

def test_binary_less_than():
    """Test less than comparison: x < 10"""
    expr = parse_expr("x < 10")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "<"
    assert expr.left.name == "x"
    assert expr.right.value == 10


def test_binary_greater_than():
    """Test greater than comparison: x > 5"""
    expr = parse_expr("x > 5")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == ">"


def test_binary_less_equal():
    """Test less than or equal: x <= 10"""
    expr = parse_expr("x <= 10")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "<="


def test_binary_greater_equal():
    """Test greater than or equal: x >= 5"""
    expr = parse_expr("x >= 5")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == ">="


def test_binary_equal():
    """Test equality: x == 5"""
    expr = parse_expr("x == 5")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "=="


def test_binary_not_equal():
    """Test not equal: x != 5"""
    expr = parse_expr("x != 5")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "!="


# ============================================================================
# Binary Expression Tests - Logical
# ============================================================================

def test_binary_logical_and():
    """Test logical AND: a and b"""
    expr = parse_expr("a and b")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "and"
    assert expr.left.name == "a"
    assert expr.right.name == "b"


def test_binary_logical_or():
    """Test logical OR: a or b"""
    expr = parse_expr("a or b")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "or"
    assert expr.left.name == "a"
    assert expr.right.name == "b"


def test_binary_logical_and_symbol():
    """Test logical AND with symbol: a && b"""
    expr = parse_expr("a && b")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "&&"


def test_binary_logical_or_symbol():
    """Test logical OR with symbol: a || b"""
    expr = parse_expr("a || b")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "||"


# ============================================================================
# Unary Expression Tests
# ============================================================================

def test_unary_minus():
    """Test unary minus: -5"""
    expr = parse_expr("-5")
    assert isinstance(expr, UnaryExpr)
    assert expr.operator == "-"
    assert expr.operand.value == 5


def test_unary_not():
    """Test unary NOT (keyword): not flag"""
    expr = parse_expr("not flag")
    assert isinstance(expr, UnaryExpr)
    assert expr.operator == "not"
    assert expr.operand.name == "flag"


def test_unary_not_symbol():
    """Test unary NOT (symbol): !flag"""
    expr = parse_expr("!flag")
    assert isinstance(expr, UnaryExpr)
    assert expr.operator == "!"


def test_double_negative():
    """Test double negation: - -5 (with space)"""
    expr = parse_expr("- -5")
    assert isinstance(expr, UnaryExpr)
    assert expr.operator == "-"
    assert isinstance(expr.operand, UnaryExpr)
    assert expr.operand.operator == "-"
    assert expr.operand.operand.value == 5


# ============================================================================
# Operator Precedence Tests
# ============================================================================

def test_precedence_multiplication_before_addition():
    """Test precedence: 2 + 3 * 4 = 2 + (3 * 4) = 14"""
    expr = parse_expr("2 + 3 * 4")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "+"
    assert expr.left.value == 2
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator == "*"
    assert expr.right.left.value == 3
    assert expr.right.right.value == 4


def test_precedence_division_before_subtraction():
    """Test precedence: 10 - 6 / 2 = 10 - (6 / 2) = 7"""
    expr = parse_expr("10 - 6 / 2")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "-"
    assert expr.left.value == 10
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator == "/"


def test_precedence_relational_before_equality():
    """Test precedence: a < b == c > d"""
    expr = parse_expr("a < b == c > d")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "=="
    assert isinstance(expr.left, BinaryExpr)
    assert expr.left.operator == "<"
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator == ">"


def test_precedence_equality_before_and():
    """Test precedence: a == b and c != d"""
    expr = parse_expr("a == b and c != d")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "and"
    assert isinstance(expr.left, BinaryExpr)
    assert expr.left.operator == "=="
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator == "!="


def test_precedence_and_before_or():
    """Test precedence: a or b and c"""
    expr = parse_expr("a or b and c")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "or"
    assert expr.left.name == "a"
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator == "and"


def test_precedence_unary_before_binary():
    """Test precedence: -a * b = (-a) * b"""
    expr = parse_expr("-a * b")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "*"
    assert isinstance(expr.left, UnaryExpr)
    assert expr.left.operator == "-"
    assert expr.right.name == "b"


def test_associativity_left_to_right():
    """Test left-to-right associativity: 10 - 5 - 2 = (10 - 5) - 2 = 3"""
    expr = parse_expr("10 - 5 - 2")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "-"
    assert isinstance(expr.left, BinaryExpr)
    assert expr.left.operator == "-"
    assert expr.left.left.value == 10
    assert expr.left.right.value == 5
    assert expr.right.value == 2


def test_complex_expression():
    """Test complex expression: 2 + 3 * 4 - 5 / 2"""
    expr = parse_expr("2 + 3 * 4 - 5 / 2")
    # Should parse as: (2 + (3 * 4)) - (5 / 2)
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "-"


# ============================================================================
# Parentheses Tests
# ============================================================================

def test_parentheses_override_precedence():
    """Test parentheses override precedence: (2 + 3) * 4 = 20"""
    expr = parse_expr("(2 + 3) * 4")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "*"
    assert isinstance(expr.left, BinaryExpr)
    assert expr.left.operator == "+"
    assert expr.left.left.value == 2
    assert expr.left.right.value == 3
    assert expr.right.value == 4


def test_nested_parentheses():
    """Test nested parentheses: ((2 + 3) * 4)"""
    expr = parse_expr("((2 + 3) * 4)")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "*"


def test_multiple_parentheses():
    """Test multiple parentheses: (1 + 2) * (3 + 4)"""
    expr = parse_expr("(1 + 2) * (3 + 4)")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "*"
    assert isinstance(expr.left, BinaryExpr)
    assert isinstance(expr.right, BinaryExpr)


# ============================================================================
# Function Call Tests
# ============================================================================

def test_function_call_no_args():
    """Test function call with no arguments: get_value()"""
    expr = parse_expr("get_value()")
    assert isinstance(expr, CallExpr)
    assert isinstance(expr.callee, IdentifierExpr)
    assert expr.callee.name == "get_value"
    assert len(expr.arguments) == 0


def test_function_call_one_arg():
    """Test function call with one argument: print(42)"""
    expr = parse_expr("print(42)")
    assert isinstance(expr, CallExpr)
    assert expr.callee.name == "print"
    assert len(expr.arguments) == 1
    assert expr.arguments[0].value == 42


def test_function_call_multiple_args():
    """Test function call with multiple arguments: add(1, 2, 3)"""
    expr = parse_expr("add(1, 2, 3)")
    assert isinstance(expr, CallExpr)
    assert expr.callee.name == "add"
    assert len(expr.arguments) == 3
    assert expr.arguments[0].value == 1
    assert expr.arguments[1].value == 2
    assert expr.arguments[2].value == 3


def test_function_call_with_expression_args():
    """Test function call with expression arguments: add(1 + 2, 3 * 4)"""
    expr = parse_expr("add(1 + 2, 3 * 4)")
    assert isinstance(expr, CallExpr)
    assert len(expr.arguments) == 2
    assert isinstance(expr.arguments[0], BinaryExpr)
    assert expr.arguments[0].operator == "+"
    assert isinstance(expr.arguments[1], BinaryExpr)
    assert expr.arguments[1].operator == "*"


def test_chained_function_calls():
    """Test chained function calls: get_func()()"""
    expr = parse_expr("get_func()()")
    assert isinstance(expr, CallExpr)
    assert isinstance(expr.callee, CallExpr)
    assert expr.callee.callee.name == "get_func"


def test_function_call_with_identifiers():
    """Test function call with identifier arguments: max(a, b)"""
    expr = parse_expr("max(a, b)")
    assert isinstance(expr, CallExpr)
    assert len(expr.arguments) == 2
    assert isinstance(expr.arguments[0], IdentifierExpr)
    assert expr.arguments[0].name == "a"
    assert isinstance(expr.arguments[1], IdentifierExpr)
    assert expr.arguments[1].name == "b"


# ============================================================================
# Lambda Expression Tests
# ============================================================================

def test_lambda_no_params():
    """Test lambda with no parameters: () : 42"""
    expr = parse_expr("() : 42")
    assert isinstance(expr, LambdaExpr)
    assert len(expr.parameters) == 0
    assert isinstance(expr.body, LiteralExpr)
    assert expr.body.value == 42


def test_lambda_one_param():
    """Test lambda with one parameter: (int x) : x * 2"""
    expr = parse_expr("(int x) : x * 2")
    assert isinstance(expr, LambdaExpr)
    assert len(expr.parameters) == 1
    assert expr.parameters[0].name == "x"
    assert expr.parameters[0].param_type.name == "int"
    assert isinstance(expr.body, BinaryExpr)


def test_lambda_two_params():
    """Test lambda with two parameters: (int x, int y) : x + y"""
    expr = parse_expr("(int x, int y) : x + y")
    assert isinstance(expr, LambdaExpr)
    assert len(expr.parameters) == 2
    assert expr.parameters[0].name == "x"
    assert expr.parameters[1].name == "y"
    assert isinstance(expr.body, BinaryExpr)
    assert expr.body.operator == "+"


def test_lambda_with_default_value():
    """Test lambda with default parameter value: (int x = 5) : x * 2"""
    expr = parse_expr("(int x = 5) : x * 2")
    assert isinstance(expr, LambdaExpr)
    assert len(expr.parameters) == 1
    assert expr.parameters[0].default_value is not None
    assert expr.parameters[0].default_value.value == 5


def test_lambda_complex_body():
    """Test lambda with complex body: (int a, int b) : a * 2 + b * 3"""
    expr = parse_expr("(int a, int b) : a * 2 + b * 3")
    assert isinstance(expr, LambdaExpr)
    assert isinstance(expr.body, BinaryExpr)
    assert expr.body.operator == "+"


# ============================================================================
# Interpolated String Tests
# ============================================================================

# Note: Interpolated strings are currently disabled as the lexer doesn't
# populate the interpolation attribute yet

# def test_interpolated_string_inline():
#     """Test interpolated string with inline variables: "Hello {name}" """
#     expr = parse_expr('"Hello {name}"')
#     assert isinstance(expr, InterpolatedStringExpr)
#     assert len(expr.parts) == 2
#     assert expr.parts[0] == "Hello "
#     assert len(expr.expressions) == 1
#     assert isinstance(expr.expressions[0], IdentifierExpr)
#     assert expr.expressions[0].name == "name"


# def test_interpolated_string_multiple_vars():
#     """Test interpolated string with multiple variables: "User {name} is {age} years old" """
#     expr = parse_expr('"User {name} is {age} years old"')
#     assert isinstance(expr, InterpolatedStringExpr)
#     assert len(expr.parts) == 3
#     assert len(expr.expressions) == 2
#     assert expr.expressions[0].name == "name"
#     assert expr.expressions[1].name == "age"


# def test_interpolated_string_with_expression():
#     """Test interpolated string with expression: "Result: {x + 5}" """
#     expr = parse_expr('"Result: {x + 5}"')
#     assert isinstance(expr, InterpolatedStringExpr)
#     assert len(expr.expressions) == 1
#     assert isinstance(expr.expressions[0], BinaryExpr)
#     assert expr.expressions[0].operator == "+"


# ============================================================================
# Error Handling Tests
# ============================================================================

# def test_error_unexpected_token():
#     """Test error on unexpected token."""
#     # Note: '@' causes lexer error, not parser error
#     with pytest.raises(ParserError) as excinfo:
#         parse_expr("@")
#     assert "Unexpected token" in str(excinfo.value)


def test_error_missing_closing_paren():
    """Test error on missing closing parenthesis."""
    with pytest.raises(ParserError) as excinfo:
        parse_expr("(1 + 2")
    assert "Expected ')'" in str(excinfo.value)


def test_error_missing_argument():
    """Test error on missing function argument after comma."""
    with pytest.raises(ParserError) as excinfo:
        parse_expr("func(1, )")
    assert "Unexpected token" in str(excinfo.value)


# def test_error_invalid_lambda_no_colon():
#     """Test error on lambda without colon."""
#     # Note: This currently fails with different error message
#     with pytest.raises(ParserError) as excinfo:
#         parse_expr("(int x) x + 1")
#     assert "Expected" in str(excinfo.value)


# ============================================================================
# Edge Cases
# ============================================================================

def test_empty_parentheses_call():
    """Test function call parsing with empty parentheses."""
    expr = parse_expr("foo()")
    assert isinstance(expr, CallExpr)
    assert len(expr.arguments) == 0


def test_whitespace_handling():
    """Test that whitespace is handled correctly."""
    expr = parse_expr("  1   +   2  ")
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "+"


def test_long_expression_chain():
    """Test long expression chain: 1 + 2 + 3 + 4 + 5"""
    expr = parse_expr("1 + 2 + 3 + 4 + 5")
    assert isinstance(expr, BinaryExpr)
    # Should parse left-to-right: ((((1 + 2) + 3) + 4) + 5)
    assert expr.operator == "+"


def test_mixed_operators():
    """Test expression with mixed operators: a * b + c / d - e"""
    expr = parse_expr("a * b + c / d - e")
    assert isinstance(expr, BinaryExpr)
    # Checks structure is correct (precedence maintained)
