"""
Tests for Declaration Parsing

This module tests the parser's ability to parse top-level declarations:
- Function declarations
- Parameter lists with default values
- Inline lambda syntax
- Program structure (ProgramNode)
"""

import pytest
from src.parser.parser import Parser, ParserError
from src.parser.ast_nodes import *
from src.lexer.lexer import Lexer
from src.lexer.token import TokenType


def parse_program(source: str) -> ProgramNode:
    """Helper: tokenize and parse program."""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_program()


# ============================================================================
# Simple Function Declarations
# ============================================================================

def test_simple_function_brace_block():
    """Test simple function: int function add(int a, int b) { return a + b }"""
    source = """
int function add(int a, int b) {
    return a + b
}
"""
    program = parse_program(source)
    assert len(program.declarations) == 1

    func = program.declarations[0]
    assert isinstance(func, FunctionDecl)
    assert func.name == "add"
    assert isinstance(func.return_type, PrimitiveType)
    assert func.return_type.name == "int"
    assert len(func.parameters) == 2
    assert func.parameters[0].name == "a"
    assert func.parameters[1].name == "b"
    assert not func.is_lambda
    assert isinstance(func.body, BlockStmt)


def test_function_no_params():
    """Test function with no parameters."""
    source = """
int function getNumber() {
    return 42
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert isinstance(func, FunctionDecl)
    assert func.name == "getNumber"
    assert len(func.parameters) == 0
    assert func.return_type.name == "int"


def test_void_function():
    """Test void function (no return value)."""
    source = """
