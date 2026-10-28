// fusion_runtime.h - the C run-time every Fusion program shares (Task 28.1.3)
// Generated from the Python compiler by: python check.py --runtime - do not edit
// A program #defines its settings (FUSION_ASCII, FUSION_MAX_LENGTH) first
#ifndef FUSION_RUNTIME_H
#define FUSION_RUNTIME_H

#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
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
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
#include <unistd.h>
#define FUSION_IS_CONSOLE(f) isatty(fileno(f))
#endif
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
    if (!headless && FUSION_IS_CONSOLE(stdin) && FUSION_IS_CONSOLE(stdout))
        atexit(fusion_wait_for_key);
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
#define FUSION_KIND_ArithmeticError 1
#define FUSION_KIND_DivideByZeroError 2
#define FUSION_KIND_FormatError 3
#define FUSION_KIND_NumberFormatError 4
#define FUSION_KIND_PatternError 5
#define FUSION_KIND_HexFormatError 6
#define FUSION_KIND_TextEncodingError 7
#define FUSION_KIND_ValueError 8
#define FUSION_KIND_RangeError 9
#define FUSION_KIND_UnknownValueError 10
#define FUSION_KIND_LookupError 11
#define FUSION_KIND_IndexError 12
#define FUSION_KIND_KeyError 13
#define FUSION_KIND_FileError 14
#define FUSION_KIND_FileNotFoundError 15
#define FUSION_KIND_PermissionError 16
#define FUSION_KIND_FileReadError 17
#define FUSION_KIND_FileWriteError 18
#define FUSION_KIND_FileTooLargeError 19
#define FUSION_KIND_DeleteError 20
#define FUSION_KIND_LimitError 21
#define FUSION_KIND_StringTooLongError 22
#define FUSION_KIND_ResultTooLargeError 23
#define FUSION_KIND_OverflowError 24
#define FUSION_KIND_StackOverflowError 25
#define FUSION_KIND_ModifiedWhileLoopingError 26
#define FUSION_KIND_PrecisionError 27
#define FUSION_KIND_ProcessError 28
#define FUSION_KIND_NullError 29
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
        fusion_fail(FUSION_KIND_StringTooLongError, fusion_at, "a string of %d characters is longer than max_length %d ([strings] in fusion.toml)", r->chars, FUSION_MAX_LENGTH);
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

// ---- Versatile string functions (Task 18.3.6) - see src/codegen/c_strings.py
static inline int fusion_utf8_size(unsigned char b) { return b < 0x80 ? 1 : b < 0xE0 ? 2 : b < 0xF0 ? 3 : 4; }
// Character position of a byte offset
static inline int fusion_char_index(fusion_string s, int byte) { return s.chars == s.len ? byte : fusion_utf8_count(s.data, byte); }
// Byte offset of the first match of `part` at or after byte `from`, or -1
static inline int fusion_find(fusion_string s, int from, const char* part, int part_len) {
    for (int i = from; i + part_len <= s.len; i++)
        if (memcmp(s.data + i, part, (size_t)part_len) == 0) return i;
    return -1;
}
// A letter: ASCII or Latin-1 (Western European accented letters)
static inline bool fusion_is_letter(fusion_char c) {
    uint32_t u = (uint32_t)c;
    if ((u >= 'a' && u <= 'z') || (u >= 'A' && u <= 'Z')) return true;
    return u == 0xAA || u == 0xB5 || u == 0xBA || (u >= 0xC0 && u <= 0xFF && u != 0xD7 && u != 0xF7);
}

// Inspect (18.3.6a)
static inline bool fusion_str_isEmpty(fusion_string s) { return s.len == 0; }
static inline bool fusion_str_isBlank(fusion_string s) {
    for (int i = 0; i < s.len; i++) if (!fusion_is_space(s.data[i])) return false;
    return true;
}
static inline bool fusion_str_isDigits(fusion_string s) {
    for (int i = 0; i < s.len; i++) if (s.data[i] < '0' || s.data[i] > '9') return false;
    return s.len > 0;
}
static inline bool fusion_str_isLetters(fusion_string s) {
    for (int i = 0; i < s.len; i += fusion_utf8_size((unsigned char)s.data[i]))
        if (!fusion_is_letter(fusion_utf8_decode(s.data + i))) return false;
    return s.len > 0;
}
// How many times `part` appears, not overlapping ("aaaa" holds "aa" twice)
static inline int fusion_str_countOf(fusion_string s, fusion_string part) {
    int n = 0;
    if (part.len == 0) return 0;
    for (int i = fusion_find(s, 0, part.data, part.len); i >= 0; i = fusion_find(s, i + part.len, part.data, part.len)) n++;
    return n;
}

// Search (18.3.6a) - character positions, -1 when not found
static inline int fusion_str_indexOfFrom(fusion_string s, fusion_string part, int from) {
    if (from < 0) from = 0;
    if (from > s.chars) return -1;
    int i = fusion_find(s, fusion_utf8_offset(s, from), part.data, part.len);
    return i < 0 ? -1 : fusion_char_index(s, i);
}
static inline int fusion_str_lastIndexOf(fusion_string s, fusion_string part) {
    for (int i = s.len - part.len; i >= 0; i--)
        if (memcmp(s.data + i, part.data, (size_t)part.len) == 0) return fusion_char_index(s, i);
    return -1;
}
// True when any one of the characters in `chars` appears in s
static inline bool fusion_str_containsAny(fusion_string s, fusion_string chars) {
    for (int j = 0; j < chars.len; j += fusion_utf8_size((unsigned char)chars.data[j]))
        if (fusion_find(s, 0, chars.data + j, fusion_utf8_size((unsigned char)chars.data[j])) >= 0) return true;
    return false;
}

// Extract (18.3.6a) - up to n characters from the start / end
static inline fusion_string fusion_str_left(fusion_string s, int n, const char* where) {
    if (n < 0) { fusion_fail(FUSION_KIND_RangeError, where, "left(%d): the count can't be negative", n); return FUSION_STR(""); }
    if (n > s.chars) n = s.chars;
    return fusion_str_make(s.data, fusion_utf8_offset(s, n));
}
static inline fusion_string fusion_str_right(fusion_string s, int n, const char* where) {
    if (n < 0) { fusion_fail(FUSION_KIND_RangeError, where, "right(%d): the count can't be negative", n); return FUSION_STR(""); }
    if (n > s.chars) n = s.chars;
    int from = fusion_utf8_offset(s, s.chars - n);
    return fusion_str_make(s.data + from, s.len - from);
}

// ---- Change (18.3.6b)
// A new string from a buffer of `len` bytes made with fusion_alloc(len + 1)
static inline fusion_string fusion_str_take(char* data, int len) {
    fusion_string r;
    data[len] = '\0';
    r.data = data; r.len = len; r.chars = fusion_utf8_count(data, len); r.owned = 1;
    FUSION_CHECK_LENGTH(r);
    return r;
}
static inline int fusion_checked_size(long long len, const char* name, const char* where) {
    if (len > 2147483646LL) { fusion_fail(FUSION_KIND_ResultTooLargeError, where, "%s: the result would be longer than 2,147,483,646 bytes", name); return -1; }
    return (int)len;
}

