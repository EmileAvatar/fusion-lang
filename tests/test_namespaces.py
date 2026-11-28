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


# 57.3 (D.206, D.213): an external library - listed in [libraries] (a namespace and its folder), or imported with
# its folder written: import "C:/vendor".SQL.Database

VENDOR = {'vendor/SQL/Database/d.fusion': 'public static string function name() : "vendor sql"\n'}


def build_and_run(root, files: dict, app: str = 'app'):
    """Compile app/main.fusion with main.py (its fusion.toml read) and run it: (stdout lines, compiler output)."""
    import os
    import subprocess
    import sys
    from tests.test_modules import write_project
    for name, text in files.items():
        write_project(root, {name: text})
    main_file = os.path.join(root, app, 'main.fusion')
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    built = subprocess.run([sys.executable, os.path.join(repo, 'main.py'), main_file, '--no-new-config'],
                           capture_output=True, text=True, encoding='utf-8')
    if built.returncode != 0:
        return None, built.stdout + built.stderr
    ran = subprocess.run([os.path.join(root, app, 'main.exe')], capture_output=True, text=True, encoding='utf-8')
    return ran.stdout.splitlines(), built.stderr


def test_a_library_listed_in_the_settings(tmp_path):
    files = dict(VENDOR)
    files['app/fusion.toml'] = '[libraries]\nSQL = "../vendor/SQL"\n'
    files['app/main.fusion'] = MAIN_SQL
    assert build_and_run(str(tmp_path), files)[0] == ['vendor sql']


def test_a_library_imported_with_its_folder(tmp_path):
    files = dict(VENDOR)
    files['app/main.fusion'] = ('import "../vendor".SQL.Database\n\n'
                                'void function main()\n'
                                '    print(Database.name())\n')
    assert build_and_run(str(tmp_path), files)[0] == ['vendor sql']


def test_a_reverse_domain_library(tmp_path):
    files = {'libs/com/example/SQL/Database/d.fusion': 'public static string function name() : "example sql"\n',
             'app/fusion.toml': '[libraries]\n"com.example.SQL" = "../libs/com/example/SQL"\n',
             'app/main.fusion': ('import com.example.SQL.Database\n\n'
                                 'void function main()\n'
                                 '    print(Database.name())\n')}
    assert build_and_run(str(tmp_path), files)[0] == ['example sql']


def test_a_library_not_found(tmp_path):
    files = {'app/main.fusion': MAIN_SQL}
    output = build_and_run(str(tmp_path), files)[1]
    assert "No module 'SQL.Database' - expected a folder SQL/Database/ with .fusion files next to the main " \
           "file, or in a library listed in [libraries]" in output


def test_a_module_in_two_places_is_an_error(tmp_path):
    files = dict(VENDOR)
    files['app/SQL/Database/d.fusion'] = 'public static string function name() : "own sql"\n'
    files['app/fusion.toml'] = '[libraries]\nSQL = "../vendor/SQL"\n'
    files['app/main.fusion'] = MAIN_SQL
    output = build_and_run(str(tmp_path), files)[1]
    assert "Module 'SQL.Database' is in two places" in output and "keep one" in output


@pytest.mark.parametrize('toml, message', [
    ('[libraries]\n"9SQL" = "x"\n', "a library is named by its namespace, as SQL or com.example.SQL"),
    ('[libraries]\nSQL = 5\n', "libraries.SQL must be the library's folder"),
    ('[libraries]\nSQL = ""\n', "libraries.SQL must be the library's folder"),
])
def test_bad_library_settings(tmp_path, toml, message):
    from src.config import ProjectConfigError, load_project_config
    (tmp_path / 'fusion.toml').write_text(toml, encoding='utf-8')
    (tmp_path / 'main.fusion').write_text('void function main()\n    print("x")\n', encoding='utf-8')
    with pytest.raises(ProjectConfigError, match=message):
        load_project_config(str(tmp_path / 'main.fusion'))


@pytest.mark.parametrize('source, message', [
    ('import "C:/vendor"\n', "Expected '.' and the module's name after the folder"),
    ('import "{x}".SQL\n', r"An import's folder is plain text - no \{...\} in it"),
])
def test_import_path_syntax_errors(source, message):
    with pytest.raises(ParserError, match=message):
        parse_file(source, 'main.fusion')


# 57.4 (D.208, D.209): a namespace imported (with an alias or not), full names once imported, two modules with the
# same name an error until one is aliased

SQL_DB = {'SQL/Database/d.fusion': ('public class Conn\n    public string url = "db://x"\n'
                                    '    public static Conn function make() : Conn()\n\n'
                                    'public static string function name() : "sql"\n'),
          'SQL/Pool/p.fusion': 'public static int function size() : 4\n'}


def run_main(tmp_path, main_body: str, imports: str, extra: dict = None) -> list:
    files = dict(SQL_DB)
    files.update(extra or {})
    files['main.fusion'] = imports + '\n\nvoid function main()\n' + \
        ''.join(f'    {line}\n' for line in main_body.split('\n'))
    return run_project(str(tmp_path), files)