void function printHello() {
    print("Hello")
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert isinstance(func, FunctionDecl)
    assert func.name == "printHello"
    assert func.return_type.name == "void"


def test_function_single_param():
    """Test function with single parameter."""
    source = """
int function square(int x) {
    return x * x
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert len(func.parameters) == 1
    assert func.parameters[0].name == "x"
    assert func.parameters[0].param_type.name == "int"


def test_function_multiple_params():
    """Test function with multiple parameters."""
    source = """
int function calculate(int a, int b, int c) {
    return a + b + c
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert len(func.parameters) == 3
    assert func.parameters[0].name == "a"
    assert func.parameters[1].name == "b"
    assert func.parameters[2].name == "c"


# ============================================================================
# Parameter Default Values
# ============================================================================

def test_function_with_default_param():
    """Test function with default parameter value."""
    source = """
void function greet(string name = "World") {
    print("Hello, " + name)
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert len(func.parameters) == 1
    assert func.parameters[0].name == "name"
    assert func.parameters[0].default_value is not None
    assert isinstance(func.parameters[0].default_value, LiteralExpr)
    assert func.parameters[0].default_value.value == "World"


def test_function_mixed_default_params():
    """Test function with mixed required and default parameters."""
    source = """
int function power(int base, int exponent = 2) {
    return base * exponent
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert len(func.parameters) == 2
    assert func.parameters[0].name == "base"
    assert func.parameters[0].default_value is None  # Required
    assert func.parameters[1].name == "exponent"
    assert func.parameters[1].default_value is not None  # Default
    assert func.parameters[1].default_value.value == 2


def test_function_all_default_params():
    """Test function with all parameters having defaults."""
    source = """
void function log(string message = "default", int level = 1) {
    print(message)
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert len(func.parameters) == 2
    assert func.parameters[0].default_value.value == "default"
    assert func.parameters[1].default_value.value == 1


# ============================================================================
# Inline Lambda Syntax
# ============================================================================

def test_inline_lambda_simple():
    """Test inline lambda: int function multiply(int x, int y) : x * y"""
    source = "int function multiply(int x, int y) : x * y"

    program = parse_program(source)
    assert len(program.declarations) == 1

    func = program.declarations[0]
    assert isinstance(func, FunctionDecl)
    assert func.name == "multiply"
    assert func.is_lambda
    assert isinstance(func.body, BlockStmt)
    # Lambda body should be wrapped in a return statement
    assert len(func.body.statements) == 1
    assert isinstance(func.body.statements[0], ReturnStmt)


def test_inline_lambda_addition():
    """Test inline lambda with addition: int function add(int a, int b) : a + b"""
    source = "int function add(int a, int b) : a + b"

    program = parse_program(source)
    func = program.declarations[0]

    assert func.is_lambda
    ret_stmt = func.body.statements[0]
    assert isinstance(ret_stmt.value, BinaryExpr)
    assert ret_stmt.value.operator == "+"


def test_inline_lambda_no_params():
    """Test inline lambda with no parameters: int function getNumber() : 42"""
    source = "int function getNumber() : 42"

    program = parse_program(source)
    func = program.declarations[0]

    assert func.is_lambda
    assert len(func.parameters) == 0
    ret_stmt = func.body.statements[0]
    assert ret_stmt.value.value == 42


def test_inline_lambda_function_call():
    """Test inline lambda with function call: void function test() : print("Hello")"""
    source = 'void function test() : print("Hello")'

    program = parse_program(source)
    func = program.declarations[0]

    assert func.is_lambda
    ret_stmt = func.body.statements[0]
    assert isinstance(ret_stmt.value, CallExpr)


# ============================================================================
# Multi-line Lambda Syntax
# ============================================================================

def test_multiline_lambda_indentation():
    """Test multi-line lambda with indentation."""
    source = """
int function factorial(int n) :
    if n <= 1
        return 1
    return n * factorial(n - 1)
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.is_lambda
    assert isinstance(func.body, BlockStmt)
    assert len(func.body.statements) > 0


def test_multiline_lambda_conditional():
    """Test multi-line lambda with conditional."""
    source = """
int function abs(int x) :
    if x < 0
        return -x
    return x
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.is_lambda
    assert isinstance(func.body, BlockStmt)


# ============================================================================
# Block Style Variations
# ============================================================================

def test_function_indentation_style():
    """Test function with indentation block style."""
    source = """
int function factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "factorial"
    assert not func.is_lambda  # Not a lambda, just indentation-style function
    assert isinstance(func.body, BlockStmt)


def test_function_end_keyword_style():
    """Test function with End keyword block style."""
    source = """
int function factorial(int n)
    if n <= 1
        return 1
    End if
    return n * factorial(n - 1)
End function
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "factorial"
    assert not func.is_lambda
    assert isinstance(func.body, BlockStmt)


# ============================================================================
# Main Function
# ============================================================================

def test_main_function():
    """Test main function entry point."""
    source = """
int function main() {
    print("Hello, World!")
    return 0
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "main"
    assert func.return_type.name == "int"
    assert len(func.parameters) == 0


# ============================================================================
# Multiple Functions
# ============================================================================

def test_multiple_functions():
    """Test multiple function declarations."""
    source = """
int function add(int a, int b) {
    return a + b
}

int function multiply(int x, int y) {
    return x * y
}

int function subtract(int a, int b) {
    return a - b
}
"""
    program = parse_program(source)
    assert len(program.declarations) == 3
    assert program.declarations[0].name == "add"
    assert program.declarations[1].name == "multiply"
    assert program.declarations[2].name == "subtract"


def test_mixed_function_styles():
    """Test mix of lambda and regular functions."""
    source = """
int function add(int a, int b) : a + b

int function multiply(int x, int y) {
    return x * y
}
"""
    program = parse_program(source)
    assert len(program.declarations) == 2
    assert program.declarations[0].is_lambda
    assert not program.declarations[1].is_lambda


# ============================================================================
# Complex Functions
# ============================================================================

def test_function_with_nested_blocks():
    """Test function with nested control structures."""
    source = """
int function max(int a, int b, int c) {
    if a > b {
        if a > c {
            return a
        } else {
            return c
        }
    } else {
        if b > c {
            return b
        } else {
            return c
        }
    }
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "max"
    assert len(func.parameters) == 3


def test_function_with_loop():
    """Test function with loop."""
    source = """
int function sum(int n) {
    int total = 0
    for i in range {
        total = total + i
    }
    return total
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "sum"
    assert isinstance(func.body, BlockStmt)


def test_recursive_function():
    """Test recursive function."""
    source = """
int function fibonacci(int n) {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "fibonacci"


# ============================================================================
# Return Types
# ============================================================================

def test_function_string_return_type():
    """Test function with string return type."""
    source = """
string function getName() {
    return "Alice"
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.return_type.name == "string"


def test_function_bool_return_type():
    """Test function with bool return type."""
    source = """
bool function isPositive(int x) {
    return x > 0
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.return_type.name == "bool"


def test_function_float_return_type():
    """Test function with float return type."""
    source = """
float function divide(int a, int b) {
    return a / b
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert func.return_type.name == "float"


# ============================================================================
# Empty Programs
# ============================================================================

def test_empty_program():
    """Test parsing empty program."""
    source = ""
    program = parse_program(source)

    assert isinstance(program, ProgramNode)
    assert len(program.declarations) == 0


def test_program_with_only_whitespace():
    """Test parsing program with only whitespace and newlines."""
    source = "\n\n\n"
    program = parse_program(source)

    assert len(program.declarations) == 0


# ============================================================================
# Error Handling
# ============================================================================

def test_error_missing_function_name():
    """Test error: function without name."""
    with pytest.raises(ParserError) as exc_info:
        source = """
int function () {
    return 0
}
"""
        parse_program(source)
    assert "Expected function name" in str(exc_info.value)


def test_error_missing_lparen():
    """Test error: missing opening parenthesis."""
    with pytest.raises(ParserError) as exc_info:
        source = "int function test) { return 0 }"
        parse_program(source)
    assert "Expected '(' after function name" in str(exc_info.value)


def test_error_missing_rparen():
    """Test error: missing closing parenthesis."""
    with pytest.raises(ParserError) as exc_info:
        source = "int function test(int x { return x }"
        parse_program(source)
    assert "Expected ')' after parameters" in str(exc_info.value)


def test_error_missing_parameter_name():
    """Test error: parameter without name."""
    with pytest.raises(ParserError) as exc_info:
        source = "int function test(int) { return 0 }"
        parse_program(source)
    assert "Expected parameter name" in str(exc_info.value)


def test_error_invalid_return_type():
    """Test error: invalid return type."""
    with pytest.raises(ParserError) as exc_info:
        source = "unknown function test() { return 0 }"
        parse_program(source)
    # Parser sees "unknown" as an identifier, not a type keyword
    assert "Unexpected token" in str(exc_info.value)


def test_error_missing_function_body():
    """Test error: function without body."""
    with pytest.raises(ParserError) as exc_info:
        source = "int function test()"
        parse_program(source)
    # Parser expects a block or colon
    assert "Unexpected" in str(exc_info.value) or "Expected" in str(exc_info.value)


def test_error_unexpected_token_at_top_level():
    """Test error: unexpected token at top level."""
    with pytest.raises(ParserError) as exc_info:
        source = "return 42"
        parse_program(source)
    assert "Unexpected token" in str(exc_info.value)


# ============================================================================
# Edge Cases
# ============================================================================

def test_function_with_underscore_in_name():
    """Test function name with underscores."""
    source = "int function get_value() { return 42 }"
    program = parse_program(source)
    func = program.declarations[0]

    assert func.name == "get_value"


def test_function_param_with_complex_default():
    """Test parameter with expression as default value."""
    source = "int function test(int x = 2 + 3) { return x }"
    program = parse_program(source)
    func = program.declarations[0]

    assert func.parameters[0].default_value is not None
    assert isinstance(func.parameters[0].default_value, BinaryExpr)


def test_very_long_parameter_list():
    """Test function with many parameters."""
    source = """
int function test(int a, int b, int c, int d, int e, int f, int g) {
    return a + b + c + d + e + f + g
}
"""
    program = parse_program(source)
    func = program.declarations[0]

    assert len(func.parameters) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
