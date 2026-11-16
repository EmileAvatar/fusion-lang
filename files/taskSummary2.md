# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## Task 45 - Arrays: plain, fixed, growable, up to 3 dimensions (plan, 2026-11-14)

- **Decided:** D.141 (the three forms), D.142 (the `Array` class), D.143 (3 dimensions), D.144 (storage), D.145 (the stack limits)
- **Buffers:** D.146 (built after self-hosting, L16.3); set-up calls right after the declaration: D.147
- **Status:** FEATURES Task 45

**Settings:**
- `[arrays] stackWarn` and `[arrays] stackLimit` (sub-task 9)
- `[arrays] storage` (sub-task 11)
- Each goes into fusionSettings.xml when built
- The buffer settings: L16.3

### The forms
| Form | Written | Size changes by | Lives on |
|---|---|---|---|
| plain | `int[] a = [5, 2, 3]`, `int[10] b`, `int[] e` (size 0) | replacing only: `a = [1, 2]` | the stack; the heap once it can be replaced by another size |
| fixed | `fixed int[10] c`, `fixed int[] d = [5, 2, 3]`, `fixed int[] d = f()` | never - the size is set once, when it is made | the stack when the size is known while compiling; the heap when it comes from `f()` |
| growable | `int:[] g`, `int[[]] g` | `add`, `removeLast` / `pop`, replacing | the heap |
| 3 dimensions | `int[10][5][7]` - rows x columns x depth | `expand(rows / columns / depth, n)` or `expand(0-2, n)`, always with a warning | FLAT (default), RECT or JAGG |

### Sub-tasks, in order (each shipped on its own)
1. **45.1 The `Array` class**
   - `len`, `.length`, `toList` and `toCSV` go behind `Array.method(a)`. The C they produce stays the same.
   - Classes.md 5b gets the value-type design.
2. **45.2 `int[] e`** - valid, size 0
3. **45.14 `fixed`**
   - The size can be written, taken from the values, or taken from `f()` while running.
   - Errors: `fixed int[] d` (no size, no value), `fixed int:[10]`, `add` on a plain or fixed array, `c = [1, 2]` on a fixed array.
4. **45.10 Replacing a plain array with another size**
   - The array gets a run-time length and lives on the heap (a counted block, like a List).
   - The wrapper structs and hidden length parameters go where the heap form is used.
5. **45.3 Growable `int:[]` / `int[[]]`**
   - `add`, `removeLast` / `pop`.
   - An empty `removeLast` is an IndexError.
   - An object slot may be null (D.140).
6. **45.4 `a + b + c`** (Lists too)
7. **45.5 `copyPart` / `copyPartAt`** (Lists too)
8. **45.7 No change while looping** (D.058)
9. **45.13 `stackWarn` / `stackLimit`**, in bytes
10. **45.12 3 dimensions**
    - Indexing and `expand`.
    - Then 45.11: `toList` / `toCSV` on them.
11. **45.15 FLAT / RECT / JAGG**
    - `setStorage`; `setStorage(null)` goes back to FLAT.
    - One row's `add` works on JAGG only.
12. **45.6 Docs and examples**
    - files/Arrays.md truth table, SYNTAX_REFERENCE, spec 031 / 140, the showcase.

**Postponed:**
- 45.8 (threads) moves to Task 42.
- To L16, after self-hosting and profiled first:
  - The buffers TWO / THIRD / RING.
  - The buffer settings.
  - The compiler picking RING above `stackLimit`.

**Tests:**
- Rule 4c: one test per truth-table row, run under the leak check.
- Rule 4b: a null object slot, read with and without `?.`.

- Done 2026-11-15: 45.1 (`Array` class), 45.2 (`int[] e`), 45.14 (`fixed`), C-style `int e[]`, 45.10 (replaced -> heap),
  45.3 (`int:[]` growable, pop gives the item back), 45.4 (`a + b`), 45.5 (`copyPart`), 45.7 (no change while looping), 45.13 (stack limits), 45.3b (`int:[10]`), 45.12a (2 and 3 dimensions), 45.12b (views), 45.12c (functions), 45.17 (bare enum values), 45.12d (growable, expand), 45.11 (toList) - FEATURES Task 45
- Done 2026-11-16: 45.11c (toList skips null slots, D.152), 45.11b (toCSV on arrays of plain values, D.151)
- Done 2026-11-16: 45.12e parts 1-2 (a whole array given to a new one: moved, byVal a copy)
- **Next Action:** 45.12e part 3 (replacing a whole array); 45.15 waits for the "To confirm" points of Q.030-Q.033

### 45.12e and 45.15 - the plan (2026-11-16, to approve)

**Found today:**
- No stack array can be copied as a whole - not even one dimension (`int[3] b = a` is an error)
- Heap and growable arrays of one dimension already move as a List does; `byVal` copies them (D.025)
- A whole array of 2 or 3 dimensions: copying, replacing and `m = f()` are all errors
- Those messages still say "comes with Task 45.12d" (done) - fixed in 45.12e

