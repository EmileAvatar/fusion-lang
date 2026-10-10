# Fusion Compiler - Post-MVP Task Archive

**Purpose:** Completed post-MVP task sections (Tasks 5+), moved out of `../taskSummary2.md`
to keep that file small - see `CLAUDE.md` Rule 3 for the archiving policy.
**See:** `../taskSummary2.md` for active/incomplete tasks, the Overall Progress table, and
Working Notes (session history). This file only holds finished task detail - sub-tasks,
success criteria, and deliverables - for reference.
**Related:** `taskSummary.md` (this same folder) archives the earlier MVP tasks (Tasks 1-4).

---

## TASK 5: Project Cleanup & Organization

**Goal:** Organize project files into proper structure
**Status:** Complete
**Priority:** CRITICAL (must complete before any new features)
**Estimated Effort:** 1-2 hours
**Actual Effort:** ~30 minutes

### Sub-tasks:

#### 5.1: Move taskSummary.md to Archive
- [x] Move d:/Dropbox/Fusion/taskSummary.md → d:/Dropbox/Fusion/task/taskSummary.md
- [x] Update CLAUDE.md references (already done)
- [x] Add note in task/taskSummary.md header: "ARCHIVED - See ../taskSummary2.md for current tasks"

#### 5.2: Move Verification Script
- [x] Move d:/Dropbox/Fusion/verify_examples.py → d:/Dropbox/Fusion/tests/verify_examples.py
- [x] Update any import paths if needed
- [x] Test script still works after move

#### 5.3: Organize Documentation
- [x] Move d:/Dropbox/Fusion/verification_report.md → d:/Dropbox/Fusion/files/verification_report.md
- [x] Create files/reports/ subdirectory for future reports
- [x] Move verification_report.md to files/reports/

#### 5.4: Update Path References
- [x] Update README.md with new file locations
- [x] Update main.py if it references moved files
- [x] Update any test files that reference verify_examples.py

#### 5.5: Verify Nothing Broke
- [x] Run `python -m pytest tests/` to ensure all tests still pass
- [x] Run `python tests/verify_examples.py` to ensure verification works
- [x] Document any issues found

**Success Criteria:**
- All files in proper locations
- All path references updated
- All tests still passing
- No broken imports

**Deliverables:**
- Clean project structure
- Updated documentation
- Test run confirmation

---

## TASK 6: Verification & Bug Fixes

**Goal:** Verify compiler works correctly and fix any issues found
**Status:** Complete
**Priority:** CRITICAL
**Estimated Effort:** 4-5 hours

### Current Verification Results:

From user's PowerShell testing:
- calculator.exe: "Sum: 15, Diff: 5, Prod: 50" - WORKS
- factorial.exe: "Factorial of 5 is 120" - WORKS
- hello_world.exe: "Hello, World!" - WORKS
- max_three.exe: "Maximum of 10, 25, 15 is 25" - WORKS
- sum_array.exe: "Sum of 1 to 10: 55" - WORKS
- fizzbuzz.exe: Only shows "Fizz", "Buzz", "FizzBuzz" - MISSING NUMBERS

### Issues Identified by Claude Opus Review:

1. **FizzBuzz Bug - ROOT CAUSE FOUND:**
   - String interpolation `print("{i}")` generates `printf("\n")` instead of `printf("%d\n", i)`
   - Code generator strips `{i}` but doesn't insert variable into printf
   - Bug is in src/codegen/ string interpolation handling

2. **Incomplete Cleanup from Task 5:**
   - 5 stale test files in root (should be in tests/ or deleted)
   - 1 debug file in root (debug_lexer.py)
   - 2 empty folders (Compiler/, Specification/)
   - 12 documentation files in root (could organize to files/)

3. **taskSummary2.md Stale Entry:**
   - Line 410 says "Await user approval for Task 5"
   - Should say "Begin Task 6 - Investigate FizzBuzz bug"

### Sub-tasks:

#### 6.0: Pre-Verification Cleanup (From Opus Review)
- [x] Identified 5 "test" files are actually DEBUG SCRIPTS (not stale tests)
  - test_trace_pos_changes.py patches Lexer.pos property globally
  - test_patch_operator.py patches lexer methods
  - Cannot be in tests/ or pytest collects them and breaks 290 tests
- [x] Created debug/ folder for debugging scripts
- [x] Moved 6 debug scripts to debug/:
  - test_lexer_simple.py
  - test_specific_case.py
  - test_detailed_trace.py
  - test_trace_pos_changes.py
  - test_patch_operator.py
  - debug_lexer.py
- [x] Updated pytest.ini to ignore debug/ folder
- [ ] Delete empty folders: Compiler/, Specification/ (REQUIRES USER)
- [x] Create files/reviews/ directory
- [x] Move AI review files to files/reviews/:
  - ClaudeOpusReview.md
  - ChatGptFusionSummary.md
  - Gemini3ProReview.md
  - GeminiReview.md
- [x] Update taskSummary2.md "Next Action" (already done)
- [x] Run pytest to ensure nothing broke (1,041 passed, 10 skipped)

#### 6.1: Investigate FizzBuzz Issue
- [x] Read examples/fizzbuzz.fusion source code
- [x] Examine generated C code for fizzbuzz
- [x] Identified ROOT CAUSE: Lexer bug in parse_string_interpolation()
  - For "{i}", lexer returned: [('INTERP_VAR', 'i')]
  - Should return: [('STRING_PART', ''), ('INTERP_VAR', 'i'), ('STRING_PART', '')]
  - Parser expects N+1 STRING_PART entries for N interpolations
  - Codegen loops over parts[], but parts=[] → no format specifiers added
- [x] Bug location: src/lexer/literals.py lines 200-204 and 250-252
- [x] Document findings

#### 6.2: Fix FizzBuzz Issue
- [x] Fixed src/lexer/literals.py:
  - Line 202: Always append STRING_PART before interpolation (even if empty)
  - Line 251: Always append final STRING_PART (even if empty)
- [x] Updated 10 failing tests in test_literals.py to expect new format
- [x] Re-compiled fizzbuzz.fusion → generates correct printf("%d\n", i)
- [x] Ran fizzbuzz.exe → correct output: 1, 2, Fizz, 4, Buzz, Fizz, 7, 8, ...
- [x] All 1,041 tests passing, 10 skipped

#### 6.3: Define Expected Outputs
- [x] calculator.fusion: "Sum: 15\nDiff: 5\nProd: 50"
- [x] factorial.fusion: "Factorial of 5 is 120"
- [x] fizzbuzz.fusion: First 15 lines (1, 2, Fizz, 4, Buzz, ..., FizzBuzz)
- [x] hello_world.fusion: "Hello, World!"
- [x] max_three.fusion: "Maximum of 10, 25, 15 is 25"
- [x] sum_array.fusion: "Sum of 1 to 10: 55"
- [x] Updated verify_examples.py with all expected outputs
- [x] Ran verification: 6/6 examples compile, run, and match expected output

#### 6.4: Update verify_examples.py
- [x] Update expected_outputs dictionary with correct values (completed in 6.3)
- [x] Existing output comparison logic works correctly
- [x] Newline handling already implemented (strips trailing whitespace)

#### 6.5: Re-run Full Verification
- [x] Run python tests/verify_examples.py
- [x] Verify all 6 examples compile (6/6 success)
- [x] Verify all 6 examples run (6/6 success)
- [x] Verify all 6 outputs match expectations (6/6 success)
- [x] Generate new verification_report.md (saved to files/reports/)

#### 6.6: Review Generated C Code Quality
- [x] Check calculator.c for correctness - PASS
  - Forward declarations: Correct
  - Function implementations: Correct
  - String interpolation: Working (printf with %d)
  - Return values: Correct
- [x] Check factorial.c for recursion handling - PASS
  - Base case (n <= 1): Correct
  - Recursive case: Correct
  - Tail recursion could be optimized but works correctly
- [x] Check fizzbuzz.c for loop and conditionals - PASS
  - While loop: Correct
  - Nested if/else: Correct logic
  - String interpolation: FIXED (printf("%d\n", i) working)
- [x] Check hello_world.c, max_three.c, sum_array.c - PASS
  - hello_world: Simple printf working
  - max_three: Multiple arguments in printf working (%d, %d, %d, %d)
  - sum_array: For loop correct, printf with %d working
- [x] Document code quality issues:
  - **Minor style observations (not bugs):**
    - Excessive parentheses around expressions: (a + b), ((i % 15) == 0)
    - All headers included even when unused (math.h, string.h)
    - Assignment statements unnecessarily wrapped: i = (i + 1)
  - **Overall assessment: EXCELLENT**
    - All code functionally correct
    - Consistent code generation patterns
    - No bugs or errors found
    - All 6 examples compile and run successfully

**Success Criteria:**
- All examples compile successfully
- All examples run without crashes
- All outputs match expected results
- Generated C code is clean and correct

**Deliverables:**
- Fixed FizzBuzz example
- Updated verify_examples.py with correct expectations
- New verification report (all passing)
- C code quality assessment

---

## TASK 7: Git Integration & GitHub Setup

**Goal:** Set up version control and remote backup
**Status:** Complete ✅
**Priority:** HIGH
**Estimated Effort:** 1-2 hours
**Actual Effort:** ~45 minutes

### Sub-tasks:

