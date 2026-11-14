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

* **Automatic Compiler Protections**

user added comment: can be seen if requested by option settings. not added by default. controled in project settings
some apps the 10000000 might be two small for large database handling. verify specific
Description: Compiler automatically adds safety checks to loops.

```
// User writes:
for i in range(1000)
    processData(i)
end loop

// Compiler automatically adds (invisible to user):
// - Infinite loop protection (default 1,000,000 iterations)
// - Thread interrupt checking (for graceful shutdown)
// - System resource monitoring (RAM/CPU usage)
```

**Configuration**:
* Default iteration limit: Based on system resources
* Project setting: `fusion.config.max_iterations = 10000000`
* Per-loop override: `#[max_iterations(100000)]`
* Disable protection: `#[no_loop_protection]` (use with caution)

**System Resource Adaptation**:
* Automatically adjusts limits based on available RAM
* Monitors CPU usage during loops
* Responds to OS shutdown signals
* Graceful degradation under resource pressure

```
// Disable automatic protection (advanced use only)
#[no_loop_protection]
while serverRunning
    handleRequest()
end loop
```

* **Loop with Manual Exit Condition**

```
int count = 0
while ship.isActive
    ship.update(deltaTime)
    count += 1
    
    // Manual break
    if count > 1000
        break
        
end loop with
    check
        if not ship.isValid()
            print("Warning: Invalid state")
```

* **Loop with Periodic Check** (Every N iterations)

```
for i in range(100000)
    processData(i)
    
end loop with {10}  // Check every 10th iteration
    check
        if systemOverloaded()
            print("System overload at iteration {i}")
            exit loop
```

* **Loop with Iteration Limit** (Infinite loop prevention)

```
while processing
    doWork()
    
end loop with {100000}  // Exit if exceeds 100,000 iterations
    check
        if iteration >= 100000
            print("Loop limit reached")
            exit loop
```

* **Loop with Thread Interrupt Handling**

```
for item in hugeCollection
    processItem(item)
    
end loop with
    check interrupt(signal, data)
        if signal == InterruptSignal.Shutdown
            print("Received shutdown signal")
            cleanup()
            exit loop
        
        if signal == InterruptSignal.Pause
            waitForResume()
            continue loop
```

* **Complete Loop Example** (All check types)

```
int count = 0
bool processing = true

while processing
    data = fetchData()
    processData(data)
    count += 1
    
    if count >= maxCount
        break

end loop with {50}  // Periodic check every 50 iterations
    
    check
        if not isHealthy()
            print("System unhealthy")
            exit loop
    
    check
        if count >= 10000
            print("Maximum iterations reached")
            exit loop
    
    check interrupt(signal, data)
        if signal == InterruptSignal.Stop
            print("Stop signal received")
            processing = false
            exit loop
```

* **Simple Loop** (Automatic safety)

```
// Most loops don't need explicit checks
for i in range(100)
    doWork(i)
end loop

// System automatically provides:
// - Infinite loop protection (default 1M iterations)
//   * Configurable based on system resources (RAM/CPU/disk space)
//   * Compiler settings can adjust based on available resources
//   * User settings can override for specific needs
//   * Protects PC from hanging or crashes
// - Thread interrupt checking
//   * Handles system shutdown gracefully
//   * Responds to user interrupts (Ctrl+C)
//   * No manual handling needed
//   * Cooperative multitasking automatic
```

**Note**: The compiler/runtime automatically adds these protections even if user doesn't specify them. This prevents common programming errors and system hangs without requiring explicit code from the developer.
user added note: can be controled from config. might not be needed in some situations.

---

### Loop Labels

Description: Named loops for nested break/continue.

```
outer: for x in range(10)
    for y in range(10)
        if grid[x][y] == target
            print("Found at ({x}, {y})")
            break outer
    end loop
end loop
```

[< 061 Enums](061-Enums.md) | [Index](index.md) | [080 Null >](080-Null.md) <!-- nav -->
