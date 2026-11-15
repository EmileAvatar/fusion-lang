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

Task 45.12 - arrays of up to 3 dimensions (D.143). Q.021-Q.026 answered 2026-11-15 (two rounds);
what is still open is under **To confirm**. Once confirmed, everything moves to Decisions.md
(D.143 changes: `expand` on growable arrays only, the number form with the Collections library).

One example cube for all of them: `int[2][3][4] cube` - 2 rows x 3 columns x 4 depth (sheets).

#### Q.021 Reading one slot (Task 45.12) - answered
**Answer:** `m[1][2]`, or `m[1],[2]`.
```fusion
cube[1][2][3] = 5              // row 1, column 2, sheet 3 (from 0)
cube[1],[2],[3] = 5            // the same slot
```

#### Q.022 Fewer indices - a view (Task 45.12) - answered
**Answer:** an index left out means all of that dimension; `m[][2]` is column 2 in every row.
A view given to a variable: numbers (primitives) are copied, objects are borrowed unless `byVal`
is used - so a variable is easier to work with than the whole cube.
```fusion
cube[1]                        // row 1 - the same as cube[1][][]: 3 columns x 4 sheets
cube[][2][1]                   // column 2 of sheet 1: one value from each row (2 values)
cube[][][3]                    // sheet 3: 2 rows x 3 columns
int[][] sheet = cube[][][3]    // a copy of the numbers - sheet changes on its own
Car[] column = cars[][2][1]    // a new array holding the same objects (borrowed)
Car[] mine = byVal cars[][2][1]           // the objects copied too
```

#### Q.023 / Q.024 foreach and sizes - the outer dimension first (Task 45.12)
**Answer:** foreach and `length` give the outer dimension first: depth -> columns -> rows. An
`int[3][4]` gives 4 columns, each of 3 rows. `.length` on something with no length - one slot,
or a row an irregular (JAGG) array doesn't have - is **-1**, not an error; reading a slot that
isn't there (`m[9][9]`) is an IndexError. `rows` and `columns` on 2 and 3 dimensions; `depth` only
on 3.
```fusion
cube.length                    // 4 - depth
cube[][][3].length             // 3 - a sheet: its columns
cube[][2][3].length            // 2 - a column: its rows
cube[1][2][3].length           // -1 - one slot
cube.rows, cube.columns, cube.depth      // 2, 3, 4
foreach (int[][] sheet in cube)             // 4 sheets
    foreach (int[] column in sheet)         // 3 columns each
        foreach (int v in column)           // 2 values each - one per row
int[3][4] m
m.length                       // 4 - its columns
m.rows, m.columns              // 3, 4;  m.depth - an error (2 dimensions)
```
**To confirm (the order):** most languages go the other way - C, C++, Java, C#, JavaScript and
Python give the **rows** first (`int m[3][4]`: `m.length` is 3, a loop gives 3 rows of 4).
Fortran, MATLAB, Julia and R go **columns** first, as here - the languages made for maths.
The order also sets how the slots lie in memory, so the loop reads them one after another (fast):
```text
int[3][4] m, columns first (here):  m[0][0] m[1][0] m[2][0]  m[0][1] m[1][1] m[2][1]  ...
int[3][4] m, rows first (C, Java):   m[0][0] m[0][1] m[0][2] m[0][3]  m[1][0] ...
```
Your rule (2026-10-27): where languages differ, a setting whose default is what most languages do.
```text
A:  [arrays] order = "columns" (default) / "rows" - your design as the default
B:  [arrays] order = "rows" (default) / "columns" - the most common as the default
C:  columns first always - no setting
```

#### Q.025 Growable arrays and `expand` (Task 45.12) - answered
**Answer:** only growable arrays expand; expanding keeps the cube (a new row on every sheet).
`int:[10]` is a one-dimension array with 10 slots made ahead. A growable many-dimension array:
`int:[2][3][4] g` or `int[[2],[3],[4]] g`, or from its values - best split over several lines.
```fusion
int:[2][3][4] g                // also int[[2],[3],[4]] g
int:[][] h = [
    [1, 2, 3],
    [4, 5, 6]]                 // from its values: 2 x 3
g.expand(ROWS, 1)              // a warning (every slot is copied) -> 3 x 3 x 4
int[2][3][4] cube
cube.expand(ROWS, 1)           // an error - a plain array doesn't grow (D.141)
```
**To confirm:** `int:[10] g` - "10 slots made ahead" means:
```text
A:  g.length is 10 - ten slots of 0, as int[10]; g.add(5) makes it 11
B:  g.length is 0 - room for 10 made ahead; the first 10 add() calls don't copy (as fixed(10), Q.017)
```

#### Q.026 Dimension names and `expand` (Task 45.12) - answered
**Answer:** the enum is `Dimension` - `ROWS`, `COLUMNS`, `DEPTH`. In the core: `expand(<Dimension>,
<int>)`. `expand(<int>, <int>)` and more than 3 dimensions come with the Collections library - a
library adds methods as if they were the core's, and Collections is imported by itself for any
collection. Until then a 4th dimension is a compile error.
```fusion
g.expand(ROWS, 1)
g.expand(0, 1)                 // an error for now - the Collections library (later)
int[2][3][4][5] big            // an error for now - more than 3 dimensions: the Collections library
```

#### Q.027 A bare enum value where the type is known (Task 45.17, all enums) - answered in part
**Answer (Q.026):** where an enum is expected in a parameter, the value alone is enough:
`expand(ROWS, 1)`; with `enum Months`: `setMonth(JUNE)`.
```fusion
enum Months
    JANUARY, FEBRUARY, ..., JUNE, ...
void function setMonth(Months m)
setMonth(JUNE)                 // the same as setMonth(Months.JUNE)
```
**To confirm:**
- Also where else the type is known?
  ```text
  A:  parameters only
  B:  also a declaration (Months m = JUNE), a comparison (m == JUNE) and a match (case JUNE)
  ```
- A variable named `JUNE` in the same place: a compile error "JUNE is both a variable and a
  Months value - write Months.JUNE" (nothing chosen silently)?

#### Side task: a cube visualiser (user, 2026-11-15)
An HTML page showing a 3-dimension array as a cube, and which slots `cube[1]`, `cube[][2][1]`,
`foreach` and `expand` reach. FEATURES 45.16.

Earlier: Q.013 (modules and namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES
Task 57. Q.014 (a may-be-null parameter mark) answered 2026-11-14: no mark - every object may be
null (D.138, D.117). Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Q.015-Q.020 (arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.028.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
