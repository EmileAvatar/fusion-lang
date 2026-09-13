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
