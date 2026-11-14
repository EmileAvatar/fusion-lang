[< 030 LibraryLayout](030-LibraryLayout.md) | [Index](index.md) | [032 DomainPackages >](032-DomainPackages.md) <!-- nav -->

# 031 Regex

**Status:** idea - no task (a fusionlib module - FEATURES 43.6)

**Contents**

- [Regex Fluent API](#regex-fluent-api)
- [Overview](#overview)
- [Regex Pattern to Method Mapping](#regex-pattern-to-method-mapping)
- [API Design (Option 1: Chainable Builder)](#api-design-option-1-chainable-builder)
- [API Design (Option 2: Static Helpers)](#api-design-option-2-static-helpers)
- [Examples](#examples)
- [Implementation Notes](#implementation-notes)
- [Open Questions](#open-questions)
- [Regex Module (Planned)](#regex-module-planned)

## Regex Fluent API

**Status:** 📝 Proposed
**Priority:** Medium (developer experience enhancement)
**Module:** `fusionlib.Core` (String utilities) OR new `fusionlib.Regex` module
**Depends On:** Basic compiler completion

**Purpose:** Provide human-readable, chainable methods for regex operations instead of cryptic regex symbols

---

### Overview

- Traditional regex is difficult to read and maintain due to symbolic syntax (`\d+`, `[a-z]*`, etc.).
- The Regex Fluent API provides descriptive method names that clearly communicate intent.

**Traditional Regex:**
```fusion
string pattern = "^\d{3}-\d{4}$"  // What does this mean?
```

**Fluent API:**
```fusion
import fusionlib.Regex

Regex phonePattern = Regex.create()
    .regexStartWith()
    .regexFilterNumbers().regexRepeat(3, 3)
    .regexLiteral("-")
    .regexFilterNumbers().regexRepeat(4, 4)
    .regexEndWith()
// Clear: "Start with 3 digits, dash, 4 digits, end"
```

---

### Regex Pattern to Method Mapping

| Traditional Pattern | Meaning | What it Does | Fluent API Method |
|---------------------|---------|--------------|-------------------|
| `.` | Any single character | Matches **any one character** except newline | `.regexAnyChar()` |
| `\d` | Digit (0–9) | Matches **any single digit** | `.regexFilterNumbers()` or `.regexFilterNumbers(0,9)` |
| `\w` | Word character | Matches **letters, numbers, or underscore** | `.regexWord()` |
| `\s` | Whitespace | Matches **spaces, tabs, newlines** | `.regexWhiteSpace()` |
| `\S` | Non-whitespace | Matches **any non-whitespace character** | `.regexNonWhiteSpace()` |
| `^` | Start of string | Ensures match **starts at beginning** | `.regexStartWith()` or `.regexStartWith('pattern')` |
| `$` | End of string | Ensures match **ends at end** | `.regexEndWith()` or `.regexEndWith('pattern')` |
| `+` | One or more | Repeats **previous element one or more times** | `.regexRepeat(1, null)` or `.regexOneOrMore()` |
| `*` | Zero or more | Repeats **previous element zero or more times** | `.regexRepeat(0, null)` or `.regexZeroOrMore()` |
| `?` | Zero or one | Makes **previous element optional** | `.regexOptional()` |
| `{n}` | Exactly n times | Repeats **exactly n times** | `.regexRepeat(n, n)` |
| `{n,m}` | Between n and m | Repeats **between n and m times** | `.regexRepeat(n, m)` |
| `[abc]` | Character set | Matches **any character in brackets** | `.regexFilterCharacters('abc')` |
| `[^abc]` | Negated set | Matches **any character NOT in brackets** | `.regexNotCharacters('abc')` |
| `[a-z]` | Character range | Matches **any character in range** | `.regexRange('a', 'z')` |
| `(pattern)` | Capture group | Groups pattern to **extract or reuse** | `.regexExtractGroup('pattern')` |
| `(?:pattern)` | Non-capture group | Groups without capturing | `.regexGroup('pattern')` |
| `pattern1\|pattern2` | Alternation (OR) | Matches **either pattern** | `.regexOr('pattern1', 'pattern2')` |
| `\b` | Word boundary | Matches **boundary between word and non-word** | `.regexWordBoundary()` |
| `\B` | Non-word boundary | Matches **not at word boundary** | `.regexNonWordBoundary()` |
| `(?=pattern)` | Positive lookahead | Matches if **followed by pattern** | `.regexLookAhead('pattern')` |
| `(?!pattern)` | Negative lookahead | Matches if **NOT followed by pattern** | `.regexNegativeLookAhead('pattern')` |

---

### API Design (Option 1: Chainable Builder)

```fusion
import fusionlib.Regex

// Builder pattern - construct regex step by step
class Regex
    // Start new pattern
    static Regex create()

    // Character matching
    Regex regexAnyChar()
    Regex regexFilterNumbers(int min = 0, int max = 9)
    Regex regexWord()
    Regex regexWhiteSpace()
    Regex regexNonWhiteSpace()
    Regex regexLiteral(string text)

    // Character sets
    Regex regexFilterCharacters(string chars)
    Regex regexNotCharacters(string chars)
    Regex regexRange(char start, char end)

    // Quantifiers
    Regex regexRepeat(int min, int? max)  // null = unlimited
    Regex regexOneOrMore()
    Regex regexZeroOrMore()
    Regex regexOptional()

    // Anchors
    Regex regexStartWith(string? pattern = null)
    Regex regexEndWith(string? pattern = null)
    Regex regexWordBoundary()
    Regex regexNonWordBoundary()

    // Groups
    Regex regexExtractGroup(Regex pattern)
    Regex regexGroup(Regex pattern)
    Regex regexOr(Regex pattern1, Regex pattern2)

    // Lookahead
    Regex regexLookAhead(Regex pattern)
    Regex regexNegativeLookAhead(Regex pattern)

    // Execute
    bool matches(string input)
    List<string> findAll(string input)
    string replace(string input, string replacement)
    string toPattern()  // Get traditional regex string
```

---

### API Design (Option 2: Static Helpers)

```fusion
import fusionlib.Regex

class RegexHelper
    // Pre-built common patterns
    static string emailPattern()
    static string phonePattern()
    static string urlPattern()
    static string ipAddressPattern()

    // Quick matchers
    static bool isEmail(string input)
    static bool isPhone(string input)
    static bool isURL(string input)
    static bool isIPAddress(string input)

    // Validation helpers
    static bool hasNumbers(string input)
    static bool hasLetters(string input)
    static bool hasSpecialChars(string input)
    static bool isAlphanumeric(string input)

    // Extraction
    static List<string> extractEmails(string text)
    static List<string> extractURLs(string text)
    static List<string> extractPhones(string text)
    static List<string> extractNumbers(string text)
```

---

### Examples

**Example 1: Email Validation**
```fusion
import fusionlib.Regex

// Traditional regex (hard to read)
string emailRegex = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

// Fluent API (readable)
Regex emailPattern = Regex.create()
    .regexStartWith()
    .regexFilterCharacters("a-zA-Z0-9._%+-").regexOneOrMore()
    .regexLiteral("@")
    .regexFilterCharacters("a-zA-Z0-9.-").regexOneOrMore()
    .regexLiteral(".")
    .regexRange('a', 'z').regexRepeat(2, null)
    .regexEndWith()

bool isValid = emailPattern.matches("user@example.com")

// Or use helper
bool isValid2 = RegexHelper.isEmail("user@example.com")
```

**Example 2: Phone Number Extraction**
```fusion
import fusionlib.Regex

string text = "Call me at 555-1234 or 555-5678"

// Fluent API
Regex phonePattern = Regex.create()
    .regexFilterNumbers().regexRepeat(3, 3)
    .regexLiteral("-")
    .regexFilterNumbers().regexRepeat(4, 4)

List<string> phones = phonePattern.findAll(text)
// Result: ["555-1234", "555-5678"]

// Or use helper
List<string> phones2 = RegexHelper.extractPhones(text)
```

**Example 3: Replace with Validation**
```fusion
import fusionlib.Regex

string html = "<p>Hello</p><div>World</div>"

// Remove HTML tags
Regex tagPattern = Regex.create()
    .regexLiteral("<")
    .regexFilterCharacters("a-zA-Z/").regexOneOrMore()
    .regexLiteral(">")

string plainText = tagPattern.replace(html, "")
// Result: "HelloWorld"
```

**Example 4: Password Strength**
```fusion
import fusionlib.Regex

bool function isStrongPassword(string password)
    // Must have: 8+ chars, uppercase, lowercase, digit, special char
    bool hasLength = password.length >= 8
    bool hasUpper = RegexHelper.hasPattern(password, "[A-Z]")
    bool hasLower = RegexHelper.hasPattern(password, "[a-z]")
    bool hasDigit = RegexHelper.hasNumbers(password)
    bool hasSpecial = RegexHelper.hasSpecialChars(password)

    return hasLength and hasUpper and hasLower and hasDigit and hasSpecial
```

---

### Implementation Notes

**Key Design Decisions:**
1. **Chainable builder** (Option 1) for complex patterns
2. **Static helpers** (Option 2) for common use cases
3. **Hybrid approach** - provide both for flexibility
4. **Interoperability** - can convert to/from traditional regex strings
5. **Performance** - compiles to traditional regex internally (no performance loss)

**Compatibility:**
- Fluent API wraps traditional regex engine
- Can use `toPattern()` to get traditional regex string
- Can construct from traditional regex: `Regex.fromPattern("^\d+$")`

**Documentation:**
- All methods have clear descriptions
- Examples for common use cases
- Migration guide from traditional regex
- Performance considerations

---

### Open Questions

1. **Module placement:** Core module or separate Regex module?
   - **Recommendation:** Start in Core, move to separate module if it grows large

2. **Replace traditional regex literals?**
   - **Recommendation:** No - supplement, don't replace. Traditional regex still supported.

3. **Case-insensitive matching?**
   - **Recommendation:** Add `.regexCaseInsensitive()` flag method

4. **Unicode support?**
   - **Recommendation:** Add `.regexUnicode()` flag method

5. **Named capture groups?**
   - **Recommendation:** Add `.regexNamedGroup(string name, Regex pattern)`

---


## Regex Module (Planned)

**Status:** Proposed
**Module:** `Fusion.Regex`
**Purpose:** Provide full regular-expression capabilities without bloating the Core module.

**Features:**

* Traditional regex engine
* Optional Fluent/Builder API
* Pattern validation
* Find/replace helpers
* Extraction utilities

**Reason:** Regex systems grow large and should stay modular.

[< 030 LibraryLayout](030-LibraryLayout.md) | [Index](index.md) | [032 DomainPackages >](032-DomainPackages.md) <!-- nav -->
