[< 020 SemanticContract](020-SemanticContract.md) | [Index](index.md) <!-- nav -->

# 030 Types

## Data Types and Variables

**Status:** [PARTLY] int, float, double, bool, char, string, byte / bytes, const and fixed-size arrays are built (01-04, 08, 09, 18.3); every array index is checked - outside the array is an IndexError (27.1); strings can be changed in place, `s[i] = c`, and a const string is fixed (29.1-29.2); nullability [PLANNED 30 - designed 2026-10-27, `files/Nullable_Values.md`]; type-inferred const, `long` and other sized types: no task yet

Description: Type system combining static typing with clear null safety rules.

---

### Type Categories

Description: Fusion distinguishes between value types and reference types for null safety.
Full design: `files/Nullable_Values.md` (user decisions 2026-10-27, Task 30 - planned).

* **Value Types**: Cannot be null, always have a value
     * Primitives: byte, ubyte, short, ushort, int, uint, long, ulong
     * Floating point: float, double, decimal
     * Boolean: bool
     * Character: char
     * Structs: All value-type structs (a struct is never null - user, 2026-10-24)
     * **Strings, arrays, `List` and `Map`**: values with methods - never null, empty when not
       set (`""`, `[]`, no keys); an empty one has length 0. A project can allow null type
       by type: `[strings]` / `[arrays]` / `[lists]` / `[maps]` `nullable = true` (default
       false)
     * Note: Syntax like `int?` / `string?` does NOT exist - `?` is used on a variable
       (`x?.method()`), never in a type

* **Reference Types**: Can be null, must be checked or guarded before use
     * Objects: All class instances (Task 32)

---

### Complete Type Specifications

Description: All built-in types with their properties and capabilities. How values are
written in the source - hex, binary, octal, digit separators, durations, money, ... - is a
proposal in `files/Literals.md` (not designed yet).

Type | Default | Min | Max | Autobox Class | Safe Cast To
---|---|---|---|---|---
byte | 0 (0x00) | 0 | 255 | Byte | short, int, long, float, double
sbyte | 0 | -128 | 127 | SByte | short, int, long, float, double
bytes | empty | - | - | - | - (raw byte array, see "Raw bytes")
short | 0 | -32,768 | 32,767 | Short | int, long, float, double
ushort | 0 | 0 | 65,535 | UShort | uint, ulong, float, double
int | 0 | -2,147,483,648 | 2,147,483,647 | Int | long, float, double
uint | 0 | 0 | 4,294,967,295 | UInt | ulong, float, double
long | 0 | -9,223,372,036,854,775,808 | 9,223,372,036,854,775,807 | Long | float, double
ulong | 0 | 0 | 18,446,744,073,709,551,615 | ULong | float, double
float | 0.0f | ±1.5 x 10^-45 | ±3.4 x 10^38 | Float | double
double | 0.0 | ±5.0 x 10^-324 | ±1.7 x 10^308 | Double | decimal
decimal | 0.0 | ±1.0 x 10^-28 | ±7.9 x 10^28 | Decimal | (highest precision)
bool | false | false | true | Boolean | int (0 or 1)
char | '\0' | U+0000 | U+10FFFF | Char | int, string
string | "" | (empty) | (memory limit) | String | (no casting from)
money | 0 | (to be designed) | (to be designed) | Money | written out only (see below)
array `T[]` | `[]` (empty, length 0) | - | - | - | -
`List<T>` | empty (length 0) | - | - | - | -
`Map<K, V>` | empty (no keys) | - | - | - | -

* **money** (planned - user, 2026-10-27; design notes in `files/Literals.md` "Money"): a
  strict decimal type for currency only, like COBOL - exact digits, nothing lost by a
  conversion. Default 0. Conversions to and from `decimal`, `float` and `int` are always
  written out; to `int` it rounds half away from zero by default (19.5 -> 20, -19.5 -> -20),
  other rounding modes chosen from an enum
* **Strings, arrays, lists and maps** are objects with methods but are treated as value
  types (user, 2026-10-27): never null, empty when declared without a value, length 0 (see
  "Null Handling")

```
int[] numbers          // [] - an empty array, length 0 (both forms - planned, Task 30.10;
int numbers[]          //      today int[] needs a size or a list of values)
List<string> shoppingList   // empty list, length 0
Map<string, int> ages       // empty map
byte b                 // 0x00
money total            // 0 (planned)
```

---

### Nullability Rules

Description: Which types can be null and how to check them.

