# TASK 10: Self-Hosting - Rewrite Compiler in Fusion

**Goal:** Rewrite the Fusion compiler in Fusion itself, enabling the compiler to compile itself
**Status:** Planning Phase
**Priority:** HIGH (Critical milestone for language maturity)
**Blocked By:** Tasks 5-9 (need core language features complete)
**Estimated Effort:** 40-60 hours (major milestone)

---

## Overview

Self-hosting means the Fusion compiler, currently written in Python, will be rewritten in Fusion. This is a critical milestone that proves:
1. Fusion is powerful enough to write complex software
2. The language is mature and feature-complete
3. The compiler can maintain itself going forward

**Bootstrap Process:**
```
Python Compiler (v1) → Compiles Fusion Compiler (v2) → Fusion Compiler compiles itself (v3)
```

Verification: v2 and v3 must produce identical output.

---

## Prerequisites (Must Complete First)

Before starting self-hosting, Fusion must have:
- ✓ Functions and recursion (already working)
- ✓ String manipulation (already working)
- [ ] File I/O (need IO module from fusionlib)
- [ ] Collections (List, Dictionary) - needed for symbol tables
- [ ] Error handling (try/catch or error returns)
- [ ] String manipulation helpers (split, substring, etc.)
- [ ] Command-line argument parsing

**Decision Point:** Do we implement these as built-in features or import from fusionlib?

---

## Sub-tasks

### 10.1: Prerequisites Analysis & Planning (2-3 hours)
- [ ] Analyze current Python compiler codebase
- [ ] List all Python features used (file I/O, collections, etc.)
- [ ] Map Python features to Fusion equivalents
- [ ] Identify missing Fusion features needed
- [ ] Create feature implementation plan
- [ ] Document required fusionlib modules (IO, Collections, System)
- [ ] Design Fusion compiler architecture
- [ ] Get user approval for approach

### 10.2: Implement Missing Language Features (8-12 hours)
- [ ] Add file I/O support to Fusion
  - [ ] File reading: `file.read()`, `file.readLines()`
  - [ ] File writing: `file.write()`, `file.writeLine()`
  - [ ] File operations: `exists()`, `delete()`, etc.
- [ ] Add collection support
  - [ ] List type: `List<T>`
  - [ ] Dictionary type: `Dictionary<K, V>`
  - [ ] Basic methods: add, remove, get, contains
- [ ] Add string manipulation
  - [ ] split(), substring(), indexOf()
  - [ ] startsWith(), endsWith(), trim()
- [ ] Add command-line arguments
  - [ ] Access via `args[]` or `System.args`
- [ ] Test all new features

### 10.3: Port Lexer to Fusion (6-8 hours)
- [ ] Create src_fusion/lexer/ directory
- [ ] Port token.py → token.fusion
  - [ ] TokenType enum
  - [ ] Token class/struct
  - [ ] Location tracking
- [ ] Port lexer.py → lexer.fusion
  - [ ] Character reading logic
  - [ ] Tokenization methods
  - [ ] Error reporting
- [ ] Port literals.py → literals.fusion
  - [ ] String interpolation parsing
  - [ ] Number parsing
  - [ ] Character parsing
- [ ] Port keywords.py → keywords.fusion
- [ ] Write tests for Fusion lexer
- [ ] Verify: Fusion lexer produces same tokens as Python lexer

### 10.4: Port Parser to Fusion (8-10 hours)
- [ ] Create src_fusion/parser/ directory
- [ ] Port ast_nodes.py → ast_nodes.fusion
  - [ ] All AST node classes/structs
  - [ ] Node visitor pattern
- [ ] Port parser.py → parser.fusion
  - [ ] Recursive descent parsing logic
  - [ ] Expression parsing (Pratt parser)
  - [ ] Statement parsing
  - [ ] Declaration parsing
  - [ ] Error recovery
- [ ] Write tests for Fusion parser
- [ ] Verify: Fusion parser produces same AST as Python parser

### 10.5: Port Semantic Analyzer to Fusion (8-10 hours)
- [ ] Create src_fusion/semantic/ directory
- [ ] Port symbol_table.py → symbol_table.fusion
  - [ ] Symbol storage and lookup
  - [ ] Scope management
- [ ] Port name_resolver.py → name_resolver.fusion
  - [ ] Variable/function resolution
  - [ ] Scope validation
- [ ] Port type_checker.py → type_checker.fusion
  - [ ] Type inference
  - [ ] Type compatibility checking
- [ ] Port control_flow_validator.py → control_flow_validator.fusion
- [ ] Port entry_point_validator.py → entry_point_validator.fusion
- [ ] Write tests for Fusion semantic analyzer
- [ ] Verify: Fusion analyzer catches same errors as Python

### 10.6: Port Code Generator to Fusion (6-8 hours)
- [ ] Create src_fusion/codegen/ directory
- [ ] Port c_generator.py → c_generator.fusion
  - [ ] AST visitor for C code generation
  - [ ] Expression generation
  - [ ] Statement generation
  - [ ] Declaration generation
  - [ ] String interpolation handling
