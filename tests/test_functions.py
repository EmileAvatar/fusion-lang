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
    assert 'fu_greet(FUSION_STR("World"), 1);' in c_code
    assert 'fu_greet(FUSION_STR("Fusion"), 1);' in c_code


def test_all_arguments_given_uses_none_of_the_defaults():
    c_code = generate_c(GREET + 'void function main()\n    greet("x", 3)\n')
    assert 'fu_greet(FUSION_STR("x"), 3);' in c_code


def test_negative_number_default():
    c_code = generate_c(
        'int function offset(int x, int by = -5) : x + by\n'
        'void function main()\n    int a = offset(10)\n'
    )
    assert 'fu_offset(10, (-5))' in c_code


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
    assert 'fu_greet(FUSION_STR("World"), 1);' in c_code


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
    assert 'int fu_sum(int* values, int fusion_len_values);' in c_code   # forward declaration
    assert 'int fu_sum(int* values, int fusion_len_values) {' in c_code  # definition
    assert 'fu_sum(a, 3)' in c_code
    assert 'i < fusion_len_values' in c_code                            # len(values)


def test_sized_array_parameter_stays_c_array():
    c_code = generate_c(
        'int function first(int[3] trio) : trio[0] + len(trio)\n'
        'void function main()\n    int[] a = [1, 2, 3]\n    int f = first(a)\n'
    )
    assert 'int fu_first(int trio[3])' in c_code
    assert '(trio[0] + 3)' in c_code      # len of a sized parameter is still a constant
    assert 'fu_first(a)' in c_code


def test_unsized_parameter_forwarded_with_its_length():
    c_code = generate_c(
        SUM + 'int function again(int[] v) : sum(v)\nvoid function main()\n    return\n'
    )
    assert 'fu_sum(v, fusion_len_v)' in c_code


def test_array_literal_argument_becomes_compound_literal():
    c_code = generate_c(SUM + 'void function main()\n    int s = sum([7, 8])\n')
    assert 'fu_sum((int[]){7, 8}, 2)' in c_code


def test_string_array_parameter():
    c_code = generate_c(
        'string function pick(string[] names) : names[0]\n'
        'void function main()\n    string[] n = ["a", "b"]\n    string p = pick(n)\n'
    )
    assert 'fusion_string* names, int fusion_len_names' in c_code
    assert 'fu_pick(n, 2)' in c_code


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


def test_unsized_array_return_type_rejected():
    # Sized array returns (int[1]) work since Task 18.2.4 - see tests/test_structs.py
    message = errors_of('int[] function make()\n    int[] a = [1]\n    return a\n')
    assert "returns an array, so its return type needs a size" in message


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


# ============================================================
# 18.1.3 - Lambdas v1 (no closures)
# ============================================================

def test_function_type_parses_with_colon_and_arrow():
    for type_text in ('(int, int) : int', '(int, int) -> int'):
        c_code = generate_c(
            f'void function main()\n    {type_text} add = func(int a, int b) : a + b\n'
        )
        assert 'typedef int (*fusion_fn_1)(int, int);' in c_code
        assert 'fusion_fn_1 add = fusion_lambda_1;' in c_code


def test_lambda_is_lifted_to_static_function_with_inferred_return_type():
    c_code = generate_c('void function main()\n    (int) : int op = func(int x) : x * 2\n')
    assert 'static int fusion_lambda_1(int x) {' in c_code
    assert 'return (x * 2);' in c_code
    assert '<lambda>' not in c_code  # the old placeholder is gone


def test_all_three_lambda_spellings():
    c_code = generate_c(
        'void function main()\n'
        '    (int) : int a = func(int x) : x\n'
        '    (int) : int b = function(int x) : x\n'
        '    (int) : int c = (int x) : x\n'
    )
    assert 'fusion_lambda_3' in c_code


def test_named_function_as_value_and_call_through_variable():
    c_code = generate_c(
        'int function tripler(int x) : x * 3\n'
        'void function main()\n    (int) : int op = tripler\n    int a = op(5)\n'
    )
    assert 'fusion_fn_1 op = fu_tripler;' in c_code
    assert 'int a = op(5);' in c_code


def test_function_named_after_c_keyword_used_as_value_is_mangled():
    c_code = generate_c(
        'int function double(int x) : x * 2\n'
        'void function main()\n    (int) : int op = double\n'
    )
    assert 'fusion_fn_1 op = fu_double;' in c_code


def test_function_returning_a_function():
    c_code = generate_c(
        'int function tripler(int x) : x * 3\n'
        '(int) : int function pick() : tripler\n'
        'void function main()\n    (int) : int f = pick()\n'
    )
    assert 'fusion_fn_1 fu_pick(void);' in c_code


