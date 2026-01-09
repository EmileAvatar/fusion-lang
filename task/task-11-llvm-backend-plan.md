# TASK 11: LLVM Backend Integration

**Goal:** Replace C code generator with LLVM IR backend for direct native compilation
**Status:** Planning Phase
**Priority:** MEDIUM (Enhancement after self-hosting)
**Blocked By:** Task 10 (Self-Hosting should be complete first)
**Estimated Effort:** 30-40 hours

---

## Overview

Currently: `Fusion → C code → GCC → Native executable`
After LLVM: `Fusion → LLVM IR → Native executable (no intermediate C)`

**Benefits:**
1. **No C intermediate** - Direct to machine code
2. **Cross-platform** - LLVM targets 30+ architectures
3. **Better optimization** - LLVM's world-class optimizer
4. **Faster compilation** - No GCC invocation overhead
5. **Advanced features** - JIT compilation, link-time optimization
6. **Industry standard** - Used by Swift, Rust, Kotlin/Native, Clang

---

## LLVM Architecture

```
Fusion Source (.fusion)
    ↓
Lexer → Parser → Semantic Analyzer
    ↓
LLVM IR Generator (NEW)
    ↓
LLVM IR (.ll or .bc)
    ↓
LLVM Optimizer (optional)
    ↓
LLVM Backend (machine code)
    ↓
Native Executable (.exe, .elf, .app)
```

---

## Prerequisites

### Technical Requirements:
- [ ] LLVM installed (llvm-config available)
- [ ] Python bindings: `llvmlite` or `llvmpy`
- [ ] Understanding of LLVM IR syntax
- [ ] Knowledge of LLVM C API or Python bindings

### Knowledge Prerequisites:
- [ ] LLVM IR fundamentals (SSA form, basic blocks, PHI nodes)
- [ ] Type system mapping (Fusion types → LLVM types)
- [ ] Function calling conventions
- [ ] Memory management in LLVM

---

## Sub-tasks

### 11.1: Research & Design (4-6 hours)
- [ ] Study LLVM architecture and IR format
- [ ] Research llvmlite vs llvmpy vs LLVM C API
- [ ] Decide on binding library (Recommendation: llvmlite)
- [ ] Design Fusion → LLVM type mapping:
  - [ ] int → i32
  - [ ] float → float
  - [ ] double → double
  - [ ] bool → i1
  - [ ] string → i8* (pointer to char array)
  - [ ] void → void
- [ ] Design function calling convention
- [ ] Plan memory management strategy
- [ ] Create architecture document
- [ ] Get user approval

### 11.2: Setup LLVM Environment (2-3 hours)
- [ ] Install LLVM on development machine
  - [ ] Windows: LLVM pre-built binaries
  - [ ] Linux: apt-get install llvm
  - [ ] macOS: brew install llvm
- [ ] Install Python bindings: `pip install llvmlite`
- [ ] Verify installation: `llvm-config --version`
- [ ] Write hello world LLVM IR test
- [ ] Compile and run test program
- [ ] Document installation process

### 11.3: Create LLVM Code Generator (8-10 hours)
- [ ] Create src/codegen/llvm_generator.py
- [ ] Implement LLVMGenerator class (similar to CCodeGenerator)
- [ ] Initialize LLVM module and builder
- [ ] Implement type mapping:
  - [ ] map_fusion_type_to_llvm()
  - [ ] Handle primitive types
  - [ ] Handle function types
- [ ] Implement basic code generation:
  - [ ] visit_ProgramNode()
  - [ ] visit_FunctionDecl()
  - [ ] visit_VarDeclStmt()
  - [ ] visit_ReturnStmt()
- [ ] Test basic program compilation

### 11.4: Implement Expression Generation (6-8 hours)
- [ ] Implement visit_LiteralExpr():
  - [ ] Integer literals → ConstantInt
  - [ ] Float literals → ConstantFP
  - [ ] Bool literals → ConstantInt(i1)
  - [ ] String literals → GlobalStringPtr
- [ ] Implement visit_IdentifierExpr():
  - [ ] Load from alloca
  - [ ] Handle function references
- [ ] Implement visit_BinaryExpr():
  - [ ] Arithmetic: add, sub, mul, div, mod
  - [ ] Comparison: eq, ne, lt, le, gt, ge
  - [ ] Logical: and, or
  - [ ] Handle type promotion (int → float)
- [ ] Implement visit_UnaryExpr():
  - [ ] Negation (neg)
  - [ ] Logical not
- [ ] Implement visit_CallExpr():
  - [ ] Function calls with arguments
  - [ ] Handle printf for print()
