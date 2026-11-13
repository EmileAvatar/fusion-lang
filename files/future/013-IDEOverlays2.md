[< 012 IDEOverlays](012-IDEOverlays.md) | [Index](index.md) | [014 IDEOverlaySettings >](014-IDEOverlaySettings.md) <!-- nav -->

# 013 IDE Overlays 2

**Status:** idea - no task

Contents: [Feature 5: Naming Quality Analysis (Dictionary Builder)](#feature-5-naming-quality-analysis-dictionary-builder) | [Feature 6: Nested Loop Warning (Performance)](#feature-6-nested-loop-warning-performance) | [Feature 7: Nested Control Flow Refactoring](#feature-7-nested-control-flow-refactoring)

## Feature 5: Naming Quality Analysis (Dictionary Builder)

**Purpose:** Build a dictionary of all identifiers (variables, functions, classes, etc.) and suggest better names based on usage context and clarity.

**Example - Poor Names:**
```fusion
class U
    private string n
    private int a

    public void function p()
        print("{n} is {a} years old")

void function main()
    U u = U()
    u.n = "Alice"
    u.a = 25
    u.p()
```

**IDE Suggestions:**

**1. Class Name `U`:**
```
⚠️ Class name 'U' is unclear (1 character)
💡 Suggested names based on usage:
   - User (contains name and age)
   - Person
   - Customer
```

**2. Field Name `n`:**
```
⚠️ Field 'n' is unclear (1 character)
💡 Suggested names based on type and usage:
   - name (most common for string)
   - fullName
   - userName
```

**3. Method Name `p()`:**
```
⚠️ Method 'p' is unclear (1 character)
💡 Suggested names based on behavior:
   - print()
   - printInfo()
   - displayDetails()
```

**Refactored Code:**
```fusion
class User
    private string name
    private int age

    public void function printInfo()
        print("{name} is {age} years old")

void function main()
    User user = User()
    user.name = "Alice"
    user.age = 25
    user.printInfo()
```

**IDE Features:**

**1. Naming Dictionary:**
- Tracks all identifiers in project
- Analyzes usage patterns
- Builds context-aware suggestions

**2. Clarity Score:**
```fusion
class User      // Clarity: 95% ✅
class U         // Clarity: 20% ⚠️
class UsrMgr    // Clarity: 60% (abbreviation)
```

**3. Auto-complete with Context:**
```fusion
// Typing: int c
// Suggestions:
//   - count (common int name)
//   - counter
//   - currentIndex
```

**Configuration:**
```json
{
  "namingQuality": {
    "enabled": true,
    "minNameLength": 3,
    "flagAbbreviations": true,
    "suggestAlternatives": true,
    "clarityThreshold": 50,  // % clarity score to warn
    "buildDictionary": true,
    "learnFromProject": true  // Learn naming patterns from codebase
  }
}
```

---

## Feature 6: Nested Loop Warning (Performance)

**Purpose:** Detect nested loops with potential O(n²) or O(n³) complexity and suggest optimization opportunities.

**Example - O(n²) Nested Loop:**
```fusion
void function findPairs(List<int> numbers)
    for i = 0 to numbers.length  // O(n)
        for j = 0 to numbers.length  // O(n) → O(n²) total
            if numbers[i] + numbers[j] == 10
                print("{numbers[i]} + {numbers[j]} = 10")
```

**IDE Warning:**
```
⚠️ Nested loop detected: O(n²) complexity
  Outer loop: line 2 (n iterations)
  Inner loop: line 3 (n iterations)
  Total: n × n = n² iterations

💡 Optimization suggestions:
  1. Use HashMap for O(n) lookup
  2. Sort and use two-pointer technique
  3. Break early when possible
```

**Optimized Code (Example):**
```fusion
void function findPairs(List<int> numbers)
    Set<int> seen = Set<int>()

    for num in numbers  // O(n)
        int complement = 10 - num
        if seen.contains(complement)  // O(1) lookup
            print("{num} + {complement} = 10")
        seen.add(num)

    // Total: O(n) instead of O(n²)
```

**IDE Visualization:**

**1. Complexity Indicator:**
```fusion
for i = 0 to n      // 🟢 O(n)
    for j = 0 to n  // 🟡 O(n²) - Nested loop warning
        for k = 0 to n  // 🔴 O(n³) - High complexity!
```

**2. Iteration Count Estimate:**
```
Loop at line 2:
  Estimated iterations: 1,000,000 (n=1000, n²=1,000,000)
  ⚠️ High iteration count - consider optimization
```

**Configuration:**
```json
{
  "nestedLoops": {
    "enabled": true,
    "warnAtComplexity": "O(n²)",  // or "O(n³)"
    "errorAtComplexity": "O(n³)",
    "suggestOptimizations": true,
    "showIterationEstimate": true,
    "estimatedInputSize": 1000  // For iteration calculations
  }
}
```

---

## Feature 7: Nested Control Flow Refactoring

**Purpose:** Detect deeply nested IF/switch statements and suggest extraction to separate functions for improved readability.

**Example - Deeply Nested Control Flow:**
```fusion
int function processRequest(Request req)
    if req.type == "GET"
        if req.hasAuth
            if req.user.role == "admin"
                if req.path.startsWith("/admin")
                    return handleAdminGet(req)
                else
                    return ErrorCode.Forbidden
            else
                return handleUserGet(req)
        else
            return ErrorCode.Unauthorized
    else if req.type == "POST"
        if req.hasAuth
            if req.body != null
                return handlePost(req)
            else
                return ErrorCode.BadRequest
        else
            return ErrorCode.Unauthorized
    else
        return ErrorCode.MethodNotAllowed
```

**IDE Warning:**
```
⚠️ Complex control flow detected (cyclomatic complexity: 8)
💡 Consider extracting to separate functions:
  - extractAuthCheck()
  - extractGetHandler()
  - extractPostHandler()
```

**Refactored Code:**
```fusion
int function processRequest(Request req)
    if not req.hasAuth
        return ErrorCode.Unauthorized

    match req.type
        case "GET":
            return handleGet(req)
        case "POST":
            return handlePost(req)
        default:
            return ErrorCode.MethodNotAllowed

int function handleGet(Request req)
    if req.user.role == "admin" and req.path.startsWith("/admin")
        return handleAdminGet(req)
    else if req.user.role == "admin"
        return ErrorCode.Forbidden
    else
        return handleUserGet(req)

int function handlePost(Request req)
    if req.body == null
        return ErrorCode.BadRequest
    return handlePostWithBody(req)
```

**IDE Visualization:**

**1. Complexity Meter:**
```
Cyclomatic Complexity: 8 🟠
  1-5:   🟢 Simple
  6-10:  🟡 Moderate - consider refactoring
  11-15: 🟠 Complex - should refactor
  16+:   🔴 Very complex - must refactor
```

**2. Visual Nesting Indicator:**
```
Nesting depth visualization (left margin):
|     if                 // Depth 1
| |     if               // Depth 2
| | |     if             // Depth 3 ⚠️
| | | |     if           // Depth 4 🔴
```

**Configuration:**
```json
{
  "controlFlowComplexity": {
    "enabled": true,
    "maxComplexity": 10,
    "warnAtComplexity": 6,
    "maxNestingDepth": 3,
    "suggestExtraction": true,
    "suggestMatchStatement": true  // Suggest 'match' instead of if-else chains
  }
}
```

[< 012 IDEOverlays](012-IDEOverlays.md) | [Index](index.md) | [014 IDEOverlaySettings >](014-IDEOverlaySettings.md) <!-- nav -->
