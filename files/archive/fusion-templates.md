# Fusion Language Templates and Notation

Description: Complete template reference showing syntax patterns with proper notation. This document uses `<>` for type/name placeholders and `{}` for optional elements.

Note: Fusion is a combination of various languages (C, Java, Python, VB.NET, Go) unified into one cohesive language.

---

## Notation Guide

Description: Understanding template syntax.

* `<type>` - Type placeholder (replace with actual type like int, string, Spaceship)
* `<name>` - Identifier placeholder (replace with actual name)
* `{element}` - Optional element (can be omitted)
* `{}` - Optional block delimiters (braces) for user preference
* `|` - Alternative options (choose one)
* `...` - Repetition (element can repeat)

---

## Variable Declaration Templates

Description: All ways to declare variables.

---

### Basic Variable Declaration

```
// Type-first with initialization
<type> <name> = <value>

// Examples
int count = 10
string name = "Starship"
float speed = 299.792
Spaceship ship = Spaceship("Enterprise", 100.0)
```

---

### Type Inference

```
// Inferred type with initialization
var <name> = <value>

// Examples
var count = 10              // Inferred as int
var name = "Starship"       // Inferred as string
var ship = Spaceship("Enterprise", 100.0)  // Inferred as Spaceship
```

---

### Declaration Without Initialization

```
// Uses default value for type
<type> <name>

// Examples
int count                   // Defaults to 0
string name                 // Defaults to ""
bool flag                   // Defaults to false
Spaceship ship              // Defaults to null (reference type)
```

---

### Constant Declaration

```
// Constant (immutable)
{public|private} const <name>: <type> = <value>

// Examples
public const MAX_SPEED: float = 1000.0
private const DEFAULT_NAME: string = "Unnamed"
const PI: double = 3.14159265359
```

---

## Function Templates

Description: Function declaration patterns.

---

### Basic Function

```
// Function template
<returnType> function <name>(<type> <param> {= <defaultValue>}, ...)
    <body>
{end function}

// Examples
void function printMessage(string msg)
    print(msg)

int function add(int a, int b)
    return a + b

Spaceship function createShip(string name = "Default", float speed = 100.0)
    return Spaceship(name, speed)
```

---

### Function with Braces (Optional Style)

```
// With braces
<returnType> function <name>(<type> <param> {= <defaultValue>}, ...) {
    <body>
}

// Examples
int function multiply(int a, int b) {
    return a * b
}

void function processData(Data d) {
    d.process()
    d.save()
}
```

---

### Function with Error Return

```
// Multiple return values for error handling
<returnType>, Error function <name>(<type> <param>, ...)
    {if <errorCondition>}
        return null, Error("<message>")
    return <result>{, null}

// Examples
Spaceship, Error function loadShip(string filename)
    if not fileExists(filename)
        return null, Error("File not found")
    return ship  // Error implicitly null

int, Error function divide(int a, int b)
    if b == 0
        return 0, Error("Division by zero")
    return a / b
```

---

### Async Function

```
// Async function template
async <returnType>{, Error} function <name>(<type> <param>, ...)
    <returnType> <result> = await <asyncOperation>
    return <result>{, null}

// Examples
async Spaceship, Error function downloadShip(string url)
    Response response = await http.get(url)
    return parseShip(response), null

async void function processAsync()
    Data data = await loadData()
    await saveData(data)
```

---

### Lambda Function

```
// Lambda template
lambda <param>, ...: <expression|body>

// Examples
var double = lambda x: x * 2
var add = lambda a, b: a + b
var complex = lambda x, y:
    int temp = x * 2
    return temp + y
```

---

## Enum Templates

Description: Enumeration declaration patterns.

---

### Enum with Braces

```
// Enum template with braces
Enum <n> {
    <CONSTANT_NAME> {= <value>},
    ...
}

// Examples
Enum Planets {
    MERCURY,
    VENUS,
    EARTH,
    MARS
}

Enum StatusCode {
    OK = 200,
    NOT_FOUND = 404,
    SERVER_ERROR = 500
}
```

---

### Enum with Indentation