**45.12e Copying and replacing a whole array** - follows D.025 and D.141, nothing new to decide
- Settings: none
- `int[2][3] n = m` moves: the slots are copied, and `m` can't be used after (as a List)
- `int[2][3] n = byVal m` copies: `m` stays usable; strings copied, objects copied too
- One dimension on the stack the same: `int[3] b = a` / `byVal a`
- `m = [[...]]` with the same shape: the slots replaced
  - another shape: a plain array moves to the heap (as 45.10 on one dimension); a fixed one is an error; a growable one is fine
- `m = f()` and `n = m` after the declaration: the same rules
- The old value's strings and objects freed; every test under the leak check
- Parts, in order: (1) one dimension on the stack, (2) many dimensions, same shape, (3) another shape (heap), (4) the messages

**45.15 Storage FLAT / RECT / JAGG** (D.144, D.147) - waits for OpenQuestions Q.030-Q.033
- Settings: `[arrays] storage` = "flat" (default) / "rect" / "jagg" - into fusionSettings.xml when built
- A built-in enum `Storage`: FLAT, RECT, JAGG, added only when used (as `Dimension`)
- `m.setStorage(RECT)` the line after the declaration or in its set-up block (D.147); anywhere else an error;
  `setStorage(null)` back to FLAT
- RECT: a block per row, all the same length - the program reads the same; slots reached through the row
- JAGG: a block per row, each its own length; one row's `add` (`j[1].add(5)`); anywhere else "use setStorage(JAGG)"
- Parts, in order: (1) the setting, the enum and `setStorage` checks, (2) RECT, (3) JAGG, (4) docs and Arrays.md rows

### 45.12 Up to 3 dimensions - the plan (2026-11-15, replanned after OpenQuestions Q.021-Q.027)
Settings: `[arrays] order` = "columns" (default) / "rows" (D.148), built with 45.12a; `[arrays] storage` is 45.15.
Decided: D.141 (`int:[10]`), D.143, D.148 (order), D.149 (views), D.150 (bare enum values).

Each part is shipped on its own, in this order:
1. **45.3b `int:[10] g`** - a growable array with 10 slots made ahead: length 10, as `int[10]` (D.141);
   `int:[10]` stops being an error (that rule was Claude's, not decided)
2. **45.12a Declaring, reading, writing** - on the stack
   - `int[2][3][4] cube`, `int[2],[3],[4] cube`, `int cube[2][3][4]`, `fixed int[2][3] f`
   - Literals `int[2][3] m = [[1, 2, 3], [4, 5, 6]]`; `int[][] m = [...]` takes its sizes from them;
     rows of different lengths an error (JAGG - 45.15)
   - `m[1][2]` / `m[1],[2]` read and write; every index checked (IndexError)
   - `[arrays] order` (D.148): laid out in memory in the loop's order, so a loop reads the slots one after another
   - `rows`, `columns` (2 and 3 dimensions), `depth` (3 only)
   - Any element type: numbers, strings (freed), structs, objects (null allowed - D.140)
   - A 4th dimension a compile error "the Collections library"
3. **45.12b Views** - an index left out: `cube[1]`, `cube[][2][1]`, `cube[][][3]`
   - `length` the outer dimension first; `-1` on one slot (no error)
   - `foreach` the outer dimension first: depth -> columns -> rows; inside a loop a view is
     borrowed (nothing copied)
   - Given to a variable or a parameter: numbers copied, objects borrowed, `byVal` copies them
4. **45.12c Functions** - parameters `int[2][3] m` (that size) and `int[][] m` (any size, the
   sizes passed hidden); returning one (on the heap); `==` slot by slot
5. **45.17 A bare enum value where the type is known** (D.150) - parameters, declarations, comparisons,
   match: `expand(ROWS, 1)`, `Months m = JUNE`, `case JUNE`; a variable of the same name a compile error
6. **45.12d Growable, many dimensions, and `expand`**
   - `int:[2][3][4] g`, `int[[2],[3],[4]] g`, `int:[][] h = [...]` (best over several lines)
   - The built-in enum `Dimension`: `ROWS`, `COLUMNS`, `DEPTH`
   - `g.expand(ROWS, 1)` - always a warning (every slot is copied); keeps the cube (a row added on
     every sheet); new slots the default value (0, "", false, null)
   - On the heap: one counted block with its sizes (FLAT)
   - `expand` on a plain or fixed array an error; `expand(0, 1)` an error "the Collections library"
7. **45.11** `toList()` (a List of Lists) and `toCSV()` (a line per row) on them
8. **45.16 The cube visualiser** - after 45.12b: an HTML page showing which slots each form reaches

- **Tests:** Rule 4c - a truth table in files/Arrays.md (form x dimensions x operation), each row a
  test; Rule 4b - a null object slot with and without `?.`; everything under the leak check
