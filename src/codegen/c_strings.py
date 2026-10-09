"""The versatile string functions (Task 18.3.6), as C appended to the runtime prelude.

Each function returns a new value and leaves its input unchanged. Positions and counts are
characters (UTF-8, Task 18.3.2b), with the ASCII fast path where it matters. Letters are
ASCII + Latin-1 (user decision 2026-10-09; full Unicode tables later). "Up to n" functions
(left, right, ...) clamp quietly; a negative count stops with a run-time error.

The Fusion-side names, signatures and optional arguments are in
src/semantic/name_resolver.py; the Fusion name -> C function table is
CCodeGenerator._STRING_BUILTINS.
"""

STRING_LIBRARY = r'''
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
    if (n < 0) fusion_runtime_error(where, "left(%d): the count can't be negative", n);
    if (n > s.chars) n = s.chars;
    return fusion_str_make(s.data, fusion_utf8_offset(s, n));
}
static inline fusion_string fusion_str_right(fusion_string s, int n, const char* where) {
    if (n < 0) fusion_runtime_error(where, "right(%d): the count can't be negative", n);
    if (n > s.chars) n = s.chars;
    int from = fusion_utf8_offset(s, s.chars - n);
    return fusion_str_make(s.data + from, s.len - from);
}
'''
