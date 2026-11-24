Memory allocation is one of the most important concepts to understand when designing Fusion. It determines **where data lives, how long it exists, who owns it, and when its memory can be reused or released.**

The traditional programming model usually talks about three main memory areas:

1. Stack
2. Heap
3. Static/Data memory

However, these aren't the only ways to manage memory. Modern languages such as Rust, Go, Swift and Zig introduce different ownership, lifetime and allocation models.

There are also newer approaches that don't fit neatly into the traditional stack/heap model.

# **1. Traditional memory allocation**

Let's first understand the basic memory layout of a running program.

[cs 465 Introduction to Security and Privacy](https://images.openai.com/static-rsc-4/pst7hME2IVHOWY1M4PBUyQLYvhVBujKyd5GMu3D_xro74BCRW8-jjnj3SnZSlwvmtBRiA3QAbI5PmP5z4gyZCpSOgqP-1v52ees7VcZbUnLwFeSd6PHYxUhdmLd43BaiXsCjfxkOhv9ZHyS8jY7BhpnKw-0xY0G51IDAFpdTXuM?purpose=inline)

[cs465.zappala.org](https://cs465.zappala.org/winter2025/notes/stack-overflows/?utm_source=chatgpt.com)

A simplified process memory layout looks like this:

| Memory area | Purpose                                   | Lifetime               |
| ----------- | ----------------------------------------- | ---------------------- |
| Text / Code | Compiled program instructions             | Usually entire process |
| Data        | Initialized global/static variables       | Entire process         |
| BSS         | Uninitialized or zero-initialized globals | Entire process         |
| Heap        | Dynamically allocated objects             | Until released         |
| Stack       | Function calls and local variables        | Until function returns |

These are logical memory regions. Actual layouts vary between operating systems, architectures and runtimes.

## **1.1 Stack allocation**

The stack is used for function calls and temporary local data.

Example in C:

```
void calculate() {
    int a = 10;
    int b = 20;
    int result = a + b;
}
```

When `calculate()` executes:

- Space is reserved for its local variables.
- The function operates on that memory.
- When the function returns, its stack frame is removed.
- The memory can immediately be reused.

Think of it as a pile of plates: the last plate added is the first removed (LIFO).

[PPT - Buffer Overflows PowerPoint Presentation, free download - ID:2533529](https://images.openai.com/static-rsc-4/cU5ejYh7M0HPgAb03WzYoYcdGXiPAQyIoPF_xpUMEDgo_I1MvRTgbHfdL-sKnIYgQO-8C1yDvFR8yFCMUQH2Qcx-FId1M0PQYMi5vz_t68KvunbJYVhOHD51U0YQUpvGGXQiblfCo2abfOt4JBEHHIlYkiZhm9rnueroNKGVbH0?purpose=inline)

[slideserve.com](https://www.slideserve.com/nellie/buffer-overflows?utm_source=chatgpt.com)

**Advantages**

- Very fast allocation and deallocation.
- No individual memory release required.
- Predictable lifetime.
- Good cache locality in many cases.

**Disadvantages**

- Data normally cannot outlive its stack frame.
- Stack space is limited.
- Returning pointers to local stack variables creates dangling references.

## **1.2 Heap allocation**

The heap is used when memory needs to survive beyond the current function or when its size/lifetime is dynamic.

Example in C:

```
int* createBalance() {
    int* balance = malloc(sizeof(int));

    *balance = 1000;

    return balance;
}
```

The pointer variable itself is local to the function, but the allocated integer lives on the heap.

The caller must eventually release it:

```
int* balance = createBalance();

printf("%d", *balance);

free(balance);
```

[Cohesyve | AI-Powered Dynamic Skill Assessments for Hiring](https://images.openai.com/static-rsc-4/u568-2MB0GzDkWbKSDOKwzD-H9jdInq0vg4UChXsdE8n59SjC-F7GMh0hmT7J_1_bh4hSD3XQOFv54Po-dOBZG98MQmXzFXV5NCwFbm-8MTfXhQvhPEU3iXpg7-j7vrNYttl7WKPBXfvEHa91e_DHLy67oQaydX9d9k61FHTrHg?purpose=inline)

[cohesyve.com](https://www.cohesyve.com/blog/interview-question-in-c-language?utm_source=chatgpt.com)

**Advantages**

- Dynamic memory sizes.
- Data can outlive the function that created it.
- Suitable for complex data structures.
- Can be shared between different parts of a program.

**Disadvantages**

- Allocation is generally more expensive than stack allocation.
- Requires lifetime management.
- Can cause memory leaks.
- Can cause fragmentation.
- Incorrect release can cause use-after-free bugs.

## **1.3 Static / Data allocation**

Static memory is allocated for the lifetime of the program.

Example in C:

```
int globalBalance = 1000;

static int transactionCount = 0;

void process() {
    transactionCount++;
}
```

Both variables exist for the entire process.

There are two commonly discussed sections:

- `.data`: initialized global/static variables.
- `.bss`: zero-initialized or uninitialized global/static variables.

Constants and read-only data may be stored in separate sections such as `.rodata`.

**Advantages**

- Predictable lifetime.
- No repeated allocation.
- Useful for configuration and application-wide state.

**Disadvantages**

- Memory stays allocated for the program's lifetime.
- Can introduce unwanted global dependencies.
- Can create concurrency problems when mutable global state is shared.

# **2. Other memory allocation models**

This is where things get interesting. Not every language relies on developers manually allocating heap memory and automatically releasing stack memory.

## **2.1 Garbage Collection (GC)**

Java, C#, Go, JavaScript, Python

Garbage collection automatically identifies memory that is no longer reachable and reclaims it.

Example in Java:

```
public void calculate() {
    Account account = new Account();
    account.balance = 1000;
}
```

When the method returns, the local reference disappears. If nothing else references the object, the garbage collector can eventually reclaim it.

Important: GC does not necessarily release memory immediately when an object becomes unused.

[Garbage collection in Data Structure: Optimizing Memory](https://images.openai.com/static-rsc-4/G8Sy1yAZRJ0sGiAgB50KTPmPN37zkO45WHI4k6rechoMUPb5htmnokF1aPYVHIgDsvQlzWwBxIO453WjFzDdEj4FlYrOti0Zr1OCjvlZwTmIqSM4IWOqTSNmUAAvOfuOkxTTAoErYh0r6nzjkcLVW7smjvo2DNrp81Sb9LB4ffY?purpose=inline)

[educba.com](https://www.educba.com/garbage-collection-in-data-structure/?utm_source=chatgpt.com)

Common GC techniques:

- Mark and Sweep.
- Generational collection.
- Copying collectors.
- Concurrent collection.

**Advantages**

- Reduces manual memory management.
- Prevents many use-after-free errors.
- Easier for complex object graphs.

**Disadvantages**

- Collection introduces runtime work.
- Memory usage can be less predictable.
- Some collectors introduce pauses.
- Unwanted references can keep unused objects alive.

## **2.2 Reference Counting**

Swift, Python, C++ shared_ptr

Each object maintains a count of how many references point to it.

Example in Swift:

```
class Account {
    var balance = 1000
}

var accountA: Account? = Account()
var accountB = accountA

accountA = nil
accountB = nil
```

When the last strong reference disappears, Swift can immediately destroy the object.

**Advantages**

- Predictable destruction when the count reaches zero.
- No traditional tracing garbage collection required.
- Useful for resource management.

**Disadvantages**

- Reference-count updates have a cost.
- Circular references can prevent reclamation.
- Weak and unowned references are needed in some designs.

Swift uses Automatic Reference Counting (ARC), while Python combines reference counting with a cyclic garbage collector.

## **2.3 Ownership and Borrowing**

Rust

Rust takes a fundamentally different approach.

Instead of relying on a garbage collector, it tracks ownership and borrowing through its type system.

```
fn main() {
    let account = String::from("Account A");

    let other = account;

    // account is no longer valid here.
    println!("{}", other);
}
```

When ownership moves to `other`, the original variable can no longer access the allocation.

Rust also supports borrowing:

```
fn print_account(account: &String) {
    println!("{}", account);
}
```

The compiler checks that references cannot outlive their owners.

**Advantages**

- No traditional GC required.
- Strong compile-time lifetime checking.
- Safe concurrent memory access.
- Predictable destruction.

**Disadvantages**

- More complex programming model.
- Ownership transfers and lifetimes require learning.
- Some architectures require additional design work to satisfy the borrow checker.

## **2.4 Arena Allocation**

Zig, Rust, C and C++ libraries

Arena allocation is a very interesting alternative.

Instead of individually allocating and releasing hundreds or thousands of objects, you allocate them together inside a memory region.

Example concept:

```
Create Arena
    |
    +-- Allocate Object A
    |
    +-- Allocate Object B
    |
    +-- Allocate Object C
    |
    +-- Allocate Object D
    |
Destroy Arena
    |
All objects released together
```

Example in Zig:

```
var arena = std.heap.ArenaAllocator.init(
    std.heap.page_allocator
);

defer arena.deinit();

const allocator = arena.allocator();

const account = try allocator.create(Account);
const ledger = try allocator.create(Ledger);
```

When the arena is destroyed, all its allocations are released together.

You don't need to individually free `account` and `ledger`.

**Advantages**

- Extremely fast allocation.
- Simple bulk cleanup.
- Reduced fragmentation in many workloads.
- Excellent for temporary groups of objects.

**Disadvantages**

- Individual objects cannot normally be released.
- Memory remains allocated until the arena is destroyed.
- Long-lived arenas can waste memory.

This could be particularly interesting for Fusion services.

# **3. Less traditional memory models**

These are particularly interesting because they offer alternatives to the conventional stack/heap approach.

## **3.1 Region-based memory management**

Very relevant to Fusion

Region-based memory management is related to arena allocation, but is a broader memory-management strategy.

Instead of managing each object individually, objects belong to a particular region.

For example:

```
Application
    |
    +-- Region A (Configuration)
    |       +-- Settings
    |       +-- Options
    |
    +-- Region B (Transaction)
    |       +-- Account
    |       +-- Ledger
    |       +-- Audit
    |
    +-- Region C (Reporting)
            +-- Report
            +-- Results
```

When the transaction finishes, Region B can be released as a whole.

The important concept is that the lifetime of the region determines the lifetime of its allocations.

This is sometimes called *region-based memory management* or *lifetime-based allocation*.

**Why I like this for Fusion:**

It fits naturally with our service ownership model.

A service could have a managed memory region containing:

- Its private state.
- Temporary working objects.
- Internal buffers.
- Cached data.

However, I would distinguish between service-owned resources and temporary service allocations. They don't necessarily need identical lifetimes.

## **3.2 Object Pools**

Used in games, servers and high-performance systems

Instead of continuously allocating and destroying objects, an application creates a collection of reusable objects.

For example:

```
Object Pool
    |
    +-- Object 1 (Available)
    +-- Object 2 (In Use)
    +-- Object 3 (Available)
    +-- Object 4 (In Use)
    +-- Object 5 (Available)
```

When an operation needs an object, it takes one from the pool.

When finished, it returns the object.

Example:

```
class ObjectPool {
    constructor(create, size) {
        this.available = Array.from(
            { length: size },
            create
        );
    }

    acquire() {
        return this.available.pop() ?? null;
    }

    release(object) {
        this.available.push(object);
    }
}
```

**Advantages**

- Reduces repeated allocations.
- Can improve performance.
- Makes resource limits easier to control.
- Useful for network connections, database connections and temporary objects.

**Disadvantages**

- Objects must be reset correctly.
- Pool exhaustion needs handling.
- Objects can accidentally be reused while still referenced.

## **3.3 Stackless / Coroutine-based execution**

Go, Kotlin, C#, JavaScript

This is slightly different from a memory allocation model, but it has significant implications for memory.

Traditional threads have their own stacks.

A coroutine or lightweight task can suspend execution without necessarily keeping a full operating-system thread occupied.

For example:

```
suspend fun processOrder() {
    val order = loadOrder()

    saveOrder(order)
}
```

The coroutine can suspend while waiting for `loadOrder()` and resume later.

Its execution state is preserved, but it doesn't need to block an entire operating-system thread.

Some implementations store suspended execution state in heap-allocated structures or compiler-generated state machines.

### **Go is particularly interesting**

Go uses goroutines.

Each goroutine has its own small stack that can grow as required.

This is different from the traditional model of allocating a large, fixed-size stack for every operating-system thread.

Go manages the growth of these stacks automatically.

This makes it practical to run very large numbers of goroutines.

**For Fusion:** We could have lightweight service operations that suspend while waiting for network or database operations, without reserving a dedicated operating-system thread for each service.

## **3.4 Per-process heaps – Erlang / BEAM**

Interesting alternative

Erlang uses the BEAM virtual machine.

Its processes are extremely lightweight and have their own isolated heaps and garbage collection.

Conceptually:

```
BEAM Virtual Machine
    |
    +-- Process A
    |      +-- Private Heap
    |      +-- Stack
    |      +-- Mailbox
    |
    +-- Process B
    |      +-- Private Heap
    |      +-- Stack
    |      +-- Mailbox
    |
    +-- Process C
           +-- Private Heap
           +-- Stack
           +-- Mailbox
```

This is quite different from the traditional Java model, where many application objects exist in a shared managed heap.

Benefits include:

- Isolated process state.
- Independent garbage collection.
- Reduced interference between processes.
- Message passing instead of directly sharing mutable objects.

There are implementation optimisations, including shared immutable data, so the diagram is conceptual rather than a complete description of BEAM's internal memory layout.

**For Fusion:** This is an excellent model to study if we want services to have isolated state and communicate through messages.

# **4. How languages approach memory differently**

Here is a comparison of the approaches.

| Language   | Main memory approach                    | Garbage collection |
| ---------- | --------------------------------------- | ------------------ |
| C          | Stack + manual heap                     | No                 |
| C++        | Stack + manual/RAII heap                | No                 |
| Java       | Stack + managed heap                    | Yes                |
| C#         | Stack + managed heap                    | Yes                |
| Python     | Managed heap + references               | Yes                |
| JavaScript | Managed heap                            | Yes                |
| Go         | Growing goroutine stacks + managed heap | Yes                |
| Rust       | Ownership + borrowing                   | No                 |
| Swift      | ARC + stack/heap                        | ARC                |
| Zig        | Explicit allocators + stack/heap        | No                 |
| Erlang     | Per-process heaps                       | Yes                |

One important clarification: these languages don't necessarily have completely different physical memory hardware or memory regions. Many use the same underlying operating-system virtual memory mechanisms.

What differs is **how the language decides to allocate, share, track and release memory**.

# **5. What I would consider for Fusion**

This is where I think we can do something interesting.

Our Service concept already gives us a natural ownership boundary. We could use that boundary to introduce a more sophisticated memory-management system.

I would investigate five allocation types for Fusion.

**Proposed Fusion memory architecture**

**1. Stack Memory**

Automatic

- Local variables.
- Temporary calculations.
- Function execution state.

**2. Service Memory**

Managed ownership

- Service-owned resources.
- Persistent service state.
- Grouped resource ownership.

**3. Region / Arena Memory**

Bulk allocation

- Temporary operation data.
- Intermediate calculations.
- Bulk cleanup.

**4. Shared Memory**

Controlled sharing

- Immutable data.
- Explicitly shared resources.
- Cross-service communication.

**5. Static Memory**

Application lifetime

- Constants.
- Global configuration.
- Static lookup tables.

These would be logical ownership and allocation categories, not necessarily five separate physical memory regions.

## **5.1 Example: Fusion Service memory**

Imagine:

```
service transaction(account, ledger) {

    run {
        var amount = 500
        var result = account.balance - amount

        if (result >= 0) {
            account.balance = result
            ledger.record(amount)
        }
    }
}
```

We could have:

| Variable/resource           | Proposed memory | Lifetime    |
| --------------------------- | --------------- | ----------- |
| `amount`                    | Stack           | Operation   |
| `result`                    | Stack           | Operation   |
| `account`                   | Service-owned   | Service     |
| `ledger`                    | Service-owned   | Service     |
| Temporary ledger buffers    | Arena           | Operation   |
| Shared currency definitions | Static/shared   | Application |

When `run` finishes:

- Stack variables disappear.
- Temporary arena allocations are released.
- Account and ledger remain available.
- The service continues accepting requests.

This is a clean separation of responsibilities.

## **5.2 An additional idea: Service lifecycle allocation**

We could introduce explicit lifecycle scopes:

```
service transaction(account, ledger) {

    onCreate {
        // Allocate service resources
    }

    run {
        // Operation-scoped memory
    }

    onReset {
        // Clear temporary state
    }

    onDestroy {
        // Release owned resources
    }
}
```

This could give Fusion predictable resource lifetimes without requiring developers to manually free every allocation.

One caution: `onDestroy` should be deterministic, but the language must also handle exceptions, cancellation and application shutdown. We shouldn't rely on a garbage collector eventually calling it.

# **6. Is this an invented way of doing things?**

No. These approaches have evolved over decades.

A rough historical progression:

| Period            | Development                                                           |
| ----------------- | --------------------------------------------------------------------- |
| Early programming | Static memory and stack allocation                                    |
| 1960s–70s         | Dynamic heap allocation becomes widespread                            |
| 1960s onward      | Garbage collection research and implementations                       |
| 1980s–90s         | Object pools, reference counting and RAII become prominent            |
| 2000s             | Region-based allocation and ownership-oriented designs gain attention |
| 2010s             | Rust ownership, Go goroutines, modern actor systems                   |
| Today             | Hybrid memory management, arenas, ownership and managed runtimes      |

There isn't one universally best allocation model. Each solves different problems.

**My recommendation for Fusion:**

I would not invent a completely new memory allocator initially. I would combine proven approaches:

1. Stack allocation for short-lived local data.
2. Service ownership for persistent mutable resources.
3. Arena allocation for temporary operation data.
4. Reference-counted or explicitly shared immutable resources where appropriate.
5. Static allocation for application-wide constants.
6. Explicit ownership and lifetime checking by the compiler.

The particularly interesting part is that Fusion Services could become the foundation for memory management itself.

Instead of asking only:

*"Where should this variable be allocated?"*

The compiler could also ask:

*"Who owns this resource, which operations can access it, and when is its lifetime finished?"*

That is a much more powerful design question, and it aligns directly with what we're trying to achieve with Fusion.