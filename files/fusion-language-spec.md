# Fusion Programming Language Specification v2

Description: A modern programming language combining the performance of C, structure of Java, simplicity of Python, readability of VB.NET, and concurrency of Go. Designed for game development, automation, and systems programming.

**Fusion is a combination of various programming languages unified into one cohesive language.**

---

## Language Philosophy

Description: Core principles guiding Fusion's design decisions.

* Performance First: Compiled to native code with optional JIT
     * C-style memory control when needed
     * Automatic memory management by default
     * Zero-cost abstractions

* Readable and Expressive: Natural language constructs
     * VB.NET-style keyword readability
     * Python-style indentation significance
     * Clear intent over brevity

* Type Safety with Flexibility: Strong typing with inference
     * Java-style static typing
     * Python-style duck typing option
     * Gradual typing support

* Modern Features: Built for today's development
     * First-class functions
     * Pattern matching
     * Async/await native support
     * Null safety by default

* Concurrency Model: Safe and efficient parallel execution
     * Go-style channels and goroutines
     * Message passing for safety
     * Shared memory with automatic locking
     * Race and deadlock detection

---

## Syntax Overview

Description: Core syntax elements borrowed from each parent language.

* From Python: Indentation-based blocks, simple syntax
* From Java: Type annotations, interface contracts
* From C: Pointer operations, memory control (optional)
* From VB.NET: Readable keywords, property syntax
* From Go: Channels, goroutines, multiple return values, defer

---

## Data Types and Variables

Description: Type system combining static typing with clear null safety rules.

---

### Type Categories

Description: Fusion distinguishes between value types and reference types for null safety.

* **Value Types**: Cannot be null, always have a value
     * Primitives: byte, ubyte, short, ushort, int, uint, long, ulong
     * Floating point: float, double, decimal
     * Boolean: bool
     * Character: char
     * Structs: All value-type structs
     * Note: Syntax like `int?` does NOT exist

* **Reference Types**: Can be null, must be checked before use
     * Objects: All class instances
     * String: Special case (class but treated as value type for convenience)

---

### Complete Type Specifications

Description: All built-in types with their properties and capabilities.

Type | Default | Min | Max | Autobox Class | Safe Cast To
---|---|---|---|---|---
byte | 0 | -128 | 127 | Byte | short, int, long, float, double
ubyte | 0 | 0 | 255 | UByte | ushort, uint, ulong, float, double
short | 0 | -32,768 | 32,767 | Short | int, long, float, double
ushort | 0 | 0 | 65,535 | UShort | uint, ulong, float, double
int | 0 | -2,147,483,648 | 2,147,483,647 | Int | long, float, double
uint | 0 | 0 | 4,294,967,295 | UInt | ulong, float, double
long | 0 | -9,223,372,036,854,775,808 | 9,223,372,036,854,775,807 | Long | float, double
ulong | 0 | 0 | 18,446,744,073,709,551,615 | ULong | float, double
float | 0.0f | ±1.5 x 10^-45 | ±3.4 x 10^38 | Float | double
double | 0.0 | ±5.0 x 10^-324 | ±1.7 x 10^308 | Double | decimal
decimal | 0.0 | ±1.0 x 10^-28 | ±7.9 x 10^28 | Decimal | (highest precision)
bool | false | false | true | Boolean | int (0 or 1)
char | '\0' | U+0000 | U+10FFFF | Char | int, string
string | "" | (empty) | (memory limit) | String | (no casting from)

---

### Nullability Rules

Description: Which types can be null and how to check them.

Type Category | Can Be Null? | Check Method | Example
---|---|---|---
Value Types | NO | N/A (always has value) | `int x` is never null
Structs | NO | N/A (always has value) | `Vector3 v` is never null
String | YES | `str?.null` or `str is null` | `if str?.null then handle`
Objects | YES | `obj?.null` or `obj is null` | `if ship?.null then handle`

---

### Variable Declarations

Description: Multiple declaration styles for different scenarios.

* **Type-First Declaration**: No ambiguity
     * Format: `<type> varName = value`
     * Use when: Type clarity important
     * Example: `int count = 10`

```
int count = 10
string name = "Starship"
float speed = 299792.458
Spaceship ship = Spaceship("Enterprise", 100.0)
```

* **Type Inference**: Less verbose
     * Format: `var varName = value`
     * Use when: Type obvious from value
     * Example: `var count = 10`

```
var name = "Starship"
var speed = 299792.458
var position = Vector3(10, 20, 30)
```

* **Declaration Without Initial Value**: Uses default
     * Format: `<type> varName`
     * Uses default value from table above
     * Example: `int count` defaults to 0

```
int count          // 0
string name        // ""
bool flag          // false
float speed        // 0.0f
Spaceship ship     // null (reference type)
```

---

### Constants

Description: Immutable values, must be initialized at declaration; reassignment is a
compile-time error.

```
const int MAX_ITERATIONS = 1000
const float PI = 3.14159265359
const string GAME_VERSION = "1.0.0"
```

**Implemented (MVP, Task 8):** local const declarations inside a function body, with an
explicit type, as shown above - matching `variable_declaration` in fusion.ebnf. Fusion uses
block-level (lexical) scoping (Task 12.6), so a const declared inside an `if`/`while`/`for`
block is only visible inside that block, and is never visible outside the function it's
declared in.

**Not yet implemented:** type-inferred const (`const GAME_VERSION = "1.0.0"` without a type
name), and module-level/class-level constants (`public const MAX_SPEED: float = 1000.0`,
shown later in this document under "Classes and Objects") - those depend on class support,
which has not been built yet.

---

### Arrays

Description: Fixed-size, homogeneous collections of a single element type.

```
int[] scores = [10, 20, 30]      // size inferred from the literal
float[3] buffer                   // explicit size, zero-initialized (no literal needed)
int[3] fixed = [1, 2, 3]          // explicit size + literal (must agree)

scores[0]                         // read
scores[0] = 99                    // write an element
int count = len(scores)           // size, as a builtin function call
```

**Implemented (Task 9 v1):** local array variables, declared with an explicit size
(`int[N]`), an initializer (`int[] x = [...]`, size inferred), or both (which must agree).
Reading and writing individual elements (`arr[i]`, `arr[i] = value`). `len(arr)` as a
builtin - since size is always known at compile time, `len(arr)` compiles directly to that
size as a literal, not a runtime call. `const int[] arr = [...]` works the same as scalar
`const` - the array and its elements become immutable.

**Not yet implemented (see taskSummary2.md Task 9 for the full list and reasoning):**
- Arrays as function parameters or return types (local variables only for now - a C array
  parameter decays to a pointer and loses its length, which needs its own design)
- Multi-dimensional arrays (`int[][]`)
- An array size given as anything other than an integer literal (`int[n]` where `n` is a
  variable is not supported; only `int[5]`-style literal sizes are)
- Whole-array reassignment after declaration (`arr = [4, 5, 6]`) - only per-element
  assignment is supported, since a plain C array isn't reassignable that way
- Dynamic/resizable arrays (no `malloc`-backed growth yet - fixed-size only)
- Bounds checking (indexing out of range is undefined behavior, same as in C, for now)
- Nullable arrays, `arr.length` (property syntax), `arr?.length` / `arr?[i]` (safe
  navigation) - see "Array Safe Navigation" and "Null Safety" later in this document,
  which already describe the intended design; building it requires deciding Fusion's
  nullability/memory model first (Task 12.7), so it's tracked as its own future task rather
  than bundled into Task 9's array launch. `len(arr)` is the only way to get an array's
  size for now.

---

### String Implementation

Description: Immutable strings with copy-on-write semantics.

* **Characteristics**
     * Readonly array of chars
     * Stored in string pool (separate from other values)
     * Multiple references share same string in memory
     * Immutable: editing creates new string
     * Old string garbage collected if no references

* **Memory Model**

```
string name = "Enterprise"     // Stored in string pool
string ref = name              // Both reference same "Enterprise"
ref = "Modified"               // New string created, name unchanged
// Old "Enterprise" kept in pool (name still references it)
```

* **String Operations**: All return new strings

```
string original = "Hello"
string upper = original.toUpper()      // Returns "HELLO", original unchanged
string sub = original.substring(0, 3)  // Returns "Hel", original unchanged
string concat = original + " World"    // Returns "Hello World", original unchanged
```

---

### Type Casting

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
float f = cast<float>(d)           // OK: loses precision
int i = cast<int>(d)               // OK: becomes 3 (truncates)

long big = 1000000000000
int small = cast<int>(big)         // Runtime error if too big!
```

* **Unsigned/Signed Conversions**

```
uint positive = 100
int signed = cast<int>(positive)   // OK: value fits

int negative = -50
uint unsign = cast<uint>(negative) // Runtime error: cannot convert negative!
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

---

## Functions and Methods

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

* **Positional Arguments**: Standard calling

```
int result = add(5, 3)
Spaceship ship = createShip("Enterprise", 200.0, 100)
```

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

---

### Lambda Expressions (Anonymous Functions)

Description: Variables that hold functions. Lambdas are first-class citizens with full type safety.

**Key Concept**: A lambda is a variable that holds a function. Use `func` or `function` keywords interchangeably based on preference.

**Format**: `<returnType> <variableName>(<type> <param> {= default}) : <expression or body>`

---

* **Simple Single-Line Lambdas**

```
// Basic lambda - variable holds function
int add(int x, int y) : x + y

// Use it like a function
int result = add(5, 3)  // result = 8

// Another example
int double(int x) : x * 2
int value = double(10)  // value = 20
```

* **Lambdas with Default Values**

```
// Lambda with default parameter
int addWithOffset(int x, int offset = 5) : x + offset

int result1 = addWithOffset(10)      // result1 = 15 (uses default offset = 5)
int result2 = addWithOffset(10, 2)   // result2 = 12 (uses offset = 2)

// String concatenation with default
string greet(string name, string greeting = "Hello") : greeting + ", " + name
string msg1 = greet("Alice")           // msg1 = "Hello, Alice"
string msg2 = greet("Bob", "Hi")       // msg2 = "Hi, Bob"
```

* **Multi-Line Lambdas with Indentation**

```
// Comparison lambda - multi-line with indentation
int comparator(int a, int b) :
    if a < b
        return -1
    if a > b
        return 1
    return 0

int result = comparator(5, 10)  // result = -1

// Complex calculation
float calculate(float x, float y) :
    float sum = x + y
    float product = x * y
    return sum / product

float answer = calculate(4.0, 5.0)
```

* **Multi-Line Lambdas with Braces**

```
// Using braces instead of indentation (user preference)
int process(int value) : {
    int doubled = value * 2
    int added = doubled + 10
    return added
}

// Braces allow flexible formatting
string format(string text, bool uppercase) : {
    if uppercase
        return text.toUpper()
    return text.toLower()
}
```

* **Using func or function Keywords (Optional)**

```
// Both keywords work - user preference
int multiply = func(int x, int y) : x * y
int divide = function(int x, int y) : x / y

// Multi-line with func
int square = func(int x) :
    return x * x

// Multi-line with function and braces
int cube = function(int x) : {
    return x * x * x
}

// Keywords are completely interchangeable
```

* **Lambdas as Function Parameters**

```
// Function that accepts lambda as parameter
// Type annotation uses : (default) or -> (alternative)
List<int> function mapValues(List<int> values, (int) : int operation)
    List<int> result = List<int>()
    for value in values
        result.add(operation(value))
    end loop
    return result

// Define a lambda
int tripler(int x) : x * 3

// Pass lambda as argument
List<int> numbers = [1, 2, 3, 4, 5]
List<int> tripled = mapValues(numbers, tripler)  // [3, 6, 9, 12, 15]

// Or define lambda inline
List<int> doubled = mapValues(numbers, func(int x) : x * 2)  // [2, 4, 6, 8, 10]
```

* **Closures - Capturing Variables**

```
// Lambda can capture variables from outer scope
int makeAdder(int offset)
    // This lambda captures 'offset' from outer scope
    int adder(int x) : x + offset
    return adder

int add5 = makeAdder(5)
int add10 = makeAdder(10)

int result1 = add5(3)   // result1 = 8  (3 + 5)
int result2 = add10(3)  // result2 = 13 (3 + 10)
```

* **Type Annotations for Lambdas**

```
// Function type syntax: (paramTypes) : returnType
// Alternative syntax: (paramTypes) -> returnType  (both work)

// Declare variable to hold function
(int, int) : int calculator = null

// Assign lambda to it
calculator = func(int a, int b) : a + b
int sum = calculator(5, 3)  // sum = 8

// Change the lambda
calculator = func(int a, int b) : a * b
int product = calculator(5, 3)  // product = 15
```

**Rules**:
* Lambda = variable that holds a function (NOT a separate keyword)
* Return type comes first (consistent with function declarations)
* `func` and `function` keywords are optional and interchangeable
* Single-line: use `:` followed by expression
* Multi-line: use `:` followed by indented block or `{}`
* Type annotation separator: `:` (default) or `->` (alternative)
* Explicit types always required (except in unsafe mode)
* Lambdas can capture variables from outer scope (closures)
* Lambdas are first-class: can be passed as arguments, returned from functions, stored in variables