// Case: ASCII + Latin-1 (user decision 2026-10-09). Each pair keeps its UTF-8 byte count, so
// a changed string has the same length as the original
static inline uint32_t fusion_upper(uint32_t c) {
    if ((c >= 'a' && c <= 'z') || (c >= 0xE0 && c <= 0xFE && c != 0xF7)) return c - 32;
    return c == 0xFF ? 0x178 : c;
}
static inline uint32_t fusion_lower(uint32_t c) {
    if ((c >= 'A' && c <= 'Z') || (c >= 0xC0 && c <= 0xDE && c != 0xD7)) return c + 32;
    return c == 0x178 ? 0xFF : c;
}
// mode 0 lower, 1 upper, 2 capitalize (the first letter), 3 title (each word's first letter)
static inline fusion_string fusion_str_case(fusion_string s, int mode) {
    fusion_string r = fusion_str_make(s.data, s.len);
    bool word_start = true, done = false;
    for (int i = 0; i < r.len; ) {
        int n = fusion_utf8_size((unsigned char)r.data[i]);
        uint32_t c = (uint32_t)fusion_utf8_decode(r.data + i), m = c;
        bool letter = fusion_is_letter((fusion_char)c);
        if (mode == 0) m = fusion_lower(c);
        else if (mode == 1) m = fusion_upper(c);
        else if (mode == 2 && letter && !done) { m = fusion_upper(c); done = true; }
        else if (mode == 3 && letter && word_start) m = fusion_upper(c);
        if (mode == 3) word_start = fusion_is_space(r.data[i]);
        if (m != c) { char buf[4]; fusion_utf8_encode((fusion_char)m, buf); memcpy(r.data + i, buf, (size_t)n); }
        i += n;
    }
    return r;
}
static inline fusion_string fusion_str_toLower(fusion_string s) { return fusion_str_case(s, 0); }
static inline fusion_string fusion_str_toUpper(fusion_string s) { return fusion_str_case(s, 1); }
static inline fusion_string fusion_str_capitalize(fusion_string s) { return fusion_str_case(s, 2); }
static inline fusion_string fusion_str_toTitle(fusion_string s) { return fusion_str_case(s, 3); }

// Replace up to `limit` matches (-1 = all); an empty `old` changes nothing
static inline fusion_string fusion_str_replace_n(fusion_string s, fusion_string old, fusion_string with, int limit, const char* where) {
    int count = 0;
    if (old.len == 0) return fusion_str_make(s.data, s.len);
    for (int i = fusion_find(s, 0, old.data, old.len); i >= 0 && count != limit; i = fusion_find(s, i + old.len, old.data, old.len)) count++;
    int len = fusion_checked_size((long long)s.len + (long long)count * (with.len - old.len), "replace", where);
    if (len < 0) return FUSION_STR("");
    char* out = (char*)fusion_alloc((size_t)len + 1);
    int from = 0, o = 0;
    for (int k = 0; k < count; k++) {
        int i = fusion_find(s, from, old.data, old.len);
        memcpy(out + o, s.data + from, (size_t)(i - from)); o += i - from;
        memcpy(out + o, with.data, (size_t)with.len); o += with.len;
        from = i + old.len;
    }
    memcpy(out + o, s.data + from, (size_t)(s.len - from));
    return fusion_str_take(out, len);
}
static inline fusion_string fusion_str_replace(fusion_string s, fusion_string old, fusion_string with, const char* where) { return fusion_str_replace_n(s, old, with, -1, where); }
static inline fusion_string fusion_str_replaceFirst(fusion_string s, fusion_string old, fusion_string with, const char* where) { return fusion_str_replace_n(s, old, with, 1, where); }

static inline fusion_string fusion_str_insert(fusion_string s, int index, fusion_string part, const char* where) {
    if (index < 0 || index > s.chars) { fusion_fail(FUSION_KIND_IndexError, where, "insert(index %d) is outside the string (length %d)", index, s.chars); return FUSION_STR(""); }
    int at = fusion_utf8_offset(s, index);
    int len = fusion_checked_size((long long)s.len + part.len, "insert", where);
    if (len < 0) return FUSION_STR("");
    char* out = (char*)fusion_alloc((size_t)len + 1);
    memcpy(out, s.data, (size_t)at);
    memcpy(out + at, part.data, (size_t)part.len);
    memcpy(out + at + part.len, s.data + at, (size_t)(s.len - at));
    return fusion_str_take(out, len);
}
static inline fusion_string fusion_str_remove(fusion_string s, int start, int count, const char* where) {
    if (start < 0 || count < 0 || start > s.chars || count > s.chars - start) {
        fusion_fail(FUSION_KIND_IndexError, where, "remove(start %d, count %d) is outside the string (length %d)", start, count, s.chars);
        return FUSION_STR("");
    }
    int from = fusion_utf8_offset(s, start), to = fusion_utf8_offset(s, start + count);
    char* out = (char*)fusion_alloc((size_t)(s.len - (to - from)) + 1);
    memcpy(out, s.data, (size_t)from);
    memcpy(out + from, s.data + to, (size_t)(s.len - to));
    return fusion_str_take(out, s.len - (to - from));
}
static inline fusion_string fusion_str_repeat(fusion_string s, int n, const char* where) {
    if (n < 0) { fusion_fail(FUSION_KIND_RangeError, where, "repeat(%d): the count can't be negative", n); return FUSION_STR(""); }
    int len = fusion_checked_size((long long)s.len * n, "repeat", where);
    if (len < 0) return FUSION_STR("");
    char* out = (char*)fusion_alloc((size_t)len + 1);
    for (int k = 0; k < n; k++) memcpy(out + (size_t)k * s.len, s.data, (size_t)s.len);
    return fusion_str_take(out, len);
}
// By character: "caf\u00e9" -> "\u00e9fac" (a character's bytes stay in order)
static inline fusion_string fusion_str_reverse(fusion_string s) {
    char* out = (char*)fusion_alloc((size_t)s.len + 1);
    for (int i = 0; i < s.len; ) {
        int n = fusion_utf8_size((unsigned char)s.data[i]);
        if (n > s.len - i) n = s.len - i;
        memcpy(out + s.len - i - n, s.data + i, (size_t)n);
        i += n;
    }
    return fusion_str_take(out, s.len);
}
static inline fusion_string fusion_str_trimStart(fusion_string s) {
    int start = 0;
    while (start < s.len && fusion_is_space(s.data[start])) start++;
    return fusion_str_make(s.data + start, s.len - start);
}
static inline fusion_string fusion_str_trimEnd(fusion_string s) {
    int end = s.len;
    while (end > 0 && fusion_is_space(s.data[end - 1])) end--;
    return fusion_str_make(s.data, end);
}

