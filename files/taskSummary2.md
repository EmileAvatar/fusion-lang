# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## Task 45 - Arrays: plain, fixed, growable, 3 dimensions (replanned 2026-11-14, third time)

The design: OpenQuestions.md "Q.015-Q.019" (answered; 6 small points to confirm).

**Settings:**
- `[arrays] stackWarn = "16KB"` - a warning, sub-task 9
- `[arrays] stackLimit = "64KB"` - a compile error, sub-task 9
- `[arrays] storage = "flat"`, with `"rect"` and `"jagg"` - sub-task 11
- Each goes into fusionSettings.xml when its sub-task is built

### The forms
| Form | Written | Size changes by | Lives on |
|---|---|---|---|
| plain | `int[] a = [5, 2, 3]`, `int[10] b`, `int[] e` (size 0) | replacing only: `a = [1, 2]` | the stack (under `stackLimit`); the heap when the compiler sees it replaced |
| fixed | `fixed int[10] c` - the number is required | never: replacing with another size is an error | the stack |
| growable | `int:[] g`, `int[[]] g` | `add`, `removeLast` / `pop`, replacing | the heap |
| 3 dimensions | `int[10][5][7]` (or `int[10],[5],[7]`) - rows x columns x depth | `expand(rows / columns / depth, n)`, or `expand(1-3, n)` - with a warning | FLAT by default; RECT / JAGG with `setStorage` |

Errors:
- `fixed int[] d`: fixed needs its size
- `fixed int:[10]` and `fixed int[[10]]`: fixed and growable can't go together
- `add` on a plain or fixed array: "declare it int:[]"

`fixed(n)` on Lists, Maps and strings is not this task (Task 47.5):
- It means "at most n", with the n slots reserved at once (D.020, D.064)

**The `Array` class** works on every array:
- `a.length` is `Array.length(a)`
- On every array: `toList`, `toCSV`, `copyPart`, `+`
- On growable arrays only: `add`, `removeLast`, `expand`, `setStorage`
- Every value type gets its methods the same way (TYP.017)

### Decisions once confirmed (Rule 3b)
- New D rows: the three forms; `fixed` on arrays; 3 dimensions and storage; the stack limits
- D.025: only growable and replaced arrays live on the heap; the ownership rules stay for every form
- D.064: its array example becomes `fixed int[10]`
- COL.002 rewritten; COL.015 joins Task 45

### Sub-tasks, in order (each shipped on its own)
1. **45.1 The `Array` class**
   - `len`, `.length`, `toList` and `toCSV` go behind `Array.method(a)`. The C they produce stays the same.
   - The design for value types goes into files/Classes.md 5b.
2. **45.2 `int[] e`** - valid, size 0
3. **45.14 `fixed int[10] c`** - and the errors above
4. **45.10 Replacing with another size**
   - `a = [1, 2]` and `int[] function make(int n)`: the array has a run-time length and lives on the heap (a counted block, like a List).
   - The wrapper structs and hidden length parameters go where the heap form is used.
5. **45.3 Growable `int:[]` / `int[[]]`**
   - `add`, `removeLast` / `pop`
   - `removeLast` on an empty array is an IndexError
   - An object slot may be null (D.140)
6. **45.4 `a + b + c`** - makes a new array. Lists the same
7. **45.5 `copyPart` / `copyPartAt` (`slice` / `sliceAt`)** - as in Arrays.md section 8. Lists the same
8. **45.7 No change while looping** (D.058)
9. **45.13 `stackWarn` / `stackLimit`** - measured in bytes
10. **45.12 3 dimensions**
    - `int[10][5][7]`, indexing, `expand` by name or number (with its warning)
    - Then 45.11: `toList` / `toCSV` on them
11. **45.15 Storage**
    - FLAT (default), RECT, JAGG
    - `setStorage`, and `[arrays] storage`
    - A single row's `add` works on JAGG only
12. **45.6 Docs and examples**
    - files/Arrays.md with a truth table (form x operation x element type)
    - SYNTAX_REFERENCE, spec 031 / 140, the showcase, Decisions.md

**Postponed:**
- 45.8 (threads) moves to Task 42.
- These go to L16, after self-hosting and profiled first:
  - L16.1-L16.2: the double buffer and the ring buffer
  - L16.3: the load amounts
  - L16.4: the program sets its own stack amounts where it runs
  - L16.5: GPU / CPU options for large arrays

**Tests:**
- Rule 4c: each truth-table row, run under the leak check
- Rule 4b: a null object slot, with and without `?.`

- **Next Action:** the user confirms the 6 points (OpenQuestions.md); then Decisions.md, then sub-task 1
