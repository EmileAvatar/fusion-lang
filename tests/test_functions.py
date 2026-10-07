"""Tests for Task 18.1 - functions with full parameter support.

18.1.1: default parameter values (trailing-only, constant-only, filled in at each C call site)
18.1.2: arrays as function parameters (`int[]` any size via a hidden length, `int[N]` exact
        size; passed by reference)
"""

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator
from tests.test_end_to_end import compile_and_run


def analyze(source: str):
    """Run semantic analysis; return (analyzer, ast, ok)."""
    ast = Parser(Lexer(source, "test.fusion").tokenize()).parse_program()
    analyzer = SemanticAnalyzer()
    ok = analyzer.analyze(ast)
    return analyzer, ast, ok


def errors_of(source: str) -> str:
    analyzer, _, ok = analyze(source)
    assert not ok, "expected semantic errors"
    return "\n".join(str(e) for e in analyzer.get_errors())


def generate_c(source: str) -> str:
    analyzer, ast, ok = analyze(source)
    assert ok, analyzer.get_errors()
    return CCodeGenerator().generate(ast)


# ============================================================
# 18.1.1 - Default parameter values
# ============================================================

GREET = (
    'void function greet(string name = "World", int times = 1)\n'
    '    for i in range(0, times)\n'
    '        print("Hello, {name}!")\n'
)


def test_omitted_default_is_filled_at_call_site():
    c_code = generate_c(GREET + 'void function main()\n    greet()\n    greet("Fusion")\n')
    assert 'greet("World", 1);' in c_code
    assert 'greet("Fusion", 1);' in c_code


def test_all_arguments_given_uses_none_of_the_defaults():
    c_code = generate_c(GREET + 'void function main()\n    greet("x", 3)\n')
    assert 'greet("x", 3);' in c_code


def test_negative_number_default():
    c_code = generate_c(
        'int function offset(int x, int by = -5) : x + by\n'
        'void function main()\n    int a = offset(10)\n'
    )
    assert 'offset(10, (-5))' in c_code


@pytest.mark.parametrize("default", ['2.5', '"text"', "'c'", 'true', 'false', '-1.5'])
def test_constant_defaults_accepted(default):
    type_name = {'2.5': 'float', '"text"': 'string', "'c'": 'char',
                 'true': 'bool', 'false': 'bool', '-1.5': 'float'}[default]
    _, _, ok = analyze(
        f'void function f({type_name} v = {default})\n    return\n'
        'void function main()\n    f()\n'
    )
    assert ok


def test_too_few_arguments_reports_range():
    message = errors_of(
        'int function f(int a, int b = 2) : a + b\nvoid function main()\n    int x = f()\n'
    )
    assert "expects 1 to 2 arguments, got 0" in message


def test_too_many_arguments_reports_range():
    message = errors_of(
        'int function f(int a, int b = 2) : a + b\nvoid function main()\n    int x = f(1, 2, 3)\n'
    )
    assert "expects 1 to 2 arguments, got 3" in message


def test_no_defaults_keeps_exact_count_message():
    message = errors_of(
        'int function f(int a) : a\nvoid function main()\n    int x = f()\n'
    )
    assert "expects 1 argument(s), got 0" in message


def test_parameter_without_default_after_one_with_default_rejected():
    message = errors_of(
        'int function f(int a = 1, int b) : a + b\nvoid function main()\n    int x = f(1, 2)\n'
    )
    assert "Parameter 'b' needs a default value" in message
    assert "defaults must come last" in message


@pytest.mark.parametrize("default", ['a', 'a + 1', 'null', '"x{a}"'])
def test_non_constant_default_rejected(default):
    type_name = 'string' if default in ('null', '"x{a}"') else 'int'
    message = errors_of(
        f'void function f(int a, {type_name} b = {default})\n    return\n'
        'void function main()\n    f(1)\n'
    )
    assert "must be a constant" in message


def test_default_type_mismatch_still_rejected():
    message = errors_of(
        'void function f(int a = "no")\n    return\nvoid function main()\n    f()\n'
    )
    assert "Default value type" in message


def test_call_before_definition_gets_defaults():
    # main calls greet before greet is declared - registration happens in an earlier pass
    c_code = generate_c('void function main()\n    greet()\n' + GREET)
    assert 'greet("World", 1);' in c_code


def test_defaults_end_to_end():
    exit_code, stdout, stderr = compile_and_run(
        GREET +
        'int function offset(int x, int by = -5) : x + by\n'
        'void function main()\n'
        '    greet()\n'
        '    greet("twice", 2)\n'
        '    int a = offset(10)\n'
        '    int b = offset(10, 2)\n'
        '    print("{a} {b}")\n'
    )
    assert exit_code == 0, stderr
    assert stdout.splitlines() == ["Hello, World!", "Hello, twice!", "Hello, twice!", "5 12"]


