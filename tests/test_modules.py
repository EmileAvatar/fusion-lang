"""Tests for Task 18.4.2 - `import` and module folders (src/modules/loader.py).

A module is a folder next to the main file; `import money` (prefix), `import money.Price`
(one name), `import money.*` (every name), `import lib.utils as u` (alias); a module is used
by the last part of its path; each module is loaded once, so imports may criss-cross; two
different modules with the same name in one file are an error. Imports are per file.
Every program runs under the leak check.
"""

import os
import subprocess

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator
from src.modules import load_program


def parse_file(source: str, path: str):
    return Parser(Lexer(source, path).tokenize()).parse_program()


def write_project(root, files: dict) -> str:
    for name, text in files.items():
        path = os.path.join(root, *name.split('/'))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    return os.path.join(root, 'main.fusion')


def load(root, files: dict):
    """(program, import errors, semantic errors) for a project."""
    main_file = write_project(root, files)
    with open(main_file, encoding='utf-8') as f:
        program = parse_file(f.read(), main_file)
    program, import_errors = load_program(main_file, program, parse_file)
    if import_errors:
        return program, [str(e) for e in import_errors], []
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    return program, [], [str(e) for e in analyzer.get_errors()]


def errors(root, files: dict) -> str:
    _, import_errors, semantic_errors = load(root, files)
    return '\n'.join(import_errors + semantic_errors)


