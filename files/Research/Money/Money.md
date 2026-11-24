# Money and decimals: COBOL and other languages (Research R10)

For Task 47 (47.2 `money`, 47.6 ranges over money). Started and written 2026-11-24.

**The question:** how do COBOL and other languages handle money accurately, and does Fusion's preference hold? The
preference (user, 2026-11-23) is that money stays a `long` of minor units (D.021), the Currency module (43.3) gives it
its meaning, and a decimal type is the backup.

**The short answer:** yes, with two additions.
- A `long` is enough to *hold* any amount of money.
- *Calculating* with money needs more room for the steps in between, because COBOL keeps 30-31 digits there. Fusion
  can use 128 bits for those steps and round once, at the end.
- A rate (a percentage, tax, an exchange rate) is not money. It needs its own exact form with more places.

Nothing here is decided. Section 5 lists the decisions for the user.

## Contents
- [1. COBOL - why banks still trust it](#1-cobol---why-banks-still-trust-it)
- [2. Other languages](#2-other-languages)
- [3. Money in practice](#3-money-in-practice)
- [4. For Fusion: the preference checked](#4-for-fusion-the-preference-checked)
- [5. Decisions for the user](#5-decisions-for-the-user)
- [Sources](#sources)

---

## 1. COBOL - why banks still trust it

- **Fixed-point fields:** `PIC S9(7)V99` is a signed number with 7 digits before an implied decimal point (`V`) and 2
  after. The point is never stored; the compiler knows the scale of every field, so the value is exact.
- **Storage:**
  - `DISPLAY`: one digit per byte;
  - `COMP-3` / `PACKED-DECIMAL`: two digits per byte plus a sign half-byte. The hardware on IBM mainframes does decimal
    arithmetic on it directly;
  - `COMP` / `BINARY`: a binary whole number, with the scale still implied. This is the same idea as Fusion's long of
    minor units.
- **Keeping the scale:** the compiler lines up the implied points before adding. A product's scale is the sum of the
  two scales. Results are stored into the target field's scale.
- **Steps in between:** they keep more digits than any field. IBM Enterprise COBOL keeps up to 30 digits (31 in
  extended mode), and Fujitsu up to 31. The 2002/2014 standards add `ARITHMETIC IS STANDARD-DECIMAL` (34 digits,
  decimal128-like), but few compilers implement it. **This is the key point:** the stored amount is small, but the
  steps in between are wide.
- **Rounding:**
  - **Without `ROUNDED`, extra places are cut off** (truncated) when a result is stored. This is a well-known COBOL
    pitfall: 2177.705 becomes 2177.70.
  - `ROUNDED` alone is half away from zero, in traditional COBOL.
  - COBOL 2014 adds `ROUNDED MODE IS` with eight modes: AWAY-FROM-ZERO, NEAREST-AWAY-FROM-ZERO, NEAREST-EVEN,
    NEAREST-TOWARD-ZERO, PROHIBITED (an error if rounding is needed), TOWARD-GREATER, TOWARD-LESSER and TRUNCATION.
  - Compilers differ in practice: GnuCOBOL and the mainframe gave 2177.71 against 2177.70 for one ROUNDED
    computation.
- **Overflow:** `ON SIZE ERROR` catches a result too big for its field. Without it, the high digits are silently
  lost. Fusion's rule (D.003) already makes that an OverflowError, never a cut value.
- **Why it is trusted:**
  - every field's places are declared;
  - the steps in between are wide;
  - rounding is written where it happens;
  - the same result on every machine, because it is decimal, never binary floating point.

## 2. Other languages

| Language / type | How | Right | Wrong / pitfall |
|---|---|---|---|
| C# `decimal` | 128 bits: a 96-bit whole number and a scale 0-28 (base 10) | exact base-10; `123.45m` literal; overflow is an exception | `Math.Round` defaults to banker's (surprises people); a scale that floats with the value, so `1.0m` and `1.00m` differ in print |
| Java `BigDecimal` | any size, a scale per value | `divide` with no mode throws when the result doesn't end (1/3) - **no silent default**; `RoundingMode` named at each step | wordy; `new BigDecimal(0.1)` takes the double's error (use the string form); `equals` compares the scale (2.0 is not 2.00) |
| Python `decimal` | any size, a context (precision 28, `ROUND_HALF_EVEN`) | the context is set once, and its traps can make inexact results an error | the context is global per thread - code far away can change it |
| SQL `DECIMAL(p, s)` / `NUMERIC` | fixed precision and scale per column | declared places, as COBOL's PIC | the precision of division results follows rules that surprise people (scale cut to 6 in SQL Server) |
| SQL Server `MONEY` | a 64-bit whole number with 4 fixed places | small and fast - the same idea as Fusion | **its known flaw:** dividing rounds to 4 places at each step, so a calculation loses precision (0.00009 rounds the wrong way); Microsoft and Red Gate say to use DECIMAL. The lesson: the *stored* form being narrow is fine, the *steps in between* must not be |
| PL/I `FIXED DECIMAL(p, q)` | declared precision and scale, as COBOL | the language rules work out each result's precision | the rules for the precision of a division are complex |
| Ada fixed-point and `delta ... digits` decimal types | a type declares its step (`delta 0.01 digits 14`) | the type itself carries the money's places - the closest to Fusion's money + Currency | rarely used outside Ada |
| IEEE 754-2008 `decimal64` / `decimal128` | decimal floating point (16 / 34 digits) | exact base-10 for most amounts; `roundTiesToEven` the default | still floating: very large or small values lose places; little hardware support (IBM POWER / z only) |
| Rust (`rust_decimal`), Go (`shopspring/decimal`) | libraries, as C#'s / BigDecimal | exact | not built in - every project picks one, and the libraries don't mix |
| JavaScript | nothing built in - only a binary double | - | `0.1 + 0.2 != 0.3`; money in a double is the classic bug; libraries (dinero.js) work with whole minor units |

**What they agree on:**
- never a binary float;
- the places are known exactly;
- overflow is an error;
- rounding is named, not hidden.

**Where they differ:** the default rounding mode, and whether the places belong to the type (COBOL, SQL, Ada) or to
each value (C#, BigDecimal).

## 3. Money in practice

- **Minor units against a decimal type:**
  - Stripe, Adyen and most payment systems send amounts as **whole numbers of minor units** (`amount: 12345` for
    123.45), with the currency beside it. This is the same as Fusion's D.021.
  - Banks' cores (COBOL) use fixed decimals with declared places.
  - Both are exact. Minor units are smaller and faster; a decimal type covers more places.
- **Each currency's places (ISO 4217):**
  - 2 for most (USD, EUR, ZAR);
  - 0 for JPY and KRW;
  - 3 for KWD, BHD and OMR (and 4 for the Chilean CLF, an accounting unit).
  - Crypto needs far more: BTC has 8 places (satoshi), ETH 18 (wei).
- **Rounding rules, by use:**
  - Banking and statistics use **half-even** (banker's). Over many roundings it doesn't drift upward.
  - Retail, invoices and tax law mostly use **half-up** (half away from zero). The EU's euro conversion rule
    (Regulation 1103/97, article 5) rounds half a cent up.
  - Some taxes and interest rules say "always down" or "always up".
  - **There is no single right default.** The rule belongs to the business, and it must be visible where it happens.
- **Splitting an amount (Fowler's Money pattern, `allocate`):**
  - R100 / 3 is 33.34 + 33.33 + 33.33. The parts always add up to the whole, and the remainder cents go to the first
    parts, one each.
  - Splitting by ratios (70 / 30) works the same way.
  - Never multiply by 0.3333.
- **The order of steps matters:** round each line, then add (invoice lines), or add, then round once (interest
  accrual). The two give different totals. Each use names its own order.
- **The range needed:**
  - A long holds plus or minus 9.22 x 10^18 minor units. With 2 places that is about 92 quadrillion currency units;
    with 3 places (KWD), 9.2 quadrillion. That is enough for any real amount (world GDP is about 10^14 USD).
  - The steps in between are different. An amount times a rate with 6 places (123.45 x 1.234567) needs about 10^25
    before rounding, which a long can't hold. 128 bits (about 1.7 x 10^38) can. This is COBOL's 30-31 digits.
  - Crypto with 18 places: a long holds only 9.2 ETH in wei. That is decimal territory (the backup).
- **Exchange rates, percentages and tax rates are not money:**
  - they have more places (a rate like 18.234567, a tax rate like 15.5%);
  - they are never added to money;
  - money times a rate is money, rounded once.
  - Storing a rate as money would cut it.

## 4. For Fusion: the preference checked

| Point | Finding | Suggested for Fusion |
|---|---|---|
| Money a long of minor units (D.021) | the same as payment systems and SQL Server's MONEY; the amount always fits | **keep** |
| Its places per currency | ISO 4217 places 0-3 (4 for CLF) | `[money] decimals` (default 2) per project; the Currency module (43.3) per value's currency |
| The steps in between | SQL Server's MONEY shows what goes wrong when they are narrow; COBOL keeps 30-31 digits | **new:** money arithmetic with a rate (`*`, `/`, `percent`, a currency conversion) is done in **128 bits** (GCC's `__int128` - fast) and rounded **once** at the end; an overflow of the stored long is still an OverflowError |
| Rates | not money - more places | **new:** a rate is written as a decimal number (`m * 1.155`, `m.percent(15.5)`) and kept exact as a whole number with its scale (1155 / 1000) - never a double; its places limited (e.g. 9) |
| Rounding default (Q.048) | half-even: banking, IEEE, Python, C#; half-up: retail, tax law, the euro rule; COBOL without ROUNDED cuts | **keep halfEven** as the default (no drift) - but an operation that rounds can name its mode (`m.percent(15, halfUp)`), and `[money] rounding` sets the project's; COBOL's silent cut never happens |
| Rounding inexact by accident | BigDecimal and COBOL's PROHIBITED make it an error | an option: `[money] rounding = "exact"` - a result needing rounding is an error (for code that must never round) |
| Literal (Q.047) | COBOL PIC and SQL declare the places; C# uses `123.45m` | **keep A**: `money price = 123.45`, more places than the minor unit a compile error (never a silent cut); `123.45m` as quick typing where the type isn't written |
| Printing | the amount alone; the symbol and grouping are the Currency module's | `123.45`, `-0.50`, always the minor unit's places |
| Splitting | Fowler's allocate | `m.split(3)` / `m.split([70, 30])` - parts add up exactly, the remainder to the first parts (47.2.2) |
| Overflow | COBOL's ON SIZE ERROR | already D.003 - an OverflowError |
| The decimal backup | needed for crypto (18 places), unit prices with more places (fuel per litre, 3; share prices, 4) and rates | `decimal(p, s)` (TYP.015) after money - a long holds p up to 18; past that 128 bits; the same 128-bit steps |
| Ranges over money (47.6e) | whole minor units, so exact | unchanged - waits for the literal (A) |

## 5. Decisions for the user

Each one goes to OpenQuestions.md as a question with options:
- **Q.047** (the literal), **A** for now: the research **supports A**. `123.45` checked against the places, and `m`
  as quick typing.
- **Q.048** (the default rounding), **A** for now: the research **supports A** (halfEven). It adds that an
  operation may name its mode, and an `"exact"` setting.
- **Q.051 (new):** the steps in between: 128 bits, rounded once at the end?
- **Q.052 (new):** how a rate is written and kept: a decimal literal kept exact, or a `rate` type?

---

## Sources
- [How COBOL handles division rounding by default (Stack Overflow)](https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/30215023/how-cobol-handles-division-rounding-by-default) - the ROUNDED MODE values; truncation without ROUNDED
- [GnuCOBOL users list, 2010](https://lists.gnu.org/archive/html/gnucobol-users/2010-02/msg00015.html) - one ROUNDED computation, two results across compilers
- [IBM Enterprise COBOL: intermediate results and arithmetic precision](https://www.ibm.com/support/knowledgecenter/SS6SG3_6.1.0/com.ibm.cobol61.ent.doc/PGandLR/concepts/cpinr02.html) - 30 / 31 digits
- [IBM: PACKED-DECIMAL (COMP-3)](https://www.ibm.com/docs/en/SS6SG3_6.3.0/perf/packed_decimal.html)
- [Fujitsu COBOL arithmetic statements](https://bs2manuals.ts.fujitsu.com/psCOBOL2000V16en/arithmetic-statements-cobol-compiler-reference-manual-2022-11-192-5298372.html) - 31 digits
- [GCC patches list on COBOL STANDARD-DECIMAL](https://mail-archive.com/gcc-patches@gcc.gnu.org/msg367999.html)
- [Red Gate: avoid MONEY and SMALLMONEY (BP022)](https://www.red-gate.com/hub/product-learning/sql-prompt/avoid-use-money-smallmoney-datatypes)
- [DZone: how to store money in SQL Server](https://dzone.com/articles/how-to-store-money-in-sql-server)
- [MSSQLTips: the money type against decimal](https://www.mssqltips.com/sqlservertip/7431/sql-money-data-type-sql-decimal-monetary-values-sql-server/)
- [Born SQL: how SQL Server stores money](https://bornsql.ca/blog/how-sql-server-stores-data-types-money/)
- General knowledge, not looked up this session:
  - C# decimal, Java BigDecimal, Python decimal, Ada, IEEE 754-2008;
  - ISO 4217;
  - the EU Regulation 1103/97;
  - Fowler's Money pattern (Patterns of Enterprise Application Architecture).
