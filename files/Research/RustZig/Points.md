# Rust and Zig - the points for Fusion (Claude, 2026-11-17)

To discuss with the user - nothing here is decided. One line per point: what the source says,
where Fusion stands today, and a suggestion (**have**, **take**, **discuss**, **skip**).
Listed in FEATURES "Research" R4; gone through with the user in FEATURES Task 59 (before self-hosting).

Sources (in this folder):
- [WhyYoutuberdontlikeRust.md](WhyYoutuberdontlikeRust.md) - "Why I Don't Like Rust" (YouTube): a C# / Zig programmer on Rust's style
- [whyZig.md](whyZig.md) - "Why Zig over Rust, C, C++, Odin, Nim" (YouTube)
- [ZigRustCompare.md](ZigRustCompare.md) - ChatGPT: Zig and Rust against C, C++, VB.NET, Java, Python, and what Fusion could study
- [RustPitfalls.md](RustPitfalls.md) - "I Spent 18 Months Using Rust And Regret It" (YouTube): a trading platform rewritten in Rust, reviewed - section 6

---

#### 1. From "Why I Don't Like Rust" - the issues
His point: not safety or the borrow checker - Rust forces one style on him.
- **R1 Forced style (iterators, not index loops)** - Fusion: `for`, `while` and `foreach` all work; no style forced (SYN.005). **Have**
- **R2 Hidden generated code (`derive` just to print or compare an enum)** - Fusion: an enum prints its name and compares without anything written (TYP.012); a class prints through `ToString` (CLS.015). **Have** - keep it a rule: basic abilities never need generated code
- **R3 Inferred types forced; some types can't be written at all** - Fusion: types are written; `let` / `var` optional (SYN.008).
  **The user (2026-11-17):** Fusion has two ways to make a variable - the usual `<type> name = value` (`int count = 5`),
  and `let` / `var`, which take the type from the value: `let` is set once and never changes, `var` may change.
  Strong static typing where possible, with the developer free to choose how they write it. (The names `let` / `var` may change.) **Take as a rule:** every value's type can be written by the programmer - nothing the compiler names that the programmer can't. **Discuss:** a strict-mode setting that requires written types
- **R4 "Enums" that are really tagged unions** - Fusion: TYP.004 does the same - `enum` covers plain values and values with data. **Discuss:** keep one keyword, or a plain `enum` (numbers only) and a separate name (`union` / `choice`) for one with data
- **R5 Results inside results, `match` everywhere** - Fusion: `T, Error function`, `try` / `catch`, `?.` - the developer picks (FUN.001, FUN.002, FUN.009). **Have**
- **R6 Long call chains, hard to read and debug** - Fusion: no lazy iterator chains yet. **Discuss:** a warning above N chained calls (a setting), or a debugger that shows each step's value
- **R7 Hundreds of features before you can start (string types, heap, globals, unsafe)** - Fusion: one `string`, simple start, advanced parts are settings; R2.4 (the learning curve). **Have** - watch the keyword count
- **R8 A large constant array overflowed the stack in debug, not in release** - Fusion: a plain array above `stackLimit` is a compile error (D.145). **Take:** a `const` array lives in static memory, never on the stack, and debug and release behave the same - add a test to Task 45
- **R9 Methods on a struct 40% faster than free functions** - Fusion: a method is the same C function (SYN.011), so no difference should exist. **Have** - confirm in the benchmark (R2.1)
- **R10 Slow compiles from generated code** - Fusion: watch the compiler's speed (R2.5). **Have**
- **R11 Traits / interfaces pointless (his opinion)** - Fusion programs to interfaces (CLAUDE.md). **Skip**
- **The whole rant, for later (user, 2026-11-17):** a guide to what puts people off learning a language - used for the
  beginner and professional courses and an AI skill.md after self-hosting and 1.0 (FEATURES L15.2)

#### 2. From "Why Zig" - what it gets right
- **Z1 Explicit: no hidden allocations, conversions or control flow** - Fusion: conversions only when exact (TYP.009); allocations for strings and Lists are hidden. **Discuss:** a way to see them - a compiler report of where memory is allocated, or a warning setting for hot code
- **Z2 Errors as values, no exceptions** - Fusion has both, each a setting (FUN.009). **Have**
- **Z3 Use C libraries directly** - Fusion: `extern "C"` designed (FUN.011). **Have (planned)**
- **Z4 One tool: compiler, build, formatter, packages, cross-compiling** - Fusion: one tool after Python (SET.012), formatter (SET.023). **Take:** cross-compiling (build for Windows on a Mac) is in no task yet - with SET.020 `[backend] platform`
- **Z5 Allocators passed in, swappable and testable** - Fusion: arenas designed (MEM.009); ownership frees by itself. **Discuss** with item C1
- **Z6 No hidden runtime** - Fusion: a small C runtime header. **Have**
- **Z7 `comptime` - run normal code while compiling** - see section 4
- **Z8 Build modes debug / safe / fast / small** - Fusion: `[safety] mode` and `[build] mode` / optimize (SET.002, SET.020). **Have (designed)** - note Zig's "safe": checks kept in a fast build; Fusion keeps them unless unsafe
- **Z9 Disliked a Python-style syntax switch** - Fusion: three block styles, one meaning (SYN.001). **Have**
- **Z10 Templates and overload rules too complex** - Fusion: operator overloading off (TYP.008), overloading designed (SYN.025). **Have** - keep overload rules simple

