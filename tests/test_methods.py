"""Tests for Task 18.3.7 - built-in type classes and method syntax.

`name.toUpper()`, `"Claude".toUpper()` and `String.toUpper(name)` all mean the built-in
toUpper(name); the plain form keeps working (user decisions 2026-10-10: keep every form;
classes for every built-in type; methods on number literals; methods keep the function
names). Every program runs under the leak check.
"""

import os
import subprocess
import tempfile

import pytest

from src.lexer import Lexer
from src.lexer.token import TokenType
from tests.test_structs import errors_of, generate_c, main
from tests.test_strings import run_ok


def test_three_forms_mean_the_same_call():
    source = main('string name = "ada"\nstring a = toUpper(name)\nstring b = name.toUpper()\n'
                  'string c = String.toUpper(name)')
    c_code = generate_c(source)
    assert c_code.count('fusion_str_toUpper(name)') == 3
    assert run_ok(main('string name = "ada"\nprint("{@1} {@2} {@3} {@4}", toUpper(name), '
                       'name.toUpper(), String.toUpper(name), "ada".toUpper())')) == ['ADA ADA ADA ADA']


def test_chaining_and_fields():
    assert run_ok('struct Person\n    string name\n    int age\n\n' + main(
        'Person p = Person("  grace hopper ", 85)\n'
        'print("[{@1}] [{@2}]", p.name.trim().toTitle().padRight(14, \'.\'), p.age.toString().padLeft(5, \'0\'))\n'
        'print("{@1}", "a-b-c".replace("-", "").toUpper().reverse().len())'
    )) == ['[Grace Hopper..] [00085]', '3']


def test_every_type_class():
    assert run_ok(main(
        'print("{@1} {@2} {@3} {@4}", 255.toHex(), 255.toHex(4), (5).toBinary(8), Int.parseInt("ff", 16))\n'
        'print("{@1} {@2} {@3}", Int.fromHex("1F"), Int.toHex(16), 1234.5.formatNumber("#,##0.00"))\n'
        'print("{@1} {@2} {@3}", \'A\'.charCode(), Char.fromCharCode(66), \'z\'.toString())\n'
        'bytes data = "kkkkk".toBytes()\n'
        'data.setInt16(0, 0x6969)\n'
        'print("{@1} {@2} {@3}", data.rawToHex(), data.toString(), data.len())\n'
        'print("{@1} {@2} {@3}", data.indexOf("kk".toBytes()), Bytes.hexToRaw("6869").toString(), Bytes.newBytes(2).rawToHex())\n'
        'byte b = data[0]\n'
        'print("{@1} {@2} {@3} {@4}", b.toHex(), b.toString(), true.toString(), 2.5.toString())\n'
        'print("{@1} {@2}", "file2".compareNatural("file10"), String.isEmpty(""))'
    )) == ['ff 00ff 00000101 255', '31 10 1,234.50', '65 B z', '69696b6b6b iikkk 5',
           '2 hi 0000', '69 105 true 2.5', '-1 true']


def test_method_always_means_the_built_in():
    """A program's own `left` replaces the plain built-in, but `s.left(3)` is still the
    string method - and a local variable can't hide a method either."""
    assert run_ok('int function left(int a)\n    return a - 1\n\n' + main(
        'string s = "Lovelace"\n'
        'int right = 2\n'
        'print("{@1} {@2} {@3}", s.left(3), left(10), s.right(right))'
    )) == ['Lov 9 ce']


def test_a_struct_field_is_not_a_method():
    assert "Struct 'Point' has no field 'move'" in errors_of(
        'struct Point\n    int x\n\n' + main('Point p = Point(1)\np.move(2)'))


def test_number_literal_before_a_method():
    def kinds(text):
        return [(t.type, t.value) for t in Lexer(text, 'test.fusion').tokenize()][:4]
    assert kinds('255.toHex()')[:3] == [(TokenType.INTEGER, '255'), (TokenType.DOT, '.'),
                                       (TokenType.IDENTIFIER, 'toHex')]
    assert kinds('2.5.toString()')[0] == (TokenType.FLOAT_LIT, '2.5')
    assert kinds('255.0')[0] == (TokenType.FLOAT_LIT, '255.0')


@pytest.mark.parametrize("body, message", [
    ('int n = 5\nstring s = n.toUpper()', "Int has no method 'toUpper'"),
    ('string s = "x"\nstring t = s.toHexx()', "String has no method 'toHexx'"),
    ('string s = "x"\ns.print()', "String has no method 'print'"),
    ('int n = String.charCode(\'a\')', "String has no method 'charCode'"),
    ('char c = 65.fromCharCode()', "Int has no method 'fromCharCode'"),
    ('int n = Int.fromCharCode(65)', "Int has no method 'fromCharCode'"),
    ('string s = "abc"\nint n = s.indexOf(5)', "Argument 2 to 'indexOf': expected string, got int"),
    ('"abcd".toBytes().setInt(0, 1)', "'setInt' changes its first argument, so it must be a variable"),
])
def test_method_errors(body, message):
    assert message in errors_of(main(body))


def test_class_names_are_reserved_for_structs():
    assert "'String' is a built-in type" in errors_of('struct String\n    int x\n\n' + main('int y = 1'))


def test_a_variable_named_like_a_class_still_works():
    assert run_ok(main('int Int = 3\nprint("{@1}", Int + 1)')) == ['4']


def test_library_programs_compile_without_warnings():
    """Programs that really call the string library, bytes and formatNumber compile with no
    gcc warnings at -O2 under -Wall -Wextra (unused functions alone don't show them all)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ('syntax_string_library', 'syntax_bytes', 'syntax_methods'):
        path = os.path.join(root, 'examples', f'{name}.fusion')
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            c_code = generate_c(f.read())
        with tempfile.TemporaryDirectory() as tmp:
            c_file = os.path.join(tmp, f'{name}.c')
            with open(c_file, 'w', encoding='utf-8') as f:
                f.write(c_code)
            build = subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-c', c_file, '-o',
                                    os.path.join(tmp, 'x.o')], capture_output=True, text=True)
            assert build.returncode == 0 and 'warning' not in build.stderr, f'{name}: {build.stderr}'
