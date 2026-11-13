[< 032 DomainPackages](032-DomainPackages.md) | [Index](index.md) <!-- nav -->

# 033 Currency

**Status:** planned - the Currency module is FEATURES 43.3, the `money` type 47.2; never fetches rates (CLAUDE.md hard rule)

Contents: [Currency Module (Financial / FX Conversion)](#currency-module-financial--fx-conversion) | [Fixed-Point Decimal Type & `Currency` Sugar (Financial / Money Precision)](#fixed-point-decimal-type--currency-sugar-financial--money-precision)

## Currency Module (Financial / FX Conversion)

**Status:** Proposed - much later in the project, well after the `decimal`/`Currency`
*type* itself exists and is implemented (see "Fixed-Point Decimal Type & `Currency` Sugar"
under "Type System Enhancements" above). This entry is a planning overview only, not a
scoped design.
**Module:** `Fusion.Currency` (or `fusionlib.Currency`)
**Purpose:** Handle real-world financial/currency operations on top of the `decimal`/
`Currency` language type - most importantly currency conversion - so applications don't
hand-roll exchange-rate math on raw `decimal` values.
**Depends On:** The `decimal`/`Currency` type proposal - this module is a standard-library
layer built on top of that language feature, not a replacement for it. The type gives exact
arithmetic at whatever precision/scale a program declares (`Currency(11, 2)`,
`Currency(21, 2)`, etc.); this module gives the real-world domain logic that sits on top.

**Features (overview only - not scoped yet):**

* Currency conversion between ISO 4217 currency codes (e.g. USD -> EUR) using exchange rates
* Exchange rates supplied by the developer - **never fetched from an external API** by the
  module (a hard rule, Decisions.md D.022)
* Currency-aware formatting (symbols, locale-specific separators - e.g. `$19.99` vs
  `19,99 €`)
* Per-currency-code default scale lookup (USD = 2 decimal places, JPY = 0, BHD = 3, etc.) -
  automatically picking the right `Currency(p, s)` shape from a currency *code*, rather than
  a programmer choosing precision/scale by hand every time
* Rounding/allocation helpers for splitting amounts without losing cents (e.g. dividing a
  bill evenly across N people) - a classic financial-code pitfall worth solving once in a
  library instead of in every application

**Reason:** Currency conversion, formatting, and locale/rounding rules are real-world domain
logic - they change (exchange rates fluctuate, locales differ, currencies have different
minor units) and don't belong baked into the `decimal`/`Currency` language type itself, the
same way `fusionlib.Regex` keeps a full regex engine out of Core. The type's job is exact,
predictable arithmetic; this module's job is everything a real financial application needs
on top of that.


---


### Fixed-Point Decimal Type & `Currency` Sugar (Financial / Money Precision)

> **Decided since (2026-10-29, Decisions.md D.021):** `money` is a long of minor units
> (Task 47.2); an exact `decimal(p, s)` stays a later option (47.2.3).

**Status:** 📝 Proposed
**Priority:** Medium-High (needed before Fusion can be credibly used for financial/trading
software)
**Purpose:** Add an exact, fixed-point decimal numeric type - similar to COBOL's
`PACKED-DECIMAL`/`COMP-3` and Java's `BigDecimal` - for money and financial calculations
where `float`/`double`'s binary floating-point rounding error is unacceptable. Also adds
`Currency` as an optional, convenient sugar type on top of it, so programmers can choose
between spelling out exact precision/scale themselves (`decimal(p, s)`) or reaching for a
ready-made money type that already does the right thing (`Currency`).

---

#### Why `float`/`double` Aren't Enough

- Fusion's current numeric types (`int`, `float`, `double`, `byte`, `short`, `long`) cover integers and IEEE-754 binary floating point.
- Binary floating point cannot represent most decimal fractions exactly:

```fusion
double price = 0.1 + 0.2
print(price)  // Prints 0.30000000000000004, not 0.3 - a classic float bug

double total = 19.99 * 3
print(total)  // May print 59.96999999999999 instead of exactly 59.97
```

- This is not a Fusion-specific bug - every IEEE-754 float has it (C, Java, Python, JavaScript included).
- It's why COBOL is still running the world's banks decades later (`PACKED-DECIMAL` never had this problem), and why every language with real financial use cases eventually grows a dedicated decimal type (Java's `BigDecimal`, C#'s `decimal`, Python's `decimal.Decimal`, Rust's `rust_decimal`).

#### Where This Fits in Fusion's Numeric Model

Reference diagram (provided by the user) for how this new type relates to Fusion's
existing numeric types:

```
                Numeric representation
                         │
          ┌──────────────┴──────────────┐
          │                             │
       Exact                          Approximate
          │                             │
   ┌──────┴──────┐                  Floating point
   │             │                  (float, double -
 Integer       Decimal               already in Fusion)
   │             │
   │       ┌─────┴─────┐
   │       │           │
 cents   fixed       arbitrary
(int/    scale       precision
 long -  (new:       (future extension
 already `decimal`,  of the same family -
 in      this        not built from
 Fusion) proposal)   scratch separately)
```

- Fusion already covers the "Integer" and "Approximate/Floating point" branches.
- This proposal adds the "Decimal" branch, starting with fixed scale (the money/trading use case actually requested) and leaving arbitrary precision as a related future extension of the same type family rather than a separate type designed from scratch later.

#### Proposed Syntax

Following Fusion's existing size-declaration pattern for arrays (`type[N]`, see "Advanced
Array Declaration Syntax" above) and the primitive/class type-casing convention (see
"Clarification: Type Casing" above), fixed-point decimal is proposed as a primitive value
type parameterized by precision and scale:

