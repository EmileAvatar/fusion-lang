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
// ---- Number bases (18.3.6d-1) - hex, binary, octal, any base 2-36. toHex / toBinary /
// toOctal write a negative number as its 32-bit two's complement pattern (C# style, user
// decision 2026-10-10): toHex(-1) -> "ffffffff"; reading that text back gives -1 again
static inline int fusion_digit_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    c = (char)(c | 32);
    return c >= 'a' && c <= 'z' ? c - 'a' + 10 : 99;
}
static inline void fusion_check_base(int base, const char* name, const char* where) {
    if (base < 2 || base > 36) fusion_runtime_error(where, "%s: base %d is not between 2 and 36", name, base);
}
// Digits of v in `base`, zero-padded to at least `width` digits, with an optional '-'
static inline fusion_string fusion_digits_text(uint32_t v, int base, bool negative, int width, const char* name, const char* where) {
    char digits[33];
    int n = 0;
    if (width < 0) fusion_runtime_error(where, "%s(width %d): the width can't be negative", name, width);
    do { digits[n++] = "0123456789abcdefghijklmnopqrstuvwxyz"[v % (uint32_t)base]; v /= (uint32_t)base; } while (v > 0);
    int pad = width > n ? width - n : 0;
    int len = fusion_checked_size((long long)negative + pad + n, name, where), o = 0;
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
    fusion_check_base(base, "toBase", where);
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
    fusion_check_base(base, "parseInt", where);
    if (!fusion_parse_base(s, base, &v))
        fusion_runtime_error(where, "'%.*s' is not a base-%d whole number that fits in an int (check with isInt(s, %d) first)", s.len, s.data, base, base);
    return v;
}
static inline int fusion_str_fromHex(fusion_string s, const char* where) { return fusion_str_parseInt(s, 16, where); }
static inline int fusion_str_fromBinary(fusion_string s, const char* where) { return fusion_str_parseInt(s, 2, where); }
static inline int fusion_str_fromOctal(fusion_string s, const char* where) { return fusion_str_parseInt(s, 8, where); }
static inline bool fusion_str_isIntBase(fusion_string s, int base, const char* where) {
    int v;
    fusion_check_base(base, "isInt", where);
    return fusion_parse_base(s, base, &v);
}

// Bytes as hex: bytesToHex("Hi") -> "4869" (the UTF-8 bytes, lowercase), and back
static inline fusion_string fusion_str_bytesToHex(fusion_string s, const char* where) {
    int len = fusion_checked_size((long long)s.len * 2, "bytesToHex", where);
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
    if (s.len % 2 != 0) fusion_runtime_error(where, "hexToBytes: '%.*s' has an odd number of hex digits", s.len, s.data);
    char* out = (char*)fusion_alloc((size_t)s.len / 2 + 1);
    for (int i = 0; i < s.len; i += 2) {
        int high = fusion_digit_value(s.data[i]), low = fusion_digit_value(s.data[i + 1]);
        if (high > 15 || low > 15) { fusion_dealloc(out); fusion_runtime_error(where, "hexToBytes: '%.*s' is not hex text", s.len, s.data); }
        out[i / 2] = (char)(high * 16 + low);
    }
    if (!fusion_utf8_valid(out, s.len / 2)) { fusion_dealloc(out); fusion_runtime_error(where, "hexToBytes: the bytes of '%.*s' are not valid text", s.len, s.data); }
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
    if (x >= 1e18) fusion_runtime_error(where, "formatNumber: %g is too large for this pattern", v);
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
        if (rounded >= 9.2e18 || rounded <= -9.2e18) fusion_runtime_error(where, "formatNumber: %g is too large for %%d", v);
        memcpy(spec + n, "lld", 4);
        piece_len = snprintf(piece, sizeof piece, spec, (long long)rounded);
    } else if (conv == 'x' || conv == 'X' || conv == 'o') {
        if (rounded >= 2147483648.0 || rounded <= -2147483649.0) fusion_runtime_error(where, "formatNumber: %g doesn't fit in an int for %%%c", v, conv);
        spec[n] = conv; spec[n + 1] = '\0';
        piece_len = snprintf(piece, sizeof piece, spec, (unsigned int)(int)(long long)rounded);
    } else {
        spec[n] = conv; spec[n + 1] = '\0';
        piece_len = snprintf(piece, sizeof piece, spec, v);
    }
    if (piece_len < 0 || piece_len >= (int)sizeof piece) fusion_runtime_error(where, "formatNumber: the result is too long");
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
    if (v != v || v - v != 0) fusion_runtime_error(where, "formatNumber: the number isn't finite (infinity or not-a-number)");
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
    fusion_runtime_error(where, "invalid number pattern \"%.*s\": %s", p.len, p.data, problem);
    return p;
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
'''
