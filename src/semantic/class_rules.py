"""Class rules checked over the whole program (Task 32.10d).

Cycles (Object_Lifetime.md O3 / O4): with OWNERSHIP an object is freed when its count reaches
0 - two objects that hold each other (`a.friend = b; b.friend = a`), or one that holds itself
(`node.next = node`), keep each other's count above 0 and are never freed. The compiler
can't see the objects, but it can see the types: a class whose fields can lead back to the
class itself - directly, through other classes, or through a List / Map / array of them -
gets a warning, once per circle of classes. The leak check then reports what a cycle left
behind (exit 5). Weak references, which break such a circle, come with Task 38.
"""

from typing import Dict, List, Optional

from src.parser.ast_nodes import (
    ArrayType, EnumDecl, ErrorDecl, FunctionDecl, ListType, MapType, StructDecl, StructType,
    VarDeclStmt,
)
from .errors import SemanticError


def _held_classes(type_node, classes: Dict[str, StructDecl]) -> List[str]:
    """The classes a field of this type can hold."""
    if isinstance(type_node, (ListType, ArrayType)):
        return _held_classes(type_node.element_type, classes)
    if isinstance(type_node, MapType):
        return _held_classes(type_node.value_type, classes)
    if isinstance(type_node, StructType) and type_node.name in classes:
        return [type_node.name]
    return []


def check_constructors(structs: List[StructDecl], type_text) -> List[SemanticError]:
    """Task 32.2b: two constructors of a class that take the same types can't be told
    apart; constructors calling each other with this(...) in a circle would never end.
    Runs after type checking - a this(...) call knows then which constructor it means."""
    errors = []
    for decl in (s for s in structs if s.is_class):
        constructors = [m for m in decl.methods if getattr(m, 'is_constructor', False)]
        text = {c.name: f"{decl.name}({', '.join(type_text(p.param_type) for p in c.parameters)})"
                for c in constructors}
        seen = {}
        for c in constructors:
            if text[c.name] in seen:
                errors.append(SemanticError(
                    f"Class '{decl.name}' has two constructors that take the same values - "
                    f"{text[c.name]} - they can't be told apart", c.location))
            seen.setdefault(text[c.name], c)
        calls = {c.name: getattr(getattr(c, 'delegate', None), 'callee', None) for c in constructors}
        reported = set()
        for start in constructors:
            path, current = [start.name], calls.get(start.name)
            while current is not None and getattr(current, 'name', None) in calls:
                name = current.name
                if name in path:
                    circle = path[path.index(name):] + [name]
                    if frozenset(circle) not in reported:
                        reported.add(frozenset(circle))
                        errors.append(SemanticError(
                            f"Constructors of '{decl.name}' call each other in a circle with "
                            f"this(...): {' -> '.join(text[n] for n in circle)} - it would never "
                            f"end", start.location))
                    break
                path.append(name)
                current = calls.get(name)
    return errors


def check_class_cycles(structs: List[StructDecl]) -> List[SemanticError]:
    """A warning for each circle of classes whose objects can hold each other."""
    classes = {s.name: s for s in structs if s.is_class}
    holds = {name: [held for f in decl.fields for held in _held_classes(f.field_type, classes)]
             for name, decl in classes.items()}
    warnings, reported = [], set()

    def circle_from(start: str) -> Optional[List[str]]:
        """The shortest way from a class back to itself, e.g. [A, B, A]."""
        paths, seen = [[start]], {start}
        while paths:
            path = paths.pop(0)
            for held in holds[path[-1]]:
                if held == start:
                    return path + [start]
                if held not in seen:
                    seen.add(held)
                    paths.append(path + [held])
        return None

    for name, decl in classes.items():
        circle = circle_from(name)
        if circle is None or frozenset(circle) in reported:
            continue
        reported.add(frozenset(circle))
        what = "itself" if len(circle) == 2 else "objects that hold it in turn"
        warnings.append(SemanticError(
            f"Class '{name}' can hold {what} ({' -> '.join(circle)}): objects that hold each "
            f"other in a circle are never freed - set one of the fields to null before "
            f"letting go (Weak references come with Task 38)", decl.location))
    return warnings


def check_visibility_written(program) -> List[SemanticError]:
    """`[visibility] required = true` (Task 32.2h): every top-level item and class member says
    who can use it - public, internal or private. main, and what the compiler makes (a
    class's default constructor, its set-up), need nothing."""
    errors = []

    def need(item, what: str, name: str):
        if not getattr(item, 'visibility_written', False):
            errors.append(SemanticError(
                f"Write who can use {what} '{name}' - public, internal or private "
                f"([visibility] required = true)", item.location))

    kinds = {EnumDecl: 'enum', ErrorDecl: 'error type', VarDeclStmt: 'module variable',
             FunctionDecl: 'function'}
    for d in program.declarations:
        if isinstance(d, FunctionDecl) and (getattr(d, 'method_of', None) or d.name == 'main'
                                            or getattr(d, 'is_static_setup', False)):
            continue
        if isinstance(d, VarDeclStmt) and getattr(d, 'static_of', None):
            continue                          # a static - checked as a member of its class
        if getattr(d, 'builtin', False):
            continue                          # the built-in error types (Task 26)
        if isinstance(d, StructDecl):
            need(d, 'class' if d.is_class else 'struct', d.name)
            if not d.is_class:
                continue
            for f in d.fields + d.static_fields:
                need(f, 'field', f.name)
            for m in d.methods + d.static_methods:
                label = 'the constructor of' if getattr(m, 'is_constructor', False) else 'function'
                need(m, label, d.name if label != 'function' else m.method_name)
        elif type(d) in kinds:
            need(d, kinds[type(d)], d.name.rsplit('.', 1)[-1])
    return errors