```fusion
// decimal(precision, scale) - total significant digits, digits after the decimal point
decimal(10, 2) price = 19.99         // up to 10 digits total, exactly 2 after the point
decimal(18, 4) exchangeRate = 1.2345 // 18 digits total, 4 after the point - common FX precision
                                      // (18, not 19 - see "Capacity" below for why that limit is real)

// Shorthand: decimal with no (precision, scale) uses a project-configurable default
// (e.g. via fusion.toml - see Task 12.12's project configuration system)
decimal total = 0.00
```

#### Arithmetic Semantics (needs an explicit decision, same pattern as Task 12.7's memory model)

- **Exact by construction:** represented internally as a scaled integer (an unscaled
  integer value + a scale), like a database `DECIMAL(p,s)` column or COBOL `COMP-3` -
  never binary floating point - so `0.1 + 0.2` is exactly `0.3`, always.
- **Rounding mode:** needs a decided default (banker's rounding / round-half-to-even,
  matching IEEE 754 and most database engines, vs. round-half-away-from-zero, the
  traditional COBOL/financial convention) - a real design decision to make before
  implementation, not an implementation detail to guess at. Candidate: default to
  round-half-even, with the option to override per-project via `fusion.toml` (ties into
  Task 12.12), since different financial jurisdictions/institutions mandate different
  rounding rules.
- **Overflow/precision loss:** an operation whose exact result doesn't fit the declared
  scale must either round predictably per the decided rounding mode, or be a compile/
  runtime error - mirrors COBOL's `ON SIZE ERROR` clause.
- **Division:** decimal division can produce a non-terminating result (e.g. `1m / 3`) -
  must always round to the target's declared scale, never silently fall back to float.
- **No implicit float conversion:** converting between `decimal` and `float`/`double`
  should require an explicit cast (a `float` can't exactly represent most `decimal`
  values either), matching the general principle that lossy conversions stay visible in
  the code rather than happening silently.

#### Capacity: What Actually Fits (a real implementation constraint, not just a syntax choice)

**Direct question this came up from: does the default hold a trillion or a quintillion?
No.** `Currency` / `decimal(11, 2)` (matching COBOL `PIC 9(9)V99`) tops out at
**999,999,999.99** - just under one billion. `PIC 9(9)V99` was sized for typical
mid-20th-century business/accounting amounts, not modern trillion-dollar balance sheets or
quintillion-scale figures - if a project needs more range, it declares more precision (see
table below), or raises `currency_precision` in `fusion.toml` for `Currency` specifically.

`decimal(p, s)`'s syntax accepts any `(p, s)` a programmer writes - but the runtime backing
proposed in the Codegen open question below (a plain `int64_t unscaled` value) has a real,
hard ceiling: a signed 64-bit integer maxes out at **9,223,372,036,854,775,807 (~9.22 x
10^18)**, which safely backs roughly **18 total digits**, not 19 or more.

