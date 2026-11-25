"""C for `money` (Task 47.2a, D.180-D.187): a sealed 16-byte value struct - never on the heap, copied like an int.

    value     8 bytes  the amount as a whole number: 12345
    scale     1 byte   how many places value holds: 2 -> 123.45 (0-18)
    currency  3 bytes  an ISO 4217 code, "ZAR"; three zero bytes = none
    symbol    4 bytes  UTF-8, padded with 0: "R", "$", "kr" - for display only (D.187)

The compiler does the plain arithmetic itself (D.186): + and - (the scales lined up, the larger kept), * by a whole
number or a decimal (exact), comparing - the currencies the same or one empty (the result takes the one set), else
a CurrencyError. Every step in between is done in an int128 (D.178) and narrowed back, checked. Rounding, dividing,
converting and formatting are the Currency module's (47.2b).
"""

MONEY_LIBRARY = r'''
// ---- money (47.2): value, scale, currency, symbol - 16 bytes ----
typedef struct { int64_t value; uint8_t scale; char currency[3]; char symbol[4]; } fusion_money;
_Static_assert(sizeof(fusion_money) == 16, "money is 16 bytes (D.184)");
static inline bool fusion_money_has_currency(fusion_money m) { return m.currency[0] != 0; }
static inline bool fusion_money_same_currency(fusion_money a, fusion_money b) {
    return a.currency[0] == b.currency[0] && a.currency[1] == b.currency[1] && a.currency[2] == b.currency[2];
}
// The currency of a + b: the same, or the one set when the other is empty - else a CurrencyError
static inline bool fusion_money_join(fusion_money* out, fusion_money a, fusion_money b, const char* op, const char* where) {
    if (fusion_money_has_currency(a) && fusion_money_has_currency(b) && !fusion_money_same_currency(a, b)) {
        fusion_fail(FUSION_KIND_CurrencyError, where, "%.3s %s %.3s: two different currencies - convert one first",
                    a.currency, op, b.currency);
        return false;
    }
    fusion_money from = fusion_money_has_currency(a) ? a : b;
    memcpy(out->currency, from.currency, 3);
    memcpy(out->symbol, a.symbol[0] ? a.symbol : b.symbol, 4);
    return true;
}
static inline fusion_money fusion_money_make_value(fusion_int128 v, int scale, const char* what, const char* where) {
    fusion_money m; memset(&m, 0, sizeof m);
    if (v > (fusion_int128)9223372036854775807LL || v < (fusion_int128)FUSION_LONG_MIN) {
        fusion_fail(FUSION_KIND_OverflowError, where, "%s doesn't fit in money (a long of its smallest steps)", what);
        return m;
    }
    m.value = (int64_t)v; m.scale = (uint8_t)scale;
    return m;
}
static inline fusion_money fusion_money_of(int64_t value, int scale) { fusion_money m; memset(&m, 0, sizeof m); m.value = value; m.scale = (uint8_t)scale; return m; }
static inline fusion_int128 fusion_money_at(fusion_money m, int scale) {
    fusion_int128 v = m.value; for (int k = m.scale; k < scale; k++) v *= 10; return v;
}
static inline fusion_money fusion_money_add(fusion_money a, fusion_money b, const char* where) {
    fusion_money r; memset(&r, 0, sizeof r);
    if (!fusion_money_join(&r, a, b, "+", where)) return r;
    int s = a.scale > b.scale ? a.scale : b.scale;
    fusion_money v = fusion_money_make_value(fusion_money_at(a, s) + fusion_money_at(b, s), s, "the sum", where);
    v.scale = (uint8_t)s; memcpy(v.currency, r.currency, 3); memcpy(v.symbol, r.symbol, 4);
    return v;
}
static inline fusion_money fusion_money_sub(fusion_money a, fusion_money b, const char* where) {
    fusion_money r; memset(&r, 0, sizeof r);
    if (!fusion_money_join(&r, a, b, "-", where)) return r;
    int s = a.scale > b.scale ? a.scale : b.scale;
    fusion_money v = fusion_money_make_value(fusion_money_at(a, s) - fusion_money_at(b, s), s, "the difference", where);
    v.scale = (uint8_t)s; memcpy(v.currency, r.currency, 3); memcpy(v.symbol, r.symbol, 4);
    return v;
}
static inline fusion_money fusion_money_neg(fusion_money a, const char* where) {
    if (a.value == FUSION_LONG_MIN) { fusion_fail(FUSION_KIND_OverflowError, where, "the negated amount doesn't fit in money"); return a; }
    a.value = -a.value; return a;
}
static inline fusion_money fusion_money_mul_whole(fusion_money a, fusion_int128 n, const char* where) {
    fusion_money v = fusion_money_make_value((fusion_int128)a.value * n, a.scale, "the product", where);
    memcpy(v.currency, a.currency, 3); memcpy(v.symbol, a.symbol, 4);
    return v;
}
// money * decimal: exact - the scales added (more than 18 places: round with the Currency module first)
static inline fusion_money fusion_money_mul_decimal(fusion_money a, fusion_decimal d, const char* where) {
    fusion_money v; memset(&v, 0, sizeof v);
    int s = a.scale + d.scale;
    if (s > 18) { fusion_fail(FUSION_KIND_OverflowError, where, "the product has %d places - money keeps up to 18; round one side first", s); return v; }
    fusion_int256 p = (fusion_int256)a.value * (fusion_int256)d.value;
    if (p > (fusion_int256)9223372036854775807LL || p < (fusion_int256)FUSION_LONG_MIN) {
        fusion_fail(FUSION_KIND_OverflowError, where, "the product doesn't fit in money (a long of its smallest steps)"); return v;
    }
    v.value = (int64_t)p; v.scale = (uint8_t)s; memcpy(v.currency, a.currency, 3); memcpy(v.symbol, a.symbol, 4);
    return v;
}
// Comparing: by amount; two different currencies can't be compared - a CurrencyError
static inline int fusion_money_cmp(fusion_money a, fusion_money b, const char* where) {
    if (fusion_money_has_currency(a) && fusion_money_has_currency(b) && !fusion_money_same_currency(a, b)) {
        fusion_fail(FUSION_KIND_CurrencyError, where, "%.3s compared with %.3s: two different currencies", a.currency, b.currency);
        return 0;
    }
    int s = a.scale > b.scale ? a.scale : b.scale;
    fusion_int128 x = fusion_money_at(a, s), y = fusion_money_at(b, s);
    return (x > y) - (x < y);
}
// == : the same amount and the same currency (none on either side counts as the same)
static inline bool fusion_money_eq(fusion_money a, fusion_money b) {
    if (fusion_money_has_currency(a) && fusion_money_has_currency(b) && !fusion_money_same_currency(a, b)) return false;
    int s = a.scale > b.scale ? a.scale : b.scale;
    return fusion_money_at(a, s) == fusion_money_at(b, s);
}
// Text: the symbol (display only - D.187), then the amount with its places: R100.05, -R3.50, 100.05
typedef struct { char bytes[40]; } fusion_money_buf;
static inline fusion_money_buf fusion_money_text(fusion_money m) {
    fusion_money_buf b; int i = 0;
    fusion_decimal_buf amount = fusion_decimal_text(fusion_decimal_make(m.value < 0 ? -(fusion_int128)m.value : m.value, m.scale));
    if (m.value < 0) b.bytes[i++] = '-';
    for (int k = 0; k < 4 && m.symbol[k]; k++) b.bytes[i++] = m.symbol[k];
    for (int k = 0; amount.bytes[k]; k++) b.bytes[i++] = amount.bytes[k];
    b.bytes[i] = '\0';
    return b;
}
static inline fusion_string fusion_money_to_str(fusion_money m) { fusion_money_buf b = fusion_money_text(m); int n = 0; while (b.bytes[n]) n++; return fusion_str_make(b.bytes, n); }
static inline fusion_decimal fusion_money_toDecimal(fusion_money m, const char* where) { (void)where; return fusion_decimal_make(m.value, m.scale); }
static inline fusion_money fusion_money_from_decimal(fusion_decimal d, const char* where) {
    return fusion_money_make_value(d.value, d.scale, "the amount", where);
}
// The currency and symbol, checked: a currency is 3 letters (or ""), a symbol up to 4 bytes (D.184)
static inline bool fusion_money_set_currency(fusion_money* m, fusion_string code, const char* where) {
    if (code.len != 0 && code.len != 3) {
        fusion_fail(FUSION_KIND_CurrencyError, where, "'%.*s' isn't a currency code - 3 letters (ISO 4217), or \"\" for none", code.len, code.data);
        return false;
    }
    memset(m->currency, 0, 3); if (code.len) memcpy(m->currency, code.data, 3);
    return true;
}
static inline bool fusion_money_set_symbol(fusion_money* m, fusion_string symbol, const char* where) {
    if (symbol.len > 4) {
        fusion_fail(FUSION_KIND_CurrencyError, where, "the symbol '%.*s' is %d bytes - money keeps up to 4 (D.184)", symbol.len, symbol.data, symbol.len);
        return false;
    }
    memset(m->symbol, 0, 4); if (symbol.len) memcpy(m->symbol, symbol.data, (size_t)symbol.len);
    return true;
}
static inline fusion_money fusion_money_make(fusion_decimal amount, fusion_string currency, fusion_string symbol, const char* where) {
    fusion_money m = fusion_money_from_decimal(amount, where);
    if (fusion_failed) return m;
    if (!fusion_money_set_currency(&m, currency, where)) return m;
    fusion_money_set_symbol(&m, symbol, where);
    return m;
}
static inline fusion_string fusion_money_currency(fusion_money m) { int n = fusion_money_has_currency(m) ? 3 : 0; return fusion_str_make(m.currency, n); }
static inline fusion_string fusion_money_symbol(fusion_money m) { int n = 0; while (n < 4 && m.symbol[n]) n++; return fusion_str_make(m.symbol, n); }
static inline bool fusion_money_set_scale(fusion_money* m, int scale, const char* where) {
    if (scale < 0 || scale > 18) { fusion_fail(FUSION_KIND_RangeError, where, "a scale of %d - money keeps 0 to 18 places", scale); return false; }
    m->scale = (uint8_t)scale; return true;
}
'''
