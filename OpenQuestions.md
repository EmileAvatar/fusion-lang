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

#### Q.042 A generic class's types from the variable it is stored in (Task 33.4 - found by the interaction test)
`Garage<Car> g = Garage()` - no argument says what T is. Today it is an error that names the fix; should the
declared type supply T?

```fusion
class Garage<T>
    List<T> items
    constructor()
        items = []

Garage<Car> g = Garage<Car>()   // today: T written twice - works
Garage<Car> g = Garage()        // today: error "T can't be worked out ... write the types: Garage<Car>(...)"
// A: keep it - the types come from the arguments or are written (D.166 as it is)
// B: the declared type supplies them when the arguments can't (Java new ArrayList<>(), C# new(), Rust's let);
//    only where a type is written on the left - var / let g = Garage() stays an error
```

Suggested: B - the familiar form, nothing guessed (the type is written once, on the left).

#### Q.043 A local taken from a parameter: `Car x = item` inside a function (Task 33.4 / Task 48 - Ownership.md)
Under strict ownership, a function that keeps a parameter takes it (D.100: returned or stored). A local
that is only an alias of the parameter is not a "keep" today - the function borrows `item`, `x` is a second
name for it, and `item` stays usable after. The same in a plain function and a generic one.

```fusion
string function nameOf(Car item)
    Car x = item          // today: x borrows item; nothing moves; nameOf borrows its argument
    x.name = "taxi"
    return item.name      // today: allowed - "taxi"
// A: keep it - a local from a parameter is a borrow (the caller's car stays the caller's)
// B: a move inside the function - item.name after it an error "'item' was moved to 'x'" (as for a local
//    Car b = a), and nameOf then keeps its parameter (the caller's car moves)
// C: as A, and an error to change it through x (a borrowed parameter is readonly through a second name)
```

Suggested: A - passing lends (the README's "passing lends it"); a local name for it is part of that loan.

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
(arrays) answered 2026-11-14/15: D.141-D.147. Next question: Q.044.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
