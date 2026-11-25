"""Task 47.8 - `decimal`: an exact base-10 number - a whole number and its scale (D.182).

    decimal price = 100.05          // a written number keeps its places exactly - never a double
    decimal sum = price + 200.125   // + - always exact, the larger scale kept: 300.175
    decimal third = 1.00 / 3        // a division that doesn't end: 18 places, rounded once ([numbers] rounding)
    round(x, 2, halfUp)             // the mode named (the built-in enum Rounding), or the project's

The value is an int128 (38 digits), every step in between an int256 (D.178). Every program runs under the leak check.
"""

import pytest

from src.config.project_config import load_project_config
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main


def run(source: str, **options) -> list:
    code, out, err = compile_and_run(source, **options)
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def show(value: str) -> str:
    return f'print("{{@1}}", {value})'


# ---------------------------------------------------------------- exact

def test_exact_addition_and_places_kept():
    assert run(main('decimal a = 0.1\ndecimal b = 0.2\ndecimal c = a + b\nprint("{c} {@1}", c == 0.3)\n'
                    'decimal p = 100.05\n' + show('p + 200.125') + '\n' + show('p - 0.05') + '\n' + show('-p'))) == [
        '0.3 true', '300.175', '100.00', '-100.05']


def test_multiply_adds_the_scales():
    assert run(main('decimal p = 100.05\n' + show('p * 1.155') + '\n' + show('p * 3') + '\n'
                    'decimal one = 2 * 0.5\nprint("{one}")')) == [
        '115.55775', '300.15', '1.0']


def test_divide_exact_when_it_ends_else_18_places():
    # written numbers alone are floats; stored as a decimal they are worked out as decimals
    assert run(main('decimal a = 10.00 / 4\ndecimal b = 1 / 8.0\ndecimal c = 1.00 / 3\ndecimal two = 2.0\n'
                    'print("{a}")\nprint("{b}")\nprint("{c}")\n' + show('two / 3'))) == [
        '2.50', '0.125', '0.333333333333333333', '0.666666666666666667']


def test_comparing_by_amount():
    assert run(main('decimal a = 1.50\ndecimal b = 1.5\nprint("{@1} {@2} {@3} {@4}", a == b, a < 1.51, a >= 2, a != 0)')) == [
        'true true false true']


def test_a_number_declared_without_a_value_is_zero():
    assert run(main('decimal z\nprint("{z}")')) == ['0']


# ---------------------------------------------------------------- rounding (D.177)

@pytest.mark.parametrize('mode, values', [
    ('halfEven', ['2', '-2', '3', '2']),
    ('halfUp', ['3', '-3', '3', '2']),
    ('down', ['2', '-2', '2', '2']),
    ('up', ['3', '-3', '3', '3']),
])
def test_rounding_modes(mode, values):
    assert run(main(f'print("{{@1}} {{@2}} {{@3}} {{@4}}", round(2.5, 0, {mode}), round(-2.5, 0, {mode}), '
                    f'round(2.51, 0, {mode}), round(2.1, 0, {mode}))')) == [' '.join(values)]


def test_round_and_divide_with_places_and_the_method_form():
    assert run(main('decimal v = 115.55775\nprint("{@1} {@2} {@3}", round(v, 2), v.round(3, halfUp), round(v, 6))\n'
                    + show('divide(10.00, 3, 4, down)') + '\n' + show('divide(2.0, 3, 2)'))) == [
        '115.56 115.558 115.557750', '3.3333', '0.67']


def test_exact_mode_is_a_rounding_error():
    assert run(main('decimal third = 1.00 / 3\ntry\n    decimal e = round(third, 2, exact)\n    print("{e}")\n'
                    'catch RoundingError e\n    print(e.message)\n' + show('round(2.50, 1, exact)'))) == [
        'the result needs rounding to 2 places - the rounding is exact', '2.5']


