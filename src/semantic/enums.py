"""Enums (Task 25): normalizing the AST, registering enums, and their type rules.

The parser can't tell an enum name from a struct name - `Color c` and `Color.Red` look like
a struct type and a field access. normalize_enums() runs first in semantic analysis (after
the module loader has merged every module and given each enum its internal name), and
rewrites, once it knows which names are enums:

    Color c                      StructType('Color')  -> EnumType('Color')
    Color.Red                    MemberExpr           -> EnumValueExpr
    Color.values(), .fromString  CallExpr             -> EnumStaticCall

so the rest of the compiler never mistakes an enum for a struct. EnumRulesMixin holds the
type checker's rules for these nodes.
"""

from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Dict, List, Optional

from src.parser.ast_nodes import (
    ASTNode, CallExpr, EnumDecl, EnumStaticCall, EnumType, EnumValueExpr, ForStmt,
    IdentifierExpr, ListType, LiteralExpr, MatchStmt, MemberExpr, ParameterDecl,
    PrimitiveType, ProgramNode, StructType, TypeNode, UnaryExpr, VarDeclStmt,
)
from .errors import SemanticError

# The number that means "no value" (Task 30.11) - FUSION_ENUM_NULL in the C run-time
ENUM_NULL = -2147483647

# Calls on the enum itself, Color.values() - a value can't have one of these names
ENUM_STATICS = ('values', 'fromString')

# Methods on an enum value, c.toString() - rewritten to the built-in call toString(c)
ENUM_METHODS = ('toString', 'toInt')

_SKIP_FIELDS = ('location', 'inferred_type', 'declaration', 'callee_declaration', 'scope',
                'resolved_arguments')


def normalize_enums(program: ProgramNode) -> List[SemanticError]:
    """Rewrite enum types, values and static calls (see the module docstring). Returns
    errors for a variable or parameter that reuses an enum's name."""
    enums: Dict[str, EnumDecl] = {d.name: d for d in program.declarations
                                  if isinstance(d, EnumDecl)}
    errors: List[SemanticError] = []
    if not enums:
        return errors

    def enum_named(node) -> Optional[EnumDecl]:
        if isinstance(node, IdentifierExpr):
            return enums.get(node.name)
        return None

    def convert(node) -> Optional[ASTNode]:
        if isinstance(node, StructType) and node.name in enums:
            return EnumType(location=node.location, name=node.name, declaration=enums[node.name])
        if isinstance(node, CallExpr) and isinstance(node.callee, MemberExpr):
            decl = enum_named(node.callee.object)
            if decl is not None:
                return EnumStaticCall(location=node.location, enum_name=decl.name,
                                      method=node.callee.member, arguments=node.arguments,
                                      declaration=decl)
        if isinstance(node, MemberExpr):
            decl = enum_named(node.object)
            if decl is not None:
                return EnumValueExpr(location=node.location, enum_name=decl.name,
                                     member=node.member, declaration=decl)
        return None

    def check_name(name: str, node: ASTNode, what: str) -> None:
        if name in enums:
            errors.append(SemanticError(
                f"'{name}' is an enum - choose another name for the {what}", node.location))

    def walk(node) -> None:
        if isinstance(node, list):
            for i, item in enumerate(node):
                new = convert(item)
                if new is not None:
                    node[i] = new
                walk(node[i])
            return
        if not is_dataclass(node) or isinstance(node, type):
            return
        if isinstance(node, VarDeclStmt):
            check_name(node.name, node, 'variable')
        elif isinstance(node, ParameterDecl):
            check_name(node.name, node, 'parameter')
        elif isinstance(node, ForStmt):
            check_name(node.variable, node, 'loop variable')
        for f in dataclass_fields(node):
            if f.name in _SKIP_FIELDS:
                continue
            value = getattr(node, f.name)
            if isinstance(value, list):
                walk(value)
                continue
            new = convert(value)
            if new is not None:
                setattr(node, f.name, new)
                value = new
            walk(value)

    walk(program.declarations)
    return errors


