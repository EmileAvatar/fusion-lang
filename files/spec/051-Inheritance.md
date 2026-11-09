[< 050 Classes](050-Classes.md) | [Index](index.md) | [052 Interfaces >](052-Interfaces.md) <!-- nav -->

# 051 Inheritance

## Inheritance

**Status:** [DONE 32.7] one parent (`inherits` / `extends`), `override`, `sealed`, `abstract`, `protected`, `super(...)` / `super.f()`, `typeOf(x)` - the truth table: files/Classes.md section 8. Favour composition over inheritance (D.083).

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

[< 050 Classes](050-Classes.md) | [Index](index.md) | [052 Interfaces >](052-Interfaces.md) <!-- nav -->
