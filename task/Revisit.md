# 🔄 Revisit List - Tests & Issues to Fix Later

**Purpose:** Track skipped tests, failing tests, and technical debt that don't block immediate development.

**Last Updated:** 2025-12-07 (Post-MVP Completion)

**Update (2026-09-13, Task 12.8):** All 39 failing tests described below (GCC-not-installed,
lambda/range parser issues, and the rest) are long resolved - the current suite is 1,090
passed, 8 skipped, 0 failing. The detailed sections below are kept as a historical record of
what those issues were and how they got fixed, not as an open task list. Only the "Skipped
Tests" section (8 single-quote comment tests) still reflects an actual, current, open item.

---

## 📊 Summary

| Category | Count | Status |
|----------|-------|--------|
| **Skipped Tests** | 8 | Deferred - Design decision needed (still current) |
| **Failing Tests** | 0 | ✅ All resolved (was 39 as of 2025-12-07) |
| **Technical Debt** | 0 | None tracked here - see taskSummary2.md Task 15 (Deferred Decisions Revisit List) for architecture-level deferred items |

**Total Items:** 8 (all in "Skipped Tests")

**Note:** MVP Compiler is complete and functional! GCC installed, actively fixing remaining bugs.

**Recent Progress (2025-12-07):**
- ✅ GCC 15.2.0 installed and working
- ✅ Break/Continue type checker fixed
- ✅ range() function now variadic (2-3 args)
- ✅ 10 tests fixed (39 → 29 failures)
- ✅ 1,014/1,051 tests passing (96.5%)

---

## ⏭️ Skipped Tests (8 total)

### Lexer - Single Quote Comment Syntax

**File:** `tests/test_comments.py`

**Tests Affected:** 8 tests
- `test_single_quote_comment_simple`
- `test_single_quote_comment_end_of_line`
- `test_single_quote_comment_multiple_lines`
- `test_single_quote_comment_with_code`
- `test_single_quote_comment_empty`
- `test_single_quote_comment_special_chars`
- `test_single_quote_comment_unicode`
- `test_mixed_comment_styles_with_single_quote`

**What Failed:**
- Single quote `'` as comment delimiter conflicts with character literals (`'a'`, `'b'`, etc.)
- Lexer cannot distinguish between `' this is a comment` and `'a'` (character literal)

**Why Skipped:**
- Design conflict: Same symbol used for two different purposes
- Character literals are higher priority for MVP
- Single quote comments are a "nice-to-have" feature

**When to Fix:**
- After MVP completion
- Requires design decision:
  - Option 1: Remove `'` comment syntax entirely (use only `//` and `/* */`)
  - Option 2: Use context-aware parsing (complex, may slow lexer)
  - Option 3: Change character literal syntax to `"a"[0]` or similar

**Priority:** Low (feature decision required)

**Resolution Path:**
1. Decide on final comment syntax in language spec
2. Update EBNF grammar
3. Update lexer implementation
4. Re-enable tests

---

## ❌ Failing Tests (39 total) - ALL RESOLVED, kept as historical record

### Category 1: GCC Not Installed (26 tests) - **BLOCKING**

**File:** `tests/test_end_to_end.py`

**Tests Affected:** 24 end-to-end tests + 2 integration tests
1. `test_hello_world` - FileNotFoundError (GCC)
2. `test_factorial_recursive` - FileNotFoundError (GCC)
3. `test_even_odd_checker` - FileNotFoundError (GCC)
4. `test_variable_shadowing` - FileNotFoundError (GCC)
5. `test_multiple_return_paths` - FileNotFoundError (GCC)
6. `test_generated_c_compiles_without_warnings` - FileNotFoundError (GCC)
7. `test_executable_runs_without_errors` - FileNotFoundError (GCC)
8. `test_output_matches_expected` - FileNotFoundError (GCC)
9. `test_return_code_zero_for_success` - FileNotFoundError (GCC)
10. `test_return_code_nonzero_for_errors` - FileNotFoundError (GCC)
11. `test_multiple_files_can_be_compiled` - FileNotFoundError (GCC)
12. `test_string_interpolation_multiple_vars` - FileNotFoundError (GCC)
(+ 14 more similar GCC-related failures)

