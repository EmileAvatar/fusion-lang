"""C for error handling (Task 26).

No setjmp / longjmp - jumping over C frames would skip Fusion's automatic cleanup. Instead,
like Go, Zig or Rust's `?`, an error travels explicitly:

- a failing function sets the current error (`fusion_raise`) and returns a default value
- right after each call that can fail, the generated C checks `fusion_failed` - inside a
  GCC statement expression, so the check sits exactly after the call, in evaluation order:

      x = __extension__ ({ int fusion_r = fu_parse(s); if (fusion_failed) goto fusion_fail_3; fusion_r; });

- each statement that has such a call gets a failure block after it, which frees the
  statement's temporaries and the values owned so far, then goes on to its target: return
  from the function (the error bubbles up), a capture (`T x, Error err = ...`), or (26.3) a
  catch. An error that reaches the end of main stops the program with its message

Which functions can fail is worked out first (failing_functions): one declared `T, Error`
or `Error function`, and - repeated until nothing changes - one calling a function that can
fail, or calling through a function value. Calls that can't fail get no check.
"""

from dataclasses import fields as dataclass_fields, is_dataclass

from src.parser.ast_nodes import (ArrayType, CallExpr, ErrorType, FunctionDecl, FunctionType,
                                  IdentifierExpr, LambdaExpr, PrimitiveType)

ERRORS_LIBRARY = r'''
// ---- Errors (Task 26) - an error travels in fusion_err while fusion_failed is set ----
typedef struct { int active; int code; fusion_string message; fusion_string where; } fusion_error;
static fusion_error fusion_err;
static int fusion_failed = 0;
static inline fusion_error fusion_error_make(fusion_string message, int code, fusion_string where) {
    fusion_error e; e.active = 1; e.code = code; e.message = message; e.where = where; return e;
}
static inline fusion_error fusion_error_copy(fusion_error e) {
    e.message = fusion_str_copy(e.message); e.where = fusion_str_copy(e.where); return e;
}
static inline void fusion_error_free(fusion_error* e) {
    fusion_str_free(&e->message); fusion_str_free(&e->where); e->active = 0; e->code = 0;
}
static inline void fusion_error_set(fusion_error* dst, fusion_error v) { fusion_error_free(dst); *dst = v; }
static inline const char* fusion_error_text(fusion_error e) { return e.message.data ? e.message.data : ""; }
// Start an error on its way (an Error holding none changes nothing)
static inline void fusion_raise(fusion_error e) {
    if (!e.active) { fusion_error_free(&e); return; }
    fusion_error_free(&fusion_err); fusion_err = e; fusion_failed = 1;
}
// Take the travelling error - it stops travelling (none: an Error holding none)
static inline fusion_error fusion_take_error(void) {
    fusion_error e = fusion_err; fusion_err = (fusion_error){0}; fusion_failed = 0; return e;
}
// An error nobody caught reached the end of main: stop, like a run-time error
static inline void fusion_uncaught(void) {
    fusion_error e = fusion_take_error();
    fflush(stdout);
    fprintf(stderr, "Error%s%s: %s\n", e.where.len ? " at " : "", e.where.len ? e.where.data : "",
            fusion_error_text(e));
    fusion_error_free(&e);
    exit(1);
}
'''


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
        if isinstance(node, CallExpr) and self.call_can_fail(node, failing):
            return True
        if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr):
            # walk only the arguments - the callee is a name, not a call
            return self._calls_failing(node.arguments, failing)
        return any(self._calls_failing(getattr(node, f.name), failing)
                   for f in dataclass_fields(node)
                   if f.name not in ('location', 'inferred_type', 'scope', 'declaration',
                                     'callee_declaration', 'resolved_arguments'))

    def call_can_fail(self, node: CallExpr, failing=None) -> bool:
        failing = self.failing_functions if failing is None else failing
        declaration = getattr(node, 'callee_declaration', None)
        if isinstance(declaration, FunctionDecl):
            return declaration.name in failing
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

    def checked_call(self, code: str, node: CallExpr) -> str:
        """A call that can fail, checked right after it runs."""
        label = self.fail_label()
        result = node.inferred_type
        if result is None or (isinstance(result, PrimitiveType) and result.name == 'void'):
            return f'__extension__ ({{ {code}; if (fusion_failed) goto {label}; }})'
        c_type = self.return_c_type(result)
        return (f'__extension__ ({{ {c_type} fusion_r = {code}; '
                f'if (fusion_failed) goto {label}; fusion_r; }})')

    # ------------------------------------------------------------------ Error values

    def visit_ErrorMakeExpr(self, node) -> str:
        string = PrimitiveType(location=node.location, name='string')
        message = self.owned_value(node.arguments[0], string)
        code = self.visit(node.arguments[1]) if len(node.arguments) > 1 else '0'
        made = f'fusion_error_make({message}, {code}, FUSION_STR({self._where(node)}))'
        if id(node) in getattr(self, 'consumed', set()):
            return made
        return self.fresh_temporary(made, node.inferred_type)

    def visit_ErrorActiveExpr(self, node) -> str:
        return f'(({self.visit(node.operand)}).active)'

    def raise_code(self, value) -> str:
        """`return Error(...)` in a function that can fail: start the error on its way."""
        return f'fusion_raise({self.owned_value(value, ErrorType(location=value.location))})'

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
