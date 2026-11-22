"""Generic functions of the program's own (Task 33.2a, D.166, D.168).

    T function first<T>(List<T> items) : items[0]
    T function last(List<T> items) : items[items.len() - 1]    // T, K, V in a signature: type parameters
    V function valueOf<K, V>(Map<K, V> m, K key) : m[key]

    int a = first(numbers)            // the types from the arguments (preferred)
    int b = first<int>(numbers)       // or written

One copy per set of types used (as C++ templates and Rust): before names are resolved, a generic
function is taken out of the program and its name registered as a generic function
(`take_generic_functions`); at each call the type checker works out the types, and makes the copy -
`first__int`, the function with T replaced by int - once per set of types, registered and added to the
program, so it is checked and turned into C like any other function (`GenericsMixin.generic_call`).

`[generics] enabled = false`: a generic declaration is an error (the built-in List<T> / Map<K, V> stay).
"""
import copy
import re
from dataclasses import fields, is_dataclass
from typing import List

from src.parser.ast_nodes import (ArrayType, EnumDecl, FunctionDecl, FunctionType, IdentifierExpr, ListType,
                                  MapType, PrimitiveType, StructDecl, StructType, TypeNode)

from .errors import SemanticError

TYPE_PARAMETER = re.compile(r'^[TKV]\d*$')       # T, K, V, T1, K2 ... (D.166)


def _type_names(type_node, found: list) -> None:
    """The names of the types written in a type, in order - StructType names, inside List<...> too."""
    if isinstance(type_node, StructType):
        if type_node.name not in found:
            found.append(type_node.name)
        for arg in getattr(type_node, 'type_args', None) or []:
            _type_names(arg, found)
    elif isinstance(type_node, (ArrayType, ListType)):
        _type_names(type_node.element_type, found)
    elif isinstance(type_node, MapType):
        _type_names(type_node.key_type, found)
        _type_names(type_node.value_type, found)
    elif isinstance(type_node, FunctionType):
        for p in type_node.parameter_types:
            _type_names(p, found)
        _type_names(type_node.return_type, found)


def type_parameters(function: FunctionDecl) -> list:
    """A function's type parameters: written in <...>, or T, K, V (and digits) in its signature."""
    if function.type_params:
        return list(function.type_params)
    found: List[str] = []
    _type_names(function.return_type, found)
    for param in function.parameters:
        _type_names(param.param_type, found)
    return [name for name in found if TYPE_PARAMETER.match(name)]


def take_generic_functions(program, enabled: bool) -> List[SemanticError]:
    """Take each generic function out of the program, into `program.generic_functions` - its copies
    are made when it is used. Also: a struct, class or enum may not be named T, K or V (D.166)."""
    errors: List[SemanticError] = []
    program.generic_functions = {}
    kept = []
    for decl in program.declarations:
        if isinstance(decl, (StructDecl, EnumDecl)) and TYPE_PARAMETER.match(decl.name):
            what = 'an enum' if isinstance(decl, EnumDecl) else 'a class' if getattr(decl, 'is_class', False) \
                else 'a struct'
            errors.append(SemanticError(
                f"'{decl.name}' can't name {what} - T, K and V (and T1, K2 ...) name a generic's type "
                f"parameters (D.166); call it {decl.name}Item or a name of its own", decl.location))
        if isinstance(decl, FunctionDecl):
            params = type_parameters(decl)
            if params:
                if not enabled:
                    errors.append(SemanticError(
                        f"'{decl.name}' is generic ({', '.join(params)}) - generics are off in this project "
                        f"([generics] enabled = false, D.168)", decl.location))
                elif decl.name in program.generic_functions:
                    errors.append(SemanticError(f"Generic function '{decl.name}' is declared twice",
                                                decl.location))
                decl.type_params = params
                decl.instances = {}
                program.generic_functions.setdefault(decl.name, decl)
                continue
        kept.append(decl)
    program.declarations[:] = kept
    return errors


def _replace_types(node, bindings: dict, memo: dict):
    """Every type parameter in a copied function replaced by its type - in signatures, locals, casts,
    loops, inside List<...> / Map<...> / T[] too. Returns the node (a type may be replaced whole)."""
    if isinstance(node, StructType) and node.name in bindings:
        return copy.deepcopy(bindings[node.name], memo)
    if isinstance(node, list):
        for i, item in enumerate(node):
            node[i] = _replace_types(item, bindings, memo)
        return node
    if not is_dataclass(node) or isinstance(node, type):
        return node
    for f in fields(node):
        if f.name in ('location', 'declaration', 'callee_declaration', 'scope'):
            continue
        value = getattr(node, f.name)
        if isinstance(value, list) or (is_dataclass(value) and not isinstance(value, type)):
            setattr(node, f.name, _replace_types(value, bindings, memo))
    for name in ('type_args',):                      # Collection<T> written in the copy (32.4)
        if getattr(node, name, None):
            setattr(node, name, _replace_types(getattr(node, name), bindings, memo))
    return node


