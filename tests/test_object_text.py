"""Tests for Task 32.2f - printing an object (Classes.md section 6).

Until a class can implement ToString (Task 32.5) an object prints as its class name - in
print / format, "{car}" and toString(car) - with one warning per class. With and without
null checks (Rule 4b): a null object prints "null" (like most languages), no NullError; with
`if car is not null` the name. Every program runs with the leak check - an object made only
to be printed is freed.
"""

import pytest

from tests.test_object_lifetime import traced

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main, warnings_of

CAR = 'class Car\n    public string name = "x"\n\n'


def test_object_prints_its_class_name(tmp_path):
    lines = traced(CAR + main('Car c = Car()\n'
                              'print("{c}")\n'
                              'print(format("{@1} {@2}", c, Car()))\n'
                              'string s = toString(c) + " " + toString(Car())\n'
                              'print(s)'), tmp_path)
    # the objects made only to be printed are freed after their statement
    assert [line for line in lines if not line.startswith('[freed')] == ['Car', 'Car Car', 'Car Car']
    assert lines.count('[freed Car]') == 3


def test_null_without_and_with_a_check(tmp_path):
    assert traced(CAR + main('Car none = null\n'
                             'print("{none}")\n'
                             'print(format("{@1}", none))\n'
                             'print(toString(none))\n'
                             'if none is not null\n'
                             '    print("{none}")\n'
                             'else\n'
                             '    print("no car")'), tmp_path) == \
        ['null', 'null', 'null', 'no car']


def test_one_warning_per_class():
    warnings = warnings_of(CAR + main('Car c = Car()\nprint("{c}")\nprint(toString(c))'))
    message = ("Car doesn't implement ToString - it prints as its class name 'Car' (class Car "
               "implements ToString, with string function toString())")
    assert warnings.count(message) == 1


TEXT = ('class Car implements ToString\n'
        '    string name\n'
        '    constructor(string name)\n'
        '        this.name = name\n'
        '    string function toString() : "Car " + name\n\n'
        'interface Shape\n    float function area()\n\n'
        'class Dot implements Shape, ToString\n'
        '    float function area() : 0.0\n'
        '    string function toString() : "a dot"\n\n'
        'class Bike\n    int gears = 3\n\n')


def test_a_class_implementing_to_string_prints_its_own_text():
    # Task 32.5b: print, format, "{x}", toString(x) - its own text, freed after (the leak check)
    code, out, err = compile_and_run(TEXT + main('Car c = Car("Honda")\n'
                                                 'print("{c}")\nprint(toString(c))\n'
                                                 'print("{@1}", c)\n'
                                                 'Shape s = Dot()\nprint("{s}")\n'
                                                 'Bike b = Bike()\nprint("{b}")'))
    assert code == 0, err
    assert out.split('\n')[:5] == ['Car Honda', 'Car Honda', 'Car Honda', 'a dot', 'Bike']


def test_a_null_object_prints_null_with_or_without_to_string():
    # Rule 4b: printing never needs a null check - a null object prints null
    code, out, err = compile_and_run(TEXT + main('Car c = null\nShape s = null\n'
                                                 'print("{c} {s}")\nprint(toString(c))'))
    assert code == 0, err
    assert out.split('\n')[:2] == ['null null', 'null']


def test_no_warning_when_it_implements_to_string():
    assert "doesn't implement ToString" not in warnings_of(
        TEXT + main('Car c = Car("x")\nprint("{c}")\nShape s = Dot()\nprint("{s}")'))


@pytest.mark.parametrize('source, message', [
    ('class Car implements ToString\n    int n\n\n',
     "Class 'Car' implements ToString but has no function 'toString' - string function toString()"),
    ('class Car implements ToString\n    int function toString() : 1\n\n',
     "doesn't match ToString"),
    ('interface ToString\n    string function text()\n\n',
     "'ToString' is Fusion's own interface"),
])
def test_to_string_errors(source, message):
    assert message in errors_of(source + main('print("x")'))
