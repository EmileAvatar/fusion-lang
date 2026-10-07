"""Tests for Task 18.1 - functions with full parameter support.

18.1.1: default parameter values (trailing-only, constant-only, filled in at each C call site)
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