- [ ] Write tests for Fusion code generator
- [ ] Verify: Fusion codegen produces same C code as Python

### 10.7: Create Main Driver (2-3 hours)
- [ ] Create fusion_compiler.fusion (main entry point)
- [ ] Command-line argument parsing
- [ ] Pipeline orchestration:
  - [ ] Lexer → Parser → Semantic → Codegen → GCC
- [ ] Error reporting and formatting
- [ ] Success/failure exit codes
- [ ] Help message and usage

### 10.8: Bootstrap Phase 1 - Initial Compilation (2-3 hours)
- [ ] Use Python compiler to compile fusion_compiler.fusion
- [ ] Generate fusion_compiler.c
- [ ] Compile fusion_compiler.exe (v2) with GCC
- [ ] Test fusion_compiler.exe on simple examples
- [ ] Fix any runtime errors
- [ ] Verify v2 compiles all example programs

### 10.9: Bootstrap Phase 2 - Self-Compilation (3-4 hours)
- [ ] Use fusion_compiler.exe (v2) to compile itself
- [ ] Generate fusion_compiler_v3.exe
- [ ] Compare outputs:
  - [ ] v2 compiling hello_world.fusion
  - [ ] v3 compiling hello_world.fusion
  - [ ] Both should produce identical C code
- [ ] Run full test suite with v3
- [ ] Verify: v3 passes all tests

### 10.10: Verification & Testing (4-6 hours)
- [ ] Compile all 6 example programs with v3
- [ ] Run all executables and verify outputs
- [ ] Performance benchmarking:
  - [ ] Python compiler compile time
  - [ ] v2 (Fusion) compiler compile time
  - [ ] v3 (self-compiled) compile time
- [ ] Stress testing with large programs
- [ ] Edge case testing
- [ ] Create comprehensive test report

### 10.11: Documentation (2-3 hours)
- [ ] Update README.md with self-hosting achievement
- [ ] Document bootstrap process
- [ ] Create BOOTSTRAP.md guide
- [ ] Update CLAUDE.md with new architecture
- [ ] Add self-hosting to feature list
- [ ] Document performance characteristics
- [ ] Write migration guide (Python → Fusion)

### 10.12: Transition & Cleanup (2-3 hours)
- [ ] Archive Python compiler to legacy/
- [ ] Update build scripts to use Fusion compiler
- [ ] Update CI/CD pipelines
- [ ] Create release notes
- [ ] Git commit: "feat: Self-hosting compiler (Fusion v2.0)"
- [ ] Tag release: v2.0.0-self-hosted
- [ ] Announce milestone

---

## Success Criteria

1. **Functional Equivalence:**
   - Fusion compiler produces identical output to Python compiler
   - All 1,041+ unit tests pass
   - All example programs compile and run correctly

2. **Self-Compilation:**
   - Compiler can compile itself
   - Self-compiled version (v3) produces same output as v2
   - v3 can compile itself again (v4), proving stability

3. **Performance:**
   - Compilation speed acceptable (within 2-5x of Python version)
   - Generated C code quality unchanged
   - Memory usage reasonable

4. **Maintainability:**
   - Fusion compiler code is clean and readable
   - Well-documented and testable
   - Easier to maintain than Python version

---

## Risks & Mitigation

**Risk 1: Missing Language Features**
- Mitigation: Complete analysis in 10.1, implement features in 10.2

**Risk 2: Performance Issues**
- Mitigation: Profile and optimize critical paths, consider keeping Python for development

**Risk 3: Bootstrap Bugs**
- Mitigation: Extensive testing at each phase, keep Python compiler as fallback

**Risk 4: Scope Creep**
- Mitigation: Port feature-for-feature first, optimize later

---

## Deliverables

1. **Source Code:**
   - src_fusion/lexer/*.fusion
   - src_fusion/parser/*.fusion
   - src_fusion/semantic/*.fusion
   - src_fusion/codegen/*.fusion
   - fusion_compiler.fusion (main)

2. **Executables:**
   - fusion_compiler.exe (self-hosted compiler)
   - All tests passing

3. **Documentation:**
   - BOOTSTRAP.md
   - Updated README.md
   - Migration guide
   - Performance report

4. **Verification:**
   - Test report showing equivalence
   - Performance benchmarks
   - Self-compilation proof

---

## Future Enhancements (Post-Self-Hosting)

After self-hosting is complete, we can:
1. Optimize the Fusion compiler for speed
2. Add advanced compiler features (optimization passes, etc.)
3. Replace C backend with LLVM (Task 11)
4. Add compiler plugins and extensions
5. Implement incremental compilation

---

**Estimated Timeline:** 6-8 weeks (part-time development)

**Next Step:** Get user approval, then implement prerequisites (10.1-10.2)