```
// Enum template with indentation
Enum <n>
    <CONSTANT_NAME> {= <value>}
    ...

// Examples
Enum Planets
    MERCURY
    VENUS
    EARTH
    MARS

Enum StatusCode
    OK = 200
    NOT_FOUND = 404
    SERVER_ERROR = 500
```

---

### Enum Single-Line

```
// Enum template single-line
Enum <n>: <CONSTANT1>, <CONSTANT2>, ...

// Examples
Enum Planets: MERCURY, VENUS, EARTH, MARS
Enum Direction: NORTH, SOUTH, EAST, WEST
Enum Priority: LOW, MEDIUM, HIGH, CRITICAL
```

---

### Using Enums

```
// Declaration
<EnumType> <varName> = <EnumType>.<CONSTANT>

// Comparison
if <varName> == <EnumType>.<CONSTANT>
    <body>

// Match statement
match <varName>
    case <EnumType>.<CONSTANT1>:
        <body>
    case <EnumType>.<CONSTANT2>:
        <body>

// Examples
Planets planet = Planets.MARS
if planet == Planets.EARTH
    print("Home")

match planet
    case Planets.MARS:
        print("Red planet")
    case Planets.EARTH:
        print("Home")
```

---

## Comment Templates

Description: Code documentation and organization patterns.

---

### Single-Line Comments

```
// Comment template with //
// <comment text>
<code>  // <end-of-line comment>

// Comment template with ' (user preference)
' <comment text>
<code>  ' <end-of-line comment>

// Examples
// This is a comment
int x = 10  // Initialize x

' This is also a comment
int y = 20  ' Initialize y
```

---

### Multi-Line Comments

```
// Multi-line comment template
/*
 * <comment text>
 * <more text>
 */

// Example
/*
 * Function: calculateDistance
 * Purpose: Calculate distance between two points
 * Returns: Distance as float
 */
float function calculateDistance(float x1, float y1, float x2, float y2)
    <body>
```

---

### Region Blocks

```
// Region template
#Region <string_literal_displayed_in_ide>
<statements>
#End Region

// Examples
#Region Initialization Code
void function initialize()
    setupSystem()
    loadConfig()
#End Region

#Region Helper Functions
void function helper1()
    <body>

void function helper2()
    <body>
#End Region
```

---

## Spread Operator Templates

Description: The `...` operator usage patterns.

---

### Range in Loops

```
// Range template
for <varName> in <start>...<end> {... <step>}
    <body>
end loop

// Examples
for i in 1...10
    print(i)  // 1, 2, 3, ..., 10
end loop

for x in 0...100...10
    print(x)  // 0, 10, 20, ..., 100
end loop
```

---

### Variadic Functions

```
// Variadic function template
<returnType> function <n>(<type>... <paramName>)
    <body>

// Examples
int function sum(int... numbers)
    int total = 0
    for num in numbers
        total += num
    end loop
    return total

void function logMessages(string level, string... messages)
    for msg in messages
        print("[{level}] {msg}")
    end loop
```

---

### Array Spread

```
// Array spread template
<type>[] <newArray> = [...<array1>, ...<array2>, ...]

// Examples
int[] arr1 = [1, 2, 3]
int[] arr2 = [4, 5, 6]
int[] combined = [...arr1, ...arr2]  // [1, 2, 3, 4, 5, 6]

// In function call
int result = sum(...combined)
```

---

### Range Array Creation

```
// Range array template
<type>[] <arrayName> = [<start>...<end> {... <step>}]

// Examples
int[] range = [1...10]       // [1, 2, 3, ..., 10]
int[] stepped = [0...100...10]  // [0, 10, 20, ..., 100]
```

---

## Class Templates

Description: Class definition patterns.

---

### Basic Class