| To represent up to... | Integer digits needed | Example declaration | Fits in `int64_t`? |
|---|---|---|---|
| ~1 billion (COBOL/`Currency` default) | 9 | `decimal(11, 2)` | Yes, comfortably |
| ~10 trillion | 13 | `decimal(15, 2)` | Yes, comfortably |
| ~10 quintillion | 19 | `decimal(21, 2)` | **No** - unscaled value (~10^21) overflows `int64_t` (~9.22 x 10^18) |

This isn't hypothetical: this proposal's own earlier FX-rate example, originally written as
`decimal(19, 4)`, sat right at (and could exceed) that same `int64_t` ceiling - corrected
above to `decimal(18, 4)` while writing this section, rather than shipping a money/precision
type with a hidden overflow bug in its own documented example.

**Two ways to actually fix this (needs its own decision - flagged here, not silently
picked):**
1. **Cap declared precision** to what `int64_t` safely backs (`p <= 18`) for v1, and reject
   anything larger at compile time with a clear error - simplest, but caps Fusion's decimal
   type below what a trillion/quintillion-scale application would need
2. **Widen the runtime backing** for larger declared precisions - e.g. GCC's 128-bit
   `__int128` (safely backs ~38 digits - comfortably past quintillions) or a true
   arbitrary-precision bignum for unbounded `p` - more implementation work, but this is
   really the same "arbitrary precision" leaf the reference diagram already calls out as a
   future extension, just needed sooner than expected because `int64_t` alone can't cover
   the full range `decimal(p, s)`'s own grammar promises

**Recommendation:** don't let `decimal(p, s)`'s grammar accept a `p` the chosen runtime
representation can't actually back. Either enforce a hard, loudly-documented compile-time
ceiling matching whatever integer width backs v1 ("decimal supports up to 18 total digits
in v1, use arbitrary-precision decimal for more once that exists"), or commit to `__int128`
as the v1 backing - it's supported by GCC (the compiler Fusion already targets) at no extra
dependency cost, and comfortably covers trillions and quintillions alike.

#### Example Use Case

```fusion
decimal(10, 2) function calculateTotal(decimal(10, 2) price, int quantity)
    return price * quantity

void function main()
    decimal(10, 2) itemPrice = 19.99
    decimal(10, 2) total = calculateTotal(itemPrice, 3)
    print("Total: {total}")  // Total: 59.97 - exact, not 59.96999999999999
```

#### `Currency` - Convenience Sugar for `decimal(precision, scale)`

**Purpose:** give programmers a choice, not a mandate. `Currency` is a money-flavored,
friendlier spelling of `decimal` with a sensible zero-config default - it is **not**
limited to one fixed shape. Just like `decimal(p, s)`, `Currency(p, s)` takes its own
explicit precision and scale, so the same keyword scales from a small shop's till to a
multi-trillion-dollar company's ledger without switching types:

```fusion
Currency price = 19.99                        // no (p, s) given - uses the project's
                                               // configured default shape (11, 2 unless
                                               // fusion.toml overrides it)

Currency(11, 2) shopTotal = 49.99             // small business - explicit, same as the default
Currency(21, 2) corporateBalance = 1000000000000.00  // multi-trillion-dollar scale - explicit

// Currency(p, s) is exactly decimal(p, s) - genuinely the same type, not merely
// convertible to it, so no cast is needed either direction
decimal(21, 2) sameAsCorporateBalance = corporateBalance  // OK
```

`Currency` (with or without explicit `(p, s)`) is proposed as a reserved keyword that is
**pure syntactic sugar**: `Currency(p, s)` desugars directly to `decimal(p, s)` during
parsing/semantic analysis, and bare `Currency` desugars to whatever `(p, s)` the project
has configured as its default. It is not a separate runtime type, needs no separate codegen
path, and adds no arithmetic rules beyond what `decimal` already defines above - keeping it
cheap to implement once `decimal` exists, not a second feature to build from scratch.

**Default mapping when no `(p, s)` is given - matches COBOL exactly:** bare `Currency`
defaults to `decimal(11, 2)`, chosen to line up bit-for-bit with COBOL's classic money
field:

| COBOL | Meaning | Fusion equivalent |
|-------|---------|--------------------|
| `PIC 9(9)V99` | 9 integer digits + 2 decimal digits (`V` = implied decimal point) = 11 total significant digits, scale 2 | `decimal(11, 2)` == bare `Currency` |

- This isn't an arbitrary default - `PIC 9(9)V99` is the de facto standard COBOL money field still running banking/insurance/trading systems today (comfortably covers amounts up to 999,999,999.99, per the "Capacity" section above).
- Giving bare `Currency` this exact shape means porting COBOL financial logic to Fusion, or interoperating with COBOL systems via `fusionlib.Lang` (see "Cross-Language Compilation Support" above), has a direct, unsurprising equivalent instead of an approximation - while `Currency(p, s)` with an explicit precision/scale covers everything from small-shop totals to a multi-trillion- dollar company's balances (subject to the same `int64_t`-vs-`__int128` backing decision the "Capacity" section above already flags for `decimal` generally).

**The zero-config default itself is configurable, not hardcoded:** real-world currencies
don't all share one shape - most use 2 minor-unit digits, but JPY uses 0 and a few (e.g.
the Bahraini Dinar) use 3. So bare `Currency`'s default shape is proposed as
project-configurable via `fusion.toml` (ties into Task 12.12), so a codebase that mostly
declares bare `Currency` isn't stuck with COBOL's shape if that's the wrong fit for it:

