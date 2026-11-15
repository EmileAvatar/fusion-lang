"""Task 45.12b - views of an array of 2 or 3 dimensions (D.143, D.148, D.149).

An index left out means all of that dimension: `cube[1]` (row 1), `cube[][2][1]` (column 2 of sheet
1), `cube[][][3]` (sheet 3). `length` is the outer open dimension (-1 on one slot); `foreach` walks
the outer one first - depth, then columns, then rows - and its variable is a borrowed view; a view
given to a variable is a copy (numbers and strings copied, objects shared, byVal copies them too).
Every program runs under the leak check.
"""
import pytest

from src.config.project_config import ArraysConfig
from tests.test_foreach import run
from tests.test_structs import errors_of, main

CAR = 'class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n'
# cube[r][c][d] = r*100 + c*10 + d: every slot says where it is
FILL = ('int[2][3][4] cube\nfor r in range(0, 2)\n    for c in range(0, 3)\n        for d in range(0, 4)\n'
        '            cube[r][c][d] = r * 100 + c * 10 + d\n')


def values(view: str) -> str:
    return f'foreach (int v in {view})\n    write("{{v}} ")\nprint("|")\n'


# The truth table (files/Arrays.md 8b): what a view reaches, on int[2][3][4] cube
@pytest.mark.parametrize('view, reaches', [
    ('cube[1][][3]', '103 113 123 |'),          # row 1, sheet 3: one value per column
    ('cube[][2][1]', '21 121 |'),               # column 2 of sheet 1: one value per row
    ('cube[0][1]', '10 11 12 13 |'),            # row 0, column 1: one value per sheet
    ('cube[1][2]', '120 121 122 123 |'),
    ('cube[][0][0]', '0 100 |'),
])
def test_a_view_reaches(view, reaches):
    assert run(main(FILL + values(view))) == [reaches]


@pytest.mark.parametrize('expression, length', [
    ('cube.length', 4),                # the whole: depth
    ('cube[1].length', 4),             # row 1: columns x depth - depth first
    ('cube[][][3].length', 3),         # sheet 3: rows x columns - columns first
    ('cube[][2][1].length', 2),        # a column: its rows
    ('cube[1][2][3].length', -1),      # one slot (D.143)
])
def test_length_the_outer_first(expression, length):
    assert run(main(FILL + f'print("{{@1}}", {expression})')) == [str(length)]


@pytest.mark.parametrize('expression, length', [('cube.length', 2), ('cube[1].length', 3),
                                                ('cube[][][3].length', 2)])
def test_length_rows_first(expression, length):
    assert run(main(FILL + f'print("{{@1}}", {expression})'), arrays_config=ArraysConfig(order='rows')) \
        == [str(length)]


def test_foreach_depth_then_columns_then_rows():
    body = FILL + ('foreach (int[][] sheet in cube)\n    foreach (int[] column in sheet)\n'
                   '        foreach (int v in column)\n            write("{v} ")\n    print("|")')
    assert run(main(body)) == ['0 100 10 110 20 120 |', '1 101 11 111 21 121 |',
                               '2 102 12 112 22 122 |', '3 103 13 113 23 123 |']


def test_foreach_rows_first():
    body = ('int[][] m = [[1, 2, 3], [4, 5, 6]]\nforeach (int[] row in m)\n    foreach (int v in row)\n'
            '        write("{v} ")\n    print("|")')
    assert run(main(body), arrays_config=ArraysConfig(order='rows')) == ['1 2 3 |', '4 5 6 |']


def test_a_loop_view_is_borrowed_and_writes_through():
    body = FILL + 'foreach (int[][] s in cube)\n    s[0][0] = 7\nprint("{@1} {@2} {@3}", cube[0][0][0], cube[0][0][3], cube[1][0][0])'
    assert run(main(body)) == ['7 7 100']


def test_the_index_a_loop_view_fixes_is_read_once():
    # r changes inside the loop - the view still is row 0
    body = FILL + 'int r = 0\nforeach (int v in cube[r][1])\n    r = 1\n    write("{v} ")\nprint("|")'
    assert run(main(body)) == ['10 11 12 13 |']


def test_a_held_index_outside_is_an_index_error():
    body = FILL + 'int r = 5\ntry\n    foreach (int v in cube[r][1])\n        print("{v}")\ncatch IndexError e\n    print("{e}")'
    assert run(main(body)) == ['index 5 is outside the array (length 2)']


def test_a_copy_changes_on_its_own():
    body = FILL + ('int[][] sheet = cube[][][3]\nsheet[0][0] = -1\nint[] row = cube[1][2]\nint[3] col = cube[1][][0]\n'
                   'print("{@1} {@2} {@3} {@4}", sheet[0][0], cube[0][0][3], sheet[1][2], sheet.length)\n'
                   'print("{@1} {@2} {@3}", row.length, row[3], col[2])')
    assert run(main(body)) == ['-1 3 123 3', '4 123 120']


def test_strings_looped_and_copied():
    body = ('string[2][2] names = [["a", "b"], ["c", "d"]]\nforeach (string[] col in names)\n'
            '    foreach (string x in col)\n        write(x)\nprint("")\nstring[] top = names[0]\nnames[0][0] = "z"\n'
            'print("{@1}{@2} {@3}", top[0], top[1], names[0][1].length)')
    assert run(main(body)) == ['acbd', 'ab 1']        # a string slot's length is the string's


def test_objects_shared_unless_byval():
    body = ('Car[2][2] cars\ncars[1][1] = Car("red")\nCar[] shared = cars[1]\nCar[] mine = byVal cars[1]\n'
            'shared[1].color = "blue"\nprint("{@1} {@2}", cars[1][1].color, mine[1].color)')
    assert run(CAR + main(body)) == ['blue red']


def test_a_null_slot_in_a_view():
    # Rule 4b: with ?. the code runs on, without it a NullError
    body = ('Car[2][2] cars\ncars[0][1] = Car("red")\nforeach (Car[] col in cars)\n    foreach (Car c in col)\n'
            '        print(c?.color ?? "none")\ntry\n    foreach (Car c in cars[1])\n        print(c.color)\n'
            'catch NullError e\n    print("null")')
    assert run(CAR + main(body)) == ['none', 'none', 'red', 'none', 'null']


@pytest.mark.parametrize('body, message', [
    ('int[2][3] m\nint[][] s = m[1]', "'s' has 2 dimensions - this part of 'm' has 1"),
    ('int[2][3] m\nint[4] r = m[1]', "'r' is int[4] - this part of 'm' is 3"),
    ('int[2][3] m\nfloat[] r = m[1]', "'r' holds float - 'm' holds int"),
    ('int[2][3] m\nint[] r = byRef m[1]', 'a part of an array given to a variable is a copy (D.149)'),
    ('int[2][3] m\nforeach (int[][] x in m)\n    print("x")', "foreach over 'm' gives its columns"),
    ('int[2][3] m\nprint("{@1}", m[1].rows)', "rows is the whole array's"),
    ('int[2][3] m\nint[2][3] n = m', 'copying or replacing a whole array comes with Task 45.12d'),
    ('int[] a = [1, 2]\nint x = a[]', 'an index left out - works on arrays of 2 and 3 dimensions'),
    ('int[2][3] m\nint x = m[0][1][2]', "Cannot index non-array type 'int'"),
])
def test_wrong_uses(body, message):
    assert message in errors_of(main(body))
