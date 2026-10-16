"""C for error handling (Task 26).

No setjmp / longjmp - jumping over C frames would skip Fusion's automatic cleanup. Instead,
like Go, Zig or Rust's `?`, an error travels explicitly:

- a failing function sets the current error (`fusion_raise`) and returns a default value
- right after each call that can fail, the generated C checks `fusion_failed` - inside a
  GCC statement expression, so the check sits exactly after the call, in evaluation order:

      x = __extension__ ({ int fusion_r = fu_parse(s); if (fusion_failed) goto fusion_fail_3; fusion_r; });

- each statement that has such a call gets a failure block after it, which frees the
  statement's temporaries and the values owned so far, then goes on to its target: return
  from the function (the error bubbles up), a capture (`T x, Error err = ...`), or a
  try's catch. An error that reaches the end of main stops the program with its message

try / catch / finally (26.3):

      <body>                         errors go to fusion_catch_N (or fusion_finerr_N)
      goto fusion_tryend_N;
      if (0) { fusion_catch_N: fusion_error err = fusion_take_error(); <catch>; goto fusion_tryend_N; }
      if (0) { fusion_finerr_N: saved = fusion_take_error(); <finally>; fusion_raise(saved); goto <outer>; }
      fusion_tryend_N:; <finally>

  and a return / break / continue leaving the try runs a copy of the finally first.

Which functions can fail is worked out first (failing_functions): one declared `T, Error`
or `Error function`, and - repeated until nothing changes - one calling a function that can
fail, or calling through a function value. Calls that can't fail get no check.

Built-ins (26.4): every run-time error is an Error too. A runtime C function takes a
`where` argument exactly when it can report one - so those calls, s[i] / xs[i] / m[k] /
b[i], element writes and Enum.fromString are checked the same way. (With [strings]
max_length set, every expression making a string can fail.)
"""

from dataclasses import fields as dataclass_fields, is_dataclass

from src.parser.ast_nodes import (ArrayType, BinaryExpr, CallExpr, ErrorDecl, ErrorMakeExpr, ErrorType,
                                  FunctionDecl, FunctionType, IdentifierExpr, IndexExpr,
                                  InterpolatedStringExpr, LambdaExpr, ListType, MapType,
                                  PrimitiveType, ThrowStmt)

# List methods whose C function takes `where` - they report errors (Task 26.4)
_FAILING_LIST_METHODS = ('insert', 'removeAt', 'slice')
# List methods that call a function given to them - it may fail
_CALLING_LIST_METHODS = ('sortBy', 'filter', 'map', 'reduce')

