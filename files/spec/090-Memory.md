[< 081 Autoboxing](081-Autoboxing.md) | [Index](index.md) <!-- nav -->

# 090 Memory

Contents: [Tier 1: Automatic Garbage Collection (optional - never the default: OWNERSHIP first, Decisions.md D.027)](#tier-1-automatic-garbage-collection-optional---never-the-default-ownership-first-decisionsmd-d027) | [Tier 2: Smart Pointers (Performance Mode)](#tier-2-smart-pointers-performance-mode) | [Tier 3: Raw Pointers (Unsafe Mode)](#tier-3-raw-pointers-unsafe-mode) | [Memory Strategy Summary](#memory-strategy-summary) | [Ownership: move, borrow, share](#ownership-move-borrow-share)

## Memory Management

**Status:** [PARTLY] strings, bytes, lists, maps and structs holding them are values, copied deeply and freed automatically (18.3, 18.5) with a leak check; Unique / Shared / Weak and GC are decided (12.7) and [PLANNED 38]

Description: Three-tier memory management strategy for different use cases.

**Design status (Task 12.7, decided 2026-09-13):**
- The `Unique<T>` / `Shared<T>` / `Weak<T>` semantics below are the authoritative, decided design - this
  section is the memory-model ADR that Task 12.7 exists to produce
- **Not yet implemented in the compiler**: `Unique`, `Shared` and `Weak` are reserved keywords only
  (tokenized, nothing else) - no parser, semantic-analysis or codegen support yet
- Building that is separate future work, unblocked by this decision but not scoped or scheduled here
  (see files/taskSummary2.md Task 30, which depends on this section's Weak / nullability decisions)

---

### Tier 1: Automatic Garbage Collection (optional - never the default: OWNERSHIP first, Decisions.md D.027)

Description: Automatic memory management for most use cases.

* No manual memory management needed
* Like Java, Python, C#
* Suitable for 95% of applications
* Simplest for developers

```
// Automatic cleanup
Spaceship ship = Spaceship("Enterprise", 100.0)
// Automatically garbage collected when no longer referenced
```

---

### Tier 2: Smart Pointers (Performance Mode)

Description: Explicit lifetime control without garbage collection pauses.

* **Unique Pointer**: Single ownership
     * Only one owner at a time
     * Automatically deleted when owner goes out of scope
     * Cannot be copied, only moved
     * **Moving is automatic (decided 2026-10-31, Decisions.md D.080 - replaces the written
       `.move()` of 2026-09-13):** under OWNERSHIP every object has one owner, and
       assigning it moves it (`Car b = a`); `byVal` copies, `byRef` borrows. So no
       `Unique<T>` wrapper is needed - single ownership is what every object already has
       (files/Ownership.md)
     * **Use-after-move is a compile-time error where provable, a runtime crash with a
       clear message otherwise** - structurally the same hybrid analysis already decided
       for Task 30's nullable arrays (definite/maybe/unknown state tracked through
       straight-line code), so moved-from tracking and null-flow tracking should share one
       analysis pass when both are eventually implemented, not two parallel ones.
     * Zero overhead
     * Use for: temporary objects, factory returns, single-owner scenarios

```
// Creating unique pointer
Unique<Spaceship> ship = Unique.create<Spaceship>("Enterprise", 100.0)

// Use like normal object
ship.start()
ship.move(direction, speed)

// Transfer ownership (move) - by assigning (D.080)
Spaceship newOwner = ship               // moved: using ship again is a compile error
Spaceship copy = byVal newOwner         // a copy - both usable

// Automatic cleanup when newOwner goes out of scope
```

* **Shared Pointer**: Reference counting
     * Multiple owners allowed
     * Keeps count of references
     * Deleted when count reaches zero
     * Can be copied
     * **Refcounting is always atomic (decided 2026-09-13):** increment/decrement of the
       reference count is thread-safe unconditionally, regardless of any project-level
       threading configuration (see Task 12.12). Chosen over a configurable
       atomic-vs-non-atomic mode to keep one correct behavior rather than two runtime
       code paths to implement, test, and document - the small overhead of an atomic op
       even in single-threaded code was judged worth that simplicity.
     * **Cycles are not detected automatically (decided 2026-09-13):** there is no cycle
       detector or tracing collector. A cycle of `Shared<T>` references leaks memory -
       matches Swift ARC / Rust `Rc` / Objective-C ARC, not a garbage-collected language's
       behavior. `Weak<T>` (below) is the documented, required way to break a cycle; this
       is an accepted, permanent limitation of the design, not a gap awaiting a future fix.
     * Small overhead (reference count storage + atomic refcount ops)
     * Use for: shared resources (textures, sounds, configs)

```
// Creating shared pointer
Shared<Texture> texture = Shared.create<Texture>("ship.png")
print("Ref count: {texture.refCount()}")  // 1

// Make copies (reference count increases)
Shared<Texture> copy1 = texture  // Ref count: 2
Shared<Texture> copy2 = texture  // Ref count: 3

// All copies deleted when ref count reaches 0
```

* **Weak Pointer**: Non-owning reference
     * Doesn't increase reference count
     * **Upgrade is nullable, never a silent crash (decided 2026-09-13):** `.lock()`
       (shown below) always returns a `Shared<T>` that is `null` if the owner was
       already destroyed. The caller must null-check before use; there is no "just crash
       if the owner is gone" mode. Chosen for consistency with the same nullable-safe-
       navigation direction Task 30 defines for arrays, so Fusion has one null-handling
       story across features rather than a different rule per type. Once Task 30's
       `?.`/`?[` syntax exists, this should read as `child.parent.lock()?.doSomething()`
       instead of the explicit if/else shown below.
     * Breaks circular references
     * Use for: observer pattern, parent-child relationships
     * **WARNING**: Discouraged in most code
     * **STRICT MODE**: Causes compilation error
     * Only use when absolutely necessary to break circular references

```
// Breaking circular reference
class Parent
    Shared<Child> child

class Child
    Weak<Parent> parent  // Weak reference prevents memory leak

// Using weak pointer
Shared<Parent> parentRef = child.parent.lock()     // null when the parent is gone (no T? types - D.063)
if parentRef?.null
    print("Parent no longer exists")
else
    parentRef.doSomething()

// In strict mode, this would cause a compile error
// Prefer redesigning to avoid circular references
```

---

### Tier 3: Raw Pointers (Unsafe Mode)

Description: Manual memory management for embedded systems.

* Only for embedded systems or FFI (Foreign Function Interface)
* Requires `unsafe` blocks
* Manual allocation and deallocation
* Compiler warnings and restrictions

```
unsafe
    Spaceship* rawPtr = allocate<Spaceship>(1)
    rawPtr.initialize("Manual", 200.0)
    // ... use pointer
    deallocate(rawPtr)
```

---

### Memory Strategy Summary

Mode | Use Case | Complexity | Performance
---|---|---|---
Automatic GC | General applications | Low | Good
Smart Pointers | Performance-critical | Medium | Excellent
Raw Pointers | Embedded/FFI only | High | Maximum

**Decided (user, 2026-10-31 - Decisions.md D.027):** no GC by default - OWNERSHIP first (one owner, moves, borrows - Task 48). A GC exists only when made in code or when a project's `fusion.toml` chooses it

---

### Ownership: move, borrow, share

**Status:** [PLANNED 48] designed 2026-10-31 (user). The rules and truth tables:
`files/Ownership.md`; the decisions: `Notes/Ownership_Decisions_2026-10-31.md`.

* **Assigning moves:** `Car b = a` hands the object over - using `a` afterwards is a compile
  error until it gets a new value. Lists and Maps move too; strings and plain structs copy
* **`byVal` copies** (`clone()` for objects); **passing borrows** for the call; reading an
  element or field is a local borrow; a struct's collection only lends itself
* **At the call:** `show(readonly acc)` - the call must not change acc; `f(byRef x)`; `f(byVal x)`
* **The contract is the signature:** `readonly Account a` only reads; `Account a` may change
  it. Inside a project it is worked out from the body; a library counts by its signature
  only; a library not written in Fusion gets a warning when a borrowed value is passed
* **`shared Car c = a`:** counted, read only except to the holder that made it shared
* **`fixed(n)`** (Task 47.5, D.064): `fixed(10) string name`, `fixed(14) List<Person> people`,
  `fixed int numbers[10]` - only the size is limited (the values may change; `const`: nothing changes),
  lower fine, never higher; memory reserved once
* Setting:
  ```toml
  [memory]
  assignment = "move"            # "move" (default) | "share" - b = a: two names, one object
  ```

[< 081 Autoboxing](081-Autoboxing.md) | [Index](index.md) <!-- nav -->
