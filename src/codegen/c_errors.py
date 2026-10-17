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

from src.semantic.error_rules import BUILTIN_ERROR_NAMES, BUILTIN_ERROR_TYPES
from .c_names import array_length_name
from .c_runtime import escape_c_text
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
// err.kind - the name of the error's type, "FileError" (Task 26.10)
static inline fusion_string fusion_error_kind_text(fusion_error e) {
    const char* name = e.kind > 0 && fusion_error_kinds ? fusion_error_kinds[e.kind].name : "Error";
    int n = 0;
    while (name[n]) n++;
    fusion_string s = {(char*)name, n, n, 0};
    return s;
}
// A fixed-size array's index (Task 27.1): outside the array is an IndexError, and the
// element at 0 is used instead - the generated code jumps away before touching it
static inline int fusion_index(int i, int length, const char* where) {
    if (i < 0 || i >= length) {
        fusion_fail(FUSION_KIND_IndexError, where, "index %d is outside the array (length %d)", i, length);
        return 0;
    }
    return i;
}
// Whole-number division (Task 26.12): by zero is a DivideByZeroError, not a crash.
// -2147483648 / -1 doesn't fit: an OverflowError (27.2b), or it wraps when not checked
static inline int fusion_div_int(int a, int b, int check, const char* where) {
    if (b == 0) { fusion_fail(FUSION_KIND_DivideByZeroError, where, "%d / 0: division by zero", a); return 0; }
    if (b == -1) {
        if (check && a == -2147483647 - 1) {
            fusion_fail(FUSION_KIND_OverflowError, where, "%d / -1 doesn't fit in an int", a);
            return 0;
        }
        return (int)(0u - (unsigned)a);
    }
    return a / b;
}
static inline int fusion_mod_int(int a, int b, int check, const char* where) {
    (void)check;
    if (b == 0) { fusion_fail(FUSION_KIND_DivideByZeroError, where, "%d %% 0: division by zero", a); return 0; }
    if (b == -1) return 0;
    return a % b;
}
// Whole-number + - * (Task 27.2b, user decision 2026-10-17): a result that doesn't fit in an
// int is an OverflowError - never a silently changed value. GCC's overflow builtins compile
// to the operation and one jump
static inline int fusion_add_int(int a, int b, const char* where) {
    int r;
    if (__builtin_add_overflow(a, b, &r)) { fusion_fail(FUSION_KIND_OverflowError, where, "%d + %d doesn't fit in an int", a, b); return 0; }
    return r;
}
static inline int fusion_sub_int(int a, int b, const char* where) {
    int r;
    if (__builtin_sub_overflow(a, b, &r)) { fusion_fail(FUSION_KIND_OverflowError, where, "%d - %d doesn't fit in an int", a, b); return 0; }
    return r;
}
static inline int fusion_mul_int(int a, int b, const char* where) {
    int r;
    if (__builtin_mul_overflow(a, b, &r)) { fusion_fail(FUSION_KIND_OverflowError, where, "%d * %d doesn't fit in an int", a, b); return 0; }
    return r;
}
static inline int fusion_neg_int(int a, const char* where) {
    if (a == -2147483647 - 1) { fusion_fail(FUSION_KIND_OverflowError, where, "-(%d) doesn't fit in an int", a); return 0; }
    return -a;
}
// Wrapping around on purpose (wrapAdd ..., an unchecked block, unsafe mode - Task 27.2d):
// done on unsigned numbers, so it is defined - never C's undefined behaviour
static inline int fusion_wrap_add(int a, int b) { return (int)((unsigned)a + (unsigned)b); }
static inline int fusion_wrap_sub(int a, int b) { return (int)((unsigned)a - (unsigned)b); }
static inline int fusion_wrap_mul(int a, int b) { return (int)((unsigned)a * (unsigned)b); }
// An int used as a float (Task 27.2f): it must fit exactly - [numbers] auto_widening = false
static inline float fusion_int_to_float(int x, const char* where) {
    float f = (float)x;
    if ((double)f != (double)x) {
        fusion_fail(FUSION_KIND_PrecisionError, where, "%d can't be stored exactly in a float "
                    "(it would become %.0f) - use a double, or set [numbers] auto_widening = true",
                    x, (double)f);
    }
    return f;
}
// Two errors are equal when they are the same type with the same code and message
static inline bool fusion_error_eq(fusion_error a, fusion_error b) {
    return a.active == b.active && a.kind == b.kind && a.code == b.code && fusion_str_eq(a.message, b.message);
}
// Fusion's own error types (Task 26.12); main sets the table with the program's own types
static const fusion_error_kind fusion_builtin_kinds[] = {
/*FUSION_BUILTIN_KIND_ROWS*/};
static const fusion_error_kind* fusion_error_kinds = fusion_builtin_kinds;
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
static inline void fusion_raise_text(int kind, void* extra, const char* where, const char* text, int len) {
    fusion_error e = fusion_error_make_kind(fusion_error_string(text, len), 0, FUSION_STR(""), kind, extra);
    if (where) {
        int n = 0;
        while (where[n]) n++;
        e.where = fusion_error_string(where, n);
    }
    e.runtime = 1;
    fusion_raise(e);
}
// Fusion's FileError holds a path (Task 26.12) - its subtypes share this data
typedef struct fusion_errdata_fu_FileError { fusion_string path; } fusion_errdata_fu_FileError;
static inline void* fusion_errdata_fu_FileError_new(fusion_string path) {
    fusion_errdata_fu_FileError* d = (fusion_errdata_fu_FileError*)fusion_alloc(sizeof *d);
    d->path = path;
    return d;
}
static void* fusion_errdata_fu_FileError_copy(void* p) {
    fusion_errdata_fu_FileError* r = (fusion_errdata_fu_FileError*)fusion_alloc(sizeof *r);
    r->path = fusion_str_copy(((fusion_errdata_fu_FileError*)p)->path);
    return r;
}
static void fusion_errdata_fu_FileError_free(void* p) {
    fusion_str_free(&((fusion_errdata_fu_FileError*)p)->path);
    fusion_dealloc(p);
}
static inline fusion_errdata_fu_FileError* fusion_errdata_fu_FileError_of(fusion_error e) {
    static fusion_errdata_fu_FileError none = {{0}};
    if (e.extra && fusion_error_is(e.kind, FUSION_KIND_FileError)) return (fusion_errdata_fu_FileError*)e.extra;
    none.path = FUSION_STR("");
    return &none;
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


# The rows of Fusion's own error types in the table of error types (Task 26.12)
BUILTIN_KIND_ROWS = ['{"Error", -1, NULL, NULL}'] + [
    f'{{"{name}", {0 if parent == "Error" else BUILTIN_ERROR_NAMES.index(parent) + 1}, '
    + ('fusion_errdata_fu_FileError_copy, fusion_errdata_fu_FileError_free' if
       name == 'FileError' or parent == 'FileError' else 'NULL, NULL') + '}'
    for name, parent, _, _ in BUILTIN_ERROR_TYPES]

ERRORS_LIBRARY = ERRORS_LIBRARY.replace(
    '/*FUSION_BUILTIN_KIND_ROWS*/', ''.join(f'    {row},\n' for row in BUILTIN_KIND_ROWS))

# Their numbers, for the runtime: FUSION_KIND_IndexError ... (declared at its top)
BUILTIN_KIND_DEFINES = ''.join(f'#define FUSION_KIND_{name} {number}\n'
                               for number, name in enumerate(BUILTIN_ERROR_NAMES, 1))


class ErrorsMixin:
    """Error code generation; generate() sets failing_functions, fail_targets, fail_sites."""

    # ------------------------------------------------------------------ which calls can fail

    def find_recursive_functions(self, program) -> set:
        """The functions that can call themselves (Task 27.2c): those on a cycle of calls - a
        call through a function value counts as a call to every function used as a value."""
        functions = {d.name: d for d in program.declarations if isinstance(d, FunctionDecl)}
        as_values = set()
        calls = {name: set() for name in functions}

        def walk(node, owner, callee_ids):
            if isinstance(node, list):
                for item in node:
                    walk(item, owner, callee_ids)
                return
            if not is_dataclass(node) or isinstance(node, type):
                return
            if isinstance(node, CallExpr):
                callee_ids.add(id(node.callee))
                declaration = getattr(node, 'callee_declaration', None)
                if isinstance(declaration, FunctionDecl) and declaration.name in functions:
                    calls[owner].add(declaration.name)
                elif not isinstance(node.callee, IdentifierExpr) or \
                        isinstance(getattr(node.callee, 'inferred_type', None), FunctionType):
                    calls[owner].add('*values*')
            if isinstance(node, IdentifierExpr) and node.name in functions and id(node) not in callee_ids:
                as_values.add(node.name)
            for f in dataclass_fields(node):
                if f.name not in ('location', 'inferred_type', 'scope', 'declaration',
                                  'callee_declaration', 'resolved_arguments'):
                    walk(getattr(node, f.name), owner, callee_ids)

        for name, decl in functions.items():
            walk(decl.body, name, set())
        for name in calls:
            if '*values*' in calls[name]:
                calls[name] = (calls[name] - {'*values*'}) | as_values

        def reaches(start, target):
            seen, todo = set(), list(calls.get(start, ()))
            while todo:
                name = todo.pop()
                if name == target:
                    return True
                if name not in seen:
                    seen.add(name)
                    todo.extend(calls.get(name, ()))
            return False

        return {name for name in functions if name != 'main' and reaches(name, name)}

    def stack_check_lines(self, node) -> list:
        """At the start of a function that can call itself: a full stack is a
        StackOverflowError, not a crash (Task 27.2c)."""
        message = escape_c_text(f"{node.name.split('.')[-1]}() went too deep - the stack is "
                                f"full (does it call itself without end?)", '"')
        return [f'if (fusion_stack_low()) {{',
                f'    fusion_fail(FUSION_KIND_StackOverflowError, {self._where(node)}, "{message}");'] + \
               ['    ' + line for line in self._fail_action(self.fail_targets[0])] + ['}']

    def depth_wrapper_lines(self, node, c_name: str, body_name: str) -> list:
        """[safety] max_call_depth = a number: the function counts its calls (Task 27.2c)."""
        return_type = self.return_c_type(node.return_type)
        params = self._c_parameter_list(node.parameters)
        names = []
        for p in node.parameters:
            names.append(p.name)
            if isinstance(p.param_type, ArrayType) and p.param_type.size is None:
                names.append(array_length_name(p.name))
        call = f'{body_name}({", ".join(names)})'
        void = return_type == 'void'
        message = escape_c_text(f"{node.name.split('.')[-1]}() went past "
                                f"[safety] max_call_depth = {self.max_call_depth} calls", '"')
        lines = [f'{return_type} {c_name}({params}) {{',
                 f'    if (fusion_call_depth >= {self.max_call_depth}) {{',
                 f'        fusion_fail(FUSION_KIND_StackOverflowError, {self._where(node)}, "{message}");']
        lines += ['        ' + line for line in self._fail_action(
            self.function_fail_target(node.name, node.return_type))] + ['    }',
                 '    fusion_call_depth++;']
        if void:
            lines += [f'    {call};', '    fusion_call_depth--;', '}', '']
        else:
            lines += [f'    {return_type} fusion_result = {call};', '    fusion_call_depth--;',
                      '    return fusion_result;', '}', '']
        return lines

    def find_failing_functions(self, program) -> set:
        """The functions that can fail. A call through a function value can fail only when
        some function that can fail is used as a value, or some lambda can fail
        (self.value_calls_fail) - so programs without errors get no checks at all."""
        functions = [d for d in program.declarations if isinstance(d, FunctionDecl)]
        self.value_calls_fail = False
        # A function that can call itself can fail: a StackOverflowError (Task 27.2c)
        self.recursive_functions = self.find_recursive_functions(program)
        while True:
            failing = {f.name for f in functions if getattr(f, 'returns_error', False)} \
                | self.recursive_functions
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
        if type(node).__name__ == 'ForStmt' and isinstance(
                getattr(node.iterable, 'inferred_type', None), (ListType, MapType)) and \
                type(node.iterable).__name__ in ('IdentifierExpr', 'MemberExpr', 'IndexExpr'):
            return True    # the list may change while looping (Task 27.2e)
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
            return isinstance(kind, (ListType, MapType, ArrayType)) or (
                isinstance(kind, PrimitiveType) and kind.name in ('string', 'bytes'))
        if type(node).__name__ == 'WidenExpr':
            return True                     # an int that may not fit a float (27.2f)
        if type(node).__name__ == 'EnumStaticCall':
            return node.method == 'fromString'
        if isinstance(node, BinaryExpr) and self.int_division_can_fail(node):
            return True
        if type(node).__name__ in ('BinaryExpr', 'UnaryExpr') and node.operator in ('+', '-', '*') \
                and self.whole_number_operands(node) and not self.wraps(node) \
                and not self.constant_fits(node):
            return not (type(node).__name__ == 'UnaryExpr'
                        and type(node.operand).__name__ == 'LiteralExpr')   # -5 is just a number
        if isinstance(node, (BinaryExpr, InterpolatedStringExpr)):
            return self._makes_limited_string(node)
        return False

    def array_length_code(self, array):
        """C code for a fixed-size array's length: its size, or an `int[]` parameter's hidden
        length - None when unknown."""
        kind = getattr(array, 'inferred_type', None)
        if isinstance(kind, ArrayType) and kind.size is not None:
            return str(kind.size)
        if isinstance(array, IdentifierExpr):
            return array_length_name(array.name)
        return None

    def checked_array_index(self, node, index_code: str) -> str:
        """`a[i]` on a fixed-size array: i checked against its length (Task 27.1) - left as
        it is when i is a number written in the source and inside the array."""
        length = self.array_length_code(node.array)
        if length is None:
            return index_code
        index = node.index
        if type(index).__name__ == 'LiteralExpr' and isinstance(index.value, int) \
                and length.isdigit() and 0 <= index.value < int(length):
            return index_code
        return self.checked_code(f'fusion_index({index_code}, {length}, {self._where(node)})', 'int')

    def loop_change_check(self, now: str, before: str, iterable_type, node) -> str:
        """A for loop over a List / Map whose elements were added or removed meanwhile: a
        ModifiedWhileLoopingError (Task 27.2e, user decision 2026-10-17)."""
        what = 'Map' if isinstance(iterable_type, MapType) else 'List'
        change = 'a key was added or removed' if what == 'Map' else 'an element was added or removed'
        return (f'if ({now} != {before}) {{ fusion_fail(FUSION_KIND_ModifiedWhileLoopingError, '
                f'{self._where(node)}, "the {what} changed while a for loop went over it ({change} '
                f'inside the loop)"); goto {self.fail_label()}; }}')

    @staticmethod
    def whole_number_operands(node) -> bool:
        """int (or byte) arithmetic - its result is an int (Task 27.2b)."""
        whole = ('int', 'byte')
        operands = [node.operand] if type(node).__name__ == 'UnaryExpr' else [node.left, node.right]
        return all(getattr(getattr(o, 'inferred_type', None), 'name', None) in whole for o in operands)

    def wraps(self, node) -> bool:
        """Arithmetic that wraps around: unsafe mode, or inside an unchecked block."""
        return getattr(self, 'safety_mode', 'normal') == 'unsafe' or getattr(node, 'unchecked', False)

    @staticmethod
    def constant_value(node):
        """The value of whole-number arithmetic made only of numbers written in the source
        (60 * 60 * 24), or None."""
        kind = type(node).__name__
        if kind == 'LiteralExpr' and isinstance(node.value, int) and not isinstance(node.value, bool):
            return node.value
        if kind == 'UnaryExpr' and node.operator == '-':
            inner = ErrorsMixin.constant_value(node.operand)
            return None if inner is None else -inner
        if kind == 'BinaryExpr' and node.operator in ('+', '-', '*'):
            left = ErrorsMixin.constant_value(node.left)
            right = ErrorsMixin.constant_value(node.right)
            if left is None or right is None:
                return None
            return {'+': left + right, '-': left - right, '*': left * right}[node.operator]
        return None

    @staticmethod
    def constant_fits(node) -> bool:
        """Numbers written in the source whose result (and every step) fits - nothing to check."""
        if type(node).__name__ != 'BinaryExpr':
            return False
        value = ErrorsMixin.constant_value(node)
        if value is None:
            return False
        steps = [node]
        while steps:
            step = steps.pop()
            if type(step).__name__ == 'BinaryExpr':
                v = ErrorsMixin.constant_value(step)
                if v is None or not -2147483648 <= v <= 2147483647:
                    return False
                steps += [step.left, step.right]
        return True

    @staticmethod
    def int_division_can_fail(node) -> bool:
        """Whole numbers divided (/ or %) by something that may be zero (Task 26.12) - a
        written number other than 0 can't be."""
        if node.operator not in ('/', '%'):
            return False
        whole = ('int', 'byte')
        if getattr(getattr(node.left, 'inferred_type', None), 'name', None) not in whole or \
                getattr(getattr(node.right, 'inferred_type', None), 'name', None) not in whole:
            return False
        right = node.right
        return not (type(right).__name__ == 'LiteralExpr' and right.value not in (0, -1))

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

    # ------------------------------------------------------------------ error types (26.9, 26.12)

    def error_kind_number(self, decl) -> int:
        if decl is None:
            return 0
        if decl.builtin:
            return BUILTIN_ERROR_NAMES.index(decl.name) + 1
        return self.error_kinds[decl.name]

    @staticmethod
    def _data_decl(decl):
        """The error type whose struct holds decl's fields: the nearest in its line with
        fields of its own (a type adding none shares its parent's) - None when it has none."""
        for d in reversed(_chain(decl)):
            if d.fields:
                return d
        return None

    def _errdata(self, decl) -> str:
        return f'fusion_errdata_{self._mangle_function_name(decl.name)}'

    def _errfield_path(self, decl, field_owner, field) -> str:
        """Where a field sits in decl's data: a parent's fields are inside `base`."""
        holders = [d for d in _chain(self._data_decl(decl)) if d.fields]
        depth = len(holders) - 1 - holders.index(field_owner)
        return 'base.' * depth + self._field_name(field.name)

    def error_type_section_lines(self, program) -> list:
        """Per error type with fields of its own: a struct (the parent's data first, as
        `base`, so a subtype's data is also its parent's) and make / copy / free / read
        helpers - then the table of every error type, set as main starts. Fusion's own
        FileError data is in the runtime (c_errors ERRORS_LIBRARY)."""
        decls = [d for d in program.declarations if isinstance(d, ErrorDecl) and not d.builtin]
        self.error_kinds = {}
        ordered = []
        for decl in decls:
            for d in _chain(decl):
                if d not in ordered and not d.builtin:
                    ordered.append(d)
        for number, decl in enumerate(ordered, len(BUILTIN_ERROR_NAMES) + 1):
            self.error_kinds[decl.name] = number
        if not ordered:
            return []
        lines = ['// Error types (Task 26.9)']
        for decl in (d for d in ordered if d.fields):
            data, parent_data = self._errdata(decl), self._data_decl(decl.parent_declaration)
            lines.append(f'typedef struct {data} {{')
            if parent_data is not None:
                lines.append(f'    {self._errdata(parent_data)} base;')
            for f in decl.fields:
                lines.append(f'    {self.map_type(f.field_type)} {self._field_name(f.name)};')
            lines.append(f'}} {data};')
        for decl in (d for d in ordered if d.fields):
            lines += self._error_data_helpers(decl)
        lines.append('static const fusion_error_kind fusion_error_kind_table[] = {')
        lines += ['    ' + row + ',' for row in BUILTIN_KIND_ROWS]
        for decl in ordered:
            holder = self._data_decl(decl)
            functions = f'{self._errdata(holder)}_copy, {self._errdata(holder)}_free' \
                if holder is not None else 'NULL, NULL'
            # err.kind: the name as written, without the module (files.MyError -> MyError)
            lines.append(f'    {{"{decl.name.split(".")[-1]}", '
                         f'{self.error_kind_number(decl.parent_declaration)}, {functions}}},')
        lines += ['};', '']
        return lines

    def _error_data_helpers(self, decl) -> list:
        data, number = self._errdata(decl), self.error_kind_number(decl)
        fields = [(d, f) for d in _chain(decl) for f in d.fields]
        params = ', '.join(f'{self.map_type(f.field_type)} {self._field_name(f.name)}'
                           for _, f in fields) or 'void'
        lines = [f'static inline void* {data}_new({params}) {{',
                 f'    {data}* d = ({data}*)fusion_alloc(sizeof({data}));',
                 f'    memset(d, 0, sizeof({data}));']
        for owner, f in fields:
            lines.append(f'    d->{self._errfield_path(decl, owner, f)} = {self._field_name(f.name)};')
        lines += ['    return d;', '}',
                  f'static void* {data}_copy(void* p) {{',
                  f'    {data}* r = ({data}*)fusion_alloc(sizeof({data}));',
                  f'    *r = *({data}*)p;']
        for owner, f in fields:
            if self.is_managed(f.field_type):
                path = self._errfield_path(decl, owner, f)
                lines.append(f'    r->{path} = {self.copy_code(f.field_type, "r->" + path)};')
        lines += ['    return r;', '}',
                  f'static void {data}_free(void* p) {{',
                  f'    {data}* d = ({data}*)p;']
        for owner, f in fields:
            for line in self.free_lines(f.field_type, 'd->' + self._errfield_path(decl, owner, f)):
                lines.append('    ' + line)
        lines += ['    (void)d;', '    fusion_dealloc(p);', '}',
                  # Reading a field: from this type or a subtype - else the field's default
                  f'static inline {data}* {data}_of(fusion_error e) {{',
                  f'    static {data} none; static int ready = 0;',
                  f'    if (e.extra && fusion_error_is(e.kind, {number})) return ({data}*)e.extra;',
                  '    if (!ready) {',
                  '        memset(&none, 0, sizeof none);']
        for owner, f in fields:
            default = self.visit(f.default_value) if f.default_value is not None \
                else self._default_value_code(f.field_type)
            lines.append(f'        none.{self._errfield_path(decl, owner, f)} = {default};')
        lines += ['        ready = 1;', '    }', '    return &none;', '}']
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
            # An error type: its number, and its fields on the heap (Tasks 26.9, 26.12)
            fields = [f for d in _chain(decl) for f in d.fields]
            holder = self._data_decl(decl)
            data = ', '.join(self.owned_value(v, f.field_type) for v, f in zip(values[2:], fields))
            extra = f'{self._errdata(holder)}_new({data})' if holder is not None else 'NULL'
            made = (f'fusion_error_make_kind({message}, {code}, {where}, '
                    f'{self.error_kind_number(decl)}, {extra})')
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
        holder = self._data_decl(decl)
        return f'{self._errdata(holder)}_of({self.visit(node.object)})->{self._errfield_path(decl, owner, field)}'

    def visit_WidenExpr(self, node) -> str:
        """An int used as a float, checked to fit exactly (Task 27.2f)."""
        return self.checked_code(f'fusion_int_to_float({self.visit(node.operand)}, '
                                 f'{self._where(node)})', 'float')

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
        target = catch_label if node.catches else fin_label
        body_target = {'kind': 'try', 'label': target, 'scope_index': len(self.cleanup_scopes),
                       'temp_level': len(self.stmt_temps)}
        self.fail_targets.append(body_target)
        self.visit_in_c_block(node.body)
        self.fail_targets.pop()
        self.emit_line(f'goto {end_label}')
        # Only paths something can jump to are written (no unused labels)
        catch_used = bool(node.catches) and body_target.get('used')
        finally_used = not node.catches and body_target.get('used')

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
            # The first catch whose type matches the error takes it (Task 26.11)
            catches_all = False
            for clause in node.catches:
                decl = getattr(clause.error_type, 'declaration', None)
                if clause.error_type is None or decl is None:
                    catches_all = True
                    self.emit('{')
                else:
                    self.emit(f'if (fusion_error_is(fusion_err.kind, {self.error_kind_number(decl)})) {{')
                self.indent()
                self.push_scope('block')
                name = clause.name or f'fusion_caught_{n}'
                self.emit_line(f'fusion_error {name} = fusion_take_error()')
                self.register_owned(name, ErrorType(location=node.location), node.location)
                self.visit(clause.body)
                self.pop_scope()
                self.emit_line(f'goto {end_label}')
                self.dedent()
                self.emit('}')
                if catches_all:
                    break
            if finally_body is not None:
                self.fail_targets.pop()
                finally_used = finally_used or catch_target.get('used')
            if not catches_all:
                # No catch matched: the error goes on - through the finally, if there is one
                if finally_body is not None:
                    self.emit_line(f'goto {fin_label}')
                    finally_used = True
                else:
                    self.emit_line(f'goto {self.fail_label()}')
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
            self.visit_in_c_block(finally_body)
            self.emit_line(f'fusion_raise({saved}); {saved} = (fusion_error){{0}}')
            self.pop_scope()
            self.emit_line(f'goto {self.fail_label()}')
            self.dedent()
            self.emit('}')
        self.emit(f'{end_label}:;')
        if finally_body is not None:
            self.visit_in_c_block(finally_body)
        return ''

    def visit_ThrowStmt(self, node) -> str:
        self.emit_line(f'fusion_raise({self.owned_value(node.value, ErrorType(location=node.location))})')
        if isinstance(node.value, ErrorMakeExpr):
            self.emit_line(f'goto {self.fail_label()}')        # always an error
        else:
            self.emit_line(f'if (fusion_failed) goto {self.fail_label()}')   # err may hold none
        return ''

    def visit_in_c_block(self, block) -> None:
        """A block in braces of its own: names declared inside don't clash with a sibling
        block's in C (`try` after `try`, a finally copied in twice)."""
        self.emit('{')
        self.indent()
        self.visit(block)
        self.dedent()
        self.emit('}')

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
                self.visit_in_c_block(entry['body'])
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