// ---- Padding & alignment (18.3.6c) - widths count characters; a string already that wide
// or wider comes back unchanged
// mode 0: fill on the left (padLeft), 1: on the right (padRight), 2: both sides (center -
// an odd extra fill goes on the right)
static inline fusion_string fusion_str_pad(fusion_string s, int width, fusion_char fill, int mode, const char* name, const char* where) {
    if (width < 0) { fusion_fail(FUSION_KIND_RangeError, where, "%s(width %d): the width can't be negative", name, width); return FUSION_STR(""); }
    if (s.chars >= width) return fusion_str_make(s.data, s.len);
    char f[4];
    int fill_len = fusion_utf8_encode(fill, f), add = width - s.chars;
    int before = mode == 0 ? add : mode == 1 ? 0 : add / 2, after = add - before;
    int len = fusion_checked_size((long long)s.len + (long long)add * fill_len, name, where), o = 0;
    if (len < 0) return FUSION_STR("");
    char* out = (char*)fusion_alloc((size_t)len + 1);
    for (int k = 0; k < before; k++) { memcpy(out + o, f, (size_t)fill_len); o += fill_len; }
    memcpy(out + o, s.data, (size_t)s.len); o += s.len;
    for (int k = 0; k < after; k++) { memcpy(out + o, f, (size_t)fill_len); o += fill_len; }
    return fusion_str_take(out, len);
}
static inline fusion_string fusion_str_padLeft(fusion_string s, int width, fusion_char fill, const char* where) { return fusion_str_pad(s, width, fill, 0, "padLeft", where); }
static inline fusion_string fusion_str_padRight(fusion_string s, int width, fusion_char fill, const char* where) { return fusion_str_pad(s, width, fill, 1, "padRight", where); }
static inline fusion_string fusion_str_center(fusion_string s, int width, fusion_char fill, const char* where) { return fusion_str_pad(s, width, fill, 2, "center", where); }
// The first `width` characters - nothing is added (user decision 2026-10-10: an added "..."
// would surprise developers); a shorter string comes back unchanged
static inline fusion_string fusion_str_truncate(fusion_string s, int width, const char* where) {
    if (width < 0) { fusion_fail(FUSION_KIND_RangeError, where, "truncate(width %d): the width can't be negative", width); return FUSION_STR(""); }
    if (width > s.chars) width = s.chars;
    return fusion_str_make(s.data, fusion_utf8_offset(s, width));
}
// ---- Number bases (18.3.6d-1) - hex, binary, octal, any base 2-36. toHex / toBinary /
// toOctal write a negative number as its 32-bit two's complement pattern (C# style, user
// decision 2026-10-10): toHex(-1) -> "ffffffff"; reading that text back gives -1 again
static inline int fusion_digit_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    c = (char)(c | 32);
    return c >= 'a' && c <= 'z' ? c - 'a' + 10 : 99;
}
static inline bool fusion_check_base(int base, const char* name, const char* where) {
    if (base < 2 || base > 36) { fusion_fail(FUSION_KIND_RangeError, where, "%s: base %d is not between 2 and 36", name, base); return false; }
    return true;
}
// Digits of v in `base`, zero-padded to at least `width` digits, with an optional '-'
static inline fusion_string fusion_digits_text(uint32_t v, int base, bool negative, int width, const char* name, const char* where) {
    char digits[33];
    int n = 0;
    if (width < 0) { fusion_fail(FUSION_KIND_RangeError, where, "%s(width %d): the width can't be negative", name, width); return FUSION_STR(""); }
    do { digits[n++] = "0123456789abcdefghijklmnopqrstuvwxyz"[v % (uint32_t)base]; v /= (uint32_t)base; } while (v > 0);
    int pad = width > n ? width - n : 0;
    int len = fusion_checked_size((long long)negative + pad + n, name, where), o = 0;
    if (len < 0) return FUSION_STR("");
    char* out = (char*)fusion_alloc((size_t)len + 1);
    if (negative) out[o++] = '-';
    while (pad-- > 0) out[o++] = '0';
    while (n > 0) out[o++] = digits[--n];
    return fusion_str_take(out, len);
}
static inline fusion_string fusion_int_toHex(int x, int width, const char* where) { return fusion_digits_text((uint32_t)x, 16, false, width, "toHex", where); }
static inline fusion_string fusion_int_toBinary(int x, int width, const char* where) { return fusion_digits_text((uint32_t)x, 2, false, width, "toBinary", where); }
static inline fusion_string fusion_int_toOctal(int x, int width, const char* where) { return fusion_digits_text((uint32_t)x, 8, false, width, "toOctal", where); }
// Sign + digits: toBase(-255, 16) -> "-ff" (like Java's Integer.toString(n, 16))
static inline fusion_string fusion_int_toBase(int x, int base, int width, const char* where) {
    if (!fusion_check_base(base, "toBase", where)) return FUSION_STR("");
    uint32_t magnitude = x < 0 ? 0u - (uint32_t)x : (uint32_t)x;
    return fusion_digits_text(magnitude, base, x < 0, width, "toBase", where);
}
// The same from text holding a whole number: toHex("255") -> "ff"
static inline fusion_string fusion_str_toHex(fusion_string s, int width, const char* where) { return fusion_int_toHex(fusion_str_toInt(s, where), width, where); }
static inline fusion_string fusion_str_toBinary(fusion_string s, int width, const char* where) { return fusion_int_toBinary(fusion_str_toInt(s, where), width, where); }
static inline fusion_string fusion_str_toOctal(fusion_string s, int width, const char* where) { return fusion_int_toOctal(fusion_str_toInt(s, where), width, where); }
static inline fusion_string fusion_str_toBase(fusion_string s, int base, int width, const char* where) { return fusion_int_toBase(fusion_str_toInt(s, where), base, width, where); }

// Reading: an optional sign, an optional 0x / 0b / 0o prefix matching the base, digits in
// either case. Base 10 stays strictly signed; for bases 2, 8 and 16 a 32-bit pattern reads
// as its two's complement value ("ffffffff" -> -1); other bases are signed
static inline bool fusion_parse_base(fusion_string s, int base, int* out) {
    if (base == 10) return fusion_parse_int(s, out);
    int i = 0;
    bool negative = false;
    uint64_t v = 0;
    if (i < s.len && (s.data[i] == '+' || s.data[i] == '-')) negative = s.data[i++] == '-';
    if (i + 1 < s.len && s.data[i] == '0') {
        char p = (char)(s.data[i + 1] | 32);
        if ((p == 'x' && base == 16) || (p == 'b' && base == 2) || (p == 'o' && base == 8)) i += 2;
    }
    if (i >= s.len) return false;
    for (; i < s.len; i++) {
        int d = fusion_digit_value(s.data[i]);
        if (d >= base) return false;
        v = v * (uint64_t)base + (uint64_t)d;
        if (v > 0xFFFFFFFFull) return false;
    }
    if (negative) {
        if (v > 2147483648ull) return false;
        *out = (int)(0u - (uint32_t)v);
    } else if (base == 2 || base == 8 || base == 16) {
        *out = (int)(uint32_t)v;
    } else {
        if (v > 2147483647ull) return false;
        *out = (int)v;
    }
    return true;
}
static inline int fusion_str_parseInt(fusion_string s, int base, const char* where) {
    int v;
    if (!fusion_check_base(base, "parseInt", where)) return 0;
    if (!fusion_parse_base(s, base, &v)) {
        fusion_fail(FUSION_KIND_NumberFormatError, where, "'%.*s' is not a base-%d whole number that fits in an int (check with isInt(s, %d) first)", s.len, s.data, base, base);
        return 0;
    }
    return v;
}
static inline int fusion_str_fromHex(fusion_string s, const char* where) { return fusion_str_parseInt(s, 16, where); }
static inline int fusion_str_fromBinary(fusion_string s, const char* where) { return fusion_str_parseInt(s, 2, where); }
static inline int fusion_str_fromOctal(fusion_string s, const char* where) { return fusion_str_parseInt(s, 8, where); }
static inline bool fusion_str_isIntBase(fusion_string s, int base, const char* where) {
    int v;
    if (!fusion_check_base(base, "isInt", where)) return false;
    return fusion_parse_base(s, base, &v);
}

