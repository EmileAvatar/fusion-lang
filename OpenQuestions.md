# Fusion - Open Questions

Questions not decided yet, one line each: `Q.NNN` the question - where it belongs. Next to
`Decisions.md`: when the user answers one, the answer goes into `Decisions.md` (and the design
document named) and the line is removed here; a new question gets the next number (never
reused). Claude adds a question here instead of guessing (CLAUDE.md Rule 3b).

Ideas not scheduled yet keep their own open questions in `files/FutureFeatures.md`
("Open Questions" sections) until they become a task.

---

#### Language
Q.001 What may a function with a readonly result return - a member of the class, a new object? - decided while building (FEATURES 50.1, D.110)
Q.002 Does `--interface` show the readonly / keeps / lends result of private functions too, or public only (likely)? - FEATURES 48.4, files/Ownership.md 8
Q.003 The exact warning rules for `?.` and `??` (files/Nullable_Values.md section 5) - when Task 30.3 is built
Q.004 A method's `this` is always borrowed (D.103) - to review once working programs can verify it - Task 48
Q.005 Form D: its syntax - a set-up block on an abstract class or interface (FEATURES 52.1, CLS.016)

#### Concurrency
Q.006 How "undone where possible" (group service rule 7) works in detail - files/Service.md "Not decided yet", Task 42

#### Platforms and modules
Q.007 An RTOS (FreeRTOS, Zephyr) has threads and timers but usually no files or console - its own layer, or optional parts of the standard library? - FEATURES Task 41
Q.008 Language modules are code the compiler runs - how are they trusted and sandboxed, and is their name next to `fusionlib.Lang`? - FEATURES Task 49 / 39

#### Documentation
Q.009 YAML front matter (id, status, affects) at the top of each spec file - now with the split, or later? - FEATURES 51.5 (files/DocumentationSystemProposal.md 8)
Q.010 `Decisions.md` lines out of date: CLS.013 says abstract / sealed / override / protected are [DESIGN] - all but `virtual` are built; SYN.024 says `is` is [DESIGN] - it is built. Split them and mark the built parts [BUILT]?
Q.011 The Rust rules compared with Fusion - the user's review (Notes/Rust_rules.md)

#### Naming
Q.012 The language's final name - MaiaFusion is the candidate; decided once the self-hosted compiler works fully; "Maia" is already a verification language (maia-eda.net) - CLAUDE.md project notes
