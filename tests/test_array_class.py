"""Task 45.1 - the built-in Array class (D.142): every array acts as an object of it, so
`Array.length(a)` and `a.length()` / `a.length` / `len(a)` mean the same; `toList` and `toCSV` too.
"""
import re

import pytest

from src.parser.parser import ParserError
from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main, parse

POINT = 'struct Point\n    int x\n    int y\n\n'


@pytest.mark.parametrize('form', ['Array.length(a)', 'Array.len(a)', 'a.length()', 'a.length',
                                  'a.len()', 'len(a)'])
def test_every_form_of_the_length(form):
    assert run(main(f'int[] a = [5, 2, 3]\nprint("{{@1}}", {form})')) == ['3']


def test_array_to_list_through_the_class():
    out = run(main('int[] a = [5, 2, 3]\nList<int> xs = Array.toList(a)\nxs.add(4)\n'
                   'print("{@1} {@2}", xs.len(), a.length)'))
    assert out == ['4 3']


def test_array_to_csv_through_the_class():
    out = run(POINT + main('Point[] ps = [Point(1, 2), Point(3, 4)]\nprint(Array.toCSV(ps, ";"))\n'
                           'print(ps.toCSV(";"))'))
    assert out[:3] == out[3:] and out[:3] == ['Point.x;Point.y', '1;2', '3;4']


def test_an_empty_array_has_length_zero():
    assert run(main('int[0] a\nprint("{@1}", Array.length(a))')) == ['0']


@pytest.mark.parametrize('body, message', [
    ('int[] a = [1]\nprint("{@1}", Array.size(a))', "Array has no method 'size' (it has length, len, toList, toCSV)"),
    ('print("{@1}", Array.length())', "Array.length needs the array first"),
    ('string s = "hi"\nprint("{@1}", Array.length(s))', "Array.length works on an array, not string"),
])
def test_wrong_uses_are_errors(body, message):
    assert message in errors_of(main(body))


@pytest.mark.parametrize('kind', ['struct', 'class', 'enum'])
def test_array_is_a_built_in_name(kind):
    decl = {'struct': 'struct Array\n    int x\n\n', 'class': 'class Array\n    public int x\n\n',
            'enum': 'enum Array\n    A\n    B\n\n'}[kind]
    assert "'Array' is a built-in type" in errors_of(decl + main('print("x")'))


# ---------- 45.2: int[] e - an empty array, size 0 (D.141) ----------

def test_an_array_with_no_size_and_no_values_is_empty():
    source = ('void function show(int[] xs)\n    print("{@1}", xs.length)\n\n'
              + main('int[] e\nstring[] names\nprint("{@1} {@2}", e.length, len(names))\nshow(e)\n'
                     'for x in e\n    print("never")\nforeach (string n in names)\n    print("never")'))
    assert run(source) == ['0 0', '0']


def test_an_index_into_an_empty_array_is_an_index_error():
    assert run(main('int[] e\ntry\n    e[0] = 1\ncatch IndexError err\n    print("index")')) == ['index']



# ---------- 45.14: fixed int[10] c - never another size (D.141) ----------

def test_a_fixed_array_works_like_any_array():
    source = ('int[3] function podium()\n    return [3, 1, 2]\n\n'
              + main('fixed int[3] a\nfixed int[] b = [5, 2, 3]\nfixed int[] c = podium()\na[0] = 7\n'
                     'b = podium()\nprint("{@1} {@2} {@3} {@4}", a[0], a.length, b[0], c.length)'))
    assert run(source) == ['7 3 3 3']


def test_a_fixed_array_of_objects():
    source = ('class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n'
              + main('fixed Car[] cars = [Car("red"), null]\ncars[1] = Car("blue")\nprint(cars[1].color)'))
    assert run(source) == ['blue']


def test_a_fixed_array_needs_its_size_or_its_values():
    assert "fixed needs its size - fixed int[3] d" in errors_of(main('fixed int[] d'))


@pytest.mark.parametrize('body, message', [
    ('fixed int x = 1', 'fixed is written on an array'),
    ('fixed(10) string s = "a"', 'fixed(n) - at most n - on a string, List or Map is planned'),
    ('fixed List<int> xs = []', 'fixed is written on an array'),
])
def test_fixed_on_anything_else_waits_for_47_5(body, message):
    with pytest.raises(ParserError, match=re.escape(message)):
        parse(main(body))


def test_a_fixed_array_cant_be_replaced_by_a_literal():
    assert "'a' is fixed - its size never changes" in errors_of(main('fixed int[] a = [1, 2]\na = [1, 2, 3]'))


def test_fixed_is_a_reserved_word():
    with pytest.raises(ParserError, match='Expected variable name'):
        parse(main('int fixed = 1'))


# ---------- int numbers[] - the C-style form, the same array (user, 2026-11-15) ----------

def test_brackets_after_the_name_declare_the_same_array():
    source = ('int function total(int values[])\n    int t = 0\n    foreach (int v in values)\n'
              '        t = t + v\n    return t\n\n'
              + main('int numbers[] = [1, 2, 3]\nint more[2]\nint none[]\nfixed int top[3] = [3, 2, 1]\n'
                     'more[1] = 5\nprint("{@1} {@2} {@3} {@4} {@5}", total(numbers), more[1], numbers.length, '
                     'none.length, top[0])'))
    assert run(source) == ['6 5 3 0 3']


def test_brackets_written_twice_are_an_error():
    with pytest.raises(ParserError, match=re.escape('Write the brackets once: int[] numbers, or int numbers[]')):
        parse(main('int[] numbers[] = [1]'))
