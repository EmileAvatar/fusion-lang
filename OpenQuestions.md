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

**Deferred until built (user, 2026-11-21 - D.161):** an open question is settled when its section is
actually being built, not ahead. Until then Fusion plans a simple implementation by default, which a
project can change by settings - in `fusion.toml` or on the object. A question waiting for its section
says **Deferred** and the task it waits for.

Ideas not scheduled yet keep their own open questions in `files/FutureFeatures.md`
("Open Questions" sections) until they become a task.

---

## Open

#### Q.038 A resource split into parts - reads, giving back, who splits (Task 42.31, files/Concurrency.md 3.14)
The database example: T1 writes users, T2 accounts; request R writes both, so T3 takes them over as a group.
```fusion
service Database db = Database.open("connection string")
string n = db.query("SELECT name FROM users WHERE id = 1")   // while T1 is writing users:
// A: waits for the write in progress   B: reads a snapshot - the last finished state   C: a setting, default B

// T3 has finished R and its queue is empty:
// D: users and accounts go back to T1 / T2 at once
// E: T3 keeps them until an idle time passes, then gives them back
// F: T3 becomes their writer from now on

// who decides the parts:
// G: the service only, by load (AUTO)   H: the developer names them   I: both - AUTO, or named by the developer
service(db).Parts = ["users", "accounts"]    // H / I: a possible form, the name to decide
```
Suggested: B (PostgreSQL and most databases let readers see a snapshot and never wait), E (no handing back and forth), I.

**Answer (user, 2026-11-21):** B for now - configurable in the database's settings; the Database library brings a
simple implementation for everyday use, built with it (Decisions.md D.160). **Deferred** (D.161): D / E / F and
G / H / I - decided when 42.31 and the Database library are built.

#### Q.039 A keyword used as a name in translated code (Task 49 - **Deferred** until Task 49, D.161)
A `Lang.<language>.Fusion` module reads its language with that language's own keywords (D.162). Once the code
becomes Fusion, a name like `type`, `service` or `match` clashes with Fusion's keywords and reserved words.
```fusion
// Java: String type = "x";   service.start();
string @type = "x"           // A: an escape mark, as C# @class
string r#type = "x"          // B: as Rust r#type
string type_ = "x"           // C: the module renames it (type_), and keeps a map of the old names
```
Suggested: C for code the module translates, A for a developer who needs one by hand.

Earlier: Q.031 (a jagged array's rows, columns and walking) answered 2026-11-21: Decisions.md D.163, D.148 (a third walk order).
Earlier: Q.034-Q.037 (script libraries) answered 2026-11-17: Decisions.md D.155-D.157; Q.037 (which Lua) deferred to FEATURES Research R5.
Earlier: Q.030, Q.032, Q.033 (jagged arrays, 3 dimensions and the stack) answered 2026-11-16: Decisions.md D.144, D.153, D.154.
Earlier: Q.028 (toCSV on arrays) and Q.029 (toList and null slots) answered 2026-11-16: Decisions.md D.151, D.152, FEATURES 45.11b / 45.11c, Notes/CSV_many_dimensions.md.
Earlier: Q.021-Q.027 (arrays of 3 dimensions, bare enum values) answered 2026-11-15:
Decisions.md D.141, D.143, D.148-D.150, FEATURES 45.12, 45.3b, 45.16, 45.17. Q.013 (modules and
namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES Task 57. Q.014 (a may-be-null
parameter mark) answered 2026-11-14: no mark - every object may be null (D.138, D.117). Q.001-Q.012
answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status PARTIAL; FEATURES
48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the name). Q.015-Q.020
(arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.040.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
