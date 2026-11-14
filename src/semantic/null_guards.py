"""The null guard (Task 52.8 - files/Nullable_Values.md section 3; D.116, D.138).

    c?.rename("x")                     // a statement: skipped when c is null
    int s = c?.speed ?? 0              // ?? gives the default when c is null
    if c?.speed > 50                   // in a condition: false when c is null
    string n = p?.spouse?.name ?? "-"  // a chain: every link checked
    Car d = c ?? Car()                 // ?? on an object: c, or the default when null

Runs first, before names are resolved: each guard is rewritten into what the language already
has - `x is not null`, `and`, the conditional operator and `if`:

    c?.rename("x")         ->  if c is not null: c.rename("x")
    c?.speed ?? 0          ->  (c is not null) ? c.speed : 0
    if c?.speed > 50       ->  if (c is not null) and (c.speed > 50)

A guarded value anywhere else (`int s = c?.speed`) is an error: a missing value needs a default
you write (`??`) - nothing changes silently (D.003). The part before `?.` is read twice, so it
must be a variable or a field path (`c`, `this.engine`, `a.b`); after a call, store the result in
a variable first. On a string, array, List or Map - never null (D.138) - the check is always true,
and the type checker warns (52.13).
"""

import copy
from dataclasses import fields, is_dataclass
from typing import List, Tuple

from src.parser.ast_nodes import (
    BinaryExpr, BlockStmt, CallExpr, CoalesceExpr, ConditionalExpr, ExpressionStmt, IdentifierExpr,
    IfStmt, IndexExpr, IsNullExpr, MemberExpr, UnaryExpr, WhileStmt,
)
from .errors import SemanticError

COMPARISONS = {'==', '!=', '===', '!==', '<>', '<', '>', '<=', '>='}


def expand_null_guards(program, not_around_guard: bool = False):
    """Returns (errors, warnings). `not_around_guard`: [conditions] notAroundGuard (D.116)."""
    errors: List[SemanticError] = []
    warnings: List[SemanticError] = []
    if _has_guard(program):
        expander = _Expander(errors)
        expander.warnings, expander.not_around_guard = warnings, not_around_guard
        expander.node(program)
    return errors, warnings


def _has_guard(node) -> bool:
    found = []

    def look(n):
        if found:
            return
        if isinstance(n, list):
            for item in n:
                look(item)
            return
        if not is_dataclass(n) or isinstance(n, type):
            return
        if isinstance(n, CoalesceExpr) or (isinstance(n, MemberExpr) and getattr(n, 'guarded', False)):
            found.append(n)
            return
        for f in fields(n):
            if f.name not in ('location', 'inferred_type'):
                look(getattr(n, f.name))
    look(node)
    return bool(found)


