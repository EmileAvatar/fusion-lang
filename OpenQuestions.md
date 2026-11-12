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

#### Q.013 What makes a file part of a module: its folder, or a line in the file? (user, 2026-11-12)

The user: "a module is not a separate module.fusion - it's just the line in the file that specifies
which namespace / module the file belongs to". Built today (MOD.001, Task 18.4, 32.2h): the **folder**
is the module, and an optional `namespace` line groups modules so they share internal names.

```fusion
// shop/cart.fusion - today: module `shop` because the file is in shop/
namespace Shop.Tools        // optional: shares internal names with other Shop.Tools modules

public class Cart
    ...
```

- **A** Keep it as built: the folder is the module; the `namespace` line is the line the user means
- **B** A `module Shop` line in the file decides its module, wherever the file is; folders only tidy
  files away - changes built behaviour (imports, `--interface`, the loader)
- **C** Both: the folder by default; a `module Shop` line, when written, overrides it

Claude's reading: A - the `namespace` line already does what was described.

---

Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Next question: Q.014.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