**What Failed:**
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Why Failing:**
- GCC (GNU Compiler Collection) is not installed on the system
- Tests attempt to compile generated C code using `gcc` command
- `subprocess.run(['gcc', ...])` fails because `gcc.exe` is not in PATH

**When to Fix:**
- **IMMEDIATE** - Task 2: Install GCC
- Required for end-to-end testing and actual compilation

**Priority:** **CRITICAL** (blocks actual compilation to executables)

**Resolution Path:**
1. Install MinGW-w64 or TDM-GCC on Windows
2. Add GCC bin directory to system PATH
3. Verify with `gcc --version`
4. Re-run tests - should pass automatically

---

## ❌ Failing Tests (continued)

### Category 2: Parser Issues with Lambda Functions and Range (4 tests)

**File:** `tests/test_end_to_end.py`

**Tests Affected:**
1. `test_sum_range` - ParserError: Expected parameter name
2. `test_lambda_functions` - ParserError: Expected function name
3. `test_large_program` - ParserError: Expected parameter name

**What Failed:**
- Parser doesn't handle inline lambda syntax after function name correctly
- `int function double(int x) : x * 2` fails with "Expected function name"
- Range function parameters cause parsing issues

**Why Failing:**
- Lambda syntax parser may need adjustments for specific edge cases
- Parser expects specific token sequence that lambda syntax doesn't match

**When to Fix:**
- Task 3 - Review parser lambda handling
- May need to relax parser expectations or adjust lambda syntax

**Priority:** High (blocks lambda function testing)

**Resolution Path:**
1. Review parser lambda expression handling in [src/parser/parser.py](../src/parser/parser.py)
2. Debug with `-v` flag to see exact token sequence
3. Fix parser to handle all lambda variations
4. Re-run tests

---

### Category 3: Semantic Analysis Issues (7 tests)

**File:** `tests/test_end_to_end.py` and `tests/test_semantic_integration.py`

**Tests Affected:**
1. `test_factorial_iterative` - Semantic errors (undefined variables in block scope)
2. `test_fizzbuzz` - Semantic errors
3. `test_calculator` - Semantic errors
4. `test_max_three` - Semantic errors
5. `test_simple_counter` - Semantic errors
6. `test_nested_loops` - Semantic errors
7. `test_complex_expressions` - Semantic errors (undefined variables)

**What Failed:**
- Tests expect code to pass semantic analysis but get "Undefined variable" errors
- Variables declared in if/while/for blocks not visible in same block
- Block-level scoping issues

**Why Failing:**
- Semantic analyzer may be creating new scopes too aggressively
- Variables declared inside blocks should be visible in that block
- Scoping rules need review

**When to Fix:**
- Task 3 - Review semantic analyzer scope management
- Check symbol table push/pop logic

**Priority:** High (blocks basic programs)

**Resolution Path:**
1. Review [src/semantic/name_resolver.py](../src/semantic/name_resolver.py) scope handling
2. Check if/while/for statement scope creation
3. Ensure variables are visible in their declaration scope
4. Run unit tests to verify fix doesn't break other scoping

---

### Category 4: Break/Continue Code Generation (1 test)

**File:** `tests/test_end_to_end.py`

**Tests Affected:**
1. `test_break_continue` - NotImplementedError: No visitor for BreakStmt

**What Failed:**
```
NotImplementedError: No visitor for BreakStmt
```

**Why Failing:**
- Code generator has `visit_BreakStmt` and `visit_ContinueStmt` methods
- But AST nodes need to be imported in the code generator file
- Import statement missing `BreakStmt` and `ContinueStmt`

**When to Fix:**
- Task 3 - Add imports to code generator

**Priority:** Medium (visitor methods exist, just import issue)

**Resolution Path:**
1. Check imports in [src/codegen/c_generator.py](../src/codegen/c_generator.py:15)
2. Verify `BreakStmt` and `ContinueStmt` are imported
3. Test should pass immediately

---

### Category 5: Lexer Error Handling Test (1 test)

**File:** `tests/test_end_to_end.py`

**Tests Affected:**
1. `test_lexer_errors_prevent_compilation` - LexerError instead of AssertionError

**What Failed:**
- Test expects `AssertionError` with message "Lexer errors"
- Actually gets `LexerError` exception

