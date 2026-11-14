"""Task 52.8 / 52.13 - the null guard: `c?.name`, `c?.f()`, `a ?? b` (files/Nullable_Values.md 3).

Each row of the design table (Nullable_Values.md "x?.getAge()" table) on a null and a set object;
every program runs under the leak check. With and without a null check (Rule 4b): `?.` is the check.
"""
import pytest

from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main, warnings_of

PERSON = ('class Person\n'
          '    public string name\n'
          '    public int age\n'
          '    public Person spouse\n'
          '    constructor(string n, int a)\n'
          '        this.name = n\n'
          '        this.age = a\n'
          '    void function greet()\n'
          '        print("hi {name}")\n\n')
SETUP = 'Person x = null\nPerson y = Person("Ann", 30)\n'


def out(body: str) -> list:
    return run(PERSON + main(SETUP + body))


def test_a_guarded_call_is_skipped_on_null():
    assert out('x?.greet()\ny?.greet()') == ['hi Ann']


def test_a_default_with_double_question_mark():
    assert out('int a = x?.age ?? -1\nint b = y?.age ?? -1\nprint("{@1} {@2}", a, b)') == ['-1 30']


def test_in_a_condition_a_guarded_test_is_false_on_null():
    assert out('if x?.age >= 18\n    print("x adult")\nif y?.age >= 18\n    print("y adult")') == ['y adult']


def test_not_around_a_guarded_test_is_true_on_null():
    assert out('if !(x?.age >= 18)\n    print("ask x for ID")') == ['ask x for ID']


def test_a_chain_checks_every_link():
    assert out('y.spouse = Person("Bob", 31)\nstring s = y?.spouse?.name ?? "none"\n'
               'string t = x?.spouse?.name ?? "none"\nprint("{s} {t}")') == ['Bob none']


def test_double_question_mark_on_an_object():
    assert out('Person z = x ?? Person("New", 1)\nprint(z.name)') == ['New']


def test_without_a_guard_a_null_is_a_null_error():
    # Rule 4b: no check - plain '.' on null is a NullError, caught
    assert out('try\n    x.greet()\ncatch e\n    print("caught")') == ['caught']


@pytest.mark.parametrize('body, message', [
    ('int a = x?.age', "'?.age' may be missing - give a default with ??"),
    ('print(x?.name)', "'?.name' may be missing"),
])
def test_a_guarded_value_without_a_default_is_an_error(body, message):
    assert message in errors_of(PERSON + main(SETUP + body))


def test_a_guard_after_a_call_is_an_error():
    source = PERSON + 'Person function find()\n    return null\n\n' + main('int a = find()?.age ?? 0')
    assert "'?.' after a call: store the result in a variable first" in errors_of(source)


def test_a_guard_on_a_string_or_list_warns():
    # 52.13: never null (D.138) - the guard does nothing
    w = warnings_of(main('string s = "hi"\nint n = s?.len() ?? 0\nList<int> xs = [1]\nint m = xs?.len() ?? 0\n'
                         'print("{@1} {@2}", n, m)'))
    assert "A string is never null - '?.' / '??' does nothing here (D.138)" in w
    assert "List<int> is never null" in w
