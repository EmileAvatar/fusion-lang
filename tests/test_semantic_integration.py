"""Integration tests for the semantic analyzer.

This module tests the SemanticAnalyzer class with complete Fusion programs,
including valid programs, invalid programs, and error recovery scenarios.
"""

import pytest
from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from src.semantic import SemanticAnalyzer


def analyze_source(source: str) -> SemanticAnalyzer:
    """Helper function to analyze Fusion source code.

    Args:
        source: Fusion source code

    Returns:
        SemanticAnalyzer instance after analysis
    """
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    assert not lexer.diagnostics.errors, f"Lexer errors: {lexer.diagnostics.errors}"

    parser = Parser(tokens)
    try:
        ast = parser.parse_program()
    except ParserError as e:
        raise AssertionError(f"Parser error: {e}")

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return analyzer


# =============================================================================
# Valid Programs (10 tests)
# =============================================================================


def test_hello_world():
    """Test simple Hello World program."""
    source = """
void function main()
    print("Hello, World!")
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 0, f"Unexpected errors: {errors}"


def test_factorial_recursive():
    """Test recursive factorial function."""
    source = """
int function factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)
End function

int function main()
    int result = factorial(5)
    print("Factorial: {result}")
    return 0
End function
"""
    analyzer = analyze_source(source)
    assert len(analyzer.get_errors()) == 0


def test_factorial_iterative():
    """Test iterative factorial with for loop."""
    source = """
int function factorial(int n)
    int result = 1
    int i = 1
    while i <= n
        result = result * i
        i = i + 1
    return result
End function

void function main()
    int result = factorial(5)
    print("Result: {result}")
End function
"""
    analyzer = analyze_source(source)
    assert len(analyzer.get_errors()) == 0


def test_fizzbuzz():
    """Test FizzBuzz program with loops and conditionals."""
    source = """
void function main()
    int i = 1
    while i <= 100
        if i % 15 == 0
            print("FizzBuzz")
        else
            if i % 3 == 0
                print("Fizz")
            else
                if i % 5 == 0
                    print("Buzz")
                else
                    print("{i}")
        i = i + 1
End function
"""
    analyzer = analyze_source(source)
    assert len(analyzer.get_errors()) == 0


def test_calculator():
    """Test calculator with multiple functions."""
    source = """
int function add(int a, int b)
    return a + b
End function

int function subtract(int a, int b)
    return a - b
End function

int function multiply(int a, int b)
    return a * b
End function

void function main()
    int x = 10
    int y = 5
    int sum = add(x, y)
    int diff = subtract(x, y)
    int prod = multiply(x, y)
    print("Sum: {sum}, Diff: {diff}, Prod: {prod}")
End function
"""
    analyzer = analyze_source(source)
    assert len(analyzer.get_errors()) == 0


def test_variable_shadowing():
    """Test function-level scoping: duplicate declaration is an error."""
    source = """
void function main()
    int x = 10
    if true
        int x = 20
        print("{x}")
    print("{x}")
End function
"""
    analyzer = analyze_source(source)
    # Function-level scoping: duplicate declaration is an error
    assert len(analyzer.get_errors()) == 1
    assert "duplicate" in analyzer.get_errors()[0].message.lower()


def test_type_promotion():
    """Test automatic type promotion from int to float."""
    source = """
void function main()
    int x = 10
    float y = 5.5
    float result = x + y
    print("{result}")
End function
"""
    analyzer = analyze_source(source)
    assert len(analyzer.get_errors()) == 0


def test_lambda_expression():
    """Test inline lambda expression."""
    source = """
int function square(int x) : x * x

void function main()
    int result = square(5)
    print("{result}")
End function
"""
    analyzer = analyze_source(source)
    assert len(analyzer.get_errors()) == 0


def test_const_variable():
    """Test constant variable declaration."""
    source = """
void function main()
    const int MAX = 100
    int i = 0
    while i < MAX
        i = i + 1
End function
"""
    analyzer = analyze_source(source)
    assert len(analyzer.get_errors()) == 0


def test_multiple_return_paths():
    """Test function with multiple return paths."""
    source = """
int function abs(int x)
    if x >= 0
        return x
    return -x
End function

void function main()
    int result = abs(-5)
    print("{result}")
End function
"""
    analyzer = analyze_source(source)
    assert len(analyzer.get_errors()) == 0


# =============================================================================
# Invalid Programs (15 tests)
# =============================================================================


def test_no_main_function():
    """Test error when main function is missing."""
    source = """
int function helper()
    return 42
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 1
    assert "main" in str(errors[0]).lower()


def test_multiple_main_functions():
    """Test error when multiple main functions exist."""
    source = """
void function main()
    print("First main")
End function

int function main()
    return 0
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) >= 1
    assert any("main" in str(e).lower() for e in errors)


def test_undefined_variable():
    """Test error for undefined variable."""
    source = """
