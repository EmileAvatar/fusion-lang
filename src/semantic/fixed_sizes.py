"""`fixed(n)` sizes (Task 47.5, D.020, D.064): n is a whole number written, or a `const` worked out when compiling -
`fixed(MAX_NAME) string name`. Every type marked `fixed_max` gets its number here; 0 or below, or not a constant,
is an error. The checks of what is stored are the type checker's (check_fixed_value); the C keeps a List's or Map's
limit (`_limit`) and checks a string's length (fusion_fixed_str)."""

from dataclasses import fields, is_dataclass

from src.parser.ast_nodes import IdentifierExpr
from .enum_fields import ConstantValues, NotConstant
from .errors import SemanticError


def resolve_fixed_sizes(program) -> list:
    errors, seen, todo = [], set(), [program.declarations]
    values = ConstantValues(program)
    while todo:
        node = todo.pop()
        if isinstance(node, list):
            todo.extend(node)
            continue
        if not is_dataclass(node) or isinstance(node, type) or id(node) in seen:
            continue
        seen.add(id(node))
        size = getattr(node, 'fixed_max', None)
        if size is not None:
            where = getattr(node, 'fixed_location', None) or node.location
            if isinstance(size, str):
                try:
                    size = values.value(IdentifierExpr(location=where, name=size))
                except NotConstant:
                    errors.append(SemanticError(f"fixed({node.fixed_max}) - '{node.fixed_max}' isn't a constant whole "
                                                f"number", where))
                    size = None
            if size is not None and (not isinstance(size, int) or isinstance(size, bool) or size <= 0):
                errors.append(SemanticError(f"fixed({size}) - the size is a whole number above 0", where))
                size = None
            node.fixed_max = size if size is not None else 1 << 30
            if type(node).__name__ in ('ListType', 'MapType'):
                program.collection_options = True       # a change may be refused - every call checked (as 32.14)
        for f in fields(node):
            if f.name not in ('location', 'scope', 'declaration', 'callee_declaration'):
                todo.append(getattr(node, f.name))
    return errors
