"""Interfaces (Task 32.5a, Decisions.md D.006, D.087): what an interface needs, and which
class gives each of its functions.

An interface is a class-like StructDecl (is_interface) whose functions are signatures -
`Shape.area(Shape this)` with no body. Before names are resolved this pass:
- checks what each interface builds on (interfaces only, no circle) and gives it every
  function of those it builds on (`D.m` for A's `m`), so a D value can call them all;
- turns a function with a body into a default method - only when [interfaces]
  defaultMethods allows it (D.006);
- checks each class that implements interfaces: every function there, public, with the same
  parameters and result; records which function answers each one, for the code generator's
  tables (class.interface_impls) and the full list (class.all_interfaces);
- marks an interface function as changing its object when any class's function does (so a
  readonly value is checked through an interface too - Task 32.2e).
"""

import copy
from dataclasses import fields, is_dataclass
from typing import List

from src.parser.ast_nodes import FunctionDecl, ParameterDecl, PrimitiveType, StructDecl, StructType
from .errors import SemanticError


def _type_text(t) -> str:
    """A type, as text that is equal for equal types (written before names are resolved)."""
    if t is None:
        return 'void'
    if not is_dataclass(t):
        return str(t)
    parts = []
    for f in fields(t):
        if f.name in ('location', 'declaration', 'inferred_type'):
            continue
        value = getattr(t, f.name)
        if isinstance(value, list):
            parts.append('[' + ','.join(_type_text(v) for v in value) + ']')
        else:
            parts.append(_type_text(value))
    return f"{type(t).__name__}({','.join(parts)})"


def _shown(t) -> str:
    """A type as it is written - for messages."""
    name = getattr(t, 'name', None)
    if name:
        return name
    element = getattr(t, 'element_type', None)
    if element is not None and type(t).__name__ == 'ListType':
        return f'List<{_shown(element)}>'
    return type(t).__name__.replace('Type', '')


def _signature(method: FunctionDecl) -> str:
    params = ', '.join(f'{_shown(p.param_type)} {p.name}' for p in method.parameters[1:])
    error = ', Error' if getattr(method, 'returns_error', False) else ''
    return f'{_shown(method.return_type)}{error} function {method.method_name}({params})'


def _same_signature(a: FunctionDecl, b: FunctionDecl) -> bool:
    if _type_text(a.return_type) != _type_text(b.return_type):
        return False
    if getattr(a, 'returns_error', False) != getattr(b, 'returns_error', False):
        return False
    pa, pb = a.parameters[1:], b.parameters[1:]
    return len(pa) == len(pb) and all(_type_text(x.param_type) == _type_text(y.param_type)
                                      for x, y in zip(pa, pb))


# Fusion's own interfaces (Task 32.5b) - added to a program only when something uses them
BUILTIN_INTERFACES = {
    'ToString': [('string', 'toString')],      # how an object prints (Classes.md section 6)
    'Cloneable': [],                           # its own clone() - checked below (32.5b, D.088)
}


def _add_builtin_interfaces(program, structs) -> List[SemanticError]:
    """Give the program each of Fusion's own interfaces that one of its types implements."""
    errors, used = [], {n for d in structs.values() for n in d.interfaces}
    for name, signatures in BUILTIN_INTERFACES.items():
        if name in structs:
            errors.append(SemanticError(f"'{name}' is Fusion's own interface - give yours another "
                                        f"name", structs[name].location))
            continue
        if name not in used:
            continue
        where = next(d for d in structs.values() if name in d.interfaces).location
        decl = StructDecl(location=where, name=name, fields=[], is_class=True, is_interface=True)
        decl.builtin = True
        for result, method_name in signatures:
            method = FunctionDecl(location=where, return_type=PrimitiveType(location=where, name=result),
                                  name=f'{name}.{method_name}', parameters=[
                                      ParameterDecl(location=where, name='this', default_value=None,
                                                    param_type=StructType(location=where, name=name))],
                                  body=None, is_public=True)
            method.method_name, method.method_of, method.interface_of = method_name, name, name
            method.changes_this = False
            decl.methods.append(method)
            program.declarations.append(method)
        program.declarations.insert(0, decl)
        structs[name] = decl
    return errors


