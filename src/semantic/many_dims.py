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

Functions (45.12c): a parameter `int[2][3] m` takes that shape; `int[][] m` takes any - its sizes
come as hidden parameters (`fusion_dim_m_0` ...), so inside the function a size may be a C name, not a
number (`strides`, `_product` build the C expression). A view passed to a parameter is copied into
a temporary first (numbers only for now). `int[2][3] function f()` returns one; `a == b` compares
two of the same shape slot by slot. `check_many_dims_uses` makes every other use an error.
"""
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Optional

from src.parser.ast_nodes import (ASTNode, ArrayLiteralExpr, ArrayType, CallExpr, ForStmt, FunctionDecl, IdentifierExpr,
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


def _times(a, b):
    """a * b - a number when both are; else the C expression (a size passed in - 45.12c)."""
    if isinstance(a, int) and isinstance(b, int):
        return a * b
    if a == 1:
        return b
    if b == 1:
        return a
    return f'({a}) * ({b})'


def strides(dims: list, order: str) -> list:
    """How far apart in the flat block one step of each index is."""
    result = []
    for k in range(len(dims)):
        step = 1
        for d in (dims[:k] if order == 'columns' else dims[k + 1:]):
            step = _times(step, d)
        result.append(step)
    return result


def _product(values):
    total = 1
    for v in values:
        total = _times(total, v)
    return total


def _known(sizes) -> bool:
    return all(isinstance(s, int) for s in sizes)


DIMENSION_VALUES = ('ROWS', 'COLUMNS', 'DEPTH')


def add_dimension_enum(program) -> None:
    """The built-in enum `Dimension` - ROWS, COLUMNS, DEPTH (45.12d, D.143) - added to a program
    that uses it (`expand`, one of its names), so no other program carries it."""
    from src.parser.ast_nodes import EnumDecl, EnumVariant
    if any(isinstance(d, EnumDecl) and d.name == 'Dimension' for d in program.declarations):
        return
    names = {'Dimension', 'expand'} | set(DIMENSION_VALUES)
    seen, todo, used = set(), [program], False
    while todo and not used:
        node = todo.pop()
        if isinstance(node, list):
            todo.extend(node)
            continue
        if not is_dataclass(node) or isinstance(node, type) or id(node) in seen:
            continue
        seen.add(id(node))
        if getattr(node, 'name', None) in names or getattr(node, 'member', None) in names:
            used = True
        for f in fields(node):
            if f.name != 'location':
                todo.append(getattr(node, f.name))
    if used:
        where = program.location
        program.declarations.insert(0, EnumDecl(location=where, name='Dimension', variants=[
            EnumVariant(location=where, name=v, value=k) for k, v in enumerate(DIMENSION_VALUES)]))


def name_parameter_sizes(program) -> None:
    """`int[][] m` - a parameter of any size (45.12c): each size becomes the C name of a hidden
    parameter, `fusion_dim_m_0` ..."""
    functions = [d for d in program.declarations if isinstance(d, FunctionDecl)]
    for decl in program.declarations:
        if isinstance(decl, StructDecl):
            functions += [m for m in getattr(decl, 'methods', None) or [] if isinstance(m, FunctionDecl)]
    for function in functions:
        for param in function.parameters:
            kind = param.param_type
            if _many(kind) and None in kind.dims:
                kind.dims[:] = [f'fusion_dim_{param.name}_{k}' for k in range(len(kind.dims))]


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

    def check_array_from_name(self, node: VarDeclStmt) -> bool:
        """`int[2][3] n = m` / `int[3] b = a` (45.12e, D.025): a whole array on the stack given to a new
        one - the slots copied, and `m` moved (it can't be used after - the ownership check); `byVal m`
        a deep copy, `m` still usable. Returns False when this isn't one (the usual checks run)."""
        from src.parser.ast_nodes import PassingExpr
        value, target = node.initializer, node.var_type
        deep = isinstance(value, PassingExpr)
        source = value.value if deep else value
        if deep and not value.by_val or not isinstance(source, IdentifierExpr):
            return False
        if target.growable or getattr(target, 'array_form', False):
            return False
        symbol = self.symbol_table.lookup(source.name)
        kind = getattr(symbol, 'data_type', None)
        if not isinstance(kind, ArrayType) or kind.growable or getattr(kind, 'view', False):
            return False
        self.visit(value)
        node.many_ok = True                 # its own errors below - not "used as a whole" as well
        given = list(kind.dims) if kind.dims else [kind.size]
        wanted = list(target.dims) if target.dims else [target.size]
        shape = self.type_to_string(kind)
        if len(given) != len(wanted) or self.type_to_string(kind.element_type) != \
                self.type_to_string(target.element_type):
            self.errors.append(SemanticError(
                f"'{node.name}' is {self.type_to_string(target)}, '{source.name}' is {shape} - a whole array "
                f"is given to one of the same type", node.location))
            return True
        if not all(isinstance(g, int) for g in given):
            self.errors.append(SemanticError(
                f"'{source.name}' takes any size - its sizes are known only while running; copy it slot by "
                f"slot, or give the parameter its sizes", node.location))
            return True
        for w, g in zip(wanted, given):
            if w is not None and w != g:
                self.errors.append(SemanticError(
                    f"'{node.name}' is {self.type_to_string(target)}, '{source.name}' is {shape} - the sizes "
                    f"must agree (or leave them out: {self.type_to_string(target.element_type)}"
                    f"{'[]' * len(given)} {node.name} = {source.name})", node.location))
                return True
        if target.dims:
            target.dims[:] = given
        target.size = kind.size
        node.array_from = (source, deep)
        node.many_ok = True
        return True

    def check_many_dims_replace(self, node, symbol) -> None:
        """`m = [[...]]`, `m = n` / `byVal n`, `m = make()` on an array of many dimensions on the stack
        (45.12e part 3): the same shape - the slots replaced (the new values made first, then the old
        ones freed). Another shape needs the heap - not built yet."""
        from src.parser.ast_nodes import PassingExpr
        target = symbol.data_type
        name = node.target.name
        value = node.value
        shape = self.type_to_string(target)
        if target.growable or not _known(target.dims):
            self.visit(value)
            node.target.many_ok_target = True
            self.errors.append(SemanticError(
                f"Replacing the whole of '{name}' ({shape}) comes with Task 45.12e part 3b - a growable array "
                f"or a parameter of any size", node.location))
            return
        node.target.many_ok_target = True
        if isinstance(value, ArrayLiteralExpr):
            probe = VarDeclStmt(location=node.location, name=name,
                                var_type=ArrayType(location=target.location, element_type=target.element_type,
                                                   size=None, dims=[None] * len(target.dims)),
                                initializer=value)
            before = len(self.errors)
            self.check_many_dims_declaration(probe)
            if len(self.errors) > before:
                return
            if list(probe.var_type.dims) != list(target.dims):
                self.errors.append(SemanticError(
                    f"'{name}' is {shape} - these values are {self.type_to_string(probe.var_type)}; another shape "
                    f"comes with Task 45.12e part 3b (on the heap)", value.location))
                return
            node.value = probe.initializer
            node.many_replace = 'values'
            return
        deep = isinstance(value, PassingExpr) and value.by_val
        source = value.value if deep else value
        if isinstance(source, IdentifierExpr) and not (isinstance(value, PassingExpr) and not value.by_val):
            kind = self.visit(value)
            if isinstance(kind, ArrayType) and kind.dims and not getattr(kind, 'view', False) \
                    and not kind.growable:
                if list(kind.dims) != list(target.dims) or not self.types_equal(kind.element_type,
                                                                               target.element_type):
                    self.errors.append(SemanticError(
                        f"'{name}' is {shape}, '{source.name}' is {self.type_to_string(kind)} - the same shape "
                        f"only for now; another comes with Task 45.12e part 3b (on the heap)", value.location))
                    return
                node.array_from = (source, deep)
                node.many_replace = 'array'
                source.many_ok_source = value.many_ok_source = True
                return
            self.errors.append(SemanticError(
                f"'{name}' is {shape} - it is replaced by values ([[...]]), another array of its shape or a "
                f"function giving one", value.location))
            return
        if isinstance(value, CallExpr):
            self._allow_array_call(value)
            kind = self.visit(value)
            if not _many(kind) or getattr(kind, 'view', False) or list(kind.dims) != list(target.dims) \
                    or not self.types_equal(kind.element_type, target.element_type):
                self.errors.append(SemanticError(
                    f"'{name}' is {shape} - this gives {self.type_to_string(kind)}", value.location))
                return
            node.many_replace = 'call'
            value.many_ok_source = True
            return
        self.visit(value)
        self.errors.append(SemanticError(
            f"'{name}' is {shape} - it is replaced by values ([[...]]), another array of its shape or a "
            f"function giving one", value.location))

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
            elif array.growable:
                self._grid_sizes(node, list(dims))
            return
        if array.growable and not isinstance(value, ArrayLiteralExpr):
            self.visit(value)
            self.errors.append(SemanticError(
                f"A growable array of many dimensions starts from its sizes or its values - "
                f"int:[2][3] {node.name}, or int:[][] {node.name} = [[...], [...]]", value.location))
            return
        if self.is_view_value(value):
            self.check_view_copy(node)
            return
        if not isinstance(value, ArrayLiteralExpr):
            if self.check_many_dims_from_call(node):       # int[2][3] m = make() (45.12c)
                return
            self.errors.append(SemanticError(
                f"An array of {len(dims)} dimensions is set from its values, a part of another one or a "
                f"function giving one, or another whole array - [[1, 2], [3, 4]], cube[][][3], make(), m",
                value.location))
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
        if array.growable:
            self._grid_sizes(node, found)

    def _grid_sizes(self, node: VarDeclStmt, start: list) -> None:
        """A growable array of many dimensions (45.12d): its sizes change while running, so from now
        on each is the C name that holds it - `fusion_dim_g[0]` ... (as a parameter's, 45.12c)."""
        array = node.var_type
        node.grid_start = list(start)
        array.dims[:] = [f'fusion_dim_{node.name}[{k}]' for k in range(len(start))]
        array.size = None
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
        if not isinstance(root, IdentifierExpr):
            self.errors.append(SemanticError(
                "A part of an array a function gives - keep the array in a variable first", value.location))
            return
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
        if not _known(sizes):
            self.errors.append(SemanticError(
                f"'{node.name}': copying a part of an array of any size (a parameter int[][]) comes later - "
                f"loop over it (foreach) to use it in place", value.location))
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
        node.many_ok = True

    def check_many_dims_from_call(self, node: VarDeclStmt) -> bool:
        """`int[2][3] m = make()` (45.12c): a function giving an array of that shape. False: not one."""
        if not isinstance(node.initializer, CallExpr):
            self.visit(node.initializer)                  # another array, whole - 45.12d
            return False
        self._allow_array_call(node.initializer)          # a returned array, stored (18.2.4)
        kind = self.visit(node.initializer)
        if not _many(kind) or getattr(kind, 'view', False):
            return False
        var = node.var_type
        if len(var.dims) != len(kind.dims) or not self.types_equal(var.element_type, kind.element_type) \
                or any(w is not None and w != k for w, k in zip(var.dims, kind.dims)):
            self.errors.append(SemanticError(
                f"'{node.name}' is {self.type_to_string(var)} - this gives {self.type_to_string(kind)}",
                node.initializer.location))
            return True
        if not _known(kind.dims):
            self.errors.append(SemanticError(
                f"'{node.name}': copying a whole array of any size comes later", node.initializer.location))
            return True
        var.dims[:] = list(kind.dims)
        var.size = _product(kind.dims)
        node.many_ok = True
        return True

    def check_many_dims_argument(self, error, arg, expected: ArrayType, actual) -> None:
        """An array of many dimensions, or a view, passed to an array parameter (45.12c, D.149)."""
        if not isinstance(actual, ArrayType):
            error(f"expected {self.type_to_string(expected)}, got {self.type_to_string(actual)}")
            return
        want = len(expected.dims) if expected.dims else 1
        have = len(actual.dims) if actual.dims else 1
        if want != have:
            error(f"expected {self.type_to_string(expected)} - {want} dimension{'s' if want > 1 else ''}, "
                  f"got {self.type_to_string(actual)} - {have}")
            return
        if not self.types_equal(expected.element_type, actual.element_type):
            error(f"expected an array of {self.type_to_string(expected.element_type)}, got an array of "
                  f"{self.type_to_string(actual.element_type)} (array element types must match exactly)")
            return
        wanted = expected.dims if expected.dims else [expected.size]
        given = actual.dims if actual.dims else [actual.size]
        if any(isinstance(w, int) and w != g for w, g in zip(wanted, given)):
            error(f"expected {self.type_to_string(expected)}, got {self.type_to_string(actual)} - "
                  f"another shape")
            return
        if getattr(actual, 'view', False):
            if not isinstance(actual.view_info[0], IdentifierExpr):
                error("a part of an array a function gives - keep the array in a variable first")
                return
            element = actual.element_type
            plain = (isinstance(element, PrimitiveType) and element.name not in ('string', 'bytes')) \
                or type(element).__name__ == 'EnumType'          # numbers, bools, chars, enums
            if not plain:
                error(f"passing a part of an array of {self.type_to_string(actual.element_type)} comes later - "
                      f"copy it into a variable first (... row = m[1]) and pass that")
                return
            if not _known(actual.dims) or not _known(actual.view_info[2]):
                error("passing a part of an array of any size comes later - loop over it (foreach)")
                return
            arg.view_pass = True
            sizes = list(actual.dims)          # the steps in the root, and in the temporary's own order
            arg.view_steps = (strides(actual.view_info[2], self.array_order),
                              strides(sizes, self.array_order) if len(sizes) > 1 else [1])
        arg.many_passed = True

    def check_many_dims_equality(self, node, left, right) -> None:
        """`a == b` on arrays of many dimensions (45.12c): the same shape, slot by slot."""
        for side in (left, right):
            if getattr(side, 'view', False):
                self.errors.append(SemanticError(
                    "Comparing a part of an array comes later - copy it into a variable first (int[] row = m[1])",
                    node.location))
                return
        if not (_many(left) and _many(right)) or left.dims != right.dims \
                or not self.types_equal(left.element_type, right.element_type):
            self.errors.append(SemanticError(
                f"Can't compare {self.type_to_string(left)} with {self.type_to_string(right)} - arrays of many "
                f"dimensions compare when they have the same shape", node.location))
            return
        if not _known(left.dims):
            self.errors.append(SemanticError("Comparing arrays of any size comes later", node.location))
            return
        node.many_compare = True

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
                and isinstance(full[dim], int) and not 0 <= index.value < full[dim]:
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

    def many_dims_expand(self, node, array_type: ArrayType):
        """`g.expand(ROWS, 1)` (45.12d, D.143): a growable array gets n more rows, columns or depth -
        it stays a cube; always a warning, every slot is copied."""
        void = PrimitiveType(location=node.location, name='void')
        name = _name_of(node.callee.object)
        if not array_type.growable or getattr(array_type, 'view', False):
            self.errors.append(SemanticError(
                f"expand: '{name}' doesn't grow - only a growable array does (D.141, D.143): "
                f"{self.type_to_string(array_type.element_type)}:{''.join('[2]' for _ in array_type.dims)} {name}",
                node.location))
            return void
        if len(node.arguments) != 2:
            self.errors.append(SemanticError("expand takes two values: the dimension (ROWS, COLUMNS, DEPTH) "
                                             "and how many", node.location))
            return void
        symbol = self.symbol_table.lookup('Dimension')
        dimension = getattr(symbol, 'data_type', None)
        which, count = node.arguments
        if isinstance(which, LiteralExpr) and isinstance(which.value, int) and not isinstance(which.value, bool):
            self.errors.append(SemanticError(
                "expand by a number - expand(0, 1) - comes with the Collections library; write "
                "expand(ROWS, 1), expand(COLUMNS, 1) or expand(DEPTH, 1)", which.location))
            return void
        kind = self._visit_value_for(dimension, which) if dimension is not None else self.visit(which)
        if not self.types_equal(kind, dimension):
            self.errors.append(SemanticError(
                f"expand: the dimension is ROWS, COLUMNS or DEPTH, got {self.type_to_string(kind)}", which.location))
            return void
        member = getattr(getattr(which, 'enum_value', None), 'member', None) or getattr(which, 'member', None)
        if member == 'DEPTH' and len(array_type.dims) < 3:
            self.errors.append(SemanticError(
                f"'{name}' has 2 dimensions - rows and columns; DEPTH is the third", which.location))
        if name in getattr(self, 'looped_grids', ()):
            self.errors.append(SemanticError(
                f"'{name}' is being looped over - it can't expand inside the loop (D.058); expand it before "
                f"or after the loop", node.location))
        many = self.visit(count)
        if not (isinstance(many, PrimitiveType) and many.name == 'int'):
            self.errors.append(SemanticError(f"expand: how many is an int, got {self.type_to_string(many)}",
                                             count.location))
        self.warnings.append(SemanticError(
            f"expand copies every slot of '{name}' into a new block - give it its full size when it is made "
            f"where you can (D.143)", node.location))
        node.grid_expand = (node.callee.object, len(array_type.dims), array_type.element_type, self.array_order)
        node.callee.grid_expand_callee = True
        return void

    def many_dims_to_list(self, node, array_type: ArrayType):
        """`cube.toList()` (45.11): a List of Lists in the loop's order - the outer dimension first
        (depth -> columns -> rows; [arrays] order rows: rows first), as foreach gives them. A copy."""
        from src.parser.ast_nodes import ListType
        receiver = node.callee.object
        root, slots, full = self._info(receiver, array_type)
        if not isinstance(root, IdentifierExpr):
            self.errors.append(SemanticError(
                "toList on an array a function gives - keep the array in a variable first", node.location))
        if node.arguments:
            given = node.arguments[0]
            self.visit(given)
            if len(node.arguments) > 1 or not (isinstance(given, LiteralExpr) and given.value is True):
                self.errors.append(SemanticError(
                    "An array's toList always copies - leave the value out", given.location))
        order, left = [], list(slots)
        while None in left:
            dim = self._outer_open(left)
            order.append(dim)
            left[dim] = 'taken'
        result = array_type.element_type
        for _ in order:
            result = ListType(location=node.location, element_type=result)
        self._check_collection_type(result, node.location)
        node.dims_to_list = (root, slots, full, strides(full, self.array_order), order)
        node.callee.many_callee = True
        return result

    CSV_DELIMITERS = ('primaryDelimiter', 'secondaryDelimiter', 'lineDelimiter')
    CSV_PLAIN = ('int', 'byte', 'float', 'double', 'string', 'bool', 'char')

    def plain_csv_array(self, array_type) -> bool:
        """An array (one dimension, many, a view, on the heap) of plain values - toCSV per D.151."""
        from src.parser.ast_nodes import EnumType
        if not (isinstance(array_type, ArrayType) or getattr(array_type, 'array_form', False)
                or getattr(array_type, 'growable', False)):
            return False
        element = array_type.element_type
        return isinstance(element, EnumType) or (isinstance(element, PrimitiveType)
                                                 and element.name in self.CSV_PLAIN)

    def array_csv(self, node, receiver, array_type):
        """`m.toCSV(",", "#", "\\n")` (45.11b, D.151): a line per row, the values split by the primary
        delimiter; 3 dimensions: each line that row of every sheet side by side, split by the
        secondary. Each delimiter positional or named, a string or a char."""
        from src.parser.ast_nodes import NamedArgument
        given = [None, None, None]
        for k, arg in enumerate(node.arguments):
            if isinstance(arg, NamedArgument):
                if arg.name not in self.CSV_DELIMITERS:
                    self.errors.append(SemanticError(
                        f"toCSV has no value '{arg.name}' - it takes {', '.join(self.CSV_DELIMITERS)}",
                        arg.location))
                    continue
                slot, value = self.CSV_DELIMITERS.index(arg.name), arg.value
            elif k < 3:
                slot, value = k, arg
            else:
                self.errors.append(SemanticError(
                    "toCSV takes three values at most: the primary, secondary and line delimiters "
                    "(\",\", \"#\", \"\\n\" when left out)", arg.location))
                continue
            kind = self.visit(value)
            if not (isinstance(kind, PrimitiveType) and kind.name in ('string', 'char')):
                self.errors.append(SemanticError(
                    f"A delimiter of toCSV is a string or char, not {self.type_to_string(kind)}",
                    value.location))
            given[slot] = value
        node.csv_delimiters = given
        string = PrimitiveType(location=node.location, name='string')
        if not getattr(array_type, 'dims', None):
            node.csv = 'plain'
            return string
        root, slots, full = self._info(receiver, array_type)
        if not isinstance(root, IdentifierExpr):
            self.errors.append(SemanticError(
                "toCSV on an array a function gives - keep the array in a variable first", node.location))
        open_dims = [k for k, s in enumerate(slots) if s is None]
        if len(open_dims) >= 3 and not getattr(self, 'csv_many_dimensions', True):
            self.errors.append(SemanticError(
                "toCSV on an array of 3 dimensions is off ([arrays] csvManyDimensions = false) - "
                "toCSV each sheet (cube[][][0]) or turn it on (D.151)", node.location))
        node.csv = 'dims'
        node.csv_dims = (root, slots, full, strides(full, self.array_order), open_dims)
        node.callee.many_callee = True
        return string

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
        if not isinstance(root, IdentifierExpr):
            self.errors.append(SemanticError(
                "foreach over an array a function gives - keep it in a variable first", node.location))
            return None
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
        node.dims_loop = (held, counter, root.name)      # the name: no expand inside (45.12d)
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


def _sized_example(type_node) -> str:
    """int[2][3] - an example of the type with its sizes written."""
    from src.parser.parser import type_text
    return type_text(type_node.element_type) + ''.join('[2]' for _ in type_node.dims)


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
    if isinstance(parent, MemberExpr) and (getattr(parent, 'grid_expand_callee', False)
                                           or getattr(parent, 'many_callee', False)):
        return True                                        # g.expand(ROWS, 1) (45.12d), cube.toList() (45.11)
    if isinstance(parent, ForStmt) and parent.iterable is node and getattr(parent, 'dims_loop', None):
        return True
    if isinstance(parent, VarDeclStmt) and getattr(parent, 'many_ok', False):
        return True                                        # a copy of a part; from a function (45.12c)
    if getattr(node, 'many_ok_target', False) or getattr(node, 'many_ok_source', False):
        return True                                        # m = [[...]] / m = n / m = make() (45.12e)
    if getattr(node, 'many_passed', False):
        return True                                        # passed to an array parameter (45.12c)
    if getattr(parent, 'many_compare', False):
        return True                                        # a == b (45.12c)
    if type(parent).__name__ == 'ReturnStmt' and not getattr(node.inferred_type, 'view', False):
        return True                                        # returned - its type was checked (45.12c)
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
        if _many(function.return_type) and not _known(function.return_type.dims):
            errors.append(SemanticError(
                f"'{function.name}': give the sizes it returns - "
                f"{_sized_example(function.return_type)} function {function.name}(...); an array of any size "
                f"returned (on the heap) comes later", function.location))
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
                        f"A part of '{_name_of(node)}' is used in a loop (foreach), copied into a variable "
                        f"(int[] row = m[1]), passed to an array parameter or through its slots", node.location))
                else:
                    errors.append(SemanticError(
                        f"'{_name_of(node)}' has {len(kind.dims)} dimensions - it is used through its slots "
                        f"({_name_of(node)}[0][0]), its parts, foreach, rows / columns / depth / length, passed "
                        f"to an array parameter, returned, compared (==) or given to a new array (int[2][3] n = "
                        f"{_name_of(node)}); replacing the whole comes with Task 45.12e", node.location))
            for child in _children(node):
                todo.append((child, node))
    return errors
