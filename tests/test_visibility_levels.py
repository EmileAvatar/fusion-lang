"""Tests for Task 32.2h - private / internal / public, namespaces, `[visibility] required`
(Classes.md section 1, files/FusionTemplate.md).

private - the class; internal - the namespace (a file without one: its module); public -
everyone. Nothing written: fields and module variables private, everything else public.
`private` on a top-level item is an error (tests/test_modules.py). `namespace A.B` is the
file's first line. Each test is a row of the table.
"""

import pytest

from src.config.project_config import VisibilityConfig
from src.semantic import SemanticAnalyzer
from tests.test_modules import errors as module_errors, run_project
from tests.test_structs import main, parse

# Two modules in namespace Shop, and the main file outside it
SHOP = {
    'stock/s.fusion': ('namespace Shop\n\n'
                       'internal int function count() : 7\n\n'
                       'class Shelf\n'
                       '    internal int items = 3\n'
                       '    public int shown = 1\n'
                       '    internal constructor()\n'
                       '        items = items + 1\n'
                       '    internal int function peek() : items\n'
                       '    public static Shelf function make() : Shelf()\n'),
    'till/t.fusion': ('namespace Shop\n\n'
                      'import stock\n\n'
                      'public string function report()\n'
                      '    stock.Shelf s = stock.Shelf()\n'          # internal constructor
                      '    return format("{@1} {@2} {@3}", stock.count(), s.items, s.peek())\n'),
}


def test_internal_is_shared_inside_the_namespace(tmp_path):
    files = dict(SHOP)
    files['main.fusion'] = ('import till\nimport stock\n\n'
                            'void function main()\n'
                            '    print(till.report())\n'
                            '    stock.Shelf s = stock.Shelf.make()\n'
                            '    print("{s.shown}")\n')
    assert run_project(str(tmp_path), files) == ['7 4 4', '1']


@pytest.mark.parametrize('line, message', [
    ('int n = stock.count()', "'count' is internal to namespace Shop - only names marked public "
                              "can be used from another module"),
    ('stock.Shelf s = stock.Shelf()', "The constructor of class 'stock.Shelf' is internal - only "
                                      "its namespace Shop can use it"),
    ('stock.Shelf s = stock.Shelf.make()\n    int n = s.items',
     "Field 'items' of class 'stock.Shelf' is internal - only its namespace Shop can use it"),
    ('stock.Shelf s = stock.Shelf.make()\n    int n = s.peek()',
     "Function 'peek' of class 'stock.Shelf' is internal - only its namespace Shop can use it"),
])
def test_internal_from_outside_the_namespace_is_an_error(tmp_path, line, message):
    files = dict(SHOP)
    files['main.fusion'] = f'import stock\n\nvoid function main()\n    {line}\n'
    assert message in module_errors(str(tmp_path), files)


def test_internal_in_a_file_without_a_namespace_is_its_module(tmp_path):
    files = {'m/a.fusion': 'internal int function secret() : 2\n',
             'm/b.fusion': 'public int function twice() : secret() * 2\n',   # same module
             'main.fusion': 'import m\n\nvoid function main()\n    print(format("{@1}", m.twice()))\n'}
    assert run_project(str(tmp_path), files) == ['4']
    files['main.fusion'] = 'import m\n\nvoid function main()\n    int n = m.secret()\n'
    assert "'secret' is internal to module 'm'" in module_errors(str(tmp_path), files)


def test_a_single_file_may_have_a_namespace(tmp_path):
    from tests.test_end_to_end import compile_and_run
    assert compile_and_run('namespace App.Tools\n\n'
                           'class Box\n    internal int n = 5\n\n'
                           + main('Box b = Box()\nprint("{b.n}")'))[1].split() == ['5']


def required_errors(source: str) -> str:
    analyzer = SemanticAnalyzer(visibility_config=VisibilityConfig(required=True))
    analyzer.analyze(parse(source))
    return '\n'.join(str(e) for e in analyzer.get_errors())


def test_visibility_required_makes_a_missing_level_an_error():
    found = required_errors('struct Point\n    int x\n\n'
                            'enum Kind: A B\n\n'
                            'int function helper() : 1\n\n'
                            'int count = 0\n\n'
                            'class Car\n'
                            '    int speed\n'
                            '    static int made\n'
                            '    constructor()\n'
                            '        speed = 1\n'
                            '    void function drive()\n'
                            '        speed = 2\n\n' + main('print("x")'))
    for what in ("struct 'Point'", "enum 'Kind'", "function 'helper'", "module variable 'count'",
                 "class 'Car'", "field 'speed'", "field 'made'", "the constructor of 'Car'",
                 "function 'drive'"):
        assert f"Write who can use {what} - public, internal or private" in found, what
    assert "'main'" not in found


def test_visibility_required_passes_when_every_level_is_written():
    assert required_errors('public struct Point\n    int x\n\n'
                           'internal int function helper() : 1\n\n'
                           'private int count = 0\n\n'
                           'public class Car\n'                       # no constructor written
                           '    private int speed\n'
                           '    public static int made\n'
                           '    public void function drive()\n'
                           '        speed = 2\n\n' + main('print("x")')) == ''
