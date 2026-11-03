# Fusion Memory Management: Ownership, Lifetimes and Services

> **Purpose:** Explain the memory-management model being considered for Fusion, alongside the existing `service` design. This document is intended as context for Claude when reviewing or extending the language design.
>
> **Important:** The `service` keyword and its current design are already specified in `Service.md`. This document does not replace that specification. Where it discusses possible extensions, they are labelled as proposals.

---

## 1. The three common memory-management models

Fusion is being designed around **ownership**: when an owned value goes out of scope, it is destroyed and its resources are released. This section compares that approach with C and garbage-collected languages.

### 1.1 C — manual memory management

In C, the programmer allocates and releases heap memory.

```c
#include <stdlib.h>

int main(void) {
    int *number = malloc(sizeof(int));

    if (number == NULL) {
        return 1;
    }

    *number = 100;

    free(number);
    number = NULL;

    return 0;
}
```

The programmer is responsible for matching allocation and deallocation.

Common failure modes:

| Problem | Meaning |
|---|---|
| Memory leak | Allocated memory is no longer useful but is never released. |
| Double free | The same allocation is released more than once. |
| Use-after-free | Code accesses memory after it has been released. |
| Dangling pointer | A pointer refers to an object whose lifetime has ended. |
| Buffer overflow | Code reads or writes outside the permitted memory range. |

**Strengths:** predictable control, low runtime overhead, suitable for systems programming.

**Weaknesses:** correctness depends heavily on programmer discipline; mistakes can cause crashes and security vulnerabilities.

### 1.2 GC — garbage collection

Languages such as Java, C#, Go and JavaScript use garbage collection for managed objects.

The program creates objects. A garbage collector identifies objects that can no longer be reached from live program references and reclaims them.

```java
Person person = new Person();
person.name = "Ada";

person = null; // The object may now be eligible for collection.
```

GC does not necessarily reclaim an object immediately. It also cannot reclaim an object that remains reachable, even if the program no longer finds it useful.

For example, an application can accidentally retain objects in a global list or cache forever.

**Strengths:** reduces manual memory-management errors; avoids many dangling-pointer and double-free problems for managed objects.

**Weaknesses:** collection timing and pauses can be less predictable; memory can be retained unnecessarily; logical leaks are still possible.

### 1.3 Rust — ownership and borrowing

Rust uses compile-time ownership and borrowing rules rather than a traditional tracing garbage collector.

The core rules are:

1. Every value has an owner.
2. A value has one owner at a time (shared ownership is available through explicit mechanisms such as `Rc` and `Arc`).
3. When the owner goes out of scope, the value is dropped.
4. References are checked so they cannot outlive the values they refer to.
5. Mutable access is restricted to prevent conflicting access.

```rust
fn main() {
    let name = String::from("Ada");

    print_name(&name); // Borrow; ownership is not transferred.

    println!("{}", name);
} // name is dropped here.

fn print_name(value: &String) {
    println!("{}", value);
}
```

Moving a value transfers ownership:

```rust
fn main() {
    let a = String::from("Hello");
    let b = a; // Ownership moves from a to b.

    // println!("{}", a); // Compile error: a no longer owns the value.
    println!("{}", b);
} // b is dropped here.
```

**Strengths:** catches many memory-safety errors before the program runs; deterministic destruction; no tracing GC required.

**Limitations:** safe Rust can still have logical memory leaks, for example through reference cycles or data retained indefinitely in a collection. `unsafe` code and foreign-function interfaces also require care.

---

## 2. Fusion's foundation: ownership and scope

Fusion is implementing an ownership model.

**Core rule:** an owned value is destroyed when its owner goes out of scope. Its owned resources are released as part of that destruction.

This should be the normal behaviour for ordinary variables, structs, class objects and other owned values. Developers should not need to manually call `free()` for ordinary owned memory.

Conceptually:

```fusion
void function processOrder() {
    Person customer = Person("Ada")
    Order order = LoadOrder()

    // Use customer and order.

} // customer and order are destroyed when their owners leave scope.
```

The compiler should reject a reference that would outlive the value it refers to. A value must not be destroyed while a valid borrower can still access it.

Ownership should be explicit and statically checked wherever possible. Automatic destruction is not the same as garbage collection: destruction follows ownership and scope rules, rather than a runtime tracing collector deciding when an object is unreachable.

---

## 3. Why Fusion has the `service` keyword

Ownership solves the question **who is responsible for a value and when is it destroyed?**

Concurrency introduces another question:

