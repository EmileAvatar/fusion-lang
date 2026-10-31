"""A class's statics (Task 32.2c, user decisions 2026-10-30 - Classes.md section 3).

    class Garage
        public const static Car CAR = new Car()          // form A - direct
        public const static Car CAR3 = new Car() {       // form B - self set-up: CAR3 only
            CAR3.speed = 4
        }
        public const static Car CAR2                      // set in form C
        static {                                          // form C - any static
            CAR2 = new Car()
        }
        static int function count() : 3                   // a static method - no `this`

expand_statics() runs before names are resolved and turns them into what exists already:
- each static field becomes a module variable named `Garage.CAR` - set up when main starts,
  freed last when the program ends (they come before the module variables)
- the class's set-up becomes the function `Garage.__setup`: form A fields in order, then
  form B (each value and its block), then form C
- `CAR` inside the class and `Garage.CAR` outside become the variable `Garage.CAR`;
  `count()` / `Garage.count()` the function `Garage.count`
- main calls every class's set-up first; static_setup_order() (after type checking) puts the
  calls in the order the classes depend on each other, and reports a circle

Checked here: a const static is set only in its class's set-up (and one with no value must
get it in form C); form B changes only its own field; a static is read only once it is set up
(form A in order, then B in order, then C).
"""

from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Dict, List, Optional, Set

from src.parser.ast_nodes import (
    AssignmentStmt, BlockStmt, CallExpr, ExpressionStmt, FunctionDecl, IdentifierExpr,
    LambdaExpr, MemberExpr, IndexExpr, PrimitiveType, ProgramNode, StructDecl, VarDeclStmt,
)
from .errors import SemanticError

_SKIP = ('location', 'inferred_type', 'scope', 'declaration', 'callee_declaration',
         'resolved_arguments')


def _walk(node, visit) -> None:
    """Call visit(node) on every node below, children first replaced by what visit returns."""
    if isinstance(node, list):
        for i, item in enumerate(node):
            node[i] = visit(item)
            _walk(node[i], visit)
        return
    if not is_dataclass(node) or isinstance(node, type):
        return
    for f in dataclass_fields(node):
        if f.name in _SKIP:
            continue
        value = getattr(node, f.name)
        if isinstance(value, list):
            _walk(value, visit)
            continue
        new = visit(value)
        if new is not value:
            setattr(node, f.name, new)
        _walk(new, visit)


def _root(expr) -> Optional[str]:
    while isinstance(expr, (MemberExpr, IndexExpr)):
        expr = expr.object if isinstance(expr, MemberExpr) else expr.array
    return expr.name if isinstance(expr, IdentifierExpr) else None


def _reads(node) -> Set[str]:
    """Every bare name used in a node."""
    found = set()

    def visit(n):
        if isinstance(n, IdentifierExpr):
            found.add(n.name)
        return n
    _walk([node] if not isinstance(node, list) else node, visit)
    return found


