"""Tests for Task 18.3.6 - the versatile string functions (src/codegen/c_strings.py).

Positions and counts are characters; letters are ASCII + Latin-1; "up to n" functions
clamp quietly; a negative count is a run-time error. Every program runs under the leak
check (see tests/test_end_to_end.py).
"""

import os
import subprocess
import tempfile

import pytest

from src.codegen.c_memory import RUNTIME_PRELUDE
from tests.test_structs import errors_of, main
from tests.test_strings import run_ok, run_error, ECHO


def show(*expressions: str) -> str:
    """A print statement showing each expression, separated by ` | `."""
    holes = ' | '.join(f'{{@{i + 1}}}' for i in range(len(expressions)))
    return f'print("{holes}", {", ".join(expressions)})'


@pytest.mark.parametrize("ascii_mode", [False, True])
def test_runtime_compiles_cleanly(ascii_mode):
    """The whole runtime - every string function - compiles with no warnings under
    -Wall -Wextra, in UTF-8 and in ascii mode (fusion_char is one byte there)."""
    with tempfile.TemporaryDirectory() as tmp:
        c_file = os.path.join(tmp, 'rt.c')
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(('#define FUSION_ASCII 1\n' if ascii_mode else '')
                    + '#include <stdarg.h>\n#include <stdbool.h>\n#include <stdint.h>\n'
                    '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n'
                    + RUNTIME_PRELUDE + 'int main(void) { return 0; }\n')
        build = subprocess.run(['gcc', '-Wall', '-Wextra', '-c', c_file, '-o',
                                os.path.join(tmp, 'rt.o')], capture_output=True, text=True)
        assert build.returncode == 0 and 'warning' not in build.stderr, build.stderr


# ============================================================
# 18.3.6a - Inspect, search, extract
# ============================================================

def test_inspect():
    assert run_ok(main(
        show('isEmpty("")', 'isEmpty(" ")', 'isBlank(" \\t\\n")', 'isBlank("")', 'isBlank(" x ")')
        + '\n' + show('isDigits("0123")', 'isDigits("")', 'isDigits("12a")', 'isDigits("-1")')
        + '\n' + show('isLetters("Caf\\u00e9")', 'isLetters("Stra\\u00dfe")', 'isLetters("")',
                      'isLetters("a b")', 'isLetters("x2")', 'isLetters("\\u65e5")')
        + '\n' + show('countOf("aaaa", "aa")', 'countOf("banana", "a")', 'countOf("abc", "")',
                      'countOf("\\u00e9t\\u00e9", "\\u00e9")')
    )) == ['true | false | true | true | false', 'true | false | false | false',
           'true | true | false | false | false | false', '2 | 3 | 0 | 2']


def test_search_counts_characters():
    assert run_ok(main(
        'string s = "caf\\u00e9 au lait"\n'
        + show('indexOf(s, "a")', 'indexOf(s, "a", 2)', 'indexOf(s, "a", 100)', 'indexOf(s, "a", -5)',
               'indexOf(s, "z")', 'lastIndexOf(s, "a")', 'lastIndexOf(s, "\\u00e9")', 'lastIndexOf(s, "z")')
        + '\n' + show('containsAny(s, "xyz\\u00e9")', 'containsAny(s, "xyz")', 'containsAny(s, "")')
    )) == ['1 | 5 | -1 | 1 | -1 | 9 | 3 | -1', 'true | false | false']


def test_left_and_right_clamp():
    assert run_ok(ECHO + main(
        'string s = echo("caf\\u00e9!")\n'
        'print("[{@1}] [{@2}] [{@3}] [{@4}] [{@5}]", left(s, 4), right(s, 2), left(s, 99), right(s, 99), left(s, 0))'
    )) == ['[caf\u00e9] [\u00e9!] [caf\u00e9!] [caf\u00e9!] []']


@pytest.mark.parametrize("call, message", [
    ('left("abc", -1)', "left(-1): the count can't be negative"),
    ('right("abc", -2)', "right(-2): the count can't be negative"),
])
def test_negative_counts_are_run_time_errors(call, message):
    assert message in run_error(main(f'print({call})'))


