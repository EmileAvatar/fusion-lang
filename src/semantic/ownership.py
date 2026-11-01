"""Ownership: moving (Task 48.1 - Ownership.md sections 1-2, truth tables 1 and 3).

    [memory]
    assignment = "move"

    Car a = Car("red")
    Car b = a                    // moved: b owns it
    print(a.color)               // error: 'a' was moved to 'b' on line 2 - use byVal a for a copy
    a = Car("blue")              // fine: a has a value again

Runs after type checking, one function at a time, and only with assignment = "move" ("share"
keeps two names on one object). A List, a Map, an object (a class or interface value) and a
struct holding one of them move; numbers, strings and plain structs are copied. A move is a
bare variable written where a value is handed over: `T b = a`, `b = a`, `x.f = a`,
`list.add(a)` / `insert`, `m[k] = a`, a List literal `[a, b]`, `return a`. `byVal a` copies,
so it never moves.

Each variable's state is followed along every path: an `if` or `match` where only some
branches move it leaves it "maybe moved"; a loop runs its body twice, so a move that isn't
given a new value before the next pass is found; a `try` that moved it leaves it maybe moved
in the `catch`. The C code is unchanged - the counting still frees every object (48.6 removes
it where a move proves one owner). Borrowing (48.2) comes next: a parameter, an element and a
field are not tracked here.
"""

from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Dict, List, Optional

from src.parser.ast_nodes import (
    ArrayLiteralExpr, AssignmentStmt, BlockStmt, BreakStmt, CallExpr, CastExpr, ContinueStmt,
    ExpressionStmt, ForStmt, FunctionDecl, IdentifierExpr, IfStmt, IndexExpr, LambdaExpr,
    ListType, MapType, MatchStmt, MemberExpr, PassingExpr, ReturnStmt, StructDecl, StructType,
    ThrowStmt, TryStmt, TypeNode, UncheckedStmt, VarDeclStmt, WhileStmt,
)
from .errors import SemanticError

# A List's methods that keep the value they are given
_KEEPING = {'add', 'insert'}
_SKIP = {'location', 'inferred_type', 'declaration', 'scope', 'callee_declaration',
         'resolved_arguments'}


class _Moved:
    """Where a variable was moved: the line, what took it, and whether only some paths did."""

    def __init__(self, line: int, to: str, maybe: bool = False, loop: bool = False):
        self.line, self.to, self.maybe, self.loop = line, to, maybe, loop

    def as_maybe(self, loop: bool = False) -> '_Moved':
        return _Moved(self.line, self.to, True, self.loop or loop)


State = Dict[str, _Moved]


def _text(expr) -> str:
    """`car.engine` as written."""
    if isinstance(expr, MemberExpr):
        return f"{_text(expr.object)}.{expr.member}"
    return getattr(expr, 'name', 'it')


def _merge(states: List[Optional[State]], loop: bool = False) -> Optional[State]:
    """Paths joining: moved on every live path stays moved; on some, maybe moved."""
    live = [s for s in states if s is not None]
    if not live:
        return None
    merged: State = {}
    for name in {n for s in live for n in s}:
        found = [s.get(name) for s in live]
        first = next(m for m in found if m is not None)
        if all(m is not None for m in found) and not any(m.maybe for m in found):
            merged[name] = first
        else:
            merged[name] = first.as_maybe(loop)
    return merged


