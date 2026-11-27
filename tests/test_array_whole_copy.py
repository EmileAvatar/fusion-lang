"""Task 45.12e (parts 1 and 2) - a whole array on the stack given to a new one (D.025).

`int[3] b = a` / `int[2][3] n = m`: the slots are copied and `a` moves - it can't be used after (as a
List); `byVal a` copies deeply and `a` stays usable. The sizes taken from the source when left out
(`int[][] n = m`), else they must agree. Every program runs under the leak check.
"""
import pytest

from tests.test_foreach import run
from tests.test_structs import errors_of, main

CAR = 'class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n'


@pytest.mark.parametrize('body, out', [
    ('int[3] a = [1, 2, 3]\nint[3] b = a\nb[0] = 9\nprint("{@1} {@2}", b[0], b.length)', ['9 3']),
    ('int[3] a = [1, 2, 3]\nint[] b = byVal a\nb[0] = 9\nprint("{@1} {@2}", a[0], b[0])', ['1 9']),
    ('string[2] a = ["x", "y"]\nstring[2] b = byVal a\nstring[2] c = a\nprint("{@1}{@2}{@3}", b[0], c[1], b[1])',
     ['xyy']),
    ('int[2][3] m = [[1, 2, 3], [4, 5, 6]]\nint[2][3] n = m\nprint("{@1} {@2} {@3}", n[1][2], n.rows, n.columns)',
     ['6 2 3']),
    ('int[][] m = [[1, 2, 3], [4, 5, 6]]\nint[][] n = byVal m\nn[0][0] = 9\nprint("{@1} {@2}", m[0][0], n[0][0])',
     ['1 9']),
    ('string[2][2][2] c\nc[1][1][1] = "z"\nstring[][][] d = byVal c\nprint("{@1} {@2}", d[1][1][1], c[1][1][1])',
     ['z z']),
])
def test_copies_and_moves(body, out):
    assert run(main(body)) == out


def test_objects_moved_and_copied():
    # Rule 4b: a null object slot copied as null - read with ?. it runs on
    body = ('Car[2] a\na[0] = Car("red")\nCar[2] b = byVal a\nb[0].color = "blue"\n'
            'print("{@1} {@2} {@3}", a[0].color, b[0].color, b[1]?.color ?? "none")\n'
            'Car[2] c = a\nprint("{@1}", c[0].color)')
    assert run(CAR + main(body)) == ['red blue none', 'red']


FN = 'int[2][2] function f()\n    int[2][2] r = [[1, 2], [3, 4]]\n    return r\n\n'


@pytest.mark.parametrize('body, out', [
    ('int[2][3] m = [[1, 2, 3], [4, 5, 6]]\nm = [[7, 8, 9], [1, 2, 3]]\nprint("{@1} {@2}", m[0][0], m[1][2])', ['7 3']),
    ('string[2][2] m = [["a", "b"], ["c", "d"]]\nm = [["w", "x"], ["y", "z"]]\nprint("{@1}{@2}", m[0][0], m[1][1])',
     ['wz']),
    ('string[2][2] m\nstring[2][2] n = [["w", "x"], ["y", "z"]]\nm = byVal n\nprint("{@1}{@2}", m[0][0], n[1][1])',
     ['wz']),
    ('string[2][2] m = [["a", "b"], ["c", "d"]]\nm = m\nprint("{@1}", m[1][1])', ['d']),
    ('int[2][2] m\nm = f()\nprint("{@1}", m[1][1])', ['4']),
    ('int[2][2][2] c\nc = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]\nprint("{@1}", c[1][0][1])', ['6']),
    ('string[2][2] m\nint i = 0\nwhile i < 3\n    m = [["a{i}", "b"], ["c", "d"]]\n    i = i + 1\nprint("{@1}", m[0][0])',
     ['a2']),
])
def test_replacing_with_the_same_shape(body, out):
    # 45.12e part 3: the new slots made first, then the old ones freed (strings) and replaced
    assert run(FN + main(body)) == out


@pytest.mark.parametrize('body, out', [
    ('int[2][3] m = [[1, 2, 3], [4, 5, 6]]\nm = [[7, 8], [1, 2], [3, 4]]\nprint("{@1} {@2} {@3}", m.rows, m.columns, m[2][1])',
     ['3 2 4']),
    ('string[][] m = [["a", "b"]]\nm = [["w", "x", "y"], ["z", "q", "r"]]\nprint("{@1} {@2}", m[1][2], m.columns)',
     ['r 3']),
    ('int:[][] g = [[1, 2], [3, 4]]\ng = [[5, 6, 7]]\ng.expand(Dimension.ROWS, 1)\nprint("{@1} {@2} {@3}", g.rows, g[0][2], g[1][2])',
     ['2 7 0']),
    ('string:[][] g = [["a"]]\nstring[2][2] n = [["w", "x"], ["y", "z"]]\ng = byVal n\nprint("{@1} {@2}", g[1][1], n[0][0])',
     ['z w']),
    ('int[2][2][2] c\nc = [[[1, 2, 3]]]\nprint("{@1} {@2}", c[0][0][2], c.depth)', ['3 3']),
    ('string[][] m = [["a"]]\nint i = 0\nwhile i < 3\n    m = [["x{i}", "y"], ["z", "w"]]\n    i = i + 1\nprint("{@1}", m[0][0])',
     ['x2']),
    ('int[2][2] m\nm = [[1, 2, 3], [4, 5, 6]]\nList<List<int>> l = m.toList()\nprint("{@1} {@2}", l.len(), l[2][1])',
     ['3 6']),
])
def test_replacing_with_another_shape(body, out):
    # 45.12e part 3b: a plain array given another shape lives on the heap (as a growable one, but
    # never expands); a growable one takes any shape - a new block, the old slots and block freed
    assert run(main(body)) == out


@pytest.mark.parametrize('body, message', [
    ('int[3] a = [1, 2, 3]\nint[3] b = a\nprint("{@1}", a[0])', "'a' was moved to 'b'"),
    ('int[2][2] m\nint[2][2] n\nm = n\nprint("{@1}", n[0][0])', "'n' was moved to 'm'"),
    ('int[2][3] m\nint[3][2] n\nm = n', 'from another array the same shape only'),
    ('int[2][3] m\nm = [[7, 8], [1, 2], [3, 4]]\nm.expand(Dimension.ROWS, 1)', "'m' is a plain array"),
    ('int:[][] g = [[1]]\nint[][] n = byVal g', 'lives on the heap'),
    ('fixed int[2][2] m\nm = [[1, 2], [3, 4]]', "'m' is fixed"),
    ('int[2][2] m\nm = 5', 'it is replaced by values'),
    ('int[2][3] m\nint[2][3] n = m\nprint("{@1}", m[0][0])', "'m' was moved to 'n'"),
    ('int[2][3] m\nint[3][2] n = m', 'the sizes must agree'),
    ('int[2][3] m\nint[6] n = m', 'one of the same type'),
    ('int[3] a\nstring[3] s = a', 'one of the same type'),
])
def test_errors(body, message):
    assert message in errors_of(main(body))
