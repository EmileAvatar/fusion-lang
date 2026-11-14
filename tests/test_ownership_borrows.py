"""Tests for Task 48.2 - borrowing (files/Ownership.md truth tables 1-3; R3-R5; D.026, D.100, D.101).

    Car first = fleet[0]         // a local borrow: fleet can't change while 'first' is used
    paint(c)                     // passing borrows: c is back after the call
    void function park(Car c)    // keeps c in a field: it takes it - park(c) moves c (D.100)

Checked with `[memory] assignment = "move"`; programs that compile still run with the leak
check - the counting is unchanged until 48.6.
"""

import pytest

from src.config.project_config import MemoryConfig
from tests.test_ownership_moves import CAR, errors, run
from tests.test_structs import main

GARAGE = 'class Garage\n    public Car car\n    void function park(Car c)\n        this.car = c\n\n'
ORDER = 'struct Order\n    int id\n    List<int> items\n\n'


# ---------- passing borrows (R3); a function that keeps a parameter takes it (D.100) ----------

def test_passing_borrows_the_value_is_back_after_the_call():
    source = CAR + 'void function paint(Car c)\n    c.color = "blue"\n\n' + \
        main('Car a = Car("red")\npaint(a)\nprint(a.color)')
    assert run(source) == ['blue']


def test_a_method_storing_its_parameter_takes_it():
    source = CAR + GARAGE + main('Garage g = Garage()\nCar a = Car("red")\ng.park(a)\nprint(a.color)')
    assert errors(source) == ["'a' was moved to 'park' (which keeps it) on line 14 - use byVal a "
                              "for a copy"]


def test_a_constructor_keeping_its_parameter_takes_it():
    source = CAR + 'class Driver\n    public Car car\n    constructor(Car c)\n        this.car = c\n\n' + \
        main('Car a = Car("red")\nDriver d = Driver(a)\nprint(a.color)')
    assert errors(source) == ["'a' was moved to 'Driver' (which keeps it) on line 13 - use byVal a "
                              "for a copy"]


def test_keeping_is_followed_through_the_calls():
    # register adds it to a List; enrol passes it to register - so enrol keeps it too
    source = CAR + 'List<Car> all = []\n\nvoid function register(Car c)\n    all.add(c)\n\n' \
        'void function enrol(Car c)\n    register(c)\n\n' + \
        main('Car a = Car("red")\nenrol(a)\nprint(a.color)')
    assert any("'a' was moved to 'enrol' (which keeps it)" in e for e in errors(source))


def test_a_parameter_kept_through_a_local_name():
    source = CAR + 'class Driver\n    public Car car\n    void function take(Car c)\n' \
        '        Car mine = c\n        this.car = mine\n\n' + \
        main('Driver d = Driver()\nCar a = Car("red")\nd.take(a)\nprint(a.color)')
    assert any("'a' was moved to 'take' (which keeps it)" in e for e in errors(source))


def test_returning_a_parameter_keeps_it():
    source = CAR + 'Car function same(Car c)\n    return c\n\n' + \
        main('Car a = Car("red")\nCar b = same(a)\nprint(a.color)')
    assert any("'a' was moved to 'same' (which keeps it)" in e for e in errors(source))


def test_reading_a_parameter_into_a_local_does_not_keep_it():
    source = CAR + 'string function colour(Car c)\n    Car mine = c\n    return mine.color\n\n' + \
        main('Car a = Car("red")\nprint(colour(a))\nprint(a.color)')
    assert run(source) == ['red', 'red']


def test_a_method_keeping_this_does_not_move_the_object():
    source = CAR + 'List<Car> all = []\n\nclass Robot\n    public string name\n' \
        '    void function join()\n        print(this.name)\n\n' + \
        main('Robot r = Robot()\nr.name = "r1"\nr.join()\nprint(r.name)')
    assert run(source) == ['r1', 'r1']


