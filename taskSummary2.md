# Fusion - Working File (active task plans)

**What this file is (Task 22, 2026-10-09):** only the task being worked on now - its detailed
plan, the next action, and the latest session note. Keep it small: it is read often.
- Status of every task and feature: `FEATURES.md` (`[ ]` open, `[DONE]`, `[POSTPONED to ...]`)
- Finished tasks and sub-tasks, old sessions: `task/taskSummaryArchive.md` (verbatim)
- Not-started task write-ups: `task/taskBacklog.md` (verbatim)
- Rules (plan first, no emojis in code, ...): `CLAUDE.md`

---

## Current status (2026-10-11)

**Task 18 (core language foundation) is COMPLETE** - functions, structs, strings, bytes,
equality, the string library and type classes, `import` / modules, lists, maps, files,
console input, program arguments and standard-library layers. Its plans and notes are in
`task/taskSummaryArchive.md`. Task 10.2 (the self-hosting prerequisites) is met.

**Before self-hosting (Task 10), still open** (see FEATURES.md):
- Task 21 - error handling (Go-style error returns + try/catch), scheduled right after 18.3
  by the user
- Enums / tagged unions - needed to represent a compiler's many node kinds; not scheduled
  yet (recommended to add as a task before Task 10)
- Task 15.4 - the user's decision on the order of Task 10 (self-hosting) and Task 11 (LLVM)

---

## Working Notes

### Session 31 (2026-10-09 .. 10-11 - 18.3.5 to 18.5.7)
- Done: 18.3.5 equality, 18.3.5b bool printing, 18.3.6 string library (a-f, masking design
  and build), 18.3.7 type classes / methods, 18.3.8 bytes, 18.4 modules (1-4), 23.7 / 23.8
  (wait at exit, --headless, .fusion preview), Task 24 added (editor support), 18.5 (1-7)
- User preferences saved to memory: as little typing as possible; never change values
  silently
- **Next Action:** user to choose the next task - recommended: plan **Task 21 (error
  handling)**, then add an enums / tagged unions task before self-hosting.
