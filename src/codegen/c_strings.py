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
    if (len > 2147483646LL) fusion_runtime_error(where, "%s: the result would be longer than 2,147,483,646 bytes", name);
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
    if (index < 0 || index > s.chars) fusion_runtime_error(where, "insert(index %d) is outside the string (length %d)", index, s.chars);
    int at = fusion_utf8_offset(s, index);
    int len = fusion_checked_size((long long)s.len + part.len, "insert", where);
    char* out = (char*)fusion_alloc((size_t)len + 1);
    memcpy(out, s.data, (size_t)at);
    memcpy(out + at, part.data, (size_t)part.len);
    memcpy(out + at + part.len, s.data + at, (size_t)(s.len - at));
    return fusion_str_take(out, len);
}
static inline fusion_string fusion_str_remove(fusion_string s, int start, int count, const char* where) {
    if (start < 0 || count < 0 || start > s.chars || count > s.chars - start)
        fusion_runtime_error(where, "remove(start %d, count %d) is outside the string (length %d)", start, count, s.chars);
    int from = fusion_utf8_offset(s, start), to = fusion_utf8_offset(s, start + count);
    char* out = (char*)fusion_alloc((size_t)(s.len - (to - from)) + 1);
    memcpy(out, s.data, (size_t)from);
    memcpy(out + from, s.data + to, (size_t)(s.len - to));
    return fusion_str_take(out, s.len - (to - from));
}
static inline fusion_string fusion_str_repeat(fusion_string s, int n, const char* where) {
    if (n < 0) fusion_runtime_error(where, "repeat(%d): the count can't be negative", n);
    int len = fusion_checked_size((long long)s.len * n, "repeat", where);
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
    if (width < 0) fusion_runtime_error(where, "%s(width %d): the width can't be negative", name, width);
    if (s.chars >= width) return fusion_str_make(s.data, s.len);
    char f[4];
    int fill_len = fusion_utf8_encode(fill, f), add = width - s.chars;
    int before = mode == 0 ? add : mode == 1 ? 0 : add / 2, after = add - before;
    int len = fusion_checked_size((long long)s.len + (long long)add * fill_len, name, where), o = 0;
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
    if (width < 0) fusion_runtime_error(where, "truncate(width %d): the width can't be negative", width);
    if (width > s.chars) width = s.chars;
    return fusion_str_make(s.data, fusion_utf8_offset(s, width));
}
'''