def test_a_taking_function_given_a_copy():
    source = CAR + GARAGE + main('Garage g = Garage()\nCar a = Car("red")\ng.park(byVal a)\n'
                                 'print("{a.color} {g.car.color}")')
    assert run(source) == ['red red']


def test_a_struct_made_with_a_list_moves_it():
    source = ORDER + main('List<int> xs = [1, 2]\nOrder o = Order(1, xs)\nprint("{@1}", xs.len())')
    assert any("'xs' was moved to 'Order'" in e for e in errors(source))


# ---------- local borrows: the owner frozen until the last use (D.101) ----------

def test_an_element_is_a_local_borrow():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nprint(first.color)\n'
                        'print("{@1}", fleet.len())')
    assert run(source) == ['red', '1']


def test_the_owner_cant_change_while_the_borrow_is_used():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nfleet.clear()\n'
                        'print(first.color)')
    assert errors(source) == ["'fleet' can't change while 'first' borrows from it (line 8, last "
                              "used on line 10)"]


def test_after_the_last_use_the_owner_may_change():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nprint(first.color)\n'
                        'fleet.clear()\nprint("{@1}", fleet.len())')
    assert run(source) == ['red', '0']


@pytest.mark.parametrize('change', [
    'fleet = []', 'fleet[0] = Car("blue")', 'fleet.add(Car("blue"))', 'fleet.removeAt(0)',
    'List<Car> other = fleet',
])
def test_every_kind_of_change_to_the_owner(change):
    source = CAR + main(f'List<Car> fleet = [Car("red")]\nCar first = fleet[0]\n{change}\n'
                        f'print(first.color)')
    assert any("'fleet' can't change while 'first' borrows from it" in e for e in errors(source))


def test_a_field_borrow_freezes_that_field_not_the_others():
    source = ORDER + main('Order o = Order(1, [1, 2])\nList<int> xs = o.items\no.id = 2\n'
                          'print("{@1} {@2}", xs.len(), o.id)')
    assert run(source) == ['2 2']
    frozen = ORDER + main('Order o = Order(1, [1, 2])\nList<int> xs = o.items\no.items = [3]\n'
                          'print("{@1}", xs.len())')
    assert any("'o.items' can't change while 'xs' borrows from it" in e for e in errors(frozen))


def test_a_method_changing_the_owner_counts():
    source = CAR + 'class Fleet\n    public List<Car> cars = []\n    void function empty()\n' \
        '        this.cars.clear()\n\n' + \
        main('Fleet f = Fleet()\nf.cars.add(Car("red"))\nCar first = f.cars[0]\nf.empty()\n'
             'print(first.color)')
    assert any("'f.cars' can't change while 'first' borrows from it" in e for e in errors(source))


def test_a_borrow_used_in_a_later_branch():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nif true\n'
                        '    fleet.clear()\n    print(first.color)')
    assert any("'fleet' can't change" in e for e in errors(source))


def test_changing_through_the_borrow_and_reading_the_owner():
    # R4 relaxed (D.123, 48.10): the owner may be read while a borrow changes it
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nfirst.color = "blue"\n'
                        'print("{@1}", fleet.len())\nprint(first.color)')
    assert errors(source) == []
    assert run(source) == ['1', 'blue']


def test_changing_the_owner_another_way_while_a_borrow_changes_it():
    # R4: one writer - changing the owner another way while the borrow is used stays an error
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nfirst.color = "blue"\n'
                        'fleet[0] = Car("green")\nprint(first.color)')
    assert any("'fleet' can't change while 'first' borrows from it" in e for e in errors(source))


def test_changing_through_the_borrow_alone_is_fine():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nfirst.color = "blue"\n'
                        'print(first.color)\nprint(fleet[0].color)')
    assert run(source) == ['blue', 'blue']


def test_another_borrow_of_the_same_owner_is_not_an_alias():
    # syntax_borrowing: 'first' ends at its last use, though 'c' borrows from fleet later
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nprint(first.color)\n'
                        'fleet.add(Car("blue"))\nfor c in fleet\n    print(c.color)')
    assert errors(source) == []


