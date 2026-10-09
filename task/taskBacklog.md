# Fusion Task Backlog

Write-ups for tasks that are **not started yet** (or not yet active), moved
verbatim from `taskSummary2.md` on 2026-10-09 (Task 22). Status lives in
`FEATURES.md`; when a task becomes active, its section moves back to
`taskSummary2.md` with a detailed plan (Rule 1). Find a task with
`grep -n "^## TASK 13" task/taskBacklog.md`.

---
## TASK 10: Self-Hosting - Rewrite Compiler in Fusion

**Goal:** Rewrite the Fusion compiler in Fusion itself
**Status:** Planning Complete
**Priority:** HIGH (Critical milestone)
**Blocked By:** Tasks 5-9 (core language features needed)
**Estimated Effort:** 40-60 hours
**Plan:** See task/task-10-self-hosting-plan.md

### Overview

Self-hosting means rewriting the Python compiler in Fusion. This proves:
1. Fusion is powerful enough for complex software
2. The language is mature and feature-complete
3. The compiler can maintain itself going forward

**Bootstrap Process:**
```
Python Compiler (v1) → Compiles Fusion Compiler (v2) → Fusion Compiler compiles itself (v3)
```

Verification: v2 and v3 must produce identical output.

### Sub-tasks:

#### 10.1: Prerequisites Analysis & Planning (2-3 hours)
- [x] Create comprehensive planning document
- [ ] Analyze Python codebase dependencies
- [ ] Map Python features to Fusion equivalents
- [ ] Identify missing Fusion features (file I/O, collections, etc.)
- [ ] Document required fusionlib modules
- [ ] Design Fusion compiler architecture
- [ ] Get user approval for approach

#### 10.2: Implement Missing Language Features (8-12 hours)
- [ ] Add file I/O support
- [ ] Add collection support (List, Dictionary)
- [ ] Add string manipulation helpers
- [ ] Add command-line argument parsing
- [ ] Test all new features

#### 10.3: Port Lexer to Fusion (6-8 hours)
- [ ] Port token.py → token.fusion
- [ ] Port lexer.py → lexer.fusion
- [ ] Port literals.py → literals.fusion
- [ ] Port keywords.py → keywords.fusion
- [ ] Write tests, verify output matches Python lexer

#### 10.4: Port Parser to Fusion (8-10 hours)
- [ ] Port ast_nodes.py → ast_nodes.fusion
- [ ] Port parser.py → parser.fusion
- [ ] Write tests, verify AST matches Python parser

#### 10.5: Port Semantic Analyzer to Fusion (6-8 hours)
- [ ] Port symbol_table.py → symbol_table.fusion
- [ ] Port name_resolver.py → name_resolver.fusion
- [ ] Port type_checker.py → type_checker.fusion
- [ ] Write tests, verify semantic checks match Python

#### 10.6: Port Code Generator to Fusion (6-8 hours)
- [ ] Port c_generator.py → c_generator.fusion
- [ ] Port compiler.py → compiler.fusion
- [ ] Write tests, verify generated C code matches

#### 10.7: Port Main Entry Point (1-2 hours)
- [ ] Port main.py → main.fusion
- [ ] Add command-line argument parsing
- [ ] Test compilation pipeline

#### 10.8: First Bootstrap - Python Compiles Fusion Compiler (2-3 hours)
- [ ] Use Python compiler to compile main.fusion
- [ ] Generate fusion_compiler.exe
- [ ] Test: Does fusion_compiler.exe work?
- [ ] Verify: Compile hello_world.fusion using fusion_compiler.exe

#### 10.9: Second Bootstrap - Fusion Compiles Itself (2-3 hours)
- [ ] Use fusion_compiler.exe (v2) to compile main.fusion
- [ ] Generate fusion_compiler_v3.exe
- [ ] Verify: v2 and v3 produce identical output

#### 10.10: Full Test Suite Verification (2-3 hours)
- [ ] Run all 1,041 tests using fusion_compiler.exe
- [ ] Verify all tests pass
- [ ] Compare outputs with Python compiler
- [ ] Fix any discrepancies

#### 10.11: Performance & Optimization (2-4 hours)
- [ ] Benchmark fusion_compiler.exe vs Python compiler
- [ ] Identify performance bottlenecks
- [ ] Optimize critical paths
- [ ] Document performance metrics

#### 10.12: Documentation & Finalization (2-3 hours)
- [ ] Update README.md with self-hosting info
- [ ] Document bootstrap process
- [ ] Update CLAUDE.md
- [ ] Git commit and tag version

**Success Criteria:**
- Fusion compiler compiles itself successfully
- v2 and v3 produce identical output (bit-for-bit)
- All 1,041 tests pass using Fusion compiler
- Performance acceptable (within 2-3x of Python)

**Deliverables:**
- Fusion compiler written in Fusion
- Bootstrap verification
- Performance benchmarks
- Updated documentation

---

## TASK 11: LLVM Backend Integration

**Goal:** Replace C code generator with LLVM IR backend
**Status:** Planning Complete
**Priority:** MEDIUM (Enhancement)
**Blocked By:** Task 10 (Self-Hosting should complete first)
**Estimated Effort:** 30-40 hours
**Plan:** See task/task-11-llvm-backend-plan.md

### Overview

**Current:** `Fusion → C code → GCC → Native executable`
**After LLVM:** `Fusion → LLVM IR → Native executable`

**Benefits:**
1. No C intermediate - Direct to machine code
2. Cross-platform - LLVM targets 30+ architectures
3. Better optimization - LLVM's world-class optimizer
4. Faster compilation - No GCC invocation overhead
5. Advanced features - JIT compilation, link-time optimization

### Sub-tasks:

#### 11.1: Research & Design (4-6 hours)
- [x] Create comprehensive planning document
- [ ] Study LLVM architecture and IR format
- [ ] Choose binding library (llvmlite recommended)
- [ ] Design Fusion → LLVM type mapping
- [ ] Design function calling convention
- [ ] Plan memory management strategy
- [ ] Get user approval

#### 11.2: Setup LLVM Environment (2-3 hours)
- [ ] Install LLVM toolkit
- [ ] Install llvmlite Python bindings
- [ ] Verify LLVM installation
- [ ] Create test LLVM IR program
- [ ] Compile test program to verify toolchain

