"""Task 45.15 part 1 - how an array of 2 or 3 dimensions is stored (D.144, D.147, D.153, D.164).

- `[arrays] storage = "flat"` (the default); "rect" comes later (D.164); "jagg" is per array only (D.153)
- `m.setStorage(FLAT)` / `setStorage(null)`: right after the declaration - the next line, or in its
  set-up block (D.147); anywhere else an error
- RECT: an error "comes later"; JAGG: only on a growable array (D.153) - built in part 2
- the built-in enum `Storage` is added only to a program that uses it
"""

import pytest

from src.config.project_config import ProjectConfigError, _load_arrays_section
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
    ('int:[][] g = [[1, 2], [3, 4]]\ng.setStorage(JAGG)', 'JAGG storage is being built'),
    ('int[2][3] m\nm.setStorage(5)', 'the storage is FLAT, JAGG or null'),
    ('int[2][3] m\nm.setStorage()', 'setStorage takes one value'),
])
def test_wrong_storage_is_an_error(body, message):
    assert any(message in e for e in errors_of(body)), errors_of(body)


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