```
// Class template
{public|private|internal} class <name> {extends <baseClass>} {implements <interface>, ...}
    // Constants (automatically static)
    {public|private} const <NAME>: <type> = <value>
    
    // Static fields
    {public|private} static <type> <name> {= <value>}
    
    // Instance fields
    {public|private} <type> <name> {= <value>}
    
    // Properties
    {public|private} property <Name>: <type> { get; {private} set; }
    
    // Constructor
    constructor(<type> <param>, ...)
        <initialization>
    
    // Static methods
    {public|private} static <returnType> function <name>(<type> <param>, ...)
        <body>
    
    // Instance methods
    {public|private} <returnType> function <name>(<type> <param>, ...)
        <body>

// Example
public class Spaceship extends Vehicle implements IMovable
    // Constants
    public const MAX_SPEED: float = 1000.0
    
    // Static fields
    private static int shipCount = 0
    
    // Instance fields
    private float fuelLevel
    private bool isActive
    
    // Properties
    public property Name: string { get; private set; }
    public property Speed: float { get; set; }
    
    // Constructor
    constructor(string name, float speed)
        this.Name = name
        this.Speed = speed
        shipCount += 1
    
    // Static method
    public static Spaceship function createDefault()
        return Spaceship("Default", 100.0)
    
    // Instance method
    public void function start()
        isActive = true
```

---

### Property Templates

```
// Auto-property
{public|private} property <Name>: <type> { get; {private} set; }

// Property with custom get/set
{public|private} property <Name>: <type>
    get
        return <expression>
    {set}
        <validation>
        <assignment>

// Indexed property
{public|private} property <Name>[<type> <index>]: <type>
    get
        return <expression>
    set
        <assignment>

// Examples
public property Name: string { get; private set; }

public property Speed: float
    get
        return _speed
    set
        if value < 0
            _speed = 0
        else
            _speed = value

public property Items[int index]: Item
    get
        return _items[index]
    set
        _items[index] = value
```

---

## Struct Template

```
// Struct template (value types only)
struct <name>
    <primitiveType> <field>
    <primitiveType>[<size>] <arrayField>  // Fixed-size array
    
    constructor(<type> <param>, ...)
        <initialization>
    
    <returnType> function <name>(<type> <param>, ...)
        <body>
    
    <struct> operator <op>(<type> <param>)
        return <expression>

// Example
struct Vector3
    float x
    float y
    float z
    
    constructor(float x, float y, float z)
        this.x = x
        this.y = y
        this.z = z
    
    Vector3 operator +(Vector3 other)
        return Vector3(x + other.x, y + other.y, z + other.z)
    
    float function magnitude()
        return sqrt(x * x + y * y + z * z)
```

---

## Static Methods and Constants Templates

Description: Class-level members that belong to the class itself.

---

### Static Method Template

```
// Static method template
{public|private} static <returnType> function <n>(<type> <param> {= <default>}, ...)
    <body>

// Examples
public static int function max(int a, int b)
    if a > b
        return a
    else
        return b

private static void function internalHelper()
    <body>

// Usage
int result = ClassName.max(10, 20)
```

---

### Static Field Template

```
// Static field template
{public|private} static <type> <n> {= <value>}

// Examples
private static int count = 0
public static string version = "1.0.0"

// Access
ClassName.count += 1
string ver = ClassName.version
```

---

### Constant Template

```
// Constant template (automatically static)
{public|private} const <type> <n> = <value>

// Examples
public const string VERSION = "1.0.0"
public const int MAX_CONNECTIONS = 100
private const float PI = 3.14159

// Usage - access via ClassName
string version = Config.VERSION
int maxConn = Config.MAX_CONNECTIONS
```

**Note**: Constants are implicitly static. No need to write "static const".

---

## Interface Template

```
// Interface template
{public|private} interface <name> {extends <interface>, ...}
    <returnType> function <name>(<type> <param>, ...)
    property <Name>: <type> { get; {set;} }
    
    // Optional default implementation
    {<returnType> function <name>(<type> <param>, ...)}
        <body>

// Example
public interface IMovable
    void function move(Vector3 direction, float deltaTime)
    void function stop()
    property Speed: float { get; }
    
    // Default implementation
    bool function isMoving()
        return Speed > 0
```

---

## Control Flow Templates

Description: Conditional and loop patterns.

---

### If Statement

```
// If template
if <condition>
    <body>
{elif <condition>}
    <body>
{else}
    <body>

// Example
if ship.fuel > 50
    ship.engageWarpDrive()
elif ship.fuel > 20
    ship.startEngine()
else
    print("Insufficient fuel")
```

---

### Match Statement

```
// Match template
match <expression>
    case <value>:
        <body>
    case <value>:
        <body>
    {else:}
        <body>

// Example
match ship.type
    case ShipType.Fighter:
        ship.activateWeapons()
    case ShipType.Cargo:
        ship.openBay()
    else:
        print("Unknown type")
```

