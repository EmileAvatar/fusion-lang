"""
Tests for Parser Integration

This module tests end-to-end parsing of complete Fusion programs:
- Example programs (Hello World, Factorial, FizzBuzz, Calculator)
- EBNF test cases from grammar specification
- Real-world code patterns
- Multi-function programs
"""

import pytest
from src.parser.parser import Parser, ParserError
from src.parser.ast_nodes import *
from src.lexer.lexer import Lexer
from src.lexer.token import TokenType


def parse_program(source: str, filename: str = "<test>") -> ProgramNode:
    """Helper: tokenize and parse complete program."""
    lexer = Lexer(source, filename)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_program()


# ============================================================================
# Example Program Tests
# ============================================================================

def test_hello_world():
    """Test parsing Hello World program."""
    source = """
int function main() {
    print("Hello, World!")
    return 0
}
"""
    program = parse_program(source, "hello_world.fusion")

    assert isinstance(program, ProgramNode)
    assert len(program.declarations) == 1

    main_func = program.declarations[0]
    assert isinstance(main_func, FunctionDecl)
    assert main_func.name == "main"
    assert main_func.return_type.name == "int"
    assert len(main_func.parameters) == 0
    assert isinstance(main_func.body, BlockStmt)


def test_factorial_recursive():
    """Test parsing factorial function (recursion)."""
    source = """
int function factorial(int n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
"""
    program = parse_program(source, "factorial.fusion")

    func = program.declarations[0]
    assert func.name == "factorial"
    assert func.return_type.name == "int"
    assert len(func.parameters) == 1
    assert func.parameters[0].name == "n"
    assert func.parameters[0].param_type.name == "int"
    assert isinstance(func.body, BlockStmt)
    # Body should have if statement and return statement
    assert len(func.body.statements) == 2


def test_factorial_iterative():
    """Test parsing iterative factorial function."""
    source = """
int function factorial(int n) {
    int result = 1
    for i in range(1, n + 1) {
        result = result * i
    }
    return result
}
"""
    program = parse_program(source, "factorial_iter.fusion")

    func = program.declarations[0]
    assert func.name == "factorial"
    assert isinstance(func.body, BlockStmt)
    # Body: var decl, for loop, return
    assert len(func.body.statements) == 3
    assert isinstance(func.body.statements[0], VarDeclStmt)
    assert isinstance(func.body.statements[1], ForStmt)
    assert isinstance(func.body.statements[2], ReturnStmt)


def test_fizzbuzz():
    """Test parsing FizzBuzz program."""
    source = """
void function fizzbuzz(int n) {
    for i in range(1, n + 1) {
        if i % 15 == 0 {
            print("FizzBuzz")
        } else if i % 3 == 0 {
            print("Fizz")
        } else if i % 5 == 0 {
            print("Buzz")
        } else {
            print(i)
        }
    }
}

int function main() {
    fizzbuzz(100)
    return 0
}
"""
    program = parse_program(source, "fizzbuzz.fusion")

    assert len(program.declarations) == 2
    assert program.declarations[0].name == "fizzbuzz"
    assert program.declarations[1].name == "main"

    fizzbuzz_func = program.declarations[0]
    assert fizzbuzz_func.return_type.name == "void"
    assert len(fizzbuzz_func.parameters) == 1


def test_calculator():
    """Test parsing calculator with multiple functions."""
    source = """
int function add(int a, int b) : a + b

int function subtract(int a, int b) : a - b

int function multiply(int a, int b) : a * b

int function divide(int a, int b) {
    if b == 0 {
        print("Error: division by zero")
        return 0
    }
    return a / b
}

int function main() {
    int x = 10
    int y = 5
    print(add(x, y))
    print(subtract(x, y))
    print(multiply(x, y))
    print(divide(x, y))
    return 0
}
"""
    program = parse_program(source, "calculator.fusion")

    assert len(program.declarations) == 5
    assert program.declarations[0].name == "add"
    assert program.declarations[1].name == "subtract"
    assert program.declarations[2].name == "multiply"
    assert program.declarations[3].name == "divide"
    assert program.declarations[4].name == "main"

    # First 3 are lambdas
    assert program.declarations[0].is_lambda
    assert program.declarations[1].is_lambda
    assert program.declarations[2].is_lambda
    # Divide is regular function
    assert not program.declarations[3].is_lambda


