"""Tests for Task 32.7 - inheritance (Classes.md section 8, Decisions.md D.083, D.084).

    class Employee inherits Person        // `extends` as quick typing; one parent only
        override string function greet() : super.greet() + "!"
        constructor(string n)
            super(n)                       // the parent's constructor, on the first line

Each test is a row of the truth table in Classes.md section 8. Fusion favours composition
(holding an object) over inheritance (D.083). Every program runs with the leak check. With and
without null checks (Rule 4b).
"""

import pytest

from src.parser.parser import ParserError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main, parse

PEOPLE = ('class Person\n'
          '    public string name\n'
          '    protected int age = 30\n'
          '    constructor(string name)\n'
          '        this.name = name\n'
          '    string function greet() : "Hi, I am " + name\n'
          '    string function kind() : "person"\n\n'
          'class Employee inherits Person\n'
          '    public int salary\n'
          '    constructor(string name, int salary)\n'
          '        super(name)\n'
          '        this.salary = salary\n'
          '    override string function greet() : super.greet() + " and I work"\n'
          '    int function older() : age + 1\n\n'
          'class Manager extends Employee\n'
          '    constructor(string name)\n'
          '        super(name, 100)\n'
          '    override string function greet() : "I manage - " + super.greet()\n\n')


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_the_objects_own_function_runs_through_a_parent():
    assert run(PEOPLE + 'void function show(Person p)\n    print(p.greet())\n\n'
               + main('show(Person("Ann"))\nshow(Employee("Bob", 50))\nshow(Manager("Cy"))\n'
                      'List<Person> all = [Manager("Di"), Person("Ed")]\n'
                      'for p in all\n'
                      '    print(p.kind())')) == [
        'Hi, I am Ann', 'Hi, I am Bob and I work', 'I manage - Hi, I am Cy and I work',
        'person', 'person']


def test_fields_functions_and_protected_are_inherited():
    assert run(PEOPLE + main('Employee b = Employee("Bob", 50)\n'
                             'print("{b.name} {@1} {@2}", b.salary, b.older())')) == ['Bob 50 31']


def test_a_constructor_without_super_runs_the_parents_without_arguments():
    source = ('class Base\n    public int n = 1\n    constructor()\n        n = 7\n\n'
              'class Child inherits Base\n    public int m = 2\n\n'
              + main('Child c = Child()\nprint("{@1} {@2}", c.n, c.m)'))
    assert run(source) == ['7 2']


def test_is_a_cast_down_and_type_of():
    assert run(PEOPLE + main('Person p = Manager("Cy")\n'
                             'if p is Employee\n'
                             '    Employee e = (Employee)p\n'
                             '    print("{@1}", e.salary)\n'
                             'print(typeOf(p))\n'
                             'print(typeOf(Person("A")))\n'
                             'print(typeOf(5))')) == ['100', 'Person.Employee.Manager', 'Person', 'int']


def test_a_wrong_cast_is_a_cast_error():
    assert run(PEOPLE + main('Person p = Person("Ann")\n'
                             'try\n'
                             '    Employee e = (Employee)p\n'
                             'catch CastError err\n'
                             '    print(err.message)')) == ['a Person is not a Employee']


def test_without_a_null_check_a_null_parent_is_a_null_error():
    # Rule 4b: no check - `.` on a null is a NullError that catch handles
    assert run(PEOPLE + main('Person p\n'
                             'try\n'
                             '    print(p.greet())\n'
                             'catch NullError e\n'
                             '    print("caught")')) == ['caught']


def test_with_a_null_check_the_code_runs_on():
    assert run(PEOPLE + main('Person p\n'
                             'Employee e = (Employee)p\n'
                             'if e is null\n'
                             '    print("null stays null")\n'
                             'print(typeOf(p))')) == ['null stays null', 'null']


def test_abstract_functions_and_classes():
    source = ('abstract class Shape\n'
              '    abstract float function area()\n'
              '    string function describe() : "a shape"\n\n'
              'class Square inherits Shape\n'
              '    public float side = 2.0\n'
              '    override float function area() : side * side\n\n'
              + main('Shape s = Square()\nprint("{@1}", s.area())'))
    assert run(source) == ['4.000000']


def test_a_child_answers_the_parents_interfaces():
    source = ('interface Named\n    string function title()\n\n'
              'class Base implements Named\n    string function title() : "base"\n\n'
              'class Child inherits Base\n    override string function title() : "child"\n\n'
              + main('Named n = Child()\nprint(n.title())'))
    assert run(source) == ['child']


def test_a_copy_through_a_parent_copies_the_child():
    assert run(PEOPLE + main('Person p = Employee("Bob", 50)\n'
                             'Person q = byVal p\n'
                             'print(typeOf(q))\n'
                             'print(q.greet())')) == ['Person.Employee', 'Hi, I am Bob and I work']


@pytest.mark.parametrize('body, message', [
    ('class Bad inherits Person\n    string function greet() : "x"\n\n',
     "Function 'greet' replaces Person's - write 'override' before it"),
    ('class Bad inherits Person\n    override string function hello() : "x"\n\n',
     "'hello' overrides nothing - Person has no function 'hello'"),
    ('class Bad inherits Person\n    override int function greet() : 1\n\n',
     "Function 'greet' doesn't match Person's"),
    ('sealed class Closed\n    int n\n\nclass Bad inherits Closed\n    int m\n\n',
     "Class 'Closed' is sealed - no class can inherit it"),
    ('class Open\n    sealed string function f() : "x"\n\n'
     'class Bad inherits Open\n    override string function f() : "y"\n\n',
     "Function 'f' of Open is sealed - it can't be overridden"),
    ('class Bad inherits Nothing\n    int n\n\n', "Class 'Bad' inherits 'Nothing', which doesn't exist"),
    ('interface Shape\n    float function area()\n\nclass Bad inherits Shape\n    int n\n\n',
     "'Shape' is an interface - write implements"),
    ('class A inherits B\n    int n\n\nclass B inherits A\n    int m\n\n', "in a circle"),
    ('abstract class Shape\n    abstract float function area()\n\n'
     'class Bad inherits Shape\n    int n\n\n',
     "Class 'Bad' must give function 'area' - it is abstract in Shape"),
    ('class Half\n    abstract int function f()\n\n', "write 'abstract class Half'"),
    ('class Bad inherits Person\n    int function f() : age2\n    constructor()\n        super("x")\n\n',
     "Undefined variable: 'age2'"),
])
def test_inheritance_rules(body, message):
    assert message in errors_of(PEOPLE + body + main('print("x")'))


@pytest.mark.parametrize('line, message', [
    ('Person p = Person("A")\n    int a = p.age', "Field 'age' of class 'Person' is protected"),
    ('abstract class X\n', None),
])
def test_protected_and_abstract_from_outside(line, message):
    if message is None:
        source = ('abstract class Shape\n    abstract float function area()\n\n'
                  + main('Shape s = Shape()'))
        assert "Class 'Shape' is abstract - it can't be made" in errors_of(source)
        return
    assert message in errors_of(PEOPLE + main(line))


def test_one_parent_only():
    with pytest.raises(ParserError, match="has one parent"):
        parse('class A\n    int n\n\nclass B\n    int m\n\nclass C inherits A inherits B\n    int k\n')
