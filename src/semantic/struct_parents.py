"""Structs building on structs (Task 32.8, user decisions 2026-10-28 / 29):

    struct Employee implements Person        (extends / includes mean the same)
        string employeeID

An Employee has Person's fields first, then its own. expand_struct_parents() runs before
names are resolved and gives Employee a first field named `Person`, holding the Person part -
in C, a Person inside the Employee. The type checker then reads `e.name` as `e.Person.name`,
runs Person's methods on `e.Person`, and passes `e.Person` where a Person is expected (a
copy of the Person part only). A chain works the same way: Manager -> Employee -> Person.

Rules checked here: the parent is a struct and no struct builds on itself; a field with the
same name as one it builds on is kept, with a warning (a bare `e.tel` is then an error - say
`e.Person.tel` or `e.Employee.tel`); a field can't have the name of a struct in its chain,
or of a method it builds on. Inside a method, an inherited field's or method's bare name
means `this.<name>`, the same as the struct's own.
"""

import copy
from typing import Dict, List, Optional, Set, Tuple

from src.parser.ast_nodes import (
    ArrayType, CallExpr, EnumType, ErrorType, IdentifierExpr, IndexExpr, ListType, MemberExpr,
    NamedArgument,
    PrimitiveType, ProgramNode, StructDecl, StructField, StructType, TypeNode,
)
from src.parser.parser import Parser
from .errors import SemanticError


def is_parent_field(field) -> bool:
    """The hidden first field holding the part a struct builds on."""
    return getattr(field, 'is_parent', False)


def own_fields(struct: StructDecl) -> list:
    """The fields written in the struct itself - not the part it builds on."""
    return [f for f in struct.fields if not is_parent_field(f)]


def chain(struct: StructDecl, lookup) -> List[StructDecl]:
    """The struct and every struct it builds on, nearest first: [Manager, Employee, Person].
    `lookup(name)` gives a StructDecl or None."""
    result = [struct]
    while getattr(result[-1], 'parent', None):
        parent = lookup(result[-1].parent)
        if parent is None or parent in result:
            break
        result.append(parent)
    return result


def flat_field_names(struct: StructDecl, lookup) -> List[str]:
    """Every field in the order a constructor takes them: the inherited ones first."""
    names = []
    for field in struct.fields:
        if is_parent_field(field):
            parent = lookup(field.field_type.name)
            names.extend(flat_field_names(parent, lookup) if parent else [])
        else:
            names.append(field.name)
    return names


class _NameClash(Exception):
    pass


def expand_struct_parents(program: ProgramNode) -> Tuple[List[SemanticError], List[SemanticError]]:
    """Give every struct that builds on another its parent part (see the module docstring).
    Returns (errors, warnings)."""
    structs: Dict[str, StructDecl] = {d.name: d for d in program.declarations
                                      if isinstance(d, StructDecl)}
    if not any(s.parent for s in structs.values()):
        return [], []
    errors: List[SemanticError] = []
    warnings: List[SemanticError] = []

    for struct in structs.values():
        if struct.parent and struct.parent not in structs:
            errors.append(SemanticError(
                f"Struct '{struct.name}' builds on '{struct.parent}', which isn't a struct",
                struct.location))
            struct.parent = None
    for struct in structs.values():
        seen, name = [struct.name], struct.parent
        while name:
            if name in seen:
                errors.append(SemanticError(
                    f"Struct '{struct.name}' builds on itself ({' -> '.join(seen + [name])})",
                    struct.location))
                struct.parent = None
                break
            seen.append(name)
            name = structs[name].parent

    done: Set[str] = set()

    def expand(struct: StructDecl) -> None:
        if struct.name in done:
            return
        done.add(struct.name)
        if not struct.parent:
            return
        parent = structs[struct.parent]
        expand(parent)
        ancestors = chain(parent, structs.get)
        inherited = set(flat_field_names(parent, structs.get))
        inherited_methods = {m.method_name for a in ancestors for m in a.methods}
        for field in struct.fields:
            if field.name in {a.name for a in ancestors} | {struct.name}:
                errors.append(SemanticError(
                    f"Field '{field.name}' of struct '{struct.name}' can't have the name of a "
                    f"struct it builds on", field.location))
                struct.parent = None
                return
            elif field.name in inherited_methods:
                errors.append(SemanticError(
                    f"Field '{field.name}' of struct '{struct.name}' has the name of a method of "
                    f"a struct it builds on", field.location))
            elif field.name in inherited:
                owner = next(a.name for a in ancestors
                             if field.name in (f.name for f in own_fields(a)))
                warnings.append(SemanticError(
                    f"Struct '{struct.name}' has field '{field.name}', and so does {owner} - both "
                    f"are kept; write .{owner}.{field.name} or .{struct.name}.{field.name}",
                    field.location))
        for method in struct.methods:
            if method.method_name in inherited:
                errors.append(SemanticError(
                    f"Method '{method.method_name}' of struct '{struct.name}' has the name of a "
                    f"field of a struct it builds on", method.location))
        part = StructField(location=struct.location, name=parent.name,
                           field_type=StructType(location=struct.location, name=parent.name))
        part.is_parent = True
        struct.fields.insert(0, part)

        # Inside a method, an inherited field's or method's bare name is this.<name>
        own = {f.name for f in own_fields(struct)}
        own_methods = {m.method_name for m in struct.methods}
        field_names = inherited - own
        method_names = inherited_methods - own_methods

        def fail(message):
            raise _NameClash(message)

        for method in struct.methods:
            try:
                Parser.rewrite_method_body(method, struct.name, field_names, method_names, fail)
            except _NameClash as clash:
                errors.append(SemanticError(str(clash), method.location))
        _mark_changes(struct, ancestors)

    for struct in structs.values():
        expand(struct)
    return errors, warnings


