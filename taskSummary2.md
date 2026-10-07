# Fusion Compiler - Post-MVP Task Summary

**Project:** Fusion Programming Language Compiler - Post-MVP Development
**Previous:** task/taskSummary.md - MVP Complete (Tasks 1-4, Phases 1-4)
**Archived:** task/taskSummaryArchive.md - Completed post-MVP task detail (Tasks 5-9, 12) -
see CLAUDE.md Rule 3 for when/how sections move there
**Status:** Planning & Verification Phase
**Last Updated:** 2026-09-13

---

## CRITICAL RULES

1. **PLAN FIRST, THEN ACT** - Never implement without approved plan
2. **NO EMOJIS IN CODE** - Only in markdown and chat
3. **UPDATE AFTER EVERY SUB-TASK** - Keep this file current
4. **taskSummary2.md STAYS IN ROOT** - Do not move until project complete
5. **SHIP AN EXAMPLE FOR EVERY NEW FEATURE** - When a new language feature lands (loops,
   classes, generics, threading, error handling, etc.), add a runnable program to
   `examples/` demonstrating it, as part of closing out that feature's task - not a
   separate ceremony done later. See Task 16 for the current backlog of missing examples.

---

## ⚠️ NAMING CONFLICT

**Discovered:** There is an existing programming language called "Fusion" (https://fusion-lang.org/)

**Renaming Plan:**
- Continue using "Fusion" name during development
- **MUST rename before 1.0 release**
- Rename will happen when language is fully working and stable
- No urgency during development - focus is on getting compiler working correctly first
- Renaming task will be added to roadmap closer to 1.0 release

---

## Current Objective

**ORGANIZE** the project structure and **VERIFY** the MVP compiler works correctly in real-world scenarios.

---

## Overall Progress

| Phase | Status | Progress | Tasks Complete | Total Tasks |
|-------|--------|----------|----------------|-------------|
| **Task 5: Cleanup & Organization** | Complete | 100% | 5 | 5 |
| **Task 6: Verification & Bug Fixes** | Complete | 100% | 7 | 7 |
| **Task 7: Git Integration** | Complete | 100% | 4 | 4 |
| **Task 8: Language Features (const)** | Complete | 100% | 8 | 8 |
| **Task 9: Language Features (arrays v1)** | Complete | 100% | 8 | 8 |
| **Task 10: Self-Hosting** | Planning Complete | 8% | 1 | 12 |
| **Task 11: LLVM Backend** | Planning Complete | 8% | 1 | 13 |
| **Task 12: Architecture Hardening** | Complete | 100% | 12 | 12 |
| **Task 13: HIDL (Hardware Interface)** | Blocked / Future | 0% | 0 | 9 |
| **Task 14: Nullable Arrays & Safe Nav** | Blocked / Future | 0% | 0 | 6 |
| **Task 15: Deferred Decisions Revisit List** | In Progress | 14% | 1 | 7 |
| **Task 16: Example Program Coverage** | Not Started | 0% | 0 | 7 |
| **Task 17: Mutable/Fixed Strings & Pooling** | Not Started | 0% | 0 | 5 |
| **Task 18: Core Language Foundation** | Not Started (next priority) | 0% | 0 | 5 |
| **Task 19: Library Trust, Isolation & Security** | In Progress (19.6 done) | 14% | 1 | 7 |
| **Task 20: Multi-Format Project Config** | Not Started | 0% | 0 | 4 |
| **Overall** | Task 19.6 Complete | 40% | 48 | 119 |

---

## Completed Tasks (Archived)

Tasks 5-9 and 12 are complete. Their full sub-task detail, success criteria, and
deliverables have been moved to `task/taskSummaryArchive.md` to keep this file small (see
CLAUDE.md Rule 3). The Overall Progress table above still tracks their status at a glance.

- Task 5: Project Cleanup & Organization - Complete
- Task 6: Verification & Bug Fixes - Complete
- Task 7: Git Integration & GitHub Setup - Complete
- Task 8: Language Features - const Keyword - Complete
- Task 9: Language Features - Array Support (v1) - Complete (fixed-size, local-variable
  arrays; nullable/safe-navigation follow-on split out to Task 14)
- Task 12: Compiler Architecture Hardening (Typed AST & Codegen Refactor) - Complete (all
  12 sub-tasks - Typed AST, C codegen split, block-level scoping, memory model semantics,
  docs sync, project configuration system, and two deliberately-deferred design decisions
  with rationale recorded - see `task/taskSummaryArchive.md` for full detail, or this
  file's Working Notes below for the session-by-session narrative)

---

## Task Order Note (2026-09-13)

Tasks below are now listed in numerical order (9, 10, 11, 12, 13, 14, 15, 16) rather than
the historical order they were written in - they had drifted out of order across sessions
(Task 14 briefly sat between 9 and 10). Task numbers themselves are unchanged; only their
position in this file moved, to make the file easier to scan.

---

## TASK 9: Language Features - Array Support - COMPLETE

**Status:** Complete (v1 scope - fixed-size, local-variable arrays) - 2026-09-13. Full
sub-task detail (syntax design, lexer/parser/semantic/codegen work, examples, docs),
success criteria, and deliverables have been moved verbatim to
`task/taskSummaryArchive.md` (see CLAUDE.md Rule 3). See the Overall Progress table above
for a glance.
**Deferred, tracked separately:** arrays as function parameters/return types,
multi-dimensional arrays, non-literal array sizes, whole-array reassignment, dynamic/
resizable arrays, bounds checking, and everything nullability-related (`.length`,
`?.length`, `?[i]`) - see **Task 14** below.

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

## TASK 12: Compiler Architecture Hardening (Typed AST & Codegen Refactor) - COMPLETE

**Status:** Complete (all 12 sub-tasks) - 2026-09-13. Full sub-task detail (Typed AST,
C codegen module split, block-level scoping, memory model semantics, docs sync, project
configuration system, and two deliberately-deferred design decisions), success criteria,
and deliverables have been moved verbatim to `task/taskSummaryArchive.md` (see CLAUDE.md
Rule 3). See the Overall Progress table above for a glance, and this file's Working Notes
below for the session-by-session narrative of how each sub-task was decided/implemented.
Task 12's completion unblocked Task 13 and Task 14 (both still need their own scoping
approval before implementation, per Rule 1).

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

#### 15.3: LambdaExpr Scope Bug (trigger: lambda codegen stops being a stub)
- [ ] `NameResolver.resolve_lambda()` resolves a `BlockStmt`-bodied lambda's statements
      inline without going through `resolve_block()`, so the block's `.scope` never gets
      set - under block-level scoping (Task 12.6), `TypeChecker.visit_BlockStmt()` falls
      back to creating a fresh scope in this one case instead of reusing the correct one
- [ ] Not fixed during Task 12.6 because no current test exercises this path and lambda
      codegen is itself still a stub (`c_generator.py` emits `/* <lambda> */`) - this was a
      deliberate, flagged deferral, not an oversight
- [ ] Fix: make `resolve_lambda()` call `resolve_block()` properly, once lambda codegen is
      actually implemented and this path becomes reachable by real programs

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

#### 15.7: Lexer Warnings Are Never Surfaced - RESOLVED (2026-10-07, as part of Task 19.6.4)
- [x] Fixed: `main.py` now prints every lexer warning (`Lexer warning: ...`) before checking
      errors; covered by `test_main_prints_lexer_warnings` in `tests/test_source_security.py`
- [x] (original note) `main.py` checks `lexer.diagnostics.errors` and stops the build on any, but never
      prints `lexer.diagnostics.warnings` anywhere - e.g. the mixed-tabs-spaces warning
      (`allow_mixed = true`, the default) is generated and silently collected, then
      dropped without ever reaching the user
- [ ] Discovered while building `examples/project_config_demo/` (Task 12.12) - not fixed
      there since it's a pre-existing gap unrelated to that task's scope
- [ ] Compare with `SemanticAnalyzer.print_diagnostics()`, which already surfaces semantic
      warnings even on a successful build (see `main.py`'s "Print warnings even on
      success" step) - `main.py` should do the equivalent for lexer warnings

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

## TASK 18: Core Language Foundation ("a simple working language first")

**Goal:** Build the small set of core features every other planned feature depends on, so
Fusion can write real (non-toy) programs before any of the larger future features begin.
**Status:** Not Started - **recommended next priority** (user agreed with the direction,
2026-10-07: "the first goal is to get a simple working language first"). Each sub-task still
needs its own detailed plan approved before implementation, per Rule 1.
**Priority:** HIGH - nearly every open task is blocked on something in this list (see "Why
this task exists")
**Blocked By:** Nothing
**Estimated Effort:** TBD - each sub-task gets its own plan; 18.4 (import) is the largest
**Source:** Claude review of the project (2026-10-07) - see `FutureFeaturesCaution.md` for
the full reasoning. Overlaps heavily with Task 10.2 (self-hosting prerequisites: file I/O,
collections, string helpers, CLI args) - this task effectively becomes that prerequisite
work, done for its own sake rather than only in service of self-hosting.

### Why this task exists

The documented vision (FutureFeatures.md) is far larger than the implemented core, and the
same few missing core features block almost everything else: the Currency Module, Crypto,
Regex, HIDL, the whole stdlib, the Symbol-ID system, most of Task 16's examples, and
self-hosting all need `import`; Currency's runtime representation, HIDL register maps, and
classes all need structs; self-hosting needs strings, file I/O, and collections. Building
this foundation unblocks roughly 80% of the open task list in one stretch.

### Sub-tasks (each needs its own approved plan before implementation)

Ordered by dependency - each builds on the ones before it.

#### 18.1: Functions With Full Parameter Types
**Why first:** functions are the unit of all reusable code - a stdlib, a self-hosted
compiler, or any non-trivial program is built out of them, and today they're restricted.
- [x] **Default parameter values don't actually work** (verified 2026-10-07) - FIXED in 18.1.1: they're parsed
      and type-checked, but calling `greet()` on `void function greet(string name = "World")`
      fails semantic analysis with "expects 1 argument(s), got 0". CLAUDE.md's Quick Syntax
      Reference advertises this syntax, so it's a correctness gap, not just a missing
      feature. C has no default arguments, so codegen must fill omitted arguments in at each
      call site
- [ ] Arrays as function parameters and return values (rejected outright today in
      `name_resolver.py`, deferred since Task 9) - needs a pointer+length representation
      in C, since C arrays decay to pointers and lose their size
- [ ] Real lambda codegen (currently emits the placeholder `/* <lambda> */`) - this also
      makes Task 15.3's LambdaExpr scope bug reachable, so fix both together
- [ ] Example program per Rule 5 / Task 16

### 18.1 Detailed Plan (APPROVED 2026-10-07 - all three parts)

Split into three parts, each shippable and committed on its own, in this order. Each one
adds tests, an example program (Rule 5), and spec/CLAUDE.md updates.

**18.1.1 - Default parameter values (the verified bug)**
**Status: COMPLETE (2026-10-07)**
- [x] Semantic: a parameter with a default must be followed only by parameters that also have
      defaults (`int f(int a = 1, int b)` is an error - otherwise the call `f(5)` is ambiguous)
      - `NameResolver.check_parameter_defaults`
- [x] Semantic: v1 defaults must be **compile-time constants** - a literal (not `null`) or a
      negated number literal. A default that references another parameter or a variable is
      an error with a clear message. This keeps C call-site filling trivially correct and
      avoids Python's "default evaluated once" trap entirely. (Planned to also allow a
      `const` - dropped, since Fusion has no global constants yet, so a function parameter
      can never see one.) Array parameters can't have defaults
- [x] Type checker: accept any argument count from (required) to (total); reports
      `expects 1 to 2 arguments, got 0`. Stores the completed list on the call node as
      `CallExpr.resolved_arguments`; the function's declaration is reached through the new
      `Symbol.declaration` field
- [x] Codegen: C has no default arguments, so each call site emits the omitted values
      (`greet()` -> `greet("World", 1)`)
- [x] Out of scope: named arguments (`f(b: 2)`, which the spec shows) - logged for later
- [x] 20 tests (`tests/test_functions.py`); new example `examples/functions_demo.fusion`
      (added to `verify_examples.py`, now 9/9); spec "Rules for default values" added.
      Full suite 1197 passed, 8 skipped

**18.1.2 - Arrays as function parameters**
- [ ] `int[] values` parameter - accepts an array of **any** size. C loses an array's length
      when it's passed, so codegen adds a hidden length parameter: `void f(int* values,
      int values_len)`, and every call passes it (`f(scores, 3)`). `len(values)` inside the
      function compiles to `values_len`
- [ ] `int[5] values` parameter - accepts only a 5-element array (checked at compile time);
      `len(values)` stays a compile-time constant
- [ ] An `int[]` parameter can be passed on to another `int[]` parameter (its hidden length
      goes with it), but not to an `int[5]` parameter (size unknown at compile time - error)
- [ ] **Passing is by reference** (recommended - same as C, Java, C#): the function works on
      the caller's array, so element changes are visible to the caller, and nothing is
      copied. A read-only (`const`) parameter can be added later if wanted
- [ ] **Arrays as return values stay rejected** - C can't return an array; this becomes easy
      once structs exist (wrap the array in a struct), so it moves to 18.2
- [ ] Still no bounds checking (unchanged - its own future item)

**18.1.3 - Lambdas v1 (no closures)**
The spec (`fusion-language-spec.md`, "Lambda Expressions") describes function types, inline
lambdas, passing functions as arguments, and closures. v1 builds everything except closures:
- [ ] Function type syntax, per spec: `(int, int) : int` (and the `->` alternative) for
      variables and parameters - e.g. `(int) : int op = tripler`
- [ ] Inline lambda expressions: `func(int x) : x * 2`, `function(...) : ...`, and the current
      `(int x) : x * 2`. The return type is inferred from the body expression (the parser
      currently records `void` as a placeholder)
- [ ] A named function can be used as a value (`apply(tripler, 5)`)
- [ ] Calling through a function-typed variable or parameter (`op(5)`)
- [ ] Codegen: each inline lambda becomes a private top-level C function
      (`static int fusion_lambda_1(int x)`), and function types become C function pointers.
      Replaces the `/* <lambda> */` placeholder
- [ ] Fix Task 15.3 (lambda block-scope bug) at the same time - this makes it reachable
- [ ] **Closures (a lambda using a variable from the surrounding function) are rejected** with
      a clear "not yet supported" error. Captured variables must outlive the function that
      created them, which needs heap memory and an ownership rule - the same decision 18.3
      has to make for strings. Revisit after 18.3
- [ ] Function-typed variables must be initialized - no `= null` yet (calling a null function
      crashes; nullability is Task 14's design)
- [ ] Out of scope: named lambdas declared inside a function body (`int adder(int x) : ...`
      inside another function) - they only matter once closures exist

**Success criteria for 18.1:** `greet()` with a default compiles and runs; a `sum(int[]
values)` function works on arrays of different sizes; `apply(func(int x) : x * 2, 5)` prints
10; a capturing lambda fails with a clear message; full suite green; 8/8 + new examples.

#### 18.2: Structs
**Why second:** the first user-defined composite type, and the lowest-risk way into
user-defined types - a value type maps directly onto a C `struct`, so it needs no runtime,
no inheritance, and no decision yet on how classes/interfaces/traits interact.
- [ ] Struct declaration, field access (`.` member access - which also delivers the parser
      piece Task 14 needs for `arr.length`), construction, assignment/copy semantics
- [ ] Structs as function parameters/return values (builds on 18.1)
- [ ] Nested structs and arrays of structs
- [ ] Prerequisite for: classes (Task 16.2), Currency's runtime struct, HIDL register maps,
      AST nodes in a self-hosted compiler
- [ ] Example program per Rule 5 / Task 16

#### 18.3: Proper Strings
**Why third:** today strings are only C string literals passed around as `char*` - there is
no concatenation, length, comparison, substring, or number conversion anywhere in codegen.
Nearly every real program needs these, and a self-hosted lexer is built entirely on them.
- [ ] **Latent bug - string `==` compiles to C pointer comparison** (verified 2026-10-07):
      `x == y` on two strings emits `(x == y)` in C, comparing addresses, not contents. It
      returns the right answer today only by accident - GCC deduplicates identical string
      literals - and will silently return false for equal strings as soon as any string is
      built at runtime. Same bug class as Task 12.6 (semantic analysis accepts something
      whose generated C is wrong). Fix early, before runtime-created strings exist
- [x] **Bug - `%` in a printed string is treated as a printf format code** - FIXED
      (2026-10-07, user-approved small fix): `print("Progress: 100% done")` printed
      `Progress: 100 1134633984one`, because string text was placed directly into `printf`'s
      format string, so `% d` read garbage from the stack (CWE-134 - `%n` could even write to
      memory). Now `escape_printf_text` in `c_runtime.py` doubles `%` in literal text on both
      the plain-print and interpolation paths, leaving codegen's own specifiers untouched.
      4 tests in `tests/test_source_security.py` (incl. end-to-end with `%d %s %n` in text)
- [ ] Concatenation, length, comparison (`==`/`!=`/ordering by content), indexing/substring,
      conversion to/from numbers
- [ ] **Equality operator family** (user request and decisions, 2026-10-07) - for strings
      first, then every other type (numbers, arrays, structs, later classes/references).
      **Decided:**
      - `=` is **assignment** as a statement (`xx = 2`), and **comparison inside an `if`
        condition** (`if xx = 2` or `if (xx = 2)`) - the compiler treats it as a compare
        there, never an assignment. Side benefit: C's classic `if (x = 5)` bug becomes
        impossible, because assignment can't happen inside a condition at all
      - `==` is **value comparison everywhere**: `xx == 2` is true if `xx` holds the number
        2, and `xx == "2"` is also true, because the value is the same
      - `===` is **strict comparison** - same type *and* same value: `xx === "2"` is false
        when `xx` is a number and `"2"` is text
      **Still open (decide when 18.3 is planned):**
      - Does `if xx = 2` compare like `==` (value) or `===` (strict)? Value seems most
        natural (VB-style readability) - confirm
      - Negation pairing: with `=` now a comparison, the original list reads as three
        pairs - `=`<->`!=`, `==`<->`!==`, `===`<->`!===` - confirm
      - Does the `=`-compares rule also apply in `else if` / `while` conditions? Consistency
        suggests yes
      - **Caution - define a small, explicit cross-type table for `==`:** JavaScript's loose
        `==` is a notorious bug source because its coercion rules are huge and surprising
        (`0 == ""` and `"0" == false` are both true). Recommend Fusion's `==` coerce only a
        few well-defined pairs (number <-> numeric text, char <-> one-character string) and
        never coerce "truthiness" (no bool <-> number/string)
      - Note: `'2'` (single quotes) is a **char** literal in Fusion, `"2"` is a string - the
        cross-type table must say whether char, string, and number all participate
      - An **identity** operator (the very same object in memory) has no symbol yet - needed
        once references and `Shared<T>` exist
      - Every operator must be defined per type and never fall through to C's raw `==` -
        that fall-through is exactly the pointer-comparison bug above
      - Security note: comparing secrets (passwords, tokens) needs constant-time comparison
        to avoid timing attacks - a Crypto concern (Task 17.5), but the operator design
        shouldn't rule it out
- [ ] Decide string memory ownership - concatenation creates new strings, so who frees
      them? This is the first place the memory model (Task 12.7) becomes practical, and
      it's the foundation Task 17 (mutable/fixed strings, pooling) builds on
- [ ] Example program per Rule 5 / Task 16

#### 18.4: `import` and Multi-File Projects
**Why fourth:** the single biggest unblocker - everything in the stdlib, every proposed
module, and every program larger than a few hundred lines needs it. Placed after 18.1-18.3
because there needs to be something worth importing (functions, structs, string utilities).
- [ ] `import` parsing (lexer keyword only today) and module resolution (how a module name
      maps to a file path)
- [ ] Visibility (`public`/`private` - already reserved keywords) across module boundaries
- [ ] Multi-file compilation: generate one C file per module plus headers, or one combined
      C file - a real decision, with implications for build speed and the future Symbol-ID
      system
- [ ] Record each module's interface signature (exported symbols, plus what capabilities
      it uses) - the groundwork for the ecosystem-fragmentation answer in
      `FutureFeaturesCaution.md`. Cheap to capture now, very expensive to retrofit later
- [ ] Example: a small multi-file project

#### 18.5: Minimal Standard Library (IO and Collections)
**Why last:** needs everything above - it's the first real importable module (18.4), built
from functions (18.1), structs (18.2), and strings (18.3).
- [ ] Console input, and file read/write
- [ ] A growable list (and probably a map/dictionary)
- [ ] Command-line arguments
- [ ] **Layer the stdlib from day one** (core / alloc / std, Rust-style): the core layer
      works with no heap, no GC, no exceptions; higher layers add allocation and OS
      services. This is the specific thing D got wrong - its standard library was built
      assuming a garbage collector, so making GC optional later split the ecosystem. See
      `FutureFeaturesCaution.md`
- [ ] Satisfies Task 10.2's self-hosting prerequisites (file I/O, collections, string
      helpers, CLI args)
- [ ] Example programs per Rule 5 / Task 16

**Success Criteria:**
- A non-trivial multi-file Fusion program (e.g. a word counter that reads a file, builds a
  list/map of words, and prints sorted counts) compiles and runs correctly
- Default parameters and string equality both behave correctly (the two verified gaps)
- Full test suite stays green; every sub-task ships with tests and an example program

**Deliverables:**
- Functions with full parameter support, structs, a real string type, `import`/multi-file
  compilation, and a minimal layered stdlib (IO + collections)
- One example program per sub-task

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

#### 19.6: Source-Level Attack Defenses - COMPLETE (2026-10-07)
**Before this task, both attacks below worked against Fusion.** A file containing two
different variables `аge` (Cyrillic `а`, U+0430) and `age` (Latin) that look identical
compiled cleanly, and so did a right-to-left override (U+202E) hidden in a comment and in a
string literal. Both are now rejected with a precise error.
- [x] Lexer rejects bidirectional-control and invisible Unicode characters anywhere in source,
      including comments and strings (Trojan Source, CVE-2021-42574) - new
      `src/lexer/source_security.py`, a pre-pass in `Lexer.tokenize()`
- [x] `\uXXXX` escapes added to string and char literals
- [x] Identifiers ASCII-only by default (user decision); opt-in via `fusion.toml`
      `[source] allow_unicode_identifiers = true`, where mixed look-alike scripts and
      compatibility characters are still rejected
- [x] Lexer warnings now printed by `main.py` (closes Task 15.7)
- [x] **Found and fixed along the way: char literals were broken end-to-end.** `char c = 'a'`
      compiled to the C multi-character constant `'\'a\''` and printed `'` instead of `a`,
      because nothing ever decoded the literal - the lexer keeps the raw text (`'a'`), and the
      parser passed it straight into the AST. The parser now decodes it
      (`decode_char_literal`). A parser test (`test_char_literal`) had been asserting the
      buggy behavior, and was corrected
- [x] Also: codegen's C-escaping (previously duplicated in four places) is now one helper,
      `escape_c_text`, which writes control/invisible characters as octal escapes so they
      never appear raw in generated C; char literals must be ASCII (a C `char` is one byte);
      Unicode digits no longer start a number
- [x] 54 new tests (`tests/test_source_security.py`, 4 config tests, 1 parser test). Full
      suite 1173 passed, 8 skipped; 8/8 examples

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

### 19.6 Detailed Plan (APPROVED 2026-10-07 - IMPLEMENTED, kept for reference)

**19.6.1 - Reject invisible and bidirectional control characters**
- [ ] A pre-pass in the lexer scans the whole source text before tokenizing, so comments
      and strings are covered - comments are exactly where Trojan Source attacks hide
- [ ] Rejected code points:
      - Bidirectional controls: U+202A-U+202E, U+2066-U+2069, U+200E, U+200F, U+061C
      - Invisible/zero-width: U+200B, U+200C, U+200D, U+2060, and U+FEFF anywhere except
        the very first character of the file (a UTF-8 byte-order mark that Windows editors
        often add is legitimate there, and is stripped)
- [ ] Hard error, not a warning, naming the character and position, e.g.:
      `trojan.fusion:4:31: error: invisible/bidirectional control character U+202E
      (RIGHT-TO-LEFT OVERRIDE) - can make code display differently than it compiles
      (Trojan Source). Write ‮ inside a string literal if this is intended.`
- [ ] Not configurable - this is a security baseline. Section 19.6.2's `\u` escape is the
      supported way to include such a character on purpose

**19.6.2 - Add `\uXXXX` escapes to string and char literals**
- [ ] `\u` followed by exactly four hex digits, e.g. `"‍"`; added to `ESCAPE_SEQUENCES`
      handling in `src/lexer/literals.py`, and emitted to C correctly
- [ ] Clear lexer errors for malformed escapes (`\u12`, `\uZZZZ`)

**19.6.3 - Confusable identifiers - DECISION NEEDED (recommendation first)**
- [ ] **Recommended: identifiers ASCII-only by default.** Simplest and strongest defense - no
      homoglyph is possible in pure ASCII - and it keeps generated C identifiers portable.
      Unicode stays fully allowed in strings and comments (`"café"`, `// 中文` are fine)
- [ ] Opt-in for projects that want non-English identifiers: `fusion.toml`
      `[source] allow_unicode_identifiers = true`. In that mode, reject identifiers that mix
      scripts (e.g. Latin plus Cyrillic or Greek in one name), detected from Unicode
      character names via Python's stdlib `unicodedata`. Full Unicode TR39 confusable
      detection (the approach Rust's compiler uses) needs a large data table - deferred
- [ ] Alternative if you prefer: allow Unicode identifiers by default and only reject mixed
      scripts. Weaker - two identifiers can still be entirely different scripts that look
      alike (all-Cyrillic `аре` vs all-Latin `ape`)

**19.6.4 - Surface lexer warnings (closes Task 15.7)**
- [ ] `main.py` currently drops lexer warnings entirely (Task 15.7). Print them, the same way
      semantic warnings are already printed - needed so any future warning-level source
      check is actually seen, and it's a small change

**19.6.5 - Tests and documentation**
- [ ] Unit tests: each rejected code point class, in code / comments / strings; BOM allowed
      only at the start; `\u` escapes valid and malformed; ASCII-only identifiers by default;
      Unicode identifiers allowed with the config flag; mixed-script rejection; ordinary
      Unicode (é, 中文) still accepted in strings and comments
- [ ] Regression test reproducing the two verified attacks above, now rejected
- [ ] Before changing identifier rules, confirm no existing test or example uses non-ASCII
      identifiers (checked 2026-10-07: the only non-ASCII characters in `tests/` are `→`
      arrows in Python comments/docstrings, not in Fusion source)
- [ ] Docs: language spec (lexical rules), CLAUDE.md, README; `fusion.toml` `[source]`
      section documented

**Success criteria for 19.6:** both verified attacks fail to compile with a clear message;
full suite stays green; 8/8 examples still pass.

---

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

## Working Notes

### Session 16 (2025-12-14 - Planning Phase)
- Created taskSummary2.md for post-MVP work
- Updated CLAUDE.md with strict PLAN-FIRST methodology
- Added NO EMOJIS IN CODE rule
- Defined Tasks 5-9:
  - Task 5: Project cleanup
  - Task 6: Verification fixes
  - Task 7: Git integration
  - Task 8: const keyword
  - Task 9: Array support
- Identified FizzBuzz bug (missing numbers in output)

### Session 17 (2025-12-14 - Task 5 Execution)
- **Task 5: Project Cleanup & Organization - COMPLETE**
  - 5.1: Moved taskSummary.md to task/ folder (archive)
  - 5.2: Moved verify_examples.py to tests/ folder
  - 5.3: Organized documentation (verification_report.md → files/reports/)
  - 5.4: Updated path references in README.md
  - 5.5: Verified all tests passing (1,041/1,041)
- **All Files Now Properly Organized**

### Session 18 (2025-01-08 - Project Review & Task 6 Planning)
- **Claude Opus Project Review Completed**
  - FizzBuzz bug ROOT CAUSE identified: String interpolation codegen issue
  - print("{i}") generates printf("\n") instead of printf("%d\n", i)
  - Identified 5 "stale" test files in root
  - Identified 2 empty folders (Compiler/, Specification/)
  - Identified 4 AI review files needing organization
- **Added Task 6.0: Pre-Verification Cleanup**
- **Executed Task 6.0 - CRITICAL DISCOVERY:**
  - "Stale test files" are actually DEBUG SCRIPTS that patch Lexer class
  - test_trace_pos_changes.py wraps pos property → breaks 290 tests when collected
  - Created debug/ folder to isolate debugging scripts from pytest
  - Moved 6 debug scripts to debug/ (pytest now ignores them)
  - Organized 4 AI review files to files/reviews/
  - Updated pytest.ini with norecursedirs = debug
  - All 1,041 tests passing after cleanup
  - Empty folders require user permission to delete
- **Executed Task 6.1 & 6.2: FizzBuzz Bug Fix - COMPLETE**
  - Investigated generated C code: printf("\n") instead of printf("%d\n", i)
  - Traced bug to lexer parse_string_interpolation() function
  - Bug: For "{i}", lexer returned [('INTERP_VAR', 'i')] with NO STRING_PART entries
  - Should return: [('STRING_PART', ''), ('INTERP_VAR', 'i'), ('STRING_PART', '')]
  - Fixed src/lexer/literals.py to always add STRING_PART (even if empty)
  - Updated 10 tests in test_literals.py to expect correct format
  - FizzBuzz now outputs correctly: 1, 2, Fizz, 4, Buzz, Fizz, 7, 8, ...
  - All 1,041 tests passing, verification 3/6 examples match expected output
- **Executed Task 6.3, 6.4, 6.5: Example Verification - COMPLETE**
  - Ran all 6 examples to capture actual outputs
  - Updated verify_examples.py with correct expected outputs:
    - calculator: "Sum: 15\nDiff: 5\nProd: 50"
    - factorial: "Factorial of 5 is 120"
    - fizzbuzz: First 15 lines (1, 2, Fizz, 4, Buzz, ..., FizzBuzz)
    - hello_world: "Hello, World!"
    - max_three: "Maximum of 10, 25, 15 is 25"
    - sum_array: "Sum of 1 to 10: 55"
  - Verification results: 6/6 compile, 6/6 run, 6/6 match expected output
  - **100% verification success rate achieved**
  - Generated detailed verification_report.md in files/reports/
- **Executed Task 6.6: C Code Quality Review - COMPLETE**
  - Reviewed all 6 generated C files
  - **All code functionally correct - no bugs found**
  - String interpolation working correctly in all examples
  - Recursion (factorial.c): Correct base case and recursive case
  - Loops (while, for): Generated correctly
  - Conditionals (if/else): Logic correct
  - Minor style observations: Excessive parentheses, unused headers (not bugs)
  - **Quality assessment: EXCELLENT**
- **TASK 6: VERIFICATION & BUG FIXES - 100% COMPLETE**
- **Updated Task Progress Table** (Task 6: 7/7 complete, Overall: 12/32 complete)

### Session 19 (2025-01-09 - Future Planning)
- **User Request:** Plan self-hosting and LLVM backend integration
  1. Keep current C-based approach
  2. Add LLVM task (after self-hosting working)
  3. Add self-hosting task (must be added eventually)
  4. "lets plan this properly before doing coding"
- **Created task/task-10-self-hosting-plan.md**
  - Comprehensive 12-phase plan (40-60 hours)
  - Prerequisites: file I/O, collections, string manipulation
  - Bootstrap process: Python v1 → Fusion v2 → v3 (self-compile)
  - Detailed porting strategy for all compiler components
- **Created task/task-11-llvm-backend-plan.md**
  - Comprehensive 13-phase plan (30-40 hours)
  - Replace C code generator with LLVM IR backend
  - Type mapping, optimization pipeline, performance benchmarking
- **Updated taskSummary2.md** with Tasks 10 & 11
  - Task 10.1: Planning complete (1/12 phases)
  - Task 11.1: Planning complete (1/13 phases)
  - Overall progress: 14/57 tasks complete (30%)
- **Next Action:** Task 7 - Git Integration & GitHub Setup (next in sequence)

### Session 20 (2025-01-09 - Git Integration)
- **Executed Task 7: Git Integration & GitHub Setup - 94% COMPLETE**
  - Task 7.1: Created .gitignore (excludes .exe, .c, cache, IDE files)
  - Task 7.2: Initialized local Git repository
    - Initial commit: e62d2cf "Initial commit - Fusion compiler MVP complete"
    - 153 files, 61,458+ lines of code
  - Task 7.3: Connected to GitHub
    - Repository URL: https://github.com/EmileAvatar/fusion-lang.git
    - Renamed branch: master → main
    - Pushed successfully to origin/main
  - Task 7.4: Verified remote backup
    - Branch tracking configured: main → origin/main
    - All commits pushed successfully
    - .gitignore working (executables, cache excluded)
- **Security Audit Completed**
  - No credentials, API keys, or sensitive information found
  - Configuration files reviewed and safe
  - Personal email only in git config (standard practice)
- **Completed Task 7.4.4: README.md Comprehensive Update**
  - Enhanced project description: Fusion as agnostic, configurable language
  - Expanded Features section with MVP complete vs. planned features
  - Added comprehensive Contributing section with PLAN FIRST methodology
  - Added MIT License (recommended for open-source)
  - Added Author section: Emile M Steenkamp
  - Added Contributors section with AI transparency:
    - Claude AI (Opus 4.5, Sonnet 4.5) - compiler implementation
    - ChatGPT (GPT-4) - language design consultation
  - Updated acknowledgments with language inspirations
  - Fixed repository URL: https://github.com/EmileAvatar/fusion-lang
  - Updated project structure to reflect actual directories
  - Enhanced Development Status with accurate test results (1,041 passing)
- **TASK 7: GIT INTEGRATION & GITHUB SETUP - 100% COMPLETE ✅**
- **Updated Task Progress Table** (Task 7: 4/4 complete, Overall: 18/57 complete, 32%)
- **Next Action:** Task 8 - const Keyword Implementation (8 sub-tasks, 4-6 hours estimated)

### Session 21 (2026-08-04 - Git History Scrub, Review Intake & README Refresh)
- **Removed personal email from public git history**: rewrote all 12 commits with
  git-filter-repo (redacted email from a README commit, remapped author/committer emails to
  the GitHub noreply address), backed up original history, force-pushed to origin/main
- **Repo made public by user**; verified via GitHub API that the repo is public (200) and
  that a commit-search for the email string returns zero results
- **Committed previously-untracked files**: const keyword debug/lexer/semantic test scripts
  and language-planning notes (commit 1067556)
- **Read two ChatGPT reviews** (Notes/02/Readme todo.md - README reframing copy; Notes/02/
  notes.md - full architecture review of lexer/parser/semantic/codegen/roadmap)
- **Added Task 12: Compiler Architecture Hardening** (Typed AST, codegen module split,
  InterpolatedString refactor, scoping ADR, memory model spec draft) - sub-tasks proposed
  only, NOT YET APPROVED for implementation
- **Flagged for Task 9**: recommended (not forced) to sequence after/alongside Task 12
- **Flagged for discussion**: review's suggestion to do LLVM before self-hosting, which
  contradicts the existing Session 19 decision - left Task 10/11 order unchanged
- **Verified ground truth before touching docs**: ran full test suite (1,057 passed, 8
  skipped - not the stale 1,041/10 figure sitting in README/CLAUDE.md), confirmed
  `examples/const_demo.fusion` already exists
- **Rewrote README.md**: applied the review's repositioning (Code as Infrastructure, Why
  Fusion Exists, Syntax Without Lock-In, elevator pitch) ahead of the existing technical
  content; moved const out of "Planned Features" into "Complete", added const example
  reference, corrected test counts to 1,057 passed / 8 skipped throughout
- **Did NOT touch**: CLAUDE.md's stale "const not yet implemented" note or the EBNF/language
  spec (Task 8.6 items) - out of scope for this session, still outstanding
- **Next Action:** User to review/approve Task 12 sub-tasks before any implementation begins;
  Task 8.6-8.8 (docs/verification/commit for const) still open

### Session 22 (2026-09-13 - HIDL Intake)
- **Moved** `Fusion_Hardware_Interface_Definition_Language_HIDL.md` from repo root into
  `files/`, alongside the other spec documents (fusion-language-spec.md, fusion.ebnf, etc.)
- **Reviewed the HIDL vision doc** (43 sections - hardware-supplier-writes-spec-once,
  tooling-generates-typed-API-per-language). Findings:
  - Strong, well-organized concept; register/bitfield/access-mode modeling (write-one-to-clear
    etc.) and the HIDL = hardware truth / Interface = promise / Trait = behavior split are the
    most valuable ideas
  - Matches real prior art worth studying: ARM CMSIS-SVD, IP-XACT, Zephyr devicetree - not a
    novel problem space
  - Gaps flagged: no concrete grammar (all examples explicitly illustrative per the doc's own
    section 6), very large surface area for one "future feature" (DMA/interrupts/security/
    simulator/IDE each is its own subsystem), no interaction defined yet with the planned
    `Unique`/`Shared`/`Weak` memory model
  - Recommended sequencing after Task 12 (Typed AST), since hardware range/state compile-time
    checks need the same `inferred_type` infrastructure Task 12 introduces
- **User confirmed:** blocked for now, eventual future integration - added as **Task 13** with
  proposed-only sub-tasks (13.1-13.9), same "not yet approved for implementation" status as
  Task 12. No code or grammar work started.
- **Updated Overall Progress table:** 23/75 tasks (31%) - denominator grew from adding Task 13's
  9 proposed sub-tasks; completed count unchanged
- **Next Action:** No action on Task 13 until Task 12 is approved and complete, and the user
  re-opens Task 13 for v1 scoping. Task 12 approval and Task 8.6-8.8 (const docs/commit) remain
  the actual next actionable items.

### Session 23 (2026-09-13 - Task 8.6-8.8 Closeout)
- **Task 8.6 (Documentation):** fixed `files/fusion-language-spec.md`'s Constants section,
  which still showed a stale `name: type = value` syntax that never matched the implemented
  type-first grammar - rewrote examples to `const int X = 1` style and added notes on current
  scope (function-local only, explicit type required, no class-level consts). Fixed
  `CLAUDE.md`'s "const keyword not yet implemented" limitation (moved to Current Features).
  Checked README.md and `files/fusion.ebnf` - both already had accurate const coverage from
  Session 21/earlier implementation work, so left unchanged.
- **Task 8.7 (Verification):** full suite 1057 passed / 8 skipped. Found
  `tests/verify_examples.py` had no expected-output entry for `const_demo`, so its output was
  being silently skipped rather than checked (6/7 "matches", not 7/7) - added an expected-output
  entry; re-ran and got 7/7 compile, run, and match. Regenerated verification_report.md.
- **Task 8.8 (Git):** deliberately did NOT run a blanket `git add .` - the working tree also had
  unrelated pending changes (deleted Notes/*.pdf and Notes/*.md files, new untracked Notes/01/
  and Notes/02/ folders, and the HIDL file moved into files/ from the previous session) that
  have nothing to do with const. Staged only the six docs/verification files, committed as
  `3e67816` "docs: Close out Task 8.6-8.8 - const keyword documentation and verification"
  (broadened from the stale placeholder message "feat: Add const keyword support" written when
  8.8 was first planned, since the actual diff was documentation, not new code), pushed
  fast-forward to origin/main with no conflicts.
- **TASK 8: const KEYWORD - 100% COMPLETE**
- **Left untouched, still pending in the working tree:** the Notes/ deletions/additions and the
  HIDL file relocation - these are separate from Task 8 and need their own review/commit
  whenever the user wants to address them.
- **Next Action:** Task 8 fully closed. Remaining open items: Task 12 approval (Architecture
  Hardening, blocks Task 9 and Task 13), and the unrelated pending Notes/ changes sitting
  uncommitted in the working tree.

### Session 24 (2026-09-13 - Git Cleanup, Task 12 Review Gap Check, HIDL Reframing)
- **Notes/ cleanup:** confirmed with the user that the "deleted" Notes/*.pdf and .md files (plus
  root's "Readme todo.md") were never actually lost - they'd been reorganized into Notes/01/ and
  Notes/02/ subfolders in an earlier session. Added `Notes/` to `.gitignore` (personal working
  scratch space for point-in-time AI reviews, not project documentation) and committed the
  resulting removals as `351026d`. Working tree confirmed clean afterward except the HIDL file.
- **Cross-checked `Notes/02/notes.md` (the ChatGPT architecture review) against Task 12** per
  the user's standing instruction to log any review findings not yet task-tracked. Found three
  recommendations from the review with no corresponding task item:
  1. A dedicated Fusion IR layer between Typed AST and backends (review section 8) - ties into
     the already-flagged Task 10/11 ordering question but is a distinct design point on its own
  2. Lowering `print()`/stdlib calls through a runtime API instead of special-casing each
     builtin in codegen (review section 10)
  3. A project-level language configuration system (indentation, safety mode, backend target) -
     notable because this is Fusion's own marketed core concept (see CLAUDE.md "Core Concept")
     but currently hardcoded in the lexer instead of configurable, and wasn't tracked anywhere
  - Added these as Task 12.10, 12.11, 12.12 (proposed-only, same as the rest of Task 12); also
    added the review's doc-hierarchy suggestion (Language Spec -> ADRs -> Roadmap -> Tasks) as
    a bullet under 12.8. Task 12's sub-task count grew from 9 to 12; overall total 75 -> 78.
- **HIDL scope correction:** user clarified HIDL is a standalone, language-agnostic hardware
  framework, not a Fusion-specific concept - Fusion's actual work is a future "HIDL module"
  that consumes an independently-specified `.hidl` file. The source doc's title and Section 1
  originally described HIDL as being "for the future Fusion programming language", which
  overstated the coupling. Added a scope-note callout at the top of
  `files/Fusion_Hardware_Interface_Definition_Language_HIDL.md` and reworded Task 13 (retitled
  "HIDL Module", goal/why-this-exists/13.1/13.4 reworded) to reflect that HIDL's grammar and
  parser are their own standalone effort, and only the Fusion-side consumer belongs on this
  compiler's roadmap.
- **Committed the HIDL doc** (previously sitting untracked since it was moved in Session 22) -
  the user asked for this explicitly, calling it important future work.
- **Next Action:** Task 12 approval remains the key blocker (now 12 sub-tasks, unblocks Task 9
  and Task 13). No other pending working-tree changes remain.

### Session 25 (2026-09-13 - Archive Completed Tasks)
- **User request:** move completed task sections out of `taskSummary2.md` into a new
  `taskSummaryArchive.md`, to keep the active tracker small (token usage), and add the practice
  to CLAUDE.md as a standing rule.
- Created `task/taskSummaryArchive.md` (alongside the existing `task/taskSummary.md` MVP
  archive) and moved Tasks 5, 6, 7, and 8 - full sub-task detail, success criteria, and
  deliverables - there verbatim. Corrected one stale field while moving it: Task 6's `Status`
  field still said "Not Started" despite every sub-task being checked off and the Overall
  Progress table already showing it Complete - fixed to `Complete` in the archive copy.
- Replaced that block in `taskSummary2.md` with a 6-line pointer + status list; left the
  Overall Progress table and Working Notes (session history) in place, since those still cover
  active/recent context, not just completed-task detail.
- File size: `taskSummary2.md` dropped from ~1,220 lines to ~900 lines.
- Added CLAUDE.md Rule 3 bullet documenting the archiving practice (see CLAUDE.md itself).
- **Next Action:** proceed to Task 9 (Array Support) per user's request - see Task 9 section
  below. Flag before starting: Task 9's own header already carries a standing recommendation
  (from the same architecture review as Task 12) to sequence Task 12 before or alongside Task 9,
  and Task 12 is still unapproved - raised to the user rather than silently started or blocked.

### Session 26 (2026-09-13 - Task 12 Core Typed AST Implementation)
- **User approved a scoped subset of Task 12** ("Core Typed AST only": 12.1-12.4 + 12.9) rather
  than the full 12-item list, to unblock Task 9 without a multi-week design detour through the
  five design-only items (12.6/12.7/12.10/12.11/12.12) and the non-blocking cleanup items
  (12.5 codegen split, 12.8 doc sync).
- **Investigated the actual code before planning implementation** (not just the review's
  pseudocode) and found the real shape was better/simpler than expected:
  - `TypeChecker.visit()` already computes the correct type for every expression while
    validating it - it was being thrown away, not missing. Fix was a one-line hook in the
    dispatcher, not a new type-inference system.
  - The review's suggested `class Expr(ASTNode): inferred_type: TypeNode | None` doesn't work
    as literal Python - dataclass field-ordering rules block a defaulted field on a common base
    when subclasses add their own required fields. Used a trailing optional field on each of
    the 7 expression classes instead.
  - The interpolation "parallel array" bug source is one step earlier than the review implied:
    the lexer already emits a safe ordered/tagged sequence; the *parser* was the one splitting
    it into two parallel arrays on the AST node. Fixed at that exact point.
  - `print()` is declared as accepting only a `string` parameter in the symbol table, so the
    review-quoted `%s` fallback in `_generate_print_call` was already dead code for any
    semantically-valid program - only reachable from codegen-only unit tests that skip semantic
    analysis. Fixed anyway (defensive correctness + those unit tests exercise it directly).
- **Implemented 12.1-12.4 + 12.9:**
  - `src/parser/ast_nodes.py`: added `inferred_type: Optional[TypeNode] = None` to
    `LiteralExpr`, `IdentifierExpr`, `BinaryExpr`, `UnaryExpr`, `CallExpr`, `LambdaExpr`; added
    new `StringTextPart`/`StringExprPart` classes; `InterpolatedStringExpr` now holds a single
    ordered `segments` list instead of parallel `parts`/`expressions` arrays
  - `src/parser/parser.py`: rewrote `parse_interpolated_string_from_parts` to build `segments`
    directly from the lexer's already-ordered tuples; deleted `parse_interpolated_string`, a
    dead method (never called, referenced a `token.interpolation` JSON shape that's never
    populated)
  - `src/semantic/name_resolver.py`, `src/semantic/type_checker.py`: updated to iterate
    `segments` instead of `expressions`; `TypeChecker.visit()` now writes the computed type
    back onto `node.inferred_type` for every expression
  - `src/codegen/c_generator.py`: added `_format_specifier_for_expr()` (reads `inferred_type`,
    maps int->%d, float/double->%f, string->%s, char->%c, bool->%d, raises a clear internal
    error if the type is missing/unrecognized instead of guessing); rewired
    `_generate_print_call`, `visit_InterpolatedStringExpr`, and `_generate_interpolated_print`
    to use it; de-duplicated the latter two into one shared `_build_interpolation_format()`
    helper (they were near-identical)
  - Updated ~30 test call sites across `tests/test_ast_nodes.py`, `tests/test_type_checker.py`,
    `tests/test_codegen_expressions.py` to the new `segments` shape; added 3 new regression
    tests covering float/string interpolation, direct non-string `print()` args, and the
    missing-`inferred_type` error path (`tests/test_parser_expressions.py`'s old interpolation
    tests were already commented out/dead - left untouched, out of scope)
- **Verified for real, not just unit tests:** compiled an ad-hoc snippet interpolating a float,
  bool, and string together - got `printf("Pi is %f, flag is %d, name is %s\n", pi, flag,
  name)` and correct runtime output. Confirms the fix is real: before it, all three would have
  used `%d`, silently reinterpreting the float's bit pattern as an int and the string's pointer
  as a raw integer.
- **Full verification:** `pytest tests/` - 1060 passed, 8 skipped (up from 1057 passed; 3 new
  tests, nothing weakened). `python tests/verify_examples.py` - 7/7 compile, run, and match.
- **Deferred, not started:** 12.5 (codegen module split), 12.6 (scoping ADR), 12.7 (memory
  model spec), 12.8 (doc sync pass), 12.10-12.12 (IR layer, stdlib lowering, project config -
  all design-only, no code changes made or implied by this session's work)
- **Task 9 unblocked:** its standing "do Task 12 first" recommendation is now satisfied for
  arrays' purposes - array type-checking/codegen can read `inferred_type` directly.
- **Next Action:** proceed to Task 9 (Array Support) planning - the user's original request,
  now actually unblocked rather than just flagged.

### Session 27 (2026-09-13 - Task 9: Array Support v1)
- **User request:** "lets do task 9 plz"
- **Scoped before coding, per Task 9.1's own checklist item ("Get user approval on syntax")**:
  proposed fixed-size, local-variable-only arrays with `len(arr)`; asked one open question
  (`len(arr)` vs `arr.length`)
- **User asked for both `len(arr)` AND `arr.length`, with `arr.length` null-aware** (warn/crash
  depending on provability, `?.`/`?[` returning 0 silently) - this doesn't fit a fixed-size C
  array (can't be null) and needs member-access parsing (doesn't exist), a null-flow-analysis
  pass, and a real nullability/memory-model decision (Task 12.7 territory). Flagged this
  explicitly rather than improvising a memory-model decision inline. User agreed to ship plain
  arrays now and track nullability separately - see new **Task 14** below.
- **Investigated the actual code before implementing** (mirroring the Task 12 approach):
  confirmed `LBRACKET`/`RBRACKET` tokens already existed and were already tokenized (just
  unused downstream); confirmed zero array support existed anywhere else (`sum_array.fusion`
  doesn't use real arrays, just sums a `range()`); found `files/fusion.ebnf` already had a
  draft array grammar to build from; found `TypeChecker.visit_CallExpr` already had a
  precedent (`range()`'s special-casing) for a builtin that needs bespoke argument checking
  rather than a fixed `FunctionType` signature - reused that exact pattern for `len()`.
- **Implemented (v1):**
  - AST: `ArrayType(element_type, size)`, `ArrayLiteralExpr(elements)`, `IndexExpr(array,
    index)` in `src/parser/ast_nodes.py`
  - Parser: `parse_type()` recognizes `int[]`/`int[5]` (integer-literal sizes only,
    multi-dimensional rejected with a clear error); array literals in `parse_primary()`;
    indexing folded into `parse_call()`'s postfix loop (renamed in spirit - now handles both
    `(...)` and `[...]` chained); array-element assignment needed zero extra parser work
  - Semantic: `ArrayType` added to `types_equal`/`types_compatible`/`type_to_string`;
    `visit_ArrayLiteralExpr` (element-type inference with numeric promotion),
    `visit_IndexExpr` (array/int-index validation); `visit_VarDeclStmt` resolves size from an
    explicit `[N]`, an initializer, or both (must agree); `visit_AssignmentStmt` split into
    identifier- and index-target paths, explicitly rejecting whole-array reassignment (a
    plain C array isn't reassignable that way) and enforcing const on elements; `len()`
    registered as a builtin and special-cased like `range()`; arrays rejected as function
    parameters/return types with a clear error (`register_function` in name_resolver.py)
  - Codegen: `map_type` handles `ArrayType`; `visit_VarDeclStmt` emits real C array
    declarators (`int arr[3] = {1, 2, 3};`, size after the name, `{0}` zero-init when no
    literal); `visit_ArrayLiteralExpr` emits C brace-init (only reachable as an initializer,
    per the semantic rules above); `visit_IndexExpr` emits plain `arr[i]`;
    `visit_AssignmentStmt` generalized from `target.name` to `self.visit(target)` so index
    targets work through the same path; **`len(arr)` compiles directly to the array's
    resolved size as an integer literal - no runtime call at all**, since sizes are always
    known at compile time in v1
- **Verified for real, not just unit tests:** compiled an ad-hoc program using array literals,
  explicit-size arrays, element read/write, a function returning a sum over a local array, and
  `len()` inside a `range()` bound - confirmed correct generated C and correct runtime output.
  Manually tested and confirmed all 7 rejection paths fire with clear messages: whole-array
  reassignment, const-element assignment, size mismatch, element type mismatch, indexing a
  non-array, missing size with no initializer, and arrays as function parameters.
- **Found and worked around a pre-existing, unrelated lexer limitation while testing:** string
  interpolation (`"{...}"`) only accepts a bare identifier inside `{}` - `{arr[0]}` or `{x+1}`
  fail to lex ("Expected } to close interpolation"). This predates Task 9 entirely (confirmed
  via the interpolation lexer's `isalnum()`-only identifier scan) and matches an already-dead,
  already-commented-out test in `tests/test_parser_expressions.py`. Not fixed here - noted as a
  pre-existing limitation, worked around in the example program with temp variables
  (`int first = scores[0]; print("{first}")`).
- **Tests:** added `tests/test_array_semantic.py` (22 tests) and `tests/test_array_codegen.py`
  (8 tests, including a full GCC compile-and-run round trip). Full suite: 1090 passed, 8
  skipped (up from 1060). Added `examples/arrays_demo.fusion`; `verify_examples.py`: 8/8.
- **Documentation:** new "Arrays" section in `files/fusion-language-spec.md` (cross-referenced
  against the spec's existing "Array Safe Navigation"/"Null Safety" sections, which already
  described the nullable design Task 14 will build toward); annotated `files/fusion.ebnf`'s
  array/postfix grammar with implemented-vs-aspirational notes; updated CLAUDE.md and README.md
  (Features, Example Programs, Development Status, Test Results) - also caught and fixed a
  small test-count drift left over from Task 12 (README's Code Generation Tests line was still
  126, three short of the actual 129 after Task 12's own additions, since README wasn't touched
  in that commit - fixed to the current accurate 137 while updating this line anyway)
- **Added Task 14** ("Nullable Arrays & Safe Navigation") - proposed-only, blocked on Task
  12.7, same convention as Tasks 12/13 - capturing the null-safety design the user actually
  asked for, scoped properly instead of bolted onto Task 9
- **TASK 9: ARRAY SUPPORT (v1) - 100% COMPLETE**
- **Next Action:** Task 9 is done and shipped. Remaining open items: Task 12 approval for its
  deferred items (12.5-12.8, 12.10-12.12), Task 14 blocked on Task 12.7, Task 13 blocked on
  Task 12.

### Session 28 (2026-09-13 - Task 12 Remaining Items, Starting with 12.8)
- **User request:** "lets do the next task" - clarified via question that "next" was ambiguous
  (Task 12's remaining items vs. Task 10/11 by number); user confirmed finishing Task 12
  first, in the proposed order: 12.8 (docs) -> 12.5 (codegen split) -> 12.6 (scoping) -> 12.7
  (memory model) -> 12.12 (project config) -> 12.10 (IR layer) -> 12.11 (stdlib lowering)
- **Executed 12.8 (Documentation Sync Pass) - COMPLETE.** Found real, meaningful staleness
  beyond what Tasks 8/9 already kept current:
  - `CLAUDE.md` claimed the repo was PRIVATE (it went public 2026-08-04) - verified via GitHub
    API (`"private": false`) and fixed; its "CURRENT STATUS"/"Next Steps" sections were still
    dated 2025-12-14, describing the FizzBuzz bug as unresolved and Tasks 5+ as not started -
    rewrote both
  - `README.md`: a "126 tests" figure never got updated after Task 12's own new codegen tests
    (should have been 129, is now correctly 137 after Task 9's additions too) - fixed while
    already touching that line for Task 9's numbers
  - `files/fusion-summary.md`, `files/README.md`, `files/fusion-planning.md`: all three
    predate the compiler entirely and still claimed `Compiler: Not Started 0%` - actively
    misleading now, not just outdated. Added historical-snapshot disclaimers to each rather
    than rewriting every stale cell (matches how `task/taskSummary.md` is already frozen and
    labeled ARCHIVED)
  - `task/Revisit.md`: "29 failing tests" (2025-12-07) is now 0 - updated the summary and
    marked the historical detail section resolved (kept for its resolution-path value, not
    deleted); also fixed a broken relative link to `taskSummary.md` left over from that file's
    move into `task/`
  - Verified test counts precisely rather than guessing: cross-checked README's
    lexer/parser/semantic/codegen category breakdown against actual `pytest --collect-only`
    groupings (251 = 198 parser-file tests + 53 `test_ast_nodes.py` tests, etc.) to confirm
    exactly where each category's count comes from, not just trust prior numbers
- **Executed 12.5 (C Codegen Module Split) - COMPLETE.** Split `src/codegen/c_generator.py`
  (962 lines) into `c_types.py` (`TypeMapperMixin`), `c_names.py` (`mangle_function_name`),
  and `c_runtime.py` (`RuntimeLoweringMixin`), leaving `c_generator.py` at 773 lines holding
  AST traversal, statements/declarations, and output management. Used mixin classes (not
  standalone functions) for the two pieces that need `self` - `map_type()` recurses on
  itself, and the print/len/interpolation helpers call `self.visit(...)` - and confirmed via
  grep that existing tests call several of these (`map_type`, `visit_InterpolatedStringExpr`,
  `_generate_interpolated_print`) directly as instance methods, which mixins preserve exactly
  and standalone functions would have broken. Public API (class name, every method name and
  signature) is unchanged - purely an internal reorganization. Verified: full suite still
  1090 passed/8 skipped (identical, since this added/removed no tests), `verify_examples.py`
  still 8/8.
- **Executed 12.6 (Scoping Decision) - COMPLETE, and actually implemented, not left as a
  paper ADR.** Presented function-level vs. block-level scoping tradeoffs; user chose
  block-level (lexical) scoping, matching the review's original recommendation ahead of
  Task 12.7's memory model.
  - **Verified this was a real bug fix, not just a style choice**, before implementing:
    compiled `if cond { int x = 10 } print(x)` and confirmed semantic analysis said "no
    errors" while GCC then failed with `'x' undeclared` - the C output was already
    natively block-scoped via its own `{ }` braces; only the semantic analyzer was
    wrongly claiming function-wide visibility.
  - Implemented via a `scope` field on `BlockStmt`/`ForStmt` (populated by NameResolver,
    reused by TypeChecker via a new `SymbolTable.enter_existing_scope()` - works because
    `Scope.parent` is a fixed object reference, so lookup_recursive is correct regardless
    of which pass is walking).
  - Verified two subtle rules against real GCC before assuming them, rather than
    guessing: (1) a function's top-level body must share its parameter scope directly, not
    nest below it (redeclaring a parameter at that level is itself a C error) - handled
    via a `new_scope=False` flag on `resolve_block()`; (2) a for-loop's body CAN shadow
    the loop's own iteration variable in real C, confirmed by compiling a minimal repro,
    so for-bodies do get their own nested scope.
  - Found and fixed a second bug surfaced by this change:
    `control_flow_validator.py`'s `validate_conditions()` re-checks conditions via the
    type checker *after* the main walk already unwound its scopes, which broke
    loop-variable lookups inside conditions - fixed by having it re-enter the relevant
    `.scope` too.
  - Updated 5 tests that asserted the old (now-incorrect) function-scoping behavior;
    added 6 new regression tests locking in shadowing, the original bug's rejection, and
    the parameter-redeclaration rule.
  - Full suite: 1095 passed, 8 skipped (up from 1090). `verify_examples.py`: 8/8.
  - Committed and pushed as `24db585` "feat: Task 12.6 - switch to block-level (lexical)
    scoping".
  - Flagged one known follow-up, not fixed: `LambdaExpr` with a `BlockStmt` body doesn't
    get its scope reused correctly - safe to defer since that path isn't functionally
    complete anyway (codegen still stubs lambdas as `/* <lambda> */`).
- **Next Action:** proceed to 12.7 (memory model - `Unique`/`Shared`/`Weak` semantics),
  the next design-decision item in the confirmed order.
- **Executed 12.7 (Memory Model Semantics) - COMPLETE, design doc only, no code change (as
  scoped).** Presented three tradeoff questions (`Unique<T>` move semantics, `Shared<T>`
  refcount atomicity + cycle handling, `Weak<T>` upgrade behavior); user chose the
  recommended option on all three:
  - `Unique<T>`: plain assignment is a compile error, explicit `.move()` required
    (rejected C++-style implicit move) - and use-after-move should share one analysis
    pass with Task 14's null-flow tracking later, not a separate mechanism.
  - `Shared<T>`: refcount is always atomic, never configurable per project (rejected
    Fusion's own "agnostic per-project config" pattern here deliberately, to avoid two
    runtime code paths before there's a concrete need); no automatic cycle detection,
    documented as a permanent accepted limitation (`Weak<T>` is the required way out).
  - `Weak<T>`: `.lock()` returns a nullable `Shared<T>?`, caller must check - never a
    silent crash - chosen so Fusion has one null-handling story shared with Task 14's
    array work, not a different rule per type.
  - Wrote all three decisions with rationale directly into
    `files/fusion-language-spec.md`'s existing Memory Management section (had draft
    Unique/Shared/Weak examples from the original pre-compiler planning phase already -
    resolved their ambiguous parts rather than replacing the section), plus a top-of-
    section status note flagging this as decided-but-not-yet-implemented.
  - Confirmed via source search that `Unique`/`Shared`/`Weak` remain lexer-keyword-only
    today (no parser/semantic/codegen handling anywhere in `src/`) - nothing to test or
    regress, matches this sub-task's "design doc, no code change" scope exactly.
  - This unblocks Task 14 (Nullable Arrays & Safe Navigation) to be scoped/approved
    whenever the user wants to pick it up - noted its `Weak<T>` and array-nullability
    null-checks should share one analysis design, not be built twice.
- **Next Action:** proceed to 12.12 (project-level language configuration system), the
  next item in the confirmed order (12.12 -> 12.10 -> 12.11 remain).
- **Executed 12.12 (Project-Level Language Configuration System) - COMPLETE, implemented,
  not just designed.** Presented three tradeoff questions (config format, lookup location,
  how much to actually implement now); user chose the recommended option on all three:
  - Format: TOML via an optional `fusion.toml`, parsed with Python 3.11's stdlib `tomllib`
    (zero new dependency) - **raises the project's minimum Python version to 3.11**,
    updated everywhere README.md stated 3.10+.
  - Lookup: source file's own directory, then cwd - no parent-directory walk, since Fusion
    has no multi-file project concept yet.
  - Scope: actually wired `[indentation]` (`tab_width`/`allow_mixed`) into the lexer - the
    real gap this task existed to close (`src/lexer/lexer.py` used to hardcode both) - and
    documented `[safety]`/`[backend]` as parsed-and-validated-but-not-yet-enforced,
    matching how `Unique`/`Shared`/`Weak` are already handled.
  - New `src/config/project_config.py` (`ProjectConfig`, `load_project_config()`,
    `find_config_file()`, `ProjectConfigError`); `Lexer.__init__` gained optional
    `tab_width`/`allow_mixed` params (old hardcoded values as defaults, so every existing
    call site/test is unaffected); `main.py` loads config before constructing the lexer,
    catches `ProjectConfigError` as a clean one-line error instead of a traceback.
  - Verified for real, not just unit-tested: a file with one line mixing spaces and a tab
    compiles with only a warning by default, but fails to compile with a clear error once
    a `fusion.toml` with `allow_mixed = false` sits next to it - the config genuinely
    changes compiler behavior end to end. Also verified a malformed `fusion.toml` fails
    cleanly rather than crashing.
  - 24 new tests (`tests/test_project_config.py`); `examples/project_config_demo/` added
    as a permanent manual demo (kept out of `examples/`'s top level specifically so its
    `fusion.toml` can't silently affect the other 8 examples - confirmed `verify_examples.py`
    still reports 8/8 after adding it).
  - Full suite: 1119 passed, 8 skipped (up from 1095). `verify_examples.py`: 8/8.
  - Documentation synced: `files/fusion-language-spec.md` (new "Project Configuration"
    subsection with full schema + rationale), `CLAUDE.md`, `README.md` (including the
    Python 3.10 -> 3.11 requirement bump in all three places it was stated).
- **Next Action:** proceed to 12.10 (Fusion IR layer - design consideration), the next
  item in the confirmed order (12.10 -> 12.11 remain to close out Task 12).
- **Executed 12.10 (Fusion IR Layer) - COMPLETE, decision recorded, no code change
  (deferred).** Presented a three-way tradeoff (defer until Task 11 starts / adopt a full
  IR now / adopt a thin contract-only IR now); user chose to defer.
  - Rationale: only one backend (C) exists today - an IR layer would have no real second
    consumer to validate against, and would mean reworking the just-cleanly-split (Task
    12.5) C codegen for no immediate capability gain. Accepted the opposite risk (Task 11
    might copy the C backend's AST-walking pattern and need a costlier retrofit later)
    rather than pay the IR-design cost now on a single-backend compiler.
  - Added a "Revisit at kickoff" note to `task/task-11-llvm-backend-plan.md` so this gets
    re-opened with real LLVM requirements in hand before any LLVM codegen is written,
    rather than silently forgotten.
  - Left the separately-flagged Task 10/11 ordering question (LLVM/IR before self-hosting)
    untouched - still open, not part of this decision.
  - No code changed - matches this sub-task's design-consideration scope exactly.
- **Next Action:** proceed to 12.11 (print()/stdlib runtime lowering - design
  consideration), the last remaining item to close out Task 12.
- **Executed 12.11 (print()/Stdlib Runtime Lowering) - COMPLETE, decision recorded, no
  code change (deferred).** Same three-way tradeoff shape as 12.10 (defer / lightweight
  registry refactor now / full runtime-API design now); user chose to defer again.
  - Checked the actual code before reasoning about it, rather than assuming: exactly 2
    builtins are special-cased in `visit_CallExpr` (`print`, `len`); `range()` isn't a
    runtime call at all, it's consumed structurally inside `visit_ForStmt`. Confirmed via
    source search that `import` has zero parser support (lexer keyword only) - there is no
    stdlib call mechanism to lower yet.
  - Updated `src/codegen/c_runtime.py`'s module docstring, which had flagged this exact
    open question since Task 12.5, to record the decision instead of leaving it open.
  - No code changed - matches this sub-task's design-consideration scope.
- **TASK 12 IS NOW FULLY COMPLETE (12/12 sub-tasks), 2026-09-13.** Summary of the whole
  task across both sessions: Typed AST (12.1-12.4, 12.9) closed the "codegen guesses
  types" architectural gap that caused the FizzBuzz bug; C codegen module split (12.5);
  block-level scoping (12.6, which fixed a second real bug along the way); memory model
  semantics for `Unique`/`Shared`/`Weak` (12.7, decided and documented, not yet
  implemented); documentation sync (12.8); project configuration via `fusion.toml`
  (12.12, implemented for indentation); and two deliberately deferred design decisions
  with rationale recorded for their actual trigger points (Fusion IR layer at Task 11
  kickoff, 12.10; stdlib runtime lowering once `import`/fusionlib work is scoped, 12.11).
  This also clears Task 13's blocker (still needs its own scoping approval) and, combined
  with 12.7, both of Task 14's original blockers.
  - **Archiving (per CLAUDE.md Rule 3):** Task 12's full section (all 12 sub-tasks, Why
    This Task Exists, Success Criteria, Deliverables, Open Question) has been moved
    verbatim to `task/taskSummaryArchive.md`. This file keeps only the short pointer below
    and the Overall Progress table row.
- **Next Action:** Task 12 is complete. Remaining open items: Task 13 (HIDL module) and
  Task 14 (nullable arrays) are both unblocked but still need their own scoping approval
  before any implementation begins (per Rule 1) - or begin Task 10/11 (self-hosting/LLVM),
  both already "planning complete" - whichever the user wants to take on next.
- **Housekeeping (2026-09-13):** archived Task 9 (per CLAUDE.md Rule 3 - it was complete
  but its full section had been left in this file); reordered Tasks 9/10/11/12/13/14 into
  numerical order (Task 14 had drifted to sit between 9 and 10 across sessions - purely a
  position change, no task renumbered); added **Task 15: Deferred Decisions Revisit List**
  - a checklist capturing every "defer this, revisit later" point that Task 12's work
  produced (Fusion IR layer, stdlib runtime lowering, the LambdaExpr scope bug, the Task
  10/11 ordering question, memory-model implementation not being tracked anywhere, fusion.toml
  safety/backend keys not being enforced, and lexer warnings never reaching the user) - each
  with its own trigger condition, so none of them stay buried in old commit messages or
  archived prose once Task 12 itself is no longer active in this file.
- **Next Action:** see the bottom-of-file Next Action line, updated to match all of the
  above.
- **Added CRITICAL RULES Rule 5 and Task 16 (Example Program Coverage), per user request
  (2026-09-13):** "add more examples in fusion examples for each new feature... so that
  users have more examples to work with." Rule 5 makes shipping an example part of closing
  out any feature task going forward, not an afterthought. Task 16 is the concrete
  checklist: 16.1 (a comprehensive control-flow example covering `while`/`for`/`break`/
  `continue` - buildable now, since the feature already exists and only `break`/`continue`
  currently have zero example coverage) plus six more items (16.2-16.7: classes/structs/
  interfaces/enums, generics, multithreading, error handling/try-catch, the Unique/Shared/
  Weak memory model, and the module system) - all six explicitly blocked, since none of
  those features are implemented yet and none currently have a task tracking their
  implementation either (flagged as its own gap on each relevant sub-item, not just "not
  done yet"). Logged only, not implemented - per Rule 1, implementation of 16.1 (the one
  unblocked item) awaits the user's go-ahead.
- **Next Action:** offer to build 16.1 (`examples/control_flow_demo.fusion`) now, since
  it's the only Task 16 item not blocked on an unbuilt feature; everything else in Task 16
  waits on its own feature being scoped and built first.
- **Added Task 17 (Mutable vs. Fixed Strings, Templated Fixed Strings & String Pooling),
  per user request (2026-09-27):** `m"..."` (explicit, though a plain literal is already
  mutable) vs. `f"..."` (fixed/immutable - "mutating" methods return a new value, never
  change the original) vs. templated fixed strings, the genuinely new part - a fixed string
  holding unresolved `{@1}`/`{@2}` placeholders becomes a reusable, callable template
  invoked later with fresh arguments each time (deferred resolution, distinct from Fusion's
  existing `{@N}` interpolation which resolves immediately at the call site). Also: strings
  are not pooled by default (each stored only where declared), pooling proposed as an
  opt-in `fusion.toml` `[strings]` setting to enable only after profiling shows real
  benefit; and a security note that plain strings are the wrong type for passwords/secrets
  (can't be reliably zeroed, pooling could retain copies) - flagged for a future
  `fusionlib.Crypto` secure-storage type, not scoped here.
  - Logged in both places per the user's explicit request: full design write-up in
    `FutureFeatures.md` (under "Type System Enhancements"), tracked task with 5 proposed
    sub-tasks here. Logged only, not implemented - per Rule 1, needs scoping approval
    before any work begins, same as Tasks 13/14/16.
- **Next Action:** Task 17 is logged only - no implementation expected until the user
  re-opens it for scoping. 16.1 remains the nearest actionable item if the user wants to
  build something now.
- **Project review + Task 18 (Core Language Foundation), 2026-10-07:** Claude reviewed the
  project at the user's request. Main conclusion: the documented vision is far larger than
  the implemented core, and a handful of missing core features block almost every open
  task. The user agreed - "the first goal is to get a simple working language first" - and
  asked for this to be logged as a task. Task 18 = functions with full parameter types,
  structs, proper strings, `import`/multi-file projects, and a minimal layered stdlib.
  - Two real gaps verified while grounding the task: (1) default parameter values are
    parsed and type-checked but unusable at call sites (`greet()` fails "expects 1
    argument(s), got 0") even though CLAUDE.md advertises the syntax; (2) string `==`
    compiles to C pointer comparison, correct today only because GCC deduplicates identical
    literals - logged as 18.1 and 18.3
  - Review, cautions, and the user's proposed answer to ecosystem fragmentation (per-symbol
    capability signatures, with the importing project's strategy overriding imported code)
    written up in a new `FutureFeaturesCaution.md`
- **Next Action:** Task 18 is the recommended next priority - start by writing the detailed
  plan for 18.1 and getting it approved.
- **Equality operators + Task 19 + memory guide, 2026-10-07:** user added the equality
  operator family (`=`, `==`, `===`, `!=`, `!==`, `!===`) to Task 18.3 - logged with two
  possible readings, **awaiting the user's decision on meaning**. User set a zero-trust
  principle for libraries ("do not trust library authors at all") and asked for: explicit
  per-function capability signatures visible before compiling, Ada-style project
  restrictions, handling of closed/licensed libraries, sandboxing with resource budgets and
  host-reclaimed memory, supply-chain security against compromised repos, and defenses
  against code hidden to manipulate AI assistants. Logged as **Task 19** (6 sub-tasks).
  Added a memory-strategy selection guide and the expanded security design to
  `FutureFeaturesCaution.md`.
- **Next Action:** unchanged - Task 18 first. Get the user's answer on the equality operator
  meaning (18.3) before that sub-task is planned.
- **User decisions + start of Task 19, 2026-10-07:**
  - Equality: `=` is assignment as a statement but comparison inside an `if` condition;
    `==` compares value everywhere (`xx == "2"` true when `xx` is 2); `===` compares type and
    value. Recorded in 18.3 with the remaining open points (negation pairing, `while`/`else
    if`, a small explicit cross-type table for `==`, char vs string)
  - Security principle sharpened: **never trust code**; no defense is airtight - the goal is
    to make attacks as hard and unlikely as possible, accepting importing code always carries
    risk. AI-targeted content will be handled by an input guard in the future `fusionlib.AI`
    module - logged now as 19.7 (far future)
  - Config: `fusion.toml`, `fusion.yaml`, `fusion.json`, and `fusion.ini` to be accepted
    interchangeably - new **Task 20** (extends Task 12.12)
  - User chose to start **Task 19** now. Only 19.6 has no dependency on `import`, so it goes
    first. Verified both 19.6 attacks (homoglyph identifiers, Trojan Source bidi characters)
    compile today. Wrote the **19.6 Detailed Plan** in Task 19 - **awaiting approval**,
    including one decision: ASCII-only identifiers by default (recommended) vs. Unicode
    identifiers with mixed-script checks
- **Next Action:** get the user's approval on the 19.6 Detailed Plan (and the identifier
  decision), then implement 19.6.1-19.6.5.
- **Task 19.6 COMPLETE, 2026-10-07.** User approved the plan and chose ASCII-only identifiers
  by default. Implemented: new `src/lexer/source_security.py` (rejects bidi/invisible
  characters everywhere incl. comments and strings; ASCII-only identifiers with an opt-in that
  still rejects mixed scripts and compatibility characters); `\uXXXX` escapes; `[source]
  allow_unicode_identifiers` in `fusion.toml`; lexer warnings printed by `main.py` (closes
  Task 15.7). Both originally-verified attacks are now rejected with precise errors.
  - **Found and fixed:** char literals were broken end-to-end (`char c = 'a'` printed `'`) -
    nothing decoded the literal; the parser now does. A parser test asserting the buggy
    behavior was corrected
  - **Found and logged, not fixed (outside the approved plan):** `%` inside a printed string
    is treated as a printf format code - `print("100% done")` prints stack garbage. Logged in
    Task 18.3 as a verified format-string bug (CWE-134), recommended to fix soon
  - Codegen C-escaping consolidated into one helper (`escape_c_text`), which also keeps
    control/invisible characters out of generated C as octal escapes
  - 54 new tests; full suite 1173 passed, 8 skipped; 8/8 examples
- **Next Action:** the rest of Task 19 needs `import` (Task 18.4). Recommended next: fix the
  printf `%` bug (small, security-relevant), then Task 18 (Core Language Foundation) starting
  with a detailed plan for 18.1.

---

## CRITICAL RULES (Reminder)

**FOR CLAUDE:**
1. **NEVER start implementation without approved plan**
2. **ALWAYS update this file after each sub-task**
3. **NEVER use emojis in code files (.py, .c, .h, etc.)**
4. **ALWAYS follow PLAN → APPROVE → IMPLEMENT → UPDATE workflow**
5. **Mark tasks as complete IMMEDIATELY after finishing**
6. **Ship a runnable example in `examples/` for every new feature** - see Task 16

---

## Related Documentation

- **task/taskSummary.md** - MVP tasks (Tasks 1-4, ARCHIVED)
- **task/taskSummaryArchive.md** - Completed post-MVP task detail (Tasks 5-9, 12, ARCHIVED)
- **CLAUDE.md** - AI assistant instructions
- **task/Revisit.md** - Technical debt
- **files/fusion-language-spec.md** - Language specification
- **FutureFeatures.md** - Long-term planned features
- **task/task-10-self-hosting-plan.md** - Self-hosting detailed plan
- **task/task-11-llvm-backend-plan.md** - LLVM backend detailed plan
- **files/Fusion_Hardware_Interface_Definition_Language_HIDL.md** - HIDL vision doc (Task 13,
  blocked/future)

---

**Next Action:** Task 12 (all 12 sub-tasks) is complete and archived. Task 9 is also now
archived. Remaining open items: Task 13 (HIDL module) and Task 14 (nullable arrays) are both
unblocked but still need their own scoping approval before implementation begins (per Rule 1);
Task 15 tracks 7 deferred decisions/gaps from Task 12, each with its own revisit trigger (see
Task 15 above); Task 16 tracks 7 missing example programs, one per language feature - 16.1
(control flow) is buildable now, 16.2-16.7 are each blocked on their own not-yet-built feature;
Task 17 (mutable/fixed strings, templated fixed strings, string pooling) is logged only, not
yet approved for scoping; Task 10 (self-hosting) and Task 11 (LLVM backend) are both "planning
complete" but not started, pending the Task 15.4 ordering decision. **Task 18 (Core Language
Foundation) remains the foundation most other work needs**. **Task 19.6** (source-level attack
defenses) is complete; the rest of Task 19 needs Task 18.4 (`import`) first. The printf `%`
format-string bug (Task 18.3) is fixed. Task 20 (multi-format
config) is logged and unblocked. Read
`FutureFeaturesCaution.md` before picking up anything from FutureFeatures.md. Completed-task
detail for Tasks 5-9 and 12 lives in `task/taskSummaryArchive.md`.