def check_enum_declaration(enum: EnumDecl) -> List[SemanticError]:
    """Two values with one name or one number, or a value named like an enum call."""
    errors = []
    names, numbers = {}, {}
    for variant in enum.variants:
        where = variant.location
        if variant.name in names:
            errors.append(SemanticError(
                f"Enum '{enum.name}' has two values named '{variant.name}'", where))
        if variant.name in ENUM_STATICS:
            errors.append(SemanticError(
                f"'{variant.name}' can't be a value of enum '{enum.name}' - "
                f"{enum.name}.{variant.name}() is built in", where))
        if variant.value == ENUM_NULL:
            errors.append(SemanticError(
                f"{variant.value} is kept for null - give '{variant.name}' another number", where))
        if variant.value in numbers and variant.name not in names:
            errors.append(SemanticError(
                f"'{variant.name}' and '{numbers[variant.value]}' in enum '{enum.name}' both "
                f"have the value {variant.value} - each value needs its own number", where))
        errors.extend(_check_variant_fields(enum, variant))
        names.setdefault(variant.name, variant)
        numbers.setdefault(variant.value, variant.name)
    return errors


def has_data(enum: EnumDecl) -> bool:
    """True for an enum with at least one value carrying data (Task 25.4)."""
    return any(v.fields for v in enum.variants)


def _check_variant_fields(enum: EnumDecl, variant) -> List[SemanticError]:
    errors, seen = [], set()
    for f in variant.fields:
        if f.name in seen:
            errors.append(SemanticError(
                f"'{variant.name}' of enum '{enum.name}' has two fields named '{f.name}'",
                f.location))
        seen.add(f.name)
        if f.default_value is not None:
            errors.append(SemanticError(
                f"The data of '{variant.name}' can't have a default value - it is given when "
                f"the value is made", f.location))
        kind = f.field_type
        if isinstance(kind, PrimitiveType) and kind.name == 'void' or type(kind).__name__ == 'FunctionType':
            errors.append(SemanticError(
                f"Field '{f.name}' of '{variant.name}' can't be "
                f"{'void' if isinstance(kind, PrimitiveType) else 'a function'}", f.location))
        if type(kind).__name__ == 'ArrayType':
            errors.append(SemanticError(
                f"Field '{f.name}' of '{variant.name}' can't be an array - use a List",
                f.location))
    # (The first value may hold the enum too since Task 30.11: a variable given no value is
    # null, not the first value)
    return errors


def check_holding_loops(program: ProgramNode) -> List[SemanticError]:
    """A value can't hold itself through other types (Task 25.5): enum E holds struct S
    which holds E again would never end. An enum holding itself directly is fine - that
    field is stored on the heap; anything else in the loop must go through a List."""
    from src.parser.ast_nodes import StructDecl, ArrayType
    decls = {d.name: d for d in program.declarations if isinstance(d, (EnumDecl, StructDecl))}

    def held(decl):
        fields = ([f for v in decl.variants for f in v.fields] if isinstance(decl, EnumDecl)
                  else decl.fields)
        for f in fields:
            kind = f.field_type
            while isinstance(kind, ArrayType):
                kind = kind.element_type
            name = getattr(kind, 'name', None)
            if type(kind).__name__ in ('EnumType', 'StructType') and name in decls \
                    and not (isinstance(decl, EnumDecl) and name == decl.name):
                yield name, f

    errors, reported = [], set()

    def visit(name, path):
        if name in path:
            loop = path[path.index(name):]
            if frozenset(loop) not in reported:
                reported.add(frozenset(loop))
                errors.append(SemanticError(
                    f"{' holds '.join(loop + [name])} - a value can't hold itself this way; "
                    f"hold it in a List instead (List<{name}>)", decls[name].location))
            return
        for inner, _ in held(decls[name]):
            visit(inner, path + [name])

    for name, decl in decls.items():
        if isinstance(decl, EnumDecl):
            visit(name, [])
    return errors


