# The `service` keyword

The reference for Fusion's `service` design: what it is, how it is used, and every setting.
The background (the traps, principles and other languages) is in `Concurrency.md`, with an
overview in `Concurrency_Traps.md`. The status is tracked in `FEATURES.md` Task 42.

**Status: designed, not built.** Version one was agreed on 2026-10-24, and the settings
on 2026-10-24 (user).

---

## What it is

`service` marks state that **several threads share**. One owner looks after it, so changes
from different threads can never collide. It works on variables, structs and class objects:

```fusion
service int counter = 0                     // a variable
service Person person = Person("Ada")       // a struct
service Car honda = Honda(Color.Black)      // a class object
```

`service` is a **keyword** (reserved since Task 46, 2026-10-29): it can't be used as the name
of a variable, field, function or parameter - write `svc`, `server`, `api` and so on instead.

## The five rules (version one)

1. **One owner.** Each statement or method call on a service is one indivisible step.
   Anything read out of it is a **copy**. Copying a service variable gives another
   **handle** to the same service.
2. **The compiler decides how it runs** unless `WorkerThreadType` says otherwise:
   - used by one thread only: a plain variable, at no cost;
   - a simple value such as `int`: CPU atomic instructions;
   - anything else: a queue of requests served by worker threads.
3. **Code runs in order.** After `counter += 1`, `print(counter)` shows the new value. To
   not wait for a reply, write `async`. A service finishes one request before it starts the
   next (it is not re-entrant).
4. **Several steps as one:** `service(x).run { ... }` is a one-time operation, carried out
   where it is written. The block says which steps form one atomic operation. Several `run`
   blocks can be written in different places, but the service carries out only one
   operation at a time. A method of a service class works the same way.
5. **A timeout means the caller stopped waiting**, not that the work was undone. Every
   request ends as **completed**, **failed**, **timed out** (its effects may still happen),
   or **cancelled**.

## Where a service is created

- Only for state that **several threads** read or write. Its job is to keep the operations
  atomic, especially when several values must change as one unit.
- **Outside loops:** as a class field, or as a variable in a function.
- **The parent thread creates it; its child threads use it.** A child may create its own
  service for its own children, then send results up to the parent's service.
- The compiler warns when no other thread ever uses a service.

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

## Using a service

| Form | What it does |
|---|---|
| `service <type> <name> = value` | Declares a service |
| `service(name).Setting = value` | Changes a setting. Only the thread that created the service may do this |
| `service(name).run { ... }` | A one-time atomic operation, carried out where it is written; the service runs one operation at a time |
| `service class Name { ... }` | Every object of the class is a service, and each method is one atomic step (advanced) |
| `async` | Sends a request without waiting for its reply |
| `service(a, b, ...) group` | Groups two or more variables into one service (see "Group services"; after version one) |

```fusion
service(account).run {
    if account.balance >= 800 {             // the check and the change are one step:
        account.balance -= 800              // two withdrawals can't both pass the check
    }
}
```

---

## Prime settings

These are the main settings. Each has a default, and `[concurrency.defaults]` in
`fusion.toml` can change the default for the whole project (except `final` and `run`, which
are code).

| Setting | What it does | Values | Default |
|---|---|---|---|
| `Mailbox` | How many requests can wait in the queue | a number | 12 |
| `WhenFull` | What happens when the queue is full | `Full.WAIT` (the sender waits), `Full.ERROR` (`QueueFullError`) | `WAIT` |
| `Timeout` | How long a caller waits for a request | a duration (`5s`) | per kind of resource (see "Example timeouts") |
| `final` | Extra clean-up code when the service goes out of scope; leaving scope always releases everything | a block | none |
| `Scheduler` | The order requests are carried out in | `IMMEDIATE`, `BATCHED`, or a custom scheduler | `IMMEDIATE` |
| `Priority` | How soon its work runs, as shares of the turns | `"5.4.1"` (high 5, medium 4, low 1 in 10), or custom shares | `"5.4.1"` |
| `Rule` | Who wins when two threads want the service | `HIERARCHY` (the senior thread), or a custom rule | `HIERARCHY` |
| `WorkerThreadType` | Who does the service's work | `AUTO`, `SINGLE`, `SHARED` (below) | `AUTO` |
| `ThreadPool` | The pool of worker threads that serves it (`SHARED`: the pool it shares; `SINGLE`: its own pool) | a pool, `ThreadPool(10)` | the program's shared pool |
| `run` | Runs several steps as one (a function, not a value) | a block | - |

