"""Tests for Task 56 - loop safety (D.214-D.220, files/spec/070-ControlFlow.md - the truth table there).

56.3 (D.219): loop labels - `outer:` before `for` / `while`; `break outer` / `continue outer` in the body. A jump
frees every string the scopes inside that loop own (the leak check runs on every program) and runs their finally.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_functions import errors_of
from tests.test_structs import main


def run(body: str, top: str = '') -> list:
    code, out, err = compile_and_run(top + main(body))
    assert code == 0, out + err
    return out.split('\n')[:-1] if out.endswith('\n') else out.split('\n')


GRID = 'int[] row = [1, 2, 3]\n'


@pytest.mark.parametrize('body, expected', [
    # break outer - leaves both loops
    ('outer: for x in 0...2\n'
     '    for y in 0...2\n'
     '        if x * y == 2\n'
     '            break outer\n'
     '        print("{x}{y}")\n'
     'print("done")',
     ['00', '01', '02', '10', '11', 'done']),
    # continue outer - the next pass of the outer loop
    ('outer: for x in 0...2\n'
     '    for y in 0...2\n'
     '        if y == 1\n'
     '            continue outer\n'
     '        print("{x}{y}")\n'
     'print("done")',
     ['00', '10', '20', 'done']),
    # a while loop, labelled
    ('int n = 0\n'
     'outer: while n < 10\n'
     '    n = n + 1\n'
     '    for y in 0...5\n'
     '        if n == 3\n'
     '            break outer\n'
     'print("{n}")',
     ['3']),
    # strings owned inside both loops - freed on each jump (the leak check)
    ('outer: for x in 0...2\n'
     '    string a = "row {x}"\n'
     '    for y in 0...2\n'
     '        string b = "{a} col {y}"\n'
     '        if y == 1\n'
     '            continue outer\n'
     '        if x == 2\n'
     '            break outer\n'
     '        print(b)\n'
     'print("done")',
     ['row 0 col 0', 'row 1 col 0', 'done']),
    # over a List and an array
    ('List<string> names = ["ada", "bob", "cy"]\n'
     'outer: for name in names\n'
     '    for n in [1, 2]\n'
     '        if name == "bob"\n'
     '            continue outer\n'
     '        print("{name}{n}")',
     ['ada1', 'ada2', 'cy1', 'cy2']),
    # three loops deep, break out of the middle one
    ('for a in 0...1\n'
     '    middle: for b in 0...1\n'
     '        for c in 0...1\n'
     '            if c == 1\n'
     '                break middle\n'
     '            print("{a}{b}{c}")',
     ['000', '100']),
])
def test_break_and_continue_with_a_label(body, expected):
    assert run(body) == expected


def test_a_jump_runs_the_finally_inside_the_loop():
    body = ('outer: for x in 0...2\n'
            '    for y in 0...2\n'
            '        try\n'
            '            if y == 1\n'
            '                break outer\n'
            '            print("{x}{y}")\n'
            '        finally\n'
            '            print("finally {x}{y}")\n'
            'print("done")')
    assert run(body) == ['00', 'finally 00', 'finally 01', 'done']


@pytest.mark.parametrize('body, message', [
    ('for x in 0...2\n    break outer', "No loop labelled 'outer' around this break"),
    ('outer: for x in 0...2\n    for y in 0...2\n        continue inner',
     "No loop labelled 'inner' around this continue (the labels around it: outer)"),
    ('outer: for x in 0...2\n    print("x")', "The label 'outer' is never used"),
    ('outer: for x in 0...2\n    outer: for y in 0...2\n        break outer',
     "A loop around this one is labelled 'outer' already"),
])
def test_label_errors(body, message):
    assert message in errors_of(main(body))
