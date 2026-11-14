# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## Task 45 - Arrays: plain, fixed, growable, up to 3 dimensions (plan, 2026-11-14)

- **Decided:** D.141 (the three forms), D.142 (the `Array` class), D.143 (3 dimensions), D.144 (storage), D.145 (the stack limits)
- **Still open:** Q.020, the buffers; Task 45 only needs its point 4 answered
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
  - The buffers TWO / THREE / RING.
  - The buffer settings.
  - The compiler picking RING above `stackLimit`.

**Tests:**
- Rule 4c: one test per truth-table row, run under the leak check.
- Rule 4b: a null object slot, read with and without `?.`.

- **Next Action:** the user approves the plan (and Q.020 point 4); then sub-task 1, 45.1 the `Array` class