---

### While Loop

```
// While loop template
while <condition>
    <body>
    {if <exitCondition>}
        break
end loop {with {<iterations>}}
    {check}
        {<condition>}
    {check interrupt(<signal>, <data>)}
        {<handler>}

// Example
while ship.isActive
    ship.update(deltaTime)
    if ship.fuel <= 0
        break
end loop with {1000}
    check
        if not ship.isValid()
            exit loop
    check interrupt(signal, data)
        if signal == Shutdown
            exit loop
```

---

### For Loop

```
// For loop template
for <var> in range(<start>, <end>{, <step>})
    <body>
end loop {with {<iterations>}}
    {check}
        {<condition>}

// Example
for i in range(0, 10)
    processItem(i)
end loop

for i in range(0, 100, 5)  // Step of 5
    print(i)
end loop
```

---

### For-Each Loop

```
// For-each template
for <var> in <collection>
    <body>
end loop {with {<iterations>}}

// Example
for ship in fleet
    ship.update(deltaTime)
end loop

for item in inventory.Items
    processItem(item)
end loop
```

---

## Threading Templates

Description: Concurrent programming patterns.

---

### Thread Creation

```
// Thread template
Thread <name> = Thread.create({lambda:} <function>)
<name>.start()
{<name>.join()}

// Example
Thread worker = Thread.create(lambda: processData(0, 100))
worker.start()
worker.join()
```

---

### Goroutine

```
// Goroutine template
go {lambda:} <function>

// Example
go processInBackground()

go lambda:
    print("Background work")
    doWork()
```

---

### Channel

```
// Channel template
Channel<<type>> <name> = Channel.create<<type>>({capacity = <size>})
<name>.send(<value>)
<type> <var> = <name>.receive()

// Example
Channel<Task> tasks = Channel.create<Task>(capacity = 10)
tasks.send(task)
Task t = tasks.receive()
```

---

### Using Statement (Auto-locking)

```
// Using template
using <resource> {= <initialization>}
    <body>
// Resource automatically released

// Examples
using file = openFile("data.txt")
    file.write("Data")

using lock
    sharedVariable += 1

using this
    // Method body protected
```

---

## Generic Templates

Description: Type-parameterized code patterns.

---

### Generic Class

```
// Generic class template
class <name><<T>{, <U>, ...}> {where <T> <constraint>}
    <T> <field>
    
    <T> function <name>(<T> <param>)
        <body>

// Example
class Container<T>
    private List<T> items
    
    void function add(T item)
        items.append(item)
    
    T function get(int index)
        return items[index]
```

---

### Generic Function

```
// Generic function template
<T> function <name><<T>{, <U>, ...}>(<T> <param>, ...) {where <T> <constraint>}
    <body>

// Example
T function findMax<T>(List<T> items) where T implements IComparable<T>
    T max = items[0]
    for item in items
        if item.compareTo(max) > 0
            max = item
    end loop
    return max
```

---

## Module Templates

Description: Code organization patterns.

---

### Module Definition

```
// Module template (in module.fusion file)
module <ModuleName>

export <ClassName>
export <ClassName>
{private <ClassName>}

{<visibility> <returnType> function <name>(<type> <param>, ...)}
    <body>

// Example
module Spaceships

export Spaceship
export Warship

void function internalHelper()
    // Module-private function
```

---

### Import Statement

```
// Import template
import <ModuleName>{.*}
import <ModuleName>.<ClassName>

// Examples
import Spaceships
import Spaceships.Spaceship
import Spaceships.*
```

---

## Error Handling Templates

Description: Error management patterns.

---

### Multiple Return Values

```
// Error return template
<returnType>, Error function <name>(<type> <param>, ...)
    {if <errorCondition>}
        return null, Error("<message>"{, <code>})
    return <result>{, null}

// Calling with error capture
<type> <result>, Error <err> = <function>(<args>)
if <err>
    <errorHandling>
<use result>

// Calling without error capture (bubbles up)
<type> <result> = <function>(<args>)

// Example
Spaceship, Error function loadShip(string filename)
    if not fileExists(filename)
        return null, Error("File not found", 404)
    return ship, null

// Usage
Spaceship ship, Error err = loadShip("ship.dat")
if err
    print("Error: {err.message}")
    return
ship.start()
```