// Bytes as hex: bytesToHex("Hi") -> "4869" (the UTF-8 bytes, lowercase), and back
static inline fusion_string fusion_str_bytesToHex(fusion_string s, const char* where) {
    int len = fusion_checked_size((long long)s.len * 2, "bytesToHex", where);
    if (len < 0) return FUSION_STR("");
    char* out = (char*)fusion_alloc((size_t)len + 1);
    for (int i = 0; i < s.len; i++) {
        out[2 * i] = "0123456789abcdef"[(unsigned char)s.data[i] >> 4];
        out[2 * i + 1] = "0123456789abcdef"[(unsigned char)s.data[i] & 15];
    }
    return fusion_str_take(out, len);
}
// Valid UTF-8 (or plain ASCII in an ascii project): no overlong forms, surrogates or
// values past U+10FFFF
static inline bool fusion_utf8_valid(const char* p, int len) {
    for (int i = 0; i < len; ) {
        unsigned char b = (unsigned char)p[i];
        int n = b < 0x80 ? 1 : (b >= 0xC2 && b < 0xE0) ? 2 : (b >= 0xE0 && b < 0xF0) ? 3 : (b >= 0xF0 && b < 0xF5) ? 4 : 0;
#ifdef FUSION_ASCII
        if (n != 1) return false;
#endif
        if (n == 0 || i + n > len) return false;
        for (int k = 1; k < n; k++) if (((unsigned char)p[i + k] & 0xC0) != 0x80) return false;
        if (n > 1) {
            uint32_t c = (uint32_t)fusion_utf8_decode(p + i);
            if ((n == 3 && c < 0x800) || (n == 4 && (c < 0x10000 || c > 0x10FFFF)) || (c >= 0xD800 && c <= 0xDFFF)) return false;
        }
        i += n;
    }
    return true;
}
static inline fusion_string fusion_str_hexToBytes(fusion_string s, const char* where) {
    if (s.len % 2 != 0) { fusion_fail(FUSION_KIND_HexFormatError, where, "hexToBytes: '%.*s' has an odd number of hex digits", s.len, s.data); return FUSION_STR(""); }
    char* out = (char*)fusion_alloc((size_t)s.len / 2 + 1);
    for (int i = 0; i < s.len; i += 2) {
        int high = fusion_digit_value(s.data[i]), low = fusion_digit_value(s.data[i + 1]);
        if (high > 15 || low > 15) { fusion_dealloc(out); fusion_fail(FUSION_KIND_HexFormatError, where, "hexToBytes: '%.*s' is not hex text", s.len, s.data); return FUSION_STR(""); }
        out[i / 2] = (char)(high * 16 + low);
    }
    if (!fusion_utf8_valid(out, s.len / 2)) { fusion_dealloc(out); fusion_fail(FUSION_KIND_TextEncodingError, where, "hexToBytes: the bytes of '%.*s' are not valid text", s.len, s.data); return FUSION_STR(""); }
    return fusion_str_take(out, s.len / 2);
}
// ---- Number formatting (18.3.6d-2): formatNumber(n, pattern). A pattern starting with '%'
// is printf style ("%.2f", "%08.3f kg"); any other is Excel/.NET style ("#,##0.00",
// "$0.0", "0.0%"). Fusion checks the pattern itself and never hands it raw to C's printf -
// the same rules as src/semantic/number_patterns.py, which checks patterns written in
// the source when compiling
typedef struct { int start, end, min_int, min_dec, max_dec; bool group, percent; } fusion_number_pattern;

static inline const char* fusion_printf_pattern_problem(fusion_string p, int* at, int* end) {
    int found = 0;
    for (int i = 0; i < p.len; i++) {
        if (p.data[i] != '%') continue;
        if (i + 1 < p.len && p.data[i + 1] == '%') { i++; continue; }
        int j = i + 1, flags = 0, width = 0, precision = 0;
        while (j < p.len && p.data[j] != '\0' && strchr("-+ 0#", p.data[j])) { j++; if (++flags > 5) return "more than 5 flags"; }
        while (j < p.len && p.data[j] >= '0' && p.data[j] <= '9') { width = width * 10 + (p.data[j++] - '0'); if (width > 1000) return "a width over 1000"; }
        if (j < p.len && p.data[j] == '.') {
            j++;
            while (j < p.len && p.data[j] >= '0' && p.data[j] <= '9') { precision = precision * 10 + (p.data[j++] - '0'); if (precision > 1000) return "a precision over 1000"; }
        }
        if (j >= p.len) return "a '%' at the end has no conversion letter";
        if (p.data[j] == '*') return "'*' widths aren't allowed - write the number";
        if (p.data[j] == '\0' || !strchr("difeEgGxXo", p.data[j])) return "only the conversions d i f e E g G x X o are allowed";
        if (found) return "more than one number conversion";
        found = 1; *at = i; *end = j + 1; i = j;
    }
    return found ? NULL : "no number conversion such as %d or %.2f";
}

static inline const char* fusion_excel_pattern_problem(fusion_string p, fusion_number_pattern* np) {
    int first = -1, last = -1;
    bool dot = false;
    memset(np, 0, sizeof *np);
    for (int i = 0; i < p.len; i++)
        if (p.data[i] == '0' || p.data[i] == '#') { if (first < 0) first = i; last = i; }
    if (first < 0) return "no 0 or # digit placeholder";
    if (first > 0 && p.data[first - 1] == '.') first--;   // ".00" - the point belongs to the number
    for (int i = first; i <= last; i++) {
        char c = p.data[i];
        if (c == '0' || c == '#') {
            if (dot) { np->max_dec++; if (c == '0') np->min_dec = np->max_dec; }
            else if (c == '0') np->min_int++;
        } else if (c == '.') {
            if (dot) return "more than one decimal point";
            dot = true;
        } else if (c == ',') {
            if (dot) return "a ',' after the decimal point";
            np->group = true;
        } else {
            return "a character other than 0 # , . inside the number part";
        }
    }
    if (np->max_dec > 15) return "more than 15 decimal places";
    for (int i = 0; i < p.len; i++) if ((i < first || i > last) && p.data[i] == '%') np->percent = true;
    np->start = first; np->end = last + 1;
    return NULL;
}

// Excel/.NET style: rounds half away from zero on the decimal value shown (2.675 with "0.00"
// -> "2.68", as Excel does despite binary floating point)
static inline fusion_string fusion_format_excel(double v, fusion_string p, fusion_number_pattern np, const char* where) {
    if (np.percent) v *= 100.0;
    bool negative = v < 0;
    double x = negative ? -v : v;
    unsigned long long scale = 1;
    for (int k = 0; k < np.max_dec; k++) scale *= 10;
    x *= (double)scale;
    if (x >= 1e18) { fusion_fail(FUSION_KIND_RangeError, where, "formatNumber: %g is too large for this pattern", v); return FUSION_STR(""); }
    unsigned long long r = (unsigned long long)(x + 0.5 + 1e-9 * (x > 1.0 ? x : 1.0));
    unsigned long long whole = r / scale, frac = r % scale;
    char ib[24], fb[24];
    int il = snprintf(ib, sizeof ib, "%llu", whole), fl = np.max_dec > 15 ? 15 : np.max_dec;
    if (whole == 0 && np.min_int == 0) il = 0;   // "#.00" of 0.5 -> ".50"
    if (fl > 0) snprintf(fb, sizeof fb, "%0*llu", fl, frac % 1000000000000000ULL);   // at most 15 digits
    while (fl > np.min_dec && fb[fl - 1] == '0') fl--;
    int digits = il > np.min_int ? il : np.min_int;
    int groups = np.group && digits > 3 ? (digits - 1) / 3 : 0;
    bool minus = negative && r != 0;
    int len = minus + np.start + digits + groups + (fl > 0 ? fl + 1 : 0) + (p.len - np.end), o = 0;
    char* out = (char*)fusion_alloc((size_t)len + 1);
    if (minus) out[o++] = '-';
    memcpy(out + o, p.data, (size_t)np.start); o += np.start;
    for (int k = 0; k < digits; k++) {
        if (groups && k > 0 && (digits - k) % 3 == 0) out[o++] = ',';
        out[o++] = k < digits - il ? '0' : ib[k - (digits - il)];
    }
    if (fl > 0) { out[o++] = '.'; memcpy(out + o, fb, (size_t)fl); o += fl; }
    memcpy(out + o, p.data + np.end, (size_t)(p.len - np.end));
    return fusion_str_take(out, len);
}