#### WorkerThreadType

This is set **per resource**:

```fusion
enum WorkerThreadType {
    AUTO        // the default: Fusion chooses, and may change its choice as the load changes
    SINGLE      // dedicated, self-contained workers that serve only this resource
    SHARED      // shared workers from a specific ThreadPool, also serving other services
}
```

- **`AUTO`** (the default) decides by how the resource is used. When more threads start
  reading it, it becomes `SHARED`. When the work is heavy, it becomes `SINGLE`.
- **`SINGLE` does not mean one thread.** It means the workers are dedicated to this
  resource and to nothing else. That can be one thread, or its own ThreadPool managing the
  resource. It suits a heavy resource that should never wait for a free worker, such as a
  log file written all the time, a device, or a large database.
- **`SHARED`** suits most services. Many services share a few workers, so 100,000 services
  don't need 100,000 threads.
- The developer can always set it by hand, per resource, or project-wide in `fusion.toml`
  (`worker_thread_type`).

```fusion
service File log = File.open("app.log")
service(log).WorkerThreadType = WorkerThreadType.SINGLE

service(log).ThreadPool = ThreadPool(2)                     // SINGLE: its own pool of 2

ThreadPool dbPool = ThreadPool(10)
service Database db = Database.open("connection string")
service(db).WorkerThreadType = WorkerThreadType.SHARED
service(db).ThreadPool = dbPool
service(db).Timeout = 30s
```

## Secondary settings

These are for advanced tuning, and come after version one. Most can also have a default in
`fusion.toml`.

| Setting | What it does |
|---|---|
| `Coalesce` | A full queue merges pending requests into the newest one, where that is safe (position updates, never withdrawals) |
| `BatchSize`, `BatchDelay` | How many requests a `BATCHED` scheduler takes, and how long it waits to fill a batch |
| `MaxParallelReads` | How many reads may run at the same time |
| `IdleTimeout` | Release the worker when the service is unused for this long |
| `OnError` | When its code fails: restart, stop, or report to the parent |
| `RestartLimit` | At most n restarts per period |
| `Retry` | How a failed request is retried |
| `Shutdown` | At the end: finish the queue, or drop it |
| `WarnAt` | Warn when the queue is this full (for example 80%) |
| `Snapshot` | Readers get a copy instead of sending one request per read |
| `Lifetime` | The scope, until it is closed, or the whole program |
| `Name` | A name for tools and logs |
| `Trace` | Profiling on |
| `Affinity` | Pin its worker to particular CPU cores |
| `MemoryLimit` | The most memory the service may use |
| `Access` | Which threads may send to it |

---

## Durations

Times are written as **duration literals**. For now each one is an `int` holding
**milliseconds**. They can also be read as text, from a string or a `fusion.toml` value.

| Written | Means (milliseconds) |
|---|---|
| `500ms` | 500 |
| `5s` | 5000 |
| `2min` | 120000 |
| `1h` | 3600000 |

```fusion
service(person).Timeout = 60s               // the same as 60000
int wait = toDuration("2min")               // 120000 - from text
```

A full time module comes later (FEATURES.md Task 43): hours, minutes, seconds,
milliseconds and nanoseconds, days, months and years, time zones, epochs, and calculations
with them.

---

## Settings in `fusion.toml`

