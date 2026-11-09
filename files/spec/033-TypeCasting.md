[< 032 Strings](032-Strings.md) | [Index](index.md) | [040 Functions >](040-Functions.md) <!-- nav -->

# 033 TypeCasting

## Type Casting

**Status:** [PARTLY] an int is used as a float only when it fits exactly (27.2f, `[numbers] autoWidening`); conversions are functions - toInt, toFloat, toString, toByte, parseInt (18.3); cast syntax and sized types: no task yet

Description: Converting between types with safety rules.

* **Implicit Casting**: Widening conversions (safe, no data loss)

```
int x = 10
long y = x              // OK: int to long
float f = x             // OK: int to float
double d = f            // OK: float to double
```

* **Explicit Casting**: Narrowing conversions (may lose data)

```
double d = 3.14159
float f = (float)d           // OK: loses precision
int i = (int)d               // OK: becomes 3 (truncates)

long big = 1000000000000
int small = (int)big         // Runtime error if too big!
```

* **Unsigned/Signed Conversions**

```
uint positive = 100
int signed = (int)positive   // OK: value fits

int negative = -50
uint unsign = (uint)negative // Runtime error: cannot convert negative!
```

* **String Conversions**

```
// To string (always works via autoboxing)
int num = 42
string str = num.toString()        // "42"

// From string (may fail)
string text = "123"
int num = int.parse(text)          // 123

string invalid = "abc"
int result = int.tryParse(invalid) // Returns option type (may be none)
```

[< 032 Strings](032-Strings.md) | [Index](index.md) | [040 Functions >](040-Functions.md) <!-- nav -->
