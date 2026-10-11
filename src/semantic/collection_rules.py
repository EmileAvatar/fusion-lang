"""Type rules for the built-in collections (Task 18.5): List<T> (18.5.1), Map<K, V> (18.5.2).

A mixin for TypeChecker. Lists are values like strings: a copy is independent, and they
are freed automatically (user decision 2026-10-11). The element type is known from the
declaration, so `[1, 2, 3]` stored as List<int> is a list literal, and `for x in xs` gives
`x` the element type.
"""

from typing import Optional

from src.parser.ast_nodes import (
    ASTNode, ArrayLiteralExpr, CallExpr, MemberExpr, IdentifierExpr, IndexExpr, LambdaExpr,
    PrimitiveType, ArrayType, FunctionType, ListType, MapType, NewCollectionExpr,
)
from .errors import SemanticError

# Methods that change the list they are called on - its variable must not be const, and a
# parameter the function changes this way gets its own copy (as with assignment)
MUTATING_LIST_METHODS = {'add', 'insert', 'removeAt', 'remove', 'clear', 'sort', 'sortBy'}
MUTATING_MAP_METHODS = {'remove', 'clear'}
MAP_KEY_TYPES = ('string', 'int', 'char')
_SORTABLE = ('int', 'float', 'double', 'byte', 'char', 'string', 'bool')


