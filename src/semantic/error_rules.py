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
    ASTNode, CallExpr, EnumDecl, ErrorActiveExpr, ErrorDecl, ErrorMakeExpr, ErrorType,
    FunctionDecl, IdentifierExpr, LiteralExpr, PrimitiveType, ProgramNode, StructDecl,
    StructType, ThrowStmt, TryStmt, TypeNode,
)
from .errors import SemanticError

# The fields every Error has, and their types
ERROR_FIELDS = {'message': 'string', 'code': 'int', 'where': 'string',
                'kind': 'string'}    # kind: the error type's name, "FileError" (Task 26.10)


# Fusion's own error types (Task 26.12): (name, parent, has a `path` field, default message).
# Their order fixes their kind numbers (1, 2, ...) - the C runtime raises them by number
BUILTIN_ERROR_TYPES = [
    ('ArithmeticError', 'Error', False, None),
    ('DivideByZeroError', 'ArithmeticError', False, 'Division by zero'),
    ('FormatError', 'Error', False, None),
    ('NumberFormatError', 'FormatError', False, None),
    ('PatternError', 'FormatError', False, None),
    ('HexFormatError', 'FormatError', False, None),
    ('TextEncodingError', 'FormatError', False, None),
    ('ValueError', 'Error', False, None),
    ('RangeError', 'ValueError', False, None),
    ('UnknownValueError', 'ValueError', False, None),
    ('LookupError', 'Error', False, None),
    ('IndexError', 'LookupError', False, 'Index out of range'),
    ('KeyError', 'LookupError', False, 'Key not found'),
    ('FileError', 'Error', True, None),
    ('FileNotFoundError', 'FileError', False, 'File not found'),
    ('PermissionError', 'FileError', False, 'Permission denied'),
    ('FileReadError', 'FileError', False, None),
    ('FileWriteError', 'FileError', False, None),
    ('FileTooLargeError', 'FileError', False, None),
    ('DeleteError', 'FileError', False, None),
    ('LimitError', 'Error', False, None),
    ('StringTooLongError', 'LimitError', False, None),
    ('ResultTooLargeError', 'LimitError', False, None),
    # (new types go last - the numbers above are fixed)
    ('OverflowError', 'ArithmeticError', False, None),          # Task 27.2b
    ('StackOverflowError', 'LimitError', False, None),          # Task 27.2c
]
BUILTIN_ERROR_NAMES = [name for name, _, _, _ in BUILTIN_ERROR_TYPES]


def builtin_error_decls(location) -> list:
    """Fresh ErrorDecls for Fusion's own error types, for one program."""
    from src.parser.ast_nodes import StructField
    decls = []
    for name, parent, has_path, message in BUILTIN_ERROR_TYPES:
        fields = [StructField(location=location, name='path',
                              field_type=PrimitiveType(location=location, name='string'),
                              default_value=LiteralExpr(location=location, value='',
                                                        type_hint='string'))] if has_path else []
        decl = ErrorDecl(location=location, name=name, parent=parent, fields=fields, builtin=True,
                         default_message=LiteralExpr(location=location, value=message,
                                                     type_hint='string') if message else None)
        decls.append(decl)
    return decls


def error_chain(decl) -> list:
    """A custom error type's line of ErrorDecls, from the one just below Error down to it."""
    chain = []
    while decl is not None and decl not in chain:
        chain.insert(0, decl)
        decl = decl.parent_declaration
    return chain


def all_error_fields(decl) -> list:
    """Every field of a custom error type: its parents' first, then its own."""
    return [f for d in error_chain(decl) for f in d.fields]


def is_error_subtype(child, parent) -> bool:
    """True when error type `child` (an ErrorDecl, or None for Error) is `parent` or one
    of its subtypes. Every error type is an Error."""
    if parent is None:
        return True
    return parent in error_chain(child)

_SKIP_FIELDS = ('location', 'inferred_type', 'declaration', 'callee_declaration', 'scope',
                'resolved_arguments')


