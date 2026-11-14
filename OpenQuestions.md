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

#### Q.014 How is a parameter marked "may be null"? (D.117, Task 52.7 - 2026-11-14)

D.117: "a parameter marked `?` without a null check warns". `T?` types are rejected (NUL.004 - `?` goes
on a variable, `x?.f()`), so the mark needs a place:

```fusion
void function drive(Car c)          // today: c may be null - nothing says so
    c.start()                       // a NullError at run time if it is

// the mark - which form?
void function drive(Car c?)         // A: `?` after the name - "c may be null"
void function drive(nullable Car c) // B: a word before the type
void function drive(Car c = null)   // C: a null default says it
    if c is null                    // with the mark: no warning once checked
        return
    c.start()
```

- **A** `Car c?` - short, and `?` stays on the variable (NUL.004); Claude's reading
- **B** `nullable Car c` - a word, like `readonly Car c`
- **C** `Car c = null` - no new syntax, but only for a parameter that can be left out

--|---|---|
| C# | `namespace Game.Inventory` (naming only) | No | The project (assembly, a DLL) |
| Kotlin | `package game.inventory` | No | The Gradle module |
| Java | `package game.inventory` | Yes | The JAR / Java module |
| Go | `package inventory` | Yes - one folder, one package | The module (`go.mod`) |
| Python | none - the file is the module | Yes | The package folder |
| Rust | `mod inventory;` in the parent | Yes | The crate |

**Part 1 - what makes a file part of a module:**
- **A** As built: the folder is the module (Go / Python)
- **B** A `module Fusion.IO` line, first in the file, decides it - wherever the file lives; folders only
  tidy files away (C# / Kotlin). All files with the same line are one module and, later, one DLL
- **C** Both: the folder by default; a `module` line, when written, overrides it
- **D** A `module` line, and the folder must match it (Java) - the compiler checks

**Part 2 - what a namespace is then:**
- **A** Keep it as built: `namespace` lets several modules share `internal` names
- **B** Drop `namespace`: the module is the boundary - `internal` means "my module"; dotted module names
  (`Fusion.IO`, `Fusion.Database`) already group them
- **C** A namespace only names a group inside a module (ChatGPT's design) - no access rules;
  `internal` means "my module"

What option B + B would look like (Claude's suggestion - a change to built behaviour):

```fusion
// src/io/file.fusion  (the folder doesn't matter)
module Fusion.IO                                  // this file belongs to module Fusion.IO

public class File
    ...
internal int function bufferSize() : 4096         // every file of Fusion.IO sees it; other modules don't

// src/io/directory.fusion
module Fusion.IO                                  // the same module, another file

public class Directory
    ...

// main.fusion
import Fusion.IO                                  // IO.File, IO.Directory (the last part, as built)
import Fusion.IO.File                             // File - one name, no prefix
import Fusion.Database as Db                      // an alias: Db.Connection

IO.File log = IO.File("log.txt")
```

What would change if B + B is chosen:
- The loader finds a module's files by their `module` line, not their folder - it needs to know where
  to look: the project folder, and `[modules] paths` (MOD.005)
- `internal` moves from "my namespace" to "my module"; `namespace` goes (or becomes Part 2 C)
- `--interface`, the examples with modules (`examples/shop/`, `examples/wordcount/`) and their tests
- A file with no `module` line: the main program, or a module named after its folder (= C)

Claude's reading: B + B - it matches "a line in the file", `Fusion.IO` as one unit, and one DLL per module.

---

None open. Q.013 (modules and namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES
Task 57. Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Next question: Q.014.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