- [ ] Implement visit_InterpolatedStringExpr():
  - [ ] Generate format string
  - [ ] Call printf with arguments
- [ ] Test expression generation

### 11.5: Implement Statement Generation (6-8 hours)
- [ ] Implement visit_ExpressionStmt()
- [ ] Implement visit_AssignmentStmt():
  - [ ] Store to alloca
  - [ ] Type checking
- [ ] Implement visit_IfStmt():
  - [ ] Create basic blocks (then, else, merge)
  - [ ] Conditional branch
  - [ ] PHI nodes if needed
- [ ] Implement visit_WhileStmt():
  - [ ] Create basic blocks (cond, body, exit)
  - [ ] Loop branches
  - [ ] PHI nodes for loop variables
- [ ] Implement visit_ForStmt():
  - [ ] Initialize, condition, increment
  - [ ] Loop basic blocks
- [ ] Implement visit_BreakStmt() and visit_ContinueStmt():
  - [ ] Track loop exit and continue blocks
  - [ ] Branch instructions
- [ ] Implement visit_BlockStmt():
  - [ ] Nested scopes
- [ ] Test control flow generation

### 11.6: Implement Declaration Generation (4-5 hours)
- [ ] Implement visit_ParameterDecl():
  - [ ] Function parameters
  - [ ] Default values (if supported)
- [ ] Implement forward declarations:
  - [ ] Declare functions before definition
  - [ ] Handle mutual recursion
- [ ] Implement visit_VarDeclStmt() fully:
  - [ ] Alloca in entry block
  - [ ] Store initial value
  - [ ] Handle const (metadata?)
- [ ] Test declaration generation

### 11.7: Implement Built-in Functions (3-4 hours)
- [ ] Implement print() as printf() call:
  - [ ] Declare printf prototype
  - [ ] Generate format strings
  - [ ] Pass arguments
- [ ] Implement other built-ins as needed:
  - [ ] Math functions (if used)
  - [ ] String functions (if used)
- [ ] Test built-in function calls

### 11.8: Integration & Compilation Pipeline (4-5 hours)
- [ ] Update main.py to support LLVM backend:
  - [ ] Add --backend flag: --backend=c or --backend=llvm
  - [ ] Route to appropriate code generator
- [ ] Implement LLVM IR output:
  - [ ] Write .ll file (human-readable IR)
  - [ ] Write .bc file (bitcode, optional)
- [ ] Implement LLVM compilation:
  - [ ] Use llc to generate object files
  - [ ] Use llvm-link for linking
  - [ ] Or use lli for JIT execution
  - [ ] Or use clang to compile .ll directly
- [ ] Test end-to-end compilation:
  - [ ] Fusion → LLVM IR → executable
- [ ] Verify executables run correctly

### 11.9: Optimization Integration (3-4 hours)
- [ ] Research LLVM optimization passes
- [ ] Add optimization levels:
  - [ ] -O0: No optimization (default)
  - [ ] -O1: Basic optimization
  - [ ] -O2: Standard optimization
  - [ ] -O3: Aggressive optimization
- [ ] Implement pass manager:
  - [ ] Function-level passes
  - [ ] Module-level passes
- [ ] Test optimization impact:
  - [ ] Compile time
  - [ ] Executable size
  - [ ] Runtime performance
- [ ] Document optimization flags

### 11.10: Testing & Verification (6-8 hours)
- [ ] Run all 1,041+ unit tests with LLVM backend
- [ ] Compare outputs: C backend vs LLVM backend
- [ ] Compile all 6 example programs with LLVM
- [ ] Verify outputs are identical
- [ ] Performance benchmarking:
  - [ ] Compilation speed (C vs LLVM)
  - [ ] Executable size (C vs LLVM)
  - [ ] Runtime performance (C vs LLVM)
  - [ ] Optimization levels impact
- [ ] Create test report with comparisons
- [ ] Fix any bugs or discrepancies

### 11.11: Advanced Features (Optional) (4-6 hours)
- [ ] JIT compilation support:
  - [ ] Use LLVM JIT engine
  - [ ] Execute Fusion code without compiling to file
  - [ ] REPL integration possibility
- [ ] Debug information generation:
  - [ ] DWARF debug info
  - [ ] Source line mapping
  - [ ] Variable names in debugger
- [ ] Link-time optimization (LTO):
  - [ ] Cross-module optimization
  - [ ] Whole-program analysis
- [ ] Profile-guided optimization (PGO):
  - [ ] Instrumentation
  - [ ] Profile collection
  - [ ] Optimized recompilation

