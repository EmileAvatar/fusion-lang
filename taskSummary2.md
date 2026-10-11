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

## PLAN (awaiting approval): reorganize and renumber FEATURES.md

**User direction (2026-10-11):** Enums first. HIDL moves after self-hosting. Self-hosting
comes in phases: phase 1 is a *test run* - a compiler written in Fusion, covering only the
simple part of the language, whose exe can compile the programs in `examples/` by itself.
The Python compiler stays the real compiler until the self-hosted one is fully
independent. Then features keep being added, and the complex parts come last.

#### Numbering scheme (recommended)
- **Done tasks keep their numbers** (01-09, 12, 18, 23): commits, the archive, code comments
  and example tags (`task: 18.3.2`) refer to them
- **Open tasks get new numbers in the order they will be done, starting at 25**, so an old
  number never means something new (old notes saying "Task 21" stay unambiguous)
- Old open tasks are retired; a table at the end of FEATURES.md maps old -> new. Their done
  sub-items (10.1, 10.2, 11.1, 15.3, 15.7-15.11, 16.7, 19.6, 22.1-22.6) move to the archive
- Task 15 (deferred decisions) is dissolved: each item moves into the task it belongs to.
  15.4 (order of Task 10 vs 11) is decided by this plan: self-hosting first, LLVM later
- Every reference is updated by a script with the old -> new map (FEATURES.md, backlog,
  spec, SYNTAX_REFERENCE.md, CLAUDE.md files, code comments) and checked by hand - about
  300 places; the archive is history and stays as written

#### New layout of FEATURES.md
```text
## Done                         01-04 .. 09, 12, 18, 23 (one line each)
## Phase 1 - up to the self-hosting test run
  25 Enums and tagged unions (NEW)
       enum Color { Red, Green }; enums with data (tagged unions), e.g.
       Token = Number(int) | Word(string); `match` with a check that every case is
       handled; printing, ==, use in List / Map. A compiler needs it for its node kinds
  26 Error handling (was 21): Go-style error returns + try/catch, switchable in config;
       file errors become catchable instead of stopping the program
  27 Housekeeping (was 22.7, 16.1, 15.12): spec status markers, control-flow example,
       left-to-right operand order; tools: check.py --ship, --fix-ascii, --example
  28 Self-hosting phase 1 - the test run (was 10.3-10.8)
       28.1 The subset: exactly what the programs in examples/ need
       28.2-28.6 Lexer, parser, checker, C code generator, driver - written in Fusion
       28.7 Verify: the Fusion-built compiler.exe compiles every example; the output
            programs print the same as the Python-built ones
       28.8 Report: what was missing or awkward -> feeds Phase 2
       The Python compiler stays the real compiler
## Phase 2 - growing the language, then a fully independent compiler
  29 Strings: mutable / fixed / templated / pooled (was 17)
  30 Nullable values and safe navigation ?. ?[ (was 14)
  31 Config file in any format + enforcing [safety] / [backend] (was 20, 15.6)
  32 Example coverage: classes, generics, threading, errors, memory (rest of 16)
  33 Self-hosting phase 2 - fully independent (was 10.9-10.12): the compiler compiles
       itself (bootstrap twice), runs the whole test suite, Python compiler retired
## Phase 3 - the advanced parts
  34 Editor support: TextMate grammar, VS Code, Sublime, then an LSP (was 24)
  35 Memory model: Unique / Shared / Weak, GC as an option (was 15.5)
  36 Library trust, isolation and security (was 19)
  37 LLVM backend (was 11, 15.1)
  38 HIDL - hardware interface definition language (was 13)
## Later / advanced            unchanged (classes, generics, threading, ...)
## Known limitations           unchanged
## Old task numbers            10->28/33, 11->37, 13->38, 14->30, 15->dissolved, 16->32,
                               17->29, 19->36, 20->31, 21->26, 22->27, 24->34
```

#### Open questions for the user
1. Numbering: keep done numbers and start the open ones at 25 (recommended), or renumber
   everything from 01 (cleaner list, but every old reference in commits, the archive and
   code comments would point at the wrong task)?
2. Classes / methods on structs and generics are in "Later" with no task. Phase 2 is the
   natural place (the self-hosted compiler will want them). Add them as tasks now, or leave
   them in Later until the phase 1 report?

#### Steps once approved
1. Script: build the new FEATURES.md from the current one + the map; archive the retired
   done sub-items verbatim
2. Script: update references elsewhere with the map; review each change
3. task/taskBacklog.md: renumber the write-ups (10 split into 28 / 33), add Task 25's
4. `python check.py`, commit, push
5. Then plan Task 25 (enums) in detail here, for approval

---

## Working Notes

### Session 31 (2026-10-09 .. 10-11 - 18.3.5 to 18.5.7)
- Done: 18.3.5 equality, 18.3.5b bool printing, 18.3.6 string library (a-f, masking design
  and build), 18.3.7 type classes / methods, 18.3.8 bytes, 18.4 modules (1-4), 23.7 / 23.8
  (wait at exit, --headless, .fusion preview), Task 24 added (editor support), 18.5 (1-7)
- User preferences saved to memory: as little typing as possible; never change values
  silently
- Task 18 archived (FEATURES.md detail too); 3 automation candidates added
- **Next Action:** user to approve the FEATURES.md reorganization plan above (2 questions),
  then plan Task 25 (enums)
