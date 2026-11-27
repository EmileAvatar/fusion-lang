"""Tests for Task 57 - namespaces and modules (D.204-D.213, files/spec/150-Modules.md).

57.1 (D.204, D.207): the folder gives a file's namespace and module - SQL/Database/ is namespace SQL, module Database;
money/ is module money without a namespace. The `namespace` / `module` lines are optional, and one that doesn't match
the folder is an error naming both. `internal` is shared by every module of the folder's namespace. The main file is
the program - in no namespace or module.
"""

import pytest

from src.parser.parser import ParserError
from tests.test_modules import errors, parse_file, run_project

MAIN_SQL = ('import SQL.Database\n\n'
            'void function main()\n'
            '    print(Database.name())\n')


@pytest.mark.parametrize('lines', [
    '',                                     # nothing written - the folder decides
    'namespace SQL\n\n',                    # the namespace only
    'module Database\n\n',                  # the module only
    'namespace SQL\nmodule Database\n\n',   # both
])
def test_the_lines_are_optional_and_match_the_folder(tmp_path, lines):
    files = {'SQL/Database/d.fusion': lines + 'public string function name() : "sql"\n',
             'main.fusion': MAIN_SQL}
    assert run_project(str(tmp_path), files) == ['sql']


@pytest.mark.parametrize('folder, lines, message', [
    ('SQL/Database', 'namespace Shop\n',
     "SQL/Database/d.fusion says 'namespace Shop', but its folder SQL/Database/ makes it namespace SQL - "
     "write 'namespace SQL', or move the file"),
    ('SQL/Database', 'module Data\n',
     "SQL/Database/d.fusion says 'module Data', but its folder SQL/Database/ makes it module Database - "
     "write 'module Database', or move the file"),
    ('SQL/Database', 'namespace SQL\nmodule Data\n', "makes it module Database"),
    ('Database', 'namespace SQL\n',
     "Database/d.fusion says 'namespace SQL', but its folder Database/ is a module without a namespace - "
     "move the module into a folder SQL/ (SQL/Database/), or remove the line"),
    ('a/b/Database', 'namespace a\n', "makes it namespace a.b"),
])
def test_a_line_that_does_not_match_the_folder_is_an_error(tmp_path, folder, lines, message):
    files = {f'{folder}/d.fusion': lines + '\npublic string function name() : "sql"\n',
             'main.fusion': f'import {folder.replace("/", ".")}\n\nvoid function main()\n    print("x")\n'}
    assert message in errors(str(tmp_path), files)


def test_internal_is_shared_by_the_folders_namespace(tmp_path):
    # D.207: no lines written - Shop/stock and Shop/till share Shop's internal names
    files = {'Shop/stock/s.fusion': 'internal int function count() : 7\n',
             'Shop/till/t.fusion': ('import Shop.stock\n\n'
                                    'public int function report() : stock.count() * 2\n'),
             'main.fusion': ('import Shop.till\n\n'
                             'void function main()\n'
                             '    print(format("{@1}", till.report()))\n')}
    assert run_project(str(tmp_path), files) == ['14']


def test_internal_is_not_shared_with_another_namespace(tmp_path):
    files = {'Shop/stock/s.fusion': 'internal int function count() : 7\n',
             'Office/desk/d.fusion': ('import Shop.stock\n\n'
                                      'public int function report() : stock.count()\n'),
             'main.fusion': ('import Office.desk\n\n'
                             'void function main()\n'
                             '    print(format("{@1}", desk.report()))\n')}
    assert "'count' is internal to namespace Shop" in errors(str(tmp_path), files)


@pytest.mark.parametrize('line', ['namespace App', 'module App', 'namespace App\nmodule Tools'])
def test_the_main_file_has_no_namespace_or_module(tmp_path, line):
    files = {'main.fusion': f'{line}\n\nvoid function main()\n    print("x")\n'}
    assert "The main file is the program - it belongs to no namespace or module" in errors(str(tmp_path), files)


# 57.2 (D.211, D.212): a module in a namespace is structured - its top-level functions and variables are static,
# written out or added with a warning; a type may be private - its module only

def warnings(root, files: dict) -> list:
    from src.modules import load_program
    from src.semantic import SemanticAnalyzer
    from tests.test_modules import write_project
    main_file = write_project(root, files)
    with open(main_file, encoding='utf-8') as f:
        program = parse_file(f.read(), main_file)
    program, import_errors = load_program(main_file, program, parse_file)
    assert import_errors == []
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(program), [str(e) for e in analyzer.get_errors()]
    return [str(w) for w in analyzer.get_warnings()]


