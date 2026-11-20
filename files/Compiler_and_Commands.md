[Main](../Main.md) | [Spec](spec/index.md) | [Decisions >](../Decisions.md) <!-- nav -->

# Fusion - the compiler, its commands, and the apps around it (a draft map)

A draft, 2026-11-20 (user's request): every job a compiler and its tools do, taken from the languages in
[Programming Languages Pain points.md](<Programming Languages Pain points.md>), so we can plan what Fusion
needs to add. Nothing here is decided; each item is marked:
- **have** - works today
- **planned** - in a task or a decision (the reference is given)
- **idea** - not scheduled; to decide later (a setting, a fixed rule, or dropped)

Contents:
- [1. What we are trying to achieve](#1-what-we-are-trying-to-achieve)
- [2. The languages and what Fusion can take from them](#2-the-languages-and-what-fusion-can-take-from-them)
- [3. What the compiler must support](#3-what-the-compiler-must-support)
- [4. The commands - one app: `console`](#4-the-commands---one-app-console)
- [5. The IDE, and the other apps](#5-the-ide-and-the-other-apps)

---

## 1. What we are trying to achieve

- **One tool, not a pile of them.** Most languages need several separate tools - a compiler, a build system (make,
  CMake, Gradle), a package manager (npm, pip), a formatter, a linter, a test runner, a version manager. Go, Rust
  (cargo), .NET (`dotnet`) and Zig show that one tool for all of it is far easier. Fusion's is called `console`
  (FEATURES L2.3, SET.012) - one app for every command in section 4
- **The compiler is a library first, the commands sit on top.** The same compiler serves the command line, the IDE,
  a REPL, script mode and the script libraries (Task 60.8 `Fusion.Compiler`, Research R7.5)
- **Safe by default, every choice a setting** - the commands read `fusion.toml`, as the compiler does (GOL.006)
- **Built for people and for AI agents:** every error in one form with a fix hint, and as JSON (L2.1, SET.009)
- **Never trust code:** packages, build scripts and plugins are untrusted - no install scripts that run on their own
  (the npm worms - Research R8.9), sandboxed libraries (D.122)
- **Today:** the compiler is `python main.py`; `check.py` holds the project's own checks. `console` comes once the
  compiler no longer needs Python (after self-hosting - L2.3)

---

## 2. The languages and what Fusion can take from them

Their tools, and the one or two ideas worth taking. Some overlap - an idea is listed where it started or is best known.

| # | Language | Its tools | What Fusion can take |
|---|---|---|---|
| 1 | Fortran | gfortran, fpm (package manager) | modules compiled once, reused; fast arrays |
| 2 | Lisp | REPL, a saved running "image", ASDF / Quicklisp | a REPL; saving a running program's state |
| 3 | COBOL | GnuCOBOL (`cobc`), copybooks | a readable compile listing / report for auditors |
| 4 | BASIC | immediate mode (`RUN`, `LIST`) | type a line, see the result at once |
| 5 | Pascal / Delphi | a very fast one-pass compiler; units with `interface` / `implementation`; the Delphi IDE | compile speed as a goal; a module's public interface (`--interface` - have) |
| 6 | C | gcc / clang, make, CMake, headers, `-Wall`, sanitizers | warning levels; sanitizers in test builds; **avoid** header files and hand-written makefiles |
| 7 | Smalltalk | a live environment: browser, inspector, debugger that fixes and continues | an object inspector; fix the code and carry on without restarting (R7.4) |
| 8 | SQL | `EXPLAIN` - shows the plan the database chose | `console explain`: show what the compiler chose (memory, ownership, stack or heap) |
| 9 | Ada / SPARK | gnat, gprbuild, `gnatprove`, `pragma Restrictions` | project restriction profiles (39.2); proving rules hold |
| 10 | C++ | CMake, Ninja, vcpkg / Conan, clang-tidy, clang-format | a linter and formatter; **avoid** C++'s build complexity |
| 11 | Erlang | rebar3, `observer` (a live view of every process), hot code upgrade | a live view of every service and its queue (R1.28); swapping code while running |
| 12 | Perl | `perl -c`, CPAN, CPAN Testers, perldoc | a central registry whose packages are tested on many machines |
| 13 | Haskell | ghc, ghci, cabal / stack, Hoogle | search functions by their type (`string -> int`) |
| 14 | Python | python, pip, venv, pytest, black, ruff, mypy, Jupyter | one command to run a script (Task 58); isolated environments; notebooks (R7.2) |
| 15 | Lua | lua, luac, LuaRocks; made to be embedded | embedding scripts in an app (Task 60) |
| 16 | R | `R CMD check`, CRAN's checks, RStudio, R Markdown | a full check before a package may be published |
| 17 | Java | javac, jar, Maven / Gradle, javadoc, jshell, Flight Recorder, jlink | docs from comments; a low-cost profiler always available; a trimmed run-time |
| 18 | JavaScript | node, npm / yarn / pnpm, ESLint, Prettier, bundlers, browser devtools | lock files; **avoid** install scripts and a sprawl of tools |
| 19 | PHP | `php -l`, Composer, `php -S` (a built-in web server) | a built-in development server (with Fusion.Web) |
| 20 | Ruby | gem, Bundler, rake, irb, Rails generators | generators: `console new web-api` makes a ready project |
| 21 | C# | `dotnet` (new, build, run, test, publish, add package, watch, format), NuGet, Roslyn analyzers, Visual Studio, Hot Reload | the model for `console`'s shape; `watch` (rebuild on save); analyzers as plugins |
| 22 | Scala | sbt, scala-cli, Metals | a script that names its own packages at the top |
| 23 | Clojure | Leiningen / deps, REPL-driven development, nREPL | the editor talks to a running REPL |
| 24 | Go | `go build / run / test / fmt / vet / mod / doc / generate`, gofmt, the race detector, pprof, `GOOS` / `GOARCH` | one tool; one format for all code; `vet`; benchmarks in tests; cross-compiling by a setting |
| 25 | Rust | cargo (new, build, run, test, bench, doc, publish, add, clippy, fmt, fix), rustup, `rustc --explain`, crates.io, miri, editions | `--explain E0123` for every error; lints with automatic fixes; editions (old code keeps working); a version manager |
| 26 | Kotlin | Gradle, IntelliJ, the Java-to-Kotlin converter | an IDE designed with the language; converting other code (Task 49) |
| 27 | Elixir | mix (new, compile, test, format, deps, release), iex, Hex, doctests | doctests - the examples in the docs run as tests (like SYNTAX_REFERENCE's examples - have) |
| 28 | Julia | Pkg (Project.toml / Manifest.toml), REPL modes | a REPL with a package mode; **avoid** slow first runs |
| 29 | TypeScript | tsc, tsconfig, `--noEmit`, `--watch`, `.d.ts` files | a check-only mode; strictness as settings (Fusion has); interface files |
| 30 | Swift | swiftc, Swift Package Manager, Xcode, Playgrounds | Playgrounds - each line's result shown beside it |
| - | Zig | `zig build` (the build written in Zig), `zig cc`, `zig fmt`, build modes | the build written in the language itself; a C cross-compiler included; debug / safe / fast / small |
| - | Goose | `goose check / run / build`; runs in memory with TinyCC | check, run and build as three commands; an instant run (R6) |
| - | Dart | `dart` (create, run, test, fix, compile), pub, Flutter hot reload | `fix` - upgrades old code to new syntax automatically |
| - | Nim | nim, nimble; compiles to C, like Fusion | the closest model for Fusion's C backend |
| - | Objective-C | clang, Xcode | - |
| - | Prolog | a query REPL | - |

---

## 3. What the compiler must support

#### Stages
- lexer, parser, checker, C generator, GCC - **have** (src/CLAUDE.md)
- an IR between the checker and the code generators - **planned** (Task 40)
- other backends: LLVM, WebAssembly - **planned** (Task 40, SET.013)
- the compiler written in Fusion - **planned** (Task 35; the test run is GOL.010)

#### What it is asked to do
- build a program - **have** (`python main.py x.fusion`)
- check only, no build (`--check`) - **idea** (Goose, TypeScript `--noEmit` - Research R6 G7)
- show a module's public interface - **have** (`--interface`)
- run at once (script mode) - **planned** (Task 58)
- interpret Fusion code - **planned** (Task 60.7)
- compile while a program runs (`Fusion.Compiler`) - **planned** (Task 60.8)
- run code while compiling (`comptime`) - **idea** (Research R4.4)

#### What it makes
- an executable - **have**
- the C source - **have** (kept beside the .exe)
- a library `.dll` / `.so` with a C interface - **planned** (MOD.003, L2.2)
- one module as one library - **planned** (57.6)
- for another platform (cross-compiling) - **idea** (Research R4.2, SET.020 `[backend] platform`)
- build modes: debug / release / safe / small - **planned** (SET.020)

#### Settings and projects
- `fusion.toml` (or .yaml / .json / .ini), written for a new project - **have** (SET.001)
- `[project]` name, version, the file holding main - **planned** (SET.019)
- modules and namespaces, search paths - **planned** (Task 57, L13.4)
- packages and their versions, a lock file - **idea**
- a locked, signed policy profile that the compiler enforces - **idea** (Research R8.7)

#### Errors and warnings
- one form: the line, what failed, a fix hint - **planned** (L2.1)
- JSON output for tools and AI agents (`--errors json`) - **planned** (SET.009)
- an error code with a long explanation (`--explain`) - **idea** (Rust)
- warning levels; warnings as errors - **idea**
- a secret written in the source an error (in a governed project) - **idea** (SEC-01, Research R8.9)

#### Safety builds
- the leak check (`-DFUSION_LEAK_CHECK`) - **have**
- sanitizers or Fil-C for the generated C - **idea** (Research R6.3)
- a report of every `unsafe` block - **idea** (Research R6.4)

#### Speed of the compiler
- compile only what changed; cache unchanged builds - **idea** (L2.5)
- the compiler's own speed watched - **planned** (Research R2.5)

#### For the IDE and other tools
- the compiler as a library: the syntax tree, the types, the symbols - **planned** (Task 60.8; needed by the language server)
- documentation comments, and documentation written from them - **planned** (SYN.032)
- a reproducible build: the same source always gives the same program, with a signed record of what it was built from - **idea** (SEC-04)

---

## 4. The commands - one app: `console`

One app for everything (L2.3, SET.012). The name `console` is the working name - final name to decide. Today's
equivalent is given where there is one.

#### Projects
- `console new <name> [template]` - a new project: folders, fusion.toml, main.fusion; templates (app, library, web-api, game) - **idea** (Ruby, C#)
- `console init` - make the current folder a project - **idea**
- `console settings` - show or change fusion.toml; write it from the master template - **planned** (SET.011)

#### Build and run
- `console build` - **have** as `python main.py x.fusion`
- `console run [file]` - build if changed, then run; a single file as a script - **planned** (Task 58)
- `console check` - check without building - **idea**
- `console watch` - rebuild (and rerun the tests) on every save - **idea** (C#, TypeScript)
- `console clean` - remove what was built - **idea**
- `console interface [module]` - **have** as `--interface`
- `console explain <error code>` - **idea** (Rust)

#### Tests and quality
- `console test` - run the tests; only the ones the change affects - **have** as `check.py` (the project's own); for users **idea** (L2.4)
- `console bench` - benchmarks - **idea** (Go)
- `console leaks` - the leak check of every example - **have** in `check.py`
- `console coverage` - which lines the tests run - **idea**
- `console fmt` - one format; convert between the three block styles - **planned** (SET.023)
- `console lint` / `console fix` - warnings and automatic fixes, upgrading old syntax - **idea** (Rust clippy, Dart fix)

#### Packages and libraries
- `console add / remove / update <package>` - **planned** (L2.3)
- `console search <words or a type>` - **idea** (Hoogle)
- `console publish` - full checks first, then publish to a registry - **idea** (R CMD check)
- `console audit` - known security problems in the packages used; licences - **idea** (Task 39.5)

#### Interactive
- `console repl` - type Fusion, see the result - **idea** (Research R7.3)
- `console notebook` - open a `.fusionnb` - **idea** (Research R7.2)

#### Documentation
- `console doc` - documentation from the comments; examples in it run as tests - **idea** (Elixir; SYNTAX_REFERENCE already works this way)

#### Release
- `console release` - a release build with an allowed-file list (no source maps, debug files, secrets), signed - **idea** (SEC-03, SEC-04)
- `console verify <program>` - check a program matches its recorded source - **idea** (SEC-04)
- `--target <platform>` on build / release - **idea** (Go, Zig)

#### The tool itself
- `console toolchain install / use <version>` - **idea** (rustup)
- `console doctor` - check GCC, paths and settings are right; say how to fix them - **idea** (Flutter); today `python check.py` and CLAUDE.md "Setting up a new machine"
- `console migrate <file.c / .py ...>` - other languages to Fusion through the language modules - **planned** (Task 49, D.158 `Fusion.Lang`)

#### Fusion's own development (stays in `check.py` until self-hosting)
- `--status`, `--ship`, `--docs`, `--builtins`, `--runtime`, `--selfhost`, `--fix-ascii`, `--example` - **have**

---

## 5. The IDE, and the other apps

#### The editor (any IDE, through a language server - Task 36)
- syntax highlighting - **planned** (36.0)
- a language server (LSP) - **planned** (SET.004):
  - errors as you type, with quick fixes
  - completion, hover (a type, a doc comment), go to definition, find every use, rename everywhere
  - inlay hints: the type `let` / `var` took, shown in grey (Points.md R3 - every type can be written)
  - format on save; convert the block style
- a debugger through the Debug Adapter Protocol: breakpoints, stepping, watching values - **planned** (SET.023)
- a test explorer: run one test, see which failed - **idea**
- a REPL panel, a notebook view - **idea** (Research R7)

#### Fusion's own views - not found in other languages' IDEs
- **ownership:** who owns this value, where it moves, where it is borrowed, and why a line is an error - **idea**
- **memory:** stack or heap, how big, which arrays move to the heap (D.154) - **idea**
- **services:** each service's queue, its worker, timeouts, health - a live dashboard - **idea** (Research R1.28)
- **settings:** fusion.toml as a form, each setting with its description and default (from fusionSettings.xml) - **idea**
- **governance links:** the ticket and the rule behind a function; suspect and orphan code - **idea** (Research R8)
- **code-quality overlays, refactoring, a symbol database** - **planned** (SET.024, fusionlib.IDE)

#### Other apps, apart from `console` and the IDE
- **a package registry** - a website and server, packages tested on several machines - **idea**
- **a documentation site** made from the docs - **idea** (Fusion.DocWiki)
- **a playground** - try Fusion in a browser, nothing installed (needs WebAssembly - Task 40) - **idea**
- **a governance console** - an administrator locks the policy profile for a team - **idea** (Research R8.7)
- **an admin dashboard** for running services and pools - **idea** (Research R1.28)
- **an installer** for Windows, Linux, macOS - **idea**
- **CI templates** - ready set-ups for GitHub Actions and others - **idea**
- **AI support** - a skill.md so AI agents can learn and write Fusion; errors as JSON - **planned** (L15.2, SET.009)

#### Open points for this map
- the final name of `console`
- which of section 4's commands are needed before 1.0, and which after
- whether the registry, the playground and the governance console are Fusion projects of their own

[Main](../Main.md) | [Spec](spec/index.md) | [Decisions >](../Decisions.md) <!-- nav -->
