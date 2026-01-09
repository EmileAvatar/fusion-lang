# Fusion Strict Mode Specification

Description: Complete reference for Fusion's strict mode - maximum safety and security enforcement for production and enterprise applications.

Last Updated: November 2, 2025

---

## Overview

Strict mode is Fusion's highest safety enforcement level, designed for production code, enterprise applications, and security-critical systems where **performance and security are the main priorities**.

**Philosophy**: Prevent bugs at compile-time rather than runtime. Strict mode enforces best practices and eliminates entire classes of errors before code ever executes.

---

## When to Use Strict Mode

**Recommended For**:
* Production applications
* Enterprise software
* Security-critical systems
* Financial applications
* Healthcare systems
* Infrastructure code
* Public APIs
* Team projects with code reviews

**Not Recommended For**:
* Prototyping and rapid development
* Educational/learning projects
* Performance benchmarking (use unsafe mode)
* Embedded systems (use unsafe mode)

---

## Enabling Strict Mode

### Project-Wide Configuration

**In fusion.project.json**:
```json
{
  "compiler": {
    "strictMode": true,
    "warningsAsErrors": true,
    "maxWarnings": 0
  },
  "language": {
    "allowWeakPointers": false,
    "requireExplicitTypes": true,
    "enforceNullChecks": true,
    "allowGoto": false,
    "allowImplicitCasts": false
  }
}
```

### File-Level Override

**In fusion.file.json**:
```json
{
  "file": {
    "path": "./src/CriticalModule.fusion"
  },
  "overrides": {
    "compiler": {
      "strictMode": true,
      "warningsAsErrors": true
    }
  }
}
```

### Command-Line

```bash
# Build with strict mode
fusion build --strict

# Build with strict and warnings as errors
fusion build --strict --warnings-as-errors

# Run with strict mode
fusion run --strict MyApp.fusion
```

### Environment Variable

```bash
# Force strict mode globally
export FUSION_STRICT_MODE=true
```

---

## Strict Mode Features

### 1. Compiler Enforcement

**strictMode: true**
* Maximum safety checks enabled
* Aggressive static analysis
* No unsafe operations allowed
* All potential bugs caught at compile-time

**warningsAsErrors: true**
* All warnings become compilation errors
* Cannot build with any warnings
* Enforces clean code
* No warning suppression allowed

**maxWarnings: 0**
* Zero-tolerance policy
* Must fix all issues before compilation
* Prevents warning accumulation

---

### 2. Type System Restrictions

#### No Type Inference (requireExplicitTypes: true)

**Standard Mode**:
```fusion
var count = 10              // OK: type inferred
var name = "Spaceship"      // OK: type inferred
var items = [1, 2, 3]       // OK: type inferred
```

**Strict Mode**:
```fusion
// var count = 10           // ERROR: Must specify type
int count = 10              // OK: Explicit type
string name = "Spaceship"   // OK: Explicit type
int[] items = [1, 2, 3]     // OK: Explicit type
```

**Rationale**: Explicit types improve code clarity, prevent inference errors, and make code self-documenting.

---

#### No Implicit Casts (allowImplicitCasts: false)

**Standard Mode**:
```fusion
int x = 10
long y = x              // OK: Implicit widening cast
float f = 3.14
int i = f               // WARNING: Implicit narrowing (loses precision)
```

**Strict Mode**:
```fusion
int x = 10
// long y = x           // ERROR: Must use explicit cast
long y = cast<long>(x)  // OK: Explicit cast

float f = 3.14
// int i = f            // ERROR: Must use explicit cast
int i = cast<int>(f)    // OK: Explicit cast (programmer aware of precision loss)
```

**Rationale**: Explicit casts make data loss visible and intentional.

---

#### Required Null Checks (enforceNullChecks: true)

**Standard Mode**:
```fusion
void function processShip(Spaceship ship)
    ship.start()        // WARNING: ship might be null
```

**Strict Mode**:
```fusion
void function processShip(Spaceship ship)
    // ship.start()     // ERROR: Must check for null first

    // Option 1: Manual null check
    if ship is null
        return
    ship.start()

    // Option 2: Early return with error
    if ship?.null
        throw Error("Ship cannot be null")
    ship.start()

    // Option 3: Safe navigation
    ship?.start()
```

**Rationale**: Eliminates null reference exceptions entirely.

---

