"""Tests for Task 32.6 - a Map is a Collection<Entry<K, V>>; keys() / values() are borrowed views
(Decisions.md D.092, D.095, D.096; files/Arrays.md section 5).

    foreach k in ages                          // the keys, as before
    foreach (Entry<string, int> e in ages)     // each key and value
    Collection<Entry<string, int>> c = ages    // the same Map
    ages.keys(), ages.values()                 // borrowed: they look into the Map - no copy
    ages.keys().toList()                       // a copy, as a List

Every program runs with the leak check. With and without null checks (Rule 4b).
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main

AGES = 'Map<string, int> ages\nages["ann"] = 30\nages["bob"] = 40\n'


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_foreach_gives_keys_or_entries_when_typed():
    assert run(main(AGES + 'foreach k in ages\n'
                           '    write("{k} ")\n'
                           'print("")\n'
                           'foreach (Entry<string, int> e in ages)\n'
                           '    print("{e.key}={@1}", e.value)')) == ['ann bob ', 'ann=30', 'bob=40']


def test_a_map_as_a_collection_of_entries():
    assert run(main(AGES + 'Collection<Entry<string, int>> c = byRef ages\n'
                           'c.add(Entry<string, int>("cy", 50))\n'
                           'print("{@1} {@2} {@3}", c.length(), c.contains(Entry<string, int>("ann", 30)), '
                           'c.contains(Entry<string, int>("ann", 31)))\n'
                           'print("{@1} {@2}", c.remove(Entry<string, int>("bob", 40)), c.length())\n'
                           'c.clear()\n'
                           'print("{@1}", c.isEmpty())')) == ['3 true false', 'true 2', 'true']


@pytest.mark.share
def test_keys_and_values_are_borrowed_views_to_list_a_copy():
    assert run(main(AGES + 'Collection<string> ks = ages.keys()\n'
                           'List<string> copy = ages.keys().toList()\n'
                           'ages["cy"] = 50\n'                      # the view sees it, the copy doesn't
                           'print("{@1} {@2}", ks.length(), copy.len())\n'
                           'print("{@1} {@2}", ages.values().contains(50), ks.add("x"))\n'
                           'ks.remove("ann")\n'                     # removing a key removes its entry
                           'print("{@1}", ages.len())')) == ['3 2', 'true false', '2']


def test_a_map_of_objects_is_freed():
    source = ('class Person\n    public string name\n    constructor(string name)\n'
              '        this.name = name\n\n'
              + main('Map<string, Person> people\n'
                     'people["a"] = Person("Ann")\n'
                     'foreach (Entry<string, Person> e in people)\n'
                     '    print("{e.key} {@1}", e.value.name)\n'
                     'foreach p in people.values()\n'
                     '    print(p.name)'))
    assert run(source) == ['a Ann', 'Ann']


def test_without_a_null_check_a_null_collection_is_a_null_error():
    # Rule 4b: no check - `.` on a null Collection is a NullError that catch handles
    assert run(main('Collection<Entry<string, int>> c\n'
                    'try\n'
                    '    print("{@1}", c.length())\n'
                    'catch NullError e\n'
                    '    print("caught")\n'
                    'Map<string, int> m')) == ['caught']


def test_with_a_null_check_the_code_runs_on():
    assert run(main('Map<string, int> m\n'
                    'Collection<Entry<string, int>> c\n'
                    'if c is null\n'
                    '    c = m\n'
                    'print("{@1}", c.length())')) == ['0']


def test_entry_needs_two_types():
    from src.parser.parser import ParserError
    import pytest
    from tests.test_structs import parse
    with pytest.raises(ParserError, match="Entry has two types"):
        parse(main('Entry<string> e'))
