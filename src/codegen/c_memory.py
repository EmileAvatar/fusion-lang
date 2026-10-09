"""String values and automatic cleanup (Task 18.3.1).

Strings are values, like structs (user decision 2026-10-09): each string variable, struct
field and array element owns its own text, copying makes an independent copy, and the
compiler frees every owned string exactly once when its owner goes away - no garbage
collector and no reference counts.

A "managed" type is one that owns heap memory and so needs copying and freeing: a string, a
struct with a managed field anywhere inside it, or an array of managed elements.

The rules codegen follows:
- Text written in the source is never freed and costs nothing at run time (FUSION_STR).
- Storing a value (variable, field, array element, constructor field, return value) gives
  the owner its own copy - unless the value is a fresh temporary (a call's result), which
  is simply handed over.
- Function parameters borrow the caller's value. A function that assigns to a parameter
  first makes its own copy, so the caller's value is never changed or freed.
- A fresh temporary that nothing takes ownership of (e.g. a call result passed straight to
  another function) is freed at the end of its statement.
- When a block ends - or is left early by return, break or continue - its owned variables
  are freed, innermost first.

The C side lives in RUNTIME_PRELUDE, emitted at the top of every generated program. Compiled
with -DFUSION_LEAK_CHECK it also tracks every allocation and stops with exit code 3 if
anything is left unfreed at exit, or 4 on a double free - the test suite always compiles
this way.
"""

from dataclasses import fields as dataclass_fields, is_dataclass

from ..parser.ast_nodes import (
    ASTNode, AssignmentStmt, MemberExpr, IndexExpr, IdentifierExpr, CallExpr, LiteralExpr,
    BinaryExpr,
    ArrayLiteralExpr, LambdaExpr, PrimitiveType, ArrayType, StructType, StructDecl,
)
from .c_names import mangle_function_name


