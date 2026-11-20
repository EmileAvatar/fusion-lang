# Programming and Execution Models

Programming languages can be developed and executed in several different ways. Some models describe how code is compiled or executed; others describe how developers interact with code or how work is organised at runtime.

These models are not mutually exclusive. For example, Java can be developed in an IDE, compiled into bytecode, executed by the JVM, and debugged interactively.

## 1. Traditional execution models

### 1. Compiled applications (AOT)

Examples: C, C++, Rust, Go.

- Source code is compiled into machine code before execution.
- Usually produces a native executable.
- Often provides excellent runtime performance.
- Compilation can catch many errors before the program runs.

Example:

```text
main.c → compiler → main.exe
```

AOT means *Ahead-Of-Time* compilation.

### 2. Interpreted or script execution

Examples: Python, JavaScript, PHP.

- Source code is executed by an interpreter or language runtime.
- A standalone executable is not necessarily required.
- Useful for automation, scripting and rapid development.

Example:

```text
python script.py
```

Implementation details vary: some interpreted languages first compile source into an intermediate representation or bytecode.

### 3. Virtual machine execution

Examples: Java JVM, .NET CLR.

- Source code is compiled into intermediate bytecode or intermediate language (IL).
- A virtual machine executes that representation.
- The runtime may use JIT compilation to turn frequently executed code into machine code.
- Runtime services can include garbage collection, type checking and managed execution.

Example:

```text
Java source → bytecode → JVM → machine code
```

### 4. Batch execution

Examples: Windows `.bat` files, Linux shell scripts, scheduled batch jobs.

- Executes a sequence of commands or tasks.
- Commonly used for automation, data processing and system administration.
- Often runs without interactive user input.
- Usually sequential by default, although parallel execution is possible.

Example:

```text
backup.bat
```

## 2. Interactive and incremental execution

These approaches let developers execute smaller pieces of code without necessarily running an entire application from the beginning.

### 5. Notebook execution

Examples: Jupyter Notebook, Google Colab.

- Code is divided into individual cells.
- Cells can be executed separately and in a chosen order.
- Runtime state persists between cell executions.
- A notebook document can contain code, documentation, results, charts and images.
- Particularly useful for experimentation, data analysis, machine learning and technical documentation.

A Jupyter `.ipynb` file is a JSON-based notebook document. The Jupyter interface sends code to a kernel, commonly an IPython kernel, which executes it in a running Python process.

### 6. REPL (Read-Eval-Print Loop)

Examples: Python interactive shell, Node.js console, Clojure REPL.

- The developer enters an expression or instruction.
- The runtime evaluates it immediately.
- The result is displayed.
- The developer can enter another instruction.
- Variables and other runtime state generally persist between commands.

Example:

```text
> let x = 100
> let y = 200
> print(x + y)
300
```

Unlike a notebook, a basic REPL normally does not organise work into a saved document of cells.

### 7. Live programming environments

Examples: Smalltalk/Pharo, LiveCode.

- Developers work with a running application and its live objects.
- Code can be modified while the application is running.
- Changes can become available without restarting the whole application.
- Developers can inspect and interact with objects directly.

This is particularly interesting for IDE design and long-running applications.

### 8. Hot reload / live reload

Examples: Flutter Hot Reload, JavaScript development servers.

- The application remains running while selected code changes are loaded.
- Some application state may be preserved.
- Useful for rapid feedback during development.
- Not every change can safely be applied without restarting; changes to data layouts, global state or runtime structures can require special handling.

## 3. Other execution and programming architectures

These models describe how computation is organised. They are not necessarily standalone execution formats.

