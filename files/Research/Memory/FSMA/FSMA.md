# FSMA - the Fusion Structured Memory Architecture

The abstract of every rule and setting for how FSMA allocates memory. Research R11 (files/FEATURES.md),
started 2026-11-24.

**Status: research - nothing here is decided.**
- Each rule (A1...) and setting is a proposal; the user decides each one (Decisions.md, Rule 3b).
- The research runs after R10 (money).
- It ends in decisions, then a task.
- It is the full form of MEM.009 (arena / region memory).

## Contents
- [1. What FSMA is](#1-what-fsma-is)
- [2. The kinds of Data Stack](#2-the-kinds-of-data-stack)
- [3. The rules](#3-the-rules)
- [4. Memory profiles](#4-memory-profiles)
- [5. Settings](#5-settings)
- [6. Gemini's review: what is taken](#6-geminis-review-what-is-taken)
- [7. Open points for the research](#7-open-points-for-the-research)
- [8. Files](#8-files)

---

## 1. What FSMA is

- **Primary Stack:** the execution frames and their locals. When it ends, the program ends and all stack and heap memory is reclaimed.
- **Heap:** a container of Data Stacks, not one shared pool of random allocations.
- **Memory Manager:** creates Data Stacks, grows them, tracks them and releases them.
- **Rule of thumb (user, 2026-11-24):**
  - A Data Stack is just a stack in the heap with a purpose; there is nothing special about it.
  - What is special is how the Fusion compiler creates, fills and releases it.
  - The kinds below are a guideline for the compiler, not a fixed list.
  - Rules added over time tell the compiler how to manage memory properly.
- **Ownership stays first (D.013).** FSMA decides *where* an object lives. *Who* owns it is still decided by the ownership rules (MEM.001-MEM.013).
- **Images** (in `images/`):
  - **v2 Complex: the main image;**
  - v1 Simple: the idea at a glance;
  - v3 Complex to fix: what needs care (Gemini);
  - Hierarchy: where data lives on the hardware;
  - Register-Only: devices with little or no memory.

## 2. The kinds of Data Stack

| Kind | Holds | A block is | The stack is released |
|---|---|---|---|
| `<Single>`, form 1 | the current frame's objects, of any type | bump-allocated | with the frame, as one unit |
| `<Single>`, form 2 | one type (e.g. `Car`) with its internals and its children's types | bump-allocated | with its owner, as one unit |
| `<Mixed>` | blocks of many uses: a grid, a mini heap | taken from a free slot, then freed and reused without the stack growing | with its owner |
| `<Scoped: Frame>` | Gemini's frame / loop / `run` arena, added **as needed** | bump-allocated | reset when the frame or loop ends |
| `<General>` | the catch-all: one-time, short-lived, or fitting nowhere else | taken from size-class free lists (Gemini agrees) and freed one by one | with the program, or by owner |
| `<String: StringPool>` | each distinct string, stored once and reused (interned) | interned | with the program, or by its owner |
| `<Type: NamePool>` | a named pool of one type plus its children (form 2 of Single, named) | from a slab or slots | per pool |

- **Reset or destroy:** a stack is either reset (its memory kept and reused) or destroyed (its memory given back). This is chosen per stack.
- **`<Mixed>` against `<Scoped>`:**
  - Mixed reuses holes where they are (v2's two columns);
  - Scoped never has holes, because everything in it ends together.

## 3. The rules

Each rule is a proposal for the user to decide.

| # | Rule | Source |
|---|---|---|
| A1 | Ownership stays first: a Data Stack only decides where an object lives | D.013 |
| A2 | Every Data Stack has one owner (a frame, an object, a service or the program) and is released when that owner ends | user |
| A3 | Outlives: a longer-lived stack never holds a reference into a shorter-lived one. This is "a borrow is never stored" (MEM.003) taken to stacks | Gemini R1 |
| A4 | Promotion: a value that escapes its stack (returned, or stored in a longer-lived stack) is allocated in the longer-lived stack from the start, decided at compile time | Gemini R2 |
| A5 | Nothing borrowed from a service's stack outlives the request | Gemini R3, S3 |
| A6 | A service owns its Data Stacks: only its worker allocates in them, so no locks are needed | Gemini, S1 / S8 |
| A7 | A hot-path service's stacks are made in its set-up block and never grow while it runs | Gemini, H1 / H8 |
| A8 | A slot in Mixed or a NamePool is reached by a handle (stack, slot, generation), so a reference to a reused slot is caught, not followed | ChatGPT (GooseVsRust.md) |
| A9 | Moving a value into a service moves its whole page when it lives alone in a NamePool; otherwise the value is copied | Gemini |
| A10 | GC and MANUAL objects live apart (MEM.005); a Data Stack holding a GC root registers it | Gemini issue 5 |
| A11 | The Memory Manager is never a bottleneck: each thread and each service has its own; nothing is global except read-only pools | ChatGPT, Gemini |

## 4. Memory profiles

The profile is chosen by the target (the Register-Only image), with `[stdlib] layer` (std / alloc / core) and HIDL (Task 41).

| Profile | Memory | Data Stacks become |
|---|---|---|
| FULL | stack, heap, Data Stacks | as above |
| STATIC | fixed RAM, no heap | static regions, sized at compile time |
| REGISTER-ONLY | registers and ROM, no RAM allocation | values in registers; no Data Stacks |

## 5. Settings

These are proposals only: the names are still to decide, and each has a safe default. A setting moves to
`files/spec/001-TomlSettings.md` only once the user decides it.

- `[memory] model = "fsma" | "heap"`: FSMA, or today's plain heap with counting
- `[memory] profile = "full" | "static" | "registers"`
- `[memory] strategy`, which exists already (ownership / GC / manual, MEM.005): how each meets FSMA
- `[memory.stacks] general = "freeList"`: how `<General>` allocates
- `[memory.stacks] mixedSlots = true`: the grid
- `[memory.stacks] scoped = false`: Gemini's frame arena, used when needed
- `[memory.stacks] stringPool = true`
- `[memory.stacks] initialSize`, `growBy`, `maxSize`: a full stack is an error, never a crash
- `[memory.stacks] handles = "generation" | "pointer"`: the safety check (A8) against raw speed
- `[memory.stacks] release = "reset" | "destroy"`: the default for a stack whose owner ends
- `[memory.pools.<Name>] type = "Customer"`, `children = true`, `initialSize`: a named pool
- `[memory.services] ownStacks = true` (A6)
- `[memory.services] hotpathPrefault = true` (A7)

## 6. Gemini's review: what is taken

Gemini's review is input, not a decision (Rule 3c). The full text is in `Gemini_FSMA_Review.md`.

- **Taken:**
  - stacks owned by a thread or service (A6);
  - hot-path stacks made at set-up (A7);
  - R1-R3 (A3-A5);
  - moving a page (A9);
  - GC roots (A10);
  - the C blueprint: a bump allocator and a mark restored on every exit path;
  - `<General>` as size-class free lists.
- **Added as needed:** `<Scoped: Frame>`, beside Mixed.
- **Not taken:**
  - replacing `<Mixed>`: Gemini read it as a strict stack that can't reuse holes, but it is a grid that does;
  - `<Single>` as one type only: it has two forms (section 2).
- **A wrong reference:** the service review cites `StructuredMemoryReview.md`, which is `Gemini_FSMA_Review.md`.

## 7. Open points for the research

- How the compiler picks a kind: by type, by owner, by a word in the code, or by a toml setting
- Growing a stack: chained pages (Goose: references stay valid) against copying
- Fragmentation in `<Mixed>` and the NamePools: size classes, compaction never (it breaks raw C pointers)
- How the generated C carries handles, and what a check costs
- The prior work, with R6 and R4.3 (an arena per service):
  - Goose's data stacks;
  - Zig's allocators;
  - Rust and arenas (bumpalo);
  - Erlang's per-process heaps;
  - mimalloc's size classes.
- Measured against today's counting (benchmarks, L16.0)

## 8. Files

- `MemoryAllocation.md`: a primer on stack, heap, GC, counting, ownership, arenas, regions and pools
- `MemoryAllocationNew.md`: the first FSMA sketch (Data Stacks A and B, a general heap; reset against destroy; Data Stack C as a grid)
- `Gemini_FSMA_Review.md`: Gemini's review and its v3
- `images/`: the five SVGs listed in section 1
- `../GooseVsRust.md`: ChatGPT's Goose against Rust, then the FSMA follow-up (handles, named pools, 12 principles)
- `../../Services/Gemini_Service_Review.md`: Gemini's service review (R3)
- `Notes/`: the old images (`stack vs heap.jpeg`, the extended PNG)