ERRORS_LIBRARY = r'''
// ---- Errors (Task 26) - an error travels in fusion_err while fusion_failed is set ----
// (fusion_error, fusion_err and fusion_failed are declared at the top of the runtime)
static inline fusion_error fusion_error_make_kind(fusion_string message, int code, fusion_string where,
                                                int kind, void* extra) {
    fusion_error e; e.active = 1; e.code = code; e.message = message; e.where = where; e.runtime = 0;
    e.kind = kind; e.extra = extra;
    return e;
}
static inline fusion_error fusion_error_make(fusion_string message, int code, fusion_string where) {
    return fusion_error_make_kind(message, code, where, 0, NULL);
}
static inline fusion_error fusion_error_copy(fusion_error e) {
    e.message = fusion_str_copy(e.message); e.where = fusion_str_copy(e.where);
    if (e.extra) e.extra = fusion_error_kinds[e.kind].copy(e.extra);
    return e;
}
static inline void fusion_error_free(fusion_error* e) {
    fusion_str_free(&e->message); fusion_str_free(&e->where); e->active = 0; e->code = 0;
    if (e->extra) fusion_error_kinds[e->kind].free(e->extra);
    e->extra = NULL; e->kind = 0;
}
// Two errors are equal when they are the same type with the same code and message
static inline bool fusion_error_eq(fusion_error a, fusion_error b) {
    return a.active == b.active && a.kind == b.kind && a.code == b.code && fusion_str_eq(a.message, b.message);
}
// Is an error of type `kind` a `target` (that type or one of its subtypes)? (Task 26.9)
static inline int fusion_error_is(int kind, int target) {
    while (kind > 0) {
        if (kind == target) return 1;
        kind = fusion_error_kinds ? fusion_error_kinds[kind].parent : 0;
    }
    return kind == target;
}
static inline void fusion_error_set(fusion_error* dst, fusion_error v) { fusion_error_free(dst); *dst = v; }
static inline const char* fusion_error_text(fusion_error e) { return e.message.data ? e.message.data : ""; }
// Start an error on its way (an Error holding none changes nothing)
static inline void fusion_raise(fusion_error e) {
    if (!e.active || fusion_failed) { fusion_error_free(&e); return; }   // the first one travels
    fusion_error_free(&fusion_err); fusion_err = e; fusion_failed = 1;
}
// A run-time error (fusion_runtime_error): its text, and where it happened
static inline fusion_string fusion_error_string(const char* text, int len) {
    // Built directly - an error's own text is never held to [strings] max_length
    fusion_string r;
    r.data = (char*)fusion_alloc((size_t)len + 1);
    if (len > 0) memcpy(r.data, text, (size_t)len);
    r.data[len] = '\0'; r.len = len; r.chars = fusion_utf8_count(text, len); r.owned = 1;
    return r;
}
static inline void fusion_raise_text(const char* where, const char* text, int len) {
    fusion_error e = fusion_error_make(fusion_error_string(text, len), 0, FUSION_STR(""));
    if (where) {
        int n = 0;
        while (where[n]) n++;
        e.where = fusion_error_string(where, n);
    }
    e.runtime = 1;
    fusion_raise(e);
}
// Take the travelling error - it stops travelling (none: an Error holding none)
static inline fusion_error fusion_take_error(void) {
    fusion_error e = fusion_err; fusion_err = (fusion_error){0}; fusion_failed = 0; return e;
}
// An error nobody caught reached the end of main: stop, like a run-time error
static inline void fusion_uncaught(void) {
    fusion_error e = fusion_take_error();
    fflush(stdout);
    fprintf(stderr, "%s%s%s: %s\n", e.runtime ? "Runtime error" : "Error", e.where.len ? " at " : "",
            e.where.len ? e.where.data : "", fusion_error_text(e));
    fusion_error_free(&e);
    exit(1);
}
'''


def _chain(decl) -> list:
    chain = []
    while decl is not None and decl not in chain:
        chain.insert(0, decl)
        decl = decl.parent_declaration
    return chain


