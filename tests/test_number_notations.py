"""Task 47.9 - number notations (D.195, D.196).

    double g = 6.67e-11          // exponents - 1e6, 5.976E24, 1.5e3f
    decimal d = 1.25e2           // 125.00 - the places written kept, a negative exponent adds places
    long big = 0xFFFF_FFFF_FFFF  // hex / binary / octal past 32 bits: a long, int128, int256
    let price = 19.99m           // m money, dec decimal - the type in the value
    double half = .5             // error: write 0.5
    Double.MAX, Float.NAN        // the special values by name

Every program runs under the leak check.
"""
import pytest

from src.lexer import Lexer
from src.lexer.literals import decimal_digits, parse_float, split_number
from src.parser.parser import ParserError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main, parse


def run(body: str) -> list:
    code, out, err = compile_and_run(main(body))
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


# ---- the lexer ----

@pytest.mark.parametrize('text, read', [
    ('6.67e-11', '6.67e-11'), ('5.976E24', '5.976E24'), ('1e6', '1e6'), ('1.5e3f', '1.5e3f'), ('2.5E+3d', '2.5E+3d'),
    ('19.99m', '19.99m'), ('0.155dec', '0.155dec'), ('5m', '5m'), ('3dec', '3dec'), ('1_000.5e2', '1_000.5e2'),
])
def test_the_lexer_reads(text, read):
    assert parse_float(text + ' ', 0) == (read, len(read))


@pytest.mark.parametrize('text', ['5', '5min', '5d', '255.toHex()', '1...10', '2else'])
def test_not_a_decimal_number(text):
    assert parse_float(text, 0) is None or parse_float(text, 0)[0] != text


@pytest.mark.parametrize('written, digits', [
    ('1.25e2', (12500, 2)), ('1.5e-3', (15, 4)), ('19.99m', (1999, 2)), ('5m', (5, 0)), ('0.155dec', (155, 3)),
    ('1e6', (1000000, 0)), ('2.50', (250, 2)),
])
def test_decimal_digits_keep_the_places(written, digits):
    assert decimal_digits(written) == digits


def test_split_number():
    assert split_number('6.67E-11f') == ('6', '67', -11, 'f')


@pytest.mark.parametrize('source, message', [
    ('double x = 5.\n', 'write 5.0'), ('double x = .5\n', 'write 0.5'), ('double x = 3 * .25\n', 'write 0.25'),
])
def test_a_digit_on_both_sides_of_the_point(source, message):
    lexer = Lexer('void function main()\n    ' + source, 't')
    with pytest.raises(Exception, match=message):
        lexer.tokenize()
        assert not lexer.diagnostics.errors
    assert True


@pytest.mark.parametrize('source, message', [
    ('double x = 1e400', "past a double's range"), ('double x = 1e-400', 'too small for a double'),
    ('float x = 1e39f', "past a float's range"),
])
def test_out_of_range_is_an_error(source, message):
    with pytest.raises(ParserError, match=message):
        parse(main(source))


# ---- the values ----

def test_exponents():
    assert run('double g = 6.67e-11\nprint("{@1}", g * 1e11 > 6.6)\nfloat f = 1.5e3f\nprint("{@1}", f)\n'
               'double big = 1e300\nprint("{@1}", big > 1e299)') == ['true', '1500.000000', 'true']


def test_exponents_in_decimals_keep_their_places():
    assert run('decimal d = 1.25e2\ndecimal small = 1.5e-3\nmoney m = 2.5e1\nprint("{d} {small} {m}")') == [
        '125.00 0.0015 25.0']


def test_hex_past_32_bits():
    assert run('long h = 0xFFFF_FFFF_FFFF\nint128 w = 0x1_0000_0000_0000_0000\nprint("{h} {w} {@1}", 0xFFFFFFFF)') == [
        '281474976710655 18446744073709551616 -1']


def test_suffixes_give_the_type():
    assert run('let price = 19.99m\nlet rate = 0.155dec\nlet whole = 5m\nmoney total = price + 0.01m\n'
               'print("{price} {rate} {whole} {total} {@1}", -2.50m)') == ['19.99 0.155 5 20.00 -2.50']


def test_a_suffix_where_another_type_is_wanted():
    assert any('Cannot assign money to variable of type int' in e for e in [errors_of(main('int x = 19.99m'))])


def test_the_named_special_values():
    assert run('double top = Double.MAX\nprint("{@1} {@2}", top > 1e308, Double.MIN < -1e308)\n'
               'print("{@1} {@2}", Double.EPSILON < 1e-15, Float.EPSILON > 1e-8)\n'
               'double inf = Double.INFINITY\nprint("{@1} {@2}", inf > top, Double.NAN == Double.NAN)') == [
        'true true', 'true true', 'true false']


def test_an_unknown_special_value():
    assert "Double has no value 'BIG'" in errors_of(main('double x = Double.BIG'))
