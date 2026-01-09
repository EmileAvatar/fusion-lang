# Fusion Memory, Layout, and Data Policy — Summary

This document summarizes how **Fusion handles memory layout, structs, classes, strings, large objects, and compiler-driven layout optimizations**, with performance, predictability, and explicit control as core goals.

---

## 1. Core Principle

> **Performance comes from data layout, not syntax.**

Fusion prioritizes:

* Contiguous hot data
* Minimal pointer indirection
* Explicit ownership and references
* Compiler optimizations that do not change observable behavior

---

## 2. Structs and Classes (Fundamental Model)

### Conceptual Model

* A **struct or class** is primarily **data**
* **Methods are shared functions**, not stored in objects
* A hidden `this` pointer is passed to methods

### Lowered Reality

```
Class → contiguous memory for fields
Method → function(this, args...)
```

### Default Rules

* Fields stored contiguously
* Field order may be optimized unless explicitly fixed
* No hidden heap allocation
* No implicit boxing

---

## 3. Pointer Indirection (Performance Cost)

### Definition

Pointer indirection = accessing data via one or more pointer hops.

### Cost Characteristics

* Each pointer hop risks cache misses
* Cache misses dominate runtime cost
* Predictable access > abstract access

### Fusion Policy

* Inline values by default
* References must be **explicit** (`&Type`)
* Indirection is opt-in, not hidden

---

## 4. Small vs Large Objects

### Size Categories (Guideline)

```
≤ 64 bytes   → small (ideal inline)
≤ 128 bytes  → acceptable inline
> 256 bytes  → large (problematic inline)
> 1 KB       → must not be inline
```

### Problems with Large Inline Objects

* Expensive copies (`memcpy`)
* Cache pollution
* Stack overflow risk
* Poor locality when partially accessed

---

## 5. Large Object Policy (Enforced)

### Rules

* Types exceeding INLINE_SIZE_LIMIT **cannot be stored inline**
* Large types must be:

  * referenced (`&Type`)
  * boxed (`box class`)
* Large value copies are disallowed unless explicitly enabled

### Example

```fusion
class Player {
    stats: Stats          // inline (small)
    inventory: &Inventory // reference (large)
}
```

---

## 6. Strings (Explicit Storage Policies)

Fusion supports **multiple string types**, each with a defined storage model.

### String Types

| Type      | Purpose               | Storage    |
| --------- | --------------------- | ---------- |
| `fstr[N]` | Small fixed strings   | Inline     |
| `string`  | Owning dynamic string | Heap + SSO |
| `strview` | Non-owning slice      | ptr + len  |
| `istr`    | Interned identifier   | Shared     |

### Large String Rule

* Large strings must **never be inline**
* `string` uses **Small String Optimization (SSO)**
* Compiler enforces max inline limits for `fstr[N]`

---

## 7. Copying and Passing Rules

### Automatic Behavior

* Small types → passed by value
* Large types → passed by reference
* Compiler may auto-lower parameters

### Goal

Avoid accidental large copies while keeping small data fast.

---

## 8. Compiler Layout Optimization (Opt-In)

Fusion allows **layout optimization** only when explicitly enabled.

### Supported Optimizations

* Field reordering
* Hot / cold splitting
* Cold data outlining
* Profile-guided layout (PGO)
* Cache-friendly grouping

### Example

```fusion
@optimize(layout)
class Player {
    @hot {
        hp: int
        mana: int
        stamina: int
    }

    @cold {
        inventory: Inventory
        questLog: QuestLog
        biography: string
    }
}
```

### Result

```
Hot data → contiguous, cache-friendly
Cold data → outlined, pointer-accessed
```

---

## 9. Compiler Safety Boundaries

The compiler **must NOT**:

* Change observable memory layout without permission
* Break pointer identity or address stability
* Optimize across FFI boundaries
* Reorder `@packed` or layout-fixed types
* Apply layout changes in debug builds by default

---

## 10. Debugging and Tooling Guarantees

Fusion guarantees:

* Logical view remains unchanged
* Physical layout may differ internally
* Debug builds preserve simple layouts
* Tools can visualize optimized layouts

---

## 11. Design Philosophy (Final)

> **Inline data is for small, hot, frequently-used fields.**
> **Heap allocation is for large, cold, infrequently-used data.**
> **Indirection is paid for only when explicitly requested.**
> **The compiler optimizes layout only when allowed.**

This model combines:

* C/C++ performance
* Modern compiler intelligence
* Data-oriented design principles
* Explicit, predictable behavior

---

If you want, next we can:

* Convert this into a `MemoryModel.md`
* Map this directly to Fusion IR structures
* Define compiler passes for layout optimization
* Add ECS-specific rules as a separate section

Just tell me where you want it placed in the Fusion project.