```toml
[concurrency]
resourceAsService = true     # files, sockets, pipes and databases are services
maxUnitWarn = 5              # service(a, b, ...) with more names: a warning
maxUnit = 32                  # more than this: a compile error

[concurrency.defaults]         # only the prime settings
mailbox = 12
whenFull = "WAIT"             # WAIT | ERROR
scheduler = "IMMEDIATE"        # IMMEDIATE | BATCHED | the name of a custom scheduler
rule = "HIERARCHY"             # HIERARCHY | the name of a custom rule
priority = "5.4.1"             # high 5, medium 4, low 1 in 10 - or custom shares
workerThreadType = "AUTO"    # AUTO (the compiler chooses) | SINGLE | SHARED
threadPool = 8                # workers in the shared pool

[concurrency.timeouts]         # example timeouts the program can use, and override per thread
databaseQuery = "30s"
databaseConnect = "30s"
httpRequest = "100s"
socketRead = "60s"
fileLock = "5s"

[concurrency.traps]            # warning | error
twoResources = "warning"
sharedVariable = "warning"
missingTimeout = "error"

[concurrency.machine.min]      # embedded, or memory unknown: the lowest settings
defaultPoolSize = 1
defaultMailbox = 4
[concurrency.machine.small]    # used below 8 GB
whenMemoryBelow = "8GB"
defaultPoolSize = 2
defaultMailbox = 12
```

#### Example timeouts

`[concurrency.timeouts]` holds **example** values that a program can use and override. Each
thread can choose its own. For example, one thread can use a `file_lock` of `5s` for quick
updates while another uses `30s` for big files:

```fusion
service(log).Timeout = config.concurrency.timeouts.file_lock    // 5s from fusion.toml
service(archive).Timeout = 30s                                  // this one needs longer
```

The values started from what other systems use (`Concurrency.md` 3.7).

#### Which value wins

| Level | Where | Strength |
|---|---|---|
| 1 | `fusion.toml`. Without one, Fusion's built-in defaults, which are the values shown above | Lowest |
| 2 | The program's own defaults | Medium: overrides level 1 |
| 3 | `service(x).Setting` in the code | Highest: it directly controls that service |

Settings that fit the machine (the `[concurrency.machine]` levels) tune these defaults.
They never stop the program from running, and a machine that matches no level gets `MIN`.

---

## Custom schedulers, rules and priorities

Each is a class with one method (agreed 2026-10-24; more in `Concurrency.md` 3.8).

```fusion
class WritesFirst implements Scheduler {
    // given what is waiting, return what to run next (several = run together)
    List<Request> function next(List<Request> waiting) {
        List<Request> writes = waiting.filter((Request r) : r.isWrite)
        if writes.len() > 0 {
            return [writes[0]]                  // one write at a time, before any read
        }
        return waiting                          // no writes: all reads together
    }
}

class PaymentsFirst implements ContentionRule {
    // return the thread that goes first; the other one waits or releases
    Thread function decide(Thread a, Thread b) {
        if a.name == "payments" {
            return a
        }
        if b.name == "payments" {
            return b
        }
        return Rule.HIERARCHY.decide(a, b)      // otherwise, the default
    }
}

service(log).Scheduler = WritesFirst()
service(db).Rule = PaymentsFirst()
service(db).Priority = "6.3.1"                  // custom shares: high 6, medium 3, low 1
```

## Decided (2026-10-24)

- **Coalesce** is a secondary setting, not part of version one.
- **Custom schedulers, rules and priorities** use the syntax above.
- **`WorkerThreadType`** defaults to `AUTO`: `SHARED` as more threads read the resource,
  `SINGLE` when its work is heavy. The developer can set it by hand.

## Service classes (for advanced use)

Agreed 2026-10-24 (user). A **class** can be declared with `service`. Every object made from
it is then a service, and **each of its methods runs as one atomic step**. This is for
more complex operations that need several steps on the same state. It suits advanced
developers who want to control exactly how the service runs; for everyday code, a group
service or `run` is enough.

```fusion
service class CarPerson {
    Person person
    Car car

    constructor(Person person, Car car) {
        this.person = person
        this.car = car
    }

    void function buyCar() { ... }              // each method is one atomic step
    void function registerCarWithGov() { ... }
    void function buyInsurance() { ... }
}

CarPerson carPerson = CarPerson(ada, honda)     // a service, because its class is one
service(carPerson).WorkerThreadType = WorkerThreadType.SINGLE    // its own thread, or
service(carPerson).ThreadPool = ThreadPool(4)                    // its own pool
carPerson.buyCar()                              // requests, carried out one at a time
carPerson.registerCarWithGov()
carPerson.buyInsurance()
```