**What happens when multiple threads need to read or change the same value?**

Fusion's `service` design addresses this by giving shared state one owner. Requests from other threads are sent to that owner instead of allowing those threads to access and mutate the internal value directly.

The service's worker performs the requested operation. Callers communicate with it through a mailbox/request queue.

```fusion
service int counter = 0
service Person person = Person("Ada")
service Car honda = Honda(Color.Black)
```

A service is not simply a lock around a variable. It is an ownership and message-passing boundary.

### 3.1 The service ownership model

The intended model is:

- The service owns the value it manages.
- The service worker is the only writer of the value inside the service.
- Other threads do not receive direct references to the service's internal value.
- A caller sends a request through the service mailbox.
- The worker fetches and executes requests.
- A normal request returns its result to the caller when complete.
- `async` allows a caller to send a request without waiting for its reply.
- Data returned from a service is copied out (`byVal`) unless a separately safe transfer mechanism is defined.
- A borrow used by a request exists only for that request and cannot escape it.

This prevents callers from bypassing the service and modifying its internal state concurrently.

### 3.2 Request flow

```text
Caller Thread A ─┐
                 │
Caller Thread B ─┼──> Service mailbox / queue
                 │             │
Caller Thread C ─┘             ▼
                         Service worker
                               │
                         Owns the value
                               │
                         Executes request
                               │
                               ▼
                       Result / completion
                               │
                               ▼
                        Calling thread
```

The caller submits work; the service worker performs it. The calling thread does not directly execute the service's protected operation.

The implementation may use a dedicated worker or a shared worker pool, depending on the service implementation and settings. Do not assume every service must permanently create its own operating-system thread.

### 3.3 Example

```fusion
service int counter = 0

go workerA(counter)
go workerB(counter)

void function workerA(service int counter) {
    counter += 1
}

void function workerB(service int counter) {
    counter += 1
}
```

Both threads send their operations to the service. The service processes changing requests in a controlled order, so the updates cannot collide.

The exact parameter/handle syntax should follow Fusion's ownership and service specifications; this is an illustrative example of the intended flow.

---

## 4. Automatic services for shared variables

A key part of the Fusion design is that developers should not have to manually create a service for every variable that becomes shared across threads.

The compiler/runtime should recognise when a value is used across thread boundaries and introduce the appropriate service ownership mechanism.

The agreed ownership design in `Service.md` describes:

- **S5 — Temporary services:** made when two or more threads use one value; they exist while the shared use requires them, then ownership returns.
- **S7 — Multiple resources:** a thread using two or more resources gets a group service, either written by the developer or created by the compiler.
- A variable can belong to at most one service or group service at a time.
- A service owns the value while requests are being served.
- A request borrows the value for the duration of that request, or moves/copies data according to the defined thread-boundary rules.

Important distinction:

- **One shared value used by multiple threads:** a temporary `SharedService` may be created for that value.
- **One thread needs multiple resources as one coordinated unit:** a group service manages those resources together.
- **An explicitly declared `service`:** the developer intentionally declares service-managed state.

The compiler should not create a new service just because two ordinary variables are used in the same function. The trigger is shared use across threads / a thread boundary, not merely the number of variable names in an expression.

### 4.1 Temporary service lifecycle

```text
Initially:
    Variable owns its value
          │
          ▼
    Another thread needs shared access
          │
          ▼
    Compiler creates temporary SharedService
          │
          ▼
    Service becomes the owner
          │
          ├── Requests enter mailbox
          ├── Worker executes requests
          └── Results are safely returned/copied
          │
          ▼
    Last shared use ends
          │
          ▼
    Temporary service is stopped and released
          │
          ▼
    Ownership returns to the variable / original owner
```

This is the intended temporary ownership transition. The compiler must prove that no thread can still submit or execute a request before the service is stopped and ownership is returned.

---

## 5. Services and multiple resources

A service manages one resource. A group service manages multiple related resources as one unit.

For example, a worker may need both a person and a car:

```fusion
Person person = Person("Ada")
Car honda = Honda(Color.Black)

service(person, honda) carPerson

service(carPerson).run {
    honda.owner = person.name
    person.car = honda.model
}
```

While the group exists, operations on either member are routed through the group service. The group worker can perform a multi-step operation as one indivisible operation.

When the group goes out of scope, its members are released from the group and ownership returns according to the group-service rules.

A variable must not be placed in two different services/groups at the same time.

---

## 6. Service mailbox and execution rules

The mailbox is the boundary between callers and the service owner.

