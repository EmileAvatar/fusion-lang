"""C code for the built-in collections (Task 18.5): List<T> (18.5.1), Map<K, V> (18.5.2).

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
    ListType, MapType, FunctionType,
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
        if isinstance(element, MapType):
            return f'map_{self._list_key(element.key_type)}__{self._list_key(element.value_type)}'
        raise NotImplementedError(f"Internal compiler error: a List of {type(element).__name__}")

    def list_c_name(self, list_type: ListType) -> str:
        """The C type of a List<T>; makes its code the first time."""
        name = 'fusion_list_' + self._list_key(list_type.element_type)
        if name not in self.list_types:
            if isinstance(list_type.element_type, (ListType, MapType)):
                self.map_type(list_type.element_type)      # the inner collection's typedef first
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
        for name, kind in self.list_types.items():
            if isinstance(kind, MapType):
                lines.append(f'typedef struct {{ {self.map_type(kind.key_type)}* keys; '
                             f'{self.map_type(kind.value_type)}* vals; int len; int cap; '
                             f'int* slots; int nslots; }} {name};')
            else:
                element_c = self.map_type(kind.element_type)
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

    def list_lvalue(self, expr, final: bool = True) -> str:
        """A C lvalue for a target that goes through a list element or a map value: xs[1] = 5,
        grid[1][0] = 9, people[0].name = "x", ages["Ada"] = 36. Only the final `m[k] = v`
        adds a missing key; a key on the way (`m["a"][0] = 5`) must already be there."""
        inner_type = getattr(getattr(expr, 'array', None), 'inferred_type', None)
        if isinstance(expr, IndexExpr) and isinstance(inner_type, ListType):
            name = self.list_c_name(inner_type)
            return (f'(*{name}_ptr(&{self.list_lvalue(expr.array, False)}, {self.visit(expr.index)}, '
                    f'{self._where(expr)}))')
        if isinstance(expr, IndexExpr) and isinstance(inner_type, MapType):
            name = self.map_c_name(inner_type)
            base = self.list_lvalue(expr.array, False)
            if final:
                return f'(*{name}_put(&{base}, {self.visit(expr.index)}))'
            return f'(*{name}_ptr(&{base}, {self.visit(expr.index)}, {self._where(expr)}))'
        if isinstance(expr, IndexExpr):
            return f'{self.list_lvalue(expr.array, False)}[{self.visit(expr.index)}]'
        if isinstance(expr, MemberExpr):
            return f'{self.list_lvalue(expr.object, False)}.{self._field_name(expr.member)}'
        return self.visit(expr)

    @staticmethod
    def goes_through_list(expr) -> bool:
        """True for a target through a list element or a map value."""
        while isinstance(expr, (IndexExpr, MemberExpr)):
            inner = expr.array if isinstance(expr, IndexExpr) else expr.object
            if isinstance(expr, IndexExpr) and isinstance(getattr(inner, 'inferred_type', None),
                                                          (ListType, MapType)):
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
            target = f'&{self.list_lvalue(receiver, final=False)}'
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
        if method == 'join':
            self.text_list_helpers()
            return f'fusion_str_join({target}, {self.visit(args[0])}, {where})'
        if method == 'map':
            helper = self.list_map_helper(list_type, node.inferred_type)
            return f'{helper}({target}, {self.visit(args[0])})'
        if method == 'reduce':
            helper = self.list_reduce_helper(list_type, node.inferred_type)
            return f'{helper}({target}, {self.visit(args[0])}, {self.visit(args[1])})'
        raise NotImplementedError(f"Internal compiler error: List method '{method}'")

    # ------------------------------------------------------------------ Map<K, V> (18.5.2)

    def map_c_name(self, map_type) -> str:
        """The C type of a Map<K, V>; makes its code the first time."""
        name = 'fusion_' + self._list_key(map_type)
        if name not in self.list_types:
            for part in (map_type.key_type, map_type.value_type):
                if isinstance(part, (ListType, MapType)):
                    self.map_type(part)            # inner collection types first
            self.list_types[name] = map_type
            self._make_map_code(name, map_type.key_type, map_type.value_type)
        return name

    def _make_map_code(self, name: str, key, value) -> None:
        """An insertion-ordered hash map: entries in keys[] / vals[] (the order they were
        added), and an open-addressing index slots[] holding entry number + 1 (0 = empty)."""
        K, V = self.map_type(key), self.map_type(value)
        key_managed, value_managed = self.is_managed(key), self.is_managed(value)
        keys_list = self.list_c_name(ListType(location=None, element_type=key))
        values_list = self.list_c_name(ListType(location=None, element_type=value))

        def kcopy(code):
            return self.copy_code(key, code) if key_managed else code

        def vcopy(code):
            return self.copy_code(value, code) if value_managed else code

        def free_entry(i):
            parts = []
            if key_managed:
                parts += self.free_lines(key, f'm->keys[{i}]')
            if value_managed:
                parts += self.free_lines(value, f'm->vals[{i}]')
            return ' '.join(parts)

        if key.name == 'string':
            hash_body = ['uint32_t h = 2166136261u;',
                         'for (int i = 0; i < k.len; i++) { h ^= (unsigned char)k.data[i]; h *= 16777619u; }',
                         'return h;']
            missing = ('fusion_runtime_error(where, "key \\"%.*s\\" is not in the map", k.len, k.data);')
        else:
            hash_body = ['return (uint32_t)k * 2654435761u;']
            missing = ('fusion_runtime_error(where, "key %d is not in the map", (int)k);' if key.name == 'int'
                       else 'fusion_runtime_error(where, "key \'%s\' is not in the map", fusion_char_text(k).bytes);')
        key_eq = self.value_equality('m.keys[e - 1]', key, 'k', key)
        value_eq = self.value_equality('a.vals[i]', value, 'b.vals[j]', value)
        functions = {
            f'uint32_t {name}_hash({K} k)': hash_body,
            f'int {name}_find({name} m, {K} k)': [
                'if (m.nslots == 0) return -1;',
                'uint32_t mask = (uint32_t)m.nslots - 1;',
                f'for (uint32_t s = {name}_hash(k) & mask;; s = (s + 1) & mask) {{',
                '    int e = m.slots[s];',
                '    if (e == 0) return -1;',
                f'    if ({key_eq}) return e - 1;',
                '}'],
            f'void {name}_index({name}* m, int nslots)': [
                'if (m->slots) fusion_dealloc(m->slots);',
                'm->slots = (int*)fusion_alloc(sizeof(int) * (size_t)nslots);',
                'memset(m->slots, 0, sizeof(int) * (size_t)nslots);',
                'm->nslots = nslots;',
                'uint32_t mask = (uint32_t)nslots - 1;',
                f'for (int i = 0; i < m->len; i++) {{ uint32_t s = {name}_hash(m->keys[i]) & mask; '
                'while (m->slots[s]) s = (s + 1) & mask; m->slots[s] = i + 1; }'],
            f'{V}* {name}_put({name}* m, {K} k)': [
                f'int i = {name}_find(*m, k);',
                'if (i >= 0) return &m->vals[i];',
                'if (m->len == m->cap) {',
                '    int cap = m->cap < 8 ? 8 : m->cap * 2;',
                f'    {K}* keys = ({K}*)fusion_alloc(sizeof({K}) * (size_t)cap);',
                f'    {V}* vals = ({V}*)fusion_alloc(sizeof({V}) * (size_t)cap);',
                f'    if (m->len > 0) {{ memcpy(keys, m->keys, sizeof({K}) * (size_t)m->len); '
                f'memcpy(vals, m->vals, sizeof({V}) * (size_t)m->len); }}',
                '    if (m->keys) { fusion_dealloc(m->keys); fusion_dealloc(m->vals); }',
                '    m->keys = keys; m->vals = vals; m->cap = cap;',
                '}',
                f'm->keys[m->len] = {kcopy("k")};',
                f'm->vals[m->len] = {self._default_value_code(value)};',
                'm->len++;',
                f'if (m->len * 2 > m->nslots) {name}_index(m, m->nslots < 16 ? 16 : m->nslots * 2);',
                'else {',
                '    uint32_t mask = (uint32_t)m->nslots - 1;',
                f'    uint32_t s = {name}_hash(k) & mask;',
                '    while (m->slots[s]) s = (s + 1) & mask;',
                '    m->slots[s] = m->len;',
                '}',
                'return &m->vals[m->len - 1];'],
            f'{V}* {name}_ptr({name}* m, {K} k, const char* where)': [
                f'int i = {name}_find(*m, k);',
                f'if (i < 0) {missing}',
                'return &m->vals[i];'],
            f'{V} {name}_get({name} m, {K} k, const char* where)': [
                f'int i = {name}_find(m, k);',
                f'if (i < 0) {missing}',
                'return m.vals[i];'],
            f'{V} {name}_getOr({name} m, {K} k, {V} otherwise)': [
                f'int i = {name}_find(m, k);',
                'return i < 0 ? otherwise : m.vals[i];'],
            f'bool {name}_has({name} m, {K} k)': [f'return {name}_find(m, k) >= 0;'],
            f'bool {name}_remove({name}* m, {K} k)': [
                f'int i = {name}_find(*m, k);',
                'if (i < 0) return false;',
                free_entry('i'),
                f'memmove(m->keys + i, m->keys + i + 1, sizeof({K}) * (size_t)(m->len - i - 1));',
                f'memmove(m->vals + i, m->vals + i + 1, sizeof({V}) * (size_t)(m->len - i - 1));',
                'm->len--;',
                f'{name}_index(m, m->nslots);',
                'return true;'],
            f'void {name}_clear({name}* m)': [
                f'for (int i = 0; i < m->len; i++) {{ {free_entry("i")} }}' if (key_managed or value_managed) else '',
                'm->len = 0;',
                'if (m->slots) memset(m->slots, 0, sizeof(int) * (size_t)m->nslots);'],
            f'{name} {name}_copy({name} v)': [
                f'{name} r = {{0}};',
                'if (v.len == 0) return r;',
                f'r.keys = ({K}*)fusion_alloc(sizeof({K}) * (size_t)v.len);',
                f'r.vals = ({V}*)fusion_alloc(sizeof({V}) * (size_t)v.len);',
                f'for (int i = 0; i < v.len; i++) {{ r.keys[i] = {kcopy("v.keys[i]")}; r.vals[i] = {vcopy("v.vals[i]")}; }}',
                'r.len = r.cap = v.len;',
                f'{name}_index(&r, v.nslots);',
                'return r;'],
            f'void {name}_free({name}* m)': [
                f'for (int i = 0; i < m->len; i++) {{ {free_entry("i")} }}' if (key_managed or value_managed) else '',
                'if (m->keys) { fusion_dealloc(m->keys); fusion_dealloc(m->vals); }',
                'if (m->slots) fusion_dealloc(m->slots);',
                f'*m = ({name}){{0}};'],
            f'void {name}_set({name}* dst, {name} value)': [f'{name}_free(dst);', '*dst = value;'],
            f'{keys_list} {name}_keys({name} m)': [
                f'{keys_list} r = {{0}};',
                f'for (int i = 0; i < m.len; i++) {keys_list}_add(&r, {kcopy("m.keys[i]")});',
                'return r;'],
            f'{values_list} {name}_values({name} m)': [
                f'{values_list} r = {{0}};',
                f'for (int i = 0; i < m.len; i++) {values_list}_add(&r, {vcopy("m.vals[i]")});',
                'return r;'],
            f'bool {name}_eq({name} a, {name} b)': [
                'if (a.len != b.len) return false;',
                'for (int i = 0; i < a.len; i++) {',
                f'    int j = {name}_find(b, a.keys[i]);',
                f'    if (j < 0 || !{value_eq}) return false;',
                '}',
                'return true;'],
        }
        for signature, body in functions.items():
            self.list_protos.append(f'static inline {signature};')
            self.list_bodies += [f'static inline {signature} {{'] + \
                [f'    {line}' for line in body if line] + ['}']

    def map_method_code(self, node) -> str:
        """C for `m.method(args)` (Task 18.5.2)."""
        method, map_type = node.map_method, node.map_type
        name = self.map_c_name(map_type)
        receiver, args = node.callee.object, node.arguments
        if method in ('remove', 'clear'):
            target = f'&{self.list_lvalue(receiver, final=False)}'
        else:
            target = self.visit(receiver)
        if method == 'len':
            return f'({target}).len'
        if method == 'clear':
            return f'{name}_clear({target})'
        if method == 'get':
            return f'{name}_getOr({target}, {self.visit(args[0])}, {self.visit(args[1])})'
        if method in ('keys', 'values'):
            return f'{name}_{method}({target})'
        return f'{name}_{method}({target}, {self.visit(args[0])})'   # has, remove

    # ------------------------------------------------------------------ text <-> lists (18.5.3)

    def text_list_helpers(self) -> None:
        """split / join / lines / words - made the first time a program uses one, after
        List<string>'s own functions (they return or take a List<string>)."""
        if 'text_lists' in self.list_extras:
            return
        self.list_extras.add('text_lists')
        lst = self.list_c_name(ListType(location=None, element_type=PrimitiveType(location=None, name='string')))
        functions = {
            # Every piece between separators ("a,,b" -> a, "", b); "" splits into characters
            f'{lst} fusion_str_split(fusion_string s, fusion_string sep)': [
                f'{lst} r = {{0}};',
                'if (sep.len == 0) {',
                '    for (int i = 0; i < s.len; ) { int n = fusion_utf8_size((unsigned char)s.data[i]); '
                f'{lst}_add(&r, fusion_str_make(s.data + i, n)); i += n; }}',
                '    return r;',
                '}',
                'int from = 0;',
                'for (int i = fusion_find(s, 0, sep.data, sep.len); i >= 0; i = fusion_find(s, from, sep.data, sep.len)) {',
                f'    {lst}_add(&r, fusion_str_make(s.data + from, i - from));',
                '    from = i + sep.len;',
                '}',
                f'{lst}_add(&r, fusion_str_make(s.data + from, s.len - from));',
                'return r;'],
            f'fusion_string fusion_str_join({lst} parts, fusion_string sep, const char* where)': [
                'long long len = 0;',
                'for (int i = 0; i < parts.len; i++) len += parts.data[i].len + (i > 0 ? sep.len : 0);',
                'int total = fusion_checked_size(len, "join", where), o = 0;',
                'char* out = (char*)fusion_alloc((size_t)total + 1);',
                'for (int i = 0; i < parts.len; i++) {',
                '    if (i > 0) { memcpy(out + o, sep.data, (size_t)sep.len); o += sep.len; }',
                '    memcpy(out + o, parts.data[i].data, (size_t)parts.data[i].len); o += parts.data[i].len;',
                '}',
                'return fusion_str_take(out, total);'],
            # Lines without their "\n" (or "\r\n"); a last newline doesn't make an empty line
            f'{lst} fusion_str_lines(fusion_string s)': [
                f'{lst} r = {{0}};',
                'int from = 0;',
                'for (int i = 0; i <= s.len; i++) {',
                '    if (i < s.len && s.data[i] != \'\\n\') continue;',
                '    if (i == s.len && from == s.len) break;',
                '    int end = i;',
                '    if (end > from && s.data[end - 1] == \'\\r\') end--;',
                f'    {lst}_add(&r, fusion_str_make(s.data + from, end - from));',
                '    from = i + 1;',
                '}',
                'return r;'],
            # Words between runs of spaces, tabs and newlines - never an empty word
            f'{lst} fusion_str_words(fusion_string s)': [
                f'{lst} r = {{0}};',
                'int i = 0;',
                'while (i < s.len) {',
                '    while (i < s.len && fusion_is_space(s.data[i])) i++;',
                '    int start = i;',
                '    while (i < s.len && !fusion_is_space(s.data[i])) i++;',
                f'    if (i > start) {lst}_add(&r, fusion_str_make(s.data + start, i - start));',
                '}',
                'return r;'],
        }
        for signature, body in functions.items():
            self.list_protos.append(f'static inline {signature};')
            self.list_bodies += [f'static inline {signature} {{'] + [f'    {line}' for line in body] + ['}']