class _FunctionCheck:
    def __init__(self, moving, errors: List[SemanticError]):
        self.moving = moving           # does a value of this type move?
        self.errors = errors
        self.reported = set()
        self.locals = set()            # names this function declares (fields are not tracked)
        self.loops: List[dict] = []    # each enclosing loop: its breaks and continues
        self.log: List[tuple] = []     # every move, in order - a catch may start after any of them

    # ---------- expressions ----------

    def _line(self, node) -> int:
        location = getattr(node, 'location', None)
        return getattr(location, 'line', 0) or 0

    def _use(self, node: IdentifierExpr, state: State) -> None:
        moved = state.get(node.name)
        if moved is None:
            return
        key = (node.name, self._line(node))
        if key in self.reported:
            return
        self.reported.add(key)
        name = node.name
        if moved.loop:
            text = (f"'{name}' was moved to {moved.to} on line {moved.line}, in an earlier pass of "
                    f"the loop - give it a new value each pass, or use byVal {name} for a copy")
        elif moved.maybe:
            text = (f"'{name}' may have been moved to {moved.to} on line {moved.line} - give it a "
                    f"new value on every path, or use byVal {name} for a copy")
        else:
            text = (f"'{name}' was moved to {moved.to} on line {moved.line} - use byVal {name} "
                    f"for a copy")
        self.errors.append(SemanticError(text, node.location))

    def _movable(self, expr) -> Optional[IdentifierExpr]:
        """The variable a value hands over, when it is a bare variable that moves."""
        while isinstance(expr, CastExpr):          # `Shape s = (Shape)c` moves c too
            expr = expr.operand
        if isinstance(expr, IdentifierExpr) and expr.name in self.locals \
                and self.moving(getattr(expr, 'inferred_type', None)):
            return expr
        return None

    def _move(self, expr, to: str, state: State) -> None:
        """Hand a value over: check it, then mark it moved."""
        self.expression(expr, state)
        variable = self._movable(expr)
        if variable is not None:
            state[variable.name] = _Moved(self._line(expr), to)
            self.log.append((variable.name, state[variable.name]))

    def expression(self, node, state: State, hidden=frozenset()) -> None:
        """Check every variable an expression reads, in the order written."""
        if node is None or isinstance(node, (str, int, float, bool, TypeNode)):
            return
        if isinstance(node, list):
            for item in node:
                self.expression(item, state, hidden)
            return
        if isinstance(node, IdentifierExpr):
            if node.name not in hidden:
                self._use(node, state)
            return
        if isinstance(node, LambdaExpr):          # a captured moved variable is a use too
            own = hidden | {p.name for p in node.parameters}
            self._reads_inside(node.body, state, own)
            return
        if isinstance(node, ArrayLiteralExpr) and isinstance(getattr(node, 'inferred_type', None),
                                                             ListType):
            for element in node.elements:
                self._move(element, 'a List', state)
            return
        if isinstance(node, CallExpr) and isinstance(node.callee, MemberExpr) \
                and getattr(node, 'list_method', None) in _KEEPING:
            self.expression(node.callee.object, state, hidden)
            owner = getattr(node.callee.object, 'name', 'the List')
            for argument in node.arguments:
                self._move(argument, f"'{owner}' ({node.list_method})", state)
            return
        if not is_dataclass(node):
            return
        for f in dataclass_fields(node):
            if f.name not in _SKIP:
                self.expression(getattr(node, f.name), state, hidden)

    def _reads_inside(self, node, state: State, hidden) -> None:
        """A lambda's body: every variable it reads (no moves are followed inside it)."""
        if node is None or isinstance(node, (str, int, float, bool, TypeNode)):
            return
        if isinstance(node, list):
            for item in node:
                self._reads_inside(item, state, hidden)
            return
        if isinstance(node, IdentifierExpr):
            if node.name not in hidden:
                self._use(node, state)
            return
        if isinstance(node, VarDeclStmt):
            hidden = hidden | {node.name}
        if not is_dataclass(node):
            return
        for f in dataclass_fields(node):
            if f.name not in _SKIP:
                self._reads_inside(getattr(node, f.name), state, hidden)

    # ---------- statements ----------

    def block(self, statements, state: Optional[State]) -> Optional[State]:
        for statement in statements:
            if state is None:
                return None                         # the rest can't be reached
            state = self.statement(statement, state)
        return state

    def statement(self, node, state: State) -> Optional[State]:
        if isinstance(node, BlockStmt):
            return self.block(node.statements, state)
        if isinstance(node, VarDeclStmt):
            self.locals.add(node.name)
            if node.initializer is not None:
                self._move(node.initializer, f"'{node.name}'", state)
            state.pop(node.name, None)             # a new variable, alive
            return state
        if isinstance(node, AssignmentStmt):
            target = node.target
            if isinstance(target, IdentifierExpr):
                to = f"'{target.name}'"
            elif isinstance(target, IndexExpr):
                self.expression(target.array, state)
                self.expression(target.index, state)
                to = f"'{getattr(target.array, 'name', 'the Map')}'"
            else:
                self.expression(target, state)
                to = f"'{_text(target)}'"
            self._move(node.value, to, state)
            if isinstance(target, IdentifierExpr):
                state.pop(target.name, None)       # a new value brings it back
            return state
        if isinstance(node, ExpressionStmt):
            self.expression(node.expression, state)
            return state
        if isinstance(node, ReturnStmt):
            self.expression(node.value, state)     # returning hands it to the caller
            return None
        if isinstance(node, ThrowStmt):
            self.expression(node.value, state)
            return None
        if isinstance(node, BreakStmt):
            if self.loops:
                self.loops[-1]['breaks'].append(dict(state))
            return None
        if isinstance(node, ContinueStmt):
            if self.loops:
                self.loops[-1]['continues'].append(dict(state))
            return None
        if isinstance(node, IfStmt):
            self.expression(node.condition, state)
            then = self.statement(node.then_branch, dict(state))
            other = self.statement(node.else_branch, dict(state)) \
                if node.else_branch is not None else dict(state)
            return _merge([then, other])
        if isinstance(node, MatchStmt):
            self.expression(node.subject, state)
            ends = [self.statement(case.body, dict(state)) for case in node.cases]
            ends.append(self.statement(node.else_body, dict(state))
                        if node.else_body is not None else dict(state))
            return _merge(ends)
        if isinstance(node, (WhileStmt, ForStmt)):
            return self._loop(node, state)
        if isinstance(node, TryStmt):
            mark = len(self.log)
            body = self.statement(node.body, dict(state))
            # an error can come after any move in the body: each is maybe moved in a catch
            start = dict(state)
            for name, moved in self.log[mark:]:
                start.setdefault(name, moved.as_maybe())
            ends = [body]
            for catch in node.catches:
                if catch.name:
                    self.locals.add(catch.name)
                ends.append(self.statement(catch.body, dict(start)))
            after = _merge(ends)
            if node.finally_body is not None:
                after = self.statement(node.finally_body, after if after is not None else dict(start))
            return after
        if isinstance(node, UncheckedStmt):
            return self.statement(node.body, state)
        self.expression(node, state)               # anything else: check what it reads
        return state

    def _loop(self, node, state: State) -> Optional[State]:
        """Run the body twice: the second pass starts where the first ended, so a move not
        given a new value before the next pass is a use after a move."""
        is_for = isinstance(node, ForStmt)
        if is_for:
            self.expression(node.iterable, state)
            self.locals.add(node.variable)
        first = self._pass(node, dict(state))
        back, breaks = first
        # the second pass: what the first moved and didn't give a new value is gone
        again = dict(state)
        for name, moved in (back or {}).items():
            if name not in state:
                again[name] = _Moved(moved.line, moved.to, True, loop=True)
        self._pass(node, again)
        # after the loop: it ran no times, some times, or ended at a break
        return _merge([state, back] + breaks)

    def _pass(self, node, head: State):
        """One pass of a loop's body: (the state going round again, the states at each break)."""
        if isinstance(node, ForStmt):
            head.pop(node.variable, None)
        else:
            self.expression(node.condition, head)
        self.loops.append({'breaks': [], 'continues': []})
        end = self.statement(node.body, head)
        loop = self.loops.pop()
        return _merge([end] + loop['continues']), loop['breaks']