// Copies pattern text, turning %% into %
static inline int fusion_copy_literal(char* out, const char* text, int len) {
    int o = 0;
    for (int i = 0; i < len; i++) { if (text[i] == '%' && i + 1 < len && text[i + 1] == '%') i++; if (out) out[o] = text[i]; o++; }
    return o;
}
// printf style: d i round half away from zero to a whole number; x X o show a whole number
// as its 32-bit pattern (like toHex); f e E g G as C prints them
static inline fusion_string fusion_format_printf(double v, fusion_string p, int at, int end, const char* where) {
    char spec[48], piece[1100];
    char conv = p.data[end - 1];
    int n = end - at - 1, piece_len;
    memcpy(spec, p.data + at, (size_t)n);
    double rounded = v < 0 ? v - 0.5 : v + 0.5;
    if (conv == 'd' || conv == 'i') {
        if (rounded >= 9.2e18 || rounded <= -9.2e18) { fusion_fail(FUSION_KIND_RangeError, where, "formatNumber: %g is too large for %%d", v); return FUSION_STR(""); }
        memcpy(spec + n, "lld", 4);
        piece_len = snprintf(piece, sizeof piece, spec, (long long)rounded);
    } else if (conv == 'x' || conv == 'X' || conv == 'o') {
        if (rounded >= 2147483648.0 || rounded <= -2147483649.0) { fusion_fail(FUSION_KIND_RangeError, where, "formatNumber: %g doesn't fit in an int for %%%c", v, conv); return FUSION_STR(""); }
        spec[n] = conv; spec[n + 1] = '\0';
        piece_len = snprintf(piece, sizeof piece, spec, (unsigned int)(int)(long long)rounded);
    } else {
        spec[n] = conv; spec[n + 1] = '\0';
        piece_len = snprintf(piece, sizeof piece, spec, v);
    }
    if (piece_len < 0 || piece_len >= (int)sizeof piece) { fusion_fail(FUSION_KIND_RangeError, where, "formatNumber: the result is too long"); return FUSION_STR(""); }
    int before = fusion_copy_literal(NULL, p.data, at), after = fusion_copy_literal(NULL, p.data + end, p.len - end);
    char* out = (char*)fusion_alloc((size_t)(before + piece_len + after) + 1);
    fusion_copy_literal(out, p.data, at);
    memcpy(out + before, piece, (size_t)piece_len);
    fusion_copy_literal(out + before + piece_len, p.data + end, p.len - end);
    return fusion_str_take(out, before + piece_len + after);
}

// `digits` - the significant digits the number really has: 7 for a float, 15 for a double or
// an int. Excel style reads the number at that precision first, so a float 2.675 (stored as
// 2.67499995...) rounds as the 2.675 that was written
static inline fusion_string fusion_formatNumber(double v, int digits, fusion_string p, const char* where) {
    if (v != v || v - v != 0) { fusion_fail(FUSION_KIND_RangeError, where, "formatNumber: the number isn't finite (infinity or not-a-number)"); return FUSION_STR(""); }
    const char* problem;
    if (p.len > 0 && p.data[0] == '%') {
        int at = 0, end = 0;
        problem = fusion_printf_pattern_problem(p, &at, &end);
        if (!problem) return fusion_format_printf(v, p, at, end, where);
    } else {
        fusion_number_pattern np;
        char decimal[40];
        problem = fusion_excel_pattern_problem(p, &np);
        snprintf(decimal, sizeof decimal, "%.*g", digits, v);
        if (!problem) return fusion_format_excel(strtod(decimal, NULL), p, np, where);
    }
    fusion_fail(FUSION_KIND_PatternError, where, "invalid number pattern \"%.*s\": %s", p.len, p.data, problem);
    return FUSION_STR("");
}
// ---- Compare (18.3.6e) - by character (code point); -1, 0 or 1. Ignoring case uses the
// ASCII + Latin-1 rules of toLower
static inline int fusion_sign(long long d) { return d < 0 ? -1 : d > 0; }
static inline int fusion_compare_chars(fusion_string a, fusion_string b, bool ignore_case) {
    int i = 0, j = 0;
    while (i < a.len && j < b.len) {
        uint32_t x = (uint32_t)fusion_utf8_decode(a.data + i), y = (uint32_t)fusion_utf8_decode(b.data + j);
        if (ignore_case) { x = fusion_lower(x); y = fusion_lower(y); }
        if (x != y) return x < y ? -1 : 1;
        i += fusion_utf8_size((unsigned char)a.data[i]);
        j += fusion_utf8_size((unsigned char)b.data[j]);
    }
    return fusion_sign((long long)(a.len - i) - (b.len - j));
}
static inline bool fusion_str_equalsIgnoreCase(fusion_string a, fusion_string b) { return fusion_compare_chars(a, b, true) == 0; }
static inline int fusion_str_compareIgnoreCase(fusion_string a, fusion_string b) { return fusion_compare_chars(a, b, true); }
// Natural order: runs of digits compare by value, so "file2" comes before "file10". When two
// strings differ only in leading zeros, the shorter run comes first ("2" before "02")
static inline int fusion_str_compareNatural(fusion_string a, fusion_string b, bool ignore_case) {
    int i = 0, j = 0, zeros = 0;
    while (i < a.len && j < b.len) {
        bool da = a.data[i] >= '0' && a.data[i] <= '9', db = b.data[j] >= '0' && b.data[j] <= '9';
        if (da && db) {
            int si = i, sj = j;
            while (i < a.len && a.data[i] == '0') i++;
            while (j < b.len && b.data[j] == '0') j++;
            int vi = i, vj = j;
            while (i < a.len && a.data[i] >= '0' && a.data[i] <= '9') i++;
            while (j < b.len && b.data[j] >= '0' && b.data[j] <= '9') j++;
            if (i - vi != j - vj) return i - vi < j - vj ? -1 : 1;       // more digits = bigger
            int c = memcmp(a.data + vi, b.data + vj, (size_t)(i - vi));
            if (c != 0) return c < 0 ? -1 : 1;
            if (zeros == 0 && i - si != j - sj) zeros = i - si < j - sj ? -1 : 1;
            continue;
        }
        uint32_t x = (uint32_t)fusion_utf8_decode(a.data + i), y = (uint32_t)fusion_utf8_decode(b.data + j);
        if (ignore_case) { x = fusion_lower(x); y = fusion_lower(y); }
        if (x != y) return x < y ? -1 : 1;
        i += fusion_utf8_size((unsigned char)a.data[i]);
        j += fusion_utf8_size((unsigned char)b.data[j]);
    }
    if ((a.len - i) != (b.len - j)) return (a.len - i) < (b.len - j) ? -1 : 1;
    return zeros;
}
// ---- Masking (design and decisions: spec "Masking", Task 18.3.6f) - by character
// formatMask: '#' a digit, 'A' a letter, '?' any character, '\' makes the next pattern
// character literal; other pattern characters are copied. Input that doesn't fit a slot is
// skipped ("555-123-4567" fills "(###) ###-####"); a literal appears only once the slot
// after it is filled; it stops when the input runs out - filled as far as it fits
static inline fusion_string fusion_str_formatMask(fusion_string s, fusion_string pattern) {
    char* out = (char*)fusion_alloc((size_t)pattern.len * 4 + (size_t)s.len + 1);
    int o = 0, pending = 0, i = 0;
    bool finished = true;
    for (int p = 0; p < pattern.len; ) {
        int n = fusion_utf8_size((unsigned char)pattern.data[p]);
        char kind = pattern.data[p];
        if (kind == '\\' && p + 1 < pattern.len) {          // an escaped literal
            p++;
            n = fusion_utf8_size((unsigned char)pattern.data[p]);
            kind = 0;
        }
        if (kind != '#' && kind != 'A' && kind != '?') {    // a literal: held until a slot fills
            memcpy(out + o + pending, pattern.data + p, (size_t)n); pending += n;
            p += n;
            continue;
        }
        while (i < s.len) {                                  // the next input that fits
            fusion_char c = fusion_utf8_decode(s.data + i);
            bool fits = kind == '?' || (kind == '#' && c >= '0' && c <= '9') || (kind == 'A' && fusion_is_letter(c));
            if (fits) break;
            i += fusion_utf8_size((unsigned char)s.data[i]);
        }
        if (i >= s.len) { finished = false; break; }         // out of input: stop here
        int m = fusion_utf8_size((unsigned char)s.data[i]);
        o += pending; pending = 0;
        memcpy(out + o, s.data + i, (size_t)m); o += m; i += m;
        p += n;
    }
    if (finished) o += pending;                              // the pattern's end was reached
    return fusion_str_take(out, o);
}
static inline fusion_string fusion_str_digitsOnly(fusion_string s) {
    char* out = (char*)fusion_alloc((size_t)s.len + 1);
    int o = 0;
    for (int i = 0; i < s.len; i++) if (s.data[i] >= '0' && s.data[i] <= '9') out[o++] = s.data[i];
    return fusion_str_take(out, o);
}
// mask: keep the first `keepStart` and last `keepEnd` characters, replace the rest with
// `with` (one for one - the length is kept)
static inline fusion_string fusion_mask_range(fusion_string s, int from, int to, fusion_char with) {
    char w[4];
    int wl = fusion_utf8_encode(with, w), k = 0, o = 0;
    char* out = (char*)fusion_alloc((size_t)s.len * 4 + 1);
    for (int i = 0; i < s.len; k++) {
        int n = fusion_utf8_size((unsigned char)s.data[i]);
        if (k >= from && k < to) { memcpy(out + o, w, (size_t)wl); o += wl; }
        else { memcpy(out + o, s.data + i, (size_t)n); o += n; }
        i += n;
    }
    return fusion_str_take(out, o);
}
static inline fusion_string fusion_str_mask(fusion_string s, int keepStart, int keepEnd, fusion_char with, const char* where) {
    if (keepStart < 0 || keepEnd < 0) { fusion_fail(FUSION_KIND_RangeError, where, "mask(%d, %d): the counts can't be negative", keepStart, keepEnd); return FUSION_STR(""); }
    if ((long long)keepStart + keepEnd >= s.chars) return fusion_str_make(s.data, s.len);
    return fusion_mask_range(s, keepStart, s.chars - keepEnd, with);
}
// maskEmail: the name before the last '@' keeps its first `keep` characters; the domain is
// kept. Text without an '@' is masked after its first `keep` characters
static inline fusion_string fusion_str_maskEmail(fusion_string s, int keep, fusion_char with, const char* where) {
    if (keep < 0) { fusion_fail(FUSION_KIND_RangeError, where, "maskEmail(%d): the count can't be negative", keep); return FUSION_STR(""); }
    int at = -1;
    for (int i = 0; i < s.len; i++) if (s.data[i] == '@') at = i;
    int name_chars = at < 0 ? s.chars : fusion_char_index(s, at);
    if (keep >= name_chars) return fusion_str_make(s.data, s.len);
    return fusion_mask_range(s, keep, name_chars, with);
}