def test_sum_array():
    """Test parsing function that sums array elements."""
    source = """
int function sum(int n) {
    int total = 0
    for i in range(0, n) {
        total = total + i
    }
    return total
}
"""
    program = parse_program(source)

    func = program.declarations[0]
    assert func.name == "sum"
    assert func.return_type.name == "int"


def test_max_of_three():
    """Test parsing function with nested conditionals."""
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


# ============================================================================
# EBNF Test Cases
# ============================================================================

def test_ebnf_case_1_inline_lambda():
    """EBNF Test Case 1: int multiply(int x, int y) : x * y"""
    source = "int function multiply(int x, int y) : x * y"

    program = parse_program(source)

    func = program.declarations[0]
    assert func.name == "multiply"
    assert func.is_lambda
    assert isinstance(func.body, BlockStmt)
    # Lambda body wrapped in return statement
    assert len(func.body.statements) == 1
    assert isinstance(func.body.statements[0], ReturnStmt)


def test_ebnf_case_2_multiline_function():
    """EBNF Test Case 2: Multi-line function with if"""
    source = """
int function abs(int x)
    if x < 0
        return -x
    return x
"""
    program = parse_program(source)

    func = program.declarations[0]
    assert func.name == "abs"
    assert not func.is_lambda
    assert isinstance(func.body, BlockStmt)


def test_ebnf_case_3_variable_declaration():
    """EBNF Test Case 3: Variable declaration in function"""
    source = """
void function test() {
    int x = 42
    string name = "Alice"
    bool flag = true
}
"""
    program = parse_program(source)

    func = program.declarations[0]
    assert len(func.body.statements) == 3
    assert all(isinstance(stmt, VarDeclStmt) for stmt in func.body.statements)


def test_ebnf_case_8_lambda_expression():
    """EBNF Test Case 8: Lambda expression (using lambda function declaration)"""
    # Note: Lambda variable assignment (func add = ...) is a future feature
    # For now, test lambda function declarations instead
    source = """
int function add(int a, int b) : a + b

int function test() {
    return add(1, 2)
}
"""
    program = parse_program(source)

    # First function is a lambda
    add_func = program.declarations[0]
    assert add_func.is_lambda
    assert add_func.name == "add"


def test_ebnf_case_9_end_function():
    """EBNF Test Case 9: End function syntax"""
    source = """
int function add(int a, int b)
    return a + b
End function
"""
    program = parse_program(source)

    func = program.declarations[0]
    assert func.name == "add"
    assert not func.is_lambda


# ============================================================================
# Block Style Variations
# ============================================================================

def test_program_with_brace_blocks():
    """Test program using only brace blocks."""
    source = """
int function fibonacci(int n) {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}
"""
    program = parse_program(source)
    assert len(program.declarations) == 1


def test_program_with_indentation_blocks():
    """Test program using only indentation blocks."""
    source = """
int function fibonacci(int n)
    if n <= 1
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""
    program = parse_program(source)
    assert len(program.declarations) == 1


def test_program_with_end_keywords():
    """Test program using End keywords."""
    source = """
int function fibonacci(int n)
    if n <= 1
        return n
    End if
    return fibonacci(n - 1) + fibonacci(n - 2)
End function
"""
    program = parse_program(source)
    assert len(program.declarations) == 1


def test_program_with_mixed_block_styles():
    """Test program with mixed block styles."""
    source = """
int function test1() {
    return 1
}

int function test2()
    return 2

int function test3()
    return 3
End function
"""
    program = parse_program(source)
    assert len(program.declarations) == 3


# ============================================================================
# Complex Programs
# ============================================================================

def test_program_with_default_parameters():
    """Test function with default parameter values."""
    source = """
void function greet(string name = "World", string greeting = "Hello") {
    print(greeting + ", " + name + "!")
}