#### 7.1: Create .gitignore
- [x] Add Python cache files: `__pycache__/`, `*.pyc`, `.pytest_cache/`
- [x] Add compiled executables: `*.exe`, `*.o`, `*.out`
- [x] Add temporary files: `*.c` (generated C code), `*.tmp`
- [x] Add IDE files: `.vscode/`, `.idea/`
- [x] Do NOT ignore: examples/*.fusion, tests/*.py, src/*.py

#### 7.2: Initialize Local Repository
- [x] Run `git init` in project root
- [x] Run `git add .` (respecting .gitignore)
- [x] Create initial commit: "Initial commit - Fusion compiler MVP complete"
- [x] Verify git status is clean

#### 7.3: Create GitHub Repository
- [x] User creates GitHub repo (name: "fusion-lang" or similar)
- [x] User provides repo URL
- [x] Add remote: `git remote add origin <URL>`
- [x] Push to GitHub: `git push -u origin main`

#### 7.4: Verify Remote Backup
- [x] Check GitHub web interface
- [x] Verify all files uploaded
- [x] Verify .gitignore working (no .exe, __pycache__, etc.)
- [x] Create README.md section about contributing

**Success Criteria:**
- ✅ Git repository initialized
- ✅ All source code committed
- ✅ Remote backup on GitHub
- ✅ Clean git history

**Deliverables:**
- ✅ .gitignore file (excludes .exe, .c, cache, IDE files)
- ✅ Initial git commit (e62d2cf - MVP complete)
- ✅ GitHub repository: https://github.com/EmileAvatar/fusion-lang
- ✅ Backup verification (all files uploaded, .gitignore working)
- ✅ Comprehensive README.md with Contributing section, AI transparency, MIT License

---

## TASK 8: Language Features - const Keyword

**Goal:** Add const variable support
**Status:** Complete ✅
**Priority:** MEDIUM
**Estimated Effort:** 4-6 hours
**Actual Effort:** ~5 hours across sessions

### Sub-tasks:

#### 8.1: Lexer - Add CONST Token
- [x] Add CONST to TokenType enum in src/lexer/token.py
- [x] Add 'const' to keywords.py keyword table
- [x] Write tests for CONST token recognition
- [x] Verify lexer tokenizes const correctly

#### 8.2: Parser - Parse const Declarations
- [x] Update parse_statement() to recognize const
- [x] Modify VarDeclStmt AST node to include is_const flag
- [x] Handle const initialization requirement (const must have initializer)
- [x] Write parser tests for const declarations
- [x] Test error: `const int x;` (no initializer) should fail

#### 8.3: Semantic Analyzer - Validate const
- [x] Add const validation in NameResolver
- [x] Ensure const variables are initialized
- [x] Add const assignment checking in TypeChecker
- [x] Error on reassignment: `const int x = 5; x = 10;` should fail
- [x] Write semantic tests for const violations

#### 8.4: Code Generator - Generate const C Code
- [x] Update visit_VarDeclStmt to emit `const` keyword
- [x] Example: `const int x = 5;` → `const int x = 5;`
- [x] Test generated C code compiles with GCC
- [x] Verify GCC catches const violations

#### 8.5: Integration Testing
- [x] Unskip 2 const tests in test_semantic_integration.py
- [x] Run all tests, ensure they pass
- [x] Create example program using const
- [x] Add const example to examples/

#### 8.6: Documentation
- [x] Update fusion-language-spec.md with const keyword (fixed stale `name: type` syntax to
      match implementation, noted local-only scope, no type inference yet)
- [x] Update CLAUDE.md to remove "const not implemented" note (moved to Current Features;
      Known Limitations now says function-scoped-only instead of "not implemented")
- [x] Add const to README.md features list (already done in Session 21 - verified present)
- [x] Update EBNF grammar with const syntax (already done - verified `variable_declaration`
      in fusion.ebnf already had the `"const" type_name identifier "=" expression` production)

#### 8.7: Verification
- [x] Run python -m pytest tests/ (1057 passed, 8 skipped - all green)
- [x] Run python tests/verify_examples.py (7/7 compile, run, and match - const_demo had no
      expected-output entry, added one to tests/verify_examples.py so it's actually checked
      instead of silently skipped)
- [x] Compile and run const example (examples/const_demo.exe runs correctly)
- [x] Update taskSummary2.md with completion (this edit)

#### 8.8: Git Commit
- [x] git add (scoped to docs/verification files - CLAUDE.md, README.md,
      fusion-language-spec.md, verification_report.md, taskSummary2.md,
      verify_examples.py; Notes/ deletions and the untracked HIDL move were left for a
      separate commit since they're unrelated to const)
- [x] git commit - `3e67816` "docs: Close out Task 8.6-8.8 - const keyword documentation
      and verification" (message broadened from the original placeholder to describe what's
      actually in the diff)
- [x] git push origin main - pushed, fast-forward, no conflicts

**Success Criteria:**
- const keyword recognized by lexer
- const declarations parsed correctly
- const violations detected in semantic analysis
- const emitted in generated C code
- All tests passing (including unskipped const tests)

**Deliverables:**
- const keyword implementation
- 2 previously skipped tests now passing
- Example program using const
- Updated documentation
- Git commit

---

## TASK 9: Language Features - Array Support

**Goal:** Add basic array types and operations
**Status:** Complete ✅ (v1 scope - fixed-size, local-variable arrays; see Task 14 for the
deferred nullable-array/safe-navigation follow-on)
**Priority:** MEDIUM
**Estimated Effort:** 8-10 hours
**Actual Effort:** ~1 session (2026-09-13), after Task 12's Core Typed AST unblocked it

**Recommendation satisfied (2026-09-13):** the 2026-08-04 architecture review recommended doing
Task 12 (Typed AST) before or alongside this task, so array codegen wouldn't inherit the
"codegen guesses the type" problem `print()`/string interpolation had. Task 12.1-12.4 unblocked
this cleanly - array indexing and `len()` read `inferred_type` directly, no guessing.

**Scope decision (2026-09-13):** mid-planning, the user asked for `arr.length` with null-aware
behavior (`arr?.length`) alongside `len(arr)`. That turned out to require a real nullable-
reference-type design (fixed-size C arrays can't be null), a new `.`/`?.` parser feature
(doesn't exist at all yet), and a compile-time null-flow-analysis pass - a language-wide
feature, not a small addition, and exactly the kind of thing Task 12.7's deferred memory-model
work exists to settle first. User agreed to ship plain non-nullable arrays now and track that
work separately - see **Task 14** below.

### Sub-tasks (all complete):

#### 9.1: Design Array Syntax - COMPLETE
- [x] Array declaration: `int[] arr = [1, 2, 3]` (size inferred) or `int[5] arr` (explicit
      size, zero-initialized) or both together (must agree)
- [x] Array indexing: `arr[0]`, `arr[i]` (read and write)
- [x] Array size: `len(arr)` - a builtin function, like `print()`/`range()`; `arr.length` was
      the other option on the table but requires general member-access parsing that doesn't
      exist yet (see Task 14) - not worth building just for this one property
- [x] Documented in `files/fusion-language-spec.md` (new "Arrays" section) and
      `files/fusion.ebnf` (annotated the existing array grammar with what's actually
      implemented vs. still aspirational)
- [x] User approved the syntax and the v1/deferred scope split (2026-09-13)

#### 9.2: Lexer - Array Tokens - COMPLETE (already existed)
- [x] `LBRACKET`/`RBRACKET` were already in `TokenType` and already tokenized by the lexer
      (`src/lexer/operators.py`) - nothing to add here

#### 9.3/9.4: Parser - Array Types, Literals, Indexing - COMPLETE
- [x] `parse_type()` (`src/parser/parser.py`) recognizes `int[]`/`int[5]` after a primitive
      type; rejects multi-dimensional (`int[][]`) and non-literal sizes (`int[n]`) with a
      clear `ParserError`
- [x] New `ArrayType(element_type, size)` TypeNode, `ArrayLiteralExpr(elements)`, and
      `IndexExpr(array, index)` AST nodes in `src/parser/ast_nodes.py`
- [x] Array literals `[1, 2, 3]` (trailing comma allowed) parsed in `parse_primary()`
- [x] Indexing `arr[i]` parsed as a postfix operator in `parse_call()` (renamed in spirit to
      "postfix" - now handles both `(...)` calls and `[...]` indexing in one chained loop,
      matching the EBNF's `postfix` production); array-element assignment (`arr[i] = v`)
      needed no extra parser work - it already falls out of the existing
      expression-then-check-for-`=` statement path
- [x] `src/semantic/name_resolver.py` updated to resolve names inside array literals/indexing

#### 9.5: Semantic Analyzer - Array Type Checking - COMPLETE
- [x] `ArrayType` added to `types_equal`/`types_compatible`/`type_to_string` in
      `type_checker.py` (element-type compatibility with existing numeric promotion, plus
      size matching)
- [x] `visit_ArrayLiteralExpr`: infers element type across all elements (promotes
      int/float/double like binary expressions already do), errors on inconsistent
      non-numeric types
- [x] `visit_IndexExpr`: errors on indexing a non-array, errors if the index isn't `int`
- [x] `visit_VarDeclStmt` extended (`_check_array_var_decl`): resolves the array's size from
      an explicit `[N]`, an initializer's element count, or both (must agree); errors if
      neither is given
- [x] `visit_AssignmentStmt` split into identifier- and index-target paths
      (`_check_identifier_assignment`/`_check_index_assignment`): rejects whole-array
      reassignment (`arr = [...]` after declaration - not supported, see Deliverables),
      enforces const on array elements, checks element type compatibility
- [x] `len()` registered as a builtin (`name_resolver.py`) and special-cased in
      `visit_CallExpr` (accepts exactly one array argument, any element type - the type
      system has no generics, so this mirrors how `range()` is already special-cased)
- [x] Arrays rejected as function parameters/return types in `register_function`, with a
      clear error rather than silently miscompiling (deferred - see Deliverables)
- [x] Bounds checking: explicitly NOT implemented (documented limitation, matches how C
      itself behaves - deferred, not a v1 blocker)
- [x] 22 new semantic tests in `tests/test_array_semantic.py`

#### 9.6: Code Generator - Generate Array C Code - COMPLETE
- [x] `map_type()` maps `ArrayType` to its element's C type; `visit_VarDeclStmt` special-cases
      `ArrayType` to emit real C array declarators (size after the name - `int arr[3]`, not
      `int[3] arr`), zero-initializing (`= {0}`) when there's no literal
- [x] `visit_ArrayLiteralExpr` emits a C brace-initializer (`{1, 2, 3}`) - only valid in C as
      an initializer, which is the only place semantic analysis allows an array literal to
      appear (whole-array reassignment and array arguments are both rejected earlier)
- [x] `visit_IndexExpr` emits plain C indexing (`arr[i]`), valid as both an rvalue and an
      assignment lvalue; `visit_AssignmentStmt` generalized from `target.name` to
      `self.visit(target)` so index-target assignment works through the same code path
- [x] `len(arr)` compiles directly to the array's resolved size as an integer literal (no
      runtime call at all) - sizes are always known at compile time in v1
- [x] Dynamic arrays (`malloc`): explicitly NOT implemented - fixed-size only, documented
      limitation, not a v1 blocker
- [x] 8 new codegen tests in `tests/test_array_codegen.py`, including a full GCC
      compile-and-run round trip

#### 9.7: Integration & Examples - COMPLETE
- [x] `examples/arrays_demo.fusion` - literal/explicit-size declarations, element
      read/write, `len()`, and arrays as local variables inside a helper function
- [x] Compiled and ran manually (verified real runtime output), then added to
      `tests/verify_examples.py`'s expected outputs
- [x] `python tests/verify_examples.py`: 8/8 compile, run, and match

#### 9.8: Documentation & Commit - COMPLETE
- [x] `files/fusion-language-spec.md`: new "Arrays" section (implemented vs. deferred, with
      cross-references to the existing "Array Safe Navigation"/"Null Safety" sections that
      already describe the nullable design Task 14 will build toward)
- [x] `files/fusion.ebnf`: annotated `array_type`, `array_literal`, and `postfix` with what's
      actually implemented vs. still aspirational
- [x] `CLAUDE.md`: added to Current Features/Known Limitations, added a Quick Syntax
      Reference example
- [x] `README.md`: Features, Example Programs, Development Status, and Test Results sections
      updated; corrected test-count drift left over from Task 12 (Code Generation Tests was
      still showing 126, three short of the actual 129 after Task 12's own new tests - fixed
      to the current 137 while updating this line anyway)
- [x] Git commit and push - `47e5116` "feat: Task 9 - fixed-size array support (v1)"

**Success Criteria:**
- [x] Array syntax defined and documented
- [x] Arrays parse correctly (22 semantic + 8 codegen tests, plus manual error-case
      verification of all 7 rejection paths: whole-array reassignment, const violation, size
      mismatch, element type mismatch, non-array indexing, missing size, array parameters)
- [x] Array type checking works
- [x] Arrays compile to C code (verified with a real GCC compile + run, not just unit tests)
- [x] Example program works

**Deliverables:**
- Array type implementation (`ArrayType`/`ArrayLiteralExpr`/`IndexExpr`, fixed-size,
  local-variable-only, single-dimension)
- `len()` builtin, resolved at compile time
- Array example program (`examples/arrays_demo.fusion`)
- Documentation (language spec, EBNF, CLAUDE.md, README)
- Git commit
- **Explicitly deferred, not delivered here**: arrays as function parameters/return types,
  multi-dimensional arrays, non-literal array sizes, whole-array reassignment, dynamic/resizable
  arrays, bounds checking, and everything nullability-related (`.length`, `?.length`, `?[i]`,
  compile-time null-flow analysis) - see Task 14

---

## TASK 12: Compiler Architecture Hardening (Typed AST & Codegen Refactor)

**Goal:** Close the gap where the C code generator guesses types instead of being told them,
before arrays/classes/generics get built on top of that gap.
**Status:** COMPLETE (2026-09-13) - all 12 sub-tasks done: Typed AST (12.1-12.4, 12.9), C
codegen module split (12.5), block-level scoping (12.6), memory model semantics (12.7), docs
sync (12.8), project configuration system (12.12), and two deliberately-deferred design
decisions recorded with rationale (Fusion IR layer, 12.10; stdlib runtime lowering, 12.11)
**Priority:** HIGH (was recommended before Task 9 - now satisfied for Task 9's purposes)
**Actual Effort:** ~2 sessions (2026-09-13) across the Core Typed AST work and this session's
completion of the remaining 8 sub-tasks
**Source:** External review of repo architecture, lexer, parser, semantic analyzer, C backend,
and commit history. Full text archived at `Notes/02/notes.md`.

### Why this task exists

The review's central finding: semantic analysis validates code but doesn't hand the code
generator enough information, so `CCodeGenerator` currently guesses C types/format specifiers
(e.g. `print()` defaulting non-string args to `%s`, interpolation defaulting to `%d`). That
already caused the FizzBuzz bug fixed in Task 6.2. The review recommends fixing this at the
architecture level - a Typed AST - rather than patching individual symptoms, before array/class/
generic work multiplies the number of places that guess wrong.

### Sub-tasks

#### 12.1: Typed AST Design - COMPLETE
- [x] Add `inferred_type` field to expression AST nodes - not a shared `Expr` base class as
      originally proposed (Python dataclass field-ordering rules make a defaulted field on a
      common base incompatible with subclasses adding their own required fields); instead each
      of the 7 expression classes (`LiteralExpr`, `IdentifierExpr`, `BinaryExpr`, `UnaryExpr`,
      `CallExpr`, `LambdaExpr`, `InterpolatedStringExpr`) carries its own trailing
      `inferred_type: Optional[TypeNode] = None` field
- [x] Decided: lives directly on the AST node (mutated in place), not a side-table - the same
      AST object already flows parser -> semantic analyzer -> codegen unmodified (verified via
      main.py), so this needed no pipeline changes to work
- [x] Design recorded here and in code docstrings (src/parser/ast_nodes.py) rather than a
      separate ADR file - didn't need one, the design followed directly from Python/pipeline
      constraints, not an open judgment call
- [x] User approved the approach (2026-09-13) before implementation began

#### 12.2: Semantic Analyzer - Populate Type Information - COMPLETE
- [x] `TypeChecker` already computed the correct type for every expression while validating it
      - it was just discarded. Fix was one hook in `TypeChecker.visit()`'s dispatcher: after
      computing the result, if the node has an `inferred_type` attribute, write the result onto
      it. Centralized in one place rather than editing all 7 `visit_XxxExpr` methods individually.
- [x] Covers every expression type that flows through `visit()`, including inside
      `InterpolatedStringExpr` segments (literals, identifiers, binary/unary expressions, calls)
- [x] Updated semantic test asserting `inferred_type` is set correctly
      (`test_interpolated_string_type` in tests/test_type_checker.py)

#### 12.3: Codegen - Consume Type Information Instead of Guessing - COMPLETE
- [x] Added `_format_specifier_for_expr()` in c_generator.py: reads `inferred_type`, maps
      int->%d, float/double->%f, string->%s, char->%c, bool->%d
- [x] Removed "for MVP, assume string" (`_generate_print_call`'s %s fallback) and "for MVP,
      use %d for most things" (both interpolation format-string builders) - all three now call
      the shared helper instead
- [x] If `inferred_type` is missing/unrecognized, raises `NotImplementedError` with a clear
      internal-compiler-error message instead of silently guessing - matches the existing
      `generic_visit` error convention already used elsewhere in both TypeChecker and
      CCodeGenerator
- [x] Regression tests added: `test_interpolation_uses_actual_type_not_always_d` (float/string
      via interpolation), `test_print_bare_non_string_uses_actual_type` (direct print() arg),
      `test_interpolation_missing_inferred_type_raises` (missing-type error path) - all in
      tests/test_codegen_expressions.py
- [x] Verified for real (not just unit tests): compiled an ad-hoc snippet interpolating
      float+bool+string together - generated
      `printf("Pi is %f, flag is %d, name is %s\n", pi, flag, name)` and ran correctly.
      Before this fix it would have generated `%d` for all three - float reinterpreted as int,
      string pointer printed as a raw integer

#### 12.4: InterpolatedString AST Refactor - COMPLETE
- [x] Replaced parallel `parts: List[str]` / `expressions: List[ASTNode]` arrays with a single
      ordered `segments: List[StringTextPart | StringExprPart]` list on `InterpolatedStringExpr`
- [x] Root cause was one step earlier than the review described: the lexer already emits a
      safe, ordered, tagged sequence (`[('STRING_PART', ...), ('INTERP_VAR', ...), ...]`); the
      parser was the one deliberately splitting that into two parallel arrays. Fix keeps the
      parser's job as "carry the order over," not "reconstruct it later."
- [x] Updated all consumers to the new shape: `ast_nodes.py` (new `StringTextPart`/
      `StringExprPart` classes), `parser.py` (rewrote `parse_interpolated_string_from_parts`;
      also deleted `parse_interpolated_string`, a dead method referencing a JSON shape
      - `token.interpolation` - that's never populated and was never called from anywhere),
      `name_resolver.py`, `type_checker.py`, `c_generator.py` (also de-duplicated
      `visit_InterpolatedStringExpr` and `_generate_interpolated_print`, which were
      near-identical, into one shared `_build_interpolation_format()` helper)
- [x] Re-ran lexer/parser/codegen interpolation tests - updated ~30 call sites across
      tests/test_ast_nodes.py, tests/test_type_checker.py, tests/test_codegen_expressions.py to
      the new segment shape (tests/test_parser_expressions.py's interpolation tests were
      already commented out/dead before this change - left as-is, out of scope here)

#### 12.5: C Codegen Module Split - COMPLETE
- [x] Extracted `c_types.py`: `TypeMapperMixin` with `map_type()`. Kept as a mixin (not a
      standalone function) because it recurses via `self.map_type(...)` for
      `FunctionType`/`ArrayType`, and `tests/test_codegen_infrastructure.py` calls
      `generator.map_type(...)` directly as an instance method
- [x] Extracted `c_names.py`: a plain `mangle_function_name(name)` function (no generator
      state needed) - `CCodeGenerator._mangle_function_name` is now a one-line delegate,
      kept so internal call sites didn't need touching
- [x] Extracted `c_runtime.py`: `RuntimeLoweringMixin` with `_FORMAT_SPECIFIERS`,
      `_format_specifier_for_expr`, `_generate_print_call`, `_generate_len_call`,
      `visit_InterpolatedStringExpr`, `_generate_interpolated_print`,
      `_build_interpolation_format` - a mixin because every method calls `self.visit(...)`,
      and `tests/test_codegen_expressions.py` calls `visit_InterpolatedStringExpr`/
      `_generate_interpolated_print` directly on generator instances
- [x] `CCodeGenerator(TypeMapperMixin, RuntimeLoweringMixin)` - public API (the class name,
      every method name and signature) is completely unchanged; this is purely an internal
      reorganization
- [x] Verified: full suite still 1090 passed, 8 skipped (identical to before the split, no
      count change since no test was added or removed - purely a refactor);
      `verify_examples.py` still 8/8. `c_generator.py`: 962 -> 773 lines (189 lines moved to
      the 3 new files, which add ~110 lines net of new module-level docstrings/cross-refs)

#### 12.6: Scoping Decision - COMPLETE (implemented, not just an ADR)
- [x] **Decision: switched to block-level (lexical) scoping.** User chose this after
      weighing the tradeoffs (RAII/ownership clarity for the upcoming Task 12.7 memory
      model vs. function-scoping's simpler mental model) - see the presented tradeoffs in
      this session's conversation.
- [x] **This turned out to fix a real, live bug, not just a style preference.** Verified by
      compiling `if cond { int x = 10 } print(x)`: semantic analysis said "no errors"
      (function-scoping), but the generated C failed with `gcc: 'x' undeclared` - C's own
      `{ }` braces are natively block-scoped, so the compiler was accepting programs it
      could never actually finish compiling. This was independent confirmation the
      decision was correct, not just architecturally nicer for later.
- [x] Implemented (not deferred as a paper-only ADR, since fixing the bug required real
      code): `BlockStmt`/`ForStmt` gained a `scope` field (Any-typed to avoid a circular
      import with `symbol.py`); `SymbolTable.enter_existing_scope()` lets a later pass
      reuse a scope an earlier pass already populated (Scope.parent is a fixed object
      reference, so lookup_recursive works correctly through reused scopes regardless of
      which pass is walking); `NameResolver.resolve_block()`/`resolve_for()` create a new
      child scope per block/loop and store it on the node; `TypeChecker.visit_BlockStmt()`
      reuses that exact scope (falls back to a fresh one if unset, for isolated unit tests
      that construct AST fragments without running NameResolver first)
- [x] **One real nuance, verified against actual GCC before assuming it**: a function's
      own top-level body must share its parameter scope directly, not nest a new scope
      below it - redeclaring a parameter name at the top level of a C function body is
      itself a C error ('redeclared as different kind of symbol'), confirmed by compiling
      a minimal C repro. `resolve_block()` takes a `new_scope` flag (default True); the
      two call sites that resolve a function's own top-level body
      (`NameResolver.resolve_function` and `semantic_analyzer.py`'s inline orchestration)
      pass `new_scope=False`. For-loop bodies do get their own nested scope below the
      loop-variable's scope - also verified against GCC (a for-body CAN shadow its own
      loop variable in real C).
- [x] **Found and fixed a second, related bug while implementing this**:
      `control_flow_validator.py`'s `validate_conditions()` redundantly re-visits every
      if/while condition via the type checker *after* the main type-checking walk has
      already unwound its scopes - under block scoping this made loop-variable references
      inside conditions fail ("Undefined variable: 'i'") even though the same condition
      had already type-checked correctly the first time. Fixed by having
      `validate_conditions()` re-enter the relevant `.scope` for `ForStmt`/`BlockStmt`
      nodes (falling back to no scope change when `.scope` is unset, preserving its
      existing behavior for the standalone `ControlFlowValidator` unit tests that never
      run `NameResolver` first).
- [x] Updated 5 existing tests that asserted the old function-scoping behavior (their
      names/docstrings described exactly what changed):
      `test_inner_scope_shadows_outer_scope`, `test_variable_not_visible_outside_scope`,
      `test_shadowing_resolution_inner_wins`, `test_variable_in_if_branch_not_visible_outside`
      (all in `tests/test_name_resolver.py`), and `test_variable_shadowing` (in
      `tests/test_semantic_integration.py`)
- [x] Added 6 new regression tests in `tests/test_end_to_end.py` covering: real shadowing
      producing correct runtime output (`test_block_scoping_shadowing_actually_works`),
      the original bug pattern now correctly rejected
      (`test_block_scoping_rejects_use_after_block`,
      `test_block_scoping_rejects_use_after_for_loop`,
      `test_block_scoping_for_loop_variable_out_of_scope_after_loop`), and the
      parameter-redeclaration nuance
      (`test_block_scoping_local_cannot_redeclare_parameter`)
- [x] Verified for real: compiled and ran the shadowing case (`int x=10; if true {int
      x=20; print(x)} print(x)`) - correct output `Inner: 20` / `Outer: 10`; compiled the
      original bug case and confirmed it now fails cleanly at the Fusion semantic-analysis
      stage instead of with a confusing raw GCC error
- [x] Full suite: 1095 passed, 8 skipped (up from 1090 - 6 new tests, 5 modified, none
      weakened). `verify_examples.py`: 8/8 (none of the 8 examples relied on the old,
      buggy cross-block visibility)
- [x] **Known follow-up, not fixed here**: `LambdaExpr` with a `BlockStmt`-style body (as
      opposed to a single-expression body) doesn't get its parameter scope reused
      correctly by `TypeChecker` under this change - `NameResolver.resolve_lambda`
      resolves the block's statements inline without going through `resolve_block`, so the
      block's `.scope` is never set. Not fixed because no current test exercises this path
      and `LambdaExpr` codegen is itself still a stub (`/* <lambda> */`, deferred
      post-MVP) - flagged here rather than silently left broken, safe to defer since this
      part of the language isn't functionally complete regardless

#### 12.7: Memory Model Semantics - COMPLETE (design doc, no code change - as scoped)
- [x] **Decision: `Unique<T>` requires explicit `.move()`.** Plain assignment
      (`Unique<T> b = a`) is a compile-time error, not a silent move (rejected the C++
      `unique_ptr` implicit-move alternative) - every ownership transfer must be visible
      at the call site, including passing a `Unique<T>` into a consuming function
      parameter. Use-after-move is a compile-time error where provable, else a runtime
      crash with a clear message - explicitly noted to share one analysis pass with
      Task 14's null-flow tracking later (moved-from and maybe-null are the same shape
      of problem), not two separate mechanisms.
- [x] **Decision: `Shared<T>` refcounting is always atomic**, not configurable per
      project (rejected the configurable option, despite it fitting Fusion's "agnostic
      per-project configuration" core concept, to avoid two runtime code paths to build/
      test/document before there's a concrete need). **Decision: no automatic cycle
      detection** - documented as a permanent, accepted limitation; `Weak<T>` is the
      required way to break a cycle (matches Swift ARC/Rust `Rc`/ObjC ARC).
- [x] **Decision: `Weak<T>.lock()` returns a nullable `Shared<T>?`, never crashes
      silently.** Caller must null-check. Chosen specifically for consistency with Task
      14's nullable-array direction, so Fusion has one null-handling story across
      features. Noted that once Task 14's `?.` exists, this composes as
      `child.parent.lock()?.doSomething()`.
- [x] All three decisions and their rationale documented directly in
      `files/fusion-language-spec.md`'s existing "Memory Management" section (which
      already had draft Unique/Shared/Weak examples from the original planning phase -
      this pass turned the ambiguous parts of that draft into decided, rationale-backed
      semantics rather than replacing it) - new top-of-section status note makes clear
      this is decided-but-not-yet-implemented (Unique/Shared/Weak are still
      tokenizer-only keywords, confirmed via a source search: no parser/semantic/codegen
      handling exists anywhere in `src/`)
- [x] User decided all three questions via explicit tradeoff presentation (2026-09-13),
      same pattern as Task 12.6's scoping decision - all three chose the recommended
      option
- [x] No code changes made or needed - matches this sub-task's own scope ("design doc,
      no code change"); unblocks Task 14 (Nullable Arrays) to proceed once scoped, since
      Task 14 was blocked specifically on this item

#### 12.8: Documentation Sync Pass - COMPLETE
- [x] Reconciled README.md / CLAUDE.md / language spec with actual implemented features (const
      and arrays were already largely current from Tasks 8/9's own doc updates - this pass
      found and fixed what those missed):
      - **CLAUDE.md**: "Repository is now PRIVATE" was flatly wrong (repo went public
        2026-08-04) - fixed; the entire "CURRENT STATUS" and "Next Steps" sections were dated
        2025-12-14 and described the FizzBuzz bug as unresolved and Tasks 5+ as not started -
        rewrote both to reflect Tasks 5-9 + Task 12 core complete; added missing doc-reference
        table entries (HIDL doc, task-10/11 plans)
      - **README.md**: fixed a stale "126 tests" figure left over from Task 12 (never updated
        after Task 12's own new tests), refreshed the AI-contributor model list (Claude Sonnet
        5 wasn't listed), added `taskSummaryArchive.md` to the doc index
      - **files/fusion-summary.md, files/README.md, files/fusion-planning.md**: all three
        predate compiler implementation entirely and claimed things like `Compiler: Not
        Started 0%` and `README.md: Not Started` - these are now misleading rather than just
        outdated, since the compiler is substantially built. Added a clear "historical
        snapshot, see taskSummary2.md for current status" note to each rather than rewriting
        every stale table cell (matches how `task/taskSummary.md` is already handled - frozen
        and labeled ARCHIVED, not continuously updated)
      - **task/Revisit.md**: "29 failing tests" (from 2025-12-07) is now 0 - all resolved;
        updated the summary table, added a resolved-marker on the historical detail section
        (kept, not deleted - has real value explaining how those issues were fixed), and fixed
        a broken relative link to `taskSummary.md` that pointed at a path that no longer
        exists after that file moved into `task/`
- [x] Confirmed test counts are current everywhere they're stated (1,090 passed / 8 skipped) -
      cross-checked README's per-category test counts (lexer/parser/semantic/codegen/other)
      against actual `pytest --collect-only` groupings rather than just trusting the prior
      numbers; skipped-test reason (single-quote comments vs. char literals) is still accurate
      and unchanged
- [x] Considered the review's suggested doc hierarchy (Language Spec -> ADRs -> Roadmap ->
      Tasks -> Implementation -> Tests): decided not to introduce a separate ADR directory
      right now - Tasks 12.6/12.7/13/14 already function as lightweight ADRs (explicit
      "proposed, not approved" status, rationale, blocked-by relationships), and archiving
      completed tasks out of `taskSummary2.md` (this session's earlier archiving work) already
      addresses the "second spec" bloat concern the suggestion was about

#### 12.9: Verification & Regression - COMPLETE
- [x] Full `python -m pytest tests/` run: 1060 passed, 8 skipped, all green (up from 1057
      passed - added 3 new regression tests, no existing test weakened)
- [x] `python tests/verify_examples.py`: 7/7 compile, run, and match expected output
- [x] Git commit and push - `d7ff009` "feat: Task 12 Core Typed AST - codegen reads types
      instead of guessing"

#### 12.10: Fusion IR Layer - COMPLETE (decision recorded, no code change - deferred)
- [x] **Decision: defer adopting a dedicated Fusion IR layer until Task 11 (LLVM backend)
      actually starts**, rather than adopting a full IR now or even a thin/contract-only
      version now. Presented as a three-way tradeoff (defer / full IR now / thin IR now);
      user chose to defer.
- [x] **Rationale:** exactly one backend exists today (C). Designing an IR now would have
      no real second consumer to validate it against, and would mean reworking the C
      codegen (just cleanly split into modules in Task 12.5) to sit behind a new
      abstraction for zero immediate capability gain. Explicitly weighed against the
      opposite risk (if Task 11 just copies the C backend's AST-walking pattern, retrofitting
      an IR afterward costs more, across two backends instead of one) - accepted that risk
      rather than pay the cost now on a single-backend compiler.
- [x] Recorded a pointer at the point this will actually matter: added a "Revisit at
      kickoff" note to `task/task-11-llvm-backend-plan.md` so this question is re-opened
      with real LLVM requirements in hand before any LLVM codegen is written, rather than
      silently forgotten or silently assumed decided either way.
- [x] Does **not** resolve the separately-flagged Task 10/11 ordering question (whether
      LLVM/IR work should come before self-hosting) - that remains open, unchanged, tracked
      in Task 12's "Open question for user" note below
- [x] No code changes made or needed - matches this sub-task's "design consideration" scope;
      the C backend is completely unaffected

#### 12.11: print() / Stdlib Runtime Lowering - COMPLETE (decision recorded, no code change - deferred)
- [x] **Decision: defer building a general runtime-API lowering layer** (Fusion stdlib call
      -> runtime API -> backend-specific implementation, e.g. `fusion_print_int`/
      `fusion_print_float`) until real stdlib/`import` work is scoped, rather than a
      lightweight registry refactor now or a full runtime-API design now. Presented as the
      same three-way tradeoff shape as Task 12.10; user chose to defer again.
- [x] **Rationale, confirmed by checking the actual code first, not assumed:** exactly two
      builtins are special-cased in `visit_CallExpr` today (`print`, `len`) -
      `src/codegen/c_generator.py:343-346`. A third apparent builtin, `range()`, isn't
      actually a runtime call at all - it's consumed structurally inside `visit_ForStmt`
      as a for-loop pattern, an architecturally different case this layer wouldn't even
      apply to. Confirmed via source search that `import` has zero parser support (lexer
      keyword only) - there is no stdlib call mechanism to lower yet, matching Task 12.10's
      "no real second consumer to validate the abstraction against" reasoning exactly.
- [x] Noted for whoever scopes Fusion's first real `import`/fusionlib module: design the
      runtime-API layer then, informed by what actual stdlib calls need (which types cross
      the boundary, error-handling convention, one shared naming scheme), rather than
      guessing the shape now against a 2-function surface
- [x] No code changes made or needed - matches this sub-task's "design consideration"
      scope; `src/codegen/c_runtime.py`'s existing module docstring already flagged this
      exact question (see Task 12.5's extraction) and is left as-is, now resolved rather
      than open

#### 12.12: Project-Level Language Configuration System - COMPLETE (implemented, not just designed)
- [x] **Decision: TOML, via an optional `fusion.toml` file.** Chosen over YAML (would add a
      new dependency - `requirements.txt` currently has none) and a custom Fusion-native
      format (would mean writing and maintaining a whole new parser for no real benefit).
      Python 3.11's stdlib `tomllib` parses it with zero added dependency - **this raises
      the project's minimum Python version from 3.10 to 3.11** (updated everywhere README.md
      stated it).
- [x] **Decision: lookup is source file's own directory, then the current working
      directory** - not a parent-directory walk like git's `.git`/npm's `package.json`,
      since Fusion has no multi-file project/workspace concept yet (that would solve a
      problem that doesn't exist yet - revisit once it does). A missing file is not an
      error (every setting defaults, identical to the old hardcoded behavior); a *present
      but malformed* file IS a hard error (bad TOML syntax or an invalid value) - never a
      silent fallback to defaults.
- [x] **Decision: implement the concrete gap now (`[indentation]`), document the rest as
      reserved.** New `src/config/project_config.py`: `ProjectConfig`/`IndentationConfig`
      dataclasses, `find_config_file()`, `load_project_config()`, `ProjectConfigError`.
      `[indentation]` (`tab_width`/`allow_mixed`) is fully validated and actually reaches
      the lexer. `[safety]` (`mode`: "normal"/"strict") and `[backend]` (`target`: "c" only
      - "llvm" explicitly rejected with a message pointing at Task 11) are parsed and
      validated (so a project can state intent and typos are caught) but not enforced by
      any pass yet - same "recognized, not implemented" status as `Unique`/`Shared`/`Weak`.
- [x] `src/lexer/lexer.py`'s `Lexer.__init__` gained optional `tab_width`/`allow_mixed`
      parameters (defaulting to the exact previous hardcoded values, so every existing
      direct `Lexer(...)` call site and test is unaffected); `main.py` now loads the
      project config before constructing the lexer and passes both through, with
      `ProjectConfigError` caught and printed as a clean one-line error (exit code 1), not
      a raw Python traceback.
- [x] Verified end-to-end, not just unit-tested: compiled a real file with a line mixing
      spaces and a tab in its indentation - with no `fusion.toml` (or `allow_mixed = true`)
      it compiles with a warning; with `allow_mixed = false` in `fusion.toml` next to it,
      the exact same file now fails to compile with a clear lexer error. Also verified a
      deliberately malformed `fusion.toml` fails cleanly (`Project configuration error:
      Invalid TOML in ...`, exit code 1, no traceback).
- [x] 24 new tests in `tests/test_project_config.py`: discovery/lookup order (including
      source-directory-wins-over-cwd), defaults-when-absent, every valid key, every invalid
      value (malformed TOML, wrong type per key, unknown enum value, `[indentation]` not a
      table), and the actual lexer-wiring path end to end
- [x] `examples/project_config_demo/` - a permanent, manual demonstration (`mixed_indent.fusion`
      + `fusion.toml` + README explaining how to reproduce both outcomes). Deliberately a
      subdirectory, not dropped into `examples/` directly: `tests/verify_examples.py` globs
      `examples/*.fusion` non-recursively, so this demo's `fusion.toml` cannot silently
      change the other 8 examples' behavior - confirmed via a real `verify_examples.py` run
      still showing 8/8 after adding it.
- [x] Full suite: 1119 passed, 8 skipped (up from 1095 - 24 new tests, nothing weakened).
      `verify_examples.py`: still 8/8.
- [x] Documented in `files/fusion-language-spec.md` (new "Project Configuration" subsection
      under "Build and Compilation", including the full schema and every decision's
      rationale), `CLAUDE.md` (file tree, Quick Syntax Reference, Current Features/Known
      Limitations, test counts, Next Steps), and `README.md` (Features, Requirements/Python
      version, project structure tree, Development Status, Test Results)

**Success Criteria:**
- [x] Code generator never guesses a type; it reads `inferred_type` from the semantic pass
- [x] String interpolation is structurally correct (no parallel-array synchronization bugs)
- [x] `CCodeGenerator` responsibilities are split into focused modules (12.5, complete)
- [x] Scoping and memory-model decisions are written down, not implicit (12.6/12.7, complete)
- [x] All existing tests still pass; no behavior regressions

**Deliverables:**
- Typed AST
- Refactored, modular C codegen
- Scoping ADR (implemented)
- Memory model spec (decided and documented; not yet implemented in the compiler)
- Project configuration system (`fusion.toml`, implemented for indentation; safety/backend
  reserved)
- Fully synced documentation
- IR-layer and stdlib-lowering decisions recorded (12.10-12.11 - both deliberately deferred
  with rationale, since neither has a real second consumer yet: only one backend exists for
  12.10, and `import`/stdlib has no parser support at all for 12.11)

**Open question for user:** the review also suggests LLVM/IR work should come before
self-hosting (reversing Task 10/11's current order), which contradicts the explicit
Session 19 decision to plan self-hosting first. Not changed here - flagged for discussion,
not acted on.

---

---

# Moved from taskSummary2.md on 2026-10-09 (Task 22 - tracking restructure)

Verbatim. Finished tasks, finished sub-tasks (18.1, 18.2, 18.3.1, 19.6), resolved
Task 15 items, the old progress table, and session notes 16-28.
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
| **Task 15: Deferred Decisions Revisit List** | In Progress | 42% | 5 | 12 |
| **Task 16: Example Program Coverage** | Not Started | 0% | 0 | 7 |
| **Task 17: Mutable/Fixed Strings & Pooling** | Not Started | 0% | 0 | 5 |
| **Task 18: Core Language Foundation** | In Progress (18.1, 18.2, 18.3.1 done) | 44% | 2 | 5 |
| **Task 19: Library Trust, Isolation & Security** | In Progress (19.6 done) | 14% | 1 | 7 |
| **Task 20: Multi-Format Project Config** | Not Started | 0% | 0 | 4 |
| **Task 21: Error Handling** | Not Started (after 18.3) | 0% | 0 | TBD |
| **Overall** | Task 18.2 Complete | 44% | 54 | 124 |

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

#### 15.3: LambdaExpr Scope Bug - RESOLVED (2026-10-07, as part of Task 18.1.3)
- [x] Fixed: `resolve_lambda()` now calls `resolve_block(new_scope=False)` for a block body, and
      stores the lambda's own scope on `LambdaExpr.scope` so the type checker re-enters it.
      A second, related bug was found and fixed with it: the type checker never entered
      the lambda's scope at all, so a lambda's parameters were undefined inside its body
- [x] (original note) `NameResolver.resolve_lambda()` resolves a `BlockStmt`-bodied lambda's statements
      inline without going through `resolve_block()`, so the block's `.scope` never gets
      set - under block-level scoping (Task 12.6), `TypeChecker.visit_BlockStmt()` falls
      back to creating a fresh scope in this one case instead of reusing the correct one
- [ ] Not fixed during Task 12.6 because no current test exercises this path and lambda
      codegen is itself still a stub (`c_generator.py` emits `/* <lambda> */`) - this was a
      deliberate, flagged deferral, not an oversight
- [ ] Fix: make `resolve_lambda()` call `resolve_block()` properly, once lambda codegen is
      actually implemented and this path becomes reachable by real programs

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

#### 15.9: Printing an Array Crashes the Compiler - RESOLVED (2026-10-08, as part of Task 18.2.1)
- [x] `print("{arr}")` where `arr` is an array fails in codegen with "Internal compiler error:
      no printf format specifier for type 'ArrayType'" - semantic analysis should reject it
      with a normal error (or, later, print the elements). Found during 18.1.2 (verified
      2026-10-07), not fixed there - unrelated to array parameters
- [x] Fixed: the type checker now rejects printing any whole array, struct or function value
      ("Can't print a whole int[3] value - print its elements or fields one at a time").
      Printing the elements automatically is still a possible later feature

#### 15.11: Positional Interpolation `{@1}` Doesn't Work - RESOLVED (2026-10-08, Task 18.2.2b)
- [x] `print("User {@1} is {@2} years old", name, age)` fails with "Function 'print' expects 1
      argument(s), got 2" - `print` is registered with one string parameter, so the extra
      arguments are never accepted. Shown in CLAUDE.md's Quick Syntax Reference and the spec
      as working; CLAUDE.md now marks it as not working. Found during 18.2.2 (2026-10-08).
      Fix: let `print` take extra arguments when its string uses `{@N}`, check each `N` is in
      range, and lower to printf in the referenced order (a `{@1}` used twice repeats the
      argument)

#### 18.1: Functions With Full Parameter Types - COMPLETE (2026-10-07)
**Why first:** functions are the unit of all reusable code - a stdlib, a self-hosted
compiler, or any non-trivial program is built out of them, and today they're restricted.
- [x] **Default parameter values don't actually work** (verified 2026-10-07) - FIXED in 18.1.1: they're parsed
      and type-checked, but calling `greet()` on `void function greet(string name = "World")`
      fails semantic analysis with "expects 1 argument(s), got 0". CLAUDE.md's Quick Syntax
      Reference advertises this syntax, so it's a correctness gap, not just a missing
      feature. C has no default arguments, so codegen must fill omitted arguments in at each
      call site
- [x] Arrays as function parameters - DONE in 18.1.2 (return values moved to 18.2)
- [x] Real lambda codegen - DONE in 18.1.3 (was the placeholder `/* <lambda> */`) - this also
      makes Task 15.3's LambdaExpr scope bug reachable, so fix both together
- [x] Example program per Rule 5 / Task 16 - `examples/functions_demo.fusion`

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
**Status: COMPLETE (2026-10-07)**
- [x] `int[] values` parameter - accepts an array of **any** size. C loses an array's length
      when it's passed, so codegen adds a hidden length parameter: `void f(int* values,
      int values_len)`, and every call passes it (`f(scores, 3)`). `len(values)` inside the
      function compiles to `values_len`
- [x] `int[5] values` parameter - accepts only a 5-element array (checked at compile time);
      `len(values)` stays a compile-time constant
- [x] An `int[]` parameter can be passed on to another `int[]` parameter (its hidden length
      goes with it), but not to an `int[5]` parameter (size unknown at compile time - error)
- [x] **Passing is by reference** (recommended - same as C, Java, C#): the function works on
      the caller's array, so element changes are visible to the caller, and nothing is
      copied. A read-only (`const`) parameter can be added later if wanted
- [x] **Arrays as return values stay rejected** - C can't return an array; this becomes easy
      once structs exist (wrap the array in a struct), so it moves to 18.2
- [x] Still no bounds checking (unchanged - its own future item)
- [x] Also (safety rules added during implementation): element types must match exactly (no
      int -> float promotion - the callee reads the caller's memory directly); a `const`
      array can't be passed (no read-only parameter form yet); an array literal can be
      passed directly (C99 compound literal `(int[]){7, 8}`); array params can't have defaults
- [x] **Found and fixed: `int[] b = a` passed semantic analysis, then failed in GCC**
      (`int b[3] = a;` is invalid C - same bug class as Task 12.6). Arrays can now only be
      initialized from an array literal, with a clear error otherwise
- [x] Logged, not fixed: Task 15.8 (`fusion_` prefix collisions) and 15.9 (`print("{arr}")`
      crashes codegen)
- [x] 15 tests in `tests/test_functions.py`; `test_array_as_function_parameter_fails` (which
      pinned the old deferral) became `..._allowed`; `functions_demo.fusion` extended; spec
      "Array parameters" section. Full suite 1212 passed, 8 skipped; 9/9 examples

**18.1.3 - Lambdas v1 (no closures)**
**Status: COMPLETE (2026-10-07)**
The spec (`fusion-language-spec.md`, "Lambda Expressions") describes function types, inline
lambdas, passing functions as arguments, and closures. v1 builds everything except closures:
- [x] Function type syntax, per spec: `(int, int) : int` (and the `->` alternative) for
      variables and parameters - e.g. `(int) : int op = tripler`
- [x] Inline lambda expressions: `func(int x) : x * 2`, `function(...) : ...`, and the current
      `(int x) : x * 2`. The return type is inferred from the body expression (the parser
      currently records `void` as a placeholder)
- [x] A named function can be used as a value (`apply(tripler, 5)`)
- [x] Calling through a function-typed variable or parameter (`op(5)`)
- [x] Codegen: each inline lambda becomes a private top-level C function
      (`static int fusion_lambda_1(int x)`), and function types become C function pointers.
      Replaces the `/* <lambda> */` placeholder
- [x] Fix Task 15.3 (lambda block-scope bug) at the same time - this makes it reachable
- [x] **Closures (a lambda using a variable from the surrounding function) are rejected** with
      a clear "not yet supported" error. Captured variables must outlive the function that
      created them, which needs heap memory and an ownership rule - the same decision 18.3
      has to make for strings. Revisit after 18.3
- [x] Function-typed variables must be initialized - no `= null` yet (calling a null function
      crashes; nullability is Task 14's design)
- [x] Out of scope: named lambdas declared inside a function body (`int adder(int x) : ...`
      inside another function) - they only matter once closures exist
- [x] Implementation notes: function types become C typedefs (`typedef int
      (*fusion_fn_1)(int);`), so variables, parameters and return types are all plain
      `<type> <name>` in C; functions can return functions (`(int) : int function pick()`);
      calling the result of an expression works (`(func(int x) : x)(5)`); a nested lambda is
      lifted ahead of the lambda that uses it
- [x] Further v1 limits, each with a clear error: lambda parameters can't have defaults or be
      arrays; function types can't have array parameters, and a function with array
      parameters can't be used as a value (a function value can't carry the hidden length);
      builtins (`print`, `len`, `range`) can't be used as values; lambda bodies are single
      expressions (multi-line lambda bodies, which the spec shows, are not supported yet)
- [x] A parser test (`test_error_missing_argument`) passed by accident - it used the reserved
      keyword `func` as a function name, so it failed at `func`, not at the missing argument
      it meant to test. Now uses `foo`
- [x] 22 tests in `tests/test_functions.py`; lambdas added to `functions_demo.fusion`; generated
      C compiles cleanly with `gcc -Wall -Wextra`. Full suite 1234 passed, 8 skipped; 9/9

**Success criteria for 18.1 - all met:** `greet()` with a default compiles and runs; a `sum(int[]
values)` function works on arrays of different sizes; `apply(func(int x) : x * 2, 5)` prints
10; a capturing lambda fails with a clear message; full suite green; 8/8 + new examples.
(Met: `apply(func(int x) : x * x, 7)` gives 49 in the example; closures are rejected with
"Lambda uses 'offset' from the surrounding function - closures ... not supported yet".)

#### 18.2: Structs - COMPLETE (2026-10-09)
**Why second:** the first user-defined composite type, and the lowest-risk way into
user-defined types - a value type maps directly onto a C `struct`, so it needs no runtime,
no inheritance, and no decision yet on how classes/interfaces/traits interact.
- [x] Struct declaration, field access (`.` member access - which also delivers the parser
      piece Task 14 needs for `arr.length`), construction, assignment/copy semantics
- [x] Structs as function parameters/return values (builds on 18.1)
- [x] Arrays as function return values (moved here from 18.1.2 - C can't return an array,
      but it can return a struct wrapping one)
- [x] Nested structs and arrays of structs
- [x] Prerequisite for: classes (Task 16.2), Currency's runtime struct, HIDL register maps,
      AST nodes in a self-hosted compiler
- [x] Example program per Rule 5 / Task 16

### 18.2 Detailed Plan (APPROVED 2026-10-08 - all four parts) - COMPLETE (2026-10-09)

**Ground rule (user note in `fusion-language-spec.md`, "Structure Definition"):** structs are
**pure value types - fields only**. No methods, no operator overloading, no user-written
constructor. The only "constructor" is one the compiler generates, so every field can be set
in one expression ("useful if you need to add all the values at once"). Behaviour belongs in
ordinary functions that take or return the struct.

**Today:** the lexer has `struct` and `.` tokens; the parser, semantic passes and codegen know
nothing about structs. Every type is a keyword today (`int`, `string`...), so the parser must
learn that a plain name like `Point` can be a type.

**User decisions (2026-10-08):**
1. **Nested structs are supported**, with depth limits set in the project config (warn at
   depth 3, maximum depth 3 by default) so a project can switch nesting off or allow more
2. **Both construction forms**: positional `Point(3, 4)` (field order = declaration order,
   the default) **and** named `Point(x = 3, y = 4)`. Named arguments are built now, for
   function calls too, not deferred
3. **A `string` field in a struct is a mutable string, not pooled, by default**, and it
   **grows to fit** - a struct can hold anything from a book title to a full product
   description. Strings are **never cut** below the hard limit. Two separate limits (revised
   2026-10-08 - replaces the earlier "fixed 64-character buffer, cut to fit" idea):
   - `string_warn_length` (default **64**) - only a guideline: a longer string still works,
     the compiler (and later the dev's IDE) just warns
   - `string_max_length` (default **4096**) - the real cut-off, the only place a string is
     ever cut. A project picks its own (e.g. sized for text coming from a database).
     `"max memory"` means no cut-off - **unsafe**, for rare use only
   All of this is controlled from the project config, so a project can also choose pooled
   and/or immutable instead. Purpose: a struct is the convenient way to copy value data
   around a large application and read/change it easily
4. These settings live in the project config file. Today only `fusion.toml` is read; once
   Task 20 lands, the same keys work in `fusion.yaml` / `.json` / `.ini` with no extra work
   (Task 20.1's one shared schema)

**New project settings** (all optional; defaults shown; validated like the existing sections -
a bad value is a config error, never a silent fallback):
```toml
[structs]
max_nesting_depth  = 3         # 1 = no struct may contain another struct; raise to allow deeper
warn_nesting_depth = 3         # warn when a struct reaches this depth (0 = never warn)
string_storage     = "owned"   # "owned" (default: each struct has its own copy) | "pooled" (reserved - Task 17)
string_mutable     = true      # false = a string field can't be changed after construction
string_warn_length = 64        # guideline only: warn when a string field holds more (0 = never)
string_max_length  = 4096      # hard cut-off, or "max memory" = no limit (unsafe, rarely used)
```
- **Depth** counts levels of structs: a struct of plain fields is depth 1; `Rect` holding
  `Point`s is depth 2; a struct holding `Rect` is depth 3. An array of structs counts the same
  as one struct (`Point[4] corners` is still depth 2)
- With the defaults, depth 3 compiles with a warning and depth 4 is a compile error naming
  the chain (`Scene -> Shape -> Rect -> Point is 4 levels deep; max_nesting_depth is 3`)
- `string_storage = "pooled"` is accepted by the validator but rejected at compile time with
  "not implemented yet (Task 17)" - same treatment as `[backend] target = "llvm"` today
- **Length rules:** below `string_warn_length` nothing happens. Above it the string is kept in
  full and the compiler warns (`string field 'description' holds 210 characters; the project
  guideline is 64`). Above `string_max_length` the string is cut to that length, with a
  warning saying so - the only cut-off. `string_max_length` must be >= `string_warn_length`
  (config error otherwise)
- `string_max_length` takes a plain number. TOML can't calculate, so "64 * 64" is written
  `4096`. `"max memory"` turns the cut-off off; the compiler prints an "unsafe setting"
  warning on every build that uses it, and once `[safety] mode = "strict"` is enforced
  (Task 15.6) strict mode will refuse it
- **How "grows to fit" is built (recommended split - please confirm):**
  - **Now, in 18.2:** a string field holds a string value, exactly like a `string` variable
    does today. Assigning any length works with nothing cut (`p.description = "...210
    characters..."`), and assigning a new value is the "mutable" part. Today every string
    in a Fusion program is a fixed piece of text written in the source - there's no way yet
    to build or edit a string while the program runs. So the compiler knows every string's
    length at compile time: the warning and the cut-off both apply now, at compile time, and
    copying a struct already behaves exactly like a full copy
  - **In 18.3 (proper strings):** once programs can build and edit strings at runtime
    (joining, editing characters), a string field becomes its own heap-allocated, growable
    buffer: copied in full when the struct is copied, freed when the struct goes away, with
    the cut-off checked at runtime too. That needs 18.3's "who frees a string" decision,
    which is exactly what 18.3 is for, so building it in 18.2 would mean making that
    decision twice
  - Not pooled by default: each struct copy owns its value. (Two identical pieces of text in
    the source may share storage in the compiled C today, but nothing in Fusion can tell -
    there is no identity operator yet. Pooling as a project choice is Task 17)

