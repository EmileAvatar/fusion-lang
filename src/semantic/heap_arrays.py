"""Plain arrays that get a new size live on the heap (Task 45.10, D.141).

A plain array keeps its size until it is replaced: `a = [1, 2]` after `int[] a = [5, 2, 3]`, or
`a = make()` where `make` returns `int[]` of any size. Such an array can't be a C array on the stack -
its size is only known while running - so it becomes a counted block on the heap, the same block a
List uses: a `ListType` marked `array_form`. It still acts as an array: no `add` (D.141 - only
`int:[]` grows), an object slot may be null (D.140), and it is passed to an `int[]` parameter as its
items and length.

Which ones (decided here, before names are resolved, by name within each function):
- a function returning `int[]` with no size returns a heap array
- a local array replaced as a whole by an array literal, by another heap array, or by a call to a
  function returning one
- a local array set from, set into or returned as a heap array - the two sides share one form
- a local array set from `a + b` (Task 45.4) or `a.copyPart(...)` (45.5) - a new array
- an array field of a struct or class written with no size (`int[] items`)

Everything else stays a C array on the stack, as before.
"""
from dataclasses import fields, is_dataclass

from src.parser.ast_nodes import (ArrayLiteralExpr, ArrayType, AssignmentStmt, BinaryExpr, CallExpr,
                                  FunctionDecl, IdentifierExpr, ListType, MemberExpr, PassingExpr, ReturnStmt, StructDecl,
                                  VarDeclStmt)


def heap_array(array_type: ArrayType) -> ListType:
    """The heap form of `T[]`: a counted block like a List, marked as an array."""
    return ListType(location=array_type.location, element_type=array_type.element_type,
                    array_form=True)


def is_heap_array(type_node) -> bool:
    return isinstance(type_node, ListType) and getattr(type_node, 'array_form', False)


def _nodes(node):
    """Every node below `node` (not into nested functions' types)."""
    if isinstance(node, list):
        for item in node:
            yield from _nodes(item)
        return
    if not is_dataclass(node) or isinstance(node, type):
        return
    yield node
    for f in fields(node):
        if f.name in ('location', 'inferred_type', 'declaration', 'scope', 'var_type',
                      'return_type', 'param_type', 'field_type'):
            continue
        value = getattr(node, f.name)
        if isinstance(value, list) or (is_dataclass(value) and not isinstance(value, type)):
            yield from _nodes(value)


def _functions(program):
    for declaration in program.declarations:
        if isinstance(declaration, FunctionDecl):
            yield declaration
        elif isinstance(declaration, StructDecl):
            yield from (m for m in getattr(declaration, 'methods', None) or [] if isinstance(m, FunctionDecl))


def mark_heap_arrays(program) -> None:
    """Turn the plain arrays that get a new size into heap arrays (see the module notes)."""
    functions = list(_functions(program))
    heap_functions = set()
    for function in functions:
        if isinstance(function.return_type, ArrayType) and function.return_type.size is None:
            function.return_type = heap_array(function.return_type)
            heap_functions.add(function.name)
    for declaration in program.declarations:
        if isinstance(declaration, StructDecl):
            for field in declaration.fields:
                if isinstance(field.field_type, ArrayType) and field.field_type.size is None:
                    field.field_type = heap_array(field.field_type)
    for function in functions:
        _mark_locals(function, heap_functions)


def _plain(value):
    """`byVal a` / `byRef a` - the array named underneath."""
    while isinstance(value, PassingExpr):
        value = value.value
    return value


def _heap_value(value, heap_names, heap_functions) -> bool:
    value = _plain(value)
    if isinstance(value, IdentifierExpr):
        return value.name in heap_names
    # a + b (45.4), a.copyPart(0, 2) (45.5): only an array's own declaration or replacing asks
    if isinstance(value, CallExpr) and isinstance(value.callee, MemberExpr):
        return value.callee.member in ('copyPart', 'slice', 'copyPartAt', 'sliceAt')
    if isinstance(value, CallExpr):
        return isinstance(value.callee, IdentifierExpr) and value.callee.name in heap_functions
    return isinstance(value, BinaryExpr) and value.operator == '+'


def _mark_locals(function, heap_functions) -> None:
    body = getattr(function, 'body', None)
    if body is None:
        return
    nodes = list(_nodes(body))
    arrays = {n.name: n for n in nodes if isinstance(n, VarDeclStmt) and isinstance(n.var_type, ArrayType)}
    if not arrays:
        return
    returns_heap = is_heap_array(function.return_type)
    # a growable array (45.3) is on the heap already - a plain one set from it joins it there
    heap = {n.name for n in nodes if isinstance(n, VarDeclStmt) and is_heap_array(n.var_type)}
    growable = set(heap)
    changed = True
    while changed:                                   # until nothing more joins
        changed = False
        for node in nodes:
            names = set()
            if isinstance(node, VarDeclStmt) and node.name in arrays and node.initializer is not None:
                if _heap_value(node.initializer, heap, heap_functions):
                    names.add(node.name)
                elif node.name in heap and isinstance(_plain(node.initializer), IdentifierExpr):
                    names.add(_plain(node.initializer).name)
            elif isinstance(node, AssignmentStmt) and isinstance(node.target, IdentifierExpr) \
                    and node.target.name in arrays and not getattr(arrays[node.target.name], 'is_fixed', False) \
                    and not arrays[node.target.name].is_const:
                value = _plain(node.value)
                if isinstance(value, ArrayLiteralExpr) or _heap_value(value, heap, heap_functions):
                    names.add(node.target.name)
                if isinstance(value, IdentifierExpr) and (node.target.name in heap or value.name in heap):
                    names |= {node.target.name, value.name}
            elif isinstance(node, ReturnStmt) and returns_heap and isinstance(node.value, IdentifierExpr):
                names.add(node.value.name)
            names = {n for n in names if n in arrays} - heap
            if names:
                heap |= names
                changed = True
    for name in heap - growable:
        arrays[name].var_type = heap_array(arrays[name].var_type)
