[< 062 CommentLevels](062-CommentLevels.md) | [Index](index.md) | [071 NamingExceptions >](071-NamingExceptions.md) <!-- nav -->

# 070 Naming Rules

**Status:** design - a minimum variable-name length in strict mode, default 3 (SYN.038); no task yet

## Enhanced Option Strict - Variable Naming Rules

**Status:** 📝 Proposed
**Priority:** Medium (code quality enhancement)
**Impact:** Compiler semantic analyzer, strict mode
**Depends On:** Basic compiler completion

**Purpose:** Extend `option strict` with configurable variable naming rules to enforce meaningful identifier names and improve code readability.

---

### Overview

- Poor variable naming is a common source of code maintenance issues.
- Single-character variable names (except in specific contexts) make code harder to understand and maintain.
- This feature extends `option strict` to enforce minimum variable name lengths with intelligent exceptions for common cases.

---

### Important Context: When Single-Character Names Are Acceptable

**🎓 Tutorial/Demo/Toy Code:**
- Single-character variables (e.g., `x`, `y`, `n`) are **acceptable** for ease of use in:
  - Tutorial code and learning materials
  - Demo applications and example code
  - Toy projects and prototypes
- **Reason:** Simplicity helps learners focus on concepts, not naming
- **Recommendation:** Disable strict mode for educational projects

**🏢 Production Code:**
- Single-character variables should be **actively prevented** in production
- **Reason:** Code maintainability, team collaboration, long-term support
- **Recommendation:** Enable strict mode with minimum 3-4 character requirement

**🔬 Math/Science/Engineering Exception:**
- Mathematical, scientific, and engineering modules **may use single-character variables** due to domain conventions
- **Common conventions:**
  - `m` = mass
  - `v` = velocity
  - `a` = acceleration
  - `t` = time
  - `F` = force
  - `E` = energy
  - `P` = power
  - `c` = speed of light constant
  - `g` = gravitational constant
  - `h` = Planck's constant
  - `π` (pi) = mathematical constant (~3.14159)
  - `e` = Euler's number (~2.71828)
  - `θ` (theta) = angle
  - `φ` (phi) = phase angle
  - `Δ` (delta) = change/difference
  - `Σ` (sigma) = summation
  - `λ` (lambda) = wavelength
- **Reason:** These are **universal domain conventions** recognized across scientific literature
- **Recommendation:** Allow short names in specific modules (Math, Physics, Chemistry, Engineering)

**Configuration Strategy by Project Type:**

```json
// Tutorial/Demo Project
{
  "strictMode": {
    "enabled": false  // Allow short names for simplicity
  }
}

// Production Web/Business Application
{
  "strictMode": {
    "enabled": true,
    "minVariableNameLength": 3,
    "enforcementLevel": "error"  // Block compilation
  }
}

// Scientific/Math Module
{
  "strictMode": {
    "enabled": true,
    "minVariableNameLength": 3,
    "allowShortNamesInModules": [
      "Math",
      "Physics",
      "Chemistry",
      "Engineering",
      "Geometry",
      "Calculus"
    ]
  }
}

// Hybrid Project (tutorial + production)
{
  "strictMode": {
    "enabled": true,
    "minVariableNameLength": 3,
    "enforcementLevel": "warning",  // Warn, don't block (for migration)
    "excludePaths": [
      "./examples/**",
      "./tutorials/**",
      "./demos/**"
    ]
  }
}
```

**Annotation-Based Exception (Future Feature):**
```fusion
// Allow short names in this function using annotation
@allow-short-names
float function calculateKineticEnergy(float m, float v)
    // m = mass, v = velocity (domain conventions)
    return 0.5 * m * v * v  // KE = ½mv²

// Or allow for entire module
@allow-short-names
module Physics.Kinematics
    // All functions in this module can use short names
```

---

**Problem:**
```fusion
// Hard to understand
int x = 10
string n = "Alice"
float p = 3.14
bool f = true

// What do these variables represent?
```

**Solution with Enhanced Strict Mode:**
```fusion
option strict

// Compiler error: Variable names must be at least 3 characters
int count = 10        // ✅ Valid
string name = "Alice" // ✅ Valid
float price = 3.14    // ✅ Valid
bool isActive = true  // ✅ Valid

int x = 10  // ❌ Error: Variable name 'x' is too short (min 3 characters)
```

---

### Feature: Minimum Variable Name Length

**Configuration:**
- **Default minimum length:** 3 characters
- **Configurable:** Project lead can adjust (e.g., 2, 3, 4, 5 characters)
- **Applies to:** Local variables, function parameters, class fields, properties
- **Does NOT apply:** Type parameters (generics), loop counters (see exceptions)

**Configuration Options (project.json):**
```json
{
  "strictMode": {
    "enabled": true,
    "minVariableNameLength": 3,
    "allowSingleCharLoopCounters": true,
    "allowGenericTypeParams": true
  }
}
```

**Alternative Configuration (.fusion/strict.json):**
```json
{
  "variableNaming": {
    "minLength": 3,
    "exceptions": {
      "loopCounters": ["i", "j", "k", "x", "y", "z"],
      "typeParameters": ["T", "K", "V"]
    }
  }
}
```

[< 062 CommentLevels](062-CommentLevels.md) | [Index](index.md) | [071 NamingExceptions >](071-NamingExceptions.md) <!-- nav -->
