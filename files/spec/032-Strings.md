[< 031 Arrays](031-Arrays.md) | [Index](index.md) | [033 TypeCasting >](033-TypeCasting.md) <!-- nav -->

# 032 Strings

Contents: [Length](#length) | [Encoding](#encoding) | [Ownership](#ownership) | [Planned](#planned) | [When a program ends](#when-a-program-ends) | [Names in the generated C](#names-in-the-generated-c) | [Built-in type classes](#built-in-type-classes) | [Comparison](#comparison) | [String operations](#string-operations) | [Raw bytes](#raw-bytes) | [Versatile string functions](#versatile-string-functions)

## Strings

Description: Strings are **values**, like structs (decided 2026-10-09, Task 18.3).

**Implementation status:**
- 18.3.1 (values, automatic cleanup, comparison) - implemented
- 18.3.2 (operations below) and 18.3.2b (Unicode by default) - implemented
- Interpolated strings outside `print` are 18.3.3 - see `files/FEATURES.md`

#### Length

**Length (Task 18.3.4b, user decisions 2026-10-09):**
- Strings grow as large as the machine allows - no limit by default (`[strings] maxLength = "max"`)
- A project for a memory-constrained device or app can set a number of characters
- A string longer than that is always an **error**, never cut:
  - a compile error for text written in the source
  - a run-time error (naming the file and line) for text built while the program runs
- Why: a silent cut causes more problems than it solves - and other languages agree: Python, Java, C#, Go and
  Rust never cut strings; SQL Server, PostgreSQL and strict-mode MySQL reject too-long values with an error
- Paged strings (loading only part of a huge string) are a later, advanced feature

#### Encoding

**Encoding (Task 18.3.2b, user decision 2026-10-09):**
- Text is Unicode, stored as UTF-8, by default
- `len(s)` counts **characters** (also written `s.len()`, `s.length()`, `s.len`, `s.length` - Task 30.8,
  `length` is quick typing for `len`)
- `lenb(s)` counts **bytes** (for files, networks, databases)
- `s[i]`, `substring` and `indexOf` count characters
- A `char` holds any Unicode character (`char c = 'é'`)
- Speed:
  - plain ASCII text keeps a fast path (no scanning)
  - text with other characters remembers the last position found (Task 44.6), so a loop over `s[i]` - or
    `substring` - doesn't count from the start each time (a 5,000-line loop: 52 s before, 0.03 s after)
- `[strings] encoding = "ascii"` in `fusion.toml`, for very small or legacy devices:
  - English text only (non-ASCII text is a compile error)
  - a `char` is one byte
  - `utf-16` and `utf-32` are named for the future but not implemented yet
- Helpers: `isAscii(s)`, `asciiOnly(s, replacement)`, `charCode(c)`, `fromCharCode(n)`, `byteAt(s, i)`
- "Character" means a Unicode code point; what a reader sees as one symbol can occasionally be several code
  points (some emoji, combining accents) - grapheme handling is a later, advanced feature

#### Ownership

* **Ownership**
     * Each string variable, struct field and array element owns its own text
     * Copying a string (`b = a`, passing it into a struct, returning it) gives an
       independent copy - changing one never changes the other
     * The compiler frees every string automatically, exactly once: when its block ends,
       on `return`, `break` and `continue`, and - for a temporary result nobody keeps - at
       the end of its statement. There is no garbage collector and nothing to free by hand
     * Text written in the source costs nothing at run time and is never freed; only
       strings built while the program runs use memory
     * Function parameters borrow the caller's string (no copy); a function that assigns
       to a parameter works on its own copy, so the caller's string never changes
     * One character can be changed in place: `s[i] = c` (Task 29.1) - only in that
       variable's own text (a copy made before, the literal and a caller's string are
       unchanged); the index is checked (IndexError); a character of another byte width
       moves the rest. A `const string` is fixed (29.2): `s[i] = c` on it is a compile
       error. String literal prefixes `m"` / `f"` / `p"` were considered and rejected
       (2026-10-27): a plain string already can change, `const` already fixes one, and
       literals are already stored once

#### Planned

**Planned (advanced, after MVP - user decision 2026-10-09):** these remain part of Fusion's design and will be
added on top of the simple value model above, which is what MVP needs:
- a **string pool** (shared storage for identical text, Task 29)
- **garbage collection** as a project-selectable memory strategy
- copy-on-write sharing
- (Method-call syntax, `name.toUpper()`, arrived with Task 18.3.7 - see "Built-in type classes")