// ---- Raw bytes (Task 18.3.8) - see src/codegen/c_bytes.py
typedef fusion_string fusion_bytes;
// A bytes value from a buffer of `len` bytes made with fusion_alloc(len + 1)
static inline fusion_bytes fusion_bytes_take(char* data, int len) {
    fusion_bytes r;
    data[len] = '\0';
    r.data = data; r.len = len; r.chars = len; r.owned = 1;
    return r;
}
static inline fusion_bytes fusion_bytes_make(const void* data, int len) {
    char* out = (char*)fusion_alloc((size_t)len + 1);
    if (len > 0) memcpy(out, data, (size_t)len);
    return fusion_bytes_take(out, len);
}
static inline uint8_t fusion_toByte(int n, const char* where) {
    if (n < 0 || n > 255) { fusion_fail(FUSION_KIND_RangeError, where, "%d doesn't fit in a byte (0-255)", n); return 0; }
    return (uint8_t)n;
}
static inline uint8_t fusion_bytes_at(fusion_bytes b, int i, const char* where) {
    if (i < 0 || i >= b.len) { fusion_fail(FUSION_KIND_IndexError, where, "byte %d is outside the bytes (length %d)", i, b.len); return 0; }
    return (uint8_t)b.data[i];
}
// b[i] = v - edits in place; a bytes value always owns its memory when it isn't empty
static inline void fusion_bytes_put(fusion_bytes* b, int i, uint8_t v, const char* where) {
    if (i < 0 || i >= b->len) { fusion_fail(FUSION_KIND_IndexError, where, "byte %d is outside the bytes (length %d)", i, b->len); return; }
    b->data[i] = (char)v;
}
static inline fusion_bytes fusion_newBytes(int n, uint8_t fill, const char* where) {
    if (n < 0) { fusion_fail(FUSION_KIND_RangeError, where, "newBytes(%d): the count can't be negative", n); return FUSION_STR(""); }
    char* out = (char*)fusion_alloc((size_t)n + 1);
    memset(out, fill, (size_t)n);
    return fusion_bytes_take(out, n);
}

// toBytes - a string's UTF-8 bytes, a char's, an int's 4 bytes, or a single byte
static inline void fusion_put_uint(char* p, uint32_t v, int size, bool big) {
    for (int k = 0; k < size; k++) p[big ? size - 1 - k : k] = (char)((v >> (8 * k)) & 0xFF);
}
static inline uint32_t fusion_get_uint(const char* p, int size, bool big) {
    uint32_t v = 0;
    for (int k = 0; k < size; k++) v |= (uint32_t)(uint8_t)p[big ? size - 1 - k : k] << (8 * k);
    return v;
}
static inline fusion_bytes fusion_str_toBytes(fusion_string s, bool big) { (void)big; return fusion_bytes_make(s.data, s.len); }
static inline fusion_bytes fusion_char_toBytes(fusion_char c, bool big) { char buf[4]; (void)big; return fusion_bytes_make(buf, fusion_utf8_encode(c, buf)); }
static inline fusion_bytes fusion_byte_toBytes(uint8_t v, bool big) { (void)big; return fusion_bytes_make(&v, 1); }
static inline fusion_bytes fusion_int_toBytes(int n, bool big) { char buf[4]; fusion_put_uint(buf, (uint32_t)n, 4, big); return fusion_bytes_make(buf, 4); }

// Joining: bytes + bytes, bytes + byte, byte + bytes
static inline fusion_bytes fusion_bytes_concat(fusion_bytes a, fusion_bytes b) {
    char* out = (char*)fusion_alloc((size_t)a.len + (size_t)b.len + 1);
    memcpy(out, a.data, (size_t)a.len);
    memcpy(out + a.len, b.data, (size_t)b.len);
    return fusion_bytes_take(out, a.len + b.len);
}
static inline fusion_bytes fusion_bytes_append(fusion_bytes a, uint8_t v) { char c = (char)v; fusion_bytes one = {&c, 1, 1, 0}; return fusion_bytes_concat(a, one); }
static inline fusion_bytes fusion_byte_prepend(uint8_t v, fusion_bytes b) { char c = (char)v; fusion_bytes one = {&c, 1, 1, 0}; return fusion_bytes_concat(one, b); }

static inline fusion_bytes fusion_bytes_slice(fusion_bytes b, int start, int count, const char* where) {
    if (start < 0 || count < 0 || start > b.len || count > b.len - start) {
        fusion_fail(FUSION_KIND_IndexError, where, "slice(start %d, count %d) is outside the bytes (length %d)", start, count, b.len);
        return FUSION_STR("");
    }
    return fusion_bytes_make(b.data + start, count);
}
// Byte position of the first match at or after `from`, or -1
static inline int fusion_bytes_indexOf(fusion_bytes b, fusion_bytes pattern, int from) {
    if (from < 0) from = 0;
    if (from > b.len) return -1;
    return fusion_find(b, from, pattern.data, pattern.len);
}