def test_the_project_rounding_setting(tmp_path):
    (tmp_path / 'fusion.toml').write_text('[numbers]\nrounding = "halfUp"\n', encoding='utf-8')
    assert load_project_config(str(tmp_path / 'fusion.toml')).numbers.rounding == 'halfUp'
    from src.config.project_config import NumbersConfig
    assert NumbersConfig().rounding == 'halfEven'
    (tmp_path / 'b').mkdir()
    (tmp_path / 'b' / 'fusion.toml').write_text('[numbers]\nrounding = "nearest"\n', encoding='utf-8')
    with pytest.raises(Exception, match='numbers.rounding must be one of'):
        load_project_config(str(tmp_path / 'b' / 'fusion.toml'))


def test_the_setting_changes_a_division():
    source = main(show('round(2.5, 0)') + '\ndecimal d = 2.0 / 3\nprint("{d}")')
    assert run(source) == ['2', '0.666666666666666667']
    assert run(source, rounding='down') == ['2', '0.666666666666666666']


# ---------------------------------------------------------------- conversions and errors

def test_conversions():
    assert run(main('decimal t = toDecimal("-12.50")\nint whole = 7\ndecimal w = whole\nlong big = 9000000000000000000\n'
                    'decimal b = big\nprint("{t} {w} {b}")\n' + show('toDouble(1.00 / 4) == 0.25') + '\n'
                    'try\n    decimal x = toDecimal("1.2.3")\n    print("{x}")\ncatch NumberFormatError e\n    print(e.message)')) == [
        '-12.50 7 9000000000000000000', 'true',
        "'1.2.3' is not a decimal number (up to 38 digits, 18 after the point)"]


def test_a_float_never_becomes_a_decimal_by_itself():
    assert "can't become a decimal exactly" in errors_of(main('double d = 1.5\ndecimal x = d'))
    assert "can't become a decimal exactly" in errors_of(main('decimal a = 1.5\nfloat f = 2.0\ndecimal b = a + f'))
    assert 'Cannot assign decimal to variable of type double' in errors_of(main('decimal a = 1.5\ndouble d = a'))
    assert "'%' isn't defined on a decimal" in errors_of(main('decimal a = 1.5\ndecimal b = a % 2'))
    assert 'a decimal holds up to 18' in errors_of(main('decimal a = 0.1234567890123456789'))


def test_overflow_and_division_by_zero():
    big = '9' * 37 + '.5'
    assert run(main(f'decimal a = {big}\ntry\n    decimal b = a * 1000\n    print("{{b}}")\ncatch OverflowError e\n'
                    '    print(e.message)\ntry\n    decimal z = 0\n    print("{@1}", a / z)\ncatch DivideByZeroError e\n'
                    '    print("by zero")')) == ["the product doesn't fit in a decimal (38 digits)", 'by zero']


# ---------------------------------------------------------------- in every place a type goes

def test_in_structs_functions_collections_and_text():
    source = ('struct Item\n    string name\n    decimal price\n\n'
              'decimal function total(List<Item> items)\n    decimal sum = 0\n    foreach it in items\n'
              '        sum = sum + it.price\n    return sum\n\nT function first<T>(List<T> xs) : xs[0]\n\n'
              + main('List<Item> items = [Item("tea", 12.50), Item("cake", 4.25)]\n' + show('total(items)') + '\n'
                     + show('items[0]') + '\nList<decimal> ds = [1.5, 2.25]\nds.add(0.125)\n'
                     'print("{@1} {@2}", ds[2], ds.contains(2.250))\nMap<string, decimal> m\nm["a"] = 9.99\n'
                     + show('m["a"]') + '\n' + show('first(ds)') + '\ndecimal[2] arr = [1.1, 2.2]\n'
                     + show('arr[0] + arr[1]') + '\nprint(toString(arr[1]))\nprint(items.toCSV())'))
    assert run(source) == ['16.75', 'name : "tea",price : 12.50', '0.125 true', '9.99', '1.5', '3.3', '2.2',
                           'Item.name,Item.price', '"tea",12.50', '"cake",4.25']
