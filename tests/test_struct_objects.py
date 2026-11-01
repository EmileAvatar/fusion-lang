"""Tests for a struct holding an object (user, 2026-11-01 - Decisions.md D.097).

    struct Record
        int id
        string name,
        Person person          // null until set; shared when the struct is copied
        List<int> scores       // never null - empty; copied with the struct

Every program runs with the leak check. With and without null checks (Rule 4b).
"""

from tests.test_end_to_end import compile_and_run
from tests.test_structs import main

PEOPLE = ('class Person\n    public string name\n    constructor(string name)\n'
          '        this.name = name\n\n'
          'struct Record\n    int id\n    string name,\n    Person person\n    List<int> scores\n\n'
          'struct Tag { int n, Person who }\n\n')


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_a_copy_shares_the_object_and_copies_the_list():
    assert run(PEOPLE + main('Record a = Record(1, "first", Person("Ann"), [1])\n'
                             'Record b = a\n'
                             'b.person.name = "Changed"\n'
                             'b.scores.add(2)\n'
                             'print("{a.person.name} {@1} {@2}", a.scores.len(), b.scores.len())')) == [
        'Changed 1 2']


def test_a_struct_prints_its_object():
    assert run(PEOPLE + main('Tag t = Tag(7, Person("Bo"))\nprint("{t}")')) == ['n : 7,who : Person']


def test_without_a_null_check_an_unset_object_is_a_null_error():
    # Rule 4b: no check - the object field is null until set; `.` on it is a NullError
    assert run(PEOPLE + main('Record r\n'
                             'try\n'
                             '    print(r.person.name)\n'
                             'catch NullError e\n'
                             '    print("caught")')) == ['caught']


def test_with_a_null_check_the_code_runs_on():
    assert run(PEOPLE + main('Record r\n'
                             'if r.person is null\n'
                             '    r.person = Person("Cy")\n'
                             'print("{r.person.name} {@1}", r.scores.len())')) == ['Cy 0']
