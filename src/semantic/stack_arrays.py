"""Arrays on the stack, measured in bytes (Task 45.13, D.145).

A plain or fixed array that stays a C array lives on the stack, which is small (1 MB on Windows).
After type checking, each local array - or a local struct holding arrays - is measured: above
`[arrays] stackWarn` (16KB) a warning, above `stackLimit` (64KB) a compile error. A growable array
(`int:[]`), a replaced one and a List live on the heap and aren't measured; neither are module
variables (not on the stack) or parameters (passed by reference).

The sizes are the C sizes the code generator uses: int, float and char 4 bytes, double 8, bool and
byte 1, a string 24; an object, List or Map is a reference (8); a struct its fields, aligned as C
aligns them.
"""
from dataclasses import fields, is_dataclass

from src.parser.ast_nodes import (ArrayType, FunctionDecl, PrimitiveType, StructDecl, StructType, TypeNode,
                                  VarDeclStmt)

from .errors import SemanticError
from .heap_arrays import _functions

_SIZES = {'int': 4, 'float': 4, 'double': 8, 'bool': 1, 'char': 4, 'byte': 1, 'string': 24, 'bytes': 24}


def size_and_alignment(type_node, structs: dict, seen=()) -> tuple:
    """(bytes, alignment) of a value of this type in C."""
    if isinstance(type_node, ArrayType):
        if type_node.size is None:
            return 8, 8                                  # a parameter's pointer
        size, align = size_and_alignment(type_node.element_type, structs, seen)
        return size * type_node.size, align
    if isinstance(type_node, PrimitiveType):
        size = _SIZES.get(type_node.name, 8)
        return size, min(size, 8)
    if type(type_node).__name__ == 'EnumType':
        return 4, 4
    if isinstance(type_node, StructType):
        decl = type_node.declaration or structs.get(type_node.name)
        if decl is None or getattr(decl, 'is_class', False) or type_node.name in seen:
            return 8, 8                                  # an object: a reference
        offset, widest = 0, 1
        for field in decl.fields:
            size, align = size_and_alignment(field.field_type, structs, seen + (type_node.name,))
            offset = (offset + align - 1) // align * align + size
            widest = max(widest, align)
        return (offset + widest - 1) // widest * widest, widest
    return 8, 8                                          # a List, Map, function: a reference


def _holds_array(type_node, structs: dict, seen=()) -> bool:
    if isinstance(type_node, ArrayType):
        return type_node.size is not None
    if isinstance(type_node, StructType):
        decl = type_node.declaration or structs.get(type_node.name)
        if decl is None or getattr(decl, 'is_class', False) or type_node.name in seen:
            return False
        return any(_holds_array(f.field_type, structs, seen + (type_node.name,)) for f in decl.fields)
    return False


def _declarations(body):
    """Every VarDeclStmt in a function's body. After type checking a node may point back at a
    declaration (a call at its function - a recursive one at itself), so each node is visited once
    and a function or struct reached that way is never entered; types are skipped."""
    seen, todo = set(), [body]
    while todo:
        node = todo.pop()
        if isinstance(node, list):
            todo.extend(node)
            continue
        if not is_dataclass(node) or isinstance(node, (type, TypeNode, FunctionDecl, StructDecl)) \
                or id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, VarDeclStmt):
            yield node
        for f in fields(node):
            if f.name not in ('location', 'inferred_type', 'declaration', 'scope'):
                todo.append(getattr(node, f.name))


def check_stack_arrays(program, stack_warn: int, stack_limit: int) -> tuple:
    """(errors, warnings) for the local arrays too large for the stack."""
    structs = {d.name: d for d in program.declarations if isinstance(d, StructDecl)}
    errors, warnings = [], []
    for function in _functions(program):
        if not isinstance(function, FunctionDecl) or getattr(function, 'body', None) is None:
            continue
        for node in _declarations(function.body):
            if not _holds_array(node.var_type, structs):
                continue
            size, _ = size_and_alignment(node.var_type, structs)
            if size > stack_limit:
                errors.append(SemanticError(
                    f"'{node.name}' takes {size:,} bytes on the stack - more than [arrays] stackLimit "
                    f"({stack_limit:,} bytes); make it smaller, use a growable array (int:[]) or a List - "
                    f"both live on the heap - or raise stackLimit (D.145)", node.location))
            elif size > stack_warn:
                warnings.append(SemanticError(
                    f"'{node.name}' takes {size:,} bytes on the stack - more than [arrays] stackWarn "
                    f"({stack_warn:,} bytes); the stack is small (1 MB on Windows) - a growable array "
                    f"(int:[]) or a List lives on the heap (D.145)", node.location))
    return errors, warnings
