"""Tests for Task 58 - script mode (D.221-D.229, files/spec/170-Build.md - the truth table there).

58.1 (D.222, D.225): a file without `main` holds statements at the top - run in order, as its main; its variables are
the script's (every function sees them); functions, types and imports as in any file; `args` - its arguments; a `#!`
first line skipped; a file with both `main` and statements at the top an error.
"""

import os
import subprocess
import sys

import pytest

from src.parser.parser import ParserError
from tests.test_modules import errors, parse_file, write_project

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_and_run(tmp_path, files: dict, args=()) -> tuple:
    """main.py on main.fusion, then the program with args: (exit code, its output)."""
    for name, text in files.items():
        write_project(str(tmp_path), {name: text})
    built = subprocess.run([sys.executable, os.path.join(REPO, 'main.py'), str(tmp_path / 'main.fusion'),
                            '--no-new-config'], capture_output=True, text=True, encoding='utf-8')
    assert built.returncode == 0, built.stdout + built.stderr
    ran = subprocess.run([str(tmp_path / 'main.exe'), *args], capture_output=True, text=True, encoding='utf-8')
    return ran.returncode, ran.stdout


TIDY = ('int removed = 0\n'
        '\n'
        'void function remove(string name)\n'
        '    removed = removed + 1              // a function sees the script\'s variable\n'
        '\n'
        'struct Item\n'
        '    string name\n'
        '\n'
        'print("start")\n'
        'for name in args\n'
        '    remove(name)\n'
        'int later = removed * 10               // declared after a statement: set here, in order\n'
        'Item it = Item("box")\n'
        'print("{removed} removed, later {later}, {it.name}")\n')


@pytest.mark.parametrize('args, expected', [
    (['a', 'b', 'c'], 'start\n3 removed, later 30, box\n'),
    ([], 'start\n0 removed, later 0, box\n'),                 # none passed - args empty (D.225)
])
def test_a_script(tmp_path, args, expected):
    assert build_and_run(tmp_path, {'main.fusion': TIDY}, args) == (0, expected)


def test_the_hash_bang_line_is_skipped(tmp_path):
    source = '#!/usr/bin/env fusion run\nprint("hi")\nint x = 1 + undefinedName\n'
    found = errors(str(tmp_path), {'main.fusion': source})
    assert "main.fusion:3:" in found                           # the lines keep their numbers


def test_the_exit_code(tmp_path):
    source = 'if args.length == 0\n    print("give a name")\n    exit(2)\nprint("ok")\n'
    assert build_and_run(tmp_path, {'main.fusion': source}) == (2, 'give a name\n')
    assert build_and_run(tmp_path, {'main.fusion': source}, ['x']) == (0, 'ok\n')


def test_types_functions_and_imports_in_a_script(tmp_path):
    files = {'shapes/s.fusion': 'public int function square(int n) : n * n\n',
             'main.fusion': ('import shapes\n\n'
                             'enum Size { SMALL, BIG }\n\n'
                             'interface Named\n    string function name()\n\n'
                             'class Box implements Named\n    public string function name() : "box"\n\n'
                             'Box b = Box()\n'
                             'Size s = Size.BIG\n'
                             'print(format("{@1} {@2} {@3}", b.name(), s, shapes.square(4)))\n'
                             'if s == Size.BIG\n'
                             '    print("big")\n')}
    assert build_and_run(tmp_path, files) == (0, 'box BIG 16\nbig\n')


@pytest.mark.parametrize('source', [
    'x = 1\n',                         # an assignment
    'xs[0] = 1\n',
    'print("x")\n',                    # a call
    'money.show(5)\n',
    'outer: for x in 0...1\n    break outer\n',
    'while false\n    print("x")\n',
    'match 1\n    case 1: print("x")\n    else: print("y")\n',
])
def test_these_are_statements_at_the_top(source):
    assert parse_file('int x = 0\nint[3] xs\n' + source, 'main.fusion').script


@pytest.mark.parametrize('source', [
    'int x = 5\n', 'Box b\n', 'money.Price p\n', 'List<int> xs = [1]\n', 'Point[3] pts\n',
    'Point[2] function corners() : [Point(0, 0), Point(5, 5)]\n', 'Point function origin() : Point(0, 0)\n',
    'Ship, Error function load() : Ship()\n', 'void function main()\n    print("x")\n',
])
def test_these_are_declarations(source):
    assert not parse_file(source, 'main.fusion').script


def test_main_and_statements_at_the_top_is_an_error():
    with pytest.raises(ParserError, match="A file with a main function can't have statements at the top too"):
        parse_file('print("a")\n\nvoid function main()\n    print("b")\n', 'main.fusion')


def test_return_at_the_top_is_still_an_error():
    with pytest.raises(ParserError, match="Unexpected token 'return' at top level"):
        parse_file('return 42\n', 'main.fusion')


def test_statements_at_the_top_of_a_module_are_an_error(tmp_path):
    files = {'tools/t.fusion': 'print("loaded")\n', 'main.fusion': 'import tools\n\nprint("x")\n'}
    assert "tools/t.fusion has statements at the top - only the file that starts the program (a script) runs " \
           "them" in errors(str(tmp_path), files)
