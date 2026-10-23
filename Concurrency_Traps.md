# Concurrency traps - overview

A one-page overview of what goes wrong when code runs on several threads, the general fix
for each problem, and which of Fusion's concurrency principles prevents it. It is meant as a
quick reference and template for people and AI tools working on Fusion. The full
explanation, with code, is in [Concurrency.md](Concurrency.md):
- Section 2: the traps;
- Section 3: the principles and real-world cases;
- Section 4: other languages.

**Status:** these are ideas for a future task (FEATURES.md Task 42), not built. This file may
change as the design develops.

**Fusion's concurrency goal:** a million requests on one machine with many cores, with no
data races by construction, deadlocks and freezes prevented by rules (any that slip through
become clear errors), and no slowdown, using as little memory and CPU as possible.
Version one of `service`: [Concurrency.md](Concurrency.md) section 3.11. The core idea: **a resource becomes a service, instead of every caller updating it
by hand.** Manual locking is a last resort.

---

#### The principles

| | Principle | In one line |
|---|---|---|
| P1 | Resource as Service | One coordinator owns each resource; everyone else sends requests (`service` keyword) |
| P2 | One Thread, One Resource | No thread holds or waits on two resources; things that must change together form one unit |
| P3 | The Hierarchy Decides | When two threads want one resource, a rule (the senior thread key, by default) picks the winner |
| P4 | Every Wait Has a Deadline | Every thread, request and wait has a timeout; a freeze becomes an error |
| P5 | Owned Threads | Every thread has a parent; parents wait for, cancel, and get errors from their children |
| P6 | Bounded Mailboxes | Every queue has a size and a stated "when full" policy |
| P7 | The Service Owns Its Schedule | The service decides the order and what runs in parallel |
| P8 | Weighted Turns | Priorities get shares of the turns; low priority still runs; priority is inherited |
| P9 | Services Never Block on Each Other | While handling a request, a service calls only down the hierarchy, or sends without waiting |
| P10 | Visible Concurrency | Editor tools and compiler warnings show who touches what |

A deadlock needs four conditions at once (Coffman, 1971): mutual exclusion, hold and wait,
no preemption, and circular wait. P2 breaks **hold and wait**, and P3 breaks **no
preemption** and **circular wait**.

---

#### The traps

| # | Trap | What goes wrong | General solution | Principles |
|---|---|---|---|---|
| 1 | Race condition | Two threads change one value at once; updates are lost (`count += 1`) | Remove shared changeable state, or make each change indivisible | P1, P10 |
| 2 | Check-then-act | The situation changes between a check and the action (an overdrawn account) | A decision and its action form one indivisible step | P1, P7 |
| 3 | Deadlock | Two threads each hold what the other waits for; the program freezes silently | Break the waiting circle: an order on resources, or no waiting while holding | P2, P3, P4, P9 |
| 4 | Forgotten unlock | An early return or error leaves a lock held forever | Tie a resource's release to a scope | P1 (no caller locks), `final` clean-up |
| 5 | Livelock | Threads keep giving way to each other and never progress | Break the symmetry between the competing threads | P3 |
| 6 | Starvation | One thread never gets its turn | Bounded waiting: fairness and aging | P8, P6 |
| 7 | Priority inversion | Important work waits behind unimportant work holding a lock | Whoever blocks important work temporarily becomes important | P8, P1 |
| 8 | Change never seen | One thread's write never becomes visible to another (a plain stop flag) | Communicate only through operations that synchronize | P1 |
| 9 | Collection changed by two threads | Lost items, crashes or corrupted memory in a shared list or map | Confinement (one owner) or immutability (snapshots) | P1 |
| 10 | Channel with nobody receiving | A send or receive waits forever | Every channel has a defined lifetime and owner; every wait has a limit | P4, P5, P6 |
| 11 | Blocking inside async | One slow call freezes every task on the shared thread | Keep blocking work and waiting work on separate executors | P7, P1 |
| 12 | Forgetting `await` | A task's result and error are silently dropped | No orphan tasks: each is awaited, or explicitly detached | P5 |
| 13 | Sync-over-async deadlock | The main thread blocks on work that needs the main thread | Never block a thread that the awaited work needs | P9, P4 |
| 14 | Errors lost in another thread | A background thread's error never reaches the caller | Errors travel with results back to whoever waits | P5 |
| 15 | Thread leaks, too many threads | Threads that never end, or one per request, exhaust memory | Bounded resources and admission control; every task has an owner and an end | P5, P6 |
| 16 | UI changed from another thread | Random crashes and drawing glitches | Thread affinity: the UI belongs to one thread and is reached only by messages | P1 |
| 17 | Contention, false sharing | Correct but slow: threads queue for one lock, or fight over one cache line | Locality: keep hot data per thread; share as little and as briefly as possible | P7, P1, P10 |

