"""Task 47.2a - `money`: a sealed 16-byte value struct built into the compiler (D.180-D.187).

    money price = 123.45                   // value 12345, scale 2 - the places written (D.176)
    money rand = money(100.05, "ZAR", "R") // currency 3 letters, symbol up to 4 bytes - display only (D.187)
    rand + 200.125                         // + - exact, the larger scale kept; same currency or one empty (D.183)
    rand * 3, rand * 1.155                 // * by a whole number or a decimal - exact
    rand.value, rand.scale, rand.currency, rand.symbol

Dividing, rounding, converting and formatting are the Currency module's (47.2b). Every program runs under the leak check.
"""

import subprocess

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def show(value: str) -> str:
    return f'print("{{@1}}", {value})'


def test_written_amounts_and_printing():
    assert run(main('money a = 123.45\nmoney b = 5\nmoney c = -3.50\nmoney z\nprint("{a} {b} {c} {z}")\n'
                    'money r = money(100.05, "ZAR", "R")\nprint("{r}")\nprint(toString(-r))')) == [
        '123.45 5 -3.50 0', 'R100.05', '-R100.05']


def test_the_fields():
    assert run(main('money r = money(100.05, "ZAR", "R")\n'
                    'print("{@1} {@2} {@3} {@4}", r.value, r.scale, r.currency, r.symbol)\n'
                    'money p = 1.5\nprint("[{@1}] [{@2}]", p.currency, p.symbol)\n'
                    'r.currency = "USD"\nr.symbol = "$"\nr.value = 250\nprint("{r} {@1}", r.currency)')) == [
        '10005 2 ZAR R', '[] []', '$2.50 USD']


def test_add_and_subtract_keep_the_larger_scale():
    assert run(main('money r = money(100.05, "ZAR", "R")\n' + show('r + 200.125') + '\n' + show('r - 0.05') + '\n'
                    'money plain = 1.10\n' + show('plain + r'))) == ['R300.175', 'R100.00', 'R101.15']


def test_multiply_by_a_whole_number_or_a_decimal():
    assert run(main('money r = money(100.05, "ZAR", "R")\ndecimal rate = 1.155\n'
                    + show('r * 3') + '\n' + show('2 * r') + '\n' + show('r * 1.155') + '\n' + show('r * rate'))) == [
        'R300.15', 'R200.10', 'R115.55775', 'R115.55775']


def test_comparing_by_amount():
    assert run(main('money r = money(100.05, "ZAR")\nmoney s = 100.050\n'
                    'print("{@1} {@2} {@3} {@4}", r == s, r > 100, r <= 99.99, r != 1)')) == [
        'true true false true']


def test_two_currencies_are_a_currency_error():
    source = main('money r = money(1.00, "ZAR")\nmoney y = money(500, "JPY")\n'
                  'try\n    money bad = r + y\n    print("{bad}")\ncatch CurrencyError e\n    print(e.message)\n'
                  'try\n    print("{@1}", r < y)\ncatch CurrencyError e\n    print(e.message)\n'
                  + show('r == y') + '\n'
                  'try\n    r.currency = "RANDS"\ncatch CurrencyError e\n    print(e.message)')
    assert run(source) == ['ZAR + JPY: two different currencies - convert one first',
                           'ZAR compared with JPY: two different currencies', 'false',
                           '\'RANDS\' isn\'t a currency code - 3 letters (ISO 4217), or "" for none']


def test_written_mistakes_are_compile_errors():
    assert "isn't a currency code" in errors_of(main('money r = money(1, "rand")'))
    assert 'money keeps up to 4' in errors_of(main('money r = money(1, "ZAR", "RANDS")'))
    assert 'money * money has no meaning' in errors_of(main('money a = 1\nmoney b = 2\nmoney c = a * b'))
    assert "the Currency module's" in errors_of(main('money a = 10\nmoney b = a / 3'))
    assert "doesn't become money by itself" in errors_of(main('decimal d = 1.5\nmoney m = d'))
    assert "doesn't become money by itself" in errors_of(main('double d = 1.5\nmoney m = d'))
    assert 'money has no field' in errors_of(main('money m = 1\nprint("{@1}", m.amount)'))


def test_overflow():
    assert run(main('money big = 9000000000000000000\ntry\n    money twice = big * 2\n    print("{twice}")\n'
                    'catch OverflowError e\n    print(e.message)')) == [
        "the product doesn't fit in money (a long of its smallest steps)"]


def test_conversions_to_and_from_decimal():
    assert run(main('money r = money(100.05, "ZAR", "R")\ndecimal d = toDecimal(r)\nprint("{d}")\n'
                    'money back = money(d * 2, "ZAR")\nprint("{back} {@1}", back.currency)')) == ['100.05', '200.10 ZAR']


def test_in_structs_functions_collections_and_text():
    source = ('struct Line\n    string item\n    money price\n\n'
              'money function total(List<Line> lines)\n    money sum = 0\n    foreach l in lines\n'
              '        sum = sum + l.price\n    return sum\n\n'
              + main('List<Line> lines = [Line("tea", money(12.50, "ZAR", "R")), Line("cake", money(4.25, "ZAR", "R"))]\n'
                     + show('total(lines)') + '\n' + show('lines[0]') + '\n'
                     'List<money> ms = [1.50, 2.25]\nprint("{@1} {@2}", ms[1], ms.contains(1.5))\n'
                     'Map<string, money> m\nm["a"] = money(9.99, "USD", "$")\n' + show('m["a"]') + '\n'
                     'money[2] arr = [1.10, 2.20]\n' + show('arr[0] + arr[1]') + '\nprint(lines.toCSV())'))
    assert run(source) == ['R16.75', 'item : "tea",price : R12.50', '2.25 true', '$9.99', '3.30',
                           'Line.item,Line.price', '"tea",R12.50', '"cake",R4.25']


def test_money_is_16_bytes(tmp_path):
    # the runtime says so with a _Static_assert (D.184); here the C struct is measured
    from src.codegen.c_money import MONEY_LIBRARY
    source = ('#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\n'
              + MONEY_LIBRARY.split('static inline')[0] + 'int main(void) { printf("%d", (int)sizeof(fusion_money)); return 0; }\n')
    c_file = tmp_path / 'size.c'
    c_file.write_text(source, encoding='ascii')
    subprocess.run(['gcc', str(c_file), '-o', str(tmp_path / 'size.exe')], check=True)
    assert subprocess.run([str(tmp_path / 'size.exe')], capture_output=True, text=True).stdout == '16'