class _Expander:
    def __init__(self, errors):
        self.errors = errors

    # ---------- the receiver chain: `p?.spouse?.name` -> (p.spouse.name, [p, p.spouse]) ----------

    def strip(self, expr) -> Tuple[object, list]:
        if isinstance(expr, MemberExpr):
            obj, guards = self.strip(expr.object)
            if getattr(expr, 'guarded', False):
                if not self.simple(obj):
                    self.errors.append(SemanticError(
                        "'?.' after a call: store the result in a variable first - the part before "
                        "'?.' is read twice (Task 52.8)", expr.location))
                guards = guards + [obj]
            return MemberExpr(location=expr.location, object=obj, member=expr.member), guards
        if isinstance(expr, CallExpr) and isinstance(expr.callee, MemberExpr):
            callee, guards = self.strip(expr.callee)
            expr.callee = callee
            expr.arguments = [self.value(a) for a in expr.arguments]
            return expr, guards
        if isinstance(expr, IndexExpr):
            array, guards = self.strip(expr.array)
            expr.array = array
            expr.index = self.value(expr.index)
            return expr, guards
        return expr, []

    def simple(self, expr) -> bool:
        while isinstance(expr, (MemberExpr, IndexExpr)):
            if isinstance(expr, IndexExpr) and not isinstance(expr.index, IdentifierExpr) \
                    and type(expr.index).__name__ != 'LiteralExpr':
                return False
            expr = expr.object if isinstance(expr, MemberExpr) else expr.array
        return isinstance(expr, IdentifierExpr)

    def not_null(self, guards, location):
        test = None
        for g in guards:
            check = IsNullExpr(location=location, operand=copy.deepcopy(g), negated=True)
            check.from_guard = True
            test = check if test is None else BinaryExpr(location=location, left=test, operator='and',
                                                         right=check)
        return test

    # ---------- the three places a guard may stand ----------

    def value(self, expr):
        """A value: `??` gives the default; a guard left anywhere else is an error."""
        if isinstance(expr, CoalesceExpr):
            left, guards = self.strip(expr.left)
            left = self.value(left)
            right = self.value(expr.right)
            if not guards:
                if not self.simple(left):
                    self.errors.append(SemanticError(
                        "'??' after a call: store the result in a variable first - it is read twice "
                        "(Task 52.8)", expr.location))
                guards = [left]
            return ConditionalExpr(location=expr.location, condition=self.not_null(guards, expr.location),
                                   then_value=left, else_value=right)
        if isinstance(expr, MemberExpr) and getattr(expr, 'guarded', False):
            self.errors.append(SemanticError(
                f"'?.{expr.member}' may be missing - give a default with ?? (x?.{expr.member} ?? ...), "
                f"or test it in a condition (Task 52.8)", expr.location))
            expr.guarded = False
        if isinstance(expr, ConditionalExpr):
            expr.condition = self.condition(expr.condition)
            expr.then_value = self.value(expr.then_value)
            expr.else_value = self.value(expr.else_value)
            return expr
        if is_dataclass(expr) and not isinstance(expr, type):
            for f in fields(expr):
                if f.name in ('location', 'inferred_type'):
                    continue
                v = getattr(expr, f.name)
                if isinstance(v, list):
                    setattr(expr, f.name, [self.value(x) for x in v])
                elif is_dataclass(v) and not isinstance(v, type):
                    setattr(expr, f.name, self.value(v))
        return expr

    def condition(self, expr):
        """In a condition a guarded test is false when something on the way is null."""
        if isinstance(expr, BinaryExpr) and expr.operator in ('and', 'or', '&&', '||'):
            expr.left = self.condition(expr.left)
            expr.right = self.condition(expr.right)
            return expr
        if isinstance(expr, UnaryExpr) and expr.operator in ('not', '!'):
            expr.operand = self.condition(expr.operand)
            if _guarded_test(expr.operand):           # D.116 (52.7): unknown is not "yes"
                text = ("'!' around a ?. test turns 'unknown' into 'yes' - when the object is null the "
                        "test is false, so '!' makes it true; test null on its own: if x is null ... "
                        "else if ... (D.116)")
                if self.not_around_guard:
                    self.warnings.append(SemanticError(text + " - allowed by [conditions] notAroundGuard",
                                                       expr.location))
                else:
                    self.errors.append(SemanticError(text + " - or [conditions] notAroundGuard = true",
                                                     expr.location))
            return expr
        guards = []
        if isinstance(expr, BinaryExpr) and expr.operator in COMPARISONS:
            expr.left, g1 = self.strip(expr.left)
            expr.right, g2 = self.strip(expr.right)
            guards = g1 + g2
        elif not isinstance(expr, CoalesceExpr):
            expr, guards = self.strip(expr)
        expr = self.value(expr)
        if not guards:
            return expr
        test = BinaryExpr(location=expr.location, left=self.not_null(guards, expr.location),
                          operator='and', right=expr)
        test.guarded_test = True
        if isinstance(expr, BinaryExpr) and expr.operator in COMPARISONS:     # D.116 (52.7)
            self.warnings.append(SemanticError(
                "A ?. comparison is false when the object is null - if null needs its own path, test it "
                "first: if x is null ... else if ... (D.116)", expr.location))
        return test

    def statement(self, stmt):
        """`c?.rename("x")` on its own - not run when something on the way is null."""
        expr, guards = self.strip(stmt.expression)
        stmt.expression = self.value(expr)
        if not guards:
            return stmt
        return IfStmt(location=stmt.location, condition=self.not_null(guards, stmt.location),
                      then_branch=BlockStmt(location=stmt.location, statements=[stmt]), else_branch=None)

    # ---------- every statement ----------

    def node(self, n):
        if isinstance(n, list):
            return [self.node(x) for x in n]
        if not is_dataclass(n) or isinstance(n, type):
            return n
        if isinstance(n, ExpressionStmt):
            return self.statement(n)
        for f in fields(n):
            if f.name in ('location', 'inferred_type'):
                continue
            v = getattr(n, f.name)
            if f.name == 'condition' and isinstance(n, (IfStmt, WhileStmt)) or \
                    (f.name == 'condition' and type(n).__name__ in ('DoWhileStmt',)):
                setattr(n, f.name, self.condition(v))
            elif isinstance(v, list):
                setattr(n, f.name, [self.node(x) if _is_statement(x) else self.value(x) for x in v])
            elif _is_statement(v):
                setattr(n, f.name, self.node(v))
            elif is_dataclass(v) and not isinstance(v, type):
                setattr(n, f.name, self.value(v))
        return n


def _is_statement(n) -> bool:
    name = type(n).__name__
    return name.endswith('Stmt') or name.endswith('Decl') or name in ('ProgramNode', 'MatchCase',
                                                                       'MatchArm', 'CatchClause')


