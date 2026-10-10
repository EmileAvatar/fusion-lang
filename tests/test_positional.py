"""Tests for Task 18.2.2b - positional placeholders and left-to-right argument order.

Part A: every call's arguments are evaluated left to right as written - positional calls,
        struct constructors and calls through function values, not only named arguments
        (18.2.2). Temporaries are only added where the order could change the result.
Part B: print("User {@1} is {@2}", name, age) - {@N} placeholders for the arguments after
        the text, in any order and repeatable, each argument evaluated once, left to right.
        Closes Task 15.11 (positional interpolation never compiled) and fixes print("{@1}")
        silently printing "1".
"""

import pytest

from src.parser.ast_nodes import StringPositionalPart
from src.codegen import CCodeGenerator
from tests.test_structs import (
    parse, analyze, errors_of, warnings_of, generate_c, main, POINT,
)
from tests.test_end_to_end import compile_and_run


SUB = 'int function sub(int a, int b) : a - b\n'
NEXT = ('int function next(int[] counter)\n'
        '    counter[0] = counter[0] + 1\n'
        '    return counter[0]\n')


# ============================================================
# Part A - left-to-right argument order
# ============================================================

def test_plain_arguments_need_no_temporaries():
    c_code = generate_c(SUB + main('int x = 1\nint r = sub(x, 2)'))
    assert 'int r = fu_sub(x, 2);' in c_code
    assert 'fusion_arg' not in c_code


def test_one_call_beside_plain_values_needs_no_temporaries():
    # A call can't change a plain variable or literal, so evaluation order isn't visible
    c_code = generate_c(SUB + 'int function twice(int v) : v * 2\n'
                        + main('int x = 1\nint r = sub(twice(x), x)'))
    assert 'int r = fu_sub(fu_twice(x), x);' in c_code


def test_two_calls_are_sequenced_left_to_right():
    c_code = generate_c(NEXT + SUB + main('int[] c = [0]\nint d = sub(next(c), next(c))'))
    assert 'int d = (fusion_arg_1 = fu_next(c, 1), fusion_arg_2 = fu_next(c, 1), ' \
           'fu_sub(fusion_arg_1, fusion_arg_2));' in c_code


def test_call_beside_array_read_is_sequenced():
    # next(c) changes c[0], so reading c[0] before or after it gives different values
    c_code = generate_c(NEXT + SUB + main('int[] c = [0]\nint d = sub(c[0], next(c))'))
    assert 'fusion_arg_1 = c[0], fusion_arg_2 = fu_next(c, 1)' in c_code


def test_struct_constructor_is_sequenced():
    c_code = generate_c(POINT + NEXT + main('int[] c = [0]\nPoint p = Point(next(c), next(c))'))
    assert '(fu_Point){fusion_arg_1, fusion_arg_2}' in c_code


def test_function_value_call_is_sequenced():
    c_code = generate_c(NEXT + SUB + main(
        'int[] c = [0]\n(int, int) : int f = sub\nint e = f(next(c), next(c))'))
    assert 'f(fusion_arg_1, fusion_arg_2)' in c_code


def test_lambda_argument_is_not_a_call():
    # A lambda's body runs later, when it's called - creating the value calls nothing
    lambda_expr = parse(main('(int) : int f = func(int x) : sub(x, x)')).declarations[0] \
        .body.statements[0].initializer
    assert not CCodeGenerator._contains_call(lambda_expr)


def test_left_to_right_end_to_end():
    exit_code, stdout, stderr = compile_and_run(
        POINT + NEXT + SUB + main(
            'int[] c = [0]\n'
            'int d = sub(next(c), next(c))\n'
            'print("{d}")\n'
            'Point p = Point(next(c), next(c))\n'
            'print("{p.x} {p.y}")\n'
            '(int, int) : int f = sub\n'
            'int e = f(next(c), next(c))\n'
            'print("{e}")\n'
            'int g = sub(c[0], next(c))\n'
            'print("{g}")\n'
        )
    )
    assert exit_code == 0, stderr
    # sub(1, 2); Point(3, 4); f(5, 6); sub(c[0] = 6 read first, then next() = 7)
    assert stdout.splitlines() == ["-1", "3 4", "-1", "-1"]


# ============================================================
# Part B - {@N} placeholders in print
# ============================================================

