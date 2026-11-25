"""Task 47.6 - ranges over decimals and money (D.170), behind `[ranges] decimals = true`.

    for x in 0.0...1.0 step 0.1          // 0.0 0.1 ... 1.0 - each value start + n * step, never added up
    for d in price...3 step 0.25         // a decimal range - exact
    for m in lo...hi step 0.25           // a money range - exact, the currencies agree
    match t                              // ranges in a match on a double - a test, never ==
        case 0.0...0.49 : ...

`stepRequired` (a step must be written), `defaultStep` (0.1), `rangeMaxStep` (3 - the finest step 0.001),
`strictStep` (a step that misses the end). Every program runs under the leak check.
"""
import pytest

from src.config.project_config import RangesConfig, load_project_config
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_structs import parse

ON = RangesConfig(decimals=True)


def source_of(body: str) -> str:
    return 'void function main()\n' + ''.join(f'    {line}\n' for line in body.split('\n'))


def run(body: str, ranges: RangesConfig = ON, expect_fail: bool = False) -> list:
    code, out, err = compile_and_run(source_of(body), analyzer_options={'ranges_config': ranges})
    assert (code != 0) == expect_fail, out + err
    return [line.strip() for line in (out + err).strip().splitlines() if not line.startswith('[freed')]


def analyzed(body: str, ranges: RangesConfig = ON):
    analyzer = SemanticAnalyzer(ranges_config=ranges)
    analyzer.analyze(parse(source_of(body)))
    return [e.message for e in analyzer.get_errors()], [w.message for w in analyzer.get_warnings()]


def loop(header: str, value: str = 'x') -> str:
    return f'for {header}\n    print("{{@1}}", {value})'


# ---- 47.6a: whole numbers only by default ----

@pytest.mark.parametrize('header', ['x in 0.5...2.5 step 0.5', 'x in 0...2 step 0.5', 'x in 0.5...2.5'])
def test_off_by_default_says_how_to_turn_it_on(header):
    errors, _ = analyzed(loop(header), RangesConfig())
    assert len(errors) == 1 and '[ranges] decimals = true' in errors[0], errors


def test_money_and_decimal_ranges_need_the_setting_too():
    errors, _ = analyzed('decimal a = 1.5\n' + loop('d in a...3 step 0.5', 'd'), RangesConfig())
    assert len(errors) == 1 and 'this one has a decimal' in errors[0], errors
    errors, _ = analyzed('money a = 1.5\n' + loop('m in a...3 step 0.5', 'm'), RangesConfig())
    assert len(errors) == 1 and 'this one has a money' in errors[0], errors


# ---- 47.6b: a step, each value from its count ----

def test_no_drift_the_end_is_reached():
    assert run(loop('x in 0.0...1.0 step 0.1')) == ['0.000000', '0.100000', '0.200000', '0.300000', '0.400000',
                                                     '0.500000', '0.600000', '0.700000', '0.800000', '0.900000',
                                                     '1.000000']


def test_the_value_is_start_plus_n_steps():
    # adding 0.1 ten times gives 0.9999999999999999 - from the count it is 1.0 exactly
    assert run('double last = 0.0\nfor x in 0.0...1.0 step 0.1\n    last = x\nprint("{@1}", last == 1.0)') == ['true']


def test_counting_down_and_whole_number_ends():
    assert run(loop('x in 2.5...0.5 step -1.0')) == ['2.500000', '1.500000', '0.500000']
    assert run(loop('x in 0...1 step 0.25')) == ['0.000000', '0.250000', '0.500000', '0.750000', '1.000000']


def test_the_loop_variable_is_a_double():
    assert run('for x in 0.5...1.5 step 0.5\n    double y = x * 2\n    print("{@1}", y)') == [
        '1.000000', '2.000000', '3.000000']


def test_a_step_from_a_value_and_ends_from_values():
    assert run('double s = 0.3\ndouble e = 1.0\n' + loop('x in 0.0...e step s')) == [
        '0.000000', '0.300000', '0.600000', '0.900000']


def test_ends_from_values_against_the_step_no_turns():
    assert run('double a = 2.0\n' + loop('x in a...1.0 step 0.5') + '\nprint("none")') == ['none']


def test_break_and_continue():
    assert run('for x in 0.0...2.0 step 0.5\n    if x == 0.5\n        continue\n    if x > 1.2\n        break\n'
               '    print("{@1}", x)') == ['0.000000', '1.000000']


def test_a_step_is_required():
    errors, _ = analyzed(loop('x in 0.5...2.5'))
    assert len(errors) == 1 and 'needs its step' in errors[0] and 'stepRequired' in errors[0], errors


