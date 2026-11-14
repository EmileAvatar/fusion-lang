"""Task 52.10 - a List or Map never holds null (D.138, D.139).

A null written in the code is a compile error (D.086); a variable that turns out null while the
program runs is refused with a NullError a `catch` handles, and nothing is stored or leaked (every
program here runs under the leak check). With and without a null check (Rule 4b).
"""
import pytest

from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main

CAR = 'class Car\n    public int n = 1\n\n'


@pytest.mark.parametrize('body, message', [
    ('List<Car> xs = []\nxs.add(null)', 'A List never holds null - add an object (D.139)'),
    ('List<Car> xs = []\nxs.insert(0, null)', 'A List never holds null - add an object (D.139)'),
    ('List<Car> xs = [Car(), null]', 'A List never holds null'),
    ('List<Car> xs = [Car()]\nxs[0] = null', 'A List never holds null - set an object (D.139)'),
    ('Map<string, Car> m = Map<string, Car>()\nm["a"] = null', 'A Map never holds null - set an object (D.139)'),
    ('List<int> xs = null', "List<int> can't be null"),
    ('string s = null', "A string can't be null"),
])
def test_a_written_null_is_a_compile_error(body, message):
    assert message in errors_of(CAR + main(body))


def test_a_list_literal_adds_each_item():
    assert run(CAR + main('Car a = Car()\nCar b = Car()\nList<Car> xs = [a, b]\nprint("{@1}", xs.len())')) == ['2']


def test_a_null_added_while_running_is_a_null_error():
    # Rule 4b: no check - the NullError is caught, nothing added
    assert run(CAR + main('List<Car> xs = []\nCar c = null\ntry\n    xs.add(c)\ncatch e\n    print("caught")\n'
                          'print("{@1}", xs.len())')) == ['caught', '0']


def test_a_null_set_or_put_while_running_is_a_null_error():
    assert run(CAR + main('List<Car> xs = [Car()]\nMap<string, Car> m = Map<string, Car>()\n'
                          'Car c1 = null\ntry\n    xs[0] = c1\ncatch e\n    print("caught set")\n'
                          'Car c2 = null\ntry\n    m["k"] = c2\ncatch e\n    print("caught put")\n'
                          'print("{@1} {@2}", xs.len(), m.len())')) == ['caught set', 'caught put', '1 0']


def test_a_null_item_in_a_list_literal_while_running_frees_the_others():
    assert run(CAR + main('Car a = Car()\nCar c = null\ntry\n    List<Car> ys = [a, c]\n'
                          '    print("{@1}", ys.len())\ncatch e\n    print("caught")')) == ['caught']


def test_with_a_null_check_nothing_is_added():
    # Rule 4b: checked first - the code runs on
    assert run(CAR + main('List<Car> xs = []\nCar c = null\nif c is null\n    print("skipped")\nelse\n'
                          '    xs.add(c)\nprint("{@1}", xs.len())')) == ['skipped', '0']


def test_no_null_option_is_still_accepted():
    # noNull() (32.14) is what every List / Map does now - writing it is harmless
    assert run(CAR + main('List<Car> xs = [] { xs.noNull() }\nxs.add(Car())\nprint("{@1}", xs.len())')) == ['1']