- **Members are grouped automatically:** every field of a service class (here `person` and
  `car`) is part of the object's group service, so calls on them are routed through it.
- **`service` in front is optional:** `service CarPerson carPerson = CarPerson(ada, honda)`
  is allowed and does nothing more, because the class is already a service. It only shows
  readers that this is a service.
- **Not in a loop:** creating service-class objects inside a loop is not recommended (a
  warning).
- **How it runs is up to the developer:** shared workers (`SHARED`), or its own thread
  or pool (`SINGLE`), with any of the prime settings.
- **Compared with a group:** a group (`service(person, honda) carPerson`) is quick and needs
  no class. A service class gives the operations names and keeps their code in one place.
- **In other languages:** this is the closest part of Fusion to a Swift `actor` or an
  Erlang `gen_server`.

## Group services (units)

Agreed 2026-10-24 (user). It will be built after version one.

A **group service** makes two or more related variables into **one** service, so they can be
changed together atomically:

```fusion
service(person, honda) carPerson             // person and honda are now one unit: carPerson
```

The form is `service(<members>) <group name>`. There is no type and no constructor. After
this line, every read, write or call on `person` or `honda` is routed to `carPerson`'s
queue, and its worker carries it out atomically.

#### The rules

1. **The group does the work.** `carPerson` handles every request that reads, writes or
   calls `person` or `honda`, and queues the requests automatically. Custom code that needs
   several members at once runs inside the group, as one step:

   ```fusion
   print(person.name)                         // routed through carPerson's queue
   service(carPerson).run {
       honda.owner = person.name              // both members change in one step
       person.car = honda.model
   }
   ```

2. **Calls are re-routed automatically.** While the group exists, a request sent to a member
   (`person.name`) is re-routed to the group as a message and queued. The group carries it
   out atomically, and the result returns to the calling thread when it is done. Calling
   through the group (`carPerson.getPerson().getName()`) is also routed to the group's
   queue, and works the same way.

   ```fusion
   string a = person.name                     // re-routed to carPerson, queued, then returned
   string b = carPerson.getPerson().getName() // the same, through the group
   ```

   **Release:** when `carPerson` goes out of scope, `person` and `honda` are released, and
   other threads use them directly again.
3. **Members are plain variables.** A member may itself be a service, which keeps its own
   worker (`SINGLE` or `SHARED`) for its own requests.
4. **One owner - a hard rule.** A variable belongs to at most one service or group at a
   time. Putting it in a second one is a **compile error**. While `person` and `honda` are
   grouped, the group is their only owner, and they can't be shared with anything else.
5. **Nesting is allowed.** A group may contain another group, as long as no variable breaks
   rule 4. Like nested loops and `if`s, deep nesting gets harder to follow.
6. **Each service keeps its own settings.** The group's settings belong to the group;
   members that are services keep theirs. A group can't take over a log file's or a
   database connection's settings. The group's `Timeout` must still be long enough for its
   members' work, such as a slow SQL query; choosing it is the developer's job.
7. **Undone where possible.** If an operation fails halfway, its changes are undone where
   that is possible:
   - a change to a value is undone by its opposite (`balance + 1` by `balance - 1`);
   - a database operation is rolled back.

   What has left the program can't be undone: a line written to a log file, or data sent
   on a socket. (To be discussed in depth once a working system exists.)
8. **Formed before use.** A group is created before any thread uses its members, like a
   database connection: create the group, change its settings if needed, then let the
   calls and child threads go through it, and finally release it.

   ```fusion
   service(person, honda) carPerson           // 1. create
   service(carPerson).Timeout = 30s           // 2. settings, if needed
   person.buyCar()                            // 3. calls go through carPerson automatically
                                              // 4. released at the end of the scope
   ```

9. **Not only in functions.** A class method can create a group from the class's fields.
   Any thread can then use the class safely.
10. **Limits:** a warning above `max_unit_warn` names (default 5) and a compile error above
    `max_unit` (default 32), both in `fusion.toml`. These are everyday defaults that a
    project can change.

