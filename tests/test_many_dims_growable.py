"""Task 45.12d - growable arrays of 2 and 3 dimensions and `expand` (D.141, D.143).

`int:[2][3][4] g` (also `int[[2],[3],[4]] g`, `int:[][] g = [[...], [...]]`) lives on the heap: one
block, its sizes beside it, changing while running. `g.expand(ROWS / COLUMNS / DEPTH, n)` - the
built-in enum `Dimension` - adds n at the end of that dimension and keeps it a cube; new slots get
the default value; always a warning (every slot is copied). Everything else - slots, parts, loops,
lengths, passing it to `int[][]` - works as on any array. Every program runs under the leak check.
"""
import pytest

from src.config.project_config import ArraysConfig
from src.parser.parser import ParserError
from tests.test_foreach import run
from tests.test_structs import errors_of, main, parse, warnings_of

CAR = 'class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n'
SUM_ALL = ('int function sumAll(int[][] m)\n    int t = 0\n    foreach (int[] column in m)\n        foreach (int v in column)\n'
           '            t = t + v\n    return t\n\n')
G = 'int:[][] g = [\n    [1, 2, 3],\n    [4, 5, 6]]\n'


@pytest.mark.parametrize('order', ['columns', 'rows'])
def test_expand_rows_then_columns(order):
    body = (G + 'g.expand(ROWS, 1)\nprint("{@1} {@2} {@3} {@4}", g.rows, g[2][0], g[1][2], sumAll(g))\n'
            'g.expand(COLUMNS, 2)\ng[2][4] = 9\nprint("{@1} {@2} {@3}", g.columns, g[0][2], g[2][4])')
    assert run(SUM_ALL + main(body), arrays_config=ArraysConfig(order=order)) == ['3 0 6 21', '5 3 9']


@pytest.mark.parametrize('declaration', ['int:[2][2][2] cube', 'int[[2],[2],[2]] cube', 'int cube[[2],[2],[2]]',
                                         'int:[2],[2],[2] cube'])
def test_a_cube_grows_in_depth(declaration):
    body = f'{declaration}\ncube[1][1][1] = 7\ncube.expand(DEPTH, 1)\nprint("{{@1}} {{@2}} {{@3}}", cube.depth, cube[1][1][1], cube[1][1][2])'
    assert run(main(body)) == ['3 7 0']


def test_it_stays_a_cube():
    # a row added to every sheet
    body = 'int:[1][1][2] c\nc[0][0][1] = 5\nc.expand(ROWS, 1)\nprint("{@1} {@2} {@3}", c[1][0][0], c[1][0][1], c[0][0][1])'
    assert run(main(body)) == ['0 0 5']


def test_strings_moved_and_new_ones_empty():
    body = ('string:[2][2] names\nnames[0][0] = "a"\nnames.expand(Dimension.ROWS, 1)\nnames[2][1] = "z"\n'
            'foreach (string[] col in names)\n    foreach (string s in col)\n        write("{s},")\nprint("")')
    assert run(main(body)) == ['a,,,,,z,']


def test_objects_and_null():
    # Rule 4b: a new slot of an object type is null - with ?. the code runs on, without it a NullError
    body = ('Car:[1][1] cars\ncars[0][0] = Car("red")\ncars.expand(COLUMNS, 1)\nprint(cars[0][0].color)\n'
            'print(cars[0][1]?.color ?? "none")\ntry\n    print(cars[0][1].color)\ncatch NullError e\n    print("null")')
    assert run(CAR + main(body)) == ['red', 'none', 'null']


def test_the_dimension_in_a_variable():
    body = G + 'Dimension d = COLUMNS\ng.expand(d, 1)\nprint("{@1}", g.columns)'
    assert run(main(body)) == ['4']


def test_expand_by_less_than_one_is_an_error_while_running():
    body = G + 'int n = 0\ntry\n    g.expand(ROWS, n)\ncatch IndexError e\n    print("{e}")'
    assert run(main(body)) == ['expand by 0 - it grows by 1 or more']


def test_always_a_warning():
    assert 'expand copies every slot of' in warnings_of(main(G + 'g.expand(ROWS, 1)'))


def test_a_program_without_it_has_no_dimension_enum():
    from src.codegen import CCodeGenerator
    from src.semantic import SemanticAnalyzer
    ast = parse(main('print("x")'))
    SemanticAnalyzer().analyze(ast)
    assert 'Dimension' not in CCodeGenerator().generate(ast)


@pytest.mark.parametrize('body, message', [
    ('int[2][3] m\nm.expand(ROWS, 1)', "expand: 'm' doesn't grow - only a growable array does"),
    ('fixed int[2][3] m\nm.expand(ROWS, 1)', "doesn't grow"),
    (G + 'g.expand(0, 1)', 'expand(0, 1) - comes with the Collections library'),
    (G + 'g.expand(DEPTH, 1)', "'g' has 2 dimensions - rows and columns; DEPTH is the third"),
    (G + 'g.expand(ROWS)', 'expand takes two values'),
    (G + 'g.expand(ROWS, "x")', 'how many is an int'),
    ('int:[][] g', "'g' needs its sizes or its values"),
    (G + 'foreach (int[] c in g)\n    g.expand(ROWS, 1)', "'g' is being looped over - it can't expand inside the loop"),
    (G + 'foreach (int[] c in g)\n    foreach (int v in c)\n        g.expand(ROWS, 1)', "it can't expand inside the loop"),
])
def test_wrong_uses(body, message):
    assert message in errors_of(main(body))


@pytest.mark.parametrize('body, message', [
    ('fixed int:[2][3] g', "fixed and a growable array can't go together"),
    ('int:[2][3][4][5] g', 'more than 3 come with the Collections library'),
    ('int:[2][] g', 'Give every size or none'),
])
def test_wrong_forms(body, message):
    with pytest.raises(ParserError, match=message.replace('(', r'\(').replace(')', r'\)')):
        parse(main(body))
