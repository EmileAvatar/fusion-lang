Here’s the straight, practical checklist of **what’s still missing** or **likely needed later** in the Fusion project — based on the full docs you’ve uploaded and what you and Claude are already building.

I’m keeping this **tight, structured, and scan-friendly** — like a co-worker reviewing the roadmap.

---

# 🔧 High-Value Areas to Add Later (Once Compiler MVP Exists)

## 1. **Name Resolution, Refactoring & Symbol Database**

You mentioned adding a “mini database” for names — good idea.
Missing pieces to define:

* Symbol table format (global, module, file, local scopes)
* Unique IDs for classes/functions/enums
* Cross-file reference graph
* Rename/refactor operations
* Dead symbol detection (unused)
* De-duplication across project boundaries
* Incremental update model (speed for IDE)

---

## 2. **AST Normalization + Persistence**

Fusion already supports 3 syntax styles; the compiler needs:

* Normalized AST (canonical layout)
* AST comparer (identical code different syntax)
* Cached AST files for incremental builds
* AST diff tool (for refactoring and optimization)

---

## 3. **Module System & Dependency Graph**

The spec lists modules, but you still need:

* Module import resolution rules
* Cyclic dependency detection
* Build order generator
* Module versioning (if you add package manager later)

---

## 4. **Full Error Codes & Diagnostics Framework**

Clarify the diagnostic system now:

* Error codes (e.g., F001: Syntax, F100: Type, F200: Memory)
* Structured diagnostic objects (message, severity, location)
* Hints & code actions (e.g., auto-fix suggestions)
* Formatter integration (for “quick fixes”)

---

## 5. **Intermediate Representation (IR) Design**

Right now you go: AST → C.
Eventually for performance you’ll want:

* Canonical IR for optimizations
* Control-flow graph (CFG)
* Data-flow graph (DFG)
* SSA form (optional but ideal later)
* Backend plugins (native, VM, interpreter)

---

## 6. **Fusion VM (Bytecode Backend)**

Planned already in future docs but undefined.

Needed:

* Instruction set
* Register vs stack model
* Bytecode loader
* JIT hooks
* GC hooks
* Debugger hooks

---

## 7. **Optimization Passes (Later, Not MVP)**

You already listed some:

* Constant folding
* Dead code elimination
* Loop unrolling
* Inline heuristics
* Escape analysis (for stack vs heap object decision)
* Auto vectorization (SIMD)
* Tail call optimization (TCO)

All need a clear spec for the compiler team.

---

## 8. **Memory Model Definition**

Fusion supports GC + smart pointers + raw.

You should add:

* Exact GC algorithm (mark-sweep? generational?)
* Smart pointer lowering rules
* Escape analysis rules
* Struct vs class allocation rules
* Thread-safety guarantees around shared pointers

---

## 9. **Testing Infrastructure**

You’ve got the idea in the big doc; refine:

* Test discovery rules
* Backend matrix (native/interpreter/bytecode)
* Benchmarks + warmup rules
* Snapshot testing for AST/IR
* Built-in mocking API
* Golden-file tests for codegen

---

## 10. **Security & Sandbox Rules**

Fusion aims to compile multiple modes.

Add the missing:

* Sandboxed execution (for VM mode)
* Allowed syscalls list
* Capabilities model (file/network/process)
* Deterministic mode (no time/random/threads)
* FFI safety boundary (for C/DLL calls)

---

## 11. **Build System Specification**

Fusion has project.json, but missing:

* Build graph
* Incremental compilation rules
* Artifact caching
* Cross-platform toolchain targeting
* Plugin hooks (“before build”, “after build”)

---

## 12. **Formatter + Syntax Conversion Engine**

You already have design notes — now formalize:

* Concrete formatting rules
* Style matrix (indent ↔ braces ↔ End)
* Comment preservation policy
* White-space normalization
* Code folding rules

---

## 13. **Debugger Protocol**

Needed for IDEs:

* Breakpoints
* Step in/out/over
* Variable inspection
* Call stack
* Memory view
* Thread inspector
* Event hooks from VM/native code

---

## 14. **Hot Reloading / Live Coding**

Optional but valuable:

* Watch mode (`fusion watch`)
* Partial recompilation
* Live VM patching
* Hot class/function reload

---

## 15. **Future Optional Systems**

These are “nice to have later”:

* Macro system
* Compile-time functions (CTF)
* Plugin compiler passes
* Code generation templates
* DSL embedding
* Attribute-driven code gen (like C# source generators)

---

# 🟢 TL;DR — Practical “Add Later” List

If you want just the short list:

1. **Symbol database + refactoring engine**
2. **AST normalization + caching**
3. **Module dependency graph**
4. **Diagnostic framework (codes + hints)**
5. **Intermediate Representation (IR)**
6. **Virtual machine + bytecode spec**
7. **Optimization rules**
8. **Memory model formalization**
9. **Testing framework (multi-backend)**
10. **Security / sandbox spec**
11. **Build system architecture**
12. **Formatter + syntax converter spec**
13. **Debugger protocol**
14. **Hot reload system**
15. **Macros / compile-time tools**

---

If you want, I can generate:

✔ a **“Fusion Future Additions” markdown file**
✔ a **roadmap diagram**
✔ a **feature priority matrix** (what to build before MVP, after MVP, post-1.0)
✔ a **compiler architecture diagram**

Just tell me which format you want.
