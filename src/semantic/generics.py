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

from src.parser.ast_nodes import (ArrayLiteralExpr, ArrayType, CallExpr, EnumDecl, FunctionDecl, FunctionType,
                                  IdentifierExpr, ListType, MapType, MemberExpr, PrimitiveType, StructDecl,
                                  StructType, TypeNode)

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
    program.generic_structs = {}
    kept = []
    members = set()           # a generic class's methods - they go with it (33.2c)
    for decl in program.declarations:
        if id(decl) in members:
            continue
        if isinstance(decl, StructDecl) and getattr(decl, 'type_params', None):
            # struct Pair<A, B> (Task 33.2b): a copy per set of types, made when a type or a call needs it
            if not enabled:
                errors.append(SemanticError(
                    f"'{decl.name}' is generic ({', '.join(decl.type_params)}) - generics are off in this project "
                    f"([generics] enabled = false, D.168)", decl.location))
            # class Box<T> (33.2c): its methods and constructors are copied with it - taken out here
            later = [what for what, there in (('a parent', getattr(decl, 'class_parent', None) or decl.parent),
                                              ('interfaces', getattr(decl, 'interfaces', None)),
                                              ('static members', getattr(decl, 'static_fields', None)
                                               or getattr(decl, 'static_methods', None)
                                               or getattr(decl, 'static_block', None))) if there]
            if later:
                errors.append(SemanticError(
                    f"A generic {'class' if decl.is_class else 'struct'} ('{decl.name}') with {later[0]} comes "
                    f"later (Task 33.3) - only fields, methods and constructors for now", decl.location))
            members.update(id(m) for m in decl.methods + getattr(decl, 'static_methods', []))
            decl.instances = {}
            program.generic_structs[decl.name] = decl
            continue
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


def variadic_parameters(program) -> List[SemanticError]:
    """`int... numbers` / `T... items` (33.2e, SYN.034): the last parameter only; inside the function it
    is a List (main's `string... args` stays an array). At the call `pack_variadic` gathers the values."""
    errors: List[SemanticError] = []
    for decl in program.declarations:
        if not isinstance(decl, FunctionDecl):
            continue
        for n, param in enumerate(decl.parameters):
            if not getattr(param, 'is_variadic', False):
                continue
            if n != len(decl.parameters) - 1:
                errors.append(SemanticError(
                    f"'{param.name}...' takes the values left over - it must be the last parameter of "
                    f"'{decl.name}'", param.location))
            elif param.default_value is not None:
                errors.append(SemanticError(
                    f"'{param.name}...' has no default - no values given is an empty List", param.location))
            elif decl.name != 'main' and isinstance(param.param_type, ArrayType):
                param.param_type = ListType(location=param.param_type.location,
                                            element_type=param.param_type.element_type)
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


def struct_instance(program, generic: StructDecl, kinds: list, key: tuple, register) -> StructDecl:
    """The copy of a generic struct for these types (Task 33.2b) - made once: its fields' types
    replaced, named `Pair__int__string`, added to the program and registered (`register`)."""
    made = generic.instances.get(key)
    if made is not None:
        return made
    memo = {id(d): d for d in program.declarations}
    instance = copy.deepcopy(generic, memo)
    instance.type_params = None
    instance.instances = None
    _replace_types(instance, dict(zip(generic.type_params, kinds)), memo)
    instance.name = f"{generic.name}__{'__'.join(_c_part(k) for k in key)}"
    instance.generic_of = generic.name
    instance.generic_types = key
    instance.generic_kinds = kinds
    members = instance.methods + list(getattr(instance, 'static_methods', None) or [])
    _rename_own(members, generic.name, instance.name)   # Box inside its own methods: this copy (33.2c)
    generic.instances[key] = instance
    # at the end: the function loop is walking the list (C puts structs in their own order)
    program.declarations.append(instance)
    program.declarations.extend(members)
    register(instance)
    return instance


