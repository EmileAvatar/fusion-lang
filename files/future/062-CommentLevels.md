[< 061 CommentHighlighting](061-CommentHighlighting.md) | [Index](index.md) | [070 NamingRules >](070-NamingRules.md) <!-- nav -->

# 062 Comment Levels

**Status:** design - comment levels and coding hints (SYN.036); no task yet

Contents: [Developer Experience Enhancements](#developer-experience-enhancements) | [Comment Level System (0-5)](#comment-level-system-0-5) | [Coding Hints System](#coding-hints-system)

## Developer Experience Enhancements

### Comment Level System (0-5)

**Status:** 📝 Proposed
**Purpose:** Standardized documentation and comment hierarchy for code quality and maintainability

**What:** A six-level comment system that provides structure for code documentation, from self-documenting code to deprecated features.

#### Comment Level Definitions

**Level 0: Naming Comments (Self-Documenting Code)**

Code should be written with descriptive names that make the logic and flow understandable without comments.

🧩 **Example:**
```fusion
// Bad - requires comments
int x = 10  // user age
string n = "John"  // user name

// Good - self-documenting
int userAge = 10
string userName = "John"
```

**Level 1: Inline Comments**

Single-line comments for classes, functions, variables, and inside code blocks (decisions, loops, structures).

🧩 **Example:**
```fusion
// User authentication service
class AuthService
    // Validate user credentials
    bool function validateUser(string username, string password)
        // Check if username exists
        if userExists(username)
            // Verify password hash matches
            return checkPasswordHash(password)
        return false
```

**Level 2: Documentation Comments (DocFeature)**

Block comments explaining code in detail, including usage examples. Used for library APIs and public interfaces.

🧩 **Example:**
```fusion
/**
 * Authenticates a user against the database.
 *
 * @param username - The user's login name
 * @param password - The user's password (will be hashed)
 * @return bool - True if authentication successful, false otherwise
 *
 * Example:
 *   bool success = authenticate("john_doe", "myPassword123")
 *   if success
 *       print("Login successful")
 */
bool function authenticate(string username, string password)
    // Implementation...
```

**Level 3: Implementation Comments**

Block comments explaining decision points and why code was implemented a certain way. Stored separately in implementation documentation and optionally shown in normal DocFeature.

🧩 **Example:**
```fusion
/**
 * IMPLEMENTATION DECISION:
 * Using bcrypt instead of SHA-256 for password hashing.
 *
 * Why: bcrypt includes automatic salting and is designed to be slow,
 * making brute-force attacks computationally expensive.
 *
 * Alternatives considered:
 * - SHA-256: Too fast, vulnerable to rainbow tables
 * - Argon2: Better but less widely supported in 2025
 *
 * Decision date: 2025-11-10
 * Decided by: Security team review
 */
string function hashPassword(string password)
    return bcrypt.hash(password, rounds: 12)
```

**Level 4: TODO Comments**

Single-line or block comments describing what needs to happen or be changed. Documented separately for tracking pending work.

🧩 **Example:**
```fusion
// TODO: Add rate limiting to prevent brute-force attacks
// TODO: Implement two-factor authentication support
// TODO: Add logging for failed login attempts

/**
 * TODO: Refactor authentication system
 * - Split into separate AuthValidator and AuthStorage classes
 * - Add support for OAuth2 providers (Google, GitHub)
 * - Implement session management with Redis
 * Priority: Medium
 * Estimated effort: 3 days
 */
```

**Level 5: Deprecated Comments**

Like Level 4, but for code that needs to be actively removed in the future. Documented separately for deprecation tracking.

🧩 **Example:**
```fusion
/**
 * DEPRECATED: Use authenticateWithHash() instead
 * This function will be removed in version 2.0
 * Reason: Uses insecure MD5 hashing
 * Migration: Replace calls with authenticateWithHash()
 * Removal date: 2026-01-01
 */
bool function authenticateOld(string username, string password)
    // Old implementation using MD5...
```

#### Comment Level Summary Table

| Level | Type | Purpose | Storage | Examples |
|-------|------|---------|---------|----------|
| 0 | Naming | Self-documenting code | In code (names) | `userAge`, `calculateTotalPrice()` |
| 1 | Inline | Quick explanations | In code | `// Check if user exists` |
| 2 | DocFeature | API documentation | In code + docs | Function/class documentation with examples |
| 3 | Implementation | Design decisions | Separate doc | Why certain algorithms/patterns were chosen |
| 4 | TODO | Pending work | Separate tracker | Features to add, bugs to fix |
| 5 | Deprecated | Code to remove | Separate tracker | Old APIs, legacy code |


#### IDE Integration

**fusionlib.IDE** can extract and manage comment levels:

```fusion
import fusionlib.IDE

// Extract all TODO comments from project
List<TodoComment> todos = CommentAnalyzer.extractTodos("./src")

// Extract deprecated code
List<DeprecatedCode> deprecated = CommentAnalyzer.extractDeprecated("./src")

// Generate implementation decisions document
string decisions = CommentAnalyzer.generateImplementationDoc("./src")
```

---

### Coding Hints System

**Status:** 📝 Proposed
**Purpose:** Provide intelligent code structure suggestions beyond basic syntax hints

**What:** Advanced IDE hints that suggest structural improvements, design patterns, and best practices (not just autocomplete).

#### Hint Categories

##### 1. Control Flow Simplification

Detect nested conditionals and suggest inversions or early returns.

🧩 **Before:**
```fusion
void function processUser(User user)
    if user != null
        if user.isActive()
            if user.hasPermission("admin")
                // Do something
```

💡 **Hint:** "Invert conditions and use early returns to reduce nesting"

🧩 **After:**
```fusion
void function processUser(User user)
    if user == null
        return
    if not user.isActive()
        return
    if not user.hasPermission("admin")
        return

    // Do something (now at top level)
```

##### 2. Extract Method

Suggest extracting nested logic into separate functions.

🧩 **Before:**
```fusion
void function handleOrder(Order order)
    if order.items.count > 0
        float total = 0.0
        for item in order.items
            total += item.price * item.quantity
            if item.discount > 0
                total -= item.price * item.discount
        order.total = total
```

💡 **Hint:** "Extract calculation logic into 'calculateOrderTotal()' method"

🧩 **After:**
```fusion
void function handleOrder(Order order)
    if order.items.count > 0
        order.total = calculateOrderTotal(order.items)

float function calculateOrderTotal(List<Item> items)
    float total = 0.0
    for item in items
        total += item.price * item.quantity
        if item.discount > 0
            total -= item.price * item.discount
    return total
```

##### 3. Design Pattern Suggestions

Suggest applicable design patterns based on code structure.

💡 **Hint Examples:**
- "Consider using Strategy pattern for multiple payment methods"
- "This looks like a Factory pattern candidate"
- "Consider Singleton for DatabaseConnection class"
- "Observer pattern could simplify event handling here"

##### 4. Best Practice Enforcement

Suggest improvements based on programming principles.

**DRY (Don't Repeat Yourself)**
```fusion
// Detects duplicate code blocks
💡 Hint: "Duplicate code detected in 3 locations - extract to shared method"
```

**SOLID Principles**
```fusion
// Class with too many responsibilities
💡 Hint: "Class has 12 methods with different concerns - consider splitting (Single Responsibility Principle)"
```

**YAGNI (You Aren't Gonna Need It)**
```fusion
// Unused code detection
💡 Hint: "Method 'calculateFutureFeature()' is never called - remove if not needed"
```

#### Hint API (fusionlib.IDE)

```fusion
import fusionlib.IDE

// Analyze code and get suggestions
class CodeHints
    static List<Hint> analyzeFile(string filePath)
    static List<Hint> analyzeClass(string className)
    static List<Hint> analyzeFunction(string functionName)

// Hint types
Enum HintType
    ControlFlowSimplification
    ExtractMethod
    DesignPattern
    DRYViolation
    SOLIDViolation
    Performance
    Security

class Hint
    HintType type
    string message
    int lineNumber
    string suggestion
    string codeExample
```

[< 061 CommentHighlighting](061-CommentHighlighting.md) | [Index](index.md) | [070 NamingRules >](070-NamingRules.md) <!-- nav -->
