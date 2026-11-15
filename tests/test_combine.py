"""Task 45.4 - `a + b + c`: a new array, all of one type; two Lists make a new List (D.142).

Each part is read once, left to right; the result is a new array on the heap (45.10), so an array
declared from it gets its size while running. Items are copied as `slice` copies them: a string
copied, an object shared. Every program runs under the leak check.
"""
import pytest

from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main

CAR = ('class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n')
TOTAL = ('int function total(int[] values)\n    int t = 0\n    foreach (int v in values)\n'
         '        t = t + v\n    return t\n\n')
MAKE = 'int[] function make(int n)\n    if n > 2\n        return [1, 2, 3]\n    return [9]\n\n'


def test_plain_sized_and_literal_arrays():
    out = run(main('int[] a = [1, 2]\nint[3] b = [3, 4, 5]\nint[] c = a + b + [6]\n'
                   'print("{@1} {@2} {@3}", c.length, c[0], c[5])'))
    assert out == ['6 1 6']


def test_replacing_with_a_combination_and_calls():
    out = run(TOTAL + MAKE + main('int[] c = [1]\nc = c + make(1) + make(3)\nprint("{@1} {@2}", c.length, total(c))'))
    assert out == ['5 16']


def test_passed_straight_to_an_array_parameter():
    out = run(TOTAL + MAKE + main('int[] a = [1, 2]\nprint("{@1}", total(a + make(5)))'))
    assert out == ['9']


def test_strings_are_copied():
    out = run(main('string[] s = ["x", "y"]\nstring[] t = s + ["z"] + s\nforeach (string w in t)\n    write(w)\n'
                   'print("")\ns[0] = "q"\nprint("{@1}", t[0])'))
    assert out == ['xyzxy', 'x']


def test_objects_are_shared():
    out = run(CAR + main('Car[] cars = [Car("red")]\nCar[] more = cars + [Car("blue")]\nmore[0].color = "green"\n'
                         'print("{@1} {@2} {@3}", more.length, more[1].color, cars[0].color)'))
    assert out == ['2 blue green']


def test_a_growable_array_from_a_combination():
    out = run(main('int[] a = [1, 2]\nint:[] g = a + [7]\ng.add(8)\nprint("{@1}", g.length)\n'
                   'print("{@1}", g.pop())'))
    assert out == ['4', '8']


def test_growable_arrays_combine():
    out = run(main('int:[] g = [1]\nint:[] h = [2]\nint[] c = g + h + g\nprint("{@1} {@2}", c.length, c[1])'))
    assert out == ['3 2']


def test_lists_combine():
    out = run(main('List<int> la = [1, 2]\nList<int> lb = la + [3] + la\nla.add(4)\n'
                   'print("{@1} {@2} {@3}", lb.len(), lb[2], la.len())'))
    assert out == ['5 3 3']


def test_a_combination_not_kept():
    out = run(MAKE + main('int[] a = [1, 2]\nint[3] b = [3, 4, 5]\nprint("{@1}", (a + b).length)\n'
                          'print("{@1}", (make(5) + a)[4])'))
    assert out == ['5', '2']


@pytest.mark.parametrize('left, expected', [('a + [3]', 'true'), ('make(3) + [1]', 'false'),
                                            ('make(1) + a', 'false'), ('[1] + [2, 3]', 'true')])
def test_compared(left, expected):
    out = run(MAKE + main(f'int[] a = [1, 2]\nbool same = {left} == [1, 2, 3]\nprint("{{@1}}", same)'))
    assert out == [expected]


def test_returned_and_in_a_struct_field():
    out = run('struct Box\n    int[] items\n\nint[] function both(int[] x, int[] y)\n    return x + y\n\n'
              + main('int[] a = [1, 2]\nBox b = Box([1])\nb.items = b.items + a\nint[] c = both(a, [8, 9])\n'
                     'print("{@1} {@2}", b.items.length, c.length)'))
    assert out == ['3 4']


def test_fixed_from_a_combination_keeps_its_size():
    assert "fixed" in errors_of(main('int[] a = [1]\nfixed int[] f = a + a\nf = [1, 2, 3]'))


@pytest.mark.parametrize('body, message', [
    ('int[] a = [1]\nList<int> l = [2]\nList<int> m = a + l', "both arrays or both Lists"),
    ('int[] a = [1]\nfloat[] f = [2.0]\nint[] m = a + f', "arrays of one type"),
    ('int[] a = [1]\nint m = a + 1', "both arrays or both Lists"),
])
def test_wrong_combinations_are_errors(body, message):
    assert message in errors_of(main(body))