#### 11.3: Create LLVM IR Generator Skeleton (2-3 hours)
- [ ] Create src/codegen/llvm_generator.py
- [ ] Implement basic module/function structure
- [ ] Add type mapping system
- [ ] Test: Generate simple "Hello World" LLVM IR

#### 11.4: Implement Type System (3-4 hours)
- [ ] Map Fusion int → LLVM i32
- [ ] Map Fusion float → LLVM float
- [ ] Map Fusion bool → LLVM i1
- [ ] Map Fusion string → LLVM i8*
- [ ] Test type conversions

#### 11.5: Implement Function Generation (4-5 hours)
- [ ] Generate function declarations
- [ ] Generate function bodies
- [ ] Handle parameters and return values
- [ ] Test: factorial.fusion → LLVM IR

#### 11.6: Implement Expression Codegen (5-6 hours)
- [ ] Arithmetic operations (+, -, *, /)
- [ ] Comparison operations (<, >, ==, !=)
- [ ] Logical operations (and, or, not)
- [ ] Function calls
- [ ] Test all operators

#### 11.7: Implement Statement Codegen (4-5 hours)
- [ ] Variable declarations and assignments
- [ ] If/else statements (using basic blocks)
- [ ] While loops (using basic blocks + PHI nodes)
- [ ] For loops
- [ ] Return statements

#### 11.8: Implement String Handling (3-4 hours)
- [ ] String literals → global constants
- [ ] String interpolation → sprintf calls
- [ ] printf calls for output
- [ ] Test: hello_world.fusion, fizzbuzz.fusion

#### 11.9: Implement Standard Library Calls (2-3 hours)
- [ ] Link with C standard library
- [ ] Map printf, scanf, etc.
- [ ] Test I/O operations

#### 11.10: Optimization Pipeline (2-3 hours)
- [ ] Add LLVM optimization passes
- [ ] Support -O0, -O1, -O2, -O3 levels
- [ ] Test optimization effects
- [ ] Benchmark performance

#### 11.11: Integration Testing (3-4 hours)
- [ ] Compile all 6 examples using LLVM backend
- [ ] Verify outputs match C backend
- [ ] Run all 150 codegen tests
- [ ] Fix any discrepancies

#### 11.12: Performance Benchmarking (2-3 hours)
- [ ] Compare LLVM vs C backend compilation time
- [ ] Compare generated code performance
- [ ] Measure executable sizes
- [ ] Document results

#### 11.13: Documentation & Finalization (2-3 hours)
- [ ] Add --backend flag: --backend=c or --backend=llvm
- [ ] Update README.md
- [ ] Update CLAUDE.md
- [ ] Git commit

**Success Criteria:**
- LLVM backend generates working executables
- All examples compile and run correctly
- Performance equal to or better than C backend
- All tests pass

**Deliverables:**
- LLVM IR code generator
- Backend selection option
- Performance benchmarks
- Updated documentation

---

## TASK 13: HIDL Module (Hardware Interface Definition Language integration)

**Important scope correction (2026-09-13):** HIDL itself is **not a Fusion feature**. It is a
standalone, language-agnostic hardware-description framework - independent of Fusion, useful to
any language's toolchain (C, C++, Rust, C#, Java, etc. per the source doc's own Section 19). This
task is specifically about Fusion eventually growing a **HIDL module**: a consumer that reads a
separately-specified `.hidl` file and generates typed Fusion bindings from it. Building HIDL
itself (its grammar, parser, validation) is a separate, standalone effort that does not require
Fusion to exist first - only the Fusion-side *consumer* belongs on this compiler's roadmap.

**Goal:** Add a Fusion module that consumes a HIDL hardware spec (registers, bits, commands,
ranges, timing, constraints) and generates a safe, typed Fusion hardware API from it - eventually
letting Fusion code talk directly to registers/assembly without hand-translating a hardware
manual per project.
**Status:** Blocked / Future (vision doc only - confirmed by user 2026-09-13, not yet scoped
to a v1 implementation). **Unblocked as of 2026-09-13** - Task 12 (all 12 sub-tasks) is now
complete; this task still needs its own scoping approval before implementation begins, per
Rule 1.
**Priority:** LOW (future/eventual - explicitly no urgency)
**Blocked By:** ~~Task 12~~ - COMPLETE (2026-09-13). Compile-time hardware range and
state-requirement checks (source doc sections 13, 21) need the `inferred_type` machinery
Task 12 delivered (12.1-12.4, 12.9), or this repeats the "codegen guesses" problem at the
hardware layer.
**Estimated Effort:** TBD - needs its own sub-plan once approved for scoping
**Source:** `files/Fusion_Hardware_Interface_Definition_Language_HIDL.md` (moved from repo root
2026-09-13, committed to the repo as an important reference doc; original vision doc, 43
sections, XML examples are illustrative only per its own section 6; carries a 2026-09-13 scope
note at the top clarifying HIDL's independence from Fusion). Reviewed by Claude same session -
see Session 22 notes below for full review.

### Why this task exists

Custom hardware normally forces every programmer to manually turn a hardware manual into
register addresses, bitmasks, enums, structs, and driver code per language - repetitive,
error-prone, and impossible to keep in sync across C/C#/Rust/etc SDKs for the same chip. HIDL's
idea is to make the hardware description itself the authoritative artifact: one spec, consumed
by tooling (any language's tooling, not just Fusion's), generating typed properties/functions/
interfaces (and eventually drivers, docs, and a simulator) instead of raw register pokes. Fusion
is one prospective consumer among several. The source doc also proposes a clean three-way split
that fits Fusion's existing design direction for its own module: **HIDL** = hardware truth,
**Interface** = promised contract, **Trait** = reusable behavior on top.

### Sub-tasks (NOT YET APPROVED - proposed breakdown only, for future scoping)

#### 13.1: Grammar & Format Decision
- [ ] Evaluate reusing an existing standard (ARM CMSIS-SVD, IP-XACT, Zephyr devicetree) vs.
      a new, standalone, language-agnostic HIDL format (not a Fusion-specific format - HIDL is
      independent of Fusion, see scope correction above)
- [ ] If new format: write a formal HIDL grammar (e.g. `files/hidl.ebnf`) as its own spec,
      independent of `fusion.ebnf`, using it only as a formatting reference
- [ ] Decide serialization (source doc's XML in section 6 is explicitly illustrative, not final)
- [ ] Get user approval on grammar/format before any parser work begins

#### 13.2: Scope v1 vs. Future Layers
- [ ] Split the source doc's Layer 1-6 model (Physical / Hardware / Semantic / Behavioral /
      API / Tooling, section 36) into a minimal v1 scope vs. explicitly deferred layers
- [ ] Recommended v1 scope: registers, bitfields, access modes (R/W/RW/W1C etc.), basic types
      and ranges, simple commands
- [ ] Recommended deferred to later versions: DMA/buffers (section 29), interrupts/events
      (section 28), security/permissions (section 27), simulator generation (section 24), IDE
      integration (section 20) - each is its own multi-week subsystem
- [ ] Document the v1/deferred split so the full 43-section vision isn't mistaken for a v1
      requirements list

#### 13.3: Memory Model Reconciliation (depends on Task 12.7)
- [ ] Resolve how hardware register/device handles interact with the planned `Unique` /
      `Shared` / `Weak` ownership model - not addressed in the source doc
- [ ] Example open question: can two `Unique` handles alias the same physical register; is a
      device handle inherently `Shared`?
- [ ] Get user decision; record alongside Task 12.7's memory model spec (same ADR, not a
      separate one)