Split into four parts, each shippable and committed on its own (same pattern as 18.1). Each
adds tests, extends the example program (Rule 5), and updates spec/EBNF/CLAUDE.md.

**18.2.1 - Core structs**
**Status: COMPLETE (2026-10-08)**
- [x] Declaration, top level only, in all three block styles:
      ```
      struct Point            struct Point {          struct Point
          int x                   int x                   int x
          int y                   int y                   int y
                              }                       End struct
      ```
- [x] v1 field types: `int`, `float`, `double`, `bool`, `char`, `string`. Rejected with a
      clear error: `void`, function types, duplicate field names, an empty struct
- [x] Optional field defaults - same rule as parameter defaults (18.1.1): constant literals
      only: `int hp = 100`
- [x] Declaring a variable: `Point p` -> every field zero / its default (like `float[3] buf`)
- [x] Generated positional constructor, fields in declaration order: `Point(3, 4)`. Fields
      with defaults may be left off the end, exactly like default parameters (reuses 18.1.1's
      call-site filling). Same int -> float promotion as function arguments
- [x] Field read and write with `.`: `p.x`, `p.x = 5`, `p.x + 1`, `print("{p.x}")` (the `.`
      postfix also gives Task 14 the parser piece it needs for `arr.length`)
- [x] **Value semantics** (per spec): `Point b = a` copies; `b.x = 9` leaves `a` alone. Passed
      to functions **by value** (a copy - unlike arrays, which pass by reference) and returned
      by value. Maps directly onto C: structs copy natively
