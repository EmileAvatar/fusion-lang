"""`let` / `var` and a match that gives a value (Task 46, user decisions 2026-10-29).

    let name = readLine()          the type comes from the value; set once, never changes
    var count = 0                  the type comes from the value; can change, the type can't
    let total                      no value yet - set exactly once later, on every path
    string day = match n { 6, 7 : "Weekend", _ : "Weekday" }

A `let` is const and read only - on a struct, string, List or array nothing inside can change
either. A `let` / `var` declared without a value gets its type from its first value;
check_set_once() then checks, path by path, that it is set before it is read - and a `let`
exactly once. A match that gives a value (form A) has one value per case, covers every possible
value (`_` or `else` for the rest) and never falls through.
"""

import copy
from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Dict, List, Optional

from src.parser.ast_nodes import (
    ArrayLiteralExpr, ArrayType, AssignmentStmt, BlockStmt, BreakStmt, CallExpr, ContinueStmt,
    EnumType, ExpressionStmt, ForStmt, FunctionDecl, IdentifierExpr, IfStmt, LambdaExpr,
    LiteralExpr, MatchExpr, MatchStmt, PrimitiveType, ProgramNode, ReturnStmt, ThrowStmt,
    TryStmt, TypeNode, UncheckedStmt, VarDeclStmt, WhileStmt,
)
from .errors import SemanticError


def set_later(symbol) -> bool:
    """A `let` declared without a value - its one assignment comes later."""
    decl = getattr(symbol, 'declaration', None)
    return isinstance(decl, VarDeclStmt) and decl.inferred == 'let' and decl.initializer is None


def not_yet_set(name: str) -> str:
    return f"'{name}' is read before it has a value - set it first, on every path"


class InferredRulesMixin:
    """The type checker's rules for let / var and match values (a mixin of TypeChecker)."""

    def _value_type_for(self, name: str, keyword: str, value) -> Optional[TypeNode]:
        """The type a let / var takes from a value - None (with an error) when it can't."""
        if isinstance(value, CallExpr):
            self._allow_array_call(value)       # let scores = make() (an array, Task 18.2.4)
        value_type = self.visit(value)
        self.checked_receivers[id(value)] = value_type     # checked once, not again
        problem = None
        if isinstance(value, LiteralExpr) and value.type_hint == 'null':
            problem = f"null has no type - give one: Color {name} = null"
        elif isinstance(value, ArrayLiteralExpr) and not value.elements:
            problem = f"[] has no element type - give one: int[] {name} = [] or List<int>"
        elif isinstance(value_type, PrimitiveType) and value_type.name == 'void':
            if isinstance(value, CallExpr):
                problem = "this call gives no value"
            else:
                return None                     # an earlier error
        if problem:
            self.checked_receivers.pop(id(value), None)
            self.errors.append(SemanticError(f"'{keyword} {name}' takes its type from its value: "
                                             f"{problem}", value.location))
            return None
        return copy.copy(value_type)

    def check_inferred_declaration(self, node: VarDeclStmt) -> bool:
        """`let x = ...` / `var x = ...`: fill in the type from the value, then check it as a
        declaration of that type. Returns False when there is nothing more to check."""
        symbol = self.symbol_table.lookup(node.name)
        if node.initializer is None:
            if self.symbol_table.current_scope is self.symbol_table.global_scope:
                self.errors.append(SemanticError(
                    f"A module-level '{node.inferred} {node.name}' needs its value where it is "
                    f"declared", node.location))
            return False
        value_type = self._value_type_for(node.name, node.inferred, node.initializer)
        if value_type is None:
            return False
        node.var_type = value_type
        if symbol is not None:
            symbol.data_type = value_type
        return True

    def first_value(self, node: AssignmentStmt, symbol) -> None:
        """`total = 100` for a `let total` / `var total` declared without a value: the first
        value gives it its type (check_set_once checks the paths)."""
        value_type = self._value_type_for(node.target.name, symbol.declaration.inferred, node.value)
        if value_type is None:
            return
        self.checked_receivers.pop(id(node.value), None)
        symbol.data_type = symbol.declaration.var_type = value_type

    # ------------------------------------------------------------------ match values (46.2)

    def visit_MatchExpr(self, node: MatchExpr) -> TypeNode:
        """A match that gives a value: each case's values checked like a match statement's,
        every possible value covered, and one value type for every case."""
        subject_type = self.visit(node.subject)
        node.exhaustive = node.else_body is not None
        nulls = [p for case in node.cases for p in case.patterns if p.is_null]
        node.has_null_case = bool(nulls)
        if len(nulls) > 1:
            self.errors.append(SemanticError("A match can have only one 'null' case",
                                             nulls[1].location))
        for case in node.cases:
            for pattern in case.patterns:
                if pattern.bindings:
                    self.errors.append(SemanticError(
                        "A match that gives a value can't read a value's data - use a match "
                        "statement", pattern.location))
        all_patterns = [case.patterns for case in node.cases]
        for case in node.cases:
            case.patterns = [p for p in case.patterns if not p.is_null]
        try:
            if isinstance(subject_type, EnumType):
                self._check_enum_cases(node, subject_type.declaration)
            elif isinstance(subject_type, PrimitiveType) and subject_type.name in self._MATCH_CONSTANT_TYPES:
                self._check_constant_cases(node, subject_type)
            elif not (isinstance(subject_type, PrimitiveType) and subject_type.name == 'void'):
                self.errors.append(SemanticError(
                    f"match works on an enum, int, byte, char or string value, got "
                    f"{self.type_to_string(subject_type)}", node.subject.location))
        finally:
            for case, patterns in zip(node.cases, all_patterns):
                case.patterns = patterns
        values = [case.value for case in node.cases] + (
            [node.else_body] if node.else_body is not None else [])
        result = None
        for value in values:
            value_type = self.visit(value)
            if result is None:
                result = value_type
            elif not (self.types_compatible(result, value_type)
                      and self.types_compatible(value_type, result)):
                self.errors.append(SemanticError(
                    f"Every case of a match that gives a value gives the same type - this one "
                    f"is {self.type_to_string(value_type)}, the first "
                    f"{self.type_to_string(result)}", value.location))
        if isinstance(result, ArrayType):
            self.errors.append(SemanticError("A match can't give an array yet", node.location))
        return result or PrimitiveType(location=node.location, name='void')


