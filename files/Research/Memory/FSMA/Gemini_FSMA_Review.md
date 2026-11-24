# Fusion Structured Memory Architecture — Review & Engineering Spec

**Target Audience:** Fusion Compiler Team / Claude Code Implementation Agent  
**Context:** Fusion compiles to C (via GCC), defaults to **single-owner ownership** (Rust-like move/borrow semantics without a default GC), supports **opt-in Manual Allocation** and **opt-in GC**, and isolates cross-thread mutable state via the **`service` keyword** (`files/Service.md`).

---

## 1. Executive Summary

Fusion's **Structured Memory Architecture** partitions the traditional monolithic heap into typed, scoped, and named **Data Stacks** (region-based memory arenas). Because Fusion compiles to C and enforces single-owner semantics by default, this model eliminates the need for a global tracing garbage collector in standard programs while avoiding per-object `malloc`/`free` fragmentation and cache misses.

However, integrating Data Stacks with **Ownership**, **`service` concurrency**, and **opt-in GC/Manual modes** requires strict lifetime, locality, and reclamation rules so that C code generation remains deterministic, leak-free, and data-race-free.

---

## 2. Architectural Review & Identified Risks

### Issue 1: Cross-Stack References & Lifetime Escape (Dangling Pointers)
* **The Flaw:** In v2, an object living in a long-lived pool (`Data Stack<String: String Pool>` or a parent scope's `Data Stack<Single>`) could hold a pointer to an object allocated inside a short-lived `Data Stack<General>` or inner lexical scope. When the short-lived Data Stack resets, the surviving pointer becomes dangling.
* **Why it matters for Fusion:** Fusion guarantees memory safety by default via ownership (`files/Ownership.md`). In C codegen, a dangling pointer across regions causes undefined behavior.

### Issue 2: Internal Fragmentation ("Holes") in `Data Stack<Mixed>` & `<General>`
* **The Flaw:** In the v2 diagram, Column 2 (`Mixed`) shows dead/freed blocks (red) trapped beneath live blocks (green). A strict LIFO stack pointer cannot reclaim middle holes without moving live objects (which breaks raw C pointers) or waiting until the entire stack resets.
* **Why it matters for Fusion:** Long-running loops or services allocating variable-sized temporary objects in `<Mixed>` or `<General>` will steadily leak memory until scope exit.

### Issue 3: Overlap Between `<Single>`, `<Mixed>`, and `<General>`
* **The Flaw:** The semantic distinction between `<Mixed>` ("General purpose stack") and `<General>` ("mixed content that cannot fit into above stacks / short-lived objects") is ambiguous. The compiler's escape/allocation pass needs deterministic rules to route allocations to the right C runtime allocator.

### Issue 4: Thread-Safety & `service` Isolation (`Service.md` Alignment)
* **The Flaw:** `Service.md` establishes strict concurrency rules:
  * **Rule S1/S8:** A `service` is the single writer of its state; internal objects use plain (non-atomic) reference counts/pointers because no two threads ever touch them concurrently.
  * **Rule H1/H8:** `hotpath service` forbids all heap allocation during its run loop (only the set-up block may allocate).
  * **Rule S6:** Data sent into a `service` request is either *borrowed* for the request duration, *moved* (`send`), or *copied*.
* **The Conflict:** If all threads share a single global `Data Stack<String: String Pool>` or `Data Stack<Mixed>`, every allocation requires mutex locking or atomic CAS operations—violating Rule S8 and bottlenecking multi-core scaling.

### Issue 5: Opt-In Memory Modes (Manual & GC) Interaction
* **The Flaw:** Fusion allows projects or modules to opt into **Manual** allocation or **GC** (`README.md`: "Code as Infrastructure"). If an opt-in GC object holds a reference into a scoped `Data Stack`, or a `Data Stack` holds a GC root, the GC tracer will either miss live objects (premature sweep) or scan dead stack memory (segfault).

---

## 3. Proposed Architectural Fixes (v3 Design)

### Fix 1: Thread-Local & Service-Owned Data Stacks (Zero-Lock Allocation)
Align Data Stacks directly with Fusion's ownership and `service` model:
1. **Thread-Local Default:** Every thread (and every `BasicService` / `HotPathService` worker) owns its own local Data Stacks. Allocations require **zero locks and zero atomics**.
2. **Service-Scoped Stacks:** When a `service` is created, it receives a private `Service Arena` (a set of Data Stacks owned exclusively by that service's worker).
   * When a value is **moved** (`send`) into a service, ownership transfers; if the value lives in a dedicated `Data Stack<Type: Pool>`, the entire region page can be transferred in $O(1)$ without deep copying.
   * For `hotpath service`, its Data Stacks are pre-allocated and prefaulted during the **set-up block** (`H8`), and locked against growth during the `running` phase (`H1`).
3. **Immutable Shared Pools (`Shared String Pool`):** Interned strings are immutable. Each thread allocates into a thread-local string chunk and periodically publishes/deduplicates into a read-only global pool (or uses lock-free read-only segments), preserving zero-lock fast paths.

### Fix 2: Sharpen the 5 Data Stack Roles & Backing Allocators
Replace the overlapping `<Mixed>` / `<General>` distinction with five distinct, compiler-routable region strategies:

| Data Stack Type | Purpose & Lifetime | C Codegen Backing Strategy | Reclamation |
| :--- | :--- | :--- | :--- |
| **`1. Data Stack<Single>`** | Homogeneous objects of type `T` tied to a lexical scope or frame. | **Typed Bump Arena** (contiguous array of `sizeof(T)`). Max cache locality. | $O(1)$ pointer reset on scope exit. |
| **`2. Data Stack<Scoped: Frame>`** *(replaces Mixed)* | Heterogeneous objects whose lifetimes are bound to a single function frame, loop iteration, or `service.run` block. | **Linear Bump Arena** (aligned variable-size bump pointer). | $O(1)$ bulk wipe when frame/block exits. Zero fragmentation. |
| **`3. Data Stack<Pool: Type>`** | Named, long-lived object pools (`String Pool`, `ASTNode Pool`, parent + child object trees). | **Segmented Slab / Page Pool** (parent header followed inline by child objects). | Freed per-pool or via generational/epoch reset. |
| **`4. Data Stack<General: Heap>`** | Dynamic objects whose lifetimes outlive their creation scope and cannot be statically proven by escape analysis. | **Segregated Size-Class Free-List** (mimalloc/jemalloc style bins) + **Single-Owner `free()`**. | Deterministic `drop()`/`free()` at owner's scope end (reclaims holes immediately). |
| **`5. Opt-In Bridge (GC / Manual)`** | Explicit `@manual` pointers or `@gc` managed objects when configured in `fusion.toml`. | **Explicit `malloc/free`** or **Boehm/Immix GC Heap** with registered root table. | Manual `free()` or GC cycle; write-barriers prevent dangling cross-stack pointers. |

### Fix 3: Compile-Time Region Hierarchy Rule (Preventing Dangling Pointers)
Enforce a strict **Outlives Partial Order** in the semantic analyzer (`src/semantic/`):
* **Rule R1 (Upward Pointer Prohibition):** An object in Data Stack $A$ may only store a reference to an object in Data Stack $B$ if $\text{Lifetime}(B) \ge \text{Lifetime}(A)$.
* **Rule R2 (Auto-Promotion via Escape Analysis):** If the compiler sees a variable allocated in `Data Stack<Scoped: Frame>` being returned from a function or stored into a longer-lived `Data Stack<Pool>`, the compiler automatically promotes its allocation site to the target's Data Stack (or `Data Stack<General: Heap>`).
* **Rule R3 (Zero-Escape Service Requests):** Per `Service.md` Rule S3, references borrowed from a `service`'s Data Stack carry a scoped region tag `'req` that cannot outlive the `service.run` block or method call.

---

## 4. C Codegen Blueprint (For Claude Code Implementation)

When implementing this in `src/codegen/` and the C runtime (`fusion_rt.h` / `fusion_rt.c`), map the architecture to clean C99/C11 primitives:

```c
// 1. Linear / Single Bump Stack (Zero-overhead scope allocation)
typedef struct FusionDataStack {
    uint8_t* base;
    uint8_t* cursor;
    uint8_t* limit;
    struct FusionDataStack* prev; // Chained pages if initial capacity exceeded
} FusionDataStack;

static inline void* fusion_stack_alloc(FusionDataStack* stack, size_t size, size_t align) {
    uintptr_t aligned = ((uintptr_t)stack->cursor + (align - 1)) & ~(align - 1);
    if (__builtin_expect(aligned + size > (uintptr_t)stack->limit, 0)) {
        return fusion_stack_alloc_slow(stack, size, align); // Allocate chained block
    }
    stack->cursor = (uint8_t*)(aligned + size);
    return (void*)aligned;
}

// 2. Scope checkpoint for O(1) bulk reclamation
typedef struct {
    FusionDataStack* page;
    uint8_t* saved_cursor;
} FusionStackMark;

static inline FusionStackMark fusion_stack_mark(FusionDataStack* stack) {
    return (FusionStackMark){ .page = stack, .saved_cursor = stack->cursor };
}

static inline void fusion_stack_restore(FusionStackMark mark) {
    // Free any chained overflow pages allocated after mark.page, then reset cursor
    fusion_stack_free_overflow_after(mark.page);
    mark.page->cursor = mark.saved_cursor;
}
```

### Compiler Pipeline Integration Checklist (`src/`)
1. **`src/semantic/escape_analysis.py` (New Pass):**
   * Classify every allocation AST node into: `STACK_VALUE`, `DATA_STACK_SINGLE`, `DATA_STACK_SCOPED`, `DATA_STACK_POOL`, `DATA_STACK_GENERAL`, or `OPT_IN_GC_MANUAL`.
   * Verify **Rule R1** (no long-lived stack pointing to a shorter-lived stack).
   * Verify **HotPath Rule H1/H8** (reject any `DATA_STACK_*` growth calls inside `hotpath` functions outside the set-up block).
2. **`src/semantic/service_check.py`:**
   * Bind each `service` instance to its own `FusionServiceMemoryContext` (holding its private Data Stacks).
   * Enforce that cross-thread `send()` operations either move an entire owned Data Stack page or deep-copy into the target service's Data Stack.
3. **`src/codegen/memory_gen.py`:**
   * Emit `FusionStackMark` at the entry of functions/loops that own `Data Stack<Single>` or `Data Stack<Scoped: Frame>`, and `fusion_stack_restore()` on all exit paths (`return`, `break`, error propagation).
   * Emit deterministic `fusion_general_free()` calls at the end of single-owner lifetimes for `Data Stack<General: Heap>` objects.