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
    BinaryExpr, InterpolatedStringExpr,
    ArrayLiteralExpr, LambdaExpr, PrimitiveType, ArrayType, StructType, StructDecl, ListType, MapType, NewCollectionExpr,
    ConditionalExpr,
)
from .c_names import mangle_function_name
from .c_strings import STRING_LIBRARY
from .c_bytes import BYTES_LIBRARY
from .c_files import FILES_LIBRARY
from .c_errors import ERRORS_LIBRARY, BUILTIN_KIND_DEFINES
from ..semantic.collection_rules import MUTATING_LIST_METHODS
from ..semantic.name_resolver import MUTATING_BUILTINS


RUNTIME_PRELUDE = r'''// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static int fusion_objects_live = 0;   // class objects made and not yet freed (Task 32.10b)
#define FUSION_OBJECT_MADE() (fusion_objects_live++)
#define FUSION_OBJECT_FREED() (fusion_objects_live--)
static inline void fusion_leak_report(void) {
    if (fusion_objects_live > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d object(s) were never freed\n", fusion_objects_live);
        _Exit(5);
    }
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#else
#define FUSION_OBJECT_MADE() ((void)0)
#define FUSION_OBJECT_FREED() ((void)0)
#endif
// -DFUSION_TRACE_OBJECTS (tests): every object freed is shown in the output, in order, so a
// test can check it was freed at the right moment (Task 32.10c)
#ifdef FUSION_TRACE_OBJECTS
#define FUSION_TRACE_FREED(name) (fflush(stdout), printf("[freed %s]\n", name), fflush(stdout))
#else
#define FUSION_TRACE_FREED(name) ((void)0)
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Only when the project sets [build] wait_at_exit =
// true (FUSION_WAIT_AT_EXIT - off by default, user 2026-10-28: for development, examples and
// testing); never with --headless or when no one is at the console (redirected - tests,
// scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
#include <unistd.h>
#define FUSION_IS_CONSOLE(f) isatty(fileno(f))
#endif
#ifdef FUSION_WAIT_AT_EXIT
static void fusion_wait_for_key(void) {
    fflush(stdout);
    fprintf(stderr, "\nPress any key to close...");
    fflush(stderr);
#ifdef _WIN32
    _getch();
#else
    getchar();
#endif
}
#endif
// Endless recursion (Task 27.2c, user decision 2026-10-17): where the stack starts, and how
// much of it the program's own functions may use - the rest is left for the runtime
static char* fusion_stack_base = NULL;
static size_t fusion_stack_room = 0;
static int fusion_call_depth __attribute__((unused)) = 0;   // [safety] max_call_depth: calls counted
#ifdef _WIN32
__declspec(dllimport) void __stdcall GetCurrentThreadStackLimits(uintptr_t* low, uintptr_t* high);
#else
#include <sys/resource.h>
#endif
static inline void fusion_stack_start(char* here) {
    size_t size = 1024 * 1024;
#ifdef _WIN32
    uintptr_t low = 0, high = 0;
    GetCurrentThreadStackLimits(&low, &high);
    if (high > low) size = (size_t)(high - low);
#else
    struct rlimit limit;
    size = getrlimit(RLIMIT_STACK, &limit) == 0 && limit.rlim_cur != RLIM_INFINITY
         ? (size_t)limit.rlim_cur : (size_t)8 * 1024 * 1024;
#endif
    fusion_stack_base = here;
    fusion_stack_room = size - size / 8;
}
// True when a function that can call itself finds the stack nearly full
static inline bool fusion_stack_low(void) {
    char here;
    return fusion_stack_base && (size_t)(fusion_stack_base - &here) > fusion_stack_room;
}

static inline void fusion_init(int argc, char** argv) {
    bool headless = false;
    char stack_here;
    fusion_stack_start(&stack_here);
#ifdef _WIN32
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);   // typed input as UTF-8 too (readLine, Task 18.5.4)
#endif
    for (int i = 1; i < argc; i++) if (strcmp(argv[i], "--headless") == 0) headless = true;
#ifdef FUSION_WAIT_AT_EXIT
    if (!headless && FUSION_IS_CONSOLE(stdin) && FUSION_IS_CONSOLE(stdout))
        atexit(fusion_wait_for_key);
#else
    (void)headless;
#endif
}

// Errors (Task 26): an error travels in fusion_err while fusion_failed is set - declared
// here so every run-time error can raise one; the rest is in the errors part further down
typedef struct {
    int active; int code; fusion_string message; fusion_string where; int runtime;
    int kind;       // 0: Error; a custom error type's number (Task 26.9)
    void* extra;    // a custom error type's own fields, on the heap - or NULL
} fusion_error;
// The program's error types (Task 26.9): name, parent, and how to copy / free their fields.
// Generated per program and set as main starts; NULL while there are none
typedef struct { const char* name; int parent; void* (*copy)(void*); void (*free)(void*); } fusion_error_kind;
static const fusion_error_kind* fusion_error_kinds;   // Fusion's own types until main sets them all
static fusion_error fusion_err;
static int fusion_failed = 0;
// Fusion's own error types (Task 26.12) - their numbers
/*FUSION_KIND_DEFINES*/
static inline void fusion_raise_text(int kind, void* extra, const char* where, const char* text, int len);
static inline void* fusion_errdata_fu_FileError_new(fusion_string path);
static void* fusion_errdata_fu_FileError_copy(void* p);
static void fusion_errdata_fu_FileError_free(void* p);
static inline fusion_string fusion_error_string(const char* text, int len);

// A run-time error (an index out of range, text that isn't a number, a file that won't
// open, ...) is an Error like any other since Task 26.4: it can be captured or caught, and
// one nobody handles stops the program at the end of main. The function that raised it
// returns a safe value at once; the generated code checks right after the call
static inline int fusion_error_format(char* text, int size, const char* format, va_list args) {
    int n = vsnprintf(text, (size_t)size, format, args);
    if (n < 0) n = 0;
    if (n >= size) n = size - 1;
    return n;
}
// An error of one of Fusion's own types (FUSION_KIND_IndexError ...) - Task 26.12
static inline void fusion_fail(int kind, const char* where, const char* format, ...) {
    char text[512];
    va_list args;
    va_start(args, format);
    int n = fusion_error_format(text, sizeof text, format, args);
    va_end(args);
    fusion_raise_text(kind, NULL, where, text, n);
}
// A FileError (or a subtype): its path too
static inline void fusion_file_fail(int kind, const char* where, fusion_string path, const char* format, ...) {
    char text[512];
    va_list args;
    va_start(args, format);
    int n = fusion_error_format(text, sizeof text, format, args);
    va_end(args);
    fusion_raise_text(kind, fusion_errdata_fu_FileError_new(fusion_error_string(path.data, path.len)),
                      where, text, n);
}
static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    char text[512];
    va_list args;
    va_start(args, format);
    int n = fusion_error_format(text, sizeof text, format, args);
    va_end(args);
    fusion_raise_text(0, NULL, where, text, n);
}

// A failure nothing can recover from - out of memory: stop at once
static inline void fusion_fatal(const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error: ");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

// The last character position found in a non-ASCII string (Task 44.6): the next lookup in the
// same string continues from there, forwards or backwards, so a loop over text[i] is fast
// instead of counting from the start every time. Only owned strings are remembered - their
// memory goes through fusion_dealloc, which forgets the string when it is freed, so a reused
// address can never give a stale answer. One per program (there are no threads yet).
static const char* fusion_hint_data = 0;
static int fusion_hint_len = 0;
static int fusion_hint_i = 0;
static int fusion_hint_off = 0;

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_fatal("out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_fatal("out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
    return p;
}

static inline void fusion_dealloc(void* p) {
    if (p == (void*)fusion_hint_data) fusion_hint_data = 0;   // forget a freed string (44.6)
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
    r.chars = s.chars;
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
// UTF-8 (Task 18.3.2b): a character takes 1-4 bytes; continuation bytes are 10xxxxxx
static inline int fusion_utf8_count(const char* data, int len) {
    int n = 0;
    for (int i = 0; i < len; i++) if ((data[i] & 0xC0) != 0x80) n++;
    return n;
}
// Byte offset of character number `index` (index == chars gives the end). Non-ASCII text
// starts from the last position found in the same string when that is nearer (44.6)
static inline int fusion_utf8_offset(fusion_string s, int index) {
    if (s.chars == s.len) return index;           // ASCII: one byte per character
    int i = 0, o = 0;
    if (s.owned && s.data == fusion_hint_data && s.len == fusion_hint_len) {
        if (fusion_hint_i <= index) {
            i = fusion_hint_i; o = fusion_hint_off;  // forwards from the last position
        } else if (fusion_hint_i - index < index) {
            i = fusion_hint_i; o = fusion_hint_off;  // backwards, when nearer than the start
            while (i > index) { o--; while (o > 0 && (s.data[o] & 0xC0) == 0x80) o--; i--; }
        }
    }
    while (i < index && o < s.len) { o++; while (o < s.len && (s.data[o] & 0xC0) == 0x80) o++; i++; }
    if (s.owned) { fusion_hint_data = s.data; fusion_hint_len = s.len; fusion_hint_i = i; fusion_hint_off = o; }
    return o;
}
static inline fusion_char fusion_utf8_decode(const char* p) {
    unsigned char b = (unsigned char)p[0];
    if (b < 0x80) return b;
    if (b < 0xE0) return (fusion_char)(((b & 0x1F) << 6) | (p[1] & 0x3F));
    if (b < 0xF0) return (fusion_char)(((b & 0x0F) << 12) | ((p[1] & 0x3F) << 6) | (p[2] & 0x3F));
    return (fusion_char)(((b & 0x07) << 18) | ((p[1] & 0x3F) << 12) | ((p[2] & 0x3F) << 6) | (p[3] & 0x3F));
}
static inline int fusion_utf8_encode(fusion_char c, char* out) {
    unsigned long v = (unsigned long)c;
    if (v < 0x80) { out[0] = (char)v; return 1; }
    if (v < 0x800) { out[0] = (char)(0xC0 | (v >> 6)); out[1] = (char)(0x80 | (v & 0x3F)); return 2; }
    if (v < 0x10000) { out[0] = (char)(0xE0 | (v >> 12)); out[1] = (char)(0x80 | ((v >> 6) & 0x3F)); out[2] = (char)(0x80 | (v & 0x3F)); return 3; }
    out[0] = (char)(0xF0 | (v >> 18)); out[1] = (char)(0x80 | ((v >> 12) & 0x3F));
    out[2] = (char)(0x80 | ((v >> 6) & 0x3F)); out[3] = (char)(0x80 | (v & 0x3F)); return 4;
}
// A character as printable text, for printf("%s", fusion_char_text(c).bytes)
typedef struct { char bytes[5]; } fusion_char_buf;
static inline fusion_char_buf fusion_char_text(fusion_char c) {
    fusion_char_buf b; int n = fusion_utf8_encode(c, b.bytes); b.bytes[n] = '\0'; return b;
}

// [strings] max_length (Task 18.3.4b): when a project sets a limit (memory-constrained
// devices), every string built while the program runs is checked as it is made, and a longer
// one stops the program with an error - never cut. No limit (the default): nothing to check
#ifdef FUSION_MAX_LENGTH
static const char* fusion_at = NULL;   // "file:line" of the statement running now
static inline void fusion_check_length(fusion_string* r) {
    if (r->chars > FUSION_MAX_LENGTH)
        fusion_fail(FUSION_KIND_StringTooLongError, fusion_at, "a string of %d characters is longer than maxLength %d ([strings] in fusion.toml)", r->chars, FUSION_MAX_LENGTH);
}
#define FUSION_CHECK_LENGTH(r) fusion_check_length(&(r))
#else
#define FUSION_CHECK_LENGTH(r) ((void)0)
#endif

static inline fusion_string fusion_str_make(const char* data, int len) {
    fusion_string r;
    r.data = (char*)fusion_alloc((size_t)len + 1);
    if (len > 0) memcpy(r.data, data, (size_t)len);
    r.data[len] = '\0';
    r.len = len;
    r.chars = fusion_utf8_count(data, len);
    r.owned = 1;
    FUSION_CHECK_LENGTH(r);
    return r;
}

static inline fusion_string fusion_str_concat(fusion_string a, fusion_string b) {
    fusion_string r;
    r.data = (char*)fusion_alloc((size_t)a.len + (size_t)b.len + 1);
    memcpy(r.data, a.data, (size_t)a.len);
    memcpy(r.data + a.len, b.data, (size_t)b.len);
    r.data[a.len + b.len] = '\0';
    r.len = a.len + b.len;
    r.chars = a.chars + b.chars;
    r.owned = 1;
    FUSION_CHECK_LENGTH(r);
    return r;
}
// A character as a string that is never freed - only for joining (the text is copied)
static inline fusion_string fusion_char_view(fusion_char c, char* buf) {
    fusion_string v; v.len = fusion_utf8_encode(c, buf); v.data = buf; v.chars = 1; v.owned = 0; return v;
}
static inline fusion_string fusion_str_concat_char(fusion_string a, fusion_char c) { char buf[4]; return fusion_str_concat(a, fusion_char_view(c, buf)); }
static inline fusion_string fusion_char_concat_str(fusion_char c, fusion_string b) { char buf[4]; return fusion_str_concat(fusion_char_view(c, buf), b); }

static inline fusion_char fusion_str_at(fusion_string s, int i, const char* where) {
    if (i < 0 || i >= s.chars) { fusion_fail(FUSION_KIND_IndexError, where, "index %d is outside the string (length %d)", i, s.chars); return 0; }
    return fusion_utf8_decode(s.data + fusion_utf8_offset(s, i));
}

// An enum with no value (Task 30.11): a number no enum value may use
#define FUSION_ENUM_NULL (-2147483647)
static inline void fusion_null_fail(const char* where, const char* what);
// `.` on an object (Task 32.10b): null is a NullError - the caller checks fusion_failed
static inline void* fusion_need(void* p, const char* where, const char* kind) {
    if (!p) { char what[160]; snprintf(what, sizeof what, "used '.' on a null %s", kind);
              fusion_null_fail(where, what); }
    return p;
}
static inline void fusion_null_fail(const char* where, const char* what) {
    fusion_fail(FUSION_KIND_NullError, where, "%s", what);
}
static inline int fusion_enum_toInt(int v, const char* where) {
    if (v == FUSION_ENUM_NULL) { fusion_null_fail(where, "toInt() on a null enum value - it has no number"); return 0; }
    return v;
}

// s[i] = c - edits the string in place (Task 29.1). Text from the source is copied first, so
// the literal itself never changes; a character of another byte width moves the rest
static inline void fusion_str_put(fusion_string* s, int i, fusion_char c, const char* where) {
    if (i < 0 || i >= s->chars) { fusion_fail(FUSION_KIND_IndexError, where, "index %d is outside the string (length %d)", i, s->chars); return; }
    char buf[4];
    int n = fusion_utf8_encode(c, buf);
    int from = fusion_utf8_offset(*s, i);
    int old = fusion_utf8_offset(*s, i + 1) - from;
    if (s->owned && n == old) { memcpy(s->data + from, buf, (size_t)n); return; }
    int len = s->len - old + n;
    char* out = (char*)fusion_alloc((size_t)len + 1);
    memcpy(out, s->data, (size_t)from);
    memcpy(out + from, buf, (size_t)n);
    memcpy(out + from + n, s->data + from + old, (size_t)(s->len - from - old));
    out[len] = '\0';
    if (s->owned) fusion_dealloc(s->data);
    s->data = out; s->len = len; s->owned = 1;
}

static inline fusion_string fusion_str_substring(fusion_string s, int start, int count, const char* where) {
    if (start < 0 || count < 0 || start > s.chars || count > s.chars - start) {
        fusion_fail(FUSION_KIND_IndexError, where, "substring(start %d, count %d) is outside the string (length %d)", start, count, s.chars);
        return FUSION_STR("");
    }
    int from = fusion_utf8_offset(s, start);
    return fusion_str_make(s.data + from, fusion_utf8_offset(s, start + count) - from);
}

// Character position of the first match, or -1
static inline int fusion_str_indexOf(fusion_string s, fusion_string part) {
    for (int i = 0; i + part.len <= s.len; i++)
        if (memcmp(s.data + i, part.data, (size_t)part.len) == 0)
            return s.chars == s.len ? i : fusion_utf8_count(s.data, i);
    return -1;
}

// Build a string from a printf-style format (Task 18.3.3): "x is {x}" as a value, and format()
static inline fusion_string fusion_str_format(const char* format, ...) {
    va_list args, measure;
    va_start(args, format);
    va_copy(measure, args);
    int n = vsnprintf(NULL, 0, format, measure);
    va_end(measure);
    fusion_string r;
    r.data = (char*)fusion_alloc((size_t)n + 1);
    vsnprintf(r.data, (size_t)n + 1, format, args);
    va_end(args);
    r.len = n;
    r.chars = fusion_utf8_count(r.data, n);
    r.owned = 1;
    FUSION_CHECK_LENGTH(r);
    return r;
}

// Encoding helpers (Task 18.3.2b)
static inline bool fusion_str_isAscii(fusion_string s) { return s.chars == s.len; }
static inline fusion_string fusion_str_asciiOnly(fusion_string s, fusion_char replacement) {
    char rep[4]; int replen = fusion_utf8_encode(replacement, rep);
    fusion_string r; int out = 0;
    r.data = (char*)fusion_alloc((size_t)s.len * 4 + 1);
    for (int i = 0; i < s.len; ) {
        if ((unsigned char)s.data[i] < 0x80) { r.data[out++] = s.data[i++]; continue; }
        memcpy(r.data + out, rep, (size_t)replen); out += replen;
        i++; while (i < s.len && (s.data[i] & 0xC0) == 0x80) i++;
    }
    r.data[out] = '\0'; r.len = out; r.chars = fusion_utf8_count(r.data, out); r.owned = 1;
    return r;
}
static inline int fusion_charCode(fusion_char c) { return (int)c; }
static inline fusion_char fusion_fromCharCode(int code, const char* where) {
#ifdef FUSION_ASCII
    if (code < 0 || code > 0x7F) { fusion_fail(FUSION_KIND_RangeError, where, "%d is not an ASCII character code (the project uses ascii encoding)", code); return 0; }
#else
    if (code < 0 || code > 0x10FFFF || (code >= 0xD800 && code <= 0xDFFF)) { fusion_fail(FUSION_KIND_RangeError, where, "%d is not a Unicode character code", code); return 0; }
#endif
    return (fusion_char)code;
}
static inline int fusion_str_byteAt(fusion_string s, int i, const char* where) {
    if (i < 0 || i >= s.len) { fusion_fail(FUSION_KIND_IndexError, where, "byte %d is outside the string (%d bytes)", i, s.len); return 0; }
    return (unsigned char)s.data[i];
}
static inline bool fusion_str_contains(fusion_string s, fusion_string part) { return fusion_str_indexOf(s, part) >= 0; }
static inline bool fusion_str_startsWith(fusion_string s, fusion_string part) {
    return part.len <= s.len && memcmp(s.data, part.data, (size_t)part.len) == 0;
}
static inline bool fusion_str_endsWith(fusion_string s, fusion_string part) {
    return part.len <= s.len && memcmp(s.data + s.len - part.len, part.data, (size_t)part.len) == 0;
}

// toUpper / toLower: see the string library (c_strings.py, Task 18.3.6b)
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
static inline fusion_string fusion_char_to_str(fusion_char value) { char buf[4]; return fusion_str_make(buf, fusion_utf8_encode(value, buf)); }

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
    if (!fusion_parse_int(s, &v)) { fusion_fail(FUSION_KIND_NumberFormatError, where, "'%.*s' is not a whole number (check with isInt first)", s.len, s.data); return 0; }
    return v;
}
static inline float fusion_str_toFloat(fusion_string s, const char* where) {
    double v;
    if (!fusion_parse_float(s, &v)) { fusion_fail(FUSION_KIND_NumberFormatError, where, "'%.*s' is not a number (check with isFloat first)", s.len, s.data); return 0; }
    return (float)v;
}
// Equality across types (Task 18.3.5): a number equals text holding that number (text that
// isn't a number is simply unequal); a char equals a one-character string
static inline bool fusion_double_eq_str(double n, fusion_string s) { double v; return fusion_parse_float(s, &v) && v == n; }
static inline bool fusion_float_eq_str(float n, fusion_string s) { double v; return fusion_parse_float(s, &v) && (float)v == n; }
static inline bool fusion_char_eq_str(fusion_char c, fusion_string s) { return s.chars == 1 && fusion_utf8_decode(s.data) == c; }
// ---- end of runtime ----
'''
RUNTIME_PRELUDE += STRING_LIBRARY  # the versatile string functions (Task 18.3.6)
RUNTIME_PRELUDE += BYTES_LIBRARY   # raw bytes (Task 18.3.8)
RUNTIME_PRELUDE += FILES_LIBRARY   # files (Task 18.5.5)
RUNTIME_PRELUDE += ERRORS_LIBRARY  # errors travelling and caught (Task 26)
RUNTIME_PRELUDE = RUNTIME_PRELUDE.replace('/*FUSION_KIND_DEFINES*/\n', BUILTIN_KIND_DEFINES)