A request may represent:

- Reading a value.
- Changing a value.
- Calling a method.
- Performing a multi-step `run` operation.
- Writing to a log.
- Executing a database operation.
- Interacting with another managed resource.

The service executes requests according to its scheduling rules.

The current version-one design includes these principles:

1. A service completes one request before starting the next, unless its configured read policy permits parallel read-only requests.
2. A changing request runs alone.
3. Requests are ordered by the service scheduler.
4. A normal synchronous request returns its result after completion.
5. `async` sends work without waiting for the reply.
6. A timeout means the caller stopped waiting; it does not automatically mean the operation was undone.
7. A request ends as completed, failed, timed out, or cancelled.
8. The worker must not expose references to its internal state.

The current service design also includes settings such as:

- `Mailbox`
- `WhenFull`
- `Timeout`
- `Scheduler`
- `Priority`
- `Rule`
- `WorkerThreadType`
- `ThreadPool`
- `MemoryLimit`
- `Lifetime`
- `Access`
- `Shutdown`

See `Service.md` for the agreed defaults, syntax and full setting descriptions.

---

## 7. Service worker implementation choices

Fusion's service design has a `WorkerThreadType` setting:

| Type | Meaning |
|---|---|
| `AUTO` | Compiler/runtime chooses based on resource use and workload. |
| `SINGLE` | Dedicated worker(s) serving only this resource. |
| `SHARED` | Workers from a shared thread pool also serve other services. |

Examples:

```fusion
service File log = File.open("app.log")
service(log).WorkerThreadType = WorkerThreadType.SINGLE

ThreadPool dbPool = ThreadPool(10)
service Database db = Database.open("connection string")
service(db).WorkerThreadType = WorkerThreadType.SHARED
service(db).ThreadPool = dbPool
```

`SINGLE` means dedicated to that resource; it does not necessarily mean exactly one worker thread. `SHARED` avoids creating an operating-system thread for every service.

`AUTO` is the default and lets Fusion choose an implementation. The agreed design describes it as choosing shared workers as more threads use a resource and dedicated workers when the work is heavy.

A normal web request, UI action or batch operation should generally not require a permanently busy thread. The hot-path service is a separate, specialised design for workloads that genuinely need a dedicated, continuously running thread.

---

## 8. Preventing memory leaks and security problems

Ownership and scope-based destruction should eliminate or prevent many common memory errors, but they do not automatically prevent every resource leak or security vulnerability.

Fusion should combine compile-time checks with runtime controls.

### 8.1 Compile-time checks

The compiler should detect or reject:

- Use after scope / use after destruction.
- References that outlive their owner.
- Double ownership of one value.
- Invalid ownership transfers.
- Mutable access that bypasses a service.
- A service request returning or storing a reference to its internal value.
- A request capturing a short-lived borrow and using it later.
- Invalid cross-thread data transfer.
- Unsafe aliasing or conflicting mutable access.
- Waiting inside one service request for another thread's result where this can create a deadlock (the current ownership design treats this as an error).

### 8.2 Runtime controls

The runtime can additionally provide:

- Mailbox capacity limits and queue-full behaviour.
- Request timeouts and cancellation states.
- Service shutdown and queue-draining rules.
- Per-service memory limits.
- Allocation and resource-use diagnostics.
- Worker and mailbox monitoring.
- Leak diagnostics for resources that remain alive unexpectedly.
- Safe cleanup when a service stops.

### 8.3 Memory budgets — proposed extension

A possible extension is a memory budget for a scope or service.

Illustrative syntax only:

```fusion
scope Request {
    memory_limit = 50 MB

    let data = LoadOrderData()
    let result = Calculate(data)
}
```

If the budget is exceeded, Fusion could return a controlled allocation error rather than allowing unbounded growth.

A service-level `MemoryLimit` already appears in the secondary settings in `Service.md`. A general scope-level memory budget and its exact enforcement rules would need a separate design decision.

Budgets must account for nested allocations, shared values and allocations performed outside the scope. The compiler/runtime must not report a misleading budget that excludes memory the scope is actually responsible for.

### 8.4 Resource lifetimes — proposed extension

Files, sockets and database connections need deterministic cleanup too.

Illustrative syntax:

```fusion
resource DatabaseConnection {
    timeout = 30s
    max_lifetime = 5min
}
```

The resource should close when its owner is destroyed or when its defined lifecycle ends.

A timeout must not forcibly destroy a resource while another thread is still using it. Cleanup must coordinate with outstanding requests, cancellation and shutdown.

