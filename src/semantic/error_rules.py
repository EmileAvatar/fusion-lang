"""Error handling (Task 26): normalizing `Error`, and its type rules.

`Error` is a built-in value - message, code, where - and the way a function fails:

    Ship, Error function loadShip(string file)      can fail; `return Error("...")` fails
    Error function save(Ship s)                      a void function that can fail
    Ship s, Error err = loadShip(f)                  capture the error (any call)
    if err                                           true when there is one

normalize_errors() runs first in semantic analysis and rewrites, once:

    Error e                 StructType('Error')  -> ErrorType
    Error("msg", 404)       CallExpr             -> ErrorMakeExpr
    Error function f()      return type Error    -> void, returns_error

An error nobody captures bubbles up to the caller (src/codegen/c_errors.py).
"""

from dataclasses import fields as dataclass_fields, is_dataclass
from typing import List, Optional

from src.parser.ast_nodes import (
    ASTNode, CallExpr, EnumDecl, ErrorActiveExpr, ErrorMakeExpr, ErrorType, FunctionDecl,
    IdentifierExpr, PrimitiveType, ProgramNode, StructDecl, StructType, TypeNode,
)
from .errors import SemanticError

# The fields every Error has, and their types
ERROR_FIELDS = {'message': 'string', 'code': 'int', 'where': 'string'}

_SKIP_FIELDS = ('location', 'inferred_type', 'declaration', 'callee_declaration', 'scope',
                'resolved_arguments')


def normalize_errors(program: ProgramNode) -> List[SemanticError]:
    errors: List[SemanticError] = []

    def convert(node) -> Optional[ASTNode]:
        if isinstance(node, StructType) and node.name == 'Error':
            return ErrorType(location=node.location)
        if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                and node.callee.name == 'Error':
            return ErrorMakeExpr(location=node.location, arguments=node.arguments)
        return None

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
    for decl in program.declarations:
        if isinstance(decl, (FunctionDecl, StructDecl, EnumDecl)) and decl.name == 'Error':
            errors.append(SemanticError(
                "'Error' is a built-in type - choose another name", decl.location))
        if isinstance(decl, FunctionDecl) and isinstance(decl.return_type, ErrorType):
            if decl.returns_error:
                errors.append(SemanticError(
                    f"'{decl.name}' is declared 'Error, Error function' - a function that can "
                    f"fail is 'T, Error function', or 'Error function' when it returns no value",
                    decl.location))
            # `Error function save()` - returns no value, and can fail
            decl.returns_error = True
            decl.return_type = PrimitiveType(location=decl.return_type.location, name='void')
    return errors


class ErrorRulesMixin:
    """Type rules for Error values (Task 26), mixed into the TypeChecker."""

    def error_type(self, location) -> ErrorType:
        return ErrorType(location=location)

    def visit_ErrorMakeExpr(self, node: ErrorMakeExpr) -> TypeNode:
        """Error("message") or Error("message", code)."""
        if not 1 <= len(node.arguments) <= 2:
            self.errors.append(SemanticError(
                f"Error(...) takes a message and optionally a code, got {len(node.arguments)} "
                f"argument(s)", node.location))
        expected = ['string', 'int']
        for argument, want in zip(node.arguments, expected):
            if type(argument).__name__ == 'NamedArgument':
                self.errors.append(SemanticError(
                    "Error(...) takes its message and code in order, without names",
                    argument.location))
                continue
            got = self.visit(argument)
            want_type = PrimitiveType(location=argument.location, name=want)
            if not self.types_compatible(want_type, got):
                self.errors.append(SemanticError(
                    f"Error(...) needs a {want} {'message' if want == 'string' else 'code'}, got "
                    f"{self.type_to_string(got)}", argument.location))
        return self.error_type(node.location)

    def visit_ErrorActiveExpr(self, node: ErrorActiveExpr) -> TypeNode:
        self.visit(node.operand)
        return PrimitiveType(location=node.location, name='bool')

    def error_member_type(self, node) -> TypeNode:
        """err.message, err.code, err.where."""
        if node.member not in ERROR_FIELDS:
            self.errors.append(SemanticError(
                f"An Error has no field '{node.member}' (its fields: "
                f"{', '.join(ERROR_FIELDS)})", node.location))
            return PrimitiveType(location=node.location, name='void')
        return PrimitiveType(location=node.location, name=ERROR_FIELDS[node.member])

    def condition_type(self, owner, attribute: str) -> TypeNode:
        """The type of a condition; an Error there means "there is an error" (user decision:
        a simple `if err`) - the node is wrapped so code generation tests that."""
        condition = getattr(owner, attribute)
        result = self.visit(condition)
        if isinstance(result, ErrorType):
            wrapped = ErrorActiveExpr(location=condition.location, operand=condition)
            setattr(owner, attribute, wrapped)
            return self.visit(wrapped)
        return result
