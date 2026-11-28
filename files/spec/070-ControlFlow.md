[< 061 Enums](061-Enums.md) | [Index](index.md) | [080 Null >](080-Null.md) <!-- nav -->

# 070 ControlFlow

**Contents**

- [Conditionals](#conditionals)
- [Loops with Safety Checks](#loops-with-safety-checks)
- [Loop Labels](#loop-labels)

## Control Flow

**Status:** [PARTLY] if / else if / else, while, for over ranges, arrays, lists and maps, break, continue, return are built (01-04, 18.5.1); `=` compares inside a condition (18.3.5); `match` built (25.3); `switch` / `elif` as aliases (FEATURES Later); the conditional operator `(c) ? a : b` built (30.7); numbers as conditions built (30.9); loop labels and loop safety limits: no task yet

Description: Natural language constructs for program flow with safety features.

---

### Conditionals

Description: Clear and readable branching with multiple comparison operators.

* **Preferred forms** (user, 2026-10-24): `else if` and `switch` are used in docs and
  examples; `elif` is an alias for `else if`, and `match` / `switch` are interchangeable
  (aliases planned - FEATURES Later)
* **A condition** is a bool - or a number, by the project's setting (Task 30.9, built; see
  "Null Handling"): `[conditions] numbers = "positive"` by default, so `if count` means
  `if count > 0`
* **The conditional operator** (Task 30.7, built) - one line, gives a value:
  `string size = (count > 5) ? "big" : "small"`
  * Only the chosen value runs
  * Both values have one type (not an array, for now)
  * Nests to the right (`(a) ? 1 : (b) ? 2 : 3`)
  * The condition is a bool (numbers as conditions: Task 30.9)

* **Comparison Operators**

Operator | Meaning | Example
---|---|---
`==` | Equal to | `if x == 10`
`!=` | Not equal to | `if x != 0`
`<>` | Not equal to (alternative) | `if x <> 0`
`<` | Less than | `if x < 10`
`>` | Greater than | `if x > 5`
`<=` | Less than or equal | `if x <= 10`
`>=` | Greater than or equal | `if x >= 5`

```
// If statements with comparisons
if ship.fuelLevel > 50
    ship.engageWarpDrive()
elif ship.fuelLevel <> 0
    ship.startEngine()
else
    print("No fuel!")

// Using <> operator
int x = 10
int y = 20

if x <> y
    print("Values are not equal")

// Both work the same
if x != y
    print("Values are not equal")

// Pattern matching
match ship.type
    case ShipType.Fighter:
        ship.activateWeapons()
    case ShipType.Cargo:
        ship.openCargoBay()
    case ShipType.Explorer:
        ship.deploySensors()
    else:
        print("Unknown ship type")
```

---

### Loops with Safety Checks

Description: Explicit loop termination with multiple safety mechanisms.

* **Basic Loop Syntax**

```
// While loop
while condition
    // body
end loop

// For loop with range function
for i in range(0, 10)
    print("Count: {i}")
end loop

// For loop with ... range operator
for i in 1...10
    print("Number: {i}")  // 1, 2, 3, ..., 10
end loop

// Range with step
for i in 0...100...10
    print(i)  // 0, 10, 20, 30, ..., 100
end loop

// For-each loop
for ship in fleet
    ship.update(deltaTime)
end loop
```

* **The `...` Operator**

Description: Multi-purpose operator for ranges, spreads, and variadic arguments.

**Use 1: Range in Loops**
```
// Simple range
for i in 1...100
    processItem(i)
end loop

// Range with step
for x in 0...360...45
    drawAngle(x)  // 0, 45, 90, 135, 180, 225, 270, 315, 360
end loop

// Create array from range
int[] numbers = [1...10]  // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

**Use 2: Variadic Functions**
```
int function sum(int... numbers)
    int total = 0
    for num in numbers
        total += num
    end loop
    return total

// Call with any number of arguments
int result = sum(1, 2, 3, 4, 5)  // 15
int result2 = sum(10, 20)         // 30
```

**Use 3: Array Spread**
```
int[] arr1 = [1, 2, 3]
int[] arr2 = [4, 5, 6]

// Spread into new array
int[] combined = [...arr1, ...arr2]  // [1, 2, 3, 4, 5, 6]

// Spread in function call
int total = sum(...combined)
```

**Use 4: Rest Parameters**
```
void function logMessage(string level, string... messages)
    for msg in messages
        print("[{level}] {msg}")
    end loop

// Usage
logMessage("INFO", "Starting", "Loading", "Complete")
```

* **Loop checks** (Task 56, D.214-D.220)

A loop's checks are written in a `with` part after its body, and run after each pass, in order. A check is not for
normal program control - only for what may affect the loop: a limit reached, an unhealthy system, a shutdown. It can
also serve as a debug or progress tool.

```fusion
while processing                     // indent style
    doWork()
with
    check 100                        // no condition: every 100th pass - a hook, the loop carries on
        print("{loop.count} passes")
    check 50 not isHealthy()         // a condition, tested every 50th pass: true - the block, then the loop ends
        print("unhealthy")
    check >= 100000                  // the passes so far
        print("too many passes")

while processing {                   // braces
    doWork()
} with {
    check >= 100000 { print("too many passes") }
}

while processing                     // End style
    doWork()
end loop with
    check >= 100000
        print("too many passes")
```

| Form | Runs | When it fires |
|---|---|---|
| `check` | every pass | its block runs; the loop carries on |
| `check 20` | every 20th pass | its block runs; the loop carries on |
| `check not isHealthy()` | every pass | true: its block runs, then the loop ends |
| `check 50 not isHealthy()` | every 50th pass | true: its block runs, then the loop ends |
| `check >= 10000` (`>`, `==`) | every pass | the passes so far reach it: its block runs, then the loop ends |
| `check InterruptSignal.Stop`, `check interrupt(signal, data)` | at the loop's safe point | with Task 42's interrupts (42.26, 42.27) |

* Inside a check's block: `break` and `continue` are errors (the check ends the loop by itself); `return` leaves the
  function; `exit loop outer` leaves an outer loop too (D.215, D.219)
* `loop.count` - the pass number, in the body and the checks (read-only - D.217)
* `[safety] maxIterations` (default 0 = no limit - D.218): a `while` or `loop` that passes it stops with a
  LoopLimitError (a built-in error a `catch` can handle) naming its line and the limit - never a silent stop; a `for`
  over a range or a collection ends by itself and has no limit; a loop with its own `check >= N` uses that instead
* Nothing is added by itself (D.220): a loop gets a pass counter only when it has checks, or when maxIterations is
  above 0. There is no RAM / CPU monitoring and no `#[...]` attribute; Ctrl+C and a shutdown come with the
  interrupts (Task 42)

**The truth table (Rule 4c)** - each row a test in tests/test_loop_checks.py:

| Case | Result |
|---|---|
| `check` / `check N`, any block style | the block every pass / every Nth; the loop carries on |
| `check cond` true / false | the block, then the loop ends / nothing |
| `check N cond` - on an Nth pass true / not an Nth pass | the block, then the end / not tested |
| `check >= N` / `> N` / `== N` | ends when the passes so far reach it |
| a condition that reads a null (Rule 4b) | a NullError a `catch` handles; with `?.` / `??` it runs on |
| `break` / `continue` in a check | a compile error |
| `return` in a check | leaves the function |
| `exit loop` / `exit loop outer` in a check | leaves this loop / the outer one |
| `break outer` / `continue outer` in the body | leaves / continues the outer loop |
| an unknown label | a compile error |
| maxIterations 0 / above 0 - a `while` past it | nothing / a LoopLimitError |
| maxIterations above 0 - a `for` over a range | no limit |
| maxIterations above 0 - a loop with `check >= N` | its own check, not the limit |

---

### Loop Labels

Description: Named loops for nested break / continue (D.219).

```fusion
outer: for x in 0...9
    for y in 0...9
        if grid[x][y] == target
            print("Found at ({x}, {y})")
            break outer
```

[< 061 Enums](061-Enums.md) | [Index](index.md) | [080 Null >](080-Null.md) <!-- nav -->
