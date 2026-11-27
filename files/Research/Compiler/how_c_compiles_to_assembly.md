# How C Compiles to Assembly Language

When a compiler like **GCC** or **Clang** turns C code into assembly (e.g., `gcc -S main.c`), it does not translate C directly to CPU instructions in one leap. Instead, it passes the code through a structured, multi-stage pipeline divided into three main parts: the **Frontend**, the **Middle-end**, and the **Backend**.

Understanding this pipeline is foundational when designing your own language, as it lets you decouple language syntax from target hardware.

---

## The High-Level Pipeline

```text
C Source Code (.c)
      │
      ▼
[1. Preprocessor]        ──► Expanded C code (macros & includes resolved)
      │
      ▼
[2. Lexer & Parser]      ──► Abstract Syntax Tree (AST)
      │
      ▼
[3. Semantic Analyzer]   ──► Typed & Validated AST + Symbol Table
      │
      ▼
[4. IR Generator]        ──► Intermediate Representation (e.g., LLVM IR / GIMPLE)
      │
      ▼
[5. Optimizer]           ──► Optimized IR
      │
      ▼
[6. Code Generator]      ──► Assembly Language (.s)
```

*(Note: After assembly is generated, an **Assembler** turns `.s` into machine code object files `.o`, and a **Linker** combines them into an executable.)*

---

## Stage 1: Preprocessing (C-Specific)

Before the compiler even understands C grammar, the preprocessor runs a text-substitution pass:
* **File Inclusion:** Copies the contents of `#include` header files directly into the source file.
* **Macro Expansion:** Performs text replacement for `#define` macros.
* **Conditional Compilation:** Strips out code blocks excluded by `#ifdef` / `#ifndef`.
* **Cleanup:** Removes comments and normalizes whitespace.

> **Language Design Tip:** Most modern languages skip a text-based preprocessor in favor of a proper **module system** and **hygienic macros** (macros that operate on the AST rather than raw text).

---

## Stage 2: The Frontend (Source $\rightarrow$ Validated AST)

The frontend is responsible for understanding *what the programmer wrote* and verifying that it follows the rules of the language.

### 1. Lexical Analysis (Tokenizing)
The **lexer** (or scanner) reads raw characters and groups them into meaningful **tokens**.
* Input: `int x = a + 2;`
* Output: `[KEYWORD(int), IDENT(x), EQUALS, IDENT(a), PLUS, INT_LIT(2), SEMICOLON]`

### 2. Syntax Analysis (Parsing)
The **parser** consumes the stream of tokens and checks them against the language's grammar, building an **Abstract Syntax Tree (AST)**. The AST captures operator precedence and nesting structure.

### 3. Semantic Analysis
Just because code is grammatically valid does not mean it makes sense (e.g., adding a `struct` to a `float`, or using an undeclared variable). The semantic analyzer walks the AST to:
* Build a **Symbol Table** tracking variable names, scopes, and memory sizes.
* Perform **Type Checking** and insert implicit type conversions (e.g., promoting `int` to `float`).
* Verify control flow rules (e.g., `break` is only used inside a loop or `switch`).

---

## Stage 3: The Middle-End (AST $\rightarrow$ Optimized IR)

Instead of generating assembly straight from the AST, modern C compilers lower the AST into an **Intermediate Representation (IR)**.

### Why Use an IR?
If you have $M$ source languages and $N$ target CPU architectures (x86-64, ARM64, RISC-V, WebAssembly), compiling directly requires $M \times N$ compilers. With a shared IR, you only need $M$ frontends and $N$ backends ($M + N$).

### What IR Looks Like
Compilers typically use **Three-Address Code (TAC)** in **Static Single Assignment (SSA)** form—where every virtual register is assigned exactly once, and the compiler assumes an *infinite* number of virtual registers.

### Optimization Passes
Because IR is simple and hardware-agnostic, the compiler runs dozens of optimization passes on it:
* **Constant Folding:** Evaluates `3 * 4` at compile time into `12`.
* **Dead Code Elimination (DCE):** Deletes unreachable code or unused variables.
* **Function Inlining:** Replaces a small function call with its body to avoid call overhead.
* **Loop Optimizations:** Hoists invariant calculations out of loops or unrolls small loops.

---

## Stage 4: The Backend (IR $\rightarrow$ Assembly)

