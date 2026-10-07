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
code carries a signature - every module, class, and function records what it uses.** And the
governing principle: **do not trust library authors at all.** Even well-meaning code can leak
memory or be badly optimised, and any library can be compromised. Built out, that becomes
eight mechanisms, each aimed at one of D's failure causes or at the trust problem:

#### 3.1 Capability signatures - explicit, published, and verified (fixes D cause 2)

Every function, class, and module gets a **requires** set - for example
`{heap, gc, unsafe, raw_memory, io, network, threads, devices, exceptions}`. Two properties
matter, and they work together:

- **Explicit and published.** The signatures ship with the library as a manifest, so a
  future importer can see exactly which parts use which features *before* compiling - and
  the project's compiler can warn when part of the project doesn't properly handle
  something a library needs. A library will often mix strategies, and that's expected:
  a performance-critical routine may use direct memory access while the rest of the
  library uses automatic memory management. The signature records that per function.
- **Never trusted, always verified.** The compiler computes every signature itself,
  transitively from the call graph (if `f` calls `g` and `g` allocates, `f` requires
  `heap`), and rejects any library whose published manifest doesn't match. An author's
  claim is a convenience for readers, never a basis for trust. D relied on authors
  annotating their own code, and that failed. (For closed libraries, where the source
  can't be re-derived, see section 5.)

The signatures live in the module's interface (Task 18.4 should record them from day one)
and later in the Symbol-ID index (FutureFeatures.md, Compiler Infrastructure).

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

#### 3.8 Project restrictions, enforced across everything (Ada-style)

The project can declare restrictions that apply to **all** code in the program - its own code
and every imported library alike:

```toml
# fusion.toml (or fusion.yaml / fusion.json / fusion.ini - all interchangeable, Task 20)
[restrictions]
no_unsafe = true
no_network = true
no_heap = false
max_stack = "64KB"
```

This is modeled directly on Ada's `pragma Restrictions` and `pragma Profile` (e.g. the
Ravenscar profile for safety-critical real-time systems), where the compiler and binder
enforce that every unit in a program stays within declared restrictions. Combined with
3.1's verified signatures, a violation is reported with the exact library function and call
chain responsible. Tracked as Task 19.2.

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

## 4. Memory Strategy Selection Guide

Fusion expects programs - and libraries - to **mix memory strategies**, choosing the right
one per function or per data structure. Every choice shows up in that code's capability
signature (section 3.1), so importers always know which strategy each part uses.

**Rule of thumb - start at the top and only move down when you have a reason:**

| Strategy | Best for | Avoid when | Typical examples |
|---|---|---|---|
| **Stack / value types** | Small, fixed-size data that lives inside one block or function. Fastest possible; freed automatically when the block ends (block scoping, Task 12.6) | Data is large (stack overflow risk) or must outlive the function | Loop counters, math temporaries, small structs, fixed arrays |
| **Static / fixed memory** | Data allocated once at startup that lives for the whole program; sizes known at compile time | Size varies at runtime | Lookup tables, constants, embedded firmware buffers, no-heap devices |
| **Automatic (GC) - the default** | Application code where productivity matters more than predictable timing: complex object graphs, business logic, UI, prototypes | Hard real-time, kernels, no-heap embedded devices, latency-critical hot paths (collection pauses) | Business apps, tools, most of "Application Fusion" |
| **`Unique<T>`** (single owner, move-only) | A resource with exactly one clear owner and a known cleanup point (deterministic destruction); zero overhead | The data genuinely needs several owners | File handles, sockets, buffers passed down a pipeline, builders |
| **`Shared<T>`** (atomic refcount) | Data held by many parts of the program with no single owner, including across threads | Cyclic structures (they leak - break cycles with `Weak<T>`); hot loops where refcount updates cost - pass a reference instead | Caches, configuration, textures and other assets |
| **`Weak<T>`** (non-owning) | Back-references and observers that must not keep their target alive; breaking `Shared<T>` cycles | You need the target guaranteed alive - use `Shared<T>` | Child-to-parent links, event listeners, caches that shouldn't pin memory |
| **Arena / region** (future) | Many allocations that all die together - freed in one step, very fast | Long-lived objects with varied lifetimes | A compiler pass's AST, one web request's buffers, one game frame's temporaries - **and a sandboxed library's memory** (section 5.2) |
| **Memory-mapped resources** (future) | Very large files or datasets read in parts; the OS loads only the pages actually touched | Small data (overhead isn't worth it) | Multi-GB assets, datasets, logs |
| **Raw / unsafe pointers** | Hardware access and the innermost performance-critical routines, **after profiling proves it's needed** | Everywhere else | Device drivers, memory-mapped I/O, DMA, custom allocators, C interop |

**Rules for raw/unsafe memory:**
- Always wrapped behind a safe interface - callers never touch the raw pointer
- Every explicit allocation must have a matching deallocation. In sandboxed code, anything
  the library fails to free is reclaimed by the host (section 5.2)
- Marked with a `###<NNNN>` design-rule reference explaining *why* it's needed
  (FutureFeatures.md, Unsafe Mode Enhancements)
- Shows up as `unsafe`/`raw_memory` in the capability signature, so project restrictions
  (section 3.8) can forbid it outright

---

## 5. Library Trust, Isolation & Security

**Principle: never trust code - do not trust library authors at all.** Not because authors
are assumed malicious - most aren't - but because even well-meaning code can leak memory or
be badly optimised, and any library can be compromised without its author knowing. Fusion
should treat every imported library as code that must earn trust through verification,
isolation, or both. Tracked as **Task 19**.

**The realistic goal:** no defense is ever airtight against a determined attacker, and
importing code always carries some risk. The aim is to make attacks as hard and as unlikely
as possible, with several independent layers (verified signatures, restrictions,
sandboxing, supply-chain checks, source checks), so that getting past one layer still
leaves the others.

### 5.1 Closed, compiled, and licensed libraries

Not every library will be open source. Some will be compiled-only, commercial, or licensed
with restrictions on how they may be used. Their signatures can't be re-derived from source
(section 3.1), so they need another basis for trust:

- **Signed manifests** produced by the library's build, plus reproducible builds where
  possible, so anyone can confirm the binary matches what was claimed
- An option to ship as **verifiable IR** instead of machine code: the consumer's compiler
  can still check capabilities and apply the project's strategy without seeing source. The
  tradeoff is that IR is easier to decompile (the same problem Java bytecode has)
- **Anything that can't be verified is sandboxed by default** (5.2)
- **Licence metadata** in the manifest (terms, permitted use), with a compiler check for
  conflicts with the project's own licence

### 5.2 Sandboxing with resource budgets

A library can run isolated from the main application, receiving only what it declares it
needs: **X RAM, CPU/GPU time, and specific devices or drivers** - for example, a hardware
driver or a specialised function the application depends on. Nothing more.

- **Per-library memory regions.** A sandboxed library allocates only from a memory region the
  host application owns. The library is expected to free what it allocates; whatever it
  leaks - through a bug or deliberately - the host reclaims when the region is torn down.
  A bad library cannot leak memory into the main application.
- **Raw and unsafe allocation must be wrapped**, so the host always knows what was allocated
  and can account for it.
- **Profiling.** Because all of a sandboxed library's resource use flows through the host, it
  can be measured against the declared budget: how much memory, CPU/GPU, and I/O the library
  actually uses, and where.
- **Isolation levels, chosen per library by the project:**

| Level | Protects against | Cost |
|---|---|---|
| None - compiled inline | Nothing beyond signatures and restrictions; for fully trusted code | Free |
| Memory region | Leaks and memory bugs | Low |
| Separate process | Actively malicious code | Highest - every call crosses a process boundary |

**Honest caution:** no isolation level is airtight against deliberate attacks - the goal is
to make them as unlikely as possible. In-process sandboxing protects well against *bugs*, but
Java's applet history shows how hard it is to defend against *deliberate* attacks - JVM
sandbox escapes were a common exploit class for years. Code that might be actively malicious
belongs in a separate process, which is a much stronger (though still not perfect) barrier.

**Prior art:** WebAssembly's component model (each module gets its own memory and explicit
imports), Deno's permission flags, Ada's restrictions.

