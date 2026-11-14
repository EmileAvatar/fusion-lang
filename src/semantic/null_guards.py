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


def expand_null_guards(program) -> List[SemanticError]:
    errors: List[SemanticError] = []
    if not _has_guard(program):
        return errors
    _Expander(errors).node(program)
    return errors


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
        return BinaryExpr(location=expr.location, left=self.not_null(guards, expr.location),
                          operator='and', right=expr)

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
