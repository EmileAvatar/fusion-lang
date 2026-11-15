"""Task 45.12c - arrays of 2 and 3 dimensions and functions (D.143, D.149).

A parameter `int[2][3] m` takes that shape - the caller's array itself; `int[][] m` takes any, its
sizes passed hidden. A view passed to a parameter is copied into a temporary first (numbers only
for now). `int[2][3] function f()` returns one; `a == b` compares two of the same shape slot by
slot. Every program runs under the leak check.
"""
import pytest

from src.config.project_config import ArraysConfig
from tests.test_foreach import run
from tests.test_structs import errors_of, main

TOTAL = 'int function total(int[] values)\n    int t = 0\n    foreach (int v in values)\n        t = t + v\n    return t\n\n'
SUM_ALL = ('int function sumAll(int[][] m)\n    int t = 0\n    foreach (int[] column in m)\n        foreach (int v in column)\n'
           '            t = t + v\n    return t\n\n')
SHOW = ('void function show(int[][] m)\n    print("{@1} {@2} {@3} {@4}", m.rows, m.columns, m.length, '
        'm[m.rows - 1][m.columns - 1])\n\n')
M = 'int[][] m = [[1, 2, 3], [4, 5, 6]]\n'


@pytest.mark.parametrize('order', ['columns', 'rows'])
def test_any_size_parameter(order):
    out = run(SUM_ALL + SHOW + main(M + 'print("{@1}", sumAll(m))\nshow(m)\nint[2][3][4] cube\ncube[1][2][3] = 7\n'
                                      'show(cube[][][3])\nprint("{@1}", sumAll(cube[1]))'),
              arrays_config=ArraysConfig(order=order))
    length = '3' if order == 'columns' else '2'
    assert out == ['21', f'2 3 {length} 6', f'2 3 {length} 7', '7']


def test_a_part_passed_to_an_int_parameter():
    out = run(TOTAL + main(M + 'print("{@1} {@2} {@3}", total(m[1]), total(m[][2]), total(m[0]))'))
    assert out == ['15 9 6']


def test_a_sized_parameter_is_the_callers_array():
    source = 'void function setCorner(int[2][3] m)\n    m[0][0] = 99\n\n'
    assert run(source + main(M + 'setCorner(m)\nprint("{@1}", m[0][0])')) == ['99']


def test_a_passed_part_is_a_copy():
    source = 'void function clear(int[] row)\n    row[0] = 0\n\n'
    assert run(source + main(M + 'clear(m[1])\nprint("{@1}", m[1][0])')) == ['4']


def test_returning_one():
    source = 'int[2][2] function identity()\n    int[][] i = [[1, 0], [0, 1]]\n    return i\n\n'
    out = run(source + main('int[2][2] id = identity()\nint[][] other = identity()\n'
                            'print("{@1} {@2} {@3}", id[1][1], identity()[0][1], other.length)'))
    assert out == ['1 0 2']


def test_equal_slot_by_slot():
    out = run(main('int[][] a = [[1, 2], [3, 4]]\nint[][] b = [[1, 2], [3, 4]]\nint[][] c = [[1, 2], [3, 5]]\n'
                   'print("{@1} {@2} {@3}", a == b, a == c, a != c)'))
    assert out == ['true false true']


def test_an_index_outside_a_passed_part():
    out = run(TOTAL + main('int[2][3][4] cube\nint k = 9\ntry\n    print("{@1}", total(cube[k][1]))\n'
                           'catch IndexError e\n    print("{e}")'))
    assert out == ['index 9 is outside the array (length 2)']


def test_strings_through_an_any_size_parameter():
    source = 'void function list(string[][] names)\n    foreach (string[] col in names)\n        foreach (string n in col)\n            write(n)\n    print("")\n\n'
    assert run(source + main('string[][] n = [["a", "b"], ["c", "d"]]\nlist(n)')) == ['acbd']


@pytest.mark.parametrize('source, message', [
    (TOTAL + main(M + 'print("{@1}", total(m))'), 'expected int[] - 1 dimension, got int[2][3] - 2'),
    (SUM_ALL + main('int[] a = [1, 2]\nprint("{@1}", sumAll(a))'), 'expected int[][] - 2 dimensions, got int[2] - 1'),
    ('void function f(int[3][2] m)\n    print("x")\n\n' + main(M + 'f(m)'), 'another shape'),
    (SUM_ALL + main('float[][] f = [[1.0]]\nprint("{@1}", sumAll(f))'), 'expected an array of int, got an array of float'),
    ('void function f(string[] s)\n    print("x")\n\n' + main('string[][] n = [["a"]]\nf(n[0])'),
     'passing a part of an array of string comes later'),
    ('int[][] function f()\n    int[2][2] m\n    return m\n\n' + main('print("x")'), "give the sizes it returns"),
    (main('int[][] a = [[1, 2], [3, 4]]\nint[][] b = [[1, 2, 3]]\nbool x = a == b'), 'the same shape'),
    (main(M + 'bool x = m[0] == m[1]'), 'Comparing a part of an array comes later'),
    ('void function f(int[][] m)\n    int[] row = m[0]\n\n' + main('print("x")'),
     'copying a part of an array of any size'),
])
def test_wrong_uses(source, message):
    assert message in errors_of(source)
