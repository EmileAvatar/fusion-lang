"""C code for the built-in collections (Task 18.5): List<T> now; Map<K, V> in 18.5.2.

Each element type gets its own list type and functions, made only when a program uses them
- `List<int>` is `fusion_list_int { int* data; int len; int cap; }` with fusion_list_int_add,
_at, _copy, _free, ... (no boxing, no speed cost). A list is a value like a string: copied
on assignment (independent), freed when its owner goes away, moved when it's new.

C needs things declared before use, and structs and lists can contain each other, so the
code goes in three places (see CCodeGenerator.generate): forward struct typedefs, list
typedefs and prototypes before the struct definitions; the function bodies after
everything else that is generated on demand.
"""

from ..parser.ast_nodes import (
    ArrayLiteralExpr, IdentifierExpr, MemberExpr, IndexExpr, PrimitiveType, StructType,
    ListType, FunctionType,
)

_SORTABLE = ('int', 'float', 'double', 'byte', 'char', 'string', 'bool')


class CollectionsMixin:
    """List code generation; needs self.list_types / list_protos / list_bodies (generate())."""

    # ------------------------------------------------------------------ names and types

    def _list_key(self, element) -> str:
        if isinstance(element, PrimitiveType):
            return element.name
        if isinstance(element, StructType):
            return self._struct_c_name(element)
        if isinstance(element, ListType):
            return 'list_' + self._list_key(element.element_type)
        raise NotImplementedError(f"Internal compiler error: a List of {type(element).__name__}")

    def list_c_name(self, list_type: ListType) -> str:
        """The C type of a List<T>; makes its code the first time."""
        name = 'fusion_list_' + self._list_key(list_type.element_type)
        if name not in self.list_types:
            if isinstance(list_type.element_type, ListType):
                self.list_c_name(list_type.element_type)   # the inner list's typedef first
            self.list_types[name] = list_type
            self._make_list_code(name, list_type.element_type)
        return name

    def collection_section_lines(self) -> list:
        """Forward struct typedefs, list typedefs and prototypes - before the structs."""
        if not self.list_types:
            return []
        lines = ['// Lists (Task 18.5.1) - types and prototypes']
        for struct in getattr(self, 'struct_decls', {}).values():
            c = self._struct_c_name(StructType(location=struct.location, name=struct.name,
                                               declaration=struct))
            lines.append(f'typedef struct {c} {c};')
        for name, list_type in self.list_types.items():
            element_c = self.map_type(list_type.element_type)
            lines.append(f'typedef struct {{ {element_c}* data; int len; int cap; }} {name};')
        lines += self.list_protos + ['']
        return lines

    def collection_body_lines(self) -> list:
        return (['// Lists (Task 18.5.1) - functions'] + self.list_bodies + ['']) if self.list_bodies else []

    # ------------------------------------------------------------------ the C for one list type

    def _make_list_code(self, name: str, element) -> None:
        T = self.map_type(element)
        managed = self.is_managed(element)

        def copy(code):
            return self.copy_code(element, code) if managed else code

        def free(lvalue):
            return ' '.join(self.free_lines(element, lvalue))

        eq = self.value_equality('a.data[i]', element, 'b.data[i]', element)
        eq_v = self.value_equality('l.data[i]', element, 'v', element)
        functions = {
            f'{name} {name}_from(const {T}* items, int n)': [
                f'{name} r = {{0}};',
                f'if (n > 0) {{ r.data = ({T}*)fusion_alloc(sizeof({T}) * (size_t)n); '
                f'memcpy(r.data, items, sizeof({T}) * (size_t)n); r.len = r.cap = n; }}',
                'return r;'],
            f'void {name}_grow({name}* l, int need)': [
                'if (need <= l->cap) return;',
                'int cap = l->cap < 4 ? 4 : l->cap;',
                'while (cap < need) { if (cap > 536870911) fusion_runtime_error(NULL, "a List '
                'can\'t hold more than 536,870,911 elements"); cap *= 2; }',
                f'{T}* data = ({T}*)fusion_alloc(sizeof({T}) * (size_t)cap);',
                f'if (l->len > 0) memcpy(data, l->data, sizeof({T}) * (size_t)l->len);',
                'if (l->data) fusion_dealloc(l->data);',
                'l->data = data; l->cap = cap;'],
            f'{name} {name}_copy({name} v)': [
                f'{name} r = {{0}};',
                f'{name}_grow(&r, v.len);',
                f'for (int i = 0; i < v.len; i++) r.data[i] = {copy("v.data[i]")};',
                'r.len = v.len;',
                'return r;'],
            f'void {name}_free({name}* l)': [
                (f'for (int i = 0; i < l->len; i++) {{ {free("l->data[i]")} }}' if managed else ''),
                'if (l->data) fusion_dealloc(l->data);',
                f'*l = ({name}){{0}};'],
            f'void {name}_set({name}* dst, {name} value)': [
                f'{name}_free(dst);', '*dst = value;'],
            f'void {name}_add({name}* l, {T} v)': [
                f'{name}_grow(l, l->len + 1);', 'l->data[l->len++] = v;'],
            f'void {name}_insert({name}* l, int i, {T} v, const char* where)': [
                'if (i < 0 || i > l->len) fusion_runtime_error(where, "insert(position %d) is '
                'outside the list (length %d)", i, l->len);',
                f'{name}_grow(l, l->len + 1);',
                f'memmove(l->data + i + 1, l->data + i, sizeof({T}) * (size_t)(l->len - i));',
                'l->data[i] = v; l->len++;'],
            f'void {name}_removeAt({name}* l, int i, const char* where)': [
                'if (i < 0 || i >= l->len) fusion_runtime_error(where, "removeAt(%d) is outside '
                'the list (length %d)", i, l->len);',
                (free('l->data[i]') if managed else ''),
                f'memmove(l->data + i, l->data + i + 1, sizeof({T}) * (size_t)(l->len - i - 1));',
                'l->len--;'],
            f'void {name}_clear({name}* l)': [
                (f'for (int i = 0; i < l->len; i++) {{ {free("l->data[i]")} }}' if managed else ''),
                'l->len = 0;'],
            f'{T} {name}_at({name} l, int i, const char* where)': [
                'if (i < 0 || i >= l.len) fusion_runtime_error(where, "index %d is outside the '
                'list (length %d)", i, l.len);',
                'return l.data[i];'],
            f'{T}* {name}_ptr({name}* l, int i, const char* where)': [
                'if (i < 0 || i >= l->len) fusion_runtime_error(where, "index %d is outside the '
                'list (length %d)", i, l->len);',
                'return &l->data[i];'],
            f'bool {name}_eq({name} a, {name} b)': [
                'if (a.len != b.len) return false;',
                f'for (int i = 0; i < a.len; i++) if (!{eq}) return false;',
                'return true;'],
            f'int {name}_indexOf({name} l, {T} v)': [
                f'for (int i = 0; i < l.len; i++) if ({eq_v}) return i;',
                'return -1;'],
            f'bool {name}_contains({name} l, {T} v)': [f'return {name}_indexOf(l, v) >= 0;'],
            f'bool {name}_remove({name}* l, {T} v)': [
                f'int i = {name}_indexOf(*l, v);',
                'if (i < 0) return false;',
                f'{name}_removeAt(l, i, NULL);',
                'return true;'],
            f'{name} {name}_slice({name} l, int start, int count, const char* where)': [
                'if (start < 0 || count < 0 || start > l.len || count > l.len - start)',
                '    fusion_runtime_error(where, "slice(start %d, count %d) is outside the list '
                '(length %d)", start, count, l.len);',
                f'{name} r = {{0}};',
                f'{name}_grow(&r, count);',
                f'for (int i = 0; i < count; i++) r.data[i] = {copy("l.data[start + i]")};',
                'r.len = count;',
                'return r;'],
            f'{name} {name}_filter({name} l, bool (*keep)({T}))': [
                f'{name} r = {{0}};',
                f'for (int i = 0; i < l.len; i++) if (keep(l.data[i])) {name}_add(&r, {copy("l.data[i]")});',
                'return r;'],
            # Stable merge sort: equal elements keep their order
            f'void {name}_msort({T}* a, {T}* tmp, int n, int (*cmp)({T}, {T}))': [
                'if (n < 2) return;',
                'int h = n / 2;',
                f'{name}_msort(a, tmp, h, cmp); {name}_msort(a + h, tmp, n - h, cmp);',
                'int i = 0, j = h, k = 0;',
                'while (i < h && j < n) tmp[k++] = cmp(a[j], a[i]) < 0 ? a[j++] : a[i++];',
                'while (i < h) tmp[k++] = a[i++];',
                'while (j < n) tmp[k++] = a[j++];',
                f'memcpy(a, tmp, sizeof({T}) * (size_t)n);'],
            f'void {name}_sortBy({name}* l, int (*cmp)({T}, {T}))': [
                'if (l->len < 2) return;',
                f'{T}* tmp = ({T}*)fusion_alloc(sizeof({T}) * (size_t)l->len);',
                f'{name}_msort(l->data, tmp, l->len, cmp);',
                'fusion_dealloc(tmp);'],
        }
        if isinstance(element, PrimitiveType) and element.name in _SORTABLE:
            order = ('fusion_str_cmp(a, b)' if element.name == 'string'
                     else '(a > b) - (a < b)')
            functions[f'int {name}_order({T} a, {T} b)'] = [f'return {order};']
            functions[f'void {name}_sort({name}* l)'] = [f'{name}_sortBy(l, {name}_order);']
        for signature, body in functions.items():
            self.list_protos.append(f'static inline {signature};')
            self.list_bodies += [f'static inline {signature} {{'] + \
                [f'    {line}' for line in body if line] + ['}']

    def list_map_helper(self, source: ListType, result: ListType) -> str:
        """`xs.map(f)`: a list of what f returns for each element."""
        name = f'{self.list_c_name(source)}_map_{self._list_key(result.element_type)}'
        if name not in self.list_extras:
            self.list_extras.add(name)
            S, R = self.map_type(source.element_type), self.map_type(result.element_type)
            src, dst = self.list_c_name(source), self.list_c_name(result)
            signature = f'{dst} {name}({src} l, {R} (*f)({S}))'
            self.list_protos.append(f'static inline {signature};')
            self.list_bodies += [f'static inline {signature} {{',
                                 f'    {dst} r = {{0}};',
                                 f'    for (int i = 0; i < l.len; i++) {dst}_add(&r, f(l.data[i]));',
                                 '    return r;', '}']
        return name

    def list_reduce_helper(self, source: ListType, value_type) -> str:
        """`xs.reduce(start, f)`: the running value starts as a copy of `start`; each step's
        result replaces it (the old one is freed)."""
        key = self._list_key(value_type)
        name = f'{self.list_c_name(source)}_reduce_{key}'
        if name not in self.list_extras:
            self.list_extras.add(name)
            S, V = self.map_type(source.element_type), self.map_type(value_type)
            src = self.list_c_name(source)
            managed = self.is_managed(value_type)
            signature = f'{V} {name}({src} l, {V} start, {V} (*f)({V}, {S}))'
            step = (f'{V} next = f(acc, l.data[i]); {" ".join(self.free_lines(value_type, "acc"))} acc = next;'
                    if managed else 'acc = f(acc, l.data[i]);')
            self.list_protos.append(f'static inline {signature};')
            self.list_bodies += [f'static inline {signature} {{',
                                 f'    {V} acc = {self.copy_code(value_type, "start") if managed else "start"};',
                                 f'    for (int i = 0; i < l.len; i++) {{ {step} }}',
                                 '    return acc;', '}']
        return name

    # ------------------------------------------------------------------ expressions

    def list_literal_code(self, node: ArrayLiteralExpr) -> str:
        list_type = node.inferred_type
        name = self.list_c_name(list_type)
        if not node.elements:
            return f'(({name}){{0}})'
        element = list_type.element_type
        items = ', '.join(self.owned_value(e, element) for e in node.elements)
        return f'{name}_from(({self.map_type(element)}[]){{{items}}}, {len(node.elements)})'

    def list_lvalue(self, expr) -> str:
        """A C lvalue for a target that goes through a list element: xs[1] = 5,
        grid[1][0] = 9, people[0].name = "x"."""
        if isinstance(expr, IndexExpr) and isinstance(getattr(expr.array, 'inferred_type', None), ListType):
            name = self.list_c_name(expr.array.inferred_type)
            return (f'(*{name}_ptr(&{self.list_lvalue(expr.array)}, {self.visit(expr.index)}, '
                    f'{self._where(expr)}))')
        if isinstance(expr, IndexExpr):
            return f'{self.list_lvalue(expr.array)}[{self.visit(expr.index)}]'
        if isinstance(expr, MemberExpr):
            return f'{self.list_lvalue(expr.object)}.{self._field_name(expr.member)}'
        return self.visit(expr)

    @staticmethod
    def goes_through_list(expr) -> bool:
        while isinstance(expr, (IndexExpr, MemberExpr)):
            inner = expr.array if isinstance(expr, IndexExpr) else expr.object
            if isinstance(expr, IndexExpr) and isinstance(getattr(inner, 'inferred_type', None), ListType):
                return True
            expr = inner
        return False

    def list_method_code(self, node) -> str:
        """C for `xs.method(args)` (Task 18.5.1)."""
        method, list_type = node.list_method, node.list_type
        name = self.list_c_name(list_type)
        element = list_type.element_type
        receiver = node.callee.object
        args = node.arguments
        where = self._where(node)
        if method in ('add', 'insert', 'removeAt', 'remove', 'clear', 'sort', 'sortBy'):
            target = f'&{self.list_lvalue(receiver)}'
        else:
            target = self.visit(receiver)
        if method == 'add':
            return f'{name}_add({target}, {self.owned_value(args[0], element)})'
        if method == 'insert':
            return f'{name}_insert({target}, {self.visit(args[0])}, {self.owned_value(args[1], element)}, {where})'
        if method == 'removeAt':
            return f'{name}_removeAt({target}, {self.visit(args[0])}, {where})'
        if method in ('clear', 'sort'):
            return f'{name}_{method}({target})'
        if method == 'sortBy':
            return f'{name}_sortBy({target}, {self.visit(args[0])})'
        if method in ('contains', 'indexOf', 'remove'):
            return f'{name}_{method}({target}, {self.visit(args[0])})'
        if method == 'len':
            return f'({target}).len'
        if method == 'slice':
            return f'{name}_slice({target}, {self.visit(args[0])}, {self.visit(args[1])}, {where})'
        if method == 'filter':
            return f'{name}_filter({target}, {self.visit(args[0])})'
        if method == 'map':
            helper = self.list_map_helper(list_type, node.inferred_type)
            return f'{helper}({target}, {self.visit(args[0])})'
        if method == 'reduce':
            helper = self.list_reduce_helper(list_type, node.inferred_type)
            return f'{helper}({target}, {self.visit(args[0])}, {self.visit(args[1])})'
        raise NotImplementedError(f"Internal compiler error: List method '{method}'")