```toml
# fusion.toml
[types]
currency_precision = 11   # default: 11 (matches COBOL PIC 9(9)V99) - used when Currency
                          # is declared with no explicit (p, s)
currency_scale = 2        # default: 2  (matches COBOL PIC 9(9)V99) - same
```

- A project working primarily in JPY, for example, could set `currency_scale = 0` project-wide, and every *bare* `Currency` declaration in that codebase follows without touching a single call site - the same "configure once, apply everywhere" philosophy `fusion.toml` already uses for `[indentation]`/`[safety]`/`[backend]` today.
- A declaration that writes its own `Currency(p, s)` explicitly always wins over the project default, exactly like writing `decimal(p, s)` explicitly does.

**Explicitly out of scope for `Currency` itself (v1):** currency-symbol-aware formatting
(`$19.99` vs `19,99 €`), preventing `Currency usd + Currency eur` from silently compiling
(multi-currency arithmetic safety), FX conversion between currencies, and automatically
picking the right scale from an ISO 4217 currency *code* (knowing `JPY` means 0 decimal
places without being told) - `Currency` here is only sugar for precision/scale, chosen
either explicitly per declaration or via the project default. These are real, valuable
follow-on needs - see the new **Currency Module** proposal near the end of this document,
which is exactly where they're expected to eventually live, on top of this type rather than
inside it.

#### Comparison with Other Languages

| Language | Type | Representation |
|----------|------|-----------------|
| COBOL | `PIC 9(n)V9(m) COMP-3` | Packed (binary-coded) decimal, fixed scale |
| COBOL | `PIC 9(9)V99 COMP-3` | The specific money field `Currency` mirrors |
| Java | `java.math.BigDecimal` | Arbitrary-precision, unscaled value + scale |
| C# | `decimal` | 128-bit fixed-point, 28-29 significant digits |
| Python | `decimal.Decimal` | Arbitrary-precision, configurable context |
| SQL | `DECIMAL(p, s)` / `NUMERIC(p, s)` | Fixed precision and scale |
| **Fusion (proposed)** | `decimal(p, s)` | Fixed-point, scaled integer internally |
| **Fusion (proposed)** | `Currency` / `Currency(p, s)` | Sugar for `decimal(p, s)`; bare `Currency` defaults to `decimal(11, 2)`, project-configurable |

#### Open Questions

1. **Default precision/scale when omitted** (`decimal total = 0`, no `(p, s)`) - a fixed
   language default (e.g. `(18, 2)`), or read from `fusion.toml` project configuration
   (ties into Task 12.12)?
2. **Rounding mode** - one fixed default for the whole language, or configurable
   per-project like the above?
3. **Arbitrary-precision decimal** (the diagram's other `Decimal` leaf, a
   `BigDecimal`-equivalent) - a separate future type, or should `decimal` support an
   "unbounded" scale mode instead of a second type?
4. **Codegen strategy** - C has no native fixed-point/packed-decimal type; needs a runtime
   struct (`{ <int type> unscaled; int scale; }`) plus a small runtime library for
   arithmetic - real runtime support to design, not just a keyword (same shape of gap Task
   15.5 already flags for `Unique`/`Shared`/`Weak`). The integer width for `unscaled`
   is itself a decision, not a given - see "Capacity: What Actually Fits" above: plain
   `int64_t` only safely backs ~18 total digits, so this question and that section's two
   options (cap precision at 18, or use `__int128`) should be decided together
