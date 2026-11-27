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

Earlier: Q.081 (A - structured = a module in a namespace), Q.082 (A - static added with a warning; who may be private) and Q.083 (A - `[libraries]`, and an import with a path) answered 2026-11-27: Decisions.md D.211-D.213.
Earlier: Q.075 (A - the namespace and module from the folder; what a module holds), Q.076 (A - the project's settings list its libraries, else a path), Q.077 (A - `internal` the namespace), Q.078 (A - `Fusion.Core` always imported), Q.079 (A - a duplicate an error until aliased) and Q.080 (A - `Fusion` reserved) answered 2026-11-27: Decisions.md D.204-D.210.
Earlier: Q.072 (B - FusionType's fields in camelCase), Q.073 (A - a CapacityError past `fixed(n)`) and Q.074 (B - a `fixed(n) string` checked now, inline later) answered 2026-11-27: Decisions.md D.201-D.203.
Earlier: Q.070 (an enum value written with its enum; `case OK` or `case Status.OK` in a match) and Q.071 (A - `[source] shadowing`, off by default) answered 2026-11-27: Decisions.md D.199, D.200.
Earlier: Q.067 (A - a digit on both sides of the point), Q.068 (m money and dec decimal suffixes) and Q.069 (B - an enum value alone anywhere, a shared name an error listing each) answered 2026-11-25: Decisions.md D.195-D.197, FEATURES 47.9, 47.10.
Earlier: Q.062-Q.066 (an enum as a built-in value struct: fields, ids, constructor, toString, capitals) answered 2026-11-25: Decisions.md D.188-D.194, files/Value_Structs.md.
Earlier: Q.058 (money 16 bytes - a 4-byte symbol), Q.059 (A - one money, a long), Q.060 (halfEven in fusion.toml; the
rules in the Currency module) and Q.061 (the symbol for display only) answered 2026-11-24: Decisions.md D.184-D.187.
Earlier: Q.053 (int128 / int256, signed), Q.054 (a fixed 3-character currency, never on the heap), Q.055 (B - the scale is how
many places the value holds), Q.056 (decimal first) and Q.057 (no currency by default) answered 2026-11-24: Decisions.md
D.179-D.183.
Earlier: Q.047 (A), Q.048 (A, plus an operation naming its mode and `[money] rounding = "exact"`) and Q.051 (A - the steps
in between wide) answered 2026-11-24: Decisions.md D.176-D.178. Q.052 (rates) answered by the redesign: money a struct,
a rate a decimal (files/taskSummary2.md Task 47, Q.056).
Earlier: Q.049 (Task 47's other parts - A: they stay in Task 47, after the number types) and Q.050 (36.0 first -
A: a simple VS Code / Sublime highlighter before Task 47) answered 2026-11-23: FEATURES Task 47 and 36.0 - task
order, not language features, so no Decisions.md row.
Earlier: Q.044 (statics on a generic class - C), Q.045 (a List implementation's core - B for now), Q.046 (a List value holding any implementation - A for now) answered 2026-11-22: Decisions.md D.173-D.175.
Earlier: Q.042 (a generic's types from the variable) and Q.043 (a local taken from a parameter: B1, for now) answered 2026-11-22: Decisions.md D.171, D.172.
Earlier: Q.041 (ranges: the step, `%`, a step that misses the end) answered 2026-11-22: Decisions.md D.170, FEATURES 33.2g, 47.6, L7.9.
Earlier: Q.038 (a resource split into parts), Q.039 (a keyword as a name in translated code), Q.040 (RECT storage) answered 2026-11-21: Decisions.md D.160, D.165, D.164; the rest of Q.038 revisited when Task 42.31 starts (D.161).
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
(arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.084.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
