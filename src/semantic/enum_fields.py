"""An enum as a built-in value struct (Task 47.3, D.188-D.194).

    enum Planet
        MERCURY(3.303e23, 2.4397e6, "Mercury")       // id 0
        EARTH(5.976e24, 6.37814e6, "Earth"), 200     // id 200
        public const double mass                     // read from anywhere (EARTH.mass) - never set
        public const double radius
        public const string name
        private Enum(double m, double r, string n)   // optional - else the values fill the fields in order
            this.mass = m ...
        double function gravity(double kg) ...       // a method - Planet.gravity(this, kg)
        string function toString()                   // optional - worked out for each value here
            return name

Every value's data is worked out here, when compiling (D.191): its arguments - constants and arithmetic on them -
fill the fields through the constructor or in order; the enum's toString() gives each value's text. The code
generator writes them into one static const table: nothing on the heap, nothing to free (D.188). An enum with no
fields but values given data (`SMALL(2, 3, 5)`) holds a const fixed array per value - `SMALL[1]` (D.191).
"""

from src.parser.ast_nodes import (AssignmentStmt, BinaryExpr, BlockStmt, EnumDecl, IdentifierExpr,
                                  InterpolatedStringExpr, LiteralExpr, MemberExpr, NamedArgument,
                                  PrimitiveType, ProgramNode, ReturnStmt, UnaryExpr, VarDeclStmt)
from .errors import SemanticError

# The types an enum's field may have (D.190): primitive values and string - never null, nothing on the heap
FIELD_TYPES = ('bool', 'char', 'byte', 'short', 'int', 'long', 'int128', 'int256', 'float', 'double', 'string')
WHOLE_BITS = {'byte': (0, 255), 'short': (-(1 << 15), (1 << 15) - 1), 'int': (-(1 << 31), (1 << 31) - 1),
              'long': (-(1 << 63), (1 << 63) - 1), 'int128': (-(1 << 127), (1 << 127) - 1),
              'int256': (-(1 << 255), (1 << 255) - 1)}
BUILT_IN_FIELDS = ('id', 'enumTypeName')


class Char(str):
    """A char worked out when compiling - told apart from a one-letter string."""


class NotConstant(Exception):
    def __init__(self, message, node):
        super().__init__(message)
        self.message, self.node = message, node


class ConstantValues:
    """Works out a constant expression when compiling: written numbers, text, chars, true / false, `-` / `not`,
    + - * / % (C's rules for whole numbers), + on text, the program's `const` values and the names given (a
    constructor's parameters, the fields already set)."""

    def __init__(self, program: ProgramNode):
        self.consts = {d.name: d for d in program.declarations
                       if isinstance(d, VarDeclStmt) and d.is_const and d.initializer is not None}
        self.working = set()

    def value(self, node, names=None):
        names = names or {}
        if isinstance(node, LiteralExpr):
            return self._literal(node)
        if isinstance(node, IdentifierExpr):
            if node.name in names:
                return names[node.name]
            decl = self.consts.get(node.name)
            if decl is None or node.name in self.working:
                raise NotConstant(f"'{node.name}' isn't a constant - an enum's data is worked out when compiling "
                                  f"(written values, constants and arithmetic on them)", node)
            self.working.add(node.name)
            try:
                return self.value(decl.initializer)
            finally:
                self.working.discard(node.name)
        if isinstance(node, MemberExpr) and isinstance(node.object, IdentifierExpr) and node.object.name == 'this' \
                and node.member in names:
            return names[node.member]
        if isinstance(node, UnaryExpr):
            inner = self.value(node.operand, names)
            if node.operator == '-' and _is_number(inner):
                return -inner
            if node.operator in ('not', '!') and isinstance(inner, bool):
                return not inner
        if isinstance(node, BinaryExpr):
            return self._binary(node, self.value(node.left, names), self.value(node.right, names))
        if isinstance(node, InterpolatedStringExpr):
            return ''.join(self._text_part(part, names) for part in node.segments)
        raise NotConstant("an enum's data is worked out when compiling - written values, constants and "
                          "arithmetic on them (not a call or a variable)", node)

    def _text_part(self, part, names):
        if hasattr(part, 'text'):
            return part.text
        value = self.value(getattr(part, 'expression', None), names)
        if isinstance(value, float):
            raise NotConstant("a decimal number in an enum's text - its digits are written by the program; give "
                              "the text as a field", part.expression)
        return ('true' if value else 'false') if isinstance(value, bool) else str(value)

    @staticmethod
    def _literal(node):
        from src.lexer.literals import integer_value, decode_char_literal
        kind, value = node.type_hint, node.value
        if kind == 'int':
            return integer_value(value) if isinstance(value, str) else value
        if kind in ('float', 'double'):
            return float(str(value).replace('_', '').rstrip('fFdD'))
        if kind == 'bool':
            return bool(value)
        if kind == 'string':
            return str(value)
        if kind == 'char':
            text = value if len(str(value)) == 1 else decode_char_literal(value)
            return Char(text)
        raise NotConstant("null can't be an enum's data - a value is never null", node)

    @staticmethod
    def _binary(node, a, b):
        op = node.operator
        if op == '+' and isinstance(a, str) and isinstance(b, str) and not (isinstance(a, Char) or isinstance(b, Char)):
            return a + b
        if not (_is_number(a) and _is_number(b)):
            raise NotConstant(f"'{op}' on these values isn't worked out when compiling", node)
        if op == '+':
            return a + b
        if op == '-':
            return a - b
        if op == '*':
            return a * b
        if op in ('/', '%'):
            if b == 0:
                raise NotConstant("divided by 0", node)
            if isinstance(a, int) and isinstance(b, int):
                quotient = abs(a) // abs(b) * (1 if (a < 0) == (b < 0) else -1)     # C: toward 0
                return quotient if op == '/' else a - b * quotient
            return a / b if op == '/' else _c_fmod(a, b)
        raise NotConstant(f"'{op}' isn't worked out in an enum's data", node)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _c_fmod(a, b):
    import math
    return math.fmod(a, b)


