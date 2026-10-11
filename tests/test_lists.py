"""Tests for Task 18.5.1 - List<T> (src/semantic/collection_rules.py, src/codegen/c_collections.py).

A list is a value like a string (user decision 2026-10-11): a copy is independent, it is
freed automatically, functions borrow it, new lists are moved. Every program runs under
the leak check, so each test also proves nothing is freed twice or left over.
"""

import pytest

from tests.test_structs import errors_of, main
from tests.test_strings import run_ok, run_error

ECHO = 'string function echo(string s)\n    return s\n\n'


def test_making_and_changing_a_list():
    assert run_ok(main(
        'List<int> xs = [3, 1, 2]\n'
        'xs.add(10)\n'
        'xs.insert(0, 7)\n'
        'xs[1] = 5\n'
        'print("{@1} {@2} {@3} {@4}", len(xs), xs.len(), xs[0], xs[4])\n'
        'xs.removeAt(1)\n'
        'bool gone = xs.remove(2)\n'
        'bool missing = xs.remove(99)\n'
        'print("{@1} {@2} {@3} {@4} {@5}", xs.len(), gone, missing, xs.contains(10), xs.indexOf(1))\n'
        'List<int> part = xs.slice(1, 2)\n'
        'print("{@1} {@2} {@3}", part.len(), part[0], part[1])\n'
        'xs.clear()\n'
        'List<int> none = List<int>()\n'
        'List<int> also\n'
        'print("{@1} {@2} {@3}", xs.len(), none.len(), also.len())'
    )) == ['5 5 7 10', '3 true false true 1', '2 1 10', '0 0 0']


def test_sorting():
    assert run_ok(main(
        'List<int> xs = [5, -1, 3, 3, 0]\n'
        'xs.sort()\n'
        'List<string> words = ["pear", "Apple", "fig"]\n'
        'words.sort()\n'
        'List<float> fs = [2.5, 0.5]\n'
        'fs.sort()\n'
        'xs.sortBy((int a, int b) : b - a)\n'
        'print("{@1} {@2} {@3} | {@4} {@5} {@6} | {@7}", xs[0], xs[2], xs[4], words[0], words[1], words[2], fs[0])'
    )) == ['5 3 -1 | Apple fig pear | 0.500000']


def test_sort_by_is_stable():
    assert run_ok('struct P\n    string name\n    int age\n\n'
                  'int function byAge(P a, P b) : a.age - b.age\n\n' + main(
                      'List<P> ps = [P("a", 2), P("b", 1), P("c", 2), P("d", 1)]\n'
                      'ps.sortBy(byAge)\n'
                      'print("{@1}{@2}{@3}{@4}", ps[0].name, ps[1].name, ps[2].name, ps[3].name)'
                  )) == ['bdac']


def test_filter_map_reduce():
    assert run_ok(ECHO + 'string function label(int x) : "#{x}"\n\n'
                  'string function joined(string acc, string s) : acc + s\n\n' + main(
                      'List<int> xs = [1, 2, 3, 4]\n'
                      'List<int> big = xs.filter((int x) : x > 2)\n'
                      'List<string> labels = xs.map(label)\n'
                      'int total = xs.reduce(0, (int sum, int x) : sum + x)\n'
                      'string all = labels.reduce(echo(""), joined)\n'
                      'print("{@1} {@2} {@3} {all}", big.len(), labels[3], total)\n'
                      'print("{@1}", xs.filter((int x) : x % 2 == 0).map(label)[1])'
                  )) == ['2 #4 10 #1#2#3#4', '#4']


def test_copies_are_independent():
    assert run_ok(main(
        'List<string> a = ["x", "y"]\n'
        'List<string> b = a\n'
        'b[0] = "changed"\n'
        'b.add("z")\n'
        'print("{@1} {@2} {@3} {@4}", a[0], a.len(), b[0], b.len())'
    )) == ['x 2 changed 3']


def test_functions_borrow_and_copy_when_they_change_a_list():
    assert run_ok('int function total(List<int> xs) : xs.reduce(0, (int s, int x) : s + x)\n\n'
                  'List<int> function grow(List<int> xs)\n    xs.add(100)\n    return xs\n\n'
                  'List<string> function names() : ["Ada", "Grace"]\n\n' + main(
                      'List<int> xs = [1, 2]\n'
                      'List<int> bigger = grow(xs)\n'
                      'print("{@1} {@2} {@3} {@4}", xs.len(), bigger.len(), total(bigger), names()[1])'
                  )) == ['2 3 103 Grace']


