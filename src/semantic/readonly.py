"""readonly parameters (Task 32.2e, user decisions 2026-10-30 - files/Object_Lifetime.md section 3).

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
    ArrayType, AssignmentStmt, CallExpr, FunctionDecl, FunctionType, IdentifierExpr, IndexExpr,
    ListType, MapType, MemberExpr, NamedArgument, PassingExpr, ReturnStmt, StructDecl,
    StructType, VarDeclStmt,
)
from .collection_rules import MUTATING_LIST_METHODS, MUTATING_MAP_METHODS
from .errors import SemanticError
from .name_resolver import MUTATING_BUILTINS
from .statics import _root, _walk


def check_readonly(program) -> List[SemanticError]:
    if not any(p.is_readonly for d in program.declarations
               for f in ([d] if isinstance(d, FunctionDecl) else
                         d.methods + d.static_methods if isinstance(d, StructDecl) else [])
               for p in f.parameters):
        return []
    functions, found, changed = _parameter_uses(program)
    return _errors(functions, found, changed)


def check_readonly_calls(program) -> List[SemanticError]:
    """`f(readonly acc)` - the caller's demand (Task 48.3, files/Ownership.md truth table 4): f must
    not change or keep it, nor pass it on to a function that does. Two errors when it does:
    at the call, naming the line that changes it, and at that line, naming the call - so the
    one who adds the change sees it too. A function value can't be looked into: an error."""
    demands, placed = [], set()

    def visit(n):
        if isinstance(n, PassingExpr) and n.is_readonly:
            demands.append(n)
        elif isinstance(n, CallExpr):
            for a in n.arguments:
                value = a.value if isinstance(a, NamedArgument) else a
                if isinstance(value, PassingExpr) and value.is_readonly:
                    placed.add(id(value))
        return n
    _walk(program.declarations, visit)
    if not demands:
        return []
    errors = [SemanticError("readonly is written at a call - f(readonly a) - or on a parameter",
                            d.location) for d in demands if id(d) not in placed]
    functions, found, changed = _parameter_uses(program)

    def who(f) -> str:
        if getattr(f, 'is_constructor', False):
            return f.method_of
        return getattr(f, 'method_name', None) or f.name

    def where(key, seen):
        """The first event that changes (or keeps) a parameter, following the calls."""
        for kind, node, extra in found.get(key, []):
            if kind != 'pass':
                return kind, node, key
            if extra in changed and extra not in seen:
                return where(extra, seen | {extra})
        return None

    calls = []
    _walk(program.declarations, lambda n: calls.append(n) or n if isinstance(n, CallExpr) else n)
    for call in calls:
        given = [a.value if isinstance(a, NamedArgument) else a for a in call.arguments]
        for arg in given:
            if not (isinstance(arg, PassingExpr) and arg.is_readonly):
                continue
            text = _written(arg.value)
            line = getattr(arg.location, 'line', 0)
            copy = f"pass byVal {text} for a copy"
            method = getattr(call, 'list_method', None) or getattr(call, 'map_method', None)
            decl = call.callee_declaration
            if method is not None:
                if method in MUTATING_LIST_METHODS | MUTATING_MAP_METHODS | {'add', 'insert'}:
                    errors.append(SemanticError(
                        f"{method} keeps what it is given - '{text}' is passed readonly; {copy}",
                        arg.location))
                continue
            if isinstance(decl, FunctionDecl):
                resolved = call.resolved_arguments or []
                index = next((i for i, r in enumerate(resolved) if r is arg), None)
                if index is None or (decl.name, index) not in changed:
                    continue
                param = decl.parameters[index].name
                found_at = where((decl.name, index), {(decl.name, index)})
                if found_at is None:
                    continue
                kind, node, (deep, deep_index) = found_at
                done = {'keep': 'keeps', 'unknown': 'passes on to a function value'}.get(kind, 'changes')
                at = getattr(getattr(node, 'location', None), 'line', 0)
                errors.append(SemanticError(
                    f"{who(decl)} {done} '{param}' (line {at}) - '{text}' is passed readonly; "
                    f"{copy}", arg.location))
                deep_param = functions[deep].parameters[deep_index].name
                errors.append(SemanticError(
                    f"{who(functions[deep])} {done} '{deep_param}' here - line {line} passes "
                    f"'{text}' to {who(decl)} as readonly", node.location))
            elif isinstance(call.callee, IdentifierExpr) and call.callee.name in MUTATING_BUILTINS \
                    and given and given[0] is arg:
                errors.append(SemanticError(
                    f"{call.callee.name} changes its first value - '{text}' is passed readonly; "
                    f"{copy}", arg.location))
            elif isinstance(getattr(call.callee, 'inferred_type', None), FunctionType):
                errors.append(SemanticError(
                    f"A function value can't be looked into - '{text}' is passed readonly; "
                    f"{copy}", arg.location))
    unique = {}
    for e in errors:                 # a class's methods are reached twice
        unique.setdefault((e.message, str(e.location)), e)
    return list(unique.values())


def _written(expr) -> str:
    """`order.items` as written."""
    if isinstance(expr, MemberExpr):
        return f"{_written(expr.object)}.{expr.member}"
    return getattr(expr, 'name', 'it')


def changed_parameters(program) -> Set[Tuple[str, int]]:
    """(function name, parameter index) of each parameter a function changes, keeps or passes
    on to a change - the borrow check uses it too (Task 48.2)."""
    return _parameter_uses(program)[2]


def _parameter_uses(program):
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
        tables = list(getattr(d, 'interface_impls', {}).items()) + \
            list(getattr(d, 'virtual_impls', {}).items())          # 32.7
        for iface, pairs in tables:
            for method, answer in pairs:
                if answer is not None and answer is not method:
                    answers.setdefault(method.name, []).append(answer.name)
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
            if isinstance(e, PassingExpr) and not e.by_val and not e.is_readonly:
                e = e.value                       # `byRef a` - a itself (48.3)
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
    return functions, found, changed


def _errors(functions, found, changed) -> List[SemanticError]:
    errors, seen = [], set()
    for f in functions.values():
        if getattr(f, 'interface_of', None):
            continue                     # checked in the classes that answer it
        for i, p in enumerate(f.parameters):
            if not p.is_readonly:
                continue
            start = f"'{p.name}' is readonly - {f.name}"
            copy = f"use a copy: byVal {p.name}"      # objects too, since Task 32.5b
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
