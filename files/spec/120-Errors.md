[< 110 Generics](110-Generics.md) | [Index](index.md) | [130 Comments >](130-Comments.md) <!-- nav -->

# 120 Errors

Contents: [Multiple Return Values](#multiple-return-values) | [Function with Error Return](#function-with-error-return) | [Calling with Error Capture](#calling-with-error-capture) | [Calling Without Error Capture](#calling-without-error-capture) | [Error Chaining](#error-chaining) | [Error Object](#error-object) | [Traditional Exceptions](#traditional-exceptions) | [When to Use Each](#when-to-use-each)

## Error Handling

**Status:** [PARTLY] Task 26 complete - built:
- error returns, capturing (26.2)
- try / catch / finally / throw (26.3)
- catchable built-in failures (26.4)
- the `[errors] returns / exceptions` switches (26.5)
- Example program: `examples/errors_demo.fusion`

**Custom error types (Task 26.9, user decisions 2026-10-16):**
- `error FileError` with fields like a struct's; `error FileNotFound : FileError` extends one
- Every error type is an Error: message, code, where - plus its parents' fields and its own
- A body line `message = "File not found"` (or `code = 404`) gives that type a default
- Made like a struct: message, code, then the fields (the parent's first), by position or by name; a field
  without a default must be given
- An error type is accepted where its parent (or Error) is expected
- Its fields are read only
- Thrown or returned like any error, copied and freed automatically, across modules with `public error`

**Typed capture, `err.kind`, match on error types (Task 26.10):**
- `Ship s, FileError err = f()` captures **any** error (user decision): err's own fields are their defaults
  unless it really is a FileError
- `err.kind` is the type's name ("FileError", "Error")
- `match err` takes error type names as cases:
  - `case FileError` also matches its subtypes, `case Error` any error
  - inside a case with one type, err *is* that type, so its own fields can be read
  - a name that isn't an error type is a compile error (string compares would let a typo through)
  - an else (or `case Error`) is required
  - a case already covered by an earlier one is a warning

**Fusion's own error types (Task 26.12):** every run-time failure raises one of these
- All are Errors; a parent catches its children (`catch LookupError e` takes IndexError and KeyError)
- A program can extend them (`error ConfigError : FileError`), not reuse their names

```text
ArithmeticError: DivideByZeroError (7 / 0, 7 % 0 on whole numbers - a crash before 26.12)
FormatError: NumberFormatError (toInt("12x")), PatternError (formatNumber), HexFormatError,
             TextEncodingError (bytes that aren't text)
ValueError: RangeError (toByte(300), negative counts, base), UnknownValueError (fromString)
LookupError: IndexError (s[9], xs[9], b[9], slice ...), KeyError (m["missing"])
FileError (path): FileNotFoundError, PermissionError, FileReadError, FileWriteError,
                  FileTooLargeError, DeleteError - chosen by why the system said no
LimitError: StringTooLongError ([strings] maxLength), ResultTooLargeError (over 2 GB)
```
- Added by Task 27: OverflowError and PrecisionError (ArithmeticError), StackOverflowError (LimitError),
  ModifiedWhileLoopingError (ValueError)
- Added by Task 30.11: NullError (Error) - using a null value: `toInt()` on a null enum, a match on a null
  enum with no case for it
- Not catchable: out of memory, a List past 536,870,911 elements

**Endless recursion (Task 27.2c, user decisions 2026-10-17):**
- A function that can call itself (directly, through others, or through a function value) checks the stack
  on entry
- When it is nearly full - the limit comes from the real stack size - it raises a **StackOverflowError**
  (a LimitError) instead of crashing
- Every frame then unwinds and frees what it holds, so it can be caught or captured like any error
- Functions that can't recurse get no check
- For memory-constrained devices `[safety] maxCallDepth = 10000` also counts calls (tune the number by
  profiling); the default "max" uses stack use alone

**Whole-number overflow (Tasks 27.2b, 27.2d, user decisions 2026-10-17):**
- int `+ - *`, unary `-` and `-2147483648 / -1` that don't fit raise an **OverflowError** (an
  ArithmeticError) - never a silently changed value (C, Go and Java wrap; Fusion checks, like Swift)
- In C each is GCC's overflow builtin: the operation and one jump
- Arithmetic made only of written numbers (`60 * 60 * 24`) isn't checked
- Wrapping on purpose (hashes, checksums):
  - `wrapAdd(a, b)`, `wrapSub`, `wrapMul` (methods too: `a.wrapMul(b)`)
  - an `unchecked` block whose `+ - *` wrap
  - `[numbers] overflowWrap = true` makes every `+ - *` wrap (Task 32.0 - it was `[safety] mode = "unsafe"`)
- Wrapping is always defined (unsigned arithmetic) - never C's undefined behaviour
- Array bounds checks are never turned off

**Typed catch (Task 26.11, user: now, for a working sample):** `catch FileNotFound e`, `catch FileError e`,
... `catch e`
- The first catch whose type matches takes the error (a parent type catches its subtypes)
- An untyped catch takes any error and must be last
- An error no catch takes goes on, through the finally
- A catch an earlier one already covers is a warning
- No central ERROR enum: each error type is its own kind, so a module can add its own

**Every run-time error is an Error (Task 26.4, user decision 2026-10-16: all of them):**
- An index out of range (strings, lists, bytes), a missing Map key, text that isn't a number, a file that
  won't open, an invalid pattern, `Enum.fromString` with an unknown name, a string over
  `[strings] maxLength`, ... can be captured or caught like any other error
- `err.where` says where it happened
- One nobody handles stops the program at the end of main with `Runtime error at main.fusion:12: ...`,
  as before
- Only running out of memory (and a List past 536,870,911 elements) still stops at once
- In C, a runtime function reports with its `where` argument and returns a safe value; the call is checked
  right after it runs

**try / catch / finally / throw as built (Task 26.3):**
- `try` then `catch err` (or a bare `catch`) and/or `finally` - indented, in braces, or closed by `End try`
- One catch catches any error - tell them apart with `err.code` (typed catches: 26.11 above)
- An error in the try block goes to the catch; one in the catch goes on (through the finally)
- `finally` always runs: after the try block, after the catch, when an error passes through, and before a
  `return`, `break` or `continue` leaves the try
- `throw Error(...)` / `throw err` work in any function - a function that throws can fail, so its callers
  check it
- A capture (`int n, Error err = f()`) also catches what `f` throws

**As built (Task 26.2, user decisions 2026-10-09 and 2026-10-16):**
* `Error` is a built-in value:
  * `message` (string), `code` (int, 0 unless given), `where` ("main.fusion:12", where it was made)
  * made with `Error("msg")` or `Error("msg", 404)`; printing it prints the message
  * there is no `null`: a captured Error with no error has an empty message
  * `if err` / `not err` test whether there is one - the one non-bool allowed as a condition
* Any function can fail:
  * `return Error(...)` fails (the value part is its default); `return ship` succeeds
  * writing `Ship, Error function loadShip(...)` only marks it as able to fail (Task 26.7, user decision
    2026-10-16) - `--interface` shows the marker, and a marked function with nothing in it that could fail
    gets a warning
  * `Error function save(...)` is a function with no value that can fail
  * `return err` passes a captured error on
* `Ship s, err = loadShip(f)` (or `Ship s, Error err = ...` - the type is optional, Task 26.8) captures the
  error of any call - including any error raised while evaluating the right side
  * `Error e = save(s)` when there's no value to keep
* An error nobody captures **bubbles up**: out of the function to its caller, until something captures (or,
  with 26.3, catches) it
  * at the end of `main` the program stops with `Error at main.fusion:12: message` and exit code 1
* In C: no setjmp / longjmp
  * a failing function sets the current error and returns a default
  * the call is checked right after it runs (a GCC statement expression)
  * the statement's failure block frees what is held before passing the error on - so every error path is
    leak-free
  * only calls that can fail are checked

Description: Explicit error handling with multiple return values.

---

### Multiple Return Values

Description: Go-style error handling with type safety.

* Functions return both result and error
* Error is null if operation succeeded
* Must check error before using result
* Explicit and visible in function signature

---

### Function with Error Return

```
Spaceship, Error function loadShip(string filename)
    if not fileExists(filename)
        return null, Error("File not found: {filename}")
    
    string data = readFile(filename)
    if data.isEmpty()
        return null, Error("Empty file")
    
    Spaceship ship = parseShipData(data)
    if ship is null
        return null, Error("Invalid ship data")
    
    return ship  // Success - error is implicitly null
```

---

### Calling with Error Capture

```
Spaceship ship, Error err = loadShip("ship.dat")

// Check error first
if err
    print("Error loading ship: {err.message}")
    return

// Safe to use ship here (no error occurred)
ship.start()
ship.move(forward, speed)
```

---

### Calling Without Error Capture

Description: Error bubbles up to caller if it occurs.

```
// Don't capture error - will propagate to caller
Spaceship ship = loadShip("ship.dat")
ship.start()

// If loadShip returns error, it bubbles up
```

---

### Error Chaining

```
Spaceship, Error function loadAndValidateShip(string filename)
    // Load ship
    Spaceship ship, Error err = loadShip(filename)
    if err
        return null, err  // Propagate error
    
    // Validate ship
    bool valid, Error err2 = validateShip(ship)
    if err2
        return null, err2  // Propagate error
    
    // Success
    return ship
```

---

### Error Object

```
class Error
    string message
    int code
    string stackTrace
    
    constructor(string msg)
        this.message = msg
        this.code = 0
        this.stackTrace = captureStackTrace()
    
    constructor(string msg, int code)
        this.message = msg
        this.code = code
        this.stackTrace = captureStackTrace()
```

---

### Traditional Exceptions

Description: Available for unexpected errors when needed.

```
void function riskyOperation()
    try
        Data data = readNetworkData()
        processData(data)
    catch NetworkException as e
        print("Network error: {e.message}")
    catch ParseException as e
        print("Parse error: {e.message}")
    finally
        cleanup()
```

---

### When to Use Each

* **Multiple Returns**: Expected errors (file not found, invalid input, network timeout)
* **Exceptions**: Unexpected errors (out of memory, assertion failures, system errors)

[< 110 Generics](110-Generics.md) | [Index](index.md) | [130 Comments >](130-Comments.md) <!-- nav -->
