# Concurrency in Fusion - terms and traps

Doing several things at once: what the words mean, and what goes wrong.

**None of this is built yet.** The code uses Fusion syntax as designed in
`files/fusion-language-spec.md` ("Threading and Concurrency Model", "Async/Await Pattern")
and `files/showcase/Fusion_showcase.fusion` section 18. Names such as `ThreadPool`,
`Atomic<T>` and `Semaphore` are suggestions until concurrency becomes a task.

- **Section 1** explains each term, with a short example.
- **Section 2** shows the common traps: each with code that has the bug, and how it is
  normally solved.
- **Section 3** collects possible ideas for Fusion: the fixes in general form, a model of
  threads and resources run as services, ten principles written like design patterns, and
  real-world cases with links.
- **Section 4** compares how C, C++, Java, C#, Go, Python, Rust, Erlang and Node.js handle a
  million requests and races, deadlocks and freezes.

---

## Section 1 - Terms

#### Concurrency vs. parallelism

- **Concurrency:** several tasks are in progress during the same period. One CPU core can
  switch between them, like a cook stirring three pots in turn.
- **Parallelism:** several tasks run at the same instant on different cores, like three cooks.

Concurrency is about structure (dealing with many things); parallelism is about speed (doing
many things at once). A concurrent program runs in parallel when there are cores free.

#### Process

A running program, with its own memory, which no other process can see. It is heavy to
start, and well isolated: when one crashes, the others keep running. Processes talk through
pipes, sockets or files.

```fusion
Process proc = Process.start("python", ["script.py"])   // another program, its own memory
string output = proc.readOutput()                       // talk to it through its output
int code = proc.exitCode
```

#### Thread

A separate path of execution inside one process. All threads of a process share its memory,
which makes them fast to talk to each other, and also dangerous (Section 2). Starting a
thread is cheap compared with a process, but not free (about 1 MB of stack each).

```fusion
void function count(string name) {
    for i in range(0, 3) {
        print("{name}: {i}")
    }
}

void function main() {
    go count("A")          // runs on a new thread
    count("B")             // main keeps going at the same time
}                          // the output of A and B can interleave in any order
```

#### Main thread / main event thread

The thread that starts the program and runs `main`. In a desktop app it also runs the
**event loop**: it waits for clicks and key presses and handles them one at a time. Only
this thread may change the user interface. A long job on it freezes the window, so long
jobs go to another thread, and their result is sent back to it.

The main thread doesn't control other threads by itself. It owns the thread pool or
ThreadManager that does. When `main` ends, the program ends, and the other threads end with it.

#### Thread pool / ThreadManager

A fixed set of threads that wait for work. You submit a **task** (a job) and a free thread
runs it. This avoids the cost of starting a thread per job, and it limits how many run at
once (usually one per CPU core).

```fusion
ThreadPool pool = ThreadPool(4)                 // 4 threads waiting for work
for file in files {
    pool.submit(func() : compress(file))        // each job runs on any free thread
}
pool.waitAll()                                  // wait until every job is done
```

#### Task / job

One unit of work given to a pool or to an async runtime. A task is not a thread. A thousand
tasks can be shared out over four threads.

#### Async / await

A way to wait without blocking a thread. It is mostly used for I/O: downloads, files,
databases.

- An `async` function can pause in the middle. It usually runs on the **same** thread,
  not a new one.
- `await` pauses it until a result is ready. While it is paused, the thread is free to do
  other work. When the result arrives, the function carries on from where it paused.

```fusion
async string, Error function fetchPage(string url) {
    Response r = await http.get(url)    // pauses here; the thread does other work meanwhile
    return await r.readBody()
}

async void function main() {
    string a = await fetchPage("https://example.com/a")
    print("{@1} characters", len(a))
}
```

**Rule of thumb:** use threads for heavy computing (many cores busy), and async for waiting
(one thread juggling many waits).

#### Future / promise

A value that will exist later: what calling an async function gives back before it has
finished. `await` turns it into the real value. Waiting for several at once:

```fusion
Future<string> a = fetchPage("a")          // both downloads start now
Future<string> b = fetchPage("b")
List<string> pages = await all([a, b])     // wait for both - about the time of the slower one
```

#### Channel

A pipe that carries values from one thread to another. `send` puts a value in, and
`receive` takes one out, **waiting** until one arrives. This is how threads hand work over
without sharing variables ("share memory by communicating", as in Go).

- An **unbuffered** channel makes the sender wait until a receiver takes the value.
- A **buffered** channel (with room for N values) lets the sender run ahead until it is
  full.
- Closing a channel tells the receivers there is nothing more to come.

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

#### Mutex (lock)

"Mutual exclusion": only one thread at a time may hold it. Code between locking and
unlocking is a **critical section**. A second thread that tries to lock waits until the
first one unlocks. `using lock { }` unlocks automatically at the end of the block, even when
an error occurs.

```fusion
Mutex lock = Mutex()
int balance = 100

void function withdraw(int amount) {
    using lock {                       // locked here
        if balance >= amount {
            balance -= amount
        }
    }                                  // unlocked here, always
}
```

#### Read-write lock

Many readers at once, or one writer alone. This is useful when data is read often and
changed rarely, such as a settings table.

```fusion
ReadWriteLock rw = ReadWriteLock()
using rw.read() {
    print(settings["theme"])           // many threads may read together
}
using rw.write() {
    settings["theme"] = "dark"         // a writer waits until every reader is done
}
```

#### Semaphore

A counter of permits: at most N threads may be inside at once. A mutex is a semaphore with
one permit.

```fusion
Semaphore downloads = Semaphore(3)     // at most 3 downloads at the same time
using downloads {
    fetch(url)
}
```

#### Atomic value

A single variable whose operations (add, swap, compare-and-set) can't be interrupted
halfway, so they need no lock. Atomics are fast, but they protect one variable only, not
a group of variables that must change together.

```fusion
Atomic<int> hits = Atomic<int>(0)
hits.add(1)                            // safe from any number of threads
```

#### Condition variable / signal

