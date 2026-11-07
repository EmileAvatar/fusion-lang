# Proposal: Documentation and Decision System

- **Status:** Proposed (needs owner approval before it is applied)
- **Audience:** Claude Code (and any other AI agent working on the language)
- **Working name of the language:** Fusion (placeholder, owner to confirm)

## 1. Purpose

We are building a new programming language. We need one source of truth for every design decision, so that:

1. The agent never forgets or contradicts an earlier decision.
2. Rejected ideas do not keep coming back.
3. An experimental idea is never treated as an approved language feature.
4. Every change to the design has a traceable reason.

The documentation must live in the repository as plain Markdown files, so it can be diffed, versioned and read by the agent.

## 2. Principles

1. **Markdown is the source of truth.** No database, no hosted wiki.
2. **Small, specific files.** One topic per file. No monolithic spec.
3. **Link, never copy.** A fact is written in one place only. Everywhere else links to it by ID.
4. **IDs are permanent.** Files, sections and decisions are never renumbered.
5. **Accepted decisions are immutable.** They are replaced by a new decision, never edited.
6. **The owner decides.** The agent proposes, only the owner accepts.

## 3. File structure

Names below are illustrative. The owner will supply the real list.

```text
CLAUDE.md                    agent rules (short, always read)
Main.md                      purpose of the language + map of all files
Decisions.md                 decision register
OpenQuestions.md             unresolved design questions
001-LanguageDesign.md        feature areas, with sub-sections
002-TypeSystem.md
003-MemoryManagement.md
...
```

Rules:

- `Main.md` is the entry point. It explains the purpose and has a table: ID, file, one-line description.
- Each numbered file covers one area and states its own ID at the top.
- Sub-sections use `NNN.NNN` IDs (for example `001.002`) as headings inside the file. Only move a sub-section into its own file when the file passes the size limit. The ID stays the same.
- A topic has exactly one home file. If another file needs it, it links to the home file (for example, concurrency is specified in one file only; other files link to it).

## 4. ID scheme

| Item | Format | Example |
|------|--------|---------|
| Spec file | `NNN` | `003` |
| Sub-section | `NNN.NNN` | `003.002` |
| Decision | `D-<section>-<seq>` | `D-003.002-01` |

- IDs are never reused or renumbered. If something is removed, mark it `Removed` and leave the gap.
- Leave gaps between file numbers if inserts are likely (for example 010, 020).
- Every spec file links to the decisions that govern it. Every decision lists the sections it affects.

## 5. Decision register (`Decisions.md`)

Start with a single register file. Each entry is short (5 to 10 lines).

```markdown
## D-003.002-01 Ownership ends at scope exit

- **Status:** Accepted
- **Affects:** 003.002, 004, 007
- **Decision:** Resources are released when the owning variable leaves scope.
- **Why:** Predictable cleanup without manual free.
- **Rejected alternatives:** garbage collection, reference counting
- **Supersedes:** none
- **Superseded by:** none
```

### Decision statuses

| Status | Meaning |
|--------|---------|
| Proposed | Under discussion, not official |
| Accepted | Official design decision |
| Rejected | Explicitly declined |
| Deprecated | Was accepted, no longer recommended |
| Superseded | Replaced by a newer decision |

Implementation progress (not started, in progress, done) is **not** a decision status. It changes independently, so track it in the planning or task files.

### Register size

- Put an index table at the top (ID, title, status, affected sections).
- When the register passes about 50 entries, move Rejected and Superseded entries to `DecisionsArchive.md` and keep the index complete.

## 6. Rules for the agent (to be added to `CLAUDE.md`)

1. Start at `Main.md`. Read only the files relevant to the task, plus `Decisions.md`.
2. Before changing language behaviour, check `Decisions.md` for related decisions and cite their IDs.
3. The agent may add decisions with status **Proposed**. Only the owner may change a status to **Accepted** or **Rejected**.
4. Never edit an Accepted decision. To change it, add a new decision that supersedes it, and update the `Superseded by` field of the old one.
5. Never reintroduce a Rejected idea without new justification, and say so explicitly.
6. If a spec file or code conflicts with an Accepted decision, flag the conflict to the owner. Do not silently change either one.
7. Do not invent facts. If something is not covered by the spec or a decision, add it to `OpenQuestions.md` and ask.
8. Every spec change must reference the decision ID that justifies it.
9. Keep each file within the size limits below.

## 7. Size limits

| Item | Target | Split or archive at |
|------|--------|---------------------|
| Spec file | 100 to 200 lines | 400 lines |
| `Main.md` | under 100 lines | 200 lines |
| `CLAUDE.md` | under 150 lines | 300 lines |
| One decision entry | 5 to 10 lines | 20 lines |
| Register | up to 40 entries | 60 entries |

A task should normally need only 3 to 5 files. If it needs more, the documentation is probably split badly.

## 8. Optional later additions (not part of the first step)

- **YAML front matter** at the top of each file (id, status, affects) so a script can validate it.
- **Validator script** that reports broken links, missing IDs, and two Accepted decisions on the same topic.
- **HTML viewer** that renders the Markdown (sidebar, tables, Mermaid diagrams). It reads the `.md` files and never replaces them. It must not be maintained by the agent as free-form HTML.
- **Mermaid diagrams** inside spec files where a diagram explains better than text.

## 9. First tasks for Claude Code

1. Create the folder structure and empty stubs for the files the owner lists.
2. Create `Main.md` with the purpose and the file map.
3. Create `Decisions.md` with the index table and the entry template from section 5.
4. Create `OpenQuestions.md`.
5. Add the rules from section 6 to `CLAUDE.md`.
6. Stop and show the owner the result. Do not write any spec content or decisions beyond the templates.

## 10. Acceptance criteria

- [ ] Every file has an ID and is linked from `Main.md`.
- [ ] Every topic has exactly one home file.
- [ ] `Decisions.md` has the index table and a working entry template.
- [ ] `CLAUDE.md` contains the rules from section 6 word for word.
- [ ] No file exceeds its split limit.
- [ ] No decision is marked Accepted by the agent.

## 11. Open questions for the owner

- Final name of the language.
- Final list of spec files and their numbers.
- Whether decisions stay in one register or become one file each once it grows.
- Whether to add front matter and a validator now or later.
