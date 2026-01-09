# Fusion Annotations, Modes, and Safety System

Description: Complete guide to Fusion's annotation system, strict mode, unsafe mode, and safety features.

---

## Overview

Description: Fusion provides multiple layers of safety and control through modes and annotations.

**Three Safety Modes**:
* **Standard Mode** - Balanced safety and flexibility (default)
* **Strict Mode** - Maximum safety with strict enforcement
* **Unsafe Mode** - Minimal restrictions for performance-critical code

**Annotation System**:
* Code-level metadata and directives
* Compiler hints and optimizations
* IDE integration and tooling support

---

## Compilation Modes

Description: Three distinct compilation modes with different safety guarantees.

---

### 1. Standard Mode (Default)

Description: Balanced approach with reasonable safety checks.

**Enabled By Default**:
* Null safety warnings
* Type checking
* Automatic loop protection
* Race condition detection (warning)
* Memory leak detection (warning)

**Allowed**:
* Type inference with `var`
* Implicit type casts (widening)
* Weak pointers (with warning)
* Optional null checks

**Configuration**:
```json
{
  "compiler": {
    "strictMode": false,
    "unsafeMode": false
  }
}
```

**Example Code**:
```fusion
// Standard mode - warnings but compiles
class Player
    Weak<Game> gameRef  // Warning: Use of weak pointer
    
    void function update()
        var health = 100  // OK: Type inference allowed
        
        // Null check optional (warning if missing)
        if gameRef?.null
            return
        
        gameRef.processPlayer(this)
```

---

### 2. Strict Mode

Description: Maximum safety with strict enforcement of best practices.

**Enforces**:
* All null checks required
* No weak pointers (compilation error)
* No implicit casts
* Explicit types (no `var` keyword)
* All functions must have return type
* Unused variables are errors
* All warnings become errors

**Forbidden**:
* `Weak<T>` pointers
* `goto` statements
* Implicit type conversion
* Missing null checks
* Type inference in sensitive contexts

**Configuration**:
```json
{
  "compiler": {
    "strictMode": true,
    "warningsAsErrors": true
  },
  "language": {
    "allowWeakPointers": false,
    "requireExplicitTypes": true,
    "enforceNullChecks": true
  }
}
```

**Example Code**:
```fusion
// Strict mode - maximum safety
class Player
    // Weak<Game> gameRef  // ERROR: Weak pointers not allowed
    Shared<Game> gameRef  // OK: Use shared pointer instead
    
    void function update()
        // var health = 100  // ERROR: Must use explicit type
        int health = 100  // OK: Explicit type
        
        // Null check mandatory
        if gameRef is null  // ERROR if missing this check
            return
        
        gameRef.processPlayer(this)
```

---

### 3. Unsafe Mode

Description: Minimal restrictions for performance-critical or embedded systems.

**Allows**:
* Raw pointers
* Manual memory management
* `goto` statements
* Unchecked array access
* Disabled automatic protections
* Direct memory manipulation

**Use Cases**:
* Embedded systems
* Real-time systems
* Performance-critical paths
* FFI (Foreign Function Interface)
* Hardware interfacing

**Configuration**:
```json
{
  "compiler": {
    "unsafeMode": true,
    "strictMode": false
  },
  "memory": {
    "enableRawPointers": true,
    "defaultMode": "raw-pointers"
  },
  "loop": {
    "autoProtection": false
  }
}
```

**Example Code**:
```fusion
// Unsafe mode - manual control
unsafe  // Required block for unsafe operations
    // Raw pointer allocation
    Player* playerPtr = allocate<Player>(1)
    playerPtr.initialize("Hero", 100)
    
    // Direct memory access
    int* healthPtr = &playerPtr.health
    *healthPtr = 50
    
    // Manual cleanup required
    deallocate(playerPtr)

// Unsafe operations outside unsafe block = ERROR
```

---

## Annotations System

Description: Metadata and directives for code control.

---

### Built-in Annotations

Description: Standard annotations provided by Fusion.

---

#### @Performance

Description: Marks performance-critical code for optimization.

**Usage**:
```fusion
@Performance
class PhysicsEngine
    @Performance
    void function updateCollisions(float deltaTime)
        // Compiler applies aggressive optimization
        // Profiler tracks execution time
```

**Effects**:
* Compiler prioritizes optimization
* Profiler automatically monitors
* IDE shows performance metrics
* Generates performance report

**Configuration**:
```json
{
  "annotations": {
    "customAnnotations": {
      "@Performance": {
        "enabled": true,
        "optimizationLevel": 3,
        "profileExecution": true
      }
    }
  }
}
```

