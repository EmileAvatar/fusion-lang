"""Task 45.10 - a plain array replaced by another size lives on the heap (D.141).

`a = [1, 2]` after `int[] a = [5, 2, 3]`, or `int[] function make(int n)` returning any size: the array
becomes a counted block on the heap (src/semantic/heap_arrays.py) and still acts as an array - passed
to an `int[]` parameter, indexed (checked), looped, `length`, `toList`, `toCSV`; no `add` (D.141), an
object slot may be null (D.140). Every program runs under the leak check.
"""
import pytest

from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main

TOTAL = ('int function total(int[] values)\n    int t = 0\n    foreach (int v in values)\n'
         '        t = t + v\n    return t\n\n')
MAKE = ('int[] function make(int n)\n    if n > 2\n        return [1, 2, 3, 4]\n    return [9]\n\n')
CAR = ('class Car\n    public string color\n    constructor(string c)\n        this.color = c\n\n')


def test_replaced_by_another_size():
    out = run(TOTAL + main('int[] a = [5, 2, 3]\nprint("{@1} {@2}", a.length, total(a))\n'
                           'a = [1, 2]\nprint("{@1} {@2} {@3}", a.length, a[1], total(a))'))
    assert out == ['3 10', '2 2 3']


def test_a_function_returning_any_size():
    out = run(TOTAL + MAKE + main('int[] a = make(5)\nint[] b = make(1)\na[0] = 10\n'
                                  'print("{@1} {@2} {@3} {@4}", a.length, Array.length(b), a[0], total(make(3)))'))
    assert out == ['4 1 10 10']


def test_a_sized_array_replaced_by_another_size():
    assert run(main('int[3] a = [1, 2, 3]\na = [7]\nprint("{@1} {@2}", a.length, a[0])')) == ['1 7']


def test_an_index_outside_is_an_index_error():
    out = run(MAKE + main('int[] a = make(5)\ntry\n    print("{@1}", a[7])\ncatch IndexError e\n    print("{e}")'))
    assert out == ['index 7 is outside the array (length 4)']


def test_strings_are_freed():
    out = run(main('string[] names = ["Ann", "Bob"]\nnames = ["Cy", "Di", "Ed"]\nnames[0] = "Flo"\n'
                   'foreach (string n in names)\n    print(n)'))
    assert out == ['Flo', 'Di', 'Ed']


def test_returning_a_local_array():
    source = ('string[] function names(bool many)\n    string[] r = ["a"]\n    if many\n'
              '        r = ["a", "b", "c"]\n    return r\n\n' + main('print("{@1} {@2}", names(true).length, names(false).length)'))
    assert run(source) == ['3 1']


def test_an_object_slot_may_be_null():
    # D.140 - unlike a List, a heap array's slot may hold null
    out = run(CAR + main('Car[] cars = [Car("red")]\ncars = [Car("blue"), null]\ncars[0] = null\n'
                         'cars[1] = Car("green")\nprint("{@1} {@2}", cars.length, cars[1].color)'))
    assert out == ['2 green']


def test_a_null_slot_without_a_check_is_a_null_error():
    # Rule 4b - without a check: a NullError, caught
    out = run(CAR + main('Car[] cars = [Car("red")]\ncars = [null, null]\ntry\n    print(cars[0].color)\n'
                         'catch NullError e\n    print("null")'))
    assert out == ['null']


def test_a_null_slot_with_a_check_runs_on():
    # Rule 4b - with a check: the code runs on
    out = run(CAR + main('Car[] cars = [Car("red")]\ncars = [null, Car("blue")]\nforeach (Car c in cars)\n'
                         '    if c is not null\n        print(c.color)\nprint("done")'))
    assert out == ['blue', 'done']


def test_to_list_and_to_csv():
    out = run('struct P\n    int x\n\n' + MAKE + main(
        'int[] a = make(4)\nList<int> xs = a.toList()\nxs.add(5)\nprint("{@1} {@2}", xs.len(), a.length)\n'
        'P[] ps = [P(1)]\nps = [P(2), P(3)]\nprint(ps.toCSV())'))
    assert out == ['5 4', 'P.x', '2', '3']


def test_a_struct_field_with_no_size():
    out = run('struct Box\n    int[] items\n\n' + main('Box b = Box([1, 2])\nb.items = [4, 5, 6]\n'
                                                       'print("{@1} {@2}", b.items.length, b.items[2])'))
    assert out == ['3 6']


@pytest.mark.parametrize('method', ['add(4)', 'insert(0, 4)', 'removeAt(0)', 'clear()'])
def test_a_plain_array_doesnt_grow(method):
    message = errors_of(MAKE + main(f'int[] a = make(4)\na.{method}'))
    assert "a plain array doesn't grow" in message


def test_an_array_is_not_a_list():
    assert "expected List<int>, got int[]" in errors_of(
        'void function f(List<int> xs)\n    print("x")\n\n' + MAKE + main('f(make(4))'))


def test_a_sized_parameter_needs_a_known_size():
    assert "make the parameter int[]" in errors_of(
        'void function f(int[3] xs)\n    print("x")\n\n' + MAKE + main('f(make(4))'))


def test_a_fixed_array_set_from_a_function():
    out = run(MAKE + main('fixed int[] d = make(5)\nprint("{@1}", d.length)'))
    assert out == ['4']


def test_a_fixed_array_cant_be_replaced():
    assert "is fixed - its size never changes" in errors_of(MAKE + main('fixed int[] d = make(5)\nd = make(1)'))


def test_equality_compares_the_items():
    out = run(MAKE + main('int[] a = make(5)\nint[] b = make(4)\nint[] c = make(1)\n'
                          'print("{@1} {@2}", a == b, a == c)'))
    assert out == ['true false']


def test_an_array_moves_like_a_list():
    # D.025: in normal code an array moves - after `b = a`, a can't be used (strict ownership)
    assert "moved" in errors_of(MAKE + main('int[] a = make(5)\nint[] b = a\nprint("{@1}", a.length)'))


def test_by_val_copies():
    out = run(MAKE + main('int[] a = make(5)\nint[] b = byVal a\nb[0] = 99\nprint("{@1} {@2}", a[0], b[0])'))
    assert out == ['1 99']


def test_a_struct_with_a_heap_array_is_copied_whole():
    out = run('struct Box\n    int[] items\n\n' + main('Box b = Box([1, 2])\nBox c = byVal b\nc.items[0] = 9\n'
                                                       'print("{@1} {@2}", b.items[0], c.items[0])'))
    assert out == ['1 9']
