[< 033 TypeCasting](033-TypeCasting.md) | [Index](index.md) | [041 Lambdas >](041-Lambdas.md) <!-- nav -->

# 040 Functions

Contents: [Function Declaration Syntax](#function-declaration-syntax) | [Main Function - Application Entry Point](#main-function---application-entry-point) | [Function Block Syntax](#function-block-syntax) | [Calling Functions](#calling-functions)

## Functions and Methods

**Status:** [PARTLY] declarations, main, the block styles, calls, default values, named arguments, lambdas v1 and function types are built (18.1, 18.2.2); closures: Later; methods on the program's own structs [PLANNED 32]

Description: Function definition with return-type-first syntax and flexible parameters.

---

### Function Declaration Syntax

Description: Clear, readable function signatures with type safety.

* **Format**: `<returnType> function name(<type> param {= defaultValue})`
     * Return type comes first (like C/Java)
     * Function keyword for clarity (like VB.NET)
     * Type before parameter name
     * Optional default values with `=`
     * void keyword required (cannot be omitted)
     * **Note**: In syntax examples, `{= defaultValue}` indicates optional default values. The curly braces are notation only, not actual syntax.

* **Basic Functions**

```
void function printMessage(string msg)
    print(msg)

int function add(int a, int b)
    return a + b

Spaceship function createShip(string name, float speed)
    return Spaceship(name, speed)

bool function isValid(int value)
    return value > 0 and value < 100
```

* **Functions with Default Parameters**

```
int function add(int a = 0, int b = 0)
    return a + b

Spaceship function createShip(string name = "Unnamed", float speed = 100.0, int crew = 50)
    return Spaceship(name, speed, crew)

void function configure(bool debug = false, int logLevel = 1)
    setupLogging(debug, logLevel)
```

**Rules for default values** (implemented, Task 18.1.1):
* Parameters with defaults must come last - `int f(int a = 1, int b)` is an error, because
  a call such as `f(5)` couldn't tell which argument was left out
* A default must be a compile-time constant: a literal (`5`, `2.5`, `"text"`, `'c'`, `true`)
  or a negated number (`-1`). It can't refer to another parameter or a variable
* Calls may omit any number of trailing parameters that have defaults; the compiler fills in
  each omitted value at the call site (C itself has no default arguments)
* With named arguments (below), any parameter with a default can be skipped, not only
  trailing ones - `createShip(crew = 200)`

---

### Main Function - Application Entry Point

Description: The main function is the entry point for all Fusion applications.

* **Format**: `void function main(string... args)`
     * Must be named `main` (case-sensitive)
     * Return type is `void` (no return value)
     * Parameter is variadic `string... args` for command-line arguments
     * Application execution starts here
     * Only one main function per application

* **Basic Main Function**

```
void function main(string... args)
    print("Hello, Fusion!")
```

* **Main with Command-Line Arguments**

```
void function main(string... args)
    print("Program started with {args.length} arguments")

    for arg in args
        print("Argument: {arg}")
    end loop

    if args.length > 0
        processCommand(args[0])
```

* **Complete Application Example**

```
// Import required modules
import Fusion.Core
import Fusion.IO

// Main entry point
void function main(string... args)
    // Check arguments
    if args.length == 0
        print("Usage: myapp <filename>")
        return

    // Process file
    string filename = args[0]
    string content, Error err = readFile(filename)

    if err
        print("Error: {err.message}")
        return

    print("File content: {content}")

// Helper function
string, Error function readFile(string filename)
    // Implementation
    return content, null
```

* **Exit Codes** (Optional)

```
import Fusion.System

void function main(string... args)
    bool success = processData()

    if not success
        System.exit(1)  // Exit with error code

    System.exit(0)  // Exit with success
```

**Rules**:
* Main function is required for executable applications
* Not required for libraries or modules
* Must be at top level (not inside a class)
* Can call any other functions or classes
* Command-line arguments passed as string array

---

### Function Block Syntax

Description: Flexible block styles for user preference.

* **No Colon Required**
     * Function declaration ends at parameter list
     * New line automatically starts function body

* **Indentation-Based** (Python-style)

```
int function calculate(int x, int y)
    int result = x + y
    result = result * 2
    return result

void function processShip(Spaceship ship)
    ship.start()
    ship.move(forward, speed)
    ship.stop()
```

* **With Braces** (C/Java-style) - Optional syntax sugar

```
// Style 1: Braces on same line
int function add(int a, int b) {
    int result = a + b
    return result
}

// Style 2: Braces on next line
int function add(int a, int b)
{
    int result = a + b
    return result
}

// When braces used, indentation is ignored
```

* **End Keyword** (VB.NET-style) - Explicit block termination

```
int function factorial(int n)
    if n <= 1
        return 1
    End if
    return n * factorial(n - 1)
End function

void function processData(string filename)
    Data data = loadData(filename)
    if data?.null
        print("Failed to load data")
        return
    End if
    processItems(data.items)
End function

// Clear, explicit endings - useful for longer functions
```

---

### Calling Functions

Description: Multiple ways to pass arguments for flexibility.

**Long lines** (Task 44.3, implemented):
- Inside `( )` and `[ ]` a line break only continues the line - no statement ends there
- Indentation isn't counted there
- So a long call or list can be written over several lines
- Braces `{ }` still open blocks

```fusion
int function total(int a, int b, int c) : a + b + c

void function main()
    int[] scores = [10,              // [ still open: the list goes on
                    20,
                    30]              // ] closes it - the statement ends here
    print("{@1} + {@2} + {@3} = {@4}",
          scores[0],                 // ( still open: the call goes on
          scores[1],
          scores[2],
          total(scores[0],           // a call inside a call - each ( must be closed
                scores[1],
                scores[2]))
```

Output: `10 + 20 + 30 = 60`. The same program, without the comments, is the tested example
`syntax_long_lines` in `files/SYNTAX_REFERENCE.md`.

* **Positional Arguments**: Standard calling

```
int result = add(5, 3)
Spaceship ship = createShip("Enterprise", 200.0, 100)
```

**Evaluation order (implemented, Tasks 18.2.2 and 18.2.2b):** a call's arguments are always
evaluated **left to right as written** - positional or named, for functions, struct
constructors and function values: `sub(next(c), next(c))` runs the first `next` first. (C
itself leaves argument order unspecified; the compiler only adds sequencing where the order
could change the result.) Operators such as `next(c) - next(c)` don't have this guarantee
yet - Task 37.2.

* **Named Arguments**: Explicit parameter names

```
// Out of order is OK
int result = add(b = 5, a = 3)
Spaceship ship = createShip(crew = 100, name = "Voyager", speed = 180.0)

// Mix positional and named (positional must come first)
Spaceship ship = createShip("Discovery", crew = 80, speed = 150.0)
```

* **Using Default Values**

```
// Use all defaults
Spaceship ship1 = createShip()  // name="Unnamed", speed=100.0, crew=50

// Override some defaults
Spaceship ship2 = createShip("Enterprise")  // name="Enterprise", others default

// Override with named parameters
Spaceship ship3 = createShip(crew = 200)  // Only crew changed
```

**Rules for named arguments** (implemented, Task 18.2.2 - for declared functions and struct
constructors):
* Named arguments can come in any order, but arguments without names must all come first
* Any parameter with a default can be left out; one without a default must be given
* Errors: an unknown name, the same parameter given twice (by name twice, or by position and
  by name), a missing parameter
* Arguments are evaluated **left to right as written**, even when named ones are moved to
  their parameter's position - `f(b = next(), a = next())` runs the `b` call first
* Not available for built-in functions (`print`, `len`, `range`) or when calling through a
  function variable or lambda - a function type has parameter types but no names
* Inside a call's parentheses, `name = value` is always a named argument (assignment is a
  statement in Fusion, never an expression)

[< 033 TypeCasting](033-TypeCasting.md) | [Index](index.md) | [041 Lambdas >](041-Lambdas.md) <!-- nav -->