# ============================================================
# 18.1.2 - Arrays as function parameters
# ============================================================

SUM = (
    'int function sum(int[] values)\n'
    '    int total = 0\n'
    '    for i in range(0, len(values))\n'
    '        total = total + values[i]\n'
    '    return total\n'
)


def test_unsized_array_parameter_gets_hidden_length():
    c_code = generate_c(SUM + 'void function main()\n    int[] a = [1, 2, 3]\n    int s = sum(a)\n')
    assert 'int sum(int* values, int fusion_len_values);' in c_code   # forward declaration
    assert 'int sum(int* values, int fusion_len_values) {' in c_code  # definition
    assert 'sum(a, 3)' in c_code
    assert 'i < fusion_len_values' in c_code                            # len(values)


def test_sized_array_parameter_stays_c_array():
    c_code = generate_c(
        'int function first(int[3] trio) : trio[0] + len(trio)\n'
        'void function main()\n    int[] a = [1, 2, 3]\n    int f = first(a)\n'
    )
    assert 'int first(int trio[3])' in c_code
    assert '(trio[0] + 3)' in c_code      # len of a sized parameter is still a constant
    assert 'first(a)' in c_code


def test_unsized_parameter_forwarded_with_its_length():
    c_code = generate_c(
        SUM + 'int function again(int[] v) : sum(v)\nvoid function main()\n    return\n'
    )
    assert 'sum(v, fusion_len_v)' in c_code


def test_array_literal_argument_becomes_compound_literal():
    c_code = generate_c(SUM + 'void function main()\n    int s = sum([7, 8])\n')
    assert 'sum((int[]){7, 8}, 2)' in c_code


def test_string_array_parameter():
    c_code = generate_c(
        'string function pick(string[] names) : names[0]\n'
        'void function main()\n    string[] n = ["a", "b"]\n    string p = pick(n)\n'
    )
    assert 'char** names, int fusion_len_names' in c_code
    assert 'pick(n, 2)' in c_code


def test_sized_parameter_rejects_wrong_size():
    message = errors_of(
        'int function first(int[3] trio) : trio[0]\n'
        'void function main()\n    int[] a = [1, 2]\n    int f = first(a)\n'
    )
    assert "expected an array of exactly 3 elements, got 2" in message


def test_sized_parameter_rejects_unsized_forward():
    message = errors_of(
        'int function first(int[3] trio) : trio[0]\n'
        'int function pass(int[] v) : first(v)\n'
    )
    assert "only known at run time" in message


def test_array_element_types_must_match_exactly():
    # No int -> float promotion: C can't read an int array's memory as floats
    message = errors_of(
        'float function total(float[] v) : v[0]\n'
        'void function main()\n    int[] a = [1, 2]\n    float t = total(a)\n'
    )
    assert "element types must match exactly" in message


def test_non_array_argument_to_array_parameter_rejected():
    message = errors_of(SUM + 'void function main()\n    int s = sum(5)\n')
    assert "expected int[], got int" in message


def test_empty_array_literal_argument_rejected():
    message = errors_of(SUM + 'void function main()\n    int s = sum([])\n')
    assert "empty array literal" in message


def test_const_array_argument_rejected():
    message = errors_of(
        SUM + 'void function main()\n    const int[] a = [1, 2]\n    int s = sum(a)\n'
    )
    assert "const array 'a' can't be passed" in message


def test_array_return_type_still_rejected():
    message = errors_of('int[] function make()\n    int[] a = [1]\n    return a\n')
    assert "not yet supported as function return types" in message


def test_array_default_value_rejected():
    message = errors_of('int function f(int[] v = [1])\n    return 0\n')
    assert "can't have a default value" in message


def test_array_initialized_from_another_array_rejected():
    # Used to pass semantic analysis and then fail in GCC: `int b[3] = a;` is invalid C
    message = errors_of('void function main()\n    int[] a = [1, 2, 3]\n    int[] b = a\n')
    assert "must be initialized with an array literal" in message


def test_array_parameters_end_to_end():
    exit_code, stdout, stderr = compile_and_run(
        SUM +
        'void function double_all(int[] values)\n'
        '    for i in range(0, len(values))\n'
        '        values[i] = values[i] * 2\n'
        'int function first(int[3] trio) : trio[0]\n'
        'void function main()\n'
        '    int[] a = [1, 2, 3]\n'
        '    int[] b = [10, 20, 30, 40, 50]\n'
        '    int s1 = sum(a)\n'
        '    int s2 = sum(b)\n'
        '    int s3 = sum([7, 8])\n'
        '    double_all(a)\n'
        '    int s4 = sum(a)\n'
        '    int f = first(a)\n'
        '    print("{s1} {s2} {s3} {s4} {f}")\n'
    )
    assert exit_code == 0, stderr
    # double_all changed the caller's array: arrays are passed by reference
    assert stdout.strip() == "6 150 15 12 2"
