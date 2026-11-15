"""Task 45.3 - a growable array: `int:[]` or `int[[]]` (D.141) grows and shrinks at its end.

`add(x)` at the end, `removeLast()` (`pop()` the same) - an empty one is an IndexError; nothing in
the middle (a List does that). On the heap, like a replaced array (45.10); an object slot may be null
(D.140). Every program runs under the leak check.
"""
import re

import pytest

from src.parser.parser import ParserError
from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main, parse

CAR = ('class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n')
TOTAL = ('int function total(int[] values)\n    int t = 0\n    foreach (int v in values)\n'
         '        t = t + v\n    return t\n\n')


@pytest.mark.parametrize('declaration', ['int:[] numbers', 'int[[]] numbers', 'int numbers[[]]'])
def test_add_and_remove_at_the_end(declaration):
    out = run(main(f'{declaration}\nnumbers.add(4)\nnumbers.add(6)\nnumbers.add(8)\nnumbers.removeLast()\n'
                   'numbers.pop()\nnumbers.add(5)\nprint("{@1} {@2} {@3}", numbers.length, numbers[0], numbers[1])'))
    assert out == ['2 4 5']


def test_starting_with_values_and_passed_to_an_array_parameter():
    out = run(TOTAL + main('int:[] xs = [1, 2]\nxs.add(3)\nprint("{@1} {@2}", total(xs), Array.length(xs))'))
    assert out == ['6 3']


def test_strings_are_freed():
    out = run(main('string:[] names\nnames.add("Ann")\nnames.add("Bob")\nnames.removeLast()\nnames.add("Cy")\n'
                   'foreach (string n in names)\n    print(n)'))
    assert out == ['Ann', 'Cy']


def test_remove_last_on_an_empty_array_is_an_index_error():
    out = run(main('int:[] xs\ntry\n    xs.removeLast()\ncatch IndexError e\n    print("{e}")'))
    assert out == ['removeLast on an empty array']


def test_an_object_slot_may_be_null():
    out = run(CAR + main('Car:[] cars\ncars.add(Car("red"))\ncars.add(null)\nprint("{@1}", cars.length)\n'
                         'foreach (Car c in cars)\n    if c is not null\n        print(c.color)'))
    assert out == ['2', 'red']


def test_a_null_slot_without_a_check_is_a_null_error():
    out = run(CAR + main('Car:[] cars\ncars.add(null)\ntry\n    print(cars[0].color)\ncatch NullError e\n'
                         '    print("null")'))
    assert out == ['null']


def test_remove_last_gives_the_item_back():
    out = run(main('int:[] xs = [3, 7]\nint last = xs.pop()\nint first = xs.removeLast()\n'
                   'print("{@1} {@2} {@3}", last, first, xs.length)'))
    assert out == ['7 3 0']


def test_arguments_run_left_to_right():
    # spec 181: each argument once, left to right - the length is read after the pops before it
    out = run(main('int:[] xs = [3, 7]\nprint("{@1} {@2} {@3}", xs.pop(), xs.removeLast(), xs.length)\n'
                   'xs.add(1)\nprint("{@1} {@2}", xs.length, xs.pop())'))
    assert out == ['7 3 0', '1 1']


def test_a_removed_string_is_owned_by_the_caller():
    out = run(main('string:[] names = ["Ann", "Bob", "Cy"]\nstring s = names.pop()\nprint(s)\n'
                   'print(names.removeLast() + "!")\nnames.pop()\nprint("{@1}", names.length)'))
    assert out == ['Cy', 'Bob!', '0']


def test_a_removed_object_lives_on():
    out = run(CAR + main('Car:[] cars\ncars.add(Car("red"))\ncars.add(Car("blue"))\nCar c = cars.pop()\n'
                         'cars.pop()\nprint(c.color)'))
    assert out == ['blue']


def test_a_removed_null_slot():
    # Rule 4b: without a check a NullError; with ?. the code runs on
    body = 'Car:[] cars\ncars.add(null)\ncars.add(null)\nCar c = cars.pop()\nprint(c?.color ?? "none")\n'
    out = run(CAR + main(body + 'Car d = cars.pop()\ntry\n    print(d.color)\ncatch NullError e\n    print("null")'))
    assert out == ['none', 'null']


def test_pop_on_an_empty_array_in_a_value_is_an_index_error():
    out = run(main('int:[] xs\ntry\n    int x = xs.pop()\n    print("{@1}", x)\ncatch IndexError e\n    print("{e}")'))
    assert out == ['removeLast on an empty array']


def test_an_int_slot_cant_be_null():
    assert errors_of(main('int:[] xs\nxs.add(null)'))


@pytest.mark.parametrize('method', ['insert(0, 4)', 'removeAt(0)', 'clear()'])
def test_only_at_its_end(method):
    assert "an array grows and shrinks only at its end" in errors_of(main(f'int:[] xs = [1]\nxs.{method}'))


def test_a_plain_array_still_doesnt_grow():
    assert "a plain array doesn't grow or shrink - declare it int:[]" in errors_of(main('int[] a = [1]\na = [2]\na.add(3)'))


def test_a_growable_array_is_not_a_plain_one():
    assert "int:[]" in errors_of(main('int:[] g = [1]\nint[] a = [2, 3]\na = g'))


@pytest.mark.parametrize('body, message', [
    ('fixed int:[] x', "fixed and a growable array can't go together"),
    ('int:[10] x', 'A growable array starts empty'),
    ('int[[10]] x', 'Arrays of many dimensions'),
])
def test_wrong_forms_are_errors(body, message):
    with pytest.raises(ParserError, match=re.escape(message)):
        parse(main(body))
