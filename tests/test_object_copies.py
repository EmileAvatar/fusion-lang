"""Tests for Task 32.5b - copies of objects (Decisions.md D.088, D.034; Object_Lifetime.md 4b).

    Car b = byVal a                // a new Car, each field copied byVal - its engine and lists too
    class Account implements Cloneable
        Account function clone()   // byVal calls it
    nocopy Database db             // set only in a constructor or clone(); the class needs Cloneable
    noshare Log log                // never handed out - `return byVal log`

Every program runs with the leak check (exit 5: an object never freed). With and without null
checks (Rule 4b): a copy of null is null.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main

CARS = ('class Engine\n'
        '    public string kind\n'
        '    constructor(string kind)\n'
        '        this.kind = kind\n\n'
        'class Car\n'
        '    public string name\n'
        '    public Engine engine\n'
        '    public List<string> trips\n'
        '    public int[2] seats\n'
        '    constructor(string name)\n'
        '        this.name = name\n'
        '        engine = Engine("V8")\n\n')


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_a_copy_is_a_new_object_with_each_field_copied():
    assert run(CARS + main('Car a = Car("Honda")\n'
                           'a.trips.add("work")\n'
                           'a.seats[0] = 4\n'
                           'Car b = byVal a\n'
                           'b.name = "Copy"\n'
                           'b.engine.kind = "V6"\n'
                           'b.trips.add("home")\n'
                           'b.seats[0] = 2\n'
                           'print("{a.name} {a.engine.kind} {@1} {@2}", a.trips.len(), a.seats[0])\n'
                           'print("{b.name} {b.engine.kind} {@1} {@2}", b.trips.len(), b.seats[0])\n'
                           'print("{@1}", a == b)')) == ['Honda V8 1 4', 'Copy V6 2 2', 'false']


def test_a_copy_of_a_list_of_objects_copies_the_objects():
    assert run(CARS + main('List<Car> cars = [Car("A")]\n'
                           'List<Car> more = byVal cars\n'
                           'more[0].name = "B"\n'
                           'print("{@1} {@2}", cars[0].name, more[0].name)')) == ['A B']


def test_a_copy_through_an_interface_is_made_by_the_objects_class():
    source = ('interface Shape\n    float function area()\n\n'
              'class Square implements Shape\n'
              '    public float side = 1.0\n'
              '    float function area() : side * side\n\n'
              + main('Square q = Square()\n'
                     'Shape s = q\n'
                     'Shape t = byVal s\n'
                     'q.side = 3.0\n'
                     'print("{@1} {@2} {t}", s.area(), t.area())'))
    assert run(source) == ['9.000000 1.000000 Square']


def test_without_a_null_check_a_copy_of_null_is_null():
    # Rule 4b: no check - byVal of a null object is null; using it is a NullError catch handles
    assert run(CARS + main('Car a = null\n'
                           'Car b = byVal a\n'
                           'try\n'
                           '    print(b.name)\n'
                           'catch NullError e\n'
                           '    print("caught")')) == ['caught']


def test_with_a_null_check_the_code_runs_on():
    assert run(CARS + main('Car a = null\n'
                           'Car b = byVal a\n'
                           'if b is null\n'
                           '    print("null copy")')) == ['null copy']


CLONEABLE = ('class Database\n    public string name = "db"\n\n'
             'class Account implements Cloneable\n'
             '    nocopy Database db\n'
             '    public int balance\n'
             '    constructor()\n'
             '        db = Database()\n'
             '    Account function clone()\n'
             '        print("clone")\n'
             '        Account a = Account()\n'
             '        a.balance = balance\n'
             '        return a\n\n')


def test_cloneable_makes_its_own_copy():
    assert run(CLONEABLE + main('Account a = Account()\n'
                                'a.balance = 5\n'
                                'Account b = byVal a\n'
                                'b.balance = 7\n'
                                'print("{@1} {@2}", a.balance, b.balance)')) == ['clone', '5 7']


def test_noshare_is_copied_when_handed_out():
    source = ('class Log\n    public List<string> lines\n\n'
              'class Shop\n'
              '    noshare Log log\n'
              '    constructor()\n'
              '        log = Log()\n'
              '        log.lines.add("open")\n'
              '    Log function history() : byVal log\n\n'
              + main('Shop s = Shop()\nLog l = s.history()\nl.lines.add("x")\n'
                     'print("{@1}", s.history().lines.len())'))
    assert run(source) == ['1']


@pytest.mark.parametrize('source, message', [
    ('class Database\n    int n\n\nclass Account\n    nocopy Database db\n\n',
     "Account's field 'db' is nocopy (implement Cloneable"),
    ('class Node\n    public Node next\n\n', "Node objects can hold each other in a circle"),
])
def test_what_cant_be_copied(source, message):
    name = 'Account' if 'Account' in source else 'Node'
    assert message in errors_of(source + main(f'{name} a = {name}()\n{name} b = byVal a'))


@pytest.mark.parametrize('source, message', [
    ('class Account implements Cloneable\n    int n\n\n',
     "Class 'Account' implements Cloneable but has no function 'Account function clone()'"),
    ('class Database\n    int n\n\nclass Account\n    nocopy Database db\n'
     '    void function swap()\n        db = Database()\n\n',
     "'db' is nocopy - only a constructor or clone() of Account sets it"),
    ('class Log\n    int n\n\nclass Shop\n    noshare Log log\n'
     '    Log function history() : log\n\n',
     "'log' is noshare - it is never handed out; give a copy: byVal log"),
])
def test_copy_rules(source, message):
    assert message in errors_of(source + main('print("x")'))