def run_project(root, files: dict) -> list:
    program, import_errors, semantic_errors = load(root, files)
    assert not import_errors and not semantic_errors, import_errors + semantic_errors
    c_file = os.path.join(root, 'out.c')
    exe = os.path.join(root, 'out.exe')
    with open(c_file, 'w', encoding='utf-8') as f:
        f.write(CCodeGenerator().generate(program))
    build = subprocess.run(['gcc', '-DFUSION_LEAK_CHECK', '-Wall', '-Wextra', c_file, '-o', exe],
                           capture_output=True, text=True)
    assert build.returncode == 0 and 'warning' not in build.stderr, build.stderr
    result = subprocess.run([exe], capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    return result.stdout.splitlines()


SHOP = {
    'money/price.fusion': ('import tax\n\n'
                           'struct Price\n    int cents\n    string currency\n\n'
                           'Price function make(int cents) : Price(cents, "EUR")\n\n'
                           'int function round(int cents)\n    return (cents + 50) / 100 * 100\n'),
    'money/format.fusion': ('import tax\n\n'
                            'string function show(Price p)\n'
                            '    int total = tax.withVat(p.cents)\n'
                            '    return format("{@1} {@2}", formatNumber(total / 100.0, "0.00"), p.currency)\n'),
    'tax/vat.fusion': ('import money\n\n'
                       'int function withVat(int cents) : cents + cents / 5\n\n'
                       'money.Price function free() : money.make(0)\n'),
    'geometry/shapes/area.fusion': 'int function square(int side) : side * side\n',
}


def test_a_multi_module_program(tmp_path):
    files = dict(SHOP)
    files['main.fusion'] = (
        'import money\nimport money.Price\nimport tax.*\nimport geometry.shapes\n\n'
        'int function round(int x) : x + 1\n\n'
        'void function main()\n'
        '    Price p = money.make(1999)\n'
        '    money.Price q = Price(500, "USD")\n'
        '    print(money.show(p))\n'
        '    print(money.show(q))\n'
        '    print("{@1} {@2} {@3}", money.round(1249), round(1249), withVat(100))\n'
        '    int square = 3\n'
        '    print("{@1} {@2}", shapes.square(4), square)\n'
        '    print("{@1}", free().cents)\n')
    assert run_project(str(tmp_path), files) == [
        '23.98 EUR', '6.00 USD', '1200 1250 120', '16 3', '0']


def test_alias_and_module_names_in_c(tmp_path):
    files = {
        'shop/utils/a.fusion': 'string function tag() : "shop"\n',
        'lib/utils/b.fusion': 'string function tag() : "lib"\n',
        'main.fusion': ('import shop.utils\nimport lib.utils as libutils\n\n'
                        'void function main()\n    print(utils.tag() + " " + libutils.tag())\n'),
    }
    assert run_project(str(tmp_path), files) == ['shop lib']
    program, _, _ = load(str(tmp_path), files)
    c_code = CCodeGenerator().generate(program)
    assert 'fusion_string fu_shop__utils__tag(void)' in c_code
    assert 'fusion_string fu_lib__utils__tag(void)' in c_code


def test_each_module_is_loaded_once(tmp_path):
    files = {
        'base/b.fusion': 'int function one() : 1\n',
        'left/l.fusion': 'import base\nint function two() : base.one() + 1\n',
        'right/r.fusion': 'import base\nimport left\nint function three() : left.two() + base.one()\n',
        'main.fusion': ('import base\nimport left\nimport right\n\n'
                        'void function main()\n    print("{@1} {@2} {@3}", base.one(), left.two(), right.three())\n'),
    }
    assert run_project(str(tmp_path), files) == ['1 2 3']


def test_program_without_imports_is_unchanged(tmp_path):
    main_file = write_project(str(tmp_path), {'main.fusion': 'void function main()\n    print("x")\n'})
    with open(main_file, encoding='utf-8') as f:
        program = parse_file(f.read(), main_file)
    assert load_program(main_file, program, parse_file) == (program, [])


@pytest.mark.parametrize("files, message", [
    ({'main.fusion': 'import nowhere\nvoid function main()\n    print("x")\n'},
     "No module 'nowhere' - expected a folder nowhere/"),
    ({'m/a.fusion': 'int function f() : 1\n',
      'main.fusion': 'import m.g\nvoid function main()\n    print("x")\n'},
     "Module 'm' has no 'g'"),
    ({'m/a.fusion': 'int function f() : 1\n',
      'main.fusion': 'import m\nvoid function main()\n    int x = m.g()\n'},
     "Module 'm' has no 'g'"),
    ({'shop/utils/a.fusion': 'int function f() : 1\n', 'lib/utils/b.fusion': 'int function f() : 2\n',
      'main.fusion': 'import shop.utils\nimport lib.utils\nvoid function main()\n    print("x")\n'},
     "Two modules are both named 'utils' here: shop.utils and lib.utils - give one another name with 'as'"),
    ({'a/a.fusion': 'int function f() : 1\n', 'b/b.fusion': 'int function f() : 2\n',
      'main.fusion': 'import a.*\nimport b.*\nvoid function main()\n    int x = f()\n'},
     "'f' is ambiguous: a.f or b.f - use the module prefix"),
    ({'m/a.fusion': 'void function main()\n    print("x")\n',
      'main.fusion': 'import m\nvoid function main()\n    print("x")\n'},
     "Module 'm' can't have a main function"),
    ({'m/a.fusion': 'int function f() : 1\n',
      'main.fusion': 'import m.f\nint function f() : 2\nvoid function main()\n    print("x")\n'},
     "'f' is imported from m and also declared here"),
    ({'m/a.fusion': 'struct P\n    int x\n',
      'main.fusion': 'import m\nvoid function main()\n    q.P p\n'},
     "No module 'q' is imported here (for the type 'q.P')"),
    ({'String/a.fusion': 'int function f() : 1\n',
      'main.fusion': 'import String\nvoid function main()\n    print("x")\n'},
     "'String' can't be a module name"),
])
def test_import_errors(tmp_path, files, message):
    assert message in errors(str(tmp_path), files)


def test_a_module_needs_its_own_imports(tmp_path):
    """Imports are per file: a file uses only what it imports itself."""
    files = {
        'a/one.fusion': 'import b\nint function f() : b.g()\n',
        'a/two.fusion': 'int function h() : b.g()\n',
        'b/b.fusion': 'int function g() : 1\n',
        'main.fusion': 'import a\nvoid function main()\n    print("x")\n',
    }
    assert "Undefined variable: 'b'" in errors(str(tmp_path), files)


def test_imports_must_come_first(tmp_path):
    from src.parser.parser import ParserError
    with pytest.raises(ParserError, match="'import' lines must come before everything else"):
        parse_file('void function main()\n    print("x")\nimport m\n', 'main.fusion')


def test_two_fusion_names_never_share_a_c_name(tmp_path):
    files = {
        'a/a.fusion': 'int function b__c() : 1\n',
        'a/b/b.fusion': 'int function c() : 2\n',
        'main.fusion': 'import a\nimport a.b\nvoid function main()\n    print("{@1} {@2}", a.b__c(), b.c())\n',
    }
    program, import_errors, semantic_errors = load(str(tmp_path), files)
    assert not import_errors and not semantic_errors
    with pytest.raises(NotImplementedError, match="would both be 'fu_a__b__c' in C"):
        CCodeGenerator().generate(program)
