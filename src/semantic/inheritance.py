"""Inheritance (Task 32.7, Decisions.md D.083, D.084): `class Manager inherits Employee`.

Runs before names are resolved, before the interface check. For each class with a parent:
- the parent must be a class, not sealed, with no circle; one parent only (the parser);
- the child gets the parent's fields first (same order, so a Manager is laid out like an
  Employee and can be used as one), and the parent's interfaces;
- the parent's functions it doesn't replace are inherited (class.inherited); replacing one
  needs `override`, the same signature, and not `sealed` / private there;
- bare names of the parent's fields and functions in the child's code become `this.x`;
- a function replaced somewhere below (or abstract) becomes virtual: the root function turns
  into a look-up in the object's class table (a hidden interface, `Employee.virtual`), its code
  moves to `Employee.greet.own`, and each class gets the answer nearest to it;
- `super.greet()` calls the parent's own code; `super(...)` on a constructor's first line
  runs the parent's constructor code (`Employee.init`) on the new object; without one, the
  parent's constructor without arguments.
"""

import copy
from dataclasses import fields, is_dataclass
from typing import List

from src.parser.ast_nodes import (CallExpr, ExpressionStmt, FunctionDecl, IdentifierExpr,
                                  MemberExpr, ParameterDecl, PrimitiveType, ReturnStmt,
                                  StructDecl, StructType, VarDeclStmt)
from .errors import SemanticError
from .interfaces import _same_signature, _signature


def _walk(node, visit):
    """visit(node) on every node below; visit may return a replacement."""
    if isinstance(node, list):
        for i, item in enumerate(node):
            node[i] = visit(item) or item
            _walk(node[i], visit)
        return
    if not is_dataclass(node) or isinstance(node, type):
        return
    for f in fields(node):
        if f.name in ('location', 'inferred_type', 'declaration', 'scope'):
            continue
        value = getattr(node, f.name)
        if isinstance(value, list):
            _walk(value, visit)
        elif is_dataclass(value) and not isinstance(value, type):
            replaced = visit(value)
            if replaced is not None and replaced is not value:
                setattr(node, f.name, replaced)
                value = replaced
            _walk(value, visit)