The backend translates the idealized, infinite-register IR into concrete assembly instructions for a specific CPU architecture (like x86-64 or ARM64).

### 1. Instruction Selection
Maps IR operations onto actual CPU instructions. A single IR node might map to multiple assembly instructions, or multiple IR nodes might fuse into one specialized CPU instruction (like x86's `LEA` for combined multiply-and-add).

### 2. Register Allocation
Real CPUs have a very limited number of physical registers (e.g., 16 general-purpose registers on x86-64). The register allocator maps the IR's infinite virtual registers onto physical registers—typically using **Graph Coloring** or **Linear Scan**.
* If there aren't enough physical registers to hold all live variables simultaneously, the compiler **spills** some variables onto the stack (RAM).

### 3. Calling Conventions & Stack Frames (ABI)
The compiler emits function **prologues** and **epilogues** to obey the OS/CPU's Application Binary Interface (ABI)—for example, System V AMD64 on Linux/macOS or Microsoft x64 on Windows:
* Which registers hold incoming arguments (e.g., `rdi`, `rsi`, `rdx` on Linux x86-64).
* Which register holds the return value (e.g., `rax`).
* Which registers must be preserved across function calls (callee-saved vs. caller-saved).
* How stack space is allocated and aligned for local variables.

### 4. Instruction Scheduling
Reorders assembly instructions (without changing program behavior) to keep the CPU's execution pipelines full and avoid hardware stalls.

---

## Concrete Walkthrough: C to x86-64 Assembly

Consider this simple C function:

```c
int compute(int a, int b) {
    return a + b * 2;
}
```

### 1. Abstract Syntax Tree (AST)
```text
FunctionDecl(compute, returns: int, params: [a: int, b: int])
 └── ReturnStmt
      └── BinaryOp(+)
           ├── VarRef(a)
           └── BinaryOp(*)
                ├── VarRef(b)
                └── IntLiteral(2)
```

### 2. Intermediate Representation (LLVM-style IR)
```llvm
define i32 @compute(i32 %a, i32 %b) {
entry:
  %mul = mul nsw i32 %b, 2
  %add = add nsw i32 %a, %mul
  ret i32 %add
}
```

### 3. Generated x86-64 Assembly (Optimized, System V ABI)
On Linux/macOS x86-64, the first argument `a` arrives in `edi`, the second argument `b` arrives in `esi`, and the return value goes in `eax`.

```asm
compute:
    lea eax, [rdi + rsi*2]   ; Fuses (a + b * 2) into a single instruction!
    ret                      ; Return value is already in eax
```

Without optimization (`-O0`), the compiler would instead allocate a stack frame (`push rbp`, `mov rbp, rsp`), store `edi` and `esi` to the stack, load them back, multiply, add, clean up the stack, and `ret`.

---

## Practical Strategy for Building Your Fusion Language

Since you are building a new language (and iterating quickly with Claude Code), you have four main paths for your backend. Choosing the right one early will save months of work:

| Backend Approach | How It Works | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Transpile to C** | Your compiler emits `.c` files, then invokes `gcc` or `clang`. | Fastest path to a working language; instant portability and world-class optimizations. | Harder to implement custom calling conventions, tail calls, or precise garbage collection. |
| **Target LLVM** | Your frontend emits LLVM IR (via C++ API, Rust `inkwell`, or text `.ll` files). | Industry-grade optimizations; targets x86, ARM, WASM, etc. | Heavy dependency; slow compile times; steep API learning curve. |
| **Target QBE or Cranelift** | Emit IR for a lightweight compiler backend (QBE is tiny C; Cranelift is Rust). | Much simpler than LLVM; fast compile times; great for JIT or AOT. | Slightly less aggressive optimizations than LLVM; fewer target architectures. |
| **Emit Raw Assembly** | Write your own instruction selector and register allocator. | Total control; zero external dependencies; great learning experience. | Very hard to get right across multiple OSes/CPUs; you must write your own optimizations. |

### Recommended Workflow with Claude Code
1. **Start with a clean AST and a Tree-Walking Interpreter** (or Bytecode VM) to lock down your fusion language's syntax and semantics quickly.
2. **Add a Transpile-to-C or QBE backend first** so you can compile to native binaries almost immediately without getting bogged down in x86 register allocation.
3. **Upgrade to LLVM or Cranelift** once your language semantics and type system stabilize.