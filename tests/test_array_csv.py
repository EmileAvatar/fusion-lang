"""Task 45.11b - toCSV on arrays of plain values (D.151, the user's choice 2026-11-16).

`a.toCSV(primaryDelimiter = ",", secondaryDelimiter = "#", lineDelimiter = "\\n")`: a line per row, the
values split by the primary delimiter; a one-dimension array one line. 3 dimensions: each line holds
that row of every sheet side by side, the sheets split by the secondary delimiter. The CSV rules: a
value holding a delimiter, a quote or a line break is wrapped in quotes, a quote inside doubled; a null
slot an empty field. `[arrays] csvManyDimensions = false` makes 3 dimensions a compile error. Every
program runs under the leak check.
"""
import pytest

from src.config.project_config import ArraysConfig, ProjectConfigError
from src.semantic import SemanticAnalyzer
from tests.test_foreach import run
from tests.test_settings_formats import load
from tests.test_structs import errors_of, main, parse


def analyze(body, **settings):
    analyzer = SemanticAnalyzer(arrays_config=ArraysConfig(**settings) if settings else None)
    analyzer.analyze(parse(main(body)))
    return [e.message for e in analyzer.get_errors()]


def lines(body, **kwargs):
    return run(main(body), **kwargs)


def test_one_dimension_one_line():
    assert lines('int[] a = [1, 2, 3]\nprint(a.toCSV())') == ['1,2,3']


def test_two_dimensions_a_line_per_row():
    assert lines('int[][] m = [[1, 2, 3], [4, 5, 6]]\nprint(m.toCSV())') == ['1,2,3', '4,5,6']


def test_the_same_with_rows_first():
    out = lines('int[][] m = [[1, 2, 3], [4, 5, 6]]\nprint(m.toCSV())', arrays_config=ArraysConfig(order='rows'))
    assert out == ['1,2,3', '4,5,6']


def test_three_dimensions_sheets_side_by_side():
    # cube[row][column][sheet]: line r holds row r of sheet 0, "#", row r of sheet 1
    body = ('int[2][2][2] c\nc[0][0][0] = 1\nc[0][1][0] = 2\nc[1][0][0] = 3\nc[1][1][0] = 4\n'
            'c[0][0][1] = 5\nc[0][1][1] = 6\nc[1][0][1] = 7\nc[1][1][1] = 8\nprint(c.toCSV())')
    assert lines(body) == ['1,2#5,6', '3,4#7,8']


def test_delimiters_positional_named_and_char():
    body = ('int[][] m = [[1, 2], [3, 4]]\nprint(m.toCSV(";", "#", " | "))\n'
            'print(m.toCSV(lineDelimiter = "/"))\nprint(m.toCSV(\';\'))')
    assert lines(body) == ['1;2 | 3;4', '1,2/3,4', '1;2', '3;4']


def test_quoting_follows_the_csv_rules():
    body = 'string[] s = ["a", "b,c", "say \\"hi\\"", "x"]\nprint(s.toCSV())'
    assert lines(body) == ['a,"b,c","say ""hi""",x']


def test_plain_kinds():
    body = ('bool[] b = [true, false]\nprint(b.toCSV())\ndouble[] d = [1.5, 2.0]\nprint(d.toCSV())\n'
            'char[] c = [\'x\', \'y\']\nprint(c.toCSV())')
    assert lines(body) == ['true,false', '1.5,2', 'x,y']


def test_a_view_and_a_growable_array():
    body = ('int[][] m = [[1, 2, 3], [4, 5, 6]]\nprint(m[1].toCSV())\n'
            'int:[] g\ng.add(7)\ng.add(8)\nprint(g.toCSV())')
    assert lines(body) == ['4,5,6', '7,8']


def test_a_null_enum_slot_is_an_empty_field():
    # Rule 4b: a null slot (D.140) - an empty field, the line goes on
    program = ('enum Color\n    RED\n    GREEN\n\n'
               + main('Color[3] c\nc[0] = Color.RED\nc[2] = Color.GREEN\nprint(c.toCSV())'))
    assert run(program) == ['RED,,GREEN']


def test_three_dimensions_off_is_an_error():
    body = 'int[2][2][2] c\nprint(c.toCSV())\nint[2][2] m\nprint(m.toCSV())'
    errors = analyze(body, csv_many_dimensions=False)
    assert len(errors) == 1 and 'csvManyDimensions' in errors[0]      # 2 dimensions still fine
    assert analyze(body) == []


def test_the_setting_is_read(tmp_path):
    found = load(tmp_path, 'fusion.toml', '[arrays]\ncsvManyDimensions = false\n')
    assert found.arrays.csv_many_dimensions is False
    with pytest.raises(ProjectConfigError, match='true or false'):
        load(tmp_path, 'fusion.toml', '[arrays]\ncsvManyDimensions = "no"\n')


@pytest.mark.parametrize('body, message', [
    ('int[] a = [1]\nprint(a.toCSV(1))', 'string or char'),
    ('int[] a = [1]\nprint(a.toCSV(",", "#", "\\n", ","))', 'three values at most'),
    ('int[] a = [1]\nprint(a.toCSV(sep = ","))', "no value 'sep'"),
])
def test_wrong_values(body, message):
    assert message in errors_of(main(body))