def expand_statics(program: ProgramNode) -> List[SemanticError]:
    errors: List[SemanticError] = []
    classes = [d for d in program.declarations if isinstance(d, StructDecl) and d.is_class
               and (d.static_fields or d.static_methods or d.static_block)]
    if not classes:
        return errors
    by_name = {c.name: c for c in classes}
    statics: Dict[str, Dict[str, str]] = {}          # class -> field -> qualified name
    methods: Dict[str, Dict[str, str]] = {}          # class -> static method -> its function
    for c in classes:
        statics[c.name] = {f.name: f'{c.name}.{f.name}' for f in c.static_fields}
        methods[c.name] = {m.method_name: m.name for m in c.static_methods}

    def outside(node):
        """Garage.CAR -> the variable; Garage.count() -> the function."""
        if isinstance(node, MemberExpr) and isinstance(node.object, IdentifierExpr) \
                and node.member in statics.get(node.object.name, {}):
            return IdentifierExpr(location=node.location, name=statics[node.object.name][node.member])
        if isinstance(node, CallExpr) and isinstance(node.callee, MemberExpr) \
                and isinstance(node.callee.object, IdentifierExpr) \
                and node.callee.member in methods.get(node.callee.object.name, {}):
            node.callee = IdentifierExpr(location=node.callee.location,
                                         name=methods[node.callee.object.name][node.callee.member])
        return node

    def inside(owner: str, where: str):
        """A static's bare name inside its class means it (a local can't take the name)."""
        names, calls = statics[owner], methods[owner]

        def visit(node):
            if isinstance(node, VarDeclStmt) and node.name in names:
                errors.append(SemanticError(
                    f"A variable in {where} can't have the name of static '{node.name}'",
                    node.location))
            if isinstance(node, IdentifierExpr) and node.name in names:
                return IdentifierExpr(location=node.location, name=names[node.name])
            if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                    and node.callee.name in calls:
                node.callee = IdentifierExpr(location=node.callee.location, name=calls[node.callee.name])
            return outside(node)
        return visit

    setups, variables = [], []
    for c in classes:
        qualified = statics[c.name]
        order: Dict[str, int] = {}                   # when each static is set up
        a_fields = [f for f in c.static_fields if f.default_value is not None and f.setup is None]
        b_fields = [f for f in c.static_fields if f.setup is not None]
        for i, f in enumerate(a_fields):
            order[f.name] = i
        for i, f in enumerate(b_fields):
            order[f.name] = len(a_fields) + i
        late = len(a_fields) + len(b_fields)         # set in form C
        given = {_root(s.target) for s in c.static_block.statements
                 if isinstance(s, AssignmentStmt)} if c.static_block else set()
        for f in c.static_fields:
            if f.default_value is None:              # a plain static is 0 / null from the start
                order[f.name] = late if f.name in given else -1
        statements = []

        def check_reads(node, before: int, what: str):
            for name in _reads(node) & set(qualified):
                if order[name] >= before:
                    errors.append(SemanticError(
                        f"{what} reads static '{name}' before it is set up - forms A, B and C "
                        f"run in that order, each top to bottom", node.location))

        for f in a_fields:
            check_reads(f.default_value, order[f.name], f"Static '{f.name}'")
            statements.append(AssignmentStmt(
                location=f.location, value=f.default_value,
                target=IdentifierExpr(location=f.location, name=f.name)))
        for f in b_fields:
            check_reads(f.default_value, order[f.name], f"Static '{f.name}'")
            check_reads(f.setup, order[f.name] + 1, f"The set-up block of '{f.name}'")
            statements.append(AssignmentStmt(
                location=f.location, value=f.default_value,
                target=IdentifierExpr(location=f.location, name=f.name)))
            for statement in f.setup.statements:     # form B changes its own field only
                targets = []
                if isinstance(statement, AssignmentStmt):
                    targets.append(_root(statement.target))
                if isinstance(statement, ExpressionStmt) and isinstance(statement.expression, CallExpr) \
                        and isinstance(statement.expression.callee, MemberExpr):
                    targets.append(_root(statement.expression.callee.object))
                for target in targets:
                    if target in qualified and target != f.name:
                        errors.append(SemanticError(
                            f"The set-up block of '{f.name}' can only change '{f.name}' - change "
                            f"'{target}' in the static block (static {{ }})", statement.location))
            statements += f.setup.statements
        if c.static_block is not None:
            statements += c.static_block.statements
        for f in c.static_fields:
            if f.is_const and f.default_value is None and f.name not in given:
                errors.append(SemanticError(
                    f"const static '{f.name}' has no value - give it one where it is declared or "
                    f"in the static block", f.location))

        setup = FunctionDecl(location=c.location, name=f'{c.name}.__setup', parameters=[],
                             return_type=PrimitiveType(location=c.location, name='void'),
                             body=BlockStmt(location=c.location, statements=statements))
        setup.method_of, setup.method_name, setup.is_static_setup = c.name, '__setup', True
        setup.module_id, setup.namespace = getattr(c, 'module_id', ''), getattr(c, 'namespace', None)
        setups.append(setup)
        for f in c.static_fields:
            variable = VarDeclStmt(location=f.location, var_type=f.field_type, name=qualified[f.name],
                                   initializer=None)
            variable.is_static, variable.static_of = True, c.name
            variable.static_const, variable.is_public = f.is_const, not f.is_private
            variable.static_private = f.is_private
            variable.static_internal = getattr(f, 'is_internal', False)     # Task 32.2h
            variable.static_class = c
            variables.append(variable)

    # Names: inside each class first (bare names), then everywhere (Class.name)
    for c in classes:
        for function in c.methods + c.static_methods + [s for s in setups if s.method_of == c.name]:
            _walk(function.body, inside(c.name, f"'{function.name}'"))
    for decl in program.declarations:
        if isinstance(decl, FunctionDecl):
            _walk(decl.body, outside)
        elif isinstance(decl, VarDeclStmt) and decl.initializer is not None:
            decl.initializer = outside(decl.initializer)
            _walk(decl.initializer, outside)

    # A const static is set only in its class's set-up
    consts = {v.name: v.static_of for v in variables if v.static_const}
    for decl in program.declarations:
        if not isinstance(decl, FunctionDecl) or getattr(decl, 'is_static_setup', False):
            continue

        def check(node, decl=decl):
            if isinstance(node, AssignmentStmt) and isinstance(node.target, IdentifierExpr) \
                    and node.target.name in consts:
                errors.append(SemanticError(
                    f"'{node.target.name}' is const static - it is set only in "
                    f"{consts[node.target.name]}'s static set-up", node.location))
            return node
        _walk(decl.body, check)

    # main sets every class up first - static_setup_order() orders the calls later
    main = next((d for d in program.declarations
                 if isinstance(d, FunctionDecl) and d.name == 'main'), None)
    if main is not None and isinstance(main.body, BlockStmt):
        calls = [ExpressionStmt(location=main.location, expression=CallExpr(
            location=main.location, arguments=[],
            callee=IdentifierExpr(location=main.location, name=s.name))) for s in setups]
        for call in calls:
            call.static_setup = True
        main.body.statements[0:0] = calls
    program.declarations[0:0] = variables            # first: freed last (D9, U10)
    program.declarations.extend(setups)
    return errors