def test_placeholder_parses_as_its_own_segment():
    call = parse(main('print("x {@2}", 1, 2)')).declarations[0].body.statements[0].expression
    positional = [s for s in call.arguments[0].segments if isinstance(s, StringPositionalPart)]
    assert [s.index for s in positional] == [2]


def test_placeholders_in_order():
    c_code = generate_c(main('string name = "Ada"\nint age = 36\n'
                             'print("User {@1} is {@2} years old", name, age)'))
    assert 'printf("User %s is %d years old\\n", name.data, age);' in c_code


def test_placeholders_out_of_order_and_repeated():
    c_code = generate_c(main('print("{@3} {@1} {@2} {@1}", "a", "b", "c")'))
    assert ('printf("%s %s %s %s\\n", FUSION_STR("c").data, FUSION_STR("a").data, '
            'FUSION_STR("b").data, FUSION_STR("a").data);') in c_code


def test_placeholders_mix_with_named_values():
    c_code = generate_c(main('string name = "Ada"\nprint("{name} scored {@1}", 99)'))
    assert 'printf("%s scored %d\\n", name.data, 99);' in c_code


def test_repeated_call_argument_is_evaluated_once():
    c_code = generate_c(NEXT + main('int[] c = [0]\nprint("{@1} {@1}", next(c))'))
    assert '(fusion_arg_1 = fu_next(c, 1), printf("%d %d\\n", fusion_arg_1, fusion_arg_1));' in c_code


def test_arguments_evaluated_in_written_order_not_placeholder_order():
    c_code = generate_c(NEXT + main('int[] c = [0]\nprint("{@2} {@1}", next(c), next(c))'))
    assert ('(fusion_arg_1 = fu_next(c, 1), fusion_arg_2 = fu_next(c, 1), '
            'printf("%d %d\\n", fusion_arg_2, fusion_arg_1));') in c_code


def test_unused_call_argument_still_runs():
    c_code = generate_c(NEXT + main('int[] c = [0]\nprint("{@1}", 5, next(c))'))
    assert 'fusion_arg_1 = fu_next(c, 1)' in c_code


def test_percent_still_escaped_with_placeholders():
    assert 'printf("100%% sure: %d%%\\n", 50);' in generate_c(main('print("100% sure: {@1}%", 50)'))


@pytest.mark.parametrize("body, message", [
    ('print("value {@1}")', "{@1} has no matching argument - print() was given 0 argument(s)"),
    ('print("{@3}", 1, 2)', "{@3} has no matching argument - print() was given 2 argument(s)"),
    ('print("{@0}", 1)', "{@0} isn't a valid placeholder - they start at {@1}"),
    ('print("plain", 1)', "the text has no {@1}-style placeholders to use them"),
    ('int[] a = [1]\nprint("{@1}", a)', "Can't print a whole int[1] value"),
    ('print(5, 1)', "Argument 1 to 'print': expected string, got int"),
])
def test_placeholder_errors(body, message):
    assert message in errors_of(main(body))


def test_value_1_bug_fixed():
    """print("value {@1}") used to compile and print "value 1" - the parser turned {@1}
    into the integer literal 1."""
    assert not analyze(main('print("value {@1}")'))[2]


def test_unused_argument_is_a_warning():
    warnings = warnings_of(main('print("{@1}", 1, 2)'))
    assert "Argument 3 to print() isn't used - no {@2} placeholder in the text" in warnings


def test_placeholders_end_to_end():
    exit_code, stdout, stderr = compile_and_run(
        NEXT + main(
            'string name = "Ada"\n'
            'int age = 36\n'
            'print("User {@1} is {@2} years old", name, age)\n'
            'print("{@3} {@1} {@2} {@1}", "a", "b", "c")\n'
            'print("{name} scored {@1}", 99)\n'
            'int[] c = [0]\n'
            'print("once: {@1} {@1}", next(c))\n'
            'print("{@2} then {@1}", next(c), next(c))\n'
            'print("100% sure: {@1}%", 50)\n'
        )
    )
    assert exit_code == 0, stderr
    assert stdout.splitlines() == [
        "User Ada is 36 years old",
        "c a b a",
        "Ada scored 99",
        "once: 1 1",
        "3 then 2",
        "100% sure: 50%",
    ]
