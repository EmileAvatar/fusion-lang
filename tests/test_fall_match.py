"""Tests for Task 30.13 - `fall match`: falls through until break.

Like a C / Java / C# `switch` (user, 2026-10-28): the matching case runs, then each case
below it, until a `break`; the `else` runs when nothing matched, and is fallen into too. A
plain `match` never falls through. `fall` is a word only right before `match`.
"""

from tests.test_end_to_end import compile_and_run
from tests.test_structs import main, errors_of

LEVEL = 'enum Level\n    Low\n    Mid\n    High\n\n'


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


def test_an_enum_falls_through_to_the_break():
    lines = run(LEVEL
                + 'string function steps(Level l)\n'
                  '    string out = ""\n'
                  '    fall match l\n'
                  '        case High: out = out + "H"\n'
                  '        case Mid: out = out + "M"\n'
                  '        case Low\n'
                  '            out = out + "L"\n'
                  '            break\n'
                  '    return out\n\n'
                + main('print(steps(Level.High))\nprint(steps(Level.Mid))\nprint(steps(Level.Low))'))
    assert lines == ['HML', 'ML', 'L']


def test_constants_break_and_else():
    lines = run(main('fall match 2\n'
                     '    case 1: print("one")\n'
                     '    case 2: print("two")\n'
                     '    case 3\n'
                     '        print("three")\n'
                     '        break\n'
                     '    case 4: print("four")\n'
                     '    else: print("else")\n'
                     'fall match 4\n'
                     '    case 4: print("four")\n'
                     '    else: print("fell into else")\n'
                     'fall match 9\n'
                     '    case 1: print("one")\n'
                     '    else: print("nothing matched")'))
    assert lines == ['two', 'three', 'four', 'fell into else', 'nothing matched']


def test_a_plain_match_still_never_falls_through_and_fall_is_a_name():
    lines = run(main('match 1\n'
                     '    case 1: print("one")\n'
                     '    case 2: print("two")\n'
                     '    else: print("else")\n'
                     'string fall = "a name"\n'
                     'print(fall)'))
    assert lines == ['one', 'a name']


def test_a_fall_match_cannot_read_a_values_data():
    message = errors_of('enum Token\n    Number(int value)\n    Word(string text)\n\n'
                        + main('Token t = Token.Number(1)\n'
                               'fall match t\n'
                               '    case Number(n): print("{n}")\n'
                               '    else: print("x")'))
    assert "A 'fall match' can't read a value's data" in message
