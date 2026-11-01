"""Tests for Task 32.4 - foreach, Iterator<T>, Collection<T> (Arrays.md section 6, Decisions.md
D.049, D.058, D.085, D.089).

    foreach (string n in names)          // or: foreach n in names
    class Team implements Collection<Person>
        Iterator<Person> function iterator()      // a new one for each loop
    class TeamIterator implements Iterator<Person>
        bool function hasNext()
        Person function next()

The collection being looped over isn't changed inside the loop - Fusion's own never, a class of
your own only with [collections] allowChangeWhileLooping. Every program runs with the leak
check. With and without null checks (Rule 4b).
"""

import pytest

from src.config.project_config import CollectionsConfig
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main

TEAM = ('class Person\n'
        '    public string name\n'
        '    constructor(string name)\n'
        '        this.name = name\n\n'
        'class TeamIterator implements Iterator<Person>\n'
        '    List<Person> people\n'
        '    int at = 0\n'
        '    constructor(List<Person> people)\n'
        '        this.people = people\n'
        '    bool function hasNext() : at < people.len()\n'
        '    Person function next()\n'
        '        at = at + 1\n'
        '        return people[at - 1]\n\n'
        'class Team implements Collection<Person>\n'
        '    List<Person> people\n'
        '    Iterator<Person> function iterator() : TeamIterator(people)\n'
        '    bool function add(Person p)\n'
        '        people.add(p)\n'
        '        return true\n'
        '    bool function remove(Person p) : false\n'
        '    int function length() : people.len()\n'
        '    bool function isEmpty() : people.len() == 0\n'
        '    bool function contains(Person p) : false\n'
        '    bool function addAll(Collection<Person> items) : false\n'
        '    bool function removeAll(Collection<Person> items) : false\n'
        '    bool function keepOnly(Collection<Person> items) : false\n'
        '    void function clear()\n'
        '        people.clear()\n\n')
FILLED = 'Team t = Team()\nt.add(Person("Ann"))\nt.add(Person("Bob"))\n'


def run(source: str, **options) -> list:
    code, out, err = compile_and_run(source, analyzer_options=options or None)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_foreach_over_arrays_lists_and_maps():
    assert run(main('int[3] a = [1, 2, 3]\n'
                    'foreach (int x in a)\n'
                    '    write("{x} ")\n'
                    'List<string> names = ["x", "y"]\n'
                    'foreach n in names\n'
                    '    write(n)\n'
                    'Map<string, int> m\n'
                    'm["k"] = 1\n'
                    'foreach (string key in m)\n'
                    '    print(" {key}")')) == ['1 2 3 xy k']


def test_foreach_over_a_class_of_your_own_and_a_loop_inside_it():
    # each loop asks for a new iterator, so a loop inside a loop over the same team works
    assert run(TEAM + main(FILLED + 'foreach (Person p in t)\n'
                                    '    foreach q in t\n'
                                    '        print("{p.name} {q.name}")')) == [
        'Ann Ann', 'Ann Bob', 'Bob Ann', 'Bob Bob']


def test_break_and_continue_and_return():
    assert run(TEAM + 'string function first(Team t)\n'
                      '    foreach p in t\n'
                      '        return p.name\n'
                      '    return ""\n\n'
               + main(FILLED + 'foreach p in t\n'
                               '    if p.name == "Ann"\n'
                               '        continue\n'
                               '    print(p.name)\n'
                               '    break\n'
                               'print(first(t))')) == ['Bob', 'Ann']


def test_without_a_null_check_a_null_collection_is_a_null_error():
    # Rule 4b: no check - looping over a null collection object is a NullError
    assert run(TEAM + main('Team t\n'
                           'try\n'
                           '    foreach p in t\n'
                           '        print(p.name)\n'
                           'catch NullError e\n'
                           '    print("caught")')) == ['caught']


def test_with_a_null_check_the_code_runs_on():
    assert run(TEAM + main('Team t\n'
                           'if t is not null\n'
                           '    foreach p in t\n'
                           '        print(p.name)\n'
                           'print("done")')) == ['done']


def test_changing_your_own_collection_while_looping():
    body = FILLED + 'foreach p in t\n    t.clear()\nprint("{@1}", t.length())'
    assert "'t' is being looped over - it can't change inside the loop (clear)" in \
        errors_of(TEAM + main(body))
    on = {'collections_config': CollectionsConfig(allow_change_while_looping=True)}
    assert run(TEAM + main(body), **on) == ['0']


@pytest.mark.parametrize('source, message', [
    ('class Bad implements Collection<int>\n    int n\n\n',
     "Class 'Bad' implements Collection<int> but has no function 'iterator' - Iterator<int> function iterator()"),
    ('class Bad implements Iterator<int>\n    bool function hasNext() : false\n\n',
     "Class 'Bad' implements Iterator<int> but has no function 'next' - int function next()"),
    ('interface Iterator\n    int function n()\n\n', "'Iterator' is Fusion's own interface"),
])
def test_what_a_collection_must_give(source, message):
    assert message in errors_of(source + main('print("x")'))


def test_a_class_without_collection_cant_be_looped():
    assert "a class implementing Collection<T>, got Person" in errors_of(
        TEAM + main('Person p = Person("A")\nforeach x in p\n    print("x")'))
