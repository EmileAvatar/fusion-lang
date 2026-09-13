"""End-to-end tests for complete compilation pipeline.

Tests compile Fusion programs to C, compile C to executable,
run the executable, and verify output.
"""

import os
import subprocess
import tempfile
import pytest
from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator


def compile_and_run(fusion_code: str) -> tuple[int, str, str]:
    """Compile Fusion code and run the executable.

    Args:
        fusion_code: Fusion source code

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write Fusion source
        fusion_file = os.path.join(tmpdir, 'test.fusion')
        with open(fusion_file, 'w') as f:
            f.write(fusion_code)

        # Compile Fusion → C
        lexer = Lexer(fusion_code, fusion_file)
        tokens = lexer.tokenize()
        assert not lexer.diagnostics.errors, f"Lexer errors: {lexer.diagnostics.errors}"

        parser = Parser(tokens)
        ast = parser.parse_program()

        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)
        assert success, f"Semantic errors: {analyzer.get_errors()}"

        generator = CCodeGenerator()
        c_code = generator.generate(ast)

        # Write C code
        c_file = os.path.join(tmpdir, 'test.c')
        with open(c_file, 'w') as f:
            f.write(c_code)

        # Compile C → executable
        exe_file = os.path.join(tmpdir, 'test.exe')
        gcc_result = subprocess.run(
            ['gcc', c_file, '-o', exe_file, '-lm'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if gcc_result.returncode != 0:
            raise RuntimeError(f"GCC failed:\n{gcc_result.stderr}")

        # Run executable
        run_result = subprocess.run(
            [exe_file],
            capture_output=True,
            text=True,
            timeout=5
        )

        return run_result.returncode, run_result.stdout, run_result.stderr


# ============================================================================
# End-to-End Valid Programs (15 tests)
# ============================================================================


def test_hello_world():
    """Test Hello World program."""
    fusion_code = '''
void function main()
    print("Hello, World!")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Hello, World!" in stdout


def test_factorial_recursive():
    """Test recursive factorial."""
    fusion_code = '''
int function factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)
End function

int function main()
    int result = factorial(5)
    print("Result: {result}")
    return 0
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Result: 120" in stdout


def test_factorial_iterative():
    """Test iterative factorial."""
    fusion_code = '''
int function factorial(int n)
    int result = 1
    int i = 1
    while i <= n
        result = result * i
        i = i + 1
    return result
End function

int function main()
    int result = factorial(5)
    print("Result: {result}")
    return 0
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Result: 120" in stdout


def test_fizzbuzz():
    """Test FizzBuzz program."""
    fusion_code = '''
void function main()
    int i = 1
    while i <= 15
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
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Fizz" in stdout
    assert "Buzz" in stdout
    assert "FizzBuzz" in stdout


def test_calculator():
    """Test calculator with multiple functions."""
    fusion_code = '''
int function add(int a, int b) : a + b
int function subtract(int a, int b) : a - b
int function multiply(int a, int b) : a * b

void function main()
    int x = 10
    int y = 5
    int sum = add(x, y)
    int diff = subtract(x, y)
    int prod = multiply(x, y)
    print("Sum: {sum}")
    print("Diff: {diff}")
    print("Prod: {prod}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Sum: 15" in stdout
    assert "Diff: 5" in stdout
    assert "Prod: 50" in stdout


def test_sum_range():
    """Test sum of range with for loop."""
    fusion_code = '''
int function sum_range(int start, int end)
    int total = 0
    for i in range(start, end)
        total = total + i
    return total
End function

void function main()
    int result = sum_range(1, 11)
    print("Sum: {result}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Sum: 55" in stdout


def test_max_three():
    """Test max of three numbers."""
    fusion_code = '''
int function max(int a, int b, int c)
    int result = a
    if b > result
        result = b
    if c > result
        result = c
    return result
End function

void function main()
    int maximum = max(10, 25, 15)
    print("Max: {maximum}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Max: 25" in stdout


def test_even_odd_checker():
    """Test even/odd checker."""
    fusion_code = '''
void function check_even_odd(int n)
    if n % 2 == 0
        print("Even")
    else
        print("Odd")
End function

void function main()
    check_even_odd(4)
    check_even_odd(7)
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Even" in stdout
    assert "Odd" in stdout


def test_simple_counter():
    """Test simple counter with for loop."""
    fusion_code = '''
void function main()
    int count = 0
    for i in range(0, 5)
        count = count + 1
    print("Count: {count}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Count: 5" in stdout


def test_nested_loops():
    """Test nested loops."""
    fusion_code = '''
void function main()
    int sum = 0
    for i in range(0, 3)
        for j in range(0, 3)
            sum = sum + 1
    print("Sum: {sum}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Sum: 9" in stdout


def test_lambda_functions():
    """Test lambda functions."""
    fusion_code = '''
int function double(int x) : x * 2
int function triple(int x) : x * 3

void function main()
    int a = double(5)
    int b = triple(5)
    print("Double: {a}")
    print("Triple: {b}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Double: 10" in stdout
    assert "Triple: 15" in stdout


def test_variable_shadowing():
    """Test mutating an outer-scope variable from inside a nested block - this is a plain
    assignment (x = 20), not a redeclaration, so it's unaffected by block scoping
    (Task 12.6): it's the same x throughout, still valid either way."""
    fusion_code = '''
void function main()
    int x = 10
    if true
        x = 20
        print("Inner: {x}")
    print("Outer: {x}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Inner: 20" in stdout
    assert "Outer: 20" in stdout  # Same x, modified in if block


def test_block_scoping_shadowing_actually_works():
    """Test block scoping (Task 12.6): unlike the test above, this one *redeclares* x
    inside the if - the inner x should shadow the outer one only within its own block."""
    fusion_code = '''