RUNTIME_PRELUDE = r'''// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
    return p;
}

static inline void fusion_dealloc(void* p) {
#ifdef FUSION_LEAK_CHECK
    int i = fusion_live_count - 1;
    while (i >= 0 && fusion_live[i] != p) i--;
    if (i < 0) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: a string was freed twice\n");
        _Exit(4);
    }
    fusion_live[i] = fusion_live[--fusion_live_count];
#endif
    free(p);
}

// An independent copy. Text from the source never changes, so it's shared rather than
// copied - except under the leak check, where every copy is real so every free is tested
static inline fusion_string fusion_str_copy(fusion_string s) {
    fusion_string r;
#ifndef FUSION_LEAK_CHECK
    if (!s.owned) return s;
#endif
    r.data = (char*)fusion_alloc((size_t)s.len + 1);
    memcpy(r.data, s.data, (size_t)s.len);
    r.data[s.len] = '\0';
    r.len = s.len;
    r.owned = 1;
    return r;
}

static inline void fusion_str_free(fusion_string* s) {
    if (s->owned) fusion_dealloc(s->data);
    *s = FUSION_STR("");
}

// Replace a stored string: the new value is computed before the old one is freed, so
// `s = s` is safe
static inline void fusion_str_set(fusion_string* dst, fusion_string value) {
    fusion_str_free(dst);
    *dst = value;
}

static inline bool fusion_str_eq(fusion_string a, fusion_string b) {
    return a.len == b.len && memcmp(a.data, b.data, (size_t)a.len) == 0;
}

// Alphabetical (byte) order: negative, zero or positive, like strcmp
static inline int fusion_str_cmp(fusion_string a, fusion_string b) {
    int n = a.len < b.len ? a.len : b.len;
    int c = memcmp(a.data, b.data, (size_t)n);
    return c != 0 ? c : a.len - b.len;
}
// ---- String operations (Task 18.3.2) - each returns a new string, the input is unchanged.
// Lengths and indexes count bytes; `where` is "file:line" for run-time error messages
static inline fusion_string fusion_str_make(const char* data, int len) {
    fusion_string r;
    r.data = (char*)fusion_alloc((size_t)len + 1);
    if (len > 0) memcpy(r.data, data, (size_t)len);
    r.data[len] = '\0';
    r.len = len;
    r.owned = 1;
    return r;
}

static inline fusion_string fusion_str_join(const char* a, int alen, const char* b, int blen) {
    fusion_string r;
    r.data = (char*)fusion_alloc((size_t)alen + (size_t)blen + 1);
    memcpy(r.data, a, (size_t)alen);
    memcpy(r.data + alen, b, (size_t)blen);
    r.data[alen + blen] = '\0';
    r.len = alen + blen;
    r.owned = 1;
    return r;
}

static inline fusion_string fusion_str_concat(fusion_string a, fusion_string b) { return fusion_str_join(a.data, a.len, b.data, b.len); }
static inline fusion_string fusion_str_concat_char(fusion_string a, char c) { return fusion_str_join(a.data, a.len, &c, 1); }
static inline fusion_string fusion_char_concat_str(char c, fusion_string b) { return fusion_str_join(&c, 1, b.data, b.len); }

static inline char fusion_str_at(fusion_string s, int i, const char* where) {
    if (i < 0 || i >= s.len) fusion_runtime_error(where, "index %d is outside the string (length %d)", i, s.len);
    return s.data[i];
}

static inline fusion_string fusion_str_substring(fusion_string s, int start, int count, const char* where) {
    if (start < 0 || count < 0 || start > s.len || count > s.len - start)
        fusion_runtime_error(where, "substring(start %d, count %d) is outside the string (length %d)", start, count, s.len);
    return fusion_str_make(s.data + start, count);
}

static inline int fusion_str_indexOf(fusion_string s, fusion_string part) {
    for (int i = 0; i + part.len <= s.len; i++)
        if (memcmp(s.data + i, part.data, (size_t)part.len) == 0) return i;
    return -1;
}
static inline bool fusion_str_contains(fusion_string s, fusion_string part) { return fusion_str_indexOf(s, part) >= 0; }
static inline bool fusion_str_startsWith(fusion_string s, fusion_string part) {
    return part.len <= s.len && memcmp(s.data, part.data, (size_t)part.len) == 0;
}
static inline bool fusion_str_endsWith(fusion_string s, fusion_string part) {
    return part.len <= s.len && memcmp(s.data + s.len - part.len, part.data, (size_t)part.len) == 0;
}

static inline fusion_string fusion_str_toUpper(fusion_string s) {
    fusion_string r = fusion_str_make(s.data, s.len);
    for (int i = 0; i < r.len; i++) if (r.data[i] >= 'a' && r.data[i] <= 'z') r.data[i] -= 32;
    return r;
}
static inline fusion_string fusion_str_toLower(fusion_string s) {
    fusion_string r = fusion_str_make(s.data, s.len);
    for (int i = 0; i < r.len; i++) if (r.data[i] >= 'A' && r.data[i] <= 'Z') r.data[i] += 32;
    return r;
}
static inline bool fusion_is_space(char c) { return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f'; }
static inline fusion_string fusion_str_trim(fusion_string s) {
    int start = 0, end = s.len;
    while (start < end && fusion_is_space(s.data[start])) start++;
    while (end > start && fusion_is_space(s.data[end - 1])) end--;
    return fusion_str_make(s.data + start, end - start);
}

// Conversions to text
static inline fusion_string fusion_int_to_str(int value) { char buf[16]; int n = snprintf(buf, sizeof buf, "%d", value); return fusion_str_make(buf, n); }
static inline fusion_string fusion_double_to_str(double value) { char buf[32]; int n = snprintf(buf, sizeof buf, "%g", value); return fusion_str_make(buf, n); }
static inline fusion_string fusion_bool_to_str(bool value) { return value ? FUSION_STR("true") : FUSION_STR("false"); }
static inline fusion_string fusion_char_to_str(char value) { return fusion_str_make(&value, 1); }

// Conversions from text: the whole text must be a number, or the program stops with a
// clear error (user decision 2026-10-09) - check first with isInt / isFloat
static inline bool fusion_parse_int(fusion_string s, int* out) {
    int i = 0; long long value = 0; int negative = 0;
    if (i < s.len && (s.data[i] == '+' || s.data[i] == '-')) negative = s.data[i++] == '-';
    if (i >= s.len) return false;
    for (; i < s.len; i++) {
        if (s.data[i] < '0' || s.data[i] > '9') return false;
        value = value * 10 + (s.data[i] - '0');
        if (value > 2147483648LL) return false;
    }
    if (negative) value = -value;
    if (value > 2147483647LL || value < -2147483648LL) return false;
    *out = (int)value;
    return true;
}
static inline bool fusion_parse_float(fusion_string s, double* out) {
    char* end;
    if (s.len == 0) return false;
    for (int i = 0; i < s.len; i++)
        if (!strchr("0123456789+-.eE", s.data[i]) || s.data[i] == '\0') return false;
    *out = strtod(s.data, &end);
    return end == s.data + s.len;
}
static inline bool fusion_str_isInt(fusion_string s) { int v; return fusion_parse_int(s, &v); }
static inline bool fusion_str_isFloat(fusion_string s) { double v; return fusion_parse_float(s, &v); }
static inline int fusion_str_toInt(fusion_string s, const char* where) {
    int v;
    if (!fusion_parse_int(s, &v)) fusion_runtime_error(where, "'%.*s' is not a whole number (check with isInt first)", s.len, s.data);
    return v;
}
static inline float fusion_str_toFloat(fusion_string s, const char* where) {
    double v;
    if (!fusion_parse_float(s, &v)) fusion_runtime_error(where, "'%.*s' is not a number (check with isFloat first)", s.len, s.data);
    return (float)v;
}
// ---- end of runtime ----
'''


