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

#### Q.028 toCSV on arrays of plain values (Task 45.11, FEATURES 45.11)
`toCSV()` works on structs only today - an `int[]` has none, so a grid of numbers has none either.
```fusion
int[][] m = [[1, 2, 3], [4, 5, 6]]
A:  m.toCSV()       // "1,2,3\n4,5,6" - a line per row, the delimiter between values;
                    // 3 dimensions: a blank line between sheets; an int[] gives one line "1,2,3"
B:  m.toCSV()       // an error - CSV stays for structs (a heading row and their fields)
```
Suggested: A - a line per row is what a spreadsheet reads, whatever `[arrays] order` says.

**Answer (user, 2026-11-16):** a line per row. `toCSV(primaryDelimiter = ",", secondaryDelimiter = "#",
lineDelimiter = "\n")` - the secondary delimiter splits dimension 3 and upwards.

**Other languages (checked 2026-11-16):** none defines a 3-dimension CSV. NumPy's savetxt refuses more
than 2 dimensions; MATLAB's writematrix puts the sheets side by side on each row, with the same
delimiter and no mark between them (`1,1,2,2,3,3`); Julia's writedlm takes 2 dimensions - so the
secondary delimiter is Fusion's own, and it marks where each sheet starts.

**Understood as:**
```fusion
int[][] m = [[1, 2, 3], [4, 5, 6]]
m.toCSV()                     // "1,2,3\n4,5,6" - a line per row
m.toCSV(";")                  // "1;2;3\n4;5;6"
int[] a = [1, 2, 3]
a.toCSV()                     // "1,2,3" - one line
int[2][2][2] cube             // sheet 0: [[1, 2], [3, 4]]   sheet 1: [[5, 6], [7, 8]]
```
**To confirm** - where the secondary delimiter goes on 3 dimensions:
```text
A:  cube.toCSV()   // "1,2#5,6\n3,4#7,8" - a line per row; that row of each sheet side by side,
                   //  the sheets split by "#" (MATLAB's layout, with the mark it lacks)
B:  cube.toCSV()   // "1#5,2#6\n3#7,4#8" - a line per row; each cell holds its depth values split by "#"
```
- Strings: written as they are, or in quotes when they hold a delimiter (`"a,b"`), as CSV does?

#### Q.029 A null slot in a one-dimension array's toList (D.139, D.140)
An array slot may be null (D.140); a List never holds null (D.139). Today `Car[] cars` with a null
slot gives a List holding null - against D.139. The new `toList` of 2 and 3 dimensions raises a
NullError (45.11).
```fusion
Car[2] cars
cars[0] = Car("red")              // cars[1] is null
A:  List<Car> l = cars.toList()   // a NullError: "toList: a slot is null - a List never holds null"
B:  List<Car> l = cars.toList()   // [red] - the null slots left out (the List shorter than the array)
```
Suggested: A - nothing changes silently, the same for every array.

**Answer (user, 2026-11-16):** B - the null slots are skipped, only the filled ones are added; if
every slot is null the List is empty. No error.

**Understood as:**
```fusion
Car[3] cars
cars[1] = Car("red")              // cars[0] and cars[2] are null
List<Car> l = cars.toList()       // [red] - l.len() is 1
Car[2] none
List<Car> e = none.toList()       // [] - empty, no error
Car[2][2] grid                    // grid[0][1] is the only one set
List<List<Car>> g = grid.toList() // its columns: [[], [car]] - each column's nulls skipped
```
- This replaces 45.11's NullError on 2 and 3 dimensions; the one-dimension toList stops adding null
- Numbers, strings and enums are never skipped - only an object slot that is null (an enum slot that
  is null too, D.051)

**To confirm:** on 2 and 3 dimensions, a column whose slots are all null stays as an empty List
(`[[], [car]]` above - the shape kept), rather than being left out?

Earlier: Q.021-Q.027 (arrays of 3 dimensions, bare enum values) answered 2026-11-15:
Decisions.md D.141, D.143, D.148-D.150, FEATURES 45.12, 45.3b, 45.16, 45.17. Q.013 (modules and
namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES Task 57. Q.014 (a may-be-null
parameter mark) answered 2026-11-14: no mark - every object may be null (D.138, D.117). Q.001-Q.012
answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status PARTIAL; FEATURES
48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the name). Q.015-Q.020
(arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.030.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