**Why Failing:**
- Test uses `pytest.raises(AssertionError, match="Lexer errors")`
- But `compile_and_run()` raises `LexerError` directly
- Test expectation mismatch

**When to Fix:**
- Task 3 - Update test expectation

**Priority:** Low (error detection works, just test issue)

**Resolution Path:**
1. Update test to expect `LexerError` instead of `AssertionError`
2. Or update `compile_and_run()` to wrap in AssertionError

---

### Category 6: Semantic Integration Tests (Old Issues - 13 tests)

**File:** `tests/test_semantic_integration.py`

**File:** `tests/test_semantic_integration.py`

**Tests Affected:**
1. `test_factorial_iterative` - Line assertions fail
2. `test_fizzbuzz` - Line assertions fail
3. `test_calculator` - Line assertions fail
4. `test_type_promotion` - Line assertions fail

**What Failed:**
- Tests expect certain number of errors/warnings but get different counts
- String interpolation (`"Result: {x}"`) works in unit tests but has minor issues in full pipeline

**Why Failing:**
- Integration tests check end-to-end behavior including string interpolation
- Lexer correctly tokenizes interpolation, but integration layer has assertion mismatches
- Core functionality works - this is a test expectation issue

**When to Fix:**
- During Task 4.2 (Expression Code Generation) - will implement proper interpolation handling
- Or during Task 4.5 (Integration Testing) - will update test expectations

**Priority:** Medium (will naturally resolve during code generation)

**Resolution Path:**
1. Implement string interpolation code generation in Task 4.2
2. Run integration tests again
3. Update test assertions if needed

---

### Category 2: Break/Continue Statement Visitor Methods (2 tests)

**File:** `tests/test_semantic_integration.py`

**Tests Affected:**
1. `test_break_outside_loop` - NotImplementedError
2. `test_continue_outside_loop` - NotImplementedError

**What Failed:**
```
NotImplementedError: No visitor for BreakStmt
NotImplementedError: No visitor for ContinueStmt
```

**Why Failing:**
- Break and Continue statements were added to AST in Phase 3
- Code generator (Phase 4) hasn't implemented visitor methods yet
- These are expected failures until we complete Task 4.3 (Statement Code Generation)

**When to Fix:**
- Task 4.3 (Statement Code Generation) - will implement `visit_BreakStmt` and `visit_ContinueStmt`

**Priority:** High (needed for MVP control flow)

**Resolution Path:**
1. In Task 4.3, add visitor methods to CCodeGenerator:
   - `visit_BreakStmt(self, node)` → emit "break;"
   - `visit_ContinueStmt(self, node)` → emit "continue;"
2. Tests should pass automatically

---

### Category 3: Const Variable Handling (2 tests)

**File:** `tests/test_semantic_integration.py`

**Tests Affected:**
1. `test_const_variable` - Assertion mismatch
2. `test_assign_to_constant` - Assertion mismatch

**What Failed:**
- Test assertions don't match actual error/warning counts
- Example: Test expects 1 error, gets 2 errors (or vice versa)

**Why Failing:**
- Semantic analyzer correctly validates const behavior in unit tests
- Integration tests may have stale expectations or generate additional diagnostics

**When to Fix:**
- Review during Task 4.5 (Integration Testing)
- May just need to update test expectations

**Priority:** Low (const validation works correctly, just test mismatch)

**Resolution Path:**
1. Run tests with verbose output to see actual vs expected counts
2. Update test assertions to match actual behavior
3. Verify const validation logic is correct

---

### Category 4: Error Detection and Reporting (6 tests)

**File:** `tests/test_semantic_integration.py`

**Tests Affected:**
1. `test_undefined_variable` - Error count mismatch
2. `test_function_call_wrong_arg_type` - Error detection issue
3. `test_call_undefined_function` - Error count mismatch
4. `test_if_condition_not_bool` - Assertion mismatch
5. `test_multiple_undefined_variables` - Error count mismatch
6. `test_undefined_function_and_type_error` - Error count mismatch

**What Failed:**
- Tests expect specific number of errors but get different counts
- Error messages are generated, but counts don't match expectations

