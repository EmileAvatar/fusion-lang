"""Task 47.2b - the Currency module (src/stdlib/Currency.fusion, D.186): written in Fusion, added to a program that
uses money. Every active ISO 4217 currency - its places and its symbol (at most 4 bytes, D.184).

    m / 3                        Currency.divide - the money's own places, rounded once ([numbers] rounding)
    m.split(3), m.splitBy([70, 30])   parts that add up exactly (Fowler)
    m.percent(15.5), m.settle(), m.round(2), m.roundWith(2, Rounding.halfUp)
    m.convert("ZAR", "JPY", 8.42)     the developer's rate - never fetched; the new currency's places
    m.format(), Currency.places("KWD"), Currency.symbol("EUR"), Currency.of(12.345, "ZAR")

Every program runs under the leak check.
"""

import re

from src.semantic.currency import CURRENCY_FILE
from tests.test_end_to_end import compile_and_run
from tests.test_structs import analyze, main


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def table() -> dict:
    """code -> (places, symbol) from Currency.fusion's table, its \\u escapes read."""
    text = CURRENCY_FILE.read_text(encoding='ascii')
    rows = re.findall(r'"([A-Z]{3}) (\d) ([^"]+)"', text)
    return {code: (int(places), symbol.encode('ascii').decode('unicode_escape')) for code, places, symbol in rows}


def test_every_iso_4217_currency_with_its_places():
    t = table()
    assert len(t) == 166         # every active ISO 4217 code with places (the 13 metals / test / fund units left out)
    assert t['ZAR'] == (2, 'R') and t['USD'] == (2, '$') and t['EUR'] == (2, '\u20AC') and t['GBP'] == (2, '\u00A3')
    assert t['JPY'][0] == 0 and t['KRW'][0] == 0 and t['ISK'][0] == 0 and t['VND'][0] == 0
    assert all(t[c][0] == 3 for c in ('BHD', 'IQD', 'JOD', 'KWD', 'LYD', 'OMR', 'TND'))
    assert t['CLF'][0] == 4 and t['UYW'][0] == 4
    assert not {'XAU', 'XAG', 'XPD', 'XPT', 'XDR'} & set(t)        # not money: no places


def test_every_symbol_fits_in_4_bytes():
    assert {c: s for c, (_, s) in table().items() if len(s.encode('utf-8')) > 4} == {}


def test_the_table_from_a_program():
    assert run(main('print("{@1} {@2} {@3} {@4}", Currency.places("JPY"), Currency.places("KWD"), '
                    'Currency.symbol("EUR"), Currency.known("XYZ"))\nprint("{@1}", Currency.of(12.345, "ZAR"))\n'
                    'try\n    int p = Currency.places("ABC")\n    print("{p}")\ncatch CurrencyError e\n    print(e.message)')) == [
        '0 3 \u20AC false', 'R12.34', "'ABC' isn't an ISO 4217 currency code"]


def test_dividing_keeps_the_places_and_split_adds_up():
    assert run(main('money r = money(100.00, "ZAR", "R")\nprint("{@1}", r / 3)\nList<money> p = r.split(3)\n'
                    'print("{@1} {@2} {@3} {@4}", p[0], p[1], p[2], p[0] + p[1] + p[2])\n'
                    'money owed = money(-10.00, "ZAR")\nList<money> q = owed.split(3)\n'
                    'print("{@1} {@2} {@3}", q[0], q[1], q[2])')) == [
        'R33.33', 'R33.34 R33.33 R33.33 R100.00', '-3.34 -3.33 -3.33']


def test_split_by_ratios_adds_up():
    assert run(main('money r = money(100.00, "ZAR", "R")\nList<money> s = r.splitBy([70, 20, 10])\n'
                    'print("{@1} {@2} {@3}", s[0], s[1], s[2])\nmoney odd = money(0.10, "USD", "$")\n'
                    'List<money> t = odd.splitBy([1, 1, 1])\nprint("{@1} {@2} {@3}", t[0], t[1], t[2])')) == [
        'R70.00 R20.00 R10.00', '$0.04 $0.03 $0.03']


def test_percent_round_settle():
    assert run(main('money r = money(200.00, "ZAR", "R")\nprint("{@1}", r.percent(15.5))\n'
                    'money raw = money(12.345, "ZAR", "R")\n'
                    'print("{@1} {@2} {@3} {@4}", raw.settle(), raw.round(1), raw.roundWith(2, Rounding.halfUp), '
                    'Currency.round(raw, 0))')) == ['R31.00', 'R12.34 R12.3 R12.35 R12']


def test_convert_with_the_developers_rate():
    assert run(main('money r = money(100.00, "ZAR", "R")\nmoney yen = r.convert("ZAR", "JPY", 8.4211)\n'
                    'money kwd = r.convert("ZAR", "KWD", 0.01663)\nprint("{yen} {kwd} {@1}", yen.currency)\n'
                    'try\n    money bad = yen.convert("ZAR", "USD", 0.05)\n    print("{bad}")\ncatch CurrencyError e\n'
                    '    print(e.message)')) == ['\u00A5842 KD1.663 JPY', 'this money is JPY, not ZAR']


def test_format_groups_thousands():
    assert run(main('money big = money(1234567.891, "USD", "$")\nprint(big.format())\n'
                    'print(Currency.format(money(-100.00, "ZAR", "R")))\nprint(Currency.format(money(999.5)))')) == [
        '$1,234,567.891', '-R100.00', '999.5']


def test_dividing_by_something_else_and_remainder_are_errors():
    from tests.test_structs import errors_of
    assert 'divide by a whole number' in errors_of(main('money a = 10\nmoney b = a % 3'))
    assert 'divide by a whole number' in errors_of(main('money a = 10\ndecimal d = 2.5\nmoney b = a / d'))


def test_added_only_where_money_is_used():
    analyzer, ast, ok = analyze(main('int x = 1'))
    assert ok and not any(getattr(d, 'name', None) == 'Currency' for d in ast.declarations)
    analyzer, ast, ok = analyze(main('money m = 1'))
    assert ok and any(getattr(d, 'name', None) == 'Currency' for d in ast.declarations)


def test_a_program_may_have_a_currency_of_its_own():
    assert run('class Currency\n    public static int function places(string code) : 7\n\n'
               + main('money m = 1.5\nprint("{@1} {m}", Currency.places("ZAR"))')) == ['7 1.5']