def _fits(value, type_name: str):
    """The value as the field's type - or an error message (never a silent change)."""
    if type_name in WHOLE_BITS:
        if not isinstance(value, int) or isinstance(value, bool):
            return None, f"a {type_name} needs a whole number"
        low, high = WHOLE_BITS[type_name]
        if not low <= value <= high:
            return None, f"{value} doesn't fit in a {type_name}"
        return value, None
    if type_name in ('float', 'double'):
        if not _is_number(value):
            return None, f"a {type_name} needs a number"
        return float(value), None
    if type_name == 'bool':
        return (value, None) if isinstance(value, bool) else (None, "a bool needs true or false")
    if type_name == 'char':
        return (value, None) if isinstance(value, Char) else (None, "a char needs a character, such as 'x'")
    if type_name == 'string':
        return (str(value), None) if isinstance(value, str) and not isinstance(value, Char) \
            else (None, "a string needs text")
    return None, f"an enum's field can't be a {type_name}"


def check_enum_fields(program: ProgramNode, upper_case: str = 'false'):
    """(errors, warnings) for every enum: its fields, each value's data, the constructor, toString(), and
    `[enums] upperCaseNames`. Fills `variant.data` (field -> value), `variant.text` (toString's), and for an
    enum without fields `enum.items_type` / `variant.items`."""
    errors, warnings = [], []
    values = ConstantValues(program)
    for enum in (d for d in program.declarations if isinstance(d, EnumDecl)):
        _check_names(enum, upper_case, errors, warnings)
        given = [v for v in enum.variants if v.arguments is not None]
        if not (enum.fields or given or enum.methods or enum.constructor or enum.to_string):
            continue
        if any(v.fields for v in enum.variants):
            errors.append(SemanticError(
                f"Enum '{enum.name}' mixes values carrying their own data (Circle(double r)) with fixed data - "
                f"an enum is one kind or the other (D.188)", enum.location))
            continue
        _check_field_types(enum, errors)
        if enum.fields:
            for variant in enum.variants:
                _fill_fields(enum, variant, values, errors)
        elif given:
            _fill_items(enum, values, errors)
        if enum.constructor is not None and not enum.fields:
            errors.append(SemanticError(f"Enum '{enum.name}' has a constructor but no fields for it to set",
                                        enum.constructor[0].location))
        if enum.to_string is not None:
            _work_out_text(enum, values, errors)
    return errors, warnings