---

### Error Handling with Multiple Returns

Description: Go-style multiple return values for explicit error handling.

* **Function with Error Return**

```
Spaceship, Error function loadShip(string filename)
    if not fileExists(filename)
        return null, Error("File not found: {filename}")
    
    Spaceship ship = parseShipFile(filename)
    if ship is null
        return null, Error("Invalid ship data")
    
    return ship  // Success - error is implicitly null
```

* **Calling with Error Capture**

```
Spaceship ship, Error err = loadShip("ship.dat")

// Check error first
if err
    print("Error loading ship: {err.message}")
    return

// Safe to use ship (no error occurred)
ship.start()
```

* **Calling Without Error Capture** (Bubble up)

```
// Error bubbles up to caller if it occurs
Spaceship ship = loadShip("ship.dat")
ship.start()
```

* **Error Object**

```
class Error
    string message
    int code
    string stackTrace
    
    constructor(string msg)
        this.message = msg
        this.code = 0
        this.stackTrace = captureStackTrace()
```

* **Error Chaining**

```
Spaceship, Error function loadAndValidateShip(string filename)
    Spaceship ship, Error err = loadShip(filename)
    if err
        return null, err
    
    bool valid, Error err2 = validateShip(ship)
    if err2
        return null, err2
    
    return ship
```

---

## Classes and Objects

Description: Object-oriented programming with modern features and clear syntax.

---

### Class Definition

Description: Java-style structure with Python simplicity.

```
class Spaceship
    // Properties - auto-implementation
    property Name: string { get; private set; }
    property Speed: float { get; set; }
    property Position: Vector3 { get; private set; }
    
    // Constants - automatically static, can be private/public
    public const MAX_SPEED: float = 1000.0
    private const DEFAULT_FUEL: float = 100.0
    
    // Static fields - belong to class, not instance
    private static int shipCount = 0
    public static int TotalShips
        get
            return shipCount
    
    // Private fields - instance-specific
    private float fuelLevel
    private bool isEngineActive
    
    // Constructor - explicit keyword, no return type
    constructor(string name, float initialSpeed)
        this.Name = name
        this.Speed = initialSpeed
        this.Position = Vector3(0, 0, 0)
        this.fuelLevel = DEFAULT_FUEL
        this.isEngineActive = false
        shipCount += 1  // Increment static counter
    
    // Instance methods - return type first
    void function start()
        if fuelLevel > 0
            isEngineActive = true
            print("Engine started: {Name}")
    
    void function move(Vector3 direction, float deltaTime)
        if isEngineActive and fuelLevel > 0
            Position = Position + (direction * Speed * deltaTime)
            fuelLevel -= 0.1 * deltaTime
    
    // Static methods - belong to class itself
    public static Spaceship function createDefault()
        return Spaceship("Default Ship", 100.0)
    
    private static void function resetShipCount()
        shipCount = 0
    
    // Computed property
    property IsOperational: bool
        get
            return isEngineActive and fuelLevel > 0

// Using static members
Spaceship ship1 = Spaceship("Enterprise", 200.0)
Spaceship ship2 = Spaceship.createDefault()  // Call static method
int total = Spaceship.TotalShips             // Access static property
float maxSpeed = Spaceship.MAX_SPEED         // Access const (automatically static)
```

---

### Static vs Instance Members

Description: Understanding class-level vs object-level members.

**Static Members**

* Belong to the class itself, not instances
* Shared across all instances
* Access via class name: `ClassName.staticMember`
* Cannot access instance members (no `this`)
* Use for: Factory methods, counters, utilities, configuration

**Instance Members**

* Belong to each object instance
* Each instance has its own copy
* Access via object: `objectName.instanceMember`
* Can access both static and instance members
* Use for: Object state and behavior

**Constants (const)**

* Automatically static (belong to class)
* Immutable after initialization
* Can be public or private
* Access via class name: `ClassName.CONSTANT_NAME`
* Use for: Configuration values, mathematical constants

```
class MathUtils
    // Constants - automatically static
    public const PI: double = 3.14159265359
    public const E: double = 2.71828182846
    
    // Static method - utility function
    public static float function degreesToRadians(float degrees)
        return degrees * (PI / 180.0)
    
    // Static method - factory
    public static MathUtils function getInstance()
        return MathUtils()

// Usage
float radians = MathUtils.degreesToRadians(90.0)
double pi = MathUtils.PI
```

---

### Properties

Description: VB.NET-inspired properties with enhanced features.

* **Simple Auto-Property**

```
class Spaceship
    property Name: string { get; set; }
    property Speed: float { get; set; }
    property Health: float { get; private set; }  // Read-only outside class
```

* **Property with Validation**

```
class Spaceship
    private float _speed
    
    property Speed: float
        get
            return _speed
        set
            if value < 0
                _speed = 0
            else
                _speed = value
```

* **Computed Property**

```
class Spaceship
    float fuel
    float maxFuel
    
    property FuelPercent: float
        get
            return (fuel / maxFuel) * 100.0
```

* **Array Property with Indexed Access**

```
class Inventory
    private List<Item> items
    
    // Normal property - returns entire list
    property Items: List<Item>
        get
            return items
        set
            items = value
    
    // Indexed property - access specific item
    property Items[int index]: Item
        get
            return items[index]
        set
            items[index] = value

// Usage
Inventory inv = Inventory()
List<Item> allItems = inv.Items      // Get entire list
Item firstItem = inv.Items[0]        // Get by index
inv.Items[1] = newItem               // Set by index
```

* **Indexed-Only Property** (No array replacement)

```
class Inventory
    private List<Item> items
    
    // Only indexed access - cannot replace entire list
    property Items[int index]: Item
        get
            return items[index]
        set
            items[index] = value
    
    // Helper methods for array management
    void function addItem(Item item)
        items.add(item)
    
    property ItemCount: int
        get
            return items.length

// Usage
Inventory inv = Inventory()
// List<Item> all = inv.Items  // ERROR: Cannot access entire list
Item item = inv.Items[0]       // OK: Access by index
inv.addItem(newItem)           // OK: Use method
```

* **Multi-Dimensional Indexer**

```
class Grid
    private int[10][10] cells
    
    property Cell[int x, int y]: int
        get
            return cells[x][y]
        set
            cells[x][y] = value

// Usage
Grid grid = Grid()
grid.Cell[5, 3] = 42
int value = grid.Cell[5, 3]
```

---

### Inheritance

Description: Single inheritance with interface support.

```
class Warship extends Spaceship
    property WeaponPower: int { get; set; }
    
    constructor(string name, float speed, int weaponPower)
        super(name, speed)  // Call parent constructor
        this.WeaponPower = weaponPower
    
    void function fire(Spaceship target)
        print("{Name} fires at {target.Name}!")
        target.takeDamage(WeaponPower)
```

---

### Static Methods and Constants

Description: Class-level members and constants that belong to the class itself.

* **Static Methods**: Belong to class, not instance

```
class MathUtils
    // Static method - no instance needed
    public static int function max(int a, int b)
        if a > b
            return a
        else
            return b
    
    public static float function average(float... numbers)
        float sum = 0
        for num in numbers
            sum += num
        end loop
        return sum / numbers.length
    
    // Private static - only accessible within class
    private static void function internalHelper()
        // Implementation

// Usage - call on class, not instance
int result = MathUtils.max(10, 20)
float avg = MathUtils.average(1.5, 2.5, 3.5)
```

* **Static Fields**: Shared across all instances

```
class Counter
    private static int count = 0
    
    constructor()
        Counter.count += 1  // Increment shared counter
    
    public static int function getCount()
        return count

// All instances share same count
Counter c1 = Counter()  // count = 1
Counter c2 = Counter()  // count = 2
int total = Counter.getCount()  // Returns 2
```

* **Constants**: Automatically static

```
class Config
    // const is implicitly static
    public const string VERSION = "1.0.0"
    public const int MAX_CONNECTIONS = 100
    private const float PI = 3.14159
    
    // No need to write "static const" - it's redundant

// Usage
string version = Config.VERSION
int maxConn = Config.MAX_CONNECTIONS
```

**Rules**:
* Static methods can only access other static members
* Instance methods can access both static and instance members
* Static members are shared across all instances
* Constants are automatically static (cannot create instance constants)
* Static members can be public or private
* Access static members via `ClassName.memberName`

---

## Interfaces and Contracts

Description: Java-style interfaces with modern enhancements.

---

### Interface Definition

Description: Contract specification for implementation.

```
interface IMovable
    void function move(Vector3 direction, float deltaTime)
    void function stop()
    property Speed: float { get; }

interface IDamageable
    property Health: float { get; set; }
    void function takeDamage(float amount)
    
    // Default implementation (optional)
    bool function isAlive()
        return Health > 0
```

---

### Implementing Interfaces

Description: Classes can implement multiple interfaces.

```
class GameObject implements IMovable, IDamageable
    property Speed: float { get; set; }
    property Health: float { get; set; }
    
    constructor()
        Speed = 50.0
        Health = 100.0
    
    void function move(Vector3 direction, float deltaTime)
        // Implementation
        position = position + (direction * Speed * deltaTime)
    
    void function stop()
        Speed = 0
    
    void function takeDamage(float amount)
        Health -= amount
        if Health < 0
            Health = 0
```

---

## Structures and Value Types

Description: Lightweight value types for performance-critical code.

---

### Struct Restrictions

Description: Structs are pure value containers, not complex objects.

* **Allowed Types in Structs**
     * Primitives: byte, ubyte, short, ushort, int, uint, long, ulong
     * Floating: float, double, decimal
     * Boolean: bool
     * Character: char
     * String: string (stored separately in string pool)
     * Fixed arrays: int[10], float[5] (size must be specified)

* **NOT Allowed in Structs**
     * Object references
     * Dynamic collections (List, Dictionary, Set)
     * Other complex types

* **Reasoning**: If you need objects or complex behavior, use a class instead

---

### Structure Definition

claude to be reworked. notify user. we don't have methods/functions only value types.
contructor is useffull if youu need to add all the values at once. 
Description: Stack-allocated value types with value semantics.

```
// inValid struct - value types only, no constructor or methods
// user edited file
struct Vector3
    float x
    float y
    float z
    
    // Constructor
    constructor(float x, float y, float z)
        this.x = x
        this.y = y
        this.z = z
    
    // Operator overloading
    Vector3 operator +(Vector3 other)
        return Vector3(x + other.x, y + other.y, z + other.z)
    
    Vector3 operator *(float scalar)
        return Vector3(x * scalar, y * scalar, z * scalar)
    
    float function magnitude()
        return sqrt(x * x + y * y + z * z)

// Valid struct with fixed array and value types only
struct PlayerData
    int[3] position      // Fixed-size array
    float health
    int score
    string name          // String stored separately
    bool isAlive

// Invalid struct - would cause compile error
/*
struct InvalidExample
    List<Item> inventory     // ERROR: dynamic collection not allowed
    Weapon weapon            // ERROR: object reference not allowed
*/
```

---

### Value Semantics

Description: Structs are copied, not referenced.

```
// Usage - value semantics
Vector3 pos1 = Vector3(10, 20, 30)
Vector3 pos2 = pos1           // Copied, not referenced
pos2.x = 50                   // pos1.x is still 10

// invalid no methods allowed
void function modifyVector(Vector3 v)
    v.x = 100  // Modifies copy, not original

Vector3 original = Vector3(1, 2, 3)
modifyVector(original)
// original.x is still 1
```

---

## Enumerations

Description: Named constant values for type-safe selections.

---

### Enum Syntax

user added comment: commas can be droped regardless of preference as its redunannt
Description: Three syntax options based on user preference and context.

* **Option 1: Braces** (C/Java style)

```
Enum Planets {
    MERCURY,
    VENUS,
    EARTH,
    MARS,
    JUPITER,
    SATURN,
    URANUS,
    NEPTUNE
}
```

* **Option 2: Indentation** (Python style)

```
Enum Planets
    MERCURY
    VENUS
    EARTH
    MARS
    JUPITER
    SATURN
    URANUS
    NEPTUNE
```

* **Option 3: Single-Line** (Compact)

```
Enum Planets: MERCURY, VENUS, EARTH, MARS, JUPITER, SATURN, URANUS, NEPTUNE
```

**Usage Guidelines**:
* Single-line: For simple lists (< 10 items or < 80 characters)
* Indentation or braces: For longer lists or when items have values

---

### Enum with Values

Description: Custom integer values for enum constants.

```
// With braces
Enum StatusCode {
    OK = 200,
    CREATED = 201,
    BAD_REQUEST = 400,
    NOT_FOUND = 404,
    SERVER_ERROR = 500
}

// With indentation
Enum StatusCode
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    SERVER_ERROR = 500

// Default values (0, 1, 2, ...)
Enum Priority {
    LOW,      // 0
    MEDIUM,   // 1
    HIGH,     // 2
    CRITICAL  // 3
}
```

