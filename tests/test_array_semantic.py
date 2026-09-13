"""Test parsing and semantic analysis of array declarations, indexing, and len().

Tests Task 9 v1 array support:
- Fixed-size arrays with an explicit size ([N]), an inferred size (from an array
  literal), or both (must agree)
- Element read/write via arr[i]
- len(arr) as a compile-time-resolved builtin
- Deferred-feature rejections: arrays as function parameters/return types,
  multi-dimensional arrays, whole-array reassignment
"""

import pytest
from src.lexer.lexer import Lexer
from src.parser.parser import Parser, ParserError
from src.semantic.semantic_analyzer import SemanticAnalyzer


def analyze_code(code: str):
    """Helper to perform full semantic analysis."""
    lexer = Lexer(code, "test.fusion")
    parser = Parser(list(lexer.tokenize()))
    program = parser.parse_program()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)

    return analyzer.get_errors(), analyzer.symbol_table


def parse_code(code: str):
    """Helper to parse without running semantic analysis (for parser-level checks)."""
    lexer = Lexer(code, "test.fusion")
    parser = Parser(list(lexer.tokenize()))
    return parser.parse_program()


def assert_no_errors(errors):
    assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"


def assert_error_contains(errors, text):
    assert len(errors) > 0, f"Expected an error containing {text!r}, got none"
    messages = [str(e) for e in errors]
    assert any(text in msg for msg in messages), \
        f"Expected an error containing {text!r}, got: {messages}"


def test_array_literal_with_inferred_size():
    """int[] arr = [1, 2, 3] - size inferred from the literal."""
    code = """
void function main()
    int[] arr = [1, 2, 3]
End function
"""
    assert_no_errors(analyze_code(code)[0])


def test_array_explicit_size_matches_literal():
    """int[3] arr = [1, 2, 3] - explicit size agrees with the literal."""
    code = """
void function main()
    int[3] arr = [1, 2, 3]
End function
"""
    assert_no_errors(analyze_code(code)[0])


def test_array_size_mismatch_fails():
    """int[5] arr = [1, 2, 3] - explicit size disagrees with the literal."""
    code = """
void function main()
    int[5] arr = [1, 2, 3]
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "declared with size 5 but initializer has 3")


def test_array_no_size_no_initializer_fails():
    """int[] arr with neither an explicit size nor an initializer is ambiguous."""
    code = """
void function main()
    int[] arr
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "must specify a size")


def test_array_explicit_size_no_initializer_ok():
    """int[5] arr with no initializer is valid - zero-initialized."""
    code = """
void function main()
    int[5] arr
End function
"""
    assert_no_errors(analyze_code(code)[0])


def test_array_index_read():
    """arr[0] used as a read is valid."""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    int x = arr[0]
End function
"""
    assert_no_errors(analyze_code(code)[0])


def test_array_index_write():
    """arr[0] = value is valid."""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    arr[0] = 99
End function
"""
    assert_no_errors(analyze_code(code)[0])


def test_array_index_write_type_mismatch_fails():
    """Assigning a string into an int array element must fail."""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    arr[0] = "hello"
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "Cannot assign string to array element of type int")


def test_array_index_must_be_int():
    """Indexing with a non-int expression must fail."""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    int x = arr[true]
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "Array index must be int")


def test_index_non_array_fails():
    """Indexing a non-array type must fail."""
    code = """
void function main()
    int x = 5
    int y = x[0]
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "Cannot index non-array type")


def test_whole_array_reassignment_fails():
    """arr = [...] after declaration is rejected - only element assignment is supported."""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    arr = [4, 5, 6]
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "Cannot reassign array 'arr' as a whole")


def test_const_array_element_assignment_fails():
    """Assigning into an element of a const array is a const violation."""
    code = """
void function main()
    const int[] arr = [1, 2, 3]
    arr[0] = 99
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "Cannot assign to element of constant array")


def test_const_array_without_reassignment_is_valid():
    """A const array that's only read is valid."""
    code = """
int function main()
    const int[] arr = [1, 2, 3]
    return arr[0]
End function
"""
    assert_no_errors(analyze_code(code)[0])


def test_len_builtin_valid():
    """len(arr) on an array is valid and returns int."""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    int n = len(arr)
End function
"""
    assert_no_errors(analyze_code(code)[0])


def test_len_on_non_array_fails():
    """len() on a non-array argument must fail."""
    code = """
void function main()
    int n = len(5)
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "Function 'len' expects an array")


def test_len_wrong_arg_count_fails():
    """len() with the wrong number of arguments must fail."""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    int n = len(arr, arr)
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "Function 'len' expects 1 argument")


def test_array_element_type_mismatch_fails():
    """Inconsistent element types in a literal must fail."""
    code = """
void function main()
    int[] arr = [1, "two", 3]
End function
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "Array elements must have consistent types")


def test_float_array_accepts_int_literal_promotion():
    """float[] arr = [1, 2, 3.5] - int literals promote to float, like elsewhere."""
    code = """
void function main()
    float[] arr = [1, 2, 3.5]
End function
"""
    assert_no_errors(analyze_code(code)[0])


def test_array_as_function_parameter_fails():
    """Arrays as function parameters are deferred (Task 9 v1 is local-only)."""
    code = """
int function sum(int[] arr)
    return arr[0]
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "not yet supported as function parameters")


def test_array_as_return_type_fails():
    """Arrays as function return types are deferred (Task 9 v1 is local-only)."""
    code = """
int[] function makeArray()
    int[] arr = [1, 2, 3]
    return arr
"""
    errors, _ = analyze_code(code)
    assert_error_contains(errors, "not yet supported as function return types")


def test_multi_dimensional_array_rejected_at_parse():
    """int[][] is not yet supported - should fail to parse with a clear message."""
    code = """
void function main()
    int[][] arr
End function
"""
    with pytest.raises(ParserError) as exc_info:
        parse_code(code)
    assert "Multi-dimensional arrays are not yet supported" in str(exc_info.value)


def test_array_size_must_be_integer_literal():
    """int[n] with a non-literal size expression is not yet supported."""
    code = """
void function main()
    int n = 5
    int[n] arr
End function
"""
    with pytest.raises(ParserError):
        parse_code(code)
