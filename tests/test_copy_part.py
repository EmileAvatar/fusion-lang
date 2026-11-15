"""Task 45.5 - copying a part (D.046, files/Arrays.md 8): `copyPart(start, count)` / `copyPartAt(start,
end)`, with `slice` / `sliceAt` as quick typing - on every array and on Lists.

Positions from 0; a count or end past the end stops there; a start outside is an IndexError;
copyPartAt includes its end, and a start after the end gives the items reversed. The original is
unchanged. An array gives a new array (on the heap), a List a new List. Items are copied as `+`
copies them: a string copied, an object shared. Every program runs under the leak check.
"""
import pytest

from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main

CAR = ('class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n')
SHOW = 'void function show(int[] xs)\n    foreach (int x in xs)\n        write("{x} ")\n    print("|")\n\n'
MAKE = 'int[] function make(int n)\n    if n > 2\n        return [1, 2, 3]\n    return [9]\n\n'


# The table in files/Arrays.md 8, on int[] someArray = [20, 30]
@pytest.mark.parametrize('call, expected', [
    ('sliceAt(0, 1)', '20 30 |'),
    ('sliceAt(0, 2)', '20 30 |'),            # stops at the end
    ('sliceAt(1, 2)', '30 |'),
    ('sliceAt(1, 0)', '30 20 |'),            # start after end: reversed
    ('sliceAt(1, 1)', '30 |'),
    ('copyPartAt(0, 1)', '20 30 |'),
    ('copyPart(0, 1)', '20 |'),
    ('copyPart(1, 5)', '30 |'),              # a count past the end stops there
    ('copyPart(0, 0)', '|'),
    ('slice(0, 2)', '20 30 |'),
])
def test_the_table(call, expected):
    out = run(SHOW + main(f'int[] someArray = [20, 30]\nshow(someArray.{call})\nprint("{{@1}}", someArray.length)'))
    assert out == [expected, '2']


@pytest.mark.parametrize('call, message', [
    ('sliceAt(2, 3)', 'copyPartAt: start 2 is outside the array (length 2)'),
    ('copyPart(-1, 1)', 'copyPart: start -1 is outside the array (length 2)'),
    ('copyPart(0, -1)', 'copyPart: count -1 is below 0'),
    ('copyPartAt(1, -1)', 'copyPartAt: end -1 is below 0'),
])
def test_outside_is_an_index_error(call, message):
    out = run(SHOW + main(f'int[] someArray = [20, 30]\ntry\n    show(someArray.{call})\ncatch IndexError e\n'
                          '    print("{e}")'))
    assert out == [message]


def test_an_empty_one_has_no_start():
    out = run(main('int[] e\ntry\n    int[] p = e.copyPart(0, 1)\ncatch IndexError e2\n    print("{e2}")'))
    assert out == ['copyPart: start 0 is outside the array (length 0)']


def test_every_array_form():
    out = run(SHOW + MAKE + main(
        'int[5] five = [1, 2, 3, 4, 5]\nint[] p = five.copyPart(1, 3)\nshow(p)\n'
        'int[] h = [7, 8, 9]\nh = h.copyPartAt(2, 0)\nshow(h)\n'
        'int:[] g = [4, 5, 6]\nshow(g.copyPart(1, 9))\n'
        'show(make(3).copyPart(1, 5))\nshow(Array.copyPart(five, 0, 2))\n'
        'print("{@1}", five.copyPart(0, 2).length)'))
    assert out == ['2 3 4 |', '9 8 7 |', '5 6 |', '2 3 |', '1 2 |', '2']


def test_a_growable_array_from_a_part():
    out = run(SHOW + main('int[5] five = [1, 2, 3, 4, 5]\nint:[] g = five.copyPartAt(4, 2)\ng.add(0)\nshow(g)'))
    assert out == ['5 4 3 0 |']


def test_lists():
    out = run(main('List<string> names = ["a", "b", "c"]\nList<string> two = names.copyPart(1, 9)\n'
                   'print("{@1} {@2}", two.len(), two[1])\nprint("{@1}", names.sliceAt(2, 0).len())\n'
                   'names[1] = "z"\nprint("{@1} {@2}", two[0], names.len())'))
    assert out == ['2 c', '3', 'b 3']


def test_strings_are_copied():
    out = run(main('string[] s = ["x", "y", "z"]\nstring[] t = s.copyPart(1, 2)\ns[1] = "q"\n'
                   'print("{@1}{@2}", t[0], t[1])'))
    assert out == ['yz']


def test_objects_are_shared():
    out = run(CAR + main('Car[] cars = [Car("red"), Car("blue")]\nCar[] last = cars.copyPart(1, 1)\n'
                         'last[0].color = "green"\nprint(cars[1].color)'))
    assert out == ['green']


def test_a_null_slot_is_copied():
    # Rule 4b: without a check a NullError; with ?. the code runs on
    body = ('Car:[] cars\ncars.add(Car("red"))\ncars.add(null)\nCar[] part = cars.copyPart(1, 1)\n'
            'print(part[0]?.color ?? "none")\ntry\n    print(part[0].color)\ncatch NullError e\n    print("null")')
    assert run(CAR + main(body)) == ['none', 'null']


@pytest.mark.parametrize('body, message', [
    ('int[] a = [1]\nint[] p = a.copyPart(0)', 'copyPart takes two values: start, count'),
    ('int[] a = [1]\nint[] p = a.sliceAt(0)', 'sliceAt takes two values: start, end'),
    ('int[] a = [1]\nint[] p = a.copyPart(0, "x")', 'a position is an int'),
    ('List<int> l = [1]\nint[] p = l.copyPart(0, 1)', 'int[]'),
])
def test_wrong_uses_are_errors(body, message):
    assert message in errors_of(main(body))


def test_fixed_from_a_part_keeps_its_size():
    assert 'fixed' in errors_of(main('int[] a = [1, 2]\nfixed int[] f = a.copyPart(0, 1)\nf = [1, 2, 3]'))