class MemoryManagementMixin:
    """Ownership-aware code generation - mixed into CCodeGenerator (Task 18.3.1)."""

    # ------------------------------------------------------------------ type queries

    def is_managed(self, type_node) -> bool:
        """True if values of this type own heap memory (a string anywhere inside them)."""
        if type(type_node).__name__ == 'BoxType':
            return True   # an enum holding itself, on the heap (Task 25.5)
        if type(type_node).__name__ == 'ErrorType':
            return True   # its message and where (Task 26)
        if isinstance(type_node, (ListType, MapType)):
            return True   # a list / map owns its buffers (Tasks 18.5.1, 18.5.2)
        if isinstance(type_node, PrimitiveType):
            return type_node.name in ('string', 'bytes')   # bytes: the same struct (18.3.8)
        if isinstance(type_node, ArrayType):
            return self.is_managed(type_node.element_type)
        if isinstance(type_node, StructType):
            struct = self._struct_decl(type_node)
            if struct.is_class:
                return True   # an object with a count (Task 32.10b)
            return any(self.is_managed(f.field_type) for f in struct.fields)
        return False

    def is_class_type(self, type_node) -> bool:
        """A class's type - a pointer to an object with a count (Task 32.10b)."""
        if not isinstance(type_node, StructType):
            return False
        decl = type_node.declaration or getattr(self, 'struct_decls', {}).get(type_node.name)
        return getattr(decl, 'is_class', False)

    def _struct_c_name(self, type_node: StructType) -> str:
        return mangle_function_name(type_node.name)

    def copy_code(self, type_node, code: str) -> str:
        """C expression giving an independent copy of a (non-array) managed value."""
        if type(type_node).__name__ == 'BoxType':
            return f'fusion_box_copy_{self.map_type(type_node.inner)}({code})'   # Task 25.5
        if type(type_node).__name__ == 'ErrorType':
            return f'fusion_error_copy({code})'                                 # Task 26
        if isinstance(type_node, PrimitiveType) and type_node.name in ('string', 'bytes'):
            return f'fusion_str_copy({code})'
        if isinstance(type_node, (ListType, MapType)):
            # a reference: one more holder of the same list (Task 32.10a)
            return f'{self.map_type(type_node)}_retain({code})'
        if self.is_class_type(type_node):
            return f'fusion_retain_{self._struct_c_name(type_node)}({code})'   # one more holder (32.10b)
        if isinstance(type_node, StructType) and self.is_managed(type_node):
            return f'fusion_copy_{self._struct_c_name(type_node)}({code})'
        return code

    def clone_code(self, type_node, code: str) -> str:
        """C expression giving a deep copy - a List or Map is copied, not shared (`byVal`, a
        struct's own copy - Task 32.10a); an object too (32.5b, D.088); anything else as
        copy_code."""
        if isinstance(type_node, (ListType, MapType)):
            return f'{self.map_type(type_node)}_clone({code})'
        if self.is_class_type(type_node):
            decl = type_node.declaration or self.struct_decls.get(type_node.name)
            has_children = any(decl.name in getattr(d, 'ancestors', ()) for d in self.struct_decls.values())
            if decl.is_interface or has_children:
                return f'fusion_clone_object({code})'      # its own class makes it (32.5b, 32.7)
            return f'fusion_clone_{self._struct_c_name(type_node)}({code})'
        return self.copy_code(type_node, code)

    def error_value(self, type_node) -> str:
        """What a call that failed gives back - never a new List / Map (nothing would free
        it): the caller goes on to the error."""
        if isinstance(type_node, (ListType, MapType)):
            return 'NULL'
        return self._default_value_code(type_node)

    def temp_initial(self, type_node) -> str:
        """A temporary's first value, set where the function starts: empty and allocating
        nothing - it may never be used (a List / Map is NULL until then)."""
        if isinstance(type_node, (ListType, MapType)):
            return 'NULL'
        if isinstance(type_node, StructType) and self.holds_collection(type_node):
            return '{0}'
        return self._default_value_code(type_node)

    def holds_collection(self, type_node) -> bool:
        """A List or Map somewhere inside a struct (its default allocates)."""
        if isinstance(type_node, (ListType, MapType)):
            return True
        if isinstance(type_node, ArrayType):
            return self.holds_collection(type_node.element_type)
        if isinstance(type_node, StructType) and not self.is_class_type(type_node):
            return any(self.holds_collection(f.field_type)
                       for f in self._struct_decl(type_node).fields)
        return False

    def free_lines(self, type_node, lvalue: str, depth: int = 0) -> list:
        """C statements freeing a managed value stored at `lvalue`."""
        if not self.is_managed(type_node):
            return []
        if type(type_node).__name__ == 'BoxType':
            return [f'fusion_box_free_{self.map_type(type_node.inner)}(&{lvalue});']   # Task 25.5
        if type(type_node).__name__ == 'ErrorType':
            return [f'fusion_error_free(&{lvalue});']                                  # Task 26
        if isinstance(type_node, (ListType, MapType)):
            return [f'{self.map_type(type_node)}_free(&{lvalue});']
        if self.is_class_type(type_node):
            return [f'fusion_release_{self._struct_c_name(type_node)}(&{lvalue});']   # Task 32.10b
        if isinstance(type_node, PrimitiveType):
            return [f'fusion_str_free(&{lvalue});']
        if isinstance(type_node, StructType):
            return [f'fusion_free_{self._struct_c_name(type_node)}(&{lvalue});']
        index = f'fusion_i{depth}'
        inner = ' '.join(self.free_lines(type_node.element_type, f'{lvalue}[{index}]', depth + 1))
        return [f'for (int {index} = 0; {index} < {type_node.size}; {index}++) {{ {inner} }}']

    def set_code(self, type_node, lvalue: str, value_code: str) -> str:
        """C statement replacing a stored managed value, freeing the old one."""
        if isinstance(type_node, (ListType, MapType)):
            return f'{self.map_type(type_node)}_set(&{lvalue}, {value_code});'
        if type(type_node).__name__ == 'ErrorType':
            return f'fusion_error_set(&{lvalue}, {value_code});'   # Task 26
        if self.is_class_type(type_node):
            return f'fusion_set_{self._struct_c_name(type_node)}(&{lvalue}, {value_code});'   # 32.10b
        if isinstance(type_node, PrimitiveType):
            return f'fusion_str_set(&{lvalue}, {value_code});'
        return f'fusion_set_{self._struct_c_name(type_node)}(&{lvalue}, {value_code});'

    # ------------------------------------------------------------------ struct helpers

    def struct_helper_lines(self, ordered_structs) -> list:
        """Copy / free / set helpers for every struct holding a string somewhere, in
        dependency order (a struct's helpers call its fields' helpers)."""
        lines = self.class_helper_lines([s for s in ordered_structs if s.is_class])
        for struct in ordered_structs:
            struct_type = StructType(location=struct.location, name=struct.name, declaration=struct)
            if struct.is_class or not self.is_managed(struct_type):
                continue
            c = self._struct_c_name(struct_type)
            copy_body, free_body = [], []
            for field in struct.fields:
                if not self.is_managed(field.field_type):
                    continue
                name = f'v.{self._field_name(field.name)}'
                field_type = field.field_type
                # A struct's List / Map is copied with it - shared only if the field is
                # byRef (Task 32.10a, user decision 2026-10-29)
                copy = self.copy_code if getattr(field, 'by_ref', False) else self.clone_code
                if isinstance(field_type, ArrayType):
                    element = field_type.element_type
                    copy_body.append(
                        f'    for (int i = 0; i < {field_type.size}; i++) '
                        f'{name}[i] = {copy(element, f"{name}[i]")};')
                else:
                    copy_body.append(f'    {name} = {copy(field_type, name)};')
                free_body += ['    ' + line for line in self.free_lines(
                    field_type, f'v->{self._field_name(field.name)}')]
            lines += [f'static inline {c} fusion_copy_{c}({c} v) {{'] + copy_body + \
                     ['    return v;', '}',
                      f'static inline void fusion_free_{c}({c}* v) {{'] + free_body + ['}',
                      f'static inline void fusion_set_{c}({c}* dst, {c} value) {{ '
                      f'fusion_free_{c}(dst); *dst = value; }}']
        return lines

    def class_helper_lines(self, classes) -> list:
        """Per class (Task 32.10b): fusion_make_fu_Car - a new object, fields at their
        defaults, count 1; fusion_retain_ - one more holder; fusion_release_ - one less, and at
        0 its fields let go and it is freed; fusion_set_ - replace what a holder holds. Named
        fusion_* so no method (fu_Car__make) can clash (Task 32.2h). Prototypes first: classes
        refer to each other."""
        from .c_runtime import escape_c_text
        protos, bodies = [], []
        for decl in classes:
            kind = StructType(location=decl.location, name=decl.name, declaration=decl)
            c = self._struct_c_name(kind)
            if decl.is_interface:
                # any object: count it through its header, free it through its class (32.5a)
                protos += [f'static inline {c}* fusion_retain_{c}({c}* o);',
                           f'static inline void fusion_release_{c}({c}** p);',
                           f'static inline void fusion_set_{c}({c}** dst, {c}* v);']
                bodies += [f'static inline {c}* fusion_retain_{c}({c}* o) {{ '
                           f'if (o) ((fusion_object*)o)->fusion_count++; return o; }}',
                           f'static inline void fusion_release_{c}({c}** p) {{ void* o = *p; *p = NULL; '
                           f'if (o) ((fusion_object*)o)->fusion_class->release(&o); }}',
                           f'static inline void fusion_set_{c}({c}** dst, {c}* v) {{ {c}* old = *dst; '
                           f'*dst = v; fusion_release_{c}(&old); }}']
                continue
            protos.append(f'static const fusion_class_t fusion_class_{c};')   # its table (32.5a)
            protos.append(f'static {c}* fusion_clone_{c}({c}* o);')             # a copy (32.5b)
            protos += [f'static inline {c}* fusion_make_{c}(void);', f'static inline {c}* fusion_retain_{c}({c}* o);',
                       f'static inline void fusion_release_{c}({c}** p);', f'static inline void fusion_set_{c}({c}** dst, {c}* v);']
            make = [f'static inline {c}* fusion_make_{c}(void) {{',
                    f'    {c}* o = ({c}*)fusion_alloc(sizeof({c}));',
                    '    memset(o, 0, sizeof *o);',
                    '    o->fusion_count = 1;',
                    f'    o->fusion_class = &fusion_class_{c};',
                    '    FUSION_OBJECT_MADE();']
            release = [f'static inline void fusion_release_{c}({c}** p) {{',
                       f'    {c}* o = *p;',
                       '    *p = NULL;',
                       '    if (!o || --o->fusion_count > 0) return;',
                       '    FUSION_OBJECT_FREED();',
                       f'    FUSION_TRACE_FREED("{escape_c_text(decl.name, chr(34))}");']
            for f in decl.fields:
                field = f'o->{self._field_name(f.name)}'
                if isinstance(f.field_type, ArrayType):
                    value = None if f.default_value is None else self.visit(f.default_value)
                    if value is not None or not self._is_zero_safe(f.field_type):
                        value = value or self._default_value_code(f.field_type)
                        make.append(f'    {{ {self.map_type(f.field_type.element_type)} init[] = '
                                    f'{value}; memcpy({field}, init, sizeof init); }}')
                elif getattr(f.default_value, 'made_by_default', False):
                    # a Default type's field: a new object from its constructor (Task 32.5b)
                    inner = f.field_type.declaration or self.struct_decls.get(f.field_type.name)
                    made = inner.default_constructor
                    maker = self._mangle_function_name(made.name)
                    protos.append(f'{self.map_type(f.field_type)} {maker}({self._c_parameter_list(made.parameters)});')
                    make.append(f'    {field} = {maker}();')
                elif f.default_value is not None:
                    make.append(f'    {field} = {self.owned_value(f.default_value, f.field_type)};')
                elif not self._is_zero_safe(f.field_type):
                    make.append(f'    {field} = {self._default_value_code(f.field_type)};')
                release += ['    ' + line for line in self.free_lines(f.field_type, field)]
            bodies += make + ['    return o;', '}']
            bodies += [f'static inline {c}* fusion_retain_{c}({c}* o) {{ if (o) o->fusion_count++; return o; }}']
            bodies += release + ['    fusion_dealloc(o);', '}']
            bodies += [f'static inline void fusion_set_{c}({c}** dst, {c}* v) {{ {c}* old = *dst; *dst = v; '
                       f'fusion_release_{c}(&old); }}']
            # freed through an interface's value: its class table points here (32.5a)
            bodies += [f'static void fusion_release_any_{c}(void** p) {{ fusion_release_{c}(({c}**)p); }}']
        return protos + bodies

    def emit_clone_function(self, decl) -> None:
        """fusion_clone_fu_Car (Task 32.5b, D.088): a new object with each field copied byVal -
        the field defaults don't run again; a Cloneable class's own clone() makes it instead."""
        kind = StructType(location=decl.location, name=decl.name, declaration=decl)
        c = self._struct_c_name(kind)
        self.emit(f'static {c}* fusion_clone_{c}({c}* o) {{')
        self.emit('    if (!o) return NULL;')
        clone = getattr(decl, 'clone_method', None)
        if clone is not None:
            self.emit(f'    return {self._mangle_function_name(clone.name)}(o);')
            self.emit('}')
            return
        self.emit(f'    {c}* r = ({c}*)fusion_alloc(sizeof({c}));')
        self.emit('    memset(r, 0, sizeof *r);')
        self.emit(f'    r->fusion_count = 1; r->fusion_class = &fusion_class_{c};')
        self.emit('    FUSION_OBJECT_MADE();')
        for f in decl.fields:
            name = self._field_name(f.name)
            if isinstance(f.field_type, ArrayType):
                element = f.field_type.element_type
                if self.is_managed(element):
                    self.emit(f'    for (int i = 0; i < {f.field_type.size}; i++) '
                              f'r->{name}[i] = {self.clone_code(element, f"o->{name}[i]")};')
                else:
                    self.emit(f'    memcpy(r->{name}, o->{name}, sizeof r->{name});')
            else:
                self.emit(f'    r->{name} = {self.clone_code(f.field_type, f"o->{name}")};')
        self.emit('    return r;')
        self.emit('}')

    def object_needed(self, code: str, type_node, node) -> str:
        """An object about to be used through `.` - null is a NullError (Task 32.10b)."""
        from .c_runtime import escape_c_text
        c = self._struct_c_name(type_node)
        name = escape_c_text(type_node.name, '"')
        return self.checked_code(f'(({c}*)fusion_need({code}, {self._where(node)}, "{name}"))',
                                 f'{c}*')

    # ------------------------------------------------------------------ ownership of values

    def is_fresh(self, expr) -> bool:
        """True for an expression whose managed value is newly made and owned by nobody
        yet: a call returning a managed value (including a constructor and the string
        built-ins), or joining strings with `+` (18.3.2). Storing it takes it over;
        otherwise it's freed at the end of the statement."""
        if isinstance(expr, BinaryExpr):
            return expr.operator == '+' and self.is_managed(getattr(expr, 'inferred_type', None))
        if isinstance(expr, InterpolatedStringExpr):
            return True  # "x is {x}" builds a new string (18.3.3)
        if type(expr).__name__ == 'ObjectMakeExpr':
            return True   # a new object, count 1 (Task 32.10b)
        if type(expr).__name__ == 'PassingExpr':
            # byVal a: a new copy; byRef a: as the value itself (Task 32.10a)
            if expr.by_val:
                return self.is_managed(getattr(expr, 'inferred_type', None))
            return self.is_fresh(expr.value)
        if type(expr).__name__ == 'MatchExpr':
            # a match value (Task 46.2): each value made owned, as with (c) ? a : b
            return self.is_managed(getattr(expr, 'inferred_type', None))
        if isinstance(expr, ConditionalExpr):
            # (c) ? a : b - each value is made owned, so the result always is (Task 30.7)
            return self.is_managed(getattr(expr, 'inferred_type', None))
        if isinstance(expr, ArrayLiteralExpr):
            # [0x6B, 0x69] stored as bytes, [1, 2] stored as a List - both are built (18.3.8, 18.5.1)
            return self._is_bytes(expr) or isinstance(getattr(expr, 'inferred_type', None), ListType)
        if isinstance(expr, NewCollectionExpr):
            return True   # List<int>() - an empty list (Task 18.5.1)
        if type(expr).__name__ == 'EnumStaticCall':
            # Color.values() builds a list (25.2); Token.Word("x") a value holding a string (25.4)
            return expr.method == 'values' or (expr.method != 'fromString'
                                               and self.is_managed(getattr(expr, 'inferred_type', None)))
        if isinstance(expr, CallExpr) and getattr(expr, 'list_method', None) in ('filter', 'map', 'slice', 'reduce', 'join', 'toList'):
            return self.is_managed(getattr(expr, 'inferred_type', None))
        if isinstance(expr, CallExpr) and getattr(expr, 'map_method', None):
            # m.keys() / m.values() make new lists; m.get(k, d) only lends a stored value
            return expr.map_method in ('keys', 'values')
        return isinstance(expr, CallExpr) and self.is_managed(getattr(expr, 'inferred_type', None))

    def owned_value(self, expr, type_node) -> str:
        """C code for a value that's about to be stored somewhere that owns it."""
        if type(type_node).__name__ == 'BoxType':
            # Expr.Add(a, b): each part goes into its own heap copy (Task 25.5)
            inner = self.owned_value(expr, type_node.inner)
            return f'fusion_box_make_{self.map_type(type_node.inner)}({inner})'
        if not self.is_managed(type_node):
            return self.visit(expr)
        if isinstance(expr, LiteralExpr):
            return self.visit(expr)  # source text - never freed, safe to store
        if isinstance(expr, ArrayLiteralExpr) and isinstance(type_node, ArrayType):
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
            initial = self.temp_initial(type_node)
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
            changed = None
            if isinstance(node, AssignmentStmt):
                changed = node.target
            elif isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                    and node.callee.name in MUTATING_BUILTINS and node.callee_declaration is None \
                    and node.arguments:
                changed = node.arguments[0]   # setInt(b, ...) changes b (Task 18.3.8)
            elif isinstance(node, CallExpr) and getattr(node, 'list_method', None) in MUTATING_LIST_METHODS:
                changed = node.callee.object   # xs.add(5) changes xs (Task 18.5.1)
            elif isinstance(node, CallExpr) and getattr(node, 'map_method', None) in ('remove', 'clear'):
                changed = node.callee.object   # m.remove(k) changes m (Task 18.5.2)
            if changed is not None:
                root = changed
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