def _rename_own(node, old: str, new: str, seen=None) -> None:
    """Inside a generic class's copied methods, its own name means the copy: the `this` parameter, a
    constructor's result and object, `this(...)`, the method names `Box.get` -> `Box__int.get`."""
    seen = set() if seen is None else seen
    if id(node) in seen:
        return
    seen.add(id(node))
    if isinstance(node, list):
        for item in node:
            _rename_own(item, old, new, seen)
        return
    if not is_dataclass(node) or isinstance(node, type):
        return
    if isinstance(node, StructType) and node.name == old and not getattr(node, 'type_args', None):
        node.name = new
    elif isinstance(node, IdentifierExpr) and node.name == old:
        node.name = new
    elif isinstance(node, FunctionDecl):
        if node.name.startswith(old + '.'):
            node.name = new + node.name[len(old):]
        if getattr(node, 'method_of', None) == old:
            node.method_of = new
        if getattr(node, 'delegate', None) is not None:
            _rename_own(node.delegate, old, new, seen)
    for f in fields(node):
        if f.name in ('location', 'declaration', 'callee_declaration', 'scope', 'inferred_type'):
            continue
        value = getattr(node, f.name)
        if isinstance(value, list) or (is_dataclass(value) and not isinstance(value, type)):
            _rename_own(value, old, new, seen)


_SKIP = ('location', 'declaration', 'callee_declaration', 'scope', 'inferred_type')
_COUNT = ('len', 'length', 'count', 'size')


def _children(node):
    """(field name, value) of each child worth walking in an AST node."""
    for f in fields(node):
        if f.name not in _SKIP:
            value = getattr(node, f.name)
            if isinstance(value, list) or (is_dataclass(value) and not isinstance(value, type)):
                yield f.name, value


def _mentions_type(node, name: str) -> bool:
    """Whether a type (or any node) names the type parameter `name`."""
    if isinstance(node, StructType) and node.name == name:
        return True
    if isinstance(node, list):
        return any(_mentions_type(item, name) for item in node)
    if not is_dataclass(node) or isinstance(node, type):
        return False
    return any(_mentions_type(value, name) for _, value in _children(node))


def _rename_variable(node, old: str, new: str) -> None:
    """Every use of the loop variable `old` becomes the value's parameter `new`."""
    if isinstance(node, list):
        for item in node:
            _rename_variable(item, old, new)
        return
    if not is_dataclass(node) or isinstance(node, type):
        return
    if isinstance(node, IdentifierExpr) and node.name == old:
        node.name = new
    for _, value in _children(node):
        _rename_variable(value, old, new)


def _leaves_loop(node) -> bool:
    """A break or continue of this loop itself (not of a loop inside it)."""
    from src.parser.ast_nodes import BreakStmt, ContinueStmt, WhileStmt
    if isinstance(node, (BreakStmt, ContinueStmt)):
        return True
    if isinstance(node, list):
        return any(_leaves_loop(item) for item in node)
    if not is_dataclass(node) or isinstance(node, (type, WhileStmt)) or type(node).__name__ == 'ForStmt':
        return False
    return any(_leaves_loop(value) for _, value in _children(node))


