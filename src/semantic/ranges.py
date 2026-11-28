"""Ranges over decimals and money (Task 47.6, D.170) - a mixin of the type checker.

`for x in 0.5...2.5 step 0.5` - a range whose ends or step is a float, double, decimal or money:
- `[ranges] decimals` (default false): such a range is an error saying how to turn it on
- `[ranges] stepRequired` (default true): its step must be written; false - `defaultStep` (0.1)
- `[ranges] rangeMaxStep` (default 3): the finest step is 0.001 (or -0.001); finer is an error - written here,
  from a value while running
- each value is worked out from its count (start + n * step), never by adding - nothing drifts; a decimal or
  money range is exact
- a step that doesn't land on the end: only the values within the range, a warning (`strictStep` an error) -
  the rule of whole-number ranges (33.2g)

The kind of the range is the widest of its parts: money, then decimal, then double, then float. Every part is
made that kind (a written number keeps its places - 0.25 as money is 25 at scale 2); the loop variable gets it.
"""

from decimal import Decimal, InvalidOperation

from src.parser.ast_nodes import LiteralExpr, UnaryExpr, PrimitiveType
from .errors import SemanticError

WHOLE_TYPES = ('byte', 'short', 'int', 'long', 'int128', 'int256')
RANGE_KINDS = ('money', 'decimal', 'double', 'float')       # the widest first


def written_number(node):
    """A number written in the code (`5`, `-2`, `0.25`) exactly, as a Decimal - or None."""
    from src.lexer.literals import integer_value
    negative = False
    if isinstance(node, UnaryExpr) and node.operator == '-':
        node, negative = node.operand, True
    if not isinstance(node, LiteralExpr):
        return None
    if node.type_hint == 'int':
        number = Decimal(integer_value(node.value) if isinstance(node.value, str) else node.value)
    elif node.type_hint in ('float', 'double') and getattr(node, 'written', None):
        from src.lexer.literals import decimal_digits
        try:
            digits, scale = decimal_digits(node.written)          # 6.67e-11, 19.99m too (47.9)
            number = Decimal(digits).scaleb(-scale)
        except (InvalidOperation, ValueError):
            return None
    else:
        return None
    return -number if negative else number


def plain(number: Decimal) -> str:
    """0.30 -> 0.3, 1E+1 -> 10: a number as a person writes it."""
    text = format(number.normalize(), 'f')
    return text if text not in ('-0', '') else '0'


def range_kind(types):
    """The kind of a range from its parts' types - money, decimal, double, float - or None (whole numbers)."""
    names = [getattr(t, 'name', None) for t in types]
    return next((k for k in RANGE_KINDS if k in names), None)


class RangesMixin:
    """The type rules of ranges over decimals and money (47.6)."""

    def check_decimal_range(self, node, types, kind) -> None:
        """`a...b step c` where a part is a float, double, decimal or money: the settings, each part made the
        range's kind, the written step and ends checked. Marks the call `range_kind` and `range_places`."""
        where = node.location
        if not getattr(self, 'range_decimals', False):
            self.errors.append(SemanticError(
                f"A range ... counts whole numbers - this one has a {kind}; ranges of decimals and money are "
                f"turned on in settings.toml: [ranges] decimals = true (then 0.5...2.5 step 0.5)", where))
            return
        args = node.arguments
        if len(args) == 2:
            if getattr(self, 'range_step_required', True):
                self.errors.append(SemanticError(
                    "A range of decimals needs its step: 0.5...2.5 step 0.5 ([ranges] stepRequired = false "
                    "uses defaultStep)", where))
                return
            default = str(getattr(self, 'range_default_step', '0.1'))
            step = LiteralExpr(location=where, value=float(default), type_hint='float')
            step.written = default
            args.append(step)
            types.append(self.visit(step))
        for arg, arg_type in zip(args, types):
            name = getattr(arg_type, 'name', None)
            if name not in WHOLE_TYPES + RANGE_KINDS:
                self.errors.append(SemanticError(
                    f"A range's ends and step are numbers - this one is {self.type_to_string(arg_type)}",
                    arg.location))
                return
        written = [written_number(a) for a in args]
        for arg, arg_type in zip(args, types):
            if kind == 'money':
                self.to_money(arg, arg_type)
            elif kind == 'decimal':
                self.to_decimal(arg, arg_type)
            elif getattr(arg_type, 'name', None) == 'int256' or getattr(arg_type, 'name', None) == 'int128':
                self.errors.append(SemanticError(
                    f"An {arg_type.name} in a range of {kind}s - a {kind} keeps fewer digits; toLong(x) first",
                    arg.location))
        node.range_kind = kind
        node.range_places = getattr(self, 'range_max_step', 3)
        self._check_written_range(node, written)

    def _check_written_range(self, node, written) -> None:
        """The parts written as numbers: a step of 0 or finer than rangeMaxStep is an error; the ends against
        the step's way an error; a step that misses the end a warning (strictStep an error)."""
        first, last, stride = written
        places = node.range_places
        if stride is not None:
            if stride == 0:
                self.errors.append(SemanticError("A range's step can't be 0 - the loop would never end",
                                                 node.arguments[2].location))
                return
            finest = Decimal(1).scaleb(-places)
            if abs(stride) < finest:
                self.errors.append(SemanticError(
                    f"A range's step of {plain(stride)} is finer than {plain(finest)} - [ranges] rangeMaxStep "
                    f"({places}) sets the finest step; raise it for a finer one", node.arguments[2].location))
                return
        if None in (first, last, stride):
            return
        shown = f"{plain(first)}...{plain(last)} step {plain(stride)}"
        if stride > 0 and first > last:
            self.errors.append(SemanticError(
                f"{shown} never starts - a positive step counts up; write step {plain(-stride)} to count down",
                node.location))
            return
        if stride < 0 and first < last:
            self.errors.append(SemanticError(
                f"{shown} never starts - a negative step counts down; write step {plain(-stride)} to count up",
                node.location))
            return
        count = (last - first) / stride
        if count == count.to_integral_value():
            return
        strict = getattr(self, 'strict_step', False)
        reached = first + int(count) * stride
        message = (f"{shown} doesn't land on {plain(last)} - the last value is {plain(reached)}"
                   f"{'' if strict else ' ([ranges] strictStep makes this an error)'}")
        (self.errors if strict else self.warnings).append(SemanticError(message, node.location))

    def range_loop_type(self, node):
        """The loop variable's type for a range over decimals or money - None for whole numbers."""
        kind = getattr(node, 'range_kind', None)
        return PrimitiveType(location=node.location, name=kind) if kind else None