### 3. Memory Management Restrictions

#### No Weak Pointers (allowWeakPointers: false)

**Standard Mode**:
```fusion
class Parent
    Shared<Child> child

class Child
    Weak<Parent> parent  // WARNING: Weak pointers discouraged
```

**Strict Mode**:
```fusion
class Parent
    Shared<Child> child

class Child
    // Weak<Parent> parent  // ERROR: Weak pointers not allowed in strict mode
```

**Alternative Solutions**:
```fusion
// Solution 1: Redesign to avoid circular reference
class Parent
    Shared<Child> child

class Child
    // No parent reference - use events or callbacks instead

// Solution 2: Use ID-based reference
class Parent
    int id
    Shared<Child> child

class Child
    int parentId  // Reference by ID instead of pointer
```

**Rationale**: Weak pointers add complexity and potential bugs. Better code design eliminates the need for them.

---

#### No Raw Pointers (enableRawPointers: false)

**Strict Mode**:
```fusion
// Spaceship* rawPtr = ...  // ERROR: Raw pointers not allowed

// Must use:
Unique<Spaceship> ship = Unique.create<Spaceship>("Enterprise", 100.0)
// or
Shared<Spaceship> ship = Shared.create<Spaceship>("Enterprise", 100.0)
// or automatic GC
Spaceship ship = Spaceship("Enterprise", 100.0)
```

**Rationale**: Raw pointers enable memory leaks, dangling pointers, and undefined behavior. Smart pointers or GC required.

---

### 4. Control Flow Restrictions

#### No goto Statements (allowGoto: false)

**Strict Mode**:
```fusion
// goto label        // ERROR: goto not allowed in strict mode
```

**Alternative**:
```fusion
// Use structured control flow
while condition
    if shouldExit
        break
    end loop
end loop
```

**Rationale**: goto creates spaghetti code and makes reasoning about program flow difficult.

---

### 5. Safety Feature Requirements

#### Mandatory Loop Protection

**Strict Mode**:
```fusion
// Loop protection ALWAYS enabled (cannot disable)
for i in 1...10000000
    process(i)
end loop

// @NoLoopProtection    // ERROR: Cannot disable loop protection in strict mode
```

**Configuration**:
```json
{
  "loop": {
    "autoProtection": true,              // Cannot be false
    "defaultMaxIterations": 1000000,     // Required
    "enableThreadInterrupts": true,      // Cannot be false
    "enableResourceMonitoring": true     // Cannot be false
  }
}
```

**Rationale**: Prevents infinite loops and system hangs in production.

---

#### Mandatory Race Detection

**Strict Mode**:
```json
{
  "threading": {
    "enableRaceDetection": true,       // Cannot be false
    "enableDeadlockDetection": true,   // Cannot be false
    "enableAutoLocking": true          // Cannot be false
  }
}
```

**Rationale**: Eliminates race conditions and deadlocks in concurrent code.

---

### 6. Performance & Security Restrictions

#### No Callbacks When Performance is Priority (allowCallbacks: false)

**Strict Mode**:
```fusion
// type Callback = void function(int)  // ERROR: Callbacks not allowed in strict mode

// Alternative: Use direct function calls or async/await
async void function processAsync(int data)
    int result = await heavyOperation(data)
    handleResult(result)
```

**Rationale**: Callbacks introduce overhead and unpredictability. Direct calls or async/await provide better performance and security.

---

### 7. Code Quality Requirements

#### Mandatory Coding Standards (enforceCodingStandards: true)

**Strict Mode Enforces**:
* CamelCase for classes: `class SpaceShip`
* camelCase for variables: `int shipCount`
* UPPER_SNAKE_CASE for constants: `const MAX_SPEED`
* Maximum function length (default: 500 lines)
* Maximum class complexity (default: 100)
* Required documentation comments for public APIs

**Example**:
```fusion
// class spaceship        // ERROR: Must be CamelCase
class Spaceship          // OK

// int ShipCount = 0      // ERROR: Must be camelCase
int shipCount = 0        // OK

// const max_speed = 100  // ERROR: Must be UPPER_SNAKE_CASE
const MAX_SPEED = 100    // OK
```

---

#### Maximum Complexity Limits

**Configuration**:
```json
{
  "language": {
    "maxFunctionLength": 500,        // Lines per function
    "maxClassComplexity": 100,       // Cyclomatic complexity
    "maxFileSize": 5000              // Lines per file
  }
}
```

