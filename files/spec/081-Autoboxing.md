[< 080 Null](080-Null.md) | [Index](index.md) | [090 Memory >](090-Memory.md) <!-- nav -->

# 081 Autoboxing

## Autoboxing

**Status:** [PARTLY] the built-in type classes (String, Int, ...) and method syntax on built-in values are built (18.3.7); autoboxing itself: no task yet

**Any function as a method** (Task 44.2, user decision 2026-10-26, implemented):
- `x.f(a)` is `f(x, a)` when the program has a function `f` whose first parameter takes `x` - a struct, a
  built-in value, a list, an enum
- List / Map methods and an enum's `toString` / `toInt` come first
- The program's own function replaces a library one of the same name, as a plain call does
- The function gets a copy (structs are values): `p = p.moved(1, 2)`
- Passing will follow VB.NET once classes exist: value types by value, objects by reference
- Functions inside a struct: a `fusion.toml` option, off by default (32.1 - since built, `[structs] functions`)

Description: Automatic primitive-to-object conversion for method calls.

---

### How It Works

* Primitives automatically become objects when calling methods
* Compiler handles conversion transparently
* No manual boxing required
* Performance optimized

---

### Using Autoboxing

Description: Call methods on primitives seamlessly.

* **Number Methods**

```
int num = 42
string str = num.toString()           // "42"
string hex = num.toHexString()        // "2A"
string binary = num.toBinaryString()  // "101010"

float pi = 3.14159
float rounded = pi.round(2)           // 3.14
int truncated = pi.floor()            // 3
```

* **String Methods**

```
string text = "hello world"
string upper = text.toUpper()         // "HELLO WORLD"
string sub = text.substring(0, 5)     // "hello"
int length = text.length              // 11
bool contains = text.contains("world") // true
```

* **Array Methods**

```
int[] numbers = [1, 2, 3, 4, 5]
int len = numbers.length              // 5
int sum = numbers.sum()               // 15
int max = numbers.max()               // 5
int[] doubled = numbers.map(lambda x: x * 2)
```

* **Arrays and null:** an array is never null, whatever the settings (D.138), so `numbers.length`
  is always safe - 0 for an empty array; see [080 Null](080-Null.md)

---

### Autobox Classes

Description: Each primitive type has corresponding object class.

Primitive | Autobox Class | Example Methods
---|---|---
int | Int | toString(), toHexString(), abs()
uint | UInt | toString(), toHexString()
long | Long | toString(), abs()
float | Float | toString(), round(), floor(), ceil()
double | Double | toString(), round(), floor(), ceil()
bool | Boolean | toString(), not()
char | Char | toString(), toUpper(), toLower(), isDigit()
byte | Byte | toString(), toHexString()

[< 080 Null](080-Null.md) | [Index](index.md) | [090 Memory >](090-Memory.md) <!-- nav -->
