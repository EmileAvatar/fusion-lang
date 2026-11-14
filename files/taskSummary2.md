# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## TASK 59: Faster checks - PLAN (2026-11-14), waiting for approval

Settings: none

59.2 What takes long - measured 2026-11-14 (`pytest --durations=0`):
- The suite: 2,714 tests, 238 s; 522 of them take 0.3-0.5 s each = 208 s (87%) - the end-to-end tests:
  Fusion -> C -> GCC -> run the program under the leak check; everything else together ~25 s
- Slowest files: test_error_handling 21 s, test_selfhost 20 s (builds the self-hosted compiler once),
  test_strings 16 s, test_string_library 14 s, test_runtime_header 12 s, test_end_to_end 8 s
- No single slow test to fix: the cost is GCC once per test; this PC has 12 cores, the suite uses one

59.3 Run the tests in parallel (the big win):
- pytest-xdist (in files/requirements.txt); check.py runs `pytest -n auto --dist loadfile` - every test
  file on one worker, so a file's shared setup (the self-hosted compiler built once) stays as it is
- Each end-to-end test already builds in its own temporary folder - safe in parallel
- Without xdist installed, check.py runs the tests one after another as today (a note says so)
- Expected: ~4 min -> under 1 min; the same 2,714 passed / 8 skipped, checked before and after

59.4 Only the tests a change needs - after 59.3, only if the suite is still slow:
- If the parallel suite is under ~60 s: keep running all of it for code changes (simplest, safest);
  documents only already skip it (59.1)
- Else: a map from source folders to test files (src/lexer -> lexer tests, ...), `--changed`; the
  full suite still runs once a task is complete

59.5 Faster end-to-end tests - postponed unless still needed: several programs per GCC call,
  caching unchanged builds

Then Task 59 complete: its lines to the archive, the Later list checked, a full check; next Task 48.

- **Next Action:** 59 - the plan above, waiting for approval; then Task 48
