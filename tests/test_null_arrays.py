"""Task 52.11 - an array slot of an object type may be null (D.140).

`Car[] cars = [car1, null, car3]`, `Car[] slots = [null, null, null]`, `cars[0] = null` frees the
object it held; an array of numbers never holds null; an element of the wrong type is an error.
Every program runs under the leak check. With and without a null check (Rule 4b).
"""
import pytest

from tests.test_ownership_moves import run
from tests.test_structs import errors_of, main

CL = 'class Car\n    public int n = 1\nclass Truck\n    public int n = 2\n\n'


def test_a_null_slot_in_a_literal():
    assert run(CL + main('Car[] cars = [Car(), null, Car()]\nprint("{@1}", cars.len())')) == ['3']


def test_every_slot_null_takes_the_declared_type():
    assert run(CL + main('Car[] slots = [null, null, null]\nslots[1] = Car()\nprint("{@1}", slots[1].n)')) == ['1']


def test_setting_a_slot_to_null_frees_the_object():
    # the leak check would fail (exit 5) if the car were never freed
    assert run(CL + main('Car[] cars = [Car(), Car()]\ncars[0] = null\nprint("done")')) == ['done']


def test_without_a_null_check_a_null_slot_is_a_null_error():
    assert run(CL + main('Car[] cars = [null, Car()]\ntry\n    print("{@1}", cars[0].n)\ncatch e\n'
                         '    print("caught")')) == ['caught']


def test_with_a_null_check_the_code_runs_on():
    assert run(CL + main('Car[] cars = [null, Car()]\nif cars[0] is null\n    print("empty slot")\n'
                         'print("{@1}", cars[1].n)')) == ['empty slot', '1']


@pytest.mark.parametrize('body, message', [
    ('int[] xs = [1, null, 3]', "A int array slot can't be null - only an array of objects or enums may hold null (D.140)"),
    ('int[] xs = [null, null]', "A int array slot can't be null"),
    ('Car[] cars = [Car(), Truck()]', 'Array elements must have consistent types'),
])
def test_refused(body, message):
    assert message in errors_of(CL + main(body))
