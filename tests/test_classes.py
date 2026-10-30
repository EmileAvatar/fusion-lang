"""Tests for Task 32.10b - minimal classes, built with the counting.

    class Car
        string name
        Engine engine                   // an object: null until set
        constructor(string name)        // or Car(string name); none written: Car()
            this.name = name

An object lives on the heap with a count; a variable holds a reference to it (null until
set), `b = a` shares it, and it is freed when its last holder lets go. `Car(...)` and `new
Car(...)` make one; `.` on null is a NullError. `==` asks whether two names hold the same
object. A `let` object can't be replaced, but the object itself can change.

Every program runs with the leak check: an object never freed stops it with exit code 5.
With and without null checks (Rule 4b): `if car is not null` runs on; a plain `.` on null is a
NullError that `catch` handles.
"""

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main

CARS = ('class Engine\n'
        '    public string kind\n'
        '    constructor(string kind)\n'
        '        this.kind = kind\n\n'
        'class Car\n'
        '    public string name\n'
        '    public int speed = 10\n'
        '    public Engine engine\n'
        '    public List<string> trips\n\n'
        '    constructor(string name)\n'
        '        this.name = name\n'
        '        engine = Engine("V8")\n\n'
        '    void function swapEngine(string kind)\n'
        '        engine = Engine(kind)\n\n'
        '    Engine function getEngine() : engine\n\n'
        '    void function drive(string where)\n'
        '        trips.add(where)\n'
        '        speed = speed + 5\n\n'
        'Car function make(string n) : new Car(n)\n\n')


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err                       # the leak check too (5: an object kept)
    return out.strip().splitlines()


def test_fields_methods_and_the_constructor():
    lines = run(CARS + main('Car honda = Car("Honda")\n'
                            'Engine e = honda.getEngine()\n'
                            'honda.swapEngine("V6")\n'
                            'honda.drive("work")\n'
                            'print("{honda.name} {honda.speed} {honda.engine.kind} {e.kind} {@1}", '
                            'honda.trips.len())'))
    assert lines == ['Honda 15 V6 V8 1']


def test_objects_are_shared_and_compared_by_identity():
    lines = run(CARS + main('Car honda = Car("Honda")\n'
                            'Car same = honda\n'
                            'same.name = "Shared"\n'
                            'print(honda.name)\n'
                            'print("{@1} {@2}", same == honda, honda == Car("Other"))\n'
                            'honda = null\n'
                            'print("{@1} {@2}", honda == null, same is null)\n'
                            'let fixed = make("Let")\n'
                            'fixed.speed = 99\n'
                            'print("{@1}", fixed.speed)'))
    assert lines == ['Shared', 'true false', 'true false', '99']


def test_no_constructor_new_and_lists_of_objects():
    lines = run(CARS + 'class Plain\n    public int n\n    public string s\n    public Car car\n\n'
                + main('Plain p = new Plain()\n'
                       'print("{@1} [{@2}] {@3}", p.n, p.s, p.car == null)\n'
                       'List<Car> cars = [make("One"), make("Two")]\n'
                       'cars.add(Car("Three"))\n'
                       'cars.removeAt(0)\n'
                       'Car("Temp").drive("nowhere")\n'
                       'print("{@1} {@2} {@3}", cars.len(), cars[1].name, Car("Temp").speed)'))
    assert lines == ['0 [] true', '2 Three 10']


def test_null_with_and_without_a_check():
    lines = run(CARS + main('Car none\n'
                            'if none is not null\n'
                            '    print(none.name)\n'
                            'else\n'
                            '    print("no car")\n'
                            'try\n'
                            '    print(none.name)\n'
                            'catch err\n'
                            '    print("caught: {err.message}")\n'
                            'try\n'
                            '    none.drive("x")\n'
                            'catch err\n'
                            '    print("caught: {err.message}")'))
    assert lines == ['no car', "caught: used '.' on a null Car",
                     "caught: used '.' on a null Car"]


def test_a_constructor_that_fails_half_way_frees_the_object():
    # O2: the error goes to the caller, never the half-made object - the leak check would
    # stop the program if the object or its engine were kept
    lines = run('class Engine\n    public string kind\n\n'
                'class Car\n'
                '    public Engine engine\n'
                '    public string name\n'
                '    constructor(string name)\n'
                '        engine = Engine()\n'
                '        if name == ""\n'
                '            throw Error("a car needs a name")\n'
                '        if name == "early"\n'
                '            return\n'
                '        this.name = name\n\n'
                + main('try\n'
                       '    Car bad = Car("")\n'
                       '    print("made")\n'
                       'catch err\n'
                       '    print("caught: {err.message}")\n'
                       'Car early = Car("early")\n'
                       'print("[{early.name}] {@1}", early.engine == null)'))
    assert lines == ['caught: a car needs a name', '[] false']


@pytest.mark.parametrize('source, message', [
    ('struct S\n    Car c\n\nclass Car\n    public int n\n\nvoid function main()\n    S s\n',
     "Struct 'S' can't hold a class object (field 'c')"),
    ('class Car\n    public int n\n\nvoid function main()\n    List<Car> cs\n    List<Car> d = byVal cs\n',
     "A copy of a List<Car> would copy its objects - that needs clone()"),
    ('class Car\n    public int n\n\nvoid function main()\n    List<Car> cs\n    List<Car> d = cs.toList()\n',
     "A copy of a List<Car> would copy its objects"),
    ('class Car\n    public int n\n\nvoid function main()\n    Car c = Car()\n    print("{c}")\n',
     "Can't print a whole Car object yet"),
    ('class Car\n    public int n\n\nvoid function main()\n    int x = null\n',
     "A int can't be null - only a class object or an enum can"),
])
def test_class_errors(source, message):
    assert message in errors_of(source)


@pytest.mark.parametrize('source, message', [
    ('class Car\n    constructor()\n        print("a")\n    constructor(int n)\n        print("b")\n',
     "One constructor per class for now"),
    ('class Car implements Thing\n    public int n\n', "comes with inheritance"),
    ('void function main()\n    int x = new 5\n', "'new' comes before a class's constructor"),
])
def test_class_parse_errors(source, message):
    with pytest.raises(ParserError, match=message):
        Parser(Lexer(source, 't').tokenize()).parse_program()
