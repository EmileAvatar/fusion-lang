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

Task 45.12 - arrays of up to 3 dimensions (D.143). Six questions before it is built (2026-11-15).

#### Q.021 Reading one slot - which brackets (Task 45.12, files/Arrays.md)
How is one slot of `int[3][4] m` read and written?
```fusion
int[3][4] m                    // 3 rows x 4 columns
A:  m[1][2] = 5                // as C, Java, JavaScript
B:  m[1, 2] = 5                // as C#, numpy - one pair of brackets
C:  both - the same slot; m[1][2] the familiar one, m[1, 2] quick typing
```
Suggested: C - the declaration already takes both `int[3][4]` and `int[3],[4]` (D.143).

#### Q.022 Fewer indices than dimensions - `m[1]` (Task 45.12)
What is `m[1]` on `int[3][4] m` - one index where two are needed?
```fusion
A:  m[1]                       // an error for now - give every index: m[1][2]
B:  int[] row = m[1]           // a copy of row 1 (4 items), as copyPart copies
C:  foreach (int x in m[1])    // a borrowed view of row 1 - no copy; m can't change while it is held
```
Suggested: A now (one rule, nothing hidden), B or C later when it is needed.

#### Q.023 foreach over a matrix (Task 45.12)
```fusion
int[2][3] m = [[1, 2, 3], [4, 5, 6]]
A:  foreach (int x in m)       // every slot, row by row: 1 2 3 4 5 6
B:  foreach (int[] row in m)   // each row (needs Q.022 B or C)
```
Suggested: A - the same for 2 and 3 dimensions, and nothing is copied.

#### Q.024 Its sizes - `length`, rows, columns, depth (Task 45.12)
```fusion
int[10][5][7] cube
A:  cube.length                // 350 - every slot (as C#)
    cube.rows, cube.columns, cube.depth      // 10, 5, 7
B:  cube.length                // 10 - the rows (as Java, C: an array of arrays)
    cube.rows, cube.columns, cube.depth      // 10, 5, 7
```
Suggested: A - `length` is always the number of slots, as `foreach` (Q.023 A) goes over them;
on a one-dimension array `rows` is 1 and `columns` its length (D.143: `int[10]` is one row of 10).

#### Q.025 Which arrays `expand` works on, and what it does (Task 45.12, D.143)
```fusion
int[2][3] m = [[1, 2, 3], [4, 5, 6]]
m.expand(rows, 1)              // a warning: every slot is copied -> 3 x 3, the new row 0 0 0
m.expand(columns, 2)           // -> 3 x 5: 2 new columns at the right of every row
fixed int[2][3] f
f.expand(rows, 1)              // an error: fixed never changes size (D.141)
A:  any plain array of 2 or 3 dimensions; it then lives on the heap (as a replaced one, 45.10)
B:  only one marked growable - int:[2][3] m (D.141's growable form)
```
- New slots get the default value (0, "", false, null for an object); `n` is 1 or more
- Added at the end of that dimension: rows at the bottom, columns at the right, depth at the back
- Suggested: A - D.143 gives `expand` to every many-dimension array, with the warning as the guard

#### Q.026 The names rows / columns / depth (Task 45.12, D.143 "a built-in enum")
```fusion
A:  m.expand(rows, 1)          // the bare word, known only inside expand(...) - a variable named rows still works
B:  m.expand(Dimension.rows, 1)   // a built-in enum Dimension; the bare word too, inside expand(...)
C:  m.expand(Dimension.rows, 1)   // the enum only
    m.expand(0, 1)             // all three: the number, counted from 0 (D.143)
```
Suggested: B - an enum a function can take and pass on (`Dimension d = rows`), and the short form
where it can only mean that.

Earlier: Q.013 (modules and namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES
Task 57. Q.014 (a may-be-null parameter mark) answered 2026-11-14: no mark - every object may be
null (D.138, D.117). Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Q.015-Q.020 (arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.027.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
