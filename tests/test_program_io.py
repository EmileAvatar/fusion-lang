"""Tests for Task 18.5.4 - the program's arguments, console input and exit.

main(string... args) gets the arguments without the program's name and --headless (on
Windows read as UTF-16, so accented arguments arrive intact); readLine() reads a line
without its ending, "" at the end of input; isEndOfInput(); exit(code). Programs run
under the leak check, with real arguments and piped input.
"""

import os
import subprocess
import tempfile

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator
from tests.test_structs import errors_of, main


def run(source: str, args=(), stdin: str = ''):
    """(exit code, stdout lines) of a program run with arguments and input."""
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(program), analyzer.get_errors()
    c_code = CCodeGenerator().generate(program)
    with tempfile.TemporaryDirectory() as tmp:
        c_file, exe = os.path.join(tmp, 'p.c'), os.path.join(tmp, 'p.exe')
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
        build = subprocess.run(['gcc', '-DFUSION_LEAK_CHECK', '-Wall', '-Wextra', c_file, '-o', exe],
                               capture_output=True, text=True)
        assert build.returncode == 0 and 'warning' not in build.stderr, build.stderr
        result = subprocess.run([exe, *args], input=stdin.encode('utf-8'), capture_output=True,
                                timeout=20)
        return result.returncode, result.stdout.decode('utf-8').splitlines()


ECHO_ARGS = ('void function main(string... args)\n'
             '    print("{@1}", len(args))\n'
             '    for a in args\n'
             '        print("[{a}] {@1}", len(a))\n')


def test_arguments():
    code, out = run(ECHO_ARGS, ['one', 'two words', '--headless', 'caf\u00e9', ''])
    assert code == 0
    assert out == ['4', '[one] 3', '[two words] 9', '[caf\u00e9] 4', '[] 0']


def test_no_arguments_and_main_without_parameters():
    assert run(ECHO_ARGS) == (0, ['0'])
    assert run(main('print("plain")'), ['ignored']) == (0, ['plain'])


def test_arguments_are_strings_like_any_other():
    source = ('int function total(string[] values)\n    int sum = 0\n    for v in values\n'
              '        sum = sum + toInt(v)\n    return sum\n\n'
              'void function main(string... args)\n'
              '    List<string> copy\n'
              '    for a in args\n'
              '        copy.add(a.toUpper())\n'
              '    print("{@1} {@2} {@3}", total(args), copy.join(","), args[0] == "1")\n')
    assert run(source, ['1', '2', '39']) == (0, ['42 1,2,39 true'])


def test_read_line_and_end_of_input():
    source = main('int count = 0\n'
                  'while not isEndOfInput()\n'
                  '    string line = readLine()\n'
                  '    count = count + 1\n'
                  '    print("{count}: [{line}] {@1}", len(line))\n'
                  'print("[{@1}]", readLine())')
    code, out = run(source, stdin='hello\r\n\ncaf\u00e9 au lait\nlast')
    assert code == 0
    assert out == ['1: [hello] 5', '2: [] 0', '3: [caf\u00e9 au lait] 12', '4: [last] 4', '[]']


def test_a_long_line():
    code, out = run(main('string s = readLine()\nprint("{@1} {@2}", len(s), s.right(3))'),
                    stdin='x' * 5000 + 'end\n')
    assert (code, out) == (0, ['5003 end'])


def test_exit_code():
    source = ('void function main(string... args)\n'
              '    string kept = "still alive".toUpper()\n'
              '    if len(args) > 0\n'
              '        exit(toInt(args[0]))\n'
              '    print(kept)\n')
    assert run(source, ['7']) == (7, [])
    assert run(source) == (0, ['STILL ALIVE'])


@pytest.mark.parametrize("source, message", [
    ('void function main(int argc)\n    print("x")\n', "main takes no parameters, or the program's arguments"),
    ('void function main(string args)\n    print("x")\n', "main takes no parameters, or the program's arguments"),
    ('int function f(int... xs) : 1\n\n' + main('int y = 1'), "'...' is only for main's arguments for now"),
])
def test_errors(source, message):
    assert message in errors_of(source)