def check_interfaces(program, default_methods: bool = False) -> List[SemanticError]:
    errors = []
    structs = {d.name: d for d in program.declarations if isinstance(d, StructDecl)}
    errors += _add_builtin_interfaces(program, structs)
    interfaces = {n: d for n, d in structs.items() if d.is_interface}

    # What each interface builds on: interfaces only, never in a circle
    for decl in interfaces.values():
        for parent in decl.interfaces:
            other = structs.get(parent)
            if other is None:
                errors.append(SemanticError(f"Interface '{decl.name}' builds on '{parent}', which "
                                            f"isn't an interface that exists", decl.location))
            elif not other.is_interface:
                errors.append(SemanticError(f"Interface '{decl.name}' can only build on interfaces - "
                                            f"'{parent}' is a {'class' if other.is_class else 'struct'}",
                                            decl.location))
    if errors:
        return errors

    def ancestors(name, path=()):
        """Every interface `name` builds on, near first; a circle is an error."""
        found = []
        for parent in interfaces[name].interfaces:
            if parent in path or parent == name:
                raise _Circle(' -> '.join(path + (name, parent)))
            if parent not in found:
                found.append(parent)
            for more in ancestors(parent, path + (name,)):
                if more not in found:
                    found.append(more)
        return found

    try:
        closure = {name: [name] + ancestors(name) for name in interfaces}
    except _Circle as circle:
        return [SemanticError(f"Interfaces build on each other in a circle: {circle}",
                              next(iter(interfaces.values())).location)]

    # A function with a body: a default method (D.006)
    defaults = {}
    for decl in interfaces.values():
        for method in decl.methods:
            if method.body is None:
                continue
            if not default_methods:
                errors.append(SemanticError(
                    f"Interface '{decl.name}' names its functions only - '{method.method_name}' "
                    f"has code (a class that implements it gives the code; default methods: "
                    f"[interfaces] defaultMethods = true)", method.location))
                continue
            default = copy.copy(method)
            default.name = f'{decl.name}.{method.method_name}.default'
            default.interface_of = None
            default.is_default_method = True
            program.declarations.append(default)
            method.body = None
            defaults[(decl.name, method.method_name)] = default
    if errors:
        return errors

    # Every interface gets the functions of those it builds on
    full = {}
    for name in interfaces:
        methods = {}
        for owner in closure[name]:
            for method in interfaces[owner].methods:
                if method.method_name in methods:
                    seen = methods[method.method_name]
                    if not _same_signature(seen, method):
                        errors.append(SemanticError(
                            f"Interface '{name}' gets two different '{method.method_name}' - "
                            f"{_signature(seen)} and {_signature(method)}", interfaces[name].location))
                    continue
                methods[method.method_name] = method
        full[name] = methods
    for name, methods in full.items():
        decl = interfaces[name]
        own = {m.method_name for m in decl.methods}
        for method_name, method in methods.items():
            if method_name in own:
                continue
            inherited = copy.copy(method)
            inherited.name = f'{name}.{method_name}'
            inherited.method_of = name
            inherited.interface_of = name
            this = ParameterDecl(location=method.location, name='this', default_value=None,
                                 param_type=StructType(location=method.location, name=name))
            inherited.parameters = [this] + [copy.copy(p) for p in method.parameters[1:]]
            decl.methods.append(inherited)
            program.declarations.append(inherited)
            if (method.method_of, method_name) in defaults:
                defaults[(name, method_name)] = defaults[(method.method_of, method_name)]
        decl.all_interfaces = list(closure[name])
    if errors:
        return errors

    # Each class: every function of every interface it implements
    for decl in structs.values():
        if decl.is_interface or not decl.interfaces:
            continue
        if not decl.is_class:
            errors.append(SemanticError(f"Struct '{decl.name}' can't implement an interface - a "
                                        f"struct only holds values (Decisions.md STC.005)",
                                        decl.location))
            continue
        wanted = []
        for name in decl.interfaces:
            other = structs.get(name)
            if other is None or not other.is_interface:
                what = "doesn't exist" if other is None else \
                    f"is a {'class - building on a class is inheritance (Task 32.7)' if other.is_class else 'struct'}"
                errors.append(SemanticError(f"Class '{decl.name}' implements '{name}', which {what}",
                                            decl.location))
                continue
            for more in closure[name]:
                if more not in wanted:
                    wanted.append(more)
        own = {m.method_name: m for m in decl.methods
               if not getattr(m, 'is_constructor', False) and not getattr(m, 'is_static', False)}
        impls = {}
        for name in wanted:
            answers = []
            for method_name, method in full[name].items():
                found = own.get(method_name)
                if found is None:
                    default = defaults.get((name, method_name))
                    if default is None:
                        errors.append(SemanticError(
                            f"Class '{decl.name}' implements {name} but has no function "
                            f"'{method_name}' - {_signature(method)}", decl.location))
                        continue
                    answers.append((method, default))
                    continue
                if not _same_signature(found, method):
                    errors.append(SemanticError(
                        f"Function '{method_name}' of class '{decl.name}' doesn't match {name}: "
                        f"{name} has {_signature(method)}, {decl.name} has {_signature(found)}",
                        found.location))
                    continue
                if getattr(found, 'is_private', False) or getattr(found, 'is_internal', False):
                    errors.append(SemanticError(
                        f"Function '{method_name}' of class '{decl.name}' must be public - it "
                        f"answers for interface {name}, which anyone may call", found.location))
                    continue
                answers.append((method, found))
            impls[name] = answers
        decl.interface_impls = impls
        decl.all_interfaces = wanted

    # Cloneable (32.5b): a public `Car function clone()` - the copy byVal makes
    for decl in structs.values():
        if decl.is_interface or 'Cloneable' not in getattr(decl, 'all_interfaces', ()):
            continue
        clone = next((m for m in decl.methods if getattr(m, 'method_name', None) == 'clone'
                      and not getattr(m, 'is_constructor', False)), None)
        if clone is None or len(clone.parameters) != 1 \
                or getattr(clone.return_type, 'name', None) != decl.name:
            errors.append(SemanticError(
                f"Class '{decl.name}' implements Cloneable but has no function "
                f"'{decl.name} function clone()' - it makes the copy", decl.location))
        elif getattr(clone, 'is_private', False) or getattr(clone, 'is_internal', False):
            errors.append(SemanticError(f"Function 'clone' of class '{decl.name}' must be "
                                        f"public - byVal calls it", clone.location))
        else:
            decl.clone_method = clone

    # An interface's function changes its object if any class's answer does (32.2e)
    for decl in structs.values():
        for answers in getattr(decl, 'interface_impls', {}).values():
            for method, answer in answers:
                if getattr(answer, 'changes_this', False):
                    for name in interfaces:
                        target = next((m for m in interfaces[name].methods
                                       if m.method_name == method.method_name), None)
                        if target is not None and name in decl.all_interfaces:
                            target.changes_this = True
    return errors


class _Circle(Exception):
    pass


def implements(actual_decl, interface_name: str) -> bool:
    """True when a class (or interface) value can be used as `interface_name`."""
    return interface_name in getattr(actual_decl, 'all_interfaces', ())
