"""Task 45.11 - toList on arrays of 2 and 3 dimensions (D.148, the user's choice 2026-11-15: form A).

`m.toList()` is a List of Lists in the loop's order - the outer dimension first (depth -> columns ->
rows; `[arrays] order = "rows"`: rows first), the same as foreach gives them. A copy: strings
copied, objects copied too (as an array's toList). Works on a part (`cube[1].toList()`) and on a
growable array. Every program runs under the leak check.
"""
import pytest

from src.config.project_config import ArraysConfig
from tests.test_end_to_end import compile_and_run
from tests.test_foreach import run
from tests.test_structs import errors_of, main

CAR = 'class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n'
M = 'int[][] m = [[1, 2, 3], [4, 5, 6]]\n'
WALK = 'foreach (List<int> c in lists)\n    foreach (int v in c)\n        write("{v} ")\nprint("|")\n'


def test_columns_first_as_foreach():
    out = run(main(M + 'List<List<int>> lists = m.toList()\n' + WALK + 'print("{@1} {@2} {@3}", lists.len(), lists[0].len(), lists[2][1])'))
    assert out == ['1 4 2 5 3 6 |', '3 2 6']


def test_rows_first():
    out = run(main(M + 'List<List<int>> lists = m.toList()\n' + WALK), arrays_config=ArraysConfig(order='rows'))
    assert out == ['1 2 3 4 5 6 |']


def test_a_cube():
    body = ('int[2][2][2] cube\ncube[1][0][1] = 7\nList<List<List<int>>> sheets = cube.toList()\n'
            'print("{@1} {@2} {@3}", sheets.len(), sheets[1].len(), sheets[1][0][1])')
    assert run(main(body)) == ['2 2 7']


@pytest.mark.parametrize('part, expected', [('m[1]', '3 6'), ('m[][2]', '2 6')])
def test_a_part(part, expected):
    assert run(main(M + f'List<int> l = {part}.toList()\nprint("{{@1}} {{@2}}", l.len(), l[l.len() - 1])')) == [expected]


def test_strings_are_copied():
    body = ('string:[][] s = [["a", "b"], ["c", "d"]]\nList<List<string>> l = s.toList()\ns[0][0] = "z"\n'
            'print("{@1}{@2}{@3}", l[0][0], l[0][1], l[1][1])')
    assert run(main(body)) == ['acd']


def test_a_grown_array():
    body = M.replace('int[][]', 'int:[][]') + 'm.expand(Dimension.ROWS, 1)\nList<List<int>> lists = m.toList()\n' + WALK
    assert run(main(body)) == ['1 4 0 2 5 0 3 6 0 |']


def test_a_null_object_slot_is_skipped():
    # Rule 4b / D.152: an array slot may be null (D.140), a List never holds null (D.139) - a null
    # slot is skipped, a column all null stays an empty List (the shape kept); once filled, it's there
    body = ('Car[1][2] cars\ncars[0][0] = Car("red")\nList<List<Car>> l = cars.toList()\n'
            'print("{@1} {@2} {@3} {@4}", l.len(), l[0].len(), l[1].len(), l[0][0].color)\n'
            'cars[0][1] = Car("blue")\nList<List<Car>> ok = cars.toList()\n'
            'print("{@1} {@2}", ok[0][0].color, ok[1][0].color)')
    assert run(CAR + main(body)) == ['2 1 0 red', 'red blue']


def test_every_slot_null():
    body = ('Car[2][2] cars\nList<List<Car>> l = cars.toList()\n'
            'print("{@1} {@2} {@3}", l.len(), l[0].len(), l[1].len())')
    assert run(CAR + main(body)) == ['2 0 0']


def test_one_dimension_skips_null_slots():
    # D.152 on a one-dimension array, on the stack and on the heap: only the filled slots
    body = ('Car[3] cars\ncars[1] = Car("red")\nList<Car> l = cars.toList()\n'
            'print("{@1} {@2}", l.len(), l[0].color)\nCar[3] none\nprint("{@1}", none.toList().len())\n'
            'int[3] n = [1, 0, 3]\nprint("{@1}", n.toList().len())')
    assert run(CAR + main(body)) == ['1 red', '0', '3']


@pytest.mark.parametrize('body, message', [
    (M + 'List<int> l = m.toList()', 'Cannot assign'),
    (M + 'List<List<int>> l = m.toList(false)', "An array's toList always copies"),
    ('Car[2][2] cars\nstring s = cars.toCSV()', 'takes plain values only'),     # 45.11b: structs / objects not
])
def test_wrong_uses(body, message):
    assert message in errors_of(main(body))


@pytest.mark.parametrize('declaration', [
    'int[2][2] a = [[1, 2], [3, 4]]',
    'int[][][] a = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]',
    'int:[][] a = [[1, 2], [3, 4]]',
])
def test_to_list_used_straight_away_is_freed_once(declaration):
    # a.toList().len() - the new List held once, freed once (it was freed twice - found by 45.6)
    source = f'void function main()\n    {declaration}\n    print("{{@1}}", a.toList().len())\n'
    code, out, err = compile_and_run(source)
    assert code == 0, out + err
    assert out.strip().splitlines()[0] == '2'
