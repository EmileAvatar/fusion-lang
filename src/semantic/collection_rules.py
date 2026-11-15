"""Type rules for the built-in collections (Task 18.5): List<T> (18.5.1), Map<K, V> (18.5.2).

A mixin for TypeChecker. Lists are values like strings: a copy is independent, and they
are freed automatically (user decision 2026-10-11). The element type is known from the
declaration, so `[1, 2, 3]` stored as List<int> is a list literal, and `for x in xs` gives
`x` the element type.
"""

from typing import Optional

from src.parser.ast_nodes import (
    ASTNode, ArrayLiteralExpr, CallExpr, MemberExpr, IdentifierExpr, IndexExpr, LambdaExpr, LiteralExpr,
    PrimitiveType, ArrayType, FunctionType, ListType, MapType, NewCollectionExpr, EnumType, StructType,
    TypeNode,
)
from .errors import SemanticError

# Methods that change the list they are called on - its variable must not be const, and a
# parameter the function changes this way gets its own copy (as with assignment)
MUTATING_LIST_METHODS = {'add', 'insert', 'removeAt', 'remove', 'clear', 'sort', 'sortBy',
                         'removeLast', 'pop'}             # a growable array's end (45.3, 45.7)
MUTATING_MAP_METHODS = {'remove', 'clear'}
# Every List / Map method - another name on a list or map may be one of the program's own
# functions called as a method (Task 44.2)
# What a plain array can't do - it doesn't grow or shrink (45.10, D.141); int:[] will (45.3)
ARRAY_GROW_METHODS = ('add', 'insert', 'removeAt', 'remove', 'clear', 'removeLast', 'pop')
# Copying a part (45.5, D.046) - on every array and List; slice / sliceAt are quick typing
PART_METHODS = ('copyPart', 'slice', 'copyPartAt', 'sliceAt')
LIST_METHOD_NAMES = {'add', 'insert', 'removeAt', 'remove', 'clear', 'len', 'contains', 'indexOf',
                     'join', 'slice', 'copyPart', 'copyPartAt', 'sliceAt', 'sort', 'sortBy', 'filter', 'map', 'reduce', 'toList',
                     'noDuplicates', 'noNull', 'readOnly'}          # options: Task 32.14
MAP_METHOD_NAMES = {'has', 'get', 'remove', 'keys', 'values', 'len', 'clear', 'noDuplicates',
                    'noNull', 'readOnly'}
MAP_KEY_TYPES = ('string', 'int', 'char')
_SORTABLE = ('int', 'float', 'double', 'byte', 'char', 'string', 'bool')


