"""Tests for Task 32.5a - interfaces (Classes.md section 7, Decisions.md D.082, D.087).

    interface Shape                      // function signatures only - what, not how
        float function area()
    class Circle implements Shape        // several: implements Shape, Named
    Shape s = Circle(2.0)                // an interface as a type
    s.area()                             // the object's own function runs
    if s is Circle                       // what it is while running
        Circle c = (Circle)s             // a cast written in front - a CastError when wrong

Each test is a row of the truth table in Classes.md section 7. Every program runs with the
leak check (exit 5: an object never freed). With and without null checks (Rule 4b).
"""

import pytest

from src.config.project_config import InterfacesConfig
from src.parser.parser import ParserError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main, parse

SHAPES = ('interface Shape\n'
          '    float function area()\n'
          '    string function name()\n\n'
          'interface Named\n'
          '    string function name()\n\n'
          'class Circle implements Shape, Named\n'
          '    public float r\n'
          '    constructor(float r)\n'
          '        this.r = r\n'
          '    float function area() : 3.0 * r * r\n'
          '    string function name() : "circle"\n\n'
          'class Square implements Shape\n'
          '    float side\n'
          '    constructor(float side)\n'
          '        this.side = side\n'
          '    float function area() : side * side\n'
          '    string function name() : "square"\n\n')


def run(source: str, **options) -> list:
    code, out, err = compile_and_run(source, analyzer_options=options or None)
    assert code == 0, err                       # the leak check too (5: an object kept)
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_the_objects_own_function_runs():
    assert run(SHAPES + 'float function total(List<Shape> shapes)\n'
                        '    float sum = 0.0\n'
                        '    for s in shapes\n'
                        '        sum = sum + s.area()\n'
                        '    return sum\n\n'
               + main('List<Shape> shapes = [Circle(1.0), Square(2.0)]\n'
                      'shapes.add(Circle(2.0))\n'
                      'print("{@1}", total(shapes))\n'
                      'Shape one = shapes[1]\n'
                      'print(one.name())')) == ['19.000000', 'square']


def test_a_class_implements_several_and_each_interface_sees_it():
    assert run(SHAPES + main('Circle c = Circle(1.0)\n'
                             'Shape s = c\n'
                             'Named n = c\n'
                             'print("{@1} {@2}", s.name(), n.name())')) == ['circle circle']


def test_an_interface_building_on_several():
    source = ('interface Sized\n    int function size()\n\n'
              'interface Named\n    string function name()\n\n'
              'interface Item implements Sized, Named\n    int function price()\n\n'
              'class Book implements Item\n'
              '    int function size() : 300\n'
              '    string function name() : "Dune"\n'
              '    int function price() : 12\n\n'
              'void function show(Named n)\n    print(n.name())\n\n'
              + main('Item i = Book()\n'
                     'print("{@1} {@2}", i.size(), i.price())\n'
                     'show(i)\n'
                     'Sized s = Book()\n'
                     'print("{@1}", s.size())'))
    assert run(source) == ['300 12', 'Dune', '300']


def test_is_and_a_cast_back_to_the_class():
    assert run(SHAPES + main('Shape s = Circle(2.0)\n'
                             'if s is Circle\n'
                             '    Circle c = (Circle)s\n'
                             '    print("circle {@1}", c.r)\n'
                             'if s is not Square\n'
                             '    print("not a square")\n'
                             'Named n = (Named)s\n'
                             'print(n.name())')) == ['circle 2.000000', 'not a square', 'circle']


def test_a_wrong_cast_is_a_cast_error_that_catch_handles():
    assert run(SHAPES + main('Shape s = Square(1.0)\n'
                             'try\n'
                             '    Circle c = (Circle)s\n'
                             '    print("never")\n'
                             'catch CastError e\n'
                             '    print(e.message)')) == ['a Square is not a Circle']


def test_without_a_null_check_a_null_is_a_null_error():
    # Rule 4b: no check - `.` on a null interface value is a NullError that catch handles
    assert run(SHAPES + main('Shape s\n'
                             'try\n'
                             '    print("{@1}", s.area())\n'
                             'catch NullError e\n'
                             '    print("caught")')) == ['caught']


