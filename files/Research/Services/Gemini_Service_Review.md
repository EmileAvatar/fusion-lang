# Fusion `service` Concurrency Architecture — Review & Compiler Spec

**Target Audience:** Fusion Compiler Team / Claude Code Implementation Agent  
**Reference Docs:** `files/Service.md`, `StructuredMemoryReview.md`  
**Context:** Fusion enforces single-owner semantics by default and isolates cross-thread shared state behind the `service` keyword. External threads never mutate a service's internal fields directly; instead, they submit requests to the service's mailbox/worker, which executes them sequentially as atomic steps.

---

## 1. Executive Summary

Fusion's `service` model combines **Actor-style single-writer isolation** with **static ownership verification** and **adaptive lowering**. By making the compiler responsible for choosing the execution mechanism (plain variable, CPU atomic, shared worker pool, dedicated worker pool, or core-pinned lock-free ring buffer), Fusion eliminates manual mutexes and lock-ordering deadlocks while keeping sequential syntax ergonomic.

To make this design airtight during semantic analysis (`src/semantic/`) and C codegen (`src/codegen/`), five concurrency edge cases must be enforced at compile time and in the C runtime.

---

## 2. Identified Edge Cases & Compiler Fixes

### Edge Case 1: Synchronous Call-Cycle Deadlocks (Actor Deadlocks)
* **The Risk:** While `service` eliminates *mutex-ordering* deadlocks, **synchronous request cycles** can still deadlock because services are non-reentrant (`Service.md` Rule 3):
  * Service `A` sends a synchronous request to Service `B` and blocks waiting for the reply.
  * While `A` is blocked, Service `B` sends a synchronous request back to Service `A` (or `A -> B -> C -> A`).
  * Both workers block indefinitely until `Timeout` fires.
