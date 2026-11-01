"""Tests for Task 32.11 - [source] caseSensitive (default true; Decisions.md SYN.040).

True: `count` and `Count` are two names, as in most languages. False: names that differ only
in case are an error, each pair listed where the second one is declared.
"""

import pytest

from src.config.project_config import SourceConfig, load_project_config
from src.semantic import SemanticAnalyzer
from tests.test_structs import main, parse


def errors(source: str, case_sensitive: bool) -> list:
    analyzer = SemanticAnalyzer(source_config=SourceConfig(case_sensitive=case_sensitive))
    analyzer.analyze(parse(source))
    return [e.message for e in analyzer.get_errors()]


TWO_COUNTS = main('int count = 1\nint Count = 2\nprint("{@1}", count + Count)')


def test_case_sensitive_by_default_two_names():
    assert errors(TWO_COUNTS, True) == []
    assert SourceConfig().case_sensitive is True


@pytest.mark.parametrize('source, pair', [
    (TWO_COUNTS, "'count' and 'Count'"),                                     # two variables
    (main('int total = 0') + 'int function Total()\n    return 1\n', "'Total' and 'total'"),  # a function and a variable
    ('struct Point\n    int x\n    int X\n\n' + main('Point p = Point(1, 2)'), "'x' and 'X'"),  # fields
    ('enum Color: Red RED\n\n' + main('Color c = Color.Red'), "'Red' and 'RED'"),         # enum values
    ('class Person\n    public string name = "a"\n\n' + main('Person person = Person()'),
     "'Person' and 'person'"),                                               # a type and a variable
    ('void function show(int size)\n    int Size = size\n    print("{@1}", Size)\n\n' + main('show(1)'),
     "'size' and 'Size'"),                                                   # a parameter and a variable
])
def test_not_case_sensitive_lists_each_pair(source, pair):
    found = errors(source, False)
    assert any(pair in e and 'differ only in case' in e for e in found), found


def test_not_case_sensitive_each_pair_once():
    source = 'int function Total()\n    return 1\n\n' + main('int total = 0') + \
        'void function other()\n    int total = 2\n    print("{@1}", total)\n'
    found = [e for e in errors(source, False) if 'differ only in case' in e]
    assert len(found) == 1, found


def test_not_case_sensitive_same_name_twice_is_fine():
    # the same spelling in two functions is one name, not a clash
    source = 'void function a()\n    int n = 1\n    print("{@1}", n)\n\n' + \
        'void function b()\n    int n = 2\n    print("{@1}", n)\n\n' + main('a()\nb()')
    assert errors(source, False) == []


def test_the_setting_is_read(tmp_path):
    (tmp_path / 'fusion.toml').write_text('[source]\ncaseSensitive = false\n')
    (tmp_path / 'p.fusion').write_text('')
    assert load_project_config(str(tmp_path / 'p.fusion')).source.case_sensitive is False


def test_the_setting_must_be_true_or_false(tmp_path):
    from src.config.project_config import ProjectConfigError
    (tmp_path / 'fusion.toml').write_text('[source]\ncaseSensitive = "no"\n')
    (tmp_path / 'p.fusion').write_text('')
    with pytest.raises(ProjectConfigError, match='caseSensitive must be true or false'):
        load_project_config(str(tmp_path / 'p.fusion'))
