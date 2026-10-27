"""Tests for Task 30.7 - the conditional operator: `(condition) ? a : b`.

One line that gives a value: the first when the condition holds, else the second - and only
the chosen one runs. Both values have one type. A string result is always a fresh value (a
borrowed one is copied), so it can be stored or used once and freed - the leak check in
compile_and_run covers that.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import main, errors_of


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


def test_numbers_strings_and_nesting():
    lines = run(main('int count = 7\n'
                     'string size = (count > 5) ? "big" : "small"\n'
                     'int k = (count > 100) ? 1 : (count > 5) ? 2 : 3\n'
                     'float f = (count > 0) ? 1.5 : 2.5\n'
                     'print("{size} {k} {f}")'))
    assert lines == ['big 2 1.500000']


def test_string_ownership_borrowed_fresh_and_reassigned():
    lines = run('string function word(int n) : "w{n}"\n\n'
                + main('int count = 7\n'
                       'string s = "abc"\n'
                       'string t = (count < 5) ? s : s + "!"\n'
                       'print(t)\n'
                       'print((count == 7) ? word(1) : word(2))\n'
                       's = (count > 5) ? s + "de" : s\n'
                       'print(s)\n'
                       'print("{@1}", ((count > 5) ? "yes" : "no").length)'))
    assert lines == ['abc!', 'w1', 'abcde', '3']


def test_only_the_chosen_value_runs():
    lines = run('int function shout(string s)\n'
                '    print(s)\n'
                '    return 1\n\n'
                + main('int n = true ? shout("then") : shout("else")\n'
                       'print("{n}")'))
    assert lines == ['then', '1']


@pytest.mark.parametrize('body, message', [
    ('int n = 5 ? 1 : 2', "The condition of '? :' must be bool, got int"),
    ('string s = true ? "a" : 3', "The two values of '? :' must have the same type"),
    ('int n = true ? 1', "Expected ':' between the two values"),
])
def test_errors(body, message):
    if 'Expected' in message:
        with pytest.raises(Exception, match="Expected ':'"):
            errors_of(main(body))
    else:
        assert message in errors_of(main(body))