def test_the_default_step_when_not_required():
    ranges = RangesConfig(decimals=True, step_required=False)
    assert run(loop('x in 0.0...0.3'), ranges) == ['0.000000', '0.100000', '0.200000', '0.300000']
    ranges = RangesConfig(decimals=True, step_required=False, default_step='0.25')
    assert run(loop('x in 0.0...0.5'), ranges) == ['0.000000', '0.250000', '0.500000']


@pytest.mark.parametrize('step, problem', [
    ('0.0001', 'finer than 0.001'), ('-0.0001', 'finer than 0.001'), ('0.0', "can't be 0"),
])
def test_a_written_step_too_fine_or_zero(step, problem):
    errors, _ = analyzed(loop(f'x in 0.0...1.0 step {step}'))
    assert len(errors) == 1 and problem in errors[0], errors


def test_rangeMaxStep_raised_allows_a_finer_step():
    ranges = RangesConfig(decimals=True, range_max_step=4)
    assert run(loop('x in 0.0...0.0002 step 0.0001'), ranges) == ['0.000000', '0.000100', '0.000200']


@pytest.mark.parametrize('step, message', [
    ('0.0', "can't be 0"), ('0.0001', 'finer than [ranges] rangeMaxStep allows (3 places)'),
])
def test_a_step_from_a_value_checked_while_running(step, message):
    lines = run(f'double s = {step}\n' + loop('x in 0.0...1.0 step s') + '\nprint("after")', expect_fail=True)
    assert any('Runtime error at test.fusion:3' in line and message in line for line in lines), lines
    assert 'after' not in lines


def test_a_step_from_a_value_caught():
    assert run('double s = 0.0\ntry\n    for x in 0.0...1.0 step s\n        print("x")\ncatch RangeError e\n'
               '    print("caught")') == ['caught']


@pytest.mark.parametrize('header, problem', [
    ('x in 2.5...0.5 step 0.5', 'never starts - a positive step counts up; write step -0.5'),
    ('x in 0.5...2.5 step -0.5', 'never starts - a negative step counts down; write step 0.5'),
])
def test_written_against_the_step(header, problem):
    errors, _ = analyzed(loop(header))
    assert len(errors) == 1 and problem in errors[0], errors


def test_floats_and_a_string_part():
    assert run('float a = 0.5\n' + loop('x in a...1.5 step 0.5')) == ['0.500000', '1.000000', '1.500000']
    errors, _ = analyzed('string s = "a"\n' + loop('x in 0.5...s step 0.5'))
    assert any('ends and step are numbers' in e for e in errors), errors


# ---- 47.6d: a step that misses the end ----

def test_a_step_that_misses_the_end_warns():
    errors, warnings = analyzed(loop('x in 0.0...1.0 step 0.3'))
    assert not errors and len(warnings) == 1, (errors, warnings)
    assert "0...1 step 0.3 doesn't land on 1 - the last value is 0.9" in warnings[0], warnings
    assert run(loop('x in 0.0...1.0 step 0.3')) == ['0.000000', '0.300000', '0.600000', '0.900000']


def test_strictStep_makes_it_an_error():
    errors, _ = analyzed(loop('x in 0.0...1.0 step 0.3'), RangesConfig(decimals=True, strict_step=True))
    assert len(errors) == 1 and "doesn't land on 1" in errors[0], errors


def test_a_step_that_lands_is_quiet():
    errors, warnings = analyzed(loop('x in 0.0...1.2 step 0.3'))
    assert not errors and not warnings, (errors, warnings)


# ---- decimal ranges: exact ----

def test_a_decimal_range_is_exact():
    assert run('decimal a = 1.50\n' + loop('d in a...3 step 0.25', 'd')) == [
        '1.50', '1.75', '2.00', '2.25', '2.50', '2.75', '3.00']
    assert run('decimal a = 0.1\ndecimal t = 0\nfor d in a...0.3 step 0.1\n    t = t + d\nprint("{t} {@1}", t == 0.6)') \
        == ['0.6 true']


def test_a_decimal_range_down_and_from_values():
    assert run('decimal hi = 1.0\ndecimal lo = 0.0\ndecimal s = -0.5\n' + loop('d in hi...lo step s', 'd')) == [
        '1.0', '0.5', '0.0']
    assert run('decimal s = 0.0\n' + loop('d in toDecimal("0")...1 step s', 'd'), expect_fail=True)


