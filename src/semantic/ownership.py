"""Ownership: moving and borrowing (Tasks 48.1, 48.2 - files/Ownership.md sections 1-2, truth tables
1-3; D.100, D.101).

    [memory]
    assignment = "move"

    Car a = Car("red")
    Car b = a                    // moved: b owns it
    print(a.color)               // error: 'a' was moved to 'b' on line 2 - use byVal a for a copy
    a = Car("blue")              // fine: a has a value again
    Car first = fleet[0]         // a borrow: fleet can't change while 'first' is used
    fleet.clear()                // error while 'first' is still used below
    print(first.color)

Runs after type checking, one function at a time, and only with assignment = "move" ("share"
keeps two names on one object). A List, a Map, an object (a class or interface value) and a
struct holding one of them move; numbers, strings and plain structs are copied. A move is a
bare variable written where a value is handed over: `T b = a`, `b = a`, `x.f = a`,
`list.add(a)` / `insert`, `m[k] = a`, a List literal `[a, b]`, a struct made with it,
`return a`, and a call to a function that keeps that parameter. `byVal a` copies, so it never
moves.

Each variable's state is followed along every path: an `if` or `match` where only some
branches move it leaves it "maybe moved"; a loop runs its body twice, so a move that isn't
given a new value before the next pass is found; a `try` that moved it leaves it maybe moved
in the `catch`.

Borrowing (48.2):
- a parameter is a borrow; a function that keeps it (stores, adds or returns it) takes it
  instead, and every call moves the argument (D.100) - worked out across the functions until
  nothing new turns up. A method's `this` is always borrowed
- an element or a field read into a local (`Car c = fleet[0]`, `List<int> xs = order.items`,
  `for c in fleet`) is a local borrow: it can't be stored, returned or captured by a stored
  function value, and the owner can't change until the borrow's last use (D.101); while the
  borrow changes it, the owner can't even be read (R4). A for loop's collection can't change
  in the loop
- a method returning its own field or element (`return this.engine`) lends it: the call's
  result borrows from the object (`Engine e = car.getEngine()` - car frozen while e is used,
  D.109); the same for a part of any borrowed parameter, and for a new object made with one
  and returned (an iterator holding its collection). Stored or returned elsewhere: an error
- any other field or element can't be moved out (`return order.items`) - `byVal` copies it
  (D.026); with `[memory] moveFieldOut = true` a field may leave a struct the function owns,
  and the struct can't be used until it gets a new value (as in Rust)

The C code is unchanged - the counting still frees every object (48.6 removes it where a move
proves one owner). Not followed yet: a function value that keeps what it is given, the
classes answering an interface or virtual function, a field of a value a call returns.
"""

from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Dict, List, Optional, Set, Tuple

from src.parser.ast_nodes import (
    ArrayLiteralExpr, ArrayType, AssignmentStmt, BlockStmt, BreakStmt, CallExpr, CastExpr,
    ContinueStmt, ExpressionStmt, ForStmt, FunctionDecl, IdentifierExpr, IfStmt, IndexExpr,
    LambdaExpr, ListType, MapType, MatchStmt, MemberExpr, NamedArgument, PassingExpr, ReturnStmt,
    StructDecl, StructType, ThrowStmt, TryStmt, TypeNode, UncheckedStmt, VarDeclStmt, WhileStmt,
)
from .collection_rules import MUTATING_LIST_METHODS, MUTATING_MAP_METHODS
from .errors import SemanticError
from .name_resolver import MUTATING_BUILTINS
from .readonly import changed_parameters

# A List's methods that keep the value they are given
_KEEPING = {'add', 'insert'}
_SKIP = {'location', 'inferred_type', 'declaration', 'scope', 'callee_declaration',
         'resolved_arguments'}
# Methods giving a view of a Map - a borrow of it (D.092)
_VIEWS = {'keys', 'values'}

Path = Tuple[str, ...]


