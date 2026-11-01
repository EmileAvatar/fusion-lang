# Programming Languages: Pain Points

Why 30 well-known languages were created, and what each kind of program (an OS, a game, an
Android app, ...) needs from a language. It helps decide what Fusion should take on, and when.

**Fusion's order of work:** first a working language with some features, not all of them;
then more features, one at a time. The "planned" items below are for later. None of them is
a reason to stop the working-language work.

Status in this file is as of 2026-11-01. The live status is in `FEATURES.md` and `Decisions.md`.

---

## 1. The pain points

Most languages were made by someone fed up with what they had. Ordered by year:

| # | Language (year) | The pain point that started it |
|---|---|---|
| 1 | **Fortran** (1957) | Programs were written in assembly, and programmer time cost more than machine time. John Backus (IBM) wanted scientists to write formulas, not machine instructions, without losing speed |
| 2 | **Lisp** (1958) | Fortran was poor at lists, symbols and recursion, which AI research needed. John McCarthy made a language where code and data have the same form, so programs can build and change programs (macros) |
| 3 | **COBOL** (1959) | Every computer maker had its own language, so business programs couldn't move between machines, and managers couldn't read them. COBOL used English-like wording and was portable (Grace Hopper's influence) |
| 4 | **BASIC** (1964) | Programming was only for scientists, using punched cards and long waits. Kemeny and Kurtz (Dartmouth) wanted every student to program, interactively, on time-shared terminals |
| 5 | **Pascal** (1970) | ALGOL 68 had grown too big. Niklaus Wirth wanted a small, strict language to teach structured programming; it later grew into Delphi |
| 6 | **C** (1972) | Unix was written in assembly, so it was stuck on one machine, and B had no types. Dennis Ritchie wanted something close to the hardware but portable, so an operating system could be written once |
| 7 | **Smalltalk** (1972) | Computers were for specialists. Alan Kay (Xerox PARC) wanted computing anyone could shape: everything an object, objects sending messages, a live environment you change while it runs |
| 8 | **SQL** (1974) | Getting data out meant writing programs that walked through the records step by step. Building on Codd's relational model, Chamberlin and Boyce (IBM) made a language where you say *what* you want and the database works out *how* |
| 9 | **Ada** (1980) | The US Department of Defense had hundreds of languages in its systems, and their software was unreliable. Ada was made for large, long-lived, safety-critical embedded systems, with strong types and checks |
| 10 | **C++** (1985) | Bjarne Stroustrup found Simula's classes good for big programs but too slow, and C fast but poor at structure. He wanted C's speed with classes ("C with Classes") |
| 11 | **Erlang** (1986) | Ericsson's telephone exchanges had to stay up for years: millions of calls at once, no stopping for an upgrade. Joe Armstrong's answer: lightweight processes, messages instead of shared memory, "let it crash" with supervisors, and code swapped while running |
| 12 | **Perl** (1987) | Shell, sed and awk were too limited for reports and text processing, and C was too much work. Larry Wall made a "glue" language for text ("there's more than one way to do it") |
| 13 | **Haskell** (1990) | In the 1980s there were many small lazy functional languages, and the best one (Miranda) was proprietary. A committee made one open, shared language for research and teaching: pure functions, laziness, strong type inference |
| 14 | **Python** (1991) | Guido van Rossum found C too much work for small jobs and shell scripts too weak. ABC was readable but closed and inflexible. He wanted readable code you write quickly |
| 15 | **Lua** (1993) | At PUC-Rio in Brazil, trade barriers made foreign software hard to get, and Petrobras projects needed a configuration and scripting language. Lua is tiny and easy to embed in C programs; it later spread through games |
| 16 | **R** (1993) | The statistics language S was commercial (S-PLUS). Ihaka and Gentleman (Auckland) made a free one for statisticians |
| 17 | **Java** (1995) | C++ was complex and crashed from memory bugs, and a program had to be rebuilt for each platform. Java offered "write once, run anywhere" (the JVM) and garbage collection, so there was no manual freeing |
| 18 | **JavaScript** (1995) | Web pages were static. Netscape needed scripting inside the browser, fast; Brendan Eich wrote the first version in about 10 days, and many of its oddities date from then |
| 19 | **PHP** (1995) | Building dynamic web pages with CGI in C or Perl was tedious. Rasmus Lerdorf's tools for his "Personal Home Page" grew into a language |
| 20 | **Ruby** (1995) | Yukihiro Matsumoto wanted a scripting language more object-oriented than Python and more pleasant than Perl, designed for "programmer happiness" |
| 21 | **C#** (2000) | Microsoft's own Java (J++) ended in a lawsuit with Sun, and Windows development (COM, C++) was painful. Anders Hejlsberg designed a modern, managed language for .NET |
| 22 | **Scala** (2004) | Java couldn't mix object-oriented and functional programming. Martin Odersky combined them on the JVM; it later influenced Kotlin |
| 23 | **Clojure** (2007) | Concurrency with shared, changing state is hard to get right. Rich Hickey made a Lisp for the JVM where data is immutable by default (persistent data structures), and change is managed explicitly |
| 24 | **Go** (2009) | At Google, large C++ builds took very long, the language had grown huge, and concurrency was hard. Go is simple, compiles fast, and has goroutines and channels built in |
| 25 | **Rust** (2010, 1.0 in 2015) | About 70% of serious security bugs in C/C++ code (Microsoft's and Google's figures) are memory bugs, and garbage collection costs speed and control. Rust gets memory safety without GC through ownership and borrowing, checked when compiling |
| 26 | **Kotlin** (2011, 1.0 in 2016) | Java was verbose and null pointer exceptions were common ("the billion-dollar mistake"). Scala compiled slowly. JetBrains wanted null safety and short syntax that still works with Java |
| 27 | **Elixir** (2012) | Erlang's virtual machine was excellent at concurrency and staying up, but its syntax and tools put people off, and Ruby was weak at concurrency. José Valim brought a friendly syntax, macros and good tools to the Erlang VM |
| 28 | **Julia** (2012) | The "two-language problem": scientists prototyped in Python, R or MATLAB, then rewrote the slow parts in C or Fortran. Julia aims to be as easy as the first and as fast as the second |
| 29 | **TypeScript** (2012) | Large JavaScript codebases broke because nothing checked types; mistakes only appeared while running. It adds types that are checked and then removed |
| 30 | **Swift** (2014) | Objective-C was old, unsafe and odd to read, which put new Apple developers off. Chris Lattner designed a safe, modern replacement |

Also worth knowing:
- **Prolog** (1972): logic programming; you state facts and rules, and the system searches for answers.
- **Objective-C** (1984): Smalltalk's messages added to C.
- **Dart** (2011): Google's answer to JavaScript, now the language of Flutter apps.
- **Zig** (2016): a C replacement with no hidden control flow and no preprocessor; code that runs at compile time (`comptime`).
- **Nim** and **OCaml**: speed with a light syntax, and ML-style types.

### What keeps recurring, and how Fusion answers it

| Pain point | Languages that chased it | Fusion's answer |
|---|---|---|
| Speed vs. safety | C → Java → Rust | OWNERSHIP by default; GC and MANUAL only as project options (`Object_Lifetime.md`, Task 48) |
| Portability | COBOL, C, Java | Compiles to C now; LLVM and other targets later (Task 40) |
| Too complex, too big | ALGOL 68 → Pascal, C++ → Go, Kotlin | Concise syntax, familiar defaults; a simple working language first |
| Programming for everyone | BASIC, Smalltalk, Python | Readable syntax; clear error messages that say what to do |
| Null crashes | Kotlin, Swift | Nullable values as a setting, `?.` / `??`, a NullError that `catch` handles (`Nullable_Values.md`) |
| Concurrency is hard | Erlang, Clojure, Go, Elixir, Rust | Services instead of locks; one writer; no data races by construction (Task 42, `Concurrency.md`) |
| Staying up, failing safely | Erlang, Elixir, Ada | Errors that `catch` handles; supervisors and restarts not designed yet |
| No type checking at scale | TypeScript, Ada | Static types from the start |
| The two-language problem | Julia, Python + C | Native speed with high-level syntax (a C backend) |
| Code that writes code | Lisp, Clojure, Elixir, Zig | Templates (Task 29.3); macros and compile-time code not designed yet |
| Small and embeddable | Lua | The `[stdlib] layer` (`core` = no heap); embedding in other programs not designed yet |
| Tedious glue and text work | Perl, PHP, Ruby | A rich string library (`files/Builtins.md`) |
| One language can't fit every job | every language on this list | Fusion's core idea: rules switched per project in `fusion.toml` (GOL.001) |

---

## 2. Domain by domain

**The idea:** in most languages the rules are fixed. Java always has GC, and Rust always has
its borrow checker. Where a language does differ by domain, it is done with outside tools or
a separate dialect, such as Rust's `#![no_std]`, Embedded C++ subsets, MISRA C guidelines or
Kotlin/Native. Fusion is meant to be one language whose **rules switch per project** in
`fusion.toml`, with the same syntax everywhere (Decisions.md GOL.001).

**What can be switched today:**
- `[stdlib] layer`: `std` (everything), `alloc` (no OS: no print, no files) or `core` (no heap). That is the start of OS and embedded support.
- `[safety] mode`: safe, strict or unsafe.
- `[numbers] overflowWrap`, nullable strings, and the `[interfaces]`, `[collections]` and `[structs]` rules.
- `[source]`: Unicode names and `caseSensitive`.
- `[backend] target = "c"`; other targets come with Task 40.

| Domain | What it needs | How it's done elsewhere | Fusion now | Fusion planned / missing |
|---|---|---|---|---|
| **Operating system / kernel** | No runtime or heap at boot, exact memory layout, interrupts, inline assembly | C, Rust `no_std`, Zig | `layer = "core"` (no heap); C output links with anything | Inline assembly, `extern` calls, fixed struct layout, no hidden allocations: not built |
| **Embedded / hardware** | Tiny binaries, registers, no OS, real-time limits | C, MISRA C, Ada | `core` layer, fixed arrays, GCC cross-compilers via C | HIDL hardware descriptions (Task 41); `[build] optimize = "size"` (designed) |
| **GPU (CUDA / shaders)** | Code that runs across thousands of threads, its own memory spaces, a different compiler | CUDA C++, GLSL / HLSL, OpenCL, Metal | Nothing | A backend that generates GPU code (after LLVM, Task 40); not designed. Settings alone can't provide it |
| **High performance / HPC** | Zero-cost abstractions, SIMD, many cores, no GC pauses | C++, Fortran, Julia, Rust | Optimised C output, no GC by default, ownership | Services and threads (Task 42); hot-path services (designed); SIMD not designed |
| **Enterprise software** | Large teams, interfaces, modules, stable APIs, readability | Java, C#, Kotlin | Classes, interfaces, inheritance, namespaces, visibility, `Collection` (Task 32 done) | Generics of your own (Task 33), library trust and isolation (Task 39), core modules (Task 43) |
| **Database engines** | Control over memory and disk, concurrency, crash safety | C, C++, Rust | Ownership and C output | Files, concurrency (Task 42), memory model options (Task 38) |
| **Database use (queries)** | Talking to a database safely: queries, no SQL injection | SQL + JDBC / ORMs, C# LINQ | Nothing | A database module (fits Task 43); LINQ-style queries over a `Collection` would be possible |
| **Graphics / games** | Frame-time limits (no GC pauses), plain data structs, maths, calls into C libraries, scripting | C++, C#, Rust; Lua for scripting | Value structs, no GC; C output can call C libraries in principle | `extern` calls to C libraries, SIMD maths, bindings for SDL / Vulkan / OpenGL |
| **Android apps** | The Java/Kotlin framework, JNI, the NDK, ARM builds | Kotlin, Java, C++ via the NDK; Dart (Flutter) | C output can be built with the NDK for native parts | Full apps need JVM interop or a Kotlin bridge; an Android platform target isn't designed (only windows-x64, linux-x64 and wasm are) |
| **iOS apps** | Apple's frameworks | Swift, Objective-C | C output only | Bindings to Apple's frameworks |
| **Desktop GUI** | An event loop, callbacks, widgets, platform APIs | C#, C++/Qt, Swift, Delphi (Pascal), JS/Electron | Lambdas exist | A GUI library or bindings (Qt, GTK, Win32); none planned yet |
| **Web backend / APIs** | Many connections, async, JSON, HTTP | Go, Java, C#, Elixir, Node.js, Python, PHP, Ruby | Strings and Maps | Services (Task 42) are aimed at this (a million requests on one machine); an HTTP / JSON module (Task 43) |
| **Web front end** | Running in the browser | JavaScript / TypeScript, wasm | Nothing | `wasm` platform (designed) |
| **Telecom / always-on systems** | Staying up for years, many small processes, upgrades while running | Erlang, Elixir | Errors that `catch` handles | Services (Task 42); supervisors, restarts and code swapping not designed |
| **Scripting / data science / statistics** | Fast to write, a REPL, notebooks, many libraries | Python, R, Julia | Concise syntax | No interpreter or REPL; GC might suit this profile |
| **Text processing / glue** | Strings, regular expressions, files, quick scripts | Perl, Python, Ruby, shell | A rich string library | Regular expressions and file modules (Task 43) |
| **AI / symbolic / rules** | Lists and trees, pattern matching, code as data, logic search | Lisp, Clojure, Prolog, Haskell | `match` on enums with data | Macros and compile-time code: not designed |
| **Safety-critical (cars, aircraft, medical)** | Rules proven by tools, no undefined behaviour, certification | Ada / SPARK, MISRA C | `safety = "strict"`, bounds checks, no silent changes | Formal proofs and certification: far off |
| **Systems tools / CLIs** | Fast start-up, one file, easy to ship | Go, Rust, C | Works today: one native exe | Nothing major missing |
| **Teaching** | A small language, clear errors, quick results | BASIC, Pascal, Python, Scratch | Readable syntax, clear errors, three block styles | A REPL or playground would help |

---

## 3. Notes: to address later

These don't block the working language. They are recorded here so they aren't forgotten.

1. **Settings change the rules, not the platform.** Switching off the heap gets you a
   kernel-friendly language, but GPU or Android support needs a **backend** (the code
   generator) or **bindings** (a way to call the platform's libraries). Those are separate
   work, mostly after Task 40. For most domains the libraries matter more than the syntax.
2. **The dialect trap.** If every project switches settings differently, a library written
   for one project may not compile in another. This is the main risk of Fusion's approach;
   C++ "subsets" and the many Lisp dialects ran into it. Two common ways to manage it (an
   idea, not a decision yet):
   - **Profiles:** named bundles of settings, such as `profile = "kernel"`, `"embedded"`,
     `"game"`, `"enterprise"` or `"server"`. You write one line and get a safe, tested
     combination, and can still override single settings.
   - **Library declarations:** a library states which settings it needs, and the compiler
     checks that a project is compatible before using it (fits Task 39, library trust).
3. **Calling C (`extern`).** Most domains above (OS, games, GUI, databases, mobile) need
   Fusion to call existing C libraries. It is the single feature that opens the most doors.
4. **A gap in the plans:** there are no tasks yet for GPU code, mobile platforms, GUI,
   macros / compile-time code, supervisors and restarts, or a REPL. Each needs a decision:
   a setting, a fixed rule, a module, or not for Fusion.

**The order stays the same:** a working language first, with some features and not all of
them; then more, one at a time (`FutureFeaturesCaution.md`).
