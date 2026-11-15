"""Task 45.17 - an enum value written alone where the enum type is known (D.150).

`setMonth(JUNE)`, `Months m = JUNE`, `m = JUNE`, `return JUNE`, `m == JUNE`, `JUNE == m` and a match's
`case JUNE` are the same as `Months.JUNE`. Anywhere else the full name is needed. A variable with
the same name there is a compile error - nothing is chosen silently.
"""
import pytest

from tests.test_foreach import run
from tests.test_structs import errors_of, main

MONTHS = 'enum Months: JANUARY FEBRUARY MARCH JUNE\n\n'
SHOW = 'void function show(Months m)\n    print("{m}")\n\n'
PICK = 'Months function pick(bool late)\n    if late\n        return JUNE\n    return Months.MARCH\n\n'


def test_where_the_type_is_known():
    body = ('show(JUNE)\nMonths m = FEBRUARY\nshow(m)\nm = JANUARY\nshow(m)\n'
            'print("{@1} {@2} {@3}", m == JANUARY, JUNE == pick(true), m != MARCH)\n'
            'match pick(false)\n    case JUNE: print("june")\n    case MARCH: print("march")\n    else: print("other")')
    assert run(MONTHS + SHOW + PICK + main(body)) == ['JUNE', 'FEBRUARY', 'JANUARY', 'true true true', 'march']


def test_the_full_name_still_works():
    assert run(MONTHS + SHOW + main('show(Months.JUNE)\nMonths m = Months.MARCH\nshow(m)')) == ['JUNE', 'MARCH']


def test_two_enums_with_the_same_value_name():
    source = 'enum Size: SMALL LARGE\n\nenum Cup: SMALL TALL\n\nvoid function pour(Cup c)\n    print("{c}")\n\n'
    assert run(source + main('Size s = SMALL\npour(SMALL)\nprint("{s}")')) == ['SMALL', 'SMALL']


def test_a_null_enum_compared():
    # Rule 4b: an unset enum is null (D.051) - comparing it with a value is false, no error
    assert run(MONTHS + main('Months m = null\nprint("{@1}", m == JUNE)')) == ['false']


@pytest.mark.parametrize('body, message', [
    ('Months JUNE = Months.MARCH\nMonths m = JUNE',
     "'JUNE' is both a variable and a Months value - write Months.JUNE for the value, or rename the variable"),
    ('print("{@1}", JUNE)', "'JUNE' alone is an enum value only where that enum is expected"),
    ('int x = JUNE', 'here write Months.JUNE'),
    ('Months m = APRIL', "Undefined variable: 'APRIL'"),
])
def test_wrong_uses(body, message):
    assert message in errors_of(MONTHS + main(body))


def test_a_value_of_another_enum():
    errors = errors_of(MONTHS + 'enum Color: RED GREEN\n\n' + main('Months m = RED'))
    assert 'here write Color.RED' in errors