def test_a_double_variable_in_a_decimal_range_is_an_error():
    errors, _ = analyzed('decimal a = 1.5\ndouble s = 0.5\n' + loop('d in a...3 step s', 'd'))
    assert any("can't become a decimal exactly" in e for e in errors), errors


# ---- 47.6e: money ranges, exact ----

def test_a_money_range():
    assert run('money lo = money(0.00, "ZAR", "R")\nmoney hi = money(1.00, "ZAR", "R")\n'
               + loop('m in lo...hi step 0.25', 'm')) == ['R0.00', 'R0.25', 'R0.50', 'R0.75', 'R1.00']


def test_a_money_range_with_written_ends():
    assert run('money step = money(2.50, "USD", "$")\n' + loop('m in 0...10 step step', 'm')) == [
        '$0.00', '$2.50', '$5.00', '$7.50', '$10.00']


def test_a_money_range_of_two_currencies_is_a_currency_error():
    lines = run('money lo = money(0.00, "ZAR", "R")\nmoney hi = money(1.00, "USD", "$")\n'
                + loop('m in lo...hi step 0.25', 'm'), expect_fail=True)
    assert any('ZAR ... USD: two different currencies' in line for line in lines), lines


def test_a_decimal_variable_in_a_money_range_is_an_error():
    errors, _ = analyzed('money a = 1.5\ndecimal s = 0.5\n' + loop('m in a...3 step s', 'm'))
    assert any("doesn't become money by itself" in e for e in errors), errors


# ---- 47.6f: ranges in a match on a double ----

GRADE = ('match t\n    case 0.0...0.49\n        print("low")\n    case 0.5...0.89\n        print("mid")\n'
         '    case 0.9...1.0\n        print("high")\n    else\n        print("out")')


@pytest.mark.parametrize('value, word', [('0.0', 'low'), ('0.49', 'low'), ('0.495', 'out'), ('0.5', 'mid'),
                                         ('0.9', 'high'), ('1.0', 'high'), ('1.5', 'out'), ('-0.1', 'out')])
def test_ranges_in_a_match_on_a_double(value, word):
    assert run(f'double t = {value}\n' + GRADE) == [word]


def test_ranges_in_a_match_on_a_float_written_digits():
    assert run('float t = 0.1\nmatch t\n    case 0.1...0.2\n        print("in")\n    else\n        print("out")') \
        == ['in']


@pytest.mark.parametrize('cases, problem', [
    ('    case 0.5\n        print("x")\n', 'takes ranges only'),
    ('    case 0.0...0.5\n        print("x")\n    case 0.5...1.0\n        print("y")\n', 'overlaps an earlier case'),
    ('    case 1.0...0.5\n        print("x")\n', 'from the smaller to the larger'),
])
def test_match_on_a_double_rules(cases, problem):
    errors, _ = analyzed('double t = 0.5\nmatch t\n' + cases + '    else\n        print("z")')
    assert any(problem in e for e in errors), errors


def test_a_match_on_a_double_needs_an_else():
    errors, _ = analyzed('double t = 0.5\nmatch t\n    case 0.0...1.0\n        print("x")')
    assert any('needs an else' in e for e in errors), errors


# ---- found with 47.6f: a written number used as a double was the float 0.49f ----

def test_a_written_number_used_as_a_double_is_the_number_written():
    assert run('double d = 0.49\nprint("{@1} {@2}", d == 0.49, d > 0.49)\ndouble e = d + 0.01\n'
               'print("{@1}", e == 0.5)\ndouble n = -0.1\nprint("{@1}", n < -0.1)', RangesConfig()) == [
        'true false', 'true', 'false']


# ---- the settings ----

def test_the_settings_are_read(tmp_path):
    (tmp_path / 'fusion.toml').write_text('[ranges]\ndecimals = true\nstepRequired = false\ndefaultStep = 0.25\n'
                                          'rangeMaxStep = 5\n', encoding='utf-8')
    ranges = load_project_config(str(tmp_path / 'main.fusion')).ranges
    assert (ranges.decimals, ranges.step_required, ranges.default_step, ranges.range_max_step) == (
        True, False, '0.25', 5)


@pytest.mark.parametrize('line', ['defaultStep = 0', 'defaultStep = -0.1', 'defaultStep = "x"', 'rangeMaxStep = 19',
                                  'rangeMaxStep = 1.5', 'decimals = 1'])
def test_bad_settings(tmp_path, line):
    from src.config.project_config import ProjectConfigError
    (tmp_path / 'fusion.toml').write_text(f'[ranges]\n{line}\n', encoding='utf-8')
    with pytest.raises(ProjectConfigError):
        load_project_config(str(tmp_path / 'main.fusion'))
