"""Tests for Task 32.10a - Lists and Maps are references with a count.

User decisions 2026-10-29 (the truth table in Arrays.md section 1):
- in normal code - a variable, parameter, element - a List / Map is shared: `b = a`, passing
  and returning give the same one; `byVal a` (or byValue) copies it, deeply
- inside a struct it is copied with the struct, unless the field is `byRef`
- never null - empty when declared; freed when its last holder lets go

Every program runs with the leak check, so a list freed too early or never is a failure.
A List / Map is never null, so the with / without null check rule (4b) has nothing to test.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err                       # the leak check too
    return out.strip().splitlines()


def test_shared_in_normal_code_and_copied_with_byval():
    lines = run('void function grow(List<int> xs)\n    xs.add(9)\n\n'
                'void function look(byVal List<int> xs)\n    xs.add(100)\n\n'
                + main('List<int> a = [1]\n'
                       'List<int> b = a\n'
                       'b.add(2)\n'
                       'List<int> c = byVal a\n'
                       'c.add(3)\n'
                       'c.add(4)\n'
                       'grow(a)\n'
                       'look(a)\n'
                       'print("{@1} {@2} {@3}", a.len(), b.len(), c.len())\n'
                       'Map<string, int> m\n'
                       'Map<string, int> n = m\n'
                       'n["x"] = 1\n'
                       'Map<string, int> k = byValue m\n'
                       'k["y"] = 2\n'
                       'print("{@1} {@2} {@3}", m.len(), n.len(), k.len())'))
    assert lines == ['3 3 4', '1 1 2']


def test_a_struct_copies_its_lists_unless_byref():
    lines = run('struct Order\n    List<string> items\n    byRef List<string> log\n\n'
                'void function fill(Order o)\n    o.items.add("from function")\n\n'
                + main('Order o1 = Order(["a"], ["start"])\n'
                       'Order o2 = o1\n'
                       'o2.items.add("b")\n'
                       'o2.log.add("shared")\n'
                       'fill(o1)\n'
                       'print("{@1} {@2} {@3} {@4}", o1.items.len(), o2.items.len(), '
                       'o1.log.len(), o2.log.len())'))
    assert lines == ['1 2 2 2']


def test_nested_lists_shared_and_a_deep_copy():
    lines = run(main('List<List<int>> grid = [[1], [2]]\n'
                     'List<List<int>> deep = byVal grid\n'
                     'deep[0].add(5)\n'
                     'List<int> row = grid[1]\n'
                     'row.add(7)\n'
                     'print("{@1} {@2} {@3}", grid[0].len(), deep[0].len(), grid[1].len())'))
    assert lines == ['1 2 2']


def test_returned_and_module_level_lists():
    lines = run('List<int> seen\nMap<string, int> counts\n\n'
                'List<int> function make()\n    List<int> xs = [1, 2]\n    return xs\n\n'
                'void function note(int n)\n    seen.add(n)\n    counts["n"] = n\n\n'
                + main('note(4)\n'
                       'note(5)\n'
                       'List<int> got = make()\n'
                       'got.add(3)\n'
                       'print("{@1} {@2} {@3} {@4}", seen.len(), counts["n"], got.len(), '
                       'make().len())'))
    assert lines == ['2 5 3 2']


def test_a_list_freed_when_the_last_holder_lets_go():
    # Each pass makes a list, shares it and drops both holders - the leak check would stop
    # the program if one were kept, and a list freed while still held would crash it
    lines = run(main('List<int> keep\n'
                     'for i in range(0, 50)\n'
                     '    List<int> xs = [i]\n'
                     '    List<int> ys = xs\n'
                     '    ys.add(i)\n'
                     '    if i == 49\n'
                     '        keep = xs\n'
                     'print("{@1}", keep.len())'))
    assert lines == ['2']


@pytest.mark.parametrize('source, message', [
    ('struct S\n    byRef int n\n\nvoid function main()\n    S s\n',
     "byRef on field 'n': only a List or Map field can be shared"),
    ('void function f(byRef int x)\n    print("a")\n\nvoid function main()\n    f(1)\n',
     "byRef works on a List or Map parameter (shared already); a parameter of type int"),
    ('struct S\n    int n\n\nvoid function main()\n    S s\n    S t = byRef s\n',
     "byRef works on a List or Map (shared already in normal code); a value of type S is copied"),
])
def test_byref_errors(source, message):
    assert message in errors_of(source)