**Why Failing:**
- Semantic analyzer generates errors correctly (unit tests pass)
- Integration tests may:
  - Expect different error counts than actually generated
  - Not account for cascading errors (one error triggers others)
  - Have outdated expectations from earlier implementation

**When to Fix:**
- During Task 4.5 (Integration Testing)
- After full pipeline is complete

**Priority:** Low (errors ARE being caught, just count mismatches)

**Resolution Path:**
1. Run tests with `-v` flag to see detailed error output
2. Compare expected vs actual error counts
3. Update test expectations OR fix duplicate error generation
4. Ensure error messages are clear and non-redundant

---

## 🔧 Technical Debt

**None currently tracked.**

Future items will be added here as they arise.

---

## 📋 Tracking Process

### When to Add Items

Add items to this file when:
1. A test must be skipped due to design conflicts
2. A test fails but doesn't block current development
3. An issue is discovered but can't be immediately fixed
4. Technical debt is identified during implementation

### How to Add Items

Use this template:

```markdown
### Category: [Brief Description]

**File:** `path/to/file.py`

**Tests Affected:**
- test_name_1
- test_name_2

**What Failed:**
[Clear description of the failure]

**Why Failing:**
[Root cause explanation]

**When to Fix:**
[Task number or milestone]

**Priority:** [High/Medium/Low]

**Resolution Path:**
[Step-by-step plan to fix]
```

### Review Schedule

- **After each Phase completion:** Review and fix high-priority items
- **After Phase 4 completion:** Major review of all items
- **Before release:** All items must be resolved or documented

---

##  🎯 Action Plan Summary

### Immediate Actions (Task 2 - Install GCC)
**Priority: CRITICAL**
1. Install MinGW-w64 or TDM-GCC on Windows
2. Add GCC to system PATH
3. Verify: `gcc --version`
4. **Expected Result:** 26 tests will pass immediately

### High Priority Fixes (Task 3 - Start Here)
**Priority: HIGH**

1. **Fix Break/Continue Import** (Category 4)
   - File: [src/codegen/c_generator.py](../src/codegen/c_generator.py:15)
   - Action: Verify `BreakStmt, ContinueStmt` are imported
   - Expected: 1-3 tests pass
   - Effort: 5 minutes

2. **Fix Semantic Scoping Issues** (Category 3)
   - File: [src/semantic/name_resolver.py](../src/semantic/name_resolver.py)
   - Action: Review block-level scope creation
   - Expected: 7 tests pass
   - Effort: 1-2 hours

3. **Fix Parser Lambda Handling** (Category 2)
   - File: [src/parser/parser.py](../src/parser/parser.py)
   - Action: Debug lambda parsing edge cases
   - Expected: 4 tests pass
   - Effort: 1-2 hours

### Medium Priority Fixes
**Priority: MEDIUM**

4. **Fix Test Expectations** (Category 5 & 6)
   - Files: `tests/test_end_to_end.py`, `tests/test_semantic_integration.py`
   - Action: Update test assertions to match actual behavior
   - Expected: 14 tests pass
   - Effort: 30 minutes - 1 hour

### Expected Results After All Fixes
- ✅ **1,043 tests passing** (99.2%)
- ⏭️ **8 tests skipped** (design decision deferred)
- ❌ **0 tests failing**

---

## 🎯 Next Review Milestone

**Target:** After GCC installation and Task 3 fixes

**Expected Resolutions:**
- 26 GCC-related tests pass (after GCC install)
- 12 semantic/parser tests pass (after fixes)
- 1 code generator import test passes (trivial fix)
- Total: 39 tests fixed → 1,043/1,051 passing (99.2%)

**Remaining Items:**
- 8 skipped tests (design decision still needed for `'` comment syntax)

---

## 📝 Notes

- This file is automatically updated when new issues arise
- Resolved items are moved to a "Resolved" section (not deleted)
- See [taskSummary2.md](../taskSummary2.md) for current overall project progress (this file's
  own link to `taskSummary.md` was broken - that file moved to `task/taskSummary.md`, i.e.
  the same folder as this file, and only covers the archived Tasks 1-4)
- See individual task files for specific implementation details

---

**Last Updated:** 2025-12-07 (Updated post-MVP completion with all 39 failing tests categorized)