class _Moved:
    """Where a variable was moved: the line, what took it, and whether only some paths did."""

    def __init__(self, line: int, to: str, maybe: bool = False, loop: bool = False,
                 field: Optional[str] = None):
        self.line, self.to, self.maybe, self.loop, self.field = line, to, maybe, loop, field

    def as_maybe(self, loop: bool = False) -> '_Moved':
        return _Moved(self.line, self.to, True, self.loop or loop, self.field)


class _Borrow:
    """A local that borrows: the owner's path, the line it was borrowed on, and the borrow it
    was given (`Car d = c`), if any."""

    def __init__(self, owner: Path, line: int, given: Optional[str] = None):
        self.owner, self.line, self.given = owner, line, given


State = Dict[str, _Moved]


def _line(node) -> int:
    location = getattr(node, 'location', None)
    return getattr(location, 'line', 0) or 0


def _text(expr) -> str:
    """`car.engine` as written."""
    if isinstance(expr, MemberExpr):
        return f"{_text(expr.object)}.{expr.member}"
    return getattr(expr, 'name', 'it')


def _bare(expr):
    """The value under its casts: `(Shape)c` hands over c."""
    while isinstance(expr, CastExpr):
        expr = expr.operand
    return expr


def _path(expr) -> Optional[Path]:
    """`order.items[0]` -> ('order', 'items'): the variable and fields a value is part of."""
    expr = _bare(expr)
    if isinstance(expr, IdentifierExpr):
        return (expr.name,)
    if isinstance(expr, MemberExpr):
        inner = _path(expr.object)
        return inner + (expr.member,) if inner is not None else None
    if isinstance(expr, IndexExpr):
        return _path(expr.array)
    if isinstance(expr, CallExpr) and isinstance(expr.callee, MemberExpr) \
            and getattr(expr, 'map_method', None) in _VIEWS:
        return _path(expr.callee.object)
    return None


def _lent(expr) -> bool:
    """`byRef a` / `readonly a`: lent, not handed over (Task 48.3)."""
    return isinstance(expr, PassingExpr) and not expr.by_val


def _part(expr) -> Optional[Path]:
    """The owner's path when a value is a field or an element of something (not the whole)."""
    expr = _bare(expr)
    if isinstance(expr, (MemberExpr, IndexExpr)) or (
            isinstance(expr, CallExpr) and getattr(expr, 'map_method', None) in _VIEWS):
        return _path(expr)
    return None


def _overlap(a: Path, b: Path) -> bool:
    """`order` and `order.items` overlap; `order.items` and `order.total` don't."""
    n = min(len(a), len(b))
    return a[:n] == b[:n]


def _names(node, found: Set[str]) -> Set[str]:
    """Every bare name used below a node."""
    if isinstance(node, list):
        for item in node:
            _names(item, found)
    elif isinstance(node, IdentifierExpr):
        found.add(node.name)
    elif is_dataclass(node) and not isinstance(node, (TypeNode, type)):
        for f in dataclass_fields(node):
            if f.name not in _SKIP:
                _names(getattr(node, f.name), found)
    return found


def _arguments(call: CallExpr) -> list:
    if call.resolved_arguments is not None:
        return call.resolved_arguments
    return [a.value if isinstance(a, NamedArgument) else a for a in call.arguments]


