"""Ranges `1...10` (Task 33.2f, SYN.034): in a for / foreach - both ends included, the same as
range(1, 11); and in a match case - `case 0...9`, `'a'...'z' : "lower"` (L7.7)."""
import pytest

from src.parser.parser import ParserError
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_structs import parse


def run(body: str, top: str = '') -> list:
    source = top + 'void function main()\n' + ''.join(f'    {line}\n' for line in body.split('\n'))
    code, out, err = compile_and_run(source)
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def errors_of(body: str, top: str = '') -> list:
    source = top + 'void function main()\n' + ''.join(f'    {line}\n' for line in body.split('\n'))
    analyzer = SemanticAnalyzer()
    analyzer.analyze(parse(source))
    return [e.message for e in analyzer.get_errors()]


@pytest.mark.parametrize('body, lines', [
    ('int t = 0\nfor i in 1...10\n    t = t + i\nprint("{t}")', ['55']),
    ('int t = 0\nfor i in range(1, 11)\n    t = t + i\nprint("{t}")', ['55']),        # the same, written as range
    ('int n = 3\nfor i in 0...n - 1\n    print("{i}")', ['0', '1', '2']),
    ('for i in -2...0\n    print("{i}")', ['-2', '-1', '0']),
    ('for i in 5...5\n    print("{i}")', ['5']),                                      # one value
    ('int a = 2\nint b = 3\nfor i in a...b\n    print("{i}")', ['2', '3']),
    ('int a = 3\nint b = 1\nfor i in a...b\n    print("{i}")\nprint("none")', ['none']),   # as range: no turns
    ('foreach (int k in 3...4)\n    print("{k}")', ['3', '4']),
    ('double d = 1.5\nfloat f = 2.\nprint("{@1} {@2}", d, f)', ['1.500000 2.000000']),  # decimals still decimals
])
def test_ranges_in_loops(body, lines):
    assert run(body) == lines


@pytest.mark.parametrize('body', ['for i in 0.5...2.5\n    print("x")', 'double d = 2.0\nfor i in 0...d\n    print("x")'])
def test_a_decimal_range_says_whole_numbers(body):
    found = errors_of(body)
    assert len(found) == 1 and 'A range ... counts whole numbers' in found[0] and '47.6' in found[0], found


def test_setting_names_ignore_spaces():
    from src.config.project_config import _folded
    assert _folded('strict Step') == _folded('strict_step') == _folded('strictStep') == 'strictstep'


def test_a_range_written_backwards_is_an_error():
    with pytest.raises(ParserError, match=r"10\.\.\.1 counts down .* range\(10, 0, -1\)"):
        parse('void function main()\n    for i in 10...1\n        print("{i}")\n')


GRADES = ('string function grade(int score)\n'
          '    match score\n'
          '        case 90...100\n'
          '            return "A"\n'
          '        case 80...89, 79\n'
          '            return "B"\n'
          '        case -10...-1\n'
          '            return "negative"\n'
          '        else\n'
          '            return "C"\n\n'
          'string function kind(char c)\n'
          '    string k = match c\n'
          '        \'a\'...\'z\' : "lower"\n'
          '        \'A\'...\'Z\' : "upper"\n'
          '        \'0\'...\'9\' : "digit"\n'
          '        else : "other"\n'
          '    return k\n\n')


def test_ranges_in_match_cases():
    body = 'print(grade(95))\nprint(grade(79))\nprint(grade(-3))\nprint(grade(50))\n' \
           'print(kind(\'q\'))\nprint(kind(\'Q\'))\nprint(kind(\'5\'))\nprint(kind(\'!\'))'
    assert run(body, top=GRADES) == ['A', 'B', 'negative', 'C', 'lower', 'upper', 'digit', 'other']


@pytest.mark.parametrize('cases, message', [
    ('        case 0...9\n            print("a")\n        case 5\n            print("b")\n',
     'already handled by an earlier case'),
    ('        case 0...9\n            print("a")\n        case 8...20\n            print("b")\n',
     'already handled by an earlier case'),
    ('        case 0...x\n            print("a")\n', 'needs a constant'),
])
def test_match_range_mistakes(cases, message):
    found = errors_of('int x = 3\nmatch x\n' + cases.replace('\n        ', '\n    ').replace('        case', '    case', 1)
                      + '    else\n        print("c")')
    assert any(message in e for e in found), found


def test_a_case_range_on_text_is_an_error():
    found = errors_of('string s = "b"\nmatch s\n    case "a"..."c"\n        print("x")\n    else\n        print("y")')
    assert any('works on whole numbers and characters' in e for e in found), found


def test_a_case_range_written_backwards_is_an_error():
    with pytest.raises(ParserError, match=r"case 9\.\.\.0 .* case 0\.\.\.9"):
        parse('void function main()\n    int x = 1\n    match x\n        case 9...0\n            print("a")\n'
              '        else\n            print("b")\n')


def test_a_line_starting_with_a_character_is_code():
    # the indentation reader took a line starting with ' for a VB comment (off - SYN.031)
    assert run("char c = 'q'\nstring k = match c\n    'q' : \"q\"\n    else : \"other\"\nprint(k)") == ['q']
