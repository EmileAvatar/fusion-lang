[< 100 Concurrency](100-Concurrency.md) | [Index](index.md) | [120 Errors >](120-Errors.md) <!-- nav -->

# 110 Generics

## Generics and Templates

**Status:** [PARTLY] the built-in `List<T>` and `Map<K, V>` (18.5); generic functions and types of your own [PLANNED 33]

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
T function findMax<T>(List<T> items) where T implements Comparable<T>
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

[< 100 Concurrency](100-Concurrency.md) | [Index](index.md) | [120 Errors >](120-Errors.md) <!-- nav -->
