"""Task 45.10 - an array as a Collection<T> value (D.090: an array's own implementation blocks remove).

    int[3] a = [1, 2, 3]
    Collection<int> c = a        // a copy of its values - a stack array can't outlive its function
    int:[] g = [5, 6]
    Collection<int> gc = byRef g // the growable array itself, shared as a List is

Reading works on both (iterator, length, isEmpty, contains, foreach); remove, removeAll, keepOnly and clear are a
ReadOnlyError on both; add / addAll grow a growable array and are a ReadOnlyError on a plain or fixed array's copy.
Every program runs under the leak check, in strict and relaxed ownership.
"""

import pytest

from src.config.project_config import MemoryConfig
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main

TOTAL = ('int function total(Collection<int> c)\n    int sum = 0\n    foreach n in c\n        sum = sum + n\n'
         '    return sum\n\n')


def run(source: str, ownership: str = 'move') -> list:
    code, out, err = compile_and_run(source, analyzer_options={'memory_config': MemoryConfig(assignment=ownership)})
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


@pytest.mark.parametrize('ownership', ['move', 'share'])
@pytest.mark.parametrize('declared', ['int[3] a = [1, 2, 3]', 'fixed int[3] a = [1, 2, 3]'])
def test_a_plain_or_fixed_array_as_a_collection(declared, ownership):
    assert run(TOTAL + main(f'{declared}\nprint("{{@1}}", total(a))\nCollection<int> c = a\n'
                            'print("{@1} {@2} {@3}", c.length(), c.contains(2), c.isEmpty())\n'
                            'Iterator<int> it = c.iterator()\nwhile it.hasNext()\n    write("{@1} ", it.next())\nprint("")\n'
                            'try\n    c.add(4)\ncatch ReadOnlyError e\n    print(e.message)\n'
                            'try\n    c.remove(1)\ncatch ReadOnlyError e\n    print(e.message)'), ownership) == [
        '6', '3 true false', '1 2 3 ',
        "an array keeps its size - add isn't possible on an array (D.090)",
        "an array keeps its items - remove isn't possible on an array (D.090)"]


@pytest.mark.parametrize('ownership', ['move', 'share'])
def test_a_growable_array_as_a_collection(ownership):
    # the array itself: adding grows it; removing is refused (D.090)
    assert run(TOTAL + main('int:[] g = [5, 6]\nCollection<int> gc = byRef g\ngc.add(7)\n'
                            'print("{@1} {@2}", g.len(), total(g))\n'
                            'try\n    gc.clear()\ncatch ReadOnlyError e\n    print(e.message)\n'
                            'try\n    gc.keepOnly(gc)\ncatch ReadOnlyError e\n    print(e.message)'), ownership) == [
        '3 18', "an array keeps its items - clear isn't possible on an array (D.090)",
        "an array keeps its items - keepOnly isn't possible on an array (D.090)"]


def test_strings_and_objects_in_the_copy():
    # strings copied, objects shared - a change through the Collection's object is the array's object
    source = ('class Car\n    public string name\n    constructor(string name)\n        this.name = name\n\n'
              + main('string[2] words = ["a", "b"]\nCollection<string> ws = words\nforeach w in ws\n    write(w)\n'
                     'print("")\nCar[2] cars = [Car("x"), Car("y")]\nCollection<Car> c = cars\nforeach car in c\n'
                     '    car.name = car.name + "!"\nprint(cars[0].name)'))
    assert run(source) == ['ab', 'x!']


@pytest.mark.parametrize('body, message', [
    ('int[2][3] m\nCollection<int> c = m', 'An array of many dimensions as a Collection<int> comes later - give its toList()'),
    ('int[2] m = [1, 2]\nCollection<string> c = m', 'Cannot assign int[2] to variable of type Collection<string>'),
])
def test_array_collection_mistakes(body, message):
    assert message in errors_of(main(body))