class ErrorsMixin:
    """Error code generation; generate() sets failing_functions, fail_targets, fail_sites."""

    # ------------------------------------------------------------------ which calls can fail

    def find_failing_functions(self, program) -> set:
        """The functions that can fail. A call through a function value can fail only when
        some function that can fail is used as a value, or some lambda can fail
        (self.value_calls_fail) - so programs without errors get no checks at all."""
        functions = [d for d in program.declarations if isinstance(d, FunctionDecl)]
        self.value_calls_fail = False
        while True:
            failing = {f.name for f in functions if getattr(f, 'returns_error', False)}
            changed = True
            while changed:
                changed = False
                for f in functions:
                    if f.name not in failing and self._calls_failing(f.body, failing):
                        failing.add(f.name)
                        changed = True
            values_fail = self._failing_values(program.declarations, failing)
            if values_fail == self.value_calls_fail:
                return failing
            self.value_calls_fail = values_fail

    def _failing_values(self, declarations, failing) -> bool:
        callees, found = set(), [False]

        def walk(node):
            if found[0] or isinstance(node, type):
                return
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if not is_dataclass(node):
                return
            if isinstance(node, CallExpr):
                callees.add(id(node.callee))
            if isinstance(node, IdentifierExpr) and node.name in failing and id(node) not in callees:
                found[0] = True       # a function that can fail, used as a value
                return
            if isinstance(node, LambdaExpr) and self._calls_failing(node.body, failing):
                found[0] = True       # a lambda that can fail
                return
            for f in dataclass_fields(node):
                if f.name not in ('location', 'inferred_type', 'scope', 'declaration',
                                  'callee_declaration', 'resolved_arguments'):
                    walk(getattr(node, f.name))

        walk([d.body for d in declarations if isinstance(d, FunctionDecl)])
        return found[0]

    def _calls_failing(self, node, failing) -> bool:
        if isinstance(node, list):
            return any(self._calls_failing(item, failing) for item in node)
        if not is_dataclass(node) or isinstance(node, type) or isinstance(node, LambdaExpr):
            return False   # a lambda is its own function
        if self.expr_can_fail(node, failing):
            return True
        if isinstance(node, ThrowStmt) or getattr(node, 'raises', False):
            return True    # throw, or `return Error(...)` in any function (Task 26.7)
        if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr):
            # walk only the arguments - the callee is a name, not a call
            return self._calls_failing(node.arguments, failing)
        return any(self._calls_failing(getattr(node, f.name), failing)
                   for f in dataclass_fields(node)
                   if f.name not in ('location', 'inferred_type', 'scope', 'declaration',
                                     'callee_declaration', 'resolved_arguments'))

    def expr_can_fail(self, node, failing=None) -> bool:
        """True for an expression that can raise an error (Task 26.4)."""
        if isinstance(node, CallExpr):
            return self.call_can_fail(node, failing)
        if isinstance(node, IndexExpr):
            kind = getattr(node.array, 'inferred_type', None)
            return isinstance(kind, (ListType, MapType)) or (
                isinstance(kind, PrimitiveType) and kind.name in ('string', 'bytes'))
        if type(node).__name__ == 'EnumStaticCall':
            return node.method == 'fromString'
        if isinstance(node, (BinaryExpr, InterpolatedStringExpr)):
            return self._makes_limited_string(node)
        return False

    def _makes_limited_string(self, node) -> bool:
        """With [strings] max_length set, a new string can be too long."""
        kind = getattr(node, 'inferred_type', None)
        return getattr(self, 'max_length', None) is not None and isinstance(kind, PrimitiveType) \
            and kind.name == 'string' and (not isinstance(node, BinaryExpr) or node.operator == '+')

    def call_can_fail(self, node: CallExpr, failing=None) -> bool:
        failing = self.failing_functions if failing is None else failing
        declaration = getattr(node, 'callee_declaration', None)
        if isinstance(declaration, FunctionDecl):
            return declaration.name in failing
        list_method = getattr(node, 'list_method', None)
        if list_method in _FAILING_LIST_METHODS:
            return True
        if list_method in _CALLING_LIST_METHODS:
            return getattr(self, 'value_calls_fail', True)
        if list_method is not None or getattr(node, 'map_method', None):
            return False
        if isinstance(node.callee, IdentifierExpr) and node.callee.name in self._STRING_BUILTINS \
                and not isinstance(getattr(node.callee, 'inferred_type', None), FunctionType):
            name = node.callee.name
            arguments = node.resolved_arguments or node.arguments
            if name == 'toString' and arguments and self._is_bytes(arguments[0]):
                return True                       # bytes that aren't valid text
            return self._STRING_BUILTINS[name][1] or self._makes_limited_string(node)
        if not isinstance(node.callee, IdentifierExpr) or \
                isinstance(getattr(node.callee, 'inferred_type', None), FunctionType):
            # A call through a function value - it may be a function that fails
            return getattr(self, 'value_calls_fail', True)
        return False

    # ------------------------------------------------------------------ failure targets and sites

    def function_fail_target(self, name: str, return_type) -> dict:
        return {'kind': 'function', 'main': name == 'main', 'return_type': return_type,
                'scope_index': len(self.cleanup_scopes) - 1, 'temp_level': 0}

    def open_fail_site(self) -> dict:
        site = {'label': None, 'target': None, 'temps': self.stmt_temps[-1],
                'owned': [len(scope['vars']) for scope in self.cleanup_scopes]}
        self.fail_sites.append(site)
        return site

    def fail_label(self) -> str:
        """The label a failing call in the current statement jumps to."""
        site = self.fail_sites[-1]
        if site['label'] is None:
            self.fail_count = getattr(self, 'fail_count', 0) + 1
            site['label'] = f'fusion_fail_{self.fail_count}'
            site['target'] = self.fail_targets[-1]
            site['target']['used'] = True     # a try's catch / finally path is needed
        return site['label']

    def close_fail_site(self, site: dict) -> None:
        """The statement's failure block: free what it and the code before it hold, then
        go on to the target."""
        self.fail_sites.pop()
        if site['label'] is None:
            return
        target = site['target']
        self.emit('if (0) {')
        self.indent()
        self.emit(f'{site["label"]}:;')
        for temps in self.stmt_temps[target['temp_level']:] + [site['temps']]:
            for name, type_node in temps:
                for line in self.free_lines(type_node, name):
                    self.emit(line)
        for index in range(len(site['owned']) - 1, target['scope_index'] - 1, -1):
            for name, type_node in reversed(self.cleanup_scopes[index]['vars'][:site['owned'][index]]):
                for line in self.free_lines(type_node, name):
                    self.emit(line)
        for line in self._fail_action(target):
            self.emit(line)
        self.dedent()
        self.emit('}')

    def _fail_action(self, target: dict) -> list:
        if target['kind'] != 'function':
            return [f'goto {target["label"]};']
        if target['main']:
            return ['fusion_uncaught();', 'return 1;']
        return_type = target['return_type']
        if return_type is None or (isinstance(return_type, PrimitiveType) and return_type.name == 'void'):
            return ['return;']
        if isinstance(return_type, ArrayType):
            wrapper = self.array_wrapper_name(return_type)
            return [f'return ({wrapper}){{{self._default_value_code(return_type)}}};']
        return [f'return {self._default_value_code(return_type)};']

    def checked_call(self, code: str, node) -> str:
        """A call (or another expression) that can fail, checked right after it runs."""
        result = node.inferred_type
        if result is None or (isinstance(result, PrimitiveType) and result.name == 'void'):
            return self.checked_code(code, None)
        # A new value a failed call still handed back is freed before the error goes on
        free = ' '.join(self.free_lines(result, 'fusion_r')) \
            if not isinstance(result, ArrayType) and self.is_fresh(node) else ''
        return self.checked_code(code, self.return_c_type(result), free)

    def checked_code(self, code: str, c_type, free: str = '') -> str:
        """`code` with a check right after it - c_type is its C type, None for no value;
        `free` frees fusion_r when it fails."""
        if not getattr(self, 'fail_sites', None):
            return code     # not inside a statement (nothing can fail there)
        label = self.fail_label()
        if c_type is None:
            return f'__extension__ ({{ {code}; if (fusion_failed) goto {label}; }})'
        on_fail = f'{{ {free} goto {label}; }}' if free else f'goto {label};'
        return (f'__extension__ ({{ {c_type} fusion_r = {code}; '
                f'if (fusion_failed) {on_fail} fusion_r; }})')

    # ------------------------------------------------------------------ custom error types (26.9)

    def error_kind_number(self, decl) -> int:
        return 0 if decl is None else self.error_kinds[decl.name]

    def _errdata(self, decl) -> str:
        return f'fusion_errdata_{self._mangle_function_name(decl.name)}'

    def _errfield_path(self, decl, field_owner, field) -> str:
        """Where a field sits in decl's data: a parent's fields are inside `base`."""
        chain = _chain(decl)
        depth = len(chain) - 1 - chain.index(field_owner)
        return 'base.' * depth + self._field_name(field.name)

    def error_type_section_lines(self, program) -> list:
        """Per custom error type: its fields' struct (a parent's struct first, as `base`, so
        a subtype's data is also its parent's), make / copy / free / read helpers - and the
        table of every error type, set as main starts."""
        decls = [d for d in program.declarations if isinstance(d, ErrorDecl)]
        self.error_kinds = {}
        if not decls:
            return []
        ordered = []
        for decl in decls:
            for d in _chain(decl):
                if d not in ordered:
                    ordered.append(d)
        for number, decl in enumerate(ordered, 1):
            self.error_kinds[decl.name] = number
        lines = ['// Error types (Task 26.9)']
        for decl in ordered:
            data = self._errdata(decl)
            lines.append(f'typedef struct {data} {{')
            if decl.parent_declaration is not None:
                lines.append(f'    {self._errdata(decl.parent_declaration)} base;')
            for f in decl.fields:
                lines.append(f'    {self.map_type(f.field_type)} {self._field_name(f.name)};')
            if decl.parent_declaration is None and not decl.fields:
                lines.append('    char fusion_none;')
            lines.append(f'}} {data};')
        for decl in ordered:
            data, number = self._errdata(decl), self.error_kinds[decl.name]
            fields = [(d, f) for d in _chain(decl) for f in d.fields]
            params = ', '.join(f'{self.map_type(f.field_type)} {self._field_name(f.name)}'
                               for _, f in fields) or 'void'
            lines.append(f'static inline void* {data}_new({params}) {{')
            lines.append(f'    {data}* d = ({data}*)fusion_alloc(sizeof({data}));')
            lines.append(f'    memset(d, 0, sizeof({data}));')
            for owner, f in fields:
                lines.append(f'    d->{self._errfield_path(decl, owner, f)} = {self._field_name(f.name)};')
            lines += ['    return d;', '}']
            lines.append(f'static void* {data}_copy(void* p) {{')
            lines.append(f'    {data}* r = ({data}*)fusion_alloc(sizeof({data}));')
            lines.append(f'    *r = *({data}*)p;')
            for owner, f in fields:
                if self.is_managed(f.field_type):
                    path = self._errfield_path(decl, owner, f)
                    lines.append(f'    r->{path} = {self.copy_code(f.field_type, "r->" + path)};')
            lines += ['    return r;', '}']
            lines.append(f'static void {data}_free(void* p) {{')
            lines.append(f'    {data}* d = ({data}*)p;')
            for owner, f in fields:
                for line in self.free_lines(f.field_type, 'd->' + self._errfield_path(decl, owner, f)):
                    lines.append('    ' + line)
            lines += ['    (void)d;', '    fusion_dealloc(p);', '}']
            # Reading a field: from this type or a subtype - else the field's default
            lines.append(f'static inline {data}* {data}_of(fusion_error e) {{')
            lines.append(f'    static {data} none; static int ready = 0;')
            lines.append(f'    if (e.extra && fusion_error_is(e.kind, {number})) return ({data}*)e.extra;')
            lines.append('    if (!ready) {')
            lines.append('        memset(&none, 0, sizeof none);')
            for owner, f in fields:
                default = self.visit(f.default_value) if f.default_value is not None \
                    else self._default_value_code(f.field_type)
                lines.append(f'        none.{self._errfield_path(decl, owner, f)} = {default};')
            lines += ['        ready = 1;', '    }', '    return &none;', '}']
        lines.append('static const fusion_error_kind fusion_error_kind_table[] = {')
        lines.append('    {"Error", -1, NULL, NULL},')
        for decl in ordered:
            data = self._errdata(decl)
            lines.append(f'    {{"{decl.name}", {self.error_kind_number(decl.parent_declaration)}, '
                         f'{data}_copy, {data}_free}},')
        lines += ['};', '']
        return lines

    # ------------------------------------------------------------------ Error values

    def visit_ErrorMakeExpr(self, node) -> str:
        string = PrimitiveType(location=node.location, name='string')
        values = list(node.resolved_arguments or node.arguments)
        message = self.owned_value(values[0], string)
        code = self.visit(values[1]) if len(values) > 1 and values[1] is not None else '0'
        where = f'FUSION_STR({self._where(node)})'
        decl = node.declaration
        if decl is None:
            made = f'fusion_error_make({message}, {code}, {where})'
        else:
            # A custom error type: its number, and its fields on the heap (Task 26.9)
            fields = [f for d in _chain(decl) for f in d.fields]
            data = ', '.join(self.owned_value(v, f.field_type) for v, f in zip(values[2:], fields))
            made = (f'fusion_error_make_kind({message}, {code}, {where}, '
                    f'{self.error_kind_number(decl)}, {self._errdata(decl)}_new({data}))')
        if id(node) in getattr(self, 'consumed', set()):
            return made
        return self.fresh_temporary(made, node.inferred_type)

    def error_field_code(self, node) -> str:
        """err.path - a custom error type's field (read only); the field's default when the
        error held is another type (Task 26.9)."""
        error_type = node.object.inferred_type
        decl = error_type.declaration
        owner = next(d for d in reversed(_chain(decl)) if any(f.name == node.member for f in d.fields))
        field = next(f for f in owner.fields if f.name == node.member)
        return f'{self._errdata(decl)}_of({self.visit(node.object)})->{self._errfield_path(decl, owner, field)}'

    def visit_ErrorActiveExpr(self, node) -> str:
        return f'(({self.visit(node.operand)}).active)'

    def raise_code(self, value) -> str:
        """`return Error(...)` in a function that can fail: start the error on its way."""
        return f'fusion_raise({self.owned_value(value, ErrorType(location=value.location))})'

    # ------------------------------------------------------------------ try / catch / finally

    def _loop_count(self) -> int:
        return sum(1 for scope in self.cleanup_scopes if scope['kind'] == 'loop')

    def visit_TryStmt(self, node) -> str:
        self.fail_count = getattr(self, 'fail_count', 0) + 1
        n = self.fail_count
        catch_label, fin_label, end_label = f'fusion_catch_{n}', f'fusion_finerr_{n}', f'fusion_tryend_{n}'
        finally_body = node.finally_body
        if finally_body is not None:
            self.finally_stack.append({'body': finally_body, 'loops': self._loop_count(),
                                       'targets': len(self.fail_targets)})
        target = catch_label if node.catch_body is not None else fin_label
        body_target = {'kind': 'try', 'label': target, 'scope_index': len(self.cleanup_scopes),
                       'temp_level': len(self.stmt_temps)}
        self.fail_targets.append(body_target)
        self.visit(node.body)
        self.fail_targets.pop()
        self.emit_line(f'goto {end_label}')
        # Only paths something can jump to are written (no unused labels)
        catch_used = node.catch_body is not None and body_target.get('used')
        finally_used = node.catch_body is None and body_target.get('used')

        if catch_used:
            self.emit('if (0) {')
            self.indent()
            self.emit(f'{catch_label}:;')
            catch_target = {'kind': 'try', 'label': fin_label,
                            'scope_index': len(self.cleanup_scopes),
                            'temp_level': len(self.stmt_temps)}
            if finally_body is not None:
                # An error in the catch still runs the finally
                self.fail_targets.append(catch_target)
            self.push_scope('block')
            name = node.catch_name or f'fusion_caught_{n}'
            self.emit_line(f'fusion_error {name} = fusion_take_error()')
            self.register_owned(name, ErrorType(location=node.location), node.location)
            self.visit(node.catch_body)
            self.pop_scope()
            if finally_body is not None:
                self.fail_targets.pop()
                finally_used = finally_used or catch_target.get('used')
            self.emit_line(f'goto {end_label}')
            self.dedent()
            self.emit('}')

        if finally_body is not None:
            self.finally_stack.pop()
        if finally_used:
            # An error passing through: run the finally, then send the error on
            self.emit('if (0) {')
            self.indent()
            self.emit(f'{fin_label}:;')
            self.push_scope('block')
            saved = f'fusion_saved_{n}'
            self.emit_line(f'fusion_error {saved} = fusion_take_error()')
            self.register_owned(saved, ErrorType(location=node.location), node.location)
            self.visit(finally_body)
            self.emit_line(f'fusion_raise({saved}); {saved} = (fusion_error){{0}}')
            self.pop_scope()
            self.emit_line(f'goto {self.fail_label()}')
            self.dedent()
            self.emit('}')
        self.emit(f'{end_label}:;')
        if finally_body is not None:
            self.visit(finally_body)
        return ''

    def visit_ThrowStmt(self, node) -> str:
        self.emit_line(f'fusion_raise({self.owned_value(node.value, ErrorType(location=node.location))})')
        if isinstance(node.value, ErrorMakeExpr):
            self.emit_line(f'goto {self.fail_label()}')        # always an error
        else:
            self.emit_line(f'if (fusion_failed) goto {self.fail_label()}')   # err may hold none
        return ''

    def emit_finally_for_exit(self, leaving: str, error_pending: bool = False) -> None:
        """Before a return (leaving 'function') or a break / continue (leaving 'loop'):
        run the finally of every try being left, innermost first. While one runs, it is no
        longer "being left", and errors in it go to the targets outside its try."""
        if not getattr(self, 'finally_stack', None):
            return
        loops = self._loop_count()
        entries = [e for e in self.finally_stack if leaving == 'function' or e['loops'] == loops]
        if not entries:
            return
        saved_stack, saved_targets = self.finally_stack, self.fail_targets
        holder = None
        if error_pending:
            self.fail_count = getattr(self, 'fail_count', 0) + 1
            holder = f'fusion_pending_{self.fail_count}'
            self.emit_line(f'fusion_error {holder} = fusion_take_error()')
        try:
            for entry in reversed(entries):
                index = saved_stack.index(entry)
                self.finally_stack = saved_stack[:index]
                self.fail_targets = saved_targets[:entry['targets']]
                self.visit(entry['body'])
        finally:
            self.finally_stack, self.fail_targets = saved_stack, saved_targets
        if holder:
            self.emit_line(f'fusion_raise({holder})')

    # ------------------------------------------------------------------ capturing

    def capture_declaration(self, node) -> None:
        """`Ship s, Error err = loadShip(f)` / `Error e = save(s)`: any error the right side
        raises is taken into the Error variable instead of travelling on."""
        self.fail_count = getattr(self, 'fail_count', 0) + 1
        label = f'fusion_cap_{self.fail_count}'
        error_type = ErrorType(location=node.location)
        capture_only = getattr(node, 'capture_only', False)
        error_name = node.name if capture_only else node.error_name
        if not capture_only:
            self.emit_line(f'{self.map_type(node.var_type)} {node.name} = '
                           f'{self._default_value_code(node.var_type)}')
        self.emit_line(f'fusion_error {error_name} = ((fusion_error){{0}})')
        self.fail_targets.append({'kind': 'capture', 'label': label,
                                  'scope_index': len(self.cleanup_scopes),
                                  'temp_level': len(self.stmt_temps)})
        try:
            if capture_only:
                code = self.visit(node.initializer)
                if code:
                    self.emit_line(f'(void)({code})' if not code.startswith('__extension__') else code)
            else:
                self.emit_line(f'{node.name} = {self.owned_value(node.initializer, node.var_type)}')
        finally:
            self.fail_targets.pop()
        self.emit(f'if (0) {{ {label}: {error_name} = fusion_take_error(); }}')
        if not capture_only:
            self.register_owned(error_name, error_type, node.location)