int function main() {
    greet()
    greet("Alice")
    greet("Bob", "Hi")
    return 0
}
"""
    program = parse_program(source)

    greet_func = program.declarations[0]
    assert len(greet_func.parameters) == 2
    assert greet_func.parameters[0].default_value is not None
    assert greet_func.parameters[1].default_value is not None


def test_program_with_nested_loops():
    """Test program with nested loops."""
    source = """
void function printMatrix(int rows, int cols) {
    for i in range(0, rows) {
        for j in range(0, cols) {
            print(i * cols + j)
        }
    }
}
"""
    program = parse_program(source)

    func = program.declarations[0]
    outer_loop = func.body.statements[0]
    assert isinstance(outer_loop, ForStmt)
    inner_loop = outer_loop.body.statements[0]
    assert isinstance(inner_loop, ForStmt)


def test_program_with_multiple_returns():
    """Test function with multiple return paths."""
    source = """
string function classify(int x) {
    if x < 0 {
        return "negative"
    } else if x == 0 {
        return "zero"
    } else {
        return "positive"
    }
}
"""
    program = parse_program(source)

    func = program.declarations[0]
    assert func.return_type.name == "string"


def test_program_with_complex_expressions():
    """Test program with complex nested expressions."""
    source = """
int function complex(int a, int b, int c) {
    return (a + b) * c - (a * b) / (c + 1) + 42
}
"""
    program = parse_program(source)

    func = program.declarations[0]
    ret_stmt = func.body.statements[0]
    assert isinstance(ret_stmt, ReturnStmt)
    assert isinstance(ret_stmt.value, BinaryExpr)


# ============================================================================
# Edge Cases
# ============================================================================

def test_empty_main_function():
    """Test parsing empty main function."""
    source = """
int function main() {
    return 0
}
"""
    program = parse_program(source)
    assert len(program.declarations) == 1


def test_function_with_no_return():
    """Test void function with no return statement."""
    source = """
void function doNothing() {
    int x = 0
}
"""
    program = parse_program(source)
    func = program.declarations[0]
    assert func.return_type.name == "void"


def test_single_line_lambda():
    """Test ultra-compact single-line lambda."""
    source = "int function id(int x) : x"

    program = parse_program(source)
    func = program.declarations[0]
    assert func.is_lambda
    assert func.name == "id"


def test_program_with_comments():
    """Test program with comments (handled by lexer)."""
    source = """
// This is a comment
int function main() {
    // Return success
    return 0
}
"""
    program = parse_program(source)
    # Comments are stripped by lexer
    assert len(program.declarations) == 1


def test_program_with_all_types():
    """Test program using all MVP primitive types."""
    source = """
void function test() {
    int a = 1
    float b = 2.5
    double c = 3.14159
    string d = "text"
    bool e = true
    char f = 'x'
}
"""
    program = parse_program(source)

    func = program.declarations[0]
    assert len(func.body.statements) == 6
    # Verify all are variable declarations
    assert all(isinstance(stmt, VarDeclStmt) for stmt in func.body.statements)


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_error_missing_closing_brace():
    """Test error on missing closing brace."""
    source = """
int function test() {
    return 42
"""  # Missing }

    with pytest.raises(ParserError) as exc_info:
        parse_program(source)
    assert "Expected" in str(exc_info.value) or "Unexpected" in str(exc_info.value)


def test_error_missing_function_body():
    """Test error on function without body."""
    source = "int function test()"

    with pytest.raises(ParserError):
        parse_program(source)


def test_error_invalid_top_level():
    """Test error on invalid top-level statement."""
    source = "return 42"  # Return at top level

    with pytest.raises(ParserError) as exc_info:
        parse_program(source)
    assert "Unexpected token" in str(exc_info.value)


def test_error_unclosed_parenthesis():
    """Test error on unclosed parenthesis."""
    source = """
int function test() {
    return (1 + 2
}
"""

    with pytest.raises(ParserError) as exc_info:
        parse_program(source)
    assert "Expected ')'" in str(exc_info.value)


def test_error_missing_parameter_type():
    """Test error on missing parameter type."""
    source = "int function test(x) { return x }"  # Missing type for x

    with pytest.raises(ParserError):
        parse_program(source)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
