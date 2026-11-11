[< 090 Memory](090-Memory.md) | [Index](index.md) | [110 Generics >](110-Generics.md) <!-- nav -->

# 100 Concurrency

**Status:** [DESIGN] - nothing is built yet beyond reserved words (section 5). files/FEATURES.md Task 42.
Gathered 2026-11-10 (Task 51.5a) from every concurrency source; decisions and clashes are settled later
(section 6). The full detail lives in:
- [files/Service.md](../Service.md) - the `service` reference
- [files/Concurrency.md](../Concurrency.md) - terms, traps with code, the model, real-world cases, other languages
- [files/Concurrency_Traps.md](../Concurrency_Traps.md) - the overview tables
- [files/Ownership.md](../Ownership.md) sections 5-7 - ownership across threads

**Direction (user, 2026-11-10):** the service model is Fusion's **primary** way. The other ways
(mutex, channels, async / await, ...) are implemented too - other languages use them, and the
`Lang.<language>.Fusion` modules (Task 49 - `Lang.Python.Fusion`, `Lang.C.Fusion`) need them.

## Index

| # | Section | What it holds |
|---|---|---|
| 1 | [Summary and comparison](#1-summary-and-comparison) | Every way to do concurrency, compared - and the service against them; how languages do it |
| 2 | [Traps](#2-traps) | The 17 traps, and which part of the service model solves each |
| 3 | [The service model](#3-the-service-model) | Fusion's primary way: rules, settings, ownership, forms, hot path, threads, channels, kinds of threads, sleep and wake, baseline timings |
| 4 | [Other models](#4-other-models) | Threads, mutex, read-write lock, semaphore, atomics, condition variables, channels, async / await, ... |
| 5 | [What is built](#5-what-is-built) | Today: reserved words only |
| 6 | [To settle](#6-to-settle) | The clashes found and the user's answers - PROPOSED until threads are built |

Status words used below: **decided** (an ACTIVE decision in Decisions.md), **planned** (an agreed
FEATURES task), **design** (being planned), **idea**, **postponed**, **old** (spec text no decision covers).

---

## 1 Summary and comparison

#### 1.1 The ways to do concurrency

| Way | How it works | Data races | Deadlocks / freezes | Used by | In Fusion |
|---|---|---|---|---|---|
| **Service** | One owner per resource; callers send requests to its mailbox; its worker is the only writer | **None** - by construction | Prevented by rules (P2, P3, P4, P9); any left: a clear error | Fusion (Erlang's processes are the closest) | **Primary** - [3](#3-the-service-model) |
| Mutex / lock | Only one thread at a time inside a critical section | Prevented only where the lock is used | Easy: forgotten unlock, two locks in different orders | C, C++, Java, C#, Go, Python, Rust | Other model - [4.2](#42-mutex--lock) |
| Read-write lock | Many readers or one writer | As a mutex | As a mutex; writers can starve | C++, Java, C#, Go, Rust | Other model - [4.3](#43-read-write-lock) |
| Semaphore | At most N threads inside | Not by itself | Possible | Most languages | Other model - [4.4](#44-semaphore) |
| Atomic value | One variable changed in one indivisible step | None for that one variable | None | Most languages | Inside services (CON.013); other model - [4.5](#45-atomic-value) |
| Condition variable | A thread sleeps until another signals | Needs a lock | Lost wake-ups | C, C++, Java, C#, Python | Other model - [4.6](#46-condition-variable) |
| Channel | A pipe: one thread sends, another receives | None for what is sent | Nobody receiving: a freeze (Go: 58% of its freezes) | Go, C#, Rust, Kotlin | Other model - [4.7](#47-channel) |
| Actor | An object with its own mailbox and state; messages only | None | Rare; timeouts by default (Erlang) | Erlang / Elixir, Akka, Orleans | The service is actor-inspired (42.30) |
| async / await | A function pauses while it waits; the thread does other work | Depends on what is shared | Blocking inside async; sync-over-async | C#, JavaScript, Python, Rust, Kotlin | Other model - [4.8](#48-async--await-futures) |
| Threads directly | Start a thread (`go f(x)`) | Whatever they share | Whatever they wait on | All | `go` - [4.1](#41-threads-and-thread-pools) |
| Immutable data | Nothing changes, so anything may read it | None | None | Clojure, Haskell, Erlang | `readonly` / `const` sharing (D.028) - [4.9](#49-immutable-data-and-thread-local-storage) |
| Thread-local storage | Each thread its own copy | None | None | Most languages | Other model - [4.9](#49-immutable-data-and-thread-local-storage) |
| Event loop | One thread juggles many waits | None in your code | One blocking call stalls everything | Node.js, Python asyncio | Through async / await |

#### 1.2 The service against the usual ways

| Question | Locks (mutex) | Channels (Go) | Actors (Erlang) | Rust | **Fusion service** |
|---|---|---|---|---|---|
| Who may change shared data | Whoever holds the lock | The receiving goroutine, by convention | The actor only | The owner, checked at compile time | **The service's worker only** (S1) |
| What the developer writes | Every lock and unlock | Channels, goroutines, selects | Processes and messages | Types, lifetimes, `Arc<Mutex<T>>` | **Nothing, or `service x`** - the compiler makes temporary services (D.017) |
| A data race | Possible | Possible (a pointer sent and kept) | Impossible | Compile error | **Impossible - checked by the compiler** |
| A deadlock | Possible | Possible | Rare | Possible | **Prevented** - one resource per thread (P2), the hierarchy decides (P3) |
| A freeze | Silent | Silent unless all are stuck | Call timeout | Silent | **Every wait has a timeout** (P4) - a clear error |
| Several values changed together | Lock all, in order | Send to one owner | One actor owns them | One lock around a struct | **A group service** (D.077) or `run { }` |
| Cost when only one thread uses it | The lock | A channel | A process | None | **None - a plain variable** (CON.013) |

The same counter both ways (from the earlier spec text):

```fusion
// With a lock - only with [concurrency] locks = true, inside unsafe (4.2)
class Counter
    private int count
    private Mutex mutex = Mutex()

    void function increment()
        unsafe
            using mutex
                count += 1             // forget the lock once, and two threads lose an update
```

```fusion
// With a service - the default
service int counter = 0
counter += 1                           // one step; the service's worker is the only writer (S1)
```

#### 1.3 How languages handle a million requests (files/Concurrency.md section 4)

| Language | A million requests | Data races | Deadlocks | Freezes |
|---|---|---|---|---|
| C | Event loop by hand (epoll / IOCP) | Undefined behaviour; tools only | Nothing | Silent hang |
| C++ | Asio, coroutines | Undefined behaviour; tools only | `scoped_lock` for several locks | Silent hang |
| Java | Virtual threads (21+) | Library tools; memory model | Detectable at run time | Pinning (fixed in 24) |
| C# | async / await, bounded Channels | Library tools | Manual | Sync-over-async; cancellation tokens |
| Go | Goroutines | Race detector (testing) | Reported only when all are stuck | Channels: 58% of freezes |
| Python | asyncio, processes | GIL hides some | Nothing | Blocking in the event loop |
| Rust | async (Tokio) | **Compile errors** | Not prevented | Blocking in async |
| Erlang | Tiny processes, mailboxes | **None** (no sharing) | Call timeout by default | Supervisors restart |
| Node.js | Event loop + worker pool | None in your code | Rare | One blocking call stalls all |

| From | What Fusion takes |
|---|---|
| Erlang | Every resource a process with a mailbox (P1), call timeouts by default (P4), supervision trees (P5) - Erlang proves the million-connection goal |
| Rust | Shared changeable data without protection is an error - in Fusion it becomes a temporary service first (D.028) |
| Go | Cheap tasks over a few threads, a race detector, deadlines passed down to children; its bug study warns that channels alone don't stop freezes |
| C# | Bounded channels with a chosen "when full" policy (P6) |
| C++ | When several locks truly are needed (unsafe mode), take them all at once in a safe order |
| Java | Virtual threads: plain blocking-style code can scale; tools must show who holds what (P10) |

Fusion's own addition is the combination: **services by default, one resource per thread, the hierarchy
deciding contention, and every wait with a deadline** - between them they break three of the four
conditions a deadlock needs (Coffman, 1971: mutual exclusion, hold and wait, no preemption, circular
wait; P2 breaks hold and wait, P3 no preemption and circular wait).

---

## 2 Traps

Each trap with code that has the bug: [files/Concurrency.md](../Concurrency.md) section 2. The last
column says what in the service model ([section 3](#3-the-service-model)) solves it.

| # | Trap | What goes wrong | Usual fix | Solved in Fusion by | Principles |
|---|---|---|---|---|---|
| 1 | Race condition | Two threads change one value at once; updates are lost (`count += 1`) | A lock, or no shared changeable state | One writer: the worker ([3.8](#38-ownership-across-threads)); temporary services made by the compiler | P1, P10, P11 |
| 2 | Check-then-act | The situation changes between a check and the action | Check and act in one step | Each call one step; `service(x).run { }` ([3.4](#34-the-five-rules-version-one)) | P1, P7 |
| 3 | Deadlock | Two threads each hold what the other waits for | An order on locks; no waiting while holding | One resource per thread, group services ([3.8](#38-ownership-across-threads)); the hierarchy decides; timeouts | P2, P3, P4, P9 |
| 4 | Forgotten unlock | An early return or error leaves a lock held | Release tied to a scope | No caller locks at all; `final` clean-up ([3.9](#39-service-forms-and-the-service-interface)) | P1 |
| 5 | Livelock | Threads keep giving way and never progress | Break the symmetry | The hierarchy decides who wins ([3.11](#311-threads-and-scheduling)) | P3 |
| 6 | Starvation | One thread never gets its turn | Fairness, aging | Weighted turns, priority "5.4.1"; bounded mailboxes ([3.7](#37-settings)) | P8, P6 |
| 7 | Priority inversion | Important work waits behind unimportant work holding a lock | Priority inheritance | Weighted turns, priority inherited; no caller locks | P8, P1 |
| 8 | Change never seen | One thread's write never becomes visible to another | Synchronising operations only | All changes go through the service | P1 |
| 9 | Collection changed by two threads | Lost items, crashes, corrupted memory | One owner, or snapshots | A temporary service for a List / Map / array (D.057, [3.8](#38-ownership-across-threads)) | P1, P11 |
| 10 | Channel with nobody receiving | A send or receive waits forever | A lifetime and owner per channel; time limits | Every wait has a timeout; bounded mailboxes; owned threads | P4, P5, P6 |
| 11 | Blocking inside async | One slow call freezes every task on the thread | Separate executors | The service owns its schedule; long work on its own thread (42.26) | P7, P1 |
| 12 | Forgetting `await` | A result and its error are silently dropped | No orphan tasks | Owned threads: errors go to the parent | P5 |
| 13 | Sync-over-async deadlock | The main thread blocks on work that needs it | Never block a needed thread | Services never block on each other; timeouts | P9, P4 |
| 14 | Errors lost in another thread | A background error never reaches the caller | Errors travel with results | Owned threads: the parent gets its children's errors | P5 |
| 15 | Thread leaks, too many threads | Threads never end, or one per request | Bounded pools, owners | A shared pool, never a thread per service (CON.013); owned threads | P5, P6 |
| 16 | UI changed from another thread | Random crashes, drawing glitches | Thread affinity, messages | The UI as a service | P1 |
| 17 | Contention, false sharing | Correct but slow | Locality, share little | The service owns its schedule; readers in parallel; hot path with padded rings ([3.10](#310-hot-path)) | P7, P1 |

---

## 3 The service model

#### 3.1 The goal

A million requests on one machine with many cores - **no data races by construction**, deadlocks and
freezes prevented by rules (any that slip through become clear errors), no slowdown, a small memory and
CPU footprint, very scalable. A resource becomes a service instead of every caller locking it; manual
locking is a last resort (CLAUDE.md, FEATURES Task 42).

#### 3.2 The principles - decided (D.075)

| | Principle | In one line |
|---|---|---|
| P1 | Resource as Service | One coordinator owns each resource; everyone else sends requests (`service` keyword) |
| P2 | One Thread, One Resource | No thread holds or waits on two resources; things that change together form one unit - a group service (D.077) |
| P3 | The Hierarchy Decides | When two threads want one resource, a rule (the senior thread, by default) picks the winner |
| P4 | Every Wait Has a Deadline | Every thread, request and wait has a timeout; a freeze becomes an error |
| P5 | Owned Threads | Every thread has a parent; parents wait for, cancel and get errors from their children |
| P6 | Bounded Mailboxes | Every queue has a size and a stated "when full" policy |
| P7 | The Service Owns Its Schedule | The service decides the order and what runs in parallel |
| P8 | Weighted Turns | Priorities get shares of the turns; low priority still runs; priority is inherited |
| P9 | Services Never Block on Each Other | While handling a request, a service calls only down the hierarchy, or sends without waiting |
| P10 | Visible Concurrency | Editor tools and compiler warnings show who touches what |
| P11 | One Writer | Assigning moves; a value two threads use gets a (temporary) service as its only writer; readers may run together |

#### 3.3 What a service is

`service` marks state that several threads share - a variable, a struct or a class object. `service` is
a reserved keyword (D.024 - decided).

```fusion
service int counter = 0                     // a variable
service Person person = Person("Ada")       // a struct
service Car honda = Honda(Color.Black)      // a class object
```

#### 3.4 The five rules (version one)

| # | Rule | Status |
|---|---|---|
| 1 | **One owner.** Each statement or call on a service is one indivisible step; anything read out is a **copy**; copying a service variable gives another **handle** | decided (D.067) |
| 2 | **The compiler decides how it runs:** one thread - a plain variable (no cost); a simple value - CPU atomics; anything else - a mailbox served by workers from a shared pool, never a thread per service | planned (CON.013) |
| 3 | **Code runs in order:** after `counter += 1`, `print(counter)` shows the new value; `async` at the call to not wait; one request at a time (not re-entrant) | decided (D.068) |
| 4 | **Several steps as one:** `service(x).run { ... }` - a one-time atomic operation where it is written | planned (CON.015) |
| 5 | **A timeout means the caller stopped waiting**, not that the work was undone; a request ends completed, failed, timed out or cancelled | planned (CON.016) |

```fusion
service(account).run {
    if account.balance >= 800 {             // the check and the change are one step:
        account.balance -= 800              // two withdrawals can't both pass the check
    }
}
```

Version one needs four settings: `Mailbox`, `WhenFull`, `Timeout`, `final`; a prototype measures the cost
first (files/Concurrency.md 3.11).

#### 3.5 Where a service is created - decided (D.066)

- Only for state that several threads read or write
- Outside loops: a class field, or a variable in a function
- The parent thread creates it; its child threads use it; a child may create its own for its children
- A warning when no other thread ever uses it

```fusion
void function processOrders(List<Order> orders) {
    service Totals totals = Totals()        // the parent creates it, outside the loop
    for order in orders {
        go worker(order, totals)            // the children use it
    }
}

void function worker(Order order, Totals totals) {
    service List<Line> lines = []           // a child's own service, for its children
    for item in order.items {
        go priceLine(item, lines)
    }
    totals.add(order.id, lines)             // the result goes up to the parent's service
}
```

#### 3.6 Using a service

| Form | What it does | Status |
|---|---|---|
| `service <type> <name> = value` | Declares a service | planned (42.1) |
| `service(name).Setting = value` | Changes a setting - only the creating thread | planned (42.2) |
| `service(name).run { ... }` | A one-time atomic operation | planned (CON.015) |
| `async` at a call | Sends a request without waiting for its reply | decided (D.068) |
| `service class Name { ... }` | Every object is a service; each method one atomic step | planned, after version one (42.3b) |
| `service(a, b, ...) group` | Two or more variables become one service | decided (D.077), after version one (42.3) |
| `service(x).final = { ... }` | Extra clean-up; leaving scope always releases everything | planned (42.4) |

#### 3.7 Settings

Prime settings (files/Service.md; FEATURES 42.14) - defaults in `fusion.toml` `[concurrency.defaults]`:

| Setting | What it does | Values | Default | Status |
|---|---|---|---|---|
| `Mailbox` | How many requests can wait | a number | 12 | planned |
| `WhenFull` | A full mailbox | `WAIT` (the sender waits), `ERROR` (`QueueFullError`); a hot path never waits | `WAIT` | decided (D.070) |
| `Timeout` | How long a caller waits | a duration (`5s`) | per kind of resource | decided (D.071); values to confirm (42.8) |
| `final` | Extra clean-up when it goes out of scope | a block | none | planned |
| `Scheduler` | The order requests run in | `IMMEDIATE`, `BATCHED`, custom | `IMMEDIATE` | planned |
| `Priority` | Shares of the turns | `"5.4.1"` (high 5, medium 4, low 1 in 10), custom | `"5.4.1"` | planned (42.14) |
| `Rule` | Who wins when two threads want it | `HIERARCHY`, custom | `HIERARCHY` | planned |
| `WorkerThreadType` | Who does the work | `AUTO` (SHARED as more threads read, SINGLE when heavy), `SINGLE`, `SHARED` | `AUTO` | decided (D.069) |
| `ThreadPool` | The pool that serves it | a pool, `ThreadPool(10)` | the program's shared pool | planned |
| `Readers` | Readonly requests together or in turn | `PARALLEL`, `SERIAL` | `PARALLEL` | planned (S4) |

| Rule | Detail | Status |
|---|---|---|
| Priority "5.4.1" | Weighted turns: in every 10, high 5, medium 4, low 1 - low never starves; turns spread through the cycle (H M H M H L ...); a level with no work gives its turns away | planned (42.14) |
| Which value wins | Built-in defaults < `fusion.toml` < the program's defaults < `service(x)` in code | planned (42.6) |
| Settings that fit the machine | Levels from MIN (embedded or unknown memory) up; a machine matching no level gets MIN | design (42.6, CON.011) |
| Durations | `500ms`, `5s`, `2min`, `1h` - int milliseconds; hot path `ns`, `us` - long nanoseconds; never mixed | planned (42.16) |
| Secondary settings | Coalesce, BatchSize, BatchDelay, IdleTimeout, OnError, RestartLimit, Name, Trace, Affinity, MemoryLimit, Lifetime, Snapshot, WarnAt, Retry, Shutdown, Access, Weight | postponed - after version one (42.11) |

Project settings (files/spec/001-TomlSettings.md "Decided, not built"):

| Setting | Values | Default | What it does |
|---|---|---|---|
| `[threads] enabled` | `true` / `false` | `true` | Threads allowed at all (off for small devices) |
| `[concurrency] autoService` | `on` / `warn` / `off` | `on` | Two or more threads using one variable: a temporary service (off: an error) |
| `[concurrency] readers` | `parallel` / `inTurn` | `parallel` | Read-only requests together or in turn |
| `[concurrency] resourceAsService` | `true` / `false` | `true` | Files, sockets, databases are services; direct access only in unsafe mode |
| `[concurrency.defaults]` | the prime settings | as above | The defaults every service starts from |
| Trap checks *(name open)* | warning / error, per check | warning | Each trap check can be made an error (D.074) |
| `[collections] threads`, `sharedThreads` | `shared` / `dedicated`; a number | `shared`, `10` | The worker a collection used by several threads gets |
| `[hotpath] ...` | see [3.10](#310-hot-path) | | |

#### 3.8 Ownership across threads

Rules in a service (files/Service.md, FEATURES 42.18 - planned):

| # | Rule |
|---|---|
| S1 | **The worker is the only writer** - nothing outside holds a reference to its inside |
| S2 | **The service owns its value; a request borrows it** - to change or only read, as the called function's signature says |
| S3 | **Nothing escapes a request** - no returning, storing or capturing a reference to the inside (`byVal` copies out) |
| S4 | **Readers in parallel** - readonly requests together; a changing request alone |
| S5 | **Temporary services** - made when two or more threads use one value, gone when the last ends |
| S6 | **Into a request** - borrowed for the request only, moved in (send), or copied |
| S7 | **Two or more resources: a group service**; waiting inside a request for another thread's result is an error |
| S8 | **Plain counts inside a service**; only handles use atomic counts (D.018) |
| S9 | **The thread-boundary table** (below) |
| S10 | **A `Service` interface** every kind implements ([3.9](#39-service-forms-and-the-service-interface)) |

| Rule | Detail | Status |
|---|---|---|
| Temporary service | Two or more threads use one variable: the compiler makes `service(x)`; the threads borrow it, one whole call at a time; the parent's own use is a request too; the last thread ends - the variable owns its value again | decided (D.017, 42.19) |
| send / sync | **send** - a value goes to another thread and the sender no longer has it; **sync** - many threads use it through a service; never written, worked out by the compiler; errors say send / copy / service | decided (D.028, 42.22) |
| Group service | A thread using two or more resources: they become one service - written or made by the compiler; it owns them while its requests run; no thread holds two separate services | decided (D.077, 42.3, 42.20) |
| Collections | An array, List or Map used by two or more threads gets a temporary service; `[collections] threads` picks its worker | decided (D.057, 42.17) |
| `shared` keyword | Not added until a real need shows - `byRef` already shares | postponed (D.106) |

Truth table 5 - a value reaching another thread (files/Ownership.md):

| Value | `go f(x)`, one thread | `go f(x)`, two or more threads | `go f(readonly x)` | `go f(byVal x)` | `service(s).send(x)` |
|---|---|---|---|---|---|
| int, plain struct | copied | copied | copied | copied | copied |
| string | copied | copied | copied | copied | copied |
| List, Map, object | borrowed - the parent frozen | **sync**: a temporary service | read in parallel, frozen meanwhile | each thread its own | **send**: moved, the sender loses it |
| a struct holding a List | borrowed | sync | read in parallel | each its own | send: moved |
| `shared` object | read only | sync | read in parallel | a copy | an error - send a copy |
| service handle | shared (atomic count) | shared | shared | an error - a service can't be copied | the handle travels |
| a function value holding a borrow | error | error | error | - | error |

#### 3.9 Service forms and the Service interface

```fusion
interface Service<T>                    // T: the kind of request
    void function send(T request)       // a caller puts a request in the mailbox
    T function fetch()                  // the worker fetches its next request
    void function start()
    void function stop()
    ServiceState function state()
    int function waiting()              // requests in the mailbox
```

| Form | When | Implementation | Status |
|---|---|---|---|
| `service T x = ...` | A shared value | `BasicService` - a mailbox and one worker | planned (CON.005, 42.21 - needs interfaces) |
| Two or more threads use a plain variable | Made by the compiler | `SharedService` (temporary) | decided (D.017) |
| A file, socket, pipe or database | Resources are services by default | `FileService`, `DatabaseService` | decided (D.072, 42.5) |
| `service class X { }` | Every object a service; each method one step | - | planned (42.3b) |
| `service(a, b) group` | Several values changed together | a group service | decided (D.077) |
| `hotpath service T x = ...` | A dedicated thread that never sleeps | `HotPathService` | decided (D.019) |
| Lanes, thread limits, buffers, named channels | Each form configured for its situation | - | idea (42.31) |

A resource is released when its block ends - a file is closed, even on an error (`final` clean-up, 42.4).

#### 3.10 Hot path

A dedicated thread that never sleeps - it keeps one processor busy (decided D.019; FEATURES 42.23-42.24).

```fusion
hotpath service Trade trading = Trade("BTC-USD") {
    service(trading).Core = 3                  // pinned to CPU core 3
    service(trading).Ring = 4096               // input slots, a power of 2
    service(trading).WhenFull = Full.COALESCE  // never WAIT (a compile error)
    service(trading).Wait = Wait.SPIN          // never sleeps
    service(trading).Budget = 50ns             // a warning when a step takes longer
}

hotpath void function step(Tick t)             // the checks without the thread
```

| | What the compiler checks (H) | | What happens while it runs (T) |
|---|---|---|---|
| H1 | No allocating | T1 | Pinned to a core, real-time priority |
| H2 | No blocking | T2 | An input ring (power of 2, cache-line padded) |
| H3 | No count changes | T3 | Wait SPIN (default) or YIELD - never PARK |
| H4 | No unknown calls | T4 | Memory locked and touched at set-up |
| H5 | No unbounded loops (a setting) | T5 | No replies - results go to other rings |
| H6 | Errors stay inside | T6 | A latency histogram, the `Budget` warning |
| H7 | Fixed-size ring messages | T7 | A watchdog |
| H8 | Only the set-up allocates | T8 | Set-up, warm-up, running, drain, stop |
| H9 | Sizes from the hardware | | |

`[hotpath]` settings (001-TomlSettings): `enabled`, `ring` (1024), `wait` (spin), `whenFull` (error),
`pinThreads`, `lockMemory`, `checks`, `loopLimit` - all on by default; ideas: `hugePages`, `budgetStrict`.

#### 3.11 Threads and scheduling

| Item | Detail | Status |
|---|---|---|
| Thread identity | Every thread has an ID (never reused, main = 0), a parent and a hierarchy key (0.2.1); the hierarchy decides who gets a resource | planned (CON.018, 42.7, 42.9) |
| The Thread class | ID, GUID, hierarchy key, priority, helpers that track threads | design (42.7) |
| Scheduler | The OS scheduler by default; a Fusion scheduler for advanced use | decided (D.073) |
| Custom schedulers, rules, priorities | One method per class (files/Service.md) | postponed - after version one (42.9, 42.15) |
| `go f(x)` | Run a function on another thread | design (CON.012) |
| A capture list: `go.run(vars)(schedule) { }` | Names exactly what crosses into the thread | idea (FutureFeatures "Threads, Schedulers and Services" 1) |
| `{ }.scheduler(x)` on a block | Which scheduler a block uses | idea (same, 1) |
| Reads and writes told apart | A scheduler knows each request's kind; a database with its own threads | idea (same, 3) |
| Request order | A sequence number that only goes up, not time + thread id | idea (42.32) |
| Cluster threads | Over several servers - a framework of its own | postponed (CON.009, 42.12) |
| `parallel for` | Each loop pass may run on a pool thread - `go` is used for now | idea (42.41) |
| Two hierarchies (user, 2026-11-10) | **Levels**: System > Process > Pool > Thread > Task / goroutine > Channel - where concurrency sits; how a thread deals with the process above it and the tasks below it. **Family tree** (CON.018): who made whom - it breaks livelocks and deadlocks | design - both kept (D.129 proposed) |

The levels (from the earlier spec text):

| Level | What it is |
|---|---|
| System | The operating system, managing every process |
| Process | A running program with its own memory |
| Thread pool | A set of threads that take work from a queue |
| Thread | A unit of work inside a process; threads share its memory |
| Task / goroutine | A very light unit of work, run by a thread |
| Channel / mailbox | Where requests wait between threads (3.14) |

#### 3.12 Interrupts, shutdown, transactions

| Item | Detail | Status |
|---|---|---|
| A block that can't sleep or be interrupted | Within one loop pass the thread doesn't sleep, yield or take an interrupt; they wait in the mailbox until the next safe point | design (42.26) |
| `check interrupt(signal, data)` | The loop's safe point for Shutdown / Pause / Stop | design (56.5, postponed to 42) |
| Shutdown always handled | The interrupt reaches services and loops; logs and connections closed | design (42.27) |
| A service's interrupt handler | `db.setCheckInterrupt(signal, data) { }` - what the service does for each interrupt; Shutdown not handled terminates it, Pause suspends it ([3.14](#314-channels-in-a-service)) | design (42.37) |
| A failing operation | Fusion undoes what it can; the developer handles the error; else it bubbles up | decided (D.120) |
| A `Transaction` interface | commit gives OK / FAILED, rollback | design (CON.020, 42.29) |

#### 3.13 Checks and tools

| Item | Detail | Status |
|---|---|---|
| Trap checks | Two resources per thread, shared variables, missing timeouts, services blocking on each other - warnings by default, errors by setting | decided (D.074, CON.019, 42.10) |
| P9 across modules | A service calls only down the hierarchy | planned (42.13) |
| The thread view in the editor | A stack of threads: who touches what | planned (36.6) |
| Memory budgets, run-time diagnostics | A limit per scope or service; mailbox pressure, memory per service | idea (FutureFeatures 5) |
| An identity for everything | A GUID per name; which variables are in a thread or group | idea (42.28) |
| Explaining services | Text boxes for people and for other AIs; diagrams; a comparison with actors | planned (42.30, 42.33) |

#### 3.14 Channels in a service

From the user (2026-11-10 - provisional, subject to change): a channel is a named mailbox - a buffer of requests, named so developers
can remember and use it. Every service (and group service) has one by default.

| Channel | What it holds | Who sends | Who takes from it | Status |
|---|---|---|---|---|
| The default mailbox (no name) | The requests to the service - linked to the service itself, so it needs no name | Any thread that uses the service | The service's thread(s) | design |
| A named channel | A named buffer of requests of one kind - e.g. `writes`, `reads`, `status` | Threads that send that kind of work | The next free thread of the service that handles it - several may be working | design (42.31, 42.34) |
| The interrupt channel | Interrupts only (Shutdown, Pause, ...) | The OS only - threads send messages, not interrupts | The service or main thread, which passes it on to each pool and child; every thread and service handles it | design (42.37) |
| An outbound channel | Results on their way out, buffered - the service's thread keeps working | The service | The calling thread waiting for feedback, or other threads | design (42.34) |

- Named channels are for a service with many threads, where some threads handle special work
- A busy thread checks for an interrupt after each loop pass - at the loop (`check interrupt`, Task 56)
  or at the service (its interrupt handler, below)
- The loop checks of Task 56 could also be set on a service, saying how it handles them

How an interrupt travels (user, 2026-11-10 - provisional):
- Threads send only messages / requests - message passing in normal operation; a thread can't send an interrupt
- An interrupt comes only from the OS (e.g. `InterruptSignal.Shutdown`)
- The service, or the main thread, receives it and passes it on to each thread pool and child
- Every thread and service must handle it - so children close and finish their tasks

```text
OS --Shutdown--> main thread / service --passes on--> thread pools --> each child thread / service
```

A service's interrupt handler (pseudo code - the design is subject to change):
- The check is implicit - the handler is the check; no `check interrupt` line, no `exit loop` or
  `continue loop` (those belong to a loop's `check` block, Task 56)

```fusion
service Database db = Database()

db.setCheckInterrupt(signal, data) {       // what this service does for each interrupt
    if signal == InterruptSignal.Shutdown
        saveProgress()
        cleanup()
    if signal == InterruptSignal.Pause
        waitForResume()
}
```

When a service does not handle an interrupt:

| Interrupt | Not handled |
|---|---|
| Shutdown | The service is terminated, and released when it reaches the end of its block |
| Pause | The service is suspended |
| Any other | Nothing happens |

More interrupts may come later; only these two have a consequence when not handled.

The `Channel` interface and the `ChannelType` enum (pseudo code - the design is subject to change; to be
designed properly after checking how other languages do it, 42.34):

```fusion
enum ChannelType { INBOUND, OUTBOUND }

interface Channel {
    channel(string name, ChannelType type?)  // ChannelType optional
    property Name (get, set)
    property ChannelType (get)
    property long getID()
}

db.channel("status", ChannelType.OUTBOUND)
db.channel("write", ChannelType.INBOUND)
```

#### 3.15 Kinds of threads

From the user (2026-11-10 - provisional, subject to change): threads get named kinds, by their job.
- The names are suggestions - they make it easier to tell the jobs apart; perhaps an enum (`ThreadType`)
- The compiler tells threads apart by their ID, not their kind
- Many threads with complex work: named kinds and named channels help; a small or single-thread
  service doesn't need them

| Kind | Its job | How many |
|---|---|---|
| Worker | Does one specific task, whatever the request | Any number; often pooled |
| Writer | The only thread that writes or changes the resource (P11) | One per resource |
| Reader | Reads the resource without having to wait | Several; pooled or shared |
| Field reader (named) | Reads only one part - e.g. a database connection on the user table, or the account table | One or more per part |
| Watcher | Watches the mailbox and the named channels; wakes the writer, readers or scheduler | Often one shared thread for many services |
| Scheduler | Watches too, and assigns threads to handle a request | One per service or group, or shared |
| Outbound | Pushes results to other channels (an outbound channel, 3.14) | One, or shared |

Not every thread is one kind:

| Size of the service | How the kinds are combined |
|---|---|
| Small | One thread does every job - watcher, writer, reader, outbound |
| Medium | One writer; readers pooled; a shared watcher wakes them |
| Large | Each kind its own threads; field readers per part; a scheduler assigns the work; outbound threads push results |

#### 3.16 Sleep and wake - the parent holds the channel

From the user (2026-11-10 - provisional, subject to change); to be designed further (42.36). It does the job of a condition variable
([4.6](#46-condition-variable)) inside the service model:
- A worker's condition variable is its mailbox or its named channel
- The parent holds that channel - not the sleeping worker
- The parent (its main thread, or a global shared thread - a watcher) checks the channel routinely,
  with its own scheduling
- A request is waiting: the parent wakes the worker; the worker does the work
- The work done: the worker sleeps, or is suspended, until the parent wakes it again
- A worker stays awake as long as it has tasks; with none left, or on Shutdown, it sleeps
- The parent's rules: how often and for how long a channel is checked - set once threads work, starting
  from the baseline below (3.18), then tuned
- Example: `orders` - a main working thread or a global shared thread checks for orders, then wakes the
  worker that does the work

```text
caller --send--> [orders mailbox] <--checks-- parent / watcher --wakes--> worker --> resource
                                                                          worker done --> sleeps
```

#### 3.17 A thread holds no state

From the user (2026-11-10 - provisional, subject to change):
- A thread holds no state data of its own - it uses the service's variables
- Variables made inside `service(x).run { }` belong to that thread for that run - no `unsafe` needed
- Thread-local storage as C, Java, Python and Rust have it (a global, one copy per thread) only in
  `unsafe` - e.g. a `Lang.C.Fusion` module that needs it

```fusion
db.run {
    int found = 0                          // this thread's, for this run - no unsafe needed
    for row in db.users
        if row.active
            found += 1
}
```

#### 3.18 Baseline timings from other languages

Gathered 2026-11-10 (user: get baseline data from other languages, tune once a working system exists).
Starting points only, not decisions - check them against current versions before use.

| Runtime | What | Value |
|---|---|---|
| Go | sysmon (its watcher thread) sleeps between checks | 20 us at first, backing off to at most 10 ms when idle |
| Go | A goroutine running without yielding is preempted after | about 10 ms |
| Go | A thread stuck in a system call loses its processor after | about 20 us (one sysmon tick), when other work waits |
| Go | The global run queue is checked | every 61st scheduling |
| Rust (Tokio) | The global queue is checked | every 61 tasks (multi-thread), 31 (current-thread); adapted at run time |
| Rust (Tokio) | I/O and timer events are polled | every 61 tasks |
| Rust (Tokio) | An idle blocking-pool thread is kept alive | 10 s |
| C# (.NET) | The thread pool may add or remove a thread | every 500 ms, or when a work item completes (hill climbing) |
| C# (.NET) | Starvation check (all threads stuck?) | every 500 ms |
| Erlang (BEAM) | A process runs before it is swapped out | 4000 reductions (2000 in older versions) |
| Erlang (BEAM) | An idle scheduler | spins briefly before sleeping (`+sbwt`); `none` saves CPU, may add latency |
| Java | An idle thread in a cached pool / ForkJoinPool is kept | 60 s (to confirm) |
| OS (Linux, Windows) | A thread's time slice | a few ms (Linux) to tens of ms (Windows) (to confirm) |

What it suggests for Fusion (to try, then tune):
- A watcher that checks often while busy (microseconds) and backs off when idle (to ~10 ms) - as Go's sysmon
- A fairness check every N requests (Go and Tokio use 61) so no channel starves
- An idle worker sleeps at once; an idle pooled thread is released after seconds (Tokio 10 s, Java 60 s)

Sources: [Go sysmon](https://golang.design/under-the-hood/en/part3concurrency/ch09sched/sysmon/),
[Go commit f9066fe1](https://lab.nexedi.com/kirr/go/-/commit/f9066fe1c0a7181242f77d8534e0b6e112c982a9?w=1),
[Go sysmon explained](https://internals-for-interns.com/posts/go-sysmon/),
[Tokio Builder](https://docs.rs/tokio/1.22.0/tokio/runtime/struct.Builder.html),
[CLR thread injection](https://mattwarren.org/2017/04/13/The-CLR-Thread-Pool-Thread-Injection-Algorithm),
[.NET issue 46077](https://github.com/dotnet/runtime/issues/46077),
[BEAM reductions (Lambda Days)](https://www.lambdadays.org/static/upload/media/1552665212914388thatonefornowbenmarx.pdf),
[Riak sbwt tuning](https://github.com/basho/leveldb/wiki/riak-tuning-2)

---

## 4 Other models

Implemented too, next to services (user, 2026-11-10): other languages use them, and the
`Lang.<language>.Fusion` modules (Task 49) need them. The syntax below is as designed in
files/Concurrency.md section 1 - not decided yet. Where each fits next to services: [section 6](#6-to-settle).

#### 4.1 Threads and thread pools

| Term | What it is |
|---|---|
| Process | A running program with its own memory |
| Thread | A unit of work inside a process; threads share the process's memory |
| Main thread | The first thread; often the only one allowed to touch the UI |
| Thread pool | A fixed set of threads that take tasks from a queue - no thread per task |
| Task / job | A piece of work handed to a pool |
| Context switch | The OS pausing one thread and running another - at any point, even inside `count += 1` |

```fusion
go worker(jobs)                        // run worker on another thread (CON.012 - design)
```

#### 4.2 Mutex / lock

Only one thread at a time may hold it; `using lock { }` unlocks at the end of the block, even on an error.

Off by default (user, 2026-11-10 - provisional, subject to change; D.125 proposed): services are the default; a project switches locks on in
`fusion.toml`, and a lock is written inside `unsafe` - it may cause deadlocks and race conditions, and the
code shows it. A `Lang.C.Fusion` module may need `unsafe` for this. The same holds for the read-write lock,
the semaphore and the condition variable (4.3, 4.4, 4.6). Lock ordering (always take lock A before lock B)
matters only here - in the service model no thread holds two resources (P2).

Unlocked at the end of its scope (user, 2026-11-11; D.133): the compiler adds the unlock where the
lock's scope ends - the block it is declared in - even if the developer forgot it; also on an error.

```fusion
unsafe {
    lock.lock()
    balance -= amount                  // no unlock written
}                                      // the compiler unlocks here
```

```toml
[concurrency]
locks = false        # default; true allows locks inside unsafe
```

```fusion
Mutex lock = Mutex()
int balance = 100

void function withdraw(int amount) {
    unsafe {                           // a lock may deadlock or race - the code shows it
        using lock {                   // locked here
            if balance >= amount {
                balance -= amount
            }
        }                              // unlocked here, always
    }
}
```

#### 4.3 Read-write lock

Many readers at once, or one writer alone.

```fusion
ReadWriteLock rw = ReadWriteLock()
using rw.read() {
    print(settings["theme"])           // many threads may read together
}
using rw.write() {
    settings["theme"] = "dark"         // a writer waits until every reader is done
}
```

#### 4.4 Semaphore

A counter of permits: at most N threads inside at once. A mutex is a semaphore with one permit.

```fusion
Semaphore downloads = Semaphore(3)     // at most 3 downloads at the same time
using downloads {
    fetch(url)
}
```

#### 4.5 Atomic value

One variable whose operations (add, swap, compare-and-set) can't be interrupted - fast, but for one
variable only. A service of a simple value uses them by itself (CON.013).

```fusion
Atomic<int> hits = Atomic<int>(0)
hits.add(1)                            // safe from any number of threads
```

#### 4.6 Condition variable

A thread sleeps until another says "something changed" (the queue is no longer empty). Channels are
built on it; most programs use a channel instead.

In Fusion (user, 2026-11-10 - provisional): the parent holds the worker's channel, checks it and wakes the
worker ([3.16](#316-sleep-and-wake---the-parent-holds-the-channel)); the raw form only with locks on,
inside `unsafe` (4.2).

#### 4.7 Channel

A pipe from one thread to another: `send` puts a value in, `receive` takes one out, waiting until one
arrives. Unbuffered: the sender waits for a receiver; buffered (N): it runs ahead until full; closing
tells the receivers nothing more is coming. CON.012 (design); `<-` is read by the lexer.

In a service (user, 2026-11-10 - provisional): a channel is a named mailbox - the default mailbox, named
channels, the interrupt channel and outbound channels ([3.14](#314-channels-in-a-service)).

```fusion
Channel<int> jobs = Channel.create<int>(10)    // room for 10 values

void function worker(Channel<int> input) {
    for n in input {                           // receives until the channel is closed
        print("square of {n} = {@1}", n * n)
    }
}

void function main() {
    go worker(jobs)
    for i in range(1, 6) {
        jobs.send(i)
    }
    jobs.close()                               // the worker's loop ends
}
```

#### 4.8 async / await, futures

A way to wait without blocking a thread - mostly for I/O. An `async` function can pause; `await` pauses
it until a result is ready, and the thread does other work meanwhile. A future is a value that exists
later. Rule of thumb: threads for heavy computing, async for waiting. CON.012 (design).

Both forms (user, 2026-11-10 - provisional; D.127 proposed): **A** `async` at a call - don't wait for a
service (D.068); **B** an `async function` with `await`, as in C#, Python and JavaScript. `await` takes a
Future from either.

```fusion
Future<int> f = async counter.get()       // A: the request is sent, this thread carries on
doOtherWork()
int value = await f                       // wait here for the answer
```

```fusion
async string, Error function fetchPage(string url) {
    Response r = await http.get(url)    // pauses here; the thread does other work meanwhile
    return await r.readBody()
}

Future<string> a = fetchPage("a")          // both downloads start now
Future<string> b = fetchPage("b")
List<string> pages = await all([a, b])     // wait for both

string page, Error err = await fetchPage("c")  // wait for one: the page, or the error
if err
    print("Error: {err.message}")
```

#### 4.9 Immutable data and thread-local storage

| Way | What it is | In Fusion |
|---|---|---|
| Immutable data | Can't change after it is made - any number of threads may read it | Share a readonly value (D.028); `const` (D.112) |
| Thread-local storage | Each thread its own copy - nothing to share | A thread holds no state; variables made in `run { }` are its own; a true thread-local only in `unsafe` ([3.17](#317-a-thread-holds-no-state)) |

#### 4.10 Cancellation / interrupt

Asking a running thread to stop - cooperative: it checks at safe points and stops cleanly. In Fusion's
design: the `check interrupt` block after a loop (Task 56, [3.12](#312-interrupts-shutdown-transactions)).

---

## 5 What is built

| Item | Status |
|---|---|
| Keywords `service`, `go`, `async`, `await`, `Unique`, `Shared`, `Weak` | Reserved (src/lexer/keywords.py) - nothing parsed |
| `<-` | Read by the lexer only |
| Everything in sections 3 and 4 | Not built - FEATURES Task 42 (services), Task 49 (Lang modules), Task 56 (check) |

---

## 6 To settle

Found while gathering (2026-11-10, Task 51.5a step 2). The user's answers (2026-11-10) are provisional,
subject to change - PROPOSED rows in Decisions.md (D.125-D.132); they stay PROPOSED until threads are
built (user, 2026-11-11). The earlier spec text is gone from this file (git keeps it): what still held
moved into sections 1, 3 and 4.

| # | Subject | What clashed | The user's answer (provisional) | Now in |
|---|---|---|---|---|
| 1 | Mutex / `using lock { }` | In normal code, unsafe only, or Lang modules only? | Only inside `unsafe`, and only with locks switched on in `fusion.toml` (off by default) - it may cause deadlocks and races; `Lang.C.Fusion` may use `unsafe` for it | 4.2; D.125 |
| 2 | Channels | When a channel, when `service(s).send(x)` | A channel is a named mailbox in a service; every service has one default mailbox with no name; named channels for many threads with special work; an interrupt channel; outbound channels | 3.14; D.126 |
| 3 | `async` / `await` | `async` at a call (D.068) or `async function` + `await` | Both forms | 4.8; D.127 |
| 4 | files/Concurrency_Traps.md | "An implicit atomic lock" for arrays | An array uses a temporary service, like every collection (D.057) | fixed there |
| 5 | files/Ownership.md truth table 5 | Strings called "immutable" | Immutable only when `const`; otherwise like an object - copied freely, changed by two or more threads through a temporary service | fixed there; D.128 |
| 6 | The showcase section 18 | Outdated, no `service` | A task to rewrite it, with the new keywords | FEATURES 42.40 |
| 7 | The earlier spec text | Lock ordering; the old threading hierarchy | The compiler makes an automatic service; a developer may still lock (4.2) or write a service; lock ordering only with locks. Both hierarchies kept: levels and the family tree | 3.11, 4.2; D.129 |
| 8 | Thread-local storage | Not designed | A thread holds no state - it uses the service's variables; variables made in `run { }` are its own; a true thread-local only in `unsafe` | 3.17; D.130 |
| 9 | Condition variables | Wanted at all? | In a service: the parent holds the worker's channel, checks it, wakes the worker - to be designed further | 3.16; D.131 |

Answered 2026-11-10 (provisional):

| # | Question | Answer | Now in |
|---|---|---|---|
| a | Who may send to the interrupt channel | Only the OS; threads send only messages / requests; the service or main thread passes the interrupt on to each pool and child | 3.14; D.132 |
| b | `exit loop` / `continue loop` in the service's handler | No - they belong to a loop's `check` block; the check is implicit. Shutdown not handled: terminated and released at the end of its block; Pause: suspended; others: nothing | 3.14; D.132 |
| c | The syntax of named channels | A `Channel` interface and a `ChannelType` enum (INBOUND, OUTBOUND) - pseudo code; to be designed after checking other languages | 3.14; 42.34 |
| d | The kinds of threads | Names are suggestions, perhaps an enum; the compiler uses the thread ID; named channels for complex cases only | 3.15 |
| e | The parent's rules | Can't be set before threads work; baseline data from other languages first, then tuned. A worker stays awake while it has tasks, sleeps when none are left or on Shutdown | 3.16, 3.18; 42.36 |

[< 090 Memory](090-Memory.md) | [Index](index.md) | [110 Generics >](110-Generics.md) <!-- nav -->
