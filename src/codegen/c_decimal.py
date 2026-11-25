"""C for `decimal` (Task 47.8, D.182): an exact base-10 number - a whole number and its scale (how many places).

The value is an int128 (38 digits), the scale 0-18 (FUSION_DECIMAL_MAX_SCALE). Every step in between is done in an
int256 (D.178) and the result narrowed back, checked - an OverflowError, never a lost digit:
- + and -: the scales lined up, the larger kept - always exact
- *: the scales added - exact; past 18 places rounded once, by the mode
- /: exact when it ends within the larger scale or 18 places (2.50, 0.125); else 18 places, rounded once by the mode
- the modes (D.177): halfEven (the default), halfUp, down (toward zero), up (away from zero), exact (rounding
  needed is a RoundingError); the order is the built-in enum Rounding's
"""

DECIMAL_LIBRARY = r'''
// ---- decimal (47.8): an exact base-10 number - value / 10^scale ----
typedef struct { fusion_int128 value; int scale; } fusion_decimal;
#define FUSION_DECIMAL_MAX_SCALE 18
enum { FUSION_ROUND_HALF_EVEN, FUSION_ROUND_HALF_UP, FUSION_ROUND_DOWN, FUSION_ROUND_UP, FUSION_ROUND_EXACT };
static inline fusion_int256 fusion_pow10_256(int n) { fusion_int256 r = 1; while (n-- > 0) r *= 10; return r; }
static inline fusion_decimal fusion_decimal_make(fusion_int128 value, int scale) { fusion_decimal d = { value, scale }; return d; }
static inline fusion_decimal fusion_decimal_of_whole(fusion_int128 value) { return fusion_decimal_make(value, 0); }
// An int256 value at a scale, narrowed to a decimal - an OverflowError past 38 digits
static inline fusion_decimal fusion_decimal_narrow(fusion_int256 v, int scale, const char* what, const char* where) {
    if (v > (fusion_int256)FUSION_int128_MAX || v < (fusion_int256)FUSION_int128_MIN) {
        fusion_fail(FUSION_KIND_OverflowError, where, "%s doesn't fit in a decimal (38 digits)", what);
        return fusion_decimal_make(0, 0);
    }
    return fusion_decimal_make((fusion_int128)v, scale);
}
// q = n / d rounded by the mode (d != 0); *inexact set when a remainder was left
static inline fusion_int256 fusion_div_round_256(fusion_int256 n, fusion_int256 d, int mode, int* inexact) {
    fusion_int256 q = n / d, r = n % d;
    *inexact = r != 0;
    if (r == 0) return q;
    int negative = (n < 0) != (d < 0);
    fusion_int256 twice = (r < 0 ? -r : r) * 2, absd = d < 0 ? -d : d;
    int away = 0;
    switch (mode) {
        case FUSION_ROUND_UP: away = 1; break;
        case FUSION_ROUND_HALF_UP: away = twice >= absd; break;
        case FUSION_ROUND_HALF_EVEN: away = twice > absd || (twice == absd && (q % 2 != 0)); break;
        default: away = 0;
    }
    return away ? (negative ? q - 1 : q + 1) : q;
}
typedef struct { char bytes[56]; } fusion_decimal_buf;
static inline fusion_decimal_buf fusion_decimal_text(fusion_decimal d) {
    fusion_decimal_buf b; fusion_int128_buf digits = fusion_int128_text(d.value < 0 ? -d.value : d.value);
    int len = 0; while (digits.bytes[len]) len++;
    int i = 0;
    if (d.value < 0) b.bytes[i++] = '-';
    if (len <= d.scale) {                       // 0.05: zeros before the digits
        b.bytes[i++] = '0'; b.bytes[i++] = '.';
        for (int z = 0; z < d.scale - len; z++) b.bytes[i++] = '0';
        for (int k = 0; k < len; k++) b.bytes[i++] = digits.bytes[k];
    } else {
        for (int k = 0; k < len; k++) {
            if (d.scale > 0 && k == len - d.scale) b.bytes[i++] = '.';
            b.bytes[i++] = digits.bytes[k];
        }
    }
    b.bytes[i] = '\0';
    return b;
}
static inline fusion_string fusion_decimal_to_str(fusion_decimal d) { fusion_decimal_buf b = fusion_decimal_text(d); int n = 0; while (b.bytes[n]) n++; return fusion_str_make(b.bytes, n); }
static inline fusion_decimal fusion_decimal_add(fusion_decimal a, fusion_decimal b, const char* where) {
    int s = a.scale > b.scale ? a.scale : b.scale;
    fusion_int256 v = (fusion_int256)a.value * fusion_pow10_256(s - a.scale) + (fusion_int256)b.value * fusion_pow10_256(s - b.scale);
    return fusion_decimal_narrow(v, s, "the sum", where);
}
static inline fusion_decimal fusion_decimal_sub(fusion_decimal a, fusion_decimal b, const char* where) {
    b.value = -b.value;
    return fusion_decimal_add(a, b, where);
}
static inline fusion_decimal fusion_decimal_neg(fusion_decimal a, const char* where) {
    if (a.value == FUSION_int128_MIN) { fusion_fail(FUSION_KIND_OverflowError, where, "the negated value doesn't fit in a decimal"); return a; }
    a.value = -a.value; return a;
}
static inline int fusion_decimal_cmp(fusion_decimal a, fusion_decimal b) {
    int s = a.scale > b.scale ? a.scale : b.scale;
    fusion_int256 x = (fusion_int256)a.value * fusion_pow10_256(s - a.scale), y = (fusion_int256)b.value * fusion_pow10_256(s - b.scale);
    return (x > y) - (x < y);
}
// A value at scale `from`, rounded to scale `to` (to < from) - RoundingError when exact and a digit would be lost
static inline fusion_decimal fusion_decimal_rescale(fusion_int256 v, int from, int to, int mode, const char* where) {
    int inexact = 0;
    fusion_int256 q = from > to ? fusion_div_round_256(v, fusion_pow10_256(from - to), mode, &inexact) : v * fusion_pow10_256(to - from);
    if (inexact && mode == FUSION_ROUND_EXACT) {
        fusion_fail(FUSION_KIND_RoundingError, where, "the result needs rounding to %d places - the rounding is exact", to);
        return fusion_decimal_make(0, 0);
    }
    return fusion_decimal_narrow(q, to, "the result", where);
}
static inline fusion_decimal fusion_decimal_mul(fusion_decimal a, fusion_decimal b, int mode, const char* where) {
    fusion_int256 v = (fusion_int256)a.value * (fusion_int256)b.value;
    int s = a.scale + b.scale;
    if (s > FUSION_DECIMAL_MAX_SCALE) return fusion_decimal_rescale(v, s, FUSION_DECIMAL_MAX_SCALE, mode, where);
    return fusion_decimal_narrow(v, s, "the product", where);
}
static inline fusion_decimal fusion_decimal_divide(fusion_decimal a, fusion_decimal b, int places, int mode, const char* where) {
    if (b.value == 0) { fusion_fail(FUSION_KIND_DivideByZeroError, where, "%s / 0: division by zero", fusion_decimal_text(a).bytes); return a; }
    // a / b at `places`: a.value * 10^(places + b.scale - a.scale) / b.value
    int shift = places + b.scale - a.scale, inexact = 0;
    fusion_int256 n = (fusion_int256)a.value, d = (fusion_int256)b.value;
    if (shift >= 0) n *= fusion_pow10_256(shift); else d *= fusion_pow10_256(-shift);
    fusion_int256 q = fusion_div_round_256(n, d, mode, &inexact);
    if (inexact && mode == FUSION_ROUND_EXACT) {
        fusion_fail(FUSION_KIND_RoundingError, where, "%s / %s needs rounding to %d places - the rounding is exact",
                    fusion_decimal_text(a).bytes, fusion_decimal_text(b).bytes, places);
        return fusion_decimal_make(0, 0);
    }
    return fusion_decimal_narrow(q, places, "the quotient", where);
}
// a / b: exact when it ends within the larger scale or 18 places - its scale the fewest places needed (at least the
// larger of the two); else 18 places, rounded once by the mode
static inline fusion_decimal fusion_decimal_div(fusion_decimal a, fusion_decimal b, int mode, const char* where) {
    if (b.value == 0) { fusion_fail(FUSION_KIND_DivideByZeroError, where, "%s / 0: division by zero", fusion_decimal_text(a).bytes); return a; }
    int least = a.scale > b.scale ? a.scale : b.scale;
    for (int places = least; places <= FUSION_DECIMAL_MAX_SCALE; places++) {
        int shift = places + b.scale - a.scale;
        fusion_int256 n = (fusion_int256)a.value, d = (fusion_int256)b.value;
        if (shift >= 0) n *= fusion_pow10_256(shift); else d *= fusion_pow10_256(-shift);
        if (n % d == 0) return fusion_decimal_narrow(n / d, places, "the quotient", where);
    }
    return fusion_decimal_divide(a, b, FUSION_DECIMAL_MAX_SCALE, mode, where);
}
static inline fusion_decimal fusion_decimal_round(fusion_decimal a, int places, int mode, const char* where) {
    if (places < 0 || places > FUSION_DECIMAL_MAX_SCALE) {
        fusion_fail(FUSION_KIND_RangeError, where, "round to %d places - from 0 to 18", places);
        return a;
    }
    return fusion_decimal_rescale((fusion_int256)a.value, a.scale, places, mode, where);
}
// Text to a decimal: digits, at most one point, a sign - "-12.50" keeps its two places; NumberFormatError otherwise
static inline fusion_decimal fusion_str_toDecimal(fusion_string s, const char* where) {
    int i = 0, negative = 0, scale = -1, digits = 0;
    fusion_int256 v = 0;
    if (i < s.len && (s.data[i] == '+' || s.data[i] == '-')) negative = s.data[i++] == '-';
    for (; i < s.len; i++) {
        char c = s.data[i];
        if (c == '.' && scale < 0) { scale = 0; continue; }
        if (c < '0' || c > '9' || digits >= 38) { digits = -1; break; }
        v = v * 10 + (c - '0'); digits++;
        if (scale >= 0) scale++;
    }
    if (digits <= 0 || scale > FUSION_DECIMAL_MAX_SCALE || scale == 0) {
        fusion_fail(FUSION_KIND_NumberFormatError, where, "'%.*s' is not a decimal number (up to 38 digits, 18 after the point)", s.len, s.data);
        return fusion_decimal_make(0, 0);
    }
    return fusion_decimal_make((fusion_int128)(negative ? -v : v), scale < 0 ? 0 : scale);
}
static inline fusion_decimal fusion_int_toDecimal(int n, const char* where) { (void)where; return fusion_decimal_of_whole(n); }
static inline fusion_decimal fusion_long_toDecimal(long long n, const char* where) { (void)where; return fusion_decimal_of_whole(n); }
static inline fusion_decimal fusion_int128_toDecimal(fusion_int128 n, const char* where) { (void)where; return fusion_decimal_of_whole(n); }
static inline fusion_decimal fusion_decimal_toDecimal(fusion_decimal d, const char* where) { (void)where; return d; }
// A decimal as a double - may lose places (said so in its name's documentation, never silently chosen)
static inline double fusion_decimal_toDouble(fusion_decimal d) {
    double v = (double)d.value;
    for (int k = 0; k < d.scale; k++) v /= 10.0;
    return v;
}
'''
