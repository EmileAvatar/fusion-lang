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


# 56.4 (D.214-D.217): the with part and check - after each pass; a condition ends the loop, none is a hook

@pytest.mark.parametrize('body, expected', [
    # a condition: true - its block, then the loop ends
    ('for x in 0...9\n'
     '    print("{x}")\n'
     'with\n'
     '    check x == 2\n'
     '        print("stop at {x}")\n'
     'print("done")',
     ['0', '1', '2', 'stop at 2', 'done']),
    # no condition: a hook every 3rd pass - the loop carries on
    ('for x in 1...7\n'
     '    int y = x\n'
     'with\n'
     '    check 3\n'
     '        print("pass {loop.count}")',
     ['pass 3', 'pass 6']),
    # every pass, no count
    ('for x in 1...3\n'
     '    int y = x\n'
     'with\n'
     '    check\n'
     '        print("after {x}")',
     ['after 1', 'after 2', 'after 3']),
    # the passes so far
    ('int n = 0\n'
     'while true\n'
     '    n = n + 1\n'
     'with\n'
     '    check >= 5\n'
     '        print("five passes, n = {n}")',
     ['five passes, n = 5']),
    # every 2nd pass, a condition - tested only then
    ('for x in 1...9\n'
     '    int y = x\n'
     'with\n'
     '    check 2 x > 4\n'
     '        print("stopped at {x}")',
     ['stopped at 6']),
    # a check without a block - just ends the loop
    ('int n = 0\n'
     'while true\n'
     '    n = n + 1\n'
     'with\n'
     '    check n == 4\n'
     'print("{n}")',
     ['4']),
    # several checks, in order
    ('for x in 1...10\n'
     '    int y = x\n'
     'with\n'
     '    check 4\n'
     '        print("progress {x}")\n'
     '    check x == 6\n'
     '        print("end {x}")',
     ['progress 4', 'end 6']),
    # continue in the body - the checks still run after that pass
    ('for x in 1...5\n'
     '    if x % 2 == 0\n'
     '        continue\n'
     '    print("odd {x}")\n'
     'with\n'
     '    check\n'
     '        print("checked {x}")',
     ['odd 1', 'checked 1', 'checked 2', 'odd 3', 'checked 3', 'checked 4', 'odd 5', 'checked 5']),
    # strings in the body, the loop variable a string - freed on every path (the leak check)
    ('List<string> names = ["ada", "bob", "cy", "dee"]\n'
     'for name in names\n'
     '    string shout = name.toUpper()\n'
     '    if name == "ada"\n'
     '        continue\n'
     '    string later = "{shout}!"\n'
     '    print(later)\n'
     'with\n'
     '    check name == "cy"\n'
     '        string bye = "bye {name}"\n'
     '        print(bye)',
     ['BOB!', 'CY!', 'bye cy']),
    # loop.count in the body
    ('for x in 5...7\n'
     '    print("{loop.count}: {x}")',
     ['1: 5', '2: 6', '3: 7']),
    # exit loop outer from an inner loop's check
    ('outer: for x in 0...3\n'
     '    for y in 0...3\n'
     '        print("{x}{y}")\n'
     '    with\n'
     '        check y == 1 and x == 1\n'
     '            exit loop outer\n'
     'print("done")',
     ['00', '01', '02', '03', '10', '11', 'done']),
    # return in a check leaves the function
    ('int r = firstBig()\nprint("{r}")',
     ['7']),
])
def test_checks(body, expected):
    top = ('int function firstBig()\n'
           '    for x in 1...9\n'
           '        int y = x\n'
           '    with\n'
           '        check x * x > 40\n'
           '            return x\n'
           '    return 0\n\n')
    assert run(body, top) == expected


@pytest.mark.parametrize('style', ['indent', 'braces', 'end'])
def test_checks_in_each_block_style(style):
    if style == 'indent':
        source = ('void function main()\n'
                  '    for x in 1...9\n'
                  '        print("{x}")\n'
                  '    with\n'
                  '        check x == 2\n'
                  '            print("stop")\n')
    elif style == 'braces':
        source = ('void function main() {\n'
                  '    for x in 1...9 {\n'
                  '        print("{x}")\n'
                  '    } with {\n'
                  '        check x == 2 { print("stop") }\n'
                  '    }\n'
                  '}\n')
    else:
        source = ('void function main()\n'
                  '    for x in 1...9\n'
                  '        print("{x}")\n'
                  '    end loop with\n'
                  '        check x == 2\n'
                  '            print("stop")\n')
    code, out, err = compile_and_run(source)
    assert code == 0, out + err
    assert out.split() == ['1', '2', 'stop']


def test_a_null_in_a_checks_condition():
    # Rule 4b: without a guard a NullError a catch handles; with ?. it runs on
    top = 'class Box\n    public int n = 3\n\n'
    body = ('Box b = null\n'
            'try\n'
            '    for x in 1...3\n'
            '        print("{x}")\n'
            '    with\n'
            '        check b.n == x\n'
            '            print("never")\n'
            'catch NullError e\n'
            '    print("caught")\n'
            'for x in 1...3\n'
            '    print("{x}")\n'
            'with\n'
            '    check (b?.n ?? 2) == x\n'
            '        print("stop at {x}")')
    assert run(body, top) == ['1', 'caught', '1', '2', 'stop at 2']


