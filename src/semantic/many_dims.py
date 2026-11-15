"""Arrays of 2 and 3 dimensions (Tasks 45.12a, 45.12b - D.143, D.148, D.149).

`int[2][3][4] cube` is rows x columns x depth. It is one flat block of every slot (FLAT, D.144), so
the rest of the compiler sees a plain array of 24: the slots get their default values, strings are
freed and the stack measure (45.13) counts it as one.

Slots: each dimension of the root array has an index - given (an expression), or open. `cube[1][2][3]`
gives all three: one slot, one position in the block. Fewer, or `[]`, leave some open - a **view**
(D.149): `cube[1]` (row 1: columns x depth), `cube[][2][1]` (column 2 of sheet 1: one value per
row), `cube[][][3]` (sheet 3). A view has no memory of its own; its type remembers the root, the
slots and the sizes, so `sheet[0][1]` is again one position in the root's block.

- `length`: the outer open dimension - depth, then columns, then rows (`[arrays] order` "columns",
  D.148; "rows": rows first); on one slot -1 (no error) unless the slot's value has a length
- `foreach` over an array or a view walks its outer open dimension; the loop variable is a view
  of what is left (borrowed - nothing copied), or the value itself on the last level. The indices a
  view fixes are worked out once, before the loop (HeldIndex)
- a view given to a variable is copied (`int[][] s = cube[][][3]`): numbers and strings copied,
  objects shared - `byVal` copies them too

`[arrays] order` decides which index varies fastest in memory - "columns" (the default): rows
fastest, so a loop over depth -> columns -> rows reads the slots one after another.

Passing, returning, comparing and replacing the whole array come with 45.12c;
`check_many_dims_uses` makes each an error until then.
"""
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Optional

from src.parser.ast_nodes import (ASTNode, ArrayLiteralExpr, ArrayType, ForStmt, FunctionDecl, IdentifierExpr,
                                  IndexExpr, LiteralExpr, MemberExpr, PrimitiveType, StructDecl, TypeNode,
                                  VarDeclStmt)

from .errors import SemanticError

DIMENSION_NAMES = ('rows', 'columns', 'depth')


@dataclass
class HeldIndex(ASTNode):
    """An index worked out once and kept in a C name: a loop's counter (`value` None), or an index
    a looped view fixes (`cube[r][][]` - r read once, before the loop)."""
    value: Optional[Any] = None
    c_name: str = ''
    size: int = 0


def strides(dims: list, order: str) -> list:
    """How far apart in the flat block one step of each index is."""
    result = []
    for k in range(len(dims)):
        step = 1
        for d in (dims[:k] if order == 'columns' else dims[k + 1:]):
            step *= d
        result.append(step)
    return result


def _product(values) -> int:
    total = 1
    for v in values:
        total *= v
    return total


def _root(expr):
    while isinstance(expr, IndexExpr):
        expr = expr.array
    return expr


def _name_of(expr) -> str:
    expr = _root(expr)
    return expr.name if isinstance(expr, IdentifierExpr) else 'the array'


def _many(type_node) -> bool:
    return isinstance(type_node, ArrayType) and bool(type_node.dims)


def _view_type(location, element, root, slots, full) -> ArrayType:
    """The type of a view: its open dimensions, and where it lies in the root (D.149)."""
    open_dims = [full[k] for k, s in enumerate(slots) if s is None]
    view = ArrayType(location=location, element_type=element, size=_product(open_dims), dims=open_dims)
    view.view = True
    view.view_info = (root, list(slots), list(full))
    return view


