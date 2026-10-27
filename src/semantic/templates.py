"""String templates (Task 29.3): expanding every use before semantic analysis.

    template string greet = "Hello {@1}, you are {@2} - welcome to {shop}"

A template is a fixed text that works as a function: each {@N} is filled from the call's
arguments (any printable value), and {name} is ordinary interpolation, read when the template
is called. expand_templates() runs first in semantic analysis and rewrites:

    greet("Ann", 30)       CallExpr       -> format(<the text>, "Ann", 30)
    welcome(greet)         a template passed where a function type is written (a parameter
    (string, int) -> string f = greet     or a variable) -> a lambda that calls format

so the rest of the compiler only sees format() calls and lambdas. A template declared inside
a function is expanded where it is called, so {name} can be one of that function's variables;
passing such a template on would need a closure (not built yet) and is an error. A template
declared outside any function may only use module variables and constants.
"""

from copy import deepcopy
from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Dict, List, Optional, Set, Tuple

from src.parser.ast_nodes import (
    ASTNode, CallExpr, FunctionDecl, FunctionType, IdentifierExpr, InterpolatedStringExpr,
    LambdaExpr, LiteralExpr, MemberExpr, NamedArgument, ParameterDecl, PrimitiveType, ProgramNode,
    StringExprPart, StringPositionalPart, TemplateDecl, VarDeclStmt,
)
from .errors import SemanticError

_SKIP_FIELDS = ('location', 'inferred_type', 'declaration', 'callee_declaration', 'scope',
                'resolved_arguments')


class _Template:
    """One declared template: its text, how many values it takes and the names it reads."""

    def __init__(self, decl: TemplateDecl, module_level: bool):
        self.decl = decl
        self.module_level = module_level
        self.used = False
        self.broken = False     # its text has an error (reported once): uses become ""
        parts = decl.text.segments if isinstance(decl.text, InterpolatedStringExpr) else []
        self.indexes = sorted({p.index for p in parts if isinstance(p, StringPositionalPart)})
        self.count = self.indexes[-1] if self.indexes else 0
        self.names = [_root_name(p.expression) for p in parts if isinstance(p, StringExprPart)]


def _root_name(expr) -> Optional[str]:
    """`shop` for {shop}, `p` for {p.name}."""
    while isinstance(expr, MemberExpr):
        expr = expr.object
    return expr.name if isinstance(expr, IdentifierExpr) else None


