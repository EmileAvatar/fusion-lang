[< 081 Autoboxing](081-Autoboxing.md) | [Index](index.md) | [100 Concurrency >](100-Concurrency.md) <!-- nav -->

# 090 Memory

**Contents**

- [Ownership explained - start here](#ownership-explained---start-here)
- [Memory Management](#memory-management)
- [Tier 1: Automatic Garbage Collection (optional - never the default: OWNERSHIP first, Decisions.md D.027)](#tier-1-automatic-garbage-collection-optional---never-the-default-ownership-first-decisionsmd-d027)
- [Tier 2: Smart Pointers (Performance Mode)](#tier-2-smart-pointers-performance-mode)
- [Tier 3: Raw Pointers (Unsafe Mode)](#tier-3-raw-pointers-unsafe-mode)
- [Memory Strategy Summary](#memory-strategy-summary)
- [Ownership: move, borrow, share](#ownership-move-borrow-share)
- [The ownership setting: strict or relaxed (user, 2026-11-14 - D.124)](#the-ownership-setting-strict-or-relaxed-user-2026-11-14---d124)

## Ownership explained - start here

For anyone new to ownership (no Rust needed). Fusion keeps memory safe without a garbage
collector: every object has **one owner**, and it is freed when that owner goes out of scope. The
object itself never moves in memory - only its address is handed over. The full rules and truth
tables: [files/Ownership.md](../Ownership.md); the setting: [below](#the-ownership-setting-strict-or-relaxed-user-2026-11-14---d124).

#### Where things live

```text
 STACK (each function's own variables - fast, freed automatically on return)
 +------------------------------+
 | main()                       |
 |   int count = 3      [ 3 ]   |  numbers, bools, chars, plain structs: the value itself
 |   Car a        [0x7F20] -----+--+   objects, Lists, Maps: only an address (8 bytes)
 +------------------------------+  |
                                   v
 HEAP (made with Car(...), lives until freed)
 +-----------------------------------+
 | 0x7F20: Car { name: "Mini" }      |  the object itself - it never moves
 +-----------------------------------+
```

- **Stack**: a function's variables; small values live there whole, and they are gone when the
  function returns
- **Heap**: objects, Lists and Maps; a variable on the stack holds only their address
- **Registers**: the CPU holds values there for a moment while working on them - they play no
  part in ownership

#### A move: the address changes hands, the object stays

```text
Car a = Car("Mini")          Car b = a                     end of main()

 a [0x7F20]--+                a [ gone ] (compile error      b goes out of scope
             v                           if used)            -> the Car at 0x7F20 is freed
        +----------+          b [0x7F20]--+                  +----------+
        | Car Mini |                      v                  |  freed   |
        +----------+                +----------+             +----------+
                                    | Car Mini |  same place
                                    +----------+
```

- The compiler makes `a` unusable after `Car b = a` - only one name ever holds the address
- So the object can be freed exactly once, when its owner's block ends

#### A borrow: a temporary second address, with a promise

```text
show(b)                      // passing borrows
  b [0x7F20]--+
              v
         +----------+
         | Car Mini |
         +----------+
              ^
  c [0x7F20]--+   show's parameter: may use it, may not keep it - gone when show returns
```

- The compiler checks a borrow never outlives its owner: it is never stored or returned
- So when `b` frees the car, nothing else still points at it

#### Copies

```text
Car c = byVal b      ->  a second Car on the heap (0x8A40), with its own owner c
Car d = byRef b      ->  a borrow, like show(b)
int x = y            ->  the number itself is copied on the stack - nothing to own
```

#### The rule of thumb

1. **Every heap object has exactly one owner** - the variable holding its address
2. **`=` hands the address over** (a move) - the old name is dead until it gets a new value
3. **Passing to a function lends it** - you get it back after the call; if the function keeps
   it, it is moved
4. **A borrow is temporary** - never stored, never returned, never longer than its owner
5. **One writer** - while a borrow changes something, nothing else changes it (reading is fine)
6. **Out of scope = freed** - the owner's block ends, the object is freed once, at a known point
7. **A second one? `byVal`** makes a copy; **sharing for a moment? `byRef`** borrows

What this rules out - checked by the compiler before the program runs:

| Bug | Why it can't happen |
|---|---|
| Use after free | nobody holds an address to freed memory - borrows end before their owner |
| Double free | only the one owner frees |
| Leak | every object has an owner whose scope ends |
| Two writers at once | one writer at a time - and only one owner to hand to another thread (services, Task 42) |

#### Today and later

- **Today** each object also carries a small counter - a safety net: a move still counts, and
  "freed" means the count reached 0
- **Later** (Task 38.5) the counter is dropped where a move proves one owner - freeing becomes one
  direct free
- **`[memory] ownership = "relaxed"`**: the counter is the real rule - two names may hold the same
  address, and the object is freed when the last one lets go (as Java, C# and Python do) - for code
  using a library without the ownership model, a GC alongside it, or manual memory

---

## Memory Management

**Status:** [PARTLY] ownership is built - one owner, moves, borrows, `[memory] ownership` (Task 48, explained above); strings, bytes, lists, maps and structs are freed automatically with a leak check (18.3, 18.5); `Shared` / `Weak` and GC as a project option [PLANNED 38] - `Unique` was dropped (D.080). The tiers below are the earlier design (2026-09)

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
* Freed at the end of its scope (user, 2026-11-11; D.134): memory allocated here and never freed is freed
  by the compiler where its block ends - some protection even for manual memory

```
unsafe
    Spaceship* rawPtr = allocate<Spaceship>(1)
    rawPtr.initialize("Manual", 200.0)
    // ... use pointer
    deallocate(rawPtr)                 // forgotten: the compiler frees it at the block's end
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

**Status:** [DONE 48] designed 2026-10-31 (user), built 2026-11 - explained at the top of this page. The rules and truth tables:
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
* Setting (built, 48.11): `[memory] ownership = "strict"` (default) | `"relaxed"` - it replaced `assignment`:

### The ownership setting: strict or relaxed (user, 2026-11-14 - D.124)

One setting covers every ownership rule. It replaces `[memory] assignment`, which covered only what
`=` does (Task 48.11):

```toml
# before (until 48.11) - one rule only
[memory]
assignment = "move"      # or "share"

# after - every ownership rule at once
[memory]
ownership = "strict"     # default - the safest | "relaxed"
```

| What it decides | `assignment = "move"` (before) | `assignment = "share"` (before) | `ownership = "strict"` (default) | `ownership = "relaxed"` |
|---|---|---|---|---|
| `Car b = a` | moves | shares | moves | shares |
| `f(a)`, f only reads it | borrows | borrows | borrows | borrows |
| `f(a)`, f keeps it | moves | shares | moves | shares |
| One writer: change `fleet` while `first` borrows from it | error | error | **error** | allowed |
| A borrow stored or returned | error | error | **error** | allowed - the object is counted |
| `byVal` / `byRef` | copy / borrow | copy / borrow | copy / borrow | copy / borrow |
| Memory freed by | counting | counting | ownership (counting until 48.6 - Task 38) | counting, or a GC / manual memory alongside it |
| Meant for | - | - | every Fusion project | code using a library with no ownership model (a GC created alongside it), or manual memory management |

- **strict** (the default, the safest): today's `"move"` with every rule on - no surprise changes
  through a second name, no leaks from objects holding each other, one owner (safe to hand to another
  thread - the base of services, Task 42)
- **relaxed**: today's `"share"` with the rules loosened - for code using a library that does not use
  the ownership model (a GC created alongside it), or manual memory management
- `byVal` / `byRef` choose a copy or a borrow in both
- With no `byVal` / `byRef`: assigning moves (strict) or shares (relaxed); passing to a function
  borrows in both, unless the function keeps the value - then it moves (strict) or shares (relaxed)
- An old `assignment = "move"` is read as `ownership = "strict"`, `"share"` as `"relaxed"`, with a
  warning that the name changed

The example behind the table:

```fusion
void function show(Car c)              // only reads c
    print(c.name)

void function keep(Car c, List<Car> garage)
    garage.add(c)                      // keeps c

void function main()
    List<Car> garage = List<Car>()
    List<Car> fleet = [Car("Mini"), Car("Golf")]
    Car a = Car("Mini")
    Car b = a                // strict: moves (a gone) - relaxed: shares
    show(b)                  // both: borrows for the call
    keep(b, garage)          // strict: moves b into the garage - relaxed: shared
    print(b.name)            // strict: compile error, b was moved - relaxed: "Mini"
    Car first = fleet[0]     // first borrows from fleet
    first.name = "Cooper"    // fine in both - one writer
    print(fleet.len())       // fine in both - reading the owner (D.123)
    fleet.removeAt(0)        // strict: compile error, fleet frozen while first is used - relaxed: fine
    print(first.name)
```

Full design and truth tables: [files/Ownership.md](../Ownership.md).

[< 081 Autoboxing](081-Autoboxing.md) | [Index](index.md) | [100 Concurrency >](100-Concurrency.md) <!-- nav -->
