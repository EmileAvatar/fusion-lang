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

**Answer (user, 2026-11-16):** a JAGG array has to be set either on the next line or in the set-up block.

**Understood as:**
```fusion
int:[][] j = [[1], [2, 3, 4], [5, 6]]
j.setStorage(JAGG)                       // the next line - uneven rows accepted

int:[][] k = [[1], [2, 3]]
    setStorage(JAGG)                     // or in its set-up block

int:[][] x = [[1], [2, 3]]               // no JAGG next to it: an error "rows of different lengths -
                                         // setStorage(JAGG) on the next line"
```

**To confirm:**
- `[arrays] storage = "jagg"` (D.144) - is it dropped for JAGG, so every jagged array says so where it
  is made? Suggested: yes - the setting keeps "flat" / "rect" only

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

**Answer (user, 2026-11-16):** check how other languages handle JAGG arrays; to me depth -> columns -> rows.

**What other languages do (Claude, 2026-11-16):**
- C#, Java, JavaScript, Go, Python, Rust: a jagged array is an array of arrays - the outer one holds the rows
- `j.length` is the number of rows; `j[1].length` that row's own length; none has a column count
- A loop gives the rows, one by one; a column is the programmer's own loop - a row too short for it
  is an IndexError (C#, Java, Go, Python, Rust) or `undefined` (JavaScript)
- C# also has a rectangular `int[,]` - `GetLength(0)`, `GetLength(1)`; only that one has columns
- NumPy refuses uneven rows (an error since 1.24); MATLAB keeps them in a cell array, walked column by column
- So no language walks a jagged array column by column - Fusion's order (D.148) would be its own

**Understood as:**
```fusion
int:[][] j = [[1], [2, 3, 4], [5, 6]]
j.setStorage(JAGG)
print(j.rows)            // 3
print(j[1].length)       // 3 - that row's own length
print(j.columns)         // 3 - the longest row (to confirm)
foreach (int[] c in j)   // the same order as every array: columns first (D.148)
    ...                  // column 0: 1 2 5; column 1: 3 6; column 2: 4 - a row too short is skipped
int[] c = j[][1]         // column 1: [3, 6] - the rows that have it
```

**To confirm:**
- `j.columns` - the longest row (3), or -1 (no single count)? Suggested: the longest
- A column skips rows too short for it (above) - or an IndexError? Suggested: skipped, so foreach and
  `j[][1]` agree
- `[arrays] order = "rows"` walks a jagged array row by row, as the other languages do

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

**Answer (user, 2026-11-16):** any 2D and above array can be JAGG, and only on a growable array.

**Understood as:**
```fusion
int:[][] g = [[1], [2, 3]]
g.setStorage(JAGG)          // fine - growable, 2 dimensions
g[0].add(7)                 // one row grows
int:[][][] c = ...
c.setStorage(JAGG)          // fine - 3 dimensions too (Q.033)
int[][] a = [[1], [2, 3]]
a.setStorage(JAGG)          // an error - "JAGG is for a growable array: int:[][] a"
```

**To confirm:** nothing - B, on 2 and 3 dimensions.

#### Q.033 3 dimensions and the stack (Task 45.15)
```fusion
int[2][3][4] cube
cube.setStorage(JAGG)    // A (suggested): JAGG on 2 dimensions only for now - 3 an error "comes later"
                         // B: every level its own lengths - each sheet's rows differ too
int[2][3] m              // on the stack (FLAT)
m.setStorage(RECT)       // C (suggested): RECT / JAGG move it to the heap (as 45.10 does)
                         // D: an error - only an array on the heap may change its storage
```

**Answer (user, 2026-11-16):** JAGG on 3 dimensions too - get it done. A JAGG array is only on the heap
for now. The stack only holds a 1D or 2D array, FLAT - the stack is just storage for an active copy
used in loops. The stack / heap split may change later, when we profile after self-hosting.

**Understood as:**
```fusion
int:[][][] c = [[[1], [2, 3]], [[4, 5, 6]]]
c.setStorage(JAGG)          // every level its own lengths (B) - on the heap (growable, Q.032)
int[2][3] m                 // 2 dimensions: on the stack, FLAT
int[2][3][4] cube           // 3 dimensions: on the heap from now on (today on the stack - to change)
m.setStorage(RECT)          // RECT: to confirm
```

**To confirm:**
- `int[2][3][4] cube` (plain or fixed, 3 dimensions) moves to the heap - today it is on the stack. Suggested: yes
- RECT - only on the heap too, so `m.setStorage(RECT)` moves a 2D stack array to the heap (C)? Suggested: C
- Noted for after self-hosting: profile the stack / heap split (L16)

Earlier: Q.028 (toCSV on arrays) and Q.029 (toList and null slots) answered 2026-11-16: Decisions.md D.151, D.152, FEATURES 45.11b / 45.11c, Notes/CSV_many_dimensions.md.
Earlier: Q.021-Q.027 (arrays of 3 dimensions, bare enum values) answered 2026-11-15:
Decisions.md D.141, D.143, D.148-D.150, FEATURES 45.12, 45.3b, 45.16, 45.17. Q.013 (modules and
namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES Task 57. Q.014 (a may-be-null
parameter mark) answered 2026-11-14: no mark - every object may be null (D.138, D.117). Q.001-Q.012
answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status PARTIAL; FEATURES
48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the name). Q.015-Q.020
(arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.034.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