5. **Naming** - `decimal` (matches C#, most familiar to mainstream developers) vs. `Money`
   (domain-specific, but too narrow - this type is also useful for scientific/trading
   precision generally, not only currency) vs. `Fixed`/`FixedPoint` (most literally
   accurate to the representation)
6. **Bare `Currency`'s default shape** (when no explicit `(p, s)` is written) - keep
   `decimal(11, 2)` (matches COBOL `PIC 9(9)V99` exactly) as the language-level default, or
   pick a different one and let `fusion.toml` be the only way most projects ever see a
   different value? (Explicit `Currency(p, s)` is unaffected either way - always honored
   as written, same as `decimal(p, s)`.)
7. **`Currency` type-casing** - capitalized like a class (`String`, per "Clarification:
   Type Casing" above) even though it behaves like a primitive value type (no heap
   allocation beyond what `decimal` itself needs)? Capitalization here would signal "this
   is sugar/opinionated," not "this is a reference type" - a departure from the existing
   convention worth deciding deliberately, not by accident
8. **Should `Currency` become type-incompatible with plain `decimal(p, s)` of a different
   shape** (e.g. can a `Currency` be passed where `decimal(19, 4)` is expected)? Proposed
   answer above is "no special-casing, `Currency` literally is a specific `decimal(p, s)`
   and follows the same compatibility rules as any other `decimal(p, s)` pair" - flagged
   here so that answer gets confirmed, not silently assumed

**Recommendation:** `decimal` as the name (widest recognition), fixed-point scaled-integer
representation for v1, with arbitrary precision explicitly deferred as a distinct future
leaf of the same family - matches the reference diagram exactly, and avoids building the
harder unbounded-precision case before the money/trading case actually requested is proven
out. `Currency` ships alongside it from day one (not a later add-on) since it's pure sugar
over `decimal` and costs almost nothing extra once `decimal` itself is built.

#### Implementation Checklist (once scoped and approved)

- [ ] Get explicit decisions on the Open Questions above (including the `Currency`-specific
      ones) before any implementation begins (same "decide first" pattern as Task
      12.7/12.10/12.11)
- [ ] Add `decimal`/`decimal(p, s)` to the lexer keyword table and type grammar (EBNF)
- [ ] Parser support for the `(precision, scale)` type parameters, reusing the array
      fixed-size parsing pattern where practical
- [ ] Semantic analyzer: type checking, promotion rules with `int`/`float`/`double`
      (explicit cast required per the Arithmetic Semantics decision above), literal
      parsing (`19.99` as a decimal literal, not always inferred as `float`/`double`)
- [ ] Codegen: C runtime representation (scaled integer struct) plus arithmetic helper
      functions (add/subtract/multiply/divide/round/compare/format) - a natural fit for
      Task 15.2's runtime-API lowering layer once that exists, rather than another
      special case bolted directly onto `visit_CallExpr`
- [ ] `len()`-style formatting helper (or a `.toString()`/interpolation format specifier)
      that prints the exact declared scale (e.g. always 2 decimal places for money),
      not a floating-point default
- [ ] Add `Currency` as a reserved keyword accepting the same optional `(p, s)` parameters
      as `decimal` - `Currency(p, s)` resolves to `decimal(p, s)` exactly as written; bare
      `Currency` resolves to the project's configured default shape (`decimal(11, 2)` unless
      overridden). Resolve this during name resolution/type checking, immediately rewriting
      to the equivalent `decimal(p, s)`, so every later pass - type checking, codegen - only
      ever needs to understand `decimal`, never a second parallel type
- [ ] Read `[types].currency_precision`/`currency_scale` from `fusion.toml`
      (`src/config/project_config.py`, extending Task 12.12's schema) to override bare
      `Currency`'s default shape per project - explicit `Currency(p, s)` always overrides
      this, same precedence as everywhere else project config meets an explicit declaration
- [ ] Example program in `examples/` demonstrating money-like arithmetic with both
      `decimal(p, s)` and `Currency` side by side (per Rule 5 / Task 16 - add this to that
      task's checklist once decimal/Currency are scoped for real)
- [ ] Documentation: `files/fusion-language-spec.md` Data Types section, `files/fusion.ebnf`,
      `CLAUDE.md` Quick Syntax Reference, Reserved Keywords, and Project Configuration
      section

[< 032 DomainPackages](032-DomainPackages.md) | [Index](index.md) <!-- nav -->
