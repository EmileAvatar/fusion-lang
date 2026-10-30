"""Tests for Task 32.2f - printing an object (Classes.md section 6).

Until a class can implement ToString (Task 32.5) an object prints as its class name - in
print / format, "{car}" and toString(car) - with one warning per class. With and without
null checks (Rule 4b): a null object prints "null" (like most languages), no NullError; with
`if car is not null` the name. Every program runs with the leak check - an object made only
to be printed is freed.
"""

from tests.test_object_lifetime import traced
from tests.test_structs import main, warnings_of

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
    message = ("Car doesn't implement ToString - it prints as its class name 'Car' (ToString "
               "comes with interfaces, Task 32.5)")
    assert warnings.count(message) == 1
