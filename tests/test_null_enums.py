"""Tests for Task 30.11 - enums can be null.

An enum is treated as a reference type, like a class (user, 2026-10-27/28): `Status s` with no
value is null, not the first value. Tests: `== null`, `!= null`, `=== null`, `is null`,
`is not null`, `x?.null`, `!x?.null`; printing and toString give "null"; toInt on null is a
NullError; a match takes null to `else` - and a match that covers every value but has no
`else` raises a NullError on null (there is nowhere else to go). The first value of an enum
may now hold the enum itself.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import main, errors_of, analyze

STATUS = 'enum Status\n    OK\n    NotFound\n\n'
TOKEN = 'enum Token\n    Number(int value)\n    Word(string text)\n\n'


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


def test_unset_is_null_and_every_null_test():
    lines = run(STATUS + main(
        'Status s\n'
        'print("{s} {@1} {@2} {@3} {@4}", s == null, s === null, s is null, s?.null)\n'
        's = Status.NotFound\n'
        'print("{s} {@1} {@2} {@3} {@4}", s != null, s is not null, !s?.null, s == Status.OK)\n'
        's = null\n'
        'print(s.toString())'))
    assert lines == ['null true true true true', 'NotFound true true true false', 'null']


def test_an_enum_with_data_and_a_struct_field():
    lines = run(TOKEN + 'struct Slot\n    Token token\n    int n\n\n' + main(
        'Token t\n'
        'Slot slot\n'
        'print("{t} {@1} {@2}", t == null, slot.token is null)\n'
        't = Token.Word("hi")\n'
        'print("{t} {@1}", t != null)\n'
        't = null\n'
        'print("{t}")'))
    assert lines == ['null true true', 'Word true', 'null']    # the leak check covers "hi"


def test_null_goes_to_else_in_a_match():
    lines = run(STATUS + main(
        'Status s = null\n'
        'match s\n'
        '    case OK: print("ok")\n'
        '    else: print("else")'))
    assert lines == ['else']


def test_a_match_with_no_else_raises_a_null_error_and_to_int_too():
    lines = run(STATUS
                + 'string function name(Status s)\n'
                  '    match s\n'
                  '        case OK: return "ok"\n'
                  '        case NotFound: return "missing"\n\n'
                + 'int function number(Status s) : s.toInt()\n\n'
                + main('Status s\n'
                       'try\n'
                       '    print(name(s))\n'
                       'catch NullError e\n'
                       '    print("caught: {e}")\n'
                       'try\n'
                       '    print("{@1}", number(s))\n'
                       'catch NullError e\n'
                       '    print("caught: {e}")\n'
                       'print(name(Status.OK))'))
    assert lines == ['caught: a match on a null Status with no case for null',
                     'caught: toInt() on a null enum value - it has no number', 'ok']


def test_the_first_value_may_hold_the_enum_now():
    lines = run('enum Expr\n    Add(Expr left, Expr right)\n    Number(int value)\n\n'
                + main('Expr e = Expr.Add(Expr.Number(1), Expr.Number(2))\n'
                       'Expr unset\n'
                       'print("{e} {unset}")'))
    assert lines == ['Add null']


@pytest.mark.parametrize('source, message', [
    (main('string s = null'), "A string can't be null - only an enum"),
    (main('int n = null'), "A int can't be null - only an enum"),
    ('enum E\n    A = -2147483647\n\n' + main('E e = E.A'), "-2147483647 is kept for null"),
])
def test_errors(source, message):
    assert message in errors_of(source)


def test_a_value_that_can_never_be_null_gives_a_warning():
    analyzer, _, ok = analyze(main('string t = "x"\nif t == null\n    print("x")'))
    assert ok
    assert any('A string is never null - this test is always false' in str(w)
               for w in analyzer.get_warnings())


def test_other_safe_navigation_is_planned():
    with pytest.raises(Exception, match="'[?][.]' before a member or method is planned"):
        errors_of(STATUS + main('Status s\nstring t = s?.toString()'))
