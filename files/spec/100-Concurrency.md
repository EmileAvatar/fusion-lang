[< 090 Memory](090-Memory.md) | [Index](index.md) | [110 Generics >](110-Generics.md) <!-- nav -->

# 100 Concurrency

Contents: [Threading Hierarchy](#threading-hierarchy) | [Two Concurrency Approaches](#two-concurrency-approaches) | ["Share Memory by Communicating" Explained](#share-memory-by-communicating-explained) | [Try-With-Resources Pattern](#try-with-resources-pattern) | [Thread Interrupt Handling](#thread-interrupt-handling) | [Async/Await Pattern](#asyncawait-pattern) | [One writer, temporary services, hot paths](#one-writer-temporary-services-hot-paths) | [Thread Safety Summary](#thread-safety-summary) | [Async and Concurrency](#async-and-concurrency)

## Threading and Concurrency Model

**Status:** [DESIGN] files/FEATURES.md Task 42. The current design is newer than this section - where they
differ, these win:
- [files/Concurrency.md](../Concurrency.md) - terms, traps, the model, other languages
- [files/Concurrency_Traps.md](../Concurrency_Traps.md) - the overview tables
- [files/Service.md](../Service.md) - the `service` keyword: a shared resource becomes a service instead of
  every caller locking it

Description: Hybrid concurrency model supporting both message passing and shared memory.

Note: This is a high-level overview. Full threading specification will be in a separate detailed document.

---

### Threading Hierarchy

Description: Layers of concurrent execution units.

* **System**: Operating system managing all processes
* **Process**: Isolated execution with own memory space
* **Thread**: Lightweight unit within process, shares memory
* **Task/Goroutine**: User-space thread, very lightweight
* **Channel**: Communication queue between threads

Extended Hierarchy: System → Process → Thread Pool → Thread → Task/Job → Channel/Queue

---

### Two Concurrency Approaches

Description: Fusion supports both paradigms for maximum flexibility.

---

#### Approach 1: Message Passing (Recommended)

Description: Share memory by communicating (Go-style).

* **Philosophy**: Don't share memory, send messages instead
* **Benefits**: No locks needed, no race conditions, clearer ownership
* **Use**: Default approach for most concurrent code

**How It Works**

* Threads don't share variables directly
* Data sent through channels
* Only one thread owns data at a time
* Ownership transfers through channel

**Analogy**: Sending emails vs writing on shared whiteboard

```
// Create channel
Channel<Task> taskQueue = Channel.create<Task>()

// Producer thread
void function producer()
    for i in range(100)
        Task task = createTask(i)
        taskQueue.send(task)  // Send to channel
    end loop

// Consumer thread
void function consumer()
    while true
        Task task = taskQueue.receive()  // Receive from channel
        processTask(task)
    end loop
```

---

#### Approach 2: Shared Memory (Traditional)

Description: Communicate by sharing memory (requires locks).

* **Philosophy**: Multiple threads access same variables
* **Requirement**: Must use locks/mutexes for synchronization
* **Benefits**: Sometimes more natural for certain problems
* **Use**: When message passing doesn't fit

**How It Works**

* Threads access shared variables
* Mutex locks prevent race conditions
* Must remember to lock/unlock

```
// Shared counter with mutex
class Counter
    private int count
    private Mutex mutex
    
    void function increment()
        mutex.lock()
        count += 1
        mutex.unlock()
    
    int function getCount()
        mutex.lock()
        int value = count
        mutex.unlock()
        return value
```

---

### "Share Memory by Communicating" Explained

Description: Understanding Go's concurrency philosophy.

**Traditional Approach** (Shared Memory)

* Multiple threads write to same variable
* Use mutex to prevent conflicts
* Easy to forget locks → bugs
* Easy to deadlock

```
// Shared variable approach
int sharedCounter = 0
Mutex lock

// Thread 1
lock.acquire()
sharedCounter += 1
lock.release()

// Thread 2
lock.acquire()
sharedCounter += 1
lock.release()
```

**Go's Approach** (Message Passing)

* Don't share variables
* Send data through channels
* Only one thread "owns" data
* No locks needed

```
// Channel approach
Channel<int> updates = Channel.create<int>()

// Thread 1 sends update
updates.send(1)

// Thread 2 sends update
updates.send(1)

// Counter thread receives all updates
int counter = 0
while true
    int update = updates.receive()
    counter += update
end loop
```

---

### Try-With-Resources Pattern

Description: Automatic resource locking to prevent race conditions and deadlocks.

* **Automatic Locking**: Compiler adds locks automatically
* **No Manual Lock/Unlock**: User doesn't need to manage locks
* **Race Condition Prevention**: Automatic synchronization
* **Deadlock Prevention**: Smart lock ordering by compiler

**How It Works**

* When thread/channel tries to access resource, it's locked automatically
* Resource unlocked when done (scope ends or exception thrown)
* Compiler analyzes code to prevent deadlocks
* User can add custom locks if needed

**File Handling Example**

```
// Automatic locking for file access
using file = openFile("data.txt")
    file.write("Some data")
    file.flush()
// File automatically closed and unlocked

// Multiple threads accessing same file
// Thread 1
using file = openFile("shared.txt")
    file.write("Thread 1 data")
// Unlocked

// Thread 2 (waits for Thread 1 to finish)
using file = openFile("shared.txt")
    file.write("Thread 2 data")
// Unlocked
```

**Object/Variable Locking Example**

```
class Counter
    private int count
    
    // Compiler automatically adds locking
    void function increment()
        using this  // Lock entire object
            count += 1
        // Unlocked
    
    int function getCount()
        using this
            return count

// Multiple threads calling increment() - automatically synchronized
Counter counter = Counter()

// Thread 1
counter.increment()  // Locked during execution

// Thread 2
counter.increment()  // Waits for Thread 1, then executes
```

**Manual Locking (When Needed)**

```
// User can specify custom locking
Mutex customLock = Mutex()

void function criticalSection()
    using customLock
        // Protected code
        sharedVariable += 1
    // Unlocked
```

**Compiler Optimizations**

* Analyzes resource access patterns
* Determines minimal locking needed
* Orders locks to prevent deadlocks
* Adds locks only where necessary for performance

---

### Thread Interrupt Handling

Description: Cooperative multitasking via loop checks.

* Threads can signal other threads to stop/pause
* Checked at `end loop` automatically
* Graceful shutdown possible

```
for item in largeDataset
    processItem(item)
    
end loop with
    check interrupt(signal, data)
        if signal == InterruptSignal.Shutdown
            saveProgress()
            cleanup()
            exit loop
        
        if signal == InterruptSignal.Pause
            waitForResume()
            continue loop
```

---

### Async/Await Pattern

Description: Modern asynchronous programming for I/O operations.

```
// Async function
async Spaceship, Error function downloadShipData(string url)
    Response response = await http.get(url)
    
    if response.statusCode != 200
        return null, Error("HTTP error: {response.statusCode}")
    
    string data = await response.readBody()
    Spaceship ship = parseShipData(data)
    return ship, null

// Calling async function
Spaceship ship, Error err = await downloadShipData("https://api.ships.com/ship/1")
if err
    print("Error: {err.message}")
else
    print("Loaded ship: {ship.Name}")
```

---

### One writer, temporary services, hot paths

**Status:** [PLANNED 42.18-42.25] designed 2026-10-31 (user) - `files/Service.md`,
`files/Concurrency.md` 3.13, `files/Ownership.md` sections 5-7.

* **One writer:** a service's worker thread is the only writer of what it holds
* **Temporary services:** two or more threads using one variable - the compiler makes
  `service(acc)`; it owns the value, the threads borrow it, one call at a time; ownership
  comes back when the last thread ends. `[concurrency] autoService = "on"` (a note) | "warn" | "off"
* **Readers in parallel:** a readonly signature or call makes a request a read
* **send / sync:** send - a value goes to another thread and the sender no longer has it;
  sync - many threads use it through a service. Worked out by the compiler
* **The `Service` interface:** `send`, `T fetch()`, ...; BasicService, SharedService,
  FileService, DatabaseService, HotPathService implement it
* **`hotpath service T x = ... { }`:** a dedicated thread that never sleeps - no allocating,
  blocking or counting (checked), an input ring, pinned to a core. `hotpath void function f()`:
  the checks without the thread. Defaults in `[hotpath]`

---

### Thread Safety Summary

Strategy | Pros | Cons | Use When
---|---|---|---
Message Passing | Safe, no locks, clear ownership | Learning curve | Default choice
Shared Memory | Familiar, sometimes natural | Needs locks, error-prone | Specific performance needs
Async/Await | Clean syntax, efficient I/O | Not for CPU-bound | I/O operations

**Note**: Full threading specification with thread pools, synchronization primitives, and detailed examples will be in separate document.

---

## Async and Concurrency

**Status:** [DESIGN] files/FEATURES.md Task 42 - see `files/Concurrency.md` and `files/Service.md`

Description: Built-in support for asynchronous programming.

* Async/Await: Modern asynchronous pattern
     * Native language support
     * Task-based model
     * Automatic state machine generation

* Parallel Processing: Multi-threading support
     * Thread-safe collections
     * Atomic operations
     * Lock-free structures

```fusion
// Async function - return-type-first syntax
async Result<Spaceship, string> function downloadShipData(string url)
    var response = await http.get(url)

    if response.statusCode != 200
        return Result.Error("HTTP error: {response.statusCode}")

    var data = await response.readBody()
    var ship = parseShipData(data)
    return Result.Ok(ship)

// Parallel processing
async void function updateFleet(List<Spaceship> fleet, float deltaTime)
    var tasks = List<Task>()

    for ship in fleet
        var task = async:
            ship.update(deltaTime)
        tasks.append(task)

    await Task.waitAll(tasks)

// Concurrent data structures
var safeQueue = ConcurrentQueue<Task>()
parallel for i in range(1000):
    safeQueue.enqueue(createTask(i))
```

[< 090 Memory](090-Memory.md) | [Index](index.md) | [110 Generics >](110-Generics.md) <!-- nav -->