---

#### @Deprecated

Description: Marks deprecated code for eventual removal.

**Usage**:
```fusion
@Deprecated("Use NewClass instead", version = "2.0.0")
class OldClass
    void function oldMethod()
        // ...

// Using deprecated code
OldClass obj = OldClass()  // Warning: Deprecated since 2.0.0
```

**Effects**:
* IDE shows warning with message
* Compiler warning (or error in strict mode)
* Documentation generation includes deprecation notice
* Migration suggestions

---

#### @Unsafe

Description: Marks unsafe code blocks explicitly.

**Usage**:
```fusion
@Unsafe
void function directMemoryAccess()
    unsafe
        // Unsafe operations
        int* ptr = allocate<int>(10)
        // ...
        deallocate(ptr)
```

**Effects**:
* Requires explicit unsafe block
* IDE highlights unsafe operations
* Code review flagged automatically
* Audit log entry

---

#### @NoOptimize

Description: Prevents compiler optimization.

**Usage**:
```fusion
@NoOptimize
void function debugFunction()
    // Debugging code - keep as-is
    printDebugInfo()
    checkInvariants()
```

**Effects**:
* Compiler skips optimization
* Preserves exact code structure
* Useful for debugging
* Time-critical timing preservation

---

#### @Inline

Description: Suggests function inlining.

**Usage**:
```fusion
@Inline
int function add(int a, int b)
    return a + b

// Compiler inlines this call
int result = add(5, 10)  // Becomes: int result = 5 + 10
```

**Effects**:
* Compiler inlines function call
* Reduces function call overhead
* May increase code size
* Performance improvement

---

#### @ThreadSafe

Description: Marks code as thread-safe.

**Usage**:
```fusion
@ThreadSafe
class Counter
    private static int count = 0
    
    @ThreadSafe
    public static void function increment()
        lock(this)
            count += 1
```

**Effects**:
* Documents thread safety
* Compiler verifies thread safety
* IDE shows thread-safe indicator
* Generated documentation includes thread safety info

---

#### @RequiresReview

Description: Flags code requiring review.

**Usage**:
```fusion
@RequiresReview("Security critical - validate input")
void function processUserData(string data)
    // Critical security code
```

**Effects**:
* Code review workflow triggered
* Cannot merge without review
* Reviewer notification sent
* Audit trail created

---

#### @Test

Description: Marks test functions.

**Usage**:
```fusion
@Test
void function testAddition()
    assert(add(2, 2) == 4)

@Test(timeout = 1000)
void function testPerformance()
    // Must complete within 1 second
```

**Effects**:
* Test runner discovers tests
* IDE shows test indicator
* Can set timeout limits
* Test results tracked

---

#### @Region