def _check_names(enum, upper_case, errors, warnings) -> None:
    """`[enums] upperCaseNames` (D.194): a value name not in capitals - nothing / a warning / an error."""
    if upper_case not in ('true', 'strict'):
        return
    for variant in enum.variants:
        if variant.name != variant.name.upper():
            message = (f"'{variant.name}' of enum '{enum.name}' isn't in capitals - write {variant.name.upper()}, "
                       f"so a reader sees a fixed value ([enums] upperCaseNames = {upper_case})")
            (errors if upper_case == 'strict' else warnings).append(SemanticError(message, variant.location))


def _check_field_types(enum, errors) -> None:
    seen = set()
    for f in enum.fields:
        name = f.field_type.name if isinstance(f.field_type, PrimitiveType) else None
        if name not in FIELD_TYPES:
            shown = getattr(f.field_type, 'name', None) or type(f.field_type).__name__
            if type(f.field_type).__name__ in ('ArrayType', 'ListType', 'MapType'):
                shown = 'a collection'
            errors.append(SemanticError(
                f"Field '{f.name}' of enum '{enum.name}' can't be {shown} - an enum's fields are bool, char, byte, "
                f"short, int, long, int128, int256, float, double or string (D.190)", f.location))
            f.enum_field_error = True
        if f.name in seen or f.name in BUILT_IN_FIELDS:
            errors.append(SemanticError(
                f"Enum '{enum.name}' already has a field '{f.name}'" + (" - every value has id and enumTypeName"
                                                                       if f.name in BUILT_IN_FIELDS else ''),
                f.location))
        seen.add(f.name)


def _fill_fields(enum, variant, values, errors) -> None:
    """A value's data (D.191): through the constructor - its parameters from the arguments, its body setting
    the fields - or, without one, the arguments filling the fields in order (named, defaults)."""
    args = variant.arguments or []
    where = variant.location
    data = {}
    if enum.constructor is not None:
        _, parameters, body = enum.constructor
        names = _bind(enum, variant, [(p.name, p.default_value) for p in parameters], args, values, errors)
        if names is None:
            return
        for p in parameters:
            ptype = p.param_type.name if isinstance(p.param_type, PrimitiveType) else None
            if ptype in FIELD_TYPES and p.name in names:
                value, problem = _fits(names[p.name], ptype)
                if problem:
                    errors.append(SemanticError(f"{variant.name}: parameter '{p.name}' - {problem}", where))
                    return
                names[p.name] = value
        fields = {f.name: f for f in enum.fields}
        for statement in body.statements:
            if isinstance(statement, AssignmentStmt):
                target = statement.target
                name = target.member if isinstance(target, MemberExpr) and isinstance(target.object, IdentifierExpr) \
                    and target.object.name == 'this' else (target.name if isinstance(target, IdentifierExpr) else None)
                if name in fields and (isinstance(target, MemberExpr) or name not in names):
                    try:
                        data[name] = values.value(statement.value, {**names, **data})
                    except NotConstant as problem:
                        errors.append(SemanticError(f"{variant.name}: {problem.message}", problem.node.location))
                        return
                    continue
            errors.append(SemanticError(
                f"An enum's constructor only sets its fields (this.mass = m) - worked out when compiling (D.191)",
                statement.location))
            return
        for f in enum.fields:
            if f.name not in data and f.default_value is not None:
                data[f.name] = _constant(values, f.default_value, errors, variant)
    else:
        names = _bind(enum, variant, [(f.name, f.default_value) for f in enum.fields], args, values, errors)
        if names is None:
            return
        data = names
    for f in enum.fields:
        if getattr(f, 'enum_field_error', False):
            continue
        if f.name not in data or data[f.name] is None:
            errors.append(SemanticError(f"{variant.name} of enum '{enum.name}' doesn't give field '{f.name}'", where))
            return
        value, problem = _fits(data[f.name], f.field_type.name)
        if problem:
            errors.append(SemanticError(f"{variant.name}: field '{f.name}' - {problem}", where))
            return
        data[f.name] = value
    variant.data = data