---

### Try-Catch

```
// Try-catch template
try
    <body>
{catch <ExceptionType> as <var>}
    <handler>
{finally}
    <cleanup>

// Example
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

## Type Casting Templates

Description: Type conversion patterns.

---

### Explicit Cast

```
// Cast template
<targetType> <var> = cast<<targetType>>(<expression>)

// Examples
float f = cast<float>(3.14159)
int i = cast<int>(3.14159)      // Truncates to 3
string s = cast<string>(42)      // "42"
```

---

### Safe Cast with Check

```
// Try cast template
<targetType>? <var> = tryCast<<targetType>>(<expression>)
if <var>?.null
    <handleFailure>

// Example
double d = 3.14159
int? result = tryCast<int>(d)
if result?.null
    print("Cast failed")
else
    int value = result.unwrap()
```

---

## Null Handling Templates

Description: Null safety patterns.

---

### Null Check

```
// Null check templates
if <object>?.null
    <handleNull>

if <object> is null
    <handleNull>

// Examples
if ship?.null
    print("Ship is null")
    return

if ship is null
    return
```

---

### Safe Navigation

```
// Safe navigation template
<type>? <var> = <object>?.<property>
<type>? <var> = <object>?.<method>(<args>)

// With default value
<type> <var> = <object>?.<property> ?? <defaultValue>

// Examples
string name = ship?.name
float speed = ship?.getSpeed() ?? 0.0
string captain = ship?.captain?.name ?? "Unknown"
```

---

## Build Command Templates

Description: Compilation command patterns.

---

### Build Commands

```
// Run as script
fusion run <file>.fusion

// Compile to executable
fusion build <file>.fusion {--output <name>} {--debug|--release} {--optimize}

// Compile to library
fusion build <file>.fusion --lib {--output <name>} {--release}

// Cross-compile
fusion build <file>.fusion --target <platform> {--output <name>}

// Examples
fusion run game.fusion
fusion build game.fusion --output game.exe --release --optimize
fusion build engine.fusion --lib --output engine.dll --release
fusion build game.fusion --target linux-x64 --output game-linux
```

---

## Complete Example Template

Description: Full class with all features.

```
// Module definition
module <ModuleName>

export <ClassName>

// Class with all features
{public|private} class <ClassName> {extends <BaseClass>} {implements <Interface>, ...}
    // Constants (automatically static)
    {public|private} const <CONSTANT_NAME>: <type> = <value>
    
    // Static fields
    {public|private} static <type> <staticField> {= <value>}
    
    // Instance fields
    {public|private} <type> <field> {= <value>}
    
    // Auto-properties
    {public|private} property <Name>: <type> { get; {private} set; }
    
    // Custom properties
    {public|private} property <Name>: <type>
        get
            return <expression>
        {set}
            <assignment>
    
    // Indexed properties
    {public|private} property <Name>[<type> <index>]: <type>
        get
            return <expression>
        set
            <assignment>
    
    // Constructor
    constructor(<type> <param> {= <defaultValue>}, ...)
        <initialization>
    
    // Static methods
    {public|private} static <returnType> function <name>(<type> <param> {= <defaultValue>}, ...)
        <body>
    
    // Instance methods
    {public|private} <returnType> function <name>(<type> <param> {= <defaultValue>}, ...)
        <body>
    
    // Async methods
    {public|private} async <returnType>{, Error} function <name>(<type> <param>, ...)
        <type> <result> = await <asyncOperation>
        return <result>{, null}
```

---

## Summary

This document provides complete template patterns for all Fusion language constructs. Use `<>` for placeholders that must be filled in, and `{}` for optional elements that can be omitted based on your needs.

Key notation reminders:
* `<type>` = Replace with actual type
* `<name>` = Replace with actual identifier
* `{element}` = Optional (can be omitted)
* `{}` = Optional braces for code blocks (user preference)
* `|` = Choose one alternative
* `...` = Can repeat

Fusion combines the best of C, Java, Python, VB.NET, and Go into a unified, powerful language.