def test_lists_in_structs_and_lists_of_lists():
    assert run_ok('struct Team\n    string name\n    List<string> members\n\n' + main(
        'Team t = Team("core", ["Ada"])\n'
        't.members.add("Ken")\n'
        'Team u = t\n'
        'u.members[0] = "Changed"\n'
        'List<Team> teams = [t, u]\n'
        'teams[1].members.add("Extra")\n'
        'print("{@1} {@2} {@3} {@4}", t.members[0], u.members[0], teams[1].members.len(), u.members.len())\n'
        'List<List<int>> grid = [[1, 2], [3, 4]]\n'
        'grid[1][0] = 9\n'
        'grid.add([5])\n'
        'grid[2].add(6)\n'
        'print("{@1} {@2} {@3}", grid[1][0], grid[2][1], grid == [[1, 2], [9, 4], [5, 6]])'
    )) == ['Ada Changed 3 2', '9 6 true']


def test_equality():
    assert run_ok(main(
        'List<int> a = [1, 2]\n'
        'List<int> b = [1, 2]\n'
        'print("{@1} {@2} {@3} {@4}", a == b, a != [2, 1], a == [1, 2, 3], [1, 2] == a)'
    )) == ['true true false true']


def test_for_each():
    assert run_ok(ECHO + 'List<int> function make() : [7, 8]\n\n' + main(
        'List<string> words = [echo("a"), "b", "c"]\n'
        'string all = ""\n'
        'for w in words\n'
        '    if w == "c"\n'
        '        break\n'
        '    all = all + w\n'
        'for n in make()\n'
        '    print("{n}")\n'
        'int[3] arr = [4, 5, 6]\n'
        'int sum = 0\n'
        'for v in arr\n'
        '    if v == 5\n'
        '        continue\n'
        '    sum = sum + v\n'
        'print("{all} {sum}")'
    )) == ['7', '8', 'ab 10']


def test_changing_a_list_while_looping_over_it_is_safe():
    assert run_ok(main(
        'List<string> xs = ["a", "b"]\n'
        'for s in xs\n'
        '    xs.add(s + "!")\n'
        '    xs.removeAt(0)\n'
        'print("{@1} {@2}", xs.len(), xs[0])'
    )) == ['2 a!']


def test_return_from_inside_a_for_each_frees_everything():
    assert run_ok(ECHO + 'string function first(List<string> xs, string start)\n'
                  '    for s in xs\n'
                  '        if s.startsWith(start)\n'
                  '            return s\n'
                  '    return ""\n\n' + main(
                      'print(first([echo("apple"), "banana"], "b"))\n'
                      'print("[{@1}]", first(["x"], "q"))'
                  )) == ['banana', '[]']


def test_for_each_over_an_array_parameter():
    assert run_ok('int function sum(int[] values)\n    int total = 0\n    for v in values\n'
                  '        total = total + v\n    return total\n\n'
                  + main('int[4] xs = [1, 2, 3, 4]\nprint("{@1}", sum(xs))')) == ['10']


@pytest.mark.parametrize("statement, message", [
    ('List<int> xs = [1]\nprint("{@1}", xs[1])', "index 1 is outside the list (length 1)"),
    ('List<int> xs = [1]\nxs[-1] = 3', "index -1 is outside the list (length 1)"),
    ('List<int> xs = [1]\nxs.insert(5, 2)', "insert(position 5) is outside the list (length 1)"),
    ('List<int> xs\nxs.removeAt(0)', "removeAt(0) is outside the list (length 0)"),
    ('List<int> xs = [1, 2]\nList<int> s = xs.slice(1, 5)', "slice(start 1, count 5) is outside the list (length 2)"),
])
def test_run_time_errors(statement, message):
    assert message in run_error(main(statement))


@pytest.mark.parametrize("body, message", [
    ('List<int> xs = [1, "two"]', "A List<int> element must be int, got string"),
    ('List<int> xs\nxs.add("x")', "The value of 'add': expected int, got string"),
    ('List<int> xs\nint n = xs.size()', "List<int> has no method 'size'"),
    ('List<int> xs\nxs.add()', "List method 'add' takes 1 argument(s), got 0"),
    ('List<int> xs\nList<int> ys = xs.filter((int x) : x * 2)', "'filter' needs a function (int) -> bool"),
    ('const List<int> xs = [1]\nxs.add(2)', "'add' can't change constant 'xs'"),
    ('for x in 5\n    print("x")', "'for ... in' needs range(...), a List or an array, got int"),
    ('List<int> xs\nprint("{xs}")', "Can't print a whole List<int> value"),
    ('Map<string, int> m = Map<string, int>()', "Map / Dictionary comes with Task 18.5.2"),
    ('List<void> xs', "A List can't hold void"),
    ('List<int> xs\nList<string> ys = xs', "Cannot assign List<int> to variable of type List<string>"),
])
def test_compile_errors(body, message):
    assert message in errors_of(main(body))


def test_sort_needs_comparable_elements():
    assert "sort() works on lists of numbers, chars, bools and text" in errors_of(
        'struct P\n    int x\n\n' + main('List<P> ps\nps.sort()'))


def test_a_struct_cannot_be_named_list():
    assert "'List' is a built-in type" in errors_of('struct List\n    int x\n\n' + main('int y = 1'))
