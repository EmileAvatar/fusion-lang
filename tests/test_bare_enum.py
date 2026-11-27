"""Task 47.11 - an enum value is written with its enum (D.199 - replaces D.150 / D.197).

`Status.OK` everywhere; in a match on an enum a case may be `case OK` or `case Status.OK` - the subject's type decides,
even when another enum has an OK. A value alone anywhere else is an error saying what to write, and a variable named
like a value is simply that variable.
"""
import pytest

from tests.test_foreach import run
from tests.test_structs import errors_of, main

MONTHS = 'enum Months: JANUARY FEBRUARY MARCH JUNE\n\n'
SHOW = 'void function show(Months m)\n    print("{m}")\n\n'


def test_the_full_name_everywhere():
    body = ('show(Months.JUNE)\nMonths m = Months.FEBRUARY\nshow(m)\nm = Months.JANUARY\n'
            'print("{@1} {@2} {Months.MARCH}", m == Months.JANUARY, toString(Months.JUNE))')
    assert run(MONTHS + SHOW + main(body)) == ['JUNE', 'FEBRUARY', 'true JUNE MARCH']


def test_a_match_takes_either_form():
    body = ('Months m = Months.MARCH\nmatch m\n    case JUNE: print("june")\n    case Months.MARCH: print("march")\n'
            '    else: print("other")\nstring s = match m { JANUARY, Months.MARCH : "early", _ : "late" }\nprint(s)')
    assert run(MONTHS + main(body)) == ['march', 'early']


def test_a_match_decides_even_when_another_enum_has_the_name():
    source = 'enum Size: SMALL LARGE\n\nenum Cup: SMALL TALL\n\n'
    assert run(source + main('Cup c = Cup.SMALL\nmatch c\n    case SMALL: print("small cup")\n    case TALL: print("tall")')) \
        == ['small cup']


@pytest.mark.parametrize('body', [
    'show(JUNE)', 'Months m = JUNE', 'Months m = Months.MARCH\nm = JUNE', 'Months m = Months.MARCH\nprint("{@1}", m == JUNE)',
    'print("{@1}", JUNE)', 'string s = "{JUNE}"',
])
def test_a_value_alone_is_an_error(body):
    assert "'JUNE' is an enum value - write Months.JUNE" in errors_of(MONTHS + SHOW + main(body))


def test_a_value_alone_of_two_enums():
    errors = errors_of('enum Light: RED GREEN\nenum Color: RED BLUE\n\n' + main('print("{@1}", RED)'))
    assert "'RED' is an enum value - write Light.RED or Color.RED" in errors, errors


def test_a_case_of_another_enum():
    errors = errors_of('enum Light: RED GREEN\nenum Color: RED BLUE\n\n'
                       + main('Light l = Light.RED\nmatch l\n    case Color.RED: print("x")\n    else: print("y")'))
    assert 'This match is on Light - write case RED or case Light.RED' in errors, errors


def test_a_variable_named_like_a_value_is_that_variable():
    assert run(MONTHS + main('int JUNE = 3\nprint("{@1} {@2}", JUNE, Months.JUNE)')) == ['3 JUNE']


def test_a_variable_named_like_a_value_of_a_built_in_enum():
    # Rounding (47.8) is added because `down` appears - the program's variable is its own
    assert run(main('int down = -4\nfor i in 10...1 step down\n    print("{i}")\n'
                    'print("{@1}", round(toDecimal("2.5"), 0, Rounding.halfUp))')) == ['10', '6', '2', '3']


def test_a_null_enum_compared():
    # Rule 4b: an unset enum is null (D.051) - comparing it with a value is false, no error
    assert run(MONTHS + main('Months m = null\nprint("{@1}", m == Months.JUNE)')) == ['false']


def test_an_unknown_value():
    assert "Undefined variable: 'APRIL'" in errors_of(MONTHS + main('Months m = APRIL'))