def _mark_changes(struct: StructDecl, ancestors: List[StructDecl]) -> None:
    """Which methods change `this` - now also through a method it builds on that does."""
    def changes(name: str) -> Optional[bool]:
        for owner in [struct] + ancestors:
            method = next((m for m in owner.methods if m.method_name == name), None)
            if method is not None:
                return method.changes_this
        return None

    for method in struct.methods:
        method.changes_this = Parser.assigns_this(method)
    while True:
        more = [m for m in struct.methods if not m.changes_this
                and any(changes(n) for n in Parser.this_calls(m))]
        if not more:
            return
        for method in more:
            method.changes_this = True


class StructParentRulesMixin:
    """The type checker's rules for structs building on structs (a mixin of TypeChecker)."""

    def struct_named(self, name: str) -> Optional[StructDecl]:
        symbol = self.symbol_table.global_scope.lookup(name)
        return symbol.declaration if symbol is not None and symbol.symbol_type == 'struct' else None

    def parent_path(self, child, parent) -> Optional[List[str]]:
        """The parts to go through from a struct to one it builds on - Manager to Person is
        ['Employee', 'Person'] - or None if it doesn't build on it."""
        if not (isinstance(child, StructType) and isinstance(parent, StructType)):
            return None
        decl, path = self.struct_named(child.name), []
        while decl is not None and decl.parent and decl.parent not in path:
            path.append(decl.parent)
            if decl.parent == parent.name:
                return path
            decl = self.struct_named(decl.parent)
        return None

    def _parts(self, obj, path: List[str], location):
        """obj.Employee.Person - each link typed."""
        for name in path:
            obj = MemberExpr(location=location, object=obj, member=name)
            obj.inferred_type = StructType(location=location, name=name,
                                           declaration=self.struct_named(name))
        return obj

    def as_parent_part(self, value, actual, expected) -> Optional[TypeNode]:
        """An Employee where a Person is expected: the value becomes its Person part,
        `e.Person` - a copy of that part only. Changed in place, because whatever holds the
        value (an argument list, a declaration, a return) keeps holding it. Returns the
        expected type, or None if this isn't such a case."""
        path = self.parent_path(actual, expected)
        if not path:
            return None
        part = self._parts(copy.copy(value), path, value.location)
        value.__dict__.clear()
        value.__class__ = MemberExpr
        value.__dict__.update(vars(part))
        return value.inferred_type

    def struct_member_type(self, node: MemberExpr, struct: StructDecl, object_type):
        """The type of `x.member` on a struct: its own field, the part it builds on
        (`e.Person`), `e.Employee` (e itself - its own fields), or a field it builds on -
        `e.name` becomes `e.Person.name`. None if there's no such field."""
        part = next((f for f in struct.fields if is_parent_field(f) and f.name == node.member), None)
        if part is not None:
            return part.field_type
        levels = chain(struct, self.struct_named)
        owners = [s for s in levels if any(f.name == node.member for f in own_fields(s))]
        if not owners:
            if struct.parent and node.member == struct.name:
                node.self_view = True
                return object_type
            return None
        owner = owners[0]
        if len(owners) > 1 and not (getattr(node.object, 'self_view', False) and owner is struct):
            names = ' or '.join(f".{s.name}.{node.member}" for s in owners)
            self.errors.append(SemanticError(
                f"Struct '{struct.name}' has more than one field '{node.member}' - write "
                f"{names}", node.location))
        if owner is not struct:
            path = [s.name for s in levels[1:levels.index(owner) + 1]]
            node.object = self._parts(node.object, path, node.location)
        return next(f.field_type for f in own_fields(owner) if f.name == node.member)

    def inherited_method(self, receiver, struct: StructDecl, member: str):
        """`e.greet()` where greet is a method of a struct e builds on: (the receiver's part
        that has it - e.Person, that struct, the method), or None."""
        levels = chain(struct, self.struct_named)
        for depth, owner in enumerate(levels[1:], start=1):
            method = next((m for m in owner.methods if m.method_name == member), None)
            if method is not None:
                part = self._parts(receiver, [s.name for s in levels[1:depth + 1]],
                                   receiver.location)
                return part, owner, method
        return None

    def flatten_parent_arguments(self, node, struct: StructDecl) -> None:
        """Employee("Jeff", "E7"): the fields it builds on come first, written out - the first
        values become the Person part, Employee(Person("Jeff"), "E7"); a named one goes there
        by its name. A whole Person may be given first instead: Employee(p, "E7")."""
        parent = self.struct_named(struct.parent) if struct.parent else None
        if parent is None or not node.arguments:
            return
        inherited = flat_field_names(parent, self.struct_named)
        positional = [a for a in node.arguments if not isinstance(a, NamedArgument)]
        named = [a for a in node.arguments if isinstance(a, NamedArgument)]
        first = positional[0] if positional else None
        if isinstance(first, (IdentifierExpr, CallExpr, MemberExpr, IndexExpr)):
            first_type = self.visit(first)
            self.checked_receivers[id(first)] = first_type
            parent_type = StructType(location=first.location, name=parent.name)
            if isinstance(first_type, StructType) and (first_type.name == parent.name
                                                       or self.parent_path(first_type, parent_type)):
                return
        own = {f.name for f in own_fields(struct)}
        for a in named:
            if a.name in own and a.name in inherited:
                self.errors.append(SemanticError(
                    f"Struct '{struct.name}' has more than one field '{a.name}' - give the "
                    f"values in order, or the {parent.name} part first: "
                    f"{struct.name}({parent.name}(...), ...)", a.location))
        take = positional[:len(inherited)]
        theirs = [a for a in named if a.name in inherited and a.name not in own]
        if not take and not theirs:
            return
        part = CallExpr(location=node.location, arguments=take + theirs,
                        callee=IdentifierExpr(location=node.location, name=parent.name))
        node.arguments = [part] + positional[len(take):] + [a for a in named if a not in theirs]

    def printable_problem(self, type_node, action: str = "print a whole") -> Optional[str]:
        """Why a value can't be printed whole, or None. A struct prints every field (Task
        32.8), so it can be printed when each of its fields can."""
        if isinstance(type_node, (PrimitiveType, EnumType, ErrorType)):
            return None
        struct = self.struct_declaration(type_node)
        if getattr(struct, 'is_class', False):
            return (f"Can't {action} {struct.name} object yet - use its fields one at a time "
                    f"(Task 32.2)")
        if struct is not None:
            for f in struct.fields:
                if self.printable_problem(f.field_type) is not None:
                    return (f"Can't {action} {struct.name}: its field '{f.name}' is a "
                            f"{self.type_to_string(f.field_type)} - use its fields one at a time")
            return None
        return (f"Can't print a whole {self.type_to_string(type_node)} value - print its "
                f"elements or fields one at a time")

    def csv_call(self, node) -> Optional[TypeNode]:
        """x.toCSV() / x.toCSV(";") (Task 32.13): a heading row and a row of values, on any
        struct, a one-dimensional array or a List of structs. A struct's own toCSV method, or
        the program's own toCSV function, comes first. Returns string, or None if this isn't
        one (the call is then checked as usual)."""
        receiver = node.callee.object
        if isinstance(receiver, IdentifierExpr) and self.symbol_table.lookup(receiver.name) is None:
            return None
        receiver_type = self.visit(receiver)
        self.checked_receivers[id(receiver)] = receiver_type
        kind, element = 'struct', receiver_type
        if isinstance(receiver_type, ArrayType):
            kind, element = 'array', receiver_type.element_type
        elif isinstance(receiver_type, ListType):
            kind, element = 'list', receiver_type.element_type
        struct = self.struct_declaration(element)
        if struct is None or self.user_method('toCSV', receiver_type) is not None or (
                kind == 'struct' and any(m.method_name == 'toCSV'
                                         for s in chain(struct, self.struct_named) for m in s.methods)):
            return None
        self.checked_receivers.pop(id(receiver), None)
        problem = self.printable_problem(element, "make CSV from a")
        if problem:
            self.errors.append(SemanticError(problem, node.location))
        if len(node.arguments) > 1 or any(isinstance(a, NamedArgument) for a in node.arguments):
            self.errors.append(SemanticError(
                "toCSV takes one value, the delimiter (\",\" when left out)", node.location))
        elif node.arguments:
            given = self.visit(node.arguments[0])
            if getattr(given, 'name', None) not in ('string', 'char') \
                    or not isinstance(given, PrimitiveType):
                self.errors.append(SemanticError(
                    f"The delimiter of toCSV is a string or char, not "
                    f"{self.type_to_string(given)}", node.arguments[0].location))
        node.csv = kind
        return PrimitiveType(location=node.location, name='string')
