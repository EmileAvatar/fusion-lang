# Memory Management Across Programming Languages & Hardware Tiers

**Context:** Most traditional languages treat the heap as a single monolithic pool of memory. However, modern systems languages and high-performance runtimes have increasingly moved toward **segregated arenas, regions, and typed pools**—the exact family of design that Fusion's **Structured Memory Architecture (Data Stacks)** belongs to.

---

## 1. How Other Languages Handle the Heap

Languages generally fall into four architectural categories regarding whether they dump objects randomly onto a single heap or partition memory systematically:

### Category A: Monolithic / General-Purpose Heap (Classic Approach)
* **Languages:** C (`malloc`), C++ (`new`), Python, Ruby, older Java.
* **How it works:** Objects of all types and lifetimes are placed into a single shared heap (often backed by general-purpose allocators like `ptmalloc`, `jemalloc`, or `mimalloc`).
* **Pros:** Simple programming model; any object can easily point to any other object.
* **Cons:** Poor CPU cache locality (unrelated objects sit next to each other), heap fragmentation, and expensive per-object allocation/freeing or global Garbage Collection (GC) pauses.

### Category B: Regions, Arenas & Data Stacks (Closest to Fusion)
* **Languages:** **Zig**, **Odin**, **Jai**, **Rust** (via `bumpalo` / `typed-arena`), **Vale** (Generational References + Regions), **Cyclone** (historical pioneer of region-based memory).
* **How it works:** Instead of freeing individual objects, memory is divided into **Arenas / Regions** (what Fusion calls **Data Stacks**).
  * **Zig & Odin:** Make allocators explicit parameters. Developers routinely pass an `ArenaAllocator` (bump stack) for frame/request-scoped data, a `PoolAllocator` for homogeneous structs (like Fusion's `Data Stack<Single>`), and a `GeneralPurposeAllocator` for unpredictable lifetimes.
  * **Vale:** Uses compile-time region analysis so immutable/isolated regions require zero reference-counting overhead—very similar to Fusion's `service` isolation.
  * **Rust:** Defaults to single-owner `Box`/`Vec` on the global allocator (`jemalloc`/system), but high-performance Rust codebases (compilers like `rustc`, game engines like `Bevy`) rely heavily on **Typed Arenas** and **ECS (Entity Component System)** archetype tables to group identical structs contiguously in RAM.

### Category C: Generational & Thread-Local Segregated Heaps (Managed VMs)
* **Languages:** **Go**, **Java (ZGC / Shenandoah)**, **C# (.NET)**, **V8 (JavaScript)**.
* **How it works:** Even though users *think* they are throwing random objects onto one heap, modern runtimes secretly partition memory behind the scenes:
  * **TLABs (Thread-Local Allocation Buffers):** Used in JVM, .NET, and Go (`mcache`). Each thread gets its own private bump-allocated chunk of RAM so small allocations require zero locks (matching Fusion's Thread-Local Data Stacks).
  * **Size-Class Spans (Go & mimalloc):** Go divides the heap into ~67 size classes (8 bytes, 16 bytes, 32 bytes, etc.) so objects of similar sizes sit together without fragmentation.
  * **Generational Regions (Java / .NET / V8):** Separates short-lived objects ("Eden / Young Gen" bump-allocated stack) from long-lived objects ("Old Gen").
  * **Escape Analysis (Go & JVM):** The compiler analyzes whether an object escapes a function; if it doesn't, it is placed directly on the CPU **Call Stack** instead of the heap.

### Category D: Data-Oriented / Archetype Storage (Game Engines & HFT)
* **Technologies:** **Bevy (Rust)**, **Unity DOTS (C#)**, **Flecs (C/C++)**.
* **How it works:** Completely abandons scattered heap objects. All entities with the same components are packed into tightly aligned, homogeneous arrays (`Struct of Arrays`) so the CPU prefetcher reads them at maximum memory bandwidth. Fusion's `Data Stack<Single>` and `Data Stack<Pool>` bring this natively into the language runtime.

---

## 2. Industry Best Practices (What Works Best Today)

Across modern systems engineering, five principles have emerged as the gold standard:

1. **Lifetime-Based Grouping (Bulk Deallocation):**
   Never free 10,000 individual nodes one by one if they all die at the end of an HTTP request, compiler pass, or game frame. Allocate them in a bump-pointer **Scoped Arena** (`Data Stack<Scoped>`) and wipe the whole region in one CPU instruction ($O(1)$).
2. **Cache-Line Contiguity (`Data Stack<Single>`):**
   Modern CPUs are bottlenecked by RAM latency (~60–100 ns), not clock speed. Keeping homogeneous structs contiguous ensures a single 64-byte L1 cache line fetch loads multiple useful objects at once.
3. **Thread-Local First, Shared Second:**
   Cross-thread synchronization on every `alloc()` kills multi-core scaling. Every thread or `service` should allocate from its own private memory region (`Service.md` Rule S8).
4. **String Interning & Deduplication (`String Pool`):**
   Programs duplicate the same strings (JSON keys, identifiers, HTTP headers) thousands of times. Interning them into a dedicated pool saves massive RAM and turns string equality (`a == b`) into a single pointer comparison (`ptr_a == ptr_b`).
5. **Pre-Allocation for Real-Time Paths (`hotpath service`):**
   Never touch the OS allocator (`mmap`/`VirtualAlloc`) inside latency-critical loops. Pre-allocate and prefault pages during startup.

---

## 3. Low-Memory vs. High-Memory Strategy Guide

Because Fusion allows project-level hardware profiles in `fusion.toml` (just like `[concurrency.machine.min]` and `[concurrency.machine.small]` in `Service.md`), Fusion can automatically tune its **Data Stack** backing behavior based on available system RAM.

### A. Low-Memory Environments (Embedded, IoT, Containers `< 512 MB – 2 GB`)
* **Primary Bottleneck:** **Memory Fragmentation & Page Overhead.** Large pre-allocated arenas waste precious RAM if they sit half-empty.
* **Best Practices for Fusion:**
  1. **Small Initial Stack Pages (4 KB – 16 KB):** Start `Data Stack<Single>` and `Data Stack<Scoped>` with tiny OS page sizes (4 KB) and grow via linked chunks only on demand.
  2. **Aggressive Scope Reclamation:** Immediately release empty overflow pages back to the allocator on `fusion_stack_restore()` rather than caching them for reuse.
  3. **Strict String Pool Caps:** Use a bounded LRU or reference-counted `String Pool` so long-running embedded devices don't accumulate dead interned strings forever.
  4. **Prefer `Data Stack<General>` (Segregated Free-List) over Large Arenas:** Reusing freed slots immediately keeps peak RSS (Resident Set Size) as flat as possible.
  5. **Opt-In Mode Recommendation:** **Default Ownership (Zero GC)**. Tracing GCs typically require $2\times$ to $3\times$ live heap headroom to avoid thrashing—unsuitable for tight RAM budgets.

### B. High-Memory Environments (Servers, Workstations, HFT, Gaming `16 GB – 512 GB+`)
* **Primary Bottleneck:** **CPU Cache Misses, TLB Thrashing & Allocator Lock Contention.** RAM is cheap; CPU cycles and nanoseconds are expensive.
* **Best Practices for Fusion:**
  1. **Large Contiguous Virtual Arenas (2 MB Huge Pages):** Pre-reserve large virtual address ranges (e.g., 64 MB – 1 GB per Data Stack) backed by **2 MB Huge Pages** (`MAP_HUGETLB`). This dramatically reduces TLB (Translation Lookaside Buffer) misses in the CPU.
  2. **Page Caching / High-Water Mark Retention:** When `Data Stack<Scoped>` resets at the end of a request or frame, **keep the allocated pages warm in cache** instead of returning them to the OS. The next request runs with zero syscalls.
  3. **Dedicated Per-Service Arenas:** Every `service` gets its own isolated set of Data Stacks (`Single`, `Scoped`, `Pool`), eliminating all cross-core cache invalidation (false sharing).
  4. **Append-Only Global `String Pool`:** With abundant RAM, lock-free append-only string interning gives $O(1)$ deduplication with zero reference-counting overhead.
  5. **Opt-In Mode Recommendation:** **Default Ownership + `Data Stack<Pool>`** for predictable low latency, or **Opt-In GC** for rapid prototyping of complex graph structures where throughput matters more than strict pause determinism.

---

## 4. Summary Comparison Matrix

| Hardware Profile | Initial Page Size | Arena Reset Behavior | String Pool Strategy | Recommended Memory Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Low Memory** (`< 2 GB` / Embedded) | **4 KB – 16 KB** (grow on demand) | Free overflow pages immediately to OS | Bounded / ref-counted pool | **Default Ownership** (Zero GC) |
| **Standard** (`2 GB – 16 GB` / Desktop) | **64 KB – 256 KB** | Retain 1–2 warm pages; free excess | Per-thread local + shared pool | **Default Ownership** |
| **High Memory** (`16 GB+` / Server & HotPath) | **2 MB Huge Pages** (pre-reserved) | Retain full high-water mark in cache | Lock-free append-only pool | **Default Ownership** (or Opt-In GC for graphs) |

### How `fusion.toml` Can Expose This Automatically
Just as `Service.md` defines `[concurrency.machine.min]`, Fusion can expose `[memory.machine.*]` tiers in `fusion.toml`:

```toml
[memory.machine.min]          # Embedded / < 512 MB RAM
initialStackPage = "4KB"
retainWarmPages = false
stringPoolLimit = "4MB"
useHugePages = false

[memory.machine.standard]     # Desktop / 2 GB - 16 GB RAM
initialStackPage = "64KB"
retainWarmPages = true
stringPoolLimit = "128MB"
useHugePages = false

[memory.machine.high]         # Server / > 16 GB RAM
initialStackPage = "2MB"
retainWarmPages = true
stringPoolLimit = "unlimited"
useHugePages = true
```