def static_setup_order(program: ProgramNode) -> List[SemanticError]:
    """After type checking (every call knows its function): set the classes up in the order
    they depend on each other - a class whose set-up uses another class comes after it - by
    following what each set-up calls, and what those call, until nothing new is found. While
    a class is being set up, no other class may use it: that is a circle, reported with the
    whole chain."""
    functions = {d.name: d for d in program.declarations if isinstance(d, FunctionDecl)}
    statics = {d.name: d.static_of for d in program.declarations
               if isinstance(d, VarDeclStmt) and getattr(d, 'is_static', False)}
    setups = {f.method_of: f for f in functions.values() if getattr(f, 'is_static_setup', False)}
    if not setups:
        return []
    errors: List[SemanticError] = []

    def uses(function) -> List[tuple]:
        """(class used, function called or None) for each use in a function's body."""
        found = []

        def visit(node):
            if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                    and node.callee.name in functions:
                called = functions[node.callee.name]
                found.append((getattr(called, 'method_of', None), called))
            elif isinstance(node, IdentifierExpr) and node.name in statics:
                found.append((statics[node.name], None))
            return node
        _walk(function.body, visit)
        return found

    depends: Dict[str, Set[str]] = {name: set() for name in setups}
    for owner, setup in setups.items():
        queue, seen = [(setup, [owner])], {setup.name}
        while queue:
            function, chain = queue.pop(0)
            for used, called in uses(function):
                here = getattr(function, 'method_of', None)
                if used is not None and used != owner and used in setups:
                    depends[owner].add(used)
                if used == owner and here not in (None, owner):
                    errors.append(SemanticError(
                        f"{here} can't use {owner} - {owner} is still being set up "
                        f"({' -> '.join(chain + [owner])})", setup.location))
                    queue = []
                    break
                if called is not None and called.name not in seen:
                    seen.add(called.name)
                    step = getattr(called, 'method_of', None)
                    queue.append((called, chain + [step] if step and step != chain[-1] else chain))
    # Classes set up after the ones they depend on; two that depend on each other: a circle
    ordered, state = [], {}

    def place(name, path):
        if state.get(name) == 'done':
            return
        if state.get(name) == 'busy':
            circle = path[path.index(name):] + [name]
            errors.append(SemanticError(
                f"The statics of {' and '.join(sorted(set(circle)))} need each other to be set "
                f"up first ({' -> '.join(circle)})", setups[name].location))
            return
        state[name] = 'busy'
        for other in sorted(depends[name]):
            place(other, path + [name])
        state[name] = 'done'
        ordered.append(name)

    for name in setups:
        place(name, [])
    main = functions.get('main')
    if main is not None and isinstance(main.body, BlockStmt):
        calls = [s for s in main.body.statements if getattr(s, 'static_setup', False)]
        rank = {setups[name].name: i for i, name in enumerate(ordered)}
        calls.sort(key=lambda s: rank.get(s.expression.callee.name, 0))
        main.body.statements[0:len(calls)] = calls
    return errors
