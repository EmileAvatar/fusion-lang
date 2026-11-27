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
    ('int x = JUNE', 'Cannot assign Months to variable of type int'),
    ('Months m = APRIL', "Undefined variable: 'APRIL'"),
])
def test_wrong_uses(body, message):
    assert message in errors_of(MONTHS + main(body))


def test_a_value_of_another_enum():
    errors = errors_of(MONTHS + 'enum Color: RED GREEN\n\n' + main('Months m = RED'))
    assert 'Cannot assign Color to variable of type Months' in errors


# ---- 47.10 (D.197): a value's name alone anywhere ----

def test_alone_anywhere_when_one_enum_has_it():
    assert run(MONTHS + main('print(toString(JUNE))\nprint("{@1} {@2}", JUNE, toString(MARCH))\nstring s = "{JUNE}"\n'
                             'print(s)')) == ['JUNE', 'JUNE MARCH', 'JUNE']


def test_alone_in_any_expression():
    source = 'enum Status\n    200, OK\n    403, FORBIDDEN\n\n'
    assert run(source + main('int code = OK.value() + 1\nList<Status> all = [OK, FORBIDDEN]\n'
                             'print("{@1} {@2}", code, all[1])')) == ['201 FORBIDDEN']


def test_two_enums_with_the_name():
    errors = errors_of('enum Light: RED GREEN\nenum Color: RED BLUE\n\n' + main('print(RED)'))
    assert "'RED' is Light.RED or Color.RED - write which" in errors, errors


def test_the_expected_enum_still_decides():
    # D.150 - where the type is known, the enum expected picks, though Color has RED too
    assert run('enum Light: RED GREEN\nenum Color: RED BLUE\n\n' + main('Light l = RED\nprint("{l} {@1}", l == Light.RED)')) \
        == ['RED true']


@pytest.mark.parametrize('top, body', [
    ('', 'int JUNE = 3\nprint(JUNE)'),
    ('const int JUNE = 3\n', 'print(JUNE)'),
])
def test_shared_with_a_variable_or_constant(top, body):
    errors = errors_of(MONTHS + top + main(body))
    assert "'JUNE' is Months.JUNE or the" in errors and 'write the enum' in errors, errors


def test_a_variable_named_like_a_value_of_an_enum_the_compiler_added():
    # Rounding (47.8) is added because `down` appears - the program's own variable wins, no error
    assert run(main('int down = -4\nfor i in 10...1 step down\n    print("{i}")\nprint("{@1}", round(toDecimal("2.5"), 0, halfUp))')) \
        == ['10', '6', '2', '3']


def test_full_name_is_always_fine():
    assert run(MONTHS + main('int JUNE = 3\nprint("{@1}", Months.JUNE)')) == ['JUNE']