#### 13.4: HIDL Parser (standalone, not Fusion compiler internals)
- [ ] Design an internal hardware model matching source doc section 40 (DEVICE -> metadata,
      memory regions, registers -> fields/access rules, types, enums, commands, properties,
      states, constraints, timing, ...)
- [ ] Implement a parser for the chosen format (13.1) - this is HIDL's own parser, usable
      independent of the Fusion compiler; Fusion's compiler only needs to invoke it
- [ ] Implement spec validation (source doc section 26: overlapping addresses, invalid bit
      ranges, field exceeds register size, read-only marked writable, duplicate command values,
      missing hardware version, etc.)

#### 13.5: Fusion Code Generation from HIDL
- [ ] Generate typed Fusion properties/functions/interfaces from the hardware model (source doc
      sections 16-19)
- [ ] Generate enums/types for named register values (e.g. `DoorState`, `PowerMode`)
- [ ] Decide and implement import syntax, e.g. `import hardware "MicrowaveController.hidl"`
      (source doc section 21)

#### 13.6: Compile-Time Hardware Safety Checks
- [ ] Hard dependency on Task 12's Typed AST / `inferred_type` work
- [ ] Enforce declared ranges and state requirements at compile time (source doc sections 13,
      21 - e.g. `microwave.Power = 500` erroring against a declared `0-100` range)

#### 13.7: Multi-Language Code Generation (stretch, after 13.5 proven)
- [ ] Generate C/C++/Rust/C#/Java bindings from the same HIDL source (source doc section 19)
- [ ] Only attempted once the Fusion generation path (13.5) is working and stable

#### 13.8: Simulator & Tooling (stretch, long-term)
- [ ] Auto-generated hardware simulator from the spec (source doc section 24) - lets developers
      test without physical hardware
- [ ] IDE integration: autocomplete, register browser, bit-field editor (source doc section 20)

#### 13.9: Documentation & Examples
- [ ] Example `.hidl` file + generated Fusion API (reuse source doc's microwave-controller
      example, sections 5-6)
- [ ] Update `files/fusion-language-spec.md`, `files/fusion.ebnf`, and README once any part of
      this ships

**Success Criteria (once unblocked and scoped):**
- HIDL format/grammar formally defined and approved (not illustrative pseudocode)
- v1 scope explicitly bounded; deferred layers documented, not silently assumed
- Memory-model interaction resolved before any code generation is implemented
- Generated Fusion API is strongly typed with compile-time range/state validation
- No behavior regressions to existing compiler phases

**Deliverables:**
- HIDL grammar/spec document
- HIDL parser + hardware-model validation
- Fusion code generator consuming the hardware model
- Example hardware definition + generated API
- Memory-model ADR entry covering hardware handles

**Explicitly NOT scheduled now:** this task is future/eventual work only. Task 12 is now
complete, so its blocker is cleared, but no implementation, grammar design, or parser work
should begin until the user re-opens this task for scoping approval.

---

## TASK 14: Nullable Arrays & Safe Navigation

