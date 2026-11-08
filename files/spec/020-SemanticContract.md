[< 010 Philosophy](010-Philosophy.md) | [Index](index.md) <!-- nav -->

# 020 The Semantic Contract

## The Semantic Contract

**Status:** [DONE 27] what every built construct does, in one place - each rule is tested
(tests/test_safety.py and the files named). Where a rule isn't settled yet it says so.

#### Values and copying
* Every value is a **value**: assigning, passing, returning and storing make an independent
  copy - deep for strings, bytes, List, Map, structs, enums with data and Errors, nested ones
  too. Changing a copy never changes the original (a parameter the function changes is its
  own copy; the caller's value stays as it was)
* Values are freed automatically when their block ends - also on `return`, `break`,
  `continue` and when an error passes through. `exit(code)` ends the program at once (the
  operating system takes the memory back)

#### Comparing
* `==` / `!=` compare values: numbers by value across int / float / double / byte, text by
  content, a char with a one-character string, numeric text with a number; structs field by
  field, arrays and lists element by element, maps by keys and values in any order, enum
  values (with their data) only within the same enum, Errors by type, code and message. Any
  other pair is a compile error - a bool only equals a bool (no "truthiness")
* `===` / `!==` also compare the type: on two different types the answer is fixed - a warning
* `=` compares in a condition - `if`, `else if`, `while`, with `and` / `or`, `not`, in
  parentheses. Everywhere else it stores; a second `=` there (`bool same = a = b`) is an
  error that says to write `==`. Inside a call's parentheses `name = value` is a named argument

#### Text
* A string is Unicode (UTF-8): `len(s)` and `s[i]` count characters (code points), `lenb(s)`
  bytes. What a reader sees as one symbol can be several code points (some emoji, accents
  written as two) - grapheme handling is a later feature

#### Numbers
* `int` is 32 bits. `+ - *` and unary `-` that don't fit raise an OverflowError (`[safety]
  mode = "unsafe"` (now `[numbers] overflowWrap = true`, Task 32.0), `unchecked` blocks and `wrapAdd` / `wrapSub` / `wrapMul` wrap instead -
  always defined, never C's undefined behaviour)
* `/` on whole numbers rounds toward zero (`-7 / 2` is -3); `%` takes the sign of the left
  side (`-7 % 2` is -1). Dividing a whole number by 0 is a DivideByZeroError;
  `-2147483648 / -1` an OverflowError
* `float` / `double` follow IEEE 754: dividing by 0.0 gives infinity, no error
* An int used as a double is always exact. An int used as a **float** (stored, passed,
  returned, or beside a float in `+ - * / %` or a comparison) must fit exactly - a float
  holds whole numbers exactly only up to 16,777,216 (Task 27.2f, user decision 2026-10-17):
  with `[numbers] autoWidening = false` (the default) a written number that doesn't fit is a
  compile error and any other value is checked while running - a **PrecisionError** (an
  ArithmeticError); with `true` it widens automatically and every place gets a warning.
  Nothing is narrowed silently - a narrowing conversion is a function (`toByte`, `toInt` of
  text) that checks
* `byte` is 0-255; byte arithmetic gives an int; storing back into a byte goes through `toByte`

#### Indexes, loops and collections
* Every index is checked - strings, bytes, lists, maps and fixed-size arrays: outside is an
  IndexError (a missing map key a KeyError), never a crash or a silent overwrite. Unsafe
  mode doesn't change this
* `for x in xs` over a List or Map: adding or removing elements of that collection inside
  the loop is a **ModifiedWhileLoopingError** (user decision 2026-10-17) - never a skipped
  element. Replacing an element's value is fine. A list made just for the loop can't be
  changed by anyone, so it isn't checked
* A function that calls itself without end raises a StackOverflowError (stack use; or
  `[safety] maxCallDepth`)

#### Errors
* Any function can fail; an error nobody captures or catches bubbles up and stops the
  program at the end of main with its message (exit code 1). A capture (`T x, err = f()`)
  takes any error the right side raises; the first error raised is the one that travels.
  Every run-time failure is an Error of one of Fusion's own types (see "Error Handling")

#### Evaluation order
* A call's arguments run left to right, as written (also with named arguments)
* `and` / `or` stop early (the right side runs only when needed)
* **Open (Task 37.2):** the two sides of other operators run in C's order - `next(c) -
  next(c)` may run the right call first. Write them on separate lines when the order matters

[< 010 Philosophy](010-Philosophy.md) | [Index](index.md) <!-- nav -->
