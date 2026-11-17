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

#### Q.031 rows / columns / foreach on a jagged array (Task 45.15)
A jagged array has no single column count, and `[arrays] order = "columns"` walks the columns first.
```fusion
int[][] j = [[1], [2, 3, 4], [5, 6]]
j.setStorage(JAGG)
print(j.rows)        // 3
print(j[1].length)   // 3 - that row's own length
print(j.columns)     // A: -1 (no single count, as one slot's length)  B: 3 (the longest)  C: an error
foreach (int[] row in j)   // D: a jagged array always walks its rows first, whatever the order setting
    ...                    // E: the order setting holds - a column skips rows too short for it
int[] c = j[][1]           // column 1 - F: an IndexError (row 0 has no slot 1)  G: the rows that have it
```
Suggested: A, D, F.

**Answer (user, 2026-11-16):** check how other languages handle JAGG arrays; to me depth -> columns -> rows.

**What other languages do (Claude, 2026-11-16):**
- C#, Java, JavaScript, Go, Python, Rust: a jagged array is an array of arrays - the outer one holds the rows
- `j.length` is the number of rows; `j[1].length` that row's own length; none has a column count
- A loop gives the rows, one by one; a column is the programmer's own loop - a row too short for it
  is an IndexError (C#, Java, Go, Python, Rust) or `undefined` (JavaScript)
- C# also has a rectangular `int[,]` - `GetLength(0)`, `GetLength(1)`; only that one has columns
- NumPy refuses uneven rows (an error since 1.24); MATLAB keeps them in a cell array, walked column by column
- So no language walks a jagged array column by column - Fusion's order (D.148) would be its own

**Answer 2 (user, 2026-11-16):** `j.columns` is not the longest - it is the length of whatever row it is on.

**Understood as:**
```fusion
int:[][] j = [[1], [2, 3, 4], [5, 6]]
j.setStorage(JAGG)
print(j.rows)            // 3
print(j[1].columns)      // 3 - the row it is on (the same as j[1].length)
print(j[0].columns)      // 1
print(j.columns)         // no row given: an error "each row has its own length - j[r].columns" (to confirm)
```

**To confirm:**
- `j.columns` with no row - an error (above)?
- Walking a column (`j[][1]`, foreach with order = "columns"): a row too short for it skipped, or an IndexError?
- `[arrays] order = "rows"` walks a jagged array row by row, as the other languages do?

#### Q.034 The script libraries' names (Task 60, files/taskSummary2.md)
```fusion
// A (suggested): under Fusion's own namespace (D.136, 57.5), one family "Script"
import Fusion.Script.Lua
import Fusion.Script.JS
import Fusion.Script.Fusion       // the Fusion interpreter
import Fusion.Compiler            // the compiler as a library

// B: next to the language modules (Task 49, D.121)
import Lang.Lua.Script

// C: a top-level name of their own
import Script.Lua
```
Suggested: A - B mixes "translate another language" (Task 49) with "run a script while running".

#### Q.035 When, and the prerequisites (Task 60)
Lua is a C library, and Fusion can't call C yet (`extern "C"` is designed only - FUN.011), nor load a library
(modules are Task 57, not built).
- A (suggested): after Task 45, Task 60 builds the minimum of both itself - `extern "C"` (60.1) and a library folder (60.2); Task 57 grows them later
- B: Task 57 (modules) in full first, then `extern "C"`, then Lua
- C: after self-hosting, all of it

#### Q.036 How much a script may do by default (Task 60.4)
```fusion
Lua mods = Lua()
// A (suggested): nothing - no files, no OS, no loading other code; only what the game exposes;
//    a step limit and a memory limit always on (defaults, changed in the set-up block)
// B: Lua's normal libraries on; the program removes what it doesn't want
// C: A, with a toml setting to change the defaults for the whole project
mods.allow(LuaLib.STRING, LuaLib.MATH)   // a way to give some back
```
Suggested: A - never trust code (GOL.008, D.122); a game mod is someone else's code.

#### Q.037 Which Lua, and keeping its source (Task 60.3)
- A (suggested): Lua 5.4 - plain C, builds with GCC everywhere; its source (MIT licence, about 30 files) kept in the repo under the library, a pinned version, the licence beside it
- B: LuaJIT - much faster, but Lua 5.1's language and fewer platforms
- C: Luau (Roblox's) - made for sandboxed game scripts, but C++, not C
- D: not kept in the repo - the developer installs Lua

Earlier: Q.030, Q.032, Q.033 (jagged arrays, 3 dimensions and the stack) answered 2026-11-16: Decisions.md D.144, D.153, D.154.
Earlier: Q.028 (toCSV on arrays) and Q.029 (toList and null slots) answered 2026-11-16: Decisions.md D.151, D.152, FEATURES 45.11b / 45.11c, Notes/CSV_many_dimensions.md.
Earlier: Q.021-Q.027 (arrays of 3 dimensions, bare enum values) answered 2026-11-15:
Decisions.md D.141, D.143, D.148-D.150, FEATURES 45.12, 45.3b, 45.16, 45.17. Q.013 (modules and
namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES Task 57. Q.014 (a may-be-null
parameter mark) answered 2026-11-14: no mark - every object may be null (D.138, D.117). Q.001-Q.012
answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status PARTIAL; FEATURES
48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the name). Q.015-Q.020
(arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.038.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
