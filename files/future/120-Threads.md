[< 111 Identity](111-Identity.md) | [Index](index.md) | [130 FarFuture >](130-FarFuture.md) <!-- nav -->

# 120 Threads

**Status:** design - the notes behind [100 Concurrency](../spec/100-Concurrency.md) (Task 42)

## Threads, Schedulers and Services: Notes for Future Consideration

**Status:** Notes and designs (user, 2026-11-02), not decisions. Some will become tasks
(42.26 and 42.27 already are), others are for future discussion. Moved here from CLAUDE.md's
project notes, with the user's clarifications and the useful ideas from the ChatGPT review
(`files/Fusion_Memory_Ownership_and_Services.md` - it saw only `files/Service.md`, so it is
taken as ideas, not plans).

#### Language documentaries

- https://nate.spot/software-documentaries/ - documentaries on how some languages came to be;
  many are on YouTube: https://www.youtube.com/channel/UCsUalyRg43M8D60mtHe6YcA
- The user's pick: the Clojure one, where Rich Hickey keeps it simple. Next to watch: *Simple
  Made Easy* (Rich Hickey, Strange Loop 2011) - **simple** (not tangled together) is not
  **easy** (familiar, close at hand). It supports "a simple working language first"; see also
  `files/Programming Languages Pain points.md`

#### 1. Starting a thread, and choosing its scheduler

The user's original note: `go.run(variables we need to use)(option how to schedule it) { ... }`

- The first brackets name the variables the thread uses (a capture list): the compiler knows
  exactly what crosses into the thread - each moved, borrowed or put in a temporary service
  (files/Ownership.md R7, Service.md S5)
- The second brackets choose a scheduler. **Optional:** by default there is none, and the
  extra brackets are left out
- **For now, the form is** `{ ... }.scheduler(x)` on the block - for example
  `service(x).run { ... }.scheduler(x)` - telling the compiler which scheduler to use when the
  service wasn't set up with one. (`go.run(...)(...)` is left aside for now)
- **The scheduler is declared before the threads that use it start:** it tells the service
  how to schedule when several variables or requests are being worked on - for example:
  - group read requests and carry them out together, instead of one at a time
  - one writer only - unless the writes touch different things (a different file lock,
    different database tables), which may run side by side
- Fits: `go f(x)` (Decisions.md CON.012); the `Scheduler` setting and a custom scheduler class
  (`files/Service.md`, Task 42.14); readers in parallel (42.18)

#### 2. A block that can't sleep or be interrupted (Task 42.26)

- While one iteration of a loop (or a marked block) runs, the thread doesn't sleep, yield or
  take an interrupt; only **between iterations** may it
- Interrupts and requests that arrive meanwhile go into the thread's **mailbox queue**, and
  are handled at the next safe point - data is never left half-changed
- This is cooperative scheduling with safe points (Erlang; Go before 1.14) - it builds on the
  `check interrupt` block after a loop (`files/Concurrency.md` "Cancellation / interrupt")
- **Issues to design for:**
  - **A long iteration could starve the other work** (why Go added preemption in 1.14). The
    user's answers:
    - a **request timeout** of so many seconds
    - and / or `sleepEvery(5)` - sleep every 5 seconds so others can work
    - **long-running work always gets its own thread**, never starving the others - loading
      a large text file, downloading a large file
  - **The operating system can always pause a thread** - no language can stop that. Fusion
    can promise the thread never sleeps, yields or takes an interrupt *by its own choice*
    mid-iteration, and ownership means no one else sees the half-done state. Truly never
    being paused needs a pinned core - the hot-path design (42.23, 42.24)
  - What counts as a safe point outside loops (a function call? the end of a `run` block?)
  - How long the mailbox may grow while a block runs (`Mailbox`, `WhenFull` settings)

#### 3. Telling requests apart: reads, writes, and resources with their own threads

- The database was only an example.
- The point: a scheduler must know **what kind of request each one is** - what is a write, what is a read, and how to tell them apart - so each request goes to the right thread and none conflict.

- **A log file is easy:** one file, one writer
- **A database is more complex:**
  - it has **its own threads** - its own pool handling requests, including requests from
    other programs, not just ours. **We can't simply lock a database because we're connected
    to it.** Fusion schedules only its own requests to it
  - a scheduler with priorities tells its requests apart
- **The user's example** - each request first goes into the queue of its service or group
  service; inside, the database object has its own threads and scheduler:

  | Request | Goes to | Why |
  |---|---|---|
  | writes `users` | the writer thread (the only one allowed to write) | one writer |
  | reads `users` while a write to it is waiting | the writer thread | it waits behind the write and sees its result |
  | reads `accounts` only | a separate shared (reader) thread | nothing writes accounts - no conflict |
  | reads `users` and `accounts` together (a join) | the writer thread | it borrows `users` for the request (a temporary borrow); the others keep readonly use of `accounts` |

- The database itself has its own **group service** implementation to handle its many
  requests (Service.md S7, D.077)
- **The goal:** every request lands on the right thread, never conflicting with another
- **To design:** how a request says what it reads and writes (worked out by the compiler,
  like the readonly analysis 32.2e, or declared by the database module); how the database's
  own concurrency (transactions, its locks) and Fusion's scheduler fit together

#### 4. A system shutdown is always handled (Task 42.27)

- When the system shuts down (or the program is asked to stop), the interrupt must be handled inside services and loops wherever the critical logic is - for example closing the log file and the database connections - so nothing is left in an unstable state.
- Fits the `Shutdown` setting (finish the mailbox, or drop it) and `final` clean-up (42.4).

#### 5. Ideas from the ChatGPT review

- **Memory budgets** - a limit per scope, request or service, giving a controlled error
  instead of growth without limit (a service's `MemoryLimit` exists in Service.md). The user
  adds: it feeds the **visualisation of threads and variables - everything - when profiling
  the program** (the thread view in the editor: 36.6)
- **Resource lifetimes** - files, sockets, database connections: a timeout and a maximum
  lifetime, **backoff settings** (how long to wait before trying again, growing each time),
  and a **timeout error to the calling thread** when a resource goes over its lifetime. A
  timeout never destroys a resource another thread is still using - clean-up waits for the
  requests still running, cancellation and shutdown
- **Run-time diagnostics** - capture everything: mailbox pressure, memory per service,
  resources still alive (logical leaks ownership can't find), and a **heatmap of variables and
  functions** - how often each is used, in threads and in normal code
- **Left for the future:** its `scope Request { memory_limit = ... }` and
  `resource X { timeout = ... }` forms (its own invented syntax, not Fusion's yet)
- **Its review questions already answered by the design:** leaving a scope (the `Shutdown`
  setting); parallel reads (the readonly analysis, 32.2e); waiting inside a request (an
  error). **Still open:** how the compiler proves a temporary service starts and ends
  (42.19); undoing side effects of a failed request; charging memory to `MemoryLimit`; when
  clean-up itself fails; the boundary with C code (`extern`)

[< 111 Identity](111-Identity.md) | [Index](index.md) | [130 FarFuture >](130-FarFuture.md) <!-- nav -->