---

## 9. Proposed overall architecture

This is a conceptual architecture, not a claim that all components have already been implemented.

```text
                    FUSION COMPILER
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
      Ownership       Borrow checker    Thread-boundary
       analysis        / lifetimes         analysis
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                  SERVICE GENERATION
                          │
               ┌──────────┴──────────┐
               ▼                     ▼
         BasicService           SharedService
         / explicit             / automatic
               │                     │
               └──────────┬──────────┘
                          ▼
                  MAILBOX / SCHEDULER
                          │
                          ▼
                   SERVICE WORKER
                          │
              Owns and operates on state
                          │
                          ▼
                RESULTS / SAFE COPIES
                          │
                          ▼
                    CALLER THREAD

       Scope ends ──> Drop owner ──> Release owned resources
```

### Responsibilities

| Component | Responsibility |
|---|---|
| Ownership analyser | Tracks who owns each value. |
| Borrow/lifetime analyser | Ensures references do not outlive owners. |
| Thread-boundary analyser | Determines what may cross between threads. |
| Service generation | Creates the required explicit or temporary service. |
| Mailbox/scheduler | Queues and orders requests. |
| Service worker | Executes requests as the service's owner. |
| Scope/drop mechanism | Destroys owned values and releases their resources. |
| Runtime diagnostics | Reports resource retention, queue pressure and memory usage. |

---

## 10. Design principles to preserve

1. **Ownership is the foundation.** Do not replace the ownership model with a traditional tracing GC.
2. **Scope determines destruction.** When the owner goes out of scope, its owned value is destroyed, subject to the compiler-proven lifetime rules.
3. **One owner at a time.** Ownership may move, but two independent owners must not both be responsible for destroying the same value.
4. **Borrowing is temporary.** A borrow cannot outlive its owner or escape a service request when it refers to service-internal state.
5. **Services own shared state.** Other threads communicate through requests, not direct references.
6. **The worker performs the request.** The caller submits work to the mailbox; it does not directly execute the service's protected operation.
7. **Automatic services are compiler-generated.** Developers should not have to write boilerplate for every shared variable.
8. **Do not create services unnecessarily.** A value used by one thread should remain an ordinary value unless explicitly declared otherwise.
9. **One resource versus multiple resources.** A service manages one resource; a group service manages a coordinated set.
10. **Do not promise impossible guarantees.** Ownership can prevent major classes of memory errors, but logical leaks, unbounded data growth and external resource failures still need design and diagnostics.

---

## 11. Questions for design review

These points should be checked against the existing Fusion decisions before implementation. They are questions, not settled changes.

1. **Temporary-service transition:** What exact compiler analysis proves that a value is now used by multiple threads and must be moved into a `SharedService`?
2. **Ownership return:** How does the runtime prove that every request has completed and no thread retains a handle before returning ownership to the original variable?
3. **Scope exit:** Does leaving scope wait for outstanding service requests, drain the mailbox, cancel requests, or follow a configurable shutdown policy?
4. **Request failure:** Which operations can be rolled back, and how are external side effects (such as a log write or socket send) reported?
5. **Read concurrency:** How are parallel read-only requests proven not to mutate state indirectly?
6. **Memory accounting:** How are nested services, shared allocations and thread-pool allocations charged to `MemoryLimit`?
7. **Deadlock prevention:** How does the compiler identify a service request that waits for another thread or service in a way that can deadlock?
8. **Resource cleanup:** How are database connections, files, sockets and locks closed when their owning service or scope ends?
9. **Error handling:** What happens if cleanup itself fails?
10. **Unsafe/FFI boundary:** What explicit rules apply when Fusion calls C libraries or receives pointers from foreign code?

---

## 12. Existing Fusion design documents to treat as authoritative

Use these documents as the source of truth when refining this proposal:

- `Ownership.md` — ownership rules and thread-boundary rules.
- `Notes/Ownership_Decisions_2026-10-31.md` — recorded ownership decisions.
- `Service.md` — service keyword, mailbox, worker, settings, service classes, group services and hot-path services.
- `Concurrency.md` — concurrency background and design reasoning.
- `Concurrency_Traps.md` — concurrency traps and failure modes.
- `FEATURES.md` — implementation status and task tracking, including Task 42.

**Status distinction:** The ownership and service rules described in the existing design documents are the agreed design. The general architecture diagram and the memory-budget/resource-lifetime extensions in this document are explanatory or proposed material; they should not silently be treated as implemented features or new decisions.