def test_a_local_given_the_borrow_extends_it():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nCar same = first\n'
                        'fleet.clear()\nprint(same.color)')
    assert any("'fleet' can't change while 'first' borrows from it" in e for e in errors(source))


# ---------- a for loop ----------

def test_a_for_loop_cant_change_its_collection():
    # a method call on it is found already (D.058, in every mode); the others here
    source = main('List<int> xs = [1, 2]\nfor x in xs\n    xs.add(x)')
    assert errors(source) == ["'xs' is being looped over - it can't change inside the loop (add); "
                              "build a new one instead"]
    # an element's value set is fine (27.2e) - unless the elements move: the loop borrows one
    assert errors(main('List<int> xs = [1, 2]\nfor x in xs\n    xs[0] = x')) == []
    source = CAR + main('List<Car> fleet = [Car("red")]\nfor c in fleet\n    fleet[0] = Car("blue")')
    assert errors(source) == ["'fleet' can't change while a for loop walks it (line 8)"]


def test_a_for_loop_variable_is_a_borrow():
    source = CAR + main('List<Car> fleet = [Car("red")]\nList<Car> keep = []\nfor c in fleet\n'
                        '    keep.add(c)')
    assert errors(source) == ["'c' borrows from 'fleet' (line 9) - a borrow can't be stored or "
                              "returned; use byVal c for a copy"]


def test_a_for_loop_keeping_copies():
    source = CAR + main('List<Car> fleet = [Car("red")]\nList<Car> keep = []\nfor c in fleet\n'
                        '    keep.add(byVal c)\nprint("{@1}", keep.len())')
    assert run(source) == ['1']


def test_the_best_one_found_in_a_loop():
    source = CAR + main('List<Car> fleet = [Car("red"), Car("blue")]\nCar best = fleet[0]\n'
                        'for c in fleet\n    if c.color == "blue"\n        best = c\nprint(best.color)')
    assert run(source) == ['blue']


# ---------- a borrow can't be stored, returned or captured (R5) ----------

def test_a_borrow_cant_be_stored():
    source = CAR + GARAGE + main('List<Car> fleet = [Car("red")]\nGarage g = Garage()\n'
                                 'Car first = fleet[0]\ng.car = first')
    assert errors(source) == ["'first' borrows from 'fleet' (line 14) - a borrow can't be stored "
                              "or returned; use byVal first for a copy"]


def test_a_borrow_of_a_local_cant_be_returned():
    # the List ends with the function - a borrow of it can't leave (of a parameter: D.109)
    source = CAR + 'Car function first()\n    List<Car> fleet = [Car("red")]\n    Car c = fleet[0]\n' \
        '    return c\n\n' + main('print(first().color)')
    assert any("'c' borrows from 'fleet'" in e for e in errors(source))


def test_a_borrow_cant_be_given_to_a_function_that_keeps_it():
    source = CAR + GARAGE + main('List<Car> fleet = [Car("red")]\nGarage g = Garage()\n'
                                 'Car first = fleet[0]\ng.park(first)')
    assert any("'first' borrows from 'fleet'" in e for e in errors(source))


@pytest.mark.parametrize('line, found', [
    ('return order.items', "'order.items' is part of 'order' and can't be moved out"),
    ('return order.items[0]', None),
])
def test_a_field_cant_be_moved_out(line, found):
    source = ORDER + f'List<int> function items()\n    Order order = Order(1, [1])\n    {line}\n\n' + \
        main('print("x")')
    if found is None:       # an int element is a copy
        source = source.replace('List<int> function', 'int function')
        assert errors(source) == []
    else:
        assert any(found in e for e in errors(source))


def test_an_element_cant_be_moved_out():
    source = CAR + main('List<Car> fleet = [Car("red")]\nList<Car> other = []\nother.add(fleet[0])')
    assert errors(source) == ["An element of 'fleet' can't be moved out - use byVal for a copy"]