def _who(decl) -> str:
    """How a function is named in a message: Car for a constructor, its own name otherwise."""
    if getattr(decl, 'is_constructor', False):
        return decl.method_of
    return getattr(decl, 'method_name', None) or decl.name


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
    def __init__(self, function, moving, errors: List[SemanticError], taken, changed,
                 own_struct=None, lends=frozenset()):
        self.moving = moving           # does a value of this type move?
        self.own_struct = own_struct   # [memory] moveFieldOut: is this a struct's type?
        self.errors = errors
        self.taken = taken             # (id(function), index) of each parameter a function keeps
        self.changed = changed         # (name, index) of each parameter a function changes
        self.reported = set()
        self.params = {p.name: i for i, p in enumerate(function.parameters) if p.name != 'this'}
        self.mine = {name for name, i in self.params.items() if (id(function), i) in taken}
        self.locals = set(self.params) # names this function declares (fields are not tracked)
        self.loops: List[dict] = []    # each enclosing loop: its breaks and continues
        self.log: List[tuple] = []     # every move, in order - a catch may start after any of them
        self.kept: Set[str] = set()    # parameters this function keeps (D.100)
        self.lends = lends             # (id(function), index): its result borrows from that one
        self.indexes = {p.name: i for i, p in enumerate(function.parameters)}   # `this` too
        self.lent: Set[str] = set()    # parameters this function's result borrows from (D.109)
        self.borrows: Dict[str, _Borrow] = {}
        self.origin: Dict[str, str] = {}   # a local naming a parameter's value: which one
        self._find_borrows(function.body)

    def _error(self, text: str, node) -> None:
        key = (text, _line(node))
        if key not in self.reported:
            self.reported.add(key)
            self.errors.append(SemanticError(text, node.location))

    # ---------- which locals borrow ----------

    def _find_borrows(self, body) -> None:
        """A local borrows when it is given an element or a field, walks a collection, or is
        given another borrow; it names a parameter's value when given that (not the place it
        was given - a borrow, for now, until its last use)."""
        given: List[tuple] = []        # (name, value, line)
        loops: List[ForStmt] = []

        def visit(node):
            if isinstance(node, list):
                for item in node:
                    visit(item)
                return
            if isinstance(node, VarDeclStmt) and node.initializer is not None:
                given.append((node.name, node.initializer, _line(node)))
            elif isinstance(node, AssignmentStmt) and isinstance(node.target, IdentifierExpr):
                given.append((node.target.name, node.value, _line(node)))
            elif isinstance(node, ForStmt):
                loops.append(node)
            if is_dataclass(node) and not isinstance(node, (TypeNode, type)):
                for f in dataclass_fields(node):
                    if f.name not in _SKIP:
                        visit(getattr(node, f.name))
        visit(body)
        for loop in loops:
            owner = _path(loop.iterable)
            element = self._element(loop.iterable)
            if owner is not None and self.moving(element):
                self.borrows.setdefault(loop.variable, _Borrow(owner, _line(loop)))
        changed = True
        while changed:
            changed = False
            for name, value, line in given:
                if name in self.borrows or not self.moving(getattr(value, 'inferred_type', None)):
                    continue
                part = _part(value)
                source = _bare(value)
                if self._field_out(source):
                    continue                   # the field leaves the struct: owned, not borrowed
                lending = self._lending(source)
                if lending is not None:
                    self.borrows[name] = _Borrow(lending, line)
                elif _lent(source) and _path(source.value) is not None:
                    self.borrows[name] = _Borrow(_path(source.value), line)
                elif part is not None:
                    self.borrows[name] = _Borrow(part, line)
                elif isinstance(source, IdentifierExpr) and source.name in self.borrows:
                    self.borrows[name] = _Borrow(self.borrows[source.name].owner, line, source.name)
                elif isinstance(source, IdentifierExpr) and name not in self.origin and \
                        name not in self.params and \
                        (source.name in self.origin or source.name in self.params):
                    self.origin[name] = self.origin.get(source.name, source.name)
                else:
                    continue
                changed = True

    @staticmethod
    def _element(iterable):
        t = getattr(iterable, 'inferred_type', None)
        if isinstance(t, (ListType, ArrayType)):
            return getattr(t, 'element_type', None)
        return None

    # ---------- expressions ----------

    def _use(self, node: IdentifierExpr, state: State) -> None:
        moved = state.get(node.name)
        if moved is None:
            return
        name = node.name
        if moved.field and not moved.maybe and not moved.loop:
            text = (f"'{name}' gave its field '{moved.field}' to {moved.to} on line {moved.line} - "
                    f"it can't be used until it gets a new value; or use byVal {name}.{moved.field} "
                    f"for a copy")
        elif moved.loop:
            text = (f"'{name}' was moved to {moved.to} on line {moved.line}, in an earlier pass of "
                    f"the loop - give it a new value each pass, or use byVal {name} for a copy")
        elif moved.maybe:
            text = (f"'{name}' may have been moved to {moved.to} on line {moved.line} - give it a "
                    f"new value on every path, or use byVal {name} for a copy")
        else:
            text = (f"'{name}' was moved to {moved.to} on line {moved.line} - use byVal {name} "
                    f"for a copy")
        self._error(text, node)

    def _lending(self, value) -> Optional[Path]:
        """`car.getEngine()` when getEngine returns a part of its object: what it borrows from."""
        value = _bare(value)
        if not isinstance(value, CallExpr) or not isinstance(value.callee_declaration, FunctionDecl):
            return None
        for i, argument in enumerate(_arguments(value)):
            if (id(value.callee_declaration), i) in self.lends and _path(argument) is not None:
                return _path(argument)
        return None

    def _lend(self, root: str) -> bool:
        """Returning a borrow of a parameter the function doesn't own: its result lends it."""
        if root in self.indexes and (root == 'this' or root not in self.mine):
            self.lent.add(root)
            return True
        return False

    def _move(self, expr, to: str, state: State, local: Optional[str] = None,
              returning: bool = False) -> None:
        """Hand a value over - to a local variable, or (local None) somewhere it is kept:
        check it, then mark it moved."""
        value = _bare(expr)
        if returning and isinstance(value, CallExpr) and isinstance(value.callee, IdentifierExpr) \
                and isinstance(value.callee_declaration, (FunctionDecl, StructDecl)):
            # a new object made with a part of this, returned: the result lends it (D.109)
            self._call(value, state, returning=True)
        else:
            self.expression(expr, state)
        if isinstance(value, LambdaExpr):
            self._captures(value, local)
            return
        if _lent(value):
            if local is None:
                text = _text(value.value)
                self._error(f"'{'readonly' if value.is_readonly else 'byRef'} {text}' only lends "
                            f"it - a borrow can't be stored or returned; give {text} itself (a "
                            f"move) or byVal {text} (a copy)", expr)
            return
        if not self.moving(getattr(expr, 'inferred_type', None)):
            return
        lending = self._lending(value)
        if lending is not None:
            if local is None and not (returning and self._lend(lending[0])):
                self._error(f"{_who(value.callee_declaration)}'s result borrows from "
                            f"'{'.'.join(lending)}' - a borrow can't be stored or returned; use "
                            f"byVal for a copy", expr)
            return
        part = _part(value)
        if part is not None and returning and self._lend(part[0]):
            return                             # a getter: the result borrows from it (D.109)
        if part is not None and self._field_out(value):
            root = value.object.name
            state[root] = _Moved(_line(expr), to, field=value.member)
            self.log.append((root, state[root]))
            return
        if part is not None:
            if local is None and isinstance(value, MemberExpr):
                self._error(f"'{_text(value)}' is part of '{'.'.join(part[:-1])}' and can't be "
                            f"moved out - use byVal {_text(value)} for a copy", expr)
            elif local is None:
                self._error(f"An element of '{'.'.join(part)}' can't be moved out - use byVal "
                            f"for a copy", expr)
            return
        if not isinstance(value, IdentifierExpr) or value.name not in self.locals:
            return
        name = value.name
        if name in self.borrows:
            if local is None and not (returning and self._lend(self.borrows[name].owner[0])):
                borrow = self.borrows[name]
                self._error(f"'{name}' borrows from '{'.'.join(borrow.owner)}' (line {borrow.line}) "
                            f"- a borrow can't be stored or returned; use byVal {name} for a copy",
                            expr)
            return
        param = self.origin.get(name, name if name in self.params else None)
        if param is not None and param not in self.mine:
            if local is None:
                self.kept.add(param)           # the function keeps it: it takes it (D.100)
            return
        state[name] = _Moved(_line(expr), to)
        self.log.append((name, state[name]))

    def _field_out(self, value) -> bool:
        """`o.ctx` with [memory] moveFieldOut, o a struct this function owns (not a parameter
        it borrows, not a borrow): the field may be taken out, o is then gone."""
        if self.own_struct is None or not isinstance(value, MemberExpr) \
                or not isinstance(value.object, IdentifierExpr):
            return False
        name = value.object.name
        return name in self.locals and name not in self.borrows and name not in self.origin \
            and (name not in self.params or name in self.mine) \
            and self.own_struct(getattr(value.object, 'inferred_type', None))

    def _captures(self, function: LambdaExpr, local: Optional[str]) -> None:
        """A function value that is kept (not just passed to a call) can't hold a borrow; one
        that holds a parameter keeps it."""
        own = {p.name for p in function.parameters}
        for name in sorted(_names(function.body, set()) - own):
            if name in self.borrows:
                borrow = self.borrows[name]
                self._error(f"A function value can't capture '{name}' - it borrows from "
                            f"'{'.'.join(borrow.owner)}' (line {borrow.line}); copy it first "
                            f"(byVal {name})", function)
            elif local is None and self.origin.get(name, name) in self.params:
                self.kept.add(self.origin.get(name, name))

    def _call(self, node: CallExpr, state: State, returning: bool = False) -> None:
        decl = node.callee_declaration
        if isinstance(decl, StructDecl) and not decl.is_class:
            for argument in _arguments(node):          # a struct keeps what it is made with
                self._move(argument, f"'{decl.name}'", state, returning=returning)
            return
        for i, argument in enumerate(_arguments(node)):
            if (id(decl), i) in self.taken and _lent(argument):
                self.expression(argument, state)
                text = _text(argument.value)
                self._error(f"{_who(decl)} keeps its '{decl.parameters[i].name}' - "
                            f"'{'readonly' if argument.is_readonly else 'byRef'} {text}' only "
                            f"lends it for the call; give {text} itself (a move) or byVal {text} "
                            f"(a copy)", argument)
            elif (id(decl), i) in self.taken:
                self._move(argument, f"'{_who(decl)}' (which keeps it)", state, returning=returning)
            else:
                self.expression(argument, state)

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
        if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                and isinstance(node.callee_declaration, (FunctionDecl, StructDecl)):
            self._call(node, state)
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
                self._move(node.initializer, f"'{node.name}'", state, local=node.name)
            state.pop(node.name, None)             # a new variable, alive
            return state
        if isinstance(node, AssignmentStmt):
            target = node.target
            local = None
            if isinstance(target, IdentifierExpr):
                to = f"'{target.name}'"
                local = target.name if target.name in self.locals else None
            elif isinstance(target, IndexExpr):
                self.expression(target.array, state)
                self.expression(target.index, state)
                to = f"'{getattr(target.array, 'name', 'the Map')}'"
            else:
                self.expression(target, state)
                to = f"'{_text(target)}'"
            self._move(node.value, to, state, local=local)
            if isinstance(target, IdentifierExpr):
                state.pop(target.name, None)       # a new value brings it back
            return state
        if isinstance(node, ExpressionStmt):
            self.expression(node.expression, state)
            return state
        if isinstance(node, ReturnStmt):
            if node.value is not None:             # returning hands it to the caller
                self._move(node.value, 'the caller', state, returning=True)
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
            ends = [self._case(case, state) for case in node.cases]
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

    def _case(self, case, state: State) -> Optional[State]:
        """A case's names (`case Function(name, params)`) are new for its body: a variable
        of the same name outside is set aside, then back as it was."""
        bound = {b for pattern in case.patterns for b in pattern.bindings}
        head = dict(state)
        outside = {name: head.pop(name) for name in bound if name in head}
        end = self.statement(case.body, head)
        if end is not None:
            for name in bound:
                end.pop(name, None)
            end.update(outside)
        return end

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

    # ---------- the owner frozen while a borrow is used (D.101) ----------

    def frozen(self, statements) -> None:
        """Every block: from each borrow to its last use, the owner can't change."""
        for i, node in enumerate(statements):
            if isinstance(node, VarDeclStmt) and node.name in self.borrows \
                    and _line(node) == self.borrows[node.name].line:
                names = self._family(node.name)
                rest = statements[i + 1:]
                last = max([_line(n) for n in self._mentions(rest, names)] or [_line(node)])
                used: list = []
                self._range(rest, names, used)
                self._check(used, names, self.borrows[node.name], node.name, last)
            if isinstance(node, ForStmt):
                owner = _path(node.iterable)
                t = getattr(node.iterable, 'inferred_type', None)
                if owner is not None and isinstance(t, (ListType, MapType, ArrayType)) and \
                        (not isinstance(t, ArrayType) or self.moving(self._element(node.iterable))):
                    borrowing = node.variable in self.borrows
                    names = self._family(node.variable) if borrowing else set()
                    self._check(node.body, names, _Borrow(owner, _line(node)),
                                node.variable if borrowing else None, _line(node),
                                looped=node.iterable)
            for block in self._blocks(node):
                self.frozen(block)

    @staticmethod
    def _blocks(node) -> List[list]:
        """The statement lists directly inside a statement."""
        found = []
        for part in (getattr(node, 'body', None), getattr(node, 'then_branch', None),
                     getattr(node, 'else_branch', None), getattr(node, 'else_body', None),
                     getattr(node, 'finally_body', None)):
            if isinstance(part, BlockStmt):
                found.append(part.statements)
            elif part is not None and not isinstance(part, list) and is_dataclass(part) \
                    and not isinstance(part, FunctionDecl):
                found.append([part])
        for case in getattr(node, 'cases', None) or []:
            found.extend(_FunctionCheck._blocks(case))
        for catch in getattr(node, 'catches', None) or []:
            found.extend(_FunctionCheck._blocks(catch))
        return found

    def _family(self, name: str) -> Set[str]:
        """A borrow and the locals given it (not other borrows of the same owner)."""
        names = {name}
        grew = True
        while grew:
            more = {other for other, borrow in self.borrows.items() if borrow.given in names}
            grew = not more <= names
            names |= more
        return names

    @staticmethod
    def _mentions(statements, names) -> List[IdentifierExpr]:
        found = []

        def visit(node):
            if isinstance(node, list):
                for item in node:
                    visit(item)
            elif isinstance(node, IdentifierExpr):
                if node.name in names:
                    found.append(node)
            elif is_dataclass(node) and not isinstance(node, (TypeNode, type)):
                for f in dataclass_fields(node):
                    if f.name not in _SKIP:
                        visit(getattr(node, f.name))
        visit(statements)
        return found

    def _range(self, statements, names, used: list) -> None:
        """The statements up to the borrow's last use: the last one itself only where it holds
        more statements (a loop is taken whole - the borrow is used again each pass)."""
        uses = [i for i, n in enumerate(statements) if self._mentions([n], names)]
        if not uses:
            return
        end = uses[-1]
        used.extend(statements[:end])
        tail = statements[end]
        if isinstance(tail, (WhileStmt, ForStmt)):
            used.append(tail)
        else:
            for block in self._blocks(tail):
                self._range(block, names, used)

    def _check(self, node, names, borrow: _Borrow, name: Optional[str], last: int,
               looped=None) -> None:
        changes, reads = [], []
        self._effects(node, changes, reads)
        owner = '.'.join(borrow.owner)
        while_text = (f"while a for loop walks it (line {borrow.line})" if looped is not None else
                      f"while '{name}' borrows from it (line {borrow.line}, last used on line {last})")
        for path, at, rebind in changes:
            if path[0] in names or not _overlap(path, borrow.owner):
                continue
            if isinstance(looped, IdentifierExpr) and isinstance(at, CallExpr) \
                    and isinstance(at.callee, MemberExpr) and _path(at.callee.object) == (looped.name,):
                continue                # found already: "being looped over" (D.058)
            if looped is not None and isinstance(at, IndexExpr) \
                    and not self.moving(getattr(at, 'inferred_type', None)):
                continue                # an element's value set: fine (27.2e) - unless it moves
            self._error(f"'{owner}' can't change {while_text}", at)
        # R4 relaxed (D.123, 48.10): while the borrow changes it, the owner may still be read -
        # only changing it another way (above) is an error

    def _effects(self, node, changes: list, reads: list) -> None:
        """The paths a statement changes (assigned, changed by a method or a call, moved) and
        the ones it reads. A function value's body runs later - left out."""
        if node is None or isinstance(node, (str, int, float, bool, TypeNode, LambdaExpr)):
            return
        if isinstance(node, list):
            for item in node:
                self._effects(item, changes, reads)
            return

        def moved(value):
            value = _bare(value)
            if isinstance(value, IdentifierExpr) and self.moving(getattr(value, 'inferred_type', None)):
                changes.append(((value.name,), value, True))

        if isinstance(node, AssignmentStmt):
            path = _path(node.target)
            if path is not None:
                changes.append((path, node.target, isinstance(node.target, IdentifierExpr)))
            if isinstance(node.target, IndexExpr):
                self._effects(node.target.index, changes, reads)
            moved(node.value)
            self._effects(node.value, changes, reads)
            return
        if isinstance(node, (VarDeclStmt, ReturnStmt)):
            value = node.initializer if isinstance(node, VarDeclStmt) else node.value
            if value is not None:
                moved(value)
                self._effects(value, changes, reads)
            return
        if isinstance(node, (IdentifierExpr, MemberExpr, IndexExpr)) and _path(node) is not None:
            reads.append((_path(node), node))
            if isinstance(node, IndexExpr):
                self._effects(node.index, changes, reads)
            return
        if isinstance(node, CallExpr):
            method = getattr(node, 'list_method', None) or getattr(node, 'map_method', None)
            if method is not None and isinstance(node.callee, MemberExpr):
                changing = MUTATING_LIST_METHODS if getattr(node, 'list_method', None) \
                    else MUTATING_MAP_METHODS
                path = _path(node.callee.object)
                if method in changing and path is not None:
                    changes.append((path, node, False))
                if method in _KEEPING:
                    for argument in node.arguments:
                        moved(argument)
            decl = node.callee_declaration
            if isinstance(decl, FunctionDecl):
                for i, argument in enumerate(_arguments(node)):
                    path = _path(argument)
                    if path is not None and (id(decl), i) not in self.lends \
                            and ((decl.name, i) in self.changed or (id(decl), i) in self.taken):
                        changes.append((path, argument, False))
            elif isinstance(node.callee, IdentifierExpr) and node.callee.name in MUTATING_BUILTINS \
                    and node.arguments and _path(node.arguments[0]) is not None:
                changes.append((_path(node.arguments[0]), node, False))
        if is_dataclass(node):
            for f in dataclass_fields(node):
                if f.name not in _SKIP:
                    self._effects(getattr(node, f.name), changes, reads)


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


