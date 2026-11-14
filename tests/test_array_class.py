"""Task 45.1 - the built-in Array class (D.142): every array acts as an object of it, so
`Array.length(a)` and `a.length()` / `a.length` / `len(a)` mean the same; `toList` and `toCSV` too.
"""
import pytest

from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main

POINT = 'struct Point\n    int x\n    int y\n\n'


@pytest.mark.parametrize('form', ['Array.length(a)', 'Array.len(a)', 'a.length()', 'a.length',
                                  'a.len()', 'len(a)'])
def test_every_form_of_the_length(form):
    assert run(main(f'int[] a = [5, 2, 3]\nprint("{{@1}}", {form})')) == ['3']


def test_array_to_list_through_the_class():
    out = run(main('int[] a = [5, 2, 3]\nList<int> xs = Array.toList(a)\nxs.add(4)\n'
                   'print("{@1} {@2}", xs.len(), a.length)'))
    assert out == ['4 3']


def test_array_to_csv_through_the_class():
    out = run(POINT + main('Point[] ps = [Point(1, 2), Point(3, 4)]\nprint(Array.toCSV(ps, ";"))\n'
                           'print(ps.toCSV(";"))'))
    assert out[:3] == out[3:] and out[:3] == ['Point.x;Point.y', '1;2', '3;4']


def test_an_empty_array_has_length_zero():
    assert run(main('int[0] a\nprint("{@1}", Array.length(a))')) == ['0']


@pytest.mark.parametrize('body, message', [
    ('int[] a = [1]\nprint("{@1}", Array.size(a))', "Array has no method 'size' (it has length, len, toList, toCSV)"),
    ('print("{@1}", Array.length())', "Array.length needs the array first"),
    ('string s = "hi"\nprint("{@1}", Array.length(s))', "Array.length works on an array, not string"),
])
def test_wrong_uses_are_errors(body, message):
    assert message in errors_of(main(body))


@pytest.mark.parametrize('kind', ['struct', 'class', 'enum'])
def test_array_is_a_built_in_name(kind):
    decl = {'struct': 'struct Array\n    int x\n\n', 'class': 'class Array\n    public int x\n\n',
            'enum': 'enum Array\n    A\n    B\n\n'}[kind]
    assert "'Array' is a built-in type" in errors_of(decl + main('print("x")'))