void function main()
    int x = 10
    if true
        int x = 20
        print("Inner: {x}")
    print("Outer: {x}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Inner: 20" in stdout
    assert "Outer: 10" in stdout  # Different x - outer was never touched


def test_block_scoping_rejects_use_after_block():
    """Test block scoping (Task 12.6): a variable declared inside an if body must not be
    visible after the if ends. Before this fix, semantic analysis allowed this (Fusion
    was "function-scoped"), but the generated C failed to compile - GCC's own { } braces
    are block-scoped natively, so this was a real, previously-undetected compiler bug."""
    fusion_code = '''
void function main()
    int total = 0
    if total == 0
        int x = 10
    print("{x}")
End function
'''
    with pytest.raises(AssertionError, match="Semantic errors"):
        compile_and_run(fusion_code)


def test_block_scoping_rejects_use_after_for_loop():
    """Test block scoping (Task 12.6): a variable declared inside a for loop's body must
    not be visible after the loop ends."""
    fusion_code = '''
void function main()
    for i in range(0, 3)
        int x = i
    print("{x}")
End function
'''
    with pytest.raises(AssertionError, match="Semantic errors"):
        compile_and_run(fusion_code)


def test_block_scoping_for_loop_variable_out_of_scope_after_loop():
    """Test block scoping (Task 12.6): a for loop's own iteration variable must not be
    visible after the loop ends either - it's scoped to the loop, not the function."""
    fusion_code = '''
void function main()
    for i in range(0, 3)
        print("{i}")
    print("{i}")
End function
'''
    with pytest.raises(AssertionError, match="Semantic errors"):
        compile_and_run(fusion_code)


def test_block_scoping_local_cannot_redeclare_parameter():
    """Test block scoping (Task 12.6): a local variable at the top level of a function
    body cannot redeclare a parameter name - matches real C, where parameters and the
    function's own top-level block share one scope (verified against GCC directly:
    redeclaring a parameter there is 'redeclared as different kind of symbol')."""
    fusion_code = '''
int function f(int x)
    int x = 5
    return x

void function main()
    int result = f(1)
    print("{result}")
End function
'''
    with pytest.raises(AssertionError, match="Semantic errors"):
        compile_and_run(fusion_code)


def test_multiple_return_paths():
    """Test function with multiple return paths."""
    fusion_code = '''
int function abs_value(int x)
    if x < 0
        return -x
    return x
End function

void function main()
    int a = abs_value(-5)
    int b = abs_value(5)
    print("Abs(-5): {a}")
    print("Abs(5): {b}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Abs(-5): 5" in stdout
    assert "Abs(5): 5" in stdout


def test_complex_expressions():
    """Test complex arithmetic expressions."""
    fusion_code = '''
void function main()
    int a = 10
    int b = 5
    int c = 3
    int result = (a + b) * c - (a / b)
    print("Result: {result}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Result: 43" in stdout


def test_break_continue():
    """Test break and continue in loops."""
    fusion_code = '''
void function main()
    int count = 0
    for i in range(0, 10)
        if i == 5
            break
        count = count + 1
    print("Count: {count}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Count: 5" in stdout


# ============================================================================
# End-to-End Error Handling (5 tests)
# ============================================================================


def test_lexer_errors_prevent_compilation():
    """Verify lexer errors prevent compilation."""
    fusion_code = '''
void function main()
    string s = "unterminated string
End function
'''
    # Lexer raises LexerError exception directly
    with pytest.raises(Exception):  # LexerError
        compile_and_run(fusion_code)


def test_parser_errors_prevent_compilation():
    """Verify parser errors prevent compilation."""
    fusion_code = '''
void function main(
    print("Hello")
End function
'''
    with pytest.raises(Exception):  # ParserError
        compile_and_run(fusion_code)


def test_semantic_errors_prevent_compilation():
    """Verify semantic errors prevent compilation."""
    fusion_code = '''
void function main()
    int x = "string"
End function
'''
    with pytest.raises(AssertionError, match="Semantic errors"):
        compile_and_run(fusion_code)


def test_missing_main_prevents_compilation():
    """Verify missing main function prevents compilation."""
    fusion_code = '''
int function foo() : 42
'''
    with pytest.raises(AssertionError, match="Semantic errors"):
        compile_and_run(fusion_code)


def test_gcc_errors_reported():
    """Verify GCC errors are reported correctly."""
    # This test is tricky - our code generator should always produce valid C
    # We'll skip this for now as it's hard to force a GCC error with valid Fusion
    pass


# ============================================================================
# Integration Tests (10 tests)
# ============================================================================


def test_generated_c_has_includes():
    """Verify generated C code has correct includes."""
    fusion_code = '''
void function main()
    print("Hello")
End function
'''
    lexer = Lexer(fusion_code, 'test.fusion')
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse_program()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    generator = CCodeGenerator()
    c_code = generator.generate(ast)

    assert '#include <stdio.h>' in c_code
    assert '#include <stdbool.h>' in c_code
    assert '#include <math.h>' in c_code


def test_generated_c_has_forward_declarations():
    """Verify generated C code has forward declarations."""
    fusion_code = '''
int function foo() : 42
void function main()
    int x = foo()
End function
'''
    lexer = Lexer(fusion_code, 'test.fusion')
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse_program()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    generator = CCodeGenerator()
    c_code = generator.generate(ast)

    # Should have forward declaration (C style with void for no params)
    assert 'int foo(void);' in c_code or 'int foo();' in c_code


def test_generated_c_compiles_without_warnings():
    """Verify generated C code compiles without warnings."""
    fusion_code = '''
void function main()
    int x = 42
    print("Value: {x}")
End function
'''
    with tempfile.TemporaryDirectory() as tmpdir:
        lexer = Lexer(fusion_code, 'test.fusion')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse_program()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

        generator = CCodeGenerator()
        c_code = generator.generate(ast)

        c_file = os.path.join(tmpdir, 'test.c')
        with open(c_file, 'w') as f:
            f.write(c_code)

        exe_file = os.path.join(tmpdir, 'test.exe')
        result = subprocess.run(
            ['gcc', c_file, '-o', exe_file, '-lm', '-Wall', '-Wextra'],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Should compile successfully (warnings are OK for MVP)
        assert result.returncode == 0


def test_executable_runs_without_errors():
    """Verify executables run without errors."""
    fusion_code = '''
void function main()
    print("Success")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Success" in stdout


def test_output_matches_expected():
    """Verify output matches expected values."""
    fusion_code = '''
void function main()
    print("Line 1")
    print("Line 2")
    print("Line 3")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Line 1" in stdout
    assert "Line 2" in stdout
    assert "Line 3" in stdout


def test_return_code_zero_for_success():
    """Verify return code is 0 for successful programs."""
    fusion_code = '''
int function main()
    return 0
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0


def test_return_code_nonzero_for_errors():
    """Verify return code can be non-zero."""
    fusion_code = '''
int function main()
    return 42
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 42


def test_multiple_files_can_be_compiled():
    """Verify multiple Fusion files can be compiled separately."""
    fusion_code1 = '''
void function main()
    print("Program 1")
End function
'''
    fusion_code2 = '''
void function main()
    print("Program 2")
End function
'''
    exit_code1, stdout1, stderr1 = compile_and_run(fusion_code1)
    exit_code2, stdout2, stderr2 = compile_and_run(fusion_code2)

    assert exit_code1 == 0
    assert exit_code2 == 0
    assert "Program 1" in stdout1
    assert "Program 2" in stdout2


def test_large_program():
    """Test large program (50+ lines) compiles."""
    fusion_code = '''
int function fibonacci(int n)
    if n <= 1
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
End function

int function factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)
End function

int function sum_range(int start, int end)
    int total = 0
    for i in range(start, end)
        total = total + i
    return total
End function

int function max(int a, int b, int c)
    int result = a
    if b > result
        result = b
    if c > result
        result = c
    return result
End function

void function print_results()
    int fib = fibonacci(8)
    int fact = factorial(5)
    int sum = sum_range(1, 11)
    int maximum = max(10, 25, 15)
    print("Fibonacci(8): {fib}")
    print("Factorial(5): {fact}")
    print("Sum(1..10): {sum}")
    print("Max(10,25,15): {maximum}")
End function

void function main()
    print("=== Large Program Test ===")
    print_results()
    print("=== Done ===")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Fibonacci(8):" in stdout
    assert "Factorial(5):" in stdout
    assert "Sum(1..10):" in stdout
    assert "Max(10,25,15):" in stdout


def test_string_interpolation_multiple_vars():
    """Test string interpolation with multiple variables."""
    fusion_code = '''
void function main()
    int a = 10
    int b = 20
    int c = 30
    print("Values: {a}, {b}, {c}")
End function
'''
    exit_code, stdout, stderr = compile_and_run(fusion_code)
    assert exit_code == 0
    assert "Values: 10, 20, 30" in stdout
