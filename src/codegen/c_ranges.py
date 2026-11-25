"""C for ranges over decimals and money (Task 47.6, D.170): `for x in 0.5...2.5 step 0.5`.

The loop counts n = 0, 1, 2 ... and works each value out from its count - start + n * step - never by adding the
step again and again, so nothing drifts (0.1 + 0.1 + 0.1 is not 0.3 in a double). The last count is worked out
once, before the first turn:
- a double or float range: (end - start) / step, a hair of tolerance for the double's last digit
- a decimal or money range: exact - the three lined up at one scale, in an int256
- -1 when the range never starts (a step against the ends' way, from values - no turns, as `range` does)
A step of 0, or one finer than [ranges] rangeMaxStep allows, is a RangeError while running; written ones were
errors when compiling. Money's currencies must agree (the rule of + - D.183), else a CurrencyError.
"""

from ..semantic.ranges import written_number

RANGES_LIBRARY = r'''
// ---- ranges over decimals and money (47.6): each value start + n * step, never added up ----
static inline long long fusion_range_step_bad(const char* where, int places) {
    fusion_fail(FUSION_KIND_RangeError, where, "a range's step is finer than [ranges] rangeMaxStep allows (%d places)", places);
    return -1;
}
static inline long long fusion_range_count_double(double s, double e, double p, int places, double tol, const char* where) {
    if (p == 0) { fusion_fail(FUSION_KIND_RangeError, where, "a range's step can't be 0 - the loop would never end"); return -1; }
    double finest = 1; for (int k = 0; k < places; k++) finest /= 10;
    if ((p < 0 ? -p : p) < finest * (1 - tol)) return fusion_range_step_bad(where, places);
    double q = (e - s) / p;
    if (!(q >= -tol)) return -1;                          // never starts (or not a number)
    q += tol * (q > 1 ? q : 1);                           // the last digit: 0.3 / 0.1 is 2.9999999999999996
    if (q >= 9.0e18) { fusion_fail(FUSION_KIND_OverflowError, where, "the range has too many values to count"); return -1; }
    return (long long)q;
}
static inline fusion_int256 fusion_range_at(fusion_int128 v, int from, int to) { fusion_int256 r = v; for (int k = from; k < to; k++) r *= 10; return r; }
static inline long long fusion_range_count_decimal(fusion_decimal s, fusion_decimal e, fusion_decimal p, int places, const char* where) {
    if (p.value == 0) { fusion_fail(FUSION_KIND_RangeError, where, "a range's step can't be 0 - the loop would never end"); return -1; }
    int sc = s.scale; if (e.scale > sc) sc = e.scale; if (p.scale > sc) sc = p.scale;
    fusion_int256 S = fusion_range_at(s.value, s.scale, sc), E = fusion_range_at(e.value, e.scale, sc);
    fusion_int256 P = fusion_range_at(p.value, p.scale, sc);
    fusion_int256 finest = P < 0 ? -P : P; for (int k = 0; k < places; k++) finest *= 10;
    if (finest < fusion_pow10_256(sc)) return fusion_range_step_bad(where, places);
    fusion_int256 d = E - S;
    if ((d > 0 && P < 0) || (d < 0 && P > 0)) return -1;   // never starts
    fusion_int256 q = d / P;
    if (q > (fusion_int256)9000000000000000000LL) { fusion_fail(FUSION_KIND_OverflowError, where, "the range has too many values to count"); return -1; }
    return (long long)q;
}
static inline fusion_decimal fusion_range_decimal_value(fusion_decimal s, fusion_decimal p, long long n, const char* where) {
    int sc = s.scale > p.scale ? s.scale : p.scale;
    fusion_int256 v = fusion_range_at(s.value, s.scale, sc) + (fusion_int256)n * fusion_range_at(p.value, p.scale, sc);
    return fusion_decimal_narrow(v, sc, "a range's value", where);
}
static inline long long fusion_range_count_money(fusion_money s, fusion_money e, fusion_money p, int places, const char* where) {
    fusion_money joined;
    if (!fusion_money_join(&joined, s, e, "...", where) || !fusion_money_join(&joined, s, p, "step", where)) return -1;
    return fusion_range_count_decimal(fusion_decimal_make(s.value, s.scale), fusion_decimal_make(e.value, e.scale),
                                      fusion_decimal_make(p.value, p.scale), places, where);
}
static inline fusion_money fusion_range_money_value(fusion_money s, fusion_money p, long long n, const char* where) {
    fusion_money m = fusion_money_mul_whole(p, (fusion_int128)n, where);
    if (fusion_failed) return m;
    return fusion_money_add(s, m, where);
}
'''

# The C type the three parts are kept in, and the loop variable's
_PART_TYPE = {'float': 'double', 'double': 'double', 'decimal': 'fusion_decimal', 'money': 'fusion_money'}
_VALUE_TYPE = {'float': 'float', 'double': 'double', 'decimal': 'fusion_decimal', 'money': 'fusion_money'}


class RangesCodeMixin:
    """The loop of a range over decimals or money (47.6) - a mixin of the code generator."""

    def decimal_range_loop(self, node) -> str:
        call = node.iterable
        kind, places = call.range_kind, call.range_places
        part = _PART_TYPE[kind]
        start, end, step = (self._range_part(a, kind) for a in call.arguments[:3])
        if self.has_pending_temps():
            start, end, step = (self._settled_value(code, part) for code in (start, end, step))
        where = self._where(node)
        self.temp_count = getattr(self, 'temp_count', 0) + 1
        n = self.temp_count
        s, e, p, c, i = (f'fusion_r{x}_{n}' for x in 'sepci')
        if kind in ('float', 'double'):
            # a float keeps about 7 digits, a double about 16 - the tolerance for the last one
            tol = '1e-6' if kind == 'float' else '1e-9'
            count = f'fusion_range_count_double({s}, {e}, {p}, {places}, {tol}, {where})'
        else:
            count = f'fusion_range_count_{kind}({s}, {e}, {p}, {places}, {where})'
        count = self.checked_code(count, 'long long')
        if kind in ('float', 'double'):
            value = f'({_VALUE_TYPE[kind]})({s} + (double){i} * {p})'
        else:
            value = self.checked_code(f'fusion_range_{kind}_value({s}, {p}, {i}, {where})', part)
        self.emit('{')
        self.indent()
        self.emit(f'{part} {s} = {start};')
        self.emit(f'{part} {e} = {end};')
        self.emit(f'{part} {p} = {step};')
        self.emit(f'long long {c} = {count};')
        self.emit(f'for (long long {i} = 0; {i} <= {c}; {i}++) {{')
        self.indent()
        self.emit(f'{_VALUE_TYPE[kind]} {node.variable} = {value};')
        self.push_scope('loop')
        self.visit(node.body)
        self.pop_scope()
        self.dedent()
        self.emit('}')
        self.dedent()
        self.emit('}')
        return ''

    def _range_part(self, arg, kind) -> str:
        """A part of the range in C: a number written in a float or double range is its written digits as a
        double (0.1, not the float 0.1f - 0.10000000149); anything else as usual."""
        if kind in ('float', 'double'):
            number = written_number(arg)
            if number is not None:
                text = format(number, 'f')
                return f'({text})' if '.' in text else f'({text}.0)'
        return self.visit(arg)
