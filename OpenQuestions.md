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

#### Q.030 Writing a jagged array (Task 45.15, files/Arrays.md)
A jagged array has rows of different lengths. Its values are given at the declaration, but
`setStorage(JAGG)` comes on the next line (D.147). How does the compiler accept the uneven rows?
```fusion
int[][] j = [[1], [2, 3, 4], [5, 6]]     // today: an error - rows of different lengths

// A (suggested): the next line / the set-up block makes it JAGG - the compiler reads it first
int[][] j = [[1], [2, 3, 4], [5, 6]]
j.setStorage(JAGG)

// B: only through the setting - [arrays] storage = "jagg" for the whole project

// C: a type of its own - int[[]][] j  (a growable row inside)
```
Suggested: A, and B as well (the project default). An uneven literal with no JAGG stays an error,
never made JAGG silently.

#### Q.031 rows / columns / foreach on a jagged array (Task 45.15)
A jagged array has no single column count, and `[arrays] order = "columns"` walks the columns first.
```fusion
int[][] j = [[1], [2, 3, 4], [5, 6]]
j.setStorage(JAGG)
print(j.rows)        // 3
print(j[1].length)   // 3 - that row's own length
print(j.columns)     // A: -1 (no single count, as one slot's length)  B: 3 (the longest)  C: an error
foreach (int[] row in j)   // D: a jagged array always walks its rows first, whatever the order setting
    ...                    // E: the order setting holds - a column skips rows too short for it
int[] c = j[][1]           // column 1 - F: an IndexError (row 0 has no slot 1)  G: the rows that have it
```
Suggested: A, D, F.

#### Q.032 Which arrays may be jagged, and where a row's `add` works (Task 45.15)
```fusion
int[][] a = [[1], [2, 3]]       // a plain array
a.setStorage(JAGG)
int:[][] g = [[1], [2, 3]]      // a growable one
g.setStorage(JAGG)
g[0].add(7)                     // one row grows - D.144

// A (suggested): any array of 2 dimensions may be JAGG (it goes on the heap); add only on a growable one
// B: JAGG only on a growable array - setStorage(JAGG) on a plain one an error
// C: any array; add on any JAGG array
```

#### Q.033 3 dimensions and the stack (Task 45.15)
```fusion
int[2][3][4] cube
cube.setStorage(JAGG)    // A (suggested): JAGG on 2 dimensions only for now - 3 an error "comes later"
                         // B: every level its own lengths - each sheet's rows differ too
int[2][3] m              // on the stack (FLAT)
m.setStorage(RECT)       // C (suggested): RECT / JAGG move it to the heap (as 45.10 does)
                         // D: an error - only an array on the heap may change its storage
```

Earlier: Q.028 (toCSV on arrays) and Q.029 (toList and null slots) answered 2026-11-16: Decisions.md D.151, D.152, FEATURES 45.11b / 45.11c, Notes/CSV_many_dimensions.md.
Earlier: Q.021-Q.027 (arrays of 3 dimensions, bare enum values) answered 2026-11-15:
Decisions.md D.141, D.143, D.148-D.150, FEATURES 45.12, 45.3b, 45.16, 45.17. Q.013 (modules and
namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES Task 57. Q.014 (a may-be-null
parameter mark) answered 2026-11-14: no mark - every object may be null (D.138, D.117). Q.001-Q.012
answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status PARTIAL; FEATURES
48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the name). Q.015-Q.020
(arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.034.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
