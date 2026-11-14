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
Both were given for "this array can grow". Are they the same thing?

**Answer** (user, 2026-11-14): two forms of the same thing - `int:[]` for less clutter, `int[[]]` to
stand out visually as growable.

**Understood as:**
```fusion
int:[] a          // growable, short form
int[[]] b         // growable, the same meaning - easy to spot
int[] c           // fixed (size 0 here) - can't grow
```
**To confirm:** nothing - ready for Decisions.md.

#### Q.016 Multi-dimensional arrays - the shape (Task 45, COL.015)
**Answer** (user, 2026-11-14): think of a cube - x is the rows, y the columns in each row, z the
sheets of x-y. Up to 3 dimensions for now (more later, in the Collections library) - for basic
matrices, math and rendering. Growing works on a whole dimension (`expand`) or on one row only (`add`).

**Other languages:**
- Names: NumPy calls a dimension an **axis** (0 = rows, 1 = columns, 2 = depth); MATLAB calls the third
  dimension **pages**; images call it **depth** or **channels**. The count of dimensions is the **rank**
- Two kinds: **rectangular** - every row the same length, one flat block (C# `int[,,]`, Fortran, NumPy -
  fast for matrices); **jagged** - an array of arrays, each row its own length (Java `int[][]`, C# `int[][]`)
- Growing a whole dimension: NumPy `np.append(a, b, axis=1)` / `np.pad` make a new array; C#, Java and
  Go can only resize one dimension by copying. None lets one row of a rectangular array grow

**Understood as** (names to confirm):
```fusion
int[[10], [5], [7]] cube      // 10 rows x 5 columns x 7 sheets, can grow (also int:[10][5][7]?)
cube[2][3][1] = 9             // row 2, column 3, sheet 1
cube.expand(columns, 2)       // every row gets 2 more columns - stays rectangular
cube[4][0].add(8)             // only row 4 (sheet 0) gets one more column - now jagged
int[10][5][7] box             // fixed (fixed is not used on arrays - Q.017)
```
**To confirm:**
- A. **The storage:** one flat block (fast for matrices) while rectangular, turning into rows of their
  own once one row gets an `add` - or B. always rows of their own (simpler, slower for matrices)
  - or C. two types: a rectangular one (`expand` only) and a jagged one (`add` per row). Suggested: **C**
- The names of the three dimensions: `rows`, `columns`, `sheets` (suggested - plain words), or `x`, `y`, `z`
- The fixed form: `int[10][5][7]` (suggested - C, Java and C# write it this way), or `int[10],[5],[7]`

#### Q.017 `fixed` on arrays, and D.064's `fixed(n)` (Task 45, Task 47.5)
**Answer** (user, 2026-11-14): an array is fixed already. `fixed` stays a reserved word, used on Lists,
Maps and strings to enforce "at most n".

**Understood as:**
```fusion
int[10] a                        // fixed - can't grow
fixed int[10] a                  // an error: an array is fixed already - drop 'fixed' (but see Q.019)
fixed(10) string name            // at most 10 characters (D.064, Task 47.5)
fixed(14) List<Person> people    // at most 14 elements
```
**To confirm:** Q.019's answer gives `fixed` a job on arrays (never another size) - see the clash there.

#### Q.018 A large fixed array on the stack (Task 45)
**Answer** (user, 2026-11-14): a large array goes on the heap depending on the stack size; the stack
holds only the part being used. A setting warns at one length and gives an error at another; two more
settings say how many items are loaded onto the stack (small / large arrays). Example numbers only.
The double buffer / ring buffer idea waits until after self-hosting, and profiling (L16).

**Other languages:**
- MSVC warns (C6262) when a function uses more than 16 KB of stack; Rust's Clippy warns
  (`large_stack_arrays`) above 512 KB; GCC warns only when asked (`-Wframe-larger-than=N`)
- Go puts a variable above 128 KB (64 KB when made with `make` / `new`) on the heap by itself - escape
  analysis; Java, C# and Swift always put arrays on the heap
- Limits are in **bytes**, not items: 5000 `int`s is 20 KB, 5000 `long`s 40 KB
- None of them copies parts of an array onto the stack: the CPU's cache already keeps the items in use
  close, and loads ahead in an ascending or descending loop (the hardware prefetcher). The stack is the
  same RAM as the heap - what makes it fast is the cache

**Understood as:**
```toml
[arrays]
stackWarn  = "16KB"   # a fixed array above this on the stack: a warning
stackLimit = "64KB"   # above this the compiler puts it on the heap - still fixed, freed at the end of its scope
```
**To confirm:**
- In bytes (suggested, like the other languages) or in items?
- "Error at 10000": an error, or (as your answer also says) the heap? Suggested: the heap, with a note -
  so a large array never crashes and never stops the build
- `loadSmall` / `loadLarge` (items copied to the stack): the cache already does this, so measure first.
  Suggested: they join the buffers in L16 (after self-hosting, with profiling) rather than Task 45

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

**Answer** (user, 2026-11-14): changing an array's size is fine - an error only when the array is
declared `fixed`, to show it must not change.

**Understood as:**
```fusion
int[] a = [5, 2, 3]
a = [1, 2]                     // fine - a is replaced by an array of 2; the old one is freed
int[] function make(int n)     // fine - any size
fixed int[3] b = [5, 2, 3]
b = [1, 2]                     // an error: b is fixed - its size never changes
b = [7, 8, 9]                  // fine - same size, new values
a.add(4)                       // still an error - only int:[] / int[[]] grows at its end
```
- Where it lives: an array the compiler sees is never resized (or `fixed`, under `stackLimit`) goes on
  the stack; one that may be replaced by another size goes on the heap

**To confirm:**
- **A clash with Q.017**: there, `fixed int[10]` was to be an error ("an array is fixed already").
  Now `fixed` on an array has a job - "never another size". Suggested: `fixed` is allowed on arrays
  with this meaning, and the Q.017 understanding changes to match
- Is `a = [1, 2]` (replace) the only way a plain array changes size, while `add` / `removeLast` stay
  for the growable form? Suggested: yes

Earlier: Q.013 (modules and namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES
Task 57. Q.014 (a may-be-null parameter mark) answered 2026-11-14: no mark - every object may be
null (D.138, D.117). Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Next question: Q.020.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