| Model | Examples | Main idea |
|---|---|---|
| Event-driven | JavaScript, C# | Code executes in response to events. |
| Reactive | RxJS, Swift Combine | Code reacts to changes in data or event streams. |
| Actor model | Erlang, Akka | Independent actors communicate through messages. |
| Dataflow | LabVIEW | Execution follows data dependencies. |
| Graph-based | Unreal Blueprints | Logic is represented as connected nodes. |
| Functional | Haskell, Clojure | Computation is expressed through functions and evaluation. |
| Declarative | SQL, Prolog | Describe what result is wanted rather than every execution step. |
| Serverless | AWS Lambda | Functions run in response to triggers, with infrastructure managed by a platform. |
| Distributed | Apache Spark | Work is divided across multiple machines or processes. |
| GPU execution | CUDA | Parallel computation runs on GPU hardware. |

## 4. Comparison of execution models

| Model | Typical execution unit | Runtime state |
|---|---|---|
| Traditional compiled | Application or process | Persists while the process runs |
| Script | Script or instruction sequence | Persists while the process runs |
| JVM / CLR | Methods and compiled units | Managed runtime persists |
| Batch | Commands or tasks | Often temporary, depending on the job |
| Jupyter | Individual cells | Persists between cell executions |
| REPL | Individual expressions | Persists between commands |
| Live programming | Changed code and live objects | Mutable while the application runs |
| Event-driven | Event handlers | Application state persists |
| Actor | Messages handled by actors | Isolated state per actor |
| Reactive | Data changes and event streams | Subscriptions and state persist |

## 5. Ideas worth investigating for Fusion

### A. Notebook + traditional compilation

Fusion could support both normal source files and notebook documents:

```text
Application.fusion
Application.fusionnb
```

- `.fusion` could be compiled as a normal application or library.
- `.fusionnb` could contain executable code blocks, documentation and results.
- Notebook cells could share a managed runtime state.
- The same language rules, type checker and compiler infrastructure should ideally be reused.

### B. Live programming + services

Imagine modifying a service while an application is running:

- Service A continues processing its current work.
- Service B receives an updated implementation.
- Existing resources remain alive where compatible.
- New requests use the updated implementation.

This is a substantial runtime feature, not simply a matter of reloading a source file. Fusion would need to handle active calls, object layouts, state migration, resource lifetimes, and compatibility between old and new code.

A safer initial design could update a service only when it reaches a defined safe point, or start a replacement service and route new work to it while the old service finishes existing work.

### C. REPL + compiler

Fusion could provide an interactive console:

```text
> let x = 100
> let y = 200
> print(x + y)
300
```

The same compiler and type-checking infrastructure could be used for both interactive development and traditional applications.

## 6. Suggested Fusion architecture

Avoid tying Fusion to only one development or execution model. Separate the architecture into layers.

```text
┌──────────────────────────────────────────────┐
│             Development Interfaces           │
│                                              │
│       IDE · Notebook · REPL · CLI             │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│          Compiler / Language Services        │
│                                              │
│ Parser · Type Checker · Optimiser · Codegen   │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│                Execution Engine              │
│                                              │
│       Interpreter · JIT · AOT · Scheduler     │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│                    Runtime                   │
│                                              │
│ Memory · GC · Services · Resources · Threads  │
└──────────────────────────────────────────────┘
```

This separation gives Fusion flexibility without requiring a completely separate language implementation for every development environment.

### Important distinctions

- **AOT, JIT and interpretation** are execution and compilation strategies.
- **Jupyter, REPL and IDEs** are development interfaces.
- **JVM and CLR** are managed runtime environments and virtual machines.
- **Batch, event-driven, actor and reactive models** describe ways of organising work and execution.

These concepts can coexist. For example, Java can be edited in an IDE, compiled into bytecode, executed in a JVM, and debugged interactively.

## 7. Further research: Smalltalk and live programming

Smalltalk's live programming environment is particularly worth investigating for Fusion.

Its approach centres on a running system whose objects can be inspected and modified interactively. This is a useful reference when considering:

- Updating Fusion services without restarting the whole application.
- Inspecting live objects and service state.
- Managing code versions while work is in progress.
- Defining safe points for replacing implementations.
- Preserving or migrating resources during updates.

The main design challenge is ensuring that code updates do not invalidate active calls, shared state or resources.
