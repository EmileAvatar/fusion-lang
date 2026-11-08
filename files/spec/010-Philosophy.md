[Index](index.md) <!-- nav -->

# 010 Philosophy and Syntax Overview

What Fusion aims for, and how its source text is written. Status lines: see `index.md`.

## Language Philosophy

**Status:** [DESIGN] the principles every task follows

Description: Core principles guiding Fusion's design decisions.

* Performance First: Compiled to native code with optional JIT
     * C-style memory control when needed
     * Automatic memory management by default
     * Zero-cost abstractions

* Readable and Expressive: Natural language constructs
     * VB.NET-style keyword readability
     * Python-style indentation significance
     * Clear intent over brevity

* Type Safety with Flexibility: Strong typing with inference
     * Java-style static typing
     * Python-style duck typing option
     * Gradual typing support

* Modern Features: Built for today's development
     * First-class functions
     * Pattern matching
     * Async/await native support
     * Null safety by default

* Concurrency Model: Safe and efficient parallel execution
     * Go-style channels and goroutines
     * Message passing for safety
     * Shared memory with automatic locking
     * Race and deadlock detection

---

## Syntax Overview

**Status:** [DONE 01-04, 19.6] the three block styles (indentation, braces, `End` keywords) and the source text rules

Description: Core syntax elements borrowed from each parent language.

* From Python: Indentation-based blocks, simple syntax
* From Java: Type annotations, interface contracts
* From C: Pointer operations, memory control (optional)
* From VB.NET: Readable keywords, property syntax
* From Go: Channels, goroutines, multiple return values, defer

---

### Source Text Rules (implemented - Task 19.6)

Fusion source is UTF-8. Ordinary Unicode text is fully allowed in **strings and comments**
(`"café"`, `// 中文`), but a few rules exist to block attacks where code *looks* different from
what it actually does. Security principle: never trust code - including your own imported
dependencies.

**1. Invisible and bidirectional control characters are rejected anywhere in a file** -
including inside comments and string literals. These characters can make code display
differently than it compiles (the "Trojan Source" attack, CVE-2021-42574): a reviewer reads
one thing while the compiler builds another. Rejected:
- Bidirectional controls: U+202A-U+202E, U+2066-U+2069, U+200E, U+200F, U+061C
- Invisible/zero-width: U+200B, U+200C, U+200D, U+2060, and U+FEFF - except a byte-order
  mark as the very first character of a file, which is allowed (many Windows editors add one)

This rule is not configurable. To put such a character in a string on purpose, write it
visibly with an escape (rule 3).

**2. Identifiers are ASCII-only by default** (`A-Z`, `a-z`, `0-9`, `_`). Look-alike letters
from different scripts can make two different names appear identical - Cyrillic `а` (U+0430)
looks exactly like Latin `a`, so `аge` and `age` could be two different variables. A project
that wants non-English identifiers opts in:

```toml
# fusion.toml
[source]
allowUnicodeIdentifiers = true
```

Even with the opt-in, an identifier is still rejected if it mixes letters from look-alike
scripts (Latin, Cyrillic, Greek, Armenian, Cherokee, Coptic) or contains compatibility
characters such as fullwidth or mathematical letters (`ｆｏｏ`). Known limitation: two
identifiers written *entirely* in different look-alike scripts aren't caught in opt-in mode -
full Unicode TR39 confusable detection is deferred, which is why ASCII-only is the default.

**3. Names are case sensitive by default** (`count` and `Count` are two names, as in most
languages). A project that wants one name whatever its case turns it off; then two names
that differ only in case are an error, each pair listed (Task 32.11):

```toml
[source]
caseSensitive = false
```

**3. `\uXXXX` escapes** - exactly four hex digits, in string and char literals:

```fusion
string joiner = "a‍b"   // the visible way to write an invisible character
string letter = "A"     // "A"
```

**4. Char literals hold one ASCII character** (`'a'`, `'\n'`, `'A'`). A Fusion `char` is a
single byte in the generated C, so anything beyond U+007F belongs in a string.

**5. Digits are ASCII** - other Unicode digits (e.g. Arabic-Indic `٣`) never start a number.

[Index](index.md) <!-- nav -->
