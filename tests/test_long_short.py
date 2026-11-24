"""Task 47.1 - `long` (64 bits) and `short` (16 bits) as types.

    long big = 5000000000         // a whole number past an int's range is a long
    long sum = big + 7            // an int with a long gives a long; int -> long widens by itself
    short s = 300                 // an int literal -32768...32767 may be stored as a short
    int back = toInt(sum - big)   // long -> int / short only written, checked: an OverflowError (D.003)

Arithmetic is checked as an int's is ([numbers] overflowWrap the same); a short's arithmetic gives an int
(as a byte's does). Every program runs under the leak check.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import analyze, errors_of, main


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def accepted(source: str) -> bool:
    return analyze(source)[2]


def catching(body: str, error: str = 'OverflowError') -> str:
    """`body` inside a try that prints the error's message."""
    inner = '\n'.join('    ' + line for line in body.splitlines())
    return f'try\n{inner}\ncatch {error} e\n    print(e.message)'


def show(value: str) -> str:
    return f'print("{{@1}}", {value})'


# ---------------------------------------------------------------- values, limits, printing

def test_long_literals_limits_and_printing():
    assert run(main('long big = 5000000000\nlong top = 9223372036854775807\nlong low = -9223372036854775808\n'
                    'print("{big} {top} {low}")\nprint(toString(big))\nprint(format("{@1}", top))\n'
                    'long small = 7\nprint("{small}")')) == [
        '5000000000 9223372036854775807 -9223372036854775808', '5000000000', '9223372036854775807', '7']


def test_short_literals_limits_and_printing():
    assert run(main('short a = 32767\nshort b = -32768\nprint("{a} {b}")\nprint(toString(a))')) == [
        '32767 -32768', '32767']


def test_int_limits_still_work():
    assert run(main('int low = -2147483648\nint top = 2147483647\nprint("{low} {top}")')) == [
        '-2147483648 2147483647']


def test_a_literal_past_a_long_is_an_error():
    assert "doesn't fit in a long" in errors_of(main('long x = 9223372036854775808'))


def test_a_long_literal_is_not_an_int():
    assert 'Cannot assign long to variable of type int' in errors_of(main('int x = 5000000000'))


def test_a_short_takes_only_a_literal_that_fits():
    assert errors_of(main('short a = 32768'))
    assert errors_of(main('int i = 5\nshort a = i'))          # an int variable: toShort(i)
    assert accepted(main('int i = 5\nshort a = toShort(i)'))
    assert accepted(main('short a = -32768\nbyte b = 200'))
    assert errors_of(main('byte b = -1'))                     # a minus still never makes a byte


# ---------------------------------------------------------------- widening and mixed arithmetic

def test_int_widens_to_long_and_mixed_gives_long():
    assert run(main('int i = 2000000000\nlong a = i\nlong b = a + i\nlong c = i * 3000000000\n'
                    'print("{a} {b} {c}")')) == ['2000000000 4000000000 6000000000000000000']


def test_a_long_never_narrows_by_itself():
    assert 'Cannot assign long to variable of type int' in errors_of(main('long a = 5\nint i = a'))


def test_short_arithmetic_gives_an_int():
    assert run(main('short a = 30000\nshort b = 30000\nint c = a + b\n' + show('c'))) == ['60000']
    assert errors_of(main('short a = 1\nshort b = 2\nshort c = a + b'))


def test_long_comparisons_and_equality():
    assert run(main('long a = 5000000000\nint i = 5\nprint("{@1} {@2} {@3} {@4}", a > i, a == 5000000000, '
                    'i < a, a != a)')) == ['true true true false']


def test_long_division_and_remainder():
    assert run(main('long a = 10000000007\nlong b = 10\nprint("{@1} {@2}", a / b, a % b)\n'
                    + catching('long z = 0\n' + show('a / z'), 'DivideByZeroError'))) == [
        '1000000000 7', '10000000007 / 0: division by zero']


# ---------------------------------------------------------------- overflow, checked

@pytest.mark.parametrize('expression, message', [
    ('top + 1', "9223372036854775807 + 1 doesn't fit in a long"),
    ('low - 1', "-9223372036854775808 - 1 doesn't fit in a long"),
    ('top * 2', "9223372036854775807 * 2 doesn't fit in a long"),
    ('-low', "-(-9223372036854775808) doesn't fit in a long"),
    ('low / -1', "-9223372036854775808 / -1 doesn't fit in a long"),
])
def test_long_overflow_is_an_error(expression, message):
    assert run(main('long top = 9223372036854775807\nlong low = -9223372036854775808\n'
                    + catching(f'long r = {expression}\n' + show('r')))) == [message]