def expand_templates(program: ProgramNode) -> Tuple[List[SemanticError], List[SemanticError], Set[str]]:
    """Expand every template use (see the module docstring). Returns (errors, warnings, the
    positions of the templates' texts - an error there repeats once per call)."""
    if not _has_template(program):
        return [], [], set()
    spots: Set[str] = set()
    errors: List[SemanticError] = []
    warnings: List[SemanticError] = []
    functions: Dict[str, FunctionDecl] = {d.name: d for d in program.declarations
                                          if isinstance(d, FunctionDecl)}
    module_names: Set[str] = {d.name for d in program.declarations if isinstance(d, VarDeclStmt)}
    reported: Set[int] = set()      # template names already reported, not reported twice

    def declare(decl: TemplateDecl, scopes: List[Dict[str, _Template]], module_level: bool):
        if decl.name in functions or decl.name in module_names \
                or any(decl.name in scope for scope in scopes):
            errors.append(SemanticError(
                f"'{decl.name}' is already used - choose another name for the template",
                decl.location))
            return
        if decl.name == 'format' or 'format' in functions:
            errors.append(SemanticError(
                "Templates fill their text with the built-in format() - a program that "
                "defines its own format() can't use templates", decl.location))
            return
        template = _Template(decl, module_level)
        spots.add(str(decl.text.location))
        missing = [n for n in range(1, template.count + 1) if n not in template.indexes]
        if missing:
            template.broken = True
            errors.append(SemanticError(
                f"Template '{decl.name}' has {{@{template.count}}} but no "
                f"{{@{missing[0]}}} - number the values from 1 without gaps", decl.location))
        if module_level:
            for name in template.names:
                if name not in module_names:
                    template.broken = True
                    errors.append(SemanticError(
                        f"Template '{decl.name}' uses '{{{name}}}' - a template outside any "
                        f"function can only use module variables and constants",
                        decl.location))
        scopes[-1][decl.name] = template

    def find(name: str, scopes) -> Optional[_Template]:
        for scope in reversed(scopes):
            if name in scope:
                return scope[name]
        return None

    def template_named(node, scopes) -> Optional[_Template]:
        return find(node.name, scopes) if isinstance(node, IdentifierExpr) else None

    def filled(template: _Template, values: List[ASTNode], location) -> ASTNode:
        template.used = True
        if template.broken or len(values) != template.count:
            # Already reported - an empty string, so nothing repeats the error
            return LiteralExpr(location=location, value='', type_hint='string')
        return CallExpr(location=location, callee=IdentifierExpr(location=location, name='format'),
                        arguments=[deepcopy(template.decl.text)] + values)

    def as_function(template: _Template, wanted, location) -> Optional[ASTNode]:
        """A template where a function type is written: a lambda that fills it (4b)."""
        name = template.decl.name
        if id(location) in reported:
            return None
        reported.add(id(location))
        if not isinstance(wanted, FunctionType):
            errors.append(SemanticError(
                f"Template '{name}' is used by calling it - {name}(...) - or passed where a "
                f"function type is written, e.g. a parameter (string) -> string", location))
            return None
        if not (isinstance(wanted.return_type, PrimitiveType) and wanted.return_type.name == 'string') \
                or len(wanted.parameter_types) != template.count:
            errors.append(SemanticError(
                f"Template '{name}' takes {template.count} value(s) and gives a string - it "
                f"doesn't fit this function type", location))
            return None
        local = [n for n in template.names if n not in module_names]
        if not template.module_level and local:
            errors.append(SemanticError(
                f"Template '{name}' uses '{{{local[0]}}}' from this function, so it can only be "
                f"called here - passing it on needs closures (not built yet)", location))
            return None
        params = [ParameterDecl(location=location, param_type=deepcopy(t),
                                name=f'template_value_{i + 1}', default_value=None)
                  for i, t in enumerate(wanted.parameter_types)]
        values = [IdentifierExpr(location=location, name=p.name) for p in params]
        return LambdaExpr(location=location, parameters=params, return_type=None,
                          body=filled(template, values, location))

    def convert(node, scopes) -> Optional[ASTNode]:
        if isinstance(node, CallExpr):
            template = template_named(node.callee, scopes)
            if template is not None:
                name = template.decl.name
                if any(isinstance(a, NamedArgument) for a in node.arguments):
                    errors.append(SemanticError(
                        f"Template '{name}' takes its values in order - {{@1}}, {{@2}}, ... - "
                        f"not by name", node.location))
                elif len(node.arguments) != template.count:
                    places = ', '.join(f'{{@{n}}}' for n in range(1, template.count + 1))
                    errors.append(SemanticError(
                        f"Template '{name}' takes {template.count} value(s)"
                        f"{' (' + places + ')' if places else ''}, got {len(node.arguments)}",
                        node.location))
                return filled(template, node.arguments, node.location)
            # A template passed to a parameter of function type: welcome(greet)
            callee = functions.get(node.callee.name) if isinstance(node.callee, IdentifierExpr) else None
            if callee is not None:
                for i, argument in enumerate(node.arguments):
                    value = argument.value if isinstance(argument, NamedArgument) else argument
                    template = template_named(value, scopes)
                    if template is None:
                        continue
                    if isinstance(argument, NamedArgument):
                        param = next((p for p in callee.parameters if p.name == argument.name), None)
                    else:
                        param = callee.parameters[i] if i < len(callee.parameters) else None
                    if param is None:
                        continue      # the type checker reports the wrong argument
                    lam = as_function(template, param.param_type, value.location)
                    if lam is not None:
                        if isinstance(argument, NamedArgument):
                            argument.value = lam
                        else:
                            node.arguments[i] = lam
        if isinstance(node, VarDeclStmt):
            if find(node.name, scopes) is not None:
                errors.append(SemanticError(
                    f"'{node.name}' is already a template - choose another name for the "
                    f"variable", node.location))
            template = template_named(node.initializer, scopes)
            if template is not None:
                lam = as_function(template, node.var_type, node.initializer.location)
                if lam is not None:
                    node.initializer = lam
        template = template_named(node, scopes)
        if template is not None:
            as_function(template, None, node.location)      # any other use: an error
        return None

    def walk(node, scopes) -> None:
        if isinstance(node, list):
            # A list of statements is a block: a template declared in it is seen by what
            # follows it in the block
            scopes.append({})
            kept = []
            for item in node:
                if isinstance(item, TemplateDecl):
                    declare(item, scopes, module_level=False)
                    continue
                new = convert(item, scopes)
                kept.append(new if new is not None else item)
                walk(kept[-1], scopes)
            node[:] = kept
            unused(scopes.pop())
            return
        if not is_dataclass(node) or isinstance(node, type):
            return
        for f in dataclass_fields(node):
            if f.name in _SKIP_FIELDS:
                continue
            value = getattr(node, f.name)
            if isinstance(value, list):
                walk(value, scopes)
                continue
            new = convert(value, scopes)
            if new is not None:
                setattr(node, f.name, new)
                value = new
            walk(value, scopes)

    def unused(scope: Dict[str, _Template]) -> None:
        for template in scope.values():
            if not template.used:
                warnings.append(SemanticError(
                    f"Template '{template.decl.name}' is never used", template.decl.location))

    module_scope: Dict[str, _Template] = {}
    for decl in program.declarations:
        if isinstance(decl, TemplateDecl):
            declare(decl, [module_scope], module_level=True)
    program.declarations[:] = [d for d in program.declarations if not isinstance(d, TemplateDecl)]
    for decl in program.declarations:
        walk(decl, [module_scope])
    unused(module_scope)
    return errors, warnings, spots


def _has_template(node) -> bool:
    """Whether the program declares any template - most don't, and then nothing changes."""
    if isinstance(node, TemplateDecl):
        return True
    if isinstance(node, list):
        return any(_has_template(item) for item in node)
    if not is_dataclass(node) or isinstance(node, type):
        return False
    return any(_has_template(getattr(node, f.name)) for f in dataclass_fields(node)
               if f.name not in _SKIP_FIELDS)