// Numbers inside bytes: getInt / setInt (4 bytes), getInt16 / getUInt16 / setInt16 (2)
static inline bool fusion_bytes_room(fusion_bytes b, int at, int size, const char* name, const char* where) {
    if (at < 0 || at > b.len - size) {
        fusion_fail(FUSION_KIND_IndexError, where, "%s(at %d) needs %d bytes there, but the bytes have length %d", name, at, size, b.len);
        return false;
    }
    return true;
}
static inline int fusion_bytes_getInt(fusion_bytes b, int at, bool big, const char* where) {
    if (!fusion_bytes_room(b, at, 4, "getInt", where)) return 0;
    return (int)fusion_get_uint(b.data + at, 4, big);
}
static inline int fusion_bytes_getInt16(fusion_bytes b, int at, bool big, const char* where) {
    if (!fusion_bytes_room(b, at, 2, "getInt16", where)) return 0;
    return (int)(int16_t)fusion_get_uint(b.data + at, 2, big);
}
static inline int fusion_bytes_getUInt16(fusion_bytes b, int at, bool big, const char* where) {
    if (!fusion_bytes_room(b, at, 2, "getUInt16", where)) return 0;
    return (int)fusion_get_uint(b.data + at, 2, big);
}
static inline void fusion_bytes_setInt(fusion_bytes* b, int at, int v, bool big, const char* where) {
    if (!fusion_bytes_room(*b, at, 4, "setInt", where)) return;
    fusion_put_uint(b->data + at, (uint32_t)v, 4, big);
}
// Accepts -32768 to 65535: the value as either a signed or an unsigned 16-bit number
static inline void fusion_bytes_setInt16(fusion_bytes* b, int at, int v, bool big, const char* where) {
    if (!fusion_bytes_room(*b, at, 2, "setInt16", where)) return;
    if (v < -32768 || v > 65535) { fusion_fail(FUSION_KIND_RangeError, where, "setInt16: %d doesn't fit in 16 bits", v); return; }
    fusion_put_uint(b->data + at, (uint32_t)v, 2, big);
}

// Back to text: the bytes must be valid text (UTF-8, or ASCII in an ascii project)
static inline bool fusion_bytes_isText(fusion_bytes b) { return fusion_utf8_valid(b.data, b.len); }
static inline fusion_string fusion_bytes_toString(fusion_bytes b, const char* where) {
    if (!fusion_utf8_valid(b.data, b.len)) { fusion_fail(FUSION_KIND_TextEncodingError, where, "these %d bytes are not valid text (check with isText first)", b.len); return FUSION_STR(""); }
    return fusion_str_make(b.data, b.len);
}
// Hex: rawToHex(b) -> "6b6b69" (lowercase, nothing added); hexToRaw("6b6b69") -> bytes
static inline fusion_string fusion_bytes_rawToHex(fusion_bytes b, const char* where) { return fusion_str_bytesToHex(b, where); }
static inline fusion_bytes fusion_str_hexToRaw(fusion_string s, const char* where) {
    if (s.len % 2 != 0) { fusion_fail(FUSION_KIND_HexFormatError, where, "hexToRaw: '%.*s' has an odd number of hex digits", s.len, s.data); return FUSION_STR(""); }
    char* out = (char*)fusion_alloc((size_t)s.len / 2 + 1);
    for (int i = 0; i < s.len; i += 2) {
        int high = fusion_digit_value(s.data[i]), low = fusion_digit_value(s.data[i + 1]);
        if (high > 15 || low > 15) { fusion_dealloc(out); fusion_fail(FUSION_KIND_HexFormatError, where, "hexToRaw: '%.*s' is not hex text", s.len, s.data); return FUSION_STR(""); }
        out[i / 2] = (char)(high * 16 + low);
    }
    return fusion_bytes_take(out, s.len / 2);
}
// ---- The program's arguments, console input, exit (Task 18.5.4)
// main(string... args): the arguments without the program's name and --headless. On
// Windows they are read as UTF-16 and turned into UTF-8 (argv uses the old code page and
// would garble accented text). They live as long as the program - never freed
#ifdef _WIN32
#include <wchar.h>
__declspec(dllimport) wchar_t* __stdcall GetCommandLineW(void);
__declspec(dllimport) wchar_t** __stdcall CommandLineToArgvW(const wchar_t* line, int* count);
__declspec(dllimport) int __stdcall WideCharToMultiByte(unsigned int page, unsigned long flags, const wchar_t* text, int len, char* out, int size, const char* fallback, int* used);
#endif
static inline fusion_string* fusion_program_args(int argc, char** argv, int* count) {
    fusion_string* args = (fusion_string*)malloc(sizeof(fusion_string) * (size_t)(argc > 0 ? argc : 1));
    int n = 0;
#ifdef _WIN32
    int wide_count = 0;
    wchar_t** wide = CommandLineToArgvW(GetCommandLineW(), &wide_count);
    (void)argv;
    for (int i = 1; wide && i < wide_count && i < argc; i++) {
        int size = WideCharToMultiByte(65001, 0, wide[i], -1, NULL, 0, NULL, NULL);
        char* text = (char*)malloc((size_t)size);
        WideCharToMultiByte(65001, 0, wide[i], -1, text, size, NULL, NULL);
        if (strcmp(text, "--headless") == 0) { free(text); continue; }
        args[n].data = text; args[n].len = size - 1;
        args[n].chars = fusion_utf8_count(text, size - 1); args[n].owned = 0; n++;
    }
#else
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--headless") == 0) continue;
        int size = 0;
        while (argv[i][size]) size++;
        args[n].data = argv[i]; args[n].len = size;
        args[n].chars = fusion_utf8_count(argv[i], args[n].len); args[n].owned = 0; n++;
    }
#endif
    *count = n;
    return args;
}
// readLine(): the next line typed (or piped) in, without "\n" / "\r\n"; "" at the end of input
static inline fusion_string fusion_readLine(void) {
    int cap = 64, len = 0, c;
    char* text = (char*)fusion_alloc((size_t)cap + 1);
    fflush(stdout);
    while ((c = getchar()) != EOF && c != '\n') {
        if (len == cap) {
            char* bigger = (char*)fusion_alloc((size_t)cap * 2 + 1);
            memcpy(bigger, text, (size_t)len);
            fusion_dealloc(text);
            text = bigger; cap *= 2;
        }
        text[len++] = (char)c;
    }
    if (len > 0 && text[len - 1] == '\r') len--;
    return fusion_str_take(text, len);
}
// isEndOfInput(): true when there is nothing left to read
static inline bool fusion_isEndOfInput(void) {
    int c = getchar();
    if (c == EOF) return true;
    ungetc(c, stdin);
    return false;
}
// exit(code): end the program now with an exit code (values still alive aren't leaks)
static inline void fusion_exit(int code) {
    fflush(stdout);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(code);
}