- [x] `const Point ORIGIN = Point(0, 0)` - no field of a const struct can be assigned
- [x] **String fields** per the settings above: any length, never cut below
      `string_max_length`; `string_warn_length` warning; cut-off with a warning above
      `string_max_length`; `"max memory"` unsafe warning; `string_mutable = false` makes field
      assignment after construction an error; `string_storage = "pooled"` -> "not implemented
      yet (Task 17)". Reading `p.name` gives an ordinary `string` (works with `print`,
      parameters, etc.). Runtime growable buffers come with 18.3 (above)
- [x] `[structs]` section added to `src/config/project_config.py` (parse + validate + tests),
      and the config is passed into the semantic analyzer and codegen - today only the lexer
      receives any config (`[indentation]`), so this is new plumbing
- [x] Struct names: may be used before they're declared (like functions); can't clash with a
      function, another struct, or a builtin; a variable/parameter can't reuse a struct's name
      (in C it would hide the type). C keyword names are mangled like functions are
- [x] Clear errors for things not supported yet: `==`/`!=` on structs (equality is 18.3's
      operator-family decision - C can't compare structs either), printing a whole struct
      (`print("{p}")`), arithmetic on structs, unknown field, unknown type name
- [x] Codegen: `typedef struct Point { int x; int y; } Point;` emitted before function typedefs
      and forward declarations; constructor -> C99 compound literal `(Point){3, 4}`; `Point p`
      -> `Point p = {0};` (or with defaults filled in)
- [x] Fix Task 15.9 at the same time (its trigger is "next touch of print/interpolation", and
      this part touches it): `print("{arr}")` gets a clear error instead of crashing codegen
- [x] New example `examples/structs_demo.fusion` (added to `verify_examples.py` -> 10/10)
- [x] **Implementation notes:** the parser treats an identifier in a type position as a struct
      type (`StructType`) and recognises `Point p` / `Point function f()` by lookahead (two
      identifiers in a row never form an expression); unknown names are reported by the name
      resolver ("Unknown type 'X'"), so 4 parser tests that pinned "an identifier is never a
      type" were updated. The lexer accepts dotted paths inside `{...}` (`{p.x}`). A string
      field is a `char*` (fine while every string is a literal - growable buffers are 18.3).
      Unknown keys in `[structs]` are a config error (catches typos). A field with a default
      can only be left off when no later field is given (`max required index` rule)
- [x] **Found and fixed:** arithmetic on a non-number (`arr + 1`, or a struct) crashed the
      compiler with a Python TypeError - `PrimitiveType('void', location=...)` passed 'void'
      as the location in 3 places of `type_checker.py`. Regression test added
- [x] **Found and guarded:** Task 15.10 (interpolated string outside `print()` -> invalid C)
- [x] **Spec rewritten:** "Structures and Value Types" (fields-only rules, construction,
      string fields, value semantics - the user's note in the spec is handled and removed),
      the space-game `Vector2` (now a plain struct + `vadd`/`vscale` functions), the quick
      reference, "Project Configuration" (`[structs]`), and the interpolation section (now says
      honestly that `{age + 1}` expressions aren't implemented yet - only names and field
      paths). EBNF `struct_declaration`/`struct_field`, `.` member access. CLAUDE.md updated
- [x] 79 new tests (`tests/test_structs.py` 64, `tests/test_project_config.py` 15 incl. one
      that compiles through `main.py` with and without a `fusion.toml`); generated C compiles
      cleanly with `gcc -Wall -Wextra`. Full suite 1312 passed, 8 skipped; 10/10 examples

**18.2.2 - Named arguments (function calls and struct construction)**
**Status: COMPLETE (2026-10-08)**
Syntax as the spec already shows it (`fusion-language-spec.md`, "Named Arguments"):
`createShip(crew = 100, name = "Voyager")`, `Point(y = 4, x = 3)`.
- [x] Named arguments in any order; positional and named can be mixed, but **positional must
      come first** (`createShip("Discovery", crew = 80)` ok; `f(a = 1, 2)` is an error)
- [x] Combines with defaults: any parameter/field with a default can be skipped, not only
      trailing ones - `createShip(crew = 200)` uses the defaults for `name` and `speed`
- [x] Errors: unknown name; the same parameter given twice (by position and by name, or named
      twice); a required parameter missing (`missing argument 'b'`)
- [x] Codegen reorders into declaration order and fills defaults (extends 18.1.1's
      `CallExpr.resolved_arguments`); C sees an ordinary positional call
- [x] **Evaluation order:** arguments are evaluated left to right *as written*. C doesn't
      guarantee argument order, so when reordering would change what runs first and an
      argument can have side effects (it contains a call), codegen stores those arguments in
      temporaries first. Otherwise `f(b = next(), a = next())` could silently swap results
- [x] No ambiguity with `=` meaning comparison inside `if` conditions (18.3 decision): inside a
      call's parentheses `name = value` is always a named argument
- [x] Not allowed (clear error): named arguments when calling through a function-type variable
      (`op(x = 5)` - a function type has no parameter names), and on builtins (`print`, `len`)
- [x] Spec: remove "Named arguments ... are not implemented yet"; mark the section implemented
- [x] **Implementation notes:** new AST node `NamedArgument` inside `CallExpr.arguments`
      (written order kept); the parser reads `name = value` at the start of an argument. One
      shared matcher (`TypeChecker._check_named_call`) handles functions and struct
      constructors; calls with no named arguments keep the 18.1.1/18.2.1 code path and
      messages unchanged. After an unknown or misplaced argument, "missing argument" isn't
      also reported (it's usually a side effect). Temporaries are `fusion_arg_N`, declared at
      the top of the C function (or lifted lambda) using them, and sequenced with C's comma
      operator; they're only used when a call has named arguments *and* some argument
      contains a call. Array arguments are never put in temporaries (passed by reference)
- [x] **Not changed (noted):** calls with only positional arguments still leave argument order
      to C, as before - e.g. `f(next(), next())`. Fusion never promised an order there;
      making all calls left-to-right would be a small follow-up if wanted
- [x] **Found and logged, not fixed:** Task 15.11 - positional interpolation `print("{@1}",
      name)` has never compiled (`print` takes one argument), although CLAUDE.md's Quick
      Syntax Reference shows it. CLAUDE.md now marks it as not working
- [x] 25 new tests in `tests/test_structs.py`; `structs_demo.fusion` extended (named struct
      construction and a named function call). Spec "Calling Functions" rules + struct
      section, EBNF `argument`, CLAUDE.md updated. Full suite 1337 passed, 8 skipped; 10/10

**18.2.2b - Positional placeholders `{@N}` and left-to-right argument order** (added
2026-10-08 at the user's request - APPROVED 2026-10-08)
**Status: COMPLETE (2026-10-08)**

User decisions: "both" - left-to-right evaluation is the **default for every call**, and
`{@N}` placeholders must work in any order (`{@3} {@1} {@2}`). Two parts, committed together.

*Part A - left-to-right argument order for all calls (extends 18.2.2's guarantee)*
- [x] Every call's arguments are evaluated left to right as written - positional calls too
      (`f(next(c), next(c))`), struct constructors, and calls through function values
- [x] Same mechanism as 18.2.2 (temporaries + C's comma operator), but only where the order
      could actually be seen, so ordinary calls stay plain C: at least one argument contains
      a call, **and** another argument also contains a call or reads an array element
      (`arr[i]`). Reasoning: in Fusion a call can only change the caller's data through an
      array passed to it (no globals, no closures, structs are copies), so a plain variable
      or literal argument reads the same value whenever it is evaluated
- [x] Not in this part (logged as Task 15.12): the same question for operators -
      `next(c) - next(c)` leaves operand order to C. Recommend the same left-to-right rule
      later

*Part B - positional placeholders in print (closes Task 15.11)*
- [x] `print("User {@1} is {@2} years old", name, age)` - extra arguments after the text are
      referenced by number, starting at 1
- [x] Placeholders in any order and repeatable: `print("{@3} {@1} {@2} {@1}", a, b, c)`
- [x] Each argument is evaluated **once, left to right as written** - whatever order or
      however often the placeholders use it. An argument containing a call goes into a
      temporary first, so a repeated `{@1}` never re-runs the call
- [x] Can be mixed with named values: `print("{name} scored {@1}", total)`
- [x] Errors: `{@N}` with no argument N (`{@3}` with 2 arguments); `{@0}`; extra arguments
      when the text has no `{@N}` at all (today's "expects 1 argument" error, clearer);
      an argument that can't be printed (whole array/struct)
- [x] Warning (not error): an argument that no `{@N}` uses - likely a mistake, but a
      translated message may leave one out on purpose (the spec's i18n use case)
- [x] **Fix the silent bug:** `print("value {@1}")` with no arguments compiles today and prints
      `value 1` - the parser turns `{@1}` into the number 1. It becomes the "no argument 1"
      error above. `{@N}` gets its own AST segment type instead of a fake integer
- [x] Only in `print` for now (interpolated strings only work in `print` - Task 15.10); a
      general `format(...)` waits for runtime strings (18.3)
- [x] Tests, `structs_demo`/`functions_demo` example lines, spec + CLAUDE.md (remove the "not
      working" marks), Task 15.11 closed
- [x] **Implementation notes:** `{@N}` is a new segment type, `StringPositionalPart` (it used to
      be re-parsed as the integer `N`). The type checker special-cases `print` with
      `_check_print_call`. Codegen's ordering rule is `_order_matters` (shared by calls and
      print); print arguments also get a temporary when they contain a call and aren't used
      exactly once. `_contains_call` skips lambda bodies and links to declarations (a
      recursive function's body would otherwise be walked forever). One 18.2.2 test changed:
      a lambda with one call beside a plain variable rightly no longer gets temporaries
- [x] 25 new tests in `tests/test_positional.py`, one AST test updated to the new segment type;
      `structs_demo` prints with out-of-order placeholders. Spec ("Calling Functions"
      evaluation order, placeholder rules) and CLAUDE.md updated. Full suite 1362 passed,
      8 skipped; 10/10 examples

**18.2.3 - Nesting: structs in structs, arrays in structs, arrays of structs**
**Status: COMPLETE (2026-10-08)**
- [x] A struct field can be another struct (`Rect` holding two `Point`s): `r.min.x = 1`.
      Depth limits from `[structs] max_nesting_depth` / `warn_nesting_depth` (above).
      A struct can't contain itself directly or through a cycle (infinite size) - error
      naming the cycle. Codegen orders struct typedefs by dependency
- [x] Fixed-size array fields, size required: `int[3] position` -> `p.position[0] = 5`;
      `len(p.position)` is a compile-time constant; an array field can be passed to an
      `int[]` parameter (by reference, as today). Copying the struct copies the array too
      (true value semantics - C does this natively for arrays inside structs)
- [x] Arrays of structs: `Point[3] pts` (zeroed), `Point[] pts = [Point(1, 2), Point(3, 4)]`,
      `pts[0].x = 7`, passing `Point[]` to a function (by reference, like other arrays)
- [x] Example extended
- [x] **Design detail decided during implementation:** array and struct fields start with their
      own defaults (zero, `""`, or the inner struct's field defaults), so - like a field with a
      written default - they can be left out of a constructor (positionally at the end, or
      skipped by name); they can't have a written default themselves. An array field in a
      constructor takes an array literal of exactly its size (same rule as array variables).
      A whole array field can't be assigned (`t.scores = [...]`) - only its elements
- [x] Depth errors/warnings are reported once, on the struct where the limit is first crossed
      (not on every struct that contains it); a cycle is reported once, naming the chain
- [x] const checks now look through fields and indexes to the variable underneath:
      `c.xs[0] = 5`, `k.a.x = 5`, `P[0].x = 5` and passing `c.xs` to a function are all
      rejected when the variable is const
- [x] Codegen: struct typedefs in dependency order; one shared "default value" builder
      (`_default_value_code`) used for struct variables, omitted fields and arrays;
      all-zero data gets correctly nested braces (`{{0}}` for `Point[3]`) so `-Wall -Wextra`
      stays clean; arrays over 64 elements that need non-zero defaults are filled in a loop
- [x] **Found and fixed:** `string[2] names` (no value) left NULL pointers - printed `(null)`
      here, can crash on other C runtimes. String arrays now start as `""`
- [x] 37 new tests (`tests/test_structs.py` 36 incl. an end-to-end run; `tests/
      test_project_config.py` 1 compiling through `main.py` with `max_nesting_depth = 1`);
      3 tests that pinned the old "not supported yet (18.2.3)" errors removed.
      `structs_demo` shows a nested `Rect`, a `Team` with array fields, and an array of
      structs passed to a function. Spec, EBNF and CLAUDE.md updated. Full suite 1396
      passed, 8 skipped; 10/10 examples

**18.2.4 - Arrays as function return values (moved here from 18.1.2)**
**Status: COMPLETE (2026-10-09)**
- [x] `int[3] function make()` - **fixed size only**; `int[]` as a return type is rejected (the
      caller needs the size at compile time; growable/sized-at-runtime arrays are 18.5's list)
- [x] Codegen wraps the array in a hidden struct C *can* return (`typedef struct { int
      data[3]; } fusion_arr_int_3;`), unwrapped at the call site
- [x] Usable as: `int[3] a = make()`, `a = make()` (whole-array assignment from a call only),
      and `make()[0]`. Element types/sizes must match exactly (as with array parameters)
- [x] Example extended
- [x] **Implementation notes:** each returned array type gets `typedef struct { T data[N]; }
      fusion_arr_T_N;` plus two `static inline` helpers - `_from` (copy an array into the
      wrapper, for `return arr`) and `_copy` (copy a wrapper into an array, for
      `int[3] a = make()` / `a = make()`), both via `memcpy`. `make()[0]` is
      `make().data[0]`. Prototyped in plain C first - clean under `-Wall -Wextra -std=c99`
- [x] Where a returned array may be used is checked in one place (`TypeChecker.visit_CallExpr`
      wraps the old body, now `_visit_call`): stored, assigned (to an array variable *or* an
      array field - the field case was a natural extra), indexed, returned, or ignored.
      Anywhere else (`len(make())`, `print("{@1}", make())`, passing to a function) is an
      error with a hint. `return` accepts a literal of the exact size, or any array of the
      same type and size (variable, parameter, field, call)
- [x] Not supported yet, each with a clear error: unsized `int[]` return types, lambdas and
      function types returning arrays, using an array-returning function as a value, a
      `const` array set from a call
- [x] **Found and fixed while testing:** a one-line function `int[3] function f() : [1, 2, 3]`
      generated invalid C (`return {1, 2, 3};`) - one-line bodies now go through the same
      return handling as `return` statements
- [x] 29 new tests (`tests/test_structs.py`, incl. end-to-end); 2 tests that pinned the old
      "not yet supported as function return types" error now check the unsized-return error.
      `structs_demo` returns an array of structs. Spec ("Array return values"), EBNF and
      CLAUDE.md updated. Full suite 1425 passed, 8 skipped; 10/10 examples

**Out of scope (logged for later):** methods / functions inside structs (never - user
decision; use free functions); struct equality (18.3); printing a whole struct; passing a
struct by reference to avoid copying a large one (a `ref`/`in` parameter form - later);
growable heap string fields (18.3); pooled string fields (Task 17); generic structs; nullable structs
(Task 14); classes (Task 16.2 / after 18.x).

**Spec/doc updates (Auto-Update Policy):** rewrite the spec's "Structure Definition" section
(remove the constructor/operator/method example, and the user note once handled) and its
"Struct Restrictions" list (nested structs now allowed, depth-limited; string fields inline
and mutable by default); rewrite the space-game example's `Vector2` (spec ~line 3047) as a
plain struct plus free functions; check `CacheEntry` (~line 2827); spec "Project
Configuration" section gets `[structs]`; EBNF `struct_declaration` (field defaults, brace /
`End struct` forms) and named arguments in the call grammar; CLAUDE.md Quick Syntax Reference
(structs, named arguments, `[structs]` config) + Current Features; Task 20's key list gains
`[structs]`.

**Success criteria:** a `Point`/`Rect` program builds, copies, nests, passes and returns structs
correctly; `Point(y = 4, x = 3)` and `createShip(crew = 200)` work; `int[3] function make()`
works; mutating a copy never changes the original (string fields included); a 210-character
string field compiles with a warning and is kept in full; changing `max_nesting_depth` /
`string_warn_length` / `string_max_length` in `fusion.toml` visibly changes compiler behaviour;
every rejected case gives a clear error (never a GCC error - the Task 12.6 bug class);
generated C compiles with `gcc -Wall -Wextra`; full suite green; 10/10 examples.

**18.3.1 - String values and automatic cleanup (the foundation)**
**Status: COMPLETE (2026-10-09)**
- [x] A small C runtime emitted into each generated program: `fusion_string` = text pointer
      + length + "owned" flag. Literals cost nothing at run time (they point at the
      program's built-in text and are never freed); only strings built at run time use the
      heap
- [x] Ownership rules (value semantics): storing a string into a variable, field or array
      element gives the owner its own copy - except a freshly built value (a temporary),
      which is simply handed over (moved), so `string s = a + b` copies nothing extra.
      Function parameters borrow the caller's string (no copy); returning a string hands it
      to the caller
- [x] Automatic cleanup: every owned string is freed exactly once when its owner goes away -
      end of its block, and on every exit path (`return`, `break`, `continue`); a
      temporary is freed at the end of the statement that made it. Structs holding strings
      get generated copy/free helpers (copying a struct copies its strings), as do arrays of
      strings
- [x] Content comparison: `==` and `!=` compare the text, not the address (fixes the latent
      bug); `<`, `>`, `<=`, `>=` compare alphabetically (byte order)
- [x] Run-time errors: a small `fusion_runtime_error` that prints `Runtime error at
      file:line: message` and stops the program. Used here for "out of memory", and by
      18.3.2 for bad indexes and conversions
- [x] Everything that uses strings today moves onto the new type unchanged in behaviour:
      literals, `print`, interpolation, parameters and defaults, struct fields, arrays,
      function types
- [x] **Leak check in the test suite:** tests can compile with a counting allocator
      (`-DFUSION_LEAK_CHECK`) that reports any string not freed - or freed twice - when the
      program ends. Every end-to-end string test runs with it, so "freed exactly once" is
      tested, not assumed
- [x] Example `examples/strings_demo.fusion` (-> 11/11)
- [x] **Implementation notes:** new module `src/codegen/c_memory.py` - the C runtime
      (`fusion_string` = data/len/owned; `FUSION_STR(lit)` for source text), the
      "managed type" rules (a string, or a struct/array holding one anywhere), generated
      `fusion_copy_S`/`fusion_free_S`/`fusion_set_S` helpers per string-holding struct,
      cleanup scopes (function / block / loop) and per-statement temporaries. Returned-array
      wrappers of strings deep-copy (`_from`), free the old elements (`_copy`) and can be freed
      (`_free`). Lambdas are now generated through the same statement machinery
- [x] A temporary in a condition is settled into a plain value and freed before the branch
      runs; `while` conditions that make temporaries become `while (1) { ...; if (!c) break; }`
- [x] **Found and fixed during testing:** a temporary on the right of `and`/`or` may be
      skipped, and freeing an unset one was undefined - the leak check caught it as a bad
      free (exit 4). Every temporary now starts as an empty value
- [x] **Found:** `string s` with no value used to be an uninitialized C pointer - it is now `""`
- [x] **Limitation (clear error):** a string-holding variable can't reuse the name of one in
      an enclosing block (the cleanup on `return` would free the wrong one) - codegen error
- [x] **Noted for Task 15.8:** `<stdlib.h>` is now included, so a user function named like a C
      library function (`free`, `exit`, `abs`, ...) collides in GCC - `rename` already did
      (`<stdio.h>`). Same fix as 15.8 (mangle or reserve names)
- [x] The leak check is verified itself (a never-freed string -> exit 3, a double free ->
      exit 4), and **every end-to-end test in the suite** now compiles with it - all pass.
      All 11 examples are leak-free under it too
- [x] 27 new tests (26 in `tests/test_strings.py`, 1 in `test_type_checker.py`); 30 existing tests updated for the new
      representation (`FUSION_STR("...")`, `fusion_string`, `.data` in printf, new includes)
      and one type-checker test (string ordering is now allowed). New example
      `strings_demo.fusion`. Spec "String Implementation" rewritten around the value model;
      the pool, GC and method syntax it described are kept as **planned advanced features
      (after MVP)** - user correction 2026-10-09, they are not dropped. Full suite 1452 passed, 8 skipped;
      11/11 examples

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

**Next Action:** Tasks 18.2.1 (core structs), 18.2.2 (named arguments) and 18.2.2b (`{@N}`
placeholders, left-to-right arguments), 18.2.3 (nesting) and 18.2.4 (array return values)
are complete - **Task 18.2 is done**. **18.3.1** (string values, automatic cleanup) is
complete. Next: **18.3.2 (string operations)** - the 18.3 plan is approved. Then Task 21. Open logged items: Task 15.8 (reserve the `fusion_`
prefix - before 18.4), 15.10 (interpolated strings outside `print()` - real fix in 18.3) and
15.12 (operator operand evaluation order).
Closures wait for 18.3's memory-ownership decision. Task 19.1-19.5 need 18.4 (`import`); Task
20 (multi-format config) is unblocked. Read `FutureFeaturesCaution.md` before picking up
anything from FutureFeatures.md. Completed-task detail for Tasks 5-9 and 12 lives in
`task/taskSummaryArchive.md`.


---

# CLAUDE.md as it was before Task 22 (2026-10-09), verbatim

Status, feature lists and the syntax reference now live in FEATURES.md and
SYNTAX_REFERENCE.md; this copy keeps the old narrative searchable.

## Fusion Programming Language - Claude Code Instructions

**Project:** Fusion Compiler Development
**Icon:** 🏗️ (official)
**Status:** MVP Complete - Post-MVP Development Phase

---

### 🚨 CRITICAL RULES - READ FIRST EVERY SESSION

#### Rule 1: PLAN FIRST, THEN ACT

**NEVER implement without an approved plan!**

1. **Read taskSummary2.md** at session start
2. **Create detailed plan** in taskSummary2.md for ANY new work
3. **Show plan to user** and get approval
4. **ONLY THEN** implement the approved plan
5. **Update taskSummary2.md** after completing each sub-task

**Why:** Prevents AI drift, hallucinations, and wasted effort.

**Example Workflow:**
```
User: "Add const keyword support"
Claude: [Read taskSummary2.md]
Claude: [Add Task 7.X with detailed sub-tasks]
Claude: "Here's my plan... [show plan]. Should I proceed?"
User: "Yes, go ahead"
Claude: [Implement Task 7.X.1]
Claude: [Update taskSummary2.md - Task 7.X.1 complete]
Claude: [Implement Task 7.X.2]
... etc
```

---

### 📋 IMPORTANT NOTES

#### Repository Status
- **Repository is PUBLIC** (made public 2026-08-04, after a git-history scrub removed the
  personal email address that had been in early commits - verified via GitHub API that the
  scrub held and a commit-search for the email returns zero results)
- **Naming Conflict Discovered**: There is an existing programming language called "Fusion"
  - https://github.com/fusionlanguage/fut
  - https://fusion-lang.org/
- **Renaming Plan**:
  - Will continue using "Fusion" name during development
  - Will rename ONLY after language is fully working and stable
  - Rename will happen after we can compile Fusion code to executables without issues
  - No rush - focus is on getting the language working correctly first

---

#### Rule 2: NO EMOJIS IN CODE FILES

**CRITICAL: Emojis cause encoding errors!**

✅ **Emojis OK in:**
- Chat responses
- Markdown files (*.md)
- Comments in markdown

❌ **NEVER use emojis in:**
- Python files (*.py)
- C files (*.c, *.h)
- Any source code files
- Configuration files
- JSON/YAML files

**Why:** Unicode characters cause encoding errors on different systems (cp1252 on Windows, UTF-8 on Linux, etc.)

**Instead of emojis in code, use:**
- `[OK]` not ✓
- `[FAIL]` not ✗
- `[WARN]` not ⚠️
- `# TODO` not 🔴

---

#### Rule 3: Task Tracking

**Active Files:**
- `taskSummary2.md` (ROOT folder) - Post-MVP tasks (Tasks 5+)
- `task/taskSummary.md` (ARCHIVED) - MVP tasks (Tasks 1-4)
- `task/taskSummaryArchive.md` (ARCHIVED) - Completed post-MVP task detail (Tasks 5+)
- `task/task-X.X.md` - Detailed task breakdowns

**Task Numbering:**
- Tasks 1-4: MVP (Phases 1-4) - COMPLETE
- Tasks 5+: Post-MVP (Verification, new features) - ACTIVE

**Update Frequency:**
- After EVERY sub-task completion
- At session start
- At session end

**Archiving Policy (minimize token usage):**
- `taskSummary2.md` grows every session and gets expensive to read into context - keep it
  small by moving fully-completed task sections out of it
- When a whole numbered task (all its sub-tasks) is marked Complete, move that task's full
  section (sub-tasks, success criteria, deliverables) from `taskSummary2.md` to
  `task/taskSummaryArchive.md`, verbatim
- Leave behind a short pointer in `taskSummary2.md` where the section was (task name + status +
  "see task/taskSummaryArchive.md") - do NOT delete the Overall Progress table row or Working
  Notes session history; those stay in the active file
- Do this as part of closing out a task (same session it's completed, or the next time
  `taskSummary2.md` is touched), not as a separate ceremony the user has to ask for each time

---

#### Rule 4: File Organization

**Current Structure:**
```
d:\Dropbox\Fusion\
├── taskSummary2.md           [ACTIVE - Keep in root]
├── CLAUDE.md                 [This file]
├── README.md                 [Project readme]
├── main.py                   [Compiler entry point]
├── task/                     [Task tracking]
│   ├── taskSummary.md        [ARCHIVED - MVP complete]
│   ├── taskSummaryArchive.md [ARCHIVED - completed post-MVP task detail]
│   ├── task-*.md             [Task details]
│   └── Revisit.md            [Technical debt]
├── files/                    [Documentation]
│   ├── *.md specs            [Language specs]
│   └── archive/              [Old versions]
├── src/                      [Source code]
│   ├── lexer/
│   ├── parser/
│   ├── semantic/
│   ├── codegen/
│   ├── config/               [Project config - fusion.toml loading, Task 12.12]
│   └── utils/
├── tests/                    [All test files]
│   ├── test_*.py             [Unit tests]
│   └── verify_examples.py    [Verification script]
├── examples/                 [Example programs]
│   ├── *.fusion              [Fusion source]
│   └── *.exe                 [Compiled executables]
├── FutureFeatures.md         [Post-MVP features - a menu, not commitments]
└── FutureFeaturesCaution.md  [Read before FutureFeatures.md - review, cautions, priorities]
```

**Rules:**
- taskSummary2.md stays in ROOT (active file)
- Use `files/` for documentation
- Use `tests/` for all test scripts
- NO `docs/` folder until compiler goes live

---

### 📍 CURRENT STATUS

**Date:** 2026-10-08
**Phase:** Post-MVP Development - Tasks 5-9 and 12 complete; Task 18 (Core Language) in progress
**MVP Status:** ✅ COMPLETE - see task/taskSummary.md; Tasks 5-9 and 12 also complete (see below)

**Test Results:**
- 1,452 tests passing (99.5%)
- 8 tests skipped (single-quote comment syntax - deferred design decision, conflicts with
  char literals; the earlier 2 skipped const tests were unskipped in Task 8.5)
- 0 tests failing

**Example Verification:**
- 11/11 examples compile, run, and produce correct output (hello_world, factorial, fizzbuzz,
  calculator, sum_array, max_three, const_demo, arrays_demo, functions_demo, structs_demo,
  strings_demo)
- Plus `examples/project_config_demo/` - a manual (not automated-harness) demo of
  `fusion.toml` actually changing compiler behavior (Task 12.12)
- FizzBuzz bug fixed long ago (Task 6.2) - was a lexer bug in interpolation part-splitting

**Completed since MVP:** Task 5 (cleanup), Task 6 (verification/FizzBuzz fix), Task 7 (git/
GitHub), Task 8 (const), Task 9 (fixed-size arrays v1), Task 12 (all 12 sub-tasks: Typed AST,
codegen split, block scoping, memory model semantics, docs sync, project config system, and
two deliberately-deferred design decisions - IR layer and stdlib lowering)

**In progress:** Task 18 (Core Language Foundation). **18.1** (default params, array
params, lambdas) is complete. **18.2 (structs)** has an approved four-part plan; **18.2.1**
(core structs), **18.2.2** (named arguments), **18.2.2b** (`{@N}` placeholders,
left-to-right argument order), **18.2.3** (nesting) and **18.2.4** (array return values) are
complete - **18.2 is done**. **18.3 (proper strings)** has an approved five-part plan;
**18.3.1** (string values, automatic cleanup, comparison) is complete, next is **18.3.2
(string operations)**. Then **Task 21 (error handling)**, scheduled right after 18.3. Task 19.1-19.5 depend on 18.4 (`import`). Guiding rule:
a simple working language first, complex features after (see `FutureFeaturesCaution.md`).
Security principle: **never trust code**.

**Open / not yet scoped:** Task 13 (HIDL module), Task 14 (nullable arrays/safe navigation),
Task 15 (deferred-decisions revisit list), Task 16 (example coverage), Task 17 (mutable/fixed
strings & pooling), Task 10 (self-hosting), Task 11 (LLVM backend) - see taskSummary2.md

**Next:** See taskSummary2.md's "Next Action" line (bottom of file) for the current session's
starting point

---

### 🎯 Core Concept

Fusion is an **agnostic programming language** where developers configure which features, safety levels, and performance systems apply per build or project.

The compiler adapts to project configuration (memory model, locking strategy, strictness level, async behavior).

---

### 📊 MVP Summary (Tasks 1-4 - COMPLETE)

#### Phase 1: Lexer (100% Complete)
- 9/9 tasks complete
- 412 tests passing
- Tokenization, indentation tracking, block styles, keywords, operators, literals, comments

#### Phase 2: Parser (100% Complete)
- 6/6 tasks complete
- 251 tests passing
- AST nodes, expression/statement/declaration parsing, all 3 block styles

#### Phase 3: Semantic Analyzer (100% Complete)
- 6/6 tasks complete
- 230 tests passing
- Symbol table, type checking, name resolution, control flow, entry point validation

#### Phase 4: Code Generator (100% Complete)
- 5/5 tasks complete
- 150 tests passing
- C code generation, GCC integration, end-to-end compilation

**Total:** 1,041 tests passing across all phases

---

### 🗂️ Documentation Reference

| File | Location | Purpose |
|------|----------|---------|
| **taskSummary2.md** | Root | Active task tracking (Tasks 5+) |
| **taskSummary.md** | task/ | Archived MVP tasks (Tasks 1-4) |
| **taskSummaryArchive.md** | task/ | Archived completed post-MVP task detail (Tasks 5+) |
| **task-X.X.md** | task/ | Detailed task breakdowns |
| **Revisit.md** | task/ | Technical debt tracking |
| **fusion.ebnf** | files/ | Grammar specification |
| **fusion-language-spec.md** | files/ | Complete language spec (5000+ lines) |
| **fusion-summary.md** | files/ | High-level overview (historical planning snapshot - predates compiler work, see its own header note) |
| **fusion_specs.md** | files/ | API specifications |
| **fusion-strict.md** | files/ | Strict mode rules |
| **fusion-threading-concurrency.md** | files/ | Threading model |
| **fusion-planning.md** | files/ | Development roadmap |
| **Fusion_Hardware_Interface_Definition_Language_HIDL.md** | files/ | HIDL vision doc (Task 13, blocked/future) |
| **Fusion_domain.md** | files/ | User-facing domain-first feature hierarchy - what Fusion supports/will support, organized by language domain (types, control flow, OOP, memory, concurrency, stdlib), not by build status |
| **task-10-self-hosting-plan.md** | task/ | Self-hosting detailed plan |
| **task-11-llvm-backend-plan.md** | task/ | LLVM backend detailed plan |
| **FutureFeatures.md** | Root | Post-MVP features (IDE, Settings, etc.) - a menu of possibilities, not commitments |
| **FutureFeaturesCaution.md** | Root | Read before FutureFeatures.md: project review, cautions (scope, feature interactions, ecosystem fragmentation), memory-strategy selection guide, library trust/sandboxing/supply-chain security (zero trust in library authors), and why core-language work (Task 18) comes first |

---

### 🔧 Quick Syntax Reference

#### Function Declaration
```fusion
// Return-type-first syntax
<return_type> function <name>(<type> <param> = <default>)

// Examples
int function add(int a, int b) : a + b
void function greet(string name = "World") : print("Hello, {name}!")

// Defaults must come last and be constants (literals, or a negated number); omitted
// trailing arguments are filled in at the call site: greet() -> greet("World") (Task 18.1.1)

// Named arguments (Task 18.2.2): any order, unnamed ones first, any default skippable;
// evaluated left to right as written. Not for builtins or function variables
createShip("Discovery", crew = 80)
int r = sub(b = 5, a = 3)
```

#### Lambdas (Task 18.1.3 - no closures yet)
```fusion
(int) : int op = func(int x) : x * 2     // function type, inline lambda
int function apply((int) : int f, int v) : f(v)
int r = apply(tripler, 5)                // named functions are values too
```

#### Block Styles
```fusion
// 1. Indentation (Python-style)
if condition
    statement1

// 2. Braces (C/Java-style)
if condition {
    statement1
}

// 3. End keyword (VB.NET-style)
if condition
    statement1
End if
```

#### String Interpolation
```fusion
// Inline: {variable}
print("Name: {name}, Age: {age}")

// Positional: {@1}, {@2}, ... - print's arguments after the text, any order, repeatable;
// each argument evaluated once, left to right (Task 18.2.2b)
print("User {@1} is {@2} years old", name, age)
print("{@2} before {@1}", a, b)
```

#### Strings (Task 18.3 - values, freed automatically)
```fusion
string a = "apple"
string b = a            // an independent copy
b = "banana"            // a is still "apple"
bool same = a == "apple"    // compares the text; < and > are alphabetical
```
Joining, `len`, `s[i]`, `substring`, conversions: 18.3.2. `string s = "x is {x}"`: 18.3.3.

#### Variable Declaration
```fusion
// Explicit type (required in safe mode)
int count = 0
string name = "Alice"

// Constant (must initialize)
const float PI = 3.14159
```

#### Arrays
```fusion
// Fixed size, inferred from the literal
int[] scores = [10, 20, 30]

// Explicit size, zero-initialized
float[3] buffer

scores[0] = 99          // element assignment
int n = len(scores)     // size (compile-time constant)

// Array parameters (by reference): int[] = any size (len() works), int[3] = exactly 3
int function sum(int[] values)
int total = sum(scores)

// Array return values need a size (Task 18.2.4)
int[3] function podium() : [3, 1, 2]
int[3] p = podium()     // or: p = podium(), podium()[0]
```

#### Structs (Task 18.2.1 - fields only, value types)
```fusion
struct Point            // also: struct Point { ... }  or  ... End struct
    int x
    int y

struct Player
    string name
    float health = 100.0     // field defaults: constants only

Point a = Point(3, 4)        // generated constructor, fields in declaration order
Point n = Point(y = 4, x = 3)   // named construction (18.2.2)
Point b = a                  // copies; b.x = 9 leaves a alone
Point z                      // every field its default, or zero
a.x = 10
print("({a.x}, {a.y})")      // fields in interpolation
Point function add(Point p, Point q) : Point(p.x + q.x, p.y + q.y)   // by value
```
Nesting (18.2.3): struct fields can be structs and fixed-size arrays (`int[3] scores`,
`Point[2] corners`); arrays of structs (`Point[] pts = [Point(1, 2)]`, `pts[0].x = 7`).
No methods/operators in structs - use functions. Not yet: `==` on structs (18.3), printing a
whole struct.

#### Project Configuration (`fusion.toml`)
```toml
## Optional - place next to your .fusion source file (or in the cwd). Every key defaults
## to the value shown; a missing file is not an error.
## Decided (Task 20, not yet implemented): fusion.yaml / fusion.json / fusion.ini will be
## accepted interchangeably. Until then only fusion.toml works.
[indentation]
tab_width = 4        # spaces per tab
allow_mixed = true   # mixed tabs/spaces: warning (true) vs compile error (false)

[source]
allow_unicode_identifiers = false   # ASCII-only identifiers by default (Task 19.6)

[structs]                      # Task 18.2
max_nesting_depth  = 3         # 1 = no nested structs; depth 4+ is an error by default
warn_nesting_depth = 3         # warn from this depth; 0 = never warn
string_storage     = "owned"   # "pooled" reserved (Task 17) - compile error until then
string_mutable     = true      # false = string fields fixed after construction
string_warn_length = 64        # guideline only: longer strings kept, with a warning
string_max_length  = 4096      # the one hard cut-off; "max memory" = no limit (unsafe)

[safety]
mode = "normal"      # "normal" | "strict" - reserved, not yet enforced (Task 12.12)

[backend]
target = "c"         # "c" only for now - "llvm" reserved for Task 11
```

---

### 🔑 Reserved Keywords (67 total)

**Control Flow:** if, else, for, while, loop, end, break, continue, return, match, case

**Functions:** function, func, async, await

**Classes:** class, struct, interface, enum, inherits, implements, property, get, set

**Modifiers:** public, private, protected, static, virtual, override, abstract, sealed

**Variables:** var, const

**Literals:** true, false, null, this

**Operators:** and, or, not, is, in

**Types:** int, float, double, string, bool, char, byte, short, long, void

**Memory:** Unique, Shared, Weak

**Threading:** go

**Error:** try, catch, finally, throw, Error

---

### 📚 Fusion Standard Library (fusionlib)

**21 Modules Total**

#### Core Libraries (5 modules)
- **Core** - Essential types, Console I/O, DateTime
- **Math** - Vector, Matrix, Quaternion, trigonometry
- **Collections** - List, Dictionary, Set, Queue, Stack, LINQ
- **Threading** - Threads, Goroutines, Channels, Mutex, Async/await
- **IO** - File operations, Streams, Compression

#### Additional Libraries (12 modules)
- **Net** - TCP/UDP, HTTP, WebSocket, DNS, Email, FTP
- **Data** - JSON, CSV, XML, YAML, Markdown, INI
- **System** - Process management, DLL loading, environment
- **Lang** - Multi-language compilation (C, C++, Java, Python)
- **Languages** - i18n/l10n, translations, locale
- **GUI** - HTML5-compliant cross-platform UI
- **Graphics** - 2D/3D rendering, sprites, shaders
- **Audio** - Sound playback, synthesis, effects, MIDI
- **Crypto** - Encryption, hashing, SSL/TLS
- **Database** - SQL/NoSQL support, ORM
- **Web** - HTTP server, REST API framework
- **AI** - Neural networks, ML algorithms

#### IDE & Development (4 modules)
- **Reflection** - Runtime type inspection, dynamic execution
- **Test** - Unit testing framework, assertions, coverage
- **Diagnostics** - Profiling, logging, debugging
- **DocWiki** - Automatic documentation generation

**Import Pattern:** `import Fusion.<ModuleName>` or `import fusionlib.<ModuleName>`

---

### ⚙️ Compiler Implementation Details

**Language:** Python (for MVP)
**Target:** C code → GCC → Native executable
**Future:** Self-hosting (rewrite compiler in Fusion)

**Current Features:**
- Block-level (lexical) scoping: a variable declared inside `if`/`while`/`for` is only
  visible inside that block, and a nested block can shadow an outer variable of the same
  name (Task 12.6, complete - replaced the earlier function-scoped model, which had a
  real bug: semantic analysis accepted programs whose generated C could never actually
  compile, since C's own `{ }` braces are natively block-scoped)
- Three block styles (indentation, braces, End keywords)
- String interpolation ({var}, {p.x}, and positional {@1} placeholders in print - Task 18.2.2b)
- Type checking with automatic int→float promotion
- Recursive functions and lambdas
- void main() → int main() automatic conversion
- C keyword name mangling (function "double" → "fusion_double")
- const declarations: must initialize, enforced immutable by semantic analyzer, emitted as
  C `const` (Task 8, complete)
- Fixed-size arrays: `int[] x = [1,2,3]` or `int[5] x`, element read/write (`x[i]`,
  `x[i] = v`), `len(x)` resolved to a compile-time constant (Task 9 v1, complete)
- Project configuration via an optional `fusion.toml` (source file's directory, then cwd) -
  `[indentation]` (`tab_width`/`allow_mixed`) actually reaches the lexer; `[safety]`/
  `[backend]` are parsed/validated but not yet enforced (Task 12.12, complete - see
  `src/config/project_config.py` and `examples/project_config_demo/`)
- Source-level attack defenses (Task 19.6, complete - `src/lexer/source_security.py`):
  invisible/bidirectional control characters rejected anywhere in a file incl. comments and
  strings (Trojan Source); identifiers ASCII-only by default, opt-in via `[source]
  allow_unicode_identifiers` (mixed look-alike scripts still rejected); `\uXXXX` escapes in
  string and char literals; lexer warnings printed by `main.py`
- Char literals work correctly end-to-end (`char c = 'a'` - was broken before Task 19.6)
- Functions (Task 18.1, complete): parameter default values; arrays as parameters (`int[]` any
  size, `int[5]` exact, by reference); lambdas and function types (`(int) : int`), named
  functions as values, calls through function variables - no closures yet (Task 18.3 first)
- Structs (Task 18.2.1): fields only (no methods), three block styles, generated positional
  constructor, field defaults, `.` access/assignment incl. in `{p.x}` interpolation, value
  semantics (copy on assign/pass/return), const structs, `[structs]` string-field length
  rules (see `tests/test_structs.py`, `examples/structs_demo.fusion`); nesting (18.2.3) -
  struct and fixed-size array fields, arrays of structs, `[structs]` depth limits
- Strings are values (Task 18.3.1): each variable/field/element owns its text, copies are
  independent, and the compiler frees every string exactly once (block end, return, break,
  continue, end of statement for temporaries) - no GC. `==`/`!=` compare text, `<`/`>`
  alphabetical. Tests compile with `-DFUSION_LEAK_CHECK`, which fails a program that leaks
  (exit 3) or double-frees (exit 4) - see `src/codegen/c_memory.py`
- Named arguments (Task 18.2.2): `f(b = 1, a = 2)`, `Point(y = 4, x = 3)` - any order after
  unnamed ones, any defaulted parameter skippable
- Every call's arguments are evaluated left to right as written; `print("{@2} {@1}", a, b)`
  positional placeholders (Task 18.2.2b)

**Known Limitations (by design):**
- Single-quote comments disabled (conflicts with char literals)
- Identifiers are ASCII-only unless `fusion.toml` opts in; char literals hold one ASCII
  character (a C `char` is one byte) - both by design (Task 19.6)

**Known bugs (logged, not yet fixed):**
- Interpolated strings only work as `print()`'s own argument - elsewhere they're now a clear
  error (Task 15.10, they used to generate invalid C); `{...}` holds a name or field path
  (`{p.x}`), not a full expression yet. Building strings at run time is Task 18.3
- Operands of operators (`next(c) - next(c)`) are still evaluated in C's unspecified order -
  call arguments are left to right since Task 18.2.2b; operators are Task 15.12
- const follows the same block scoping as other variables (no global/class-level
  constants yet - classes not implemented)
- `fusion.toml`'s `[safety]`/`[backend]` sections are recognized and validated but not
  enforced by any compiler pass yet (same status as the `Unique`/`Shared`/`Weak` keywords
  below - reserved, not implemented); `[indentation]`, `[source]` and `[structs]` change
  real behavior today
- Arrays can be function parameters (by reference) and sized return values (`int[3]
  function f()`, Task 18.2.4 - a returned array must be stored, assigned, indexed or
  returned, not passed straight on); they're single-dimension, fixed-size (no dynamic resize), no bounds checking, and not nullable (no `.length`,
  `?.`, or `?[` yet - see taskSummary2.md Task 14)

---

### 🔄 Archive Policy

**Ignore unless explicitly requested:**
- `files/archive/*` - Old specification versions
- Single-quote comment tests (8 skipped) - Future design decision

**Technical Debt:**
- See `task/Revisit.md` for deferred issues
- Review before each major release

---

### 🎯 Auto-Update Policy

**When updating any Fusion specification, automatically propagate changes to ALL relevant files:**

| If User Changes... | Must Auto-Update... |
|-------------------|---------------------|
| Lambda syntax | EBNF grammar, language-spec, summary, CLAUDE.md, examples |
| Block syntax | EBNF grammar, language-spec, summary, CLAUDE.md |
| Standard library module | fusionlib table (CLAUDE.md), language-spec, summary |
| Type system | EBNF grammar, language-spec, summary, CLAUDE.md |
| String interpolation | language-spec, CLAUDE.md, code examples |
| Keywords/operators | EBNF grammar, language-spec, summary |

**DO NOT ASK** - just update all files automatically to maintain consistency.

---

### 📝 Session Workflow

**At Session Start:**
1. Read `taskSummary2.md`
2. Check current task status
3. Review any notes from previous session

**During Work:**
1. Create plan in taskSummary2.md for new tasks
2. Get user approval
3. Implement approved plan
4. Update taskSummary2.md after each sub-task

**At Session End:**
1. Update taskSummary2.md with current state
2. Document any blockers or issues
3. Set "Next Action" for next session

---

### 🚀 Next Steps

**Current Focus:** Task 18.3.1 (string values and automatic cleanup) is done. Next: 18.3.2
(string operations), per the approved 18.3 plan in taskSummary2.md; then Task 21 (error
handling). Read
`FutureFeaturesCaution.md` before picking up anything from `FutureFeatures.md`.

**Completed:**
- Tasks 1-9 and 12 - see task/taskSummary.md and task/taskSummaryArchive.md for full detail

**Planned (see taskSummary2.md for full detail and current blockers):**
- Task 13: HIDL module, Task 14: Nullable arrays & safe navigation - both unblocked, need
  scoping approval
- Task 15: Deferred decisions revisit list (IR layer, stdlib lowering, a LambdaExpr scope
  bug, Task 10/11 ordering, etc.) - each item has its own trigger
- Task 16: Example program coverage (16.1 buildable now)
- Task 17: Mutable/fixed strings, templated strings, string pooling - logged, not scoped
- Task 10: Self-hosting, Task 11: LLVM backend (both planning-complete, intentionally not
  started - ordering between them is itself an open question, Task 15.4)

---

### 💻 Setting Up a New Machine

The repo is fully self-describing - no out-of-band context is needed beyond this file and
`taskSummary2.md`. To verify a fresh environment:

1. **Python 3.11+** (required - `src/config/project_config.py` uses stdlib `tomllib`)
2. **GCC on PATH** (MinGW-w64 on Windows) - `main.py` invokes `gcc` directly
3. `pip install -r requirements.txt`
4. `python -m pytest tests/ -q` - expect **1452 passed, 8 skipped**
5. `python tests/verify_examples.py` - expect **11/11**

If both match, the environment is correct. Note `Notes/` (user's AI review notes) and
`.claude/settings.local.json` (Claude Code permissions) are gitignored - they exist only via
Dropbox sync, not via `git clone`.

---

**Last Updated:** 2026-10-08
**Version:** 2.0 (Post-MVP)
**Next Action:** See taskSummary2.md

---

## TASK 22: Project Tracking Restructure (COMPLETE 2026-10-09)

**Goal:** save tokens without losing context (user request). Housekeeping only - no compiler
changes, test count unchanged. One commit.
- [x] 22.1 New `FEATURES.md` (root) - the one status tracker. Line format, grep-friendly:
      top-level `## 18 Core Language Foundation [ ]`; sub-tasks tab-indented, status first:
      `<TAB>[DONE] 18.1 Functions`, `<TAB><TAB>[ ] 18.3.2 String operations`,
      `[POSTPONED to 17.4] String pool` (blocked by a needed feature). Every task 5-21, plus a
      "Later / advanced" part (pool, GC, string methods, closures, ...) and known bugs as items
- [x] 22.2 New `SYNTAX_REFERENCE.md` (root) - a showcase: one short working example per
      implemented feature (functions, named args, lambdas, block styles, arrays, structs,
      strings, interpolation/placeholders, control flow, fusion.toml), plus reserved words.
      Grows as features ship
- [x] 22.3 Slim `CLAUDE.md` to rules + how to run: keep the 4 rules (rewritten tracking
      rule), file layout, auto-update policy (+ the two new files), session workflow, how to
      run/test (incl. leak check), doc pointers. Remove: current status, MVP summary, syntax
      reference, feature/bug lists, next steps (-> FEATURES.md / SYNTAX_REFERENCE.md)
- [x] 22.4 Slim `taskSummary2.md` to a working file: active task's detailed plan + next action
      + latest session note. Completed detail (Tasks 9/12 leftovers, 18.1, 18.2, 18.3.1, 19.6,
      resolved 15.x, sessions 16-28) -> `task/taskSummaryArchive.md` verbatim; not-started
      task write-ups (10, 11, 13, 14, 16, 17, 19.1-19.5, 19.7, 20, 21) -> new
      `task/taskBacklog.md` verbatim, each one line in FEATURES.md
- [x] 22.5 Verify nothing lost (moved line counts match), suite + examples unchanged, commit

---


---

#### 18.3.2 (archived 2026-10-09)

**18.3.2 - String operations**
**Status: COMPLETE (2026-10-09)**
- [x] `a + b` joins two strings (also string + char); numbers are joined with interpolation
      (`"{name}{count}"`) rather than `+`, which avoids JavaScript's `"1" + 1` surprises
- [x] `len(s)`, and `s[i]` reads one character (a `char`). **Bounds-checked**: a bad index
      stops the program with a run-time error - strings know their length, so this is cheap
      (arrays stay unchecked for now)
- [x] Built-in functions (no methods - consistent with fields-only structs):
      `substring(s, start, count)`, `contains(s, part)`, `indexOf(s, part)` (-1 if absent),
      `startsWith`, `endsWith`, `toUpper`, `toLower`, `trim`
- [x] Conversions: `toString(x)` for int/float/double/bool/char; `toInt(s)`, `toFloat(s)`
      (decision 2: invalid text stops the program with a clear run-time error), plus
      `isInt(s)` / `isFloat(s)` to check first
- [x] Length/indexing unit (decision 3): bytes. `len("cafe")` is 4; accented or other
      non-ASCII text counts its UTF-8 bytes. Unicode-aware character functions are later work
- [x] Implementation: runtime functions in `c_memory.py` (`fusion_str_concat`, `_at`,
      `_substring`, `_indexOf`, ..., `fusion_parse_int/float`); built-ins registered in the
      name resolver (names reserved); a joined string is a fresh temporary like a call result.
      Run-time errors carry "file:line". 26 new tests in `tests/test_strings.py`; strings_demo
      and SYNTAX_REFERENCE extended

---

## TASK 23: Examples Folder as a Showcase (COMPLETE 2026-10-09)

**Goal:** `examples/` shows what Fusion can do - for each example the `.fusion` source, the
generated `.c`, and the working `.exe` (after self-hosting: `.fusion` + `.exe` only).
**User decisions:** `.c`, `.exe`, `#list.csv` and `#run.bat` stay **out of git** for now (local
testing/preview only - they reach the other PC through Dropbox); `.fusion` files and
`examples/CLAUDE.md` are in git.
- [x] 23.1 `python check.py --build-examples`: writes each SYNTAX_REFERENCE.md ```fusion block
      to `examples/<section-name>.fusion`, compiles it to `.c` and `.exe`. SYNTAX_REFERENCE.md
      stays the single source. Hand-written demos (hello_world, fizzbuzz, ...) stay too
- [x] 23.2 `examples/#list.csv` - `fusion,c,exe,task,added` per example; existing rows keep
      their date; regenerated by `--build-examples`
- [x] 23.3 `examples/#run.bat` - runs every `.exe`, separated by a blank line,
      `---- name.exe ----`, a blank line; ends with `pause`; regenerated by `--build-examples`
- [x] 23.4 `examples/CLAUDE.md` - the folder's rules (what belongs here; `#list.csv` and
      `#run.bat` are generated, never hand-edited; how to add an example)
- [x] 23.5 Main CLAUDE.md Rule 4 points to it (done with the scheduling update)
- [x] 23.6 Remove the stray `examples/New folder`; `fusion.yaml` -> `files/fusion-overview.yaml`
      (done - it would have been read as a project config once Task 20 lands)

---


---

#### 18.3.2b (archived 2026-10-09)

**18.3.2b - Unicode by default** (user decisions 2026-10-09; APPROVED - "lets continue")
- [x] Config `[strings] encoding = "utf-8"` (default) | `"ascii"`; `"utf-16"` / `"utf-32"`
      listed as possible values but rejected as "not implemented yet" (like `llvm`)
- [x] `fusion_string` gains a character count (`chars`); plain-ASCII text has chars == len,
      the fast path (no scanning). Non-ASCII literals are emitted with their count
- [x] `len(s)` = characters, new `lenb(s)` = bytes; `s[i]`, `substring`, `indexOf` count
      characters (bounds errors too); UTF-8 is decoded/encoded in the runtime
- [x] `char` holds any Unicode character: C type `fusion_char` (32-bit; 1 byte in ascii
      mode); `char c = 'é'` valid; printing/joining/`toString` encode it as UTF-8
- [x] Helpers: `isAscii(s)`, `asciiOnly(s, replacement)`, `charCode(c)`, `fromCharCode(n)`
      (bad code point = run-time error), `byteAt(s, i)` (one byte, bounds-checked)
- [x] ascii mode: a non-ASCII string or char literal is a compile error naming the character
      (moved from the lexer, which used to reject every non-ASCII char literal)
- [x] Tests (incl. é / 日本 / emoji, leak check), SYNTAX_REFERENCE section, spec + FEATURES
- [x] Done 2026-10-09: `fusion_string` gained `chars`; `fusion_char` is uint32_t (unsigned char
      with `#define FUSION_ASCII`); UTF-8 helpers in `c_memory.py`. Found and fixed: the
      end-to-end test helper wrote sources / read output in Windows' cp1252, which can't hold
      e.g. U+65E5 - now UTF-8. 19 new tests (strings + config); syntax_unicode example

---

#### 18.3.3 (archived 2026-10-09)

**18.3.3 - Interpolated strings as values (the real fix for Task 15.10)**
- [x] `string s = "x is {x}"`, `return "Hello, {name}"`, `f("{a}-{b}")` - an interpolated
      string builds a new string anywhere, not only in `print`. Remove the 15.10 guard
- [x] `format("{@2} before {@1}", a, b)` returns the text `print` would print - the same
      placeholder rules as 18.2.2b (any order, repeatable, each argument evaluated once,
      left to right)
- [x] `print` itself is unchanged (still writes directly, no extra copy)
- [x] Done 2026-10-09: `fusion_str_format` (vsnprintf, measured first) builds the string; an
      interpolated value is a fresh temporary like a call result; `format` reuses print's
      placeholder checks. `{@N}` outside print/format is an error. 15 new tests

---

#### 18.3.4 (archived 2026-10-09)

**18.3.4 - Struct string fields become growable (user decision 2026-10-08)**
- [x] Follows from 18.3.1: a string field owns its text, so it holds any length, is copied
      with the struct, and is freed with it
- [x] `[structs] string_max_length` now also applies at run time: a longer value stored into
      a field is cut to the limit (compile-time warnings for literals stay as they are;
      `"max memory"` = no cut). `string_warn_length` stays a compile-time guideline -
      there's nothing useful to warn about while a program runs
- [x] `string_mutable = false` keeps working (no assignment after construction)
- [x] Done 2026-10-09: growable fields came with 18.3.1; added `fusion_str_limit` (cuts by
      character, takes ownership) applied by codegen to non-literal values stored in a field
      or string-array field element; `CCodeGenerator(string_max_length=...)` from fusion.toml.
      Not covered: an array returned by a function copied into an array field (`t.tags =
      names()`) is not limited - noted. 4 new tests incl. a 10,000-character field

---

#### 18.3.4b (archived 2026-10-09)

**18.3.4b - One length limit for every string** (user decisions 2026-10-09 - COMPLETE)
- [x] No limit by default: `[strings] max_length = "max"`; a number is for memory-constrained
      devices or apps, set per project. Replaces `[structs] string_max_length` (the old key
      gives a clear "moved" error) and `"max memory"` with its unsafe-setting warning
- [x] **Too long is always an error, never a cut** (user decision, revised mid-task - a
      `too_long = ignore | warn | error` setting was started and dropped): compile error for
      source text, run-time error with file:line for text built while running
- [x] Checked where strings are made (`fusion_str_make`, `_concat`, `_format`), so it covers
      every string - struct fields, variables, and arrays returned by functions (closing the
      18.3.4 gap). With no limit, no checking code is emitted at all; with a limit, each
      statement records `fusion_at` for the error message
- [x] `[structs] string_warn_length = 64` kept as the compile-time guideline
- [x] Tests rewritten (config, structs, strings); 1509 passed

---

#### 18.3.5 (archived 2026-10-09)

**18.3.5 - The equality operator family (user decisions 2026-10-07 - COMPLETE)**
Decided already: `=` assigns as a statement but compares inside a condition; `==` compares
value; `===` compares type and value. Open points, with recommendations (decision 4):
- [x] `if x = 2` compares like `==` (value) - VB-style readability
- [x] The same rule in `while` and `else if` conditions, for consistency
- [x] Negations as in JavaScript: `!=` is "not `==`" and `!==` is "not `===`". (A
      separate "not `=`" isn't needed, since `=` in a condition already means `==`)
- [x] `==` across types uses a small, explicit table - and nothing else: a number equals
      numeric text (`2 == "2"`, `2.5 == "2.5"`); a char equals a one-character string
      (`'a' == "a"`); int and float compare by value (`2 == 2.0`). Never "truthiness" (no
      bool <-> number/string), never anything else. Any other mixed pair is a compile error
      for `==`, and simply false for `===`
- [x] Structs: `==` compares every field with these same rules; `===` also requires the
      same struct type. Arrays: element by element, same size. (Closes "struct equality"
      deferred from 18.2)
- [x] Every comparison is generated per type - never C's raw `==` on anything that isn't a
      plain number (the root of the pointer-comparison bug)

Implementation (2026-10-09):
- Lexer: `===` / `!==` tokens (three-character operators). Parser: an `if` / `while` / `else
  if` condition is parsed with a flag that lets `=` act as `==` at equality level (named
  arguments `f(x = 2)` still win, as they're matched first)
- Checker: one table for `==` (above); `===` on two different types is a warning ("always
  false"), not an error. Functions can't be compared. Different struct types are `==` when
  they have the same field names in the same order and every field pair compares
- Generator (`c_equality.py`): numbers -> C `==`; number vs text ->
  `fusion_double_eq_str` / `fusion_float_eq_str` (text that isn't a number is simply
  unequal); char vs one-character string -> `fusion_char_eq_str`; structs and arrays ->
  helpers generated on demand (`fusion_eq_A__B`, `fusion_arr_eq_A__B`, length + elements)

---

#### 18.3.5b (archived 2026-10-09)

**18.3.5b - A bool prints as true / false** (user request 2026-10-09 - COMPLETE)
- [x] print, `{...}` interpolation and format() show `true` / `false`; as a value a bool stays 1 / 0
- [x] Expectations in test_strings.py and the strings_demo output updated; new test in test_equality.py

---

#### 18.3.6a (archived 2026-10-09)

**18.3.6a - Groundwork + inspect / search / extract** (COMPLETE)
- [x] Built-ins take optional trailing arguments (`BUILTIN_DEFAULTS` in name_resolver.py,
      filled in through `resolved_arguments` like user defaults): `indexOf(s, part, from = 0)`
- [x] A program's own top-level function or struct may reuse a library built-in's name
      (`left`, `right`, `trim`, ...) and replaces it; print / len / range / format stay reserved
- [x] isEmpty, isBlank, isDigits, isLetters (ASCII + Latin-1), countOf, lastIndexOf,
      indexOf with from, containsAny, left, right - C in the new `src/codegen/c_strings.py`
- [x] The whole runtime compiles warning-free under -Wall -Wextra, UTF-8 and ascii mode
- [x] Fixed on the way: `## String operations` heading -> `####` (Rule 5); its example said
      "bytes" where len counts characters

---

#### 18.3.6b (archived 2026-10-09)

**18.3.6b - Change** (COMPLETE)
- [x] replace / replaceFirst (empty `old` changes nothing), insert, remove (positions must be
      valid, like substring), repeat (negative count and results over 2 GB are run-time
      errors), reverse (by character), trimStart, trimEnd
- [x] Case rules ASCII + Latin-1 in one place (`fusion_str_case`): toUpper / toLower moved
      from c_memory.py and upgraded; capitalize / toTitle change only first letters (acronyms
      survive), words split on whitespace; y-umlaut <-> U+0178; sharp s stays
- [x] Every growing result goes through `fusion_str_take`, so `[strings] max_length` applies

---

#### 18.3.6c (archived 2026-10-10)

**18.3.6c - Padding & alignment** (COMPLETE)
- [x] padLeft / padRight / center with an optional fill char (default ' ', any Unicode
      character); center puts an odd extra fill on the right; wide strings come back unchanged
- [x] truncate(s, width, ending = "...") - at most `width` characters, ending included; an
      ending wider than `width` is itself cut to fit
- [x] Negative widths are run-time errors; the first char / string defaults for built-ins
- [x] Revised (user decision 2026-10-10): truncate adds nothing - `truncate(s, width)` returns
      only the first `width` characters; the optional "..." ending was removed

---

#### 18.3.6d-1 (archived 2026-10-10)

**18.3.6d-1 - Hex, binary, octal, both directions** (COMPLETE)
- [x] User decisions 2026-10-10: negatives in two's complement, C# style, after comparing C,
      C#, Java, Rust (two's complement) with Python, JavaScript, Go (sign + digits);
      bytes as hex now; 0x / 0b / 0o literals with `_` separators
- [x] toHex / toBinary / toOctal / toBase take an int or numeric text (the checker's
      INT_OR_TEXT_BUILTINS; the generator picks fusion_int_* or fusion_str_*), optional width
- [x] fromHex / fromBinary / fromOctal / parseInt / isInt(s, base): prefix, either case, sign;
      32-bit patterns read back as negatives for bases 2 / 8 / 16; base 10 strict
- [x] bytesToHex / hexToBytes with full UTF-8 validation (overlongs, surrogates, > U+10FFFF)
- [x] Literals: hex / binary / octal up to 32 bits (0xFFFFFFFF is -1), `_` between digits in
      every number literal; negative int literals are bracketed in C, INT_MIN written safely

---

#### 18.3.8 (archived 2026-10-10)

**18.3.8 - Raw bytes: `byte` and `bytes` (PLAN APPROVED 2026-10-10)**
User request: strings and ints convert to an array of raw bytes and back, so raw bytes can
be written and transformed by the time Fusion self-hosts. No file reading / writing yet
(Task 18.5). Scheduled now, before 18.3.6d-2.

- **Types:** `byte` - one raw byte, **unsigned 0-255** (decision 1, as C#, Go, Rust, Python;
  the spec's signed Java-style byte changes, a signed `sbyte` is for later); `bytes` - a growable array of
  bytes. `bytes` is a value like `string`: copying gives an independent copy, it's freed
  automatically, it works in struct fields and arrays. Unlike a string it is **edited in
  place**: `b[2] = 0x69`. It holds any bytes at all - no UTF-8 rule
- **Never a silent cut** (user rule): putting 300 into a byte is a compile error for a
  literal and a run-time error otherwise; a byte widens to int automatically
- **Making bytes:** `bytes b` (empty), `bytes b = [0x6B, 0x6B, 0x69]`, `newBytes(n, fill = 0)`,
  `toBytes("kkkkk")` (the UTF-8 bytes), `toBytes('k')`, `toBytes(258)` (4 bytes),
  `hexToRaw("6b6b")`
- **Byte order (decision 2):** little-endian by default (258 -> 02 01 00 00 - x86 / ARM,
  Windows, ZIP and most file formats), with an optional last argument `bigEndian = true` for
  network order: `toBytes(n, bigEndian)`, `getInt(b, at, bigEndian)`, `setInt(b, at, v,
  bigEndian)`, and the same for the 16-bit versions
- **Hex (decision 3, keep both):** `hexToBytes` / `bytesToHex` stay as shipped (text);
  new `hexToRaw(h)` -> bytes (any bytes, no text check) and `rawToHex(b)` -> "6b6b..."
- **Reading:** `b[i]` (bounds-checked), `len(b)`, `b == c` (byte by byte), `slice(b, start,
  count)`, `indexOf(b, pattern, from = 0)`, `getInt(b, at)` (4 bytes), `getInt16` /
  `getUInt16` (2 bytes) - decision 2 for byte order
- **Changing:** `b[i] = x`, `b + c` (join), `b + 0x0A` (append one byte), `setInt(b, at, v)`,
  `setInt16(b, at, v)` - positions outside the bytes are run-time errors
- **Back to text / numbers:** `toString(b)` - the bytes must be valid text (UTF-8, or ASCII
  in an ascii project), else a run-time error; check first with `isText(b)`. `getInt(b, 0)`
  for an int. `rawToHex(b)` -> "6b6b696a6b"
- **Printing (decision 4):** `print("{b}")` shows plain lowercase hex with nothing added -
  "6b6b696a6b" - the raw value only (user: never add characters without the developer's
  consent; display formatting is for downstream modules or the developer's code)
- **In C:** the same struct as a string (data, length, owned), so all of 18.3.1's copy /
  free / move rules apply unchanged - only the Fusion type differs
- Example: the kkkkk -> kkijk edit from the user's question, done on bytes in memory
- [x] Built as planned; `bytes` reuses the string struct in C (c_bytes.py), so 18.3.1's
      ownership rules apply unchanged; setInt / setInt16 count as assignments to their
      first argument (a parameter is copied on entry)
- [x] Found and fixed on the way: unary minus and arithmetic returned the operand's own type
      object, so a literal's "fits in a byte" mark leaked (`byte b = 100 + 200` compiled) -
      both now return a fresh type

---

#### 18.3.6d-2 (archived 2026-10-10)

**18.3.6d-2 - formatNumber** (COMPLETE)
- [x] Excel/.NET style (0 # , . and text around; % multiplies by 100) and printf style
      (a pattern starting with %: one conversion d i f e E g G x X o, flags, width,
      precision, %% and text after) - per the approved plan
- [x] Plan correction: its example "Total: %8.2f kr" didn't start with %, which the rule
      requires; text before a number is Excel style's job ("$0.00")
- [x] Patterns checked by Fusion itself: in src/semantic/number_patterns.py when written in
      the source (compile errors), in the C runtime when built while running; never handed
      raw to printf; %s %n %p * and second conversions rejected
- [x] Rounding half away from zero on the number as written: a float is read at 7
      significant digits, a double / int at 15 (a float 2.675 is 2.67499995 in binary)

---

#### 18.3.6e (archived 2026-10-10)

**18.3.6e - Compare** (COMPLETE)
- [x] equalsIgnoreCase, compareIgnoreCase, compareNatural(a, b, ignoreCase = false); -1 / 0 / 1
      (chosen over "any negative" - easier to test against)
- [x] Case-insensitive by code point with the toLower rules (ASCII + Latin-1)
- [x] Natural order: digit runs by value; leading zeros only break a tie (shorter first), so
      the order is total and deterministic

---

#### 18.3.6 plan and 18.3.6f (archived 2026-10-10)

**18.3.6 - Versatile string functions (PLAN APPROVED 2026-10-09)**
Same pattern as the 18.3.2 built-ins: a signature in `name_resolver.py`, a C name in
`_STRING_BUILTINS`, a C function in the runtime (`c_memory.py`). Each returns a new string;
the input is unchanged; everything counts characters (UTF-8), with the ASCII fast path.
Indexes start at 0, as `s[i]` and `substring` do. Six parts, each committed on its own:

- **18.3.6a Groundwork + inspect / search / extract** - COMPLETE, detail archived
  - Groundwork: optional trailing arguments for built-ins (decision 3), e.g.
    `indexOf(s, part, from = 0)`, `padLeft(s, width, fill = ' ')`
  - `isEmpty(s)` (no characters), `isBlank(s)` (only spaces/tabs/newlines), `isDigits(s)`
    (0-9 only, not empty), `isLetters(s)` (letters only, not empty), `countOf(s, part)`
    (non-overlapping), `lastIndexOf(s, part)`, `indexOf(s, part, from)`,
    `containsAny(s, chars)` (any one of the characters), `left(s, n)`, `right(s, n)`
- **18.3.6b Change** - COMPLETE, detail archived: `replace(s, old, new)` (every match), `replaceFirst`,
  `insert(s, index, part)`, `remove(s, start, count)`, `repeat(s, n)`, `reverse(s)` (by
  character), `trimStart`, `trimEnd`, `capitalize(s)` ("hello world" -> "Hello world"),
  `toTitle(s)` ("hello world" -> "Hello World"). An empty `old` in replace returns `s`
  unchanged; `repeat` with n < 0 is a run-time error
- **18.3.6c Padding & alignment** - COMPLETE, detail archived: `padLeft(s, width, fill)`, `padRight`, `center` (extra
  space goes right), `truncate(s, width)` - the first `width` characters, nothing added (user decision
  2026-10-10, replacing an optional "..." ending) - the result is at most `width`
  characters including the ending. A string already at or past `width` is returned as is
  by the pad functions
- **18.3.6d Number formatting and bases** (DETAILED PLAN APPROVED 2026-10-10) - COMPLETE
  Two sub-parts, each committed on its own:

  **18.3.6d-1 Hex, binary, octal - both directions** (user request 2026-10-10) - COMPLETE
  - To text - from an int **or** from text holding a whole number (`"255"`):
    `toHex(x)` -> "ff", `toBinary(x)` -> "11111111", `toOctal(x)` -> "377", and the general
    `toBase(x, base)` (2-36). Optional minimum width, zero-padded: `toHex(255, 4)` ->
    "00ff", `toBinary(5, 8)` -> "00000101". Lowercase letters (use `toUpper` for "FF").
    Text that isn't a whole number stops with a run-time error, like `toInt`
  - From text - to an int: `fromHex("ff")` -> 255, `fromBinary("101")` -> 5,
    `fromOctal("17")` -> 15, and `parseInt(s, base)` (2-36). Upper or lower case; an
    optional prefix (`0x`, `0b`, `0o`) and a leading `-` are accepted; a value outside int
    or a wrong digit is a run-time error. Check first with `isInt(s, base)` (isInt gets an
    optional base, default 10)
  - Hex text <-> decimal text needs no extra functions: `toString(fromHex("ff"))` -> "255",
    `toHex("255")` -> "ff"
  - Negative numbers (decision A, user 2026-10-10 after comparing languages): **two's
    complement, C# style** - `toHex(-1)` -> "ffffffff", `toBinary(-1)` -> 32 ones,
    `toOctal(-1)` -> "37777777777"; and reading it back gives the negative number again:
    `fromHex("ffffffff")` -> -1. For bases 2, 8 and 16, reading accepts both a 32-bit
    pattern and a leading `-` ("-ff" -> -255); base 10 stays strictly signed (`isInt` /
    `toInt` unchanged). `toBase(n, base)` writes sign + digits ("-ff"), like Java's
    `Integer.toString(n, 16)`. The width pads with zeros: `toHex(-1, 4)` stays "ffffffff"
    (a minimum, never a cut)
  - Literals in source (decision C, yes): `0xFF`, `0b1010`, `0o17` as int literals, with `_`
    allowed between digits (`0b1111_0000`, `1_000_000`); up to 32 bits, read as the bit
    pattern like `fromHex` (`0xFFFFFFFF` is -1)
  - Bytes as hex (decision B, user: both now): `bytesToHex("Hi")` -> "4869" (the UTF-8
    bytes, lowercase), `hexToBytes("4869")` -> "Hi"; odd length, a wrong digit, or bytes
    that aren't valid UTF-8 text (ASCII in an ascii project) are run-time errors

  **18.3.6d-2 formatNumber(n, pattern)** - n is int, float or double; both pattern styles
  (user decision 2026-10-09), chosen per call:
  - **Excel/.NET style** (the pattern doesn't start with `%`): `0` = digit always shown,
    `#` = digit only if needed, `,` in the whole-number part = thousands groups, `.` =
    decimal point, `%` = multiply by 100 and show `%` (as in Excel); any other characters
    before or after are printed as they are (`"$#,##0.00"` -> "$1,234.50",
    `"0.0 kg"`). Rounds half away from zero on the decimal value shown (2.675 with "0.00"
    -> "2.68", as Excel does, despite binary floating point). A minus sign goes in front
  - **printf style** (starts with `%`): one number conversion - `d i` (whole numbers; a
    float is rounded), `f e g` (decimals), `x X o` (hex / octal of a whole number) - with
    flags `- + space 0 #`, width and precision; `%%` for a percent sign; text around it is
    kept after the conversion (`"%8.2f kr"` - text before a number is Excel style's job,
    since the style is chosen by the leading `%`). `%s`, `%n`, `%p`, `*` widths and a second conversion are
    rejected: Fusion checks the pattern itself and never hands it raw to C
  - A bad pattern is a compile error when the pattern is written in the source, and a
    run-time error when it's built while running
  - Separators fixed to `,` and `.` for now; locales (`1.234,50`), negative-number
    sections (`"0.00;(0.00)"`) and scientific notation in Excel style come later

- **18.3.6e Compare** - COMPLETE, detail archived: `equalsIgnoreCase(a, b)`, `compareIgnoreCase(a, b)` and
  `compareNatural(a, b)` - negative / 0 / positive like `fusion_str_cmp`; natural order
  compares digit runs as numbers ("file2" < "file10")
- **18.3.6f Masking - planning overview only** (user decision): a spec section on
  `mask(s, pattern)` for email, phone and custom formats ("a***@x.com", "***-***-1234",
  "(###) ###-####"), with open questions listed. No code

Out-of-range rules (decision 2): `left`, `right`, `truncate` and the pad functions are
"up to n" functions and clamp quietly (`left("ab", 5)` -> "ab"); `insert` / `remove` with
a position outside the string stop with a run-time error, like `substring`. A negative
count or width is always a run-time error.

Letters and case (decision 1): ASCII + Latin-1 letters (a-z plus Western European
accented letters such as e-acute, u-umlaut, n-tilde, sharp s), for isLetters, capitalize,
toTitle, the IgnoreCase functions - and `toUpper` / `toLower` are upgraded to match (today
they only change a-z). Full Unicode case tables are logged for later.

**Decisions (user, 2026-10-09):** 1. ASCII + Latin-1 letters; 2. "up to n" functions clamp
quietly; 3. optional arguments for built-ins; 4. formatNumber takes both Excel/.NET and
printf-style patterns.

Each part: tests (unit + run under the leak check), a `SYNTAX_REFERENCE.md` example,
spec + `FEATURES.md`, `python check.py`, commit and push.
- [x] 18.3.6f: masking design overview written into the spec (two jobs - shaping into a
      pattern and hiding part of a value; proposed API; PCI DSS first-6 / last-4 rule;
      9 open questions). Building it is postponed until the questions are decided
- [x] Masking decisions (user, 2026-10-10): keep the length (crypto handles secrets);
      optional mask character, default *; formatMask fills as far as it fits; placeholders
      # A ? and \; emails show the first character (configurable); no country / phone
      formats - the developer supplies the pattern (maskPhone dropped); core string library;
      named mask; no validation

---

#### 18.3.7 (archived 2026-10-10)

**18.3.7 - Type classes and method syntax (PLAN APPROVED 2026-10-10 - all four decisions as recommended: keep every form; all built-in types; 255.toHex(); same names)**
User request (2026-10-09): every string function reachable as `String.replace(s, a, b)`,
`name.replace(a, b)` and `"Claude".toUpper()`. Fusion has no classes yet, so these are
**built-in type classes** the compiler knows: no objects, no memory or speed cost -
`name.toUpper()` compiles to exactly the same C call as `toUpper(name)` does today.

- **How it works:** `x.f(args)` on a value of a built-in type becomes the built-in `f(x,
  args)`; `String.f(args)` becomes `f(args)`, checked to belong to that class. Chaining
  works: `name.trim().toUpper().padLeft(10)`. A method always means the built-in, even
  when the program has its own function `left` (it can't hide a method)
- **The classes** (decision 2) - each function goes where its first argument's type is:
  - `String` - everything taking text first: `s.toUpper()`, `s.indexOf("a")`, `s.len()`,
    `s.toInt()`, `s.toBytes()`, `s.formatMask(...)` later, ...
  - `Bytes` - `data.getInt(0)`, `data.slice(1, 3)`, `data.rawToHex()`, `data.setInt(0, 5)`
    (changes `data`, so it must be a variable, as now); statics `Bytes.newBytes(8)`,
    `Bytes.hexToRaw("ff")`
  - `Int` - `n.toHex()`, `n.toBinary(8)`, `n.toBytes()`, `n.toString()`,
    `n.formatNumber("#,##0")`; statics `Int.parseInt("ff", 16)`, `Int.fromHex("ff")`
  - `Char` - `c.charCode()`, `c.toString()`, `c.toBytes()`; static `Char.fromCharCode(65)`
  - `Float` / `Double` / `Byte` / `Bool` - `toString`, `formatNumber`, `toBytes` where they apply
  - Text-first functions are also on `String` statically: `String.toUpper(name)`
- **Numbers before a dot** (decision 3): `255.toHex()` - the lexer today reads `255.` as the
  float 255.0. Change: a `.` followed by a letter ends the number
- **Names** (decision 4): a method has the same name as its function (`data.rawToHex()`)
- **The plain functions** (decision 1): what happens to `toUpper(name)`
- **Reserved:** a struct can't be named `String`, `Bytes`, `Int`, `Char`, `Float`, `Double`,
  `Byte` or `Bool`
- **Unchanged:** `print`, `len`, `range` and `format` stay plain functions (`s.len()` also
  works); properties without brackets (`s.length`) wait for real classes
- **Out of scope:** methods on structs (`p.move(1, 2)`) - that is user-defined classes, after
  MVP; extension methods
- Tests, a `SYNTAX_REFERENCE.md` example, spec + EBNF, every existing example still compiling
- [x] Built as planned: the checker rewrites `x.f(a)` / `Class.f(a)` into the built-in call
      (a method uses the built-in symbol table snapshot, so user functions and variables
      can't hide it); the lexer ends a number at `.` + letter
- [x] Refinement: statics that make a value of their class are that class's only
      (`Char.fromCharCode`, not `Int.fromCharCode` or `65.fromCharCode()`); toBytes is both
- [x] Found on the way: gcc -Wformat-truncation in formatNumber, visible only when the
      function is really called - fixed, and a new test compiles the library examples at -O2

---

#### Masking built (archived 2026-10-10)

- [x] formatMask (# A ? and backslash; skips input that doesn't fit; literals appear once
      the next slot fills; stops when input runs out), digitsOnly, mask (keepStart, keepEnd,
      optional char; length kept), maskEmail (keep = 1, optional char; domain kept)
- [x] Implementation choices within the decisions: skipping non-fitting input and lazy
      literals - both make "fill as far as it fits" read naturally

---

#### 18.4.1 (archived 2026-10-10)

**18.4.1 - Names in the generated C** (COMPLETE, closes 15.8)
- [x] Functions and struct types: `fu_` prefix in C (main unchanged) - c_names.mangle_function_name
- [x] Locals / parameters renamed only when they'd break the C (C keywords, printf, pow, C
      type and macro names, `fusion_` / `fu_` / `__` prefixes) - a pass over each function's
      AST after semantic analysis, so messages keep the Fusion names; it also reaches
      `{name}` inside interpolated strings (StringExprPart is a plain dataclass)
- [x] Fields: only C keywords change (c_member_name)
- [x] ~80 exact-C test expectations updated mechanically (function / struct names)

---

#### 18.4.2 (archived 2026-10-10)

**18.4.2 - `import` and module folders** (COMPLETE)
- [x] Parser: `import` lines first (path, `.*`, `as`), dotted struct types (`money.Price`)
- [x] src/modules/loader.py: module = folder next to the main file; each loaded once
      (registered before its own imports, so cycles can't loop); module files may not have
      `main`; module names can't be type classes or contain `__`
- [x] Names rewritten before semantic analysis, scope-aware (a local `square` is left
      alone): own names -> `money.round`; `money.round` / `import M.Name` / `import M.*` /
      aliases -> the internal name; everything merged into one ProgramNode
- [x] Name rules done here (planned for 18.4.3): aliases, the same-module-name error,
      ambiguous `.*` names, an imported name also declared locally
- [x] Imports are per file (as Go / Java / Python) - a file uses only what it imports
- [x] C: `money.round` -> `fu_money__round`; codegen reports two Fusion names sharing a C name
- [x] Fixed on the way: a method call on an undefined receiver reported the error 3 times
