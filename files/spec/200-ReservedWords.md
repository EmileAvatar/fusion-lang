[< 191 Interop](191-Interop.md) | [Index](index.md) | [210 FeaturesSummary >](210-FeaturesSummary.md) <!-- nav -->

# 200 Reserved Words

**Contents**

- [Reserved Keywords](#reserved-keywords)
- [Operators](#operators)
- [Operator Precedence](#operator-precedence)

## Reserved Words and Operators

**Status:** [PARTLY] every operator listed is built except where its section says otherwise; the four word lists are built (Task 61) - the reserved words' features are not

Description: Complete list of language keywords and operators.

---

### Reserved Keywords

Description: Words that cannot be used as identifiers.

Four lists (Task 61, D.162 - user, 2026-11-21). In all of them, a word after `.` is a member name
(`m.get`, `x.type`, `s.default`) - there it can only be a field or method.

**1. Keywords** - the compiler's list (src/lexer/keywords.py `KEYWORDS`, 70 words; the self-hosted lexer
the same):

`abstract`, `and`, `async`, `await`, `bool`, `break`, `byte`, `case`, `cast`, `catch`, `char`, `class`, `const`, `continue`, `double`, `else`, `end`, `End`, `enum`, `Enum`, `false`, `finally`, `fixed`, `float`, `for`, `func`, `function`, `get`, `go`, `if`, `implements`, `import`, `in`, `inherits`, `int`, `interface`, `internal`, `is`, `let`, `long`, `loop`, `match`, `namespace`, `new`, `not`, `null`, `or`, `override`, `private`, `property`, `protected`, `public`, `return`, `sealed`, `service`, `set`, `Shared`, `short`, `static`, `string`, `struct`, `this`, `throw`, `true`, `try`, `var`, `virtual`, `void`, `Weak`, `while`

- `end` and `End` both close a block; `end` is never a name (Task 61, D.162 - Task 44.5 had made it a name)
- `let`, `var` and `service` (Task 46, 2026-10-29); `fixed` (Task 45.14, D.141) - `fixed(n)` on a string,
  List or Map is Task 47.5
- In `match`, `_` skips a value: `case Rect(w, _)`

**2. Reserved for a planned Fusion feature** (keywords.py `RESERVED_WORDS`) - as a name, the error says
what it is kept for: `'check' is reserved for loop safety checks (Task 56) - choose another name`

| Word | Kept for |
|---|---|
| `check` | loop safety checks (Task 56) |
| `unsafe` | unsafe blocks (Task 42.40) |
| `hotpath` | hot-path services (Task 42.23) |
| `extern` | calling C libraries (`extern "C"`) |
| `switch`, `elif` | aliases of `match` and `else if` (D.065, SYN.018) |
| `assert` | SYN.023 |
| `channel`, `lock` | channels in a service, locks inside `unsafe` (Task 42.34, 42.38) |
| `where` | conditions on generic types (Task 33) |
| `defer`, `comptime`, `union`, `choice`, `operator`, `yield` | ideas: clean-up next to the set-up, code run while compiling, an enum with data, operator overloading, generators |

**3. Reserved for future use, from other languages** - as a name, the error says "reserved for future use":
- Likely to be wanted: `module`, `export`, `using`, `default`, `typeof`, `sizeof`, `nameof`, `select`, `atomic`, `transaction`
- Confusing as a name: `goto`, `delete`, `volatile`, `synchronized`, `self`, `base`, `ref`, `out`, `mut`, `move`,
  `macro`, `type`, `record`, `trait`, `impl`

**4. Built, recognised only where they are used** - names everywhere else, not in the lexer: `super`,
`extends`, `byVal`, `byRef`, `readonly`, `foreach`, `typeOf`

**Other languages' code (user, 2026-11-21):** these lists are Fusion's own. A `Lang.<language>.Fusion` module
(Task 49) reads that language with its own keywords, so a Java or Python name such as `type` or `service`
stays readable there; how such a name is written once it becomes Fusion is OpenQuestions Q.039 (deferred
to Task 49).

**The earlier design list** (below) - words in it that are in none of the four lists: `do`,
`lambda` (today `func`), `thread`, `goroutine` (today `go`), `unlock`, `none`, `allocate` /
`deallocate`, `constructor`; `#[attribute]` (Fusion has no attributes - 56.1)

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
* `var`, `const`, `fixed`
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
`?.` | Null guard (built - Task 52.8): not run on null, no error | `object?.method()`
`??` | Default when null (built - Task 52.8) | `object?.method() ?? default`
`? :` | Conditional operator (Task 30.7, built) | `(count > 5) ? "big" : "small"`
`[]` | Array/index access | `array[0]`
`?[]` | Null-guarded index - rejected: an array is never null (D.138) | -
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