def _moving_types(program):
    """Which types move: a List, a Map, a class or interface value, a struct holding one."""
    structs = {d.name: d for d in program.declarations if isinstance(d, StructDecl)}
    cache: Dict[str, bool] = {}

    def moving(t, seen=()) -> bool:
        if isinstance(t, (ListType, MapType)):
            return True
        if not isinstance(t, StructType):
            return False
        decl = structs.get(t.name) or getattr(t, 'declaration', None)
        if decl is None:
            return False
        if decl.is_class or getattr(decl, 'is_interface', False):
            return True
        if t.name in cache:
            return cache[t.name]
        if t.name in seen:
            return False
        result = any(moving(f.field_type, seen + (t.name,)) for f in decl.fields
                     if hasattr(f, 'field_type'))
        cache[t.name] = result
        return result
    return moving


def check_ownership(program) -> List[SemanticError]:
    errors: List[SemanticError] = []
    moving = _moving_types(program)
    functions, seen = [], set()
    for d in program.declarations:
        for f in ([d] if isinstance(d, FunctionDecl) else
                  d.methods + getattr(d, 'static_methods', []) if isinstance(d, StructDecl) else []):
            if id(f) not in seen and f.body is not None and isinstance(f.body, BlockStmt):
                seen.add(id(f))
                functions.append(f)
    for function in functions:
        check = _FunctionCheck(moving, errors)
        check.locals = {p.name for p in function.parameters if p.name != 'this'}
        check.block(function.body.statements, {})
    return errors
