# Fusion Structured Memory Architecture (FSMA)

How Fusion plans to organise memory: what it is, how the idea grew, what it holds today and the new kinds proposed.
For readers new to the idea - developers and AIs. Research R11 (files/FEATURES.md); started 2026-11-24.

**Status: research - nothing here is decided yet.** Each rule and kind is a proposal; the user decides each one
(Decisions.md). Today's compiler uses the plain heap with ownership and counting (Task 48); FSMA is the planned next
step. The working abstract of every rule and setting is
[Research/Memory/FSMA/FSMA.md](Research/Memory/FSMA/FSMA.md).

Contents:
- [1. The problem FSMA solves](#1-the-problem-fsma-solves)
- [2. The idea](#2-the-idea)
- [3. How it grew - v1 to v4](#3-how-it-grew---v1-to-v4)
- [4. The kinds of Data Stack today](#4-the-kinds-of-data-stack-today)
- [5. The rules](#5-the-rules)
- [6. A Data Stack made by hand](#6-a-data-stack-made-by-hand)
- [7. New kinds proposed (v4)](#7-new-kinds-proposed-v4)
- [8. Machines with little memory](#8-machines-with-little-memory)
- [9. What is still open](#9-what-is-still-open)
- [10. Files](#10-files)

---

## 1. The problem FSMA solves

A program keeps its data in two places:

- **the stack** - each function call's own values; fast, and gone when the call returns
- **the heap** - everything that must outlive a call (objects, Lists, strings); most languages treat it as one big
  pool of separate allocations

One big pool has costs: every allocation and free is a separate step, memory gets scattered (fragmentation), and
freeing is either the programmer's job (C - leaks, crashes), a garbage collector's (Java, Go - pauses) or tracked by
ownership (Rust - strict rules). A short primer on all of these: [MemoryAllocation.md](Research/Memory/FSMA/MemoryAllocation.md).

## 2. The idea

- **The heap is a container of Data Stacks**, not one pool. A Data Stack is simply a stack in the heap with a purpose:
  the objects of one frame, of one type, of one service.
- **The compiler creates, fills and releases them.** What is special is not the stack but how Fusion manages it - it
  knows from the code which objects belong together and when they end.
- **A Data Stack ends as a unit.** When its owner ends (a frame, an object, a service, the program), the whole stack is
  reset (its memory kept for reuse) or destroyed (given back) in one step - no object-by-object freeing.
- **Ownership stays first.** FSMA decides *where* an object lives; *who* owns it is still Fusion's ownership rules
  (files/Ownership.md, D.013).
- **The kinds are a guide for the compiler, not a fixed list** (user, 2026-11-24); rules added over time tell it how to
  manage memory well.

![FSMA v2 - the main picture](Research/Memory/FSMA/images/Fusion%20Structured%20Memory%20Architecture%20v2%20Complex.svg)

## 3. How it grew - v1 to v4

| Version | What it added | Picture |
|---|---|---|
| Sketch (2026-11-24) | Data Stacks A (one frame) and B (one type) beside a general heap; reset against destroy; Data Stack C as a grid | [MemoryAllocationNew.md](Research/Memory/FSMA/MemoryAllocationNew.md) |
| v1 Simple | the idea at a glance: the primary stack, the heap of Data Stacks, the Memory Manager | [v1](Research/Memory/FSMA/images/Fusion%20Structured%20Memory%20Architecture%20v1%20Simple.svg) |
| v2 Complex | the main picture: Single, Mixed (a grid that reuses holes), General, the string pool, named pools | [v2](Research/Memory/FSMA/images/Fusion%20Structured%20Memory%20Architecture%20v2%20Complex.svg) |
| v3 (Gemini) | what needs care: stacks that outlive others, values that escape, services - rules A3-A7 | [v3](Research/Memory/FSMA/images/Fusion%20Structured%20Memory%20Architecture%20v3%20Complex%20to%20fix.svg) |
| Hierarchy, Register-Only | where data lives on the hardware; machines with little or no memory (section 8) | [Hierarchy](Research/Memory/FSMA/images/Fusion%20Structured%20Memory%20Architecture%20Hierarchy.svg), [Register-Only](Research/Memory/FSMA/images/Fusion%20Structured%20Memory%20Architecture%20Register-Only.svg) |
| v4 (2026-11-27) | the new kinds proposed in section 7 | [v4](Research/Memory/FSMA/images/fusion_structured_memory_architecture_v4.svg) |

## 4. The kinds of Data Stack today

| Kind | Holds | How a block is taken | Released |
|---|---|---|---|
| `<Single>`, form 1 | one frame's objects, any type | bump: the next free bytes | with the frame, as one unit |
| `<Single>`, form 2 | one type (`Car`) with its internals and children | bump | with its owner, as one unit |
| `<Mixed>` | blocks of many uses - a grid, a mini heap | a free slot; freed slots reused, the stack doesn't grow | with its owner |
| `<Scoped: Frame>` | a frame's, loop's or `run` block's objects (Gemini; added as needed) | bump | reset when the frame or loop ends |
| `<General>` | the catch-all: one-time, short-lived, fitting nowhere else | size-class free lists, freed one by one | with the program, or by owner |
| `<String: StringPool>` | each distinct string once, reused | interned | with the program, or by owner |
| `<Type: NamePool>` | a named pool of one type and its children | a slab or slots | per pool |

The difference between Mixed and Scoped: Mixed reuses holes where they are; Scoped never has holes, because everything
in it ends together.

## 5. The rules

Proposals A1-A11 (the full table: [FSMA.md section 3](Research/Memory/FSMA/FSMA.md#3-the-rules)). In short:

- **A1-A2** - ownership stays first; every Data Stack has one owner and ends with it
- **A3-A5** - a longer-lived stack never points into a shorter-lived one; a value that escapes is placed in the longer
  stack from the start (decided when compiling); nothing borrowed from a service outlives the request
- **A6-A7** - a service owns its stacks (only its worker allocates, so no locks); a hot-path service's stacks are made
  at set-up and never grow while it runs
- **A8** - a reused slot is reached through a handle (stack, slot, generation), so an old reference is caught, not
  followed
- **A9-A11** - moving a value to a service moves its page when it lives alone; GC and manual objects live apart; each
  thread and service has its own Memory Manager - nothing global but read-only pools

## 6. A Data Stack made by hand

The compiler makes Data Stacks itself, but a developer may make one too (user, 2026-11-27), choosing how it behaves:

```fusion
DataStack<Customer> customers {
    layout: contiguous           // one block, or pages / slots
    allocation: dynamic          // grows as needed, or fixed at set-up
    growth: automatic            // how it grows
    reclamation: automatic       // released with its owner, or reset / destroyed by hand
}
```

A Data Stack is configurable, so the new kinds in section 7 can be made this way as well. The settings' names are
proposals (FEATURES R11.9).

## 7. New kinds proposed (v4)

Twelve kinds from a ChatGPT review (2026-11-27 - files/Research/Memory/FSMA/DataStructures/); a review with a limited
view (CLAUDE.md Rule 3c). Four exist already; eight are new proposals:

| Kind | Main purpose | Note |
|---|---|---|
| `Single<T>` | one known object type | today's form 2 |
| `Mixed` | several known types | ChatGPT reads Mixed as "many types"; in Fusion it is the grid that reuses holes (section 4) |
| `General` | objects of unpredictable shape | ChatGPT: types known only while running; Fusion's General is the catch-all with free lists |
| `Grid` | independently allocated slots | Fusion's Mixed already is this - one of the two names goes |
| `Temporal` | lifetime by time - expiry, sessions, caches | `DataStack<Temporal> { defaultLifetime: 10.minutes }` |
| `Versioned` | earlier versions of an object kept | history, undo, audit |
| `Shared` | controlled access by several services | with Task 42's services |
| `Stream` | continuous data, several readers | a ring of chunks |
| `Indexed` | objects found by a field, kept up to date | an index beside the stack |
| `Transactional` | several changes made together or not at all | commit / roll back |
| `Spatial` | search by position | R-tree / KD-tree |
| `Compressed` | less memory for data read rarely | packed, unpacked when read |

ChatGPT's own advice, which fits section 2: treat these as **capabilities of one Data Stack** (an index, an expiry, a
version history, a sharing policy) rather than twelve separate memory designs - most combine an allocator with
metadata and an access policy.

## 8. Machines with little memory

| Profile | Memory | Data Stacks become |
|---|---|---|
| FULL | stack, heap, Data Stacks | as above |
| STATIC | fixed RAM, no heap | static regions, sized when compiling |
| REGISTER-ONLY | registers and ROM | values in registers; no Data Stacks |

Chosen by the target, with `[stdlib] layer` and HIDL (Task 41); memory tiers by machine size: R11.8.

## 9. What is still open

- How the compiler picks a kind - by type, by owner, by a word in the code or by a setting
- Growing a stack: chained pages (references stay valid) or copying
- Fragmentation in Mixed and the named pools; compaction never (it would break C pointers)
- What a handle check costs in the generated C
- Which of the twelve kinds to take, and as kinds or as capabilities (R11.9)
- Measured against today's counting (benchmarks, L16.0)
- Prior work: Goose's data stacks, Zig's allocators, Rust's arenas, Erlang's per-process heaps, mimalloc

## 10. Files

| File | What it holds |
|---|---|
| [Research/Memory/FSMA/FSMA.md](Research/Memory/FSMA/FSMA.md) | The working abstract: every rule and setting proposed |
| [MemoryAllocation.md](Research/Memory/FSMA/MemoryAllocation.md) | A primer on memory models |
| [MemoryAllocationNew.md](Research/Memory/FSMA/MemoryAllocationNew.md) | The first sketch |
| [Gemini_FSMA_Review.md](Research/Memory/FSMA/Gemini_FSMA_Review.md) | Gemini's review and v3 |
| [MemoryTiers_Gemini.md](Research/Memory/FSMA/MemoryTiers_Gemini.md) | Memory by machine size |
| [DataStructures/](Research/Memory/FSMA/DataStructures/DataStructures_Guide.md) | Data structures across languages; the twelve kinds (section 8) |
| `Research/Memory/FSMA/images/` | The pictures v1-v4, Hierarchy, Register-Only |