### 5.3 Supply-chain security

Compromised repositories and packages that inject backdoors into applications are a real,
recurring problem - the xz-utils backdoor (2024), the event-stream npm compromise (2018), and
more recent package and repository compromises. Defenses:

- **Lockfile pinning** - every dependency at an exact version **and content hash**, so a
  tampered package fails to install
- **Signed packages** (e.g. Sigstore-style) and **reproducible builds**
- **No arbitrary code execution at install or build time** - npm `postinstall` scripts and
  build scripts are major attack vectors. Any compile-time code execution must itself be
  sandboxed
- **Capability-diff alerts on every update** - "v2.4 now requires `network`; v2.3 didn't."
  A compromised update usually needs a capability its library never used before, so
  verified signatures (3.1) make many injected backdoors visible at upgrade time
- **SBOM output** (software bill of materials) - a complete record of what's inside a build

### 5.4 Source-level attacks, including attacks aimed at AI assistants

**Status: the first two attacks below are now blocked (Task 19.6, complete 2026-10-07).**
Before that, both worked against Fusion: a file with two different variables that looked
identical (`аge` with a Cyrillic `а`, and `age`) compiled cleanly, as did a right-to-left
override character hidden in a comment and a string. See "Source Text Rules" in
`files/fusion-language-spec.md`.

- **Trojan Source (CVE-2021-42574):** invisible bidirectional-control Unicode characters make
  code *display* differently from how it *compiles* - a reviewer reads one thing, the
  compiler builds another. Fusion's lexer should reject these characters in source,
  including inside comments and strings, with a `\u` escape as the visible way to include
  one on purpose
- **Confusable identifiers:** look-alike characters from different scripts (e.g. Cyrillic
  `а` vs Latin `a`). Recommended defense: ASCII-only identifiers by default, with an opt-in
  for projects that want non-English identifiers (where mixed-script names are rejected)
- **Content aimed at AI tools:** instructions hidden in text or code, written to manipulate
  AI models like Claude or ChatGPT (prompt injection). In Fusion this belongs in the future
  **`fusionlib.AI` module**: before that module passes any text to an AI model, it parses the
  text and checks it for embedded code and hidden instructions. Logged now (Task 19.7, far
  future) because attacks on AI tools are a real and growing risk - including against the AI
  helping build Fusion - and the requirement should shape that module from its first design.
  Detection is heuristic and never a guarantee; the model must still treat the text as data,
  not instructions

The first two checks are implemented (Task 19.6); the AI input guard waits for
`fusionlib.AI` (Task 19.7).

---

## 6. Recommendation - Build the Core First (Task 18)

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

## 7. Languages With Overlapping Goals

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
