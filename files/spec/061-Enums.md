[< 060 Structs](060-Structs.md) | [Index](index.md) | [070 ControlFlow >](070-ControlFlow.md) <!-- nav -->

# 061 Enums

Contents: [Enum Syntax](#enum-syntax) | [Enum with Values](#enum-with-values) | [Using Enums](#using-enums) | [Enum Properties](#enum-properties)

## Enumerations

**Status:** [DONE 25]
- Plain enums (25.2), `match` (25.3), enums with data (25.4) and enums that hold themselves (25.5)
- The properties / next() / fromValue below stay design

**Enums that hold themselves (Task 25.5):**
- A value's data may be the enum itself - `Add(Expr left, Expr right)` - or a List of it -
  `Call(string name, List<Expr> args)`
- That is what an expression tree or a compiler's syntax tree needs
- Such a field is stored on the heap but is still a value:
  - a copy is a deep copy
  - `==` compares the whole tree
  - everything is freed automatically
- One rule: a value can't hold itself through other types (enum A holds struct S holds A) - hold it in a List instead
- (The first value may hold the enum too since Task 30.11 - an unset variable is null, not the first value)

Example program using all of it (Task 25.6): `examples/expressions/`
- a `Token` enum with data
- a tokenizer using `match` on chars
- a parser building an `Expr` tree (`Binary(char op, Expr left, Expr right)`)
- an evaluator matching on it

**Enums with data as built (Task 25.4, user decisions 2026-10-12):**
- A value may carry fields - `Number(int value)`, `Pair(string a, int b)`
  - any type a struct field can have except a fixed array (use a List), with no defaults
- Made with `Token.Number(42)` or named arguments `Token.Pair(b = 7, a = "k")`
- A value without data is still `Token.Plus`
- The data is read **only** through `match`: `case Number(n)` gives `n` a copy of the field
  - `_` skips one
  - a case listing several values can't name data
- A value is a value: copied deeply, freed automatically, `==` compares the value and its data
- Printing and `toString` give the value's name only; `toInt` its number
- `values()` / `fromString` and use as a Map key are for enums without data
- A variable given no value is null (Task 30.11)
- In C it is a struct: a `tag` and every value's fields

**Enums can be null (Task 30.11, built - user decisions 2026-10-27/28):**
- An enum is treated as a reference type, like a class
- `Status s` with no value - a variable, a struct field, an array element - is **null**, not the first value (`OK`)
- It never silently means a value nobody chose
* Tests: `s == null`, `s != null`, `s === null`, `s is null`, `s is not null`, `s?.null`
  (quick typing for "is null"), `!s?.null`; `s = null`; `s == Status.OK` is simply false
* Printing and `toString` give `null`; `toInt` on null is a **NullError** (it has no number)
* `match`: null equals no case value - it goes to `else`. A match that covers every value but
  has no `else` raises a NullError on null (`case null` - Task 30.12)
* In C null is the number -2147483647 (`FUSION_ENUM_NULL`) - an enum value can't use it
* Not yet: `s?.toString() ?? "unset"` (the general null guard, Task 30.2)

**`match` as built (Task 25.3, user decisions 2026-10-12):**
- `match value` then `case` lines - indented, in braces, or closed by `End match`
- A case lists one or more values (`case Red, Yellow`) and has a block, or one statement after `:`
- `else` catches the rest
- On an enum:
  - the cases name values bare (`case Red`, never `case Color.Red`)
  - every value must be covered unless there is an `else` - the error names the missing ones
  - an `else` after every value is a warning
- On an int, byte, char or string the cases are constants and an `else` is required
- A value handled twice is an error
- Exactly one case runs - no fall-through
- `break` inside a case ends the match (as in a switch); `continue` acts on the loop around it
  (Task 30.12, user 2026-10-28 - before, `break` left the loop)
- A match whose every case returns (and that covers everything) ends a function

**`fall match` (Task 30.13, built - user 2026-10-28):** falls through, like a C / Java / C# `switch`
- The matching case runs, then each case below it, until a `break`
- The `else` runs when nothing matched, and is fallen into too
- A case can't read a value's data (it may be reached from the case above)
- `fall` is a word only right before `match`

```
fall match level
    case High: out = out + "H"      // High: H, then M, then L
    case Mid: out = out + "M"
    case Low
        out = out + "L"
        break                       // stop falling
```

**`case null` (Task 30.12, built):**
- At most one per match, on any value - a library or module may hand over a null, and strings may be
  nullable by a setting
- A null equals no case value: it goes to `case null`, else to `else`
- A match on an enum that covers every value with no `else` and no `case null` raises a NullError on null
- `case OK, null` shares a case like any values

**As built (Task 25.2, user decisions 2026-10-12):**
* `enum` (or `Enum`) at top level, `public enum` for other modules. Forms: one line after
  `:`, an indented block (optionally closed by `End enum`), or braces. Commas are optional
* A value's number is written (`OK = 200`, `Low = -1`) or the previous one + 1, from 0. Two
  values can't share a name or a number; `values` / `fromString` can't be value names
* A value is always written `Color.Red` (bare names only in `match` cases - Task 25.3)
* In C an enum is an int; a variable, field or array element given no value starts at the
  enum's **first** value (since Task 30.11: null - see "Enums can be null")
* `==` / `!=` / `===` only between values of the same enum - never with a number (use
  `toInt()`); no arithmetic
* Printing (`print`, `{c}`, `format`) and `toString` give the name; `toInt` the number;
  `Color.values()` a `List<Color>` in declaration order; `Color.fromString("Red")` the value
  - an unknown name stops the program with a clear error until error handling (Task 26)
* An enum works as a variable, parameter, return value, struct field, array / List element
  and Map key; a variable can't have an enum's name
* Not built (stay design below): `.name` / `.value` / `.ordinal` properties (use the
  methods), `next()` / `previous()`, `fromValue`

Description: Named constant values for type-safe selections.

---

### Enum Syntax

user added comment: commas can be droped regardless of preference as its redunannt
Description: Three syntax options based on user preference and context.

* **Option 1: Braces** (C/Java style)

```
Enum Planets {
    MERCURY,
    VENUS,
    EARTH,
    MARS,
    JUPITER,
    SATURN,
    URANUS,
    NEPTUNE
}
```

* **Option 2: Indentation** (Python style)

```
Enum Planets
    MERCURY
    VENUS
    EARTH
    MARS
    JUPITER
    SATURN
    URANUS
    NEPTUNE
```

* **Option 3: Single-Line** (Compact)

```
Enum Planets: MERCURY, VENUS, EARTH, MARS, JUPITER, SATURN, URANUS, NEPTUNE
```

**Usage Guidelines**:
* Single-line: For simple lists (< 10 items or < 80 characters)
* Indentation or braces: For longer lists or when items have values

---

### Enum with Values

Description: Custom integer values for enum constants.

```
// With braces
Enum StatusCode {
    OK = 200,
    CREATED = 201,
    BAD_REQUEST = 400,
    NOT_FOUND = 404,
    SERVER_ERROR = 500
}

// With indentation
Enum StatusCode
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    SERVER_ERROR = 500

// Default values (0, 1, 2, ...)
Enum Priority {
    LOW,      // 0
    MEDIUM,   // 1
    HIGH,     // 2
    CRITICAL  // 3
}
```

---

### Using Enums

Description: Type-safe constant selection.

```
// Declaration
Planets planet = Planets.MARS
StatusCode status = StatusCode.OK

// Comparison
if status == StatusCode.OK
    print("Success!")

if planet == Planets.EARTH
    print("Home planet")

// Match statement - as built (Task 25.3): bare value names, no ':' needed before a block
match status
    case OK
        print("Request successful")
    case NOT_FOUND
        print("Resource not found")
    else: print("Something else")

// Get integer value
int code = status.toInt()  // 200

// Iteration
for planet in Planets.values()
    print(planet.toString())
end loop
```

---

### Enum Properties

Description: Built-in methods and properties.

```
Enum Direction: NORTH, SOUTH, EAST, WEST

Direction dir = Direction.NORTH

// Properties
string name = dir.name          // "NORTH"
int value = dir.value           // 0
int ordinal = dir.ordinal       // 0 (position in enum)

// Methods
string str = dir.toString()     // "NORTH"
Direction next = dir.next()     // SOUTH
Direction prev = dir.previous() // WEST (wraps around)

// Static methods
List<Direction> all = Direction.values()
Direction d = Direction.fromString("NORTH")
Direction d2 = Direction.fromValue(0)
```

[< 060 Structs](060-Structs.md) | [Index](index.md) | [070 ControlFlow >](070-ControlFlow.md) <!-- nav -->
