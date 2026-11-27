"""Task 47.4 - the built-in enum FusionType (D.201): every type described - type, kind, size, canBeNull, and min /
max / default in the type itself (FusionType.INT.max is an int). Added only to a program that uses it."""
import pytest

from src.semantic.fusion_type import TYPES
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main


def run(body: str) -> list:
    code, out, err = compile_and_run(main(body))
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def test_min_and_max_are_the_type_itself():
    assert run('int top = FusionType.INT.max\nlong low = FusionType.LONG.min\nbool b = FusionType.BOOL.max\n'
               'print("{top} {low} {b}")') == ['2147483647 -9223372036854775808 true']


@pytest.mark.parametrize('expression, shown', [
    ('FusionType.BYTE.max', '255'), ('FusionType.SHORT.min', '-32768'),
    ('FusionType.INT128.max', '170141183460469231731687303715884105727'),
    ('FusionType.MONEY.max', '9223372036854775807'), ('FusionType.DECIMAL.max', '9' * 38),
    ('FusionType.INT.default', '0'), ('FusionType.BOOL.default', 'false'),
])
def test_each_value(expression, shown):
    assert run(f'print("{{@1}}", {expression})') == [shown]


def test_the_float_limits():
    assert run('print("{@1} {@2}", FusionType.DOUBLE.max > 1e308, FusionType.FLOAT.min < -3e38f)\n'
               'print("{@1}", FusionType.DOUBLE.max == Double.MAX)') == ['true true', 'true']


def test_the_plain_fields():
    assert run('print("{@1} {@2} {@3} {@4}", FusionType.DOUBLE.type, FusionType.DOUBLE.kind, FusionType.DOUBLE.size, '
               'FusionType.CLASS.canBeNull)') == ['double value 8 true']


def test_every_type_listed():
    lines = run('for t in FusionType.values()\n    print("{t} {@1}", t.size)')
    assert [line.split()[0] for line in lines] == list(TYPES)


@pytest.mark.parametrize('body, message', [
    ('string s = FusionType.STRING.max', 'FusionType.STRING has no max - a string has none'),
    ('FusionType t = FusionType.INT\nint x = t.max', 'write the value: FusionType.INT.max'),
    ('FusionType.INT.size = 3', "An enum's data is fixed"),
])
def test_errors(body, message):
    assert message in errors_of(main(body))


def test_not_added_when_unused():
    from src.semantic.fusion_type import add_fusion_type_enum
    from tests.test_structs import parse
    program = parse(main('print("x")'))
    add_fusion_type_enum(program)
    assert not any(getattr(d, 'name', None) == 'FusionType' for d in program.declarations)