#### When a program ends

**When a program ends** (user requests 2026-10-11, 2026-10-28):
- With `[build] wait_at_exit = true` a compiled program waits for a key ("Press any key to close...", on
  stderr) before its window closes
- So a program started by double-clicking it doesn't vanish before its output, or a run-time error, can be read
- **Off by default**: it is for development, the examples (`examples/fusion.toml` turns it on) and testing -
  or an app that should show its details to the customer
- `--headless` closes at once
- It never waits when its input or output is redirected (pipes, files, tests)

#### Names in the generated C

**Names in the generated C** (Task 18.4.1, closes 15.8): a Fusion name never collides with C or with the runtime
- Functions and struct types get a `fu_` prefix in C (`add` -> `fu_add`, `Point` -> `fu_Point`; `main` stays `main`)
- A local or parameter whose name would break the C gets one too: `auto`, `register`, `printf`, `uint8_t`,
  `NULL`, or starting with `fusion_` / `fu_`
- So a program may name a function `free`, `exit` or `abs`, or a variable `auto`
- Struct fields keep their names (only C keywords change)

#### Built-in type classes

**Built-in type classes** (Task 18.3.7, user decisions 2026-10-10): every built-in function can be called three
ways, all compiling to the same C call - no objects, no memory or speed cost:
- plain: `toUpper(name)` (kept - nothing breaks)
- a method on a value: `name.toUpper()`, `"Claude".toUpper()`, `255.toHex()`, `p.name.trim().toTitle()`
  (chained); the value becomes the first argument
- through the class: `String.toUpper(name)`, `Int.parseInt("ff", 16)`

The rules:
- The classes are `String`, `Bytes`, `Int`, `Char`, `Float`, `Double`, `Byte` and `Bool`
- A function belongs to the class of its first argument's type (`len` and `toString` to every class they accept)
- Statics that make a value of their class belong to that class only: `Int.parseInt` / `Int.fromHex` /
  `Int.fromBinary` / `Int.fromOctal`, `Char.fromCharCode`, `Bytes.newBytes` / `Bytes.hexToRaw` / `Bytes.toBytes`
- Methods keep the function names
- A method always means the built-in - a program's own function `left` or a variable named `left` can't hide
  `s.left(3)`
- `print`, `range` and `format` stay plain functions
- A `.` followed by a letter ends a number literal, so `255.toHex()` works; `255.0` and `2.5` are unchanged
- A struct can't be named after a class (a variable can)
- Methods on structs (`p.move(1, 2)`) are user-defined classes - after MVP

#### Comparison

* **Comparison**: `==` and `!=` compare the text; `<`, `>`, `<=`, `>=` compare alphabetically
  (byte order). (Before Task 18.3.1, `==` compared memory addresses - right only by accident)

```
string name = "Enterprise"
string copy = name             // an independent copy
copy = "Modified"              // name is still "Enterprise"
bool same = name == "Enterprise"   // true - compares the text
```

#### String operations

* **String Operations** (Task 18.3.2, implemented): all return a new string and leave the
  original unchanged. Each is also a method (`name.toUpper()`, Task 18.3.7). Lengths and
  indexes count characters
     * `a + b` joins strings (or a string and a char); numbers are joined with interpolation
       (`"{name}{count}"`) - `"a" + 5` is a compile error
     * `len(s)` (characters), `lenb(s)` (bytes); `s[i]` reads one `char` - a bad index stops
       the program with a run-time error naming the file and line
     * `substring(s, start, count)`, `contains(s, part)`, `indexOf(s, part, from = 0)` (-1 if absent),
       `startsWith`, `endsWith`, `toUpper`, `toLower`, `trim`
     * `toString(x)` for int/float/double/bool/char/string; `toInt(s)`, `toFloat(s)` stop the
       program with a clear error on text that isn't a number - check first with `isInt(s)` /
       `isFloat(s)` (until error handling, Task 26, makes it catchable)
     * A program's own top-level function or struct may reuse one of these names (`left`,
       `right`, `trim`, ...) and then replaces the built-in; a local variable simply hides
       it inside its block. The core built-ins `print`, `len`, `range` and `format` can't be
       replaced (Task 18.3.6)

#### Raw bytes

