# Structs and built-in value structs

Why Fusion has structs, and what a **built-in value struct** is - a struct the compiler defines and fills itself, so a
complicated thing (an amount of money, a planet with its mass and radius) can be used as one plain value. `money`
and enums are the two built today. For future readers of the language and its code (user, 2026-11-25).

Contents:
- [1. A struct is the ultimate value type](#1-a-struct-is-the-ultimate-value-type)
- [2. A struct or a class](#2-a-struct-or-a-class)
- [3. Built-in value structs](#3-built-in-value-structs)
- [4. money](#4-money)
- [5. Enums](#5-enums)
- [6. The rules every built-in value struct keeps](#6-the-rules-every-built-in-value-struct-keeps)
- [7. How other languages do it](#7-how-other-languages-do-it)
- [8. Where the decisions are](#8-where-the-decisions-are)

---

## 1. A struct is the ultimate value type

A struct bundles several values into **one type that behaves like a value** - as an `int` does:

```fusion
struct Point
    int x
    int y

Point a = Point(1, 2)
Point b = a            // b is its own Point - changing b.x never changes a
```

- It is **never null** - a struct always holds something (STC.001)
- Giving it to another variable gives a whole struct (moved, borrowed or copied - the ownership rules, Task 48); its
  fields are never moved out one at a time (STC.006)
- It may hold strings, Lists, Maps and even an object (STC.001, STC.007) - the struct is still one value
- It has no identity of its own: two Points with the same x and y are the same point

The idea (user, 2026-11-25): **a struct lets you bundle types and objects as if they were one value type.** An `int`
is one number; a `Point` is two numbers that travel together and mean one thing.

## 2. A struct or a class

| | struct | class |
|---|---|---|
| What it is | a value - its data is what it is | an object - a thing with an identity that lives on |
| Null | never | may be null (D.138) |
| Where it lives | where it is declared (the stack, or inside what holds it) | on the heap, owned (Task 48) |
| Given to another variable | the whole value moves / is copied | the object is handed over or shared - one object, two names |
| Methods | off by default (`[structs] functions`, STC.002) | yes |
| Inheritance, interfaces | builds on another struct only (STC.003) - no interfaces (STC.005) | yes |
| Use it for | data: a point, a date, an amount, a record read from a file | behaviour and state: a connection, a game player, a service |

A class can be as complex as it needs. A struct stays simple on purpose: it holds values, and is one.

## 3. Built-in value structs

Some values are complicated inside but should feel as simple as a number. A **built-in value struct** is a struct
that the **compiler** defines, fills and guards:

- the developer uses it as a value - declares it, passes it, prints it, compares it
- the compiler knows its layout, makes its values, does its arithmetic, and checks its rules
- it is **never on the heap and never pooled** - nothing to allocate, nothing to free, no leak possible
- it is **sealed** - no one builds on it

So it has a struct's benefits (several values bundled, a fixed size, copied cheaply, no garbage) and a value's
simplicity (no constructor calls to remember, no null, no lifetime to think about).

## 4. money

`money` (Task 47.2, D.180-D.187) is a 16-byte built-in value struct:

```fusion
money price = money(100.05, "ZAR", "R")
money total = price * 3 + 0.50          // the compiler lines up the scales, checks the currencies
print("{total}")                         // R300.65
```

What the compiler holds for it - never written by the developer:

```text
struct money (16 bytes, sealed)
    long value        8 bytes   10005 - the amount in its smallest steps
    byte scale        1 byte    2     - how many places value holds
    char currency[3]  3 bytes   "ZAR" - empty = no currency
    char symbol[4]    4 bytes   "R"   - for display only
```

- `+ - *` and comparing are done by the compiler; rounding, dividing, splitting and converting by the Currency module
  (D.186)
- the developer reads its parts as fields (`price.currency`, `price.scale`), never sees a constructor, never frees it

## 5. Enums

An enum (Task 47.3, D.188-D.194) is a built-in value struct too: each of its values is one **static const** struct the
compiler makes once. The developer writes:

```fusion
enum Planet
    MERCURY(3.303e23, 2.4397e6, "Mercury")
    EARTH(5.976e24, 6.37814e6, "Earth")
    MARS(6.421e23, 3.3972e6, "Mars")

    public const double mass
    public const double radius
    public const string name

    double function gravity(double kg)
        return 6.67e-11 * mass * kg / (radius * radius)

    string function toString()
        return name

print("{@1}", EARTH.mass)            // no variable needed - EARTH always exists
Planet p = MARS                      // p only borrows MARS - nothing copied, nothing freed
print("{p} {@1}", p.value())         // Mars 2
```

What the compiler makes for each value - never written by the developer:

```text
struct (static const) EARTH
    int id = 1                          counted from 0, or written: 200, OK
    string enumTypeName = "EARTH"       the name as written
    double mass = 5.976e24
    double radius = 6.37814e6
    string name = "Earth"
    string toString() -> name           the enum's own; without one, enumTypeName
    int value() -> id
```

- The values exist for the whole program, in one static table - never on the heap, never pooled; a string field is
  never null
- A variable, parameter, List or Map holding an enum **borrows** it - the value itself is never moved or copied
- Fields are primitive types and string only (no decimal, money, enum, class, interface or array) - the value stays
  small and fixed
- An enum may have methods (whatever `[structs] functions` says) and its own `toString()`; it can't inherit or
  implement an interface (for now)

## 6. The rules every built-in value struct keeps

| Rule | money | enum |
|---|---|---|
| Defined by | the compiler | the developer's fields; the compiler adds id, enumTypeName, toString, value |
| Values made by | the developer, any time (`money(...)`, `123.45`) | the compiler, once, where the enum is declared |
| Changes after it is made | its fields may be set (checked) | never - const |
| Where it lives | where it is declared, copied like an int | one static table; variables borrow |
| Heap, pool | never | never |
| Null | never | an unset enum variable may be null (D.051) - a value itself never is |
| Built on, sealed | sealed | sealed - no inheritance, no interfaces (for now) |

A new built-in value struct (a date, a time span, a coordinate) should keep the same rules: a fixed size, never on the
heap, the compiler doing the work that has rules.

## 7. How other languages do it

| Language | Value structs | Enums with data | Money / decimals |
|---|---|---|---|
| C | `struct` - plain data, copied on assignment; no methods | `enum` is a named int; data kept in a separate array by hand | none built in - libraries, or whole cents in a `long` |
| C++ | `struct` and `class` are the same apart from the default visibility; both can be values (copied) or on the heap | `enum class` is a typed int; data by a lookup table or a class with static instances | none built in - libraries |
| C# | `struct` is a value type (copied, on the stack or inline); `record struct` adds value equality; `class` a reference type | `enum` is a named int (`[Flags]` for combining); no data - an extension method or a lookup | `decimal` - a built-in 128-bit value type (D.182 compares) |
| Java | no user value types yet (Project Valhalla's value classes are coming); `record` is a class with value equality | `enum` is a class: each value a single static object with fields, constructor and methods - the model Fusion follows, but on the heap | `BigDecimal` - a class on the heap |
| Rust | `struct` is a value; `Copy` types copied, others moved (ownership) | `enum` is a tagged union - each value may carry different data (Fusion's enums with data, TYP.004); const data by `impl` methods with `match` | none built in - crates (`rust_decimal`) |
| Swift | `struct` is a value type, copied on write; the standard library's `Int`, `String`, `Array` are all structs | `enum` with raw values (`case earth = 3`) and associated values; methods and computed properties allowed | `Decimal` (Foundation) - a struct |
| Go | `struct` is a value, copied on assignment; a pointer to share | no enum - `const` with `iota` counts ids; data by a map or switch | none built in |
| Kotlin | `data class` (a class with value equality); `value class` wraps one value without a heap object | `enum class` - as Java: fields, constructor, methods per value | `BigDecimal` (from Java) |
| Python | no value types - everything is an object; `dataclass(frozen=True)` acts like one | `Enum` - members are singleton objects; data by a tuple value | `decimal.Decimal` - an object |
| VB.NET | `Structure` is a value type, as C#'s struct | `Enum` is a named int, as C# | `Decimal` - as C# |
| COBOL | records (`01` levels) are fixed-size values | level-88 condition names give values names | `PIC 9(7)V99` - exact fixed-point, the reason COBOL still runs banks (R10) |

What Fusion takes from them:
- the struct as a value (C, C#, Swift, Go) - never null, copied or moved, nothing on the heap unless it holds a List
- an enum value as a single static instance with fields and methods (Java, Kotlin) - but static and const in a
  table, never on the heap
- ids written by the developer (C#'s `OK = 200`, Swift's raw values, Go's `iota` counting on)
- money as a built-in value, exact (COBOL, C#'s decimal) - never a float

## 8. Where the decisions are

- Structs: `Decisions.md` STC.001-STC.008; `files/Classes.md` for classes
- money: TYP.003, D.180-D.187; research `files/Research/Money/Money.md`
- Enums as built-in value structs: TYP.005, D.188-D.194; the plan in `files/taskSummary2.md` (Task 47.3)
