"""Tests for Task 32.6 - a List is a Collection<T> value (Decisions.md D.090, Arrays.md section 6).

    List<int> xs = [1, 2, 3]
    Collection<int> c = xs          // the same List - its own implementation answers
    c.add(4)                        // xs has 4 items too
    foreach n in c                  // a new Iterator<int> from c.iterator()

Each List type gets a class table only when the program uses Collection<X> for its element type.
Every program runs with the leak check. With and without null checks (Rule 4b).
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_every_collection_function_on_a_list():
    assert run(main('List<int> xs = [1, 2, 3]\n'
                    'Collection<int> c = xs\n'
                    'c.add(4)\n'
                    'print("{@1} {@2} {@3}", c.length(), c.contains(2), c.isEmpty())\n'
                    'print("{@1} {@2} {@3}", c.remove(1), c.remove(7), xs.len())\n'
                    'List<int> other = [2, 9]\n'
                    'c.keepOnly(other)\n'
                    'c.addAll(other)\n'
                    'List<int> nine = [9]\n'
                    'c.removeAll(nine)\n'
                    'print("{@1} {@2} {@3}", xs.len(), xs[0], xs[1])\n'
                    'c.clear()\n'
                    'print("{@1}", xs.len())')) == ['4 true false', 'true false 3', '2 2 2', '0']


def test_foreach_and_an_iterator_over_a_collection():
    assert run('int function total(Collection<int> c)\n'
               '    int sum = 0\n'
               '    foreach n in c\n'
               '        foreach m in c\n'
               '            sum = sum + n * m\n'
               '    return sum\n\n'
               + main('List<int> xs = [1, 2]\n'
                      'print("{@1}", total(xs))\n'
                      'Collection<int> c = xs\n'
                      'Iterator<int> it = c.iterator()\n'
                      'while it.hasNext()\n'
                      '    write("{@1} ", it.next())\n'
                      'print("")')) == ['9', '1 2']


def test_strings_and_objects_are_freed():
    source = ('class Person\n    public string name\n    constructor(string name)\n'
              '        this.name = name\n\n'
              + main('List<string> words = ["a"]\n'
                     'Collection<string> w = words\n'
                     'w.add("b")\n'
                     'foreach s in w\n'
                     '    write(s)\n'
                     'print("")\n'
                     'List<Person> people = [Person("Ann")]\n'
                     'Collection<Person> c = people\n'
                     'c.add(Person("Bob"))\n'
                     'foreach p in c\n'
                     '    write("{p.name} ")\n'
                     'print("{@1}", people.len())'))
    assert run(source) == ['ab', 'Ann Bob 2']


def test_next_past_the_end_is_null_not_an_error():
    # D.091: an error is for a genuine failure, never to end a loop - past the end: null
    source = ('class Person\n    public string name = "Ann"\n\n'
              + main('List<Person> xs = [Person()]\n'
                     'Collection<Person> c = xs\n'
                     'Iterator<Person> it = c.iterator()\n'
                     'Person a = it.next()\n'
                     'Person b = it.next()\n'
                     'print("{a.name} {b}")'))
    assert run(source) == ['Ann null']


def test_without_a_null_check_a_null_collection_is_a_null_error():
    # Rule 4b: no check - `.` on a null Collection is a NullError that catch handles
    assert run(main('Collection<int> c\n'
                    'try\n'
                    '    print("{@1}", c.length())\n'
                    'catch NullError e\n'
                    '    print("caught")')) == ['caught']


def test_with_a_null_check_the_code_runs_on():
    assert run(main('Collection<int> c\n'
                    'if c is not null\n'
                    '    print("never")\n'
                    'List<int> five = [5]\n'
                    'c = five\n'
                    'print("{@1}", c.length())')) == ['1']


def test_a_list_of_another_type_isnt_that_collection():
    assert "Collection<string>" in errors_of(main('List<int> xs = [1]\nCollection<string> c = xs'))


def test_next_past_the_end_a_string_is_null_an_int_an_index_error():
    # D.094 (user, 2026-11-01): a string, List, Map, object or enum - null (no more items),
    # whatever the nullable settings say; a primitive can't be null - an IndexError that says
    # to check hasNext() first. hasNext() is the way: foreach never fails
    assert run(main('List<string> words = ["a"]\n'
                    'Collection<string> w = words\n'
                    'Iterator<string> si = w.iterator()\n'
                    'string first = si.next()\n'
                    'string none = si.next()\n'
                    'print("{first} {none}")\n'
                    'if none is null\n'
                    '    print("no more")\n'
                    'List<int> xs = [1]\n'
                    'Collection<int> c = xs\n'
                    'Iterator<int> it = c.iterator()\n'
                    'while it.hasNext()\n'
                    '    print("{@1}", it.next())\n'
                    'try\n'
                    '    int x = it.next()\n'
                    'catch IndexError e\n'
                    '    print(e.message)')) == [
        'a null', 'no more', '1', 'next() past the end of the List - check hasNext() first']
