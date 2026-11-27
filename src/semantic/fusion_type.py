"""The built-in enum `FusionType` (Task 47.4, D.201) - every type, described for developers and IDEs.

    print("{@1}", FusionType.INT.max)            // 2147483647 - an int
    bool b = FusionType.BOOL.max                 // true - min / max / default are the value's own type
    print("{@1}", FusionType.DOUBLE.size)        // 8
    for t in FusionType.values()
        print("{t}: {@1}", t.kind)               // INT: value ... LIST: ref

An enum with fields (47.3): `type`, `kind`, `size` (bytes; -1 when it grows with its contents) and `canBeNull` are
ordinary fields. `min`, `max` and `default` have the value's own type (INT.max an int, DOUBLE.min a double) - more than
an enum's fields can be, so the type checker reads them from TYPES when the value is written (FusionType.INT.max).
The numbers are the same as files/FusionTypes.html's table; added to a program only when it uses FusionType.
"""

from dataclasses import fields, is_dataclass

from src.parser.ast_nodes import EnumDecl, EnumVariant, LiteralExpr, PrimitiveType, StructField

LONG_MIN, LONG_MAX = -(1 << 63), (1 << 63) - 1
FLOAT_MAX, DOUBLE_MAX = 3.4028234663852886e38, 1.7976931348623157e308

# value: (type, kind, size, canBeNull, min, max, default) - min / max / default None when the type has none
TYPES = {
    'INT': ('int', 'value', 4, False, -(1 << 31), (1 << 31) - 1, 0),
    'BYTE': ('byte', 'value', 1, False, 0, 255, 0),
    'SHORT': ('short', 'value', 2, False, -(1 << 15), (1 << 15) - 1, 0),
    'LONG': ('long', 'value', 8, False, LONG_MIN, LONG_MAX, 0),
    'INT128': ('int128', 'value', 16, False, -(1 << 127), (1 << 127) - 1, 0),
    'INT256': ('int256', 'value', 32, False, -(1 << 255), (1 << 255) - 1, 0),
    'FLOAT': ('float', 'value', 4, False, -FLOAT_MAX, FLOAT_MAX, 0.0),
    'DOUBLE': ('double', 'value', 8, False, -DOUBLE_MAX, DOUBLE_MAX, 0.0),
    'DECIMAL': ('decimal', 'value', 32, False, -(10 ** 38 - 1), 10 ** 38 - 1, 0),
    'MONEY': ('money', 'value', 16, False, LONG_MIN, LONG_MAX, 0),
    'BOOL': ('bool', 'value', 1, False, False, True, False),
    'CHAR': ('char', 'value', 4, False, 0, 0x10FFFF, 0),
    'STRING': ('string', 'value', 24, False, None, None, ''),
    'BYTES': ('bytes', 'value', 24, False, None, None, None),
    'LIST': ('List', 'ref', 8, False, None, None, None),
    'MAP': ('Map', 'ref', 8, False, None, None, None),
    'STRUCT': ('struct', 'value', -1, False, None, None, None),
    'CLASS': ('class', 'ref', 8, True, None, None, None),
    'ENUM': ('enum', 'value', 4, True, None, None, None),
    'ERROR': ('Error', 'value', -1, False, None, None, None),
}
TYPED_FIELDS = ('min', 'max', 'default')


def _uses_fusion_type(program) -> bool:
    seen, todo = set(), [program.declarations]
    while todo:
        node = todo.pop()
        if isinstance(node, list):
            todo.extend(node)
            continue
        if not is_dataclass(node) or isinstance(node, type) or id(node) in seen:
            continue
        seen.add(id(node))
        if getattr(node, 'name', None) == 'FusionType':
            return True
        for f in fields(node):
            if f.name != 'location':
                todo.append(getattr(node, f.name))
    return False


def add_fusion_type_enum(program) -> None:
    """FusionType added to a program that names it (before the enums are normalised)."""
    if any(isinstance(d, EnumDecl) and d.name == 'FusionType' for d in program.declarations) \
            or not _uses_fusion_type(program):
        return
    where = program.location

    def literal(value, hint):
        return LiteralExpr(location=where, value=value, type_hint=hint)

    variants = []
    for number, (name, (kind_name, kind, size, null, *_)) in enumerate(TYPES.items()):
        variant = EnumVariant(location=where, name=name, value=number)
        variant.arguments = [literal(kind_name, 'string'), literal(kind, 'string'), literal(size, 'int'),
                             literal(null, 'bool')]
        variants.append(variant)

    def field(name, kind):
        return StructField(location=where, name=name, field_type=PrimitiveType(location=where, name=kind))

    decl = EnumDecl(location=where, name='FusionType', variants=variants,
                    fields=[field('type', 'string'), field('kind', 'string'), field('size', 'int'),
                            field('canBeNull', 'bool')])
    for f in decl.fields:
        f.is_private = False
    decl.added_by_compiler = True
    decl.fusion_type = TYPES
    program.declarations.insert(0, decl)
