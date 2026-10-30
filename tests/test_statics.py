"""Tests for Task 32.2c - a class's statics (Classes.md section 3).

Forms A (direct), B (a block that sets up its own field) and C (`static { }`, any static),
run in that order before main; classes set up in the order they depend on each other; a
circle is a compile error showing the whole chain; statics freed last (after main's locals
and module variables). Each test is a row of the tables.
"""

import pytest

from tests.test_object_lifetime import traced
from tests.test_structs import errors_of, main

GARAGE = ('class Engine\n'
          '    public string kind\n'
          '    public static int made\n'
          '    constructor(string kind)\n'
          '        this.kind = kind\n'
          '        made = made + 1\n\n'
          'class Car\n'
          '    public string name\n'
          '    public int speed\n'
          '    public static int count\n'
          '    public const static Car BASIC = new Car("Basic")\n'          # form A
          '    public const static Car TUNED = new Car("Tuned") {\n'        # form B
          '        TUNED.speed = 99\n'
          '    }\n'
          '    public const static Car SPECIAL\n'
          '    private static Engine spare\n'
          '    static {\n'                                                  # form C
          '        SPECIAL = new Car("Special")\n'
          '        spare = Engine("V8")\n'
          '        TUNED.name = "Tuned!"\n'
          '    }\n'
          '    constructor(string name)\n'
          '        this.name = name\n'
          '        count = count + 1\n'
          '    static string function describe() : format("{@1} cars, spare {@2}", count, spare.kind)\n\n')


def test_forms_a_b_c_and_static_methods(tmp_path):
    assert traced(GARAGE + main('print("{Car.BASIC.name} {Car.TUNED.name} {Car.TUNED.speed} '
                                '{Car.SPECIAL.name}")\n'
                                'print(Car.describe())\n'
                                'Car mine = Car("Mine")\n'
                                'print("{@1} {@2}", Car.count, Engine.made)'), tmp_path) == \
        ['Basic Tuned! 99 Special', '3 cars, spare V8', '4 1',
         '[freed Car]',                                        # mine - main's local first
         '[freed Engine]', '[freed Car]', '[freed Car]', '[freed Car]']   # the statics last


def test_classes_set_up_by_dependency(tmp_path):
    # Car's set-up uses Parts and Engine, declared after it - they are set up first
    assert traced('class Car\n'
                  '    public static int wheels = Parts.WHEELS\n'
                  '    public static Engine SPARE = Engine("V6")\n\n'
                  'class Engine\n'
                  '    public string kind\n'
                  '    constructor(string kind)\n'
                  '        this.kind = kind\n\n'
                  'class Parts\n'
                  '    public const static int WHEELS = 4\n\n'
                  + main('print("{Car.wheels} {Car.SPARE.kind}")'), tmp_path) == \
        ['4 V6', '[freed Engine]']


CIRCLE = ('class Car\n'
          '    public static int count\n'
          '    public static Engine SPARE = Engine("V6")\n\n'
          'class Engine\n'
          '    public string kind\n'
          '    constructor(string kind)\n'
          '        this.kind = kind\n'
          '        Factory.build()\n\n'
          'class Factory\n'
          '    static void function build()\n'
          '        Car.count = Car.count + 1\n\n')

RULES = ('class Rules\n'
         '    public static int first = second\n'
         '    public static int second = 2\n'
         '    public static int other = 1\n'
         '    public const static int FIXED\n'
         '    public static int keep = 5 {\n'
         '        other = 9\n'
         '    }\n'
         '    private static int hidden = 3\n\n')


@pytest.mark.parametrize('source, message', [
    (CIRCLE + main('print("x")'),
     "Factory can't use Car - Car is still being set up (Car -> Engine -> Factory -> Car)"),
    ('class A\n    public static int x = B.y\n\nclass B\n    public static int y = A.x\n\n'
     + main('print("x")'), "The statics of A and B need each other to be set up first (A -> B -> A)"),
    (RULES + main('print("x")'), "Static 'first' reads static 'second' before it is set up - "
                                 "forms A, B and C run in that order"),
    (RULES + main('print("x")'), "The set-up block of 'keep' can only change 'keep' - change "
                                 "'other' in the static block"),
    (RULES + main('print("x")'), "const static 'FIXED' has no value"),
    (RULES + main('Rules.FIXED = 3'), "'Rules.FIXED' is const static - it is set only in "
                                      "Rules's static set-up"),
    (RULES + main('print("{Rules.hidden}")'), "Static 'Rules.hidden' is private"),
])
def test_static_errors(source, message):
    assert message in errors_of(source)
