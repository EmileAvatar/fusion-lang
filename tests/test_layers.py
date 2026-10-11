"""Tests for Task 18.5.6 - standard-library layers: [stdlib] layer = core | alloc | std.

core: no heap - numbers, chars, bools, arrays, range, toByte, charCode / fromCharCode.
alloc: adds text, bytes, List, Map and their functions. std (default): adds the operating
system - print, console input, files, exit, main's arguments. Using something above the
project's layer is a compile error (the D lesson: layer the stdlib from day one).
"""

import os
import subprocess
import sys

import pytest

from src.config import StdlibConfig, load_project_config, ProjectConfigError
from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from tests.test_structs import main


def errors_with(layer: str, source: str) -> list:
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer(stdlib_config=StdlibConfig(layer=layer))
    analyzer.analyze(program)
    return [str(e) for e in analyzer.get_errors()]


CORE_PROGRAM = ('int function square(int x) : x * x\n\n'
                + main('int[3] xs = [1, 2, 3]\n'
                       'int total = 0\n'
                       'for i in range(0, 3)\n'
                       '    total = total + square(xs[i])\n'
                       'byte b = toByte(total)\n'
                       'char c = fromCharCode(65)\n'
                       'int code = charCode(c)\n'
                       'bool ok = total == 14 and len(xs) == 3'))


def test_core_programs_compile_at_every_layer():
    for layer in ('core', 'alloc', 'std'):
        assert errors_with(layer, CORE_PROGRAM) == []


@pytest.mark.parametrize("body, message", [
    ('string s = "hi"', "text needs the alloc layer, but this project uses core"),
    ('string s', "text needs the alloc layer"),
    ('List<int> xs = [1]', "a List needs the alloc layer"),
    ('Map<string, int> m', "a Map needs the alloc layer"),
    ('bytes b = toBytes(5)', "'toBytes' needs the alloc layer"),
    ('int n = len("abc")', "text needs the alloc layer"),
])
def test_core_refuses_the_heap(body, message):
    assert any(message in e for e in errors_with('core', main(body)))


def test_core_refuses_heap_types_in_declarations():
    errors = errors_with('core', 'struct P\n    string name\n\n'
                                 'string function f(List<int> xs) : "x"\n\n' + main('int y = 1'))
    assert sum("needs the alloc layer" in e for e in errors) >= 3


ALLOC_PROGRAM = main('List<string> ws = "a b".words()\n'
                     'Map<string, int> counts\n'
                     'for w in ws\n'
                     '    counts[w] = counts.get(w, 0) + 1\n'
                     'string s = formatNumber(3.5, "0.00").toUpper()\n'
                     'bytes b = toBytes(s)')


def test_alloc_allows_text_lists_and_maps():
    assert errors_with('alloc', ALLOC_PROGRAM) == []
    assert errors_with('std', ALLOC_PROGRAM) == []


@pytest.mark.parametrize("body, message", [
    ('print("hi")', "'print' needs the std layer, but this project uses alloc"),
    ('string t = readText("a.txt")', "'readText' needs the std layer"),
    ('exit(1)', "'exit' needs the std layer"),
    ('string line = readLine()', "'readLine' needs the std layer"),
])
def test_alloc_refuses_the_operating_system(body, message):
    assert any(message in e for e in errors_with('alloc', main(body)))


def test_main_arguments_need_std():
    source = 'void function main(string... args)\n    int n = len(args)\n'
    assert any("main's arguments (string... args) needs the std layer" in e
               for e in errors_with('alloc', source))
    assert errors_with('std', source) == []


def test_each_place_is_reported_once():
    errors = errors_with('alloc', main('print("a")\nprint("b")'))
    assert len([e for e in errors if "'print' needs the std layer" in e]) == 2


def test_config(tmp_path):
    (tmp_path / 'p.fusion').write_text('void function main()\n    print("x")\n')
    assert load_project_config(str(tmp_path / 'p.fusion')).stdlib.layer == 'std'
    (tmp_path / 'fusion.toml').write_text('[stdlib]\nlayer = "alloc"\n')
    assert load_project_config(str(tmp_path / 'p.fusion')).stdlib.layer == 'alloc'
    for text, message in [('[stdlib]\nlayer = "kernel"\n', "stdlib.layer must be one of"),
                          ('[stdlib]\nlevel = "core"\n', "unknown setting stdlib.level")]:
        (tmp_path / 'fusion.toml').write_text(text)
        with pytest.raises(ProjectConfigError, match=message):
            load_project_config(str(tmp_path / 'p.fusion'))


def test_the_compiler_reads_the_layer(tmp_path):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    (tmp_path / 'fusion.toml').write_text('[stdlib]\nlayer = "alloc"\n')
    (tmp_path / 'p.fusion').write_text('void function main()\n    print("x")\n')
    result = subprocess.run([sys.executable, os.path.join(root, 'main.py'), str(tmp_path / 'p.fusion')],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "'print' needs the std layer, but this project uses alloc" in result.stderr
