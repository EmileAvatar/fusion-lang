"""Task 45.15 part 1 - how an array of 2 or 3 dimensions is stored (D.144, D.147, D.153, D.164).

- `[arrays] storage = "flat"` (the default); "rect" comes later (D.164); "jagg" is per array only (D.153)
- `m.setStorage(FLAT)` / `setStorage(null)`: right after the declaration - the next line, or in its
  set-up block (D.147); anywhere else an error
- RECT: an error "comes later"; JAGG: only on a growable array (D.153) - built in part 2
- the built-in enum `Storage` is added only to a program that uses it
"""

import pytest

from src.config.project_config import ArraysConfig, ProjectConfigError, _load_arrays_section
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_structs import main, parse


def errors_of(body: str) -> list:
    analyzer = SemanticAnalyzer()
    analyzer.analyze(parse(main(body)))
    return [e.message for e in analyzer.get_errors()]


@pytest.mark.parametrize('body', [
    'int[2][3] m\nm.setStorage(FLAT)\nm[1][2] = 5\nprint("{@1}", m[1][2])',
    'int[2][3] m\nm.setStorage(Storage.FLAT)\nm[1][2] = 5\nprint("{@1}", m[1][2])',
    'int[2][3] m\nm.setStorage(null)\nm[1][2] = 5\nprint("{@1}", m[1][2])',
    'int[2][3] m = [[1, 2, 3], [4, 5, 6]] {\n    m.setStorage(FLAT)\n}\nm[1][2] = 5\nprint("{@1}", m[1][2])',
    'int[2][3][2] c\nc.setStorage(FLAT)\nc[1][2][1] = 5\nprint("{@1}", c[1][2][1])',
])
def test_flat_right_after_the_declaration_runs(body):
    code, out, err = compile_and_run(main(body))
    assert code == 0, err
    assert out.strip().splitlines()[0] == '5'


@pytest.mark.parametrize('body, message', [
    ('int[2][3] m\nm[0][0] = 1\nm.setStorage(FLAT)', 'setStorage comes right after'),
    ('int[3] a\na.setStorage(FLAT)', 'setStorage is for an array of 2 or 3 dimensions'),
    ('int[2][3] m\nm.setStorage(RECT)', 'RECT storage comes later'),
    ('int[2][3] m\nm.setStorage(JAGG)', 'JAGG is only for a growable array'),
    ('int:[2][2][2] g\ng.setStorage(JAGG)', 'JAGG on 3 dimensions comes later'),
    ('int:[][] j = [[1], [2, 3]]\nj.setStorage(JAGG)\nprint("{@1}", j.length)', "'j' is jagged"),
    ('int:[][] j = [[1], [2, 3]]\nj.setStorage(JAGG)\nj.expand(ROWS, 1)', "has no method 'expand'"),
    ('int:[][] j = [[1], [2, 3]]\nprint("{@1}", j[0][0])\nj.setStorage(JAGG)', 'setStorage comes right after'),
    ('int[2][3] m\nm.setStorage(5)', 'the storage is FLAT, JAGG or null'),
    # 45.6: growing an array that doesn't grow says how to get one that does
    ('int[3] a\na.add(4)', "a plain or fixed array doesn't grow or shrink - declare it int:[]"),
    ('fixed int[3] a\nprint("{@1}", a.removeLast())', "a plain or fixed array doesn't grow or shrink"),
    ('int[2][2] m\nm.add([1, 2])', 'grows with expand(ROWS, 1)'),
    ('int:[][] g = [[1, 2], [3, 4]]\ng.add([1, 2])', "an array of many dimensions doesn't grow by its items"),
    ('int:[][] j = [[1], [2, 3]]\nj.setStorage(JAGG)\nprint(j.toCSV())', 'toCSV on a jagged array comes later'),
    ('int[2][3] m\nm.setStorage()', 'setStorage takes one value'),
])
def test_wrong_storage_is_an_error(body, message):
    assert any(message in e for e in errors_of(body)), errors_of(body)


JAGGED = 'int:[][] j = [[1], [2, 3, 4], [5, 6]]\nj.setStorage(JAGG)\n'


def run(body: str, **options) -> list:
    code, out, err = compile_and_run(main(body), analyzer_options=options or None)   # under the leak check
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_jagged_rows_each_their_own_length():
    lines = run(JAGGED + 'print("{@1} {@2} {@3}", j.rows, j.columns, j[1].columns)\n'
                         'print("{@1} {@2}", j[1][2], j[2][0])\n'
                         'j[1].add(9)\nj[0][0] = 7\nj.add([8, 8])\n'
                         'print("{@1} {@2} {@3} {@4}", j[1][3], j[0][0], j[3][1], j.rows)')
    assert lines == ['3 0 3', '4 5', '9 7 8 4']