def test_optional_argument_counts():
    errors = errors_of(main('int a = indexOf("abc")\nint b = indexOf("abc", "b", 1, 2)'))
    assert "Function 'indexOf' expects 2 to 3 arguments, got 1" in errors
    assert "Function 'indexOf' expects 2 to 3 arguments, got 4" in errors


def test_own_function_replaces_a_library_built_in():
    """left, right, ... are everyday names: a program's own function or struct with that
    name replaces the built-in; a local variable just shadows it."""
    assert run_ok('int function right(int a)\n    return a + 1\n\nstruct left\n    int x\n\n' + main(
        'int remove = 2\n'
        'left l = left(right(remove))\n'
        'print("{@1}", l.x)'
    )) == ['3']


def test_core_built_ins_cannot_be_replaced():
    assert "Duplicate declaration of 'print'" in errors_of('void function print(string s)\n    return\n\n'
                                                            + main('int x = 1'))


# ============================================================
# 18.3.6b - Change
# ============================================================

def test_replace_insert_remove():
    assert run_ok(ECHO + main(
        'string s = echo("a-b-c")\n'
        'print("[{@1}] [{@2}] [{@3}] [{@4}]", replace(s, "-", "+="), replaceFirst(s, "-", ""), replace(s, "", "x"), replace(s, "z", "y"))\n'
        'print("[{@1}] [{@2}] [{@3}]", insert("caf\u00e9", 3, "-"), insert("ab", 2, "!"), insert("", 0, "x"))\n'
        'print("[{@1}] [{@2}] [{@3}]", remove("caf\u00e9 au", 2, 3), remove("abc", 0, 3), remove("abc", 3, 0))\n'
        's = replace(s, "b", s)\n'
        'print(s)'
    )) == ['[a+=b+=c] [ab-c] [a-b-c] [a-b-c]', '[caf-\u00e9] [ab!] [x]', '[caau] [] [abc]', 'a-a-b-c-c']


def test_repeat_reverse_trim():
    assert run_ok(main(
        'print("[{@1}] [{@2}] [{@3}]", repeat("ab", 3), repeat("ab", 0), repeat("", 5))\n'
        'print("[{@1}] [{@2}] [{@3}]", reverse("caf\u00e9"), reverse(""), reverse("\u65e5\u672c!"))\n'
        'print("[{@1}] [{@2}]", trimStart("  x  "), trimEnd("  x \t\n"))'
    )) == ['[ababab] [] []', '[\u00e9fac] [] [!\u672c\u65e5]', '[x  ] [  x]']


def test_case_covers_latin_1():
    """ASCII + Latin-1 (user decision): toUpper / toLower now change accented letters too;
    capitalize and toTitle change only first letters, so acronyms survive."""
    assert run_ok(main(
        'print("{@1} {@2}", toUpper("caf\u00e9 \u00fcber \u00ff\u00df"), toLower("CAF\u00c9 \u0178"))\n'
        'print("[{@1}] [{@2}] [{@3}]", capitalize("  hello world"), capitalize("\u00e9t\u00e9"), capitalize("42"))\n'
        'print("[{@1}] [{@2}]", toTitle("hello  big\tworld"), toTitle("NASA and jean-luc"))'
    )) == ['CAF\u00c9 \u00dcBER \u0178\u00df caf\u00e9 \u00ff',
           '[  Hello world] [\u00c9t\u00e9] [42]',
           '[Hello  Big\tWorld] [NASA And Jean-luc]']


@pytest.mark.parametrize("call, message", [
    ('insert("abc", 4, "x")', "insert(index 4) is outside the string (length 3)"),
    ('insert("abc", -1, "x")', "insert(index -1) is outside the string"),
    ('remove("abc", 1, 3)', "remove(start 1, count 3) is outside the string (length 3)"),
    ('repeat("ab", -1)', "repeat(-1): the count can't be negative"),
    ('repeat("abcdefgh", 1000000000)', "repeat: the result would be longer than"),
])
def test_change_run_time_errors(call, message):
    assert message in run_error(main(f'print({call})'))