def normalize_errors(program: ProgramNode) -> List[SemanticError]:
    errors: List[SemanticError] = []
    # Fusion's own error types first (Task 26.12) - a program's type can extend them, not
    # take their names
    location = program.declarations[0].location if program.declarations else None
    for decl in [d for d in program.declarations if isinstance(d, ErrorDecl) and not d.builtin]:
        if decl.name in BUILTIN_ERROR_NAMES:
            errors.append(SemanticError(
                f"'{decl.name}' is one of Fusion's own error types - extend it instead "
                f"(error MyError : {decl.name})", decl.location))
            program.declarations.remove(decl)
    if not any(isinstance(d, ErrorDecl) and d.builtin for d in program.declarations):
        program.declarations[0:0] = builtin_error_decls(location)
    # Custom error types (Task 26.9) - linked to their parents here
    custom = {d.name: d for d in program.declarations if isinstance(d, ErrorDecl)}
    errors.extend(_link_error_types(custom))

    def convert(node) -> Optional[ASTNode]:
        if isinstance(node, StructType) and (node.name == 'Error' or node.name in custom):
            return ErrorType(location=node.location, name=node.name,
                             declaration=custom.get(node.name))
        if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                and (node.callee.name == 'Error' or node.callee.name in custom):
            return ErrorMakeExpr(location=node.location, arguments=node.arguments,
                                 declaration=custom.get(node.callee.name))
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


def _link_error_types(custom: dict) -> List[SemanticError]:
    """Each custom error type's parent must be Error or another error type, with no loops;
    a field name can't repeat one from a parent, or be message / code / where / kind."""
    errors = []
    for decl in custom.values():
        if decl.parent != 'Error':
            decl.parent_declaration = custom.get(decl.parent)
            if decl.parent_declaration is None:
                errors.append(SemanticError(
                    f"Error type '{decl.name}' extends '{decl.parent}', which is not an error "
                    f"type (declare it with `error {decl.parent}`)", decl.location))
    for decl in custom.values():
        seen, step = set(), decl
        while step is not None and step.name not in seen:
            seen.add(step.name)
            step = step.parent_declaration
        if step is not None:
            errors.append(SemanticError(
                f"Error type '{decl.name}' extends itself through '{step.name}'", decl.location))
            decl.parent_declaration = None
    for decl in custom.values():
        taken = set(ERROR_FIELDS)
        for d in error_chain(decl):
            for f in d.fields:
                if f.name in taken and d is decl:
                    errors.append(SemanticError(
                        f"Error type '{decl.name}' already has a field '{f.name}'"
                        + (" (every error has message, code, where and kind)"
                           if f.name in ERROR_FIELDS or f.name == 'kind' else " from a parent"),
                        f.location))
                taken.add(f.name)
    return errors


def check_error_settings(program: ProgramNode, config) -> List[SemanticError]:
    """[errors] returns = false / exceptions = false (Task 26.5): that syntax is an error."""
    if config is None or (config.returns and config.exceptions):
        return []
    errors: List[SemanticError] = []
    off = "is turned off for this project ([errors] {key} = false in fusion.toml)"

    def walk(node) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if not is_dataclass(node) or isinstance(node, type):
            return
        if not config.returns:
            if type(node).__name__ == 'ReturnStmt' and getattr(node, 'raises', False):
                errors.append(SemanticError(
                    f"Returning an Error {off.format(key='returns')} - throw it instead",
                    node.location))
            if isinstance(node, FunctionDecl) and node.returns_error:
                errors.append(SemanticError(
                    f"'{node.name}' returns an Error - error returns {off.format(key='returns')}",
                    node.location))
            if type(node).__name__ == 'VarDeclStmt' and (node.error_name or getattr(node, 'capture_only', False)):
                errors.append(SemanticError(
                    f"Capturing an error {off.format(key='returns')}", node.location))
        if not config.exceptions and isinstance(node, (TryStmt, ThrowStmt)):
            what = 'try / catch / finally' if isinstance(node, TryStmt) else 'throw'
            errors.append(SemanticError(f"{what} {off.format(key='exceptions')}", node.location))
        for f in dataclass_fields(node):
            if f.name not in _SKIP_FIELDS:
                walk(getattr(node, f.name))

    walk(program.declarations)
    return errors


