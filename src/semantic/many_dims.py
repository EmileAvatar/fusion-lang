"""Arrays of 2 and 3 dimensions (Task 45.12a, D.143, D.148).

`int[2][3][4] cube` is rows x columns x depth. It is one flat block of every slot (FLAT, D.144), so
the rest of the compiler sees a plain array of 24: the slots get their default values, strings are
freed and the stack measure (45.13) counts it as one. What this module adds:

- the declaration: its sizes written, or taken from nested values `[[1, 2, 3], [4, 5, 6]]` (every
  row the same length); the values are put in the order the slots lie in memory
- `cube[1][2][3]` (or `cube[1],[2],[3]`): one index per dimension, each checked against its own
  size; the generator turns them into one position
- `rows`, `columns` (2 and 3 dimensions), `depth` (3 only), `length` - the outer dimension first

`[arrays] order` (D.148) decides which index varies fastest in memory - "columns" (the default):
the outer dimension first, depth -> columns -> rows, so rows vary fastest; "rows": as C, the last
index fastest. A loop (45.12b) then reads the slots one after another.

Anything else done with the whole array - a view (`cube[1]`), passing it, copying, comparing,
looping over it - comes with 45.12b / 45.12c; `check_many_dims_uses` makes each an error until then.
"""
from dataclasses import fields, is_dataclass

from src.parser.ast_nodes import (ArrayLiteralExpr, ArrayType, FunctionDecl, IdentifierExpr, IndexExpr,
                                  LiteralExpr, MemberExpr, PrimitiveType, StructDecl, TypeNode,
                                  VarDeclStmt)

from .errors import SemanticError

DIMENSION_NAMES = ('rows', 'columns', 'depth')


def strides(dims: list, order: str) -> list:
    """How far apart in the flat block one step of each index is."""
    result = []
    for k in range(len(dims)):
        step = 1
        for d in (dims[:k] if order == 'columns' else dims[k + 1:]):
            step *= d
        result.append(step)
    return result


def _name_of(expr) -> str:
    while isinstance(expr, IndexExpr):
        expr = expr.array
    return expr.name if isinstance(expr, IdentifierExpr) else 'the array'


class ManyDimsMixin:
    """The type rules of 2 and 3 dimensions - a mixin of the type checker."""

    array_order = 'columns'

    def check_many_dims_declaration(self, node: VarDeclStmt) -> None:
        """`int[2][3] m`, `int[][] m = [[1, 2, 3], [4, 5, 6]]` - the sizes, and the values flattened."""
        array = node.var_type
        dims = array.dims
        value = node.initializer
        if value is None:
            if None in dims:
                self.errors.append(SemanticError(
                    f"'{node.name}' needs its sizes or its values: {self.type_to_string(array.element_type)}"
                    f"{''.join('[2]' for _ in dims)} {node.name}, or ... = [[...], [...]]", node.location))
            return
        if not isinstance(value, ArrayLiteralExpr):
            self.visit(value)
            self.errors.append(SemanticError(
                f"An array of {len(dims)} dimensions is set from its values for now - [[1, 2], [3, 4]]; "
                f"from a function or another array comes with Task 45.12c", value.location))
            return
        found = list(dims)
        leaves = []

        def walk(literal, depth, position):
            if not isinstance(literal, ArrayLiteralExpr):
                self.errors.append(SemanticError(
                    f"'{node.name}' has {len(dims)} dimensions - this needs a list of values [...] here",
                    literal.location))
                return
            count = len(literal.elements)
            if found[depth] is None:
                found[depth] = count
            if count != found[depth]:
                what = DIMENSION_NAMES[depth] if depth < 3 else 'values'
                self.errors.append(SemanticError(
                    f"'{node.name}' needs {found[depth]} {what} here, got {count} - every row the same length "
                    f"(an irregular array is JAGG - Task 45.15)", literal.location))
                return
            for i, element in enumerate(literal.elements):
                if depth + 1 < len(dims):
                    walk(element, depth + 1, position + [i])
                else:
                    leaves.append((position + [i], element))

        before = len(self.errors)
        walk(value, 0, [])
        if len(self.errors) > before:
            return                                  # the shape is wrong - nothing more to check
        if 0 in found:
            self.errors.append(SemanticError(f"'{node.name}' needs at least one value in each dimension",
                                             value.location))
            return
        element_type = array.element_type
        for _, leaf in leaves:
            actual = self._visit_value_for(element_type, leaf)
            if not self.types_compatible(element_type, actual):
                self.errors.append(SemanticError(
                    f"A value of '{node.name}' must be {self.type_to_string(element_type)}, got "
                    f"{self.type_to_string(actual)}", leaf.location))
        total = 1
        for d in found:
            total *= d
        array.dims[:] = found
        array.size = total
        step = strides(found, self.array_order)
        flat = [None] * total
        for position, leaf in leaves:
            flat[sum(p * s for p, s in zip(position, step))] = leaf
        node.initializer = ArrayLiteralExpr(location=value.location, elements=flat)
        node.initializer.inferred_type = ArrayType(location=value.location, element_type=element_type,
                                                   size=total)

    def many_dims_index(self, node: IndexExpr, array_type: ArrayType, index_type) -> TypeNode:
        """`m[1]` on an array of many dimensions: one more index taken; all of them - the slot."""
        if not (isinstance(index_type, PrimitiveType) and index_type.name == 'int'):
            self.errors.append(SemanticError(
                f"Array index must be int, got {self.type_to_string(index_type)}", node.index.location))
        inner = node.array
        chain = getattr(inner, 'dims_chain', None) if isinstance(inner, IndexExpr) else None
        root, indices, full = chain if chain else (inner, [], array_type.dims)
        indices = indices + [node.index]
        size = full[len(indices) - 1]
        index = node.index
        if isinstance(index, LiteralExpr) and isinstance(index.value, int) and not isinstance(index.value, bool) \
                and size is not None and not 0 <= index.value < size:
            what = DIMENSION_NAMES[len(indices) - 1]
            self.errors.append(SemanticError(
                f"Index {index.value} is outside '{_name_of(root)}' - its {what} are 0 to {size - 1}",
                index.location))
        rest = full[len(indices):]
        if rest:
            node.dims_chain = (root, indices, full)
            total = 1
            for d in rest:
                total *= d or 0
            view = ArrayType(location=node.location, element_type=array_type.element_type, size=total,
                             dims=list(rest))
            view.view = True
            return view
        node.dims_slot = (root, indices, list(full), strides(full, self.array_order))
        return array_type.element_type

    def many_dims_member(self, node: MemberExpr, array_type: ArrayType):
        """`m.rows`, `m.columns`, `m.depth`, `m.length` - known while compiling. None: not one."""
        member = node.member
        if member not in DIMENSION_NAMES + ('length', 'len'):
            return None
        int_type = PrimitiveType(location=node.location, name='int')
        if getattr(array_type, 'view', False):
            self.errors.append(SemanticError(
                f"The length of a part of '{_name_of(node.object)}' comes with views (Task 45.12b)",
                node.location))
            return int_type
        dims = array_type.dims
        if member == 'depth' and len(dims) < 3:
            self.errors.append(SemanticError(
                f"'{_name_of(node.object)}' has {len(dims)} dimensions - rows and columns; depth is the third "
                f"(D.143)", node.location))
            return int_type
        if member in DIMENSION_NAMES:
            node.dims_value = dims[DIMENSION_NAMES.index(member)]
        else:       # the outer dimension first - [arrays] order (D.148)
            node.dims_value = dims[-1] if self.array_order == 'columns' else dims[0]
        return int_type