**Raw bytes** (Task 18.3.8, user request and decisions 2026-10-10) - for raw / hex work now and for
self-hosting later (reading and writing files is Task 18.5):
- `byte` is one raw byte, **unsigned 0-255** (as C#, Go, Rust and Python - `sbyte` for -128 to 127 is for later)
  - an int literal 0-255 can be stored in a byte (`0x6B`, `105`)
  - any other int needs `toByte(n)`, which stops with a run-time error when the value doesn't fit - never a
    silent cut
  - a byte widens to int automatically, and arithmetic on bytes gives an int (as in C#):
    `byte b = d[0] + 1` is an error
- `bytes` is a growable array of bytes
  - like a string it is a value - a copy is independent, it's freed automatically, it works in struct fields
    and arrays
  - but it holds **any** bytes (no text rules, no `[strings] maxLength`)
  - and is **edited in place**: `b[2] = 0x69`; a function that edits a `bytes` parameter edits its own copy
- Making:
  - `bytes b` (empty)
  - `bytes b = [0x6B, 0x69]` (an array literal becomes bytes when it is stored straight into a bytes variable)
  - `newBytes(n, fill = 0)`
  - `toBytes(x, bigEndian = false)` - from a string (its UTF-8 bytes), a char, a byte, or an int (4 bytes)
  - `hexToRaw("6b69")`
- Reading: `b[i]` (bounds-checked), `len(b)`, `b == c` (byte by byte), `slice(b, start, count)`,
  `indexOf(b, pattern, from = 0)`, `getInt(b, at)` (4 bytes), `getInt16` / `getUInt16` (2 bytes)
- Changing:
  - `b[i] = x`, `b + c`, `b + 0x0A` (append a byte), `0x01 + b` (prepend)
  - `setInt(b, at, value)`, `setInt16(b, at, value)` - these two change `b` itself, so `b` must be a variable
    (or a field / element of one) that isn't const
- Back to text: `toString(b)` - the bytes must be valid text (UTF-8, or ASCII in an ascii project), else a
  run-time error; check first with `isText(b)`
- **Byte order:**
  - little-endian by default (258 -> `02 01 00 00` - x86 / ARM, Windows, ZIP and most file formats)
  - pass `bigEndian = true` (the last argument) for network order
  - a 16-bit `setInt16` accepts -32768 to 65535
- Hex: `rawToHex(b)` -> "6b6b69"; `hexToRaw(h)` -> bytes (any bytes); the text versions `bytesToHex` /
  `hexToBytes` (18.3.6d-1) stay as they are
- **Printing** `"{b}"` shows plain lowercase hex with nothing added - "6b6b696a6b"
  - no spaces or brackets are added without the developer asking (user decision): display formatting belongs to
    downstream modules or the developer's own code
- Outside the bytes - an index, a slice, a 4-byte read too close to the end - is a run-time error naming the
  file and line

```
bytes data = toBytes("kkkkk")      // 6b6b6b6b6b
data[2] = 0x69                     // kkikk - one byte edited in place
data[3] = toByte(fromHex("6A"))    // kkijk
print(toString(data))              // kkijk
```

#### Versatile string functions

**Versatile string functions** (Task 18.3.6, user decisions 2026-10-09) - built-in functions, all counting
characters and returning a new value:
- **Inspect** (18.3.6a):
  - `isEmpty(s)`
  - `isBlank(s)` (only spaces / tabs / newlines - an empty string is blank)
  - `isDigits(s)` (0-9, not empty), `isLetters(s)` (not empty)
  - `countOf(s, part)` (non-overlapping: "aaaa" holds "aa" twice)
- **Search** (18.3.6a): `indexOf(s, part, from)`, `lastIndexOf(s, part)`, `containsAny(s, chars)` (any one of
  the characters)
- **Extract** (18.3.6a): `left(s, n)`, `right(s, n)` - up to n characters
- **Change** (18.3.6b):
  - `replace(s, old, new)` (every match; an empty `old` changes nothing), `replaceFirst`
  - `insert(s, index, part)`, `remove(s, start, count)`, `repeat(s, n)`
  - `reverse(s)` (by character), `trimStart`, `trimEnd`
  - `capitalize(s)` (the first letter)
  - `toTitle(s)` (the first letter of each word - words are separated by spaces, tabs and newlines); only first
    letters change, so "NASA" stays "NASA": use `toTitle(toLower(s))` for "Hello World" from "HELLO WORLD"
  - `toUpper` / `toLower` change ASCII and Latin-1 letters ("cafe-acute" -> "CAFE-ACUTE"; sharp s has no
    one-letter capital and stays as it is)
- **Padding** (18.3.6c):
  - `padLeft(s, width, fill = ' ')`, `padRight`, `center` (an odd extra fill goes on the right)
  - the fill is any character; a string already `width` characters or wider comes back unchanged
  - `truncate(s, width)` gives the first `width` characters and **adds nothing** - no "..." (user decision
    2026-10-10: an added ending would conflict with what developers expect); a shorter string comes back unchanged
- **Number bases** (18.3.6d-1, user decisions 2026-10-10):
  - `toHex(x, width = 0)`, `toBinary`, `toOctal` take an int **or** text holding a whole number (`toHex(255)` and
    `toHex("255")` -> "ff"), lowercase, zero-padded to at least `width` digits (`toHex(255, 4)` -> "00ff")
  - a negative number is its 32-bit **two's complement** pattern, as in C, C#, Java's toHexString and every
    debugger: `toHex(-1)` -> "ffffffff"
  - `fromHex(s)`, `fromBinary`, `fromOctal` and `parseInt(s, base)` read text back - either case, an optional
    `0x` / `0b` / `0o` prefix and a leading `-`
  - for bases 2, 8 and 16 a 32-bit pattern reads as its two's complement value (`fromHex("ffffffff")` -> -1, a
    round trip, as in C#'s Convert.ToInt32); base 10 stays strictly signed
  - `toBase(x, base, width = 0)` writes sign + digits for any base 2-36 (`toBase(-255, 16)` -> "-ff")
  - `isInt(s, base = 10)` checks first; bad text is a run-time error, like `toInt`
  - `bytesToHex(s)` shows the text's UTF-8 bytes ("Hi" -> "4869"); `hexToBytes(h)` turns them back into text -
    an odd length, a non-hex digit or bytes that aren't valid text are run-time errors
- **Number formatting** (18.3.6d-2, user decision 2026-10-09: both styles, chosen per call):
  `formatNumber(n, pattern)` for an int, byte, float or double
  - **Excel/.NET style:**
    - `0` a digit always shown, `#` a digit only if needed, `,` in the whole-number part for thousands groups,
      `.` the decimal point
    - text before and after is printed as it is, and a `%` there multiplies by 100
    - `formatNumber(1234.5, "$#,##0.00")` -> "$1,234.50", `"000"` -> "007", `"0.0%"` of 0.256 -> "25.6%",
      `"0.0##"` keeps up to 3 decimals
    - rounds half away from zero on the number as written (2.675 -> "2.68", as Excel does - a float is read at
      its 7 significant digits, a double at 15)
    - the decimal point is left out when no decimals are shown
  - **printf style** - a pattern that starts with `%`:
    - one conversion: `d i` (rounded to a whole number), `f e E g G`, `x X o` (a whole number's 32-bit
      pattern, like `toHex`)
    - up to 5 flags `- + space 0 #`, width and precision up to 1000, `%%` for a percent sign, and text after
      it: `"%.2f"`, `"%05d"`, `"%8.2f kg"`
    - never `%s`, `%n`, `%p` or `*`: Fusion checks every pattern itself and never hands one raw to C
    - text *before* a number is what Excel style is for (`"$0.00"`)
  - a bad pattern is a compile error when it's written in the source and a run-time error when it's built
    while running
  - separators are fixed to `,` and `.` for now; locales, negative-number sections (`"0.00;(0.00)"`) and
    Excel's scientific notation come later
- **Compare** (18.3.6e):
  - `equalsIgnoreCase(a, b)`, `compareIgnoreCase(a, b)` and `compareNatural(a, b, ignoreCase = false)` return
    -1, 0 or 1 (`<` / `>` on strings stay case-sensitive byte order)
  - ignoring case uses the ASCII + Latin-1 rules of `toLower` ("CAFE-ACUTE" equals "cafe-acute")
  - natural order compares runs of digits by value - "file2" before "file10", "v1.9" before "v1.10"
  - when two strings differ only in leading zeros, the shorter run comes first ("x7" before "x007"), so the
    order is always the same
- **Raw bytes** (Task 18.3.8, user decisions 2026-10-10) - see [Raw bytes](#raw-bytes) above
- **Number literals** (18.3.6d-1):
  - `0xFF`, `0b1010`, `0o17`, with `_` allowed between digits (`0b1111_0000`, `1_000_000`, `2.5_0`)
  - hex, binary and octal literals hold up to 32 bits and read as the bit pattern, like `fromHex`:
    `0xFFFFFFFF` is -1
- **Letters** are ASCII plus Latin-1 (Western European accented letters such as e-acute, u-umlaut, sharp s);
  full Unicode letter and case tables come later
- **Built-ins take optional arguments** like user functions' defaults: `indexOf(s, "a", 5)` or
  `indexOf(s, "a")` (from 0)
- **Out of range:**
  - "up to n" functions (`left`, `right`, padding, `truncate`) clamp quietly - `left("ab", 5)` is "ab"
  - a negative count stops the program with a run-time error
  - positions inside the string (`insert`, `remove`, like `substring`) must be valid
     * **Masking** (designed in Task 18.3.6f, built 2026-10-10 after the user decided all
       nine questions below). "Masking" covers two
       different jobs, and the design keeps them apart:

       **1. Shaping text into a pattern** (input / display masks) - digits or letters poured
       into a template:
       ```
       formatMask("5551234567", "(###) ###-####")     // "(555) 123-4567"
       formatMask("8001015009087", "######-####-###") // an ID number in groups
       formatMask("ab12", "AA-##")                    // "ab-12"
       digitsOnly("(555) 123-4567")                   // "5551234567" - the way back
       ```
       Placeholders (decided): `#` a digit, `A` a letter, `?` any character, `\` makes the
       next character literal; everything else is copied. (`#` matches formatNumber's digit
       placeholder. .NET's MaskedTextProvider uses `0 9 L ? A &` - more choices, harder to
       remember.)

       **2. Hiding part of a value** (redaction - privacy, logs, receipts):
       ```
       mask("4111111111111111", 0, 4)          // "************1111"  keep first 0, last 4
       mask("4111111111111111", 6, 4, '#')     // "411111######1111"  optional mask character
       maskEmail("alice.smith@example.com")    // "a**********@example.com"
       ```
       Card numbers: PCI DSS allows at most the first 6 and last 4 digits to be shown -
       `mask(card, 6, 4)` is exactly that rule.

       Masking only changes what is shown: it is not encryption, and the original value is
       still in memory. Wiping secrets from memory belongs to Task 29.5 (secure strings).

       **Decisions** (user, 2026-10-10):
       1. **Length is kept** - the masked text lines up with the original
          (`a**********@x.com`). Secrets and encryption are the job of a Crypto module, not
          masking
       2. **The mask character is optional, `*` by default** - `mask(card, 6, 4, 'X')`; any
          character (an ascii project: any ASCII character)
       3. **formatMask fills in as far as it fits** - too little input leaves the rest of the
          pattern out; extra input is ignored; no error
       4. **Placeholders: `#` a digit, `A` a letter, `?` any character, `\` for a literal**
          (the simple set - fill-as-far-as-it-fits already covers optional parts, so .NET's
          optional-slot symbols aren't needed)
       5. **Emails** - only the first character of the name is shown by default; how many are
          shown can be configured (an optional argument)
       6. **No built-in country or phone formats** - masking is format-agnostic: the developer
          supplies the pattern (`maskPhone` is dropped; `formatMask` / `mask` cover it)
       7. **Lives in the core string library**; encryption only in Crypto
       8. **The name is `mask`** (`mask`, `maskEmail`, `formatMask`) - not `redact`
       9. **No validation** - masking is about display only (no phone or card checksum checks)

       **As built:**
       - `formatMask(s, pattern)`:
         - skips input that doesn't fit a slot (so "555-123-4567" fills "(###) ###-####" too)
         - shows a literal only once the slot after it is filled ("555" -> "(555", not "(555) ")
         - stops when the input runs out
       - `digitsOnly(s)`
       - `mask(s, keepStart, keepEnd, with = '*')` returns the text unchanged when the kept parts cover it
       - `maskEmail(s, keep = 1, with = '*')` masks the name before the last `@` (text without an `@` is masked
         after its first `keep` characters)
       - Negative counts are run-time errors
       - All are `String` methods too: `card.mask(0, 4)`

```
string original = "Hello"
string upper = toUpper(original)          // "HELLO", original unchanged
string sub = substring(original, 0, 3)    // "Hel"
string joined = original + " World"       // "Hello World"
int n = toInt("42")                       // 42; toInt("12x") stops with a run-time error
```

[< 031 Arrays](031-Arrays.md) | [Index](index.md) | [033 TypeCasting >](033-TypeCasting.md) <!-- nav -->