def expand_inheritance(program) -> List[SemanticError]:
    errors = []
    structs = {d.name: d for d in program.declarations if isinstance(d, StructDecl)}
    classes = {n: d for n, d in structs.items() if d.is_class and not d.is_interface}

    for decl in classes.values():
        for m in decl.methods:
            if getattr(m, 'is_abstract', False) and not decl.is_abstract:
                errors.append(SemanticError(f"Class '{decl.name}' has the abstract function "
                                            f"'{m.method_name}' - write 'abstract class "
                                            f"{decl.name}'", m.location))
        if decl.class_parent is None:
            continue
        parent = structs.get(decl.class_parent)
        if parent is None:
            errors.append(SemanticError(f"Class '{decl.name}' inherits '{decl.class_parent}', "
                                        f"which doesn't exist", decl.location))
        elif not parent.is_class or parent.is_interface:
            what = 'an interface - write implements' if parent.is_interface else 'a struct'
            errors.append(SemanticError(f"Class '{decl.name}' can only inherit a class - "
                                        f"'{parent.name}' is {what}", decl.location))
        elif parent.is_sealed:
            errors.append(SemanticError(f"Class '{parent.name}' is sealed - no class can inherit "
                                        f"it", decl.location))
    if errors:
        return errors

    order, state = [], {}

    def visit(name, path):
        if state.get(name) == 'done':
            return
        if state.get(name) == 'busy':
            raise _Circle(' -> '.join(path + [name]))
        state[name] = 'busy'
        parent = classes[name].class_parent
        if parent is not None:
            visit(parent, path + [name])
        state[name] = 'done'
        order.append(classes[name])

    try:
        for name in classes:
            visit(name, [])
    except _Circle as circle:
        return [SemanticError(f"Classes inherit each other in a circle: {circle}",
                              next(iter(classes.values())).location)]
    if not any(d.class_parent for d in classes.values()):
        return []

    from src.parser.parser import Parser
    for decl in order:
        decl.ancestors = []
        decl.inherited = {}
        if decl.class_parent is None:
            continue
        parent = classes[decl.class_parent]
        decl.ancestors = [parent.name] + parent.ancestors
        own_fields = {f.name for f in decl.fields}
        inherited_fields = []
        for f in parent.fields:
            if f.name in own_fields:
                errors.append(SemanticError(f"Class '{decl.name}' has a field '{f.name}' - "
                                            f"{parent.name} has one already", decl.location))
                continue
            field = copy.copy(f)
            field.owner = getattr(f, 'owner', parent.name)
            inherited_fields.append(field)
        decl.fields = inherited_fields + decl.fields
        decl.interfaces = list(dict.fromkeys(parent.interfaces + decl.interfaces))

        visible = dict(parent.inherited)
        visible.update({m.method_name: m for m in parent.methods
                        if not getattr(m, 'is_constructor', False)})
        own = {m.method_name: m for m in decl.methods if not getattr(m, 'is_constructor', False)}
        for name, method in own.items():
            above = visible.get(name)
            if above is None:
                if getattr(method, 'is_override', False):
                    errors.append(SemanticError(f"'{name}' overrides nothing - {parent.name} has "
                                                f"no function '{name}'", method.location))
                continue
            if getattr(above, 'is_private', False):
                errors.append(SemanticError(f"Function '{name}' is private to {above.method_of} - "
                                            f"give this one another name", method.location))
            elif getattr(above, 'is_sealed', False):
                errors.append(SemanticError(f"Function '{name}' of {above.method_of} is sealed - it "
                                            f"can't be overridden", method.location))
            elif not getattr(method, 'is_override', False):
                errors.append(SemanticError(f"Function '{name}' replaces {above.method_of}'s - write "
                                            f"'override' before it", method.location))
            elif not _same_signature(above, method):
                errors.append(SemanticError(
                    f"Function '{name}' doesn't match {above.method_of}'s: {_signature(above)}",
                    method.location))
            method.overrides = above
        decl.inherited = {n: m for n, m in visible.items() if n not in own}

        # Bare names of the parent's fields and functions in the child's code
        parent_fields = {f.name for f in inherited_fields}
        inherited_names = set(decl.inherited)

        def fail(message):
            raise _NameClash(message)
        for method in decl.methods:
            names = parent_fields - {p.name for p in method.parameters} \
                if getattr(method, 'is_constructor', False) else parent_fields
            shim = copy.copy(method)         # the same body; `this` isn't a clash here
            shim.parameters = [p for p in method.parameters if p.name != 'this']
            try:
                Parser.rewrite_method_body(shim, decl.name, names, inherited_names, fail)
            except _NameClash as clash:
                errors.append(SemanticError(str(clash), method.location))
    if errors:
        return errors

    errors += _virtual_functions(program, order, classes)
    errors += _supers(program, order, classes)
    return errors


def _root(method):
    while getattr(method, 'overrides', None) is not None:
        method = method.overrides
    return method


def _virtual_functions(program, order, classes) -> List[SemanticError]:
    """Functions replaced somewhere below - or abstract - are called through the class table."""
    errors = []
    roots = {}
    for decl in order:
        for m in decl.methods:
            if getattr(m, 'overrides', None) is not None:
                root = _root(m)
                roots[id(root)] = root
            elif getattr(m, 'is_abstract', False):
                roots[id(m)] = m
    by_class = {}
    for root in roots.values():
        by_class.setdefault(root.method_of, []).append(root)
    for owner, family in by_class.items():
        name = f'{owner}.virtual'
        iface = StructDecl(location=classes[owner].location, name=name, fields=[], is_class=True,
                           is_interface=True)
        iface.builtin = True
        for root in family:
            if root.body is not None:            # its code moves; the root becomes the look-up
                own = copy.copy(root)
                own.name = f'{root.name}.own'
                own.is_own_code = True
                program.declarations.append(own)
                root.own_code = own
                root.body = None
            root.interface_of = name
            root.virtual_dispatcher = root
            iface.methods.append(root)
        iface.all_interfaces = [name]
        program.declarations.insert(0, iface)
        # every class from the owner down: the answer nearest to it
        for decl in order:
            if decl.name != owner and owner not in getattr(decl, 'ancestors', []):
                continue
            answers = []
            for root in family:
                answer = None
                for level in [decl.name] + decl.ancestors:
                    found = next((m for m in classes[level].methods
                                  if getattr(m, 'method_name', None) == root.method_name
                                  and not getattr(m, 'is_constructor', False)), None)
                    if found is not None:
                        answer = getattr(found, 'own_code', None) if found is root else found
                        break
                if found is not root:
                    found.virtual_dispatcher = root
                if answer is None and not decl.is_abstract:
                    errors.append(SemanticError(
                        f"Class '{decl.name}' must give function '{root.method_name}' - it is "
                        f"abstract in {owner} ({_signature(root)})", decl.location))
                answers.append((root, answer))
            decl.virtual_impls = dict(getattr(decl, 'virtual_impls', {}))
            decl.virtual_impls[name] = answers
            decl.virtual_tables = list(getattr(decl, 'virtual_tables', [])) + [name]
    return errors


