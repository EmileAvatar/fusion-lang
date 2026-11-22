"""Task 33.3d1 - a List of your own (D.174): `class Ring<T> implements List<T>`.

    class Ring<T> implements List<T>
        int function len() ...             // the core five, written by the class
        T function get(int i) ...
        void function set(int i, T value) ...
        void function insert(int i, T value) ...
        void function removeAt(int i) ...

Fusion adds every other List method the class doesn't write (add, contains, indexOf, remove, clear,
toList, copyPart / copyPartAt / slice / sliceAt, filter, sortBy), written in Fusion from the core five.
Every program runs under the leak check, in strict and relaxed ownership.
"""

import pytest

from src.config.project_config import MemoryConfig
from src.parser.parser import ParserError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import parse

RING = ('class Ring<T> implements List<T>\n'
        '    List<T> items\n'
        '    int function len() : items.len()\n'
        '    T function get(int i) : items[i]\n'
        '    void function set(int i, T value)\n'
        '        items[i] = value\n'
        '    void function insert(int i, T value)\n'
        '        items.insert(i, value)\n'
        '    void function removeAt(int i)\n'
        '        items.removeAt(i)\n\n'
        'class Car\n'
        '    public string name\n'
        '    constructor(string name)\n'
        '        this.name = name\n\n')


def run(body: str, top: str = RING, ownership: str = 'move') -> list:
    source = top + 'void function main()\n' + ''.join(f'    {line}\n' for line in body.split('\n'))
    code, out, err = compile_and_run(source, analyzer_options={'memory_config': MemoryConfig(assignment=ownership)})
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


@pytest.mark.parametrize('ownership', ['move', 'share'])
def test_the_methods_fusion_adds(ownership):
    assert run('Ring<int> r = Ring()\nr.add(5)\nr.add(3)\nr.add(9)\nr.insert(0, 1)\n'
               'print("{@1} {@2} {@3} {@4}", r.len(), r.get(0), r.contains(9), r.contains(4))\n'
               'print("{@1} {@2}", r.indexOf(3), r.indexOf(7))\n'
               'print("{@1} {@2}", r.remove(3), r.remove(3))\n'
               'r.sortBy(func(int a, int b) : b - a)\n'
               'List<int> all = r.toList()\nprint("{@1} {@2} {@3}", all[0], all[1], all[2])\n'
               'print("{@1}", r.filter(func(int x) : x > 4).len())\n'
               'List<int> part = r.copyPart(1, 5)\nList<int> back = r.sliceAt(2, 0)\n'
               'print("{@1} {@2} {@3} {@4}", part.len(), part[0], back[0], back[2])\n'
               'r.clear()\nprint("{@1}", r.len())', ownership=ownership) == [
        '4 1 true false', '2 -1', 'true false', '9 5 1', '2', '2 5 1 9', '0']


@pytest.mark.parametrize('ownership', ['move', 'share'])
def test_a_list_of_objects_of_your_own(ownership):
    assert run('Ring<Car> r = Ring()\nr.add(Car("van"))\nr.add(Car("mini"))\n'
               'r.sortBy(func(Car a, Car b) : a.name.len() - b.name.len())\nprint(r.get(0).name)\n'
               'List<Car> all = r.toList()\n'
               'print("{@1} {@2}", all.len(), r.filter(func(Car c) : c.name == "van").len())\n'
               'r.removeAt(0)\nprint("{@1}", r.len())', ownership=ownership) == ['van', '2 1', '1']


def test_a_class_writes_its_own_instead():
    # one the class writes stays its own - not replaced by Fusion's
    top = RING.replace('    void function removeAt(int i)\n',
                       '    bool function contains(T value) : false\n    void function removeAt(int i)\n')
    assert run('Ring<int> r = Ring()\nr.add(5)\nprint("{@1}", r.contains(5))', top=top) == ['false']


def test_a_plain_class_on_list_of_int():
    top = ('class Counts implements List<int>\n    List<int> items\n    int function len() : items.len()\n'
           '    int function get(int i) : items[i]\n    void function set(int i, int value)\n        items[i] = value\n'
           '    void function insert(int i, int value)\n        items.insert(i, value)\n'
           '    void function removeAt(int i)\n        items.removeAt(i)\n\n')
    assert run('Counts c = Counts()\nc.add(2)\nc.add(4)\nprint("{@1} {@2}", c.len(), c.indexOf(4))', top=top) == ['2 1']


def test_a_part_starting_outside_is_an_index_error():
    code, out, err = compile_and_run(RING + 'void function main()\n    Ring<int> r = Ring()\n    r.add(1)\n'
                                     '    print("{@1}", r.copyPart(5, 1).len())\n')
    assert code != 0 and 'copyPart: start 5 is outside 0...1' in out + err


@pytest.mark.parametrize('top, message', [
    ('class R implements List<int>\n    int function len() : 0\n\n',
     "Class 'R' implements List<int> but has no get, set, insert, removeAt - a List of your own writes len(), "
     "get(int i), set(int i, int value), insert(int i, int value), removeAt(int i) (D.174)"),
    ('class R implements List<int>\n    int function len() : 0\n    int function get() : 0\n'
     '    void function set(int i, int v)\n        print("x")\n    void function insert(int i, int v)\n'
     '        print("x")\n    void function removeAt(int i)\n        print("x")\n\n',
     "Class 'R' implements List<int> but writes get with other parameters"),
])
def test_the_core_five_are_needed(top, message):
    with pytest.raises(ParserError, match=message.replace('(', r'\(').replace(')', r'\)')):
        parse(top + 'void function main()\n    print("x")\n')
