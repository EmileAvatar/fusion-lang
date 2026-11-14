# Fusion - Working File (the active plan only)

Only the plan being worked on now and the next action - nothing done, nothing waiting (user,
2026-11-13). Keep it small.
- Status of every task: `files/FEATURES.md` - `[ ]` open, `[DONE]`, `[POSTPONED to X]` with a one-line why
- Finished plans and old sessions: `task/taskSummaryArchive.md` (verbatim)
- Tasks not started: `task/taskBacklog.md`

---

## Task 45 - Arrays: fixed and growable (replanned 2026-11-14 with the user's design - waiting for answers to Q.015-Q.019)

**Settings:** maybe one, `[arrays] stackLimit`, depending on the answer to Q.018. Otherwise none.

### The user's design, as understood

**Two forms of array**
- **A fixed array** is the normal one. It sits inline, on the stack (or inside the object that holds it), never on the heap by itself, and it can't grow:
  - `int[] a = [5, 2, 3]` - its size comes from the values.
  - `int[10] b` - ten zeros.
  - `int[] numbers` - size 0. Valid, and it can't grow.
  - `numbers.add(4)` on any of these is a compile error: "a fixed array can't grow - declare it `int:[]`".
- **A growable array** lives on the heap and grows and shrinks at its end only:
  - `int:[] numbers` - empty, can grow.
  - `int[[]]` - the bracket form. Q.015: is it the same as `int:[]`?
  - Multi-dimensional and growable: `int[[], [], []]` (three empty rows) or `int[[10], [5], [7]]` (rows of 10, 5 and 7 slots). Q.016 covers this.
  - `fixed` on a growable form is an error.
- **Fixed multi-dimensional:** `fixed int[10],[5],[7]`. Q.016 covers this too.

**The `Array` object - every array acts as if it were an object (a kind of autoboxing)**
- `anIntArray.length` means `Array.length(anIntArray)`. It works on any array, fixed or growable.
- The methods live in one built-in `Array` class: `length`, `toList`, `toCSV`, `copyPart` / `copyPartAt` (`slice` / `sliceAt`), `+` and so on.
- Only on a growable array: `add`, `removeLast` (`pop`).
- The same idea for every value type (`int`, `string`, ...): their built-in methods come from a built-in class. TYP.017 / the `Length` interface (52.4) fits under this.

### Conflicts with ACTIVE decisions (Rule 3b - to settle)
- **D.025 and FEATURES 45.10** say "arrays live on the heap and follow the List rules". Now only growable arrays do. The ownership rules (an array moves, `byVal` copies, inside a struct it is only borrowed) stay for both forms. For a fixed array, a move is a copy of its slots, and the old name can't be used after it.
- **D.064 / D.020 (`fixed(n)`, Task 47.5)** mean "at most n, starts empty". The new `fixed int[10],[5],[7]` means "can't grow". Q.017 covers this.
- **COL.015** (multi-dimensional arrays, postponed) comes in with this task. Q.016 covers it.

### Sub-tasks, in order (once the questions are answered)
1. **45.1 The `Array` built-in class:**
   - Move `len` / `.length` / `toList` / `toCSV` on arrays behind `Array.method(arr)`. Today's C stays the same.
   - Write the design for value types in files/Classes.md 5b, beside `Length`.
2. **45.2 `int[] numbers` is valid:** size 0, can't grow. Today it is an error.
3. **45.10 The growable array `int:[]` (and `int[[]]` if Q.015 says so):**
   - On the heap: a counted block like a List, with its length known while running.
   - Pass, return, struct field, `foreach`, equality, `toList`, `toCSV`.
   - Moved and borrowed like a List (D.025). An object slot may be null (D.140).
   - Replacing it with an array of another size: `numbers = [1, 2, 3]`.
4. **45.3 `add`, `removeLast` / `pop`** on a growable array:
   - On a fixed array they are compile errors.
   - `removeLast` on an empty array is an IndexError.
5. **45.4 `a + b + c`:**
   - Makes a new growable array. Q.019: or a fixed array when every size is known?
   - Lists the same.
6. **45.5 `copyPart` / `copyPartAt` (`slice` / `sliceAt`)**, following files/Arrays.md section 8. Lists the same.
7. **45.7 No change while looping (D.058).**
8. **45.12 Multi-dimensional arrays (new, from COL.015):**
   - `int[[10], [5], [7]]` and `fixed int[10],[5],[7]`, depending on the answer to Q.016.
   - Then 45.11: `toList` / `toCSV` on them.
9. **45.13 Large fixed arrays and the stack** (Q.018).
10. **45.6 Docs and examples:**
    - files/Arrays.md with a truth table (form x operation x element type), SYNTAX_REFERENCE, spec 031 and spec 140, the showcase.
    - Decisions.md.

**Postponed:** 45.8 (an array used by threads) moves to Task 42.

**Tests:**
- Rule 4c: every row of the truth table is a test, run under the leak check.
- Rule 4b: a null object slot, read both without a check and with `?.`.

- **Next Action:** the user answers Q.015-Q.019 (OpenQuestions.md); then the answers go into
  Decisions.md and start sub-task 1