## Ownership in a service (agreed 2026-10-31)

A service is the one writer of what it holds. These rules come from the ownership design
(`Ownership.md`; the record: `Notes/Ownership_Decisions_2026-10-31.md`). FEATURES.md 42.18.

| # | Rule | Why |
|---|---|---|
| S1 | **The worker is the only writer** - nothing outside the service holds a reference to its inside | one writer |
| S2 | **The service owns its value; a request borrows it** for the call - to change it or only read it, as the called function's signature says | the owner / borrower model |
| S3 | **Nothing escapes a request** - it can't return, store or capture a reference to the inside (`byVal` copies it out) | no back door around the worker |
| S4 | **Readers in parallel** - readonly requests may run together; a changing request runs alone. `Readers = PARALLEL \| SERIAL` | `show` and `log` |
| S5 | **Temporary services** - made when two or more threads use one value, gone when the last ends; ownership comes back (Ownership.md section 6) | the user's design |
| S6 | **What goes into a request** - borrowed for the request only, moved in (send), or copied | a borrow never outlives its owner |
| S7 | **A thread using two or more resources gets a group service** (written, or made by the compiler); waiting inside a request for another thread's result is an error | no deadlocks (P2) |
| S8 | **Plain counts inside a service**; only handles use atomic counts | speed - an object inside is never reached by two threads |
| S9 | **The thread-boundary table** - what may reach another thread (Ownership.md truth table 5) | the compiler check |
| S10 | **A `Service` interface** that every kind of service implements (below) | program to an interface |

**Several resources** (Ownership.md section 7, D.077): a **service** manages one resource, a
**group service** several. A thread that uses two or more resources - a database and its
log - gets a group service: written by the developer ("Group services" below) or made by the
compiler. It owns them while its requests run, then each variable owns its value again.

## The Service interface (agreed 2026-10-31)

Code to an interface: `Service` is the interface; each kind of service implements it.
FEATURES.md 42.21. Needs interfaces (Task 32.5).

```fusion
interface Service<T>                    // T: the kind of request
    void function send(T request)       // a caller puts a request in the mailbox
    T function fetch()                  // the worker fetches its next request (waits as Wait says)
    void function start()
    void function stop()
    ServiceState function state()
    int function waiting()              // requests in the mailbox

class BasicService implements Service      // a mailbox and one worker thread (version one)
class SharedService implements Service     // the temporary one (Ownership.md section 6)
class FileService implements Service       // one writer per file
class DatabaseService implements Service   // one connection, queries in turn
class HotPathService implements Service    // a dedicated thread that never sleeps (below)

Service log = BasicService() { ... }
```

| Written | Implementation behind `service(x)` |
|---|---|
| `service T x = ...` | `BasicService` (one worker thread) |
| two or more threads use a plain variable | `SharedService` (made by the compiler) |
| `hotpath service T x = ...` | `HotPathService` |
| a file / database as a service (42.5) | `FileService` / `DatabaseService` |

Settings are checked against the implementation: `service(trading).Core` exists only on a
`HotPathService`.

## Hot-path services (`hotpath service`, agreed 2026-10-31)

A hot path is a **dedicated thread that never sleeps**: it keeps one processor busy all the
time - a CPU core, or a CPU core feeding a GPU or a chip on some hardware. FEATURES.md
42.23-42.24.

```fusion
hotpath service Trade trading = Trade("BTC-USD") {   // service(trading) is a HotPathService
    service(trading).Core = 3                  // pinned to CPU core 3
    service(trading).Ring = 4096               // input slots, a power of 2
    service(trading).Producers = SINGLE        // one feed: a lock-free single-producer ring
    service(trading).WhenFull = Full.COALESCE  // never WAIT (a compile error)
    service(trading).Wait = Wait.SPIN          // never sleeps
    service(trading).Budget = 50ns             // a warning when a step takes longer
    trading.preparePools(10000)                // allocating is fine here, in the set-up
}

struct Tick                                    // ring messages: fixed-size values
    money price                                // Task 47 - a long of cents, no heap
    int quantity
    fixed(16) string symbol                    // at most 16 characters, no heap (47.5)

hotpath void function step(Tick t)             // the checks without the thread (game frames, audio)
```

