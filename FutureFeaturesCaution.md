# Future Features - Cautions & Review

**Read this before picking up anything from `FutureFeatures.md`.**

**Created:** 2026-10-07, from a project review by Claude (Opus 5.5) requested by the user
**Companion to:** `FutureFeatures.md` (what Fusion *could* become) and `taskSummary2.md`
(what is actually being built)

---

## The Guiding Rule

> **The first goal is a simple working language. Complex features come after.**

`FutureFeatures.md` is a menu of possibilities, not a list of commitments. Some features in
it will be built, some will change shape, and some will never be added. Nothing there should
be started while the core language is still missing the basics every program needs. That
core work is tracked as **Task 18 (Core Language Foundation)** in `taskSummary2.md`.

---

## 1. What's Strong

- **The process.** Plan-first, ADR-style decisions, ~1,100 tests, and status tracking that's
  honest about the difference between *decided*, *built*, and *wished for*. That's rarer than
  it should be in hobby compilers, and especially in AI-assisted ones.
- **Several decisions were genuinely good engineering, not just reasonable:**
  - building the Typed AST *before* arrays (Task 12 before Task 9)
  - checking scoping behavior against real GCC instead of assuming it (Task 12.6)
  - deferring the IR layer until there's a second backend to design it against (Task 12.10)
  - TOML for project configuration (Task 12.12)
  - mapping `decimal`/`Currency` onto COBOL's `PIC 9(9)V99`
- **A few ideas are actually distinctive.** "Stable meaning, configurable implementation
  strategy" is a good one-line thesis. The most interesting long-term idea is source stored
  in one canonical form, with each developer seeing it rendered in their preferred block
  style - that turns "three syntaxes" from a parsing curiosity into a real tooling advantage.

---

## 2. Cautions

### Caution 1 - The documented vision far outweighs the implemented core

`FutureFeatures.md` is ~5,800 lines. As of 2026-10-07 the compiler:
- compiles one file at a time
- has no `import`
- has no structs or classes
- can't pass an array to a function
- emits a placeholder comment instead of real code for lambdas
- has no string operations (no concatenation, length, or content comparison)

The vision runs from kernels to clusters, with every OOP model, every memory model, 21+
stdlib modules, four backends, and HIDL. The danger isn't that the vision is wrong. It's that
planning quietly becomes the product. Almost every open task is blocked on the same few
core features - which is why Task 18 exists.

### Caution 2 - "Every feature, all combinable" is the hardest target in language history

Configurability helps *users*. It doesn't help the compiler author, who has to make every
combination work correctly. Feature interactions grow combinatorially.

- **PL/I** is the classic cautionary tale, and it's oddly on-theme for Fusion: it tried to
  unify COBOL's business features, FORTRAN's scientific ones, and systems programming. It
  became enormous and notoriously hard to implement.
- **C++** is the modern version of the same story.

**Mitigation:** add features one at a time, each fully finished (tests, example, docs)
before the next, and test the named profiles rather than every possible combination.

### Caution 3 - Ecosystem fragmentation is the hardest unsolved problem

If project A uses a no-GC Embedded profile and project B uses the managed Application
profile, can A use a library B wrote? If not, the ecosystem splits into incompatible
dialects. See section 3 for the proposed answer.

### Caution 4 - No beachhead yet

Successful languages usually win one niche first: Rust took memory-safe systems code, Go
took network services, Zig is taking "better C plus toolchain." "Choose your own tradeoffs"
is a meta-feature, not a use case.

The `decimal`/`Currency`/COBOL thread is a plausible niche. COBOL modernization is a real,
underserved market, and exact-decimal correctness is a concrete, demonstrable selling point.

---

## 3. Ecosystem Fragmentation - Where D Failed, and a Proposed Answer

### Why D failed

D made its garbage collector optional (`@nogc`, `-betterC`), but the ecosystem split anyway.
The root causes, in order of importance:

