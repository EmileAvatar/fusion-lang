"""C for the wide whole numbers int128 and int256 (Task 47.7, D.179).

int128 is GCC's `__int128` (two registers - as fast as a long for + and -), int256 is C23's `_BitInt(256)`.
Each gets what a long has (c_errors.py): + - * / % and minus checked - an OverflowError, never a changed value -,
wrapping on purpose, text (printf has no format for them: a small buffer returned by value, nothing allocated),
reading from text, and checked narrowing. Written once per width from one template.
"""

WIDE_TYPES = ('int128', 'int256')

# The widest whole number of each operand kind, in order - arithmetic is done in the widest one there
WHOLE_ORDER = ('int', 'long', 'int128', 'int256')

_TEMPLATE = r'''
// ---- NAME (47.7): BITS bits, signed ----
typedef CTYPE fusion_NAME;
typedef unsigned CTYPE fusion_uNAME;
#define FUSION_NAME_MAX ((fusion_NAME)(((fusion_uNAME)1 << (BITS - 1)) - 1))
#define FUSION_NAME_MIN (-FUSION_NAME_MAX - 1)
typedef struct { char bytes[DIGITS]; } fusion_NAME_buf;
static inline fusion_NAME_buf fusion_NAME_text(fusion_NAME v) {
    fusion_NAME_buf b; char tmp[DIGITS]; int n = 0;
    fusion_uNAME u = v < 0 ? (fusion_uNAME)0 - (fusion_uNAME)v : (fusion_uNAME)v;
    do { tmp[n++] = (char)('0' + (int)(u % 10)); u /= 10; } while (u);
    int i = 0;
    if (v < 0) b.bytes[i++] = '-';
    while (n) b.bytes[i++] = tmp[--n];
    b.bytes[i] = '\0';
    return b;
}
static inline fusion_string fusion_NAME_to_str(fusion_NAME v) { fusion_NAME_buf b = fusion_NAME_text(v); int n = 0; while (b.bytes[n]) n++; return fusion_str_make(b.bytes, n); }
static inline fusion_NAME fusion_add_NAME(fusion_NAME a, fusion_NAME b, const char* where) {
    fusion_NAME r;
    if (__builtin_add_overflow(a, b, &r)) { fusion_fail(FUSION_KIND_OverflowError, where, "%s + %s doesn't fit in an NAME", fusion_NAME_text(a).bytes, fusion_NAME_text(b).bytes); return 0; }
    return r;
}
static inline fusion_NAME fusion_sub_NAME(fusion_NAME a, fusion_NAME b, const char* where) {
    fusion_NAME r;
    if (__builtin_sub_overflow(a, b, &r)) { fusion_fail(FUSION_KIND_OverflowError, where, "%s - %s doesn't fit in an NAME", fusion_NAME_text(a).bytes, fusion_NAME_text(b).bytes); return 0; }
    return r;
}
static inline fusion_NAME fusion_mul_NAME(fusion_NAME a, fusion_NAME b, const char* where) {
    fusion_NAME r;
    if (__builtin_mul_overflow(a, b, &r)) { fusion_fail(FUSION_KIND_OverflowError, where, "%s * %s doesn't fit in an NAME", fusion_NAME_text(a).bytes, fusion_NAME_text(b).bytes); return 0; }
    return r;
}
static inline fusion_NAME fusion_neg_NAME(fusion_NAME a, const char* where) {
    if (a == FUSION_NAME_MIN) { fusion_fail(FUSION_KIND_OverflowError, where, "-(%s) doesn't fit in an NAME", fusion_NAME_text(a).bytes); return 0; }
    return -a;
}
static inline fusion_NAME fusion_div_NAME(fusion_NAME a, fusion_NAME b, int check, const char* where) {
    if (b == 0) { fusion_fail(FUSION_KIND_DivideByZeroError, where, "%s / 0: division by zero", fusion_NAME_text(a).bytes); return 0; }
    if (b == -1) {
        if (check && a == FUSION_NAME_MIN) { fusion_fail(FUSION_KIND_OverflowError, where, "%s / -1 doesn't fit in an NAME", fusion_NAME_text(a).bytes); return 0; }
        return (fusion_NAME)((fusion_uNAME)0 - (fusion_uNAME)a);
    }
    return a / b;
}
static inline fusion_NAME fusion_mod_NAME(fusion_NAME a, fusion_NAME b, int check, const char* where) {
    (void)check;
    if (b == 0) { fusion_fail(FUSION_KIND_DivideByZeroError, where, "%s %% 0: division by zero", fusion_NAME_text(a).bytes); return 0; }
    if (b == -1) return 0;
    return a % b;
}
static inline fusion_NAME fusion_wrap_add_NAME(fusion_NAME a, fusion_NAME b) { return (fusion_NAME)((fusion_uNAME)a + (fusion_uNAME)b); }
static inline fusion_NAME fusion_wrap_sub_NAME(fusion_NAME a, fusion_NAME b) { return (fusion_NAME)((fusion_uNAME)a - (fusion_uNAME)b); }
static inline fusion_NAME fusion_wrap_mul_NAME(fusion_NAME a, fusion_NAME b) { return (fusion_NAME)((fusion_uNAME)a * (fusion_uNAME)b); }
// Text to an NAME: the whole text a number that fits, or a NumberFormatError
static inline bool fusion_parse_NAME(fusion_string s, fusion_NAME* out) {
    int i = 0; fusion_uNAME value = 0; int negative = 0;
    const fusion_uNAME limit = (fusion_uNAME)FUSION_NAME_MAX + 1;
    if (i < s.len && (s.data[i] == '+' || s.data[i] == '-')) negative = s.data[i++] == '-';
    if (i >= s.len) return false;
    for (; i < s.len; i++) {
        if (s.data[i] < '0' || s.data[i] > '9') return false;
        if (value > limit / 10) return false;
        value = value * 10 + (fusion_uNAME)(s.data[i] - '0');
        if (value > limit) return false;
    }
    if (!negative && value == limit) return false;
    *out = negative ? (fusion_NAME)((fusion_uNAME)0 - value) : (fusion_NAME)value;
    return true;
}
static inline fusion_NAME fusion_str_toNAMECAP(fusion_string s, const char* where) {
    fusion_NAME v;
    if (!fusion_parse_NAME(s, &v)) { fusion_fail(FUSION_KIND_NumberFormatError, where, "'%.*s' is not a whole number that fits in an NAME", s.len, s.data); return 0; }
    return v;
}
static inline fusion_NAME fusion_int_toNAMECAP(int n, const char* where) { (void)where; return n; }
static inline fusion_NAME fusion_long_toNAMECAP(long long n, const char* where) { (void)where; return n; }
// Narrowing, always written and checked (D.003): toInt(x), toLong(x) - an OverflowError when it doesn't fit
static inline int fusion_NAME_toInt(fusion_NAME n, const char* where) {
    if (n < -2147483647LL - 1 || n > 2147483647LL) { fusion_fail(FUSION_KIND_OverflowError, where, "%s doesn't fit in an int (-2147483648 to 2147483647)", fusion_NAME_text(n).bytes); return 0; }
    return (int)n;
}
static inline long long fusion_NAME_toLong(fusion_NAME n, const char* where) {
    if (n < FUSION_LONG_MIN || n > 9223372036854775807LL) { fusion_fail(FUSION_KIND_OverflowError, where, "%s doesn't fit in a long", fusion_NAME_text(n).bytes); return 0; }
    return (long long)n;
}
static inline short fusion_NAME_toShort(fusion_NAME n, const char* where) {
    if (n < -32768 || n > 32767) { fusion_fail(FUSION_KIND_OverflowError, where, "%s doesn't fit in a short (-32768 to 32767)", fusion_NAME_text(n).bytes); return 0; }
    return (short)n;
}
'''

