"""Task 45.12a - arrays of 2 and 3 dimensions (D.143, D.148): declaring, reading, writing.

`int[2][3][4] cube` is rows x columns x depth, one flat block on the stack. A slot is `cube[1][2][3]`
or `cube[1],[2],[3]`; each index is checked against its own size. `rows`, `columns`, `depth` and
`length` (the outer dimension first) are known while compiling. `[arrays] order` sets how the slots
lie in memory. What isn't built yet - views, passing, copying, looping - is an error naming its
task. Every program runs under the leak check.
"""
import re

import pytest

from src.codegen import CCodeGenerator
from src.config.project_config import ArraysConfig
from src.parser.parser import ParserError
from src.semantic import SemanticAnalyzer
from tests.test_foreach import run
from tests.test_structs import errors_of, main, parse

CAR = 'class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n'


@pytest.mark.parametrize('declaration', ['int[2][3][4] cube', 'int[2],[3],[4] cube', 'int cube[2][3][4]',
                                         'int cube[2],[3],[4]', 'fixed int[2][3][4] cube'])
def test_the_forms_of_a_cube(declaration):
    out = run(main(f'{declaration}\ncube[1][2][3] = 5\ncube[0],[1],[2] = 7\n'
                   'print("{@1} {@2} {@3}", cube[1][2][3], cube[0][1][2], cube[1][1][1])'))
    assert out == ['5 7 0']


def test_sizes():
    out = run(main('int[2][3][4] cube\nint[3][5] m\n'
                   'print("{@1} {@2} {@3} {@4}", cube.rows, cube.columns, cube.depth, cube.length)\n'
                   'print("{@1} {@2} {@3}", m.rows, m.columns, m.length)'))
    assert out == ['2 3 4 4', '3 5 5']          # length: the outer dimension first (D.148)


def test_sizes_rows_first():
    out = run(main('int[2][3][4] cube\nint[3][5] m\nprint("{@1} {@2}", cube.length, m.length)'),
              arrays_config=ArraysConfig(order='rows'))
    assert out == ['2 3']


@pytest.mark.parametrize('order', ['columns', 'rows'])
def test_values_from_nested_lists(order):
    body = ('int[][] m = [[1, 2, 3], [4, 5, 6]]\nint r = 1\nm[r][2] = m[r][2] * 10\n'
            'print("{@1} {@2} {@3} {@4}", m[0][2], m[1][0], m[1][2], m.rows)\n'
            'int[][][] c = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]\nprint("{@1} {@2}", c[0][1][0], c[1][0][1])')
    assert run(main(body), arrays_config=ArraysConfig(order=order)) == ['3 4 60 2', '3 6']


@pytest.mark.parametrize('order, flat', [('columns', '{1, 4, 2, 5, 3, 6}'), ('rows', '{1, 2, 3, 4, 5, 6}')])
def test_the_slots_lie_in_the_order(order, flat):
    # columns first: rows vary fastest - m[0][0] m[1][0] m[0][1] ...; rows first: as C
    analyzer = SemanticAnalyzer(arrays_config=ArraysConfig(order=order))
    ast = parse(main('int[2][3] m = [[1, 2, 3], [4, 5, 6]]\nprint("{@1}", m[1][1])'))
    assert analyzer.analyze(ast), analyzer.get_errors()
    assert f'int m[6] = {flat};' in CCodeGenerator().generate(ast)


def test_strings_are_freed_and_replaced():
    out = run(main('string m[2][2] = [["a", "b"], ["c", "d"]]\nm[1][1] = "z"\nstring[2][3] e\ne[0][0] = "x"\n'
                   'print("{@1}{@2}{@3}[{@4}]{@5}", m[0][0], m[1][0], m[1][1], e[1][2], e[0][0])'))
    assert out == ['acz[]x']


def test_objects_and_null():
    # Rule 4b: an object slot may be null (D.140) - with ?. the code runs on, without it a NullError
    body = ('Car[2][2] cars\ncars[0][1] = Car("red")\nprint(cars[0][1].color)\nprint(cars[1][1]?.color ?? "none")\n'
            'try\n    print(cars[1][0].color)\ncatch NullError e\n    print("null")')
    assert run(CAR + main(body)) == ['red', 'none', 'null']


@pytest.mark.parametrize('read, message', [
    ('m[k][0]', 'index 5 is outside the array (length 2)'),
    ('m[0][k]', 'index 5 is outside the array (length 3)'),
    ('m[0][0 - k]', 'index -5 is outside the array (length 3)'),
])
def test_each_index_is_checked(read, message):
    out = run(main(f'int[2][3] m\nint k = 5\ntry\n    print("{{@1}}", {read})\ncatch IndexError e\n    print("{{e}}")'))
    assert out == [message]


def test_a_written_index_outside_is_a_compile_error():
    assert "Index 3 is outside 'm' - its columns are 0 to 2" in errors_of(main('int[2][3] m\nm[1][3] = 1'))


@pytest.mark.parametrize('body, message', [
    ('int[2][3] m\nprint("{@1}", m[1],[2])', "Can't print a whole int[3] value"),  # inside ( ): two values
    ('int[2][3] m\nforeach (int x in m)\n    print("{x}")',
     "foreach over 'm' gives its columns - each one int[]: foreach (int[] x in ...)"),
    ('int[2][3] m\nint[3][2] n\nbool b = m == n', 'arrays of many dimensions compare when they have the same shape'),
    ('int[2][3] m\nm = [[1, 2], [4, 5]]', "another shape comes with Task 45.12e part 3b"),
    ('int[2][3] m\nprint("{@1}", len(m))', "'m' has 2 dimensions"),
    ('int[2][3] m\nprint("{@1}", m.depth)', "'m' has 2 dimensions - rows and columns; depth is the third"),
    ('int[][] m', "'m' needs its sizes or its values"),
    ('int[][] m = [[1, 2], [3]]', "'m' needs 2 columns here, got 1"),
    ('int[][] m = [1, 2]', 'this needs a list of values [...] here'),
    ('int[2][2] m = [[1, "x"], [3, 4]]', 'A value of \'m\' must be int, got string'),
])
def test_what_isnt_built_yet_or_is_wrong(body, message):
    assert message in errors_of(main(body))


@pytest.mark.parametrize('source, message', [
    ('int[][] function f()\n    int[2][2] m\n    return m\n\n', "'f': give the sizes it returns - int[2][2] function f"),
    ('struct Grid\n    int[2][3] cells\n\n', 'a field of many dimensions comes with Task 45.12c'),
])
def test_parameters_and_fields_come_later(source, message):
    assert message in errors_of(source + main('print("x")'))


@pytest.mark.parametrize('body, message', [
    ('int[2][3][4][5] big', 'more than 3 come with the Collections library'),
    ('int[2][] m', 'Give every size or none'),
    ('int[2][0] m', 'A dimension of size 0'),
    ('int:[2][0] g', 'A dimension of size 0'),
])
def test_wrong_forms(body, message):
    with pytest.raises(ParserError, match=re.escape(message)):
        parse(main(body))


def test_the_stack_measure_counts_every_slot():
    analyzer = SemanticAnalyzer()
    analyzer.analyze(parse(main('int[100][100][2] big')))      # 80,000 bytes
    assert any("'big' takes 80,000 bytes on the stack" in e.message for e in analyzer.get_errors())