class ManyDimsMixin:
    """The type rules of 2 and 3 dimensions - a mixin of the type checker."""

    array_order = 'columns'

    def _info(self, expr, array_type) -> tuple:
        """(root, slots, full sizes) of an array or a view."""
        info = getattr(array_type, 'view_info', None)
        if info is not None:
            return info[0], list(info[1]), list(info[2])
        return expr, [None] * len(array_type.dims), list(array_type.dims)

    def _outer_open(self, slots) -> int:
        """The dimension a loop and length take first - [arrays] order (D.148)."""
        open_dims = [k for k, s in enumerate(slots) if s is None]
        return open_dims[-1] if self.array_order == 'columns' else open_dims[0]

    # ------------------------------------------------------------------ declarations

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
        if self.is_view_value(value):
            self.check_view_copy(node)
            return
        if not isinstance(value, ArrayLiteralExpr):
            self.visit(value)
            self.errors.append(SemanticError(
                f"An array of {len(dims)} dimensions is set from its values or from a part of another one "
                f"for now - [[1, 2], [3, 4]], cube[][][3]; from a function comes with Task 45.12c", value.location))
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
                self.errors.append(SemanticError(
                    f"'{node.name}' needs {found[depth]} {DIMENSION_NAMES[depth]} here, got {count} - every row "
                    f"the same length (an irregular array is JAGG - Task 45.15)", literal.location))
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
        total = _product(found)
        array.dims[:] = found
        array.size = total
        step = strides(found, self.array_order)
        flat = [None] * total
        for position, leaf in leaves:
            flat[sum(p * s for p, s in zip(position, step))] = leaf
        node.initializer = ArrayLiteralExpr(location=value.location, elements=flat)
        node.initializer.inferred_type = ArrayType(location=value.location, element_type=element_type,
                                                   size=total)

    def is_view_value(self, value) -> bool:
        """Is this - written as it is - a part of an array of many dimensions (`cube[1]`, `sheet`)?
        Decided from the names, before the value is checked."""
        inner = value
        while type(inner).__name__ == 'PassingExpr':
            inner = inner.value
        if not isinstance(inner, (IndexExpr, IdentifierExpr)):
            return False
        root = _root(inner)
        if not isinstance(root, IdentifierExpr):
            return False
        symbol = self.symbol_table.lookup(root.name)
        kind = getattr(symbol, 'data_type', None)
        if getattr(kind, 'view', False):
            return True
        return _many(kind) and isinstance(inner, IndexExpr)

    def check_view_copy(self, node: VarDeclStmt) -> None:
        """`int[][] sheet = cube[][][3]`, `int[] row = m[1]` - a copy of a view (D.149): numbers and
        strings copied, objects shared; `byVal` copies them too."""
        value = node.initializer
        by_val = by_ref = False
        if type(value).__name__ == 'PassingExpr':
            by_val, by_ref = value.by_val, not value.by_val
        kind = self.visit(value)
        var = node.var_type
        if by_ref:
            self.errors.append(SemanticError(
                f"'{node.name}': a part of an array given to a variable is a copy (D.149) - byRef can't "
                f"borrow it; loop over it instead (foreach) to use it in place", value.location))
            return
        if not getattr(kind, 'view', False):
            if _many(kind):
                self.errors.append(SemanticError(
                    f"'{node.name}': copying a whole array of many dimensions comes with Task 45.12c",
                    value.location))
            else:
                self.errors.append(SemanticError(
                    f"Cannot assign {self.type_to_string(kind)} to '{node.name}' "
                    f"({self.type_to_string(var)})", value.location))
            return
        root, slots, full = kind.view_info
        sizes = list(kind.dims)
        want = len(var.dims) if var.dims else 1
        if want != len(sizes):
            self.errors.append(SemanticError(
                f"'{node.name}' has {want} dimension{'s' if want > 1 else ''} - this part of "
                f"'{_name_of(root)}' has {len(sizes)}", value.location))
            return
        if not self.types_equal(var.element_type, kind.element_type):
            self.errors.append(SemanticError(
                f"'{node.name}' holds {self.type_to_string(var.element_type)} - '{_name_of(root)}' holds "
                f"{self.type_to_string(kind.element_type)}", value.location))
            return
        written = var.dims if var.dims else [var.size]
        if any(w is not None and w != s for w, s in zip(written, sizes)):
            self.errors.append(SemanticError(
                f"'{node.name}' is {self.type_to_string(var)} - this part of '{_name_of(root)}' is "
                f"{' x '.join(str(s) for s in sizes)}", value.location))
            return
        if var.dims:
            var.dims[:] = sizes
        var.size = _product(sizes)
        target = strides(sizes, self.array_order) if var.dims else [1]
        node.view_copy = (root, slots, full, strides(full, self.array_order), target, by_val)

    # ------------------------------------------------------------------ an index, a view

    def many_dims_index(self, node: IndexExpr, array_type: ArrayType, index_type) -> TypeNode:
        """`m[1]`, `m[]`, `m[1][2]` on an array of many dimensions or a view: the next open
        dimension given (or left open with []); all given - one slot."""
        if node.index is not None and not (isinstance(index_type, PrimitiveType) and index_type.name == 'int'):
            self.errors.append(SemanticError(
                f"Array index must be int, got {self.type_to_string(index_type)}", node.index.location))
        inner = node.array
        chain = getattr(inner, 'dims_chain', None) if isinstance(inner, IndexExpr) else None
        if chain:
            root, base, entries, full = chain
        else:
            root, base, full = self._info(inner, array_type)
            entries = []
        open_base = [k for k, s in enumerate(base) if s is None]
        if len(entries) >= len(open_base):
            self.errors.append(SemanticError(
                f"Too many indices - '{_name_of(root)}' has {len(full)} dimensions", node.location))
            return array_type.element_type
        entries = entries + [node.index]
        dim = open_base[len(entries) - 1]
        index = node.index
        if isinstance(index, LiteralExpr) and isinstance(index.value, int) and not isinstance(index.value, bool) \
                and not 0 <= index.value < full[dim]:
            self.errors.append(SemanticError(
                f"Index {index.value} is outside '{_name_of(root)}' - its {DIMENSION_NAMES[dim]} are 0 to "
                f"{full[dim] - 1}", index.location))
        slots = list(base)
        for k, entry in zip(open_base, entries):
            slots[k] = entry
        node.dims_chain = (root, base, entries, full)
        if None in slots or len(entries) < len(open_base):
            for k in open_base[len(entries):]:
                slots[k] = None
            return _view_type(node.location, array_type.element_type, root, slots, full)
        node.dims_slot = (root, slots, full, strides(full, self.array_order))
        return array_type.element_type

    def many_dims_member(self, node: MemberExpr, array_type: ArrayType):
        """`m.rows`, `m.columns`, `m.depth`, `m.length` - known while compiling. None: not one."""
        member = node.member
        if member not in DIMENSION_NAMES + ('length', 'len'):
            return None
        int_type = PrimitiveType(location=node.location, name='int')
        root, slots, full = self._info(node.object, array_type)
        if getattr(array_type, 'view', False):
            if member in DIMENSION_NAMES:
                self.errors.append(SemanticError(
                    f"{member} is the whole array's - '{_name_of(root)}.{member}'; a part has a length",
                    node.location))
                return int_type
            node.dims_value = full[self._outer_open(slots)]
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
            node.dims_value = full[self._outer_open(slots)]
        return int_type

    def slot_length(self, node: MemberExpr, slot_type) -> bool:
        """`cube[1][2][3].length` - one slot: -1, not an error (D.143), unless its value has a
        length of its own (a string, a List)."""
        if node.member not in ('length', 'len') or not isinstance(node.object, IndexExpr) \
                or not getattr(node.object, 'dims_slot', None) or self._has_length(slot_type):
            return False
        node.dims_value = -1
        return True

    # ------------------------------------------------------------------ foreach

    def many_dims_loop(self, node: ForStmt, iterable_type: ArrayType):
        """`foreach (int[][] sheet in cube)` - the outer open dimension (D.148); the loop variable is
        a view of the rest (borrowed), or the value on the last level. None after an error."""
        root, slots, full = self._info(node.iterable, iterable_type)
        self.held_count = getattr(self, 'held_count', 0) + 1
        number = self.held_count
        held = []
        for k, slot in enumerate(slots):
            if slot is None or isinstance(slot, HeldIndex):
                continue
            if isinstance(slot, LiteralExpr):
                continue                                 # a written number - nothing to work out
            slot = HeldIndex(location=slot.location, value=slot, c_name=f'fusion_at_{number}_{k}', size=full[k])
            slots[k] = slot
            held.append(slot)
        dim = self._outer_open(slots)
        counter = HeldIndex(location=node.location, value=None, c_name=f'fusion_dim_{number}', size=full[dim])
        slots[dim] = counter
        node.dims_loop = (held, counter)
        element = iterable_type.element_type
        declared = getattr(node, 'declared_type', None)
        what = DIMENSION_NAMES[dim]
        if None in slots:
            item = _view_type(node.location, element, root, slots, full)
            if declared is not None:
                want = len(declared.dims) if isinstance(declared, ArrayType) and declared.dims else \
                    (1 if isinstance(declared, ArrayType) else 0)
                if want != len(item.dims) or not self.types_equal(declared.element_type, element):
                    brackets = ''.join('[]' for _ in item.dims)
                    self.errors.append(SemanticError(
                        f"foreach over '{_name_of(root)}' gives its {what} - each one "
                        f"{self.type_to_string(element)}{brackets}: foreach ({self.type_to_string(element)}"
                        f"{brackets} x in ...)", node.location))
                    return None
        else:
            item = element
            node.dims_item = (root, slots, full, strides(full, self.array_order))
            if declared is not None and not self.types_equal(declared, element):
                self.errors.append(SemanticError(
                    f"foreach over this part of '{_name_of(root)}' gives its values - each one "
                    f"{self.type_to_string(element)}", node.location))
                return None
        return item


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