def _c_part(text: str) -> str:
    """A type as part of a C name: List<int> -> List_int, int[] -> int_arr."""
    return re.sub(r'_+', '_', re.sub(r'\W', '_', text.replace('[]', '_arr'))).strip('_')


class GenericsMixin:
    """Calls to generic functions - a mixin of the type checker. Set by the analyzer: `program`, and
    `generic_host` (the analyzer - it registers a copy's name)."""

    def generic_call(self, node, generic: FunctionDecl):
        """`first(numbers)` / `first<int>(numbers)`: the types worked out, the copy made (once per set of
        types), and the call checked as a call of that copy."""
        void = PrimitiveType(location=node.location, name='void')
        params = generic.type_params
        if any(type(a).__name__ == 'NamedArgument' for a in node.arguments):
            self.errors.append(SemanticError(
                f"Named arguments to a generic function ('{generic.name}') come later - give them in order",
                node.location))
            return void
        bindings = {}
        written = getattr(node, 'type_args', None)
        if written is not None:
            if len(written) != len(params):
                self.errors.append(SemanticError(
                    f"'{generic.name}' has {len(params)} type parameter(s) ({', '.join(params)}) - "
                    f"{len(written)} written", node.location))
                return void
            for name, kind in zip(params, written):
                self.generic_host.name_resolver.resolve_type(kind)
                bindings[name] = kind
        else:
            before = len(self.errors)
            actual = [self.visit(arg) for arg in node.arguments]
            for arg in node.arguments:
                self.checked_receivers.pop(id(arg), None)
            if len(self.errors) > before:
                return void                                  # an argument is wrong - said already
            for param, kind in zip(generic.parameters, actual):
                self._bind(param.param_type, kind, bindings, params)
            missing = [p for p in params if p not in bindings]
            if missing:
                example = ', '.join('int' for _ in params)
                self.errors.append(SemanticError(
                    f"'{generic.name}': {', '.join(missing)} can't be worked out from the arguments - write the "
                    f"types: {generic.name}<{example}>(...) (D.166)", node.location))
                return void
        instance = self._generic_instance(generic, [bindings[p] for p in params], bindings)
        node.callee = IdentifierExpr(location=node.callee.location, name=instance.name)
        node.generic_of = generic.name
        return self._visit_call(node)

    def _bind(self, expected, actual, bindings: dict, params) -> None:
        """Match a parameter's type against an argument's: each type parameter found gets the type in
        the same place (the first one found wins - a later different one is the call's own error)."""
        if actual is None:
            return
        if isinstance(expected, StructType) and expected.name in params:
            bindings.setdefault(expected.name, actual)
            return
        if isinstance(expected, ArrayType) and isinstance(actual, (ArrayType, ListType)):
            self._bind(expected.element_type, actual.element_type, bindings, params)
        elif isinstance(expected, ListType) and isinstance(actual, ListType):
            self._bind(expected.element_type, actual.element_type, bindings, params)
        elif isinstance(expected, MapType) and isinstance(actual, MapType):
            self._bind(expected.key_type, actual.key_type, bindings, params)
            self._bind(expected.value_type, actual.value_type, bindings, params)

    def _generic_instance(self, generic: FunctionDecl, kinds: list, bindings: dict) -> FunctionDecl:
        """The copy of a generic function for these types - made once, registered, added to the program
        (the analyzer's function loop checks it; the generator writes it like any other)."""
        key = tuple(self.type_to_string(k) for k in kinds)
        made = generic.instances.get(key)
        if made is not None:
            return made
        memo = {id(d): d for d in self.program.declarations}      # other declarations stay shared
        instance = copy.deepcopy(generic, memo)
        instance.type_params = None
        instance.instances = None
        _replace_types(instance, {name: k for name, k in bindings.items()}, memo)
        instance.name = f"{generic.name}__{'__'.join(_c_part(k) for k in key)}"
        instance.generic_of = generic.name
        instance.generic_types = key
        generic.instances[key] = instance
        self.program.declarations.append(instance)
        self.generic_host.register_generic_instance(instance)
        return instance