* **Compiler Fix (Static Call-Graph Cycle Check):**
  1. Build a directed call graph of synchronous service invocations (`sync_service_calls`) during semantic analysis.
  2. **Direct Self-Call:** Emit a compile error if a `service(x).run { ... }` block or a `service class` method invokes a synchronous request on `x` itself.
  3. **Multi-Service Cycle:** Run cycle detection (Tarjan's SCC / DFS) on `sync_service_calls`. If a cycle `A -> B -> ... -> A` exists, emit a compile error instructing the developer to break the cycle with `async` on at least one edge.

### Edge Case 2: Closure Capture Inside `service(x).run { ... }`
* **The Risk:** `service(x).run { ... }` is written inside the *caller's* lexical scope, even though it executes under `x`'s exclusive ownership/worker. If the `.run` block captures a non-service mutable local variable by reference from the caller's stack frame (especially when combined with `async`), it creates a data race or dangling stack pointer.
* **Compiler Fix (Strict Capture Boundary — Rule S6):**
  * Treat every `service(x).run { ... }` block as a **thread-boundary closure**.
  * Any outer variable referenced inside `.run` must satisfy one of three rules:
    1. **Copied by value** (`byVal` / primitive / immutable value type),
    2. **Moved** (`send`) into the `.run` request payload (invalidating the caller's binding), or
    3. **Another `service` handle** (which routes its own accesses safely through its own mailbox).
  * Borrowing a plain mutable outer variable inside `.run` must be a compile error.

### Edge Case 3: Thread-Pool Starvation via Blocking I/O in `SHARED` Services
* **The Risk:** When multiple services share a fixed `ThreadPool(N)` (`WorkerThreadType.SHARED`), if `N` services simultaneously execute blocking I/O (e.g., network socket reads, file sync, slow DB queries) inside a request or `.run` block, all `N` pool threads block. Unrelated CPU-bound services sharing that pool freeze completely.
* **Compiler Fix (Blocking-Effect Propagation):**
  1. Introduce a compiler-inferred `[blocking]` effect flag (mirroring the `[hotpath]` effect system in `Service.md` Rule H2/H4). Any stdlib call that performs OS blocking I/O or sleeps carries `[blocking]`.
  2. Propagate `[blocking]` transitively through function calls.
  3. If a `service` invokes any `[blocking]` function inside its methods or `.run` blocks:
     * When `WorkerThreadType == AUTO`, the compiler **automatically lowers it to `WorkerThreadType.SINGLE`** (dedicated worker/pool) so it cannot starve the shared pool.
     * When the user explicitly sets `WorkerThreadType.SHARED`, emit a compile warning (`[concurrency.traps]` -> `blockingInSharedPool`).

### Edge Case 4: The "Timeout Ghost Effect" on Queued Requests (`Rule 5`)
* **The Risk:** `Service.md` Rule 5 notes that a timeout means the caller stopped waiting, not that work was undone. However, if a request times out *while still sitting in the mailbox queue* (before the worker has even popped it), executing it later causes silent duplicate mutations when callers retry non-idempotent requests (e.g., `account.balance -= 800`).
* **Compiler & Runtime Fix (Two-Phase Request State):**
  * Represent each queued request in the C runtime with an atomic state header: `PENDING -> CLAIMED -> COMPLETED | FAILED`.
  * **Queue Timeout (Before Claim):** If the caller's `Timeout` expires while the request is still `PENDING`, the caller atomically transitions the slot to `CANCELLED` (CAS `PENDING -> CANCELLED`). When the worker pops a `CANCELLED` slot, it skips execution immediately.
  * **Execution Timeout (After Claim):** Once the worker atomically transitions the slot `PENDING -> CLAIMED`, the request cannot be cancelled mid-flight (preserving Rule 5's atomicity guarantee); if the caller times out during execution, the request finishes its atomic step cleanly and reports `TIMED_OUT` to the caller.

### Edge Case 5: Group Service Scope & Child Thread Lifetimes
* **The Risk:** In `service(person, honda) carPerson`, `person` and `honda` are temporarily governed by `carPerson` until the group goes out of scope (`Service.md` Group Rule 2). If a parent thread spawns child threads (`go worker(person)`) while the group is active, and the parent exits the group's lexical scope while child threads are still running, `person` would revert to an unguarded plain variable while still shared across threads.
* **Compiler Fix (Structured Concurrency Scope Tie):**
  * Enforce **Structured Concurrency** for any scope containing a `group service`: all `go` child tasks spawned within that scope (or receiving handles to members of that group) must be joined before the `group service` dissolves at scope exit.
  * Alternatively, if a child thread outlives the lexical scope (detached `go`), automatically promote the group's backing state to a reference-counted `SharedService` (`Rule S5`) until the last thread handle drops.

---

## 3. Adaptive Lowering Matrix (For `src/semantic/` & `src/codegen/`)

The compiler should lower `service T x = ...` into one of five C runtime representations based on static escape/thread analysis and user settings:

| Lowering Tier | Trigger Condition | C Runtime Representation | Synchronization Cost |
| :--- | :--- | :--- | :--- |
| **Tier 0: Plain Variable** | Escape analysis proves `x` never crosses a `go` thread boundary (`WorkerThreadType == AUTO`). | Raw C variable / struct on local stack or Data Stack. | **0 ns** (zero overhead). |
| **Tier 1: Hardware Atomic** | `T` is a primitive (`int`, `long`, `bool`, `float`) accessed across threads without multi-statement `.run` blocks. | C11 `_Atomic(T)` with `atomic_fetch_add` / `atomic_compare_exchange`. | **~5–15 ns** (lock-free CPU instruction). |
| **Tier 2: `SharedService` (Shared Pool)** | Struct/class/group accessed by multiple threads; non-blocking; `WorkerThreadType == AUTO` or `SHARED`. | `FusionMailbox` + private `FusionServiceMemoryContext` scheduled onto global `ThreadPool`. | **~50–150 ns** (lock-free MPSC queue push). |
| **Tier 3: `BasicService` (Dedicated)** | Heavy workload, `[blocking]` I/O detected, or explicit `WorkerThreadType.SINGLE`. | `FusionMailbox` + dedicated OS worker thread(s) (`ThreadPool(N)`). | Dedicated core/OS thread; zero pool starvation. |
| **Tier 4: `HotPathService`** | Declared with `hotpath service`. | Core-pinned thread (`pthread_setaffinity_np`), cache-line padded SPSC/MPSC power-of-2 ring buffer, `Wait.SPIN`, pre-faulted Data Stacks (`H1–H9`). | **< 20–50 ns** deterministic tail latency. |

---

## 4. C Codegen Blueprint (For Claude Code Implementation)

When generating C code for `BasicService` / `SharedService` mailboxes in `src/codegen/service_gen.py`:

```c
#include <stdatomic.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    REQ_PENDING   = 0,
    REQ_CLAIMED   = 1,
    REQ_CANCELLED = 2,
    REQ_COMPLETED = 3,
    REQ_FAILED    = 4
} FusionReqState;

typedef struct FusionRequest {
    _Atomic uint32_t state;          // Prevents Ghost Execution on queue timeout
    void (*fn)(void* ctx, void* arg);
    void* arg;                       // Owned/copied payload in target service's Data Stack
    _Atomic bool done;               // Signaled for synchronous callers
} FusionRequest;

// Worker loop: single writer, zero locks on service state
static inline void fusion_service_step(void* service_state, FusionRequest* req) {
    uint32_t expected = REQ_PENDING;
    // Atomically claim the request; if caller timed out while queued, skip it
    if (!atomic_compare_exchange_strong(&req->state, &expected, REQ_CLAIMED)) {
        return; // REQ_CANCELLED
    }
    req->fn(service_state, req->arg);
    atomic_store_explicit(&req->state, REQ_COMPLETED, memory_order_release);
    atomic_store_explicit(&req->done, true, memory_order_release);
}
```

### Compiler Pipeline Checklist (`src/`)
1. **`src/semantic/service_analyzer.py` (New Pass):**
   * Classify every `service` declaration into **Tier 0 – Tier 4** using thread-escape and `[blocking]` effect analysis.
   * Build `sync_service_calls` graph and reject self-calls or synchronous call cycles (`Edge Case 1`).
   * Validate `.run { ... }` closure captures against **Rule S6** (`Edge Case 2`).
   * Enforce structured join boundaries for `group service` scopes (`Edge Case 5`).
2. **`src/semantic/hotpath_check.py`:**
   * Enforce Rules `H1–H9`: verify zero Data Stack growth calls outside the set-up block, zero `[blocking]` calls, and fixed-size value messages.
3. **`src/codegen/service_gen.py`:**
   * Emit C11 `_Atomic` operations for **Tier 1** services.
   * Emit `FusionRequest` structs with two-phase `REQ_PENDING -> REQ_CLAIMED` CAS transitions for **Tier 2 / Tier 3** services (`Edge Case 4`).
   * Bind each service's worker to its own `FusionServiceMemoryContext` (from `StructuredMemoryReview.md`) so internal allocations remain 100% lock-free.