def _allowed(node, parent) -> bool:
    """A many-dimension array or a view used where it is built (45.12a, 45.12b)."""
    if isinstance(parent, IndexExpr) and parent.array is node:
        return True
    if isinstance(parent, MemberExpr) and getattr(parent, 'dims_value', None) is not None:
        return True
    if isinstance(parent, ForStmt) and parent.iterable is node and getattr(parent, 'dims_loop', None):
        return True
    if isinstance(parent, VarDeclStmt) and getattr(parent, 'view_copy', None):
        return True
    return type(parent).__name__ == 'PassingExpr'        # byVal cube[1] - its parent decides


def check_many_dims_uses(program) -> list:
    """The uses of a many-dimension array not built yet (45.12c) - each an error, never a silent use
    of the flat block."""
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
            if _many(kind) and not isinstance(node, VarDeclStmt) and not _allowed(node, parent) \
                    and not getattr(node, 'reported_many', False):
                node.reported_many = True
                if getattr(kind, 'view', False):
                    errors.append(SemanticError(
                        f"A part of '{_name_of(node)}' is used here in a loop (foreach), copied into a variable "
                        f"(int[] row = m[1]) or through its slots; passing it to a function comes with "
                        f"Task 45.12c", node.location))
                else:
                    errors.append(SemanticError(
                        f"'{_name_of(node)}' has {len(kind.dims)} dimensions - for now it is used through its "
                        f"slots ({_name_of(node)}[0][0]), its parts, foreach and rows / columns / depth / length; "
                        f"passing, copying the whole, comparing and replacing it come with Task 45.12c",
                        node.location))
            for child in _children(node):
                todo.append((child, node))
    return errors
