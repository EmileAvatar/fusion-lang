"""Tests for Task 18.3.5 - the equality operator family.

- `=` compares inside an if / while / else-if condition (the same as `==`)
- `==` / `!=` compare values; across types only: a number and numeric text, a char and a
  one-character string, int and float. Any other mixed pair is a compile error
- `===` / `!==` also compare the type - on two different types always false (a warning)
- structs compare field by field, arrays element by element (same size)

Every program here runs under the leak check (see tests/test_end_to_end.py).
"""

import pytest

from src.lexer import Lexer
from src.lexer.token import TokenType
from src.parser.ast_nodes import BinaryExpr, AssignmentStmt
from tests.test_structs import parse, errors_of, warnings_of, generate_c, main, POINT
from tests.test_strings import run_ok, ECHO


def show(*conditions: str) -> str:
    """Statements printing each condition's result as `true` / `false`, one per line (a
    bool prints as 1 / 0 today, so through an if)."""
    lines = []
    for i, condition in enumerate(conditions):
        lines += [f'bool r{i} = {condition}', f'if r{i}', '    print("true")', 'else',
                  '    print("false")']
    return '\n'.join(lines)


# ============================================================
# Tokens and parsing
# ============================================================

def test_strict_operators_are_tokens():
    types = [t.type for t in Lexer('a === b !== c == d != e', 'test.fusion').tokenize()]
    assert TokenType.STRICT_EQUAL in types and TokenType.STRICT_NOT_EQUAL in types
    assert types.count(TokenType.EQUAL) == 1 and types.count(TokenType.NOT_EQUAL) == 1


def _condition(source: str):
    function = parse(main(source)).declarations[0]
    return function.body.statements[1].condition


@pytest.mark.parametrize("statement", ['if x = 2\n    x = 3', 'while x = 2\n    x = 3'])
def test_equals_sign_compares_in_a_condition(statement):
    condition = _condition('int x = 2\n' + statement)
    assert isinstance(condition, BinaryExpr) and condition.operator == '=='


def test_equals_sign_compares_in_else_if_and_with_and():
    stmt = parse(main('int x = 2\nif x = 1\n    x = 3\nelse if x = 2 and x = 2\n    x = 4')) \
        .declarations[0].body.statements[1]
    condition = stmt.else_branch.condition
    assert condition.operator == 'and'
    assert condition.left.operator == '==' and condition.right.operator == '=='


def test_equals_sign_still_assigns_in_the_body():
    stmt = parse(main('int x = 2\nif x = 2\n    x = 3')).declarations[0].body.statements[1]
    assert isinstance(stmt.then_branch.statements[0], AssignmentStmt)


# ============================================================
# Running: values, mixed types, strict
# ============================================================

def test_equality_of_simple_values():
    out = run_ok(ECHO + main(
        'int x = 2\n'
        'string s = echo("ab")\n'
        'if x = 2\n'
        '    print("if")\n'
        'if x = 3\n'
        '    print("no")\n'
        'else if s = "ab"\n'
        '    print("else if")\n'
        'int n = 0\n'
        'while n = 0\n'
        '    n = n + 1\n'
        + show('s == "ab"', 's != "ab"', 'echo("x") == echo("x")', "'a' == 'a'", 'true == false',
               'x != 3', '2.5 == 2.5')
    ))
    assert out == ['if', 'else if', 'true', 'false', 'true', 'true', 'false', 'true', 'true']


def test_mixed_types_by_value():
    out = run_ok(ECHO + main(
        'float half = 2.5\n'
        + show('2 == "2"', '"2" == 2', '2 == "2.0"', 'half == "2.5"', '2 == "two"', '2 == ""',
               '2 != "3"', "'a' == \"a\"", "\"a\" == 'a'", "'a' == \"ab\"", "'a' == \"\"",
               '2 == 2.0', '2 != 2.5', "'\\u00e9' == \"\\u00e9\"")
    ))
    assert out == ['true', 'true', 'true', 'true', 'false', 'false', 'true', 'true', 'true',
                   'false', 'false', 'true', 'true', 'true']