// ---- Files (Task 18.5.5) - see src/codegen/c_files.py
#include <errno.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall MultiByteToWideChar(unsigned int page, unsigned long flags, const char* text, int len, wchar_t* out, int size);
__declspec(dllimport) unsigned long __stdcall GetFileAttributesW(const wchar_t* path);
#else
#include <sys/stat.h>
#include <sys/wait.h>
#endif
// A NUL-terminated copy of a path (malloc - freed by the caller)
static inline char* fusion_path_text(fusion_string path) {
    char* p = (char*)malloc((size_t)path.len + 1);
    memcpy(p, path.data, (size_t)path.len);
    p[path.len] = '\0';
    return p;
}
#ifdef _WIN32
static inline wchar_t* fusion_wide(const char* text) {
    int n = MultiByteToWideChar(65001, 0, text, -1, NULL, 0);
    wchar_t* w = (wchar_t*)malloc(sizeof(wchar_t) * (size_t)(n > 0 ? n : 1));
    if (n <= 0) { w[0] = 0; return w; }
    MultiByteToWideChar(65001, 0, text, -1, w, n);
    return w;
}
#endif
static inline FILE* fusion_open_file(fusion_string path, const char* mode, const char* what, const char* where) {
    char* p = fusion_path_text(path);
    FILE* f;
#ifdef _WIN32
    wchar_t* w = fusion_wide(p);
    wchar_t wmode[4] = {0};
    for (int i = 0; mode[i] && i < 3; i++) wmode[i] = (wchar_t)mode[i];
    f = _wfopen(w, wmode);
    free(w);
#else
    f = fopen(p, mode);
#endif
    if (!f) {
        // Why it won't open decides the error type (Task 26.12)
        int kind = errno == ENOENT ? FUSION_KIND_FileNotFoundError
                 : errno == EACCES || errno == EPERM ? FUSION_KIND_PermissionError
                 : mode[0] == 'r' ? FUSION_KIND_FileReadError : FUSION_KIND_FileWriteError;
        fusion_file_fail(kind, where, path, "%s: can't open '%s' (%s)", what, p, strerror(errno));
    }
    free(p);
    return f;   // NULL when it can't be opened - the error is on its way
}
// The whole file in a fusion_alloc buffer with room for a final '\0'
static inline char* fusion_read_all(fusion_string path, int* len, const char* what, const char* where) {
    FILE* f = fusion_open_file(path, "rb", what, where);
    if (!f) return NULL;
    int cap = 4096, n = 0;
    char* data = (char*)fusion_alloc((size_t)cap + 1);
    size_t got;
    while ((got = fread(data + n, 1, (size_t)(cap - n), f)) > 0) {
        n += (int)got;
        if (n == cap) {
            if (cap > 1073741823) { fclose(f); fusion_dealloc(data); fusion_file_fail(FUSION_KIND_FileTooLargeError, where, path, "%s: the file is larger than 2 GB", what); return NULL; }
            char* bigger = (char*)fusion_alloc((size_t)cap * 2 + 1);
            memcpy(bigger, data, (size_t)n);
            fusion_dealloc(data);
            data = bigger; cap *= 2;
        }
    }
    int failed = ferror(f);
    fclose(f);
    if (failed) { fusion_dealloc(data); fusion_file_fail(FUSION_KIND_FileReadError, where, path, "%s: reading failed (%s)", what, strerror(errno)); return NULL; }
    *len = n;
    return data;
}
static inline fusion_bytes fusion_readBytes(fusion_string path, const char* where) {
    int len;
    char* data = fusion_read_all(path, &len, "readBytes", where);
    if (!data) return FUSION_STR("");
    return fusion_bytes_take(data, len);
}
static inline fusion_string fusion_readText(fusion_string path, const char* where) {
    int len, skip = 0;
    char* data = fusion_read_all(path, &len, "readText", where);
    if (!data) return FUSION_STR("");
    if (len >= 3 && (unsigned char)data[0] == 0xEF && (unsigned char)data[1] == 0xBB && (unsigned char)data[2] == 0xBF) skip = 3;
    if (!fusion_utf8_valid(data + skip, len - skip)) {
        char* p = fusion_path_text(path);
        fusion_dealloc(data);
        fusion_fail(FUSION_KIND_TextEncodingError, where, "readText: '%s' is not valid text - use readBytes for a binary file", p);
        free(p);
        return FUSION_STR("");
    }
    if (skip) memmove(data, data + 3, (size_t)(len - 3));
    return fusion_str_take(data, len - skip);
}
static inline void fusion_write_all(fusion_string path, const char* mode, const char* data, int len, const char* what, const char* where) {
    FILE* f = fusion_open_file(path, mode, what, where);
    if (!f) return;
    size_t wrote = len > 0 ? fwrite(data, 1, (size_t)len, f) : 0;
    int closed = fclose(f);
    if ((int)wrote != len || closed != 0) {
        char* p = fusion_path_text(path);
        fusion_file_fail(FUSION_KIND_FileWriteError, where, path, "%s: writing '%s' failed (%s)", what, p, strerror(errno));
        free(p);
    }
}
static inline void fusion_writeText(fusion_string path, fusion_string text, const char* where) { fusion_write_all(path, "wb", text.data, text.len, "writeText", where); }
static inline void fusion_appendText(fusion_string path, fusion_string text, const char* where) { fusion_write_all(path, "ab", text.data, text.len, "appendText", where); }
static inline void fusion_writeBytes(fusion_string path, fusion_bytes b, const char* where) { fusion_write_all(path, "wb", b.data, b.len, "writeBytes", where); }
// True for an existing file (not a folder)
static inline bool fusion_fileExists(fusion_string path) {
    char* p = fusion_path_text(path);
    bool found;
#ifdef _WIN32
    wchar_t* w = fusion_wide(p);
    unsigned long attributes = GetFileAttributesW(w);
    free(w);
    found = attributes != 0xFFFFFFFFul && !(attributes & 0x10ul);
#else
    struct stat info;
    found = stat(p, &info) == 0 && S_ISREG(info.st_mode);
#endif
    free(p);
    return found;
}
static inline void fusion_deleteFile(fusion_string path, const char* where) {
    char* p = fusion_path_text(path);
    int failed;
#ifdef _WIN32
    wchar_t* w = fusion_wide(p);
    failed = _wremove(w);
    free(w);
#else
    failed = remove(p);
#endif
    if (failed) fusion_file_fail(errno == ENOENT ? FUSION_KIND_FileNotFoundError : FUSION_KIND_DeleteError,
                                 where, path, "deleteFile: can't delete '%s' (%s)", p, strerror(errno));
    free(p);
}
// run(command) (Task 28.1.1): the command goes to the system shell (cmd /c on Windows,
// /bin/sh -c elsewhere); waits until it ends and returns its exit code. A program that
// runs and fails is not an error - its code comes back. Only a shell that can't be started
// is a ProcessError. Output already printed is flushed first, so lines stay in order.
// On Windows the whole command gets one more pair of quotes: cmd /c strips exactly that
// pair, so a command like "C:/My Apps/x.exe" "a b" runs as written.
static inline int fusion_run(fusion_string command, const char* where) {
    char* c = fusion_path_text(command);
    int code;
    fflush(NULL);
#ifdef _WIN32
    char* quoted = (char*)malloc((size_t)command.len + 3);
    quoted[0] = '"';
    memcpy(quoted + 1, c, (size_t)command.len);
    quoted[command.len + 1] = '"';
    quoted[command.len + 2] = '\0';
    wchar_t* w = fusion_wide(quoted);
    free(quoted);
    code = _wsystem(w);
    free(w);
#else
    int status = system(c);
    code = status == -1 ? -1 : WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
#endif
    if (code == -1) fusion_fail(FUSION_KIND_ProcessError, where, "run: can't start '%s' (%s)",
                                c, strerror(errno));
    free(c);
    return code;
}

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
    {"Error", -1, NULL, NULL},
    {"ArithmeticError", 0, NULL, NULL},
    {"DivideByZeroError", 1, NULL, NULL},
    {"FormatError", 0, NULL, NULL},
    {"NumberFormatError", 3, NULL, NULL},
    {"PatternError", 3, NULL, NULL},
    {"HexFormatError", 3, NULL, NULL},
    {"TextEncodingError", 3, NULL, NULL},
    {"ValueError", 0, NULL, NULL},
    {"RangeError", 8, NULL, NULL},
    {"UnknownValueError", 8, NULL, NULL},
    {"LookupError", 0, NULL, NULL},
    {"IndexError", 11, NULL, NULL},
    {"KeyError", 11, NULL, NULL},
    {"FileError", 0, fusion_errdata_fu_FileError_copy, fusion_errdata_fu_FileError_free},
    {"FileNotFoundError", 14, fusion_errdata_fu_FileError_copy, fusion_errdata_fu_FileError_free},
    {"PermissionError", 14, fusion_errdata_fu_FileError_copy, fusion_errdata_fu_FileError_free},
    {"FileReadError", 14, fusion_errdata_fu_FileError_copy, fusion_errdata_fu_FileError_free},
    {"FileWriteError", 14, fusion_errdata_fu_FileError_copy, fusion_errdata_fu_FileError_free},
    {"FileTooLargeError", 14, fusion_errdata_fu_FileError_copy, fusion_errdata_fu_FileError_free},
    {"DeleteError", 14, fusion_errdata_fu_FileError_copy, fusion_errdata_fu_FileError_free},
    {"LimitError", 0, NULL, NULL},
    {"StringTooLongError", 21, NULL, NULL},
    {"ResultTooLargeError", 21, NULL, NULL},
    {"OverflowError", 1, NULL, NULL},
    {"StackOverflowError", 21, NULL, NULL},
    {"ModifiedWhileLoopingError", 8, NULL, NULL},
    {"PrecisionError", 1, NULL, NULL},
    {"ProcessError", 0, NULL, NULL},
    {"NullError", 0, NULL, NULL},
};
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

#endif  // FUSION_RUNTIME_H