def _bind(enum, variant, slots, args, values, errors):
    """The arguments of `EARTH(...)` against (name, default) slots - by position, then by name; a slot left
    out takes its default. Their values, or None after an error."""
    names, position = {}, 0
    for arg in args:
        if isinstance(arg, NamedArgument):
            if arg.name not in [s for s, _ in slots]:
                errors.append(SemanticError(f"{variant.name}: enum '{enum.name}' has no field or parameter "
                                            f"'{arg.name}'", arg.location))
                return None
            if arg.name in names:
                errors.append(SemanticError(f"{variant.name}: '{arg.name}' is given twice", arg.location))
                return None
            value = _constant(values, arg.value, errors, variant)
            if value is None:
                return None
            names[arg.name] = value
            continue
        if names and any(isinstance(a, NamedArgument) for a in args[:args.index(arg)]):
            errors.append(SemanticError(f"{variant.name}: a value by position comes before the named ones",
                                        arg.location))
            return None
        if position >= len(slots):
            errors.append(SemanticError(f"{variant.name} gives {len(args)} values - enum '{enum.name}' takes "
                                        f"{len(slots)}", arg.location))
            return None
        value = _constant(values, arg, errors, variant)
        if value is None:
            return None
        names[slots[position][0]] = value
        position += 1
    for name, default in slots:
        if name not in names:
            if default is None:
                errors.append(SemanticError(f"{variant.name} of enum '{enum.name}' doesn't give '{name}'",
                                            variant.location))
                return None
            names[name] = _constant(values, default, errors, variant)
    return names


def _constant(values, node, errors, variant):
    try:
        return values.value(node)
    except NotConstant as problem:
        errors.append(SemanticError(f"{variant.name}: {problem.message}", problem.node.location))
        return None


def _fill_items(enum, values, errors) -> None:
    """No fields, but values given data (D.191): each value a const fixed array of one type - SMALL[1]."""
    kinds = set()
    for variant in enum.variants:
        items = []
        for arg in variant.arguments or []:
            if isinstance(arg, NamedArgument):
                errors.append(SemanticError(f"{variant.name}: a name needs a field - enum '{enum.name}' has none",
                                            arg.location))
                return
            value = _constant(values, arg, errors, variant)
            if value is None:
                return
            items.append(value)
            kinds.add('char' if isinstance(value, Char) else 'string' if isinstance(value, str)
                      else 'bool' if isinstance(value, bool) else 'double' if isinstance(value, float) else 'whole')
        variant.items = items
    if kinds == {'whole', 'double'}:
        kinds = {'double'}
    if len(kinds) > 1:
        errors.append(SemanticError(
            f"The data of enum '{enum.name}' mixes {', '.join(sorted(kinds))} - without fields, every value holds "
            f"one type (give the enum fields for more)", enum.location))
        return
    kind = kinds.pop() if kinds else 'int'
    if kind == 'whole':
        widest = max((abs(x) for v in enum.variants for x in v.items), default=0)
        kind = next(k for k in ('int', 'long', 'int128', 'int256') if widest <= WHOLE_BITS[k][1])
    for variant in enum.variants:
        variant.items = [_fits(x, kind)[0] for x in variant.items]
    enum.items_type = kind


def _work_out_text(enum, values, errors) -> None:
    """The enum's own toString() (D.192): `return <text>` from the fields - worked out for each value now, so
    the text stays in the static table."""
    body = enum.to_string.body
    statements = body.statements if isinstance(body, BlockStmt) else [body]
    returned = statements[0].value if len(statements) == 1 and isinstance(statements[0], ReturnStmt) else None
    if returned is None and len(statements) == 1 and not isinstance(statements[0], ReturnStmt):
        returned = getattr(statements[0], 'expression', None)
    if returned is None:
        errors.append(SemanticError(
            f"toString() of enum '{enum.name}' gives its text in one line - return name, or "
            f"return \"{{name}} ({{enumTypeName}})\" (worked out when compiling)", enum.to_string.location))
        return
    for variant in enum.variants:
        names = dict(getattr(variant, 'data', None) or {})
        names.update(id=variant.value, enumTypeName=variant.name)
        try:
            text = values.value(returned, names)
        except NotConstant as problem:
            errors.append(SemanticError(f"toString() of enum '{enum.name}': {problem.message}", problem.node.location))
            return
        if not isinstance(text, str) or isinstance(text, Char):
            errors.append(SemanticError(f"toString() of enum '{enum.name}' gives text - not "
                                        f"{type(text).__name__}", enum.to_string.location))
            return
        variant.text = text
