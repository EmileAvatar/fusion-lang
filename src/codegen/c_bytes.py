"""Raw bytes (Task 18.3.8), as C appended to the runtime prelude after the string library.

`bytes` is a growable array of raw bytes. In C it is the same struct as a string (data,
length, owned), so the string rules for copying, moving and freeing apply unchanged - but
it holds any bytes at all (no UTF-8 rule, no [strings] max_length) and can be edited in
place (`b[i] = 0x69`). `chars` always equals `len`. `byte` is one raw byte, uint8_t, 0-255
(user decision 2026-10-10: unsigned, as in C#, Go, Rust and Python).

Byte order for ints: little-endian by default, `bigEndian = true` for network order (user
decision 2026-10-10). Nothing is ever cut silently: a value that doesn't fit a byte, or a
position outside the bytes, is a run-time error.
"""

BYTES_LIBRARY = r'''
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
    if (n < 0 || n > 255) fusion_runtime_error(where, "%d doesn't fit in a byte (0-255)", n);
    return (uint8_t)n;
}
static inline uint8_t fusion_bytes_at(fusion_bytes b, int i, const char* where) {
    if (i < 0 || i >= b.len) fusion_runtime_error(where, "byte %d is outside the bytes (length %d)", i, b.len);
    return (uint8_t)b.data[i];
}
// b[i] = v - edits in place; a bytes value always owns its memory when it isn't empty
static inline void fusion_bytes_put(fusion_bytes* b, int i, uint8_t v, const char* where) {
    if (i < 0 || i >= b->len) fusion_runtime_error(where, "byte %d is outside the bytes (length %d)", i, b->len);
    b->data[i] = (char)v;
}
static inline fusion_bytes fusion_newBytes(int n, uint8_t fill, const char* where) {
    if (n < 0) fusion_runtime_error(where, "newBytes(%d): the count can't be negative", n);
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
    if (start < 0 || count < 0 || start > b.len || count > b.len - start)
        fusion_runtime_error(where, "slice(start %d, count %d) is outside the bytes (length %d)", start, count, b.len);
    return fusion_bytes_make(b.data + start, count);
}
// Byte position of the first match at or after `from`, or -1
static inline int fusion_bytes_indexOf(fusion_bytes b, fusion_bytes pattern, int from) {
    if (from < 0) from = 0;
    if (from > b.len) return -1;
    return fusion_find(b, from, pattern.data, pattern.len);
}

// Numbers inside bytes: getInt / setInt (4 bytes), getInt16 / getUInt16 / setInt16 (2)
static inline void fusion_bytes_room(fusion_bytes b, int at, int size, const char* name, const char* where) {
    if (at < 0 || at > b.len - size)
        fusion_runtime_error(where, "%s(at %d) needs %d bytes there, but the bytes have length %d", name, at, size, b.len);
}
static inline int fusion_bytes_getInt(fusion_bytes b, int at, bool big, const char* where) {
    fusion_bytes_room(b, at, 4, "getInt", where);
    return (int)fusion_get_uint(b.data + at, 4, big);
}
static inline int fusion_bytes_getInt16(fusion_bytes b, int at, bool big, const char* where) {
    fusion_bytes_room(b, at, 2, "getInt16", where);
    return (int)(int16_t)fusion_get_uint(b.data + at, 2, big);
}
static inline int fusion_bytes_getUInt16(fusion_bytes b, int at, bool big, const char* where) {
    fusion_bytes_room(b, at, 2, "getUInt16", where);
    return (int)fusion_get_uint(b.data + at, 2, big);
}
static inline void fusion_bytes_setInt(fusion_bytes* b, int at, int v, bool big, const char* where) {
    fusion_bytes_room(*b, at, 4, "setInt", where);
    fusion_put_uint(b->data + at, (uint32_t)v, 4, big);
}
// Accepts -32768 to 65535: the value as either a signed or an unsigned 16-bit number
static inline void fusion_bytes_setInt16(fusion_bytes* b, int at, int v, bool big, const char* where) {
    fusion_bytes_room(*b, at, 2, "setInt16", where);
    if (v < -32768 || v > 65535) fusion_runtime_error(where, "setInt16: %d doesn't fit in 16 bits", v);
    fusion_put_uint(b->data + at, (uint32_t)v, 2, big);
}

// Back to text: the bytes must be valid text (UTF-8, or ASCII in an ascii project)
static inline bool fusion_bytes_isText(fusion_bytes b) { return fusion_utf8_valid(b.data, b.len); }
static inline fusion_string fusion_bytes_toString(fusion_bytes b, const char* where) {
    if (!fusion_utf8_valid(b.data, b.len)) fusion_runtime_error(where, "these %d bytes are not valid text (check with isText first)", b.len);
    return fusion_str_make(b.data, b.len);
}
// Hex: rawToHex(b) -> "6b6b69" (lowercase, nothing added); hexToRaw("6b6b69") -> bytes
static inline fusion_string fusion_bytes_rawToHex(fusion_bytes b, const char* where) { return fusion_str_bytesToHex(b, where); }
static inline fusion_bytes fusion_str_hexToRaw(fusion_string s, const char* where) {
    if (s.len % 2 != 0) fusion_runtime_error(where, "hexToRaw: '%.*s' has an odd number of hex digits", s.len, s.data);
    char* out = (char*)fusion_alloc((size_t)s.len / 2 + 1);
    for (int i = 0; i < s.len; i += 2) {
        int high = fusion_digit_value(s.data[i]), low = fusion_digit_value(s.data[i + 1]);
        if (high > 15 || low > 15) { fusion_dealloc(out); fusion_runtime_error(where, "hexToRaw: '%.*s' is not hex text", s.len, s.data); }
        out[i / 2] = (char)(high * 16 + low);
    }
    return fusion_bytes_take(out, s.len / 2);
}
'''