def test_long_overflow_wraps_when_asked():
    assert run(main('long top = 9223372036854775807\nunchecked\n    long r = top + 1\n    ' + show('r'))) == [
        '-9223372036854775808']


# ---------------------------------------------------------------- conversions

def test_toInt_and_toShort_of_a_long_check_the_range():
    assert run(main('long a = 70000\nint i = toInt(a)\n' + show('i') + '\n'
                    + catching('short s = toShort(a)\n' + show('s')) + '\n'
                    + catching('long big = 5000000000\n' + show('toInt(big)')))) == [
        '70000', "70000 doesn't fit in a short (-32768 to 32767)",
        "5000000000 doesn't fit in an int (-2147483648 to 2147483647)"]


def test_toShort_of_an_int():
    assert run(main('int i = -300\nshort s = toShort(i)\n' + show('s') + '\n'
                    + catching('short t = toShort(40000)\n' + show('t')))) == [
        '-300', "40000 doesn't fit in a short (-32768 to 32767)"]


def test_toLong_from_text_and_from_an_int():
    assert run(main('long a = toLong("-9223372036854775808")\nlong b = toLong(12)\nprint("{a} {b}")\n'
                    + catching('long c = toLong("9223372036854775808")\n' + show('c'), 'NumberFormatError') + '\n'
                    + catching('long d = toLong("12x")\n' + show('d'), 'NumberFormatError'))) == [
        '-9223372036854775808 12',
        "'9223372036854775808' is not a whole number that fits in a long",
        "'12x' is not a whole number that fits in a long"]


def test_toShort_from_text():
    assert run(main('short a = toShort("-123")\n' + show('a'))) == ['-123']


def test_a_long_as_a_double_must_fit_exactly():
    assert run(main('long a = 9007199254740992\ndouble d = a\n' + show('d > 0.0') + '\n'
                    + catching('long b = 9007199254740993\ndouble e = b\n' + show('e'), 'PrecisionError'))) == [
        'true', "9007199254740993 can't be stored exactly in a double (it would become 9007199254740992) - "
                "set [numbers] autoWidening = true to allow it"]


def test_a_written_long_that_a_double_cannot_hold_is_an_error():
    assert "can't be stored exactly in a double" in errors_of(main('double d = 9007199254740993'))


# ---------------------------------------------------------------- in every place a type goes

def test_long_and_short_in_functions_structs_arrays_and_collections():
    source = ('long function twice(long n) : n * 2\n\n'
              'struct Account\n    long cents\n    short year\n\n'
              + main('Account a = Account(5000000000, 2026)\nprint("{@1} {@2}", twice(a.cents), a.year)\n'
                     'long[3] xs = [1, 5000000000, 3]\n' + show('xs[1]') + '\n'
                     'List<long> ys = [9000000000, 2]\nys.add(3)\nlong total = 0\nforeach y in ys\n'
                     '    total = total + y\n' + show('total') + '\n'
                     'Map<string, long> m\nm["a"] = 7000000000\n' + show('m["a"]') + '\n'
                     'short[2] ss = [1, 2]\n' + show('ss[0] + ss[1]')))
    assert run(source) == ['10000000000 2026', '5000000000', '9000000005', '7000000000', '3']


def test_sorting_map_keys_match_and_text():
    source = ('struct Account\n    string name\n    long cents\n    short year\n\n'
              + main('List<long> xs = [9000000000, 2, 5000000000]\nxs.sort()\n'
                     'print("{@1} {@2} {@3}", xs[0], xs[1], xs[2])\n'
                     'List<short> ss = [3, -1, 2]\nss.sort()\n' + show('ss[0]') + '\n'
                     'Account a = Account("Ann", 5000000000, 2026)\nprint("{a}")\n'
                     'Map<long, string> names\nnames[5000000000] = "five"\nprint(names[5000000000])\n'
                     + catching('print(names[4])', 'KeyError') + '\n'
                     'long n = 5000000000\nmatch n\n    case 5000000000: print("big")\n    else: print("other")\n'
                     'List<Account> all = [a]\nprint(all.toCSV())\nlong[] arr = [1, 5000000000]\nprint(arr.toCSV())'))
    assert run(source) == ['2 5000000000 9000000000', '-1', 'name : "Ann",cents : 5000000000,year : 2026',
                           'five', 'key 4 is not in the map', 'big',
                           'Account.name,Account.cents,Account.year', '"Ann",5000000000,2026', '1,5000000000']


def test_a_generic_function_with_long():
    source = 'T function first<T>(List<T> items) : items[0]\n\n' + main(
        'List<long> xs = [6000000000]\nlong f = first(xs)\n' + show('f'))
    assert run(source) == ['6000000000']