---

#### Real-world cases

| # | Case | System / language | Traps | Prevented by | Link |
|---|---|---|---|---|---|
| 1 | Several processes writing one log file | Python logging | 1, 9 | P1 | [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes) |
| 2 | Two transfers deadlock on two rows | PostgreSQL | 3 | P3, P7 | [PostgreSQL - Deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-DEADLOCKS) |
| 3 | A shared map crashes a log shipper | Go, Grafana Promtail | 1, 9 | P1 | [grafana/loki#3571](https://github.com/grafana/loki/issues/3571) |
| 4 | A HashMap loops forever at 100% CPU | Java 7 | 9 | P1 | [DZone - Resizing the HashMap](https://dzone.com/articles/resizing-the-hashmap-dangers-ahead) |
| 5 | Engine hangs on start-up; 171 real Go bugs (58% of freezes from message passing) | Go, Docker / Kubernetes / etcd / gRPC | 3, 10 | P9, P4, P1 | [moby/moby#25384](https://github.com/moby/moby/pull/25384), [go-concurrency-bugs](https://github.com/system-pclub/go-concurrency-bugs) |
| 6 | Servers freeze: virtual threads pinned while waiting for a lock | Java 21, Netflix | 3, 15 | P2, P10 | [Netflix Tech Blog](https://netflixtechblog.com/java-21-virtual-threads-dude-wheres-my-lock-3052540e231d) |
| 7 | The UI freezes waiting for its own async work | C# / .NET | 13 | P9, P4 | [Stephen Cleary - Don't Block on Async Code](https://blog.stephencleary.com/2012/07/dont-block-on-async-code.html) |
| 8 | One slow request stalls every client | Node.js | 11 | P1, P7 | [Node.js - Don't Block the Event Loop](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop) |
| 9 | The lander keeps resetting itself (priority inversion) | Mars Pathfinder, 1997 | 7 | P8, P1 | [Glenn Reeves - What really happened on Mars](https://www.cs.cornell.edu/courses/cs614/1999sp/papers/pathfinder2.html) |
| 10 | The alarm system silently stops; part of the 2003 blackout | GE XA/21 energy management | 1 | P1, P10 | [The Register](https://www.theregister.com/2004/04/08/blackout_bug_report/) |
| 11 | 105 real bugs: a third break the intended order, 34% span several variables | MySQL, Apache, Mozilla, OpenOffice | 1, 2 | P1, P2 | [Lu et al. 2008 (PDF)](https://www.cs.columbia.edu/~junfeng/10fa-e6998/papers/concurrency-bugs.pdf) |
| 12 | 2-3 million connections per server, done right | WhatsApp on Erlang | - | P1, P5, P6 | [FreeBSD Foundation - WhatsApp](https://freebsdfoundation.org/testimonial/whatsapp/) |

---

#### How to use this file

- **Designing a concurrency feature:** check which traps it could cause, and that a
  principle covers each one.
- **Reviewing concurrent code:** go through the traps column, and look for the "What goes
  wrong" pattern.
- **Adding a trap, principle or case:** add a row here, and the full write-up in
  `Concurrency.md` (CLAUDE.md asks for both to be kept in step).