**Rationale**: Enforces maintainable code size and complexity.

---

### 8. Module System Restrictions

#### No Circular Dependencies (allowCircularDependencies: false)

**Strict Mode**:
```fusion
// Module A imports Module B
// Module B imports Module A
// ERROR: Circular dependency detected
```

**Rationale**: Circular dependencies create fragile, hard-to-maintain code.

---

### 9. Error Handling Requirements

#### Mandatory Error Handling

**Standard Mode**:
```fusion
Spaceship ship = loadShip("ship.dat")  // WARNING: Unchecked error
```

**Strict Mode**:
```fusion
// Spaceship ship = loadShip("ship.dat")  // ERROR: Must handle error

// Must use:
Spaceship ship, Error err = loadShip("ship.dat")
if err
    print("Error: {err.message}")
    return
```

**Rationale**: Forces explicit error handling, preventing silent failures.

---

## Complete Strict Mode Configuration

### Full fusion.project.json for Strict Mode

```json
{
  "project": {
    "name": "ProductionApp",
    "version": "1.0.0",
    "description": "Production-ready application",
    "projectType": "application"
  },

  "compiler": {
    "strictMode": true,
    "unsafeMode": false,
    "warningsAsErrors": true,
    "maxWarnings": 0,
    "optimizationLevel": 2,
    "parallelCompilation": true
  },

  "language": {
    "allowWeakPointers": false,
    "allowGoto": false,
    "enforceNullChecks": true,
    "requireExplicitTypes": true,
    "allowImplicitCasts": false,
    "maxFunctionLength": 500,
    "maxClassComplexity": 100,
    "enforceCodingStandards": true,
    "allowCallbacks": false
  },

  "loop": {
    "autoProtection": true,
    "defaultMaxIterations": 1000000,
    "enableThreadInterrupts": true,
    "enableResourceMonitoring": true,
    "adaptToSystemResources": true
  },

  "memory": {
    "defaultMode": "gc",
    "enableSmartPointers": true,
    "enableRawPointers": false,
    "gcMaxHeapSize": "512MB"
  },

  "threading": {
    "enableChannels": true,
    "enableSharedMemory": true,
    "enableAutoLocking": true,
    "maxThreads": 8,
    "enableRaceDetection": true,
    "enableDeadlockDetection": true
  },

  "modules": {
    "allowCircularDependencies": false,
    "enableModuleCaching": true
  },

  "testing": {
    "enableUnitTests": true,
    "coverageThreshold": 90,
    "parallelTests": true
  },

  "annotations": {
    "customAnnotations": {
      "@Unsafe": {
        "enabled": false
      }
    }
  }
}
```

---

## Strict Mode vs Other Modes

### Feature Comparison Table

Feature | Standard Mode | Strict Mode | Unsafe Mode
---|---|---|---
Type Inference | ✓ Allowed | ✗ Not Allowed | ✓ Allowed
Implicit Casts | ✓ Warnings | ✗ Errors | ✓ Allowed
Null Checks | ⚠ Warnings | ✓ Required | ✗ Optional
Weak Pointers | ⚠ Warnings | ✗ Errors | ✓ Allowed
Raw Pointers | ✗ Not Allowed | ✗ Not Allowed | ✓ Allowed
goto Statements | ✗ Not Allowed | ✗ Not Allowed | ✓ Allowed
Callbacks | ✓ Allowed | ✗ Not Allowed (perf) | ✓ Allowed
Loop Protection | ✓ Automatic | ✓ Mandatory | ✗ Optional
Warnings as Errors | ✗ Optional | ✓ Required | ✗ Not Required
Race Detection | ✓ Enabled | ✓ Mandatory | ✗ Optional
Circular Dependencies | ⚠ Warnings | ✗ Errors | ⚠ Warnings
Coding Standards | ⚠ Warnings | ✓ Enforced | ✗ Optional

---

## Migration to Strict Mode

### Step-by-Step Migration

**Step 1: Enable Strict Mode Gradually**
```bash
# Check what would break
fusion build --strict --dry-run

# Fix issues file by file
fusion build --strict --file src/Module1.fusion
```

**Step 2: Common Fixes Needed**

**Fix 1: Add Explicit Types**
```fusion
// Before
var count = 10

// After
int count = 10
```