# Function values can't capture variables yet (closures come later); the rule is ready for them

def test_a_stored_function_value_cant_capture_a_borrow():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\n'
                        '(int) : string f = func(int x) : first.color\nprint(f(1))')
    assert any("A function value can't capture 'first' - it borrows from 'fleet'" in e
               for e in errors(source))


def test_a_function_value_used_by_the_call_may_read_a_borrow():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\n'
                        'List<int> xs = [1, 2]\nList<int> big = xs.filter(func(int x) : first.color == "red")\n'
                        'print("{@1}", big.len())')
    assert not any("can't capture" in e for e in errors(source))


# ---------- nulls (Rule 4b) ----------

def test_without_a_null_check_a_null_borrow_is_a_null_error():
    # a List never holds null (D.139) - the null is borrowed from an object's field instead
    source = CAR + 'class Garage\n    public Car car\n\n' + main(
        'Garage g = Garage()\nCar first = g.car\ntry\n    print(first.color)\n'
        'catch NullError e\n    print("null")')
    assert run(source) == ['null']


def test_with_a_null_check_the_borrow_runs_on():
    source = CAR + 'class Garage\n    public Car car\n\n' + main(
        'Garage g = Garage()\nCar first = g.car\nif first is not null\n'
        '    print(first.color)\nprint("done")')
    assert run(source) == ['done']


# ---------- the setting ----------

def test_share_has_no_borrow_errors():
    source = CAR + main('List<Car> fleet = [Car("red")]\nCar first = fleet[0]\nfleet.clear()\n'
                        'print("{@1}", fleet.len())')
    assert errors(source, {}) == []


# ---------- a cast back to the class moves unless byVal / byRef is written (D.104) ----------

SHAPES = 'interface Shape\n    int function sides()\n\n' \
         'class Square implements Shape\n    int function sides() : 4\n\n'


@pytest.mark.parametrize('cast, moves', [
    ('Square q = (Square)s', True),
    ('Square q = byVal (Square)s', False),
    ('Square q = byRef (Square)s', False),
])
def test_a_cast_back_to_the_class(cast, moves):
    source = SHAPES + main(f'Shape s = Square()\n{cast}\nprint("{{@1}}", s.sides())')
    found = errors(source)
    assert any("'s' was moved to 'q'" in e for e in found) == moves, found


# ---------- [memory] moveFieldOut (user, 2026-11-03): off - fields are only borrowed ----------

FIELD_OUT = {'memory_config': MemoryConfig(assignment='move', move_field_out=True)}
HOLDER = CAR + 'struct Holder\n    Car car\n    int n\n\n' + GARAGE


def test_a_field_cant_be_taken_out_by_default():
    source = HOLDER + main('Holder h = Holder(Car("red"), 1)\nGarage g = Garage()\ng.park(h.car)')
    assert any("'h.car' is part of 'h' and can't be moved out" in e for e in errors(source))


def test_with_move_field_out_the_struct_is_gone_after():
    source = HOLDER + main('Holder h = Holder(Car("red"), 1)\nGarage g = Garage()\ng.park(h.car)\n'
                           'print("{h.n}")')
    found = errors(source, FIELD_OUT)
    assert found == ["'h' gave its field 'car' to 'park' (which keeps it) on line 18 - it can't be "
                     "used until it gets a new value; or use byVal h.car for a copy"], found
    fine = HOLDER + main('Holder h = Holder(Car("red"), 1)\nGarage g = Garage()\ng.park(h.car)\n'
                         'print(g.car.color)')
    assert run(fine, FIELD_OUT) == ['red']


def test_move_field_out_never_from_a_parameter():
    source = HOLDER + 'void function keep(Holder h, Garage g)\n    g.park(h.car)\n\n' + main('print("x")')
    assert any("'h.car' is part of 'h'" in e for e in errors(source, FIELD_OUT))


