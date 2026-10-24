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

`service` is a **contextual** keyword, as `error` is: a variable may still be named
`service`. It may become a full keyword later.

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
4. **Several steps as one:** `service(x).run { ... }`, or a method of the class, runs as one
   step.
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
| `service(name).run { ... }` | Runs several steps as one indivisible step |
| `async` | Sends a request without waiting for its reply |
| `service(a, b, ...) T unit = ...` | One unit owning several services (after version one) |

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
resource_as_service = true     # files, sockets, pipes and databases are services
max_unit_warn = 5              # service(a, b, ...) with more names: a warning
max_unit = 32                  # more than this: a compile error

[concurrency.defaults]         # only the prime settings
mailbox = 12
when_full = "WAIT"             # WAIT | ERROR
scheduler = "IMMEDIATE"        # IMMEDIATE | BATCHED | the name of a custom scheduler
rule = "HIERARCHY"             # HIERARCHY | the name of a custom rule
priority = "5.4.1"             # high 5, medium 4, low 1 in 10 - or custom shares
worker_thread_type = "AUTO"    # AUTO (the compiler chooses) | SINGLE | SHARED
thread_pool = 8                # workers in the shared pool

[concurrency.timeouts]         # example timeouts the program can use, and override per thread
database_query = "30s"
database_connect = "30s"
http_request = "100s"
socket_read = "60s"
file_lock = "5s"

[concurrency.traps]            # warning | error
two_resources = "warning"
shared_variable = "warning"
missing_timeout = "error"

[concurrency.machine.min]      # embedded, or memory unknown: the lowest settings
default_pool_size = 1
default_mailbox = 4
[concurrency.machine.small]    # used below 8 GB
when_memory_below = "8GB"
default_pool_size = 2
default_mailbox = 12
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

## Not decided yet

- Units (`service(a, b, ...)`), after version one.