---

### Using Enums

Description: Type-safe constant selection.

```
// Declaration
Planets planet = Planets.MARS
StatusCode status = StatusCode.OK

// Comparison
if status == StatusCode.OK
    print("Success!")

if planet == Planets.EARTH
    print("Home planet")

// Match statement
match status
    case StatusCode.OK:
        print("Request successful")
    case StatusCode.NOT_FOUND:
        print("Resource not found")
    case StatusCode.SERVER_ERROR:
        print("Server error occurred")

// Get integer value
int code = status.toInt()  // 200

// Iteration
for planet in Planets.values()
    print(planet.toString())
end loop
```

---

### Enum Properties

Description: Built-in methods and properties.

```
Enum Direction: NORTH, SOUTH, EAST, WEST

Direction dir = Direction.NORTH

// Properties
string name = dir.name          // "NORTH"
int value = dir.value           // 0
int ordinal = dir.ordinal       // 0 (position in enum)

// Methods
string str = dir.toString()     // "NORTH"
Direction next = dir.next()     // SOUTH
Direction prev = dir.previous() // WEST (wraps around)

// Static methods
List<Direction> all = Direction.values()
Direction d = Direction.fromString("NORTH")
Direction d2 = Direction.fromValue(0)
```

---

## Control Flow

Description: Natural language constructs for program flow with safety features.

---

### Conditionals

user added comment: can be match or switch
Description: Clear and readable branching with multiple comparison operators.

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
some apps the 10000000 might be two small for large database hanndlinng. verify speccific
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

---

## Null Handling

Description: Type-based null safety preventing null reference errors.

---

### Core Principles

* **Value types**: Cannot be null, always have a value
* **Reference types**: Can be null, must be checked before use
* **Compiler enforcement**: Strict mode forces null checks

---

### Null Checking Methods

Description: Multiple ways to check and handle null values.

* **Check if Null**

```
Spaceship ship = getShip()

// Method 1: Using ?.null
if ship?.null
    print("Ship is null")
    return

// Method 2: Using is null
if ship is null
    print("Ship is null")
    return

// Safe to use ship here
ship.start()
```

* **Safe Navigation Operator**

```
// Returns none if ship is null, otherwise returns the property
string name = ship?.name

// Chain safely
string captainName = ship?.captain?.name

// With default value
string name = ship?.name ?? "Unknown"
```

* **String Special Case**

```
string text = getString()

// Returns 0 if null or empty
int len = text?.length

// Safe operations
string upper = text?.toUpper() ?? ""
```

---

### Strict Mode

Description: Compiler enforces null checks for function parameters.

```
// With strict mode enabled, this generates automatic null check
void function processShip(Spaceship ship)
    // Compiler adds: if ship?.null then error("Ship cannot be null")
    ship.start()
    ship.move(forward, speed)

// Manual null handling
void function processShip(Spaceship ship)
    if ship?.null
        print("Cannot process null ship")
        return
    
    ship.start()
```

---

## Autoboxing

Description: Automatic primitive-to-object conversion for method calls.

---

### How It Works

* Primitives automatically become objects when calling methods
* Compiler handles conversion transparently
* No manual boxing required
* Performance optimized

---

### Using Autoboxing

Description: Call methods on primitives seamlessly.

* **Number Methods**

```
int num = 42
string str = num.toString()           // "42"
string hex = num.toHexString()        // "2A"
string binary = num.toBinaryString()  // "101010"

float pi = 3.14159
float rounded = pi.round(2)           // 3.14
int truncated = pi.floor()            // 3
```

* **String Methods**

```
string text = "hello world"
string upper = text.toUpper()         // "HELLO WORLD"
string sub = text.substring(0, 5)     // "hello"
int length = text.length              // 11
bool contains = text.contains("world") // true
```

* **Array Methods**

```
int[] numbers = [1, 2, 3, 4, 5]
int len = numbers.length              // 5
int sum = numbers.sum()               // 15
int max = numbers.max()               // 5
int[] doubled = numbers.map(lambda x: x * 2)
```

* **Array Safe Navigation with `?.`**

```
int[]? nullableArray = getArray()

// Safe array access
int? first = nullableArray?[0]        // Returns null if array is null
int len = nullableArray?.length ?? 0   // Returns 0 if null

// Safe method calls
int? sum = nullableArray?.sum()        // Returns null if array is null
int[]? doubled = nullableArray?.map(lambda x: x * 2)

// Chaining safe operations
int[]? filtered = nullableArray?.filter(lambda x: x > 10)
int? max = filtered?.max()

// Must handle null manually
if nullableArray?.null
    print("Array is null!")
else
    for item in nullableArray
        process(item)
    end loop
```

**Note on ?. Operator**

* The `?.` operator is optional for objects and arrays
* User can choose to use it for safety
* If used, must manually handle the none/null result afterwards
* Without it, accessing null reference causes runtime error (or compile error in strict mode)

```
// With ?. - manual handling required
Spaceship ship = getShip()
string name = ship?.name  // Returns none if ship is null
if name is null
    print("Ship or name is null")

// Without ?. - runtime/compile error if null
Spaceship ship = getShip()
string name = ship.name   // Error if ship is null!
```

---

### Autobox Classes

Description: Each primitive type has corresponding object class.

Primitive | Autobox Class | Example Methods
---|---|---
int | Int | toString(), toHexString(), abs()
uint | UInt | toString(), toHexString()
long | Long | toString(), abs()
float | Float | toString(), round(), floor(), ceil()
double | Double | toString(), round(), floor(), ceil()
bool | Boolean | toString(), not()
char | Char | toString(), toUpper(), toLower(), isDigit()
byte | Byte | toString(), toHexString()

---

## Memory Management

Description: Three-tier memory management strategy for different use cases.