@pytest.mark.parametrize('body, message', [
    ('for x in 0...2\n    print("x")\nwith\n    check x == 1\n        break',
     "'break' can't be in a check - a check with a condition ends the loop by itself"),
    ('for x in 0...2\n    print("x")\nwith\n    check x == 1\n        continue', "'continue' can't be in a check"),
    ('for x in 0...2\n    exit loop', "'exit loop' belongs in a loop's check - in the body, write 'break'"),
    ('for x in 0...2\n    print("x")\nwith\n    check x == 1\n        exit loop outer',
     "No loop labelled 'outer' around this exit loop"),
    ('print("{loop.count}")', "'loop.count' is the pass number of a loop - use it inside one"),
])
def test_check_errors(body, message):
    assert message in errors_of(main(body))


@pytest.mark.parametrize('body, message', [
    ('for x in 0...2\n    print("x")\nwith\n    print("y")', "Only 'check' lines go in a loop's 'with' part"),
    ('for x in 0...2\n    print("x")\nwith\n    check', "A check without a condition runs its block"),
    ('for x in 0...2\n    print("x")\nwith\n    check 0\n        print("y")', "A check's count is a whole number above 0"),
    ('check x == 1', "'check' goes in a loop's 'with' part, after its body"),
])
def test_check_syntax_errors(body, message):
    from src.parser.parser import ParserError
    from tests.test_modules import parse_file
    with pytest.raises(ParserError, match=message):
        parse_file(main(body), 'main.fusion')


# 56.5 (D.218): [safety] maxIterations - a while past it stops with a LoopLimitError; 0 - nothing added

def run_with_limit(tmp_path, body: str, limit: int, top: str = '') -> tuple:
    """Build through main.py with a settings.toml setting the limit; (exit code, output)."""
    import os
    import subprocess
    import sys
    (tmp_path / 'settings.toml').write_text(f'[safety]\nmaxIterations = {limit}\n', encoding='utf-8')
    (tmp_path / 'main.fusion').write_text(top + main(body), encoding='utf-8')
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    built = subprocess.run([sys.executable, os.path.join(repo, 'main.py'), str(tmp_path / 'main.fusion')],
                           capture_output=True, text=True, encoding='utf-8')
    assert built.returncode == 0, built.stdout + built.stderr
    ran = subprocess.run([str(tmp_path / 'main.exe')], capture_output=True, text=True, encoding='utf-8')
    return ran.returncode, ran.stdout + ran.stderr


FOREVER = 'int n = 0\nwhile true\n    n = n + 1\nprint("{n}")'


def test_a_while_past_the_limit_stops(tmp_path):
    code, output = run_with_limit(tmp_path, FOREVER, 1000)
    assert code != 0
    # uncaught: "Runtime error at main.fusion:3: ..." - the loop's line, as every built-in error says it
    assert 'Runtime error at main.fusion:3: the loop passed [safety] maxIterations - 1000 passes' in output


def test_a_catch_handles_it(tmp_path):
    body = ('int n = 0\n'
            'try\n'
            '    while true\n'
            '        n = n + 1\n'
            'catch LoopLimitError e\n'
            '    print("stopped after {n}")')
    assert run_with_limit(tmp_path, body, 50) == (0, 'stopped after 50\n')


def test_a_loop_under_the_limit_runs(tmp_path):
    body = 'int n = 0\nwhile n < 100\n    n = n + 1\nprint("{n}")'
    assert run_with_limit(tmp_path, body, 100) == (0, '100\n')


def test_a_for_loop_has_no_limit(tmp_path):
    body = 'int n = 0\nfor x in 1...500\n    n = n + 1\nprint("{n}")'
    assert run_with_limit(tmp_path, body, 10) == (0, '500\n')


def test_a_loops_own_check_instead_of_the_limit(tmp_path):
    body = ('int n = 0\n'
            'while true\n'
            '    n = n + 1\n'
            'with\n'
            '    check >= 300\n'
            '        print("own limit at {n}")')
    assert run_with_limit(tmp_path, body, 10) == (0, 'own limit at 300\n')


def test_zero_adds_nothing(tmp_path):
    body = 'int n = 0\nwhile n < 5\n    n = n + 1\nprint("{n}")'
    assert run_with_limit(tmp_path, body, 0) == (0, '5\n')
    assert '_pass' not in (tmp_path / 'main.c').read_text(encoding='utf-8')     # no counter at all


@pytest.mark.parametrize('value', ['-1', '"lots"', 'true', '1.5'])
def test_bad_limits(tmp_path, value):
    from src.config import ProjectConfigError, load_project_config
    (tmp_path / 'settings.toml').write_text(f'[safety]\nmaxIterations = {value}\n', encoding='utf-8')
    (tmp_path / 'main.fusion').write_text(main('print("x")'), encoding='utf-8')
    with pytest.raises(ProjectConfigError, match='safety.maxIterations must be a whole number'):
        load_project_config(str(tmp_path / 'main.fusion'))