def _guarded_test(expr) -> bool:
    """A condition holding a test made from a `?.` guard."""
    if getattr(expr, 'guarded_test', False):
        return True
    if isinstance(expr, BinaryExpr) and expr.operator in ('and', 'or', '&&', '||'):
        return _guarded_test(expr.left) or _guarded_test(expr.right)
    if isinstance(expr, UnaryExpr):
        return _guarded_test(expr.operand)
    return False


def check_surely_null(program, is_object, is_default) -> List[SemanticError]:
    """D.117 (Task 52.7): an object surely null when it is passed - `Car c = null` then `drive(c)`
    with nothing in between that could give it an object - is a compile error. Followed in each
    block from top to bottom; a name given a value anywhere inside an if / loop / try is no longer
    surely null after it. Runs after type checking (it needs to know what is an object)."""
    from src.parser.ast_nodes import (AssignmentStmt, FunctionDecl, LiteralExpr, NamedArgument,
                                      ReturnStmt, StructDecl, VarDeclStmt)
    errors: List[SemanticError] = []

    def is_null(e):
        return isinstance(e, LiteralExpr) and e.type_hint == 'null'

    def assigned(node, names):
        def look(n):
            if isinstance(n, list):
                for x in n:
                    look(x)
                return
            if not is_dataclass(n) or isinstance(n, type):
                return
            if isinstance(n, AssignmentStmt) and isinstance(n.target, IdentifierExpr):
                names.discard(n.target.name)
            if isinstance(n, VarDeclStmt):
                names.discard(n.name)
            for f in fields(n):
                if f.name not in ('location', 'inferred_type', 'callee_declaration', 'declaration'):
                    look(getattr(n, f.name))
        look(node)

    def calls_in(expr, found):
        if isinstance(expr, list):
            for x in expr:
                calls_in(x, found)
            return
        if not is_dataclass(expr) or isinstance(expr, type) or _is_statement(expr):
            return
        if isinstance(expr, CallExpr):
            found.append(expr)
        for f in fields(expr):
            if f.name not in ('location', 'inferred_type', 'callee_declaration', 'declaration'):
                calls_in(getattr(expr, f.name), found)

    def block(statements):
        surely = set()
        for s in statements:
            exprs = []
            if isinstance(s, ExpressionStmt):
                exprs = [s.expression]
            elif isinstance(s, VarDeclStmt) and s.initializer is not None:
                exprs = [s.initializer]
            elif isinstance(s, AssignmentStmt):
                exprs = [s.value]
            elif isinstance(s, ReturnStmt) and s.value is not None:
                exprs = [s.value]
            found = []
            calls_in(exprs, found)
            for call in found:
                if not isinstance(getattr(call, 'callee_declaration', None), FunctionDecl):
                    continue                  # a built-in (print shows "null") - only your functions
                start = 1 if getattr(call, 'struct_method', False) else 0     # `this` - not passed
                for arg in call.arguments[start:]:
                    arg = arg.value if isinstance(arg, NamedArgument) else arg
                    if isinstance(arg, IdentifierExpr) and arg.name in surely:
                        who = getattr(call.callee, 'name', 'the function')
                        errors.append(SemanticError(
                            f"'{arg.name}' is surely null here - {who.split('.')[-1]} would get null; "
                            f"give it an object first, or check it (if {arg.name} is null ...) (D.117)",
                            arg.location))
            if isinstance(s, VarDeclStmt):
                if s.initializer is not None and is_null(s.initializer) and is_object(s.var_type) \
                        and not is_default(s.var_type):
                    surely.add(s.name)
                else:
                    surely.discard(s.name)
            elif isinstance(s, AssignmentStmt) and isinstance(s.target, IdentifierExpr):
                if is_null(s.value) and s.target.name in surely | {s.target.name} \
                        and is_object(getattr(s.target, 'inferred_type', None)) \
                        and not is_default(getattr(s.target, 'inferred_type', None)):
                    surely.add(s.target.name)
                else:
                    surely.discard(s.target.name)
            elif not isinstance(s, (ExpressionStmt, ReturnStmt)):
                assigned(s, surely)                   # an if / loop / try may give it a value
            for inner in _blocks_of(s):
                block(inner)

    def _blocks_of(s):
        out = []
        for f in fields(s):
            v = getattr(s, f.name)
            if isinstance(v, BlockStmt):
                out.append(v.statements)
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, BlockStmt):
                        out.append(x.statements)
                    elif is_dataclass(x) and not isinstance(x, type) and _is_statement(x):
                        out.extend(_blocks_of(x))
            elif is_dataclass(v) and not isinstance(v, type) and type(v).__name__ in ('IfStmt', 'CatchClause'):
                out.extend(_blocks_of(v))
        return out

    for d in program.declarations:
        for f in ([d] if isinstance(d, FunctionDecl) else
                  d.methods + d.static_methods if isinstance(d, StructDecl) else []):
            if f.body is not None and isinstance(f.body, BlockStmt):
                block(f.body.statements)
    return errors