def _unroll_pack(body, pack: str, pack_type: str, kinds: list, program, problems: list):
    """A pack's function body for these types (33.2e2) - see `GenericsMixin._pack_instance`."""
    from src.parser.ast_nodes import BlockStmt, ForStmt, LiteralExpr

    def is_pack(node):
        return isinstance(node, IdentifierExpr) and node.name == pack

    def count(location):
        return LiteralExpr(location=location, value=len(kinds), type_hint='int')

    def walk(node):
        if isinstance(node, list):
            return [walk(item) for item in node]
        if not is_dataclass(node) or isinstance(node, type):
            return node
        if isinstance(node, ForStmt) and is_pack(node.iterable):
            declared = getattr(node, 'declared_type', None)
            if declared is not None and not (isinstance(declared, StructType) and declared.name == pack_type):
                problems.append(f"'foreach' over '{pack}' names its item {pack_type}, or no type - each value "
                                f"is of its own type")
            if _leaves_loop(node.body):
                problems.append(f"break / continue in a loop over '{pack}' comes later - each value's code is "
                                f"written out in turn")
            turns = []
            for n, kind in enumerate(kinds):           # the body once per value, with that value's type
                turn = copy.deepcopy(node.body, {id(d): d for d in program.declarations})
                turn = _replace_types(turn, {pack_type: kind}, {id(d): d for d in program.declarations})
                _rename_variable(turn, node.variable, f'{pack}__{n}')
                turn = walk(turn)
                if isinstance(turn, BlockStmt):
                    turn.braced = True                  # a C scope of its own - names repeat per turn
                turns.append(turn)
            return BlockStmt(location=node.location, statements=turns)
        if isinstance(node, CallExpr) and not node.arguments and isinstance(node.callee, MemberExpr) \
                and is_pack(node.callee.object) and node.callee.member in _COUNT:
            return count(node.location)                 # items.len()
        if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                and node.callee.name in _COUNT and len(node.arguments) == 1 and is_pack(node.arguments[0]):
            return count(node.location)                 # len(items)
        if isinstance(node, MemberExpr) and is_pack(node.object) and node.member in _COUNT:
            return count(node.location)                 # items.length
        if type(node).__name__ == 'IndexExpr' and is_pack(node.array):
            index = node.index
            if isinstance(index, LiteralExpr) and index.type_hint == 'int' and 0 <= index.value < len(kinds):
                return IdentifierExpr(location=node.location, name=f'{pack}__{index.value}')
            problems.append(f"'{pack}[...]' takes a number written in the code, 0 to {len(kinds) - 1} - each "
                            f"value is of its own type")
            return node
        if is_pack(node):
            problems.append(f"'{pack}' can be looped (for x in {pack}), counted ({pack}.len()) or read by a "
                            f"written number ({pack}[0]) - not passed or kept whole")
            return node
        if isinstance(node, StructType) and node.name == pack_type:
            problems.append(f"{pack_type} is used outside 'for x in {pack}' - there it has no one type")
            return node
        for name, value in _children(node):
            setattr(node, name, walk(value))
        return node

    return walk(body)


def _c_part(text: str) -> str:
    """A type as part of a C name: List<int> -> List_int, int[] -> int_arr."""
    return re.sub(r'_+', '_', re.sub(r'\W', '_', text.replace('[]', '_arr'))).strip('_')


NUMBER_TYPES = ('byte', 'short', 'int', 'long', 'float', 'double')


def _condition_text(name: str, condition) -> str:
    """<T extends Vehicle implements Comparable> as written - for a message."""
    extends, interfaces = condition
    text = name
    if extends is not None:
        text += f" extends {getattr(extends, 'name', extends)}"
    if interfaces:
        text += f" implements {', '.join(interfaces)}"
    return f'<{text}>'


def check_condition_declarations(program) -> List[SemanticError]:
    """Each condition names something that exists (33.2d, D.167): `extends` a class or struct of the
    program, `Number` or a basic type; `implements` an interface."""
    errors: List[SemanticError] = []
    declared = {d.name: d for d in program.declarations if isinstance(d, (StructDecl, EnumDecl))}
    declared.update(getattr(program, 'generic_structs', {}))
    generics = list(getattr(program, 'generic_functions', {}).values()) + \
        list(getattr(program, 'generic_structs', {}).values())
    for generic in generics:
        for name, (extends, interfaces) in (getattr(generic, 'type_conditions', None) or {}).items():
            where = _condition_text(name, (extends, interfaces))
            if isinstance(extends, StructType) and extends.name != 'Number':
                target = declared.get(extends.name)
                if target is None:
                    errors.append(SemanticError(f"'{generic.name}' {where}: no class or struct '{extends.name}'",
                                                generic.location))
                elif getattr(target, 'is_interface', False):
                    errors.append(SemanticError(
                        f"'{generic.name}' {where}: '{extends.name}' is an interface - write "
                        f"<{name} implements {extends.name}>", generic.location))
                elif isinstance(target, EnumDecl):
                    errors.append(SemanticError(
                        f"'{generic.name}' {where}: '{extends.name}' is an enum - nothing extends it; write the "
                        f"enum type itself", generic.location))
            elif extends is not None and not isinstance(extends, (StructType, PrimitiveType)):
                errors.append(SemanticError(
                    f"'{generic.name}' {where}: extends takes a class, a struct, Number or a basic type",
                    generic.location))
            for interface in interfaces:
                target = declared.get(interface)
                if not getattr(target, 'is_interface', False):
                    errors.append(SemanticError(
                        f"'{generic.name}' {where}: '{interface}' is not an interface"
                        + (f" - write <{name} extends {interface}>" if target is not None else ''),
                        generic.location))
    return errors


