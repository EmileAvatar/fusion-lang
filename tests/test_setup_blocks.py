"""Tests for Task 32.2d - form B on any variable (Classes.md section 4).

A block right after a value sets that variable up further: a local (typed, `let`, `const`), a
List, a field of a class (each constructor runs it first, before its own body - once, also
when it hands over to another with `this(...)`). The block changes its own variable only.
With and without null checks (Rule 4b): a block on a null object is a NullError `catch`
handles; with `if ... is not null` it runs on. Every program runs with the leak check.
"""

import pytest

from tests.test_object_lifetime import traced
from tests.test_structs import errors_of, main

CLASSES = ('class Engine\n'
           '    public string kind = "none"\n'
           '    public int power\n\n'
           'class Car\n'
           '    public string name = "car"\n'
           '    public Engine engine = new Engine() {\n'
           '        engine.kind = "V6"\n'
           '        engine.power = 300\n'
           '    }\n'
           '    public int speed = 5\n'
           '    constructor()\n'
           '        speed = speed + 1\n'
           '    constructor(string name)\n'
           '        this()\n'
           '        this.name = name\n\n')


def test_locals_typed_let_const_and_lists(tmp_path):
    assert traced(CLASSES + main('Car c = new Car() {\n'
                                 '    c.speed = 99\n'
                                 '    int extra = 1\n'                 # the block's own variable
                                 '    c.engine.power = c.engine.power + extra\n'
                                 '}\n'
                                 'print("{c.speed} {c.engine.power}")\n'
                                 'let e = new Engine()\n'
                                 '    e.kind = "electric"\n'           # an indented block
                                 'const Engine k = new Engine() { k.kind = "diesel" }\n'
                                 'print("{e.kind} {k.kind}")\n'
                                 'List<string> names = List<string>() {\n'
                                 '    names.add("a")\n'
                                 '    names.add("b")\n'
                                 '}\n'
                                 'print(format("{@1}", names.length()))'), tmp_path)[:3] == \
        ['99 301', 'electric diesel', '2']


def test_field_blocks_run_first_in_every_constructor(tmp_path):
    # Car("d") hands over to Car() - the field's block runs once, before speed + 1
    assert traced(CLASSES + main('Car c = new Car()\n'
                                 'Car d = new Car("d")\n'
                                 'print("{c.name} {c.speed} {c.engine.kind} {c.engine.power}")\n'
                                 'print("{d.name} {d.speed} {d.engine.kind}")'), tmp_path)[:2] == \
        ['car 6 V6 300', 'd 6 V6']


def test_field_value_that_is_not_a_constant(tmp_path):
    # a field's value may use one before it - each constructor sets it in field order
    assert traced('class Box\n'
                  '    public int width = 3\n'
                  '    public int area = width * width\n\n'
                  + main('Box b = new Box()\nprint("{b.area}")'), tmp_path)[:1] == ['9']


def test_null_without_and_with_a_check(tmp_path):
    assert traced(CLASSES + main('Car none = null\n'
                                 'try\n'
                                 '    Car c = none {\n'
                                 '        c.speed = 1\n'
                                 '    }\n'
                                 '    print("set")\n'
                                 'catch err\n'
                                 '    print("caught: {err.message}")\n'
                                 'Car safe = none {\n'
                                 '    if safe is not null\n'
                                 '        safe.speed = 1\n'
                                 '}\n'
                                 'print("ran on")'), tmp_path) == \
        ["caught: used '.' on a null Car", 'ran on']


@pytest.mark.parametrize('source, message', [
    (CLASSES + main('Car other = new Car()\n'
                    'Car c = new Car() {\n'
                    '    other.speed = 3\n'
                    '}'),
     "The set-up block of 'c' can only change 'c' - change 'other' after the block"),
    (CLASSES + main('List<string> log = List<string>()\n'
                    'Car c = new Car() {\n'
                    '    log.add("made")\n'
                    '}'),
     "The set-up block of 'c' can only change 'c' - change 'log' after the block"),
    ('class Garage\n'
     '    public int count\n'
     '    public Engine spare = new Engine() {\n'
     '        count = 1\n'
     '    }\n\n'
     'class Engine\n'
     '    public string kind\n\n' + main('print("x")'),
     "The set-up block of 'spare' can only change 'spare' - change 'count' in a constructor"),
])
def test_block_changes_its_own_variable_only(source, message):
    assert message in errors_of(source)
