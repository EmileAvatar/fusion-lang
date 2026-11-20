# Memory research: Goose, arenas, Fil-C, where Rust is not memory safe, Zig's allocators (Claude, 2026-11-20)

For future research - nothing here is decided. Listed in FEATURES "Research" R6. One line per point, each marked
**have**, **take**, **discuss** or **skip**.

Sources:
- [goose_language_and_fusion_comparison.md](goose_language_and_fusion_comparison.md) - ChatGPT on Goose (https://aardappel.github.io/goose/)
  and other languages. The first draft, `Goose.md`, is the same text with image links; it went to `Notes/Goose_original_chatgpt.md`
  (not in git) - nothing in it is missing from this one
- Fil-C: https://fil-c.org/ (read 2026-11-20)
- The user's notes (2026-11-20): "Rust may not be memory safe in some situations"; Zig's allocator (already Research R4, C1 / Z5)

**A correction to the Goose document:** it says Fusion's memory model is "still to be decided". It is decided and built:
ownership first (one owner, moves, borrows - Task 48, MEM.001-MEM.013), objects counted and freed when the last holder
goes (CLS.001), no GC by default (D.080); arenas are designed only (MEM.009).

---

#### 1. What an arena is (the user's question)

How memory is normally handed out and given back - the **heap**:
- each `malloc` (C) / `new` (C++, Java) asks the allocator for one block: it searches its free lists for a gap that fits,
  marks it used, and records its size
- each `free` gives that one block back: the allocator merges it with free neighbours so the space can be reused
- cost: every allocation and every free is its own piece of work - fast (tens of nanoseconds) but it adds up with
  millions of small objects; the heap also gets fragmented (gaps too small to use)
- Fusion today: every string, List and object is one heap block, freed on its own when its owner goes

An **arena** (also called a region, a zone, a bump allocator):
- one big block is taken up front (say 1 MB)
- **allocating** = "the next free byte is here; move the pointer forward by the size" - one addition, no search
- **freeing one object**: not done at all - nothing is given back one by one
- **freeing everything**: move the pointer back to the start (or give the whole block back) - one step, however many
  objects were in it
- so: allocating is the fastest possible, freeing a million objects costs the same as freeing one

When it fits - many objects that all die at the same moment:
- one web request: everything made while handling it is dropped when the reply is sent
- one game frame: temporary data for that frame
- a compiler pass: the tokens and tree nodes of one file
- a Fusion service request, or a whole service (Research R4, C1)

When it doesn't fit:
- objects that live different lengths of time - a long-lived one keeps the whole arena alive (memory grows)
- a reference into the arena that outlives it is a dangling pointer - the language must stop that
  (Goose's compiler does; Fusion's ownership rules would have to)

Where other languages have it:
- **C / C++:** hand-written, or libraries (`std::pmr::monotonic_buffer_resource` in C++17)
- **Zig:** `std.heap.ArenaAllocator` - passed to any function that takes an allocator
- **Rust:** crates (`bumpalo`, `typed-arena`)
- **Go:** an experimental `arena` package (put on hold)
- **Goose:** built into the language - its "data stacks" are compiler-managed arenas freed at the end of a scope
- **Java / C# / Go:** their garbage collectors allocate this way inside ("bump pointer" in the young generation),
  then move the survivors out

The speed, in rough numbers (they depend on the machine and the allocator):
| | Heap (`malloc` / `free`) | Arena |
|---|---|---|
| allocate | a search: ~20-100 ns | a pointer bump: ~1-2 ns |
| free one | ~20-100 ns | nothing |
| free a million | a million frees | one step |
| fragmentation | yes | none inside the arena |
| objects of different lifetimes | fine | wastes memory |

#### 2. Goose - the points
- **G1 No heap: dynamic data on compiler-managed "data stacks" (arenas per scope)** - Fusion: the heap with ownership. **Discuss** - with MEM.009: an arena as an option per function, service or request, not the only model (Goose's limits below)
- **G2 Lifetimes worked out by the compiler, never written** - Fusion: the same aim - no lifetime annotations; borrows are never stored (MEM.003). **Have**
- **G3 A growing array never moves - references into it stay valid** (reserved address space) - Fusion: a growable array or List moves when it grows; a borrow of a slot can't be stored, so nothing dangles. **Discuss** for L16 (profiling): reserving address space for very large arrays
- **G4 Six array forms** (`T[k]`, `T[]`, `T[..k]`, `T[..]`, `T[>..]` grow-only, `T[>..<]` grow and shrink) - Fusion: plain, fixed, growable (D.141) - close. **Have** - maybe a grow-only form later
- **G5 Records and enums of different sizes packed tightly** - **Discuss** after self-hosting (L16)
- **G6 Runs a program at once in memory (TinyCC), or builds C with a C compiler** - Fusion: C through GCC; script mode (Task 58) could use TinyCC for an instant start. **Take into Task 58.2's comparison**
- **G7 `goose check` - type checks without building** - Fusion: no such command yet. **Take** - small (`python main.py x.fusion --check`)
- **G8 Debug checks for overflow, bounds, enum tags** - Fusion: always on in safe mode. **Have**
- **G9 Limits: data lifetimes tied to scopes, some recursion and closure patterns not allowed, long-lived object graphs hard** - why Fusion should not make it the only model. **Skip as the default**
- **G10 Its own benchmarks: faster than C++ and Rust** - the project's own numbers. **Note only** - for Research R2.1 (Fusion's benchmark)
- **G11 "Memory safety a result of the design, not something the developer remembers"** - Fusion's aim too (GOL.005). **Have**

#### 3. Fil-C - what it is and whether Fusion can use it
What it is: a memory-safe C and C++ - a changed clang (20.1.8) that compiles existing C with no or few changes.
- every pointer carries hidden bounds ("InvisiCaps"); out of bounds, use after free, a double free all stop the program (a "Fil-C panic")
- a concurrent garbage collector (FUGC); `free()` still works and later use is caught
- runs CPython, OpenSSH, Emacs, Wayland; threads, atomics, signals, setjmp work
- cost: up to about 4x slower in the bad cases; not ABI-compatible with normal C (its own libraries); 64-bit only
- clang, not GCC; Linux, Darwin, Windows (Peregrine distribution); Apache 2 / BSD licences

For Fusion:
- **F1 A second safety net for the C Fusion writes** - build a program's C with Fil-C in a test or debug mode: any memory bug in the generated C or the run-time is caught. **Discuss** - a `[backend] cCompiler` / build mode option; good for the test suite and the leak check
- **F2 Safe C libraries for Fusion programs** - a C library (Lua in Task 60, any `extern "C"` one) built with Fil-C can't corrupt the program's memory. **Discuss** for Task 60 / Task 39 - but it can't be mixed with normal C (no shared ABI)
- **F3 Not the main backend** - 4x slower and a GC: against "fast, no GC by default". **Skip as the default**
- **F4 Its pointer-with-bounds idea** - Fusion already checks every index. **Have**

#### 4. Where Rust is not memory safe (the user's note: "we need to check")
Rust's guarantee holds only for "safe Rust", and has known gaps:
- **R1 `unsafe` blocks** - the standard library and many crates use them; a bug inside breaks safety for everyone above. Fusion: `unsafe` designed (MEM.006) - **take:** keep it rare, visible, and counted in a report
- **R2 Compiler soundness bugs** - a type-system hole known since 2015 (issue 25860) lets safe code read freed memory (shown by the `cve-rs` project). **Note:** a checker can have bugs - test it hard (Fusion's leak check of every example)
- **R3 Leaks are "safe"** - `Rc` cycles and `mem::forget` leak memory and Rust allows it. Fusion: a warning for a class cycle that could leak (CLS.010); the leak check. **Have**
- **R4 Integer overflow wraps silently in release builds** - Fusion: overflow is always an error unless asked for (TYP.001, `unchecked`). **Have**
- **R5 Stack overflow aborts** - Fusion: a catchable StackOverflowError (FUN.007). **Have**
- **R6 Calling C (FFI)** - all of C's dangers come back. Fusion: the same risk with `extern "C"` - **discuss** with F2 and Task 39
- **R7 Data races are prevented, deadlocks are not** - Fusion's services aim at both (GOL.004). **Have (designed)**
- To check in full: a list of Rust CVEs in safe code, and what each would mean for Fusion's checker

#### 5. Zig's allocators (the user's note)
Already in Research R4 (Points.md C1, Z5): functions take an allocator, so a program picks a general one, an arena,
or a fixed one for a small device. **With section 1 above:** the question for Fusion is where an arena is chosen -
per function, per service, per request - while ownership stays the default.
