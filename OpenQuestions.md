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

Task 45.12 - arrays of up to 3 dimensions (D.143). Q.021-Q.026 answered 2026-11-15; the
**To confirm** points below wait for the user, then everything moves to Decisions.md.

One example cube for all six: `int[2][3][4] cube` - 2 rows x 3 columns x 4 depth (sheets).

#### Q.021 Reading one slot - which brackets (Task 45.12)
**Answer:** form A - `m[1][2]`, or `m[1],[2]`.

**Understood as:**
```fusion
cube[1][2][3] = 5              // row 1, column 2, sheet 3 (from 0)
cube[1],[2],[3] = 5            // the same slot - the commas only break it up, as in int[2],[3],[4]
cube[1, 2, 3]                  // an error - not a form
```

#### Q.022 Fewer indices - `m[1]` (Task 45.12)
**Answer:** it borrows a view of the row; an empty index means "all of that dimension" -
`m[][2]` all the rows of column 2; `m[][2][1]` all the rows of column 2 on sheet 1.

**Understood as:**
```fusion
cube[1]                        // row 1 - the same as cube[1][][]: a borrowed view, 3 columns x 4 sheets
cube[][2][1]                   // column 2 of sheet 1: a view of 2 values, one from each row
cube[][][3]                    // sheet 3: a view of 2 rows x 3 columns
cube[1][][3]                   // row 1 of sheet 3: a view of 3 values
// a view is borrowed - no copy; cube can't change while one is held (as D.058 in a loop)
cube[][2][1][0] = 7            // writing through a view writes cube[0][2][1]
```
**To confirm:**
- You wrote that `m[][2]` "returns all the columns" - read here as column 2 only, one value per row. Right?
- A view held in a variable: `int[][] sheet = cube[][][3]` - borrowed (cube is frozen while
  `sheet` is used), or a copy?

#### Q.023 foreach over a matrix (Task 45.12)
**Answer:** foreach takes the outer dimension first, or the dev gives the exact array; then another
foreach goes inside it. The order is reversed: depth -> columns -> rows.

**Understood as:**
```fusion
foreach (int[][] sheet in cube)             // 4 times - each sheet (the depth)
    foreach (int[] column in sheet)         // 3 times - each column of that sheet
        foreach (int v in column)           // 2 times - each row's value in that column
foreach (int v in cube[1][][3])             // the dev gives the exact one: row 1 of sheet 3
foreach (int v in cube)                     // an error - a 3-dimension array gives sheets, not ints
```
**To confirm:**
- On 2 dimensions `int[3][4] m` (3 rows x 4 columns): `foreach (int[] column in m)` gives the 4
  columns, each 3 values (most languages give the rows first). Right?

#### Q.024 Its sizes (Task 45.12)
**Answer:** as Q.023 - the outer dimension first: depth -> columns -> rows. `cube.rows`,
`cube.columns`, `cube.depth` only for a regular 3-dimension cube. An irregular one (rows, columns
or depth of different sizes): `cube[x][x][x].length` for that one length - **-1 when there is no
length, not an error**. More than 3: `cube[x][x][x][x].length`.

**Understood as:**
```fusion
cube.length                    // 4 - the outer dimension: depth
cube[][][3].length             // 3 - a sheet's outer dimension: its columns
cube[][2][3].length            // 2 - a column: its rows
cube[1][2][3].length           // -1 - one slot: no length (no error)
cube.rows, cube.columns, cube.depth      // 2, 3, 4 - a regular 3-dimension cube only
int[3][4] m
m.rows                         // an error - 2 dimensions: m.length (4 columns), m[][0].length (3 rows)
```
**To confirm:**
- `cube.length` is 4 (the depth), and on `int[3][4] m` it is 4 (the columns)? A one-dimension
  `int[10]` stays 10.
- An irregular cube is a JAGG one (45.15)? There an index outside it - a row that isn't
  there - also gives -1 from `.length`, or an IndexError?
- `rows` / `columns` / `depth` on a 2-dimension array: an error, or rows and columns allowed?

#### Q.025 Which arrays `expand` works on (Task 45.12)
**Answer:** B - only growable arrays. `expand` keeps the array a cube: expanding rows adds rows on
every sheet. (A visualiser is needed - see below.)

**Understood as:**
```fusion
int[2][3][4] cube
cube.expand(ROWS, 1)           // an error - a plain array doesn't grow (D.141); declare it growable
<growable 2 x 3 x 4> g         // how it is written: To confirm
g.expand(ROWS, 1)              // a warning (every slot is copied) -> 3 x 3 x 4: a new row on every sheet
g.expand(DEPTH, 2)             // -> 3 x 3 x 6: two new sheets at the back
// new slots get the default value (0, "", false, null for an object); n is 1 or more
```
**To confirm:** how a growable many-dimension array is written (D.141: a growable one-dimension
array starts empty - `int:[10]` is an error):
```fusion
A:  int:[2][3][4] g            // the sizes allowed once there are many dimensions
B:  int[[2],[3],[4]] g         // your first form (2026-11-14); int[[]] is the growable mark
C:  int:[][][] g = [[[...]]]   // starts from its values, or empty (0 x 0 x 0)
```

#### Q.026 The names rows / columns / depth (Task 45.12)
**Answer:** `cube.rows`, `cube.columns`, `cube.depth` for a plain Fusion 3-dimension array only;
the enum values are `ROWS`, `COLUMNS`, `DEPTH`. Two forms of `expand`:
`expand(<dimension enum>, <int>)` for a Fusion 3-dimension array, `expand(<int>, <int>)` for it
or for more dimensions.

**Understood as:**
```fusion
g.expand(ROWS, 1)              // the enum - bare, as setStorage(RECT) / setBufferType(TWO)
g.expand(0, 1)                 // the same: dimension 0 is rows, 1 columns, 2 depth
big.expand(3, 1)               // a 4th dimension - only the number form
```
**To confirm:**
- The enum's name - `Dimension` (`Dimension.ROWS`, bare `ROWS` where only a dimension fits)?
- More than 3 dimensions: D.143 put them in the Collections library. Are they now part of the
  language (`int[2][3][4][5]`), or still the library - with `expand(int, int)` working on both?

#### Side task: a cube visualiser (user, 2026-11-15)
An HTML page showing a 3-dimension array as a cube, and which slots `cube[1]`, `cube[][2][1]`,
`foreach` and `expand` reach - for users to see how data is fetched. Scheduled: FEATURES 45.16.

Earlier: Q.013 (modules and namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES
Task 57. Q.014 (a may-be-null parameter mark) answered 2026-11-14: no mark - every object may be
null (D.138, D.117). Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Q.015-Q.020 (arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.027.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
