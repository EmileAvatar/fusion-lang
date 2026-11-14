# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## Task 45 - Arrays: plain, fixed, growable, up to 3 dimensions (replanned 2026-11-14, second time)

Answers: Q.015-Q.019 (OpenQuestions.md). The "To confirm" points still open:
- Q.016 the storage of many dimensions (C suggested), the names (`rows` / `columns` / `sheets`), the fixed form `int[10][5][7]`
- Q.018 bytes or items; the heap (not an error) above `stackLimit`; `loadSmall` / `loadLarge` -> L16
- Q.019 vs Q.017: `fixed` allowed on arrays, meaning "never another size"

**Settings:** `[arrays] stackWarn`, `[arrays] stackLimit` (Q.018 - sub-task 9). `loadSmall` / `loadLarge`
wait in L16.3 with the buffers (after self-hosting, profiled first).

### The design, as understood
| Form | Example | Size changes by | Lives on |
|---|---|---|---|
| plain | `int[] a = [5, 2, 3]`, `int[10] b`, `int[] c` (size 0) | replacing: `a = [1, 2]` | the stack when never resized, else the heap |
| fixed | `fixed int[3] b` | never - `b = [1, 2]` is an error | the stack (the heap above `stackLimit`) |
| growable | `int:[] a`, `int[[]] a` (the same) | `add`, `removeLast` / `pop` at the end, and replacing | the heap |
| 3 dimensions | `int[[10], [5], [7]]` rows x columns x sheets | `expand(columns, 2)` a whole dimension; `cube[r][s].add(x)` one row | the heap |

- `add` on a plain or fixed array: a compile error - "declare it `int:[]`"
- **The `Array` class:** `a.length` is `Array.length(a)`; `length`, `toList`, `toCSV`, `copyPart`, `+`
  on every array; `add` / `removeLast` / `expand` only on growable ones. Every value type the same way
  (TYP.017 - the design goes into files/Classes.md 5b)
- `fixed(n)` on Lists, Maps and strings: "at most n" (D.064, Task 47.5 - not this task)

### Decisions to update once confirmed (Rule 3b)
- D.025: only growable (and resized) arrays live on the heap; the ownership rules stay for every form
- D.064: `fixed` on an array means "never another size"; `fixed(n)` on strings / Lists / Maps "at most n"
- New rows for Q.015-Q.019; COL.002 rewritten; COL.015 (3 dimensions) moves into Task 45

### Sub-tasks, in order (each shipped on its own)
1. **45.1 The `Array` class:** `len` / `.length` / `toList` / `toCSV` behind `Array.method(a)` (same C); value-type design in Classes.md 5b
2. **45.2 `int[] c`:** valid, size 0
3. **45.10 The run-time length + the heap when needed:** a plain array the compiler sees replaced by another size goes on the heap (a counted block, like a List); `a = [1, 2]`, `int[] function make(int n)`; the wrapper structs and hidden length parameters go where the heap form is used
4. **45.14 `fixed int[3] b`:** another size is an error (Q.019)
5. **45.3 The growable form `int:[]` / `int[[]]`:** `add`, `removeLast` / `pop`; an empty `removeLast` is an IndexError; an object slot may be null (D.140)
6. **45.4 `a + b + c`** - a new array (Lists the same)
7. **45.5 `copyPart` / `copyPartAt` (`slice` / `sliceAt`)** - Arrays.md section 8 (Lists the same)
8. **45.7 No change while looping (D.058)**
9. **45.13 Large arrays:** `[arrays] stackWarn` (a warning) and `stackLimit` (the heap, still fixed)
10. **45.12 Up to 3 dimensions** (Q.016): rows, columns, sheets; `expand`, a row's `add`; then 45.11 `toList` / `toCSV` on them
11. **45.6 Docs and examples:** files/Arrays.md with a truth table (form x operation x element type), SYNTAX_REFERENCE, spec 031 / 140, the showcase, Decisions.md

**Postponed:** 45.8 (threads) -> Task 42; buffers / ring buffer / load settings -> L16 (after self-hosting).

**Tests:** each truth-table row (Rule 4c), under the leak check; a null object slot with and without `?.` (Rule 4b).

- **Next Action:** the user confirms the open points above; then the answers go into Decisions.md and
  sub-task 1 starts