A way for a thread to sleep until another thread says "something changed" (for example, "the
queue is no longer empty"). Channels are built on this. Most programs use a channel instead.

#### Thread-safe

Code or data that gives correct results when many threads use it at once. A plain `List`
usually is not thread-safe; a channel is.

#### Immutable data

Data that can't change after it is created. Any number of threads can read it safely with
no locks, because nobody can write to it. This is the simplest way to share data.

#### Thread-local storage

A variable where each thread has its own copy, so there is nothing to share and nothing to
lock.

#### Cancellation / interrupt

Asking a running thread or task to stop. It is **cooperative**: the thread checks for the
request at safe points and stops cleanly. Killing a thread from outside can leave locks held
and data half-written. In Fusion's design this is the `check interrupt` block after a loop.

```fusion
for item in hugeList {
    process(item)
} with {
    check interrupt(signal, data) {
        if signal == InterruptSignal.Shutdown {
            saveProgress()
            exit loop
        }
    }
}
```

#### Context switch

The operating system pausing one thread and running another on the same core. It happens
thousands of times a second, at **any** point, including in the middle of `count += 1`. That
is the root of most traps below.

---

## Section 2 - Traps

Each trap has a short description, code that has the bug, and how it is normally solved.

Concurrency bugs are hard because they are **timing-dependent**. The code may work a
thousand times and fail on the next run, or only on a customer's faster machine. They often
disappear when you add a `print` to look for them ("heisenbugs"), so preventing them by
design matters more than testing for them.

#### 1. Race condition (data race)

Two threads change the same variable at once. `count += 1` is really three steps (read, add,
write). If two threads read 5 at the same time, both write 6, and one increment is lost.

```fusion
int count = 0

void function addMany() {
    for i in range(0, 100000) {
        count += 1                     // read, add, write - another thread can cut in between
    }
}

void function main() {
    go addMany()
    go addMany()
    waitForAll()
    print("{count}")                   // expected 200000, prints e.g. 137412, different every run
}
```

**Solved by**, from the simplest:
- don't share: each thread counts on its own, and the totals are added at the end;
- an atomic counter (`Atomic<int>`, `hits.add(1)`);
- a mutex around the change (`using lock { count += 1 }`);
- a channel: send each change to one thread that owns the counter.

Rust refuses to compile shared changes without one of these. Fusion could do the same in
strict mode.

#### 2. Check-then-act

Two steps that are each safe on their own, but not as a pair: the situation changes between
the check and the action.

```fusion
void function withdraw(int amount) {
    if balance >= amount {             // thread A checks: 100 >= 80, fine
                                       // thread B checks: 100 >= 80, fine
        balance -= amount              // A: 20 ... B: -60, the account is overdrawn
    }
}
```

The same happens with files ("if the file doesn't exist, create it") and maps ("if the key
is missing, add it").

**Solved by:** putting the check **and** the action in one critical section (`using lock`
around both), or by using a single operation that does both at once. Examples are
compare-and-set, `map.getOrAdd(key, value)`, and a create-file call that fails when the
file already exists.

#### 3. Deadlock

Two threads each hold one lock and wait forever for the other's lock. The program freezes,
uses no CPU, and gives no error message.

```fusion
void function transfer(Account from, Account to, int amount) {
    using from.lock {                  // thread A locks account 1 ...
        using to.lock {                // ... and waits for account 2
            from.balance -= amount     // thread B, transferring the other way, locked
            to.balance += amount       // account 2 and waits for account 1: both wait forever
        }
    }
}
// thread A: transfer(acc1, acc2, 10)    thread B: transfer(acc2, acc1, 5)
```

**Solved by:**
- **Lock ordering:** always take locks in one global order (for example, the lower account
  number first).
- Hold one lock at a time where possible.
- Locks with a timeout (`tryLock(timeout)`) that back off and retry.
- Channels instead of locks: one owner thread per account and no shared locks.

Some runtimes detect deadlocks while debugging. Go reports "all goroutines are asleep".

#### 4. Forgotten unlock

An early `return` or an error between lock and unlock leaves the lock held forever. Every
other thread then waits on it: a deadlock with one thread.

```fusion
void function save(Data d) {
    lock.lock()
    if not d.isValid() {
        return                         // the lock is never released
    }
    write(d)                           // an error here: never released either
    lock.unlock()
}
```

**Solved by:** never pairing lock and unlock by hand. Use a block that always unlocks:
`using lock { }` in Fusion's design, `lock` in C#, `with` in Python, or a guard object in
Rust and C++.

#### 5. Livelock

The threads are not blocked; they keep reacting to each other and get nowhere. It is like
two people in a corridor who both step aside the same way, again and again.

```fusion
// both threads: "if the other one wants the lock, politely let go and try again"
while not done {
    if other.wantsLock {
        release()                      // both release at the same time ...
        retry()                        // ... both retry at the same time, forever
    }
}
```

**Solved by:** waiting a **random** amount of time before retrying (backoff with jitter,
as network protocols do), or giving one side priority.

#### 6. Starvation

One thread never gets its turn: other threads keep taking the lock, or a low-priority thread
never gets a core.

```fusion
// 20 reader threads hold a read lock almost all the time:
using rw.read() {
    busyReading()
}
// the one writer waits for a moment with no readers - which never comes
using rw.write() {
    update()
}
```

**Solved by:** fair locks, which serve waiting threads in the order they arrived. Many
read-write locks also stop admitting new readers once a writer is waiting.

#### 7. Priority inversion

A high-priority thread waits for a lock held by a low-priority thread, and a medium-priority
thread keeps the low one from running. In effect the high-priority thread runs last. This
famously reset the Mars Pathfinder lander in 1997.

**Solved by:** **priority inheritance**: while a low-priority thread holds a lock that a
high-priority thread wants, it temporarily gets the high priority. Real-time operating
systems do this. It matters for Fusion's embedded and HIDL targets.

#### 8. Visibility: a change one thread never sees

For speed, CPUs and compilers keep values in registers and caches, and may reorder
instructions. Without synchronization, one thread's write may never become visible to
another.

```fusion
bool stop = false

void function worker() {
    while not stop {                   // the compiler may read stop once and loop forever
        work()
    }
}
// main thread, later:
stop = true                            // the worker may never notice
```

**Solved by:** sharing such flags only through something that synchronizes. That means an
atomic (`Atomic<bool>`), a lock, a channel, or a cancellation token. These add the
**memory barriers** that make a write visible. Never use a plain variable as a signal
between threads.

#### 9. Changing a collection while another thread uses it

A plain list or map is not thread-safe. If one thread adds while another loops, or two
threads add at once, the result can be lost items, duplicates, a crash, or corrupted memory.

```fusion
List<string> log = []

void function record(string msg) {
    log.add(msg)                       // two threads adding at once: one message lost, or a
}                                      // crash while the list grows its storage
// meanwhile another thread: for line in log { print(line) }
```

Fusion already raises a `ModifiedWhileLoopingError` when a single thread changes a list it is
looping over (Task 27.2e). Across threads the problem is worse, because the change can land
halfway through `add`.

**Solved by:**
- a concurrent collection (`ConcurrentMap`, `ConcurrentQueue`);
- a lock around every use;
- one owner thread, with the others sending it changes through a channel;
- copy-on-write: readers get an unchanging snapshot.

#### 10. Unbuffered channel with nobody receiving

On an unbuffered channel, `send` waits until another thread receives. If nobody ever does,
the sender waits forever. The same happens when you receive from a channel nobody sends to,
or when you forget to close it, so a `for n in channel` loop never ends.

```fusion
void function main() {
    Channel<int> ch = Channel.create<int>()
    ch.send(1)                         // waits for a receiver - there is none: frozen
    go reader(ch)                      // never reached
}
```

**Solved by:**
- starting the receiver before sending;
- buffered channels where it makes sense;
- the sender always closing the channel when it is done;
- a timeout on `send` and `receive`.

Go turns the "everyone is waiting" case into a clear crash message. Fusion could do the
same.

#### 11. Blocking inside async code

An async function runs on a thread shared by many tasks. A slow, blocking call inside it
(`sleep`, a synchronous file read, heavy computing) freezes **every** task on that thread,
not just this one.

```fusion
async void function handle(Request r) {
    string data = readText("big.log")       // blocking read: every other request waits too
    string summary = heavyAnalysis(data)    // seconds of CPU work on the shared thread
    await r.reply(summary)
}
```

**Solved by:**
- using the async versions of I/O (`await readTextAsync(...)`);
- moving CPU-heavy work to a thread pool and awaiting its result
  (`await pool.run(func() : heavyAnalysis(data))`).

#### 12. Forgetting `await`

Calling an async function without `await` starts it, but nothing waits for it. Its result,
and its **error**, are silently dropped, and the code after it runs too early.

```fusion
async void function saveAll() {
    saveToDisk()                       // missing await: carries on at once
    print("saved")                     // printed before saving finished - or when it failed
}
```

**Solved by:** compilers that warn when a future is ignored (C# and Rust do). Fusion could
make it a compile error unless the call is explicitly marked "run in the background".

#### 13. Sync-over-async deadlock

Code on the main (UI) thread waits **blocking** for an async task, but that task needs the
main thread to finish. Each waits for the other.

```fusion
void function onClick() {                       // runs on the main thread
    string page = fetchPage("a").waitResult()   // blocks the main thread ...
}                                               // ... and fetchPage needs the main thread to
                                                // continue after its await: frozen
```

**Solved by:** "async all the way". Make the caller async too (`await fetchPage("a")`),
and never block-wait on a future from the main thread.

#### 14. Errors lost in another thread

An error thrown on a background thread doesn't reach `main`'s try / catch. Depending on the
language, the thread dies silently, or the whole program stops with no context.

```fusion
void function main() {
    try {
        go importFile("data.csv")      // its FileNotFoundError happens on the other thread
    } catch e {
        print("never reached")         // this catch only covers starting the thread
    }
}
```

**Solved by:** having tasks return their result **or** their error, and collecting both
when you wait for them (`Spaceship s, err = await task`). Fusion's `T, Error` returns fit
this well. Pools and runtimes can also be given a handler that logs every uncaught error.

#### 15. Thread leaks and too many threads

Threads that are started and never end (waiting on a channel nobody closes, or looping
forever) build up until memory runs out. Starting one thread per request has the same
effect under load: 10,000 threads means about 10 GB of stacks and constant context
switching.

```fusion
for request in incoming {
    go handle(request)                 // one new thread per request, no limit
}
```

**Solved by:**
- thread pools with a fixed size;
- semaphores that limit how many run at once;
- async for I/O-bound work;
- giving every thread a clear way to end (closing channels, cancellation).

#### 16. Updating the UI from another thread

Most UI toolkits are not thread-safe. Changing a label or window from a background thread
gives random crashes or drawing glitches, or the toolkit throws an error.

```fusion
go downloadThen(func(string page) : statusLabel.text = "done")   // runs on the wrong thread
```

**Solved by:** sending the update back to the main thread, for example with
`mainThread.post(func() : statusLabel.text = "done")`. In C# this is `Dispatcher.Invoke`;
in Android it is `runOnUiThread`. An `await` on the main thread usually comes back to the
main thread on its own.

#### 17. Performance traps: contention and false sharing

These programs are correct, just slow.

- **Lock contention:** many threads queue for one busy lock, so 8 cores run like 1.
- **False sharing:** two threads update **different** variables that sit next to each
  other in memory, in the same 64-byte cache line. The cores keep taking the cache line
  away from each other.

```fusion
int[8] counters                        // one counter per thread, all in one cache line
// thread i: counters[i] += 1  - no race, but every write slows down every other core
```

**Solved by:**
- holding locks as briefly as possible (compute first, lock only to store);
- splitting one lock into several (one per bucket);
- per-thread counters that are combined at the end;
- padding hot variables to separate cache lines.

#### Summary - how most languages stay safe

| Approach | Idea | Languages |
|---|---|---|
| Don't share | Each thread owns its data; send it over channels | Go, Erlang, Fusion's recommended style |
| Don't change | Immutable data is always safe to share | Functional languages, Kotlin, Rust by default |
| Lock what you share | `using lock { }`, never manual unlock | Java, C#, Python, C++ |
| Let the compiler check | Shared changes without protection don't compile | Rust (`Send` / `Sync`), Swift actors |
| Async for waiting | One thread juggles many waits; threads only for computing | C#, JavaScript, Python, Rust |

Fusion's spec already chooses "share memory by communicating" (channels) as the default,
`using` blocks for locks, and atomic reference counts for `Shared<T>`. Which of these traps
the compiler should **prevent**, and which it should only warn about, is a design question
for when concurrency becomes a task. Rust shows that races (trap 1) can be made a compile
error; Go shows that a frozen program (traps 3 and 10) can at least give a clear message.

---

## Section 3 - Future: possible ideas

**These are possible ideas, not design choices.** They are written down to be discussed
when concurrency becomes a task. The code is a sketch: nothing here is decided, and the
names may change.

### 3.1 The fixes, in general form

Each trap in Section 2 has specific fixes. Behind each fix is a more general principle (the
"abstract solution"), which can guide a language design rather than a single program.

| # | Trap | Usual fixes | Abstract solution |
|---|---|---|---|
| 1 | Race condition | Don't share; atomics; a mutex; one owner thread fed by a channel | **Remove shared changeable state**, or make each change **indivisible** |
| 2 | Check-then-act | Check and act inside one lock; one combined operation (compare-and-set, `getOrAdd`) | **A decision and its action form one indivisible step** |
| 3 | Deadlock | One global lock order; one lock at a time; locks with a timeout; channels instead of locks | **Break the waiting circle**: an order on resources, or no waiting while holding |
| 4 | Forgotten unlock | `using lock { }` / guard objects - never a manual unlock | **Tie a resource's release to a scope**, so leaving it in any way releases it |
| 5 | Livelock | Random backoff before retrying; give one side priority | **Break the symmetry** between the competing threads |
| 6 | Starvation | Fair (first-come) locks; writers block new readers | **Bounded waiting**: every waiter is served within a known limit (fairness, aging) |
| 7 | Priority inversion | Priority inheritance | **Whoever blocks important work temporarily becomes important** |
| 8 | Change never seen | Atomics, locks, channels, cancellation tokens - never a plain flag | **Communicate only through operations that synchronize** (that set up "happens before") |
| 9 | Collection changed by two threads | Concurrent collections; a lock; one owner thread; copy-on-write snapshots | **Confinement** (one owner) **or immutability** (readers get a snapshot) |
| 10 | Channel with nobody receiving | Start the receiver first; buffers; the sender closes; timeouts | **Every channel has a defined lifetime and owner**, and every wait has a limit |
| 11 | Blocking inside async | Async I/O; heavy work moved to a thread pool | **Keep blocking work and waiting work on separate executors** |
| 12 | Forgetting `await` | A compiler warning or error for an ignored future | **No orphan tasks**: every started task is awaited, or explicitly detached |
| 13 | Sync-over-async deadlock | "Async all the way" | **Never block a thread that the awaited work needs** |
| 14 | Errors lost in another thread | Tasks return a result or an error; a handler for uncaught errors | **Errors travel with results** back to whoever waits |
| 15 | Thread leaks, too many threads | Fixed-size pools; semaphores; async for I/O; a clear way for every thread to end | **Bounded resources and admission control**; every task has an owner and an end |
| 16 | UI from another thread | Post the update to the main thread | **Thread affinity**: an object that belongs to one thread is only reached by messages to it |
| 17 | Contention, false sharing | Short critical sections; split locks; per-thread counters; padding | **Locality**: keep each thread's hot data its own, and share as little and as briefly as possible |

Three ideas cover most of the table:
- **Ownership:** one owner per piece of changeable data.
- **Scoped lifetimes:** locks, tasks and channels end with the block that created them.
- **Bounded waiting:** timeouts, fairness and limits.

The model below builds on all three.

### 3.2 The goal

**A million requests on one machine with many cores, with no data races by construction,
deadlocks and freezes prevented by rules (any that slip through become clear errors), and
no slowdown.**

The approach is to turn the traps into **design principles**, the way the "Gang of Four" book
turned common object-oriented problems into Design Patterns. The principles are built into
the language and its libraries, with defaults that are safe and settings that can change
them. This may not solve concurrency for good. The aim is to make races and deadlocks
**very hard to write**.

Its core is one sentence: **a resource becomes a service, instead of every caller updating
it by hand.** Manual locking is a last resort.

Out of scope for now: several machines (a later `ClusterThreadPool`). Everything here is
about one machine with many cores.

### 3.3 The model (user's direction, 2026-10-23)

#### A. Every thread has an identity and a place in the family tree

- **ID:** a number. Each new thread gets the next number, and an ID is never used twice in a
  run. The main thread is always **0**, the **prime** thread.
- **GUID:** a globally unique ID, for logs and for later, across processes and machines.
- **Key:** the path of who created whom. Main is `0`, its threads are `0.1` and `0.2`, and a
  thread created by `0.2` is `0.2.1`.
- **Priority:** `normal` unless stated.

```fusion
Thread importer = Thread.start(importData, priority = Priority.Low, timeout = 30s)
print("{importer.id} {importer.key} {importer.guid}")   // 7  0.2.1  6f1c...
```

A parent owns its children. Cancelling a parent cancels its children, a child's error is
reported to its parent, and a parent ends only after its children. This is **structured
concurrency**, used by Kotlin, Swift and Java, and it fixes orphan tasks, lost errors and
thread leaks (traps 12, 14 and 15).

#### B. The hierarchy decides who gets a resource

When two threads want the same resource, a **rule** decides which one must give way.

- The default is **`Rule.HIERARCHY`**: the senior key wins. If A is `0.1` and B is `0.2`,
  B releases the resource and A goes first.
- A program can define its own rule. For example, B may have priority over this one
  resource, so A must release it.

Because the hierarchy decides in advance, two threads can never wait on each other in a
circle. This is the same idea as "always lock in one order" (trap 3), made automatic.

#### C. Resources are services (the default)

Files, sockets, pipes and database connections are **services**:
- When the resource is opened, a thread or thread pool is created to manage it. That thread
  or pool **coordinates this one resource only**.
- Other threads never lock the resource. They send it requests, and it carries them out and
  sends back the results.
- When the resource is closed, its thread is released.
- The lock on the real file (for other programs, for example several applications writing
  one log file) is held only during each read or write, then released at once.

```fusion
File log = File.open("app.log")       // log gets its own thread, which manages it as a service
log.write("started")                  // 10 threads may call this: the service puts the
log.write("ready")                    // writes in order, one at a time
string text = await log.readAll()
log.close()                           // the service ends, its thread is released
```

A service brings its own **thread pool** and **scheduler**. Fusion provides some schedulers,
and a developer can write their own:

```fusion
Database db = Database.open("connection string", ThreadPool(10), Scheduler.BASIC)
// Database db = Database.open("connection string")     // the default pool and scheduler
db.execute("UPDATE ...")
db.execute("SELECT ...")
db.close()
```

The application sees **one** database object served by 10 threads. Behind it, the database
may accept 1,000 connections; the service decides how to use them. From outside, each request
is one action.

**The scheduler decides the order** in which requests are carried out:
- `IMMEDIATE`: each request is carried out as it arrives.
- `BATCHED`: requests are collected and run together, as many as the service allows at
  once. Databases do this to save disk writes ("group commit").
- **Custom:** the developer's own order, for example all writes first and then the reads.

**The service decides what can run in parallel.** For example, a write locks only the table
or column it changes, while any number of reads run alongside it.

**The mailbox** (the queue of requests waiting) is set when the service is created:
- its size: unlimited, or a number, for example 100;
- what happens when it is full: the sender waits, or the sender gets a **`QueueFullError`**
  and the request is not added.

```fusion
File audit = File.open("audit.log", mailbox = 100, whenFull = Full.ERROR)   // QueueFullError
File trace = File.open("trace.log", mailbox = 1000, whenFull = Full.WAIT)
```

**Settings (`fusion.toml`):**

```toml
[concurrency]
resource_as_service = true      # the default
```

- `true` (the default): every file, socket, pipe and database is a service, even in a
  single-threaded program.
- `false`: the thread that opened the resource controls it. Other threads can use it
  directly, so all the traps in Section 2 are possible, and syncing is the developer's job.
  Frameworks that manage their own resources may choose this.
- Direct access with no service at all is allowed only in **unsafe** mode, for embedded
  systems.

**The `service` keyword (user, 2026-10-23).** Any variable, struct or class object can be
made a service. On its own the keyword uses Fusion's default settings for the service's
thread:

```fusion
service int counter = 0                        // a variable is now a service
service Person person = Person("Ada")          // a struct is now a service
service Car honda = Honda(Color.Black)         // a class object is now a service
counter += 1                                   // a request to counter's thread, done atomically
```

**Settings** are changed with `service(name)`, and only by the thread that created the
service, never by its sub-threads. The compiler chooses the defaults that are not given.

```fusion
service(counter).Mailbox = 1000                // queue size
service(person).WhenFull = Full.ERROR          // a full queue gives QueueFullError
service(honda).Scheduler = MyCustomScheduler
service(person).Timeout = 60000                // milliseconds: 60 seconds
service(dbConnection).final = {                // extra clean-up, as in try-with-resources;
    dbConnection.flush()                       // leaving scope always releases everything
}
```

**One unit from several services.** `service(a, b, ...)` makes one service that owns them
all, so they change together and no thread ever holds two resources (P2). The list holds one
or more names. A long list is a sign of a bad design, so the compiler warns above a limit
(for example 5) and gives an error above a hard limit (for example 32). Both limits are
settings in `fusion.toml`:

```fusion
service(person, honda) carPerson      // one group service: carPerson
print(person.name)                    // routed to carPerson's queue, carried out atomically
```

The agreed rules for groups (2026-10-24) are in `files/Service.md`, "Group services". A class
can also be declared `service class` ("Service classes"): each of its methods is one atomic
step.

**Settings that fit the machine.** Defaults can depend on the computer the program runs on,
because a PC with 2 GB can't take what suits one with 32 GB. The values are resolved in this
order:
1. Fusion's built-in defaults;
2. `fusion.toml`;
3. the program's own defaults, which may override the machine's settings;
4. `service(name)` in the code.

The program must run on **any** machine. The lowest level is `MIN`, used for embedded
systems and for machines whose memory is unknown; `2GB` is an example of a low-end level.
Machine settings only tune the defaults for the developer's app: they **never** stop the
program from running and never cause an error. A machine that matches no level gets the
`MIN` settings.

```toml
[concurrency]
max_unit_warn = 5                        # service(a, b, ...) with more names: a warning
max_unit = 32                            # more than this: a compile error

[concurrency.machine.min]                # embedded, or memory unknown: the lowest settings
default_pool_size = 1
default_mailbox = 16
[concurrency.machine.small]              # used when the machine has less than 8 GB
when_memory_below = "8GB"
default_pool_size = 2
default_mailbox = 100
```

The syntax: `service <type> <name>` declares a service, and `service(<list of names>)`
changes settings or forms a unit.

The same applies to collections. `ModifiedWhileLoopingError` (Task 27.2e) is for ordinary
lists, which must not change while something loops over them. A list declared as a service
may be changed while others loop: each loop sees a snapshot.

#### D. One thread, one resource

**No thread ever holds more than one resource.** Waiting on two or more results at once is a
sign of a bad design.

- By default this is a **warning** in the editor and the compiler. A setting can make it a
  **compile error**.
- Only **unsafe** mode allows a thread to wait on two or more resources, and then it's the
  developer's decision.
- **Two resources that can't be separated logically** (for example, a file and a database
  row that must change together) are treated as **one unit**. One service owns both, and
  only its thread touches them, so the atomic step happens inside that service. All other
  threads use channels to reach it.

#### E. Scheduling

- The default is the **operating system's** scheduler.
- A **Fusion scheduler** is an option for advanced developers who need finer control. It
  can be set in `fusion.toml`, or per pool in the code: `ThreadPool(10, Scheduler.WEIGHTED)`.
- **Weighted turns:** priorities get shares of the turns, not absolute precedence. For
  example, out of 10 turns high priority gets 5, medium 4 and low 1, so low priority still
  runs at least 1 time in 10. The numbers only illustrate the idea.

#### F. Every wait has a timeout

Each thread, task and request states a timeout:
- **Defaults per kind of resource.** The starting values are 2 minutes for a database,
  2 minutes for a file and 60 seconds for a socket. They are to be checked against best
  practice; for comparison, .NET's `SqlCommand` waits 30 seconds by default, and Erlang's
  `gen_server:call` 5 seconds.
- **Set per resource** when it is opened (`timeout = 10min` for a big SQL update).
- **`never`** is only for very important long-running threads, such as a server waiting for
  clients.
- When a timeout runs out, the work stops cooperatively, and its resources are released.
  Because a service's requests either complete or are rolled back, nothing is left
  half-written.

#### G. How the traps are reported

- Every trap the compiler or runtime can see is a **warning** by default.
- `fusion.toml` can turn each one into an **error**. The error is a Fusion error type that
  the program must catch and handle, for example a `DeadlockError`, `TimeoutError` or
  `QueueFullError`.

```toml
[concurrency.traps]
two_resources = "warning"     # warning | error
shared_variable = "warning"
missing_timeout = "error"
```

#### H. Editor tools: a stack of threads

Fusion's editor tools would show the threads the way a debugger shows a call stack: what each
thread does, in order.

```text
Thread 0      main app
Thread 1      autolock variable A, as a service
Thread 2      uses variable A - sends a request to Thread 1
Thread 1      variable A out of scope - resources released
```

The same view would show:
- which variables each thread changes;
- which files, sockets, web connections and databases it uses;
- profiling: time waiting, time running, how full each mailbox is.

Graphs and heat maps come later. Most of this is known **before** the program runs, because
the compiler sees which variables and resources each function touches. The rest comes from
tracing while it runs. (Noted in `FEATURES.md` under Task 36.)

### 3.4 The principles - a catalogue

Each principle is written like a design pattern: its intent, the problem it solves, the
solution, and what it costs. They rest on one fact.

A deadlock needs **all four** of these "Coffman conditions" (1971):
1. **Mutual exclusion:** only one thread may use a resource at a time.
2. **Hold and wait:** a thread holds one resource while it waits for another.
3. **No preemption:** a resource can't be taken from the thread that holds it.
4. **Circular wait:** threads wait on each other in a circle.

Break any one, and deadlock is impossible. The principles below break three of them.

#### P1. Resource as Service

- **Intent:** make shared resources safe without locks in the callers.
- **Problem:** many threads update one file, socket, database or variable, which leads to
  races, check-then-act bugs and forgotten unlocks (traps 1, 2, 4, 8, 9).
- **Solution:** one coordinator (a thread or pool) owns the resource; everyone else sends
  requests (model C).
- **Consequences:** callers can't corrupt the resource. The costs are a hop through a
  mailbox (microseconds), and the mailbox can fill up (P6).
- **Seen in:** Erlang's `gen_server`, database connection pools, Node.js's file thread pool,
  and Python's advice for logging from many processes (case 1 below).

#### P2. One Thread, One Resource

- **Intent:** no thread waits on two resources.
- **Problem:** a thread that holds A and waits for B is half of every deadlock (trap 3).
- **Solution:** a warning or compile error when a thread would hold two (model D). Things
  that must change together become one service.
- **Consequences:** this breaks **hold and wait**. A design that needs two resources at once
  must name them as one unit, which also documents the dependency.

#### P3. The Hierarchy Decides

- **Intent:** contention always has a known winner.
- **Problem:** two threads each wait for the other to give way (traps 3 and 5).
- **Solution:** `Rule.HIERARCHY` (the senior key wins), or a custom rule; the loser
  releases (model B).
- **Consequences:** this breaks **circular wait** and **no preemption**. Releasing must
  be safe, which services guarantee (a request completes or is rolled back).

#### P4. Every Wait Has a Deadline

- **Intent:** nothing waits forever.
- **Problem:** frozen programs: lost replies, a channel nobody reads, services waiting on
  each other (traps 3, 10, 13 and 15).
- **Solution:** a timeout on every thread, request and wait, with defaults per resource
  kind (model F). A child's deadline is never later than its parent's.
- **Consequences:** a freeze becomes a `TimeoutError` with a clear message. The timeout
  values need care: too short, and slow but healthy work fails.

#### P5. Owned Threads (the family tree)

- **Intent:** every thread and task has an owner and an end.
- **Problem:** orphan tasks, lost errors, leaked threads (traps 12, 14 and 15).
- **Solution:** the ID / key tree (model A): parents wait for children, cancel them, and
  receive their errors.
- **Consequences:** a thread can't outlive its purpose. Long-lived workers belong to a
  long-lived parent, for example a server.
- **Seen in:** Erlang's supervision trees, which restart failed workers, Kotlin's
  coroutine scopes, and Java's StructuredTaskScope.

#### P6. Bounded Mailboxes

- **Intent:** overload is visible and controlled.
- **Problem:** requests arrive faster than they are served. Memory fills up and everything
  slows down at once.
- **Solution:** a size for every mailbox, and a stated policy for when it is full (wait or
  `QueueFullError`).
- **Consequences:** the system slows down at the edge (back-pressure) instead of
  collapsing in the middle.

#### P7. The Service Owns Its Schedule

- **Intent:** the resource, which knows its own rules, decides the order and what runs in
  parallel.
- **Problem:** callers can't know that reads may share and writes may not, or that batching
  saves 90% of disk writes.
- **Solution:** a scheduler per service, chosen from `IMMEDIATE`, `BATCHED` or a custom one
  (model C).
- **Consequences:** this gives the best throughput, and the caller's code stays simple.
- **Seen in:** SQLite in WAL mode: many readers at once, one writer, and readers never block
  the writer.

#### P8. Weighted Turns

- **Intent:** important work goes first, and no work starves.
- **Problem:** strict priority starves low priority (trap 6) and allows priority inversion
  (trap 7).
- **Solution:** shares of the turns (model E). A service takes requests from a high-priority
  thread first, **including requests a low-priority thread makes on its behalf**
  (priority inheritance).
- **Seen in:** Linux's weights per "nice" level; the Mars Pathfinder fix (case 9 below).

#### P9. Services Never Block on Each Other

- **Intent:** stop deadlocks between services, which message passing alone does not
  prevent.
- **Problem:** service A, while handling a request, waits for service B's reply, while B
  waits for A's. This is the most common deadlock in Go programs (case 5).
- **Solution:** a service handling a request may only call **down** the hierarchy, or
  send without waiting for a reply. The compiler can check this from the key tree. P4 is
  the backstop.
- **Consequences:** Together with P2 and P3, this closes the remaining circle.

#### P10. Visible Concurrency

- **Intent:** concurrency bugs can be seen before they happen.
- **Problem:** bugs that depend on timing hide from testing. The 2003 blackout bug took
  weeks of code audit to find (case 10).
- **Solution:** the editor's thread stack, graphs and heat maps (model H), and compiler
  warnings for shared variables and for threads holding two resources.

### 3.5 Real-world cases

Each case says what happened, shows a short sketch of the bug, and names the principle that
prevents it. The code sketches are simplified, not the original code.

#### Case 1 - Several processes writing one log file (Python)

Python's own documentation says logging to one file from **several processes** is not
supported. There is no standard way to serialize access to a file across processes, and
log lines get mixed up. Its advice is to send every log record to one process (or one
thread) that alone writes the file. That is **P1, Resource as Service**, recommended by the
language itself.

```python
# every worker process: send, don't write
queue_handler = logging.handlers.QueueHandler(queue)
# one listener: the only writer of the file
listener = logging.handlers.QueueListener(queue, logging.FileHandler("app.log"))
```

Link: [Python Logging Cookbook - Logging to a single file from multiple processes](https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes)

#### Case 2 - Two transfers deadlock in a database (PostgreSQL)

This is the textbook database deadlock, from PostgreSQL's manual. Two transactions update
the same two rows in opposite orders, and each waits for the other's row lock. PostgreSQL
detects it and cancels one transaction.

```sql
-- transaction 1                                   -- transaction 2
UPDATE accounts SET balance = balance + 100        UPDATE accounts SET balance = balance + 100
  WHERE acctnum = 11111;                             WHERE acctnum = 22222;
                                                   UPDATE accounts SET balance = balance - 100
                                                     WHERE acctnum = 11111;   -- waits for 1
UPDATE accounts SET balance = balance - 100
  WHERE acctnum = 22222;                           -- waits for 2: deadlock
```

The manual's advice: always take locks in the same order. Prevented by **P3** (the order is
fixed by the hierarchy) and **P7** (the database service orders the writes).

Link: [PostgreSQL documentation - Deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-DEADLOCKS)

#### Case 3 - A shared map crashes a log shipper (Go, Grafana Promtail)

Promtail 2.2.0 crashed with `fatal error: concurrent map read and map write` when it sent
logs to several Loki servers. Several clients used one shared map without a lock, and Go's
runtime stopped the program. The fix added synchronization.

```go
var tenants = map[string]string{}       // shared by every client goroutine
func getTenantID(c Client) string {
    return tenants[c.Name]              // read in one goroutine ...
}                                       // ... while another writes: fatal error
```

Prevented by **P1**: the map is a service (`service Map<string, string> tenants`), so only
its owner touches it.

Link: [grafana/loki#3571](https://github.com/grafana/loki/issues/3571), fix [grafana/loki#3573](https://github.com/grafana/loki/pull/3573)

#### Case 4 - A HashMap loops forever at 100% CPU (Java)

In Java 7, two threads that resized the same `HashMap` at once could link its internal
list into a **circle**. Every later `get` then looped forever. Servers froze at 100% CPU
with no error message. Java 8 removed the loop, but entries can still be lost. The
documented fix is `ConcurrentHashMap` or a lock.

```java
static Map<String, User> cache = new HashMap<>();   // not thread-safe
// many request threads:
cache.put(id, user);       // two resizes at once -> a circular list
cache.get(id);             // spins forever
```

Prevented by **P1**: a shared collection is a service, never touched directly from two
threads.

Link: [DZone - Resizing the HashMap: Dangers Ahead](https://dzone.com/articles/resizing-the-hashmap-dangers-ahead)

#### Case 5 - Docker hangs on start-up, and a study of 171 Go bugs

Docker's engine deadlocked on start-up whenever more than one plugin was installed (fixed in
moby/moby#25384). It is one of 171 concurrency bugs collected from Docker, Kubernetes, etcd,
CockroachDB, gRPC and BoltDB, in a 2019 study of real Go programs.

The key finding: **58% of the blocking bugs (freezes) came from message passing**, not
locks. Channels alone don't prevent deadlocks. This is why **P9** (services never block on
each other) and **P4** (deadlines) are needed alongside **P1**.

```go
ch := make(chan result)          // unbuffered
go func() { ch <- work() }()     // sends, and waits for a receiver
select {
case r := <-ch: use(r)
case <-time.After(timeout):      // the caller gives up and leaves ...
    return                       // ... and the goroutine waits forever: a leak
}
```

Links:
- [moby/moby#25384 - fix deadlock when more than 1 plugin is installed](https://github.com/moby/moby/pull/25384)
- [system-pclub/go-concurrency-bugs](https://github.com/system-pclub/go-concurrency-bugs) (the
  data set)
- [Understanding Real-World Concurrency Bugs in Go (paper, ASPLOS 2019)](https://songlh.github.io/paper/go-study.pdf)

#### Case 6 - Netflix servers freeze on Java 21 virtual threads

After moving to Java 21 virtual threads, Netflix servers stopped answering at random:
- Virtual threads waiting inside `synchronized` blocks were **pinned** to the few real
  carrier threads.
- With every carrier pinned, the thread holding the lock could never be scheduled to
  release it.
- Ordinary thread dumps didn't show the cause.

JDK 24 (JEP 491) later removed this kind of pinning.

```java
synchronized (span) {      // pins this virtual thread to its carrier thread
    lock.lock();           // waits - and every carrier is now pinned and waiting,
}                          // so the lock's owner can never run to release it
```

Prevented by **P2** (no thread holds two locks: here `synchronized` and `lock`) and **P10**
(the thread view shows who holds what).

Links:
- [Netflix Tech Blog - Java 21 Virtual Threads: Dude, Where's My Lock?](https://netflixtechblog.com/java-21-virtual-threads-dude-wheres-my-lock-3052540e231d)
- [Reproducing the deadlock with TLA+](https://surfingcomplexity.blog/2024/08/01/reproducing-a-java-21-virtual-threads-deadlock-scenario-with-tla/)
- [OpenJDK loom-dev: real-world pinning / ReentrantLock deadlock](https://mail.openjdk.org/pipermail/loom-dev/2024-June/006808.html)

#### Case 7 - The UI freezes waiting for its own async work (C#)

This is the classic .NET freeze. A button handler blocks on `.Result`, but the async method
needs the UI thread to continue after its `await`, so each waits for the other.

```csharp
void Button_Click(...) {
    var json = GetJsonAsync(uri).Result;   // blocks the UI thread ...
}
async Task<string> GetJsonAsync(Uri uri) {
    var s = await client.GetStringAsync(uri);   // ... which this needs to continue
    return s;
}
```

The fix: "async all the way down", never blocking on async code. Prevented by **P9** (never
block on something that needs you) and **P4** (a deadline turns the freeze into an error).

Link: [Stephen Cleary - Don't Block on Async Code](https://blog.stephencleary.com/2012/07/dont-block-on-async-code.html)

#### Case 8 - One slow request stalls every client (Node.js)

Node.js serves thousands of clients with one event-loop thread and a small worker pool, and
uses that pool for file operations. One CPU-heavy callback, or a synchronous file read, on
the event loop stalls **every** client.

```javascript
app.get("/report", (req, res) => {
    const data = fs.readFileSync("big.csv");   // blocks the only event-loop thread
    res.send(summarize(data));                 // every other client waits
});
```

Prevented by **P1** (the file is a service with its own pool; Node's own design for `fs`)
and **P7** (heavy work goes to a pool that is meant for it).

Links:
- [Node.js - Don't Block the Event Loop (or the Worker Pool)](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop)
- [Alice Ryhl - Async: What is blocking?](https://ryhl.io/blog/async-what-is-blocking/) (Rust:
  aim for 10-100 microseconds between `.await` points)

#### Case 9 - Mars Pathfinder resets itself on Mars (1997)

A low-priority weather task held a shared bus lock. Medium-priority tasks kept it from
running, so the high-priority bus task waited too long. A watchdog then reset the whole
computer, again and again. The fix, sent from Earth, turned on **priority inheritance** for
that lock.

Prevented by **P8** (requests on behalf of a high-priority thread are served at high
priority) and **P1** (the bus is a service, so no lock is held across tasks).

Link: [Glenn Reeves (JPL software lead) - What really happened on Mars](https://www.cs.cornell.edu/courses/cs614/1999sp/papers/pathfinder2.html)

#### Case 10 - The 2003 North American blackout

A race condition in GE's XA/21 energy management system silently stopped the alarm system
at FirstEnergy's control room. Operators didn't see the failing lines in time, and about 50
million people lost power. The bug's window was milliseconds wide. It took weeks of auditing
about a million lines of code, and a lab that slowed the system down, to find it.

Prevented by **P1** (the alarm list is a service) and **P10** (shared variables are flagged
by the compiler, not found after the blackout).

Link: [The Register - Software bug contributed to blackout](https://www.theregister.com/2004/04/08/blackout_bug_report/)

#### Case 11 - What real concurrency bugs look like (MySQL, Apache, Mozilla, OpenOffice)

A 2008 study of 105 real concurrency bugs found:
- about a third of the non-deadlock bugs broke the order the programmer intended ("A
  must happen before B");
- 34% involved **several variables** that had to change together;
- 92% could be triggered by forcing the order of at most four memory accesses.

This supports **P1** and **P2**. Things that must change together belong in one service,
which carries out each request whole and in order. The study won the ASPLOS Influential
Paper award.

Link: [Lu et al. - Learning from Mistakes: A Comprehensive Study on Real World Concurrency Bug Characteristics (PDF)](https://www.cs.columbia.edu/~junfeng/10fa-e6998/papers/concurrency-bugs.pdf)

#### Case 12 - Scaling done right: WhatsApp on Erlang

WhatsApp ran **2 to 3 million connections on one server** with Erlang on FreeBSD:
- each connection is a light Erlang process with its own mailbox, and no shared memory;
- supervisors restart whatever fails.

This is P1, P5 and P6 together, proven at the scale this document aims for.

Links:
- [FreeBSD Foundation - WhatsApp testimonial](https://freebsdfoundation.org/testimonial/whatsapp/)
- [High Scalability - How WhatsApp grew to nearly 500 million users](https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/)
- [Erlang - OTP Design Principles](https://www.erlang.org/doc/system/design_principles.html)
  (supervision trees, `gen_server`)

### 3.6 Questions settled (user, 2026-10-23)

| Question | Answer |
|---|---|
| Ordering of requests | The service's scheduler: `IMMEDIATE`, `BATCHED`, or custom (for example writes first) |
| Mailbox full | The developer chooses: unlimited or a size; when full, the sender waits or gets `QueueFullError` |
| Reads in parallel | The service decides. Writes lock only what they change, reads run together |
| Two resources in one step | Never two resources per thread; if they can't be separated, one service owns both as a unit |
| OS threads or Fusion tasks | The OS scheduler by default; a Fusion scheduler for advanced developers (`fusion.toml`, or `ThreadPool(10, scheduler)`) |
| Timeouts | Defaults per resource kind, starting from what others use (3.7); set per resource when opened |
| Compile error or warning | Warnings by default; `fusion.toml` can make each one an error the program must catch |
| Direct access without a service | Only in unsafe mode (embedded). `resource_as_service = true` is the default; `false` gives control to the opening thread |

### 3.7 Default timeouts - what others use (researched 2026-10-23)

These are the starting point for Fusion's defaults per kind of resource:

| What | Default elsewhere | Source |
|---|---|---|
| Database: getting a connection from the pool | 30 s | HikariCP `connectionTimeout` (Java) |
| Database: one command or query | 30 s | .NET `SqlCommand.CommandTimeout` |
| Database: an idle pooled connection is closed after | 10 min | HikariCP `idleTimeout` |
| Database: a connection is replaced after | 30 min | HikariCP `maxLifetime` |
| SQLite: waiting for a locked database | 5 s | Python `sqlite3.connect(timeout=5.0)` |
| HTTP request (whole request) | 100 s | .NET `HttpClient.Timeout` |
| Proxy: waiting between two reads from a server | 60 s | nginx `proxy_read_timeout` |
| A call to another service | 5 s | Erlang `gen_server:call` |
| HTTP in Go, Python `requests`, Java `HttpClient` | **none** (waits forever) | A well-known trap: always set one |

**Suggested Fusion starting values** (to be confirmed when the task starts):
- a database query: 30 s;
- getting a connection: 30 s;
- an HTTP request: 100 s;
- a socket read: 60 s;
- a request to a service: 5 s;
- waiting for a file lock: 5 s.

A file read or write itself gets no fixed limit, because its size varies; a timeout can be
given per call (`timeout = 10min` for a big file).

### 3.8 Custom rules and schedulers - examples

**A rule** decides who wins when two threads want the same service. The default is the
hierarchy (the senior key wins). A custom rule is a class with one method:

```fusion
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
service(db).Rule = PaymentsFirst()
```

**A scheduler** decides the order in which a service carries out the requests in its
mailbox. A custom one is a class with one method:

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
service(log).Scheduler = WritesFirst()
```

### 3.9 Does any other language have this?

Several languages have parts of it. None has the whole set: a service made from any
variable, struct or class at the place it is declared, with settings such as mailbox,
timeout, scheduler and rule, grouped units, and resources as services by default.

| Language | What it has | How Fusion's `service` differs |
|---|---|---|
| **Swift** | `actor` keyword (5.5): a class-like type whose state only its own task touches; callers must `await`; the compiler checks it | An actor is fixed when the **type** is written; in Fusion **any** value becomes a service where it is declared. Swift has no mailbox, timeout or scheduler settings. Swift actors can change between `await`s (re-entrancy), a known trap |
| **Pony** | `actor` keyword; no locks at all, so it is free of data races and deadlocks, checked by the compiler | The closest in guarantees. Pony never lets anyone wait for a reply (only send), which is how it avoids deadlock. Fusion allows `await`, so it needs P4 and P9 |
| **Erlang / Elixir** | Every process is a service (`gen_server`); mailboxes; 5 s call timeout; supervisors | The proven model, but as a library pattern, not a keyword on a variable; dynamic types |
| **Akka** (Scala / Java), **Orleans** (C#) | Actor libraries; Orleans "grains" are services that exist on demand | Libraries, not the language; no compiler checks |
| **Kotlin** | `actor { }` coroutine builder (now obsolete), channels | A library function |
| **Go, Java, C#, C++, Python, Rust** | Channels, locks, async - no service construct | The developer builds the service by hand |

So Fusion's `service` is close to a **Swift actor applied to any value**, combined with
**Erlang's operational settings** (mailbox, timeouts, supervision), and resources as
services by default. That combination, with the one-resource-per-thread and hierarchy
rules, would be Fusion's signature.

Links:
- [Swift - Concurrency (actors)](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
- [Pony - What makes Pony different](https://ponylang.io/discover/what-makes-pony-different/)
- [Microsoft Orleans](https://learn.microsoft.com/en-us/dotnet/orleans/overview)

### 3.10 Future tasks

Scheduled in `FEATURES.md` Task 42:
- **42.8:** the exact default values (3.7 is the starting point).
- **42.7:** the `Thread` class: its internal counter (IDs), and helpers that track threads as
  they start and end.
- **42.13:** how the compiler checks P9 (a service calls only down the hierarchy) across
  modules.
- **42.12:** cluster threads across several servers. This is later, probably outside Fusion's
  first scope, and handled by a separate cluster framework.

### 3.12 Collections and threads (user, 2026-10-27)

Arrays, lists and maps get thread safety built in, so the common cases need no lock written
by hand (FEATURES.md 42.17, 45.8; `Arrays.md`):
- **Arrays** grow and shrink only at their end, so one atomic lock around "add at the end" /
  "remove the last" is enough - taken implicitly, never written in the code
- **Lists and maps** can change anywhere, so they are served like a small service (P1): a
  shared thread, or a dedicated one for a busy list or map, does the adding, reading and
  removing; callers send requests
- Open: which is the default for lists and maps (shared or dedicated), and the setting that
  chooses

### 3.11 Version one of `service` (agreed 2026-10-24)

The full reference, with every setting and the `fusion.toml` defaults: `files/Service.md`.

This version was agreed after reviews by ChatGPT and Claude
(`Notes/notes chatgpt review on our concurrency.md`). The aim is to keep it as simple as
possible. Everything else in Section 3 builds on these rules later.

#### The five rules

1. **What `service` means:** one owner of the state. Every statement or method call on it is
   one indivisible step. Anything read out of it is a **copy**. Copying a service variable
   gives another **handle** to the same service, not a second copy of its state.
2. **How it runs is the compiler's choice.** A service is a logical owner, never a thread of
   its own:
   - used by one thread only: it becomes a plain variable, at no cost;
   - a simple value (`service int`): CPU atomic instructions;
   - anything else: a mailbox, served by a small shared worker pool.
3. **Waiting:** ordinary code reads in order. `counter += 1` followed by `print(counter)`
   prints the updated value. Not waiting must be asked for (`async`). A service finishes one
   request before it starts the next, even if the request `await`s in the middle. That makes
   it **not re-entrant** by default; re-entrancy has to be opted into.
4. **Several steps as one:** a class method, or `service(x).run { ... }`, runs as one step:

   ```fusion
   service(account).run {
       if account.balance >= 800 {       // the check and the change are one step:
           account.balance -= 800        // two withdrawals can't both pass the check
       }
   }
   ```

5. **A timeout means the caller stopped waiting, not that the work was undone.** Every
   request ends as **completed**, **failed**, **timed out** (its effects may still happen),
   or **cancelled**.

#### Where a service is created (user, 2026-10-24)

- A service exists **only** for state that several threads read or write. Its job is to
  make sure the operations are atomic, especially when several values must change as one
  unit.
- It is declared **outside** loops: as a class field, or as a variable, struct or class
  object in a function. The threads (for example, child workers started in a loop) then
  act on it.
- **Only a parent thread creates a service**, and its child threads use it. A child thread
  can in turn create its own service, for further processing by **its** children, and send
  results on to its parent's service.
- If no other thread ever uses a service, the compiler gives a warning.

```fusion
void function processOrders(List<Order> orders) {
    service Totals totals = Totals()          // created by the parent, outside the loop
    for order in orders {
        go worker(order, totals)              // child threads act on the shared service
    }
}

void function worker(Order order, Totals totals) {
    service List<Line> lines = []             // a child may create its own service, for
    for item in order.items {                 // its own children to fill
        go priceLine(item, lines)
    }
    totals.add(order.id, lines)               // then send the result to the parent's service
}
```

#### The keyword

`service` is a **contextual** keyword for now, the way `error` is. A variable may still be
named `service`. It may become a full keyword later.

#### Adopted from the reviews

- **Three separate concerns:**
  - **Ownership:** the thread tree. It decides who cancels whom and where errors go.
  - **Priority:** what runs sooner.
  - **Contention:** who wins when two threads want one resource.

  `Rule.HIERARCHY` is only the default for contention.
- **"One resource per thread" means at the same time:** never hold one resource while
  waiting on another. Using a database and then a log file, one after the other, is fine.
- **A release happens between requests, never in the middle of one.**
- **Cheap reads:** readers can get a **snapshot** instead of sending one request per read.
- **When the mailbox is full:** wait, reject (`QueueFullError`), or **coalesce**. Coalescing
  merges pending requests into the newest one where that is safe, such as position updates,
  never withdrawals.
- **Nothing escapes:** a class object inside a service is never handed out; only copies
  leave.
- **The goal's wording:** no data races by construction; deadlocks and freezes prevented
  by rules, and any that slip through turned into clear errors.

#### Postponed until version one works

- units (`service(a, b)`);
- custom schedulers and contention rules;
- machine-dependent profiles;
- most of the settings in FEATURES.md 42.11.

Version one needs four settings: `Mailbox`, `WhenFull`, `Timeout` and `final`. The
execution profiles ChatGPT suggested (LOCAL, SERIAL, PARALLEL, IO, REALTIME) are dropped:
the compiler chooses the implementation (rule 2).

#### Roadmap (from ChatGPT's review)

1. **Meaning:** the five rules, a mailbox, exclusive ownership, waiting and `async`, error
   propagation.
2. **Structured execution:** tasks and futures, `await`, cancellation, parent-child
   lifetimes, bounded queues, deadlines, shutdown and clean-up.
3. **An efficient runtime:** the shared worker pool, cheap logical services, back-pressure,
   snapshots, profiling.
4. **Advanced coordination:** units across several resources, scheduling and fairness,
   priority inheritance, deadlock diagnostics, custom schedulers.
5. **Platforms:** embedded profiles, high-throughput servers, backend optimizations;
   distributed services (the cluster framework) only if justified.

Before phase 1 is planned in full: a small prototype measuring the cost per request and
per service.

#### First tests

1. Thousands of concurrent increments give the exact expected result.
2. Concurrent withdrawals never break the balance rule.
3. A snapshot stays consistent while the service changes.
4. Errors reach the right caller.
5. Cancellation and shutdown release every resource.
6. A full mailbox gives the configured result.
7. Services calling each other never wait in an endless circle.
8. Many logical services share a small worker pool.

A **deterministic test mode** (a seed that fixes the order threads run in) lets a failing
order be replayed.

---

## Section 4 - How other languages handle it

This section compares other languages on the two things that matter most here: **serving
a million requests**, and **avoiding races, deadlocks and freezes**.

#### C

- **A million requests:** an event loop on the operating system's event API (epoll on
  Linux, IOCP on Windows). One thread watches thousands of sockets; nginx and Redis work
  this way. It is fast but hard to write: every request is a state machine written by hand.
- **Races:** the language does nothing. A data race is undefined behaviour. Tools find
  some races while testing (ThreadSanitizer: `gcc -fsanitize=thread`).
- **Deadlocks and freezes:** nothing. A deadlock is a silent hang.

```c
pthread_mutex_lock(&m);
balance -= amount;          /* forget the unlock on one path: a silent hang later */
pthread_mutex_unlock(&m);
```

#### C++

- **A million requests:** event loops (Boost.Asio), and since C++20 coroutines
  (`co_await`), so the code reads in a straight line.
- **Races:** undefined behaviour, as in C. `std::atomic` and `std::mutex` help, and
  ThreadSanitizer finds some races.
- **Deadlocks:** `std::scoped_lock` can lock **several mutexes at once without deadlock**,
  using a built-in avoidance algorithm. Guard objects (`lock_guard`) make forgotten unlocks
  impossible.

```cpp
std::scoped_lock both(from.m, to.m);   // takes both locks in a safe order - trap 3 avoided
from.balance -= amount;
to.balance += amount;                  // both unlocked when 'both' goes out of scope
```

#### Java

- **A million requests:** **virtual threads** (Java 21, JEP 444). Millions of cheap threads
  run on a few real ones, so plain blocking code scales.

  ```java
  try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      for (int i = 0; i < 1_000_000; i++) {
          executor.submit(() -> handle(request));   // one cheap virtual thread per request
      }
  }   // waits for all of them - structured
  ```

- **Races:** `synchronized`, `java.util.concurrent` (`ConcurrentHashMap`, atomics), and a
  defined memory model. Races are still possible, and nothing stops them at compile time.
- **Deadlocks and freezes:**
  - The runtime can **find** deadlocked threads (`ThreadMXBean.findDeadlockedThreads()`),
    and thread dumps show who holds which lock.
  - Pinning froze Netflix (case 6) until JDK 24.

#### C\#

- **A million requests:** `async` / `await` on a thread pool, plus `System.Threading.Channels`
  for producer/consumer queues with a bounded size and a choice of what happens when full.
  That is **P6**, built in.
- **Races:** `lock`, `Interlocked`, concurrent collections. No compile-time check.
- **Deadlocks and freezes:** the sync-over-async freeze (case 7) is the best-known trap.
  `CancellationToken` and timeouts are passed through most APIs (**P4**).

```csharp
var channel = Channel.CreateBounded<Request>(new BoundedChannelOptions(100) {
    FullMode = BoundedChannelFullMode.Wait          // or DropOldest, DropNewest, DropWrite
});
```

#### Go

- **A million requests:** goroutines, which start with a 2 KB stack, multiplexed by Go's
  own scheduler onto a few OS threads. A million goroutines is normal.
- **Races:** "share memory by communicating" with channels. The **race detector**
  (`go run -race`) finds races while testing. A map used from two goroutines can crash
  the program on purpose (case 3), which is better than corrupting it silently.
- **Deadlocks and freezes:** the runtime reports `all goroutines are asleep - deadlock!`,
  but only when **every** goroutine is stuck. A partial deadlock in a server goes unnoticed,
  and most real Go freezes come from channels (case 5). `context` passes deadlines and
  cancellation down to children (**P4**, **P5**).

```go
ctx, cancel := context.WithTimeout(parent, 2*time.Second)   // the child inherits a deadline
defer cancel()
row := db.QueryRowContext(ctx, "SELECT ...")                // gives up after 2 s
```

#### Python

- **A million requests:** `asyncio` (one thread, an event loop, many coroutines), or
  several processes. Threads don't run Python code in parallel because of the **GIL**
  (Global Interpreter Lock); Python 3.13 offers an optional build without it.
- **Races:** the GIL hides some races but not all. `count += 1` can still lose updates
  between threads. Locks and `queue.Queue` are the tools.
- **Deadlocks and freezes:** no detection. Blocking calls inside `asyncio` freeze the event
  loop (trap 11). Python's own advice for shared files is a single writer (case 1, **P1**).

#### Rust

- **A million requests:** async with a runtime such as Tokio (millions of tasks on a thread
  pool).
- **Races:** **data races are compile errors.** The `Send` and `Sync` rules stop a value
  from being shared between threads unless it is safe, such as an `Arc<Mutex<T>>` or an
  atomic. This is the strongest guarantee of any mainstream language, and the model for
  "let the compiler check".

  ```rust
  let count = Rc::new(0);
  thread::spawn(move || println!("{}", count));
  // compile error: `Rc<i32>` cannot be sent between threads safely
  ```

- **Deadlocks and freezes:** **not** prevented. Two `Mutex`es locked in opposite orders
  still deadlock, and blocking inside async freezes a worker (case 8).

#### Erlang / Elixir

- **A million requests:** the reference point. Processes are tiny (a few KB), each has a
  mailbox, and there is no shared memory. WhatsApp held 2-3 million connections per server
  (case 12).
- **Races:** no shared memory means **no data races** at all. Each process is a service
  (**P1**).
- **Deadlocks and freezes:**
  - `gen_server:call` has a **5-second timeout by default**, so a deadlock between two
    servers becomes an error, not a freeze (**P4**).
  - Supervision trees restart what fails (**P5**). "Let it crash" is the philosophy: a
    process in a bad state is restarted fresh.

```erlang
gen_server:call(BankServer, {withdraw, 80})   % a request to the service; 5 s timeout
```

#### JavaScript / Node.js

- **A million requests:** one event-loop thread plus a worker pool (libuv). It suits I/O
  and is weak at CPU-heavy work.
- **Races:** your own code runs on one thread, so there are no data races. Ordering bugs
  between `await`s remain (check-then-act across an `await`).
- **Freezes:** any blocking call stalls every client (case 8).

#### Summary

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

#### What Fusion can take from each

- From **Erlang:** every resource and shared value is a process with a mailbox (P1), call
  timeouts by default (P4), and supervision trees (P5). Erlang alone proves the
  million-connection goal.
- From **Rust:** shared changeable data without protection is a compile error. In Fusion
  that is a warning by default, an error when `fusion.toml` says so.
- From **Go:** cheap tasks over a few threads, a race detector for testing, and deadlines
  passed down to children (`context`). Go's bug study is also a warning: channels alone
  don't stop freezes.
- From **C#:** bounded channels with a chosen "when full" policy (P6).
- From **C++:** when several locks truly are needed (unsafe mode), take them all at once
  in a safe order.
- From **Java:** virtual threads show that plain, blocking-style code can scale. The
  Netflix case shows why tools must show who holds what (P10).

Fusion's own addition is the combination: **services by default, one resource per thread,
the hierarchy deciding contention, and every wait with a deadline.** Between them they break
three of the four conditions a deadlock needs. That is the claim to test when concurrency
becomes a task.
