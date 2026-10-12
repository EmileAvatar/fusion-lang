# Fusion - Working File (active task plans)

**What this file is (Task 22, 2026-10-09):** only the task being worked on now - its detailed
plan, the next action, and the latest session note. Keep it small: it is read often.
- Status of every task and feature: `FEATURES.md` (`[ ]` open, `[DONE]`, `[POSTPONED to ...]`)
- Finished tasks and sub-tasks, old sessions: `task/taskSummaryArchive.md` (verbatim)
- Not-started task write-ups: `task/taskBacklog.md` (verbatim)
- Rules (plan first, no emojis in code, ...): `CLAUDE.md`

---

## Current status (2026-10-11)

**Task 18 (core language foundation) is COMPLETE** and archived (plans, notes and the
FEATURES.md detail are in `task/taskSummaryArchive.md`). Task 10.2 is met.

---

## Current plan: the roadmap (FEATURES.md, renumbered 2026-10-11)

Done tasks keep their numbers; open tasks were renumbered from 25 into three phases (the
approved plan is archived). Phase 1 = 25 enums, 26 error handling, 27 semantic contract and
safety (bounds checks, the three-block-style check), 28 self-hosting test run.

---

## TASK 25: Enums and tagged unions - ACTIVE (plan approved 2026-10-12)

**Why now:** the self-hosting test run (Task 28) needs a clean way to say "this is one of
these" - token kinds, node kinds, a value that is a number *or* a word. Enums carry that; a
compiler written without them is a pile of int constants and string compares.

**Starting point:** `enum`, `Enum`, `match` and `case` are already reserved keywords. The
spec ("Enumerations") designs plain enums: three block styles + a one-line form, explicit
values (`OK = 200`), `Color.Red`, `match`, toInt, values(), fromString, and the user's note
"commas can be dropped regardless of preference as it's redundant". Nothing designs enums
with data - that part is new.

#### What it looks like (proposal - details depend on the questions below)
```text
enum Color: Red Green Blue                 // one line; commas optional

enum Status                                // indentation (braces and End enum work too)
    OK = 200
    NotFound = 404

enum Token                                 // enum with data (a tagged union)
    Number(int value)
    Word(string text)
    Plus
    End                                    // a variant without data

enum Expr                                  // recursive: an expression tree
    Num(int value)
    Add(Expr left, Expr right)

Color c = Color.Red
print(c)                                   // Red
print(c.toInt(), Status.NotFound.toInt())  // 0 404
for x in Color.values()                    // Red, Green, Blue

match t                                    // t is a Token
    case Number(n)
        print("number {n}")
    case Word(w)
        print("word {w}")
    case Plus, End
        print("symbol")
                                           // every case covered - no else needed

match ch                                   // on int / char / string: else required
    case '+', '-'
        print("operator")
    else
        print("other")

int function eval(Expr e)
    match e
        case Num(v)
            return v
        case Add(a, b)
            return eval(a) + eval(b)
```

#### Sub-tasks
- **25.2 Plain enums** - declaration in all three block styles + the one-line form, commas
  optional, explicit int values (default 0, 1, 2 ...; duplicates an error); `Color.Red`;
  == / != (only the same enum type - comparing with an int is an error, use toInt);
  print / `{c}` / toString give the name; toInt; `Color.values()` (a List); `fromString`
  (an unknown name stops the program with a clear error until Task 26 makes it
  catchable); as a variable, parameter, return value, struct field, array / List element
  and Map key; `public` + import across modules; `--interface` shows them. C: an int
  type + a names table
- **25.3 `match` statement** - on an enum: case names written bare (the type is known),
  every value must be covered unless there is an `else` (missing ones are named in the
  error); on int / char / string: constant cases, `else` required; several values per
  case (`case '+', '-'`); a duplicate case is an error; no fall-through; all three block
  styles; `break` / `continue` / `return` inside cases work as usual
- **25.4 Enums with data** - variants with named fields, built like a struct
  (`Token.Number(42)`, named arguments too); the data is read by `match` binding names
  by position (`case Number(n)`); value semantics like structs: copied deeply, freed
  automatically (strings, lists inside), == compares variant + fields, print shows
  `Number(42)`. C: a tag + a C union of per-variant structs, with copy / free / equality
  helpers
- **25.5 Recursive enums** - a variant may hold its own enum type (`Add(Expr left, Expr
  right)`) or a List of it: such fields are stored on the heap but still behave as
  values (a copy is a deep copy). What an expression tree / AST needs
- **25.6 Example + docs** - SYNTAX_REFERENCE.md section; a demo `examples/calculator2`
  (or similar): tokenize "2 + 3 * 4" into a List<Token>, parse into an Expr tree,
  evaluate - a small rehearsal of the self-hosted compiler; spec "Enumerations" updated
  (status line, data enums, match); fusion.ebnf
- Every part: tests (parser, checker, codegen, end-to-end under the leak check)

#### Not in this task (stay in the spec as design)
`next()` / `previous()`, `fromValue`, `.ordinal`, `match` as an expression (a value),
ranges in cases (`case 1..9`), guards (`case n if n > 0`), methods on enums (Task 32)

#### Decisions (user, 2026-10-12) - plan approved
1. Enums with data live inside `enum` (one concept)
2. `Color.Red` everywhere; bare names only in `match` cases
3. The fallback case is `else`
4. The data is read only through `match`

---

## TASK 22 (housekeeping) - ACTIVE (user: "do the housekeeping first and the ascii issue first")

Kept under Task 22 until the renumbering is approved.

- 22.8-22.11 DONE (tools; detail archived)
- 16.1 DONE - examples/control_flow
- 22.7a DONE - README reduced to goals + pointers
- 22.7b DONE - spec status lines (Task 22 complete)
- Each one: FEATURES.md line, `task/automation.md` row marked Automated, check, commit

---

## Working Notes

### Session 31 (2026-10-09 .. 10-11 - 18.3.5 to 18.5.7)
- Done: 18.3.5 equality, 18.3.5b bool printing, 18.3.6 string library (a-f, masking design
  and build), 18.3.7 type classes / methods, 18.3.8 bytes, 18.4 modules (1-4), 23.7 / 23.8
  (wait at exit, --headless, .fusion preview), Task 24 added (editor support), 18.5 (1-7)
- User preferences saved to memory: as little typing as possible; never change values
  silently
- Task 18 archived (FEATURES.md detail too); 3 automation candidates added
- 22.8-22.11 done: check.py --fix-ascii / --ship / --example, tools/patch.py
- 16.1 done: examples/control_flow; map literals noticed missing (FEATURES.md Later)
- 22.7a done: README is goals + pointers (554 -> 321 lines); 22.7b waits for the renumbering
- User answered: numbers from 25, classes / generics in Phase 2. ChatGPT review read:
  fixed arrays are not bounds-checked (segfault) -> new Task 27 "semantic contract and safety"
- FEATURES.md reorganized into phases and renumbered (22.12); the user asked for 27.1
  (bounds checks for fixed arrays) and 27.4 (one app in 3 block styles -> identical C)
- 2026-10-12: 22.7b done - a status line under each of the spec's 31 major sections; Task 22
  complete
- Task 25 plan approved (all 4 recommended answers)
- **Next Action:** 25.2 plain enums
