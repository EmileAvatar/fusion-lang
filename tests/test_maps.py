"""Tests for Task 18.5.2 - Map<K, V>, also written Dictionary<K, V> (the same type).

Keys are string, int or char; values anything. A map remembers the order its keys were
added (keys(), values(), for k in m). It is a value like a list: copies are independent,
freed automatically. Every program runs under the leak check.
"""

import pytest

from tests.test_structs import errors_of, main
from tests.test_strings import run_ok, run_error


def test_adding_reading_replacing():
    assert run_ok(main(
        'Map<string, int> ages = Map<string, int>()\n'
        'ages["Alice"] = 30\n'
        'ages["Bob"] = 25\n'
        'ages["Alice"] = 31\n'
        'print("{@1} {@2} {@3} {@4} {@5}", ages["Alice"], ages.len(), len(ages), ages.has("Bob"), ages.has("Zed"))\n'
        'print("{@1} {@2}", ages.get("Zed", -1), ages.get("Bob", -1))\n'
        'bool removed = ages.remove("Bob")\n'
        'bool again = ages.remove("Bob")\n'
        'print("{@1} {@2} {@3}", removed, again, ages.len())\n'
        'ages.clear()\n'
        'Map<string, int> none\n'
        'print("{@1} {@2}", ages.len(), none.len())'
    )) == ['31 2 2 true false', '-1 25', 'true false 1', '0 0']


def test_insertion_order():
    assert run_ok(main(
        'Map<string, int> m\n'
        'm["c"] = 3\n'
        'm["a"] = 1\n'
        'm["b"] = 2\n'
        'm["a"] = 10\n'
        'List<string> ks = m.keys()\n'
        'List<int> vs = m.values()\n'
        'print("{@1}{@2}{@3} {@4} {@5} {@6}", ks[0], ks[1], ks[2], vs[0], vs[1], vs[2])\n'
        'for k in m\n'
        '    print(k)'
    )) == ['cab 3 10 2', 'c', 'a', 'b']


def test_many_entries_grow_and_remove():
    assert run_ok(main(
        'Map<int, string> names\n'
        'for i in range(0, 200)\n'
        '    names[i] = "n" + toString(i)\n'
        'for i in range(0, 200, 2)\n'
        '    names.remove(i)\n'
        'print("{@1} {@2} {@3} {@4}", names.len(), names.has(100), names[101], names.keys()[0])'
    )) == ['100 false n101 1']


def test_char_keys_and_counting():
    assert run_ok(main(
        'Map<char, int> counts\n'
        'string text = "banana"\n'
        'for i in range(0, len(text))\n'
        '    counts[text[i]] = counts.get(text[i], 0) + 1\n'
        'print("{@1} {@2} {@3} {@4}", counts[\'a\'], counts[\'n\'], counts[\'b\'], counts.len())'
    )) == ['3 2 1 3']


def test_maps_are_values():
    assert run_ok('Map<string, int> function scores() \n    Map<string, int> m\n    m["x"] = 1\n    return m\n\n'
                  'int function total(Map<string, int> m) : m.values().reduce(0, (int s, int x) : s + x)\n\n'
                  'void function bump(Map<string, int> m)\n    m["x"] = 100\n\n' + main(
                      'Map<string, int> a = scores()\n'
                      'Map<string, int> b = a\n'
                      'b["y"] = 2\n'
                      'bump(a)\n'
                      'print("{@1} {@2} {@3} {@4}", a.len(), b.len(), a["x"], total(b))\n'
                      'b.remove("y")\n'
                      'print("{@1} {@2}", a == b, a != b)'
                  )) == ['1 2 1 3', 'true false']


def test_equality_ignores_order():
    assert run_ok(main(
        'Map<string, int> a\n'
        'a["x"] = 1\n'
        'a["y"] = 2\n'
        'Map<string, int> b\n'
        'b["y"] = 2\n'
        'b["x"] = 1\n'
        'Map<string, int> c = b\n'
        'c["x"] = 9\n'
        'print("{@1} {@2}", a == b, a == c)'
    )) == ['true false']


def test_nested_and_in_structs():
    assert run_ok('struct Person\n    string name\n    Map<string, int> scores\n\n' + main(
        'Dictionary<string, List<string>> groups = Dictionary<string, List<string>>()\n'
        'groups["admins"] = ["ann"]\n'
        'groups["admins"].add("ben")\n'
        'groups["users"] = List<string>()\n'
        'Map<string, Map<string, int>> deep\n'
        'deep["a"] = Map<string, int>()\n'
        'deep["a"]["b"] = 7\n'
        'Person p = Person("Ada", Map<string, int>())\n'
        'p.scores["math"] = 90\n'
        'Person q = p\n'
        'q.scores["math"] = 50\n'
        'List<Map<string, int>> rows = [p.scores, q.scores]\n'
        'print("{@1} {@2} {@3} {@4} {@5}", groups["admins"][1], groups.keys()[1], deep["a"]["b"], p.scores["math"], rows[1]["math"])'
    )) == ['ben users 7 90 50']


@pytest.mark.parametrize("statement, message", [
    ('Map<string, int> m\nprint("{@1}", m["nope"])', 'key "nope" is not in the map'),
    ('Map<int, int> m\nprint("{@1}", m[42])', 'key 42 is not in the map'),
    ("Map<char, int> m\nprint(\"{@1}\", m['q'])", "key 'q' is not in the map"),
    ('Map<string, List<int>> m\nm["a"][0] = 5', 'key "a" is not in the map'),
])
def test_run_time_errors(statement, message):
    assert message in run_error(main(statement))


@pytest.mark.parametrize("body, message", [
    ('Map<float, int> m', "Map keys can be string, int or char, got float"),
    ('Map<string, void> m', "A Map can't hold void"),
    ('Map<string, int> m\nm[1] = 2', "Map key must be string, got int"),
    ('Map<string, int> m\nm["a"] = "b"', "Cannot assign string to array element of type int"),
    ('Map<string, int> m\nint n = m.size()', "Map<string, int> has no method 'size'"),
    ('Map<string, int> m\nbool b = m.has(1)', "Argument of 'has': expected string, got int"),
    ('Map<string, int> m\nint x = m.get("a")', "Map method 'get' takes 2 argument(s), got 1"),
    ('const Map<string, int> m = Map<string, int>()\nm.clear()', "'clear' can't change constant 'm'"),
    ('Map<string, int> m\nMap<string, float> f = m', "Cannot assign Map<string, int> to variable of type Map<string, float>"),
])
def test_compile_errors(body, message):
    assert message in errors_of(main(body))


def test_dictionary_is_the_same_type():
    assert run_ok(main('Dictionary<string, int> d\nd["a"] = 1\nMap<string, int> m = d\nprint("{@1}", m["a"])')) == ['1']
