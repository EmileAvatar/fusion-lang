# Literals - a proposal

**Status: a proposal only (2026-10-24), not part of the design yet.** It collects the ways a
value could be written directly in Fusion source. Some of these may become Fusion literals.
Others will belong to a future class that handles units (time, data sizes, money) instead of
being part of the language itself. Nothing here is scheduled in `FEATURES.md` yet.

---

## What a literal is

A **literal** is a value written directly in the source: `42`, `"hi"`, `'A'`. A **number
literal** can have up to three parts:

```text
 0x   FA_FA          -> a hex number
 --   -----
prefix  digits

      500   ms       -> a duration
      ---   --
    digits  suffix
```

- **Prefix** (a radix or base prefix): sets how the digits are read: `0x` hex, `0b`
  binary, `0o` octal.
- **Digits:** `_` may group them (`1_000_000`) and is ignored.
- **Suffix** (a unit or type suffix): letters glued straight onto the digits: `ms`, `GB`,
  `L`. C++ calls user-made ones "user-defined literals"; F# has "units of measure".

The **lexer** tells them apart. It reads the prefix, then the digits, then any letters
glued on, and makes one token.

---

## Built today

| Literal | Example | Meaning |
|---|---|---|
| Whole number | `42` | `int` |
| Grouped digits | `1_000_000` | `_` is ignored |
| Hex | `0xFAFA` | base 16 |
| Binary | `0b0101` | base 2 |
| Octal | `0o17` | base 8 |
| Decimal | `2.5` | `float` / `double` |
| Long suffix | `123L` | read by the lexer; `long` is not a built type yet |
| Float / double suffix | `3.14f`, `3.14d` | read by the lexer |
| Character | `'A'`, `'é'` | `char` |
| Text | `"hi"`, `"{name}"` | `string`, with interpolation |

---

## Proposed

| Kind | Examples | Notes |
|---|---|---|
| Durations | `500ms`, `5s`, `2min`, `1h` | Agreed for services: an `int` of milliseconds (FEATURES.md 42.16) |
| More durations | `10ns`, `10us`, `1d` | Nanoseconds, microseconds, days |
| Data sizes | `512B`, `4KB`, `5MB`, `5GB`, `5GiB` | `B` byte, `b` bit; 1000 or 1024 (rule 4) |
| Unsigned | `10u` | The spec designs `uint` |
| Money to decimal | `decimal total = 19.99m` | See "Money" below |
| Scientific | `1.5e3`, `2E-8` | 1500.0, 0.00000002 |
| Percent | `50%` | 0.5 |
| Date / time | `2026-10-24`, `14:30` | Better in the Time module (FEATURES.md 43.1) |

#### Money

Money gets its **own dedicated type** (to be designed), not a literal of its own.
- `m` converts a money value to `decimal`: `decimal total = 19.99m`.
- Converting to `int` **rounds up**. Whether that means always up (19.01 becomes 20) or
  half up (19.49 becomes 19, 19.50 becomes 20) is still to be settled.

---

## Rules the compiler would need

1. **The suffix is glued on.** `5s` is a duration; `5 s` is the number 5 followed by a name
   `s`.
2. **A closed list of suffixes.** An unknown suffix (`5xyz`) is a compile error, never
   silently ignored.
3. **Case matters, because units clash.** `m` could mean milli, minute, metre or money, so
   durations use `min`, never `m`. `M` (mega) is not `m` (milli). `B` (byte) is not `b`
   (bit): `5Gb` is 5 gigabits, an eighth of `5GB`.
4. **1000 or 1024.** `5GB` can mean 5 x 1000^3 bytes, as disk makers count, or 5 x 1024^3,
   as Windows counts. The usual fix is two spellings: `GB` = 1000^3, `GiB` = 1024^3. It must
   be decided, never guessed.
5. **Months and years are not durations.** A month is 28-31 days, and a year is 365 or 366,
   so `1month` can't be a fixed number of milliseconds. They belong to the calendar part of
   the Time module (FEATURES.md 43.1).
6. **Inside hex, letters are digits.** In `0x1d`, the `d` is a hex digit (the value 29), not
   a double suffix.

---

## Literal or class?

The rough split, for when this is designed:
- **Fusion literals:** the number forms (bases, grouping, scientific, the type suffixes) and
  the durations services need.
- **A future units class:** data sizes, money, dates, times and anything that needs
  conversion rules or a calendar.
