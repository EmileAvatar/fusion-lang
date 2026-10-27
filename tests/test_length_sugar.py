"""Tests for Task 30.8 - `.len` and `.length`, with and without brackets.

On a string, bytes, an array, a List or a Map, `x.len()`, `x.length()`, `x.len` and
`x.length` all mean `len(x)` - `length` is quick typing for `len` (user, 2026-10-27). A struct's
own field called `length`, and the program's own `length` function called as a method
(Task 44.2), come first.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import main, errors_of

SETUP = ('string s = "abc"\n'
         'int[] a = [1, 2]\n'
         'List<int> xs = [1, 2, 3, 4]\n'
         'Map<string, int> m\n'
         'm["k"] = 1\n'
         'bytes b = toBytes("hi")\n')


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


@pytest.mark.parametrize('form', ['{x}.len()', '{x}.length()', '{x}.len', '{x}.length'])
def test_every_form_on_every_type(form):
    values = ', '.join(form.format(x=x) for x in ('s', 'a', 'xs', 'm', 'b'))
    lines = run(main(SETUP + f'print("{{@1}} {{@2}} {{@3}} {{@4}} {{@5}}", {values})'))
    assert lines == ['3 2 4 1 2']


def test_a_fresh_string_and_a_field_and_a_condition():
    lines = run('struct P\n    int[3] scores\n\n'
                'string function word() : "four"\n\n'
                + main('P p = P([5, 6, 7])\n'
                       'string s = "ab"\n'
                       'print("{@1} {@2} {@3}", word().length, (s + "cde").len, p.scores.length)\n'
                       'if s.length > 1\n'
                       '    print("long")'))
    assert lines == ['4 5 3', 'long']           # the leak check covers the fresh strings


def test_a_struct_field_called_length_comes_first():
    lines = run('struct Rope\n    int length\n\n'
                + main('Rope r = Rope(12)\n'
                       'print("{@1}", r.length)'))
    assert lines == ['12']


def test_the_programs_own_length_function_comes_first():
    lines = run('int function length(string s) : 99\n\n'
                + main('string s = "abc"\n'
                       'print("{@1} {@2}", s.length(), s.len())'))
    assert lines == ['99 3']


def test_length_on_a_number_is_still_an_error():
    message = errors_of(main('int n = 5\nint k = n.length'))
    assert "Cannot read field 'length'" in message