class MemoryManagementMixin:
    """Ownership-aware code generation - mixed into CCodeGenerator (Task 18.3.1)."""

    # ------------------------------------------------------------------ type queries

    def is_managed(self, type_node) -> bool:
        """True if values of this type own heap memory (a string anywhere inside them)."""
        if isinstance(type_node, PrimitiveType):
            return type_node.name == 'string'
        if isinstance(type_node, ArrayType):
            return self.is_managed(type_node.element_type)
        if isinstance(type_node, StructType):
            struct = self._struct_decl(type_node)
            return any(self.is_managed(f.field_type) for f in struct.fields)
        return False

    def _struct_c_name(self, type_node: StructType) -> str:
        return mangle_function_name(type_node.name)

    def copy_code(self, type_node, code: str) -> str:
        """C expression giving an independent copy of a (non-array) managed value."""
        if isinstance(type_node, PrimitiveType) and type_node.name == 'string':
            return f'fusion_str_copy({code})'
        if isinstance(type_node, StructType) and self.is_managed(type_node):
            return f'fusion_copy_{self._struct_c_name(type_node)}({code})'
        return code

    def free_lines(self, type_node, lvalue: str, depth: int = 0) -> list:
        """C statements freeing a managed value stored at `lvalue`."""
        if not self.is_managed(type_node):
            return []
        if isinstance(type_node, PrimitiveType):
            return [f'fusion_str_free(&{lvalue});']
        if isinstance(type_node, StructType):
            return [f'fusion_free_{self._struct_c_name(type_node)}(&{lvalue});']
        index = f'fusion_i{depth}'
        inner = ' '.join(self.free_lines(type_node.element_type, f'{lvalue}[{index}]', depth + 1))
        return [f'for (int {index} = 0; {index} < {type_node.size}; {index}++) {{ {inner} }}']

    def set_code(self, type_node, lvalue: str, value_code: str) -> str:
        """C statement replacing a stored managed value, freeing the old one."""
        if isinstance(type_node, PrimitiveType):
            return f'fusion_str_set(&{lvalue}, {value_code});'
        return f'fusion_set_{self._struct_c_name(type_node)}(&{lvalue}, {value_code});'

    # ------------------------------------------------------------------ struct helpers

    def struct_helper_lines(self, ordered_structs) -> list:
        """Copy / free / set helpers for every struct holding a string somewhere, in
        dependency order (a struct's helpers call its fields' helpers)."""
        lines = []
        for struct in ordered_structs:
            struct_type = StructType(location=struct.location, name=struct.name, declaration=struct)
            if not self.is_managed(struct_type):
                continue
            c = self._struct_c_name(struct_type)
            copy_body, free_body = [], []
            for field in struct.fields:
                if not self.is_managed(field.field_type):
                    continue
                name = f'v.{self._field_name(field.name)}'
                field_type = field.field_type
                if isinstance(field_type, ArrayType):
                    element = field_type.element_type
                    copy_body.append(
                        f'    for (int i = 0; i < {field_type.size}; i++) '
                        f'{name}[i] = {self.copy_code(element, f"{name}[i]")};')
                else:
                    copy_body.append(f'    {name} = {self.copy_code(field_type, name)};')
                free_body += ['    ' + line for line in self.free_lines(
                    field_type, f'v->{self._field_name(field.name)}')]
            lines += [f'static inline {c} fusion_copy_{c}({c} v) {{'] + copy_body + \
                     ['    return v;', '}',
                      f'static inline void fusion_free_{c}({c}* v) {{'] + free_body + ['}',
                      f'static inline void fusion_set_{c}({c}* dst, {c} value) {{ '
                      f'fusion_free_{c}(dst); *dst = value; }}']
        return lines

    # ------------------------------------------------------------------ ownership of values

    def is_fresh(self, expr) -> bool:
        """True for an expression whose managed value is newly made and owned by nobody
        yet: a call returning a managed value (including a constructor and the string
        built-ins), or joining strings with `+` (18.3.2). Storing it takes it over;
        otherwise it's freed at the end of the statement."""
        if isinstance(expr, BinaryExpr):
            return expr.operator == '+' and self.is_managed(getattr(expr, 'inferred_type', None))
        return isinstance(expr, CallExpr) and self.is_managed(getattr(expr, 'inferred_type', None))

    def owned_value(self, expr, type_node) -> str:
        """C code for a value that's about to be stored somewhere that owns it."""
        if not self.is_managed(type_node):
            return self.visit(expr)
        if isinstance(expr, LiteralExpr):
            return self.visit(expr)  # source text - never freed, safe to store
        if isinstance(expr, ArrayLiteralExpr):
            element = type_node.element_type
            return '{' + ', '.join(self.owned_value(e, element) for e in expr.elements) + '}'
        if self.is_fresh(expr):
            self.consumed.add(id(expr))
            return self.visit(expr)
        return self.copy_code(type_node, self.visit(expr))

    # ------------------------------------------------------------------ statement temporaries

    def _declare_temp(self, prefix: str, c_type: str, initial: str = None) -> str:
        """A compiler temporary declared at the top of the current C function."""
        self.temp_count = getattr(self, 'temp_count', 0) + 1
        name = f'fusion_{prefix}_{self.temp_count}'
        init = f' = {initial}' if initial is not None else ''
        self.temp_scopes[-1].append(f'{c_type} {name}{init};')
        return name

    def fresh_temporary(self, code: str, type_node) -> str:
        """Hold a fresh managed value nobody takes over in a temporary, freed after the
        statement: `f(g())` where g returns a string."""
        if not getattr(self, 'temp_scopes', None) or not self.stmt_temps:
            return code
        # Every temporary starts as an empty value: in `a and f() == "x"` the call is
        # skipped when `a` is false, and freeing an empty value is harmless. (Freeing also
        # resets a value to empty, so a temporary reused by a loop stays safe too.)
        if isinstance(type_node, ArrayType):
            c_type = self.array_wrapper_name(type_node)
            initial = '{' + self._default_value_code(type_node) + '}'
        else:
            c_type = self.map_type(type_node)
            initial = self._default_value_code(type_node)
        name = self._declare_temp('tmp', f'{c_type}', initial)
        self.stmt_temps[-1].append((name, type_node))
        return f'({name} = {code})'

    def begin_statement(self) -> None:
        self.stmt_temps.append([])

    def end_statement(self) -> None:
        """Free the statement's temporaries and close it."""
        self.flush_temps()
        self.stmt_temps.pop()

    def has_pending_temps(self) -> bool:
        return bool(self.stmt_temps and self.stmt_temps[-1])

    def flush_temps(self) -> None:
        """Free the current statement's temporaries now (newest first) - e.g. after a
        loop condition is evaluated, before the loop body runs."""
        temps, self.stmt_temps[-1] = self.stmt_temps[-1], []
        for name, type_node in reversed(temps):
            if isinstance(type_node, ArrayType):
                self.emit(f'{self.array_wrapper_name(type_node)}_free(&{name});')
            else:
                for line in self.free_lines(type_node, name):
                    self.emit(line)

    # ------------------------------------------------------------------ cleanup scopes

    def push_scope(self, kind: str) -> None:
        self.cleanup_scopes.append({'kind': kind, 'vars': []})

    def pop_scope(self) -> None:
        """Leave a scope normally, freeing its owned variables (newest first)."""
        scope = self.cleanup_scopes.pop()
        for name, type_node in reversed(scope['vars']):
            for line in self.free_lines(type_node, name):
                self.emit(line)

    def register_owned(self, name: str, type_node, location=None) -> None:
        """Record a managed variable, to be freed when its scope ends."""
        if not self.is_managed(type_node) or not self.cleanup_scopes:
            return  # no enclosing function (only when a unit test drives codegen directly)
        for scope in reversed(self.cleanup_scopes):
            if any(existing == name for existing, _ in scope['vars']):
                raise NotImplementedError(
                    f"Variable '{name}' at {location} reuses the name of a string (or struct "
                    f"or array holding strings) in an enclosing block - not supported yet; "
                    f"choose another name"
                )
            if scope['kind'] == 'function':
                break
        self.cleanup_scopes[-1]['vars'].append((name, type_node))

    def owned_in_scopes(self, until: str) -> list:
        """Owned variables in the scopes being left - up to the function (return) or the
        innermost loop (break/continue) - innermost first."""
        found = []
        for scope in reversed(self.cleanup_scopes):
            if scope['kind'] == until:
                if until == 'function':
                    found += list(reversed(scope['vars']))
                break
            found += list(reversed(scope['vars']))
        return found

    def emit_frees(self, owned: list) -> None:
        for name, type_node in owned:
            for line in self.free_lines(type_node, name):
                self.emit(line)

    # ------------------------------------------------------------------ parameters

    @staticmethod
    def assigned_roots(body) -> set:
        """Names of the variables a function body assigns to (including through fields and
        indexes): `p.name = ...` assigns to `p`."""
        names = set()

        def walk(node):
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if isinstance(node, LambdaExpr) or not (is_dataclass(node) and isinstance(node, ASTNode)):
                return
            if isinstance(node, AssignmentStmt):
                root = node.target
                while isinstance(root, (MemberExpr, IndexExpr)):
                    root = root.object if isinstance(root, MemberExpr) else root.array
                if isinstance(root, IdentifierExpr):
                    names.add(root.name)
            for f in dataclass_fields(node):
                if f.name not in ('location', 'inferred_type', 'scope', 'declaration',
                                  'callee_declaration', 'resolved_arguments'):
                    walk(getattr(node, f.name))

        walk(body)
        return names
