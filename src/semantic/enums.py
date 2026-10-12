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
    IdentifierExpr, ListType, MemberExpr, ParameterDecl, PrimitiveType, ProgramNode,
    StructType, TypeNode, VarDeclStmt,
)
from .errors import SemanticError

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
        if variant.value in numbers and variant.name not in names:
            errors.append(SemanticError(
                f"'{variant.name}' and '{numbers[variant.value]}' in enum '{enum.name}' both "
                f"have the value {variant.value} - each value needs its own number", where))
        if variant.fields:
            errors.append(SemanticError(
                f"'{variant.name}' carries data - enums with data are not built yet "
                f"(Task 25.4)", where))
        names.setdefault(variant.name, variant)
        numbers.setdefault(variant.value, variant.name)
    return errors


class EnumRulesMixin:
    """Type rules for enums (Task 25.2), mixed into the TypeChecker."""

    def enum_type(self, decl: EnumDecl, location) -> EnumType:
        return EnumType(location=location, name=decl.name, declaration=decl)

    def visit_EnumValueExpr(self, node: EnumValueExpr) -> TypeNode:
        decl = node.declaration
        if decl.variant(node.member) is None:
            self.errors.append(SemanticError(
                f"Enum '{decl.name}' has no value '{node.member}' (its values: "
                f"{', '.join(v.name for v in decl.variants)})", node.location))
        return self.enum_type(decl, node.location)

    def visit_EnumStaticCall(self, node: EnumStaticCall) -> TypeNode:
        decl = node.declaration
        string = PrimitiveType(location=node.location, name='string')
        if node.method == 'values':
            self._expect_enum_arguments(node, [])
            return ListType(location=node.location, element_type=self.enum_type(decl, node.location))
        if node.method == 'fromString':
            self._expect_enum_arguments(node, [string])
            return self.enum_type(decl, node.location)
        if decl.variant(node.method) is not None:
            self.errors.append(SemanticError(
                f"'{decl.name}.{node.method}' is a value, not a function - write it "
                f"without ( )", node.location))
        else:
            self.errors.append(SemanticError(
                f"Enum '{decl.name}' has no function '{node.method}' (it has "
                f"{decl.name}.values() and {decl.name}.fromString(text))", node.location))
        return self.enum_type(decl, node.location)

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
