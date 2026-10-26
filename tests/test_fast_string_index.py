"""Tests for Task 44.6 - fast text[i] for any string.

A non-ASCII string used to make every text[i] count from the start (28.1.2: a loop over
5,000 lines took 52 s). The run-time now remembers the last position found in an owned
string and continues from there. These tests check the answers stay right - forwards,
backwards, after the string is freed and its memory reused, and in substring - and that
the leak check stays clean.
"""

from tests.test_end_to_end import compile_and_run
from tests.test_structs import main


def run(body: str) -> list:
    code, out, err = compile_and_run(main(body))
    assert code == 0, err
    return out.strip().splitlines()


def test_forwards_and_backwards_over_non_ascii_text():
    lines = run('string s = "caf\\u00e9 " + "na\\u00efve \\u65e5\\u672c!"\n'
                'string forwards = ""\n'
                'for i in range(0, len(s))\n'
                '    forwards = forwards + s[i]\n'
                'string backwards = ""\n'
                'int i = len(s) - 1\n'
                'while i >= 0\n'
                '    backwards = backwards + s[i]\n'
                '    i = i - 1\n'
                'print(forwards)\n'
                'print(backwards)')
    assert lines[0] == 'caf\u00e9 na\u00efve \u65e5\u672c!'
    assert lines[1] == '!\u672c\u65e5 ev\u00efan \u00e9fac'


def test_jumping_around_gives_the_right_characters():
    lines = run('string s = "\\u00e9" + "a\\u00e9b\\u00e9c\\u00e9d"\n'
                'print("{@1}{@2}{@3}{@4}{@5}{@6}", s[6], s[1], s[7], s[0], s[3], s[5])')
    # s = e-acute a e-acute b e-acute c e-acute d: [6] [1] [7] [0] [3] [5]
    assert lines[0] == '\u00e9' + 'a' + 'd' + '\u00e9' + 'b' + 'c'


def test_a_new_string_in_the_same_variable_is_not_confused_with_the_old_one():
    lines = run('string s = "\\u00e9" + "xyz"\n'
                'char c = s[3]\n'
                's = "abc" + "\\u00e9"\n'               # same length, different text
                'print("{c}{@1}{@2}", s[3], s[0])')
    assert lines[0] == 'z\u00e9a'


def test_substring_uses_the_same_positions():
    lines = run('string s = "\\u00e9\\u00e8" + "abcdef"\n'
                'print(substring(s, 2, 3))\n'
                'print(substring(s, 1, 4))')
    assert lines == ['abc', '\u00e8abc']
