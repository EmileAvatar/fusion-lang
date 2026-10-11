"""Tests for Task 18.5.3 - text helpers that need lists: split, join, lines, words.
Every program runs under the leak check."""

import pytest

from tests.test_structs import errors_of, main
from tests.test_strings import run_ok


def test_split_keeps_every_piece():
    assert run_ok(main(
        'List<string> parts = "a,,b".split(",")\n'
        'print("{@1} [{@2}] [{@3}]", parts.len(), parts[1], parts[2])\n'
        'print("{@1} {@2} {@3}", split("a--b--c", "--").len(), "".split(",").len(), split(",", ",").len())\n'
        'print("{@1}", "caf\\u00e9".split("").join("-"))'
    )) == ['3 [] [b]', '3 1 2', 'c-a-f-\u00e9']


def test_join_as_function_and_method():
    assert run_ok(main(
        'List<string> parts = ["a", "b", "c"]\n'
        'print("{@1} {@2} [{@3}]", join(parts, ", "), parts.join(""), join(List<string>(), "x"))\n'
        'print("{@1}", join(["one"], "+"))'
    )) == ['a, b, c abc []', 'one']


def test_lines():
    assert run_ok(main(
        'List<string> rows = lines("one\\r\\ntwo\\n\\nfour\\n")\n'
        'print("{@1} {@2} {@3} [{@4}] {@5}", rows.len(), rows[0], rows[1], rows[2], rows[3])\n'
        'print("{@1} {@2} {@3}", lines("").len(), lines("x").len(), lines("\\n").len())'
    )) == ['4 one two [] four', '0 1 1']


def test_words():
    assert run_ok(main(
        'List<string> ws = words("  the  quick\\tbrown \\n fox ")\n'
        'print("{@1} {@2}", ws.len(), ws.join("|"))\n'
        'print("{@1}", "   ".words().len())'
    )) == ['4 the|quick|brown|fox', '0']


def test_round_trip_and_counting():
    assert run_ok(main(
        'string csv = "3,1,2"\n'
        'List<int> numbers\n'
        'for part in csv.split(",")\n'
        '    numbers.add(toInt(part))\n'
        'numbers.sort()\n'
        'Map<string, int> counts\n'
        'for w in words("the cat and the hat")\n'
        '    counts[w] = counts.get(w, 0) + 1\n'
        'print("{@1}{@2}{@3} {@4} {@5}", numbers[0], numbers[1], numbers[2], counts["the"], counts.len())'
    )) == ['123 2 4']


@pytest.mark.parametrize("body, message", [
    ('List<int> xs\nstring s = xs.join(",")', "join() needs a List<string>, got List<int>"),
    ('string s = join("abc", ",")', "Argument 1 to 'join': expected List<string>, got string"),
    ('List<string> p = split("a", 5)', "Argument 2 to 'split': expected string, got int"),
])
def test_errors(body, message):
    assert message in errors_of(main(body))
