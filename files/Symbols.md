[Main](../Main.md) | [Spec](spec/index.md) | [Decisions >](../Decisions.md) <!-- nav -->

# Fusion - the symbols and what each one does

**Why this file (user, 2026-11-17):** so Fusion uses its symbols consistently - one meaning per symbol wherever
possible - and doesn't scatter syntax around that confuses developers or makes the code hard to read. Each symbol:
what it means in Fusion, and what it means in other languages. Section 4 lists the symbols that have more than one
job in Fusion today - to review. To review with the user; nothing here is a new decision.

Contents:
- [1. The common symbols](#1-the-common-symbols)
- [2. More symbols](#2-more-symbols)
- [3. Why a chain of calls is hard to read - the Rust example](#3-why-a-chain-of-calls-is-hard-to-read---the-rust-example)
- [4. Symbols with more than one job - to review](#4-symbols-with-more-than-one-job---to-review)

---

## 1. The common symbols

#### `.` (dot) - reach inside something
"The thing on the right that belongs to the thing on the left": `person.name` (a field), `name.toUpper()` (a method),
`Fusion.Script.Lua` (a library inside a namespace).
- Other languages: the same almost everywhere (C#, Java, JavaScript, Python, Go, Rust, Zig). C and C++ also have
  `->` for "inside, through a pointer"; C++ and Rust use `::` for namespaces (`std::vector`)
- Fusion: the dot for all of them. `name.toUpper()` is also another way to write `String.toUpper(name)`, and your
  own functions work the same way (SYN.011)

#### `<>` - two different jobs
- **Generics:** `List<int>`, `Map<string, Person>` - "a List of what?". The type in the brackets is filled in when it
  is used, so one `List` design works for every type. C#, Java, C++, Rust, TypeScript and Fusion; Go and Python use
  `[ ]` instead (`list[int]`)
- **"Not equal"** in old Basic, VB.NET and SQL: `if a <> b`. Fusion accepts it as another way to write `!=` (SYN.029)
- The compiler tells them apart by where they appear: after a type name a generic, between two values "not equal"

#### `=` - assignment
`int count = 5` means "put 5 into count" - not a question.
- C, Java and JavaScript allow `if (x = 5)`, which quietly sets x to 5 instead of comparing - a famous source of bugs
- Fusion follows VB: **inside a condition `=` compares** (`if x = 2` is the same as `if x == 2`), so that bug can't happen

#### Comparisons
| Symbol | Means | Notes |
|---|---|---|
| `==` | equal | in Fusion `2 == "2"` is true - it compares values across a few types |
| `!=` / `<>` | not equal | `<>` is the Basic / SQL spelling |
| `===` | equal **and** the same type | from JavaScript and PHP; in Fusion `2 === "2"` is false |
| `!==` | not equal, or another type | |
| `<` `>` `<=` `>=` | less / greater / or equal | the same in every language |

#### `:` (colon) - "here comes the part that goes with this"
Its job changes with the place, but it always joins a thing to its detail.

In Fusion:
- a one-line body: `int function double(int x) : x * 2`
- a lambda: `func(int x) : x * 2`
- a match case: `Red, Yellow : "stop"`
- the one-line if-else: `(x > 0) ? "yes" : "no"` - "if so, this, otherwise that"

Elsewhere:
- Python ends a block's first line with it: `if x > 5:`
- TypeScript, Rust, Go, Kotlin put the type after it: `count: int` - Fusion puts the type first (`int count`), as C and Java do
- JSON and JavaScript objects pair a key and a value: `{"name": "Ann"}`
- C#: "inherits from" - `class Car : Vehicle`

#### `;` (semicolon) - the end of a statement
C, C++, Java, C#, JavaScript and Rust need it, because to them a line break means nothing. Python, Go (mostly), VB
and Fusion use the line break instead. Fusion accepts a `;` so pasted code still works (SYN.037).

#### `=>` and `->` (arrows) - "goes to" / "gives back"
- `=>` in C# and JavaScript makes a lambda: `x => x * 2` - "x goes to x times 2"; Scala uses it in match cases
- `->` in Rust, Python and Swift gives the return type: `fn add(a: i32) -> i32`; in C and C++ it is "inside, through a pointer" (`p->name`)
- **Fusion has no arrows today:** it uses `:` where others use `=>` (`func(int x) : x * 2`), and the return type goes in
  front (`int function add(...)`)

---

## 2. More symbols

| Symbol | Means | In Fusion |
|---|---|---|
| `?.` | a member only if the thing isn't null (`person?.name`) | built |
| `??` | "or this, if null" (`name ?? "nobody"`) | designed |
| `? :` | if-else in one line | built |
| `( )` | a call `f(x)`, grouping `(a + b) * c`, a cast `(int)d` | built |
| `[ ]` | an array or an index: `[1, 2, 3]`, `a[0]` | built |
| `{ }` | a block (C style); a value inside a string `"{name}"` | one of the three block styles; string interpolation |
| `+=` `-=` `*=` `/=` | change in place (`count += 1`) | built |
| `++` `--` | add / take away one | designed - a statement only, never inside an expression (SYN.020) |
| `&&` `\|\|` `!` | and, or, not | Fusion accepts both: `and`, `or`, `not` (SYN.039) and the C-style symbols |
| `%` | the remainder (`7 % 3` is 1) | built |
| `&` `\|` `^` `<<` `>>` | bit operations (hardware, flags) | designed (TYP.010, TYP.014) |
| `...` | a range `1...100`; "any number of" `int... numbers` | partly built (SYN.034) |
| `//` `/* */` | comments | built |
| `'a'` / `"a"` | one character / a string | built |
| `\` | an escape inside a string - `"\n"` is a new line | built |
| `_` | "I don't care about this one" in a match | built (SYN.017) |
| `@` | an annotation, extra information for the compiler (`@deprecated`) | designed (SYN.035) |
| `#` | C's preprocessor (`#include`); a region in VB | `#Region` designed (SYN.032) |
| `::` | a namespace path in C++ and Rust | not used - Fusion uses `.` |
| `**` | to the power of (`2 ** 3` is 8) | designed (SYN.035) |

---

## 3. Why a chain of calls is hard to read - the Rust example

From the "Why I Don't Like Rust" video ([Research/RustZig/Points.md](Research/RustZig/Points.md), R3 and R6). The job:
find every `.cpp` file in a folder.

```rust
let files = WalkDir::new(path)              // 1. a walker over the folder
    .into_iter()                            // 2. turn it into an iterator: something that hands out one entry at a time
    .filter_map(|e| e.ok())                 // 3. keep the entries that read without an error, unwrapped
    .filter(|e| e.path().extension() == Some("cpp"));   // 4. keep only the .cpp files
```

What makes it confusing:
- **Four steps on one statement** - each `.` works on what the step before it gave back, and none of those in-between
  results has a name or a visible type
- **`|e| ...` is a lambda** (Rust's spelling of `func(e) : ...`) - a small function written inside the call
- **Nothing has happened yet** - an iterator is lazy: no file is read until something loops over `files`
- **The type of `files` can't be written by the programmer** - the compiler calls it something like
  `Filter<FilterMap<IntoIter, {closure#1}>, {closure#2}>`, and the `{closure}` parts have no name you can type
- **`e.ok()`, `Some("cpp")`** - Rust's Result and Option types, which need their own rules to read

The same job written step by step, as the YouTuber preferred - every value named, every type visible:
```fusion
List<string> files = []
foreach (string name in listFiles(path))    // listFiles is a sketch - no such built-in yet
    if name.endsWith(".cpp")
        files.add(name)
```

For Fusion (Points.md R3, R6): every value's type can be written by the programmer; a chain is allowed but never
the only way, and a loop like the one above always works.

---

## 4. Symbols with more than one job - to review

Where Fusion gives one symbol several meanings today. Each one is fine only if the place makes the meaning obvious.

| Symbol | Its jobs in Fusion | Told apart by |
|---|---|---|
| `=` | assign; compare inside a condition | where it is: a statement or a condition |
| `<>` | generics; "not equal" | after a type name, or between two values |
| `:` | a one-line body; a lambda; a match case; `? :` | what comes before it |
| `{ }` | a block (C style); a value inside a string | inside quotes or not |
| `( )` | a call; grouping; a cast `(int)d` | what comes before or inside it |
| `...` | a range; "any number of"; spreading `[...a, ...b]` (designed) | where it is |
| `==` / `===` | two kinds of equal | the third `=` |
| `!=` / `<>` | two spellings of "not equal" | the same meaning - a choice of style |
| `and` / `&&`, `or` / `\|\|`, `not` / `!` | two spellings of one thing | the same meaning - a choice of style |

To decide later: whether any of these should lose a job, and which symbols Fusion should never take on
(e.g. `::` beside `.`, both `=>` and `:` for a lambda).

[Main](../Main.md) | [Spec](spec/index.md) | [Decisions >](../Decisions.md) <!-- nav -->
