[< 070 NamingRules](070-NamingRules.md) | [Index](index.md) | [080 Arrays >](080-Arrays.md) <!-- nav -->

# 071 Naming Exceptions

**Status:** design - with SYN.038

Contents: [Exception 1: Reserved Loop Counter Names](#exception-1-reserved-loop-counter-names) | [Exception 2: Generic Type Parameters (Reserved Names)](#exception-2-generic-type-parameters-reserved-names) | [Scope and Applicability](#scope-and-applicability) | [Error Messages](#error-messages) | [Configuration Levels](#configuration-levels) | [Implementation Notes](#implementation-notes) | [IDE Integration](#ide-integration) | [Benefits](#benefits)

## Exception 1: Reserved Loop Counter Names

**Allowed single-character names in loop contexts ONLY:**
- `i` - Primary loop counter (most common)
- `j` - Nested loop counter
- `k` - Third-level nested loop counter
- `x` - Horizontal coordinate loops
- `y` - Vertical coordinate loops
- `z` - Depth coordinate loops (3D)

**Valid Usage (within loops only):**
```fusion
// ✅ Valid: i, j, k in loop context
for i = 0 to 10
    print(i)

for i = 0 to 10
    for j = 0 to 5
        print("{i}, {j}")

// ✅ Valid: x, y for coordinates
for x = 0 to width
    for y = 0 to height
        drawPixel(x, y)

// ✅ Valid: nested loops with i, j, k
for i = 0 to rows
    for j = 0 to cols
        for k = 0 to depth
            matrix[i][j][k] = 0
```

**Invalid Usage (outside loop context):**
```fusion
// ❌ Error: 'i' not allowed outside loop context
int i = 5
print(i)

// ❌ Error: 'x' not allowed as function parameter
int function calculate(int x, int y)
    return x + y

// ❌ Error: 'j' not allowed as class field
class Counter
    private int j  // Error: Use meaningful name like 'count' or 'value'
```

**Context Detection:**
The compiler tracks whether a variable is declared inside:
- `for` loop initializer
- `while` loop body (local scope)
- `loop` statement body (local scope)

**Example: Valid and Invalid**
```fusion
// ✅ Valid loop counter
for i = 0 to 10
    print(i)  // 'i' valid here

// ❌ Error: 'i' used outside loop
print(i)  // Error: Variable 'i' out of scope or invalid name

// ✅ Valid: meaningful names required outside loops
int index = 0
for i = 0 to 10
    index = i * 2  // Both valid in their contexts
```

---

## Exception 2: Generic Type Parameters (Reserved Names)

**Allowed single-character type parameter names:**
- `T` - Generic Type (most common)
- `K` - Key type (for maps/dictionaries)
- `V` - Value type (for maps/dictionaries)

**Common Usage Patterns:**

**Generic Type `T`:**
```fusion
// ✅ Valid: T for generic type parameter
class Box<T>
    private T value

    public constructor(T item)
        value = item

    public T function get()
        return value

// ✅ Valid: Multiple type parameters
class Pair<T, U>
    public T first
    public U second

// ✅ Valid: Generic function
T function identity<T>(T item)
    return item

// ✅ Valid: Generic collection
class ArrayList<T>
    private List<T> items

    public void function add(T item)
        items.append(item)

    public T function get(int index)
        return items[index]
```

**Key-Value Types `K` and `V`:**
```fusion
// ✅ Valid: K for Key, V for Value
class Map<K, V>
    private Dictionary<K, V> data

    public void function put(K key, V value)
        data[key] = value

    public V function get(K key)
        return data[key]

// ✅ Valid: Dictionary usage
class Cache<K, V>
    private Map<K, V> storage

    public void function set(K key, V value)
        storage.put(key, value)

// ✅ Valid: Generic function with K, V
V function getOrDefault<K, V>(Map<K, V> map, K key, V defaultValue)
    if map.containsKey(key)
        return map.get(key)
    return defaultValue
```

**Descriptive Type Parameter Names (Alternative):**
While `T`, `K`, `V` are allowed as single-character names, developers may also use longer descriptive names:
```fusion
// Also valid: Descriptive type parameter names
class Box<TItem>
    private TItem value

class Map<TKey, TValue>
    private Dictionary<TKey, TValue> data

// Both styles allowed - project lead decides coding standards
```

**IDE Tooltip Support:**
When hovering over generic type parameters in IDEs:
```fusion
// Hover over 'T' in code
ArrayList<String> names = ArrayList<String>()
// IDE Tooltip: "T = String (generic type parameter)"

// Hover over 'K' or 'V'
Map<int, String> userMap = Map<int, String>()
// IDE Tooltip:
//   "K = int (key type parameter)"
//   "V = String (value type parameter)"
```

**Type Parameter Constraints:**
```fusion
// ✅ Valid: T with constraint
class NumberBox<T> where T : Number
    private T value

// ✅ Valid: Multiple constraints
class Sortable<T> where T : Comparable, Cloneable
    private List<T> items

    public void function sort()
        items.sort()  // T implements Comparable
```

---

## Scope and Applicability

**Applies to:**
- Local variables in functions
- Function parameters
- Class fields (private, protected, public)
- Struct fields
- Property backing fields
- Lambda parameters (if not inferred)

**Does NOT apply to:**
- Generic type parameters (`T`, `K`, `V`) - always allowed as single-char
- Loop counters (`i`, `j`, `k`, `x`, `y`, `z`) - allowed in loop context only
- Constant names (follow separate naming conventions)
- Enum values (follow separate naming conventions)
- Interface method parameters (often abbreviated)

---

## Error Messages

**Example 1: Variable name too short**
```fusion
int x = 10
```
**Error:**
```
Error: Variable name 'x' is too short (min 3 characters required in strict mode)
  at line 1, column 5
  Hint: Use a descriptive name like 'count', 'index', or 'value'
  Hint: Single-character names are only allowed for loop counters (i, j, k, x, y, z) within loops
```

**Example 2: Loop counter outside loop**
```fusion
int i = 0
while i < 10
    print(i)
    i = i + 1
```
**Error:**
```
Error: Variable name 'i' is too short (min 3 characters required in strict mode)
  at line 1, column 5
  Hint: Single-character name 'i' is only allowed as a loop counter inside a 'for' loop initializer
  Hint: Use 'for i = 0 to 10' instead, or rename to a descriptive name like 'index' or 'counter'
```

**Example 3: Correct usage**
```fusion
// ✅ All valid
for i = 0 to 10
    int count = i * 2  // 'i' valid in loop, 'count' is 5 chars
    print(count)

class Box<T>  // 'T' allowed as type parameter
    private T value  // 'value' is 5 chars (valid)
```

---

## Configuration Levels

**Project managers can configure strictness levels:**

**Level 1: Lenient (minLength = 2)**
```json
{ "minVariableNameLength": 2 }
```
- Allows: `id`, `x`, `y`, `no`, `ok`
- Good for: Prototyping, small projects

**Level 2: Balanced (minLength = 3, default)**
```json
{ "minVariableNameLength": 3 }
```
- Allows: `age`, `idx`, `key`, `val`
- Good for: Most projects, teams

**Level 3: Strict (minLength = 4)**
```json
{ "minVariableNameLength": 4 }
```
- Requires: `name`, `user`, `count`, `index`
- Good for: Enterprise, large teams

**Level 4: Very Strict (minLength = 5)**
```json
{ "minVariableNameLength": 5 }
```
- Requires: `userId`, `count`, `index`, `value`
- Good for: Critical systems, strict coding standards

**Per-Project Configuration:**
Project leads decide based on:
- Team size and experience
- Project complexity
- Maintenance requirements
- Industry standards (e.g., finance, healthcare)

---

## Implementation Notes

**Semantic Analyzer Changes:**
1. Check variable/parameter names during declaration
2. Track variable declaration context (loop vs. non-loop)
3. Enforce minimum length (configurable)
4. Allow exceptions for:
   - Loop counters (`i`, `j`, `k`, `x`, `y`, `z`) in loop context
   - Generic type parameters (`T`, `K`, `V`)
5. Provide helpful error messages with suggestions

**Configuration System:**
- Read from `project.json` under `strictMode` section
- Fall back to `~/.fusion/strict.json` for user defaults
- Command-line override: `fusion build --strict-var-length=3`

**Compiler Flags:**
```bash
# Enable strict mode with custom min length
fusion build --strict --min-var-length=4

# Disable variable name checking (override strict mode)
fusion build --no-strict-names

# Show all variable name violations (warnings, don't fail)
fusion build --warn-short-names
```

---

## IDE Integration

**Real-time Validation:**
- IDE underlines short variable names as you type
- Tooltip explains minimum length requirement
- Quick-fix suggestions: "Rename to descriptive name"

**Code Completion:**
- IDE suggests meaningful names based on type
  - `int` → suggests "count", "index", "value"
  - `string` → suggests "name", "text", "message"
  - `bool` → suggests "isActive", "hasValue", "enabled"

**Refactoring:**
- "Rename variable" command checks minimum length
- Warns if new name is too short
- Auto-suggests longer alternatives

---

## Benefits

**For Code Quality:**
- ✅ Enforces meaningful variable names
- ✅ Reduces "code smell" from poor naming
- ✅ Makes code self-documenting
- ✅ Easier code reviews

**For Maintenance:**
- ✅ New developers understand code faster
- ✅ Less need for comments (names explain purpose)
- ✅ Reduces bugs from variable confusion
- ✅ Easier refactoring

**For Teams:**
- ✅ Consistent naming standards across projects
- ✅ Configurable per project/team needs
- ✅ Enforced automatically (no manual code reviews needed)
- ✅ Exceptions for common patterns (loops, generics)

[< 070 NamingRules](070-NamingRules.md) | [Index](index.md) | [080 Arrays >](080-Arrays.md) <!-- nav -->
