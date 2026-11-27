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