def _children(node):
    for f in fields(node):
        if f.name in ('location', 'inferred_type', 'declaration', 'scope'):
            continue
        value = getattr(node, f.name)
        if isinstance(value, list):
            for item in value:
                if is_dataclass(item) and not isinstance(item, (type, TypeNode)):
                    yield item
        elif is_dataclass(value) and not isinstance(value, (type, TypeNode)):
            yield value


def _many(type_node) -> bool:
    return isinstance(type_node, ArrayType) and bool(type_node.dims)


def check_many_dims_uses(program) -> list:
    """The uses of a many-dimension array not built yet (45.12b, 45.12c) - each an error, never a
    silent use of the flat block."""
    errors = []
    for decl in program.declarations:
        if isinstance(decl, VarDeclStmt) and _many(decl.var_type):
            errors.append(SemanticError(
                f"'{decl.name}': a module variable of many dimensions comes with Task 45.12c", decl.location))
        if isinstance(decl, StructDecl):
            for field in decl.fields:
                if _many(field.field_type):
                    errors.append(SemanticError(
                        f"Field '{field.name}': a field of many dimensions comes with Task 45.12c", field.location))
    functions = [d for d in program.declarations if isinstance(d, FunctionDecl)]
    for decl in program.declarations:
        if isinstance(decl, StructDecl):
            functions += [m for m in getattr(decl, 'methods', None) or [] if isinstance(m, FunctionDecl)]
    for function in functions:
        for param in function.parameters:
            if _many(param.param_type):
                errors.append(SemanticError(
                    f"Parameter '{param.name}': passing an array of many dimensions comes with Task 45.12c",
                    param.location))
        if _many(function.return_type):
            errors.append(SemanticError(
                f"'{function.name}': returning an array of many dimensions comes with Task 45.12c",
                function.location))
        if getattr(function, 'body', None) is None:
            continue
        seen, todo = set(), [(function.body, None)]
        while todo:
            node, parent = todo.pop()
            if id(node) in seen or isinstance(node, (FunctionDecl, StructDecl)):
                continue
            seen.add(id(node))
            kind = getattr(node, 'inferred_type', None)
            if _many(kind) and not isinstance(node, VarDeclStmt):
                allowed = (isinstance(parent, IndexExpr) and parent.array is node) or \
                          (isinstance(parent, MemberExpr) and getattr(parent, 'dims_value', None) is not None)
                if not allowed and not getattr(node, 'reported_many', False):
                    node.reported_many = True
                    if getattr(kind, 'view', False):
                        errors.append(SemanticError(
                            f"A part of '{_name_of(node)}' - a view (cube[1], cube[][2]) - comes with Task 45.12b; "
                            f"give every index: one slot", node.location))
                    else:
                        errors.append(SemanticError(
                            f"'{_name_of(node)}' has {len(kind.dims)} dimensions - for now it is used through its "
                            f"slots ({_name_of(node)}[0][0]) and rows / columns / depth / length; passing, "
                            f"copying, comparing and looping over it come with Task 45.12b-c", node.location))
            for child in _children(node):
                todo.append((child, node))
    return errors