@pytest.mark.parametrize('imports, body', [
    ('import SQL as Q', 'print(Q.Database.name())\nprint(format("{@1}", Q.Pool.size()))'),
    ('import SQL', 'print(SQL.Database.name())\nprint(format("{@1}", SQL.Pool.size()))'),
    ('import SQL.Database\nimport SQL.Pool', 'print(Database.name())\nprint(format("{@1}", SQL.Pool.size()))'),
    ('import SQL.Database as D\nimport SQL.Pool', 'print(D.name())\nprint(format("{@1}", SQL.Pool.size()))'),
    ('import SQL.Database\nimport SQL.Pool', 'print(SQL.Database.name())\nprint(format("{@1}", Pool.size()))'),
])
def test_a_namespace_and_full_names(tmp_path, imports, body):
    assert run_main(tmp_path, body, imports) == ['sql', '4']


@pytest.mark.parametrize('imports, body', [
    ('import SQL as Q', 'Q.Database.Conn c = Q.Database.Conn.make()\nprint(c.url)'),
    ('import SQL.Database', 'SQL.Database.Conn c = Database.Conn.make()\nprint(c.url)'),
    ('import SQL.Database', 'Database.Conn c = SQL.Database.Conn()\nprint(c.url)'),
])
def test_types_by_a_namespace_or_full_name(tmp_path, imports, body):
    assert run_main(tmp_path, body, imports) == ['db://x']


def test_a_namespace_import_loads_only_what_is_used(tmp_path):
    # Pool has an error in it - never loaded, as nothing uses Q.Pool
    extra = {'SQL/Pool/p.fusion': 'public static int function size() : "four"\n'}
    assert run_main(tmp_path, 'print(Q.Database.name())', 'import SQL as Q', extra) == ['sql']


TWO = {'A/Database/a.fusion': 'public static string function name() : "a"\n',
       'B/Database/b.fusion': 'public static string function name() : "b"\n'}


def test_two_modules_with_one_name_need_an_alias(tmp_path):
    files = dict(TWO)
    files['main.fusion'] = 'import A.Database\nimport B.Database\n\nvoid function main()\n    print("x")\n'
    assert "Two modules are both named 'Database' here: A.Database and B.Database - give one another name " \
           "with 'as'" in errors(str(tmp_path), files)
    files['main.fusion'] = ('import A.Database\nimport B.Database as BD\n\n'
                            'void function main()\n'
                            '    print(Database.name())\n    print(BD.name())\n'
                            '    print(A.Database.name())\n    print(B.Database.name())\n')
    assert run_project(str(tmp_path), files) == ['a', 'b', 'a', 'b']


@pytest.mark.parametrize('main_text, message', [
    ('import SQL as Q\n\nvoid function main()\n    print(Q.Nope.name())\n',
     "Namespace SQL has no module 'Nope' (in 'Q.Nope.name')"),
    ('import SQL.Database\n\nvoid function main()\n    print(SQL.Pool.size())\n', "Undefined"),
    ('import SQL as Q\n\nint Q = 1\n\nvoid function main()\n    print("x")\n',
     "'Q' is both a namespace and a name declared here"),
    ('import SQL.Database\n\nvoid function main()\n    SQL.Nope.Conn c = Database.Conn()\n',
     "No module 'SQL.Nope' is imported here (for the type 'SQL.Nope.Conn')"),
])
def test_namespace_import_errors(tmp_path, main_text, message):
    files = dict(SQL_DB)
    files['main.fusion'] = main_text
    assert message in errors(str(tmp_path), files)


# 57.5 (D.208, D.210): Fusion's own modules - Fusion.Core always there, Fusion.Currency added with money; the
# namespace Fusion reserved

@pytest.mark.parametrize('main_text, output', [
    ('void function main()\n    Fusion.Core.print("core")\n', ['core']),
    ('import Fusion.Core\n\nvoid function main()\n    print("core")\n', ['core']),
    ('import Fusion.Currency\n\nvoid function main()\n'
     '    print(format("{@1}", Fusion.Currency.Currency.places("JPY")))\n', ['0']),
    ('void function main()\n    print(format("{@1}", Currency.places("ZAR")))\n', ['2']),
])
def test_fusions_own_modules(tmp_path, main_text, output):
    files = {'app/main.fusion': main_text}
    assert build_and_run(str(tmp_path), files)[0] == output


@pytest.mark.parametrize('files, message', [
    ({'app/main.fusion': 'import Fusion.IO\n\nvoid function main()\n    print("x")\n'},
     "Fusion has no module 'IO' - its own modules so far: Fusion.Core, Fusion.Currency"),
    ({'app/main.fusion': 'void function main()\n    Fusion.IO.print("x")\n'}, "Fusion has no module 'IO'"),
    ({'app/main.fusion': 'import Fusion.Core as C\n\nvoid function main()\n    print("x")\n'},
     "Fusion.Core is imported without 'as'"),
    ({'app/fusion.toml': '[libraries]\nFusion = "../mine"\n', 'app/main.fusion': MAIN_SQL},
     "the namespace Fusion is reserved for Fusion's own modules"),
])
def test_the_fusion_namespace_is_reserved(tmp_path, files, message):
    assert message in build_and_run(str(tmp_path), files)[1]


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