def check_set_once(program: ProgramNode) -> List[SemanticError]:
    """A `let` / `var` declared without a value: on every path it is set before it is read,
    and a `let` exactly once (never twice, never inside a loop it was declared outside of)."""
    errors: List[SemanticError] = []
    reported = set()

    def report(message, location):
        key = (message, str(location))
        if key not in reported:
            reported.add(key)
            errors.append(SemanticError(message, location))

    for decl in program.declarations:
        if isinstance(decl, FunctionDecl) and decl.body is not None:
            _Paths(report).run(decl.body)
    return errors


class _Paths:
    """Walks a function's statements tracking, for each pending let / var, whether it is
    'unset', 'set' or 'maybe' (set on some paths) at each point."""

    def __init__(self, report):
        self.report = report
        self.kinds: Dict[str, str] = {}     # name -> 'let' / 'var'
        self.loops: List[set] = []          # names declared inside each enclosing loop

    def run(self, body) -> None:
        self.block(body, {})

    @staticmethod
    def merge(*states):
        states = [s for s in states if s is not None]     # None: a path that ended
        if not states:
            return None
        merged = {}
        for name in states[0]:
            values = {s.get(name, 'unset') for s in states}
            merged[name] = values.pop() if len(values) == 1 else 'maybe'
        return merged

    def reads(self, node, state) -> None:
        if state is None or node is None or isinstance(node, (type, LambdaExpr)):
            return
        if isinstance(node, list):
            for item in node:
                self.reads(item, state)
            return
        if isinstance(node, IdentifierExpr):
            if state.get(node.name) in ('unset', 'maybe'):
                self.report(not_yet_set(node.name), node.location)
            return
        if not is_dataclass(node):
            return
        for f in dataclass_fields(node):
            if f.name not in ('location', 'inferred_type', 'scope', 'declaration',
                              'callee_declaration', 'resolved_arguments', 'var_type'):
                self.reads(getattr(node, f.name), state)

    def block(self, node, state):
        statements = node.statements if isinstance(node, BlockStmt) else [node]
        for statement in statements:
            if state is None:
                break                       # after a return / break: never reached
            state = self.statement(statement, state)
        return state

    def statement(self, node, state):
        if isinstance(node, VarDeclStmt):
            self.reads(node.initializer, state)
            if node.inferred and node.initializer is None:
                state = dict(state)
                state[node.name] = 'unset'
                self.kinds[node.name] = node.inferred
                if self.loops:
                    self.loops[-1].add(node.name)
            elif node.name in state:
                state = {k: v for k, v in state.items() if k != node.name}
            return state
        if isinstance(node, AssignmentStmt):
            self.reads(node.value, state)
            if isinstance(node.target, IdentifierExpr) and node.target.name in state:
                name = node.target.name
                if self.kinds.get(name) == 'let':
                    if state[name] != 'unset':
                        self.report(f"'{name}' is a let - it can be set only once",
                                    node.location)
                    elif self.loops and name not in self.loops[-1]:
                        self.report(f"'{name}' is a let - setting it inside a loop would set it "
                                    f"more than once", node.location)
                state = dict(state)
                state[name] = 'set'
                return state
            self.reads(node.target, state)
            return state
        if isinstance(node, (ReturnStmt, ThrowStmt)):
            self.reads(node.value, state)
            return None
        if isinstance(node, (BreakStmt, ContinueStmt)):
            return None
        if isinstance(node, IfStmt):
            self.reads(node.condition, state)
            then = self.block(node.then_branch, dict(state))
            other = self.block(node.else_branch, dict(state)) if node.else_branch is not None \
                else dict(state)
            return self.merge(then, other)
        if isinstance(node, (WhileStmt, ForStmt)):
            for part in ('condition', 'iterable', 'start', 'end', 'step'):
                self.reads(getattr(node, part, None), state)
            self.loops.append(set())
            after = self.block(node.body, dict(state))
            self.loops.pop()
            return self.merge(state, after) or state
        if isinstance(node, MatchStmt):
            self.reads(node.subject, state)
            paths = [self.block(case.body, dict(state)) for case in node.cases]
            if node.else_body is not None:
                paths.append(self.block(node.else_body, dict(state)))
            elif not getattr(node, 'exhaustive', False):
                paths.append(dict(state))
            if getattr(node, 'falls', False):
                return self.merge(state, *paths) or state
            return self.merge(*paths)
        if isinstance(node, TryStmt):
            body = self.block(node.body, dict(state))
            start = self.merge(state, body) or state
            caught = [self.block(c.body, dict(start)) for c in node.catches]
            state = self.merge(body, *caught) if node.catches else body
            if node.finally_body is not None:
                state = self.block(node.finally_body, dict(state if state is not None else start))
            return state
        if isinstance(node, (BlockStmt, UncheckedStmt)):
            return self.block(node.body if isinstance(node, UncheckedStmt) else node, state)
        if isinstance(node, ExpressionStmt):
            self.reads(node.expression, state)
            return state
        self.reads(node, state)
        return state