def test_the_setting_is_read_and_checked(tmp_path):
    from src.config.project_config import ProjectConfigError, load_project_config
    (tmp_path / 'p.fusion').write_text('')
    (tmp_path / 'fusion.toml').write_text('[memory]\nmoveFieldOut = true\n')
    assert load_project_config(str(tmp_path / 'p.fusion')).memory.move_field_out is True
    (tmp_path / 'fusion.toml').write_text('[memory]\nmoveFieldOut = "yes"\n')
    with pytest.raises(ProjectConfigError, match='moveFieldOut must be a boolean'):
        load_project_config(str(tmp_path / 'p.fusion'))


# ---------- a getter lends: its result borrows from the object (D.109, user 2026-11-03) ----------

SHOP = CAR + ('class Garage\n    public Car car\n    public List<Car> cars = []\n'
              '    Car function getCar()\n        return this.car\n'
              '    Car function at(int i)\n        return this.cars[i]\n'
              '    Car function first()\n        return this.at(0)\n\n')


def test_a_getter_lends_from_the_object():
    source = SHOP + main('Garage g = Garage()\ng.car = Car("red")\nCar c = g.getCar()\nc.color = "blue"\n'
                         'print(g.car.color)')
    assert run(source) == ['blue']            # not a copy: the change reaches the garage


def test_the_object_is_frozen_while_the_result_is_used():
    source = SHOP + main('Garage g = Garage()\ng.car = Car("red")\nCar c = g.getCar()\n'
                         'g.car = Car("blue")\nprint(c.color)')
    assert any("'g' can't change while 'c' borrows from it" in e for e in errors(source))


@pytest.mark.parametrize('call', ['g.at(0)', 'g.first()'])
def test_an_element_getter_and_one_calling_it_lend_too(call):
    source = SHOP + main(f'Garage g = Garage()\ng.cars.add(Car("red"))\nCar c = {call}\n'
                         f'g.cars.clear()\nprint(c.color)')
    assert any("'g' can't change while 'c' borrows from it" in e for e in errors(source))


def test_a_getters_result_cant_be_stored():
    source = SHOP + main('Garage g = Garage()\ng.car = Car("red")\nList<Car> all = []\nall.add(g.getCar())')
    assert errors(source) == ["getCar's result borrows from 'g' - a borrow can't be stored or "
                              "returned; use byVal for a copy"]
    copied = SHOP + main('Garage g = Garage()\ng.car = Car("red")\nList<Car> all = []\n'
                         'all.add(byVal g.getCar())\nprint("{@1}", all.len())')
    assert run(copied) == ['1']


def test_a_getter_on_a_null_object():
    # Rule 4b: without a check a NullError, with one the code runs on
    source = SHOP + main('Garage g = null\ntry\n    Car c = g.getCar()\ncatch NullError e\n    print("null")')
    assert run(source) == ['null']
    checked = SHOP + main('Garage g = null\nif g is not null\n    print(g.getCar().color)\nprint("done")')
    assert run(checked) == ['done']


def test_an_iterator_made_with_the_collection_lends_from_it():
    # D.109 (user, 2026-11-03): returning a new object made with a part of this lends this
    source = CAR + ('class Walker\n    List<Car> cars\n    int at = 0\n    constructor(List<Car> cars)\n'
                    '        this.cars = cars\n    bool function more() : at < cars.len()\n\n'
                    'class Fleet\n    public List<Car> cars = []\n'
                    '    Walker function walk() : Walker(this.cars)\n\n')
    fine = source + main('Fleet f = Fleet()\nf.cars.add(Car("red"))\nWalker w = f.walk()\nprint("{@1}", w.more())')
    assert run(fine) == ['true']
    frozen = source + main('Fleet f = Fleet()\nWalker w = f.walk()\nf.cars.clear()\nprint("{@1}", w.more())')
    assert any("'f' can't change while 'w' borrows from it" in e for e in errors(frozen))
    stored = source + main('Fleet f = Fleet()\nList<Walker> all = []\nall.add(f.walk())')
    assert any("walk's result borrows from 'f'" in e for e in errors(stored))