class CollectionRulesMixin:
    def _part_call(self, node, receiver_type) -> TypeNode:
        """`xs.copyPart(start, count)` / `xs.copyPartAt(start, end)` and their quick names `slice` /
        `sliceAt` (45.5, D.046): a copy of a part. A List gives a List; any array a new array."""
        method = node.callee.member
        element = receiver_type.element_type
        if len(node.arguments) != 2:
            ends = node.callee.member in ('copyPartAt', 'sliceAt')
            last = 'end' if ends else 'count'
            self.errors.append(SemanticError(f"{method} takes two values: start, {last}", node.location))
        int_type = PrimitiveType(location=node.location, name='int')
        for arg in node.arguments:
            actual = self.visit(arg)
            if not self.types_compatible(int_type, actual):
                self.errors.append(SemanticError(
                    f"{method}: a position is an int, got {self.type_to_string(actual)}", arg.location))
        if isinstance(element, ArrayType):
            self.errors.append(SemanticError(
                f"{method} on an array of arrays waits for many dimensions (Task 45.12)", node.location))
        is_list = isinstance(receiver_type, ListType) and not receiver_type.array_form
        result = ListType(location=node.location, element_type=element, array_form=not is_list)
        node.list_method = method
        node.list_type = result
        node.new_array = not is_list
        return result

    def combine_type(self, node, left: TypeNode, right: TypeNode) -> Optional[TypeNode]:
        """`a + b + c` (Task 45.4): two arrays make a new array, two Lists a new List - all of one
        type. None when neither side is an array or a List."""
        def kind(t):
            if isinstance(t, ArrayType) or (isinstance(t, ListType) and t.array_form):
                return 'array'
            return 'list' if isinstance(t, ListType) else None
        left_kind, right_kind = kind(left), kind(right)
        if left_kind is None and right_kind is None:
            return None
        if left_kind != right_kind:
            self.errors.append(SemanticError(
                f"Can't combine {self.type_to_string(left)} and {self.type_to_string(right)} with '+' - "
                f"both arrays or both Lists (toList() makes a List of an array)", node.location))
            return left if left_kind else right
        element = left.element_type
        if isinstance(element, ArrayType):
            self.errors.append(SemanticError(
                "Combining arrays of arrays with '+' waits for many dimensions (Task 45.12)", node.location))
        elif not self.types_equal(element, right.element_type):
            self.errors.append(SemanticError(
                f"'+' combines arrays of one type - {self.type_to_string(left)} and "
                f"{self.type_to_string(right)}", node.location))
        node.combine = left_kind
        node.new_array = left_kind == 'array'
        return ListType(location=node.location, element_type=element, array_form=left_kind == 'array')

    def array_to_list_call(self, node: CallExpr) -> Optional[ASTNode]:
        """`scores.toList()` on an array: a new List with copies of its elements (Task
        32.10a.1). Sharing (`toList(false)`) waits until arrays live on the heap (Task 45);
        an array of arrays waits for multi-dimensional arrays. None if not an array."""
        receiver = node.callee.object
        if isinstance(receiver, IdentifierExpr) and self.symbol_table.lookup(receiver.name) is None:
            return None
        receiver_type = self.visit(receiver)
        self.checked_receivers[id(receiver)] = receiver_type
        heap = isinstance(receiver_type, ListType) and receiver_type.array_form     # 45.10
        if not (isinstance(receiver_type, ArrayType) or heap) or self.user_method('toList', receiver_type):
            return None
        self.checked_receivers.pop(id(receiver), None)
        if isinstance(receiver_type, ArrayType) and receiver_type.dims:
            return self.many_dims_to_list(node, receiver_type)      # a List of Lists (45.11)
        element = receiver_type.element_type
        if isinstance(element, ArrayType):
            self.errors.append(SemanticError(
                "toList works on a one-dimensional array for now - arrays of arrays come later",
                node.location))
        if len(node.arguments) > 1:
            self.errors.append(SemanticError("toList takes one value: copy (true when left out)",
                                             node.location))
        elif node.arguments:
            given = node.arguments[0]
            self.visit(given)
            if not (isinstance(given, LiteralExpr) and given.value is True):
                self.errors.append(SemanticError(
                    "An array's toList always copies for now - it can't share the array as a "
                    "List until arrays can grow (Task 45); leave the value out", given.location))
        node.array_to_list = True
        node.list_type = ListType(location=node.location, element_type=element)
        self._check_collection_type(node.list_type, node.location)
        return node.list_type

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
            if not ((isinstance(key, PrimitiveType) and key.name in MAP_KEY_TYPES)
                    or (isinstance(key, EnumType)
                        and not any(v.fields for v in key.declaration.variants))):
                self.errors.append(SemanticError(
                    f"Map keys can be string, int, char or an enum without data, got {self.type_to_string(key)}",
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
            if isinstance(element, LiteralExpr) and element.type_hint == 'null' and list_type.array_form:
                element.inferred_type = element_type   # a heap array's slot may be null (D.140, 45.10)
                if not (self.is_class(element_type) or isinstance(element_type, EnumType)
                        or getattr(self.struct_declaration(element_type), 'is_interface', False)):
                    self.errors.append(SemanticError(
                        f"An array of {self.type_to_string(element_type)} can't hold null - only an "
                        f"array of objects or enums can (D.140)", element.location))
                continue
            if isinstance(element, LiteralExpr) and element.type_hint == 'null':     # D.139 (52.10)
                self.errors.append(SemanticError(
                    f"A List never holds null - {self.type_to_string(list_type)} "
                    f"[...] adds each item; give an object (D.139)", element.location))
                continue
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

    def _collection_option(self, node, method: str, receiver, is_map: bool = False):
        """noDuplicates() / noNull() / readOnly() (Task 32.14): set in the variable's own set-up
        block - `List<string> names = [] { names.noDuplicates() }`."""
        if node.arguments:
            self.errors.append(SemanticError(f"'{method}' takes no arguments", node.location))
        if not getattr(node, 'in_setup', False):
            name = getattr(receiver, 'name', 'xs')
            self.errors.append(SemanticError(
                f"'{method}()' is set in the List's / Map's own set-up block - "
                f"List<string> {name} = [] {{ {name}.{method}() }}", node.location))
        elif is_map and method == 'noDuplicates':
            self.errors.append(SemanticError("A Map's keys never repeat already - noDuplicates() is "
                                             "for a List", node.location))
        return self._void(node)

    def _collection_method_call(self, node: CallExpr) -> Optional[ASTNode]:
        """`xs.add(5)` on a List - checked here and marked for the generator
        (node.list_method). Returns the result type, or None when the receiver isn't a
        collection (then it's a built-in type's method or a struct field)."""
        receiver = node.callee.object
        if isinstance(receiver, IdentifierExpr) and self.symbol_table.lookup(receiver.name) is None:
            return None   # String.toUpper - a type class, not a value
        receiver_type = self.visit(receiver)
        self.checked_receivers[id(receiver)] = receiver_type   # checked once
        names = LIST_METHOD_NAMES if isinstance(receiver_type, ListType) else MAP_METHOD_NAMES
        if isinstance(receiver_type, (ListType, MapType)) and node.callee.member not in names \
                and self.user_method(node.callee.member, receiver_type) is not None:
            return None   # the program's own function, called as a method (Task 44.2)
        if isinstance(receiver_type, MapType):
            self.checked_receivers.pop(id(receiver), None)
            return self._map_method_call(node, receiver, receiver_type)
        iface = self.struct_declaration(receiver_type)
        if getattr(iface, 'is_interface', False) and iface.name.startswith('Collection<') \
                and node.callee.member == 'toList' and not node.arguments:
            # c.toList() - a copy of any Collection, as a List (32.6, D.095)
            self.checked_receivers.pop(id(receiver), None)
            node.to_list = (iface.name, receiver)
            return ListType(location=node.location, element_type=iface.element_type)
        if isinstance(receiver_type, ArrayType) and receiver_type.dims and node.callee.member == 'expand':
            self.checked_receivers.pop(id(receiver), None)
            return self.many_dims_expand(node, receiver_type)    # g.expand(ROWS, 1) (45.12d)
        if (isinstance(receiver_type, ArrayType) or getattr(receiver_type, 'array_form', False)) \
                and node.callee.member in ('setBufferType', 'setSize'):
            self.checked_receivers.pop(id(receiver), None)      # buffers - after self-hosting (D.146)
            self.errors.append(SemanticError(
                f"{node.callee.member} is not built yet - buffers for large arrays come after self-hosting, "
                f"once they can be measured (D.146, FEATURES L16.3)", node.location))
            return self._void(node)
        if isinstance(receiver_type, ArrayType) and node.callee.member in PART_METHODS:
            self.checked_receivers.pop(id(receiver), None)      # a stack array's part (45.5)
            return self._part_call(node, receiver_type)
        if not isinstance(receiver_type, ListType):
            return None
        self.checked_receivers.pop(id(receiver), None)
        method = node.callee.member
        element = receiver_type.element_type
        if receiver_type.array_form:
            # a plain array on the heap (45.10): the Array class's methods only (D.141, D.142)
            if receiver_type.growable and method in ('add', 'removeLast', 'pop'):
                pass                          # int:[] grows and shrinks at its end (45.3)
            elif receiver_type.growable and method in ARRAY_GROW_METHODS:
                self.errors.append(SemanticError(
                    f"{method}: an array grows and shrinks only at its end - add, removeLast (pop); "
                    f"use a List to change it anywhere (D.141)", node.location))
                return self._void(node)
            elif method in ARRAY_GROW_METHODS:
                self.errors.append(SemanticError(
                    f"{method}: a plain array doesn't grow or shrink - declare it "
                    f"{self.type_to_string(element)}:[] (D.141)", node.location))
                return self._void(node)
            elif method not in ('len',) + PART_METHODS:
                self.errors.append(SemanticError(
                    f"An array has no method '{method}' (it has length, len, toList, toCSV, copyPart, "
                    f"copyPartAt)", node.location))
                return self._void(node)
        node.list_method = method
        node.list_type = receiver_type
        if method in ('noDuplicates', 'noNull', 'readOnly'):
            return self._collection_option(node, method, receiver)        # Task 32.14
        if method in MUTATING_LIST_METHODS:
            self._check_changeable(receiver, method)
        args = node.arguments
        if method in ('removeLast', 'pop'):              # a growable array (45.3): the item back
            if args:
                self.errors.append(SemanticError(f"{method}() takes no values", node.location))
            return element

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
        if method == 'toList':
            # xs.toList() - a copy (deep, as byVal); xs.toList(false) - the same list, shared
            # (Task 32.10a.1, user 2026-10-29)
            if len(args) > 1:
                want(1)
            elif args:
                check(args[0], bool_type, 'copy')
            if self.holds_objects(element) and not (
                    args and isinstance(args[0], LiteralExpr) and args[0].value is False):
                self.no_object_copies(receiver_type, node.location)   # 32.10b: needs clone()
            return receiver_type
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
        if method in PART_METHODS:
            return self._part_call(node, receiver_type)
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
        if method in ('noDuplicates', 'noNull', 'readOnly'):
            return self._collection_option(node, method, receiver, is_map=True)    # 32.14
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
        from src.parser.parser import type_text
        view = lambda t: StructType(location=node.location, name=f'Collection<{type_text(t)}>',
                                    declaration=self.struct_named(f'Collection<{type_text(t)}>'))
        # keys() / values(): borrowed views of the Map - no copy (32.6, D.095)
        return {'has': bool_type, 'get': value, 'remove': bool_type,
                'keys': view(key),
                'values': view(value),
                'len': int_type, 'clear': self._void(node)}[method]

    # ------------------------------------------------------------------ for ... in

    def _collection_of(self, type_node):
        """The Collection<X> interface a class implements, or None (Task 32.4)."""
        decl = self.struct_declaration(type_node)
        name = next((n for n in getattr(decl, 'all_interfaces', ()) if n.startswith('Collection<')), None)
        if name is None and getattr(decl, 'is_interface', False) and decl.name.startswith('Collection<'):
            name = decl.name
        return self.struct_named(name) if name else None

    def _no_change_while_looping(self, node, iterable_type) -> None:
        """D.058 (Task 32.4): the collection being looped over isn't changed inside the loop -
        Fusion's own never; a class of your own only with [collections]
        allowChangeWhileLooping. A compile error here; a change this can't see is a
        ModifiedWhileLoopingError while running."""
        from dataclasses import fields as dataclass_fields, is_dataclass
        looped = node.iterable
        if not isinstance(looped, IdentifierExpr):
            return
        own = self._collection_of(iterable_type) is not None
        if own and getattr(self, 'allow_change_while_looping', False):
            return
        changing = MUTATING_MAP_METHODS if isinstance(iterable_type, MapType) else MUTATING_LIST_METHODS
        decl = self.struct_declaration(iterable_type) if own else None

        def changes(member):
            if not own:
                return member in changing
            method = next((m for m in decl.methods if getattr(m, 'method_name', None) == member), None) \
                or getattr(decl, 'inherited', {}).get(member)
            return member in ('add', 'remove', 'addAll', 'removeAll', 'keepOnly', 'retainAll', 'clear') \
                or getattr(method, 'changes_this', False)

        def walk(n):
            if isinstance(n, list):
                for item in n:
                    walk(item)
                return
            if not is_dataclass(n) or isinstance(n, type):
                return
            if isinstance(n, CallExpr) and isinstance(n.callee, MemberExpr) \
                    and isinstance(n.callee.object, IdentifierExpr) \
                    and n.callee.object.name == looped.name and changes(n.callee.member):
                hint = (" - or [collections] allowChangeWhileLooping = true for a class of your own"
                        if own else "")
                self.errors.append(SemanticError(
                    f"'{looped.name}' is being looped over - it can't change inside the loop "
                    f"({n.callee.member}); build a new one instead{hint}", n.location))
            for f in dataclass_fields(n):
                if f.name not in ('location', 'inferred_type', 'declaration', 'scope'):
                    walk(getattr(n, f.name))
        walk(node.body)

    def _check_for_iterable(self, node) -> None:
        """`for x in range(...)`, `for x in xs` (a List or an array): the loop variable gets
        the element type. Anything else is an error - it used to loop 0..9 silently."""
        iterable = node.iterable
        if isinstance(iterable, CallExpr) and isinstance(iterable.callee, IdentifierExpr) \
                and iterable.callee.name == 'range':
            self.visit(iterable)
            return
        iterable_type = self.visit(iterable)
        if isinstance(iterable_type, ArrayType) and iterable_type.dims:
            # foreach over 2 or 3 dimensions: the outer one first, a view of the rest (45.12b)
            element = self.many_dims_loop(node, iterable_type)
            scope = getattr(node, 'scope', None)
            if element is not None and scope is not None and node.variable in scope.symbols:
                scope.symbols[node.variable].data_type = element
            return
        if isinstance(iterable_type, ListType):
            element = iterable_type.element_type
        elif isinstance(iterable_type, MapType):
            element = iterable_type.key_type      # a map's keys, in the order they were added
            declared = getattr(node, 'declared_type', None)
            if isinstance(declared, StructType) and declared.name.startswith('Entry<'):
                element = declared               # each key and value (32.6, D.096)
                node.map_entries = declared.name
        elif isinstance(iterable_type, ArrayType):
            element = iterable_type.element_type
        elif self._collection_of(iterable_type) is not None:
            # a class implementing Collection<X> (Task 32.4): its iterator() gives the items
            iface = self._collection_of(iterable_type)
            element = iface.element_type
            node.collected = (ListType(location=iterable.location, element_type=element), iface.name)
        else:
            if not (isinstance(iterable_type, PrimitiveType) and iterable_type.name == 'void'):
                self.errors.append(SemanticError(
                    f"'for ... in' needs range(...), a List, a Map, an array or a class "
                    f"implementing Collection<T>, got "
                    f"{self.type_to_string(iterable_type)}", iterable.location))
            return
        node.element_type = element
        declared = getattr(node, 'declared_type', None)            # foreach (T x in c) - 32.4
        if declared is not None and not self.types_equal(declared, element):
            self.errors.append(SemanticError(
                f"foreach ({self.type_to_string(declared)} {node.variable} in ...): its items are "
                f"{self.type_to_string(element)}", node.location))
        self._no_change_while_looping(node, iterable_type)          # D.058
        scope = getattr(node, 'scope', None)
        if scope is not None and node.variable in scope.symbols:
            scope.symbols[node.variable].data_type = element