Description: Code folding regions (alternative to #Region).

**Usage**:
```fusion
@Region("Initialization")
void function init()
    // ...

void function setup()
    // ...
@EndRegion
```

---

### Custom Annotations

Description: Define project-specific annotations.

**Definition**:
```json
{
  "annotations": {
    "customAnnotations": {
      "@GameLogic": {
        "enabled": true,
        "description": "Marks game-specific logic",
        "parameters": {
          "module": "string",
          "priority": "int"
        },
        "effects": {
          "documentationCategory": "Game Logic",
          "ideIcon": "game-controller"
        }
      },
      "@NetworkSync": {
        "enabled": true,
        "description": "Marks network-synchronized code",
        "parameters": {
          "frequency": "int",
          "reliable": "bool"
        }
      }
    }
  }
}
```

**Usage**:
```fusion
@GameLogic(module = "combat", priority = 1)
class CombatSystem
    @NetworkSync(frequency = 60, reliable = true)
    void function syncPlayerState(Player player)
        // Network synchronization code
```

---

## Annotation Syntax

Description: How to use annotations in Fusion code.

**Basic Syntax**:
```fusion
// Single annotation
@AnnotationName
class MyClass

// With parameters
@AnnotationName(param = value)
class MyClass

// Multiple parameters
@AnnotationName(param1 = value1, param2 = value2)
class MyClass

// Multiple annotations
@Annotation1
@Annotation2
@Annotation3
class MyClass
```

**Annotation Targets**:
* Classes
* Functions/Methods
* Properties
* Variables
* Parameters
* Modules
* Enums

---

## Loop Protection Annotations

Description: Control automatic loop protection.

---

### @NoLoopProtection

Description: Disables automatic loop safety.

**Usage**:
```fusion
@NoLoopProtection
void function infiniteLoop()
    while true  // No automatic protection
        processRequest()
```

**Warning**: Use with extreme caution!

---

### @MaxIterations

Description: Set custom iteration limit.

**Usage**:
```fusion
@MaxIterations(10000000)
void function heavyComputation()
    for i in 1...50000000
        // Custom limit instead of default
        process(i)
    end loop
```

---

## Mode Combinations

Description: How modes and annotations work together.

---

### Standard + @Performance

```fusion
// Standard mode with performance hints
@Performance
class GameEngine
    void function update(float dt)
        var count = calculateCount()  // OK in standard
```

**Result**: Optimized code with standard safety checks

---

### Strict + @Unsafe

```fusion
// Strict mode with selective unsafe
@Unsafe  // Required annotation
void function criticalSection()
    unsafe  // Required block
        // Unsafe operations allowed here
        
// Rest of project: strict mode
```

**Result**: Maximum safety with controlled unsafe regions

---

### Unsafe + @ThreadSafe

```fusion
// Unsafe mode with thread safety documentation
@ThreadSafe
@Unsafe
void function lockFreeOperation()
    unsafe
        // Lock-free algorithm with manual memory
```

**Result**: Performance with documented thread safety

---

## IDE Integration

Description: How annotations appear in development environment.

**Visual Indicators**:
* @Performance - Lightning bolt icon
* @Deprecated - Strike-through text
* @Unsafe - Warning triangle
* @ThreadSafe - Lock icon
* @Test - Test tube icon

**Hover Information**:
* Shows annotation details
* Parameter values
* Deprecation messages
* Related documentation

**Code Completion**:
* Suggests available annotations
* Shows parameter options
* Template insertion

---

## Compiler Behavior

Description: How compiler processes modes and annotations.

---

### Compilation Phases

**Phase 1: Mode Detection**
* Check fusion.project.json
* Check file-level overrides
* Apply command-line flags

**Phase 2: Annotation Processing**
* Parse all annotations
* Validate parameters
* Check conflicts

**Phase 3: Code Analysis**
* Apply mode rules
* Process annotations
* Generate warnings/errors

**Phase 4: Optimization**
* Apply @Performance hints
* Respect @NoOptimize
* Inline @Inline functions

**Phase 5: Code Generation**
* Insert safety checks
* Generate documentation metadata
* Create debug symbols

---

## Best Practices

Description: Recommended usage patterns.

**General**:
* Start with standard mode
* Use strict mode for production
* Limit unsafe mode to specific files
* Document all unsafe code
* Review @Unsafe code thoroughly

**Annotations**:
* Don't over-annotate
* Use built-in annotations first
* Document custom annotations
* Keep annotation definitions in config
* Review @Performance impact

**Safety**:
* Prefer strict mode for new projects
* Use unsafe blocks minimally
* Always review unsafe code
* Test with different modes
* Profile performance impact

---

## Command Line Usage

**Compilation Commands**:
```bash
# Standard mode (default)
fusion build

# Strict mode
fusion build --strict

# Unsafe mode
fusion build --unsafe

# Override config
fusion build --mode=strict

# Check annotations
fusion analyze --annotations

# List all annotations in project
fusion annotations list
```

---

## Migration Guide

Description: Moving between modes.

---

### Standard to Strict

**Steps**:
1. Enable strict mode in config
2. Fix all warnings
3. Replace `var` with explicit types
4. Add missing null checks
5. Remove weak pointers
6. Test thoroughly

**Common Issues**:
* Weak pointers → Use Shared<T>
* Missing null checks → Add checks
* Type inference → Add explicit types

---

### Strict to Unsafe (Specific Files)

**Steps**:
1. Identify performance bottlenecks
2. Create file-level override
3. Add @Unsafe annotation
4. Wrap unsafe code in blocks
5. Extensive testing
6. Document decisions

---

## Summary

**Mode Comparison**:

Feature | Standard | Strict | Unsafe
---|---|---|---
Null checks | Warning | Required | Optional
Weak pointers | Warning | Error | Allowed
Type inference | Allowed | Limited | Allowed
Raw pointers | No | No | Yes
goto | No | No | Yes
Auto protection | Yes | Yes | Optional
Implicit casts | Yes | No | Yes

**Annotation Categories**:
* Safety: @Unsafe, @ThreadSafe
* Performance: @Performance, @Inline, @NoOptimize
* Documentation: @Deprecated, @RequiresReview
* Testing: @Test
* Organization: @Region

**Key Principles**:
* Safety by default
* Opt-in to unsafe
* Annotate intentions
* Document exceptions
* Test thoroughly