### 11.12: Documentation & Migration (3-4 hours)
- [ ] Update README.md with LLVM backend info
- [ ] Create LLVM.md guide:
  - [ ] Installation instructions
  - [ ] Usage: --backend=llvm flag
  - [ ] Optimization levels
  - [ ] Performance comparison
- [ ] Update CLAUDE.md with LLVM architecture
- [ ] Document type mapping
- [ ] Create migration guide (C → LLVM)
- [ ] Write performance tuning guide
- [ ] Update build instructions

### 11.13: Release & Finalization (2-3 hours)
- [ ] Create feature flag for LLVM backend:
  - [ ] Enable/disable at compile time
  - [ ] Default to C backend for stability
  - [ ] --backend=llvm as opt-in
- [ ] Update CI/CD to test both backends
- [ ] Create release notes
- [ ] Git commit: "feat: Add LLVM backend support"
- [ ] Tag release: v2.1.0-llvm
- [ ] Announce LLVM backend availability

---

## Success Criteria

1. **Functional Equivalence:**
   - LLVM backend produces same behavior as C backend
   - All tests pass with LLVM backend
   - All examples compile and run correctly

2. **Performance:**
   - Compilation speed competitive with C backend
   - Generated code quality equal or better
   - Optimization levels provide measurable improvements

3. **Integration:**
   - Seamless --backend=llvm flag
   - Both backends maintained in parallel
   - Easy to switch between backends

4. **Quality:**
   - Clean, maintainable LLVM generator code
   - Well-documented
   - Comprehensive tests

---

## Type Mapping Reference

| Fusion Type | LLVM Type | Notes |
|-------------|-----------|-------|
| int | i32 | 32-bit integer |
| float | float | 32-bit floating point |
| double | double | 64-bit floating point |
| bool | i1 | 1-bit integer |
| char | i8 | 8-bit integer |
| string | i8* | Pointer to null-terminated char array |
| void | void | No return value |
| int[] | i32* | Pointer to array (+ length metadata) |
| function(int,int):int | i32 (i32, i32)* | Function pointer type |

---

## LLVM IR Example

**Fusion Code:**
```fusion
int function add(int a, int b)
    return a + b
End function

void function main()
    int result = add(10, 20)
    print("Result: {result}")
End function
```

**Generated LLVM IR:**
```llvm
define i32 @add(i32 %a, i32 %b) {
entry:
  %sum = add i32 %a, %b
  ret i32 %sum
}

@.str = private unnamed_addr constant [12 x i8] c"Result: %d\0A\00"

define i32 @main() {
entry:
  %result = call i32 @add(i32 10, i32 20)
  %printf = call i32 (i8*, ...) @printf(i8* getelementptr([12 x i8], [12 x i8]* @.str, i32 0, i32 0), i32 %result)
  ret i32 0
}

declare i32 @printf(i8*, ...)
```

---

## Risks & Mitigation

**Risk 1: LLVM Complexity**
- Mitigation: Start with simple features, iterate gradually

**Risk 2: Platform-Specific Issues**
- Mitigation: Test on Windows, Linux, macOS

**Risk 3: Performance Regression**
- Mitigation: Keep C backend as fallback, benchmark thoroughly

**Risk 4: Maintenance Burden**
- Mitigation: Two backends means more code to maintain, but LLVM is more future-proof

---

## Deliverables

1. **Source Code:**
   - src/codegen/llvm_generator.py
   - LLVM IR generation for all language features
   - Tests for LLVM backend

2. **Documentation:**
   - LLVM.md guide
   - Updated README.md
   - Performance comparison report

3. **Integration:**
   - --backend flag in main.py
   - CI/CD updates
   - Both backends working

4. **Verification:**
   - All tests passing
   - Performance benchmarks
   - Example programs working

---

## Future Enhancements (Post-LLVM)

After LLVM integration, we can:
1. Add JIT compilation for REPL
2. Implement advanced optimizations
3. Support more target architectures
4. Add GPU code generation (CUDA, OpenCL via LLVM)
5. Implement ahead-of-time (AOT) compilation cache

---

## References

- **LLVM Official:** https://llvm.org/docs/
- **LLVM Tutorial:** https://llvm.org/docs/tutorial/
- **llvmlite Docs:** https://llvmlite.readthedocs.io/
- **LLVM IR Language Reference:** https://llvm.org/docs/LangRef.html
- **LLVM Programmer's Manual:** https://llvm.org/docs/ProgrammersManual.html

---

**Estimated Timeline:** 4-6 weeks (after Task 10 complete)

**Dependencies:** Task 10 (Self-Hosting) should be complete first for stability

**Next Step:** Get user approval, complete Task 10, then begin LLVM integration