def test_with_a_null_check_the_code_runs_on():
    # Rule 4b: with a check - a null is no type, and a cast of null stays null
    assert run(SHAPES + main('Shape s\n'
                             'if s is not null\n'
                             '    print("never")\n'
                             'print("{@1}", s is Circle)\n'
                             'Circle c = (Circle)s\n'
                             'if c is null\n'
                             '    print("still null")')) == ['false', 'still null']


def test_printing_an_interface_value_gives_the_objects_class():
    assert run(SHAPES + main('Shape s = Square(1.0)\n'
                             'print("{s}")\n'
                             'print(toString(s))')) == ['Square', 'Square']


def test_default_methods_when_the_setting_allows_them():
    source = ('interface Greeter\n'
              '    string function name()\n'
              '    string function greet() : "Hello " + this.name()\n\n'
              'class English implements Greeter\n'
              '    string function name() : "Ann"\n\n'
              'class Formal implements Greeter\n'
              '    string function name() : "Bob"\n'
              '    string function greet() : "Good day " + name()\n\n'
              + main('Greeter a = English()\n'
                     'Greeter b = Formal()\n'
                     'print(a.greet())\n'
                     'print(b.greet())'))
    on = {'interfaces_config': InterfacesConfig(default_methods=True)}
    assert run(source, **on) == ['Hello Ann', 'Good day Bob']
    assert "has code" in errors_of(source)          # the default: no code in an interface


@pytest.mark.parametrize('body, message', [
    ('class Bad implements Shape\n    float function area() : 1.0\n\n',
     "Class 'Bad' implements Shape but has no function 'name' - string function name()"),
    ('class Bad implements Shape\n    int function area() : 1\n    string function name() : "x"\n\n',
     "Function 'area' of class 'Bad' doesn't match Shape: Shape has float function area(), "
     "Bad has int function area()"),
    ('class Bad implements Shape\n    float function area() : 1.0\n'
     '    private string function name() : "x"\n\n',
     "Function 'name' of class 'Bad' must be public"),
    ('class Bad implements Circle\n    int n\n\n', "which is a class - building on a class is inheritance"),
    ('class Bad implements Nothing\n    int n\n\n', "implements 'Nothing', which doesn't exist"),
    ('interface Loop implements Loop2\n    int function a()\n\n'
     'interface Loop2 implements Loop\n    int function b()\n\n', "in a circle"),
])
def test_what_a_class_must_give(body, message):
    assert message in errors_of(SHAPES + body + main('print("x")'))


@pytest.mark.parametrize('line, message', [
    ('Shape s = Shape()', "'Shape' is an interface - it can't be made"),
    ('Circle c = Circle(1.0)\n    Square q = (Square)c', "A Circle is never a Square"),
    ('Circle c = Circle(1.0)\n    bool b = c is Square', "A Circle is never a Square"),
    ('int n = 3\n    bool b = n is Circle', "Only an object has a type to test"),
    ('Square q = Square(1.0)\n    Named n = q', "Named"),        # Square isn't Named
])
def test_what_can_never_hold(line, message):
    assert message in errors_of(SHAPES + main(line))


def test_an_interface_holds_functions_only():
    with pytest.raises(ParserError, match="An interface holds functions only"):
        parse('interface Shape\n    int sides\n')


def test_readonly_holds_through_an_interface():
    # 32.2e: an interface's function changes its object when any class's answer does
    counter = ('interface Counter\n    void function add()\n    int function total()\n\n'
               'class Tally implements Counter\n'
               '    int n\n'
               '    void function add()\n        n = n + 1\n'
               '    int function total() : n\n\n')
    reads = counter + 'int function look(readonly Counter c) : c.total()\n\n'
    assert run(reads + main('Counter c = Tally()\nc.add()\nprint("{@1}", look(c))')) == ['1']
    changes = counter + 'void function bump(readonly Counter c)\n    c.add()\n\n'
    assert "'c' is readonly" in errors_of(changes + main('print("x")'))