void function main()
    print("{x}")
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    # Both name_resolver and type_checker report this error (2 errors total)
    assert len(errors) == 2
    assert all("undefined" in str(e).lower() or "not defined" in str(e).lower() for e in errors)


def test_type_mismatch_assignment():
    """Test error for type mismatch in assignment."""
    source = """
void function main()
    int x = "hello"
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 1
    assert "type" in str(errors[0]).lower()


def test_type_mismatch_return():
    """Test error for type mismatch in return statement."""
    source = """
int function test()
    return "hello"
End function

void function main()
    int x = test()
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) >= 1
    assert any("type" in str(e).lower() for e in errors)


def test_function_call_wrong_arg_count():
    """Test error for function call with wrong argument count."""
    source = """
int function add(int a, int b)
    return a + b
End function

void function main()
    int result = add(5)
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 1
    assert "argument" in str(errors[0]).lower()


def test_function_call_wrong_arg_type():
    """Test error for function call with wrong argument type."""
    source = """
int function add(int a, int b)
    return a + b
End function

void function main()
    int result = add(5, "hello")
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    # Error message contains "expected int, got string"
    assert len(errors) >= 1
    error_strs = [str(e).lower() for e in errors]
    assert any("expected" in e and ("int" in e or "string" in e) for e in error_strs)


def test_break_outside_loop():
    """Test error for break statement outside loop."""
    source = """
void function main()
    break
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 1
    assert "break" in str(errors[0]).lower()


def test_continue_outside_loop():
    """Test error for continue statement outside loop."""
    source = """
void function main()
    continue
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 1
    assert "continue" in str(errors[0]).lower()


def test_missing_return():
    """Test error for non-void function missing return."""
    source = """
int function test()
    int x = 5
End function

void function main()
    int y = test()
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) >= 1
    assert any("return" in str(e).lower() for e in errors)


def test_duplicate_variable_same_scope():
    """Test error for duplicate variable in same scope."""
    source = """
void function main()
    int x = 10
    int x = 20
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 1
    assert "duplicate" in str(errors[0]).lower() or "already defined" in str(errors[0]).lower()


def test_duplicate_function():
    """Test error for duplicate function definition."""
    source = """
int function helper()
    return 42
End function

int function helper()
    return 100
End function

void function main()
    int x = helper()
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) >= 1
    assert any("duplicate" in str(e).lower() or "already defined" in str(e).lower() for e in errors)


def test_call_undefined_function():
    """Test error for calling undefined function."""
    source = """
void function main()
    int x = unknown()
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    # 3 errors: 2x "undefined function" (from name_resolver and type_checker) + 1x "cannot assign void"
    assert len(errors) == 3
    undefined_errors = [e for e in errors if "undefined" in str(e).lower() or "not defined" in str(e).lower()]
    assert len(undefined_errors) >= 1


def test_assign_to_constant():
    """Test error for assigning to constant variable."""
    source = """
void function main()
    const int MAX = 100
    MAX = 200
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 1
    assert "const" in str(errors[0]).lower() or "constant" in str(errors[0]).lower()


def test_if_condition_not_bool():
    """Test error for if condition that's not boolean."""
    source = """
void function main()
    if 42
        print("test")
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    # 2 errors: from type_checker and control_flow_validator
    assert len(errors) == 2
    assert all("bool" in str(e).lower() or "condition" in str(e).lower() for e in errors)


# =============================================================================
# Error Recovery (5 tests)
# =============================================================================


def test_multiple_undefined_variables():
    """Test that multiple undefined variables are all reported."""
    source = """
void function main()
    print("{x}")
    print("{y}")
    print("{z}")
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    # 6 errors: 3 from name_resolver + 3 from type_checker (duplicates)
    assert len(errors) == 6


def test_multiple_type_errors():
    """Test that multiple type errors are all reported."""
    source = """
void function main()
    int x = "hello"
    int y = true
    float z = "world"
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) == 3  # All three type errors


def test_undefined_function_and_type_error():
    """Test that both undefined function and type error are reported."""
    source = """
void function main()
    int x = unknown()
    int y = "hello"
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    # 4 errors: 2x undefined function (duplicate) + 1x cannot assign void + 1x cannot assign string
    assert len(errors) == 4


def test_missing_return_and_type_error():
    """Test that both missing return and type error are reported."""
    source = """
int function test()
    int x = "hello"
End function

void function main()
    int y = test()
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    assert len(errors) >= 2  # At least type error and missing return


def test_errors_and_warnings():
    """Test that both errors and warnings are collected."""
    source = """
int function test()
    return 42
    int x = 10
End function

void function main()
    int y = unknown()
End function
"""
    analyzer = analyze_source(source)
    errors = analyzer.get_errors()
    warnings = analyzer.get_warnings()
    assert len(errors) >= 1  # Undefined variable
    assert len(warnings) >= 1  # Unreachable code
