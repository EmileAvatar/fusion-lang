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

#### Q.047 How `money` is written and printed (Task 47.2 - D.021)
`money` is a long of minor units (cents). How is an amount written in the code, and how does it print?

```fusion
// A: a decimal literal, its places checked against [money] decimals (2): stored as minor units
money price = 123.45            // stored 12345; 123.456 an error (more places than the minor unit)
print(price)                    // 123.45
// B: a suffix marks it - plain numbers stay int / double
money price = 123.45m
// C: minor units only - nothing new to read
money price = money(12345)      // 123.45
```

Suggested: A, with B accepted as quick typing (`123.45m` where the type isn't written, e.g. `var`).

**Answer** (user, 2026-11-23): A for now - until something better turns up in the research R10 (COBOL
and other languages; money is a special kind of decimal, handled accurately as COBOL does).
**Deferred** until R10 is done (FEATURES Research R10) - then settled with 47.2.

#### Q.048 The default rounding for money (Task 47.2.2)
Dividing, a percentage or a split can leave half a cent. Which way does it go by default (a project changes it in
`[money] rounding`)?

```fusion
money m = 0.05
print(m.percent(50))            // 0.025 -> ?
// A: halfEven (banker's): 0.02 - the default of C#'s Math.Round, Python's Decimal; no drift over many sums
// B: halfUp: 0.03 - what most people expect on paper
// C: no default - a project must set it
```

Suggested: A (`halfEven`), with `halfUp`, `down`, `up` as the other values.

**Answer** (user, 2026-11-23): A (halfEven) - checked against the research R10 first.
**Deferred** until R10 is done - then settled with 47.2.2.

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
(arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.051.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
