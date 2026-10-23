# Concurrency in Fusion - terms and traps

Doing several things at once: what the words mean, and what goes wrong.

**None of this is built yet.** The code uses Fusion syntax as designed in
`files/fusion-language-spec.md` ("Threading and Concurrency Model", "Async/Await Pattern")
and `files/showcase/Fusion_showcase.fusion` section 18. Names such as `ThreadPool`,
`Atomic<T>` and `Semaphore` are suggestions until concurrency becomes a task.

- **Section 1** explains each term, with a short example.
- **Section 2** shows the common traps: each with code that has the bug, and how it is
  normally solved.
- **Section 3** collects possible ideas for Fusion: the fixes in general form, and a first
  model of threads, priorities and resources run as services.

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

### 3.2 A first model (user's proposal, 2026-10-23)

This section restates the proposal, and adds notes on what exists elsewhere and what would
need to be worked out.

#### A. Every thread has an identity

- **ID:** a number. Each new thread gets the next number (ID + 1), so an ID is never used
  twice in a run. The main thread is always **0**, the **prime** thread.
- **GUID:** a globally unique ID, so a thread can also be identified across processes, logs
  and machines.
- **Key:** a multi-part key that records **who created it**. Main is `0`, a thread created
  by main is `0.3`, and a thread created by that one is `0.3.7`. The key is the thread's
  place in the family tree.
- **Priority:** `normal` unless stated.

```fusion
Thread importer = Thread.start(importData, priority = Priority.Low, timeout = 30s)
print("{importer.id} {importer.key} {importer.guid}")   // 7  0.3.7  6f1c...-...
```

*Notes:*
- The key matches **structured concurrency** (Kotlin coroutines, Swift tasks, Java's
  StructuredTaskScope): a parent owns its children. This gives clear rules:
  - cancelling a parent cancels its children;
  - an error in a child is reported to its parent;
  - a parent doesn't end until its children have ended.

  That fixes trap 12 (orphan tasks), trap 14 (lost errors) and trap 15 (leaks).
- The ID never repeating needs a 64-bit counter. At a million threads per second it would
  take about 290,000 years to run out.
- For tasks (many small jobs on few threads) the same identity can apply to each task, not
  only to each operating-system thread.

#### B. Priority: lower priority yields to higher

A thread with lower priority, deeper in the tree, always yields to a thread with higher
priority.

*Notes:* "always yields" alone leads to **starvation** (trap 6): a busy high-priority
thread could stop low ones forever. Point E (weighted turns) is the fix, so B and E work
together. Priority also needs **priority inheritance** (trap 7). In this model that means a
service (point D) handles a high-priority request first, even when it came from a
low-priority thread acting on a high one's behalf.

#### C. A sleeping thread releases its locks

When a thread sleeps it gives up its resources, and it takes them again when it wakes, before
it carries on.

*Notes:* This is how a **condition variable wait** already works. The danger is that
anything may have changed while it slept. A check made before sleeping can be wrong after
waking (trap 2). Two possible rules:
- Sleeping inside a lock is a compile error. Only a `wait until <condition>` is allowed
  there; it releases the lock, then takes it again **and checks the condition again**.
- Releasing must only happen where the data is consistent, never halfway through an update.
  The compiler could check this.

#### D. Resources run as services (the core idea)

For files, sockets, pipes and database connections, the usual model is reversed:
- The resource gets its own thread, or a small pool, the moment it is opened.
- Other threads **never lock it**. They send it messages ("write this line", "read 4 KB",
  "run this query").
- The resource's thread carries out each request **atomically**, one at a time and in order,
  and sends the result back.
- When the resource is closed, its thread is released.
- When code writes to a file, it is the file's own thread that does the writing, not the
  calling thread.
- The real lock on the file (for other **applications**, for example several programs
  sharing one log file) is held only for the moment of each read or write. It is released
  straight after.

```fusion
File log = File.open("app.log")       // the file becomes a service with its own worker
log.write("started")                  // a message to the service - this thread locks nothing
string all = await log.readAll()      // the reply comes back as a future
log.close()                           // the service ends; its worker is released
```

To the caller it reads like ordinary code; the message passing is hidden inside.

*Notes:*
- **This is the actor model** (Erlang / Elixir, Akka, Microsoft Orleans). It is proven at very
  large scale: Erlang runs millions of these in phone switches and WhatsApp. Database
  connection pools and asynchronous log writers already work this way.
- It removes traps 1, 2, 4, 8 and 9 for resources, because only one thread ever touches them.
- **One thread per open file does not scale to a million.** The usual answer:
  - Each resource is a **mailbox** (a queue of requests), not a thread.
  - A few I/O threads serve all the mailboxes, using the operating system's event-driven
    I/O (IOCP on Windows, epoll / io_uring on Linux).
  - It still looks like "the file has its own worker", but it costs a few hundred bytes,
    not 1 MB of stack.
