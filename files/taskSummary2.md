# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## TASK 51.6: A link check in check.py - PLAN (2026-11-13), waiting for approval

Settings: none

- A new check in `check.py` (`links`), also run by `--docs`:
  - Every relative link `[text](path)` in the Markdown files points to a file that exists
  - A link with `#anchor` - the heading exists in that file (the GitHub slug)
  - Skipped: web links (`http...`), `Notes/` (git-ignored), `task/` (archives - old paths kept as they were)
  - Links inside code blocks are skipped
- First run: list every broken link; fix them (most will be old paths from before the splits)
- A test for the checker: a good link, a missing file, a missing anchor
- Then Task 51 is complete: its `[DONE]` lines to `task/featuresArchive.md`, a full check
  (`--ship ... --full`)

- **Next Action:** 51.6 - the link check plan above, waiting for approval