class CollectionRulesMixin:
    """List rules for the TypeChecker (Task 18.5.1)."""

    # ------------------------------------------------------------------ types and literals

    def _void(self, node) -> PrimitiveType:
        return PrimitiveType(location=node.location, name='void')

    def _check_collection_type(self, type_node, location) -> None:
        """A list holds any value type; a map's keys are string, int or char (18.5.2).
        Also: a declared type needing the heap needs the alloc layer (18.5.6)."""
        self.require_type_layer(type_node, location)
        if isinstance(type_node, MapType):
            key = type_node.key_type
            if not (isinstance(key, PrimitiveType) and key.name in MAP_KEY_TYPES):
                self.errors.append(SemanticError(
                    f"Map keys can be string, int or char, got {self.type_to_string(key)}",
                    location))
            self._check_held_type(type_node.value_type, 'A Map', location)
        elif isinstance(type_node, ListType):
            self._check_held_type(type_node.element_type, 'A List', location)

    def _check_held_type(self, element, holder: str, location) -> None:
        """What a list or a map's values can be: any value type but void, arrays and functions."""
        if isinstance(element, PrimitiveType) and element.name == 'void':
            self.errors.append(SemanticError(f"{holder} can't hold void", location))
        elif isinstance(element, (ArrayType, FunctionType)):
            self.errors.append(SemanticError(
                f"{holder} can't hold {self.type_to_string(element)} yet - use a List of "
                f"Lists, or a struct", location))
        else:
            self._check_collection_type(element, location)

    def _check_list_literal(self, node: ArrayLiteralExpr, list_type: ListType) -> ListType:
        """[1, 2, 3] stored as a List<int>: every element must fit the element type."""
        element_type = list_type.element_type
        for element in node.elements:
            actual = self._visit_value_for(element_type, element)
            if not self.types_compatible(element_type, actual):
                self.errors.append(SemanticError(
                    f"A {self.type_to_string(list_type)} element must be "
                    f"{self.type_to_string(element_type)}, got {self.type_to_string(actual)}",
                    element.location))
        node.inferred_type = list_type
        return list_type

    def visit_NewCollectionExpr(self, node: NewCollectionExpr):
        self._check_collection_type(node.collection_type, node.location)
        return node.collection_type

    # ------------------------------------------------------------------ methods

    def _collection_method_call(self, node: CallExpr) -> Optional[ASTNode]:
        """`xs.add(5)` on a List - checked here and marked for the generator
        (node.list_method). Returns the result type, or None when the receiver isn't a
        collection (then it's a built-in type's method or a struct field)."""
        receiver = node.callee.object
        if isinstance(receiver, IdentifierExpr) and self.symbol_table.lookup(receiver.name) is None:
            return None   # String.toUpper - a type class, not a value
        receiver_type = self.visit(receiver)
        self.checked_receivers[id(receiver)] = receiver_type   # checked once
        if isinstance(receiver_type, MapType):
            self.checked_receivers.pop(id(receiver), None)
            return self._map_method_call(node, receiver, receiver_type)
        if not isinstance(receiver_type, ListType):
            return None
        self.checked_receivers.pop(id(receiver), None)
        method = node.callee.member
        element = receiver_type.element_type
        node.list_method = method
        node.list_type = receiver_type
        if method in MUTATING_LIST_METHODS:
            self._check_changeable(receiver, method)
        args = node.arguments

        def want(count):
            if len(args) != count:
                self.errors.append(SemanticError(
                    f"List method '{method}' takes {count} argument(s), got {len(args)}",
                    node.location))
                return False
            return True

        def check(arg, expected, what):
            actual = self._visit_value_for(expected, arg)
            if not self.types_compatible(expected, actual):
                self.errors.append(SemanticError(
                    f"{what} of '{method}': expected {self.type_to_string(expected)}, got "
                    f"{self.type_to_string(actual)}", arg.location))
            return actual

        int_type = PrimitiveType(location=node.location, name='int')
        bool_type = PrimitiveType(location=node.location, name='bool')
        void = self._void(node)
        if method in ('add', 'contains', 'indexOf', 'remove'):
            if want(1):
                check(args[0], element, 'The value')
            return {'add': void, 'contains': bool_type, 'indexOf': int_type,
                    'remove': bool_type}[method]
        if method == 'insert':
            if want(2):
                check(args[0], int_type, 'The position')
                check(args[1], element, 'The value')
            return void
        if method == 'removeAt':
            if want(1):
                check(args[0], int_type, 'The position')
            return void
        if method in ('clear', 'len'):
            want(0)
            return void if method == 'clear' else int_type
        if method == 'join':
            # parts.join(", ") - a List<string> joined into one string (Task 18.5.3)
            if not (isinstance(element, PrimitiveType) and element.name == 'string'):
                self.errors.append(SemanticError(
                    f"join() needs a List<string>, got {self.type_to_string(receiver_type)}",
                    node.location))
            if want(1):
                check(args[0], PrimitiveType(location=node.location, name='string'), 'The separator')
            return PrimitiveType(location=node.location, name='string')
        if method == 'slice':
            if want(2):
                check(args[0], int_type, 'The start')
                check(args[1], int_type, 'The count')
            return receiver_type
        if method == 'sort':
            want(0)
            if not (isinstance(element, PrimitiveType) and element.name in _SORTABLE):
                self.errors.append(SemanticError(
                    f"sort() works on lists of numbers, chars, bools and text - use "
                    f"sortBy((a, b) : ...) for a {self.type_to_string(receiver_type)}",
                    node.location))
            return void
        if method in ('sortBy', 'filter', 'map'):
            if not want(1):
                return void
            fn = self.visit(args[0])
            if method == 'sortBy':
                expected = FunctionType(location=node.location, parameter_types=[element, element],
                                        return_type=int_type)
            elif method == 'filter':
                expected = FunctionType(location=node.location, parameter_types=[element],
                                        return_type=bool_type)
            else:
                result = fn.return_type if isinstance(fn, FunctionType) else void
                expected = FunctionType(location=node.location, parameter_types=[element],
                                        return_type=result)
            if not self.types_equal(expected, fn):
                self.errors.append(SemanticError(
                    f"'{method}' needs a function {self.type_to_string(expected)}, got "
                    f"{self.type_to_string(fn)}", args[0].location))
                return void if method == 'sortBy' else receiver_type
            if method == 'map':
                mapped = ListType(location=node.location, element_type=expected.return_type)
                self._check_collection_type(mapped, node.location)
                return mapped
            return void if method == 'sortBy' else receiver_type
        if method == 'reduce':
            if not want(2):
                return void
            start = self.visit(args[0])
            fn = self.visit(args[1])
            expected = FunctionType(location=node.location, parameter_types=[start, element],
                                    return_type=start)
            if not self.types_equal(expected, fn):
                self.errors.append(SemanticError(
                    f"'reduce' needs a function {self.type_to_string(expected)} (the running "
                    f"value, an element), got {self.type_to_string(fn)}", args[1].location))
            return start
        self.errors.append(SemanticError(
            f"{self.type_to_string(receiver_type)} has no method '{method}'", node.location))
        return void

    def _map_method_call(self, node: CallExpr, receiver, map_type: MapType):
        """`ages.has("Bob")` on a Map (Task 18.5.2)."""
        method = node.callee.member
        key, value = map_type.key_type, map_type.value_type
        node.map_method = method
        node.map_type = map_type
        if method in MUTATING_MAP_METHODS:
            self._check_changeable(receiver, method)
        args = node.arguments
        int_type = PrimitiveType(location=node.location, name='int')
        bool_type = PrimitiveType(location=node.location, name='bool')
        expected = {'has': [key], 'get': [key, value], 'remove': [key], 'keys': [],
                    'values': [], 'len': [], 'clear': []}.get(method)
        if expected is None:
            self.errors.append(SemanticError(
                f"{self.type_to_string(map_type)} has no method '{method}'", node.location))
            return self._void(node)
        if len(args) != len(expected):
            self.errors.append(SemanticError(
                f"Map method '{method}' takes {len(expected)} argument(s), got {len(args)}",
                node.location))
        for arg, want in zip(args, expected):
            actual = self._visit_value_for(want, arg)
            if not self.types_compatible(want, actual):
                self.errors.append(SemanticError(
                    f"Argument of '{method}': expected {self.type_to_string(want)}, got "
                    f"{self.type_to_string(actual)}", arg.location))
        return {'has': bool_type, 'get': value, 'remove': bool_type,
                'keys': ListType(location=node.location, element_type=key),
                'values': ListType(location=node.location, element_type=value),
                'len': int_type, 'clear': self._void(node)}[method]

    # ------------------------------------------------------------------ for ... in

    def _check_for_iterable(self, node) -> None:
        """`for x in range(...)`, `for x in xs` (a List or an array): the loop variable gets
        the element type. Anything else is an error - it used to loop 0..9 silently."""
        iterable = node.iterable
        if isinstance(iterable, CallExpr) and isinstance(iterable.callee, IdentifierExpr) \
                and iterable.callee.name == 'range':
            self.visit(iterable)
            return
        iterable_type = self.visit(iterable)
        if isinstance(iterable_type, ListType):
            element = iterable_type.element_type
        elif isinstance(iterable_type, MapType):
            element = iterable_type.key_type      # a map's keys, in the order they were added
        elif isinstance(iterable_type, ArrayType):
            element = iterable_type.element_type
        else:
            if not (isinstance(iterable_type, PrimitiveType) and iterable_type.name == 'void'):
                self.errors.append(SemanticError(
                    f"'for ... in' needs range(...), a List, a Map or an array, got "
                    f"{self.type_to_string(iterable_type)}", iterable.location))
            return
        node.element_type = element
        scope = getattr(node, 'scope', None)
        if scope is not None and node.variable in scope.symbols:
            scope.symbols[node.variable].data_type = element