def test_strict_equality():
    source = main(show('2 === 2', '2 === 2.0', '2 === "2"', "'a' === \"a\"", '"a" === "a"',
                       '2 !== 2.0', '2 !== 2'))
    assert run_ok(source) == ['true', 'false', 'false', 'false', 'true', 'true', 'false']
    warnings = warnings_of(source)
    assert "'===' is always false here: int and float are different types" in warnings
    assert "'!==' is always true here: int and float are different types" in warnings


def test_strict_on_different_types_still_runs_both_sides():
    out = run_ok(ECHO + 'int function loud()\n    print("ran")\n    return 1\n\n'
                 + main(show('loud() === echo("1")')))
    assert out == ['ran', 'false']


# ============================================================
# Structs and arrays
# ============================================================

STRUCTS = (POINT
           + 'struct Spot\n    int x\n    float y\n\n'
           + 'struct Book\n    string title\n    string[2] tags\n\n'
           + 'struct Shelf\n    Book book\n    int count\n\n')


def test_struct_equality_field_by_field():
    out = run_ok(ECHO + STRUCTS + main(
        'Point a = Point(1, 2)\n'
        'Point b = Point(1, 2)\n'
        'Point c = Point(1, 3)\n'
        'Spot s = Spot(1, 2.0)\n'
        'Book x = Book(echo("Dune"), ["sf", echo("classic")])\n'
        'Book y = Book("Dune", ["sf", "classic"])\n'
        'Book z = Book("Dune", ["sf", "new"])\n'
        'Shelf one = Shelf(x, 1)\n'
        'Shelf two = Shelf(y, 1)\n'
        + show('a == b', 'a != c', 'a == s', 'a === s', 'x == y', 'x == z', 'one == two',
               'one === two', 'Point(1, 2) == a')
    ))
    assert out == ['true', 'true', 'true', 'false', 'true', 'false', 'true', 'true', 'true']


def test_array_equality_element_by_element():
    out = run_ok(ECHO + 'bool function same(int[] a, int[] b)\n    return a == b\n\n' + main(
        'int[3] a = [1, 2, 3]\n'
        'int[3] b = [1, 2, 3]\n'
        'int[2] two = [1, 2]\n'
        'float[3] f = [1.0, 2.0, 3.0]\n'
        'string[2] s = [echo("a"), "b"]\n'
        'if same(a, b) and not same(a, two)\n'
        '    print("true false")\n'
        + show('a == b', 'a == two', 'a == f', 'a === f', 'a == [1, 2, 3]', 's == ["a", "b"]',
               's != ["a", "c"]')
    ))
    assert out == ['true false', 'true', 'false', 'true', 'false', 'true', 'true', 'true']


def test_struct_helpers_are_generated_once():
    c_code = generate_c(STRUCTS + main(
        'Point a\nPoint b\nbool r = a == b\nbool r2 = a != b\nSpot s\nbool r3 = a == s'))
    assert c_code.count('static inline bool fusion_eq_Point(') == 1
    assert 'static inline bool fusion_eq_Point__Spot(' in c_code
    assert '!fusion_eq_Point(a, b)' in c_code


# ============================================================
# Errors: only the pairs in the table compare
# ============================================================

@pytest.mark.parametrize("body, expected", [
    ('bool r = true == 1', "Can't compare bool with int using '=='"),
    ('bool r = "true" == true', "a bool only equals a bool (no truthiness)"),
    ("bool r = 'a' == 97", "Can't compare char with int using '=='"),
    ('Point p\nbool r = p == "p"', "Can't compare Point with string"),
    ('Point p\nBook b\nbool r = p != b', "structs Point and Book have different fields"),
    ('int[2] a = [1, 2]\nstring[2] s = ["1", "2"]\nbool r = a == 5', "Can't compare int[2] with int"),
    ('int[2] a = [1, 2]\nbool[2] b = [true, true]\nbool r = a == b',
     "their elements can't be compared"),
    ('bool r = main == main', "functions can't be compared"),
])
def test_pairs_outside_the_table_are_errors(body, expected):
    assert expected in errors_of(STRUCTS + main(body))
