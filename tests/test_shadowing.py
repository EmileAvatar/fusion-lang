"""Task 47.12 - `[source] shadowing` (D.200).

false (default): a variable, parameter or loop variable with the name of one further out - an outer block, a
parameter, a module variable or constant - is a compile error naming where the other is.
true: allowed - a name means the nearest one; `::total` reaches the module's, `this.total` the object's field.
"""
import pytest

from src.config.project_config import SourceConfig, load_project_config, ProjectConfigError
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_structs import parse

ON = {'source_config': SourceConfig(shadowing=True)}


def run(source: str, options=ON) -> list:
    code, out, err = compile_and_run(source, analyzer_options=options)
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def errors_of(source: str, options=None) -> list:
    analyzer = SemanticAnalyzer(**(options or {}))
    analyzer.analyze(parse(source))
    return [e.message for e in analyzer.get_errors()]


MODULE = 'int total = 10\n\n'
BLOCKS = ('void function main()\n    int count = 1\n    if true\n        int count = 2\n        count = count + 5\n'
          '        print("{count}")\n    print("{count}")\n')
LOOP = 'void function main()\n    int i = 7\n    for i in 0...1\n        print("{i}")\n    print("{i}")\n'
MODULE_LOCAL = (MODULE + 'void function main()\n    int total = 0\n    for num in [1, 2, 3]\n        total = total + num\n'
                '        ::total = ::total + num\n    print("{total} {@1}", ::total)\n')


# ---- off (the default): an error ----

@pytest.mark.parametrize('source, message', [
    (BLOCKS, "Variable 'count' has the name of a variable further out (line 2)"),
    (LOOP, "Loop variable 'i' has the name of a variable further out (line 2)"),
    (MODULE + 'void function main()\n    int total = 0\n    print("{total}")\n',
     "Variable 'total' has the same name as the module variable 'total'"),
    ('const int LIMIT = 3\n\nvoid function main()\n    int LIMIT = 4\n    print("{LIMIT}")\n', "module"),
])
def test_off_a_name_further_out_is_an_error(source, message):
    found = errors_of(source)
    assert any(message in e and '[source] shadowing = true' in e for e in found), found


def test_off_two_blocks_side_by_side_are_fine():
    # not shadowing - neither block is further out than the other
    assert run('void function main()\n    if true\n        int n = 1\n        print("{n}")\n    if true\n'
               '        int n = 2\n        print("{n}")\n', None) == ['1', '2']


def test_off_module_scope_is_an_error():
    found = errors_of(MODULE + 'void function main()\n    print("{@1}", ::total)\n')
    assert any("[source] shadowing is off, so nothing hides it: write total" in e for e in found), found


# ---- on: the nearest wins ----

def test_on_the_inner_block_wins():
    assert run(BLOCKS) == ['7', '1']


def test_on_a_loop_variable_hides_a_local():
    assert run(LOOP) == ['0', '1', '7']


def test_on_a_local_hides_the_module_variable_and_double_colon_reaches_it():
    assert run(MODULE_LOCAL) == ['6 16']


def test_on_module_scope_needs_a_module_variable():
    found = errors_of('void function main()\n    int x = 1\n    print("{@1}", ::x)\n', ON)
    assert any("there is no module variable 'x'" in e for e in found), found


def test_on_a_field_is_reached_by_this():
    source = ('class Orders\n    public int total = 100\n\n    public int function sum(int[] numbers)\n'
              '        int total = 0\n        for num in numbers\n            total = total + num\n'
              '            this.total = this.total + num\n        return total\n\n'
              'void function main()\n    Orders o = Orders()\n    int[] xs = [1, 2]\n'
              '    print("{@1} {@2}", o.sum(xs), o.total)\n')
    assert run(source) == ['3 103']


# ---- the setting ----

def test_the_setting_is_read(tmp_path):
    (tmp_path / 'fusion.toml').write_text('[source]\nshadowing = true\n', encoding='utf-8')
    assert load_project_config(str(tmp_path / 'main.fusion')).source.shadowing is True
    (tmp_path / 'fusion.toml').write_text('[source]\nshadowing = "yes"\n', encoding='utf-8')
    with pytest.raises(ProjectConfigError):
        load_project_config(str(tmp_path / 'main.fusion'))
