"""Tests for Task 32.14 - List / Map options set in the variable's set-up block (files/Arrays.md
section 4, Decisions.md D.086).

    List<string> names = [] {
        names.noDuplicates()       // adding a value it has: a DuplicateError
        names.noNull()             // adding null: a NullError
        names.readOnly()           // after the block: a change is a ReadOnlyError
    }

A compile error wherever it can be seen, else an error while running (D.086). Every program
runs with the leak check - a refused value is freed. With and without null checks (Rule 4b).
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main

GROW = 'void function grow(List<string> v, string s)\n    v.add(s)\n\n'


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_read_only_after_its_set_up():
    assert run(GROW + main('List<string> names = ["a"] {\n'
                           '    names.readOnly()\n'
                           '    names.add("b")\n'              # still its set-up: fine
                           '}\n'
                           'try\n'
                           '    grow(names, "c")\n'
                           'catch ReadOnlyError e\n'
                           '    print(e.message)\n'
                           'print("{@1}", names.len())')) == ['the List is read only', '2']


def test_no_duplicates():
    assert run(GROW + main('List<string> tags = [] {\n'
                           '    tags.noDuplicates()\n'
                           '}\n'
                           'tags.add("x")\n'
                           'try\n'
                           '    grow(tags, "x")\n'
                           'catch DuplicateError e\n'
                           '    print(e.message)\n'
                           'print("{@1}", tags.len())')) == ['the List has it already (noDuplicates)', '1']


PEOPLE = 'class Person\n    public string name = "Ann"\n\n'


def test_without_a_null_check_no_null_refuses_one():
    # Rule 4b: no check - a null added to a noNull List is a NullError that catch handles
    assert run(PEOPLE + 'void function put(List<Person> v, Person p)\n    v.add(p)\n\n'
               + main('List<Person> people = [] {\n'
                      '    people.noNull()\n'
                      '}\n'
                      'Person nobody\n'
                      'try\n'
                      '    put(people, nobody)\n'
                      'catch NullError e\n'
                      '    print(e.message)')) == ['a List never holds null (D.139)']


def test_with_a_null_check_the_code_runs_on():
    assert run(PEOPLE + main('List<Person> people = [] {\n'
                             '    people.noNull()\n'
                             '}\n'
                             'Person nobody\n'
                             'if nobody is not null\n'
                             '    people.add(nobody)\n'
                             'people.add(Person())\n'
                             'print("{@1}", people.len())')) == ['1']


def test_a_maps_options():
    assert run(main('Map<string, int> codes = Map<string, int>() {\n'
                    '    codes["a"] = 1\n'
                    '    codes.readOnly()\n'
                    '}\n'
                    'print("{@1}", codes["a"])')) == ['1']


@pytest.mark.parametrize('body, message', [
    ('List<string> xs = [] {\n    xs.readOnly()\n}\nxs.add("a")',
     "'xs' is read only after its set-up - it can't change (add)"),
    ('List<string> xs = ["a"] {\n    xs.readOnly()\n}\nxs[0] = "b"', "'xs' is read only after its set-up"),
    ('List<string> xs = ["a"]\nxs.readOnly()', "'readOnly()' is set in the List's / Map's own set-up block"),
    ('Map<string, int> m = Map<string, int>() {\n    m.noDuplicates()\n}', "A Map's keys never repeat already"),
    ('Map<string, int> m = Map<string, int>() {\n    m.readOnly()\n}\nm.clear()', "'m' is read only after its set-up"),
])
def test_option_errors(body, message):
    assert message in errors_of(main(body))
