"""Test code generation for const declarations.

Tests that:
- const declarations generate "const int x = 5;"
- Regular variables generate "int x = 5;"
- Generated C code compiles with GCC
- GCC catches const violations
"""

import pytest
import os
import tempfile
import subprocess
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.semantic_analyzer import SemanticAnalyzer
from src.codegen.c_generator import CCodeGenerator


def compile_and_generate(code: str):
    """Helper to compile Fusion code to C."""
    lexer = Lexer(code, "test.fusion")
    parser = Parser(list(lexer.tokenize()))
    program = parser.parse_program()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    if not success:
        errors = analyzer.get_errors()
        raise Exception(f"Semantic analysis failed: {errors}")

    generator = CCodeGenerator()
    c_code = generator.generate(program)

    return c_code


def test_const_declaration_generates_const_keyword():
    """Test that const declarations emit 'const' in C code."""
    code = """
void function main()
    const int x = 5
End function
"""
    c_code = compile_and_generate(code)

    # Check that "const int x = 5;" is in the generated code
    assert "const int x = (5);" in c_code or "const int x = 5;" in c_code, \
        f"Expected 'const int x = 5;' in generated C code, got:\n{c_code}"

    print("[OK] const int x = 5 generates 'const int x = 5;'")


def test_regular_var_no_const_keyword():
    """Test that regular variables don't have 'const' keyword."""
    code = """
void function main()
    int x = 5
End function
"""
    c_code = compile_and_generate(code)

    # Check that generated code has "int x = 5;" without const
    # (make sure const doesn't appear before this declaration)
    lines = c_code.split('\n')
    for line in lines:
        if 'int x =' in line and 'const' in line:
            raise AssertionError(f"Regular variable should not have const: {line}")

    assert 'int x = (5);' in c_code or 'int x = 5;' in c_code, \
        f"Expected 'int x = 5;' in generated C code"

    print("[OK] Regular int x = 5 generates 'int x = 5;' (no const)")


def test_multiple_const_declarations():
    """Test multiple const declarations generate correct C code."""
    code = """
void function main()
    const int MAX = 100
    const float PI = 3.14
    int sum = MAX + 1
End function
"""
    c_code = compile_and_generate(code)

    # Check for const declarations
    assert 'const int MAX' in c_code, f"Expected 'const int MAX' in C code"
    assert 'const float PI' in c_code or 'const double PI' in c_code, \
        f"Expected 'const float/double PI' in C code"

    # Check that sum is not const
    assert 'int sum' in c_code, f"Expected 'int sum' (non-const) in C code"

    # Make sure sum doesn't have const
    lines = c_code.split('\n')
    for line in lines:
        if 'int sum' in line and 'const' in line:
            raise AssertionError(f"sum should not be const: {line}")

    print("[OK] Multiple const declarations generate correct C code")


def test_const_code_compiles_with_gcc():
    """Test that generated C code with const compiles with GCC."""
    code = """
int function main()
    const int x = 5
    return x
End function
"""
    c_code = compile_and_generate(code)

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        c_file = f.name
        f.write(c_code)

    try:
        # Try to compile with GCC
        exe_file = c_file.replace('.c', '.exe')
        result = subprocess.run(
            ['gcc', c_file, '-o', exe_file, '-std=c11'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            raise AssertionError(
                f"GCC compilation failed:\n{result.stderr}\n\nC code:\n{c_code}"
            )

        print("[OK] Generated C code with const compiles successfully")

        # Clean up executable
        if os.path.exists(exe_file):
            os.remove(exe_file)

    finally:
        # Clean up C file
        if os.path.exists(c_file):
            os.remove(c_file)


def test_gcc_catches_const_violation():
    """Test that GCC catches const reassignment violations."""
    # This Fusion code should be rejected by semantic analysis
    # But if we manually generate invalid C code, GCC should catch it

    invalid_c_code = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

int main() {
    const int x = 5;
    x = 10;  // This should cause GCC error
    return 0;
}
"""

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        c_file = f.name
        f.write(invalid_c_code)

    try:
        # Try to compile with GCC - should fail
        exe_file = c_file.replace('.c', '.exe')
        result = subprocess.run(
            ['gcc', c_file, '-o', exe_file, '-std=c11'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should have failed
        assert result.returncode != 0, \
            "Expected GCC to reject const reassignment, but it succeeded"

        # Check error message mentions const or assignment
        assert 'const' in result.stderr.lower() or 'assignment' in result.stderr.lower() or 'read-only' in result.stderr.lower(), \
            f"Expected GCC error about const, got: {result.stderr}"

        print("[OK] GCC correctly rejects const reassignment")

    finally:
        # Clean up
        if os.path.exists(c_file):
            os.remove(c_file)


def test_const_in_expression():
    """Test const variables can be used in expressions."""
    code = """
int function main()
    const int BASE = 10
    const int MULTIPLIER = 2
    int result = BASE * MULTIPLIER
    return result
End function
"""
    c_code = compile_and_generate(code)

    # Check const declarations
    assert 'const int BASE' in c_code
    assert 'const int MULTIPLIER' in c_code

    # Check that result uses BASE and MULTIPLIER
    assert 'BASE' in c_code and 'MULTIPLIER' in c_code

    print("[OK] const variables used in expressions generate correct C code")


if __name__ == "__main__":
    test_const_declaration_generates_const_keyword()
    test_regular_var_no_const_keyword()
    test_multiple_const_declarations()
    test_const_code_compiles_with_gcc()
    test_gcc_catches_const_violation()
    test_const_in_expression()

    print("\n[ALL TESTS PASSED]")