def test_an_empty_jagged_array_gives_0():
    # D.163: an array is empty by default - its rows and columns are 0, never null or an error
    assert run('int:[][] e\ne.setStorage(JAGG)\nprint("{@1} {@2}", e.rows, e.columns)') == ['0 0']


def test_a_slot_outside_its_row_is_an_index_error():
    code, out, err = compile_and_run(main(JAGGED + 'print("{@1}", j[0][1])'))
    assert code != 0 and 'outside' in (out + err)


@pytest.mark.parametrize('order, lines', [
    # columns first (the default, D.148): each column from the rows long enough for it (D.163)
    ('columns', ['3: 1', '2: 3', '1: 4']),
    # rows first: each row as it is
    ('rows', ['1: 1', '3: 2', '2: 5']),
])
def test_walking_follows_the_order(order, lines):
    body = JAGGED + 'foreach (int[] part in j)\n    print("{@1}: {@2}", part.length, part[0])'
    assert run(body, arrays_config=ArraysConfig(order=order)) == lines


def test_jagged_strings_are_copied_and_freed():
    body = ('string:[][] s = [["a"], ["b", "c"]]\ns.setStorage(JAGG)\ns[1].add("d")\n'
            'foreach (string[] column in s)\n    print("{@1} {@2}", column.length, column[0])')
    assert run(body) == ['2 a', '1 c', '1 d']


def test_jagged_in_its_set_up_block():
    body = 'int:[][] j = [[1], [2, 3]] {\n    j.setStorage(JAGG)\n}\nprint("{@1}", j[1].columns)'
    assert run(body) == ['2']


CUBE = ('int[2][3][2] cube\n'
        'for r in range(0, 2)\n    for c in range(0, 3)\n        for d in range(0, 2)\n'
        '            cube[r][c][d] = r * 100 + c * 10 + d\n'
        'string text = ""\n'
        'foreach (int[][] a in cube)\n    foreach (int[] b in a)\n        foreach (int v in b)\n'
        '            text = text + "{v} "\n'
        'print("{@1} | {@2}", cube.length, text)')


@pytest.mark.parametrize('order, line', [
    ('columns', '2 | 0 100 10 110 20 120 1 101 11 111 21 121'),       # depth -> columns -> rows
    ('rows', '2 | 0 1 10 11 20 21 100 101 110 111 120 121'),          # rows -> columns -> depth
    ('depthRows', '2 | 0 10 20 100 110 120 1 11 21 101 111 121'),     # depth -> rows -> columns (part 3)
])
def test_the_three_walk_orders(order, line):
    assert [l.rstrip() for l in run(CUBE, arrays_config=ArraysConfig(order=order))] == [line]


@pytest.mark.parametrize('order', ['columns', 'rows', 'depthRows'])
def test_expand_keeps_every_slot_in_each_order(order):
    body = ('int:[2][2][2] g\ng[1][1][1] = 7\ng[0][1][0] = 3\ng.expand(COLUMNS, 1)\ng[1][2][1] = 9\n'
            'print("{@1} {@2} {@3} {@4}", g[1][1][1], g[0][1][0], g[1][2][1], g.columns)')
    assert run(body, arrays_config=ArraysConfig(order=order)) == ['7 3 9 3']


def test_the_order_setting_takes_depth_rows():
    assert _load_arrays_section({'arrays': {'order': 'depthRows'}}, 'fusion.toml').order == 'depthRows'


def test_the_storage_enum_only_where_used():
    program = parse(main('int x = 1'))
    SemanticAnalyzer().analyze(program)
    assert not any(getattr(d, 'name', None) == 'Storage' for d in program.declarations)


@pytest.mark.parametrize('value, message', [
    ('rect', 'comes later'),
    ('jagg', 'a jagged array says so where it is made'),
    ('wide', 'must be "flat"'),
])
def test_the_project_setting(value, message):
    with pytest.raises(ProjectConfigError, match=message):
        _load_arrays_section({'arrays': {'storage': value}}, 'fusion.toml')
    assert _load_arrays_section({'arrays': {'storage': 'flat'}}, 'fusion.toml').storage == 'flat'