MAIN_PRICING = ('import Shop.Pricing\n\n'
              'void function main()\n'
              '    print(format("{@1}", Pricing.make(5)))\n')


@pytest.mark.parametrize('module_text, expected', [
    ('public static int function make(int n) : n * 2\n', []),
    ('static int function make(int n) : n * 2\n', []),
    ('int function make(int n) : n * 2\n',
     ["Function 'make' is at the top of module Shop.Pricing, so it is static - write 'public static' before it, "
      "or put it in a class (D.212)"]),
    ('internal int function helper() : 2\n\npublic static int function make(int n) : n * helper()\n',
     ["Function 'helper' is at the top of module Shop.Pricing, so it is static - write 'internal static'"]),
    ('static int made = 0\n\npublic static int function make(int n) : n * 2\n', []),
    ('int made = 0\n\npublic static int function make(int n) : n * 2\n',
     ["Variable 'made' is at the top of module Shop.Pricing, so it is static - write 'static' before it (D.212)"]),
    ('public int shown = 0\n\npublic static int function make(int n) : n * 2\n',
     ["write 'public static' before it"]),
    ('const int TIMES = 2\n\npublic static int function make(int n) : n * TIMES\n', []),
    ('enum Kind { A, B }\n\ninterface Sized\n    int function size()\n\n'
     'public static int function make(int n) : n * 2\n', []),
])
def test_a_structured_modules_functions_and_variables_are_static(tmp_path, module_text, expected):
    files = {'Shop/Pricing/m.fusion': module_text, 'main.fusion': MAIN_PRICING}
    found = warnings(str(tmp_path), files)
    assert len(found) == len(expected), found
    for text, warning in zip(expected, found):
        assert text in warning
    assert run_project(str(tmp_path), files) == ['10']


def test_a_module_without_a_namespace_is_naked(tmp_path):
    # D.211: money/ has no namespace - free, as today: no warning
    files = {'money/m.fusion': 'int made = 0\n\npublic int function make(int n) : n * 2\n',
             'main.fusion': 'import money\n\nvoid function main()\n    print(format("{@1}", money.make(5)))\n'}
    assert warnings(str(tmp_path), files) == []


def test_a_private_type_is_its_modules_only(tmp_path):
    module_text = ('private struct Box\n    int n\n\n'
                   'public static int function make(int n)\n'
                   '    Box b = Box(n * 2)\n'
                   '    return b.n\n')
    files = {'Shop/Pricing/m.fusion': module_text, 'main.fusion': MAIN_PRICING}
    assert run_project(str(tmp_path), files) == ['10']
    files['main.fusion'] = 'import Shop.Pricing\n\nvoid function main()\n    Pricing.Box b = Pricing.Box(1)\n'
    assert "'Box' is private to module 'Shop.Pricing'" in errors(str(tmp_path), files)


def test_an_interface_in_a_module(tmp_path):
    # an interface's functions name it in full (Shop.Pricing.Sized) - it crashed the C generator before
    module_text = ('interface Sized\n    int function size()\n\n'
                   'class Box implements Sized\n    int n = 3\n    int function size() : n\n\n'
                   'public static int function measure(Sized s) : s.size() * 2\n\n'
                   'public static int function make(int n) : measure(Box()) + n - 6 + n\n')
    files = {'Shop/Pricing/m.fusion': module_text, 'main.fusion': MAIN_PRICING}
    assert run_project(str(tmp_path), files) == ['10']


@pytest.mark.parametrize('source', [
    'static interface Sized\n    int function size()\n',
    'public static int function f() : 1\n',
    'internal static int function f() : 1\n',
    'private static int count = 0\n',
    'private class C\n    int x\n',
    'private enum E { A }\n',
    'private interface I\n    int function size()\n',
])
def test_static_and_private_at_the_top_parse(source):
    parse_file(source, 'main.fusion')


@pytest.mark.parametrize('source, message', [
    ('module SQL.Database\n', "A module's name is one word - the folders above it are its namespace"),
    ('import m\nmodule A\n', r"'module' comes right after the namespace line \(or first\) - before the imports"),
    ('module A\nnamespace B\n', "'namespace' must be the first line of the file"),
    ('module A B\n', "Expected the end of the line after the module's name"),
    ('int module = 1\n', "Expected"),
])
def test_module_line_syntax_errors(source, message):
    with pytest.raises(ParserError, match=message):
        parse_file(source, 'main.fusion')