def _supers(program, order, classes) -> List[SemanticError]:
    """super.f() - the parent's own code; super(...) - the parent's constructor code."""
    errors = []
    parents = {d.class_parent for d in order if d.class_parent}
    for decl in order:
        parent = classes.get(decl.class_parent) if decl.class_parent else None
        for method in decl.methods:
            if method.body is None:
                continue

            def call_super(node):
                if isinstance(node, CallExpr) and isinstance(node.callee, MemberExpr) \
                        and isinstance(node.callee.object, IdentifierExpr) \
                        and node.callee.object.name == 'super':
                    if parent is None:
                        errors.append(SemanticError(f"'super' - class '{decl.name}' has no parent",
                                                    node.location))
                        return None
                    member = node.callee.member
                    target = next((m for m in parent.methods if getattr(m, 'method_name', None) == member
                                   and not getattr(m, 'is_constructor', False)), None) \
                        or parent.inherited.get(member)
                    if target is None:
                        errors.append(SemanticError(f"super.{member}() - {parent.name} has no function "
                                                    f"'{member}'", node.location))
                        return None
                    target = getattr(target, 'own_code', None) or target
                    if target.body is None and not getattr(target, 'is_own_code', False):
                        errors.append(SemanticError(f"super.{member}() - it is abstract in "
                                                    f"{target.method_of}", node.location))
                        return None
                    node.callee = IdentifierExpr(location=node.location, name=target.name)
                    node.arguments = [IdentifierExpr(location=node.location, name='this')] + list(node.arguments)
                return None
            _walk(method.body, call_super)

        if parent is None:
            continue
        for maker in [m for m in decl.methods if getattr(m, 'is_constructor', False)]:
            statements = maker.body.statements
            found = [i for i, s in enumerate(statements) if _is_super_call(s)]
            if getattr(maker, 'delegate', None) is not None:
                if found:
                    errors.append(SemanticError("A constructor starting with this(...) can't also "
                                                "call super(...)", maker.location))
                continue                                # the other constructor calls super
            if len(found) > 1:
                errors.append(SemanticError("super(...) once, on the constructor's first line",
                                            maker.location))
                continue
            if found:
                call = statements.pop(found[0]).expression
            else:
                call = CallExpr(location=maker.location,
                                callee=IdentifierExpr(location=maker.location, name='super'),
                                arguments=[])
            call.callee = IdentifierExpr(location=call.location, name=parent.name)
            call.super_call = True
            # right after `Manager this = <new>`, before the child's own field set-ups
            statements.insert(1, ExpressionStmt(location=call.location, expression=call))
    # Then (once each super(...) is in place - a parent may have a parent) the parent's constructor code as a function of an object already made: Employee.init
    for name in parents:
        for maker in [m for m in classes[name].methods if getattr(m, 'is_constructor', False)]:
            init = copy.deepcopy(maker)
            statements = init.body.statements
            if getattr(maker, 'delegate', None) is not None:
                maker.init = None                       # this(...) first: not as a parent yet
                continue
            init.body.statements = statements[1:-1]     # without `this = <new>` / `return this`

            def no_value(node):
                if isinstance(node, ReturnStmt):
                    node.value = None
            _walk(init.body, no_value)
            init.parameters = [ParameterDecl(location=maker.location, name='this', default_value=None,
                                             param_type=StructType(location=maker.location, name=name))] \
                + init.parameters
            init.return_type = PrimitiveType(location=maker.location, name='void')
            init.name = maker.name.replace('.new', '.init', 1)
            init.method_name = 'init'
            init.is_constructor = False
            init.is_private = False
            init.is_parent_init = True
            maker.init = init
            program.declarations.append(init)

    return errors


def _is_super_call(statement) -> bool:
    return isinstance(statement, ExpressionStmt) and isinstance(statement.expression, CallExpr) \
        and isinstance(statement.expression.callee, IdentifierExpr) \
        and statement.expression.callee.name == 'super'


class _Circle(Exception):
    pass


class _NameClash(Exception):
    pass


def is_ancestor(decl, name: str) -> bool:
    """`name` is decl's parent, or its parent's parent ..."""
    return name in getattr(decl, 'ancestors', ())
