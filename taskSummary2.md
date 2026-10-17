# Fusion - Working File (active task plans)

**What this file is (Task 22, 2026-10-09):** only the task being worked on now - its detailed
plan, the next action, and the latest session note. Keep it small: it is read often.
- Status of every task and feature: `FEATURES.md` (`[ ]` open, `[DONE]`, `[POSTPONED to ...]`)
- Finished tasks and sub-tasks, old sessions: `task/taskSummaryArchive.md` (verbatim)
- Not-started task write-ups: `task/taskBacklog.md` (verbatim)
- Rules (plan first, no emojis in code, ...): `CLAUDE.md`

---

## Current status (2026-10-11)

**Task 18 (core language foundation) is COMPLETE** and archived (plans, notes and the
FEATURES.md detail are in `task/taskSummaryArchive.md`). Task 10.2 is met.

---

## Current plan: the roadmap (FEATURES.md, renumbered 2026-10-11)

Done tasks keep their numbers; open tasks were renumbered from 25 into three phases (the
approved plan is archived). Phase 1 = 25 enums, 26 error handling, 27 semantic contract and
safety (bounds checks, the three-block-style check), 28 self-hosting test run.

---

## TASK 27: Semantic contract and safety - ACTIVE (plan approved 2026-10-17)

**Why before self-hosting:** the self-hosting test run is only meaningful if what each
construct does is pinned down and nothing fails silently. Sources: the ChatGPT review
(2026-10-11), Notes/04/notes.md step 2, and the user's decisions on arrays, overflow and
recursion.

#### Sub-tasks, in the order they would be done
- 27.1 DONE (array bounds checks, array literal indexing) - detail archived
- 27.5 DONE (equality heading), 27.4 DONE (three block styles, same C) - detail archived
- 27.2b DONE (OverflowError, unsafe mode), 27.2d DONE (wrapAdd, unchecked) - detail archived
- 27.2c DONE (endless recursion) - detail archived
- **27.3 Interaction tests** - features together: a struct holding lists and enums with
  data, copied, passed through functions and across modules; nested collections; errors
  passing through all of it; early returns, break, continue - every program leak-checked
- **27.2 The contract** - written last, in one spec section, documenting what was built
  and tested: copying (deep), the equality table, `=` in conditions (with its ambiguous
  cases tested), Unicode indexing (code points), integer conversions and overflow, changing
  a collection while looping over it, cleanup on every path, error propagation, evaluation
  order (call arguments left to right; operands - the open 37.2 noted)

#### Decisions (user, 2026-10-17) - plan approved
1. Array bounds checks are **always** on - unsafe mode doesn't remove them
2. Wrapping on purpose: functions `wrapAdd(a, b)`, `wrapSub`, `wrapMul` (methods too)
3. Endless recursion: **both** - stack use is the default (a limit from the real stack
   size); `[safety] max_call_depth` = "max" (default: stack use only) or a number (a call
   counter) for memory-constrained devices, tuned by profiling - most projects won't use it
4. Turning checks off: the whole project (`[safety] mode = "unsafe"`) **and** per block now -
   an `unchecked` block turns overflow checks off inside it (bounds checks stay)

---

## TASK 26: Error handling - COMPLETE (2026-10-16)

Error values, functions that can fail, capturing, bubbling, try / catch / finally / throw,
every built-in failure catchable, `[errors]` switches, examples/errors_demo. Part 2 (26.7-26.13):
implicit errors, untyped capture, custom error types, err.kind, match on error types, typed
catch, Fusion's own error types. Plan and notes:
`task/taskSummaryArchive.md`.

---

## TASK 25: Enums and tagged unions - COMPLETE (2026-10-12)

Plain enums, `match`, enums with data, enums holding themselves, and the expressions
example. Plan and notes: `task/taskSummaryArchive.md`.

---

## TASK 22 (housekeeping) - ACTIVE (user: "do the housekeeping first and the ascii issue first")

Kept under Task 22 until the renumbering is approved.

- 22.8-22.11 DONE (tools; detail archived)
- 16.1 DONE - examples/control_flow
- 22.7a DONE - README reduced to goals + pointers
- 22.7b DONE - spec status lines (Task 22 complete)
- Each one: FEATURES.md line, `task/automation.md` row marked Automated, check, commit

---

## Working Notes

### Session 31 (2026-10-09 .. 10-11 - 18.3.5 to 18.5.7)
- Done: 18.3.5 equality, 18.3.5b bool printing, 18.3.6 string library (a-f, masking design
  and build), 18.3.7 type classes / methods, 18.3.8 bytes, 18.4 modules (1-4), 23.7 / 23.8
  (wait at exit, --headless, .fusion preview), Task 24 added (editor support), 18.5 (1-7)
- User preferences saved to memory: as little typing as possible; never change values
  silently
- Task 18 archived (FEATURES.md detail too); 3 automation candidates added
- 22.8-22.11 done: check.py --fix-ascii / --ship / --example, tools/patch.py
- 16.1 done: examples/control_flow; map literals noticed missing (FEATURES.md Later)
- 22.7a done: README is goals + pointers (554 -> 321 lines); 22.7b waits for the renumbering
- User answered: numbers from 25, classes / generics in Phase 2. ChatGPT review read:
  fixed arrays are not bounds-checked (segfault) -> new Task 27 "semantic contract and safety"
- FEATURES.md reorganized into phases and renumbered (22.12); the user asked for 27.1
  (bounds checks for fixed arrays) and 27.4 (one app in 3 block styles -> identical C)
- 2026-10-12: 22.7b done - a status line under each of the spec's 31 major sections; Task 22
  complete
- Task 25 plan approved (all 4 recommended answers)
- 25.2 plain enums and 25.3 `match` done
- 25.4 enums with data done
- 25.5 enums holding themselves done
- Task 25 complete (25.6: examples/expressions)
- Task 26 plan approved (bubble up, capture any call, all built-ins catchable, one catch)
- 26.2 done
- 26.3 done
- 26.4 done
- 26.5 done
- Task 26 complete (26.6: examples/errors_demo)
- Task 26 part 2 planned, 4 questions answered
- Plan updated (default message, match on error types, typed catch now, built-in
  error type list)
- 26.7 done
- 26.8 done
- 26.9 done
- 26.10 done
- 26.11 done
- 26.12 done
- Task 26 part 2 complete (26.7-26.13)
- Task 27 plan approved (bounds always; wrapAdd functions; stack use + max_call_depth; unchecked blocks)
- 27.1 done
- 27.5 and 27.4 done
- 27.2b and 27.2d done
- 27.2c done
- **Next Action:** 27.3 interaction tests
