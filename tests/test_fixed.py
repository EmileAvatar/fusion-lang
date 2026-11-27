"""Task 47.5 - `fixed(n)`: at most n (D.020, D.064, D.202, D.203).

    fixed(10) string code               // at most 10 characters - the text may change
    fixed(14) List<Person> people       // at most 14 elements, the 14 reserved at once
    fixed(3) Map<string, int> m         // at most 3 keys
    fixed(MAX_NAME) string name         // n a whole number or a constant

Written past n: a compile error. While running: a CapacityError - the value is never cut and the old one stays.
Every program runs under the leak check.
"""
import pytest

from src.parser.parser import ParserError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main, parse


def run(body: str, top: str = '') -> list:
    code, out, err = compile_and_run(top + main(body))
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def catching(statement: str, then: str = '') -> str:
    return f'try\n    {statement}\ncatch CapacityError e\n    print("{{e}}")' + (f'\n{then}' if then else '')


# ---- strings ----

def test_a_string_within_its_size():
    assert run('fixed(10) string name = "Ada"\nname = "Ada Byron"\nprint(name)') == ['Ada Byron']


def test_a_string_past_its_size_while_running():
    assert run('fixed(10) string name = "Ada"\nstring longer = "Ada Lovelace!"\n' + catching('name = longer') +
               '\nprint(name)') == ['the text has 13 characters - it holds at most 10 (fixed(10))', 'Ada']


def test_a_string_made_by_joining():
    assert run('fixed(5) string s = "ab"\nstring t = "cdef"\n' + catching('s = s + t', 'print(s)')) == [
        'the text has 6 characters - it holds at most 5 (fixed(5))', 'ab']


def test_a_written_string_past_its_size():
    assert '"TOO-LONG-CODE" has 13 characters - this string holds at most 10 (fixed(10))' in errors_of(
        main('fixed(10) string code = "TOO-LONG-CODE"'))


def test_a_struct_field_and_a_constant_size():
    top = 'const int CODE_SIZE = 6\n\nstruct Item\n    fixed(CODE_SIZE) string code\n\n'
    assert run('Item it = Item("AB-123")\nstring other = "TOO-LONG"\n' + catching('it.code = other') +
               '\nprint(it.code)', top) == ['the text has 8 characters - it holds at most 6 (fixed(6))', 'AB-123']


def test_a_parameter():
    top = 'void function show(fixed(3) string s)\n    print(s)\n\n'
    assert run('string ok = "abc"\nstring bad = "abcd"\nshow(ok)\n' + catching('show(bad)'), top) == [
        'abc', 'the text has 4 characters - it holds at most 3 (fixed(3))']


# ---- Lists and Maps ----

def test_a_list_holds_at_most_n():
    assert run('fixed(3) List<int> xs = [1, 2]\nxs.add(3)\n' + catching('xs.add(4)') + '\nprint("{@1}", xs.len())') == [
        'the List holds at most 3 (fixed(3))', '3']


def test_a_list_declared_empty_and_insert():
    assert run('fixed(2) List<string> xs\nxs.add("a")\nxs.insert(0, "b")\n' + catching('xs.insert(0, "c")') +
               '\nprint("{@1} {@2}", xs.len(), xs[0])') == ['the List holds at most 2 (fixed(2))', '2 b']


def test_a_map_holds_at_most_n_keys():
    assert run('fixed(2) Map<string, int> m\nm["a"] = 1\nm["b"] = 2\nm["a"] = 5\n' + catching('m["c"] = 3') +
               '\nprint("{@1} {@2}", m.len(), m["a"])') == ['the Map holds at most 2 keys (fixed(2))', '2 5']


def test_a_bigger_list_stored():
    assert run('fixed(2) List<int> xs = [1]\nList<int> big = [1, 2, 3]\n' + catching('xs = big') +
               '\nprint("{@1}", xs.len())') == ['the List has 3 - it holds at most 2 (fixed(2))', '1']


def test_a_written_list_past_its_size():
    assert '3 values - this List holds at most 2 (fixed(2))' in errors_of(main('fixed(2) List<int> xs = [1, 2, 3]'))


def test_a_map_of_fixed_strings():
    assert run('Map<string, fixed(4) string> codes\ncodes["a"] = "ab"\nprint(codes["a"])') == ['ab']


# ---- the size ----

@pytest.mark.parametrize('source, message', [
    ('fixed(0) string s', 'the size is a whole number above 0'),
    ('fixed(LIMIT) string s', "'LIMIT' isn't a constant whole number"),
])
def test_bad_sizes(source, message):
    assert message in errors_of(main(source))


@pytest.mark.parametrize('source, message', [
    ('fixed(3) int x = 1', 'fixed(n) goes on a string, a List or a Map'),
    ('fixed("a") string s', 'fixed(n) takes a whole number'),
])
def test_bad_forms(source, message):
    import re
    with pytest.raises(ParserError, match=re.escape(message)):
        parse(main(source))


def test_an_array_keeps_its_own_fixed():
    assert run('fixed int[3] a = [1, 2, 3]\nprint("{@1}", a[2])') == ['3']