class GenericsMixin:
    """Calls to generic functions - a mixin of the type checker. Set by the analyzer: `program`, and
    `generic_host` (the analyzer - it registers a copy's name)."""

    def pack_variadic(self, node, decl):
        """A call of `f(int... numbers)` (33.2e): the values after the fixed parameters become one List -
        written one by one (`f(1, 2, 3)`, or none - an empty List), or one array (`.toList()`) or List
        (as it is). Returns ('list', element type) or ('values', [each value's type]); None when the
        function takes no `...` or the call was packed already."""
        params = decl.parameters
        if not params or not getattr(params[-1], 'is_variadic', False) or decl.name == 'main' \
                or getattr(node, 'variadic_packed', False):
            return None
        fixed = len(params) - 1
        if len(node.arguments) < fixed or any(type(a).__name__ == 'NamedArgument' for a in node.arguments):
            return None                                  # the usual count / name errors say what is wrong
        node.variadic_packed = True
        extra = node.arguments[fixed:]
        if len(extra) == 1:
            kind = self.visit(extra[0])
            self.checked_receivers.pop(id(extra[0]), None)
            if isinstance(kind, ListType) and not kind.array_form:
                return 'list', kind.element_type        # a List - passed as it is
            if isinstance(kind, (ArrayType, ListType)):
                node.arguments[fixed] = CallExpr(       # an array - its values as a List
                    location=extra[0].location, arguments=[],
                    callee=MemberExpr(location=extra[0].location, object=extra[0], member='toList'))
                return 'list', kind.element_type
        kinds = []
        for value in extra:
            kinds.append(self.visit(value))
            self.checked_receivers.pop(id(value), None)
        location = extra[0].location if extra else node.location
        values = ArrayLiteralExpr(location=location, elements=list(extra))
        values.variadic_values = True          # the values are lent to the call, not moved (ownership)
        node.arguments = node.arguments[:fixed] + [values]
        return 'values', kinds

    def generic_call(self, node, generic: FunctionDecl):
        """`first(numbers)` / `first<int>(numbers)`: the types worked out, the copy made (once per set of
        types), and the call checked as a call of that copy."""
        void = PrimitiveType(location=node.location, name='void')
        params = generic.type_params
        if isinstance(generic, StructDecl) and self._generic_parameters(generic, node) is None \
                and getattr(node, 'type_args', None) is None:
            what = 'a constructor taking ' if generic.is_class else 'a value for each field '
            sizes = sorted({len(m.parameters) for m in generic.methods if getattr(m, 'is_constructor', False)}) \
                if generic.is_class else [len(generic.fields)]
            self.errors.append(SemanticError(
                f"'{generic.name}' is generic - give {what}({' or '.join(map(str, sizes))}) so its types can "
                f"be worked out, or write them: {generic.name}<{', '.join('int' for _ in params)}>(...)",
                node.location))
            return void
        if any(type(a).__name__ == 'NamedArgument' for a in node.arguments):
            self.errors.append(SemanticError(
                f"Named arguments to a generic function ('{generic.name}') come later - give them in order",
                node.location))
            return void
        bindings = {}
        packed = self.pack_variadic(node, generic) if isinstance(generic, FunctionDecl) else None
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
            fixed_args = node.arguments[:-1] if packed else node.arguments
            actual = [self.visit(arg) for arg in fixed_args]
            for arg in fixed_args:
                self.checked_receivers.pop(id(arg), None)
            if len(self.errors) > before:
                return void                                  # an argument is wrong - said already
            for (_, expected), kind in zip(self._generic_parameters(generic, node), actual):
                self._bind(expected, kind, bindings, params)
            if packed:
                result = self._bind_variadic(generic, packed, bindings, params, node)
                if result is False:
                    return void
                if result == 'pack':
                    return self._call_pack(node, generic, bindings, params, packed[1])
            missing = [p for p in params if p not in bindings]
            if missing:
                # stored in a variable of this type (Box<Car> b = Box()): the hint names it, and the call is
                # taken as that type - no second error about assigning (33.4)
                stored = getattr(node, 'stored_as', None)
                shown = self.type_to_string(stored) if stored is not None else ''
                if shown.startswith(f'{generic.name}<'):
                    written = shown
                else:
                    stored = None
                    written = f"{generic.name}<{', '.join('int' for _ in params)}>"
                self.errors.append(SemanticError(
                    f"'{generic.name}': {', '.join(missing)} can't be worked out from the arguments - write the "
                    f"types: {written}(...) (D.166)", node.location))
                return stored or void
        unmet = self.unmet_condition(generic, bindings)
        if unmet:
            self.errors.append(SemanticError(unmet, node.location))
            return void
        if isinstance(generic, StructDecl):
            instance = self.generic_host.struct_instance(generic, [bindings[p] for p in params])
        else:
            instance = self._generic_instance(generic, [bindings[p] for p in params], bindings)
        node.callee = IdentifierExpr(location=node.callee.location, name=instance.name)
        node.generic_of = generic.name
        return self._visit_call(node)

    def _bind_variadic(self, generic, packed, bindings: dict, params, node) -> bool:
        """`T... items` (33.2e): T from one List / array (its element), or from the values written - all
        of one type; of several types that all meet `extends Vehicle`, T is Vehicle. False (said why) when
        the values' types differ otherwise - a pack of types comes with the next step."""
        expected = generic.parameters[-1].param_type.element_type
        how, kinds = packed
        if how == 'list':
            self._bind(expected, kinds, bindings, params)
            return True
        if not kinds:
            return True                       # no values - T from elsewhere, or "write the types"
        shown = [self.type_to_string(k) for k in kinds]
        if len(set(shown)) == 1:
            self._bind(expected, kinds[0], bindings, params)
            return True
        name = getattr(expected, 'name', None)
        extends = ((getattr(generic, 'type_conditions', None) or {}).get(name) or (None, []))[0] \
            if isinstance(expected, StructType) and name in params else None
        if isinstance(extends, StructType) and extends.name != 'Number' and name not in bindings:
            parent = StructType(location=extends.location, name=extends.name,
                                declaration=self.struct_declaration(extends))
            bindings[name] = parent           # each value checked against it with the call
            return True
        conditions = (getattr(generic, 'type_conditions', None) or {}).get(name)
        if isinstance(expected, StructType) and name in params and name not in bindings and not conditions:
            return 'pack'                     # values of any type each (33.2e2)
        if conditions:
            why = f"each must meet {_condition_text(name, conditions)}"
        elif name in bindings:
            why = f"{name} is {self.type_to_string(bindings[name])} already, from an earlier argument"
        else:
            why = "give values of one type"
        self.errors.append(SemanticError(
            f"'{generic.name}': the values for '{generic.parameters[-1].name}...' are of different types "
            f"({', '.join(dict.fromkeys(shown))}) - {why}", node.location))
        return False

    def _call_pack(self, node, generic, bindings: dict, params, kinds):
        """`show(1, "two", car)` (33.2e2): a copy for this combination of types - one parameter per value -
        and the call made to it with the values as written."""
        void = PrimitiveType(location=node.location, name='void')
        pack_type = generic.parameters[-1].param_type.element_type.name
        missing = [p for p in params if p != pack_type and p not in bindings]
        if missing:
            self.errors.append(SemanticError(
                f"'{generic.name}': {', '.join(missing)} can't be worked out from the arguments - write the "
                f"types (D.166)", node.location))
            return void
        values = node.arguments[-1]
        node.arguments = node.arguments[:-1] + list(values.elements)
        instance = self._pack_instance(generic, bindings, params, pack_type, kinds, node)
        if instance is None:
            return void
        node.callee = IdentifierExpr(location=node.callee.location, name=instance.name)
        node.generic_of = generic.name
        return self._visit_call(node)

    def _pack_instance(self, generic, bindings, params, pack_type, kinds, node):
        """The copy for a pack: `items...` becomes `items__0`, `items__1` ... each of its own type; in
        the body `for x in items` is written out once per value (x that value, T its type),
        `items.len()` / `len(items)` the count, `items[1]` that value. Anything else with the pack -
        or T outside such a loop - is an error (each value is of another type)."""
        others = [p for p in params if p != pack_type]
        key = tuple(self.type_to_string(bindings[p]) for p in others) + tuple(self.type_to_string(k) for k in kinds)
        made = generic.instances.get(key)
        if made is not None:
            return made
        memo = {id(d): d for d in self.program.declarations}
        instance = copy.deepcopy(generic, memo)
        instance.type_params = None
        instance.instances = None
        _replace_types(instance, {p: bindings[p] for p in others}, memo)
        last = instance.parameters.pop()
        pack = last.name
        for n, kind in enumerate(kinds):
            one = copy.copy(last)
            one.name, one.is_variadic = f'{pack}__{n}', False
            one.param_type = copy.deepcopy(kind, {id(d): d for d in self.program.declarations})
            instance.parameters.append(one)
        problems = []
        if _mentions_type(instance.return_type, pack_type):
            problems.append(f"the result is {pack_type}, but each value is of another type - give the result a "
                            f"type of its own, or values of one type")
        instance.body = _unroll_pack(instance.body, pack, pack_type, kinds, self.program, problems)
        if problems:
            self.errors.append(SemanticError(
                f"'{generic.name}' called with values of different types ({', '.join(key[len(others):])}) - a "
                f"pack: {problems[0]}", node.location))
            return None
        instance.name = f"{generic.name}__{'__'.join(_c_part(k) for k in key)}"
        instance.generic_of = generic.name
        instance.generic_types = key
        generic.instances[key] = instance
        self.program.declarations.append(instance)
        self.generic_host.register_generic_instance(instance)
        return instance

    def unmet_condition(self, generic, bindings: dict):
        """The message for the first condition a type doesn't meet (33.2d, D.167), or None:
        `extends X` / `: X` - X or a child of it; `extends Number` - any number; `extends int` - only int;
        `implements I` - a class (or interface) that implements I."""
        for name, (extends, interfaces) in (getattr(generic, 'type_conditions', None) or {}).items():
            kind = bindings.get(name)
            if kind is None:
                continue
            shown = self.type_to_string(kind)
            where = f"'{generic.name}' {_condition_text(name, (extends, interfaces))}"
            if isinstance(extends, StructType) and extends.name == 'Number':
                if not (isinstance(kind, PrimitiveType) and kind.name in NUMBER_TYPES):
                    return f"{where}: {shown} is not a number type"
            elif isinstance(extends, PrimitiveType):
                if not (isinstance(kind, PrimitiveType) and kind.name == extends.name):
                    return f"{where}: {shown} is not {extends.name} - only {extends.name} is accepted"
            elif isinstance(extends, StructType):
                target = StructType(location=extends.location, name=extends.name,
                                    declaration=self.struct_declaration(extends))
                if not (isinstance(kind, StructType) and self.types_compatible(target, kind)):
                    return f"{where}: {shown} is not {extends.name} or a child of it"
            for interface in interfaces:
                target = StructType(location=generic.location, name=interface)
                target.declaration = self.struct_declaration(target)
                if not (isinstance(kind, StructType) and (kind.name == interface
                                                          or self.implements_interface(kind, target))):
                    return f"{where}: {shown} doesn't implement {interface}"
        return None

    def _generic_parameters(self, generic, node):
        """(name, type) pairs the arguments are matched against - a function's parameters, a struct's
        fields (its constructor takes them in order), a class's constructor taking that many (33.2c);
        None when no constructor takes that many."""
        count = len(node.arguments)
        if isinstance(generic, StructDecl) and generic.is_class:
            maker = next((m for m in generic.methods if getattr(m, 'is_constructor', False)
                          and len(m.parameters) == count), None)
            return None if maker is None else [(p.name, p.param_type) for p in maker.parameters]
        if isinstance(generic, StructDecl):
            return [(f.name, f.field_type) for f in generic.fields] if count == len(generic.fields) else None
        return [(p.name, p.param_type) for p in generic.parameters]

    def _bind(self, expected, actual, bindings: dict, params) -> None:
        """Match a parameter's type against an argument's: each type parameter found gets the type in
        the same place (the first one found wins - a later different one is the call's own error)."""
        if actual is None:
            return
        if isinstance(expected, StructType) and expected.name in params:
            bindings.setdefault(expected.name, actual)
            return
        if isinstance(expected, StructType) and getattr(expected, 'generic_base', None) \
                and isinstance(actual, StructType) \
                and getattr(actual.declaration, 'generic_of', None) == expected.generic_base:
            # Pair<T, T1> against Pair<int, string> (33.2b): each type argument in its place
            for inner, kind in zip(expected.type_args, actual.declaration.generic_kinds):
                self._bind(inner, kind, bindings, params)
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
