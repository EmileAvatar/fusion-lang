[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->

# Fusion - Open Questions

Questions not decided yet. Next to `Decisions.md`: when the user answers one, the answer goes
into `Decisions.md` (and the design document named) and the question is removed here. A new
question gets the next number (never reused). Claude adds a question here instead of guessing
(CLAUDE.md Rule 3b).

**How a question is written (user, 2026-11-07):**
- A heading `#### Q.NNN` with a short title and where it belongs (task, document)
- One or two lines: the question
- **An example code block** wherever code can show it - Claude's understanding of today's
  rule and the options, marked `A:` / `B:` / `C:`, so the user can see it and answer by letter.
  Only a question code can't show (a review, a name) goes without one
- Claude's suggestion, if it has one, marked "suggested"
- Once the user answers: **Answer** (the user's words, short), **Understood as** (a code block
  of the rule as Claude now reads it) and **To confirm** (anything still unclear). After the
  user confirms, it moves to `Decisions.md`

Ideas not scheduled yet keep their own open questions in `files/FutureFeatures.md`
("Open Questions" sections) until they become a task.

---

## Open

#### Q.015-Q.019 Arrays: plain, fixed, growable, 3 dimensions (Task 45 - answered 2026-11-14, understanding to confirm)
The questions: Q.015 `int:[]` and `int[[]]`; Q.016 many dimensions; Q.017 `fixed`; Q.018 large arrays on
the stack; Q.019 changing an array's size. The user answered all five (2026-11-14); this is Claude's
understanding of the answers. Once confirmed it goes into Decisions.md and this section is removed.

**Understood as - the forms (Q.015, Q.017, Q.019):**
```fusion
int[] a = [5, 2, 3]       // plain - size from the values
a = [1, 2]                // fine - replaced by another size; the only way a plain array changes size
a.add(4)                  // an error - plain arrays don't grow: declare it int:[]
int[] e                   // plain, size 0
fixed int[10] c           // fixed - 10 slots, never another size; says it out loud for the reader
c = [1, 2]                // an error - c is fixed
fixed int[] d             // an error - fixed needs its size written
int:[] g                  // growable - short form
int[[]] h                 // growable - the same, easy to spot
g.add(4)                  // fine; g.removeLast() / g.pop()
fixed int:[10] x          // an error - fixed and growable can't go together (fixed int[[10]] too)
fixed(10) List<int> l     // Lists, Maps, strings: at most 10 - the 10 slots reserved at once, so
                          // adding never costs a grow (D.020, D.064, Task 47.5)
```

**Understood as - 3 dimensions (Q.016):**
```fusion
int[10][5][7] cube        // 10 rows x 5 columns x 7 depth - preferred form
int[10],[5],[7] cube      // the same - the commas only break it up visually
cube[2][3][1] = 9         // row 2, column 3, depth 1
cube.expand(rows, 2)      // 2 more rows        - stays rectangular; a warning: every slot is copied
cube.expand(columns, 2)   // 2 more columns in every row
cube.expand(depth, 2)     // 2 more depth everywhere ("depth" the name; sheets / pages not used)
cube.expand(1, 2)         // by number: 1 rows, 2 columns, 3 depth - for more dimensions later
                          // (more than 3: the Collections library)
cube.setStorage(RECT)     // this array only: FLAT (default), RECT or JAGG
cube.setStorage(null)     // back to FLAT
```
- `rows`, `columns`, `depth` are values of a built-in enum (`Dimension`), so `expand(rows, 2)` is checked
- Storage: **FLAT** - one block, every slot side by side (fast for matrices - the default);
  **RECT** - each row its own block, all rows the same length; **JAGG** - each row its own block and its
  own length, so one row can `add`
- `[arrays] storage = "flat"` (`"flat"` / `"rect"` / `"jagg"`) - the project's default
- Later: large arrays on a GPU or the CPU - special options (L16)

**Understood as - large arrays (Q.018):**
```toml
[arrays]
stackWarn  = "16KB"    # a plain / fixed array above this on the stack: a warning
stackLimit = "64KB"    # above this: a compile error - "too large for the stack: use int:[] (the heap)"
```
- In bytes, so `int` and `long` arrays are measured fairly
- While running, the program may lower or raise how much it puts on the stack for where it runs - a small
  PC less, a server more - and plays nice: it never takes memory other programs need. That is with the
  buffers in L16 (after self-hosting, profiled first)

**To confirm:**
1. `fixed int[] d = [5, 2, 3]` - the size is in the values: still an error (fixed always writes the
   number), or fine? Suggested: an error, as said - `fixed int[3] d = [5, 2, 3]`
2. Above `stackLimit` an error (as now answered), not moved to the heap by itself? Suggested: yes, an error
3. `setStorage(null)` goes back to FLAT - or to the project's `[arrays] storage`? Suggested: the project's
   setting (FLAT unless the project chose another)
4. On FLAT or RECT, a single row's `add` is an error - "use setStorage(JAGG)"? Suggested: yes
5. Dimension numbers count from **1** (`expand(1, 2)` = rows), while indexes count from 0? Suggested: from
   0 like everything else (`expand(0, 2)` = rows) - one rule. Or 1 as written
6. `int[10][5][7]` is rows x columns x depth; `int[10]` alone is 10 slots in one row

Earlier: Q.013 (modules and namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES
Task 57. Q.014 (a may-be-null parameter mark) answered 2026-11-14: no mark - every object may be
null (D.138, D.117). Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Next question: Q.020.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
