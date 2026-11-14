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

#### Q.015 The growable form: `int:[]` and `int[[]]` (Task 45, files/Arrays.md)
Both were given for "this array can grow". Are they the same thing, or does each have its own job?
```fusion
int:[] numbers            // can grow - one dimension
int[[]] numbers           // A: the same as int:[] - two spellings
                          // B: int:[] for one dimension; [[...]] only for more: int[[], [], []]
                          // C: only int:[]; growable rows are written int:[][3] (or similar)
```
Suggested: **B** - one way to write each shape.

#### Q.016 Multi-dimensional arrays - the shape (Task 45, COL.015)
Understood: `int[[10], [5], [7]]` is three rows, of 10, 5 and 7 slots (rows may differ in length - "jagged").
```fusion
int[[10], [5], [7]] grid      // 3 rows: 10, 5, 7 slots; each row can grow at its end
grid[1].add(4)                // row 1 now has 6 slots
grid.add([])                  // A: a 4th row - the number of rows grows too
                              // B: an error - 3 rows always; only the rows grow
fixed int[10],[5],[7] table   // nothing grows: table[2].add(1) is an error
int[3][4] board               // C: also a square fixed form (3 rows of 4) - or not needed?
```
Suggested: **A** for the growable form (rows grow too). For a square board, ask separately: is `int[3][4]` wanted, or is `fixed int[4],[4],[4]` enough?

#### Q.017 `fixed` on arrays, and D.064's `fixed(n)` (Task 45, Task 47.5)
A plain `int[10]` already can't grow, so `fixed` adds nothing there. D.064 (ACTIVE) says `fixed(n)` means "at most n, starts empty, the values may change".
```fusion
int[10] a                        // fixed already - can't grow
fixed int[10] a                  // A: allowed, the same as int[10] (says it out loud)
                                 // B: an error - write int[10]; fixed only on many dimensions
fixed int[10],[5],[7] t          // fixed many dimensions
fixed(10) string name            // D.064: at most 10 characters - stays (Task 47.5)
fixed(14) List<Person> people    // D.064: at most 14 - stays
```
Suggested: **A**, and D.064 stays for strings, Lists and Maps ("at most n").

#### Q.018 A large fixed array on the stack (Task 45)
The stack is small: 1 MB per thread by default on Windows, 8 MB on Linux. `int[1000000] a` is 4 MB and would crash the program when it starts the function.
```fusion
int[1000000] samples
// A: a compile error above a limit ([arrays] stackLimit, e.g. 64 KB): "use int:[] or a smaller size"
// B: above the limit the compiler puts it on the heap for you - still fixed, freed at the
//    end of its scope - and says so in a note (not a warning)
// C: allowed - the developer's risk
```
Suggested: **B** - it never crashes, and nothing about its values changes. C# and Go do the same: the compiler picks the place.

#### Q.019 A fixed array's size is known when compiling (Task 45)
A fixed array lives on the stack, so its size must be known when the program is compiled.
```fusion
int[] a = [5, 2, 3]          // size 3 - known
a = [1, 2]                   // A: an error - a fixed array keeps its size (use int:[])
int[] function make(int n)   // a size that depends on n:
                             // A: an error - return int:[] instead
                             // B: allowed - such a fixed array goes on the heap, still can't grow
int[] c = a + b              // A: fixed when both sizes are known, else growable
```
Suggested: **A** - "fixed" always means the size is known and never changes.

Earlier: Q.013 (modules and namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES
Task 57. Q.014 (a may-be-null parameter mark) answered 2026-11-14: no mark - every object may be
null (D.138, D.117). Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Next question: Q.020.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
