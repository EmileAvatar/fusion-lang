"""Tests for Task 32.1 - methods on structs.

A function written inside a struct, allowed by `[structs] functions = true` (default false -
user decision 2026-10-24). It gets the struct as `this`, by reference, so `p.move(1, 2)`
changes p. Inside, a field's bare name means `this.field` and another method's bare name
`this.method(...)`; a parameter or local can't take a field's name. On a const struct, a
method that changes `this` is an error. The struct's own method comes before a free
function of the same name (Task 44.2).
"""

import os
import subprocess

import pytest

from src.codegen import CCodeGenerator
from src.config import StructsConfig
from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from src.semantic import SemanticAnalyzer
from tests.test_structs import main

ON = StructsConfig(functions=True)

POINT = ('struct Point\n'
         '    int x\n'
         '    int y\n'
         '    string label\n\n'
         '    void function move(int dx, int dy)\n'
         '        x = x + dx\n'
         '        this.y = this.y + dy\n'
         '        rename(label + "!")\n\n'
         '    void function rename(string text)\n'
         '        label = text\n\n'
         '    int function sum() : x + y\n\n'
         '    string function describe() : format("{@1} ({@2}, {@3})", label, x, y)\n\n'
         'Point function make() : Point(10, 20, "made")\n\n')


def analyze(source: str, config=ON):
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer(structs_config=config)
    analyzer.analyze(program)
    return analyzer, program


def errors(source: str, config=ON) -> list:
    return [str(e) for e in analyze(source, config)[0].get_errors()]


def run(source: str, tmp_path) -> list:
    analyzer, program = analyze(source)
    assert not analyzer.get_errors(), analyzer.get_errors()
    c_file, exe = os.path.join(tmp_path, 'out.c'), os.path.join(tmp_path, 'out.exe')
    with open(c_file, 'w', encoding='utf-8') as f:
        f.write(CCodeGenerator().generate(program))
    build = subprocess.run(['gcc', '-Wall', '-DFUSION_LEAK_CHECK', c_file, '-o', exe],
                           capture_output=True, text=True)
    assert build.returncode == 0 and 'warning' not in build.stderr, build.stderr
    result = subprocess.run([exe], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr        # the leak check too
    return result.stdout.strip().splitlines()


def test_a_method_changes_the_callers_struct(tmp_path):
    lines = run(POINT + main('Point p = Point(1, 2, "p")\n'
                             'p.move(3, 4)\n'
                             'print(p.describe())\n'
                             'print("{@1}", p.sum())'), tmp_path)
    assert lines == ['p! (4, 6)', '10']


def test_on_a_list_element_a_field_and_a_temporary(tmp_path):
    lines = run(POINT + 'struct Shape\n    Point corner\n\n'
                + main('List<Point> ps = [Point(0, 0, "a")]\n'
                       'ps[0].move(1, 1)\n'
                       'Shape s = Shape(Point(5, 5, "c"))\n'
                       's.corner.move(1, 0)\n'
                       'print(ps[0].describe())\n'
                       'print(s.corner.describe())\n'
                       'print("{@1}", make().sum())'), tmp_path)
    assert lines == ['a! (1, 1)', 'c! (6, 5)', '30']


def test_a_method_comes_before_a_free_function(tmp_path):
    lines = run(POINT + 'int function sum(Point p) : 999\n\n'
                + main('Point p = Point(1, 2, "p")\nprint("{@1}", p.sum())'), tmp_path)
    assert lines == ['3']


def test_off_by_default():
    found = errors(POINT + main('Point p = Point(1, 2, "p")'), StructsConfig())
    assert any("functions on structs are off; [structs] functions = true allows them" in e
               for e in found)


def test_a_const_struct_can_only_call_methods_that_dont_change_it():
    found = errors(POINT + main('const Point c = Point(1, 2, "c")\n'
                                'int s = c.sum()\n'
                                'c.move(1, 1)'))
    assert found == [f for f in found if "Method 'move' changes the Point - 'c' is a constant" in f]
    assert len(found) == 1


@pytest.mark.parametrize('body, message', [
    ('    void function f(int x)\n        print("x")\n', "has the name of a field"),
    ('    void function f()\n        int x = 1\n', "can't have the name of field 'x'"),
    ('    int function x() : 1\n', "'x' is both a field and a method"),
    ('    constructor(int x)\n        print("x")\n', "can't have a constructor"),
])
def test_method_errors(body, message):
    with pytest.raises(ParserError, match=message):
        Parser(Lexer('struct P\n    int x\n' + body, 't').tokenize()).parse_program()
