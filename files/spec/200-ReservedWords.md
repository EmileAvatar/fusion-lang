[< 191 Interop](191-Interop.md) | [Index](index.md) | [210 FeaturesSummary >](210-FeaturesSummary.md) <!-- nav -->

# 200 Reserved Words

**Contents**

- [Reserved Keywords](#reserved-keywords)
- [Operators](#operators)
- [Operator Precedence](#operator-precedence)

## Reserved Words and Operators

**Status:** [PARTLY] every operator listed is built except where its section says otherwise; several reserved keywords belong to planned features (match: 25, class / interface: 32)

Description: Complete list of language keywords and operators.

---

### Reserved Keywords

Description: Words that cannot be used as identifiers.

**Reserved today** - the compiler's list (src/lexer/keywords.py, 68 words - `Unique` released 2026-11-14, 48.8):

`abstract`, `and`, `async`, `await`, `bool`, `break`, `byte`, `case`, `cast`, `catch`, `char`, `class`, `const`, `continue`, `double`, `else`, `End`, `enum`, `Enum`, `false`, `finally`, `float`, `for`, `func`, `function`, `get`, `go`, `if`, `implements`, `import`, `in`, `inherits`, `int`, `interface`, `internal`, `is`, `let`, `long`, `loop`, `match`, `namespace`, `new`, `not`, `null`, `or`, `override`, `private`, `property`, `protected`, `public`, `return`, `sealed`, `service`, `set`, `Shared`, `short`, `static`, `string`, `struct`, `this`, `throw`, `true`, `try`, `var`, `virtual`, `void`, `Weak`, `while`

- **`end` is not reserved** (Task 44.5): `End` closes a block; a lowercase `end` does only right before
  a block word (`end function`, `end if`, ...) and is an ordinary name everywhere else
- `let`, `var` and `service` are reserved (Task 46, 2026-10-29)
- In `match`, `_` skips a value: `case Rect(w, _)`
- A name after `.` may be a reserved word (`m.get`, `x.set`) - there it can only be a field or method
- To reserve when their features are built: `check` (56.3), `unsafe` (42.40)

**The earlier design list** (below) - words in it that the compiler doesn't reserve: `elif`, `do`,
`lambda` (today `func`), `module` / `export` (replaced - [150 Modules](150-Modules.md)), `where`,
`thread`, `channel`, `goroutine` (today `go`), `lock` / `unlock`, `none`, `super`, `goto`, `unsafe`,
`allocate` / `deallocate`, `constructor`; `#[attribute]` (Fusion has no attributes - 56.1)

**Control Flow**:
* `if`, `elif`, `else`
* `match`, `case`
* `for`, `while`, `do`
* `break`, `continue`
* `return`
* `end` (end loop, end function, etc.)

**Type Declarations**:
* `class`, `struct`, `interface`, `enum`
* `property`
* `var`, `const`
* `static`

**Access Modifiers**:
* `public`, `private`, `protected`, `internal`

**Memory & Pointers**:
* `unsafe`
* `allocate`, `deallocate`
* `Shared`, `Weak`

**Functions & Methods**:
* `function`
* `constructor`
* `lambda`
* `async`, `await`

**Modules**:
* `module`
* `import`, `export`

**Operators & Logic**:
* `and`, `or`, `not`
* `is`, `in`
* `where`

**Threading & Concurrency**:
* `thread`, `channel`
* `goroutine`
* `lock`, `unlock`
* `try` (try-with-resources)

**Error Handling**:
* `try`, `catch`, `finally`
* `throw`, `Error`

**Literals**:
* `true`, `false`
* `null`, `none`

**Special**:
* `this`, `super`
* `goto` (reserved but not used, except in unsafe embedded mode)

**Annotations & Directives**:
* `#Region`, `#End Region`
* `#[attribute]` (for annotations like `#[no_loop_protection]`)

---

### Operators

Description: Symbols used for operations.

---

#### Arithmetic Operators

Operator | Description | Example
---|---|---
`+` | Addition | `a + b`
`-` | Subtraction | `a - b`
`*` | Multiplication | `a * b`
`/` | Division | `a / b`
`%` | Modulo | `a % b`
`**` | Exponentiation | `a ** 2` (a squared)

---

#### Comparison Operators

Operator | Description | Example
---|---|---
`==` | Equal value | `a == b`
`!=` | Not `==` | `a != b`
`===` | Same type and equal value | `a === b`
`!==` | Not `===` | `a !== b`
`=` | Inside an `if` / `while` / `else if` condition: the same as `==` | `if a = b`
`<>` | Not equal to (alternative) | `a <> b`

**Equality rules (Task 18.3.5, user decisions 2026-10-07):**

* `=` assigns as a statement, but compares inside an `if`, `while` or `else if` condition
  (VB-style readability): `if x = 2` is `if x == 2`. Named arguments still win:
  `if f(x = 2)` passes `x`
* `==` compares values. Across types it uses a small fixed table, and nothing else:
  * a number equals text holding that number - `2 == "2"`, `2.5 == "2.5"`, `2 == "2.0"`;
    text that isn't a number is simply unequal (`2 == "two"` is false, no error)
  * a char equals a one-character string - `'a' == "a"`
  * int, float and double compare by value - `2 == 2.0`
  * never "truthiness": a bool only equals a bool. Any other mixed pair (bool and int,
    char and int, a struct and a number, ...) is a compile error
* `===` also requires the same type: `2 === 2.0` and `2 === "2"` are false. On two
  different types the answer is known when compiling, so the compiler warns that it is
  always false (both sides still run)
* `!=` is "not `==`" and `!==` is "not `===`", as in JavaScript
* A `bool` prints as `true` / `false` - in `print`, `{...}` interpolation and `format()` -
  while as a value it stays 1 / 0 in the generated C (Task 18.3.5b)
* Structs compare field by field with the same rules; two different struct types compare
  with `==` when they have the same field names in the same order (`===` needs the same
  struct). Arrays compare element by element and must have the same length
* Every comparison is generated per type - C's raw `==` is used only on plain numbers,
  chars and bools, never on strings, structs or arrays
`<` | Less than | `a < b`
`>` | Greater than | `a > b`
`<=` | Less than or equal to | `a <= b`
`>=` | Greater than or equal to | `a >= b`

---

#### Logical Operators

Operator | Description | Example
---|---|---
`and` | Logical AND | `a and b`
`or` | Logical OR | `a or b`
`not` | Logical NOT | `not a`
`&&` | Alternative AND | `a && b`
`||` | Alternative OR | `a || b`
`!` | Alternative NOT | `!a`

---

#### Bitwise Operators

Operator | Description | Example
---|---|---
`&` | Bitwise AND | `a & b`
`|` | Bitwise OR | `a | b`
`^` | Bitwise XOR | `a ^ b`
`~` | Bitwise NOT | `~a`
`<<` | Left shift | `a << 2`
`>>` | Right shift | `a >> 2`

---

#### Assignment Operators

Operator | Description | Example
---|---|---
`=` | Assignment | `a = 10`
`+=` | Add and assign | `a += 5`
`-=` | Subtract and assign | `a -= 5`
`*=` | Multiply and assign | `a *= 2`
`/=` | Divide and assign | `a /= 2`
`%=` | Modulo and assign | `a %= 3`

---

#### Special Operators

Operator | Description | Example
---|---|---
`.` | Member access | `object.property`
`?.` | Null guard (Task 30): not run on null, no error | `object?.method()`
`??` | Default when null (Task 30) | `object?.method() ?? default`
`? :` | Conditional operator (Task 30.7, built) | `(count > 5) ? "big" : "small"`
`[]` | Array/index access | `array[0]`
`?[]` | Null-guarded index (only with `[arrays] nullable = true`) | `array?[0]`
`()` | Function call / grouping | `function(args)`
`...` | Spread/variadic/range | `1...10`, `int... args`
`::` | Scope resolution - design, not built (`.` is used: `money.round`) | `Module::Class`
`:` | Lambda/type separator (default) | `int add(int x) : x + 1`
`->` | Lambda/type separator (alternative) - built | `(int) -> string f`

---

### Operator Precedence

Description: Order of operations from highest to lowest priority.

Priority | Operators | Associativity
---|---|---
1 | `()`, `[]`, `.`, `?.` | Left-to-right
2 | `**` | Right-to-left
3 | `~`, `!`, `not`, unary `-`, unary `+` | Right-to-left
4 | `*`, `/`, `%` | Left-to-right
5 | `+`, `-` | Left-to-right
6 | `<<`, `>>` | Left-to-right
7 | `<`, `<=`, `>`, `>=` | Left-to-right
8 | `==`, `!=`, `<>` | Left-to-right
9 | `&` | Left-to-right
10 | `^` | Left-to-right
11 | `|` | Left-to-right
12 | `and`, `&&` | Left-to-right
13 | `or`, `||` | Left-to-right
14 | `??` | Left-to-right
15 | `? :` (conditional) | Right-to-left
16 | `=`, `+=`, `-=`, `*=`, `/=`, `%=` | Right-to-left

**Use parentheses for clarity**: When in doubt, use `()` to make order explicit.

[< 191 Interop](191-Interop.md) | [Index](index.md) | [210 FeaturesSummary >](210-FeaturesSummary.md) <!-- nav -->
