"""Test semantic analysis of const declarations.

Tests const variable validation:
- const variables must have initializers
- const variables cannot be reassigned
- const variables can be used in expressions
"""

import pytest
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.semantic_analyzer import SemanticAnalyzer


def analyze_code(code: str):
    """Helper to perform full semantic analysis."""
    lexer = Lexer(code, "test.fusion")
    parser = Parser(list(lexer.tokenize()))
    program = parser.parse_program()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)

    return analyzer.get_errors(), analyzer.symbol_table


def test_const_with_initializer():
    """Test const with initializer is valid."""
    code = """
void function main()
    const int x = 5
End function
"""
    errors, symbol_table = analyze_code(code)

    # Should have no errors
    assert len(errors) == 0, f"Expected no errors, got: {errors}"

    print("[OK] const int x = 5 is valid")


def test_const_without_initializer_fails():
    """Test const without initializer raises error."""
    code = """
void function test()
    const int x
End function
"""
    # This should fail at parse time, not semantic analysis
    # But we'll test it anyway for completeness
    with pytest.raises(Exception) as exc_info:
        lexer = Lexer(code, "test.fusion")
        parser = Parser(list(lexer.tokenize()))
        parser.parse_program()

    assert "must have an initializer" in str(exc_info.value)
    print("[OK] const without initializer fails at parse time")


def test_const_reassignment_fails():
    """Test that reassigning to const raises error."""
    code = """
void function main()
    const int x = 5
    x = 10
End function
"""
    errors, symbol_table = analyze_code(code)

    # Should have error about const reassignment
    assert len(errors) > 0, "Expected error for const reassignment"

    error_messages = [str(e) for e in errors]
    assert any("Cannot assign to constant" in msg for msg in error_messages), \
        f"Expected 'Cannot assign to constant' error, got: {error_messages}"

    print("[OK] const reassignment error detected")


def test_const_in_expression():
    """Test const can be used in expressions."""
    code = """
int function main()
    const int BASE = 10
    const int MULTIPLIER = 2
    int result = BASE * MULTIPLIER
    return result
End function
"""
    errors, symbol_table = analyze_code(code)

    # Should have no errors
    assert len(errors) == 0, f"Expected no errors, got: {errors}"

    print("[OK] const variables used in expressions")


def test_multiple_const_declarations():
    """Test multiple const declarations."""
    code = """
void function main()
    const int MAX = 100
    const float PI = 3.14
    const string NAME = "Fusion"
    int sum = MAX + 1
End function
"""
    errors, symbol_table = analyze_code(code)

    # Should have no errors
    assert len(errors) == 0, f"Expected no errors, got: {errors}"

    print("[OK] Multiple const declarations valid")


def test_regular_var_can_be_reassigned():
    """Test that regular variables can still be reassigned."""
    code = """
void function main()
    int x = 5
    x = 10
    x = 15
End function
"""
    errors, symbol_table = analyze_code(code)

    # Should have no errors
    assert len(errors) == 0, f"Expected no errors, got: {errors}"

    print("[OK] Regular variables can be reassigned")


def test_const_shadowing_different_scope():
    """Test const in different functions (different scopes)."""
    code = """
void function main()
    int x = 0
End function

void function func1()
    const int VALUE = 100
End function

void function func2()
    const int VALUE = 200
End function
"""
    errors, symbol_table = analyze_code(code)

    # Should have no errors (different scopes)
    assert len(errors) == 0, f"Expected no errors, got: {errors}"

    print("[OK] const in different scopes is valid")


def test_const_then_var_same_name_fails():
    """Test declaring const then var with same name fails."""
    code = """
void function main()
    const int x = 5
    int x = 10
End function
"""
    errors, symbol_table = analyze_code(code)

    # Should have error about duplicate declaration
    assert len(errors) > 0, "Expected error for duplicate declaration"

    error_messages = [str(e) for e in errors]
    assert any("Duplicate declaration" in msg for msg in error_messages), \
        f"Expected duplicate declaration error, got: {error_messages}"

    print("[OK] const then var with same name fails")


if __name__ == "__main__":
    test_const_with_initializer()
    test_const_without_initializer_fails()
    test_const_reassignment_fails()
    test_const_in_expression()
    test_multiple_const_declarations()
    test_regular_var_can_be_reassigned()
    test_const_shadowing_different_scope()
    test_const_then_var_same_name_fails()

    print("\n[ALL TESTS PASSED]")
