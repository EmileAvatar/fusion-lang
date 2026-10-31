"""readonly parameters (Task 32.2e, user decisions 2026-10-30 - Object_Lifetime.md section 3).

    void function show(readonly Account a)
        print(a.balance)             // reading - fine
        a.balance = 0                // a change - compile error
        update(a)                    // an error only when update changes its parameter
        Account b = a                // b is readonly too
        log.add(a)                   // kept where it could change later - an error

Runs after type checking. For every function and each of its parameters it finds what the
function does with that parameter (and the variables that share it, `Car c = a`): changes it
(an assignment through it, a List / Map method that changes it, setInt), keeps it (stored in
a field, a List or a module variable, or returned), passes it on (to a parameter of another
function - a change when that one changes it, worked out by following the calls until
nothing new turns up), or hands it to a function value it can't see into. A readonly
parameter may do none of these. A method's `this` is a parameter too, so a method that
changes its object is found the same way. `byVal a` (a copy) is never the parameter itself.
"""

from typing import Dict, List, Set, Tuple

from src.parser.ast_nodes import (
    ArrayType, AssignmentStmt, CallExpr, FunctionDecl, IdentifierExpr, IndexExpr, ListType,
    MapType, MemberExpr, ReturnStmt, StructDecl, StructType, VarDeclStmt,
)
from .collection_rules import MUTATING_LIST_METHODS, MUTATING_MAP_METHODS
from .errors import SemanticError
from .name_resolver import MUTATING_BUILTINS
from .statics import _root, _walk


def check_readonly(program) -> List[SemanticError]:
    functions: Dict[str, FunctionDecl] = {}
    for d in program.declarations:
        for f in ([d] if isinstance(d, FunctionDecl) else
                  d.methods + d.static_methods if isinstance(d, StructDecl) else []):
            if f.body is not None or getattr(f, 'interface_of', None):
                functions[f.name] = f
    # An interface's function (Task 32.5a) does what the classes' answers do: it passes each
    # parameter on to every function that answers it
    answers: Dict[str, List[str]] = {}
    for d in program.declarations:
        for iface, pairs in getattr(d, 'interface_impls', {}).items():
            for method, answer in pairs:
                answers.setdefault(f'{iface}.{method.method_name}', []).append(answer.name)
    if not any(p.is_readonly for f in functions.values() for p in f.parameters):
        return []
    classes = {d.name for d in program.declarations if isinstance(d, StructDecl) and d.is_class}

    def shared(t) -> bool:
        """A value two names can share: a class object, a List, a Map."""
        return isinstance(t, (ListType, MapType)) or (isinstance(t, StructType) and t.name in classes)

    def passed(t) -> bool:
        """A value a function gets itself, not a copy (arrays too)."""
        return shared(t) or isinstance(t, ArrayType)

    def place(e) -> bool:
        return isinstance(e, (IdentifierExpr, MemberExpr, IndexExpr))

    def uses(function: FunctionDecl, name: str) -> List[Tuple]:
        """What the function does with a parameter: ('change' | 'keep' | 'unknown', node, None)
        or ('pass', node, (callee, index))."""
        tracked, found = {name}, []
        variables = {p.name for p in function.parameters}
        if getattr(function, 'interface_of', None):
            index = [p.name for p in function.parameters].index(name)
            return [('pass', function, (answer, index)) for answer in answers.get(function.name, [])]

        def mine(e) -> bool:
            return place(e) and _root(e) in tracked

        def visit(n):
            if isinstance(n, VarDeclStmt):
                variables.add(n.name)
                if n.initializer is not None and mine(n.initializer) and \
                        shared(getattr(n.initializer, 'inferred_type', None)):
                    tracked.add(n.name)                   # `Car c = a` - the same object
            elif isinstance(n, AssignmentStmt):
                target = n.target
                if _root(target) in tracked and not (isinstance(target, IdentifierExpr)
                                                     and target.name != name):
                    found.append(('change', n, None))
                if mine(n.value) and shared(getattr(n.value, 'inferred_type', None)):
                    found.append(('keep', n, None))
            elif isinstance(n, ReturnStmt):
                if n.value is not None and mine(n.value) and \
                        shared(getattr(n.value, 'inferred_type', None)):
                    found.append(('keep', n, None))
            elif isinstance(n, CallExpr):
                method = getattr(n, 'list_method', None) or getattr(n, 'map_method', None)
                if method is not None and isinstance(n.callee, MemberExpr):
                    changing = MUTATING_LIST_METHODS if getattr(n, 'list_method', None) \
                        else MUTATING_MAP_METHODS
                    if method in changing and mine(n.callee.object):
                        found.append(('change', n, None))
                    for arg in n.arguments:
                        if mine(arg) and shared(getattr(arg, 'inferred_type', None)):
                            found.append(('keep', n, None))
                elif isinstance(n.callee, IdentifierExpr):
                    callee = n.callee.name
                    for i, arg in enumerate(n.arguments):
                        if not mine(arg):
                            continue
                        if callee in functions:
                            params = functions[callee].parameters
                            if i < len(params) and (passed(getattr(arg, 'inferred_type', None))
                                                    or params[i].by_ref):
                                found.append(('pass', n, (callee, i)))
                        elif callee in variables:             # a function value
                            if passed(getattr(arg, 'inferred_type', None)):
                                found.append(('unknown', n, None))
                        elif i == 0 and callee in MUTATING_BUILTINS:
                            found.append(('change', n, None))
            return n
        _walk([function.body], visit)
        return found

    found: Dict[Tuple[str, int], List[Tuple]] = {}
    for f in functions.values():
        for i, p in enumerate(f.parameters):
            found[(f.name, i)] = uses(f, p.name)
    # a parameter is changed when the function changes, keeps or passes it to a change
    changed: Set[Tuple[str, int]] = {key for key, events in found.items()
                                     if any(kind != 'pass' for kind, _, _ in events)}
    while True:
        more = {key for key, events in found.items() if key not in changed
                and any(kind == 'pass' and extra in changed for kind, _, extra in events)}
        if not more:
            break
        changed |= more

    errors, seen = [], set()
    for f in functions.values():
        if getattr(f, 'interface_of', None):
            continue                     # checked in the classes that answer it
        for i, p in enumerate(f.parameters):
            if not p.is_readonly:
                continue
            start = f"'{p.name}' is readonly - {f.name}"
            # a class object's copy comes with Cloneable (Task 32.5)
            copy = "a copy of an object comes with clone(), Task 32.5" \
                if isinstance(p.param_type, StructType) and p.param_type.name in classes \
                else f"use a copy: byVal {p.name}"
            for kind, node, extra in found[(f.name, i)]:
                if kind == 'pass':
                    if extra not in changed:
                        continue
                    callee = functions[extra[0]]
                    if getattr(node, 'struct_method', False) and extra[1] == 0:
                        message = (f"{start} calls {callee.method_name}, which changes "
                                   f"{p.name}")
                    else:
                        message = f"{start} passes it to {extra[0]}, which changes it ({copy})"
                elif kind == 'keep':
                    message = (f"{start} can't keep it (in a field, a List or by returning it) "
                               f"where it could change later ({copy})")
                elif kind == 'unknown':
                    message = f"{start} passes it to a function value that may change it"
                else:
                    message = f"{start} may read it but not change it"
                if (id(node), message) not in seen:
                    seen.add((id(node), message))
                    errors.append(SemanticError(message, node.location))
    return errors
