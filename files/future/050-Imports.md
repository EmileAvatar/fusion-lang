[< 040 CrossLanguage](040-CrossLanguage.md) | [Index](index.md) | [060 Comments >](060-Comments.md) <!-- nav -->

# 050 Imports

**Status:** design - importing only some names (MOD.005), grouped import blocks (MOD.008); namespaces and modules: Task 57 (D.136)

Contents: [Multi-Import & Parameter Syntax](#multi-import--parameter-syntax) | [Feature 1: Grouped Import Blocks](#feature-1-grouped-import-blocks) | [Feature 2: Multi-line Function Parameters](#feature-2-multi-line-function-parameters) | [Feature 3: Mixed Import Styles](#feature-3-mixed-import-styles) | [Examples](#examples) | [Implementation Details](#implementation-details) | [Style Guide Recommendations](#style-guide-recommendations) | [Clarification: Type Casing](#clarification-type-casing)

## Multi-Import & Parameter Syntax

**Status:** 📝 Proposed
**Priority:** Medium (syntax enhancement)
**Impact:** Grammar changes to EBNF
**Depends On:** Basic compiler completion

**Purpose:** Support Go-style grouped imports and multi-line function parameters for better code organization

---

### Feature 1: Grouped Import Blocks

**Current Syntax:**
```fusion
import Fusion.Core
import Fusion.Collections
import Fusion.IO
import Fusion.Net
```

**Proposed Grouped Syntax (Go-style):**
```fusion
import (
    Fusion.Core
    Fusion.Collections
    Fusion.IO
    Fusion.Net
)
```

**Benefits:**
- Cleaner organization for multiple imports
- Clear visual grouping
- Less repetition of `import` keyword
- Standard in many modern languages (Go, Kotlin)

**Grammar Changes Required:**
```ebnf
import_statement = "import" ( single_import | grouped_import )
single_import = module_path
grouped_import = "(" newline { module_path newline } ")"
module_path = identifier { "." identifier }
```

---

### Feature 2: Multi-line Function Parameters

**Current Syntax (single-line):**
```fusion
int function createUser(string name, string surname, int age, Date birthDate)
```

**Proposed Multi-line Syntax:**
```fusion
// Stepped/formatted parameters
int function createUser(string name,      // first name
                        string surname,   // last name
                        int age,          // user age
                        Date birthDate)   // date of birth
```

**Benefits:**
- Better readability for functions with many parameters
- Inline documentation via comments
- IDE parameter hints enhanced
- Common in enterprise codebases

**Implementation Notes:**
- Comments are standard `//` comments (already supported)
- Compiler ignores comments, preserves formatting
- No grammar change needed - already valid syntax
- IDE formatter can auto-align parameters

---

### Feature 3: Mixed Import Styles

**Allow mixing single and grouped imports:**
```fusion
import Fusion.Core  // Single import

import (
    Fusion.Collections
    Fusion.IO
    Fusion.Net
)

import Fusion.Math  // Another single import
```

**Style Recommendation:**
- Use grouped imports for related modules
- Use single imports for one-off imports
- Keep grouped imports together

---

### Examples

**Example 1: Web Application Imports**
```fusion
// Before
import Fusion.Core
import Fusion.Collections
import Fusion.IO
import Fusion.Net
import Fusion.Web
import Fusion.Database
import Fusion.Crypto

// After (grouped)
import (
    Fusion.Core
    Fusion.Collections
    Fusion.IO
    Fusion.Net
    Fusion.Web
    Fusion.Database
    Fusion.Crypto
)
```

**Example 2: Categorized Imports**
```fusion
// Core modules
import (
    Fusion.Core
    Fusion.Collections
    Fusion.Math
)

// Network modules
import (
    Fusion.Net
    Fusion.Web
)

// Database modules
import (
    Fusion.Database
    Fusion.Crypto
)
```

**Example 3: Multi-line Function with Comments**
```fusion
import Fusion.Database

User function registerUser(
    string email,        // User's email address (must be valid)
    string password,     // Hashed password (min 8 chars)
    string firstName,    // First name
    string lastName,     // Last name
    int age,             // Age (must be 18+)
    Date registeredDate, // Registration timestamp
    bool isActive)       // Account active status

    // Function implementation
    User user = User(email, password, firstName, lastName)
    Database.save(user)
    return user
```

**Example 4: Complex Function Signature**
```fusion
import (
    Fusion.Collections
    Fusion.Database
)

List<Order> function searchOrders(
    int customerId,           // Customer ID to filter by
    Date startDate,           // Start of date range
    Date endDate,             // End of date range
    OrderStatus status,       // Order status filter
    int pageNumber = 1,       // Pagination: page number (default 1)
    int pageSize = 20,        // Pagination: items per page (default 20)
    bool includeArchived = false)  // Include archived orders (default false)

    // Implementation
    return Database.query()
        .where("customerId", customerId)
        .where("orderDate", ">=", startDate)
        .where("orderDate", "<=", endDate)
        .where("status", status)
        .paginate(pageNumber, pageSize)
        .toList()
```

---

### Implementation Details

**Grouped Imports:**
1. Update EBNF grammar for import statements
2. Lexer already handles parentheses and newlines
3. Parser modification to recognize grouped syntax
4. Validation: ensure no duplicate imports
5. Code generator: flatten to single imports in C code

**Multi-line Parameters:**
1. No grammar change needed (already valid)
2. Formatter tool can auto-align parameters (future IDE feature)
3. IDE can extract parameter comments for hints
4. Comments preserved in AST for documentation generation

**Compatibility:**
- Single-line imports still fully supported
- Mixed styles allowed
- No breaking changes to existing code

---

### Style Guide Recommendations

**When to use grouped imports:**
- 3+ imports from same namespace
- Related functional modules (all network, all database, etc.)
- Standard library modules vs third-party

**When to use multi-line parameters:**
- 4+ parameters
- Complex parameter types
- When parameter documentation is important
- Enterprise/team codebases

**Formatting:**
```fusion
// Good: aligned parameters
int function createOrder(
    int customerId,    // Customer ID
    int productId,     // Product ID
    int quantity)      // Order quantity

// Bad: misaligned
int function createOrder(
int customerId, // Customer ID
int productId,     // Product ID
    int quantity)  // Order quantity
```

---

### Clarification: Type Casing

**Question:** Is `String` vs `string` significant?

**Answer:**
- **`string`** = primitive type (value type)
- **`String`** = class object (reference type, for autoboxing)

**Similar to other languages:**
- Java: `int` (primitive) vs `Integer` (wrapper class)
- C#: `int` (primitive) vs `Int32` (struct)
- Fusion: `string` (primitive) vs `String` (class for advanced operations)

**Example:**
```fusion
string name = "Alice"  // Stack-allocated primitive
String name2 = String("Alice")  // Heap-allocated object with methods

// Autoboxing (implicit conversion)
string primitive = "test"
String object = primitive  // Auto-converts to String object
```

**Grammar Impact:**
- Both `string` and `String` are valid types
- Types ARE case-sensitive
- `string` ≠ `String` (different types, autoboxing allowed)

[< 040 CrossLanguage](040-CrossLanguage.md) | [Index](index.md) | [060 Comments >](060-Comments.md) <!-- nav -->