**Goal:** Let arrays (and eventually other reference-like types) be nullable, with
`arr.length`/`arr?.length` and `arr?[i]` behaving safely instead of crashing unpredictably -
the richer null-safety design the user asked for while scoping Task 9, split out because it's
a language-wide feature, not an array-specific one.
**Status:** Not Started (proposed breakdown only, not yet approved for implementation - same
status convention as Tasks 12/13). **Unblocked as of 2026-09-13** - Task 12.7 is now complete;
this task still needs its own scoping approval before implementation begins, per Rule 1.
**Priority:** MEDIUM (no urgency stated)
**Blocked By:** ~~Task 12.7~~ - COMPLETE (2026-09-13). Task 12.7 decided `Weak<T>.lock()`
returns a nullable value that must be checked, which is the same null-handling shape this task
needs for `arr?.length`/`arr?[i]` - the two features should share one null-flow-analysis
design (noted in Task 12.7's own writeup), not two independent ones.
**Estimated Effort:** TBD - needs its own sub-plan once approved for scoping
**Source:** Arose from scoping Task 9 (2026-09-13) - the user asked for `arr.length` with
null-checking, `arr?.length` returning 0 silently on null, and a hybrid null-safety model:
compile-time error where the compiler can prove an array is null before use, a runtime crash
with a clear message where it can't prove it, and `?.`/`?[` as the way to opt out of both (get
0 back instead). The user also noted this might eventually be configurable per-project
(ties to Task 12.12's project configuration system). Notably, `files/fusion-language-spec.md`
already describes this exact design for strings and arrays under "Array Safe Navigation" and
"Null Safety" (e.g. "`string?.length` returns 0 if null") - this task is about actually
building it, starting with arrays.

### Sub-tasks (NOT YET APPROVED - proposed breakdown only)

#### 14.1: Nullability Model Decision
- [ ] Decide whether arrays become a nullable reference type (pointer + length) or whether
      nullability is a separate wrapper/modifier applicable to multiple types
- [ ] Decide how `null` (currently type-checks as `void`, not wired to any real type) becomes
      assignable to nullable array types
- [ ] Resolve alongside Task 12.7's `Unique`/`Shared`/`Weak` design - a nullable array's
      ownership story needs to fit that same model, not a separate one
- [ ] Get user decision; record as an ADR alongside Task 12.7's memory model spec

#### 14.2: Compile-Time Null-Flow Analysis
- [ ] Track definite-null / maybe-null / definite-non-null state through straight-line code
      (at minimum; branch-merging is a further decision)
- [ ] Compile-time error when `.length`/indexing is used on a provably-null array without a
      preceding `?.`/`?[`
- [ ] Write semantic tests for provably-null and provably-safe cases

#### 14.3: `.` / `?.` / `?[` Parser Support
- [ ] Add member-access (`.` identifier) and safe-navigation (`?.` identifier, `?[`
      expression `]`) postfix parsing - doesn't exist in the parser at all today
- [ ] `arr.length` lowers to the same thing `len(arr)` does (both should stay available and
      behave identically per the user's "give devs both, don't lock into one way" request)

#### 14.4: Runtime Null-Check Codegen
- [ ] For accesses that can't be proven safe at compile time: emit a null check that crashes
      with a clear message on null (matches the user's "crash the app with clear error
      message" requirement)
- [ ] For `?.`/`?[` accesses: emit a null check that evaluates to 0 instead of crashing (no
      warning - matches the user's "we don't execute the function and return a 0" description)
- [ ] Regression tests: provably-null (compile error), runtime-null via non-provable path
      (crash with message), `?.`/`?[` on null (0, no crash)

#### 14.5: Extend Beyond Arrays (stretch)
- [ ] `string?.length` is already described in the language spec alongside arrays - evaluate
      applying the same mechanism to strings once arrays prove it out
- [ ] Note for future classes/objects: this mechanism should generalize, not be
      array-specific plumbing

#### 14.6: Documentation & Examples
- [ ] Update `files/fusion-language-spec.md`'s "Array Safe Navigation"/"Null Safety" sections
      from aspirational to actually-implemented, with the real semantics decided above
- [ ] Example program demonstrating `.length` vs `len()` vs `?.length` vs `?[i]`
- [ ] Update `files/fusion.ebnf`'s postfix production (already has the grammar drafted -
      confirm it still matches what got built)

**Success Criteria:**
- Arrays can be null; `null` is assignable to a nullable array type
- `.length` and `len(arr)` both exist and behave identically
- A provably-null `.length`/index access is a compile-time error
- A non-provably-null access that turns out null at runtime crashes with a clear message
- `?.length`/`?[i]` on null returns 0 without crashing, silently (no warning)
- No behavior regressions to Task 9's existing non-nullable array support

**Deliverables:**
- Nullability decision recorded (ADR, alongside Task 12.7)
- Compile-time null-flow analysis pass
- `.`/`?.`/`?[` parser support
- Runtime null-check codegen
- Updated language spec matching actual behavior

**Explicitly NOT scheduled now:** this task is future work. Task 12.7 is now complete, so
its blocker is cleared, but no implementation, grammar design, or parser work should begin
until the user re-opens this task for scoping approval - same convention as Tasks 12/13.

---

## TASK 15: Deferred Decisions Revisit List

**Goal:** Track every decision or known gap that Task 12's work deliberately deferred
(rather than fixed or resolved) as an actual checklist, each with its own trigger
condition for when to come back to it - so none of them get silently forgotten just
because Task 12 itself is marked complete.
**Status:** Not Started (tracking list - each sub-item has its own independent trigger; not
a single unit of work to approve/implement all at once)
**Priority:** LOW individually per item (none are urgent on their own - see each item's
trigger); the list itself is worth keeping current
**Source:** Surfaced during Task 12 (Architecture Hardening, complete 2026-09-13) - full
detail on each underlying decision is in `task/taskSummaryArchive.md`'s Task 12 section

### Why this task exists

Several Task 12 sub-tasks concluded "defer this, revisit later" rather than "done." Once
Task 12's section moved to the archive, those revisit notes risked becoming easy to lose
track of (each one only lived as a paragraph inside a module docstring or a plan file, not
as anything checkable). This task exists purely to hold them as visible `[ ]` items with a
concrete trigger, so a future session can scan this list and act on whichever item's
trigger has arrived, rather than re-discovering them by reading old commit messages.

### Sub-tasks (each independent - work through at each item's own trigger, not as a batch)

#### 15.1: Fusion IR Layer Decision (trigger: Task 11 kickoff)
- [ ] Before writing any LLVM codegen, revisit whether to introduce a dedicated Fusion IR
      (`AST -> Typed AST -> Fusion IR -> {C, LLVM, VM, WASM}`) instead of Task 11 consuming
      the Typed AST directly like the C backend does today (Task 12.10 deferred this -
      only one backend existed to validate the abstraction against)
- [ ] Decide among: full IR (real lowered representation, migrate the C backend to it
      too), thin/contract-only IR (formalize the Typed AST as a stable backend contract,
      no new data structure), or continue direct-AST consumption as
      `task/task-11-llvm-backend-plan.md` currently assumes
- [ ] If a full IR is adopted, migrate the C backend to it too, so both backends share one
      design instead of the IR being LLVM-only
- [ ] Note already recorded in `task/task-11-llvm-backend-plan.md`'s "Revisit at kickoff"
      callout - this item is the actual action, not just re-reading that note again

#### 15.2: Stdlib Runtime Lowering Decision (trigger: first real `import`/fusionlib module scoped)
- [ ] Revisit replacing the 2 special-cased builtins in `CCodeGenerator.visit_CallExpr`
      (`print` and `len` - the two true runtime-call builtins; `range()` is not a runtime
      call, it's consumed structurally inside `visit_ForStmt`, so it doesn't apply here)
      with a general runtime-API lowering layer: Fusion stdlib call -> runtime API ->
      backend-specific implementation (e.g. `fusion_print_int`/`fusion_print_float`)
- [ ] Task 12.11 deferred this because `import` has zero parser support today - there is
      no real stdlib call to lower yet. Design the layer once informed by what an actual
      first stdlib module needs (which types cross the boundary, error-handling
      convention, one shared naming scheme) rather than guessing its shape now
- [ ] Note already recorded in `src/codegen/c_runtime.py`'s module docstring

#### 15.4: Task 10/11 Ordering Question (trigger: before starting either Task 10 or Task 11)
- [ ] The original architecture review suggested LLVM/IR work should come before
      self-hosting, reversing Task 10/11's current planned order - this contradicts an
      earlier explicit decision (Session 19) to plan self-hosting first
- [ ] Never resolved either way since being flagged - get an explicit user decision before
      starting either Task 10 or Task 11, rather than defaulting to the existing order by
      inertia just because it was written down first

#### 15.5: Memory Model Implementation Is Not Tracked Anywhere (trigger: needs scoping first)
- [ ] `Unique<T>`/`Shared<T>`/`Weak<T>` semantics are fully decided and documented (Task
      12.7's ADR in `files/fusion-language-spec.md`), but there is zero parser/semantic/
      codegen implementation - confirmed via source search, they remain lexer-keyword-only
      in `src/lexer/keywords.py`
- [ ] No task currently tracks actually building this. Before assuming it's "done" just
      because the design is written down, scope a real implementation task: parser support
      for `Unique<T>`-style generic-looking syntax, semantic rules for move/refcount/
      weak-upgrade checking, and codegen lowering

#### 15.6: fusion.toml Safety/Backend Keys Are Not Enforced (trigger: strict mode or a second backend gets built)
- [ ] `[safety].mode` and `[backend].target` are parsed and validated by
      `src/config/project_config.py` (Task 12.12) but read by nothing else - `mode =
      "strict"` currently changes no compiler behavior at all, and `backend.target` only
      ever has one legal value ("c") to select between
- [ ] Wire `safety.mode == "strict"` into the semantic analyzer once strict-mode rules are
      actually defined (e.g. `files/fusion-language-spec.md`'s existing claim that "Weak
      pointers cause a compile error in strict mode")
- [ ] Wire `backend.target` to actually select a backend once Task 11 (LLVM) exists as a
      second option

#### 15.8: Reserve the `fusion_` Identifier Prefix (trigger: before `import`, Task 18.4)
- [ ] Generated C uses `fusion_` names the user never wrote: `fusion_double` (a function
      named after a C keyword, Task 12.5) and `fusion_len_values` (the hidden length of an
      `int[] values` parameter, Task 18.1.2). A user identifier spelled the same way would
      collide with them in the C output
- [ ] Fix: reject user identifiers starting with `fusion_` (clear error), or mangle every
      user identifier. Cheap now; harder once libraries exist. Found during 18.1.2
- [ ] Same problem with C library names (noted 2026-10-09, 18.3.1): a Fusion function named
      `rename`, `free`, `exit`, `abs`, ... collides with `<stdio.h>`/`<stdlib.h>` in GCC.
      Mangling every user identifier fixes both

#### 15.10: Interpolated Strings Outside print() Generate Invalid C - GUARDED (2026-10-08, Task 18.2.1)
- [x] `string s = "x is {x}"` passed semantic analysis, then generated `char* s = "x is %d",
      x;` - invalid C (Task 12.6 bug class). Found while planning struct string fields, which
      would have hit the same thing. Now a clear error: an interpolated string can only be
      passed directly to `print()`
- [ ] **Real fix belongs to 18.3:** once strings can be built at run time, an interpolated
      string becomes an ordinary string value usable anywhere - remove the guard then

#### 15.12: Operand Evaluation Order (trigger: after 18.2.2b, or when it bites)
- [ ] `next(c) - next(c)` leaves the order of the two calls to C (unspecified). 18.2.2b makes
      call *arguments* left to right; operators (`+ - * / == and or ...`) should follow the
      same rule. `and`/`or` already short-circuit left to right in C, so only the others need
      it. Logged 2026-10-08

**Success Criteria:** Not applicable in the usual sense - this is a tracking list, not a
single feature. Each sub-task's own trigger condition (not a shared deadline) determines
when it gets actioned; "done" for this task as a whole just means every item above has
either been resolved or re-confirmed as still correctly deferred.

**Deliverables:** N/A (tracking only) - resolving any individual item produces its own
deliverables (a decision, a bug fix, a new task) at that time.

---

## TASK 16: Example Program Coverage

**Goal:** Give users a runnable example for every language feature - both features that
already exist but currently have no dedicated example, and features that don't exist yet
and should get one as soon as they're built (rather than that becoming an afterthought
each time). Formalizes Rule 5 above into an actual checklist.
**Status:** Not Started (16.1 is buildable now against already-implemented features; 16.2
onward are each blocked on their own feature being built first - see each item)
**Priority:** MEDIUM (doesn't block the compiler working; does matter for anyone other than
the maintainer trying to learn Fusion from examples alone)
**Source:** User request (2026-09-13) - "add more examples in fusion examples for each new
feature... so that users have more examples to work with"

### Why this task exists

The 8 examples in `examples/` today (`hello_world`, `factorial`, `fizzbuzz`, `calculator`,
`sum_array`, `max_three`, `const_demo`, `arrays_demo`) were each added alongside the task
that built their feature, but coverage has gaps even for already-implemented features
(nothing demonstrates `break`/`continue` outside unit tests, for instance), and there's no
standing checklist for the larger, not-yet-built features (classes, generics, threading,
error handling) to pick up once those land. This task is that checklist.

### Sub-tasks

#### 16.1: Control Flow / Loops Example - NOT BLOCKED (feature already implemented)
- [ ] New `examples/control_flow_demo.fusion` demonstrating `while`, `for` (including
      `range()`), nested loops, `break`, `continue`, and an `if`/`else if`/`else` chain all
      in one place - today these only appear incidentally scattered across other examples
      (`fizzbuzz.fusion`'s `while`, `sum_array.fusion`'s `for`), and `break`/`continue`
      specifically have zero example coverage anywhere, only unit tests
- [ ] Compile and run manually to verify real output, then add to
      `tests/verify_examples.py`'s expected outputs like every other example
- [ ] Add to README's Example Programs list

#### 16.2: Classes, Structs, Interfaces & Enums (OOP) Example - BLOCKED
- [ ] Blocked on classes/structs/interfaces/enums actually being implemented - currently
      just reserved keywords (`class`, `struct`, `interface`, `enum`, `inherits`,
      `implements`, `property`, `get`, `set`), no parser/semantic/codegen support at all
- [ ] Note: **no task currently tracks building this feature itself** - flagging that gap
      here too, since an example can't exist before the language feature does. Scoping the
      feature is a separate, larger decision than this task covers

#### 16.3: Generics Example - BLOCKED
- [ ] Blocked on generic type parameters being implemented - currently just a "Planned
      Features" line item in README, no task tracks building it, no reserved syntax
      decided beyond the general concept

#### 16.4: Multithreading / Async Example - BLOCKED
- [ ] Blocked on the Threading model actually being implemented - currently just the `go`
      keyword reserved plus `async`/`await` keywords reserved; the fusionlib `Threading`
      module (goroutines, channels, mutex) is vision-only, no task tracks building it

#### 16.5: Error Handling (try/catch) Example - BLOCKED
- [ ] Blocked on `try`/`catch`/`finally`/`throw`/`Error` actually being implemented -
      currently reserved keywords only, no parser/semantic/codegen support; no task
      currently tracks building this feature
- [ ] This is the "test error to try/catch them" example specifically requested - once the
      feature exists, demonstrate both a caught error (clean recovery) and an uncaught one
      (clear runtime error message), matching the project's existing preference for clear
      error messages over silent failure

#### 16.6: Memory Model (Unique/Shared/Weak) Example - BLOCKED
- [ ] Blocked on implementing the semantics Task 12.7 already decided (move-only
      `Unique<T>`, always-atomic `Shared<T>`, nullable-upgrade `Weak<T>`) - ties directly
      to **Task 15.5**, which tracks that no implementation task exists yet either

#### 16.7: Module System / Import Example - BLOCKED
- [ ] Blocked on `import` actually being parseable - confirmed via source search it's
      lexer-keyword-only today (same gap Task 15.2 already flagged for stdlib lowering);
      an example needs at least two files and a working `import` before it means anything

**Success Criteria:**
- Every implemented language feature has at least one dedicated, runnable example in
  `examples/`, verified via `tests/verify_examples.py`
- Every example added here follows the existing convention: compiled and run manually
  first to confirm real output, then locked in as an automated regression via
  `verify_examples.py`

**Deliverables:**
- `examples/control_flow_demo.fusion` (16.1 - the only currently-actionable item)
- One example per feature in 16.2-16.7, each added when its underlying feature ships
- Updated `tests/verify_examples.py` and README Example Programs list per new example

---

## TASK 17: Mutable vs. Fixed Strings, Templated Fixed Strings & String Pooling

**Goal:** Add an explicit mutable/immutable distinction to Fusion's string type
(`m"..."`/plain = mutable, `f"..."` = fixed/immutable), including fixed strings that hold
unresolved `{@N}` placeholders and can be invoked later like a function to fill them in, plus
an opt-in (off by default) string-pooling setting.
**Status:** Not Started (proposed breakdown only, not yet approved for implementation - same
status convention as Tasks 13/14)
**Priority:** MEDIUM (a real, common bug class in other languages - accidental mutation of a
string another part of the program still holds - but nothing currently built depends on this)
**Blocked By:** Nothing technical, but the templated-fixed-string mechanism (17.3) is a
genuinely new capability - not just applying existing `{@N}` syntax to a variable - and
needs real design before scoping, not just wiring
**Estimated Effort:** TBD - needs its own sub-plan once approved for scoping
**Source:** User request (2026-09-27) - full design write-up (syntax, semantics, examples,
open questions) is in `FutureFeatures.md`'s "Mutable vs. Fixed Strings, Templated Fixed
Strings & String Pooling" section under "Type System Enhancements" - this task is the
tracked pointer to it, per Rule 5 / this file's practice of logging every proposal as both a
`FutureFeatures.md` write-up and a `taskSummary2.md` task

### Sub-tasks (NOT YET APPROVED - proposed breakdown only)

#### 17.1: Mutable String Literal Syntax
- [ ] Decide whether `m"..."` is worth adding as an explicit prefix at all, given a plain
      string literal is already mutable by default - likely justified only for symmetry
      with `f"..."`, not because it changes behavior
- [ ] If added: lexer/parser support for the `m` prefix (no semantic change from a plain
      string literal)

#### 17.2: Fixed (Immutable) String Type
- [ ] Add `f"..."` as a fixed/immutable string literal - the value itself can never change
      after creation
- [ ] Decide what "mutating" methods (e.g. `.ToUpper()`) return when called on a fixed
      string: a new fixed string, or a new plain (mutable) string - needs an explicit
      decision, not an assumption
- [ ] Semantic rules: reassigning a fixed-string *variable* is presumably still allowed
      (the variable isn't `const`) - only the string *value* itself is immutable. Confirm
      this distinction is the intended one, since it's easy to conflate with `const`

#### 17.3: Templated Fixed Strings (the genuinely new part)
- [ ] Design how a fixed string containing unresolved `{@1}`/`{@2}` placeholders becomes a
      reusable, callable template - this is NOT the same as Fusion's existing `{@N}`
      interpolation, which resolves immediately at the point of use; this proposes
      *deferred* resolution, invoked later with fresh arguments each call
- [ ] Decide the type of a placeholder-bearing fixed string: still `string`, or a distinct
      template/closure-shaped type that supports being called
- [ ] Decide error handling for non-contiguous placeholders (`{@1}`/`{@3}` with no `{@2}`)
      and argument-count mismatches - compile-time (placeholder count is statically known)
      or runtime
- [ ] Decide whether this needs a new AST node distinct from the existing
      `InterpolatedStringExpr`, or whether that node can grow a "deferred" mode
- [ ] Get user decision on all of the above before any implementation begins

#### 17.4: String Pooling Configuration
- [ ] Add a `[strings]` section to `fusion.toml` (extending Task 12.12's schema):
      `pooling = false` by default - strings are stored only where declared, no implicit
      interning of equal values
- [ ] Document the guidance from the request explicitly: pooling should only be enabled
      after profiling shows a real benefit (large volumes of duplicate strings), not as a
      default optimization - matches Fusion's general "configure deliberately, don't guess"
      philosophy already used elsewhere in `fusion.toml`
- [ ] If ever implemented: define what pooling actually changes (storage reuse only - must
      never be observable as a behavior difference to a correct program)

#### 17.5: Secure String Storage (far future - depends on fusionlib.Crypto existing)
- [ ] Document that plain strings (pooled or not) are the wrong type for passwords/
      cryptographic secrets - matches well-known guidance in other managed languages (e.g.
      Java recommending `char[]` over `String` for passwords, since a `String` can't be
      reliably zeroed and pooling can retain copies indefinitely)
- [ ] Note for whoever eventually designs `fusionlib.Crypto`: it should include a dedicated
      secure-storage type - explicitly never pooled, intended for secrets rather than
      general text - this task only identifies the need, doesn't scope the Crypto module
      itself
- [ ] Blocked on `fusionlib.Crypto` existing at all, which is blocked on `import` having
      parser support in the first place (currently none - same gap Task 15.2/16.7 already
      flag)

**Success Criteria:**
- Mutable strings behave exactly as they do today - no regression
- Fixed strings are provably never mutated in place
- A templated fixed string can be invoked multiple times with different arguments without
  changing the stored template
- String pooling is off by default with zero behavioral effect when disabled
- Passwords/secrets have a documented, explicitly-recommended alternative to plain strings

**Deliverables:**
- `m"..."`/`f"..."` lexer and parser support (pending 17.1's "is `m` worth it" decision)
- Semantic rules for fixed-string immutability and templated-fixed-string calling
- `[strings]` `fusion.toml` section (`pooling`)
- A noted cross-reference from `fusionlib.Crypto`'s eventual design to the secure-storage
  need identified here (17.5) - not a deliverable of this task itself

**Explicitly NOT scheduled now:** this task is future work only. No implementation, grammar
design, or parser work should begin until the user re-opens this task for scoping approval -
same convention as Tasks 13/14/16.

---

## TASK 19: Library Trust, Isolation & Security

**Goal:** Make Fusion safe to build on other people's code. Every imported library's use of
memory, hardware, network, and unsafe operations is explicit and verified; untrusted or
closed libraries can be sandboxed with a resource budget; the supply chain is protected
against compromised packages; and source-level attacks (including content hidden to
manipulate AI coding assistants) are caught.
**Status:** Not Started (proposed breakdown only, not yet approved for implementation - same
convention as Tasks 13/14/17)
**Priority:** HIGH once libraries exist - security retrofitted onto an existing ecosystem
rarely works (the same lesson as D's GC split). Most of this can't start until Task 18.4
(`import`) exists; **19.6's lexer checks can be done any time**.
**Blocked By:** Task 18.4 (`import`/multi-file) for 19.1-19.5; nothing for 19.6
**Estimated Effort:** TBD - large; each sub-task needs its own plan
**Source:** User direction (2026-10-07). Principle, in the user's words: **never trust code** -
do not trust library authors at all; even well-meaning code can leak memory or be badly
optimised, and a library can be compromised. **No defense is ever airtight against a
determined attacker** - the goal is to make attacks as hard and unlikely as possible, with
layered defenses, accepting that importing code always carries some risk. Full design
reasoning: `FutureFeaturesCaution.md` sections 3-5.

### Sub-tasks (NOT YET APPROVED - proposed breakdown only)

#### 19.1: Explicit, Compiler-Verified Capability Signatures
- [ ] Every function, class, and module carries a signature of exactly what it uses: memory
      strategy (stack/GC/`Unique`/`Shared`/arena/raw), heap, unsafe, I/O, network, threads,
      hardware/devices, exceptions
- [ ] Signatures are **published** with the library (a manifest), so importers can see what
      every part uses *before* compiling - and the importing compiler can warn when the
      project doesn't handle something a library needs
- [ ] Signatures are **never trusted from the author** - for source libraries the importing
      compiler re-derives them from the code and rejects a mismatch with the manifest
- [ ] On library upgrade, show a **capability diff** - "v2.4 now requires `network`, v2.3
      didn't." A sudden new capability in a minor update is one of the strongest signals of
      a compromised package

#### 19.2: Project Restrictions (Ada `pragma Restrictions`-style)
- [ ] A `[restrictions]` section in `fusion.toml` (e.g. `no_unsafe`, `no_network`,
      `no_heap`, `max_stack`) enforced across **all** code in the program - the project's
      own code and every imported library - modeled on Ada's `pragma Restrictions` /
      `pragma Profile`, which has done this industrially for decades
- [ ] Clear diagnostics naming the exact library function and the call chain that violates
      a restriction

#### 19.3: Closed, Compiled, and Licensed Libraries
- [ ] Support libraries whose source isn't available (commercial, compiled-only, restricted
      licence) - their signatures can't be re-derived from source, so they need another
      basis for trust:
      - **Signed manifests** from the library's build, plus reproducible builds where possible
      - Option to ship as **verifiable IR** instead of machine code, so the consumer's
        compiler can still check capabilities and apply the project's strategy without
        seeing the source (with the tradeoff that IR is easier to decompile - the Java
        bytecode problem)
      - **Default to sandboxing** (19.4) anything that can't be verified
- [ ] Licence metadata in the manifest (terms, permitted use) with a compiler check for
      licence conflicts with the project

#### 19.4: Library Sandboxing and Resource Budgets
- [ ] A library can run isolated from the main application with only a **declared budget**:
      X RAM, CPU/GPU time, and specific devices or drivers - nothing else
- [ ] **Per-library memory regions:** a sandboxed library allocates only from a region the
      host owns. Explicit allocations must be freed by the library; anything it leaks, the
      host reclaims when the region is torn down - bad or compromised code can't leak into
      the main application
- [ ] Unsafe/raw allocation inside a library must be wrapped behind a safe interface
- [ ] Isolation levels chosen per library by the project: none (trusted, compiled inline) /
      memory-region (guards against bugs and leaks) / separate process (strongest - for code
      that may be actively malicious). In-process sandboxing protects well against *bugs*;
      Java's applet history shows it is very hard to make airtight against *deliberate
      attacks*, so untrusted code should get process isolation
- [ ] **Profiling** of each library's real resource use (memory, CPU/GPU, I/O) against its
      declared budget
- [ ] Prior art to study: WebAssembly's component model (each module has its own memory and
      explicit imports), Deno's permission flags, Ada restrictions

#### 19.5: Supply-Chain Security
- [ ] Lockfile pinning every dependency to an exact version **and content hash**
- [ ] Signed packages (e.g. Sigstore-style) and reproducible builds
- [ ] **No arbitrary code execution at install or build time** - npm `postinstall` scripts and
      build scripts are major attack vectors; any compile-time code execution must itself be
      sandboxed
- [ ] Capability-diff alerts on every dependency update (19.1)
- [ ] Software bill of materials (SBOM) output
- [ ] Real precedents this guards against: the xz-utils backdoor (2024), the event-stream npm
      compromise (2018), and recent repository/package compromises that inject backdoors

#### 19.7: AI Module Input Guard (far future - depends on fusionlib.AI existing)
- [ ] When Fusion's future `fusionlib.AI` module passes text to an AI model, it first parses
      that text and checks for embedded code and hidden instructions - content written to
      manipulate the model (prompt injection) - before anything reaches the model
- [ ] Logged now, rather than when the AI module is designed, because attacks aimed at AI
      tools (including Claude, which helps build Fusion) are a real and growing risk, and
      the requirement should shape that module from its first design
- [ ] Detection is heuristic, never a guarantee - the guard reduces risk; it can't remove it.
      The model receiving the text must still treat it as data, not instructions

**Success Criteria:**
- Before compiling, a developer can see exactly what every imported function uses
- No library can use a capability the project hasn't allowed, and no library's leaked memory
  outlives its sandbox
- A dependency update that adds new capabilities is flagged, never applied silently
- Source containing Trojan Source characters fails to compile

**Deliverables:**
- Verified capability signatures and manifests; `[restrictions]` in `fusion.toml`
- Library sandbox with memory regions and resource budgets
- Lockfile, signing, and capability-diff tooling
- Lexer-level source attack checks

**Scheduling:** 19.6 done (2026-10-07). 19.1-19.5 need Task 18.4 (`import`) first; 19.7 needs
`fusionlib.AI`.

## TASK 20: Multi-Format Project Configuration

**Goal:** Accept the project configuration file in any of four interchangeable formats -
`fusion.toml`, `fusion.yaml`, `fusion.json`, or `fusion.ini` - so older applications and
tooling that can only produce JSON or INI (or prefer YAML) can still configure a Fusion
project.
**Status:** Not Started (decided by the user 2026-10-07; detailed plan still needs approval
before implementation, per Rule 1)
**Priority:** MEDIUM - small and self-contained; not blocked by anything
**Source:** User decision (2026-10-07). This extends Task 12.12, which chose TOML-only. TOML
stays the documented default; the other three become equally valid alternatives.

### Sub-tasks

#### 20.1: One Loader Per Format, One Shared Schema
- [ ] Each format gets a small loader that produces the **same in-memory dictionary**; the
      existing validation in `src/config/project_config.py` then runs unchanged on it, so all
      four formats are guaranteed to mean exactly the same thing
- [ ] TOML (`tomllib`), JSON (`json`), and INI (`configparser`) are all in Python's standard
      library - no new dependencies
- [ ] **YAML needs a third-party package (PyYAML)** - the one format that adds a dependency.
      Recommend loading it lazily, only when a project actually uses `fusion.yaml`, with a
      clear error if PyYAML isn't installed - so projects that don't use YAML never need it
- [ ] INI stores every value as text, so its loader must convert types (`"4"` -> 4,
      `"true"` -> true) before validation. Nested sections map onto INI section names
      (`[imports.policy]` works as a literal section name)
- [ ] Known YAML pitfall to guard against: older YAML parsers read unquoted `no`/`yes`/`on`/
      `off` as booleans (the "Norway problem" - the country code `NO` becomes `false`). The
      shared validation step catches wrong types, but the docs should recommend quoting

#### 20.2: Discovery and Ambiguity
- [ ] Look for all four names (source directory first, then the current directory, as today)
- [ ] **Recommend: if more than one config file is found in the same place, stop with an
      error** ("found fusion.toml and fusion.json - keep only one") rather than silently
      picking one by precedence - two configs that disagree is exactly the kind of silent
      surprise Fusion avoids
- [ ] Error messages name the specific file and format that failed

#### 20.3: Tests
- [ ] The same configuration written in all four formats produces an identical result
- [ ] Format-specific edge cases: INI type conversion, YAML booleans, JSON syntax errors,
      missing PyYAML
- [ ] Ambiguity error when two config files exist

#### 20.4: Documentation
- [ ] Language spec "Project Configuration" section, CLAUDE.md Quick Syntax Reference,
      README, and `examples/project_config_demo/` (show at least one non-TOML variant)

**Success Criteria:** all four formats load identically through one shared validation path;
TOML/JSON/INI add no dependencies; existing `fusion.toml` behavior is unchanged.

---

## TASK 21: Error Handling (Go-style error returns + try/catch)

**Goal:** Let Fusion programs report and handle errors - both ways the spec describes,
as **complementary** tools, not competing ones.
**Status:** Not Started - **scheduled right after Task 18.3** (needs real strings for error
messages), before 18.5's standard library (file I/O must be able to report "file not found")
**Priority:** HIGH
**Blocked By:** Task 18.3 (strings - "we do need strings to be working properly as to make sure
we can pass string error messages")
**Source:** user decisions, 2026-10-09

**User decisions (2026-10-09):**
- **Go-style error returns are supported, on by default** - and are **only for returning an
  error from a function**: `Spaceship, Error function loadShip(string file)`, then
  `Spaceship ship, Error err = loadShip("ship.dat")` and a simple `if err` check. Not a
  general multiple-return-values feature. "Sometimes we don't need the full try catch but
  just the simple check for the error"
- **`try`, `catch`, `finally`, `throw` and `Error` are supported, on by default**
- **Both can be turned off per project** in the config file (`fusion.toml`, and the other
  formats once Task 20 lands) - consistent with FutureFeaturesCaution.md: the core stdlib
  layer works with no exceptions, and `[imports.policy] exceptions = "abort"` maps a throw to
  a clear termination when a project disables them
- Both are complementary: a function can return an error for a caller that just checks it,
  or throw for a caller that wants try/catch

**Sub-tasks:** a detailed plan is written and approved before any implementation (Rule 1).
Starting points for that plan (not yet decided):
- How the two meet: can `try` catch an error *returned* Go-style, and can an `Error` return
  value be re-thrown? What happens to an unchecked returned error (spec: "bubbles up")?
- `Error` as a built-in struct (message, plus file/line?), and error chaining (spec section
  "Error Chaining")
- C lowering for try/catch (setjmp/longjmp vs. explicit error propagation) - and how
  automatic string cleanup (18.3.1) runs when an error unwinds through a function
- Config keys, e.g. `[errors] error_returns = true`, `exceptions = true`
- 18.3.2's stop-with-a-run-time-error conversions (`toInt("12x")`) can then become catchable
- Example program: Task 16.5 (catch an error, and show an uncaught one) is unblocked by this

---