Type Category | Can Be Null? | Check Method | Example
---|---|---|---
Value Types | NO | N/A (always has value) | `int x` is never null
Structs | NO | N/A (always has value) | `Vector3 v` is never null
String, array, List, Map | NO by default (a `nullable` setting allows it) | `s.length() == 0` for empty | `string s` is `""`
Objects | YES | `obj == null`, `obj === null`, `obj is null`, `obj?.null` (quick typing); `!obj?.null` = not null | `if ship?.null` then handle

Using a possibly-null object: `obj?.method()` is a guard - on null the method is not run and
nothing errors (in an `if`, the condition is false); `obj?.method() ?? fallback` gives a
default; plain `obj.method()` on null is a NullError. Truth tables and when to use `?.`:
`files/Nullable_Values.md`.

---

### Variable Declarations

Description: Multiple declaration styles for different scenarios.

* **Type-First Declaration**: No ambiguity
     * Format: `<type> varName = value`
     * Use when: Type clarity important
     * Example: `int count = 10`

```
int count = 10
string name = "Starship"
float speed = 299792.458
Spaceship ship = Spaceship("Enterprise", 100.0)
```

* **Type Inference (Task 46.1, built)**: the type comes from the value
     * `let name = value` - set once, never changes. On a struct, string, List or array it
       is const and read only: nothing inside can change either (a compile error)
     * `var name = value` - can change; its type can't
     * Without a value (`let total`, `var later`) the first value gives the type. On every
       path it must be set before it is read, and a `let` exactly once - not twice, and not
       inside a loop it was declared outside of
     * `const` stays: a value fixed where it is written; a `let` may be set later, while running
     * Parameters: `function f(let int a, var int b)` - `let` can't change inside the function,
       `var` can (the default). The type is written; one taken from each caller is generics
       (Task 33)
     * A value with no type of its own can't give one: `let x = null`, `let xs = []` - write
       the type instead
     * A module-level `let` / `var` needs its value where it is declared; a module-level
       `let` is allowed like a constant (`[modules] variables` doesn't apply)
     * `let`, `var` (and `service`, for Task 42) are reserved words

```
let name = "Starship"
var speed = 299792.458
let position = Vector3(10, 20, 30)
let total                    // set once below, on every path
if big
    total = 100
else
    total = 1
```

* **Declaration Without Initial Value**: Uses default
     * Format: `<type> varName`
     * Uses default value from table above
     * Example: `int count` defaults to 0

```
int count          // 0
string name        // ""
bool flag          // false
float speed        // 0.0f
Spaceship ship     // null (a class object - reference type)
int[] scores       // [] - arrays, lists and maps are never null by default
```

---

### Constants

Description: Immutable values, must be initialized at declaration; reassignment is a
compile-time error.

```
const int MAX_ITERATIONS = 1000
const float PI = 3.14159265359
const string GAME_VERSION = "1.0.0"
```

**Implemented (MVP, Task 8):** local const declarations inside a function body, with an
explicit type, as shown above - matching `variable_declaration` in fusion.ebnf. Fusion uses
block-level (lexical) scoping (Task 12.6), so a const declared inside an `if`/`while`/`for`
block is only visible inside that block, and is never visible outside the function it's
declared in.

**Constant strings are `const` strings** (once called fixed strings; `fixed(n)` now means a maximum size - Task 47.5) (Task 29.2, user decision 2026-10-27 - no separate
fixed type or `f"..."` prefix): a `const string` never changes - neither replaced nor
edited in place (`s[i] = c` is a compile error), and the same holds for a string inside a
const struct or array. Fixed-ness belongs to the variable, not the text: a copy of a const
string (`string copy = GREETING`) is an ordinary string and can be changed.

**Module-level variables and constants** (Task 44.1, implemented): declared outside any
function - `const int LIMIT = 3`, `int count = 0`, `public string version = "1.0"`.
* Set in the order written, before `main`'s own code. An initializer may use the functions
  and the module variables above it (a function that reads a later one sees it still unset)
* Every function of the module sees them; `public` ones are used from other modules as
  `stats.total`, and `--interface` lists them
* A variable, parameter or loop variable inside a function can't have a module variable's
  name - which one is meant would be easy to misread
* Strings, lists, maps and structs held in them are freed when the program ends
* A module-level array needs a list of values (`int[] primes = [2, 3, 5]`)
* `fusion.toml` `[modules] variables = false` turns module variables off; constants are
  always allowed (user decision 2026-10-26)
* Shared between threads, a module variable is what `service` is for (Task 42)

**Not yet implemented:** type-inferred const (`const GAME_VERSION = "1.0.0"` without a type
name), and class-level constants (`public const MAX_SPEED: float = 1000.0`, shown later in
this document under "Classes and Objects").

[< 020 SemanticContract](020-SemanticContract.md) | [Index](index.md) <!-- nav -->
