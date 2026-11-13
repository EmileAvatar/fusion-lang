[< 071 NamingExceptions](071-NamingExceptions.md) | [Index](index.md) | [081 Strings >](081-Strings.md) <!-- nav -->

# 080 Arrays

**Status:** idea - multi-dimensional arrays postponed (COL.015); arrays that grow: FEATURES Task 45; built today: [031 Arrays](../spec/031-Arrays.md)

## Type System Enhancements

### Advanced Array Declaration Syntax

> **Replaced (2026-10-31, Decisions.md D.064):** read-only is `const`, a size limit is
> `fixed(n)` - `type()` / `type(N)` are not used.

**Status:** 📝 Proposed
**Purpose:** Provide fine-grained control over array mutability and resizing

**What:** Extended array syntax using `[]` vs `()` to control element mutability and array resizing behavior.

#### Array Syntax Overview

| Syntax | Size | Elements | Use Case |
|--------|------|----------|----------|
| `type[]` | Flexible (can grow/shrink) | Mutable (can edit) | General-purpose dynamic arrays |
| `type[N]` | Fixed (cannot resize) | Mutable (can edit) | Fixed-size buffers, C-style arrays |
| `type()` | Flexible (can grow) | Immutable (read-only) | Append-only collections |
| `type(N)` | Fixed (cannot resize) | Immutable (read-only) | Constant lookup tables |

#### Detailed Examples

##### 1. Flexible Mutable Arrays `type[]`

Can grow/shrink, elements can be changed.

```fusion
string cars[] = ['Volvo', 'BMW', 'Toyota']

// Modify elements
cars[0] = 'Mercedes'  // OK

// Resize array
cars.add('Audi')      // OK - now 4 elements
cars.remove('BMW')    // OK - now 3 elements
cars.clear()          // OK - now 0 elements
```

##### 2. Fixed Mutable Arrays `type[N]`

Cannot resize, but elements can be changed.

```fusion
string cars[3] = ['Volvo', 'BMW', 'Toyota']

// Modify elements
cars[0] = 'Mercedes'  // OK

// Resize attempts fail
cars.add('Audi')      // ❌ Compile error: Cannot resize fixed array
cars.remove('BMW')    // ❌ Compile error: Cannot resize fixed array
```

🧩 **Use case:** C-style arrays, hardware buffers
```fusion
byte buffer[256] = [0, 0, 0, ...]  // Fixed 256-byte buffer
buffer[10] = 0xFF  // OK - modify element
```

##### 3. Flexible Immutable Arrays `type()`

Can grow (append-only), elements cannot be changed.

```fusion
string cars() = ('Volvo', 'BMW', 'Toyota')

// Modify elements fails
cars[0] = 'Mercedes'  // ❌ Compile error: Cannot modify immutable element

// Can append (grows)
cars.add('Audi')      // OK - now 4 elements

// Cannot remove
cars.remove('BMW')    // ❌ Compile error: Cannot remove from immutable array
```

🧩 **Use case:** Append-only logs, event streams
```fusion
string logMessages() = ()
logMessages.add("Application started")
logMessages.add("User logged in")
// Old logs cannot be modified or deleted
```

##### 4. Fixed Immutable Arrays `type(N)`

Cannot resize, elements cannot be changed.

```fusion
string cars(3) = ('Volvo', 'BMW', 'Toyota')

// Modify elements fails
cars[0] = 'Mercedes'  // ❌ Compile error: Cannot modify immutable element

// Resize fails
cars.add('Audi')      // ❌ Compile error: Cannot resize fixed array
```

🧩 **Use case:** Constants, lookup tables
```fusion
string dayNames(7) = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
int primes(10) = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)

// Read-only access
print(dayNames[0])  // OK: "Mon"
```

#### Syntax Disambiguation

**`()` on types vs function calls:**

```fusion
// Array declaration (type followed by ())
string names() = ('Alice', 'Bob')
int values(5) = (1, 2, 3, 4, 5)

// Function call (variable/function name followed by ())
void function greet()
    print("Hello")

greet()  // Function call - OK

// No ambiguity
string arr() = ()     // Empty immutable array
myFunction()          // Function call
```

**Rule:** If `()` follows a **type name** → array declaration. If `()` follows a **variable/function name** → function call.

#### Array Syntax API

```fusion
// Common operations on all array types

// Read access (all types)
string item = cars[0]

// Write access (only mutable: [], [N])
cars[0] = 'Mercedes'  // OK for [], [N]; Error for (), (N)

// Add (only flexible: [], ())
cars.add('Audi')      // OK for [], (); Error for [N], (N)

// Remove (only flexible mutable: [])
cars.remove('BMW')    // OK for []; Error for [N], (), (N)

// Size
int count = cars.length  // All types

// Iterate (all types)
for car in cars
    print(car)
```

#### Type Safety Examples

```fusion
// Compile-time enforcement
string mutable[] = ['A', 'B', 'C']
string immutable() = ('X', 'Y', 'Z')

mutable[0] = 'D'     // OK
immutable[0] = 'E'   // ❌ Compile error

void function processArray(string items[])
    items.add('new')  // OK - expects flexible mutable

processArray(mutable)    // OK
processArray(immutable)  // ❌ Type error: Cannot pass immutable() as mutable[]
```

[< 071 NamingExceptions](071-NamingExceptions.md) | [Index](index.md) | [081 Strings >](081-Strings.md) <!-- nav -->