def marked_but_cannot_fail(program: ProgramNode) -> List[SemanticError]:
    """A function marked `, Error` with nothing in it that could fail: a warning (Task 26.7).
    Anything that might fail - a throw, `return Error(...)`, a call, an index, fromString -
    counts, so this never warns wrongly."""
    def might_fail(node) -> bool:
        if isinstance(node, list):
            return any(might_fail(item) for item in node)
        if not is_dataclass(node) or isinstance(node, type):
            return False
        if isinstance(node, (ThrowStmt, CallExpr)) or type(node).__name__ in (
                'IndexExpr', 'EnumStaticCall') or getattr(node, 'raises', False):
            return True
        return any(might_fail(getattr(node, f.name)) for f in dataclass_fields(node)
                   if f.name not in _SKIP_FIELDS)

    return [SemanticError(f"'{d.name}' is marked as able to fail (', Error'), but nothing in it "
                          f"can give an error", d.location)
            for d in program.declarations
            if isinstance(d, FunctionDecl) and d.returns_error and not might_fail(d.body)]


class ErrorRulesMixin:
    """Type rules for Error values (Task 26), mixed into the TypeChecker."""

    def error_type(self, location) -> ErrorType:
        return ErrorType(location=location)

    def visit_ErrorMakeExpr(self, node: ErrorMakeExpr) -> TypeNode:
        """Error("message", code) / FileError("message", code, path, ...) - by position or
        by name; message can be left out when the type gives a default, code is 0 unless
        given, a field without a default must be given (Task 26.9)."""
        decl = node.declaration
        name = decl.name if decl is not None else 'Error'
        loc = node.location
        message_default = next((d.default_message for d in reversed(error_chain(decl))
                                if d.default_message is not None), None)
        code_default = next((d.default_code for d in reversed(error_chain(decl))
                             if d.default_code is not None), None) \
            or LiteralExpr(location=loc, value=0, type_hint='int')
        slots = [('message', PrimitiveType(location=loc, name='string'), message_default),
                 ('code', PrimitiveType(location=loc, name='int'), code_default)]
        slots += [(f.name, f.field_type, f.default_value) for f in all_error_fields(decl)]
        self._check_named_call(node, f"'{name}(...)'", 'field', slots)
        return ErrorType(location=loc, name=name, declaration=decl)

    def visit_ErrorActiveExpr(self, node: ErrorActiveExpr) -> TypeNode:
        self.visit(node.operand)
        return PrimitiveType(location=node.location, name='bool')

    def visit_TryStmt(self, node: TryStmt) -> None:
        """try / catch err / finally (Task 26.3) - err is an Error in the catch block."""
        self.visit(node.body)
        taken = []      # the types caught so far (None: any error)
        for index, clause in enumerate(node.catches):
            decl = getattr(clause.error_type, 'declaration', None) \
                if isinstance(clause.error_type, ErrorType) else None
            catches_all = clause.error_type is None or (
                isinstance(clause.error_type, ErrorType) and decl is None)
            if None in taken or (decl is not None and any(
                    t is not None and is_error_subtype(decl, t) for t in taken)):
                self.warnings.append(SemanticError(
                    "This catch never runs - an earlier catch already takes its errors",
                    clause.location))
            if clause.error_type is None and index != len(node.catches) - 1:
                self.errors.append(SemanticError(
                    "A catch without an error type catches everything - it must be the last "
                    "catch", clause.location))
            taken.append(None if catches_all else decl)
            self.visit(clause.body)
        if node.finally_body is not None:
            self.visit(node.finally_body)

    def visit_ThrowStmt(self, node: ThrowStmt) -> None:
        value_type = self.visit(node.value)
        if not isinstance(value_type, ErrorType) and not (
                isinstance(value_type, PrimitiveType) and value_type.name == 'void'):
            self.errors.append(SemanticError(
                f"throw needs an Error - throw Error(\"what went wrong\") - got "
                f"{self.type_to_string(value_type)}", node.value.location))

    def error_member_type(self, node, error_type) -> TypeNode:
        """err.message, err.code, err.where - and a custom error type's own fields."""
        if node.member in ERROR_FIELDS:
            return PrimitiveType(location=node.location, name=ERROR_FIELDS[node.member])
        fields = all_error_fields(error_type.declaration)
        found = next((f for f in fields if f.name == node.member), None)
        if found is None:
            names = list(ERROR_FIELDS) + [f.name for f in fields]
            self.errors.append(SemanticError(
                f"{'An Error' if error_type.declaration is None else error_type.name} has no "
                f"field '{node.member}' (its fields: {', '.join(names)})", node.location))
            return PrimitiveType(location=node.location, name='void')
        return found.field_type

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
