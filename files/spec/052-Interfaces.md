[< 051 Inheritance](051-Inheritance.md) | [Index](index.md) | [060 Structs >](060-Structs.md) <!-- nav -->

# 052 Interfaces

## Interfaces and Contracts

**Status:** [DONE 32.5a] `interface`, `implements` (several), an interface building on several, an interface as a type, `is`, casts written in front, default methods behind `[interfaces] defaultMethods` - the truth table: files/Classes.md section 7; the built-in ToString, Default, Cloneable [DONE 32.5b] - copies of objects with `byVal`, `nocopy` / `noshare` fields

Description: Java-style interfaces with modern enhancements.

---

### Interface Definition

Description: Contract specification for implementation.

```
interface Movable
    void function move(Vector3 direction, float deltaTime)
    void function stop()
    property Speed: float { get; }

interface Damageable
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
class GameObject implements Movable, Damageable
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

[< 051 Inheritance](051-Inheritance.md) | [Index](index.md) | [060 Structs >](060-Structs.md) <!-- nav -->