#### 3. From the ChatGPT comparison
- **C1 One allocator per service: everything the service made is freed with it (an arena)** - Fusion: services own their state (Service.md), arenas designed (MEM.009). **Discuss** for Task 42 - a fast, simple free when a service or a request ends
- **C2 `defer` - clean-up written next to the set-up** - Fusion: `finally`; ownership frees memory by itself. **Discuss:** `defer` for things that aren't memory (a file, a lock, a log line)
- **C3 Interfaces with default methods** - Fusion: built (CLS.006). **Have**
- **C4 Services as an actor-style model** - Fusion: already compared (42.30). **Have**
- **C5 Combine Rust's compile-time safety with Zig's explicit resources** - Fusion's goal already (README). **Have**
- **C6 Reflection / making types while compiling** - see section 4

#### 4. `comptime` - would it help Fusion? (the user's question)
What it is: Zig runs ordinary Zig code while compiling; the results become constants or even new types.
- **Useful:** tables computed once while compiling - lookup tables, CRC, chess moves (R8); the program starts with them ready
- **Useful:** checks while compiling - `assert` on constants, a setting's value, a size
- **Not needed:** generics - Fusion plans normal generics (Task 33); Zig uses `comptime` for them because it has none
- **Risky:** making types or code while compiling - "hidden magic" (R2), hard to read and debug
- **Security:** code run while compiling runs on the developer's machine - "never trust code": no files, no network, a step limit
- **Cost:** the compiler needs a way to run Fusion code - an interpreter; the same engine could serve script mode (Task 58.2)
- **Suggested:** after self-hosting, a `[compile] comptime` setting, default off: only functions with no side effects, their results become constants; no making types at first

#### 5. Running Fusion as a script, and running other Fusion code while running (the user's idea)
- Script mode is Task 58 (`fusion run tidy.fusion`)
- Running other Fusion code from a running program: today `run` starts another program (FUN.006); an engine inside the program (plugins, `eval`, hot reload - SET.023) is new
- **Discuss:** the same interpreter as section 4; loaded code is untrusted - its own limits (Task 39, library trust)

#### 6. From "I Spent 18 Months Using Rust And Regret It" - pitfalls Fusion must not fall into (user, 2026-11-21)
A developer rewrote a whole trading platform from TypeScript to Rust and regretted it; a reviewer (ThePrimeagen) agrees
in part ("a skill issue - but a real one"). The lesson for Fusion: the pitfalls below, and why a rewrite is the wrong path.
- **P1 Async, traits and lifetimes together make types no one can read** - `Pin<Box<dyn Future<Output = R> + Send + '_>>`,
  `where` clauses that take 90 minutes. Fusion: no lifetimes; async designed (D.127, proposed). **Take as a rule:** an async
  function's type stays simple (`Future<string>`), and whether it may cross threads is the compiler's job (ownership, services)
- **P2 A helper over async calls couldn't be written, so the code was copied instead** - a `retry(operation, 3)` helper.
  **Take as a test:** generics (Task 33) and async must combine - a retry helper over any async call must compile, plainly written
- **P3 "Wrong duplication is better than the wrong abstraction"** - copying is easy to fix later, a bad abstraction isn't. **Note** for the courses (L15.2)
- **P4 `?` makes passing an error up so easy that no one adds context** - it surfaces ten calls higher with no hint of where.
  Fusion: `?` designed (FUN.010), a stack trace on every error designed (FUN.013). **Take:** the trace on by default, `?` records
  where it passed; a short way to add context (e.g. `? "reading the config"`) - to design
- **P5 Stack traces off by default** (`RUST_BACKTRACE=1` to see them). **Take:** on by default in debug builds
- **P6 Asserts and simulations before real money** - Fusion: `assert` designed (SYN.023). **Have (designed)**
- **P7 "The pit of success"** - the right way must be the easiest way; in Rust the easy `?` and `clone` lead the wrong way.
  **Take as a design rule** for every Fusion feature (with GOL.007)
- **P8 The learning curve is three cliffs** - the borrow checker, then lifetimes, then async. Fusion: no lifetimes; `strict` /
  `relaxed` ownership (MEM.013). **Have** - watch async so it doesn't become the third cliff
- **P9 `Arc<Mutex>` and `clone` everywhere to get past the checker - and the speed is lost**. Fusion: a service instead of a
  lock (Task 42); `byVal` copies say so. **Have (designed)**
- **P10 An unkind community** ("skill issue", "use Postgres instead") drives beginners away. **Note** for L15.2: docs, errors
  and the community kind to beginners - every error says how to fix it (L2.1)
- **P11 Go's channel traps** (send to a nil channel blocks forever, a closed one returns zero) vs Rust's Option.
  Fusion: Concurrency.md trap 10. **Have**
- **P12 Shadowing** - the same name given a new type (`let x = x.unwrap()`); the reviewer came to like it. Fusion: a name
  can't be reused in an inner block (Known limitations). **Discuss**
- **P13 `From` / `TryFrom`** - a type says how it is made from another, then `.into()` works everywhere; the reviewer's
  favourite. Fusion: conversions are functions (TYP.011). **Discuss** - a class declaring its own conversions
- **P14 Rewriting a working project in a new language** - 18 months, and regret. **The user's answer (2026-11-21):** this is why
  `Lang.<language>.Fusion` exists (Task 49, D.158) - the compiler reads the existing code and translates it to Fusion, or
  better, compiles it as it is, without a rewrite
- **P15 Learn the language before rewriting in it** - allocation, async, pinning first. **Note** for L15.2
