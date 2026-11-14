"""Task 48.12 - storing `this` shares the object, counted (D.103).

`cars.add(this)` inside a method: the object is held by every collection it is added to (one car,
not copies); a change through one holder is seen through the others; it is freed when the last
holder lets go. Every program here runs under the leak check - exit 5 if an object is never freed.
With and without a null check (CLAUDE.md Rule 4b).
"""
from tests.test_ownership_moves import run
from tests.test_structs import main

CAR = ('class Car\n'
       '    public string name\n'
       '    constructor(string n)\n'
       '        this.name = n\n\n'
       '    void function register(List<Car> a, List<Car> b)\n'
       '        a.add(this)\n'
       '        b.add(this)\n\n')


def test_one_object_in_two_collections():
    source = CAR + main('List<Car> fleet = List<Car>()\nList<Car> sold = List<Car>()\n'
                        'Car c = Car("Mini")\nc.register(fleet, sold)\n'
                        'fleet[0].name = "Cooper"\n'
                        'print("{@1} {@2} {@3}", sold[0].name, c.name, fleet.len())')
    assert run(source) == ['Cooper Cooper 1']


def test_still_alive_while_one_holder_keeps_it():
    # the first holder lets go - the second still has the car, then it lets go too: freed (leak check)
    source = CAR + main('List<Car> fleet = List<Car>()\nList<Car> sold = List<Car>()\n'
                        'Car c = Car("Mini")\nc.register(fleet, sold)\n'
                        'fleet.clear()\nprint(sold[0].name)\nsold.clear()\nprint("{@1}", sold.len())')
    assert run(source) == ['Mini', '0']


def test_storing_this_in_a_loop_shares_each_object():
    source = CAR + main('List<Car> fleet = List<Car>()\nList<Car> sold = List<Car>()\n'
                        'for name in ["a", "b", "c"]\n    Car c = Car(name)\n    c.register(fleet, sold)\n'
                        'sold[1].name = "B"\nprint(fleet[1].name)')
    assert run(source) == ['B']


def test_without_a_null_check_a_null_object_is_a_null_error():
    # Rule 4b: no check - the call on null is a NullError, caught
    source = CAR + main('List<Car> fleet = List<Car>()\nList<Car> sold = List<Car>()\nCar c = null\n'
                        'try\n    c.register(fleet, sold)\ncatch e\n    print("caught")\n'
                        'print("{@1}", fleet.len())')
    assert run(source) == ['caught', '0']


def test_with_a_null_check_nothing_is_stored():
    # Rule 4b: a null check - nothing stored, no error (`c?.register(...)` once 30.2 builds `?.` calls)
    source = CAR + main('List<Car> fleet = List<Car>()\nList<Car> sold = List<Car>()\nCar c = null\n'
                        'if c is null\n    print("no car")\nelse\n    c.register(fleet, sold)\n'
                        'print("{@1} {@2}", fleet.len(), sold.len())')
    assert run(source) == ['no car', '0 0']


# ---------- Rule 4b for moves and borrows (48.7): a null value moved or borrowed ----------

def test_a_moved_null_without_a_check_is_a_null_error():
    source = CAR + main('Car a = null\nCar b = a\ntry\n    print(b.name)\ncatch e\n    print("caught")')
    assert run(source) == ['caught']


def test_a_moved_null_with_a_check_runs_on():
    source = CAR + main('Car a = null\nCar b = a\nif b is null\n    print("no car")\nelse\n    print(b.name)')
    assert run(source) == ['no car']


def test_a_borrowed_null_element_without_and_with_a_check():
    source = CAR + main('List<Car> fleet = [Car("Mini")]\nfleet[0] = null\nCar first = fleet[0]\n'
                        'if first is null\n    print("empty slot")\n'
                        'try\n    print(first.name)\ncatch e\n    print("caught")')
    assert run(source) == ['empty slot', 'caught']