1. **The standard library was built GC-first.** Phobos (D's stdlib) assumed a GC
   everywhere. Making the GC optional *afterwards* meant most of the stdlib was unusable
   from no-GC code.
2. **Requirements were implicit.** Whether a function used the GC wasn't tracked unless the
   author annotated it - and D only inferred these attributes automatically for templates,
   not ordinary functions. Library authors rarely annotated, so no-GC users couldn't tell
   what was safe to call.
3. **The opt-out came after the ecosystem existed.** The default was "uses GC," and
   retrofitting discipline onto existing code never happens at scale.
4. **Coarse granularity.** Compatibility was effectively all-or-nothing per library, even
   when most of a library's functions didn't need the GC at all.
5. **Binary distribution fixed the strategy.** A compiled library had its memory strategy
   baked in at its own compile time, not the consumer's.

### The proposed Fusion answer

The user's starting point (2026-10-07): **the project overrides imported code, and imported
code carries a signature - every module, class, and function records what it uses.** Built
out, that becomes seven mechanisms, each aimed at one of D's failure causes:

#### 3.1 Capability signatures, inferred automatically (fixes D cause 2)

Every function, class, and module gets a computed **requires** set - for example
`{heap, exceptions, threads, io, unsafe, float, reflection}`. The compiler computes it
transitively from the call graph: if `f` calls `g` and `g` allocates, `f` requires `heap`.

**Inference must be automatic for all code**, not opt-in annotation. D's annotations
depended on library-author discipline and failed for exactly that reason. The signatures
live in the module's interface (Task 18.4 should record them from day one) and later in the
Symbol-ID index (FutureFeatures.md, Compiler Infrastructure).

```text
module TextUtils
  function trim(string) -> string           requires { heap }
  function startsWith(string, string) -> bool  requires { }        <- usable anywhere
  function readLines(path) -> list          requires { heap, io }
```

#### 3.2 Depend on meaning, not mechanism - this is where "the project overrides imported code" happens

Separate **semantic** requirements from **strategy** choices:
- *Semantic:* "this function needs heap allocation." The library genuinely needs it.
- *Strategy:* "allocation goes through a GC / an arena / refcounting." That's the
  project's choice, not the library's.

Libraries record only semantic requirements. **The importing project supplies the
strategy**, and imported code is compiled under it. The same library can then run under
different memory strategies in different projects without being rewritten. This is
Fusion's own thesis - stable meaning, configurable implementation - applied to libraries.

#### 3.3 Distribute libraries as source or semantic IR, not strategy-fixed binaries (fixes D cause 5)

For the project to override imported code, the imported code has to be compiled by the
consumer. Libraries ship as source (as Rust crates, Zig packages, and Nim modules already
do), or later as a semantic IR. Prebuilt binaries can still exist as an optimization, one
variant per common profile.

#### 3.4 Function-level compatibility checking (fixes D cause 4)

At import, the compiler compares each imported symbol's signature against the project's
enabled capabilities. The check is **per function, not per library**:
- Fully compatible symbols compile normally under the project's strategy.
- Incompatible symbols are still importable, but calling one is a compile error naming
  the exact reason.

So a no-heap embedded project can still use the 80% of a string library that never
allocates. Example diagnostic:

```text
error: TextUtils.trim requires capability 'heap'
       (trim -> buildResult -> List.add allocates)
       project profile 'embedded' disables 'heap'
note:  TextUtils.startsWith has no requirements and can be used
```

#### 3.5 Explicit project override policies for gaps that can't be bridged

Some requirements can't be satisfied by any strategy - for example, a library that throws
exceptions, used in a project with exceptions disabled. The project may declare an
explicit mapping policy in `fusion.toml`:

```toml
[imports.policy]
exceptions = "abort"    # imported code that throws terminates with a clear message
```

The rule: **never silent.** A mapping that changes behavior (like turning a throw into an
abort) must be written down by the developer - it is never inferred or applied by default.

#### 3.6 Layer the standard library from day one (fixes D cause 1 - the most important one)

Build the stdlib bottom-up, the way Rust's `core` / `alloc` / `std` layering already
proves works:
- **core** - no heap, no GC, no exceptions, no OS. Usable on bare metal.
- **alloc** - adds heap allocation (collections, growable strings).
- **std** - adds OS services (files, threads, networking).

Because the lowest layer is written to the tightest profile first, the default ecosystem
naturally fits restrictive profiles, instead of being retrofitted later. **This must be
decided when the first stdlib is written** (Task 18.5) - it's nearly impossible to fix
afterwards, as D shows.

#### 3.7 Library-declared ceilings, enforced by the compiler (fixes D cause 3)

A library may declare a capability budget in its manifest - "this library stays within
`{heap}`." The compiler checks that the inferred signatures never exceed it, so CI catches
the regression the moment someone accidentally adds a file read or a throw to a library
that promised not to need them. This prevents the slow creep that eroded D's no-GC story.

### Honest limits

- Not every library will work in every project. A library that fundamentally needs heap
  allocation can't run on a no-heap device, and no design changes that. The goal is that
  incompatibility is **precise, detected at compile time, at function granularity, with a
  clear reason** - and that the default ecosystem is built so most libraries fit tight
  profiles naturally.
- Automatic inference has a compile-time cost on large projects. The Symbol-ID index's
  incremental analysis (FutureFeatures.md) is what keeps that tractable.

### Prior art worth studying for this specifically

- **Ada** - `pragma Restrictions` and `pragma Profile` (e.g. Ravenscar): the compiler and
  binder enforce that every unit in a program, libraries included, stays within declared
  restrictions. The closest existing industrial version of this whole design.
- **Rust** - `core`/`alloc`/`std` layering; auto traits (`Send`/`Sync`) as automatically
  inferred, compiler-checked properties; editions, which let crates on different language
  versions interoperate.
- **Koka** - effect inference: functions' side effects are inferred and tracked in their
  types automatically.
- **D** - the cautionary example: attribute inference existed, but only for templates.

---

## 4. Recommendation - Build the Core First (Task 18)

Pause growing the vision documents for a while, and build the core every profile needs:

1. **Functions with full parameter types** - default values (currently broken at call
   sites), arrays as parameters/returns, real lambda codegen. Functions are the unit of all
   reusable code.
2. **Structs** - the first user-defined type; maps directly onto a C `struct`, so it needs no
   runtime and no decision yet on how classes/interfaces/traits interact. Prerequisite for
   classes, Currency, HIDL, and a self-hosted compiler.
3. **Proper strings** - concatenation, length, content comparison (string `==` currently
   compares C pointers), substring, number conversion. A self-hosted lexer is built on these.
4. **`import` and multi-file projects** - the single biggest unblocker. Every stdlib module
   and every proposed feature module depends on it.
5. **A minimal, layered stdlib** - console/file IO, a growable list/map, CLI arguments.
   Layered core/alloc/std from the start (section 3.6).

That unblocks roughly 80% of the open task list in one stretch, and it's the same list
Task 10.2 already names as self-hosting prerequisites.

---

## 5. Languages With Overlapping Goals

No single language matches Fusion's whole vision, but most of its individual ideas have
serious prior art:

| Language | Overlap with Fusion | Lesson |
|---|---|---|
| **Nim** | Probably the closest technically: compiles to C, memory model chosen per build (`--mm:arc/orc/none`), Python-like indentation syntax | Proof that "compile to C, configurable memory model" works; study it closely |
| **Ada** | **Profiles** that restrict a feature set per program (e.g. Ravenscar for safety-critical real-time), plus built-in decimal fixed-point types | Fusion's feature-registry-with-profiles idea and `decimal(p,s)` both exist here, industrial-grade, for decades |
| **D** | Systems to applications, multi-paradigm, GC optional (`@nogc`, `-betterC`) | The cautionary tale for optional features fragmenting an ecosystem (section 3) |
| **Racket** | `#lang`: each file picks its own language dialect, and they all interoperate on one runtime | The best existing answer to "per-project language, shared ecosystem" |
| **Mojo** | Python-style syntax that escalates to systems control (`def` vs. `fn`, opt-in ownership) | Closest to "easy by default, never a dead end" |
| **Rust** | Contained `unsafe` blocks; editions let crates on different language versions interoperate | Editions are a proven model for configuration that *doesn't* fragment an ecosystem |
| **Zig** | Allocators passed explicitly as parameters; strong C interop | "Configurable memory strategy" done at library level, without language dialects |
| **Swift** | ARC with strong/weak/unowned references, plus a restricted Embedded Swift mode | Very close to the `Unique`/`Shared`/`Weak` decision in Task 12.7 |
| **ReasonML / OCaml** | An alternate surface syntax over the same compiler and AST | Precedent for "one language, multiple syntaxes" |
| **Haxe** | One language, many targets (C++, JS, C#, a VM) | The multi-backend angle in practice |

**If you study only three:** **Nim** for how to build it, **Ada** for profiles and decimal
types, and **D** for what to avoid.
