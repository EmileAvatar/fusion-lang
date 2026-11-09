[< 042 MultipleReturns](042-MultipleReturns.md) | [Index](index.md) | [051 Inheritance >](051-Inheritance.md) <!-- nav -->

# 050 Classes

Contents: [Class Definition](#class-definition) | [Static vs Instance Members](#static-vs-instance-members) | [Properties](#properties)

## Classes and Objects

**Status:** a minimal class is built (Task 32.10b) - the rest [PLANNED 32].

**Visibility (Task 32.2a, built - files/Classes.md section 1):** in a class, fields are **private**
and functions and constructors **public** unless `public` / `private` is written; a private
member is used only by the class's own functions (another object of the same class
included); a private constructor means only the class makes its objects. At module level,
structs, classes and enums are public by default, functions and module variables private
(`private struct Helper`, `public int function api()`).

**Statics (Task 32.2c, built - files/Classes.md section 3):** `static` fields belong to the class -
one for the whole program, read as `Car.count` (or `count` inside Car); `const static` ones
are set only in the class's set-up. Three set-up forms, run in this order before `main`:
**A** `public const static Car CAR = new Car()`; **B** `= new Car() { CAR3.speed = 4 }` - a
block that changes only its own field and reads statics already set up; **C** `static { }` -
may set and change any static of the class (and gives a `const static` declared without a
value its value). Classes are set up in the order they depend on each other, found by
following what each set-up uses and what that calls; another class using a class still
being set up is a compile error showing the chain. `static` methods have no `this`
(`Car.make()`). A static field is private unless written public. Statics are freed last,
when the program ends. In C a static is a module variable (`fusion_g_Car__count`) and a
class's set-up the function `Car.__setup`, called first in main.

**Printing an object (Task 32.2f, built - files/Classes.md section 6):** in `print` / `format`,
`"{car}"` and `toString(car)` an object shows its class name (`Car`; a null one `null`), with a
warning once per class until it can implement ToString (Task 32.5) - then its `toString()`.

**readonly parameters (Task 32.2e, built - files/Object_Lifetime.md section 3):** `void function
show(readonly Account a)` - the function reads `a` but never changes it, deeply: not
assigned, not through a field or element, not by a List / Map method or a method that
changes its object, not passed to a parameter another function changes (worked out by
following the calls - `readonly` needn't be written all the way down), not handed to a
function value. A variable that shares it (`Account b = a`) is readonly too; keeping it
(a field, a List, a module variable, `return a`) is an error; `byVal a` is a copy. A set-up
block (form B, C) may still change the const / let it sets up.

**readonly, byVal, byRef at the call (Task 48.3, built - files/Ownership.md section 4):**
`show(readonly acc)` is the caller's demand: the call must not change or keep `acc`, checked
through every call `show` makes (truth table 4). When it does: an error at the call, naming
the line that changes it, and one at that line, naming the call. A value that is copied
anyway (an int, a string) can't be passed readonly; `readonly` stands only at a call or on a
parameter; through a function value it can't be checked - an error. `log(byVal acc)` gives a
copy; `log(byRef acc)` lends it, changeable (a List, a Map or an object). With
`[memory] assignment = "move"`, `byRef` and `readonly` only lend: given to a function that
keeps its parameter (D.100), stored or returned, they are an error; `Car b = byRef a` is a
local borrow of `a`.

**Form B on any variable (Task 32.2d, built - files/Classes.md section 4):** a block right after
a declaration's value sets that variable up further: a local (`Car c = new Car() { c.speed =
4 }`, also `let` / `const`, Lists and Maps), a class field, a static (32.2c). The block may
change only its own variable (an assignment to, or a method call on, another variable is a
compile error); variables declared in it are its own. A class field's value may be any
expression: each constructor sets the field and runs its block first, in field order, before
its own body - not again when it hands over with `this(...)`.

**Constructors (Task 32.2b, built - files/Classes.md section 2):** a class may have several; a call
picks the one whose parameters take the values given - by their number, then their types,
and when several fit, the one whose types match exactly (two that can't be told apart, or a
call that fits none or two equally, is a compile error). `this(...)` on a constructor's first
line lets another constructor make the object; this one's body then goes on. It can't use
the object's fields (the object isn't made yet); constructors calling each other in a circle
are a compile error. Named values with several constructors come later.

**Built (Task 32.10b, user decisions 2026-10-28 / 29):** `class Car` with fields (defaults
allowed), methods (`this`; a field's bare name means `this.field`) and an optional
constructor - `constructor(...)`, or `Car(...)` named like the class; none written: `Car()`
with every value field at its default and every object null. `Car("x")` and `new Car("x")`
are the same. An object lives on the heap with a **count**: a variable holds a reference
(null until set), `b = a` shares it, passing borrows it, and it is freed when its last holder
lets go - with what it holds (files/Object_Lifetime.md). `.` on null is a NullError; `== null` /
`is null`; `==` on two objects asks whether they are the same object. A `let` object can't be
replaced, but the object can still change. A constructor that fails frees its half-made
object. In C an object is `fu_Car*` with `fusion_count` first and helpers `__make`,
`__retain`, `__release`, `__set`; the constructor is the function `Car.new`. Not yet: several
constructors, inheritance, interfaces, private / static, `?.`, copies of objects (clone), a
printing a whole object. (Since built: a struct holding an object - D.097.)

Decided in the showcase
review (user, 2026-10-23/24, FEATURES Later): operator overloading off by default
(`[language] operatorOverloading`); several return values only with `[functions]
multiple_returns = true`; class objects are the only values that can be null (Task 30)

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

[< 042 MultipleReturns](042-MultipleReturns.md) | [Index](index.md) | [051 Inheritance >](051-Inheritance.md) <!-- nav -->