- Questions to settle:
  - **Ordering:** requests from one sender are carried out in the order sent. Is that
    enough?
  - **Full mailbox (back-pressure):** what happens when requests arrive faster than they
    are served? The sender waits, gets an error, or the oldest requests are dropped.
  - **Reads in parallel:** many readers of a file could be served at once, like a
    read-write lock.
  - **Two resources in one step** (write a file **and** update a database, or neither): this
    needs a coordinator or a compensating step (the "saga" pattern). Atomic actions across
    services are the hard part of every actor system.
  - **Services waiting on each other** can still deadlock (A waits for B's reply, and B waits
    for A's). Timeouts (point F) turn that into an error instead of a freeze.

#### E. Weighted turns: even low priority always runs

Priorities get **shares** of the turns, not absolute precedence. For example, out of every
10 turns:
- high priority gets 5;
- medium gets 4;
- low gets 1.

A low-priority thread is still guaranteed at least 1 turn in 10. The numbers only illustrate
the idea; the real ones would be settings.

*Notes:*
- This is **weighted fair scheduling**: Linux's scheduler gives weights from "nice"
  values, and "stride" and "lottery" scheduling are textbook forms.
- The operating system decides which **OS thread** runs on a core, not Fusion. Fusion could
  apply the weights in two places it controls:
  - **its own task scheduler**, if Fusion runs many light tasks on a few OS threads, as Go
    does (a large piece of work);
  - **the order in which a service (D) takes requests from its mailbox**, which is simpler
    and gives most of the benefit.
- Weights go well with **aging**: a request that has waited long enough moves up a level.

#### F. Every thread states a timeout

Each thread or task says how long it may run, or waits for something:
- `never` is only for very important long-running threads, such as a server that waits for
  clients for as long as it is up.
- Others get a time to match their work: a quick log write or a small database update gets
  a short timeout, while a big file or a large SQL update gets a longer one.
- When the time is up, the thread is stopped and its resources are released automatically.

```fusion
Thread server = Thread.start(serveClients, priority = Priority.High, timeout = never)
Thread report = Thread.start(buildReport, timeout = 10min)
db.execute("UPDATE ...", timeout = 2s)
```

*Notes:*
- Go passes a **deadline** down to every child ("context"); in this model a child's timeout
  could never be longer than its parent's (see A).
- "Stopped" must be **cooperative** (see "Cancellation" in Section 1), or a write could be cut
  in half. Services (D) make this safe: a request either completes or is rolled back, and a
  timeout never leaves a half-written record.
- A missing timeout could be a compile error. Alternatively, it could take a default from
  `fusion.toml`, set per kind of work (quick, file, database, server).

#### G. Editor tools: seeing the threads

The editor tools Fusion will have (Task 36) would show, for each thread:
- what it is doing;
- which variables it changes;
- which files, sockets, web connections and databases it uses;
- profiling: how long it waits, how long it runs, and how full its mailbox is.

*Notes:* the compiler already knows which variables and resources each function touches, so
much of this is available **before** the program runs. That includes warnings like "two
threads change `count` without a lock". The rest comes from tracing while it runs, as in
Visual Studio's Parallel Stacks, Go's trace viewer and tokio-console.

#### H. The goal: a million requests without locking up or slowing down

The aim is that a server can handle 1,000,000 requests without freezing and without
slowing down. The pieces above serve that goal:
- Requests are **tasks**, not threads: a million tasks over a pool sized to the CPU cores
  (traps 15 and 17).
- Busy resources are **services** with bounded mailboxes. The resource controls the work,
  not the callers, so there are no shared locks to queue for (traps 1, 3 and 17), and
  back-pressure instead of collapse.
- **Weighted turns** keep low-priority work moving (traps 6 and 7).
- **Timeouts** stop anything from waiting forever (traps 3, 10 and 15).
- **The family tree** (keys) means nothing is orphaned and no error is lost (traps 12, 14 and
  15).

In short: **the resource becomes a service, instead of every caller updating it by hand.**

### 3.3 Open questions for later

1. Operating-system threads only, or Fusion's own light tasks on top (as in Go and
   Erlang)? Points B and E depend on this.
2. Mailbox full: does the sender wait, get an error, or are old requests dropped? Could
   this be a setting per resource?
3. Is the timeout required in the code, or taken from a `fusion.toml` default per kind of
   work?
4. Which traps are compile errors, which are warnings, and which are run-time errors with a
   clear message?
5. How do services stay atomic across two resources (file and database together)?
6. Is the service model the only way to reach a file, or is direct access still allowed
   for simple single-threaded programs (with no worker started)?
