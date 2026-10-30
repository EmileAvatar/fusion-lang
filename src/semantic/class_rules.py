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

from src.parser.ast_nodes import ArrayType, ListType, MapType, StructDecl, StructType
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