_WIDTHS = {'int128': ('__int128', 128, 48), 'int256': ('_BitInt(256)', 256, 88)}


def _one(name: str) -> str:
    ctype, bits, digits = _WIDTHS[name]
    cap = 'Int' + name[3:]
    return (_TEMPLATE.replace('fusion_uNAME', f'fusion_u{name}').replace('NAMECAP', cap)
            .replace('NAME', name).replace('CTYPE', ctype).replace('BITS', str(bits)).replace('DIGITS', str(digits)))


WIDE_LIBRARY = _one('int128') + _one('int256') + r'''
static inline fusion_int128 fusion_int128_toInt128(fusion_int128 n, const char* where) { (void)where; return n; }
static inline fusion_int256 fusion_int256_toInt256(fusion_int256 n, const char* where) { (void)where; return n; }
static inline fusion_int256 fusion_int128_toInt256(fusion_int128 n, const char* where) { (void)where; return n; }
static inline fusion_int128 fusion_int256_toInt128(fusion_int256 n, const char* where) {
    if (n < FUSION_int128_MIN || n > FUSION_int128_MAX) { fusion_fail(FUSION_KIND_OverflowError, where, "%s doesn't fit in an int128", fusion_int256_text(n).bytes); return 0; }
    return (fusion_int128)n;
}
'''


def widest_whole(names) -> str:
    """The kind whole-number arithmetic is done in: 'int' (byte, short, int), 'long', 'int128' or 'int256';
    None when an operand isn't a whole number."""
    kinds = []
    for name in names:
        if name in ('byte', 'short', 'int'):
            kinds.append('int')
        elif name in WHOLE_ORDER:
            kinds.append(name)
        else:
            return None
    return max(kinds, key=WHOLE_ORDER.index) if kinds else None