def check_ownership(program, move_field_out: bool = False) -> List[SemanticError]:
    moving = _moving_types(program)
    structs = {d.name for d in program.declarations if isinstance(d, StructDecl)
               and not d.is_class and not getattr(d, 'is_interface', False)}
    own_struct = (lambda t: isinstance(t, StructType) and t.name in structs) \
        if move_field_out else None
    functions, seen = [], set()
    for d in program.declarations:
        for f in ([d] if isinstance(d, FunctionDecl) else
                  d.methods + getattr(d, 'static_methods', []) if isinstance(d, StructDecl) else []):
            if id(f) not in seen and f.body is not None and isinstance(f.body, BlockStmt):
                seen.add(id(f))
                functions.append(f)
    changed = changed_parameters(program)
    # the parameters each function keeps, followed through the calls until nothing new turns up
    taken: Set[Tuple[int, int]] = set()
    lends: Set[Tuple[int, int]] = set()      # results that borrow from a parameter (D.109)
    while True:
        errors: List[SemanticError] = []
        more, lending = set(), set()
        for function in functions:
            check = _FunctionCheck(function, moving, errors, taken, changed, own_struct, lends)
            check.block(function.body.statements, {})
            more |= {(id(function), check.params[name]) for name in check.kept}
            lending |= {(id(function), check.indexes[name]) for name in check.lent}
        if more <= taken and lending <= lends:
            break
        taken |= more
        lends |= lending
    for function in functions:
        _FunctionCheck(function, moving, errors, taken, changed,
                       own_struct, lends).frozen(function.body.statements)
    return errors