def test_void_lambda():
    exit_code, stdout, stderr = compile_and_run(
        'void function each(int n, (int) : void action)\n'
        '    for i in range(0, n)\n'
        '        action(i)\n'
        'void function main()\n'
        '    each(3, func(int i) : print("item {i}"))\n'
    )
    assert exit_code == 0, stderr
    assert stdout.splitlines() == ["item 0", "item 1", "item 2"]


def test_nested_lambda_lifted_before_its_user():
    c_code = generate_c(
        'int function apply((int) : int op, int v) : op(v)\n'
        'void function main()\n'
        '    (int) : int outer = func(int x) : apply(func(int y) : y + 1, x)\n'
    )
    # The outer lambda is numbered first, but the inner one must be defined before it
    assert c_code.index('fusion_lambda_1(int x)') > c_code.index('fusion_lambda_2(int y)')


def test_closure_rejected():
    message = errors_of(
        'void function main()\n'
        '    int offset = 5\n'
        '    (int) : int add = func(int x) : x + offset\n'
    )
    assert "Lambda uses 'offset' from the surrounding function" in message
    assert "closures" in message


def test_closure_over_function_parameter_rejected():
    message = errors_of(
        '(int) : int function makeAdder(int offset) : func(int x) : x + offset\n'
        'void function main()\n    return\n'
    )
    assert "Lambda uses 'offset'" in message


def test_lambda_may_use_global_functions_and_its_own_parameters():
    _, _, ok = analyze(
        'int function tripler(int x) : x * 3\n'
        'void function main()\n    (int) : int op = func(int x) : tripler(x) + x\n'
    )
    assert ok


def test_lambda_parameter_shadowing_outer_variable_is_not_a_capture():
    _, _, ok = analyze(
        'void function main()\n    int x = 1\n    (int) : int op = func(int x) : x * 2\n'
    )
    assert ok


def test_function_variable_must_be_initialized():
    message = errors_of('void function main()\n    (int) : int op\n')
    assert "Function variable 'op' must be initialized" in message


def test_function_variable_null_rejected():
    message = errors_of('void function main()\n    (int) : int op = null\n')
    assert "Cannot assign" in message


def test_lambda_return_type_mismatch_rejected():
    message = errors_of('void function main()\n    (int) : bool op = func(int x) : x * 2\n')
    assert "Cannot assign" in message


def test_call_through_variable_checks_argument_count_and_types():
    message = errors_of(
        'void function main()\n'
        '    (int) : int op = func(int x) : x\n'
        '    int a = op()\n'
        '    int b = op("no")\n'
    )
    assert "Calling 'op' expects 1 argument(s), got 0" in message
    assert "Argument 1 to 'op': expected int, got string" in message


def test_calling_a_non_function_variable_rejected():
    message = errors_of('void function main()\n    int n = 3\n    int a = n(1)\n')
    assert "'n' is not a function" in message


def test_builtin_as_value_rejected():
    message = errors_of('void function main()\n    (string) : void p = print\n')
    assert "Built-in function 'print' can't be used as a value" in message


def test_lambda_parameter_default_rejected():
    message = errors_of('void function main()\n    (int) : int op = func(int x = 1) : x\n')
    assert "Lambda parameter 'x' can't have a default value" in message


def test_function_type_with_array_parameter_rejected():
    message = errors_of('void function main()\n    (int[]) : int op = func(int x) : x\n')
    assert "Function types can't have array parameters yet" in message


def test_function_with_array_parameters_as_value_rejected():
    message = errors_of(SUM + 'void function main()\n    (int) : int op = sum\n')
    assert "has array parameters, so it can't be used as a value" in message


def test_lambdas_end_to_end():
    exit_code, stdout, stderr = compile_and_run(
        'int function tripler(int x) : x * 3\n'
        'int function apply((int) : int op, int value) : op(value)\n'
        '(int) : int function pick(bool triple)\n'
        '    if triple\n'
        '        return tripler\n'
        '    return func(int x) : x + 100\n'
        'void function main()\n'
        '    (int) : int op = tripler\n'
        '    int a = op(5)\n'
        '    op = func(int x) : x * 2\n'
        '    int b = op(5)\n'
        '    int c = apply(tripler, 4)\n'
        '    int d = apply(function(int x) : x - 1, 4)\n'
        '    (int) : int chosen = pick(false)\n'
        '    int e = chosen(1)\n'
        '    (int, int) -> int add = func(int p, int q) : p + q\n'
        '    int f = add(2, 3)\n'
        '    print("{a} {b} {c} {d} {e} {f}")\n'
    )
    assert exit_code == 0, stderr
    assert stdout.strip() == "15 10 12 3 101 5"