The set-up block is form B (Task 32.2d): it runs once, before the loop starts, so it may
allocate.

#### H: what the compiler checks (the worker and everything it calls)

| # | Rule | Why |
|---|---|---|
| H1 | no allocating - no new objects, no growing Lists / Maps, no building strings | `malloc` costs 20-100 ns, unpredictably |
| H2 | no blocking - no locks, I/O, `print`, sleeping or waiting for a reply | one block costs microseconds |
| H3 | no count changes - values, or objects the hot path owns (moved in, never `shared`) | an atomic count is 5-20 ns |
| H4 | no unknown calls - a function value must be `hotpath` itself | the compiler can't check what it can't see |
| H5 | no unbounded loops inside one step (a setting) | each step finishes in its budget |
| H6 | errors stay inside - an error counter or ring; the loop never stops | it can never stop |
| H7 | ring messages are fixed-size values | copied into reserved slots |
| H8 | only the set-up block may allocate | the lifecycle below |
| H9 | sizes come from the hardware - ring and message sizes, `fixed` lengths: constants from settings or read from the device at set-up (cache line 64 / 128 bytes, NIC descriptors, a GPU command buffer) | fixed, never grown |

#### T: what happens while it runs

| # | Feature |
|---|---|
| T1 | a dedicated thread pinned to a core, real-time priority where the OS allows it |
| T2 | an input ring - one or many producers, a power-of-2 size, counters padded to the cache line (no false sharing) |
| T3 | wait: `SPIN` (default - never sleeps) or `YIELD`; `PARK` is not allowed on a hot path |
| T4 | memory locked and touched at set-up (no page faults while running); huge pages optional |
| T5 | no replies - results go to other rings (an order gateway, a logger) |
| T6 | a latency histogram (p50 / p99 / p99.9) and the `Budget` warning, from the CPU's cheap timer |
| T7 | a watchdog thread that notices a stall |
| T8 | lifecycle: set-up (may allocate) -> warm-up (fake data, so code and data are in cache) -> running (H1-H9) -> drain -> stop |

**Settings per hot-path service:** `Core`, `Ring`, `Producers` (SINGLE / MULTI), `WhenFull`
(DROP / OVERWRITE / COALESCE / ERROR - never WAIT), `Wait` (SPIN / YIELD), `Budget`,
`Priority` (REALTIME), `Prefault`, `WarmUp`. Project defaults: `fusion.toml` `[hotpath]`
(files/showcase/fusion.toml).

#### Where a hot path is justified

| Processor kept busy | What the hot path does | Justified? |
|---|---|---|
| CPU (trading) | market data, matching engines, risk checks before an order goes out | yes |
| GPU | builds and submits command buffers; feeds a persistent kernel's ring | yes - engines, VR, GPU risk |
| FPGA (trading cards, signal processing) | reads and writes the card's DMA rings | yes |
| SmartNIC / DPU / network card | polls receive and send rings (DPDK style) at 10-100 Gbit/s | yes |
| DSP chip, audio interface | keeps sample buffers full - a gap is heard | yes |
| software-defined radio | streams millions of samples a second; 5G radio slots | yes |
| NPU / TPU | keeps inference batches flowing so the chip never waits | yes, at scale |
| video encoder chip (NVENC, Quick Sync), capture cards, camera image processors | feeds frames, collects packets before a buffer overflows | yes |
| NVMe storage (SPDK) | polls completion queues instead of waiting for interrupts | yes - storage engines |
| motor drive / microcontroller (EtherCAT, CAN), LiDAR, radar, PLC I/O | control loops at 1-10 kHz that must not miss a cycle | yes (hard real-time also needs certification) |
| telemetry ingestion, real-time bidding | millions of events a second | yes |
| a web server, a UI, batch jobs | - | **no** - a BasicService |
| a game frame, an audio callback | sleeps between turns | `hotpath function` - the checks without the thread |

## Not decided yet

- How "undone where possible" (group rule 7) works in detail.
