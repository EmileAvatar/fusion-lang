[< 080 Arrays](080-Arrays.md) | [Index](index.md) | [090 Unsafe >](090-Unsafe.md) <!-- nav -->

# 081 Strings

**Status:** partly built - strings change in place, `const` strings never (Task 29, [032 Strings](../spec/032-Strings.md)); templates built (29.3); pooling postponed (STR.005, 29.4)

## Mutable vs. Fixed Strings, Templated Fixed Strings & String Pooling

> **Decided since (Task 29, Decisions.md D.059, D.064):** no `m"` / `f"` prefixes - a plain
> string can change, `const string` never does; templates are `template string`; `fixed(n)`
> now means a maximum size.

**Status:** 📝 Proposed
**Priority:** Medium (a real, common source of bugs in other languages - accidental
mutation of a string another part of the program still holds a reference to - but not
blocking anything currently built)
**Source:** User request (2026-09-27) - also logged as **Task 17** in `files/taskSummary2.md`

### Mutable strings (default) vs. fixed/immutable strings

```fusion
string mutable = m"mutable string"   // explicit mutable prefix
string mutable2 = "mutable string"   // same thing - the m prefix is implicit/optional
                                      // on a plain string literal

string fixedString1 = f"fixed string, not mutable"
```

- `m` and plain (no prefix) both mean "ordinary mutable string" - `m"..."` exists purely so `m"..."` and `f"..."` read symmetrically side by side, not because a prefix is required.
- `f"..."` marks the value as **fixed**: once created, nothing about that specific string value can change.
- This is the same idea as Java's/C#'s immutable `String`, and the same prefix-on-a-string-literal pattern Python (`f"..."`, `r"..."`, `b"..."`) and C# (`$"..."`) already use, just applied to mutability instead of formatting/rawness.

**Calling a method on a fixed string doesn't mutate it - it returns a new value:**

```fusion
mutable = "changed string"
printf(fixedString1.ToUpper())

// Output:
// mutable is now "changed string"
// FIXED STRING, NOT MUTABLE      <- fixedString1 itself is completely unchanged after this
```

So "fixed" describes the variable's own stored value, not a restriction on what you can
compute from it - `.ToUpper()` still works, it just can't be the *same* string object
afterward.

### Templated fixed strings - the more novel part

A fixed string containing positional placeholders (`{@1}`, `{@2}`, ...) can be stored once
and then **invoked later, like a function, with different arguments each time**:

```fusion
string fixedString2 = f"fixed string but with {@1} with changable value {@2}. not mutable"

printf(fixedString2("inserted text", "second inserted text").ToUpper())
// FIXED STRING WITH INSERTED TEXT WITH CHANGABLE VALUE SECOND INSERTED TEXT. NOT MUTABLE
```

**This is a real, new capability, not just applying existing syntax to a variable.**
Fusion's `{@1}`/`{@2}` positional interpolation already exists today, but it resolves
*immediately*, at the point the expression is evaluated (e.g. inside a `print(...)` call,
using the arguments given at that call site). What's proposed here is different: the
placeholders stay **unresolved** inside the stored value, and `fixedString2` itself becomes
a reusable, callable template - closer to a compiled format string / a closure over its own
placeholder slots than to today's immediate interpolation. This needs real design before
it's buildable, not just wiring up existing syntax:
- What is `fixedString2`'s actual type - still `string`, or does a placeholder-bearing
  fixed string need a distinct type (e.g. something template/closure-shaped) that happens
  to also support `.ToUpper()`-style chaining once called?
- What happens if the placeholders aren't contiguous (`{@1}` and `{@3}` but no `{@2}`), or
  the call is given the wrong number of arguments - compile-time error (the placeholder
  count is known at the point `f"..."` was written) or runtime error?
- Does this require a new AST node distinct from the existing `InterpolatedStringExpr`, or
  can that node grow a "deferred" mode?

### String pooling - opt-in, not default

```text
Strings are not pooled by default. Each string is stored where it's declared - no implicit
interning/deduplication of equal string values.
```

String pooling (reusing one underlying storage location for multiple equal string values,
as Java and Python both do automatically for at least some strings) is proposed as an
**opt-in project setting**, not a default optimization:

```toml
# fusion.toml
[strings]
pooling = false   # default - matches "no implicit behavior the developer didn't ask for"
```

**Explicit guidance from the request:** only turn pooling on *after profiling* shows it's
actually worth it for a given application - i.e. after confirming a large volume of
repeated/duplicate strings are being created and that reusing storage would meaningfully
help. Pooling isn't free (it needs a lookup/hash step on string creation, and changes the
lifetime story for anything sharing pooled storage), so defaulting it off and treating it as
a measured, deliberate optimization - not a silent language behavior - fits Fusion's general
"don't guess, let the project decide" philosophy already established for `fusion.toml`.

### Security: strings are the wrong type for secrets

Explicitly flagged as unsuitable for passwords/cryptographic material: a plain string
(pooled or not) can end up copied or retained in memory for longer than intended, and can't
be reliably zeroed out once no longer needed - a well-known real problem in other managed
languages (Java's own security guidance recommends `char[]` over `String` for passwords for
exactly this reason - a `String` can't be scrubbed, and if it's ever pooled/interned, a
copy of the secret can persist in memory well past the point the program considers it
"done" with it).

**Proposed answer: a dedicated secure-storage type in a future `fusionlib.Crypto` module**
(Crypto is already one of the 21 envisioned stdlib modules) - explicitly never pooled,
intended to store encrypted-at-rest secrets rather than plain fixed/mutable strings. Marked
explicitly as **far-future** - this depends on the Crypto module existing at all, which
depends on `import` having parser support in the first place (currently none).

**Success Criteria:**
- Mutable strings behave exactly as they do today (no regression - `m"..."` and a plain
  literal are equivalent)
- `f"..."` strings are provably never mutated in place - every "mutating" method returns a
  new value
- A templated fixed string can be invoked multiple times with different arguments without
  ever changing the stored template
- String pooling is off by default and has zero effect on program behavior when disabled;
  enabling it changes memory reuse only, never observable string equality/behavior
- Passwords/secrets have a documented, explicitly-recommended alternative to plain strings

**Deliverables (once scoped and approved):**
- `m"..."`/`f"..."` lexer and parser support
- Semantic rules for fixed-string immutability and templated-fixed-string calling
- `[strings]` `fusion.toml` section (`pooling`)
- Cross-reference from `fusionlib.Crypto`'s eventual design to the secure-storage need
  identified here

[< 080 Arrays](080-Arrays.md) | [Index](index.md) | [090 Unsafe >](090-Unsafe.md) <!-- nav -->