class EnumRulesMixin:
    """Type rules for enums (Task 25.2), mixed into the TypeChecker."""

    def enum_type(self, decl: EnumDecl, location) -> EnumType:
        return EnumType(location=location, name=decl.name, declaration=decl)

    def visit_EnumValueExpr(self, node: EnumValueExpr) -> TypeNode:
        decl = node.declaration
        variant = decl.variant(node.member)
        if variant is None:
            self.errors.append(SemanticError(
                f"Enum '{decl.name}' has no value '{node.member}' (its values: "
                f"{', '.join(v.name for v in decl.variants)})", node.location))
        elif variant.fields:
            self.errors.append(SemanticError(
                f"'{decl.name}.{node.member}' carries data - give it: {decl.name}.{node.member}("
                f"{', '.join(f.name for f in variant.fields)})", node.location))
        return self.enum_type(decl, node.location)

    def visit_EnumStaticCall(self, node: EnumStaticCall) -> TypeNode:
        decl = node.declaration
        string = PrimitiveType(location=node.location, name='string')
        if node.method in ENUM_STATICS and has_data(decl):
            self.errors.append(SemanticError(
                f"{decl.name}.{node.method}() only works on an enum whose values carry no data",
                node.location))
            return self.enum_type(decl, node.location)
        if node.method == 'values':
            self._expect_enum_arguments(node, [])
            return ListType(location=node.location, element_type=self.enum_type(decl, node.location))
        if node.method == 'fromString':
            self._expect_enum_arguments(node, [string])
            return self.enum_type(decl, node.location)
        variant = decl.variant(node.method)
        if variant is not None and variant.fields:
            self._check_enum_construction(node, decl, variant)
            return self.enum_type(decl, node.location)
        if variant is not None:
            self.errors.append(SemanticError(
                f"'{decl.name}.{node.method}' is a value, not a function - write it "
                f"without ( )", node.location))
        else:
            self.errors.append(SemanticError(
                f"Enum '{decl.name}' has no function '{node.method}' (it has "
                f"{decl.name}.values() and {decl.name}.fromString(text))", node.location))
        return self.enum_type(decl, node.location)

    # ------------------------------------------------------------------ match (Task 25.3)

    _MATCH_CONSTANT_TYPES = ('int', 'byte', 'char', 'string')

    def visit_MatchStmt(self, node: MatchStmt) -> None:
        """A match on an enum: bare value names, every value covered unless there is an
        `else`. On an int, byte, char or string: constant cases and a required `else`. A
        value can't be handled twice. Sets node.exhaustive - the validator reads it."""
        subject_type = self.visit(node.subject)
        node.exhaustive = node.else_body is not None
        # case null (Task 30.12): at most one, on any value (a library may hand over a null);
        # the checks below see the other patterns only
        nulls = [p for case in node.cases for p in case.patterns if p.is_null]
        node.has_null_case = bool(nulls)
        if len(nulls) > 1:
            self.errors.append(SemanticError("A match can have only one 'case null'",
                                             nulls[1].location))
        if nulls and type(subject_type).__name__ == 'ErrorType':
            self.errors.append(SemanticError(
                "An Error is never null - test it with 'if err' / 'if not err'", nulls[0].location))
        if node.falls:
            # fall match (Task 30.13): a case can be reached from the one above it, so it
            # can't name a value's data - only the value it matched has that data
            for case in node.cases:
                for pattern in case.patterns:
                    if pattern.bindings:
                        self.errors.append(SemanticError(
                            "A 'fall match' can't read a value's data - a case may be reached "
                            "from the one above it; use 'match'", pattern.location))
        all_patterns = [case.patterns for case in node.cases]
        for case in node.cases:
            case.patterns = [p for p in case.patterns if not p.is_null]
        try:
            self._check_cases_by_type(node, subject_type)
        finally:
            for case, patterns in zip(node.cases, all_patterns):
                case.patterns = patterns

    def _check_cases_by_type(self, node: MatchStmt, subject_type) -> None:
        if isinstance(subject_type, EnumType):
            self._check_enum_cases(node, subject_type.declaration)
        elif type(subject_type).__name__ == 'ErrorType':
            self._check_error_cases(node)               # Task 26.10
            return
        elif isinstance(subject_type, PrimitiveType) and subject_type.name in self._MATCH_CONSTANT_TYPES:
            self._check_constant_cases(node, subject_type)
        elif not (isinstance(subject_type, PrimitiveType) and subject_type.name == 'void'):
            self.errors.append(SemanticError(
                f"match works on an enum, int, byte, char or string value, got "
                f"{self.type_to_string(subject_type)}", node.subject.location))
        for case in node.cases:
            self.visit(case.body)
        if node.else_body is not None:
            self.visit(node.else_body)

    def _check_error_cases(self, node: MatchStmt) -> None:
        """`match err` with error type names as cases (Task 26.10): `case FileError` matches a
        FileError or one of its subtypes, `case Error` any error. A name that isn't an error
        type is a compile error. Inside a case with one type, err is that type - so its own
        fields can be read. Error types can't all be listed: an else (or `case Error`) is
        required."""
        from .error_rules import is_error_subtype
        from src.parser.ast_nodes import ErrorType
        catches_all = False
        seen = []
        for case in node.cases:
            types = []
            for pattern in case.patterns:
                pattern.error_declaration = None
                if pattern.name is None or pattern.bindings:
                    self.errors.append(SemanticError(
                        "A case on an Error names an error type, e.g. case FileError",
                        pattern.location))
                    continue
                if pattern.name == 'Error':
                    catches_all = True
                    types.append(None)
                    continue
                symbol = self.symbol_table.lookup(pattern.name)
                if symbol is None or symbol.symbol_type != 'errortype':
                    self.errors.append(SemanticError(
                        f"'{pattern.name}' is not an error type", pattern.location))
                    continue
                decl = symbol.declaration
                if any(is_error_subtype(decl, earlier) for earlier in seen if earlier is not None) \
                        or None in seen:
                    self.warnings.append(SemanticError(
                        f"'{pattern.name}' never matches here - an earlier case already takes it",
                        pattern.location))
                pattern.error_declaration = decl
                types.append(decl)
            seen.extend(types)
            # Inside the case, err is that error type (one type, err a variable)
            narrowed = None
            if len(types) == 1 and types[0] is not None and type(node.subject).__name__ == 'IdentifierExpr':
                narrowed = self.symbol_table.lookup(node.subject.name)
            if narrowed is not None:
                saved = narrowed.data_type
                narrowed.data_type = ErrorType(location=case.location, name=types[0].name,
                                               declaration=types[0])
                try:
                    self.visit(case.body)
                finally:
                    narrowed.data_type = saved
            else:
                self.visit(case.body)
        node.exhaustive = node.else_body is not None or catches_all
        if not node.exhaustive:
            self.errors.append(SemanticError(
                "A match on an Error needs an else (or `case Error`) - error types can't all be "
                "listed", node.location))
        if node.else_body is not None:
            self.visit(node.else_body)

    def _check_enum_cases(self, node: MatchStmt, decl: EnumDecl) -> None:
        handled = set()
        for case in node.cases:
            for pattern in case.patterns:
                if pattern.dotted:
                    self.errors.append(SemanticError(
                        f"In a case, write just the value's name: case "
                        f"{pattern.name.split('.')[-1]}", pattern.location))
                    continue
                if pattern.name is None:
                    self.errors.append(SemanticError(
                        f"A case on enum '{decl.name}' names one of its values, e.g. case "
                        f"{decl.variants[0].name}", pattern.location))
                    continue
                variant = decl.variant(pattern.name)
                if variant is None:
                    self.errors.append(SemanticError(
                        f"Enum '{decl.name}' has no value '{pattern.name}' (its values: "
                        f"{', '.join(v.name for v in decl.variants)})", pattern.location))
                    continue
                if pattern.name in handled:
                    self.errors.append(SemanticError(
                        f"'{pattern.name}' is already handled by an earlier case", pattern.location))
                handled.add(pattern.name)
                if pattern.bindings and not variant.fields:
                    self.errors.append(SemanticError(
                        f"'{pattern.name}' carries no data - write just case {pattern.name}",
                        pattern.location))
                elif pattern.bindings:
                    self._type_bindings(case, pattern, variant)
        missing = [v.name for v in decl.variants if v.name not in handled]
        if node.else_body is None and missing:
            self.errors.append(SemanticError(
                f"This match on {decl.name} doesn't handle {', '.join(missing)} - add a case "
                f"for {'it' if len(missing) == 1 else 'them'}, or an else (or _)", node.location))
        elif node.else_body is not None and not missing:
            self.warnings.append(SemanticError(
                f"The else of this match never runs - every value of {decl.name} has its own "
                f"case", node.else_body.location))
        node.exhaustive = True if not missing else node.exhaustive

    def _type_bindings(self, case, pattern, variant) -> None:
        """`case Number(n)`: n gets the field's type, in the case's own scope (Task 25.4)."""
        if len(case.patterns) > 1:
            self.errors.append(SemanticError(
                "A case with several values can't name their data - give it its own case",
                pattern.location))
            return
        if len(pattern.bindings) != len(variant.fields):
            self.errors.append(SemanticError(
                f"'{variant.name}' carries {len(variant.fields)} value(s) ("
                f"{', '.join(f.name for f in variant.fields)}) - name each, or write just "
                f"case {variant.name}", pattern.location))
            return
        scope = getattr(case.body, 'scope', None)
        for name, f in zip(pattern.bindings, variant.fields):
            symbol = scope.lookup(name) if scope is not None and name != '_' else None
            if symbol is not None:
                symbol.data_type = f.field_type

    def _check_constant_cases(self, node: MatchStmt, subject_type: PrimitiveType) -> None:
        seen = set()
        for case in node.cases:
            for pattern in case.patterns:
                value = pattern.value
                constant = isinstance(value, LiteralExpr) and value.type_hint != 'null' or (
                    isinstance(value, UnaryExpr) and value.operator == '-'
                    and isinstance(value.operand, LiteralExpr)
                    and value.operand.type_hint in ('int', 'float', 'double'))
                if not constant:
                    self.errors.append(SemanticError(
                        f"A case on {subject_type.name} needs a constant, such as 42, 'x' or "
                        f"\"text\"", pattern.location))
                    continue
                value_type = self.visit(value)
                if not self.types_compatible(subject_type, value_type):
                    self.errors.append(SemanticError(
                        f"This case is {self.type_to_string(value_type)}, but the match is on "
                        f"{subject_type.name}", pattern.location))
                    continue
                key = ('-', value.operand.value) if isinstance(value, UnaryExpr) else value.value
                if key in seen:
                    self.errors.append(SemanticError(
                        "This value is already handled by an earlier case", pattern.location))
                seen.add(key)
        if node.else_body is None:
            self.errors.append(SemanticError(
                f"A match on {subject_type.name} needs an else (or _) - its values can't all "
                f"be listed", node.location))

    def _check_enum_construction(self, node: EnumStaticCall, decl: EnumDecl, variant) -> None:
        """Token.Number(42) or Token.Number(value = 42) - one argument per field (Task 25.4)."""
        owner = f"'{decl.name}.{variant.name}'"
        if any(type(a).__name__ == 'NamedArgument' for a in node.arguments):
            self._check_named_call(node, owner, 'field',
                                   [(f.name, f.field_type, None) for f in variant.fields])
            return
        if len(node.arguments) != len(variant.fields):
            self.errors.append(SemanticError(
                f"{owner} takes {len(variant.fields)} value(s) ("
                f"{', '.join(f.name for f in variant.fields)}), got {len(node.arguments)}",
                node.location))
            for argument in node.arguments:
                self.visit(argument)
            return
        for f, argument in zip(variant.fields, node.arguments):
            got = self._visit_value_for(f.field_type, argument)
            if not self.types_compatible(f.field_type, got):
                self.errors.append(SemanticError(
                    f"{owner} field '{f.name}': expected {self.type_to_string(f.field_type)}, "
                    f"got {self.type_to_string(got)}", argument.location))
        node.resolved_arguments = list(node.arguments)

    def _expect_enum_arguments(self, node: EnumStaticCall, expected: List[TypeNode]) -> None:
        call = f"{node.declaration.name}.{node.method}"
        if len(node.arguments) != len(expected):
            self.errors.append(SemanticError(
                f"{call}() takes {len(expected)} argument(s), got {len(node.arguments)}",
                node.location))
        for argument, want in zip(node.arguments, expected):
            got = self.visit(argument)
            if not self.types_compatible(want, got):
                self.errors.append(SemanticError(
                    f"{call}() needs {self.type_to_string(want)}, got {self.type_to_string(got)}",
                    argument.location))
