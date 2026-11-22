"""Task 33.3d2 - a List<E> value holding a List of your own (D.175).

    List<int> xs = Ring()        // Ring<T> implements List<T> - T from the List's element
    xs.add(3)                    // through Ring's insert
    xs[0] = 9                    // set back through Ring's set once the statement is done
    for x in xs ...              // over a copy of it

Each List operation checks which List it is: Fusion's own goes the direct way as before; a List of your
own goes through its core five - a single read keeps what get gave a while (it is handed out borrowed),
reading many at once (foreach, ==, copyPart, map, print ...) works on a copy. Every program runs under
the leak check, in strict and relaxed ownership.
"""

import pytest

from src.config.project_config import MemoryConfig
from tests.test_end_to_end import compile_and_run

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
        'int function total(List<int> xs)\n'
        '    int sum = 0\n'
        '    for x in xs\n'
        '        sum = sum + x\n'
        '    return sum\n\n'
        'struct Point\n    int x\n    int y\n\n')


def run(body: str, ownership: str = 'move') -> list:
    source = RING + 'void function main()\n' + ''.join(f'    {line}\n' for line in body.split('\n'))
    code, out, err = compile_and_run(source, analyzer_options={'memory_config': MemoryConfig(assignment=ownership)})
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


@pytest.mark.parametrize('ownership', ['move', 'share'])
def test_list_operations_on_a_list_of_your_own(ownership):
    assert run('List<int> xs = Ring()\nxs.add(3)\nxs.add(5)\nxs.insert(0, 1)\n'
               'print("{@1} {@2} {@3} {@4}", xs[0], xs[2], xs.contains(5), xs.indexOf(5))\n'
               'xs[1] = 7\nprint("{@1}", xs[1])\nxs.removeAt(0)\nxs.sortBy(func(int a, int b) : b - a)\n'
               'print("{@1} {@2} {@3}", xs[0], len(xs), xs.len())\nxs.clear()\nprint("{@1}", xs.len())',
               ownership) == ['1 5 true 2', '7', '7 2 2', '0']


@pytest.mark.parametrize('ownership', ['move', 'share'])
def test_reading_many_at_once(ownership):
    # foreach, a List<int> parameter, ==, copyPart, toList, byVal, map, filter, +, join - over a copy
    assert run('List<int> xs = Ring()\nxs.add(3)\nxs.add(5)\nxs.add(9)\nprint("{@1}", total(xs))\n'
               'foreach (int x in xs)\n    print("{@1}", x)\nList<int> same = [3, 5, 9]\nprint("{@1}", xs == same)\n'
               'List<int> part = xs.copyPart(1, 2)\nList<int> copy = xs.toList()\nList<int> deep = byVal xs\n'
               'print("{@1} {@2} {@3}", part[0], copy.len(), deep[2])\n'
               'print("{@1} {@2}", xs.map(func(int x) : x * 2)[2], xs.filter(func(int x) : x > 4).len())\n'
               'List<int> joined = xs + same\nprint("{@1} {@2}", joined.len(), total(Ring()))\n'
               'List<string> words = Ring()\nwords.add("a")\nwords.add("b")\nprint(words.join("-"))',
               ownership) == ['17', '3', '5', '9', 'true', '5 3 9', '18 2', '6 0', 'a-b']


def test_an_element_changed_in_place_is_set_back():
    # relaxed: the Ring read straight after - the change is there (set back when the statement ends)
    assert run('Ring<int> r = Ring()\nList<int> xs = r\nxs.add(1)\nxs[0] = 9\nprint("{@1}", r.get(0))\n'
               'Ring<Point> pr = Ring()\nList<Point> ps = pr\nps.add(Point(1, 2))\nps[0].x = 5\n'
               'print("{@1} {@2}", pr.get(0).x, ps[0].y)', 'share') == ['9', '5 2']


def test_the_type_comes_from_the_list():
    # List<int> xs = Ring() - Ring<T> implements List<T>: T is int (D.171 with the List's element)
    assert run('List<string> names = Ring()\nnames.add("Ada")\nprint(names[0])') == ['Ada']


LOOPS = ('int function divide(int x) : 10 / x\n\n'
         'void function grow(List<int> v)\n    v.add(5)\n\n'
         'int function firstBig()\n    List<int> xs = Ring()\n    xs.add(3)\n    xs.add(9)\n'
         '    for x in xs\n        if x > 5\n            return x\n    return 0\n\n')


@pytest.mark.parametrize('body, lines', [
    ('List<int> xs = Ring()\nxs.add(1)\nxs.add(0)\ntry\n    for x in xs\n        print("{@1}", divide(x))\n'
     'catch e\n    print("caught")', ['10', 'caught']),                    # an error leaving the loop
    ('List<string> xs = Ring()\nxs.add("a")\ntry\n    for x in xs\n        throw Error("stop {x}")\n'
     'catch e\n    print("caught")', ['caught']),                          # a throw
    ('print("{@1}", firstBig())', ['9']),                                   # a return inside
    ('List<int> xs = Ring()\nxs.add(1)\nxs.add(2)\nfor x in xs\n    break\nprint("done")', ['done']),
])
def test_every_way_out_of_a_loop_frees_its_copy(body, lines):
    # the loop walks a copy of a List of your own - freed however the loop ends (the leak check)
    source = RING + LOOPS + 'void function main()\n' + ''.join(f'    {line}\n' for line in body.split('\n'))
    code, out, err = compile_and_run(source, analyzer_options={'memory_config': MemoryConfig(assignment='share')})
    assert code == 0, out + err
    assert out.strip().splitlines() == lines


def test_changing_it_while_looping_is_an_error():
    # 27.2e: never a skip - the List given is watched, not the copy walked (relaxed: strict stops it compiling)
    source = RING + LOOPS + 'void function main()\n' + ''.join(f'    {line}\n' for line in (
        'List<int> xs = Ring()\nxs.add(1)\ntry\n    for x in xs\n        grow(xs)\ncatch e\n    print("{e.kind}")'
    ).split('\n'))
    code, out, err = compile_and_run(source, analyzer_options={'memory_config': MemoryConfig(assignment='share')})
    assert code == 0, out + err
    assert out.strip() == 'ModifiedWhileLoopingError'
