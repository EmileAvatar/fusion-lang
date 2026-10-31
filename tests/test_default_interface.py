"""Tests for Task 32.5b - Default: a variable of the type is never null (Classes.md section 5,
Decisions.md D.010).

    class Settings implements Default
        private constructor()        // a constructor without arguments - may be private
    Settings s                       // made: the compiler calls Settings()
    s = null                         // the old object goes; a new default one comes

Each test is a row of the table in Classes.md section 5. Every program runs with the leak
check. With and without null checks (Rule 4b): a Default value is never null - `.` never
fails, and `is null` is always false (a warning).
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main, warnings_of

SETTINGS = ('class Settings implements Default\n'
            '    public int size = 3\n'
            '    private constructor()\n'
            '        size = 5\n\n'
            'class App\n'
            '    public Settings settings\n'
            '    public static Settings shared\n\n')


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_a_variable_with_no_value_gets_a_default_object():
    assert run(SETTINGS + main('Settings s\nprint("{@1}", s.size)')) == ['5']


def test_null_lets_the_old_object_go_and_makes_a_new_one():
    assert run(SETTINGS + main('Settings s\n'
                               's.size = 9\n'
                               's = null\n'
                               'print("{@1}", s.size)\n'
                               'Settings t = null\n'
                               'print("{@1}", t.size)')) == ['5', '5']


def test_a_field_and_a_static_of_the_type_get_one_too():
    assert run(SETTINGS + main('App a = App()\n'
                               'print("{@1} {@2}", a.settings.size, App.shared.size)')) == ['5 5']


def test_without_a_null_check_dot_never_fails():
    # Rule 4b: no check needed - a Default value is never null, so `.` is never a NullError
    assert run(SETTINGS + main('Settings s = null\n'
                               'try\n'
                               '    print("{@1}", s.size)\n'
                               'catch NullError e\n'
                               '    print("never")')) == ['5']


def test_with_a_null_check_it_is_never_null():
    # Rule 4b: with a check - always false, so the compiler warns
    assert "is never null" in warnings_of(SETTINGS + main('Settings s\n'
                                                          'if s is null\n'
                                                          '    print("never")'))


@pytest.mark.parametrize('source, message', [
    ('class Settings implements Default\n    int n\n    constructor(int n)\n        this.n = n\n\n',
     "Class 'Settings' implements Default but has no constructor without arguments"),
    ('class Node implements Default\n    Node next\n\n',
     "Class 'Node' implements Default and holds itself (Node -> Node)"),
])
def test_default_errors(source, message):
    assert message in errors_of(source + main('print("x")'))