**Fix 2: Add Null Checks**
```fusion
// Before
void function process(Ship ship)
    ship.start()

// After
void function process(Ship ship)
    if ship is null
        throw Error("Ship cannot be null")
    ship.start()
```

**Fix 3: Replace Weak Pointers**
```fusion
// Before
Weak<Parent> parent

// After
int parentId  // Use ID instead
```

**Fix 4: Explicit Casts**
```fusion
// Before
long y = x

// After
long y = cast<long>(x)
```

---

## Best Practices in Strict Mode

### 1. Design for Safety First
* Prefer value types over references
* Use Option/Result types instead of null
* Design APIs that can't be misused
* Make invalid states unrepresentable

### 2. Use Smart Pointers Over GC
* Unique<T> for single ownership
* Shared<T> for shared ownership
* Avoid Weak<T> entirely (not allowed)

### 3. Explicit Over Implicit
* Explicit types > type inference
* Explicit casts > implicit casts
* Explicit error handling > exceptions
* Explicit null checks > assumptions

### 4. Leverage Compiler Checks
* Let compiler catch bugs
* Treat warnings as bugs
* Fix issues immediately
* Don't suppress warnings

### 5. Document Everything
* Public APIs must have doc comments
* Complex logic needs explanation
* Assumptions must be stated
* Invariants must be documented

---

## Performance Considerations

### Strict Mode Impact on Performance

**Compile-Time**:
* ✗ Slower compilation (more checks)
* ✓ But catches bugs early
* ✓ Parallel compilation helps

**Runtime**:
* ✓ Same or better performance
* ✓ Better optimization opportunities
* ✓ No runtime type checks needed
* ✓ Compiler has more information

**Trade-off**: Slower builds, faster and safer execution.

---

## Security Benefits

### Attack Surface Reduction

**Eliminated Attack Vectors**:
* ✓ Null pointer dereferences
* ✓ Buffer overflows (no raw pointers)
* ✓ Use-after-free (no manual memory)
* ✓ Race conditions (mandatory detection)
* ✓ Type confusion (explicit types)
* ✓ Integer overflow (checked math)

**Strict Mode = Secure by Default**

---

## CLI Commands

```bash
# Build with strict mode
fusion build --strict

# Build with strict + warnings as errors
fusion build --strict --warnings-as-errors

# Run with strict mode
fusion run --strict main.fusion

# Check strict mode compliance
fusion check --strict

# Convert project to strict mode
fusion convert --to-strict

# Show strict mode violations
fusion lint --strict

# Test with strict mode
fusion test --strict
```

---

## Configuration Priority

**Highest to Lowest Priority**:
1. Command-line flags (`--strict`)
2. Environment variables (`FUSION_STRICT_MODE`)
3. File-level config (`fusion.file.json`)
4. Project config (`fusion.project.json`)
5. User config (`fusion.user.json`)
6. System defaults

**Example**:
```bash
# Project has strictMode: false
# But command-line overrides it
fusion build --strict  # Strict mode enabled
```

---

## Troubleshooting

### Common Errors in Strict Mode

**Error: "Type inference not allowed in strict mode"**
```fusion
// Fix: Add explicit type
int count = 10
```

**Error: "Implicit cast not allowed"**
```fusion
// Fix: Add explicit cast
long y = cast<long>(x)
```

**Error: "Null check required before use"**
```fusion
// Fix: Add null check
if ship is null
    return
ship.start()
```

**Error: "Weak pointer not allowed in strict mode"**
```fusion
// Fix: Redesign to avoid weak pointer
int parentId  // Use ID instead
```

---

## Summary

**Strict Mode Purpose**: Maximum safety and security for production code.

**Key Principles**:
* Explicit over implicit
* Compile-time checks over runtime
* Safety over convenience
* Quality over speed of development

**When to Use**: Production, enterprise, security-critical applications where **performance and security are the main priorities**.

**Result**: More upfront work, but dramatically fewer bugs, better performance, and higher security in production.

---

## See Also

* [fusion-language-spec.md](fusion-language-spec.md) - Complete language specification
* [fusion_specs.md](fusion_specs.md) - All configuration options
* [json/fusion.project.json](json/fusion.project.json) - Example project configuration
* [fusion-threading-concurrency.md](fusion-threading-concurrency.md) - Threading safety details

---

**Fusion Strict Mode: Safe, Secure, and Fast.**
