[< 070 ControlFlow](070-ControlFlow.md) | [Index](index.md) | [081 Autoboxing >](081-Autoboxing.md) <!-- nav -->

# 080 Null

## Null Handling

**Status:** [PLANNED 30] - designed 2026-10-27 (user decisions). Full write-up with truth
tables and when (not) to use `?.`: `files/Nullable_Values.md`.

Description: No value is null unless it can be, and a missing object never crashes the program by surprise.
- The problem it solves: in Java, C#, C, JavaScript and Python any object may be null, and using it crashes -
  far from where it was left unset
- It matters most for data from outside: a JSON object whose field is `null`, a database row, user input, a
  class object that was never created

---

### Core Principles

* **Only class objects and enums can be null** (class objects: Task 32; enums: built, Task
  30.11 - `Status s` with no value is null, not the first value). Numbers, bools, chars and structs are
  values; strings, arrays, `List` and `Map` are values too - never null, empty when not
  set (`""`, `[]`), length 0 when empty
* **A project may allow null** for strings, arrays, lists or maps when "not set yet" must
  differ from "empty": `[strings]` / `[arrays]` / `[lists]` / `[maps]` `nullable = true`
  (default false)
* **`?` is never part of a type** (no `int?`, `string?`): it is used on a variable, as a
  guard - `x?.method()`
* **Nothing changes silently**: a default is always one written in the code (`??`)

---

### Null Checking Methods

Description: Three ways to handle a value that might be null - check first, guard, or let it
fail.

* **Check if null** - `==`, `===`, `is null`, and `x?.null` as quick typing; `!x?.null`
  means "not null"

```
Spaceship ship = getShip()

if ship?.null                    // the same as: if ship == null / if ship is null
    print("No ship")
    return

ship.start()                     // safe: checked above
```

* **Guard with `?.`** - on a null object the method is not run and nothing errors. The
  result is null; inside an `if` the condition is false, so the else block runs - also
  for a comparison

```
Person pep                       // never set: null

if pep?.getAge() >= 18           // no error: false, the else block runs
    print("old enough")
else
    print("not old enough, or unknown")

if !(pep?.getAge() >= 18)        // true: runs
    print("ask for ID")

string captainName = ship?.getCaptain()?.getName() ?? "Unknown"   // a chain
```

* **Default with `??`** - only where a value is expected and none may come:
  `someObject?.someMethod() ?? value`
* **Plain `.`** - `pep.getAge()` on null is a **NullError** (an Error subtype, Task 26):
  only a `catch` handles it. Use it where missing would be a bug
* **Length through `?.`** - `string?.length()` and `array?.length` give -1 on a null string
  or array (only with the `nullable` settings on); an empty one gives 0. Every other member
  or method gives null
* **No `x!`** ("I know it isn't null") - write `if !x?.null` instead
* **Warnings**: a guarded value in a comparison (with null, `>= 18` and `< 18` are both
  false, so `!(x >= 18)` is not `x < 18`); `??` after `?.length()` (-1 is not null, so the
  default is never used)

---

### Numbers as conditions

`if count` with a number: a `fusion.toml` setting (Task 30.9, user 2026-10-27):

```toml
[conditions]
numbers = "positive"   # default: positive is true; zero and negatives are false
                       # "nonzero": 0 false, other numbers true (C, Python, JavaScript)
                       # "off": a condition must be a bool (Java, C#, Go, Rust, Swift)
```

- With `"positive"`, -1 ("not found", "not set") and 0 ("empty") are both false
- The editor shows the project's choice as a hint (Task 36.7)
- **Built (Task 30.9)**: a number in a condition becomes `n > 0` ("positive") or `n != 0` ("nonzero") while
  compiling

Where numbers count as true / false (user, 2026-10-27) - only when the setting is not "off":
- in an `if` or `while` condition, including `and` / `or` / `not` inside it:
  `if count and ready`, `if not errors`
- `count == true` / `count == false` compares by the same rule (0 false; 1, 2, 1000 true)
- `count === true` is always false - a number is not a bool (the compiler already warns that
  `===` on two different types is always false)
- `bool b = count` is always an error, whatever the setting - write `bool b = count > 0`
- `and` / `or` always give a bool

---

### Strict Mode (replaced)

The earlier "strict mode" (the compiler adding null checks to every parameter) is replaced
by the rules above: only class objects and enums can be null, a plain `.` on null is a NullError with
file and line, and `?.` is the guard where missing is normal.

[< 070 ControlFlow](070-ControlFlow.md) | [Index](index.md) | [081 Autoboxing >](081-Autoboxing.md) <!-- nav -->
