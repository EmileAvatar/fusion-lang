"""Task 45.7 - the array being looped over can't change inside the loop (D.058).

A compile error where the compiler sees it: adding or removing at a growable array's end, replacing
the array (any form), passing it to a function that changes it. A change it can't see is a
ModifiedWhileLoopingError while running - never a skipped item. Setting an item (`xs[0] = 5`) is no
change of size and is allowed. Every program runs under the leak check.
"""
import pytest

from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main


@pytest.mark.parametrize('loop', ['foreach (int x in xs)', 'for x in xs'])
@pytest.mark.parametrize('declaration, change', [
    ('int:[] xs = [1, 2]', 'xs.add(4)'),
    ('int:[] xs = [1, 2]', 'xs.pop()'),
    ('int:[] xs = [1, 2]', 'xs.removeLast()'),
    ('int:[] xs = [1, 2]', 'int last = xs.pop()'),
    ('int:[] xs = [1, 2]', 'xs = [7]'),
    ('int[] xs = [1, 2]', 'xs = [7, 8, 9]'),
    ('int[2] xs = [1, 2]', 'xs = [7, 8]'),
])
def test_a_change_inside_the_loop_is_a_compile_error(loop, declaration, change):
    errors = errors_of(main(f'{declaration}\n{loop}\n    {change}'))
    assert "'xs'" in errors and ('loop' in errors)


def test_passed_to_a_function_that_changes_it():
    errors = errors_of('void function grow(int:[] g)\n    g.add(9)\n\nvoid function main()\n    int:[] xs = [1, 2]\n'
                       '    foreach (int x in xs)\n        grow(xs)\n')
    assert "'xs' can't change while a for loop walks it" in errors


def test_a_struct_field_replaced():
    errors = errors_of('struct Box\n    int[] items\n\nvoid function main()\n    Box b = Box([1, 2])\n'
                       '    foreach (int x in b.items)\n        b.items = [5]\n')
    assert "'b.items' can't change while a for loop walks it" in errors


def test_setting_an_item_is_allowed():
    out = run(main('int:[] xs = [1, 2, 3]\nforeach (int x in xs)\n    xs[0] = x\nprint("{@1}", xs[0])'))
    assert out == ['3']


def test_changing_another_array_is_allowed():
    out = run(main('int[] xs = [1, 2, 3]\nint:[] kept\nforeach (int x in xs)\n    if x > 1\n        kept.add(x)\n'
                   'print("{@1}", kept.length)'))
    assert out == ['2']


def test_a_change_through_an_object_is_caught():
    # through the object's own method: the loop borrows s.items, and shrink() changes s
    source = ('class Stack\n    public int:[] items\n    constructor()\n        this.items.add(1)\n'
              '        this.items.add(2)\n    public void function shrink()\n        this.items.pop()\n\n'
              + main('Stack s = Stack()\nforeach (int x in s.items)\n    s.shrink()'))
    assert "'s.items' can't change while a for loop walks it" in errors_of(source)