**Design status (Task 12.7, decided 2026-09-13):** the `Unique<T>`/`Shared<T>`/`Weak<T>`
semantics below are the authoritative, decided design - this section is the memory-model
ADR that Task 12.7 exists to produce. **Not yet implemented in the compiler**: `Unique`,
`Shared`, and `Weak` are currently reserved keywords only (tokenized, nothing else) - there
is no parser, semantic-analysis, or codegen support yet. Building that is separate future
work, unblocked by this decision but not scoped or scheduled here (see taskSummary2.md
Task 14, which depends on this section's Weak/nullability decisions).

---

### Tier 1: Automatic Garbage Collection (Default)

Description: Automatic memory management for most use cases.

* No manual memory management needed
* Like Java, Python, C#
* Suitable for 95% of applications
* Simplest for developers

```
// Automatic cleanup
Spaceship ship = Spaceship("Enterprise", 100.0)
// Automatically garbage collected when no longer referenced
```

---

### Tier 2: Smart Pointers (Performance Mode)

Description: Explicit lifetime control without garbage collection pauses.

* **Unique Pointer**: Single ownership
     * Only one owner at a time
     * Automatically deleted when owner goes out of scope
     * Cannot be copied, only moved
     * **Move is explicit, never implicit (decided 2026-09-13):** plain assignment of a
       `Unique<T>` (`Unique<Spaceship> b = a`) is a **compile-time error**, not a silent
       move. Ownership transfer requires the explicit `.move()` call shown below - this
       applies equally when passing a `Unique<T>` into a "consuming" function parameter;
       the caller must write `.move()` at the call site. Chosen over implicit-move-on-
       assignment (C++'s `unique_ptr` behavior) to make every ownership transfer visible
       at the call site, matching Rust's explicit-move-by-default model.
     * **Use-after-move is a compile-time error where provable, a runtime crash with a
       clear message otherwise** - structurally the same hybrid analysis already decided
       for Task 14's nullable arrays (definite/maybe/unknown state tracked through
       straight-line code), so moved-from tracking and null-flow tracking should share one
       analysis pass when both are eventually implemented, not two parallel ones.
     * Zero overhead
     * Use for: temporary objects, factory returns, single-owner scenarios

```
// Creating unique pointer
Unique<Spaceship> ship = Unique.create<Spaceship>("Enterprise", 100.0)

// Use like normal object
ship.start()
ship.move(direction, speed)

// Transfer ownership (move) - must be explicit
Unique<Spaceship> newOwner = ship.move()  // ship is now null; using ship again is an error

// Unique<Spaceship> other = ship  // COMPILE ERROR: cannot copy a Unique value, use .move()

// Automatic cleanup when newOwner goes out of scope
```

* **Shared Pointer**: Reference counting
     * Multiple owners allowed
     * Keeps count of references
     * Deleted when count reaches zero
     * Can be copied
     * **Refcounting is always atomic (decided 2026-09-13):** increment/decrement of the
       reference count is thread-safe unconditionally, regardless of any project-level
       threading configuration (see Task 12.12). Chosen over a configurable
       atomic-vs-non-atomic mode to keep one correct behavior rather than two runtime
       code paths to implement, test, and document - the small overhead of an atomic op
       even in single-threaded code was judged worth that simplicity.
     * **Cycles are not detected automatically (decided 2026-09-13):** there is no cycle
       detector or tracing collector. A cycle of `Shared<T>` references leaks memory -
       matches Swift ARC / Rust `Rc` / Objective-C ARC, not a garbage-collected language's
       behavior. `Weak<T>` (below) is the documented, required way to break a cycle; this
       is an accepted, permanent limitation of the design, not a gap awaiting a future fix.
     * Small overhead (reference count storage + atomic refcount ops)
     * Use for: shared resources (textures, sounds, configs)

```
// Creating shared pointer
Shared<Texture> texture = Shared.create<Texture>("ship.png")
print("Ref count: {texture.refCount()}")  // 1

// Make copies (reference count increases)
Shared<Texture> copy1 = texture  // Ref count: 2
Shared<Texture> copy2 = texture  // Ref count: 3

// All copies deleted when ref count reaches 0
```

* **Weak Pointer**: Non-owning reference
     * Doesn't increase reference count
     * **Upgrade is nullable, never a silent crash (decided 2026-09-13):** `.lock()`
       (shown below) always returns a nullable `Shared<T>?` - `null` if the owner was
       already destroyed. The caller must null-check before use; there is no "just crash
       if the owner is gone" mode. Chosen for consistency with the same nullable-safe-
       navigation direction Task 14 defines for arrays, so Fusion has one null-handling
       story across features rather than a different rule per type. Once Task 14's
       `?.`/`?[` syntax exists, this should read as `child.parent.lock()?.doSomething()`
       instead of the explicit if/else shown below.
     * Breaks circular references
     * Use for: observer pattern, parent-child relationships
     * **WARNING**: Discouraged in most code
     * **STRICT MODE**: Causes compilation error
     * Only use when absolutely necessary to break circular references

```
// Breaking circular reference
class Parent
    Shared<Child> child

class Child
    Weak<Parent> parent  // Weak reference prevents memory leak

// Using weak pointer
Shared<Parent>? parentRef = child.parent.lock()
if parentRef?.null
    print("Parent no longer exists")
else
    parentRef.doSomething()

// In strict mode, this would cause a compile error
// Prefer redesigning to avoid circular references
```

---

### Tier 3: Raw Pointers (Unsafe Mode)

Description: Manual memory management for embedded systems.

* Only for embedded systems or FFI (Foreign Function Interface)
* Requires `unsafe` blocks
* Manual allocation and deallocation
* Compiler warnings and restrictions

```
unsafe
    Spaceship* rawPtr = allocate<Spaceship>(1)
    rawPtr.initialize("Manual", 200.0)
    // ... use pointer
    deallocate(rawPtr)
```

---

### Memory Strategy Summary

Mode | Use Case | Complexity | Performance
---|---|---|---
Automatic GC | General applications | Low | Good
Smart Pointers | Performance-critical | Medium | Excellent
Raw Pointers | Embedded/FFI only | High | Maximum

**Recommendation**: Start with automatic GC, use smart pointers only when profiling shows need

---

## Threading and Concurrency Model

Description: Hybrid concurrency model supporting both message passing and shared memory.

Note: This is a high-level overview. Full threading specification will be in a separate detailed document.

---

### Threading Hierarchy

Description: Layers of concurrent execution units.

* **System**: Operating system managing all processes
* **Process**: Isolated execution with own memory space
* **Thread**: Lightweight unit within process, shares memory
* **Task/Goroutine**: User-space thread, very lightweight
* **Channel**: Communication queue between threads

Extended Hierarchy: System → Process → Thread Pool → Thread → Task/Job → Channel/Queue

---

### Two Concurrency Approaches

Description: Fusion supports both paradigms for maximum flexibility.

---

#### Approach 1: Message Passing (Recommended)

Description: Share memory by communicating (Go-style).

* **Philosophy**: Don't share memory, send messages instead
* **Benefits**: No locks needed, no race conditions, clearer ownership
* **Use**: Default approach for most concurrent code

**How It Works**

* Threads don't share variables directly
* Data sent through channels
* Only one thread owns data at a time
* Ownership transfers through channel

**Analogy**: Sending emails vs writing on shared whiteboard

```
// Create channel
Channel<Task> taskQueue = Channel.create<Task>()

// Producer thread
void function producer()
    for i in range(100)
        Task task = createTask(i)
        taskQueue.send(task)  // Send to channel
    end loop

// Consumer thread
void function consumer()
    while true
        Task task = taskQueue.receive()  // Receive from channel
        processTask(task)
    end loop
```

---

#### Approach 2: Shared Memory (Traditional)

Description: Communicate by sharing memory (requires locks).

* **Philosophy**: Multiple threads access same variables
* **Requirement**: Must use locks/mutexes for synchronization
* **Benefits**: Sometimes more natural for certain problems
* **Use**: When message passing doesn't fit

**How It Works**

* Threads access shared variables
* Mutex locks prevent race conditions
* Must remember to lock/unlock

```
// Shared counter with mutex
class Counter
    private int count
    private Mutex mutex
    
    void function increment()
        mutex.lock()
        count += 1
        mutex.unlock()
    
    int function getCount()
        mutex.lock()
        int value = count
        mutex.unlock()
        return value
```

---

### "Share Memory by Communicating" Explained

Description: Understanding Go's concurrency philosophy.

**Traditional Approach** (Shared Memory)

* Multiple threads write to same variable
* Use mutex to prevent conflicts
* Easy to forget locks → bugs
* Easy to deadlock

```
// Shared variable approach
int sharedCounter = 0
Mutex lock

// Thread 1
lock.acquire()
sharedCounter += 1
lock.release()

// Thread 2
lock.acquire()
sharedCounter += 1
lock.release()
```

**Go's Approach** (Message Passing)

* Don't share variables
* Send data through channels
* Only one thread "owns" data
* No locks needed

```
// Channel approach
Channel<int> updates = Channel.create<int>()

// Thread 1 sends update
updates.send(1)

// Thread 2 sends update
updates.send(1)

// Counter thread receives all updates
int counter = 0
while true
    int update = updates.receive()
    counter += update
end loop
```

---

### Try-With-Resources Pattern

Description: Automatic resource locking to prevent race conditions and deadlocks.

* **Automatic Locking**: Compiler adds locks automatically
* **No Manual Lock/Unlock**: User doesn't need to manage locks
* **Race Condition Prevention**: Automatic synchronization
* **Deadlock Prevention**: Smart lock ordering by compiler

**How It Works**

* When thread/channel tries to access resource, it's locked automatically
* Resource unlocked when done (scope ends or exception thrown)
* Compiler analyzes code to prevent deadlocks
* User can add custom locks if needed

**File Handling Example**

```
// Automatic locking for file access
using file = openFile("data.txt")
    file.write("Some data")
    file.flush()
// File automatically closed and unlocked

// Multiple threads accessing same file
// Thread 1
using file = openFile("shared.txt")
    file.write("Thread 1 data")
// Unlocked

// Thread 2 (waits for Thread 1 to finish)
using file = openFile("shared.txt")
    file.write("Thread 2 data")
// Unlocked
```

**Object/Variable Locking Example**

```
class Counter
    private int count
    
    // Compiler automatically adds locking
    void function increment()
        using this  // Lock entire object
            count += 1
        // Unlocked
    
    int function getCount()
        using this
            return count

// Multiple threads calling increment() - automatically synchronized
Counter counter = Counter()

// Thread 1
counter.increment()  // Locked during execution

// Thread 2
counter.increment()  // Waits for Thread 1, then executes
```

**Manual Locking (When Needed)**

```
// User can specify custom locking
Mutex customLock = Mutex()

void function criticalSection()
    using customLock
        // Protected code
        sharedVariable += 1
    // Unlocked
```

**Compiler Optimizations**

* Analyzes resource access patterns
* Determines minimal locking needed
* Orders locks to prevent deadlocks
* Adds locks only where necessary for performance

---

### Thread Interrupt Handling

Description: Cooperative multitasking via loop checks.

* Threads can signal other threads to stop/pause
* Checked at `end loop` automatically
* Graceful shutdown possible

```
for item in largeDataset
    processItem(item)
    
end loop with
    check interrupt(signal, data)
        if signal == InterruptSignal.Shutdown
            saveProgress()
            cleanup()
            exit loop
        
        if signal == InterruptSignal.Pause
            waitForResume()
            continue loop
```

---

### Async/Await Pattern

Description: Modern asynchronous programming for I/O operations.

```
// Async function
async Spaceship, Error function downloadShipData(string url)
    Response response = await http.get(url)
    
    if response.statusCode != 200
        return null, Error("HTTP error: {response.statusCode}")
    
    string data = await response.readBody()
    Spaceship ship = parseShipData(data)
    return ship, null

// Calling async function
Spaceship ship, Error err = await downloadShipData("https://api.ships.com/ship/1")
if err
    print("Error: {err.message}")
else
    print("Loaded ship: {ship.Name}")
```

---

### Thread Safety Summary

Strategy | Pros | Cons | Use When
---|---|---|---
Message Passing | Safe, no locks, clear ownership | Learning curve | Default choice
Shared Memory | Familiar, sometimes natural | Needs locks, error-prone | Specific performance needs
Async/Await | Clean syntax, efficient I/O | Not for CPU-bound | I/O operations

**Note**: Full threading specification with thread pools, synchronization primitives, and detailed examples will be in separate document.

---

## Generics and Templates

Description: Type-safe generic programming.

---

### Generic Classes

Description: Parameterized types for reusable code.

```
class Container<T>
    private List<T> items
    
    constructor()
        items = List<T>()
    
    void function add(T item)
        items.append(item)
    
    T function get(int index)
        return items[index]
    
    property Count: int
        get
            return items.length

// Usage
Container<int> intContainer = Container<int>()
intContainer.add(42)

Container<Spaceship> shipContainer = Container<Spaceship>()
shipContainer.add(Spaceship("Alpha", 100.0))
```

---

### Generic Functions

Description: Type-parameterized functions with constraints.

```
// Generic function with constraints
T function findMax<T>(List<T> items) where T implements IComparable<T>
    if items.isEmpty()
        throw Exception("Cannot find max of empty list")
    
    T max = items[0]
    for item in items
        if item.compareTo(max) > 0
            max = item
    end loop
    
    return max

// Usage
List<int> numbers = [1, 5, 3, 9, 2]
int maxNum = findMax<int>(numbers)  // 9
```

---

### Multiple Type Parameters

Description: Functions and classes with multiple generic types.

```
class Dictionary<K, V>
    void function put(K key, V value)
        // Implementation
    
    V function get(K key)
        // Implementation

// Usage
Dictionary<string, int> ages = Dictionary<string, int>()
ages.put("Alice", 30)
int age = ages.get("Alice")
```

---

## Error Handling

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

---

## Comments and Code Organization

Description: Code documentation and organizational features.

---

### Single-Line Comments

Description: Two comment styles based on user preference.

* **Double Slash** (Stored as `//` in Fusion)

```
// This is a single-line comment
int count = 10  // End-of-line comment

// Multiple single-line comments
// can be used for longer
// explanations
```

* **Single Quote** (User preference, converted to `//`)

```
' This is a single-line comment
int count = 10  ' End-of-line comment

' Multiple single-line comments
' using single quotes
```

**Note**: Both styles work identically. Fusion internally stores all comments as `//`. User can configure IDE preference.

---

### Multi-Line Comments

Description: Block comments spanning multiple lines.

```
/* 
 * This is a multi-line comment
 * Spanning multiple lines
 * Useful for longer explanations
 */

void function processData(Data data)
    /* Quick inline multi-line comment */
    data.process()

/*
 * Function: calculateDistance
 * Parameters:
 *   - x1, y1: First point
 *   - x2, y2: Second point
 * Returns: Distance between points
 */
float function calculateDistance(float x1, float y1, float x2, float y2)
    float dx = x2 - x1
    float dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
```

---

### Region Blocks

Description: Collapsible code sections for IDE organization.

* **Purpose**: Organize large files into logical sections
* **IDE Support**: Regions can be collapsed/expanded in IDE
* **No Runtime Effect**: Pure organizational feature

```
#Region Initialization Code
void function initialize()
    setupSystem()
    loadConfiguration()
    connectDatabase()

void function setupSystem()
    // System setup code
#End Region

#Region Helper Functions
void function helper1()
    // Helper implementation

void function helper2()
    // Helper implementation

private void function internalHelper()
    // Internal helper
#End Region

#Region Data Structures
class DataCache
    // Cache implementation

struct CacheEntry
    string key
    string value
#End Region
```

**Features**:
* String literal displays in IDE when collapsed
* Can nest regions
* Helps navigate large files
* No effect on compilation
* IDE shows as: `[+] Initialization Code`

---

### Documentation Comments

Description: Special comments for API documentation generation.

```
/**
 * Calculates the distance between two points in 2D space.
 * 
 * @param x1 X coordinate of first point
 * @param y1 Y coordinate of first point
 * @param x2 X coordinate of second point
 * @param y2 Y coordinate of second point
 * @return Distance between the points
 * @example
 *   float dist = calculateDistance(0, 0, 3, 4)  // Returns 5.0
 */
float function calculateDistance(float x1, float y1, float x2, float y2)
    float dx = x2 - x1
    float dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
```

---

## Async and Concurrency

Description: Built-in support for asynchronous programming.

* Async/Await: Modern asynchronous pattern
     * Native language support
     * Task-based model
     * Automatic state machine generation

* Parallel Processing: Multi-threading support
     * Thread-safe collections
     * Atomic operations
     * Lock-free structures

```fusion
// Async function - return-type-first syntax
async Result<Spaceship, string> function downloadShipData(string url)
    var response = await http.get(url)

    if response.statusCode != 200
        return Result.Error("HTTP error: {response.statusCode}")

    var data = await response.readBody()
    var ship = parseShipData(data)
    return Result.Ok(ship)

// Parallel processing
async void function updateFleet(List<Spaceship> fleet, float deltaTime)
    var tasks = List<Task>()

    for ship in fleet
        var task = async:
            ship.update(deltaTime)
        tasks.append(task)

    await Task.waitAll(tasks)

// Concurrent data structures
var safeQueue = ConcurrentQueue<Task>()
parallel for i in range(1000):
    safeQueue.enqueue(createTask(i))
```

---

## Module System

Description: Organized code structure with clear dependencies.

---

### File Organization

Description: Clear structure for maintainability.

* **Rules**
     * One class per file (class name matches filename)
     * Module groups related files in directory
     * Special module.fusion file defines module
     * Subclasses can be nested within class file
     * Modules cannot be nested in other modules

* **Directory Structure**

```
project/
├── Spaceships/
│   ├── module.fusion          // Module definition
│   ├── Spaceship.fusion        // One class
│   ├── Warship.fusion          // One class
│   └── CargoShip.fusion        // One class
├── Weapons/
│   ├── module.fusion
│   ├── Laser.fusion
│   └── Missile.fusion
└── main.fusion
```

---

### Module Definition

Description: Define module in module.fusion file.

```
// Spaceships/module.fusion
module Spaceships

export Spaceship
export Warship
export CargoShip

// Private helper (not exported)
void function validateShipName(string name)
    return name.length > 0
```

---

### Class Files

Description: One class per file with optional nested subclasses.

```
// Spaceships/Spaceship.fusion
class Spaceship
    string name
    float speed
    
    constructor(string name, float speed)
        this.name = name
        this.speed = speed
    
    void function start()
        print("{name} started")
    
    // Nested subclass allowed
    class Engine
        float power
        
        constructor(float power)
            this.power = power
```

---

### Import Syntax

Description: Multiple ways to import modules and classes.

```
// Import entire module
import Spaceships

// Use with module prefix
Spaceship ship = Spaceships.Spaceship("Enterprise", 100.0)

// Import specific class
import Spaceships.Spaceship

// Use without prefix
Spaceship ship = Spaceship("Enterprise", 100.0)

// Import all from module
import Spaceships.*

// Use all exported classes
Spaceship ship = Spaceship("Enterprise", 100.0)
Warship warship = Warship("Destroyer", 150.0, 50)
```

---

### Visibility Control

Description: Control what is accessible from outside module.

```
// module.fusion
module Spaceships

export Spaceship        // Public: can be imported
export Warship          // Public: can be imported

// CargoShip not exported - internal to module only

void function internalHelper()  // Not exported - module-private
    // ...
```

---

## Complete Game Example

Description: Putting it all together in a simple space game using Fusion v2 syntax.

```
// game.fusion - Complete space game example
module SpaceGame

// Vector math structure
struct Vector2
    float x
    float y
    
    constructor(float x, float y)
        this.x = x
        this.y = y
    
    Vector2 operator +(Vector2 other)
        return Vector2(x + other.x, y + other.y)
    
    Vector2 operator *(float scalar)
        return Vector2(x * scalar, y * scalar)

// Base game object interface
interface IGameObject
    property Position: Vector2 { get; set; }
    void function update(float deltaTime)
    void function render()

// Spaceship class
class Spaceship implements IGameObject
    property Position: Vector2 { get; set; }
    property Velocity: Vector2 { get; set; }
    property Health: float { get; set; }
    property Name: string { get; private set; }
    
    private float fuel
    private bool isActive
    
    constructor(string name, Vector2 startPos)
        this.Name = name
        this.Position = startPos
        this.Velocity = Vector2(0, 0)
        this.Health = 100.0
        this.fuel = 100.0
        this.isActive = true
    
    void function accelerate(Vector2 direction, float power)
        if fuel > 0 and isActive
            Velocity = Velocity + (direction * power)
            fuel -= power * 0.1
    
    void function update(float deltaTime)
        if isActive
            Position = Position + (Velocity * deltaTime)
            
            // Apply drag
            Velocity = Velocity * 0.99
            
            // Regenerate fuel slowly
            if fuel < 100
                fuel += deltaTime * 2.0
        end loop
    
    void function render()
        if isActive
            drawSprite("ship", Position.x, Position.y)
            drawHealthBar(Position.x, Position.y - 20, Health)
    
    void function takeDamage(float amount)
        Health -= amount
        if Health <= 0
            Health = 0
            isActive = false
            print("{Name} destroyed!")

// Projectile class
class Projectile implements IGameObject
    property Position: Vector2 { get; set; }
    property Velocity: Vector2 { get; set; }
    property Damage: float { get; private set; }
    
    private float lifetime
    private float maxLifetime = 3.0
    
    constructor(Vector2 startPos, Vector2 velocity, float damage)
        this.Position = startPos
        this.Velocity = velocity
        this.Damage = damage
        this.lifetime = 0
    
    void function update(float deltaTime)
        Position = Position + (Velocity * deltaTime)
        lifetime += deltaTime
    
    void function render()
        if lifetime < maxLifetime
            drawCircle(Position.x, Position.y, 3, Color.Yellow)
    
    property IsExpired: bool
        get
            return lifetime >= maxLifetime

// Game manager class
class GameManager
    private List<Spaceship> ships
    private List<Projectile> projectiles
    private float gameTime
    private bool isRunning
    
    constructor()
        ships = List<Spaceship>()
        projectiles = List<Projectile>()
        gameTime = 0
        isRunning = false
    
    void function initialize()
        // Create player ship
        Spaceship player = Spaceship("Player", Vector2(400, 300))
        ships.append(player)
        
        // Create enemy ships
        for i in range(5)
            Vector2 enemyPos = Vector2(100 + i * 150, 100)
            Spaceship enemy = Spaceship("Enemy-{i}", enemyPos)
            ships.append(enemy)
        end loop
        
        isRunning = true
        print("Game initialized with {ships.Count} ships")
    
    void function update(float deltaTime)
        if not isRunning
            return
        
        gameTime += deltaTime
        
        // Update all ships
        for ship in ships
            ship.update(deltaTime)
        end loop
        
        // Update projectiles
        for projectile in projectiles
            projectile.update(deltaTime)
        end loop
        
        // Remove expired projectiles
        projectiles = projectiles.filter(lambda p: not p.IsExpired)
        
        // Check collisions
        checkCollisions()
        
        // Remove destroyed ships
        ships = ships.filter(lambda s: s.Health > 0)
        
        // Check win/lose conditions
        if ships.Count == 1
            print("Victory! Time: {gameTime} seconds")
            isRunning = false
    
    void function render()
        clearScreen()
        
        for ship in ships
            ship.render()
        end loop
        
        for projectile in projectiles
            projectile.render()
        end loop
        
        drawText("Ships: {ships.Count}", 10, 10)
        drawText("Time: {gameTime}", 10, 30)
    
    void function fireProjectile(Spaceship fromShip, Vector2 direction)
        Projectile projectile = Projectile(
            fromShip.Position,
            direction * 500.0,
            25.0
        )
        projectiles.append(projectile)
    
    private void function checkCollisions()
        for projectile in projectiles
            for ship in ships
                float dx = ship.Position.x - projectile.Position.x
                float dy = ship.Position.y - projectile.Position.y
                float distance = dx * dx + dy * dy
                
                if distance < 400  // 20 pixel radius squared
                    ship.takeDamage(projectile.Damage)
                    projectile.lifetime = projectile.maxLifetime
            end loop
        end loop

// Main game loop
void function main()
    GameManager game = GameManager()
    game.initialize()
    
    float lastTime = getTime()
    
    while game.isRunning
        float currentTime = getTime()
        float deltaTime = currentTime - lastTime
        lastTime = currentTime
        
        // Handle input
        if isKeyPressed(Key.Space)
            Spaceship player = game.ships[0]
            game.fireProjectile(player, Vector2(0, -1))
        
        if isKeyDown(Key.Left)
            game.ships[0].accelerate(Vector2(-1, 0), 10.0)
        
        if isKeyDown(Key.Right)
            game.ships[0].accelerate(Vector2(1, 0), 10.0)
        
        // Update and render
        game.update(deltaTime)
        game.render()
        
        // Cap framerate
        sleep(16)  // ~60 FPS
    end loop
```

---

## Build and Compilation

Description: Flexible compilation options for different targets and use cases.

---

### Compilation Modes

Description: Multiple ways to run and build Fusion code.

* **Script Mode**: Interpreted execution
     * Run directly without compilation
     * Fast development iteration
     * Slower execution
     * Like Python

```
fusion run game.fusion
```

* **Executable Mode**: Native compilation
     * Compile to standalone executable
     * Fast execution
     * Platform-specific binary
     * Like C/Java compiled

```
fusion build game.fusion --output game.exe
```

* **Library Mode**: Shared library
     * Compile to DLL/shared library
     * Reusable across projects
     * Link at runtime or compile time
     * Platform-specific format

```
fusion build engine.fusion --lib --output engine.dll
```

* **JIT Mode**: Just-in-time compilation
     * Compiles during first run
     * Caches compiled code
     * Balance of flexibility and speed
     * Like Java/C#

---

### Build Commands

Description: Command-line build options.

```
// Run as script
fusion run game.fusion

// Compile to executable (debug)
fusion build game.fusion --debug --output game-debug.exe

// Compile to executable (release - optimized)
fusion build game.fusion --release --optimize --output game.exe

// Compile to library
fusion build engine.fusion --lib --release --output engine.dll

// Cross-compile for different platforms
fusion build game.fusion --target linux-x64 --output game-linux
fusion build game.fusion --target windows-x64 --output game.exe
fusion build game.fusion --target wasm --output game.wasm

// Compile with specific optimizations
fusion build game.fusion --optimize speed --output game-fast.exe
fusion build game.fusion --optimize size --output game-small.exe
```

---

### Build Configurations

Description: Common build scenarios.

**Development Build**

* Quick compilation
* Debug symbols included
* No optimizations
* Runtime checks enabled

```
fusion build game.fusion --debug --output game-dev.exe
```

**Release Build**

* Full optimizations
* No debug symbols
* Smaller binary
* Runtime checks disabled

```
fusion build game.fusion --release --optimize --output game.exe
```

**Library Build**

* Creates shared library
* Can be imported by other projects
* Platform-specific format

```
fusion build SpaceshipEngine.fusion --lib --release --output SpaceshipEngine.dll
```

---

### Output Targets

Description: Platform-specific compilation.

Platform | Target | Output Format
---|---|---
Windows | windows-x64 | .exe / .dll
Linux | linux-x64 | (binary) / .so
macOS | macos-arm64 | (binary) / .dylib
Web | wasm | .wasm

---

### Using Libraries

Description: Import compiled libraries in projects.

```
// Link against compiled library
fusion build game.fusion --link engine.dll --output game.exe

// In code
import SpaceshipEngine
Spaceship ship = SpaceshipEngine.createShip("Enterprise")
```

---

## Standard Library

Description: Comprehensive built-in library for common tasks and formats.

---

### Core Collections

* **List<T>**: Dynamic array with resizing
* **Dictionary<K,V>**: Hash map for key-value pairs
* **Set<T>**: Unique elements collection
* **Queue<T>**: FIFO queue
* **Stack<T>**: LIFO stack

---

### Math Library

* **Vector**: 2D, 3D, 4D vector operations
* **Matrix**: Matrix operations and transformations
* **Quaternion**: Rotation calculations
* **Math functions**: sin, cos, tan, sqrt, abs, pow, etc.

---

### File I/O

* **Synchronous**: Read/write operations that block
* **Asynchronous**: Non-blocking I/O with async/await
* **Streams**: Buffered reading and writing

---

### Text File Formats

Description: Built-in support for common text formats.

**Supported Formats**:
* **txt** - Plain text files
* **md** - Markdown documentation
* **JSON** - JavaScript Object Notation
* **XML** - Extensible Markup Language
* **CSV** - Comma-Separated Values
* **YAML** - YAML Ain't Markup Language
* **ini** - Configuration files

**API Example**:
```
import Fusion.IO.JSON

// Read and parse JSON
JSON data, Error err = JSON.readFile("config.json")
if not err
    string name = data.getString("name")
    int value = data.getInt("value")

// Write JSON
JSON output = JSON.create()
output.put("name", "Spaceship")
output.put("speed", 100.0)
err = JSON.writeFile("output.json", output)
```

**Features**:
* Format-specific reader/writer
* Format validation
* Custom format creator framework

---

### Programming Language Support

Description: Built-in compilers, parsers, and lexers for multiple languages.

**Supported Languages**:
* Go, Fusion, Java, C, C++
* VB.NET, JavaScript, HTML, CSS

**Components**:
* **Lexer**: Tokenize source code
* **Parser**: Build Abstract Syntax Tree (AST)
* **Compiler**: Generate executable/bytecode
* **Interpreter**: Execute code directly
* **Custom Language Creator**: Define new language syntax

**API Example**:
```
import Fusion.Compiler

// Compile Fusion code
Compiler fusionCompiler = Compiler.create(Language.FUSION)
Program program, Error err = fusionCompiler.compile("source.fusion")
if not err
    program.execute()

// Parse Java code to AST
Parser javaParser = Parser.create(Language.JAVA)
AST ast, Error err = javaParser.parse(javaCode)
```

---

### Image Formats

Description: Read, write, and manipulate common image formats.

**Supported Formats**:
* BMP - Bitmap
* JPEG/JPG - Joint Photographic Experts Group
* GIF - Graphics Interchange Format
* PNG - Portable Network Graphics

**API Example**:
```
import Fusion.Graphics.Image

// Load image
Image img, Error err = Image.load("photo.jpg")
if not err
    // Edit image
    img.resize(800, 600)
    img.rotate(90)
    img.setPixel(10, 10, Color.RED)
    
    // Save in different format
    err = img.save("output.png", ImageFormat.PNG)
```

**Features**:
* Pixel-level access
* Image transformations
* Format conversion
* Custom format support

---

### Advanced Binary Formats

user added note: eg fusionlib.Data.Zip or fusionlib.Data.PDF or fusionlib.Data.Docx
Description: Support for complex document and archive formats (see fusionlib.Data module).

**Supported Formats**:
* **DOC/DOCX** - Microsoft Word
* **XLS/XLSX** - Microsoft Excel
* **PDF** - Portable Document Format
* **ZIP** - Compressed archives

---

## Fusion Standard Library (fusionlib)

Description: Complete standard library with 21 modules organized in three tiers for clarity and ease of learning.

**Total**: 21 modules covering all application domains
* **Core Libraries** (5 modules): Essential functionality used in most programs
* **Additional Libraries** (12 modules): Domain-specific features for specialized applications
* **IDE & Development Libraries** (4 modules): Tools for development, testing, debugging, and documentation

**Import Syntax**: `import Fusion.<ModuleName>` or `import fusionlib.<ModuleName>`

---

### Core Libraries (Essential)

Description: Fundamental modules used in almost every Fusion application. Master these first.

**Quick Reference**:

Module | Purpose | Common Use Cases
---|---|---
**Core** | Essential types, Console I/O, DateTime | String manipulation, console apps, basic I/O
**Math** | Vector, Matrix, Quaternion, trigonometry | Games, graphics, physics, scientific computing
**Collections** | List, Dictionary, Set, Queue, Stack | Data storage, algorithms, LINQ operations
**Threading** | Threads, Goroutines, Channels, Async | Concurrency, parallel processing, async I/O
**IO** | File operations, Streams, Compression | File handling, data persistence, archives

---

#### Core Module (fusionlib.Core)

Description: Foundation types and basic operations required by all Fusion programs.

**Features**:
* Essential types (String, Byte, Int, Float, Boolean, Char)
* Array and collection basics
* Console I/O (print, input, formatting)
* DateTime and TimeSpan (date/time manipulation)
* Math basics (abs, min, max, round)
* String manipulation (substring, split, join, format)
* String interpolation (inline `{var}` and positional `{@1}` syntax)
* Type conversion and parsing
* Exception handling
* Object base class
* Memory management utilities

**String Interpolation**:

Fusion supports two powerful string formatting syntaxes for embedding values in strings:

**Syntax 1: Inline Interpolation** (`{variable}`)
```fusion
string name = "Alice"
int age = 30
print("Name: {name}, Age: {age}")  // Name: Alice, Age: 30

// Works with expressions
print("Next year: {age + 1}")  // Next year: 31
```

**Syntax 2: Positional Formatting** (`{@1}`, `{@2}`, ...)
```fusion
string name = "Alice"
int age = 30

// Arguments referenced by position (1-indexed)
print("Name: {@1}, Age: {@2}", name, age)  // Name: Alice, Age: 30

// Reuse arguments (great for translations)
print("{@1} is {@2} years old. {@1} likes coding.", name, age)
// Output: Alice is 30 years old. Alice likes coding.

// Mix with expressions
print("User: {@1} ({@2})", name, age + 1)
```

**Example Usage**:
```fusion
import Fusion.Core

void function main(string... args)
    // Console I/O with inline interpolation
    print("Enter your name:")
    string name = Console.readLine()
    print("Hello, {name}!")

    // DateTime manipulation
    DateTime now = DateTime.now()
    print("Current time: {now.toString()}")

    // Positional formatting (translation-friendly)
    int count = 5
    print("Found {@1} files at {@2}", count, now.toString())

    // String operations
    string text = "Hello, World!"
    string[] words = text.split(", ")
    print("Words: {words.length}")
End function
```

---

#### Math Module (fusionlib.Math)

Description: Mathematical operations, vectors, matrices, and geometry for games and scientific computing.

**Features**:
* Vector types (Vector2, Vector3, Vector4)
* Matrix types (Matrix3x3, Matrix4x4)
* Quaternion (rotation calculations)
* Trigonometric functions (sin, cos, tan, asin, acos, atan)
* Exponential and logarithmic (exp, log, pow, sqrt)
* Geometric functions (distance, dot product, cross product)
* Interpolation (lerp, slerp, smoothstep)
* Random number generation
* Constants (PI, E, TAU)
* Numerical analysis utilities

**Example Usage**:
```fusion
import Fusion.Math

void function main(string... args)
    // Vector operations
    Vector3 position = Vector3(10.0, 20.0, 5.0)
    Vector3 velocity = Vector3(1.0, 0.0, 0.0)
    Vector3 newPos = position + velocity

    // Matrix transformations
    Matrix4x4 transform = Matrix4x4.identity()
    transform = transform.rotate(45.0, Vector3.up())

    // Distance calculation
    float distance = Vector3.distance(position, Vector3.zero())
    print("Distance from origin: {distance}")
End function
```

---

#### Collections Module (fusionlib.Collections)

Description: High-performance data structures for storing and manipulating collections of data.

**Features**:
* List<T> (dynamic array with resizing)
* Dictionary<K,V> (hash map, key-value pairs)
* Set<T> (unique elements, no duplicates)
* Queue<T> (FIFO queue)
* Stack<T> (LIFO stack)
* LinkedList<T> (doubly-linked list)
* PriorityQueue<T> (heap-based priority queue)
* HashSet<T> (fast lookup set)
* SortedSet<T> (ordered set)
* Concurrent collections (thread-safe variants)
* LINQ-style operations (map, filter, reduce, sort)

**Example Usage**:
```fusion
import Fusion.Collections

void function main(string... args)
    // List operations
    List<int> numbers = List<int>()
    numbers.add(1)
    numbers.add(2)
    numbers.add(3)

    // Dictionary usage
    Dictionary<string, int> ages = Dictionary<string, int>()
    ages["Alice"] = 30
    ages["Bob"] = 25

    // LINQ operations
    List<int> evens = numbers.filter((int x) : x % 2 == 0)
    int sum = numbers.reduce(0, (int acc, int x) : acc + x)
    print("Sum: {sum}")
End function
```

---

#### Threading Module (fusionlib.Threading)

Description: Concurrency primitives for multi-threaded and parallel programming.

**Features**:
* Thread creation and management
* Goroutines (lightweight threads)
* Channels (message passing, Go-style)
* Mutex and RWLock (synchronization primitives)
* Semaphore and Barrier
* Thread pools and task scheduling
* Atomic operations
* Thread-local storage
* Race condition detection
* Deadlock detection
* Async/await support

**Example Usage**:
```fusion
import Fusion.Threading

void function main(string... args)
    // Create channel
    Channel<int> ch = Channel.create<int>()

    // Launch goroutine
    go processData(ch)

    // Send data
    ch.send(42)
    ch.send(100)
    ch.close()

    // Async operation
    async Task<string> result = fetchDataAsync()
    string data = await result
    print("Received: {data}")
End function

void function processData(Channel<int> ch)
    while not ch.isClosed()
        int value = ch.receive()
        print("Processing: {value}")
    End while
End function
```

---

#### IO Module (fusionlib.IO)

Description: File system operations, stream processing, and data persistence.

**Features**:
* File operations (read, write, append, delete)
* Directory operations (create, delete, list, traverse)
* Path manipulation (join, normalize, absolute)
* Stream I/O (FileStream, MemoryStream, BufferedStream)
* Text readers and writers
* Binary readers and writers
* Async file I/O
* File watching (monitor changes)
* Compression (zip, gzip)
* Temporary files and directories

**Example Usage**:
```fusion
import Fusion.IO

void function main(string... args)
    // Write to file
    File.writeText("output.txt", "Hello, Fusion!")

    // Read from file
    string content = File.readText("output.txt")
    print("File contents: {content}")

    // Directory operations
    Directory.create("temp")
    string[] files = Directory.getFiles(".", "*.txt")
    print("Found {files.length} text files")

    // Async file I/O
    async Task<string> content = File.readTextAsync("large.txt")
    string data = await content
End function
```

---

### Additional Libraries (Extended Functionality)

Description: Domain-specific modules for networking, multimedia, system integration, and advanced features.

---

#### Networking & Data Processing

##### Net Module (fusionlib.Net)

Description: Network communication protocols and utilities.

**Features**:
* TCP client and server
* UDP sockets
* HTTP client (GET, POST, PUT, DELETE)
* HTTP server (basic web server)
* WebSocket client and server
* DNS resolution
* Email (SMTP, POP3, IMAP)
* FTP client
* SSL/TLS support
* Socket options and configuration
* Network utilities (ping, traceroute)

---

##### Data Module (fusionlib.Data)

Description: Parsing and serialization for common data formats.

**Features**:
* JSON parser and serializer
* CSV reader and writer
* XML parser and generator
* YAML parser and serializer
* Markdown parser and renderer
* INI file parser
* TOML parser
* Protocol Buffers support
* MessagePack support
* Custom format creators

---

#### System Integration

##### System Module (fusionlib.System)

Description: Operating system integration and process management.

**Features**:
* Process creation and management
* Environment variables
* Command-line execution
* DLL/shared library loading
* Platform detection (OS, architecture)
* System information (CPU, memory, disk)
* Registry access (Windows)
* User and group management
* Permissions and security
* System events and signals

---

##### Lang Module (fusionlib.Lang)

Description: Multi-language compilation and code execution support.

**Features**:
* C compiler integration
* C++ compiler integration
* Java compiler and JVM execution
* VB.NET compiler integration
* Python interpreter
* Ruby interpreter
* JavaScript engine (V8/SpiderMonkey)
* Go compiler integration
* Fusion self-hosting compiler
* Assembly language support
* Lexer and parser generators
* AST manipulation
* Code generation utilities

---

##### Languages Module (fusionlib.Languages)

Description: Internationalization and localization support.

**Features**:
* Internationalization (i18n)
* Localization (l10n)
* Translation management
* Locale support (date, time, currency formats)
* Resource bundles
* Text direction (LTR, RTL)
* Unicode handling
* Character encoding conversion
* Pluralization rules
* Language detection

---

#### Multimedia & User Interface

##### GUI Module (fusionlib.GUI)

Description: Cross-platform user interface framework.

**Features**:
* HTML5-compliant UI framework
* Cross-platform widgets (buttons, textboxes, labels, etc.)
* Layout managers (grid, stack, dock, flex)
* Event handling (click, hover, keyboard, etc.)
* Data binding
* Styling and theming (CSS-like)
* Drag and drop
* Menus and toolbars
* Dialogs (file picker, message box, etc.)
* Custom controls
* Accessibility support

---

##### Graphics Module (fusionlib.Graphics)

Description: 2D/3D rendering and game development utilities.

**Features**:
* 2D rendering (shapes, lines, curves)
* 2D sprites and textures
* 2D animations and sprite sheets
* 3D rendering pipeline
* 3D meshes and models
* Lighting and shadows
* Shaders (vertex, fragment, compute)
* Cameras and viewports
* Particle systems
* Physics integration
* Image loading and manipulation
* Game engine utilities

---

##### Audio Module (fusionlib.Audio)

Description: Sound playback, synthesis, and audio processing.

**Features**:
* Sound playback (WAV, MP3, OGG, FLAC)
* Music streaming and looping
* 3D spatial audio positioning
* Real-time synthesis (oscillators, filters)
* Audio effects (reverb, delay, distortion, EQ)
* Multi-track mixing
* Microphone input and recording
* MIDI support
* Audio analysis (FFT, spectrum, beat detection)

---

#### Advanced Features

##### Crypto Module (fusionlib.Crypto)

Description: Cryptography and security operations.

**Features**:
* Symmetric encryption (AES, ChaCha20)
* Asymmetric encryption (RSA, ECC)
* Hashing (SHA-256, SHA-512, BLAKE3)
* Password hashing (bcrypt, Argon2)
* Digital signatures
* Key derivation (PBKDF2, HKDF)
* Random number generation (CSPRNG)
* SSL/TLS support
* Certificate management

---

##### Database Module (fusionlib.Database)

Description: Database connectivity and ORM support.

**Features**:
* SQL database support (SQLite, PostgreSQL, MySQL, SQL Server)
* NoSQL support (MongoDB, Redis, Cassandra)
* Connection pooling
* Transaction management
* ORM (Object-Relational Mapping)
* Query builder
* Schema migration
* Database backup/restore
* Performance optimization

---

##### Web Module (fusionlib.Web)

Description: Web server and REST API framework.

**Features**:
* HTTP/HTTPS server
* WebSocket server
* Routing and middleware
* Template engine
* Session management
* Cookie handling
* REST API framework
* JSON/XML serialization
* File upload/download
* Static file serving
* Request/response handling
* CORS support

---

##### AI Module (fusionlib.AI)

Description: Machine learning and artificial intelligence.

**Features**:
* Neural networks (feedforward, CNN, RNN, LSTM)
* Training algorithms (backpropagation, gradient descent)
* Model serialization and loading
* Data preprocessing and normalization
* Feature extraction
* Classification and regression
* Clustering algorithms
* Natural language processing basics
* Computer vision utilities
* Pre-trained model integration

---

### IDE & Development Libraries

Description: Tools specifically designed for development workflow, testing, debugging, documentation, and IDE integration.

---

#### Reflection Module (fusionlib.Reflection)

Description: Runtime type introspection and dynamic code execution.

**Features**:
* Runtime type inspection
* Method invocation (call methods dynamically)
* Property access (get/set dynamically)
* Attribute/annotation reading
* Type creation at runtime
* Assembly loading
* Code generation (emit IL/bytecode)
* Serialization and deserialization
* Duck typing support
* Dynamic proxy generation

**IDE Integration**:
* Powers autocomplete and IntelliSense
* Enables runtime code analysis
* Supports dynamic plugin systems

---

#### Test Module (fusionlib.Test)

Description: Comprehensive testing framework with IDE integration.

**Features**:
* Unit testing framework
* Assertions (assertEquals, assertTrue, etc.)
* Test fixtures and setup/teardown
* Test suites and runners
* Mocking and stubbing
* Code coverage analysis
* Benchmarking tools
* Performance testing
* Parameterized tests
* Test reporting (HTML, XML, JSON)

**IDE Integration**:
* Test runner UI
* Real-time test execution
* Coverage visualization
* Failure navigation

---

#### Diagnostics Module (fusionlib.Diagnostics)

Description: Profiling, logging, and debugging utilities.

**Features**:
* Logging framework (levels: debug, info, warn, error)
* Performance profiling
* CPU profiling
* Memory profiling
* Execution tracing
* Stopwatch and timing
* Performance counters
* Event logging
* Crash reporting
* Debug output and breakpoints

**IDE Integration**:
* Profiler visualization
* Memory leak detection
* Performance hotspot highlighting
* Real-time log viewing

---

#### DocWiki Module (fusionlib.DocWiki)

Description: Automatic documentation generation and wiki creation during background compilation.

**Features**:
* Automatic documentation extraction from code comments
* Real-time wiki generation during IDE background compilation
* API reference generation from function signatures and types
* Markdown and HTML output formats
* Cross-referencing of types, methods, and modules
* Custom documentation templates
* Code example extraction and formatting
* Version history and changelog generation
* Search index creation
* Export to static site generators (Jekyll, Hugo, Docusaurus)

**Documentation Comment Formats**:
```fusion
/// Single-line documentation comment

/**
 * Multi-line documentation comment
 * Supports markdown formatting
 */

/**
 * Calculates the factorial of a number
 * @param n The input number (must be non-negative)
 * @return The factorial of n
 * @example
 *   int result = factorial(5)  // Returns 120
 */
int function factorial(int n)
    if n <= 1
        return 1
    End if
    return n * factorial(n - 1)
End function
```

**Supported Annotations**:
* `@param` - Parameter description
* `@return` - Return value description
* `@throws` - Exception descriptions
* `@example` - Code examples
* `@deprecated` - Mark as deprecated
* `@since` - Version information
* `@see` - Cross-references

**IDE Integration**:
* Real-time preview in IDE sidebar
* Hover tooltips with documentation
* Automatic wiki updates on file save
* Documentation coverage metrics
* Broken link detection
* IntelliSense powered by doc comments

**Example Usage**:
```fusion
import Fusion.DocWiki

/// Main application entry point
/// @param args Command-line arguments
void function main(string... args)
    // Generate documentation for the project
    DocWiki wiki = DocWiki.create("MyProject")
    wiki.setVersion("1.0.0")
    wiki.addSource("src/")
    wiki.setOutputFormat(DocFormat.HTML)
    wiki.generate("docs/")

    print("Documentation generated successfully!")
    print("Open docs/index.html to view")
End function

/**
 * Vector3 represents a 3D vector
 * @example
 *   Vector3 pos = Vector3(10.0, 5.0, 0.0)
 *   float length = pos.magnitude()
 */
class Vector3
    public float x
    public float y
    public float z

    /// Calculates the magnitude (length) of the vector
    /// @return The Euclidean length of the vector
    float function magnitude()
        return Math.sqrt(x * x + y * y + z * z)
    End function
End class
```

---

### Library Summary

**Quick Import Reference**:
```fusion
// Core Libraries (use in 90% of programs)
import Fusion.Core
import Fusion.Math
import Fusion.Collections
import Fusion.Threading
import Fusion.IO

// Networking & Data
import Fusion.Net
import Fusion.Data

// System Integration
import Fusion.System
import Fusion.Lang
import Fusion.Languages

// Multimedia
import Fusion.GUI
import Fusion.Graphics
import Fusion.Audio

// Advanced
import Fusion.Crypto
import Fusion.Database
import Fusion.Web
import Fusion.AI

// IDE & Development
import Fusion.Reflection
import Fusion.Test
import Fusion.Diagnostics
import Fusion.DocWiki
```

See **fusion_specs.md** for complete API documentation of each module.

**Module Count**: 21 total (5 Core + 12 Additional + 4 IDE)

---

## Callbacks and Events

Description: Function pointers and event-driven programming.

**Note**: Callbacks are not allowed in strict mode when performance is more important, as they can introduce overhead and unpredictability in execution.

**Function Types**:
```
// Define callback type
type Callback = void function(int result)
type EventHandler = void function(Object sender, EventArgs args)

// Use callback
void function processAsync(int data, Callback onComplete)
    int result = data * 2
    onComplete(result)

// Lambda callback
processAsync(42, lambda r: print("Result: {r}"))

// Events
class Button
    Event<void function(Button)> onClick
    
    void function click()
        onClick.invoke(this)

Button btn = Button()
btn.onClick += lambda b: print("Clicked!")
```

---

## External Interoperability

Description: Integration with external code and systems.

---

### DLL Loading

```
import Fusion.System.DllLoader

DLL lib = DLL.load("mylib.dll")
type AddFunc = int function(int, int)
AddFunc add = lib.getFunction<AddFunc>("add")
int result = add(10, 20)
lib.unload()
```

---

### External Processes

```
import Fusion.System.Process

Process proc = Process.start("python", ["script.py"])
string output = proc.readOutput()
int exitCode = proc.exitCode
```

---

### Assembly Language

```
@Unsafe
int function fastAdd(int a, int b)
    int result
    asm
        mov eax, [a]
        add eax, [b]
        mov [result], eax
    return result
```

---

### External Compilers

```
import Fusion.Lang.Compiler

Compiler msvc = Compiler.loadExternal("fusion-msvc-x64.dll")
msvc.setOptimizationLevel(3)
CompileResult result = msvc.compile("code.fusion")
```

---

## Auto-Documentation

Description: Generate documentation from source comments.

**Documentation Format**:
```
/**
 * @title Spaceship Class
 * @description Main spaceship entity
 * @category Game/Entities
 * @example
 *   Spaceship ship = Spaceship("Enterprise", 100.0)
 */
class Spaceship
```

**Generate**:
```bash
fusion doc generate --output ./wiki
```

---

**Word Documents**:
```
import Fusion.Documents

Document doc, Error err = Document.load("report.docx")
if not err
    string text = doc.getText()
    doc.appendText("New content")
    doc.save("modified.docx")
```

**Excel Spreadsheets**:
```
import Fusion.Spreadsheet

Workbook wb, Error err = Workbook.load("data.xlsx")
Sheet sheet = wb.getSheet("Sheet1")
string value = sheet.getCell("A1").getValue()
sheet.setCell("B1", "New Value")
wb.save()
```

**PDF Documents**:
```
import Fusion.PDF

PDF pdf = PDF.create()
pdf.addPage()
pdf.drawText(100, 700, "Hello PDF!")
pdf.save("output.pdf")
```

**ZIP Archives**:
```
import Fusion.Archive

ZIP zip = ZIP.create("archive.zip")
zip.addFile("file1.txt")
zip.addFile("file2.txt")
zip.close()
```

---

### Custom Format Creator

Description: Framework for defining new file formats.

```
import Fusion.Format

// Define custom format
FormatDefinition myFormat = FormatDefinition.create("myformat")
myFormat.setMagicBytes([0x4D, 0x59, 0x46, 0x4D])
myFormat.defineField("header", FieldType.STRING, 32)
myFormat.defineField("version", FieldType.INT32)

// Create reader/writer
FormatReader reader = FormatReader.create(myFormat)
FormatWriter writer = FormatWriter.create(myFormat)
```

---

### Localization Support

Description: Multi-language application support.

**Supported Languages**: English, Japanese, Spanish, French, German, Chinese, and more

**API Example**:
```
import Fusion.Localization

// Set current language
Locale.setCurrent("ja-JP")

// Get translated strings
string greeting = Locale.getString("greeting")  // "こんにちは"

// Formatted strings
string message = Locale.format("welcome_user", userName)
```

---

### Networking

* **HTTP**: Client and server implementations
* **WebSocket**: Real-time bidirectional communication
* **TCP/UDP**: Low-level socket programming

---

### Graphics and Audio

* **2D Graphics**: Drawing primitives, sprites, textures
* **3D Graphics**: Rendering, lighting, shaders
* **Audio**: Sound playback, synthesis, effects

---

### Threading and Concurrency

* **Task Parallel Library**: High-level task management
* **Thread Pools**: Efficient worker thread management
* **Channels**: Message passing between threads
* **Async/Await**: Simplified asynchronous programming

---

### Date and Time

* **DateTime**: Date and time manipulation
* **TimeSpan**: Duration calculations
* **Calendar**: Calendar-specific operations
* **Time zones**: Timezone conversions

---

### Regular Expressions

* **Pattern matching**: Powerful text search and replace
* **Validation**: Input validation with regex
* **Parsing**: Extract data from text

---

## Reserved Words and Operators

Description: Keywords and symbols reserved by the Fusion language.

---

## Reserved Words and Operators

Description: Complete list of language keywords and operators.

---

### Reserved Keywords

Description: Words that cannot be used as identifiers.

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
* `Unique`, `Shared`, `Weak`

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
`==` | Equal to | `a == b`
`!=` | Not equal to | `a != b`
`<>` | Not equal to (alternative) | `a <> b`
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
`?.` | Safe navigation | `object?.property`
`??` | Null coalescing | `value ?? default`
`[]` | Array/index access | `array[0]`
`?[]` | Safe array access | `array?[0]`
`()` | Function call / grouping | `function(args)`
`...` | Spread/variadic/range | `1...10`, `int... args`
`::` | Scope resolution | `Module::Class`
`:` | Lambda/type separator (default) | `int add(int x) : x + 1`
`->` | Lambda/type separator (alternative) | Reserved, alternative to `:`

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
15 | `=`, `+=`, `-=`, `*=`, `/=`, `%=` | Right-to-left

**Use parentheses for clarity**: When in doubt, use `()` to make order explicit.

---

## Language Features Summary

Description: Comprehensive overview of Fusion's capabilities and design decisions.

---

### Syntax Features

* **Function Declaration**: `<returnType> function name(<type> param = defaultValue)`
* **Variable Declaration**: `type name = value` or `var name = value`
* **Constructor**: `constructor(type param)` - explicit keyword
* **Loop Endings**: `end loop` with optional safety checks
* **No Semicolons**: Line breaks end statements
* **Flexible Blocks**: Indentation-based or braces (user preference)
* **Named Parameters**: `function(param2 = value, param1 = value)`
* **Default Parameters**: Optional parameter values
* **Enums**: Three syntax styles (braces, indentation, single-line)
* **Comments**: Both `//` and `'` supported, `/* */` for multi-line
* **Regions**: `#Region` / `#End Region` for code organization
* **Comparison Operators**: Both `!=` and `<>` for not-equal
* **Spread Operator**: `...` for variadic, range, and array spread

---

### Enumerations

* **Multiple Syntaxes**: Braces, indentation, or single-line
* **Custom Values**: Integer values for enum constants
* **Type Safety**: Cannot assign int directly to enum
* **Built-in Methods**: `toString()`, `values()`, `fromString()`
* **Usage**: In switch/match statements, comparisons

---

### The `...` Operator

* **Range in Loops**: `for i in 1...100`
* **Variadic Functions**: `int function sum(int... numbers)`
* **Array Spread**: `[...arr1, ...arr2]`
* **Rest Parameters**: `function log(string level, string... messages)`
* **Can Be Disabled**: In strict mode if needed

---

### Type System

* **Value Types**: Never null (int, float, bool, char, struct)
* **Reference Types**: Can be null (objects, string)
* **No Nullable Value Types**: Syntax like `int?` does not exist
* **Explicit Null Checks**: `object?.null` or `object is null`
* **String Implementation**: Immutable, copy-on-write, string pool
* **Type Casting**: Implicit widening, explicit narrowing
* **Default Values**: All types have defaults (0, false, "", null)
* **Enums**: Type-safe enumeration values

---

### Static Members and Constants

* **Static Methods**: Belong to class, not instance
* **Static Fields**: Shared across all instances
* **Constants**: Automatically static (no instance constants)
* **Access**: Via `ClassName.memberName`
* **Visibility**: Can be public or private

---

### Array Safe Navigation

* **Safe Access**: `array?[0]` returns null if array is null
* **Safe Methods**: `array?.sum()`, `array?.map()`
* **Chaining**: `array?.filter()?.max()`
* **Manual Handling**: Programmer must handle null afterward
* **Optional Use**: Can use `?.` or not (user choice)

---

### Error Handling

* **Multiple Return Values**: `result, err = function()`
* **Optional Error Capture**: `result = function()` (error bubbles up)
* **Error Object**: Built-in with message, code, stack trace
* **Traditional Exceptions**: Available for unexpected errors
* **When to Use**: Multiple returns for expected, exceptions for unexpected

---

### Memory Management

* **Tier 1**: Automatic garbage collection (default)
* **Tier 2**: Smart pointers (Unique, Shared, Weak) for performance
* **Tier 3**: Raw pointers (unsafe mode, embedded systems only)
* **Strategy**: Start with GC, optimize with smart pointers if needed

---

### Null Safety

* **Value Types**: Cannot be null, always have value
* **Objects**: Must check with `?.null` or `is null`
* **Safe Navigation**: `object?.property` returns none if null
* **Strict Mode**: Compiler enforces null checks
* **String Safety**: `string?.length` returns 0 if null

---

### Autoboxing

* **Automatic Conversion**: Primitives become objects when needed
* **Method Calls**: `(42).toString()`, `(3.14).round(2)`
* **Autobox Classes**: Int, Long, Float, Double, Boolean, Char, Byte
* **Performance**: Compiler optimizes unnecessary boxing

---

### Properties

* **Auto-Properties**: `property Name: type { get; set; }`
* **Computed Properties**: Custom get/set with validation
* **Indexed Properties**: `property Items[int index]: type`
* **Indexed-Only**: Prevent array replacement, allow element access
* **Multi-Dimensional**: `property Cell[int x, int y]: type`

---

### Structures

* **Value Semantics**: Copied, not referenced
* **Allowed Types**: Primitives, string, fixed arrays only
* **Not Allowed**: Objects, dynamic collections
* **Use Case**: Pure data containers for performance

---

### Threading and Concurrency

* **Message Passing**: Channels for safe communication (Go-style)
* **Shared Memory**: Traditional locks when needed
* **Async/Await**: Built-in for I/O operations
* **Thread Interrupts**: Cooperative multitasking via loop checks
* **Philosophy**: "Share memory by communicating"

---

### Loops

* **Explicit Endings**: `end loop` marker
* **Safety Checks**: Manual, periodic, iteration limit, interrupt handling
* **Check Types**: `end loop with {count} check ...`
* **Automatic Protection**: Compiler adds infinite loop prevention
* **Resource Monitoring**: Adapts to system RAM/CPU
* **Thread Safety**: Interrupt handling built-in
* **Range Operator**: `for i in 1...100` with optional step
* **Configurable**: Per-project or per-loop settings

---

### Standard Library

* **File Formats**: txt, md, JSON, XML, CSV, YAML, ini
* **Programming Languages**: Compilers for Go, Fusion, Java, C, C++, VB.NET, JS, HTML, CSS
* **Image Formats**: BMP, JPEG, GIF, PNG readers/writers
* **Binary Formats**: DOC, Excel, PDF, ZIP support
* **Custom Formats**: Framework for defining new formats
* **Localization**: Multi-language support (English, Japanese, etc.)
* **Collections**: List, Dictionary, Set, Queue, Stack
* **Math**: Vector, Matrix, Quaternion libraries
* **Networking**: HTTP, WebSocket, TCP/UDP
* **Graphics**: 2D and 3D rendering primitives
* **Audio**: Sound playback and synthesis

---

### Modules

* **Organization**: One class per file
* **Module Definition**: Special module.fusion file
* **Import Syntax**: `import Module` or `import Module.Class`
* **Visibility**: Export control for public/private
* **Nested Classes**: Allowed within class file

---

### Compilation

* **Script Mode**: Run directly without compilation
* **Executable**: Native binary compilation
* **Library**: DLL/shared library for reuse
* **JIT Mode**: Just-in-time compilation
* **Cross-Platform**: Linux, Windows, macOS, WebAssembly

---

### From Parent Languages

* **From C**: Performance, structs, memory control, operators
* **From Java**: Strong typing, interfaces, generics, OOP structure
* **From Python**: Simple syntax, indentation, easy to read
* **From VB.NET**: Readable keywords, properties, explicit intent
* **From Go**: Message passing, channels, multiple returns, goroutines

---

### Unique to Fusion

* **Return-Type-First**: Clear function signatures
* **Value/Reference Distinction**: Explicit null safety
* **Flexible Block Syntax**: Indentation or braces (user preference)
* **Three Enum Syntaxes**: Braces, indentation, or single-line
* **Dual Comment Styles**: Both `//` and `'` supported
* **Loop Safety Checks**: Multiple check types with automatic protection
* **Indexed Properties**: Enhanced array access
* **Error Bubbling**: Optional error capture with multiple returns
* **Three-Tier Memory**: GC, smart pointers, or raw
* **Script or Compile**: Choose execution mode
* **`...` Operator**: Multi-purpose (range, spread, variadic)
* **`<>` Comparison**: Alternative to `!=` for not-equal
* **Automatic Locking**: Try-with-resources prevents deadlocks
* **Weak Pointers Discouraged**: Error in strict mode
* **Constants Auto-Static**: No instance constants
* **Comprehensive Standard Library**: Built-in support for 20+ file formats
* **Programming Language Support**: Built-in compilers for 9 languages
* **IDE Integration**: Threading visualization, code regions
* **Main Function**: `void function main(string... args)` as application entry point

---

## Language Comparison

Description: How Fusion compares to its parent languages across key features.

---

### Syntax and Structure Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Function Syntax** | `int add(int a)` | `int add(int a)` | `def add(a):` | `Function Add(a) As Integer` | `func add(a int) int` | `int function add(int a)`
**Return Type** | Before name | Before name | None/hints | After name | After params | **Before name**
**Block Style** | Braces `{}` | Braces `{}` | Indentation | Keywords | Braces `{}` | **Both** (user choice)
**Semicolons** | Required | Required | Not used | Not used | Optional | **Not used**
**Type Inference** | No (C89), Yes (C11) | Limited (`var`) | Yes | Limited (`var`) | Yes | **Yes** (`var`)
**Null Safety** | No | Limited | No | Limited | No | **Yes** (built-in)
**Comments** | `//` `/* */` | `//` `/* */` | `#` | `'` `REM` | `//` `/* */` | **`//` `'` `/* */`**
**Main Entry** | `int main()` | `void main()` | N/A (script) | `Sub Main()` | `func main()` | **`void function main(string... args)`**

---

### Type System Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Static Typing** | Yes | Yes | No (dynamic) | Yes | Yes | **Yes**
**Type Inference** | Limited | Limited | N/A | Limited | Yes | **Yes**
**Nullable Types** | All (pointers) | Objects only | All | Limited | Pointers only | **Objects only**
**Value Types** | Structs | Primitives | N/A | Structures | Structs | **Primitives + Structs**
**String Type** | `char*` | `String` (object) | `str` | `String` | `string` | **`string` (immutable)**
**Generics** | No | Yes | No | Yes | Yes | **Yes**
**Auto-boxing** | No | Yes | N/A | Yes | No | **Yes**

---

### Memory Management Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Manual Memory** | malloc/free | No | No | No | No | **Yes (unsafe mode)**
**Garbage Collection** | No | Yes | Yes | Yes | Yes | **Yes (tier 1)**
**Smart Pointers** | No (C++11) | No | No | No | No | **Yes (tier 2)**
**Raw Pointers** | Yes | No | No | No | Yes | **Yes (unsafe only)**
**Memory Safety** | No | Yes | Yes | Yes | Mostly | **Yes (3 tiers)**
**RAII** | No (C++ only) | No | No | No | Defer | **Yes (using)**

---

### Concurrency Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Threading** | pthreads | Threads | Threads | Threads | Goroutines | **Threads + Goroutines**
**Channels** | No | No | queue.Queue | No | Yes | **Yes (Go-style)**
**Message Passing** | No | Limited | queue | No | Yes | **Yes**
**Shared Memory** | Yes | Yes | Limited (GIL) | Yes | Yes | **Yes (with locks)**
**Async/Await** | No | No | Yes | Yes | No | **Yes**
**Race Detection** | No | No | No | No | Yes | **Yes (built-in)**
**Auto-locking** | No | No | No | No | No | **Yes (try-with)**

---

### Error Handling Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Exceptions** | No | Yes | Yes | Yes | No | **Yes**
**Multiple Returns** | No | No | Yes (tuples) | No | Yes | **Yes (Go-style)**
**Error Type** | int codes | Exception | Exception | Exception | error | **Error object**
**Try-Catch** | No | Yes | Yes | Yes | No | **Yes**
**Error Bubbling** | No | Yes | Yes | Yes | No | **Yes (optional)**
**Checked Exceptions** | No | Yes | No | No | No | **No**

---

### Object-Oriented Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Classes** | No (structs) | Yes | Yes | Yes | No | **Yes**
**Inheritance** | No | Single | Multiple | Single | No | **Single**
**Interfaces** | No | Yes | Protocols | Yes | Yes | **Yes**
**Properties** | No | No (getters) | Yes | Yes | No | **Yes (VB-style)**
**Constructors** | No | Yes | `__init__` | `New` | No | **Yes (`constructor`)**
**Static Members** | No | Yes | Class vars | Yes | No | **Yes**
**Access Modifiers** | No | Yes | Convention | Yes | Capitalization | **Yes (public/private)**

---

### Advanced Features Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Enums** | Yes (int) | Yes | Enum class | Yes | iota | **Yes (3 styles)**
**Pattern Matching** | No | Limited | Yes (3.10+) | No | No | **Yes (match)**
**Lambdas** | No | Yes | Yes | Yes | Yes | **Yes**
**Closures** | No | Limited | Yes | Yes | Yes | **Yes**
**Operator Overload** | No (C++ only) | No | Yes | Yes | No | **Yes**
**Reflection** | No | Yes | Yes | Yes | Limited | **Yes**
**Annotations** | No | Yes | Decorators | Attributes | No | **Yes (custom)**

---

### Standard Library Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Collections** | Limited | Extensive | Extensive | Extensive | Limited | **Extensive (20 modules)**
**File I/O** | Basic | Good | Excellent | Good | Good | **Excellent**
**Networking** | Sockets | Good | Excellent | Good | Excellent | **Excellent**
**JSON** | No (libs) | Yes | Yes | Yes | Yes | **Yes (built-in)**
**XML** | No (libs) | Yes | Yes | Yes | No | **Yes (built-in)**
**HTTP** | No (libs) | Limited | Yes | Limited | Yes | **Yes (built-in)**
**Graphics** | No (libs) | Limited | Yes (libs) | Yes | No | **Yes (built-in)**
**Audio** | No (libs) | Limited | Yes (libs) | Yes | No | **Yes (built-in)**
**Crypto** | No (libs) | Yes | Yes (libs) | Yes | No | **Yes (built-in)**
**Database** | No (libs) | JDBC | Yes (libs) | ADO.NET | database/sql | **Yes (built-in ORM)**
**Web Server** | No (libs) | Limited | Yes (Flask/Django) | ASP.NET | net/http | **Yes (built-in)**
**AI/ML** | No (libs) | Limited | Excellent (libs) | ML.NET | No | **Yes (built-in)**
**Multi-language** | No | No | No | No | No | **Yes (10 languages)**

---

### Build and Execution Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Compilation** | Native | Bytecode | Bytecode | IL/Native | Native | **Native/Bytecode/JIT**
**Script Mode** | No | No | Yes | No | No | **Yes**
**Execution Speed** | Fastest | Fast | Slow | Fast | Fast | **Fast**
**Compile Time** | Slow | Medium | N/A | Medium | Fast | **Medium**
**Cross-Platform** | Yes (recompile) | Yes (JVM) | Yes | Limited | Yes (recompile) | **Yes (recompile)**
**Binary Size** | Small | Large (JVM) | Large | Medium | Medium | **Medium**
**Startup Time** | Instant | Slow (JVM) | Medium | Medium | Instant | **Fast**

---

### Safety and Security Comparison

Feature | C | Java | Python | VB.NET | Go | Fusion
---|---|---|---|---|---|---
**Memory Safety** | No | Yes | Yes | Yes | Mostly | **Yes (3 modes)**
**Type Safety** | Weak | Strong | Dynamic | Strong | Strong | **Strong**
**Null Safety** | No | Limited | No | Limited | No | **Yes (built-in)**
**Buffer Overflow** | Vulnerable | Protected | Protected | Protected | Protected | **Protected**
**Safety Modes** | No | No | No | No | No | **Yes (3 levels)**
**Strict Mode** | No | No | No | No | No | **Yes**
**Unsafe Mode** | Default | No | No | No | unsafe | **Yes (explicit)**

---

### Unique Language Features Summary

Feature | Availability
---|---
**Return-type-first syntax** | Fusion only
**Dual comment styles (// and ')** | Fusion only (VB has ')
**Three enum syntaxes** | Fusion only
**Flexible blocks (indent or braces)** | Fusion only
**Three-tier memory (GC/Smart/Raw)** | Fusion only
**Automatic loop protection** | Fusion only
**Try-with-resources auto-locking** | Fusion only (Java has try-with, Fusion adds locking)
**Built-in language compilers** | Fusion only
**20+ file format support** | Fusion only
**Script or compile mode** | Fusion + Python
**Indexed properties** | Fusion + VB.NET
**Multiple return values** | Fusion + Go + Python
**Channels** | Fusion + Go
**Message passing concurrency** | Fusion + Go
**`...` operator (multi-purpose)** | Fusion only (others have parts)
**Main function syntax** | Unique: `void function main(string... args)`

---

### Language Philosophy Comparison

Language | Primary Focus | Strengths | Weaknesses
---|---|---|---
**C** | Performance, low-level control | Fast, small binaries, hardware access | Unsafe, manual memory, no OOP
**Java** | Enterprise, portability | Strong ecosystem, JVM, garbage collection | Verbose, slow startup, memory heavy
**Python** | Simplicity, productivity | Easy to learn, extensive libraries, rapid dev | Slow execution, GIL limits threading
**VB.NET** | Readability, RAD | Natural language syntax, quick UI dev | Windows-focused, less popular
**Go** | Simplicity, concurrency | Fast compilation, goroutines, simple | No generics (old), limited OOP
**Fusion** | **All of the above** | Combines best features, flexible, comprehensive | New (unproven), learning curve

---

### Fusion's Advantage

**Fusion combines**:
* ✓ C's performance and memory control
* ✓ Java's strong typing and OOP structure
* ✓ Python's simplicity and ease of learning
* ✓ VB.NET's readability and natural syntax
* ✓ Go's concurrency model and efficiency

**Plus unique features**:
* ✓ Three safety modes (standard, strict, unsafe)
* ✓ Flexible syntax (choose your style)
* ✓ Built-in language compilers
* ✓ Comprehensive standard library
* ✓ Script or compile execution
* ✓ Superior error handling (exceptions + multiple returns)

**Result**: A modern, flexible, safe, and powerful language suitable for any application domain.

