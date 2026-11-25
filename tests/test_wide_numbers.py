"""Task 47.7 - `int128` and `int256`: signed wide whole numbers, used like any number (D.179).

    int128 big = 170141183460469231731687303715884105727   // past a long's range: an int128
    int256 huge = toInt256(big) * 2                         // widening is automatic, toInt256 makes it explicit
    long back = toLong(big / 10000000000000000000)          // narrowing is written and checked (D.003)

C: GCC's __int128 and C23's _BitInt(256). Arithmetic is done in the widest operand's kind and checked for overflow,
as int's and long's are; never mixed with a float or double. Every program runs under the leak check.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import analyze, errors_of, main

MAX128 = 170141183460469231731687303715884105727
MAX256 = 57896044618658097711785492504343953926634992332820282019728792003956564819967


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def catching(body: str, error: str = 'OverflowError') -> str:
    inner = '\n'.join('    ' + line for line in body.splitlines())
    return f'try\n{inner}\ncatch {error} e\n    print(e.message)'


def show(value: str) -> str:
    return f'print("{{@1}}", {value})'


# ---------------------------------------------------------------- values, limits, printing

def test_limits_and_printing():
    assert run(main(f'int128 a = {MAX128}\nint128 b = -{MAX128 + 1}\nint256 c = {MAX256}\nint256 d = -{MAX256 + 1}\n'
                    'print("{a} {b}")\nprint("{c}")\nprint(toString(d))\n' + show('a') + '\nint128 z\n' + show('z'))) == [
        f'{MAX128} -{MAX128 + 1}', str(MAX256), f'-{MAX256 + 1}', str(MAX128), '0']


def test_a_written_number_takes_the_smallest_type_that_holds_it():
    assert 'Cannot assign int256 to variable of type int128' in errors_of(main(f'int128 x = {MAX128 + 1}'))
    assert "doesn't fit in an int256" in errors_of(main(f'int256 x = {MAX256 + 1}'))
    assert analyze(main('int128 small = 5\nint256 mid = 9223372036854775808'))[2]


# ---------------------------------------------------------------- widening, arithmetic in the widest kind

def test_widening_and_mixed_arithmetic():
    assert run(main('long l = 9000000000000000000\nint128 a = l\nint128 b = a + l\nint256 c = b\nint256 d = c * b\n'
                    'print("{a} {b}")\n' + show('d'))) == [
        '9000000000000000000 18000000000000000000', str(18000000000000000000 ** 2)]


def test_long_arithmetic_stays_a_long():
    # long + long is a long - widen one side first (toInt128), as int + int stays an int
    assert run(main('long l = 9000000000000000000\n' + catching('int128 s = l + l\n' + show('s')) + '\n'
                    'int128 t = toInt128(l) + l\n' + show('t'))) == [
        "9000000000000000000 + 9000000000000000000 doesn't fit in a long", '18000000000000000000']


def test_never_narrowed_by_itself_and_never_mixed_with_a_float():
    assert 'Cannot assign int128 to variable of type long' in errors_of(main('int128 a = 5\nlong l = a'))
    assert 'Cannot assign int256 to variable of type int128' in errors_of(main('int256 a = 5\nint128 b = a'))
    assert "can't be mixed" in errors_of(main('int128 a = 5\ndouble d = 1.5\ndouble e = d + 1.0\nbool x = a > d'))
    assert 'Cannot assign int128 to variable of type double' in errors_of(main('int128 a = 5\ndouble d = a'))


def test_division_remainder_comparison():
    assert run(main(f'int128 a = {MAX128}\nint128 b = 1000000000000\n'
                    'print("{@1} {@2} {@3} {@4}", a / b, a % b, a > b, a == b)\n'
                    + catching('int128 z = 0\n' + show('a / z'), 'DivideByZeroError'))) == [
        f'{MAX128 // 10 ** 12} {MAX128 % 10 ** 12} true false', f'{MAX128} / 0: division by zero']


# ---------------------------------------------------------------- overflow, checked

@pytest.mark.parametrize('kind, top', [('int128', MAX128), ('int256', MAX256)])
@pytest.mark.parametrize('expression, message', [
    ('top + 1', '{top} + 1 doesn\'t fit in an {kind}'),
    ('low - 1', '-{low} - 1 doesn\'t fit in an {kind}'),
    ('top * 2', '{top} * 2 doesn\'t fit in an {kind}'),
    ('-low', '-(-{low}) doesn\'t fit in an {kind}'),
    ('low / -1', '-{low} / -1 doesn\'t fit in an {kind}'),
])
def test_overflow_is_an_error(kind, top, expression, message):
    low = top + 1
    assert run(main(f'{kind} top = {top}\n{kind} low = -{low}\n'
                    + catching(f'{kind} r = {expression}\n' + show('r')))) == [
        message.format(top=top, low=low, kind=kind)]


def test_wrapping_when_asked():
    assert run(main(f'int128 top = {MAX128}\nunchecked\n    int128 r = top + 1\n    ' + show('r'))) == [f'-{MAX128 + 1}']


# ---------------------------------------------------------------- conversions

def test_conversions_from_text_and_numbers():
    assert run(main('int128 a = toInt128("-12345678901234567890123")\nint256 b = toInt256("99999999999999999999999999999999999999999")\n'
                    'int128 c = toInt128(5)\nint256 d = toInt256(c)\nprint("{a} {b} {c} {d}")\n'
                    + catching(f'int128 e = toInt128("{MAX128 + 1}")\n' + show('e'), 'NumberFormatError') + '\n'
                    + catching('int128 f = toInt128("12x")\n' + show('f'), 'NumberFormatError'))) == [
        '-12345678901234567890123 99999999999999999999999999999999999999999 5 5',
        f"'{MAX128 + 1}' is not a whole number that fits in an int128",
        "'12x' is not a whole number that fits in an int128"]


def test_narrowing_is_checked():
    assert run(main(f'int256 big = {MAX256}\nint128 small = 70000\n'
                    'print("{@1} {@2} {@3}", toInt(small), toLong(small), toShort(toInt128(12)))\n'
                    + catching('int128 x = toInt128(big)\n' + show('x')) + '\n'
                    + catching('long y = toLong(toInt128(big / 2))\n' + show('y')) + '\n'
                    + catching('short s = toShort(small)\n' + show('s')))) == [
        '70000 70000 12', f"{MAX256} doesn't fit in an int128", f"{MAX256 // 2} doesn't fit in an int128",
        "70000 doesn't fit in a short (-32768 to 32767)"]


# ---------------------------------------------------------------- in every place a type goes

def test_in_functions_structs_arrays_collections_match_and_text():
    source = ('int128 function twice(int128 n) : n * 2\n\nstruct Total\n    string name\n    int128 amount\n\n'
              + main(f'Total t = Total("all", {MAX128 // 4})\nprint("{{@1}}", twice(t.amount))\nprint("{{t}}")\n'
                     'int256[2] xs = [1, 2]\nxs[1] = toInt256(t.amount) * 4\n' + show('xs[1]') + '\n'
                     f'List<int128> ys = [{MAX128}, 3, -7]\nys.sort()\nprint("{{@1}} {{@2}}", ys[0], ys[2])\n'
                     f'Map<int128, string> names\nnames[{MAX128}] = "top"\nprint(names[{MAX128}])\n'
                     + catching('print(names[4])', 'KeyError') + '\n'
                     'int128 n = 3\nmatch n\n    case 3: print("three")\n    else: print("other")\n'
                     'List<Total> all = [t]\nprint(all.toCSV())'))
    assert run(source) == [str(MAX128 // 4 * 2), f'name : "all",amount : {MAX128 // 4}', str(MAX128 // 4 * 4),
                           f'-7 {MAX128}', 'top', 'key 4 is not in the map', 'three',
                           'Total.name,Total.amount', f'"all",{MAX128 // 4}']


def test_a_generic_function_with_int256():
    source = 'T function first<T>(List<T> items) : items[0]\n\n' + main(
        f'List<int256> xs = [{MAX256}]\nint256 f = first(xs)\n' + show('f'))
    assert run(source) == [str(MAX256)]
